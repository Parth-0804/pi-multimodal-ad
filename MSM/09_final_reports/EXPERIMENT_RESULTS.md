# MSM independent evaluation results

**Status: PASS.** These are measured held-out results, not smoke-test metrics. Primary average precision is pooled over the independent outer tests (MSM) or the eligible official test split (Handover), calculated separately for every seed. Fixed threshold0.5 is used for classification metrics. AP is scikit-learn average precision, not trapezoidal PR area or the F-beta=2 score. F2 is the logistic-fusion model name.

## Complete three-seed comparison

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

Standard deviations describe three head-training seeds, not three independent datasets. Deterministic classical models may be identical across seeds. P is original pretrained CNN initialization; any R rows use only the exact completed canonical source. No best seed/fold was selected.

## Paired within-dataset AP differences

| initialization | comparison | mean | min | max |
| --- | --- | --- | --- | --- |
| P | F2 minus F2_aug | -0.003291 | -0.006141 | -0.001104 |
| P | F2 minus averaging | 0.021285 | -0.006416 | 0.046858 |
| P | F2 minus sensor_histgradient | -0.144421 | -0.154682 | -0.132670 |
| P | F2 minus sensor_logistic | -0.071737 | -0.081999 | -0.059986 |
| P | F2 minus visual | 0.457978 | 0.440011 | 0.482140 |
| P | F2_aug minus F2 | 0.003291 | 0.001104 | 0.006141 |
| P | F2_aug minus averaging | 0.024575 | -0.000276 | 0.049486 |
| P | F2_aug minus sensor_histgradient | -0.141130 | -0.148541 | -0.130042 |
| P | F2_aug minus sensor_logistic | -0.068446 | -0.075858 | -0.057358 |
| P | F2_aug minus visual | 0.461269 | 0.446152 | 0.484768 |
| P | QG_aug minus F2 | 0.069642 | 0.052425 | 0.089325 |
| P | QG_aug minus F2_aug | 0.066351 | 0.049797 | 0.088221 |
| P | QG_aug minus averaging | 0.090927 | 0.060760 | 0.112737 |
| P | QG_aug minus sensor_histgradient | -0.074779 | -0.087505 | -0.056586 |
| P | QG_aug minus sensor_logistic | -0.002095 | -0.014822 | 0.016098 |
| P | QG_aug minus visual | 0.527620 | 0.507188 | 0.541107 |
| P | QG_clean minus F2 | 0.080540 | 0.069054 | 0.095284 |
| P | QG_clean minus F2_aug | 0.077249 | 0.066426 | 0.094180 |
| P | QG_clean minus averaging | 0.101824 | 0.070865 | 0.118696 |
| P | QG_clean minus sensor_histgradient | -0.063881 | -0.077401 | -0.050626 |
| P | QG_clean minus sensor_logistic | 0.008802 | -0.004718 | 0.022057 |
| P | QG_clean minus visual | 0.538518 | 0.517292 | 0.551194 |
| P | averaging minus F2 | -0.021285 | -0.046858 | 0.006416 |
| P | averaging minus F2_aug | -0.024575 | -0.049486 | 0.000276 |
| P | averaging minus sensor_histgradient | -0.165705 | -0.179528 | -0.148266 |
| P | averaging minus sensor_logistic | -0.093022 | -0.106844 | -0.075582 |
| P | averaging minus visual | 0.436693 | 0.428370 | 0.446427 |

F2 is compared with its actual logistic-sensor component, vision, averaging and the stronger sensor control. An improvement over the logistic component alone does not establish superiority over the stronger numerical baseline. QG_aug has extra predefined corruption-training exposure; compare it with F2_aug as well as clean F2. Original F2 remains the clean-OOF model.

## Uncertainty and independence

Paired cluster bootstrap (2,000 replicates) resamples complete groups with the same draws for all models/seeds. It is conditional on the fixed fitted models and split assignments; no bootstrap refitting was performed. Seeds are averaged descriptively, not treated as independent data. Both nominal-folder and calendar-date-proxy intervals are provided. Only five dates support the stricter interval; unknown tool/workpiece reuse across dates can still invalidate physical independence.

| initialization | protocol | grouping | groups | comparison | point_AP_or_difference | lower_95 | upper_95 | valid_bootstrap_replicates | seeds_averaged_not_independent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P | primary__group_id | calendar_date_group | 5 | F2 minus visual | 0.457978 | 0.186444 | 0.772165 | 2000 | True |
| P | primary__group_id | calendar_date_group | 5 | F2 minus sensor_logistic | -0.071737 | -0.100356 | -0.051477 | 2000 | True |
| P | primary__group_id | calendar_date_group | 5 | F2 minus sensor_histgradient | -0.144421 | -0.245433 | 0.030865 | 2000 | True |
| P | primary__group_id | calendar_date_group | 5 | F2 minus averaging | 0.021285 | -0.077511 | 0.244561 | 2000 | True |
| P | primary__group_id | calendar_date_group | 5 | F2 minus F2_aug | -0.003291 | -0.018191 | 0.012049 | 2000 | True |


