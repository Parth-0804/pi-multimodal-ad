# FINAL REASSEMBLE HANDOFF

## A. Original purpose

REASSEMBLE was added as a second empirical study to test fusion where explicit execution labels and simultaneous deployable modalities support a defensible predictive comparison. Its purpose was to test prerequisites, complementarity and robustness, not to make named Transformer architectures win.

## B. Relationship to PHM

PHM remains Study 1: continuous damage estimation with a provisional image-derived target, few independent runs, and restricted deployment modalities. REASSEMBLE supplies a different, binary task with more recording groups. Task-appropriate metrics differ across the two empirical studies because PHM is a continuous damage-estimation problem whereas REASSEMBLE is a binary execution-failure classification problem. Numerical MAE/RMSE values are never ranked against AUROC/AUPRC/F1.

## C. Dataset

The frozen primary cohort has **4,530 high-level action segments**, **509 failures**, and **148 recordings**. Failure is positive. Actions are pick, insert, remove and place. The cohort uses the hand camera and five sensor streams, 22 scalar channels, 512 progress positions and 220 engineered statistics. Available raw inventory contains 149 recordings; audited exclusions and primary-task/dual-complete criteria determine the final cohort. Audio remains secondary.

| Action | Success | Failure |
| --- | --- | --- |
| insert | 913 | 243 |
| pick | 1092 | 98 |
| place | 1066 | 22 |
| remove | 950 | 146 |


## D. Evaluation

The exact five outer and four inner recording-disjoint folds are reused throughout. Branch/fusion fitting, scaling, selection, calibration and thresholds use training data only; additional nested branch cross-fitting excludes inner assessment recordings. Uncertainty uses 2,000 paired recording-cluster bootstrap replicates conditional on fitted models. Section 1/1B controls cyclically permuted labels within recording/action strata and reran full nested procedures: 19 nulls give minimum plus-one p=0.05. Those controls test a conditional cyclic-exchangeability null, not arbitrary IID chance. No corruption-specific refit or outer-test tuning occurred. This is an adaptive exploratory sequence, not independent confirmation.

## E. Section 1

Statistical sensor AUROC/AP: 0.7793 [0.7549, 0.8040] / 0.4294 [0.3801, 0.4828]. RT-DETR: 0.6978 [0.6716, 0.7232] / 0.2307 [0.1983, 0.2701]. PatchTST: 0.7054 [0.6798, 0.7304] / 0.2416 [0.2102, 0.2826]. Both neural branches improved AP beyond action context, but their standalone AUROC improvement remained unresolved. Statistics outperformed the tested PatchTST; no further tuning was performed. The original Section 1 gate remained conditional and was not rewritten.

## F. Section 1B

Fusion admissibility tested incremental information beyond the strongest sensor representation rather than requiring the old standalone visual gate. F2 minus sensor: AUROC 0.0156 [0.0060, 0.0255]; AP 0.0179 [0.0086, 0.0283]. RT-DETR correctly classified 97 sensor-missed failures across 61 recordings. Sensor permutation p-values were 0.05 / 0.05. The oracle remained diagnostic. FUSION GO justified the bounded architecture comparison.

## G. Section 2

Clean result: **SIMPLE FUSION SUFFICIENT**. F2 is the principal static reference; F1 has similar point discrimination but poorer calibration. No gate establishes a clean AP gain and all lose AUROC relative to F2. F3 also does not establish an AP gain over U1. Context changes weights, but that is not itself useful adaptation. The primary proposed F6 was retained as a falsifiable model, not redesigned.

