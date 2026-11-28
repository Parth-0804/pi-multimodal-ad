# VIFAILBACK

Multiview completed-episode outcome classification. This is the canonical physical workspace under `implementations/`. The approved location-only relocation preserved original data, frozen source, configurations, checkpoints and saved-result identities. Historical manifests retain their original path names; no experiment was replayed.

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

The current training queue is closed by the researcher. Unexecuted fits are not negative model results. Use the study-local stop, coverage and analysis records for actual completion; the older dataset-level status may describe an earlier plan. Direct frozen-study CLI commands require the explicit context described in the [relocation activation guide](relocation/README.md), including activation in each participating Python process. The [relocation receipt](../general/docs/repository_history/root_cleanup_20261126/approved_relocation/README.md) records preservation and bounded source checks. No restart is authorized by this navigation.

## Thesis and evidence

Evidence IDs below follow the researcher-requested 28 November renumbering. The [complete mapping](../../00_thesis_writing_tracking/final_thesis_prep/evidence_publication_20261128/manifest.json) relates them to the prior IDs retained in historical records.

Chapter 8; current evidence E085–E103, E113–E114 and E121. The [completed-scope analysis](latest_results/RESULT_ANALYSIS.md) reports full frozen/donor 20-epoch coverage, limited FULL20 coverage and separate 100-epoch pilots. The available matched full-CNN intervals are inconclusive; they do not establish equivalence. Metrics use both-class macro average precision; the pilot meta bank differs from the nested OOF bank, so duration is not an isolated treatment. Unexecuted robustness work supplies no robustness finding.

The [original dataset/label verification](10_final_research_reports/02_DATASET_AND_LABEL_VERIFICATION.md), [preprocessing report](10_final_research_reports/03_DATA_PREPROCESSING.md), [original protocol](configs/protocol.json) and matched study's [protocol/source evidence](experiments/matched_cnn_20_100_f2_20261111/01_protocol_and_source_evidence/) preserve source/version, inputs, task partitions and model provenance. Use the [chapter map](../../docs/THESIS_CODE_MAP.md) to distinguish original and matched studies.

[Preserved original workspace guide](docs/WORKSPACE_BEFORE_CONSOLIDATION.md) · [Independent dataset verification](02_dataset_verification/independent_verification/) · [All datasets](../README.md) · [Repository map](../../REPO_MAP.md)