## All per-seed held-out metrics

| initialization | seed | model | AP | AUROC | F1 | precision | recall | specificity | balanced_accuracy | Brier | log_loss | prevalence | TN | FP | FN | TP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P | 42 | F2 | 0.755389 | 0.940474 | 0.820438 | 0.805158 | 0.836310 | 0.956382 | 0.896346 | 0.056091 | 0.204205 | 0.177309 | 1491 | 68 | 55 | 281 |
| P | 42 | F2_aug | 0.756493 | 0.940085 | 0.815906 | 0.807580 | 0.824405 | 0.957665 | 0.891035 | 0.057164 | 0.206467 | 0.177309 | 1493 | 66 | 59 | 277 |
| P | 42 | QG_aug | 0.844713 | 0.935356 | 0.766854 | 0.726064 | 0.812500 | 0.933932 | 0.873216 | 0.070128 | 0.302609 | 0.177309 | 1456 | 103 | 63 | 273 |
| P | 42 | QG_clean | 0.850673 | 0.941046 | 0.786421 | 0.749326 | 0.827381 | 0.940346 | 0.883864 | 0.064406 | 0.294241 | 0.177309 | 1466 | 93 | 58 | 278 |
| P | 42 | averaging | 0.731977 | 0.922865 | 0.718973 | 0.690411 | 0.750000 | 0.927518 | 0.838759 | 0.084895 | 0.284061 | 0.177309 | 1446 | 113 | 84 | 252 |
| P | 42 | direction_only_DIAGNOSTIC | 0.241181 | 0.585006 | 0.356542 | 0.239959 | 0.693452 | 0.526620 | 0.610036 | 0.241350 | 0.674990 | 0.177309 | 821 | 738 | 103 | 233 |
| P | 42 | prevalence | 0.145395 | 0.320038 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 0.500000 | 0.160406 | 0.513736 | 0.177309 | 1559 | 0 | 336 | 0 |
| P | 42 | sensor_histgradient | 0.901299 | 0.974077 | 0.837956 | 0.822350 | 0.854167 | 0.960231 | 0.907199 | 0.049034 | 0.201030 | 0.177309 | 1497 | 62 | 49 | 287 |
| P | 42 | sensor_logistic | 0.828616 | 0.929702 | 0.811268 | 0.770053 | 0.857143 | 0.944836 | 0.900990 | 0.061724 | 0.395542 | 0.177309 | 1473 | 86 | 48 | 288 |
| P | 42 | visual | 0.303607 | 0.710922 | 0.395379 | 0.347630 | 0.458333 | 0.814625 | 0.636479 | 0.195364 | 0.915400 | 0.177309 | 1270 | 289 | 182 | 154 |
| P | 123 | F2 | 0.768630 | 0.940894 | 0.819383 | 0.808696 | 0.830357 | 0.957665 | 0.894011 | 0.056814 | 0.206838 | 0.177309 | 1493 | 66 | 57 | 279 |
| P | 123 | F2_aug | 0.771258 | 0.940617 | 0.818316 | 0.812317 | 0.824405 | 0.958948 | 0.891676 | 0.058776 | 0.211224 | 0.177309 | 1495 | 64 | 59 | 277 |
| P | 123 | QG_aug | 0.821055 | 0.927972 | 0.751032 | 0.698210 | 0.812500 | 0.924310 | 0.868405 | 0.077251 | 0.343730 | 0.177309 | 1441 | 118 | 63 | 273 |
| P | 123 | QG_clean | 0.837683 | 0.932489 | 0.774825 | 0.730871 | 0.824405 | 0.934573 | 0.879489 | 0.070347 | 0.315023 | 0.177309 | 1457 | 102 | 59 | 277 |
| P | 123 | averaging | 0.721772 | 0.917768 | 0.702778 | 0.658854 | 0.752976 | 0.915972 | 0.834474 | 0.091870 | 0.304269 | 0.177309 | 1428 | 131 | 83 | 253 |
| P | 123 | direction_only_DIAGNOSTIC | 0.241181 | 0.585006 | 0.356542 | 0.239959 | 0.693452 | 0.526620 | 0.610036 | 0.241350 | 0.674990 | 0.177309 | 821 | 738 | 103 | 233 |
| P | 123 | prevalence | 0.145395 | 0.320038 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 0.500000 | 0.160406 | 0.513736 | 0.177309 | 1559 | 0 | 336 | 0 |
| P | 123 | sensor_histgradient | 0.901299 | 0.974077 | 0.837956 | 0.822350 | 0.854167 | 0.960231 | 0.907199 | 0.049034 | 0.201030 | 0.177309 | 1497 | 62 | 49 | 287 |
| P | 123 | sensor_logistic | 0.828616 | 0.929702 | 0.811268 | 0.770053 | 0.857143 | 0.944836 | 0.900990 | 0.061724 | 0.395542 | 0.177309 | 1473 | 86 | 48 | 288 |
| P | 123 | visual | 0.286490 | 0.700602 | 0.369119 | 0.310345 | 0.455357 | 0.781911 | 0.618634 | 0.215784 | 1.095330 | 0.177309 | 1219 | 340 | 183 | 153 |
| P | 20261023 | F2 | 0.746617 | 0.940747 | 0.822840 | 0.809798 | 0.836310 | 0.957665 | 0.896987 | 0.057203 | 0.208031 | 0.177309 | 1493 | 66 | 55 | 281 |
| P | 20261023 | F2_aug | 0.752758 | 0.940501 | 0.821270 | 0.815249 | 0.827381 | 0.959589 | 0.893485 | 0.058610 | 0.210354 | 0.177309 | 1496 | 63 | 58 | 278 |
| P | 20261023 | QG_aug | 0.813794 | 0.915785 | 0.720867 | 0.661692 | 0.791667 | 0.912765 | 0.852216 | 0.086750 | 0.381448 | 0.177309 | 1423 | 136 | 70 | 266 |
| P | 20261023 | QG_clean | 0.823898 | 0.922241 | 0.748960 | 0.701299 | 0.803571 | 0.926235 | 0.864903 | 0.077398 | 0.340057 | 0.177309 | 1444 | 115 | 66 | 270 |
| P | 20261023 | averaging | 0.753034 | 0.924442 | 0.706704 | 0.665789 | 0.752976 | 0.918538 | 0.835757 | 0.085041 | 0.279245 | 0.177309 | 1432 | 127 | 83 | 253 |
| P | 20261023 | direction_only_DIAGNOSTIC | 0.241181 | 0.585006 | 0.356542 | 0.239959 | 0.693452 | 0.526620 | 0.610036 | 0.241350 | 0.674990 | 0.177309 | 821 | 738 | 103 | 233 |
| P | 20261023 | prevalence | 0.145395 | 0.320038 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 0.500000 | 0.160406 | 0.513736 | 0.177309 | 1559 | 0 | 336 | 0 |
| P | 20261023 | sensor_histgradient | 0.901299 | 0.974077 | 0.837956 | 0.822350 | 0.854167 | 0.960231 | 0.907199 | 0.049034 | 0.201030 | 0.177309 | 1497 | 62 | 49 | 287 |
| P | 20261023 | sensor_logistic | 0.828616 | 0.929702 | 0.811268 | 0.770053 | 0.857143 | 0.944836 | 0.900990 | 0.061724 | 0.395542 | 0.177309 | 1473 | 86 | 48 | 288 |
| P | 20261023 | visual | 0.306606 | 0.705498 | 0.375000 | 0.333333 | 0.428571 | 0.815266 | 0.621919 | 0.204625 | 1.036667 | 0.177309 | 1271 | 288 | 192 | 144 |

