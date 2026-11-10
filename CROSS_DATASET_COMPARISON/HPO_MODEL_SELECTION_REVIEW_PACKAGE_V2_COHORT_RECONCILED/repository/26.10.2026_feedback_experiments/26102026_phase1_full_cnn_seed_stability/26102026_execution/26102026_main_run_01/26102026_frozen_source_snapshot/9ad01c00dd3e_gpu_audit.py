"""Bounded, training-only GPU audit. All writes stay in a new audit run.

Imports only the existing model and normalization helpers; never invokes the
historical training, pixel-cache promotion/eviction, or study status writers.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import statistics
import subprocess
import sys
import threading
import time
import uuid

import cv2
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

REPO = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    path = Path(path)
    if not path.resolve().is_relative_to(BASE):
        raise ValueError("Output must stay inside the requested audit folder")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write("\n")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024**2), b""):
            h.update(chunk)
    return h.hexdigest()


def command(args):
    p = subprocess.run(args, capture_output=True, text=True, check=False)
    return {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def validate_config(c):
    if c["frames"] != 16 or c["microbatch_segments"] != 1:
        raise ValueError("Audit preserves the fixed 16-frame, one-action microbatch")
    if c["effective_batch_segments"] != 8 or c["precision"] != "float32":
        raise ValueError("Effective batch eight and float32 are protocol locked")
    if c["window_seconds"] < 30 or c["repetitions"] < 2:
        raise ValueError("Use sustained windows and at least two repetitions")
    if c["full_execution_allowed"]:
        raise ValueError("This entry point cannot authorize full execution")
    if c["training_samples"] % 8 or not 8 <= c["training_samples"] <= 32:
        raise ValueError("Use a bounded whole number of effective batches")
    if len(c["configurations"]) < 2:
        raise ValueError("At least two benchmark configurations are required")
    if not (REPO / c["output_root"]).resolve().is_relative_to(BASE):
        raise ValueError("Output root must be inside the requested folder")
    names = [x["name"] for x in c["configurations"]]
    if len(names) != len(set(names)) or any(not n.replace("_", "").isalnum() for n in names):
        raise ValueError("Configuration names must be unique simple identifiers")
    for x in c["configurations"]:
        if x["workers"] < 0 or x["workers"] > 4:
            raise ValueError("Worker count exceeds this bounded audit")


def worker_init(_):
    torch.set_num_threads(1)
    cv2.setNumThreads(1)


class PixelDataset(Dataset):
    """Read-only compressed cache; every 32-frame decoded identity is checked."""

    def __init__(self, run, repeats=1):
        self.root = Path(run)
        self.rows = read(self.root / "manifests/selected_training.json")
        self.repeats = repeats

    def __len__(self):
        return len(self.rows) * self.repeats

    def __getitem__(self, index):
        row = self.rows[index % len(self.rows)]
        start = time.perf_counter()
        blob = (self.root / "cache" / (row["sample_id"] + ".npz")).read_bytes()
        loaded = time.perf_counter()
        with np.load(io.BytesIO(blob), allow_pickle=False) as z:
            u = z["pixels"]
        unpacked = time.perf_counter()
        assert hashlib.sha256(u.tobytes()).hexdigest() == row["pixel_content_sha256"]
        hashed = time.perf_counter()
        x = torch.from_numpy(u[row["positions16_in32"]].astype("float32") * np.float32(1 / 255))
        end = time.perf_counter()
        return x, torch.tensor([row["failure"]], dtype=torch.float32), {
            "read_s": loaded - start,
            "decompress_s": unpacked - loaded,
            "hash_s": hashed - unpacked,
            "preprocess_s": end - hashed,
        }


def loader(run, setting, repeats=1000):
    options = dict(
        batch_size=None, num_workers=setting["workers"],
        pin_memory=setting["pin_memory"],
        generator=torch.Generator().manual_seed(91427),
        worker_init_fn=worker_init,
    )
    if setting["workers"]:
        options.update(
            persistent_workers=setting["persistent_workers"],
            prefetch_factor=setting["prefetch_factor"],
            multiprocessing_context="spawn",
        )
    return DataLoader(PixelDataset(run, repeats), **options)


def hardware():
    limits = {}
    relative = Path("/proc/self/cgroup").read_text().strip().split("::")[-1]
    base = Path("/sys/fs/cgroup") / relative.lstrip("/")
    for p in [base, *base.parents]:
        if not p.is_relative_to("/sys/fs/cgroup"):
            continue
        for name in ("cpu.max", "memory.max", "cpuset.cpus.effective"):
            if (p / name).is_file():
                limits[str((p / name).relative_to("/sys/fs/cgroup"))] = (p / name).read_text().strip()
    return {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "gpu": command(["nvidia-smi", "--query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu,utilization.memory,driver_version", "--format=csv"]),
        "nvidia_smi": command(["nvidia-smi"]),
        "topology": command(["nvidia-smi", "topo", "-m"]),
        "torch_version": torch.__version__, "cuda_runtime": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version(),
        "cuda_devices": [{"index": i, "name": torch.cuda.get_device_name(i),
                          "bytes": torch.cuda.get_device_properties(i).total_memory,
                          "capability": torch.cuda.get_device_capability(i)}
                         for i in range(torch.cuda.device_count())],
        "native_bf16": torch.cuda.is_bf16_supported(including_emulation=False),
        "allocation_variables": {k: os.environ.get(k) for k in (
            "CUDA_VISIBLE_DEVICES", "NVIDIA_VISIBLE_DEVICES", "SLURM_JOB_ID",
            "SLURM_JOB_GPUS", "SLURM_STEP_GPUS", "SLURM_CPUS_PER_TASK")},
        "allocation_interpretation": "Single visible idle VM GPU, consistent with the prior project allocation; no attempt to discover remote/hidden GPUs",
        "cpu_affinity": sorted(os.sched_getaffinity(0)), "cgroup_limits": limits,
        "cpu": command(["lscpu"]), "ram": command(["free", "-b"]),
        "disk": dict(zip(("total", "used", "free"), shutil.disk_usage(BASE))),
        "diskstats": Path("/proc/diskstats").read_text(),
        "memory_info": Path("/proc/meminfo").read_text(),
        "python": platform.python_version(),
        "packages": {n: importlib.metadata.version(n) for n in (
            "torch", "torchvision", "transformers", "numpy", "opencv-python", "pytest")},
    }


def preserved_files(study):
    paths = list((study / "source").glob("*"))
    paths += [study / p for p in (
        "progress.json", "config/resolved_config.json", "data_manifests/cohort_and_frames.json",
        "data_manifests/fit_partitions.json", "provenance/scientific_fit_lock.json",
        "shared_cache/CACHE_EVICTED.json", "shared_cache/pixels/CACHE_EVICTED.json")]
    paths += list(study.glob("**/in_progress.pt")) + list(study.glob("**/model.pt"))
    return {str(p.relative_to(REPO)): {"bytes": p.stat().st_size,
            "mtime_ns": p.stat().st_mtime_ns,
            "sha256": digest(p) if p.stat().st_size < 16 * 1024**2 else None}
            for p in paths if p.is_file()}


def prepare(run, c, study):
    from transformers import RTDetrImageProcessor

    original_config = read(study / "config/resolved_config.json")
    assert all(original_config[k] == c[k] for k in (
        "protocol", "effective_batch_segments", "microbatch_segments", "precision"))
    cohort = read(study / "data_manifests/cohort_and_frames.json")
    jobs = read(study / "data_manifests/fit_partitions.json")
    job = next(j for j in jobs if j["role"] == "outer_assessment")
    order = np.random.default_rng(job["seed"]).permutation(len(job["G"]))
    rows = [cohort[job["G"][int(i)]] for i in order[:c["training_samples"]]]
    assert not set(r["recording_id"] for r in rows) & set(
        cohort[i]["recording_id"] for key in ("C", "predict") for i in job[key])
    write(run / "manifests/selected_training.json", rows)
    write(run / "config/original_protocol.json", original_config)
    write(run / "manifests/job.json", job)
    processor = RTDetrImageProcessor.from_pretrained(REPO / original_config["weights_dir"], local_files_only=True)
    (run / "cache").mkdir()
    profiles, inputs, used = [], [], 0
    cv2.setNumThreads(1)
    for row in rows:
        video = REPO / row["video_path"]
        st = video.stat()
        assert st.st_size == row["video_bytes"] and st.st_mtime_ns == row["video_mtime_ns"]
        inputs.append({k: row[k] for k in (
            "sample_id", "recording_id", "segment_id", "source_path", "source_recorded_sha256",
            "source_bytes", "source_mtime_ns", "video_path", "video_bytes", "video_mtime_ns",
            "frames16", "frames32", "pixel_content_sha256")})
        start = time.perf_counter()
        cap = cv2.VideoCapture(str(video))
        assert cap.isOpened()
        images = []
        for index in row["frames32"]:
            current = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if index < current or index - current > 64:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(index))
            else:
                for _ in range(index - current):
                    cap.grab()
            ok, frame = cap.read()
            assert ok, ("FRAME_DECODE_FAILURE", row["sample_id"], index)
            images.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        cap.release()
        decoded = time.perf_counter()
        pixels = processor(images=images, return_tensors="np")["pixel_values"]
        u = np.rint(pixels / original_config["rescale_factor"]).astype("uint8")
        assert np.array_equal(u.astype("float32") * np.float32(original_config["rescale_factor"]), pixels)
        assert hashlib.sha256(u.tobytes()).hexdigest() == row["pixel_content_sha256"], "PIXEL_IDENTITY_DRIFT"
        processed = time.perf_counter()
        stream = io.BytesIO()
        np.savez_compressed(stream, pixels=u)
        blob = stream.getvalue()
        packed = time.perf_counter()
        used += len(blob)
        assert used <= c["max_cache_bytes"]
        assert shutil.disk_usage(run).free - len(blob) >= c["minimum_free_bytes"]
        path = run / "cache" / (row["sample_id"] + ".npz")
        with path.open("xb") as f:
            f.write(blob)
        profiles.append({"sample_id": row["sample_id"], "decode_s": decoded - start,
                         "processor_hash_s": processed - decoded,
                         "compress_s": packed - processed, "cache_bytes": len(blob),
                         "write_s": time.perf_counter() - packed})
        print("prepared", len(profiles), "/", len(rows), flush=True)
    write(run / "manifests/inputs.json", inputs)
    write(run / "tables/cold_decode_profile.json", profiles)
    # Bounded read-only storage probe. No cache dropping, write benchmark or raw scan.
    probes = []
    for row in rows[:4]:
        video = REPO / row["video_path"]
        for repetition in range(2):
            start = time.perf_counter()
            with video.open("rb") as f:
                blob = f.read(16 * 1024**2)
            elapsed = time.perf_counter() - start
            probes.append({"video_path": row["video_path"], "repetition": repetition,
                           "bytes": len(blob), "seconds": elapsed,
                           "MiB_s": len(blob) / 1024**2 / elapsed,
                           "caveat": "page-cache-affected buffered read; not physical disk bandwidth"})
    write(run / "tables/storage_reads.json", probes)


class Monitor:
    def __init__(self, interval):
        self.interval, self.rows, self.stop = interval, [], threading.Event()

    def __enter__(self):
        self.thread = threading.Thread(target=self.poll, daemon=True)
        self.thread.start()
        return self

    def poll(self):
        while not self.stop.is_set():
            t = time.monotonic()
            result = command(["nvidia-smi", "--query-gpu=utilization.gpu,utilization.memory,memory.used,power.draw", "--format=csv,noheader,nounits"])
            try:
                values = [float(v.strip()) for v in result["stdout"].strip().split(",")]
                if len(values) == 4:
                    self.rows.append({"monotonic": t, **dict(zip(("gpu_compute_percent", "memory_controller_percent", "vram_MiB", "power_W"), values))})
            except ValueError:
                pass
            self.stop.wait(self.interval)

    def __exit__(self, *args):
        self.stop.set()
        self.thread.join(timeout=3)


def create_model(study, job):
    # These existing helpers have no writes on these paths. Never import training.py.
    sys.path.insert(0, str(study / "source"))
    from visual_model import original, Visual, optimizer
    from fusion import standardizer

    features = np.load(study / "shared_cache/original_features_16.npy", allow_pickle=False)
    mean, std = standardizer(features[job["G"]])
    backbone = original()
    torch.manual_seed(job["seed"])
    torch.cuda.manual_seed_all(job["seed"])
    model = Visual(backbone, features.shape[1], mean, std, True).cuda().train()
    return model, optimizer(model), optimizer


def take_update(model, opt, iterator, setting, pos_weight, *, gradients=False):
    opt.zero_grad(set_to_none=True)
    timings = {k: 0.0 for k in ("loader_wait_s", "h2d_ms", "compute_ms", "read_s", "decompress_s", "hash_s", "preprocess_s")}
    events, losses = [], []
    for _ in range(8):
        start = time.perf_counter()
        x, y, cost = next(iterator)
        timings["loader_wait_s"] += time.perf_counter() - start
        for k, v in cost.items():
            timings[k] += float(v)
        a, b, d = [torch.cuda.Event(enable_timing=True) for _ in range(3)]
        a.record()
        x = x.unsqueeze(0).to("cuda", non_blocking=setting["pin_memory"])
        y = y.to("cuda", non_blocking=setting["pin_memory"])
        b.record()
        logit = model(x)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logit, y, pos_weight=pos_weight)
        if setting["legacy_sync"]:
            assert torch.isfinite(loss)
        (loss / 8).backward()
        d.record()
        if setting["legacy_sync"]:
            float(loss.detach())
        losses.append(loss.detach())
        events.append((a, b, d))
    evidence = None
    if gradients:
        evidence = {n: {"finite": bool(torch.isfinite(p.grad).all()),
                        "nonzero": bool(torch.count_nonzero(p.grad))}
                    for n, p in model.named_parameters() if p.grad is not None}
        assert evidence and all(v["finite"] for v in evidence.values())
        assert all(n.startswith(("head.", "backbone.encoder.stages.3.")) for n in evidence)
        for prefix in ("head.", "backbone.encoder.stages.3."):
            assert any(v["nonzero"] for n, v in evidence.items() if n.startswith(prefix))
    a, b = [torch.cuda.Event(enable_timing=True) for _ in range(2)]
    a.record()
    norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    if setting["legacy_sync"]:
        assert torch.isfinite(norm)
    opt.step()
    b.record()
    return timings, events, (a, b), torch.stack(losses), norm.detach(), evidence


def finish_timing(updates):
    totals = {k: 0.0 for k in ("loader_wait_s", "h2d_ms", "compute_ms", "read_s", "decompress_s", "hash_s", "preprocess_s", "optimizer_ms")}
    for timing, events, optimizer_events, losses, norm, _ in updates:
        assert bool(torch.isfinite(losses).all()) and bool(torch.isfinite(norm))
        for k, v in timing.items():
            totals[k] += v
        for a, b, d in events:
            totals["h2d_ms"] += a.elapsed_time(b)
            totals["compute_ms"] += b.elapsed_time(d)
        totals["optimizer_ms"] += optimizer_events[0].elapsed_time(optimizer_events[1])
    return totals


def cpu_state(model):
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}


def compare_states(expected, actual, c):
    errors, passed, exact = {}, True, True
    for k, value in expected.items():
        other = actual[k]
        if torch.is_floating_point(value):
            errors[k] = float((value - other).abs().max())
            passed &= torch.allclose(value, other, atol=c["parity_atol"], rtol=c["parity_rtol"])
        else:
            passed &= torch.equal(value, other)
        exact &= torch.equal(value, other)
    return {"passed": bool(passed), "bitwise_equal": bool(exact), "max_absolute_difference": max(errors.values()),
            "atol": c["parity_atol"], "rtol": c["parity_rtol"]}


def numerical_check(run, c, setting, model, opt, optimizer_factory, pos_weight, iterator):
    initial = cpu_state(model)
    rng = torch.get_rng_state(), torch.cuda.get_rng_state_all()
    reference = dict(setting, legacy_sync=True)
    data = [PixelDataset(run)[i] for i in range(8)]
    result = take_update(model, opt, iter(data), reference, pos_weight, gradients=True)
    torch.cuda.synchronize()
    expected = cpu_state(model)
    expected_rng = torch.get_rng_state(), torch.cuda.get_rng_state_all()
    expected_opt = copy.deepcopy(opt.state_dict())
    changed = [k for k in initial if not torch.equal(initial[k], expected[k])]
    assert any(k.startswith("head.") for k in changed)
    assert any(k.startswith("backbone.encoder.stages.3.") for k in changed)
    assert all(k.startswith(("head.", "backbone.encoder.stages.3.")) for k in changed)
    assert not any("running_" in k or "num_batches_tracked" in k for k in changed)
    model.load_state_dict(initial)
    opt = optimizer_factory(model)
    torch.set_rng_state(rng[0])
    torch.cuda.set_rng_state_all(rng[1])
    candidate = take_update(model, opt, iterator, setting, pos_weight, gradients=True)
    torch.cuda.synchronize()
    parity = compare_states(expected, cpu_state(model), c)
    assert parity["passed"], parity
    assert torch.equal(torch.get_rng_state(), expected_rng[0])
    assert all(torch.equal(a, b) for a, b in zip(torch.cuda.get_rng_state_all(), expected_rng[1]))
    optimizer_equal = all(torch.equal(v, opt.state_dict()["state"][k][name]) if torch.is_tensor(v)
                          else v == opt.state_dict()["state"][k][name]
                          for k, state in expected_opt["state"].items() for name, v in state.items())
    assert optimizer_equal
    torch.cuda.synchronize()
    # Replay an actual disk checkpoint for each setting, including optimizer/RNG.
    saved = run / "checks" / (setting["name"] + "_disposable.pt")
    saved.parent.mkdir(exist_ok=True)
    with saved.open("xb") as f:
        torch.save({"model": cpu_state(model), "optimizer": opt.state_dict(),
                    "cpu_rng": torch.get_rng_state(), "cuda_rng": torch.cuda.get_rng_state_all(),
                    "precision": "float32", "effective_batch_segments": 8,
                    "next_sample": 8, "disposable_audit_only": True}, f)
    take_update(model, opt, iter(data), setting, pos_weight)
    torch.cuda.synchronize()
    after = cpu_state(model)
    after_opt = copy.deepcopy(opt.state_dict())
    replay_rng = torch.get_rng_state(), torch.cuda.get_rng_state_all()
    d = torch.load(saved, weights_only=True, map_location="cpu")
    model.load_state_dict(d["model"])
    opt = optimizer_factory(model)
    opt.load_state_dict(d["optimizer"])
    torch.set_rng_state(d["cpu_rng"])
    torch.cuda.set_rng_state_all(d["cuda_rng"])
    take_update(model, opt, iter(data), setting, pos_weight)
    torch.cuda.synchronize()
    replay = compare_states(after, cpu_state(model), c)
    replay_opt_equal = all(torch.equal(v, opt.state_dict()["state"][k][name]) if torch.is_tensor(v)
                           else v == opt.state_dict()["state"][k][name]
                           for k, state in after_opt["state"].items() for name, v in state.items())
    assert replay["bitwise_equal"] and replay_opt_equal
    assert torch.equal(torch.get_rng_state(), replay_rng[0])
    assert all(torch.equal(a, b) for a, b in zip(torch.cuda.get_rng_state_all(), replay_rng[1]))
    check = {"passed": True, "update_parity": parity, "optimizer_exact": optimizer_equal,
             "rng_exact": True, "gradients": candidate[-1], "changed_tensors": changed,
             "frozen_parameters_and_BN_buffers_unchanged": True,
             "backbone_eval": all(not m.training for m in model.backbone.modules()),
             "checkpoint_replay": replay, "replay_optimizer_and_rng_exact": True,
             "checkpoint_sha256": digest(saved), "disposable_updates": 4}
    write(run / "checks" / (setting["name"] + "_numerical.json"), check)
    model.load_state_dict(initial)
    opt = optimizer_factory(model)
    torch.set_rng_state(rng[0])
    torch.cuda.set_rng_state_all(rng[1])
    return opt


def benchmark(run, name):
    c = read(run / "config/resolved_config.json")
    setting = next(x for x in c["configurations"] if x["name"] == name)
    study = REPO / c["study_root"]
    assert not command(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"])["stdout"].strip(), "GPU already occupied; do not contend"
    torch.set_num_threads(c["cpu_threads"])
    job = read(run / "manifests/job.json")
    cohort = read(study / "data_manifests/cohort_and_frames.json")
    positives = sum(cohort[i]["failure"] for i in job["G"])
    pos_weight = torch.tensor((len(job["G"]) - positives) / positives, device="cuda")
    data_loader = loader(run, setting)
    iterator = iter(data_loader)
    model, opt, factory = create_model(study, job)
    opt = numerical_check(run, c, setting, model, opt, factory, pos_weight, iterator)
    windows = []
    for repetition in range(c["repetitions"]):
        for _ in range(c["warmup_updates"]):
            take_update(model, opt, iterator, setting, pos_weight)
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        updates = []
        io_before = Path("/proc/self/io").read_text()
        cpu_before = time.process_time()
        with Monitor(c["monitor_interval_seconds"]) as monitor:
            start = time.monotonic()
            while time.monotonic() - start < c["window_seconds"] and len(updates) < c["max_updates_per_window"]:
                updates.append(take_update(model, opt, iterator, setting, pos_weight))
                # Completion bounds queueing and permits prompt numerical failure.
                # One check per eight actions preserves per-action RNG/order.
                torch.cuda.synchronize()
                assert torch.isfinite(updates[-1][3]).all() and torch.isfinite(updates[-1][4])
            torch.cuda.synchronize()
            end = time.monotonic()
        cpu_seconds = time.process_time() - cpu_before
        samples = len(updates) * 8
        measured = [r for r in monitor.rows if start + 1 <= r["monotonic"] <= end - 1]
        assert measured, "No GPU telemetry collected"
        timings = finish_timing(updates)
        window = {"repetition": repetition, "seconds": end - start,
                  "actions": samples, "frames": samples * 16,
                  "actions_per_second": samples / (end - start),
                  "estimated_epoch_seconds_G2966": len(job["G"]) * (end - start) / samples,
                  "gpu_compute_percent_mean": statistics.mean(r["gpu_compute_percent"] for r in measured),
                  "gpu_compute_percent_median": statistics.median(r["gpu_compute_percent"] for r in measured),
                  "vram_MiB_max": max(r["vram_MiB"] for r in measured),
                  "peak_torch_allocated_bytes": torch.cuda.max_memory_allocated(),
                  "peak_torch_reserved_bytes": torch.cuda.max_memory_reserved(),
                  "cpu_main_process_seconds": cpu_seconds, "timings": timings,
                  "process_io_before": io_before, "process_io_after": Path("/proc/self/io").read_text(),
                  "reached_duration": end - start >= c["window_seconds"]}
        windows.append(window)
        write(run / "logs" / f"{name}_{repetition}_telemetry.json", monitor.rows)
        print(json.dumps({"name": name, **{k: v for k, v in window.items() if k not in ("process_io_before", "process_io_after", "timings")}}), flush=True)
    write(run / "tables" / (name + ".json"), {"configuration": setting, "windows": windows,
          "all_finite": True, "disposable_optimizer_updates": 4 + c["warmup_updates"] * c["repetitions"] + sum(w["actions"] // 8 for w in windows),
          "initialization_checkpoint_and_warmup_excluded": True,
          "order_caveat": "Identical cyclic 24-action training-only order across configurations; not a scientific epoch"})
    if data_loader._iterator is not None:
        data_loader._iterator._shutdown_workers()


def finalize(run, c, study, before, start):
    results = [read(run / "tables" / (s["name"] + ".json")) for s in c["configurations"]]
    summary = []
    for result in results:
        windows = result["windows"]
        summary.append({"name": result["configuration"]["name"],
                        "actions_s": sum(w["actions"] for w in windows) / sum(w["seconds"] for w in windows),
                        "gpu_percent": statistics.mean(w["gpu_compute_percent_mean"] for w in windows),
                        "vram_MiB": max(w["vram_MiB_max"] for w in windows),
                        "epoch_s": statistics.mean(w["estimated_epoch_seconds_G2966"] for w in windows),
                        "range_actions_s": [min(w["actions_per_second"] for w in windows), max(w["actions_per_second"] for w in windows)]})
    best = max(summary, key=lambda r: r["actions_s"])
    jobs = read(study / "data_manifests/fit_partitions.json")
    presentations = sum(len(j["G"]) * 5 for j in jobs)
    after = preserved_files(study)
    assert before == after, "Historical file identity changed"
    write(run / "checks/historical_preservation.json", {"passed": True, "before": before, "after": after})
    estimate = {"one_seed_25_fits_16frame_adapted_presentations": presentations,
                "best_warm_cache_16frame_training_hours": presentations / best["actions_s"] / 3600,
                "four_arm_estimate_method": "16-frame adapted measured; 32-frame adapted provisionally 2x; frozen-head, extraction, inference, checkpoint and cold-decode overhead excluded",
                "four_arm_warm_training_lower_bound_hours": 3 * presentations / best["actions_s"] / 3600,
                "multi_seed_count": None, "actual_full_experiment_gpu_hours": 0,
                "audit_wall_hours_with_one_gpu_reserved": (time.monotonic() - start) / 3600,
                "measured_training_window_gpu_hours": sum(w["seconds"] for r in results for w in r["windows"]) / 3600}
    write(run / "tables/summary.json", summary)
    write(run / "reports/time_estimate.json", estimate)
    gate = {"status": "BENCHMARKS_COMPLETE_FULL_EXECUTION_LOCKED",
            "bottleneck_investigated": True, "at_least_two_configs": len(results) >= 2,
            "selected_configuration": best["name"], "selection_metric": "measured actions/s",
            "numerical_and_gradient_checks": all(read(run / "checks" / (s["name"] + "_numerical.json"))["passed"] for s in c["configurations"]),
            "time_estimate_recorded": True, "full_execution_allowed": False,
            "limitations": ["Cold whole-cohort sustained loading not yet benchmarked", "32-frame training not benchmarked", "No new multi-seed/fold protocol specified", "No scientific runner modified or launched"]}
    write(run / "reports/performance_gate.json", gate)
    write(run / "reports/warnings.json", c["warnings"] + gate["limitations"])
    outputs = [{"path": str(p.relative_to(run)), "bytes": p.stat().st_size,
                "sha256": digest(p) if p.stat().st_size < 32 * 1024**2 else None,
                "role": "regenerable_lossless_pixels" if "cache" in p.parts else "audit_evidence"}
               for p in sorted(run.rglob("*")) if p.is_file()]
    write(run / "manifests/outputs.json", outputs)
    print(json.dumps({"run": str(run.relative_to(REPO)), "summary": summary, "estimate": estimate, "gate": gate}), flush=True)


def run_audit(config_path):
    c = read(config_path)
    validate_config(c)
    run = REPO / c["output_root"] / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    run.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    write(run / "config/resolved_config.json", c)
    write(run / "provenance.json", {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
          "command": shlex.join(sys.argv), "git_commit": command(["git", "rev-parse", "HEAD"]),
          "git_status": command(["git", "status", "--short", "--untracked-files=all"]),
          "source_sha256": digest(__file__), "config_sha256": digest(config_path),
          "config_source": str(config_path.relative_to(REPO)), "methodology": "bounded-fp32-action16-audit-v1"})
    study = REPO / c["study_root"]
    before = preserved_files(study)
    write(run / "manifests/historical_before.json", before)
    probe = command([sys.executable, "-B", str(Path(__file__).resolve()), "hardware"])
    if probe["returncode"]:
        raise RuntimeError(probe["stderr"])
    write(run / "reports/hardware.json", json.loads(probe["stdout"]))
    print("RUN", str(run.relative_to(REPO)), flush=True)
    prepare(run, c, study)
    for setting in c["configurations"]:
        args = [sys.executable, "-B", str(Path(__file__).resolve()), "worker", "--run", str(run), "--name", setting["name"]]
        with (run / (setting["name"] + ".log")).open("x") as log:
            p = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=False)
        print(setting["name"], "exit", p.returncode, flush=True)
        if p.returncode:
            write(run / "reports/performance_gate.json", {"status": "BLOCKED", "failed_configuration": setting["name"], "full_execution_allowed": False})
            raise RuntimeError("Benchmark failed; see " + str(run / (setting["name"] + ".log")))
    finalize(run, c, study, before, start)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["run", "worker", "hardware"])
    parser.add_argument("--config", type=Path, default=BASE / "configs/gpu_audit.json")
    parser.add_argument("--run", type=Path)
    parser.add_argument("--name")
    args = parser.parse_args()
    if args.mode == "hardware":
        print(json.dumps(hardware()))
    elif args.mode == "run":
        run_audit(args.config.resolve())
    else:
        if args.run is None or not args.run.resolve().is_relative_to(BASE / "runs"):
            parser.error("Worker requires a new audit run under the audit folder")
        benchmark(args.run.resolve(), args.name)


if __name__ == "__main__":
    main()
