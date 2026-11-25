# Implement and run the visual-backbone comparison for F2 fusion

## Read this first

This is a NEW, bounded scientific implementation and execution assignment, not another general audit, literature review, UI task, or automation-framework project.

The user has selected F2 as the reference fusion formulation and wants a controlled comparison of frozen versus partially fine-tuned CNN features, using 16 versus 32 frames per completed action. Implement, test, train, evaluate, and explain that comparison within the limits below. Do not finish with only a plan when execution is possible.

Repository expected from the current project:

`/home/student/Master_Thesis_WS/pi-multimodal-ad`

Verify the working directory. Do not assume that a path in a historical report exists in the current environment.

Pasting the launch instruction for THIS file authorizes the new clean-input experiment specified here, including its bounded local training and inference. Earlier audit packets saying “no experiments authorized” describe their own historical scope; preserve them, but do not treat them as a reason to repeat the audit instead of performing this newly requested work. Follow actual governing instructions and enforced access restrictions. Do not change approval credentials or circumvent permissions.

This is not permission to restart or complete the historical discontinued Task1, or to relabel its outputs. The new study has a distinct 2-by-2 comparison, mean pooling, its own protocol, fresh fits, and new output paths. Historical Task4 corruption-aware training remains excluded, including repair, extension, and equivalent renamed work.

## 1. Exactly what to answer

Primary question:

> Under one fixed training and evaluation protocol, does adapting the final CNN stage improve held-out visual predictions and static F2 fusion compared with keeping the CNN frozen?

Secondary question:

> Does increasing the input from 16 to 32 distinct frames per completed action change visual-only or fused performance, with the other choices held fixed?

Implement exactly these conditions:

| Folder / condition | Backbone | Frames per segment |
| --- | --- | --- |
| `frozen_16_frames` | All CNN parameters frozen | 16 |
| `fine_tuned_16_frames` | Final CNN stage trainable; earlier stages frozen | 16 |
| `frozen_32_frames` | All CNN parameters frozen | 32 |
| `fine_tuned_32_frames` | Final CNN stage trainable; earlier stages frozen | 32 |

“Fine-tuned” means PARTIAL fine-tuning of the final spatial stage, retaining pretrained initialization. It does not mean full-backbone training or training from scratch. “Frames per segment” is not the optimizer batch size.

The new frozen-16 condition is the WITHIN-STUDY reference. It uses the F2 formulation, but is not assumed to reproduce historical F2 scores: this assignment specifies a new fixed-budget fitting policy with recording-disjoint holdout calibration, and 32-frame eligibility may change the common cohort. Report those differences explicitly.

This remains a completed-action outcome classification study on a previously examined dataset. Do not call it untouched confirmation, online warning, object detection, an adaptive-fusion experiment, or a robustness test.

## 2. Scope and operational limits

Authorized: targeted source inspection needed for this implementation; new source/config/tests; reading already accessible REASSEMBLE data and original pretrained weights; feature extraction; gradient checks; fitting and inference for the four conditions; saved-prediction evaluation; figures; progress/checkpoints; a final review package.

Not authorized: a new temporal transformer; RT-DETR encoder/decoder/detection-head execution; full-backbone fine-tuning; PatchTST changes; adaptive gates; corruption or missing-modality experiments; external datasets; UI development; another literature report; generic runner development; dataset/model downloads; package installation/upgrades; additional paid API/cloud services; changes to credentials or governing instructions; destructive Git operations; background schedules.

Use these proposed defaults as the task limits when this prompt is launched, unless the user's launch message explicitly replaces a limit:

- At most ONE already allocated/available local GPU and one training worker. Respect the assigned device; do not choose an unrelated busy GPU or kill other jobs.
- Maximum total wall time: 24 hours from task start, including implementation and evaluation. Finish earlier when complete. This is a ceiling, not a completion promise.
- At most 4 computational CPU threads, 2 data-loader workers, and a 32 GiB host-memory ceiling where enforceable and compatible with the allocation. Use the lower allocation limit when applicable.
- At most 30 GiB of new study storage, including checkpoints and caches. Keep at least 10 GiB of filesystem free space, or the administrator's larger required reserve.
- One fixed training seed family, base seed 42. No extra seeds or hyperparameter sweep in this task.
- At most 110 full visual-model fits including any bounded restarted fits (100 planned fits for a complete five-fold study). Count the actual cross-fitted jobs, not just the four headline conditions.
- At most two technical repair attempts per failed stage, within the same time/storage limits. A poor score is not a failure warranting repair.
- Preflight gradient/timing tests: at most 20 optimizer steps in total on disposable models and records from the first outer TRAIN partition. Never continue a scientific fit from a smoke-test model.
- No automatic extension of the time, fit, storage, or resource limits. No bypassing mandatory execution approval.

