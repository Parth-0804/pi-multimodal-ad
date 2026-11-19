# 01 — Data preprocessing and inputs

Both branches refer to the **same labelled action segment**. The visual path produces 896 frozen features and then a learned classifier probability. The sensor path starts with the same 512 × 22 aligned sequence used in the sensor baseline, but summarizes it into **220 statistics**, then uses a balanced logistic classifier.

There are 10 statistics per scalar channel: mean, standard deviation, median, minimum, maximum, 25th percentile, 75th percentile, range, RMS and slope over normalized progress. The stored feature vector is **statistic-major** (22 means, then 22 standard deviations, and so on). Fitted scaling uses training data only.

For static fusion, convert each branch's logit to a calibrated failure probability. The stacker's two columns are `[p_rtdetr, p_sensor_statistics]`. Their row identities and held-out partitions must match. PatchTST probabilities are not inputs to this core stacker.

- [Alignment functions](../../../../src/reassemble/alignment.py)
- [Frame selection, feature extraction and statistics](../../../../src/reassemble/section1_features.py)
- [Training-only standardizer](../../../../src/reassemble/section1_models.py)
- [Example channel schema](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/sensor_channel_schema.csv)
- [Example frame indices](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/frame_selection.csv)
- [Saved feature archive for the example recording](../../../../runs/reassemble/20260927T154732Z-section1/features/2025-01-13-16-45-31.npz)

The feature archive uses `row_index` to map its recording-local rows back to the frozen cohort; do not index a per-recording archive directly with global row 3326. Keys: `sensor` [N,512,22], `statistics` [N,220], `visual` [N,896], and `frame_indices` [N,16].

Next: [02 — Model](../02_model/README.md).
