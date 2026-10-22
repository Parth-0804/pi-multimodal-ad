# Run the RT-DETR encoder comparison

## Assignment and authorization

Implement and execute the next REASSEMBLE experiment. This is a scientific implementation, feature-extraction, classifier-training, and evaluation task, not another general audit, literature review, UI task, or automation-framework project.

Expected repository:

`/home/student/Master_Thesis_WS/pi-multimodal-ad`

Verify the actual working directory. Keep ALL new experiment code, configuration, tests, caches, logs, predictions, and reports inside:

`00_experiments/rt_detr_encoder_comparison/`

Launching this assignment authorizes the bounded two-condition, clean-input experiment below. Earlier packets describe their own audit-only permissions; they are not a reason to stop this newly authorized work at another planning handoff. Respect governing instructions, administrator restrictions, and actual execution approvals. Do not edit credentials, governing instructions, or approval mechanisms.

The preceding frozen/fine-tuned, 16/32-frame study has priority. You may prepare isolated code and lightweight CPU tests while it is running, but do not launch competing GPU work, alter its files, or select settings based on its scores. Start this study's GPU extraction and fitting only after the preceding job is no longer using the allocated device and the necessary input manifests are stable. Do not kill or pause another process.

## 1. The experiment: exactly two conditions

Primary question:

> Does adding the pretrained RT-DETR hybrid encoder to frozen CNN feature extraction improve held-out F2 fusion under an otherwise matched classification protocol?

Secondary questions: does visual-only prediction improve, and what additional compute and representation/head capacity does the change require?

| Condition folder | Executed visual extractor | Trainable visual components | Frames per completed action |
| --- | --- | --- | --- |
| `cnn_only` | Original pretrained CNN backbone | Separate visual classification head only | 16 |
| `cnn_plus_encoder` | Same CNN, required pretrained encoder input projections, and pretrained hybrid encoder | Separate visual classification head only | 16 |

Freeze ALL pretrained feature-extractor parameters in both conditions, including projection layers and the hybrid encoder. Freeze their running statistics and disable their training-time dropout. Train the visual head, sensor classifier, branch calibrators, and F2 stacker on their permitted partitions.

Use the same 16 actual frames for each segment in both conditions. Do not select 32 frames or the best fine-tuning variant after observing the previous study. Do not introduce temporal attention: every image is encoded independently, followed by averaging across frames.

No detector decoder, query initialization/selection, proposal-ranking heads, detection class/box heads, detection loss, box predictions, or postprocessing may execute. Instantiating a detector wrapper to load the original pretrained checkpoint is permitted; forwarding the full detector and discarding its detections is NOT the requested extraction path.

This tests a hybrid-encoder representation pipeline, including its projections, attention, and cross-scale processing. It does not isolate the causal benefit of attention alone, perfectly match model capacity, test adaptive fusion, establish robustness, or demonstrate real-time operation. Do not call the branch the full RT-DETR detector or a temporal video transformer.

## 2. Human-readable folders

Create or resume this structure without moving existing work:

```text
00_experiments/
  rt_detr_encoder_comparison/
    Run_Encoder_Comparison.md
    README.md
    config.json
    run_experiment.py
    code/
    tests/
    results/
      run_01/
        README_FIRST.md
        experiment_plan.md
        resolved_config.json
        progress.json
        how_to_resume.md
        data/
        sensor_reference/
        cnn_only/
        cnn_plus_encoder/
        comparison/
          RESULTS_SUMMARY.md
          metrics.csv
          paired_comparisons.csv
          changed_predictions.csv
          plots/
        checks/
        provenance/
        cache/
        logs/
        REVIEW_PACKAGE.zip
```

Within condition folders use `fold_01`, `fold_02`, etc., and readable fit roles such as `fusion_training/inner_fold_01` and `outer_assessment`. Record mappings to original split IDs in manifests. Use purpose-based filenames, not timestamps, hash-only directories, unexplained task codes, or `final_final` variants. Timestamps and hashes belong inside metadata.

The tree describes responsibilities, not a required file count. Use a small number of clear modules such as `features.py`, `fitting.py`, `data.py`, and `evaluation.py` where useful. Do not build a general orchestration platform.

If matching work already exists, resume only after code/config/input/fit identity checks. Use `run_02` only for a genuinely different, explicitly justified protocol revision, never to overwrite results or expand the authorized trial budget. Keep incomplete/invalidated runs visible.

