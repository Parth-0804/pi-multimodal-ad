# Extra reports and supporting documents

This folder collects ancillary documents created for planning, writing support,
repository reviews, storage inventories and Git handoffs. The original folder
structure is kept below this directory so each document remains identifiable.

Core implementations are organised under [implementations/](../../implementations/README.md).
Experiment protocols, scientific results, failed-gate evidence, checkpoints,
provenance and recovery/retention records retain their study locations. A report
needed to interpret a study belongs with that study.

## Find the extra documents

- [Thesis-writing and research-tool workflow kit](Thesis_Workflow_Starter_Kit/00_START_HERE.txt)
- [Storage overview and observational audit reports](STORAGE_AUDIT/20261028T115408Z/PROJECT_STORAGE_OVERVIEW.md)
- [Generated directory-map reports](STORAGE_AUDIT/20261028T192446975701Z_directory_map/PROJECT_DIRECTORY_MAP.md)
- [Earlier repository folder listing](docs/REPOSITORY_FOLDER_STRUCTURE_20260929T135756Z.md)
- [Historical fusion roadmap](docs/planning/FUSION_ROADMAP.md)
- [Historical implementation backlog](docs/planning/PHM_CODEX_IMPLEMENTATION_BACKLOG.md)
- [Completed repository-reorganisation handoff](docs/repository_restructure/CONTINUATION.md)
- [Completed compatibility-work handoff](docs/repository_restructure/COMPATIBILITY_CONTINUATION.md)
- [General data-acquisition lessons](experiments/LARGE_DATASET_ACQUISITION_BEST_PRACTICES.md)
- [Git commit/push handoff](00_experiments/completed_reassemble_work_git_handoff_01/README_FIRST.md)
- [Version-control packaging note](00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/GIT_VERSION_CONTROL.md)
- [Prompt examples and original messages](docs/thesis/AI_PROMPT_EXAMPLES.md)
- [Implementation relocation paths and original hashes](repository_organization_20261119/RELOCATION_MANIFEST.json)
- [Implementation relocation checks](repository_organization_20261119/VALIDATION.json)

## Relocation record

[RELOCATION_MANIFEST.json](RELOCATION_MANIFEST.json) records original and new paths,
content hashes, reasons for moving each file and navigation edits. It distinguishes
filesystem moves from the retained prompt note: that note was already absent from
its old path, so the exact version retained in this chat was archived here.

[DOCUMENT_CLASSIFICATION.json](DOCUMENT_CLASSIFICATION.json) records the disposition
of the 1,654 Markdown paths inventoried outside raw-data roots, environments and
caches. Retained groups were classified by their location and role; this is not
a new validation of their scientific claims.

Relative Markdown links were adjusted where needed. Exact bytes from before
link changes are preserved under `_originals_before_link_updates/`. Those copies
are historical originals; use the indexed documents for working links. Literal
paths inside historical text and frozen manifests keep their original meaning;
the relocation manifest supplies the current location.

The move preserved the existing missing tracked paths and unrelated working-tree
changes. No model code, dataset, experiment configuration or scientific result
was rewritten. No experiment was run and no commit or push was made.
