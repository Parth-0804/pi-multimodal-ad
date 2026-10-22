# Select the strongest clean fusion pipeline, then run its noise test

## Read this first

This is an IMPLEMENTATION AND INFERENCE assignment, not another broad audit, planning session, literature review, or automation project.

The user wants the following sequence:

1. Read the completed outputs of the visual-backbone and RT-DETR hybrid-encoder comparisons.
2. Compare their eligible fused predictions with the matched original F2 reference on CLEAN data.
3. When an eligible new pipeline has higher observed clean fused AP, select that pipeline. Otherwise retain the matched original F2 reference.
4. Lock that choice BEFORE generating or inspecting new corrupted predictions.
5. Run the noise/degradation study on ONLY the selected fusion pipeline, together with the outputs of its own two unimodal branches. Do not spend inference time running every discarded fusion candidate under noise.

"Best" here means highest observed clean failure-class AP among the eligible, comparable candidates and coverage available. It does not mean proven best in the population or most robust under noise. The original and upgraded pipelines may ALL still use static F2 probability stacking. Changing the visual representation does not turn F2 into adaptive fusion.

Expected repository:
`/home/student/Master_Thesis_WS/pi-multimodal-ad`

Keep all new study code, configuration, tests, caches, logs, predictions, and reports under:
`00_experiments/fusion_noise_test/`

Implement the checks needed for valid inference, then actually execute the permitted study when prerequisites and resources are available. Preserve historical files and all other experiments. Do not ask the user to relay ordinary intermediate messages.

## 1. Authorization and resource limits

Authorized:
- Targeted reading of the two preceding studies, relevant source, existing data, local checkpoint state, fitted components, and directly identified predictions.
- New code and tests in this study folder; clean-score reconciliation; model-selection records; replay of the SELECTED saved pipeline; raw-input corruption; held-out inference; metric calculations; plots; evidence packaging.
- Computing corruption scale parameters from the selected fit's permitted CLEAN TRAINING inputs when they were not retained. These scales describe the perturbation and must never refit or change the predictor.

Not authorized:
- New training, fine-tuning, optimizer steps, refitting a classifier/stacker/scaler/calibrator, threshold tuning, model selection using noisy outcomes, corruption-aware training, or test-time adaptation.
- Training or introducing an adaptive gate. This assignment evaluates the chosen pipeline's robustness; it does not on its own establish a benefit from adaptivity.
- Dataset/weight downloads, package installation or upgrades, new paid services/resources, external datasets, UI work, generic runner development, modifying governing instructions, destructive Git actions, or unattended schedules.
- Running, repairing, extending, or renaming historical Task4 corruption-training work. This is a NEW evaluation-only study of fixed models from the two new visual studies, not a revival of excluded training experiments.
- Running full-detector/decoder heads or a temporal transformer not present in an eligible, authorized upstream condition.

Limits:
- One already allocated GPU; never interrupt another user's process or the preceding experiments.
- At most 24 hours total wall time from this task's start, including implementation, waiting, replay, evaluation, and packaging. Finish sooner when done.
- At most 30 GiB of new study storage; retain at least 10 GiB of filesystem free space or the administrator's larger reserve.
- No concurrent GPU workers; start with no more than two CPU worker threads and two decode workers. Respect stricter host restrictions.
- Three fixed realizations for each stochastic corruption, specified below. No extra trials because a result looks surprising or unfavorable.
- At most two technical repair attempts per failed stage, within these limits. A model performing poorly is not a technical failure.

Read the governing repository instructions first and preserve them. Keep source data and upstream outputs read-only. Redirect any new library caches or temporary outputs to this study folder where possible; do not modify an upstream scientific environment to make imports work. Monitor time/storage and distinguish monitored limits from OS-enforced controls. Reserve time for a partial report and safe shutdown. Stop only this task's child processes at its deadline. No automatic extension or scheduled restart.

## 2. Human-readable layout

Use this structure, adapting only small implementation filenames when necessary:

