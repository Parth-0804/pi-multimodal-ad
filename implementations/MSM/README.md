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

The [native input records](01_raw_dataset/) and [legacy milling studies](experiments/legacy/) are physically consolidated here. The repaired [official dataset link](01_raw_dataset/official_dataset/) resolves to the retained [legacy source tree](experiments/legacy/data/raw/msm/versions/2/). Dataset/source identities remain distinct and protected. Failed scientific gates and study eligibility remain authoritative. Shared fitting/evaluation code is in [external_eval](../cross_dataset/src/external_eval/). The [legacy execution-path audit](../general/docs/repository_history/root_cleanup_20261126/approved_relocation/vifailback_adapter/LEGACY_CONSUMER_LIMITS.md) identifies unresolved string-I/O and controller paths; current navigation does not certify unchanged historical commands as runnable.

Each study's frozen protocol, fit manifests and assessment records determine what ran and which comparisons are eligible. A folder or script is not execution evidence. Historical commands retain their original paths; navigation/package checks are not model reproduction.

## Thesis and evidence

Evidence IDs below follow the researcher-requested 28 November renumbering. The [complete mapping](../../00_thesis_writing_tracking/final_thesis_prep/evidence_publication_20261128/manifest.json) relates them to the prior IDs retained in historical records.

Chapter 7; current evidence E066–E079 and E119. The [primary handoff](results/09_final_reports/REVIEW_HANDOFF.md) reports a completed three-seed comparison in which the stronger sensor reference exceeds the tested fusion models. Native class 1 is positive against classes 0+2; the DOWN-only, label-2-excluded sensitivity failed the fixed class-support gate. Earlier feasibility work must remain distinct from these completed assessments.

[Dataset overview](results/09_final_reports/DATASET_OVERVIEW.md), [validation](results/09_final_reports/DATASET_VALIDATION.md), [model implementation](results/09_final_reports/MODEL_IMPLEMENTATION.md) and [reproducibility](results/09_final_reports/REPRODUCIBILITY.md) provide source/label provenance, preparation, fitting and saved-evidence locations. Their old execution commands are historical records. The [chapter map](../../docs/THESIS_CODE_MAP.md) links the current shared evaluator.

[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
