# PHM + REASSEMBLE — Bounded Final Validity Audit

## Purpose

Check whether the completed thesis results are numerically traceable, whether the
prediction task and possible shortcuts are described correctly, and whether the
main fusion finding survives reasonable alternative summaries.

This is NOT another architecture search. Numerical checking does not turn an
adaptive exploratory study into independent confirmation.

Repository:
`/home/student/Master_Thesis_WS/pi-multimodal-ad`

Read `AGENTS.md` and applicable project instructions first. Follow their approval
and preservation requirements. This request authorizes the non-destructive audit,
the limited diagnostic logistic models expressly specified below, and preparation
of human-review materials. It does not authorize model tuning beyond that scope.

Prefer a separate Codex review session. Write a separate audit implementation
rather than asking the original reporting program whether its own results match.
Describe this as independent computational checking, not independent human
certification, new data validation, or full training reproduction.

## Protect completed and ongoing work

Preserve:
- PHM, Intel and REASSEMBLE raw data and historical outputs;
- original Section 1, Section 1B, Section 2, Section 3 and final synthesis;
- the active `additional_improvements_executed` queue and its checkpoints;
- existing thesis matrices, reproducibility documents and master reasoning record.

Do not restart, stop, alter, or compete for the GPU with the additional-improvements
queue. No new deep-model training, pretrained-model download, dataset download,
relabelled performance evaluation, audio model, object-OOD model, or architecture
search is authorized.

Only use completed, sealed source artifacts. A handoff file's existence alone is
not proof that its run is complete: inspect status and manifests. Do not interpret
partially written additional-improvements outputs.

Run this audit CPU-side with bounded resources. Use the existing environment;
no automatic package upgrades. For new audit work use one CPU thread by default,
but do not change another process's environment. Do not delete files or rewrite Git
history. Below 30 GiB free, defer clip encoding; below 20 GiB, stop new substantial
writes and document the blocker.

## Output layout

Create a new UTC timestamped directory, refusing to overwrite any prior audit:

`artifacts/thesis/FINAL_VALIDITY_AUDIT/<UTC_RUN_ID>/`

Structure:

```text
00_protocol/
01_independent_result_check/
02_task_and_shortcut_audit/
03_sensitivity_and_operating_points/
04_human_review/
05_final_review/
```

Use a separate source/test namespace, for example:

```text
scripts/thesis/final_validity_audit/
tests/thesis/final_validity_audit/
```

Small reports belong in the audit directory. Store any clips outside Git under
the existing external-data/cache policy; include their paths and hashes in the
audit. Do not commit review keys or clips by accident.

## Evidence to read

Locate actual paths rather than guessing missing files:

- FINAL_REASSEMBLE_HANDOFF.md and THESIS_STORYLINE_ADDENDUM.md.
- Section 1, 1B, 2 and 3 protocols, handoffs, prediction artifacts and manifests.
- Modality-dropout report and checkpoints/provenance as needed.
- Cohort and nested split manifests.
- Historical PHM target-version ledger, LOEO report and recovery/reproducibility
  documents.
- Existing exposé matrix, claim matrix and reproducibility audit, when present.

The external master reasoning document may not exist in the repository. Do not
invent it, overwrite it, or treat its absence as a scientific failure.

Do not overwrite existing integration files, including:
`docs/thesis/final_ADDITIONAL_IMPROVEMENTS_INTEGRATION.md`
`artifacts/thesis/final_additional_improvements_decision.csv`.

Expected context, to verify from evidence rather than force:
- 4,530 REASSEMBLE segments, 509 failures, 148 recordings.
- Five outer/four inner recording-disjoint folds.
- Sensor-statistics AP approximately .4294.
- Static F2 AP approximately .4473.
- F2 minus sensors AP approximately .0179 [.0086, .0283].
- F2 is logistic stacking on calibrated branch probabilities.
- F6 is a masked scalar-logit process/quality gate.
- The primary task is retrospective completed-segment classification.
- PHM uses a provisional continuous target and regression metrics.

---

# STEP 0 — Freeze the audit before calculating new results

Save:
- Git HEAD and working-tree status;
- identities/hashes of source prediction files, configs, splits and sealed manifests;
- audit environment and disk state;
- the exact audit script revision;
- a registry of reused versus newly computed checks.

Write `00_protocol/AUDIT_PROTOCOL.md` before new numerical outcomes. Freeze:
- comparisons and source runs;
- metrics and their definitions;
- floating-point tolerances;
- bootstrap rules and random seed;
- human-sample algorithm;
- allowed diagnostic-model specifications;
- stopping and escalation rules.