| Model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE | Parameters | Latency ms* |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Prior | 0.4839 | 0.1083 | 0.5000 | 0.4702 | 0.0000 | 0.0000 | 0.0998 | 0.0002 | 1 | not measured |
| Action only | 0.6851 | 0.1808 | 0.6505 | 0.4835 | 0.7642 | 0.1727 | 0.0951 | 0.0080 | 7 | not measured |
| Sensor statistics | 0.7793 | 0.4294 | 0.7056 | 0.6223 | 0.6149 | 0.2765 | 0.0804 | 0.0174 | 223 | 26.27 |
| RT-DETR | 0.6978 | 0.2307 | 0.6414 | 0.5153 | 0.6621 | 0.1810 | 0.0943 | 0.0070 | 11305059 | 478.42 |
| PatchTST | 0.7054 | 0.2416 | 0.6352 | 0.5463 | 0.5639 | 0.1956 | 0.0937 | 0.0067 | 109507 | not measured |
| Uniform late | 0.7951 | 0.4457 | 0.7087 | 0.6331 | 0.6031 | 0.2913 | 0.0834 | 0.0355 | 11305282 | 504.69 |
| Learned static | 0.7950 | 0.4473 | 0.7117 | 0.6340 | 0.6110 | 0.2920 | 0.0784 | 0.0138 | 11305285 | 504.69 |
| Concatenation | 0.7856 | 0.4122 | 0.6999 | 0.6024 | 0.6385 | 0.2529 | 0.0827 | 0.0149 | 11490409 | not measured |
| Process gate | 0.7815 | 0.4437 | 0.7047 | 0.6268 | 0.6031 | 0.2827 | 0.0802 | 0.0128 | 11305720 | not measured |
| Quality gate | 0.7760 | 0.4445 | 0.7001 | 0.6206 | 0.6012 | 0.2747 | 0.0806 | 0.0126 | 11307256 | 564.04 |
| Process + quality | 0.7755 | 0.4414 | 0.7019 | 0.6384 | 0.5717 | 0.3012 | 0.0807 | 0.0124 | 11307448 | 564.02 |
| Modality dropout | 0.7754 | 0.4377 | 0.6981 | 0.6310 | 0.5737 | 0.2903 | 0.0809 | 0.0130 | 11307448 | 564.02 |
| AST | not run | not run | not run | not run | not run | not run | not run | not run | not measured | not measured |
| Tri-modal fusion | not run | not run | not run | not run | not run | not run | not run | not run | not measured | not measured |

Full clustered intervals, source keys and comparability status: `runs/reassemble/20260927T204649Z-final-synthesis/tables/01_master_clean_metrics.csv`. Latency entries are warm sequential component sums; missing entries were not remeasured.

## H. Section 3

No family/gate pair met both the predeclared weight-adaptation and smaller-degradation criteria at its highest severity. Absolute high-severity AP superiority over F2 was supported for none of these family/gate pairs. These are separate claims and marginal exploratory intervals; no universal reliability-awareness claim follows.

Corruptions were fixed before outcomes: native-pixel Gaussian noise (0.02/0.05/0.10), blur sigma 1/2/4, frame dropout 2/5/8 of 16; raw sensor Gaussian noise (0.10/0.50/1.00 training-channel SD), channel dropout 2/7/11 of 22, temporal block dropout 10/30/50%, six force/torque channels stuck at training medians, and complete single-modality loss. Sensor features and the same quality measures were recomputed from perturbed raw signals; models and clean thresholds stayed frozen. Static and masked gates return the remaining branch under total loss, using its frozen threshold. Unavailable unimodal models abstain. No combined corruption matrix was needed.

| Family | Gate | Class | Spearman | Weight shift [95%] | Absolute AP superiority |
| --- | --- | --- | --- | --- | --- |
| V1 | F5 | ROBUSTNESS-D | -0.083 | 0.2053 [0.1232, 0.2883] | False |
| V1 | F6 | ROBUSTNESS-D | 0.130 | 0.2246 [0.1604, 0.2897] | False |
| V2 | F5 | ROBUSTNESS-C | 0.122 | 0.1096 [0.0760, 0.1432] | False |
| V2 | F6 | ROBUSTNESS-C | 0.097 | 0.0726 [0.0510, 0.0937] | False |
| V3 | F5 | ROBUSTNESS-C | 0.066 | 0.0491 [0.0394, 0.0594] | False |
| V3 | F6 | ROBUSTNESS-C | 0.105 | 0.0824 [0.0742, 0.0908] | False |
| S1 | F5 | ROBUSTNESS-D | 0.112 | 0.0721 [0.0601, 0.0838] | False |
| S1 | F6 | ROBUSTNESS-D | 0.133 | 0.0719 [0.0524, 0.0912] | False |
| S2 | F5 | ROBUSTNESS-B | -0.174 | -0.1703 [-0.1923, -0.1468] | False |
| S2 | F6 | ROBUSTNESS-B | -0.213 | -0.2867 [-0.3393, -0.2326] | False |
| S3 | F5 | ROBUSTNESS-B | -0.258 | -0.1172 [-0.1483, -0.0871] | False |
| S3 | F6 | ROBUSTNESS-B | -0.295 | -0.3024 [-0.3696, -0.2375] | False |

