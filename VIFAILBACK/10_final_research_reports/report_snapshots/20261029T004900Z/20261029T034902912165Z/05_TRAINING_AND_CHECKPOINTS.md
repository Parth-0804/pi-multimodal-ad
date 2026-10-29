# 05 TRAINING AND CHECKPOINTS

Run `20261029T004900Z`. Published 2026-10-29T03:49:05.228393+00:00. Pipeline state: **CPU_SENSOR_BASELINES_COMPLETE_VISUAL_FEATURES_RUNNING**. Immutable report snapshot: `VIFAILBACK/10_final_research_reports/report_snapshots/20261029T004900Z/20261029T034902912165Z`.

V1 uses frozen original pretrained CNN features and a new896→128→1 head. V2 trains the complete CNN convolution and promoted FrozenBN affine from the original pretrained source. V3 uses the verified REASSEMBLE full-CNN donor, a new head, and the same adaptation recipe as V2. All100 epochs execute; highest validation macro_AP selects the checkpoint, earliest tie. T-only balanced BCE; AdamW head1e-3/backbone1e-5, wd1e-3, clip1, cosine100→0.1initial LR, FP32, effective batch8. FrozenBN moments stay fixed. Full models use exact two-pass frame chunks4 with all48 images.

Each fit saves `BEST_MODEL.pt`, `FINAL_EPOCH100.pt`, `RECOVERY.pt`, `HISTORY.json`, gradient/update evidence, calibrator, predictions, metrics and a hash receipt. Final/recovery are hardlinks to the same immutable payload, saving space. Epoch-boundary recovery stores model/optimizer/scheduler and Python/NumPy/Torch/CUDA RNG; an interrupted epoch replays. Source checkpoint compatibility alone is not a trained target result.

There are12 fit partitions per seed and condition,36 per visual condition,72 full-CNN fits across V2/V3. The live GPU is reserved for the ongoing REASSEMBLE75-fit study. Target GPU runs wait for its verified completion marker and an idle GPU; no GPU-hour cutoff or reduction of100 epochs is applied. This can require a long queue. The CPU preflight is not a GPU throughput estimate.

Original weights: `../datasets/REASSEMBLE/cache/section1_models/ac77a11ff0170a41b771c03264987f8ce2b0d753/model.safetensors`, SHA256 `fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093`.
Donor: `26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_BEST_MODEL.pt`, SHA256 `5700e8912cf360c845087923e4b417631a886daf928e1655b1031c9ac27c8ce0`; selected epoch47,100 executed, seed42. Only115 compatible CNN tensors transfer; source head, normalization buffers, calibrators, fusion coefficients and gates do not transfer. The source's75-fit study is separate and unfinished at initial inspection.

Measured disposable CPU preflight: [63.62, 58.592, 54.466]seconds/update; all73 CNN/head trainable tensors changed, moments fixed and replay exact when the preflight receipt passes. These updates are not retained as a target classifier or evaluated as evidence.

Acquisition: {'ACQUIRED_VERIFIED': 13095, 'VERIFIED_EXISTING': 57}. Camera QC: (13150, 13152). Final cohort: 4382. Completed fits: {'visual_frozen': 0, 'visual_frozen_high_only': 0, 'visual_finetuned100': 0, 'reassemble_transfer': 0, 'sensor_baselines': 36}.