# HANDOVER

Robot handover success/failure classification. Recording/task groups do not establish participant independence.

| Stage | Location |
|---|---|
| 01 — Labels and alignment | [Data-contract records](results/02_labels_and_alignment) |
| 02 — Preprocessing and protocol | [Processed inputs](results/03_processed_model_inputs); [Protocol](results/04_experiment_protocol) |
| 03 — Models and training | [Adapters](src); [Training records](results/05_trained_models) |
| 04 — Main eligible study | [Common-support study](experiments/common_support_v2) |
| 05 — Assessment and robustness | [Evaluation](results/06_evaluation_results); [Robustness](results/07_robustness_experiments) |
| 06 — Examples and handoff | [Examples](results/08_visual_examples_and_eda); [Research handoff](results/09_final_reports/REVIEW_HANDOFF.md) |

[Source](src) · [Tests](tests) · [Documentation](docs)

Native inputs stay at repository-root HANDOVER/01_raw_dataset/. Preserve participant-identity limitations and mandatory participant-safe OOF gates. Missing identity is not permission to substitute trial groups or in-sample stacking.

Each study's frozen protocol, fit manifests and assessment records determine what ran and which comparisons are eligible. A folder or script is not execution evidence. Historical commands retain their original paths; navigation/package checks are not model reproduction.

[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
