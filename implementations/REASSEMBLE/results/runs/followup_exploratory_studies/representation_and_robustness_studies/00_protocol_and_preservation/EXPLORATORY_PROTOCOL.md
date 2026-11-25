# ADDITIONAL EXPLORATORY EXPERIMENTS — frozen protocol

Frozen before new performance. User confirmed no added wall-time limit; use only
specified budgets. Original evidence, inputs, external Reasoning Record and old
implementations remain immutable. Exact settings and input hashes are in
`experiment_matrix.json` and `configuration.json`; preservation/environment
checks accompany them. Missing PHM `docs/restructuring/TASKS.md` is recorded; it
does not expand or block this separately authorized extension.

## Estimands and controls

The four primary contrasts are (1) V-TEMP minus V-MEAN clean AP; (2) S-LONG minus
S-6 clean AP; (3) A-ADAPTIVE minus A0 clean AP; (4) augmented A-ADAPTIVE minus
augmented F2, equal mean AP across six Gaussian test conditions. No winner
combination, architecture expansion, additional training budget, or promoted
secondary contrast. AP means average precision. Report all eight established
metrics; 2,000 paired recording bootstrap draws, marginal 95% intervals, per-fold
and per-seed metrics. Practical AP reference 0.01; non-significance is not
equivalence. The study is an outcome-informed extension on the same cohort.

## Shared nesting and numerical rules

Use 4,530 segments, 509 failures, 148 recordings, the sealed five outer/four inner
splits and original features/masks. No outer-test targets enter fitting,
calibration, epoch selection, or thresholds. New neural seeds are 20260927,
20260928, 20260929, reset at each fit. Compare mean calibrated seed probabilities;
retain seed predictions. Float32 training, original AdamW/class-balanced binary
cross entropy/gradient clip 1; mini-batch 128. Tensor and split checks run before
real training. All standardization uses only the fitting partition. Exact
original refits use original seed and 16 BLAS threads; new neural work uses four
PyTorch threads and deterministic algorithms.

Unimodal early stopping records every epoch and chooses first maximal inner AP,
maximum 100 epochs, earliest stop epoch 10, patience 12 after last improvement.
Outer/full-partition refit duration is nearest integer (half upward) median of
inner best epochs for each seed. Train-only selected cross-fitted raw logits
calibrate each seed via original unweighted C=1 sigmoid logistic calibration.
Use original balanced-accuracy threshold grid 0.01 to 0.99 with tie nearest 0.5,
on mean calibrated inner scores. S-6 specifically retains original mean-inner-AP
choice of 3 versus 6 epochs per seed, rather than replacing this expressly
requested control with per-inner epoch selection. Save all epoch histories.
Calibration cross-fits are branch training predictions; before these are supplied
to a fusion training row, a further recording-disjoint selection/calibration
level excludes that assessed row. Existing Section 1B/2 nested branch predictions
are reusable only in their original partitions. Whole-cohort outer OOF is never a
fusion training matrix.

## Task 1

V-HIST is sealed. Re-extract 16 actual per-frame vectors at saved frame indices;
assert segment mean parity <=5e-5, preserve timestamps/masks/model processor hash.
V-MEAN uses original head. V-TEMP/V-NOPOS: linear 896->128, fixed sinusoidal/no
position, one 4-head Transformer layer, FFN256, dropout0.1, valid-frame mean, binary
linear head. Normalize sequences using fitting-segment mean-vector moments,
shared with V-MEAN. Original lr=.001, decay=.001; same 100/min10/patience12 rules.
Fixed-weight reverse and seed-determined permutation diagnostics; V-MEAN and
V-NOPOS invariance tolerance 1e-5. Positional sensitivity alone proves no benefit.

V-FT starts from the corresponding training-partition V-TEMP checkpoint. Only
`encoder.stages.3` of actual RTDetrResNetBackbone can receive backbone gradients;
all BatchNorm running statistics stay frozen. Head lr1e-4, stage lr1e-5,
decay.001, max20 additional epochs, patience5, effective batch128, initial
microbatch2, no more than two OOM reductions with accumulation. Synthetic gradient
and memory audit precedes real adaptation. Compute backbone from pixels for FT;
pooled frozen feature caches cannot represent adapted outputs. Select additional
epochs in inner folds, median outer refit, train-only calibration. Preserve exact
gradient parameter list and resource failures; an unsupported FT is explicitly
not run, never silently substituted with frozen features.

## Task 2

S-HIST and S-STATS are sealed. S-6 and S-LONG retain original SensorHead/PatchTST,
512 positions, 22 channels, patch32 stride16, width32, two layers/four heads FF64,
dropout.1, original observed mask, mean patch pooling and channel concatenation.
S-LONG uses same long budget as Task1. S-HYBRID uses C1 unweighted logistic on
calibrated S-LONG and S-STATS; obtain strictly nested branch predictions using
Section1B saved subfolds (exclude assessment from branch selection/calibration).
Fit and threshold on training-only cross-fitted branch scores. Do not change
Tasks3/4 branches. Cap reached is a limitation, never automatic extension.