```text
00_experiments/
└── fusion_noise_test/
    ├── Run_Noise_Test.md
    ├── README.md
    ├── run_experiment.py
    ├── config.json
    ├── code/
    ├── tests/
    └── results/
        └── run_01/
            ├── README_FIRST.md
            ├── experiment_plan.md
            ├── model_selection/
            │   ├── clean_comparison.csv
            │   ├── selection_report.md
            │   └── selected_model.json
            ├── data/
            ├── predictions/
            │   ├── clean/
            │   ├── image_noise/
            │   ├── image_blur/
            │   ├── frame_loss/
            │   ├── sensor_noise/
            │   ├── sensor_channel_loss/
            │   ├── sensor_time_loss/
            │   └── missing_modality/
            ├── comparison/
            │   ├── RESULTS_SUMMARY.md
            │   ├── robustness_metrics.csv
            │   ├── paired_differences.csv
            │   ├── modality_sensitivity.csv
            │   └── plots/
            ├── checks/
            ├── provenance/
            ├── progress.json
            ├── how_to_resume.md
            └── REVIEW_PACKAGE.zip
```

Use readable names such as `fold_01`, `mild`, `medium`, `strong`, and `repeat_01`; record exact original fold IDs, numeric severities, timestamps, and hashes in metadata. Avoid timestamp-only folder names, cryptic task codes, or `final_final`.

Resume a matching existing run rather than creating competing writers. A distinct authorized protocol uses the next readable run number; it must not overwrite `run_01` or silently expand the current task's scope.

## 3. Locate and finish the dependency check without another audit

The two expected upstream studies are:

- Visual-backbone comparison: normally `runs/reassemble/visual_backbone_comparison/`, with `frozen_16_frames`, `fine_tuned_16_frames`, `frozen_32_frames`, and `fine_tuned_32_frames`.
- Encoder comparison: `00_experiments/rt_detr_encoder_comparison/results/`, with `cnn_only` and `cnn_plus_encoder`.

These are expected locators, not proof of completed outputs. Read the actual source/config/progress/fit manifests and result files. Follow established links when a study was relocated; do not scan or hash entire video/weight trees. Do not select an arbitrary run solely because its timestamp is newest. Pin an unambiguous matching pair of runs and record their identities. If multiple incompatible pairs remain plausible, report that specific ambiguity.

The upstream tasks have priority. Prepare isolated code and lightweight CPU tests while they run, but do not read half-written result banks, freeze a selection prematurely, or compete for their GPU. After useful preparation, allow at most 60 minutes of waiting, within the overall deadline, checking no more frequently than every 60 seconds. If required work is still active or resources are unavailable, save `WAITING_FOR_PREVIOUS_RESULTS` or `WAITING_FOR_GPU` and a supported resume command; do not schedule it.

A preceding task that stopped with partial or blocked results must be reported as such. Do not resume its training from this assignment. Missing historical anonymous-bank provenance need not block this study when new directly identified fits exist.

## 4. Establish eligible candidates BEFORE examining their ranking

### Reference and candidates

The PRIMARY reference is the NEW matched `frozen_16_frames` F2 pipeline, not a hard-coded historical AP number. Its new cohort and fitting policy may differ from historical F2. Historical F2 may appear in a clearly noncomparable context note, never as the primary ranking denominator.

Consider the actual completed conditions from the two studies:

- `frozen_16_frames`: canonical original-representation F2 reference.
- `fine_tuned_16_frames`.
- `frozen_32_frames`.
- `fine_tuned_32_frames`.
- `cnn_plus_encoder`.

`cnn_only` is intended as an alias or replicate of the original-representation reference, not a sixth architecture. Verify reuse/fit identities. Do not pick whichever duplicate reference scored higher. Prefer the first study's canonical reference. Use the encoder study's reference only when the original is unavailable and the documented data/fitting design is compatible. Record which reference is used. Independently refitted repeats are not silently identical checkpoints.

Do not create an untested combination such as fine-tuned CNN plus hybrid encoder, 32-frame encoder input, or a new fusion head. A condition name is not enough evidence of what ran.

### Compatibility and replay eligibility