Per-fold metrics and all sensitivity protocols are in `MSM/06_evaluation_results/metrics/`; every prediction carries its native sample ID, split role, fit/case ID, model, seed and corruption. `metric_reproduction.json` verifies that all saved fold metrics match prediction artifacts within1e-12.

## Overfitting diagnostic

| initialization | model | training_in_sample_AP | AP_mean | train_minus_heldout_AP |
| --- | --- | --- | --- | --- |
| P | sensor_histgradient | 1.000000 | 0.901299 | 0.098701 |
| P | sensor_logistic | 0.978253 | 0.828616 | 0.149637 |
| P | visual | 0.980672 | 0.298901 | 0.681771 |

These in-sample scores were computed after model fitting and never entered F2. A train/held-out gap is consistent with overfitting and/or operating-condition/domain shift; it does not isolate the cause. Ten fixed head epochs and40 fixed gate epochs were used, with no assessment-selected stopping. Every loss curve and completed checkpoint is preserved.

## Data-specific limits

Direction contingency and direction-only held-out baseline are reported separately. Direction is excluded from all main predictors. Both directions have support for the frozen primary grouped design. DOWN-only label-2-excluded training fails the fixed class-support split gate; no seed search or fold reduction was performed. Within-direction held-out subgroup metrics are descriptive, not a causal direction intervention.

Technical frame/sensor eligibility does not prove that an anomaly is optically visible. Mean pooling also does not model frame order. The tasks are retrospective interval/trial classification, not online failure prediction, damage localization or early warning. Dataset/task prevalence and observation horizon differ from REASSEMBLE, so absolute cross-dataset AP cannot establish general superiority.
