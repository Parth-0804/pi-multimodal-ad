# Session handoff — read this first

Last updated: 2026-09-12

A self-contained brief for continuing this work in a fresh session with no
memory of prior conversation. Everything below is verified against the repo or
against output produced by the researcher; nothing is estimated. Where
something is a hypothesis rather than a measurement it says so.

---

## 1. What this project is

A Master's thesis built on the **PHM North America 2026 Data Challenge**.
A spur gear with 28 teeth is run to failure; the task is to estimate its
damage state over time from **vibration sensors alone**. Tooth photographs
exist **only for training** — the test and validation experiments are
sensor-only. The organiser provides **no ground-truth labels at all**, so the
project derives its own target from the training photos, then trains a
sensor-only model against it.

Scoring is **MSE after an optimal monotonic rescale** of the predictions, so
only trajectory *shape* counts, not absolute scale.

## 2. Where the work stands

Gate A is closed: two baselines are frozen and labelled, superseded runs are
archived, and a citable run index exists.

Current position: **Stage 1 — validating the target label** — where a real
confound was found and is mid-repair. Nothing has been fused yet. No model
currently beats a constant.

## 3. The numbers that matter

All percentage-point (pp) figures are in units of the provisional target
`phm2026_image_damage_v2` (candidate damage area as a percentage of the
visible tooth-flank ROI).

### Model results, EXP-F test split, n=8 runs

| Model | Metric | Level | Value |
|---|---|---|---|
| Constant (train mean **and** median) | MAE | run | **0.6797 pp** |
| PatchTST (sensor, canonical) | MAE | run | 0.8314 pp |
| PatchTST | bias | run | **+0.686 pp** (over-predicts) |
| PatchTST | R² | run | −0.806 |
| PatchTST | Spearman | run | 0.119 |
| RT-DETR R3 (frozen encoder) | MAE | image | 0.894 pp |
| RT-DETR R3 | MAE | run | 1.347 pp |
| RT-DETR R4-multitask | MAE | image | 0.733 pp |
| RT-DETR R4-multitask | MAE | run | 1.627 pp |
| RT-DETR R4-detector | mAP@0.50 | image | 0.0000831 |

**Nothing beats the constant at run level.** That is the central open problem.

The constant is fit on the **train split only** — verified in
`models/patchtst_regression.py::build_predictions`, which computes
`train_targets` from `sequences if sequence.split == "train"`. It is not an
oracle, so beating it is a fair bar.

### Dataset shape

- 3 experiments available: **EXP-A (5 runs), EXP-B (7), EXP-F (8)** = 20 runs.
- Split is fixed everywhere: **EXP-B train, EXP-A validation, EXP-F test**.
- 1,311 photos; 560 per-tooth labels; 28 teeth per run.
- ~370–380 one-minute sensor files per run (~6 h); range 73–528.
- The challenge actually has **7 experiments (A–G)**. Only A/B/F were ever
  downloaded. The other four are the official Test/Validation sets and have
  never been touched. Scope is hardcoded in three places, not just config:
  `configs/datasets/phm2026.yaml`, `PHM2026Adapter.supported_runs`, and the
  adapter's regex `EXP[\s_-]*([ABF])`.
- 0 of 560 per-tooth labels have been reviewed by a human.
- 0 of 1,311 photos have a verified UTC timestamp, so image↔sensor pairing is
  possible only at run level.

### Target scale (run-level top-3 mean)

| Experiment | Split | Mean | Std | Min | Max |
|---|---|---|---|---|---|
| EXP-A | validation | 5.772 | 0.775 | 5.007 | 6.918 |
| EXP-B | train | 4.948 | 1.330 | 3.508 | 6.552 |
| EXP-F | test | 4.853 | 0.824 | 3.833 | 6.175 |

## 4. The confound (the live issue)

**Measurement protocol differs by experiment.** EXP-A and EXP-B photograph
teeth 1–4 **ten times each** and every other tooth once. EXP-F photographs
**every tooth once**. The target took the **maximum across views**, and a
maximum over ten draws exceeds a maximum over one even when damage is
identical.

Measured effects:

| Check | EXP-A | EXP-B | EXP-F |
|---|---|---|---|
| Multi-view minus single-view tooth value | **+1.415 pp** | **+0.899 pp** | n/a (no multi-view) |
| Teeth 1–4 share of top-3 slots (base rate 0.143) | 0.533 | 0.333 | 0.000 |
| `multi_median_vs_single` (is the tooth really worse?) | −0.281 | −0.707 | n/a |

