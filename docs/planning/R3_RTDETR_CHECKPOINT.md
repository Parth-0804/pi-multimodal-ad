# R3 RT-DETR checkpoint

Status: **PROVISIONAL ENGINEERING BASELINE COMPLETE**  
Run: `20260814T020338751021Z-d0f225c8`

## Formulation and compute

No verified boxes/classes exist. The selected model is an **RT-DETR-derived image-regression baseline**, not unchanged detection: COCO-pretrained RT-DETR-L frozen multi-scale encoder → global average pooling of 80×80, 40×40 and 20×20 256-channel maps → concatenated 768-vector → 768→128→1 scalar head.

Ultralytics scale-fills 1440×2560 BGR input to 640×640, converts BGR→RGB/BCHW float32/255 and uses no pixel mask. Encoder features were computed once for 995 images. Only the 98,689-parameter head trained; the encoder has 32,148,140 frozen parameters. Tesla T4 peak allocated CUDA memory was 259 MB. Median encoder inference was 35.50 ms/image (95th percentile 36.43 ms; first-call maximum 1,386 ms).

Tiny-batch MSE fell from 1.382 to 0.0000078. The bounded training early-stopped after 6 epochs with best epoch 1. Only pretrained encoder, best head and last head are retained.

## Results

On untouched EXP-F:

- image/tooth MAE 0.894, RMSE 1.563, Spearman 0.361, R² −1.176;
- raw run top-3 MAE 1.347, RMSE 1.757, Spearman 0.571 (8 runs);
- monotonic run top-3 MAE 1.920, RMSE 2.203.

The image-view MAE beats the training-mean baseline (1.020), but negative R², out-of-range predictions (−0.424 to 19.579 versus pseudo-target 0.285–8.793), acquisition-protocol shift and unreviewed masks preclude physical-damage claims. EXP-F was not used for tuning.

Primary artifacts:

- `runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/reports/rtdetr_regression_report.md`
- `runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/tables/metrics.csv`
- `runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/checkpoints/{best_head.pt,last_head.pt}`
- `runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/figures/`

Next scientific gate: complete human target review and revise/freeze the target before any PatchTST or sensor-to-damage training.
