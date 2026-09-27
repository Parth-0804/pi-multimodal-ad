# Cross-study synthesis handoff

## Central comparison

The comparison concerns **conditions for meaningful fusion**, not which dataset scored higher. PHM remains Study 1 and REASSEMBLE remains Study 2; neither is rewritten to create a cleaner success narrative.

## Different targets require different metrics

**Task-appropriate metrics differ across the two empirical studies because PHM is a continuous damage-estimation problem whereas REASSEMBLE is a binary execution-failure classification problem.**

PHM uses MAE, RMSE where reported, Spearman/rank association and grouped paired uncertainty. REASSEMBLE uses AUROC, AUPRC, balanced accuracy, macro-F1, failure precision/recall, Brier and ECE. Never directly compare a numerical PHM MAE with REASSEMBLE AUROC, AP or F1. Improvements are interpreted within task against task-appropriate references.

## PHM evidence available in this repository

The retained leave-one-experiment-out summary covers 20 runs from A/B/F and uses 10,000 run-cluster bootstrap draws. Its provisional damage-estimation target must not be called independently validated physical damage ground truth.

| PHM model | MAE | MAE 95% interval | RMSE | Spearman |
| --- | --- | --- | --- | --- |
| constant_train_mean | 0.8042 | [0.5769, 1.0360] | 0.9608 | -0.0354 |
| patchtst_single_encoder | 0.9415 | [0.6754, 1.2264] | 1.1337 | -0.2053 |
| fused_all_three | 0.8238 | [0.5527, 1.1015] | 1.0332 | -0.1046 |

The stored paired fused-minus-constant difference is 0.0177 [-0.1962, 0.2278] on its run-weighted comparison, with no resolved benefit. Its paired estimator need not equal the difference of pooled displayed MAEs. Source: `runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json`. The RT-DETR R4 image row is explicitly **NOT LOEO**, lacks EXP-B predictions and must not enter this grouped model ranking.

Retained `docs/planning/HANDOFF.md` documents provisional photo-derived labels, run-level rather than verified UTC image/sensor pairing, only 20 run units, and deployment restricted to sensors. It is historical and partly superseded by later run artifacts: its statement that no fusion had occurred must not override the later LOEO summary. These sources substantiate target/independence/deployment caveats. Later external PHM reasoning about additional positive controls or corruption studies is not quantitatively reconstructed here without its exact artifacts. The importance of positive controls and the warning that flat low-signal degradation is not robustness are methodological conclusions, not invented PHM measurements.

## REASSEMBLE evidence

REASSEMBLE provides explicit execution outcomes, 148 recording groups and simultaneous visual/sensor measurements. Statistical sensors exceeded the tested temporal Transformer. Section 1B established visual complementarity and incremental static-fusion AP; Section 2 found no clean gain from additional gating. The predeclared corruption suite now supports this bounded SQ3 answer: No family/gate pair met both the predeclared weight-adaptation and smaller-degradation criteria at its highest severity. Absolute high-severity AP superiority over F2 was supported for none of these family/gate pairs. These are separate claims and marginal exploratory intervals; no universal reliability-awareness claim follows.

Modality dropout changed clean AP by -0.0037 [-0.0085, 0.0003] versus ordinary F6. Under complete visual or sensor loss, predictions are exactly the surviving frozen branch for both variants; missing-condition improvement is structurally impossible for this masked scalar-logit gate. At marginal paired 95% intervals, degraded AP improved for S2_0.3 and worsened for V1_0.05; remaining comparisons were unresolved.

Audio failed the segment-timing gate; the study did not force an AST result.

## Conditions and implications

1. Validate the target and independent evaluation units before optimizing architecture.
2. Establish deployable modality informativeness and perform group-compatible controls.
3. Establish incremental complementarity against the strongest unimodal reference.
4. Prefer simple fusion when added complexity lacks supported benefit.
5. Test unavailable and degraded modalities explicitly; report absolute performance as well as decline from clean performance.
6. Require both induced allocation response and predictive benefit before calling a gate reliability-aware, and restrict that claim to the tested families.
7. Preserve negative results, including architecture failure, timing-gate exclusion and structurally limited fallback.

## Integration boundary

This addendum is intended for later integration with the researcher’s external master Reasoning Record. That record and historical PHM artifacts were not modified. Scene/day/object confounding, adaptive reuse of REASSEMBLE folds, artificial corruption and VM timing prevent broad deployment/generalization conclusions.
