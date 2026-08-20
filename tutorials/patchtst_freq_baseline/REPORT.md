# A from-scratch PatchTST baseline on raw HF/spectral vibration data

> **Read this before the numbers.** The target used throughout — `raw_top3_mean_pct`
> from target version `phm2026_image_damage_v2` — is a **provisional,
> image-derived pseudo-label**, not organizer ground truth, not
> expert-reviewed. Nothing in this report is a claim about physical gear
> damage. It measures whether a from-scratch PatchTST trained on raw
> high-frequency vibration spectra can predict that pseudo-label better
> than the existing low-frequency (LF) summary-statistic baseline or a
> trivial constant. Every line of the data pipeline, feature engineering,
> model, and training loop here is new code written for this tutorial —
> the only reuse is reading two pinned parquet outputs (the T2.2 split,
> the `phm2026_image_damage_v2` run-level targets) as data, per the task's
> explicit exception.

## Why this exists

The existing LF-only PatchTST baseline
(`docs/planning/P4_PATCHTST_BASELINE_CHECKPOINT.md`) used only bounded,
one-minute *summary statistics* (mean/std/median/min/max/last/slope of
five low-rate context channels) and explicitly flagged this as a
limitation: *"This initial LF representation omits raw vibration spectral
information and does not prove sensors lack damage information."* This
tutorial tests that directly, from scratch, on the raw 102,400 Hz
`Vibration/Accel 1` and `Accel 2` waveforms the LF baseline never touched.

## Headline result

| model | MAE (pp) | RMSE | Spearman | R² |
|---|---:|---:|---:|---:|
| Training mean (recomputed here) | 0.6797 | 0.7768 | n/a (constant) | -0.0153 |
| Training median (recomputed here) | 0.6797 | 0.7712 | n/a (constant) | -0.0009 |
| Existing LF-only PatchTST (cited, P4) | 1.011 | 1.243 | -0.262 | -1.601 |
| **This HF/spectral PatchTST (all 72 features)** | **1.2203** | **1.3583** | **-0.0238** | **-2.1045** |

**This is a genuine negative result, reported plainly, as instructed.**
The from-scratch HF/spectral baseline does not beat either constant
baseline, and it is also worse than the existing LF-only baseline it was
built to test against. Recomputed constants (0.6797) match P4's cited
0.680 pp almost exactly — the same pinned target values are being used,
so this comparison is apples-to-apples, not an artifact of a
target-reading bug. MAE 95% bootstrap CI (2,000 resamples, N=8 test runs):
**[0.846, 1.640]**.

Per-run EXP-F predictions (the sole test-set evaluation pass):

| run | y_true | y_pred | abs_error |
|---|---:|---:|---:|
| EXP-F/run-1 | 3.917 | 5.017 | 1.101 |
| EXP-F/run-2 | 4.698 | 3.666 | 1.032 |
| EXP-F/run-3 | 3.833 | 4.466 | 0.633 |
| **EXP-F/run-4** | **4.245** | **1.843** | **2.402** |
| EXP-F/run-5 | 6.175 | 4.341 | 1.834 |
| EXP-F/run-6 | 5.493 | 4.247 | 1.246 |
| EXP-F/run-7 | 5.232 | 6.344 | 1.112 |
| EXP-F/run-8 | 5.229 | 4.827 | 0.403 |

## Does adding spectral/HF information change the result — and why?

**Yes, it changes the result, in the negative direction — and the
evidence points at overfitting from excess feature dimensionality as a
real, implicated cause, not (only) an absence of signal in the raw HF
data.** Retraining the *actual* model (not a separate probe) on feature
subsets (`analysis/ablation.py`) found the full 72-feature model is the
**single worst-performing variant of everything tested**:

| variant | n_features | MAE | Spearman |
|---|---:|---:|---:|
| broadband_stats_only (RMS/crest/centroid, no bands) | 8 | 0.730 | 0.048 |
| low_bands (20-297 Hz) only | 30 | 0.737 | 0.143 |
| bands_only (no broadband stats) | 66 | 0.763 | 0.143 |
| mid_bands (297-4,408 Hz) only | 30 | 0.768 | 0.095 |
| accel1 only | 36 | 0.779 | **0.405** |
| accel2 only | 36 | 0.815 | 0.095 |
| high_bands (4,408-51,200 Hz) only | 28 | 0.997 | **-0.357** |
| **all 72 features** | **72** | **1.220** | **-0.024** |

Every reduced-dimensionality variant beats the full model — several by a
wide margin — though **none beats the 0.6797 constant baseline either**.
"X (headline MAE 1.220) is high partly because Y (72 continuous features
fit from only 7 training runs) — evidenced directly by Z (every smaller
feature subset, down to just 8 broadband stats, scores better than the
full model on the identical train/val/test split and target)." This does
not prove spectral information is useless — it shows this particular
72-dimensional representation, at this sample size, overfits before it
can be evaluated on its merits.