The inflation (+0.9 to +1.4 pp) is **larger than the entire 0.6797 pp error
budget** the models are trying to beat.

The negative `multi_median_vs_single` means multi-view teeth are **not**
genuinely more damaged — the elevation is an artefact of the aggregation rule.

**EXP-F confirms it from the other side:** teeth 1–4 there rank in the bottom
half in **all 8 runs**, averaging 2.30 pp against 2.96 pp for the rest (−22%).
So teeth 1–4 are genuinely *low*-damage, yet appear *high* in EXP-A/B. The
protocol effect is large enough to overturn a real 22% deficit.

### Repair attempted so far

A **one-deterministic-view** rule (use `canonical_tooth` where it exists; for
teeth 1–4 in EXP-A/B, which have only `camera_sequence` close-ups, take the
earliest by embedded `WIN_YYYYMMDD_HH_MM_SS` filename timestamp). Validated in
scratch, no official run minted.

Gap to EXP-F (4.853) under three aggregation rules:

| | max (original) | median | one-view |
|---|---|---|---|
| EXP-A | +0.92 | +0.42 | **+0.80** |
| EXP-B | +0.10 | −0.37 | **−0.03** |

Result: EXP-B is essentially fixed (−0.03). **Individual** tooth-4 top-3 share
lands on base rate (0.133 / 0.143). But teeth 1–4 **as a group** remain
elevated (0.40 / 0.286 vs 0.143), and EXP-A's gap is worse than under median.

### Why the residual cannot be calibrated away

**In EXP-A/B, tooth index and image role are perfectly confounded.** Teeth 1–4
have *only* `camera_sequence`; teeth 5–28 have *only* `canonical_tooth`. No
tooth anywhere is measured both ways, so no paired comparison exists and no
calibration factor can be fitted. The residual is most likely the close-up
framing itself (camera distance, crop, what fraction of the ROI is actually
flank) reading a systematically different ratio than the wide shot — but that
is a **hypothesis**, not a measurement.

### The open decision

Options on the table:

- **(a)** Accept the one-view fix and proceed to re-derive the official target
  and wire up the profile head.
- **(b)** Characterise the close-up framing effect first (compare ROI pixel
  counts / crop dimensions between roles). Diagnoses but cannot fix.
- **(d, recommended)** **Drop teeth 1–4 from the target in all three
  experiments.** Every remaining tooth is then one `canonical_tooth` wide shot
  everywhere, with no role mixing — the confound is removed at its source
  rather than mitigated. Cost is near zero: teeth 1–4 take **0 of 24** top-3
  slots in EXP-F, so EXP-F's target is unchanged exactly.

  Prediction if (d) is run: both gaps to EXP-F shrink, and **EXP-A falls well
  below +0.80**. If EXP-A's gap does *not* move, the reasoning is wrong and the
  elevation is something else.

  Costs: 24 teeth not 28, so `output_teeth=24` and all profile constants
  refit; deviates from the challenge's "all 28 teeth" framing and must be
  stated explicitly in the methods, not buried; and if teeth 1–4 carry real
  signal in EXP-A/B it is lost — though that cannot be checked, which is
  itself the argument for dropping.

## 5. Decisions already made (do not silently revisit)

| Decision | Rationale |
|---|---|
| **Canonical sensor baseline** = `20260911T193200607744Z-433d4154` | First PatchTST run reproducible from committed code. |
| **Canonical image baseline** = R4-multitask (`20260814T050026535618Z-9b00f099`) | Chosen for richer output (boxes + scalar from a shared encoder), needed by later stages. **Accepts that it is worse than R3 at run level (1.627 vs 1.347)** — the quantity actually scored. Both numbers must be reported side by side; an examiner will ask. |
| **Split fixed**: EXP-B train / EXP-A val / EXP-F test | Pinned via `split_manifest.parquet`, not recomputed. Never retune against EXP-F. |
| Provenance schema **1.1.0** | `git.dirty` now means tracked modifications only; `git.untracked_present` is separate. |
| 11 superseded runs archived to `runs/_superseded/` | Config-pinned and newest-per-study runs are protected. |

## 6. Reasoning worth not re-deriving

