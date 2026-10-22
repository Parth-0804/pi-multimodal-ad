# COMPLETE_ON_PILOT_COVERAGE — selected-model robustness

Selected `frozen_16_frames`: the canonical original-representation, frozen 16-frame F2 pipeline. Clean fused AP is 0.307928835369, equal to reference AP 0.307928835369; improvement over reference is +0. The eligible encoder candidate scored lower, so the predeclared rule retained F2.

PARTIAL_COVERAGE_PILOT: exactly fold_01, 753 actions, 77 failures, 26 recordings. The encoder comparison completed five paired folds, but the canonical first-study reference has only one complete eligible fold. The fixed intersection therefore remains one whole fold. The incomplete fine-tuned and 32-frame variants have zero usable folds. The separate paused two-epoch amendment was not substituted for the pinned five-epoch comparison. cnn_only is a reference alias/replicate, not an additional candidate chosen by score.

| Condition | Visual AP | Sensor AP | Fused AP | AP drop | 95% interval for drop |
| --- | --- | --- | --- | --- | --- |
| Clean | 0.200401 | 0.290531 | 0.307929 | 0.000000 | — |
| Image Gaussian σ=0.10 | 0.123958 | 0.290531 | 0.284640 | 0.023289 | [-0.003184, 0.042857] |
| Sensor Gaussian α=1.00 | 0.200401 | 0.127743 | 0.169409 | 0.138520 | [0.070831, 0.221115] |

Stochastic entries are means of three independently computed metrics, not AP of averaged probabilities or pooled repeated subjects. AP drop is clean minus corrupted; positive values mean deterioration. Failure is class 1. The image endpoint is the prescribed strongest Gaussian σ=0.10, and the sensor endpoint is α=1.00 times G-only raw-channel SD.

Under strongest image Gaussian noise, fused AP minus the unchanged sensor branch is -0.005891. Under strongest sensor Gaussian noise, fused AP minus the unchanged visual branch is -0.030992. A negative value identifies harmful fusion relative to the surviving clean branch for that named fault; it is not a universal modality-importance ranking. All partial faults retain the same F2 function, with no fault-aware switching.

Observed harmful fusion on these predefined levels (using the prescribed realization means): image_noise/medium: -0.000060 versus the unchanged sensor branch (95% interval [-0.030565, 0.021237]); image_noise/strong: -0.005891 versus the unchanged sensor branch (95% interval [-0.032703, 0.018163]); sensor_noise/medium: -0.001707 versus the unchanged visual branch (95% interval [-0.068132, 0.056531]); sensor_noise/strong: -0.030992 versus the unchanged visual branch (95% interval [-0.096683, 0.016000]).

All four negative fusion-minus-unchanged-branch intervals include zero. These point estimates flag possible harmful fusion; they do not establish a reliable population disadvantage. Under the prescribed strongest channel-loss and time-loss faults, fused AP falls to 0.219848 and 0.240681 respectively. Frame-loss effects are small here and their intervals include zero; the observed increases do not establish a benefit from dropping frames.

## Every prescribed partial fault

| Fault | Level | Visual AP | Sensor AP | Fused AP | AP drop | 95% interval |
| --- | --- | --- | --- | --- | --- | --- |
| image_noise | mild | 0.140204 | 0.290531 | 0.296506 | 0.011423 | [-0.001809, 0.020969] |
| image_noise | medium | 0.113465 | 0.290531 | 0.290470 | 0.017459 | [0.002081, 0.028774] |
| image_noise | strong | 0.123958 | 0.290531 | 0.284640 | 0.023289 | [-0.003184, 0.042857] |
| sensor_noise | mild | 0.200401 | 0.257773 | 0.281512 | 0.026417 | [0.012668, 0.043274] |
| sensor_noise | medium | 0.200401 | 0.166555 | 0.198693 | 0.109235 | [0.062174, 0.170328] |
| sensor_noise | strong | 0.200401 | 0.127743 | 0.169409 | 0.138520 | [0.070831, 0.221115] |
| image_blur | mild | 0.195552 | 0.290531 | 0.303867 | 0.004061 | [-0.015539, 0.017008] |
| image_blur | medium | 0.182979 | 0.290531 | 0.293555 | 0.014374 | [-0.015755, 0.035023] |
| image_blur | strong | 0.160365 | 0.290531 | 0.290537 | 0.017391 | [-0.015360, 0.038762] |
| frame_loss | mild | 0.193364 | 0.290531 | 0.307673 | 0.000256 | [-0.001785, 0.002424] |
| frame_loss | medium | 0.188560 | 0.290531 | 0.309524 | -0.001596 | [-0.004745, 0.001618] |
| frame_loss | strong | 0.188281 | 0.290531 | 0.311094 | -0.003165 | [-0.009155, 0.002591] |
| sensor_channel_loss | mild | 0.200401 | 0.274432 | 0.285684 | 0.022245 | [-0.013027, 0.055173] |
| sensor_channel_loss | medium | 0.200401 | 0.227762 | 0.243661 | 0.064267 | [0.006799, 0.123887] |
| sensor_channel_loss | strong | 0.200401 | 0.201146 | 0.219848 | 0.088081 | [0.018610, 0.162135] |
| sensor_time_loss | mild | 0.200401 | 0.287031 | 0.310286 | -0.002357 | [-0.032403, 0.036023] |
| sensor_time_loss | medium | 0.200401 | 0.289672 | 0.309061 | -0.001132 | [-0.041240, 0.051536] |
| sensor_time_loss | strong | 0.200401 | 0.218541 | 0.240681 | 0.067248 | [0.004979, 0.148065] |

