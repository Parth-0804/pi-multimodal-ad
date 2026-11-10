# MSM model and configuration audit

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

The primary MSM cohort has **1,895 eligible intervals,336 abnormal examples**, with45 nominal groups. Original labels remain recorded, including a separate sensitivity that excludes native label2. The target is the declared abnormal-cut mapping; run/stage numbers are not damage labels. Physical tool/workpiece/session identities are incomplete, and only five date proxies are available.

The protocol uses three outer folds and two inner folds, seeds42,123,20261023. Retain/exclude-label2 crossed with nominal/machine-date/calendar-date grouping produces six protocols and54 completed cases. There are594 fitted model records, including base branches and fusion/gates. The table below is the **mean across three seeds of pooled three-outer-fold AP**, matching the earlier reported results. It is not an unweighted mean of nine fold-level AP values. Seeds reuse the same assessment samples.

Visual training is fixed at10 epochs, batch32, AdamW LR0.001/weight decay0.001, clip1, FP32, frozen CNN plus114,945-parameter head. Sixteen temporal-bin-center RGB frames are letterboxed to640 with sample-aspect-ratio correction. Fifteen actual MTConnect numerical channels produce90 features (six statistics each). Sensor LR is balanced C1, lbfgs, max_iter2000, random_state0. HGB uses learning_rate0.1, max_iter100, max_leaf_nodes15, min_samples_leaf10, l2_regularization1, early_stoppingFalse with balanced sample weights.

Average and F2 use the **LR sensor branch**, not HGB. F2 is unweighted C1 logistic on OOF probabilities. Quality gates use36 quality features plus two availability indicators, hidden16,40 epochs, LR0.003, weight decay0.001, batch128, clip1. Augmented variants use fixed lowest-severity corruption views. These are predefined external recipes, not optimizer HPO.

Saved pooled results reconcile the previously reported AP values: visual0.298901, LR0.828616, HGB0.901299, average0.735594, F20.756879, F2aug0.760170, quality-clean0.837418, quality-aug0.826521. In contrast, mean-fold AP is0.345443 visual,0.837925 LR,0.888524 HGB and0.787849 F2. AP_AGGREGATION_RECONCILIATION.csv preserves both conventions by model. They are different estimands, not conflicting predictions. The pooled prevalence baseline AP0.145395 differs from cohort prevalence0.177309 because each fold uses its own training prior. Conditional paired group intervals use2,000 draws; they do not establish physical-tool independence.

Every completed case's recorded output hashes and clean held-out metrics were checked. All exported prediction rows, including every corruption and role, were joined to native IDs/labels, with disjoint assessment/training IDs. Complete results retain all folds/seeds, sensitivity protocols, corruptions, subgroups and recorded intervals. Nominal grouping and date proxies limit stronger independence claims.

R transfer remains NOT EXECUTED. The canonical donor now exists at20 epochs, but `validated_source` requires at least25. Neither donor nor validator was changed.

| Model | Mean held-out AP | AUROC | F1 | Brier |
| --- | --- | --- | --- | --- |
| F2 | 0.756879 | 0.940705 | 0.820887 | 0.056703 |
| F2_aug | 0.760170 | 0.940401 | 0.818497 | 0.058183 |
| QG_aug | 0.826521 | 0.926371 | 0.746251 | 0.078043 |
| QG_clean | 0.837418 | 0.931925 | 0.770069 | 0.070717 |
| averaging | 0.735594 | 0.921692 | 0.709485 | 0.087269 |
| direction_only_DIAGNOSTIC | 0.241181 | 0.585006 | 0.356542 | 0.241350 |
| prevalence | 0.145395 | 0.320038 | 0.000000 | 0.160406 |
| sensor_histgradient | 0.901299 | 0.974077 | 0.837956 | 0.049034 |
| sensor_logistic | 0.828616 | 0.929702 | 0.811268 | 0.061724 |
| visual | 0.298901 | 0.705674 | 0.379833 | 0.205258 |

## Evidence anchors

- [MSM/04_experiment_protocol/experiment_config.json](../../../../MSM/04_experiment_protocol/experiment_config.json) — fixed P recipe, labels/groups/sensor channels.
- [MSM/03_processed_model_inputs/final_sample_manifest.csv](../../../../MSM/03_processed_model_inputs/final_sample_manifest.csv) — 1895 eligible sample IDs/native labels/clock mapping/source hashes.
- [MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json](../../../../MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json) — 54 completed protocol/fold/seed cases, output hashes.
- [CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py](../../../src/external_eval/evaluate.py) — execute_case: train, inner OOF, official validation, held-out scopes.
- [CROSS_DATASET_COMPARISON/src/external_eval/models.py](../../../src/external_eval/models.py) — fit_base/fit_fusions/fit_quality/predictions.
