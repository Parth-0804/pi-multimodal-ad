# Matching controls and explicit adaptations

The primary causal contrast within each matched ViFailback pair is whether the original pretrained CNN parameters receive gradient updates. Both arms use the same native episode IDs, task-disjoint roles, 48 source frames,896-dimensional episode features, newly seeded head, effective eight-episode minibatches, training-only feature moments, class weight, optimizer family, validation criterion and epoch/scheduler budget. Full training promotes the original fixed-normalization affine values to parameters without updating running moments.

The complete source audit is indexed by `AUTHORITATIVE_SOURCE_MANIFEST.json`. Its 25 completed C20 fits and single selected Full100 fit are source evidence, not ViFailback results. The approved stop after25 source fits is not relabeled as completion of the original75-fit plan. The100-epoch source donor remains selected epoch47 after100 executed epochs.

| Detail | REASSEMBLE reference | This ViFailback study |
|---|---|---|
| Prediction unit | One action,16 RGB frames | One completed native episode,three cameras ×16 timestamps |
| CNN | Pinned RT-DETR ResNet18-vd backbone only | Same CNN; same spatial means,896 features |
| Pooling | Equal mean over16 timestamps | Equal mean over48 camera/timestamp features |
| Selection | Primarily failure-class validation AP | Both-class validation macro AP, then lower T-weighted validation BCE, then earliest epoch |
| Head execution | Source full-image implementation used episode accumulation | One vectorized CPU head minibatch for both matched target arms, matching the retained ViFailback frozen implementation |
| CNN execution | Live image training or cached frozen features | Original full CNN on CUDA; verified frozen/original and donor feature banks on CPU |
|20-epoch schedule | First20 of cosine50 | Exactly20, same cosine50 prefix |
|100-epoch schedule | Exactly100 with cosine100 | Exactly100, same cosine100 horizon |
| Learning-rate multiplier | Source cosine with0.1 floor | `0.1 + 0.9 × (1 + cos(pi × completed_epochs / horizon)) / 2` |
| F2 bank | Source single-bank pilot versus source nested roles |100: separate788-episode meta bank;20: complete three-inner OOF |
| Sensor pilot | Inner bank predictions and outer-refit sensor | Same distinct-inner/outer-refit meaning; fixed identical vectors across visual arms |

This is a controlled target-domain comparison and a documented recipe transfer, not a claim that all numerical execution details are identical between datasets.

## Why Frozen100 is reused

The retained `seed42/outer0_inner0` trajectory has100 consecutive completed epochs, the exact target roles and frozen feature identities, the same seeded head, AdamW settings and cosine100 schedule. Its validation-selected checkpoint is epoch11. Independently applying the new full tie rule to the retained histories selects the same checkpoint; all36 retained V1 fits also pass this selection-equivalence check. The historical strict-macro-AP selection rule is disclosed rather than silently rewritten. Historical best/final bytes remain at their original paths and are referenced by hash.

The existing V1 outer0_final model is a separate historical reference. It is not substituted for the matched pilot model because its fitting roles differ. New Frozen20 heads are required because20/cosine50 is not the retained100/cosine100 procedure.

## Numerical and stochastic controls

The full trainer first computes pooled episode leaves, performs one CPU head/dropout execution for the actual minibatch, then recomputes CNN frame chunks and propagates the exact derivative of the episode mean. CNN normalization has fixed running moments and no stochastic CNN layer. Decoder-worker seeding uses a separate generator so starting a loader does not consume the CPU head's dropout RNG.

The real48-frame proof compared recomputation with ordinary end-to-end autograd using activation checkpoints. All trainable gradients passed the declared tolerance, every CNN stage updated, and all normalization running moments stayed unchanged. The saved CPU feature bank versus the live original CUDA CNN differed by at most `5.960464477539062e-07` in the bounded episode. This floating-point implementation difference is measured; bitwise identity of cached CPU and live CUDA features is not claimed.

A second proof executed eight distinct training episodes through the production loader, one `(8,896)` CPU head call and exactly one optimizer update. It passed all11 checks. Full model/optimizer/scheduler/RNG reload reproduced the next bounded update exactly. These are bounded implementation checks, not validation of external generalization.

## Interpretation controls

All new seeds were named before new held-out results. Resource admission used measured throughput and disk only. No additional100-epoch folds or seeds, target-domain donor CNN tuning, hyperparameter search or quality-aware gate are declared. Strong sensor HGB remains a secondary reference and is never substituted into canonical F2. Negative visual coefficients are permitted by original unweighted logistic F2 and are not interpreted as causal modality percentages.

The source donor carries only learned CNN values through its verified frozen feature bank. Every target head, scaler, sigmoid calibration and F2 fit is target-specific. The source classifier, source feature moments, sensor state, calibrator and fusion coefficients do not transfer.
