# REASSEMBLE — Additional Improvements Executed

## Purpose and authorization

Execute a bounded exploratory follow-up to the completed REASSEMBLE study.
Test four proposed improvements; do not assume any will improve performance.

Repository:
`/home/student/Master_Thesis_WS/pi-multimodal-ad`

Read `AGENTS.md`, the final REASSEMBLE handoff, continuation files, and original
Section 1/1B/2/3 configurations before work. Follow applicable repository policy.
This request authorizes the four non-destructive experiments below, not new
datasets, indefinite tuning, deleting data, altering completed evidence, or
external publication.

The original study remains complete. Its results, final reports, and conclusions
must not be overwritten. This extension was motivated by already-observed
results on the same cohort; nested fitting does NOT make it independent
confirmation. Label all new results **ADDITIONAL EXPLORATORY EXPERIMENTS**.

Do not run audio, object-OOD modelling, PHM experiments, or a new backbone search.
Do not change data exclusions, labels, camera, statistical sensor features, or
outer folds to improve scores.

## Output location and naming

Create one new, timestamped root:

`runs/reassemble/additional_improvements_executed/<UTC_RUN_ID>/`

Use these subfolders:

```text
00_protocol_and_preservation/
01_temporal_visual/
02_patchtst_training_budget/
03_static_anchored_adaptation/
04_corruption_training/
05_final_comparison/
reports/
```

Place new source and configuration files in an isolated namespace, for example:

```text
scripts/reassemble/additional_improvements/
configs/reassemble/additional_improvements/
tests/reassemble/additional_improvements/
```

Reuse existing implementations through imports/wrappers where correct.
Do not silently patch the implementations used for the sealed experiments.

Create the root and task status files before execution. "Improvements executed"
names the attempted interventions, not a claim that they succeeded.

---

# Shared protocol — applies to all four tasks

### 1. Verify evidence and freeze the plan

Read the actual source reports and machine-readable artifacts. Expected context:

- 4,530 segments, 509 failures, 148 recordings.
- Existing five outer / four inner recording-disjoint folds.
- Statistical sensors are the strongest established unimodal model.
- Frozen RT-DETR supplies complementary information.
- F2 is logistic stacking on calibrated branch probabilities, NOT a convex
  weighted average.
- Original F6 is a masked scalar-logit gate.
- PatchTST selected the maximum six-epoch budget in every outer fold.
- Audio and physical-object studies were excluded by feasibility checks.

Verify rather than transcribe these facts. Save source paths and hashes.

Before generating new real-data performance results, write and freeze:

`00_protocol_and_preservation/EXPLORATORY_PROTOCOL.md`
`00_protocol_and_preservation/experiment_matrix.json`

Record exact implementations, budgets, seeds, comparisons, corruption families,
stopping rules, and all deviations from the completed study.

### 2. Preserve completed work

Record Git state, input identities, historical output-manifest identities,
environment, hardware, and free disk. Reuse the existing preservation verifier;
do not hash the entire dataset repeatedly.

Protect Sections 1/1B/2/3, final synthesis, PHM, Intel, raw data, and external
thesis documents. Never overwrite historical checkpoints or reports.

Use the existing environment and pinned RT-DETR checkpoint. Do not upgrade
dependencies automatically. Discover the data root from the repository config.

### 3. Keep fitting genuinely nested

Use the exact existing cohort and outer folds. All preprocessing, hyperparameter
selection, early stopping, calibration, thresholds, and fusion fitting must use
outer-training recordings only.

Generate branch predictions for training a stacker/gate through recording-wise
cross-fitting. For every assessed inner recording, exclude it from branch
training, scaler fitting, model selection, and calibration. Reuse the validated
Section 1B sub-inner machinery when applicable.

The existing whole-cohort outer-OOF matrix is for comparison, NOT a training
matrix for a new fusion model that will be scored on those same rows.

For new neural branches, use three fixed seeds:
`20260927, 20260928, 20260929`.
Retain original published scores and also use matched new controls where seed
ensembling or training budgets would otherwise confound a comparison.

Within an outer fold, select epochs using inner validation only. Derive the
outer refit duration from the rounded median of selected inner best epochs;
refit on all outer-training recordings. No outer-test early stopping.

For new neural variants, the primary prediction is the mean of the three
seed probabilities calibrated using training-only data. Use that same rule
for matched neural controls; retain individual seed results separately.

