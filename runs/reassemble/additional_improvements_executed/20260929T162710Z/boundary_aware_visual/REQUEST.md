# REASSEMBLE — SMALL FOLLOW-UP: BOUNDARY-AWARE VISUAL POOLING

## Objective

Test whether the current visual branch loses useful failure information because it temporally averages the entire action segment too aggressively.

This experiment is motivated by the blinded human review:

- 59/64 clips were judgeable.
- 57/59 determinate human judgements agreed with the recorded outcome.
- 5/64 clips were `cannot_determine`.
- uncertainty/disagreement was concentrated more on failure cases than success cases.
- some cases had questionable boundaries or possible artifacts.

IMPORTANT:

The 64 human-reviewed clips are MOTIVATION ONLY.

Do NOT use:
- reviewer judgements
- reviewed-case identities
- flagged-case status
- human-review disagreements

for model training, hyperparameter selection, fold selection, or threshold tuning.

The original nested recording-disjoint evaluation remains unchanged.

This is an exploratory follow-up and must remain separate from the completed core REASSEMBLE study.

==================================================
1. PRESERVE EXISTING EVIDENCE
==================================================

Read:

- AGENTS.md
- completed Section 1 / 1B / 2 reports
- final REASSEMBLE handoff
- human-review evaluation
- current additional-improvements run status

Do not modify historical results.

Create a new run under:

runs/reassemble/additional_improvements_executed/<timestamp>/boundary_aware_visual/

Create final report:

artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md

==================================================
2. SCIENTIFIC QUESTION
==================================================

Current RT-DETR visual representation:

16 deterministic frames sampled through the annotated segment

→ frozen RT-DETR frame embeddings

→ temporal mean pooling

→ visual failure score.

Question:

> Does preserving coarse temporal position within the action segment improve visual failure prediction compared with whole-segment mean pooling?

Hypothesis:

Failure evidence may be concentrated near action transitions or consequences, so averaging the entire segment may dilute useful information.

This hypothesis must be tested prospectively.

==================================================
3. USE EXISTING CACHED VISUAL FEATURES
==================================================

Prefer the already validated frozen RT-DETR frame-embedding cache.

Do NOT re-run RT-DETR extraction unless required.

Before use, verify:

- source hashes
- frame indices
- segment IDs
- fold identities
- embedding dimensions
- cache preprocessing configuration

match the frozen Section-1 visual branch.

If the cache differs:

STOP and report rather than silently rebuilding a different representation.

==================================================
4. KEEP RT-DETR FROZEN
==================================================

No backbone fine-tuning.

No new visual architecture.

No new camera.

No additional frames beyond the already frozen 16-frame sequence unless absolutely required for parity.

The only experimental variable is TEMPORAL AGGREGATION.

==================================================
5. FIXED EVALUATION
==================================================

Use the exact same:

- 4,530 primary segments
- 148 recordings
- labels
- 5 outer folds
- 4 inner folds
- recording grouping
- calibration procedure
- threshold procedure
- uncertainty procedure

as the completed visual experiment.

Do not create new folds.

==================================================
6. PRIMARY CONTROL
==================================================

Reproduce the historical RT-DETR whole-segment mean-pooling result exactly.

Expected approximately:

AUROC 0.6978
AUPRC 0.2307

but verify from frozen artifacts.

Require reproduction within the existing parity tolerance before running variants.

If control does not reproduce:

STOP.

==================================================
7. TEMPORAL AGGREGATION VARIANTS
==================================================

Test ONLY these predefined variants.

Do not add new variants after looking at results.

--------------------------------------------------
V0 — FULL SEGMENT MEAN
--------------------------------------------------

Historical control.

Mean all 16 frame embeddings.

--------------------------------------------------
V1 — FIRST HALF / SECOND HALF
--------------------------------------------------

Frames 1–8:
mean → z_first

Frames 9–16:
mean → z_second

Concatenate:

[z_first ; z_second]

Then small classifier head.

Purpose:

retain coarse early/late information.

