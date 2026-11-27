# GitHub supporting-evidence upload plan

27 November 2026. Identification only: no upload, commit, staging, ignore-rule change or LaTeX link insertion has been performed. Current files were compared with actual remote `main` at `40f3f7ecea292c13fd1b2906b64e2654c281071b`, rather than relying on a stale local remote-tracking ref. The review branch is at `2ae0c76e3d377a0fae3361c00f2e7d65f704545a`.

## What is already published and what is missing

The full [CSV inventory](supporting_file_inventory.csv) / [JSON inventory](supporting_file_inventory.json) records each exact path, claim/section, role, priority, size, SHA-256, Git blob identity, local tracking/ignore rule, both remote-branch comparisons and inspection limits. Existing-file availability is separated from unresolved historical pointers.

| Chapter | Selected existing files | Identical on main | Core additions | Additional supporting files | Optional inputs absent |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5 — PHM | 73 | 53 | 7 | 13 | 0 |
| 6 — REASSEMBLE | 138 | 46 | 7 | 8 | 77 |
| 7 — MSM | 83 | 20 | 7 | 1 | 55 |
| 8 — ViFailback | 48 | 48 | 0 | 0 | 0 |
| Total | 342 | 167 | 21 | 22 | 132 |

**Recommended first publication scope:** the 21 missing core files (1.75 MiB), plus the 22 additional supporting files (5.67 MiB) where their documented claim needs that input. These 43 files total 7.42 MiB. Existing reports need no duplicate upload. The 132 optional files total 146.27 MiB and are separately inventoried; they are not necessary to start linking report-level claims.

All 21 core files and 21 of the additional supporting files are ignored locally. The remaining supporting item is the untracked `00_thesis_writing_tracking/empirical_revision_20261127_01/reassemble_arithmetic.json`. Future tracking should use exact paths with lineage, not blanket unignoring of result directories. No source paths or historical files need moving.

## Exact core additions

Every row below is absent from both checked remote branches. The [core CSV](core_files_to_add.csv) includes the claim mapping and exact ignore rule. “Core” identifies the direct numerical/report support selected for the current chapters, not a claim that every row alone reproduces its experiment.

### Chapter 5 — PHM

- `implementations/PHM2026/docs/studies/ANOMALYDINO_SWEEP.csv` — 937 bytes.
- `implementations/PHM2026/docs/tutorials/patchtst_freq_baseline/analysis/ablation_output/ablation_comparison.csv` — 1,405 bytes.
- `implementations/PHM2026/docs/tutorials/patchtst_freq_baseline/training_output/test_predictions.csv` — 355 bytes.
- `implementations/PHM2026/results/runs/phm2026_patchtst_baseline/20260814T121641338050Z-433d4154/tables/metrics.csv` — 6,359 bytes.
- `implementations/PHM2026/results/runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af/tables/detection_metrics.csv` — 2,129 bytes.
- `implementations/PHM2026/results/runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099/tables/scalar_metrics.csv` — 2,652 bytes.
- `implementations/PHM2026/results/runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/metrics.csv` — 3,346 bytes.

### Chapter 6 — REASSEMBLE

- `implementations/REASSEMBLE/experiments/additional/adaptive_fusion_robustness/results/run_01/comparison/model_comparison.csv` — 1,204 bytes.
- `implementations/REASSEMBLE/experiments/additional/adaptive_fusion_robustness/results/run_01/comparison/paired_intervals.csv` — 4,090 bytes.
- `implementations/REASSEMBLE/experiments/additional/adaptive_fusion_robustness/results/run_01/comparison/per_condition_metrics.csv` — 68,922 bytes.
- `implementations/REASSEMBLE/experiments/additional/rt_detr_encoder_comparison/results/run_01/comparison/metrics.csv` — 6,927 bytes.
- `implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/PHASE1_100EPOCH_COMPARISON_METRICS.json` — 1,502 bytes.
- `implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/PHASE1_COMPARISON_PROCESS_ATTEMPTS.json` — 2,757 bytes.
- `implementations/REASSEMBLE/results/runs/followup_exploratory_studies/representation_and_robustness_studies/02_patchtst_training_budget/hybrid_comparison/metrics.csv` — 413 bytes.

### Chapter 7 — MSM

- `implementations/MSM/results/04_experiment_protocol/group_split_inventory.csv` — 7,784 bytes.
- `implementations/MSM/results/06_evaluation_results/metrics/clean_seed_summary.csv` — 6,851 bytes.
- `implementations/MSM/results/06_evaluation_results/metrics/paired_group_bootstrap_95ci.csv` — 61,626 bytes.
- `implementations/MSM/results/06_evaluation_results/metrics/paired_seed_differences.csv` — 39,172 bytes.
- `implementations/MSM/results/06_evaluation_results/metrics/pooled_heldout_metrics.csv` — 1,062,322 bytes.
- `implementations/MSM/results/06_evaluation_results/metrics/training_diagnostic_AP.csv` — 31,950 bytes.
- `implementations/MSM/results/07_robustness_experiments/robustness_metrics.csv` — 524,845 bytes.

### Chapter 8 — ViFailback

