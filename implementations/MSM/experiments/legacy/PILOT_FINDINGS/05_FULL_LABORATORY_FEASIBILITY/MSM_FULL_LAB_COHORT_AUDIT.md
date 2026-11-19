# Full MSM laboratory cohort audit

**CONDITIONAL GO for further research preparation; full evaluation awaits visibility, target and physical-group approval.** No model was trained, no full CNN feature bank was extracted and no F2 evaluation was run.

Dataset `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2` (ID 8392825), [official dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), [publication](https://www.nature.com/articles/s41597-026-07255-7). Version 2 was reverified against the official public API and all 481 paths/sizes match Stage 1. All native labels and historical outputs were preserved.


Acquired **204 files / 2,533,736,741 bytes (2.533736741 GB decimal)** and reused 22 matching files in the 226-file minimal plan. No planned file remains missing or failed. One public request timed out and was safely retried; its failure receipt is preserved. The 2.7 GB budget and 10 GiB reserve gates passed; final disk free was 72.28 GiB. All 56 laboratory MP4, MTC, S2 and NC sets plus two XML files are present. The original labels/workbook were reused. No additional ACC, industrial video, S0 microphone or full archive was downloaded. Acquisition receipts and official inventory: [20261027T013606719154Z-stage5-full-lab](../20261027T013606719154Z-stage5-full-lab). Exact status and hashes: `MSM_DOWNLOAD_MANIFEST.csv`.

Native laboratory total: **2,512 intervals = 1,877 label 0 + 458 label 1 + 177 label 2**, 56 nominal folders, 25 positive-containing folders. Native meanings: stable normal (0), intervention-worthy abnormal cutting (1), stable cutting with a defective tool (2). Folder remarks are never used as ground truth.

| Machine | Native 0 / 1 / 2 | Joint 0 / 1 / 2 | Joint intervals | Joint folders / positive folders |
| --- | --- | --- | --- | --- |
| imi_vm20i | 1173 / 325 / 87 | 854 / 238 / 68 | 1160 | 27 / 11 |
| imi_vmx30ui | 704 / 133 / 90 | 580 / 98 / 57 | 735 | 18 / 6 |

| Gate | Intervals |
| --- | --- |
| Accepted recording alignment | 2381 |
| Video + exact 16 frames | 1924 |
| Common MTC | 2448 |
| Joint technical | 1895 |
| Joint independent visibility pending | 1895 |

The joint technical cohort contains **1895 cuts**, with 1434 label 0, 336 label 1 and 125 label 2. These are technical candidates, not independently visibility-certified examples. Positive prevalence under the frozen 1-versus-0/2 task is 17.7309%. Excluded native cuts: 617. Gate denominators are separate and exclusion reasons can overlap.

| Reason (nonexclusive) | Intervals |
| --- | --- |
| alignment_rejected:ambiguous_equal_calibration_consensus | 64 |
| alignment_rejected:insufficient_validation_support | 66 |
| alignment_rejected:no_calibration_anchors | 1 |
| fewer_than_16_distinct_native_frames | 13 |
| insufficient_mtc_rows | 21 |
| mtc_time_gap_exceeds_0.5s | 48 |
| outside_validated_audio_support | 444 |

The original 114 joint pilot examples were retained, with the final +49.73 s VMX9 mapping. No pilot GPU or visual-review experiment was repeated. New clips use one forward native video decode; small representative contacts are recorded for all experiments, including eligible positive sequences where available. Five previous pilot atlases are indexed rather than regenerated.

The sensor contract remains 15 ordered numerical signals × six statistics = 90. No interpolation, label metadata, program/tool identifiers, raw ACC substitution or statistical redefinition. All finite, >=5-row and <=0.5 s edge-inclusive coverage gates were applied. MTC held values do not represent fresh high-frequency measurements; unknown aggregation latency limits this to retrospective coarse cutting intervals. Per-channel missing/held fractions and clocks are in `manifests/sensor_schema_audit.json`.

## Every experiment

Alignment counts mean intervals in recordings with accepted timing, not automatic interval support. Pending visibility counts refer to frame-valid intervals. Independent visual judgement is still pending even where the earlier Codex coarse-context review exists. Complete row-level source identities and exclusion reasons are in `MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv`; exact selected frame PTS/content hashes in `manifests/selected_frame_manifest.csv`.

| Experiment | Native 0/1/2 | Alignment | 16 frames | MTC | Joint 0/1/2 | Visibility pending |
| --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | 0/12/0 | 12 | 8 | 12 | 0/8/0 | 8 |
| imi_vm20i/dataset10 | 64/0/0 | 64 | 17 | 63 | 17/0/0 | 17 |
| imi_vm20i/dataset11 | 64/0/0 | 64 | 53 | 64 | 53/0/0 | 53 |
| imi_vm20i/dataset12 | 64/0/0 | 0 | 0 | 63 | 0/0/0 | 0 |
| imi_vm20i/dataset13 | 64/0/0 | 64 | 64 | 62 | 62/0/0 | 64 |
| imi_vm20i/dataset14 | 64/0/0 | 64 | 56 | 62 | 55/0/0 | 56 |
| imi_vm20i/dataset15 | 5/4/0 | 0 | 0 | 2 | 0/0/0 | 0 |
| imi_vm20i/dataset16 | 44/20/0 | 64 | 59 | 62 | 39/18/0 | 59 |
| imi_vm20i/dataset17 | 6/1/0 | 0 | 0 | 7 | 0/0/0 | 0 |
| imi_vm20i/dataset18 | 6/1/0 | 0 | 0 | 7 | 0/0/0 | 0 |
| imi_vm20i/dataset19 | 19/0/0 | 19 | 19 | 18 | 18/0/0 | 19 |
| imi_vm20i/dataset2 | 0/0/18 | 0 | 0 | 17 | 0/0/0 | 0 |
| imi_vm20i/dataset20 | 64/0/0 | 64 | 64 | 64 | 64/0/0 | 64 |
| imi_vm20i/dataset21 | 64/0/0 | 64 | 62 | 64 | 62/0/0 | 62 |
| imi_vm20i/dataset22 | 0/1/0 | 0 | 0 | 1 | 0/0/0 | 0 |
| imi_vm20i/dataset23 | 64/0/0 | 64 | 20 | 62 | 20/0/0 | 20 |
| imi_vm20i/dataset24 | 0/64/0 | 64 | 55 | 64 | 0/55/0 | 55 |
| imi_vm20i/dataset25 | 8/56/0 | 64 | 47 | 63 | 4/43/0 | 47 |
| imi_vm20i/dataset26 | 0/19/45 | 64 | 64 | 64 | 0/19/45 | 64 |
| imi_vm20i/dataset27 | 39/25/0 | 64 | 64 | 64 | 39/25/0 | 64 |
| imi_vm20i/dataset28 | 44/20/0 | 64 | 24 | 64 | 15/9/0 | 24 |
| imi_vm20i/dataset29 | 18/46/0 | 64 | 39 | 62 | 8/30/0 | 39 |
| imi_vm20i/dataset3 | 0/0/12 | 12 | 12 | 12 | 0/0/12 | 12 |
| imi_vm20i/dataset30 | 40/24/0 | 64 | 24 | 64 | 9/15/0 | 24 |
| imi_vm20i/dataset31 | 64/0/0 | 64 | 61 | 64 | 61/0/0 | 61 |
| imi_vm20i/dataset32 | 64/0/0 | 64 | 63 | 63 | 63/0/0 | 63 |
| imi_vm20i/dataset33 | 0/1/0 | 0 | 0 | 1 | 0/0/0 | 0 |
| imi_vm20i/dataset34 | 64/0/0 | 64 | 59 | 64 | 59/0/0 | 59 |
| imi_vm20i/dataset35 | 64/0/0 | 64 | 64 | 64 | 64/0/0 | 64 |
| imi_vm20i/dataset36 | 64/0/0 | 64 | 60 | 63 | 59/0/0 | 60 |
| imi_vm20i/dataset37 | 64/0/0 | 64 | 64 | 64 | 64/0/0 | 64 |
| imi_vm20i/dataset4 | 0/0/12 | 12 | 12 | 11 | 0/0/11 | 12 |
| imi_vm20i/dataset5 | 4/5/0 | 9 | 7 | 9 | 3/4/0 | 7 |
| imi_vm20i/dataset6 | 44/20/0 | 64 | 28 | 64 | 16/12/0 | 28 |
| imi_vm20i/dataset7 | 0/1/0 | 0 | 0 | 1 | 0/0/0 | 0 |
| imi_vm20i/dataset8 | 0/1/0 | 0 | 0 | 1 | 0/0/0 | 0 |
| imi_vm20i/dataset9 | 0/4/0 | 0 | 0 | 4 | 0/0/0 | 0 |
| imi_vmx30ui/dataset1 | 0/0/18 | 0 | 0 | 7 | 0/0/0 | 0 |
| imi_vmx30ui/dataset10 | 64/0/0 | 64 | 64 | 63 | 63/0/0 | 64 |
| imi_vmx30ui/dataset11 | 64/0/0 | 64 | 56 | 63 | 55/0/0 | 56 |
| imi_vmx30ui/dataset12 | 64/0/0 | 64 | 49 | 64 | 49/0/0 | 49 |
| imi_vmx30ui/dataset13 | 64/0/0 | 64 | 48 | 64 | 48/0/0 | 48 |
| imi_vmx30ui/dataset14 | 16/48/0 | 64 | 38 | 61 | 3/33/0 | 38 |
| imi_vmx30ui/dataset15 | 10/54/0 | 64 | 51 | 61 | 5/44/0 | 51 |
| imi_vmx30ui/dataset16 | 64/0/0 | 64 | 55 | 62 | 53/0/0 | 55 |
| imi_vmx30ui/dataset17 | 26/1/0 | 27 | 25 | 27 | 24/1/0 | 25 |
| imi_vmx30ui/dataset18 | 64/0/0 | 64 | 64 | 64 | 64/0/0 | 64 |
| imi_vmx30ui/dataset19 | 0/16/48 | 64 | 52 | 57 | 0/14/36 | 52 |
| imi_vmx30ui/dataset2 | 0/0/12 | 12 | 12 | 12 | 0/0/12 | 12 |
| imi_vmx30ui/dataset3 | 0/0/12 | 12 | 12 | 9 | 0/0/9 | 12 |
| imi_vmx30ui/dataset4 | 0/12/0 | 12 | 10 | 6 | 0/4/0 | 10 |
| imi_vmx30ui/dataset5 | 64/0/0 | 64 | 17 | 63 | 17/0/0 | 17 |
| imi_vmx30ui/dataset6 | 64/0/0 | 64 | 64 | 63 | 63/0/0 | 64 |
| imi_vmx30ui/dataset7 | 64/0/0 | 64 | 61 | 64 | 61/0/0 | 61 |
| imi_vmx30ui/dataset8 | 64/0/0 | 64 | 64 | 64 | 64/0/0 | 64 |
| imi_vmx30ui/dataset9 | 12/2/0 | 14 | 13 | 14 | 11/2/0 | 13 |

## Reproducibility

Independent data-side validation rechecked 280 experiment input hashes, all 56 original laboratory label hashes, all 2,512 native source rows, 1924 exact frame policies and 2448 actual sensor vectors. Maximum float32 feature difference: 0.0. 175 historical run files match their saved manifests. Source/config/tests, failure records and software identities are retained in this delivery. New raw files stay Git-ignored; no staging/commit occurred.