Reuse existing evidence where a question has already been answered. Explicitly
state when a task is satisfied by a retained result instead of launching a duplicate.

Throughout, distinguish:
1. directly inspected evidence;
2. independent recomputation from predictions;
3. statements merely reported by another artifact;
4. reviewer interpretation;
5. missing evidence.

---

# TASK 1 — Independently reconstruct the headline results

## 1A. Validate identities before metrics

For each selected prediction file, verify:
- unique composite segment ID;
- recording ID and outer-fold assignment;
- exact match to the frozen cohort and label mapping;
- failure is the positive class;
- no missing/extra/duplicated samples;
- finite probabilities in [0,1], distinct from logits;
- matching sample order by identity, not assumed array position.

Join predictions by composite identity. Never align arrays merely because their
lengths match. Verify fold/sample membership against manifests rather than only
against labels embedded in prediction files.

Core comparisons:
- clean statistical sensors versus clean F2;
- clean F2 versus clean F6;
- highest visual Gaussian-noise F2 versus F5/F6;
- complete visual/sensor loss for ordinary and dropout-trained gates.

Include the original visual branch as the surviving-branch reference.

## 1B. Write a separate metric implementation

For headline numerical verification, do NOT import project result-generation or
metric wrappers.

Use a compact NumPy implementation for:
- average precision, grouping tied scores at a common threshold;
- AUROC using a rank/pair interpretation with half credit for ties;
- Brier score using calibrated probabilities.

Validate first on hand-calculable synthetic cases:
perfect ordering, reversed ordering, constant scores, mixed ties, duplicate
scores, empty input, and one-class input. A one-class AUROC must be undefined,
not silently set to zero or .5.

Cross-check against an established installed library as a second check.
Do not install a new environment.

For hard-decision metrics, use saved decisions or the exact retained
training-selected thresholds:
failure precision/recall, specificity, balanced accuracy and macro-F1.
Never choose new thresholds on outer-test outcomes.
Distinguish macro-F1 from failure-class F1.

ECE is secondary: reproduce the documented bin boundaries, edge convention and
weighting. If these are not recoverable, mark ECE incompletely specified instead
of assuming a convenient definition.

## 1C. Compare exact values correctly

Compare independent scores with machine-readable full-precision outputs.
Use an audit tolerance declared before comparing results, e.g. absolute 1e-8
for deterministic float64 score calculations, with dtype/serialization caveats
recorded in advance.

For rounded Markdown tables, compare using their display precision, not an
unattainable full-precision tolerance. Do not subtract rounded scores to overwrite
a paired difference computed from full-precision data.

No reported number is a target to tune the checker toward.

## 1D. Independently reproduce paired uncertainty

For the core paired differences, recompute 2,000 paired recording-cluster
bootstrap replicates. Sample whole recordings with replacement, retaining all
their segments and identical resampling for both models.

Use the historical seed and exact sampling rule when documented. Otherwise
freeze seed 20260928, report that the point estimate should reproduce but
percentile endpoints can differ by Monte Carlo variation, and compare the
algorithm and interpretation rather than demanding identical endpoints.

For a replicate lacking both classes, mark the affected metric undefined,
count/report it, and do not silently redraw until desirable precision appears.
Use valid replicates for the reported interval; flag materially inadequate support.

These are conditional intervals over retained predictions, not complete
retraining/model-selection uncertainty or simultaneous multiple-comparison bounds.

## 1E. Trace fitting scopes, not just file existence

Check all available outer/inner manifests for recording separation.

Then trace one deterministic representative outer fold (lowest fold ID; never
selected based on performance), and one nested assessment split, through:
- preprocessing/scalers;
- branch fitting and hyperparameter/epoch selection;
- branch calibration;
- branch-generated meta-training predictions;
- fusion fitting and threshold selection;
- outer predictions.

Require evidence that the assessed recording was excluded from every required
fitting/selection step. Inspect configs/source and retained provenance. A file
named "inner_oof" is not sufficient evidence by itself.

Report the coverage explicitly: a sampled deep trace does not certify every
execution step in every fold. If training identities are not retained, record
PROVENANCE GAP rather than silently declaring a pass.

## 1F. Check complete-loss invariants

Verify numerically that the documented fallback predictions equal the surviving
frozen calibrated branch. Verify hard decisions against the fallback's documented
threshold, which may differ from the two-modality fusion threshold.

