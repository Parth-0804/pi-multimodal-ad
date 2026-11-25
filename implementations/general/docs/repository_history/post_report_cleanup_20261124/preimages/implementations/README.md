# Implementations

Choose a dataset below to find its code, protocols, experiments and results.
The dataset guides follow the work from inputs and labels through evaluation
and scientific conclusions, without imposing a common experimental protocol.

## Repository at a glance

```text
implementations/
  PHM2026/        src, scripts, configs, tests, experiments, results, docs
  PADERBORN/      scripts, processed results, docs; historical ARCH-VAL-PB study
  INTEL_WELDING/  src, scripts, configs, tests, experiments, results, docs
  MSM/            src, tests, experiments, results, docs
  HANDOVER/       src, tests, experiments, results, docs
  REBOOT/         src, tests, results, docs
  REASSEMBLE/     src, scripts, configs, tests, experiments, results, docs
  cross_dataset/  src, configs, tests, results
  general/        scripts, tests, results, docs, research_workflow
VIFAILBACK/       original implementation and experiment workspace
```

`results/` contains retained evidence, including each dataset's numbered stages
where applicable. `experiments/` separates study-specific work and frozen source
snapshots. Native raw inputs retain their original roots.

## Choose a dataset

| Dataset | Task or role | Main evidence |
|---|---|---|
| [PHM2026](PHM2026/README.md) | Gear condition and image-derived proxy targets. | [Experiments](PHM2026/experiments), [results](PHM2026/results) |
| [PADERBORN](PADERBORN/README.md) | Historical bearing mechanism and feasibility study. | [Scripts](PADERBORN/scripts), [derived features](PADERBORN/results/processed/bearing_features), [protocol and report](PADERBORN/docs) |
| [INTEL_WELDING](INTEL_WELDING/README.md) | Historical intended-condition research and foundation audits. | [Review](INTEL_WELDING/docs/RESULTS_REVIEW.md), [results](INTEL_WELDING/results) |
| [MSM](MSM/README.md) | Metal-milling interval classification. | [Result stages](MSM/results), [earlier work](MSM/experiments/legacy) |
| [HANDOVER](HANDOVER/README.md) | Robot handover outcomes. | [Result stages](HANDOVER/results), [common-support study](HANDOVER/experiments/common_support_v2) |
| [REBOOT](REBOOT/README.md) | Dataset, annotation and visual-observability feasibility. | [Research decision](REBOOT/results/07_research_decision) |
| [REASSEMBLE](REASSEMBLE/README.md) | Completed-action failure classification and fusion. | [Core walkthrough](REASSEMBLE/experiments/core), [retained results](REASSEMBLE/results/artifacts) |
| [VIFAILBACK](../VIFAILBACK/README.md) | Multiview robot manipulation outcomes. | [Existing study workspaces](../VIFAILBACK/experiments) |

## Other work and retained paths

- [Cross-dataset implementation and comparisons](cross_dataset/README.md).
- [General tools, thesis records and dataset discovery](general/README.md).
- [Research workflows](general/research_workflow), [repository history](general/docs/repository_history)
  and [storage history](general/docs/storage_history).
- [Repository map](../REPO_MAP.md) and [latest consolidation record](general/docs/repository_history/dataset_layout_cleanup.json).

REASSEMBLE now owns its [source modules](REASSEMBLE/src/reassemble),
[scripts](REASSEMBLE/scripts), [configs](REASSEMBLE/configs),
[named runs](REASSEMBLE/results/runs) and [artifacts](REASSEMBLE/results/artifacts).
VIFAILBACK retains its existing workspace. Five shared source files remain in
[root src/reassemble](../src/reassemble), with their existing bytecode cache,
and their relocation is deferred while VIFAILBACK uses them.
The [phase-one source/configuration and fit references](../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability)
and [bootstrap experiments](../parth_ws_bootstrap/00_experimentation) also remain
in place. Other workflow and audit folders from those parents have moved into
REASSEMBLE or general tools according to their purpose.

Old compatibility aliases have been removed. Source-path and packaging fixes
remain unfinished; existing commands are not yet validated for this layout.
See the [recorded state](general/docs/repository_history/physical_restructure_20261119/PAUSED_STATE.md)
and [move mapping](general/docs/repository_history/dataset_layout_cleanup.json).

A folder does not establish that a study ran or passed. Study protocols,
execution manifests and scientific eligibility decisions remain authoritative.
This index does not amend the [written scope](../docs/active_scope.md) or grant
experiment execution authority; follow [AGENTS.md](../AGENTS.md).
