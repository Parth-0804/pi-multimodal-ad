# Repository working instructions

## Purpose and authority

A reproducible master's thesis research workspace for the design,
implementation, comparison and evaluation of multimodal learning and fusion
architectures for industrial condition and action-failure monitoring.

Work includes visual and numerical sensor representations, CNN feature extraction
and fine-tuning, unimodal baselines, feature-level and probability-level fusion,
static and quality-aware fusion, missing/degraded modality robustness, independent
dataset evaluation, hyperparameter and seed experiments, reproducibility and thesis
documentation. These are research areas, not blanket execution authorization or
claims that every dataset has completed every study.

Read relevant domain instructions, protocols and actual execution evidence before
working. Start with [REPO_MAP.md](REPO_MAP.md) and [README.md](README.md), while
retaining the scope limitations below. Core policies remain
[data boundaries](docs/data_boundaries.md), [output policy](docs/output_policy.md)
and [written active scope](docs/active_scope.md). Navigation describes repository
contents, not permission to execute work. Distinguish written policy, traceable
task-specific researcher authorization, researcher-reported supervisor agreement,
execution evidence and proposed policy interpretation. Completed work and saved
commands do not themselves amend policy or authorize a new task.

The [original exposé](MA_Exposé_Ravaliya_Parth.pdf), §3, pp.2–3, is the research-question
starting point: representation components (SQ1), comparative fusion (SQ2),
missing/degraded-modality robustness (SQ3), and evaluation beyond accuracy (SQ4).
Use the [reconciled charter](docs/thesis_research_direction/RESEARCH_CHARTER.md),
[alignment decision](docs/thesis_research_direction/EXPOSE_ALIGNMENT_DECISION.md),
[experiment inventory](docs/thesis_research_direction/THESIS_EXPERIMENT_INVENTORY.md)
and [evidence map](docs/thesis_research_direction/EXISTING_EVIDENCE_MAP.md) with their
dates and evidence boundaries. Keep original questions, later proposals and
formally approved scope distinct. The alignment decision dated 2026-10-25 records
a REPORTED researcher statement of supervisor agreement to PHM + REASSEMBLE,
attributed to the 2026-10-06 review, §1.1. Preserve that recorded decision; check
its provenance and precise scope when materially relevant. It is not independent
verification of supervisor approval or authorization of a final title, manuscript
or additional experiment.

## SCIENTIFIC EVIDENCE AND CLAIM VALIDATION

Use these classifications for substantive scientific and implementation claims:

| Classification | Meaning |
|---|---|
| VERIFIED | Directly inspected source, configuration or artifact, or independently recomputed result, within an explicitly stated scope. |
| REPORTED | Existing report or researcher statement, without independent verification of the underlying claim. |
| INFERRED | Interpretation supported by identified evidence; state assumptions and alternatives. |
| PROPOSED | Future implementation or research experiment; not an executed result or approval. |
| UNKNOWN | Insufficient evidence; identify what is missing. |

- Never claim training ran because a script exists, or full fine-tuning because
  a checkpoint/experiment name suggests it. Verify executed forward paths,
  trainable parameters, optimizer coverage and execution records.
- Reading saved results or recalculating metrics does not reproduce training.
  Attribute earlier reviews' checks to those reviews; do not relabel them as new
  independent verification. A completion marker alone does not prove current
  artifact availability, integrity or scientific validity.
- Never invent metrics, checkpoints, labels, references or missing evidence. Cite
  exact source paths, experiment IDs, revisions and the scope of each check.
- Keep evaluation protocols, cohorts, target versions, fitting procedures and
  selection histories separate. Distinguish pooled AP, mean-fold AP, failure-class
  AP and both-class macro AP; state positive class, prevalence and aggregation.
  Do not silently interchange average precision and trapezoidal PR area.
- State selection, leakage, independence, missing-data and uncertainty limitations.
  Running the same architecture on another dataset does not establish cross-dataset
  generalization; distinguish independent dataset-specific fitting from transfer
  of learned parameters and from zero-shot evaluation.
