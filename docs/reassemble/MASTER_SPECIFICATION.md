You are the lead research engineer implementing Study 2 of a Master's thesis on process-aware multimodal fusion for robust industrial anomaly detection.

Study 1 already exists and uses the PHM North America 2026 gear-damage dataset.

DO NOT overwrite, migrate, alter, simplify, or delete the PHM study.

REASSEMBLE is Study 2.

The purpose of Study 2 is to test the multimodal architecture under conditions where genuinely concurrent visual, sensor and audio modalities exist.

The primary architecture family is:

VISUAL:
RT-DETR pretrained visual backbone

SENSOR:
PatchTST

AUDIO:
Audio Spectrogram Transformer (AST)

FUSION:
unimodal
embedding concatenation
uniform late fusion
learned late fusion
quality-aware gated fusion
process-aware gated fusion
process+quality-aware gated fusion

ROBUSTNESS:
controlled modality corruption
missing modalities
noise
modality dropout
gate-response analysis

Do NOT optimize for a positive result.

The thesis must remain valid if late fusion beats gating or if fusion does not help.

==================================================
0. FIRST PRINCIPLE
==================================================

The scientific question is NOT:

"Can a complicated fusion model score highly?"

It is:

"When multiple industrial modalities contain useful but potentially complementary information, does adaptive process-aware fusion improve predictive performance and robustness over simpler unimodal and multimodal alternatives?"

Study 1 PHM represents a setting where those prerequisites were weak.

Study 2 must test them explicitly before fusion.

==================================================
1. REPOSITORY SAFETY
==================================================

Read:

AGENTS.md

and all repository instructions.

Work within:

/home/student/Master_Thesis_WS/pi-multimodal-ad

Do not modify PHM outputs except documentation explicitly intended to describe the cross-study design.

Create a clean Study-2 namespace:

src/reassemble/
configs/reassemble/
scripts/reassemble/
tests/reassemble/
artifacts/reassemble/
docs/reassemble/
runs/reassemble/

Raw data must remain outside Git.

Recommended conceptual structure:

<DATA_ROOT>/REASSEMBLE/
    downloads/
    raw/
    cache/

Determine DATA_ROOT from STORAGE_PREFLIGHT.md.

==================================================
2. MASTER RESEARCH CONTRACT
==================================================

Before downloading/modeling, create:

docs/reassemble/RESEARCH_CONTRACT.md

Freeze:

PRIMARY TASK
high-level action-segment success/failure classification

label:
segments_info/<segment>/success

positive anomaly class:
failure

PRIMARY GROUPING UNIT:
source HDF5 recording

PRIMARY EVALUATION:
nested recording-disjoint cross-validation

PRIMARY METRICS:
AUROC
AUPRC

SECONDARY:
macro-F1
balanced accuracy
failure recall
failure precision
specificity
Brier score
ECE

MAIN MODALITIES:
RGB video
robot/F&T sensor time series
audio

PROCESS CONTEXT:
high-level action type
pick / insert / remove / place

subject to context-shortcut audit.

DO NOT use:
session filename
recording timestamp
segment index
absolute acquisition date/time
natural-language segment text
object-identifying strings
as unrestricted predictors.

==================================================
PHASE A — DOWNLOAD
==================================================

3. VERIFY STORAGE AGAIN
==================================================

Before network transfer, reread:

artifacts/reassemble/audits/STORAGE_PREFLIGHT.md

Recheck:

df -BG <DATA_ROOT>

Require at least:

160 GiB currently free

unless the researcher explicitly approved a different storage plan.

If below threshold:

STOP.

==================================================
4. DOWNLOAD FROM OFFICIAL SOURCE ONLY
==================================================

Use the official TU Wien Research Data record:

DOI:
10.48436/0ewrv-8cb44

Resolve its official file links programmatically.

Do not use third-party mirrors.

Download:

data.zip
poses.zip
splits.zip
README.txt

Use resumable download support.

