# MSM: scientific interpretation of the completed evaluation

This is an additive interpretation of the sealed P evaluation, with no new
training, prediction, exclusion, threshold or model-selection change. The
original eight reports and completion receipt remain unchanged.

**The implementation transfers; the primary F2 benefit does not.** All validated
inputs and the full frozen comparison ran, but adding the visual branch through
F2 reduces primary pooled AP relative to its own logistic sensor component.

| Primary model | AP, mean of all three seeds |
| --- | ---: |
| Visual | 0.298901 |
| Sensor logistic | 0.828616 |
| Sensor HistGradientBoosting | 0.901299 |
| Averaging | 0.735594 |
| F2 | 0.756879 |
| F2_aug | 0.760170 |
| QG_clean | 0.837418 |
| QG_aug | 0.826521 |

F2 minus sensor logistic is **−0.071737 AP** on average. Its three seed differences
are −0.073227, −0.059986 and −0.081999. The paired calendar-date-proxy bootstrap
95% interval is **[−0.100356, −0.051477]**, conditional on these fitted models and
splits. Only five dates support that interval, and physical tool/workpiece reuse
remains unresolved. This supports a bounded negative result for the frozen
protocol, rather than a universal claim that vision or late fusion is harmful.

The effect is not uniform across individual folds: F2 exceeds logistic sensor AP
in two seeds of outer fold2, while losing in folds0/1 for every seed. Both the
three-seed pooled comparison and the descriptive mean of the fold APs favor
sensor logistic. Outer-test positive prevalence is27.69%,5.07%,23.75%; substantial
group/condition and prior shifts limit interpretation. No split seed, fold count,
calibration or threshold was changed after observing this.

All six predefined target/grouping protocols have lower mean F2 AP than sensor
logistic. In particular, excluding label2 and grouping by calendar date gives
F2 AP0.521826 versus sensor logistic0.891656. Sensitivity to target/cohort/grouping
is a substantive finding, not a reason to select a favorable protocol.

QG_clean's mean gain over logistic sensor is only+0.008802 AP, with one negative
seed and calendar-date interval[−0.097085,+0.056426]. It does not establish a
stable clean-data fusion gain. The stronger sensor control has the highest
primary point AP; its ranking is not asserted for every sensitivity or fault.

Named perturbations also restrict the robustness claim. At the highest sensor
noise, F2 AP is0.206863, intact vision0.298901, QG_aug0.298636, averaging0.300027
and the noisy stronger sensor control0.606157. Improving on degraded F2 does
not demonstrate an advantage over the appropriate intact/control modality.
Under strongest blur, QG_aug reaches0.682784 versus F2 0.771420 and intact sensor
logistic0.828616. Entire-modality absence uses an imposed surviving-branch
fallback:0.828616 without vision,0.298901 without sensors. That behavior is not
learned adaptive recovery.

Mean per-fold training AP is0.980672 for vision and0.978253 for sensor logistic,
compared with pooled held-out AP0.298901/0.828616. These differently aggregated
in-sample/held-out diagnostics are consistent with overfitting and/or condition
shift; they do not isolate a cause. Coolant obscures the interface, and source
timing validity does not prove visible anomaly evidence. Direction alone reaches
AP0.241181; it is a documented confound, excluded from the main features.

REASSEMBLE-learned CNN transfer remains **unmeasured** because the exact completed
canonical source was absent. P uses the original generic pretrained CNN. Neither
source heads nor source F2 coefficients entered the MSM fits.

For the thesis, report the negative primary F2 result, mixed gate result, all
seeds, six sensitivities, uncertainty assumptions and actual corruption/fallback
controls. Describe a validated retrospective cutting-label classifier and modular
adaptation, without claiming optical defect recognition, online warning,
zero-shot transfer, industrial visual generalization or general robustness.

Sources: `06_evaluation_results/metrics/clean_seed_summary.csv`,
`paired_seed_differences.csv`, `paired_group_bootstrap_95ci.csv`, the per-fold
metrics, `07_robustness_experiments/robustness_metrics.csv` and
`06_evaluation_results/implementation_validation.json` under `MSM/`.
