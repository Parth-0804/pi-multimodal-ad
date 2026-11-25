# MSM

Metal-milling interval classification from video and machine measurements. Earlier milling work is part of this dataset history, not another independent dataset.

| Stage | Location |
|---|---|
| 01 — Dataset and labels | [Label/alignment records](results/02_labels_and_alignment) |
| 02 — Preprocessing | [Processed model inputs](results/03_processed_model_inputs) |
| 03 — Protocol | [Experiment protocol](results/04_experiment_protocol) |
| 04 — Models and training | [Adapters](src); [Trained-model records](results/05_trained_models) |
| 05 — Assessment and robustness | [Evaluation](results/06_evaluation_results); [Robustness](results/07_robustness_experiments) |
| 06 — Examples and handoff | [Examples and EDA](results/08_visual_examples_and_eda); [Research handoff](results/09_final_reports/REVIEW_HANDOFF.md) |
| 07 — Earlier studies | [Legacy milling studies](experiments/legacy) |

[Source](src) · [Tests](tests) · [Documentation](docs)

Native inputs remain at repository-root `MSM/01_raw_dataset/` and `MILLING DATASET/data/`. Failed scientific gates and study eligibility remain authoritative. Shared fitting/evaluation implementation is in ../cross_dataset/src/external_eval/.

Each study's frozen protocol, fit manifests and assessment records determine what ran and which comparisons are eligible. A folder or script is not execution evidence. Historical commands retain their original paths; navigation/package checks are not model reproduction.

[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
