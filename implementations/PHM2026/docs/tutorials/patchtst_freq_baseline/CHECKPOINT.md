---
Running log for tutorials/patchtst_freq_baseline. Overwritten/appended each
phase. **Update 2026-08-20: the user explicitly said to proceed through all
remaining phases without waiting for responses ("go ahead with all the
planned phases please don't care to wait for my response") — from Phase 1
onward this log documents continuous, non-stopping execution.**
---

# Phase 0 — Discovery

**Status: COMPLETE. Stopping for review before Phase 1, as instructed.**

All exploration below opened raw archive members read-only, one at a time,
via plain `zipfile`/`h5py`; nothing was extracted in place, moved, renamed,
or written into `gtc-data-experiment/`. One temporary scratch file (deleted
immediately after each inspection) was used to give `h5py` a real file
handle, since HDF5 needs a seekable file and can't read out of a live `zipfile`
member stream directly.

## What HF/high-sample-rate members actually exist

`gtc-data-experiment/high_frequency/{EXP A,EXP B,EXP F}/Exp-<X>_HDF5_Run-<n>.zip`
— **20 outer archives, exactly one per run** (EXP-A: 5, EXP-B: 7, EXP-F: 8),
mirroring the LF/CI directory shape but with **no nested inner ZIP** this
time — each outer archive directly contains one HDF5 file per roughly-one-minute
recording segment (confirmed via `zipfile.infolist()`, central directory
only, no payload read). Full inventory (member counts and byte totals from
central-directory metadata, `<300ms` per archive, no decompression):

| experiment | run | members | uncompressed (GB) | compressed (GB) |
|---|---|---|---|---|
| EXP-A | 1 | 372 | 30.97 | 20.81 |
| EXP-A | 2 | 372 | 30.98 | 20.81 |
| EXP-A | 3 | 371 | 31.01 | 20.69 |
| EXP-A | 4 | 341 | 28.59 | 19.03 |
| EXP-A | 5 | 377 | 31.94 | 20.97 |
| EXP-B | 1 | 372 | 30.97 | 20.64 |
| EXP-B | 2 | 372 | 30.99 | 20.70 |
| EXP-B | 3 | 371 | 30.99 | 20.66 |
| EXP-B | 4 | 372 | 31.05 | 20.64 |
| EXP-B | 5 | 371 | 31.01 | 20.67 |
| EXP-B | 6 | 372 | 30.98 | 20.66 |
| EXP-B | 7 | 145 | 12.06 | 7.99 |
| EXP-F | 1 | 373 | 31.04 | 20.60 |
| EXP-F | 2 | 445 | 30.10 | 19.98 |
| EXP-F | 3 | 372 | 31.00 | 20.60 |
| EXP-F | 4 | 528 | 29.02 | 19.19 |
| EXP-F | 5 | 382 | 31.63 | 20.86 |
| EXP-F | 6 | 371 | 31.00 | 20.60 |
| EXP-F | 7 | 73 | 6.01 | 3.94 |
| EXP-F | 8 | 372 | 31.02 | 20.62 |
| **total** | | **7,124** | **572.4** | **380.6** |

7,124 total members matches D1.1/D1.2's figures exactly. Per-run member
counts (73–528) exactly match T2.2/P4's independently-reported LF run
durations ("file count × 60 seconds: 73–528 minutes") — strong evidence HF
and LF share the same one-file-per-minute recording cadence and the same 20
runs, even though the two modalities are stored in structurally different
archive layouts (HF: flat per-run ZIP; LF: nested nested-ZIP-per-run, per
D1.2). Member filenames follow the physical dyno's own naming, e.g.
`Run-1/Dyno Gear303Run1_00005.hdf5` — the embedded "Run1"/"Run2" token can
disagree with the outer Run-N directory (confirmed: EXP-B Run-6's last
member is named `..._Run7_00139.hdf5`, EXP-F Run-2's members are named
`Run9`/`Run10`), exactly the kind of internal/outer run-token mismatch
D1.2 already flagged for LF/CI. **Consequence for Phase 1/2: outer
archive/run-directory membership will be treated as authoritative for
experiment/run identity (never the internal filename token), and file
order will not be treated as time order** — the real per-file `wf_start_time`
attribute must be used for chronology, exactly as the existing LF pipeline
already does, for the same reason.

Internal HDF5 structure (confirmed identical group names across an EXP-A
member, an EXP-F member, and edge-case first/last members of a short run;
one schema variation found — see below):

- **`Vibration/`** — the actual raw high-rate waveform, the group this
  task cares about. Three datasets, `Accel 1`, `Accel 2`, `Encoder`, each
  1-D float32. Confirmed **exactly 102,400 Hz** directly from the source
  attribute `wf_increment = 9.765624999999954e-06` seconds
  (`1/wf_increment = 102,400.0 Hz`, not a rounded/assumed value) — this is
  the real archive member D1.2's "approximately 102,400 Hz" referred to.
  Units come from `unit_string`/`NI_UnitDescription` source attributes, not
  inferred: `Accel 1`/`Accel 2` = **g** (acceleration), `Encoder` =
  **degrees** (shaft encoder angle/position, not a vibration channel — a
  potential order-tracking reference signal, not used for spectral features
  in this baseline; noted as a possible future extension).
- **`Context/`** — the same five channels the LF pipeline already uses
  (`Accel1 RMS`, `Accel2 RMS`, `PAU Speed`, `PAU Torque`, `Temperature`),
  once per second (60 values/minute), same units as documented in
  `P4_PATCHTST_BASELINE_CHECKPOINT.md`. HF archives are a strict superset
  of this LF context info — **not used here**, since duplicating it would
  not test anything new versus the existing LF baseline; the point of this
  task is the `Vibration/` group specifically.
- **`CI/`** (60 values/minute, 1 Hz) and **`CI_4s/`** (15 values/minute, 4 s
  cadence) — **pre-computed** classical vibration health indicators (FM4,
  NA4, M6A, ALR, kurtosis, RMS, crest factor, envelope-order ratio, etc.),
  all explicitly attributed to `acc_channel = "Accel 2"`. These are
  upstream-engineered features, not raw spectral data — **not used here**,
  since building spectral features from the raw waveform ourselves, not
  reading someone else's precomputed indicators, is what "from scratch"
  means for this task. Their presence is recorded for honesty/completeness.
- **`Transforms/`** (60×4096/minute) and **`Transforms_4s/`** (15×4096/minute)
  — pre-computed **time-synchronous-averaged** spectral-domain arrays
  (`TSA`, `difference`, `e_op`, `residual`), order-tracked via the Encoder
  channel. Also pre-computed, also **not used** for the same "from scratch"
  reason — this baseline will compute its own FFT/PSD features directly
  from `Vibration/Accel 1`/`Accel 2`, not reuse this existing product.
- **`DM4500 Data/`** and **`ICM2 Data/`** — oil-debris particle-count bins
  (analogous to LF "Oil" data), 7-8 bins, 1 value/minute each. Out of scope
  (not vibration/spectral); noted but not used.
- **One schema variation found directly**: EXP-F Run-7's last member
  (`Run-7/Dyno Gear309Run7_00072.hdf5`) is **missing the `ICM2 Data` group**
  entirely (present in every other checked member). `Vibration` itself was
  present in every member checked. **Consequence: the Phase 2 reader must
  treat every group except `Vibration` as optional and must not hard-fail
  if a non-Vibration group is absent** — confirmed necessary from a real
  file, not assumed defensively.

## Duration/sample-count reality check — this determines feasibility directly

**Member duration is NOT a fixed 60 seconds.** Checked four members
(EXP-A Run-1 first/mid, EXP-F Run-7 first/last — the short 73-member run):

| member | `Vibration/Accel 1` shape | duration |
|---|---|---|
| EXP-A Run-1, `_00000` (first) | (2,457,600,) | 24.00 s |
| EXP-A Run-1, `_00050` (mid) | (6,144,000,) | 60.00 s |
| EXP-F Run-7, `_00000` (first) | (1,459,200,) | 14.25 s |
| EXP-F Run-7, `_00072` (last) | (3,584,000,) | 35.00 s |

Interior members are consistently the full 60s / 6,144,000 samples; first
and last members of a run are shorter (real recording start/stop
boundaries within a minute). **Consequence: Phase 2's reader must read the
real per-member array length, never assume a fixed 6,144,000-sample block.**

A full 60s member is 6,144,000 samples × 4 bytes × 2 channels (Accel 1 +
Accel 2) ≈ 49 MB of raw float32 in memory if fully loaded for two channels
at once — **one member at a time is entirely feasible in RAM**; it is
*all 7,124 members simultaneously, or a whole run concatenated
(30 GB uncompressed per run)*, that is infeasible and exactly what the
task's hard constraint rules out. One member's on-disk materialized size
(83.7 MB, matching the archive's own uncompressed byte count) took **0.60s
to decompress-and-write to a scratch temp file (≈139 MB/s)** — extrapolating
that measured rate across the full 572.4 GB uncompressed corpus gives a
**rough order-of-magnitude I/O budget of ~1–1.5 hours** for a full read-once
pass over every one of the 7,124 members, before any feature-computation
CPU time on top. This is a real, measured estimate (not a guess) that
Phase 1 will use to size the full-vs-sampled decision explicitly.

**Disk headroom**: only **70 GB free** on the local filesystem right now
(`df -h`: 495G total, 426G used). Since features will be computed one
member at a time with the temp payload deleted immediately after (peak
temp usage ≈84 MB, never accumulating), this is not a blocker for
processing the full corpus — but it does rule out ever caching/extracting
the HF corpus in bulk, which the hard constraints already forbid anyway.

## Cross-check against the pinned split — full coverage, no gaps

Read directly with pandas (as data, not via any loader import):

- Pinned split: `runs/phm2026_model_dataset/20260814T013357354377Z-6b068cab/tables/split_manifest.parquet`
  (T2.2 canonical run, confirmed in `docs/planning/PROJECT_STATE.md` and
  `docs/planning/T2_2_CHECKPOINT.md`). Experiment-level split, confirmed
  from the actual table: **EXP-B → train (7 runs), EXP-A → validation
  (5 runs), EXP-F → test (8 runs)** — 20 runs total, matching P4's own
  split usage exactly.
- Pinned run-level targets: `runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/tables/run_damage_targets.parquet`
  (target run ID confirmed in `docs/planning/P4_PATCHTST_BASELINE_CHECKPOINT.md`).
  **All 20 runs (EXP-A 1-5, EXP-B 1-7, EXP-F 1-8) have a valid,
  `included_provisional` `raw_top3_mean_pct`/`causal_monotonic_top3_mean_pct`
  target with `valid_tooth_count=28` (complete inspection) — zero
  exclusions.** Both columns are the exact same provisional
  `phm2026_image_damage_v2` target the existing LF-only PatchTST baseline
  used, read here purely as data.

Cross-referencing against the HF archive inventory above: **every one of
the 20 pinned-split runs has a corresponding HF archive present, and every
HF archive's run count falls in the same 73-528-member range T2.2/P4
already documented for LF.** No run needs to be dropped or reported as
missing HF coverage — full, honest coverage across train/validation/test.

## What this means for Phase 1

- No structural surprises that block the task: HF data is real, present
  for every pinned-split run, at a confirmed exact 102,400 Hz on two
  acceleration channels in physical units (g), variable-length per member,
  one member ≈ one minute (not fixed-length), 7,124 members / 572.4 GB
  uncompressed / 380.6 GB compressed in total.
- The measured ~139 MB/s single-stream decompression rate makes a
  full-corpus pass a ~1-1.5 hour I/O operation, not a multi-hour or
  multi-day one — this is the concrete number Phase 1 will size the
  windowing/feature/compute plan against, per the task's "don't scale
  down, but justify against what Phase 0 found" instruction.
- `Accel 2` is the channel the pre-existing (unused, for-reference-only)
  `CI`/`CI_4s` indicators were all computed from — worth noting as a
  hint about which channel the original instrumentation treated as
  primary, without over-relying on it; both `Accel 1` and `Accel 2` are
  available and real, so Phase 1 can decide whether to use one or both.

## Next action (superseded — see Phase 1 below; user said proceed without stopping)

Write `tutorials/patchtst_freq_baseline/PLAN.md` (Phase 1): exact
windowing/FFT/spectral-binning strategy sized against the real member
durations and the ~139 MB/s measured I/O rate above, the from-scratch
PatchTST architecture, the fair-comparison protocol against P4's EXP-F
raw-target MAE 1.011 pp / constant baselines 0.680 pp, and a concrete
compute/time budget.

---

# Phase 1 — Plan

**Status: COMPLETE.** Wrote `tutorials/patchtst_freq_baseline/PLAN.md`:

- **Windowing/spectral strategy**: one feature row per ~1-minute HF member
  (matching LF's own granularity, deliberately, for a controlled
  comparison). Per member: Welch PSD (`scipy.signal.welch`, Hann,
  nperseg=8192, 50% overlap) per channel → 32 log-spaced band-energy
  features (20 Hz–51,200 Hz, `log1p`-compressed) + 3 broadband stats (RMS,
  crest factor, spectral centroid) + missingness flag → 36/channel × 2
  channels = 72 features/minute.
- **From-scratch PatchTST**: channel-independent patching (patch_len=16,
  stride=8, matching LF's own geometry deliberately), shared 2-layer
  Transformer encoder (d_model=32, 4 heads, d_ff=64), mask-aware pooling,
  MLP head. Full training set as one batch (only 7 train runs).
- **Fair comparison**: same target (`raw_top3_mean_pct`), same pinned
  split, metrics reimplemented from scratch, constants recomputed from the
  same pinned values as an internal consistency check against P4's cited
  0.680 pp.
- **Budget**: Phase 0's measured ≈139 MB/s throughput → full-corpus pass
  estimated ~1-1.5h I/O-bound; training itself estimated seconds-minutes.

---

# Phase 2 — Data assembly

**Status: COMPLETE.**

## What was built (all new code, no `pi_multimodal_ad` imports)

- `reader.py` — from-scratch archive discovery (`discover_hf_run_archives`)
  + bounded, non-extracting member materialization (`materialize_member`,
  streams via `zipfile.ZipFile.open()` + chunked read/write, never calls
  `.extract()`) + disk-space check helper.
- `features.py` — Welch PSD + log-band binning + broadband stats +
  `parse_wf_start_time` (explicit-UTC-only, mirrors the LF pipeline's
  *principle*, independently written) + `extract_member_features` (per-file
  orchestration, handles missing groups/channels/timestamps explicitly).
- `build_features.py` — CLI: discovers all 20 run archives, processes one
  member at a time (materialize → featurize → delete), writes each run's
  features to its own parquet the moment that run finishes, checks free
  disk space before starting and before every run (20 GiB gate), logs one
  JSON line per member to `features/build_log.jsonl` for full auditability.

## Smoke-tested before the full run

3-members-per-run across all 20 archives (60 members, 53s): 0 exclusions,
correct variable-length handling (confirmed some EXP-F runs pack many
short ~1-second sub-recordings under distinct internal "RunNNN" labels
rather than continuous 60s minutes — handled correctly, `wf_start_time`
threads them into real chronological order regardless of internal naming).

## Full run result

All 7,124 members across all 20 runs, **117.5 minutes wall-clock**
(close to Phase 1's ~1-1.5h estimate), **free disk stable at 74.3 GB
throughout (zero accumulation)** — confirms the one-member-at-a-time
discipline holds under sustained load, not just in the smoke test.

- **7,123 / 7,124 members included** (99.99%). **1 excluded**:
  `EXP-F/run-5/Run-5/Dyno Gear309Run5_00000.hdf5` — reason
  `no_vibration_group` (this one member's HDF5 file has no `Vibration`
  group at all; every other group present). Confirmed via
  `features/build_log.jsonl`, which records every member's outcome, not
  just the excluded ones.
- **Per-split minute-row / run counts**: train (EXP-B) 2,375 rows / 7 runs;
  validation (EXP-A) 1,833 rows / 5 runs; test (EXP-F) 2,915 rows / 8 runs.
  Per-run row counts match the archive's own member counts from Phase 0
  almost exactly (off by at most 1, only for the single excluded member).
- **Feature dimensionality: 72**, confirmed directly from the written
  parquet files (not just the design intent) — zero NaNs anywhere, zero
  missingness flags set (both channels present and readable in all 7,123
  included members) — the "handle missing channels gracefully" code path
  exists but was never actually exercised by this real data, which is
  itself worth recording honestly (defensive code, not proven necessary).
- Total feature output: **8.2 MB** for all 20 runs (vs. 572.4 GB raw) —
  confirms the compression from raw waveform to spectral summary is
  extreme, as expected.

## Important data-quality finding, found independently by this exploration

**EXP-A Run-1 and EXP-A Run-2's entire HF archives are exact duplicates of
each other.** Discovered by comparing feature fingerprints across all
C(20,2)=190 run pairs (`(wf_start_time, accel1_band00_energy)` sets):
**EXP-A_run1 and EXP-A_run2 share 372/372 rows — 100% of both runs** —
verified further by direct row-by-row comparison of all 72 features
(exact floating-point equality, not just close) plus identical internal
member filenames in identical order (149 members carry an internal
"Run1" name token, 223 carry "Run2" — the *same* 149/223 split, in the
*same* order, in *both* outer archives). **No other pair among the 190
overlaps at all** — this is the only duplication in the entire HF corpus.

This directly confirms, with hard evidence, what `docs/planning/PROJECT_STATE.md`
already flagged as an *unverified* concern: *"EXP-A Run 2 stays in scope
with its reported, unverified 311-file overlap warning."* This exploration
independently found the real extent is larger and exact: not a partial
~311-file overlap but a **complete, exact 372/372 duplication** confirmed
via the actual spectral content, not just filenames.

**Consequence, handled per the hard constraints (no split re-derivation)**:
EXP-A Run-2 stays in the validation split exactly as pinned — it is not
excluded or altered. But this is reported prominently because it means:
(a) **no train/test leakage** — the duplication is entirely contained
within the validation split, EXP-F (test) and EXP-B (train) are unaffected
and share zero rows with anything; (b) the validation split's model
selection is effectively driven by **4 independent run-level observations,
not 5** — EXP-A Run-1 and Run-2 will receive near-identical model
predictions by construction, so early-stopping/validation-MAE in Phase 3
should be read with this in mind, and this will be stated plainly in
Phase 4/5 rather than glossed over.

## Next action (superseded — see Phase 3 below)

Proceed to Phase 3: train the from-scratch PatchTST (`train.py`, already
written and unit-tested on synthetic data — 23,905 parameters, verified
forward/backward pass and short-sequence edge case), evaluate once on
EXP-F, recompute constant baselines (already spot-checked by hand against
the real pinned targets: 0.6797 pp, matching P4's cited 0.680 pp).

---

# Phase 3 — Train + evaluate

**Status: COMPLETE.** `ma_thesis_env/bin/python tutorials/patchtst_freq_baseline/train.py`,
default hyperparameters from `PLAN.md` (max_epochs=4000, patience=400,
lr=1e-3, weight_decay=1e-4), GPU (`cuda`, confirmed in
`training_output/environment.json`, PyTorch 2.13.0+cu130). Training time:
**7.5 seconds** (23,905 parameters, tiny 7-run full-batch training).
Early-stopped at epoch 540; **best validation epoch was 140**.

## Headline result — a genuine negative result, reported plainly

| model | MAE (pp) | RMSE | Spearman | R² |
|---|---:|---:|---:|---:|
| Training mean (recomputed here) | 0.6797 | 0.7768 | n/a (constant) | -0.0153 |
| Training median (recomputed here) | 0.6797 | 0.7712 | n/a (constant) | -0.0009 |
| Existing LF-only PatchTST (cited, P4) | 1.011 | 1.243 | -0.262 | -1.601 |
| **This HF/spectral PatchTST** | **1.2203** | **1.3583** | **-0.0238** | **-2.1045** |

**This from-scratch spectral/HF baseline does not beat either constant
baseline, and it is also worse than the existing LF-only baseline it was
built to test against.** MAE 95% bootstrap CI (2,000 resamples over the 8
test runs): [0.846, 1.640] — wide, as expected at N=8, but does not
overlap favorably with the 0.68 constant baselines' performance.

Recomputed constants (0.6797) match P4's cited 0.680 pp almost exactly —
confirms the pinned-target reading is correct and this comparison is
apples-to-apples, not an artifact of reading the wrong target values.

## What the training curve shows (worth carrying into Phase 4)

Validation MAE improved sharply early (epoch 1: 5.55 → epoch 140: **0.52,
the best**), then got markedly *worse* with continued training (epoch 400:
2.31) while training MAE kept monotonically falling (epoch 400: 0.257) —
a textbook small-N overfitting curve. Early stopping correctly reverted to
the epoch-140 weights, but **even that best-validation checkpoint produced
an EXP-F MAE of 1.22, more than double its own best validation MAE of
0.52** — validation performance did not transfer to the test experiment.
Phase 2 already found EXP-A Run-1/Run-2 are exact duplicates within the
5-run validation set; combined with only 4 truly-independent validation
runs and a known EXP-F domain shift (Phase 4 will quantify this
specifically), this is a plausible contributing explanation to carry
forward, not yet a proven one.

## Per-run EXP-F predictions (this run's sole test pass)

| run | y_true | y_pred | abs_error |
|---|---:|---:|---:|
| EXP-F/run-1 | 3.9165 | 5.0171 | 1.1006 |
| EXP-F/run-2 | 4.6982 | 3.6659 | 1.0323 |
| EXP-F/run-3 | 3.8326 | 4.4655 | 0.6329 |
| EXP-F/run-4 | 4.2445 | 1.8428 | 2.4018 |
| EXP-F/run-5 | 6.1746 | 4.3411 | 1.8335 |
| EXP-F/run-6 | 5.4933 | 4.2474 | 1.2459 |
| EXP-F/run-7 | 5.2320 | 6.3445 | 1.1125 |
| EXP-F/run-8 | 5.2295 | 4.8267 | 0.4028 |

Run-4 stands out as the worst prediction by a wide margin (abs_error
2.40, roughly double the next-worst). Phase 4's residual analysis will
look at this concretely rather than treat it as noise.

Fixed one cosmetic issue found while reviewing this output: `compute_metrics`'s
Spearman guard only checked whether `y_true` was constant, not `y_pred`
(scipy correctly returns NaN with a `ConstantInputWarning` for the two
constant-baseline rows, since a constant predictor has undefined rank
correlation — not a bug, just a noisy warning); extended the guard to
check both arrays. Does not change any reported number, both baseline
rows were already the correct NaN.

## Next action (superseded — see Phase 4 below)

Proceed to Phase 4: run `analysis/ablation.py` (band/channel ablation —
already written, calls `train_and_evaluate` directly so it retrains the
real model, not a toy probe) and `analysis/residuals.py` (full 20-run
residual view, run-order/target-magnitude correlations, EXP-F domain-shift
check) — both already written and syntax-checked, ready to run against
the real features now that Phase 2/3 are complete.

---

# Phase 4 — Explain the result

**Status: COMPLETE.**

## Does adding spectral/HF information change the result? Yes — for the worse, and dimensionality is implicated

The full 72-feature model (MAE 1.2203) is not just worse than constants
(0.6797) and worse than the cited LF-only baseline (1.011) — running
`analysis/ablation.py` (which retrains the *actual* PatchTST, not a
separate probe, on column subsets) found **the full-feature model is the
single worst-performing variant of everything tested**:

| variant | n_features | MAE | Spearman |
|---|---:|---:|---:|
| broadband_stats_only (RMS/crest/centroid, no bands) | 8 | 0.7304 | 0.048 |
| low_bands (20-297 Hz) only | 30 | 0.7365 | 0.143 |
| bands_only (no broadband stats) | 66 | 0.7635 | 0.143 |
| mid_bands (297-4,408 Hz) only | 30 | 0.7675 | 0.095 |
| accel1 only | 36 | 0.7788 | **0.405** |
| accel2 only | 36 | 0.8147 | 0.095 |
| high_bands (4,408-51,200 Hz) only | 28 | 0.9969 | **-0.357** |
| **all 72 features (Phase 3's main run)** | **72** | **1.2203** | **-0.024** |

Every reduced-dimensionality variant beats the full model, several by a
wide margin, though **none beats the 0.6797 constant baseline either** —
the honest floor is that no version of this HF/spectral approach clears
the constant baseline at N=7 training runs, but the full-feature model is
worse than its own ablated sub-models, not just worse than the baseline.
This points at **overfitting/curse-of-dimensionality (72 continuous
features fit from 7 training runs) as a real, implicated driver of the
poor headline number** — separate from, and compounding, any question of
whether HF spectral content itself carries damage-predictive information.

## Which bands/channels carry signal, if any?

Weakly suggestive, not decisive (N=7/5/8 — see below): `accel1_only`
reaches the best Spearman correlation of any variant (0.405) despite not
having the lowest MAE, hinting Accel 1 alone carries some rank-order
signal that gets diluted/overwhelmed when combined with Accel 2 and all
bands. **`high_bands_only` (4,408-51,200 Hz) is the worst individual
variant** (MAE 0.997, Spearman **-0.357**, i.e. anti-correlated) —
suggesting the top ~2.5 octaves of the 102.4 kHz-rate spectrum are the
least reliable/most overfitting-prone frequency range in this dataset,
while `low_bands` (20-297 Hz, shaft/gear-mesh-fundamental range) is among
the better-behaved reduced variants. This is consistent with, though does
not prove, a physically plausible story: shaft-rate-scale vibration
content is more stable/interpretable than high-frequency content, which
may be dominated by acquisition noise or resonances unrelated to gear
wear at this sample size.

## Residual analysis (`analysis/residuals.py`, all 20 runs, not just test)

Mean absolute error rises monotonically from **validation (0.524) → train
(0.776) → test (1.220)** (see `residual_analysis.png`, right panel) — the
model performs best exactly on the split that drove its own early
stopping, worse on its own training data (only 140 of 540 epochs were
used, so training wasn't run to convergence), and worst on the genuinely
held-out experiment. This ordering — val error lower than train error —
is itself a symptom worth flagging: it is consistent with (though not
proof of) the model's best checkpoint being selected on a validation
signal that includes the exact-duplicate EXP-A Run-1/Run-2 pair found in
Phase 2 (both runs receive nearly identical predictions by construction,
so 2 of the 5 "validation" data points are not independent evidence of
generalization).

- **Run-order correlation, EXP-F (N=8)**: `corr(run_number, signed_error)
  = -0.105` — negligible. No evidence of a monotonic progressive-wear
  pattern in the residuals (contrast with the RT-DETR image baseline,
  where a similar per-run slice showed a *mild* upward recall trend
  across runs — no comparable trend appears here).
- **Target-magnitude correlation, EXP-F (N=8)**: `corr(y_true, abs_error)
  = 0.136` — also negligible; the model is not simply failing more on
  higher-damage runs specifically.
- **Errors are not concentrated in one or two runs**: `residual_analysis.png`'s
  left panel shows EXP-F residuals scattered both above and below zero
  across all 8 runs, no single outlier run dominating the total error
  budget — except **EXP-F run-4** (abs_error 2.40, more than double the
  next-worst at 1.83), which the predicted-vs-true scatter shows as a
  clear visual outlier (true 4.24, predicted only 1.84 — the model's most
  compressed/lowest prediction on the hardest-to-place point). One run
  standing out from an otherwise unremarkable spread is itself worth
  naming plainly rather than averaging away.
- **Does EXP-F's domain shift show up the way it did in the RT-DETR
  work?** Differently. The RT-DETR image baseline found a *specific,
  measurable, geometric* mechanism (pseudo-box size distribution shift
  driving IoU-based recall to near-zero). Here, the shift shows up only
  as **elevated mean error on the whole EXP-F split relative to train/val**
  (1.220 vs 0.776/0.524) — real, and directionally consistent with a
  domain-shift story, but nothing this analysis measured (run order,
  target magnitude, per-run pattern) explains *why* within EXP-F itself.
  This is an honest limit of what N=8 can support, not a finding that no
  mechanism exists.

## What's statistically supportable vs. suggestive only, made explicit

- **Supportable**: the headline ranking (constants < LF-only PatchTST <
  this HF/spectral PatchTST) is a real, reproducible (fixed-seed,
  internally-consistency-checked-against-P4) empirical fact for this
  specific run configuration. The full-vs-ablated-variant ordering is
  similarly a real, reproducible fact about *this* model and *this* data.
  The complete EXP-A Run-1/Run-2 duplication is a certain, fully-verified
  fact (372/372 exact match), not probabilistic.
- **Suggestive only, not decisive**: every correlation computed above
  (run-order, target-magnitude, band/channel importance) is estimated
  from 7-8 data points. A single bootstrap 95% CI on EXP-F MAE already
  spans [0.85, 1.64] — wider than the gap between any two rows in the
  ablation table. None of the band/channel differences in the ablation
  table should be read as "band X is proven more informative than band Y"
  — only as "in this one N=7 training run, this ordering appeared."
  Re-running with a different seed, a different patch geometry, or (most
  importantly) a genuinely larger N would be needed before treating any
  individual ablation ranking as a stable conclusion.

## Next action (superseded — see Phase 5 below)

Proceed to Phase 5: write `tutorials/patchtst_freq_baseline/REPORT.md`
tying every metric above to its evidence, the comparison to the LF-only
baseline, and concrete next steps that follow specifically from the
overfitting/dimensionality finding, the high-band unreliability finding,
and the EXP-A duplicate-run finding.

---

# Phase 5 — Final report

**Status: COMPLETE.** Wrote `tutorials/patchtst_freq_baseline/REPORT.md`:
headline comparison table, the ablation-driven overfitting finding tied
explicitly to evidence, the band/channel suggestive findings, residual
analysis, the EXP-A Run-1/Run-2 duplication finding and its consequences,
an explicit statistically-supportable-vs-suggestive section, and 5
concrete next steps each citing the specific finding it follows from.

---

# ALL PHASES COMPLETE (0-5)

Nothing was committed or pushed, per instructions. Final deliverable
inventory under `tutorials/patchtst_freq_baseline/`:

- `PLAN.md`, `CHECKPOINT.md` (this file), `REPORT.md`
- `reader.py`, `features.py`, `build_features.py` (Phase 2, from scratch)
- `features/` — 7,123-row feature dataset (20 per-run parquet files,
  `build_log.jsonl`, `run_summary.json`, `data_summary_per_run.csv`)
- `model.py`, `train.py` (Phase 3, from scratch)
- `training_output/` — trained checkpoint, training curve, comparison
  table, per-run predictions, environment/config record
- `analysis/ablation.py`, `analysis/residuals.py` (Phase 4) plus their
  `ablation_output/` and `residuals_output/` result directories

Headline: this HF/spectral PatchTST (MAE 1.220 pp on EXP-F) does not beat
the recomputed constant baselines (0.680 pp) or the cited LF-only baseline
(1.011 pp) — an honest negative result. The most load-bearing findings
behind *why*: (1) the full 72-feature model overfits — every
dimensionality-reduced ablation variant scored better; (2) EXP-A Run-1 and
Run-2's HF archives are an exact, complete duplicate of each other,
independently confirming a previously-unverified concern in
`docs/planning/PROJECT_STATE.md` and reducing validation to 4 effectively
independent runs; (3) no run-order or target-magnitude pattern explains
EXP-F's elevated error, unlike the RT-DETR image baseline's clearer
geometric mechanism — an honest limit of N=8, not a found-and-explained
mechanism. Full detail and evidence for every claim is in `REPORT.md`.
