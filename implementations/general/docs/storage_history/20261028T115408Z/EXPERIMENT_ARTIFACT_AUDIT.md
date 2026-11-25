# Experiment artifact audit

Audit `20261028T115408Z` · 2026-10-28T12:54:08+01:00. Read-only assessment; no cleanup or downloads initiated by this audit. Concurrent REBOOT work is identified separately. GB/MB are decimal; GiB/MiB are binary. Directory sizes are allocated blocks, with hard links counted once per subtree and symlinks not followed.

## Artifact classes in the largest-file inventory

| Class | Top-100 path entries | Logical size of entries (not savings) |
| --- | --- | --- |
| A Raw datasets | 26 | 30.506 GB |
| B Processed datasets | 1 | 0.159 GB |
| C Extracted CNN features | 0 | 0.000 GB |
| D Model checkpoints | 50 | 6.604 GB |
| E Predictions and evaluation outputs | 0 | 0.000 GB |
| F Visualizations and videos | 0 | 0.000 GB |
| G Archives and backups | 3 | 1.498 GB |
| H Python environments and caches | 17 | 4.177 GB |
| I Other | 3 | 15.817 GB |

Zero entries in a class means it is absent from the top 100, not absent from the project. Classification of raw acquisition staging is based on purpose, not CSV extension. Raw archives stay in class A. The top-100 list includes hard-link aliases and Git internals, so its logical total is not additive disk usage.

## Retention decisions

| Path / artifact | Allocated | Status and evidence | Consequence of removal |
| --- | --- | --- | --- |
| 26.10.2026_feedback_experiments | 4.247 GB | RED: live comparison controller/training and workers; PHASE1_ACTIVE_REVISION identifies 100-epoch comparison and C-only continuation | Breaks current execution/recovery and possibly later automatic continuation |
| 00_experiments | 7.235 GB | RED: learned models, optimizer states, robustness exports and comparison evidence | Breaks model/prediction/result provenance; similarly sized fitted folds are distinct |
| runs/reassemble | 4.974 GB | RED default: completed and partial historical run evidence, models and predictions | Breaks thesis and methodological traceability |
| runs/_superseded | 0.645 GB | RED default: superseded target/run evidence is still protected | Loses recorded versions; superseded does not mean disposable |
| experiments/exp_a_initial_eda_r1_r3_r5 | 0.369 GB | RED explicitly protected historical EDA | No validated replacement/approval established |
| MSM/03_processed_model_inputs/visual_features | 1.002 GB | YELLOW: 3,796 feature/cache files; frozen extraction code and provenance retained | Future replay requires isolated feature regeneration and parity check |
| HANDOVER/experiments/common_support_v2/03_processed_model_inputs/visual_features | 0.308 GB | YELLOW: 1,180 feature/cache files; current raw inputs and saved fit/prediction evidence retained | Future replay requires matching camera/frame policy and corruption features |
| CROSS_DATASET_COMPARISON/INDEPENDENT_REVIEW_PACKAGE | 2.710 GB | RED curated expanded payload; YELLOW only the separate ZIP | Contains unique guides/projections/review validation, not all recreated by copying source |
| parth_ws_bootstrap | 0.471 GB | RED: newer workspaces symlink to saved manifests/features and shared cache metadata | Removing old workspace breaks newer workflows |
| scratch | 0.051 GB | UNKNOWN: provenance and regeneration not certified | Could be only local source-derived evidence after PHM raw retirement |
| ma_thesis_env | 7.215 GB | RED active environment; installed CUDA libraries are runtime dependencies | Breaks running work or future reproduction |
| .cache/repository_restructure | 0.002 GB | YELLOW old relocated bytecode; validate original-source/preimage correspondence first | Historical migration evidence may depend on preservation |

The October 26 cache eviction already removed 7,241 arrays (~66.9 GiB). Frozen-prefix JSON identities and pixel manifests remain; completion flags are historical. Do not count those absent arrays, remove retained metadata or run old training drivers to regenerate them. Prefix regeneration needs a new isolated cache-only runner and ~43.2 GiB plus headroom; see `docs/maintenance/REASSEMBLE_CACHE_RETENTION.md`.

## Live process evidence

At 2026-10-28T11:40:52.617232+00:00, same-UID /proc inspection found 11 project writer processes (including inherited log descriptors), controller PID 2691799, training PID 2823659 and Python/data-loader workers. At least four data workers had external encoded-media MP4 inputs open. No process was stopped or restarted. Three process-access permission errors limit visibility; lack of an open descriptor is not proof a path is unused. Command lines, environment values, session contents and mapped memory were not read.

| PID | Name | Observed project write paths |
| --- | --- | --- |
| 2691799 | python | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/PHASE1_COMPARISON_CONTROLLER.log; 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/PHASE1_COMPARISON_SINGLE_WRITER.lock; 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_execution/26102026_main_run_01/PHASE1_SINGLE_WRITER.lock; 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2823659 | python | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2823718 | python | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2823722 | pt_data_worker | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2823786 | pt_data_worker | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2823826 | pt_data_worker | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2823865 | pt_data_worker | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2834331 | pt_data_worker | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2834383 | pt_data_worker | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2834400 | pt_data_worker | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |
| 2834418 | pt_data_worker | 26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_logs/PHASE1_C_full_finetuned16_ATTEMPT003.log |

Detailed read/write path observations are retained in `AUDIT_PROVENANCE.json`. Final process identities are time-specific; recheck them before any later cleanup. No scientific regeneration, decoder run, checkpoint load or training was performed.