- Negative and inconclusive findings are legitimate outcomes. Unfinished work is
  not a negative model result. Do not modify experiments to obtain favorable
  results after inspecting held-out performance, or disguise implementation
  mistakes as planned research contributions.

## Research domains and evidence navigation

Condition estimation, completed-action failure classification and online anomaly
detection are different tasks. Preserve their prediction units, labels and claim
boundaries. The following identifies study roles and evidence locations, not a
common leaderboard or proof of successful fusion across all datasets.

| Domain | Scientific role and evidence |
|---|---|
| PHM2026 | Industrial gear-condition and proxy-target studies. Canonical code: `src/phm2026/`; navigation: [PHM experiments](experiments/phm2026/README.md); evidence: `runs/` entries prefixed `phm2026_` and `artifacts/phm2026/`. Consult the inventory/evidence map for retained negative findings and proxy-target limitations; image-derived targets are not independently validated physical damage labels. |
| REASSEMBLE | Robotic completed-action failure classification, representations, fusion and controlled robustness. Code: `src/reassemble/`; [core walkthrough](experiments/reassemble/README.md); evidence: `runs/reassemble/` and `artifacts/reassemble/`. Consult the [core closure](artifacts/reassemble/reports/REASSEMBLE_COMPLETION_STATUS.md), [extension closure](artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_STATUS.md) and inventory for their respective scopes, discontinued work, negative findings and limitations. |
| MSM | Metal-milling interval classification from video and machine measurements. [Workspace](MSM/README.md), `MSM/src/`, protocols and saved evaluation records under `MSM/04_experiment_protocol/` and `MSM/06_evaluation_results/`. Consult the [research handoff](MSM/09_final_reports/REVIEW_HANDOFF.md) for study eligibility, findings and failed gates. |
| HANDOVER | Robot handover success/failure classification. [Workspace](HANDOVER/README.md), adapters in `HANDOVER/src/`, assessment evidence in `HANDOVER/experiments/common_support_v2/`. Consult the [research handoff](HANDOVER/09_final_reports/REVIEW_HANDOFF.md) for participant-identity limitations and learned-stacking eligibility; preserve mandatory study-specific OOF gates. |
| VIFAILBACK | Robot manipulation outcome classification with multiview video and numerical robot observations. [Workspace](VIFAILBACK/README.md), `VIFAILBACK/src/` and study-local source, protocols, fit coverage and reports under `VIFAILBACK/experiments/`. Check the relevant study and per-condition artifacts; implementation or scheduling is not completion. |
| REBOOT / dataset research | Dataset discovery, annotation audits, alignment, visibility and feasibility. [REBOOT decision](REBOOT/07_research_decision/REBOOT_RESEARCH_DECISION.md) gates further work; feasibility is not model evaluation. [DATASET_RESEARCH](DATASET_RESEARCH/README.md) links canonical workspaces rather than defining additional independent datasets. |
| Intel Welding | Historical research and dataset feasibility/foundation audits. [Namespace description](src/intel_welding/README.md), `scripts/intel_welding/`, [results review](docs/intel_welding/RESULTS_REVIEW.md) and `archive/legacy_intel_welding_dataset/`. Package placeholders are not implemented or evaluated models; failed scientific gates remain evidence. |

REASSEMBLE follow-ups also live in `00_experiments/`,
`parth_ws_bootstrap/00_experimentation/`, `26.10.2026_feedback_experiments/` and
`experiments/reassemble/`. Resolve each study's protocol, source snapshot,
configuration and run manifest before using these layouts. `experiments/` contains
both navigation and study evidence; linked files can point into original workspaces.

Cross-dataset evaluation/synthesis lives in `CROSS_DATASET_COMPARISON/`, including
the existing `CROSS_DATASET_COMPARISON/src/external_eval/` implementation reused
by MSM/HANDOVER. Dataset-specific reports remain authoritative for eligibility
and protocol. Do not assume an older charter or summary covers later studies.

