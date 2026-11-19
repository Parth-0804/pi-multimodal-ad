# Section 1 protocol, frozen before training

The new SECTION_PLAN.md explicitly authorizes Section 1 training, superseding the
initial-execution restriction in the earlier contract. STOP after the Section 1
handoff for researcher review. Sections 2–4 remain future gated work.

Question: do visual and sensor measurements each predict action-segment failure
beyond recording-disjoint prior and action-only baselines? Failure is positive.
Use the audited primary-task, dual-complete cohort (4,530 segments / 148 recordings),
not all rows in cohort.parquet. Reuse the exact frozen 5 outer / 4 inner folds.
All preprocessing, model selection, calibration and thresholds stay inside the
outer training partition. Selection uses mean inner-fold average precision.

configs/reassemble/section1.json freezes all choices and budgets before predictions.
RT-DETR uses the official PekingU/rtdetr_r18vd COCO checkpoint, pinned revision,
its shipped image processor, spatial means of the last three backbone maps and
mean pooling of 16 deterministic in-segment frames. Only a 128-unit projection
and binary classifier are trained. No detector labels or bounding boxes invented.
PatchTST uses the installed Transformers implementation, a shared channel-independent
patch encoder, 32 hidden units, 2 layers, 4 heads, patch 32/stride 16, mean patch
pooling and a learned 128-dimensional classifier projection over ordered channels.
This modest budget is a bounded initial model; a negative result cannot exclude
signal achievable with longer training or other architectures. No fine-tuning,
audio modelling, fusion or corruption experiments are in this section.

Sensor streams retain their audited order and 512 progress points. Scaling is
per channel, training-only. Unobserved positions are filled with zero AFTER
scaling (the training mean); the observed mask is retained and supplied to
PatchTST. With internal scaling disabled, this mask does not mask attention;
missing-position robustness is not claimed. Statistics baseline uses per-channel
mean, std, median, min, max, quartiles, range, RMS and progress slope. Its imputation
and scaling also fit training only. Action-only uses fixed four-category one-hot
encoding; neither deep branch receives action, identity, text, absolute time,
object annotation or outcome-derived quality as predictors.

For each candidate epoch, each inner fit runs from initialization and produces
held-out logits; selected-epoch inner logits fit sigmoid calibration and choose
a balanced-accuracy threshold. The final model is refit on all outer training
records for that epoch budget. No outer-test early stopping or selection occurs.
The prior baseline predicts the outer training failure prevalence; majority is
reported separately. Logistic C search and deep epoch search are bounded.

Report all requested metrics, ECE with 15 fixed equal-width bins, calibration
curves, pooled OOF estimates and recording-cluster percentile bootstrap intervals
(2,000 shared replicates). Paired differences reuse the same resampled recordings.
These intervals condition on fitted cross-validation models; they do not represent
all training or dataset-selection uncertainty. Primary AUPRC is average precision.

Nineteen predeclared permutation repetitions independently circular-shift labels
within recording/action strata. This preserves group/action prevalence and within-
stratum circular run structure; singleton/constant strata cannot change. The null
is conditional on these strata and cyclic exchangeability, not arbitrary IID
label exchangeability. Log changed-label counts and refit the COMPLETE nested
selection/calibration procedure under each permutation. Evaluate against its
permuted held-out labels. p=(1+null AP >= observed AP)/(1+19); resolution 0.05.
Both branch claims must pass (intersection-union rule). Do not use permutations
as hyperparameter search or change the count after seeing results.

PASS requires positive lower 95% paired bootstrap differences for both AUROC and
AP against both prior and action-only, plus permutation p<=0.05. Unsupported point
performance is FAIL; unresolved uncertainty or conditional null limitations are
CONDITIONAL. A positive conditional control does not remove shared-day/scene or
object confounds. Complementarity is descriptive and computed only if both pass.
No fusion benefit is inferred from disagreement alone.

Sources: https://huggingface.co/PekingU/rtdetr_r18vd ;
https://huggingface.co/docs/transformers/model_doc/rt_detr ;
https://huggingface.co/docs/transformers/model_doc/patchtst ;
https://github.com/yuqinie98/PatchTST . Installed code and pinned checkpoint metadata
are the operational implementation record. No environment packages are changed.
