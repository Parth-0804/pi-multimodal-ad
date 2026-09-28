# Extension execution queue — live continuation

Root: `runs/reassemble/additional_improvements_executed/20260928T000346Z`.
Protocol commit `26ae3a7`; initial implementation + completed Task3 commit `484bd35`.
User confirmed **no additional wall-time limit; use fixed plan bounds**.
Original study and external master Reasoning Record remain immutable.

## Current jobs (check processes and logs before starting anything)

- GPU per-frame extraction: `python -B -m reassemble.additional_improvements.visual_features`;
  log `01_temporal_visual/extraction.log`. Tool session 84775.
- GPU sensor controls: `python -B -m reassemble.additional_improvements.unimodal --task 2`;
  log `02_patchtst_training_budget/execution.log`. Tool session 33834.
- These two concurrent jobs were explicitly justified by the saved
  `00_protocol_and_preservation/parallel_resource_audit.json`: synthetic PatchTST
  batch128 peak 0.55GiB; total observed GPU use ~3.4GiB. Later GPU work serial.
- Task3 completed on CPU. Final report
  `03_STATIC_ANCHORED_ADAPTATION_RESULTS.md`; all three controls, paired intervals,
  curves, per-seed/fold results, ablations and coefficients saved. AP gain .0210,
  marginal 95% [.0015,.0419], exploratory only. Do not overwrite completed fits.

## Remaining execution

All commands use `PYTHONPATH=src ma_thesis_env/bin/python -B -m
reassemble.additional_improvements.<module>` from repository root.

1. Wait for extraction and sensor-control jobs; inspect exit codes and logs.
2. Validate remaining code with new synthetic tests (Task4 train-only scaling,
   corruption namespaces already tested). Run original repository validation.
3. `unimodal --task 1`: matched V-MEAN/V-TEMP/V-NOPOS. No outer-label selection.
4. `finetune`: synthetic gradient/memory audit, then V-FT from V-TEMP checkpoints,
   pixel-based final-stage adaptation, fixed20/patience5 bounds. This may be long;
   no wall-time limit was imposed. Keep all checkpoints/attempts. No resource
   failure has been established; do not mark it skipped without actual evidence.
5. `hybrid`: strictly nested S-LONG/statistics stacker including deeper crossfits
   for inner stacker thresholds. Potentially many GPU fits, resumable per fit.
6. `branch_banks recover`: reconstruct 105 original branch partition fits, assert
   clean parity and save original calibrator/selection/checkpoint provenance.
7. `corruptions visual`: native-pixel train/validation/test banks, 41 conditions
   (8 train/validation Gaussian, 15 test Gaussian, 3 blur, 15 frame dropout).
8. `branch_banks sensor`: 105 partition-specific raw sensor banks; can distribute
   `--job-index 0..104` across bounded CPU workers after branch recovery. Full
   timestamp streams are required for original global native-rate gap semantics.
9. `branch_banks visual`: score pixel banks with every correct branch checkpoint.
10. `robust_fusion`: CPU matched clean/augmented F2/F6/anchored models with strict
    inner objective and original branch fallback. Source implemented but not yet
    exercised end-to-end on actual banks. Review and test before launch.
11. `robust_report`: per-realization metrics + paired recording/realization
    bootstrap. Implemented; still needs end-to-end validation and learning-curve
    artifacts/historical-reference comparisons.
12. Produce Task1/2 reports and required final three handoffs, compact final
    comparison CSV/JSON/registry/manifest/validation. Preserve original manifests
    and re-run preservation verifier. No combined winner model.

Source names are in `src/reassemble/additional_improvements/`. All neural fits
save source/config signatures, selected checkpoints, predictions, every-epoch
curves and train/assessment row identities. Do not change neural.py/models.py
mid-run: fit signatures intentionally reject silent source changes.

First Task3 attempt failed due decimal penalty filename suffix collision; fixed
before completed contrasts. Original attempt/log retained. No scientific model
was changed. Detailed correction in Task3 folder.

Current limitations to address before final completion: Task4 learning-curve
plots, historical clean references in the new reports, required aggregate
handoffs/manifests, full validation/preservation checks. No task is blocked merely
because it is long. Do not call the whole extension complete while jobs remain.
