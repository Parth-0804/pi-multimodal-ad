# MSM Stage 1 file availability

Official source: [Kaggle dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), dataset ID 8392825, **version 2**. The version-pinned public file-list API was paginated to completion (3 pages, 481 unique files), and the sum of listed sizes equals the official dataset total: **40,412,136,430 bytes** (40.412 GB; 37.637 GiB). No full archive was requested. `manifests/official_file_inventory.json` retains every remote path, byte size, and creation date; `manifests/file_inventory.csv` adds modality and local status. Listed size is not a cryptographic checksum or validation of payload readability.

## Verified hierarchy

The dataset root has `dataset_summary.xlsx` (11,784 bytes), `imi_vm20i.xml` (16,596), `imi_vmx30ui.xml` (13,831), and `tmf_vf10.xml` (4,859). Machine folders contain contiguous `dataset1` through `dataset37`, `dataset19`, and `dataset13`, respectively. Each experiment has one `label.csv`, one timestamped `*_mtc.csv`, and `*_s0.wav` plus `*_s2.wav`. Both lab machines have MP4 and NC files for every experiment. VM20i additionally has `*_acc.csv` and `*_s1.wav`; TMF has `*_ct.csv`. Extra PNG figures occur only in VM20i datasets 6 and 7.

| Machine | Experiments | Labels | MP4 | S0 / S1 / S2 | ACC | MTC | CT | NC | Bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| imi_vm20i | 37 | 37 | 37 | 37 / 37 / 37 | 37 | 37 | 0 | 37 | 36553478458 |
| imi_vmx30ui | 19 | 19 | 19 | 19 / 0 / 19 | 0 | 19 | 0 | 19 | 1566739638 |
| tmf_vf10 | 13 | 13 | 0 | 13 / 0 / 13 | 0 | 13 | 13 | 0 | 2291871264 |

| Modality / type | Files | Bytes |
| --- | --- | --- |
| acc | 37 | 32652898979 |
| audio_s0 | 69 | 2836191432 |
| audio_s1 | 37 | 1131728496 |
| audio_s2 | 69 | 2836191444 |
| ct | 13 | 21607 |
| label | 69 | 173594 |
| mtc | 69 | 47454900 |
| nc | 56 | 255178 |
| png | 2 | 3275932 |
| video | 56 | 903897798 |
| xlsx | 1 | 11784 |
| xml | 3 | 35286 |

## Missing versus intentionally unacquired

**No expected annotation files are missing**: 69/69 are local, totaling 173,594 bytes. The other **412 listed files are intentionally not downloaded**. The spreadsheet and XML files are listed but were not acquired during this annotation-only stage. Only the pasted downloader was supplied with this task; no local MSM summary workbook was located. The stated spreadsheet counts were independently checked against the complete hierarchy and actual labels.

All 13 industrial experiments lack listed MP4 and NC files. The publication explicitly withholds industrial NC programs; it describes videos for laboratory data. These are modality limitations, not failed downloads. Accelerometers are absent from the second lab and industry folders; S1 is VM20i-only. Every experiment has S0/S2 audio listed. No media or sensor file has been checked for decoding, completeness, sampling rate, missing values, or annotation coverage.

Video pairing remains a material gate. Filenames already differ from sensor reference timestamps: VM20i dataset1 video is approximately +2.213 s, VM20i dataset19 video approximately -75.487 s, and VMX30Ui dataset9 video approximately -143.523 s relative to its sensor filename reference, **if** the naming clocks and formats are comparable. These arithmetic differences are not calibrated offsets and cannot be applied to labels. Later inspection must establish video start, editing/compression effects, drift, coverage of each cutting interval, and useful visibility. Sensor synchronization described by the publication does not establish smartphone-video alignment.

Industrial CT CSVs total only 21,607 bytes across 13 recordings. Their small size makes schema and temporal-resolution inspection essential before treating them as an appropriate continuous sensor branch. MTConnect channel availability likewise requires payload inspection.

## Per-experiment availability