Keep the established calibration and decision-threshold rules. Calibration of
new models must use training-only cross-fitted scores, not historical parameters
from a different model.

### 4. Metrics and interpretation

Failure is positive. Primary metric: **average precision (AP)**, explicitly
distinguished from trapezoidal PR-area calculations. Also report AUROC, balanced
accuracy, macro-F1, failure precision/recall, Brier, and 15-bin ECE using the
existing metric implementation.

Use 2,000 paired recording-cluster bootstrap replicates and show per-outer-fold
results. Intervals are conditional on fitted models and do not include all
training or adaptive-study-selection uncertainty. Seeds and segments are not
independent recording groups.

Freeze four principal contrasts:
1. Temporal visual model minus its budget-matched mean-pooling control: clean AP.
2. Longer-trained PatchTST minus its matched six-epoch control: clean AP.
3. Static-anchored adaptive model minus matched F2: clean AP.
4. Corruption-trained anchored adaptation minus corruption-trained static fusion:
   mean AP across the two seen corruption families' test conditions.

Report secondary comparisons separately, including comparisons against the
strongest original sensor model and original F2. Do not nominate a new primary
contrast after seeing results.

For a contrast, distinguish supported improvement, supported deterioration,
and inconclusive difference. A non-significant difference is not equivalence.
Treat 0.01 AP as a prospectively stated practical reference, not an established
industrial requirement. Show effect sizes regardless of whether they cross it.

### 5. Resource and failure policy

Run GPU jobs serially unless resource checks justify otherwise. Cache compact
features, not permanent decoded frame collections. Estimate cache bytes first.
Use the original execution settings when exact numerical parity is required;
record BLAS/threading differences rather than silently relaxing tolerances.

Below 30 GiB free: prohibit new large caches.
Below 20 GiB free: stop new writing/training safely and report the blocker.
No deletion is authorized to recover space.

For OOM, allow at most two documented microbatch reductions with gradient
accumulation preserving effective batch size. Do not change model size or
scientific budgets to chase a result.

Stop globally for leakage, changed protected inputs, or corrupt source data.
For an isolated task failure, mark that task blocked and continue independent
tasks if valid. Keep failed attempts and their logs. Never loop indefinitely
until a preferred model wins.

---

# TASK 1 — Preserve temporal information in the RT-DETR visual branch

## Question

Does retaining frame order improve execution-failure prediction compared with
the original temporal average? Separately, does limited fine-tuning help?

## Implementation

1. Keep the existing camera, 16 deterministic in-segment frame positions,
   pretrained RT-DETR revision, and image preprocessing exactly unchanged.
   Do not simultaneously change aspect-ratio handling, resolution, or crop.

2. Inspect caches. If only the segment-averaged vector was retained, extract
   the 16 per-frame vectors again using the pinned frozen backbone. A sequence
   cannot be reconstructed from its mean. Save source timestamps, masks,
   model/preprocessing hashes, and compact per-frame features.

3. Run these fixed variants:
   - **V-HIST:** sealed original visual result, unchanged.
   - **V-MEAN:** original mean-pooling architecture with the same new training
     budget and seed protocol as V-TEMP.
   - **V-TEMP:** per-frame linear projection to 128 dimensions; fixed positional
     encoding; one Transformer encoder layer, four heads, FFN 256, dropout 0.1;
     valid-frame mean pooling; binary head.
   - **V-NOPOS:** the same small temporal model without positional encoding,
     providing a matched order-insensitive control.

4. For V-MEAN/V-TEMP/V-NOPOS: maximum 100 epochs, minimum 10 before stopping,
   patience 12 on inner AP. Keep the original neural loss, class-weight,
   optimizer, and gradient-clipping conventions; freeze exact values before
   training. Do not expand this architecture grid.

5. Secondary **V-FT**: start from the training-fold V-TEMP fit, unfreeze only
   the final spatial backbone stage identified from the actual implementation,
   and fine-tune for at most 20 additional epochs, patience five. Proposed LRs:
   1e-5 for unfrozen pretrained weights and 1e-4 for the head.
   Freeze these before outcomes. Validate memory on synthetic tensors first.
   If unsupported within the resource policy, skip V-FT with an explicit reason.
   Frozen feature caches are invalid for this fine-tuning stage. Keep pretrained
   BatchNorm running statistics frozen; record exactly which parameters receive
   gradients and verify this with a synthetic forward/backward test.

