"""Bounded MSM development smoke; never predicts or scores an outer test set."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import warnings

import cv2
import numpy as np
import pandas as pd
import psutil
import torch
from torch.utils.data import DataLoader

from .data import digest, load_cohort, sensor_features, IntervalPixels, worker_init, FEATURE_NAMES
from .experiment import fit_oof_fusion, branch_probabilities
from .models import verified_backbone, IntervalCNN, save_bundle, load_bundle, predict_visual, averaging
from .splits import smoke_partition, nested_plan, verify_plan


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def gpu_snapshot():
    return {"gpu": subprocess.check_output(["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu", "--format=csv,noheader,nounits"], text=True).strip(),
            "processes": subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"], text=True).strip()}


def choose_smoke(frame):
    result = []
    for group, count in (("imi_vm20i/dataset1", 8), ("imi_vm20i/dataset4", 6), ("imi_vmx30ui/dataset8", 6)):
        result.extend(frame.index[frame.group_id == group][:count])
    for label in (0, 1):
        result.extend(frame.index[(frame.group_id == "imi_vmx30ui/dataset9") & (frame.native_label == label)][:2])
    return np.array(sorted(result), int)


def loader_for(dataset, workers, pin_memory=True):
    extra = {"prefetch_factor": 1, "multiprocessing_context": "spawn", "persistent_workers": True} if workers else {}
    return DataLoader(dataset, batch_size=1, shuffle=False, num_workers=workers, pin_memory=pin_memory,
                      worker_init_fn=worker_init, generator=torch.Generator().manual_seed(42), **extra)


def consume(dataset, encoder, processor, workers, deadline, reserve_mib, collect=True):
    """Finite exhaustion before closing persistent workers; no discarded batches."""
    loader = loader_for(dataset, workers)
    iterator = iter(loader)
    process = psutil.Process()
    before_cpu = sum(process.cpu_times()[:2])
    started = time.perf_counter()
    vectors, ids, waits, decodes, child_pids, gpu_samples = [], [], [], [], [], []
    try:
        if workers:
            child_pids = [worker.pid for worker in iterator._workers]
        while True:
            before = time.perf_counter()
            try:
                item = next(iterator)
            except StopIteration:
                break
            waits.append(time.perf_counter() - before)
            if time.monotonic() > deadline:
                raise RuntimeError("Smoke runtime budget reached; no full training may proceed")
            free, _ = torch.cuda.mem_get_info()
            if free < reserve_mib * 1024**2:
                raise RuntimeError("GPU free-memory reserve reached")
            # Shipped processor rescale is exactly uint8 / 255. Verify below.
            pixels = item["pixels"].to("cuda", non_blocking=True).float().div_(255)
            with torch.inference_mode():
                z = encoder(pixels)
            if not torch.isfinite(z).all():
                raise ValueError("Nonfinite CNN embedding")
            vectors.append(z.cpu().numpy()[0])
            ids.extend(item["interval_id"])
            decodes.extend(item["decode_seconds"].tolist())
            if len(ids) % 4 == 0:
                gpu_samples.append(gpu_snapshot())
            del pixels, z
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        cpu = sum(process.cpu_times()[:2]) - before_cpu
        child_cpu = sum(sum(psutil.Process(pid).cpu_times()[:2]) for pid in child_pids)
        rss = process.memory_info().rss + sum(psutil.Process(pid).memory_info().rss for pid in child_pids)
    finally:
        if workers:
            iterator._shutdown_workers()
            codes = [worker.exitcode for worker in iterator._workers]
        else:
            dataset.close()
            codes = []
    if any(code != 0 for code in codes) or any(psutil.pid_exists(pid) for pid in child_pids):
        raise RuntimeError("Unclean worker shutdown")
    return np.stack(vectors), ids, {"workers": workers, "intervals": len(ids), "frames": 16 * len(ids),
        "wall_seconds_including_first_batch": elapsed, "intervals_per_second": len(ids) / elapsed,
        "parent_cpu_seconds": cpu, "worker_cpu_seconds": child_cpu, "parent_plus_workers_rss_bytes": rss,
        "cpu_core_equivalents": (cpu + child_cpu) / elapsed,
        "loader_wait_seconds": float(sum(waits)), "worker_decode_seconds_sum": float(sum(decodes)),
        "worker_exit_codes": codes, "workers_reaped": True, "gpu_samples_device_wide_not_process_attributable": gpu_samples,
        "peak_torch_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_torch_reserved_bytes": torch.cuda.max_memory_reserved()}


def main(config_path, output):
    config = json.loads(Path(config_path).read_text())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name in ("config", "manifests", "cache", "checkpoints", "reports"):
        (output / name).mkdir()
    write(output / "config/resolved_config.json", config)
    write(output / "config/protocol_lock.json", {"UTC_before_any_fitting": datetime.now(timezone.utc).isoformat(),
          "config_sha256": digest(config_path), "outer_results_inspected": False})
    started = time.monotonic()
    deadline = started + config["smoke"]["maximum_runtime_seconds"]
    torch.set_num_threads(1)
    cv2.setNumThreads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    frame = load_cohort(config["stage2"], config["label2"])
    readiness = {"eligible_intervals": len(frame), "positive_intervals": int(frame.target.sum()),
                 "positive_groups": frame.loc[frame.target == 1, "group_id"].nunique(), "full_evaluation_ready": False}
    try:
        frozen = nested_plan(frame, outer=config["outer_folds"], inner=config["inner_folds"], seed=config["split_seed"])
        write(output / "manifests/outer_splits.json", frozen)
        readiness["full_evaluation_ready"] = True
    except ValueError as exc:
        readiness["blocker"] = str(exc)
    write(output / "manifests/readiness.json", readiness)
    selected = choose_smoke(frame)
    if len(selected) != config["smoke"]["max_intervals"]:
        raise ValueError("Changed audited smoke population")
    small = frame.iloc[selected].copy().reset_index(drop=True)
    train, protected, plan = smoke_partition(frame)
    local_train, local_protected, local_plan = smoke_partition(small)
    if len(local_protected) or set(small.group_id) & set(frame.iloc[protected].group_id):
        raise ValueError("Protected group entered smoke")
    write(output / "manifests/smoke_split.json", {
        "purpose": "development-only OOF integrity; not an outer performance experiment",
        "cohort_train_ids": frame.iloc[train].interval_id.tolist(),
        "protected_ids_not_decoded_or_predicted": frame.iloc[protected].interval_id.tolist(),
        "smoke_ids": small.interval_id.tolist(),
        "OOF": [{"fit_groups": sorted(set(small.iloc[a].group_id)), "prediction_groups": sorted(set(small.iloc[b].group_id))} for a, b in local_plan]})
    inputs = json.loads((Path(config["stage2"]) / "manifests/input_manifest.json").read_text())
    verified = []
    # Hash only the local, authorized MSM pilot sources; no full-dataset scan.
    for item in inputs:
        if digest(item["path"]) != item["sha256"]:
            raise ValueError("Stage 2 input hash changed")
        verified.append(item)
    write(output / "manifests/input_manifest.json", verified)
    sensors, sensor_gates = sensor_features(small, config["data_root"], config["sensor"]["channels"])
    reference = pd.read_csv(Path(config["stage2"]) / "manifests/common_mtc_statistics.csv").set_index("interval_id")
    reference_columns = list(FEATURE_NAMES)
    reference_values = reference.loc[small.interval_id, reference_columns].to_numpy(np.float32)
    maximum_sensor_difference = float(np.max(np.abs(sensors - reference_values)))
    if not np.allclose(sensors, reference_values, rtol=2e-6, atol=1e-4):
        raise ValueError("Stage 2 statistics parity failed")
    write(output / "manifests/sensor_contract.json", {"feature_names": list(FEATURE_NAMES), "gates": sensor_gates,
          "stage2_max_absolute_difference": maximum_sensor_difference})
    before_gpu = gpu_snapshot()
    free, total = torch.cuda.mem_get_info()
    if free < (config["smoke"]["gpu_memory_reserve_mib"] + config["smoke"]["gpu_process_memory_cap_mib"]) * 1024**2:
        raise RuntimeError("Insufficient free GPU memory for bounded admission")
    torch.cuda.set_per_process_memory_fraction(config["smoke"]["gpu_process_memory_cap_mib"] * 1024**2 / total)
    processor, backbone, identity = verified_backbone(config)
    write(output / "manifests/pretrained_model.json", identity)
    encoder = IntervalCNN(backbone, config["visual"]["feature_microbatch"]).cuda().eval()
    probe_data = IntervalPixels(small.iloc[:4], config["stage2"])
    pixels = probe_data[0]["pixels"]
    shipped = processor(images=[pixels[0].permute(1, 2, 0).numpy()], return_tensors="pt")["pixel_values"]
    if not torch.equal(shipped, pixels[:1].float() / 255):
        # Processor float32 multiplication and division can differ by 1 ULP.
        max_preprocessing_error = float((shipped - pixels[:1].float() / 255).abs().max())
        if max_preprocessing_error > 6e-8:
            raise ValueError("Verified processor parity failed")
    else:
        max_preprocessing_error = 0.
    # Float32 scale roundoff is bounded above against the shipped processor.
    with torch.inference_mode():
        baseline = encoder(pixels[None].cuda().float() / 255).cpu().numpy()
    benchmark = []
    reference_vectors = None
    for workers in config["smoke"]["worker_settings"]:
        torch.cuda.reset_peak_memory_stats()
        data = IntervalPixels(small.iloc[:4], config["stage2"])
        values, ids, measured = consume(data, encoder, processor, workers, deadline, config["smoke"]["gpu_memory_reserve_mib"])
        if reference_vectors is None:
            reference_vectors = values
        if not np.array_equal(values, reference_vectors) or not np.array_equal(values[:1], baseline):
            raise ValueError("Worker loading changed numerical inputs/features")
        benchmark.append(measured)
    # Extraction is streaming and stores 896-value features, not decoded images.
    torch.cuda.reset_peak_memory_stats()
    data = IntervalPixels(small, config["stage2"])
    visual, ids, extraction = consume(data, encoder, processor, 0, deadline, config["smoke"]["gpu_memory_reserve_mib"])
    if ids != small.interval_id.tolist() or not np.array_equal(visual[:4], reference_vectors):
        raise ValueError("Prediction unit/order parity failed")
    frozen_gradients_absent = all(p.grad is None and not p.requires_grad for p in backbone.parameters())
    del encoder, backbone
    torch.cuda.empty_cache()
    np.savez_compressed(output / "cache/smoke_features.npz", visual=visual, sensor=sensors, interval_id=np.array(ids))
    fit, fusion, bank, oof_provenance, logs = fit_oof_fusion(small, visual, sensors, local_train, local_plan,
                    config, config["smoke"]["seed"], config["smoke"]["epochs"])
    updates = sum(item["updates"] for item in logs)
    if updates > config["smoke"]["maximum_head_updates"] or not all(item["all_head_parameters_nonzero_gradient"] for item in logs):
        raise ValueError("Smoke budget/gradient requirement failed")
    if time.monotonic() > deadline:
        raise RuntimeError("Smoke exceeded runtime budget")
    checkpoint = output / "checkpoints/development_only.pt"
    save_bundle(checkpoint, *fit[:3], fusion, {"protocol": config["protocol"], "development_only": True,
                "feature_names": list(FEATURE_NAMES), "pretrained_revision": config["visual"]["revision"],
                "fit_ids": ids, "seed": config["smoke"]["seed"]})
    restored = load_bundle(checkpoint)
    probabilities = branch_probabilities(fit, visual, sensors, local_train)
    reloaded = np.column_stack([predict_visual(restored[0], restored[1], visual), restored[2].predict(sensors)])
    reload_error = float(np.max(np.abs(probabilities - reloaded)))
    f2_error = float(np.max(np.abs(fusion.predict(probabilities) - restored[3].predict(reloaded))))
    if reload_error != 0 or f2_error != 0:
        raise ValueError("Checkpoint reload prediction changed")
    if not np.isfinite(averaging(probabilities)).all():
        raise ValueError("Averaging control failed")
    np.savez_compressed(output / "cache/development_oof.npz", probabilities=bank, interval_id=np.array(ids))
    write(output / "manifests/stacking_provenance.json", oof_provenance)
    write(output / "manifests/benchmark.json", {"gpu_before": before_gpu, "gpu_after": gpu_snapshot(),
        "settings": benchmark, "extraction": extraction, "preprocessing_max_absolute_error": max_preprocessing_error,
        "worker_embedding_exact_parity": True, "shared_gpu": True,
        "warning": "Short warm page-cache timings on shared busy T4; device utilization cannot be attributed to MSM; not a sustained exclusive benchmark."})
    write(output / "manifests/smoke_validation.json", {"passed": True, "intervals": len(small), "groups": small.group_id.nunique(),
        "native_counts": {str(k): int(v) for k, v in small.native_label.value_counts().items()},
        "head_updates": updates, "epochs_per_fit": config["smoke"]["epochs"], "base_fits": 3,
        "finite_losses": all(item["finite_losses"] for item in logs), "head_gradients_finite_nonzero": True,
        "backbone_frozen_gradients_absent": frozen_gradients_absent, "checkpoint_branch_max_abs_difference": reload_error,
        "checkpoint_f2_max_abs_difference": f2_error, "outer_predictions": 0, "efficacy_metrics_calculated": False,
        "cnn_frames_forwarded": 16 * (1 + 4 + 4 + len(small)), "total_wall_seconds": time.monotonic() - started,
        "fusion_new_coefficient": fusion.model.coef_[0].tolist(), "fusion_new_intercept": float(fusion.model.intercept_[0])})
    write(output / "provenance.json", {"UTC": datetime.now(timezone.utc).isoformat(), "command": sys.argv,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True)),
        "python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__, "opencv": cv2.__version__,
        "config_sha256": digest(config_path), "device": torch.cuda.get_device_name(0), "input_files_verified": len(verified),
        "source_sha256": {str(path): digest(path) for path in sorted(Path("MILLING DATASET/source/msm").glob("*.py"))},
        "reused_source_sha256": {str(path): digest(path) for path in map(Path, ["src/reassemble/section1_features.py", "src/reassemble/section1_models.py", "MILLING DATASET/source/stage2/frame_contract.py", "MILLING DATASET/source/stage2/audit_sensors.py"])}})
    print(json.dumps({"run": str(output), "smoke_passed": True, "head_updates": updates, "full_evaluation_ready": readiness["full_evaluation_ready"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="MILLING DATASET/configs/stage3_protocol.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.config, args.output)