Examples of acceptable mechanisms:

wget continuation

or

curl resume

or equivalent.

Store under:

<DATA_ROOT>/REASSEMBLE/downloads/

Do not place the 54.8-GiB archive in Git.

==================================================
5. VERIFY ARCHIVE
==================================================

For data.zip compute MD5.

Required:

812103a652ca9201e87a3bcecfee4ef3

If mismatch:

DO NOT EXTRACT.

Attempt a resumable repair/redownload.

If still mismatched:

STOP WITH DOWNLOAD FAIL.

Also verify published checksums for auxiliary files against official metadata.

Run archive-integrity test before extraction.

==================================================
6. MEASURE ACTUAL EXTRACTED SIZE BEFORE CLEANUP
==================================================

After successful download:

record compressed archive size.

Inspect archive member listing.

Extract into:

<DATA_ROOT>/REASSEMBLE/raw/

Do not overwrite an existing verified extraction.

After extraction calculate:

du -sh raw/

number of H5 files
number of JSON files
total byte size

Store:

artifacts/reassemble/audits/storage_actual.md

Report:

official compressed size
actual compressed size
actual extracted size
remaining filesystem space

Do NOT delete data.zip automatically.

Only propose deleting it later if space becomes important.

==================================================
PHASE B — DATA AUDIT
==================================================

7. CLONE/REFERENCE OFFICIAL LOADER
==================================================

Use the official:

TUWIEN-ASL/REASSEMBLE

repository for dataset-structure reference.

Do not make the thesis repository depend blindly on their runtime.

Implement minimal local reading code with:

h5py
ffmpeg/imageio/opencv as appropriate

Preserve provenance:

upstream commit hash
dataset DOI
dataset checksums

==================================================
8. INVENTORY EVERY RECORDING
==================================================

Implement:

scripts/reassemble/01_inventory.py

For every H5 file inventory:

filename
file size
top-level keys
video streams
audio streams
event stream
robot_state arrays
timestamp arrays
segment count
low-level segment count

For every high-level segment inventory:

recording_id
segment_id
start timestamp
end timestamp
duration
success
text
derived high-level action type
available modalities
sensor sample counts
video coverage
audio coverage

Output:

artifacts/reassemble/audits/recordings.parquet
artifacts/reassemble/audits/segments.parquet
artifacts/reassemble/audits/inventory.md

==================================================
9. DO NOT TRUST DOCUMENTED SCHEMA BLINDLY
==================================================

Verify actual HDF5 keys and shapes.

Expected classes of sensor streams include:

force
torque
gripper positions
joint efforts
joint positions
joint velocities
pose
velocity

But derive exact names and dimensions from the real files.

Do not silently force documentation onto incompatible arrays.

==================================================
10. INGEST KNOWN DATASET ISSUES
==================================================

The official README lists recordings with:

missing hand camera
hand camera missing at beginning
missing empty action
invalid F/T in final action
broken gripper
missing pose

Create:

artifacts/reassemble/audits/known_issues.json

Verify each issue against actual files.

Define exclusion at the SMALLEST valid level:

segment rather than entire recording where possible.

Never remove data based on eventual model performance.

==================================================
11. LABEL AUDIT
==================================================

Verify counts.

Official publication reports approximately:

4,551 demonstrations
4,035 successful
516 failed

Recompute independently.

Report by:

action:
pick
insert
remove
place

success/failure

recording

object where safely derivable

duration bins

camera availability

sensor validity

audio validity

Produce:

artifacts/reassemble/audits/label_audit.md

==================================================
GATE 1 — LABEL SUPPORT
==================================================

Require:

failure class represented across MANY independent recordings

and

both success/failure represented sufficiently for group-disjoint evaluation.

Do not rely only on sample counts.

Count independent recordings containing failures.

If failures occur in only a tiny number of source recordings:

STOP AND REPORT.

==================================================
12. MODALITY COMPLETENESS
==================================================

For each segment establish usable coverage for:

