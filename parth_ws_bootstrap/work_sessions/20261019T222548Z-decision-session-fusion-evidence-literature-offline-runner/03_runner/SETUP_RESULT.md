# Offline runner setup result

DONE_WITHIN_SCOPE. Reused the compatible completed build by byte-identical copy, without changing the old build or scientific files. REUSE_PROVENANCE.json records every copied source/schema/config digest. Three runner files and the original31-test suite are unchanged; two session-specific no-work tests were added. No new production handler or live connection exists.

Observed validation:31 original checks plus2 new no-work checks passed, zero failures/errors. The original suite measured 11.584s; wrapper times were 11.660s and 1.230s. Ten explicit CLI checks passed, including six fake dispatches for a three-task handoff, duplicate-free completed resume, stop/explicit resume, read-only historical queue preview, and activation refusal with exit 2 LIVE_DISABLED. Exact argument arrays, output files and outcomes are in TEST_RESULTS.json and evidence/CLI_CHECKS.json. Tests use standard-library fake processes, OS flock, hash checks and synthetic JSON; no scientific repository tests or modules were imported.

The copied implementation has task/DAG/output contracts; separate execution/evidence/authorization status; atomic snapshots and fsynced hash-chain event log; writer/control locks; input/code/config/fixture-authorization identity checks; registered argument arrays; bounded timeout/retry/dispatch/output reservations; stop and conservative interrupted resume; actual artifact/review validation. A valid synthetic negative passes while an invalid high-score fixture fails. A public test signature is deliberately not a credential or real approval.

Session repair cycles used0. Both repair cycles used by the earlier completed build remain historical evidence; no further general framework development was attempted. All new state/fixtures live under this03_runner. No synthetic success updates SESSION_STATE's scientific authorization or the read-only legacy queue.

## Commands and observed behavior

Run from the repository root. Set this task-specific shell variable (no installation):

```bash
TASK_RUNNER=parth_ws_bootstrap/work_sessions/20261019T222548Z-decision-session-fusion-evidence-literature-offline-runner/03_runner
```

These exact command forms were tested against the retained completed demo:

```bash
ma_thesis_env/bin/python -I -B "$TASK_RUNNER/runner/controller.py" status --root "$TASK_RUNNER/runtime/fusion-workflow-synthetic-handoff"
ma_thesis_env/bin/python -I -B "$TASK_RUNNER/runner/controller.py" preview --root "$TASK_RUNNER/runtime/fusion-workflow-synthetic-handoff"
ma_thesis_env/bin/python -I -B "$TASK_RUNNER/runner/controller.py" resume --root "$TASK_RUNNER/runtime/fusion-workflow-synthetic-handoff"
ma_thesis_env/bin/python -I -B "$TASK_RUNNER/runner/controller.py" stop --root "$TASK_RUNNER/runtime/fusion-workflow-synthetic-handoff"
ma_thesis_env/bin/python -I -B "$TASK_RUNNER/runner/controller.py" resume --clear-stop --root "$TASK_RUNNER/runtime/fusion-workflow-synthetic-handoff"
```

Status displays durable state; preview checks configuration/input authority but is not a full completed-artifact integrity certificate. Resume revalidates completed artifacts and dependency trust before progression; interrupted RUNNING work is not replayed automatically. Stop writes a marker for this synthetic runtime only; it never targets an arbitrary historical PID.

To repeat a new demo, choose a previously absent child name, e.g. runtime/review-demo-02, then use prepare-demo, preview, run and resume with that same --root. prepare-demo refuses an existing directory. The retained demo is already DONE; resume is a no-new-dispatch check. Do not overwrite evidence or run another full suite merely to consume time.

Observed test commands (new files only):

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 ma_thesis_env/bin/python -I -B "$TASK_RUNNER/tests/test_controller.py"
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 ma_thesis_env/bin/python -I -B "$TASK_RUNNER/tests/test_session_no_work.py"
```

Each suite creates fresh tiny synthetic case directories under evidence/test_work. Repeating the copied suite rewrites its own TEST_SUMMARY.json, so preserved session evidence should be copied to a newly approved review namespace before any later repeat. Test-generated symlinks are never followed by packaging/preservation code.

The config/derived_queue.json is a byte-identical HISTORICAL proposed queue for read-only preview/test isolation, not this session's authorization or completion state. Actual current task state is ../00_control/SESSION_STATE.json. Keep old literature-waiting flags historical rather than editing them to imitate approval.

## Limits

LIVE_READINESS.md distinguishes implemented, tested, untested and blocked. Host protection against same-privilege workers has not been established. Path/symlink checks are application-level and not race-proof confinement against hostile workers. Time reservations/output polling have termination/measurement overshoot; quotas are not OS-wide CPU/GPU/RAM/disk or money enforcement. No model-backed CLI/API, external service, new account, package install, scientific run or scheduled continuation occurred.

Evidence checked: copied actual code,33 observed passing offline tests,10 explicit CLI outcomes and copied-source hashes.
Still uncertain: live authority/trust/results isolation, real research handlers and budgets.
Defensible conclusion: a useful offline handoff runner is available; successful fake work is not research approval.
