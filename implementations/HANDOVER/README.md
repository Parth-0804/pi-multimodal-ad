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

Native inputs are physically retained at [01_raw_dataset/](01_raw_dataset/), also
reached through the repaired [common-support study input link](experiments/common_support_v2/01_raw_dataset/).
The [approved relocation receipt](../general/docs/repository_history/root_cleanup_20261126/approved_relocation/README.md)
records the same-filesystem move and preservation of file identities. The
[legacy execution-path audit](../general/docs/repository_history/root_cleanup_20261126/approved_relocation/vifailback_adapter/LEGACY_CONSUMER_LIMITS.md)
records remaining manifest-string and controller-path dependencies; no replay is
claimed. Preserve participant-identity limitations and mandatory participant-safe
OOF gates. Missing identity is not permission to substitute trial groups or
in-sample stacking.

Each study's frozen protocol, fit manifests and assessment records determine what ran and which comparisons are eligible. A folder or script is not execution evidence. Historical commands retain their original paths; navigation/package checks are not model reproduction.

## Thesis and evidence

Evidence IDs below follow the researcher-requested 28 November renumbering. The [complete mapping](../../00_thesis_writing_tracking/final_thesis_prep/evidence_publication_20261128/manifest.json) relates them to the prior IDs retained in historical records.

Appendix H; current evidence E080–E084. The [research handoff](results/09_final_reports/REVIEW_HANDOFF.md) reports completed unimodal and fixed-averaging assessment in the common-support study. F2, augmented F2 and learned quality gates were skipped because participant-disjoint OOF predictions cannot be certified from the released identity metadata. Their omission is a failed eligibility gate, not a negative fitted-model result.

The [dataset overview](results/09_final_reports/DATASET_OVERVIEW.md), [validation](results/09_final_reports/DATASET_VALIDATION.md), [model implementation](results/09_final_reports/MODEL_IMPLEMENTATION.md) and [common-support configuration](experiments/common_support_v2/04_experiment_protocol/experiment_config.json) retain acquisition/source identity, preparation, target and observation-horizon rules. Use the [chapter map](../../docs/THESIS_CODE_MAP.md) for current source and assessment links.

[All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
