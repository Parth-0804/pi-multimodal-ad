# Repository map

Start with [implementations/](implementations/README.md). Each dataset guide
points to its code, protocols, experiments and retained results.

## Physical layout

| Folder | Contents |
|---|---|
| [implementations/PHM2026](implementations/PHM2026/README.md) | PHM source, scripts, configs, tests, experiments, results and documentation. |
| [implementations/PADERBORN](implementations/PADERBORN/README.md) | Historical ARCH-VAL-PB scripts, derived bearing features and protocol/report records. |
| [implementations/INTEL_WELDING](implementations/INTEL_WELDING/README.md) | Historical namespace, audit scripts, configs, tests and research evidence. |
| [implementations/MSM](implementations/MSM/README.md) | Milling adapters, tests, numbered result stages and earlier milling experiments. |
| [implementations/HANDOVER](implementations/HANDOVER/README.md) | Handover adapters, tests, numbered result stages and common-support study. |
| [implementations/REBOOT](implementations/REBOOT/README.md) | Feasibility code, tests, annotation audits and research decisions. |
| [implementations/REASSEMBLE](implementations/REASSEMBLE/README.md) | Source modules, scripts, configs, tests, studies, named runs, audits and reports; five shared source files temporarily remain at repo root. |
| [VIFAILBACK](VIFAILBACK/README.md) | Existing implementation, numbered stages and study-local training workspaces. |
| [implementations/cross_dataset](implementations/cross_dataset/README.md) | External-evaluation source, configs, tests, comparison reports and provenance. |
| [implementations/general](implementations/general/README.md) | Maintenance and thesis tools, research workflows, repository history and storage records. |
| [docs](docs) and [AGENTS.md](AGENTS.md) | Written policies, working instructions and retention requirements. |

Within an implementation, `src/` holds code, `scripts/` entry points, `configs/`
settings, `tests/` checks, `experiments/` separate studies, `results/` retained
outputs and `docs/` supporting documentation. Only applicable folders exist.
Numbered result stages preserve each dataset's own organisation.

## Paths retained in place

Most REASSEMBLE implementation and evidence now live in its
[dataset folder](implementations/REASSEMBLE/README.md). The remaining training
dependencies retain their existing paths:

- [Five shared REASSEMBLE source files](src/reassemble) and their existing bytecode
  cache. Their relocation is deferred while VIFAILBACK uses them.
- The retained [phase-one source/configuration and fit references](26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability)
  and [bootstrap experiments](parth_ws_bootstrap/00_experimentation). Other audit
  and workflow folders from those parents now live with their implementation owner.
- [VIFAILBACK workspace](VIFAILBACK) and
  [verification records](DATASET_RESEARCH/VIFAILBACK_VERIFICATION).

Native input roots remain in place, including `MSM/01_raw_dataset/`,
`HANDOVER/01_raw_dataset/`, `REBOOT/01_raw_dataset/` and `MILLING DATASET/data/`.
[REBOOT/runs](REBOOT/runs) retains source and investigation evidence. The initial
[PHM EDA](experiments/exp_a_initial_eda_r1_r3_r5) remains protected at its original
path. Other specifically retained source subtrees are listed in the
[approved move plan](implementations/general/docs/repository_history/physical_restructure_20261119/BULK_MOVE_PLAN.md).

## Reading the moved work

Old compatibility aliases were removed. Source-path and package-discovery
updates remain unfinished; historical commands and installation instructions
may refer to former locations. This layout has not been validated as a runnable
release. Use the [earlier physical-move mapping](implementations/general/docs/repository_history/physical_restructure_20261119/PATH_MAPPING.json)
and [recorded unfinished work](implementations/general/docs/repository_history/physical_restructure_20261119/PAUSED_STATE.md).
The [latest consolidation record](implementations/general/docs/repository_history/dataset_layout_cleanup.json)
tracks readable run names, report names and current physical paths.
PHM planning lives in
[PHM2026/docs/research_history](implementations/PHM2026/docs/research_history);
its study reports and derived companions live in
[PHM2026/docs/studies](implementations/PHM2026/docs/studies). The separate bearing
study lives in [PADERBORN](implementations/PADERBORN/README.md).
REASSEMBLE assignments and handoffs live in
[REASSEMBLE/docs](implementations/REASSEMBLE/docs). General support lives in
[research_workflow](implementations/general/research_workflow),
[repository_history](implementations/general/docs/repository_history) and
[storage_history](implementations/general/docs/storage_history).

Frozen source snapshots and run manifests keep their historical paths and
identities. Their recorded revision and relocation mapping are needed when
interpreting them. Moving a result is not a new experiment or a reproduction.

Scientific scope and execution authority remain governed by
[AGENTS.md](AGENTS.md), [active scope](docs/active_scope.md),
[data boundaries](docs/data_boundaries.md) and [output policy](docs/output_policy.md).
Read the [REASSEMBLE cache-retention record](docs/maintenance/REASSEMBLE_CACHE_RETENTION.md)
before assuming historical arrays remain available.
