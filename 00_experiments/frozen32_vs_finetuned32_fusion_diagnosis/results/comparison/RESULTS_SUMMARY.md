# Frozen32 versus Fine-tuned32: matched two-epoch fusion diagnosis

Status: **COMPLETE**. Finished UTC: 2026-10-23T17:18:18.684160+00:00.
Completed visual fits: 75 new, 25 explicitly reused. This is equal epoch/data budget, not equal compute.

| Seed | Matched folds | Scope |
|---|---:|---|
| 42 | 5/5 | Complete common 4,530-action cohort |
| 20261023 | 5/5 | Complete common 4,530-action cohort |

## AP results and recording uncertainty

| Seed | Method | Frozen pooled AP | Fine-tuned pooled AP | Difference | 95% interval | Frozen mean-fold AP | Fine-tuned mean-fold AP |
|---|---|---:|---:|---:|---|---:|---:|
| 42 | visual | 0.222708 | 0.230609 | +0.007902 | [-0.017312, +0.033219] | 0.228864 | 0.242172 |
| 42 | uniform | 0.444720 | 0.440946 | -0.003774 | [-0.014238, +0.007851] | 0.453956 | 0.446159 |
| 42 | F2 | 0.439363 | 0.438566 | -0.000796 | [-0.006424, +0.006072] | 0.448859 | 0.449334 |
| 20261023 | visual | 0.216799 | 0.200517 | -0.016282 | [-0.039636, +0.009790] | 0.222990 | 0.203281 |
| 20261023 | uniform | 0.436495 | 0.428489 | -0.008006 | [-0.018180, +0.003279] | 0.447559 | 0.434520 |
| 20261023 | F2 | 0.435202 | 0.432380 | -0.002822 | [-0.008285, +0.003602] | 0.445546 | 0.440512 |

Pooled AP and mean-fold AP are distinct. Seeds reuse the same recordings and must not be pooled as independent samples. Recording intervals condition on fitted models; two seeds give descriptive sensitivity, not a robust estimate of seed uncertainty. Threshold0.5 and all settings were fixed before assessment.

## OOF, calibration and complementarity

`oof_vs_assessment.csv` contains branch-held-out visual scores by seed/fold/condition/role. These OOF rows train F2, so F2 scores on them would be training performance, not independent validation. Read them alongside `F2_coefficients.csv`, `calibration_comparison.csv` and fixed ten-bin reliability counts. Positive calibrator slopes preserve raw within-fit ranking; negative slopes, if observed, reverse it and are reported without retuning. Calibration effects on cross-fold comparability and stacker inputs are not isolated as causal effects.

`complementarity.csv` reports true-label Brier/log-loss changes separately for sensor-missed/detected failures and sensor-false-positive/correct successes. `correctness_overlap.csv` separates failures and successes at the unchanged0.5 threshold. Sensor probabilities are identical for both arms and seeds. Subset AP is not used to rank different-prevalence groups.

Seed 42: fine-tuned visual AP is higher/lower in 2/3 matched OOF banks and 3/2 outer assessments; denominator 5 matched folds.
Seed 20261023: fine-tuned visual AP is higher/lower in 3/2 matched OOF banks and 2/3 outer assessments; denominator 5 matched folds.

| Seed | Sensor group | Actions | Visual Brier change | Visual log-loss change | Uniform Brier change | F2 Brier change | F2 log-loss change |
|---|---|---:|---:|---:|---:|---:|---:|
| 42 | sensor_missed_failure | 413 | +0.001093 | +0.040256 | -0.000103 | -0.001092 | +0.002306 |
| 42 | sensor_detected_failure | 96 | -0.046520 | -0.156063 | -0.016773 | -0.008411 | -0.020211 |
| 42 | sensor_false_positive_success | 31 | +0.004773 | +0.014591 | +0.005952 | +0.006128 | +0.025477 |
| 42 | sensor_correct_success | 3990 | +0.000446 | -0.000509 | +0.000142 | +0.000171 | +0.000084 |
| 20261023 | sensor_missed_failure | 413 | +0.010619 | +0.040791 | +0.005003 | +0.003168 | +0.013465 |
| 20261023 | sensor_detected_failure | 96 | +0.007780 | +0.016240 | +0.002246 | +0.002066 | +0.005169 |
| 20261023 | sensor_false_positive_success | 31 | -0.002751 | -0.006519 | -0.002672 | -0.007943 | -0.027118 |
| 20261023 | sensor_correct_success | 3990 | -0.000454 | -0.001156 | -0.000190 | -0.000135 | -0.000615 |