Use a deadline-aware local process with checkpoints and clean shutdown of its own child processes. Distinguish OS-enforced limits from monitored/procedural limits. If no suitable GPU or essential existing dependency/data/weight access is available, finish the implementation and feasible tests, report the precise blocker, and do not quietly substitute a very long CPU experiment or different checkpoint.

## 3. Human-readable folder and file names

Preserve the domain-first repository structure. Add the following new locations; do not reorganize existing files:

```text
src/reassemble/visual_backbone_comparison/
    __init__.py
    data.py
    visual_model.py
    training.py
    fusion.py
    evaluation.py
    experiment.py

scripts/reassemble/run_visual_backbone_comparison.py
configs/reassemble/visual_backbone_comparison.json
tests/reassemble/visual_backbone_comparison/

runs/reassemble/visual_backbone_comparison/
    README.md
    run_01/
        README_FIRST.md
        experiment_plan.md
        progress.json
        how_to_resume.md
        provenance/
        data_manifests/
        sensor_reference/
        frozen_16_frames/
        fine_tuned_16_frames/
        frozen_32_frames/
        fine_tuned_32_frames/
        shared_cache/
        comparison/
            RESULTS_SUMMARY.md
            comparison_metrics.csv
            paired_comparisons.csv
            plots/
            changed_predictions.csv
        checks/
        REVIEW_PACKAGE.zip
```

Keep equivalent new modules smaller or combine them when that genuinely reduces code. These are suggested module responsibilities, not a quota of files to generate.

Use `fold_01`, `fold_02`, etc. within condition folders, with readable deeper roles such as `fusion_training/inner_fold_01/calibration_holdout` and `outer_assessment`. Store the mapping to original zero-based split identifiers in metadata. Name checkpoint, prediction, and learning-curve files by purpose.

Do not use timestamp-only directories, unexplained experiment codes, `final_final`, `new_v3`, or architecture names that conceal what runs. Store timestamps and hashes INSIDE manifests.

If matching work already exists, inspect progress and resume only when its code, configuration, cohort, and fit identities match. Do not overwrite or auto-start a duplicate writer. A genuinely new protocol gets `run_02`, not overwritten `run_01` results. Do not increase the current task's authorized experiment count by creating extra runs.

Place all temporary outputs, generated bytecode, test caches, and study-specific caches inside the new allowed locations or a designated study temporary directory. Preserve the pre-existing dirty working tree. Do not edit old scientific modules or launchers: import pure compatible functions, or create a minimal attributed new wrapper/copy in this study. Snapshot the exact reused sources.

## 4. Short implementation check, then work

Do NOT perform the proposed A1 audit or reconstruct every historical run as a prerequisite. Spend only the source-inspection effort needed to make this NEW study correct. Aim to complete the targeted source map in 30 minutes; that is not permission to overlook a blocking data or gradient defect.

Start with the actual corresponding functions in:

- `src/reassemble/section1_features.py`: visual loading, sampled frame support, pooling, statistics.
- `src/reassemble/section1_models.py`: visual head, standardization, branch fitting/calibration, split use.
- `src/reassemble/section1b.py`: probability stacking and its nested branch inputs.
- The existing additional-improvements fine-tuning, model, and prefix-cache modules, if present.
- Actual input inventory, cohort, model/processor metadata, and saved recording-group partitions.

The uploaded reports are navigation aids, not independent verification of current code. In particular, they report an unconditionally frozen core loader and an existing partial fine-tuning path coupled to `TemporalHead`. Do not assume that changing a `frozen` config field unfreezes the executed path. Do not reuse `TemporalHead` in this study.

Record exact source paths/functions, versions, relevant hashes, current dirty source snapshots, actual checkpoint revision, processor settings, and the effective forward path in a compact provenance file. No repository-wide raw-data checksum sweep is required. Missing historical anonymous-prediction lineage is not a blocker for new fits whose sample and fit lineage is recorded from the start.

## 5. Fix the model formulation

### Visual branch

