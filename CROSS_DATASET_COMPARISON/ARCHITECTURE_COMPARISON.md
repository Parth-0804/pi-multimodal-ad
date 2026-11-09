# Architecture comparison

| Component | MSM | Handover | Reuse versus adaptation |
| --- | --- | --- | --- |
| Prediction unit | One native cutting interval | One completed trial over common recorded support | New native annotation adapters; retrospective tasks |
| Input RGB |16 source-aligned native frames |16 source-clock bin-center native frames | Shared SAR-aware letterbox640, same frozen CNN |
| Visual representation |896 mean-pooled values |896 mean-pooled values | Actual RT-DETR-derived ResNet CNN only; no detector/transformer |
| Visual classifier |896→128→1, ReLU/dropout.1 |Same | Newly fitted domain heads and training-only standardizers |
| Numerical input |15 MTC channels×6stats=90 |6 wrench channels×6stats=36 | New physically meaningful domain adapters; no fabricated shared joints |
| Numerical classifier |Balanced L2 logistic C1 |Same | New coefficients/standardization; stronger HGB control fixed |
| Learned F2 |Unweighted L2 logistic on group-OOF [pv,ps] |BLOCKED: no participant mapping | Actual F2 semantics reused; no source fusion coefficient transfer |
| Nonlearned averaging |Evaluated |Evaluated | Same visual/logistic-sensor branches; no stacking fit |
| Quality fusion |QG_clean, QG_aug; matched F2_aug control |BLOCKED: no participant mapping | Actual DecisionGate reused with explicitly new quality context adapter |
| Main assessment |3 outer×2inner experiment-group folds |Official335train/101val/151test eligible | No label/metadata-derived grouping invented |

All three seeds42,123,20261023 use a fixed10-epoch AdamW visual head (lr.001,wd.001,batch32,clip1,FP32,finalepoch), training-only normalization and identical inputs/splits per model. Gates use40 fixed epochs and fixed augmentation exposure. The CNN is cached once per dataset/preprocessing/weight identity, not refitted per fold. The original REASSEMBLE raw-sequence sensor encoder is **not** claimed to have transferred unchanged: these are the verified statistics-based external adaptations.

Sixteen-frame averaging is permutation invariant. These experiments do not establish temporal-order modeling, object localization or a benefit over a one-frame ablation (not run). Crops and contact sheets are examination derivatives only. F2 is a model name, not F-beta=2 and not a quality-aware gate.

The exact completed canonical REASSEMBLE source checkpoint remained unavailable. P-only external evaluations use the original generic pretrained CNN. **Transfer of weights learned on REASSEMBLE is unmeasured**, not a failed transfer result; an incomplete/other-fold source was never substituted.