candidate RGB streams:
hama1
hama2
hand

candidate audio streams

force/torque

robot proprioception

A modality is available only when its timestamps overlap the segment interval enough to construct the intended representation.

Generate completeness table by:

action
success
recording

==================================================
13. CHOOSE PRIMARY CAMERA WITHOUT USING MODEL RESULTS
==================================================

Do NOT train all cameras and select the winner.

Select one PRIMARY camera according to:

1. highest valid segment coverage
2. stable frame decoding
3. sufficient segment overlap
4. process visibility

If candidates are effectively tied, prefer the camera offering the clearest close-range interaction view based on documented hardware position, not classification results.

Freeze the choice before visual modelling.

Other cameras become exploratory.

==================================================
14. CHOOSE PRIMARY AUDIO STREAM WITHOUT PERFORMANCE SEARCH
==================================================

Use analogous rule:

coverage
decodability
proximity/relevance to contact events

Freeze primary microphone before AST experiments.

==================================================
15. SEGMENT ALIGNMENT
==================================================

Use the high-level segment:

start
end

timestamps.

For each modality obtain only data whose timestamps fall inside the segment.

Do not use future data beyond segment end.

Measure:

video coverage ratio
audio coverage ratio
sensor coverage ratio

Report gaps.

==================================================
16. MULTIRATE SENSOR SYNCHRONISATION
==================================================

The dataset preserves streams at different sampling frequencies.

Do not assume one common sampling rate.

For PatchTST construct a segment-level progress representation.

Recommended approach:

map each segment to normalized progress:

0.0 → 1.0

Interpolate selected continuous sensor channels to:

512 time positions

Initial primary sensor channels:

measured force
measured torque
gripper positions
joint efforts
joint velocities

Consider joint positions / pose / Cartesian velocity only after auditing dimensionality and leakage usefulness.

Do not use absolute timestamps as features.

==================================================
17. SENSOR QUALITY SIGNALS
==================================================

For every segment compute QUALITY METADATA not derived from labels:

valid coverage
missing-channel count
constant-channel count
outlier fraction
interpolation fraction
signal clipping where applicable

These later become allowed gate inputs.

==================================================
18. VIDEO QUALITY SIGNALS
==================================================

Compute:

valid frame ratio
mean brightness
brightness variability
blur/focus proxy
frame decoding failure ratio
motion-energy proxy

Do not derive them from success/failure.

==================================================
19. AUDIO QUALITY SIGNALS
==================================================

Compute:

valid-duration ratio
RMS
clipping fraction
silence fraction
simple noise/SNR proxy if defensible

Again no label-derived quality.

==================================================
GATE 2 — MULTIMODAL SAMPLE SUPPORT
==================================================

Define:

PRIMARY_COMPLETE_COHORT

requiring usable:

primary RGB stream
primary audio stream
primary sensor sequence
label
recording ID

Do not assume every segment is complete.

Report:

complete segments
complete failure segments
complete success segments
independent recordings

If complete multimodal support is inadequate:

allow a dual-modality VISUAL+SENSOR primary cohort,

with AUDIO moved to secondary analysis.

Do not throw away the entire study solely because audio is incomplete.

==================================================
PHASE C — CONTEXT AND SPLIT DESIGN
==================================================

20. PROCESS CONTEXT AUDIT
==================================================

Derive high-level action:

pick
insert
remove
place

from the official segment annotations.

Do NOT use unrestricted free-form natural-language text as model input.

Train no deep models yet.

Calculate failure rate by action.

Later build an ACTION-ONLY baseline.

If action alone strongly predicts failure:

that does not invalidate gating,

but every process-aware model must be compared against action-only predictions.

==================================================
21. GROUPING UNIT
==================================================

Primary grouping unit:

source HDF5 recording.

No segments from the same HDF5 recording may cross train/validation/test boundaries.

Check whether related recordings have a higher-level shared collection grouping.

If evidence exists that multiple H5 files are effectively one experimental session/trial family:

use the higher-level group instead.

Document decision.

==================================================
22. NESTED EVALUATION
==================================================

Use:

5 outer group-disjoint folds

with reasonable success/failure balance.

Inside each outer-training set:

4 inner group-disjoint folds

for:

hyperparameters
early stopping policy
threshold
calibration
learned fusion weights

Do not use outer-test metrics for development.

==================================================
23. OFFICIAL SPLIT
==================================================

Audit supplied splits.zip.

Determine whether:

training and validation files are recording-disjoint.

Use the official split only as a SECONDARY literature-comparability evaluation if scientifically valid.

Primary thesis protocol remains nested group CV.

==================================================
GATE 3 — LEAKAGE
==================================================

Assert:

no recording crosses folds

no identical content hashes cross groups where inappropriate

no filename/timestamp enters predictors

no segment text enters model features

no absolute recording ID enters model

No training until PASS.

==================================================
PHASE D — SIMPLE BASELINES
==================================================

24. DUMMY BASELINES
==================================================

Implement:

majority
prior probability
action-only logistic regression

Metrics from group-disjoint OOF predictions.

==================================================
25. SIMPLE SENSOR BASELINE
==================================================

Before PatchTST:

calculate segment statistics:

mean
std
median
min
max
quantiles
range
energy/RMS where applicable
slope

Train regularized logistic regression or shallow MLP.

Purpose:

determine whether complex temporal modelling adds value.

==================================================
26. SIMPLE VISUAL BASELINE
==================================================

Use deterministic sampled frames and a lightweight pretrained visual embedding plus simple pooling.

This is a sanity baseline only.

Do not let it replace RT-DETR primary branch.

==================================================
27. SIMPLE AUDIO BASELINE
==================================================

Log-mel spectrogram + lightweight CNN.

==================================================
PHASE E — RT-DETR VISUAL BRANCH
==================================================

28. VISUAL REPRESENTATION
==================================================

Use RT-DETR as a PRETRAINED REPRESENTATION EXTRACTOR.

Do NOT train object detection.

There are no bounding-box labels required for this task.

For each segment:

sample a fixed number of frames across normalized action progress.

Suggested:

16 frames initially.

Evaluation sampling must be deterministic.

Training may use small temporal jitter.

==================================================
29. RT-DETR FEATURE EXTRACTION
==================================================

Extract multi-scale encoder/backbone representations.

Pool spatial features to create per-frame vectors.

Then aggregate temporally.

Primary aggregation:

mean pooling

Secondary predeclared comparison:

small temporal attention pooling.

Do not build a large video transformer on top.

Output:

z_visual

with fixed dimensional projection, e.g.:

128.

==================================================
30. VISUAL TRAINING STAGES
==================================================

Stage V1:

freeze RT-DETR backbone.

Train:

projection
temporal aggregation if trainable
classifier

If signal gate passes:

Stage V2:

optionally unfreeze only final visual blocks.

Use low learning rate.

Do not fully fine-tune tens of millions of parameters immediately.

==================================================
GATE 4A — VISUAL SIGNAL
==================================================

Require OOF predictive information beyond dummy/action-only baseline with uncertainty.

Use:

AUROC
AUPRC
session/recording-cluster bootstrap

Also run group-aware label-permutation control.

If no visual signal:

record FAIL.

Do not pretend fusion can rescue it.

==================================================
PHASE F — PATCHTST SENSOR BRANCH
==================================================

31. SENSOR INPUT
==================================================

Input shape conceptually:

B × T × C

with:

T = 512 progress positions

C = selected valid sensor channels.

Fit all normalization using outer/inner training folds only.

Use robust or standard scaling based exclusively on training data.

==================================================
32. PATCHTST
==================================================

Use PatchTST as main Transformer sensor representation.

Start with modest capacity.

Suggested starting region:

d_model 64
2–4 transformer layers
4 heads
dropout ~0.1
patch length 16–32
stride approximately half patch length

