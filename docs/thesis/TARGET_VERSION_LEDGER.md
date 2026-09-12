# Target-version ledger

2026-09-12. Verification only — no target definition, config or code was
changed to produce this, and no target run was regenerated. Every number below
was recomputed from the artifact cited, by
`scripts/results/verify_target_constants.py`.

---

## 1. CURRENT VERSION

> **`phm2026_image_damage_v3` — artifact
> `runs/phm2026_image_target/20260912T052857044116Z-c936a4e3`, 24 teeth (5–28),
> one deterministic view per tooth. All new work uses this and nothing else.**

---

## 2. Versions that have existed

| Label | Artifact | Git | Across-views rule | Across-teeth | Teeth | Rows | Status |
|---|---|---|---|---|---|---|---|
| **v1** | `runs/_superseded/phm2026_image_target/20260814T011051111606Z-e7600a8a` | `d3ce4808` **dirty** | `maximum_candidate_ratio` | top-3 mean | 1–28 (**28**) | 560 | superseded by v2 same day; archived |
| **v2** | `runs/phm2026_image_target/20260814T012054997053Z-e195f6d9` | `d3ce4808` **dirty** | `maximum_candidate_ratio` | top-3 mean | 1–28 (**28**) | 560 | superseded by v3 |
| **median-28** | **REFERENCED-BUT-MISSING — no artifact exists** | code state `8a9ac7a` | `median_candidate_ratio` | top-3 mean | 1–28 (**28**) | n/a | never materialised |
| **v3** | `runs/phm2026_image_target/20260912T052857044116Z-c936a4e3` | `2460243` clean | `single_deterministic_view` | top-3 mean | 5–28 (**24**) | 480 | **CURRENT** |

Image types included: v1/v2 aggregate **both** `canonical_tooth` and
`camera_sequence` across views. v3 selects **one** view — `canonical_tooth`
where one exists, else the earliest `camera_sequence` by embedded timestamp.

**The median-28 version has no run directory.** Commit `8a9ac7a` ("updates")
changed the aggregation from `max(values)` to `np.median(values)` but left
`TARGET_DEFINITION_VERSION = "phm2026_image_damage_v2"` unchanged, and no
derivation was ever run from that code state. So the label **"v2" names two
different computations**: `max` (the artifact) and `median` (the code between
`8a9ac7a` and `2460243`). Every median-28 number in circulation came from
in-memory scratch computation, not an artifact.

**v1 → v2 changed the measurement geometry, not just the aggregation.** From
the two `config/resolved_config.yaml` files: `residual_z_threshold` 2.2 → 2.0
and the ROI narrowed vertically from 0.08–0.72 to 0.12–0.50. A smaller ROI
denominator plus a looser threshold is why v1's targets sit near 0.75–1.33 pp
and v2's near 4.85–5.77 pp — a ~6× scale change. **v1 and v2 numbers are not
comparable on any axis.**

## 3. Constants, recomputed from the artifacts

Fixed split = train EXP-B, evaluate EXP-F. LOEO folds = predict EXP-A←train
EXP-F, predict EXP-B←train EXP-F, predict EXP-F←train EXP-B (matching
`scripts/results/loeo_evaluation.py`).

Run-level target cross-checked against each run's own
`run_damage_targets.parquet`: **max |diff| = 0.0000000000** for all three
artifacts.

| Version | EXP-A mean | EXP-B mean | EXP-F mean | scalar const. | **run MAE, EXP-F** | profile len | **tooth MAE, EXP-F** | **LOEO run MAE** | LOEO clustered CI |
|---|---|---|---|---|---|---|---|---|---|
| v1 | 0.8449 | 0.7486 | 1.3332 | 0.7486 | **0.5866** | 28 | **0.3039** (n=224) | **0.5613** | [0.4380, 0.6926] |
| v2 | 5.7722 | 4.9479 | 4.8527 | 4.9479 | **0.6797** | 28 | **0.5263** (n=224) | **0.8953** | [0.6525, 1.1467] |
| median-28 *(no artifact)* | 5.2679 | 4.4779 | 4.8527 | 4.4779 | **0.7348** | 28 | **0.6557** (n=224) | not computed | — |
| **v3 (current)** | 5.2307 | 4.4779 | 4.8527 | 4.4779 | **0.7348** | 24 | **0.6901** (n=192) | **0.8042** | [0.5784, 1.0364] |

Two structural facts that matter for reading this table:

