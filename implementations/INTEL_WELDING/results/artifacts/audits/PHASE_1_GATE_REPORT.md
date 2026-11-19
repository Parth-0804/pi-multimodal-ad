# Phase 1 foundation gate report

**Decision: NO-GO for unimodal modelling.** The primary blocker is prior
final-holdout exposure, compounded by selective missingness and unresolved
video/timestamp integrity. No model was trained in this pass. PHM work, raw data,
existing Intel outputs and the original proposed split were preserved.

Evidence directory: `artifacts/intel_welding/audits/foundation_runs/20260927T114705163655Z`. Manifest SHA256: `9c4fb4df70bb137fc851dd858ac22d53eed86ba08c3806d7177e40b300406826`.

## Repository audit

Starting HEAD: `ea4a76f64887fd590fd1f93cc83a726192dcfecb` on main, three commits
ahead of origin/main. That commit already contains the research contract and
separate Intel package directories. Ten untracked Intel files existed at entry:
three scripts, three audit files and four split files; an ignored inventory
parquet also existed. They were not overwritten or committed by this audit.
`docs/restructuring/TASKS.md` is referenced by policy but absent; no
`pyproject.toml` was found. Repository environment is available.

The first sandbox command failed during initialization; read/write commands ran
through approved escalation. No credentials, authentication session files or
PHM raw payloads were read. No downloads, package installs, extraction, raw writes,
model training or commits occurred. The user's current Intel request provides
the dataset-scope authorization; no PHM migration was performed.

## Delivered foundations

1. Repository protection/audit and committed-contract verification.
2. Local data access verified; see GATE_0_DATA_ACCESS.md.
3. All 4,040 rows inventoried; all 8,284 modality files fully hashed.
4. Full and readable-subset label/session support, process crosstabs and
   systematic missingness quantified.
5. Supplied SPLIT rejected: 216/236 sessions cross its partitions.
6. Existing proposed split audited and invalidated; evidence and IDs preserved.
   No scientifically valid replacement can be manufactured from exposed sessions.
7. Structural temporal feasibility measured; cross-modal lag estimation deferred.
8. Context-only baseline specified, not trained.

## Main measurements

| modality | present | missing_percent | present_failing_probe |
| --- | --- | --- | --- |
| audio | 2723 | 32.6 | 0 |
| video | 2723 | 32.6 | 16 |
| sensor | 2725 | 32.55 | 0 |

| CATEGORY | samples | sessions | readable | readable_sessions |
| --- | --- | --- | --- | --- |
| Burnthrough | 320 | 19 | 320 | 19 |
| Crater_Cracks | 161 | 12 | 161 | 12 |
| Excessive_Convexity | 160 | 9 | 160 | 9 |
| Excessive_Penetration | 480 | 25 | 480 | 25 |
| Good | 819 | 55 | 819 | 55 |
| Lack_of_Fusion | 320 | 16 | 320 | 16 |
| Overlap | 160 | 12 | 160 | 12 |
| Porosity | 340 | 17 | 109 | 6 |
| Porosity_w_Excessive_Penetration | 480 | 27 | 167 | 12 |
| Spatter | 320 | 17 | 6 | 1 |
| Undercut | 160 | 9 | 4 | 1 |
| Warping | 320 | 18 | 1 | 1 |

Files with all deployable modalities: 2,723; passing structural probes: 2,707.
Only 22 samples have all five post-weld images. Zero exact-byte duplicate groups,
but 20 repeated basename IDs require composite keys and grouping review.
Sensor cadence median is approximately 8.62 Hz; video metadata reports 30/31 FPS.
Duration agreement is insufficient for alignment; 32 CSV timestamp series fail
monotonicity. All conclusions describe the present local copy.

## Protocol and interpretation

Use intended-condition terminology. Do not equate recipe prediction with
physical-defect detection. Read `label_session_process_audit.md` and
`docs/intel_welding/FOUNDATION_PROTOCOL_ADDENDUM.md` for corrected assumptions.
The public [Intel dataset card](https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset)
supports session grouping, intended-label caveats and the need to measure
synchronization; actual availability/rates above were measured locally.

