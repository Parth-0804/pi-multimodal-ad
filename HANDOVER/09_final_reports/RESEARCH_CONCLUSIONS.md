# HANDOVER research conclusions

P, averaging minus visual: mean +0.031455 AP, seed range [+0.026418, +0.039579]. The sign is positive in all seeds.

P, averaging minus sensor_logistic: mean -0.020522 AP, seed range [-0.028971, -0.005003]. The sign is negative in all seeds.

P, averaging minus sensor_histgradient: mean -0.103218 AP, seed range [-0.111667, -0.087699]. The sign is negative in all seeds.

The implementation reuses the verified CNN/head and late-fusion primitives with a dataset-specific annotation/sensor adapter and freshly fitted classifiers. This establishes software portability. Predictive value is the measured held-out within-dataset difference in EXPERIMENT_RESULTS.md, not the fact that code ran. Fusion can be weaker than a unimodal or stronger classical sensor model; the complete seed/condition tables preserve such outcomes.

The canonical REASSEMBLE full-backbone source was unavailable at the completed-receipt gate, so learned-weight transfer is NOT evaluated. P means original generic pretrained CNN weights, not a REASSEMBLE-trained CNN. New dataset heads/scalers/F2 coefficients are not reused source-domain parameters. No zero-shot or no-retraining claim is made.

F2, F2_aug, QG_clean and QG_aug are SKIPPED: participant-disjoint OOF probabilities cannot be certified without participant IDs. No in-sample probability stack or trial-group substitute was used. Robot and task differ in force estimation, camera view and class prevalence; see subgroup tables. The common-support amendment retains all151 official test trials; it is not a test-score-selected cohort.

Only the listed synthetic corruption/fallback experiments support robustness statements. All three seed results are retained; seeds do not replace independent physical experiments or participants. Unknown tool/workpiece reuse, five-date support (MSM), unprovided participant identities (Handover), camera occlusion, sensor estimation/holding and retrospective observation horizons constrain inference. These limitations remain even if AP is high.
