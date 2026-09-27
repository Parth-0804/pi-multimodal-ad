# SECTION 2 — Clean fusion handoff

**A. SIMPLE FUSION SUFFICIENT**

## A. Scientific question

Given demonstrated visual/sensor complementarity, which small fusion strategy exploits it, and does process/quality gating add value beyond learned static fusion? This is an **adaptive exploratory study**: Sections 1 and 1B informed this design using these same folds. No new untouched dataset exists. Nested fitting prevents training leakage, not study-selection bias.

## B. Evidence entering Section 2

Section 1B returned FUSION GO: sensor AUROC/AUPRC 0.7793/0.4294 increased to 0.7950/0.4473 with static logistic stacking; paired gains were 0.0156 [0.0060, 0.0255] and 0.0179 [0.0086, 0.0283]. RT-DETR rescued 97 sensor-missed failures across 61 recordings. The sensor conditional permutation p-value was 0.05 for both metrics (19 nulls). The old standalone visual intersection-union gate was not required. Section 1 and 1B remain frozen.

## C. Why PatchTST was not the primary sensor branch

The tested PatchTST achieved about AUROC 0.7054 / AUPRC 0.2416, substantially below statistical sensors (0.7793/0.4294), with paired evidence favoring statistics. It remains the bounded SQ1 negative result for the tested temporal Transformer. No further epochs, tuning or substitution occurred; this says nothing universal about all temporal Transformers.

## D. Why decision-level gating was adopted

The selected sensor model is logistic regression on engineered statistics. Inventing a deep sensor embedding for the primary gate would change that validated model. Decision-level gating instead preserves both calibrated branch models, modularity and interpretable modality allocation. This is a scientifically justified architecture adaptation. F3 explicitly tests feature concatenation as a separate comparator.

## E. Evaluation protocol

Exactly 4,530 segments, 509 failures and 148 recordings; original five outer and four inner recording-disjoint folds, labels and grouping. No outer-test prediction or label fits any fusion parameter. F2 and final branch probabilities are reused from Section 1B. For gate hyperparameter assessment, strictly nested branch-training predictions use its saved four subfolds; at the additional depth selection uses the remaining three subfolds, with no regenerated partition. See the frozen protocol for this training-only depth. Every quality/scaling estimate uses the fitting subset. Primary metrics are AUROC and average precision (reported as AUPRC); ECE uses the original 15 equal-width probability bins. The 2,000 paired recording-cluster bootstrap replicates condition on fitted models, and seeds are not independent observations. Thresholds maximize inner-OOF balanced accuracy on 0.01–0.99, tie nearest 0.5; these threshold-training scores are not independent performance estimates.

## F. Architecture definitions

| ID | Architecture |
| --- | --- |
| U1 | Frozen 220 statistical features → standardized balanced logistic model; frozen C selection/calibration |
| U2 | Frozen RT-DETR backbone features → frozen fold-specific 128-dimensional head → calibrated probability |
| F1 | 0.5 × calibrated visual probability + 0.5 × calibrated sensor probability; training-only threshold |
| F2 | Exact Section 1B two-probability L2 logistic stacker, C=1; three scalar parameters |
| F3 | Frozen visual 128-vector + unchanged 220 statistics; separate 128 projections; LayerNorm; 256→32/64→1; trained fusion layers only |
| F4 | Action one-hot + availability → 8/16-unit MLP → masked softmax → weighted calibrated branch logits |
| F5 | Audited quality + availability → same small gate → weighted calibrated branch logits |
| F6 | Action + quality + availability → same small gate → weighted calibrated branch logits |