The existing context scores are not used as valid results. They demonstrate a
protocol exposure problem, not a successful model comparison. All Good sessions
were included in the prior complete-population audit, so recovering missing
files cannot alone yield a pristine binary final test. See split_disposition.md.

## Checks and limits

Six synthetic tests passed: full hashing beyond the old prefix limit, timestamp
rollover/nonmonotonicity, safe paths, missing-modality flags, duplicate crossings
including images/CV, and overwrite refusal. Repository pip check passed. Full
video decoding, perceptual duplicates, physical grouping verification, alignment
lags, context retraining and any model comparison remain unperformed. This run
is traceable but not claimed to be clean-environment reproduction validated.
The initial audit invocation failed on relative-path handling before producing
inventory; its config-only run directory was retained, the bug fixed and the
full run succeeded in a fresh directory.

## Phase boundary and next action

New code: `04_foundations.py`, `05_foundation_report.py`, foundation config and
six synthetic tests. New documentation: protocol addendum, baseline specification,
foundation/failed-gate review and these versioned audit reports/tables/manifests.
Existing untracked work is retained. `git diff --stat` has no tracked-file changes;
new files are untracked and therefore absent from that statistic. No bulk outputs
were staged. The versioned run contains config, hashes and provenance.

Exact next action: researcher review of the holdout incident and choice of a
compliant recovery path, followed by explicit phase approval. Under AGENTS.md,
“Work one approved restructuring phase at a time” and “then wait for approval.”
This pause also follows the user's failed-gate and first-execution boundaries.
No dependent experiment will run before recovery and approval.

## Every gate

CONDITIONAL for future gates means **not evaluated / prerequisite unresolved**,
not a provisional pass.

| Gate | Status | Evidence / numbers | Files in run | Consequence |
|---|---|---|---|---|
| 0 Data access | PASS | Local manifest plus representative audio/video/CSV/images readable; no credentials inspected or download attempted. | GATE_0_DATA_ACCESS.md | Inventory permitted; complete hosted access not asserted. |
| 1 Integrity | CONDITIONAL | 2,707 probe-readable triplets; 1,317 missing audio/video; 16 failed video probes; 113 images. | dataset_integrity.md | Missingness analysis completed; population/repair policy unresolved. |
| 2 Label support | CONDITIONAL | 55 Good and 114 non-Good sessions with triplets; three conditions have one session each. | label_session_process_audit.md | Binary support exists; full twelve-class evaluation unsupported locally. |
| 3 Split leakage / test protection | FAIL | Proposed 32-session holdout included in prior all-population context study; 216 supplied-split crossings. | split_disposition.md; leakage_tests.json | No modelling or final-test claims; no replacement seed search. |
| 4 Temporal alignment | CONDITIONAL | 32 invalid timestamp series; median audio/video duration gap 2.355 s; lag unmeasured. | alignment_audit.md | Temporal cross-attention disabled; sample-level option only after other gates. |
| 5A Audio signal | CONDITIONAL | Not evaluated; 0 new models. | provenance.json | Blocked by Gate 3; no positive or negative signal conclusion. |
| 5B Video signal | CONDITIONAL | Not evaluated; 0 new models. | provenance.json | Blocked by Gate 3. |
| 5C Sensor signal | CONDITIONAL | Not evaluated; 0 new models. | provenance.json | Blocked by Gate 3. |
| 6 Fusion prerequisite | CONDITIONAL | 0 modalities have validated development signal evidence. | provenance.json | Fusion prohibited; absence of evidence is not evidence of no signal. |
| 7 Gate input use | CONDITIONAL | No gated model or positive control run. | provenance.json | Not reached; no robustness interpretation. |
| 8 Robustness claim | CONDITIONAL | No clean/corrupted model comparisons. | provenance.json | Not reached; SQ3 remains unanswered. |
| 9 Final test unlock | FAIL | Holdout invalidated; allow_final_test=false. | split_disposition.json | No final evaluation; new preregistration and valid holdout required. |

**NO-GO for unimodal modelling.**
