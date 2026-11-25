# MSM

Metal-milling interval classification using video and machine measurements.
The earlier `MILLING DATASET/` work belongs to the same dataset's history,
rather than an additional independent evaluation dataset.

| Part | Location |
|---|---|
| Adapters | [src](src) |
| Shared evaluation code | [cross_dataset/src/external_eval](../cross_dataset/src/external_eval) |
| Checks | [tests](tests) |
| Labels and alignment | [results/02_labels_and_alignment](results/02_labels_and_alignment) |
| Processed-input records | [results/03_processed_model_inputs](results/03_processed_model_inputs) |
| Protocol | [results/04_experiment_protocol](results/04_experiment_protocol) |
| Model records | [results/05_trained_models](results/05_trained_models) |
| Evaluation | [results/06_evaluation_results](results/06_evaluation_results) |
| Robustness | [results/07_robustness_experiments](results/07_robustness_experiments) |
| Examples and EDA | [results/08_visual_examples_and_eda](results/08_visual_examples_and_eda) |
| Findings and eligibility | [Research handoff](results/09_final_reports/REVIEW_HANDOFF.md) |
| Earlier milling studies | [experiments/legacy](experiments/legacy) |
| Workspace documentation | [docs](docs), [preserved workspace guide](docs/WORKSPACE.md) |

Native inputs remain at `MSM/01_raw_dataset/` and `MILLING DATASET/data/`, with
specifically protected source subtrees retained in place. Study protocols and
failed gates determine which comparisons are admissible; directory names alone
do not establish completed model evaluation.

Old source aliases were removed. Source-path and packaging updates remain
unfinished; the [move mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
resolves paths recorded before these moves.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
