# Proposed ViFailback portability experiment — not executed

**Status: DRAFT FOR RESEARCHER REVIEW. No training authorization is inferred.**
The exact settings are `../config/EXPERIMENT_PROPOSAL.json`;30 core evaluated
systems and28 optional transfer systems are enumerated in `EXPERIMENT_MATRIX.csv`.
The proposal reuses project primitives and introduces dataset-owned adapters;
it does not duplicate the model framework.

## Target, cohort and input/output contracts

One original episode is one prediction example. Positive is original native
failure_detection=yes;negative=no. Native labels are not copied onto arbitrary
individual frames. Final mechanical task completion is not a separately verified
target. The V2 core has4,384 episodes(3,755/629),99 task groups;all model arms use
the **same eligible held-out episodes**. Human-category restriction and task55
coordinate quarantine define the estimand and must be disclosed. Do not make
visual-only easier by retaining rows that sensor-only excludes.

Primary visual input is16 full-view cam_high frames,chosen uniformly from0..N-1
by the fixed rule in config. No failure annotations,keyframes,native types,
review confidence or end-state judgments affect selection. Ordered unique indices
and matching converted timestamps are mandatory. Input tensor[B,16,3,640,640]
FP32,/255,resize bilinear,no ImageNet normalization;CNN spatial-pool+concat+frame
mean gives[B,896],new head gives[B] logits and calibrated failure probabilities.
All-three-camera extension uses the same16 temporal positions but48 RGB images;
it is a separate compute/input condition,not silently called a16-image model.
No cropping is required by the primary classifier; gallery enlargements are review aids.

Numerical input is the complete same episode,14 positions+12 nonplaceholder
joint velocities+two gripper-effort channels. Apply the historical ten-statistic
function per channel to obtain[B,280]. No fixed REASSEMBLE channel identity or
count is required. Do not call these force/torque. Dataset adapters should own
annotation joins,source frame selection,measured-column loading,channel whitelist,
label mapping and canonical-task/duplicate groups in `src/vifailback/` if later
implementation is authorized. Reuse the visual head/pooling,F2 and DecisionGate
primitives and regression-test unchanged feature behavior.

Forbidden ordinary features/context:episode/task/source IDs,instructions,
failure types,annotations,avoid/correct keyframes,source labels,human category,
source checkpoints' classifier/calibrators,or metadata containing the target.
Raw action/command columns are excluded. Duration is not added as a metadata
feature. Whole-episode frames/statistics can still contain temporal/end-state
cues,so results are retrospective native-outcome recognition,not early warning.

## Splits and fit lineage

Use the exact5×4 task-disjoint V2 partitions and25 T/V/C/assessment base plans.
All seeds,heads,sensor families,budgets,freeze rules and P/R initialization share
those IDs. T fits features/models,V selects a finite candidate/epoch,C calibrates,
assessment is prediction-only. No sample/task in an assessment set appears in
that fit's T,V,C,scalers or calibration. Canonical-task identity is grouping only.
Session/operator/object-instance independence remains unknown.

Within each outer-training set,the four inner assessment sets produce one OOF
visual and sensor probability per training episode. Concatenate these pairs and
fit final F2 or fixed-policy gate. Refit the branches with the outer T/V/C plan
and evaluate outer-test episodes once. All calibration/selection for an OOF row
must exclude that row's entire task. Splitting already-created OOF pairs into
meta-folds is insufficient if branch construction saw those meta-held-out labels.
If fusion hyperparameters/thresholds are later tuned,regenerate deeper nested
branch predictions. Here C1,gate size/epochs and threshold0.5 are predeclared.

## Models and controlled budgets

- Visual:original pretrained CNN with new head;frozen versus full-CNN updates.
  Execute25 and50-epoch budget conditions with the same cosine50 LR prefix;
  a single50-epoch trajectory can preserve selected checkpoints for each budget.
  Report the shared-prefix relationship rather than counting independent25/50 runs.
- Sensor logistic:balanced class weighting;C0.1/1/10 chosen using V AP;max_iter2000.
- Strong nonlinear sensor baseline:HGB,200 iterations,lr0.05,L2=0.1,min_leaf20,
  max_leaf7/15/31 chosen on V. Disable sklearn's random internal early stopping.
  Use T-only inverse-frequency sample weights. Reuse deterministic fits across
  matching visual arms;do not treat repeated identical predictions as replication.
- Averaging:0.5*(p_visual+p_sensor),for each sensor family.
- F2:new unweighted C1 probability logistic,refitted separately for each visual/
  sensor condition and seed on group-held-out OOF pairs. No source coefficients.
- Quality-aware fusion:existing F5 DecisionGate with native quality+availability,
  hidden16,ReLU,masked softmax,weighted clipped branch logits;fixed40 epochs,
  AdamW lr0.003,weight_decay0.001,unweighted BCE. No task/action one-hots. Refit it
  on the same OOF pairs and no source gate weights.

