# SECTION 1 — Unimodal models and signal validation

2026-09-27T17:26:07.529463+00:00

## A. Question

Do frozen visual representations and sensor sequences independently identify failure beyond prior/action context on unseen recordings?

## B. Why this came before fusion

Fusion needs two demonstrably informative branches. Combining unsupported branches cannot establish complementarity; disagreement alone does not demonstrate fusion benefit.

## C. Evaluation protocol

4,530 complete action segments, 509 failures, 148 source HDF5 recordings. Exact frozen 5 outer / 4 inner recording-disjoint folds; seed 20260927. Models see no identity, text, absolute time or object labels. All scaling, selection, calibration and thresholds are fitted in outer training/inner folds. Epoch/C choices maximize mean inner AP. Inner-OOF sigmoid calibration and balanced-accuracy thresholds precede outer refitting; no test selection. ECE uses 15 fixed bins. 2000 recording-cluster bootstrap replicates give percentile intervals and paired differences. Intervals condition on fitted models; shared collection-day/scene effects remain a limitation.

## D. Baselines

Prior and majority measure trivial support. Four-action logistic regression tests context shortcuts. Per-channel statistical sensor logistic regression tests whether temporal complexity adds value; C in [0.1,1,10]. Statistics: mean, std, median, min, max, quartiles, range, RMS, progress slope.

## E. RT-DETR

Pinned PekingU/rtdetr_r18vd COCO backbone; final three maps spatial-mean pooled, 16 deterministic in-segment frames temporally mean pooled. Shipped preprocessing: bilinear resize to 640x640 RGB and divide by255; do_normalize=False in the pinned processor (no ImageNet mean/std normalization). All backbone parameters frozen; train 128-dimensional ReLU/dropout projection and binary head. AdamW lr .001, decay .001, batch 128; 5 or 10 epochs selected inside training folds. No boxes, detector training or fine-tuning. Exact model revision, processor and weight checksums: pretrained_model.json. Selected budgets/calibration: assessment/tuning.json.

Selected outer-fold epoch budgets (folds0–4): **5,5,10,10,5**. Trainable head: **114,945 parameters**, dropout0.1. Training uses binary cross-entropy with positive weight equal to training negatives/positives; gradient norm is clipped at1. Backbone remains in evaluation mode throughout feature extraction.

## F. PatchTST

Channels: measured_force:0, measured_force:1, measured_force:2, measured_torque:0, measured_torque:1, measured_torque:2, gripper_positions:0, gripper_positions:1, joint_efforts:0, joint_efforts:1, joint_efforts:2, joint_efforts:3, joint_efforts:4, joint_efforts:5, joint_efforts:6, joint_velocities:0, joint_velocities:1, joint_velocities:2, joint_velocities:3, joint_velocities:4, joint_velocities:5, joint_velocities:6.

512 in-segment progress positions, no extrapolation/long-gap interpolation. Training-only per-channel standard scaling; missing values filled with training mean and mask retained. Internal scaling disabled; masks do not suppress attention, so missingness robustness is untested. Transformers PatchTST initialized from scratch: 32 hidden units, 2 layers, 4 heads, FFN64, patch32/stride16, dropout .1; channel-independent shared encoder; mean patch pooling, channel concatenation, 128-dimensional projection. AdamW lr .001, decay .001, batch128; 3 or6 epochs selected by inner AP. This bounded budget does not establish optimal architecture suitability.

Selected outer-fold budgets: **6 epochs in every fold** (the maximum predeclared budget). **109,505 trainable parameters**. Weighted binary cross-entropy and gradient norm clipping match the visual head. No outcome-driven extension of the epoch budget was made.

## G. Results

Point estimate [95% recording-cluster interval]. Failure is positive; AUPRC means average precision.

| model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prior | 0.4839 [0.4520, 0.5162] | 0.1083 [0.0963, 0.1221] | 0.5000 [0.5000, 0.5000] | 0.4702 [0.4669, 0.4734] | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0.0998 [0.0910, 0.1089] | 0.0002 [0.0002, 0.0131] |
| majority | 0.5000 [0.5000, 0.5000] | 0.1124 [0.1011, 0.1242] | 0.5000 [0.5000, 0.5000] | 0.4702 [0.4669, 0.4734] | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 0.1124 [0.1011, 0.1242] | 0.1124 [0.1011, 0.1242] |
| action_only | 0.6851 [0.6623, 0.7088] | 0.1808 [0.1613, 0.2018] | 0.6505 [0.6302, 0.6697] | 0.4835 [0.4700, 0.4970] | 0.7642 [0.7235, 0.8036] | 0.1727 [0.1552, 0.1904] | 0.0951 [0.0869, 0.1037] | 0.0080 [0.0043, 0.0191] |
| sensor_statistics | 0.7793 [0.7549, 0.8040] | 0.4294 [0.3801, 0.4828] | 0.7056 [0.6830, 0.7286] | 0.6223 [0.6066, 0.6393] | 0.6149 [0.5661, 0.6622] | 0.2765 [0.2522, 0.3032] | 0.0804 [0.0735, 0.0879] | 0.0174 [0.0127, 0.0274] |
| rtdetr | 0.6978 [0.6716, 0.7232] | 0.2307 [0.1983, 0.2701] | 0.6414 [0.6175, 0.6658] | 0.5153 [0.4956, 0.5355] | 0.6621 [0.6149, 0.7075] | 0.1810 [0.1617, 0.2013] | 0.0943 [0.0862, 0.1028] | 0.0070 [0.0057, 0.0184] |
| patchtst | 0.7054 [0.6798, 0.7304] | 0.2416 [0.2102, 0.2826] | 0.6352 [0.6123, 0.6595] | 0.5463 [0.5286, 0.5643] | 0.5639 [0.5173, 0.6100] | 0.1956 [0.1745, 0.2192] | 0.0937 [0.0859, 0.1025] | 0.0067 [0.0058, 0.0198] |

