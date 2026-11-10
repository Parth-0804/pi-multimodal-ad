# F2 coefficient analysis

F2 is sigmoid(b+w_visual*p_visual+w_sensor*p_sensor). Coefficients act on probabilities, not logits; their signs are unconstrained and they are not normalized mixture weights.

| Arm | Visual coefficient | Sensor coefficient | Intercept |
|---|---:|---:|---:|
| frozen | 0.944387733 | 5.071542980 | -3.081963542 |
| finetuned | 1.133451787 | 5.075054970 | -3.100495158 |

For frozen, a +0.1 visual probability change adds +0.094439 to fused log odds when the sensor value is fixed; a +0.1 sensor change adds +0.507154. This is the fitted model response, not a causal feature effect.

For finetuned, a +0.1 visual probability change adds +0.113345 to fused log odds when the sensor value is fixed; a +0.1 sensor change adds +0.507505. This is the fitted model response, not a causal feature effect.

Branch calibration scales differ and predictions can be correlated, so raw coefficient magnitude alone is not evidence of visual usefulness or modality importance. Training probability spreads, coefficient×spread and branch correlation are retained separately. Regularization can shrink the visual contribution even when visual-only AP improves. The paired fusion scores, rather than an appealing coefficient, answer whether fusion improved. No coefficient was selected or altered after evaluating the test set.

Actual held-out disagreement examples and their failure labels, all seven probabilities, source identities,16 input frames and original timestamps are saved in08. Selection covers both native classes, both disagreement directions, fusion corrections and regressions when available; absent categories are reported, not manufactured. These are diagnostics after freezing the models and cannot establish a physical failure cause.