Gates have no context-to-classifier bypass, final bias or post-gate calibration. Three seed probabilities are averaged; reported weights average seed weights, so the ensemble probability is not exactly sigmoid of the mean-weight logit. All clean masks are [1,1]. Quality consists of six hand-camera measures and six measures for each of five sensor streams; no labels, IDs, annotation text or audio features. Quality may also reflect process/content. Constant quality fields: `hand.valid_frame_ratio, hand.decode_failure_ratio, measured_force.finite_fraction, measured_force.constant_channels, measured_force.missing_channels, measured_torque.finite_fraction, measured_torque.constant_channels, measured_torque.missing_channels, gripper_positions.finite_fraction, gripper_positions.missing_channels, joint_efforts.finite_fraction, joint_efforts.constant_channels, joint_efforts.missing_channels, joint_velocities.finite_fraction, joint_velocities.constant_channels, joint_velocities.missing_channels`.

## G. Hyperparameters and seeds

Config: `configs/reassemble/section2.json`. Exactly two predefined concatenation configurations and two gate configurations, shared across F4–F6; select by mean four-inner-fold AP of three-seed mean probabilities. Seeds: [20260927, 20260928, 20260929]. F3 candidates: `[{"hidden": 32, "epochs": 10, "lr": 0.001, "weight_decay": 0.001}, {"hidden": 64, "epochs": 20, "lr": 0.001, "weight_decay": 0.001}]`. Gate candidates: `[{"hidden": 8, "epochs": 40, "lr": 0.003, "weight_decay": 0.001}, {"hidden": 16, "epochs": 40, "lr": 0.003, "weight_decay": 0.001}]`. Batch size 128, AdamW, gradient norm 1; F3 dropout 0.1 and class-balanced BCE, gates unweighted BCE. F3 alone receives sigmoid calibration fitted to selected inner-OOF raw logits for each seed. Frozen branch epochs/C grids and 16 BLAS threads are unchanged. Final configuration selections and threshold values are in `assessment/selected_hyperparameters.json`.

| Model | Pooled AUROC by seed | Pooled AUPRC by seed | AP seed std |
| --- | --- | --- | --- |
| F3 | 0.7815, 0.7803, 0.7810 | 0.4068, 0.4094, 0.3951 | 0.0063 |
| F4 | 0.7813, 0.7815, 0.7817 | 0.4435, 0.4438, 0.4440 | 0.0002 |
| F5 | 0.7749, 0.7744, 0.7735 | 0.4382, 0.4397, 0.4449 | 0.0029 |
| F6 | 0.7740, 0.7718, 0.7758 | 0.4328, 0.4287, 0.4458 | 0.0073 |


## H. Clean results

| Model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1 statistical sensors | 0.7793 [0.7549, 0.8040] | 0.4294 [0.3801, 0.4828] | 0.7056 [0.6830, 0.7286] | 0.6223 [0.6066, 0.6393] | 0.6149 [0.5661, 0.6622] | 0.2765 [0.2522, 0.3032] | 0.0804 [0.0735, 0.0879] | 0.0174 [0.0127, 0.0274] |
| U2 RT-DETR | 0.6978 [0.6716, 0.7232] | 0.2307 [0.1983, 0.2701] | 0.6414 [0.6175, 0.6658] | 0.5153 [0.4956, 0.5355] | 0.6621 [0.6149, 0.7075] | 0.1810 [0.1617, 0.2013] | 0.0943 [0.0862, 0.1028] | 0.0070 [0.0057, 0.0184] |
| F1 uniform late | 0.7951 [0.7728, 0.8174] | 0.4457 [0.3949, 0.4989] | 0.7087 [0.6866, 0.7289] | 0.6331 [0.6149, 0.6517] | 0.6031 [0.5563, 0.6463] | 0.2913 [0.2624, 0.3231] | 0.0834 [0.0761, 0.0912] | 0.0355 [0.0267, 0.0448] |
| F2 learned static late | 0.7950 [0.7727, 0.8178] | 0.4473 [0.3968, 0.5019] | 0.7117 [0.6875, 0.7343] | 0.6340 [0.6161, 0.6527] | 0.6110 [0.5603, 0.6582] | 0.2920 [0.2640, 0.3225] | 0.0784 [0.0713, 0.0858] | 0.0138 [0.0118, 0.0251] |
| F3 feature concatenation | 0.7856 [0.7615, 0.8090] | 0.4122 [0.3593, 0.4672] | 0.6999 [0.6768, 0.7230] | 0.6024 [0.5834, 0.6221] | 0.6385 [0.5941, 0.6846] | 0.2529 [0.2249, 0.2820] | 0.0827 [0.0755, 0.0903] | 0.0149 [0.0117, 0.0261] |
| F4 process gate | 0.7815 [0.7571, 0.8063] | 0.4437 [0.3935, 0.4974] | 0.7047 [0.6805, 0.7289] | 0.6268 [0.6087, 0.6455] | 0.6031 [0.5523, 0.6526] | 0.2827 [0.2544, 0.3139] | 0.0802 [0.0731, 0.0878] | 0.0128 [0.0109, 0.0237] |
| F5 quality gate | 0.7760 [0.7511, 0.8003] | 0.4445 [0.3957, 0.4958] | 0.7001 [0.6755, 0.7235] | 0.6206 [0.6018, 0.6400] | 0.6012 [0.5508, 0.6498] | 0.2747 [0.2468, 0.3053] | 0.0806 [0.0733, 0.0882] | 0.0126 [0.0109, 0.0240] |
| F6 process + quality gate | 0.7755 [0.7514, 0.7989] | 0.4414 [0.3935, 0.4937] | 0.7019 [0.6778, 0.7254] | 0.6384 [0.6206, 0.6565] | 0.5717 [0.5201, 0.6241] | 0.3012 [0.2713, 0.3320] | 0.0807 [0.0734, 0.0883] | 0.0124 [0.0112, 0.0237] |


