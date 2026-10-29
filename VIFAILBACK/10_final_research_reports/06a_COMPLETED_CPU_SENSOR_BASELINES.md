# Completed CPU sensor baselines

These are sensor-only native-label results. Visual learning, CNN weight transfer, F2 and robustness remain pending. The frozen protocol has not changed after these results.

The common cohort contains4,382 episodes across99canonical tasks, all with both outcomes. Failure prevalence is3,753/4,382=0.856458; success prevalence is0.143542. One complete recorded episode is one prediction.

| Model | AP failure | AP success | Macro AP | AUROC |
|---|---:|---:|---:|---:|
| S3 | 0.954370 | 0.343577 | 0.648974 | 0.784370 |
| S2 | 0.970510 | 0.429530 | 0.700020 | 0.853756 |
| T_prevalence | 0.847889 | 0.131384 | 0.489637 | 0.455410 |

Each value pools three task-disjoint outer assessments per seed, then averages allthree seed results. Allthree prediction vectors are identical for these deterministic sensor methods on the fixed splits. Zero seed spread here is not CNN-seed stability or proof of broad robustness.

S3 is the source-exact balanced C1 logistic branch with T-only scaling and C-only sigmoid calibration; S1 is identical and was not separately duplicated. S2 is the prespecified balanced HGB200-iteration baseline, with leaves7/15/31 chosen on V and C-only calibration. T_prevalence uses only its corresponding training labels. Its pooled AP can differ from the global constant-score baseline because the three folds have different training priors.

S2 minus S3 macro AP is+0.051046; paired99-task bootstrap95%interval[0.015210,0.104288],2,000resamples shared across methods/seeds. This is conditional on the fitted models and canonical-task grouping, exploratory and not multiplicity-adjusted. Unknown sessions/operators and task similarities remain limitations.

All36prediction tables (9outer assessments and27inner assessments) were checked against native targets and exact split IDs. Allsaved metrics were recomputed; direct independent AP/AUROC/confusion/F1/precision/recall/Brier/logloss formulas agreed. T normalizers were recalculated and C sigmoid fits were reproduced from the cached verified statistics. The sensor base estimators were not independently retrained in this audit.

The prespecified F2 branch remains S3. The HGB result is an essential stronger comparator, and does not trigger a post-test architecture or hyperparameter change. A future fusion gain over S3 alone cannot establish superiority over S2.

Exact tables: `reproducibility/SENSOR_BASELINES_INDEPENDENT_CHECK.json`; allfold/seed results also appear in report06. Artifacts: `VIFAILBACK/06_training_experiments/sensor_baselines/runs/20261029T004900Z/seed{42,123,20261023}/{outerN_final,outerN_innerK}/`.