| Experiment | Files | Listed modalities | Total bytes | Locally acquired |
| --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 346312487 | label.csv only |
| imi_vm20i/dataset2 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 447908718 | label.csv only |
| imi_vm20i/dataset3 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 325424327 | label.csv only |
| imi_vm20i/dataset4 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 294367548 | label.csv only |
| imi_vm20i/dataset5 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 418006659 | label.csv only |
| imi_vm20i/dataset6 | 9 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;png;video | 1670888297 | label.csv only |
| imi_vm20i/dataset7 | 9 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;png;video | 974980214 | label.csv only |
| imi_vm20i/dataset8 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 744129901 | label.csv only |
| imi_vm20i/dataset9 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1278428594 | label.csv only |
| imi_vm20i/dataset10 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1301397369 | label.csv only |
| imi_vm20i/dataset11 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1250502737 | label.csv only |
| imi_vm20i/dataset12 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1875038389 | label.csv only |
| imi_vm20i/dataset13 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 916603755 | label.csv only |
| imi_vm20i/dataset14 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1313546374 | label.csv only |
| imi_vm20i/dataset15 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 229338335 | label.csv only |
| imi_vm20i/dataset16 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 809859538 | label.csv only |
| imi_vm20i/dataset17 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 149570877 | label.csv only |
| imi_vm20i/dataset18 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 220298730 | label.csv only |
| imi_vm20i/dataset19 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 400539807 | label.csv only |
| imi_vm20i/dataset20 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 932177980 | label.csv only |
| imi_vm20i/dataset21 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1452651520 | label.csv only |
| imi_vm20i/dataset22 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 59327390 | label.csv only |
| imi_vm20i/dataset23 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 927942894 | label.csv only |
| imi_vm20i/dataset24 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1491985494 | label.csv only |
| imi_vm20i/dataset25 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1407896792 | label.csv only |
| imi_vm20i/dataset26 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1001507930 | label.csv only |
| imi_vm20i/dataset27 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 962675717 | label.csv only |
| imi_vm20i/dataset28 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1683386249 | label.csv only |
| imi_vm20i/dataset29 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1649080171 | label.csv only |
| imi_vm20i/dataset30 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1661215060 | label.csv only |
| imi_vm20i/dataset31 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1295455172 | label.csv only |
| imi_vm20i/dataset32 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1288560819 | label.csv only |
| imi_vm20i/dataset33 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 130265730 | label.csv only |
| imi_vm20i/dataset34 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1304909826 | label.csv only |
| imi_vm20i/dataset35 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1430479000 | label.csv only |
| imi_vm20i/dataset36 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1437027408 | label.csv only |
| imi_vm20i/dataset37 | 8 | acc;audio_s0;audio_s1;audio_s2;label;mtc;nc;video | 1469790650 | label.csv only |
| imi_vmx30ui/dataset1 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 41593766 | label.csv only |
| imi_vmx30ui/dataset2 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 27975719 | label.csv only |
| imi_vmx30ui/dataset3 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 27223289 | label.csv only |
| imi_vmx30ui/dataset4 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 34528631 | label.csv only |
| imi_vmx30ui/dataset5 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 103177692 | label.csv only |
| imi_vmx30ui/dataset6 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 111770467 | label.csv only |
| imi_vmx30ui/dataset7 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 165195481 | label.csv only |
| imi_vmx30ui/dataset8 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 57277910 | label.csv only |
| imi_vmx30ui/dataset9 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 33566098 | label.csv only |
| imi_vmx30ui/dataset10 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 74601938 | label.csv only |
| imi_vmx30ui/dataset11 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 111346574 | label.csv only |
| imi_vmx30ui/dataset12 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 80178745 | label.csv only |
| imi_vmx30ui/dataset13 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 123726399 | label.csv only |
| imi_vmx30ui/dataset14 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 144407676 | label.csv only |
| imi_vmx30ui/dataset15 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 146299533 | label.csv only |
| imi_vmx30ui/dataset16 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 78195448 | label.csv only |
| imi_vmx30ui/dataset17 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 70852012 | label.csv only |
| imi_vmx30ui/dataset18 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 75303732 | label.csv only |
| imi_vmx30ui/dataset19 | 6 | audio_s0;audio_s2;label;mtc;nc;video | 59518528 | label.csv only |
| tmf_vf10/dataset1 | 5 | audio_s0;audio_s2;ct;label;mtc | 193080706 | label.csv only |
| tmf_vf10/dataset2 | 5 | audio_s0;audio_s2;ct;label;mtc | 152903418 | label.csv only |
| tmf_vf10/dataset3 | 5 | audio_s0;audio_s2;ct;label;mtc | 153166607 | label.csv only |
| tmf_vf10/dataset4 | 5 | audio_s0;audio_s2;ct;label;mtc | 152775642 | label.csv only |
| tmf_vf10/dataset5 | 5 | audio_s0;audio_s2;ct;label;mtc | 153190040 | label.csv only |
| tmf_vf10/dataset6 | 5 | audio_s0;audio_s2;ct;label;mtc | 187570633 | label.csv only |
| tmf_vf10/dataset7 | 5 | audio_s0;audio_s2;ct;label;mtc | 290867196 | label.csv only |
| tmf_vf10/dataset8 | 5 | audio_s0;audio_s2;ct;label;mtc | 121685114 | label.csv only |
| tmf_vf10/dataset9 | 5 | audio_s0;audio_s2;ct;label;mtc | 153528215 | label.csv only |
| tmf_vf10/dataset10 | 5 | audio_s0;audio_s2;ct;label;mtc | 183422346 | label.csv only |
| tmf_vf10/dataset11 | 5 | audio_s0;audio_s2;ct;label;mtc | 183330683 | label.csv only |
| tmf_vf10/dataset12 | 5 | audio_s0;audio_s2;ct;label;mtc | 182903998 | label.csv only |
| tmf_vf10/dataset13 | 5 | audio_s0;audio_s2;ct;label;mtc | 183446666 | label.csv only |

## Exact proposed next-pilot files — not downloaded

