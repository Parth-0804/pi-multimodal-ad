# Overnight run — 2026-09-12

Autonomous session. Phases 0–3 of the stage-1 brief all ran to completion.

---

## 1. Summary

Set out to repair the protocol-confounded per-tooth label, implement and score
the organizer's actual metric, and train the first fusion model under a
pre-registration. All three ran.

Two results matter, and both are negative in the useful sense:

**The monotonic-MSE re-scoring appeared to reverse the headline result, and
does not survive a null.** PatchTST's monotonic-MSE on EXP-F beats the
constant's (0.4711 vs 0.5943) where its raw MAE loses (0.8314 vs 0.6797). But
the transform is fitted in-sample on 8 points, and a constant is the one
predictor that provably cannot exploit that. Calibrated against noise: **pure
noise beats the constant 87% of the time, and matches or beats PatchTST's
score 48% of the time** (permutation p ≈ 0.48). The reversal is an artefact of
the metric at this sample size, not a finding. Had this been reported without
the null it would have been a false headline.

**The fusion model did not beat the constant.** `fused_all_three` won selection
on EXP-A, and its single EXP-F evaluation gave MAE 0.6548 against the v3
constant's 0.7348 — a 0.0800 pp advantage, below the 0.15 pp threshold declared
in advance, with a paired-bootstrap 95% CI of [−0.548, +0.414] spanning zero.
Reported as not distinguishable from the constant.

The label repair itself worked and its stated prediction held.

---

## 2. Phase by phase

### Phase 0 — preflight: PASS (6/6)

| Check | Result |
|---|---|
| 0.1 pull / clean tree | `e6db986`; tree cleaned by stashing an in-place edit (see §3) |
| 0.2 imports | torch 2.13.0+cu130, pandas 2.3.3, numpy 2.4.6, scipy 1.18.0, sklearn 1.7.2 |
| 0.3 pinned source runs | all 7 artifacts across 4 runs present |
| 0.4 image_target tables | both present |
| 0.5 unit tests | 114 passed, 0 failed |
| **0.6 baseline reproduction** | **MAE 0.8314187490377436 — exact match, PASS** |

### Phase 1 — target repair: COMPLETE

`phm2026_image_damage_v3` implemented as a *new* definition; v2 left intact and
reproducible. The definition is now options-driven
(`target_definition_version`, `view_selection`, `excluded_tooth_ids` on
`ImageDamageOptions`) rather than a module constant, with defaults reproducing
committed v2 behaviour exactly.

- Derivation run: `runs/phm2026_image_target/20260912T052857044116Z-c936a4e3`
- Sensor rebuild: `runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee`
- 480 per-tooth records = 20 runs × 24 teeth; 20 run targets

**Stated prediction: HELD.** EXP-A's gap to EXP-F falls from **+0.80 → +0.378**.

| | max (v2) | median | one-view, 28 teeth | **v3 (drop 1–4)** |
|---|---|---|---|---|
| EXP-A gap | +0.92 | +0.42 | +0.80 | **+0.378** |
| EXP-B gap | +0.10 | −0.37 | −0.03 | **−0.375** |

Note the trade: dropping teeth 1–4 fixes EXP-A and *worsens* EXP-B (−0.03 →
−0.375), landing v3 almost exactly on the median-aggregation numbers. The
justification for v3 is not the gap — it is that v3 is the only rule under
which no tooth is measured by a protocol no other tooth gets. Selecting an
aggregation rule by gap-to-EXP-F would be tuning against the test set.

Target scale under v3: EXP-A 5.231 ± 1.009, EXP-B 4.478 ± 1.066,
EXP-F 4.853 ± 0.824. **EXP-F is bit-identical to v2** (0 of 8 runs changed),
as predicted, since teeth 1–4 never reached its top-3.

Teeth 1–4 share of top-3 before being dropped: **EXP-A 0.533, EXP-B 0.333**
against a 0.143 base rate (v2/max); 0.40 / 0.286 under one-view. EXP-F: 0.000.

Profile-head constants refit at 24 teeth, train split (EXP-B) only:

```
profile_init_base     0.7944511591465376
profile_target_mean   2.365311342852689
profile_target_scale  1.3065097003604282
profile_init_steps    23 values, min 0.0359, max 0.9950
```

### Phase 2 — the organizer's metric: COMPLETE

`evaluation/monotonic.py` + 7 unit tests, including the degenerate constant
case (labelled, not NaN). Rescoring run:
`runs/phm2026_monotonic_rescoring/20260912T053108724500Z-c0b86e16`.

