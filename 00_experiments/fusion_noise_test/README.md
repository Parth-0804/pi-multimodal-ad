# Selected-model raw-input robustness study — COMPLETE_ON_PILOT_COVERAGE

[Start with the completed run_02 report](results/run_02/README_FIRST.md). The original frozen 16-frame F2 was retained by the fixed clean selection rule. All 51 prescribed realizations completed on the locked fold_01 pilot: 753 actions, 77 failures, 26 recordings.

- [Selection report](results/run_02/model_selection/selection_report.md) and [clean comparison](results/run_02/model_selection/clean_comparison.csv)
- [Results and limitations](results/run_02/comparison/RESULTS_SUMMARY.md)
- [Direct prediction tables and hashes](results/run_02/comparison/prediction_table_index.csv)
- [Review package](results/run_02/REVIEW_PACKAGE.zip)

The earlier [run_01 pilot](results/run_01/README_FIRST.md), its lock, partial replay evidence and reports remain preserved. The user authorized run_02's new selection after encoder completion, before any corruption. Original deadlines and cumulative resource/repair budgets were retained.

Metric-only recalculation, from the repository root:

```bash
ma_thesis_env/bin/python -B 00_experiments/fusion_noise_test/results/run_02/checks/recalculate_metrics.py
```

The study-specific entry point remains `run_after_encoder.py` with implemented `prepare`, `test`, and `resume --wait-seconds 0` commands. No further inference is required or scheduled. No retraining, recalibration, threshold tuning, detector/decoder execution, or historical Task4 work occurred. The separately paused visual task is handled under the explicit user resume instruction, with a provenance receipt once restarted.

The requested visual restart was attempted and blocked by its existing time-admission policy; it is not running. [Exact receipt](results/run_02/provenance/visual_resume_receipt.json).
