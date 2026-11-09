# HPO model-selection independent-review package

This portable export packages the completed2026-11-03 audit and the existing implementation evidence for independent model-selection discussion. No audit was rerun,no training/tuning/inference was started,and no experiment,checkpoint,label or result was modified. No final model or HPO budget is selected.

## Where to find every requested item

| Requested item | Package location |
|---|---|
| 1. Executive summary,Tables A–H | [EXECUTIVE_AUDIT_SUMMARY.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/01_executive_overview/EXECUTIVE_AUDIT_SUMMARY.md) |
| 2. Complete model configuration table | [ALL_MODEL_CONFIGURATION_TABLE.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/03_hyperparameter_configuration/ALL_MODEL_CONFIGURATION_TABLE.md) |
| 2/11. Every effective run configuration | [EFFECTIVE_CONFIGURATIONS.json](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json) |
| 3. Hyperparameter tuning history | [HYPERPARAMETER_TUNING_HISTORY.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/03_hyperparameter_configuration/HYPERPARAMETER_TUNING_HISTORY.md) |
| 4. All model results | [ALL_MODEL_RESULTS_SUMMARY.csv](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/05_results/ALL_MODEL_RESULTS_SUMMARY.csv) |
| 4/5. All numeric metrics,with seed/fold/scope | [ALL_RECORDED_METRICS_LONG.csv](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/05_results/ALL_RECORDED_METRICS_LONG.csv) |
| 5. Exact training-run and seed/fold identities | [TRAINING_RUN_INVENTORY.csv](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/04_training_and_checkpoints/TRAINING_RUN_INVENTORY.csv) |
| 6. Scientific comparability matrix | [COMPARABILITY_MATRIX.csv](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/05_results/COMPARABILITY_MATRIX.csv) |
| 7. Model-selection evidence | [MODEL_SELECTION_EVIDENCE_TABLE.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/08_future_hpo_readiness/MODEL_SELECTION_EVIDENCE_TABLE.md) |
| 8. HPO readiness and constraints | [HPO_READINESS_AND_CONSTRAINTS.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/08_future_hpo_readiness/HPO_READINESS_AND_CONSTRAINTS.md) |
| 9. CNN loss curves | [100E_LOSS.png](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/100E_LOSS.png) |
| 9. Validation AP curves | [100E_VALIDATION_AP.png](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/100E_VALIDATION_AP.png) |
| 9. LR schedules | [100E_LEARNING_RATES.png](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/100E_LEARNING_RATES.png) |
| 9/11. All C20 outer-refit curves | [C20_OUTER_REFIT_CURVES.png](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/C20_OUTER_REFIT_CURVES.png) |
| 10. Full100-epoch comparison | [FROZEN_VS_FINETUNED_100_EPOCHS.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/FROZEN_VS_FINETUNED_100_EPOCHS.md) |
| 11. C20 status/configuration/results narrative | [MODEL_AND_CONFIGURATION_AUDIT.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/MODEL_AND_CONFIGURATION_AUDIT.md) |
| 11. Complete REASSEMBLE results | [COMPLETE_RESULTS.csv](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/COMPLETE_RESULTS.csv) |
| 11. Complete epoch histories | [EPOCH_HISTORIES.csv](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/EPOCH_HISTORIES.csv) |
| 12. Frozen/full-CNN fitter | [phase_training.py](repository/26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_training.py) |
| 12/15. Architecture,optimizer and scheduler | [phase_model.py](repository/26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py) |
| 12. Original frozen branch training | [section1_models.py](repository/src/reassemble/section1_models.py) |
| 12. C20 launcher and override | [c20_train.py](repository/26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_c_only_20epoch_revision_01/26102026_source/c20_train.py) |
| 12. Full/frozen100 launcher | [compare100_train.py](repository/26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py) |
| 12. Original F2 fitting and nested OOF | [section1b.py](repository/src/reassemble/section1b.py) |
| 12.100-epoch static-sensor F2 follow-up | [evaluate.py](repository/experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/src/evaluate.py) |
| 13. Original sensor model and training settings | [section1.json](repository/configs/reassemble/section1.json) |
| 13. External visual/sensor/fusion implementations | [models.py](repository/CROSS_DATASET_COMPARISON/src/external_eval/models.py) |
| 13. ViFailback sensor implementations | [baselines.py](repository/VIFAILBACK/src/vifailback/baselines.py) |
| 14. Recorded overfitting diagnostic | [TRAINING_GENERALIZATION_DIAGNOSTICS.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/06_dataset_specific/REASSEMBLE/TRAINING_GENERALIZATION_DIAGNOSTICS.md) |
| 14. Recorded dropout/weight decay/augmentation | [ALL_RUN_HYPERPARAMETERS.csv](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/03_hyperparameter_configuration/ALL_RUN_HYPERPARAMETERS.csv) |
| 15. Checkpoint-selection audit | [CHECKPOINT_SELECTION_AUDIT.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/04_training_and_checkpoints/CHECKPOINT_SELECTION_AUDIT.md) |
| 16. Original REASSEMBLE nested splits | [nested_splits.json](repository/runs/reassemble/20260927T154732Z-section1/nested_splits.json) |
| 16. Phase1 actual fit/split plan | [PHASE1_FIT_PLAN.json](repository/26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_evidence/PHASE1_FIT_PLAN.json) |
| 16. External evaluation and OOF protocol | [evaluate.py](repository/CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py) |
| 16. ViFailback task partitions | [fit_partitions.json](repository/VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json) |
| 16. MSM evaluation protocol | [split_protocol.md](repository/MSM/04_experiment_protocol/split_protocol.md) |
| 16. Handover protocol/participant limitation | [split_protocol.md](repository/HANDOVER/experiments/common_support_v2/04_experiment_protocol/split_protocol.md) |
| 17. Scientific missing evidence | [MISSING_EVIDENCE.md](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/07_scientific_validity/MISSING_EVIDENCE.md) |
| 17. Historical audit source manifest | [FILE_AND_SOURCE_MANIFEST.csv](repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103/09_reviewer_handoff/FILE_AND_SOURCE_MANIFEST.csv) |

