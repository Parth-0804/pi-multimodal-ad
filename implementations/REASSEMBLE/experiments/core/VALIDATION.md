# Numbered REASSEMBLE navigation: validation

This phase adds an experiment reading layout. It does not relocate implementation, checkpoints, datasets or historical runs.

| Check | Result |
|---|---|
| Frozen cohort | 4,530 segments; 509 failures; 148 recordings |
| Prediction identity | All three primary files have 4,530 rows, matching cohort labels and outer-fold assignments |
| Recording separation | Five outer folds and their four inner folds preserve train/held-out recording separation |
| Saved metric cross-check | AUROC and average precision recomputed from existing predictions match each recorded estimate to absolute tolerance 1e-12 |
| Static fusion identity | Section 1B predictions exactly match the Section 2 F2 probabilities, hard decisions, labels and fold IDs |
| Example trace | Cohort row 3326 maps to the saved recording cache: visual [896], sensor [512,22], statistics [220], frame indices [16] |
| Shortcuts | All 26 use relative targets and resolve to the intended originals |
| Original-file preservation | All 67 referenced originals retain their before/after SHA256, size and mtime |
| Markdown navigation | All relative Markdown links in these new guides resolve locally |
| Formatting | `git diff --check` passed; new guides have no trailing whitespace |
| Environment | `ma_thesis_env/bin/python -B -m pip check`: No broken requirements found |

The checks read existing numerical arrays and recompute evaluation metrics only. No training, predictive inference, model download, raw-data access, report regeneration or Task 4 execution was performed in this organization phase. Model parameters were not loaded/executed. These checks do not reproduce training or independently validate every scientific claim, confidence interval, gate, or later experiment.

Changed files: 26 walkthrough Markdown files, this validation report, one navigation manifest, and 26 relative symbolic shortcuts under `experiments/reassemble/`; `REPO_MAP.md` gains the entry link. Three NPZ shortcut names remain ignored by the existing bulk-artifact rules; the manifest and guides retain their canonical locations. No ignore rules were changed, and nothing was staged or committed.

`git diff --stat -- REPO_MAP.md` reports **1 file changed, 2 insertions**. Untracked additions are not counted by `git diff --stat`. The full worktree diff also contains the pre-existing deletion of `src/shared/README.md` (7 deletions); this phase leaves it unchanged. Pre-existing `artifacts/presentation/` and `tutorials/reassemble/` additions are also left unchanged.

Next action: review the [start page](README.md), then follow one experiment from 00 to 03. This completes the selected REASSEMBLE navigation phase; expanding the layout to PHM or later experiments is a separate phase awaiting the researcher's approval.

See [navigation_manifest.json](navigation_manifest.json) for every shortcut's original path and the source checksums captured during this phase.
