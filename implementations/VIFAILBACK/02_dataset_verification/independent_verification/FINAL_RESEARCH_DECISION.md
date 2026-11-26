# Final research decision

**CONDITIONAL GO: ViFailback supports an episode-level REASSEMBLE-style visual/proprioceptive fusion study, subject to a frozen quality-controlled cohort and independent human review.** It does not establish hardware-accurate failure-onset localization or an unconditional model-ready 5,202-example cohort. The secondary candidate is NO-GO for supervised binary training under its published normal-only training/validation split.

## Answers supported by actual evidence

1. **Native outcomes:** 657 success and 4,545 failure labels agree exactly across all 109 original annotation files and the conversion. Labels are episode outcomes; sparse reference keyframes do not define a temporal failure mask.
2. **Paired modalities:** actual 20-episode tables and 60 videos pass same-ID/length/index checks. Both downloaded original HDF5 episodes exactly reproduce all three observation arrays, and 18 original-image comparisons support camera/index correspondence after lossy encoding.
3. **Visible failures:** nine of ten native failed pilot cases show clear physical evidence in the fixed samples; one drawing case is uncertain. This is a masked-key AI-assisted screen requiring an independent human review, not a measured model benefit.
4. **Independent groups:** 100 canonical task groups all contain both classes; task-disjoint nested evaluation is feasible. Session/operator/object-instance independence remains unverified. Six duplicate episode pairs must be grouped or represented once.
5. **Within-task class overlap:** all 100 task instructions have both outcomes; 104/109 source directories do. Nine task variants must remain combined.
6. **Architecture adaptation:** reuse the verified CNN feature extractor/loading/model interfaces; fit new dataset-specific visual and sensor heads and new fusion parameters. No current training, source-head reuse, weight-transfer claim or inherited F2 coefficients is justified by this audit.
7. **Fair comparisons:** paired fixed cohorts, frame/camera policy, grouped folds, initialization rules, budgets, inner selection and seeds are required; no result is predicted in advance.

## Cohort and input contract to freeze next

Prediction unit: one whole original execution; target failure=1, success=0 from the native field. Preserve all three camera perspectives for review. A prospective shared-CNN three-view variant takes **B×3 cameras×16 timestamps×3 RGB channels×H×W**, pools the sixteen frame features per view and then averages view features before a new visual head. This is 48 source images per episode, not 48 labels. Alternatively, retain the original sixteen-image architecture using a fixed primary camera and make three-view pooling a separately declared ablation; select the camera rule from training-side/pilot evidence before outer-test results exist.

Numerical input is the same episode's observed time series. There are 42 stored fields with 14 structural-zero placeholders; a source-informed candidate mask retains 14 positions, 12 joint velocities and 2 gripper effort values. Physical units are not validated. Use configurable channel identities/statistical extraction, not REASSEMBLE's channel count. Fit scaling, imputation and any learned feature selection within training partitions only. Do not use commands, `episode_index`, global/source IDs, task IDs, failure flags, avoid/correct markers, annotation text or final outcomes as ordinary predictors. Duration/frame counts can be powerful completion shortcuts; exclude them as ordinary features in the primary specification or declare a matched ablation, and do not disguise them as quality features.

Raw source count is 5,202. The validated matched input pilot is **20** executions. The conservative metadata QC proposal is **5,023** candidates (4,377 failure, 646 success) after 173 constant-position flags and six duplicate copies; this candidate cohort is not fully payload-validated. The two actual QC defects are upstream. Preserve all exclusions and decide before model work whether to quarantine all flags, repair only with original valid evidence, or study missing-state masks separately. Do not invent repaired sensor values.

External human intervention and high-level task-planning errors need explicit strata. A predeclared pose/state-only physical-failure analysis is plausible but changes the target population and prevalence. Do not silently omit difficult or nonvisible positives; report all strata and observability exclusions.

## Fair visual/sensor/fusion comparisons

| Model | Fair prospective definition |
|---|---|
| Visual only | Same fixed 16-timepoint/camera policy, verified extractor and newly trained ViFailback head; same initialization/freezing/fine-tuning rule across paired comparisons |
| Sensor only | Same execution cohort, measured observation statistics, newly fitted classifier and training-only scaling/selection |
| Averaging | Nonlearned 0.5×p_visual + 0.5×p_sensor, with the same branch calibration policy |
| F2 static fusion | Reuse the project's two-probability L2 logistic stacking definition (C=1 reference): sigmoid(b + w_v p_v + w_s p_s); refit three parameters on leakage-safe grouped OOF probabilities only |
| Quality-aware fusion | A small declared gate using target-free availability/quality indicators, the same branch predictions and training groups; no failure keyframes, labels, task ID, or test-adaptive optimization |

Existing `src/reassemble/section2_report.py` and `section2_models.py` establish the static/quality-gate interfaces read-only; nothing there was edited or executed for training. For any F2/gate selection, the probability for a training episode must come from a branch whose training, tuning and calibration exclude that episode's entire group. Hyperparameter selection for stacking/gating needs the additional nested training-only level; outer-test labels cannot fit branches, calibration, thresholds, stackers or quality weights. Refit F2 separately for each visual initialization/seed condition; never reuse REASSEMBLE coefficients.

Use identical outer task folds and inner task folds for every model, deterministic seeds such as 42/123/20261023, and a predeclared common budget/selection rule; exact assignments and budgets remain for the next reviewed protocol. Report all folds/seeds with paired task-cluster intervals. Primary failure AP must be accompanied by failure prevalence (**87.370% native**) and a constant-score baseline; also report AUROC, success-class AP, balanced accuracy, classwise recall, Brier and calibration estimates with support/limitations. Do not choose only the best seed or fold, or treat seeds as independent datasets.

Quality-awareness does not imply robustness. Corrupted/missing-modality claims require a separately authorized held-out perturbation protocol; none was run here. Strong sensors, visible failures or a flexible gate do not guarantee improved fusion.

## Full-study resource implications and stop condition

The complete converted release is **29.215 GB decimal (~27.21 GiB)**. It spans 14.41 execution-hours, with three camera streams. Full native-resolution decoded pixels would require about **230.1 GB** for three views and sixteen images/episode even as uint8; do not materialize such a cache on this workspace. Resized 224×224 uint8 three-view samples would be about **37.6 GB**, excluding video originals, models and metadata; stream/decode bounded batches instead. Compact pooled-feature/statistic caches are much smaller, but exact dimensions/cache budgets belong to implementation planning.

Only the selected source evidence and pilot were acquired. No original full HDF5 collection, full Zenodo archive, CNN extraction, GPU benchmark or model training was run. Training-time/GPU-hour estimates would be unsupported without an authorized benchmark. Full acquisition can fit only with an explicit reserve/cache/checkpoint plan and a fresh storage check, preserving at least 20 GiB; ongoing REASSEMBLE work has priority.

Stop now for independent research review of labels, QC policy, visual observations, grouping, actual measured channels and the proposed target. No full acquisition or experiment matrix starts automatically.