Do not create new files in `src/`, `scripts/`, `configs/`, `runs/`, or the earlier bootstrap/audit directories. Import compatible stable helpers read-only or make small attributed snapshots inside this experiment. Do not edit old scientific code. Redirect bytecode, test caches, temporary files, and study caches into the experiment folder. Existing raw data and original model caches remain read-only and are not copied wholesale.

## 3. Resource limits and handling the running study

Use these bounded defaults when this prompt is launched, unless the user's launch explicitly changes a limit:

- One already allocated local GPU, one scientific worker, no new hardware/cloud/API purchases.
- At most 24 hours from this task's start, including preparation, waiting, tests, extraction, fitting, and reporting. Finish sooner when complete.
- At most 4 computational CPU threads, 2 data-loader workers, and 32 GiB host RAM where enforceable, or the lower allocation limit. While the preceding experiment is active, restrict preparation to lightweight work with at most 2 CPU threads.
- At most 30 GiB of new study storage; retain at least 10 GiB filesystem free space or the administrator's larger reserve. Estimate cache and archive sizes first.
- One seed family, base seed 42; no sweeps or extra seeds.
- At most 55 full visual-head fits INCLUDING restarted fits. The planned maximum is 50 fits: 2 conditions x 5 outer folds x (4 inner fits + 1 outer fit). Exact compatible reuse reduces new fitting.
- At most 30 raw sensor fits including retries, normally 25 shared fits; at most 12 F2 stacker fits including retries, normally 10. Record separate calibrator counts.
- At most two technical repair attempts per failed stage, within all other caps. A low score is not grounds for a repair or extra trial.
- Disposable preflight: at most 20 head-optimizer steps and at most 32 distinct action segments from the first outer TRAIN partition. Do not warm-start scientific fits from smoke-test models.

No dataset/model downloads, package installations/upgrades, external data acquisition, paid model/API worker launches, new service, or scheduled/background continuation. Do not expand historical Task4 or restart discontinued Task1 under a new name. This is the newly authorized frozen spatial-encoder comparison only.

Inspect known progress/lock files and actual process/device state before expensive work. A low GPU-utilization snapshot is not proof that the preceding job has ended. Use process identity and ownership where accessible; uncertainty about safe allocation blocks GPU work. Do not select an unrelated busy GPU.

A low-frequency foreground wait inside this task is permitted while an identified preceding job finishes, bounded by the same 24-hour deadline. Save readiness and progress during waiting. If this environment cannot sustain the wait, or the deadline approaches, finish implementation/tests, write `WAITING_FOR_GPU` or `WAITING_FOR_INPUT_MANIFEST`, and provide the exact resume command. Do not claim execution has been queued when no process exists, and do not install a scheduler.

Record which limits are technically enforced versus monitored. Stop only this task's own children at its deadline. If GPU, existing weights, or essential packages are unavailable, complete feasible implementation/tests and report the concrete blocker; do not silently switch to a long CPU experiment or substitute another model.

## 4. A targeted source check, not another audit campaign

Read the prior `Run_Visual_Backbone_Comparison.md` when available and locate its actual study code, resolved config, cohort/frame/split manifests, progress, and `frozen_16_frames` artifacts. Expected locations include `runs/reassemble/visual_backbone_comparison/` and `src/reassemble/visual_backbone_comparison/`; verify rather than invent paths. If more than one incompatible study is present, do not choose by performance.

Use the supplied audit/decision records only to locate relevant functions, including the core feature loader, visual head, sensor statistics, branch calibration, and F2 stacker. Inspect the installed RT-DETR library source for its real backbone-to-encoder call path and output structure. No need to repair anonymous historical banks or reproduce unrelated historical studies before making new keyed fits.

Create a compact source/version record with actual function names, local paths, relevant hashes, processor/checkpoint identities, and inherited protocol details. Aim to finish this targeted mapping promptly and proceed to implementation; do not produce another broad four-eyes report as the main deliverable.

Snapshot any shared helper before importing it if its source might still be edited by the preceding job. Verify its identity before reuse. Preserve pre-existing dirty-tree changes. Other ongoing processes may legitimately change their outputs: distinguish observed external changes from this task's own writes and do not claim repository-wide preservation without evidence.

