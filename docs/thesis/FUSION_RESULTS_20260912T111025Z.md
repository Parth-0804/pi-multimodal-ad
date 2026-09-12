# Fusion build — results

2026-09-12. Phases 0–2 completed. **Phase 3 was not built**, because Phase 1
removed the evidence for both of its candidate designs. Reasoning in §5.

---

## 1. The table

Leave-one-experiment-out, v3 target (24 teeth), run-level MAE, **run-clustered**
95% CI, every run predicted once by a model that never saw its experiment.

| Model | n runs | MAE ↓ | 95% CI (clustered) | Spearman |
|---|---|---|---|---|
| **constant (per-fold train mean)** | 20 | **0.8042** | [0.577, 1.036] | −0.035 |
| `fused_all_three` (late fusion) | 20 | 0.8238 | [0.553, 1.101] | −0.105 |
| `patchtst_single_encoder` (sensor baseline) | 20 | 0.9415 | [0.675, 1.226] | −0.205 |
| RT-DETR R4 image baseline — **NOT LOEO** | 13 | 1.8264 | [1.458, 2.221] | **+0.659** |

Folds: predict EXP-A ← train EXP-F, validate EXP-B · predict EXP-B ← train
EXP-F, validate EXP-A · predict EXP-F ← train EXP-B, validate EXP-A. LOEO
leaves no third experiment for early stopping, so the larger remaining
experiment trains and the smaller validates — deterministic, and never the
held-out experiment. The EXP-F fold is exactly the project's existing protocol.

Frozen hyperparameters, unchanged from the committed config, nothing tuned:
`max_epochs 80, patience 10, batch_size 4, lr 1e-3, weight_decay 1e-4`, seed
20260814.

**The image row is not comparable to the others.** R4 was trained on EXP-B, has
no EXP-B predictions at all, and covers 13 of 20 runs. It is a reference, not a
LOEO result.

## 2. Does fusion beat the constant?

**No.** Paired on the same runs, clustered by run:

| Comparison | Δ MAE vs constant | 95% CI | Excludes zero? |
|---|---|---|---|
| `fused_all_three` − constant | **+0.0177 pp** (worse) | [−0.196, +0.228] | **No** |
| `patchtst_single_encoder` − constant | +0.1358 pp (worse) | [−0.085, +0.356] | **No** |

Last night's −0.0800 pp fusion advantage on EXP-F **did not survive**. Under
LOEO the sign flips: fusion is marginally *worse* than the constant, and the
interval spans zero either way. **Not distinguishable from the constant** — and
the EXP-F number was a single-fold artefact, which is exactly what 8
contaminated points were expected to produce.

The constant is the best model in this table.

Note also that all three sensor models have **negative** LOEO Spearman
(−0.04, −0.10, −0.21). The sensor features as currently built carry no
run-ranking signal at all. The image model ranks runs well (+0.659) while
being badly miscalibrated in level (MAE 1.83) — it knows which runs are worse,
not by how much.

## 3. Phase 1: what the image branch actually transfers

The claim in circulation — reported to the supervisor — was that the image
model "correctly picks out which teeth are damaged but gets the severity
wrong." It traces to a tooth-indexed Spearman **pooled across all runs** of an
experiment. Evidence: `scripts/results/analyze_teacher_identity.py`.

**1.1 — tooth-indexed, not sorted.** The original analysis joined on
`tooth_id`, so it was not an order-statistic artefact. The *kind* of claim was
legitimate. (Elsewhere the sensor path does sort: `build_profiles` calls
`np.sort` and `SortedProfileHead` emits a monotone vector — both are order
statistics and neither can express tooth identity.)

**1.2/1.3 — the claim is directionally right and numerically overstated.**
Pooling conflates two things: if one run is more damaged overall, all its teeth
outrank another run's, so a model knowing only run-level severity still scores
a high pooled correlation. Decomposed:

| | EXP-A | EXP-F |
|---|---|---|
| pooled ρ (**what was reported**) | +0.4432 | +0.4981 |
| **within-run ρ** (the real "which teeth") | **+0.3703** | **+0.4372** |
| between-run ρ (severity, folded into the pool) | +0.6000 | +0.8571 |
| P(tooth-shuffle null ≥ observed within-run) | 0.0200 | 0.0000 |

So within-run identity is **real** and clearly beats a tooth-shuffling null.
But ρ ≈ 0.37–0.44 is a moderate rank correlation, not "correctly picks out",
and the reported figure was inflated by run severity. **The supervisor should
be told the direction holds and the number was overstated** — not that the
claim was wrong, and not quietly dropped.

**Is there a path for identity to reach the sensor branch? No.** Tooth-indexed
sensor output requires knowing which angular sector is which tooth — a
keyphasor. `Vibration/Encoder` gives absolute degrees 0–360 with no index pulse
tying angle to tooth 1. Identity is real in the image branch and not
transferable to the sensor branch.

