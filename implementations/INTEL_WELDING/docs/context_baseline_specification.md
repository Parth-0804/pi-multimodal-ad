# Context-only shortcut baseline specification — not executed

Status: blocked pending holdout recovery, grouping review and leakage clearance.
The prior context scores are contaminated exploratory evidence, not validated
performance. No new training is authorized in this foundation pass.

## Inputs and tasks

Allow only WELD_TYPE, STEEL_TYPE, THICKNESS_MM, CURRENT_A, VOLTAGE_V,
GAS_BAR and ROBOT_SPEED_CPM. Exclude CATEGORY-derived variables, DIRECTORY,
SUBDIRS, sample/session identifiers, SAMPLES, SPLIT, paths, filenames, absolute
timestamps and post-weld measurements. Persist the exact allow-list in config.
Inspect actual fields before interpreting units as validated sensor quantities.

Primary: Good versus non-Good intended condition, AUROC. Secondary: twelve-label
intended-condition diagnosis, macro-F1, explicitly reporting unsupported classes.
Do not silently turn the secondary task into a nine-class task. If a secondary
supported-category subset is used, label it separately and retain the twelve-class
support table. Report undefined metrics as undefined, not zero or fabricated AUROC.

## Fixed candidate models

1. Prior-probability dummy and majority decision rule, distinguished explicitly.
2. Logistic regression with C in {0.1, 1, 10}, max_iter=2000.
3. Decision tree with depth in {2, 3, 5}, min_samples_leaf=5.
4. Random forest with 300 trees, depth in {3, 5}, min_samples_leaf=5.

Use seeds 0, 1 and 2; identical outer folds across models. No test-based selection.
Numeric median imputation and standardization, categorical missing-value handling
and one-hot encoding fit inside training folds. Unknown categories are supported.
Hyperparameter selection uses nested group-disjoint development folds only.
No tuning if independent session support is inadequate. Report this precondition.

## Evaluation and uncertainty

After establishing a valid frozen protocol, use five session-disjoint development
folds when both classes have sufficient session support; document any reduction
before model outcomes. Validate class coverage in every training/validation fold.
Preserve every sample's session, true intended label, fold, logits/probabilities,
prediction and model seed in machine-readable OOF output. Sessions used for final
test must never be passed to fitting, selection or diagnostic model evaluation.

Report binary AUROC, AUPRC, macro-F1, balanced accuracy, Brier and calibration,
multiclass macro-F1/per-class metrics and confusion matrices. For development
threshold-dependent metrics, choose thresholds and fit calibration inside the
outer training fold using inner OOF predictions. Select final frozen rules from
development predictions only after comparisons. Define ECE bins before use.

Use 2,000 session-cluster bootstrap replicates and 95% percentile intervals;
resample whole sessions with replacement and report rejected one-class draws.
Use paired draws for model differences. Report pooled OOF and fold-level AUROC
separately: fold-specific prior scores can give pooled dummy AUROC below 0.5 even
when each fold has constant predictions. No claim of a below-chance physical model
should follow from that artifact.

Compute permutation importance on each held-out development fold, aggregate by
session, and acknowledge correlated process variables. Recipe uniqueness and
category-by-setting tables are descriptive confound evidence, not performance.
A session-ID probe is optional and would require an explicitly justified within-
development identification protocol; it must not be presented as group-disjoint
unseen-session generalization or bypass the prohibition on random sample splits.

## Required comparisons and interpretation

Compare physical-modality-only, context-only and physical modality plus context.
High recipe predictability may reflect intended experimental settings; it does not
establish detection of a verified physical defect. No positive architectural
conclusion follows from the historical context scores. Persist config, seed,
commit/dirty-state, manifest/split hashes, environment, command, OOF predictions,
metrics, warnings and fitted pipeline for every future run.
