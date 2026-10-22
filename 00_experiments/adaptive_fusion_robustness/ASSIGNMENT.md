# Audit the inputs, then execute a controlled adaptive-fusion robustness study

Work in the existing HFU `pi-multimodal-ad` repository.

## Goal

Answer:

“For the fixed frozen 16-frame CNN and sensor branches, does a small quality-conditioned fusion model improve performance under predefined input corruptions compared with augmentation-matched static F2?”

A negative or inconclusive result is acceptable. Do not optimize the experiment to produce a positive conclusion.

This is a new experiment. Preserve previous encoder, noise and backbone-study artifacts. Historical Task4 remains excluded.

Proceed autonomously within this scope when the checks pass. Do not restart backbone or encoder fine-tuning.

## 1. Establish the evidence and budget

Locate the completed encoder comparison, current noise `run_02`, their source/configuration snapshots, model components, memberships, OOF predictions and provenance.

Verify actual files and fit identities rather than trusting filenames or summary text.

Use a separate maximum 24-hour wall-clock window for this experiment, including audit, preparation, waiting, extraction, fitting and reporting. Persist its start and deadline once. Reserve the final three hours for evaluation and reporting. Do not renew the clock on restart or change the older study’s deadlines or STOP markers.

Check GPU ownership before GPU work. Do not terminate another workflow.

Aim for five matched outer folds using verified CNN-only branch fits from the completed encoder study. Before assessment, benchmark on permitted training inputs and conservatively estimate the complete workload. If five folds cannot fit, lock a smaller fixed prefix of fold IDs based only on runtime and available artifacts. Label reduced coverage as a pilot.

Do not choose folds, samples, conditions or seeds using scores.

## 2. Perform a bounded data and implementation audit first

Write `DATA_AUDIT.md` and machine-readable checks.

### Labels and eligibility

- Trace each selected target to the native recording and exact segment.
- Verify the intended annotation level: high-level action versus low-level sub-action.
- Verify success datatype and accepted values explicitly. Reject ambiguous strings, missing values or unsupported encodings; do not rely on generic truthiness.
- Verify the explicit success-to-failure mapping, action identity and start/end interval.
- Reconcile original eligibility rules, exclusions and class counts.
- Confirm that labels are source annotations rather than predictions or sensor-derived proxies.

### Known dataset issues

Read the official dataset notes:
https://github.com/TUWIEN-ASL/REASSEMBLE

In particular, reconcile the documented last-action force/torque issues in:

- 2025-01-11-14-45-48
- 2025-01-11-15-27-19
- 2025-01-11-15-35-08

Also check relevant missing-camera and hardware-issue notes.

Determine which exact actions are affected and how the current dataset version and pipeline handle them. A recording-level warning does not justify dropping every action in that recording. Finite sensor values do not establish physical validity.

### Images and alignment

- Verify native camera identity, cached-video provenance, timestamps and frame indexing.
- Check the exact 16 selected frames against the action interval.
- Document that the current sampler is uniform in frame index, which need not be uniform in elapsed time.
- Verify BGR/RGB handling, resize, scaling and normalization against the actual pretrained processor.
- Check sensor/video interval alignment and missing-data handling.
- Compare a deterministic small sample of native and cached frames using an appropriate codec-aware method.

Create evidence for 16 predetermined development/training examples spanning successes, failures, action types and recordings: short action playback or contact sheets, selected timestamps, native annotation and aligned sensor summaries. Do not select examples by prediction error.

Distinguish machine checks, visual observations and any human review still needed. Do not claim that automated inspection proves all labels correct.

### Existing encoder implementation

Record the actual extraction path, tensor shapes, spatial pooling and frame aggregation. Confirm that the encoder receives spatial feature maps and that frame averaging discards temporal order.

On existing training-only cached features, check finite values, near-constant dimensions, normalizer floors, extreme standardized values and final-checkpoint evaluation-mode training loss. Do not tune the encoder using assessment results.

