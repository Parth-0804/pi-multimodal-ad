# SECTION 1B — Fusion admissibility handoff

## 1. Why PatchTST was not tuned further

Section1 is frozen. Its tested PatchTST was significantly worse than engineered sensor statistics. The researcher explicitly excluded longer training or another architecture search; this remains a bounded SQ1 negative result, not a claim that all temporal Transformers lack value.

## 2. Why statistical sensors were selected

This was the strongest Section1 sensor model (AUROC0.7793, AP0.4294). Its frozen per-channel statistics, logistic architecture, training-only scaling, C grid[0.1,1,10], four-inner-fold mean-AP selection, calibration and thresholds were reused. RT-DETR uses its existing frozen representations and the original5/10-epoch head budgets. No backbone fine-tuning or feature re-extraction occurred.

## 3. Statistical-sensor permutation result

Same19 circular shifts within recording/action, same seeds, outer/inner folds and complete branch procedure as Section1. Nulls retain recording/action prevalence and require conditional cyclic exchangeability. Monte Carlo resolution is0.05; no universal IID-chance interpretation. Both null metrics and changed-label counts follow.

| Run | AUROC | AUPRC | changed labels |
| --- | --- | --- | --- |
| observed | 0.7793 | 0.4294 | 0 |
| 1 | 0.6293 | 0.1576 | 794 |
| 2 | 0.6386 | 0.1693 | 784 |
| 3 | 0.6214 | 0.1596 | 786 |
| 4 | 0.6294 | 0.1671 | 812 |
| 5 | 0.6129 | 0.1632 | 792 |
| 6 | 0.6315 | 0.1695 | 744 |
| 7 | 0.6112 | 0.1617 | 780 |
| 8 | 0.6308 | 0.1677 | 762 |
| 9 | 0.6249 | 0.1573 | 774 |
| 10 | 0.6213 | 0.1647 | 738 |
| 11 | 0.6056 | 0.1502 | 774 |
| 12 | 0.6014 | 0.1521 | 772 |
| 13 | 0.6414 | 0.1742 | 766 |
| 14 | 0.6251 | 0.1608 | 804 |
| 15 | 0.6344 | 0.1592 | 802 |
| 16 | 0.6693 | 0.1915 | 796 |
| 17 | 0.6238 | 0.1660 | 784 |
| 18 | 0.6327 | 0.1710 | 778 |
| 19 | 0.6128 | 0.1540 | 788 |

Plus-one p-values: AUROC **0.05**, AP **0.05**. Numerical reproduction and identical selected C are recorded in sensor_reproduction.json; original BLAS threading is restored after the one-thread reproduction failed its strict parity guard; the failed attempt is retained.

## 4. RT-DETR/statistical-sensor complementarity

Original recording-disjoint OOF scores and original training-selected hard decisions, unmodified. Correlations are Pearson; error correlation uses binary errors. Different branch thresholds affect correctness overlap.

| Subset | N | score r | error r | both correct | both wrong | visual only | sensor only | oracle correct | oracle rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 4530 | 0.3130 | 0.1627 | 2347 | 529 | 486 | 1168 | 4001 | 0.8832 |

## 5. Failure-only complementarity

| Subset | N | score r | error r | both correct | both wrong | visual only | sensor only | oracle correct | oracle rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| failures | 509 | 0.2527 | 0.2797 | 240 | 99 | 97 | 73 | 410 | 0.8055 |

Visual rescues of sensor-missed failures occur in **61 recordings**. Rescue fraction among all failures: **0.1906 [0.1542, 0.2285]**. The failure-only oracle rate is oracle recall. It uses the true outcome to choose the right model, so it is not deployable and does not establish attainable fusion benefit.

## 6. Per-action complementarity

| Subset | N | score r | error r | both correct | both wrong | visual only | sensor only | oracle correct | oracle rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pick | 1190 | 0.1473 | 0.0950 | 591 | 132 | 166 | 301 | 1058 | 0.8891 |
| insert | 1156 | 0.2115 | 0.1110 | 392 | 217 | 121 | 426 | 939 | 0.8123 |
| remove | 1096 | 0.1411 | 0.0766 | 458 | 150 | 139 | 349 | 946 | 0.8631 |
| place | 1088 | 0.3517 | 0.2105 | 906 | 30 | 60 | 92 | 1058 | 0.9724 |

Failure-only within each action:

| Subset | N | score r | error r | both correct | both wrong | visual only | sensor only | oracle correct | oracle rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pick_failures | 98 | 0.1118 | 0.0926 | 22 | 32 | 22 | 22 | 66 | 0.6735 |
| insert_failures | 243 | 0.1902 | 0.3241 | 142 | 34 | 43 | 24 | 209 | 0.8601 |
| remove_failures | 146 | 0.0913 | 0.1874 | 68 | 24 | 29 | 25 | 122 | 0.8356 |
| place_failures | 22 | 0.3609 | 0.5477 | 8 | 9 | 3 | 2 | 13 | 0.5909 |

## 7. Minimal late-fusion result

Exactly one static L2 logistic stacker (C1, unweighted, lbfgs, max_iter2000) on two calibrated probabilities. No adaptive/quality gate. Every outer-training meta-row is predicted by branch models whose selection, calibration and scaling exclude that row's inner assessment recording. Four sub-inner recording folds implement each inner-training branch procedure. Final branches are refitted on the original outer training data using the exact Section1 procedure; their predictions must numerically match the frozen branch evidence.

The fixed stacker fits only outer-training inner-OOF probabilities. Its decision threshold uses meta-cross-fitted training predictions, balanced accuracy, grid0.01..0.99 and ties nearest0.5. No extra calibrator or stacker hyperparameter search. These threshold scores condition on the branch OOF matrix and are not claimed unbiased inner performance estimates. No outer-test OOF score was used to fit fusion.

