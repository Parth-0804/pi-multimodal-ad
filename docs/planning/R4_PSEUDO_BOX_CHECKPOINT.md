# R4 pseudo-box checkpoint

Status: **COMPLETE — PROVISIONAL ENGINEERING LABELS, HUMAN REVIEW PENDING**  
Evidence date: 2026-08-14  
Canonical run: `20260814T040854991567Z-3fa0f794`

## Purpose and scientific status

The PHM archives provide no organizer damage boxes. This stage deterministically
replayed the versioned `phm2026_image_damage_v2` candidate masks within the
visible-flank ROI, filtered connected components, and converted retained
components to tight one-class boxes named `damage_candidate`.

These boxes are **pseudo-boxes**, not physical-damage ground truth. They measure
agreement with the provisional image heuristic. Expert review of masks and
boxes remains required before making a physical spall claim.

## Pinned input and output

- Input target/mask run: `20260814T012054997053Z-e195f6d9`.
- Configuration hash: `3fa0f794722a1216a1dc77c290b9a134bb899024213b51ed6d432c2695c94e42`.
- Output directory:
  `runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794/`.
- Output manifest SHA-256:
  `6bff0d8eea1d31ab7bbcb6cba00a817f9b171b76ba88f1d3043b22331c1b8024`.

Primary pinned artifacts:

- `tables/annotation_image_manifest.parquet` —
  `2ad4251a856757426aa75c7e9785ca7fbcd70edd6c2ebfd98be00e34661ccb87`;
- `tables/annotation_manifest.parquet` —
  `42d43c2ed35026853a1eee54922e55ed6b93c1eae52cbe308b248f251e381641`;
- `tables/coco_annotations.json` —
  `738627b858940550b1f73f78e6d59e4bc733e76a20853e043ae9bea7ea9ccd12`;
- `manifests/materialized_cache.parquet` —
  `14f080a1c98d7ec21d3b9fc1fc83609ce2ca29d230c988a4834fd2456e7b5595`;
- `reports/annotation_quality.json` —
  `dba902e14bda7f96fdd93288ce377e799f4cadfad7a699d5ef5328c1a77b0cc4`.

## Quality-gate result

- 995/995 pinned model samples resolved and were materialized once in a
  versioned ignored cache (493,282,436 bytes including labels).
- Split was unchanged: EXP-B/train 448, EXP-A/validation 323, EXP-F/test 224.
- 30,628 valid retained pseudo-boxes; all boxes passed image/ROI bounds checks.
- 995 positive images and 0 negative images under this heuristic.
- Zero replay differences from the versioned candidate-mask target values.
- Whole-ROI box fraction: 0.0.
- EXP-F was not used for threshold or component-parameter selection.

The gate status is
`PROVISIONAL_PSEUDO_BOXES_FOR_ENGINEERING_BASELINE`. The all-positive outcome
and high component count are important limitations: many boxes represent small
surface/texture candidates, and absence of a box is not established as an
authoritative negative label.

## Review and figures

The canonical run contains COCO JSON, Ultralytics labels, every retained and
rejected component, a human-review queue, a review guide, deterministic contact
sheets, box-count/area plots, and the 1,311 → 995 → 560 → 20 evidence funnel.
No source archive was modified or extracted in place.