Use the same original locally available pretrained CNN backbone and feature-map selection as the traced core. Do not use previously task-fine-tuned weights as initialization. Never infer the executed architecture from a checkpoint name.

For each frame, spatially average each selected backbone feature map, concatenate the resulting vectors, and mean-pool the selected frame vectors to one segment vector. Derive and assert dimensions from the actual model, rather than hardcoding an unverified reported width.

Use the same visual head in all conditions:

`train-partition standardization -> Linear(D,128) -> ReLU -> Dropout(0.1) -> Linear(128,1)`

For a fine-tuned fit, obtain the initial standardizer from that fit's training segments using the ORIGINAL pretrained features for its frame count. Freeze those normalization statistics for the complete fit and apply them differentiably in the forward path using buffers. Do not re-estimate the standardizer on assessment data or change it after training without refitting the corresponding head. The frozen condition uses this same policy.

The gradient path must be:

`loss -> visual head -> fixed affine standardization -> mean pooling -> selected live backbone feature maps -> trainable final CNN stage`.

No detached cached segment embeddings, NumPy conversion, `no_grad`, or `inference_mode` may break the live final-stage path. Frozen-prefix computation can use an appropriate no-gradient path, with outputs suitable as inputs to the subsequent differentiable computation.

Keep all backbone BatchNorm running statistics fixed in evaluation mode, including in the trainable stage. Final-stage affine parameters may train when they belong to that stage; earlier affine parameters remain frozen. Keep the visual head's dropout in training mode only during fitting. Recheck these settings after calls to `train()`.

No new augmentation or information source: same deterministic processor, resize policy, full-interval support, spatial pooling, and head across conditions. No boundary-only pooling, attention, action one-hot appended to the visual vector, or head-capacity change.

### Sensor branch

Keep the core sensor-statistics representation and logistic classifier family, with fit-local standardization and calibration. Do not concatenate raw image features into the sensor predictor.

For this new fixed-budget study, use `LogisticRegression(C=1.0, class_weight='balanced', max_iter=2000, random_state=42)` for the raw sensor classifier, or the equivalent installed implementation. The C value is deliberately fixed, not independently retuned for each visual condition. A convergence problem is a technical issue to record; do not silently change the model.

Fit sensor components once per exact training/calibration partition and reuse their keyed predictions across all four visual conditions. Historical anonymous banks cannot substitute for newly identified branch predictions. Pure label-independent raw statistics can be reused only when sample identity, extraction settings, and inputs are established; scalers and fitted predictors remain partition-specific.

### F2 fusion

Use calibrated failure probabilities from the two branches, not embeddings or raw logits:

`p_fused = sigmoid(intercept + coefficient_visual*p_visual + coefficient_sensor*p_sensor)`.

Fit an unweighted logistic stacker with intercept, C=1.0, no feature scaling, and no subsequent fusion calibrator. Coefficients need not be positive or sum to one. They are not causal percentage contributions.

Refit the stacker for each condition and outer fold using properly out-of-fold branch probabilities. Do not freeze historical F2 coefficients when changing the visual branch. This task fine-tunes vision on its own branch loss; it does not jointly backpropagate the fusion loss through the backbone.

## 6. Cohort, frame sampling, and sample identity

Use the existing native completed-action task and original recording-group split assignments, not a frame-level random split. Validate the current recording+segment identity, annotation-derived failure target, interval boundaries, and input availability directly enough to generate a new keyed cohort manifest. Report missing records rather than inventing labels or forcing historical counts.

For a clean 16-versus-32 comparison, the PRIMARY study cohort consists of the otherwise eligible segments with at least 32 distinct decodable, in-interval frames in the selected camera. Establish that common cohort before fitting or examining new model scores. All conditions and the sensor reference use exactly these rows.

Report exclusions and class/recording counts before and after this rule, by saved outer fold. This is a population restriction, not a harmless implementation detail. The new reference may differ from historical F2 for this reason. Never choose an eligibility rule to improve scores. If existing partitions become infeasible (e.g. a necessary training/calibration partition has only one class), report the specific blocker rather than silently generating a more favorable split.

For each eligible segment:

1. Preserve the source-defined deterministic 16-frame selection when it is valid and unique.
2. Construct the 32-frame selection as a deterministic SUPERSET of those 16, adding distinct in-interval frames to fill the largest remaining temporal gaps. Define tie-breaking and end-gap handling explicitly, without outcome labels. Preserve chronological order.
3. Save both index/timestamp lists and their relation in the manifest. Test that 16 indices are a subset of 32 and that both satisfy interval boundaries.

