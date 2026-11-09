"""Stage 4 dependency audit. Scientific gates precede model fitting or scoring."""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import itertools
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import psutil
import torch
from transformers import RTDetrForObjectDetection

from .data import digest, load_cohort, sensor_features, FEATURE_NAMES
from .splits import nested_plan, grouped_plan
from .transfer import compatible_cnn_state, validated_source
from .smoke import write, gpu_snapshot


def save_csv(path, frame):
    with Path(path).open("x", newline="") as stream:
        frame.to_csv(stream, index=False)


def snapshot_json(path, destination):
    data = json.loads(Path(path).read_text())
    write(destination, data)
    return data


def audit_prior_artifacts(protocol):
    evidence, seen = [], set()
    for folder in (protocol["stage1"], protocol["stage2"], protocol["stage3"]):
        run = Path(folder)
        manifest = run / "manifests/output_manifest.json"
        checked = 0
        for item in json.loads(manifest.read_text())["files"]:
            path = Path(item["path"])
            # Shared navigation/ignore files evolved intentionally in later stages.
            if str(path) in seen or (folder != protocol["stage3"] and not (
                    path.is_relative_to(run) or path.is_relative_to("MILLING DATASET/source") or path.is_relative_to("MILLING DATASET/tests"))):
                continue
            if not path.exists() or digest(path) != item["sha256"]:
                raise ValueError("Prior-stage input/source artifact changed: " + str(path))
            seen.add(str(path))
            checked += 1
        evidence.append({"run": folder, "manifest_sha256": digest(manifest), "unique_artifacts_checked": checked})
    inputs = {}
    for folder in (protocol["stage1"], protocol["stage2"]):
        for item in json.loads((Path(folder) / "manifests/input_manifest.json").read_text()):
            path = item["path"]
            if path not in inputs:
                if not Path(path).is_file() or digest(path) != item["sha256"]:
                    raise ValueError("MSM raw input hash mismatch: " + path)
                inputs[path] = item
    return evidence, list(inputs.values())


