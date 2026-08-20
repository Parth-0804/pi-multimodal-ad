# patchtst_freq_baseline — plan

Everything below is new code written for this tutorial. The single reuse
exception (per the task) is reading two pinned parquet outputs as data:
`runs/phm2026_model_dataset/20260814T013357354377Z-6b068cab/tables/split_manifest.parquet`
(split) and
`runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/tables/run_damage_targets.parquet`
(target `raw_top3_mean_pct`, secondary `causal_monotonic_top3_mean_pct`) —
both confirmed present and complete for all 20 runs in Phase 0.

## Windowing / spectral-binning strategy

**Granularity choice: one feature row per ~1-minute HF member, matching
the LF baseline's own per-minute granularity exactly.** This is a
deliberate choice for a controlled comparison — it changes *only* the
feature content (real spectral information vs. LF's time-domain summary
stats), while holding sequence length, patch structure, and downstream
architecture directly comparable. It also keeps per-run sequence length in
the same 73-528 range Phase 0 already confirmed for both modalities, which
is a length PatchTST-style patching handles comfortably.

Per member (per `Vibration/Accel 1` and `Vibration/Accel 2`, each a
variable-length 1-D float32 array at exactly 102,400 Hz, per Phase 0):

1. **Welch power spectral density** (`scipy.signal.welch` — a standard
   library spectral-estimation routine, not repo code): Hann window,
   `nperseg=8192` (≈80ms, frequency resolution ≈12.5 Hz — fine enough to
   resolve shaft/gear-mesh-scale fundamentals well under 1 kHz while still
   reaching the full 51,200 Hz Nyquist band relevant to the 102.4 kHz
   sample rate), 50% overlap. For a full 60s member this averages over
   ≈1,500 overlapping segments per channel — a smooth, low-variance PSD
   estimate, computed member-by-member so peak memory is one member's
   ≈49MB two-channel float32 array plus its PSD output, never a whole run.
2. **Log-spaced band-energy binning** (the "spectral-binning" decision):
   32 log-spaced band edges from 20 Hz to 51,200 Hz
   (`np.logspace(log10(20), log10(51200), 33)`). Log spacing is the
   standard choice for vibration spectra spanning decades of frequency
   (shaft-rate fundamentals at tens of Hz vs. high-frequency
   resonance/impulsive content near Nyquist) — linear bins would waste
   almost all resolution on the top octave. Each band's feature is
   `log1p(sum of PSD power within the band)` — log-compressed for the same
   reason audio log-mel features are log-compressed: gear vibration energy
   is heavy-tailed and dominated by a few peaks otherwise.
3. **Three broadband time-domain stats per channel**: RMS, crest factor
   (peak-abs / RMS), and spectral centroid (Hz) — classic, cheap-to-justify
   scalar vibration-health summaries that complement the band-energy
   vector without duplicating the LF baseline's own five `Context/`
   channels (never read here).
4. **Missingness flags**: 1 binary flag per channel, set if that channel
   failed to read/decode for a given member (expected to be rare — Phase 0
   found `Vibration` present in every member checked — but handled, not
   assumed away, exactly as the LF baseline's own missingness mask does
   independently for its channels).

Per-minute feature vector: `(32 bands + 3 stats) × 2 channels + 2
missingness flags = 72` — the same dimensionality as the existing LF
baseline's 72 inputs. That match is a convenient side effect of
independently-justified choices (32 bands and 3 stats are both chosen on
their own merits above), not a target; it is noted here only because it
makes the eventual comparison table read cleanly (same input width, same
architecture hyperparameters below, only feature semantics differ).

