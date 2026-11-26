# Complete model inventory

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

The audit defines **32 computational families**, separating distinct forward paths and explicitly including non-gradient baselines. This is a taxonomy, not a count of independent trained models. RT-DETR pretrained detector archives, tutorials, random-gradient tests and recovery slots are not additional scientific families. Mean16/32/48, seed repetitions and augmented versions remain variants of their computational family.

| ID | Dataset | Model family | Actual architecture | Status/results |
| --- | --- | --- | --- | --- |
| F01 | All primary | Prevalence constant | Training-side positive prior; no learned neural parameters | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F02 | REASSEMBLE | Action-only logistic | One-hot action context → balanced logistic | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F03 | All primary | Static sensor logistic | Training-only standardization → logistic → optional sigmoid calibration; penalty default unverified where absent | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F04 | MSM/HANDOVER/VIFAILBACK | Sensor HGB | Histogram gradient-boosted classification trees | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F05 | All primary | Frozen R18vd mean + MLP | 128+256+512 spatial means → temporal/camera mean896 →128 ReLU dropout0.1 →1 | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F06 | REASSEMBLE | Last-stage CNN adaptation | Frozen CNN prefix + final stage trainable + visual head | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F07 | REASSEMBLE | Full CNN adaptation | All executed CNN convolutions + promoted FrozenBN affine + fresh head; fixed running moments | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F08 | REASSEMBLE legacy | CNN + RT-DETR hybrid encoder | CNN → input projections → RTDetrHybridEncoder AIFI/FPN/PAN → pooled head | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F09 | REASSEMBLE | Positional temporal Transformer | 896→128, sinusoidal time positions, 1 encoder layer/4 heads/FF256, masked mean →1 | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F10 | REASSEMBLE | Temporal Transformer without positions | Same TemporalHead, positions=False; order ablation | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F11 | REASSEMBLE | Boundary-bin visual pooling | Shared 896→128 ReLU dropout0.1; selected frame-bin means concatenated →1 | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F12 | REASSEMBLE | Temporal GRU | 896→64 ReLU dropout0.1 + positions → GRU64 → mean →1 | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F13 | REASSEMBLE | PatchTST classification | 22 channels×512 progress points, patch32/stride16, d32, 2 layers/4 heads/FF64 →128→1 | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F14 | All primary except blocked Handover | F2 probability logistic | sigmoid(b+wV*pV+wS*pS); signed unconstrained constant coefficients | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F15 | All primary | Probability average | (pV+pS)/2; no fitted fusion coefficients | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F16 | REASSEMBLE | Feature concatenation F3 | Visual128 and sensor220 separately→128; concat256 LayerNorm→32/64 ReLU dropout→1 | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F17 | REASSEMBLE/MSM/VIFAILBACK | Masked softmax logit gate | Context→hidden ReLU→2; masked softmax; sigmoid(sum alpha*logit(p)) | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F18 | REASSEMBLE | Anchored constant adjustment | Fixed F2 anchor; two learned tanh-bounded coefficient adjustments | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F19 | REASSEMBLE | Anchored adaptive adjustment | Context42→16→2 adjusts fixed F2 coefficients per sample | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F20 | REASSEMBLE legacy | Additive quality logistic | sigmoid(b + w·[pV, pS, z8]) | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F21 | REASSEMBLE legacy | Interaction quality logistic | sigmoid(b + w·[pV, pS, z8, pV*z8, pS*z8]) | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F22 | PHM legacy | PatchTST scalar regression | Minute feature channels → PatchTST encoders → scalar damage regression | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F23 | PHM legacy | Ridge regression | Per-normalized-minute feature mean/std/min/max/last → Ridge | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F24 | PHM legacy | RT-DETR scalar regression | Detector-derived image representation → scalar pseudo-damage head | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F25 | PHM legacy | RT-DETR object detection | Ultralytics detector, pseudo-bounding-box target; detection losses | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F26 | PHM legacy | RT-DETR multitask | Joint detector loss and scalar regression loss | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F27 | PHM legacy | Latent sensor late fusion | One PatchTST per sensor group; pooled embeddings concatenate → scalar head | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F28 | PHM legacy | Decision sensor late fusion | Per-group PatchTST+scalar head; learned affine combination of scalars | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F29 | PHM legacy | Process-aware sensor gate | Per-group embeddings project to32; process-context gate softmax; weighted embedding→scalar head | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F30 | PHM legacy evaluation | DINOv2 change scoring | Frozen DINOv2 patch cosine NN to baseline bank; mean/top fractions/max score | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F31 | PHM legacy diagnostic | Sorted profile constant | Mean ordered training tooth profile; top3 scalar diagnostic | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |
| F32 | REASSEMBLE | Static/temporal sensor hybrid | Static and temporal SENSOR probability combination; no video branch | SOURCE VERIFIED; completed evidence where linked; DINO/profile are evaluation baselines |