For primary comparison require:
- Direct recording and segment identifiers, label orientation, interval support, camera identity, and unique assessment rows.
- The same cohort definition, expected outer partitions, and complete rows within each included fold. Do not compare AP on different populations or cherry-pick an overlapping subset of individual rows.
- Matching raw-fit/calibration/inner/outer memberships and the intended common sensor method, head family, calibration, fusion, seed/training-budget/threshold policy. The intended representation, fine-tuning, frame count, and associated feature width may differ; unrelated protocol departures cannot be silently attributed to these changes.
- Traceable clean fused probabilities and all final outer-fit components required for new inference: original weights or reconstruction references, any fine-tuned stage state, visual head, visual standardizer, sensor classifier/standardizer, branch calibrators, F2 coefficients, and processor/sampling/precision metadata.
- No evidence that assessment rows were included in the corresponding raw fitting, normalization, or calibration. Record the checks actually possible, without claiming training reproduction.

Determine exclusions from these requirements, not score. Record missing, failed, partial, incompatible, and unreplayable candidates in `clean_comparison.csv` with reasons. An unavailable high-scoring report is not a deployable model; do not fabricate checkpoints or refit missing components.

### Full versus partial coverage policy

Default: compare all expected outer folds, normally five, using exactly the same complete-fold rows for every eligible candidate and reference.

Predeclared fallback when upstream tasks are terminal but incomplete: before ranking, fix the intersection of fully completed and replayable outer folds across the compatible candidates that have any such folds, including the reference. Use whole saved folds, not a favorable row intersection. List candidates with zero usable folds as untested/excluded. If the common set is nonempty, proceed as a prominently labeled `PARTIAL_COVERAGE_PILOT`; one fold is only a pilot. If the intersection is empty or lacks necessary class support, block primary selection rather than mixing unequal coverage. Do not discard a low-scoring fold or candidate to enlarge coverage.

The noise cohort must then be EXACTLY the same fixed coverage used for selection. Do not append later-completing folds or change models mid-session. A selection based on partial coverage is not the best model of a completed five-fold study.

## 5. Clean-score comparison and one-time model selection

Compute failure-class AP from the directly keyed CLEAN FUSED probabilities on the locked common coverage. Use the installed `average_precision_score` definition, positive class 1; do not rank visual-only AP, accuracy, mean fold AP, or a copied rounded number. Also show visual-only and sensor-only metrics for context. Save pooled AP and per-fold AP separately.

Use this rule, fixed before reading new corruption results:

1. Compute unrounded pooled clean fused AP for the canonical reference and each eligible candidate.
2. A candidate is empirically higher-scoring only when its AP exceeds the reference by more than numerical tolerance `1e-12`. This is a numerical tie policy, NOT a meaningful-effect or statistical-significance margin.
3. If none qualifies, select the original-representation F2 reference.
4. Otherwise select the qualifying candidate with the greatest clean fused AP.
5. For numerical ties, prefer the reference when it is tied for highest; otherwise prefer fewer frames, then fewer executed model parameters if reliably measured, then alphabetical condition name. Do not use noisy performance or selectively measured latency to break ties.

Use ONE selected condition across folds, with its own previously fitted model for each fold. Do not choose a different architecture per fold or train one final all-data model.

For each candidate-minus-reference clean contrast, calculate the descriptive paired recording-cluster interval defined below. Report overlapping/negative intervals honestly. A small positive point estimate can win this empirical rule without establishing a true improvement. Do not require an invented significance rule or choose a different rule after seeing the scores.

Write and hash:
- `model_selection/clean_comparison.csv`: eligibility, origin, sample/fold coverage, fused/visual/sensor AP, delta versus reference, uncertainty, and incomplete-status reasons.
- `model_selection/selection_report.md`: reference identity, why the selected model won or why F2 was retained, limitations, and exact executed formulation.
- `model_selection/selected_model.json`: condition, per-fold fit/checkpoint/component references and hashes, label/camera/frame/processor identities, chosen common cohort/folds, fixed thresholds, exposure designation, and selection rule.

Freeze this selection and the corruption configuration BEFORE producing new corrupted predictions. On resume verify their hashes. An agent-written selection record is reproducibility metadata, not permission to expand the scope.

