# Study 2 research contract

Frozen before dataset transfer, 2026-09-27. This protocol concerns REASSEMBLE
(DOI 10.48436/0ewrv-8cb44); PHM Study 1 and all its evidence are preserved.

## Primary task and evaluation

Classify high-level action-segment success/failure from
`segments_info/<segment>/success`; failure is positive (1). Empty/unrecognized
actions are inventoried but excluded from the four-action primary task.
The primary grouping unit is the source HDF5 recording, escalated to a documented
shared trial/session family if evidence establishes dependence. Use five outer
and four inner group-disjoint folds. Every preprocessing statistic, calibration,
threshold and learned fusion weight is fitted only within training/inner folds.
Outer-test outcomes cannot select representations, channels or architectures.
Primary metrics: AUROC and average precision (AUPRC definition). Secondary:
macro-F1, balanced accuracy, failure recall/precision, specificity, Brier score,
and ECE (15 equal-width probability bins). Paired recording-cluster bootstrap
provides uncertainty; no claim of independent segment observations.

## Inputs and exclusions

Main candidate modalities: RGB video, robot/F&T sensors and audio. Action context
is limited to pick/insert/remove/place and requires an action-only comparator.
Filenames, absolute times, recording ID, segment index, annotation text and
object-identifying strings are audit metadata, never unrestricted predictors.
Audio may contain operator narration; audit this semantic shortcut explicitly
before interpreting audio as mechanical/contact information.
Use only timestamps inside each segment; never include later samples. Sensor
representation uses 512 normalized progress positions, initially measured force,
measured torque, gripper positions, joint efforts and joint velocities. Inspect
actual shapes and rates; no assumed common sampling frequency. Fit scaling and
outlier reference statistics on training folds only.

## Outcome-independent audit rules

Availability requires at least 90% interval coverage, valid timestamp ordering,
and enough finite samples for representation. Gaps larger than five median
sampling intervals do not count as covered. At least 16 decodable timestamped
frames support the visual representation. Audit audio timing against the official
loader; absent defensible alignment means unavailable, not guessed timestamps.
Select primary camera/microphone by valid segment coverage, decoding stability,
overlap, and documented hardware placement, never predictive performance.
Predeclare a coverage tie as <=1 percentage point; resolve using documented
interaction proximity, otherwise a documented deterministic name order.
Sensor channels with missing/nonfinite values remain explicitly masked; no
extrapolation beyond the observed interval is treated as valid data.
Known defects create segment/modality exclusions where defensible; never delete
records or exclude on eventual model performance. Conservative unresolved defect
flags remain visible and prevent unsupported gate PASS decisions.

For initial label support require >=10 failure-bearing independent recordings
and >=10 success-bearing recordings, plus both labels in every proposed outer
and inner assessment partition. This operational minimum does not guarantee
statistical precision. Primary complete cohort requires usable visual, sensor,
audio, label and group; if it fails support, test visual+sensor support and move
audio to secondary. Report both denominators and action distributions.
Hash recordings for exact duplicate detection. Freeze deterministic split seed
20260927; never search seeds based on model outcomes. Official split is secondary
only if disjoint. Higher-level grouping evidence can require revised grouping
before any modelling; calendar dates alone do not establish shared trial identity.

## Later modelling (not authorized in this execution)

RT-DETR is a frozen pretrained representation extractor initially, not a detector
trained with invented boxes. PatchTST is the primary sensor model; AST is the
candidate audio model. Each exposes 128-dimensional embeddings, separate logits
and calibrated probabilities, availability masks and label-independent quality.
Compare dummy/action-only/simple modality baselines, unimodal models,
concatenation, uniform and learned late fusion, uniform embedding average,
quality-only, process-only and process+quality gating. Unavailable modalities get
exact zero gate weight. No adaptive fusion claim without two independently
informative modalities and synthetic positive controls. Unimodal signal gates
require group-disjoint predictions, uncertainty and group-aware permutations.
Freeze corruption seeds and severities before robustness evaluation; sensor
noise uses training-fold statistics. Measure gate weight response, missingness,
modality dropout, calibration, compute and action-specific results. Negative
results and superiority of simple late fusion remain valid thesis outcomes.

## Scope and review boundary

Current execution: acquisition, checksum/integrity, extraction, measured storage,
recording/segment inventory, labels, modality completeness and grouping/leakage
audit. No baseline or deep model training. Write PHASE_A_B_GATE_REPORT.md and
stop for researcher review under AGENTS.md and master specification section 71.
The master gate numbering G0 storage, G1 checksum, G2 labels, G3 completeness,
G4 leakage is authoritative; subsequent model gates are not evaluated here.
