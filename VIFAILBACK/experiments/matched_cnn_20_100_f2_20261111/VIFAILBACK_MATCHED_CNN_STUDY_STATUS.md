# VIFAILBACK_MATCHED_CNN_STUDY_STATUS

Generated 2026-11-10T23:47:30.757333+00:00. 74 completed fits; 0 partially trained fits; 1 currently running fits (PID and creation time verified); 20 complete F2 assessment cohorts. Unfinished planned work is not a negative scientific result.

|Experiment|Complete|Partial / running|Blocked|Queued|Resource deferred|Awaiting admission|Exact unresolved requirement|
|---|---|---|---|---|---|---|---|
|FROZEN20|36|0|0|0|0|0|None for declared fit scope|
|FULL20|0|0|0|36|0|0|Finish/resume declared fits; admit prospective seeds only by resource gate; F2 needs complete meta-bank and outer predictions.|
|DONOR20|36|0|0|0|0|0|None for declared fit scope|
|FROZEN100|1|0|0|0|0|0|None for declared fit scope|
|FULL100|0|1|0|0|0|0|Finish/resume declared fits; admit prospective seeds only by resource gate; F2 needs complete meta-bank and outer predictions.|
|DONOR100|1|0|0|0|0|0|None for declared fit scope|

Reports: `14_final_research_reports/01_EXECUTIVE_SUMMARY.md` through `13_RESEARCHER_HANDOFF.md`. Exact checkpoint/history/configuration/prediction paths: `11_metrics_and_statistics/FIT_COVERAGE.json`; F2 coefficients: `09_f2_fusion/`; split manifests: `02_dataset_and_splits/`; results: `11_metrics_and_statistics/CURRENT_RESULTS.json`; limitations: `14_final_research_reports/10_UNCERTAINTY_AND_LEAKAGE_LIMITATIONS.md`; Git commit evidence: `13_reproducibility/`.

```json
{
  "generated_utc": "2026-11-10T23:47:30.768167+00:00",
  "git_HEAD_at_report": "2a51688af2fc4a355607716e9bb9ab3b01e23f91",
  "protocol_sha256": "71cbb3b01b0adb47d2e055bf79391276f1f2f3a9dd339e5b0f07013932caa9c5",
  "completed_fits": 74,
  "partial_fits": 0,
  "running_fits": 1,
  "completed_fusion_cohorts": 20,
  "controller": {
    "CPU_CONTROLLER_STATUS": {
      "completed_fits": 74,
      "create_time": 1794353606.39,
      "git_commit": "2a51688af2fc4a355607716e9bb9ab3b01e23f91",
      "lane": "cpu",
      "pid": 29076,
      "planned_fits": 74,
      "python": "3.12.3",
      "stage": "COMPLETE",
      "utc": "2026-11-10T23:42:23.265193+00:00",
      "same_process_alive": false
    },
    "GPU_CONTROLLER_STATUS": {
      "completed_fits": 0,
      "condition": "FULL100",
      "create_time": 1794353606.37,
      "fit_directory": "06_full100/seed42/outer0_inner0",
      "fit_id": "outer0_inner0",
      "git_commit": "47e16d3120fb4ae905118b16f40dee4000ec3592",
      "lane": "gpu",
      "pid": 29074,
      "planned_fits": 37,
      "python": "3.12.3",
      "seed": 42,
      "stage": "TRAINING",
      "utc": "2026-11-10T23:33:34.131583+00:00",
      "same_process_alive": true
    },
    "WATCH_STATUS": {
      "evaluated_completion_fingerprint": "4eb0ec294842a472839de64c3188d3cbca1e796cb49f6cee783273a22b0becbd",
      "lane_stages": [
        "COMPLETE",
        "TRAINING"
      ],
      "stage": "WATCHING",
      "utc": "2026-11-10T23:46:30.553052+00:00"
    },
    "GPU_TELEMETRY": {
      "compute_pids": [
        29074
      ],
      "current_process_hours": 0.2312112828049999,
      "devices": [
        {
          "index": 0,
          "memory_total_MiB": 16384,
          "memory_used_MiB": 5589,
          "name": "Tesla T4",
          "utilization_percent": 0,
          "uuid": "GPU-44f7c9c1-5574-c432-d4e3-7a278b27f958"
        }
      ],
      "mean_observed_utilization_percent": 69.73493975903614,
      "other_compute_pids": [],
      "peak_device_used_MiB": 5691,
      "samples": 83,
      "sampling_seconds": 10,
      "scope": "device utilization during this controller process; elapsed includes decoding and validation",
      "utc": "2026-11-10T23:47:21.765278+00:00"
    }
  },
  "GPU_sessions": {
    "session_count": 1,
    "observed_GPU_controller_process_hours": 0.23125010661055537,
    "interpretation": "Observed per-process elapsed time summed once per PID/creation identity; includes decoding, validation and checkpointing. A killed process may leave an observation lower bound. It is not pure GPU kernel time.",
    "paths": [
      "VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/13_reproducibility/runtime/GPU_SESSION_29074_1794353606.json"
    ]
  },
  "historical_outputs_modified": false,
  "push_performed_by_reporter": false
}
```