State prominently: choosing from previously observed outer scores makes this a DEVELOPMENT-EXPOSED, exploratory model-selection and robustness study. Outer predictions remain out-of-fit for their underlying models; they are not an untouched independent test of the selected winner. Bootstrap intervals do not undo winner selection. External validation remains separate.

## 6. Selected pipeline only: reconstruct and replay

Load only the selected condition's correct final components for each outer fold. Each assessment recording must use the model that excluded it in the upstream fitting design. Never substitute an inner model, another fold's model, the original pretrained state for missing fine-tuned weights, or a new model fitted on all rows.

Preserve the selected condition's actual 16 or 32 frames, image processor/resolution, pooled representation, visual head, sensor features, trained parameters, scalers, branch calibration, F2 coefficients, precision, and fixed decision thresholds. If the selected pipeline includes the hybrid encoder, execute that encoder; if it uses the CNN only, do not add one. Keep detector/decoder paths excluded. Verify the effective forward path in the loaded implementation.

All neural components run in evaluation mode with gradients disabled; freeze BatchNorm buffers and dropout. Fine-tuned weights are FIXED at their learned values here. No optimizer, adaptation, new fitting, or recalibration is permitted.

First perform clean replay. Compare actual output probabilities against saved selected-model clean predictions on all included assessment rows, beginning with a small fixed sample per fold. Default absolute tolerances: `1e-5` for the same float32 path and `1e-3` for the same bfloat16 path, as in the preceding tasks. Preserve any stricter already locked tolerance. Record probability/logit/decision/AP discrepancies, not just a pass flag. Do not choose a looser tolerance after failure.

Use one consistent newly replayed clean bank as the within-noise-study baseline; retain its comparison with the upstream bank. Any tolerable numerical ranking ambiguity must be reported. If replay materially fails or undermines the chosen ranking, stop the dependent noise inference; do not swap to the next model without a new pre-noise decision.

The original unselected F2 reference is used ONLY through its saved clean predictions in the selection table. Do not re-run it under noise when an upgraded condition wins. Likewise do not run all other discarded fusion conditions. Outputs of the SELECTED model's own visual and sensor branches are permitted diagnostics, not another fusion-model search.

## 7. Freeze the corruption protocol

Perturb actual model inputs BEFORE feature extraction. Do not emulate damaged images by adding noise to cached segment features or simulate sensor faults by perturbing the final failure probability. Never modify source files in place. Keep action targets, IDs, timing boundaries, and the evaluation cohort unchanged.

Use one corrupted modality at a time; the other modality remains bitwise unchanged at its input boundary. No combined-fault grid, corruption training, adversarial search, severity tuning, or fault-dependent model switching.

Predeclared conditions:

| Folder | Perturbation | Mild / medium / strong | Repetitions |
|---|---|---|---|
| `clean` | None | One reference | Once |
| `image_noise` | Independent Gaussian RGB noise on decoded pixels in [0,1] | sigma 0.02 / 0.05 / 0.10 | Three |
| `image_blur` | Gaussian blur on decoded native-resolution RGB | sigma 1 / 2 / 4 native pixels | Once |
| `frame_loss` | Remove selected frames, without replacement frames | 10% / 30% / 50% | Three |
| `sensor_noise` | Gaussian noise on finite native sensor samples | 0.10 / 0.50 / 1.00 times fit-local raw-channel training SD | Three |
| `sensor_channel_loss` | Mask complete sensor channels within the interval | 10% / 30% / 50% of channels | Three |
| `sensor_time_loss` | Mask one common contiguous time block across sensor channels | 10% / 30% / 50% of action duration | Three |
| `missing_modality` | Known complete image absence; known complete sensor absence | Two separate conditions | Once each |

There are 19 nominal clean/partial-corruption conditions plus two known-absence conditions. With three repetitions for the five stochastic families, there are 51 clean/corruption/absence prediction realizations per fold, not 51 independently trained models. The absence wrapper is reported separately below.

These are fixed synthetic perturbations, not a claim that equal severity labels are physically comparable across modalities or that these values represent calibrated industrial fault rates. Preserve raw units and affected counts. Existing historical code can be reused only when its actual semantics match; do not copy a numeric label while executing a different transform.

### Images