| Proposed file (dataset relative) | Bytes | Cohort | Status |
| --- | --- | --- | --- |
| dataset_summary.xlsx | 11784 | metadata | proposed_only |
| imi_vm20i.xml | 16596 | metadata | proposed_only |
| imi_vm20i/dataset1/20240229_053831.227000_mtc.csv | 287755 | lab_primary | proposed_only |
| imi_vm20i/dataset1/20240229_053831.227000_s0.wav | 10728620 | lab_primary | proposed_only |
| imi_vm20i/dataset1/20240229_053833440_comp_reduced.mp4 | 4802507 | lab_primary | proposed_only |
| imi_vm20i/dataset1/A_N2-a3_ab.nc | 1083 | lab_primary | proposed_only |
| imi_vm20i/dataset1/label.csv | 833 | lab_primary | already_acquired |
| imi_vm20i/dataset19/20240226_083508421_comp_reduced.mp4 | 5031932 | lab_primary | proposed_only |
| imi_vm20i/dataset19/20240226_083623.908287_mtc.csv | 330970 | lab_primary | proposed_only |
| imi_vm20i/dataset19/20240226_083623.908287_s0.wav | 12436336 | lab_primary | proposed_only |
| imi_vm20i/dataset19/E_P1S-a3.nc | 5050 | lab_primary | proposed_only |
| imi_vm20i/dataset19/label.csv | 1271 | lab_primary | already_acquired |
| imi_vm20i/dataset4/20240229_062017.610010_mtc.csv | 245931 | lab_primary | proposed_only |
| imi_vm20i/dataset4/20240229_062017.610010_s0.wav | 9277484 | lab_primary | proposed_only |
| imi_vm20i/dataset4/20240229_062019896_comp_reduced.mp4 | 4233467 | lab_primary | proposed_only |
| imi_vm20i/dataset4/E_P3-a3_ab.nc | 1064 | lab_primary | proposed_only |
| imi_vm20i/dataset4/label.csv | 867 | lab_primary | already_acquired |
| imi_vmx30ui.xml | 13831 | metadata | proposed_only |
| imi_vmx30ui/dataset8/20240228_074220540_comp_reduced.mp4 | 16966173 | lab_primary | proposed_only |
| imi_vmx30ui/dataset8/20240228_074323.317000_mtc.csv | 451638 | lab_primary | proposed_only |
| imi_vmx30ui/dataset8/20240228_074323.317000_s0.wav | 19925420 | lab_primary | proposed_only |
| imi_vmx30ui/dataset8/F2_N2-a5.nc | 5077 | lab_primary | proposed_only |
| imi_vmx30ui/dataset8/label.csv | 4182 | lab_primary | already_acquired |
| imi_vmx30ui/dataset9/20240228_035647972_comp_reduced.mp4 | 8875147 | lab_primary | proposed_only |
| imi_vmx30ui/dataset9/20240228_035911.495000_mtc.csv | 270417 | lab_primary | proposed_only |
| imi_vmx30ui/dataset9/20240228_035911.495000_s0.wav | 12207404 | lab_primary | proposed_only |
| imi_vmx30ui/dataset9/D_P1-a5.nc | 4789 | lab_primary | proposed_only |
| imi_vmx30ui/dataset9/label.csv | 937 | lab_primary | already_acquired |
| tmf_vf10.xml | 4859 | industrial_optional | proposed_only |
| tmf_vf10/dataset1/20240115_141431.622703_ct.csv | 1799 | industrial_optional | proposed_only |
| tmf_vf10/dataset1/20240115_141431.622703_mtc.csv | 419945 | industrial_optional | proposed_only |
| tmf_vf10/dataset1/20240115_141431.622703_s0.wav | 96329264 | industrial_optional | proposed_only |
| tmf_vf10/dataset1/label.csv | 436 | industrial_optional | already_acquired |

The primary five-laboratory-experiment plan uses one S0 audio channel, the MTC table, MP4, and NC program from each selected folder, plus the summary workbook and the two laboratory machine XML models for semantic/grouping context. Existing labels require no further transfer. The optional TMF diagnostic adds S0, MTC, CT, and the TMF XML model; it cannot provide a visual-sensor pair. Additional S1/S2 audio channels and high-volume accelerometers can wait until synchronization and branch choice are established. This selection is for inspection, not a claim that MTC has the needed channels or rates.

- Primary laboratory plan plus metadata: **106,130,475 new bytes** (106.130 MB; 101.214 MiB).
- Optional industrial diagnostic: **96,755,867 new bytes** (96.756 MB).
- Combined proposed transfer: **202,886,342 new bytes** (202.886 MB; 193.487 MiB).
- Optional VM20i accelerometer files for the three selected VM20i folders add **928,949,792 bytes**; combined plan with these becomes **1,131,836,134 bytes** (1.054 GiB).

These are sums of official per-file sizes for direct selective downloads, not compressed-transfer estimates. Budget at least 1 GiB free for the base inspection plan (2 GiB if adding ACC), plus separate space for any later derived frames/features. Do not pre-extract video frames. The machine-readable file plan is `manifests/pilot_file_plan.csv`; storage totals are in `manifests/pilot_storage.json`. Researcher review must precede all pilot media downloads.
