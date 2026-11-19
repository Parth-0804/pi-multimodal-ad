# RoboFAC native-label and data audit

**Decision: NO-GO for the current real-world visual-plus-numerical experiment.** A simulated study is a different scientific question and is not recommended before resolving the native label and identity issues below.

## Source identity and license

The official [Hugging Face release](https://huggingface.co/datasets/MINT-SJTU/RoboFAC-dataset/tree/d18353ab36db82ff888ebc9e8485c9fa77e1b25b) is pinned to **d18353ab36db82ff888ebc9e8485c9fa77e1b25b**. The official code is pinned to **638eb5320d409e4072710a0db26f1c0d68cef3de**. The dataset card declares MIT and the repository includes an MIT license. The complete `dataset_files_with_sizes.json` inventory contains 12,739 files, totaling 25,771,018,505 bytes. `file_tree.json` is a 1,000-entry preliminary page and was **not** used as a complete inventory. Complete `siblings` metadata with sizes and LFS hashes was used instead.

The author-reported totals are 9,440 erroneous and 1,282 successful trajectories, comprising simulation and real-world data. They are not substituted for independently counted source records. The original task is failure analysis/correction QA, not a ready-made clean binary multimodal classifier benchmark. The [paper, version 2](https://arxiv.org/html/2505.12224v2) reports 8,960 simulated failures, 1,160 simulated successes, 480 real failures and 122 real successes; only the real action counts are reproduced directly by the released QA/path grouping here.

## Original records and measured counts

| Source and prediction unit | False / failed | True / successful | Total |
|---|---:|---:|---:|
| 679 simulation JSON files, raw `success` rows | 9,890 | 4,729 | 14,619 |
| Simulation JSON rows with exact listed video path | 7,138 | 1,786 | 8,924 |
| Real-world original failure-detection QA, per camera video | 960 | 244 | 1,204 |
| Real-world camera groups, same dataset path and episode filename | 480 | 122 | 602 |
| Simulation test QA with explicit original Failure detection answer | 1,359 | 153 | 1,512 |

These rows are different units and must not be added. There are 10,120 listed simulated videos. The test simulation QA covers 6,720 unique video paths, but 5,208 have no explicit Failure detection entry. Absence of this entry does not mean success. `training_qa.json` contains 64,691 QA rows for 10,115 unique video paths. Exact verified detection prompts yield 8,127 `No.` and 1,151 `Yes.` QA rows; these reduce to 7,601 and 1,007 unique video paths respectively. These counts remain QA-specific and are not a validated physical-sensor cohort.

Real-world counts use the seven original `test_qa_realworld/annos_per_video_split*.json` files. Each record includes a UUID, `video`, `task`, and an `annos` dictionary. Within `Failure detection`, the human question asks whether the task succeeded and the assistant answer is literally `No.` or `Yes.`. All 602 real action path groups have exactly two camera views and consistent answers between views. Directory suffix `error` is not used as a label: successful actions occur in these directories too.

| Real-world task path | Failed actions | Successful actions |
| --- | --- | --- |
| so100_insert_cylinder_error | 100 | 20 |
| so100_pick_cube_in_box_error | 60 | 20 |
| so100_pull_cube_by_tool_error | 140 | 20 |
| so100_pull_cube_error | 60 | 22 |
| so100_push_cube_error | 60 | 20 |
| so100_stack_cube_error | 60 | 20 |

Native schema: each simulated JSON has `env_info` and an `episodes` list with `episode_id`, `episode_seed`, `elapsed_steps`, `unique_id`, reset metadata and Boolean `success`. A simulation label is episode-level environment success; QA answers refer to intended task success. Neither is a frame-level anomaly interval.

## Integrity and semantic problems

- 13,351 distinct UUIDs occur in 14,619 trajectory rows; 326 UUIDs recur. **76 UUIDs have differing native success flags** across metadata locations. Join by full source path plus episode ID; a global UUID alone is insufficient. Of exact video-joined rows, only 8,859 distinct UUIDs remain.
- **5,695** trajectory rows have no video at the exact documented leaf-directory/UUID path. This is an exact join failure, not proof that no alternative copy exists elsewhere.
- All 679 JSON leaf paths have an HDF5 counterpart listed, but the full internal trajectory contents were not downloaded. No missing/invalid success field or duplicate local episode index was found in these JSON records.
- Of 1,044 unambiguous exact video comparisons between simulation test QA and native JSON success, **184 disagree**. Recovery, intentional-error versus final environment success, or misassociated metadata could explain some differences; the release does not resolve that distinction. Do not silently relabel or call every difference corruption.
- Even `simulation_data/success_data/` contains 1,041 true and 351 false flags. Names are not reliable binary supervision.
- **6,715** video paths overlap between released training QA and test QA. These are not acceptable independent episode splits for this architecture. A question-level split may have different intended semantics; it must not be rebranded episode-disjoint.
- All 11,324 MP4 files and all 679 HDF5 files have distinct source LFS content identities. This does not exclude similar/repeated trajectories under changed filenames or views.

See `checks/robofac_native_trajectory_records.csv`, `robofac_test_native_detection_records.csv`, `robofac_qa_json_outcome_comparison.csv`, `robofac_counts.json` and `robofac_extended_identity_screen.json` for exact exceptions and denominators.

## Numerical modality: actual HDF5 inspection

Two original HDF5 files were downloaded, totaling 1,012,212 bytes:

1. `simulation_data/UprightStack-gen1/place_upright_view1_position_offset/ToolsTask_traj.h5`: one trajectory.
2. `simulation_data/success_data/PickCube-v1/stack_error/ToolsTask_traj.h5`: thirty trajectories.

All **31** JSON-to-`traj_N` joins exist, action lengths equal JSON `elapsed_steps`, and terminal HDF5 success agrees with JSON success in these sampled trajectories. This is independently checked sample evidence, not full HDF5-corpus verification.

Both contain `actions` (T×8), `env_states/articulations/...` (T+1×31), actor state arrays (T+1×13), rewards, success, terminated and truncated flags. The first sample's numerical arrays are finite. These are commanded controls and **simulated environment states**, including privileged object positions; no measured real-world force/torque or robot observation stream was found in these checked schemas. Exact coordinate layout, SI units, and physical/control sample rate are not specified by these HDF5 attributes. Do not invent channel names within the 31-D or 13-D vectors.

The matching small simulated MP4 has 205 frames at 30 fps; its action stream has 204 steps and state stream 205 entries. That supports a candidate state/frame indexing relation in this sample, not independently timestamp-verified synchronization. No explicit HDF5 time vector was found. The two real-world preview videos have 242 and 241 frames at 30 fps, but **the complete real-world inventory has zero numerical/HDF5 files**. Real video cannot be joined to simulation kinematics as if measured from the same example.

Rewards, success flags, termination markers, QA text and privileged goal/object states must not become ordinary classifier inputs. [Numerical checks](checks/robofac_two_h5_identity_checks.json) preserve the exact source joins.

## Grouping, visibility and minimum next dependency

For real data, keep both views of each `(task dataset, episode filename)` together. All six task groups contain both outcomes. No released session/operator/date table was found. For simulation, group scene/environment, reset seed and all related camera/error variants; additionally union repeated UUID identities. The published QA split cannot be reused without episode-overlap controls.

Actual real previews show an unsuccessful grasp and a successful lift/insertion in `so100_insert_cylinder_error`, episodes 0 and 100. The gripper and cylinder are visible; exact hole engagement is partly occluded. One simulated clip shows a manipulated peg and unstable/fallen objects. Visibility of these few examples does not fix missing real numerical data or resolve label semantics.

Before recommending this candidate, obtain author-validated real-world numerical counterparts with episode/timestamp mapping, or explicitly change the objective to simulation and resolve the 184 sampled QA/JSON differences, repeated UUIDs and missing exact video paths. The existing tiny previews are sufficient to demonstrate the current blocker; no additional RoboFAC acquisition is proposed.