- Decode the locked frames once using the selected model's established decoding policy. Apply Gaussian noise in floating-point RGB [0,1], clip to [0,1], then use the same processor without double rescaling/normalization. Record any required quantization. Preserve a float-domain path when compatible; validate that the clean/no-op route agrees with the upstream processor.
- Apply blur before the existing resize/processor. Use a documented implementation with reflect boundary handling and support radius `ceil(3*sigma)`; record native frame dimensions and effective implementation. Never blur across time or color channels.
- For frame loss, let `k = min(N-1, max(1, floor(fraction*N + 0.5)))`. Remove k of the already selected N frames according to a seeded permutation. Retain chronological order of survivors and mean-pool only the surviving frame vectors. Do not resample replacements or invent zero frame embeddings. This is declared capture/frame loss, not silent visual degradation.
- No augmentation settings are fitted from damaged data. A corrupted image must actually pass through the SELECTED extractor, including learned final-stage weights or hybrid encoder where selected.

### Sensors and noise scales

- Recover channel names, native streams/timestamps, extraction rules, and raw-fit set G from actual fit metadata. Do not assume a channel count solely from old reports.
- Reuse saved raw-channel training SDs only with matching units and fit membership. Otherwise compute a deterministic finite-sample population SD per channel from clean in-interval raw samples of G ONLY. G excludes calibration and outer-assessment recordings. Save method, units, finite counts, memberships, and resulting scales. Do not substitute SDs of the 10-per-channel statistical feature vector for raw-signal SDs.
- Inject `x_corrupt = x + alpha * raw_training_sd * z` into finite native sensor values only. Preserve existing missingness. For a valid zero training SD use zero additive scale and disclose that limitation; for an undefined required scale block that dependent fault condition instead of inventing units or using assessment values.
- Recompute the selected model's usual resampling/statistics from corrupted raw streams, with the original timestamps, gap policy, and unchanged saved feature standardizer/classifier/calibrator. Do not globally re-standardize corrupted inputs.
- Channel loss: `k = min(C-1, max(1, floor(fraction*C + 0.5)))`, for C > 1. Use a seeded channel permutation, mask all in-interval samples of those named channels, and record affected names. Insufficient channel count is an explicit unsupported condition, not silent total loss.
- Time loss: choose a seeded center in normalized progress [0.25,0.75]. Mask native samples in `[center-fraction/2, center+fraction/2]` across streams/channels. This makes the three severities nested. No samples outside the annotated action interval are altered or brought in for imputation.
- Apply masks so forbidden interpolation cannot silently bridge the deliberately removed block. The selected statistical extractor must emit missing features where support is absent, with unchanged saved training-time imputation thereafter. Suppress numerical warnings only with explicit all-missing behavior, not arbitrary replacement features.
- Fix the evaluation cohort BEFORE corruption. Do not reapply the original clean-data completeness filter to drop damaged examples and report improved AP on the survivors. An inference-only adapter may carry fault masks through the existing resampling/statistics semantics; it must not change clean behavior or refit imputation. If the selected pipeline genuinely cannot represent a fault, report unsupported/failed coverage without dropping rows or claiming a completed score for that condition.

### Randomness and reproducibility

Use realization seeds `271828`, `271829`, and `271830`. Derive stable subkeys from seed, sample key, frame/channel identity, and corruption family using a recorded stable hash, not Python's process-randomized `hash()` or wall-clock time. Do not use labels, predictions, AP, or retry count.

Within a realization, reuse the base Gaussian draws across severity values, use nested frame/channel prefixes of one permutation, and reuse the time-loss center. Keep the same perturbation after resume or a change in batch size. Never average images or probabilities over random seeds and call that a single-model test.

## 8. Missing modalities are a separate system-policy test

Ordinary F2 needs both calibrated branch probabilities. A missing visual input is not `p_visual=0`; a missing sensor input is not `p_sensor=0.5` by default.

For EXPLICITLY DECLARED total image absence, report `sensor_only_fallback`: return the selected pipeline's surviving calibrated sensor branch with that branch's already fixed threshold. For total sensor absence, report `visual_only_fallback` analogously. Label this added routing policy separately from the learned F2 function. It is deterministic fallback, not learned reliability adaptation.

