# PHM 2026 asset inventory

Schema version: `1.0.0`

This report inventories filesystem metadata and ZIP central directories only. No archive member was extracted, decompressed, or payload-hashed.

## Totals

- Discovered files: 52
- Profiled files: 2
- ZIP archives: 2
- Archive members: 744
- Outer compressed bytes: 41617088475
- Member uncompressed bytes: 61949223304
- Nested ZIP members: 0
- Missing expected combinations: 0
- Issues: 0 errors, 2 warnings, 0 informational

## Experiment, run, and modality totals

| Experiment | Run | Modality | Archives | Bytes | Members | Uncompressed member bytes |
|---|---:|---|---:|---:|---:|---:|
| EXP-A | 1 | high_frequency | 1 | 20807599520 | 372 | 30973891556 |
| EXP-A | 2 | high_frequency | 1 | 20809488955 | 372 | 30975331748 |

## Duplicate evidence

- Rows in CRC32 + uncompressed-size candidate groups: 622
- Repeated identical central-directory member rows: 0
- CRC32 evidence is lightweight and is not cryptographic proof of equal payloads.

## Issues

| Severity | Code | Path | Message |
|---|---|---|---|
| warning | member_archive_run_conflict | high_frequency/EXP A/Exp-A_HDF5_Run-1.zip | 223 member name(s) encode a run different from archive run 1; archive scope was retained. Examples: 'Run-1/Dyno Gear233Run2_00000.hdf5', 'Run-1/Dyno Gear233Run2_00001.hdf5', 'Run-1/Dyno Gear233Run2_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP A/Exp-A_HDF5_Run-2.zip | 149 member name(s) encode a run different from archive run 2; archive scope was retained. Examples: 'Run-2/Dyno Gear233Run1_00000.hdf5', 'Run-2/Dyno Gear233Run1_00001.hdf5', 'Run-2/Dyno Gear233Run1_00002.hdf5' |
