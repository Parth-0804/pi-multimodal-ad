# Fixed protocol for the new F2 visual backbone comparison

This protocol was written before any new model scores. Preparation is in progress; a completed cohort lock and the dynamic gradient checks must exist before fitting. The launch accepts five epochs and the other fixed settings below. Valid negative or inconclusive findings complete the experiment; no target AP or score-based repair is permitted.

## Question and four conditions

The primary contrast is F2 AP for final-stage adaptation with16 frames minus F2 AP for frozen16. Secondary comparisons add32 observations to each arm and describe the interaction. The same visual comparisons and each F2-minus-sensor AP are reported. This is a new completed-action failure study on previously examined REASSEMBLE data. It is not completion of historical Task1, online warning, untouched confirmation or robustness testing. Historical Task4 remains excluded.

| Condition | CNN training | Distinct interval frames |
|---|---|---:|
| frozen_16_frames | Frozen |16|
| fine_tuned_16_frames | Final stage only |16|
| frozen_32_frames | Frozen |32|
| fine_tuned_32_frames | Final stage only |32|

The actual original local object is RTDetrResNetBackbone; the caller returns `.model.backbone.model`. Its selected features are stage2/stage3/stage4. No detector encoder/decoder or temporal transformer forward is used. Final-stage name is `backbone.encoder.stages.3`: five convolution-weight tensors,8,388,608 parameters, identified by the constructed object rather than a checkpoint name. Normalization affine quantities in this implementation are buffers, so they remain frozen along with running statistics. Dynamic forwards will determine the pooled width. The shared head is fitting-G standardization, Linear(D,128), ReLU, Dropout(0.1), Linear(128,1). Spatial means concatenate selected maps; frame vectors use an arithmetic mean.

## Cohort and identity

Verify native recording/segment keys, annotation-derived failure labels, intervals and actual frame decoding. Retain otherwise primary/dual-complete rows only when32 distinct in-interval hand-camera frames decode. Preserve the original16 uniformly rounded frame indices. Add frames by greatest distance in timestamp from the nearest already selected timestamp, with earlier index breaking ties; original selection includes interval end candidates. Save both chronological lists and subset positions. All methods use this one cohort, locked before fitting or scoring. Exclusions and class/recording counts before and after restriction are saved by original outer fold. No outcome-driven eligibility changes or split redraws.

## Group cross-fitting and calibration

Restrict the original five outer/four inner recording-group assignments to the new cohort. Each exact allowed raw-branch partition A receives one GroupShuffleSplit with20% recording groups for calibration C; G=A minus C. A SHA-derived seed from base42, outer fold and partition role is identical across conditions and sensor. Verify G/C/held-recording exclusion and both-class support before fitting. Stop on infeasibility.

Raw normalizers, gradients and positive weights use G only. Sigmoid logistic calibration C=1, unweighted, uses only C raw logits and labels. Retain the G-trained raw model; never refit it on G union C with that calibrator. Four inner held-out branch predictions supply one calibrated pair per outer T sample. Fit F2 on these OOF pairs and T labels; separate final G/C branches predict outer E. Save keys, model/config/cohort identities and all memberships.

Planned total:100 independent full visual fits and25 sensor fits. Within each outer fold, complete frozen16, adapted16, frozen32, adapted32 before moving to the next fold. Reuse only the newly identified sensor result for the exact matching partition.

## Fixed fitting choices

Every visual fit starts independently from the original local pretrained CNN and a fresh role-seeded head/optimizer. Exactly five epochs, final weights, AdamW head learning rate1e-3 and final-stage rate1e-5, weight decay1e-3, gradient clipping1. Effective batch eight segments; common microbatch one segment; normalize a partial final batch by its actual segment count. Positive BCE weight equals negatives/positives in G. Matched role seeds and deterministic segment order use base42. No augmentation, early stopping, sweep, extra seeds, full-backbone adaptation or joint fusion backpropagation.

Float32 is fixed: the available T4 has no native BF16. Keep every CNN module in evaluation mode while the head uses dropout during fitting. The G normalizer is derived from ORIGINAL pretrained features for the matching frame count, uses the core1e-6 standard-deviation floor and stays fixed/differentiable throughout adaptation.

