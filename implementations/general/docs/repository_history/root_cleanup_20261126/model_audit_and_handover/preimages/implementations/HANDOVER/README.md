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

## Thesis and evidence

Appendix H; existing evidence E082–E086. The [research handoff](results/09_final_reports/REVIEW_HANDOFF.md) reports completed unimodal and fixed-averaging assessment in the common-support study. F2, augmented F2 and learned quality gates were skipped because participant-disjoint OOF predictions cannot be certified from the released identity metadata. Their omission is a failed eligibility gate, not a negative fitted-model result.

The [dataset overview](results/09_final_reports/DATASET_OVERVIEW.md), [validation](results/09_final_reports/DATASET_VALIDATION.md), [model implementation](results/09_final_reports/MODEL_IMPLEMENTATION.md) and [common-support configuration](experiments/common_support_v2/04_experiment_protocol/experiment_config.json) retain acquisition/source identity, preparation, target and observation-horizon rules. Use the [chapter map](../../docs/THESIS_CODE_MAP.md) for current source and assessment links.

[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
