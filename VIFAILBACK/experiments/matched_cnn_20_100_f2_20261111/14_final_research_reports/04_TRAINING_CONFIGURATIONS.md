# Frozen training protocol

AdamW: head LR 0.001, CNN LR 0.00001, weight decay 0.001, betas (0.9,0.999), epsilon 1e-8. Effective batch eight episodes, live microepisode one, frame chunks four, FP32, gradient norm clipping 1.0. T-only standardization and T negative/positive BCE weight. No augmentation or warmup.

All 20-epoch arms execute the first 20 epochs of cosine50; all 100-epoch arms use cosine100. Every requested epoch runs. Highest V macro AP wins, then lower V BCE using the same T class weight, then earliest epoch. Macro AP is the declared ViFailback adaptation of REASSEMBLE failure-AP selection. Selected weights are sigmoid-calibrated on separate C tasks.

FROZEN100 reuses the verified historical V1 outer0_inner0 trajectory only because the frozen selection rule selects the same epoch 11. Historical cost is retained separately. New 20-epoch fits are required because original V1 used cosine100.

Immutable protocol: `../01_protocol_and_source_evidence/protocol.json`. Exact per-fit config/history/checkpoint references and hashes: `../11_metrics_and_statistics/FIT_COVERAGE.json`.

|Condition|Seed|Fit|Executed|Selected epoch|Last minus best V macro AP|Curve|
|---|---|---|---|---|---|---|
|FROZEN20|42|outer0_final|20|20|0.000000|[Figure](../12_learning_curves/FROZEN20/seed42/outer0_final/learning_curve.png)|
|FROZEN20|42|outer0_inner0|20|11|-0.032132|[Figure](../12_learning_curves/FROZEN20/seed42/outer0_inner0/learning_curve.png)|
|FROZEN20|42|outer0_inner1|20|1|-0.047453|[Figure](../12_learning_curves/FROZEN20/seed42/outer0_inner1/learning_curve.png)|
|FROZEN20|42|outer0_inner2|20|6|-0.033891|[Figure](../12_learning_curves/FROZEN20/seed42/outer0_inner2/learning_curve.png)|
|FROZEN20|42|outer1_final|20|19|-0.045959|[Figure](../12_learning_curves/FROZEN20/seed42/outer1_final/learning_curve.png)|
|FROZEN20|42|outer1_inner0|20|9|-0.042265|[Figure](../12_learning_curves/FROZEN20/seed42/outer1_inner0/learning_curve.png)|
|FROZEN20|42|outer1_inner1|20|12|-0.078047|[Figure](../12_learning_curves/FROZEN20/seed42/outer1_inner1/learning_curve.png)|
|FROZEN20|42|outer1_inner2|20|20|0.000000|[Figure](../12_learning_curves/FROZEN20/seed42/outer1_inner2/learning_curve.png)|
|FROZEN20|42|outer2_final|20|2|-0.007499|[Figure](../12_learning_curves/FROZEN20/seed42/outer2_final/learning_curve.png)|
|FROZEN20|42|outer2_inner0|20|8|-0.014610|[Figure](../12_learning_curves/FROZEN20/seed42/outer2_inner0/learning_curve.png)|
|FROZEN20|42|outer2_inner1|20|16|-0.044170|[Figure](../12_learning_curves/FROZEN20/seed42/outer2_inner1/learning_curve.png)|
|FROZEN20|42|outer2_inner2|20|1|-0.052336|[Figure](../12_learning_curves/FROZEN20/seed42/outer2_inner2/learning_curve.png)|
|FROZEN20|123|outer0_final|20|8|-0.028387|[Figure](../12_learning_curves/FROZEN20/seed123/outer0_final/learning_curve.png)|
|FROZEN20|123|outer0_inner0|20|2|-0.037890|[Figure](../12_learning_curves/FROZEN20/seed123/outer0_inner0/learning_curve.png)|
|FROZEN20|123|outer0_inner1|20|1|-0.060023|[Figure](../12_learning_curves/FROZEN20/seed123/outer0_inner1/learning_curve.png)|
|FROZEN20|123|outer0_inner2|20|10|-0.022469|[Figure](../12_learning_curves/FROZEN20/seed123/outer0_inner2/learning_curve.png)|
|FROZEN20|123|outer1_final|20|16|-0.047991|[Figure](../12_learning_curves/FROZEN20/seed123/outer1_final/learning_curve.png)|
|FROZEN20|123|outer1_inner0|20|12|-0.010770|[Figure](../12_learning_curves/FROZEN20/seed123/outer1_inner0/learning_curve.png)|
|FROZEN20|123|outer1_inner1|20|14|-0.039614|[Figure](../12_learning_curves/FROZEN20/seed123/outer1_inner1/learning_curve.png)|
|FROZEN20|123|outer1_inner2|20|19|-0.013402|[Figure](../12_learning_curves/FROZEN20/seed123/outer1_inner2/learning_curve.png)|
|FROZEN20|123|outer2_final|20|2|-0.022523|[Figure](../12_learning_curves/FROZEN20/seed123/outer2_final/learning_curve.png)|
|FROZEN20|123|outer2_inner0|20|17|-0.006065|[Figure](../12_learning_curves/FROZEN20/seed123/outer2_inner0/learning_curve.png)|
|FROZEN20|123|outer2_inner1|20|17|-0.052578|[Figure](../12_learning_curves/FROZEN20/seed123/outer2_inner1/learning_curve.png)|
|FROZEN20|123|outer2_inner2|20|1|-0.094385|[Figure](../12_learning_curves/FROZEN20/seed123/outer2_inner2/learning_curve.png)|
|FROZEN20|20261023|outer0_final|20|13|-0.027551|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer0_final/learning_curve.png)|
|FROZEN20|20261023|outer0_inner0|20|13|-0.052848|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer0_inner0/learning_curve.png)|
|FROZEN20|20261023|outer0_inner1|20|18|-0.011648|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer0_inner1/learning_curve.png)|
|FROZEN20|20261023|outer0_inner2|20|14|-0.028081|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer0_inner2/learning_curve.png)|
|FROZEN20|20261023|outer1_final|20|18|-0.038770|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer1_final/learning_curve.png)|
|FROZEN20|20261023|outer1_inner0|20|8|-0.009420|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer1_inner0/learning_curve.png)|
|FROZEN20|20261023|outer1_inner1|20|13|-0.042385|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer1_inner1/learning_curve.png)|
|FROZEN20|20261023|outer1_inner2|20|1|-0.037387|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer1_inner2/learning_curve.png)|
|FROZEN20|20261023|outer2_final|20|1|-0.025444|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer2_final/learning_curve.png)|
|FROZEN20|20261023|outer2_inner0|20|16|-0.015862|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer2_inner0/learning_curve.png)|
|FROZEN20|20261023|outer2_inner1|20|5|-0.020655|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer2_inner1/learning_curve.png)|
|FROZEN20|20261023|outer2_inner2|20|7|-0.057178|[Figure](../12_learning_curves/FROZEN20/seed20261023/outer2_inner2/learning_curve.png)|
|DONOR20|42|outer0_final|20|7|-0.048503|[Figure](../12_learning_curves/DONOR20/seed42/outer0_final/learning_curve.png)|
|DONOR20|42|outer0_inner0|20|11|-0.024548|[Figure](../12_learning_curves/DONOR20/seed42/outer0_inner0/learning_curve.png)|
|DONOR20|42|outer0_inner1|20|20|0.000000|[Figure](../12_learning_curves/DONOR20/seed42/outer0_inner1/learning_curve.png)|
|DONOR20|42|outer0_inner2|20|9|-0.008650|[Figure](../12_learning_curves/DONOR20/seed42/outer0_inner2/learning_curve.png)|
|DONOR20|42|outer1_final|20|5|-0.029597|[Figure](../12_learning_curves/DONOR20/seed42/outer1_final/learning_curve.png)|
|DONOR20|42|outer1_inner0|20|11|-0.041665|[Figure](../12_learning_curves/DONOR20/seed42/outer1_inner0/learning_curve.png)|
|DONOR20|42|outer1_inner1|20|5|-0.021980|[Figure](../12_learning_curves/DONOR20/seed42/outer1_inner1/learning_curve.png)|
|DONOR20|42|outer1_inner2|20|16|-0.027465|[Figure](../12_learning_curves/DONOR20/seed42/outer1_inner2/learning_curve.png)|
|DONOR20|42|outer2_final|20|19|-0.017521|[Figure](../12_learning_curves/DONOR20/seed42/outer2_final/learning_curve.png)|
|DONOR20|42|outer2_inner0|20|19|-0.048920|[Figure](../12_learning_curves/DONOR20/seed42/outer2_inner0/learning_curve.png)|
|DONOR20|42|outer2_inner1|20|14|-0.011882|[Figure](../12_learning_curves/DONOR20/seed42/outer2_inner1/learning_curve.png)|
|DONOR20|42|outer2_inner2|20|5|-0.026318|[Figure](../12_learning_curves/DONOR20/seed42/outer2_inner2/learning_curve.png)|
|DONOR20|123|outer0_final|20|8|-0.036945|[Figure](../12_learning_curves/DONOR20/seed123/outer0_final/learning_curve.png)|
|DONOR20|123|outer0_inner0|20|18|-0.007632|[Figure](../12_learning_curves/DONOR20/seed123/outer0_inner0/learning_curve.png)|
|DONOR20|123|outer0_inner1|20|3|-0.020951|[Figure](../12_learning_curves/DONOR20/seed123/outer0_inner1/learning_curve.png)|
|DONOR20|123|outer0_inner2|20|10|-0.017120|[Figure](../12_learning_curves/DONOR20/seed123/outer0_inner2/learning_curve.png)|
|DONOR20|123|outer1_final|20|12|-0.025879|[Figure](../12_learning_curves/DONOR20/seed123/outer1_final/learning_curve.png)|
|DONOR20|123|outer1_inner0|20|5|-0.010623|[Figure](../12_learning_curves/DONOR20/seed123/outer1_inner0/learning_curve.png)|
|DONOR20|123|outer1_inner1|20|9|-0.032578|[Figure](../12_learning_curves/DONOR20/seed123/outer1_inner1/learning_curve.png)|
|DONOR20|123|outer1_inner2|20|3|-0.023647|[Figure](../12_learning_curves/DONOR20/seed123/outer1_inner2/learning_curve.png)|
|DONOR20|123|outer2_final|20|16|-0.001622|[Figure](../12_learning_curves/DONOR20/seed123/outer2_final/learning_curve.png)|
|DONOR20|123|outer2_inner0|20|11|-0.039984|[Figure](../12_learning_curves/DONOR20/seed123/outer2_inner0/learning_curve.png)|
|DONOR20|123|outer2_inner1|20|7|-0.036055|[Figure](../12_learning_curves/DONOR20/seed123/outer2_inner1/learning_curve.png)|
|DONOR20|123|outer2_inner2|20|1|-0.044269|[Figure](../12_learning_curves/DONOR20/seed123/outer2_inner2/learning_curve.png)|
|DONOR20|20261023|outer0_final|20|11|-0.043119|[Figure](../12_learning_curves/DONOR20/seed20261023/outer0_final/learning_curve.png)|
|DONOR20|20261023|outer0_inner0|20|13|-0.022700|[Figure](../12_learning_curves/DONOR20/seed20261023/outer0_inner0/learning_curve.png)|
|DONOR20|20261023|outer0_inner1|20|20|0.000000|[Figure](../12_learning_curves/DONOR20/seed20261023/outer0_inner1/learning_curve.png)|
|DONOR20|20261023|outer0_inner2|20|15|-0.019364|[Figure](../12_learning_curves/DONOR20/seed20261023/outer0_inner2/learning_curve.png)|
|DONOR20|20261023|outer1_final|20|4|-0.026491|[Figure](../12_learning_curves/DONOR20/seed20261023/outer1_final/learning_curve.png)|
|DONOR20|20261023|outer1_inner0|20|6|-0.026354|[Figure](../12_learning_curves/DONOR20/seed20261023/outer1_inner0/learning_curve.png)|
|DONOR20|20261023|outer1_inner1|20|11|-0.003541|[Figure](../12_learning_curves/DONOR20/seed20261023/outer1_inner1/learning_curve.png)|
|DONOR20|20261023|outer1_inner2|20|17|-0.018993|[Figure](../12_learning_curves/DONOR20/seed20261023/outer1_inner2/learning_curve.png)|
|DONOR20|20261023|outer2_final|20|18|-0.000188|[Figure](../12_learning_curves/DONOR20/seed20261023/outer2_final/learning_curve.png)|
|DONOR20|20261023|outer2_inner0|20|16|-0.000387|[Figure](../12_learning_curves/DONOR20/seed20261023/outer2_inner0/learning_curve.png)|
|DONOR20|20261023|outer2_inner1|20|8|-0.025483|[Figure](../12_learning_curves/DONOR20/seed20261023/outer2_inner1/learning_curve.png)|
|DONOR20|20261023|outer2_inner2|20|10|-0.057173|[Figure](../12_learning_curves/DONOR20/seed20261023/outer2_inner2/learning_curve.png)|
|FROZEN100|42|outer0_inner0|100|11|-0.019786|[Figure](../12_learning_curves/FROZEN100/seed42/outer0_inner0/learning_curve.png)|
|DONOR100|42|outer0_inner0|100|40|-0.025634|[Figure](../12_learning_curves/DONOR100/seed42/outer0_inner0/learning_curve.png)|

Figures show loss and validation macro AP with the selected epoch. A negative last-minus-best value documents validation deterioration by the last observed epoch; this alone does not prove outer-test overfitting. Partial curves are not final-epoch results.
