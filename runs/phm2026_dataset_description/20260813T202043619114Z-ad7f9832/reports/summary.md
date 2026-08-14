# PHM 2026 asset inventory

Schema version: `1.0.0`

This report inventories filesystem metadata and ZIP central directories only. No archive member was extracted, decompressed, or payload-hashed.

## Totals

- Discovered files: 52
- Profiled files: 52
- ZIP archives: 52
- Archive members: 8512
- Outer compressed bytes: 381481906106
- Member uncompressed bytes: 573234365197
- Nested ZIP members: 40
- Missing expected combinations: 0
- Issues: 0 errors, 13 warnings, 0 informational

## Experiment, run, and modality totals

| Experiment | Run | Modality | Archives | Bytes | Members | Uncompressed member bytes |
|---|---:|---|---:|---:|---:|---:|
| EXP-A | 1 | high_frequency | 1 | 20807599520 | 372 | 30973891556 |
| EXP-A | 1 | image | 1 | 30394169 | 66 | 31260655 |
| EXP-A | 2 | high_frequency | 1 | 20809488955 | 372 | 30975331748 |
| EXP-A | 2 | image | 1 | 30070957 | 64 | 30893876 |
| EXP-A | 3 | high_frequency | 1 | 20687254473 | 371 | 31013456360 |
| EXP-A | 3 | image | 1 | 28302619 | 69 | 29225651 |
| EXP-A | 4 | high_frequency | 1 | 19026810876 | 341 | 28586677728 |
| EXP-A | 4 | image | 1 | 30058082 | 66 | 30958491 |
| EXP-A | 5 | high_frequency | 1 | 20973857618 | 377 | 31938515728 |
| EXP-A | 5 | image | 1 | 31878952 | 68 | 32814260 |
| EXP-A | aggregate | condition_indicator | 1 | 22538230 | 5 | 22677601 |
| EXP-A | aggregate | image | 2 | 59971491 | 136 | 61798874 |
| EXP-A | aggregate | low_frequency | 1 | 30482546 | 5 | 30654419 |
| EXP-B | 1 | high_frequency | 1 | 20638664348 | 372 | 30974825568 |
| EXP-B | 1 | image | 1 | 31524002 | 65 | 32394264 |
| EXP-B | 2 | high_frequency | 1 | 20697314116 | 372 | 30992838168 |
| EXP-B | 2 | image | 1 | 30488806 | 65 | 31353290 |
| EXP-B | 3 | high_frequency | 1 | 20661623508 | 371 | 30992657392 |
| EXP-B | 3 | image | 1 | 31247865 | 69 | 32156012 |
| EXP-B | 4 | high_frequency | 1 | 20637642166 | 372 | 31053377088 |
| EXP-B | 4 | image | 1 | 30697747 | 65 | 31538586 |
| EXP-B | 5 | high_frequency | 1 | 20672046928 | 371 | 31011338496 |
| EXP-B | 5 | image | 1 | 32945504 | 65 | 33796273 |
| EXP-B | 6 | high_frequency | 1 | 20657664574 | 372 | 30981021808 |
| EXP-B | 6 | image | 1 | 31976429 | 65 | 32824586 |
| EXP-B | 7 | high_frequency | 1 | 7992390098 | 145 | 12057086100 |
| EXP-B | 7 | image | 1 | 31506902 | 65 | 32383357 |
| EXP-B | aggregate | condition_indicator | 1 | 29290956 | 7 | 29476226 |
| EXP-B | aggregate | image | 2 | 62986034 | 130 | 64688896 |
| EXP-B | aggregate | low_frequency | 1 | 39503931 | 7 | 39716126 |
| EXP-F | 1 | high_frequency | 1 | 20595148449 | 373 | 31044145248 |
| EXP-F | 1 | image | 1 | 13509784 | 29 | 13903800 |
| EXP-F | 2 | high_frequency | 1 | 19975424912 | 445 | 30100377796 |
| EXP-F | 2 | image | 1 | 13951041 | 29 | 14339047 |
| EXP-F | 3 | high_frequency | 1 | 20602084592 | 372 | 31004906688 |
| EXP-F | 3 | image | 1 | 13116675 | 29 | 13529187 |
| EXP-F | 4 | high_frequency | 1 | 19192542102 | 528 | 29015127600 |
| EXP-F | 4 | image | 1 | 13861174 | 29 | 14251125 |
| EXP-F | 5 | high_frequency | 1 | 20861336445 | 382 | 31633914924 |
| EXP-F | 5 | image | 1 | 14302292 | 29 | 14691954 |
| EXP-F | 6 | high_frequency | 1 | 20599133224 | 371 | 31004214516 |
| EXP-F | 6 | image | 1 | 14144338 | 29 | 14526793 |
| EXP-F | 7 | high_frequency | 1 | 3942910165 | 73 | 6009130572 |
| EXP-F | 7 | image | 1 | 14050258 | 29 | 14436103 |
| EXP-F | 8 | high_frequency | 1 | 20619409807 | 372 | 31020696068 |
| EXP-F | 8 | image | 1 | 14186600 | 29 | 14569582 |
| EXP-F | aggregate | condition_indicator | 1 | 32853093 | 8 | 33119559 |
| EXP-F | aggregate | image | 2 | 27250982 | 58 | 28037733 |
| EXP-F | aggregate | low_frequency | 1 | 44467771 | 8 | 44817719 |

