# VIFAILBACK

Robot manipulation outcome classification with multiview video and numerical robot observations.

The established VIFAILBACK layout uses ten numbered sections. The nine-stage reading order below maps to that layout without renumbering it. Use each experiment's source, protocol and per-condition records for execution status.

[Source](src) · [Scripts](scripts) · [Configurations](configs) · [Tests](tests) · [Workspace](../../VIFAILBACK/README.md)

This folder links to the existing workspace. Its implementation paths were retained
to protect the training job and its shared source dependencies during this reorganisation.

## Follow the implementation

The reading order follows HANDOVER's stages. Links point to existing canonical
locations; the numbering here does not rename a dataset's own stages or establish
that every stage was executed.

| Stage | Where to go | Purpose and evidence boundary |
|---|---|---|
| 01 | [Dataset source](01_original_dataset) | Official source identities and acquisition records. |
| 02 | [Labels and alignment](02_dataset_verification) | Target, grouping, availability and alignment verification. |
| 03 | [Processed inputs](03_preprocessing) | Input representations and preprocessing records. |
| 04 | [Experiment protocol](04_evaluation_splits) | Split definitions; experiment-specific protocols also live under experiments/. |
| 05 | [Models and training](06_training_experiments) | Training evidence; model definitions are under 05_model_implementations/ and src/. |
| 06 | [Evaluation results](09_evaluation_results) | Saved dataset-level assessment outputs; consult the producing study. |
| 07 | [Robustness](07_robustness_experiments) | Condition-specific robustness work and its coverage. |
| 08 | [Examples and EDA](08_visual_examples_and_eda) | Visual examples and data inspection. |
| 09 | [Reports and handoff](10_final_research_reports) | Reports and versioned snapshots; use study-local records for later experiments. |

## Related work

- [Experiment workspaces](experiments)
- [Model implementations](05_model_implementations)
- [Dataset README](../../VIFAILBACK/README.md)

[All implementations](../../implementations/README.md) · [Repository map](../../REPO_MAP.md)
