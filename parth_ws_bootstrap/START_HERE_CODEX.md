# Start the Parth WS research workflow — audit only

You are working in my thesis repository. Help me set up a sequential, evidence-based
research workflow with minimal manual handoffs. In this task, perform ONLY a bounded
static audit and create a new preparation packet. Do not implement experiments.

## Read first

Read the existing governing instructions, including applicable AGENTS.md and
AGENTS.override.md files. Then read:
- parth_ws_bootstrap/RESEARCH_RULES.md
- parth_ws_bootstrap/TASK_QUEUE.json
- parth_ws_bootstrap/prompts/VERIFIER.md
- parth_ws_bootstrap/STUDY_PROTOCOL_TEMPLATE.md

These are explicit task instructions, not permission to override stricter existing
rules. The task queue is a proposal/state specification, not an executing controller.
Do not assume the conversation that produced this pack is in your context.

My primary scientific goal is independently testing adaptive multimodal-fusion
robustness. All six candidate workstreams are described in RESEARCH_RULES.md.
Do not assume any particular architecture, previously reported score, or novelty
claim is correct. Do not try to make the thesis look successful at any cost.

## Scope and permissions

Treat all scientific source, datasets, configurations, models, existing artifacts,
and existing instructions as read-only. Create only NEW audit outputs under:
  parth_ws_bootstrap/outputs/<actual-UTC-timestamp>-audit/

Use a unique suffix when necessary; never overwrite a previous output directory.
Do not edit this starter pack or existing AGENTS files. Copy the queue into the new
output directory and update only that copied state. Initialize RUN_STATE.json and
COMMAND_LOG.md at the start; update them before and after each stage and before
any pause. A partial run must leave enough state to resume without repeating work.

No training, inference, feature extraction, evaluation/rescoring, corruption runs,
project tests, notebook execution, model deserialization, package installation,
dataset/weight downloads, remote sessions, scientific fixes, Git mutations, cloud
jobs, scheduled jobs, or UI development. The historical experiment called Task 4
remains excluded. Do not run it under a new name.

Safe static inspection and bounded local metadata commands are allowed, subject
to the actual sandbox and approval policy. Do not change those policies. No external
network work in this audit. Prepare the independent literature task; do not run it.

Do not ask me to approve each file read or report section when it is already allowed.
Respect platform approval prompts. Ask a question only for a material access/identity
ambiguity that cannot be resolved safely; otherwise record the gap and continue the
unrelated authorized work.

## Stage A — establish the actual environment and preserve state

1. Identify the selected repository root without searching unrelated directories.
   If multiple repositories could be the target, do not guess.
2. Read the applicable instruction hierarchy and report conflicting requirements.
3. Record current HEAD and initial dirty/untracked status using non-mutating Git
   inspection with optional index locks disabled. Do not assume HEAD contains
   every scientific file. Do not print credentials or remote URLs with tokens.
4. Record observable OS, interpreter/package declarations, lockfiles, dataset paths
   in accessible configs, and existing local compute metadata. Distinguish observed
   installed versions from declared dependency versions. Read metadata without
   importing the project or initializing a model/GPU. Do not connect to remote compute.
5. Record whether available tools support a separate reviewer, web research, CLI
   invocation, and structured outputs. Mark untested capabilities UNKNOWN; do not
   install, enable, or invoke new services just to check them.

Save ENVIRONMENT_AND_ACCESS.md, including commands actually used, results, and
scope limits. Save INITIAL_STATE.json with the initial repository status and hashes
of the small source/config files actually used as evidence, not all data or weights.

## Stage B — trace the research implementation, not its names

Use targeted search over the repository and its accessible docs. Common prior
references such as src/reassemble, section1_features.py, section1_models.py,
section1b.py, and section2_models.py are search hints ONLY; locate the actual files
and record their real paths. Do not invent a missing file from a report reference.

For REASSEMBLE trace, where inspectable:
- sample identity, target provenance, split unit, frame and sensor selection;
- image preprocessing and model/checkpoint loading;
- the actual called backbone/encoder/decoder path and returned features;
- spatial/temporal pooling and feature-cache boundaries;
- trained versus frozen components, gradient boundaries, and classifier inputs;
- retained sensor branch versus alternatives tested separately;
- actual fusion formulas, inputs, calibration, missingness handling, and thresholds;
- paths tying current source to retained runs, including gaps and later variants.

Create CURRENT_SYSTEM_MAP.md. For every substantive claim cite relative file path,
function/symbol, actual inspected line range, and file hash or source version.
Record a caller/output trace rather than assuming imports establish execution.

For each key claim say VERIFIED_WITHIN_SCOPE, REPORTED, INFERRED, PROPOSED, or
UNKNOWN. Static source verification is not run reproduction. Do not report dynamic
output sizes or trained parameter counts as measured without suitable saved evidence.

