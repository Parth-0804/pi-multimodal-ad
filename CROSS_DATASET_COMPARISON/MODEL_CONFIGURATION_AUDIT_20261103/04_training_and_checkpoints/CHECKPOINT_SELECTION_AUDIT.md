# Checkpoint selection and training completion

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

Original visual/PatchTST select a common epoch candidate by mean inner AP (5/10 or3/6); candidate training loss trajectories do not constitute held-out curves. F3/gates select an inner configuration and evaluate source-defined final epochs. Later temporal/anchored models use100maximum, min10, patience12 and saved validation objective; V-FT uses20maximum, patience5. Per-run best/final values are preserved rather than inferred from directory names.

B100 and C100 each executed100epochs. Best epochs **14 and47** are selected by V AP, with V weighted BCE/earliest tie rule in the Phase1 code. All100epoch histories exist; selected checkpoint state epoch agrees with receipt and history. This is not early termination at14/47. Checkpoint selection uses V, not the753assessment labels. However the choice of this particular fit for a new100epoch follow-up was informed by earlier experiment results, so the final cohort is not pristine.

C20 executes exactly20epochs for25fits at seed42; no early stop, originalcosine50prefix. Receipt predictions correspond to the V-selected best checkpoint, not automatically epoch20. The approved stop marker is final for the25-fit cap; it is not the original75-fit all-complete marker. Vi frozen100 similarly runs all100 and picks the first strict maximum of V macro AP, verified for all72heads.

PHM saved histories/counts are separate from native classification. Legacy SQ2/SQ3 aggregate results do not retain actual selected epochs or executed epoch histories: those fields remain NOT RECORDED. No epoch count is invented from max80.

For every exact best/last path, hash, available state components and recorded epoch, use CHECKPOINT_INVENTORY.csv, TRAINING_RUN_INVENTORY.csv and JSON_FITTED_STATE_REFERENCES.csv. Original selected outputs were hash-checked before metric recomputation.

## Evidence anchors

- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json) — effective shared100 horizon; head/backbone LR.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py) — all CNN stages, FrozenBN affine promotion; fixed running moments.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py) — training100/checkpoint selection/recovery.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json) — history/best/executed_epochs, T/V/C/assessment sample identities.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json) — history/best/executed_epochs, T/V/C/assessment sample identities.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
- [src/reassemble/additional_improvements/neural.py](../../../src/reassemble/additional_improvements/neural.py) — early stop and best-state selection.
