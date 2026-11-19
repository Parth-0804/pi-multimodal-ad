# 02.3 — Training and saved parameters

The development split is EXP-B training, EXP-A validation, EXP-F test. It is not the five-fold scheme used by REASSEMBLE, and this saved run did not refit on EXP-A+EXP-B.

Feature standardization and target standardization use EXP-B only. The saved feature list contains 768 image values plus `feature_latency_ms`; its input width is 769, not the 768 shown in the historical architecture description. The scalar head minimizes MSE in standardized target units, with AdamW (learning rate 0.001, weight decay 0.0001), batch size 32, seed 20260814. The configured maximum is 30 epochs with patience 5. The saved run completed **6 epochs** and selected **epoch 1** by validation MSE. A separate eight-sample, 100-step overfit check tested basic trainability; it is not held-out performance evidence.

| File | Role |
|---|---|
| [Pretrained detector](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/checkpoints/rtdetr-l.pt) | Frozen feature extractor |
| [Best head](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/checkpoints/best_head.pt) | Selected regression-head state dictionary |
| [Last head](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/checkpoints/last_head.pt) | Final epoch state; different from selected best state |
| [Saved scalers](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/config/preprocessing_target_scalers.json) | Feature ordering, 769 means/scales (including latency), target mean/scale |
| [Training summary](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/reports/training_summary.json) | Epoch selection, overfit check, counts and test-use declaration |
| [Loss history](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/training_history.csv) | Training and validation MSE by epoch |
| [Provenance](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/provenance.json) | Original command, Git identity, packages and pinned source runs |

`best_head.pt` alone does not reconstruct the full pipeline: the architecture/config, frozen pretrained extractor, exact feature ordering and both scalers are also required. No checkpoint was loaded or executed to create this guide.
