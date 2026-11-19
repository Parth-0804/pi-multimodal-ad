# Sensor feature contracts and estimators

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

| Dataset | Native channels | Window/clock | Statistical vector | Missing/scaling |
|---|---|---|---|---|
| REASSEMBLE | force3, torque3, gripper2, efforts7, velocities7 =22 | Annotated action window; per-stream timestamps;512 normalized-progress points |22×10=220: mean, population SD, median, min/max, Q25/Q75, peak-to-peak, RMS, slope over progress |Observed mask retained; fit-local mean fill/standardization; no new filtering |
| MSM |15 configured real MTConnect numerical channels | Native cut interval; verified video/sensor mapping; variable irregular samples |15×6=90: mean, SD, RMS, min, max, peak-to-peak |Finite real measurements; fit-local scaling; corruption scale derived from training rows |
| Handover |6 measured/estimated wrench channels | Explicit common video/sensor support; nearest native frame/sample mapping, <=0.1s bound |6×6=36, same external statistics contract |14 zero-channel traces retained; HSR measured versus Gen3 estimated wrench is a domain limitation |
| ViFailback |14 state+12 joint velocity+2 gripper effort =28 |25Hz episode-relative clock; entire recorded episode |28×10=280, exact channel list in sensor contract |Training-only imputation/scaling; finite cache join by episode ID; not a force/torque sensor |

REASSEMBLE512 is a sample count per action, **not512Hz**. None of these window-level predictors proves early failure detection. Original action labels are native outcomes; no lifecycle-to-health relabeling is allowed.

Original REASSEMBLE static sensor LR: balanced classes, candidate C0.1/1/10, max_iter2000, random_state0; mean inner AP selects C, training-OOF sigmoid calibration and balanced-accuracy threshold. Solver/penalty/tolerance omitted from original construction are FRAMEWORK DEFAULT — NOT VERIFIED unless a fitted estimator supplies them. Later F2 follow-up reuses the canonical original sensor probabilities/calibration rather than retraining a convenient replacement. Later shared legacy recipes use random_state42; nominal experiment seed and estimator RNG are separate fields.

MSM/Handover LR is predefined balanced C1, lbfgs, max_iter2000, random_state0. HGB: learning_rate0.1, max_iter100, max_leaf_nodes15, min_samples_leaf10, l2_regularization1, early_stoppingFalse; balanced sample weights. Saved source-identified estimator.get_params is retained in the per-run configuration. No fixed-depth value is invented when max_depth=None.

ViFailback S1=S3 is one actual balanced C1 logistic method, max_iter2000, random_state42, plus separate C calibration. S2 HGB varies max_leaf_nodes7/15/31; learning_rate0.05, max_iter200, min_samples_leaf20, l2_regularization0.1, early_stoppingFalse; training balance weights and nominal seed. Validation macro AP selects among three candidates before C calibration.36 jobs imply108 actual candidate fits,36 selected states. The three deterministic seeds can yield identical sensor predictions; they are not independent data samples.

REASSEMBLE PatchTST classifier:22channels/context512, patch32, stride16, d_model32,2layers,4heads, FF64, dropout0.1, channel pooled22×32→128→1, random initialization;3/6 epoch snapshots. S-6/S-LONG change budget, not the native channel definition. S-HYBRID combines sensor branches; it is not visual fusion. PHM PatchTST is a separate scalar-regression implementation using72 derived minute-feature channels in its standard recipe, train-only median imputation/population SD, masked temporal pooling, GELU/dropout scalar head. Ridge summarizes these sequences and selects alpha by EXP-A MAE.

No feature-selection algorithm is demonstrated for the fixed primary sensor contracts. Specific channel names, raw source paths, native label mapping, timestamps and group identities are linked in the native manifests; they are preserved rather than replaced with generic names.

## Evidence anchors

- [configs/reassemble/section1.json](../../../configs/reassemble/section1.json) — visual/sensor/logistic_C/selection/calibration.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — actual classifier forwards, neural_fit, logistic_fit.
- [src/reassemble/section1_features.py](../../../src/reassemble/section1_features.py) — frame pooling and normalized-progress sensor resampling.
- [runs/reassemble/20260927T154732Z-section1/training_implementation.json](../../../runs/reassemble/20260927T154732Z-section1/training_implementation.json) — recorded original implementation revision.
- [MSM/04_experiment_protocol/experiment_config.json](../../../MSM/04_experiment_protocol/experiment_config.json) — fixed P recipe, labels/groups/sensor channels.
- [MSM/03_processed_model_inputs/final_sample_manifest.csv](../../../MSM/03_processed_model_inputs/final_sample_manifest.csv) — 1895 eligible sample IDs/native labels/clock mapping/source hashes.
- [MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json](../../../MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json) — 54 completed protocol/fold/seed cases, output hashes.
- [CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py](../../src/external_eval/evaluate.py) — execute_case: train, inner OOF, official validation, held-out scopes.
- [CROSS_DATASET_COMPARISON/src/external_eval/models.py](../../src/external_eval/models.py) — fit_base/fit_fusions/fit_quality/predictions.
- [HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json](../../../HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json) — participant_oof_gate/observation_amendment/validation_use.
- [HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv](../../../HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv) — 587 mapped IDs, native labels, empty participant IDs.
- [HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json](../../../HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json) — three seeds complete; fused methods skipped.
- [HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json](../../../HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json) — official dataset record and metadata.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