Every condition has absolute metrics, clean-relative deltas and paired difference-in-degradation intervals in the robustness tables. Smaller decline from a weaker clean starting point is not automatically better corrupted performance.

Primary robustness values below are AUROC / AUPRC; severity uses the preregistered condition IDs.

| Condition | Sensor | Visual | Uniform | Static | Quality gate | Process + quality |
| --- | --- | --- | --- | --- | --- | --- |
| clean | 0.7793 / 0.4294 | 0.6978 / 0.2307 | 0.7951 / 0.4457 | 0.7950 / 0.4473 | 0.7760 / 0.4445 | 0.7755 / 0.4414 |
| V1_0.1 | 0.7793 / 0.4294 | 0.5232 / 0.1165 | 0.7217 / 0.3885 | 0.7250 / 0.3963 | 0.5933 / 0.1288 | 0.5779 / 0.1275 |
| V2_4.0 | 0.7793 / 0.4294 | 0.5789 / 0.1501 | 0.7487 / 0.3476 | 0.7615 / 0.4099 | 0.7323 / 0.4061 | 0.7375 / 0.4179 |
| V3_0.5 | 0.7793 / 0.4294 | 0.6884 / 0.2193 | 0.7939 / 0.4411 | 0.7960 / 0.4455 | 0.7735 / 0.4392 | 0.7725 / 0.4381 |
| S1_1.0 | 0.5882 / 0.1637 | 0.6978 / 0.2307 | 0.6289 / 0.2236 | 0.6153 / 0.2222 | 0.6001 / 0.1753 | 0.6038 / 0.1788 |
| S2_0.5 | 0.6976 / 0.2839 | 0.6978 / 0.2307 | 0.7468 / 0.3246 | 0.7374 / 0.3198 | 0.7326 / 0.3183 | 0.7295 / 0.3014 |
| S3_0.5 | 0.7276 / 0.3165 | 0.6978 / 0.2307 | 0.7636 / 0.3631 | 0.7547 / 0.3490 | 0.7513 / 0.3543 | 0.7316 / 0.3267 |
| S4 | 0.7408 / 0.4185 | 0.6978 / 0.2307 | 0.7728 / 0.4398 | 0.7694 / 0.4396 | 0.7417 / 0.4230 | 0.7385 / 0.4211 |
| V4 | 0.7793 / 0.4294 | unavailable | 0.7793 / 0.4294 | 0.7793 / 0.4294 | 0.7793 / 0.4294 | 0.7793 / 0.4294 |
| S5 | unavailable | 0.6978 / 0.2307 | 0.6978 / 0.2307 | 0.6978 / 0.2307 | 0.6978 / 0.2307 | 0.6978 / 0.2307 |

Paired AP effects at highest severity distinguish absolute performance from change relative to each model’s clean score.

| Family | Gate | Absolute AP difference vs F2 [95%] | AP degradation advantage vs F2 [95%] |
| --- | --- | --- | --- |
| V1 | F5 | -0.2675 [-0.3142, -0.2227] | -0.2647 [-0.3093, -0.2221] |
| V1 | F6 | -0.2688 [-0.3139, -0.2246] | -0.2628 [-0.3062, -0.2203] |
| V2 | F5 | -0.0038 [-0.0352, 0.0223] | -0.0011 [-0.0289, 0.0241] |
| V2 | F6 | 0.0080 [-0.0235, 0.0355] | 0.0139 [-0.0111, 0.0363] |
| V3 | F5 | -0.0063 [-0.0272, 0.0133] | -0.0036 [-0.0106, 0.0038] |
| V3 | F6 | -0.0074 [-0.0270, 0.0118] | -0.0015 [-0.0092, 0.0060] |
| S1 | F5 | -0.0469 [-0.0705, -0.0207] | -0.0442 [-0.0701, -0.0174] |
| S1 | F6 | -0.0434 [-0.0672, -0.0174] | -0.0374 [-0.0622, -0.0103] |
| S2 | F5 | -0.0015 [-0.0204, 0.0173] | 0.0013 [-0.0247, 0.0287] |
| S2 | F6 | -0.0184 [-0.0410, 0.0044] | -0.0125 [-0.0395, 0.0159] |
| S3 | F5 | 0.0054 [-0.0142, 0.0258] | 0.0081 [-0.0158, 0.0350] |
| S3 | F6 | -0.0223 [-0.0535, 0.0091] | -0.0163 [-0.0493, 0.0189] |


