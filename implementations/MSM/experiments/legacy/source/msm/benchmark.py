"""Short exclusive-GPU follow-up, within the frozen smoke frame/update budget."""
import argparse
import json
from pathlib import Path
import threading
import time

import numpy as np
import psutil
import torch

from .data import IntervalPixels, load_cohort, digest
from .models import verified_backbone, IntervalCNN, fit_visual
from .smoke import choose_smoke, loader_for, gpu_snapshot, write


def main(run):
    run = Path(run)
    destination = run / "reports/exclusive_benchmark.json"
    if destination.exists():
        raise FileExistsError(destination)
    config = json.loads((run / "config/resolved_config.json").read_text())
    before = gpu_snapshot()
    if before["processes"]:
        blocked = run / "reports/exclusive_benchmark_blocked.json"
        if not blocked.exists():
            write(blocked, {"reason": "GPU admission found another compute process; zero benchmark work performed",
                            "snapshot": before, "no_job_interrupted": True})
        raise RuntimeError("Exclusive follow-up requires an idle GPU; no job will be interrupted")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    free, total = torch.cuda.mem_get_info()
    torch.cuda.set_per_process_memory_fraction(2048 * 1024**2 / total)
    processor, backbone, identity = verified_backbone(config)
    encoder = IntervalCNN(backbone, 2).cuda().eval()
    frame = load_cohort(config["stage2"])
    small = frame.iloc[choose_smoke(frame)].reset_index(drop=True)
    selected = small.iloc[:6]
    results, arrays, samples = [], [], []
    stop = threading.Event()

    def monitor():
        while not stop.is_set():
            samples.append({"monotonic": time.monotonic(), **gpu_snapshot()})
            stop.wait(.5)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    try:
        for workers in (0, 2):
            dataset = IntervalPixels(selected, config["stage2"])
            loader = loader_for(dataset, workers)
            setup_start = time.perf_counter()
            iterator = iter(loader)
            pids = [worker.pid for worker in iterator._workers] if workers else []
            collected = []
            try:
                for _ in range(2):
                    item = next(iterator)
                    with torch.inference_mode():
                        encoder(item["pixels"].cuda(non_blocking=True).float() / 255)
                torch.cuda.synchronize()
                setup = time.perf_counter() - setup_start
                process = psutil.Process()
                cpu_before = sum(process.cpu_times()[:2])
                child_before = sum(sum(psutil.Process(pid).cpu_times()[:2]) for pid in pids)
                torch.cuda.reset_peak_memory_stats()
                begin, wall_start = time.monotonic(), time.perf_counter()
                waits, decodes = [], []
                for _ in range(4):
                    wait_start = time.perf_counter()
                    item = next(iterator)
                    waits.append(time.perf_counter() - wait_start)
                    with torch.inference_mode():
                        values = encoder(item["pixels"].cuda(non_blocking=True).float() / 255)
                    collected.append(values.cpu().numpy())
                    decodes.extend(item["decode_seconds"].tolist())
                torch.cuda.synchronize()
                elapsed, end = time.perf_counter() - wall_start, time.monotonic()
                parent_cpu = sum(process.cpu_times()[:2]) - cpu_before
                child_cpu = sum(sum(psutil.Process(pid).cpu_times()[:2]) for pid in pids) - child_before
                rss = process.memory_info().rss + sum(psutil.Process(pid).memory_info().rss for pid in pids)
                try:
                    next(iterator)
                    raise ValueError("Unexpected extra interval")
                except StopIteration:
                    pass
            finally:
                if workers:
                    iterator._shutdown_workers()
                    codes = [worker.exitcode for worker in iterator._workers]
                else:
                    dataset.close()
                    codes = []
            if any(code != 0 for code in codes) or any(psutil.pid_exists(pid) for pid in pids):
                raise RuntimeError("Worker shutdown failed")
            arrays.append(np.concatenate(collected))
            results.append({"workers": workers, "warmup_intervals": 2, "timed_intervals": 4,
                "worker_startup_plus_warmup_seconds": setup, "wall_seconds": elapsed,
                "intervals_per_second": 4 / elapsed, "frames_per_second": 64 / elapsed,
                "parent_cpu_seconds": parent_cpu, "worker_cpu_seconds_window_delta": child_cpu,
                "cpu_core_equivalents_during_timed_window": (parent_cpu + child_cpu) / elapsed,
                "rss_parent_plus_workers_bytes": rss, "loader_wait_seconds": sum(waits),
                "decode_seconds_sum": sum(decodes), "worker_exit_codes": codes, "workers_reaped": True,
                "peak_torch_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_torch_reserved_bytes": torch.cuda.max_memory_reserved(),
                "monotonic_window": [begin, end]})
        if not np.array_equal(*arrays):
            raise ValueError("Exclusive worker numerical parity failed")
        del encoder, backbone
        torch.cuda.empty_cache()
        with np.load(run / "cache/smoke_features.npz") as cached:
            visual = cached["visual"].copy()
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        started = time.perf_counter()
        model, scaler, evidence = fit_visual(visual, small.target.to_numpy(int), config["visual"], 42, epochs=2, device="cuda")
        torch.cuda.synchronize()
        training_seconds = time.perf_counter() - started
        training = {"intervals": len(small), "epochs": 2, "updates": evidence["updates"],
            "initialization_plus_training_seconds": training_seconds,
            "interval_presentations_per_second_including_initialization": 2 * len(small) / training_seconds,
            "finite_losses": evidence["finite_losses"], "finite_nonzero_head_gradients": evidence["all_head_parameters_nonzero_gradient"],
            "peak_torch_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_torch_reserved_bytes": torch.cuda.max_memory_reserved()}
        del model
        torch.cuda.empty_cache()
    finally:
        stop.set()
        thread.join(timeout=5)
    import os
    unexpected = set()
    for sample in samples:
        for line in sample["processes"].splitlines():
            if line and int(line.split(",")[0]) != os.getpid():
                unexpected.add(line)
    if unexpected:
        raise RuntimeError("Another GPU job appeared: do not call this an exclusive benchmark")
    historical = json.loads((run / "manifests/smoke_validation.json").read_text())
    total_frames = historical["cnn_frames_forwarded"] + 12 * 16
    head_report = run / "reports/cached_head_benchmark.json"
    previous_head_updates = sum(item["updates"] for item in json.loads(head_report.read_text())["results"]) if head_report.exists() else 0
    total_updates = historical["head_updates"] + previous_head_updates + training["updates"]
    if total_frames > config["smoke"]["maximum_cnn_frame_forwards_including_benchmark"] or total_updates > config["smoke"]["maximum_head_updates"]:
        raise ValueError("Combined smoke budget exceeded")
    write(destination, {"exclusive_gpu_verified_by_sampled_process_inventory": True, "gpu_before": before,
        "settings": results, "training_cached_head_gpu": training, "telemetry": samples,
        "worker_feature_bitwise_parity": True, "additional_cnn_frames": 192,
        "combined_cnn_frames": total_frames, "combined_head_updates": total_updates,
        "source_sha256": digest(__file__), "no_outer_predictions": True,
        "limitations": "Four measured intervals per setting, no sustained utilization claim; warm page-cache video seeking; head timing includes initialization; feature extraction is frozen-CNN inference, not CNN backpropagation."})
    print(json.dumps({"benchmark": str(destination), "combined_frames": total_frames, "combined_updates": total_updates}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    main(parser.parse_args().run)
