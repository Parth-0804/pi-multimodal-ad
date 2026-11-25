# Additional improvements executed — final scope-adjusted handoff

ADDITIONAL IMPROVEMENTS PARTIALLY EXECUTED — BLOCKERS DOCUMENTED

**Documentation complete; Tasks 2–4 complete; Task 1 discontinued by the researcher on 2026-09-30. No execution remains queued.** This does not assert that all four original tasks finished. The disposition is a scope cancellation, not a technical blocker or a negative model result.

## Scope and preservation

Task1 must not be restarted. Some frozen-head comparisons, caches and partial fine-tuning checkpoints already exist; preserve them as archived partial evidence, exclude Task1 from the retained extension comparisons, and do not claim it never started. No completed fine-tuning conclusion is available. The later boundary-aware visual-pooling study is a separate completed protocol; it is not completion of Task1. Older paused/running status files are preserved historical snapshots, superseded administratively by SCOPE_DECISION.json and these final documents. No model was trained, labels changed or additional winner combination made during consolidation.

## Why these follow-ups were proposed

Task1 asked whether temporal order or limited spatial fine-tuning helps; its remaining work is now discontinued. Task2 tests whether the original six-epoch PatchTST cap explained its weakness. Task3 tests bounded context-dependent adjustments around successful F2 while retaining its probability-input logistic link. Task4 tests whether equal degradation exposure changes the comparison of static and adaptive fusion. The original core remains completed evidence; these are **ADDITIONAL EXPLORATORY EXPERIMENTS** motivated by already-observed outcomes on the same cohort.

## Fixed evaluation and implementation

All4530 segments,509 failures,148 recordings, original5 outer/4 inner recording-disjoint folds. Scaling, selection, calibration and thresholds use appropriate training partitions; strictly nested branch probabilities supply fusion. Tasks2/3 neural seeds20260927–29;2000 paired recording-cluster resamples condition on fitted models. Task4 additionally resamples stochastic realization indices and averages metrics across realizations. Intervals for Tasks2–4 are marginal across reported comparisons, not a blanket multiplicity-adjusted discovery claim.

Task2 preserves PatchTST channels512×22, patch32/stride16, width32,2 layers/4 heads/FF64 and masking behavior. S-6 retains3/6-epoch selection; S-LONG allows100 epochs, min10/patience12; training uses BCE positive weighting, AdamW lr.001/decay.001, batch128, clipping1. Zero long-budget inner fits reached100. Outer refit budgets use rounded median inner best epochs per seed; calibration is sigmoid logistic. S-HYBRID is one C1 stacker on strictly nested S-LONG/statistics probabilities, two representations of the same sensor modality.

Task3 freezes each proper-training-partition F2 anchor; sigmoid(b+sum(a*(1+tanh(h(u)))*p)). A-CONSTANT has two global adjustments; A-ADAPTIVE uses action4+quality36+availability2 through42→16→2 with zero final initialization. Lambdas.01/.1/1, AdamW.003, decay.001, max100/min10/patience12. Selection uses mean inner AP of three-seed probabilities. A0 shares original probability scores within documented tolerance, but its threshold protocol differs from historical F2; therefore hard-decision metrics must not be treated as identical. Coefficients are not normalized probability weights or causal mechanisms.

Task4 retains original frozen branches. Four training realizations per family; mixture50% clean,25% pixel Gaussian sigma.01–.08,25% sensor Gaussian alpha.05–.8 training-channel SD. Recompute quality without supplying fault identity/severity. Static C1 expansion weights parents equally; neural models sample one view per parent/epoch. All models use matched validation objective. Test stochastic faults use five separate realizations; deterministic faults one. Gaussian highest severities exceed training ranges; other families are held out from augmentation but were observed in the earlier core study. No new branches from Task2 or boundary pooling enter this comparison.

## Prespecified primary contrasts

Task1’s original principal contrast is explicitly excluded by the revised scope, not replaced with the later visual study.

| Task | Frozen principal contrast | ΔAP [95%] | ΔAUROC [95%] | Interpretation |
| --- | --- | --- | --- | --- |
| 2 | S-LONG minus S-6 | +0.0297 [+0.0122, +0.0451] | +0.0142 [+0.0033, +0.0247] | supported improvement |
| 3 | A-ADAPTIVE minus A0 | +0.0210 [+0.0015, +0.0419] | +0.0044 [-0.0031, +0.0115] | supported improvement |
| 4 | augmented A-ADAPTIVE minus augmented F2, mean six seen-family conditions | +0.0097 [-0.0034, +0.0228] | +0.0105 [-0.0027, +0.0248] | inconclusive difference |

## Secondary contrasts

