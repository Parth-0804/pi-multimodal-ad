"""Protocol-gate tests on tiny synthetic values, without GPU initialization."""
import importlib.util
import json
from pathlib import Path
import sys
import threading
from types import SimpleNamespace

import hashlib
import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit_checks", ROOT / "source/gpu_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


@pytest.mark.parametrize("key,value", [
    ("frames", 32), ("microbatch_segments", 2), ("effective_batch_segments", 16),
    ("precision", "float16"), ("full_execution_allowed", True), ("training_samples", 1024),
    ("window_seconds", 1), ("repetitions", 1), ("output_root", "runs/unsafe"),
])
def test_rejects_protocol_changes_or_unbounded_work(key, value):
    config = json.loads((ROOT / "configs/gpu_audit.json").read_text())
    config[key] = value
    with pytest.raises(ValueError):
        audit.validate_config(config)


def test_parity_detects_numerical_drift():
    config = {"parity_atol": 1e-7, "parity_rtol": 1e-5}
    expected = {"weight": torch.tensor([1.0, 2.0])}
    assert audit.compare_states(expected, expected, config)["bitwise_equal"]
    assert not audit.compare_states(expected, {"weight": torch.tensor([1.0, 2.1])}, config)["passed"]


def test_selected16_preserves_frame_order_and_exact_pixels(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "source"))
    from selected16_audit import Selected16Dataset

    original = np.arange(32 * 3 * 2 * 2, dtype=np.uint16).astype("uint8").reshape(32, 3, 2, 2)
    positions = list(range(0, 32, 2))
    expected = original[positions]
    row = {"sample_id": "synthetic", "frames16": [3 * p + 17 for p in positions],
           "frames32": list(range(32)), "failure": 1,
           "selected16_sha256": hashlib.sha256(expected.tobytes()).hexdigest()}
    data = object.__new__(Selected16Dataset)
    data.rows = [row]

    def decode(request):
        assert request["frames32"] == row["frames16"]
        return expected.copy()

    data.decoder = decode
    x, label, _ = data[0]
    assert torch.equal(x, torch.from_numpy(expected.astype("float32") * np.float32(1 / 255)))
    assert label.item() == 1
    row["selected16_sha256"] = "0" * 64
    with pytest.raises(AssertionError, match="SELECTED16_PIXEL_DRIFT"):
        data[0]


def test_kernel_busy_time_does_not_double_count_overlaps(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "source"))
    from trace_summary import union_microseconds

    events = [{"ts": 0, "dur": 10}, {"ts": 3, "dur": 4},
              {"ts": 8, "dur": 5}, {"ts": 20, "dur": 4}]
    assert union_microseconds(events) == 17
    assert union_microseconds([]) == 0


def test_cooperative_workers_preserve_global_action_order(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "source"))
    import managed_loader

    shards = []
    for worker in range(4):
        monkeypatch.setattr(managed_loader, "get_worker_info", lambda w=worker: SimpleNamespace(id=w, num_workers=4))
        shards.append(list(managed_loader.CooperativeDataset(list(range(24)), threading.Event())))
    assert [value for group in zip(*shards) for value in group] == list(range(24))


def test_cooperative_stop_releases_video_handles(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "source"))
    import managed_loader

    released = []
    decoder = SimpleNamespace(captures={"video": SimpleNamespace(release=lambda: released.append(True))})

    class Mapped:
        def __len__(self):
            return 10

        def __getitem__(self, index):
            return index

    mapped = Mapped()
    mapped.decoder = decoder
    stop = threading.Event()
    monkeypatch.setattr(managed_loader, "get_worker_info", lambda: None)
    iterator = iter(managed_loader.CooperativeDataset(mapped, stop))
    assert next(iterator) == 0
    stop.set()
    assert list(iterator) == []
    assert released == [True] and mapped.decoder is None
