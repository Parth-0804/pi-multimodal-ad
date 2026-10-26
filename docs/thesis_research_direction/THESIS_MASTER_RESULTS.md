# Thesis master results

TASK 4 · 2026-10-26 · baseline `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.

These are six **separate evidence families**, not a combined leaderboard. The [inventory](THESIS_EXPERIMENT_INVENTORY.md) defines each task, implementation ID and protocol. The [ledger](THESIS_CONTRIBUTION_LEDGER.md) controls interpretation; [gaps/validation](THESIS_EVIDENCE_GAPS.md) describe what was checked. All historical reports remain unchanged.

**V** = TASK 4 saved-artifact arithmetic or bounded metadata check. **R** = historical reported result/interval/cost; **I** = interpretation/algebra; **P** = proposed decision. Every confidence interval in this document is **R**, unless explicitly stated otherwise. No bootstrap or neural replay was run in TASK 4. A V point estimate with an R interval is not newly reproduced uncertainty. AP is sklearn average precision, not trapezoidal PR-AUC; ↑ is better for AP/AUROC, ↓ for MAE/Brier/ECE. Brier is overall probability quality, not calibration alone. ECE depends on binning and is not a proper score.

Intervals are conditional on fitted predictions, declared groups and sometimes fixed corruption realizations. They omit full refitting and adaptive development-selection uncertainty. Recording separation is not automatically session/operator/object independence; PHM run intervals do not capture new-experiment uncertainty over only three domains. All retained datasets have a history of assessment exposure.

## A. PHM feasibility and prediction

### A1. Retained v3 LOEO run regression — P04/P06

Twenty runs; provisional top-three candidate-area target, teeth5–28; larger remaining experiment trains, third validates. No visual branch in `fused_all_three`. **V** means recalculated from [loeo_predictions.csv](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv), with truth matched to the retained v3 target table. Intervals and Spearman below are **R** from [loeo_summary.json](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json), 10,000 run resamples.

| Model | Runs | MAE pp (V) | 95% interval (R) | Spearman (R) |
| --- | --- | --- | --- | --- |
| constant_train_mean | 20 | 0.804156 | [0.576867, 1.036024] | -0.035400 |
| fused_all_three | 20 | 0.823786 | [0.552712, 1.101495] | -0.104551 |
| patchtst_single_encoder | 20 | 0.941455 | [0.675433, 1.226433] | -0.205340 |

| Contrast vs constant | Empirical ΔMAE (V) | Stored bootstrap-mean ΔMAE (R) | 95% interval (R) |
| --- | --- | --- | --- |
| fused_all_three | +0.019629 | +0.017668 | [-0.196189, 0.227769] |
| patchtst_single_encoder | +0.137299 | +0.135838 | [-0.085423, 0.355913] |

Neither tested sensor model demonstrated improvement over the constant. This is not equivalence or absence of sensor information. The constant reference uses the training **mean** although MAE's optimal constant is the median; do not claim comparison against every possible trivial predictor. The global/experiment-specific target and sequence lengths may confound inference. [Historical report](../thesis/FUSION_RESULTS_20260912T111025Z.md).

The separately marked R4 image reference covers only A/F, 13 runs: **V MAE1.826411**, **R** [1.458355,2.220912], Spearman .659341. It reaggregates a model trained on B against v3 truth; it is **NOT LOEO** and cannot rank against the three A1 rows. Its presence does not establish a visual–sensor fusion result.

### A2. Separate v3 four-arm sensor-subgroup experiment — P07–P10

Same three-domain outer rule, three seeds. Values and intervals **R** from [SQ2_SQ3_RESULTS.json](../thesis/SQ2_SQ3_RESULTS.json); parsed for transcription, not recomputed from per-run predictions. Separate group heads/parameter sharing differ from A1. Do not substitute A3 for `fused_all_three`.

| Arm | Mean MAE pp (R) | Seed SD (R) | Run interval (R) |
| --- | --- | --- | --- |
| A1_M1_accel1 | 0.881117 | 0.035417 | [0.636315, 1.137617] |
| A1_M2_accel2 | 0.828852 | 0.027841 | [0.593297, 1.072347] |
| A1_M4_context | 0.883207 | 0.005384 | [0.636138, 1.147753] |
| A1_M5_condition_indicators | 0.939857 | 0.026474 | [0.695340, 1.200209] |
| A2_concatenation | 0.964288 | 0.077900 | [0.673835, 1.266517] |
| A3_modular_late | 0.828813 | 0.010577 | [0.589671, 1.080089] |
| A4_gated | 0.907363 | 0.074528 | [0.674908, 1.162846] |

Constant MAE .8042 is lower in point estimate than all arms. Of 28 marginal pairwise intervals, the report identifies three excluding zero: M5−constant +.1355 [.0703,.2044]; A3−A4 −.0781 [−.1619,−.0046]; M2−A4 −.0784 [−.1557,−.0039]. No multiplicity-adjusted discovery claim; overlapping individual intervals do not replace paired contrasts.

Sensor zero/noise ablations (R) show A3 baseline .8288, dropM1 .8365, 10dB .8283, 0dB .8267, dropM4 .8273; A4 .9074/.9160/.9072/.9062/.9074 respectively. M3 has no columns, so its drop is exactly vacuous. Reported flatness/seed SD is not an equivalence or useful robustness test. [Full report](../thesis/SQ2_SQ3_RESULTS_20260913T053509Z.md).

### A3. Historical v2 RT-DETR detection — P02

All **R** from [detection checkpoint](../planning/R4_RTDETR_DETECTION_CHECKPOINT.md). B448/A323/F224 views; 9,883 F pseudo-boxes; not physical ground truth. AP here is detection AP at IoU, not action-classification AP.

| Metric/operating point | Full detector (R) |
| --- | --- |
| mAP@.50 / mAP@.50:.95 | .000083 / .000016 |
| A-selected confidence | .60 |
| TP / FP / FN at confidence | 0 / 0 / 9,883 |
| Precision / recall / F1 | 0 / 0 / 0 |
| Configured trainable / frozen parameters | 25,156,067 / 6,829,728 |
| Training / peak CUDA allocation | 234.19 s T4 / 2,448,414,208 bytes |

This is a poor result on pseudo-box agreement under a short schedule and protocol shift; the actual Transformer decoder executes. It cannot be confused with REASSEMBLE's retained CNN feature branch.

### A4. Historical v2 image regression/multitask — P01/P03

All **R** from [multitask checkpoint](../planning/R4_RTDETR_MULTITASK_CHECKPOINT.md); same image split/target version within each level. The frozen comparator has no newly matched grouped interval. No cross-level or v2/v3 ranking.

| Level | Constant / frozen / multitask (MAE pp, R) | Uncertainty/qualification |
| --- | --- | --- |
| Image/view, F n224 | Train-mean1.020 / frozen .894 / multitask .732990 | Multitask run-grouped500-draw interval [.656733,.838133]; RMSE .971507, Spearman .494771, R² .159300 |
| Raw run top-three, F n8 | Frozen1.347 / multitask1.627254 | Different aggregate from image MAE; multitask RMSE1.751389/Spearman .738095 |
| Cumulative-maximum run, F n8 | Multitask1.854585 | Different target/postprocessing estimand; not a prospective forecast |
| Multitask detection, F224 | mAP50 .000054; mAP50:95 .000013 | At A-selected .01: TP88/FP57,606/FN9,795 |
| Multitask compute | 160.62 s T4; peak2,654,548,480 bytes | 25,963,235 detector +33,025 scalar-head trainable parameters; λ58.261490 |

The multitask image-level improvement coexists with worse raw run-level MAE. No blanket improvement, reliable physical-damage accuracy or clean bitwise retraining claim follows. Historical CUDA grid-sampler nondeterminism warning remains.

### A5. Label/representation feasibility diagnostics — P00/P05/P11–P14

These are **separate diagnostics**, not rows competing with A1. All values **R**; no fresh raw reading, DINO inference or review-map reconstruction.

| Study | Observation (R) | Scientific limit/source |
| --- | --- | --- |
| Target/version feasibility | v3 current24 teeth; median-28 artifact missing; repeated-photo within-tooth SD about .796pp | Different measurement level; this SD is not a universal minimum detectable model difference. [Ledger](../thesis/TARGET_VERSION_LEDGER.md) |
| AnomalyDINO selected human sample | Prespecified23/38=60.5%; best-of20 29/38=76.3%; heuristic30/38=78.9%; four unsure among42 | Rank7/14 per experiment; same38 used for selection, not population accuracy/equivalence. [Report](../thesis/ANOMALYDINO_RESULT_20260913T215556Z.md) |
| Raw vibration L1 | 472 steady files;50 run features; F exceedance .223 (16passes/null median11) | No predictive L2/L3 run; three domains,300 permutations. [Report](../thesis/RAW_VIB_20260927T095726Z.md) |
| Tooth-sector L1 | 80features; F .223 (26/null17); DAQ-sector .09 | No physical tooth registration; formula/phase/sign assumptions. [Report](../thesis/TOOTH_SECTOR_20260927T102354Z.md) |
| TSA transform agreement | Best circular correlation with DAQ median .997 on472files | Transform-level agreement, not full indicator or physical target validation. Same sector report. |
| Rank-mapped oracle | A n5 MAE .5724 [.2121,1.0777]; matched constant .7430 [.2344,1.3269] | Needs photographs, partial coverage, no deployable statistically established gain. [Report](../thesis/CLOSING_EXPERIMENTS_20260912T171608Z.md) |
| Odd/even photo split | 13runs; correlations .3736/.4011; null exceedances .105/.087 | Shared run photometrics survive; does not quantify causal artifact percentage. Same report. |
| Sorted profile head | Ordered output/loss implemented; no retained matched benefit promoted here | Rank ≠ tooth identity or time. [Model](../../src/phm2026/models/patchtst/model.py), [diagnostics](../thesis/PROFILE_DIAGNOSTICS_V3.json) |
| Historical monotonic rescoring | Eight-run in-sample isotonic score reversal; reported noise matches/beats model about48% | Old fixed-split/version diagnostic, not v3 LOEO or a training-fitted calibration gain. [Report](../thesis/OVERNIGHT_20260912T054144Z.md), inventory P16. |

### A6. Synthetic controls — deliberately not PHM observations

Only this table contains generated target-aligned features. All values **R** from [closing controls](../thesis/CLOSING_EXPERIMENTS_20260912T171608Z.md); later retest grids are separate noise/weight protocols and are not pooled. Synthetic pipeline sensitivity does not prove real-data “no signal,” real-data leakage absence or universally ineffective distillation.

| SYNTHETIC condition | SYNTHETIC result (R) | Interpretation |
| --- | --- | --- |
| α0, original per-minute noise | MAE .7998 ±.0472 (three seeds) | Approximately constant reference under this synthetic mechanism |
| α.2, all72channels | MAE .1616 ±.0197; reported3/3 seed comparisons favor injected signal | Many minute/channel draws make averaging highly informative; not a natural-data sensitivity threshold |
| α.6, one informative channel | MAE .4996 ±.0515 | Demonstrates this imposed channel can be detected |
| Rank distillation α.6, weight1 | ΔMAE +.0453 [.018,.074] / +.0965 [.030,.161], two seeds | Harm in a nearly solved synthetic regime; no universal transfer conclusion |

No AP/AUROC/calibration threshold is invented for PHM scalar regression. Old v1/v2/missing median-28 and untraceable August1.011 are excluded from current v3 headline comparison. The historical reports and retired values are preserved.

## B. REASSEMBLE core unimodal/representation comparison

4,530 completed actions/509 failures/148 recordings. **V** point estimates from six S1 `*_perm00.npz` files; **R** paired/individual intervals from [Section1 assessment](../../runs/reassemble/20260927T154732Z-section1/assessment/results.json) and [report](../../artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md). Brier/ECE15 use saved probabilities; recall uses original training-selected hard decisions.

| Model | AP V [R interval] | AUROC V [R interval] | Brier V | ECE15 V | Failure recall V |
| --- | --- | --- | --- | --- | --- |
| prior | 0.108347 [0.096293, 0.122143] | 0.483853 [0.452016, 0.516156] | 0.099756 | 0.000172 | 0.000000 |
| majority | 0.112362 [0.101110, 0.124155] | 0.500000 [0.500000, 0.500000] | 0.112362 | 0.112362 | 0.000000 |
| action_only | 0.180805 [0.161275, 0.201790] | 0.685090 [0.662251, 0.708804] | 0.095052 | 0.008046 | 0.764244 |
| sensor_statistics | 0.429392 [0.380128, 0.482839] | 0.779325 [0.754879, 0.803975] | 0.080448 | 0.017396 | 0.614931 |
| rtdetr | 0.230658 [0.198328, 0.270102] | 0.697795 [0.671583, 0.723162] | 0.094299 | 0.007017 | 0.662083 |
| patchtst | 0.241591 [0.210223, 0.282594] | 0.705351 [0.679796, 0.730357] | 0.093735 | 0.006734 | 0.563851 |

The fold-specific prior is not one globally constant score: its pooled AUROC .4839/AP .1083 can differ from .5/prevalence because training prevalences differ across folds. Majority is a global constant score. Do not interpret this as an erroneous definition of chance.

**R paired findings:** PatchTST−statistics ΔAP −.1878 [−.2314,−.1407], ΔAUROC −.0740 [−.1004,−.0469]. Visual−action ΔAP+.0499 [.0225,.0836], but ΔAUROC+.0127 [−.0154,.0406]; PatchTST−action analogous AUROC uncertainty. Both deep branches initially failed the joint two-metric admission gate. Section1B's later sensor/statics fusion question was informed by these results, so it was exploratory.

Architecture/budget: visual frozen pretrained CNN896→128/head114,945, selected5/5/10/10/5 epochs; scratch PatchTST109,505 parameters, every fold selects6; sensor logistic220features+221 coefficients/intercept before calibration. Context/action4 is a separate baseline. Original branches receive unweighted affine sigmoid calibration and training-side balanced-accuracy thresholds. Full probability-score/hard-decision intervals remain in linked sources; there is no single shared .5 operating point in this table.

## C. Original F1–F6 clean fusion comparison

Use these original core scores throughout the main architecture chapter. **V** all eight core metrics agree exactly with [Section2 results](../../runs/reassemble/20260927T192852Z-section2/assessment/results.json); **R** intervals. F2/U1/U2 are reused evidence from S1/S1B, not independent new confirmation. F3–F6 deploy three-seed probability means.

| Model | AP V [R interval] | AUROC V [R interval] | Brier V | ECE15 V |
| --- | --- | --- | --- | --- |
| F1 | 0.445742 [0.394939, 0.498878] | 0.795061 [0.772798, 0.817372] | 0.083374 | 0.035468 |
| F2 | 0.447299 [0.396817, 0.501921] | 0.794968 [0.772714, 0.817765] | 0.078443 | 0.013812 |
| F3 | 0.412231 [0.359335, 0.467162] | 0.785584 [0.761495, 0.808997] | 0.082715 | 0.014914 |
| F4 | 0.443725 [0.393492, 0.497415] | 0.781506 [0.757085, 0.806252] | 0.080179 | 0.012786 |
| F5 | 0.444549 [0.395704, 0.495781] | 0.775987 [0.751060, 0.800255] | 0.080640 | 0.012569 |
| F6 | 0.441356 [0.393508, 0.493658] | 0.775523 [0.751413, 0.798935] | 0.080711 | 0.012374 |

### C1. Paired contrasts — discrimination versus probability quality

Point differences **V**; all intervals **R**. Gate contrasts are the original marginal intervals, with additional multiplicity criteria below. F2−F1 is a **post-hoc descriptive** review contrast, sign-reversed from the stored F1−F2 [review table](../../runs/reassemble/20260927T192852Z-section2/assessment/review_comparisons.json); its interval is not silently promoted to a predeclared discovery test.

| Contrast | ΔAP V [R interval] | ΔAUROC V [R interval] | ΔBrier V [R interval] | ΔECE V [R interval] |
| --- | --- | --- | --- | --- |
| F2−U1 | +0.017907 [0.008603, 0.028284] | +0.015644 [0.006030, 0.025465] | -0.002005 [-0.003099, -0.000908] | -0.003584 [-0.012700, 0.009897] |
| F2−F1 | +0.001556 [-0.007607, 0.011165] | -0.000093 [-0.004315, 0.004187] | -0.004931 [-0.007201, -0.002730] | -0.021656 [-0.027614, -0.005703] |
| F3−U1 | -0.017160 [-0.057276, 0.022977] | +0.006260 [-0.016598, 0.029467] | +0.002267 [-0.000490, 0.005172] | -0.002482 [-0.010919, 0.008708] |
| F4−F2 | -0.003573 [-0.013355, 0.005746] | -0.013462 [-0.021985, -0.005440] | +0.001736 [0.000529, 0.002987] | -0.001027 [-0.009891, 0.006899] |
| F5−F2 | -0.002749 [-0.022816, 0.017071] | -0.018981 [-0.028859, -0.009498] | +0.002197 [0.000567, 0.003869] | -0.001243 [-0.010667, 0.007894] |
| F6−F2 | -0.005943 [-0.024796, 0.013695] | -0.019445 [-0.028801, -0.010239] | +0.002268 [0.000661, 0.003940] | -0.001438 [-0.010234, 0.007391] |

F2 has no established AP/AUROC advantage over F1; its probability scores are better in this descriptive paired review. F2's AP/AUROC gain over U1 supports the bounded **combined-pipeline** comparison. A matched sensor-only meta-calibration reference was not established, so “unique visual information caused the gain” is stronger than this design identifies. Descriptive branch disagreement/rescues support a complementarity interpretation but are not its causal decomposition.

Every gate misses the predeclared AP gain≥.01, positive simultaneous AP lower bound, ≥3 positive folds and AUROC lower>−.01 package. Simultaneous AP lower bounds: F4−F2 −.0151, F5 −.0265, F6 −.0276 (R). Their lower AUROC and nonqualifying AP do not establish all adaptive families' inferiority or equivalence. Gate link/convexity/intercept/calibration/loss differences confound adaptation attribution; see inventory R07.

### C2. Decisions and thresholds

All points/counts **V** from saved `*_hard`, not assessment-optimized thresholds. Each model has a five-element threshold vector (folds0–4) read from training-side saved metadata. Balanced accuracy does not encode an agreed industrial cost. False alarms below are action-level false positives, not alarms per hour.

| Model | Balanced accuracy | Macro F1 | Failure recall | Failure precision | TP/FN/FP/TN | Thresholds0–4 |
| --- | --- | --- | --- | --- | --- | --- |
| U1 | 0.705625 | 0.622332 | 0.614931 | 0.276502 | 313/196/819/3202 | 0.14, 0.13, 0.11, 0.15, 0.13 |
| U2 | 0.641412 | 0.515284 | 0.662083 | 0.180988 | 337/172/1525/2496 | 0.14, 0.12, 0.12, 0.11, 0.10 |
| F1 | 0.708684 | 0.633125 | 0.603143 | 0.291271 | 307/202/747/3274 | 0.12, 0.16, 0.14, 0.13, 0.17 |
| F2 | 0.711743 | 0.634000 | 0.611002 | 0.292019 | 311/198/754/3267 | 0.10, 0.11, 0.11, 0.12, 0.11 |
| F3 | 0.699880 | 0.602437 | 0.638507 | 0.252918 | 325/184/960/3061 | 0.11, 0.13, 0.10, 0.09, 0.08 |
| F4 | 0.704705 | 0.626770 | 0.603143 | 0.282689 | 307/202/779/3242 | 0.15, 0.13, 0.13, 0.13, 0.12 |
| F5 | 0.700117 | 0.620569 | 0.601179 | 0.274686 | 306/203/808/3213 | 0.14, 0.13, 0.12, 0.13, 0.13 |
| F6 | 0.701920 | 0.638422 | 0.571709 | 0.301242 | 291/218/675/3346 | 0.15, 0.14, 0.12, 0.13, 0.17 |

F2 detects311/509 failures with754 false-positive successes at its selected thresholds; U1 detects313 with819 false positives. Improved AP is not a demonstrated recall gain or validated online decision policy. Threshold-training scores condition on their selection/calibration; F2's documented global-OOF training-side threshold dependency is not a newly proven outer-assessment leak. [S1B protocol](../reassemble/SECTION_1B_PROTOCOL.md).

### C3. Model and fitting cost — separate timing scopes

All timings/parameter accounting **R** from [Section2 costs](../../runs/reassemble/20260927T192852Z-section2/assessment/results.json); TASK4 verifies source interpretation, not wall-clock measurements. F1 has0 fusion parameters; F2 has3. Neural counts below are **per seed**; deployment uses three seeds, plus the shared branches.

| Head | Parameters/seed by fold | Summed inner search s | Summed final fitting s | Warm three-seed head µs/row range |
| --- | --- | --- | --- | --- |
| F3 | 61825, 61825, 61825, 61825, 61825 | 89.73 | 19.87 | 0.676–0.997 |
| F4 | 74, 74, 74, 74, 146 | 187.87 | 30.51 | 0.895–1.221 |
| F5 | 658, 330, 658, 658, 330 | 187.94 | 30.72 | 0.885–1.264 |
| F6 | 362, 722, 722, 722, 722 | 187.52 | 30.81 | 0.879–1.248 |

Warm head timings exclude branch inference, normalization, transfer, raw decoding and action acquisition. The broader original [efficiency study](../../artifacts/reassemble/reports/EFFICIENCY_HANDOFF.md) is also **R**: three deterministic segments, sensors in RAM, cached compressed-video decoding, T4/four CPU threads; **sequential component sums**, not measured production latency.

| Model | Total / fitted parameters (R) | Checkpoint MiB (R) | Component sum ms (R) |
| --- | --- | --- | --- |
| U1 | 223 / 223 | .039 | 26.267 |
| U2 | 11,305,059 / 114,947 | 77.607 | 478.415 |
| F1 | 11,305,282 / 115,170 | 77.646 | 504.688 |
| F2 | 11,305,285 / 115,173 | 77.646 | 504.693 |
| F5 | 11,307,256 / 117,144 | 77.664 | 564.038 |
| F6 | 11,307,448 / 117,336 | 77.663 | 564.021 |
| D6 | 11,307,448 / 117,336 | 77.664 | 564.016 |

“Fitted” includes calibrator coefficients and fitting elsewhere in the pipeline; it is not the number fine-tuned during robustness. Original source weights may store unused detector components. Parameter scopes therefore differ legitimately from head-only counts. No energy, acquisition-window latency, operational monetary cost or operator usability measurement is available.

## D. Original robustness testing

### D1. Frozen clean-trained models — R08

**V** AP below recomputed from22 saved condition arrays in [Section3 predictions](../../runs/reassemble/20260927T204649Z-section3/predictions); AP/AUROC/Brier/ECE agree with [results.json](../../runs/reassemble/20260927T204649Z-section3/results.json). Each graded severity has one seeded realization, full core coverage. These severities are not equal physical doses across modalities. Timestamps remain unchanged. V1 pixel Gaussian σ; V2 blurσ; V3 frame-removal fraction; S1 sensor Gaussian×training SD; S2 channel-removal fraction; S3 time-block fraction; S4 stuck force/torque; V4 visual absent; S5 sensors absent. No training or new corruption inference here.

| Condition | U1 AP V | U2 AP V | F1 AP V | F2 AP V | F5 AP V | F6 AP V |
| --- | --- | --- | --- | --- | --- | --- |
| clean | 0.429392 | 0.230658 | 0.445742 | 0.447299 | 0.444549 | 0.441356 |
| V1_0.02 | 0.429392 | 0.163143 | 0.408708 | 0.411828 | 0.192096 | 0.181311 |
| V1_0.05 | 0.429392 | 0.126277 | 0.410948 | 0.407553 | 0.144516 | 0.140871 |
| V1_0.1 | 0.429392 | 0.116461 | 0.388516 | 0.396275 | 0.128782 | 0.127483 |
| V2_1.0 | 0.429392 | 0.223039 | 0.451224 | 0.447781 | 0.443434 | 0.445831 |
| V2_2.0 | 0.429392 | 0.186474 | 0.424102 | 0.439073 | 0.435192 | 0.437278 |
| V2_4.0 | 0.429392 | 0.150094 | 0.347553 | 0.409889 | 0.406062 | 0.417875 |
| V3_0.1 | 0.429392 | 0.232029 | 0.447326 | 0.447914 | 0.443494 | 0.441161 |
| V3_0.3 | 0.429392 | 0.228560 | 0.448379 | 0.447979 | 0.446998 | 0.443272 |
| V3_0.5 | 0.429392 | 0.219342 | 0.441134 | 0.445483 | 0.439156 | 0.438063 |
| S1_0.1 | 0.394564 | 0.230658 | 0.418244 | 0.415984 | 0.392916 | 0.396052 |
| S1_0.5 | 0.266863 | 0.230658 | 0.302948 | 0.296003 | 0.271138 | 0.276010 |
| S1_1.0 | 0.163710 | 0.230658 | 0.223578 | 0.222160 | 0.175258 | 0.178769 |
| S2_0.1 | 0.398811 | 0.230658 | 0.425084 | 0.421052 | 0.373392 | 0.373426 |
| S2_0.3 | 0.331292 | 0.230658 | 0.370502 | 0.363472 | 0.353878 | 0.326455 |
| S2_0.5 | 0.283937 | 0.230658 | 0.324586 | 0.319781 | 0.318323 | 0.301363 |
| S3_0.1 | 0.417552 | 0.230658 | 0.441526 | 0.439956 | 0.429970 | 0.405389 |
| S3_0.3 | 0.386152 | 0.230658 | 0.423244 | 0.413523 | 0.418728 | 0.378160 |
| S3_0.5 | 0.316464 | 0.230658 | 0.363146 | 0.348980 | 0.354350 | 0.326689 |
| V4 | 0.429392 | unavailable | 0.429392 | 0.429392 | 0.429392 | 0.429392 |
| S4 | 0.418470 | 0.230658 | 0.439762 | 0.439648 | 0.423004 | 0.421061 |
| S5 | unavailable | 0.230658 | 0.230658 | 0.230658 | 0.230658 | 0.230658 |

Selected F2 probability-quality/ranking observations below are **V**, with no new intervals or selected-condition significance claim. Full paired absolute/difference-in-degradation intervals remain **R** in the linked results. Ranking retention and probability calibration can diverge severely.

| Condition | F2 AUROC V | F2 Brier V | F2 ECE15 V |
| --- | --- | --- | --- |
| clean | 0.794968 | 0.078443 | 0.013812 |
| V1_0.1 | 0.725038 | 0.296807 | 0.436835 |
| V2_4.0 | 0.761499 | 0.081574 | 0.014590 |
| S1_1.0 | 0.615315 | 0.479791 | 0.525090 |
| S2_0.5 | 0.737359 | 0.089884 | 0.016404 |
| S3_0.5 | 0.754687 | 0.091827 | 0.042078 |
| S4 | 0.769412 | 0.082229 | 0.023704 |

**R mechanism/outcome decision:** 0/12 high-severity family×gate checks satisfy both expected allocation response and a qualifying performance-retention advantage. This does not mean all weights stay fixed. S2/S3 have the intended degraded-sensor weight shift; V1/S1 shifts can be opposite. Original [robustness report](../../artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md) retains all twelve checks. F2's S1 strong AP drop is not external industrial validation.

Complete absence outputs are the surviving calibrated branch, with its original branch threshold; equality is an explicit structural policy. The unavailable unimodal model abstains. Both-absent handling is a source/policy property; this original condition suite does not contain a both-absent empirical row.

### D2. Completed original modality-dropout F6 — R09

Separate gate fitting, same original folds and three seeds; categorical training masks .15/.15/.70. Point AP/AUROC **V**; Δ intervals **R** from [dropout results](../../runs/reassemble/20260927T204649Z-modality-dropout/results.json). All eleven saved condition arrays checked. Do not confuse this with September Gaussian augmentation.

| Condition | Dropout AP V | Dropout AUROC V | ΔAP vs ordinary F6 V [R interval] |
| --- | --- | --- | --- |
| clean | 0.437651 | 0.775374 | -0.003705 [-0.008546, 0.000288] |
| V4 | 0.429392 | 0.779325 | +0.000000 [0.000000, 0.000000] |
| S5 | 0.230658 | 0.697795 | +0.000000 [0.000000, 0.000000] |
| V1_0.02 | 0.179025 | 0.660129 | -0.002286 [-0.008088, 0.003683] |
| V1_0.05 | 0.135076 | 0.595049 | -0.005795 [-0.010104, -0.001992] |
| V1_0.1 | 0.127394 | 0.577446 | -0.000089 [-0.003503, 0.005009] |
| S1_0.1 | 0.396898 | 0.764075 | +0.000846 [-0.002657, 0.004556] |
| S1_0.5 | 0.273890 | 0.666955 | -0.002120 [-0.007877, 0.003756] |
| S1_1.0 | 0.180256 | 0.605891 | +0.001487 [-0.002539, 0.005984] |
| V2_2.0 | 0.433377 | 0.755297 | -0.003902 [-0.013221, 0.004973] |
| S2_0.3 | 0.351098 | 0.751943 | +0.024643 [0.006289, 0.042840] |

No overall robustness advantage is established. The positive channel-loss and negative image-noise marginal conditions are mixed secondary findings. Singleton masked weights have zero gate-parameter gradient, so exact full-loss equality is expected mathematically; dropout cannot recover absent information in this architecture. [Handoff](../../artifacts/reassemble/reports/MODALITY_DROPOUT_HANDOFF.md).

## E. September exploratory extensions

All values/intervals in E are **R**, transcribed from the [completed scope-adjusted handoff](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md) and [pooling handoff](../../artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md), not independently recalculated in TASK4. The same cohort was repeatedly examined. Original frozen core results are not rewritten.

### E1. Training budget and same-sensor hybrid — R11/R12

| Model | AP R | AUROC R | Brier R | ECE15 R |
| --- | --- | --- | --- | --- |
| S-HIST, original one-seed candidate | .2416 | .7054 | .0937 | .0067 |
| S-6, matched three-seed procedure | .2557 | .7155 | .0929 | .0114 |
| S-LONG | .2853 | .7298 | .0919 | .0156 |
| S-STATS | .4294 | .7793 | .0804 | .0174 |
| S-HYBRID, two sensor representations | .4403 | .7948 | .0791 | .0155 |

| Contrast | ΔAP R [95%] | ΔAUROC R [95%] |
| --- | --- | --- |
| S-LONG−S-6 | +.0297 [.0122,.0451] | +.0142 [.0033,.0247] |
| S-LONG−S-STATS | −.1441 [−.1861,−.1009] | −.0496 [−.0760,−.0237] |
| S-6−S-HIST | +.0141 [−.0045,.0338] | +.0102 [−.0031,.0233] |
| S-HYBRID−S-STATS | +.0110 [.0054,.0181] | +.0155 [.0090,.0226] |

Longer training helps this matched PatchTST recipe but does not beat statistics alone. Same-sensor representation stacking helps historically; it is not another sensing modality. Reported thresholds/calibrators are training-side; exact values remain in the separate run's fits. Summed120 fit rows =2,460.01s, excluding preparation/cache extraction/full wall time.

### E2. Static-anchored adaptation — R13

| Model | AP R | AUROC R | Recall R | Precision R | Brier R | ECE15 R |
| --- | --- | --- | --- | --- | --- | --- |
| A0 | .4473 | .7950 | .6071 | .2977 | .0784 | .0138 |
| A-CONSTANT | .4457 | .7950 | .6071 | .2937 | .0785 | .0129 |
| A-ADAPTIVE | .4683 | .7993 | .5874 | .3118 | .0770 | .0180 |

| Contrast | ΔAP R [95%] | ΔAUROC R [95%] |
| --- | --- | --- |
| Adaptive−A0 | +.0210 [.0015,.0419] | +.0044 [−.0031,.0115] |
| Adaptive−constant adjustment | +.0226 [.0036,.0432] | +.0043 [−.0031,.0115] |
| Constant adjustment−A0 | −.0016 [−.0035,.0003] | +.0001 [−.0005,.0006] |

Positive exploratory clean AP finding, with lower recall/higher ECE than A0. A0 shares F2 probabilities within its parity tolerance, but the threshold protocol differs; do not copy original F2 hard decisions. Marginal intervals, no blanket multiplicity-adjusted claim. Retained391 fit rows sum193.46s; not full wall time. Coefficient scale changes are not normalized reliability weights.

### E3. Equal Gaussian-exposure robustness — R14

| Comparison | ΔAP R [95%] | ΔAUROC R [95%] | Disposition |
| --- | --- | --- | --- |
| Augmented adaptive−augmented F2, mean six seen-family conditions | +.0097 [−.0034,.0228] | +.0105 [−.0027,.0248] | Primary inconclusive |
| Same models, clean | +.0168 [.0010,.0305] | See full report | Condition-specific; not overall robustness |
| Strong sensor noise, same models | +.0333 [.0184,.0471] | See full report | Secondary favorable condition |
| Strong channel loss, same models | −.0796 [−.1090,−.0526] | See full report | Secondary harm |
| Strong temporal block loss, same models | −.0848 [−.1241,−.0464] | See full report | Secondary harm |
| Augmented adaptive−own clean-trained adaptive, on clean | −.0173 [−.0306,−.0047] | See full report | Clean loss; .01-margin noninferiority fails |

Clean AP/AUROC: clean_F2 .4473/.7950; augmented_F2 .4341/.7805; clean_F6 .4449/.7873; augmented_F6 .4335/.7867; clean_adaptive .4682/.7997; augmented_adaptive .4509/.7940 (all R). Historical F6 .4414/.7755 is a different fitted procedure. Do not replace one with the other. Training mixture50/25/25; five assessment realizations for stochastic faults; original branches retained. Retained540 fit rows sum433.10s, excluding full wall time. Full scores/calibration/condition intervals remain in the handoff. The .01 noninferiority margin belongs to this study, not October's strict zero-clean-loss criterion.

### E4. Boundary-aware pooling — R15

| Variant | AP R | AUROC R | Brier R | ECE15 R | ΔAP vs V0 R [95%] | Simultaneous lower R |
| --- | --- | --- | --- | --- | --- | --- |
| V0 whole mean | .2307 | .6978 | .0943 | .0070 | reference | — |
| V1 two halves | .2556 | .7119 | .0930 | .0070 | +.0249 [−.0045,.0499] | −.0118 |
| V2 early/mid/late | .3080 | .7668 | .0891 | .0093 | +.0774 [.0415,.1106] | +.0306 |
| V3 last quarter | .319146 | .7728 | .0884 | .0139 | +.0885 [.0424,.1293] | +.0301 |
| V4 early/late | .2922 | .7547 | .0905 | .0146 | +.0616 [.0272,.0943] | +.0177 |
| V5 ordered GRU+positions | .2250 | .7167 | .0940 | .0130 | −.0056 [−.0345,.0212] | −.0425 |

Five AP contrasts use Bonferroni percentile .005/.995 bounds. One historical seed family; V0–V4 parameters114,945/115,073/115,201/114,945/115,073; GRU82,433; budgets differ as documented. The positive observation concerns temporal **location/aggregation**, not proof of learned temporal order. V3 uses no sequence-order model; V5's change is unresolved.

Exactly one selected V3 static-F2 follow-up: **R AP .493437** versus original .447299; paired ΔAP+.0461 [.0260,.0632], ΔAUROC+.0403 [.0291,.0522]. Strong exploratory support within this protocol, selected after comparing pooling variants on exposed data. Not a pristine confirmation or a model combining the sensor hybrid, anchored head and pooling winners. Thresholds use training-side OOF rules; selective-prediction coverage90/80% is computational abstention, not a human-uncertainty validation.

September Task1 was partly attempted and subsequently cancelled; no completed temporal/fine-tuning result is promoted from it. The completed pooling study is a separate protocol. Historical/partial outputs remain preserved.

## F. October encoder, fine-tuning and quality-aware studies

Each subsection below has its own protocol. Full-cohort AP around .440 is not a recomputation of core .447299: G/C calibration, budgets and fixed .5 operating points differ. E4/E7/E8 results are **R** in TASK4. E6 pilot points are **V** with **R** intervals; E5 values remain **R**.

### F1. Spatial hybrid encoder versus CNN — R16 / E4

| Representation | Visual AP R | Sensor AP R | F2 AP R | Active frozen parameters R | Head parameters R |
| --- | --- | --- | --- | --- | --- |
| CNN only | .221644 | .420926 | .440764 | 11,190,112 | 114,945 |
| CNN+hybrid encoder | .171915 | .420926 | .424979 | 16,155,232 | 98,561 |

Full4530/509/148, fixed16 frames/five-epoch heads/G-only fit and C-only calibration. F2 ΔAP−.015785 [−.024804,−.005800], reported2,000 valid recording resamples. Transformer executes spatial AIFI, not temporal attention; widths/capacity/compute differ. Reported extraction71.00min including decoding (883.14s recorded compute); training-only extractor .121970/.192610s per action excluding decoding; new head fitting675.26s. [Exact report/cost sources](../../00_experiments/rt_detr_encoder_comparison/results/run_01/comparison/RESULTS_SUMMARY.md). No attention-only causal conclusion.

### F2. Asymmetric epoch-budget fine-tuning — R17 / E7

| Condition | Epochs R | Visual AP R | Sensor AP R | F2 AP R | Summed raw fit h R | C/V prediction h R |
| --- | --- | --- | --- | --- | --- | --- |
| Frozen16 | 5 | .221644 | .420803 | .440680 | .164 | .000 |
| Tuned16 | 2 | .224466 | .420803 | .437521 | 9.086 | 3.424 |
| Frozen32 | 5 | .219427 | .420803 | .439584 | .160 | .000 |
| Tuned32 | 2 | .230609 | .420803 | .438566 | 12.456 | 5.118 |

Fivefold complete4530-action cohort/one seed family,100 visual fits. Tuned16−frozen16 F2 Δ−.003159 [−.012573,.008052], primary inconclusive. Frame contrasts also unresolved; do not infer pure fine-tuning or convergence effects from unequal budgets. Original shared extraction2.84h, including2.35h pixel/cache/transfer; cached frozen timing excludes it. All threshold metrics use .5; AUROC/Brier and full decision tables remain in the [study report](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/comparison/RESULTS_SUMMARY.md) and its linked numerical sources. Cost is a scope-qualified observation, not an equal-compute experiment.

### F3. Matched two-epoch32-frame diagnosis — R18 / E8

| Seed | Method | Frozen AP R | Tuned AP R | ΔAP R [95%] |
| --- | --- | --- | --- | --- |
| 42 | Visual | .222708 | .230609 | +.007902 [−.017312,.033219] |
| 42 | Uniform | .444720 | .440946 | −.003774 [−.014238,.007851] |
| 42 | F2 | .439363 | .438566 | −.000796 [−.006424,.006072] |
| 20261023 | Visual | .216799 | .200517 | −.016282 [−.039636,.009790] |
| 20261023 | Uniform | .436495 | .428489 | −.008006 [−.018180,.003279] |
| 20261023 | F2 | .435202 | .432380 | −.002822 [−.008285,.003602] |

Fivefold/full cohort for each seed, equal epochs/data, not equal compute.75 new/25 reused fits; elapsed through evaluation21.845h reported, with different scope from E7 summed fits. Fixed .5; conditional recording intervals; two seeds share recordings. Branch-error/calibration diagnostics do not isolate a cause. Result: **CAUSE_NOT_RESOLVED**. Full probability/operating-point diagnostics are linked in the [report](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results/comparison/RESULTS_SUMMARY.md), rather than fabricated here. Same-seed reused fits are not independent replication.

### F4. Static selected-model noise pilot — R19 / E5

One fold_01,753 actions/77 failures/26 recordings; AP calculated per realization then averaged over three repeats where stochastic. No comparator adaptive head. All **R** from [noise report](../../00_experiments/fusion_noise_test/results/run_02/comparison/RESULTS_SUMMARY.md).

| Condition | Visual AP R | Sensor AP R | F2 AP R | AP drop R [95%] |
| --- | --- | --- | --- | --- |
| Clean | .200401 | .290531 | .307929 | 0, reference |
| Image Gaussianσ.10 | .123958 | .290531 | .284640 | +.023289 [−.003184,.042857] |
| Sensor Gaussian×1.00 | .200401 | .127743 | .169409 | +.138520 [.070831,.221115] |
| Strong channel loss | .200401 | .201146 | .219848 | +.088081 [.018610,.162135] |
| Strong time loss | .200401 | .218541 | .240681 | +.067248 [.004979,.148065] |

The positive sensor-noise deterioration is supported under this fault/pilot. Negative point F2−unchanged-branch contrasts do not establish reliable harmful fusion: their reported intervals all cross zero.51 inference realizations/753 rows each; reported saved-job4.037h excludes preparation/evaluation/packaging. Complete loss explicitly returns sensor AP .290531 or visual .200401; both absent abstains. Raw noise policy is recorded, not external industrial validity.

### F5. Controlled quality-aware pilot — R20 / E6

Same753/77/26 coverage. A/B/C trained on exactly3,777 inner-OOF parent actions/11,331 rows with weights .5/.25/.25;3/11/27 parameters, no new branch training/output calibrator; threshold .5. **V**34 indexed tables,25,602 rows,196 finite metric sets; labels/keys agree;753 both-absent rows explicitly unavailable. Strict no-clean-loss criterion remains the pilot's zero margin; do not borrow September's .01 margin.

| Model | Clean AP V | Primary mean AP V | Primary mean AUROC V | Primary mean Brier V | Clean Brier V | Clean recall at .5 V |
| --- | --- | --- | --- | --- | --- | --- |
| historical_static | 0.307929 | 0.255937 | 0.664432 | 0.135867 | 0.083800 | 0.181818 |
| static_augmented | 0.307397 | 0.253996 | 0.667111 | 0.099508 | 0.083700 | 0.064935 |
| quality_additive | 0.292965 | 0.237360 | 0.618766 | 0.098168 | 0.084002 | 0.077922 |
| quality_interaction | 0.312168 | 0.257009 | 0.670997 | 0.088445 | 0.082399 | 0.129870 |
| visual | 0.200401 | 0.162982 | 0.576661 | 0.138361 | 0.089839 | 0.012987 |
| sensor | 0.290531 | 0.239087 | 0.673832 | 0.130182 | 0.085946 | 0.142857 |

Primary means first calculate each metric per realized table, then equally average repeats, severities and the two Gaussian families. No pooling of repeated subjects and no AP of averaged probabilities. Mean AUROC/Brier here use that same declared aggregation as descriptive additional metrics; no new inferential primary endpoint or CI is assigned to them. Do not compare these means directly to clean pooled metrics as if they shared an input distribution.

| Contrast | ΔAP V | 95% interval R | Disposition |
| --- | --- | --- | --- |
| C−A primary | +.003012 | [−.026711,.032165] | Inconclusive; does not establish superiority/equivalence |
| C−B primary | +.019649 | [−.000813,.038743] | Inconclusive interaction contribution |
| B−A primary | −.016636 | [−.030676,−.002429] | Reported secondary deterioration |
| A−historical primary | −.001941 | [−.005019,.001816] | Augmentation benefit unresolved |
| C−A clean | +.004771 | [−.034258,.044544] | Clean preservation unresolved at zero margin |

Clean decision counts at .5 (V): historical TP14/FP9; A TP5/FP4; B TP6/FP5; C TP10/FP4;77 failures total. These are low-recall decisions, not failed ranking definitions or a threshold optimized for plant costs. No pilot ECE comparison is promoted here as equivalent to the core15-bin evaluation; source per-condition metrics retain their recorded definitions. [Full summary](../../00_experiments/adaptive_fusion_robustness/results/run_01/RESULTS_SUMMARY.md), [intervals](../../00_experiments/adaptive_fusion_robustness/results/run_01/comparison/paired_intervals.csv), [per-condition metrics](../../00_experiments/adaptive_fusion_robustness/results/run_01/comparison/per_condition_metrics.csv).

All C−A individual severity AP intervals span zero. Image/blur-side point gains and sensor/time-side losses do not establish reliable fault-specific mechanisms. Eight observed q values are not eight validated reliability measurements; direct q can predict outcome content, while interactions/capacity change coefficients. No q-only/interaction-only/content-matched reliability control was completed.

**R cost:** CPU-only eight threads, approximate active scientific12.94h/results18.82h elapsed, max observed RSS1.723GiB, study storage .578GiB; not new timing. [Runtime](../../00_experiments/adaptive_fusion_robustness/results/run_01/provenance/final_runtime.json). Extra folds require fitting/inference and separate approval, and would remain development-exposed.

## Headline disposition

**P central result:** retain the original architecture comparison: F2 improves the selected combined pipeline over U1, while original gates do not establish incremental value over the simple static reference. It does not establish F2 discrimination superiority over F1 or a causal adaptation explanation.

**R strongest separate exploratory gain:** last-quarter representation plus its own static fusion follow-up. Its .493437 AP belongs in the exploratory chapter with its selection/coverage limitations; it does not replace the central core table.

No combined-best model, audio score, true clock-shift result, independent MSM score, physical gear-damage accuracy, prospective alarm rate or full reproducibility certification is available. Do not fill missing cells with estimates or interpret untested outcomes as negative performance. **STOP after the evidence handoff.**
