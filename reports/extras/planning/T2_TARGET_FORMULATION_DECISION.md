# T2 target formulation decision

Status: **AUTHORITATIVE TASK SEMANTICS RESOLVED; IMAGE MEASUREMENT UNDER VALIDATION**  
Decision version: `phm2026_image_damage_v2`  
Decision date: 2026-08-14

## Official interpretation

The [official PHM North America 2026 challenge description](https://data.phmsociety.org/phm-north-america-2026-conference-data-challenge/) is authoritative. Training images are captured after each run; participants estimate spall size or severity for all 28 teeth, aggregate those values into one scalar trajectory, and train a model that uses sensor measurements to estimate damage. The organizer retains a separate undisclosed reference. No organizer-provided participant target is expected.

This clarification supersedes the earlier assumption that absence of an organizer scalar necessarily blocks target construction. The earlier audit remains preserved as pre-clarification evidence. D-phase findings remain historical evidence and are cited in `PROJECT_STATE.md`.

## Prediction and cadence

Estimate the current gear-tooth damage state reached at the end of experiment `e`, run `r`, using only sensor measurements collected no later than that run's end. This is current-state estimation, not automatically six-hour-ahead forecasting.

Six hours is the typical run duration, approximate post-run inspection cadence, and required prediction-output cadence. Some runs last about one to three hours. Actual duration must come from counts/timing of one-minute HDF5 recordings. Six hours is not assumed to be a forecast horizon or fixed input history.

## Per-tooth measurement

For tooth `j`, the primary candidate is the percentage of visible tooth-flank ROI pixels assigned to a reproducible damage-candidate mask:

`a[e,r,j] = 100 * A_damage_candidate[e,r,j] / A_visible_flank_ROI[e,r,j]`.

Until a human verifies the ROI and mask, `a` is a **provisional pseudo-label**, not organizer ground truth or calibrated physical spall area. Multiple close-up views of one tooth remain individually traceable; their deterministic tooth aggregation and protocol bias are reported.

## Run target

Primary raw candidate:

`z[e,r] = mean(Top3({a[e,r,1], ..., a[e,r,28]}))`.

Causal monotonic candidate:

`y[e,r] = max(z[e,1], ..., z[e,r])`.

Both raw and monotonic values remain available. Top-1, top-5, all-tooth mean, total burden, damaged-tooth count, ordinal severity, visual anomaly and early-tooth change remain comparison evidence. The primary choice cannot be made merely for sensor correlation.

## Association and quality

The authoritative non-temporal key is `experiment_id + run_id`; tooth identity extends it for image measurement. Post-run images pair to sensor recordings from the same experiment/run when repository naming/manifests agree. Local-naive or missing image timestamps do not invalidate run-level association. ZIP order, filename order, equal file-count division and coerced UTC values are forbidden.

A missing tooth is never zero. Each run records valid-tooth count and protocol. Incomplete or ambiguous inspections are excluded using a versioned minimum-coverage rule. EXP-A/B have ten close-ups for teeth 1–4 and generally one canonical image for teeth 5–28; EXP-F has one canonical image per tooth. This protocol difference requires explicit confidence and human review.

## Candidate exclusions

Run number, elapsed time, lifetime percentage, archive order, FM4/NA4/M6A/ALR alone, COCO detections, lifecycle labels and RUL are not image-derived damage targets. Sensor indicators may be inputs or convergent-validity evidence only.

## Human validation

Review must cover ROI acceptability, mask acceptability, corrected tooth value, failure reason, reviewer and timestamp. Provisional metrics/checkpoints cannot be presented as validated physical-damage performance before review.

## Model roles

With per-tooth scalar pseudo-targets but no boxes, the permitted image architecture is an **RT-DETR-derived image-regression baseline**: image → pretrained RT-DETR backbone/hybrid encoder → multi-scale aggregation → scalar head. Each tooth image is trained against its own value; run predictions use the same aggregation rule. Standard COCO inference remains architecture feasibility only.

PatchTST is reserved for a later sensor-only model over ordered compact run features. It is not authorized in the current task.

## Leakage, versioning and change control

- no sensor values after the run cutoff and no image features at sensor-model inference;
- no run, inspection, tooth group or near-duplicate group crosses partitions;
- scaling and learned thresholds fit on training only; EXP-F is untouched for tuning;
- monotonic correction uses only current/earlier targets in the same experiment;
- target definition, algorithm, ROI, thresholds, view aggregation, minimum coverage and review state are hash-pinned;
- raw measurements remain alongside corrections; changes create a new definition, manifests, splits and run.
