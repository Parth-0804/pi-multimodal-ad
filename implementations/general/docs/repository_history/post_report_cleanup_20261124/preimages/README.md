# pi-multimodal-ad

Master's thesis workspace for visual and sensor representations, unimodal
baselines, multimodal fusion and missing or degraded modality evaluation.

Start with [implementations/](implementations/README.md) to find each dataset's
code, experiments, results and scientific reports. [REPO_MAP.md](REPO_MAP.md)
shows the repository layout and the paths retained for training dependencies.

Open the [Thesis implementations workspace](.vscode/thesis.code-workspace) in
VS Code for an Explorer view of `implementations/`. Physical root exceptions
remain listed in the repository map.

The physical reorganisation is ahead of the code updates. Source-path and
packaging fixes remain unfinished, so earlier installation instructions and
commands are not a validated quickstart for this layout. Old compatibility
aliases have been removed. See the [recorded state](implementations/general/docs/repository_history/physical_restructure_20261119/PAUSED_STATE.md)
and [earlier move mapping](implementations/general/docs/repository_history/physical_restructure_20261119/PATH_MAPPING.json).
The [latest consolidation record](implementations/general/docs/repository_history/dataset_layout_cleanup.json)
records the current source, run, report and supporting-folder locations.

## Find the work

| Work | Where to start |
|---|---|
| PHM2026 gear-condition and proxy-target studies | [PHM2026](implementations/PHM2026/README.md) |
| Historical Paderborn bearing study (ARCH-VAL-PB) | [PADERBORN](implementations/PADERBORN/README.md) |
| REASSEMBLE completed-action failure classification | [REASSEMBLE](implementations/REASSEMBLE/README.md) |
| VIFAILBACK multiview manipulation outcomes | [Existing VIFAILBACK workspace](VIFAILBACK/README.md) |
| MSM metal-milling interval classification | [MSM](implementations/MSM/README.md) |
| HANDOVER robot handover outcomes | [HANDOVER](implementations/HANDOVER/README.md) |
| REBOOT dataset feasibility | [REBOOT](implementations/REBOOT/README.md) |
| Intel Welding historical research and audits | [INTEL_WELDING](implementations/INTEL_WELDING/README.md) |
| Cross-dataset evaluation and comparisons | [cross_dataset](implementations/cross_dataset/README.md) |
| Maintenance, thesis and presentation tools | [general](implementations/general/README.md) |
| Research workflow and thesis-writing support | [general/research_workflow](implementations/general/research_workflow) |
| Repository and storage history | [repository_history](implementations/general/docs/repository_history), [storage_history](implementations/general/docs/storage_history) |

Most moved work is grouped under `implementations/<dataset>/`, using `src/`,
`scripts/`, `configs/`, `tests/`, `experiments/`, `results/` and `docs/` where
applicable. VIFAILBACK retains its existing workspace. Five shared REASSEMBLE
source files and the phase-one/bootstrap reference trees retain their original paths
while training dependencies are protected. Raw inputs and protected historical
outputs also remain in place. Dataset guides link these exceptions directly.

## Research context and boundaries

The PHM North America 2026 studies use post-run photos and vibration
measurements for gear-condition research. Image-derived targets and heuristic
pseudo-boxes are provisional supervision, not independently validated physical
damage labels. Earlier RT-DETR and PatchTST baselines include negative findings;
retain their target versions, protocols and limitations when using the
[PHM records](implementations/PHM2026/README.md).

Earlier Intel Welding research is retained in the
[historical study](implementations/INTEL_WELDING/experiments/legacy/README.md).

Later datasets address different prediction tasks and evaluation units. Their
study-specific protocols, eligibility decisions and saved execution records
remain authoritative. A folder or model implementation does not establish a
completed experiment, and this navigation does not amend the written thesis
scope. The [original thesis documents](implementations/general/docs/thesis/source_documents)
and study records retain their separate history.

Read [AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md),
[data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md)
before changing data, experiments or repository structure. Protected raw-root
identities include `gtc-data-experiment/**` and `data/Full Dataset/**`, even when
those inputs are unavailable locally. Git does not contain every local dataset,
cache or checkpoint.

Before reusing REASSEMBLE caches, consult the
[retention and recovery record](docs/maintenance/REASSEMBLE_CACHE_RETENTION.md).
Dependency specifications remain in [requirements.txt](requirements.txt) and
[pyproject.toml](pyproject.toml); the latter still needs alignment with the moved
source layout.

See [LICENSE](LICENSE).
