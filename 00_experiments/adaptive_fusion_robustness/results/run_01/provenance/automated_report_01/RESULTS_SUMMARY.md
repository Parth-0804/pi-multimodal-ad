# COMPLETE_ON_PILOT_COVERAGE — controlled adaptive-fusion robustness

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

Coverage: ['fold_01']. The fixed prefix is based on training-only end-to-end runtime, not scores. Five folds were the target; unavailable GPU ownership and bounded CPU runtime restricted this study to a prominently labeled pilot. No old workflow was stopped or restarted. Scientific cutoff and final deadline are in config/clock.json, with the recorded initial-audit allowance deducted; the final three hours are reserved for evaluation/reporting.

Question: for identical frozen 16-frame CNN and sensor branches, does quality interaction improve predefined corruption AP over augmentation-matched static F2? Branches and calibrators are fixed. Clean historical F2 is an additional reference. New models share identical inner OOF parent actions, deterministic augmentations and 0.5/0.25/0.25 weights. Eight observable input-quality proxies use no clean counterpart, injected severity/name/seed, identity, correctness or label as predictor inputs. Input-dependent coefficients are not trust percentages or causal modality importance.

Primary AP is calculated separately per fold/family/severity/realization, then averaged repeats -> severities -> two Gaussian families -> matched folds equally. Pooled outer AP is separately labeled. The 2,000 paired recording-cluster resamples stay within folds and retain every action/variant multiplicity. Intervals condition on fixed fits and three realizations; secondary intervals are unadjusted. Blur and sensor time loss are held-out fitting fault families, not an independent dataset. Complete absence uses an identical explicit surviving-branch fallback for all models; both absent is unavailable.

This is DEVELOPMENT-EXPOSED exploratory complete-action classification. It is not online/early detection, a validated reliability estimator, independent generalization or a result for every possible fault. See DATA_AUDIT.md for known issues and semantic limits. Historical Task4 is excluded.

Artifacts: PROTOCOL.md; config/; checks/; fusion_fits/ with identified OOF inputs and saved fusion components when complete; predictions/; comparison/coverage_and_prediction_index.csv; comparison/per_condition_metrics.csv; comparison/paired_intervals.csv; comparison/model_comparison.csv. Missing not-yet-produced results are explicitly incomplete, not zero effects. Independent saved-table recalculation: `ma_thesis_env/bin/python -B 00_experiments/adaptive_fusion_robustness/code/recalculate.py` after evaluation. Source, small tables, audit visuals and provenance are in REVIEW_PACKAGE.zip; raw videos, feature caches and upstream weight blobs are excluded and referenced by identity.

Next decision: require complete matched coverage and independent-recording validation before adopting a quality-conditioned fusion pipeline. No additional experiment is launched here.
