# R4 multitask RT-DETR checkpoint

Status: **COMPLETE — PROVISIONAL ENGINEERING BASELINE, HUMAN REVIEW PENDING**  
Evidence date: 2026-08-14  
Canonical run: `20260814T050026535618Z-9b00f099`

## Architecture and target

The model retains genuine RT-DETR classification and bounding-box outputs and
adds one scalar output per image. Encoder layer 27 emits
`B×256×20×20`; global average pooling and a 256→128→1 MLP produce the scalar.
The feature is not detached. Standard Ultralytics RT-DETR detection loss is
optimized jointly with SmoothL1 scalar loss, and gradients reach the shared
encoder and scalar head.

The scalar is the exact pinned provisional `target_value_pct` from target
version `phm2026_image_damage_v2`. View values aggregate by maximum to a tooth;
tooth values aggregate by run top-3 mean; a causal cumulative maximum is
retained separately. This estimates current post-run state, not six-hour-ahead
damage.

## Study design and training

- Train EXP-B: 448 image views.
- Validation EXP-A: 323 image views.
- Test EXP-F: 224 image views, evaluated exactly once after selection.
- Input: RGB scale-fill to `B×3×640×640`, batch 4.
- Initial checkpoint: Model A best detector
  `129d143cf7511fc4b0d95a0ffff064ac117e92e8a6eb5290c76d777d70fe7970`.
- First 9 detector layers frozen; 25,963,235 detector parameters and 33,025
  scalar-head parameters trainable.
- AdamW groups: detector LR `1e-5`, scalar head LR `5e-4`.
- Train-only shared-gradient balancing selected λ=58.261490; no EXP-F value
  influenced it.
- Tiny-batch scalar SmoothL1 fell from 1.043545 to 0.446057 in 12 steps.
- Validation early stopping selected epoch 2 and stopped after epoch 4.
- Training time: 160.62 seconds on Tesla T4; peak CUDA allocation:
  2,654,548,480 bytes.

PyTorch emitted a warning that CUDA grid-sampler backward lacks a deterministic
implementation. Seeds and splits are fixed, but bitwise-identical retraining is
therefore not guaranteed.

## Detection result — pseudo-box agreement only

EXP-A selected confidence 0.01. On the sole EXP-F pass (N=224 images,
9,883 pseudo-boxes):

- TP=88, FP=57,606, FN=9,795;
- precision=0.001525, recall=0.008904, F1=0.002604;
- mAP@0.50=0.000054; mAP@0.50:0.95=0.000013;
- mean IoU of the 88 matches=0.573943;
- all 224 test images had both false positives and false negatives.

This is technically functional but scientifically poor detection. It does not
support a claim that RT-DETR learned physical gear damage.

## Scalar result — provisional pseudo-target agreement

EXP-F image/view level (N=224): MAE 0.732990 percentage points, RMSE 0.971507,
Spearman 0.494771, R² 0.159300. The run-grouped 500-repetition MAE interval was
0.656733–0.838133.

EXP-F raw run top-3 (N=8): MAE 1.627254 pp, RMSE 1.751389, Spearman 0.738095.
Causal-monotonic run top-3 (N=8): MAE 1.854585 pp, RMSE 1.998240.

At image level the multitask MAE is lower than train mean (1.020), train median
(1.203), and the earlier frozen-encoder model (0.894). At raw run level the
earlier frozen model is lower (1.347) than multitask (1.627), so a blanket
improvement claim is not supported. Comparisons are level-matched, but the
frozen-model result lacks the newly computed run-grouped interval.

## Pinned evidence

- Configuration SHA-256:
  `9b00f099e73474fa4b13a7e002e3a5fca52362280a9eadda936621b37d577d60`.
- Best checkpoint SHA-256:
  `7acc98726701925abd0a7c9d5c30e937943ce7acead53d75322374d4777c32c1`.
- Last checkpoint SHA-256:
  `dd7b4cf75b0a09e7ffaa13d28373043cb573d55254809b1731b2a70716160e1e`.
- Detection metrics SHA-256:
  `78f3828b4867646eebaeeda1d4c324a0ac8867f80e2a9ac14c8f4b111f7055fa`.
- Scalar metrics SHA-256:
  `e3c3eba8ab1cf81ee3164def1a3cac8e3baa62afd21e07c78bef4cbc84df672e`.
- Output manifest SHA-256:
  `b716ca6ad1ef48995cf8b516a6d704a1de206f55d53c8900bc85816b5fcdf84a`.

Canonical outputs are under
`runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099/`. The final
professor package is
`runs/phm2026_rtdetr_r4_results/20260814T051127631836Z-18a96ee3/`.

The pseudo-target and pseudo-boxes remain unverified physical measurements.
Expert review of masks, boxes, and per-tooth values is the next scientific gate.