Then the null calibration described in §1, made reproducible as
`scripts/results/monotonic_null_test.py`.

### Phase 3 — first fusion model: COMPLETE

Pre-registration written and committed **before any training**
(`docs/thesis/PREREGISTRATION_20260912T053329Z.md`, commit `8c4ae31`, which
contains no results). Eight variants, identical budget, seed 20260814,
trained on EXP-B, selected on EXP-A raw MAE alone.

Run: `runs/phm2026_fusion_latefusion/20260912T054016807597Z-e1911d4f`

---

## 3. Failures and how they were handled

| # | What broke | Diagnosis | Action | Status |
|---|---|---|---|---|
| 1 | `git push` rejected: `could not read Username` | No credential helper, no SSH key, no token env var; read-only remote works | Checked all three auth paths. Cannot invent credentials | **OPEN — needs you** |
| 2 | `rescore_monotonic.py` crashed: `RunContext has no attribute relative_directory` | Used a `PinnedRun` attribute on a `RunContext`; the correct one is `run_directory`. Crash was *after* `finalize_run`, so the run was complete | Fixed the attribute, re-ran for a clean provenance record | Resolved |
| 3 | `test_single_group_model_only_sees_its_own_channels` failed | Hypothesis: my *test* was wrong, not the model — no `.eval()`, so dropout made two passes differ. Supported by the padding test, which does call `.eval()`, passing | Added `.eval()`/`no_grad`; assertion kept strict at atol 1e-6 and passes | Resolved — model was correct |
| 4 | Fusion run written to `runs/phm2026_patchtst_baseline/` | Copied the baseline config and never changed `study`/`output_root` | Fixed config, re-ran (deterministic, identical numbers) | Resolved |

Nothing was worked around by loosening an assertion or regenerating a pinned
artifact.

**Failure 1 detail (blocks delivery, not results):** everything is committed
locally — 4 commits, `2460243`, `ab8de3d`, `8c4ae31`, `2425b22`, on `main` at
`e6db986`. A single `git push origin main` ships the night.

---

## 4. Results

Two constants appear below and **must not be compared across target
versions**: 0.6797 is v2's, 0.7348 is v3's.

### The one EXP-F evaluation (pre-declared, performed once)

| Variant | Split | MAE | monotonic-MSE | n |
|---|---|---|---|---|
| constant (train mean), **v3** | test | **0.7348** | 0.5943 | 8 |
| **`fused_all_three`** ← the single EXP-F evaluation | **test** | **0.6548** | 0.3824 | 8 |

Delta vs constant: **−0.0800 pp**. Pre-registered threshold 0.15 pp → **not
distinguishable from the constant.** Paired bootstrap 95% CI [−0.548, +0.414],
P(model better) = 0.617. The monotonic-MSE column carries the §1 null: at n=8
noise beats the constant 87% of the time, so it is not evidence either.

Per-run absolute errors show the two fail on *different* runs rather than one
dominating — model `[1.43, 0.17, 1.42, 0.91, 0.92, 0.20, 0.06, 0.12]`,
constant `[0.56, 0.22, 0.64, 0.23, 1.70, 1.01, 0.75, 0.75]`.

### All eight variants — validation only (EXP-A, n=5)

| # | Variant | val MAE | val mono-MSE | val Spearman |
|---|---|---|---|---|
| 4 | **`fused_all_three`** ← selected | **0.7577** | 0.6977 | −0.154 |
| 1 | `solo_process_context` | 0.8031 | 0.1170 | +0.564 |
| 2 | `solo_organiser_rms` | 0.8466 | 0.0365 | +0.667 |
| 8 | `loo_drop_condition_indicators` | 0.9700 | 0.0271 | +0.975 |
| 5 | `single_encoder_all_9ch` (baseline arch) | 0.9710 | 0.7513 | −0.667 |
| 6 | `loo_drop_process_context` | 1.0058 | 0.7513 | −0.667 |
| 3 | `solo_condition_indicators` | 1.0974 | 0.8151 | −0.872 |
| 7 | `loo_drop_organiser_rms` | 1.0254 | 0.7513 | −0.667 |

No variant diverged; all eight trained. Fusion did beat the single-encoder
baseline on validation (0.7577 vs 0.9710) — but at n=5 validation runs, treat
that as weak.

### Reference: v2 canonical PatchTST, re-scored (Phase 2)