Explain the architecture consequence separately from statistical inference:
with one available branch, normalized masked scalar-logit weights are exactly
0 and 1. With frozen surviving predictions and no learnable post-fallback path,
gate-only training cannot change that output.

## 1G. PHM scope check

Use existing PHM evidence to verify that current headline metrics are identified
by target version, evaluation level, actual train/validation grouping and run.
Do not combine retired fixed-split v2 numbers with v3 LOEO results.

Where PHM saved predictions are available and readable, apply analogous
independent MAE/RMSE checks. Otherwise mark the scope as document/provenance-only.
Do not redownload PHM, claim raw revalidation, or invent missing fusion inputs.

## Task 1 outputs

- `01_independent_result_check/01_INDEPENDENT_RESULT_CHECK.md`
- `metric_recomputation.csv`
- `paired_recomputation.csv`
- `fitting_scope_trace.md`
- `identity_checks.json`
- `discrepancies.json`

Classify findings as:
VERIFIED_NUMERICALLY / MATCHES_DISPLAY_PRECISION / DOCUMENTED_MONTE_CARLO_DIFFERENCE /
PROVENANCE_GAP / NUMERICAL_DISCREPANCY / LEAKAGE_SUSPECTED.

If an unexplained numerical discrepancy or suspected leakage affects a headline,
stop downstream predictive interpretation. Preserve the evidence and report the
affected claims. Do not patch historical output to make the checker pass.

---

# TASK 2 — Task boundary, shortcut diagnostics and human review

## 2A. Build an input-availability ledger

Inspect the actual data loader and feature/gate paths.

For every input or derived quantity record:
- source field/code location;
- how it is constructed;
- whether it is available at action start, during action, only after completion,
  or only from annotation;
- whether that availability was verified or assumed;
- whether it enters the existing model;
- the legitimate task interpretation;
- potential shortcut and existing evidence against it.

Cover:
annotated segment boundaries, action labels, full duration, progress resampling,
frame selection, padding/masks, sample counts, coverage and quality measurements,
controller/robot signals, absolute times, identifiers, filenames and free text.

Specifically check for:
- samples beyond the scored segment's end;
- inclusion of the next action or outcome-dependent trailing idle;
- off-by-one timestamp/index conventions;
- label-dependent trimming or missingness rules;
- whether the same extraction rules apply to successful and failed segments.

Full-segment information may be legitimate for retrospective classification.
Do not call it leakage solely because it becomes available after action start.
Instead make explicit why it does not establish early warning.

Likewise, visible failure consequences inside the stated segment are not
automatically an invalid shortcut for an outcome-classification task.

## 2B. One bounded diagnostic-baseline family

Run ONLY if not already answered by matching retained analyses.
This is the only newly authorized predictive fitting in this audit.

Freeze three diagnostic models before outcomes:
- D0: action only.
- D1: action + log(positive completed-segment duration).
- D2: action + log duration + already-audited coverage/missingness quantities.

Use one regularized logistic regression specification:
C=1, L2, no class weighting, fixed solver and convergence cap.
No feature search or tuning grid. Use the same configuration for all D models.

Eligible D2 inputs must be identifiable before fitting and genuinely derived
without the outcome label. Do not add filenames, absolute timestamps, recording
IDs, object text, suspected label encodings, raw visual embeddings or sensor
statistics. Mark outcome-contaminated candidate fields as prohibited.

Use existing outer/inner recording folds. Imputers, scaling, encoding, calibration
and thresholds are training-only. Reuse the frozen calibration/threshold policy,
not outer-test-selected cutoffs.

Compare D0/D1/D2 with one another and with the historical action-only and strong
sensor/F2 results, disclosing any specification differences. Results are
post-hoc exploratory diagnostics.

A strong D1/D2 result means acquisition/task metadata predicts outcome.
It does NOT prove the original model uses that shortcut or that physical signals
lack information. Report the alternative explanation without causal inflation.

## 2C. Prepare a blinded human audit — do not fabricate reviewer responses

Prepare 64 clips: eight for each action × recorded-outcome stratum
(4 actions × 2 outcomes). Use seed 20260928.

Sampling algorithm:
1. Determine eligible segments using the frozen cohort, not model correctness.
2. For each stratum, sample eight distinct recordings without replacement
   when available, then sample one eligible segment uniformly per recording.