def main(config_path, output):
    started = time.perf_counter()
    process = psutil.Process()
    cpu_before = sum(process.cpu_times()[:2])
    config = json.loads(Path(config_path).read_text())
    protocol = json.loads(Path(config["stage3_config"]).read_text())
    protocol["stage3"] = config["stage3_run"]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name in ("config", "manifests", "evidence", "reports", "figures"):
        (output / name).mkdir()
    write(output / "config/resolved_config.json", config)
    # Preserve exact bytes of the frozen source configuration, including its hash.
    with (output / "config/stage3_protocol.original.json").open("xb") as stream:
        stream.write(Path(config["stage3_config"]).read_bytes())
    lock = json.loads((Path(config["stage3_run"]) / "config/protocol_lock.json").read_text())
    if digest(config["stage3_config"]) != lock["config_sha256"]:
        raise ValueError("Stage 3 scientific protocol changed")
    for key in ("training_seeds", "outer_folds", "inner_folds"):
        if config[key] != protocol[key]:
            raise ValueError("Unmatched frozen setting: " + key)
    torch.set_num_threads(1)
    gpu = gpu_snapshot()
    prior, raw = audit_prior_artifacts(protocol)
    write(output / "manifests/prior_stage_integrity.json", prior)
    write(output / "manifests/input_manifest.json", raw)
    frame = load_cohort(protocol["stage2"], protocol["label2"])
    sensors, sensor_gates = sensor_features(frame, protocol["data_root"], protocol["sensor"]["channels"])
    reference = pd.read_csv(Path(protocol["stage2"]) / "manifests/common_mtc_statistics.csv").set_index("interval_id")
    ref = reference.loc[frame.interval_id, list(FEATURE_NAMES)].to_numpy(np.float32)
    if not np.allclose(sensors, ref, rtol=2e-6, atol=1e-4):
        raise ValueError("Independent Stage 4 MTC reconstruction differs")
    write(output / "manifests/interval_contract_check.json", {"intervals": len(frame),
          "feature_width": sensors.shape[1], "statistics_max_abs_difference": float(np.max(np.abs(sensors - ref))),
          "native_annotation_and_frame_policy_revalidated": True, "sensors_not_used_for_fitting": True})
    save_csv(output / "manifests/sensor_coverage_audit.csv", pd.DataFrame(sensor_gates))
    groups = []
    for group, rows in frame.groupby("group_id", sort=True):
        groups.append({"group_id": group, "machine": rows.machine.iloc[0], "intervals": len(rows),
                       "native_0": int(sum(rows.native_label == 0)), "native_1": int(sum(rows.native_label == 1)),
                       "native_2": int(sum(rows.native_label == 2)), "positive_intervals": int(rows.target.sum()),
                       "binary_prevalence": float(rows.target.mean())})
    save_csv(output / "manifests/cohort_by_experiment.csv", pd.DataFrame(groups))
    machines = []
    for machine, rows in frame.groupby("machine", sort=True):
        machines.append({"machine": machine, "intervals": len(rows), "groups": rows.group_id.nunique(),
                         "positive_groups": rows.loc[rows.target == 1, "group_id"].nunique(),
                         "native_0": int(sum(rows.native_label == 0)), "native_1": int(sum(rows.native_label == 1)),
                         "native_2": int(sum(rows.native_label == 2)), "binary_prevalence": float(rows.target.mean())})
    save_csv(output / "manifests/cohort_by_machine.csv", pd.DataFrame(machines))
    split = {"ready": False, "outer_folds": protocol["outer_folds"], "inner_folds": protocol["inner_folds"],
             "cohort_intervals": len(frame), "positive_groups": frame.loc[frame.target == 1, "group_id"].nunique()}
    try:
        planned = nested_plan(frame, outer=protocol["outer_folds"], inner=protocol["inner_folds"], seed=protocol["split_seed"])
        split["ready"] = True
        write(output / "manifests/frozen_nested_splits.json", planned)
    except ValueError as exc:
        split["reason"] = str(exc)
    write(output / "manifests/split_gate.json", split)
    # Examine secondary machine transfer feasibility without scoring any model.
    cross = []
    for training_machine, test_machine in itertools.permutations(sorted(frame.machine.unique()), 2):
        train = np.flatnonzero(frame.machine.to_numpy() == training_machine)
        test = np.flatnonzero(frame.machine.to_numpy() == test_machine)
        entry = {"train_machine": training_machine, "test_machine": test_machine,
                 "train_intervals": len(train), "test_intervals": len(test),
                 "train_positive_groups": frame.iloc[train].loc[lambda x: x.target == 1, "group_id"].nunique(),
                 "test_positive_groups": frame.iloc[test].loc[lambda x: x.target == 1, "group_id"].nunique(),
                 "same_common_sensor_schema": True, "both_classes_train_and_test": bool(frame.iloc[train].target.nunique() == frame.iloc[test].target.nunique() == 2),
                 "matched_F2_OOF_ready": False, "model_fits": 0, "test_predictions": 0}
        try:
            grouped_plan(frame, train, folds=protocol["inner_folds"], seed=protocol["split_seed"] + 100)
            entry["matched_F2_OOF_ready"] = True
        except ValueError as exc:
            entry["reason"] = str(exc)
        cross.append(entry)
    write(output / "manifests/cross_machine_feasibility.json", cross)
    clusters = pd.read_csv(Path(protocol["stage1"]) / "manifests/reference_date_groups.csv")
    group_date = {g: f"{row.machine}/{int(row.filename_reference_date)}" for row in clusters.itertuples() for g in row.groups.split(";")}
    date_groups = frame.group_id.map(group_date)
    write(output / "manifests/dependency_group_audit.json", {"nominal_experiment_groups": frame.group_id.nunique(),
        "machine_reference_date_clusters": date_groups.nunique(),
        "positive_machine_reference_date_clusters": date_groups[frame.target == 1].nunique(),
        "physical_tool_session_independence_resolved": False})

    phase = Path(config["reassemble_phase1_root"])
    execution = phase / "26102026_execution/26102026_main_run_01"
    for name in ("PHASE1_COMPLETED_FIT_INDEX.json", "PHASE1_CONTROLLER_STATUS.json", "PHASE1_PROGRESS.json"):
        if (execution / name).is_file():
            snapshot_json(execution / name, output / "evidence" / name)
    gate = snapshot_json(phase / "26102026_evidence/PHASE1_FULL_CNN_GATE.json", output / "evidence/PHASE1_FULL_CNN_GATE.json")
    plan = json.loads((phase / "26102026_evidence/PHASE1_FIT_PLAN.json").read_text())
    rule = config["source_rule"]
    job = next(j for j in plan if j["outer_fold_original"] == rule["outer_fold_original"] and j["role"] == rule["role"])
    source_folder = execution / f"26102026_seed{rule['seed']}_{rule['arm']}_outer{rule['outer_fold_original']+1}_{rule['role'].replace('_','')}"
    candidates = []
    for folder in sorted(execution.glob("26102026_seed*")):
        if not folder.is_dir():
            continue
        receipt_path = folder / "PHASE1_FIT_COMPLETE.json"
        checkpoint = folder / "PHASE1_BEST_MODEL.pt"
        item = {"folder": str(folder), "completion_receipt": receipt_path.exists(), "selected_checkpoint_exists": checkpoint.exists(),
                "source_eligible": False, "active_checkpoint_payload_read": False}
        if receipt_path.is_file():
            receipt = json.loads(receipt_path.read_text())
            item.update(arm=receipt["arm"], seed=receipt["seed"], job_index=receipt["job_index"],
                        receipt_sha256=digest(receipt_path))
            if checkpoint.is_file() and digest(checkpoint) != receipt["selected_model_sha256"]:
                raise ValueError("Completed Phase 1 selected model hash mismatch")
            if receipt["arm"] == "C_full_finetuned16":
                item["source_eligible"] = True
            else:
                item["reason"] = "Completed frozen B head has no REASSEMBLE-trained full CNN"
        else:
            item["reason"] = "Active/incomplete fit; no final completion receipt"
        candidates.append(item)
    completed_c = sum(item.get("arm") == "C_full_finetuned16" and item["completion_receipt"] for item in candidates)
    source = {"ready": False, "canonical_source_folder": str(source_folder), "rule": rule,
              "canonical_job_index": job["job_index"], "completed_C_fits_observed": completed_c,
              "full_150_fit_completion_marker_exists": (execution / "PHASE1_ALL_COMPLETE.json").exists(),
              "full_matrix_completion_required_for_single_valid_source": False, "source_numeric_gate": gate["status"],
              "candidates": candidates}
    try:
        payload, receipt = validated_source(source_folder, rule["seed"], job["job_index"])
        source["ready"] = True
        source["source_checkpoint_sha256"] = receipt["selected_model_sha256"]
    except ValueError as exc:
        source["reason"] = str(exc)
    write(output / "manifests/source_checkpoint_gate.json", source)

    # CPU-only structural audit: original pretrained model and a diagnostic-only
    # immutable full-CNN preflight payload. The latter is NEVER condition R.
    base = json.loads(Path(protocol["reassemble_config"]).read_text())
    expected = json.loads(Path(protocol["pretrained_identity"]).read_text())
    weights = Path(base["data_root"]) / "cache/section1_models" / protocol["visual"]["revision"]
    identities = []
    for name, item in expected["files"].items():
        if digest(weights / name) != item["sha256"]:
            raise ValueError("Original pretrained weight identity mismatch")
        identities.append({"path": str(weights / name), **item})
    model = RTDetrForObjectDetection.from_pretrained(weights, local_files_only=True).model.backbone.model.eval().requires_grad_(False)
    diagnostic = execution / "26102026_full_cnn_preflight_01/PHASE1_RELOAD_MODEL.pt"
    diagnostic_receipt = execution / "26102026_full_cnn_preflight_01/PHASE1_FULL_CNN_RELOAD.json"
    diag_info = json.loads(diagnostic_receipt.read_text())
    if digest(diagnostic) != diag_info["model_sha256"]:
        raise ValueError("Diagnostic full-CNN payload identity mismatch")
    diagnostic_payload = torch.load(diagnostic, map_location="cpu", weights_only=True)
    compatible, excluded = compatible_cnn_state(diagnostic_payload["model"], model.state_dict())
    changed = [name for name, value in compatible.items() if not torch.equal(value, model.state_dict()[name])]
    transfer = {"original_pretrained_files": identities, "original_backbone_parameters": sum(p.numel() for p in model.parameters()),
        "original_backbone_state_tensors": len(model.state_dict()), "compatible_CNN_tensors_in_diagnostic_payload": len(compatible),
        "missing_or_extra_CNN_tensors": 0, "shape_dtype_or_finite_errors": 0,
        "excluded_source_keys": excluded, "diagnostic_tensors_changed_vs_P": len(changed),
        "normalization_weight_bias_parameter_to_buffer_mapping": "same names/shapes; values included, then frozen in MSM",
        "diagnostic_checkpoint": str(diagnostic), "diagnostic_checkpoint_sha256": diag_info["model_sha256"],
        "diagnostic_used_as_R": False, "diagnostic_used_on_MSM": False,
        "scope": "Structural compatibility only; not transfer accuracy or a selected source checkpoint"}
    write(output / "manifests/CNN_transfer_compatibility.json", transfer)
    del model, diagnostic_payload, compatible

    # Strict evaluation admission. Failed science gates end this execution
    # without fitting, predictions, replacement folds or source substitutions.
    status = "BLOCKED_COHORT_AND_SOURCE" if not split["ready"] and not source["ready"] else "BLOCKED_COHORT" if not split["ready"] else "BLOCKED_SOURCE" if not source["ready"] else "DEPENDENCIES_READY"
    if status == "DEPENDENCIES_READY":
        raise RuntimeError("Dependencies unexpectedly changed; require a separately validated resumable evaluation runner before fitting")
    entries = [{"condition": arm, "seed": seed, "outer_fold": fold, "model": name, "status": status,
                "fit_count": 0, "prediction_count": 0, "AP": None, "AUROC": None,
                "test_prevalence": None, "Brier": None, "log_loss": None}
               for arm, seed, fold, name in itertools.product(config["conditions"], config["training_seeds"], range(3), config["models"])]
    save_csv(output / "manifests/planned_results_status.csv", pd.DataFrame(entries))
    save_csv(output / "manifests/predictions.csv", pd.DataFrame(columns=["interval_id", "group_id", "native_label", "target", "condition", "seed", "outer_fold", "model", "probability", "prediction", "checkpoint_sha256"]))
    save_csv(output / "manifests/training_curves.csv", pd.DataFrame(columns=["condition", "seed", "outer_fold", "inner_fold", "epoch", "training_loss", "validation_loss", "optimizer_updates", "elapsed_seconds"]))
    write(output / "manifests/selected_checkpoints.json", {"selected": [], "reason": status,
          "source_checkpoint_selected": None, "training_started": False,
          "Stage3_development_checkpoint_not_promoted": True})
    # Plot observed class support, never invented loss/performance curves.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    table = pd.DataFrame(groups)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    bottom = np.zeros(len(table))
    for label, color, title in (("native_0", "#5b8db8", "0: stable normal"), ("native_1", "#c44e52", "1: abnormal cutting"), ("native_2", "#d6ae40", "2: stable defective tool")):
        ax.bar(table.group_id, table[label], bottom=bottom, label=title, color=color)
        bottom += table[label].to_numpy()
    ax.set_ylabel("Verified cutting intervals")
    ax.set_title("MSM verified cohort: only two experiments contain positive cuts")
    ax.tick_params(axis="x", labelrotation=18)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "figures/cohort_class_coverage.png", dpi=160)
    plt.close(fig)
    write(output / "manifests/execution_status.json", {"status": status, "scientific_gates_passed": False,
        "stage4_execution_authorized": True, "historical_stage3_full_matrix_flag_is_not_permission_blocker": True,
        "MSM_model_fits": 0, "MSM_optimizer_updates": 0, "MSM_CNN_frame_forwards": 0,
        "MSM_outer_predictions": 0, "training_checkpoints": 0, "training_curves": 0,
        "performance_metrics_or_intervals_estimated": False, "training_GPU_seconds": 0,
        "scientific_reason": [split.get("reason"), source.get("reason")],
        "no_industrial_or_alternative_split_substitution": True})
    write(output / "provenance.json", {"created_UTC": datetime.now(timezone.utc).isoformat(), "command": sys.argv,
        "Git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "tracked_dirty": bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True)),
        "python": platform.python_version(), "software": {name: version(name) for name in ("torch", "transformers", "numpy", "pandas", "scikit-learn", "pytest", "psutil")},
        "configuration_sha256": digest(config_path), "frozen_stage3_configuration_sha256": lock["config_sha256"],
        "source_sha256": {str(p): digest(p) for p in Path("MILLING DATASET/source/msm").glob("*.py")},
        "GPU_observation": gpu, "CUDA_context_created_by_stage4": torch.cuda.is_initialized(),
        "audit_wall_seconds": time.perf_counter() - started, "audit_CPU_seconds": sum(process.cpu_times()[:2]) - cpu_before,
        "audit_peak_RSS_bytes": process.memory_info().rss, "MSM_training_GPU_seconds": 0,
        "MSM_training_and_prediction_wall_seconds": 0, "immutable_MSM_raw_inputs_verified": len(raw)})
    print(json.dumps({"run": str(output), "status": status, "source_C_completed": completed_c,
                      "verified_examples": len(frame), "outer_predictions": 0}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="MILLING DATASET/configs/stage4_execution.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.config, args.output)