**1.4 — what is transferable (shape), and it is not there.**

| | EXP-A | EXP-F |
|---|---|---|
| level-free sorted-shape correlation | +0.947 | +0.961 |
| top-3 share of run total — teacher vs true | 0.156 vs 0.190 | 0.157 vs **0.206** |
| across-run correlation of that concentration | −0.900 (n=5) | **+0.119** |

The teacher systematically **understates concentration** and barely tracks
which runs are concentrated versus spread (+0.119 on EXP-F). The high
level-free shape correlation is near-trivial: any two sorted, mean-normalised
monotone profiles correlate highly. (A first version of this metric used
Spearman between sorted profiles and returned exactly +1.0000 by construction;
that was a bug in the metric, fixed, and is not reported as a finding.)

**Coverage blocker: the teacher has zero predictions for EXP-B** — 0 of 7 runs.

## 4. Every EXP-F exposure to date

Reconstructed from the project record; a count rather than an exact audit, and
it belongs in the methods as a stated limitation.

| Episode | Approximate EXP-F scorings |
|---|---|
| Historical pre-existing runs (R3, R4, PatchTST, naive baselines) | many |
| Shrinkage test, R3 + R4 per-image predictions | 2 |
| Tooth-level constant baseline | 1 |
| `broadband_stats_only`, 5 seeds + 2000-draw bootstrap | 5 + bootstrap |
| Teacher-profile check | 1 |
| Profile head: 5 seeds, 10-point weight-decay sweep, multi-seed at selected, bootstraps | ~20 |
| Run-identifier comparison (2 models) | 2 |
| Overnight Phase 0.6 reproduction | 1 |
| Overnight Phase 2 rescoring + 20,000-draw null | 1 + null |
| Overnight Phase 3 (the one pre-registered evaluation) | 1 |
| Today: Phase 0.3 reproduction, Phase 1 analysis, Phase 2 LOEO fold | 3 |

**EXP-F is not a holdout and has not been one for a long time.** The overnight
"exactly one evaluation" was true only within that pre-registration's scope.
This is the reason LOEO now replaces single-split EXP-F reporting.

## 5. What I did not do, and why

**Phase 3 — the fusion model — was not built.** Its design was explicitly
conditional on Phase 1, and neither branch's precondition survived:

- *Default (shape transfer)* required "shape agreement but no usable identity
  path." Shape agreement is not there: the teacher's across-run concentration
  correlation is **+0.119** on EXP-F and −0.900 on EXP-A at n=5. Transferring
  that would transfer approximately nothing.
- *Alternative (identity path)* required a genuine identity path. Identity is
  real in the image branch but needs a keyphasor to reach the sensor branch,
  and there is none.

Two further blockers, either of which is independently sufficient:

1. **No teacher coverage of EXP-B** (0 of 7 runs). Distillation needs teacher
   outputs on training data; EXP-B trains 2 of the 3 LOEO folds. Generating
   them would mean running R4 inference on EXP-B — the experiment R4 was
   *trained* on — so the targets would be in-sample and optimistically biased,
   a known distillation trap.
2. **The student has no signal to improve.** All three sensor models have
   negative LOEO Spearman. There is no rank signal for a teacher to sharpen.

Building it anyway would have produced a model, a table, and no defensible
claim. That seemed worse than reporting the blocker.

**Also not done:**

- **Did not push.** `origin/main` is still at `e6db986`; **8 commits** are
  local-only on one machine with no backup. No SSH key, no token, no credential
  helper, no `gh` — re-checked and retried this session. This is the single
  highest-priority item and it needs credentials only you can supply.
- Did not tune anything inside or outside the LOEO loop, add variants after
  seeing results, or move a threshold.
- Did not delete or move any run directory.
- Did not reuse the pre-v3 numbers 0.632 / 0.656 / 0.733; they are pre-v3,
  28-tooth, EXP-F-only and uncertainty-free, and are superseded by §1.

## 6. What I would do next

1. **Push.** Everything else compounds on an unbacked machine.
2. **Report the corrected supervisor claim** (§3): direction holds, number
   overstated, identity not transferable without a keyphasor.
3. **The honest headline is now available and defensible:** under a protocol
   with 20 evaluation points and run-clustered intervals, on a
   confound-repaired target, *nothing beats a constant* — and the sensor
   features carry no run-ranking signal at all, while the image modality does
   (+0.659). That is the Stage 6 oracle-gap story with evidence behind it,
   and it is a stronger thesis result than a marginal fusion win would have
   been.
4. If fusion is still wanted, the blocker to clear first is **teacher coverage
   of EXP-B by a model not trained on it** — not another architecture.
