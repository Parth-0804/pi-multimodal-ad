# Dataset integrity and missingness

Evidence directory: `artifacts/intel_welding/audits/foundation_runs/20260927T114705163655Z`. Manifest SHA256: `9c4fb4df70bb137fc851dd858ac22d53eed86ba08c3806d7177e40b300406826`.

All 4040 manifest rows and 236 session directories were
inventoried. All on-disk modality files map to the manifest; no extra sample
directories or missing sample directories were found. Empty/incomplete sample
directories still count as manifest samples.

| modality | present | missing_percent | present_failing_probe |
| --- | --- | --- | --- |
| audio | 2723 | 32.6 | 0 |
| video | 2723 | 32.6 | 16 |
| sensor | 2725 | 32.55 | 0 |

All three deployable files exist for 2723 samples (67.40%).
Structural readability probes pass for 2707 samples (67.00%).
This is an audit flag, not an approved exclusion rule. At least 1,333 samples
(33.00%) have a missing deployable file or fail a probe, exceeding the 5% trigger.
Class and session missingness tables were generated before any exclusion.

All present FLAC files were decoded and all CSVs parsed. All 113 available images
decoded. Video probes decode first/middle/last frames only: 16 files fail, all in
Porosity_w_Excessive_Penetration. OpenCV/FFmpeg also emitted damaged-block/VLC
warnings. Error concealment may return a frame; 2,707 probe passes do not certify
that every frame is undamaged. A full video decode has not been completed.

Only 24 samples have any post-weld images; 22 have five, one has one, and one has
two. The remaining 4,016 have none. Image availability is concentrated in Warping
(97 images) and Porosity_w_Excessive_Penetration (16). No Good sample has images;
an offline binary teacher is unsupported by this local copy.

## Label support and selective missingness

| CATEGORY | samples | sessions | readable | readable_sessions |
| --- | --- | --- | --- | --- |
| Burnthrough | 320 | 19 | 320 | 19 |
| Crater_Cracks | 161 | 12 | 161 | 12 |
| Excessive_Convexity | 160 | 9 | 160 | 9 |
| Excessive_Penetration | 480 | 25 | 480 | 25 |
| Good | 819 | 55 | 819 | 55 |
| Lack_of_Fusion | 320 | 16 | 320 | 16 |
| Overlap | 160 | 12 | 160 | 12 |
| Porosity | 340 | 17 | 109 | 6 |
| Porosity_w_Excessive_Penetration | 480 | 27 | 167 | 12 |
| Spatter | 320 | 17 | 6 | 1 |
| Undercut | 160 | 9 | 4 | 1 |
| Warping | 320 | 18 | 1 | 1 |

The full manifest has Good 819/55 sessions and non-Good 3,221/181 sessions.
The readable subset has Good 819/55 sessions and non-Good 1,888/114 sessions.
Spatter, Undercut and Warping each retain only one session with deployable data.
Their absence is strongly class-dependent. A complete-case restriction changes
the target population and cannot be silently applied or generalized to all twelve
conditions. The local copy's incompleteness is not proof that the hosted dataset
is incomplete.

## Identity and duplicates

Full SHA256 was computed for all 8284 modality files
(26,812,891,824 bytes); zero exact-byte duplicate groups were found, including
images. No exact duplicates cross the proposed dev/test boundary or CV folds.
Near-duplicates and re-encodings remain untested. Sample SUBDIRS are unique, but
20 basename identifiers occur in two different Overlap sessions (FE410 and BSK46).
Use `(session_id, sample_id)` or SUBDIRS as the primary key, not basename alone.
The differing materials and file hashes do not independently certify physical
session independence; retain this grouping question for researcher review.

## Measurement details

Audio: all 2,723 files are 16 kHz. Video: all are 960×600; 1,495 report 30 FPS
and 1,228 report 31 FPS. The 31 FPS files are deviations from nominal documentation,
not automatically corrupt. Sensor CSVs: Date, Time, Part No, Pressure, CO2 Weld Flow, Feed, Primary Weld Current, Wire Consumed, Secondary Weld Voltage, Remarks. All 2,725 parse, with
195–666 rows. Thirty-two files have invalid/nonmonotone timing; 68 adjacent steps
are nonpositive. Parsed numeric channels, constants, missing-cell counts, paths,
sizes and per-file errors are retained in the inventory. Part No, Date, Time and
Remarks must be excluded from predictors; relative time may be used for alignment.

Files: dataset_inventory.parquet, file_inventory.parquet, dataset_summary.json,
category_missingness.csv, session_summary.csv, duplicate_files.csv.