This tests adding observations to the same full interval; it does not simultaneously introduce a different action boundary or 32 repeated copies. Do not drop only difficult 32-frame cases after seeing predictions. Detect decoding failures before cohort lock where feasible; a later unresolved failure makes dependent comparisons incomplete rather than authorizing selective deletion.

Reuse saved outer folds (expected five) and inner recording-group folds (expected four), restricting membership to the new common cohort without changing recording assignments. Verify the actual files. Unexpected partition structure is a targeted issue, not a reason to invent claimed five-fold evaluation.

## 7. Fixed training settings for the first study

Record these as PROPOSED SETTINGS ACCEPTED BY LAUNCHING THIS ASSIGNMENT, not previously optimized or historical defaults:

- Original pretrained initialization for every independently fitted visual model.
- Exactly 5 epochs per full visual fit. Final-epoch weights; no performance-based early stopping, epoch extension, or learning-rate search.
- AdamW, visual-head learning rate `1e-3`, trainable final-stage learning rate `1e-5`, weight decay `1e-3`, gradient-norm clipping `1.0`.
- Positive-weighted binary cross-entropy from logits; the positive weight is negatives/positives in the EXACT gradient-training subset only.
- Effective optimizer batch: 8 SEGMENTS across all four conditions. Choose a common feasible microbatch before evaluation; use gradient accumulation to preserve that effective batch, with correct loss normalization for partial final batches. Segment count and frame count are separate configuration keys.
- Select one consistent precision policy using training-only preflight: float32 by default; bfloat16 autocast is permitted if supported and finite forward/backward checks pass for all four conditions. Record the chosen policy before fitting. No condition-specific precision shortcut.
- Same seed family and deterministic training-segment ordering for matched fits. Derive seeds from stable partition roles, not from Python's process-random hash. Reinitialize all model/optimizer/normalizer state independently between fits; never warm-start across folds or conditions.
- Calibration: an unweighted sigmoid logistic calibrator, C=1.0, fit only on a recording-disjoint calibration holdout excluded from that raw model's gradient training, as detailed below.
- Thresholded secondary metrics use a predeclared probability threshold of 0.5 for each calibrated branch and F2. Do not optimize it on assessment data. This is an intentional new-study difference from historical trained thresholds; AP is the primary metric and does not depend on this threshold.

At 32 frames, the number of frame evaluations per optimizer step increases. Equal epochs/segment batches do not make compute equal; measure the cost rather than claiming matched computation or optimal tuning.

Write `experiment_plan.md` and the resolved config before any assessment predictions are scored. Do not change scientific settings after inspecting new assessment results. Record a protocol revision and affected invalidated fits if an actual implementation defect requires correction; do not pool incompatible versions.

## 8. Cross-fitting with bounded, recording-disjoint calibration

Implement genuine recording-group out-of-fold branch probabilities. Ordinary row-wise stacking defaults are not sufficient. Globally fine-tuning the backbone before cross-validation is prohibited.

IMPORTANT NEW-STUDY DESIGN CHOICE: To keep this first comparison computationally manageable, use a fixed calibration holdout inside each branch's allowed training partition rather than repeating a deep nested hyperparameter/calibration search. This means raw branches do NOT train on all records allowed to the full calibrated branch. It is a deliberate fitting-protocol change, shared by all four conditions; preserve the F2 formulation but do not call this exact historical F2 reproduction.

Define `fit_calibrated_branch(A)` for an allowed set of records A:

1. Make one deterministic recording-group holdout: approximately 20% of RECORDINGS in A are calibration records C; the rest are gradient/raw-model training records G. Use `GroupShuffleSplit(n_splits=1, test_size=0.20)` or an equivalent deterministic grouping implementation with a role-derived fixed seed. The same G/C roles apply to both modalities and all four conditions for this A.
2. Save the split before fitting. Verify recording disjointness, class support, and coverage. Do not repeatedly redraw until finding favorable performance or quietly convert a class-degenerate split into a random row split. A class-support failure is an explicit protocol blocker.
3. Fit the raw visual model on G only, with its standardizer and positive class weight from G only. Start from original pretrained weights. Fit the sensor raw classifier and scaler on G only, and reuse their identified result across visual conditions.
4. Predict RAW logits on C. Fit each branch's unweighted sigmoid logistic calibrator on those logits and C labels. C is an actual raw-model holdout, not in-sample logits from a model trained on C.
5. Return the G-trained raw model plus its C-fitted calibrator. Do NOT then refit the raw model on G union C while retaining the old calibrator. Keep each predictor paired with the specific raw model that produced its calibration logits.