No additions among the selected existing core files. The unavailable per-fit ViFailback inputs remain a separate recovery gap, not an upload-ready bundle.

## Existing report entry points

These are already on main with identical local bytes. They are useful readable entry points, while the CSV/JSON artifacts supply the exact figures. Some historical reports contain broader claims than the current thesis accepts; retain the qualifications documented in the chapter reviews.

| Chapter | Report paths already available |
| --- | --- |
| 5 | `implementations/PHM2026/docs/studies/THESIS_CODE_TRACEABILITY.md`, `TARGET_VERSION_LEDGER.md`, `TARGET_AND_FUSION_INITIAL_STUDY.md` |
| 6 | `implementations/REASSEMBLE/results/artifacts/reports/SECTION_1_UNIMODAL_HANDOFF.md`, `SECTION_2_FUSION_HANDOFF.md`, `SECTION_3_ROBUSTNESS_HANDOFF.md`, `ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md` |
| 7 | `implementations/MSM/results/09_final_reports/EXPERIMENT_RESULTS.md`, `ROBUSTNESS_RESULTS.md`, `SCIENTIFIC_INTERPRETATION_v2.md`, `REPRODUCIBILITY.md` |
| 8 | `implementations/VIFAILBACK/10_final_research_reports/06_UNIMODAL_BASELINE_RESULTS.md`, `07_FUSION_RESULTS.md`; matched-study `14_final_research_reports/01_EXECUTIVE_SUMMARY.md` and the final stopped-study snapshot identified below |

Basenames grouped in a row share the preceding directory. The inventory expands all paths exactly.

## Additional support and optional numerical inputs

The [22-file supporting addition list](additional_supporting_files_to_add.csv) contains PHM derived target/prediction tables, REASSEMBLE diagnostic/timing/cohort support and the MSM admitted-sample manifest. Keep these distinct from the 21 direct core additions. Files marked `inspected=false` were identified as contextual dependencies but were not independently content-audited in this pass; that flag is preserved rather than inferred from adjacent checks.

The [132-file optional list](optional_audit_inputs_not_on_main.csv) contains REASSEMBLE predictions and resource receipts plus MSM prediction inputs/example metadata. In particular, the 54 MSM compressed prediction tables total about 88 MiB. These permit deeper numerical review but include derived labels and source/group identifiers; review the exact selected fields against dataset redistribution terms before publication. Reading them for this audit did not grant permission to publish them. No raw videos, frames, sensor payloads, feature caches or checkpoints are included.

The complete inventory also contains optional historical reports already published. Optional priority describes their necessity for this task, not scientific quality.

## Missing historical pointers and evidence to recover

- E057–E060: four missing REASSEMBLE handoff files under `docs/thesis_review_handoff/REASSEMBLE_FINETUNING_CURRENT_STATUS_20261110_02/`: `03_COMPLETE_MODEL_CONFIGURATIONS.csv`, `09_MATCHED_COMPARISON_AND_UNCERTAINTY.md`, `12_CURRENT_25_VS_75_FIT_STATUS.md`, `14_UNRESOLVED_EVIDENCE.md`. Current C20 fit index/predictions/timing and C100 comparison/attempt receipts are identified in the inventory. They support the current numbers but do not recover the exact historical validator/cache narrative.

- E095: the old live ViFailback result path is absent. The retained, already published file is `implementations/VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/18_fit_stop_and_analysis_20261124T1955Z/final_evidence/11_metrics_and_statistics/CURRENT_RESULTS.json`. Its SHA-256 is `9bd34a5cd02c3dcfbfa7f580b3d1cf7c4da5461f22ad65a12f83bd98b05e89c2`. Use that actual snapshot as the eventual link target.

- E108: `thesis_manuscript/evidence/external_dataset_results.json` was not found. Existing domain reports can support the relevant summary, but must not be called the same missing inventory.

- ViFailback: per-fit artifacts referenced for all 79 completed fits are absent locally, including predictions, completion/configuration/history records; relevant fusion/original evaluation outputs are also absent. Retain the compact final evidence and state this limitation. Current local files cannot support a promise of fresh metric/F2/calibration replay.

- PHM fixed-fusion interval: its historical report remains available, but per-run test predictions supporting that particular confidence interval were not located. This is separate from the independently checked principal LOEO predictions.

## Later publication sequence

1. Resolve the explicit source/provenance qualifications in the [audit report](AUDIT_REPORT.md), preserving historical records. Choose the exact core/supporting files above; keep optional numerical inputs a separate decision.
2. Add an evidence index connecting chapter claims to the exact report, compact metric, protocol and verification receipt. Include known missing artifacts and distinguish fresh arithmetic from historical report correspondence. The current CSV/JSON inventories supply that mapping.
3. When publication is authorized, add only the chosen exact paths with appropriate tracking rules, commit and verify their remote availability/bytes. Do not bulk-upload this audit directory: its `before/` snapshots and remote-tree dumps are local working records.
4. Only after that publication check, create commit-pinned GitHub links in the LaTeX sources. Use the published commit and actual snapshot paths, and preserve current chapter qualifications.

This pass completes steps of evidence identification and verification only. It creates no GitHub repository changes or thesis hyperlinks.