### Audit decision

If a concrete label-mapping, alignment, cache or split defect invalidates the experiment, preserve the evidence and stop before adaptive training. Explain the exact blocker and required correction.

Do not silently relabel examples, alter the cohort or overwrite historical results.

If the checks pass, proceed. Carry remaining semantic uncertainty into the report.

## 3. Lock the protocol before new assessment

Save a protocol and resolved configuration defining:

- Task, target, eligible cohort and exact folds.
- Branch-fit identities and all fitting/prediction roles.
- Quality features and their mathematical definitions.
- Fusion models and fixed fitting settings.
- Training augmentation, assessment conditions and seeds.
- Primary estimand, secondary analyses and stopping rules.
- Compute budget and artifact plan.

The REASSEMBLE cohort and previous outer scores are already development-exposed. Describe this as an exploratory controlled study. A new split or new corruption seed does not make it an untouched independent dataset.

Use completed-action classification throughout. Do not claim online or early failure detection.

## 4. Keep the branches fixed and compare four fusion models

Use identical frozen CNN and sensor branch predictions across fusion conditions.

Retain the historical clean-trained F2 as a reference.

Fit these three additional models:

A. `static_augmented`
Logistic regression using `[p_visual, p_sensor]`.

B. `quality_additive`
Logistic regression using `[p_visual, p_sensor, q]`.

C. `quality_interaction`
Logistic regression using `[p_visual, p_sensor, q, p_visual*q, p_sensor*q]`.

Here `q` contains a small fixed set of observable input-quality statistics.

For C, the visual coefficient becomes `beta_visual + theta_visual · q`, and similarly for the sensor coefficient. Describe these as input-dependent coefficients, not percentages of trust or causal modality importance.

Use the existing F2 regularization/solver recipe where compatible, including C=1 and unweighted class treatment. Fix the numerical settings before assessment. Do not perform an architecture or hyperparameter search. Do not add a new fusion calibrator in this minimal study.

Include visual-only and sensor-only outputs as contextual baselines.

All three new fusion models must receive the same parent actions, corruption realizations and sample weights.

## 5. Generate valid fusion-training inputs

Fit a separate fusion model for each outer fold.

For each outer fold, define T as its training recordings and E as its assessment recordings. E labels must never enter fitting, normalization, calibration or selection.

Use verified inner out-of-fold branch predictions covering T. For corrupted fusion-training inputs, generate predictions on each inner job’s held-out prediction recordings using that job’s saved branches and calibrators. Those recordings must be absent from the branch-training and branch-calibration groups.

Never use the previous noise study’s outer-assessment predictions to train or tune fusion.

Never combine OOF tables from different outer folds into one global fusion model.

Do not casually split an existing OOF table for validation or calibration: upstream fits generating other rows may already have used those proposed validation labels. Keep fusion settings fixed and fit on the permitted OOF rows. Any future tuning would require properly nested feature generation.

Fit quality normalization only on the appropriate fusion-training inputs. Fit raw-channel scales only on the permitted branch-training inputs.

Keep every clean/corrupted variant of a recording in the same partition.

## 6. Define observable quality and matched augmentation

Use at most ten predeclared, inexpensive quality features, such as:

- Image sharpness or high-frequency variation.
- Clipping/saturation fraction.
- Contrast.
- Actually available unique-frame fraction.
- Sensor finite-value fraction.
- Available-channel fraction.
- Observable missing-time gaps.
- Sensor variation relative to training-derived channel scales.

Record exact formulas, aggregation, missing-value treatment, clipping and normalization before fitting.

Compute quality from the input actually received at prediction time. Do not use a pristine counterpart, corruption name, injected severity, seed, correctness, recording identity or known fault label as a model input.

Quality features are proxies; do not assume they are validated reliability measurements.

Use a fixed training mixture:

