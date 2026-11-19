# Initial sensor-only PatchTST baseline

This run estimates the **current end-of-run** provisional image-derived damage state from compact, chronological one-minute sensor features. It is not six-hour-ahead forecasting.

The fixed split is EXP-B train, EXP-A validation, and untouched EXP-F test. The primary target is `raw_top3_mean_pct` from `phm2026_image_damage_v2`; it remains provisional pending human image review.

The initial input deliberately excludes raw 102.4-kHz vibration. It uses bounded LF context, organizer RMS, and FM4/NA4/M6A/ALR summaries. Missing values are training-median imputed and standardized using EXP-B only.

Metrics in the accompanying tables compare training mean, training median, Ridge, PatchTST, and the pinned image-only RT-DETR result only at matching run-level target and split. With only eight EXP-F test runs, results are descriptive rather than conclusive.
