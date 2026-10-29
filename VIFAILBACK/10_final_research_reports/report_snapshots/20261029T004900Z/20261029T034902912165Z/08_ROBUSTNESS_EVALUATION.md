# 08 ROBUSTNESS EVALUATION

Run `20261029T004900Z`. Published 2026-10-29T03:49:05.228393+00:00. Pipeline state: **CPU_SENSOR_BASELINES_COMPLETE_VISUAL_FEATURES_RUNNING**. Immutable report snapshot: `VIFAILBACK/10_final_research_reports/report_snapshots/20261029T004900Z/20261029T034902912165Z`.

Stress tests are fixed in `src/vifailback/corruptions.py`: missing25/50%frames, dropped temporal windows25/50%, blur kernels5/15, square occlusion25/50%area,1/2 cameras unavailable, JPEG20/5, visual shifts10/25%; sensor channels missing25/50%, intervals20/40%, Gaussian noise0.5/1.0 T-channel std, frozen readings, shifts10/25%; combined partial degradation and complete modality loss. Selection/masks never consult labels.

Clean-trained branches, F2 and gate face matched test corruptions. No corruption augmentation was given only to the gate. Raw observations are corrupted before source statistics; missing statistics use T-scaled mean imputation for logistic and native HGB missing-value handling. Input quality is recomputed identically from clean/corrupted selected frames and sensor arrays. Synthetic shifts are within-episode sampling perturbations.

Complete visual/sensor absence invokes the same explicitly programmed surviving-branch fallback for all fusion methods. Missing unimodal scores use a declared T-prevalence reference. Both missing abstains, with coverage reported separately. These fallbacks are not learned robustness. No robustness result exists until the matching saved stress predictions/metric tables complete. Exact outputs live under07_robustness_experiments, never inferred from clean AP.

Matched augmented controls distinguish quality conditioning from merely receiving corruption training: compare Gate_aug with F2_aug and Gate_static_aug. Comparison with clean-trained unimodal models alone cannot attribute an advantage to conditioning. Static F2_aug uses the same C1 source method on the augmented records; augmentation also changes its effective sample count/regularization context. All control choices predate held-out results.