## Duplicate evidence

- Rows in CRC32 + uncompressed-size candidate groups: 622
- Repeated identical central-directory member rows: 0
- CRC32 evidence is lightweight and is not cryptographic proof of equal payloads.

## Issues

| Severity | Code | Path | Message |
|---|---|---|---|
| warning | member_archive_run_conflict | high_frequency/EXP A/Exp-A_HDF5_Run-1.zip | 223 member name(s) encode a run different from archive run 1; archive scope was retained. Examples: 'Run-1/Dyno Gear233Run2_00000.hdf5', 'Run-1/Dyno Gear233Run2_00001.hdf5', 'Run-1/Dyno Gear233Run2_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP A/Exp-A_HDF5_Run-2.zip | 149 member name(s) encode a run different from archive run 2; archive scope was retained. Examples: 'Run-2/Dyno Gear233Run1_00000.hdf5', 'Run-2/Dyno Gear233Run1_00001.hdf5', 'Run-2/Dyno Gear233Run1_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP A/Exp-A_HDF5_Run-4.zip | 2 member name(s) encode a run different from archive run 4; archive scope was retained. Examples: 'Run-4/Dyno Gear233Run9_00000.hdf5', 'Run-4/Dyno Gear233Run9_00001.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP A/Exp-A_HDF5_Run-5.zip | 376 member name(s) encode a run different from archive run 5; archive scope was retained. Examples: 'Run-5/Dyno Gear233Run6_00000.hdf5', 'Run-5/Dyno Gear233Run6_00001.hdf5', 'Run-5/Dyno Gear233Run6_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP B/Exp-B_HDF5_Run-1.zip | 329 member name(s) encode a run different from archive run 1; archive scope was retained. Examples: 'Run-1/Dyno Gear303Run2_00000.hdf5', 'Run-1/Dyno Gear303Run2_00001.hdf5', 'Run-1/Dyno Gear303Run2_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP B/Exp-B_HDF5_Run-4.zip | 371 member name(s) encode a run different from archive run 4; archive scope was retained. Examples: 'Run-4/Dyno Gear303Run5_00000.hdf5', 'Run-4/Dyno Gear303Run5_00001.hdf5', 'Run-4/Dyno Gear303Run5_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP B/Exp-B_HDF5_Run-6.zip | 140 member name(s) encode a run different from archive run 6; archive scope was retained. Examples: 'Run-6/Dyno Gear303Run7_00000.hdf5', 'Run-6/Dyno Gear303Run7_00001.hdf5', 'Run-6/Dyno Gear303Run7_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP F/Exp-F_HDF5_Run-1.zip | 122 member name(s) encode a run different from archive run 1; archive scope was retained. Examples: 'Run-1/Dyno Gear309Run2_00000.hdf5', 'Run-1/Dyno Gear309Run2_00001.hdf5', 'Run-1/Dyno Gear309Run2_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP F/Exp-F_HDF5_Run-2.zip | 87 member name(s) encode a run different from archive run 2; archive scope was retained. Examples: 'Run-2/Dyno Gear309Run10_00000.hdf5', 'Run-2/Dyno Gear309Run11_00000.hdf5', 'Run-2/Dyno Gear309Run12_00000.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP F/Exp-F_HDF5_Run-3.zip | 174 member name(s) encode a run different from archive run 3; archive scope was retained. Examples: 'Run-3/Dyno Gear309Run4_00000.hdf5', 'Run-3/Dyno Gear309Run4_00001.hdf5', 'Run-3/Dyno Gear309Run4_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP F/Exp-F_HDF5_Run-4.zip | 527 member name(s) encode a run different from archive run 4; archive scope was retained. Examples: 'Run-4/Dyno Gear309Run100_00000.hdf5', 'Run-4/Dyno Gear309Run101_00000.hdf5', 'Run-4/Dyno Gear309Run102_00000.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP F/Exp-F_HDF5_Run-5.zip | 380 member name(s) encode a run different from archive run 5; archive scope was retained. Examples: 'Run-5/Dyno Gear309Run10_00000.hdf5', 'Run-5/Dyno Gear309Run10_00001.hdf5', 'Run-5/Dyno Gear309Run10_00002.hdf5' |
| warning | member_archive_run_conflict | high_frequency/EXP F/Exp-F_HDF5_Run-8.zip | 242 member name(s) encode a run different from archive run 8; archive scope was retained. Examples: 'Run-8/Dyno Gear309Run9_00000.hdf5', 'Run-8/Dyno Gear309Run9_00001.hdf5', 'Run-8/Dyno Gear309Run9_00002.hdf5' |
