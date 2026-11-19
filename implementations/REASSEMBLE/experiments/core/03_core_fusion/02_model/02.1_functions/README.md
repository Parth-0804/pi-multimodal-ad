# 02.1 — Function map

Open the linked source file, then search for the function or class name. These are the existing implementations; this folder adds no duplicate Python modules.

| Step | Source | Function/class | Input → output |
|---|---|---|---|
| Choose eligible cohort | [section1_features.py](../../../../../src/reassemble/section1_features.py) | `cohort` | inventory rows → paired cohort |
| Align streams | [alignment.py](../../../../../src/reassemble/alignment.py) | `interval_indices, resample_progress` | timestamps and interval → selected frames / sensor grid |
| Build feature arrays | [section1_features.py](../../../../../src/reassemble/section1_features.py) | `extract, statistics` | segment media → 896 visual / 512×22 sensor / 220 statistics |
| Restore row order | [section1_models.py](../../../../../src/reassemble/section1_models.py) | `load_features` | recording caches → cohort-aligned arrays |
| Fit branch classifiers | [section1b.py](../../../../../src/reassemble/section1b.py) | `fit_branch` | nested branch fits → calibrated probabilities |
| Prevent partition overlap | [section1b.py](../../../../../src/reassemble/section1b.py) | `guard_partition, subfolds` | recording partitions → validated inner plans |
| Fit static fusion | [section1b.py](../../../../../src/reassemble/section1b.py) | `fit_stacker, stacking` | two probability columns → held-out fused predictions |
| Compare core fusion models | [section2.py](../../../../../src/reassemble/section2.py) | `main` | F1–F6 experiment orchestration |
| Define learned comparison heads | [section2_models.py](../../../../../src/reassemble/section2_models.py) | `ConcatHead, DecisionGate` | features / context → fusion predictions |
| Calculate performance | [section1_report.py](../../../../../src/reassemble/section1_report.py) | `metrics` | held-out probabilities, decisions and labels → metrics |

Training and extraction entry points write outputs and can load/download models. Reading source is sufficient for this walkthrough; no entry point was executed to create it.