6. With weights fixed, run frame-order reversal and deterministic permutation
   diagnostics. Verify V-MEAN is invariant within numerical tolerance.
   A V-TEMP score change alone does not prove useful temporal reasoning;
   assess predictive performance and the V-NOPOS comparison.

## Comparisons and limits

Compare V-TEMP with V-MEAN, not only with the shorter-trained historical model.
Compare V-TEMP with V-NOPOS to separate temporal order from added capacity.
Report V-FT separately: it adds supervised backbone adaptation and compute.

Do not insert the new visual branch into every fusion arm. This task isolates
visual representation changes.

## Required report

`reports/01_TEMPORAL_VISUAL_RESULTS.md`

Include the rationale, exact architecture, best epochs, losses/AP learning
curves, trainable parameters, clean metrics, paired contrasts, order diagnostics,
compute cost, failures, provenance, and conclusions. Distinguish "more capacity
helped" from evidence specifically supporting temporal order.

---

# TASK 2 — Test PatchTST's training-budget explanation

## Question

Was the six-epoch cap an important limitation, or do engineered sensor statistics
remain stronger after a reasonable convergence-oriented budget?

## Implementation

1. Keep all original PatchTST channels, 512-position resampling, normalization,
   patching, layers, widths, pooling, loss, optimizer and masking behavior.
   Do not quietly repair masking or enlarge the architecture in this task.

2. Compare:
   - **S-HIST:** sealed original PatchTST scores.
   - **S-6:** original 3/6-epoch selection procedure with the new three-seed
     protocol, as the matched short-budget control.
   - **S-LONG:** identical architecture with maximum 100 epochs, minimum 10,
     patience 12 on inner AP. Keep the original learning-rate rule initially.
   - **S-STATS:** the established statistical sensor reference.

3. Save every epoch's training loss and inner-validation AP/AUROC. Report whether
   each fold still reaches the cap. Reaching a cap permits an undertraining
   caveat, NOT another automatic budget extension.

4. Secondary **S-HYBRID**: combine calibrated S-LONG and S-STATS probabilities
   with one fixed C=1 logistic stacker using correctly nested cross-fitted
   predictions. This tests incremental temporal information; it is two
   representations of the SAME sensor modality, not a new modality.

## Comparisons and limits

Report S-LONG minus S-6 and S-LONG minus S-STATS. Report S-HYBRID minus S-STATS
separately. Do not declare longer training successful merely because it beats
the original one-seed score.

This task does not modify the primary sensor branch in Tasks 3–4: those keep
the validated statistical sensor model to isolate changes to fusion.

## Required report

`reports/02_PATCHTST_BUDGET_RESULTS.md`

Include selected/refit epochs, convergence plots, all comparisons, seed
variability, parameter and compute costs, any hybrid result, failed attempts,
and bounded interpretation of whether the original budget mattered.

---

# TASK 3 — Test adaptation without changing the successful fusion form

## Question

Can input-dependent coefficient adjustments improve the successful static
stacker when the branch inputs and output link are held constant?

## Fixed inputs

Use the ORIGINAL frozen RT-DETR branch procedure and statistical sensor branch
from the completed study. Do not use Task 1 or Task 2 improvements here.

For each proper training partition, obtain cross-fitted calibrated probabilities
p_v and p_s and reproduce the original F2 fitting procedure:

    l0 = b + a_v * p_v + a_s * p_s
    p0 = sigmoid(l0)

Fit b, a_v and a_s on training-only cross-fitted rows. Do not transfer an
outer-fitted anchor into an inner validation procedure.

## Static-anchored adaptation

Freeze each fitted anchor and define:

    l = b
        + a_v * (1 + tanh(h_v(u))) * p_v
        + a_s * (1 + tanh(h_s(u))) * p_s
    p = sigmoid(l)

Here u contains the already-defined process action, quality variables, and
availability mask. Use a one-hidden-layer MLP with 16 hidden units. Initialize
the final gate layer's weights and biases to zero.

At initialization, p MUST equal the corresponding F2 prediction numerically.
Do not force a softmax, change probabilities into branch logits, or add an
unrestricted context-dependent intercept.