- **The profile constant is a mean of ORDER STATISTICS, not a positional
  mean.** `build_profiles` calls `np.sort` on each run's teeth *before*
  averaging, so entry *k* is "mean *k*-th smallest tooth value across training
  runs", not "mean of tooth *k*". Tooth identity is discarded. Verified in
  `scripts/targets/analyze_tooth_profiles.py`.
- **The profile constant's run-level top-3 MAE is identical to the scalar
  constant's**, for every version (0.5866 / 0.6797 / 0.7348 / 0.7348), by
  linearity of the mean. Verified numerically per version. So "scalar constant"
  and "profile constant read at run level" are the *same number* and cannot
  explain any discrepancy between them.
- v3 drops teeth 1–4 in all three experiments: 480 tooth/run combinations
  instead of 560 (20 runs × 24). EXP-F's run target is bit-identical to v2's
  because teeth 1–4 never reached its top-3.

## 4. The 0.6797 / 0.7348 discrepancy — RESOLVED

**Both numbers are correct. They are the same quantity — fixed-split
(train EXP-B) run-level constant MAE on EXP-F — computed under different target
versions.** Neither is stale, and neither is a scalar-vs-profile confusion.

| Number | Version | Teeth | Split | Level | Artifact |
|---|---|---|---|---|---|
| **0.6797** | v2 (`max`) | 28 | train EXP-B → EXP-F | run | `.../20260814T012054997053Z-e195f6d9/tables/per_tooth_damage.parquet` |
| **0.7348** | v3 (`single_deterministic_view`) | 24 | train EXP-B → EXP-F | run | `.../20260912T052857044116Z-c936a4e3/tables/per_tooth_damage.parquet` |

Tested and rejected as explanations: different split or fold (both fixed
split); scalar vs profile constant (proven identical above); train-mean vs
train-median (under v2 *both* give 0.6797 — which is why the old
`model_comparison` table showed identical mean and median rows); stale prose.

**The second record is also right, and that is the actual source of confusion.**
0.7348 is *simultaneously* the median-28 constant and the v3 constant, because
EXP-B's top-3 is unchanged by whether teeth 1–4 are median-aggregated or
dropped — they never reach EXP-B's top-3 either way. Recomputed in memory from
v2's `image_manifest.parquet` at the `8a9ac7a` code state: median-28 gives
EXP-B mean **4.4779** and EXP-F run MAE **0.7348**, matching v3 exactly.

So: "0.6797 v2 vs 0.7348 v3" and "0.7348 is the median-corrected 28-tooth
run-level constant" are both true statements about the same value. The
description that is *not* safe is treating 0.7348 as a 28-tooth number when
quoting it beside v3 per-tooth figures, since the tooth-level constants differ
(0.6557 at 28 teeth vs 0.6901 at 24).

## 5. Audit of every reported number

### UNTRACEABLE — read these first

| Number | Where quoted | Why untraceable |
|---|---|---|
| **1.011** | `PROJECT_STATE.md`, `FUSION_ROADMAP.md`, `P4_PATCHTST_BASELINE_CHECKPOINT.md` | The August PatchTST run at `d3ce4808` with `git.dirty: true`; the working-tree diff was never recorded and the device differed (`cuda:0`). The code state that produced it no longer exists. Cannot be reproduced or assigned a verified version. **Retire as a citable number.** |
| **0.656** | `R4_RTDETR_MULTITASK_CHECKPOINT.md` | There it is the fragment `0.656733–0.838133` (part of a range), which is **unrelated** to the 0.6557 tooth-level constant that "0.656" denotes elsewhere. One string, two unrelated meanings. |
| **1.220** | `PROFILE_DIAGNOSTICS.json` (as a substring only — no value within 5e-4 exists in that file) | Also equals the tutorial ablation `all_72_features` MAE 1.2202835 in `tutorials/patchtst_freq_baseline/analysis/ablation_output/ablation_comparison.csv`. Provenance as quoted is ambiguous. |
| **0.733** | `HANDOFF.md`, `FUSION_RESULTS_*.md` | Two distinct quantities collide: R4's **image-level** MAE under v2, and the teacher's **tooth-level** MAE against median-28 truth. Numerically near-identical because EXP-F has one canonical photo per tooth, so image-level and tooth-level coincide there. Must always be qualified by level. |

### Assigned

