# Current project directory map

Measured 2026-10-28 20:29:00 CET. Project root: `pi-multimodal-ad/`.

**245,183 regular file paths · 17,831 directories · 69.60 GiB of file storage · 74 symbolic links.**

Counts include all descendants, hidden files and ignored files. Sizes use binary units (1 GiB = 1,073,741,824 bytes). The tree shows allocated regular-file blocks, with hard links counted once within each folder. The table also shows logical file bytes (the sum of file lengths, counting every path). Directory and symlink metadata blocks are excluded. Parent values already include children: do not add parent and child rows. Shared hard links can also overlap between sibling folders. Symlinks are listed without following their targets; their target files are not counted again. Private-file contents were never opened; this report lists groups instead of individual file names.

The scan read directory entries and file metadata only. It did not open datasets, archives, checkpoints or credentials. The new report directory `STORAGE_AUDIT/20261028T192446975701Z_directory_map/` is excluded from its own snapshot. Concurrent jobs may change file counts or sizes after this scan.

## Top-level folders

| Folder | Content | Files, recursive | File storage on disk | Logical size |
|---|---|---:|---:|---:|
| `.cache/` | Preserved local caches | 86 | 1.64 MiB | 1.47 MiB |
| `.git/` | Git history and repository metadata | 3,549 | 14.81 GiB | 14.80 GiB |
| `.github/` | Repository contribution instructions | 1 | 4.00 KiB | 2.94 KiB |
| `.pytest_cache/` | Pytest cache | 5 | 52.00 KiB | 35.54 KiB |
| `.vscode/` | Editor configuration | 1 | 4.00 KiB | 38 B |
| `00_experiments/` | REASSEMBLE follow-up studies and comparisons | 96,779 | 6.72 GiB | 6.44 GiB |
| `26.10.2026_feedback_experiments/` | CNN benchmarks, fine-tuning and seed-stability studies | 5,660 | 3.96 GiB | 3.94 GiB |
| `archive/` | Preserved legacy code and research records | 9 | 48.00 KiB | 25.19 KiB |
| `artifacts/` | Curated figures, reports and thesis evidence | 481 | 480.73 MiB | 479.66 MiB |
| `configs/` | Dataset and experiment configurations | 31 | 164.00 KiB | 101.61 KiB |
| `CROSS_DATASET_COMPARISON/` | Cross-dataset evaluation, synthesis and review export | 8,761 | 2.52 GiB | 2.50 GiB |
| `data/` | Supplementary datasets currently stored here | 10 | 59.01 MiB | 58.99 MiB |
| `DATASET_RESEARCH/` | Dataset navigation links and registry | 2 | 8.00 KiB | 1.68 KiB |
| `docs/` | Policies, methodology, research notes and indexes | 433 | 70.20 MiB | 69.24 MiB |
| `experiments/` | Historical EDA and numbered experiment walkthroughs | 323 | 352.39 MiB | 351.73 MiB |
| `HANDOVER/` | Handover raw inputs, evaluation and research evidence | 17,370 | 16.14 GiB | 32.09 GiB |
| `ma_thesis_env/` | Installed Python environment and libraries | 60,656 | 6.69 GiB | 6.55 GiB |
| `MILLING DATASET/` | Historical MSM acquisition, pilots and source data | 2,586 | 4.06 GiB | 7.55 GiB |
| `MSM/` | Final MSM evaluation and research evidence | 6,708 | 1.33 GiB | 2.37 GiB |
| `parth_ws_bootstrap/` | Original REASSEMBLE workspace and experiment history | 11,751 | 443.92 MiB | 416.75 MiB |
| `REBOOT/` | REBOOT feasibility audit and blinded visual-review pilot | 1,954 | 3.34 GiB | 3.34 GiB |
| `runs/` | Versioned PHM, REASSEMBLE, Intel and thesis outputs | 27,316 | 8.47 GiB | 8.41 GiB |
| `scratch/` | Existing scratch and exploratory inspection outputs | 92 | 48.84 MiB | 48.67 MiB |
| `scripts/` | Command-line research and maintenance scripts | 167 | 1.77 MiB | 1.35 MiB |
| `src/` | Domain-owned implementation and compatibility wrappers | 213 | 2.15 MiB | 1.64 MiB |
| `STORAGE_AUDIT/` | Dated storage and directory-map snapshots | 38 | 6.18 MiB | 6.11 MiB |
| `tests/` | Validation code and synthetic fixtures | 57 | 368.00 KiB | 240.01 KiB |
| `tutorials/` | Tutorials, baseline demonstrations and presentations | 132 | 117.36 MiB | 117.05 MiB |
| Files directly in project root | Root documents, scripts, configuration, model and local files | 12 | 5.78 MiB | 5.76 MiB |

## Condensed directory tree

Each `[grouped]` branch represents every descendant beneath that folder. Repeated sessions, model outputs, raw files and installed packages are summarized by their complete counts and sizes. The CSV inventory contains a measurement for every scanned directory if a deeper lookup is needed.

