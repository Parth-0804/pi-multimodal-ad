# HANDOVER independent evaluation results

**Status: PARTIAL.** These are measured held-out results, not smoke-test metrics. Primary average precision is pooled over the independent outer tests (MSM) or the eligible official test split (Handover), calculated separately for every seed. Fixed threshold0.5 is used for classification metrics. AP is scikit-learn average precision, not trapezoidal PR area or the F-beta=2 score. F2 is the logistic-fusion model name.

## Complete three-seed comparison

| initialization | protocol | model | AP_mean | AP_seed_std | AP_min | AP_max |
| --- | --- | --- | --- | --- | --- | --- |
| P | official | averaging | 0.803102 | 0.013458 | 0.794653 | 0.818621 |
| P | official | prevalence | 0.728477 | 0.000000 | 0.728477 | 0.728477 |
| P | official | sensor_histgradient | 0.906319 | 0.000000 | 0.906319 | 0.906319 |
| P | official | sensor_logistic | 0.823624 | 0.000000 | 0.823624 | 0.823624 |
| P | official | visual | 0.771647 | 0.006411 | 0.767664 | 0.779042 |

Standard deviations describe three head-training seeds, not three independent datasets. Deterministic classical models may be identical across seeds. P is original pretrained CNN initialization; any R rows use only the exact completed canonical source. No best seed/fold was selected.

## Paired within-dataset AP differences

| initialization | comparison | mean | min | max |
| --- | --- | --- | --- | --- |
| P | averaging minus sensor_histgradient | -0.103218 | -0.111667 | -0.087699 |
| P | averaging minus sensor_logistic | -0.020522 | -0.028971 | -0.005003 |
| P | averaging minus visual | 0.031455 | 0.026418 | 0.039579 |

F2 is compared with its actual logistic-sensor component, vision, averaging and the stronger sensor control. An improvement over the logistic component alone does not establish superiority over the stronger numerical baseline. QG_aug has extra predefined corruption-training exposure; compare it with F2_aug as well as clean F2. Original F2 remains the clean-OOF model.

## Uncertainty and independence

Participant-level uncertainty is unavailable because the official release has no participant-to-trial mapping. No trial-based pseudo-independent CI is substituted. All three seed results and their descriptive range/std are reported. Official subject-based splitting is the publisher claim; it is not independently identity-verified.

## All per-seed held-out metrics

