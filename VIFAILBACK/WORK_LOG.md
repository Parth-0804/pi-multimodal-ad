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
