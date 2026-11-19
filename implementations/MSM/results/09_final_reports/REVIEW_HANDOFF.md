# MSM review handoff

**PASS.** Active measured evaluation: `MSM`. Main comparison uses all three fixed seeds; no best seed/fold, source checkpoint or threshold was selected using test scores.

| initialization | protocol | model | AP_mean | AP_seed_std | AP_min | AP_max |
| --- | --- | --- | --- | --- | --- | --- |
| P | primary__group_id | F2 | 0.756879 | 0.011082 | 0.746617 | 0.768630 |
| P | primary__group_id | F2_aug | 0.760170 | 0.009783 | 0.752758 | 0.771258 |
| P | primary__group_id | QG_aug | 0.826521 | 0.016168 | 0.813794 | 0.844713 |
| P | primary__group_id | QG_clean | 0.837418 | 0.013389 | 0.823898 | 0.850673 |
| P | primary__group_id | averaging | 0.735594 | 0.015942 | 0.721772 | 0.753034 |
| P | primary__group_id | direction_only_DIAGNOSTIC | 0.241181 | 0.000000 | 0.241181 | 0.241181 |
| P | primary__group_id | prevalence | 0.145395 | 0.000000 | 0.145395 | 0.145395 |
| P | primary__group_id | sensor_histgradient | 0.901299 | 0.000000 | 0.901299 | 0.901299 |
| P | primary__group_id | sensor_logistic | 0.828616 | 0.000000 | 0.828616 | 0.828616 |
| P | primary__group_id | visual | 0.298901 | 0.010853 | 0.286490 | 0.306606 |

Direction contingency and direction-only held-out baseline are reported separately. Direction is excluded from all main predictors. Both directions have support for the frozen primary grouped design. DOWN-only label-2-excluded training fails the fixed class-support split gate; no seed search or fold reduction was performed. Within-direction held-out subgroup metrics are descriptive, not a causal direction intervention.

Read [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md), [ROBUSTNESS_RESULTS.md](ROBUSTNESS_RESULTS.md), [DATASET_VALIDATION.md](DATASET_VALIDATION.md), [MODEL_IMPLEMENTATION.md](MODEL_IMPLEMENTATION.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Source-native prediction tables, all per-fold/per-seed metrics and completed checkpoints are preserved in their separate dataset stages. No full-model efficacy is inferred from earlier smoke tests; prior blocked findings remain historical prerequisites, not negative model scores.
