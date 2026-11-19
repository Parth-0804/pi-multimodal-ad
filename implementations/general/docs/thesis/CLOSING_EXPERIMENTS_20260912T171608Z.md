# Closing experiments — Tasks A, B, C

2026-09-12. Last experiments on EXP-A/B/F. v3 target (24 teeth, artifact
`20260912T052857044116Z-c936a4e3`), committed LOEO folds, hyperparameters
frozen, no tuning anywhere.

**Task C numbers are SYNTHETIC by construction and appear in their own
section and their own tables only.** They are a control on the pipeline, never
a PHM result.

---

## 1. Task A — rank-mapped oracle

**Only 1 of 3 LOEO folds is computable.** R4 has predictions for EXP-A and
EXP-F but none for EXP-B, so EXP-B can neither be ranked as a held-out fold
nor fit λ as a training fold. This is the same coverage blocker that stopped
the Phase 3 distillation build.

| Fold | Status |
|---|---|
| predict EXP-A (train EXP-F) | computable, n=5, λ = 0.7407 |
| predict EXP-B (train EXP-F) | **not computable** — no image predictions to rank EXP-A's held-out runs |
| predict EXP-F (train EXP-B) | **not computable as specified** — λ must be fit on EXP-B, which has no image predictions |

On the one computable fold:

| Model | MAE | clustered 95% CI | n |
|---|---|---|---|
| **rank-mapped ORACLE** *(needs photographs; not deployable)* | **0.5724** | [0.2121, 1.0777] | 5 |
| constant, same 5 runs | 0.7430 | [0.2344, 1.3269] | 5 |

**Is the target predictable from anything? Weak yes, on thin evidence.** The
point estimate lands almost exactly on the predicted ~0.59, which is a real
success for the derivation. But the intervals overlap almost completely at
n=5, so this is not a significant result.

Two corrections to the task's framing:

- The prediction compared ~0.59 against **0.8042**, the *20-run* LOEO
  constant. The like-for-like constant on the 5 covered runs is **0.7430**, so
  the gain is 0.171, not 0.23.
- "This CANNOT lose by construction" does not strictly hold. λ is fitted on
  the training experiment, so a held-out loss to the constant was possible
  without being an implementation error. It won anyway, so the point is moot
  here — but the reasoning should not be relied on next time.

ρ = 0.659 rests on 20 points with SE ≈ 0.23, and the improvement scales with
ρ. Task B sharpens this: see §2.

## 2. Task B — odd/even tooth split

Balance confirmed: odd = {5,7,…,27} (12 teeth), even = {6,8,…,28} (12 teeth).
Baseline reproduces the committed figure exactly (**+0.6593** vs the recorded
+0.659), which validates the harness before the split is applied.

| Configuration | ρ | P(null ≥ obs) | n |
|---|---|---|---|
| baseline — all 24 teeth both sides | **+0.6593** | — | 13 |
| target = ODD, prediction = EVEN | **+0.3736** | 0.105 | 13 |
| target = EVEN, prediction = ODD | **+0.4011** | 0.087 | 13 |

**Verdict: INTERMEDIATE, in both directions.** Neither reaches the ≥0.5
"survives" threshold nor the ≤0.2 "collapses" threshold. About **60% of the
correlation survives** the split, so +0.659 is **part real run-level signal
and part shared-photo artefact** — and neither split direction reaches
conventional significance at n=13 (p ≈ 0.09–0.11).

This partially undercuts Task A. The oracle's projected gain scales with ρ: at
ρ ≈ 0.39 rather than 0.659, r = 2·sin(πρ/6) falls from ≈0.68 to ≈0.41, roughly
halving the expected improvement. **The oracle's 0.5724 was built on the
un-split ρ and is therefore optimistic.**

Coverage: 13 runs (EXP-A + EXP-F). No EXP-B predictions were generated; they
would be in-sample, since R4 was trained on EXP-B.

**Stated limitation, carried as instructed:** if lighting varies per *session*
rather than per photo, session effects are shared across the odd/even split
and survive regardless. This test separates per-photo noise from run-level
effects; it **cannot** distinguish run-level damage from run-level lighting.
Resolving that needs information outside the images.

---

## 3. Task C — synthetic control

> **EVERY NUMBER IN THIS SECTION IS SYNTHETIC.** Features were generated from
> the true target by construction — `f[m,j] = α·z_r + √(1−α²)·ε`. That is what
> makes this a control rather than a result. No number here describes the PHM
> data, and none may be placed in a table with a real number.

### C.1 sensitivity sweep — prediction FAILED, mechanism identified

| α | MAE (3 seeds) | constant | Δ | seeds significant |
|---|---|---|---|---|
| 0.0 | 0.7998 ± 0.0472 | 0.8042 | −0.005 | **0/3** |
| **0.2** | **0.1616 ± 0.0197** | 0.8042 | −0.642 | **3/3** |
| 0.4 | 0.1026 ± 0.0158 | 0.8042 | −0.701 | 3/3 |
| 0.6 | 0.0992 ± 0.0080 | 0.8042 | −0.704 | 3/3 |
| 0.8 | 0.1094 ± 0.0231 | 0.8042 | −0.694 | 3/3 |
| 1.0 | 0.1011 ± 0.0139 | 0.8042 | −0.703 | 3/3 |

**α\* = 0.2** — the smallest α tested at which the model beats the constant
with a CI excluding zero, in 3 of 3 seeds. The true threshold lies somewhere
in (0, 0.2].

**α = 0 reproduces the constant** (0.7998 vs 0.8042, 0/3 significant), as
expected — a necessary sanity check that the harness is not leaking.

