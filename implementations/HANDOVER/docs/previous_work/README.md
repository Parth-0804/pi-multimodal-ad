# Preserved Handover audit history

The first full-video audit remains unchanged in the canonical root's
`02_labels_and_alignment/`, `03_processed_model_inputs/` and
`04_experiment_protocol/` files. It retained335/101/59 train/validation/test
trials and was never used to fit or score a model.

Before any Handover model score, the common-support amendment froze the
intersection of actual camera and raw-wrench recording support, using the same
rule for every robot, task and outcome. The active version is
`HANDOVER/experiments/common_support_v2/`, with335/101/151 eligible trials.
The earlier audit was not moved or overwritten. Root-stage
`active_common_support_v2` references identify the evaluated cohort.

The exact amendment is
`HANDOVER/04_experiment_protocol/COMMON_SUPPORT_AMENDMENT.json`. The separate
split-qualified trial-ID correction is recorded in
`HANDOVER/01_raw_dataset/source_evidence/split_identifier_namespace_correction.json`.
Neither correction invents participant identities or changes native labels.
