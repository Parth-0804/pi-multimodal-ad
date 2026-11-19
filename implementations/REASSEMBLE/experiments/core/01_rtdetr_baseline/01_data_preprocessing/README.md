# 01 — Data preprocessing and inputs

1. Select video timestamps inside the annotated interval, including both endpoints.
2. Choose 16 evenly ranked in-interval frame indices using `linspace(...).round()`; these are 16 frames over the action, not a 16-fps clip.
3. Decode BGR frames to RGB. The saved processor resizes to 640 × 640 and rescales pixels by 1/255; its `do_normalize` is false. Raw example videos are 640 × 480.
4. Pass frames through the frozen RT-DETR R18 backbone. Spatially average each of the final three maps (128, 256 and 512 channels), concatenate, and average across frames: **one 896-value vector per action**.
5. Fit the feature standardizer using only the current training partition, then transform the vectors before the learned head. Missing/nonfinite transformed values become zero.

The detector's box decoder is not used for this classifier. Frozen visual extraction is still model inference when executed; this guide only opens saved evidence.

- [Alignment functions](../../../../src/reassemble/alignment.py)
- [Frame selection, feature extraction and statistics](../../../../src/reassemble/section1_features.py)
- [Training-only standardizer](../../../../src/reassemble/section1_models.py)
- [Example channel schema](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/sensor_channel_schema.csv)
- [Example frame indices](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/frame_selection.csv)
- [Saved feature archive for the example recording](../../../../runs/reassemble/20260927T154732Z-section1/features/2025-01-13-16-45-31.npz)

The feature archive uses `row_index` to map its recording-local rows back to the frozen cohort; do not index a per-recording archive directly with global row 3326. Keys: `sensor` [N,512,22], `statistics` [N,220], `visual` [N,896], and `frame_indices` [N,16].

Next: [02 — Model](../02_model/README.md).
