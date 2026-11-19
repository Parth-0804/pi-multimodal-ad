# Reuse inventory and precise remaining gaps

Inspection: 22 October 2026. No equivalent diagnostic process is running. No process is stopped or interrupted by this task.

Paths below are relative to `00_experiments/visual_backbone_one_day/`.

| Work | Initial status | Evidence reused | Exact remaining gap |
|---|---|---|---|
| Four-arm fit completion, matched cohort, G/C/assessment separation, saved replay checks | Already complete | `run_01_two_epoch_finetuning/checks/SELF_REVIEW_FINAL.md`; `fine_tuning_diagnostics_01/checks/analysis_checks.json`; `checks/final_self_check.json` in that diagnostic folder | Verify current relevant input hashes match the completed checks; do not rerun fits, leakage suite or replays |
| Pooled and per-fold AP, AUROC, Brier, log loss; learning curves | Already complete | `fine_tuning_diagnostics_01/tables/assessment_metrics.csv`, `learning_curve_summary.csv`, `all_learning_curves.csv` | Present pooled and mean/per-fold AP separately; no new metric-suite execution |
| Fine-tuned16/frozen16 and frame-count contrast intervals | Already complete | `run_01_two_epoch_finetuning/comparison/paired_comparisons.csv`, `bootstrap_policy.json` | Reuse original estimates and intervals |
| Fine-tuned32/frozen32 and practical fine-tuned32/frozen16 intervals | Missing | Original `bootstrap_draws.csv`, `bootstrap_recording_order.json`; per-replicate AP values are not retained | Compute only these missing contrasts for visual and F2, using the same multiplicities and pooled aggregation; mark exploratory |
| Complementarity at fixed ranking budgets, conditional sensor-score slices | Already complete | `fine_tuning_diagnostics_01/tables/fixed_budget_complementarity.csv`, `sensor_score_strata.csv` | No repetition |
| Visual-versus-sensor correct/wrong overlaps at 0.5 by truth class | Partial | Existing `threshold_error_transitions.csv` compares frozen-versus-fine-tuned errors, not the full requested cross-modality table | Add the four cross-modality outcomes separately for failures/successes |
| Label-aware continuous prediction changes | Partial | Existing paired segment CSVs include per-action visual/F2 Brier changes and ranks | Reuse those changes; add true-label log-loss changes and class/overlap summaries |
| Tied-score AP accounting, action/recording attribution, PR plots | Already complete | Prior `source/test_diagnostics.py`, `checks/synthetic_tests.log`, `tables/paired_segments_*`, `tables/action_AP_contributions.csv`; original `comparison/plots/pooled_precision_recall.png` | Do not recompute attribution or regenerate plots |
| Failure ranking improvements that fail to transfer to fusion | Partial | Existing paired segment CSVs retain within-fold rank changes; existing examples were selected by Brier | Summarise direction combinations and select a small explicitly keyed set by rank changes |
| Calibration, reliability, score spread, F2 arithmetic/logit-change decomposition | Already complete | Prior `tables/calibration_by_fit.csv`, `reliability_bins.csv`, `fusion_coefficients_and_score_spread.csv`, `exact_fusion_logit_change_decomposition.csv`, `checks/analysis_checks.json` | Verify saved feature order; summarise raw-logit/probability distributions and cross-fold comparability without new calibration fits or model substitutions |
| OOF versus assessment visual behaviour | Already complete | Prior `tables/OOF_to_assessment_pair_changes.csv` | Reuse; explicitly distinguish branch-held-out rows from fusion-training rows |
| Small self-contained review ZIP | Missing | Reusable report, selected tables, figures, source and test receipts | Add only missing analyses, a concise integrated report, source/input manifest and ZIP; preserve both existing packets |
| Causal mechanism, independent scientific review, new controlled experiment | Unresolved / outside execution scope | Existing evidence and limitations | Do not claim mechanism identification; do not launch a new experiment |

Original study sensor fits are used exclusively. No outputs from the separate encoder study are substituted.