3. If fewer than eight recordings exist in a stratum, use all, then fill
   deterministically from remaining segments and record the support limitation.
4. Record recordings repeated across strata. Never prefer visually dramatic
   failures, clean clips, disagreement cases or favorable predictions.

This recording-spread balanced sample is a qualitative/structured audit, not a
simple random sample of the whole cohort. Do not extrapolate its agreement rate
to population annotation error.

Prepare:
- anonymous random review IDs;
- outcome/score-masked filenames and folders;
- normal-speed in-segment video clips, matching the audited visual stream;
- two independently ordered reviewer sheets containing the SAME sampled cases;
- a separate restricted ID-to-source/label mapping.

Do not include recorded success/failure labels, predictions, confidences,
experiment grouping or descriptive identifiers in reviewer exports. Action type
may be included explicitly as task context.

Do not claim perfect blinding: source content or the author's prior knowledge
may still reveal context. Record limitations.

For boundary review only, an optional separately labelled context clip can show
one second before/after the interval where real data exist. It must NOT be used
to judge the scored model or fed into inference. Outcome review should be based
on the actual in-segment clip.

Do not add unverified audio. Do not silently alter image content or synthesize
missing frames. Report visibility/decoding limitations.

Encode compact review copies without modifying raw data; estimate size first,
with a maximum total clip budget of 2 GiB. Reduce presentation resolution or
defer encoding if needed; never drop unfavorable samples. Preserve a note about
encoding effects on visibility.

Reviewer fields:
review_id, reviewer_id, judged_outcome (success/failure/cannot_determine),
boundary_quality (acceptable/questionable/cannot_determine),
visibility (adequate/partial/insufficient), artifact_flag, short_reason.

Ask the thesis author and preferably one other technically informed person to
review independently, without consulting each other's answers. Do not invent
a second rater or claim expert verification when unavailable.

The agent must NEVER fill human ratings itself or use an AI-generated judgement
as an independent human annotation.

## 2D. Human return workflow

Generate an ingestion/analysis script, synthetic-tested but not run on invented
real ratings. It should validate IDs and completeness, preserve submitted sheets
immutably, and report:
- per-stratum counts, uncertainty and boundary flags;
- agreement with recorded labels, naming both numerator and denominator;
- "cannot determine" counts explicitly;
- if two raters respond, three-category inter-rater agreement and Cohen's kappa
  where defined;
- determinate-only summaries separately, without hiding exclusions.

Agreement is not proof of physical ground truth. Do not relabel the scored cohort,
drop disputed cases from performance tables, tune the model, or erase old reports.

If plausible label/boundary problems appear, produce an adjudication request.
Only a separately approved correction protocol may change labels or recompute
model performance.

Continue automated Task 3 while human review is pending.

## Task 2 outputs

- `02_task_and_shortcut_audit/02_TASK_AND_SHORTCUT_AUDIT.md`
- `input_availability.csv`
- `boundary_checks.json`
- `diagnostic_baselines.csv` and their OOF predictions, if run
- `04_human_review/REVIEWER_INSTRUCTIONS.md`
- `reviewer_A_blank.csv`, `reviewer_B_blank.csv`
- `review_export_manifest.json`
- `HUMAN_REVIEW_STATUS.md`

Keep the label/source key separately from the blind review package.
Initial status must be **PENDING_HUMAN_REVIEW**, not audit passed.

---

# TASK 3 — Sensitivity and practical operating points from frozen predictions

## 3A. Scope

Use original sealed U1 sensor, U2 visual and F2 static predictions.
Include F6 as a secondary clean comparator. Do not use "best model" chosen from
partial additional-improvements outputs. Do not retrain these models.

## 3B. Within-action actual fusion gain

For pick, insert, remove and place separately, report:
- segments and recordings;
- failures and recordings containing failures;
- success support and positive prevalence;
- U1 and F2 AP/AUROC;
- paired differences with recording-cluster intervals.

Reuse retained equivalent results rather than recomputing unnecessarily.

The prior complementarity table counts branch errors; it is NOT the actual
within-action fusion gain. Distinguish them.

Resample whole recordings and filter by action within each draw. Handle
single-class/empty draws explicitly. Flag fewer than five failure-containing
recordings or otherwise unstable subgroup support. Do not require a positive
significant result in every action and do not quietly exclude the place group.

Report all four groups. Do not pool action APs into a new headline chosen because
it looks better; AP depends on positive prevalence and score distribution.

## 3C. Equal-recording-weight sensitivity

