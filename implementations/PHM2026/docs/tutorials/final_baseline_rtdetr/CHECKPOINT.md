# final_baseline_rtdetr — running checkpoint

This file is overwritten at the end of every phase with a running log, per
the task's instructions. It mirrors AGENTS.md's phase-boundary discipline
even though this tutorial sits outside the governed pipeline.

**Status: ALL PHASES COMPLETE (0, 1, 2, 4, 5; Phase 3 skipped by the Phase 0
decision). Nothing committed or pushed — everything left in the working
tree for review, per instructions.**

---

## Phase 0 — Discovery

### Docs read (in order)

1. `docs/planning/PROJECT_STATE.md`
2. `docs/planning/R4_RTDETR_DETECTION_CHECKPOINT.md`
3. `docs/planning/R4_RTDETR_MULTITASK_CHECKPOINT.md`
4. `docs/planning/R3_RTDETR_CHECKPOINT.md`
5. `docs/planning/T2_2_CHECKPOINT.md`
6. `docs/planning/R4_PSEUDO_BOX_CHECKPOINT.md` (added — directly referenced by
   the task's "995/995 positive, zero negatives" claim)
7. `src/pi_multimodal_ad/models/rtdetr_detection.py`
8. `scripts/train_rtdetr_detector.py`
9. Real run-directory artifacts (not just checkpoint-doc summaries):
   `runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af/tables/{detection_metrics,validation_threshold_selection,ap_by_iou_threshold,test_predictions}.csv|parquet`,
   `logs/{warmup,finetune}/results.csv`, `reports/rtdetr_detection_report.md`;
   `runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794/tables/annotation_manifest.parquet`;
   `configs/experiments/phm2026_rtdetr_detection.yaml`.

### Answer 1 — Does a genuine, held-out-EXP-F RT-DETR detection run already exist?

**Yes.** Canonical run `20260814T043751107678Z-7f1e13af`
(`runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af/`), produced by
`scripts/train_rtdetr_detector.py`. This is a genuine one-class RT-DETR-L
detector (backbone + multiscale/hybrid encoder + transformer decoder/object
queries + class head + box head retained), NOT the frozen-encoder scalar
regression from R3. Trained on EXP-B (448 images), confidence/threshold
selected on EXP-A (323 images, validation-only), evaluated exactly once on
EXP-F (224 images, true held-out test) — verified in the training script
itself via a hardcoded split-count assertion
(`{("train","EXP-B"):448, ("validation","EXP-A"):323, ("test","EXP-F"):224}`),
which is the exact T2.2 canonical split.

It measured precision, recall, F1, mAP@0.50, and mAP@0.50:0.95 via
`pi_multimodal_ad.models.rtdetr_detection.metrics_at_threshold` /
`average_precision` (the same functions this tutorial is told to reuse).
Verified straight from `tables/detection_metrics.csv` (scope=all, N=224
images, 9,883 pseudo-boxes, confidence=0.60 selected on EXP-A):

| metric | value |
|---|---|
| true_positive | 0 |
| false_positive | 0 |
| false_negative | 9,883 |
| precision | 0.0000 |
| recall | 0.0000 |
| F1 | 0.0000 |
| mAP@0.50 | 0.0000831 |
| mAP@0.50:0.95 | 0.0000159 |
| false_negative_images | 224 / 224 |

This is a genuine, complete negative result — not a frozen-encoder proxy.

**New evidence found beyond the checkpoint doc's summary** (this matters a lot
for Phase 4): `tables/validation_threshold_selection.csv` shows TP=0 at
**every** EXP-A confidence candidate from 0.01 through 0.60 (12 candidates
tested, 10,310 ground-truth boxes, 96,900 raw predictions at conf>=0.01).
Zero true positives even at the loosest confidence threshold means this is
not a confidence-miscalibration story — it is a **geometric IoU@0.5 mismatch**
between what the model predicts and what the pseudo-boxes look like, present
at every operating point. Quantified directly:

- Ground-truth pseudo-boxes (`annotation_manifest.parquet`, N=30,628 across
  995 images): median width 51px, median height 17px, **median area 840px²**,
  ~30.8 boxes/image (mean), max 72 boxes on one image.
