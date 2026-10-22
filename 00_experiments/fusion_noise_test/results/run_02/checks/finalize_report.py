"""Create the completed-run narrative from verified saved metrics only."""
import datetime
import json
import os
from pathlib import Path

for name in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"]:
    os.environ[name] = "2"
if hasattr(os, "sched_getaffinity"):
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])

import pandas as pd

RUN = Path(__file__).resolve().parent.parent
STUDY = RUN.parent.parent


def read(path):
    return json.loads(path.read_text())


def markdown(headers, rows):
    def fmt(value):
        return f"{value:.6f}" if isinstance(value, float) else str(value)
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join(["---"] * len(headers)) + " |"] +
                     ["| " + " | ".join(fmt(value) for value in row) + " |" for row in rows])


def main():
    progress = read(RUN / "progress.json")
    assert progress["status"] == "COMPLETE_ON_PILOT_COVERAGE"
    checked = read(RUN / "checks/independent_metric_recalculation.json")
    assert checked["passed"] and checked["completed_prediction_files"] == 51
    selected = read(RUN / "model_selection/selected_model.json")
    comparison = pd.read_csv(RUN / "model_selection/clean_comparison.csv")
    metrics = pd.read_csv(RUN / "comparison/robustness_metrics.csv")
    intervals = pd.read_csv(RUN / "comparison/paired_differences.csv")
    branch_intervals = pd.read_csv(RUN / "comparison/branch_contrast_intervals.csv")
    assert read(RUN / "checks/branch_contrast_bootstrap.json")["passed"]
    absence = pd.read_csv(RUN / "comparison/absence_fallback.csv")
    costs = pd.read_csv(RUN / "comparison/inference_cost.csv")
    scales = read(RUN / "data/raw_training_scales/fold_01/scales.json")
    processor = read(RUN / "checks/processor_noop.json")
    config = read(STUDY / "config.json")
    replay = pd.read_csv(RUN / "checks/replay/fold_01/differences.csv")

    def score(family, level, branch="fused"):
        repeat = "0" if family in ["clean", "image_blur", "missing_modality"] else "mean_of_3_metrics"
        rows = metrics.loc[(metrics.family == family) & (metrics.level == level) &
                           (metrics.branch == branch) & (metrics.scope == "pooled") &
                           (metrics.repeat.astype(str) == repeat)]
        assert len(rows) == 1 and rows.iloc[0].status == "COMPLETE"
        return rows.iloc[0]

    def interval(family, level):
        row = intervals.loc[(intervals.family == family) & (intervals.level == level) & (intervals.branch == "fused")].iloc[0]
        return f"[{row.lower95:.6f}, {row.upper95:.6f}]"

    clean = score("clean", "clean")
    image = score("image_noise", "strong")
    sensor = score("sensor_noise", "strong")
    main_table = markdown(["Condition", "Visual AP", "Sensor AP", "Fused AP", "AP drop", "95% interval for drop"], [
        ["Clean", score("clean", "clean", "visual").AP, score("clean", "clean", "sensor").AP, clean.AP, 0., "—"],
        ["Image Gaussian σ=0.10", score("image_noise", "strong", "visual").AP, score("image_noise", "strong", "sensor").AP, image.AP, image.AP_drop, interval("image_noise", "strong")],
        ["Sensor Gaussian α=1.00", score("sensor_noise", "strong", "visual").AP, score("sensor_noise", "strong", "sensor").AP, sensor.AP, sensor.AP_drop, interval("sensor_noise", "strong")]])
    selection_table = markdown(["Candidate", "Eligible", "Clean fused AP", "Δ reference / exclusion"], [
        [row.condition, bool(row.eligible), float(row.fused_AP) if row.eligible else "NOT_TESTED",
         float(row.delta_reference) if row.eligible else row.reason] for _, row in comparison.iterrows()])
    fault_rows = []
    harmful = []
    for family in ["image_noise", "sensor_noise", "image_blur", "frame_loss", "sensor_channel_loss", "sensor_time_loss"]:
        for level in ["mild", "medium", "strong"]:
            fused = score(family, level)
            fault_rows.append([family, level, score(family, level, "visual").AP,
                               score(family, level, "sensor").AP, fused.AP, fused.AP_drop, interval(family, level)])
            unchanged = "sensor" if family in ["image_noise", "image_blur", "frame_loss"] else "visual"
            gap = fused.AP-score(family, level, unchanged).AP
            if gap < -1e-12:
                ci = branch_intervals.loc[(branch_intervals.family == family) & (branch_intervals.level == level) & (branch_intervals.contrast == "F2_minus_"+unchanged)].iloc[0]
                harmful.append(f"{family}/{level}: {gap:+.6f} versus the unchanged {unchanged} branch (95% interval [{ci.lower95:.6f}, {ci.upper95:.6f}])")
    fault_table = markdown(["Fault", "Level", "Visual AP", "Sensor AP", "Fused AP", "AP drop", "95% interval"], fault_rows)
    absence_table = markdown(["Declared absence", "Policy", "AP", "Coverage"],
                             [[row.level, row.policy, row.AP, int(row.coverage)] for _, row in absence.iterrows()])
    image_advantage = image.AP-score("image_noise", "strong", "sensor").AP
    sensor_advantage = sensor.AP-score("sensor_noise", "strong", "visual").AP
    harmful_text = ("Observed harmful fusion on these predefined levels (using the prescribed realization means): " + "; ".join(harmful) + ".") if harmful else "No predefined partial-fault level had a lower mean fused AP than its unchanged clean branch on this pilot. This does not establish robustness outside these tested faults."
    elapsed = (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(config["started_utc"])).total_seconds()
    if progress.get("blocker"):
        progress["historical_preparation_blocker"] = progress["blocker"]
    progress.update(blocker=None, remaining_realizations=0, completed_realization_count=51,
                    total_elapsed_seconds=elapsed, remaining_wall_seconds=max(0,config["wall_seconds"]-elapsed))
    (RUN / "progress.json").write_text(json.dumps(progress, indent=2)+"\n")
    choice = (f"Selected `{selected['condition']}`: the canonical original-representation, frozen 16-frame F2 pipeline. "
              f"Clean fused AP is {selected['clean_AP']:.12g}, equal to reference AP {selected['reference_AP']:.12g}; "
              f"improvement over reference is {selected['clean_AP_improvement']:+.12g}. "
              "The eligible encoder candidate scored lower, so the predeclared rule retained F2.")
    coverage = ("PARTIAL_COVERAGE_PILOT: exactly fold_01, 753 actions, 77 failures, 26 recordings. "
                "The encoder comparison completed five paired folds, but the canonical first-study reference has only one complete eligible fold. "
                "The fixed intersection therefore remains one whole fold. The incomplete fine-tuned and 32-frame variants have zero usable folds. "
                "The separate paused two-epoch amendment was not substituted for the pinned five-epoch comparison. "
                "cnn_only is a reference alias/replicate, not an additional candidate chosen by score.")
    evidence = (f"All 753 clean rows replayed before corruption, with maximum probability discrepancy {replay.max_probability_abs.max():.3g}, "
                "fixed tolerance 1e-5, and zero fused-AP discrepancy. "
                "All 51 realizations completed with 753 directly identified rows each; no failed rows or dropped damaged samples. "
                "Fifteen focused CPU tests passed before execution. Runtime checks verified frozen parameters/buffers, disabled dropout, "
                "forbidden-component guards, no-op processing, raw-input invariance, and live/cache agreement. "
                f"Self-review independently recalculated {len(checked['recalculated_metrics'])} AP values and {len(checked['verified_means'])} three-realization means. "
                "This is independent calculation code, not a separate external reviewer.")
    limits = ("DEVELOPMENT-EXPOSED and exploratory: selecting from observed outer scores does not create an untouched test set. "
              "The 2,000 recording-cluster bootstrap resamples (seed 314159) describe conditional uncertainty for this fitted model, "
              "these 26 recordings and the three fixed perturbation realizations. They omit selection and repeated-training uncertainty; "
              "secondary intervals are unadjusted. Equal named severity levels across modalities have different units. "
              "Only the selected F2 pipeline was tested under faults, so no relative robustness claim against discarded candidates is supported. "
              "This complete-action classification study does not establish online detection, causality, adaptive fusion or deployment robustness.")
    method = (f"Image processing policy: `{processor['policy']}`. Noise/blur operate on native floating-point RGB; "
              "the original processor requires nearest-integer uint8 conversion after corruption. The real clean/no-op path matched exactly. "
              "Clipping/RMS metadata describe the floating-point perturbation before that recorded quantization. Blur uses reflect boundaries and radius ceil(3σ). "
              f"Raw sensor scales use {len(scales['identity']['G_keys'])} permitted G actions and {len(scales['names'])} named channels; "
              f"zero-scale channels: {scales['zero_scale_channels']}; undefined channels: {scales['undefined_channels']}. "
              "Calibration/assessment inputs were excluded from scales. Recorded native units are preserved; unspecified source units remain unspecified. "
              "Frame/channel masks are nested seeded removals, and time masks cannot be interpolated away. No classifier, scaler, calibrator, "
              "fusion weight or 0.5 threshold was refitted or tuned. Seeds are 271828, 271829 and 271830.")
    cost = (f"Saved inference job times total {costs.seconds.sum()/3600:.3f} hours, including clean replay and the first raw-scale calculation. "
            "These job times exclude preparation, model construction, evaluation and packaging. Total elapsed time remains measured from the "
            "original task start, including waiting and the earlier pilot; budgets were not reset. See inference_cost.csv and resource observations. "
            "The earlier run_01 precision failure and its documented repair remain preserved; run_02 completed full clean replay after that repair. "
            "No new run_02 inference failure remains unresolved.")
    next_decision = "Require complete matched-fold and independent-recording validation before adopting or claiming a robust winner; do not infer deployment readiness from this one-fold pilot."
    selection_report = f"""# Clean model selection — locked before noise

{choice}

{selection_table}

{coverage}

The canonical source is `{config['visual_run']}`. Encoder results come from `{config['encoder_run']}`. Eligibility used direct keys, identical labels and complete-fold rows, compatible memberships/fitting policy, and traceable replayable components before ranking. The unrounded pooled clean fused AP rule used tolerance 1e-12; visual-only AP and corrupted results played no part. The reference was retained because no eligible newer candidate exceeded it. The encoder-minus-reference pilot interval is in `clean_comparison.csv`; numerical selection is not a significance claim.

The user explicitly authorized this new pre-noise selection after encoder completion. The original run_01 lock is preserved, and no corrupted assessment predictions existed when run_02 was locked. See `selected_model.json`, `selection_lock.json`, `selected_fold_components.json`, and `../provenance/pre_noise_lock_observation.json`. Actual per-fold fits, coefficients and thresholds are retained by identity. The earlier partial pilot was not silently rewritten.

Direct clean evidence: `clean_predictions/frozen_16_frames.csv` and `clean_predictions/cnn_plus_encoder.csv`. These upstream selection tables are distinct from newly replayed `../predictions/clean/clean/repeat_00/fold_01/predictions.csv`.

{limits}

Evidence checked: directly identified clean predictions, eligibility/component records, locked selection and complete clean replay. Still uncertain: untested candidates and full-coverage winner selection. Defensible conclusion: retain the original F2 on the eligible common fold under the fixed rule.
"""
    (RUN / "model_selection/selection_report.md").write_text(selection_report)
    result = f"""# COMPLETE_ON_PILOT_COVERAGE — selected-model robustness

{choice}

{coverage}

{main_table}

Stochastic entries are means of three independently computed metrics, not AP of averaged probabilities or pooled repeated subjects. AP drop is clean minus corrupted; positive values mean deterioration. Failure is class 1. The image endpoint is the prescribed strongest Gaussian σ=0.10, and the sensor endpoint is α=1.00 times G-only raw-channel SD.

Under strongest image Gaussian noise, fused AP minus the unchanged sensor branch is {image_advantage:+.6f}. Under strongest sensor Gaussian noise, fused AP minus the unchanged visual branch is {sensor_advantage:+.6f}. A negative value identifies harmful fusion relative to the surviving clean branch for that named fault; it is not a universal modality-importance ranking. All partial faults retain the same F2 function, with no fault-aware switching.

{harmful_text}

## Every prescribed partial fault

{fault_table}

## Known complete absence — separate routing policy

{absence_table}

These are explicit sensor-only and visual-only fallbacks, not the learned F2 function. The absent branch has an unavailable probability rather than an invented zero. Both absent is excluded and tested to abstain. No partial-fault curve silently switches to fallback.

## Execution, checks and limits

{evidence}

{method}

{cost}

{limits}

## Direct review paths

`model_selection/clean_comparison.csv` and `model_selection/clean_predictions/` reproduce selection. `comparison/prediction_table_index.csv` identifies all 51 actual prediction tables by path and SHA256. `comparison/robustness_metrics.csv` includes each realization and distinct pooled/fold metrics; `paired_differences.csv` includes interval replicate counts. `probability_shifts_and_signed_errors.csv`, `corruption_support.csv`, `modality_sensitivity.csv`, `branch_contrast_intervals.csv`, `reliability_bins.csv`, `absence_fallback.csv`, and `plots/` supply diagnostics. Raw signals/videos, feature caches and model blobs are excluded from the verified review ZIP and referenced by identity.

Recalculate all primary AP values and realization means from the repository root with `ma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/results/run_02/checks/recalculate_metrics.py`. This writes verification and diagnostic tables only; it does not run predictors.

Teaching chain: clean results -> eligibility and fixed common coverage -> locked selected pipeline -> one-modality raw-input faults -> branch and F2 predictions -> matched metrics -> bounded conclusion.

Recommended next decision: {next_decision}

Evidence checked: source and upstream provenance, focused synthetic tests, actual clean/corrupted inference, frozen-state checks, and independently recalculated saved-table metrics. Still uncertain: untested candidates, broader recording coverage, model-selection/training variability and deployment faults. Defensible conclusion: the named synthetic faults characterize this fixed F2 pipeline on the stated pilot only.
"""
    (RUN / "comparison/RESULTS_SUMMARY.md").write_text(result)
    (RUN / "README_FIRST.md").write_text(f"""# COMPLETE_ON_PILOT_COVERAGE

{choice}

Coverage: fold_01, 753 actions, 77 failures, 26 recordings. All 51 prescribed clean/fault/absence realizations completed. No retraining, recalibration or threshold tuning occurred.

{main_table}

The canonical reference has only one complete eligible fold; the three fine-tuned/32-frame alternatives remain untested. Results are DEVELOPMENT-EXPOSED and exploratory. Five-fold encoder results are a separate comparison and cannot replace this pilot denominator.

- [Selection report](model_selection/selection_report.md) and [clean comparison](model_selection/clean_comparison.csv)
- [Results and all fault levels](comparison/RESULTS_SUMMARY.md)
- [All prediction paths and hashes](comparison/prediction_table_index.csv)
- [Metrics](comparison/robustness_metrics.csv), [paired intervals](comparison/paired_differences.csv), [review package](REVIEW_PACKAGE.zip)

Recommended next decision: {next_decision}

Evidence checked: clean replay, frozen input-level inference and saved-table recalculation. Still uncertain: full coverage and external generalization. Defensible conclusion: completed robustness evidence for this fixed pipeline on pilot coverage.
""")
    (RUN / "how_to_resume.md").write_text("# Completed on the locked pilot coverage\n\nAll 51 realizations finished. No further inference or model selection is scheduled. The original deadline was retained. For metric-only recalculation, use:\n\n```bash\nma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/results/run_02/checks/recalculate_metrics.py\n```\n\nThe separately checkpoint-paused visual task is resumed only under the user's explicit pause/complete/resume instruction; see the resume receipt in provenance. This does not authorize another noise or encoder experiment.\n")
    print(main_table)


if __name__ == "__main__":
    main()