Do not switch away from F2 for noisy-but-present inputs based on knowledge of the injected fault or severity. No corruption labels, hidden oracle flags, assessment labels, or fault names may enter model features.

Report full-absence coverage and fallback metrics in a separate table. Do not draw a continuous F2 robustness curve that silently changes to a different model at total loss. Both modalities absent is not included and must raise an explicit unavailable/abstain state, never a confident prediction.

## 9. Efficient execution without changing the study

- Reuse unchanged sensor predictions under image corruption, after a direct invariance check. Reuse unchanged visual predictions under sensor corruption. This avoids unnecessary extraction.
- For frame loss, compact clean per-frame features may be reused if the exact fit-specific extractor, frame identities, preprocessing, and independent-frame pooling are established and live-versus-cache agreement passes. Never reuse one fold's task-fine-tuned feature cache for another fold.
- For changed pixels, run the actual visual extractor. A frozen-backbone clean segment cache cannot stand in for the corrupted input path.
- Stream and discard large corrupted tensors. Save compact predictions and corruption manifests; do not write a full damaged copy of the dataset or every multiscale feature map.
- Benchmark on a small deterministic training-input subset to estimate inference cost before the large loop. Do not examine corrupted assessment AP to optimize batch policy, transform choice, or condition order. Preserve the selected upstream precision policy; a GPU-memory issue permits smaller inference batches, not fewer frames or different weights.

Schedule: finish clean replay for all included folds first. Then perform image Gaussian noise and sensor Gaussian noise in paired severity/realization blocks across the same complete folds. Continue with blur, frame loss, channel loss, time loss, and declared-absence checks. Report partial coverage if interrupted; never report a complete paired contrast using different folds or realizations.

Save each completed condition/fold/repeat atomically with checksums and progress. Do not silently rerun completed inference or redraw noise. Do not reselect a model when its noise performance is poor. Continue other safe conditions after a specifically unsupported fault, while preserving its failure and sample coverage; validity failures affecting shared inputs or model identity block all dependent inference.

## 10. Focused tests that must pass before expensive inference

Implement the tests, then proceed; no test-count target or separate general audit.

1. **Selection:** synthetic candidate tables cover a superior eligible model, no improvement, numerical ties, an incompatible apparent winner, a missing checkpoint, duplicate reference aliases, partial folds, and no common coverage. Corrupted score fields must not affect selection.
2. **Cohort and fit binding:** direct keys, no duplicates, exact labels, fold membership, training/calibration/assessment disjointness, stable frame lists, and no assessment-derived sensor scales.
3. **Clean replay:** actual selected-model outputs reconcile with upstream keyed outputs; no-op transforms reproduce clean inference within predeclared tolerances.
4. **Frozen inference:** relevant parameters and BatchNorm buffers unchanged before/after representative inference; dropout disabled; forbidden model components not called; no optimizer/fitting entrypoint invoked.
5. **Fault validity:** one modality changes and the other is unchanged; sigma=0 is identity; Gaussian amplitude and clipping are logged; frame/channel counts and nested masks match definitions; time masks do not alter out-of-interval inputs or get interpolated away.
6. **Missingness:** no damaged sample is removed by a clean cohort filter; all-missing features obey saved imputation behavior; zero probability is not confused with absent input; the declared fallback equals the surviving branch while partial corruptions still use F2.
7. **Reproducibility:** stable noise and outputs across batch sizes/resume; cache keys bind the model/fit and transformed input; upstream files are not modified by helpers/import side effects.
8. **Metrics:** AP uses failure probabilities, not hard decisions; ties and class-edge cases handled; clean-minus-corrupted signs correct; duplicate recording bootstrap multiplicities honored; random realizations are not treated as extra independent samples.

When a test fails, repair only the new implementation within scope. Do not change the underlying scientific model or tolerance to manufacture a pass. Record actual dynamic checks separately from code inspection and synthetic tests.

## 11. Metrics, uncertainty, and interpretation

Primary endpoint: failure-class average precision. For each fault level and realization calculate selected fusion, selected visual-only, and selected sensor-only AP on the same directly identified rows. For deterministic conditions calculate once. Also report per-fold and pooled metrics distinctly.

