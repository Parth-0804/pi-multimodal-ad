# VIFAILBACK

Multiview completed-episode outcome classification. This is the canonical browsing entry under implementations/. Linked folders retain the original immutable data and frozen experiment locations; no raw data or checkpoint is copied or moved.

| Stage | Location |
|---|---|
| 01 — Dataset source | [Original dataset and acquisition](01_original_dataset) |
| 02 — Verification | [Labels, alignment and availability](02_dataset_verification) |
| 03 — Preprocessing | [Representations](03_preprocessing) |
| 04 — Protocol and splits | [Evaluation splits](04_evaluation_splits); [Study workspaces](experiments) |
| 05 — Models and training | [Model definitions](05_model_implementations); [Training records](06_training_experiments) |
| 06 — Assessment | [Dataset-level results](09_evaluation_results); [Latest completed-scope analysis](latest_results/RESULT_ANALYSIS.md) |
| 07 — Robustness | [Condition-specific work](07_robustness_experiments) |
| 08 — Examples | [Examples and EDA](08_visual_examples_and_eda) |
| 09 — Reports | [Historical reports](10_final_research_reports); [Current training comparison](latest_results/TRAINING_COMPARISON.md) |

[Source](src) · [Scripts](scripts) · [Configurations](configs) · [Tests](tests)

The current training queue is closed by the researcher. Unexecuted fits are not negative model results. Use the study-local stop, coverage and analysis records for actual completion; the older dataset-level status may describe an earlier plan. No restart is authorized by this navigation.

## Thesis and evidence

Chapter 8; existing evidence E087–E105, E115–E116 and E123. The [completed-scope analysis](latest_results/RESULT_ANALYSIS.md) reports full frozen/donor 20-epoch coverage, limited FULL20 coverage and separate 100-epoch pilots. The available matched full-CNN intervals are inconclusive; they do not establish equivalence. Metrics use both-class macro average precision; the pilot meta bank differs from the nested OOF bank, so duration is not an isolated treatment. Unexecuted robustness work supplies no robustness finding.

The [original dataset/label verification](../../VIFAILBACK/10_final_research_reports/02_DATASET_AND_LABEL_VERIFICATION.md), [preprocessing report](../../VIFAILBACK/10_final_research_reports/03_DATA_PREPROCESSING.md), [original protocol](../../VIFAILBACK/configs/protocol.json) and matched study's [protocol/source evidence](../../VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/01_protocol_and_source_evidence/) preserve source/version, inputs, task partitions and model provenance. Use the [chapter map](../../docs/THESIS_CODE_MAP.md) to distinguish original and matched studies.

[Original workspace](../../VIFAILBACK/README.md) · [All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