Do not treat these as fixed if repository implementation differs.

Hyperparameter search must be bounded and predeclared.

Output:

z_sensor
dimension 128.

==================================================
33. SENSOR ABLATIONS
==================================================

Predeclare meaningful groups:

F/T only

proprioception only

F/T + proprioception

Primary PatchTST may use the combined set.

Do not search arbitrary channel subsets based on outer-test performance.

==================================================
GATE 4B — SENSOR SIGNAL
==================================================

Same criteria as visual branch.

Also compare against simple sensor baseline.

PatchTST need not beat the simple model to qualify as informative.

But representation suitability must discuss that result.

==================================================
PHASE G — AST AUDIO BRANCH
==================================================

34. AUDIO PREPROCESSING
==================================================

Decode primary microphone segment.

Construct log-mel spectrogram.

Use pretrained AST-compatible preprocessing.

Do not fit global normalization using test data.

==================================================
35. AUDIO MODEL
==================================================

Stage A1:

frozen AST backbone
train projection/classifier

Stage A2:

only if informative,
unfreeze final blocks with low learning rate.

Output:

z_audio
dimension 128.

==================================================
GATE 4C — AUDIO SIGNAL
==================================================

Same group-disjoint and permutation criteria.

If audio fails:

do not force tri-modal fusion.

Proceed with visual+sensor fusion and report audio negative.

==================================================
PHASE H — COMPLEMENTARITY
==================================================

36. OOF COMPLEMENTARITY ANALYSIS
==================================================

Before fusion use only development/OOF predictions.

For every informative pair compute:

prediction correlation

error correlation

both correct

both wrong

A correct / B wrong

B correct / A wrong

failure-specific complementarity

performance by action type

oracle selector upper bound

Create:

artifacts/reassemble/analysis/modality_complementarity.md

==================================================
GATE 5 — FUSION PREREQUISITE
==================================================

Require at least TWO independently informative modalities.

If only one passes:

STOP PRIMARY FUSION CLAIMS.

Do not fuse constants.

If visual + sensor pass:

dual-modal fusion is scientifically allowed.

If audio also passes:

tri-modal fusion is allowed.

==================================================
PHASE I — FUSION
==================================================

37. COMMON INTERFACE
==================================================

Every modality exposes:

embedding z_m of dimension 128

logits p_m

availability mask m_m

quality vector q_m

Freeze/standardize this interface.

==================================================
38. FUSION A1 — UNIMODAL
==================================================

Keep:

RT-DETR branch
PatchTST branch
AST branch if passed

as full baselines.

==================================================
39. FUSION A2 — CONCATENATION
==================================================

Concatenate:

[z_visual ; z_sensor]

or:

[z_visual ; z_sensor ; z_audio]

depending passed modalities.

Then:

LayerNorm
small MLP
classifier

Parameter count documented.

==================================================
40. FUSION A3 — UNIFORM LATE
==================================================

Average calibrated probabilities/logits from informative modalities.

No learned fusion weights.

This is a strong simple baseline.

==================================================
41. FUSION A4 — LEARNED LATE
==================================================

Learn convex modality weights from training/inner-validation data.

Use:

softmax weights

Never fit weights on outer fold.

==================================================
42. FUSION A5 — QUALITY-AWARE GATE
==================================================

Gate input:

modality availability
video quality
sensor quality
audio quality

Gate emits normalized modality weights.

Unavailable modality gets exact weight zero.

Remaining modalities renormalize.

==================================================
43. FUSION A6 — PROCESS-AWARE GATE
==================================================

Gate input:

high-level action type

plus availability mask.

Do not give gate segment success label.

Do not give free-form action description.

==================================================
44. FUSION A7 — PROCESS + QUALITY GATE
==================================================

Gate input:

action type
+
modality quality
+
availability mask

This is the primary proposed adaptive model.

==================================================
45. GATE FORM
==================================================

For passed modalities:

g = MLP(context, quality, availability)