## I. Paired comparisons

Differences are first model minus reference; lower Brier/ECE is better. Marginal paired 95% intervals:

| Comparison | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1−U1 | 0.0157 [0.0030, 0.0289] | 0.0164 [-0.0005, 0.0333] | 0.0031 [-0.0118, 0.0163] | 0.0108 [-0.0018, 0.0234] | -0.0118 [-0.0435, 0.0180] | 0.0148 [-0.0015, 0.0317] | 0.0029 [0.0013, 0.0046] | 0.0181 [0.0050, 0.0263] |
| F2−U1 | 0.0156 [0.0060, 0.0255] | 0.0179 [0.0086, 0.0283] | 0.0061 [-0.0054, 0.0165] | 0.0117 [0.0026, 0.0201] | -0.0039 [-0.0255, 0.0163] | 0.0155 [0.0039, 0.0265] | -0.0020 [-0.0031, -0.0009] | -0.0036 [-0.0127, 0.0099] |
| F3−U1 | 0.0063 [-0.0166, 0.0295] | -0.0172 [-0.0573, 0.0230] | -0.0057 [-0.0291, 0.0171] | -0.0199 [-0.0379, -0.0022] | 0.0236 [-0.0225, 0.0713] | -0.0236 [-0.0442, -0.0032] | 0.0023 [-0.0005, 0.0052] | -0.0025 [-0.0109, 0.0087] |
| F4−F2 | -0.0135 [-0.0220, -0.0054] | -0.0036 [-0.0134, 0.0057] | -0.0070 [-0.0179, 0.0043] | -0.0072 [-0.0160, 0.0018] | -0.0079 [-0.0295, 0.0145] | -0.0093 [-0.0208, 0.0025] | 0.0017 [0.0005, 0.0030] | -0.0010 [-0.0099, 0.0069] |
| F5−F2 | -0.0190 [-0.0289, -0.0095] | -0.0027 [-0.0228, 0.0171] | -0.0116 [-0.0248, 0.0012] | -0.0134 [-0.0235, -0.0029] | -0.0098 [-0.0352, 0.0150] | -0.0173 [-0.0300, -0.0042] | 0.0022 [0.0006, 0.0039] | -0.0012 [-0.0107, 0.0079] |
| F6−F2 | -0.0194 [-0.0288, -0.0102] | -0.0059 [-0.0248, 0.0137] | -0.0098 [-0.0224, 0.0030] | 0.0044 [-0.0056, 0.0145] | -0.0393 [-0.0649, -0.0122] | 0.0092 [-0.0040, 0.0228] | 0.0023 [0.0007, 0.0039] | -0.0014 [-0.0102, 0.0074] |
| F6−U1 | -0.0038 [-0.0129, 0.0050] | 0.0120 [-0.0063, 0.0301] | -0.0037 [-0.0160, 0.0077] | 0.0161 [0.0053, 0.0260] | -0.0432 [-0.0662, -0.0211] | 0.0247 [0.0100, 0.0388] | 0.0003 [-0.0009, 0.0014] | -0.0050 [-0.0093, 0.0041] |

