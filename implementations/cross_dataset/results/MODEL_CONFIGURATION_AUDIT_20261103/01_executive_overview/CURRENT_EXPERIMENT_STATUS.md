# Current experiment status

Audit date: 2026-11-03. Read-only evidence reconstruction; no new training, tuning or feature extraction.

| Study | Current evidence | Completed scope | Outstanding |
|---|---|---|---|
| REASSEMBLE C20 |Approved stop completed Nov3 12:23:30UTC (13:23Berlin) |25/25 cap;25/75 original;seed42;20 epochs each |50 deferred fits;C20 F2 not finalized |
| B/C100 |COMPLETE |Two arms,100 epochs each, selected14/47 |No additional paired folds/seeds |
|100-epoch static F2 |COMPLETE pilot |Two fitted F2 states, M1–M7 metrics |Single920-row stack bank;not four-inner100-epoch OOF |
| MSM P |COMPLETE |54 cases, six protocols, three seeds |R transfer unexecuted;donor20 epochs fails minimum25 |
| Handover P baselines |COMPLETE |Three seeds, official common-support cohort |F2/gates blocked by participant mapping;R unexecuted |
| Vi frozen/sensor/V1 fusion |COMPLETE saved chains |72 heads,36 LR+108 HGB candidates,27 fusion/gates |V2/V3 training0;75-fit scheduling barrier |
| PHM |Historical completed states and aggregate-only evidence |Canonical runs and legacy fusion/scoring studies |Provisional targets, missing per-fit states/epochs, LOEO defect |
| REBOOT/Intel |Feasibility/EDA/source evidence |No trained native classifier found |No performance claim |

No active primary research training was found at initial inspection. Vi's controller PID metadata was stale. Process/resource snapshots are recorded in provenance; a saved status file is not proof of a live or paused process. The audit did not signal, launch, restart or reschedule any job. The25-fit cap is complete, not a failed fit or a75-fit completion. Changes by external processes after the snapshot are outside this audit's control.

## Evidence anchors

- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_c_only_20epoch_revision_01/26102026_execution/PHASE1_C_ONLY_STATUS.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_c_only_20epoch_revision_01/26102026_execution/PHASE1_C_ONLY_STATUS.json) — authoritativecompleted25status.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_c_only_20epoch_revision_01/02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json](../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_c_only_20epoch_revision_01/02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json) — completiontimestamp/hashreceipt.
- [VIFAILBACK/configs/experiment.json](../../../VIFAILBACK/configs/experiment.json) — revision, seeds, donor SHA, architecture,100-epoch recipe.
- [VIFAILBACK/src/vifailback/splits.py](../../../VIFAILBACK/src/vifailback/splits.py) — plans/require_oof task-disjoint roles.
- [VIFAILBACK/src/vifailback/training.py](../../../VIFAILBACK/src/vifailback/training.py) — fit checkpoint selection and optimizer.
- [VIFAILBACK/src/vifailback/baselines.py](../../../VIFAILBACK/src/vifailback/baselines.py) — S3 LR and three S2 HGB candidate settings.
- [VIFAILBACK/src/vifailback/fusion.py](../../../VIFAILBACK/src/vifailback/fusion.py) — F2 and quality/availability gates.
- [VIFAILBACK/src/vifailback/resources.py](../../../VIFAILBACK/src/vifailback/resources.py) — gpu_state75-fit scheduling barrier.
- [VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json](../../../VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json) — historical waiting state, not process liveness.
