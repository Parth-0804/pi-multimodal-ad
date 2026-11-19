# WAITING_FOR_GPU

Selected frozen_16_frames; saved clean fused AP 0.307928835369, reference 0.307928835369, difference +0. Coverage: PARTIAL_COVERAGE_PILOT on 1 folds and 753 rows.

Clean replay, strongest predefined image-noise AP and strongest predefined sensor-noise AP: NOT_RUN. Paired drops and uncertainty are not computable.

Stage: WAITING_FOR_GPU. Blocker: Upstream work is not terminal or allocated GPU remains owned; no selection or corrupted inference permitted.. Upstream status: {'visual': {'status': 'BLOCKED', 'full_visual_fits_completed': 6, 'completed_paired_folds': None, 'background_worker': None, 'queued': None}, 'encoder': {'status': 'WAITING_FOR_GPU', 'full_visual_fits_completed': None, 'completed_paired_folds': 0, 'background_worker': False, 'queued': False}}. No background job or scheduled continuation exists.

Technical replay repair 01: initial clean replay stopped after 61 passing rows; no corrupted assessment predictions had been generated. The sensor adapter incorrectly promoted float32 statistics to float64. The repaired adapter preserves the original float32 reduction path and exactly reproduces the failed row’s saved features and sensor probability. Visual mean pooling and standardization also now use the original Torch arithmetic. A failing-then-passing regression test is retained. The selection lock, fitted components, frame count, corruption configuration and 1e-5 tolerance are unchanged. Original and repaired source hashes are recorded in provenance/replay_repair_01/approved_revision.json. Full repaired clean replay remains PENDING; this repair is not proof that all clean rows pass.

No completed newly replayed clean or corrupted prediction table exists. Directly identified upstream selection evidence is model_selection/clean_predictions/frozen_16_frames.csv; partial clean frame caches are not claimed as a completed prediction bank.

- [Selection report](model_selection/selection_report.md)
- [Clean comparison](model_selection/clean_comparison.csv)
- [Results summary](comparison/RESULTS_SUMMARY.md)
- [Progress](progress.json), [resume](how_to_resume.md), [review package](REVIEW_PACKAGE.zip)

All work stays inside this study. No selected_model.json is created until valid one-time selection. Unranked inherited predictions are not newly replayed or corrupted predictions.


**Execution is incomplete.** The ten-minute foreground wait ended while a separate training run occupied the sole GPU. Fifteen CPU tests pass. Initial clean inference passed 61 rows, then stopped; a documented float32 reconstruction repair passes regression tests and exactly fixes the failed sensor row, but full repaired replay is still pending. No corrupted assessment predictions were generated.

[Directly identified saved clean selection predictions](model_selection/clean_predictions/frozen_16_frames.csv) support independent recalculation of AP. They are not newly replayed clean or corrupted predictions. See the [exact formulation](model_selection/locked_formulation.md), [self-review](checks/self_review.md), and [supported resume command](how_to_resume.md). No continuation is queued.
