# Paired statistical comparison

| Contrast, treatment minus control | AP difference [95% CI] | AUROC difference [95% CI] |
|---|---|---|
| visual finetuned minus frozen | +0.018809 [95% CI -0.036995, +0.095910] | +0.010720 [95% CI -0.032385, +0.049727] |
| F2 finetuned minus frozen | +0.014117 [95% CI -0.000773, +0.029089] | +0.011623 [95% CI +0.001070, +0.022797] |
| F2 finetuned minus sensor | +0.021390 [95% CI -0.000345, +0.036358] | +0.016618 [95% CI +0.004581, +0.031573] |
| F2 frozen minus sensor | +0.007273 [95% CI -0.003151, +0.015377] | +0.004995 [95% CI -0.004794, +0.016064] |
| F2 finetuned minus visual | +0.136510 [95% CI +0.027101, +0.234603] | +0.064973 [95% CI +0.018472, +0.115683] |
| F2 frozen minus visual | +0.141202 [95% CI +0.055647, +0.229613] | +0.064071 [95% CI +0.027308, +0.100459] |
| F2 frozen minus average | -0.013029 [95% CI -0.033067, +0.003665] | +0.007435 [95% CI -0.012888, +0.026942] |
| F2 finetuned minus average | -0.009439 [95% CI -0.051172, +0.021666] | -0.005687 [95% CI -0.026207, +0.014341] |


All comparisons use the same 2,000 paired recording-cluster resamples (seed20261029). Each draw samples 26 recordings with replacement and retains every action of each selected recording; repeated recordings repeat all their actions. Each model receives identical draw indices. This respects within-recording dependence and preserves the action-level estimand instead of treating753 actions as independent replicates.

Intervals are percentile95% intervals conditional on this selected split and these fitted models. They do not include retraining, seed/fold variation, prior test exposure or the original fit-selection process. The eight contrasts are exploratory, with no multiplicity adjustment and no new model selected from them. Resamples missing either native class are excluded because AUROC is undefined; excluded and valid draw counts plus full AP/AUROC draws are retained. Intervals crossing zero do not establish improvement; a positive conditional interval still does not constitute independent confirmation.

F2 fine-tuned minus frozen: **+0.014117 [95% CI -0.000773, +0.029089]**. The interval includes zero; an improvement is not established.

F2 frozen minus sensor: **+0.007273 [95% CI -0.003151, +0.015377]**. The interval includes zero; an improvement is not established.

F2 fine-tuned minus sensor: **+0.021390 [95% CI -0.000345, +0.036358]**. The interval includes zero; an improvement is not established.
