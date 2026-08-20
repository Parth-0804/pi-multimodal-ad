# RT-DETR gear-tooth damage baseline — score, and why it scores that way

> **Read this before the numbers.** Every box used here — targets and
> predictions alike are trained against — is the provisional
> `phm2026_image_damage_v2` pseudo-label: a deterministic heuristic mask
> (CLAHE contrast normalization + background subtraction + robust z-score
> threshold + morphology, all pinned in
> `configs/experiments/phm2026_image_target.yaml`), not organizer ground
> truth, not expert-reviewed. Nothing in this report is a claim about
> physical spall/pitting detection accuracy. It measures whether a genuine
> RT-DETR detector agrees with that heuristic's boxes, and explains why it
> mostly doesn't.

## What this is

This tutorial reuses an existing, canonical, already-completed RT-DETR
detection run rather than retraining (see `CHECKPOINT.md`'s Phase 0 for the
full decision record) and spends its effort on a deep, evidence-based
explanation of *why* that run scored the way it did. All data, splits, and
metric functions are reused by import from the governed pipeline; nothing
under `src/`, `scripts/`, `configs/`, or `runs/` was modified, and
`gtc-data-experiment/` was never opened by this tutorial (all images come
from an already-materialized, pinned cache).

- **Model**: genuine one-class Ultralytics RT-DETR-L (`rtdetr-l.pt`
  COCO-pretrained backbone, fine-tuned) — backbone, multiscale/hybrid
  encoder, transformer decoder/object queries, classification head, and box
  head all retained and trained. Class: `damage_candidate`.
- **Split** (T2.2-pinned, reused unmodified, zero leakage): train = EXP-B
  (448 images), validation = EXP-A (323 images, used only for confidence
  selection), test = EXP-F (224 images, evaluated once, held out).
- **Source run reused as the score**: `runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af/`.
- **Source run reused for images/pseudo-boxes**: `runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794/`.

## The headline score

At the confidence threshold (0.60) selected on EXP-A validation, evaluated
once on the EXP-F test set (N=224 images, 9,883 pseudo-boxes), using
`pi_multimodal_ad.models.rtdetr_detection`'s own metric functions:

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

**This is a genuine, complete negative result, and it is not dressed up
here.** A one-class RT-DETR detector trained on this pipeline's provisional
pseudo-boxes, under this training schedule, does not produce usable
detections on held-out EXP-F at any officially-tested operating point.

That is not, however, the full story — the sections below explain
specifically *why*, using recomputed metrics (same reused functions, wider
threshold sweep) and several independent lines of evidence that all agree.

## Why it scored that way — findings tied to evidence

### 1. The official TP=0 is partly a thresholding artifact — but a real, much smaller failure remains underneath

Every one of the 12 confidence candidates tested during validation
selection (0.01 through 0.60) is *above* the model's entire observed
prediction-confidence range on EXP-F (**0.001242–0.001497**). So literally
none of the model's 67,200 raw test predictions (224 images × 300 max
detections) ever survived any threshold that was tried — `TP=FP=0`
identically at every row of `validation_threshold_selection.csv`, and at
the selected test threshold 0.60. This alone explains the *exact* zero in
the headline table; it does not yet tell us whether the model made any
geometrically correct guesses at all.

