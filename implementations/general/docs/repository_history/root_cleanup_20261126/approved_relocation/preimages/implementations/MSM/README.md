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

Native input records are at `implementations/MSM/01_raw_dataset/`; the root `MSM/` no longer exists. The pre-existing `official_dataset` link there is broken; its intended source tree remains at repository-root `MILLING DATASET/data/`. A verified target repair is pending with the protected-location consolidation. Failed scientific gates and study eligibility remain authoritative. Shared fitting/evaluation implementation is in ../cross_dataset/src/external_eval/.

Each study's frozen protocol, fit manifests and assessment records determine what ran and which comparisons are eligible. A folder or script is not execution evidence. Historical commands retain their original paths; navigation/package checks are not model reproduction.

## Thesis and evidence

Chapter 7; existing evidence E068–E081 and E121. The [primary handoff](results/09_final_reports/REVIEW_HANDOFF.md) reports a completed three-seed comparison in which the stronger sensor reference exceeds the tested fusion models. Native class 1 is positive against classes 0+2; the DOWN-only, label-2-excluded sensitivity failed the fixed class-support gate. Earlier feasibility work must remain distinct from these completed assessments.

[Dataset overview](results/09_final_reports/DATASET_OVERVIEW.md), [validation](results/09_final_reports/DATASET_VALIDATION.md), [model implementation](results/09_final_reports/MODEL_IMPLEMENTATION.md) and [reproducibility](results/09_final_reports/REPRODUCIBILITY.md) provide source/label provenance, preparation, fitting and saved-evidence locations. Their old execution commands are historical records. The [chapter map](../../docs/THESIS_CODE_MAP.md) links the current shared evaluator.

[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
