# MSM research conclusions

P, F2 minus visual: mean +0.457978 AP, seed range [+0.440011, +0.482140]. The sign is positive in all seeds.

P, F2 minus sensor_logistic: mean -0.071737 AP, seed range [-0.081999, -0.059986]. The sign is negative in all seeds.

P, F2 minus sensor_histgradient: mean -0.144421 AP, seed range [-0.154682, -0.132670]. The sign is negative in all seeds.

P, F2 minus averaging: mean +0.021285 AP, seed range [-0.006416, +0.046858]. The sign is mixed or zero across seeds.

P, QG_aug minus F2_aug: mean +0.066351 AP, seed range [+0.049797, +0.088221]. The sign is positive in all seeds.

The implementation reuses the verified CNN/head and late-fusion primitives with a dataset-specific annotation/sensor adapter and freshly fitted classifiers. This establishes software portability. Predictive value is the measured held-out within-dataset difference in EXPERIMENT_RESULTS.md, not the fact that code ran. Fusion can be weaker than a unimodal or stronger classical sensor model; the complete seed/condition tables preserve such outcomes.

The canonical REASSEMBLE full-backbone source was unavailable at the completed-receipt gate, so learned-weight transfer is NOT evaluated. P means original generic pretrained CNN weights, not a REASSEMBLE-trained CNN. New dataset heads/scalers/F2 coefficients are not reused source-domain parameters. No zero-shot or no-retraining claim is made.

Direction contingency and direction-only held-out baseline are reported separately. Direction is excluded from all main predictors. Both directions have support for the frozen primary grouped design. DOWN-only label-2-excluded training fails the fixed class-support split gate; no seed search or fold reduction was performed. Within-direction held-out subgroup metrics are descriptive, not a causal direction intervention.

Only the listed synthetic corruption/fallback experiments support robustness statements. All three seed results are retained; seeds do not replace independent physical experiments or participants. Unknown tool/workpiece reuse, five-date support (MSM), unprovided participant identities (Handover), camera occlusion, sensor estimation/holding and retrospective observation horizons constrain inference. These limitations remain even if AP is high.