Regularize the mean squared tanh adjustments. Predeclare lambda in
[0.01, 0.1, 1.0]; select only inside the inner procedure. Maximum 100 epochs,
patience 12; fix optimizer settings in the protocol.

## Controls

Compare:
- **A0:** reproduced F2.
- **A-CONSTANT:** identical bounded coefficient adjustment, but with global
  trainable constants instead of input-dependent h(u).
- **A-ADAPTIVE:** the process+quality input-dependent adjustment above.

This distinguishes an adaptive benefit from ordinary coefficient refitting.
Run neutral-quality and action-permutation diagnostics with weights frozen.

Report effective coefficients and their changes. These are NOT automatically
probability weights or causal explanations. If an anchor coefficient is
non-positive, preserve and report it; do not silently clamp it. Action-dependent
coefficients can still encode action-associated failure priors.

For exactly one available modality, explicitly return its frozen calibrated
probability and decision rule. For no available modalities, abstain. Verify
these identities; do not claim adaptive recovery under complete loss.

## Required report

`reports/03_STATIC_ANCHORED_ADAPTATION_RESULTS.md`

Include mathematical definitions, initialization-parity tests, branch and
cross-fitting identities, selected penalties, clean metrics, A-ADAPTIVE minus
A0/A-CONSTANT contrasts, ablations, coefficients, and limitations.

---

# TASK 4 — Train fusion on partial degradation and test separate corruptions

## Question

Does training on unreliable inputs improve robustness, and is adaptive fusion
better than a static model given the SAME corruption exposure?

Keep the original visual/statistical sensor branches frozen. Train fusion
layers, not the backbones, in this task.

## Training exposure

Before any new corruption result, freeze this mixture:

- 50% clean.
- 25% visual Gaussian noise, native [0,1] pixel SD sampled from [0.01, 0.08].
- 25% sensor Gaussian noise, alpha sampled from [0.05, 0.80] times the
  relevant training-partition channel SD.

Corrupt pixels before frozen visual extraction; corrupt sensor sequences before
the original statistics. Recompute the established quality variables from the
corrupted input. Never provide the gate with the injected severity, family ID,
random seed, target, or true corrupted-modality label.

Use four fixed training perturbation realizations per example/family, sampled
during fitting. Preserve parent-recording groups for every derived copy.
Normalize total example weight per original segment so augmentation does not
manufacture independent observations or change class weights through duplication.

For each cross-fitted training row, corrupted branch predictions must come from
models whose fitting/selection/calibration exclude that row's recording.
Noise scales and quality scaling must also exclude that assessment recording.

## Matched model comparisons

Evaluate clean-trained and corruption-trained versions of:
- **F2:** static probability stacker.
- **F6:** original masked scalar-logit gate, architecture unchanged.
- **A-ADAPTIVE:** Task 3's static-anchored architecture.

Use matched seeds, optimizer/search budgets, branch information, and examples.
For these matched robustness comparisons, use the SAME inner-selection objective:

    0.50 * clean AP
    + 0.25 * visual-noise validation AP
    + 0.25 * sensor-noise validation AP

Inner-validation corruption realizations must be separate from training.
Use only these two Gaussian families for selection, not held-out fault families.
Retain historical clean-trained checkpoints as additional references. If a
matched refit differs from them, report both; do not overwrite historical scores.

Comparing adaptive augmented fusion ONLY against clean-trained static fusion
is insufficient: F2 with the same augmentation is mandatory.

## Evaluation

Use five fixed new test-corruption realizations per stochastic condition,
separate from training and inner validation. Reuse the SAME realized corrupted
sample across all evaluated models. Record seeds and source hashes.

Seen-family test conditions:
- Visual Gaussian SD: 0.02, 0.05, 0.10.
- Sensor Gaussian alpha: 0.10, 0.50, 1.00.

The highest levels are outside the declared training-severity ranges.
Label the lower levels as in-range, not unseen severities.

Training-family-held-out conditions:
- Visual blur sigma 1, 2, 4.
- Frame dropout 2, 5, 8 of the original 16 frames.
- Sensor channel dropout 2, 7, 11 of the original 22 channels.
- Sensor temporal block dropout 10%, 30%, 50%.
- Six F/T channels stuck at training medians.
- Complete visual loss and complete sensor loss.

Reuse the established corruption semantics. These families were examined in the
original study, so call them "held out of augmentation training", NOT a new
untouched benchmark. New random realizations do not create new independent
recordings or remove outcome-informed design.