Negative true-label loss changes are improvements. Conditional probability scores do not identify causal sensor dominance.

## Training-budget control

The source seed42 fine-tuned2 fits are fixed. `budget_comparison.csv` compares original frozen5 with new frozen2 under the same seed, data and head settings. New frozen2 training loss prefixes must agree with the retained original first-two-epoch logs within1e-6. A change in the original contrast can establish a bounded duration effect for this seed; it is not evidence that longer adaptation would improve results.

## Cause assessment

| Candidate explanation | Evidence for | Evidence against / limit | Status |
|---|---|---|---|
| Seed instability | F2 effects by seed: [-0.000796187072331811, -0.0028219224160057066]; sign reversal=False | Only two seed families; recording intervals do not estimate a seed-variance distribution | Unresolved |
| Unequal training budget | visual: old contrast +0.011182, matched +0.007902; F2: old contrast -0.001017, matched -0.000796 | Direct fixed-seed budget comparison is bounded to seed42; same-seed reuse is not independent replication | Unresolved |
| Limited sensor complementarity | Predeclared Pattern B by seed: [np.True_, np.False_]; class-conditional true-label changes in complementarity.csv | Not improving AP does not establish absence of image information; probabilities and operating points can differ | Weak evidence |
| Calibration/F2 interaction | Predeclared Pattern A by seed: [np.False_, np.False_]; F2 coefficients and calibrators retained | Uniform and F2 use the same calibrated inputs; no causal calibration intervention was performed | Unresolved |
| OOF-to-assessment mismatch | Folds with OOF deficit, assessment gain and reduced visual coefficient by seed: [1, 2]/5 | Different fits/training sizes/calibration sets; OOF banks overlap; F2 learned on those rows | Weak evidence |

No cause is promoted merely because it is plausible. Supported labels require repeated fold/seed directions and relevant directional intervals under the locked protocol. They support candidate patterns rather than unique causation. **Defensible conclusion: CAUSE_NOT_RESOLVED**

## Evidence and limits

Evidence: new and reused fit manifests in `fit_evidence_index.csv`, exact model/prediction/source hashes, three-action saved-model pixel replay for every new fit, new gradient/update checks, original verified replay receipts for reused fits, fixed sensor lineage, OOF membership checks, uniform/F2 arithmetic and source code lock. The original study, raw inputs and historical outputs were not edited.

Limits: exposed data, exactly two seed families, conditional recording uncertainty, different parameter/compute costs, fixed training/calibration recipe and no external validation. No architecture, corruption, sensor fitting, threshold search or new seed was added. Review is a self-review. Any interrupted/unpaired condition is excluded from matched comparisons and remains visible in its progress/manifests.

The Git gate was verified against origin/main before this study. See ../../GIT_COMMIT_REPORT.md. No ZIP was uploaded and no further work was scheduled.


Actual elapsed time through evaluation: 21.845 hours; archive verification records the final elapsed runtime.

An observed progress-update gap lasted 21.79 minutes and resolved without a training restart. Its cause was not established. The original clock and settings were unchanged; see `../provenance/resolved_training_progress_gap.json`.

Optimizer/RNG restoration has a CPU head test; no deliberate GPU resume-equivalence test was run. Saved-model pixel replays verify the new completed model predictions.