## I. Modality dropout

Modality dropout changed clean AP by -0.0037 [-0.0085, 0.0003] versus ordinary F6. Under complete visual or sensor loss, predictions are exactly the surviving frozen branch for both variants; missing-condition improvement is structurally impossible for this masked scalar-logit gate. At marginal paired 95% intervals, degraded AP improved for S2_0.3 and worsened for V1_0.05; remaining comparisons were unresolved. Training used one F6 variant with probabilities .15 visual missing/.15 sensor missing/.70 both available, never both absent; three seeds and frozen Section 2 selected head settings. No corruption-based tuning.

| Condition | AP | AP difference vs ordinary F6 [95%] |
| --- | --- | --- |
| clean | 0.4377 | -0.0037 [-0.0085, 0.0003] |
| V4 | 0.4294 | 0.0000 [0.0000, 0.0000] |
| S5 | 0.2307 | 0.0000 [0.0000, 0.0000] |
| V1_0.02 | 0.1790 | -0.0023 [-0.0081, 0.0037] |
| V1_0.05 | 0.1351 | -0.0058 [-0.0101, -0.0020] |
| V1_0.1 | 0.1274 | -0.0001 [-0.0035, 0.0050] |
| S1_0.1 | 0.3969 | 0.0008 [-0.0027, 0.0046] |
| S1_0.5 | 0.2739 | -0.0021 [-0.0079, 0.0038] |
| S1_1.0 | 0.1803 | 0.0015 [-0.0025, 0.0060] |
| V2_2.0 | 0.4334 | -0.0039 [-0.0132, 0.0050] |
| S2_0.3 | 0.3511 | 0.0246 [0.0063, 0.0428] |


## J. Audio

**AUDIO NOT INCLUDED — SEGMENT-ALIGNMENT OR COVERAGE PRECONDITION FAILED**. Segment-level, not frame-perfect, timing was required. Nominal origin is inferred from a non-audio clock and lacks an independently verified audio offset/drift or segment anchor. Header attributes, timestamps, nominal overlap, durations and prior actual decoding were audited. No AST/tri-modal/audio-noise model was warranted; this says nothing about audio’s possible predictive information.

| Stream | Nominal valid % | Failure valid % | Nominal recordings | Verified intervals |
| --- | --- | --- | --- | --- |
| hama1_audio | 97.31 | 96.46 | 148 | 0 |
| hama2_audio | 96.20 | 95.48 | 148 | 0 |
| hand_audio | 100.00 | 100.00 | 148 | 0 |


## K. Efficiency

Warm measurements used Tesla T4 and 4 CPU threads. warm VM measurements on 3 deterministic segments from distinct recordings; raw sensor arrays already in RAM; video decoding from existing cache measured separately; sequential component sums are estimates, not measured production end-to-end latency. Peak GPU allocated: 1351.2 MiB. Total parameters include the frozen backbone; trainable means parameters fitted somewhere in the retained pipeline. Source-checkpoint bytes can include unused detector components.

| Model | Total params | Trainable params | Checkpoint MiB | Component-sum ms | Cached fusion µs |
| --- | --- | --- | --- | --- | --- |
| U1 | 223 | 223 | 0.039 | 26.267 | 0.000 |
| U2 | 11305059 | 114947 | 77.607 | 478.415 | 0.000 |
| F1 | 11305282 | 115170 | 77.646 | 504.688 | 6.038 |
| F2 | 11305285 | 115173 | 77.646 | 504.693 | 11.030 |
| F5 | 11307256 | 117144 | 77.664 | 564.038 | 298.180 |
| F6 | 11307448 | 117336 | 77.663 | 564.021 | 281.787 |
| D6 | 11307448 | 117336 | 77.664 | 564.016 | 276.533 |

Static/gated late fusion supports independent branch updates without joint backbone training, but interface/calibration changes require training-only fusion revalidation. Interpret weights with probability calibration, action context and corruption response, not as causal explanations. No new test-fitted calibrator was used.

Static fusion coefficients act on calibrated failure probabilities before a logistic link; they are not convex allocation weights.

