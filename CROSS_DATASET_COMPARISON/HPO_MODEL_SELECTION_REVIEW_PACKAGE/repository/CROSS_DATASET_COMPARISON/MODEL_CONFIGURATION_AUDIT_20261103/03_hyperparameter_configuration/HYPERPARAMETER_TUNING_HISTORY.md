# Hyperparameter tuning history and verdicts

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

| Model | Verdict | Parameters tested | Configurations/trials | Selection | Evidence |
| --- | --- | --- | --- | --- | --- |
| Original REASSEMBLE static/action LR | SYSTEMATICALLY TUNED | C0.1/1/10 | 3 per selection fold | mean inner AP; selected refit | configs/reassemble/section1.json; section1_models.evaluate_model |
| Original visual head / PatchTST | CHECKPOINT SELECTION ONLY | epochs5/10;3/6 | 2 stored epoch candidates each | mean inner AP; same optimizer recipe | configs/reassemble/section1.json |
| F3 | SYSTEMATICALLY TUNED | hidden32/epochs10 vs64/epochs20 | 2 coupled configs | mean inner AP of three-seed mean | configs/reassemble/section2.json; section2.py |
| F4/F5/F6 | SYSTEMATICALLY TUNED | hidden8/16 | 2 per gate family | mean inner AP | src/reassemble/section2.py; section2_models.py |
| Anchored F2 adjustments | SYSTEMATICALLY TUNED | lambda.01/.1/1 | 3 per adjustment family | inner validation AP/robust selection from saved execution | configs/reassemble/additional_improvements/execution.json |
| Boundary V0–V5 / legacy16/32/encoder | LIMITED/MANUAL TUNING | architecture/frame/final-stage alternatives | see variant receipts | outer-score-informed follow-up; exploratory | src/reassemble/boundary_visual/runner.py; legacy receipts |
| C20 and B/C100 | CHECKPOINT SELECTION ONLY | validation epoch; fixed LR/wd/batch | one recipe per arm | V AP; no optimizer search | PHASE1_C_ONLY_CONFIG.json; PHASE1_COMPARISON_CONFIG.json |
| MSM/Handover primary recipe | PREDEFINED CONFIGURATION | no optimizer grid | 1 per family | fixed final epoch; group/sensitivity comparisons | CROSS_DATASET_COMPARISON/configs/frozen_core.json |
| Vi frozen head / F2 / gates / LR | CHECKPOINT SELECTION ONLY / PREDEFINED CONFIGURATION | V epoch only for head | one recipe | V macro AP for head; fixed other fits | VIFAILBACK/src/vifailback/training.py; fusion.py |
| Vi HGB | SYSTEMATICALLY TUNED | max_leaf_nodes7/15/31 | 3×36=108 fitted candidates | V macro AP then C calibration | VIFAILBACK/src/vifailback/baselines.py; S2_SELECTION_AND_CALIBRATION.json |
| PHM Ridge | SYSTEMATICALLY TUNED | alpha.01/.1/1/10/100 | 5×6 saved studies=30 | EXP-A MAE | src/phm2026/models/patchtst/regression.py; ridge_selection.json |
| PHM DINO scoring | LIMITED/MANUAL TUNING | 2backbones×2banks×5aggregations | 20 evaluation configs, no new gradient fits | same38 human calls reused; best biased | docs/thesis/ANOMALYDINO_SWEEP.csv; scripts/phm2026/results/anomalydino_sweep.py |


Small explicit nested grids **are systematic tuning**. No evidence was found for Optuna, GridSearchCV, RandomizedSearchCV, Ray Tune, Bayesian search, Hyperband or successive halving in the discovered research source/notebooks. Absence of an HPO framework does not negate manual grids. Exact observed selected values and every retained trial are in EFFECTIVE_CONFIGURATIONS.json; unretained original candidate weights limit exact re-inference.

Training to100 epochs is a budget change, not by itself hyperparameter optimization. Choosing an epoch is checkpoint selection. Fitting sigmoid calibration or F2 coefficients estimates model parameters and is not tuning its C unless C was compared. Repeating seeds is stability analysis. Comparing full/frozen or16/32 frames is model/protocol comparison and becomes exploratory selection if the exposed outer result drives the next experiment.

Search count is distinct from fit count: e.g.540 Section2 logs include seeds, inner candidates and final refits, not540 different hyperparameter configurations. The original Section1 and sensor-null trial expansions include19 permutation controls; they are not independent evidence of native predictive performance. PHM DINO's best-of20 and boundary variants lack fresh confirmatory held-out selection evidence.

## Evidence anchors

- [configs/reassemble/section1.json](../../../configs/reassemble/section1.json) — visual/sensor/logistic_C/selection/calibration.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — actual classifier forwards, neural_fit, logistic_fit.
- [src/reassemble/section1_features.py](../../../src/reassemble/section1_features.py) — frame pooling and normalized-progress sensor resampling.
- [runs/reassemble/20260927T154732Z-section1/training_implementation.json](../../../runs/reassemble/20260927T154732Z-section1/training_implementation.json) — recorded original implementation revision.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json) — effective shared100 horizon; head/backbone LR.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py) — all CNN stages, FrozenBN affine promotion; fixed running moments.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py) — training100/checkpoint selection/recovery.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
- [src/phm2026/models/patchtst/regression.py](../../../src/phm2026/models/patchtst/regression.py) — Ridge candidate loop.
- [docs/thesis/ANOMALYDINO_SWEEP.csv](../../../docs/thesis/ANOMALYDINO_SWEEP.csv) — all20 scoring configurations.
