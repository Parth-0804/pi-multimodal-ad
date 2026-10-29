# 03 DATA PREPROCESSING

Run `20261029T004900Z`. Published 2026-10-29T03:33:18.706783+00:00. Pipeline state: **READY_FOR_CPU_EXECUTION_GPU_QUEUED**. Immutable report snapshot: `VIFAILBACK/10_final_research_reports/report_snapshots/20261029T004900Z/20261029T033317107110Z`.

One complete episode is one target, not48 independent labeled frames. Uniform rounded linspace selects16 matching frame indices in each camera, without avoid/correct keyframes or outcome labels. Three views pool equally after the original image processor. No full decoded-image cache is retained; resumable per-frame CNN feature banks retain896float32 values per frame.

Measured sensor channels:14state,12nonplaceholder velocity,2gripper-effort fields. Exact source10statistics/channel produce280 stat-major features. Placeholder constant channels are excluded. Per-episode statistics have no population fitting. Model standardizers fit T only; sigmoid calibration fits disjoint C only. All labels, failure types, native keyframes, source/task IDs, action commands and manual judgments are excluded from ordinary input features. Time is normalized episode progress only for slope.

Runtime contract, feature names, source identities and exclusions are under `03_preprocessing/`. Model comparisons use the identical final technically eligible cohort. Semantically uncertain videos stay flagged and do not get filtered by model correctness.

Secondary camera ablation: V1_high_only retrains the same frozen head on16high-camera frames, using the same primary cohort and task partitions. The camera was fixed before held-out prediction; this is not a fine-tuned single-camera or fusion experiment.