w = masked_softmax(g)

Then:

z_fused =
Σ w_m * z_m

classifier(z_fused)

==================================================
46. GATE ABLATIONS
==================================================

Required:

uniform embedding average

quality-only

process-only

process+quality

process shuffled at evaluation

quality zeroed

availability-mask ablation only where safe

Measure:

mean weights
weight std
entropy
weight by action
weight by success/failure descriptively
weight by quality

==================================================
GATE 6 — GATE VALIDITY
==================================================

Do not call the gate "process-aware" merely because weights vary.

Process awareness requires controlled evidence that action/context changes weights.

Do not call it "reliability-aware" until corruption experiments show weight adaptation.

==================================================
PHASE J — CLEAN PERFORMANCE
==================================================

47. CLEAN COMPARISON TABLE
==================================================

For each architecture report OOF:

AUROC
AUPRC
macro-F1
balanced accuracy
failure recall
failure precision
Brier
ECE
parameter count
latency
GPU memory

Use paired recording-cluster bootstrap for model differences.

Primary comparisons:

concat − strongest unimodal

uniform late − strongest unimodal

learned late − uniform late

quality gate − uniform late

process gate − uniform late

process+quality gate − uniform late

process+quality gate − strongest unimodal

Report interval and effect size.

==================================================
PHASE K — CONTROLLED MODALITY NOISE
==================================================

48. FREEZE CORRUPTIONS BEFORE RUNNING
==================================================

Do NOT tune corruption levels based on outcomes.

Use deterministic corruption seeds.

Store every corruption definition in:

configs/reassemble/corruptions.yaml

==================================================
49. VIDEO NOISE
==================================================

Primary additive pixel noise:

normalize pixels to [0,1].

Gaussian noise levels:

σ = 0.02
σ = 0.05
σ = 0.10

Clip back to valid range.

Also test secondary visual corruption:

Gaussian blur:
mild
medium
strong

frame dropout:

10%
30%
50%

Optional brightness shift:

±20%
±40%

Do not combine corruptions initially.

==================================================
50. SENSOR NOISE
==================================================

Noise must be relative to TRAINING-FOLD channel statistics.

For each sensor channel:

x_corrupt =
x + α * σ_train * ε

with:

α = 0.1
0.5
1.0

Also test:

channel dropout:
10%
30%
50%

temporal block dropout:
10%
30%
50%

stuck-channel corruption:

selected channels replaced by their training median.

Never calculate σ from test data.

==================================================
51. AUDIO NOISE
==================================================

Add independent noise to obtain target SNR:

20 dB
10 dB
0 dB

Calculate signal power per sample but use noise generation independent of label.

Also:

temporal dropout
10%
30%
50%

Optional clipping severity:
mild
medium
strong.

==================================================
52. FULL MODALITY MISSINGNESS
==================================================

Test:

video missing

sensor missing

audio missing if audio branch exists

video + sensor missing only when a third modality exists

video + audio missing

sensor + audio missing

Do not evaluate configurations with zero available modalities except as prior-only sanity baseline.

==================================================
53. SINGLE-MODALITY CORRUPTION FIRST
==================================================

Corrupt ONE modality at a time while all others remain clean.

This is critical for gate interpretation.

For every corruption severity record:

performance

performance drop from clean

gate weights

change in gate weight for corrupted modality

==================================================
54. EXPECTED RELIABILITY-AWARE BEHAVIOUR
==================================================

Do not force this result.

But test whether:

corruption severity ↑

causes:

weight on corrupted modality ↓

and whether adaptive fusion loses less performance than:

concatenation
uniform late fusion
learned static late fusion.

==================================================
55. MULTI-MODALITY CORRUPTION
==================================================

Only after single-modality experiments.

Use a small predeclared matrix.

Examples:

video medium noise + sensor mild noise

sensor medium noise + audio 10 dB

video dropout 30% + audio 10 dB

Do not create a combinatorial explosion.

