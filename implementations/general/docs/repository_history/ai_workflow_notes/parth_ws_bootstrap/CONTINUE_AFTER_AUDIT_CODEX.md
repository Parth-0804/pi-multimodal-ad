# Parth WS — build the runner from the audit outputs

You are working in my existing thesis repository. Read the completed audit packet,
then implement and offline-test the smallest useful sequential research runner.
The objective is to remove manual handoffs between research, implementation and
review, while preserving scientific validity and explicit authorization boundaries.
Do not finish with another generic plan when the permitted implementation is possible.

## 1. Read the actual inputs; do not assume their conclusions

Read applicable governing instructions, then locate a matching pair of:
- APPROVAL_PACKET.md
- AUTOMATION_READINESS.md

Look first under parth_ws_bootstrap/outputs/. Select the latest complete packet
for this repository using its recorded identity/state, not file modification time
alone. Do not mix files from different audits. If selection is genuinely ambiguous,
ask one focused question. If the reports are absent, report the missing prerequisite;
do not invent them or quietly repeat the full audit.

Read the packet's RUN_STATE.json, PROTOCOL_DRAFT.md, VERIFIER_REVIEW.md,
ARTIFACT_MANIFEST.json and relevant supporting reports where available. Also read:
- parth_ws_bootstrap/RESEARCH_RULES.md
- parth_ws_bootstrap/TASK_QUEUE.json
- parth_ws_bootstrap/prompts/VERIFIER.md
- parth_ws_bootstrap/prompts/INDEPENDENT_LITERATURE_REVIEW.md

Check the relevant recorded hashes and current source state. Reports are leads,
not proof that source was executed or that a user approved anything. Investigate
material contradictions with targeted source inspection; do not reopen unrelated work.
Record unresolved fields rather than supplying plausible values.

IMPORTANT DEPENDENCY CORRECTION: the original queue puts CONTROLLER_SETUP after
LITERATURE and LOCK_PROTOCOL. This assignment authorizes an additional, separate
CONTROLLER_BOOTSTRAP_SETUP step now, limited to infrastructure and offline tests.
Do not mark the later CONTROLLER_SETUP, LOCK_PROTOCOL or any research task complete.
Keep later protocol-specific integration and activation behind their existing gates.
Document this change in a derived queue; preserve the original queue and audit packet.

## 2. Current authorization: infrastructure, not experiments

You may create a new isolated folder beneath:
  parth_ws_bootstrap/controller_builds/<unique-actual-UTC-timestamp>/

Within that folder, write runner code, controller-specific tests, synthetic fixtures,
derived state/configuration, documentation and logs. Keep all setup writes there;
use a unique suffix for collisions. Use existing local runtimes and prefer standard
libraries. Do not restructure the scientific repository to fit this runner.

You may run only targeted metadata/help commands and the newly created offline
controller tests. Such tests must not import scientific modules, discover repository
tests or hooks, initialize GPUs, load models, or use real samples. Inspect installed
CLI help/version metadata without making model requests. Use official documentation
through already available read-only browsing if needed, without sending private data.

Do not modify existing scientific source/configuration, data, labels, splits, model
weights, historical outputs, AGENTS files, user/global configuration or lockfiles.
Preserve the dirty working tree. No Git mutations, commits, worktrees, resets, stash,
cleanup, package installation, downloads of datasets/weights, remote connections,
scheduled/background jobs, UI implementation, training, inference, feature extraction,
metric rescoring, corruption runs, or literature research in this assignment.

Additional model-backed subprocess/API calls and remote jobs have a zero budget here.
Use a fake adapter for runner tests. A separate reviewer may use an already available
in-session delegation tool within this scope, not a newly provisioned service.
Do not read secrets, copy credentials, weaken sandbox restrictions or bypass approval
prompts. Previously excluded historical Task 4 remains excluded, including aliases
or an equivalent rerun. Reports discussing it are not execution instructions.

