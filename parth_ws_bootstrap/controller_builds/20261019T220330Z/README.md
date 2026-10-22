# Parth WS offline controller bootstrap

Standalone standard-library runner, synthetic tests and a disabled live Codex adapter. No scientific project files are imported. All writes stay under this build. Start with SETUP_RESULT.md and USER_DECISIONS.md.

From the repository root, the following commands were exercised with the existing interpreter. The commands explicitly use this build's runtime/demo-final, tagged SYNTHETIC_ORCHESTRATION_TEST. The default runtime/demo is preserved pre-repair evidence; its old code binding correctly fails current resume checks. Status and preview inspect state without dispatch; resume dispatches only pending registered fake work after revalidation; stop affects only this runtime.

```bash
ma_thesis_env/bin/python -I -B parth_ws_bootstrap/controller_builds/20261019T220330Z/runner/controller.py status --root parth_ws_bootstrap/controller_builds/20261019T220330Z/runtime/demo-final
ma_thesis_env/bin/python -I -B parth_ws_bootstrap/controller_builds/20261019T220330Z/runner/controller.py preview --root parth_ws_bootstrap/controller_builds/20261019T220330Z/runtime/demo-final
ma_thesis_env/bin/python -I -B parth_ws_bootstrap/controller_builds/20261019T220330Z/runner/controller.py resume --root parth_ws_bootstrap/controller_builds/20261019T220330Z/runtime/demo-final
ma_thesis_env/bin/python -I -B parth_ws_bootstrap/controller_builds/20261019T220330Z/runner/controller.py stop --root parth_ws_bootstrap/controller_builds/20261019T220330Z/runtime/demo-final
ma_thesis_env/bin/python -I -B parth_ws_bootstrap/controller_builds/20261019T220330Z/runner/controller.py resume --clear-stop --root parth_ws_bootstrap/controller_builds/20261019T220330Z/runtime/demo-final
ma_thesis_env/bin/python -I -B parth_ws_bootstrap/controller_builds/20261019T220330Z/runner/controller.py preview --research --root parth_ws_bootstrap/controller_builds/20261019T220330Z/runtime/demo-final
```

The complete demo already ran: prepare -> implement (valid negative fixture) -> handoff, each with a separate fake evidence-review process. Repeating resume does not rerun completed jobs. To create another synthetic runtime, use `prepare-demo --root parth_ws_bootstrap/controller_builds/20261019T220330Z/runtime/<new-name>`, followed by the same --root on commands. Existing runtimes are never overwritten. Angle-bracket names are instructions to choose a new name, not a tested literal path.

Run only the new controller suite:

```bash
ma_thesis_env/bin/python -I -B parth_ws_bootstrap/controller_builds/20261019T220330Z/tests/test_controller.py
```

This test file explicitly loads its own unittest class. It does not discover repository tests/conftest, load scientific packages/models or make network/model requests. Test working directories and failing evidence are retained inside evidence/test_work. Tests use separate fixture state, never the real research queue.

Runtime files: workflow.json (synthetic definition), fixture_authorization.json (public-keyed synthetic fixture only), .controller/events.jsonl (fsynced hash-chained write-ahead state), .controller/state.json (atomic cache), .controller/progress.json (teaching handoff), work/<task>/attempt<n>/ (outputs, stdout/stderr, exact argv/cwd/exit/time/receipt hashes). A zero exit or DONE response alone never completes a task. Evidence must pass identity/hash/validity checks plus the separate fake review. Negative results pass; invalid high scores fail.

Dependency-first scheduling is independent of task-list order. Resume invalidates progression trust transitively when upstream evidence fails; retained artifacts are preserved. Current on-disk config, not only the cached object, is checked before dispatch. The coordinator is serialized with an actual flock. A separate control lock serializes stop with launch; active owned child process groups receive TERM then KILL if needed. An interrupted RUNNING attempt becomes NEEDS_RECONCILIATION; it is not automatically replayed. A partial journal is preserved and refused. Resume revalidates synthetic authority, source/config/input identities and completed artifacts/reviews. The journal repairs stale snapshot interpretation without trusting an agent-edited DONE cache. Unknown jobs/PIDs are never killed as a shortcut. Reconciliation of uncertain work requires evidence and a later explicit recovery decision; there is no unsafe reset command.

Limits are mandatory. Every dispatch (including review, fork intent and failures) consumes a dispatch reservation and full child timeout reservation before launch. Measured child elapsed time is logged separately. A timeout includes polling/termination overhead; reserved child seconds are not a certified host-wide CPU/GPU/money limit. Only registered idempotent synthetic technical failures (exit75 or timeout) can retry, at most twice; no score-driven retries. Output capture is polled and capped with bounded polling overshoot, not a hard filesystem quota. Partial stdout/stderr is retained. No monetary accuracy is claimed.

Path/argument/policy checks are application-level tests; they do not sandbox a hostile process or close all symlink race windows. Fake workers are fixed, locally trusted fixtures. They share the OS user and could reach controller/authority files if rewritten maliciously. Their synthetic HMAC key is intentionally public, not a credential or protected authorization service. No fake approval can activate a live task.

## Live activation procedure — unavailable until prerequisites exist

Current checked behavior:

```bash
ma_thesis_env/bin/python -I -B parth_ws_bootstrap/controller_builds/20261019T220330Z/runner/controller.py activate --scope LITERATURE --root parth_ws_bootstrap/controller_builds/20261019T220330Z/runtime/demo-final
```

This returns exit2/LIVE_DISABLED, as observed in CLI_SMOKE_FINAL.json. It does not launch anything and is not a one-command research launcher. There is no JSON flag or chmod step that enables it.

Later activation must show the user: exact LITERATURE-only task IDs/operation; finalized literature protocol version/digest; results-neutral input digest; allowed public access/output paths; explicit wall-time/model/provider/spend/storage/retry limits; review requirement; and the host-owned approval/launcher identity. Every currently unset value must be decided and checked before an explicit user confirmation. Scientific protocol/datasets/experiments remain separately gated.

Before implementing a live handler, a separately authorized host integration must make controller code, policy and approval source inaccessible to worker writes and give the literature worker access only to the clean assignment and its output area. The same-user shared repository cannot establish those guarantees. Read-only Codex sandbox flags alone do not establish results blindness or protect all controller/credential state. No accounts, permissions, services or global configuration were changed here. Do not edit CodexAdapter.execute to bypass this boundary.

Installed interface: codex-cli0.162.0-alpha.17.2; exec help exposes --sandbox/--json/--output-schema/--output-last-message/-C/--model/stdin. Only version/help were invoked. The typed builder prepares these arguments without executing them. Official references: [CLI reference](https://learn.chatgpt.com/docs/cli/reference), [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode). No account, subscription, remote service or model availability was inferred.
