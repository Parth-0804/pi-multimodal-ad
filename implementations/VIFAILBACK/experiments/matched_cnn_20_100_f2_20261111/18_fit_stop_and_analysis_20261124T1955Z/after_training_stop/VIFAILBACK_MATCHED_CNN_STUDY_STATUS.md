# VIFAILBACK_MATCHED_CNN_STUDY_STATUS

Generated 2026-11-24T22:04:19.215167+00:00. 79 completed fits; 0 partially trained fits; 0 currently running fits (PID and creation time verified); 22 complete F2 assessment cohorts. Unfinished planned work is not a negative scientific result.

|Experiment|Complete|Partial / running|Blocked|Queued|Resource deferred|Awaiting admission|Exact unresolved requirement|
|---|---|---|---|---|---|---|---|
|FROZEN20|36|0|0|0|0|0|None for declared fit scope|
|FULL20|4|0|0|32|0|0|Finish/resume declared fits; admit prospective seeds only by resource gate; F2 needs complete meta-bank and outer predictions.|
|DONOR20|36|0|0|0|0|0|None for declared fit scope|
|FROZEN100|1|0|0|0|0|0|None for declared fit scope|
|FULL100|1|0|0|0|0|0|None for declared fit scope|
|DONOR100|1|0|0|0|0|0|None for declared fit scope|

Reports: `14_final_research_reports/01_EXECUTIVE_SUMMARY.md` through `13_RESEARCHER_HANDOFF.md`. Exact checkpoint/history/configuration/prediction paths: `11_metrics_and_statistics/FIT_COVERAGE.json`; F2 coefficients: `09_f2_fusion/`; split manifests: `02_dataset_and_splits/`; results: `11_metrics_and_statistics/CURRENT_RESULTS.json`; limitations: `14_final_research_reports/10_UNCERTAINTY_AND_LEAKAGE_LIMITATIONS.md`; Git commit evidence: `13_reproducibility/`.

```json
{
  "generated_utc": "2026-11-24T22:04:19.227418+00:00",
  "git_HEAD_at_report": "aa4dc0cb80e0d169e9f75c7679c07583aa94622a",
  "protocol_sha256": "71cbb3b01b0adb47d2e055bf79391276f1f2f3a9dd339e5b0f07013932caa9c5",
  "completed_fits": 79,
  "partial_fits": 0,
  "running_fits": 0,
  "completed_fusion_cohorts": 22,
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
      "completed_fits": 5,
      "create_time": 1794656559.67,
      "error": "RuntimeError('Another study process holds VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/04_full20/seed42/outer1_final/FIT.lock')",
      "git_commit": "aa4dc0cb80e0d169e9f75c7679c07583aa94622a",
      "lane": "gpu",
      "pid": 50845,
      "planned_fits": 37,
      "python": "3.12.3",
      "resume": "Re-run this lane; completed receipts are checked and unfinished fits resume at committed epoch boundary.",
      "stage": "FAILED",
      "traceback": "Traceback (most recent call last):\n  File \"/home/student/Master_Thesis_WS/pi-multimodal-ad/VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/src/matched_vifailback/common.py\", line 136, in exclusive_lock\n    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)\nBlockingIOError: [Errno 11] Resource temporarily unavailable\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File \"/home/student/Master_Thesis_WS/pi-multimodal-ad/VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/src/matched_vifailback/controller.py\", line 142, in run\n    receipt = fit(condition, seed, job, context=context)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/student/Master_Thesis_WS/pi-multimodal-ad/VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/src/matched_vifailback/training.py\", line 270, in fit\n    with exclusive_lock(root/'FIT.lock'):\n  File \"/usr/lib/python3.12/contextlib.py\", line 137, in __enter__\n    return next(self.gen)\n           ^^^^^^^^^^^^^^\n  File \"/home/student/Master_Thesis_WS/pi-multimodal-ad/VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/src/matched_vifailback/common.py\", line 138, in exclusive_lock\n    raise RuntimeError(f'Another study process holds {relative(path)}') from exc\nRuntimeError: Another study process holds VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/04_full20/seed42/outer1_final/FIT.lock\n",
      "utc": "2026-11-24T22:01:59.962017+00:00",
      "same_process_alive": false
    },
    "WATCH_STATUS": {
      "evaluated_completion_fingerprint": "2f7d5d119f6464ae9443cfb7112718706254e362bb01aa1e6c5a30973677ffc7",
      "lane_stages": [
        "COMPLETE",
        "TRAINING"
      ],
      "stage": "WATCHING",
      "utc": "2026-11-24T22:01:09.566290+00:00"
    },
    "GPU_TELEMETRY": {
      "compute_pids": [
        50845
      ],
      "current_process_hours": 250.3184912367475,
      "devices": [
        {
          "index": 0,
          "memory_total_MiB": 16384,
          "memory_used_MiB": 5589,
          "name": "Tesla T4",
          "utilization_percent": 100,
          "uuid": "GPU-44f7c9c1-5574-c432-d4e3-7a278b27f958"
        }
      ],
      "mean_observed_utilization_percent": 66.91499814920752,
      "other_compute_pids": [],
      "peak_device_used_MiB": 5669,
      "samples": 89151,
      "sampling_seconds": 10,
      "scope": "device utilization during this controller process; elapsed includes decoding and validation",
      "utc": "2026-11-24T22:01:51.073172+00:00"
    }
  },
  "GPU_sessions": {
    "session_count": 2,
    "observed_GPU_controller_process_hours": 303.7617104355631,
    "interpretation": "Observed per-process elapsed time summed once per PID/creation identity; includes decoding, validation and checkpointing. A killed process may leave an observation lower bound. It is not pure GPU kernel time.",
    "paths": [
      "VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/13_reproducibility/runtime/GPU_SESSION_29074_1794353606.json",
      "VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/13_reproducibility/runtime/GPU_SESSION_50845_1794656559.json"
    ]
  },
  "historical_outputs_modified": false,
  "push_performed_by_reporter": false
}
```
