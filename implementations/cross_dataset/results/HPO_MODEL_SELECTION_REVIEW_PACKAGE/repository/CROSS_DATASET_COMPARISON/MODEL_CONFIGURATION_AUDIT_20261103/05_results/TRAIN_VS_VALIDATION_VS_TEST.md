# Metric scopes and definitions

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

`evaluation_scope` is mandatory in the long tables. TRAINING / TRAINING IN-SAMPLE diagnose fit; VALIDATION / VALIDATION OFFICIAL choose epochs/settings or describe official validation; INNER-OOF ASSESSMENT supports training-side meta fitting; HELD-OUT is the outer/official assessment; PAIRED DIFFERENCE and BOOTSTRAP INTERVAL are contrasts/interval endpoints, not standalone model predictions. Permutation controls and human-appearance development are separate. Do not pool these categories.

AP is non-interpolated average precision, sum of recall increments times precision at each score threshold; ties are grouped. Original `AUPRC` here is the saved average-precision implementation, not assumed trapezoidal PR area. AUROC is pairwise ranking with half credit for ties. Binary threshold metrics use source threshold (often0.5); native original training-OOF balanced-accuracy thresholds are retained separately. F1 versus macro_F1 are distinct. Vi macro_AP is mean of failure AP on p and success AP on1-p. Prevalence is required context:REASSEMBLE509/4530, selected100pilot77/753, MSM336/1895, Handover110/151, Vi3753/4382. A constant prior can have different pooled ranking if its fold-specific training prior varies; do not replace MSM pooled prior AP with overall prevalence.

Precision=TP/(TP+FP), recall=TP/(TP+FN), specificity=TN/(TN+FP), balanced accuracy=(recall+specificity)/2. Brier is mean squared probability error; log loss uses source-defined clipping. Original ECE uses15bins; external fixed recipe does not record ECE, so absent entries are NOT RECORDED. Zero divisions follow the original evaluation. Confusion matrices are flattened as TN/FP/FN/TP where available; original matrix/classification tables retain their source paths.

Mean-fold AP, pooled out-of-fold AP, seed-mean AP and AP of seed-mean predictions are different quantities. The audit does not merge them. Robustness tables preserve corruption name/severity and evaluation subset. Conditional confidence intervals resample recording/group/run where recorded; seed repeats on the same held-out samples do not increase independent N. Absent intervals are NOT AVAILABLE; no new interval is manufactured.

ALL_RECORDED_METRICS_LONG.csv includes every extracted numeric metric and recorded interval endpoint, plus epoch metrics. The raw metric key is preserved to avoid silently changing scientific definitions. `held_out_N` in historical aggregate rows may be NOT RECORDED where the source does not specify scope. Source `metric_path` is retained for nested aggregates; arrays of bootstrap draws are linked rather than copied. Summary CSVs omit epoch rows only; EPOCH_HISTORIES and long metrics retain them. Official Handover validation rows are explicitly labeled VALIDATION OFFICIAL.

## Evidence anchors

- [CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py](../../src/external_eval/evaluate.py) — metrics and execute_case roles.
- [VIFAILBACK/src/vifailback/metrics.py](../../../VIFAILBACK/src/vifailback/metrics.py) — both-class metrics.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — original AP/calibration/threshold.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ORIGINAL_NATIVE_THRESHOLD_METRICS.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ORIGINAL_NATIVE_THRESHOLD_METRICS.json) — native versus0.5 thresholds.
