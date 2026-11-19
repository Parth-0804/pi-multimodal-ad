# Fixed encoder comparison

Failure=1; success=0. Common >=32-frame-eligible cohort, exact saved 16 frames, five outer/four inner recording splits and saved G/C memberships. No score-based choices.

Original local checkpoint -> independent images -> native multiscale maps -> per-scale spatial means -> concatenation -> 16-frame arithmetic mean. CNN reference omits projections/encoder; encoder branch includes pretrained encoder projections/AIFI/FPN/PAN and ends before decoder projections. All pretrained state frozen/eval. Float32 both branches.

Each raw head uses G-only standardization, 128 hidden units, ReLU/dropout .1, 5 epochs, AdamW lr/decay .001, clipping 1, effective batch 8 with per-segment accumulation and actual partial-batch denominator. NumPy role-seed+epoch ordering independent of head dimension. G-only positive weighting. Sigmoid calibrators fitted on C. Shared balanced C=1 sensor logistic model and C-only calibration. F2 C=1 unweighted logistic uses held-inner calibrated probabilities, no scaling/fused calibrator. E excluded from all fitting.

Fold order 01..05; both conditions completed before advancing. Maximum 50 planned visual/25 sensor/10 stacker fits, caps 55/30/12 including retries. Shared original features/statistics may be cached across folds; no fitted normalizer is shared across roles.

Primary: pooled paired AP(F2 encoder)-AP(F2 CNN). Per-fold and pooled AP, AUROC, precision/recall at .5, balanced accuracy, macro F1, Brier. Reliability: 10 equal-width probability bins, mean predicted versus empirical failure fraction. 2000 paired recording-cluster bootstrap replicates, seed314159, percentile95% intervals, degenerate replicates skipped and counted. Secondary exploratory visual AP and each F2-minus-shared-sensor AP. No new trial based on outcomes.

CPU preparation capped at two threads; one allocated T4 only after priority process/device release and stable manifests. 24h including waiting, 30GiB new storage, 10GiB free reserve, 32GiB monitored RSS. Budget checks before stages/writes and during fitting; elapsed reporting reserve15min. GPU runtime traces and saved-model replay are prerequisites, not inferred from source.

No assessment scores examined in preparation. Resource estimate: compact features are N*(observed CNN D+observed encoder D)*4 bytes, head files at most55*(128*D+257)*4 plus optimizer checkpoints; no pixel cache retained. Exact dimensions and training-only benchmark determine remaining execution feasibility before full extraction. Review ZIP excludes model blobs and feature arrays.