For stochastic conditions, report each realization's metric and the mean of the THREE independently calculated metric values. The primary result is NOT AP of seed-averaged probabilities and NOT AP after stacking repeated rows as additional subjects.

Report:
- Absolute corrupted AP and `AP_drop = AP_clean - AP_corrupted`; positive drop is deterioration and negative drop is improvement.
- Fusion-minus-sensor and fusion-minus-visual AP under the SAME inputs/realization.
- Failure recall/precision, balanced accuracy, macro F1, AUROC where defined, and Brier score. Use the previously saved fixed threshold for each evaluated output; the preceding study intended 0.5, but actual artifacts establish it. Do not choose new thresholds using corrupted labels.
- Reliability diagrams with a fixed, recorded binning scheme; raw sample counts and undefined metrics. Do not rely on a single calibration scalar alone.
- Probability shifts, signed errors, corruption counts/scales, numerical failure/abstention coverage, and inference cost.

For sampling uncertainty use 2,000 paired recording-cluster bootstrap resamples with seed `314159`. Use identical sampled recording multiplicities across compared models/conditions; include every segment of each sampled recording with its multiplicity. For stochastic conditions calculate AP separately for each fixed realization within each bootstrap and then average metrics. Do not bootstrap random repetitions as independent recordings. Report 95% percentile intervals and invalid/undefined resample counts. Do not fabricate intervals where class support is insufficient.

These are descriptive intervals conditional on selected model fits, exposed data, selected candidate, these three perturbation realizations, and the recorded independent unit. They do not include full model-selection or repeated-training uncertainty. Secondary intervals are unadjusted/exploratory. Raw replicate spread describes observed noise variability, not a precise population variance from three draws.

If the selected fusion is F2, save its per-fold coefficients and optionally reconcile exact logit changes:
`delta_z = w_visual * delta_p_visual + w_sensor * delta_p_sensor`.
This is an algebraic diagnostic of the fixed stacker. Weights may be negative and need not sum to one; these terms are NOT causal percentages or learned sample-dependent gates. Report modality sensitivity under the named faults, not an intrinsic universal ranking of sensor/image importance. Equal severity labels across images and sensors have different units and are not equivalent fault strengths.

Do not claim:
- that the best clean candidate was already known to be the most robust;
- that a clean improvement proves a statistically reliable or practically meaningful gain;
- that the selected pipeline is more robust than the discarded original F2 when that pipeline was not evaluated under matched noise;
- that this static-F2 study establishes adaptive-fusion superiority;
- that complete-action classification is online detection, or that synthetic corruption proves deployment robustness or causality.

Existing historical corrupted results may be mentioned only as nonmatched prior context, not silently added as a primary comparative curve. A poor corrupted result is a valid outcome. Do not launch corruption training or search for a new winner afterward.

## 12. Outputs that answer the user's question and support independent review

Produce useful evidence, not dozens of empty documents. Include:

- `README_FIRST.md`: COMPLETE / COMPLETE_ON_PILOT_COVERAGE / PARTIAL / BLOCKED status, selected condition, reference clean AP, selected clean AP, included folds and rows, main links, and limitations.
- `experiment_plan.md` and resolved config: locked selection rule, model reconstruction, thresholds, corruption formulas/units/seeds, scale memberships, precision, coverage, resource caps, exposure status, and deviations.
- Model-selection table/report/lock and small directly keyed clean candidate prediction tables sufficient to independently repeat the comparison. Clearly distinguish upstream stored predictions from this task's clean replay.
- Data/fit/frame manifests; component source/config/checkpoint references and hashes; actual raw training noise scales and named channel order. Never fabricate file paths or identifiers from row positions.
- Every executed assessment prediction saved in CSV or compressed CSV with at least: recording ID, segment ID, outer fold, truth, selected condition, fold fit IDs, corruption family, numeric severity, realization/seed key, effective frame/channel support, raw branch logits where available, calibrated visual/sensor probabilities, fused probability, relevant fixed thresholds/decisions, availability, and fallback policy if any. Include undefined/failed rows with explicit status rather than deleting them. Preserve numeric precision in saved probabilities/logits (for example, round-trippable 17-significant-digit CSV for float64); do not round the inputs used to recompute AP.
- `comparison/robustness_metrics.csv`, `paired_differences.csv`, `modality_sensitivity.csv`, plots of AP versus named severity and calibration, and a separate full-absence fallback table.
- `checks/`: actual commands/results, replay differences, transform/invariance and freeze checks, resume checks, scoped input preservation, and review observations. A self-review remains labeled self-review; do not claim an unavailable independent reviewer.
- `progress.json` and `how_to_resume.md`: completed condition/fold/repeat jobs, blocked ones, remaining time/storage limits, and real supported commands. Do not schedule the resume command.