- Model's EXP-F predictions (`test_predictions.parquet`, N=67,200 = 224
  images × 300 max_det, i.e. literally every decoder query survived the
  0.001 confidence floor for every image): median width 165.8px, median
  height 28.9px, **median area 5,006px²** — roughly **6x larger area** than
  the median pseudo-box, and confidence values pinned in an extremely narrow
  band (0.00138 mean, std 0.000025) — essentially flat/uninformative, meaning
  the classification head never learned to discriminate this one class at
  all within the schedule actually run.
- Training curves (`logs/{warmup,finetune}/results.csv`): Ultralytics'
  own val mAP50(B) is ~0.00006–0.0002 from epoch 1 onward and does not
  improve with more fine-tune epochs; val cls_loss/giou_loss/l1_loss do not
  show a clear convergent trend across the 4 fine-tune epochs (best epoch
  selected was epoch 1). Total training time was 234.19 seconds — a very
  short schedule (1 smoke epoch on 3% of data, 1 warmup epoch with 21/28
  layers frozen, then early-stopped fine-tuning after 4 epochs).

This gives a concrete, falsifiable starting hypothesis for Phase 4: the
combination of (a) a pseudo-label design that is dense (~31 tiny boxes/image,
median area 840px²) and all-positive (995/995 images positive, 0 negatives,
per `R4_PSEUDO_BOX_CHECKPOINT.md`), and (b) a very short training schedule
that never moved the classification head off its confidence floor, jointly
explain the near-zero mAP — independent of whether RT-DETR-as-an-architecture
is fundamentally unsuited to this problem. Phase 4 will test this directly
rather than assume it, exactly as the task asks.

### Answer 2 — Is the run's split/config still canonical/pinned, or stale?

**Still canonical.** `configs/experiments/phm2026_rtdetr_detection.yaml` pins
`source_runs.pseudo_boxes` = `20260814T040854991567Z-3fa0f794` (the R4
pseudo-box run, itself built from the T2.2/T2.1-pinned split and target
version `phm2026_image_damage_v2`) and `source_runs.pretrained` =
`20260814T020338751021Z-d0f225c8` (R3's frozen-encoder run, reused only for
its downloaded `rtdetr-l.pt` COCO checkpoint artifact). The training script
hard-asserts the split counts match T2.2 exactly before it will run. No
newer pseudo-box run, target version, or split run exists in
`docs/planning/PROJECT_STATE.md`'s "Completed work" list — `phm2026_image_damage_v2`
and split run `20260814T013357354377Z-6b068cab` remain the latest.

### Answer 3 — (a) reuse existing run, or (b) retrain fresh? Decision and reasoning

**Decision: (a) — reuse run `20260814T043751107678Z-7f1e13af`'s predictions
and metrics as this tutorial's "final score," and put this task's effort into
the interpretability/causal-analysis deliverable (Phases 2 and 4-5).**

Reasoning:

1. The existing run already satisfies every requirement the task states for
   "an actual performance score": genuine (non-frozen) RT-DETR, the exact
   pinned canonical split, a true held-out single-pass EXP-F evaluation, and
   metrics computed with the exact reusable functions
   (`pi_multimodal_ad.models.rtdetr_detection`) this task is told to reuse
   rather than reimplement.
2. Training is seeded and deterministic-mode-requested
   (`training.deterministic: true`, fixed `seed: 20260814`), so a re-run
   under the identical pinned config, pinned pseudo-box run, and pinned
   pretrained checkpoint would be expected to reproduce essentially the same
   catastrophic near-zero result — the run's own checkpoint doc already flags
   that CUDA's grid-sampler backward has no deterministic implementation, so
   a rerun would not even be bit-exact, just another sample from the same
   failure mode. Spending a full GPU training run to regenerate a number we
   can already show, with no new hyperparameters and no new question being
   asked of it, would not add evidence toward the actual ask (explaining
   *why* it fails).
3. Retraining with *different* hyperparameters (to try to fix it) is outside
   this task's scope — the ask is to explain the existing baseline's
   behavior with evidence, then separately propose evidence-backed changes
   in the final report. Actually implementing a fix belongs to a follow-on
   task, not this one.
4. Reuse keeps this tutorial's evidence traceable to a single canonical,
   already-hash-pinned, already-governed run — consistent with this repo's
   own norm of "never substitute 'latest run'" (`PROJECT_STATE.md`) and with
   the hard constraint to reuse code by importing rather than forking.