## 5. Lock the cohort, frames, and partitions

Preferred basis: the stable locked manifests from the preceding visual-backbone comparison. Reuse its COMMON cohort, including its at-least-32-distinct-usable-frames eligibility restriction, even though this study uses only 16 frames. This keeps the reference population unchanged. Do not silently expand the cohort to all 16-frame-eligible actions.

Use native completed-action labels with the established success-to-failure mapping, the same hand-camera stream, complete action intervals, original recording-group outer/inner splits, and EXACT saved 16-frame index/timestamp lists. Record exclusions and sample/failure/recording counts per fold. Do not fabricate counts or identify anonymous predictions just by matching labels and fold numbers.

Required keys are at least `(recording_id, segment_id)`, with preserved identifier types, action/interval metadata, label, frame list, original fold ID, and fit role. If a segment ID is only unique within a recording, never join on segment ID alone.

Pin exact gradient-training/calibration memberships from the preceding study when they exist and match the specified protocol. Their membership, not a guessed seed, establishes comparability.

If that study has not yet produced stable manifests, prepare the new code/tests and wait within the task budget. If it is absent or stopped before producing them, do not silently invent a replacement population/split and call it the agreed follow-up. State the missing prerequisite and provide a ready-to-resume implementation. Missing historical metrics are NOT a blocker when the new cohort and fit design are established.

Any later decoding error or missing row is a reported failure; do not selectively drop it after observing predictions. An unresolved loss of shared rows makes the dependent paired comparison incomplete.

## 6. Implement the actual feature extractors

### Load the ORIGINAL pretrained state

Use the same original, locally available RT-DETR checkpoint revision and processor as the preceding frozen-16 reference, not the fine-tuned checkpoint or latest online revision. A reported locator such as `PekingU/rtdetr_r18vd` is not sufficient identity. Record the actual local revision, weight/config hashes, processor parameters, relevant library versions, and loading diagnostics.

Confirm pretrained weights are present for the CNN, encoder input projections, and ALL executed hybrid-encoder components. Fail for missing, shape-mismatched, or randomly initialized used components. Do not set `ignore_mismatched_sizes` or construct an untrained encoder from config as a substitute. Explain unused detector-head keys separately from missing used keys. Keep model loading local-only.

### `cnn_only`

Call the same pretrained backbone feature-map stages as the preceding frozen-16 condition. Spatially average each selected feature map, concatenate scale vectors in the recorded stage order, and mean-pool the 16 frame vectors into one segment vector. Do not add encoder input projections to this reference branch.

### `cnn_plus_encoder`

Follow the installed model's native prefix exactly:

`processed image -> same backbone maps -> required pretrained encoder input projections -> hybrid encoder -> final multiscale encoder feature maps`

Honor the native scale order, stride definitions, spatial positions, masks, projection normalization, and evaluation settings. Some required projections live outside the encoder object; selecting `.encoder` alone is not necessarily the complete pretrained prefix. Inspect the installed implementation rather than guess its attributes.

Extract the final cross-scale-fused maps immediately after the hybrid encoder and before decoder-side projections, proposal scoring/selection, and decoder work. Spatially average EACH output map separately, concatenate those scale vectors in the native output order, then mean-pool the 16 frame vectors. Do not average all flattened multiscale tokens indiscriminately: that changes scale weighting. If the installed output is flattened, recover per-scale boundaries from verified shape metadata; do not guess them.

Do not use decoder `last_hidden_state`, detection logits, predicted boxes, or output-key names as evidence that you captured encoder maps. Assert actual tensor shapes and module provenance. Do not hardcode the previously reported backbone dimension or an assumed encoder dimension.

Keep frames as independent image-batch elements. No frame positional embeddings, cross-frame attention, temporal head, action input appended to vision, boundary-only pooling, image augmentation, resolution changes, or label-guided frame selection.

### Frozen state and feature caching

All executed pretrained components remain `requires_grad=False` and in evaluation mode. Keep BatchNorm buffers unchanged, including encoder projections/cross-scale convolution layers. Setting a parent classifier to training mode must not turn the frozen extractor back to training mode. Only the head uses training dropout.

Use identical preprocessing and an agreed precision policy for both conditions. Frozen feature extraction may run under a no-gradient/inference context, but cached outputs must be ordinary tensors/arrays usable by autograd when fitting the separate head.