For each original outer fold, let T be outer-training records and E outer-assessment records:

A. For each original inner held-out recording fold V within T, call `fit_calibrated_branch(T minus V)` for vision and sensors. Predict V. V's labels and recordings must be absent from G, C, normalization, gradient training, and calibration. Pool these held-inner calibrated probabilities to create F2 training features for all T. There must be exactly one such prediction per T sample.

B. Fit the unweighted F2 logistic stacker on these two-column out-of-fold probabilities and T labels.

C. Call `fit_calibrated_branch(T)` using its own predeclared G/C split for the final outer visual and sensor predictors. Predict E with those calibrated branches and the stacker from B. E never enters any fitting, normalization, calibration, frame-rule decision, or training/stopping selection.

D. Save E predictions with direct sample keys, explicit G/C/T/E memberships and producing fit identities. Save corresponding inner predictions for traceability, without calling the stacker's own fitted training outputs independent performance.

This procedure has FOUR inner raw visual fits plus ONE final outer raw visual fit per condition per outer fold. With five outer folds and four conditions, that is 100 planned full visual fits, not four jobs. The sensor procedure has 25 corresponding raw fits, reused across conditions. Verify and save the actual job graph before training.

The inner and outer raw predictors have different training-set sizes, as in cross-fitted stacking; record the sizes. The calibration holdout further reduces raw-model training data, which must be included in limitations. The goal here is a matched first comparison within the budget, not an optimally tuned historical reproduction.

No hyperparameter search or calibration-subfold model training is additionally authorized. Reuse only exact per-partition results within this new study when input, G/C memberships, initialization, preprocessing, and config identities match. Never reuse a task-trained visual model across folds, frame counts, or trainable-weight policies. A shared original pretrained or wholly frozen-prefix cache is different from a shared task-trained feature cache.

## 9. Implementation tests and efficient execution

Integrate these checks into the task rather than creating a separate audit campaign:

- Frozen condition: after a disposable training step, no backbone parameters or BatchNorm buffers change; the visual head receives gradients and updates.
- Fine-tuned condition: the named final stage has nonzero finite gradients and an observed parameter change; earlier weights and all frozen BatchNorm running statistics remain unchanged. Merely listing `requires_grad=True` is insufficient.
- Hooks or an equivalent trace confirm this caller uses the CNN and not a temporal transformer or detector encoder/decoder. Verify the actual final-stage name from the model object.
- Dynamic feature dimensions, pooling, normalization, sigmoid inputs, probability range, and F2 formula are correct.
- 16/32 sample pairing, nesting of frame selections, recording-group exclusion, and fit-local calibration/normalization pass.
- An input-label sentinel test demonstrates that held-out labels cannot enter fitting helpers. Record membership checks for every real fit as well; a synthetic test alone does not validate actual partitions.
- Newly saved predictions can be recomputed from a small held-out sample set and its saved model/normalizer/calibrator/stacker within a declared numerical tolerance. Do not choose tolerance after inspecting discrepancies; default probability tolerance 1e-5 for float32 and 1e-3 for bfloat16, with stricter identical-path checks where suitable.
- Reload/checkpoint/resume retains the required model, optimizer, random generator, epoch, data order, and precision state. Do not call a partial restarted fit complete.

Efficiency is allowed when scientifically equivalent:

- Cache deterministic frozen per-frame pooled features for frozen models; fit their normalization and heads locally to each partition.
- A frozen spatial-prefix cache for fine-tuning is optional. Use it only after full-forward versus cached-prefix output AND final-stage-gradient agreement on training-only examples. Do not reuse whole segment embeddings for live final-stage training.
- Estimate prefix-cache size before building it. Use a bounded cache or recomputation if the full cache exceeds the storage budget; do not materialize a huge feature tensor hoping it fits.
- Save shared original weights once and store compact trainable-stage/head state plus a reconstruction manifest, provided small saved-model reload tests pass. Keep prediction-producing checkpoints and scalar fitting state sufficient for replay; do not retain unnecessary optimizer copies after completed fits.

Before the expensive loop, estimate time, peak memory, storage, and total fits using the training-only timing check. Write actual estimates and uncertainty. Do not change epochs, cross-fitting, calibration holds, samples, or method in order to squeeze the complete study into the cap.

