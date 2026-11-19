# HANDOVER

Robot handover success/failure classification.

Reference layout for this index. The common-support study lives under `HANDOVER/experiments/common_support_v2/`. Its handoff records the participant-identity limitation and the mandatory OOF gate for learned fusion.

[Source](src) · [Tests](tests) · [Workspace](../../HANDOVER/README.md)

Implementation files are stored here. Original code paths remain relative symlinks
for compatibility; native inputs and saved study evidence retain their original locations.

## Follow the implementation

The reading order follows HANDOVER's stages. Links point to existing canonical
locations; the numbering here does not rename a dataset's own stages or establish
that every stage was executed.

| Stage | Where to go | Purpose and evidence boundary |
|---|---|---|
| 01 | [Dataset source](01_raw_dataset) | Native source and acquisition records; protected inputs remain in their existing location. |
| 02 | [Labels and alignment](../../HANDOVER/experiments/common_support_v2/02_labels_and_alignment) | Study-specific input validation and native outcome mapping. |
| 03 | [Processed inputs](../../HANDOVER/experiments/common_support_v2/03_processed_model_inputs) | Common-support inputs and data contract. |
| 04 | [Experiment protocol](../../HANDOVER/experiments/common_support_v2/04_experiment_protocol) | Splits, baselines and fitting requirements. |
| 05 | [Models and training](../../HANDOVER/experiments/common_support_v2/05_trained_models) | Study-local fitted model artifacts, where retained; eligibility remains protocol-specific. |
| 06 | [Evaluation results](../../HANDOVER/experiments/common_support_v2/06_evaluation_results) | Saved assessment outputs. |
| 07 | [Robustness](../../HANDOVER/experiments/common_support_v2/07_robustness_experiments) | Missing/degraded-input study outputs. |
| 08 | [Examples and EDA](../../HANDOVER/experiments/common_support_v2/08_visual_examples_and_eda) | Study-local galleries and examples. |
| 09 | [Reports and handoff](09_final_reports/REVIEW_HANDOFF.md) | Interpretation, eligibility, limitations and reproduction references. |

## Related work

- [Dataset README](../../HANDOVER/README.md)

[All implementations](../../implementations/README.md) · [Repository map](../../REPO_MAP.md)