==================================================
PHASE L — MODALITY-DROPOUT TRAINING
==================================================

56. TRAINING ROBUSTNESS VARIANT
==================================================

Take best PREDECLARED gated architecture family.

Train second variant with modality dropout.

At training time randomly mask modalities.

Example probabilities:

single modality dropped:
0.1 each

none dropped:
remaining probability

Never drop all modalities.

Freeze probabilities before robustness evaluation.

==================================================
57. COMPARE
==================================================

Compare:

ordinary gated model

vs

modality-dropout gated model

on:

clean data

single corrupted modality

missing modality

multiple corruption.

Determine whether robustness costs clean accuracy.

==================================================
PHASE M — POSITIVE AND NEGATIVE CONTROLS
==================================================

58. LABEL PERMUTATION
==================================================

For strongest:

visual
sensor
audio if used
fusion

run group-compatible label permutation.

Performance must collapse toward chance.

If not:

STOP AND AUDIT LEAKAGE.

==================================================
59. SYNTHETIC FUSION CONTROL
==================================================

Create synthetic informative modality representation inside the fusion harness.

Verify:

late fusion can exploit it

gate can allocate weight toward it

when deliberately degraded,
quality-aware gate can reduce its weight.

This validates robustness machinery independently of real outcomes.

==================================================
PHASE N — ACTION/OBJECT GENERALISATION
==================================================

60. ACTION BREAKDOWN
==================================================

Report all principal model results by:

pick
insert
remove
place

Do not infer broad failure-mode conclusions from tiny subclasses.

==================================================
61. SECONDARY OBJECT GENERALISATION
==================================================

If object identities and support allow:

construct a secondary object-disjoint evaluation.

Train on subset of objects.

Test on unseen objects.

This asks whether anomaly detection transfers beyond familiar assembly parts.

This is secondary and must not replace primary recording-disjoint CV.

==================================================
PHASE O — EFFICIENCY AND SQ4
==================================================

62. PRACTICAL METRICS
==================================================

For every final architecture report:

total parameters
trainable parameters
model disk size
peak GPU VRAM
inference latency
throughput
preprocessing cost
number of required modalities
handling of missing modalities

==================================================
63. MODULARITY
==================================================

Discuss experimentally:

Can one branch be removed?

Can one branch be replaced?

Does late fusion permit independent branch updates?

Does gated fusion require joint retraining?

How much accuracy/robustness is purchased by extra architectural complexity?

==================================================
PHASE P — REQUIRED FIGURES
==================================================

Generate source data and figures for:

dataset success/failure distribution

failures by action

recording-disjoint split

unimodal comparison

modality complementarity

clean fusion comparison

gate-weight distribution

video noise robustness

sensor noise robustness

audio noise robustness

missing-modality robustness

weight shift under corruption

performance-vs-corruption severity

calibration

performance-vs-latency

performance-vs-parameter count

==================================================
64. REQUIRED TABLES
==================================================

T1 REASSEMBLE dataset summary

T2 modality completeness

T3 evaluation/grouping protocol

T4 simple and unimodal baselines

T5 representation comparison

T6 fusion comparison

T7 paired model differences

T8 video corruption

T9 sensor corruption

T10 audio corruption

T11 missing modality

T12 gate ablations

T13 modality-dropout comparison

T14 action-level performance

T15 efficiency/modularity

==================================================
PHASE Q — CROSS-STUDY SYNTHESIS
==================================================

65. DO NOT ERASE PHM
==================================================

Create:

docs/research/CROSS_STUDY_SYNTHESIS.md

Structure:

STUDY 1 — PHM

purpose:
test multimodal/process-aware methodology in a difficult predictive-maintenance setting where labels and modality informativeness are uncertain.

key methodological findings:
target validity matters
group/generalisation unit matters
fusion prerequisites matter
complexity cannot create absent information
robustness cannot be inferred from flat outputs
positive controls are necessary.

STUDY 2 — REASSEMBLE

