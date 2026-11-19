# Canonical MSM migration

The new canonical root is MSM/. No historical source, raw data or result was moved, renamed or overwritten. MSM/01_raw_dataset/official_dataset is a verified relative symlink to the version-2 raw directory. MSM/99_preserved_previous_work/MILLING_DATASET references the complete historical tree.

Physical relocation is deferred because historical manifests/configurations embed MILLING DATASET paths and active independent processes must not be disrupted. All new model inputs, splits, checkpoints, predictions, robustness results and reports are written under MSM/. Existing implementations are imported via the preserved reference rather than duplicated. No additional migration approval is needed to use these safe canonical references.