| Outer fold | Visual coefficient | Sensor coefficient | Intercept |
| --- | --- | --- | --- |
| 0 | 3.1142870718353524 | 6.555473656516644 | -3.462645774559234 |
| 1 | 3.099190073698223 | 6.709429737842258 | -3.449530736808982 |
| 2 | 3.414462142641008 | 6.630402833796571 | -3.4277562284296486 |
| 3 | 4.06349876142734 | 6.574018335159987 | -3.5504153440098536 |
| 4 | 3.730206293325205 | 6.217766052642035 | -3.565643545773553 |

Clean F2 minus U1 Brier: -0.0020 [-0.0031, -0.0009]; ECE: -0.0036 [-0.0127, 0.0099]. Lower is better for both; these paired intervals quantify the calibration trade-off without test-fitted recalibration.

## L. Generalization stress test

**NOT RUN — GATE FAILED**. Object annotations are categories/targets without verified physical-instance identity. Shared object categories connect recordings; a stress test preserving both recording and object disjointness lacks validated independent groups. Do not substitute a category label for physical object identity. Annotation categories: 17; recording/object connected components: 1. This is a completed feasibility decision, not a postponed core experiment.

## M. SQ1

Frozen RT-DETR contributes incremental information, although sensor statistics are stronger alone. The tested PatchTST is inferior to the statistical representation. Audio was excluded by the segment-alignment gate; audio predictive utility was not tested.

## N. SQ2

Simple learned late fusion captures useful visual/sensor complementarity. No tested adaptive gate improves clean AUPRC beyond F2, and all three have lower clean AUROC with paired intervals below zero. This does not establish equivalence or rule out every untested gate.

## O. SQ3

No family/gate pair met both the predeclared weight-adaptation and smaller-degradation criteria at its highest severity. Absolute high-severity AP superiority over F2 was supported for none of these family/gate pairs. These are separate claims and marginal exploratory intervals; no universal reliability-awareness claim follows. Complete modality loss yields explicit fallback, not recovery of missing information. Modality dropout changed clean AP by -0.0037 [-0.0085, 0.0003] versus ordinary F6. Under complete visual or sensor loss, predictions are exactly the surviving frozen branch for both variants; missing-condition improvement is structurally impossible for this masked scalar-logit gate. At marginal paired 95% intervals, degraded AP improved for S2_0.3 and worsened for V1_0.05; remaining comparisons were unresolved.

## P. SQ4

Clean F2 minus U1 Brier: -0.0020 [-0.0031, -0.0009]; ECE: -0.0036 [-0.0127, 0.0099]. Lower is better for both; these paired intervals quantify the calibration trade-off without test-fitted recalibration. Static fusion offers a small, modular fusion layer with calibrated branch interfaces. Gate weights expose allocation but are not causal explanations. Frozen visual extraction dominates computational cost; warm VM timings and synthetic degradation limit deployment claims. Replacing a branch requires revalidation of score calibration and fusion, even without joint backbone retraining.

## Q. Main RQ

Fusion is warranted when independently evaluated modalities provide complementary task information. In REASSEMBLE, simple calibrated late fusion captures this benefit; greater representation or gate complexity does not automatically help. Robustness must be judged jointly by induced allocation response, absolute degraded performance and change from clean performance, not by weight movement alone. No family/gate pair met both the predeclared weight-adaptation and smaller-degradation criteria at its highest severity. Absolute high-severity AP superiority over F2 was supported for none of these family/gate pairs. These are separate claims and marginal exploratory intervals; no universal reliability-awareness claim follows.

## R. Negative findings

The tested PatchTST loses to engineered statistics; RT-DETR is weaker alone than statistics; the initial standalone neural AUROC gates were unresolved; concatenation and gating did not justify clean complexity; context sensitivity did not establish clean benefit; audio timing failed its gate; physical-object OOD identity/support was insufficient; modality dropout cannot change exact one-branch fallback in this architecture. Negative robustness family results are retained without architecture rescue.

## S. Failed hypotheses

“A temporal Transformer should beat simple sensor statistics” was falsified for this tested implementation/budget. “Process/quality gating should improve clean fusion” was unsupported and contradicted by the AUROC comparison. “Modality dropout can improve a masked scalar gate when only one frozen branch remains” is ruled out by the architecture and checked empirically. Reliability-aware robustness remains family-specific according to Section 3, not presumed from the exposé.

## T. Corrections

