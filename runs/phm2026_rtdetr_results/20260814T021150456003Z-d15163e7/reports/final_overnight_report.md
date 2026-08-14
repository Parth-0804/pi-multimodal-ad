# Final PHM T2 and RT-DETR engineering report

> **PROVISIONAL PSEUDO-TARGET — pending human mask validation; not organizer ground truth or validated physical spall performance.**

## Official formulation

The official challenge requires a self-defined scalar from 28 post-run tooth images and a later sensor-only estimator. This work estimates end-of-run current damage state. Six hours is typical run/inspection/output cadence, not a six-hour-ahead horizon. Pairing uses verified experiment/run/tooth identity.

## Target and dataset

Target version `phm2026_image_damage_v2`: elongated dark candidate pixels / normalized visible-flank ROI, maximum across views per tooth, raw top-3 tooth mean per run, plus causal cumulative-maximum alternative. All 1,311 images decoded; 560 tooth/run records and 20 run targets; 0 decode exclusions; 560 human reviews pending. EXP-A/B close-up protocol differs from EXP-F canonical views.

The image baseline has 995 view samples: 448 EXP-B train, 323 EXP-A validation, 224 untouched EXP-F test, with zero run/near-duplicate cross-split violations. T2.2 also records 7,124 one-minute HDF5 members and 20 run windows; compact sensor features were deliberately not fabricated or extracted in this image task.

## Baselines and RT-DETR

Training-mean EXP-F MAE: 1.020 percentage points. The frozen RT-DETR-L encoder (32,148,140 parameters) plus 98,689-parameter head early-stopped after 6 epochs; best epoch 1. EXP-F image MAE 0.894, RMSE 1.563, Spearman 0.361, R² -1.176. Negative R² and out-of-range predictions show weak cross-protocol calibration despite improved MAE.

Preprocessing: original 1440×2560×3 image → Ultralytics scale-fill 640×640 → RGB BCHW float32/255 → 80×80, 40×40, 20×20 256-channel maps → pooled 768-vector → scalar. Median encoder latency 35.50 ms/image on Tesla T4.

## Limitations and review

Masks can include shadows/edges; no organizer labels or verified boxes exist; metrics quantify pseudo-label emulation only. Human reviewers must accept/reject/correct every selected overlay and assess A/B-versus-F acquisition bias before target freezing. No PatchTST, sensor-model training, fusion, leaderboard work, or official test/validation modelling occurred.

## Reproduce

```bash
ma_thesis_env/bin/python -B scripts/derive_image_targets.py
ma_thesis_env/bin/python -B scripts/build_model_dataset.py
ma_thesis_env/bin/python -B scripts/evaluate_naive_baselines.py
ma_thesis_env/bin/python -B scripts/train_rtdetr_regression.py
ma_thesis_env/bin/python -B scripts/generate_rtdetr_results.py
```

Exact source runs/hashes are in `config/resolved_config.yaml` and `manifests/inputs.json`; figure sources are indexed in `reports/figure_index.md`. Referenced source-run storage at report time: 0.690 GiB. Next gate before PatchTST: complete human target review, revise/freeze target, then run a separately bounded streaming sensor-feature build.