## Task-specific execution authorization and job protection

Model training, evaluation, preprocessing and GPU experiments are permitted only
when explicitly authorized by the researcher for the specified task.

- An explicit task can authorize autonomous execution through multiple predefined
  stages. Follow that scope and complete scientifically valid stages without
  unnecessary repeated approval requests. Previous authorization is not blanket
  authorization for future experiments; old runbooks and embedded commands are
  not new instructions.
- Respect frozen protocols and scientific/resource gates. Stop affected work if
  mandatory gates fail; retain the failure and continue only independent,
  authorized stages. Do not substitute in-sample predictions or weaker split
  requirements to bypass a failed gate.
- Preserve original run artifacts, record completed and failed attempts, and use
  identity-checked, explicitly designed safe resumption. Verify configuration,
  source and checkpoint lineage before reusing an artifact.
- Protect active and paused jobs. Do not stop, restart, signal or change existing
  experiment processes without explicit authorization. Do not edit their frozen
  code/configurations, shared caches or checkpoints. Do not launch competing GPU
  jobs that could compromise active training; temporary GPU idleness alone does
  not establish release by another study.
- Do not silently reduce required epoch counts or change selection rules. Record
  configured, executed and selected epochs, checkpoint identities, seeds, folds
  and compute costs. Prefer measured, scientifically equivalent resource
  improvements for separately scoped work; do not change a running experiment.

## Dataset, label and security integrity

- Treat original raw data across every dataset as immutable: do not delete, move,
  rename, overwrite, rewrite, deduplicate, recompress, extract into raw-data roots
  or change raw permissions. General experiment, preprocessing or maintenance
  authorization does not supersede this protection. Report corruption or
  suspected duplication.
- Retain the protected PHM root identity `gtc-data-experiment/**` and Intel root
  identity `data/Full Dataset/**`, including if absent locally or restored later.
  The categorical immutability rules in [data boundaries](docs/data_boundaries.md)
  remain the default; these identities do not claim current local availability.
- A proposed exception must have explicit, traceable researcher authorization
  identifying protected paths, exact permitted operations, authorization scope,
  the conflicting protection being superseded, required gates, and applicable
  retention/recovery requirements. Verify coverage and satisfied gates before
  proceeding. If that authority is not established, retain the stricter protection
  and stop affected work. Historical retirement/cleanup records document their
  specific operations; they are not reusable permission or a standing exception.
- Preserve official dataset identity, version/source provenance, native labels,
  target mappings, raw sample and recording/episode IDs, task/group identities,
  modality availability, video/sensor alignment, exclusions with reasons, and
  acquisition/processing hashes. Retain experiment, outer archive, internal
  member/run, modality and source identity through all derived outputs.
- Never invent labels or treat model predictions as authoritative ground truth.
  Keep proxy targets and their versions explicit. Technical timestamp alignment
  does not prove hardware synchronization or visual observability of an event;
  commands, measured robot state and force/torque are not interchangeable.
- PHM scope remains EXP-A Runs 1–5, EXP-B Runs 1–7 and EXP-F Runs 1–8; see
  [canonical dataset configuration](configs/datasets/phm2026.yaml). EXP-A Run 2
  carries a REPORTED organizer warning of 311 files overlapping Run 1, not an
  independently verified count. Preserve both runs; duplicate handling must be
  configurable, non-destructive and reported, defaulting to report-and-include.
  Run number/lifecycle stage is not ground-truth health or damage; distribution
  shift alone does not prove degradation.
- Preserve `experiments/exp_a_initial_eda_r1_r3_r5/**` unchanged until a validated
  replacement reproduces it and the researcher approves a later migration.
  Existing generated outputs remain
  `HISTORICAL_OUTPUT_PROTECT_UNTIL_REPRODUCED`. Never overwrite historical results.
