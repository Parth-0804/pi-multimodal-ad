# Seed and fold coverage

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

| Dataset/study | Seeds actually represented | Outer/inner coverage | Inference limit |
| --- | --- | --- | --- |
| OriginalREASSEMBLE | 20260927withdeterministicoffsets; Section2threeoffsetfamilies | 5outer/4inner/nested; nullcontrols19 | notthePhase1threecanonicalseeds |
| C20 | 42only;123/20261023deferred | 25fits=5×(4inner+1outer) | onefullouterpartition, not3seedstability |
| B/C100andF2pilot | 42only | 1selectedjob;753assessment | onefold/postselected;920stackbank |
| MSM | 42/123/20261023 | 3outer/2inner,6protocols=54cases | sameheldoutIDsacrossseeds |
| Handover | 42/123/20261023 | official335/101/151;noeligibleparticipantinnerfolds | noindependentparticipantreplication |
| Vi | 42/123/20261023 | 12jobs/seed/headcondition;3outer/3inner | same4382episodes; deterministicLR/HGB |
| PHM canonical | savedrunseed/config | EXP-Btrain/Aval/Ftest | 20runsandprovisionaltarget |
| PHM SQ2/SQ3 | 1/2/3 | 3LOEO, aggregateperseed | 174callsinferred;foldnormalizationlimitation |

Per-run configurations retain actual seeds, not only seed-family names. Negative-control permutations and reused checkpoints are explicitly labeled. More files do not create independent folds. C20 has complete five-outer-fold coverage for seed42 only. The100-epoch CNN/F2 pilots each have one selected fold and seed. MSM, Handover and ViFailback repeat three seeds on shared assessment identities, so seed variation cannot be treated as independent sample uncertainty.

## Evidence anchors

- [configs/reassemble/section1.json](../../../configs/reassemble/section1.json) — visual/sensor/logistic_C/selection/calibration.
- [src/reassemble/section1_models.py](../../../src/reassemble/section1_models.py) — actual classifier forwards, neural_fit, logistic_fit.
- [src/reassemble/section1_features.py](../../../src/reassemble/section1_features.py) — frame pooling and normalized-progress sensor resampling.
- [runs/reassemble/20260927T154732Z-section1/training_implementation.json](../../../runs/reassemble/20260927T154732Z-section1/training_implementation.json) — recorded original implementation revision.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
