#!/usr/bin/env python3
"""Verify small saved PHM tables; never train, infer, read raw data or replace output.

Run from any directory with the repository's existing NumPy environment. The
default is JSON on stdout. --output uses exclusive creation and fails if present.
This verifies saved-score arithmetic and selected source identities, not training.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / "AGENTS.md").is_file() and (p / "pyproject.toml").is_file())
PHM = "implementations/PHM2026/"
LOEO = PHM + "results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/"
TARGET = PHM + "results/runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/"
FUSION = PHM + "results/runs/phm2026_fusion_latefusion/20260912T054016807597Z-e1911d4f/"
E027 = PHM + "results/runs/phm2026_patchtst_baseline/20260912T053924941825Z-4235307c/"
BROWSING_COMMIT = "e2037412036c5bbfc01fb2323215a37ef0b2e090"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def key(row):
    return row["experiment"], int(row["run"])


def verify():
    identities = {}

    def read(relative):
        data = (ROOT / relative).read_bytes()
        identities[relative] = {"bytes": len(data), "sha256": digest(data)}
        return data

    def rows(relative):
        return list(csv.DictReader(read(relative).decode("utf-8").splitlines()))

    predictions = rows(LOEO + "tables/loeo_predictions.csv")
    saved = json.loads(read(LOEO + "reports/loeo_summary.json"))
    tooth_rows = rows(TARGET + "tables/per_tooth_damage.csv")
    run_rows = rows(TARGET + "tables/run_damage_targets.csv")
    assert len(predictions) == 73 and len(tooth_rows) == 480 and len(run_rows) == 20
    truth = {key(r): float(r["raw_top3_mean_pct"]) for r in run_rows}
    assert len(truth) == len(run_rows)
    assert {r["target_definition_version"] for r in tooth_rows + run_rows} == {"phm2026_image_damage_v3"}
    assert {r["view_aggregation"] for r in tooth_rows} == {"single_deterministic_view"}
    differences = []
    for run_key in truth:
        scoped = [r for r in tooth_rows if key(r) == run_key]
        assert len(scoped) == 24 and {int(r["tooth_id"]) for r in scoped} == set(range(5, 29))
        top3 = np.sort([float(r["per_tooth_damage_candidate_pct"]) for r in scoped])[-3:].mean()
        differences.append(abs(float(top3) - truth[run_key]))
    assert max(differences) < 1e-12
    assert max(abs(float(r["y_true"]) - truth[key(r)]) for r in predictions) < 1e-12
    target_parquet = read(TARGET + "tables/run_damage_targets.parquet")
    assert digest(target_parquet) == "e5e098e01822307791138b83c015307ae74a5b2fdaf80957e413170a343e92f1"

    seed, draws = 20260814, int(saved["bootstrap"]["draws"])
    assert draws == 10000
    metrics, errors_by_model = {}, {}
    for model in sorted({r["model"] for r in predictions}):
        scoped = [r for r in predictions if r["model"] == model]
        keys = [key(r) for r in scoped]
        assert len(set(keys)) == len(keys)
        if model != "rtdetr_r4_image_NOT_loeo":
            assert set(keys) == set(truth) and all(r["fold"] == r["experiment"] for r in scoped)
        else:
            assert len(keys) == 13 and all(r["fold"] == "not_loeo" for r in scoped)
        signed = np.array([float(r["y_pred"]) - float(r["y_true"]) for r in scoped])
        errors = np.abs(signed)
        errors_by_model[model] = dict(zip(keys, errors))
        rng = np.random.default_rng(seed)
        values = np.array([errors[rng.integers(0, len(keys), len(keys))].mean() for _ in range(draws)])
        low, high = np.percentile(values, [2.5, 97.5])
        observed = {"n_runs": len(keys), "mae": float(errors.mean()),
                    "rmse": float(np.sqrt(np.mean(signed ** 2))),
                    "mae_ci95_low": float(low), "mae_ci95_high": float(high)}
        expected = next(r for r in saved["summary"] if r["model"] == model)
        max_difference = max(abs(observed[k] - expected[k]) for k in observed)
        assert max_difference < 1e-12
        metrics[model] = {**observed, "max_abs_difference_from_saved_summary": max_difference}

    paired = {}
    for model in ("fused_all_three", "patchtst_single_encoder"):
        keys = list(errors_by_model[model])
        a = np.array([errors_by_model[model][k] for k in keys])
        b = np.array([errors_by_model["constant_train_mean"][k] for k in keys])
        rng = np.random.default_rng(seed)
        values = []
        for _ in range(draws):
            selected = rng.integers(0, len(keys), len(keys))
            values.append(a[selected].mean() - b[selected].mean())
        low, high = np.percentile(values, [2.5, 97.5])
        observed = {"mean_delta_vs_constant": float(np.mean(values)),
                    "ci95_low": float(low), "ci95_high": float(high)}
        expected = saved["paired_deltas_vs_constant"][model]
        difference = max(abs(observed[k] - expected[k]) for k in observed)
        assert difference < 1e-12
        paired[model] = {"observed_mae_difference": float(a.mean() - b.mean()),
                         "bootstrap_mean_difference": observed["mean_delta_vs_constant"],
                         "ci95_low": float(low), "ci95_high": float(high),
                         "max_abs_difference_from_saved_bootstrap": difference}

    for r in predictions:
        if r["model"] == "constant_train_mean":
            train = saved["folds"][r["fold"]]["train"]
            expected = np.mean([v for k, v in truth.items() if k[0] == train])
            assert abs(float(r["y_pred"]) - expected) < 1e-12
    fixed_mean = np.mean([v for k, v in truth.items() if k[0] == "EXP-B"])
    fixed_mae = np.mean([abs(v - fixed_mean) for k, v in truth.items() if k[0] == "EXP-F"])

    provenance = {}
    for label, location in (("target_v3", TARGET), ("fixed_fusion", FUSION),
                            ("principal_loeo", LOEO), ("E027_misnamed_run", E027)):
        record = json.loads(read(location + "provenance.json"))
        provenance[label] = {k: record[k] for k in ("git", "command", "seed")}
        read(location + "config/resolved_config.yaml")
    assert provenance["E027_misnamed_run"]["command"][0].endswith("train_late_fusion.py")
    lineage = {}
    for label, suffixes in (("fixed_fusion", ("train_late_fusion.py", "fusion/late_fusion.py")),
                            ("principal_loeo", ("loeo_evaluation.py",))):
        commit = provenance[label]["git"]["commit"]
        tree = git("ls-tree", "-r", "--name-only", commit).decode().splitlines()
        matches = {suffix: [p for p in tree if p.endswith(suffix)] for suffix in suffixes}
        assert not any(matches.values())
        lineage[label] = {"recorded_commit": commit, "matching_paths_in_commit": matches,
                          "interpretation": "Recorded commit lacks named source; untracked source lineage unresolved."}

    browsing = {}
    paths = ["src/phm2026/targets/image_damage.py", "src/phm2026/models/rtdetr/regression.py",
             "src/phm2026/features/sensor_minutes.py", "src/phm2026/preprocessing/timeseries.py",
             "src/phm2026/models/patchtst/model.py", "src/phm2026/models/patchtst/regression.py",
             "src/phm2026/fusion/late_fusion.py", "src/phm2026/fusion/modality_fusion.py",
             "scripts/results/loeo_evaluation.py", "scripts/results/sq2_sq3_fusion.py",
             "configs/experiments/phm2026_fusion_latefusion.yaml",
             "experiments/walkthrough/01_rtdetr_scalar_regression/KNOWN_IMPLEMENTATION_ISSUES.md"]
    paths += [(LOEO + "reports/loeo_summary.json")[len(PHM):],
              (TARGET + "config/resolved_config.yaml")[len(PHM):],
              "docs/studies/SQ2_SQ3_RESULTS.json"]
    for relative in paths:
        path = PHM + relative
        current = read(path)
        published = git("show", f"{BROWSING_COMMIT}:{path}")
        assert current == published, path
        browsing[path] = {"commit": BROWSING_COMMIT, "sha256": digest(published),
                          "current_bytes_equal_commit": True,
                          "scope": "Git object comparison; remote accessibility checked separately."}
    read(Path(__file__).resolve().relative_to(ROOT).as_posix())
    return {
        "schema_version": "1.0", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "VERIFIED saved-table arithmetic and selected Git object identities only",
        "head_at_check": git("rev-parse", "HEAD").decode().strip(),
        "command": "ma_thesis_env/bin/python -B implementations/PHM2026/docs/studies/verify_thesis_saved_evidence.py --output implementations/PHM2026/docs/studies/THESIS_SAVED_EVIDENCE_VERIFICATION_20261126.json",
        "python": sys.version.split()[0], "numpy": np.__version__,
        "raw_data_read": False, "training_inference_or_fitting": False,
        "source_modules_imported": False, "historical_artifacts_modified": False,
        "target": {"version": "phm2026_image_damage_v3", "runs": len(truth),
                   "tooth_rows": len(tooth_rows), "tooth_ids": list(range(5, 29)),
                   "top3_max_abs_difference": max(differences),
                   "all_saved_prediction_targets_match_v3": True,
                   "fixed_B_train_F_test_mean_mae": float(fixed_mae)},
        "bootstrap": {"draws": draws, "seed": seed, "resampling_unit": "whole run",
                      "limitations": "Conditional on saved fitted models; no training/selection uncertainty; runs nested in only three experiments."},
        "metrics": metrics, "paired_differences": paired, "run_provenance": provenance,
        "unresolved_source_lineage": lineage, "browsing_source_identity": browsing,
        "checked_file_identities": identities,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(text)
        print(f"Verified saved PHM evidence; wrote {args.output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
