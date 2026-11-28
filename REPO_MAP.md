# Repository map

The [root README](README.md) is the academic entry point. Use the [thesis-to-code map](docs/THESIS_CODE_MAP.md) to follow an empirical section into its source, configuration, assessment and evidence; use the dataset guides for detailed procedures.

## Manuscript and review evidence

| Location | Role |
|---|---|
| [00_thesis_writing_tracking/](00_thesis_writing_tracking/README.md) | Canonical thesis navigation and state |
| [final_thesis_prep/LaTeX_Project/](00_thesis_writing_tracking/final_thesis_prep/LaTeX_Project/README.md) | Sole active manuscript; compile `main.tex`. Historical figures, supporting files and release records remain separate. |
| [Thesis/PDFs/](00_thesis_writing_tracking/Thesis/PDFs/) | Working/historical PDF outputs; use the state record to identify their version |
| [review_submissions/2026-11-26/](00_thesis_writing_tracking/review_submissions/2026-11-26/README.md) | Immutable 71-page combined source PDF for the submitted extracts |
| [scientific_cross_mapping_20261125/](00_thesis_writing_tracking/scientific_cross_mapping_20261125/README.md) | Scientific mapping, chronology, F2 checks and retained historical `applied_revision_01` assets; removed manuscript sources are recoverable through the cleanup record |
| [Historical baseline](00_thesis_writing_tracking/scientific_cross_mapping_20261125/applied_revision_01/baseline/LaTeX_Project/) | Retained November 20 supporting assets; removed manuscript sources are recoverable from the cleanup checkpoint |
| [Applied revision working snapshot](00_thesis_writing_tracking/scientific_cross_mapping_20261125/applied_revision_01/working/LaTeX_Project/) | Retained revision assets and provenance; removed manuscript sources are recoverable from the cleanup checkpoint |
| [Thesis/revision_pipeline/](00_thesis_writing_tracking/Thesis/revision_pipeline/) | Current state navigation alongside dated revision records |
| [Thesis/References/](00_thesis_writing_tracking/Thesis/References/) | Local reference/provenance material; redistribution of downloaded publications requires separate review |
| [consolidation_20261126/](00_thesis_writing_tracking/consolidation_20261126/) | Relocation receipt, hash/link checks and publication-content decisions; no commit or tag implied |

Appendix F and its [evidence source index](00_thesis_writing_tracking/final_thesis_prep/LaTeX_Project/tables/evidence_source_index.csv) use the researcher-requested 28 November numbering: E001/E002 are unchanged, former E003/E004 were removed, and former E005–E154 became E003–E152. The [publication manifest](00_thesis_writing_tracking/final_thesis_prep/evidence_publication_20261128/manifest.json) records the complete mapping. The code map is a browsing layer, not a replacement evidence register. Historical records, including the cited PHM traceability document, retain their prior evidence IDs, paths and hashes; use the migration receipt to interpret relocated names and the [source cleanup record](00_thesis_writing_tracking/final_thesis_prep/SOURCE_CLEANUP_20261128.json) for removed manuscript sources.

## Dataset and implementation navigation

| Study | Thesis role | Code, configuration and evidence entry |
|---|---|---|
| PHM2026 | Chapter 5: photographic proxy targets and sensor-group regression | [Guide](implementations/PHM2026/README.md); [complete PHM traceability](implementations/PHM2026/docs/studies/THESIS_CODE_TRACEABILITY.md) |
| REASSEMBLE | Chapter 6: completed-action classification, fusion and controlled robustness | [Guide](implementations/REASSEMBLE/README.md); [core walkthrough](implementations/REASSEMBLE/experiments/core/README.md); later studies retain their own snapshots |
| MSM | Chapter 7: milling interval classification | [Guide](implementations/MSM/README.md); shared [external evaluator](implementations/cross_dataset/src/external_eval/) |
| ViFailback | Chapter 8: completed-episode classification and partial matched CNN study | [Guide](implementations/VIFAILBACK/README.md); [preserved original workspace guide](implementations/VIFAILBACK/docs/WORKSPACE_BEFORE_CONSOLIDATION.md) |
| HANDOVER | Appendix H: common-support assessment and participant-identity gate | [Guide](implementations/HANDOVER/README.md) |
| Intel Welding | Original application; historical modelling and later failed foundation gates | [Guide](implementations/INTEL_WELDING/README.md) |
| PADERBORN | Bearing-mechanism feasibility; evaluation protocol fork | [Guide](implementations/PADERBORN/README.md) |
| REBOOT | Annotation/alignment/visual-observability feasibility; supervised comparison not admitted | [Guide](implementations/REBOOT/README.md) |
| Cross-dataset | Synthesis and shared implementation, preserving separate tasks and metrics | [Guide](implementations/cross_dataset/README.md) |
| General | Original exposé, dataset discovery, maintenance and historical research records | [Guide](implementations/general/README.md) |