Recomputing the same reused matching/AP functions with the threshold swept
down through the model's real range (`analysis/01_threshold_and_geometry/threshold_sweep_full_range.csv`,
figure `geometry_and_pr_curve.png`) finds the true floor: at the loosest
possible threshold (effectively unthresholded), **TP=145, FP=67,055,
FN=9,738** — recall **1.47%**, precision **0.216%**, mean IoU of the boxes
that do match **0.579** (a real, non-trivial overlap, not borderline-0.5
noise). The best achievable operating point anywhere in the sweep reaches
only precision ≈0.45%, recall ≈0.32% — so while the exact-zero in the
official table is partly an artifact of an under-ranged threshold list, the
detector is genuinely unusable at *every* threshold, not just the ones
tested. **X (headline recall/precision = 0.0) is low because Y (thresholds
tested were entirely above the model's actual confidence range) — but even
Z (the true achievable best-case across the full range) is still ~0.3-1.5%,
evidenced by the full sweep in `threshold_sweep_full_range.csv`.**

### 2. Box-scale mismatch is the dominant, quantified cause of the residual failure

`analysis/01_threshold_and_geometry/box_geometry_prediction_vs_pseudo_box.csv`:
on EXP-F, median prediction area is **5,007px²**; median pseudo-box area is
**676px²** — predictions are **7.4x larger by area** (3.6x wider, 1.9x
taller, and more elongated: aspect ratio 5.93 vs 3.12). A simple
area-ratio bound shows that even a perfectly-placed median-sized prediction
containing a median-sized pseudo-box with zero wasted area could reach at
most IoU 0.135 — well short of the 0.5 operating threshold used everywhere
in this evaluation.

This is directly confirmed, not just bounded, by
`analysis/02_calibration_and_slicing/recall_by_pseudo_box_size_tercile.csv`:
splitting EXP-F's 9,883 pseudo-boxes into size terciles gives **0.0%
recall for the small tercile (median 253px²), 0.0% for the medium tercile
(median 676px²), and 4.4% for the large tercile (median 3,108px²) — every
single one of the 145 true positives found anywhere in the unthresholded
prediction set came from the largest third of pseudo-boxes.** This is the
single cleanest result in the whole analysis. **Recall is near-zero because
the model's box-regression head outputs boxes at roughly 7x the pseudo-label
scale, evidenced by the geometry table and made unambiguous by the
size-tercile recall split.**

### 3. Confidence carries almost no signal about correctness

`analysis/02_calibration_and_slicing/calibration_by_decile.png` and
`calibration_correlation.txt`: Pearson correlation between confidence and
IoU≥0.5-match across all 67,200 EXP-F predictions is **0.0214** — a real
but negligible relationship. The top 3 confidence deciles do show roughly
2-3x the match rate of the bottom 7 (≈0.0036-0.0045 vs ≈0.0007-0.0019), so
it is not literally random, but the entire usable range spans only
0.00124-0.00150 — far too narrow to threshold on in practice. **The
confidence output is uninformative because the training schedule (234
total seconds, best epoch selected = epoch 1 of a 4-epoch early-stopped
fine-tune, per `docs/planning/R4_RTDETR_DETECTION_CHECKPOINT.md`) never
meaningfully separated the classification head's outputs, evidenced
directly by this near-zero correlation.**

### 4. The backbone/encoder ARE localizing correctly — the failure is downstream of them

`analysis/04_activation_hooks/*_activation.png`, produced by running the
actual fine-tuned `best_detector.pt` (not the untrained storybook baseline)
with the same forward-hook technique as
`tutorials/rtdetr_storybook/rtdetr_storybook.py`. On both a
true-positive-present example and a false-negative-only example, the
backbone ("Eyes"/HGStem) activation-energy heatmap lights up sharply and
specifically on the exact horizontal damage-streak region, closely tracking
where the pseudo-boxes actually are — this happens whether or not that
particular image ended up with a recorded match. The encoder ("Brain"/AIFI)
heatmap is far more diffuse (expected: AIFI runs only on the smallest 20×20
feature map) but is still weighted toward the same region, not uniform
noise.

This is corroborated qualitatively by
`analysis/03_error_taxonomy/*.jpg`: the model's own highest-confidence raw
guesses (drawn in red) visibly cluster over the correct damage streak in
both true-positive and false-negative example images — they are simply
much coarser and fewer than the dense field of tiny green pseudo-boxes.
**The model is not failing to "see" the damage region — it is failing to
regress boxes at the right scale once it gets there — evidenced jointly by
the activation heatmaps, the qualitative example drawings, and the size-tercile
recall finding above.**

### 5. Test-time distribution shift compounds the scale mismatch on three separate axes

From `data_summary/split_summary.csv` and
`analysis/02_calibration_and_slicing/sliced_metrics_view_role_and_run.csv`:

| split | experiment | mean boxes/image | median box area (px²) | % camera_sequence view | % canonical_tooth view |
|---|---|---|---|---|---|
| train | EXP-B | 23.29 | 968 | 62.5% | 37.5% |
| validation | EXP-A | 31.92 | 912 | 61.9% | 38.1% |
| test | EXP-F | **44.12** | **676** | **0.0%** | **100.0%** |

Three compounding, quantified shifts: (a) box **density** nearly doubles
test-vs-train (44.1 vs 23.3 mean boxes/image); (b) box **size shrinks**
further test-vs-train (676px² vs 968px² median) — pushing EXP-F's targets
even further from the ~5,007px² scale the model tends to predict, worsening
Finding 2 specifically at test time; (c) EXP-F is **100% canonical_tooth**
wide-frame views while train/validation are ~62% close-up
`camera_sequence` views — the validation split used to pick the confidence
threshold was never representative of the test view-role distribution
either. Per-run slicing on EXP-F shows a mild upward recall trend across
runs (run 1: 1.6% → run 8: 2.3%), consistent with progressively larger
damage patches later in a run's life being marginally more matchable per
Finding 2. **EXP-F's near-total failure is worse than EXP-A's would likely
be, because EXP-F sits further from the training distribution on box size,
box density, and view composition simultaneously, evidenced by the split
summary table.**

### 6. Qualitative error taxonomy

`analysis/03_error_taxonomy/per_image_category_summary.csv`: 105/224
(46.9%) EXP-F images have at least one IoU≥0.5 match somewhere in their
unthresholded prediction set — the (small) signal is spread thin across
nearly half the images rather than concentrated in a handful of easy cases,
consistent with a systematic scale problem rather than a few anomalous
images. True-positive examples top out at 4 matched boxes per image against
tens of pseudo-boxes (e.g. `true_positive_present_image_sample_9ac.jpg`:
58 pseudo-boxes, 4 matches) — genuine true positives exist but are rare and
partial, not a hidden success story the aggregate metrics are obscuring.

## What the headline numbers actually mean, restated plainly

- **mAP@0.50 = 0.0000831 is low because**: (1) the officially tested
  confidence thresholds never admitted any predictions (Finding 1), and (2)
  even the unthresholded prediction set only geometrically matches pseudo-boxes
  7.4x smaller than its typical output at a 1.47% hit rate, concentrated
  entirely in the largest size tercile (Finding 2).
- **Precision/recall = 0/0 at the selected threshold is because**: the
  selected threshold (0.60) sits ~400x above the model's actual maximum
  observed confidence (0.0015) — not because the model produces zero
  reasonable-looking boxes (Finding 1, Finding 6).
- **The gap is not a "model can't see the damage" problem**: backbone
  activations correctly localize to the damage streak in both successful
  and failed examples (Finding 4) — it is specifically a box-regression
  scale problem, worsened by an undertrained, uninformative confidence head
  (Finding 3) and a test distribution that pushes pseudo-box scale even
  further from the model's typical output than train/validation did
  (Finding 5).

## Concrete, evidence-backed suggestions for what to change next

Each suggestion below follows directly from a specific finding above —
this is not a generic detector-tuning checklist.

1. **Redefine the pseudo-label boxes at a coarser granularity, or merge
   adjacent components before boxing.** Directly follows Finding 2: median
   pseudo-box area (676-968px² depending on split) is inherently far below
   what RT-DETR's decoder queries naturally regress to at 640×640 input
   resolution, and Finding 2's size-tercile split shows recall is
   monotonically tied to box size, not confidence or location. The pipeline
   already computes connected components before boxing
   (`targets/image_damage.py`'s `measure_damage_candidate` +
   `make_raw_demo_dataset.py`'s / the pseudo-box run's `boxes_from_mask`);
   a coarser closing kernel, a larger `minimum_component_fraction`, or a
   deliberate component-merging pass before box extraction would shrink the
   scale gap without touching the underlying damage-detection heuristic's
   sensitivity.
2. **Train substantially longer, or unfreeze more layers, before drawing
   any conclusion about architecture fit.** Directly follows Finding 3: the
   canonical run trained for only 234 total seconds with early stopping at
   fine-tune epoch 1, and the classification head never developed a
   confidence range wider than 0.0003 — that is consistent with
   undertraining, not with RT-DETR being fundamentally unable to learn this
   task. Given Finding 4 shows the backbone already localizes well even
   under this short schedule, more fine-tuning epochs (with the same frozen
   layers, or fewer frozen layers) is a concrete, testable next experiment
   before switching architectures.
3. **Re-select the validation confidence-threshold candidate range using
   the model's actual observed confidence distribution, not a fixed
   0.01-0.60 list.** Directly follows Finding 1: `select_confidence_threshold`'s
   candidate list should be informed by (or include) values near the
   trained model's realized output range, otherwise a future run with a
   similarly under-trained classification head will silently reproduce the
   same "TP=0 at every candidate" artifact and obscure whatever partial
   signal does exist, exactly as happened here.
4. **Rebalance the validation split's view-role composition toward EXP-F's,
   or add an EXP-F-view-role-matched validation slice, before trusting
   confidence-threshold selection.** Directly follows Finding 5: EXP-A
   validation (61.9% camera_sequence / 38.1% canonical_tooth) does not
   resemble EXP-F test (100% canonical_tooth) on this axis; any threshold
   or hyperparameter chosen against EXP-A is being chosen against a
   distribution the model will not see at test time.
5. **Do not increase the IoU@0.5 operating threshold's importance without
   first fixing box scale.** Given Finding 2's area-ratio bound (max
   achievable IoU ≈0.135 for a typical size pair), any metric or loss
   change that further emphasizes tight IoU agreement (rather than, e.g., a
   scale-aware loss term or GIoU reweighting toward smaller anchor
   priors) will not fix the underlying mismatch and risks masking it
   further.

## What's in this folder

- `PLAN.md` — Phase 1 plan (data path, metrics, prioritized analysis list).
- `CHECKPOINT.md` — running phase-by-phase log with full reasoning.
- `data_summary/` — Phase 2 split/box-size/view-role tables and figure.
- `analysis/01_threshold_and_geometry/` — Finding 1 + 2 tables and figure.
- `analysis/02_calibration_and_slicing/` — Finding 3 + 5 (partial) + size-tercile evidence for Finding 2.
- `analysis/03_error_taxonomy/` — Finding 6, qualitative example images.
- `analysis/04_activation_hooks/` — Finding 4, backbone/encoder activation heatmaps.
- `scripts/` — the four Phase 4 analysis scripts plus the Phase 2 data-summary
  script, all read-only against the two pinned runs named above, all
  reusing `pi_multimodal_ad.models.rtdetr_detection` (and, for the
  activation-hook script, `tutorials/rtdetr_storybook/rtdetr_storybook.py`)
  by import.

Nothing here was committed or pushed; everything is left in the working
tree for review.