| Model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sensor_statistics | 0.7793 [0.7549, 0.8040] | 0.4294 [0.3801, 0.4828] | 0.7056 [0.6830, 0.7286] | 0.6223 [0.6066, 0.6393] | 0.6149 [0.5661, 0.6622] | 0.2765 [0.2522, 0.3032] | 0.0804 [0.0735, 0.0879] | 0.0174 [0.0127, 0.0274] |
| rtdetr | 0.6978 [0.6716, 0.7232] | 0.2307 [0.1983, 0.2701] | 0.6414 [0.6175, 0.6658] | 0.5153 [0.4956, 0.5355] | 0.6621 [0.6149, 0.7075] | 0.1810 [0.1617, 0.2013] | 0.0943 [0.0862, 0.1028] | 0.0070 [0.0057, 0.0184] |
| minimal_late_fusion | 0.7950 [0.7727, 0.8178] | 0.4473 [0.3968, 0.5019] | 0.7117 [0.6875, 0.7343] | 0.6340 [0.6161, 0.6527] | 0.6110 [0.5603, 0.6582] | 0.2920 [0.2640, 0.3225] | 0.0784 [0.0713, 0.0858] | 0.0138 [0.0118, 0.0251] |

## 8. Paired uncertainty and coherence

2,000 paired recording-cluster percentile bootstrap replicates; intervals condition on fitted models. Differences are fusion minus statistical sensors; lower Brier/ECE is better.

| Metric | Difference [95% interval] |
| --- | --- |
| AUROC | 0.0156 [0.0060, 0.0255] |
| AUPRC | 0.0179 [0.0086, 0.0283] |
| balanced_accuracy | 0.0061 [-0.0054, 0.0165] |
| macro_F1 | 0.0117 [0.0026, 0.0201] |
| failure_recall | -0.0039 [-0.0255, 0.0163] |
| failure_precision | 0.0155 [0.0039, 0.0265] |
| Brier | -0.0020 [-0.0031, -0.0009] |
| ECE | -0.0036 [-0.0127, 0.0099] |

| Outer fold | N | failures | AUROC difference | AP difference |
| --- | --- | --- | --- | --- |
| 0 | 753 | 77 | 0.0207 | 0.0395 |
| 1 | 964 | 109 | 0.0117 | 0.0146 |
| 2 | 1037 | 125 | 0.0244 | 0.0113 |
| 3 | 906 | 99 | 0.0029 | -0.0047 |
| 4 | 870 | 99 | 0.0200 | 0.0364 |

| Omitted outer fold | Pooled AUROC difference | Pooled AP difference |
| --- | --- | --- |
| 0 | 0.0144 | 0.0147 |
| 1 | 0.0168 | 0.0192 |
| 2 | 0.0142 | 0.0168 |
| 3 | 0.0186 | 0.0248 |
| 4 | 0.0145 | 0.0144 |

The rule was frozen before Section1B outcomes: AP gain>=0.01 with lower95%>0, >=3 positive outer-fold AP differences, all leave-one-fold-out AP differences>0, AUROC lower95%>-0.01, positive failure complementarity across>=5 recordings, and sensor conditional permutation AP p<=0.05. The old standalone RT-DETR intersection-union gate is not used.

| Requirement | Satisfied |
| --- | --- |
| positive_failure_complementarity | True |
| meaningful_AP_gain_with_positive_interval | True |
| coherent_fold_evidence | True |
| AUROC_noninferiority_supported | True |
| sensor_permutation_pass | True |

## 9. Allowed claims

Complementarity describes the frozen predictions on this cohort. The paired results quantify the incremental performance of this one predeclared stacker over the selected sensor model. The permutation result addresses the specified conditional null only. Any positive decision supports a bounded next-phase comparison, not a claim that complex gating is needed.

## 10. Claims not supported

No optimal architecture, adaptive gating, corruption robustness, audio benefit, causal diagnosis, online warning, unseen-site/object generalization or deployable oracle. This follow-up hypothesis and sensor choice were informed by Section1 results on the same folds: it is an adaptive exploratory assessment, not independent confirmatory evidence. Nested refitting prevents training leakage but does not erase that prior outcome-informed study choice. No new held-out dataset was added.

## 11. Exact recommendation for Section2

After researcher review, authorize a bounded clean fusion comparison using frozen RT-DETR and statistical-sensor branches, with this stacker and the strong sensor baseline retained. Do not substitute PatchTST without a separately authorized rationale. Gate complexity must demonstrate added value over static fusion. This run does not itself authorize Section2.

## 12. Artifact paths, configs and commits

Run: `runs/reassemble/20260927T175336Z-section1b`. Frozen config: `configs/reassemble/section1b.json`; protocol: `docs/reassemble/SECTION_1B_PROTOCOL.md`; live/final IDE handoff: `docs/reassemble/SECTION_1B_CONTINUATION.md`. Section1 evidence commit08d498d; branch implementation852a123. Current implementation commit/source hashes: implementation.json. Protocol/config/source identities: provenance.json. All metrics, controls and complementarity: assessment/results.json. Subfold memberships, coefficients, thresholds, branch parity and inner probabilities: stacking/. Sensor null predictions and selections: sensor_controls/predictions/. Input feature/OOF identities remain in the unchanged Section1 final_output_manifest.json. New final validation and output identities are recorded separately in this run.

## 13. Failed attempts and corrections

See failures_and_corrections.md and validation.json for executed checks and any exceptions. No failed attempt is erased or used to alter the decision rule. Section1 remains unchanged; this follow-up replaces neither its results nor its original gate.

FUSION GO