`comparison/RESULTS_SUMMARY.md` must directly answer:
1. Which candidate was selected, against which exact F2 reference, and by how much clean AP?
2. Is this a full comparison or a common-fold pilot? Which candidates could not be compared?
3. How does the selected fusion behave under image faults versus sensor faults?
4. Do its surviving unimodal branches reveal harmful fusion when one modality is degraded?
5. What happens under known complete absence, and which behavior is an added fallback policy rather than the original F2 function?
6. What uncertainty, cost, failures, selection exposure, and untested comparisons limit the conclusions?
7. What ONE subsequent scientific decision is justified? Do not execute it.

Include the teaching chain:
`Clean results -> candidate selection -> frozen selected pipeline -> one-modality perturbation -> branch and fused predictions -> matched metrics -> bounded conclusion`.

Create `REVIEW_PACKAGE.zip` with the small new source/tests/config, manifests, clean selection tables and keyed predictions, all compact noise/fallback assessment predictions, metrics, plots, and actual check evidence. Add a size/SHA256 manifest and verify the ZIP. Exclude raw videos/signals, datasets, large feature caches, model blobs, credentials, and unrelated archives. Reference excluded local weights by verified identity. The package MUST enable independent recalculation of selection and robustness metrics from included prediction tables. Do not upload anything automatically.

## 13. End-to-end entry point and final stopping rule

Implement a simple study-specific entry point supporting the actual pipeline; useful subcommands are `prepare`, `select`, `run`, `evaluate`, `status`, and `resume`. Publish only commands implemented and tested. Provide a single supported invocation that advances through all eligible stages without requiring manual message passing.

After the necessary checks and selection lock, proceed to actual authorized inference. Do not stop at a generic proposal. Genuine missing final results/weights, invalid replay, incompatible cohorts, host permission blocks, or exhausted budgets are precise blockers; they are not permission to refit models, change cohorts, or disregard a sandbox.

At completion or safe stop provide:
- Actual paths to `README_FIRST.md`, `comparison/RESULTS_SUMMARY.md`, and `REVIEW_PACKAGE.zip`, stating explicitly if a file was not produced.
- A compact clean-selection table and selected-model explanation.
- The selected fusion's clean, strongest predefined image-noise, and strongest predefined sensor-noise AP, with paired drops/coverage/uncertainty where computed. Do not choose the worst condition after the fact and relabel it the primary test.
- Main limitations, whether the original F2 was retained or not, what actually executed, exact remaining blockers/resume command, and one next decision.

Then STOP. Do not switch models, retrain, start another study, or schedule continuation.

End with: Evidence checked; Still uncertain; Defensible conclusion. Separate read source, upstream reported execution, recomputed metrics, newly replayed inference, synthetic tests, and proposed interpretations.

## Preparation basis

The prompt author inspected the two preceding execution prompts and the supplied audit/decision evidence. Their contents define intended studies; they do not establish that those studies completed or which candidate won. No remote thesis results, weights, training, or inference were inspected/executed while preparing this file.

Primary documentation checked for metric and inference terminology:
- scikit-learn average_precision_score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
- scikit-learn model-selection bias example: https://scikit-learn.org/1.5/auto_examples/model_selection/plot_nested_cross_validation_iris.html
- PyTorch inference mode: https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html

The installed versions and actual local implementations govern execution. These references are not an instruction for another literature search. Corruption levels, budgets, repetitions, tie policy, and partial-coverage behavior above are explicit proposed study choices authorized only when the user launches this assignment.