- Clean input.
- One image-corrupted variant per parent action, drawn deterministically from image Gaussian noise or frame loss.
- One sensor-corrupted variant per parent action, drawn deterministically from sensor Gaussian noise or channel loss.

Use the existing documented severity levels, with a predetermined uniform sampling rule. Give each action total weight 1: 0.5 clean, 0.25 image-corrupted, 0.25 sensor-corrupted.

Use disjoint training and assessment random seeds, fixed before fitting.

Apply corruption to actual image pixels or native sensor signals. Do not substitute noise on saved probabilities or embeddings.

## 7. Run the predefined assessment

Primary assessment:

- Image Gaussian noise: sigma 0.02, 0.05 and 0.10 on RGB scaled to [0,1].
- Sensor Gaussian noise: 0.1, 0.5 and 1.0 times permitted training-derived channel standard deviations.
- Three assessment realizations per severity.
- Corrupt one modality at a time; keep the other unchanged.

Secondary assessments, excluded from augmentation fitting:

- Image blur at the previously documented three levels.
- Sensor time-block loss at the previously documented three levels.
- Clean input.
- Declared complete modality absence.

For absence, apply the same explicit fallback policy to every fusion model and report it separately. Both absent must produce an explicit unavailable/abstain outcome.

Verify exact keyed coverage and unchanged-branch equality. Retain failed cases in coverage accounting; do not silently drop difficult samples.

Cache expensive frozen features once per exact input/transformation identity and reuse them across compatible heads. Include weights, preprocessing, sample IDs, corruption parameters, seeds and applicable training-derived scales in cache identities.

## 8. Evaluate the question fairly

Primary contrast:

Quality-interaction model minus augmentation-matched static F2 in AP.

Compute AP separately within each outer fold, corruption family, severity and realization. Average repeats, then severities, then the two primary families, then matched folds with equal weights.

Do not pool repeated corruptions as independent subjects or compute AP from averaged probabilities. Report pooled outer-fold AP separately from mean-fold AP.

Use 2,000 paired recording-cluster bootstrap resamples within folds, keeping models and all variants of a recording paired. Report valid/invalid replicate counts and state that uncertainty conditions on the fitted models and fixed realizations.

Also report:

- Adaptive versus additive-quality contrast.
- Augmented static versus historical static contrast.
- Each corruption family and severity separately.
- Clean AP differences against both static baselines.
- Unimodal comparisons.
- AUROC, Brier, precision, recall and confusion counts at fixed threshold 0.5.
- Worst-family performance, runtime, memory and completed coverage.

Do not claim that nonsignificant clean deterioration establishes “no harm.” Use zero clean degradation as the conservative margin for any claim of improvement without clean AP cost; otherwise report the clean tradeoff or uncertainty explicitly.

A positive primary interval supports improvement under the predefined noise mixture. It does not prove superiority under every fault. Evidence specifically for quality-dependent modality coefficients also requires comparison with the additive-quality control.

Held-out fault families are excluded from this fitting procedure; they are not an independent dataset.

Do not rerun with different settings merely because results are negative.

## 9. Deliver a reviewable package

Produce:

- `README_FIRST.md`
- `RESULTS_SUMMARY.md`
- `DATA_AUDIT.md`
- Locked protocol and resolved configuration.
- Sample audit visuals.
- Exact split, fit and source identities.
- Saved fusion components and quality-feature definitions.
- Keyed clean and corrupted predictions.
- Metrics, paired intervals and per-condition coverage.
- Independent saved-table recalculation code and results.
- Runtime/budget records and reproducible commands.
- A checksummed review ZIP containing the necessary source and small artifacts, with large raw data and weight files referenced by identity.

Finish with a direct answer: supported improvement, no demonstrated improvement, inconclusive, or blocked.

State what completed, any clean-performance cost, the contribution of augmentation versus quality information versus interactions, and the limits imposed by coverage and prior development exposure.