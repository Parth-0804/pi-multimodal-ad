# Repository map

The [root README](README.md) is the academic entry point. Use the [thesis-to-code map](docs/THESIS_CODE_MAP.md) to follow an empirical section into its source, configuration, assessment and evidence; use the dataset guides for detailed procedures.

## Manuscript and review evidence

| Location | Role |
|---|---|
| [00_thesis_writing_tracking/](00_thesis_writing_tracking/README.md) | Canonical thesis navigation and state |
| [Thesis/LaTeX_Project/](00_thesis_writing_tracking/Thesis/LaTeX_Project/README.md) | Sole authoritative working manuscript; `main.tex`, `review.tex`, `manav_review.tex` and chapter-preview entry points |
| [Thesis/PDFs/](00_thesis_writing_tracking/Thesis/PDFs/) | Working/historical PDF outputs; use the state record to identify their version |
| [review_submissions/2026-11-26/](00_thesis_writing_tracking/review_submissions/2026-11-26/README.md) | Immutable 71-page combined source PDF for the submitted extracts |
| [scientific_cross_mapping_20261125/](00_thesis_writing_tracking/scientific_cross_mapping_20261125/README.md) | Scientific mapping, chronology, F2 checks and the complete historical `applied_revision_01` package |
| [Historical baseline](00_thesis_writing_tracking/scientific_cross_mapping_20261125/applied_revision_01/baseline/LaTeX_Project/) | Preserved November 20 manuscript; not a current working copy |
| [Applied revision working snapshot](00_thesis_writing_tracking/scientific_cross_mapping_20261125/applied_revision_01/working/LaTeX_Project/) | Preserved revision provenance; current editing belongs in the canonical project above |
| [Thesis/revision_pipeline/](00_thesis_writing_tracking/Thesis/revision_pipeline/) | Current state navigation alongside dated revision records |
| [Thesis/References/](00_thesis_writing_tracking/Thesis/References/) | Local reference/provenance material; redistribution of downloaded publications requires separate review |
| [consolidation_20261126/](00_thesis_writing_tracking/consolidation_20261126/) | Relocation receipt, hash/link checks and publication-content decisions; no commit or tag implied |

Appendix F and its [evidence source index](00_thesis_writing_tracking/Thesis/LaTeX_Project/tables/evidence_source_index.csv) retain the existing E-identifiers. The code map is a browsing layer, not a replacement evidence register. Historical manifests retain original paths and hashes; use the migration receipt to interpret relocated names.

## Dataset and implementation navigation

| Study | Thesis role | Code, configuration and evidence entry |
|---|---|---|
| PHM2026 | Chapter 5: photographic proxy targets and sensor-group regression | [Guide](implementations/PHM2026/README.md); [complete PHM traceability](implementations/PHM2026/docs/studies/THESIS_CODE_TRACEABILITY.md) |
| REASSEMBLE | Chapter 6: completed-action classification, fusion and controlled robustness | [Guide](implementations/REASSEMBLE/README.md); [core walkthrough](implementations/REASSEMBLE/experiments/core/README.md); later studies retain their own snapshots |
| MSM | Chapter 7: milling interval classification | [Guide](implementations/MSM/README.md); shared [external evaluator](implementations/cross_dataset/src/external_eval/) |
| ViFailback | Chapter 8: completed-episode classification and partial matched CNN study | [Guide](implementations/VIFAILBACK/README.md); [original workspace](VIFAILBACK/README.md) |
| HANDOVER | Appendix H: common-support assessment and participant-identity gate | [Guide](implementations/HANDOVER/README.md) |
| Intel Welding | Original application; historical modelling and later failed foundation gates | [Guide](implementations/INTEL_WELDING/README.md) |
| PADERBORN | Bearing-mechanism feasibility; evaluation protocol fork | [Guide](implementations/PADERBORN/README.md) |
| REBOOT | Annotation/alignment/visual-observability feasibility; supervised comparison not admitted | [Guide](implementations/REBOOT/README.md) |
| Cross-dataset | Synthesis and shared implementation, preserving separate tasks and metrics | [Guide](implementations/cross_dataset/README.md) |
| General | Original exposé, dataset discovery, maintenance and historical research records | [Guide](implementations/general/README.md) |

Each dataset guide links inputs/labels, preparation, architecture, protocol, saved assessment and limitations. Completed, unsuccessful, exploratory and unfinished work retain their study-local status. A script's presence is not evidence that an experiment ran. Dataset-specific fitting, learned-weight transfer and zero-shot evaluation are different claims.

## Protected locations and dependencies

Native inputs retain their original roots, including `MSM/01_raw_dataset/`, `HANDOVER/01_raw_dataset/`, `REBOOT/01_raw_dataset/`, `MILLING DATASET/data/` and `VIFAILBACK/01_original_dataset/`. Protected PHM `gtc-data-experiment/**` and Intel `data/Full Dataset/**` identities remain protected even when absent. No raw tree or model run is relocated by the thesis consolidation.

`implementations/` is the canonical browsing structure. Root `src/` has compatibility links to the PHM2026, REASSEMBLE, Intel Welding and shared external-evaluation packages. `implementations/VIFAILBACK/` links into the retained frozen root workspace. Original phase-one and bootstrap source/configuration/fit references remain at `26.10.2026_feedback_experiments/` and `parth_ws_bootstrap/00_experimentation/`. The protected initial PHM EDA remains at [experiments/exp_a_initial_eda_r1_r3_r5/](experiments/exp_a_initial_eda_r1_r3_r5/); `REBOOT/runs/` retains feasibility evidence.

## History, retrieval and policy

- [November 26 thesis consolidation](00_thesis_writing_tracking/consolidation_20261126/) records the approved local changes and publication dependencies.
- [November 25 broader physical move proposal](implementations/general/docs/repository_history/final_consolidation_20261125/MOVE_PLAN.md) is an earlier proposal, not an instruction to move dataset implementations now.
- [November 24 organization checks](implementations/general/docs/repository_history/post_report_cleanup_20261124/STATUS.json) and [change record](implementations/general/docs/repository_history/post_report_cleanup_20261124/CHANGES.json) describe that earlier scope.
- [Earlier dataset consolidation](implementations/general/docs/repository_history/dataset_layout_cleanup.json) and [physical path mapping](implementations/general/docs/repository_history/physical_restructure_20261119/PATH_MAPPING.json) resolve older source names.
- [PHM raw recovery](implementations/PHM2026/docs/RAW_DATA_RECOVERY.md), dataset-native acquisition records and [REASSEMBLE cache retention](docs/maintenance/REASSEMBLE_CACHE_RETENTION.md) distinguish retained evidence from external or regenerable payloads.

Relocation, link checks and recomputation of saved metrics do not reproduce training. Scope, data and retention decisions remain governed by [AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md), [data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md). Later task-specific research authorization does not silently amend the PHM-centred scope document.
