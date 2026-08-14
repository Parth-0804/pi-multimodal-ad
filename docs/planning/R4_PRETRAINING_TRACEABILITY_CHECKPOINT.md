# R4 pre-training traceability checkpoint

Status: **TRACEABILITY_GATE_PASSED; PSEUDO-BOX QUALITY GATE PENDING**  
Evidence date: 2026-08-14  
Git baseline: `d3ce4808abfa8abb0aaad58d7b458defd0c7c5d0`

## Pinned upstream evidence

| Stage | Run ID | Primary pinned artifact | SHA-256 |
|---|---|---|---|
| Canonical image target | `20260814T012054997053Z-e195f6d9` | `tables/image_manifest.parquet` | `970eb991fb425f46c188658f4a4c28a2414d68aed27bb71e3ea53ee573667e0f` |
| T2.2 samples | `20260814T013357354377Z-6b068cab` | `tables/model_sample_manifest.parquet` | `8cc50418016ce5fd492ae973c99549c538971a382b74db17f52c6aa9968b2144` |
| T2.2 splits | `20260814T013357354377Z-6b068cab` | `tables/split_manifest.parquet` | `6463b00cafa8785708b1a32b13901077f7b9eef1e177c54f7fc6e0a6137d4359` |
| T2.3 naive baseline | `20260814T015914190145Z-4423f1fa` | `tables/baseline_metrics.parquet` | `9f9c9a8bbbba5d23da7a3ae09d9dff094b6b6fd5809bfdf55eac51fe8bbd9539` |
| Existing frozen-encoder regression | `20260814T020338751021Z-d0f225c8` | `manifests/outputs.json` | `bd3ae8a517333a600d9ddc4855ef2af1bc83fba18390c4f8062f40933713a5c1` |
| Final R3 result package | `20260814T021150456003Z-d15163e7` | `manifests/outputs.json` | `e8ad88f8f8f4afcbdecfb0d2e89e80b96bb4a6d84a9fdc4fbb768dbab518c528` |

All paths are repository-relative and all upstream runs are immutable inputs to
R4. No “latest run” lookup is permitted.

## Exact funnel and target contract

- Source images: **1,311** decoded JPEG records.
- Post-run model samples: **995** image views.
- Experiment/run/tooth records: **560** (`20 runs × 28 teeth`).
- Run targets: **20**.
- Existing RT-DETR regression target column: `per_image_damage_candidate_pct`,
  in provisional percentage points of the fixed visible-flank ROI.
- View-to-tooth aggregation: maximum candidate-area ratio, with a stable
  image-ID tie break.
- Tooth-to-run aggregation: arithmetic mean of the three largest tooth values.
  The causal monotonic alternative is the within-experiment cumulative maximum
  of that raw top-3 mean.

The count reductions are evidence-based:

1. `1,311 → 995`: exclude 316 non-run inspection images (test-start/pre-run and
   break-in); all post-run images remain.
2. `995 → 560`: preserve multiple EXP-A/B camera close-ups as separate model
   views, then aggregate views sharing experiment/run/tooth. EXP-F has one
   canonical view per tooth. EXP-A Run 5 has 67 views; other EXP-A/B runs have
   64; every EXP-F run has 28.
3. `560 → 20`: aggregate exactly 28 tooth records for each of the 20 in-scope
   experiment/run inspections.

## Frozen experiment-level split

| Split | Experiment | Samples |
|---|---|---:|
| train | EXP-B | 448 |
| validation | EXP-A | 323 |
| test | EXP-F | 224 |

The persisted T2.2 validation reports zero run/tooth-group and near-duplicate
cross-split violations. R4 must consume these assignments exactly. EXP-F may
not influence pseudo-box thresholds, model selection, confidence threshold or
early stopping.

## Scientific label boundary

The organizer provides no participant-visible damage boxes. R4 may create only
`damage_candidate` pseudo-boxes by replaying the exact hash-pinned v2 mask
algorithm and configuration. The canonical target run persisted overlays and
measurements, but not standalone binary mask files. Therefore R4 must:

1. reproduce each selected mask from the immutable source image with the exact
   v2 ROI and algorithm;
2. verify reproduced candidate pixels/ratio against the pinned image manifest;
3. derive boxes only after exact agreement;
4. retain zero-box negatives; and
5. report all detection metrics as pseudo-label agreement, never physical
   damage validation.

Any mask replay mismatch or systematically degenerate box distribution blocks
training.

## Resource preflight

- Free disk: **79,748,640,768 bytes** at the gate (minimum required: 50 GB).
- Existing `runs/`: **1,593,352,810 bytes**.
- Immutable PHM baseline: **52 ZIP files / 381,481,906,106 bytes**.
- GPU: NVIDIA Tesla T4, 16,384 MiB total, 15,930 MiB free at preflight.
- Runtime: PyTorch `2.13.0+cu130`, CUDA `13.0`, Ultralytics `8.4.104`,
  OpenCV `5.0.0`, Transformers `5.14.1`.

One bounded materialized JPEG cache for the 995 selected images is permitted
only if projected free space remains above 50 GB. Raw archives and historical
outputs remain immutable.