## Task 3

Reuse original strict branch inputs. On each proper training partition fit C1
unweighted probability-input logistic F2 anchor, freeze intercept/coefs, then
`logit=b+sum(a*(1+tanh(h(u)))*p)`. Inputs are action4, standardized quality36,
availability2. Adaptive h is 42->16 ReLU->2; final layer zero. Constant h is two
zero-initialized global parameters. Penalties [.01,.1,1] times mean squared tanh
adjustments; AdamW lr.003 decay.001, max100/min10/patience12, batch128, clip1.
Choose penalty by mean inner-fold AP of seed mean; per-seed median epochs for
outer refit. No extra output calibrator: probabilities are calibrated branch
inputs and specified logistic output, as original F2/F6; adding another fitted
link would change the prespecified anchor parity. Inner prediction threshold
uses original rule. Matched A0 uses honest inner-partition anchor predictions
for threshold and identical outer anchor probability fit; original F2 decisions
remain additional historical references. No positivity clamp. Test neutral
quality and within-test-fold action permutation with weights frozen. Single
available branch returns exact original probability and branch threshold; zero
available branches yields explicit abstention.

## Task 4

Keep original visual/statistics branches, reproduce refits from saved selected
hyperparameters, seeds/calibration and assert clean parity. Four fixed training
realizations per example/family: visual native-pixel Gaussian sigma U(.01,.08),
sensor alpha U(.05,.8) times fitting-partition channel SD, original corruption
semantics. Separate seed namespaces for training, validation and new test
realizations. Four validation realizations per Gaussian family. All derivative
copies retain parent recording; each parent contributes weight1 (clean .5,
each of 4 visual .0625, each of 4 sensor .0625). Neural training draws one
realization/family per parent epoch with mixture .5/.25/.25, unchanged batch and
step count. Static logistic uses exact normalized weighted expansion, C1.
Quality is recomputed from corrupted raw inputs; its scaling excludes assessment
recordings. No severity/family/seed/truth flags reach models.

For each matched clean/augmented model, select by .5 clean AP + .25 mean visual
validation AP + .25 mean sensor validation AP, per-realization metrics then mean.
F2 fixed C1, deterministic; F6 retains masked scalar-logit gate, hidden16 (one
existing original configuration), AdamW lr.003 decay.001, max40 epochs, select
best epoch by shared objective (min10/patience12). A-ADAPTIVE retains Task3
settings/penalty grid and clean F2 anchor in each proper partition. Three neural
seeds. Clean and augmented versions have same architecture/search/step budget.
Threshold from selected clean inner OOF mean probabilities, unchanged decision
rule; no additional gate calibrator. Task3 clean fit and sealed original models
are supplementary references because Task4 selects with Gaussian validation.

Test five new realizations for each Gaussian/frame-drop/channel-drop/block-drop
condition, same realized input across all models. Gaussian visual .02/.05/.10,
sensor .10/.50/1.00; largest out of training range, lower two in-range.
Augmentation-held-out: blur1/2/4 (deterministic), frame-drop2/5/8, channel-drop2/7/11,
block-drop.10/.30/.50, six F/T channels stuck at training median (deterministic),
complete visual/sensor loss (deterministic). No both-loss performance claims.
Use original random/quality semantics. Metrics are averaged across realizations,
never predictions; bootstrap paired recordings and resample realization indices
within condition, shared across models. Equal six-condition AP mean is primary;
held-out families reported separately. These are not independent new recordings
or untouched corruption benchmarks. Report all eight metrics, fold/seed results,
clean loss, contrasts vs matched clean/augmented F2 and surviving unimodal,
coefficient/weight changes. Clean non-inferiority AP margin .01 requires lower
95% bound >-.01. Static augmentation mandatory for any adaptive value claim.

## Operations, provenance and stopping

Source: isolated `src/reassemble/additional_improvements/`. CLI modules run with
`PYTHONPATH=src ma_thesis_env/bin/python -B -m reassemble.additional_improvements.<module>`.
Run GPU jobs serially. Cache compact feature arrays, never permanent decoded
frames. Below30GiB prohibit new large caches; below20GiB stop new writes/training;
no deletion. At most two microbatch reductions for OOM, no model/budget changes.
Leakage, changed protected inputs or corrupt source stop globally. Isolated
failures retain traceback and block that subtask while independent work continues.
Record implementation commits, commands, timestamps, checkpoint/config hashes,
curves, prediction identities, corrections and all failed attempts. Resume only
identical completed fit signatures. Preserve the root/task status and
`reports/CONTINUATION.md`; final manifests exclude mutable manifests themselves.
Final required handoffs and status explicitly distinguish complete, failed,
blocked, and not-run work; all improvements/deteriorations/unresolved findings
are equally eligible for reporting. No automatic subsequent combined model.
