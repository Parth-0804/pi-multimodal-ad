# 11 LIMITATIONS AND THREATS TO VALIDITY

Run `20261029T004900Z`. Published 2026-10-29T03:33:18.706783+00:00. Pipeline state: **READY_FOR_CPU_EXECUTION_GPU_QUEUED**. Immutable report snapshot: `VIFAILBACK/10_final_research_reports/report_snapshots/20261029T004900Z/20261029T033317107110Z`.

Canonical-task independence is tested; session, operator, robot and object-instance independence are not established. The native outcome is an episode failure annotation, not a frame-level fault time or independently scored final mechanical success. The known human-intervention category is excluded; incidental human presence and semantic visibility remain incompletely reviewed. Whole-episode sensors and RGB are retrospective inputs, so these results cannot establish early warning.

Coordinate task55 remains quarantined; no guessed sign transformation or clipping is applied. All converted sensor tables were checked, but original HDF5 comparisons cover only3 anomalous episodes/9 arrays. Position/velocity/gripper-effort fields are measured observations, not calibrated force/torque. Converted25Hz agreement does not establish independent hardware clock synchronization.

The historical20-example visual pilot was selected for observability and balance. Nineteen decided observations agreed with native labels; B02 remains uncertain. It is neither a prevalence sample nor a held-out classifier benchmark. The conservative cohort excludes818 episodes before video QC; exclusions change the estimand and their counts overlap by reason.

Mean pooling is invariant to permutation of retained frames and camera order. Within-episode shifts change sampled content through edge padding; they do not prove tolerance to real hardware clock errors. Quality gating has clean-only training; robustness claims require measured stress-test results. Explicit missing-modality masks and surviving-branch fallback are programmed behavior, not learned reliability recognition. All-both-missing cases abstain. Fixed masks and severities are simulations, not evidence about every deployment failure.

Meta models see smaller-data inner branch predictions than final outer branches. This stacking distribution shift is reported rather than repaired using test outcomes. The fixed three-seed design does not make repeated folds or episodes independent replications. Task bootstrap intervals are conditional on fitted models, do not capture donor selection uncertainty, and multiple comparisons remain exploratory.

Exact raw trajectory and video-triplet duplicates are screened; near-duplicate executions and semantic overlap between different canonical tasks are not exhaustively resolved. Shared workspaces, robots, objects and unknown sessions can limit effective independence. The donor has one fixed source training seed; three target seeds do not establish donor-seed stability.

Some native judgments depend on intended task goals and corrective history, which may not be uniquely observable from16sampled images and episode statistics. The experiment predicts native whole-episode annotations; it does not establish instruction-compliant final success, causal fault localization or early warning.