```text
pi-multimodal-ad/  245,183 files; 69.60 GiB on disk; 74 links
├── .cache/  86 files; 1.64 MiB on disk — Preserved local caches [grouped]
├── .git/  3,549 files; 14.81 GiB on disk — Git history and repository metadata [grouped]
├── .github/  1 file; 4.00 KiB on disk — Repository contribution instructions
├── .pytest_cache/  5 files; 52.00 KiB on disk — Pytest cache [grouped]
├── .vscode/  1 file; 4.00 KiB on disk — Editor configuration
├── 00_experiments/  96,779 files; 6.72 GiB on disk; 8 links — REASSEMBLE follow-up studies and comparisons
│   ├── adaptive_fusion_robustness/  82,464 files; 841.17 MiB on disk — REASSEMBLE adaptive fusion robustness study
│   │   ├── code/  15 files; 120.00 KiB on disk — Study source code
│   │   ├── results/  82,443 files; 841.01 MiB on disk — Saved experiment results [grouped]
│   │   ├── tests/  3 files; 12.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 3; 32.00 KiB on disk]
│   ├── completed_reassemble_work_git_handoff_01/  40 files; 388.00 KiB on disk — REASSEMBLE completed reassemble work git handoff 01 study
│   │   ├── before/  9 files; 32.00 KiB on disk — before files
│   │   ├── checks/  5 files; 36.00 KiB on disk — checks files
│   │   ├── commits/  15 files; 144.00 KiB on disk — commits files
│   │   ├── selection/  6 files; 108.00 KiB on disk — selection files
│   │   └── [files directly here: 5; 68.00 KiB on disk]
│   ├── frozen32_vs_finetuned32_fusion_diagnosis/  1,096 files; 3.38 GiB on disk — REASSEMBLE frozen32 vs finetuned32 fusion diagnosis study
│   │   ├── code/  7 files; 92.00 KiB on disk — Study source code
│   │   ├── data_manifests/  4 files; 15.98 MiB on disk — Dataset and sample identities
│   │   ├── existing_evidence/  4 files; 16.00 KiB on disk — existing evidence files
│   │   ├── git_handoff/  14 files; 1.30 MiB on disk — git handoff files
│   │   ├── results/  1,034 files; 3.36 GiB on disk — Saved experiment results [grouped]
│   │   ├── tests/  24 files; 468.00 KiB on disk — Validation code and fixtures [grouped]
│   │   └── [files directly here: 9; 236.00 KiB on disk]
│   ├── fusion_noise_test/  1,939 files; 151.23 MiB on disk — REASSEMBLE fusion noise test study
│   │   ├── code/  9 files; 100.00 KiB on disk — Study source code
│   │   ├── results/  1,923 files; 151.05 MiB on disk — Saved experiment results [grouped]
│   │   ├── tests/  1 file; 16.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 6; 68.00 KiB on disk]
│   ├── rt_detr_encoder_comparison/  9,706 files; 398.56 MiB on disk — REASSEMBLE rt detr encoder comparison study
│   │   ├── code/  7 files; 88.00 KiB on disk — Study source code
│   │   ├── results/  9,694 files; 398.41 MiB on disk — Saved experiment results [grouped]
│   │   ├── tests/  1 file; 12.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 4; 52.00 KiB on disk]
│   └── visual_backbone_one_day/  1,534 files; 1.99 GiB on disk; 8 links — REASSEMBLE visual backbone one day study
│       ├── fine_tuning_diagnostics_01/  54 files; 20.45 MiB on disk — fine tuning diagnostics 01 files [grouped]
│       ├── fusion_AP_explanation_addendum_01/  121 files; 45.09 MiB on disk — fusion AP explanation addendum 01 files [grouped]
│       ├── run_01_two_epoch_finetuning/  1,358 files; 1.93 GiB on disk; 8 links — run 01 two epoch finetuning files [grouped]
│       └── [files directly here: 1; 4.00 KiB on disk]
├── 26.10.2026_feedback_experiments/  5,660 files; 3.96 GiB on disk — CNN benchmarks, fine-tuning and seed-stability studies
│   ├── 26102026_phase1_full_cnn_seed_stability/  5,480 files; 2.54 GiB on disk — 26102026 phase1 full cnn seed stability files
│   │   ├── 26102026_bestfit_100epoch_frozen_vs_full_cnn/  438 files; 590.53 MiB on disk — 26102026 bestfit 100epoch frozen vs full cnn files [grouped]
│   │   ├── 26102026_c_only_20epoch_revision_01/  45 files; 173.22 MiB on disk — 26102026 c only 20epoch revision 01 files [grouped]
│   │   ├── 26102026_configuration/  1 file; 4.00 KiB on disk — 26102026 configuration files
│   │   ├── 26102026_evidence/  17 files; 17.78 MiB on disk — 26102026 evidence files
│   │   ├── 26102026_execution/  4,955 files; 1.78 GiB on disk — 26102026 execution files [grouped]
│   │   ├── 26102026_reports/  7 files; 44.00 KiB on disk — 26102026 reports files
│   │   ├── 26102026_source/  12 files; 116.00 KiB on disk — 26102026 source files
│   │   ├── 26102026_tests/  2 files; 16.00 KiB on disk — 26102026 tests files
│   │   └── [files directly here: 3; 16.00 KiB on disk]
│   ├── configs/  1 file; 4.00 KiB on disk — Configuration files
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── runs/  167 files; 1.42 GiB on disk — Versioned study runs and provenance
│   │   ├── 20261026T212550Z-934ad6c7/  63 files; 540.15 MiB on disk — 20261026T212550Z-934ad6c7 files [grouped]
│   │   ├── 20261026T213457Z-stream-a8efd0e8/  33 files; 342.57 MiB on disk — 20261026T213457Z-stream-a8efd0e8 files [grouped]
│   │   ├── 20261026T214258Z-stream-ca88704c/  37 files; 342.62 MiB on disk — 20261026T214258Z-stream-ca88704c files [grouped]
│   │   └── 20261026T215300Z-selected16-e15865ad/  34 files; 231.43 MiB on disk — 20261026T215300Z-selected16-e15865ad files [grouped]
│   ├── source/  8 files; 68.00 KiB on disk — Study source code
│   │   └── [files directly here: 8; 68.00 KiB on disk]
│   ├── tests/  1 file; 4.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   └── [files directly here: 3; 28.00 KiB on disk]
├── archive/  9 files; 48.00 KiB on disk — Preserved legacy code and research records
│   ├── legacy_intel_welding_dataset/  8 files; 44.00 KiB on disk — legacy intel welding dataset files
│   └── [files directly here: 1; 4.00 KiB on disk]
├── artifacts/  481 files; 480.73 MiB on disk — Curated figures, reports and thesis evidence
│   ├── intel_welding/  40 files; 2.18 MiB on disk — intel welding artifacts files [grouped]
│   ├── phm2026/  16 files; 220.00 KiB on disk — phm2026 artifacts files [grouped]
│   ├── presentation/  83 files; 60.12 MiB on disk — presentation files [grouped]
│   ├── reassemble/  54 files; 1.80 MiB on disk — REASSEMBLE artifacts files [grouped]
│   └── thesis/  288 files; 416.41 MiB on disk — thesis artifacts files [grouped]
├── configs/  31 files; 164.00 KiB on disk — Dataset and experiment configurations
│   ├── datasets/  1 file; 4.00 KiB on disk — datasets files
│   ├── experiments/  21 files; 96.00 KiB on disk — experiments files
│   ├── intel_welding/  1 file; 4.00 KiB on disk — intel welding configs files
│   ├── phm2026/  1 file; 28.00 KiB on disk — phm2026 configs files
│   └── reassemble/  7 files; 32.00 KiB on disk — REASSEMBLE configs files [grouped]
├── CROSS_DATASET_COMPARISON/  8,761 files; 2.52 GiB on disk — Cross-dataset evaluation, synthesis and review export
│   ├── configs/  4 files; 16.00 KiB on disk — Configuration files
│   │   └── [files directly here: 4; 16.00 KiB on disk]
│   ├── INDEPENDENT_REVIEW_PACKAGE/  8,597 files; 2.51 GiB on disk — Complete independent-review evidence and ZIP archive
│   │   ├── 01_Research_Reports/  95 files; 46.12 MiB on disk — Exported 01 Research Reports evidence [grouped]
│   │   ├── 02_Experiment_Configurations/  51 files; 356.00 KiB on disk — Exported 02 Experiment Configurations evidence [grouped]
│   │   ├── 03_Dataset_And_Label_Manifests/  2,899 files; 243.72 MiB on disk — Exported 03 Dataset And Label Manifests evidence [grouped]
│   │   ├── 04_Train_Validation_Test_Splits/  16 files; 1.98 MiB on disk — Exported 04 Train Validation Test Splits evidence [grouped]
│   │   ├── 05_Model_Source_Code/  218 files; 2.53 MiB on disk — Exported 05 Model Source Code evidence [grouped]
│   │   ├── 06_Model_Checkpoints_And_Training_Histories/  879 files; 124.32 MiB on disk — Exported 06 Model Checkpoints And Training Histories evidence [grouped]
│   │   ├── 07_Predictions_And_OOF_Fusion/  447 files; 185.96 MiB on disk — Exported 07 Predictions And OOF Fusion evidence [grouped]
│   │   ├── 08_Complete_Evaluation_Metrics/  153 files; 8.69 MiB on disk — Exported 08 Complete Evaluation Metrics evidence [grouped]
│   │   ├── 09_Robustness_Experiments/  298 files; 42.89 MiB on disk — Exported 09 Robustness Experiments evidence [grouped]
│   │   ├── 10_Visual_And_Sensor_Examples/  1,613 files; 470.10 MiB on disk — Exported 10 Visual And Sensor Examples evidence [grouped]
│   │   ├── 11_REASSEMBLE_Architecture_Evidence/  1,049 files; 108.05 MiB on disk — Exported 11 REASSEMBLE Architecture Evidence evidence [grouped]
│   │   ├── 12_Validation_And_Reproducibility/  873 files; 219.27 MiB on disk — Exported 12 Validation And Reproducibility evidence [grouped]
│   │   └── [files directly here: 6; 1.09 GiB on disk]
│   ├── logs/  21 files; 216.00 KiB on disk — Run logs
│   │   └── [files directly here: 21; 216.00 KiB on disk]
│   ├── provenance/  104 files; 1.04 MiB on disk — Source and execution provenance
│   │   ├── source_snapshot/  74 files; 940.00 KiB on disk — source snapshot files [grouped]
│   │   └── [files directly here: 30; 120.00 KiB on disk]
│   ├── src/  21 files; 280.00 KiB on disk — Source code
│   │   └── external_eval/  21 files; 280.00 KiB on disk — external eval files [grouped]
│   ├── tests/  4 files; 16.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 4; 16.00 KiB on disk]
│   └── [files directly here: 10; 96.00 KiB on disk]
├── data/  10 files; 59.01 MiB on disk — Supplementary datasets currently stored here
│   ├── paderborn/  3 files; 3.35 MiB on disk — paderborn dataset files
│   ├── rawvib/  6 files; 55.65 MiB on disk — rawvib dataset files
│   └── [files directly here: 1; 4.00 KiB on disk]
├── DATASET_RESEARCH/  2 files; 8.00 KiB on disk; 4 links — Dataset navigation links and registry
│   ├── HANDOVER@ → ../HANDOVER [link; target files not counted again]
│   ├── MILLING_DATASET@ → ../MILLING DATASET [link; target files not counted again]
│   ├── MSM@ → ../MSM [link; target files not counted again]
│   ├── REBOOT@ → ../REBOOT [link; target files not counted again]
│   └── [files directly here: 2; 8.00 KiB on disk]
├── docs/  433 files; 70.20 MiB on disk — Policies, methodology, research notes and indexes
│   ├── intel_welding/  5 files; 36.00 KiB on disk — intel welding docs files
│   ├── maintenance/  14 files; 38.70 MiB on disk — maintenance files [grouped]
│   ├── phm2026/  1 file; 12.00 KiB on disk — phm2026 docs files
│   ├── planning/  17 files; 204.00 KiB on disk — planning files
│   ├── reassemble/  17 files; 168.00 KiB on disk — REASSEMBLE docs files
│   ├── repository_restructure/  224 files; 20.40 MiB on disk — repository restructure files [grouped]
│   ├── thesis/  29 files; 472.00 KiB on disk — thesis docs files
│   ├── thesis_research_direction/  15 files; 460.00 KiB on disk — thesis research direction files
│   ├── thesis_review_handoff/  107 files; 9.37 MiB on disk — thesis review handoff files [grouped]
│   └── [files directly here: 4; 420.00 KiB on disk]
├── experiments/  323 files; 352.39 MiB on disk; 36 links — Historical EDA and numbered experiment walkthroughs
│   ├── exp_a_initial_eda_r1_r3_r5/  279 files; 352.18 MiB on disk — exp a initial eda r1 r3 r5 files [grouped]
│   ├── exp_b_eda_expA&F/  0 files; 0 B on disk — exp b eda expA&F files
│   ├── phm2026/  13 files; 64.00 KiB on disk; 10 links — phm2026 experiments files
│   │   ├── 01_rtdetr_scalar_regression/  10 files; 40.00 KiB on disk; 10 links — 01 rtdetr scalar regression files [grouped]
│   │   └── [files directly here: 3; 24.00 KiB on disk]
│   ├── phm2026_dataset_description/  1 file; 4.00 KiB on disk — phm2026 dataset description files
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── phm2026_rtdetr_feasibility/  1 file; 4.00 KiB on disk — phm2026 rtdetr feasibility files
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── reassemble/  28 files; 136.00 KiB on disk; 26 links — REASSEMBLE experiments files
│   │   ├── 01_rtdetr_baseline/  8 files; 32.00 KiB on disk; 8 links — 01 rtdetr baseline files [grouped]
│   │   ├── 02_patchtst_baseline/  8 files; 32.00 KiB on disk; 9 links — 02 patchtst baseline files [grouped]
│   │   ├── 03_core_fusion/  9 files; 36.00 KiB on disk; 9 links — 03 core fusion files [grouped]
│   │   └── [files directly here: 3; 36.00 KiB on disk]
│   └── [files directly here: 1; 16.00 KiB on disk]
├── HANDOVER/  17,370 files; 16.14 GiB on disk; 8 links — Handover raw inputs, evaluation and research evidence
│   ├── 01_raw_dataset/  13,146 files; 15.69 GiB on disk — Raw dataset files and source metadata
│   │   ├── official_dataset/  13,092 files; 15.62 GiB on disk — Original dataset files [grouped]
│   │   ├── source_evidence/  52 files; 64.52 MiB on disk — source evidence files [grouped]
│   │   └── [files directly here: 2; 8.00 KiB on disk]
│   ├── 02_labels_and_alignment/  1,189 files; 9.67 MiB on disk; 1 links — Labels, sample manifests and alignment evidence
│   │   ├── trial_checkpoints/  1,178 files; 6.59 MiB on disk — trial checkpoints files
│   │   ├── active_common_support_v2@ → ../experiments/common_support_v2/02_labels_and_alignment [link; target files not counted again]
│   │   └── [files directly here: 11; 3.09 MiB on disk]
│   ├── 03_processed_model_inputs/  5 files; 1.05 MiB on disk; 1 links — Derived features, model inputs and split manifests
│   │   ├── sensor_features/  1 file; 344.00 KiB on disk — sensor features files
│   │   ├── split_manifests/  2 files; 24.00 KiB on disk — split manifests files
│   │   ├── visual_features/  0 files; 0 B on disk — visual features files
│   │   ├── active_common_support_v2@ → ../experiments/common_support_v2/03_processed_model_inputs [link; target files not counted again]
│   │   └── [files directly here: 2; 704.00 KiB on disk]
│   ├── 04_experiment_protocol/  4 files; 20.00 KiB on disk; 1 links — Experiment configuration and methodology
│   │   ├── active_common_support_v2@ → ../experiments/common_support_v2/04_experiment_protocol [link; target files not counted again]
│   │   └── [files directly here: 4; 20.00 KiB on disk]
│   ├── 05_trained_models/  1 file; 4.00 KiB on disk; 1 links — Fitted models, scalers and training histories
│   │   ├── adaptive_fusion_if_applicable/  0 files; 0 B on disk — adaptive fusion if applicable files
│   │   ├── averaging_fusion/  0 files; 0 B on disk — averaging fusion files
│   │   ├── f2_fusion/  0 files; 0 B on disk — f2 fusion files
│   │   ├── sensor_only/  0 files; 0 B on disk — sensor only files
│   │   ├── visual_only/  0 files; 0 B on disk — visual only files
│   │   ├── active_common_support_v2@ → ../experiments/common_support_v2/05_trained_models [link; target files not counted again]
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── 06_evaluation_results/  1 file; 4.00 KiB on disk; 1 links — Predictions, metrics and evaluation figures
│   │   ├── calibration/  0 files; 0 B on disk — calibration files
│   │   ├── confusion_matrices/  0 files; 0 B on disk — confusion matrices files
│   │   ├── metrics/  0 files; 0 B on disk — metrics files
│   │   ├── precision_recall_curves/  0 files; 0 B on disk — precision recall curves files
│   │   ├── predictions/  0 files; 0 B on disk — predictions files
│   │   ├── active_common_support_v2@ → ../experiments/common_support_v2/06_evaluation_results [link; target files not counted again]
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── 07_robustness_experiments/  1 file; 4.00 KiB on disk; 1 links — Corruption policies and robustness results
│   │   ├── comparison_reports/  0 files; 0 B on disk — comparison reports files
│   │   ├── degraded_video/  0 files; 0 B on disk — degraded video files
│   │   ├── missing_modalities/  0 files; 0 B on disk — missing modalities files
│   │   ├── noisy_sensors/  0 files; 0 B on disk — noisy sensors files
│   │   ├── active_common_support_v2@ → ../experiments/common_support_v2/07_robustness_experiments [link; target files not counted again]
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── 08_visual_examples_and_eda/  1 file; 4.00 KiB on disk; 1 links — Representative inputs and exploratory figures
│   │   ├── prediction_examples/  0 files; 0 B on disk — prediction examples files
│   │   ├── sample_previews/  0 files; 0 B on disk — sample previews files
│   │   ├── sensor_visualizations/  0 files; 0 B on disk — sensor visualizations files
│   │   ├── active_common_support_v2@ → ../experiments/common_support_v2/08_visual_examples_and_eda [link; target files not counted again]
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── 09_final_reports/  15 files; 540.00 KiB on disk — Final scientific reports
│   │   └── [files directly here: 15; 540.00 KiB on disk]
│   ├── 99_preserved_previous_work/  1 file; 4.00 KiB on disk — Links or records preserving earlier work
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── experiments/  2,992 files; 451.82 MiB on disk; 1 links — experiments files
│   │   └── common_support_v2/  2,992 files; 451.82 MiB on disk; 1 links — common support v2 files [grouped]
│   ├── logs/  6 files; 964.00 KiB on disk — Run logs
│   │   └── [files directly here: 6; 964.00 KiB on disk]
│   ├── src/  5 files; 68.00 KiB on disk — Source code
│   │   ├── __pycache__/  1 file; 28.00 KiB on disk — Python bytecode cache
│   │   └── [files directly here: 4; 40.00 KiB on disk]
│   ├── tests/  1 file; 4.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   └── [files directly here: 2; 8.00 KiB on disk]
├── ma_thesis_env/  60,656 files; 6.69 GiB on disk; 4 links — Installed Python environment and libraries [grouped]
├── MILLING DATASET/  2,586 files; 4.06 GiB on disk — Historical MSM acquisition, pilots and source data
│   ├── .tools/  21 files; 76.27 MiB on disk — .tools files [grouped]
│   ├── configs/  3 files; 12.00 KiB on disk — Configuration files
│   │   └── [files directly here: 3; 12.00 KiB on disk]
│   ├── data/  516 files; 3.48 GiB on disk — data files
│   │   └── raw/  516 files; 3.48 GiB on disk — raw files [grouped]
│   ├── PILOT_FINDINGS/  97 files; 4.95 MiB on disk — PILOT FINDINGS files
│   │   ├── 01_DATASET_AND_LABEL_AUDIT/  7 files; 72.00 KiB on disk — 01 DATASET AND LABEL AUDIT files [grouped]
│   │   ├── 02_VIDEO_ALIGNMENT_AND_MODALITIES/  9 files; 60.00 KiB on disk — 02 VIDEO ALIGNMENT AND MODALITIES files [grouped]
│   │   ├── 03_ARCHITECTURE_IMPLEMENTATION_SMOKE/  7 files; 56.00 KiB on disk — 03 ARCHITECTURE IMPLEMENTATION SMOKE files [grouped]
│   │   ├── 04_BLOCKED_EVALUATION_AND_TRANSFER/  7 files; 44.00 KiB on disk — 04 BLOCKED EVALUATION AND TRANSFER files [grouped]
│   │   ├── 05_FULL_LABORATORY_FEASIBILITY/  61 files; 4.66 MiB on disk — 05 FULL LABORATORY FEASIBILITY files [grouped]
│   │   ├── 06_MATCHED_CUT_REVIEW/  2 files; 8.00 KiB on disk — 06 MATCHED CUT REVIEW files
│   │   └── [files directly here: 4; 64.00 KiB on disk]
│   ├── runs/  1,896 files; 3.98 GiB on disk — Versioned study runs and provenance [grouped]
│   ├── source/  44 files; 736.00 KiB on disk — Study source code
│   │   ├── __pycache__/  4 files; 128.00 KiB on disk — Python bytecode cache
│   │   ├── msm/  12 files; 140.00 KiB on disk — msm files
│   │   ├── stage2/  13 files; 120.00 KiB on disk — stage2 files
│   │   └── [files directly here: 15; 348.00 KiB on disk]
│   ├── tests/  7 files; 44.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 7; 44.00 KiB on disk]
│   └── [files directly here: 2; 8.00 KiB on disk]
├── MSM/  6,708 files; 1.33 GiB on disk; 2 links — Final MSM evaluation and research evidence
│   ├── 01_raw_dataset/  4 files; 76.00 KiB on disk; 1 links — Raw dataset files and source metadata
│   │   ├── source_evidence/  2 files; 4.00 KiB on disk — source evidence files
│   │   ├── official_dataset@ → ../../MILLING DATASET/data/raw/msm/versions/2 [link; target files not counted again]
│   │   └── [files directly here: 2; 72.00 KiB on disk]
│   ├── 02_labels_and_alignment/  11 files; 13.44 MiB on disk — Labels, sample manifests and alignment evidence
│   │   └── [files directly here: 11; 13.44 MiB on disk]
│   ├── 03_processed_model_inputs/  4,341 files; 1,003.57 MiB on disk — Derived features, model inputs and split manifests
│   │   ├── sensor_features/  541 files; 43.33 MiB on disk — sensor features files [grouped]
│   │   ├── split_manifests/  2 files; 1.68 MiB on disk — split manifests files
│   │   ├── visual_features/  3,796 files; 955.23 MiB on disk — visual features files [grouped]
│   │   └── [files directly here: 2; 3.34 MiB on disk]
│   ├── 04_experiment_protocol/  8 files; 36.00 KiB on disk — Experiment configuration and methodology
│   │   └── [files directly here: 8; 36.00 KiB on disk]
│   ├── 05_trained_models/  1,566 files; 199.02 MiB on disk — Fitted models, scalers and training histories
│   │   ├── adaptive_fusion_if_applicable/  0 files; 0 B on disk — adaptive fusion if applicable files
│   │   ├── averaging_fusion/  0 files; 0 B on disk — averaging fusion files
│   │   ├── f2_fusion/  702 files; 94.59 MiB on disk — f2 fusion files [grouped]
│   │   ├── sensor_only/  54 files; 16.93 MiB on disk — sensor only files [grouped]
│   │   └── visual_only/  810 files; 87.49 MiB on disk — visual only files [grouped]
│   ├── 06_evaluation_results/  562 files; 104.98 MiB on disk — Predictions, metrics and evaluation figures
│   │   ├── calibration/  1 file; 8.00 KiB on disk — calibration files
│   │   ├── confusion_matrices/  0 files; 0 B on disk — confusion matrices files
│   │   ├── figures/  4 files; 992.00 KiB on disk — figures files
│   │   ├── metrics/  63 files; 4.99 MiB on disk — metrics files
│   │   ├── precision_recall_curves/  0 files; 0 B on disk — precision recall curves files
│   │   ├── predictions/  486 files; 98.87 MiB on disk — predictions files [grouped]
│   │   └── [files directly here: 8; 144.00 KiB on disk]
│   ├── 07_robustness_experiments/  3 files; 1.16 MiB on disk — Corruption policies and robustness results
│   │   ├── comparison_reports/  1 file; 128.00 KiB on disk — comparison reports files
│   │   ├── degraded_video/  0 files; 0 B on disk — degraded video files
│   │   ├── missing_modalities/  0 files; 0 B on disk — missing modalities files
│   │   ├── noisy_sensors/  0 files; 0 B on disk — noisy sensors files
│   │   └── [files directly here: 2; 1.03 MiB on disk]
│   ├── 08_visual_examples_and_eda/  181 files; 40.18 MiB on disk — Representative inputs and exploratory figures
│   │   ├── prediction_examples/  177 files; 40.05 MiB on disk — prediction examples files [grouped]
│   │   ├── sample_previews/  0 files; 0 B on disk — sample previews files
│   │   ├── sensor_visualizations/  0 files; 0 B on disk — sensor visualizations files
│   │   └── [files directly here: 4; 128.00 KiB on disk]
│   ├── 09_final_reports/  15 files; 1.02 MiB on disk — Final scientific reports
│   │   └── [files directly here: 15; 1.02 MiB on disk]
│   ├── 99_preserved_previous_work/  0 files; 0 B on disk; 1 links — Links or records preserving earlier work
│   │   └── MILLING_DATASET@ → ../../MILLING DATASET [link; target files not counted again]
│   ├── logs/  10 files; 72.00 KiB on disk — Run logs
│   │   └── [files directly here: 10; 72.00 KiB on disk]
│   ├── src/  3 files; 16.00 KiB on disk — Source code
│   │   └── [files directly here: 3; 16.00 KiB on disk]
│   ├── tests/  1 file; 8.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 1; 8.00 KiB on disk]
│   └── [files directly here: 3; 12.00 KiB on disk]
├── parth_ws_bootstrap/  11,751 files; 443.92 MiB on disk; 4 links — Original REASSEMBLE workspace and experiment history
│   ├── 00_Experimentaitons/  3 files; 112.00 KiB on disk — 00 Experimentaitons files
│   ├── 00_experimentation/  9,542 files; 432.92 MiB on disk — 00 experimentation files
│   │   └── visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/  9,542 files; 432.92 MiB on disk — visual backbone f2 frozen vs final stage 16 vs 32 frames files [grouped]
│   ├── controller_builds/  1,534 files; 6.87 MiB on disk; 3 links — controller builds files
│   │   └── 20261019T220330Z/  1,534 files; 6.87 MiB on disk; 3 links — 20261019T220330Z files [grouped]
│   ├── outputs/  31 files; 336.00 KiB on disk — outputs files
│   │   └── 20261019T213827Z-audit/  31 files; 336.00 KiB on disk — 20261019T213827Z-audit files [grouped]
│   ├── prompts/  2 files; 12.00 KiB on disk — prompts files
│   │   └── [files directly here: 2; 12.00 KiB on disk]
│   ├── work_sessions/  628 files; 3.57 MiB on disk; 1 links — work sessions files
│   │   └── 20261019T222548Z-decision-session-fusion-evidence-literature-offline-runner/  628 files; 3.57 MiB on disk; 1 links — 20261019T222548Z-decision-session-fusion-evidence-literature-offline-runner files [grouped]
│   └── [files directly here: 11; 108.00 KiB on disk]
├── REBOOT/  1,954 files; 3.34 GiB on disk — REBOOT feasibility audit and blinded visual-review pilot
│   ├── 00_dataset_overview/  9 files; 1.06 MiB on disk — 00 dataset overview files
│   │   └── [files directly here: 9; 1.06 MiB on disk]
│   ├── 01_raw_dataset/  257 files; 2.75 GiB on disk — Raw dataset files and source metadata
│   │   ├── official_release/  238 files; 2.75 GiB on disk — Pinned REBOOT dataset files [grouped]
│   │   ├── remote_range_evidence/  16 files; 264.00 KiB on disk — Original byte-range acquisition evidence [grouped]
│   │   └── [files directly here: 3; 240.00 KiB on disk]
│   ├── 02_labels_and_annotations/  5 files; 140.00 KiB on disk — Native annotations and label audits
│   │   └── [files directly here: 5; 140.00 KiB on disk]
│   ├── 03_video_sensor_alignment/  41 files; 9.54 MiB on disk — Numerical projections and video alignment evidence
│   │   ├── decoder_probe/  17 files; 4.68 MiB on disk — decoder probe files
│   │   ├── numerical_projections/  20 files; 3.54 MiB on disk — numerical projections files [grouped]
│   │   └── [files directly here: 4; 1.32 MiB on disk]
│   ├── 04_visual_failure_review/  1,458 files; 591.04 MiB on disk — Real frames, video previews and blinded review materials
│   │   ├── galleries/  1,451 files; 590.98 MiB on disk — galleries files [grouped]
│   │   └── [files directly here: 7; 64.00 KiB on disk]
│   ├── 05_architecture_compatibility/  1 file; 4.00 KiB on disk — Architecture compatibility evidence
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   ├── 06_evaluation_feasibility/  4 files; 24.00 KiB on disk — Grouping, duplicate and evaluation feasibility evidence
│   │   └── [files directly here: 4; 24.00 KiB on disk]
│   ├── 07_research_decision/  3 files; 16.00 KiB on disk — Research decision and researcher handoff
│   │   └── [files directly here: 3; 16.00 KiB on disk]
│   ├── runs/  167 files; 3.29 MiB on disk — Versioned study runs and provenance
│   │   ├── 20261028T113139848361Z-independent-feasibility-v1/  162 files; 2.88 MiB on disk — 20261028T113139848361Z-independent-feasibility-v1 files [grouped]
│   │   └── 20261028T192832Z-research-blockers-v2/  5 files; 412.00 KiB on disk — 20261028T192832Z-research-blockers-v2 files [grouped]
│   ├── src/  6 files; 100.00 KiB on disk — Source code
│   │   └── [files directly here: 6; 100.00 KiB on disk]
│   ├── tests/  1 file; 4.00 KiB on disk — Validation code and fixtures
│   │   └── [files directly here: 1; 4.00 KiB on disk]
│   └── [files directly here: 2; 8.00 KiB on disk]
├── runs/  27,316 files; 8.47 GiB on disk; 8 links — Versioned PHM, REASSEMBLE, Intel and thesis outputs
│   ├── _superseded/  1,598 files; 614.47 MiB on disk —  superseded files [grouped]
│   ├── intel_welding/  18 files; 1.67 MiB on disk — intel welding runs files [grouped]
│   ├── phm2026/  24 files; 2.16 MiB on disk — PHM 2026  outputs [grouped]
│   ├── phm2026_dataset_description/  99 files; 164.31 MiB on disk — PHM 2026 dataset description outputs [grouped]
│   ├── phm2026_evaluation/  11 files; 888.00 KiB on disk — PHM 2026 evaluation outputs [grouped]
│   ├── phm2026_fusion_latefusion/  6 files; 36.00 KiB on disk — PHM 2026 fusion latefusion outputs [grouped]
│   ├── phm2026_image_target/  2,782 files; 1.17 GiB on disk — PHM 2026 image target outputs [grouped]
│   ├── phm2026_loeo_evaluation/  8 files; 44.00 KiB on disk — PHM 2026 loeo evaluation outputs [grouped]
│   ├── phm2026_model_dataset/  21 files; 7.22 MiB on disk — PHM 2026 model dataset outputs [grouped]
│   ├── phm2026_monotonic_rescoring/  12 files; 96.00 KiB on disk — PHM 2026 monotonic rescoring outputs [grouped]
│   ├── phm2026_patchtst_baseline/  166 files; 13.43 MiB on disk — PHM 2026 patchtst baseline outputs [grouped]
│   ├── phm2026_patchtst_results/  58 files; 3.52 MiB on disk — PHM 2026 patchtst results outputs [grouped]
│   ├── phm2026_rtdetr_detection/  67 files; 708.79 MiB on disk — PHM 2026 rtdetr detection outputs [grouped]
│   ├── phm2026_rtdetr_multitask/  85 files; 340.95 MiB on disk — PHM 2026 rtdetr multitask outputs [grouped]
│   ├── phm2026_rtdetr_pseudo_boxes/  2,029 files; 676.46 MiB on disk — PHM 2026 rtdetr pseudo boxes outputs [grouped]
│   ├── phm2026_rtdetr_r4_results/  19 files; 416.00 KiB on disk — PHM 2026 rtdetr r4 results outputs [grouped]
│   ├── phm2026_rtdetr_regression/  61 files; 103.57 MiB on disk — PHM 2026 rtdetr regression outputs [grouped]
│   ├── phm2026_rtdetr_results/  78 files; 42.23 MiB on disk — PHM 2026 rtdetr results outputs [grouped]
│   ├── phm2026_sensor_features/  46 files; 56.23 MiB on disk — PHM 2026 sensor features outputs [grouped]
│   ├── phm2026_target_audit/  29 files; 1.69 MiB on disk — PHM 2026 target audit outputs [grouped]
│   ├── reassemble/  20,089 files; 4.63 GiB on disk; 8 links — REASSEMBLE experiment files [grouped]
│   ├── thesis/  9 files; 88.00 KiB on disk — thesis runs files [grouped]
│   └── [files directly here: 1; 8.00 KiB on disk]
├── scratch/  92 files; 48.84 MiB on disk — Existing scratch and exploratory inspection outputs
│   └── blind_inspection/  92 files; 48.84 MiB on disk — blind inspection files [grouped]
├── scripts/  167 files; 1.77 MiB on disk — Command-line research and maintenance scripts
│   ├── __pycache__/  20 files; 380.00 KiB on disk — Python bytecode cache
│   ├── dataset/  6 files; 24.00 KiB on disk — dataset files
│   ├── features/  2 files; 8.00 KiB on disk — features files
│   ├── intel_welding/  6 files; 72.00 KiB on disk — intel welding scripts files
│   ├── ops/  4 files; 40.00 KiB on disk — ops files [grouped]
│   ├── paderborn/  9 files; 72.00 KiB on disk — paderborn files [grouped]
│   ├── phm2026/  40 files; 472.00 KiB on disk — phm2026 scripts files [grouped]
│   ├── presentation/  1 file; 120.00 KiB on disk — presentation files
│   ├── rawvib/  7 files; 88.00 KiB on disk — rawvib files [grouped]
│   ├── reassemble/  28 files; 164.00 KiB on disk — REASSEMBLE scripts files [grouped]
│   ├── results/  17 files; 68.00 KiB on disk — Saved experiment results
│   ├── targets/  8 files; 32.00 KiB on disk — targets files
│   ├── thesis/  13 files; 248.00 KiB on disk — thesis scripts files [grouped]
│   └── training/  6 files; 24.00 KiB on disk — training files
├── src/  213 files; 2.15 MiB on disk — Domain-owned implementation and compatibility wrappers
│   ├── intel_welding/  8 files; 4.00 KiB on disk — intel welding src files [grouped]
│   ├── phm2026/  58 files; 908.00 KiB on disk — phm2026 src files [grouped]
│   ├── pi_multimodal_ad/  56 files; 224.00 KiB on disk — pi multimodal ad files [grouped]
│   └── reassemble/  91 files; 1.04 MiB on disk — REASSEMBLE src files [grouped]
├── STORAGE_AUDIT/  38 files; 6.18 MiB on disk — Dated storage and directory-map snapshots
│   ├── 20261028T114917Z/  10 files; 288.00 KiB on disk — 20261028T114917Z files
│   ├── 20261028T115408Z/  10 files; 296.00 KiB on disk — 20261028T115408Z files
│   ├── cleanup_20261028T190906Z/  17 files; 5.60 MiB on disk — cleanup 20261028T190906Z files [grouped]
│   └── [files directly here: 1; 16.00 KiB on disk]
├── tests/  57 files; 368.00 KiB on disk — Validation code and synthetic fixtures
│   ├── compatibility/  3 files; 16.00 KiB on disk — compatibility files
│   ├── fixtures/  5 files; 20.00 KiB on disk — fixtures files [grouped]
│   ├── intel_welding/  1 file; 4.00 KiB on disk — intel welding tests files
│   ├── ops/  1 file; 4.00 KiB on disk — ops files
│   ├── phm2026/  30 files; 228.00 KiB on disk — phm2026 tests files
│   ├── reassemble/  14 files; 84.00 KiB on disk — REASSEMBLE tests files [grouped]
│   └── thesis/  3 files; 12.00 KiB on disk — thesis tests files [grouped]
├── tutorials/  132 files; 117.36 MiB on disk — Tutorials, baseline demonstrations and presentations
│   ├── EDA/  8 files; 5.70 MiB on disk — EDA files
│   ├── final_baseline_rtdetr/  31 files; 4.41 MiB on disk — final baseline rtdetr files [grouped]
│   ├── patchtst_freq_baseline/  54 files; 8.65 MiB on disk — patchtst freq baseline files [grouped]
│   ├── presentations/  2 files; 9.38 MiB on disk — presentations files
│   └── rtdetr_storybook/  37 files; 89.22 MiB on disk — rtdetr storybook files [grouped]
└── [files directly in project root: 12; 5.78 MiB on disk]
```

