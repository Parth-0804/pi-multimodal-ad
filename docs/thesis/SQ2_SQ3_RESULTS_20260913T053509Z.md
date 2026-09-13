# SQ2 / SQ3 — four-arm fusion over sensor sub-modalities

2026-09-13. v3 target (24 teeth), committed LOEO folds, frozen
hyperparameters, 3 seeds, run-clustered bootstrap. **All numbers here are real
PHM results.** The synthetic Task-1 control numbers are in
`CLOSING_C3_RETEST_*` and appear in no table below.

---

## 1. Sub-modality partition, by HDF5 provenance

| Group | Base channels | HDF5 path | Columns |
|---|---|---|---|
| M1_accel1 | `axial_rms` | `/Context/Accel1 RMS` | 8 |
| M2_accel2 | `radial_rms` | `/Context/Accel2 RMS` | 8 |
| **M3_encoder** | — | `/Vibration/Encoder` | **0 — EMPTY** |
| M4_context | `rpm`, `torque`, `temperature` | `/Context/PAU Speed`, `PAU Torque`, `Temperature` | 24 |
| M5_condition_indicators | `fm4`, `na4`, `m6a`, `alr` | `/CI/*` | 32 |

8 + 8 + 0 + 24 + 32 = **72 columns, zero unassigned.**

**Two forced deviations from the four-group scheme, both from the data:**

1. **M3 is empty.** No channel in the committed feature pipeline reads
   `/Vibration/Encoder`. A unimodal M3 arm is impossible and **ablation R2 is
   vacuous** — it is reported below but changes nothing by construction.
2. **The condition indicators cannot be attributed to an accelerometer.**
   `/CI/*` does not distinguish accel 1 from accel 2, so `fm4/na4/m6a/alr`
   cannot join M1 or M2. They are 32 of 72 columns — the largest group — so
   discarding them would have made these arms non-comparable to the existing
   baselines. They form their own group, M5.

A1 therefore has **four** unimodal results (M1, M2, M4, M5), not the M1–M4 the
task specified.

## 2. Four-arm comparison — LOEO, run-level MAE

| Arm | MAE | ± seed std | clustered 95% CI |
|---|---|---|---|
| **constant (per-fold train mean)** | **0.8042** | — | [0.5784, 1.0364] |
| A3 modular late fusion | 0.8288 | ±0.0106 | [0.5897, 1.0801] |
| A1 unimodal M2_accel2 | 0.8289 | ±0.0278 | [0.5933, 1.0723] |
| A1 unimodal M1_accel1 | 0.8811 | ±0.0354 | [0.6363, 1.1376] |
| A1 unimodal M4_context | 0.8832 | ±0.0054 | [0.6361, 1.1478] |
| A4 process-aware gated | 0.9074 | ±0.0745 | [0.6749, 1.1628] |
| A1 unimodal M5_condition_indicators | 0.9399 | ±0.0265 | [0.6953, 1.2002] |
| A2 concatenation | 0.9643 | ±0.0779 | [0.6738, 1.2665] |

**The constant is the best model.** Every arm is worse in point estimate, and
every CI overlaps it.

A2 was **reused**, not rebuilt — it is the existing single-encoder
architecture. A3 is **new**: the task specifies decision-level combination
(per-group scalar heads, combining the scalars), which differs from the
existing embedding-concatenation late fusion.

## 3. Pairwise differences

Of 28 pairwise comparisons, **three exclude zero — and none of them is an arm
beating the constant**:

| Comparison | Δ | 95% CI |
|---|---|---|
| A1_M5_condition_indicators − constant | **+0.1355** | [+0.0703, +0.2044] |
| A3_modular_late − A4_gated | **−0.0781** | [−0.1619, −0.0046] |
| A1_M2_accel2 − A4_gated | **−0.0784** | [−0.1557, −0.0039] |

Read plainly: the condition-indicator arm is significantly **worse** than the
constant; the gated arm is significantly **worse** than both modular late
fusion and a single accelerometer used alone. The only resolvable signal in
this table is that more elaborate architectures are *worse*, which is what
adding parameters does when the features carry nothing to fit.

**No arm beats the constant, and no fusion strategy beats any other in the
helpful direction.**

## 4. Robustness — A3 and A4 under degradation

| Condition | A3 modular late | A4 gated | A4 gate weights [M1, M2, M4, M5] |
|---|---|---|---|
| none (baseline) | 0.8288 ±0.0106 | 0.9074 ±0.0745 | [0.355, 0.296, **0.040**, 0.308] |
| R1 drop M1 | 0.8365 ±0.0087 | 0.9160 ±0.0632 | [0.355, 0.296, 0.040, 0.308] |
| R2 drop M3 *(vacuous)* | 0.8288 ±0.0106 | 0.9074 ±0.0745 | [0.355, 0.296, 0.040, 0.308] |
| R3 noise 10 dB | 0.8283 ±0.0100 | 0.9072 ±0.0751 | [0.355, 0.296, 0.040, 0.308] |
| R3 noise 0 dB | 0.8267 ±0.0082 | 0.9062 ±0.0775 | [0.355, 0.296, 0.040, 0.308] |
| R4 drop M4 | 0.8273 ±0.0078 | 0.9074 ±0.0748 | [0.350, 0.305, 0.039, 0.307] |

