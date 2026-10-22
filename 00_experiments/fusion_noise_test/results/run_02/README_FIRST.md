# COMPLETE_ON_PILOT_COVERAGE

Selected `frozen_16_frames`: the canonical original-representation, frozen 16-frame F2 pipeline. Clean fused AP is 0.307928835369, equal to reference AP 0.307928835369; improvement over reference is +0. The eligible encoder candidate scored lower, so the predeclared rule retained F2.

Coverage: fold_01, 753 actions, 77 failures, 26 recordings. All 51 prescribed clean/fault/absence realizations completed. No retraining, recalibration or threshold tuning occurred.

| Condition | Visual AP | Sensor AP | Fused AP | AP drop | 95% interval for drop |
| --- | --- | --- | --- | --- | --- |
| Clean | 0.200401 | 0.290531 | 0.307929 | 0.000000 | — |
| Image Gaussian σ=0.10 | 0.123958 | 0.290531 | 0.284640 | 0.023289 | [-0.003184, 0.042857] |
| Sensor Gaussian α=1.00 | 0.200401 | 0.127743 | 0.169409 | 0.138520 | [0.070831, 0.221115] |

The canonical reference has only one complete eligible fold; the three fine-tuned/32-frame alternatives remain untested. Results are DEVELOPMENT-EXPOSED and exploratory. Five-fold encoder results are a separate comparison and cannot replace this pilot denominator.

- [Selection report](model_selection/selection_report.md) and [clean comparison](model_selection/clean_comparison.csv)
- [Results and all fault levels](comparison/RESULTS_SUMMARY.md)
- [All prediction paths and hashes](comparison/prediction_table_index.csv)
- [Metrics](comparison/robustness_metrics.csv), [paired intervals](comparison/paired_differences.csv), [review package](REVIEW_PACKAGE.zip)

Recommended next decision: Require complete matched-fold and independent-recording validation before adopting or claiming a robust winner; do not infer deployment readiness from this one-fold pilot.

Evidence checked: clean replay, frozen input-level inference and saved-table recalculation. Still uncertain: full coverage and external generalization. Defensible conclusion: completed robustness evidence for this fixed pipeline on pilot coverage.


Requested visual-study continuation: the existing supervisor was launched after both studies and their ZIPs completed. Worker 106854 stopped with `COMPLETE_OUTER_CYCLE_NOT_ADMITTED` (exit 75): estimated remaining outer-cycle cost 68,884.2 s (19.13 h), versus 53,835.7 s (14.95 h) before the original reporting reserve. The paused checkpoint is unchanged (453 updates, 3,621 rows seen); no new training updates ran. The visual study is **not running**. Its original training cutoff remains 2026-10-21 20:16:52 UTC and final deadline 23:16:52 UTC. No restart is scheduled. See `provenance/visual_resume_receipt.json` (relative to this run root). Continuing requires a separately approved budget/protocol amendment; neither completed study was changed.
