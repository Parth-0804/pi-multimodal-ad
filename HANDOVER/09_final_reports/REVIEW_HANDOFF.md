# HANDOVER review handoff

**PARTIAL.** Active measured evaluation: `HANDOVER/experiments/common_support_v2`. Main comparison uses all three fixed seeds; no best seed/fold, source checkpoint or threshold was selected using test scores.

| initialization | protocol | model | AP_mean | AP_seed_std | AP_min | AP_max |
| --- | --- | --- | --- | --- | --- | --- |
| P | official | averaging | 0.803102 | 0.013458 | 0.794653 | 0.818621 |
| P | official | prevalence | 0.728477 | 0.000000 | 0.728477 | 0.728477 |
| P | official | sensor_histgradient | 0.906319 | 0.000000 | 0.906319 | 0.906319 |
| P | official | sensor_logistic | 0.823624 | 0.000000 | 0.823624 | 0.823624 |
| P | official | visual | 0.771647 | 0.006411 | 0.767664 | 0.779042 |

F2, F2_aug, QG_clean and QG_aug are SKIPPED: participant-disjoint OOF probabilities cannot be certified without participant IDs. No in-sample probability stack or trial-group substitute was used. Robot and task differ in force estimation, camera view and class prevalence; see subgroup tables. The common-support amendment retains all151 official test trials; it is not a test-score-selected cohort.

Read [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md), [ROBUSTNESS_RESULTS.md](ROBUSTNESS_RESULTS.md), [DATASET_VALIDATION.md](DATASET_VALIDATION.md), [MODEL_IMPLEMENTATION.md](MODEL_IMPLEMENTATION.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Source-native prediction tables, all per-fold/per-seed metrics and completed checkpoints are preserved in their separate dataset stages. No full-model efficacy is inferred from earlier smoke tests; prior blocked findings remain historical prerequisites, not negative model scores.
