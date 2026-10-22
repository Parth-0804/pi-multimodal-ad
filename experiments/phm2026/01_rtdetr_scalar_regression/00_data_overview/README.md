# 00 — Dataset and one sample

The governed PHM scope covers EXP-A Runs 1–5, EXP-B Runs 1–7 and EXP-F Runs 1–8. Model 1 uses the image-view samples in the pinned model manifest; it does not consume HF/LF/CI sensor streams.

| Partition | Experiment | Runs | Included image views |
|---|---|---|---:|
| Training | EXP-B | 1–7 | 448 |
| Validation | EXP-A | 1–5 | 323 |
| Held-out test | EXP-F | 1–8 | 224 |

**One sample is one image view**, identified by `sample_id`, `image_id`, `source_member_id`, experiment, run, inspection and tooth. Multiple views of a tooth are different image samples, combined later for tooth-level evaluation. Image capture is after the same run, so this is retrospective estimation, not prediction before that run.

Example: **EXP-F / Run 1 / Tooth 01**, from `photos/EXP-F/Exp-F_Photos_Run-1.zip!Run 1/Tooth 01.jpg`. Its saved image dimensions are 2560 × 1440. The example is the first test sample sorted by run, tooth and sample ID, selected independently of prediction error.

The sample's target is **2.555844% candidate area** under target definition `phm2026_image_damage_v2`, with status `provisional_pending_human_review`. A run number or lifecycle stage is not the target.

- [Sample manifest](../../../../runs/phm2026_model_dataset/20260814T013357354377Z-6b068cab/tables/model_sample_manifest.parquet)
- [Split manifest](../../../../runs/phm2026_model_dataset/20260814T013357354377Z-6b068cab/tables/split_manifest.parquet)
- [Saved split-validation report](../../../../runs/phm2026_model_dataset/20260814T013357354377Z-6b068cab/reports/split_validation.json)
- [Image identity, source member and target measurement](../../../../runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/tables/image_manifest.parquet)
- [Target quality and provisional status](../../../../runs/phm2026_image_target/20260814T012054997053Z-e195f6d9/reports/target_quality_report.json)

The historical split audit records no experiment/run or near-duplicate groups crossing partitions. This is not an independent resolution of the organizer's 311-file EXP-A Run-2 overlap warning; raw files remain preserved and no deduplication was performed here.

Next: [01 — Preprocessing](../01_data_preprocessing/README.md).