Three model seeds:42,123,20261023. Visual AdamW head_lr1e-3,CNN_lr1e-5,
weight_decay1e-3,gradient clipping1,microbatch1,accumulation8,FP32,no augmentation
in the portability reference. Promote original FrozenBatchNorm affine values to
trainable parameters for full-CNN,keep its running moments fixed. Every CNN arm
starts from the same declared P/R source and matched newly seeded target head.
Feature moments are fitted on target T at initialization and kept fixed during
that fit. Never reuse source-domain feature moments or target-test statistics.
Select highest V AP within each budget,ties lower weighted V BCE then earlier
epoch. Both rules execute the same budget;no test-selected stopping. T loss
uses pos_weight=N_negative/N_positive because native failure is the majority.
Unweighted C-only sigmoid calibration restores the target fitted-population prior.

The optional R extension uses the verified source epoch47 checkpoint:
`26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_BEST_MODEL.pt`
with SHA-256 `5700e8912cf360c845087923e4b417631a886daf928e1655b1031c9ac27c8ce0`. Transfer115 compatible CNN tensors only;
discard source head,moments,calibration,F2/gate state. P and R share inputs,
groups,budgets,selection,trainable parameter rules and seeds. Fix this donor
before any target test;do not select another donor from target performance.
One source donor cannot establish stability across source-training seeds.

## Metrics, uncertainty and safeguards

Primary:failure Average Precision. Report prevalence(85.652372% in V2) and
the no-skill constant-score AP baseline. Because the positive class is dominant,
also report AP_success,macro AP,macro-task AP,AUROC,balanced accuracy,MCC,macroF1,
class-specific precision/recall,Brier,log loss and fixed10-bin ECE/reliability
diagrams. Threshold0.5 is predeclared. No test-optimal threshold or best-seed/fold
result is substituted for the full result table.

For each seed,pool its cross-fitted outer predictions and also show every fold.
Use2000 paired task-cluster bootstrap replicates for mean per-seed metric
differences,common resampled tasks across arms. Seeds/folds are not independent
samples;three-seed variability is descriptive. Separate visual benefit(P/R or
frozen/fine)from incremental F2 benefit over each matched unimodal branch.
Inspect train/V curves and calibration for overfitting;do not tune using outer
tests or exclude poorly performing tasks after seeing results.

Quality-only prediction and quality-neutral/permuted gate ablations are useful
prespecified controls for shortcuts. Clean-data quality gating alone is not a
robustness result. Corruption/missing-modality claims require a separately
specified paired corruption and availability evaluation;no such claim is made here.

## Loading, storage and computational feasibility

No ViFailback throughput/VRAM benchmark or smoke training was run. The GPU is
already used by a separate REASSEMBLE study;this task used CPU verification only.
After later authorization,benchmark actual ViFailback decoding/forward/training
on T-only samples with workers0/2/4,decoder threads1/2,pinned memory,persistent
workers and accumulation8;check numerical behavior,worker stability,CPU wait,
throughput,VRAM and recovery. Do not assume REASSEMBLE's utilization applies.

Primary high-camera missing payload is10,033,575,648 bytes
(9.344GiB);all-three missing payload is
24,617,630,045 bytes(22.927GiB).
The whole16-frame640×640 uint8 tensor cache for4,384 episodes would be about
80.27GiB before compression,so use bounded new-run caches,not a full resident
cache. Cache only immutable decoded pixels/frozen features with source/model/
processor/selection hashes;fine-tuned embeddings must be recomputed as CNN
weights change. Preserve all existing historical caches/data.

For one initialization and both backbone rules,the25 base fits×three seeds give
75 full-CNN50-epoch trajectories and75 frozen-head trajectories,with25-budget
snapshots sharing prefixes. The actual enumerated T sizes total43,061 per one
epoch over25 fits. Full-CNN50 across three seeds means6,459,150
episode presentations. At the **REASSEMBLE-only** rate2.032 episodes/s this is
about883.0training GPU-hours before validation/calibration/I/O;
this is a planning extrapolation,not a ViFailback benchmark or promised runtime.
An R extension roughly doubles this CNN exposure. Selected full-CNN weights
alone occupy roughly3.4GB for75 fits;two180MB recovery generations per fit would
add about27GB,plus caches/raw videos/curves. Preflight storage and checkpoint
retention must be reviewed;do not silently delete completed evidence to fit.

## Required prelaunch acceptance checks

1. Researcher reviews V2 restrictions and protocol;resolve or retain documented
   coordinate quarantine without automatic sign correction.
2. Retrieve only needed pinned video paths;verify hashes,count/dimensions/PTS,
   all16 frames,frame/table association and visibility/overlays/human presence.
   Version any revised eligible cohort and preserve the current split maps.
3. Validate frame/sensor/label contracts,forward/gradient paths,save/reload,
   group disjointness,per-row OOF lineage,metric calculations and bounded loading.
4. Verify P/R CNN-only loading and reinitialized target head/moments/calibrators.
5. Freeze implementation/config/software/checkpoint hashes before outer assessment.

No training,neural inference,new model calibration or transfer result is supplied
by this verification task. This document is an executable research specification
for later implementation/authorization,not evidence that the architecture works.
