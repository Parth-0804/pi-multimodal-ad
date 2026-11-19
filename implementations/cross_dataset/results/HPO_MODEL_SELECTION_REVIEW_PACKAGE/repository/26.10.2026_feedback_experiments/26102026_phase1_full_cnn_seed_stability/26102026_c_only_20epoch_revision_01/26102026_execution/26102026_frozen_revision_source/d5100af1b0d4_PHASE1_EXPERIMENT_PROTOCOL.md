# Model C only — explicit20-epoch revision

The user removed Model B and explicitly selected20 epochs per fit on27 October
2026. This supersedes the earlier B/C schedule and25–50 execution horizon.
All pending B fits, F2-B and supplementary A_r comparisons are removed. One
completed B fit is preserved and excluded from the revised analysis.

Retain exactly the predetermined seeds42,123,20261023 and all five outer folds
with four inner OOF fits plus one outer-assessment fit each. This requires
**75 full-CNN fits**. Reuse the25 matched deterministic sensor fits; fit15 F2-C
models from appropriately inner-held-out probabilities. Every C fit executes
exactly20 epochs unless unsafe or explicitly interrupted. Select the best
training-side V AP checkpoint among epochs1–20, with the original tie breaks.
No patience stop occurs before20.

The original input, label, recording-disjoint partition, normalization,
calibration and leakage controls remain intact. All executed CNN convolutions
and normalization affine parameters train jointly with the classifier. Running
normalization moments stay fixed. FP32,16 whole-action frames, microbatch1,
accumulation8, four persistent workers and FFmpeg2 are unchanged. Reuse the
existing numerical/performance/recovery gates because the forward/backward,
optimizer and input computations are unchanged.

Preserve the cosine learning-rate schedule's original50-epoch horizon for
every fit, including newly initialized fits, and execute its first20 epochs.
This makes the current completed model/optimizer/scheduler/RNG/sampler prefix
exactly resumable. Resetting to a20-epoch cosine schedule would change the
already executed prefix. This revision does not make that change.

The immutable original training-configuration hash remains the base checkpoint
identity. A separate revision configuration hash and completion receipt record
the changed execution budget and schedule. The current C fit stops at a
completed epoch, workers close cooperatively, its entire recovery checkpoint
is retained in this revision, and continuation uses the same original fitter
with an explicit20-epoch loop/stop override. No incomplete epoch is counted.
Historical configurations, checkpoints, reports and the completed B result are
preserved.

Report pooled and per-fold AP/AUROC, prevalence, calibration, seed mean/sample
SD and recording-cluster uncertainty conditional on fitted models. Use2000
common recording draws across all fixed seeds; do not treat folds or seeds as
independent observations. F2-C minus its matched sensor baseline can be
reported as a paired contrast. The withdrawn B comparison prevents attributing
performance differences specifically to full-CNN adaptation beyond longer
classifier training. Historical AP values remain descriptive context.

This remains a follow-up on a repeatedly examined dataset. Only one GPU-heavy
fit runs at a time; foreign GPU jobs cause waiting/checkpoint recovery. No
Phase2/3 experiments, raw-data changes, checkpoint deletion, commit or push.
