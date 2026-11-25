# Approved computation-only amendment — before any V-FT outcomes

User authorization: **Allow verified frozen-prefix caching** (recorded separately
in `prefix_cache_authorization.json`). The original instruction forbade frozen
feature caches for fine-tuning. This exception applies only to unchanged layers
before the trainable final spatial stage; cached final-stage/pooled adapted
features remain invalid.

Cache the output of `encoder.stages.2` and the earlier two spatial means, with
lossless NPZ compression and their original float32 values. Always recompute
`encoder.stages.3` and the temporal head with gradients during training. Pinned
weights,16frames,processor,normalization,architectures,seeds,losses,learning rates,
effective batch128 and maximum20/patience5 fine-tuning budget are unchanged.

The initial audit failed the1e-5 gradient tolerance when prefix extraction used
16 images but the direct fine-tuning forward used32 images. Preserve that failed
attempt; do not relax the tolerance. The correction matches32-image extraction
for two-segment microbatches. Singleton microbatches use the original pixel
forward with16 images, preserving its convolution/RNG behavior. The corrected
GPU prediction/gradient audit passed; exact values, parameter names, checkpoint
hashes and precision are in `frozen_prefix_GPU_equivalence.json`.

Before allocating the full cache, use ten predetermined recordings to estimate
compressed size. Require the largest sampled per-segment size extrapolated to
all4530 segments to leave30GiB free. Check the30GiB reserve on every cache pair.
If unsupported, preserve sampled/partial cache and use original pixel-based
fine-tuning; no deletion or model/budget reduction is authorized. Full cache
completion, per-segment hashes and selected source-frame identities are retained.

This changes computation reuse only. It is not an outcome-driven model change,
new representation, new fine-tuning budget, or combination of winning models.
