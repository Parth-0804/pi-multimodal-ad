# 02.1 — Function map

Open the linked source file, then search for the function or class name. These are the existing implementations; this folder adds no duplicate Python modules.

| Step | Source | Function/class | Input → output |
|---|---|---|---|
| Choose eligible cohort | [section1_features.py](../../../../../src/reassemble/section1_features.py) | `cohort` | inventory rows → paired cohort |
| Align streams | [alignment.py](../../../../../src/reassemble/alignment.py) | `interval_indices, resample_progress` | timestamps and interval → selected frames / sensor grid |
| Build feature arrays | [section1_features.py](../../../../../src/reassemble/section1_features.py) | `extract, statistics` | segment media → 896 visual / 512×22 sensor / 220 statistics |
| Restore row order | [section1_models.py](../../../../../src/reassemble/section1_models.py) | `load_features` | recording caches → cohort-aligned arrays |
| Scale inputs | [section1_models.py](../../../../../src/reassemble/section1_models.py) | `Standardizer` | training inputs → fitted scaling |
| Define network | [section1_models.py](../../../../../src/reassemble/section1_models.py) | `SensorHead` | model inputs → logit and 128-dimensional embedding |
| Train and select | [section1_models.py](../../../../../src/reassemble/section1_models.py) | `neural_fit, evaluate_model` | training/inner folds → selected epoch and held-out outputs |
| Calibrate probability | [section1_models.py](../../../../../src/reassemble/section1_models.py) | `calibrate` | inner OOF logits → calibration and threshold |
| Calculate performance | [section1_report.py](../../../../../src/reassemble/section1_report.py) | `metrics` | held-out probabilities, decisions and labels → metrics |

Training and extraction entry points write outputs and can load/download models. Reading source is sufficient for this walkthrough; no entry point was executed to create it.
