# 01 — Target construction and model-input preprocessing

There are two paths from the same photograph. Keep them distinct when validating the implementation.

**Path A: construct the provisional target.** `measure_damage_candidate` crops the fixed normalized ROI `[0.08,0.12,0.92,0.50]`, applies CLAHE to LAB luminance, estimates a Gaussian background (sigma 31 pixels), and thresholds robust dark-residual z-scores at 2.0. Morphological opening/closing and a horizontal-component filter retain candidate regions. The output is `100 × candidate_pixels / ROI_pixels`.

For the example, the saved counts are **30,058 candidate pixels / 1,176,050 ROI pixels = 2.555844%**. This is a deterministic pseudo-label, pending human review. The existing overlay shows its candidate regions; it is not a predicted detection result.

**Implementation detail to preserve:** the function calculates `gradient_z` and the config contains `gradient_z_threshold`, but the current candidate-mask expression uses only `residual_z`. This guide describes that behavior; it does not alter the formula.

**Path B: construct the model input.** `extract_features` decodes the full image as BGR, then calls Ultralytics RT-DETR prediction preprocessing: scale-fill to 640 × 640, BGR → RGB, BCHW float values divided by 255, with no pixel mask. The ROI crop and candidate mask from Path A are not the input to Model 1.

Forward hooks read the three 256-channel feature maps at layers 21, 24 and 27. Spatial averaging gives three 256-value vectors; concatenating gives **768 features per image**. The existing extraction call runs the detector to obtain these intermediate maps, but box outputs do not define the scalar prediction. **The actual head input then contains 769 columns:** the prefix-based column selector includes `feature_latency_ms` alongside those 768 image features. The saved scaler confirms this ordering. Feature means/scales and target mean/scale are fitted on EXP-B training rows only. The linked historical diagram shows the 768 extracted image features but does not reveal the extra head input; see [the implementation finding](../KNOWN_IMPLEMENTATION_ISSUES.md).

- [Target function](../../../../src/phm2026/targets/image_damage.py)
- [Frozen target configuration](../../../../runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/config/resolved_config.yaml)
- [Feature extraction implementation](../../../../src/phm2026/models/rtdetr/regression.py)
- [Saved tensor shapes](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/tensor_shapes.csv)
- [Saved 995 × 768 feature values with identity columns](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/cache/encoder_features.parquet)
- [Training-only feature and target scalers](../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/config/preprocessing_target_scalers.json)

Next: [02 — Model](../02_model/README.md).
