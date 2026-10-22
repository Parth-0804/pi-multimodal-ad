# Observed offline coverage

Source: tests/test_controller.py, evidence/TEST_SUMMARY.json and exact logs. Initial28 checks had2 direct-CLI import failures; repair1/rerun passed28. Final setup repair2 added three failing-then-passing regressions for unordered DAGs, transitive invalidation and current config drift. Full final suite:31 passed,0 failures/errors in13.287s. Both allowed repair cycles are used; no further automatic repair is authorized.

| Required area | Targeted checks | Scope |
|---|---|---|
| Dependency/review progression and no duplicates |01|Fixed subprocess workers and separate evidence-reading fake reviewers|
| Missing/malformed/revoked/mismatched/forged auth |02–06|Synthetic binding/signature simulation only; public fixture key is not a live trust boundary|
| Blocked DAG, budgets, excluded handlers |07–08,15–16|Strict registered synthetic handlers; every research handler unavailable|
| Fabricated DONE, missing/hash-invalid output, review failure |09–10|Actual retained JSON/hash/input/validity checks|
| Timeouts/nonzero/malformed/retry budgets |11–16|Actual owned child timeouts; dispatch/time reservations include failures|
| Interrupted/resume/concurrent/stop |17–22|Journal crash injection plus actual OS flock/child termination; not production job reattachment|
| Paths/symlinks/args/policy |23–24|Application-level refusal checks, not hostile-worker OS sandbox tests|
| Negative vs invalid high score |25|Synthetic validity independent of score direction|
| Live boundary, unattended fake handoff, research queue unchanged |01,26–27|No model request, real connection or research status transition|
| JSON ambiguity/config drift |28|Duplicate keys/nonfinite values rejected; sealed config identity checked|

Test byte captures are polled limits with bounded scheduling/termination overshoot. File/path validation does not prove OS-denied access by an adversarial worker. Money/GPU/host-wide resource enforcement and fresh-results isolation remain live integration prerequisites, not successes of this suite.

Additional regression coverage29–31 checks unordered valid DAG progression, multi-level downstream invalidation/no additional dispatch, and an on-disk config edit after coordinator construction. Pre-repair failures are preserved in repair_cycle02/regressions_before.txt.