Both arms are **flat to within seed noise under every degradation**, including
0 dB noise — noise as strong as the signal. R2 is bit-identical, as it must
be: the group is empty.

## 5. The R4 gate finding, described

**The gate does not fail, does not fall back, and does not produce garbage. It
degrades with no measurable consequence — and that is not a virtue.**

Three observations, in order of how much they revise the naive reading:

1. **The gate is not a constant.** Across runs its weights vary with std
   ≈ 0.39 / 0.27 / 0.04 / 0.33 against means of 0.355 / 0.296 / 0.040 / 0.308
   — variation comparable to the means themselves, i.e. a near-saturated
   softmax that assigns very different weights to different runs. It is
   strongly input-dependent.
2. **Its invariance under R1 and R3 is correct by design**, not a defect. The
   gate conditions only on M4, and R1/R3 degrade M1/M2, which the gate never
   sees. Identical gate output there is the architecture working as specified.
3. **Under R4 — removal of its own conditioning input — almost nothing
   happens.** Weights shift by ~0.005, MAE by 0.0000, and the run-to-run std
   is essentially unchanged (0.387 vs 0.394). Zeroing a gate's entire
   conditioning input should collapse its output to a single fixed weighting;
   instead the variation survives intact.

Two things explain why R4 is inconsequential. First, **M4 receives only 4% of
the gate's own combination weight** — the gate learned to down-weight the
process context to near-nothing, so removing it removes almost nothing.
Second, the surviving variation appears not to come from context *values*: an
untrained-model probe finds that zeroing M4 changes gate weights by only 0.013
on average, leaves run-to-run std nearly intact (0.016 → 0.012), and that gate
output correlates with **sequence length** (ρ ≈ −0.33 untouched, −0.41
zeroed). The plausible mechanism is that the gate's encoder branch responds to
the time mask — how long the run is — rather than to what the process context
says. **This is a probe on an untrained model and bounds the mechanism rather
than proving it for the trained gate.**

So "process-aware" is not doing what the exposé intends: the gate varies per
run, but under ablation its variation does not depend on the process context
it is supposed to be aware of.

## 6. SQ2 — how do the four fusion strategies compare?

**They do not differ in any way that favours fusion, and none beats a
constant.** Unimodal arms span 0.829–0.940, concatenation reaches 0.964,
modular late fusion 0.829, gated fusion 0.907, against a constant at 0.804.
Every confidence interval overlaps the constant's. The only three resolvable
differences all point the wrong way: the condition-indicator arm is worse than
the constant, and the gated arm is worse than both modular late fusion and a
single accelerometer.

This is the direct consequence of D1: the sensor features carry no signal
beyond permutation chance, so fusion has nothing to combine. Architectural
sophistication adds parameters and variance without adding information, which
is why the most elaborate arms (A2 concatenation, A4 gated) sit furthest from
the constant. **The answer to SQ2 is a clean null with intervals, not a
ranking.**

## 7. SQ3 — can gated fusion improve robustness under missing/degraded input?

**Not demonstrably, and this experiment cannot show that it could.** Both A3
and A4 are flat within seed noise under every degradation, including total
loss of a modality and 0 dB noise. On the face of it that is perfect graceful
degradation. It is not evidence of robustness.

**The caveat applies in full, and it is the honest reading.** Every arm is
effectively a constant predictor: none beats the per-fold training mean, and
all sit within overlapping intervals of it. A model that ignores its inputs
cannot be harmed by degrading them, so flat ablation curves here are a
restatement of the null in §6, not a robustness property. Presenting these
curves as evidence that gating confers robustness would be wrong.

The one substantive robustness finding is negative and specific: **the gated
architecture is significantly worse than simple modular late fusion**
(−0.0781 [−0.1619, −0.0046]) while also being unable to demonstrate that its
gate uses the process context at all (§5).

## 8. Assumptions not specified here

1. **M5 group created.** The task's scheme had no home for the condition
   indicators; I grouped rather than discarded them. Discarding 32 of 72
   columns was the alternative and would have broken comparability.
2. **Dropping a modality = zeroing its columns in place**, keeping input
   dimensionality fixed, so the architecture stays valid at inference. This is
   what a real sensor dropout looks like to a fixed-shape model.
3. **SNR convention**: features are unit-variance after normalisation, so
   noise SD = √(1/10^(SNR/10)) — 0.316 at 10 dB, 1.0 at 0 dB.
4. **A3's decision-level combination** is a learned linear weighting of the
   per-group scalars, initialised uniformly. The task said "combined at the
   decision level" without fixing the combiner.
5. **A4's shared projection** is 32-dimensional, matching `d_model`.
6. **Per-fold validation** for early stopping uses the third experiment (the
   one that is neither training nor held out), so the held-out experiment is
   never seen during training.
7. **The §5 mechanism probe is on an untrained model.** It bounds the
   explanation for the surviving gate variation; it does not prove it for the
   trained gate.
