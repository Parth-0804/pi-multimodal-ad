# Remaining physical moves for approval

Automatic review rejected the earlier bulk action because it could include protected source payloads or active dependencies. No bulk move occurred.

The verified small source/configuration/documentation phase is separate. This plan lists the remaining physical moves, with no old-path aliases.

If approved, move only the listed files/subtrees, including any source copies enclosed in these inactive evidence bundles. This is a narrow exception to no-move protection for these listed paths only. Do not edit/delete payloads, interrupt jobs, move the excluded roots below, or rewrite stored provenance. Use same-filesystem renames, verify every regular file by device/inode/size, preserve original records, and keep the source-to-destination mapping for recovery.

## Excluded roots

- `MSM/01_raw_dataset`
- `HANDOVER/01_raw_dataset`
- `REBOOT/01_raw_dataset`
- `REBOOT/runs`
- `MILLING DATASET/data`
- `MILLING DATASET/.tools`
- `VIFAILBACK`
- `DATASET_RESEARCH/VIFAILBACK_VERIFICATION`
- `src/reassemble`
- `scripts/reassemble`
- `configs/reassemble`
- `runs/reassemble`
- `artifacts/reassemble`
- `26.10.2026_feedback_experiments`
- `parth_ws_bootstrap`
- `experiments/exp_a_initial_eda_r1_r3_r5`
- `data`
- `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/staging`
- `MILLING DATASET/runs/20261026T233709740813Z-stage2/staging`
- `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/source_evidence`
- `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/10_Visual_And_Sensor_Examples`

## Physical move list

