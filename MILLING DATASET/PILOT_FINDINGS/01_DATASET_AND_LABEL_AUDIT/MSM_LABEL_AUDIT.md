# MSM Stage 1 label audit

Audit date: 2026-10-27T00:14:19.453082+01:00. Dataset ID **8392825**, pinned handle **`manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`**. Counts below come from all 69 actual downloaded `label.csv` files, not spreadsheet remarks. Source bytes and SHA-256 hashes are in `manifests/input_manifest.json`; every native row is preserved in `MSM_INTERVAL_MANIFEST.csv`.

## Native meanings and target interpretation

The [publication](https://www.nature.com/articles/s41597-026-07255-7) defines 0 as stable normal cutting, 1 as abnormal cutting warranting intervention, and 2 as a defective tool cutting stably. Abnormal cutting overrides the tool-defect category. The [Kaggle data card](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly) abbreviates label 2 as tool defect; that abbreviation must not be used to combine labels 1 and 2 automatically.

The audit preserves all three native categories. A later intervention-detection target could compare 1 against {0,2}, with a separately declared 1-versus-0 sensitivity analysis. Neither mapping is approved for training here. Tool marks, label fields, remarks, and stop outcomes must not become unrestricted predictors.

## Counts and actual prediction units

| Machine | Experiments | Intervals | Label 0 | Label 1 | Label 2 | Label-1 groups |
| --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i | 37 | 1585 | 1173 | 325 | 87 | 19 |
| imi_vmx30ui | 19 | 927 | 704 | 133 | 90 | 6 |
| tmf_vf10 | 13 | 63 | 56 | 7 | 0 | 5 |
| TOTAL | 69 | 2575 | 1933 | 465 | 177 | 30 |

There are **2,575 native labeled intervals**, grouped into **69 experiments/operations**. Treat one interval as one candidate example before any windowing. A 1-versus-0-only cohort would contain 2,398 intervals; retaining all native classes gives 2,575. Sensor/video payloads were not acquired: **zero multimodal examples have yet passed pairing, timing, coverage, or signal-quality validation**. Window counts are therefore undefined and would not increase the number of independent experiment groups.

The laboratory subset has 2,512 intervals, including 458 label-1 intervals in 25 positive-containing folders, with video listed for every folder. The industrial subset has 63 intervals, including 7 label-1 intervals in 5 folders, and no listed videos. These units differ: laboratory labels typically describe short cutting passes; industrial annotations can segment longer machining paths. Interval-level and duration-weighted metrics would answer different questions.

## Integrity and publication consistency

All 69 files have the same 12-column header: `start,end,label,direction,N,ap,ae,F,Z,D,Tool,Workpiece`. All 2,575 rows have finite, nonnegative start times, strictly later end times, and labels in {0,1,2}. No annotation files, mandatory cells, context cells, overlapping intervals, out-of-order rows, duplicate rows within a file, or identical annotation-file hashes were found missing/invalid. There are **0 invalid rows and 0 annotation warning rows**. Blank lines are ignored by the CSV parser; original bytes are preserved.

All numeric context fields inspected (`N,ap,ae,F,Z,D`) are finite and positive; every direction is UP or DOWN. Context validation found 0 issues. Every one of the 177 label-2 rows has a starred tool ID, and all 1,933 label-0 rows have unstarred IDs. Of the label-1 rows, 59 have starred and 406 have unstarred tools. This agrees with the stated override rule; it does not independently verify experts' judgments. Without signals/media, timing accuracy and the physical cause of each anomaly remain unaudited. Interval duration is `end - start` in seconds, calculated using decimal arithmetic; no formulas or source values were corrected.

## Duration distributions

| Machine / label | n | Min s | Median s | Max s | Total s |
| --- | --- | --- | --- | --- | --- |
| imi_vm20i/label_0 | 1173 | 0.533 | 3.0510 | 7.019 | 3662.007 |
| imi_vm20i/label_1 | 325 | 0.534 | 4.5230 | 7.421 | 1393.990 |
| imi_vm20i/label_2 | 87 | 1.514 | 2.4960 | 4.757 | 238.397 |
| imi_vmx30ui/label_0 | 704 | 0.747 | 1.6850 | 6.400 | 1526.504 |
| imi_vmx30ui/label_1 | 133 | 0.683 | 5.3330 | 7.296 | 655.988 |
| imi_vmx30ui/label_2 | 90 | 0.682 | 1.1310 | 4.907 | 184.743 |
| tmf_vf10/label_0 | 56 | 1.066 | 132.9275 | 408.529 | 9179.962 |
| tmf_vf10/label_1 | 7 | 2.304 | 26.7950 | 85.418 | 236.714 |

Across all intervals: minimum 0.533 s, median 3.008 s, maximum 408.529 s; summed annotated cutting time 17,078.305 s (4.744 h). Duration summaries describe annotated cuts only, not complete recording lengths. Do not label gaps as normal. Industrial transitions share some endpoints; use a documented half-open interval policy if converting to windows, without rewriting annotations.

## Group-disjoint feasibility and dependence

**30 experiment folders contain label 1** (19 + 6 + 5). This establishes nominal group counts, not independence of physical trials. All three machines have labels 0 and 1. Both laboratory machines also have label 2; the industrial machine has none. There are 4 label-2-containing groups on each laboratory machine. `imi_vm20i` has the strongest abnormal-group support; `imi_vmx30ui` has only 6 positive groups, and `tmf_vf10` has only 7 positive intervals across 5 groups. Industrial estimates will be especially unstable.

Experiment-disjoint splitting is feasible in principle if every interval/window from a folder stays together and class coverage is checked. A provisional 3-fold grouped design is more plausible than many folds; it is a proposal, not a generated or validated split. Five-fold industrial evaluation would leave roughly one positive group per test fold and very few abnormal intervals. Three-class folds additionally need explicit label-2 support. Do not claim machine-held-out three-class coverage when holding out `tmf_vf10`.

Reference dates in MTConnect filenames reveal only **12 machine/date clusters**: 3 for `imi_vm20i`, 4 for `imi_vmx30ui`, and 5 for `tmf_vf10`; respectively 3, 4, and 4 contain positives. The two laboratory machines together span only 5 distinct calendar dates. These are filename-derived proxies, not verified session IDs. See `manifests/reference_date_groups.csv`. Shared dates, tool IDs, workpieces, repeated NC programs, and adjacent production cycles can create dependence across folders. IDs such as G1/G2 recur throughout industry data, but an ID alone does not establish physical-tool identity. Confirm chronology and physical tool/workpiece/session links before finalizing groups; use stronger groups when dependence is established. Sensor-level duplicates were not assessed.

Positive-containing experiments, in native folder numbering:

- **imi_vm20i**: dataset1, dataset5, dataset6, dataset7, dataset8, dataset9, dataset15, dataset16, dataset17, dataset18, dataset22, dataset24, dataset25, dataset26, dataset27, dataset28, dataset29, dataset30, dataset33

- **imi_vmx30ui**: dataset4, dataset9, dataset14, dataset15, dataset17, dataset19

- **tmf_vf10**: dataset1, dataset6, dataset8, dataset10, dataset11

## Counts for every experiment

| Experiment | Intervals | Label 0 | Label 1 | Label 2 | Invalid | Warnings |
| --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | 12 | 0 | 12 | 0 | 0 | 0 |
| imi_vm20i/dataset2 | 18 | 0 | 0 | 18 | 0 | 0 |
| imi_vm20i/dataset3 | 12 | 0 | 0 | 12 | 0 | 0 |
| imi_vm20i/dataset4 | 12 | 0 | 0 | 12 | 0 | 0 |
| imi_vm20i/dataset5 | 9 | 4 | 5 | 0 | 0 | 0 |
| imi_vm20i/dataset6 | 64 | 44 | 20 | 0 | 0 | 0 |
| imi_vm20i/dataset7 | 1 | 0 | 1 | 0 | 0 | 0 |
| imi_vm20i/dataset8 | 1 | 0 | 1 | 0 | 0 | 0 |
| imi_vm20i/dataset9 | 4 | 0 | 4 | 0 | 0 | 0 |
| imi_vm20i/dataset10 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset11 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset12 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset13 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset14 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset15 | 9 | 5 | 4 | 0 | 0 | 0 |
| imi_vm20i/dataset16 | 64 | 44 | 20 | 0 | 0 | 0 |
| imi_vm20i/dataset17 | 7 | 6 | 1 | 0 | 0 | 0 |
| imi_vm20i/dataset18 | 7 | 6 | 1 | 0 | 0 | 0 |
| imi_vm20i/dataset19 | 19 | 19 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset20 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset21 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset22 | 1 | 0 | 1 | 0 | 0 | 0 |
| imi_vm20i/dataset23 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset24 | 64 | 0 | 64 | 0 | 0 | 0 |
| imi_vm20i/dataset25 | 64 | 8 | 56 | 0 | 0 | 0 |
| imi_vm20i/dataset26 | 64 | 0 | 19 | 45 | 0 | 0 |
| imi_vm20i/dataset27 | 64 | 39 | 25 | 0 | 0 | 0 |
| imi_vm20i/dataset28 | 64 | 44 | 20 | 0 | 0 | 0 |
| imi_vm20i/dataset29 | 64 | 18 | 46 | 0 | 0 | 0 |
| imi_vm20i/dataset30 | 64 | 40 | 24 | 0 | 0 | 0 |
| imi_vm20i/dataset31 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset32 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset33 | 1 | 0 | 1 | 0 | 0 | 0 |
| imi_vm20i/dataset34 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset35 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset36 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vm20i/dataset37 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset1 | 18 | 0 | 0 | 18 | 0 | 0 |
| imi_vmx30ui/dataset2 | 12 | 0 | 0 | 12 | 0 | 0 |
| imi_vmx30ui/dataset3 | 12 | 0 | 0 | 12 | 0 | 0 |
| imi_vmx30ui/dataset4 | 12 | 0 | 12 | 0 | 0 | 0 |
| imi_vmx30ui/dataset5 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset6 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset7 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset8 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset9 | 14 | 12 | 2 | 0 | 0 | 0 |
| imi_vmx30ui/dataset10 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset11 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset12 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset13 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset14 | 64 | 16 | 48 | 0 | 0 | 0 |
| imi_vmx30ui/dataset15 | 64 | 10 | 54 | 0 | 0 | 0 |
| imi_vmx30ui/dataset16 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset17 | 27 | 26 | 1 | 0 | 0 | 0 |
| imi_vmx30ui/dataset18 | 64 | 64 | 0 | 0 | 0 | 0 |
| imi_vmx30ui/dataset19 | 64 | 0 | 16 | 48 | 0 | 0 |
| tmf_vf10/dataset1 | 6 | 5 | 1 | 0 | 0 | 0 |
| tmf_vf10/dataset2 | 4 | 4 | 0 | 0 | 0 | 0 |
| tmf_vf10/dataset3 | 4 | 4 | 0 | 0 | 0 | 0 |
| tmf_vf10/dataset4 | 4 | 4 | 0 | 0 | 0 | 0 |
| tmf_vf10/dataset5 | 4 | 4 | 0 | 0 | 0 | 0 |
| tmf_vf10/dataset6 | 6 | 5 | 1 | 0 | 0 | 0 |
| tmf_vf10/dataset7 | 4 | 4 | 0 | 0 | 0 | 0 |
| tmf_vf10/dataset8 | 5 | 4 | 1 | 0 | 0 | 0 |
| tmf_vf10/dataset9 | 4 | 4 | 0 | 0 | 0 | 0 |
| tmf_vf10/dataset10 | 6 | 4 | 2 | 0 | 0 | 0 |
| tmf_vf10/dataset11 | 8 | 6 | 2 | 0 | 0 | 0 |
| tmf_vf10/dataset12 | 4 | 4 | 0 | 0 | 0 | 0 |
| tmf_vf10/dataset13 | 4 | 4 | 0 | 0 | 0 | 0 |

## Next bounded pilot

| Experiment | 0 / 1 / 2 | Role | Proposed new bytes |
| --- | --- | --- | --- |
| imi_vm20i/dataset1 | 0 / 12 / 0 | Abnormal cutting with defective tool; 12 label-1 intervals | 15819965 |
| imi_vm20i/dataset4 | 0 / 0 / 12 | Stable defective-tool control; 12 label-2 intervals | 13757946 |
| imi_vm20i/dataset19 | 19 / 0 / 0 | Normal control; 19 label-0 intervals; test video offset | 17804288 |
| imi_vmx30ui/dataset9 | 12 / 2 / 0 | Second-machine mixed experiment; 12 label-0 and 2 label-1 intervals | 21357757 |
| imi_vmx30ui/dataset8 | 64 / 0 / 0 | Second-machine normal control; 64 label-0 intervals | 37348308 |
| tmf_vf10/dataset1 | 5 / 1 / 0 | Optional industrial diagnostic; 5 label-0 and 1 label-1 intervals; no video | 96751008 |

The five laboratory groups provide 121 intervals (95 label 0, 14 label 1, 12 label 2), including pure normal and stable defective-tool controls. The optional industrial group adds 6 intervals (5 label 0, 1 label 1). This is an ingestion/alignment pilot, not an evaluation cohort: only two laboratory positive groups are selected, and no performance claim or training is justified by the pilot alone.

The supplied script's original pilot list would emphasize abnormal experiments: `imi_vm20i/dataset5` actually has 5 label-1 intervals, while datasets 7 and 8 each have just one interval. The revised proposal adds explicit controls and retains a second-machine mixed experiment. Full experiment folders are unnecessary for the initial timing check; see the exact file plan and storage in `MSM_FILE_AVAILABILITY.md`.

Stage 1 stops here. The researcher must review the native-label target, stronger grouping needs, and video pairing evidence before authorizing Stage 2.
