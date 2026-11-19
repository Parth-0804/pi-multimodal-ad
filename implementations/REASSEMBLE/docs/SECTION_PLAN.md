# SECTION 1 — Unimodal Models and Signal Validation

## Goal

Establish whether the two primary REASSEMBLE modalities independently contain useful failure information before any fusion is attempted.

Primary modalities:

- Visual → RT-DETR pretrained backbone as representation extractor
- Sensor → PatchTST on force/torque + proprioception

Do NOT build fusion models yet.

## Tasks

1. Verify and freeze recording-disjoint evaluation folds.
2. Run trivial/prior baseline.
3. Run action-only logistic-regression baseline.
4. Run simple statistical sensor baseline.
5. Train/evaluate frozen RT-DETR visual model.
6. Train/evaluate PatchTST sensor model.
7. Run label-permutation controls for RT-DETR and PatchTST.
8. Compute:
   - AUROC
   - AUPRC
   - balanced accuracy
   - macro-F1
   - failure recall
   - failure precision
   - Brier score
   - calibration if available
9. Use recording-clustered uncertainty.
10. If both modalities show defensible predictive information, compute visual-vs-sensor complementarity:
    - both correct
    - both wrong
    - visual-only correct
    - sensor-only correct
    - failure-specific disagreement
    - prediction correlation
    - error correlation
    - breakdown by pick / insert / remove / place

## Gate

End with exactly one:

FUSION GO — VISUAL AND SENSOR MODALITIES BOTH DEMONSTRATE SIGNAL

FUSION CONDITIONAL — EVIDENCE REQUIRES REVIEW

FUSION NO-GO — MULTIPLE INFORMATIVE MODALITIES NOT DEMONSTRATED

## Required handoff file

Create:

`artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md`

The file must contain:

### A. Question
What scientific question did this section test?

### B. Why this section came before fusion
Explain why unimodal information is a prerequisite for meaningful fusion.

### C. Evaluation protocol
Exact grouping unit, folds, inner validation, seeds and leakage protections.

### D. Baselines
What was tested and why.

### E. RT-DETR
Architecture, preprocessing, frame sampling, frozen/fine-tuned status, hyperparameters.

### F. PatchTST
Channels, resampling, normalization, architecture and hyperparameters.

### G. Results
Complete tables with all metrics and uncertainty.

### H. Permutation controls
Results and interpretation.

### I. Complementarity
Only if both modalities contain signal.

### J. Failed attempts / corrections
Anything that went wrong must remain documented.

### K. Interpretation
What can actually be claimed?

### L. What cannot be claimed?
Explicitly list overclaims to avoid.

### M. Decision
PASS / FAIL / CONDITIONAL for each modality.

### N. Provenance
Git commit, run directories, configuration files, artifact paths.

Then STOP.

Do not train fusion models until researcher review.


# SECTION 2 — Clean Fusion Architecture Comparison

## Prerequisite

Run ONLY if Section 1 returns Fusion GO or an explicitly approved conditional GO.

## Goal

Compare the proposed multimodal architectures under clean, uncorrupted data.

## Models

Keep the same selected RT-DETR and PatchTST branches for every fusion architecture.

Do not give one fusion method stronger unimodal encoders than another.

Run:

### F1 — Concatenation
`[z_visual ; z_sensor] → MLP → prediction`

### F2 — Uniform late fusion
`0.5 * p_visual + 0.5 * p_sensor`

### F3 — Learned late fusion
Static learned convex weights.

### F4 — Quality-aware gated fusion
Gate reads modality-quality variables.

### F5 — Process-aware gated fusion
Gate reads action type:
- pick
- insert
- remove
- place

### F6 — Process + quality gated fusion
Gate reads:
- action
- visual quality
- sensor quality
- availability masks

## Required comparisons

Compare against:

- strongest unimodal model
- concatenation
- uniform late fusion
- learned late fusion

Use paired recording-clustered uncertainty.

Report:

- AUROC
- AUPRC
- balanced accuracy
- macro-F1
- failure recall
- failure precision
- Brier
- ECE
- parameter count
- latency
- GPU memory where practical

## Gate analysis

For gated models report:

- mean visual weight
- mean sensor weight
- weight variance
- gate entropy
- weights by action
- weights by recording
- weights by success/failure descriptively

Also run:

- process context shuffled
- process context neutralized
- quality features neutralized

Purpose:

determine whether the gate actually uses the intended variables.

## Required handoff file

Create:

`artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md`

Include:

### A. Fusion hypothesis before results
Why fusion might help based on Section 1 complementarity.

### B. Architectures
Exact definitions.

### C. Fairness controls
Parameter/tuning consistency.

### D. Clean results
Full metric tables.

### E. Pairwise differences
Point estimate + interval.

### F. Gate behaviour
Weights, actions, quality, ablations.

### G. Complexity versus benefit
Did additional architecture complexity buy anything?

### H. Best-supported conclusion
Examples:
- fusion improves
- late fusion sufficient
- gating adds value
- gating adds no value
- no fusion advantage

### I. Failed attempts / corrections

### J. Claims allowed

### K. Claims not allowed

### L. Provenance
Commits, run folders, configs.