Adaptive claims additionally require the predeclared simultaneous Bonferroni percentile lower bound across three gates, AP gain ≥0.01, ≥3 positive folds, and AUROC lower 95% >−0.01. These exploratory criteria do not erase prior same-cohort selection.

| Gate vs F2 | Simultaneous AP lower | Checks |
| --- | --- | --- |
| F4 | -0.0151 | {"meaningful_AP_gain": false, "simultaneous_AP_lower_positive": false, "AUROC_noninferiority": false, "fold_coherence": false, "action_changes_weights": true} |
| F5 | -0.0265 | {"meaningful_AP_gain": false, "simultaneous_AP_lower_positive": false, "AUROC_noninferiority": false, "fold_coherence": false, "quality_changes_weights": true} |
| F6 | -0.0276 | {"meaningful_AP_gain": false, "simultaneous_AP_lower_positive": false, "AUROC_noninferiority": false, "fold_coherence": false, "action_changes_weights": true, "quality_changes_weights": true} |


## J. Fold-level consistency

| Model | Fold 0 AUROC/AP | Fold 1 | Fold 2 | Fold 3 | Fold 4 |
| --- | --- | --- | --- | --- | --- |
| U1 | 0.7237/0.3277 | 0.7967/0.4715 | 0.8089/0.4965 | 0.8084/0.4860 | 0.7451/0.3798 |
| U2 | 0.7265/0.2328 | 0.7193/0.2571 | 0.7286/0.2502 | 0.6689/0.1836 | 0.6693/0.2840 |
| F1 | 0.7481/0.3708 | 0.8064/0.4930 | 0.8376/0.5000 | 0.8053/0.4775 | 0.7630/0.4213 |
| F2 | 0.7444/0.3672 | 0.8084/0.4861 | 0.8333/0.5079 | 0.8113/0.4813 | 0.7651/0.4162 |
| F3 | 0.7819/0.3626 | 0.8327/0.5254 | 0.8067/0.4551 | 0.7773/0.3868 | 0.7435/0.4146 |
| F4 | 0.7294/0.3534 | 0.7980/0.4866 | 0.8111/0.5068 | 0.8042/0.4947 | 0.7506/0.3915 |
| F5 | 0.7279/0.3799 | 0.7945/0.4731 | 0.8024/0.5339 | 0.7880/0.4687 | 0.7513/0.3755 |
| F6 | 0.7256/0.3496 | 0.7916/0.4760 | 0.8011/0.5327 | 0.8001/0.4787 | 0.7461/0.3856 |


## K. Gate-weight behaviour

