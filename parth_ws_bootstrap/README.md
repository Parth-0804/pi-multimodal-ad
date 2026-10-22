# Parth WS — Codex research workflow starter

Prepared 19 October 2026. This is a proposed instruction pack, not an installed automation,
completed audit, research report, or approval to run experiments.

## Start with one handoff

1. Extract this folder inside the thesis repository so its name remains
   `parth_ws_bootstrap`. Do not overwrite an existing folder with that name; keep
   both versions and point Codex to the new one instead.
2. Open that thesis repository in Codex desktop. Keep sandboxing and approval
   controls enabled. Do not select unrestricted/full access just to reduce prompts.
3. Paste the contents of `START_HERE_CODEX.md` into a new Codex task.

That prompt authorizes a bounded, static audit and creation of NEW reports only.
It does not authorize training, inference, tests, corruption runs, dependency
installation, scientific code changes, dataset downloads, a scheduled job, or
external publication. The task should finish at a consolidated approval packet.

Selecting a workspace can expose permitted local content to the model service.
Do not include credentials or data that you are not permitted to process this way.
No software or account settings have been changed by creating this pack.

## What the first task does

Inspect the instruction hierarchy and environment; trace the current visual,
sensor, and fusion paths; inventory existing robustness evidence; distinguish
current source from historical runs; obtain a separate evidence review where the
available tools support it; produce a prioritized, resumable plan.

It must preserve the existing dirty working tree, raw data, historical outputs,
scientific code, configurations, and existing AGENTS files.

The final packet should identify one next proposed step and the actual barriers
to unattended execution. It must not imply that a desktop connection, persistent
controller, fresh reviewer, research run, or background task exists when it does not.

## Contents

- `START_HERE_CODEX.md`: first task prompt; paste this once.
- `RESEARCH_RULES.md`: evidence, safety, and scientific boundaries.
- `TASK_QUEUE.json`: dependencies and locked later stages; a specification, not a runner.
- `STUDY_PROTOCOL_TEMPLATE.md`: the decisions needed before experiments.
- `prompts/VERIFIER.md`: a separate audit review assignment.
- `prompts/INDEPENDENT_LITERATURE_REVIEW.md`: a later, results-blind research prompt.
- `RESUME_CODEX.md`: continue an interrupted audit without silently authorizing more work.
- `AGENTS_APPEND_PROPOSAL.md`: a proposed persistent instruction addition; not installed.
- `OFFICIAL_REFERENCES.md`: product documentation checked when preparing the pack.
- `MANIFEST.sha256`: integrity hashes for these files.

## What is automatic and what is not

Within a running task, the coordinator is instructed to move through eligible
audit stages without asking you to relay messages. Subagent capability must be
checked; a self-review must be labelled self-review, not a second independent review.

This pack does not contain an executable controller and does not schedule tasks.
It cannot restart Codex after interruption or approve its own next research stage.
A JSON status and a prompt are not a security boundary. Later unattended execution
requires verified runtime permissions, a protected approval record, a controller,
and tested stop/resume/budget behaviour. The first audit should specify that minimal
setup, not build an elaborate platform or install it unasked.

## Later research sequence

Independent literature and dataset screening -> approved protocol and resource
limits -> baseline/reproduction checks -> missing controlled robustness comparisons
-> conditional encoder studies -> locked external-dataset assessment -> interface
and teaching handoff. Optional encoder studies may be omitted for scientific reasons.

The main goal is testing adaptive-fusion robustness. A valid negative finding is
successful research. Better AP does not make an invalid experiment acceptable.

The historical experiment previously called Task 4 remains excluded from execution
unless the user explicitly reauthorizes that specific experiment. The new queue
uses named stage IDs to avoid confusing it with an unrelated fourth task.