Because the extractors are fixed original pretrained functions without label-fitted statistics, their deterministic pooled features may be cached once across folds. All standardization and supervised fitting remain partition-specific. Record this distinction explicitly. Stream and pool maps immediately; do not cache every full-resolution multiscale tensor across the dataset. Cache compact segment vectors, or compact per-frame vectors only when justified within storage limits.

Cache keys must bind extractor identity, checkpoint, processor, frame list, sample IDs, precision, pooling, and output dimension. Never reuse task-fine-tuned representations across folds. Verify live-versus-cached agreement on training-only examples before relying on a cache.

The head is the same FAMILY in both conditions:

`fit-local standardization -> Linear(D,128) -> ReLU -> Dropout(0.1) -> Linear(128,1)`

D may differ between conditions. Preserve 128 hidden units and dropout, report the actual dimensions and trainable parameters, and do not call this exactly capacity-matched. Do not introduce PCA, random projection, extra layers, or attention-specific ablations in this task.

## 7. Fitting policy: keep F2, not historical coefficients

The intended policy matches the preceding study's fixed-budget design:

- Five epochs per visual-head fit, final-epoch weights, no score-based early stopping or extra epochs.
- AdamW head learning rate 0.001, weight decay 0.001, gradient clipping 1.0.
- Effective training batch of 8 ACTION SEGMENTS, not 8 frames. Use the same ordering/accumulation policy for the two conditions; final partial batches must be normalized correctly.
- Positive-weighted binary cross-entropy from logits; negatives/positives computed only on that fit's raw training subset.
- Base seed 42 with recorded stable role-derived seeds. Independent model/optimizer/scaler state for each fit; no warm starts across folds or conditions. Use a separate deterministic data-order generator so different head dimensions do not accidentally change segment order.
- Use the preceding matched reference's recorded precision policy where compatible: float32 or preflight-validated bfloat16. Apply the SAME chosen policy to both new branches. If compatibility requires a different numerical policy, refit the CNN reference too and disclose the change rather than reuse incompatible predictions. No mixed-policy primary comparison.
- Raw sensor method: the same sensor statistics and fit-local standardizer; logistic regression C=1, balanced class weights, max_iter=2000, random_state=42.
- Branch calibration: unweighted sigmoid logistic regression, C=1, on a recording-disjoint holdout excluded from the associated raw model's training.
- F2: unweighted logistic regression, C=1, intercept, inputs `[p_visual, p_sensor]`, no feature scaling and no extra fused calibrator.
- Thresholded metrics use probability 0.5, fixed before assessment. No threshold tuning on assessment outcomes.

F2 is:

`p_fused = sigmoid(b + w_visual*p_visual + w_sensor*p_sensor)`.

Its learned coefficients are shared across samples; this is static probability stacking, not an adaptive gate or a normalized average. Refit F2 per representation and outer fold. Do not reuse a stacker trained on a different visual branch. No fusion-loss backpropagation through the frozen extractors.

Fit the standardizer on each raw training subset only. The same standardization PROCEDURE applies to both representations, not numerically identical means/stds for different features. Preserve the preceding study's documented missing/near-zero-scale handling. Sensor statistics and calibrated sensor predictions must be identical across the two visual conditions for identical fit roles.

Confirm the preceding study's actual protocol against these settings before reusing artifacts. Do not silently inherit an undocumented scientific departure. If incompatible artifacts are the only issue, train both conditions afresh under this specified policy using the locked data/partition manifests; mark the earlier result noncomparable. If the actual cohort/fit design cannot support the specified comparison, report that precise blocker.

## 8. Recording-group cross-fitting and calibration

Use the existing five outer and four inner recording-group partitions, after verifying their actual structure. Do not replace them with row-wise default cross-validation.

For a branch's allowed training recording set A, define:

- G: raw-model/standardizer training recordings.
- C: calibration recordings, excluded from G; approximately 20% of A's recordings.

Use the preceding study's saved G/C roles. Only when those roles are not yet saved but its exact deterministic seed/partition procedure is established may they be reconstructed and saved before fitting. Never generate multiple candidate holds to seek a favorable score. Both modalities and both representations use the same G/C roles for each A. Verify disjointness, coverage, finite inputs, and required class support; a class-degenerate partition is a stated blocker, not permission for a row-level split.

