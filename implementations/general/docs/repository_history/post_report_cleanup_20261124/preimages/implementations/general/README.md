# General tools and documentation

Repository maintenance, thesis evidence work, presentation generation and
supplementary utilities. Dataset-specific implementations retain their own
ownership; this folder does not introduce a shared Python package.

| Work | Location |
|---|---|
| Maintenance scripts and checks | [scripts/ops](scripts/ops), [tests/ops](tests/ops) |
| Thesis evidence scripts and checks | [scripts/thesis](scripts/thesis), [tests/thesis](tests/thesis) |
| Cross-study evidence reviews | [FINAL_VALIDITY_AUDIT](results/artifacts/FINAL_VALIDITY_AUDIT), [REVIEW_RESULTS_BUNDLE](results/artifacts/REVIEW_RESULTS_BUNDLE) |
| REASSEMBLE human-review interface | [Builder](../REASSEMBLE/scripts/review_interface), [derived exports](../REASSEMBLE/results/human_review) |
| Presentation generation | [scripts/presentation](scripts/presentation) |
| PHM raw-vibration utilities | [PHM2026/scripts/rawvib](../PHM2026/scripts/rawvib) |
| Paderborn bearing study | [PADERBORN](../PADERBORN/README.md) |
| EDA utilities with multiple dataset consumers | [scripts/eda](scripts/eda) |
| Synthetic test inputs | [tests/fixtures](tests/fixtures) |
| Thesis documentation and source documents | [docs/thesis](docs/thesis) |
| Dataset discovery and screening | [docs/dataset_research](docs/dataset_research/README.md) |
| Presentation documents | [docs/presentations](docs/presentations) |
| Retained general outputs | [results](results) |
| Packaging and dependencies | [pyproject.toml](../../pyproject.toml), [requirements.txt](../../requirements.txt) |
| Repository policy | [AGENTS.md](../../AGENTS.md), [data boundaries](../../docs/data_boundaries.md), [output policy](../../docs/output_policy.md), [active scope](../../docs/active_scope.md) |
| Research automation and its evidence | [research_workflow/automation](research_workflow/automation/README.md) |
| Workflow prompt pack | [research_workflow/parth_ws_bootstrap](research_workflow/parth_ws_bootstrap) |
| Thesis-writing support | [research_workflow/thesis_writing](research_workflow/thesis_writing) |
| Repository moves, validation and cleanup history | [docs/repository_history](docs/repository_history) |
| Storage audits and retention evidence | [docs/storage_history](docs/storage_history) |
| Latest folder consolidation | [dataset_layout_cleanup.json](docs/repository_history/dataset_layout_cleanup.json) |

PHM raw-vibration work and the Paderborn bearing study have their own dataset
folders. EDA utilities retain multiple dataset consumers and remain here.
Shared external-evaluation work belongs under [cross_dataset](../cross_dataset/README.md).

The [claim matrix](docs/thesis/FINAL_CLAIM_MATRIX.md),
[reproducibility snapshot](docs/thesis/FINAL_THESIS_REPRODUCIBILITY.md) and
[expose-to-thesis matrix](docs/thesis/EXPOSE_TO_FINAL_THESIS_MATRIX.md) retain their
historical relative paths. Use the [latest layout mapping](docs/repository_history/dataset_layout_cleanup.json)
and [earlier consolidation record](docs/repository_history/dataset_consolidation_20261120.json)
to locate relocated PHM and Paderborn reports and companion records.

Old script aliases were removed. Source-path and packaging updates remain
unfinished, including references to former script and fixture locations. Use the
[move mapping](docs/repository_history/dataset_layout_cleanup.json)
and [recorded state](docs/repository_history/physical_restructure_20261119/PAUSED_STATE.md)
before reusing historical commands. This documentation does not authorize new
experiments or establish artifact availability beyond the cited study records.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
