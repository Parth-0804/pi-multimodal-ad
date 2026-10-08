# Sensor-only recovery attempt

User asked to start work while deferring a decision on visual work. Experimental Task 1 is visual: its frozen-feature comparisons are complete and V-FT remains deferred. Only unfinished experimental Task 2 is launched. An asynchronous clarification about the task numbering remains pending.

Preflight read 869 sensor fit/branch metadata files, verified 807 checkpoint and 869 prediction hashes, and found no orphan .pt files. 657 strict-hybrid fits were complete; first two outer folds already complete. Approximately 2–4 hours remain; this is a throughput estimate, not a deadline or budget change.

Recovery corrections: completed hybrid outer folds previously would have been recomputed/re-serialized on restarting the driver. The new guard validates saved row order/probabilities/threshold decisions and reuses them without writing. Reporting now accepts a new sensor-only output directory, preserving prior reports and tables. neural.py, models.py and the scientific configuration are unchanged. This is resumption of the same bounded computation, not a new experiment or expanded budget.

The filesystem apply_patch helper failed twice at sandbox initialization, before any files were written. Equivalent scoped edits were applied with Python under the approved repository-write execution path. All nine existing extension tests and three fold-recovery tests passed (12); the additional daily-deadline test and three recovery tests passed (4). pip check and git diff --check passed. Tracked source diff: two files, 15 insertions, 5 deletions; new source/helper/test files are recorded in the attempt snapshot.

Only one GPU process is launched. Torch threads remain 4; OPENBLAS_NUM_THREADS=16, OMP_NUM_THREADS=4, MKL_NUM_THREADS=4. The config's BLAS setting is 16. Complete original sensor fits act as short recovery units (observed mean approximately 13.8 seconds); no mid-fit optimizer recovery is claimed. The wrapper checks the 05:50 Europe/Berlin stop deadline before each new fit/replay. No automatic post-reboot restart, visual fine-tuning, corruption worker, full supervisor, new architecture or extra scientific budget is launched.

Outputs: worker.log, preflight.json, status.json; source snapshot and source_changes.diff; report/ after completion, plus completion_manifest.json after protected-file verification. Main mutable handoff: reports/CURRENT_EXECUTION.md.
