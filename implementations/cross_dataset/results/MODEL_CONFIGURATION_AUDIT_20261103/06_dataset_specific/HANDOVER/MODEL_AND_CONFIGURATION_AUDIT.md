# HANDOVER model and configuration audit

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

The native589 trials become **587 aligned examples** in `common_support_v2`:335 official training,101 validation and151 test. The test set contains110 failures and41 successes (failure prevalence0.728477). Two training trials were excluded for nearest wrench/video gaps above0.1 seconds. An earlier full-tail audit flagged92 test tails; the documented common observation-window amendment before fitting superseded that rule and retained all151 test trials. This preprocessing amendment must remain explicit.

The frozen visual head uses16 temporal-bin-center letterboxed RGB frames,10 epochs, AdamW LR0.001/weight decay0.001, batch32, clip1. Six wrench channels produce36 statistical features. LR is balanced C1, lbfgs, max_iter2000, random_state0; HGB uses0.1 learning rate,100 iterations,15 leaves, min_samples_leaf10, l2_regularization1, early_stoppingFalse with balanced sample weights. All three seeds42,123,20261023 completed the supported baselines. Average uses visual plus LR. Official validation rows are descriptive under the fixed recipe; they are not inner OOF predictions.

**F2, F2aug, quality-clean and quality-aug are NOT EXECUTED / BLOCKED.** Official documentation describes a participant-disjoint split, but available metadata and author code identify robot/task/trial rather than participants. The empty `participant_id` fields are preserved. Trial, robot, task or date identifiers cannot substitute for people. Certifiable participant-disjoint inner OOF is therefore unavailable. No fusion was fitted on official validation/test to bypass that limitation, and no participant bootstrap is defensible.

The final manifest preserves clock mappings, selected frames, native wrench indices, source hashes and original labels. HSR wrench is measured while Gen3 wrench is estimated;14 zero-channel traces were retained. These are limitations, not silently repaired data. Three seeds reuse the same151 test trials and do not supply independent participant evidence.

Mean held-out AP is0.771647 visual,0.823624 LR,0.906319 HGB,0.803102 average and0.728477 constant prior. Full per-seed, official-validation, test and robustness metrics remain in COMPLETE_RESULTS.csv. R transfer has not executed: the20-epoch canonical donor fails the validator's25-epoch minimum. Recovering participant groups requires official pseudonymous metadata, not inferred identities.

| Model | Mean held-out AP | AUROC | F1 | Brier |
| --- | --- | --- | --- | --- |
| averaging | 0.803102 | 0.580118 | 0.728694 | 0.230493 |
| prevalence | 0.728477 | 0.500000 | 0.842912 | 0.197807 |
| sensor_histgradient | 0.906319 | 0.746563 | 0.781395 | 0.212665 |
| sensor_logistic | 0.823624 | 0.582040 | 0.720000 | 0.237479 |
| visual | 0.771647 | 0.539911 | 0.580126 | 0.264805 |

## Evidence anchors

- [HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json](../../../../HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json) — participant_oof_gate/observation_amendment/validation_use.
- [HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv](../../../../HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv) — 587 mapped IDs, native labels, empty participant IDs.
- [HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json](../../../../HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json) — three seeds complete; fused methods skipped.
- [HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json](../../../../HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json) — official dataset record and metadata.
