# ViFailback current models and status

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

The current final core contains **4,382 episodes:3,753 failures,629 successes,99 tasks**. Historical4,384/3,755 figures are superseded. Native totals are5,202 episodes (4,545 failures,657 successes). Camera QC passed13,150 of13,152 videos, followed by two episode exclusions. The sensor cache still contains4,384 rows; models correctly join the final4,382 episode IDs. Task55 quarantine and B02 uncertainty remain documented. Whole-episode outcome classification does not establish failure-time localization or early warning; physical-session independence and hardware-clock alignment are unverified.

Task-disjoint three-outer/three-inner splits use label-blind hash ordering. T/V/C/assessment task sets are disjoint, and each meta-OOF episode is absent from its base fitting, validation and calibration partitions. Seeds are42,123,20261023. Completed work comprises **72 frozen100-epoch heads** (36 three-camera V1,36 high-only),36 LR fits,108 HGB candidate fits across36 jobs, and nine V1 fusion jobs with F2/quality/neutral gates (27 models), totaling243 fitted classifier/candidate/gate records.

**V2 full-CNN training and V3 transfer-classifier training have not executed.** Both original V1 and C100-donor V3 feature banks are complete. A cached donor representation is not a trained transfer head or a transfer fusion result.

Frozen heads use896→128 ReLU/dropout0.1→1,114,945 trainable parameters,100 cosine epochs, batch8, LR0.001, weight decay0.001, clip1, FP32. Selection is the first strict maximum of validation macro AP, followed by separate C calibration. BEST_MODEL and FINAL_EPOCH100 are retained. Sensors are28 state/velocity/gripper-effort channels at25Hz with280 statistics; they are not force/torque channels. S1=S3 is one balanced C1 logistic method, random_state42, max_iter2000. HGB usesLR0.05, max_iter200, min_samples_leaf20, l2_regularization0.1, no early stop; validation macro AP selects leaves7/15/31, then C calibrates. F2 uses training-side OOF probabilities. Quality gates use11 quality plus two availability inputs, hidden16,40 epochs, LR0.001, weight decay0.001, batch64. The neutral gate zeros quality with the same trained capacity.

Every pooled row below uses the same4,382 episodes per seed. Failure prevalence0.856458 makes failure AP alone misleading: both classes and macro AP are reported. Saved sensor predictions are deterministic across seeds. F2 macro AP is below LR macro AP in all three seeds; no new confidence interval is manufactured.

The saved Oct30 PIPELINE_STATUS says WAITING_REASSEMBLE75_COMPLETE_AND_GPU_IDLE and names controller PID290646, which was dead at initial inspection. The source gate requires the75-fit completion marker plus final-metrics hash; the approved25-fit cap does not produce it. V2/V3 are blocked by that scheduling contract, not currently progressing. The audit did not change or restart the controller.

| Model | Seed | Failure AP | Success AP | Macro AP | AUROC | F1 at0.5 | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | 123 | 0.954370 | 0.343577 | 0.648974 | 0.784370 | 0.918168 | 0.107868 |
| S2 | 123 | 0.970510 | 0.429530 | 0.700020 | 0.853756 | 0.916996 | 0.109334 |
| S3 | 20261023 | 0.954370 | 0.343577 | 0.648974 | 0.784370 | 0.918168 | 0.107868 |
| S2 | 20261023 | 0.970510 | 0.429530 | 0.700020 | 0.853756 | 0.916996 | 0.109334 |
| S3 | 42 | 0.954370 | 0.343577 | 0.648974 | 0.784370 | 0.918168 | 0.107868 |
| S2 | 42 | 0.970510 | 0.429530 | 0.700020 | 0.853756 | 0.916996 | 0.109334 |
| V1 | 123 | 0.845749 | 0.146991 | 0.496370 | 0.475157 | 0.922680 | 0.125489 |
| V1 | 20261023 | 0.839708 | 0.129067 | 0.484387 | 0.463408 | 0.922680 | 0.126591 |
| V1 | 42 | 0.853052 | 0.137260 | 0.495156 | 0.479402 | 0.922680 | 0.129213 |
| V1_high_only | 123 | 0.851883 | 0.131194 | 0.491539 | 0.456897 | 0.922680 | 0.127796 |
| V1_high_only | 20261023 | 0.849646 | 0.133288 | 0.491467 | 0.466178 | 0.922680 | 0.128678 |
| V1_high_only | 42 | 0.847815 | 0.133835 | 0.490825 | 0.459756 | 0.922680 | 0.128452 |
| F1_average | 123 | 0.933227 | 0.317011 | 0.625119 | 0.731510 | 0.922680 | 0.111606 |
| F2 | 123 | 0.943543 | 0.307257 | 0.625400 | 0.746198 | 0.922129 | 0.113445 |
| quality_gate | 123 | 0.948804 | 0.323724 | 0.636264 | 0.760464 | 0.919315 | 0.110313 |
| gate_static | 123 | 0.952706 | 0.333420 | 0.643063 | 0.773207 | 0.921808 | 0.108946 |
| F1_average | 20261023 | 0.931124 | 0.307745 | 0.619435 | 0.726439 | 0.922415 | 0.112168 |
| F2 | 20261023 | 0.940587 | 0.301547 | 0.621067 | 0.733723 | 0.922129 | 0.113740 |
| quality_gate | 20261023 | 0.950272 | 0.321449 | 0.635860 | 0.761641 | 0.919712 | 0.110474 |
| gate_static | 20261023 | 0.952475 | 0.326896 | 0.639686 | 0.770848 | 0.921921 | 0.109444 |
| F1_average | 42 | 0.931760 | 0.289037 | 0.610399 | 0.716501 | 0.922282 | 0.113196 |
| F2 | 42 | 0.945168 | 0.312405 | 0.628787 | 0.752701 | 0.922129 | 0.113107 |
| quality_gate | 42 | 0.947321 | 0.320718 | 0.634019 | 0.756404 | 0.919349 | 0.110529 |
| gate_static | 42 | 0.951757 | 0.323318 | 0.637538 | 0.769223 | 0.921692 | 0.109431 |

## Evidence anchors

- [VIFAILBACK/configs/experiment.json](../../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
- [VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json](../../../../VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json) — all12T/V/C/Ajobs and OOF coverage.
