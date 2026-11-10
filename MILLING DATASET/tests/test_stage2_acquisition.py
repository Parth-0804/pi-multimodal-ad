"""Synthetic tests for bounded pilot transfer and preservation of existing bytes."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("pilot_download", Path(__file__).parents[1] / "source/stage2/download_msm.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
HANDLE = "synthetic/milling/versions/2"


def test_transfer_pins_one_file_and_never_overwrites(monkeypatch, tmp_path):
    body = b"synthetic payload"
    def response(url, timeout):
        assert "datasetVersionNumber=2" in url
        assert "fileName=m%2Fdataset1%2Fsample.csv" in url
        return io.BytesIO(body)
    monkeypatch.setattr(module.urllib.request, "urlopen", response)
    row = {"path": "m/dataset1/sample.csv", "bytes": len(body)}
    dest = tmp_path / "raw"
    result = module.transfer(HANDLE, row, dest, tmp_path / "staging")
    assert result["sha256"] == hashlib.sha256(body).hexdigest()
    with pytest.raises(FileExistsError):
        module.transfer(HANDLE, row, dest, tmp_path / "second_staging")
    assert (dest / row["path"]).read_bytes() == body


@pytest.mark.parametrize("body", [b"tiny", b"too many bytes"])
def test_bad_response_size_is_not_published(monkeypatch, tmp_path, body):
    monkeypatch.setattr(module.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(body))
    row = {"path": "m/dataset1/sample.csv", "bytes": 8}
    with pytest.raises(ValueError):
        module.transfer(HANDLE, row, tmp_path / "raw", tmp_path / "staging")
    assert not (tmp_path / "raw" / row["path"]).exists()


def test_existing_files_require_both_size_and_acquisition_hash(tmp_path):
    dest = tmp_path / "raw"; dest.mkdir()
    path = dest / "label.csv"; path.write_bytes(b"abc")
    cfg = {"handle": HANDLE, "download_plan": [{"name": "label.csv", "bytes": 3}], "max_download_bytes": 10}
    inventory = {"dataset_id": 8392825, "handle": HANDLE, "files": [{"name": "label.csv", "bytes": 3}]}
    with pytest.raises(ValueError, match="matching acquisition hash"):
        module.audit_plan(cfg, inventory, dest)
    receipt = {"handle": HANDLE, "results": [{"path": "label.csv", "sha256": hashlib.sha256(b"abc").hexdigest()}]}
    (dest / "_msm_download_receipt_test.json").write_text(json.dumps(receipt))
    assert module.audit_plan(cfg, inventory, dest)[0]["status"] == "verified_existing"
    path.write_bytes(b"bad")
    with pytest.raises(ValueError, match="matching acquisition hash"):
        module.audit_plan(cfg, inventory, dest)