- Observe bounded read permissions in [data boundaries](docs/data_boundaries.md).
  Full archive hashing, CRC scans, large extraction, raw-payload scans and
  expensive analyses require explicit task authorization. Hash requirements do
  not authorize an otherwise forbidden full scan; report unavailable identities.
  Use isolated temporary extraction outside raw roots only within approved scope.
- Never read, expose, copy, summarize or commit `synology_cookies.txt`, `.env` or
  its variants, tokens, credentials, private keys, cookies, session contents or
  authentication/package-index configuration. Check ignore status without
  reading sensitive contents. If a secret appears tracked or exposed, stop and
  notify the researcher without reproducing it.
- Tests use tiny synthetic fixtures, never real source payloads, sensor rows,
  images or credentials copied from datasets.

## Experimental scientific protocol

- Declare the prediction task, evaluation unit, native label/target provenance,
  positive class, eligible population, class prevalence and exclusion rules.
- Verify training/validation/calibration/test manifests and appropriate
  group-disjoint splits. No source episode, recording or derived window may
  cross a protected split. Do not claim participant/session/site independence
  from weaker recording/task IDs or unavailable metadata.
- Fit preprocessing, select hyperparameters, calibrate and choose thresholds only
  within authorized training-side partitions, including designated
  validation/calibration partitions, respecting each partition's role. Protected
  assessment data must not influence these choices.
- Every fusion method needs an explicit leakage-safe fitting and assessment
  protocol. For stacking, gating or other downstream procedures fitted on branch
  predictions, use group-safe out-of-fold predictions where required to avoid
  leakage, with traceable fitting/calibration roles. Jointly trained feature
  fusion does not inherently require branch OOF predictions. Do not replace a
  mandatory study-specific OOF requirement with in-sample probabilities or weaken
  grouping when support is insufficient. All fitting and selection stay within
  training-side partitions, including designated validation/calibration partitions.
- Paired comparisons require identical eligible assessment examples, targets and
  group identities; report any cohort restriction. Use fair comparison budgets
  or explicitly describe unequal optimization, selection and compute budgets.
- Predefine seeds, folds, stopping rules, model selection, metrics and aggregation.
  Record actual execution. Document every frozen-protocol deviation as a distinct
  experiment or explicit amendment; do not retrofit a favorable rationale.
- Independently recalculate saved metrics wherever feasible within the authorized
  task. Use defensible sampling units for uncertainty; preserve pairing and group
  dependence. Repeated windows, corruptions or seeds are not independent subjects.
  State whether intervals condition on fixed models and omit training/selection
  uncertainty; inconclusive intervals do not establish equivalence.
- Separate clean performance, corrupted-input robustness and missingness fallback.
  Known-absence routing cannot demonstrate an adaptive advantage between models
  with identical fallback. No robustness, transfer, generalization or deployment
  readiness claim without evidence appropriate to that claim.
- Preserve negative/incomplete experiments and corrections. Regression-test
  historical feature behavior before refactoring. Document defects; scientific
  formula or ingestion corrections need separately reviewable changes,
  failing-then-passing regression tests and methodology notes.

## Model architecture terminology

Describe the checkpoint's original architecture separately from executed
components, frozen/trained components, representations, fitted classifiers,
parameters reused across datasets and newly initialized parameters. Inspect the
actual forward path, trainability and optimizer, then bind execution claims to
run evidence; source inspection alone establishes implementation, not execution.

- RT-DETR pretraining does not imply its spatial Transformer/hybrid encoder,
  detector decoder or bounding-box heads ran. The core REASSEMBLE path in
  `src/reassemble/section1_features.py` extracts CNN backbone maps; separate PHM
  detector and spatial-encoder studies must retain their own forward descriptions.
- Distinguish frozen feature extraction with a fitted head, final-stage CNN
  fine-tuning and full executed-backbone fine-tuning. All three conditions exist
  in separate study implementations; none establishes full detector training.
  Describe normalization-affine parameters and fixed running statistics precisely.
