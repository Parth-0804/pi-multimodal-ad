# Section 2: clean fusion protocol, before modelling

This is an **adaptive exploratory study**. Section 1 selected statistical sensors;
Section 1B demonstrated complementarity on these same outer folds. No untouched
dataset was added. Nested fitting prevents training leakage, not study-selection
bias. Section 1 and 1B, including their handoffs, remain frozen.

Use exactly 4,530 segments, 509 failures, 148 recordings and the original five
outer / four inner recording folds. Reuse F2 and its strict inner branch OOF
predictions. U1/U2 are frozen statistical-sensor/RT-DETR results. F1 averages
their calibrated probabilities, selecting only a threshold on training OOF.

F3 uses the frozen, fold-specific Section 1 visual head's 128-dimensional output
(the backbone cache itself has 896 dimensions) plus the exact 220 statistical
features. Additional independent 128-dimensional linear/ReLU projections feed
LayerNorm and a 256→32/64→1 MLP. These new projections are fusion parameters;
the underlying visual head is frozen. Each inner visual head is refitted with
the original Section 1B selected epoch, seed and procedure, then frozen; outer
heads reuse Section 1 checkpoints. No feature extraction or backbone fitting.

F4/F5/F6 combine calibrated branch scalar logits through a convex softmax gate.
F4 inputs action and availability; F5 audited quality and availability; F6 both.
No context-to-classifier bypass, output bias or extra gate calibration. Quality
normalization uses the current fitting subset only; neutral quality is its mean.
Masks enter both the gate input and masked softmax. All current samples have
both modalities available, so missing-modality behavior is not established.

Decision-level gating preserves the strongest validated statistical logistic
sensor model and the frozen visual branch. Forcing a deep sensor representation
into the primary gate would change the evidence-supported branch. F3 is an
explicit feature-fusion comparator, not a replacement sensor branch.

Quality comes only from already audited hand-camera and five sensor streams.
Six camera measures: valid-frame ratio, decode-failure ratio, brightness mean/std,
focus and motion proxies. Six sensor measures per stream: finite and resampled
finite fractions, interpolation fraction, MAD-outlier fraction, constant and
missing channel counts. No label, annotation text, segment index, recording ID,
duration, object label or audio feature enters any model. Quality may encode
process/content as well as acquisition quality; clean gating is not reliability
validation. Constant measures are retained and their lack of variation reported.

## Inner gate selection without assessment-label contamination

For a given frozen inner split, its assessment predictions are reused from
Section 1B. Gate-training predictions must also exclude that assessment fold.
Use the four subfolds already saved for that inner split in Section 1B. For each
subfold, select/calibrate branches using the other three existing subfolds,
restricting their training memberships to the current subfold's training set.
Refit and predict its held-out subfold. No fold is regenerated; all partitions
are saved and checked. This repeats the same branch estimators, candidate budgets
and calibration recipe with three available selection folds at this additional
depth. The original four-fold procedure remains unchanged for the actual inner
assessment and outer-test branch predictions. The extra training-only depth is
necessary for unbiased fusion hyperparameter assessment, not branch tuning.

For final gate fitting reuse Section 1B's strict outer-training branch OOF matrix.
Never fit on existing outer-test OOF predictions. Same branch information for
every decision fusion; same underlying visual/sensor features for F3.

## Small budget and assessment

Exact candidates/seeds are frozen in `configs/reassemble/section2.json`:
two F3 configurations; two gate widths shared across F4–F6; three seeds each.
Mean inner-fold AP of seed-mean predictions selects a configuration. Seeds are
not independent samples. Final predictions average three fitted seed probabilities.
F3 uses training-only class weighting and sigmoid calibration on selected inner
OOF raw logits; gates use unweighted BCE on calibrated branch logits, preserving
their exact weighted-logit interpretation. Thresholds use selected inner OOF
probabilities only, as in Section 1. Threshold metrics are secondary.

Report all eight metrics, seed variation, fold consistency, fusion parameter
cost and measured runtime. Inference timing excludes branch extraction and is
hardware/batch specific. F2 reuse is a parity check, not independent reproduction.
Use 2,000 paired recording-cluster bootstrap replicates with the Section 1B seed;
intervals condition on fitted models. Report all seven requested contrasts.
Additional adaptive-vs-static claims require AP gain ≥0.01, positive simultaneous
Bonferroni percentile lower bound across the three gate comparisons, at least
three positive fold gains, and AUROC lower 95% bound >−0.01. Report marginal
intervals regardless. Absence of significance does not demonstrate equivalence.
Preference and A–F interpretation rules are recorded in config before fitting.

Save per-sample and per-seed gate weights; report mean, standard deviation,
entropy and quantiles by action, fold, recording and descriptive outcome.
Fixed test-time action permutation, zero action, and training-mean quality
ablations change context only, not signals, availability or model parameters.
Use these to assess sensitivity, not causal process effects or robustness.

No PatchTST, audio, corruption, dropout of modalities, expanded branch budgets,
or RT-DETR backbone fine-tuning. End with the detailed A–V handoff and one allowed
Section 3 decision. SQ3 remains **NOT YET ANSWERED**. Stop before Section 3.

Preflight quality audit: 1,562 gripper MAD-outlier fractions are undefined;
no quality column is entirely missing. Impute unavailable measures to the fitting
subset mean after scaling, with no label-based exclusion or additional predictors.
A mechanism must change mean absolute visual weight by at least 0.01 under its
context ablation to qualify as functionally context-sensitive. This criterion
is fixed before model fitting.