| Gate | Subset | Visual mean ± std | Sensor mean ± std | Entropy (nats) | Visual 5/25/50/75/95% |
| --- | --- | --- | --- | --- | --- |
| F4 | all | 0.1985 ± 0.1493 | 0.8015 ± 0.1493 | 0.4180 | 0.006, 0.059, 0.226, 0.334, 0.476 |
| F4 | pick | 0.3005 ± 0.0495 | 0.6995 ± 0.0495 | 0.6053 | 0.226, 0.291, 0.292, 0.334, 0.363 |
| F4 | insert | 0.0212 ± 0.0204 | 0.9788 ± 0.0204 | 0.0942 | 0.006, 0.009, 0.010, 0.016, 0.059 |
| F4 | remove | 0.1826 ± 0.1225 | 0.8174 ± 0.1225 | 0.4250 | 0.066, 0.074, 0.100, 0.291, 0.352 |
| F4 | place | 0.2915 ± 0.1444 | 0.7085 ± 0.1444 | 0.5501 | 0.093, 0.178, 0.237, 0.395, 0.476 |
| F4 | fold 0 | 0.1370 ± 0.1047 | 0.8630 ± 0.1047 | 0.3472 | 0.009, 0.074, 0.074, 0.178, 0.291 |
| F4 | fold 1 | 0.1425 ± 0.1465 | 0.8575 ± 0.1465 | 0.3202 | 0.006, 0.006, 0.093, 0.363, 0.363 |
| F4 | fold 2 | 0.1824 ± 0.1411 | 0.8176 ± 0.1411 | 0.4016 | 0.016, 0.016, 0.226, 0.226, 0.395 |
| F4 | fold 3 | 0.3135 ± 0.1639 | 0.6865 ± 0.1639 | 0.5375 | 0.010, 0.334, 0.352, 0.476, 0.476 |
| F4 | fold 4 | 0.2133 ± 0.1001 | 0.7867 ± 0.1001 | 0.4829 | 0.059, 0.059, 0.291, 0.292, 0.292 |
| F5 | all | 0.2111 ± 0.2555 | 0.7889 ± 0.2555 | 0.3188 | 0.000, 0.014, 0.096, 0.329, 0.800 |
| F5 | pick | 0.2261 ± 0.2393 | 0.7739 ± 0.2393 | 0.3668 | 0.001, 0.032, 0.138, 0.349, 0.750 |
| F5 | insert | 0.1200 ± 0.1974 | 0.8800 ± 0.1974 | 0.2166 | 0.000, 0.002, 0.021, 0.146, 0.584 |
| F5 | remove | 0.2329 ± 0.2662 | 0.7671 ± 0.2662 | 0.3375 | 0.001, 0.021, 0.112, 0.386, 0.821 |
| F5 | place | 0.2695 ± 0.2889 | 0.7305 ± 0.2889 | 0.3563 | 0.001, 0.035, 0.147, 0.442, 0.902 |
| F5 | fold 0 | 0.2106 ± 0.2380 | 0.7894 ± 0.2380 | 0.3408 | 0.001, 0.017, 0.104, 0.346, 0.714 |
| F5 | fold 1 | 0.1303 ± 0.2007 | 0.8697 ± 0.2007 | 0.2386 | 0.000, 0.005, 0.037, 0.165, 0.585 |
| F5 | fold 2 | 0.2089 ± 0.2617 | 0.7911 ± 0.2617 | 0.3041 | 0.000, 0.010, 0.082, 0.346, 0.810 |
| F5 | fold 3 | 0.3004 ± 0.3105 | 0.6996 ± 0.3105 | 0.3563 | 0.002, 0.033, 0.168, 0.528, 0.925 |
| F5 | fold 4 | 0.2107 ± 0.2206 | 0.7893 ± 0.2206 | 0.3673 | 0.000, 0.035, 0.145, 0.305, 0.701 |
| F6 | all | 0.2333 ± 0.2664 | 0.7667 ± 0.2664 | 0.3362 | 0.000, 0.017, 0.112, 0.394, 0.801 |
| F6 | pick | 0.3348 ± 0.2593 | 0.6652 ± 0.2593 | 0.4658 | 0.005, 0.085, 0.308, 0.539, 0.783 |
| F6 | insert | 0.1039 ± 0.1888 | 0.8961 ± 0.1888 | 0.1902 | 0.000, 0.001, 0.017, 0.109, 0.562 |
| F6 | remove | 0.2119 ± 0.2598 | 0.7881 ± 0.2598 | 0.3161 | 0.001, 0.017, 0.093, 0.327, 0.825 |
| F6 | place | 0.2813 ± 0.2904 | 0.7187 ± 0.2904 | 0.3699 | 0.004, 0.045, 0.159, 0.460, 0.893 |
| F6 | fold 0 | 0.2273 ± 0.2501 | 0.7727 ± 0.2501 | 0.3497 | 0.000, 0.017, 0.122, 0.400, 0.742 |
| F6 | fold 1 | 0.1887 ± 0.2419 | 0.8113 ± 0.2419 | 0.2962 | 0.000, 0.008, 0.057, 0.320, 0.711 |
| F6 | fold 2 | 0.2147 ± 0.2717 | 0.7853 ± 0.2717 | 0.2995 | 0.000, 0.010, 0.084, 0.340, 0.830 |
| F6 | fold 3 | 0.3150 ± 0.3121 | 0.6850 ± 0.3121 | 0.3665 | 0.001, 0.034, 0.199, 0.569, 0.912 |
| F6 | fold 4 | 0.2250 ± 0.2270 | 0.7750 ± 0.2270 | 0.3811 | 0.002, 0.039, 0.134, 0.366, 0.685 |