Then STOP.

Do not run corruption experiments yet.


# SECTION 3 — Noise, Missing Modalities and Robustness

## Prerequisite

Section 2 clean models must already exist and be frozen.

Do not change model architecture after observing corruption results.

## Goal

Test SQ3:

Does adaptive fusion improve robustness when one modality becomes unreliable or unavailable?

## Freeze corruption definitions before running

Create one corruption config before seeing results.

### Visual corruption

Gaussian pixel noise:
- σ = 0.02
- σ = 0.05
- σ = 0.10

Blur:
- mild
- medium
- strong

Frame dropout:
- 10%
- 30%
- 50%

Complete visual loss:
- visual missing

### Sensor corruption

Gaussian noise relative to training-fold standard deviation:

- α = 0.1
- α = 0.5
- α = 1.0

Channel dropout:
- 10%
- 30%
- 50%

Temporal dropout:
- 10%
- 30%
- 50%

Stuck-channel corruption.

Complete sensor loss:
- sensor missing

## Run one modality corruption at a time first

When vision is degraded:
sensor remains clean.

When sensor is degraded:
vision remains clean.

This is required to interpret the gate.

## Compare

- concatenation
- uniform late fusion
- learned late fusion
- quality gate
- process gate
- process+quality gate

## For every corruption level measure

- AUROC
- AUPRC
- performance drop from clean
- failure recall
- Brier/calibration change

For gated models additionally measure:

- visual gate weight
- sensor gate weight
- change from clean
- weight vs corruption severity

## Key mechanism test

Test whether:

modality corruption increases
→
weight assigned to that modality decreases
→
performance is preserved better than static fusion.

Do not claim robustness if only the weights change.

Do not claim adaptive gating if performance changes but weights do not respond coherently.

## Modality-dropout training

After ordinary robustness testing, train ONE additional predeclared gated variant with modality dropout.

Example:

visual drop probability = 0.15
sensor drop probability = 0.15

never both simultaneously.

Compare:

ordinary gated fusion
vs
modality-dropout gated fusion

under:

- clean
- corrupted vision
- corrupted sensors
- missing vision
- missing sensors

## Required handoff file

Create:

`artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md`

Include:

### A. Robustness hypothesis

### B. Frozen corruption definitions

### C. Clean reference performance

### D. Visual corruption results

### E. Sensor corruption results

### F. Missing-modality results

### G. Gate-response results

### H. Modality-dropout results

### I. Does gating truly improve robustness?

Answer with evidence.

### J. Clean-performance versus robustness trade-off

### K. Failed hypotheses / unexpected findings

### L. Claims allowed

### M. Claims prohibited

### N. Provenance

Then STOP.


# SECTION 4 — Audio Extension + Thesis Evidence Package

## Important

Do NOT automatically execute a large audio study.

This section begins with an audio feasibility gate.

The visual+sensor study already constitutes the primary multimodal experiment.

## Part A — Audio feasibility

Check:

- audio availability
- audio segment coverage
- timestamp quality
- duration alignment
- whether segment-level audio can reliably be extracted

Frame-perfect synchronization is NOT required if AST independently aggregates the audio segment.

If audio cannot be reliably associated with action segments:

record:

AUDIO NOT INCLUDED — ALIGNMENT/COVERAGE PRECONDITION FAILED

and stop audio modelling.

This is a valid methodological decision.

## Part B — AST if feasible

If audio passes:

1. extract segment audio
2. log-mel spectrogram
3. frozen pretrained AST
4. 128-dim embedding
5. nested recording-disjoint evaluation
6. permutation control

Only if AST demonstrates signal:

extend already-selected fusion architecture to:

visual + sensor + audio.

Do not repeat the entire architecture search.

Run:

- uniform late
- selected best static fusion
- selected best gated fusion

Optional audio corruption:

20 dB
10 dB
0 dB
audio missing

## Part C — Final evidence package

Whether audio runs or not, generate:

`artifacts/reassemble/reports/SECTION_4_FINAL_HANDOFF.md`

This file must contain:

### 1. Complete REASSEMBLE study chronology

From acquisition to final models.

### 2. Every scientific gate

For each:

question
result
PASS / FAIL / CONDITIONAL
consequence.

### 3. Every model result

One consolidated table.

### 4. Fusion conclusions

### 5. Robustness conclusions

### 6. Audio decision/result

### 7. Negative findings

### 8. Corrections and withdrawn claims

### 9. Important failed experiments

### 10. Limitations

### 11. Exact thesis-safe claims

### 12. Claims that would be overstatements

### 13. PHM → REASSEMBLE connection

Explain:

What PHM taught.

Why REASSEMBLE was added.

How PHM changed the experimental methodology.

### 14. Answers to SQ1–SQ4

Evidence only.

### 15. Proposed answer to the Main RQ

Evidence only.

### 16. Thesis figure inventory

For every important figure:

artifact path
what it demonstrates
which thesis chapter it belongs in.

### 17. Thesis table inventory

Same.

### 18. Provenance

All relevant:
commits
run directories
configs
split hashes.

Then STOP.

Do not attempt to edit an external thesis reasoning document that is not present in the repository.