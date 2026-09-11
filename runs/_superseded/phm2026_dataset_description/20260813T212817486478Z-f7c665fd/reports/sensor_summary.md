# HDF5 and sensor profile

Schema version: `1.0.0`
Mode: `sampled`

Each HDF5 member was materialized one at a time in a unique temporary directory and removed after inspection. No permanent extraction occurred.

## Coverage

- Selected D1.1 source rows: 1
- Profiled HDF5 members: 1
- Readable members: 1
- Unreadable members: 0
- HDF5 datasets: 83
- Unknown/unmapped paths: 24
- Timestamped datasets: 83

## Channels by experiment and run

| Experiment/run | Role counts |
|---|---|
| EXP-A/run-1 | condition_indicator: 51, operating_context: 5, unknown: 24, vibration: 3 |

## Exact array shapes

| Shape | Dataset rows |
|---|---:|
| `[1]` | 16 |
| `[24,4096]` | 4 |
| `[2457600]` | 3 |
| `[24]` | 31 |
| `[6,4096]` | 4 |
| `[6]` | 25 |

## Dtypes

| Dtype | Dataset rows |
|---|---:|
| `float32` | 8 |
| `float64` | 59 |
| `uint16` | 16 |

## Sampling-frequency and duration evidence

- Evidenced sampling-rate rows: 67
- Sampling rates (Hz): `{"0.25": 28, "1.0": 34, "100000.0": 2, "102400.00000000048": 3}`
- Evidence sources: `{"dataset_attribute:fs": 2, "derived:1/dataset_attribute:wf_increment": 65}`
- Evidenced durations: 67
- Duration min/median/max seconds: 6e-05 / 24.0 / 24.0

## Schema and coverage warnings

- File schema variants: 1
- Distinct HDF5 dataset paths: 83
- Variable path schemas: `{}`
- Missing expected paths: `{}`
- Unknown paths: `{"/DM4500 Data/DM4500 Bin 0": 1, "/DM4500 Data/DM4500 Bin 1": 1, "/DM4500 Data/DM4500 Bin 2": 1, "/DM4500 Data/DM4500 Bin 3": 1, "/DM4500 Data/DM4500 Bin 4": 1, "/DM4500 Data/DM4500 Bin 5": 1, "/DM4500 Data/DM4500 Bin 6": 1, "/DM4500 Data/DM4500 Bin 7": 1, "/ICM2 Data/ICM2 Bin 0": 1, "/ICM2 Data/ICM2 Bin 1": 1, "/ICM2 Data/ICM2 Bin 2": 1, "/ICM2 Data/ICM2 Bin 3": 1, "/ICM2 Data/ICM2 Bin 4": 1, "/ICM2 Data/ICM2 Bin 5": 1, "/ICM2 Data/ICM2 Bin 6": 1, "/ICM2 Data/ICM2 Bin 7": 1, "/Transforms/TSA": 1, "/Transforms/difference": 1, "/Transforms/e_op": 1, "/Transforms/residual": 1, "/Transforms_4s/TSA": 1, "/Transforms_4s/difference": 1, "/Transforms_4s/e_op": 1, "/Transforms_4s/residual": 1}`
- Run-token conflicts: 0
- Conflict sources: `[]`
- Unreadable sources: `[]`

## Limitations

- Metadata mode does not read array values; statistics and value-quality counts remain null.
- Sampled statistics describe only deterministic sampled values and do not prove whole-array constancy or extrema.
- Full statistics are chunk-bounded but are not run without an explicit positive source limit.
- A missing expected path is a coverage warning, not evidence of corruption.
- Sampling rates and UTC timestamps are recorded only when supported by attributes; no historical 102,400 Hz fallback is applied.
- Internal run tokens remain separate from authoritative archive or nested-archive run identity.
- For rank greater than one, sample count uses axis 0 and channel count uses the product of remaining axes; this layout inference must be reviewed for unknown transforms.
