# PHM North America 2026 — professor-facing dataset description

This report is generated only from exact, hash-pinned D1.1–D1.4 profiling artifacts. It does not rescan PHM archives, inspect Intel data, construct a target, or create a training sample.

## 1. Scope and inventory

In-scope experiments and filename-level runs are EXP-A (1, 2, 3, 4, 5), EXP-B (1, 2, 3, 4, 5, 6, 7), and EXP-F (1, 2, 3, 4, 5, 6, 7, 8).
The complete central-directory inventory found 52 readable ZIP archives, 8,512 central-directory members, and 40 nested ZIP members. It recorded 0 missing expected assets and 0 unreadable archives, alongside 13 warnings. Source: run `20260813T202043619114Z-ad7f9832`, `reports/summary.json` (SHA-256 `f5db7f36aef8d9b86908388a48799024e9ac97d160a6b6d132c5fcebcdf0a013`).
The inventory records 622 CRC32-plus-size candidate rows, but these are lightweight candidates rather than confirmed duplicate payloads; exact central-directory metadata duplicate rows were 0. Source: run `20260813T202043619114Z-ad7f9832`, `reports/summary.json` (SHA-256 `f5db7f36aef8d9b86908388a48799024e9ac97d160a6b6d132c5fcebcdf0a013`).
The bounded sensor profile retained 446 internal run-token conflicts as warnings; it did not rename, remove, or merge any raw member. Source: run `20260813T212734652736Z-f7c665fd`, `reports/sensor_summary.json` (SHA-256 `1e3bb106e94ab873b5ed601fc76a767ad95e793b498bce680301457961df4654`).

## 2. Sensor description

D1.2 inspected 745 HDF5 members and produced 27,165 dataset rows; all 745 inspected representative members were readable. It observed 13 file-schema variants and 12 exact shape families. Source: run `20260813T212734652736Z-f7c665fd`, `reports/sensor_summary.json` (SHA-256 `1e3bb106e94ab873b5ed601fc76a767ad95e793b498bce680301457961df4654`); shape evidence: run `20260813T212734652736Z-f7c665fd`, `reports/hdf5_schema.json` (SHA-256 `cb678d869843ede481677753b1b9e7e4010beac2ced96d36dfdf2d6c68910237`).
Observed dtypes were float32, float64, uint16. Evidenced sampling-rate families included 0.25 Hz, 1 Hz, 100,000 Hz, and approximately 102,400 Hz. Observed role counts include vibration, operating context, condition indicator, and unknown paths; oil/environment should not be claimed beyond rows actually profiled. Representative durations with time evidence ranged from 6e-05 to 60.0 seconds (median 60.0 seconds). Source: run `20260813T212734652736Z-f7c665fd`, `reports/sensor_summary.json` (SHA-256 `1e3bb106e94ab873b5ed601fc76a767ad95e793b498bce680301457961df4654`).

> Sensor structural findings are based on bounded representative EXP-A Run-1 coverage and are not an exhaustive schema confirmation across every EXP-A/B/F archive.

## 3. Image description

The complete header profile contains 1,311 images: EXP-A 455, EXP-B 576, and EXP-F 280. All 1,311 headers were readable. The observed structural schema is uniform: 1440 × 2560 × 3, RGB, uint8, 8-bit JPEG. Source: run `20260813T215718624432Z-bd9395ad`, `reports/image_summary.json` (SHA-256 `d9f6807b34b19a68383f934727eefdaaeefe5fc39415f1c3b4593d7c19174649`).
The deterministic sampled-quality pass decoded 104 images, with 104 successful pixel reads. It found no exact SHA-256 duplicate group among the 104 hash-covered images and 127 dHash near-duplicate candidate pairs. These candidates are not semantic or dataset-wide duplicate proof. Source: run `20260813T215756728445Z-bd9395ad`, `reports/image_summary.json` (SHA-256 `91a759f44eb29f68912938f4d2c8f78f33ecf9f95c9413dabff46aae9e88eda8`).
No bounding-box, mask, keypoint, continuous-target, or verified image-level damage-label sidecar was discovered in the bounded photo-archive listing. This is listing evidence, not proof that undocumented external annotations do not exist. Complete header coverage and sampled pixel-quality coverage are distinct.

## 4. Cross-modal clock audit

