# final_baseline_rtdetr — plan

Decision from Phase 0 (see `CHECKPOINT.md`): **reuse existing run
`20260814T043751107678Z-7f1e13af`** as the final score; spend this task's
effort on Phases 2 and 4-5 (data summary + deep causal analysis + report).
Phase 3 (train fresh) is skipped.

## Data path

- **Images + pseudo-boxes**: pinned pseudo-box run
  `runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794/`
  (config `configs/experiments/phm2026_rtdetr_detection.yaml`'s
  `source_runs.pseudo_boxes`). Read-only from this tutorial:
  `tables/annotation_image_manifest.parquet` (995 rows, one per image
  sample), `tables/annotation_manifest.parquet` (30,628 rows, one per
  pseudo-box), and the materialized JPEG cache under `cache/images/{train,
  validation,test}/` + YOLO-format labels under `cache/labels/...` (already
  extracted once, read-only from here — never regenerated or written to).
- **Target version**: `phm2026_image_damage_v2` (provisional pseudo-label;
  `annotation_manifest.parquet.target_definition_version` confirms every row
  is this version). Class is a single label, `damage_candidate`.
- **Split**: the T2.2-pinned split, reused unmodified — EXP-B train (448
  images), EXP-A validation (323 images), EXP-F test (224 images), verified
  by the `annotation_image_manifest.parquet.split`/`experiment` columns and
  cross-checked against `T2_2_CHECKPOINT.md`'s published counts. No new split
  logic of any kind is written in this tutorial.
- **Model predictions**: pinned detection run
  `runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af/tables/{test_predictions,validation_predictions}.parquet`
  (raw predictions at every confidence >= 0.001, i.e. effectively
  unthresholded — 67,200 test rows = 224 images × 300 max_det, 96,900
  validation rows = 323 × 300) plus `checkpoints/best_detector.pt` (loaded
  read-only for the Phase 4 activation-hook pass only; no weight update).

## Metrics — reused, not reimplemented

Imported directly from `pi_multimodal_ad.models.rtdetr_detection`:
`box_iou`, `_iou_matrix` (module-private but reused via the public
`match_counts`/`average_precision` wrappers), `match_counts`,
`average_precision`, `metrics_at_threshold`, `select_confidence_threshold`,
`sliced_metrics`. These are the exact functions the canonical run used, so
every number this tutorial reports is reproducible against the same
definitions (greedy IoU@0.5 matching by descending confidence, 101-point
interpolated AP, precision/recall/F1 at a chosen operating threshold).

Headline numbers to report as-is from the existing run (no recomputation
needed, already verified against real CSVs in Phase 0): precision=0,
recall=0, F1=0, mAP@0.50=0.0000831, mAP@0.50:0.95=0.0000159 at the
EXP-A-selected confidence 0.60, N=224 EXP-F images, 9,883 pseudo-boxes.

## Interpretability analyses — prioritized by Phase 0 evidence

Phase 0 surfaced three concrete, falsifiable, *already partially quantified*
findings that reframe the menu's priority order:

1. **Confidence-floor artifact (new, highest priority — not on the original
   menu, added because Phase 0 found it directly in the data)**: every one
   of the model's 300 queries per image outputs confidence in a narrow band
   (0.00124–0.00150) — *below* every tested confidence candidate (0.01–0.60).
   So `TP=0` in the official table is partly a **thresholding artifact**: no
   candidate threshold was ever low enough to admit any prediction. This
   must be disentangled from genuine detection failure by recomputing
   `match_counts`/`average_precision` at the model's actual observed minimum
   confidence (~0.0012) — i.e. effectively unthresholded — to see how many
   true IoU@0.5 matches exist in the full 67,200-prediction pool at all,
   before asking why so few of them count.
2. **Pseudo-label design / box-geometry mismatch (menu item, high priority —
   already quantified in Phase 0)**: median pseudo-box area 840px² vs
   median (effectively unthresholded) prediction area 5,006px² — ~6x larger,
   with ~31 pseudo-boxes packed per image vs. RT-DETR's per-query box
   proposals. Plan: histogram/ECDF box width, height, area, and
   count-per-image for predictions vs. pseudo-boxes on the same images;
   directly test whether IoU@0.5 is geometrically achievable at these size
   ratios even with perfect localization (a back-of-envelope: one predicted
   box the size of ~6 GT boxes cannot reach IoU 0.5 with any single one of
   them unless it happens to align almost exactly with just one).