| Model | Split | MAE | monotonic-MSE | n |
|---|---|---|---|---|
| constant (train mean/median), **v2** | test | **0.6797** | 0.5943 | 8 |
| PatchTST | test | 0.8314 | 0.4711 | 8 |
| Ridge | test | 5.0151 | 0.4572 | 8 |

---

## 5. Did the Phase 1 prediction hold?

**Yes.** EXP-A's gap to EXP-F fell from +0.80 to **+0.378**, well below +0.80.
The reasoning behind dropping teeth 1–4 is not falsified by this check.

Two honest caveats on the diagnostics:

- Block 2 ("teeth 1–4 share of top-3 = 0.000 everywhere") is **tautological**
  under v3 — those teeth no longer exist in the target. It is not evidence.
- Block 3 reports 2 remaining "multi-view" teeth in EXP-A with +2.088 pp
  inflation. Investigated: these are EXP-A run 5 teeth 16 and 24, which have
  duplicate *canonical* photos (2 and 3 of them). The target value is still
  taken from a single selected view; `view_count` merely records how many
  existed. n=2, and not view-count leakage.

**A real limitation found while investigating that:** canonical photos carry no
`timestamp_text` (only close-ups do), so for those duplicate-canonical teeth
the "earliest by timestamp" tie-break falls through to `image_id` — a content
hash. That is deterministic and reproducible, but arbitrary rather than
principled, and it matters: tooth 24's three candidates span 5.84–6.84 pp.
Affects 2 of 480 records (0.4%), both in EXP-A run 5.

---

## 6. What I would do next, and why

1. **Push.** One command; the night is otherwise stranded locally.
2. **Decide the duplicate-canonical tie-break** (§5). 0.4% of records, but
   currently resolved by hash. A stated rule — lowest value, or mean of
   duplicates — is defensible; a hash is not.
3. **Do not chase the fusion result.** It is inside the noise band declared in
   advance, and the honest reading is that N=7 training runs is the binding
   constraint, not representation. This is Gate D's "No" branch, which points
   at Stage 4 (per-tooth supervision, the 28× lever) as the only stage that
   attacks sample size.
4. **Stage 4a is already answered** and should be written into the roadmap
   rather than re-run: the encoder channel exists (`Vibration/Encoder`,
   102,400 Hz, absolute degrees 0–360, 24.0 s of waveform per file ≈ 88
   revolutions ≈ 222 RPM), and there is no separate keyphasor. That puts
   Gate E at "encoder usable, no keyphasor" → path 4b, rotation-invariant.

> **CORRECTION (added 2026-09-12, after the report was first written).**
> This section originally claimed `T2_2_CHECKPOINT.md`'s "file count × 60
> seconds" run-duration arithmetic was wrong by 2.5×. **That claim was wrong
> and is withdrawn.** It conflated two different quantities.
>
> Checked against `sensor_run_sequences.parquet` timestamps: `median_cadence_
> seconds` is **60.0 for all 20 runs**, and full runs span ~22,165 s ≈ **6.16 h**.
> Files are captured **one per minute**, and runs really are ~6 hours, so the
> checkpoint's arithmetic and the challenge's "~6-hour run" cadence are both
> correct.
>
> What is true is narrower: each file *contains* **24.0 s of waveform**
> (2,457,600 samples ÷ 102,400 Hz), not 60 s. So acquisition is duty-cycled —
> 24 s of signal recorded per 60 s of wall clock, ~40%. Elapsed run duration is
> file count × 60 s; available *signal* is file count × 24 s. The distinction
> matters for signal-derived quantities (revolutions per file, TSA averages),
> not for run duration.
5. **Treat in-sample monotonic-MSE as unusable at this n** until it is
   cross-fitted. The metric of record cannot currently discriminate anything.

---

## 7. What I deliberately did not do

- **Did not push** — no credentials exist and inventing them is not mine to do.
- **Did not touch EXP-F except once**, for `fused_all_three`, after selection
  was final. `train_variant` is never passed the test sequences, so no code
  path can score EXP-F during training or selection.
- **Did not delete or move** the misplaced fusion run under
  `phm2026_patchtst_baseline/`, or the partial rescoring run from failure 2.
  Both remain; both are superseded by the re-runs named above.
- **Did not commit** the stashed in-place edit (still at `stash@{0}`) or any
  `experimental_edits_*.patch`.
- **Did not re-run** the eight variants after seeing the test number, add a
  variant, or reframe the 0.08 pp advantage as a win.
- **Did not re-litigate** the decision to drop teeth 1–4; Phase 1 was run as
  specified and the prediction was used as falsification, not selection.
- **Did not start Stages 4–6.** They need their own pre-registration.
