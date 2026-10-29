# 04 ARCHITECTURE EXPLANATION

Run `20261029T004900Z`. Published 2026-10-29T02:15:32.074020+00:00. Pipeline state: **FULL_VIDEO_QC_IN_PROGRESS**. Immutable report snapshot: `VIFAILBACK/10_final_research_reports/report_snapshots/20261029T004900Z/20261029T021531975083Z`.

The visual branch executes the RT-DETR-derived ResNet18VD CNN only, not its detection transformer or bounding-box head. Spatial means of128/256/512 feature maps concatenate to896; mean over16times and3cameras produces896; original new-task head896→128 ReLU dropout0.1→1 predicts an episode logit. T-only feature scaling and C-only sigmoid calibration follow the source workflow.

The source framework is imported through `src/vifailback/reference.py`, not copied. ViFailback adapters own label/episode joins, multiview sampling, sensor channels, feature names, groups, fit orchestration and corruption policy. S1=S3 is source-exact balanced C1 logistic plus C calibration. S2 is balanced HGB with200iterations, leaves7/15/31 selected on V; no internal random early stopping.

F1 averages calibrated probabilities. Exact F2 fits unweighted C1 logistic on[visual_probability,S3_probability], using grouped OOF predictions. It is not the F2 classification metric. The original F5-style DecisionGate uses quality and availability only:13→16 ReLU→2softmax weights branch logits. Fixed40epochs and OOF-only scaling; no task/action one-hot. All target heads/calibration/F2/gates fit anew.

Original weights: `../datasets/REASSEMBLE/cache/section1_models/ac77a11ff0170a41b771c03264987f8ce2b0d753/model.safetensors`, SHA256 `fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093`.
Donor: `26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_BEST_MODEL.pt`, SHA256 `5700e8912cf360c845087923e4b417631a886daf928e1655b1031c9ac27c8ce0`; selected epoch47,100 executed, seed42. Only115 compatible CNN tensors transfer; source head, normalization buffers, calibrators, fusion coefficients and gates do not transfer. The source's75-fit study is separate and unfinished at initial inspection.
