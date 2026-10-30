# Active ViFailback run

Run: `20261029T004900Z`. Implementation commit: `786814344`.
Initial preservation: `9414da8f8`. Initial repository HEAD:
`94f61529116ebdc966bcf87704a93e4d02fa5e89`.

Final common cohort:4,382 episodes,3,753 failure/629 no-failure,99tasks,all mixed;
820excluded/quarantined. All13,152 requested clips are publisher-hash verified;
13,150decode completely. Two source defects (2071/right,4784/left) are confirmed
with two decoders and remain preserved. All12T/V/C/A partitions per seed contain
both classes and disjoint canonical tasks. Sensors:28observed fields,280stats;
force/torque calibration and session/operator independence are not established.

The implementation has28passing synthetic tests, package compatibility checks,
and separately saved actual-data CPU gradient/reload/forward checks. Source
donor115tensors/69changes and100executed epochs/selected47 are independently
verified. Diagnostic updates are not empirical target results.

Autonomous controller PID is recorded with creation time in
`logs/20261029T004900Z/CONTROLLER_PROCESS.json`; initial PID290646. It is detached,
low priority, and holds its own lock. Native labels and final splits passed at
startup; the full-task blinded gallery precedes CPU sensor baselines/features/
frozen heads. Read `PIPELINE_STATUS.json`, `STAGE_HISTORY.json` and stage logs.

Source/configuration are frozen in `reproducibility/PROTOCOL_FREEZE.json`.
**Do not edit frozen source/configuration while this controller is live.**
Documentation publications preserve immutable snapshots. Own code and reused
source/software identities are rechecked before stages. No changes were made
to the active REASSEMBLE study. Its75-fit completion marker and metric hash,
plus an idle GPU, are mandatory before target GPU work. There is no wall-time
cutoff or shortened CNN schedule.

Three outer/three inner folds ×seeds42/123/20261023 require36fits per primary
visual condition:V1frozen,V2original-full100,V3donor-full100. Secondary high-only
frozen heads add36fits. F2 and quality/static gates use held-out inner outputs.
Supplemental F2_aug/Gate_aug/static_aug use identical label-blind corruptedOOF
records, with20×2N gate presentations matching40×Nclean. Full CNN schedules
remain100. Robustness uses fixed raw-input stresses, explicit fallback versus
learned conditioning, both-missing abstention and clean replay checks.

Final probabilities, checkpoints, histories and plots remain ignored large
artifacts. Reports01–13 and completion status are active indices with retained
snapshots. Performance/transfer/fusion/robustness verdicts remain pending until
the corresponding completed artifacts and independent calculations exist.

Only specific relevant local files were committed. Unrelated pre-existing
changes to rootREADME,REPO_MAP andTHESIS_EVIDENCE_GAPS remain unstaged. No push,
PR, amend, reset, raw-data deletion or old-evidence replacement was performed.

## 2026-10-30: researcher priority correction

The primary scientific question is controlled replication of original REASSEMBLE
fusion on ViFailback. Original frozen V1, original static sensor S1=S3 Logistic
Regression, original-initialized full CNN V2 for 100 executed epochs, F1 averaging,
original OOF-fitted F2 and missing/degraded-modality evaluation take priority in
interpretation. Report within-dataset differences before cross-dataset consistency.
HGB remains completed, preserved exploratory work; it does not replace S3 in F2.
V3 transfer, camera ablations and gated extensions remain supplementary. The
older description of V3 as a primary visual condition above records the earlier
framing, not the corrected research emphasis.

The live controller has completed 36 V1 fits, 36 high-only fits and frozen fusion;
both frozen and donor initial feature banks are complete. It is waiting for
the source REASSEMBLE 75-fit study and GPU availability. That source study reported
10/75 fits completed at 2026-10-30T16:29:35Z. No process was signaled or restarted,
and no source/configuration, queue order, split, epoch budget or fitting rule was
changed. The 31 frozen implementation/configuration files and 5 reused source files
still match their recorded hashes.

The dated reporting correction and saved-result check live in
`10_final_research_reports/researcher_handoff/20261030_RESEARCH_PRIORITY_CORRECTION/`.
The check recomputes AP/AUROC from all 9 frozen outer prediction tables, verifies
the original LR joins and inner OOF lineage, reconstructs averaging/F2 using
saved coefficients and checks 100-epoch completion receipts for all 36 V1 fits.
It does not retrain, refit, retune, reload model payloads or produce new bootstrap
intervals. Frozen F2 exceeds vision but falls below original LR in pooled macro
AP for each of the three seeds. The full CNN 100-epoch and robustness conclusions remain
pending; this partial result does not establish cross-dataset fusion consistency.
