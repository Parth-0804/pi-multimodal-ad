# 02.2 — Initial architecture

```text
16 × 3 × 640 × 640 RGB pixels per action
  → frozen pretrained RT-DETR R18 backbone
  → spatial mean of 128-, 256-, 512-channel maps
  → concatenate to 896 features per frame
  → mean over 16 frames → [896]
  → training-only standardization
  → Linear(896,128) → ReLU → Dropout(0.1)
  → Linear(128,1) → failure logit
  → inner-OOF logistic calibration → failure probability
```

Pretrained identity: `PekingU/rtdetr_r18vd`, revision `ac77a11ff0170a41b771c03264987f8ce2b0d753`. Only the classification head is fitted in this baseline. The 128-value representation is the learned head embedding, not the raw backbone feature vector.

[Original model configuration](../../../../../runs/reassemble/20260927T154732Z-section1/config.json) · [Saved pretrained backbone and image processor details](../../../../../runs/reassemble/20260927T154732Z-section1/pretrained_model.json)