Verified UTC image timestamps: 0; timezone-unknown local-naive image timestamps: 640; missing image timestamps: 671. Where sensor timestamps were evidenced, D1.2/D1.4 records the UTC-compatible sensor clock domain `phm_hdf5_explicit_utc`. Source: run `20260813T223944047252Z-d6474ff4`, `reports/alignment_blockers.json` (SHA-256 `f774ecea6dc00129561092843ab188570590d6b7261e38ca49df896b9b9d3341`).
D1.4 classification: **PARTIALLY_COMPLETE_BLOCKED_BY_UNVERIFIED_IMAGE_CLOCK_DOMAIN**. Image–sensor timestamps are comparable: False; nearest temporal matching is authorized: False; join cardinality is computable: False; six-hour cross-modal cadence: UNRESOLVED. Assigning a timezone by assumption could shift photographs by hours and create false image–sensor pairs. Source: run `20260813T223944047252Z-d6474ff4`, `reports/alignment_blockers.json` (SHA-256 `f774ecea6dc00129561092843ab188570590d6b7261e38ca49df896b9b9d3341`).

## 5. Blocked traceability example

**Illustrative traceability record — not a valid aligned training sample.**

| schema_version | record_label | experiment | run | image_id | image_source_relative_path | image_timestamp_status | image_timestamp_raw_or_local_naive | sensor_event_id | sensor_source_identity | sensor_timestamp_utc | sensor_clock_domain | clock_domain_compatible | alignment_result | required_to_unblock |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.0.0 | Illustrative traceability record — not a valid aligned training sample. | EXP-A | 1 | image_profile_e571434bf519386598ae61e77c92e42bde69c740bffcd03c2aee4a27172e81de | photos/EXP-A/Exp-A_Photos_Run-1.zip!Run 1/All Teeth/Tooth 09.jpg | missing | UNKNOWN | canonical_event_000ca3f7fd9c8fcc070ef147a03e05c2b2e3b7a3ce8a1548152400d6253f6d83 | LF_Dyno Gear233Run1_00115.hdf5 | 2024-09-16T16:13:38.205228+00:00 | phm_hdf5_explicit_utc | False | NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED | ["authoritative timezone for camera filename timestamps","evidence of camera/sensor clock synchronization or documented offset/drift","an authoritative non-temporal image-to-sensor pairing key if clocks are not comparable","scalar target definition including unit, timestamp, and six-hour interpretation"] |

The image and sensor identities above are genuine generated-artifact references, but no time delta, candidate target, or training sample was produced. Source: run `20260813T223944047252Z-d6474ff4`, `tables/candidate_sample_traces.parquet` (SHA-256 `6957fc36e954462542d9064c27ce6c92f0277ae9069eb5a526dde8663491c65c`).

## 6. Model-readiness implications

- **RT-DETR:** images have a consistent usable structural format, but no bounding-box annotations were discovered. Standard supervised RT-DETR object-detection training is therefore not supported by the discovered annotations. RT-DETR-derived image regression remains possible only after a defensible image-to-target mapping is defined.
- **PatchTST:** sensor structures and sampling-rate families have been identified representatively. Complete cross-experiment schema validation remains limited. PatchTST window construction cannot be finalized until the target, forecast horizon, and six-hour interpretation are confirmed.
- **Multimodal modelling:** image–sensor fusion is blocked until clock-domain alignment is resolved or an authoritative non-temporal pairing key is identified.

## 7. Questions for the professor or dataset provider

1. What exact scalar should be predicted?
2. Does six hours represent observation cadence, input history, or forecast horizon?
3. Are image timestamps expressed in UTC or another timezone?
4. Was the camera clock synchronized with the sensor acquisition system?
5. Is there a known clock offset or drift?
6. Is there an authoritative inspection/run/tooth identifier connecting images and sensor observations?
7. Are bounding boxes, damage labels, masks, or quantitative tooth-damage measurements available elsewhere?
8. Is representative sensor schema coverage sufficient for the next meeting, or should a broader stratified scan be performed?

## Evidence and limitations

All numerical claims cite exact source runs and generated artifact hashes in `tables/artifact_source_index.csv`. Run and lifecycle labels are not health or damage labels. No causal degradation claim, target selection, interpolation, raw-data modification, or model implementation is included.
