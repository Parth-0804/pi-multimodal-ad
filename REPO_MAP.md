# Repository map

The human-facing entry is [implementations/](implementations/README.md). Each dataset guide gives a staged route to its code, protocol, saved results and reports.

| Stage | Location |
|---|---|
| [Dataset implementations](implementations/README.md) | PHM2026, PADERBORN, INTEL_WELDING, MSM, HANDOVER, REBOOT, REASSEMBLE and VIFAILBACK |
| [Cross-dataset work](implementations/cross_dataset/README.md) | Shared external evaluation and comparison evidence |
| [Research support](implementations/general/README.md) | Thesis, maintenance, presentations, discovery and retained history |
| [Policies](docs) | Scope, raw-data boundaries, retention and output rules |

## Protected and historical locations

Native raw inputs remain at their original roots, including MSM/01_raw_dataset/, HANDOVER/01_raw_dataset/, REBOOT/01_raw_dataset/, MILLING DATASET/data/ and VIFAILBACK/01_original_dataset/. Root VIFAILBACK/ retains its complete frozen workspace; implementations/VIFAILBACK/ provides relative browsing links. No raw tree or scientific run was relocated by this phase.

Root src/ provides compatibility links to canonical dataset packages. The five remaining shared REASSEMBLE primitives were consolidated into implementations/REASSEMBLE/src/reassemble/ without changing their bytes. Original phase-one and bootstrap source/configuration/fit references remain at 26.10.2026_feedback_experiments/ and parth_ws_bootstrap/00_experimentation/. The protected initial PHM EDA stays at experiments/exp_a_initial_eda_r1_r3_r5/. REBOOT/runs/ retains investigation evidence.

## History and reproducibility

- [Pending full physical consolidation: exact move plan and approval boundary](implementations/general/docs/repository_history/final_consolidation_20261125/MOVE_PLAN.md) — prepared on 2026-11-25; no moves executed in this phase.
- [Current organization phase and checks](implementations/general/docs/repository_history/post_report_cleanup_20261124/STATUS.json)
- [Current move/link/deletion record](implementations/general/docs/repository_history/post_report_cleanup_20261124/CHANGES.json)
- [Earlier dataset consolidation](implementations/general/docs/repository_history/dataset_layout_cleanup.json)
- [Earlier physical move mapping](implementations/general/docs/repository_history/physical_restructure_20261119/PATH_MAPPING.json)
- [Archived AI workflow notes](implementations/general/docs/repository_history/ai_workflow_notes/README.md)

Frozen manifests and commands retain historical content and revisions. Relocation is not training reproduction. Package/import and selected synthetic checks do not establish that every historical command is runnable; consult the actual phase results. Old broad compatibility aliases remain removed except the explicitly recorded source import and preserved-history links.

Scientific scope remains governed by [AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md), [data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md).