## Where the dataset work lives

| Study | Main locations | Interpretation |
|---|---|---|
| REASSEMBLE | `src/reassemble/`, `scripts/reassemble/`, `configs/reassemble/`, `runs/reassemble/`, `artifacts/reassemble/`, `experiments/reassemble/`, `00_experiments/`, `parth_ws_bootstrap/`, `26.10.2026_feedback_experiments/` | Implementation, walkthroughs, original experiments and later CNN/fusion studies; raw inputs may be referenced outside this project. |
| MSM / Milling | `MSM/`, `MILLING DATASET/` | Current MSM evaluation plus preserved acquisition and pilot evidence for the same dataset. |
| Handover | `HANDOVER/` | Native inputs, labels, evaluation, robustness and reports. |
| REBOOT | `REBOOT/` | Independent feasibility pilot, source audit and blinded visual review. |
| PHM 2026 | `src/phm2026/`, `scripts/phm2026/`, `configs/`, `runs/phm2026*/`, `artifacts/phm2026/`, `experiments/` | PHM implementations and historical/current research outputs. |
| Intel welding | `src/intel_welding/`, `scripts/intel_welding/`, `runs/intel_welding/`, `artifacts/intel_welding/`, `archive/` | Implementation, audit evidence and historical work. Folder existence does not imply raw data are present. |
| Shared navigation | `DATASET_RESEARCH/` | Links to MSM, Milling, Handover and REBOOT; no extra copies of those datasets. |
| Cross-dataset review | `CROSS_DATASET_COMPARISON/` | Shared external evaluation and the independent-review export. |

