# Important completed model evaluations

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

| Dataset | Study/model | Seed | Fold | Held-out N | Prevalence | AP | AUROC | F1 | Brier | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REASSEMBLE | original SECTION1B/sensor_statistics | one original split/offset family | pooled5 | 4530 | 0.112362 | 0.429392 | 0.779325 | 0.622332 | 0.080448 | COMPLETE; exploratory test reuse |
| REASSEMBLE | original SECTION1B/rtdetr | one original split/offset family | pooled5 | 4530 | 0.112362 | 0.230658 | 0.697795 | 0.515284 | 0.094299 | COMPLETE; exploratory test reuse |
| REASSEMBLE | original SECTION1B/minimal_late_fusion | one original split/offset family | pooled5 | 4530 | 0.112362 | 0.447299 | 0.794968 | 0.634000 | 0.078443 | COMPLETE; exploratory test reuse |
| REASSEMBLE | REASSEMBLE_PHASE1_C20/C_full_finetuned16 | 42 | pooled5 | 4530 | 0.112362 | 0.312127 | 0.756386 | 0.130809 | 0.090146 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M1_frozen100 | 42 | 0 | 753 | 0.102258 | 0.193776 | 0.664605 | 0.000000 | 0.089570 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M2_finetuned100 | 42 | 0 | 753 | 0.102258 | 0.212585 | 0.675325 | 0.070588 | 0.089255 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M3_sensor | 42 | 0 | 753 | 0.102258 | 0.327705 | 0.723680 | 0.252632 | 0.081479 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M4_F2_frozen | 42 | 0 | 753 | 0.102258 | 0.334977 | 0.728675 | 0.177778 | 0.080453 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M5_F2_finetuned | 42 | 0 | 753 | 0.102258 | 0.349094 | 0.740298 | 0.177778 | 0.080157 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M6_average_frozen | 42 | 0 | 753 | 0.102258 | 0.348007 | 0.721240 | 0.073171 | 0.081605 | COMPLETE; scope limited as documented |
| REASSEMBLE | CNN100_STATIC_SENSOR_F2/M7_average_finetuned | 42 | 0 | 753 | 0.102258 | 0.358533 | 0.745985 | 0.074074 | 0.080793 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S3 | 123 | pooled3 | 4382 | 0.856458 | 0.954370 | 0.784370 | 0.918168 | 0.107868 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S2 | 123 | pooled3 | 4382 | 0.856458 | 0.970510 | 0.853756 | 0.916996 | 0.109334 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S3 | 20261023 | pooled3 | 4382 | 0.856458 | 0.954370 | 0.784370 | 0.918168 | 0.107868 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S2 | 20261023 | pooled3 | 4382 | 0.856458 | 0.970510 | 0.853756 | 0.916996 | 0.109334 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S3 | 42 | pooled3 | 4382 | 0.856458 | 0.954370 | 0.784370 | 0.918168 | 0.107868 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/S2 | 42 | pooled3 | 4382 | 0.856458 | 0.970510 | 0.853756 | 0.916996 | 0.109334 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1 | 123 | pooled3 | 4382 | 0.856458 | 0.845749 | 0.475157 | 0.922680 | 0.125489 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1 | 20261023 | pooled3 | 4382 | 0.856458 | 0.839708 | 0.463408 | 0.922680 | 0.126591 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1 | 42 | pooled3 | 4382 | 0.856458 | 0.853052 | 0.479402 | 0.922680 | 0.129213 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1_high_only | 123 | pooled3 | 4382 | 0.856458 | 0.851883 | 0.456897 | 0.922680 | 0.127796 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1_high_only | 20261023 | pooled3 | 4382 | 0.856458 | 0.849646 | 0.466178 | 0.922680 | 0.128678 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/V1_high_only | 42 | pooled3 | 4382 | 0.856458 | 0.847815 | 0.459756 | 0.922680 | 0.128452 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F1_average | 123 | pooled3 | 4382 | 0.856458 | 0.933227 | 0.731510 | 0.922680 | 0.111606 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F2 | 123 | pooled3 | 4382 | 0.856458 | 0.943543 | 0.746198 | 0.922129 | 0.113445 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/quality_gate | 123 | pooled3 | 4382 | 0.856458 | 0.948804 | 0.760464 | 0.919315 | 0.110313 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/gate_static | 123 | pooled3 | 4382 | 0.856458 | 0.952706 | 0.773207 | 0.921808 | 0.108946 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F1_average | 20261023 | pooled3 | 4382 | 0.856458 | 0.931124 | 0.726439 | 0.922415 | 0.112168 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F2 | 20261023 | pooled3 | 4382 | 0.856458 | 0.940587 | 0.733723 | 0.922129 | 0.113740 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/quality_gate | 20261023 | pooled3 | 4382 | 0.856458 | 0.950272 | 0.761641 | 0.919712 | 0.110474 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/gate_static | 20261023 | pooled3 | 4382 | 0.856458 | 0.952475 | 0.770848 | 0.921921 | 0.109444 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F1_average | 42 | pooled3 | 4382 | 0.856458 | 0.931760 | 0.716501 | 0.922282 | 0.113196 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/F2 | 42 | pooled3 | 4382 | 0.856458 | 0.945168 | 0.752701 | 0.922129 | 0.113107 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/quality_gate | 42 | pooled3 | 4382 | 0.856458 | 0.947321 | 0.756404 | 0.919349 | 0.110529 | COMPLETE; scope limited as documented |
| VIFAILBACK | 20261029T004900Z/gate_static | 42 | pooled3 | 4382 | 0.856458 | 0.951757 | 0.769223 | 0.921692 | 0.109431 | COMPLETE; scope limited as documented |
| MSM | primary__group_id/F2 | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.756879 | 0.940705 | 0.820887 | 0.056703 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/F2_aug | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.760170 | 0.940401 | 0.818497 | 0.058183 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/QG_aug | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.826521 | 0.926371 | 0.746251 | 0.078043 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/QG_clean | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.837418 | 0.931925 | 0.770069 | 0.070717 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/averaging | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.735594 | 0.921692 | 0.709485 | 0.087269 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/direction_only_DIAGNOSTIC | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.241181 | 0.585006 | 0.356542 | 0.241350 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/prevalence | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.145395 | 0.320038 | 0.000000 | 0.160406 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/sensor_histgradient | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.901299 | 0.974077 | 0.837956 | 0.049034 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/sensor_logistic | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.828616 | 0.929702 | 0.811268 | 0.061724 | COMPLETE; mean of per-seed pooled AP |
| MSM | primary__group_id/visual | mean3 seeds | pooled3 outer per seed | 1895 | 0.177309 | 0.298901 | 0.705674 | 0.379833 | 0.205258 | COMPLETE; mean of per-seed pooled AP |
| HANDOVER | official/averaging | mean3 seeds | official test | 151 | 0.728477 | 0.803102 | 0.580118 | 0.728694 | 0.230493 | COMPLETE; mean seeds official test |
| HANDOVER | official/prevalence | mean3 seeds | official test | 151 | 0.728477 | 0.728477 | 0.500000 | 0.842912 | 0.197807 | COMPLETE; mean seeds official test |
| HANDOVER | official/sensor_histgradient | mean3 seeds | official test | 151 | 0.728477 | 0.906319 | 0.746563 | 0.781395 | 0.212665 | COMPLETE; mean seeds official test |
| HANDOVER | official/sensor_logistic | mean3 seeds | official test | 151 | 0.728477 | 0.823624 | 0.582040 | 0.720000 | 0.237479 | COMPLETE; mean seeds official test |
| HANDOVER | official/visual | mean3 seeds | official test | 151 | 0.728477 | 0.771647 | 0.539911 | 0.580126 | 0.264805 | COMPLETE; mean seeds official test |

AP values are never ranked across datasets. MSM entries are means across seeds of pooled3-outer AP; ViFailback and original REASSEMBLE entries are pooled AP. ViFailback both-class metrics are in its dataset report. All other recorded model variants, folds, robustness conditions and metric endpoints remain in ALL_MODEL_RESULTS_SUMMARY.csv and ALL_RECORDED_METRICS_LONG.csv. Missing individual metric values are NOT RECORDED, not zero.
