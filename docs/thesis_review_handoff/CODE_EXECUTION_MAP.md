# Code execution map

Use this as an inspection guide for the professor meeting. **Do not execute these research entry points for review.** Flows derive from static imports and named calls; `->` means an inspected processing/call step and `=>` means a persisted-data dependency, not a direct function call. A retained run does not imply its entire upstream raw pipeline can currently rerun. Canonical migration and compatibility: [REPO_MAP.md](../../REPO_MAP.md)<br>[docs/repository_restructure/path_mapping.csv](../../docs/repository_restructure/path_mapping.csv)<br>[docs/repository_restructure/COMPATIBILITY_VALIDATION.md](../../docs/repository_restructure/COMPATIBILITY_VALIDATION.md).

## W1. PHM structural inventory and alignment

**Purpose and input/intermediate/output:** Read-only archive identities and event tables; input raw archives are now retired locally. Preserve outer/member/run/modality identity. Alignment output is a sample-definition audit, not certified image/sensor synchronization.

```text
scripts/phm2026/dataset/profile_dataset.py
  -> phm2026.cli.profile_dataset_main
  -> profile_asset_inventory(plan, PHM2026Adapter())
  -> archive and source inventory and provenance
  => pinned profiling tables used downstream by audit_alignment_main
  -> build_alignment_pipeline -> write_alignment_run
```

**Inspected entry/modules:** [scripts/phm2026/dataset/profile_dataset.py](../../scripts/phm2026/dataset/profile_dataset.py)<br>[src/phm2026/cli.py](../../src/phm2026/cli.py)<br>[src/phm2026/datasets/phm2026.py](../../src/phm2026/datasets/phm2026.py)<br>[src/phm2026/profiling/assets.py](../../src/phm2026/profiling/assets.py)<br>[src/phm2026/profiling/alignment_pipeline.py](../../src/phm2026/profiling/alignment_pipeline.py)

