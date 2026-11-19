# Measured performance comparison

Compare paired effects **within each dataset**, not raw AP between tasks. MSM has336/1895 positives (17.73%); Handover's official test has110/151 failures (72.85%). Completed-trial failure and short stable/abnormal cutting are different targets, horizons, cameras and physical systems. High failure prevalence alone raises the Handover AP baseline.

## Primary clean-data scores, every permitted model and all seeds

| dataset | initialization | protocol | model | AP_mean | AP_seed_std | AP_min | AP_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MSM | P | primary__group_id | F2 | 0.756879 | 0.011082 | 0.746617 | 0.768630 |
| MSM | P | primary__group_id | F2_aug | 0.760170 | 0.009783 | 0.752758 | 0.771258 |
| MSM | P | primary__group_id | QG_aug | 0.826521 | 0.016168 | 0.813794 | 0.844713 |
| MSM | P | primary__group_id | QG_clean | 0.837418 | 0.013389 | 0.823898 | 0.850673 |
| MSM | P | primary__group_id | averaging | 0.735594 | 0.015942 | 0.721772 | 0.753034 |
| MSM | P | primary__group_id | direction_only_DIAGNOSTIC | 0.241181 | 0.000000 | 0.241181 | 0.241181 |
| MSM | P | primary__group_id | prevalence | 0.145395 | 0.000000 | 0.145395 | 0.145395 |
| MSM | P | primary__group_id | sensor_histgradient | 0.901299 | 0.000000 | 0.901299 | 0.901299 |
| MSM | P | primary__group_id | sensor_logistic | 0.828616 | 0.000000 | 0.828616 | 0.828616 |
| MSM | P | primary__group_id | visual | 0.298901 | 0.010853 | 0.286490 | 0.306606 |
| HANDOVER | P | official | averaging | 0.803102 | 0.013458 | 0.794653 | 0.818621 |
| HANDOVER | P | official | prevalence | 0.728477 | 0.000000 | 0.728477 | 0.728477 |
| HANDOVER | P | official | sensor_histgradient | 0.906319 | 0.000000 | 0.906319 | 0.906319 |
| HANDOVER | P | official | sensor_logistic | 0.823624 | 0.000000 | 0.823624 | 0.823624 |
| HANDOVER | P | official | visual | 0.771647 | 0.006411 | 0.767664 | 0.779042 |

AP_seed_std/range are descriptive head-training variability, not independent-sample uncertainty. No best seed, fold or model is retroactively promoted as independently validated. Diagnostic direction-only results are explicitly separate from main models.

The prevalence predictor uses each outer-training partition's positive fraction. Its constants differ between MSM outer folds, so pooled cross-validation AP need not equal the overall test prevalence. The prevalence column is also the descriptive all-tied AP reference; test prevalence was never used to fit the baseline. Handover has one fixed training partition, so its constant baseline AP equals test prevalence.

### MSM, P

F2 minus visual: mean AP difference +0.457978; three-seed range [+0.440011, +0.482140] (positive across seeds).

F2 minus sensor_logistic: mean AP difference -0.071737; three-seed range [-0.081999, -0.059986] (negative across seeds).

F2 minus sensor_histgradient: mean AP difference -0.144421; three-seed range [-0.154682, -0.132670] (negative across seeds).

F2 minus averaging: mean AP difference +0.021285; three-seed range [-0.006416, +0.046858] (mixed/zero across seeds).

QG_aug minus F2_aug: mean AP difference +0.066351; three-seed range [+0.049797, +0.088221] (positive across seeds).

averaging minus visual: mean AP difference +0.436693; three-seed range [+0.428370, +0.446427] (positive across seeds).

averaging minus sensor_logistic: mean AP difference -0.093022; three-seed range [-0.106844, -0.075582] (negative across seeds).
### HANDOVER, P

F2 minus visual: unavailable under the scientific gate.

F2 minus sensor_logistic: unavailable under the scientific gate.

F2 minus sensor_histgradient: unavailable under the scientific gate.

F2 minus averaging: unavailable under the scientific gate.

QG_aug minus F2_aug: unavailable under the scientific gate.

averaging minus visual: mean AP difference +0.031455; three-seed range [+0.026418, +0.039579] (positive across seeds).

averaging minus sensor_logistic: mean AP difference -0.020522; three-seed range [-0.028971, -0.005003] (negative across seeds).

MSM paired cluster bootstrap includes nominal-folder and calendar-date-proxy95% intervals,2,000 common draws per paired comparison, averaging seeds without treating them as independent data. Only five calendar dates and unresolved tool/workpiece reuse limit inferential strength. Full interval tables are under MSM/06_evaluation_results/metrics/paired_group_bootstrap_95ci.csv. More positive per-seed deltas do not resolve a group-level interval spanning zero.

Handover has no participant IDs, so no participant CI or leakage-safe F2 estimate is fabricated. Its five official-split baselines provide publisher-partition held-out evidence with unverified participant identity independence. Validation results are separately reported and never chose epochs/thresholds. The binary labels are released outcomes, not observer-assigned camera labels.

MSM repeats the entire fixed model/seed pipeline under two stricter date groupings and label2 exclusion: all six protocols are retained, including weaker or inconsistent outcomes. Machine/direction/native-class and Handover robot/task subgroup tables are descriptive rather than newly selected confirmatory tests. No cross-machine retraining, industrial sensor-only substitution or zero-shot cross-domain classifier test is claimed.

The exact completed canonical REASSEMBLE source checkpoint remained unavailable. P-only external evaluations use the original generic pretrained CNN. **Transfer of weights learned on REASSEMBLE is unmeasured**, not a failed transfer result; an incomplete/other-fold source was never substituted.