| Task | Secondary contrast | ΔAP [95%] | ΔAUROC [95%] | Interpretation |
| --- | --- | --- | --- | --- |
| 2 | S-LONG minus S-STATS | -0.1441 [-0.1861, -0.1009] | -0.0496 [-0.0760, -0.0237] | supported deterioration |
| 2 | S-6 minus S-HIST | +0.0141 [-0.0045, +0.0338] | +0.0102 [-0.0031, +0.0233] | inconclusive difference |
| 2 | S-HYBRID minus S-STATS | +0.0110 [+0.0054, +0.0181] | +0.0155 [+0.0090, +0.0226] | supported improvement |
| 3 | A-ADAPTIVE minus A-CONSTANT | +0.0226 [+0.0036, +0.0432] | +0.0043 [-0.0031, +0.0115] | supported improvement |
| 3 | A-CONSTANT minus A0 | -0.0016 [-0.0035, +0.0003] | +0.0001 [-0.0005, +0.0006] | inconclusive difference |

## Clean metrics and trade-offs

| Task | Model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | S-6 | 0.7155 | 0.2557 | 0.6410 | 0.5360 | 0.6090 | 0.1908 | 0.0929 | 0.0114 |
| 2 | S-LONG | 0.7298 | 0.2853 | 0.6609 | 0.5688 | 0.5914 | 0.2173 | 0.0919 | 0.0156 |
| 2 | S-HIST | 0.7054 | 0.2416 | 0.6352 | 0.5463 | 0.5639 | 0.1956 | 0.0937 | 0.0067 |
| 2 | S-STATS | 0.7793 | 0.4294 | 0.7056 | 0.6223 | 0.6149 | 0.2765 | 0.0804 | 0.0174 |
| 2 | S-HYBRID | 0.7948 | 0.4403 | 0.7095 | 0.6314 | 0.6090 | 0.2886 | 0.0791 | 0.0155 |
| 3 | A0 | 0.7950 | 0.4473 | 0.7129 | 0.6379 | 0.6071 | 0.2977 | 0.0784 | 0.0138 |
| 3 | A-CONSTANT | 0.7950 | 0.4457 | 0.7111 | 0.6351 | 0.6071 | 0.2937 | 0.0785 | 0.0129 |
| 3 | A-ADAPTIVE | 0.7993 | 0.4683 | 0.7116 | 0.6464 | 0.5874 | 0.3118 | 0.0770 | 0.0180 |
| 4 | clean_F2 | 0.7950 | 0.4473 | 0.7129 | 0.6379 | 0.6071 | 0.2977 | 0.0784 | 0.0138 |
| 4 | augmented_F2 | 0.7805 | 0.4341 | 0.7011 | 0.6635 | 0.5246 | 0.3518 | 0.0856 | 0.0380 |
| 4 | clean_F6 | 0.7873 | 0.4449 | 0.7035 | 0.6248 | 0.6031 | 0.2801 | 0.0811 | 0.0197 |
| 4 | augmented_F6 | 0.7867 | 0.4335 | 0.7118 | 0.6321 | 0.6149 | 0.2893 | 0.0810 | 0.0155 |
| 4 | clean_A-ADAPTIVE | 0.7997 | 0.4682 | 0.7102 | 0.6398 | 0.5953 | 0.3012 | 0.0771 | 0.0199 |
| 4 | augmented_A-ADAPTIVE | 0.7940 | 0.4509 | 0.7029 | 0.6422 | 0.5678 | 0.3074 | 0.0789 | 0.0185 |
| 4 | HIST_F2 | 0.7950 | 0.4473 | 0.7117 | 0.6340 | 0.6110 | 0.2920 | 0.0784 | 0.0138 |
| 4 | HIST_F6 | 0.7755 | 0.4414 | 0.7019 | 0.6384 | 0.5717 | 0.3012 | 0.0807 | 0.0124 |
| 4 | TASK3_A | 0.7993 | 0.4683 | 0.7116 | 0.6464 | 0.5874 | 0.3118 | 0.0770 | 0.0180 |
| 4 | U_VISUAL | 0.6978 | 0.2307 | 0.6414 | 0.5153 | 0.6621 | 0.1810 | 0.0943 | 0.0070 |
| 4 | U_SENSOR | 0.7793 | 0.4294 | 0.7056 | 0.6223 | 0.6149 | 0.2765 | 0.0804 | 0.0174 |

Longer training improves PatchTST over matched short training but it remains below engineered statistics. The same-sensor hybrid adds a small supported AP gain. Clean anchored adaptation improves AP while AUROC gain remains unresolved; its failure recall is lower and ECE higher than matched A0. These trade-offs rule out a universal improvement claim.

## Fold and seed consistency