Per-recording and descriptive success/failure distributions are saved in `assessment/gate_weights.json`; per-sample and per-seed weights in `predictions/oof.npz`, aligned to frozen cohort row order. Entropy describes modality allocation, not predictive uncertainty. Success/failure differences are not causal.

## L. Process-context ablation

One fixed action permutation within each outer test fold, plus all-zero action; signals, quality, availability and trained parameters unchanged. Differences are ablated minus clean; negative values favor genuine context. These are context interventions, not signal-corruption experiments. A single permutation is a sensitivity diagnostic, not a permutation significance test. Zero one-hot context is outside the training support.

| Gate/context intervention | Mean |Δ visual weight| | Δ AUROC [95%] | Δ AP [95%] |
| --- | --- | --- | --- |
| F4:action_permuted | 0.1383 | 0.0049 [0.0011, 0.0084] | -0.0028 [-0.0154, 0.0115] |
| F4:action_zero | 0.1258 | 0.0037 [0.0002, 0.0073] | -0.0079 [-0.0153, 0.0007] |
| F6:action_permuted | 0.1013 | 0.0034 [-0.0016, 0.0080] | -0.0038 [-0.0125, 0.0060] |
| F6:action_zero | 0.0922 | 0.0027 [-0.0006, 0.0063] | -0.0034 [-0.0102, 0.0032] |


## M. Quality-context ablation

Quality variables replaced by each final fit’s training means (zeros after its own normalization); availability and action unchanged. Differences are ablated minus clean. This measures clean-context sensitivity, not verified reliability awareness.

| Gate/context intervention | Mean |Δ visual weight| | Δ AUROC [95%] | Δ AP [95%] |
| --- | --- | --- | --- |
| F5:quality_neutral | 0.2050 | 0.0124 [0.0034, 0.0216] | -0.0028 [-0.0210, 0.0157] |
| F6:quality_neutral | 0.1981 | 0.0045 [-0.0033, 0.0125] | 0.0046 [-0.0152, 0.0226] |


## N. Complexity versus benefit

Fusion parameters only: F1=0 and F2=3. U1 has 221 logistic coefficients/intercept plus calibration; U2 has 114,945 trained head parameters plus calibration; the shared frozen backbone is additional. F3–F6 costs below exclude shared feature extraction/branch inference. Neural deployment uses three models, so multiply per-seed parameter counts by three. Timing is hardware-specific, GPU warm-batch inference, not online end-to-end latency; normalization and transfer excluded. Device: `Tesla T4`.

| Model | Parameters/seed by fold | Inner training seconds | Final training seconds | 3-seed inference µs/row by fold |
| --- | --- | --- | --- | --- |
| F3 | [61825, 61825, 61825, 61825, 61825] | 89.7 | 19.9 | 1.00, 0.74, 0.68, 0.82, 0.81 |
| F4 | [74, 74, 74, 74, 146] | 187.9 | 30.5 | 1.22, 0.96, 0.89, 1.00, 1.03 |
| F5 | [658, 330, 658, 658, 330] | 187.9 | 30.7 | 1.26, 0.95, 0.89, 1.02, 1.06 |
| F6 | [362, 722, 722, 722, 722] | 187.5 | 30.8 | 1.25, 0.95, 0.88, 0.98, 1.05 |