Section 1B’s one-thread BLAS attempt failed exact probability reproduction; restoring original 16-thread execution passed without changing scientific settings. Section 2’s automatic AP-only gate shortlist was corrected during documented final review using uncertainty, stability and cost. Section 3 serial extractors were interrupted only for recording-level parallelism; completed checkpoints were hash-verified and retained. Corruption formulas, seeds, batch size and parity tolerances were unchanged. Expected all-NaN-channel statistic warnings under deliberate dropout are counted, not treated as raw corruption or silently fixed. Detailed corrections are retained in each run.

## U. Limitations

Outcome-informed sensor selection and the same outer folds reused sequentially make this adaptive exploratory work. Recording clustering does not remove shared scene/day/object confounding or all training uncertainty. Labels concern execution success/failure, not physical damage; segment classification is retrospective, not online early warning. Artificial corruptions and one seeded realization per severity do not represent every field fault. Marginal multiple-family intervals do not establish universal robustness. Audio lacks verified segment timing. No validated unseen-object/site generalization claim is available. Missingness fallback does not recover absent information. VM component timing is not production latency. PHM targets are provisional; its metric scales are task-specific.

## V. Exact safe thesis claims

“On the evaluated REASSEMBLE cohort, engineered sensor statistics outperformed the tested PatchTST representation.”

“Frozen visual features provided incremental information beyond the statistical-sensor model in the tested nested static fusion procedure.”

“The tested adaptive gates did not establish a clean AUPRC improvement over learned static late fusion and had lower clean AUROC.”

“Gate-weight changes were evaluated separately from predictive changes under predeclared synthetic degradation.”

“No family/gate pair met both the predeclared weight-adaptation and smaller-degradation criteria at its highest severity. Absolute high-severity AP superiority over F2 was supported for none of these family/gate pairs. These are separate claims and marginal exploratory intervals; no universal reliability-awareness claim follows.”

“Complete single-modality loss reduced the tested fusion rules to their surviving calibrated branch.”

“Audio was excluded because trustworthy segment-level clock association was not established; its predictive value was not evaluated.”

“These results are an adaptive exploratory assessment on the same cohort, not independent confirmation.”

## W. Claims that would be overstatements

Do not write: “Transformers are unsuitable for sensor anomaly detection”; “The gate is universally reliability-aware”; “Adaptive fusion is robust in deployment”; “Audio contains no useful information”; “The models generalize to unseen physical objects”; “The method provides real-time early warnings”; “MAE in PHM is directly comparable to AUPRC in REASSEMBLE”; or “The oracle is deployable.” Each exceeds the evaluated target, comparison, timing or generalization evidence.

## X. Thesis figures

| Figure | PDF path | Caption / supported claim |
| --- | --- | --- |
| 01_two_study_design | runs/reassemble/20260927T204649Z-final-synthesis/figures/01_two_study_design.pdf | Two task-specific studies investigate conditions for meaningful fusion; metric scales are not directly comparable. |
| 02_cohort | runs/reassemble/20260927T204649Z-final-synthesis/figures/02_cohort.pdf | Action and outcome support in the frozen primary cohort; segments are clustered within recordings. |
| 03_unimodal | runs/reassemble/20260927T204649Z-final-synthesis/figures/03_unimodal.pdf | Unimodal discrimination with recording-clustered 95% intervals. Statistical sensors outperform the tested PatchTST; this is not a universal Transformer claim. |
| 04_complementarity | runs/reassemble/20260927T204649Z-final-synthesis/figures/04_complementarity.pdf | Frozen OOF correctness overlap. Visual-only correct failures number 97 across 61 recordings. The oracle is diagnostic, not deployable. |
| 05_clean_fusion | runs/reassemble/20260927T204649Z-final-synthesis/figures/05_clean_fusion.pdf | Clean fusion comparison. No adaptive gate establishes incremental value over F2; intervals condition on fitted models. |
| 06_weights_by_action | runs/reassemble/20260927T204649Z-final-synthesis/figures/06_weights_by_action.pdf | Clean modality allocation varies by action; allocation differences do not establish causal process value. |
| 07_visual_corruptions | runs/reassemble/20260927T204649Z-final-synthesis/figures/07_visual_corruptions.pdf | Clean-trained model AUPRC under single-modality degradation. Shading shows marginal recording-cluster 95% intervals; one deterministic corruption realization per condition. |
| 08_sensor_corruptions | runs/reassemble/20260927T204649Z-final-synthesis/figures/08_sensor_corruptions.pdf | Clean-trained model AUPRC under single-modality degradation. Shading shows marginal recording-cluster 95% intervals; one deterministic corruption realization per condition. |
| 09_missing_modalities | runs/reassemble/20260927T204649Z-final-synthesis/figures/09_missing_modalities.pdf | All fusion models fall back to the remaining branch. Unavailable unimodal models abstain and have no metric bar. |
| 10_gate_response | runs/reassemble/20260927T204649Z-final-synthesis/figures/10_gate_response.pdf | Measured gate response, without forced monotonicity. Lower degraded-modality weight alone is insufficient to establish predictive robustness. |
| 11_dropout_tradeoff | runs/reassemble/20260927T204649Z-final-synthesis/figures/11_dropout_tradeoff.pdf | Clean and degraded performance trade-off from one preregistered modality-dropout variant. Exact zero under complete modality loss follows from the architecture. |
| 12_efficiency | runs/reassemble/20260927T204649Z-final-synthesis/figures/12_efficiency.pdf | Task-specific accuracy/cost trade-off. Latency is a sum of measured warm components on this VM, not production end-to-end timing. |
| 13_audio_gate | runs/reassemble/20260927T204649Z-final-synthesis/figures/13_audio_gate.pdf | Nominal overlap is distinct from trustworthy segment alignment. Audio modelling was excluded by the timing gate, not by a negative predictive result. |
| 14_cross_study_conditions | runs/reassemble/20260927T204649Z-final-synthesis/figures/14_cross_study_conditions.pdf | Cross-study synthesis: establish modality informativeness and complementarity before architectural complexity; flat low-signal degradation is not robustness. |