## Preserve run-level differences

The full configuration JSON/CSV,parameter provenance,all model metrics,per-seed/per-fold results and epoch histories are included without row reduction. Filter dataset,experiment,seed,fold,evaluation_scope,protocol,corruption,threshold and metric_path before aggregating. MSM pooled AP and mean-fold AP remain distinct. Original F2 and the100-epoch pilot have different stacking designs. C20 has25 completed20-epoch fits at seed42;the other50 original fits are deferred and C20 F2 finalization has not executed. Handover participant-OOF fusion and Vi full/transfer classifier training remain unexecuted. These historical findings are not re-evaluated by this export.

Every original implementation/configuration path is preserved below `repository/`,including support modules,legacy source versions,training receipts and split plans. Use `repository/` as the root when interpreting repository-relative values. Scientific configuration values and result cells are unchanged. Scripts are included for inspection;the package does not automatically run them and it does not contain the raw inputs/large weights needed for a training replay.

## External artifacts and portable references

Large checkpoint binaries,serialized estimators,raw recordings/datasets,feature arrays/caches and bulk prediction banks are intentionally external. Their original paths,recorded SHA256 identities and sizes are in [EXTERNAL_ARTIFACTS.csv](EXTERNAL_ARTIFACTS.csv),the historical checkpoint inventory and source manifest. Lack of a local binary is not missing scientific reporting. Available fitted JSON coefficients/scalers,configuration metadata and histories are included where selected.

Local Markdown links to included files resolve inside this package. Links to intentionally external historical evidence are redirected to [EXTERNAL_REFERENCES.md](EXTERNAL_REFERENCES.md);[LINK_TARGET_TRANSFORMATIONS.csv](LINK_TARGET_TRANSFORMATIONS.csv) retains the original target. Only exported Markdown navigation was changed. Original code,configuration values,metric rows and source evidence remain byte-identical. [SOURCE_FILE_MANIFEST.csv](SOURCE_FILE_MANIFEST.csv) records original and exported hashes,including any navigation-only transformation. Historical audit manifests refer to the original audit bytes;the package manifest governs exported bytes.

Derived working-state gzip duplicates,temporary synthetic checkpoint fixtures and in-progress audit notes are excluded;their complete final configurations/results remain included. [EXPORT_OMISSIONS.csv](EXPORT_OMISSIONS.csv) lists those audit-only exclusions. Credentials,environment secrets and raw datasets are not exported.

## Integrity and verification

[PACKAGE_MANIFEST.csv](PACKAGE_MANIFEST.csv) lists SHA256 and size for every package file except its own recursive entry. [EXPORT_VALIDATION.json](EXPORT_VALIDATION.json) records the packaging checks. The ZIP was CRC-tested,extracted into an independent temporary directory,and verified by file hash and internal Markdown references. No original experiment modules were imported or executed. Git HEAD and staged-state identity are recorded in [EXPORT_PROVENANCE.json](EXPORT_PROVENANCE.json);nothing was staged,committed or pushed.

After extracting,use `python package_tools/verify_package.py PATH_TO_PACKAGE_ROOT` to repeat package-integrity and reference checks using only the standard library. This verifies the export,not the research experiments.