3. **Confidence calibration (menu item)**: given finding 1, calibration is
   almost certainly "uninformative" — the near-zero-variance confidence band
   leaves no room for confidence to track correctness. Plan: still compute
   it properly (bin predictions by confidence quantile — even within the
   tiny 0.0012–0.0015 band — against IoU@0.5 correctness) rather than
   asserting this; report the (very likely degenerate) result as evidence,
   not assumption.
4. **Precision-recall operating curve (menu item)**: reproduce properly
   using `select_confidence_threshold`/`sliced_metrics` machinery, but
   extend the candidate list down to the true observed minimum confidence
   (~0.0012) rather than stopping at 0.01, since finding 1 shows the
   existing curve is entirely degenerate (flat at the origin) over the
   originally tested range.
5. **EXP-A/EXP-B → EXP-F domain shift (menu item, high priority — Phase 0
   found a second, previously undocumented shift)**: `view_role` breakdown
   from `annotation_image_manifest.parquet` shows EXP-B/train is 62.5%
   `camera_sequence` (close-up WIN_ photos) / 37.5% `canonical_tooth`, EXP-A/
   validation is 61.9% / 38.1%, but **EXP-F/test is 100.0% `canonical_tooth`,
   0% `camera_sequence`** — the model never validated or trained on a
   test-representative view-role mix; EXP-A validation (used for confidence
   selection) itself only partially resembles EXP-F. Plan: quantify box
   count/size *per view_role* in addition to per-experiment, to see whether
   the already-known EXP-A→EXP-F shift is actually compounded by (or
   largely explained by) this view-role composition shift.
6. **Error taxonomy with concrete examples (menu item)**: pull real
   false-negative / (if any exist) true-positive image+box examples once
   finding 1 is resolved (i.e. at a threshold where predictions actually
   exist) — the existing run's `deterministic_examples.parquet` was
   generated at confidence 0.60, where finding 1 shows literally nothing
   survives, so every example in it is trivially "false_negative" by
   construction and not informative on its own; will regenerate at a
   non-degenerate low threshold for real qualitative inspection.
7. **Slicing by split/view_role/run/box-size (menu item)**: reuse
   `sliced_metrics` (already slices by view_role and run) at the corrected
   threshold, and add a box-size-bucketed slice (small/medium/large
   pseudo-box terciles) since finding 2 suggests size is the dominant axis.
8. **Backbone/encoder activation qualitative check (menu item)**: reuse the
   forward-hook approach from `tutorials/rtdetr_storybook/rtdetr_storybook.py`
   (`StorybookHooks`/`_find_first_module`/`_activation_heatmap`, imported by
   path-inserting that tutorial's directory the same way
   `rtdetr_storybook.py` itself does for `make_raw_demo_dataset`, since it's
   a tutorial module rather than `src/pi_multimodal_ad/` code and copying it
   would violate the "reuse via import" constraint) on `best_detector.pt`
   for a handful of representative EXP-F failure cases, to see qualitatively
   whether the Eyes/Brain stages are even localizing to the damage-streak
   region before the head's (finding-1-degenerate) classification collapses
   everything to the confidence floor.

Menu items intentionally **not** run as separate work, with reason: nothing
dropped outright — items 3-4 above already fold the calibration/PR-curve
menu items in; the "true positive" qualitative example category is expected
to be sparse-to-empty per finding 1, which will be reported as a finding
itself (see item 6) rather than skipped silently.

## Deliverable shape

- `tutorials/final_baseline_rtdetr/data_summary/` — Phase 2 tables/plots.
- `tutorials/final_baseline_rtdetr/analysis/` — Phase 4 tables/figures
  (one subfolder per numbered finding above).
- `tutorials/final_baseline_rtdetr/REPORT.md` — Phase 5 final write-up.
- `CHECKPOINT.md` — updated after every phase.

All analysis code lives in scripts/notebooks under
`tutorials/final_baseline_rtdetr/` importing `pi_multimodal_ad.models.rtdetr_detection`
and (for the activation-hook step only) `tutorials/rtdetr_storybook/rtdetr_storybook.py`;
nothing under `src/`, `scripts/`, `configs/`, or `runs/` is modified.

## Next action

Proceed to Phase 2: materialize a read-only view of the split (counts, box
counts, box-size distribution per split, with the view_role composition
shift quantified), write the data-summary table, then move directly to
Phase 4 (Phase 3 skipped per the Phase 0 decision).
