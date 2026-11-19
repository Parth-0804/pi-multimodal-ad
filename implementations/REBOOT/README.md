# REBOOT

Dataset qualification, annotation/source audits, alignment and visual-observability feasibility.

This workspace records feasibility investigations. Its decision records govern further work; feasibility is not a trained-model or predictive-performance result.

[Source](src) · [Tests](tests) · [Workspace](../../REBOOT/README.md)

Implementation files are stored here. Original code paths remain relative symlinks
for compatibility; native inputs and saved study evidence retain their original locations.

## Follow the implementation

The reading order follows HANDOVER's stages. Links point to existing canonical
locations; the numbering here does not rename a dataset's own stages or establish
that every stage was executed.

| Stage | Where to go | Purpose and evidence boundary |
|---|---|---|
| 01 | [Dataset source](00_dataset_overview/REBOOT_SOURCE_AUDIT.md) | Pinned source/version and acquisition audit. |
| 02 | [Labels and annotations](02_labels_and_annotations) | Native annotation semantics, defects and target-feasibility records. |
| 03 | [Inputs and alignment](03_video_sensor_alignment) | Video/state alignment feasibility and its limits. |
| 04 | [Evaluation feasibility](06_evaluation_feasibility) | Grouping and proposed-protocol evidence; not an executed assessment. |
| 05 | [Architecture compatibility](05_architecture_compatibility) | Compatibility assessment rather than trained-model evidence. |
| 06 | Evaluation results | No model-evaluation result is supplied by these feasibility records; consult the research decision. |
| 07 | Robustness | No trained-model robustness evidence is established by this feasibility workspace. |
| 08 | [Examples and visual review](04_visual_failure_review) | Blinded visual review materials and observability evidence. |
| 09 | [Decision and handoff](07_research_decision) | Scientific eligibility decisions, blockers and follow-up boundaries. |

## Related work

- [Visual EDA](08_visual_examples_and_eda)
- [Versioned investigation runs](../../REBOOT/runs)
- [Dataset-discovery navigation](../../DATASET_RESEARCH/README.md)

[All implementations](../../implementations/README.md) · [Repository map](../../REPO_MAP.md)
