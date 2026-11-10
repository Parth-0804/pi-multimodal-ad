# HANDOVER modality robustness

All corruptions/severities were fixed before inspecting held-out effects. RGB Gaussian blur (sigma1/2/4), brightness/contrast (0.8/0.5/0.2), centered content occlusion (10/25/40%) were applied to real image pixels and passed through the actual frozen CNN. They are not embedding noise proxies. Frame dropout omits4/8/12 real frames and pools the remaining cached frame embeddings, mathematically exact for this frozen independent-frame CNN and mean pool.

Gaussian measurement noise (0.1/0.5/1× pooled raw training channel SD), zeroed channels and explicitly missing channels (10/30/50%) act on the corresponding sensor observations/statistics. Statistics are recomputed for noise/zeroed channels. Missing-channel statistics use only clean training feature means, with explicit masks for the gate; no scaler is refitted on corrupted test data. Randomness is stable per sample/type and shared across models, seeds and P/R. Labels, groups and split roles do not change.

## All measured scenarios, means of the three seeds

| initialization | model | corruption | AP | absolute_AP_degradation | relative_AP_degradation_percent |
| --- | --- | --- | --- | --- | --- |
| P | averaging | brightness_contrast_1 | 0.798156 | 0.004945 | 0.598554 |
| P | averaging | brightness_contrast_2 | 0.793864 | 0.009238 | 1.117377 |
| P | averaging | brightness_contrast_3 | 0.792650 | 0.010452 | 1.272861 |
| P | averaging | channel_dropout_1 | 0.723883 | 0.079219 | 9.849629 |
| P | averaging | channel_dropout_2 | 0.701075 | 0.102027 | 12.689978 |
| P | averaging | channel_dropout_3 | 0.701824 | 0.101278 | 12.599903 |
| P | averaging | clean | 0.803102 | 0.000000 | 0.000000 |
| P | averaging | frame_dropout_1 | 0.800492 | 0.002609 | 0.322226 |
| P | averaging | frame_dropout_2 | 0.797148 | 0.005953 | 0.740825 |
| P | averaging | frame_dropout_3 | 0.792120 | 0.010981 | 1.368144 |
| P | averaging | gaussian_blur_1 | 0.798975 | 0.004126 | 0.492639 |
| P | averaging | gaussian_blur_2 | 0.784816 | 0.018286 | 2.252367 |
| P | averaging | gaussian_blur_3 | 0.779066 | 0.024036 | 2.966694 |
| P | averaging | missing_sensor | 0.771647 | 0.031455 | 3.907602 |
| P | averaging | missing_sensor_channels_1 | 0.797447 | 0.005655 | 0.678400 |
| P | averaging | missing_sensor_channels_2 | 0.743081 | 0.060020 | 7.445353 |
| P | averaging | missing_sensor_channels_3 | 0.758146 | 0.044955 | 5.574223 |
| P | averaging | missing_visual | 0.823624 | -0.020522 | -2.574347 |
| P | averaging | partial_occlusion_1 | 0.774090 | 0.029012 | 3.588346 |
| P | averaging | partial_occlusion_2 | 0.779754 | 0.023348 | 2.877127 |
| P | averaging | partial_occlusion_3 | 0.806617 | -0.003515 | -0.459658 |
| P | averaging | sensor_noise_1 | 0.805328 | -0.002226 | -0.285189 |
| P | averaging | sensor_noise_2 | 0.820532 | -0.017430 | -2.186440 |
| P | averaging | sensor_noise_3 | 0.796955 | 0.006147 | 0.750302 |
| P | prevalence | brightness_contrast_1 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | brightness_contrast_2 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | brightness_contrast_3 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | channel_dropout_1 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | channel_dropout_2 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | channel_dropout_3 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | clean | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | frame_dropout_1 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | frame_dropout_2 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | frame_dropout_3 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | gaussian_blur_1 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | gaussian_blur_2 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | gaussian_blur_3 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | missing_sensor | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | missing_sensor_channels_1 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | missing_sensor_channels_2 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | missing_sensor_channels_3 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | missing_visual | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | partial_occlusion_1 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | partial_occlusion_2 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | partial_occlusion_3 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | sensor_noise_1 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | sensor_noise_2 | 0.728477 | 0.000000 | 0.000000 |
| P | prevalence | sensor_noise_3 | 0.728477 | 0.000000 | 0.000000 |
| P | sensor_histgradient | brightness_contrast_1 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | brightness_contrast_2 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | brightness_contrast_3 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | channel_dropout_1 | 0.872173 | 0.034146 | 3.767570 |
| P | sensor_histgradient | channel_dropout_2 | 0.844345 | 0.061975 | 6.838075 |
| P | sensor_histgradient | channel_dropout_3 | 0.856297 | 0.050022 | 5.519301 |
| P | sensor_histgradient | clean | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | frame_dropout_1 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | frame_dropout_2 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | frame_dropout_3 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | gaussian_blur_1 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | gaussian_blur_2 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | gaussian_blur_3 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | missing_sensor_channels_1 | 0.895534 | 0.010785 | 1.189983 |
| P | sensor_histgradient | missing_sensor_channels_2 | 0.860457 | 0.045862 | 5.060243 |
| P | sensor_histgradient | missing_sensor_channels_3 | 0.864100 | 0.042219 | 4.658294 |
| P | sensor_histgradient | missing_visual | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | partial_occlusion_1 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | partial_occlusion_2 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | partial_occlusion_3 | 0.906319 | 0.000000 | 0.000000 |
| P | sensor_histgradient | sensor_noise_1 | 0.913056 | -0.006736 | -0.743269 |
| P | sensor_histgradient | sensor_noise_2 | 0.714359 | 0.191960 | 21.180208 |
| P | sensor_histgradient | sensor_noise_3 | 0.731344 | 0.174975 | 19.306112 |
| P | sensor_logistic | brightness_contrast_1 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | brightness_contrast_2 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | brightness_contrast_3 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | channel_dropout_1 | 0.727196 | 0.096427 | 11.707704 |
| P | sensor_logistic | channel_dropout_2 | 0.704906 | 0.118718 | 14.414078 |
| P | sensor_logistic | channel_dropout_3 | 0.704861 | 0.118763 | 14.419521 |
| P | sensor_logistic | clean | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | frame_dropout_1 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | frame_dropout_2 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | frame_dropout_3 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | gaussian_blur_1 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | gaussian_blur_2 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | gaussian_blur_3 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | missing_sensor_channels_1 | 0.799050 | 0.024574 | 2.983635 |
| P | sensor_logistic | missing_sensor_channels_2 | 0.727715 | 0.095909 | 11.644737 |
| P | sensor_logistic | missing_sensor_channels_3 | 0.752408 | 0.071216 | 8.646654 |
| P | sensor_logistic | missing_visual | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | partial_occlusion_1 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | partial_occlusion_2 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | partial_occlusion_3 | 0.823624 | 0.000000 | 0.000000 |
| P | sensor_logistic | sensor_noise_1 | 0.818158 | 0.005465 | 0.663547 |
| P | sensor_logistic | sensor_noise_2 | 0.835789 | -0.012165 | -1.477059 |
| P | sensor_logistic | sensor_noise_3 | 0.824952 | -0.001329 | -0.161344 |
| P | visual | brightness_contrast_1 | 0.766197 | 0.005450 | 0.699190 |
| P | visual | brightness_contrast_2 | 0.748487 | 0.023160 | 2.989826 |
| P | visual | brightness_contrast_3 | 0.730599 | 0.041048 | 5.318101 |
| P | visual | channel_dropout_1 | 0.771647 | 0.000000 | 0.000000 |
| P | visual | channel_dropout_2 | 0.771647 | 0.000000 | 0.000000 |
| P | visual | channel_dropout_3 | 0.771647 | 0.000000 | 0.000000 |
| P | visual | clean | 0.771647 | 0.000000 | 0.000000 |
| P | visual | frame_dropout_1 | 0.772185 | -0.000538 | -0.070143 |
| P | visual | frame_dropout_2 | 0.769155 | 0.002492 | 0.324091 |
| P | visual | frame_dropout_3 | 0.755974 | 0.015673 | 2.034439 |
| P | visual | gaussian_blur_1 | 0.772700 | -0.001052 | -0.143665 |
| P | visual | gaussian_blur_2 | 0.760928 | 0.010720 | 1.378491 |
| P | visual | gaussian_blur_3 | 0.738580 | 0.033067 | 4.272001 |
| P | visual | missing_sensor | 0.771647 | 0.000000 | 0.000000 |
| P | visual | missing_sensor_channels_1 | 0.771647 | 0.000000 | 0.000000 |
| P | visual | missing_sensor_channels_2 | 0.771647 | 0.000000 | 0.000000 |
| P | visual | missing_sensor_channels_3 | 0.771647 | 0.000000 | 0.000000 |
| P | visual | partial_occlusion_1 | 0.728512 | 0.043135 | 5.579641 |
| P | visual | partial_occlusion_2 | 0.727510 | 0.044137 | 5.714885 |
| P | visual | partial_occlusion_3 | 0.735802 | 0.035846 | 4.640779 |
| P | visual | sensor_noise_1 | 0.771647 | 0.000000 | 0.000000 |
| P | visual | sensor_noise_2 | 0.771647 | 0.000000 | 0.000000 |
| P | visual | sensor_noise_3 | 0.771647 | 0.000000 | 0.000000 |