**The stated expectation of monotonic decrease FAILED.** MAE drops sharply at
α = 0.2 then plateaus, and wobbles non-monotonically: 0.0992 (α=0.6) →
0.1094 (α=0.8) → 0.1011 (α=1.0).

Per instruction I stopped and investigated rather than proceeding as if it
held. My reading — offered as evidence, not as a dismissal — is **saturation,
not a pipeline defect**:

- The wobble is inside seed noise. Per-α seed spreads are 0.020–0.051, larger
  than the 0.010 non-monotone step.
- Each run averages ~370 minutes × 72 channels ≈ **26,600 independent samples**
  of `α·z_r + noise`. Even at α = 0.2 that recovers `z_r` almost exactly, so
  the curve should saturate immediately rather than ramp.
- The plateau sits at ≈0.10, not 0, consistent with a floor from estimating
  µ_train and σ_train on 7–8 runs rather than from feature information.

A defect cannot be fully excluded from this evidence; what can be said is that
the failure is confined to the saturated region and the informative part of
the curve (0 → 0.2) behaves exactly as predicted.

### C.2 channel sparsity (α = 0.6)

| informative channels | MAE (3 seeds) | Δ vs constant | seeds significant |
|---|---|---|---|
| 1 of 72 | 0.4996 ± 0.0515 | −0.304 | 3/3 |
| 8 of 72 | 0.1742 ± 0.0270 | −0.630 | 3/3 |
| 72 of 72 | 0.0992 ± 0.0080 | −0.704 | 3/3 |

Monotone in k, as expected. **Even a single informative channel out of 72 is
detected significantly**, which is the realistic case for a physics-informed
feature.

### C.3 fusion control — distillation does not work even with signal present

Synthetic teacher at β = 0.678 (Spearman ≈ 0.66, matching R4's observed
value); pairwise logistic rank-distillation at weight 1.0.

| α | seed | plain | distilled | Δ | 95% CI | helps? |
|---|---|---|---|---|---|---|
| 0.0 | 1 | 0.7384 | 0.8119 | +0.0737 | [−0.028, +0.170] | no |
| 0.0 | 2 | 0.8531 | 0.8480 | −0.0053 | [−0.043, +0.031] | no |
| 0.3 | 1 | 0.1465 | 0.1601 | +0.0139 | [−0.049, +0.074] | no |
| 0.3 | 2 | 0.1273 | 0.0763 | −0.0510 | [−0.086, −0.022] | **yes** |
| 0.6 | 1 | 0.1086 | 0.1539 | +0.0453 | [+0.018, +0.074] | **hurts** |
| 0.6 | 2 | 0.1001 | 0.1968 | +0.0965 | [+0.030, +0.161] | **hurts** |

Against the three stated outcomes, this is the **third**: distillation never
reliably helps. It is neutral at α = 0, mixed at α = 0.3 (1 of 2 seeds), and
**significantly harmful at α = 0.6 in both seeds**.

The good news is what did *not* happen: **no help at α = 0 rules out the
teacher-leakage bug.** Had distillation improved a student with zero feature
signal, that would have indicated the teacher was injecting target information
directly.

**Important caveat that weakens this conclusion.** At α ≥ 0.3 the synthetic
student is already near the 0.10 floor, so the task loss is essentially solved
and any auxiliary term can only perturb it. This control may therefore be
unfair to distillation precisely *because* the synthetic student is too good —
the regime where a teacher should help (weak but non-zero student signal) is
narrow here. Separating "mechanism ineffective" from "auxiliary weight badly
chosen for an already-solved task" needs a distillation-weight sweep, which
this task did not specify and I did not run.

### One-sentence answer to Task C's question

**Yes — the pipeline was fully capable of detecting signal:** it finds even
α = 0.2 with 3/3 seeds significant, and finds a single informative channel out
of 72, so the failure to beat the constant on real data reflects absent
feature signal rather than an undetecting pipeline.

---

## 4. What failed its stated prediction

1. **C.1 monotonicity — FAILED.** MAE does not decrease monotonically in α; it
   saturates after α = 0.2 and wobbles within seed noise. Evidence in §3.1
   points to saturation from ~26,600-sample averaging rather than a defect,
   but a defect is not excluded.
2. **Task A coverage — 5 of 20 runs, not 20.** Two of three folds are not
   computable because R4 has no EXP-B predictions.
3. **Task A's comparison base was wrong** — ~0.59 was set against the 20-run
   constant (0.8042); the like-for-like value is 0.7430.
4. **Task A's "cannot lose by construction"** does not hold, since λ is fit on
   train, not on the held-out fold.
5. **Task B landed INTERMEDIATE**, matching neither stated branch.
6. **C.3 matched the least favourable of the three outcomes** — the mechanism
   never reliably helps, and hurts at α = 0.6.

## 5. Assumptions not specified here

1. **Model for Task C** — the task said "the model" without naming one; I used
   the PatchTST single-encoder sensor baseline, not the late-fusion variant.
2. **No renormalisation of synthetic features.** They are unit-variance by
   construction (`α·z + √(1−α²)·ε`), so the pipeline's train-fitted normaliser
   would be near-identity. Skipped, and stated.
3. **Early stopping inside Task C** uses the training experiment's own loss.
   LOEO leaves no third experiment, and using the held-out fold would leak.
4. **Rank-distillation mechanism** was unspecified; I used a pairwise logistic
   ranking loss over each batch at weight 1.0, with no weight sweep (see the
   C.3 caveat).
5. **Task A λ fit** by least squares of `(target − µ) ` on `σ·z` over the
   training experiment.
6. **C.3 used 2 seeds**, not 3, to stay inside the compute budget; C.1 and C.2
   used 3.
7. **Task B run-level aggregation** applies the v3 top-3 rule to each 12-tooth
   half, so it is the top 3 of 12 rather than of 24.