Create CLAIMS_AND_CORRECTIONS.csv with columns:
claim_id, claim, evidence_status, source_path, symbol, line_range, source_sha256,
run_reference, evidence_limit, affected_document_or_decision, correction_or_next_check.
Unknown fields remain empty with the uncertainty explained; never fill by guessing.

## Stage C — check existing study coverage

Inventory existing reports, configs, logs, manifests, and prediction-bank metadata
for clean baselines, visual/sensor corruption, missing inputs, gate behaviour,
encoder follow-ups, and external datasets. Do not execute them or recompute scores.

Create EXISTING_EXPERIMENTS.md. For each study distinguish:
- proposed only;
- reported as run;
- source/config inspected;
- retained artifacts located;
- historical producing source bound or not bound;
- which verification would still be needed.

A filename or summary is not proof of a completed or valid experiment. An inaccessible
artifact is not proof it never existed. Flag possible duplication before recommending
a new corruption study. Recover the names of the earlier two dataset candidates only
from accessible records; otherwise explicitly mark their identities unresolved.

## Stage D — propose the smallest useful sequence

Create PRIORITIZED_PLAN.md using the six candidate workstreams, but do not promote
all of them into compulsory thesis experiments. Separate representation quality,
fusion adaptivity, external validation, and engineering usability/reproducibility.

For each proposed task state: hypothesis; closest existing internal evidence; inputs;
change being isolated; fixed controls; acceptance criteria based on validity rather
than positive results; dependencies; exact scope of allowed future claims; and a
reason it could be deferred or rejected.

Prepare, but do not execute, the results-blind literature assignment from
prompts/INDEPENDENT_LITERATURE_REVIEW.md. Assess whether a genuinely fresh context
without project outcomes is possible. If not, say so; do not label a reused-context
review independent or blind.

Draft a PROTOCOL_DRAFT.md using STUDY_PROTOCOL_TEMPLATE.md. Leave unresolved numeric
budgets, dataset identities, and thresholds explicitly undecided. Mark the entire
protocol PROPOSED / NOT APPROVED. Do not select new hyperparameters from test results.

In AUTOMATION_READINESS.md specify the smallest later controller plan using the
actual environment. Include persistent state, task dependencies, one writer, separate
review, outside-agent approval protection, least privilege, budget limits, bounded
retries, stop/resume behaviour, failure handling, and technical enforcement. Do not
install or build the controller now. Do not claim chat memory or this pack enforces
these boundaries.

## Stage E — additional evidence review

Use an actually available separate read-only reviewer with prompts/VERIFIER.md.
Give it the relevant primary source locations, hash/version information, criteria,
and draft packet. It must inspect sources itself for the claims it reviews. It may
return findings to the coordinator, who remains the only report writer.

If tools do not support a fresh reviewer, perform a clearly labelled SELF_REVIEW_ONLY
and record the missing separate review. Never invent a subagent, model identity,
independence, command run, or reviewer approval. Do not invoke a billed external API
or install tools to obtain a reviewer.

Create VERIFIER_REVIEW.md. Allow at most two report-only correction cycles. Do not
repair scientific code or rerun studies in response to findings. Keep unresolved
findings visible. Correct documents by preserving a revisions log inside this new
packet rather than silently erasing contrary evidence.

## Stage F — finish and stop at the approval boundary

Create APPROVAL_PACKET.md with:
1. What was actually inspected and produced; no claims of experiment execution.
2. The current architecture and evidence boundaries in plain language.
3. Existing work that should not automatically be repeated.
4. The proposed sequence and first next task, with no execution authority implied.
5. What needs one explicit user decision: scientific protocol, dataset, access,
   code-write scope, budget, review policy, and evidence thresholds.
6. Conditions that should interrupt future automation; valid negative results are
   not an interruption merely because they are disappointing.
7. A teaching handoff: input -> operations -> output -> evaluation -> conclusion
   -> uncertainty, grounded in the inspected material.

Save RUN_STATE.json (copy of queue with actual audit statuses, not unlocked future
stages), COMMAND_LOG.md, and ARTIFACT_MANIFEST.json (paths and hashes of created
reports; exclude the manifest itself to avoid self-referential hashes).

Compare final Git status and the hashes of inspected scientific files with the
initial state. Report unexpected changes without reverting or attributing them
without evidence. New authorized packet outputs should be distinguished from any
pre-existing dirty files. Bound the preservation check to the files actually checked.

Future research stages must remain WAITING_USER_AUTHORIZATION or DEFERRED.
Do not declare the task complete just because reports exist: check references,
required sections, status consistency, and primary-evidence limits.

End with a compact human-readable summary of findings and blockers and the exact
path to APPROVAL_PACKET.md. Include the evidence checkpoint. Then stop. Do not
schedule a continuation, start the literature search, train anything, or claim you
will keep working after this task ends.
