# T2.3 checkpoint — evaluation and naive baselines

Status: **COMPLETE FOR PROVISIONAL IMAGE BASELINE**  
Run: `20260814T015914190145Z-4423f1fa`

The tested common schema and metrics cover MSE, MAE, RMSE, median absolute error, bias, R² when meaningful, Spearman/Kendall and deterministic MAE bootstrap intervals. All errors use provisional percentage points of visible-flank candidate area.

Training mean/median fit EXP-B only. On untouched EXP-F image views:

- training mean: MAE 1.020, RMSE 1.366, 95% bootstrap MAE CI 0.911–1.139;
- training median: MAE 1.203, RMSE 1.560.

Previous-run persistence was not executed because earlier image-derived targets are unavailable in the challenge's sensor-only test inference. No validation/test statistic defines scaling or a baseline. Physical calibration, maintenance thresholds and false-alarm costs remain unresolved.

Primary artifacts: `runs/phm2026_evaluation/20260814T015914190145Z-4423f1fa/{tables,reports}`.