## Relevant links and external inputs

Links below retain their original locations. External targets are named only by their final component; their contents were not traversed or included in project totals.

| Link | Target | Target location | Exists at scan |
|---|---|---|---|
| `00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/original_features` | `../../../../parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/original_features` | Inside project | Yes |
| `00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/pixels` | `../../../../parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/pixels` | Inside project | Yes |
| `00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/shared_cache/preparation` | `../../../../parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/shared_cache/preparation` | Inside project | Yes |
| `DATASET_RESEARCH/HANDOVER` | `../HANDOVER` | Inside project | Yes |
| `DATASET_RESEARCH/MILLING_DATASET` | `../MILLING DATASET` | Inside project | Yes |
| `DATASET_RESEARCH/MSM` | `../MSM` | Inside project | Yes |
| `DATASET_RESEARCH/REBOOT` | `../REBOOT` | Inside project | Yes |
| `HANDOVER/02_labels_and_alignment/active_common_support_v2` | `../experiments/common_support_v2/02_labels_and_alignment` | Inside project | Yes |
| `HANDOVER/03_processed_model_inputs/active_common_support_v2` | `../experiments/common_support_v2/03_processed_model_inputs` | Inside project | Yes |
| `HANDOVER/04_experiment_protocol/active_common_support_v2` | `../experiments/common_support_v2/04_experiment_protocol` | Inside project | Yes |
| `HANDOVER/05_trained_models/active_common_support_v2` | `../experiments/common_support_v2/05_trained_models` | Inside project | Yes |
| `HANDOVER/06_evaluation_results/active_common_support_v2` | `../experiments/common_support_v2/06_evaluation_results` | Inside project | Yes |
| `HANDOVER/07_robustness_experiments/active_common_support_v2` | `../experiments/common_support_v2/07_robustness_experiments` | Inside project | Yes |
| `HANDOVER/08_visual_examples_and_eda/active_common_support_v2` | `../experiments/common_support_v2/08_visual_examples_and_eda` | Inside project | Yes |
| `HANDOVER/experiments/common_support_v2/01_raw_dataset` | `../../01_raw_dataset` | Inside project | Yes |
| `MSM/01_raw_dataset/official_dataset` | `../../MILLING DATASET/data/raw/msm/versions/2` | Inside project | Yes |
| `MSM/99_preserved_previous_work/MILLING_DATASET` | `../../MILLING DATASET` | Inside project | Yes |

## Snapshot checks

- All 17,832 scanned directory records reconcile with the root file and byte totals.
- 300 directory branches are printed; other descendants are covered by their grouped parent and the complete CSV.
- 0 metadata access/change warnings; 0 special filesystem entries.
- Hard-link repeats: 11,682. Unique regular-file content is 69.01 GiB; unique regular-file allocated blocks occupy 69.60 GiB. These exclude directory blocks and external link targets.
- Whole filesystem at scan: 74.38 GiB free of 494.92 GiB. This is filesystem capacity, not this project’s size.
- Existing files, experiments and running jobs were left unchanged. No training or cleanup was run.

Companion files: `DIRECTORY_INVENTORY.csv` (every scanned directory), `SYMLINK_INVENTORY.json`, `PROVENANCE.json`, `config/resolved_config.json`, `validation.json` and `source/build_directory_map.py`.
