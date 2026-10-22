"""Independent AP recalculation from directly identified CSV rows.

Run from the repository root with its existing Python environment after inference.
Writes verification and diagnostic tables only; never imports either study pipeline.
The default needs only the extracted noise review package; --include-encoder also
checks the completed encoder study in the sibling repository directory.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

for name in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"]:
    os.environ[name] = "2"
if hasattr(os, "sched_getaffinity"):
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

HERE = Path(__file__).resolve().parent
ENCODER = HERE.parent.parent.parent.parent / "rt_detr_encoder_comparison/results/run_01"
NOISE = HERE.parent
KEYS = ["recording_id", "segment_id"]


def table(path):
    frame = pd.read_csv(path, dtype={key: str for key in KEYS})
    assert not frame.duplicated(KEYS).any(), str(path)
    assert set(frame.failure).issubset({0, 1}), str(path)
    return frame.sort_values(KEYS).reset_index(drop=True)


def ap(frame, branch):
    values = frame["p_" + branch].to_numpy()
    assert np.isfinite(values).all() and ((values >= 0) & (values <= 1)).all()
    return float(average_precision_score(frame.failure, values))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-encoder", action="store_true")
    args = parser.parse_args()
    records = []
    selection = pd.read_csv(NOISE / "model_selection/clean_comparison.csv")
    selected = json.loads((NOISE / "model_selection/selected_model.json").read_text())
    selection_banks = {}
    for _, candidate in selection.loc[selection.eligible == True].iterrows():
        frame = table(NOISE / f"model_selection/clean_predictions/{candidate.condition}.csv")
        selection_banks[candidate.condition] = frame
        for branch in ["visual", "sensor", "fused"]:
            value = ap(frame, branch)
            assert abs(value - candidate[branch + "_AP"]) < 1e-12
            records.append(dict(study="clean_selection", condition=candidate.condition,
                                branch=branch, AP=value, samples=len(frame)))
    reference = selection_banks["frozen_16_frames"]
    for frame in selection_banks.values():
        assert frame[KEYS].equals(reference[KEYS]) and np.array_equal(frame.failure, reference.failure)
        np.testing.assert_allclose(frame.p_sensor, reference.p_sensor, atol=5e-15, rtol=0)
    assert selected["condition"] == "frozen_16_frames"
    assert all(ap(frame, "fused") <= ap(reference, "fused") + 1e-12 for frame in selection_banks.values())
    if args.include_encoder:
        enc_metrics = pd.read_csv(ENCODER / "comparison/metrics.csv")
        enc = {}
        for condition in ["cnn_only", "cnn_plus_encoder"]:
            path = ENCODER / f"comparison/identified_outer_predictions_{condition}.csv"
            frame = enc[condition] = table(path)
            for branch in ["visual", "sensor", "fused"]:
                for scope, subset in [("pooled", frame)] + list(frame.groupby("fold_name")):
                    saved = enc_metrics.loc[(enc_metrics.condition == condition) &
                                            (enc_metrics.branch == branch) & (enc_metrics.scope == scope)]
                    assert len(saved) == 1
                    value = ap(subset, branch)
                    assert abs(value - saved.AP.iloc[0]) < 1e-12
                    records.append(dict(study="encoder", condition=condition, branch=branch,
                                        scope=scope, AP=value, samples=len(subset)))
        a, b = enc.values()
        assert a[KEYS].equals(b[KEYS]) and np.array_equal(a.failure, b.failure)
        assert np.array_equal(a.p_sensor, b.p_sensor)
    noise_metrics = pd.read_csv(NOISE / "comparison/robustness_metrics.csv")
    completed = sorted((NOISE / "predictions").glob("**/complete.json"))
    assert completed
    jobs = {}
    costs = []
    for marker in completed:
        info = json.loads(marker.read_text())
        path = marker.parent / "predictions.csv"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == info["predictions_sha256"]
        job = info["job"]
        costs.append(dict(**job, fold=info["fold"], rows=info["rows"],
                          seconds=info["seconds"], failed_rows=info["failed_rows"],
                          prediction_table=str(path.relative_to(NOISE)),
                          predictions_sha256=info["predictions_sha256"]))
        jobs.setdefault((job["family"], job["level"], job["repeat"]), []).append(table(path))
    clean = pd.concat(jobs[("clean", "clean", 0)]).sort_values(KEYS).reset_index(drop=True)
    expected = {"clean": 1, "image_noise": 9, "sensor_noise": 9, "image_blur": 3,
                "frame_loss": 9, "sensor_channel_loss": 9, "sensor_time_loss": 9,
                "missing_modality": 2}
    assert len(jobs) == 51
    for family, count in expected.items():
        assert sum(key[0] == family for key in jobs) == count
    assert all(len(parts) == len(selected["folds"]) for parts in jobs.values())
    assert len(clean) == selected["samples"]
    shifts = []
    invariance = []
    fault_support = []
    for (family, level, repeat), parts in jobs.items():
        frame = pd.concat(parts).sort_values(KEYS).reset_index(drop=True)
        assert not frame.duplicated(KEYS).any()
        assert frame[KEYS].equals(clean[KEYS]) and np.array_equal(frame.failure, clean.failure)
        assert (frame.status == "OK").all()
        if family == "missing_modality":
            surviving = "sensor" if level == "image_absent" else "visual"
            absent = "visual" if surviving == "sensor" else "sensor"
            assert (frame.fallback_policy == surviving + "_only_fallback").all()
            assert frame["p_" + absent].isna().all()
            assert np.array_equal(frame.p_fused, frame["p_" + surviving])
            assert not frame[absent + "_available"].any() and frame[surviving + "_available"].all()
        else:
            assert (frame.fallback_policy == "F2").all()
            assert frame.visual_available.all() and frame.sensor_available.all()
        metadata = [json.loads(value) for value in frame.corruption_metadata]
        pixels = [item for value in metadata for item in value.get("images", [])]
        affected = [value["affected_native_values"] for value in metadata if "affected_native_values" in value]
        fault_support.append(dict(
            family=family, level=level, repeat=repeat, samples=len(frame),
            frames_min=int(frame.effective_frames.min()), frames_max=int(frame.effective_frames.max()),
            channels_min=int(frame.effective_channels.min()), channels_max=int(frame.effective_channels.max()),
            native_shapes=json.dumps(sorted({tuple(item["native_shape"]) for item in pixels if "native_shape" in item})),
            mean_prequantization_pixel_RMS=float(np.mean([item["rms_change"] for item in pixels])) if pixels else None,
            mean_prequantization_clipped_fraction=float(np.mean([item["clipped_fraction"] for item in pixels])) if pixels else None,
            affected_native_positions_min=min(affected) if affected else None,
            affected_native_positions_median=float(np.median(affected)) if affected else None,
            affected_native_positions_max=max(affected) if affected else None))
        unchanged = ("sensor" if family in ["image_noise", "image_blur", "frame_loss"] else
                     "visual" if family in ["sensor_noise", "sensor_channel_loss", "sensor_time_loss"] else None)
        if unchanged:
            difference = float(np.max(np.abs(frame["p_"+unchanged].to_numpy()-clean["p_"+unchanged].to_numpy())))
            assert difference <= 5e-15, "Untouched-branch serialized probabilities changed"
            invariance.append(dict(family=family, level=level, repeat=repeat,
                                   unchanged_branch=unchanged, serialization_max_abs=difference))
        for branch in ["visual", "sensor", "fused"]:
            if family == "missing_modality" and frame["p_" + branch].isna().all():
                continue
            value = ap(frame, branch)
            probability = frame["p_" + branch].to_numpy()
            baseline = clean["p_" + branch].to_numpy()
            shifts.append(dict(family=family, level=level, repeat=repeat, branch=branch,
                               samples=len(frame), mean_probability_shift=float(np.mean(probability-baseline)),
                               mean_absolute_probability_shift=float(np.mean(np.abs(probability-baseline))),
                               mean_signed_error=float(np.mean(probability-frame.failure.to_numpy())),
                               failures_mean_probability=float(probability[frame.failure.to_numpy()==1].mean()),
                               successes_mean_probability=float(probability[frame.failure.to_numpy()==0].mean())))
            saved = noise_metrics.loc[(noise_metrics.family == family) &
                                     (noise_metrics.level == level) &
                                     (noise_metrics.repeat.astype(str) == str(repeat)) &
                                     (noise_metrics.branch == branch) & (noise_metrics.scope == "pooled")]
            assert len(saved) == 1 and abs(value - saved.AP.iloc[0]) < 1e-12
            assert abs((ap(clean, branch)-value)-saved.AP_drop.iloc[0]) < 1e-12
            records.append(dict(study="noise", family=family, level=level, repeat=repeat,
                                branch=branch, AP=value, samples=len(frame)))
    pd.DataFrame(shifts).to_csv(NOISE / "comparison/probability_shifts_and_signed_errors.csv", index=False, float_format="%.17g")
    pd.DataFrame(fault_support).to_csv(NOISE / "comparison/corruption_support.csv", index=False, float_format="%.17g")
    pd.DataFrame(costs).to_csv(NOISE / "comparison/inference_cost.csv", index=False, float_format="%.17g")
    pd.DataFrame(costs).drop(columns="seconds").to_csv(NOISE / "comparison/prediction_table_index.csv", index=False)
    recomputed_noise = pd.DataFrame([row for row in records if row["study"] == "noise"])
    means = []
    stochastic = ["image_noise", "sensor_noise", "frame_loss", "sensor_channel_loss", "sensor_time_loss"]
    for (family, level, branch), group in recomputed_noise.loc[recomputed_noise.family.isin(stochastic)].groupby(["family", "level", "branch"]):
        assert set(group.repeat) == {1, 2, 3}
        value = float(group.AP.mean())
        saved = noise_metrics.loc[(noise_metrics.family == family) & (noise_metrics.level == level) &
                                 (noise_metrics.branch == branch) & (noise_metrics.scope == "pooled") &
                                 (noise_metrics.repeat == "mean_of_3_metrics")]
        assert len(saved) == 1 and abs(value-saved.AP.iloc[0]) < 1e-12
        assert abs((ap(clean, branch)-value)-saved.AP_drop.iloc[0]) < 1e-12
        means.append(dict(family=family, level=level, branch=branch, mean_of_3_AP=value))
    (HERE / "independent_metric_recalculation.json").write_text(
        json.dumps({"passed": True, "completed_prediction_files": len(completed),
                    "recalculated_metrics": records, "verified_means": means,
                    "unchanged_branch_checks": invariance}, indent=2) + "\n")
    print(f"Verified {len(records)} AP values from directly identified rows.")


if __name__ == "__main__":
    main()