purpose:
evaluate the architecture under explicit segment labels and synchronized-by-timestamp multimodal industrial interaction data.

Do not claim that REASSEMBLE "fixes" PHM.

They answer complementary parts of the overall research question.

==================================================
66. RESEARCH-QUESTION ANSWERS
==================================================

At completion explicitly answer:

SQ1

How suitable are RT-DETR, PatchTST and AST as modality representation components?

Consider:
predictive performance
sample efficiency
compute
stability
latency.

SQ2

How do:

unimodal
concatenation
late fusion
gated fusion

compare?

SQ3

Does adaptive gating improve robustness under:

noise
dropout
missing modalities?

Does the gate actually shift weight away from degraded modalities?

SQ4

What are the trade-offs in:

accuracy
robustness
interpretability
modularity
calibration
compute
practical deployment?

MAIN RQ

Answer conditionally using BOTH datasets.

Do not claim one architecture is universally best.

==================================================
67. POSSIBLE VALID ENDINGS
==================================================

All of these are acceptable.

A.

Gated fusion improves clean performance and robustness.

B.

Gated fusion improves robustness but not clean performance.

C.

Simple late fusion matches/exceeds gating.

D.

Fusion improves over unimodal but complexity gives no extra benefit.

E.

Different actions require different modality combinations.

F.

REASSEMBLE also fails to show fusion benefit.

Do not manipulate methodology to avoid E or F.

==================================================
68. CLAIM DISCIPLINE
==================================================

Prefer:

"under recording-disjoint evaluation"

"within the evaluated REASSEMBLE tasks"

"under the predeclared corruption range"

"failed action segment"

"the gated model assigned less weight..."

Avoid:

"proves"

"universally"

"true anomaly"

"best architecture"

unless strictly supported.

==================================================
69. REPRODUCIBILITY
==================================================

Every run stores:

config
dataset hash/version
split hash
Git commit
seed
environment
metrics
predictions
training history
checkpoint reference

Use resumable preprocessing caches.

Cache:

deterministically sampled frame references

RT-DETR frozen embeddings

sensor resampled arrays

audio spectrogram metadata

but keep cache provenance linked to source file hash and preprocessing config.

==================================================
70. MASTER EXECUTION GATES
==================================================

G0 STORAGE

G1 DOWNLOAD CHECKSUM

G2 LABEL SUPPORT

G3 MODALITY COMPLETENESS

G4 GROUP LEAKAGE

G5 VISUAL SIGNAL

G6 SENSOR SIGNAL

G7 AUDIO SIGNAL

G8 AT LEAST TWO INFORMATIVE MODALITIES

G9 FUSION HARNESS POSITIVE CONTROL

G10 CLEAN FUSION COMPARISON

G11 GATE INPUT VALIDITY

G12 CONTROLLED CORRUPTION

G13 MISSING MODALITY

G14 MODALITY-DROPOUT ROBUSTNESS

At every gate write:

PASS / FAIL / CONDITIONAL

evidence

numbers

artifact paths

consequence.

==================================================
71. PHASE POLICY
==================================================

This document is the MASTER IMPLEMENTATION SPECIFICATION.

If AGENTS.md requires approval between restructuring/research phases:

obey it.

At each required phase boundary:

produce the corresponding report
stop
request researcher review.

Do not violate local repository policy merely because this master prompt describes later phases.

==================================================
72. FIRST EXECUTION AFTER STORAGE GO
==================================================

Begin with:

1. repository safety check

2. dataset download

3. checksum

4. extraction

5. measured extracted size

6. recording inventory

7. segment inventory

8. label distribution

9. modality completeness

10. recording grouping/leakage audit

Do NOT train RT-DETR, PatchTST or AST yet.

Produce:

artifacts/reassemble/audits/PHASE_A_B_GATE_REPORT.md

End with exactly:

GO FOR REASSEMBLE MODELLING

or

NO-GO FOR REASSEMBLE MODELLING

Then stop if repository policy requires approval.