| contrast | AUROC difference | AP difference |
| --- | --- | --- |
| rtdetr minus prior | 0.2139 [0.1658, 0.2599] | 0.1223 [0.0910, 0.1598] |
| rtdetr minus action_only | 0.0127 [-0.0154, 0.0406] | 0.0499 [0.0225, 0.0836] |
| patchtst minus prior | 0.2215 [0.1787, 0.2643] | 0.1332 [0.1042, 0.1703] |
| patchtst minus action_only | 0.0203 [-0.0115, 0.0494] | 0.0608 [0.0293, 0.0974] |
| patchtst minus sensor_statistics | -0.0740 [-0.1004, -0.0469] | -0.1878 [-0.2314, -0.1407] |

All outer-fold, per-action and calibration-bin results: assessment/results.json.

## H. Permutation controls

19 full nested refits per deep branch; circular label shifts within each recording/action, preserving stratum prevalence and circular runs. Fixed original folds. This is a conditional cyclic-exchangeability control, not an IID null or a proof against scene/object shortcuts. p=(1+null AP >= observed AP)/20, resolution .05.

| model | observed AP | null AP range | p |
| --- | --- | --- | --- |
| rtdetr | 0.2307 | 0.1435–0.1784 | 0.05 |
| patchtst | 0.2416 | 0.1548–0.1876 | 0.05 |

Complete null scores and changed-label counts: results.json.

Both conditional permutation p-values are **0.05**, the minimum resolution with19 controls. The retained action/recording structure means null AUROC need not equal0.5. These controls do not by themselves satisfy the paired comparison gate against action-only.

## I. Complementarity

Not computed: two informative branches have not both passed the predeclared gate.

## J. Failed attempts / corrections

See failures_and_corrections.md in this run. Earlier acquisition corrections (audio header length, trailing-idle defect masks, optional report formatter) are retained in the audit; audio is outside this section. No outer-result-driven architecture change is allowed.

## K. Interpretation

Both learned branches improve AP over action-only: RT-DETR difference **+0.0499 [0.0225,0.0836]**, PatchTST **+0.0608 [0.0293,0.0974]**. Their AUROC differences remain inconclusive: **+0.0127 [-0.0154,0.0406]** and **+0.0203 [-0.0115,0.0494]**, respectively. Thus neither primary branch satisfies the predeclared requirement on both metrics.

The statistical sensor baseline is the strongest tested model. PatchTST is worse by **0.0740 AUROC [0.0469,0.1004]** and **0.1878 AP [0.1407,0.2314]** (paired differences expressed as the baseline advantage). This run establishes no benefit from the tested temporal Transformer over engineered sensor statistics. It does not establish that the sensor modality lacks information.

All PatchTST folds selected the maximum allowed6 epochs. Whether a larger training budget changes this result is an untested question requiring a new predeclared phase, not a reason to revise this experiment after observing its outer results. No complementary-error analysis was run because both primary gates remained conditional.

## L. What cannot be claimed

No fusion advantage, corruption robustness, unseen-object/site generalization, causal failure diagnosis, online early-warning performance, independent segment observations, verified audio alignment, optimal hyperparameters or superiority of all Transformers. OOF uncertainty omits full refitting uncertainty. Conditional permutation invariance and a small Monte Carlo sample limit inference.

## M. Decision

| modality | decision |
| --- | --- |
| rtdetr | CONDITIONAL |
| patchtst | CONDITIONAL |

PASS requires positive paired lower bounds versus prior and action-only on both primary metrics, plus conditional permutation p<=.05. Both must pass for the joint GO; this is an intersection-union decision, not choosing a winning modality. Stop for researcher review before Section 2.

## N. Provenance

Run: `runs/reassemble/20260927T154732Z-section1`. Configuration: `configs/reassemble/section1.json`; protocol: `docs/reassemble/SECTION_1_PROTOCOL.md`. Baseline Git commit and frozen protocol/config/split hashes: provenance.json. Actual training source hashes/device: training_implementation.json. Initial audit checkpoint: 6721414. Input identities: preceding audit input_manifest.json. Model weights/checkpoints, OOF predictions and permutation evidence stay in this unique run. Final output identities: output_manifest.json. Actual training implementation commit: **852a123**. All **44 complete OOF model/control runs and220 outer assessments** finished; logs contain no training/decoder warnings or errors. **41 tests passed**, dependencies passed, and preservation checks found no changes to **68,745 protected entries or149 raw HDF5 files**. The initial preservation verifier followed three Python symlinks incorrectly; comparison was corrected to lstat, matching the original snapshot, with zero differences. No fusion, audio or robustness model was trained.

The original machine-generated report remains unchanged in assessment/. This reviewed report and final validation are in finalization/. Final output identities and logs are recorded in final_output_manifest.json. The remaining decision is researcher review of conditional unimodal evidence before any Section2 or further training.

FUSION CONDITIONAL — EVIDENCE REQUIRES REVIEW
