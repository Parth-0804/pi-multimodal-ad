# Architecture verification

The executed primary F2 fitter is `src/reassemble/section1b.py::fit_stacker`; the later clean-CNN primitive is retained as a separately identified reference. The 100-epoch CNN extension is `26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py`; its inference/training recipe is `phase_training.py` in the same folder. Their source hashes and original checkpoint hashes are in the run input manifest. The earliest historical F2 is `src/reassemble/section1b.py`; differences are recorded below rather than treating later recipes as identical to every historical experiment.

## Static sensor branch — canonical earliest original implementation

`src/reassemble/section1_features.py::statistics` defines22 original sensor channels: measured force3, measured torque3, gripper positions2, joint efforts7 and joint velocities7. It computes10 blocks after the original512-point resampling: mean, population standard deviation, median, minimum, maximum, q25, q75, peak-to-peak, RMS and slope over normalized action progress. This gives220 features. All4530 cached rows match the original 148 recording blocks exactly; no feature was changed or re-extracted.

The primary sensor uses the earliest `src/reassemble/section1_models.py` functions `Standardizer`, `logistic_fit` and `calibrate` and Section1b nested selection/calibration procedure. Standardizer fits nanmean/nanstd on its branch-training rows only, floors invalid or tiny standard deviations at1 and fills remaining transformed nonfinite values with0. Balanced logistic C is selected from0.1/1/10 on training-only recording folds. A separate unweighted sigmoid calibrator is fitted to genuine within-training OOF logits, then applied to the refitted branch's assessment logits.

The original inner3 branch uses2857 fit/OOF-calibration actions and selected C0.1; it generates the 920 genuinely held-out F2 fitting probabilities. The original outer branch uses3777 fit/OOF-calibration actions and selected C1; it generates the 753 test probabilities shared exactly by M3–M7. Its original native decision threshold is0.14. The original code did not persist raw logistic weights/scalers. These small states were reconstructed from the exact recorded training groups, using the original source and settings, and independently verified against the original saved probabilities and OOF calibrators. Scientific evaluation reuses the saved original probabilities rather than replacing them with the reconstructed outputs.

The later clean-CNN/Phase1 separate-C sensor variant (G2171/C686 and G2966/C811) was also audited and replayed exactly, but is retained as reference evidence only. It is **not substituted for the canonical original primary sensor**. Both historical recipes, source paths and the pre-test protocol clarification are preserved. Matching the original16-thread numerical-library context reproduces the original canonical probability banks exactly; no original source, checkpoint or result was modified.

## Visual branch

Sixteen distinct hand-camera frame indices per action, exact original resize/rescale and verified pixel hashes feed the pinned RT-DETR R18vd CNN. The last three backbone maps are spatially averaged/concatenated to896 dimensions, followed by the original 16-frame arithmetic mean and training-T-only standardization. The classifier is896→128, ReLU, dropout0.1, then128→1. The frozen arm reuses verified FP32 pooled features. The fine-tuned arm learned all executed CNN convolution and normalization-affine parameters plus the head; normalization running moments remained fixed. No detection transformer/head, PatchTST, audio or32-frame input is used.

Both arms executed 100 epochs from original pretrained initialization, seed 42, with the same selected fit 3 partitions, FP32 recipe, effective action batch8, AdamW, head LR0.001, backbone LR0.00001 where trainable, weight decay0.001, clipping1 and cosine100 schedule. Checkpoint selection used V only: frozen epoch14, full epoch47. Each visual calibrator was learned on the same separate686-action C bank. Saved calibrators are reused; no calibration is fitted on the F2 bank or test set.

The saved original first-epoch gradient receipt was checked directly: every CNN stage and the head had finite, nonzero gradient evidence and changed weights, while running normalization moments remained unchanged. No new gradient-training pass was used for verification.

## F2 method, not an F2 classification metric

The executed fitter is the original `src/reassemble/section1b.py::fit_stacker`. It fits unweighted C1 logistic regression (`lbfgs`, max_iter2000, random_state0) directly to `[p_visual,p_sensor]`, with unrestricted coefficients and intercept. Probabilities are not converted to logits or meta-standardized:

`p_F2 = sigmoid(intercept + w_visual*p_visual + w_sensor*p_sensor)`.

The same original function also selects a native threshold by maximizing balanced accuracy on recording-disjoint meta-cross-fitted training probabilities over0.01–0.99, ties nearest0.5. This original native threshold is saved and evaluated for each F2 arm. The primary common-threshold metric table additionally uses0.5 for every model so precision/recall/F1 share an identical convention. Native-threshold metrics are retained separately; no test-derived threshold is chosen.

To isolate fitting from evaluation, the original fitter receives only the 920 training-side probability pairs/labels and a fixed dummy prediction row. Real outer probabilities are opened only after saving and hashing the fitted models. The two visual arms use the same 920 rows, canonical sensor column and four recording-disjoint meta folds. Simple averaging is exactly `(p_visual+p_sensor)/2`.

Historical M8 uses the same canonical sensor, original F2 formulation and native threshold-selection rule, but has the old visual recipe and a complete3777-row nested branch-OOF fitting bank. The new fixed100-epoch checkpoints can supply one920-row genuine holdout bank; this explicit holdout-stacking adaptation is not presented as a complete historical nested-OOF reproduction.
