# MSM and ViFailback publication selection

Prepared 27 November 2026. Only the two selection files in this reviews directory were written. No ignore rules, Git index, manuscript, experiment source or retained result bytes were changed. No experiments, inference, raw scans, restores or checkpoint reads occurred.

## Selection

The companion JSON contains **2020 include decisions** (217199746 bytes in total; largest file 4969217 bytes), plus 10 explicit exclusion/representative rows. All 131 prior audit support paths are included.

- MSM: 971 files, 205325667 bytes.
- shared audited source: 6 files, 55203 bytes.
- VIFAILBACK: 1043 files, 11818876 bytes.

MSM coverage includes all 54 compressed score-only prediction tables across the retained label/grouping sensitivities, their 54 case receipts, per-case metrics and training diagnostics; aggregate clean/pooled/paired/bootstrap/robustness tables; gate allocations; runtime/loss summaries; cohort/alignment/split manifests; all compact fit and stacking-lineage receipts; final reports and prior audited implementation sources. F2 coefficient JSON and gate receipts are readable small evidence, not model pickle/checkpoint payloads. Prediction headers contain scores and identities, not input feature vectors.

ViFailback coverage includes original final reports and dated compact report/metric snapshots; matched model/protocol/source provenance; split and pilot-role checks; learning-curve identities; final/before/after-stop evidence and independent-verification records; compact performance/optimization reports and verification summaries. Historical snapshots remain dated evidence and must not be presented as the latest completed scope. Missing ViFailback per-fit prediction/calibrator/receipt/history artifacts were not recovered or rerun. The previously audited snapshot replacements remain the available numerical support.

Every included path exists and is at most 10 MiB. New CSV/gzip files were inspected by header and a bounded row; JSON was parsed for structure and bounded value inspection; text was inspected through bounded excerpts and prior audit knowledge. This classifies publication roles, not a new scientific correctness or secret-scanning certification. Source/media payloads were excluded before content reads.

## Exclusions and scope

- ignore-rule: 2 encountered files excluded.
- temporary-or-telemetry: 1095 encountered files excluded.
- binary-cache-model-or-media: 827 encountered files excluded.
- engineered-feature-table: 1 encountered files excluded.
- conversation-or-workspace-dump: 2 encountered files excluded.
- unrequested-code: 34 encountered files excluded.

`implementations/MSM/results/03_processed_model_inputs/interval_statistics.csv` is excluded despite its small size: its columns are engineered sensor feature values, not predictions. NPZ/numerical caches, checkpoint/model binary formats, generated images/HTML previews, `.writing` files, logs and JSONL telemetry remain excluded. Full conversation/workspace dumps are not selected. Directory pruning excluded raw dataset links/trees, acquired media, feature/cache directories, sample previews and logs before traversal. No source images or example signal arrays are selected. The selection does retain compact example score tables and frame-reference manifests, which contain metadata but no image bytes.

The JSON lists representative binary/temporary exclusions rather than every redundant intermediate file; those omitted files are not selected. Current final result roots were reviewed; the separate legacy MSM raw/feasibility tree was not traversed.

## Ignore constraints for the parent

- Root `.gitignore` excludes `*.csv`, model/cache formats and logs. Keep these broad protections; add exact reviewed file exceptions only.
- `implementations/MSM/results/.gitignore` excludes `/06_evaluation_results/predictions/`, `/05_trained_models/` and `/08_visual_examples_and_eda/prediction_examples/`. Exact selected descendants require explicit ancestor reopening at this scoped file, while maintaining default exclusion of other contents. The same-named rules in `implementations/MSM/.gitignore` apply to older direct-domain paths, not the nested `results/` paths.
- ViFailback domain ignores original fit/result runtime roots and generated media. The matched-study `.gitignore` also excludes runtime directories, per-condition fit trees and live `11_metrics_and_statistics/*.json`. Selected final/before/after-stop snapshots remain at their actual dated paths; they do not justify unignoring absent live outputs.
- The nested independent-verification ignore protects source evidence, checks and gallery/unblinding assets. No reopening of those source/media/answer-key trees is proposed.
- Parent owns all allowlist/index changes and final security/publication review. No commit or push has been made or requested by this selection step.
