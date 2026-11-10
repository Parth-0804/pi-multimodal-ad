# HANDOVER input validation

Native verified labels: **589**. Eligible visual-plus-sensor examples: **587**. Excluded: **2**; all exclusions retain the original native label.

| official_split | target | eligible_examples |
| --- | --- | --- |
| test | 0 | 41 |
| test | 1 | 110 |
| train | 0 | 90 |
| train | 1 | 245 |
| validation | 0 | 25 |
| validation | 1 | 76 |


The following rows partition the excluded native units by their complete combination of failure reasons (no double counting):

| combined_technical_exclusion_reason | native_examples |
| --- | --- |
| wrench_nearest_time_gap_exceeds_0.1s | 2 |


Every admitted supplied wrench_resampled.npy is exactly reproduced from raw wrench.npy using the nearest raw timestamp, matching the author resample.py implementation. Each native camera index joins to head_cam_ts.npy and the corresponding six-wrench row. Video PTS are retained separately and are not assumed equal to sensor-clock seconds. The full-video audit is preserved, including its 92 test exclusions for unsupported tails. Before any Handover model score, an explicit common-support amendment froze the intersection of camera/raw-wrench support for every class/robot. Sixteen source-clock bin-center frames and sensor statistics use that same common recorded window. Maximum nearest timing gap remains 0.1 s; two training trials fail it. All 151 official test trials are retained. No action or outcome annotation chooses frames.

The allowed channels are `force_x, force_y, force_z, torque_x, torque_y, torque_z`. Channel-major statistics are mean, population std (ddof 0), RMS, minimum, maximum and peak-to-peak: **36 values** per native example. No label, tool ID, program, direction, folder, robot, task or participant metadata enters the main predictors. Training-only means/standard deviations are fitted separately for every inner and final fit. Gripper/joint configurations differ between robots and are not fabricated into a shared joint vector. HSR wrench is measured; Gen3 wrench is estimated from joint torque. Fourteen trials have all-six-channel zero traces; they are retained as native, timestamp-valid observations and flagged as uninformative, not silently relabeled or “repaired”.

One prediction is one native cutting interval or completed trial. It is retrospective classification, not early warning. Technical decoding/alignment is distinct from optical anomaly observability. Native labels, raw data and all prior results remain unchanged.

The machine-readable validation gate and exclusion inventory are under `HANDOVER/experiments/common_support_v2/02_labels_and_alignment/`.