**The dirty-tree flag was a red herring.** All 28 historical runs record
`dirty: true`, which initially looked like an integrity crisis. It is not.
`_git_state` counted *untracked* files as dirtiness, and every run writes a new
untracked output directory, so the flag went true after essentially any run.
Fixed in schema 1.1.0. Pre-1.1.0 runs are **unresolvable**, not contaminated.

**The +0.686 bias is probably validation-driven, not train-driven.** The
train→test target gap is only +0.095, far too small to explain it. But EXP-A —
the **validation** set used for early stopping — is the *most* protocol-inflated
experiment and sits +0.919 above EXP-F. The observed bias lands about
three-quarters of the way from the train gap to the validation gap. So model
*selection* is plausibly pulling predictions toward an inflated level. This is
a hypothesis consistent with the numbers, not proof.

**A constant cannot benefit from monotonic rescaling.** A flat prediction
carries no rank information, so isotonic regression cannot recover anything
from it. PatchTST's Spearman of 0.119 is weak but non-zero. **Monotonic-MSE is
therefore the single metric where the sensor model could plausibly overtake the
constant, and it has never been computed.** This is cheap and high-value.

**Sorting hides the confound.** `SortedProfileHead` sorts the profile
ascending, discarding tooth identity. Any per-tooth inflation survives as an
inflated upper profile with nothing left in the output to attribute it to —
which is why the label had to be checked *before* the head is trained, not
after.

**Images vanish at inference.** So "fusion" cannot mean two live input streams.
It means either (i) fusing the sensor sub-modalities that *are* present at test
time, or (ii) using the image branch as a **teacher** that shapes the sensor
representation during training and is then discarded.

## 7. Tools built (all tested)

| Path | Purpose |
|---|---|
| `scripts/ops/build_thesis_run_index.py` | Chronological citable index of every run → `docs/thesis/RUN_INDEX.md`. Optional archiving; refuses to move config-pinned or newest-per-study runs. |
| `scripts/ops/repin_source_run.py` | Re-points one `source_runs` entry at a different run — id, directory, all artifact hashes — leaving the rest of the file byte-identical. |
| `scripts/targets/analyze_tooth_profiles.py` | Five diagnostic blocks plus train-only fitting of the profile-head constants. Validated against synthetic data in both confounded and clean regimes. |

Model code already written by the researcher, **not yet wired into any config
or training script**: `SortedProfileHead` and `profile_loss` in
`models/patchtst.py`. Maps the pooled representation to a monotone 28-vector
via softplus deltas and cumsum, so `profile[:, -3:].mean(1)` *is* the top-3
aggregate by construction. Inert while `output_teeth is None`.

## 8. What comes next

Full detail in `docs/planning/FUSION_ROADMAP.md`. Sequence:

1. **Stage 1 (current)** — finish the label repair, re-derive the official
   target, re-run diagnostics.
2. **Stage 2** — implement monotonic-rescale-then-MSE and re-score everything.
   Cheap, and could reverse the headline result.
3. **Stage 3** — fuse the sensor sub-modalities present at inference (process
   context / organiser RMS / condition indicators), with missing-modality
   ablations. Buildable today, no new data.
4. **Stage 4** — per-tooth supervision via `SortedProfileHead` (the 28× sample
   lever). Needs a feasibility probe on the raw HDF5 encoder channel first.
5. **Stage 5** — privileged-information distillation, image teacher → sensor
   student.
6. **Stage 6** — oracle upper bound; the gap quantifies what the image modality
   is worth.

## 9. Rules of engagement

- `AGENTS.md` is the binding contract. Raw data under `gtc-data-experiment/**`
  is immutable. Run outputs are append-only and never overwritten.
- **Never retune against EXP-F.** Stated explicitly in
  `.github/copilot-instructions.md`.
- Every run writes a versioned, hash-pinned directory. Downstream stages load
  upstream runs by `run_id` + SHA-256 via `load_pinned_run`, which re-hashes and
  refuses on mismatch. Moving a pinned run breaks training.
- `tables/*.parquet` are gitignored as regenerable. They exist only on the
  researcher's compute box, **not** in a fresh clone — so analysis requiring
  them cannot run from a bare checkout.
- The target is a **provisional pseudo-label**, never organiser ground truth.
  Every artefact carries that status string; keep it.
- Competition ended 2026-08-07; manuscript deadline 2026-09-04. Both have
  passed. This is thesis work now, not a submission race.
