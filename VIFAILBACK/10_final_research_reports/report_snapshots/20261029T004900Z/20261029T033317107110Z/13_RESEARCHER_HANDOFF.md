# 13 RESEARCHER HANDOFF

Run `20261029T004900Z`. Published 2026-10-29T03:33:18.706783+00:00. Pipeline state: **READY_FOR_CPU_EXECUTION_GPU_QUEUED**. Immutable report snapshot: `VIFAILBACK/10_final_research_reports/report_snapshots/20261029T004900Z/20261029T033317107110Z`.

Acquisition: {'ACQUIRED_VERIFIED': 13095, 'VERIFIED_EXISTING': 57}. Camera QC: (13150, 13152). Final cohort: 4382. Completed fits: {'visual_frozen': 0, 'visual_frozen_high_only': 0, 'visual_finetuned100': 0, 'reassemble_transfer': 0, 'sensor_baselines': 0}.

Configuration: `VIFAILBACK/configs/experiment.json` and `VIFAILBACK/configs/protocol.json`.
Controller: `VIFAILBACK/scripts/run_pipeline.py`; live status: `VIFAILBACK/logs/20261029T004900Z/PIPELINE_STATUS.json`.
Final cohort: `VIFAILBACK/03_preprocessing/processed_manifests/20261029T004900Z/eligible.json`.
Splits: `VIFAILBACK/04_evaluation_splits/train_validation_test/20261029T004900Z/fit_partitions.json`.
Checkpoints/predictions: `VIFAILBACK/06_training_experiments/{visual_frozen,visual_finetuned100,reassemble_transfer,sensor_baselines,fusion_experiments}/runs/20261029T004900Z/`.
Robustness: `VIFAILBACK/07_robustness_experiments/combined_corruption/runs/20261029T004900Z/`.
Historical unblinding and exclusions remain under `DATASET_RESEARCH/VIFAILBACK_VERIFICATION/FOLLOWUP_REVIEW/20261028T233227Z/`.

Reproduce/resume using `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 CUBLAS_WORKSPACE_CONFIG=:4096:8 ma_thesis_env/bin/python -B VIFAILBACK/scripts/run_pipeline.py`. It acquires only the declared conservative cohort, waits for full QC, freezes the common manifest/splits, runs CPU baselines/features/frozen heads, then waits for the existing study before GPU full100/fusion/robustness. Failures are recorded and stop the affected stage. Never launch a second controller while its file lock is held. Per-stage commands are available through `scripts/worker.py --help`.

The active report index is versioned on every publication. Prior report bytes remain in report_snapshots. Raw and historical evidence are preserved. Large videos/features/checkpoints remain ignored. Relevant local commits are recorded in `researcher_handoff/GIT_HANDOFF.json`; nothing is pushed. The original3unrelated tracked modifications and unrelated pre-existing untracked trees remain untouched. Final performance and prediction galleries must only be read when their COMPLETE receipts exist.
