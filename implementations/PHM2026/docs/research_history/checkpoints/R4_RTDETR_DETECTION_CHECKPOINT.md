# R4 genuine RT-DETR detection checkpoint

Status: **COMPLETE — EXECUTION VALID, SCIENTIFIC PERFORMANCE FAILED/WEAK**  
Evidence date: 2026-08-14  
Canonical run: `20260814T043751107678Z-7f1e13af`

## Formulation

This is a genuine one-class Ultralytics RT-DETR-L detector: backbone,
multiscale/hybrid encoder, transformer decoder/object queries, classification
head, and bounding-box head were retained. It is different from the earlier
frozen-encoder scalar-regression baseline.

Training used pseudo-boxes only. All reported detection metrics therefore mean
agreement with provisional masks, not validated physical-damage accuracy.

## Frozen study design

- Train: EXP-B, 448 images.
- Validation/model and confidence selection: EXP-A, 323 images.
- Test: EXP-F, 224 images, evaluated once after selection.
- Input: scale-fill to 640×640, batch 4.
- One smoke epoch, one frozen warm-up epoch, then bounded fine-tuning with
  AdamW and validation early stopping.
- Fine-tune layers: first 9 detector layers frozen; 25,156,067 configured
  trainable parameters and 6,829,728 frozen parameters.
- Best and last detector checkpoints are the only retained model checkpoints.
- EXP-F did not select epochs, checkpoint, confidence, or augmentation.

## Result

Training completed in 234.19 seconds on a Tesla T4. Early stopping selected
epoch 1 after four fine-tune epochs. Peak CUDA allocation was 2,448,414,208
bytes. PyTorch warned that CUDA grid-sampler backward lacks a deterministic
implementation; deterministic mode was warn-only, so exact bitwise rerun
identity is not promised.

Every EXP-A confidence candidate from 0.01 through 0.60 had zero true
positives. The deterministic tie rule selected 0.60. On the single EXP-F pass:

- N=224 images; 9,883 pseudo-boxes;
- 67,200 raw low-confidence predictions before the operating threshold;
- at confidence 0.60: TP=0, FP=0, FN=9,883;
- precision=0, recall=0, F1=0;
- mAP@0.50=0.000083;
- mAP@0.50:0.95=0.000016;
- all 224 images were false-negative images at the operating point.

The small nonzero AP is rank-based over low-confidence raw predictions; it does
not contradict the absence of retained detections at 0.60. This is an honest
negative result. It suggests that the dense texture-like pseudo-components,
short schedule, and EXP-F protocol/domain shift are poorly matched to this
detector formulation.

## Pinned evidence

- Configuration SHA-256:
  `7f1e13af9eea8e24ddd9145e82af0731742ef5b65cedc905884646d901510c87`.
- Best detector SHA-256:
  `129d143cf7511fc4b0d95a0ffff064ac117e92e8a6eb5290c76d777d70fe7970`.
- Detection metrics SHA-256:
  `c0cd7b7d91b254f859d02f7a1f3bbef18b1bfbcfcf77caee450d8c7c7f805bb2`.
- Output manifest SHA-256:
  `8da9eec1db9cd1589356b757bf05ff1055301d7bd158da0afde87df6714bd1e5`.
- Canonical directory:
  `runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af/`.

The run includes prediction/metric tables, threshold selection, AP-by-IoU,
latency, tensor shapes, deterministic examples, PNG/SVG figures, configuration,
input/output manifests, and environment provenance. Physical validity remains
blocked on expert review of the source masks and pseudo-boxes.