Execution schedule: complete all four conditions for the FIRST existing outer fold, then the next fold, and so on. This is a predeclared compute-bounded schedule, not a method chosen after viewing AP. Reuse the sensor fit results for that fold. Never finish all five frozen folds first and leave both fine-tuned conditions unattempted.

If the full matrix will not fit, proceed through the authorized paired-fold schedule only while time/resources suffice. Reserve time to save and summarize. Compare only the identical COMPLETED outer folds/rows shared by all required conditions, prominently label those results PARTIAL, and state coverage. A single-fold result is a pilot, not completed five-fold evaluation. Do not launch another block that cannot reasonably finish before the deadline. Partial unpaired predictions may be saved but cannot support a four-condition ranking.

Stop for actual data/partition/gradient failures or budget limits. A lower AP is a valid result and does not authorize new trials. When the time cap is reached, checkpoint and stop; provide the exact resume command rather than silently scheduling a continuation.

## 10. Evaluation and explanation

The primary outcome is failure-class average precision using the installed, recorded `average_precision_score` definition, not trapezoidal area under a precision-recall curve. Report visual-only, sensor-only, and F2 results for each condition on the same assessment rows.

Save both per-outer-fold metrics and pooled out-of-fold metrics. Distinguish pooled AP from the mean of fold APs. Include failure count, sample count, recording count, completed folds, base seed, and the random-ranking prevalence reference.

Primary contrast:

`F2(fine_tuned_16_frames) - F2(frozen_16_frames)`.

Secondary contrasts:

- `F2(frozen_32_frames) - F2(frozen_16_frames)`.
- `F2(fine_tuned_32_frames) - F2(fine_tuned_16_frames)`.
- Descriptive interaction: `(fine_tuned_32 - frozen_32) - (fine_tuned_16 - frozen_16)`.

Also report the analogous visual-only differences and each condition's F2-minus-sensor AP. Interpret visual improvement and fusion improvement separately. No invented minimally important improvement threshold or automatic “winner” declaration.

Use 2,000 paired recording-cluster bootstrap resamples with fixed evaluation seed 314159, reusing the same sampled recording multiplicities across compared methods. Keep all segment rows within each sampled recording, including multiplicity. Record discarded/undefined resamples and how many valid replicates remain. Report 95% percentile intervals as descriptive sampling uncertainty conditional on these fits, exposed data, and recorded grouping. This is NOT repeated-training uncertainty or proof of population-wide generalization. Secondary intervals are unadjusted/exploratory; avoid a set of unsupported significance claims.

Secondary metrics: AUROC where defined, failure precision/recall, balanced accuracy, macro F1, Brier score, and clearly defined reliability plots at the locked threshold policy. Include actual training loss trajectories, trainable/total parameters, optimizer updates, training wall/GPU time, peak memory, and measured inference timing under a stated hardware/batching protocol. Separate feature extraction, training, and inference costs; no real-time claim.

Explain 12 deterministic changed-prediction examples: three largest fine-tuning improvements and three largest deteriorations within each ground-truth class, using reduction/increase in true-class log loss versus frozen-16 on common assessment rows; handle ties by sample key and report overlap/insufficient cases. These are deliberately selected illustrations, not independent statistical evidence. Save actual IDs, action/interval, truth, both branch probabilities, F2 probability, fold, and frame lists. Contact sheets from real selected frames are optional local explanatory artifacts; do not invent samples, attention maps, or “causal contribution” images.

Required conclusions:

- Did partial adaptation help the visual predictor under this fixed budget?
- Did it help F2 beyond the unchanged sensor method?
- Did 32 observations help in frozen and adapted conditions?
- What did the extra computation cost?
- Are results complete, partial, negative, or inconclusive?
- What ONE later question is best motivated? Do not execute it.

Do not train a final model on all assessment records or deploy a selected winner in this task. Keep the outer models for correctly held-out later comparisons. Choosing a next variant from these exposed results remains exploratory.

## 11. Artifacts that must make the results reviewable

Create useful files, not a target count of deliverables. At minimum include:

