# Version2 cohort qualification

The [verified action/split reconciliation](../../../../COHORT_RECONCILIATION/MATCHED_COMPARISON_SUMMARY.md) governs REASSEMBLE comparisons in this package. The753 actions (26 recordings) are exactly original outer fold0 within4,530 actions (148 recordings). The920-action selected inner assessment is disjoint. C20 outer refit job4 shares the753 held-out actions with CNN100; C20 inner job2 does not. Compare only matching action/label/assessment/observation passports. Training and selection differences remain limitations. A stale prediction_recordings list is documented without altering the original JSON. No training or inference was run.

The original audit text and numerical results follow unchanged; generic pre-reconciliation comparison statements are historical context and are superseded by the revised comparability matrix and passports.

---

# Leakage and selection audit

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

The audit checked disjoint sample roles for25 REASSEMBLE plan jobs and12 ViFailback T/V/C/assessment jobs. Vi task groups are disjoint, and the three inner-OOF pools exactly cover their corresponding outer training pools without assessment overlap. All MSM/Handover saved prediction rows, including all roles and corruptions, were joined to native final manifests; IDs and labels matched. Original case output hashes and763 independent metric/history checks passed. `SPLIT_AND_LABEL_VERIFICATION.csv` records the checks and their limits. A valid nominal-group contract does not certify unknown physical participant/tool/session identities.

Original REASSEMBLE normalization, branch selection, sigmoid calibration and fusion fitting use nested training-side data. Phase1 separates T/V/C/assessment. However, selecting fit3 for a later100-epoch study and choosing boundary variants from exposed outer AP introduces research-level post-selection. Per-fit isolation and an untouched confirmatory test are different properties. The100-epoch follow-up's920-row stacking bank is genuinely base-held-out but is not a full four-inner-fold100-epoch OOF design. Fusion accuracy on its own meta-training rows is training performance.

MSM nominal-group OOF is checked. Date-proxy sensitivities and incomplete tool/workpiece identities limit stronger independence claims. External standardizers, quality moments and corruption scales use fitting rows. Handover trial-disjointness cannot certify participant-disjointness; the participant OOF gate appropriately blocks fused training. The common-window observation amendment remains explicit, and participant identities were not invented.

ViFailback task disjointness is supported; physical-session and hardware-clock independence remain unverified. Seeds reuse the same episodes. The4,384-row feature bank versus4,382-row model cohort is a valid ID-subset join, not automatically leakage. Labels describe episode outcomes, not visible failure times.

**Concrete PHM legacy preprocessing defect:** `scripts/phm2026/results/sq2_sq3_fusion.py::main` fits a single normalizer before LOEO using default `training_split='train'`, which is fixed EXP-B in the source minute table. LOEO instead trains on EXP-F for EXP-A/EXP-B assessments. Consequently, EXP-B held-out measurements enter its normalization; for EXP-A assessment the scaler uses EXP-B validation rather than EXP-F training. The normalizer is training-only for the canonical B/A/F design but not for this changing LOEO design. The aggregate results are preserved with this limitation; no correction was made.

Some PHM late-fusion summaries declare targetv3 while their resolved configuration declaresv2. Both records remain visible; equivalence is not assumed. The20-setting DINO appearance sweep reuses38 human calls for comparison/selection; best-of20 is optimistic development performance.

Missing identity metadata, repeated test exposure and concrete preprocessing-scope mismatches are separately reported. These findings do not imply intentional leakage. The audit did not change labels, formulas, source code, splits or historical results.

## Evidence anchors

- [configs/reassemble/section1.json](../../../configs/reassemble/section1.json) — visual/sensor/logistic_C/selection/calibration.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — actual classifier forwards, neural_fit, logistic_fit.
- [src/reassemble/section1_features.py](../../../src/reassemble/section1_features.py) — frame pooling and normalized-progress sensor resampling.
- [runs/reassemble/20260927T154732Z-section1/training_implementation.json](../../../runs/reassemble/20260927T154732Z-section1/training_implementation.json) — recorded original implementation revision.
- [MSM/04_experiment_protocol/experiment_config.json](../../../MSM/04_experiment_protocol/experiment_config.json) — fixed P recipe, labels/groups/sensor channels.
- [MSM/03_processed_model_inputs/final_sample_manifest.csv](../../../MSM/03_processed_model_inputs/final_sample_manifest.csv) — 1895 eligible sample IDs/native labels/clock mapping/source hashes.
- [MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json](../../../MSM/06_evaluation_results/P_EVALUATION_COMPLETE.json) — 54 completed protocol/fold/seed cases, output hashes.
- [CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py](../../src/external_eval/evaluate.py) — execute_case: train, inner OOF, official validation, held-out scopes.
- [CROSS_DATASET_COMPARISON/src/external_eval/models.py](../../src/external_eval/models.py) — fit_base/fit_fusions/fit_quality/predictions.
- [HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json](../../../HANDOVER/experiments/common_support_v2/04_experiment_protocol/experiment_config.json) — participant_oof_gate/observation_amendment/validation_use.
- [HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv](../../../HANDOVER/experiments/common_support_v2/03_processed_model_inputs/final_sample_manifest.csv) — 587 mapped IDs, native labels, empty participant IDs.
- [HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json](../../../HANDOVER/experiments/common_support_v2/06_evaluation_results/P_EVALUATION_COMPLETE.json) — three seeds complete; fused methods skipped.
- [HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json](../../../HANDOVER/01_raw_dataset/source_evidence/zenodo_record_10708763.json) — official dataset record and metadata.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
- [scripts/phm2026/results/sq2_sq3_fusion.py](../../../scripts/phm2026/results/sq2_sq3_fusion.py) — main fixednormalizer before evaluate/train_fold LOEO.
- [src/phm2026/preprocessing/timeseries.py](../../../src/phm2026/preprocessing/timeseries.py) — fit_feature_normalizer training_split=train.
- [docs/thesis/ANOMALYDINO_RESULT_20260913T215556Z.md](../../../docs/thesis/ANOMALYDINO_RESULT_20260913T215556Z.md) — bestof20development caveat.