Degradation is clean AP minus corrupted AP; negative values mean measured improvement. Relative degradation divides by clean AP. Individual seed values and all grouping/label sensitivities are preserved in the CSV, not selected by the heatmap.

For completely missing vision/sensors, the unavailable unimodal model is marked UNAVAILABLE_MODALITY. Averaging, F2 and quality gates use the separately identified deterministic surviving-branch fallback. F2 never receives an invented missing-branch prediction. Equal fallback performance is imposed behavior, not proof that a learned gate discovered robustness. Compare every corruption with the appropriate unaffected/surviving unimodal baseline, not only the clean fused score.

QG_clean and QG_aug are explicitly distinct from logistic F2. QG_aug/F2_aug saw the same seven lowest-severity OOF corruptions at fixed weight/exposure; higher severities are assessment only. Any advantage of augmentation is not automatically a quality-gating advantage. These experiments establish only behavior under the named synthetic corruptions and native data-quality limitations, not robustness to arbitrary real hardware faults, unseen robots/machines or all forms of missing data.

Brightness, image variance and sensor standard deviation are quality proxies that can also encode scene/process context. Gate weights are not causal explanations or independently verified reliability estimates. The saved quality_gate_allocations.csv records the actual held-out allocation summaries where gates were permitted.

F2, F2_aug, QG_clean and QG_aug are SKIPPED: participant-disjoint OOF probabilities cannot be certified without participant IDs. No in-sample probability stack or trial-group substitute was used. Robot and task differ in force estimation, camera view and class prevalence; see subgroup tables. The common-support amendment retains all151 official test trials; it is not a test-score-selected cohort.
