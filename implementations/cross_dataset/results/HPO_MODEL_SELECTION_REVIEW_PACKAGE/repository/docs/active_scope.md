# Active PHM 2026 experimental scope

## Authority

This document is the canonical human-readable scope for the active thesis
pipeline. Historical scripts and notes may describe narrower studies; they do
not override this scope.

## Included experiments and runs

| Experiment | Included runs | Current raw HF archive coverage |
|---|---|---|
| EXP-A | 1, 2, 3, 4, 5 | Runs 1–5 present by filename |
| EXP-B | 1, 2, 3, 4, 5, 6, 7 | Runs 1–7 present by filename |
| EXP-F | 1, 2, 3, 4, 5, 6, 7, 8 | Runs 1–8 present by filename |

HF, nested LF, nested CI, and photo modalities are within pipeline scope where
the dataset provides them. Presence in the baseline is filename-level evidence,
not a completed integrity or schema assessment.

Experiments other than EXP-A, EXP-B, and EXP-F are outside the active scope
unless the researcher explicitly changes this document and the canonical
configuration.

## EXP-A Run-2 duplication warning

Challenge-organizer information reported 311 Run-2 files overlapping Run 1.
This is a data-integrity warning, not permission to remove or alter either run.
The count has not yet been independently verified.

The future configuration and integrity pipeline must:

- include Run 2 in the registry;
- attach the warning to Run 2 and identify Run 1 as the related run;
- use a configurable duplicate policy;
- report the chosen policy in manifests and results;
- default to reporting rather than excluding data;
- never delete, rewrite, or deduplicate raw archives or members.

Supported policies are to be implemented and tested later. Candidate policies
include including all members, excluding only confirmed duplicate members from
derived analysis, and comparing the affected runs separately.

## Interpretation constraints

- Run number is an experimental/lifecycle identity, not a damage score.
- Early, intermediate, and late stages are relative positions, not
  healthy/damaged/failed labels.
- Distribution shift does not by itself prove degradation.
- Speed, torque, temperature, experiment design, and sensor/schema differences
  may confound comparisons.
- Within-experiment results should precede cross-experiment comparisons.

## Historical EXP-A study

`experiments/exp_a_initial_eda_r1_r3_r5/` remains a protected historical
experiment covering EXP-A Runs 1, 3, and 5. Its narrower scope had computational
and duplicate-warning motivations and retains research value. It must not be
rewritten or presented as the current all-run implementation.

## Machine-readable scope

Canonical YAML configuration and validation are scheduled for restructuring
Phase 4. Until then, this document and `docs/restructuring/TASKS.md` define the
scope; existing scripts are not yet compliant.