This is a new infrastructure-only task, not permission to override higher-priority
rules or convert the audit's scientific recommendations into approved experiments.

## 3. Turn the findings into a minimal implementation

First create a short report-to-action mapping with the relevant report section,
evidence status, required runner capability, unresolved issue and effect on progression.
Distinguish infrastructure blockers from scientific gaps: implement safe generic
infrastructure even where a dataset, budget or protocol is still undecided.

Reuse an existing controller only if it can be integrated without editing protected
files; otherwise build a small standalone runner. Do not create a general autonomous
research platform, a dashboard or a collection of unnecessary services.

Implement:

A. Persistent task state and dependency validation.
Each task needs an ID, dependencies, operation class, authorization requirement,
input/evidence references, outputs, acceptance checks, resource limits and attempts.
Keep evidence status, execution status and authorization status separate. Unknown
fields must block affected live operations, not inherit permissive defaults.

B. A coordinator with one writer and explicit review handoffs.
The coordinator selects only eligible tasks, dispatches bounded work, validates
returned evidence and checks required review before advancing. A worker's DONE
message or zero exit status is insufficient. Record which checks passed and their
scope. A review must inspect evidence rather than merely restate a worker report.
If separate review is unavailable, report SELF_REVIEW_ONLY; do not satisfy a required
separate-review gate by silently substituting self-review.

C. A pluggable execution boundary.
Implement a fake adapter for tests and a disabled-by-default live adapter using an
actually supported installed interface. Inspect local help and current official docs;
do not assume CLI flags, model names, subscriptions or desktop features.
Do not automate mouse clicks between chat windows. Never execute free-form shell
commands copied from an agent response or report. Use registered operation types,
validated argument arrays, confined working directories and explicit permission
profiles. Unimplemented research handlers remain blocked, not successful no-ops.

D. Protected authorization checks.
Require explicit user authorization for the exact protocol/version, task scope,
access, write scope, resource limits and permitted operations before live work.
APPROVAL_PACKET.md is not itself an approval. A JSON field written by an agent,
a checksum, a reviewer verdict or this prompt cannot authorize experiments.
Bind execution to the approved inputs and policies. Document a real trust boundary:
workers must not be able to edit the active controller, authorization source or
protected policy. Do not claim that a read-only-looking file in a worker-writable
folder enforces this. If the environment cannot enforce the required separation,
keep live execution disabled and explain the smallest missing setup.
Do not change OS permissions or create accounts/services during this assignment.

E. Budgets, recovery and stop controls.
Check limits before every dispatch; count attempts, including failures. Unknown live
budgets mean no execution. Implement timeouts, bounded retries, single-run locking,
atomic state updates and an interruption-safe event log. Allow at most two automatic
repair retries for an eligible technical failure; never retry for a better score.
Support status, preview/dry-run, explicit activation, resume and stop. Resume must
revalidate authorization, inputs and prior artifacts. Reconcile interrupted jobs;
do not blindly repeat a possibly completed long-running or non-idempotent operation.
Stopping must prevent new launches and handle active child processes safely.

F. Durable evidence and teaching outputs.
Log input/config/code identifiers, commands actually run, timestamps, exit codes,
artifacts, checks, review findings and limitations. Redact credentials. Distinguish
recorded from measured usage; do not promise exact monetary enforcement without a
mechanism that actually bounds it. Generate a concise progress report explaining
input -> operations -> output -> evaluation -> conclusion -> uncertainty.

## 4. Preserve the research sequence without implementing it now

Derive future tasks from the inspected reports and existing queue. Preserve these
scientific distinctions and restrictions:

- Prepare a genuinely results-blind literature/research assignment where isolation
  is possible; do not give it achieved results. Do not claim blindness merely from
  creating a new role. If access/context isolation is unavailable, record the limit.
