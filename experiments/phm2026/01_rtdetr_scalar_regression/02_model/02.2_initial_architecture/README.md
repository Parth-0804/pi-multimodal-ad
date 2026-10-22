# 02.2 — Initial architecture

```text
One full image → [1,3,640,640]
  → frozen COCO-pretrained Ultralytics RT-DETR-L (rtdetr-l.pt)
  → layer 21 [1,256,80,80]
    layer 24 [1,256,40,40]
    layer 27 [1,256,20,20]
  → average each map over spatial dimensions
  → concatenate [1,768]
  → append feature_latency_ms → [1,769]
  → training-only feature standardization
  → Linear(769,128) → ReLU → Dropout(0.1) → Linear(128,1)
  → inverse training-target standardization
  → provisional candidate-area prediction (% units)
```

The actual saved head has **98,689 trainable parameters**, consistent with 769 inputs. A 768-input head would have 98,561. The extra input is extraction latency, included by the feature-name prefix selector. This differs from the historical 768→128→1 description; see [the detailed finding](../../KNOWN_IMPLEMENTATION_ISSUES.md). The saved environment records 32,148,140 frozen detector parameters. There is no sigmoid output, classification threshold or clipping to [0,100] in the scalar head/prediction code, so the prediction can be negative or exceed the observed target range.

PHM's 768-dimensional representation and Ultralytics RT-DETR-L are different from REASSEMBLE's 896-dimensional RT-DETR R18 representation. Their checkpoints and preprocessing cannot be exchanged.

[Pinned model configuration](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/config/resolved_config.yaml) · [Recorded environment and preprocessing](../../../../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8/reports/environment_device.json)
