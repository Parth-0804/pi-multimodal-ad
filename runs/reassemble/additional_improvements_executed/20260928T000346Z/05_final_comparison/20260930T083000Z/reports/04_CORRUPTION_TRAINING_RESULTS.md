# Task 4 — exposure-matched corruption training

ADDITIONAL EXPLORATORY EXPERIMENTS. [VERIFIED EXECUTION]

Question: does exposure to partial degradation improve robustness, and does adaptation beat static fusion with the same exposure? Branch architectures, original fit procedures, cohort and folds are unchanged.

Exact protocol: four training realizations per segment/family; mixture .5 clean/.25 native-pixel Gaussian (.01–.08)/.25 raw-sensor Gaussian (.05–.8 times training-channel SD). Quality is recomputed; no injected fault identifiers enter the model. Each parent contributes total weight1. Neural fits sample one view per parent epoch; static C1 fits the exact weighted expansion. All branch fit/selection/calibration/noise scale and quality normalization exclude the assessment recording. Validation uses distinct realizations and shared .5 cleanAP+.25 visualAP+.25 sensorAP objective. F6 is the original masked-logit family with hidden16; A-ADAPTIVE retains the frozen clean F2 anchor and Task3 bounded adjustments. Matched clean fits use identical architecture/budget/selection objective.

[OBSERVED RESULT] Primary six-condition mean: augmented A-ADAPTIVE minus augmented F2 ΔAP +0.0097, marginal paired 95% [-0.0034, +0.0228]: **inconclusive difference**.

Every Gaussian/frame-drop/channel-drop/block-drop condition has five fixed new realizations; blur, stuck F/T and complete loss are deterministic. Test observations are shared across models. Metrics, not predictions, are averaged. Paired intervals resample recordings and realization indices. Highest Gaussian severities extrapolate beyond augmentation; lower levels are in-range. Other families are held out of augmentation, but were already examined in the original study.

All absolute metrics, clean changes, paired contrasts against both static controls and remaining unimodal references: `results.json`, `absolute_metrics.csv`, `paired_comparisons.csv`. Fold/seed results: `per_fold_metrics.csv`, `per_seed_metrics.csv`. Weight/coefficient response: `weight_coefficient_response.csv`; coefficients are not normalized probability weights or causal explanations. Single-loss predictions are explicitly replaced by the surviving branch probability and its original threshold.

| Condition | clean F2 AP | augmented F2 AP | augmented adaptive AP | adaptive−augmented static ΔAP,95% |
| --- | --- | --- | --- | --- |
| clean | 0.4473 | 0.4341 | 0.4509 | +0.0168 [+0.0010,+0.0305] |
| test_V1_0.02 | 0.4123 | 0.4282 | 0.4285 | +0.0003 [-0.0223,+0.0231] |
| test_V1_0.05 | 0.4076 | 0.4252 | 0.4343 | +0.0091 [-0.0122,+0.0293] |
| test_V1_0.1 | 0.3960 | 0.4267 | 0.4159 | -0.0108 [-0.0313,+0.0100] |
| test_V2_1 | 0.4478 | 0.4324 | 0.4455 | +0.0131 [-0.0025,+0.0265] |
| test_V2_2 | 0.4391 | 0.4304 | 0.4330 | +0.0026 [-0.0122,+0.0151] |
| test_V2_4 | 0.4099 | 0.4256 | 0.3968 | -0.0288 [-0.0464,-0.0121] |
| test_V3_2 | 0.4469 | 0.4338 | 0.4507 | +0.0169 [+0.0011,+0.0305] |
| test_V3_5 | 0.4462 | 0.4339 | 0.4500 | +0.0161 [+0.0006,+0.0297] |
| test_V3_8 | 0.4471 | 0.4342 | 0.4505 | +0.0163 [+0.0004,+0.0309] |
| test_S1_0.1 | 0.4191 | 0.4084 | 0.4121 | +0.0037 [-0.0109,+0.0174] |
| test_S1_0.5 | 0.2882 | 0.2787 | 0.3011 | +0.0224 [+0.0019,+0.0425] |
| test_S1_1 | 0.2246 | 0.1749 | 0.2081 | +0.0333 [+0.0184,+0.0471] |
| test_S2_2 | 0.4128 | 0.3978 | 0.3457 | -0.0521 [-0.0785,-0.0250] |
| test_S2_7 | 0.3533 | 0.3318 | 0.2613 | -0.0705 [-0.0995,-0.0418] |
| test_S2_11 | 0.3157 | 0.2924 | 0.2128 | -0.0796 [-0.1090,-0.0526] |
| test_S3_0.1 | 0.4474 | 0.4335 | 0.3739 | -0.0596 [-0.0972,-0.0223] |
| test_S3_0.3 | 0.3998 | 0.3805 | 0.3082 | -0.0724 [-0.1165,-0.0296] |
| test_S3_0.5 | 0.3442 | 0.3204 | 0.2356 | -0.0848 [-0.1241,-0.0464] |
| test_S4_median | 0.4396 | 0.4374 | 0.4366 | -0.0008 [-0.0115,+0.0111] |
| test_missing_visual | 0.4294 | 0.4294 | 0.4294 | +0.0000 [+0.0000,+0.0000] |
| test_missing_sensor | 0.2307 | 0.2307 | 0.2307 | +0.0000 [+0.0000,+0.0000] |

Clean non-inferiority uses a prospectively fixed .01 AP margin. A confidence interval crossing zero does not establish equivalence or non-inferiority; see the explicit lower-bound decisions in `results.json`. Adaptation claims require both appropriate coefficient response and advantage over equally exposed static fusion. Isolated favorable cells do not establish a general robustness claim.

Learning curves and compute: matched_learning_curves.csv/.png/.pdf and matched_fit_compute.csv, covering 540 neural fits and 433.1 summed fit-seconds. Static logistic fits have no epoch curve; their solver configuration and runtimes are in fits/*.json. Per-realization and per-seed/fold results are retained separately.

Limitations: same outcome-informed cohort; marginal intervals across many reported cells; fixed fitted models; finite seed/realization bank; artificial faults are not a representative industrial deployment distribution. Historical models remain additional sealed references, without rewriting historical conclusions. No changes from Tasks1/2 are inserted into this task.
