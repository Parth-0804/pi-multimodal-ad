# MSM

Metal-milling interval classification using video and machine measurements.

The canonical evaluation workspace is `MSM/`. `MILLING DATASET/` holds preserved earlier work for the same dataset, rather than a separate independent evaluation dataset.

[Source](src) · [Tests](tests) · [Workspace](../../MSM/README.md)

Implementation files are stored here. Original code paths remain relative symlinks
for compatibility; native inputs and saved study evidence retain their original locations.

## Follow the implementation

The reading order follows HANDOVER's stages. Links point to existing canonical
locations; the numbering here does not rename a dataset's own stages or establish
that every stage was executed.

| Stage | Where to go | Purpose and evidence boundary |
|---|---|---|
| 01 | [Dataset source](01_raw_dataset) | Source/acquisition navigation; native inputs remain protected. |
| 02 | [Labels and alignment](02_labels_and_alignment) | Native label, eligibility and alignment validation. |
| 03 | [Processed inputs](03_processed_model_inputs) | Data contract, feature inputs and split manifests. |
| 04 | [Experiment protocol](04_experiment_protocol) | Architecture, baselines and split protocol. |
| 05 | [Models and training](05_trained_models) | Retained fitted models and training artifacts. |
| 06 | [Evaluation results](06_evaluation_results) | Saved predictions, metrics and figures. |
| 07 | [Robustness](07_robustness_experiments) | Controlled missing/degraded-modality evidence. |
| 08 | [Examples and EDA](08_visual_examples_and_eda) | Representative examples and galleries. |
| 09 | [Reports and handoff](09_final_reports/REVIEW_HANDOFF.md) | Study conclusions, failed gates and reproducibility. |

## Related work

- [Preserved earlier milling work](../../MILLING%20DATASET/README.md)
- [Shared external-evaluation implementation](../cross_dataset/src/external_eval)

[All implementations](../../implementations/README.md) · [Repository map](../../REPO_MAP.md)
