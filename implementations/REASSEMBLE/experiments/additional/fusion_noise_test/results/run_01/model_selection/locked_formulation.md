# Locked selected pipeline

Selected condition: `frozen_16_frames`; `PARTIAL_COVERAGE_PILOT`, fold_01 only, 753 actions from 26 recordings with 77 failures. This is the canonical reference itself; clean AP improvement over reference is zero. All four newer variants are untested on the required completed-fold basis.

Sixteen fixed hand-camera frames per action, original local frozen RT-DETR CNN only, independent spatial pooling at three CNN scales (896 features) and mean pooling across frames. The original processor, 128-unit ReLU/dropout visual head in evaluation mode, saved visual standardizer and calibration are retained. No hybrid encoder, detector decoder, query/proposal selection, detection head, or temporal transformer executes for this selected condition.

The sensor branch retains 22 native channels and ten saved statistical feature definitions per channel (220 features), the original resampling and float32 feature arithmetic, saved standardizer/imputation, logistic classifier and calibration. The technical adapter repair restores that arithmetic without fitting any parameter.

Static probability stacking for fold_01 is:

`p_fused = sigmoid(-3.4435794011917382 + 3.1595261006182307 * p_visual + 6.2215756855005768 * p_sensor)`.

The coefficients are fixed across assessment actions. They are not causal percentages or sample-dependent reliability weights. All three decision thresholds are 0.5. Complete declared image absence would return the calibrated sensor branch; complete declared sensor absence would return the calibrated visual branch. These fallback cases remain unexecuted and are separate from the F2 function for present inputs.

The immutable component paths/hashes and exact fit memberships are in [selected_model.json](selected_model.json) and the referenced fit manifests. New corruption inference is forbidden until every selected clean row passes the original absolute probability tolerance 1e-5. Full repaired replay and all 50 corruption/absence realizations are still pending.

Selection evidence: [directly identified saved clean predictions](clean_predictions/frozen_16_frames.csv), [comparison](clean_comparison.csv), [per-fold metrics](clean_per_fold_metrics.csv). Development exposure and one-fold coverage prevent a claim of independent or completed architecture comparison.
