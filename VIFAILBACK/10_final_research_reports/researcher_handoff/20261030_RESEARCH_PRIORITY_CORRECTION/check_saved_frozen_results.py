"""Read-only saved-prediction check; no model fitting or protocol changes.

Run from repository root with ma_thesis_env/bin/python -B <this-file>.
Writes a new check receipt beside this script; refuses to overwrite one.
"""
import hashlib
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess

import numpy as np
import psutil
from scipy.special import expit
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "VIFAILBACK"
RUN = "20261029T004900Z"
SEEDS = [42, 123, 20261023]
INPUTS = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    INPUTS[str(path.relative_to(ROOT))] = digest(path)
    return json.loads(path.read_text())


def scores(y, p):
    y, p = np.asarray(y), np.asarray(p)
    assert set(y) == {0, 1} and np.isfinite(p).all()
    assert ((p >= 0) & (p <= 1)).all()
    af = float(average_precision_score(y, p))
    ass = float(average_precision_score(1 - y, 1 - p))
    return {"AP_failure": af, "AP_success": ass, "macro_AP": (af + ass) / 2,
            "AUROC": float(roc_auc_score(y, p))}


def checked_predictions(directory):
    receipt = read(directory / "COMPLETE.json")
    rows = read(directory / "predictions.json")
    assert digest(directory / "predictions.json") == receipt["prediction_sha256"]
    return receipt, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("SAVED_FROZEN_RESULTS_CHECK.json"))
    args = parser.parse_args()
    output_name = str(args.output.resolve().relative_to(ROOT)) if args.output.resolve().is_relative_to(ROOT) else str(args.output)
    assert Path.cwd().resolve() == ROOT, "Run from repository root"
    INPUTS[str(Path(__file__).resolve().relative_to(ROOT))] = digest(Path(__file__).resolve())
    freeze = read(PROJECT / "10_final_research_reports/reproducibility/PROTOCOL_FREEZE.json")
    execution = read(PROJECT / "logs" / RUN / "EXECUTION_PROVENANCE.json")
    identity = {**freeze["implementation"], **execution["reused_source"]}
    assert all(digest(ROOT / p) == s for p, s in identity.items())
    cohort_path = PROJECT / "03_preprocessing/processed_manifests" / RUN / "eligible.json"
    splits_path = PROJECT / "04_evaluation_splits/train_validation_test" / RUN / "fit_partitions.json"
    cohort = read(cohort_path)
    jobs = read(splits_path)
    assert digest(cohort_path) == freeze["eligible_manifest_sha256"]
    assert digest(splits_path) == freeze["split_manifest_sha256"]
    native = {r["episode_index"]: r for r in cohort}
    assert len(native) == 4382 and sum(r["label"] for r in cohort) == 3753
    for job in jobs:
        partitions = list(job["groups"].values())
        assert all(set(a).isdisjoint(b) for i, a in enumerate(partitions) for b in partitions[i + 1:])
        for name, ids in job["ids"].items():
            assert {native[e]["canonical_task_id"] for e in ids} == set(job["groups"][name])

    records, per_fold, schedules = [], [], []
    for seed in SEEDS:
        seen = set()
        for outer in range(3):
            final = next(j for j in jobs if j["outer"] == outer and j["inner"] == -1)
            visual_root = PROJECT / "06_training_experiments/visual_frozen/runs" / RUN / f"seed{seed}"
            sensor_root = PROJECT / "06_training_experiments/sensor_baselines/runs" / RUN / f"seed{seed}"
            root = PROJECT / "06_training_experiments/fusion_experiments/runs" / RUN / "V1" / f"seed{seed}" / f"outer{outer}"
            vr, visual = checked_predictions(visual_root / final["id"])
            sr, sensor = checked_predictions(sensor_root / final["id"])
            fr, fusion = checked_predictions(root)
            assert vr["executed_epochs"] == 100 and fr["group_safe_OOF_verified"]
            assert fr["outer_prediction_sha256"] == {"visual": vr["prediction_sha256"], "sensor": sr["prediction_sha256"]}
            assert [r["episode_index"] for r in visual] == [r["episode_index"] for r in sensor] == [r["episode_index"] for r in fusion] == final["ids"]["A"]
            assert not seen.intersection(final["ids"]["A"])
            seen.update(final["ids"]["A"])
            meta = read(root / "META_TRAINING_PREDICTIONS.json")
            coefficients = read(root / "F2_COEFFICIENTS.json")
            assert digest(root / "META_TRAINING_PREDICTIONS.json") == fr["meta_training_sha256"]
            assert digest(root / "F2_COEFFICIENTS.json") == fr["f2_sha256"]
            assert coefficients["C"] == 1 and not coefficients["balanced"]
            expected_meta = []
            for job in [j for j in jobs if j["outer"] == outer and j["inner"] >= 0]:
                ivr, iv = checked_predictions(visual_root / job["id"])
                isr, iss = checked_predictions(sensor_root / job["id"])
                assert ivr["executed_epochs"] == 100
                schedules.append({"seed": seed, "fit": job["id"], "executed_epochs": 100, "selected_epoch": ivr["selected_epoch"]})
                assert fr["inner_prediction_sha256"][job["id"]] == {"visual": ivr["prediction_sha256"], "sensor": isr["prediction_sha256"]}
                assert [r["episode_index"] for r in iv] == [r["episode_index"] for r in iss] == job["ids"]["A"]
                for v, s in zip(iv, iss):
                    assert v["label"] == s["label"] == native[v["episode_index"]]["label"]
                    expected_meta.append({"episode_index": v["episode_index"], "fit_id": job["id"], "label": v["label"],
                                          "visual_probability": v["probability"], "sensor_probability": s["S3_probability"]})
            assert meta == expected_meta
            assert len({r["episode_index"] for r in meta}) == len(meta)
            assert {r["episode_index"] for r in meta} == set(native) - set(final["ids"]["A"])
            schedules.append({"seed": seed, "fit": final["id"], "executed_epochs": 100, "selected_epoch": vr["selected_epoch"]})
            for v, s, f in zip(visual, sensor, fusion):
                assert v["label"] == s["label"] == f["label"] == native[v["episode_index"]]["label"]
                assert f["visual_probability"] == v["probability"] and f["sensor_probability"] == s["S3_probability"]
            p = np.asarray([[r["visual_probability"], r["sensor_probability"]] for r in fusion], dtype="float32")
            assert np.allclose(p.mean(1), [r["F1_average"] for r in fusion], atol=1e-12, rtol=0)
            reconstructed = expit(p @ np.asarray(coefficients["coefficient"]) + coefficients["intercept"])
            assert np.allclose(reconstructed, [r["F2_probability"] for r in fusion], atol=1e-12, rtol=0)
            fields = {"V1": "visual_probability", "S3": "sensor_probability", "F1_V1": "F1_average", "F2_V1": "F2_probability"}
            saved = {"V1": read(visual_root / final["id"] / "metrics.json"),
                     "S3": read(sensor_root / final["id"] / "metrics.json")["S3"]}
            fm = read(root / "metrics.json")
            saved.update(F1_V1=fm["F1_average"], F2_V1=fm["F2"])
            for model, field in fields.items():
                result = scores([r["label"] for r in fusion], [r[field] for r in fusion])
                assert all(abs(v - saved[model][k]) < 1e-12 for k, v in result.items())
                per_fold.append({"seed": seed, "outer": outer, "model": model, "episodes": len(fusion), **result})
            records.extend({"seed": seed, "episode_index": r["episode_index"], "label": r["label"],
                            **{m: r[k] for m, k in fields.items()}} for r in fusion)
        assert seen == set(native)

    pooled, differences = [], []
    for seed in SEEDS:
        rows = [r for r in records if r["seed"] == seed]
        result = {m: scores([r["label"] for r in rows], [r[m] for r in rows]) for m in fields}
        pooled.extend({"seed": seed, "model": m, "episodes": len(rows), **v} for m, v in result.items())
        for a, b in [("F2_V1", "V1"), ("F2_V1", "S3"), ("F2_V1", "F1_V1"), ("F1_V1", "S3"), ("F1_V1", "V1")]:
            differences.append({"seed": seed, "A": a, "B": b, **{k: result[a][k] - result[b][k] for k in result[a]}})
    process_receipt = read(PROJECT / "logs" / RUN / "CONTROLLER_PROCESS.json")
    controller = psutil.Process(process_receipt["pid"])
    assert abs(controller.create_time() - process_receipt["create_time"]) < .01
    publication = read(PROJECT / "10_final_research_reports/LATEST_PUBLICATION.json")
    assert all(digest(PROJECT / "10_final_research_reports" / p) == s for p, s in publication["reports"].items())
    assert digest(PROJECT / "RESEARCH_COMPLETION_STATUS.md") == publication["completion_status_sha256"]
    assert all(digest(ROOT / p) == s for p, s in identity.items())
    output = {"utc": datetime.now(timezone.utc).isoformat(), "run": RUN,
              "git_HEAD": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "command": "ma_thesis_env/bin/python -B " + str(Path(__file__).resolve().relative_to(ROOT)) + " --output " + output_name,
              "scope": "Saved-prediction consistency, saved OOF lineage and schedule receipts only; no retraining, coefficient refitting, new model selection, checkpoint payload reload, or bootstrap performed.",
              "controller": {"pid": controller.pid, "create_time": controller.create_time(), "status": controller.status()},
              "code_config_reused_source_and_published_reports_match": True,
              "cohort": {"episodes": len(native), "failures": 3753, "no_failures": 629, "tasks": 99},
              "pooled_per_seed": pooled, "within_dataset_differences": differences,
              "per_fold": per_fold, "visual_schedule_receipts": schedules, "input_sha256": INPUTS}
    path = args.output
    with path.open("x") as stream:
        json.dump(output, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"receipt": output_name, "status": "PASS", "per_seed": pooled, "differences": differences}, indent=2))


if __name__ == "__main__":
    main()