Seed variability, calibration and fold consistency accompany point rankings. Reused F2 predictions require no new fitting. Additional nested branch generation is shared preprocessing, retained separately in inputs and execution log.

## O. Failed attempts and corrections

See `failures_and_corrections.md` and final validation for every failed attempt or correction. Previous Section 1B BLAS mismatch remains in its original run; original 16-thread execution is retained here. No unsuccessful artifact is deleted, no outcome-driven architecture expansion is permitted, and no frozen evidence is overwritten.

## P. Interpretation

**A. SIMPLE FUSION SUFFICIENT**. No gate satisfies all predeclared incremental criteria. Prefer static fusion for this tested budget. If intervals admit a meaningful gain, this is a simplicity decision under uncertainty, not proof of equivalence or proof that all adaptive architectures fail. The exact Section 1B F2 metrics reproduce by reuse; that is a provenance/parity result, not new independent confirmation. A convex weighted-logit gate is a constrained family: failure to beat F2 does not rule out every form of adaptive fusion.

## Q. Claims allowed

Frozen visual and statistical-sensor branches carry complementary information on this cohort. Static fusion retains its previously demonstrated incremental value. Model differences, context sensitivity and gate allocation may be described with their paired uncertainty. “Adaptive fusion improved clean predictive performance” is allowed only for a gate satisfying the stated incremental criteria. Restrict claims to the tested configurations, folds and cohort.

## R. Claims NOT allowed

No claim of robustness to degraded modalities, reliability awareness, audio benefit, unseen-site/object generalization, causal process diagnosis, universal architectural superiority or independent confirmation. Quality can encode process/content. A non-significant interval does not establish equivalence. No raw-accuracy headline, no treating seeds as independent sample size, no deployable oracle claim.

## S. SQ2 answer at this stage

A. SIMPLE FUSION SUFFICIENT. No gate satisfies all predeclared incremental criteria. Prefer static fusion for this tested budget. If intervals admit a meaningful gain, this is a simplicity decision under uncertainty, not proof of equivalence or proof that all adaptive architectures fail.

## T. SQ3 status

**NOT YET ANSWERED**. No signal corruption, modality dropout, missing-modality experiment or audio analysis was run. Clean performance and context ablations cannot establish robustness.

## U. Recommendation for Section 3

After researcher review, carry at most U1 statistical sensors, F2 learned static late fusion, and F5 (quality gate) into controlled mechanism testing. The adaptive reference is only the strongest tested gate by clean AP for mechanism testing; it is not declared superior to F2. Do not carry every architecture. Concatenation is optional only with a separate scientific rationale. This report recommends a future scope; no Section 3 experiment starts automatically.

## V. Provenance

Run: `runs/reassemble/20260927T192852Z-section2`. Config: `configs/reassemble/section2.json`; predeclared protocol: `docs/reassemble/SECTION_2_PROTOCOL.md`. Implementation commit: `e65d1dac83111ae167a23cd05a889a0fa74fd8f0`. Section 1 evidence `08d498d`; Section 1B implementation `06f93d1`, final evidence `4089b02`. Split SHA256: `30bb666f014f19e12bce7363ed84080721af30bbe499e6f03b3fd1da8ad78e69`. Input quality/feature/source identities are in `implementation.json` and unchanged prior manifests. Branch matrix hashes and all new output hashes are in `output_manifest.json`; training-only branches and fold memberships in `inputs/`; individual seed fits/checkpoints in `fits/`; final OOF scores/weights/ablations in `predictions/`; complete metrics and per-recording weights in `assessment/`. Final preservation, tests and environment checks: `validation.json`. IDE continuation: `docs/reassemble/SECTION_2_CONTINUATION.md`. No external master Reasoning Record was modified. The final result commit is discoverable with `git log -1 --format=%H -- artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md`.

SECTION 3 GO — STATIC FUSION IS THE APPROPRIATE ROBUSTNESS REFERENCE