## Which bands/channels carry signal, if any?

Weakly suggestive only (formal caveat below): `accel1_only` reaches the
best rank correlation of any variant (Spearman 0.405) despite not having
the lowest MAE — hinting Accel 1 alone carries some signal that gets
diluted when combined with Accel 2 and all bands. **`high_bands_only`
(4,408-51,200 Hz) is the worst individual variant** (MAE 0.997, Spearman
**-0.357**, i.e. anti-correlated with the target) — the top ~2.5 octaves
of the 102.4 kHz-rate spectrum look like the least reliable frequency
range in this dataset at this sample size, while `low_bands` (20-297 Hz,
the shaft-rate/gear-mesh-fundamental range) is among the better-behaved
reduced variants. Physically plausible (shaft-rate-scale vibration is
typically more stable/interpretable than high-frequency content, which
can be dominated by acquisition noise or unrelated resonances) but **not
proven** — see the statistical-power caveat below.

## Residual analysis

Full detail: `analysis/residuals.py` output, `residual_analysis.png`.

- **Error rises monotonically validation (0.524) → train (0.776) → test
  (1.220)**. Validation error being *lower* than training error is a
  symptom, not a good sign: the model's checkpoint was selected (early
  stopping) on the exact split where it scores best, only 140 of 540
  training epochs were actually used (training itself hadn't converged),
  and — critically — **2 of the validation split's 5 runs are exact
  duplicates of each other** (see below), so the validation signal that
  drove model selection is less independent than "N=5" suggests.
- **No run-order (progressive-wear) pattern in EXP-F**: `corr(run_number,
  signed_error) = -0.105` (N=8) — negligible, unlike the RT-DETR image
  baseline, which found a *mild* upward recall trend across EXP-F runs.
  No comparable trend appears here.
- **No target-magnitude pattern**: `corr(y_true, abs_error) = 0.136`
  (N=8) — the model is not simply failing more on higher-damage runs.
- **Errors are spread across EXP-F, not concentrated — except one run**:
  residuals scatter both above and below zero across all 8 test runs, no
  dominant outlier — except **EXP-F run-4** (abs_error 2.40, more than
  double the next-worst), the model's most compressed/lowest single
  prediction (predicted 1.84 against a true 4.25). Named plainly rather
  than averaged away.
- **Does EXP-F's domain shift show up the way it did in the RT-DETR
  work?** Differently, and less legibly. RT-DETR found a *specific,
  geometric* mechanism (pseudo-box size distribution shift driving IoU
  recall to near-zero). Here, the shift shows up only as elevated *mean*
  error on the whole EXP-F split relative to train/validation — real, and
  directionally consistent with a domain-shift story, but this analysis
  did not find a specific *mechanism* within EXP-F (no run-order or
  target-magnitude pattern explains it). That is an honest limit of what
  N=8 supports, not evidence that no mechanism exists.

## An independent, load-bearing data-quality finding: EXP-A Run-1 ≡ Run-2

Comparing spectral-feature fingerprints across all 190 possible run pairs
(`build_features.py`'s output) found **EXP-A Run-1 and EXP-A Run-2's
entire HF archives are exact duplicates**: 372/372 rows identical across
all 72 features, identical internal member filenames in identical order
(149 "Run1"-labeled + 223 "Run2"-labeled members, in both outer archives).
No other pair among the 190 overlaps at all.

This independently *confirms and sharpens* a concern
`docs/planning/PROJECT_STATE.md` already carried as *unverified*:
*"EXP-A Run 2 stays in scope with its reported, unverified 311-file
overlap warning."* The real extent, verified here directly against
spectral content rather than filenames, is larger than "unverified
~311-file" — it is a **complete, exact, 372/372 duplication**.

Per the hard constraint against re-deriving the pinned split, EXP-A Run-2
was kept in the validation split exactly as pinned — nothing was excluded
or altered. Two consequences, stated plainly: (a) **no train/test
leakage** — the duplication is entirely contained within validation, EXP-B
(train) and EXP-F (test) share zero rows with anything; (b) **the
validation split effectively provides 4 independent run-level
observations, not 5** — Run-1 and Run-2 necessarily receive near-identical
predictions by construction, which plausibly contributed to the
early-stopping/generalization gap described above.

## What's statistically supportable vs. suggestive only

N is genuinely tiny throughout: 7 training runs, 5 validation runs (4
independent, per the finding above), 8 test runs.

- **Supportable, treated as fact**: the headline ranking (constants <
  LF-only PatchTST < this HF/spectral PatchTST) for this exact,
  reproducible configuration; the full-vs-ablated-variant ordering for
  this exact model/data; the EXP-A Run-1/Run-2 duplication (a certain,
  fully-verified fact, not a probabilistic estimate).
- **Suggestive only, not decisive**: every correlation in this report
  (run-order, target-magnitude, band/channel importance) is estimated
  from 7-8 points. The bootstrap 95% CI on the headline MAE alone spans
  [0.85, 1.64] — wider than the gap between any two rows in the ablation
  table. No individual band/channel ranking here should be read as
  "proven more informative" — only as "this is what appeared in this one
  N=7 training run." A different seed, a different patch geometry, or (by
  far the most important lever) a genuinely larger N would be needed
  before treating any single ablation ranking as stable.

## Concrete next steps — each following from a specific finding above

1. **Reduce feature dimensionality before drawing any conclusion about
   whether HF spectral content helps.** Directly follows the ablation
   finding: every reduced variant beat the full 72-feature model. A
   principled next step is not "add more spectral detail" but the
   opposite — e.g., PCA/factor-reduce the 64 band-energy features to a
   handful of components fit on train only, or restrict to the
   `broadband_stats_only` (8-feature) or `low_bands_only` (30-feature)
   variants that already outperformed the full model here, before
   re-testing against the constant baseline.
2. **Treat the 4,408-51,200 Hz band range with real suspicion, not as a
   free source of extra signal.** Directly follows the ablation table:
   `high_bands_only` was the single worst individual-variant Spearman
   (-0.357). Before trusting any future model that includes this range,
   check whether it is capturing acquisition-chain noise/resonances
   rather than gear-mesh-related content — e.g., by checking coherence
   with a non-damage-related covariate, or simply re-testing with that
   range excluded once dimensionality is otherwise fixed.
3. **Do not use EXP-A Run-2 as if it were 5th independent validation
   evidence.** Directly follows the confirmed exact duplication. Any
   future validation-based decision (confidence thresholds,
   early-stopping criteria, architecture choices) that treats EXP-A as
   "5 runs" is silently weighting one run-level pattern twice. Either
   drop Run-2 from *validation-signal* computations specifically (while
   still respecting the pinned split's inclusion of it as a sample) or
   explicitly downweight it — and flag this duplication upstream (e.g. to
   whoever owns `docs/planning/PROJECT_STATE.md`) so the "unverified"
   qualifier on the existing warning can be resolved with this evidence.
4. **Investigate EXP-F/run-4 specifically before treating it as generic
   noise.** It is the clear residual outlier (abs_error 2.40, more than
   double the next-worst) and the model's most under-predicted point.
   Worth a targeted look at that run's raw vibration data (e.g., does it
   have unusual operating conditions, a sensor issue, or a genuinely
   different damage trajectory the pseudo-label heuristic scores
   differently than its neighbors?) before generalizing any per-run
   conclusion from this dataset.
5. **A larger N is the highest-leverage fix available, and nothing here
   substitutes for it.** Every correlation and ablation ranking in this
   report is explicitly flagged as suggestive-only because N=7/5/8 gives
   almost no statistical power. If more runs, more experiments, or a
   genuinely independent validation set become available, re-running this
   exact pipeline (already written, deterministic under a fixed seed, and
   fast — 7.5 seconds per training run) is the most direct way to test
   whether today's rankings hold up.

## What's in this folder

- `PLAN.md`, `CHECKPOINT.md` — running phase-by-phase plan and log with
  full reasoning (nothing in this report is not traceable there).
- `reader.py`, `features.py`, `build_features.py` — from-scratch,
  read-only HF archive discovery, spectral feature extraction (Welch PSD
  + log-band binning + broadband stats), and the orchestration CLI that
  processed all 7,124 members / 20 runs (117.5 min, one member in memory
  at a time, disk stable at 74.3 GB free throughout).
- `features/` — per-run parquet feature tables (7,123 minute-rows, 72
  features, 8.2 MB total), `build_log.jsonl` (per-member audit trail),
  `data_summary_per_run.csv`.
- `model.py` — from-scratch channel-independent PatchTST (23,905
  parameters), unit-tested on synthetic data before real training.
- `train.py` — training loop, constant-baseline recomputation, EXP-F
  single-pass evaluation; `training_output/` holds the trained checkpoint,
  training curve, and comparison table.
- `analysis/ablation.py`, `analysis/residuals.py` — Phase 4 scripts and
  their `ablation_output/` / `residuals_output/` results.

Nothing here was committed or pushed; everything is left in the working
tree for review. `gtc-data-experiment/` and `data/Full Dataset/` were
never written to — every archive access went through
`reader.materialize_member`, which streams into a temporary file deleted
immediately after each member's features were extracted.