| Contrast | Positive AP folds | Fold AP differences |
| --- | --- | --- |
| S-LONG minus S-6 | 5/5 | +0.0867, +0.0442, +0.0098, +0.0094, +0.0020 |
| S-LONG minus S-STATS | 0/5 | -0.0361, -0.1622, -0.2221, -0.1683, -0.1028 |
| S-6 minus S-HIST | 3/5 | -0.0158, -0.0149, +0.0101, +0.0126, +0.0882 |
| S-HYBRID minus S-STATS | 5/5 | +0.0022, +0.0052, +0.0019, +0.0160, +0.0211 |
| A-ADAPTIVE minus A0 | 4/5 | +0.0020, +0.0275, +0.0570, -0.0192, +0.0211 |
| A-ADAPTIVE minus A-CONSTANT | 4/5 | +0.0046, +0.0276, +0.0569, -0.0192, +0.0214 |
| A-CONSTANT minus A0 | 1/5 | -0.0026, -0.0001, +0.0001, -0.0001, -0.0003 |

| Model | Seed AUPRCs |
| --- | --- |
| S-6 | 20260927: 0.2355, 20260928: 0.2499, 20260929: 0.2368 |
| S-LONG | 20260927: 0.2518, 20260928: 0.2780, 20260929: 0.2641 |
| A0 | 20260927: 0.4473, 20260928: 0.4473, 20260929: 0.4473 |
| A-CONSTANT | 20260927: 0.4456, 20260928: 0.4458, 20260929: 0.4458 |
| A-ADAPTIVE | 20260927: 0.4667, 20260928: 0.4695, 20260929: 0.4668 |

Full eight-metric fold/seed values are in per_fold_metrics.csv/per_seed_metrics.csv; Task4’s per-fold/per-seed rows and every condition are copied separately. Seeds are not independent recording groups.

## Task4 robustness and clean-performance qualifications

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

| Augmented model | Compared with | Δ clean AP [95%] | Noninferiority at margin .01 |
| --- | --- | --- | --- |
| augmented_F2 | versus_clean_F2 | -0.0132 [-0.0247, -0.0020] | False |
| augmented_F2 | versus_own_clean_model | -0.0132 [-0.0247, -0.0020] | False |
| augmented_F6 | versus_clean_F2 | -0.0138 [-0.0240, -0.0042] | False |
| augmented_F6 | versus_own_clean_model | -0.0114 [-0.0239, -0.0016] | False |
| augmented_A-ADAPTIVE | versus_clean_F2 | +0.0036 [-0.0111, +0.0180] | False |
| augmented_A-ADAPTIVE | versus_own_clean_model | -0.0173 [-0.0306, -0.0047] | False |

The principal six-condition adaptive-versus-equally-augmented-static contrast is inconclusive. Isolated favorable conditions do not establish general robustness. Marked losses occur under channel and temporal-block dropout and strong blur. Complete-modality-loss equality follows structural fallback, not learned recovery. The clean-performance noninferiority claims above require the specific lower bound >−.01; crossing zero alone is insufficient.

## Compute, curves and source identities

| Task | Timed fit rows | Summed fit seconds |
| --- | --- | --- |
| 2 | 120 | 2460.005013569942 |
| 4 | 540 | 433.102954083035 |
| 3 | 391 | 193.46226181006932 |

These sums measure retained fit compute, not full wall time, acquisition, cache extraction, interrupted attempts or all preprocessing. Source CSV columns and exact source identities are in compute_summary.json. Learning curves, validation AP/AUROC histories, selected epochs, checkpoints, scaler/calibrator parameters and prediction hashes are linked in each full task report copied beside this handoff. Detailed locations:

- Task2: `runs/reassemble/additional_improvements_executed/20260928T000346Z/02_patchtst_training_budget`; its `fits/`, result tables, comparison JSON and per-fit identity metadata remain the authoritative numerical evidence.
- Task3: `runs/reassemble/additional_improvements_executed/20260928T000346Z/03_static_anchored_adaptation`; its `fits/`, result tables, comparison JSON and per-fit identity metadata remain the authoritative numerical evidence.
- Task4: `runs/reassemble/additional_improvements_executed/20260928T000346Z/04_corruption_training`; its `fits/`, result tables, comparison JSON and per-fit identity metadata remain the authoritative numerical evidence.
- Task2 final curves/checkpoint-retention validation: `runs/reassemble/additional_improvements_executed/20260928T000346Z/recovery/sensor_task2/20260928T140922Z/report`.
- Config: `configs/reassemble/additional_improvements/execution.json`; source: `src/reassemble/additional_improvements/`; exact current identities and dirty state: provenance.json.
- Protocol commit26ae3a7; initial Task3 commit484bd35; queue/cache commite665029; current consolidation HEAD `8d4e7a9378cb51ffc3cd7b9be1e2785efc02d792`. Uncommitted implementation is identified by SHA256, not attributed wholly to HEAD.

