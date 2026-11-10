# ViFailback research completion status

**CPU_SENSOR_BASELINES_COMPLETE_VISUAL_FEATURES_RUNNING.** 

Acquisition: {'ACQUIRED_VERIFIED': 13095, 'VERIFIED_EXISTING': 57}. Camera QC: (13150, 13152). Final cohort: 4382. Completed fits: {'visual_frozen': 0, 'visual_frozen_high_only': 0, 'visual_finetuned100': 0, 'reassemble_transfer': 0, 'sensor_baselines': 36}.

Verified native5202episodes:4545failure/657no-failure. Provisional conservative4384episodes:3755/629,99tasks;818excluded/quarantined. Final common cohort: **4382 episodes**, 3753 failures, 629 no-failures, 99 canonical tasks; 820 unique exclusions/quarantines. Sensor280feature contract, native joins and real48-image CPU gradient/reload checks are available. Pipeline/code validation does not establish fusion benefit.

Three task-disjoint outer folds,3inner OOF folds, seeds42/123/20261023; 100executed epochs for V2/V3. GPU work waits for the ongoing REASSEMBLE75-fit study. There is no shortened epoch schedule. Full training, transfer and robustness questions remain unresolved until their saved artifacts complete.

Read `10_final_research_reports/01_EXECUTIVE_SUMMARY.md`, `05_TRAINING_AND_CHECKPOINTS.md`, `11_LIMITATIONS_AND_THREATS_TO_VALIDITY.md`, and `13_RESEARCHER_HANDOFF.md`. Live stage/PID/errors: `logs/20261029T004900Z/PIPELINE_STATUS.json`; immutable report snapshot: `10_final_research_reports/report_snapshots/20261029T004900Z/20261029T034902912165Z`.

Scientific status: technically reproducible investigation in progress; no superiority/robustness claim. Native failure is whole-episode, positions/velocities/gripper-effort are not force/torque, hardware clocks and session independence are unverified, task55 remains quarantined, B02 remains uncertain.

Commits are local only; no push or PR. Exact hashes/worktree exclusions: `10_final_research_reports/researcher_handoff/GIT_HANDOFF.json`. Historical evidence and unrelated work remain preserved.
