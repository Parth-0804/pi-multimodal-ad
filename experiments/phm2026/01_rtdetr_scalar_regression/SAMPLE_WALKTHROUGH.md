# Follow one PHM sample through 00 → 03

Example selected by sorting test samples by run, tooth and sample ID, without considering model scores: **EXP-F / Run 1 / Tooth 01**.

| Stage | What to inspect | Saved evidence for this sample |
|---|---|---|
| 00 — Dataset/sample | Image manifest and model manifest | Source `photos/EXP-F/Exp-F_Photos_Run-1.zip!Run 1/Tooth 01.jpg`; held-out test; 2560 × 1440 pixels |
| 01 — Target path | Saved target measurement | 30,058 candidate pixels / 1,176,050 ROI pixels × 100 = 2.555843714% |
| 01 — Model-input path | Full image preprocessing, then feature cache | 640 × 640 RGB input → three feature maps → 768-value vector |
| 02 — Model | Frozen extractor, best head and saved scalers | 768 image features + extraction latency → 769 → 128 → 1; best head epoch 1; inverse target scaling |
| Fusion | No fusion in this experiment | Single image modality; later aggregation combines views/teeth |
| 03 — Prediction | Join prediction table by `sample_id` | 3.336106300% predicted; 2.555843714% provisional target |
| 03 — Evaluation | Compute error in percentage points | Absolute error = 0.780262586; whole-test MAE = 0.893852 |
| 03 — Results | Original tables and report | Image, tooth and run metrics remain distinct |

Sample ID: `image_sample_b8cab099479eb3703e8e1f04bc872082980c5b07812920f00556d31f502901f7`.

Image ID: `image_profile_7caa4c75509287f4b97efcffef693ad6e3659edc4875250bc58bbf36ce769b3d`.

Source member ID: `archive_member_ce84626c3766d6bea9ed3221f82343ed2cd74ade90d6646876c326104db0acb1`.

The images, feature table and predictions use these identifiers, not a universal row number. The target's name `y_true_raw` in a prediction table does **not** turn the heuristic into ground truth.

- [00 — Sample definition](00_data_overview/README.md)
- [01 — Both preprocessing paths](01_data_preprocessing/README.md)
- [02 — Architecture](02_model/02.2_initial_architecture/README.md)
- [03 — Predictions and interpretation](03_model_outputs_and_results/README.md)
- [The retained target overlay](../../../runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/overlays/image_profile_7caa4c75509287f4b97efcffef693ad6e3659edc4875250bc58bbf36ce769b3d.jpg)
- [Exact sample table](../../../runs/phm2026_model_dataset/20260814T013357354377Z-6b068cab/tables/model_sample_manifest.parquet)
- [Saved features](../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/cache/encoder_features.parquet)
- [Saved predictions](../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/predictions.parquet)