Retain ordinary segment-weighted pooled metrics as primary.

For the alternative estimand assign each segment in recording r weight 1/n_r,
so every recording contributes equal total mass. Compute weighted pooled AP,
AUROC and Brier for U1/F2, plus their paired differences.

This is NOT the arithmetic mean of per-recording AUROCs, which may be undefined
for single-class recordings.

For bootstrap draws, each sampled occurrence of a recording contributes unit
mass; a recording drawn k times has per-segment weight k/n_r.
Report the weighted positive prevalence and label this:
"recording-balanced sensitivity analysis."

Do not replace the original reported metric. A change in effect describes
sensitivity to the target population weighting, not automatic invalidity.

## 3D. Translate the established operating points

Using saved decisions and the verified historical threshold rules, report:
TP, FP, TN, FN; failure precision/recall; specificity; false-positive rate;
flagged fraction; and false flags per 100 successful segments.

Also express:
- true failures per 100 issued failure flags;
- missed cases per 100 actual failures.

Use denominators explicitly and derive all counts from predictions. Explain that
outer folds may use different training-selected thresholds; this is evaluation
of the threshold-selection procedure, not one universal deployed cutoff.

Do not report false alarms per hour without validated operating-time exposure.
Do not equate prospective warning with retrospective outcome classification.

Do not optimize new thresholds on outer results. A new sensitivity-at-fixed-FPR
policy would require its own training-only selection; it is outside this bounded
audit unless already retained.

## Task 3 outputs

- `03_sensitivity_and_operating_points/03_SENSITIVITY_AND_OPERATING_POINTS.md`
- `per_action_fusion.csv`
- `recording_weight_sensitivity.csv`
- `operating_points.csv`
- `paired_sensitivity.json`

---

# FINAL SYNTHESIS AND STOP

Create:
- `05_final_review/FINAL_VALIDITY_AUDIT_HANDOFF.md`
- `05_final_review/VALIDITY_STORYLINE_ADDENDUM.md`
- `05_final_review/CLAIM_IMPACT_MATRIX.csv`
- `05_final_review/AUDIT_STATUS.json`
- `05_final_review/validation.json`
- `05_final_review/output_manifest.json`

The handoff must answer:
1. Do the main numerical results reproduce from retained predictions?
2. Which fitting-scope checks were directly traced, and which remain unverified?
3. Is the input/target boundary retrospective and consistently implemented?
4. Did metadata diagnostics identify alternative explanations?
5. What is the human-review status and, if available, what did reviewers find?
6. Do the fusion results change by action or recording weighting?
7. What do the selected operating points mean practically?
8. Which claims remain unchanged, need qualification, or must be suspended?
9. Which limitations cannot be removed with the existing data?
10. Is any correction necessary, rather than merely another experiment possible?

For each check include: question, reason, exact method, source artifact, result,
uncertainty, limitation, consequence and status. Separate measured findings from
suggested explanations.

Do not change the exposé/claim/master reasoning documents directly. Provide an
addendum suitable for later integration. Identify the current versus historical
claims and reference the existing documents, including user-edited filenames.

Use separate status fields for:
automated_numerical_audit,
fitting_scope_trace,
task_boundary_audit,
diagnostic_baselines,
sensitivity_analysis,
human_review,
headline_claims.

Allowed final headline statuses:

**AUTOMATED VALIDITY AUDIT COMPLETE — HUMAN REVIEW PENDING**

**VALIDITY AUDIT COMPLETE — NO UNRESOLVED MATERIAL FINDINGS IDENTIFIED WITHIN AUDIT SCOPE**

**VALIDITY AUDIT COMPLETE WITH LIMITATIONS — GAPS DOCUMENTED**

**VALIDITY AUDIT BLOCKED — AFFECTED CLAIMS REQUIRE REVIEW**

Never announce the full human audit complete before actual reviewer returns.
Human review pending must not block numerical/sensitivity work.

Tests must cover metric ties, identity joins, cluster pairing, equal-recording
weights, one-class handling, training-only diagnostic transforms, blind-export
label masking, reviewer-sheet ingestion and historical-file preservation.

No independent dataset was added. More bootstrap draws, new weighting, metadata
models or human spot-checks do not erase adaptivity or establish unseen-site,
physical-object or online generalization.

After these outputs, STOP. Do not launch new architectures or repeat analyses
until the conclusion becomes favorable. Report a concrete correction request
only if a material validity issue is found.
