"""Bounded CPU/CUDA cached-head path check; no outer performance measurement."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
import torch
from .data import load_cohort, digest
from .models import MillingVisual, fit_visual
from .smoke import choose_smoke, write, gpu_snapshot


def main(run):
    run = Path(run)
    output = run / "reports/cached_head_benchmark.json"
    if output.exists():
        raise FileExistsError(output)
    config = json.loads((run / "config/resolved_config.json").read_text())
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    frame = load_cohort(config["stage2"])
    small = frame.iloc[choose_smoke(frame)].reset_index(drop=True)
    with np.load(run / "cache/smoke_features.npz") as source:
        x = source["visual"].copy()
        if source["interval_id"].tolist() != small.interval_id.tolist():
            raise ValueError("Cached development interval identity mismatch")
    free, total = torch.cuda.mem_get_info()
    if free < (3072 + 256) * 1024**2:
        raise RuntimeError("Insufficient GPU reserve for small classifier check")
    torch.cuda.set_per_process_memory_fraction(256 * 1024**2 / total)
    before_gpu = gpu_snapshot()
    # The same untrained head and real development features compare device paths.
    torch.manual_seed(42)
    cpu = MillingVisual().eval()
    gpu = MillingVisual().cuda().eval()
    gpu.load_state_dict(cpu.state_dict())
    sample = torch.from_numpy(x[:2] / max(float(np.std(x)), 1e-6))
    with torch.no_grad():
        difference = float((cpu(sample) - gpu(sample.cuda()).cpu()).abs().max())
    if difference > 2e-5:
        raise ValueError("CPU/CUDA head forward mismatch")
    del cpu, gpu
    results = []
    for device in ("cpu", "cuda"):
        if device == "cuda":
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        model, scaler, info = fit_visual(x, small.target.to_numpy(int), config["visual"], 42, epochs=2, device=device)
        if device == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        results.append({"device": device, "intervals": len(x), "epochs": 2, "updates": info["updates"],
            "initialization_plus_training_seconds": elapsed, "interval_presentations_per_second_including_initialization": 2 * len(x) / elapsed,
            "finite_losses": info["finite_losses"], "nonzero_finite_head_gradients": info["all_head_parameters_nonzero_gradient"],
            "peak_torch_allocated_bytes": torch.cuda.max_memory_allocated() if device == "cuda" else None})
        del model
    baseline = json.loads((run / "manifests/smoke_validation.json").read_text())
    total_updates = baseline["head_updates"] + sum(item["updates"] for item in results)
    if total_updates > config["smoke"]["maximum_head_updates"]:
        raise ValueError("Frozen combined optimizer-update budget exceeded")
    write(output, {"results": results, "CPU_CUDA_untrained_forward_max_abs_difference": difference,
        "gpu_before": before_gpu, "shared_gpu": bool(before_gpu["processes"]),
        "combined_optimizer_updates": total_updates, "combined_cnn_frames": baseline["cnn_frames_forwarded"],
        "source_sha256": digest(__file__), "outer_predictions": 0,
        "limitations": "Two updates per device; includes construction/optimizer startup; GPU shared; no sustained timing or efficacy interpretation."})
    print(json.dumps({"head_benchmark": str(output), "total_updates": total_updates}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    main(parser.parse_args().run)
