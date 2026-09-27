# Modality-dropout handoff

One F6 variant, same architecture/settings, three seeds and original folds. Masks .15 visual missing/.15 sensor missing/.70 both available; never both absent.

| Condition | AUROC | AUPRC | Δ AP vs ordinary F6 [95%] |
| --- | --- | --- | --- |
| clean | 0.7754 | 0.4377 | -0.0037 [-0.0085, 0.0003] |
| V4 | 0.7793 | 0.4294 | 0.0000 [0.0000, 0.0000] |
| S5 | 0.6978 | 0.2307 | 0.0000 [0.0000, 0.0000] |
| V1_0.02 | 0.6601 | 0.1790 | -0.0023 [-0.0081, 0.0037] |
| V1_0.05 | 0.5950 | 0.1351 | -0.0058 [-0.0101, -0.0020] |
| V1_0.1 | 0.5774 | 0.1274 | -0.0001 [-0.0035, 0.0050] |
| S1_0.1 | 0.7641 | 0.3969 | 0.0008 [-0.0027, 0.0046] |
| S1_0.5 | 0.6670 | 0.2739 | -0.0021 [-0.0079, 0.0038] |
| S1_1.0 | 0.6059 | 0.1803 | 0.0015 [-0.0025, 0.0060] |
| V2_2.0 | 0.7553 | 0.4334 | -0.0039 [-0.0132, 0.0050] |
| S2_0.3 | 0.7519 | 0.3511 | 0.0246 [0.0063, 0.0428] |

Missing-modality probabilities are exactly unchanged: with one available branch, masked softmax gives a fixed unit weight and zero gate-parameter gradient. This architecture cannot recover absent information through modality-dropout training. Clean/degraded joint-present trade-offs above are empirical, not universal robustness evidence. Full paired metrics, degradation advantages and seed weights: runs/reassemble/20260927T204649Z-modality-dropout.
