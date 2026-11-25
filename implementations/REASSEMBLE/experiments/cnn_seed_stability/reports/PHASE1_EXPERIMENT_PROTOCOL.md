# Phase 1 experiment protocol — fixed before new outer-test evaluation

Protocol: REASSEMBLE-PHASE1-FULL-CNN-SEEDS3-LONG50-v1. Follow-up on previously studied data; exploratory, not untouched confirmation.

Primary contrasts: C versus B visual AP and static F2 AP. Historical A/F2-A remains read-only context. A supplemental reconstructed short reference A_r comes from B's identical epoch5/10 trajectory, selected on training-side V only; it isolates extending the frozen-head horizon without a different dataset, initialization or learning-rate prefix. A_r is explicitly distinct from original A and needs no extra CNN training.

## Data, nesting and fit count

Use the original 4,530 actions, 509 failures, 148 recordings and original whole-action uniform16 frame policy. Failure=1 is exactly NOT segments_info.success. No last-quarter sampling or temporal attention. Full-cohort label, time, image and exact-input checks precede training.

Retain existing five outer/four inner folds and all25 historical A/G/C/prediction roles. Within each role, split original G once into T (80% recording groups) and validation V (20%), using fixed GroupShuffleSplit seed20261026+job_index. The exact plan is locked in PHASE1_FIT_PLAN.json before fitting. T,V,C and held-out prediction recordings are mutually disjoint. Splits remain identical across conditions and seeds. No split-seed search was performed; every initial split has both classes.

Fit normalization and gradient updates only on T. Select epochs only on V. Fit visual sigmoid calibration only on C. The sensor methodology stays balanced statistics logistic C1 on original G, with separate calibration C; these25 deterministic sensor models are shared across visual arms/seeds. Sensor/visual training sizes therefore differ deliberately, identically for B/C. Inner-role prediction groups are excluded from all base-model gradient fitting, selection and calibration. Their probabilities form four complete OOF banks per outer fold, which train the unweighted C1 F2 stacker. Apply that stacker to independently fitted outer-role probabilities. Outer labels never select parameters, epochs, seeds or thresholds.

2 arms ×3 seeds ×5 outer folds ×(4 inner OOF fits +1 outer fit)=150 visual fits, of which75 use full CNN backpropagation. No extra validation refits are needed because V is held out within each fit. There are25 deterministic sensor fits and30 main F2 stackers. Supplementary A_r adds15 inexpensive calibrator/stacker evaluations from existing B trajectories, not additional visual fits.

## Architecture and BatchNorm

Use local PekingU/rtdetr_r18vd revision ac77a11ff0170a41b771c03264987f8ce2b0d753. Execute only its ResNet CNN, spatially mean-pool the last three maps, concatenate to896 dimensions, then mean over16 independent frames. No RT-DETR hybrid encoder, decoder, proposals, detector or learned temporal model executes. Head: Linear896→128, ReLU, dropout0.1, Linear128→1.

B keeps the original backbone frozen and uses hash-verified FP32 frozen features. C begins from exactly the same pretrained CNN and seeded head, trains every executed convolution, and promotes original FrozenBatchNorm weight/bias buffers to Parameters without changing their exact forward formula. All these affine parameters train. Original running_mean/var remain fixed: one action's16 correlated frames are not a defensible population-BN batch. Backbone train mode is enabled; original normalization modules have no batch-dependent forward path. This preserves the initialized representation while allowing full convolutional and affine adaptation. Verify stem, middle, final and head gradients/updates and unchanged running buffers before launch.

## Optimization and selection

Seeds exactly42,123,20261023; no winner selection. FP32; one action/16 frames per forward; accumulation8 actions with a partial final effective batch divided by its actual size. Four persistent workers, prefetch2, pinned non-blocking transfers, two FFmpeg decoder threads. Reuse cooperative exhaustion/drain/decoder-release shutdown and validate finite epochs, early termination, exceptions and resume.

AdamW: head LR1e-3, full CNN LR1e-5, decay1e-3, gradient clipping1. No augmentation, warm-up or hyperparameter sweep. Shared cosine LR multiplier1→0.1 across50 epochs, stepped only after an epoch. Both arms run at least25 epochs unless unsafe, at most50; stop after at least25 and10 epochs without a validation-AP improvement. Choose the highest V AP checkpoint even if it predates25; break AP ties using lower weighted BCE then earlier epoch. Save every epoch's loss, V AP/AUROC, LR, runtime, VRAM and GPU telemetry. B and C have identical selection principles and classifier exposure bounds; actual stopping/selected epochs remain outcomes.

## Recovery, outputs and uncertainty

Checkpoint model, optimizer, scheduler, CPU/CUDA/Python/NumPy RNG, completed epoch, deterministic next-order seed, best validation state and histories. Two alternating resumable generations plus one selected model; no historical checkpoint is changed. Resume only completed-epoch boundaries. Roll back an incomplete epoch and replay it deterministically, recording its discarded computation separately; do not skip or count duplicate scientific samples. Verify interrupted-versus-uninterrupted continuation before long runs.

Primary AP is sklearn average_precision_score. Report AUROC, prevalence, Brier/log loss/calibration, per-fold AP and pooled held-out AP separately. Report each seed and descriptive mean/sample SD across3 seeds. Paired recording-cluster bootstrap (2000 common draws) resamples recordings consistently across both arms and all seeds; aggregate paired differences across seeds within each draw. Do not treat seeds or folds as independent recordings. Intervals condition on fitted models and exposed data; small effects do not establish general superiority.

Stage gates: A historical/input/leakage audit; B full-CNN gradient/update/reload/resume and sustained benchmark; C full150-fit matrix; D leakage-safe F2 and reporting. Only one GPU-heavy process; wait for another GPU job rather than terminate it. Full-backbone time is measured afresh. No Phase2/Phase3, package installation, commit or push. User explicitly authorizes autonomous completion within these boundaries.

## Final pre-execution clarifications

Each committed recovery generation contains its selected best-model payload
and, for B, its selected short-reference payload. An interrupted replacement of
the standalone best-model file cannot promote an uncommitted future epoch on
resume. This is a recovery-integrity extension; the gradient/update computation
and model architecture remain identical to the numerical pilot. Byte-identical
pilot source is retained with its original recorded hashes.

Use the same paired recording-cluster bootstrap for the secondary long B minus
matched short A_r contrast, keeping the primary C minus B contrast separate.
Report each fixed seed's paired direction without selecting a seed. No minimum
practically meaningful AP increase is declared after seeing outer results.
Matched inference timing uses both selected models with the same live16 input
path on 24 training-side actions; cached-head-only timing is reported separately
from end-to-end visual inference.

The measured pilot projects 495–991 full-CNN training hours for 25–50 epochs
across all 75 full-CNN fits, before validation and other overhead. The planning
allowance is 594–1,387 GPU-job hours (about 25–58 days of exclusive T4 use).
These are estimates, not executed budgets or a GPU-time cutoff.