## Y. Thesis tables

All final tables are in `runs/reassemble/20260927T204649Z-final-synthesis/tables`. Master clean metrics include uncertainty/source keys; corruption tables separate absolute and relative performance; missingness, gate response, dropout, audio, efficiency and RQ tables preserve their different scopes. See THESIS_TABLE_INDEX.md for exact paths and purposes.

## Z. Provenance

Frozen evidence commits: Section 1 `08d498d`; Section 1B `4089b02`; Section 2 `d16c251`. Corruption preregistration `280b842`; sensor path `2883149`; runtime-only parallelism `6f9ea67`; downstream implementation `8917cdd`; synthetic dropout checkpoint test `0f03f54`. Configurations: `configs/reassemble/completion.json`, `section3_corruptions.json`, and unchanged Section 1/1B/2 configs. Unique phase paths:

| Phase | Run |
| --- | --- |
| completion-preflight | runs/reassemble/20260927T204649Z-completion-preflight |
| section3 | runs/reassemble/20260927T204649Z-section3 |
| modality-dropout | runs/reassemble/20260927T204649Z-modality-dropout |
| audio-gate | runs/reassemble/20260927T204649Z-audio-gate |
| efficiency | runs/reassemble/20260927T204649Z-efficiency |
| object-feasibility | runs/reassemble/20260927T204649Z-object-feasibility |
| final-synthesis | runs/reassemble/20260927T204649Z-final-synthesis |

Machine-readable result sources:

- `runs/reassemble/20260927T154732Z-section1/assessment/results.json`
- `runs/reassemble/20260927T175336Z-section1b/assessment/results.json`
- `runs/reassemble/20260927T192852Z-section2/assessment/results.json`
- `runs/reassemble/20260927T204649Z-section3/results.json`
- `runs/reassemble/20260927T204649Z-modality-dropout/results.json`
- `runs/reassemble/20260927T204649Z-efficiency/results.json`
- `runs/reassemble/20260927T204649Z-audio-gate/results.json`

Final validation/output manifests record current implementation hashes, tests, preserved-file checks, raw metadata, package versions and claim audit. Numerical intermediate caches remain local and ignored. No external master Reasoning Record was modified. Recent commits:

```text
338ad8e Keep thesis model labels readable in comparison figures
82a712b Include primary robustness values and paired intervals in self-contained handoff
ecd5182 Document exact autonomous resume and final review procedure
c4ec844 Specify exact source tables for every thesis figure
4c15d68 Audit recovered sensor training identities and complete narrative checkpoint
0f03f54 Verify modality-dropout fitting and checkpoint resumption on synthetic data
e0be4ad Record completion phase configuration snapshots and validation history
b126f99 Report both clean and degraded modality-dropout tradeoffs
```