There are 7,969 reconstructed per-fit/configuration records: 7,929 marked COMPLETE and 40 REUSED. Of COMPLETE, 174 PHM SQ2/SQ3 calls are inferred from completed aggregate output plus source control flow, not individual receipts. The remaining 7,755 are individually corroborated by fit logs/receipts/candidate validation tables. They include permutation controls, nested candidate trials and recovery reconstruction refits; they are **not 7,929 independent replications**. Calibration/meta-crossfit nuisance estimators are not all included in that count. Other unlogged historical fits may not be recoverable.

See EXPERIMENT_INVENTORY.csv for study entry points/configurations/status and TRAINING_RUN_INVENTORY.csv for every record. The 4,920 checkpoint candidates include pretrained/disposable/copied/recovery artifacts; 4,438 unique hashes are byte identities, not unique model count. JSON coefficient-state references are indexed separately.

REBOOT has feasibility/parsing evidence, but no trained native-failure model artifacts were found. Intel welding material is preliminary data/EDA/source evidence, not a completed comparable classifier study. PHM architecture/results are historical provisional damage-target research and must remain separate from native binary failure outcomes.

## Evidence anchors

- [CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py](../../src/external_eval/evaluate.py) — metrics/predictions.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — logistic_fit/evaluate_model.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — Standardizer/logistic_fit.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — run.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — VisualHead.
- [src/reassemble/additional_improvements/finetune.py](../../../src/reassemble/additional_improvements/finetune.py) — FineTunedVisual.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py) — full CNN forward / optimizer.
- [00_experiments/rt_detr_encoder_comparison/code/features.py](../../../00_experiments/rt_detr_encoder_comparison/code/features.py) — Prefix.forward.
- [src/reassemble/additional_improvements/models.py](../../../src/reassemble/additional_improvements/models.py) — TemporalHead.
- [src/reassemble/additional_improvements/models.py](../../../src/reassemble/additional_improvements/models.py) — TemporalHead.forward.
- [src/reassemble/boundary_visual/models.py](../../../src/reassemble/boundary_visual/models.py) — V0–V4.
- [src/reassemble/boundary_visual/models.py](../../../src/reassemble/boundary_visual/models.py) — V5.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — SensorHead.
- [src/reassemble/section1b.py](../../../src/reassemble/section1b.py) — fit_stacker.
- [CROSS_DATASET_COMPARISON/src/external_eval/models.py](../../src/external_eval/models.py) — predictions.
- [src/reassemble/section2_models.py](../../../src/reassemble/section2_models.py) — ConcatHead.
- [src/reassemble/section2_models.py](../../../src/reassemble/section2_models.py) — DecisionGate.
- [src/reassemble/additional_improvements/models.py](../../../src/reassemble/additional_improvements/models.py) — AnchoredAdjustment.
- [src/reassemble/additional_improvements/models.py](../../../src/reassemble/additional_improvements/models.py) — AnchoredAdjustment.forward.
- [00_experiments/adaptive_fusion_robustness/code/quality_fusion.py](../../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py) — design/fit_all.
- [00_experiments/adaptive_fusion_robustness/code/quality_fusion.py](../../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py) — design/fit_all.
- [src/phm2026/models/patchtst/model.py](../../../src/phm2026/models/patchtst/model.py) — PatchTSTRegressor.
- [src/phm2026/models/patchtst/regression.py](../../../src/phm2026/models/patchtst/regression.py) — Ridge alpha selection.
- [src/phm2026/models/rtdetr/regression.py](../../../src/phm2026/models/rtdetr/regression.py) — regressor forward.
- [src/phm2026/models/rtdetr/detection.py](../../../src/phm2026/models/rtdetr/detection.py) — detector training.
- [src/phm2026/models/rtdetr/multitask.py](../../../src/phm2026/models/rtdetr/multitask.py) — multitask forward.
- [src/phm2026/fusion/late_fusion.py](../../../src/phm2026/fusion/late_fusion.py) — LateFusionRegressor.
- [src/phm2026/fusion/modality_fusion.py](../../../src/phm2026/fusion/modality_fusion.py) — DecisionLevelFusion.
- [src/phm2026/fusion/modality_fusion.py](../../../src/phm2026/fusion/modality_fusion.py) — ProcessAwareGatedFusion.
- [scripts/phm2026/results/anomalydino_sweep.py](../../../scripts/phm2026/results/anomalydino_sweep.py) — 20 frozen scoring configurations; no gradient fits.
- [scripts/phm2026/results/verify_target_constants.py](../../../scripts/phm2026/results/verify_target_constants.py) — sorted_profiles; no neural fit.
- [src/reassemble/additional_improvements/hybrid.py](../../../src/reassemble/additional_improvements/hybrid.py) — main.