- Distinguish engineered statistical sensor representations, PatchTST/other
  temporal encoders, feature concatenation, static probability fusion,
  process-aware gates, quality-conditioned fusion and explicit missing-modality
  fallback. Same-sensor representation fusion is not two sensing modalities.
- Describe the actual fusion inputs, equation, calibration and training protocol.
  F2's fitted logistic coefficients are not causal modality-importance percentages;
  unrestricted probability stacking is different from convex logit gates and
  quality-interaction models. Weight changes alone do not establish reliability.
- Frame averaging is not learned temporal modeling. Completed-action or
  whole-episode classification is not real-time early warning. Warm component
  timing is not end-to-end deployment latency.

## Organization, configuration and paths

- Keep domain-owned implementation under `src/phm2026/`, `src/intel_welding/`
  and `src/reassemble/`, with their domain scripts/configurations/tests. Existing
  dedicated MSM/HANDOVER/VIFAILBACK/REBOOT and experiment-local layouts remain
  valid. `src/pi_multimodal_ad/` provides legacy compatibility; do not duplicate
  the historical monolith or introduce circular imports between datasets.
- Shared helpers require actual reusable consumers across domains; generic names
  alone do not justify a shared abstraction. Do not invent empty packages to
  satisfy an obsolete proposed tree.
- Use portable configurations for selection, channels/modalities, data/output
  roots, duplicate policy and validation. Default to repository-relative paths
  with environment-variable/CLI overrides; do not introduce absolute workstation
  or VM paths. Resolve paths without changing source data or permissions.
- Keep dataset-specific raw/processed inputs, model/checkpoint provenance,
  evaluation reports and cross-dataset comparisons traceable. Prefer navigation
  documents and provenance links over migration or dataset/checkpoint copies.
  Inspect symlink targets before writing; links can share protected evidence.
- `configs/datasets/`, `configs/experiments/` and domain/experiment-specific
  configurations coexist. Tests mirror actual ownership under `tests/` and
  dedicated workspaces; central tiny synthetic fixtures are in `tests/fixtures/`.

## Reproducibility, outputs and retention

Every substantive scientific experiment should record applicable items below,
explicitly marking unavailable or inapplicable fields rather than fabricating them:

- Experiment ID, dataset/version, Git revision and dirty-tree/source identities;
  exact executed command, timestamp/timezone and effective configuration snapshot.
- Training seeds, group/split manifests, exclusions, exact architecture,
  initialization/pretraining source, trainable parameter configuration, optimizer
  and learning-rate schedule; configured/executed/selected epochs and checkpoints.
- Model/checkpoint hashes, software versions, input/output manifests and available
  acquisition/processing identities; per-example predictions where appropriate.
- Metrics, class definitions/prevalence, aggregation and uncertainty; measured
  CPU/GPU execution costs with attribution limits; warnings, failures, deviations
  and scientific limitations.

Write new work to unique versioned run directories, preserving original artifacts.
Fail on conflicting existing outputs except through an explicitly designed,
identity-checked resume mode; final scientific results remain immutable. Consult
[output policy](docs/output_policy.md) before tracking generated artifacts. Never
commit raw data, extracted HDF5/source payloads, secrets, environments, caches,
large checkpoints or large temporary outputs. Small curated evidence needs explicit
tracking rules and lineage. A Git commit does not prove ignored artifacts were
preserved elsewhere; verify retention/recovery separately. Do not call outputs
reproduced until the stated reproduction procedure actually passes.

## Policy conflicts and historical exceptions