## Known complete absence — separate routing policy

| Declared absence | Policy | AP | Coverage |
| --- | --- | --- | --- |
| image_absent | sensor_only_fallback | 0.290531 | 753 |
| sensor_absent | visual_only_fallback | 0.200401 | 753 |

These are explicit sensor-only and visual-only fallbacks, not the learned F2 function. The absent branch has an unavailable probability rather than an invented zero. Both absent is excluded and tested to abstain. No partial-fault curve silently switches to fallback.

## Execution, checks and limits

All 753 clean rows replayed before corruption, with maximum probability discrepancy 4.19e-08, fixed tolerance 1e-5, and zero fused-AP discrepancy. All 51 realizations completed with 753 directly identified rows each; no failed rows or dropped damaged samples. Fifteen focused CPU tests passed before execution. Runtime checks verified frozen parameters/buffers, disabled dropout, forbidden-component guards, no-op processing, raw-input invariance, and live/cache agreement. Self-review independently recalculated 157 AP values and 45 three-realization means. This is independent calculation code, not a separate external reviewer. The saved-table reviewer initially demanded exact binary equality for copied clean sensor probabilities; a measured one-ULP serialization difference was resolved using its existing 5e-15 CSV diagnostic bound. No scientific tolerance or prediction changed; see checks/metric_review_repair_01.json.

Image processing policy: `round_nearest_uint8_after_float_corruption`. Noise/blur operate on native floating-point RGB; the original processor requires nearest-integer uint8 conversion after corruption. The real clean/no-op path matched exactly. Clipping/RMS metadata describe the floating-point perturbation before that recorded quantization. Blur uses reflect boundaries and radius ceil(3σ). Raw sensor scales use 2966 permitted G actions and 22 named channels; zero-scale channels: []; undefined channels: []. Calibration/assessment inputs were excluded from scales. Recorded native units are preserved; unspecified source units remain unspecified. Frame/channel masks are nested seeded removals, and time masks cannot be interpolated away. No classifier, scaler, calibrator, fusion weight or 0.5 threshold was refitted or tuned. Seeds are 271828, 271829 and 271830.

Saved inference job times total 4.037 hours, including clean replay and the first raw-scale calculation. These job times exclude preparation, model construction, evaluation and packaging. Total elapsed time remains measured from the original task start, including waiting and the earlier pilot; budgets were not reset. See inference_cost.csv and resource observations. The earlier run_01 precision failure and its documented repair remain preserved; run_02 completed full clean replay after that repair. No new run_02 inference failure remains unresolved.

DEVELOPMENT-EXPOSED and exploratory: selecting from observed outer scores does not create an untouched test set. The 2,000 recording-cluster bootstrap resamples (seed 314159) describe conditional uncertainty for this fitted model, these 26 recordings and the three fixed perturbation realizations. They omit selection and repeated-training uncertainty; secondary intervals are unadjusted. Equal named severity levels across modalities have different units. Only the selected F2 pipeline was tested under faults, so no relative robustness claim against discarded candidates is supported. This complete-action classification study does not establish online detection, causality, adaptive fusion or deployment robustness.

## Direct review paths

`model_selection/clean_comparison.csv` and `model_selection/clean_predictions/` reproduce selection. `comparison/prediction_table_index.csv` identifies all 51 actual prediction tables by path and SHA256. `comparison/robustness_metrics.csv` includes each realization and distinct pooled/fold metrics; `paired_differences.csv` includes interval replicate counts. `probability_shifts_and_signed_errors.csv`, `corruption_support.csv`, `modality_sensitivity.csv`, `branch_contrast_intervals.csv`, `reliability_bins.csv`, `absence_fallback.csv`, and `plots/` supply diagnostics. Raw signals/videos, feature caches and model blobs are excluded from the verified review ZIP and referenced by identity.

Recalculate all primary AP values and realization means from the repository root with `ma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/results/run_02/checks/recalculate_metrics.py`. This writes verification and diagnostic tables only; it does not run predictors.

Teaching chain: clean results -> eligibility and fixed common coverage -> locked selected pipeline -> one-modality raw-input faults -> branch and F2 predictions -> matched metrics -> bounded conclusion.

Recommended next decision: Require complete matched-fold and independent-recording validation before adopting or claiming a robust winner; do not infer deployment readiness from this one-fold pilot.

Evidence checked: source and upstream provenance, focused synthetic tests, actual clean/corrupted inference, frozen-state checks, and independently recalculated saved-table metrics. Still uncertain: untested candidates, broader recording coverage, model-selection/training variability and deployment faults. Defensible conclusion: the named synthetic faults characterize this fixed F2 pipeline on the stated pilot only.


Requested visual-study continuation: the existing supervisor was launched after both studies and their ZIPs completed. Worker 106854 stopped with `COMPLETE_OUTER_CYCLE_NOT_ADMITTED` (exit 75): estimated remaining outer-cycle cost 68,884.2 s (19.13 h), versus 53,835.7 s (14.95 h) before the original reporting reserve. The paused checkpoint is unchanged (453 updates, 3,621 rows seen); no new training updates ran. The visual study is **not running**. Its original training cutoff remains 2026-10-21 20:16:52 UTC and final deadline 23:16:52 UTC. No restart is scheduled. See `provenance/visual_resume_receipt.json` (relative to this run root). Continuing requires a separately approved budget/protocol amendment; neither completed study was changed.