Fit each raw branch on G; predict logits on C; fit that branch's calibrator on C. Keep the raw model paired with the calibrator fitted to ITS logits. Do not refit the raw model on G union C while retaining that calibrator.

For each outer fold:

1. Let T be outer-training recordings and E outer-assessment recordings.
2. For each inner held-out fold V within T, fit each calibrated branch with A=T minus V and predict V. V must be excluded from raw fitting, normalization, and calibration. Assemble exactly one two-branch held-inner probability row per sample in T.
3. Train the F2 stacker on that out-of-fold probability matrix and T labels.
4. Fit the final calibrated branches with A=T using its saved G/C split. Predict E and apply the stacker from step 3.
5. Save direct sample keys, labels, logits, calibrated probabilities, decisions, fit IDs, and exact training/calibration/assessment memberships.

E labels must not enter fitting, stopping, normalization, calibration, or protocol decisions. Fixed original pretrained feature extraction is not task training. Out-of-fold branch predictions for stacking are required even when the visual extractor is frozen, because its head is trained.

There are normally 25 visual-head fits per condition, 25 reusable raw sensor fits across conditions, and 10 stacker fits across the complete study. The calibration holdout reduces raw-model training data; record actual sizes and do not call this exact historical F2 reproduction.

## 9. Reuse only compatible, identifiable work

Prefer reusing complete `frozen_16_frames` reference fits/predictions and matching sensor fits from the preceding NEW study when they genuinely match. Inspect their source/config identities, original pretrained checkpoint, cohort, frame selections, preprocessing, precision, normalizer policy, all G/C/T/E roles, seed and epoch/batch policy, and directly keyed inner/outer predictions. A historical AP number alone is never a reusable baseline.

Accept reuse per matching fold/fit. Save origin paths/hashes and mark status `REUSED`, not newly trained or independently reproduced. Recheck saved-model predictions on a small sample where the replay artifacts are available. Never relabel a different condition as `cnn_only` just because its score is convenient.

If compatible reference artifacts are missing or incomplete, refit the required CNN heads and sensor components inside this experiment. Do not launch the old four-condition study or repair its outputs. Missing historical lineage does not require an endless reconstruction when new, keyed fits can establish the comparison.

Cache label-independent sensor statistics only with verified sample identity/extraction settings. Reuse fitted sensor models only with exact role and config identity. Save small reused prediction tables/manifests locally for review rather than copying large weights or datasets.

## 10. Checks integrated into implementation

Implement and run focused tests, then proceed to actual extraction and fitting. Do not replace the experiment with a test-count target.

Required checks:

1. **Actual forward path:** hooks or equivalent runtime observations show backbone calls for both conditions; required encoder projection, encoder attention, and cross-scale fusion calls for `cnn_plus_encoder`; none for `cnn_only`. Add guards on forbidden decoder/proposal/detection modules so an accidental call fails. Confirm attention-bearing layers actually execute rather than inferring transformer use from imports.
2. **Frozen versus trained state:** extractor parameters and normalization buffers remain unchanged before/after representative head-training steps; the head receives finite nonzero gradients and updates. Save actual named-module counts and observations.
3. **Shapes and pooling:** assert scale dimensions/order, 16-frame grouping, per-scale spatial averaging then frame averaging. A frame permutation leaves the mean-pooled segment representation unchanged within declared numerical tolerance; batching/chunking does not mix samples. This is a code property, not proof the task needs no temporal information.
4. **Feature correctness:** verify baseline live features against a compatible prior cache when available and each new live/cache path on identified training-only samples. Validate the encoder prefix against the installed native component sequence, including projections and positional handling, without forwarding the decoder. Inspect initial shapes/finite values before extracting the whole cohort.
5. **Partition protection:** check every real fit's recording memberships, keyed joins, one-to-one prediction coverage, G/C/V/E exclusions, and that held-out labels cannot enter fitting helpers. Include negative/sentinel tests that would fail when these contracts are violated.
6. **Saved-state replay:** reconstruct a small set of outer predictions from saved extractor identity, head, standardizer, branch calibrators, and stacker. Predeclare probability tolerances: 1e-5 for float32 or 1e-3 for bfloat16; report actual deviations and do not loosen tolerances to pass a discrepancy. Keep full-precision saved prediction values.
7. **Resume/preservation:** atomic completed-fit records, partial-file detection, safe failure/restart, exact input identity validation, and restricted write paths. Status must not launch training. Preserve failed-attempt logs; do not mix incompatible protocol versions.