Sensor representation retains the attributed512-point progress resampling and channel statistics. Raw logistic C=1, balanced classes, max_iter2000, random_state42; fit-local G scaling. F2 is unweighted logistic C=1 with intercept on `[p_visual,p_sensor]`, with no scaling or fusion calibrator. Decision threshold0.5 is locked for every calibrated branch and F2. Coefficients are not causal percentage contributions.

## Execution, checks and resources

Use one foreground training worker on the suitable available T4. The latest user launch removes the24-hour ceiling; it does not relax scientific settings or fit/storage limits. Four-CPU affinity and four-thread libraries, zero loader workers, monitored32 GiB process RSS. At most110 full visual fit starts including restarted fits,20 disposable optimizer steps on first-outer G records, and two technical repairs per failed stage. No installations, purchases, downloads, extra jobs or schedules. All new source/config/tests/logs/artifacts/caches remain inside this human-readable study directory.

Before full fitting, pass synthetic partition/calibration/frame/F2/sentinel/regression tests; actual frozen/last-stage gradient and weight/BN checks; saved model and optimizer/RNG checkpoint replay; dynamic pooling widths; and training-only timing/resource estimates. Full fits additionally record membership, observed gradients/weight scope and loss trajectories. Saved full pixel-to-calibrated-probability replay uses the first three held-out keys, tolerance1e-5 declared before results. F2 arithmetic uses1e-12. Preserve original dirty files and selected input hashes.

Original-feature extraction uses each condition's actual frame-batch shape and Torch float32 pooling reductions. Adaptation always has a live final-stage gradient path; no cached learned segment embedding is substituted. No spatial-prefix cache is used. Pixels may be stored losslessly as uint8 NPZ only after bitwise processor equivalence, with uncompressed content SHA verification. Disk cache cap24 GiB and compressed RAM cap8 GiB form exclusive LRU tiers; reserve4 GiB for models/features/metadata, below the30 GiB new-storage ceiling. Keep at least10 GiB filesystem free. Completed optimizer copies are released only after compact stage/head state, calibrator, keyed predictions and replay evidence exist; a SHA/size/completion receipt remains. Interrupted fits retain optimizer, RNG, epoch, order position, precision and compact model state. Own regenerable cache files may be evicted; no historical or raw file may be changed.

## Evaluation before any further decision

Compare only identical outer folds completed by all four conditions. Save per-fold and pooled failure average precision using sklearn.average_precision_score, and mean fold AP separately; save counts and prevalence. Use2000 paired recording-cluster draws, seed314159, retaining every segment and sampled multiplicity,95% percentile intervals conditional on these fitted models and exposed data. Mark one-class draws undefined, discard them without replacement and report valid counts. Secondary intervals are unadjusted/exploratory and omit repeated-training uncertainty.

Secondary metrics: AUROC where defined, precision/recall, balanced accuracy, macroF1, Brier and ten fixed equal-width reliability bins, all with threshold0.5. Record original-feature extraction, raw training and inference/replay costs separately, parameter counts, optimizer updates and peak memory. Equal epochs do not imply equal compute.

Select12 illustrations by F2 true-class log-loss reduction, adapted16 versus frozen16: three greatest strictly positive improvements and three greatest strictly negative deteriorations within each truth class, ties by sample key; mark insufficient cases and overlap. Save IDs, action, interval, truth, branch/F2 probabilities, fold and both frame lists. These chosen illustrations are not independent evidence.

Final outputs: README_FIRST.md, comparison/RESULTS_SUMMARY.md, directly keyed assessment predictions/metrics and REVIEW_PACKAGE.zip with new source/tests/config/manifests/evidence. Exclude raw data, caches and weight blobs; preserve their local identities and hashes. Validate archive CRC, payload hashes and direct AP recomputation from archived keyed CSVs. Self-review is explicit; independent review remains outstanding. Do not fit a final all-data model, select a favorable setting after assessment, deploy, launch another experiment or schedule continuation.
