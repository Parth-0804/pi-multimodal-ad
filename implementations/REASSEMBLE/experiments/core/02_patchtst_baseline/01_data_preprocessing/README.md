# 01 — Data preprocessing and inputs

1. Read measured force, measured torque, gripper positions, joint efforts and joint velocities. Together they contain **22 scalar channels**; preserve their configured order.
2. Select each stream's finite samples inside the action interval, including endpoints.
3. Interpolate onto 512 evenly spaced action-progress positions. Do not extrapolate outside available samples; leave gaps longer than five native sampling intervals missing.
4. Concatenate the five groups into **[512 positions, 22 channels] per action**. These positions represent normalized action progress, not 512 seconds or a common sampling frequency.
5. Estimate each channel's mean and standard deviation using the current training partition over samples and time. Transform all required inputs with those training values; fill missing transformed entries with zero. Retain the original finite-value mask for the model call.

The plot shortcut uses per-channel visualization scaling within this one sample. That is different from the training-only preprocessing above.

- [Alignment functions](../../../../src/reassemble/alignment.py)
- [Frame selection, feature extraction and statistics](../../../../src/reassemble/section1_features.py)
- [Training-only standardizer](../../../../src/reassemble/section1_models.py)
- [Example channel schema](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/sensor_channel_schema.csv)
- [Example frame indices](../../../../artifacts/presentation/reassemble_dataset_assets/20261016T092947Z/frame_selection.csv)
- [Saved feature archive for the example recording](../../../../runs/reassemble/20260927T154732Z-section1/features/2025-01-13-16-45-31.npz)

The feature archive uses `row_index` to map its recording-local rows back to the frozen cohort; do not index a per-recording archive directly with global row 3326. Keys: `sensor` [N,512,22], `statistics` [N,220], `visual` [N,896], and `frame_indices` [N,16].

Next: [02 — Model](../02_model/README.md).
