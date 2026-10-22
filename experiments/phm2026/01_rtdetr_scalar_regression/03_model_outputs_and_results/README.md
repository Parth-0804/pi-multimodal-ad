# 03 — Prediction, evaluation and result files

**Image prediction:** `predict_all` applies the training feature scaler, evaluates the scalar head, then restores percentage units with `scaled_prediction × target_scale + target_mean`. Join predictions to input samples using `sample_id`; manifest row order and prediction row order differ.

For EXP-F / Run 1 / Tooth 01, the saved prediction is **3.336106%**, versus the provisional target **2.555844%**: absolute error **0.780263 percentage points**. This is a saved lookup, not fresh inference.

**Aggregation is not modality fusion.** At tooth level, take the maximum over that tooth's available views, separately for targets and predictions. At run level, independently sort tooth targets and tooth predictions, then average each set's largest three. The predicted top three need not be the same teeth as the target top three. A separate monotonic result takes the causal cumulative maximum over runs within each experiment.

| EXP-F test evaluation | Count | MAE (percentage points) | RMSE | R² | Spearman |
|---|---:|---:|---:|---:|---:|
| Image view | 224 | 0.893852 | 1.563013 | -1.176080 | 0.360657 |
| Tooth | 224 | 0.893852 | 1.563013 | -1.176080 | 0.360657 |
| Run, raw top-three mean | 8 | 1.347448 | 1.757261 | -4.196063 | 0.571429 |
| Run, monotonic top-three mean | 8 | 1.920403 | 2.203457 | -5.422146 | 0.935414 |

The same numerical image/tooth results arise because EXP-F has one included image per tooth/run. Negative test R² means worse squared error than the test-set mean reference used by that metric; it does not contradict an MAE improvement over a separately fitted training-mean baseline. A high monotonic rank correlation does not establish small absolute error.

**Interpretation:** provisional engineering baseline, not validated physical-damage prediction. This review also found that extraction latency was an input to the trained head. These metrics therefore describe the stored 769-input model, not a verified image-feature-only 768-input model. The effect of removing latency has not been measured; see [the implementation finding](../KNOWN_IMPLEMENTATION_ISSUES.md). The unreviewed image heuristic and EXP-F acquisition-protocol shift limit scientific claims. Later reports and variants must be reviewed under their own run IDs.

| Open | Meaning |
|---|---|
| [Image predictions](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/predictions.csv) | 995 rows: includes train, validation and test; filter split=test for held-out evaluation |
| [Tooth predictions](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/tooth_predictions.csv) | View-maximum aggregates |
| [Run predictions](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/run_predictions.csv) | Raw and monotonic run aggregates |
| [Full metrics](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/metrics.csv) | 12 rows: four evaluation levels × three partitions |
| [Original assessment](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/reports/rtdetr_regression_report.md) | Historical interpretation and caveats |
| [Original output manifest](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/manifests/outputs.json) | Artifact identities and recorded provenance |

[End-to-end sample trace](../SAMPLE_WALKTHROUGH.md) · [Back to PHM start](../../README.md)
