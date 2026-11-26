# Fit-boundary stop and completed-result analysis

This administrative run implements the researcher's 24 November 2026 instruction
to finish the active FULL20 seed42 outer0_inner2 fit, start no further CNN fits,
and analyse the completed work within three hours after that fit completes.
The exact instruction and process identities are in `CONTROL_REQUEST.json`.

`boundary_guard.py` holds the nonblocking `FIT.lock` for the next scheduled
fit, seed42 outer1_final. The guard created that otherwise absent directory
containing only the lock. It is not a scientific training attempt. The original
controller checks that lock before creating the next configuration, model or
checkpoint; contention ends the controller's loop and cannot skip to later fits.
The original controller may record this deliberate contention as `FAILED`.
`STOP_RECEIPT.json` identifies it as an administrative stop rather than a model
or scientific failure. Frozen source, configurations and existing models remain
unchanged by this administrative mechanism.

The guard validates the completed20-epoch history and prediction/history hashes,
waits for the training controller to exit, lets the existing watcher finish its
safe assessment, and runs the original `evaluate` command with CPU-only device
visibility. Its shared deadline is the current fit receipt's completion time
plus10800 seconds. No new CNN fit, robustness inference or parameter search is
launched. The permitted downstream F2 fit retains its complete three-inner OOF
gate and training-side fitting roles; missing folds/seeds are never replaced
with in-sample probabilities.

`analyze_completed.py` independently recomputes AP for each native class,
both-class macro AP, AUROC, Brier score and log loss from saved probabilities.
It also independently implements paired task-bootstrap macro-AP intervals for
the full-CNN comparisons using scikit-learn's weighted AP. It does not load a
model, feature bank, original video or numerical payload. Saved-score checking
does not reproduce training. Its reports retain the incomplete original matrix,
single-fold FULL20 limitation, single-bank100-epoch pilot, conditional uncertainty
and unverified session/operator independence.

The researcher-requested approximately 47 additional GPU days is an inferred
planning allowance for the unexecuted matrix on the current T4. The measured-rate,
split-weighted central estimate from the preceding audit was approximately 43
days. Neither estimate is elapsed runtime or a negative model result.

## Records

- `GUARD_STATUS.json`: current administrative stage, including the guard identity.
- `STOP_RECEIPT.json`: appears only after the authorized controller stops.
- `FINAL_STATUS.json`: analysis exits, elapsed time and three-hour limit outcome.
- `initial_analysis/`: checks and table before the last fit completes.
- `completed_scope_analysis/`: final checks, result analysis and training table.
- `before_stop/`, `after_training_stop/`, `final_evidence/`: report/metric snapshots.
- `README_before_stop.md`: preserved study README before the scope amendment.

The six synthetic guard tests verify lock exclusion before any new fit write,
PID-reuse rejection, signal identity checking, incomplete-fit rejection and
deadline enforcement on only the guard's own analysis child. Two independent
metric tests cover known AP values and paired identical-score intervals. All
tests use tiny synthetic fixtures. The
initial analysis independently checked972 scalar metrics and two paired
bootstrap intervals; the final pass must record its actual counts separately.

Do not restart the original training lane or release the guard while the
authorized controller remains alive. A new researcher instruction is required
for any further training. No commit or push is performed by this administrative
run. Runtime logs and lock files remain ignored; original checkpoints and
scientific prediction artifacts are retained in their existing study locations.
