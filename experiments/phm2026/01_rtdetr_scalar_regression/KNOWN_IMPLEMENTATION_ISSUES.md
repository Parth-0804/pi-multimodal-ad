# Review finding: extraction latency entered the trained PHM head

**Status: confirmed from source and saved artifacts; not corrected.** This affects the frozen-encoder scalar-regression baseline run `20260814T020338751021Z-d0f225c8` described here. It does not establish whether other PHM experiments have the same issue.

The extractor writes 768 image features named `feature_0000` through `feature_0767`. It also writes `feature_latency_ms`. Both `train_head` and the saved feature-scaler column list use the prefix `feature_`, so the timing column enters the training inputs and predictions.

Evidence:

- The saved scaler contains **769 column names**, with `feature_latency_ms` last; both mean and scale arrays have length 769.
- The saved training summary reports **98,689 head parameters**, matching 769→128→1: `769*128 + 128 + 128 + 1`. The historical 768→128→1 description would instead imply 98,561 parameters.
- `predict_all` uses this saved column list, so the timing input is part of the retained predictions as well.
- The example EXP-F / Run 1 / Tooth 01 has saved extraction latency 35.242398 ms. No new timing or prediction was measured for this review.

Extraction latency is a runtime quantity, not an image representation. It can vary with hardware, warm-up and execution conditions. Its presence compromises interpreting this retained model as solely a learned function of the 768 image features. The size and direction of its effect on accuracy remain unknown. The numerical metrics can still be checked against the stored predictions, but that check does not validate the intended architecture.

- [Extractor, train_head and predict_all source](../../../src/phm2026/models/rtdetr/regression.py)
- [Exact fitted column order and scalers](../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/config/preprocessing_target_scalers.json)
- [Recorded training summary](../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/reports/training_summary.json)
- [Feature cache including timing column](../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/cache/encoder_features.parquet)
- [Historical architecture description](../../../docs/planning/R3_RTDETR_CHECKPOINT.md)

A separately approved scientific correction should first add a failing regression test for the allowed feature-column names, then make the selector exclude runtime metadata, and preserve this run while producing any new comparison under a unique run ID. Retraining would need explicit authorization. This navigation review changes neither feature selection nor scientific results.

A second observed implementation detail is that target construction calculates `gradient_z` but does not use it in the candidate-mask condition, despite a `gradient_z_threshold` config field. The walkthrough describes the actual residual-only rule. Any methodological correction belongs in a separate reviewed change.
