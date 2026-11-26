# Measured modalities and alignment

## Actual same-episode evidence

The matched pilot downloaded **20 Parquet tables and 60 AV1 MP4 videos**, totaling **127,669,857 bytes**. It contains 5,255 sensor rows and 15,765 camera frames across the three streams. The three cameras are `cam_high`, `cam_left_wrist`, `cam_right_wrist`, each 640×480 RGB at 25 fps. Filenames, episode/task fields and lengths agree for every sampled execution. All sixty clips decoded sixteen requested positions through their last frame without reported decode errors. All **960** selected decoded images are distinct within their own sixteen-frame sequences.

One same-task original success/failure pair (`pick_marker_draw_line`, episodes 2 and 6) was independently downloaded as original HDF5, **110,957,834 bytes total**. Both files declare `sim=False`; the stored puppet-arm arrays `observations/qpos`, `observations/qvel`, `observations/effort` match `observation.state`, `observation.velocity`, `observation.effort` **exactly**, with maximum absolute conversion error zero for all six comparisons. This demonstrates source observation provenance, not solely a README claim.

Original HDF5 images and converted frames were compared at three uniform positions in each camera of both episodes: **18 comparisons**, expected lossy-conversion differences, PSNR **40.60–45.32 dB**. They support camera/episode/index mapping in those samples; they are not a content scan of the full release. Source image decoding follows the author's stored-RGB convention, with no extra channel swap.

## Sensor meaning and channel availability

State is current puppet-arm joint position, velocity is joint telemetry and effort is the native effort feedback field. These are separate from `action`, `action_leader`, target end-effector action and base commands. None of the command fields, labels, keyframe flags, correction text, source IDs or task IDs is admissible as an ordinary sensor input in the proposed primary experiment.

There are 42 stored observation fields (three 14-D arrays), but they are **not 42 informative independent channels**. All 5,202 published statistic records and the 20 actual pilot tables show the following structural zeros: gripper velocity indices 6/13, and twelve non-gripper effort indices. Only the two gripper effort fields vary in the pilot; each pose/state stream has at least seven varying channels per sampled episode and velocity at least twelve. There are **28 non-placeholder fields by this source screen**: 14 positions, 12 arm velocities, 2 gripper effort signals. Some legitimately inactive-arm fields are constant within an execution.

| Index | Channel name | State | Velocity | Effort |
| --- | --- | --- | --- | --- |
| 0 | left_waist | position observation | velocity observation | zero placeholder |
| 1 | left_shoulder | position observation | velocity observation | zero placeholder |
| 2 | left_elbow | position observation | velocity observation | zero placeholder |
| 3 | left_forearm_roll | position observation | velocity observation | zero placeholder |
| 4 | left_wrist_angle | position observation | velocity observation | zero placeholder |
| 5 | left_wrist_rotate | position observation | velocity observation | zero placeholder |
| 6 | left_gripper | position observation | zero placeholder | gripper effort, units unverified |
| 7 | right_waist | position observation | velocity observation | zero placeholder |
| 8 | right_shoulder | position observation | velocity observation | zero placeholder |
| 9 | right_elbow | position observation | velocity observation | zero placeholder |
| 10 | right_forearm_roll | position observation | velocity observation | zero placeholder |
| 11 | right_wrist_angle | position observation | velocity observation | zero placeholder |
| 12 | right_wrist_rotate | position observation | velocity observation | zero placeholder |
| 13 | right_gripper | position observation | zero placeholder | gripper effort, units unverified |

Physical calibration/units are not included in the inspected HDF5 attributes or conversion feature metadata. Do not label effort as calibrated Nm or contact force, or state that wrist six-axis force/torque is provided. Retain raw units and document the lack of calibration; statistical scaling must be fitted inside training groups. Gripper positions/effort cannot be assumed dimensionally equivalent to arm joint positions/torques. No audio is used or substituted.

## Time-index alignment and its limits

For every pilot table, `frame_index` is exactly 0..N−1; `timestamp` is strictly increasing and agrees with index/25. All actual row/global indices and episode/task associations pass. Selected FFmpeg video presentation times align with the corresponding table times with a maximum absolute difference of **0.000000915527 seconds (0.916 microseconds)**. The same sixteen indices and presentation times are used in all three cameras.

This is agreement on the **converted, regular 25 Hz time index**. The checked original HDF5 files have no explicit per-camera capture times, robot hardware timestamp vector or independently calibrated clock offset. Video FPS is assigned on conversion. Camera-to-robot hardware latency and capture jitter therefore remain **unquantified**, not bounded by 0.92 microseconds or proven below one frame (40 ms). The source arrays and camera lengths provide strong episode/index pairing evidence, sufficient to consider retrospective action classification; precise failure-onset prediction/closed-loop anticipation needs additional timing evidence. No offset was estimated from labels or anomaly correspondence.

## Defects and unresolved samples

The complete listing contains no missing episode modality paths. The sampled good cohort has no missing/nonfinite observed values, no ordering mismatch, no repeated selected decoded image, and no flagged decoder error. This does not establish every full-data payload is intact or free of within-video repetition.

**Constant position telemetry:** published records flag 173 episodes (162 failure, 11 success) with all fourteen positions fixed. Actual tables for episodes **1294** and **3325** confirm this. Their high-camera videos show clear robot arm/object motion while positions remain constant; velocity and gripper effort still vary. Bounded reads of the original HDF5 observation arrays reproduce exactly the converted arrays in both cases. The issue is therefore present upstream, not introduced by this conversion. Original source paths are `raw_data/pick_coke_bottle_place_plate_ep1/episode_24.hdf5` and `raw_data/pick_plate_from_drawer_put_pink_cube_ep1/episode_72.hdf5`.

These two are confirmed unreliable position records. Quarantine all 173 flagged cases until reviewed; do not automatically claim all 173 are defective, since genuinely stationary executions require separate judgment. Do not integrate velocities to invent replacement ground-truth positions. The two QC cases are additional to the 20 matched examples. Evidence: `checks/constant_state_actual_sample_audit.json`, `constant_state_origin_audit.json`, `constant_state_QC_1294.jpg`, `constant_state_QC_3325.jpg`.

This combination of strong valid pilot pairing and explicit upstream defects supports a **conditional**, quality-controlled cohort rather than unconditional use of all 5,202 episodes.
