# 02.2 — Initial architecture

```text
[B,512,22] standardized sensor inputs + finite-value mask
  → patches of length 32, stride 16 → 31 patches per channel
  → PatchTST: d_model=32, 2 layers, 4 attention heads, FFN width=64
  → hidden output [B,22,31,32]
  → mean over patches → [B,22,32] → flatten [B,704]
  → Linear(704,128) → ReLU → Dropout(0.1)
  → Linear(128,1) → failure logit
  → inner-OOF logistic calibration → failure probability
```

`B` is batch size. The encoder starts from random weights (`pretrained=false`); it is trained for classification. The configuration disables internal scaling (`scaling=None`), uses layer normalization and disables input masking (`do_mask_input=False`). The passed observed mask is not a custom attention mask that suppresses all missing positions. See the exact `SensorHead` constructor/forward for the library call.

[Original model configuration](../../../../../runs/reassemble/20260927T154732Z-section1/config.json)