**Configuration/settings:** [configs/datasets/phm2026.yaml](../../configs/datasets/phm2026.yaml). **Saved run/artifact:** [runs/phm2026_dataset_description/20260813T202043619114Z-ad7f9832](../../runs/phm2026_dataset_description/20260813T202043619114Z-ad7f9832). **Output/report:** [docs/planning/D1_3_CHECKPOINT.md](../../docs/planning/D1_3_CHECKPOINT.md). **Relevant software test:** [tests/phm2026/test_alignment_pipeline.py](../../tests/phm2026/test_alignment_pipeline.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W2. PHM v3 target construction

**Purpose and input/intermediate/output:** Image source identities -> heuristic candidate area -> tooth rows -> raw worst-three run score plus separately named alternatives. Post-run offline target generation; not independently physical damage truth.

```text
scripts/phm2026/targets/derive_image_targets.py
  -> load_yaml_config + load_pinned_run
  -> load_image_sources -> profile_target_images
  -> aggregate_targets: deterministic view, exclude teeth 1-4
  -> write_target_run
  => per_tooth_damage / run_damage_targets used by sensor feature stage
```

**Inspected entry/modules:** [scripts/phm2026/targets/derive_image_targets.py](../../scripts/phm2026/targets/derive_image_targets.py)<br>[src/phm2026/profiling/images.py](../../src/phm2026/profiling/images.py)<br>[src/phm2026/targets/image_damage.py](../../src/phm2026/targets/image_damage.py)

**Configuration/settings:** [configs/experiments/phm2026_image_target_v3.yaml](../../configs/experiments/phm2026_image_target_v3.yaml). **Saved run/artifact:** [runs/phm2026_image_target/20260912T052857044116Z-c936a4e3](../../runs/phm2026_image_target/20260912T052857044116Z-c936a4e3). **Output/report:** [docs/thesis/TARGET_VERSION_LEDGER.md](../../docs/thesis/TARGET_VERSION_LEDGER.md). **Relevant software test:** [tests/phm2026/test_target_definition_v3.py](../../tests/phm2026/test_target_definition_v3.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W3. PHM features and run sequences

**Purpose and input/intermediate/output:** Historical model-manifest eligibility is reused; target pin is v3. Minute features/masks are grouped into run sequences; no claim raw high-frequency waveform enters this summary-feature baseline.

```text
scripts/phm2026/features/build_model_dataset.py
  -> build_sensor_manifests / build_image_samples
  => pinned sensor-file eligibility manifest
 scripts/phm2026/features/build_sensor_features.py
  -> extract_minute_features -> archive and HDF5 bounded reading
  -> write_sensor_feature_run
  => build_run_sequences + fit_feature_normalizer (training rows only)
```

**Inspected entry/modules:** [scripts/phm2026/features/build_model_dataset.py](../../scripts/phm2026/features/build_model_dataset.py)<br>[src/phm2026/targets/model_dataset.py](../../src/phm2026/targets/model_dataset.py)<br>[scripts/phm2026/features/build_sensor_features.py](../../scripts/phm2026/features/build_sensor_features.py)<br>[src/phm2026/features/sensor_minutes.py](../../src/phm2026/features/sensor_minutes.py)<br>[src/phm2026/preprocessing/timeseries.py](../../src/phm2026/preprocessing/timeseries.py)

**Configuration/settings:** [configs/experiments/phm2026_sensor_features_v3.yaml](../../configs/experiments/phm2026_sensor_features_v3.yaml). **Saved run/artifact:** [runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee](../../runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee). **Output/report:** [runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee/reports/sensor_feature_summary.json](../../runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee/reports/sensor_feature_summary.json). **Relevant software test:** [tests/phm2026/test_sensor_minute_features.py](../../tests/phm2026/test_sensor_minute_features.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W4. PHM sensor LOEO comparison and separate rescoring

**Purpose and input/intermediate/output:** Twenty out-of-experiment run predictions; fold train mean is constant. Sensor-submodality fusion uses three encoders. Monotonic diagnostic is a separate historical pinned-prediction path, intentionally evaluation-label fitted; no deployment calibration claim.

```text
scripts/phm2026/results/loeo_evaluation.py
  -> pinned minute features + run targets
  -> FOLDS: held-out experiment, other train/validation experiments
  -> training normalizer -> build_run_sequences
  -> train_fold(build_model(PatchTSTRegressor or LateFusionRegressor))
  -> run predictions / regression_metrics
  -> clustered_bootstrap / paired_clustered_bootstrap -> loeo_summary
 Separate: rescore_monotonic.py -> monotonic_metrics
  -> monotonic_rescale.fit_transform(prediction, evaluation truth)
```

**Inspected entry/modules:** [scripts/phm2026/results/loeo_evaluation.py](../../scripts/phm2026/results/loeo_evaluation.py)<br>[src/phm2026/models/patchtst/model.py](../../src/phm2026/models/patchtst/model.py)<br>[src/phm2026/fusion/late_fusion.py](../../src/phm2026/fusion/late_fusion.py)<br>[src/phm2026/evaluation/regression.py](../../src/phm2026/evaluation/regression.py)<br>[scripts/phm2026/results/rescore_monotonic.py](../../scripts/phm2026/results/rescore_monotonic.py)<br>[src/phm2026/evaluation/monotonic.py](../../src/phm2026/evaluation/monotonic.py)

**Configuration/settings:** [runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/config/resolved_config.yaml](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/config/resolved_config.yaml). **Saved run/artifact:** [runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f). **Output/report:** [runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json). **Relevant software test:** [tests/phm2026/test_regression_evaluation.py](../../tests/phm2026/test_regression_evaluation.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W5. Historical PHM pseudo-box detection and scalar multitask

**Purpose and input/intermediate/output:** Pseudo-box source and scalar targets are heuristic historical v2; detector AP differs from segment-classification AP. R4 reference lacks B predictions and is explicitly excluded from PHM LOEO model ranking.

```text
build_rtdetr_pseudo_boxes.py -> pseudo_boxes helpers -> heuristic annotation bank
  => train_rtdetr_detector.py -> Ultralytics RTDETR + detection evaluation
  => train_rtdetr_multitask.py -> PseudoBoxScalarDataset
  -> RTDETRMultitask + ScalarDamageHead / training_loss
  -> normalized_rtdetr_predictions + scalar/detection metrics
```

**Inspected entry/modules:** [scripts/phm2026/targets/build_rtdetr_pseudo_boxes.py](../../scripts/phm2026/targets/build_rtdetr_pseudo_boxes.py)<br>[src/phm2026/targets/pseudo_boxes.py](../../src/phm2026/targets/pseudo_boxes.py)<br>[scripts/phm2026/training/train_rtdetr_detector.py](../../scripts/phm2026/training/train_rtdetr_detector.py)<br>[scripts/phm2026/training/train_rtdetr_multitask.py](../../scripts/phm2026/training/train_rtdetr_multitask.py)<br>[src/phm2026/models/rtdetr/multitask.py](../../src/phm2026/models/rtdetr/multitask.py)

**Configuration/settings:** [configs/experiments/phm2026_rtdetr_multitask.yaml](../../configs/experiments/phm2026_rtdetr_multitask.yaml). **Saved run/artifact:** [runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099](../../runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099). **Output/report:** [docs/planning/R4_RTDETR_MULTITASK_CHECKPOINT.md](../../docs/planning/R4_RTDETR_MULTITASK_CHECKPOINT.md). **Relevant software test:** [tests/phm2026/test_rtdetr_multitask.py](../../tests/phm2026/test_rtdetr_multitask.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W6. REASSEMBLE cohort, features and unimodal controls

**Purpose and input/intermediate/output:** 4530 dual-complete completed action segments; independent evaluation unit recording. Standardizer/logistic C selection/Platt-style sigmoid calibration/thresholds use training data. Null is conditional cyclic-exchangeability, not IID label chance.

```text
01_inventory.py -> reassemble.inventory.main
  => 02_audit.py -> interval/coverage and recording split artifacts
  => 03_section1_features.py -> cohort + extract
  -> resample_progress(512) -> statistics(220)
  -> 16 hand frames -> frozen .model.backbone.model -> pooled visual vector
  => 04_section1_train.py -> verify_splits + evaluate_model
  -> inner selection -> refit -> calibrate -> outer predictions
  -> chronological cyclic permute_labels within recording/action
  => 05_section1_report.py -> grouped metrics / bootstrap
```

**Inspected entry/modules:** [scripts/reassemble/01_inventory.py](../../scripts/reassemble/01_inventory.py)<br>[scripts/reassemble/02_audit.py](../../scripts/reassemble/02_audit.py)<br>[src/reassemble/section1_features.py](../../src/reassemble/section1_features.py)<br>[src/reassemble/section1_models.py](../../src/reassemble/section1_models.py)<br>[src/reassemble/section1_report.py](../../src/reassemble/section1_report.py)

**Configuration/settings:** [configs/reassemble/section1.json](../../configs/reassemble/section1.json). **Saved run/artifact:** [runs/reassemble/20260927T154732Z-section1](../../runs/reassemble/20260927T154732Z-section1). **Output/report:** [artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md](../../artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md). **Relevant software test:** [tests/reassemble/test_section1.py](../../tests/reassemble/test_section1.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W7. Strict nested F2 and original learned fusion heads

**Purpose and input/intermediate/output:** F2 fits three logistic parameters on training branch OOF, never concatenated outer-test OOF. Section2 config is configs/reassemble/section2.json. Meta-threshold crossfit is conditional on the branch bank, not unbiased full-pipeline validation.

```text
07_section1b.py -> section1b.stacking
  -> index_plan + guard_partition
  -> subfolds -> fit_branch (exclude inner assessment groups)
  -> outer-training branch OOF probability pairs
  -> fit_stacker(meta[train], y[train]) / training meta threshold
  -> branch refits + frozen parity -> outer-test probability pair -> F2 OOF
  => 09_section2.py -> train_outer + inner_inputs + fit_head
  -> F3/F4/F5/F6 -> train-only calibration -> outer predictions
```

**Inspected entry/modules:** [scripts/reassemble/07_section1b.py](../../scripts/reassemble/07_section1b.py)<br>[src/reassemble/section1b.py](../../src/reassemble/section1b.py)<br>[scripts/reassemble/09_section2.py](../../scripts/reassemble/09_section2.py)<br>[src/reassemble/section2.py](../../src/reassemble/section2.py)<br>[src/reassemble/section2_data.py](../../src/reassemble/section2_data.py)<br>[src/reassemble/section2_models.py](../../src/reassemble/section2_models.py)

**Configuration/settings:** [configs/reassemble/section1b.json](../../configs/reassemble/section1b.json). **Saved run/artifact:** [runs/reassemble/20260927T175336Z-section1b](../../runs/reassemble/20260927T175336Z-section1b). **Output/report:** [artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md](../../artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md). **Relevant software test:** [tests/reassemble/test_section1b.py](../../tests/reassemble/test_section1b.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W8. Frozen corruption inference and synthesis

**Purpose and input/intermediate/output:** Fault seed derivation does not use labels. Complete missing branch returns surviving model with its frozen threshold; both absent abstain. Completion gates do not train AST/object OOD after failed prerequisites. Warm cost measured separately.

```text
12_section3_visual.py / 13_section3_sensor.py
  -> native pixel / raw sensor perturbations -> recomputed features/quality
  => 14_section3_evaluate.py -> gate_predict / extract_arrays
  -> fixed clean branches/heads/thresholds -> degraded predictions
  => 16_section3_report.py -> paired absolute/degradation/weight diagnostics
  => completion_efficiency / completion_synthesis -> tables/figures/handoff
```

**Inspected entry/modules:** [scripts/reassemble/12_section3_visual.py](../../scripts/reassemble/12_section3_visual.py)<br>[scripts/reassemble/13_section3_sensor.py](../../scripts/reassemble/13_section3_sensor.py)<br>[src/reassemble/section3_visual.py](../../src/reassemble/section3_visual.py)<br>[src/reassemble/section3_sensor.py](../../src/reassemble/section3_sensor.py)<br>[src/reassemble/section3_evaluate.py](../../src/reassemble/section3_evaluate.py)<br>[src/reassemble/section3_report.py](../../src/reassemble/section3_report.py)<br>[src/reassemble/completion_synthesis.py](../../src/reassemble/completion_synthesis.py)

**Configuration/settings:** [configs/reassemble/section3_corruptions.json](../../configs/reassemble/section3_corruptions.json). **Saved run/artifact:** [runs/reassemble/20260927T204649Z-section3](../../runs/reassemble/20260927T204649Z-section3). **Output/report:** [artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md](../../artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md). **Relevant software test:** [tests/reassemble/test_section3.py](../../tests/reassemble/test_section3.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W9. Independent validity and real human review

**Purpose and input/intermediate/output:** Independent metric implementation still compares sklearn as a reference; it does not just call the original reporter. Core audit and later human receipt have different sealed dates/statuses. Human ratings never enter model fitting.

```text
scripts/thesis/final_validity_audit/numerical.py
  -> join saved cohort / predictions / groups
  -> independent metrics.py (NumPy rank/AP/confusion/calibration)
  -> compare original sklearn summaries + paired cluster draws
  -> sensitivities(per action, recording weights, operating points)
 scope_boundary.py -> trace / boundaries; diagnostics.py -> permitted logistic diagnostics
 human_review.py -> blinded clip package / real CSV ingestion
  -> receipt + flagged cases + pending adjudication
 finalize.py / seal.py -> validation / manifest / core audit handoff
```

**Inspected entry/modules:** [scripts/thesis/final_validity_audit/numerical.py](../../scripts/thesis/final_validity_audit/numerical.py)<br>[scripts/thesis/final_validity_audit/metrics.py](../../scripts/thesis/final_validity_audit/metrics.py)<br>[scripts/thesis/final_validity_audit/scope_boundary.py](../../scripts/thesis/final_validity_audit/scope_boundary.py)<br>[scripts/thesis/final_validity_audit/diagnostics.py](../../scripts/thesis/final_validity_audit/diagnostics.py)<br>[scripts/thesis/final_validity_audit/human_review.py](../../scripts/thesis/final_validity_audit/human_review.py)<br>[scripts/thesis/final_validity_audit/finalize.py](../../scripts/thesis/final_validity_audit/finalize.py)

**Configuration/settings:** [artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z/00_protocol/audit_config.json](../../artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z/00_protocol/audit_config.json). **Saved run/artifact:** [artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z](../../artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z). **Output/report:** [artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z/05_final_review/FINAL_VALIDITY_AUDIT_HANDOFF.md](../../artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z/05_final_review/FINAL_VALIDITY_AUDIT_HANDOFF.md). **Relevant software test:** [tests/thesis/final_validity_audit/test_metrics_identity.py](../../tests/thesis/final_validity_audit/test_metrics_identity.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## W10. Separate completed exploratory extensions

**Purpose and input/intermediate/output:** Arrows with => are persisted-artifact handoffs, not direct call claims. Task1 discontinued; old supervisor must not restart it. Boundary study has its own config/source/control parity and single-seed scope, not a combination of best extensions.

```text
sensor_resume.py -> neural/checkpoint training recovery -> longer sensor branch
  -> hybrid.main -> nested same-sensor stacking
 Section1B stacking / Section2 strict inner inputs => anchored.main -> Task3 fit
 task4_external.py -> corruption_resume.worker -> declared stage module
  -> branch_banks/corruptions/robust_fusion -> matched augmentation
  => robust_report.py
 close_additional_improvements.py -> numerical_audit -> scope decision / final reports
 Separate boundary_visual.runner: preflight.load -> training.branch
  -> variant OOF -> conditional section1b.fit_stacker
  => boundary_visual.report
```

**Inspected entry/modules:** [src/reassemble/additional_improvements/sensor_resume.py](../../src/reassemble/additional_improvements/sensor_resume.py)<br>[src/reassemble/additional_improvements/hybrid.py](../../src/reassemble/additional_improvements/hybrid.py)<br>[src/reassemble/additional_improvements/branch_banks.py](../../src/reassemble/additional_improvements/branch_banks.py)<br>[src/reassemble/additional_improvements/anchored.py](../../src/reassemble/additional_improvements/anchored.py)<br>[src/reassemble/additional_improvements/corruption_resume.py](../../src/reassemble/additional_improvements/corruption_resume.py)<br>[src/reassemble/additional_improvements/robust_fusion.py](../../src/reassemble/additional_improvements/robust_fusion.py)<br>[scripts/reassemble/close_additional_improvements.py](../../scripts/reassemble/close_additional_improvements.py)<br>[src/reassemble/boundary_visual/runner.py](../../src/reassemble/boundary_visual/runner.py)<br>[src/reassemble/boundary_visual/report.py](../../src/reassemble/boundary_visual/report.py)

**Configuration/settings:** [configs/reassemble/additional_improvements/execution.json](../../configs/reassemble/additional_improvements/execution.json). **Saved run/artifact:** [runs/reassemble/additional_improvements_executed/20260928T000346Z/05_final_comparison/20260930T083000Z](../../runs/reassemble/additional_improvements_executed/20260928T000346Z/05_final_comparison/20260930T083000Z). **Output/report:** [artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md). **Relevant software test:** [tests/reassemble/additional_improvements/test_training_recovery.py](../../tests/reassemble/additional_improvements/test_training_recovery.py); test scope is the named component, not an automatic full-scientific-workflow validation.

## Supplementary paths to inspect only if discussing these studies



|Study|Actual execution/data relationship|Settings and saved evidence|Boundary|
|---|---|---|---|
|RawVib|angular_features.py process → angular_resample/order_spectrum/residual_of/channel_features → file_features; l1_screen.py reads retained run summaries; save_tsa/sector_features/sector_screen are separately executed stages.|[scripts/rawvib/angular_features.py](../../scripts/rawvib/angular_features.py)<br>[scripts/rawvib/l1_screen.py](../../scripts/rawvib/l1_screen.py)<br>[scripts/rawvib/sector_screen.py](../../scripts/rawvib/sector_screen.py)<br>[data/rawvib/l1_screen.json](../../data/rawvib/l1_screen.json)<br>[docs/thesis/RAW_VIB_20260927T095726Z.md](../../docs/thesis/RAW_VIB_20260927T095726Z.md)|Script defaults; no dedicated unit-test file identified. Later rank/level models were not run after failed EXP-F feature gate.|
|Paderborn|extract_features.py reads named MAT channels and identifiers; parse_factsheets.py creates target table; gate1_sanity/gate2_signal call common protocol/models/bootstrap; gate3 scripts exist but not executed.|[scripts/paderborn/extract_features.py](../../scripts/paderborn/extract_features.py)<br>[scripts/paderborn/parse_factsheets.py](../../scripts/paderborn/parse_factsheets.py)<br>[scripts/paderborn/common.py](../../scripts/paderborn/common.py)<br>[scripts/paderborn/gate2_signal.py](../../scripts/paderborn/gate2_signal.py)<br>[data/paderborn/gate2.json](../../data/paderborn/gate2.json)<br>[docs/thesis/ARCH_VAL_PB_20260926T224859Z.md](../../docs/thesis/ARCH_VAL_PB_20260926T224859Z.md)|Protocol fork and ordinal bearing-constant labels; Gate3 unrun. No dedicated test located.|
|Intel foundations|01_inventory → 02_label_audit → 03_make_split; 04_foundations inspect_sample/audit_split performs integrity/timing/exposure probes; 05_foundation_report consolidates outputs.|[scripts/intel_welding/01_inventory.py](../../scripts/intel_welding/01_inventory.py)<br>[scripts/intel_welding/04_foundations.py](../../scripts/intel_welding/04_foundations.py)<br>[scripts/intel_welding/05_foundation_report.py](../../scripts/intel_welding/05_foundation_report.py)<br>[configs/intel_welding/foundations.json](../../configs/intel_welding/foundations.json)<br>[tests/intel_welding/test_intel_foundations.py](../../tests/intel_welding/test_intel_foundations.py)<br>[docs/intel_welding/RESULTS_REVIEW.md](../../docs/intel_welding/RESULTS_REVIEW.md)|Arrows describe separately executed stage outputs. src/intel_welding model packages are placeholders; new modelling blocked.|

## Environment, paths and what not to run

Inspect [pyproject.toml](../../pyproject.toml): source-layout package discovery includes phm2026, intel_welding, reassemble and legacy forwarding. The supported environment is the existing ma_thesis_env editable installation, with imports tested without PYTHONPATH. Scientific runtime dependencies are not declared/pinned by this minimal project metadata. Experiment environment/provenance controls historical reproduction: [docs/thesis/FINAL_THESIS_REPRODUCIBILITY.md](../../docs/thesis/FINAL_THESIS_REPRODUCIBILITY.md), [runs/reassemble/20260927T154732Z-section1/environment.json](../../runs/reassemble/20260927T154732Z-section1/environment.json), [docs/repository_restructure/compatibility_runs/20261006T182404Z/provenance.json](../../docs/repository_restructure/compatibility_runs/20261006T182404Z/provenance.json).

[src/phm2026/repository_paths.py](../../src/phm2026/repository_paths.py) discovers repository markers .git and AGENTS.md; real workflows with relative inputs still expect repository root. Script bootstraps and supported legacy forwarding preserve execution behavior; former flat unit-test filename selectors remain historical, not recreated: [docs/repository_restructure/COMPATIBILITY_VALIDATION.md](../../docs/repository_restructure/COMPATIBILITY_VALIDATION.md). Avoid downloader main/help (provenance side effects), old additional-improvements supervisor, train scripts and report generators that may rewrite/relaunch runs. No such entry point was called for this review.

## Code tiers

The master §15 lists Tier1 scientific logic and its oral-defense rationale, Tier2 supporting concepts and Tier3 tooling: [docs/thesis_review_handoff/MASTER_THESIS_REVIEW_HANDOFF.md](../../docs/thesis_review_handoff/MASTER_THESIS_REVIEW_HANDOFF.md). Tests and historical results are separately scoped in the evidence index.
