# Implementations

Start here to find code, protocols, results and required reports by dataset.
The reading order follows HANDOVER: source → labels → inputs → protocol → models
→ evaluation → robustness → examples → reports.

Inactive implementation files now live under their dataset folders below. General
tools have their own folder. Relative symlinks preserve the old code paths used by
imports, scripts and existing documentation. Keep symlink support enabled when
checking out this layout on another computer.

VIFAILBACK and the REASSEMBLE code it depends on retain their original physical
locations for this organisation phase. Their entries here link to those locations.
Native raw data, checkpoints, run outputs, frozen source snapshots and scientific
reports remain in their existing workspaces. Numbered stage links make those
records accessible here without moving them.

## Repository at a glance

```text
implementations/
  HANDOVER/          src, tests and links to the numbered study stages
  MSM/               src, tests and links to the numbered study stages
  PHM2026/           src, scripts, tests, configs and evidence links
  INTEL_WELDING/     namespace, audit scripts, tests, configs and evidence links
  REBOOT/            src, tests and links to the feasibility stages
  VIFAILBACK/        links to the retained implementation and study stages
  REASSEMBLE/        links to the retained implementation and evidence
  cross_dataset/     external-evaluation source, tests and evidence links
  general/           maintenance, thesis, presentation and supplementary tools
reports/extras/       additional reports, planning notes and writing support
MSM/, HANDOVER/, ...  retained native inputs, models, results and study evidence
runs/, artifacts/    retained execution/evaluation records
src/, scripts/, ...  retained dependencies and compatibility paths
configs/, tests/     retained settings, synthetic fixtures and compatibility tests
docs/                policy, protocols, interpretation and recovery
```

## Choose a dataset

| Dataset | Task or role | Implementation | Evidence and protocols |
|---|---|---|---|
| [HANDOVER](HANDOVER/README.md) | Robot handover outcomes. | [Source](HANDOVER/src) | [Study workspace](../HANDOVER/README.md) |
| [MSM](MSM/README.md) | Metal-milling intervals. | [Source](MSM/src) | [Study workspace](../MSM/README.md) |
| [PHM2026](PHM2026/README.md) | Gear condition and image-derived proxy targets. | [Source](PHM2026/src/phm2026) | [Walkthrough](PHM2026/walkthrough/README.md) |
| [INTEL_WELDING](INTEL_WELDING/README.md) | Historical intended-condition research and foundation audits. | [Audit scripts](INTEL_WELDING/scripts) | [Namespace and scope](INTEL_WELDING/src/intel_welding/README.md) |
| [REBOOT](REBOOT/README.md) | Dataset and annotation feasibility. | [Source](REBOOT/src) | [Feasibility workspace](../REBOOT/README.md) |
| [VIFAILBACK](VIFAILBACK/README.md) | Multiview robot manipulation outcomes. | [Retained source](VIFAILBACK/src) | [Study workspace](../VIFAILBACK/README.md) |
| [REASSEMBLE](REASSEMBLE/README.md) | Completed-action failure classification and fusion. | [Retained source](REASSEMBLE/src) | [Walkthrough](REASSEMBLE/walkthrough/README.md) |

A folder or stage link does not establish that an experiment ran or passed.
Study-specific handoffs and manifests remain authoritative for execution,
scientific eligibility and limitations. Dataset-specific fitting, learned-weight
transfer and zero-shot evaluation retain their different meanings.

## Other work

- [Cross-dataset implementation and comparisons](cross_dataset/README.md)
- [General tools and repository infrastructure](general/README.md)
- [Dataset discovery and screening](../DATASET_RESEARCH/README.md)
- [Extra reports and supporting documents](../reports/extras/README.md)
- [Repository rules](../AGENTS.md) and [repository map](../REPO_MAP.md)
- [Relocation paths, original hashes and retained-source records](../reports/extras/repository_organization_20261119/RELOCATION_MANIFEST.json)

The historical `MILLING DATASET/` tree belongs to MSM's lineage. Supplementary
raw-vibration and Paderborn work is linked from PHM2026. Root packaging and
dependency files remain where the tools expect them. Use the existing study
commands from the required working directory; organisation does not authorise
new experiments or alter scientific protocols.
