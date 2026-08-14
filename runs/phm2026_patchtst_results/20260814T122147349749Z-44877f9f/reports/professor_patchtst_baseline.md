# Professor report: initial sensor-only PatchTST baseline

## Scientific formulation

The model estimates the **current post-run damage state** from sensor history collected during that run. Six hours is a typical run/cadence description, not a forecast horizon. The primary response is the provisional image-derived `raw_top3_mean_pct` from `phm2026_image_damage_v2`; it is not organizer ground truth or validated physical spall area.

## Dataset and split

There are 20 independent run sequences: EXP-B (7) trains, EXP-A (5) validates/early-stops, and EXP-F (8) is evaluated once after configuration selection. The 7,119 chronological minute records are repeated observations within those 20 samples, not independent labels. Five timestamp-missing EXP-F records remain traceable but are excluded.

## Inputs and preprocessing

The initial bounded baseline uses RPM, torque, temperature, organizer axial/radial RMS, and FM4/NA4/M6A/ALR from LF archives. Each minute/channel contributes mean, population standard deviation, median, min, max, last, and slope per within-file sample index plus a channel missingness mask. EXP-B alone supplies imputation medians and scaling statistics. No raw high-frequency waveform or FFT cache is used.

## EXP-F raw-target results

- `sensor_training_median`: MAE 0.680, RMSE 0.771, Spearman nan, R² -0.0008784413845237538, N=8.
- `sensor_training_mean`: MAE 0.680, RMSE 0.777, Spearman nan, R² -0.015278162718699084, N=8.
- `patchtst_sensor_regression`: MAE 1.011, RMSE 1.243, Spearman -0.261904761904762, R² -1.6009302743599494, N=8.
- `sensor_ridge_run_summary`: MAE 5.015, RMSE 11.311, Spearman 0.09523809523809526, R² -214.27244792264398, N=8.

PatchTST does **not** outperform the constant sensor baselines on EXP-F in this canonical seed. Ridge is severely unstable because the summary dimension is large relative to seven training runs. Negative results are retained without EXP-F tuning. Run-bootstrap intervals are included but are intrinsically unstable at N=8.

## Interpretation

This result does not establish that sensor history lacks damage information. It shows that this compact initial representation/model, trained on seven runs under strong domain separation, does not beat a constant baseline on the provisional target. The image-only RT-DETR comparison is descriptive and uses the same EXP-F run target rows, but it is a separate modality.

## Next gate

Before any complex PatchTST or fusion work: complete human review of the image-derived target, review LF channel/path/unit coverage, and pre-register a small number of train/validation-only changes. Do not use EXP-F to select them.