Timestamp handling mirrors the LF pipeline's *principle*, reimplemented
independently: chronology comes from each member's own `Vibration/Accel 1`
`wf_start_time` attribute (parsed only when it carries an explicit `Z` UTC
suffix — matching Phase 0's confirmed format), never ZIP order or the
internal `Dyno Gear...RunN_NNNNN` filename token (Phase 0 found that token
can disagree with the outer archive's run directory). A member with an
unparseable/missing timestamp is recorded with an explicit exclusion
reason and dropped from its run's sequence, not silently coerced.

## From-scratch PatchTST design

Plain PyTorch, `tutorials/patchtst_freq_baseline/model.py`, structurally
following the published PatchTST (Nie et al. 2023) channel-independence
idea — treat each of the 72 input features as an independent univariate
series, patch it, embed it, and run it through one **shared** encoder
across channels — because that channel-independent patching is the
architecture's actual defining idea, not an implementation detail specific
to this repo's existing `patchtst.py`. No import from that file; every
layer is redefined here.

- Input per run: `T × 72` (T = valid minute-rows for that run, 73-528),
  right-padded to the batch's max T with a boolean time mask.
- Training-only normalization: median-impute + standardize each of the 72
  features using statistics fit on EXP-B only, persisted to
  `reports/feature_normalizer.json` for transparency (mirrors the LF
  baseline's train-only-fit *principle*; independently implemented here).
- Patching: length 16 minutes, stride 8 — chosen to match the LF
  baseline's own patch geometry, again deliberately, so a difference in
  the final comparison table cannot be attributed to a patching-geometry
  difference. `B × 72 × N × 16` after patching.
- Per-channel (per-feature) linear projection to `d_model=32`.
- 2 channel-independent (shared-weight) Transformer encoder layers, 4
  heads, feed-forward width 64, dropout 0.1 — a comparable-scale encoder
  to the LF baseline's, not copied from it (own module definitions).
- Mask-aware mean pooling over valid patches → `B × 72 × 32` → flatten/mean
  across the 72 channels → 64-unit MLP → scalar output `B`.
- Loss: Smooth-L1 (Huber) against `raw_top3_mean_pct`. AdamW, lr 1e-3,
  weight decay 1e-4. Validation (EXP-A) early stopping, patience 10 —
  same regularization posture as the LF baseline, independently coded.
- Given only 7 training runs, training uses the full training set as one
  batch per step (no benefit to mini-batching at this scale, and it avoids
  an extra source of padding variability run to run).

## Fair-comparison protocol against the existing LF-only P4 result

- **Same target**: `raw_top3_mean_pct` (primary), read from the exact same
  pinned target run `20260814T012054997053Z-e195f6d9` P4 used.
- **Same split**: the exact same pinned `split_manifest.parquet` (EXP-B
  train / EXP-A validation / EXP-F test, 7/5/8 runs).
- **Same evaluation metrics**: MAE, RMSE, Spearman, R² — reimplemented in
  a few lines with numpy/scipy (`scipy.stats.spearmanr`), not imported from
  `pi_multimodal_ad.evaluation`. Computed once, after EXP-F is unblinded
  exactly once (no retuning against it), same discipline P4 used.
- **Constant baselines recomputed from scratch** on my own read of the
  training target values (mean/median of EXP-B's 7 `raw_top3_mean_pct`
  values) — this doubles as an internal consistency check: if my
  recomputed constants don't land at P4's reported 0.680 pp MAE, that
  signals a target-reading bug to fix before trusting anything else.
- Final comparison table: training mean, training median, existing LF
  PatchTST (cited from `P4_PATCHTST_BASELINE_CHECKPOINT.md`: MAE 1.011),
  this HF/spectral PatchTST — all four rows scored against the identical
  8 EXP-F `raw_top3_mean_pct` values.

## Compute/time budget (sized against Phase 0's measurements)

- **Phase 2 (data assembly)**: I/O-bound. Phase 0 measured ≈139 MB/s
  single-stream decompress-and-write for one representative member;
  extrapolated across the full 572.4 GB uncompressed / 380.6 GB compressed
  corpus, that is a **~1-1.5 hour** full pass over all 7,124 members
  across all 20 runs — no sampling/scaling-down, per the task's
  instruction. Per-member Welch PSD compute (≈1,500 overlapping 8192-point
  FFTs) is milliseconds, negligible next to the I/O cost. Disk: only 70GB
  free, but peak temp usage per member stays ≈84MB (materialize → featurize
  → delete), so the full pass is disk-safe; free space will be checked
  before starting and periodically during the run as an explicit gate.
- **Phase 3 (training)**: tiny dataset (7 train runs, ≈100-400K
  parameters), GPU available (confirmed this session) — training to
  convergence/early-stop is a matter of seconds to low minutes, not a
  meaningful cost next to Phase 2.
- **Total realistic wall-clock for Phases 2-5**: on the order of 2-3
  hours, dominated entirely by Phase 2's raw-archive I/O.

## Deliverable shape

- `PLAN.md` (this file), `CHECKPOINT.md` (running log).
- `reader.py` — from-scratch bounded, read-only ZIP+HDF5 member reader
  (own implementation; not `pi_multimodal_ad.profiling.archive_io`).
- `features.py` — Welch PSD + log-band binning + broadband stats.
- `build_features.py` — CLI: walks all 20 runs, writes one parquet per run
  incrementally under `features/`, with a running data-summary log.
- `model.py` — from-scratch PatchTST (patching, channel-independent
  encoder, pooling, head).
- `train.py` — training loop, constant baselines, EXP-F single-pass eval.
- `analysis/` — Phase 4 scripts and outputs.
- `REPORT.md` — Phase 5.

## Next action

Proceed to Phase 2: implement `reader.py` + `features.py` +
`build_features.py`, run the full 20-run pass, report the data summary.