--------------------------------------------------
V2 — FIRST QUARTER / MIDDLE / LAST QUARTER
--------------------------------------------------

Frames:

1–4 → early mean

5–12 → middle mean

13–16 → late mean

Concatenate:

[z_early ; z_middle ; z_late]

Then small classifier.

Purpose:

preserve action boundary/context without complex temporal modelling.

--------------------------------------------------
V3 — LAST-QUARTER ONLY
--------------------------------------------------

Mean frames 13–16 only.

Purpose:

test whether outcome evidence is concentrated toward the action end.

This is specifically motivated by retrospective failure consequences potentially appearing late in the annotated interval.

--------------------------------------------------
V4 — EARLY + LATE
--------------------------------------------------

Mean frames 1–4

and frames 13–16

Concatenate:

[z_early ; z_late]

Ignore middle frames.

Purpose:

retain transition information while reducing dilution.

--------------------------------------------------
V5 — SMALL ORDERED TEMPORAL POOLER
--------------------------------------------------

Use the 16 frozen frame embeddings in order.

Add explicit positional encoding.

Use ONE lightweight sequence model only.

Preferred:

single-layer GRU
or
single-layer Transformer encoder

Choose one BEFORE results based on easiest existing implementation.

Maximum capacity:

hidden dimension <=128
1 layer
dropout <=0.1

Then pooled output → classifier.

Do not compare multiple temporal neural architectures.

==================================================
8. PARAMETER FAIRNESS
==================================================

V1–V4 classifiers should remain small.

If concatenation increases input dimensionality, use projections so classifier capacity does not explode.

Document trainable parameter count for each variant.

The purpose is testing temporal structure, not simply giving later variants many more parameters.

==================================================
9. TRAINING BUDGET
==================================================

Use the same general head-training procedure as the historical RT-DETR model.

Predeclare a small epoch grid such as:

5
10

If V5 needs additional convergence budget, allow at most:

5
10
20

selected strictly by inner-CV AUPRC.

Do not expand after seeing outer results.

Minimum 3 seeds for trainable neural variants if the existing visual protocol used multiple seeds; otherwise preserve the historical seed policy.

==================================================
10. PRIMARY METRICS
==================================================

Report:

AUROC
AUPRC

Secondary:

balanced accuracy
macro-F1
failure recall
failure precision
Brier
ECE.

Failure remains the positive class.

Use recording-clustered uncertainty.

==================================================
11. PRIMARY COMPARISON
==================================================

Every temporal variant is compared against:

V0 historical mean pooling.

Report paired:

delta AUPRC

delta AUROC

95% recording-cluster intervals.

==================================================
12. MULTIPLICITY / EXPLORATORY STATUS
==================================================

This experiment compares several temporal aggregation rules.

Therefore:

- report all variants;
- do not hide losing variants;
- do not call the best point estimate a confirmed winner without considering multiplicity and uncertainty;
- label this entire study EXPLORATORY.

Do not introduce another independent architecture after the best variant is known.

==================================================
13. ACTION BREAKDOWN
==================================================

For the historical V0 and the strongest predeclared temporal variant, report performance by:

pick
insert
remove
place.

This is descriptive/exploratory only.

Question:

Does temporal pooling help especially in actions where consequences may become visible near the boundary?

Do not use action-specific results to select the model.

==================================================
14. FAILURE-SIDE ANALYSIS
==================================================

Since the human review showed greater ambiguity on failure examples, calculate:

failure recall

failure precision

false negatives

per-recording failure rescue counts.

Compare best temporal variant vs V0.

Report:

number of V0-missed failures corrected by the temporal variant

number of V0-correct failures lost by the temporal variant.

Do not cross-reference human-reviewed-case identities.

==================================================
15. CONFIDENCE / SELECTIVE-PREDICTION DIAGNOSTIC
==================================================

As a SECONDARY analysis only:

Using inner-CV predictions, define uncertainty from predicted probability distance to 0.5 or entropy.

Do NOT use human-reviewed clips to tune a threshold.