5. This also directly serves the task's own hint: Phase 0 was explicitly
   asked to check whether the pseudo-label design (not the architecture)
   drives the poor mAP — and the box-size/confidence-floor evidence above
   already points there. Reusing (a) lets Phase 4 spend its full effort
   confirming or refuting that hypothesis with deep, real analysis (error
   taxonomy, slicing, calibration, PR curve, domain-shift quantification,
   activation inspection) instead of re-deriving a number that already
   exists and is already the real, valid answer.

Compute is available (this run's own logs confirm a Tesla T4 was used
previously; the current session also has an available CUDA GPU per
`nvidia-smi`), so this is not a compute-avoidance shortcut — it is a
deliberate choice to spend the (unconstrained) compute budget on Phase 4's
deep analysis, which is the actual ask, rather than on a redundant retrain.

**Consequence for the phase plan below:** Phase 3 ("Train + evaluate — only
if Phase 0 chose option (b)") is skipped entirely and will be marked as such
in its own checkpoint update. Phase 2 will materialize/link to the existing
run's cached images + pseudo-box labels (not re-download/re-derive them) and
add the descriptive/size-distribution analysis the task asks for. Phase 4
will pull real predictions, real pseudo-boxes, and real cached images from
run `20260814T043751107678Z-7f1e13af` (predictions) and
`20260814T040854991567Z-3fa0f794` (images + pseudo-boxes, materialized cache
under that run's directory) to do the actual error/slice/calibration/domain-shift/
activation analysis.

---

## Phase 1 — Plan

Wrote `tutorials/final_baseline_rtdetr/PLAN.md`: reuse run
`20260814T043751107678Z-7f1e13af` for the headline score; reuse
`pi_multimodal_ad.models.rtdetr_detection`'s metrics functions; an 8-item
prioritized interpretability plan (confidence-floor thresholding artifact
added as new highest-priority item found directly in Phase 0's data,
box-geometry mismatch, calibration, PR curve, view-role-driven domain shift,
error taxonomy, size-bucketed slicing, activation hooks reused from
`tutorials/rtdetr_storybook/rtdetr_storybook.py`). Full reasoning in
`PLAN.md`; not duplicated here.

## Phase 2 — Data assembly

Wrote and ran `tutorials/final_baseline_rtdetr/scripts/phase2_data_summary.py`
(read-only against the pinned pseudo-box run's parquet tables; no images
copied, no writes into `runs/`, no raw-archive access). Output under
`tutorials/final_baseline_rtdetr/data_summary/`: `split_summary.csv`,
`split_view_role_composition.csv`, `view_role_share_pct_by_split.csv`,
`box_size_and_count_by_split.png`. Cross-checked the manifest's own
`box_count` column against a fresh groupby of the box table before trusting
either (zero mismatches over 995 images — the script raises if this ever
disagrees).

**Data summary (real numbers, all provisional `phm2026_image_damage_v2`
pseudo-boxes, not organizer ground truth):**

| split | experiment | images | total boxes | mean boxes/img | median boxes/img | median box area (px²) | % camera_sequence view | % canonical_tooth view |
|---|---|---|---|---|---|---|---|---|
| train | EXP-B | 448 | 10,435 | 23.29 | 23 | 968 | 62.5% | 37.5% |
| validation | EXP-A | 323 | 10,310 | 31.92 | 32 | 912 | 61.9% | 38.1% |
| test | EXP-F | 224 | 9,883 | 44.12 | 43 | 676 | **0.0%** | **100.0%** |

This quantifies two compounding, previously only qualitatively-described
shifts between train/validation and test:

1. **Box density almost doubles**: EXP-F averages 44.1 pseudo-boxes/image vs
   23.3 on EXP-B/train (1.9x) and 31.9 on EXP-A/validation (1.4x); range of
   boxes/image on test (18-72) sits entirely above train's typical range.
2. **Box size shrinks**: EXP-F's median pseudo-box area (676px²) is ~30%
   smaller than train's (968px²) — smaller AND more numerous boxes packed
   into the same fixed ROI.
3. **View-role composition is not just different in degree but categorical**:
   train/validation are ~62% close-up `camera_sequence` (WIN_* burst photos
   for teeth 1-4) / ~38% `canonical_tooth` (single wide photo per tooth);
   EXP-F is 100% `canonical_tooth`. The model was never validated on a
   view-role mix resembling its actual test distribution — EXP-A validation,
   despite being a different experiment, still shares the close-up/canonical
   mixture that EXP-F entirely lacks.

The area-distribution histogram (`box_size_and_count_by_split.png`) shows
all three splits' log-area distributions are heavily overlapping and
unimodal (no evidence of a broken/degenerate mask pipeline per split); the
boxes-per-image histogram cleanly separates the three splits with test's
distribution visibly shifted right (denser) relative to train, confirming
finding 1 is not an artifact of a few outlier images.

## Phase 3 — Train + evaluate

**Skipped.** Phase 0 selected option (a): reuse existing run
`20260814T043751107678Z-7f1e13af` rather than retrain. See Phase 0's
"Answer 3" above for full reasoning.

---

## Phase 4 — Explain WHY it performed that way

Four scripts under `tutorials/final_baseline_rtdetr/scripts/`, all reusing
`pi_multimodal_ad.models.rtdetr_detection`'s functions (and, for item 8,
`tutorials/rtdetr_storybook/rtdetr_storybook.py`'s hook machinery) rather
than reimplementing IoU matching, AP, or hook registration. Output under
`tutorials/final_baseline_rtdetr/analysis/{01..04}_*/`.

### Finding 1 — the official TP=0 result is partly a thresholding artifact, but a real (much smaller) signal exists underneath

`scripts/phase4_01_threshold_and_geometry.py`. EXP-F test predictions'
confidence values span **0.001242-0.001497** — every one of the 12 official
candidate thresholds (0.01-0.60) is *above* this entire range, so literally
0 of 67,200 predictions ever survive any tested threshold. That is why
TP=FP=0 identically at every row of `validation_threshold_selection.csv`
and at the selected test-time threshold 0.60 — not evidence the model made
zero correct-shaped guesses, evidence that the threshold sweep never went
low enough to look.

Recomputing `match_counts`/`average_precision` (reused, not reimplemented)
at the model's true minimum confidence (effectively unthresholded, all
67,200 raw predictions retained) finds: **TP=145, FP=67,055, FN=9,738**
out of 9,883 pseudo-boxes — recall **1.47%**, precision **0.216%**, mean
matched IoU (for the boxes that *do* match) **0.579**. A full threshold
sweep across the model's true range (`threshold_sweep_full_range.csv`) shows
the best achievable operating point tops out around precision **0.45%**,
recall **0.32%** — i.e. even hand-picking the best threshold post hoc, this
detector is not usable at any operating point, confirming the "is there ANY
threshold where this works" menu question with real evidence: no.

### Finding 2 — box-geometry mismatch is the dominant, quantifiable cause of the near-zero recall

Same script, `box_geometry_prediction_vs_pseudo_box.csv`. Median prediction
area on EXP-F is **5,007px²** vs median pseudo-box area **676px²** — **7.4x**
larger; median width 3.6x larger, height 1.9x larger, aspect ratio also
more elongated (5.93 vs 3.12). A simple area-ratio upper bound shows a
median-sized prediction perfectly containing a median-sized pseudo-box with
zero wasted area could reach at most IoU **0.135** — well under the 0.5
operating threshold used everywhere in this pipeline. This is not a
localization failure; see Finding 4.

Directly confirmed by `phase4_02_calibration_and_slicing.py`'s pseudo-box
size-tercile recall table: **0.0% recall in the small tercile (median
253px²), 0.0% in the medium tercile (median 676px²), 4.4% in the large
tercile (median 3,108px²) — every one of the 145 true positives came from
the largest third of pseudo-boxes.** This is the single cleanest, most
conclusive result in the whole analysis: box scale, not spatial location or
confidence, is the dominant recall bottleneck.

### Finding 3 — confidence is uninformative (near-zero calibration correlation)

Same script. Pearson correlation(confidence, IoU>=0.5-match) = **0.0214**
over all 67,200 test predictions — essentially no linear relationship.
Decile breakdown shows a real but small step up in match rate in the top 3
deciles (~0.0036-0.0045) vs the bottom 7 (~0.0007-0.0019), so the signal
is not pure noise, but it is far too weak and far too compressed
(0.00124-0.00150 total range) to threshold on for any practical use. This
is consistent with the extremely short training schedule (234 total
seconds, best epoch = 1) never meaningfully separating the classification
head's outputs.

### Finding 4 — the backbone/encoder ARE localizing correctly; the failure is downstream

`phase4_04_activation_hooks.py`, reusing the storybook's hook code against
the actual fine-tuned `best_detector.pt` (not the stock baseline). On both
a true-positive-present example and a false-negative-only example, the
"Eyes" (HGStem backbone) activation-energy heatmap lights up sharply and
specifically on the exact horizontal damage streak — matching the pseudo-box
region closely — regardless of whether that image ended up with any
recorded true positive. The "Brain" (AIFI encoder) heatmap is far more
diffuse (expected, since AIFI operates on the smallest 20x20 feature map)
but still weighted toward the same lower-middle region, not random. This
rules out "the model isn't looking at the right place at all" as an
explanation — combined with Finding 2, the evidence points specifically at
the box-regression/decoder head producing badly-scaled boxes despite
reasonable early localization.

### Finding 5 — EXP-F's test-time distribution differs from train/validation in three compounding, quantified ways

From Phase 2's `split_summary.csv` plus Phase 4's `sliced_metrics_view_role_and_run.csv`:
(a) box density almost doubles test-vs-train (44.1 vs 23.3 boxes/image
mean); (b) median box area shrinks ~30% test-vs-train (676px² vs 968px²) —
compounding Finding 2, since the training distribution's boxes were already
closer in scale to what the model tends to predict, and EXP-F pushes
further away; (c) **view_role composition is categorically different**:
train/validation are ~62% close-up `camera_sequence` / ~38% wide
`canonical_tooth`, EXP-F is 100% `canonical_tooth` — the validation split
used for confidence-threshold selection never resembled the test
distribution on this axis either. Per-run slicing on EXP-F
(`sliced_metrics_view_role_and_run.csv`) shows recall creeping up across
later runs (run 1: 1.6%, run 8: 2.3%) — consistent with progressive wear
producing larger damage patches later in a run's life, which (per Finding 2)
are exactly the pseudo-boxes this model can occasionally match.

### Finding 6 — qualitative error taxonomy confirms the quantitative story

`phase4_03_error_taxonomy.py`. 105/224 (46.9%) EXP-F images have at least
one IoU>=0.5 match somewhere in their unthresholded prediction set — so the
lucky matches are spread thin across nearly half the images, not
concentrated in a few easy cases. Drawn examples
(`analysis/03_error_taxonomy/*.jpg`) visually confirm Finding 4: the
model's highest-confidence raw guesses (red) consistently cluster over the
correct damage-streak region in both true-positive and false-negative
examples, but are coarser and fewer than the dense field of tiny green
pseudo-boxes — visually the same box-scale mismatch Finding 2 quantifies.

### Menu items folded in rather than run separately

- PR-curve ("is there any usable threshold") is answered directly by
  Finding 1's full sweep — no separate item.
- Calibration is Finding 3.
- Domain shift is Finding 5.
- "True positive" qualitative examples exist (Finding 6) but are sparse and
  weak (max 4 boxes matched on the best example image below), which is
  itself reported as a finding, not silently dropped.

---

## Phase 5 — Final report

Wrote `tutorials/final_baseline_rtdetr/REPORT.md`: headline metrics
(precision/recall/F1=0, mAP@0.50=0.0000831, mAP@0.50:0.95=0.0000159 at the
official operating point), six findings each tied explicitly to specific
evidence files/numbers ("X is low because Y, evidenced by Z" pattern
throughout), a plain-language restatement of what the headline numbers
mean, and a separated section of five concrete, evidence-backed suggestions
(coarser pseudo-box granularity, longer training, threshold-candidate
range informed by real model output, EXP-F-representative validation
slice, and a caution against increasing IoU-threshold emphasis before
fixing box scale) — each suggestion cites the specific finding it follows
from, not a generic wishlist.

## Next action

**None — task complete.** All five phases (0, 1, 2, 4, 5) are done; Phase 3
was correctly skipped per the Phase 0 decision. Deliverables:
`PLAN.md`, `CHECKPOINT.md` (this file), `REPORT.md`, `data_summary/`
(4 files), `analysis/{01..04}_*/` (14 files across 4 subfolders),
`scripts/` (5 scripts). Nothing was committed or pushed. Ready for review.
