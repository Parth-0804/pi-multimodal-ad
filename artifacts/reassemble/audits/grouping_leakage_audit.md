# Grouping and leakage audit

All 149 source recordings have unique full-file SHA256 hashes. No identical
combined primary-sensor segment hashes cross recordings. Absolute sensor
acquisition intervals do not overlap across recordings. The official project
describes each H5 as one trial; no evidence requires a higher grouping unit.
Same-day acquisition conditions remain a limitation of recording-disjoint claims.

Primary cohort: 148 recordings; nested 5 outer / 4 inner folds, seed 20260927.
Every train/validation/test boundary is recording-disjoint and both labels occur
in every assessment partition.

| Outer fold | Training recordings | Test recordings | Test segments | Test failures |
| --- | --- | --- | --- | --- |
| 0 | 122 | 26 | 753 | 77 |
| 1 | 117 | 31 | 964 | 109 |
| 2 | 116 | 32 | 1037 | 125 |
| 3 | 119 | 29 | 906 | 99 |
| 4 | 118 | 30 | 870 | 99 |

The official split contains 111 training and 37 test recordings, with no overlap
or unknown filenames. It omits `2025-01-10-16-17-40`.
It is eligible only as a secondary evaluation of its listed subset; it does not
define the primary nested folds or justify dropping other recordings.

Predictor-field allowlisting is regression-tested. Recording IDs, absolute time,
segment IDs, free text, object strings and labels are not approved predictors.
No models have been trained; this is a data/split readiness PASS, not a validation
of future training implementations. Normalization, calibration, thresholds and
fusion fitting must still remain inside inner/training folds.

Primary-cohort exclusions: 21 segments (7 failures).
Of these, 9 lack usable selected video and 13 lack usable selected sensors (categories may overlap).
All original rows remain in segments.parquet; exclusion details are in
`runs/reassemble/20260927T141645Z-inventory/tables_v2/cohort_exclusions.parquet`.