Evaluate outer predictions at predeclared retained-coverage levels:

100%
90%
80%

Report:

coverage
AUROC/AUPRC on retained cases
failure recall
indeterminate/abstention count.

This is NOT a replacement for the main all-sample metrics.

Purpose:

determine whether ambiguous predictions can be identified computationally.

==================================================
16. DO NOT RELABEL DATA
==================================================

Human review does NOT authorize:

- changing labels
- removing disputed cases
- removing cannot-determine cases
- modifying boundaries
- tuning the model on those 64 clips.

Any annotation correction requires its own separately approved protocol.

==================================================
17. RESULT CLASSIFICATION
==================================================

At the end classify the outcome as one:

A. TEMPORAL STRUCTURE HELPS

A predefined temporal variant improves AUPRC over V0 with positive paired interval and no material contradictory AUROC degradation.

B. TEMPORAL STRUCTURE HELPS WEAKLY

Point estimate improves, but uncertainty overlaps zero.

C. LATE-SEGMENT SIGNAL ONLY

V3 improves meaningfully but richer temporal aggregation does not.

D. NO EVIDENCE TEMPORAL POOLING HELPS

No temporal variant improves convincingly over mean pooling.

E. TEMPORAL COMPLEXITY HURTS

Ordered models perform worse than V0.

All are valid.

==================================================
18. FUSION FOLLOW-UP — ONLY IF VISUAL MODEL IMPROVES
==================================================

If one temporal variant satisfies result class A:

run ONE follow-up only.

Use that improved visual probability with the frozen statistical sensor branch.

Reuse the exact Section-1B learned static stacking procedure.

Compare:

original F2
vs
new temporal-visual + sensor F2.

Do not rerun gates.

Do not build a new fusion architecture.

Report:

delta AUROC
delta AUPRC
paired recording-cluster intervals.

Question:

Does improved visual representation translate into improved multimodal fusion?

If temporal variant does not achieve class A:

do NOT run fusion follow-up.

==================================================
19. DOCUMENTATION
==================================================

Create:

`artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md`

Required sections:

## A. Motivation from human review

State only aggregate human-review findings.

Do not use reviewed identities.

## B. Hypothesis

## C. Historical control reproduction

## D. Temporal aggregation variants

## E. Parameter/training fairness

## F. Main metrics

## G. Paired comparisons

## H. Action-level analysis

## I. Failure-side rescue analysis

## J. Selective-prediction diagnostic

## K. Fusion follow-up, if triggered

## L. Failed variants

## M. Interpretation

## N. Exact thesis-safe claim

## O. Claims not supported

## P. Limitations

## Q. Provenance

## R. Recommended thesis placement

==================================================
20. STORYLINE ADDENDUM
==================================================

Create:

`artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_STORYLINE_ADDENDUM.md`

Use:

ASSUMPTION

QUESTION

WHY IT MATTERED

METHOD

RESULT

INTERPRETATION

STATUS

CONSEQUENCE.

This will later be merged into the master Reasoning Record.

==================================================
21. PRESERVATION
==================================================

Verify after completion:

- Section 1 unchanged
- Section 1B unchanged
- Section 2 unchanged
- robustness evidence unchanged
- human-review submissions unchanged
- raw HDF5 unchanged
- existing additional-improvement runs unchanged.

Use a new run directory only.

==================================================
22. FINAL STATUS FILE
==================================================

Create:

`artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_STATUS.md`

Start with one exact line:

BOUNDARY-AWARE VISUAL EXPERIMENT COMPLETE

Then report:

- best predefined variant
- historical V0 AUPRC/AUROC
- new variant AUPRC/AUROC
- paired differences
- failure-rescue count
- whether fusion follow-up was triggered
- result class A/B/C/D/E
- thesis recommendation.

==================================================
23. STOP
==================================================

After the report is written:

STOP.

Do not:

- fine-tune RT-DETR
- invent new temporal architectures
- modify labels
- change action boundaries
- add audio
- retune sensor models
- rerun gated fusion.

This is a bounded exploratory follow-up only.