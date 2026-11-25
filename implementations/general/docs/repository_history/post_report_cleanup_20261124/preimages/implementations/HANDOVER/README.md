# HANDOVER

Robot handover success/failure classification. Preserve the study's grouping
limits and mandatory out-of-fold prediction gates when interpreting learned
fusion; recording identities do not establish participant independence.

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
| Separate common-support study | [experiments/common_support_v2](experiments/common_support_v2) |
| Workspace documentation | [docs](docs), [preserved workspace guide](docs/WORKSPACE.md) |

Native inputs remain at `HANDOVER/01_raw_dataset/`; the study's existing raw-access
link remains at its original location. Model and report contents retain their
study identities. Use each study's protocol, manifests and eligibility decisions.

Old source aliases were removed. Source-path and packaging updates remain
unfinished; use the [move mapping](../general/docs/repository_history/dataset_layout_cleanup.json)
for historical paths.

[All implementations](../README.md) · [Repository map](../../REPO_MAP.md)
