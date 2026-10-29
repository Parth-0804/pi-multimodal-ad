# Actual REASSEMBLE reference and source checkpoint audit

Source paths below are repository-relative unless explicitly beginning `../`.
All inspected source/config/weight/prediction identities are in
`../provenance/REASSEMBLE_SOURCE_AND_CHECKPOINT_HASHES.json`.

## Executed architecture

Original source: `PekingU/rtdetr_r18vd`,revision
`ac77a11ff0170a41b771c03264987f8ce2b0d753`; directory:
`../datasets/REASSEMBLE/cache/section1_models/ac77a11ff0170a41b771c03264987f8ce2b0d753`.
`model.safetensors` SHA-256 is
`fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093`.
Its config and processor hashes also match the historical identity manifest.

The actual primitive is
`parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/source/visual_model.py`:
`original()` returns only `RTDetrForObjectDetection.model.backbone.model`.
The detector transformer/encoder/decoder/class/bounding-box heads do not execute.
The CNN is RT-DETR ResNet18VD,depths2/2/2/2. Stage2/3/4 maps have128/256/512 channels;
each is spatially averaged,concatenated to896,then arithmetic-mean pooled across
16 ordered frames. No temporal attention is used in this mean-pooling reference.
The head is Linear896→128,ReLU,Dropout0.1,Linear128→1. Input resizing is bilinear
640×640 with /255 rescaling; `do_normalize=false`,despite mean/std values being
present in processor metadata. Feature standardization is fitted on T only.

`src/reassemble/section1_features.py:statistics` returns ten statistics per
channel:mean,std,median,min,max,q25,q75,range,RMS and slope against normalized
progress. It is the useful reusable primitive for ViFailback's28 native channels.
`.../run_01/source/fusion.py:sensor_fit` uses T/G-only normalization,balanced
logistic C1 and a separate unweighted sigmoid calibrator on C. The older
Section1 baseline selects C from0.1/1/10. The PatchTST branch in
`src/reassemble/section1_models.py` is a distinct sensor model and is not the
statistics/logistic branch used by the minimal F2 reference. Its source domain
includes actual force/torque fields that ViFailback does not supply.

## F2 and quality-aware implementations

`src/reassemble/section1b.py` builds nested group-held-out branch probabilities
and `fit_stacker` fits unweighted LogisticRegression C1 on two probability
columns. The later `.../run_01/source/fusion.py:stacker` is the same fixed form:
sigmoid(b+w_v*p_visual+w_s*p_sensor). This **F2 is a fusion model**,not the
F-beta2 metric. Its coefficients need not be positive or sum to one.
Calibration,feature scaling and branch selection have fit-local lineage.

`src/reassemble/section2_models.py:DecisionGate` is a different mechanism:
context→Linear(hidden)→ReLU→Linear2→availability-masked softmax weights;
output logit is the convex weighted sum of the two branch logits. F4 uses action
context,F5 quality context,F6 action+quality; all include availability. The
source action one-hots and domain-specific quality dimensions must not be
copied as ViFailback task IDs. Proposed transfer reuses F5's class/mechanism,
with native quality inputs and newly learned gate weights.

`src/reassemble/additional_improvements/models.py:AnchoredAdjustment` is another
existing implementation: frozen static-F2 coefficients multiplied by1+tanh(delta)
from a small context network. It is **not** DecisionGate. Any later use must
anchor newly fitted target-domain F2 rather than source coefficients. Neither
implementation proves adaptation or robustness on ViFailback.

## Saved results checked against prediction artifacts

All point estimates below were independently recomputed from saved probability
arrays and match stored AP/AUROC/Brier to within1e-12. No training,feature
extraction,calibration fitting or neural inference was rerun. Bootstrap interval
generation and the original experiments were not independently reproduced here.

| Saved REASSEMBLE system | N | Failure prevalence | AP | AUROC | Brier |
| --- | --- | --- | --- | --- | --- |
| sensor_statistics | 4530 | 0.112362 | 0.4293918694 | 0.7793245579 | 0.0804481477 |
| visual_frozen | 4530 | 0.112362 | 0.2306583150 | 0.6977948286 | 0.0942987774 |
| F2_static | 4530 | 0.112362 | 0.4472985514 | 0.7949683611 | 0.0784430122 |
| F5_quality_gate | 4530 | 0.112362 | 0.4445492940 | 0.7759869721 | 0.0806401570 |
| F6_action_quality_gate | 4530 | 0.112362 | 0.4413558906 | 0.7755232964 | 0.0807109258 |


The clean F5 and F6 point APs do not exceed static F2. Do not claim that
quality-aware or adaptive fusion was superior from these reference artifacts.
These are same-cohort historical results,not independent cross-domain evidence.

## CNN fine-tuning completion and transfer eligibility

The separate100-epoch two-arm comparison is complete. Both arms executed100
epochs from the original initialization. Frozen selected epoch14; full-CNN
selected epoch47 by REASSEMBLE validation AP. Actual recorded T/V/C sample and
recording identities are disjoint from the753 assessment actions in26 recordings.
The selected-job config retains an old `prediction_recordings` field from its
original inner role; actual prediction IDs/`predict` rows establish the26-recording
assessment. This stale bookkeeping is documented,not silently rewritten.

Valid CNN donor checkpoint:
`26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_BEST_MODEL.pt`

SHA-256 `5700e8912cf360c845087923e4b417631a886daf928e1655b1031c9ac27c8ce0`;45,347,917 bytes. Completion receipts,predictions
and checkpoint hashes agree. CPU `weights_only=True` inspection finds115
compatible CNN tensors,69 changed versus original source and46 unchanged;
stem and all four stages changed,normalization running moments did not.
See `CHECKPOINT_TENSOR_CHANGES.csv`. Thus it is genuinely trained full-CNN state,
not an untrained head or silently assumed checkpoint. The frozen-control file
contains a head and feature moments but **no backbone**,so it is not a learned
CNN donor. No detector components or source classifier/fusion coefficients should transfer.

On the matched753-action assessment,AP frozen0.1937755776,full0.2125845033;
AUROC0.6646046261 versus0.6753246753. Saved paired AP difference0.0188089257 has
conditional recording-bootstrap95% interval[-0.0364453272,0.0969255849]. This is
a post-selected single-split,seed42 study; the interval includes zero.
No new F2 was fitted in that comparison. Full-CNN training took86,271.0883
seconds(23.9642h); frozen-head training219.5726seconds. These REASSEMBLE timings
and99.74% reported kernel-busy activity do not benchmark ViFailback.

The broader active C-only study is separate: snapshot `2026-10-28T23:43:36.126035+00:00`,
**3/75 C fits complete**,20 executed epochs per completed fit,
with original cosine50 prefix. Its three-seed/five-fold evaluation is not complete.
`ACTIVE_STUDY_STATUS_SNAPSHOT.json` and completed receipt/checkpoint paths in
`REFERENCE_AUDIT.json` preserve the observed status; the ongoing job was not
paused,resumed or otherwise managed by this audit.

The epoch47 donor was fixed using source-domain validation,not ViFailback tests.
It can support a controlled optional target transfer experiment,but **no weight
transfer or target learning has yet been executed**. Source donor variability is
still only one selected seed/fit; target seeds cannot resolve that limitation.
REASSEMBLE has action-interval failures(509/4530,11.2362%);ViFailback has native
whole-episode failure detection(V2:3,755/4,384,85.6524%). Absolute APs are
not directly comparable across these targets/prevalences.
