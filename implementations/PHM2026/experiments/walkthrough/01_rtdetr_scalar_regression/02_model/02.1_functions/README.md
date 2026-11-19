# 02.1 — Functions

Open the source and search for the named function/class. These are navigation links, not duplicated executable modules.

| Stage | Source | Function/class | Input → output |
|---|---|---|---|
| Define target | [image_damage.py](../../../../../src/phm2026/targets/image_damage.py) | `measure_damage_candidate` | RGB photo → candidate mask and area percentage |
| Build sample identity and partition | [model_dataset.py](../../../../../src/phm2026/targets/model_dataset.py) | `build_image_samples` | target/image tables → image sample manifest |
| Extract frozen features | [regression.py](../../../../../src/phm2026/models/rtdetr/regression.py) | `extract_features` | full image → 768 values |
| Define scalar head | [regression.py](../../../../../src/phm2026/models/rtdetr/regression.py) | `RegressionHead` | 769 selected values, including latency → scalar in standardized target space |
| Scale, train, early-stop | [regression.py](../../../../../src/phm2026/models/rtdetr/regression.py) | `train_head` | training/validation features → head states and scalers |
| Generate image prediction | [regression.py](../../../../../src/phm2026/models/rtdetr/regression.py) | `predict_all` | features + head + scalers → percentage prediction |
| Combine image views and teeth | [regression.py](../../../../../src/phm2026/models/rtdetr/regression.py) | `aggregate_predictions` | image predictions → tooth maxima → run top-three means |
| Calculate performance | [regression.py](../../../../../src/phm2026/models/rtdetr/regression.py) | `build_metrics` | image/tooth/run predictions → metric table |
| Metric formulas | [regression.py](../../../../../src/phm2026/evaluation/regression.py) | `regression_metrics` | target/prediction pairs → MAE, RMSE, R², correlations |
| Write historical run | [regression.py](../../../../../src/phm2026/models/rtdetr/regression.py) | `write_regression_run` | results → tables, figures, checkpoints and provenance |

[Original training entry point](../../../../../scripts/phm2026/training/train_rtdetr_regression.py) orchestrates these steps. Do not run it just to browse this guide: it can download a model, extract features and train.