- `README_FIRST.md`: completed/partial/blocked status and direct links to results, limitations, and resume instructions.
- `experiment_plan.md` plus resolved config and provenance: actual model/stage/head/processor, differences from historical F2, fixed settings, partitions, exposure status, resource caps, source snapshots, and commands.
- `data_manifests/`: keyed common cohort, exclusions, 16/32 frame selections, exact outer/inner fold and calibration-holdout memberships, and a fit-lineage index. Include recording and segment IDs in the SAVED predictions themselves, not only in an ordering assumption.
- Per-condition/per-fold results: keyed raw logits, calibrated visual and sensor probabilities, F2 probability, threshold and decisions, true labels, fit/model/config IDs, learning curves, parameters, calibrator/stacker coefficients, checkpoint references, and cost observations.
- `comparison/RESULTS_SUMMARY.md`, `comparison_metrics.csv`, `paired_comparisons.csv`, actual plots, and `changed_predictions.csv`.
- `checks/`: actual gradient/weight/BatchNorm observations, partition and sampling checks, saved-model replay results, test commands/outputs, and scoped original-file preservation checks. Distinguish static reads, synthetic tests, dynamic checks, and real fits.
- `progress.json` and `how_to_resume.md`: completed jobs, unsuccessful attempts, active/blocked job, elapsed time, remaining caps, and exact supported resume command. Resume must not rescore/retrain completed work silently.
- A concise code-and-concept walkthrough inside the results summary: Input -> Representation -> Training -> Branch predictions -> F2 -> Evaluation -> Conclusions.

Produce `REVIEW_PACKAGE.zip` with the small relevant NEW source/tests/config, summaries, cohort/frame/fit manifests, directly keyed OUTER assessment predictions, learning curves, numerical tables, test evidence, and a size/hash manifest. Exclude raw videos, original datasets, large intermediate caches, model-weight blobs, credentials, and unrelated historical artifacts. Include local paths and hashes for excluded weights. This review package must allow an independent reader to recompute reported outer prediction metrics; do not omit the small keyed prediction tables as the previous review package did.

Keep native data and packages local; do not upload the ZIP or any private material automatically. Hash the finalized payloads and validate archive contents after generation.

## 12. Final working and reporting behavior

Use simple study-specific Python entry points for prepare/train/evaluate/status/resume rather than extending the old generic synthetic runner. Implement only commands that actually work and list their real invocations in the README. A status command should inspect state; it must not accidentally start training.

Proceed from implementation checks to the authorized scientific jobs without a new general audit/approval loop. Interrupt only for a genuine prerequisite outside this scope, a validity defect, incompatible governing restriction, or an exhausted limit.

A separate read-focused reviewer may examine code and keyed outputs if it is actually available within existing permissions and usage; do not purchase/launch extra model-backed services. Lack of such a reviewer does not block this exploratory task: explicitly label self-review, run the concrete tests, and leave independent review outstanding. A model's completion message is not scientific verification.

At completion or safe stop, return:

1. Paths to `README_FIRST.md`, `comparison/RESULTS_SUMMARY.md`, and `REVIEW_PACKAGE.zip`.
2. A four-row table of visual AP, sensor AP, F2 AP, and coverage, with missing cells marked NOT_RUN/INCOMPLETE rather than estimated.
3. The exact final-stage parameters trained and whether gradient/weight changes were observed.
4. Whether all five folds finished; exact unresolved blockers and resume instructions otherwise.
5. One bounded next recommendation, with no automatic follow-up execution.

End with a brief evidence checkpoint: sources/code and actual executions checked; uncertainties; strongest defensible conclusion.

A valid negative result completes a valid experiment. An invalid comparison with a higher score does not.

## Reference basis for the prompt author (not a new literature assignment)

This assignment was prepared using the user's supplied decision/audit packets and these selected files from `SHAREABLE_REVIEW_PACKET.zip`: `01_evidence/IMPLEMENTATION_AND_STUDY_STATUS.md`, `04_decisions/EXPERIMENT_CARDS.md`, and `04_decisions/PRIORITIZED_ROADMAP.md`. Their reported historical implementation must still be checked locally for this new task. Their old deferral recommendations are not the current assignment.

General implementation guidance checked by the prompt author:

- PyTorch, Transfer Learning for Computer Vision Tutorial: https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
- PyTorch, Autograd mechanics (freezing, gradient modes, and evaluation mode): https://docs.pytorch.org/docs/stable/notes/autograd.html
- scikit-learn, StackingClassifier (out-of-fold stacking and the prefit overfitting warning): https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html

The numerical training/resource choices here are proposed bounded study settings, not optimality claims derived from those references. No scientific run was performed by the prompt author when creating this document.
