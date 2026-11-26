# Visual architectures and executed trainable scope

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

The primary research visual representation is **RT-DETR R18vd CNN only**, loaded from `PekingU/rtdetr_r18vd`, pinned revision `ac77a11ff0170a41b771c03264987f8ce2b0d753`. Source forwards select `.model.backbone.model`; the RT-DETR hybrid encoder, decoder, boxes and object scores are not consumed. Every frame contributes spatial means of the final 128/256/512 maps, concatenated to 896. Temporal averaging removes order in the mean baseline. The head is Linear896→128, ReLU, Dropout0.1, Linear128→1; sigmoid is applied for probabilities. A training-only fixed standardizer precedes the head. Head parameters: **114,945**.

Original visual inputs: RGB, 640×640, rescale1/255, no ImageNet mean/std. Sixteen uniform ordered action frames use rounded linspace indices; original extraction uses FP16 autocast and stores FP32 features. New Phase1/100e uses the preserved action-frame contract and FP32 fine-tuning. MSM/Handover use 16 temporal-bin centers, aspect-preserving letterbox640 with sample-aspect-ratio correction: this is a dataset-specific preprocessing adaptation, not an identical pixel path. ViFailback uses 16 rounded-linspace frames from each of three ordered cameras (48 embeddings), equal mean over time then cameras; high-only is 16-frame ablation.

Frozen CNN has 11,190,112 parameters, plus 114,945 head: conceptual pipeline **11,305,057 total**, **114,945 trainable**, **11,190,112 frozen**. Cached-head checkpoints can contain only the head and moments; absence of backbone tensors is expected for that fit module and requires the separately identified pretrained bank for end-to-end inference.

Full C promotes **9,856 FrozenBatchNorm affine buffers** into trainable parameters, preserving tensor names and pretrained values. CNN count becomes **11,199,968**; with head, **11,314,913 trainable/total**, zero frozen *parameters*. Frozen running means/variances remain buffers and remain fixed. All executed convolution stages are trainable. First-update and full-fit gradient/weight checks are retained in each original fit directory. Fresh original pretrained CNN and a freshly seeded head initialize both100e arms; C100 did not resume C20. Different parameter count comes from promoted affine buffers, not a changed feature width.

Historical `FineTunedVisual` and one-day/32-frame probes tune only the final CNN stage, with frozen prefix; they must not be described as full CNN training. The additional-improvements V-FT also warm-starts an existing temporal head and uses FP16 autocast/GradScaler. Its learning conditions differ from C100.

TemporalHead projects896→128, optional sinusoidal positions, one TransformerEncoder layer (4 heads, FF256, dropout0.1), masked temporal mean→1 (247,425 trainable parameters). V-MEAN retains mean pooling; V-NOPOS disables positions. Boundary V0–V4 use bin-based means with shared896→128 projection: V1 two8-frame bins, V2 4/8/4, V3last4, V4first4+last4; V5 uses64-dimensional one-layer GRU with positional encoding. They consume frozen CNN features.

The legacy encoder comparison actually executes CNN + input_proj + `RTDetrHybridEncoder` (AIFI and FPN/PAN), then pooling/head; no decoder or object outputs. Its feature width and parameter capacity differ, so any score difference is a complete-pipeline comparison, not isolated proof of attention benefit. Exact checkpoint/config counts are in MODEL_PARAMETER_COUNTS.csv; unrecovered values are NOT RECORDED.

PHM RT-DETR detection/regression/multitask implementations are separate Ultralytics/pseudo-target work. They do not define the native-failure architecture. Frozen DINOv2 nearest-baseline patch scoring is also distinct and has no new gradient training.

## Evidence anchors

- [configs/reassemble/section1.json](../../../configs/reassemble/section1.json) — visual/sensor/logistic_C/selection/calibration.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — actual classifier forwards, neural_fit, logistic_fit.
- [src/reassemble/section1_features.py](../../../src/reassemble/section1_features.py) — frame pooling and normalized-progress sensor resampling.
- [runs/reassemble/20260927T154732Z-section1/training_implementation.json](../../../runs/reassemble/20260927T154732Z-section1/training_implementation.json) — recorded original implementation revision.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json) — effective shared100 horizon; head/backbone LR.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py) — all CNN stages, FrozenBN affine promotion; fixed running moments.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py) — training100/checkpoint selection/recovery.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json) — history/best/executed_epochs, T/V/C/assessment sample identities.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json) — history/best/executed_epochs, T/V/C/assessment sample identities.
- [src/reassemble/additional_improvements/finetune.py](../../../src/reassemble/additional_improvements/finetune.py) — FineTunedVisual.
- [00_experiments/rt_detr_encoder_comparison/code/features.py](../../../00_experiments/rt_detr_encoder_comparison/code/features.py) — Prefix.forward.
- [src/reassemble/additional_improvements/models.py](../../../src/reassemble/additional_improvements/models.py) — TemporalHead.
- [src/reassemble/boundary_visual/models.py](../../../src/reassemble/boundary_visual/models.py) — V0–V4.
- [src/reassemble/boundary_visual/models.py](../../../src/reassemble/boundary_visual/models.py) — V5.
- [scripts/phm2026/results/anomalydino_sweep.py](../../../scripts/phm2026/results/anomalydino_sweep.py) — 20 frozen scoring configurations; no gradient fits.
