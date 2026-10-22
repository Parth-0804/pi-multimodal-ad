# 02.2 — Initial architecture

```text
16 video frames → frozen 896 features → visual head → calibrated p_visual
512 × 22 sensors → 220 statistics → logistic classifier → calibrated p_statistics

[p_visual, p_statistics]
  → LogisticRegression(C=1, class_weight=None)
  → sigmoid(intercept + w_visual*p_visual + w_statistics*p_statistics)
  → fused failure probability
  → threshold selected using meta cross-fitting → failure/success
```

This is the static stacker called `minimal_late_fusion` in Section 1B and **F2** in Section 2. Coefficients are regression coefficients: they need not be positive or sum to one. The inputs here are probabilities, not branch logits. F4–F6 are separate gating comparisons; their weights and logit combinations must not be interpreted as F2 coefficients.

The five outer folds have separate fitted parameters. There is no single universal trained fusion model in these cross-validation results.

[Original model configuration](../../../../../configs/reassemble/section1b.json)