Each dataset guide links inputs/labels, preparation, architecture, protocol, saved assessment and limitations. Completed, unsuccessful, exploratory and unfinished work retain their study-local status. A script's presence is not evidence that an experiment ran. Dataset-specific fitting, learned-weight transfer and zero-shot evaluation are different claims.

## Protected locations and dependencies

The approved native-input destinations are [HANDOVER inputs](implementations/HANDOVER/01_raw_dataset/), [REBOOT inputs](implementations/REBOOT/01_raw_dataset/), [legacy milling data](implementations/MSM/experiments/legacy/data/) and [ViFailback originals](implementations/VIFAILBACK/01_original_dataset/). MSM input records remain at [01_raw_dataset/](implementations/MSM/01_raw_dataset/); its repaired `official_dataset` link resolves to the retained legacy dataset tree. The [one-off relocation receipt](implementations/general/docs/repository_history/root_cleanup_20261126/approved_relocation/README.md) covers the exact eleven approved groups, including raw/source material, frozen studies and initial PHM EDA. Content, provenance and stopped-study protections remain in force at their new locations. Protected PHM `gtc-data-experiment/**` and Intel `data/Full Dataset/**` were outside that scope and retain their protected identities even when absent.

`implementations/` is the canonical physical study structure. Root `src/` retains compatibility links to the PHM2026, REASSEMBLE, Intel Welding and shared external-evaluation packages. [ViFailback](implementations/VIFAILBACK/README.md) now owns its physical workspace. REASSEMBLE retains [phase-one feedback](implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback/) and [bootstrap studies](implementations/REASSEMBLE/experiments/bootstrap/00_experimentation/); initial PHM EDA is at [its preserved experiment directory](implementations/PHM2026/experiments/exp_a_initial_eda_r1_r3_r5/), and [REBOOT runs](implementations/REBOOT/runs/) retain feasibility evidence. Historical manifests keep original names such as `26.10.2026_feedback_experiments/` and `parth_ws_bootstrap/`; current navigation resolves their physical destinations.

Frozen source and output identities are preserved, not regenerated. Direct frozen-study CLI calls require an explicit relocation context: consult the [REASSEMBLE activation guide](implementations/general/docs/repository_history/root_cleanup_20261126/approved_relocation/reassemble_adapter/README.md), [ViFailback activation guide](implementations/VIFAILBACK/relocation/README.md) and [legacy consumer limits](implementations/general/docs/repository_history/root_cleanup_20261126/approved_relocation/vifailback_adapter/LEGACY_CONSUMER_LIMITS.md). Literal string I/O and child-process paths are not universally translated; these checks establish bounded path compatibility, not full historical replay.

## History, retrieval and policy

- [November 26 thesis consolidation](00_thesis_writing_tracking/consolidation_20261126/) records the approved local changes and publication dependencies.
- [November 26 root cleanup](implementations/general/docs/repository_history/root_cleanup_20261126/README.md) retains the earlier model-audit, maintenance-document and Handover-link phases. The later [approved eleven-group relocation](implementations/general/docs/repository_history/root_cleanup_20261126/approved_relocation/README.md) records physical consolidation, identity preservation and bounded adapter checks.
- [November 25 broader physical move proposal](implementations/general/docs/repository_history/final_consolidation_20261125/MOVE_PLAN.md) is an earlier proposal, not an instruction to move dataset implementations now.
- [November 24 organization checks](implementations/general/docs/repository_history/post_report_cleanup_20261124/STATUS.json) and [change record](implementations/general/docs/repository_history/post_report_cleanup_20261124/CHANGES.json) describe that earlier scope.
- [Earlier dataset consolidation](implementations/general/docs/repository_history/dataset_layout_cleanup.json) and [physical path mapping](implementations/general/docs/repository_history/physical_restructure_20261119/PATH_MAPPING.json) resolve older source names.
- [PHM raw recovery](implementations/PHM2026/docs/RAW_DATA_RECOVERY.md), dataset-native acquisition records and [REASSEMBLE cache retention](implementations/REASSEMBLE/docs/maintenance/REASSEMBLE_CACHE_RETENTION.md) distinguish retained evidence from external or regenerable payloads.

Relocation, link checks and recomputation of saved metrics do not reproduce training. Scope, data and retention decisions remain governed by [AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md), [data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md). Later task-specific research authorization does not silently amend the PHM-centred scope document.