| Existing path | New path |
|---|---|
| `MSM/02_labels_and_alignment` | `implementations/MSM/results/02_labels_and_alignment` |
| `MSM/03_processed_model_inputs` | `implementations/MSM/results/03_processed_model_inputs` |
| `MSM/04_experiment_protocol` | `implementations/MSM/results/04_experiment_protocol` |
| `MSM/05_trained_models` | `implementations/MSM/results/05_trained_models` |
| `MSM/06_evaluation_results` | `implementations/MSM/results/06_evaluation_results` |
| `MSM/07_robustness_experiments` | `implementations/MSM/results/07_robustness_experiments` |
| `MSM/08_visual_examples_and_eda` | `implementations/MSM/results/08_visual_examples_and_eda` |
| `MSM/09_final_reports` | `implementations/MSM/results/09_final_reports` |
| `MSM/MIGRATION_PLAN.md` | `implementations/MSM/docs/MIGRATION_PLAN.md` |
| `MSM/README.md` | `implementations/MSM/docs/WORKSPACE.md` |
| `MSM/logs` | `implementations/MSM/results/logs` |
| `HANDOVER/02_labels_and_alignment` | `implementations/HANDOVER/results/02_labels_and_alignment` |
| `HANDOVER/03_processed_model_inputs` | `implementations/HANDOVER/results/03_processed_model_inputs` |
| `HANDOVER/04_experiment_protocol` | `implementations/HANDOVER/results/04_experiment_protocol` |
| `HANDOVER/05_trained_models` | `implementations/HANDOVER/results/05_trained_models` |
| `HANDOVER/06_evaluation_results` | `implementations/HANDOVER/results/06_evaluation_results` |
| `HANDOVER/07_robustness_experiments` | `implementations/HANDOVER/results/07_robustness_experiments` |
| `HANDOVER/08_visual_examples_and_eda` | `implementations/HANDOVER/results/08_visual_examples_and_eda` |
| `HANDOVER/09_final_reports` | `implementations/HANDOVER/results/09_final_reports` |
| `HANDOVER/README.md` | `implementations/HANDOVER/docs/WORKSPACE.md` |
| `HANDOVER/logs` | `implementations/HANDOVER/results/logs` |
| `HANDOVER/experiments/common_support_v2/.gitignore` | `implementations/HANDOVER/experiments/common_support_v2/.gitignore` |
| `HANDOVER/experiments/common_support_v2/02_labels_and_alignment` | `implementations/HANDOVER/experiments/common_support_v2/02_labels_and_alignment` |
| `HANDOVER/experiments/common_support_v2/03_processed_model_inputs` | `implementations/HANDOVER/experiments/common_support_v2/03_processed_model_inputs` |
| `HANDOVER/experiments/common_support_v2/04_experiment_protocol` | `implementations/HANDOVER/experiments/common_support_v2/04_experiment_protocol` |
| `HANDOVER/experiments/common_support_v2/05_trained_models` | `implementations/HANDOVER/experiments/common_support_v2/05_trained_models` |
| `HANDOVER/experiments/common_support_v2/06_evaluation_results` | `implementations/HANDOVER/experiments/common_support_v2/06_evaluation_results` |
| `HANDOVER/experiments/common_support_v2/07_robustness_experiments` | `implementations/HANDOVER/experiments/common_support_v2/07_robustness_experiments` |
| `HANDOVER/experiments/common_support_v2/08_visual_examples_and_eda` | `implementations/HANDOVER/experiments/common_support_v2/08_visual_examples_and_eda` |
| `HANDOVER/experiments/common_support_v2/logs` | `implementations/HANDOVER/experiments/common_support_v2/logs` |
| `HANDOVER/99_preserved_previous_work` | `implementations/HANDOVER/docs/previous_work` |
| `REBOOT/00_dataset_overview` | `implementations/REBOOT/results/00_dataset_overview` |
| `REBOOT/02_labels_and_annotations` | `implementations/REBOOT/results/02_labels_and_annotations` |
| `REBOOT/03_video_sensor_alignment` | `implementations/REBOOT/results/03_video_sensor_alignment` |
| `REBOOT/04_visual_failure_review` | `implementations/REBOOT/results/04_visual_failure_review` |
| `REBOOT/05_architecture_compatibility` | `implementations/REBOOT/results/05_architecture_compatibility` |
| `REBOOT/06_evaluation_feasibility` | `implementations/REBOOT/results/06_evaluation_feasibility` |
| `REBOOT/07_research_decision` | `implementations/REBOOT/results/07_research_decision` |
| `REBOOT/08_visual_examples_and_eda` | `implementations/REBOOT/results/08_visual_examples_and_eda` |
| `REBOOT/README.md` | `implementations/REBOOT/docs/WORKSPACE.md` |
| `MILLING DATASET/PILOT_FINDINGS` | `implementations/MSM/experiments/legacy/PILOT_FINDINGS` |
| `MILLING DATASET/README.md` | `implementations/MSM/experiments/legacy/README.md` |
| `MILLING DATASET/runs/20261026T230520276818Z-stage1` | `implementations/MSM/experiments/legacy/runs/20261026T230520276818Z-stage1` |
| `MILLING DATASET/runs/20261026T233709740813Z-stage2/MSM_PILOT_SAMPLE_MANIFEST.csv` | `implementations/MSM/experiments/legacy/runs/20261026T233709740813Z-stage2/MSM_PILOT_SAMPLE_MANIFEST.csv` |
| `MILLING DATASET/runs/20261026T233709740813Z-stage2/cache` | `implementations/MSM/experiments/legacy/runs/20261026T233709740813Z-stage2/cache` |
| `MILLING DATASET/runs/20261026T233709740813Z-stage2/config` | `implementations/MSM/experiments/legacy/runs/20261026T233709740813Z-stage2/config` |
| `MILLING DATASET/runs/20261026T233709740813Z-stage2/evidence` | `implementations/MSM/experiments/legacy/runs/20261026T233709740813Z-stage2/evidence` |
| `MILLING DATASET/runs/20261026T233709740813Z-stage2/figures` | `implementations/MSM/experiments/legacy/runs/20261026T233709740813Z-stage2/figures` |
| `MILLING DATASET/runs/20261026T233709740813Z-stage2/logs` | `implementations/MSM/experiments/legacy/runs/20261026T233709740813Z-stage2/logs` |
| `MILLING DATASET/runs/20261026T233709740813Z-stage2/manifests` | `implementations/MSM/experiments/legacy/runs/20261026T233709740813Z-stage2/manifests` |
| `MILLING DATASET/runs/20261027T001047876764Z-stage2-validated` | `implementations/MSM/experiments/legacy/runs/20261027T001047876764Z-stage2-validated` |
| `MILLING DATASET/runs/20261027T003527238586Z-stage3` | `implementations/MSM/experiments/legacy/runs/20261027T003527238586Z-stage3` |
| `MILLING DATASET/runs/20261027T005343579234Z-stage4` | `implementations/MSM/experiments/legacy/runs/20261027T005343579234Z-stage4` |
| `MILLING DATASET/runs/20261027T010816468715Z-stage5` | `implementations/MSM/experiments/legacy/runs/20261027T010816468715Z-stage5` |
| `MILLING DATASET/runs/20261027T011419561081Z-stage5-validated` | `implementations/MSM/experiments/legacy/runs/20261027T011419561081Z-stage5-validated` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/.gitignore` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/.gitignore` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/MSM_DOWNLOAD_MANIFEST.csv` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/MSM_DOWNLOAD_MANIFEST.csv` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/cache` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/cache` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/config` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/config` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/evidence` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/evidence` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/experiments` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/experiments` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/figures` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/figures` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/logs` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/logs` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/manifests` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/manifests` |
| `MILLING DATASET/runs/20261027T013606719154Z-stage5-full-lab/provenance_initial.json` | `implementations/MSM/experiments/legacy/runs/20261027T013606719154Z-stage5-full-lab/provenance_initial.json` |
| `MILLING DATASET/runs/20261027T015205931708Z-stage5-full-lab-validated` | `implementations/MSM/experiments/legacy/runs/20261027T015205931708Z-stage5-full-lab-validated` |
| `MILLING DATASET/runs/20261027T190627566058Z-matched-visual-review` | `implementations/MSM/experiments/legacy/runs/20261027T190627566058Z-matched-visual-review` |
| `MILLING DATASET/runs/20261027T190717486889Z-matched-visual-review` | `implementations/MSM/experiments/legacy/runs/20261027T190717486889Z-matched-visual-review` |
| `runs/phm2026` | `implementations/PHM2026/results/runs/phm2026` |
| `runs/phm2026_dataset_description` | `implementations/PHM2026/results/runs/phm2026_dataset_description` |
| `runs/phm2026_evaluation` | `implementations/PHM2026/results/runs/phm2026_evaluation` |
| `runs/phm2026_fusion_latefusion` | `implementations/PHM2026/results/runs/phm2026_fusion_latefusion` |
| `runs/phm2026_image_target` | `implementations/PHM2026/results/runs/phm2026_image_target` |
| `runs/phm2026_loeo_evaluation` | `implementations/PHM2026/results/runs/phm2026_loeo_evaluation` |
| `runs/phm2026_model_dataset` | `implementations/PHM2026/results/runs/phm2026_model_dataset` |
| `runs/phm2026_monotonic_rescoring` | `implementations/PHM2026/results/runs/phm2026_monotonic_rescoring` |
| `runs/phm2026_patchtst_baseline` | `implementations/PHM2026/results/runs/phm2026_patchtst_baseline` |
| `runs/phm2026_patchtst_results` | `implementations/PHM2026/results/runs/phm2026_patchtst_results` |
| `runs/phm2026_rtdetr_detection` | `implementations/PHM2026/results/runs/phm2026_rtdetr_detection` |
| `runs/phm2026_rtdetr_multitask` | `implementations/PHM2026/results/runs/phm2026_rtdetr_multitask` |
| `runs/phm2026_rtdetr_pseudo_boxes` | `implementations/PHM2026/results/runs/phm2026_rtdetr_pseudo_boxes` |
| `runs/phm2026_rtdetr_r4_results` | `implementations/PHM2026/results/runs/phm2026_rtdetr_r4_results` |
| `runs/phm2026_rtdetr_regression` | `implementations/PHM2026/results/runs/phm2026_rtdetr_regression` |
| `runs/phm2026_rtdetr_results` | `implementations/PHM2026/results/runs/phm2026_rtdetr_results` |
| `runs/phm2026_sensor_features` | `implementations/PHM2026/results/runs/phm2026_sensor_features` |
| `runs/phm2026_target_audit` | `implementations/PHM2026/results/runs/phm2026_target_audit` |
| `runs/_superseded/phm2026_dataset_description` | `implementations/PHM2026/results/superseded/phm2026_dataset_description` |
| `runs/_superseded/phm2026_image_target` | `implementations/PHM2026/results/superseded/phm2026_image_target` |
| `runs/_superseded/phm2026_patchtst_baseline` | `implementations/PHM2026/results/superseded/phm2026_patchtst_baseline` |
| `runs/_superseded/phm2026_sensor_features` | `implementations/PHM2026/results/superseded/phm2026_sensor_features` |
| `artifacts/phm2026` | `implementations/PHM2026/results/artifacts` |
| `artifacts/intel_welding` | `implementations/INTEL_WELDING/results/artifacts` |
| `runs/intel_welding` | `implementations/INTEL_WELDING/results/runs` |
| `archive/legacy_intel_welding_dataset` | `implementations/INTEL_WELDING/experiments/legacy` |
| `artifacts/thesis` | `implementations/general/results/artifacts` |
| `runs/thesis` | `implementations/general/results/runs` |
| `artifacts/presentation` | `implementations/general/results/presentation` |
| `docs/thesis` | `implementations/general/docs/thesis` |
| `docs/repository_restructure` | `reports/extras/repository_restructure_history` |
| `experiments/phm2026` | `implementations/PHM2026/experiments/walkthrough` |
| `experiments/phm2026_dataset_description` | `implementations/PHM2026/experiments/dataset_description` |
| `experiments/phm2026_rtdetr_feasibility` | `implementations/PHM2026/experiments/rtdetr_feasibility` |
| `experiments/exp_b_eda_expA&F` | `implementations/PHM2026/experiments/exp_b_eda_expA&F` |
| `experiments/reassemble` | `implementations/REASSEMBLE/experiments/core` |
| `00_experiments` | `implementations/REASSEMBLE/experiments/additional` |
| `tutorials/EDA` | `implementations/general/scripts/eda` |
| `tutorials/presentations` | `implementations/general/docs/presentations` |
| `MA_Exposé_Ravaliya_Parth.pdf` | `implementations/general/docs/thesis/source_documents/MA_Exposé_Ravaliya_Parth.pdf` |
| `critical_literature_review.pdf` | `implementations/general/docs/thesis/source_documents/critical_literature_review.pdf` |
| `yolo26n.pt` | `implementations/general/results/pretrained/yolo26n.pt` |
| `tutorials/final_baseline_rtdetr` | `implementations/PHM2026/docs/tutorials/final_baseline_rtdetr` |
| `tutorials/patchtst_freq_baseline` | `implementations/PHM2026/docs/tutorials/patchtst_freq_baseline` |
| `tutorials/rtdetr_storybook` | `implementations/PHM2026/docs/tutorials/rtdetr_storybook` |
| `CROSS_DATASET_COMPARISON/ARCHITECTURE_COMPARISON.md` | `implementations/cross_dataset/results/ARCHITECTURE_COMPARISON.md` |
| `CROSS_DATASET_COMPARISON/FINAL_RESEARCH_SUMMARY.md` | `implementations/cross_dataset/results/FINAL_RESEARCH_SUMMARY.md` |
| `CROSS_DATASET_COMPARISON/HPO_MODEL_SELECTION_REVIEW_PACKAGE` | `implementations/cross_dataset/results/HPO_MODEL_SELECTION_REVIEW_PACKAGE` |
| `CROSS_DATASET_COMPARISON/HPO_MODEL_SELECTION_REVIEW_PACKAGE.verification.json` | `implementations/cross_dataset/results/HPO_MODEL_SELECTION_REVIEW_PACKAGE.verification.json` |
| `CROSS_DATASET_COMPARISON/HPO_MODEL_SELECTION_REVIEW_PACKAGE.zip` | `implementations/cross_dataset/results/HPO_MODEL_SELECTION_REVIEW_PACKAGE.zip` |
| `CROSS_DATASET_COMPARISON/HPO_MODEL_SELECTION_REVIEW_PACKAGE.zip.sha256` | `implementations/cross_dataset/results/HPO_MODEL_SELECTION_REVIEW_PACKAGE.zip.sha256` |
| `CROSS_DATASET_COMPARISON/HPO_MODEL_SELECTION_REVIEW_PACKAGE_V2_COHORT_RECONCILED` | `implementations/cross_dataset/results/HPO_MODEL_SELECTION_REVIEW_PACKAGE_V2_COHORT_RECONCILED` |
| `CROSS_DATASET_COMPARISON/HPO_MODEL_SELECTION_REVIEW_PACKAGE_V2_COHORT_RECONCILED.verification.json` | `implementations/cross_dataset/results/HPO_MODEL_SELECTION_REVIEW_PACKAGE_V2_COHORT_RECONCILED.verification.json` |
| `CROSS_DATASET_COMPARISON/HPO_MODEL_SELECTION_REVIEW_PACKAGE_V2_COHORT_RECONCILED.zip` | `implementations/cross_dataset/results/HPO_MODEL_SELECTION_REVIEW_PACKAGE_V2_COHORT_RECONCILED.zip` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/.gitignore` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/.gitignore` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/01_Research_Reports` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/01_Research_Reports` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/02_Experiment_Configurations` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/02_Experiment_Configurations` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/03_Dataset_And_Label_Manifests` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/03_Dataset_And_Label_Manifests` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/04_Train_Validation_Test_Splits` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/04_Train_Validation_Test_Splits` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/05_Model_Source_Code` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/05_Model_Source_Code` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/06_Model_Checkpoints_And_Training_Histories` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/06_Model_Checkpoints_And_Training_Histories` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/07_Predictions_And_OOF_Fusion` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/07_Predictions_And_OOF_Fusion` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/08_Complete_Evaluation_Metrics` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/08_Complete_Evaluation_Metrics` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/09_Robustness_Experiments` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/09_Robustness_Experiments` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/11_REASSEMBLE_Architecture_Evidence` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/11_REASSEMBLE_Architecture_Evidence` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/12_Validation_And_Reproducibility` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/12_Validation_And_Reproducibility` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/ARCHIVE_DELIVERY.json` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/ARCHIVE_DELIVERY.json` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/INDEPENDENT_REVIEW_PACKAGE.zip` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/INDEPENDENT_REVIEW_PACKAGE.zip` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/MISSING_EVIDENCE.md` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/MISSING_EVIDENCE.md` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/PACKAGE_MANIFEST.csv` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/PACKAGE_MANIFEST.csv` |
| `CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE/README_FOR_REVIEWER.md` | `implementations/cross_dataset/results/INDEPENDENT_REVIEW_PACKAGE/README_FOR_REVIEWER.md` |
| `CROSS_DATASET_COMPARISON/PERFORMANCE_COMPARISON.md` | `implementations/cross_dataset/results/PERFORMANCE_COMPARISON.md` |
| `CROSS_DATASET_COMPARISON/REASSEMBLE_COHORT_RECONCILIATION_20261103` | `implementations/cross_dataset/results/REASSEMBLE_COHORT_RECONCILIATION_20261103` |
| `CROSS_DATASET_COMPARISON/REVIEW_HANDOFF.md` | `implementations/cross_dataset/results/REVIEW_HANDOFF.md` |
| `CROSS_DATASET_COMPARISON/ROBUSTNESS_COMPARISON.md` | `implementations/cross_dataset/results/ROBUSTNESS_COMPARISON.md` |
| `CROSS_DATASET_COMPARISON/SCIENTIFIC_VERDICT_v2.md` | `implementations/cross_dataset/results/SCIENTIFIC_VERDICT_v2.md` |
| `CROSS_DATASET_COMPARISON/comparison_tables.csv` | `implementations/cross_dataset/results/comparison_tables.csv` |
| `CROSS_DATASET_COMPARISON/configs` | `implementations/cross_dataset/configs` |
| `CROSS_DATASET_COMPARISON/logs` | `implementations/cross_dataset/results/logs` |
| `CROSS_DATASET_COMPARISON/paired_comparison_tables.csv` | `implementations/cross_dataset/results/paired_comparison_tables.csv` |
| `CROSS_DATASET_COMPARISON/provenance` | `implementations/cross_dataset/results/provenance` |
| `CROSS_DATASET_COMPARISON/robustness_comparison_tables.csv` | `implementations/cross_dataset/results/robustness_comparison_tables.csv` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/.gitignore` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/.gitignore` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/DATASET_COMPARISON.md` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/DATASET_COMPARISON.md` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/FAILURE_LABEL_AUDIT.md` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/FAILURE_LABEL_AUDIT.md` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/FINAL_DATASET_RECOMMENDATION.md` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/FINAL_DATASET_RECOMMENDATION.md` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/GROUP_INDEPENDENCE_SCREENING.md` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/GROUP_INDEPENDENCE_SCREENING.md` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/NATIVE_LABEL_EXAMPLES.csv` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/NATIVE_LABEL_EXAMPLES.csv` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/OUTPUT_MANIFEST.json` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/OUTPUT_MANIFEST.json` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/README.md` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/README.md` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/RESEARCHER_HANDOFF.md` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/RESEARCHER_HANDOFF.md` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/ROBOFAC_LABEL_AUDIT.md` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/ROBOFAC_LABEL_AUDIT.md` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/SOURCE_PROVENANCE.json` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/SOURCE_PROVENANCE.json` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/VISUAL_FEASIBILITY_SCREENING.md` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/VISUAL_FEASIBILITY_SCREENING.md` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/checks` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/checks` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/code` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/code` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/config` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/config` |
| `DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/visual_screening` | `implementations/general/docs/dataset_research/NEW_DATASET_SELECTION_20261028/visual_screening` |
| `DATASET_RESEARCH/DATASET_REGISTRY.json` | `implementations/general/docs/dataset_research/DATASET_REGISTRY.json` |
| `DATASET_RESEARCH/README.md` | `implementations/general/docs/dataset_research/README.md` |
| `STORAGE_AUDIT/20261028T192446975701Z_directory_map/source` | `reports/extras/STORAGE_AUDIT/20261028T192446975701Z_directory_map/source` |
| `STORAGE_AUDIT/FINAL_CLEANUP_REPORT.md` | `reports/extras/STORAGE_AUDIT/FINAL_CLEANUP_REPORT.md` |
| `STORAGE_AUDIT/cleanup_20261028T190906Z` | `reports/extras/STORAGE_AUDIT/cleanup_20261028T190906Z` |

The complete machine-readable plan is [BULK_MOVE_MANIFEST.json](BULK_MOVE_MANIFEST.json). File metadata was collected without reading or hashing payloads; this is not a dataset-integrity audit.
