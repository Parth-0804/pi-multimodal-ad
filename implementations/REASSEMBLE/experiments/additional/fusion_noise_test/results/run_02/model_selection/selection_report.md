# Clean model selection — locked before noise

Selected `frozen_16_frames`: the canonical original-representation, frozen 16-frame F2 pipeline. Clean fused AP is 0.307928835369, equal to reference AP 0.307928835369; improvement over reference is +0. The eligible encoder candidate scored lower, so the predeclared rule retained F2.

| Candidate | Eligible | Clean fused AP | Δ reference / exclusion |
| --- | --- | --- | --- |
| frozen_16_frames | True | 0.307929 | 0.000000 |
| fine_tuned_16_frames | False | NOT_TESTED | Zero complete usable folds |
| frozen_32_frames | False | NOT_TESTED | Zero complete usable folds |
| fine_tuned_32_frames | False | NOT_TESTED | Zero complete usable folds |
| cnn_plus_encoder | True | 0.291898 | -0.016030 |

PARTIAL_COVERAGE_PILOT: exactly fold_01, 753 actions, 77 failures, 26 recordings. The encoder comparison completed five paired folds, but the canonical first-study reference has only one complete eligible fold. The fixed intersection therefore remains one whole fold. The incomplete fine-tuned and 32-frame variants have zero usable folds. The separate paused two-epoch amendment was not substituted for the pinned five-epoch comparison. cnn_only is a reference alias/replicate, not an additional candidate chosen by score.

The canonical source is `parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01`. Encoder results come from `00_experiments/rt_detr_encoder_comparison/results/run_01`. Eligibility used direct keys, identical labels and complete-fold rows, compatible memberships/fitting policy, and traceable replayable components before ranking. The unrounded pooled clean fused AP rule used tolerance 1e-12; visual-only AP and corrupted results played no part. The reference was retained because no eligible newer candidate exceeded it. The encoder-minus-reference pilot interval is in `clean_comparison.csv`; numerical selection is not a significance claim.

The user explicitly authorized this new pre-noise selection after encoder completion. The original run_01 lock is preserved, and no corrupted assessment predictions existed when run_02 was locked. See `selected_model.json`, `selection_lock.json`, `selected_fold_components.json`, and `../provenance/pre_noise_lock_observation.json`. Actual per-fold fits, coefficients and thresholds are retained by identity. The earlier partial pilot was not silently rewritten.

Direct clean evidence: `clean_predictions/frozen_16_frames.csv` and `clean_predictions/cnn_plus_encoder.csv`. These upstream selection tables are distinct from newly replayed `../predictions/clean/clean/repeat_00/fold_01/predictions.csv`.

DEVELOPMENT-EXPOSED and exploratory: selecting from observed outer scores does not create an untouched test set. The 2,000 recording-cluster bootstrap resamples (seed 314159) describe conditional uncertainty for this fitted model, these 26 recordings and the three fixed perturbation realizations. They omit selection and repeated-training uncertainty; secondary intervals are unadjusted. Equal named severity levels across modalities have different units. Only the selected F2 pipeline was tested under faults, so no relative robustness claim against discarded candidates is supported. This complete-action classification study does not establish online detection, causality, adaptive fusion or deployment robustness.

Evidence checked: directly identified clean predictions, eligibility/component records, locked selection and complete clean replay. Still uncertain: untested candidates and full-coverage winner selection. Defensible conclusion: retain the original F2 on the eligible common fold under the fixed rule.