## Attempts, corrections and deviations

- Task3’s first attempt stopped on a decimal-penalty filename/signature collision; corrected filenames and initial artifacts are preserved.
- S-6 selected-epoch checkpoint retention required deterministic replay of already-selected budgets with logit parity; no new selection or changed predictions.
- Task4 first recovery stopped on list-versus-tuple JSON metadata equality; exact canonical equality was established, model identity unchanged, and resumed work used immutable bank reuse.
- Daily reset recovery used completed units and fresh attempt directories; no uninterrupted execution claim.
- Task1 had approved frozen-prefix caching and partial recovery before cancellation; failed/partial attempts remain archived and support no finished fine-tuning claim.
- No report silently reconciled a numerical discrepancy. Exact failure/correction paths are listed in failed_attempts_and_corrections.json.

- `runs/reassemble/additional_improvements_executed/20260928T000346Z/03_static_anchored_adaptation/correction_001.md`
- `runs/reassemble/additional_improvements_executed/20260928T000346Z/01_temporal_visual/prefix_cache_correction_001.md`
- `runs/reassemble/additional_improvements_executed/20260928T000346Z/02_patchtst_training_budget/checkpoint_retention_correction.md`
- `runs/reassemble/additional_improvements_executed/20260928T000346Z/recovery/task4/20260928T174834Z/CORRECTION.md`

## Separate completed visual follow-up

The boundary-aware experiment is reported separately and not used to rescue the discontinued Task1. Historical V0 reproduced exactly. Best pooled-AP variantV3 (last quarter) AP0.319146 versus0.230658, ΔAP +0.0885 [+0.0424, +0.1293]; ΔAUROC +0.0750 [+0.0518, +0.0972]. Its own protocol considered five AP comparisons and classified the studyA. The single authorized static-fusion follow-up achieved AP0.493437 versus originalF2 0.447299, paired ΔAP +0.0461 [+0.0260, +0.0632]. It did not combine the new sensor hybrid or anchored gate. This is exploratory same-cohort selection, not independent confirmation. Full report: `artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md`.

## Thesis-safe sentences

- “In the additional exploratory REASSEMBLE experiments, S-LONG minus S-6 changed AUPRC by +0.0297 [+0.0122, +0.0451] (paired marginal95% recording-cluster interval), classified as supported improvement.”
- “In the additional exploratory REASSEMBLE experiments, S-HYBRID minus S-STATS changed AUPRC by +0.0110 [+0.0054, +0.0181] (paired marginal95% recording-cluster interval), classified as supported improvement.”
- “In the additional exploratory REASSEMBLE experiments, A-ADAPTIVE minus A0 changed AUPRC by +0.0210 [+0.0015, +0.0419] (paired marginal95% recording-cluster interval), classified as supported improvement.”
- “In the additional exploratory REASSEMBLE experiments, augmented A-ADAPTIVE minus augmented F2, mean six seen-family conditions changed AUPRC by +0.0097 [-0.0034, +0.0228] (paired marginal95% recording-cluster interval), classified as inconclusive difference.”

The longer-budget result qualifies the scope of the original short-budget PatchTST negative finding; it does not reverse statistics’ superiority to standalone PatchTST. Anchored adaptation extends the model family tested after the core: it does not retrospectively make original F6 successful. Task4 provides no general adaptive-robustness claim. Original studies, handoffs and numerical evidence remain unchanged.

## Claims not supported and remaining work

No statement that all four original tasks completed; no completed Task1 fine-tuning result; no universal temporal-Transformer superiority, general deployment robustness, causal coefficient interpretation, independent confirmation, unseen-object/site validity, audio inference, label correction or benefit from combining intervention winners. Non-significance is not equivalence. Human review has one actual submission and pending adjudication; that separate process is not settled by these experiments. External master Reasoning Record and THESIS_WRITING_MAP_v3 remain unlocated; neither was fabricated.

## Validation and closure

Saved prediction point estimates, per-fold/seed results and paired point differences were recomputed; Task4 averages were recomputed per realization before averaging. Boundary follow-up points were checked separately. Historical small-file hashes and large-file size/mtime preservation were checked with the original preserved snapshot; this is not a fresh full raw-HDF5 rehash. Confidence intervals are retained from the saved deterministic procedures, not rerun here. See validation.json and output_manifest.json for exact checks, scope, inputs and outputs. Tasks2–4 are complete; Task1 is administratively closed, not queued. Stop after documentation; do not run the legacy full supervisor.
