# Configuration differences that matter

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

| Comparison | Preserved factors | Material differences / effect on interpretation |
|---|---|---|
| Original frozen versus C100 |Pinned CNN family,16frames,896→128→1 |Batch128 versus8; short5/10 snapshots versus100cosine; original extraction FP16 versus full FP32; T/V/C role changes; test-exposed fit selection. Not an isolated fine-tuning effect. |
| Paired B100 versus C100 |Seed42, same1752 T/419 V/686 C/753assessment, fresh head, FP32,100horizon, headLR.001, wd.001, batch8,16frames, no augmentation |C adds backboneLR1e-5 and trains all CNN+affine; B uses cached fixed features; time/VRAM excludes B extraction. Controlled within-pilot point comparison, one exposed fold. |
| C20 versus C100 |Full-CNN architecture, original pretrained initialization |Different jobs/cohort roles; C20 executes cosine50 prefix to20, C100cosine100; C100 restarts fresh. No continuation or monotonic budget inference. |
| Original F2 versus100eF2 |Canonical static sensor probabilities/labels for same original outer1 |Original nested fourinner branches versus single920holdout stack bank; different visual branches and fitting rows, exposed test. Raw AP gain cannot isolate representation effect. |
| Historical V-FT versus fullC |Same R18vd family |Last-stage-only, temporal warm-start, AMP versus all CNN/affine fresh-head FP32. Different computational architecture/training scope. |
| External P across datasets |Fixed base/fusion code and hyperparameters |Real sensor definitions, frame sampling/letterbox, window/native labels/group granularity differ; Handover participant OOF blocked. Scores cannot rank datasets. |
| Vi V1 versus high-only |Same task splits, seeds,100head recipe |48frame3-camera versus16framehigh; not matched observation bandwidth. V2/V3 model training absent. |

Every per-run field can be resolved in PARAMETER_PROVENANCE.csv. Missing betas/epsilon remain FRAMEWORK DEFAULT — NOT VERIFIED unless recovered from the actual state;28 Phase1/100e optimizer states were statically verified as betas(.9,.999), eps1e-8. Do not silently apply that recovery to other source-only histories.

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
- [runs/reassemble/20260927T175336Z-section1b/assessment/results.json](../../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json) — metrics, paired recording intervals, complementation.
- [runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json](../../../runs/reassemble/20260927T175336Z-section1b/assessment/stacker_coefficients.json) — five fitted F2 coefficient states.
- [src/reassemble/section1b.py](../../../src/reassemble/section1b.py) — fit_stacker; nested calibrated probability inputs.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ALL_MODEL_METRICS.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/ALL_MODEL_METRICS.json) — M1–M7 common-threshold metrics.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json) — conditional paired recording intervals.
- [experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/HISTORICAL_COMPARABILITY.json](../../../experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/07_evaluation_results/HISTORICAL_COMPARABILITY.json) — canonical sensor identities and stacking-bank limitations.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
