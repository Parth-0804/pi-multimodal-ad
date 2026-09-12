# Pre-registration — late fusion over sensor sub-modalities

Written: 2026-09-12T05:33:29Z
Status: **written before any Phase 3 model was trained.** Committed prior to
the first training run; the commit that adds this file contains no results.

This document fixes, in advance, what will be trained, how the winner is
chosen, and how many times EXP-F is touched. At n=7 training runs a sweep
without this is uninterpretable, because with enough variants something will
beat a baseline by chance.

---

## 1. Question

Does late fusion over the sensor sub-modalities that exist at inference beat
(a) a single encoder over all nine channels, and (b) the train-mean constant?

Images are unavailable at test time, so this is fusion of what is actually
present, not image+sensor fusion.

## 2. Variants — all eight, fixed in advance

One PatchTST encoder per sub-modality, pooled embeddings concatenated, single
scalar head. The three sub-modalities partition the 72 feature columns exactly
(verified: 24 + 16 + 32 = 72, no column unassigned, none double-counted):

| Sub-modality | Base channels | Columns |
|---|---|---|
| process context | `rpm`, `torque`, `temperature` | 24 |
| organiser RMS | `axial_rms`, `radial_rms` | 16 |
| condition indicators | `fm4`, `na4`, `m6a`, `alr` | 32 |

Variants:

| # | Name | Description |
|---|---|---|
| 1 | `solo_process_context` | that sub-modality alone |
| 2 | `solo_organiser_rms` | that sub-modality alone |
| 3 | `solo_condition_indicators` | that sub-modality alone |
| 4 | `fused_all_three` | late fusion, three encoders |
| 5 | `single_encoder_all_9ch` | existing baseline architecture, reference |
| 6 | `loo_drop_process_context` | fusion of the other two |
| 7 | `loo_drop_organiser_rms` | fusion of the other two |
| 8 | `loo_drop_condition_indicators` | fusion of the other two |

No variant will be added after seeing results. If a variant fails to train it
is reported as failed, not silently dropped or replaced.

## 3. Budget — identical across variants

Fixed seed 20260912. Same optimiser, learning rate, weight decay, batch size,
max epochs and patience for every variant; only the channel subset and encoder
count differ. Any deviation forced by a training failure (for example a
learning-rate reduction to escape divergence) will be applied to **all**
variants and re-run, or reported as a deviation — never applied to one variant
only.

## 4. Selection rule — EXP-A only

The winner is selected **solely** on EXP-A (validation) performance. EXP-B is
training data. EXP-F is not consulted, viewed, or scored during selection.

**Decision metric: raw MAE on EXP-A, run level, target `raw_top3_mean_pct`.**
Lowest wins. Ties beyond 1e-6 broken by the lower validation loss at the
selected epoch, then by variant number.

### Why raw MAE and not the organizer's monotonic-MSE

The organizer scores monotonic-MSE, so that is the metric of record — but it
cannot be the *selection* metric here. Measured tonight on EXP-F (n=8), an
in-sample isotonic fit is so flexible that **pure noise beats the constant 87%
of the time**, and the canonical PatchTST's apparent win carries permutation
p ≈ 0.48. EXP-A has n=5, where the degeneracy is strictly worse. Selecting on
a metric that noise wins would select noise.

Monotonic-MSE is still **reported** for every variant, alongside its null
calibration. It is simply not permitted to choose anything.

## 5. EXP-F budget — exactly one evaluation

EXP-F will be evaluated **once**, on the single variant selected by rule 4,
after selection is final. One model, one evaluation, one number.

If the selected variant errors during test evaluation, that is reported as a
failure. It does not license evaluating a second variant.

## 6. Declared in advance: what would count as a real result

At n=8 test runs, an MAE difference under ~0.15 pp is within noise. Therefore:

- fusion beating the constant by **< 0.15 pp** will be reported as **not
  distinguishable from the constant**, regardless of sign;
- any monotonic-MSE comparison will be reported only with its permutation
  p-value attached;
- "nothing beat the constant" is an expected and publishable outcome, and will
  be reported plainly rather than reframed.

## 7. Target version

Trained against the target produced by Phase 1 (`phm2026_image_damage_v3`:
teeth 1–4 dropped in all three experiments, one deterministic view per
remaining tooth) **if** the v3 chain — target derivation, then sensor-feature
rebuild against it — completes and verifies.

Pre-specified contingency, fixed before results are seen: if the v3 chain does
not complete, Phase 3 trains against the existing pinned v2 chain instead, and
every resulting number is annotated `target=v2 (v3 chain incomplete)` in the
report. The variant list, selection rule, decision metric and one-shot EXP-F
budget are unchanged either way.

## 8. What this pre-registration does not cover

Stage 4 per-tooth supervision, Stage 5 distillation and Stage 6 oracle are out
of scope tonight and will need their own pre-registration. No result from them
is implied or reserved here.
