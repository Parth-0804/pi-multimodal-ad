# General tools and repository infrastructure

General scripts and their tests are stored here. Original script and test paths
remain compatibility symlinks. Dataset-specific implementations retain their own
ownership; this organisation adds no shared Python package.

| Work | Canonical location | Related checks or documentation |
|---|---|---|
| Repository maintenance | [Maintenance scripts](scripts/ops) | [Maintenance tests](tests/ops) |
| Thesis evidence checking | [Thesis scripts](scripts/thesis) | [Thesis tests](tests/thesis) and [scientific documentation](../../docs/thesis) |
| Presentation generation | [Presentation scripts](scripts/presentation) | Existing source reports remain the authority for any included claim. |
| Synthetic test inputs | [Fixtures](fixtures) | Synthetic inputs only; not a dataset or assessment cohort. |
| Packaging | [pyproject.toml](../../pyproject.toml) | Canonical packages live under [src/](../../src). |
| Dependency specification | [requirements.txt](../../requirements.txt) | The existing environment is described in the root [README](../../README.md). |
| Compatibility | [Legacy forwarding namespace](../../src/pi_multimodal_ad) | [Compatibility contract](../../docs/repository_restructure/COMPATIBILITY_CONTRACT.md) |
| Dataset discovery | [Dataset research](../../DATASET_RESEARCH/README.md) | Feasibility records point to their owning dataset workspace. |
| Research policy | [Repository instructions](../../AGENTS.md) | [Data boundaries](../../docs/data_boundaries.md), [output policy](../../docs/output_policy.md) and [written active scope](../../docs/active_scope.md) |
| Ancillary documents | [reports/extras/](../../reports/extras/README.md) | Planning notes, general reviews and writing support. |

The [external-evaluation implementation](../cross_dataset/src/external_eval)
has its own [cross-dataset guide](../../implementations/cross_dataset/README.md)
and study-specific consumers. The supplementary [raw-vibration](scripts/rawvib)
and [Paderborn](scripts/paderborn) utilities are indexed with
[PHM2026](../../implementations/PHM2026/README.md).

Run commands from the working directory required by the original scripts and
protocols. The links in this index do not redefine output roots, data roots,
configuration resolution or execution authorisation.

[All implementations](../../implementations/README.md)
