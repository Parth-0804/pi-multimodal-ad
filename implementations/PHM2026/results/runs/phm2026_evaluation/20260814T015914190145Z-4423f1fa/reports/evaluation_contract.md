# Evaluation contract

Per-image-view metrics: MAE, RMSE, median absolute error and bias in percentage points of the provisional visible-flank candidate-area ratio; Spearman correlation; R² only with sufficient sample count/variance. Run-trajectory evaluation additionally uses MSE, Spearman/Kendall and monotonicity violations after versioned image→tooth→run aggregation.

All thresholds/scalers/baselines are fitted on EXP-B training only. EXP-A is validation and EXP-F is untouched test. Previous-run persistence is not run here because an image-derived previous target is unavailable in challenge sensor-only test inference. Results are provisional pseudo-target fidelity, not validated physical-spall accuracy.
