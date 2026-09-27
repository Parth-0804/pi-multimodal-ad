# Section 3 corruption preregistration

Freeze this document and `configs/reassemble/section3_corruptions.json` before
any corrupted predictions are assessed. The user explicitly authorizes all
remaining non-destructive phases; negative results trigger documentation and
continuation, not architecture rescue. Sections 1/1B/2 remain immutable.

Same 4,530 segments, 509 failures, 148 recordings and original outer folds.
Models: frozen U1 sensor statistics, U2 visual diagnostic, F1 uniform, F2 learned
static, F5 quality gate, F6 process+quality gate. No concatenation tournament.
Gates retain all three seeds and exact Section 2 checkpoints, normalizers and
thresholds. Recover a sensor checkpoint only by exactly reproducing its original
C/scaler/refit/calibration and requiring probability parity ≤1e-5 before use.
No fitting uses any corrupted outer-test labels or predictions.

## Perturbations

V1: decoded native-resolution pixels /255; Gaussian sigma 0.02/0.05/0.10;
clip, round to uint8, then original RT-DETR preprocessing. V2: Gaussian blur
sigma 1/2/4, kernel 2ceil(3sigma)+1, reflect-101 border. V3: deterministic dropout
of 2/5/8 of the original 16 frame indices, omitting invalid frames from pooling.
V4: visual unavailable; no visual information supplied to fusion.

S1: Gaussian noise alpha 0.10/0.50/1.00 times each outer-training channel std.
The std uses all finite resampled training values, never test data. Noise is
applied to raw in-segment measurements; consequently interpolation may attenuate
it. S2: remove 2/7/11 of the 22 channels, using NaNs. S3: one contiguous block,
10/30/50% normalized progress; uniform seeded start, all channels masked with
NaNs. S4: all six measured force/torque channels stuck at outer-training medians.
S5: sensor unavailable. Raw timestamps never change. Recompute the exact existing
512-position resampling and statistical features. All-NaN-channel warnings are
expected under deliberate dropout; retain the frozen NaN/imputation and slope
behavior rather than silently changing formulas. The other modality stays clean.

Hash-derived seeds use global seed, recording, segment, family and severity;
visual noise additionally uses original frame index. No label-dependent seed.
All definitions, including rounding and missingness conventions, are in config.
No combined corruptions are planned.

## Quality and fidelity

Use exactly the six existing visual fields and six fields for each of the five
sensor streams. Recompute visual brightness/focus/motion with the original
160×120 grayscale formulas on perturbed decoded frames; valid-frame ratio uses
16 requested frames, and dropped frames are not treated as valid zeros. Recompute
sensor finite/missing/constant/MAD-outlier/interpolation/resampled-finite measures
using the original raw-sample formulas and timestamps. Training quality scalers
and mean imputation remain frozen. No new quality input is added. Missing whole
modality qualities use the training mean and the availability mask; these quality
values cannot influence the exactly zero masked branch weight. Before corruption,
verify clean feature and quality reproduction against existing caches. A pipeline
mismatch is a hard scientific guard, not a reason to relax tolerances after outcomes.

## Missingness conventions

With one modality absent, F1 and F2 return the remaining calibrated branch
probability, bypassing F2's two-input intercept/weights. This is an explicitly
specified fallback convention, not a trained missingness guarantee. Gates must
return exactly the same branch through masked softmax. Use its frozen unimodal
threshold in this case, allowing probability and decision parity. An unavailable
unimodal model abstains (undefined metrics), never receives invented replacement
signal. Report fallback, not magical robustness or informational recovery.

## Metrics, uncertainty and mechanism

Eight original metrics and clean-relative AUROC/AP deltas; 2,000 paired
recording-cluster bootstrap draws with the original seed. Required contrasts:
F5−F2, F6−F2, F2−U1 where U1 remains available. Also report paired differences
in clean-relative degradation, so a worse clean baseline cannot masquerade as
superior corrupted performance. Intervals condition on fitted models and each
single seeded corruption realization. Save all seed/mean gate weights.

For each ordered severity family report Spearman(severity, degraded-modality
weight), paired high-vs-clean weight differences, entropy and distributions.
Repeated-segment correlations are descriptive; do not use IID p-values. A
family-specific ROBUSTNESS-A requires expected weight adaptation with clustered
CI excluding zero AND a positive paired AP degradation advantage with compatible
AUROC. Absolute superiority is a separate claim requiring corrupted AP difference
CI >0. Complete modality-loss masking is deterministic fallback, not learned
reliability awareness. All multiple-family findings remain exploratory; no broad
claim from an isolated marginal interval. Never force monotonicity.

## Modality dropout, predeclared now

After the entire clean-trained corruption suite completes, fit only F6 with
categorical training masks: visual missing .15, sensor missing .15, both present
.70, never both absent. Same three seeds and Section 2 fold-specific selected
head settings; no corruption-based selection. Refit inner heads only to derive
training-only thresholds, then final outer heads. Branches stay frozen. Since a
single available branch makes gate weights [1,0] or [0,1], its loss provides no
gate-parameter gradient: missing-condition probabilities cannot improve under
this architecture. Empirically compare the variant anyway; effects can arise
through reduced clean gradient exposure, not information recovery. This is a
potential negative result, not permission to change architecture.

Compare clean, both modality-loss cases, all Gaussian severities, blur sigma 2,
and channel-dropout 30%. No robust-training architecture or severity search.

## Later gates

Audio: audit segment timing, not frame-perfect synchrony. Adequate nominal
coverage alone cannot establish that the correct waveform interval is assigned
when clock origin/drift lacks evidence. If this precondition fails, document
exclusion and continue; no AST is then warranted. Object-disjoint stress testing
requires reliable physical object identities and viable disjoint recording support;
annotation strings alone are not assumed to identify physical instances.

Stop new cache/training jobs below 20 GiB free; otherwise proceed to efficiency,
final figures/tables, cross-study synthesis and preservation/claim audits.
