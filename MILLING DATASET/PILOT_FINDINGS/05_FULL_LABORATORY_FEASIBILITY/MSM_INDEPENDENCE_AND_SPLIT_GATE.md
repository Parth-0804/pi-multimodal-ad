# MSM independence and nested split gate

Dataset `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2` (ID 8392825), [official dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), [publication](https://www.nature.com/articles/s41597-026-07255-7). Version 2 was reverified against the official public API and all 481 paths/sizes match Stage 1. All native labels and historical outputs were preserved.


**This is a feasibility check, not a final split freeze.** Both targets use the existing `msm.splits.nested_plan`: three outer folds, two inner folds, fixed outer seed 42 and inner seed 142+outer index. There was no seed search, automatic fold reduction, random interval split or model fitting. Both classes, group disjointness, complete outer coverage and one out-of-fold prediction per inner training row are required by the adapter.

| Target | Grouping | Intervals | Groups | Positive groups | Mixed groups | 3 outer / 2 inner | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stable_negative | group_id | 1895 | 45 | 17 | 14 | PASS | Frozen single-seed nested construction passes technical group/class gates |
| stable_negative | machine_date_group | 1895 | 7 | 7 | 7 | PASS | Frozen single-seed nested construction passes technical group/class gates |
| stable_negative | calendar_date_group | 1895 | 5 | 5 | 5 | PASS | Frozen single-seed nested construction passes technical group/class gates |
| exclude | group_id | 1770 | 41 | 17 | 12 | PASS | Frozen single-seed nested construction passes technical group/class gates |
| exclude | machine_date_group | 1770 | 7 | 7 | 6 | PASS | Frozen single-seed nested construction passes technical group/class gates |
| exclude | calendar_date_group | 1770 | 5 | 5 | 5 | PASS | Frozen single-seed nested construction passes technical group/class gates |

The machine/experiment gate can establish only nominal separation. A nominal PASS still allows related reference dates in train/test; exact outer and inner date overlaps are recorded in `manifests/split_feasibility.json`. The machine/date analysis prevents same-machine/date overlap but can share a calendar date across machines. Calendar-date grouping is a conservative third diagnostic. Neither proxy proves separate physical sessions across dates. No final fold IDs were frozen or adopted for evaluation.

## Metadata relationships and physical dependence

**VERIFIED:** machine and folder identities; original reference dates from MTC filenames; native Tool/Workpiece strings; MTC Current_Tool and running/editing program names; exact NC bytes/hashes. The full laboratory material spans 7 machine/reference-date clusters and 5 calendar dates. Full metadata, tool/material values and NC headers are in `manifests/metadata_relationships.json`. These are provenance, never ordinary predictor features.

**INFERRED:** folders recorded on the same machine/date may share physical tool, workpiece, setup, operator and camera session. Same-day records across machines can share laboratory conditions. Exact NC reuse establishes shared program content, not simultaneous execution or independent sessions. Generic tool letters/defect markers and material descriptions are conditions, not unique serial identities.

**UNRESOLVED:** physical session boundaries, actual tool reuse and wear trajectories, workpiece instance reuse, repeated setups spanning dates, camera-position persistence, and internal MTC aggregation latency. Different folders do not prove independence. Different dates do not rule out reuse of the same tool/workpiece.

| Exact NC SHA-256 | Folders |
| --- | --- |
| 6c3c75987e424b5a2e104d0ffe5d581b13211946e0887a5ae4e1de4d71b0cbd5 | imi_vm20i/dataset17; imi_vm20i/dataset18 |
| bd1354f33c823e8d175186b2c18b2b0b07f465e88ac145b49b518ad839e90d41 | imi_vm20i/dataset26; imi_vm20i/dataset27 |
| 66729ee4a1ad3d0d57da206cc7bece273d4e7a971ea55904872484db498d60ef | imi_vm20i/dataset33; imi_vm20i/dataset34 |

## Label definition requires approval

Frozen primary: label 1 versus stable labels 0 and 2, 1895 joint candidates. It asks whether the cutting process warrants intervention and retains defective-tool-but-stable cuts as negatives. Sensitivity: label 1 versus label 0 with label 2 excluded, 1770 candidates. It avoids mixing stable tool conditions but changes prevalence, sample size and condition coverage. Neither target measures generic tool health. No predictive performance was observed to choose between them.

**Researcher decision required before evaluation:** finalize the primary target and physical grouping policy; reconcile session evidence or approve an explicitly limited date-group proxy. A passing nominal split alone is insufficient for an independent physical-session claim. If the stricter fixed split fails, any approved alternative fold design/estimand must be a separately reviewed protocol revision; no alternative was silently substituted.

## Positive distribution and class support


### stable_negative: group_id

| Group | Native 0 | Native 1 | Native 2 | Both classes | Folders |
| --- | --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | 0 | 8 | 0 | False | 1 |
| imi_vm20i/dataset10 | 17 | 0 | 0 | False | 1 |
| imi_vm20i/dataset11 | 53 | 0 | 0 | False | 1 |
| imi_vm20i/dataset13 | 62 | 0 | 0 | False | 1 |
| imi_vm20i/dataset14 | 55 | 0 | 0 | False | 1 |
| imi_vm20i/dataset16 | 39 | 18 | 0 | True | 1 |
| imi_vm20i/dataset19 | 18 | 0 | 0 | False | 1 |
| imi_vm20i/dataset20 | 64 | 0 | 0 | False | 1 |
| imi_vm20i/dataset21 | 62 | 0 | 0 | False | 1 |
| imi_vm20i/dataset23 | 20 | 0 | 0 | False | 1 |
| imi_vm20i/dataset24 | 0 | 55 | 0 | False | 1 |
| imi_vm20i/dataset25 | 4 | 43 | 0 | True | 1 |
| imi_vm20i/dataset26 | 0 | 19 | 45 | True | 1 |
| imi_vm20i/dataset27 | 39 | 25 | 0 | True | 1 |
| imi_vm20i/dataset28 | 15 | 9 | 0 | True | 1 |
| imi_vm20i/dataset29 | 8 | 30 | 0 | True | 1 |
| imi_vm20i/dataset3 | 0 | 0 | 12 | False | 1 |
| imi_vm20i/dataset30 | 9 | 15 | 0 | True | 1 |
| imi_vm20i/dataset31 | 61 | 0 | 0 | False | 1 |
| imi_vm20i/dataset32 | 63 | 0 | 0 | False | 1 |
| imi_vm20i/dataset34 | 59 | 0 | 0 | False | 1 |
| imi_vm20i/dataset35 | 64 | 0 | 0 | False | 1 |
| imi_vm20i/dataset36 | 59 | 0 | 0 | False | 1 |
| imi_vm20i/dataset37 | 64 | 0 | 0 | False | 1 |
| imi_vm20i/dataset4 | 0 | 0 | 11 | False | 1 |
| imi_vm20i/dataset5 | 3 | 4 | 0 | True | 1 |
| imi_vm20i/dataset6 | 16 | 12 | 0 | True | 1 |
| imi_vmx30ui/dataset10 | 63 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset11 | 55 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset12 | 49 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset13 | 48 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset14 | 3 | 33 | 0 | True | 1 |
| imi_vmx30ui/dataset15 | 5 | 44 | 0 | True | 1 |
| imi_vmx30ui/dataset16 | 53 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset17 | 24 | 1 | 0 | True | 1 |
| imi_vmx30ui/dataset18 | 64 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset19 | 0 | 14 | 36 | True | 1 |
| imi_vmx30ui/dataset2 | 0 | 0 | 12 | False | 1 |
| imi_vmx30ui/dataset3 | 0 | 0 | 9 | False | 1 |
| imi_vmx30ui/dataset4 | 0 | 4 | 0 | False | 1 |
| imi_vmx30ui/dataset5 | 17 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset6 | 63 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset7 | 61 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset8 | 64 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset9 | 11 | 2 | 0 | True | 1 |

### stable_negative: machine_date_group

| Group | Native 0 | Native 1 | Native 2 | Both classes | Folders |
| --- | --- | --- | --- | --- | --- |
| imi_vm20i/20240226 | 409 | 34 | 0 | True | 11 |
| imi_vm20i/20240229 | 402 | 62 | 23 | True | 12 |
| imi_vm20i/20240302 | 43 | 142 | 45 | True | 4 |
| imi_vmx30ui/20240227 | 144 | 33 | 0 | True | 4 |
| imi_vmx30ui/20240228 | 295 | 46 | 0 | True | 7 |
| imi_vmx30ui/20240229 | 0 | 4 | 21 | True | 3 |
| imi_vmx30ui/20240302 | 141 | 15 | 36 | True | 4 |

### stable_negative: calendar_date_group

| Group | Native 0 | Native 1 | Native 2 | Both classes | Folders |
| --- | --- | --- | --- | --- | --- |
| 20240226 | 409 | 34 | 0 | True | 11 |
| 20240227 | 144 | 33 | 0 | True | 4 |
| 20240228 | 295 | 46 | 0 | True | 7 |
| 20240229 | 402 | 66 | 44 | True | 15 |
| 20240302 | 184 | 157 | 81 | True | 8 |

### exclude: group_id

| Group | Native 0 | Native 1 | Native 2 | Both classes | Folders |
| --- | --- | --- | --- | --- | --- |
| imi_vm20i/dataset1 | 0 | 8 | 0 | False | 1 |
| imi_vm20i/dataset10 | 17 | 0 | 0 | False | 1 |
| imi_vm20i/dataset11 | 53 | 0 | 0 | False | 1 |
| imi_vm20i/dataset13 | 62 | 0 | 0 | False | 1 |
| imi_vm20i/dataset14 | 55 | 0 | 0 | False | 1 |
| imi_vm20i/dataset16 | 39 | 18 | 0 | True | 1 |
| imi_vm20i/dataset19 | 18 | 0 | 0 | False | 1 |
| imi_vm20i/dataset20 | 64 | 0 | 0 | False | 1 |
| imi_vm20i/dataset21 | 62 | 0 | 0 | False | 1 |
| imi_vm20i/dataset23 | 20 | 0 | 0 | False | 1 |
| imi_vm20i/dataset24 | 0 | 55 | 0 | False | 1 |
| imi_vm20i/dataset25 | 4 | 43 | 0 | True | 1 |
| imi_vm20i/dataset26 | 0 | 19 | 0 | False | 1 |
| imi_vm20i/dataset27 | 39 | 25 | 0 | True | 1 |
| imi_vm20i/dataset28 | 15 | 9 | 0 | True | 1 |
| imi_vm20i/dataset29 | 8 | 30 | 0 | True | 1 |
| imi_vm20i/dataset30 | 9 | 15 | 0 | True | 1 |
| imi_vm20i/dataset31 | 61 | 0 | 0 | False | 1 |
| imi_vm20i/dataset32 | 63 | 0 | 0 | False | 1 |
| imi_vm20i/dataset34 | 59 | 0 | 0 | False | 1 |
| imi_vm20i/dataset35 | 64 | 0 | 0 | False | 1 |
| imi_vm20i/dataset36 | 59 | 0 | 0 | False | 1 |
| imi_vm20i/dataset37 | 64 | 0 | 0 | False | 1 |
| imi_vm20i/dataset5 | 3 | 4 | 0 | True | 1 |
| imi_vm20i/dataset6 | 16 | 12 | 0 | True | 1 |
| imi_vmx30ui/dataset10 | 63 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset11 | 55 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset12 | 49 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset13 | 48 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset14 | 3 | 33 | 0 | True | 1 |
| imi_vmx30ui/dataset15 | 5 | 44 | 0 | True | 1 |
| imi_vmx30ui/dataset16 | 53 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset17 | 24 | 1 | 0 | True | 1 |
| imi_vmx30ui/dataset18 | 64 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset19 | 0 | 14 | 0 | False | 1 |
| imi_vmx30ui/dataset4 | 0 | 4 | 0 | False | 1 |
| imi_vmx30ui/dataset5 | 17 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset6 | 63 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset7 | 61 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset8 | 64 | 0 | 0 | False | 1 |
| imi_vmx30ui/dataset9 | 11 | 2 | 0 | True | 1 |

### exclude: machine_date_group

| Group | Native 0 | Native 1 | Native 2 | Both classes | Folders |
| --- | --- | --- | --- | --- | --- |
| imi_vm20i/20240226 | 409 | 34 | 0 | True | 11 |
| imi_vm20i/20240229 | 402 | 62 | 0 | True | 10 |
| imi_vm20i/20240302 | 43 | 142 | 0 | True | 4 |
| imi_vmx30ui/20240227 | 144 | 33 | 0 | True | 4 |
| imi_vmx30ui/20240228 | 295 | 46 | 0 | True | 7 |
| imi_vmx30ui/20240229 | 0 | 4 | 0 | False | 1 |
| imi_vmx30ui/20240302 | 141 | 15 | 0 | True | 4 |

### exclude: calendar_date_group

| Group | Native 0 | Native 1 | Native 2 | Both classes | Folders |
| --- | --- | --- | --- | --- | --- |
| 20240226 | 409 | 34 | 0 | True | 11 |
| 20240227 | 144 | 33 | 0 | True | 4 |
| 20240228 | 295 | 46 | 0 | True | 7 |
| 20240229 | 402 | 66 | 0 | True | 11 |
| 20240302 | 184 | 157 | 0 | True | 8 |
