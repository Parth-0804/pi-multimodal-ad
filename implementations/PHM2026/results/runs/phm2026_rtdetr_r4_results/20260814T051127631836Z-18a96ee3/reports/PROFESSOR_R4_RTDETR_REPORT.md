# Professor report: genuine and multitask RT-DETR on PHM images

> **All masks, boxes, and scalar targets in this package are provisional pseudo-labels pending expert review. Detection metrics measure pseudo-label agreement; scalar metrics measure pseudo-target agreement. Neither is validated physical-spall performance.**

## Question-first summary

**What entered the models?** Exactly 995 post-run gear-tooth image views: EXP-B 448 for training, EXP-A 323 for validation/model selection, and EXP-F 224 for the single held-out test. Images were decoded from the one bounded versioned cache and scale-filled to `B×3×640×640` RGB float tensors. Sensor data was not used.

**What was predicted?** Model A predicted one-class `damage_candidate` boxes/classes/confidences. Model B retained those genuine RT-DETR outputs and added one scalar per image from the shared layer-27 encoder feature. The scalar is the exact pinned `phm2026_image_damage_v2` candidate-area percentage, not organizer ground truth.

**What was comparison truth?** Pseudo-boxes were connected components from the deterministic mask replay inside the visible-flank ROI. Per-view scalar predictions were compared with the corresponding provisional candidate-area value. Multiple views of a tooth aggregate by maximum; 28 tooth values aggregate by the mean of the three largest. A causal cumulative maximum is reported separately. The task estimates the current state after a run, not six-hour-ahead damage.

**Was the split random?** No. It was persisted before these models: EXP-B train / EXP-A validation / EXP-F test, with no run, inspection, tooth group, or known near-duplicate group crossing. EXP-F was not used for tuning.

## Traceability and count reduction

The exact evidence funnel is 1,311 discovered JPGs → 995 model-ready views → 560 tooth/run records → 20 run targets. Extra EXP-A/B close-ups are combined at tooth level; excluded baseline/break-in/unpaired records never become model samples. EXP-F is a canonical-view-only acquisition protocol, so it is also a domain shift.

The pseudo-box run retained 30,628 boxes over all 995 images, with zero negative images and zero whole-ROI boxes. This dense all-positive result is a central scientific limitation: the heuristic frequently describes texture/surface candidates rather than expert-confirmed spalls.

## Genuine detector result (Model A)

The real RT-DETR-L detection architecture was fine-tuned; this was not frozen pooled-feature regression. EXP-A selected confidence 0.60, but every validation threshold had zero true positives. The one EXP-F pass produced TP=0, FP=0, FN=9,883 at that operating point, mAP@0.50=0.000083, and mAP@0.50:0.95=0.000016. This is a valid negative result.

## Multitask result (Model B)

The multitask model jointly optimized the standard Ultralytics RT-DETR detection loss and a SmoothL1 scalar loss. Encoder layer 27 (`B×256×20×20`) feeds a global-pool 256→128→1 head without detachment. A train-only shared-gradient ratio selected λ=58.261490. EXP-A early stopping selected epoch 2; EXP-F was then evaluated once.

At EXP-A-selected confidence 0.01, EXP-F detection yielded precision=0.001525, recall=0.008904, F1=0.002604, mAP@0.50=0.000054, and mAP@0.50:0.95=0.000013. It therefore did not solve the dense pseudo-box task.

Scalar EXP-F results were view MAE=0.732990 percentage points (N=224, run-grouped 95% bootstrap interval 0.656733–0.838133), RMSE=0.971507, Spearman=0.494771, and R²=0.159300. Raw run-top-3 MAE was 1.627254 pp (N=8); causal-monotonic run MAE was 1.854585 pp (N=8).

At image/view level, the multitask MAE (0.733) is lower than training mean (1.020), training median (1.203), and earlier frozen-encoder RT-DETR regression (0.894). At raw run level, the earlier frozen model is lower (1.347) than multitask (1.627); therefore no blanket improvement claim is supported. Frozen-model confidence intervals were not recomputed, and all results depend on the same provisional pseudo-target.

## Reproducibility, resources, and limitations

Model A best checkpoint: `129d143cf7511fc4b0d95a0ffff064ac117e92e8a6eb5290c76d777d70fe7970`. Model B best checkpoint: `7acc98726701925abd0a7c9d5c30e937943ce7acead53d75322374d4777c32c1`. Model B trained 160.62 seconds on a Tesla T4, peaked at 2,654,548,480 CUDA bytes, and retained best/last checkpoints only. PyTorch warned that CUDA grid-sampler backward is not bitwise deterministic; fixed seeds and persisted splits do not remove that kernel limitation.

Human/expert review must verify the ROI, mask, boxes, per-tooth values, and failure cases before these values can support physical-damage claims. The detector's near-zero pseudo-label agreement and all-positive/dense annotation pattern are evidence against presenting it as a successful damage detector. Generic COCO classes were never reinterpreted as damage. No PatchTST, sensor features, fusion, leaderboard, or official test modeling was performed.

See `reports/FIGURE_INDEX.md`, `tables/source_artifact_index.csv`, and the input/output manifests for exact evidence lineage.