- `README.md` retains PHM-centered background. `docs/active_scope.md` explicitly
  calls itself canonical for the active thesis pipeline and requires a researcher
  change to that document and canonical configuration for experiments outside
  A/B/F. Later research documents and domain records describe broader work;
  [preserved MSM/HANDOVER task instructions](CROSS_DATASET_COMPARISON/provenance/task_authorization.txt)
  record specific execution authorization. Those records and the REPORTED
  supervisor agreement do not establish a general amendment of the written scope
  policy. That boundary remains unresolved: do not infer an exemption from
  completed studies or this navigation. Where proposed work depends on superseding
  it, require traceable researcher direction resolving the conflict; otherwise
  retain the restrictive boundary and stop affected work. The charter's dated MSM
  proposal and later evaluation records retain their separate chronology.
- [PHM retirement report](artifacts/phm2026/PHM_RAW_RETIREMENT_REPORT.md) and
  [recovery instructions](docs/phm2026/RAW_DATA_RECOVERY.md) report a one-off raw-tree
  retirement with D1/D2 gates, in conflict with older blanket immutability wording.
  [REASSEMBLE cache retention](docs/maintenance/REASSEMBLE_CACHE_RETENTION.md) reports
  a separate narrow derived-cache exception with retention/recovery requirements.
  These are historical authorization/execution records, not independent proof of
  authority for a new operation. Apply the explicit exception requirements above;
  neither record grants future deletion, replay, restoration or job resumption.
- [Migration plan](docs/repository_restructure/MIGRATION_PLAN.md) and dated
  structure records describe historical phases. Current code, `pyproject.toml`,
  [compatibility contract](docs/repository_restructure/COMPATIBILITY_CONTRACT.md)
  and actual path existence must be checked before reusing old commands or claims
  about missing packaging, forwarding paths or proposed shared directories.
- If policies conflict with later decisions or execution evidence, name exact
  sources, evidence classification and scope. Do not infer authority from execution
  or silently choose a convenient interpretation. Preserve historical evidence
  and the stricter disputed protection until the affected boundary is resolved.

## Thesis documentation and AI use

Link claims to source evidence; distinguish implementation and execution from
literature descriptions. Verify scientific references against original sources;
never invent citations, DOIs, pages or results. Preserve research chronology,
important methodological corrections, negative/incomplete studies and unresolved
limitations. Keep proposed charter/title changes distinct from the exposé and
approved scope. Record AI tools and prompts where university/supervisor policy
requires; do not assume such documentation certifies compliance. Never claim
plagiarism or reference checks passed unless performed. Codex can prepare evidence
and drafts; its report cannot certify correctness, novelty or academic acceptance.

## Git safety, validation and handoff

- Before edits inspect Git status/current HEAD and applicable instructions.
  Preserve pre-existing staged, unstaged and untracked work. Change only approved
  paths; never reset, silently discard changes or rewrite history.
- Stage only relevant paths when commits are authorized; use meaningful scoped
  messages. Never push without explicit instruction. Keep raw data and large
  generated artifacts ignored.
- Stop and request confirmation before destructive or difficult-to-reverse work
  unless an existing explicit, narrow authorization already covers that operation
  and its mandatory gates pass. Historical cleanup permission is not reusable.
- Work one approved restructuring phase at a time. At phase boundaries report
  changed files, `git diff --stat`, checks, unresolved issues and exact next action;
  wait for approval of a further phase unless already explicitly authorized.
- Review the complete edited document, contradictions, duplication, Markdown links
  and path existence. Do not embed volatile scores, fit counts, PIDs or current job
  states in these instructions. Check records for current execution status.

Run applicable non-destructive checks and report only those actually performed:

```bash
git diff --check
git status --short --branch --untracked-files=all
```

For documentation changes, also review the exact diff, Markdown and navigation.
Use the actual repository environment documented in README/domain instructions
when available and relevant; do not assume a fixed virtual-environment path.
Run documented domain pytest/package checks for relevant authorized code changes;
dependency-health checks are needed only when relevant to the change or required
by an applicable instruction. Documentation-only work does not call for model
tests, inference, preprocessing or training. Do not install dependencies or alter
environments without authorization. Report pre-existing/environment failures and
unresolved policy decisions without broadening scope to fix them.
