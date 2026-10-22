# COMPLETE_ON_PILOT_COVERAGE

Direct answer: **inconclusive**. Primary interaction-minus-augmentation-matched-static AP difference +0.003012, paired 95% interval [-0.026711, 0.032165]. Interaction-minus-additive: +0.019649 [-0.000813, 0.038743]. Clean interaction-minus-historical-static: +0.004239 [-0.032954, 0.043717]. A nonsignificant clean difference is not evidence of no harm; zero degradation is the conservative margin.

| model | primary_mean_fold_AP | clean_mean_fold_AP | worst_primary_family_AP | worst_all_fault_family_AP | image_noise_AP | sensor_noise_AP | image_blur_AP | sensor_time_loss_AP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| historical_static | 0.255937 | 0.307929 | 0.221124 | 0.221124 | 0.290750 | 0.221124 | 0.295987 | 0.297046 |
| static_augmented | 0.253996 | 0.307397 | 0.216642 | 0.216642 | 0.291350 | 0.216642 | 0.295744 | 0.291400 |
| quality_additive | 0.237360 | 0.292965 | 0.215069 | 0.215069 | 0.259651 | 0.215069 | 0.283978 | 0.277316 |
| quality_interaction | 0.257009 | 0.312168 | 0.204040 | 0.204040 | 0.309977 | 0.204040 | 0.306400 | 0.280845 |
| visual | 0.162982 | 0.200401 | 0.125563 | 0.125563 | 0.125563 | 0.200401 | 0.179632 | 0.200401 |
| sensor | 0.239087 | 0.290531 | 0.187644 | 0.187644 | 0.290531 | 0.187644 | 0.290531 | 0.270442 |

All predeclared contrasts, including clean versus both static baselines, appear in comparison/paired_intervals.csv. Augmentation, additive quality and coefficient interactions have separate controls; a primary improvement alone does not establish that interactions are necessary.

[Data audit](DATA_AUDIT.md) · [Results and limitations](RESULTS_SUMMARY.md) · [Protocol](PROTOCOL.md) · [Prediction paths/coverage](comparison/coverage_and_prediction_index.csv) · [Review package](REVIEW_PACKAGE.zip)

Only the fixed prefix is executed; broader coverage remains untested. The original visual workflow is untouched. See progress.json and config/clock.json for exact completion and time bounds.
