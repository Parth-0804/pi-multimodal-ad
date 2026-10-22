# Model selection — WAITING_FOR_GPU

Selected frozen_16_frames; saved clean fused AP 0.307928835369, reference 0.307928835369, difference +0. Coverage: PARTIAL_COVERAGE_PILOT on 1 folds and 753 rows.

| Candidate | Available folds | Clean fused AP | Status / reason |
|---|---|---|---|
| frozen_16_frames | fold_01 | 0.3079288353686113 |  |
| fine_tuned_16_frames |  |  | Zero complete usable folds |
| frozen_32_frames |  |  | Zero complete usable folds |
| fine_tuned_32_frames |  |  | Zero complete usable folds |
| cnn_plus_encoder |  |  | Zero complete usable folds |

The canonical reference is the matched first-study frozen_16_frames F2, not historical anonymous scores. cnn_only is an alias/replicate, never an extra winner chosen for a favorable score. Eligibility, exact fold rows, component hashes, G/C/T/E and inner-OOF coverage are checked before ranking. While upstream work is active, completed immutable prediction tables may be copied as UNRANKED evidence; this does not authorize a premature partial pilot.

Stage: WAITING_FOR_GPU. Blocker: Upstream work is not terminal or allocated GPU remains owned; no selection or corrupted inference permitted.. Upstream status: {'visual': {'status': 'BLOCKED', 'full_visual_fits_completed': 6, 'completed_paired_folds': None, 'background_worker': None, 'queued': None}, 'encoder': {'status': 'WAITING_FOR_GPU', 'full_visual_fits_completed': None, 'completed_paired_folds': 0, 'background_worker': False, 'queued': False}}. No background job or scheduled continuation exists.

Technical replay repair 01: initial clean replay stopped after 61 passing rows; no corrupted assessment predictions had been generated. The sensor adapter incorrectly promoted float32 statistics to float64. The repaired adapter preserves the original float32 reduction path and exactly reproduces the failed row’s saved features and sensor probability. Visual mean pooling and standardization also now use the original Torch arithmetic. A failing-then-passing regression test is retained. The selection lock, fitted components, frame count, corruption configuration and 1e-5 tolerance are unchanged. Original and repaired source hashes are recorded in provenance/replay_repair_01/approved_revision.json. Full repaired clean replay remains PENDING; this repair is not proof that all clean rows pass.

No completed newly replayed clean or corrupted prediction table exists. Directly identified upstream selection evidence is model_selection/clean_predictions/frozen_16_frames.csv; partial clean frame caches are not claimed as a completed prediction bank.

Selection, when eligible, uses pooled failure-class clean fused AP with tolerance1e-12 and the fixed tie rules. Clean candidate tables are retained under clean_predictions after selection; preliminary copies are under unranked_upstream_predictions. An absent selected_model.json means no lock and no authorized corrupted assessment inference. DEVELOPMENT-EXPOSED: a winner selected on these outer predictions is not independently confirmed, and intervals do not undo selection.


See [the exact locked formulation](locked_formulation.md), [identified saved clean predictions](clean_predictions/frozen_16_frames.csv), and [per-fold recalculation](clean_per_fold_metrics.csv). The reference was retained because every newer variant has zero usable completed outer folds. It did not win a completed head-to-head comparison. The full repaired replay remains pending on GPU availability. No new corrupted assessment predictions exist.