| initialization | seed | model | AP | AUROC | F1 | precision | recall | specificity | balanced_accuracy | Brier | log_loss | prevalence | TN | FP | FN | TP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P | 42 | averaging | 0.796032 | 0.580710 | 0.627660 | 0.756410 | 0.536364 | 0.536585 | 0.536475 | 0.244061 | 0.682487 | 0.728477 | 22 | 19 | 51 | 59 |
| P | 42 | prevalence | 0.728477 | 0.500000 | 0.842912 | 0.728477 | 1.000000 | 0.000000 | 0.500000 | 0.197807 | 0.584789 | 0.728477 | 0 | 41 | 0 | 110 |
| P | 42 | sensor_histgradient | 0.906319 | 0.746563 | 0.781395 | 0.800000 | 0.763636 | 0.487805 | 0.625721 | 0.212665 | 0.658547 | 0.728477 | 20 | 21 | 26 | 84 |
| P | 42 | sensor_logistic | 0.823624 | 0.582040 | 0.720000 | 0.704348 | 0.736364 | 0.170732 | 0.453548 | 0.237479 | 0.681045 | 0.728477 | 7 | 34 | 29 | 81 |
| P | 42 | visual | 0.767664 | 0.541463 | 0.421053 | 0.761905 | 0.290909 | 0.756098 | 0.523503 | 0.296968 | 0.796613 | 0.728477 | 31 | 10 | 78 | 32 |
| P | 123 | averaging | 0.794653 | 0.578049 | 0.778761 | 0.758621 | 0.800000 | 0.317073 | 0.558537 | 0.224535 | 0.640695 | 0.728477 | 13 | 28 | 22 | 88 |
| P | 123 | prevalence | 0.728477 | 0.500000 | 0.842912 | 0.728477 | 1.000000 | 0.000000 | 0.500000 | 0.197807 | 0.584789 | 0.728477 | 0 | 41 | 0 | 110 |
| P | 123 | sensor_histgradient | 0.906319 | 0.746563 | 0.781395 | 0.800000 | 0.763636 | 0.487805 | 0.625721 | 0.212665 | 0.658547 | 0.728477 | 20 | 21 | 26 | 84 |
| P | 123 | sensor_logistic | 0.823624 | 0.582040 | 0.720000 | 0.704348 | 0.736364 | 0.170732 | 0.453548 | 0.237479 | 0.681045 | 0.728477 | 7 | 34 | 29 | 81 |
| P | 123 | visual | 0.768235 | 0.540576 | 0.646154 | 0.741176 | 0.572727 | 0.463415 | 0.518071 | 0.254275 | 0.704011 | 0.728477 | 19 | 22 | 47 | 63 |
| P | 20261023 | averaging | 0.818621 | 0.581596 | 0.779661 | 0.730159 | 0.836364 | 0.170732 | 0.503548 | 0.222883 | 0.636964 | 0.728477 | 7 | 34 | 18 | 92 |
| P | 20261023 | prevalence | 0.728477 | 0.500000 | 0.842912 | 0.728477 | 1.000000 | 0.000000 | 0.500000 | 0.197807 | 0.584789 | 0.728477 | 0 | 41 | 0 | 110 |
| P | 20261023 | sensor_histgradient | 0.906319 | 0.746563 | 0.781395 | 0.800000 | 0.763636 | 0.487805 | 0.625721 | 0.212665 | 0.658547 | 0.728477 | 20 | 21 | 26 | 84 |
| P | 20261023 | sensor_logistic | 0.823624 | 0.582040 | 0.720000 | 0.704348 | 0.736364 | 0.170732 | 0.453548 | 0.237479 | 0.681045 | 0.728477 | 7 | 34 | 29 | 81 |
| P | 20261023 | visual | 0.779042 | 0.537694 | 0.673171 | 0.726316 | 0.627273 | 0.365854 | 0.496563 | 0.243171 | 0.679570 | 0.728477 | 15 | 26 | 41 | 69 |

Per-fold metrics and all sensitivity protocols are in `HANDOVER/experiments/common_support_v2/06_evaluation_results/metrics/`; every prediction carries its native sample ID, split role, fit/case ID, model, seed and corruption. `metric_reproduction.json` verifies that all saved fold metrics match prediction artifacts within1e-12.

## Overfitting diagnostic

| initialization | model | training_in_sample_AP | AP_mean | train_minus_heldout_AP |
| --- | --- | --- | --- | --- |
| P | sensor_histgradient | 1.000000 | 0.906319 | 0.093681 |
| P | sensor_logistic | 0.933785 | 0.823624 | 0.110161 |
| P | visual | 0.954964 | 0.771647 | 0.183317 |

These in-sample scores were computed after model fitting and never entered F2. A train/held-out gap is consistent with overfitting and/or operating-condition/domain shift; it does not isolate the cause. Ten fixed head epochs and40 fixed gate epochs were used, with no assessment-selected stopping. Every loss curve and completed checkpoint is preserved.

## Data-specific limits

F2, F2_aug, QG_clean and QG_aug are SKIPPED: participant-disjoint OOF probabilities cannot be certified without participant IDs. No in-sample probability stack or trial-group substitute was used. Robot and task differ in force estimation, camera view and class prevalence; see subgroup tables. The common-support amendment retains all151 official test trials; it is not a test-score-selected cohort.

Technical frame/sensor eligibility does not prove that an anomaly is optically visible. Mean pooling also does not model frame order. The tasks are retrospective interval/trial classification, not online failure prediction, damage localization or early warning. Dataset/task prevalence and observation horizon differ from REASSEMBLE, so absolute cross-dataset AP cannot establish general superiority.
