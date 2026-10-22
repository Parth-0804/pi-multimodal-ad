# Selected-model robustness — WAITING_FOR_GPU

Selected frozen_16_frames; saved clean fused AP 0.307928835369, reference 0.307928835369, difference +0. Coverage: PARTIAL_COVERAGE_PILOT on 1 folds and 753 rows.

Clean replay, strongest predefined image-noise AP and strongest predefined sensor-noise AP: NOT_RUN. Paired drops and uncertainty are not computable.

| Candidate | Available folds | Clean fused AP | Status / reason |
|---|---|---|---|
| frozen_16_frames | fold_01 | 0.3079288353686113 |  |
| fine_tuned_16_frames |  |  | Zero complete usable folds |
| frozen_32_frames |  |  | Zero complete usable folds |
| fine_tuned_32_frames |  |  | Zero complete usable folds |
| cnn_plus_encoder |  |  | Zero complete usable folds |

## What ran and what did not

Inspect checks for actual synthetic tests, processor checks, component verification and runtime replay. An implemented transform is not an executed corruption study. No predictor training, recalibration, threshold tuning or historical Task4 work is permitted.

Stage: WAITING_FOR_GPU. Blocker: Upstream work is not terminal or allocated GPU remains owned; no selection or corrupted inference permitted.. Upstream status: {'visual': {'status': 'BLOCKED', 'full_visual_fits_completed': 6, 'completed_paired_folds': None, 'background_worker': None, 'queued': None}, 'encoder': {'status': 'WAITING_FOR_GPU', 'full_visual_fits_completed': None, 'completed_paired_folds': 0, 'background_worker': False, 'queued': False}}. No background job or scheduled continuation exists.

Technical replay repair 01: initial clean replay stopped after 61 passing rows; no corrupted assessment predictions had been generated. The sensor adapter incorrectly promoted float32 statistics to float64. The repaired adapter preserves the original float32 reduction path and exactly reproduces the failed row’s saved features and sensor probability. Visual mean pooling and standardization also now use the original Torch arithmetic. A failing-then-passing regression test is retained. The selection lock, fitted components, frame count, corruption configuration and 1e-5 tolerance are unchanged. Original and repaired source hashes are recorded in provenance/replay_repair_01/approved_revision.json. Full repaired clean replay remains PENDING; this repair is not proof that all clean rows pass.

No completed newly replayed clean or corrupted prediction table exists. Directly identified upstream selection evidence is model_selection/clean_predictions/frozen_16_frames.csv; partial clean frame caches are not claimed as a completed prediction bank.

## Interpretation

Until matched noisy predictions exist, image-versus-sensor sensitivity, harmful fusion and robustness are unknown. Full absence uses a separately declared sensor-only or visual-only fallback; noisy-but-present inputs keep the saved F2. Both absent must abstain. A winning newer model would be the only fusion pipeline evaluated under noise; discarded F2/candidates would remain clean-selection evidence only.

The primary fault summaries are strongest prescribed image Gaussian sigma0.10 and sensor Gaussian alpha1.00, with means of three separately computed AP values. No worst-observed severity is substituted. AP drops are clean minus corrupted. Paired bootstrap clusters recordings, preserving all rows and averaging metrics across fixed realizations. Equal severity labels across modalities are not equivalent physical faults. This is exposed-data exploratory analysis, not untouched generalization, causality or a claim about adaptive fusion.

## Teaching chain

Clean results -> eligibility and whole-fold coverage -> candidate selection -> lock frozen selected pipeline -> one-modality raw-input perturbation -> branch/F2 predictions -> matched metrics -> bounded conclusion.

## Review artifacts and next decision

The package contains source/tests/config, exact cohort/frame/fit manifests, copied completed upstream prediction tables clearly marked unranked where appropriate, and any actually executed noise predictions. It cannot recalculate nonexistent results. Model blobs/raw inputs are excluded and referenced by hashes.

Recommended next decision: resume this same evaluation once the predecessor runs reach a stable terminal state and the allocated GPU is free, within the original deadline; a later budget needs explicit authorization. Do not resume upstream training from this task.

Evidence checked: distinguish recorded source and synthetic checks from upstream execution. Still uncertain: any unexecuted model selection, full clean replay and fault metrics. Defensible conclusion: no selected-model robustness result yet.


## Actual execution at this safe stop

Status: **WAITING_FOR_GPU; robustness study incomplete.** The ten-minute foreground resume wait ended without acquiring the allocated GPU. No worker or scheduled continuation remains. A separate visual-backbone two-epoch training run owns the device; it was not interrupted, modified, or substituted into the pinned five-epoch comparison.

| Evidence / endpoint | Fused failure AP | Coverage |
|---|---:|---|
| Saved clean canonical F2, retained selection | 0.30792883536861149 | fold_01: 753 actions, 26 recordings, 77 failures |
| Newly replayed full clean bank | Not completed | Initial replay passed 61 rows before a numerical adapter failure |
| Strong image Gaussian noise, sigma 0.10 | Not run | No corrupted assessment predictions |
| Strong sensor Gaussian noise, alpha 1.00 | Not run | No corrupted assessment predictions |

The original-representation F2 is retained with zero improvement over itself. Fine-tuned 16 frames, frozen 32 frames, fine-tuned 32 frames, and cnn_plus_encoder each have zero complete eligible outer folds. Their absence is not evidence of inferiority. This is a **PARTIAL_COVERAGE_PILOT**, not a completed five-fold architecture comparison.

The first replay's 61 passing probability rows were held in memory and not persisted before the assertion; surviving frame caches identify the rows, but are not presented as a completed prediction table. The repaired failure path now preserves partial probabilities and discrepancies. The sensor precision defect is corrected and the failed row exactly matches its saved sensor features/probability, but full repaired replay remains unverified. The original 1e-5 probability tolerance and model/configuration locks are unchanged.

[Exact locked formulation](../model_selection/locked_formulation.md), [direct clean selection predictions](../model_selection/clean_predictions/frozen_16_frames.csv), [per-fold clean AP](../model_selection/clean_per_fold_metrics.csv), and [self-review including evidence limitations](../checks/self_review.md) distinguish source inspection, upstream stored execution, recomputed selection metrics, synthetic tests, and partial live inference. All 15 focused CPU tests pass; repository diff hygiene and installed-environment dependency checks passed. No new fitting or corruption-aware adaptation occurred.

Image-versus-sensor fault sensitivity, harmful fusion, known-absence fallback performance, paired AP drops, and robustness uncertainty are **unmeasured**. Fallback is specified but has not executed. Selecting on observed outer predictions is DEVELOPMENT-EXPOSED; neither one-fold coverage nor bootstrap intervals establish independent validation.

**One recommended next decision:** resume this same locked pilot when the allocated GPU is free, within the original deadline. The supported command is in [how_to_resume.md](../how_to_resume.md). Do not reselect, retrain, append newly completed folds, or launch another study. If the original deadline has passed, a new time authorization is required; no restart is queued.

Evidence checked: identified saved clean probabilities, recomputed AP, fixed component hashes, focused CPU tests, partial runtime replay, and the precision regression. Still uncertain: full repaired replay and all fault/absence outcomes. Defensible conclusion: original F2 is the only selectable completed-fold pipeline in this pilot; no robustness conclusion is yet supported.