| Number | Where quoted | Version | Teeth | Split | Level | Reuse? |
|---|---|---|---|---|---|---|
| 0.680 / 0.6797 | `HANDOFF.md`, `FUSION_ROADMAP.md`, `PROJECT_STATE.md`, `OVERNIGHT_*` | v2 | 28 | fixed | run | **RETIRED** (v2 superseded) |
| 0.7348 | `OVERNIGHT_*`, §4 above | v3 (= median-28) | 24 (also 28) | fixed | run | **SAFE** for v3 fixed-split only |
| 0.6557 | not in `docs/`; conversation only | median-28 | 28 | fixed | tooth | **RETIRED** — version has no artifact |
| 0.632 | `FUSION_RESULTS_*` (already marked retired) | median-28 | 28 | fixed | tooth | **RETIRED** |
| 0.730 | not in `docs/`; `ablation_comparison.csv` | v2 | 28 | fixed | run | **RETIRED** |
| 0.7426 | not in `docs/`; conversation only | median-28 | 28 | fixed | run | **RETIRED** |
| **0.8042** | `FUSION_RESULTS_*` | **v3** | 24 | **LOEO** | run | **SAFE** — current reference constant |
| **0.8238** | `FUSION_RESULTS_*` | **v3** | 24 | **LOEO** | run | **SAFE** (fusion) |
| **0.9415** | `FUSION_RESULTS_*` | **v3** | 24 | **LOEO** | run | **SAFE** (PatchTST) |
| 0.8314 | `HANDOFF.md`, `FUSION_ROADMAP.md`, `OVERNIGHT_*` | v2 | 28 | fixed | run | **RETIRED** for v3 comparison; valid only as a v2-internal number |
| 1.020 | `R4_*`/`R3_RTDETR_CHECKPOINT.md`, `T2_3_CHECKPOINT.md` | v2 | 28 | fixed | **image** | **RETIRED**; note it is an *image-level* constant, not run-level |
| 1.627 | `R4_RTDETR_MULTITASK_CHECKPOINT.md`, `HANDOFF.md` | v2 | 28 | fixed | run | **RETIRED** |
| 0.894 | `R3_RTDETR_CHECKPOINT.md`, `HANDOFF.md` | v2 | 28 | fixed | image | **RETIRED** |
| 0.796 | `PROFILE_DIAGNOSTICS_V3.json` (substring only) | v3 manifest | — | n/a | **label noise** | **SAFE** but not a model result: within-tooth measurement std from repeat photographs |

## 6. Do not mix

- **Never place a v1 number beside a v2/v3 number.** v1 changed ROI and
  threshold; its scale is ~6× different.
- **Never place a 28-tooth per-tooth figure beside a v3 per-tooth figure.**
  The tooth-level constant is 0.6557 at 28 teeth and 0.6901 at 24.
- **Never compare a fixed-split number to a LOEO number.** v3's constant is
  0.7348 fixed-split and 0.8042 under LOEO — the same constant, different
  protocol.
- **Never compare across levels.** run-level, tooth-level and image-level MAE
  are different quantities even in identical units. 1.020 is image-level;
  0.7348 is run-level.
- **The only mutually comparable set for new work** is the v3 LOEO run-level
  column: constant 0.8042, fusion 0.8238, PatchTST 0.9415, with clustered CIs.
- Context for all of it: the label's own repeatability is **0.796 pp**
  (within-tooth std across repeat photographs), which is the same size as the
  best model's entire MAE. Differences below ~0.8 pp are inside label noise.

## 7. Assumptions I had to make

1. **LOEO fold definition** was not specified in this task; I used the folds
   already committed in `loeo_evaluation.py` (larger remaining experiment
   trains) so the numbers match the existing results table.
2. **Run-level aggregation recomputed from `per_tooth_damage.parquet`** rather
   than read from `run_damage_targets.parquet`, so every version is computed
   identically. The two agree to 1e-10 on all three artifacts (§3).
3. **median-28 was recomputed in memory** from v2's `image_manifest.parquet` at
   the `8a9ac7a` aggregation rule, purely to resolve §4. Nothing was written
   and no run was created; it remains REFERENCED-BUT-MISSING.
4. **LOEO for median-28 not computed** — a version with no artifact did not
   warrant extending the in-memory reconstruction further. Marked "not
   computed", not UNKNOWN.
5. `v1`/`v2`/`median-28`/`v3` are my labels for this ledger; only
   `phm2026_image_damage_v1/v2/v3` appear in artifacts, and median-28 has no
   label of its own because it reused the v2 string.