Use disposable training-only examples for development/timing. Reset all scientific head/RNG state afterward. No attention heatmaps or causal claims are required. Test output inspection is not a substitute for real per-fit membership checks.

## 11. Execute efficiently and retain paired results

Write `experiment_plan.md`, resolved config, execution/fit schedule, metric definitions, and actual resource estimates BEFORE scoring new assessment predictions. Select settings on the predefined protocol and training-only preflight, not the previous study's winning score.

Extract compact frozen features once per required condition, reusing compatible caches. Preserve required hardware isolation. Train only the fold-specific small heads/calibrators/stackers; do not accidentally re-run the pretrained encoder during every head epoch when equivalent cached features are available.

Process outer folds in the existing deterministic order. Complete BOTH conditions for a fold, with the shared sensor reference, before advancing to the next fold. Reused complete reference folds count as available partners, but record that they were reused.

Reserve time/storage for metrics, lineage files, checkpoint replay, and packaging. Do not alter cohort, epochs, head, seed, calibration, or folds to force completion within the cap. Stop cleanly if the next paired block is unlikely to fit. Compare only identical completed folds and sample keys; label a one-fold result a pilot and incomplete five-fold coverage PARTIAL. Preserve unpaired outputs but do not rank methods on different rows.

No automatic final refit on all assessment data, deployment, more seeds, encoder fine-tuning, attention ablation, corruption testing, adaptive gating, external dataset, or next experiment. A lower AP is a valid outcome of a valid task.

## 12. Evaluation and interpretation

Primary contrast:

`AP(F2, cnn_plus_encoder) - AP(F2, cnn_only)`.

Secondary contrasts: analogous visual-only AP difference, and each condition's F2-minus-sensor-only AP. Use failure as the positive class and the installed `average_precision_score` definition, not trapezoidal PR area. State label orientation explicitly.

Report per-fold and pooled outer-held-out metrics separately: AP, AUROC where defined, failure recall/precision, balanced accuracy, macro F1, Brier score, and reliability plots with their definition. Include sample/failure/recording counts, prevalence, completed folds, and threshold policy. Pooled AP is not the mean of fold APs.

Use 2,000 paired recording-cluster bootstrap resamples, fixed evaluation seed 314159, identical sampled recording multiplicities across methods, and all segment rows within sampled recordings. Report 95% percentile intervals, undefined/skipped replicates, and effective replicate count. These are descriptive sampling intervals conditional on this exposed dataset and one set of fitted models, not seed-to-seed training uncertainty or untouched external generalization. Secondary contrasts are exploratory/unadjusted.

For cost, measure on the same stated hardware, input size, frame count, and batch policy: extraction wall time/throughput, head/fusion training time, peak GPU/host memory, feature dimensions/storage, and active frozen/trainable parameter counts. Benchmark the real extractor, not only the cached head, on training-only samples after a short warm-up. Distinguish reused historical timings from new matched measurements. Do not count discarded detection heads as executed parameters or claim equal compute.

Save deterministic illustrative prediction changes using real IDs: largest improvements and deteriorations in true-class log loss, separated by label class and tied by sample key. Mark them outcome-selected illustrations, not independent explanatory evidence. No UI/contact-sheet generation is necessary.

Explain the results plainly:

- Did hybrid-encoder representations help visual-only classification?
- Did they help F2 relative to the same CNN and sensor references?
- How large is the effect and its conditional uncertainty?
- What extra computation and head capacity were introduced?
- What failed, remained incomplete, or was reused?
- What is the strongest conclusion under this fixed protocol?

A positive result supports this encoder-feature pipeline, not the isolated causal effect of attention. A negative result does not prove transformers cannot help. Do not claim full-detector evaluation, temporal modelling, robustness, novelty, or real-time capability from these results.

## 13. Artifacts for an actual independent review

Keep useful outputs, not a quota of documents. At minimum:

- `README_FIRST.md`: COMPLETE/PARTIAL/BLOCKED/WAITING status, one-screen findings, links, unresolved items.
- `experiment_plan.md`, `resolved_config.json`, and provenance: actual extraction boundaries, source/checkpoint/processor hashes, versions, recorded protocol and deviations, reuse decisions, hardware and resource limits.
- `data/`: directly keyed cohort/frame/split/fit membership manifests, exclusions, original and readable fold mappings. Include G/C/T/E and inner-held-out roles, not anonymous row order only.
- Each condition: directly keyed inner and outer prediction tables, head weights and reconstruction state, normalizer/calibrator/stacker parameters, training curves, parameter counts, and measured costs. Persist original weights by reference/hash rather than duplicate blobs.
- `comparison/RESULTS_SUMMARY.md`, `metrics.csv`, `paired_comparisons.csv`, plots, and changed-prediction examples. Provide a two-row comparison of visual, sensor, and F2 AP with coverage.
- `checks/`: actual test commands/results, component-execution traces, frozen-state observations, saved-model replay, membership checks, input/write-preservation scope, and review notes. Label self-review honestly if no separate permitted reviewer is available; do not purchase extra model services or block this exploratory study solely for that reason.
- `progress.json` and `how_to_resume.md`: job identities, NEW versus REUSED fits, attempts, elapsed/waiting time, remaining caps, completed/partial work, and exact supported commands. Never retry a completed fit silently.

Create `REVIEW_PACKAGE.zip` containing the small NEW code/tests/config, necessary snapshots, summaries, directly keyed inner and OUTER predictions, cohort/frame/fit manifests, metric tables, training curves, and actual check evidence. Include a size/SHA256 manifest and verify the archive after writing it. This ZIP must permit independent recalculation of reported outer metrics. Exclude videos, original datasets, large feature caches, model-weight blobs, credentials, and unrelated historical material. Do not automatically upload anything.

Give a short teaching walkthrough: Input -> Image representation -> Partition-specific head/calibration -> Two branch probabilities -> F2 -> Held-out evaluation -> Bounded conclusion.

## 14. Entry point and stopping rule

Implement a simple study-specific entry point, not the generic synthetic runner. Suggested subcommands are `prepare`, `run`, `status`, `resume`, and `evaluate`; publish only commands that actually exist and work. Support running the complete eligible pipeline after preflight rather than requiring the user to relay each stage manually.

After focused checks pass and resources/manifests are ready, proceed to the authorized scientific work. Stop for a genuine validity/access blocker or exhausted budget, not merely because historical material once said “deferred.” Never bypass higher-level restrictions.

At completion or safe stop return:

1. Actual paths to `README_FIRST.md`, `comparison/RESULTS_SUMMARY.md`, and `REVIEW_PACKAGE.zip` (or clearly state which do not yet exist).
2. A two-row table: condition, visual AP, sensor AP, F2 AP, completed folds, NEW/REUSED status. Use NOT_RUN/INCOMPLETE for missing cells.
3. Evidence that the hybrid encoder/attention executed, the decoder/detection modules did not, and feature-extractor state remained frozen.
4. Paired AP difference and conditional interval where computable, actual cost, protocol limits, and the exact resume command if needed.
5. One proposed next decision. Do not run it.

End with: Evidence checked; Still uncertain; Defensible conclusion. Separate inspected source, reported history, synthetic checks, real extraction/training, replay, and statistical interpretation. Do not call a higher-scoring invalid comparison a success.

## Reference basis and scope of preparation

This assignment follows the user's agreed next spatial-representation comparison and the existing `Run_Visual_Backbone_Comparison.md`. The uploaded implementation/status and audit records are navigation evidence, not a fresh inspection of the currently executing repository. The prompt author did not run thesis extraction, training, or inference.

Primary references checked while preparing the task (installed local code/version takes precedence for actual execution):

- Zhao et al., CVPR 2024, DETRs Beat YOLOs on Real-time Object Detection: https://openaccess.thecvf.com/content/CVPR2024/html/Zhao_DETRs_Beat_YOLOs_on_Real-time_Object_Detection_CVPR_2024_paper.html
- Hugging Face RT-DETR documentation: https://huggingface.co/docs/transformers/model_doc/rt_detr
- Hugging Face Transformers reference implementation: https://raw.githubusercontent.com/huggingface/transformers/main/src/transformers/models/rt_detr/modeling_rt_detr.py
- scikit-learn average_precision_score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
- scikit-learn stacking documentation: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html

The numerical budgets/settings above are explicit bounded study choices, not optimality claims. Do not turn these references into another literature-search assignment.