## Outcomes to report

For every condition show:
- absolute AP/AUROC and other established metrics;
- change from that model's clean performance;
- paired difference against clean F2 AND equally augmented F2;
- remaining unimodal branch performance;
- effective coefficient/gate-weight change on the corrupted modality.

Evaluate each corruption realization separately, then average metrics across
realizations. Do NOT average different noisy observations' predictions into an
unrealistic test-time denoising ensemble.

For uncertainty, resample paired recordings and additionally resample stochastic
realization indices when applicable; deterministic conditions have no synthetic
realization variance. Describe this as conditional evaluation uncertainty, not
full retraining uncertainty. Do not treat augmented copies as new patients/trials.

Report the primary seen-family mean AP with equal family and severity weights.
Report held-out families separately rather than hiding failures in one average.
Report 95% intervals as marginal unless a valid multiplicity adjustment is
implemented and described. Do not scan cells for a single favorable p-value.

Clean-performance preservation requires its own evidence. Report a prospective
0.01-AP noninferiority margin: a lower paired bound above -0.01 supports that
bounded statement; an interval spanning zero alone does not.

A reliability-adaptation claim requires both an appropriate coefficient/weight
response and a predictive benefit against the matched static comparator.
Complete-loss fallback remains structural, not a learnable improvement.

## Required report

`reports/04_CORRUPTION_TRAINING_RESULTS.md`

Include training and evaluation distributions, matched controls, all clean and
degraded results, replicate variability, absolute versus relative robustness,
seen versus training-held-out families, adaptation diagnostics, exact fallback
tests, failures and allowed/prohibited claims.

---

# Final consolidation — then stop

Do not automatically combine the winning visual, sensor and gate changes into a
new system. That would be another experiment with several simultaneous changes.
Describe it as future work requiring a separate protocol.

Create:

`reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md`
`reports/ADDITIONAL_IMPROVEMENTS_STORYLINE_ADDENDUM.md`
`reports/ADDITIONAL_IMPROVEMENTS_STATUS.md`
`05_final_comparison/results_summary.json`
`05_final_comparison/clean_comparisons.csv`
`05_final_comparison/robustness_comparisons.csv`
`05_final_comparison/experiment_registry.json`
`05_final_comparison/output_manifest.json`
`05_final_comparison/validation.json`

The main handoff must include:
1. Why each follow-up was proposed after the original completed study.
2. Historical reference, matched control, exact intervention, and result.
3. All primary contrasts, uncertainty, seed/fold consistency and compute cost.
4. What improved, worsened, or remained unresolved.
5. All unsuccessful attempts and protocol deviations.
6. Which original conclusions are qualified, and which remain unchanged.
7. Exact thesis-safe sentences and overstatements to avoid.
8. Every artifact/config/source/checkpoint path and Git identity.
9. Explicit outcome-informed/exploratory status.
10. Whether anything is blocked rather than complete.

The storyline addendum must use:
QUESTION -> ORIGINAL EVIDENCE -> HYPOTHESIS -> METHOD -> RESULT ->
ALTERNATIVE EXPLANATIONS -> CONSEQUENCE.

Distinguish [VERIFIED EXECUTION], [OBSERVED RESULT], [HYPOTHESIS],
[INCONCLUSIVE], [NOT RUN], and [CORRECTED]. Do not mark a causal explanation
verified merely because a score increased.

Every trained run retains selected checkpoints, scalers/calibrators, histories,
OOF predictions, fold/config hashes, environment and source identities.
Validate all reported numbers against saved predictions and verify historical
preservation before completion. Include tests for split isolation, augmented
parent-group isolation, train-only statistics, frame masks, anchor parity,
gradient flow, corruption reproducibility and missing-modality fallback.

Start with the shared preflight, then execute Tasks 1–4 in dependency order where
policy permits. Continue despite negative scientific findings. No automatic
budget extensions, new backbones, new datasets, or search until a win appears.

Finish with one truthful status:

**ADDITIONAL IMPROVEMENTS EXECUTED — EXPLORATORY RESULTS READY FOR REVIEW**

or

**ADDITIONAL IMPROVEMENTS PARTIALLY EXECUTED — BLOCKERS DOCUMENTED**

Do not say "improvements achieved" unless specific comparisons support it.