- Locate and assess existing robustness work before proposing another run.
- Require a clear, user-approved protocol before experimental execution.
- Distinguish modality sensitivity from adaptive-fusion benefit. Keep matched
  representations/mixing-rule controls, paired comparisons and uncertainty in scope.
- Keep fine-tuning and spatial/temporal transformer studies conditional on an approved
  hypothesis; do not activate every idea automatically.
- Freeze the chosen method and selection recipe before independent assessment.
  Do not relabel a repeatedly consulted test set as fresh.
- Separate independent-dataset retraining, zero-shot transfer, code portability and
  reproducibility. Do not guess the earlier dataset candidates or invent labels.
- Leave the inspection UI deferred unless expressly selected later.
- A valid negative result passes a research task. Invalid or unverified evaluation
  does not become acceptable because a score improves.

Prepare task interfaces and acceptance criteria, not speculative training scripts.
Do not run literature searches or experiments to fill missing protocol fields here.
The eventual workflow must distinguish a literature-only authorization from approval
of a final experimental protocol; do not pretend unknown scientific decisions have
already been made just to promise one-click completion.

## 5. Demonstrate the runner with offline tests

Use isolated SYNTHETIC_ORCHESTRATION_TEST fixtures and fake workers. Keep their
state separate from the real research queue. Explicitly test:

1. Successful dependency progression and prevention of duplicate execution.
2. Missing, malformed, revoked, mismatched or agent-forged authorization is rejected.
3. Blocked dependencies, missing budgets and excluded tasks cannot launch.
4. Fabricated DONE responses, missing outputs, inconsistent hashes and failed
   acceptance/reviewer checks do not mark a task complete.
5. Timeouts, malformed responses, nonzero exits, bounded retries and exhausted budgets
   save honest state and block dependent work.
6. Interruption/resume, concurrent-start locking and stop controls behave as documented.
7. Path traversal and symlink escapes, unauthorized command arguments, and attempts
   to weaken policy are refused; separate unit checks from real OS isolation tests.
8. A valid negative-result fixture advances, while an invalid high-score fixture fails.
9. The complete fake workflow passes work between coordinator, worker and reviewer
   without the user copying intermediate messages.
10. No fake success changes a real research task's status or creates live authorization.

Record exact commands and observed outcomes. Do not call simulated adapter tests a
successful real Codex connection. Do not run the repository's existing test suite.
Allow at most two setup repair cycles; preserve remaining failures as blockers.

Use an available separate reviewer to inspect the new code, tests, report mapping
and permission boundaries. The old audit-verifier prompt is a reference: give this
reviewer an explicit setup-review scope, not a fabricated new identity or approval.
A second AI review remains an additional check, not scientific certification.

## 6. Deliver a working setup or a precisely bounded blocker

Write SETUP_RESULT.md and the executable runner, tests, fixtures, derived queue,
state/log schemas, artifact manifest and a short README. Keep documentation compact.
Include a scope/preservation check against the initial state for files actually
checked; do not assert that every repository file was verified unchanged.

SETUP_RESULT.md must distinguish:
- implemented and tested offline;
- inspected but not live-tested;
- blocked by a specific environmental requirement;
- waiting for user authorization;
- deliberately deferred research work.

Create USER_DECISIONS.md containing only unresolved decisions needed for the next
real stage, grouped into one approval request. State recommended options and their
reasons but leave unapproved budgets/choices visibly unapproved. Do not ask the user
to write new prompts, edit complex JSON, or relay reports back to ChatGPT.

Provide actual copyable commands for this environment to inspect status, dry-run,
resume and stop. State the verified scope of each. Provide a separate activation
procedure that shows the exact scope, protocol version and budgets for explicit
user confirmation. If live prerequisites remain unmet, say which ones; do not
present a placeholder command as a tested one-command launch.

Finish with the path to SETUP_RESULT.md, what now works, what cannot yet run, and
the single next user action. End with Evidence checked / Still uncertain /
Defensible conclusion. Then stop. Do not activate, schedule or launch research.
