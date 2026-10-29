# Native outcome and annotation audit

## Pinned sources and actual annotation verification

Official [conversion](https://huggingface.co/datasets/sii-rhos-ai/vifailback-dataset-lerobot/tree/619791b94f61667333fe179d471051e0bca0e06f): **619791b94f61667333fe179d471051e0bca0e06f**. Official [original dataset](https://huggingface.co/datasets/sii-rhos-ai/ViFailback-Dataset/tree/21df46c2585c52e5a62df5f4b946bae6cbc6fed7): **21df46c2585c52e5a62df5f4b946bae6cbc6fed7**. Both dataset cards declare MIT licensing. The complete conversion inventory contains 20,815 files and **29,215,133,223 bytes**; 5,202 Parquet files, 15,606 MP4 videos and seven other files. Full payload acquisition was not performed.

Native conversion records: `meta/vifailback_annotations.jsonl` (15,553,675 bytes), `meta/episodes.jsonl` (943,651 bytes), `meta/tasks.jsonl` (12,738 bytes), `meta/info.json` (7,427 bytes). Additionally, **all 109** original `annotated_data/<task>/<task>_annotations.json` files were discovered from pinned directory listings and downloaded. Their exact original paths, sizes, HTTP receipts and SHA-256 identities are retained. The source files contain 5,202 records with no duplicate original video identities. **Every complete nested original annotation object equals the corresponding preserved conversion object**, not merely its label string.

Native `annotation.failure_detection` is literally **`yes` for a failed episode** and **`no` for a successful episode**. The conversion normalizes these to `episode_success = failure/success`. These are direct native fields, not inferred QA answers, folder-name labels, generated labels or LLM-created supervision.

| Native outcome | Original records | Converted records |
|---|---:|---:|
| `failure_detection=yes` / `episode_success=failure` | 4,545 | 4,545 |
| `failure_detection=no` / `episode_success=success` | 657 | 657 |
| Total | 5,202 | 5,202 |

Failure prevalence is **87.370242%**. Prediction units are episodes, not 1,297,146 frames or the 960 exported pilot images. The source annotations are manually authored/assisted according to the paper's annotation workflow; agreement with the release is not independent verification of every physical outcome. The pilot supplies an initial visual plausibility check.

## Granularity and native failure taxonomy

| Native failure category | Episodes | Interpretation and admissibility |
|---|---:|---|
| gripper 6d-pose | 2,771 | Position/orientation errors; failed grasp, alignment or placement may be visible, but native subtype is not a guaranteed visible event |
| gripper state | 988 | Opening/closing errors; can include loss of object or failed grasp |
| task planning | 645 | Wrong object/subtask/order; requires task context and can be subtle at sparse samples |
| human intervention | 141 | External disturbance; visible people can become an easy shortcut; separate stratum/control |
| successful outcome | 657 | Native successful action |

Do not replace this taxonomy with invented drop/misalignment labels. Our physical-event descriptions in the visual report are observer notes, not new ground truth. A physical-failure-focused prospective cohort could use the 3,759 pose/state failures plus successes; planning and human-intervention strata should be specified separately before training. This audit does not silently remove them from the native totals or the balanced gallery.

`complementary_info.vifailback_flags` contains `[is_failure_episode, is_avoid_keyframe, is_correct_keyframe]`. The first flag repeats the episode label on every row. Avoid/correct indices are sparse diagnostic/corrective reference frames, **not exhaustive failure-onset/offset intervals**. They were checked for range validity but never used to improve positive frame selection. An episode label cannot become a frame-level failure annotation.

## Complete join audit

All 5,202 episode indices are unique and agree between annotations and episodes metadata. Declared lengths sum to **1,297,146 frames**, with **18–925 frames per episode**; every episode has at least sixteen stored positions. Instructions agree with task metadata. Every expected Parquet and each of three video paths exists in the pinned complete file listing. No invalid outcome, metadata-length mismatch, missing listed modality, missing task mapping or out-of-range normalized keyframe was found. This verifies listings/metadata for the complete release; actual table/video checks are limited to the pilot and QC samples.

For the 20 pilot tables, actual row counts, episode IDs, task IDs, global frame index offsets, per-episode frame indices and all three flags agree with metadata. No nonfinite values occur in the inspected state, velocity or effort arrays. Full source records and exceptions are preserved in `checks/all_native_episode_records.csv`, `native_label_summary.json`, `original_native_annotation_comparison.json`, `pilot_numerical_audit.json`.

## 100 tasks versus 109 source directories

There are **100 unique English task instructions/task indices**, all containing both native outcomes. The physical release has **109** source directories; nine task instructions span two variants. Five source directories contain only failures, although their canonical tasks contain successes in the related variant. Group by canonical `task_index`, not the directory suffix or a claim of 109 independent tasks. Full original-directory counts are in `checks/class_counts_by_source_task.csv`; canonical counts are below and in `checks/class_counts_by_task.csv`.

| Task index | Source directories | Success | Failure |
| --- | --- | --- | --- |
| 0 | cut_sausage | 2 | 31 |
| 1 | drag_basket_place_cube_ep1 | 27 | 130 |
| 2 | grab_socket_unplug_charger_ep1 | 25 | 125 |
| 3 | grasp_bottle_place_bowl | 1 | 14 |
| 4 | grasp_coke_can_put_tray | 3 | 13 |
| 5 | grasp_cube_place_shelf | 1 | 14 |
| 6 | grasp_duck_put_cup | 3 | 13 |
| 7 | grasp_filter_place_juicer | 2 | 18 |
| 8 | grasp_knife_place_drawer | 3 | 13 |
| 9 | grasp_knife_place_plate | 3 | 13 |
| 10 | grasp_marker_place_in_cup | 2 | 18 |
| 11 | grasp_spatula_place_basket | 3 | 13 |
| 12 | grasp_spatula_put_pot | 1 | 14 |
| 13 | grasp_test_tube_place_bowl | 3 | 13 |
| 14 | hold_socket_plug | 3 | 13 |
| 15 | lift_lid_and_place_cube_ep1 | 25 | 132 |
| 16 | lift_lid_and_put_green_duck | 1 | 17 |
| 17 | lift_lid_place_duck | 3 | 13 |
| 18 | lift_lid_place_pot | 1 | 14 |
| 19 | open_box_place_cable | 1 | 14 |
| 20 | open_box_place_marker | 3 | 13 |
| 21 | open_drawer_put_marker | 3 | 13 |
| 22 | open_drawer_put_stapler | 3 | 13 |
| 23 | open_left_right_door | 1 | 19 |
| 24 | open_lid_place_filter | 3 | 13 |
| 25 | open_lid_put_spoon  /  open_lid_put_spoon_ep2 | 26 | 139 |
| 26 | open_microwave_door_put_bowl | 1 | 14 |
| 27 | open_microwave_door_put_green_duck | 3 | 13 |
| 28 | pick_ball_put_drawer | 3 | 13 |
| 29 | pick_block_drawer_to_plate | 2 | 34 |
| 30 | pick_bowl_cube  /  pick_bowl_cube_ep2 | 27 | 138 |
| 31 | pick_bowl_on_top_shelf | 2 | 13 |
| 32 | pick_coke_bottle_place_plate_ep1 | 25 | 113 |
| 33 | pick_cube_drawer_plate | 3 | 13 |
| 34 | pick_cube_place_plate | 1 | 9 |
| 35 | pick_cube_put_pot | 3 | 13 |
| 36 | pick_cube_transfer_place_basket_ep1 | 25 | 105 |
| 37 | pick_cup_on_left_table | 1 | 14 |
| 38 | pick_cylinder_place_drawer | 3 | 13 |
| 39 | pick_eraser_place_right_box | 3 | 13 |
| 40 | pick_green_cube_put_basket | 3 | 13 |
| 41 | pick_marker_draw_cross_ep1  /  pick_marker_draw_cross_ep2 | 23 | 155 |
| 42 | pick_marker_draw_line | 3 | 13 |
| 43 | pick_marker_place_bowl | 1 | 14 |
| 44 | pick_marker_place_cup | 3 | 13 |
| 45 | pick_marker_transfer_place_cup | 3 | 13 |
| 46 | pick_marker_transfer_place_plate_ep1  /  pick_marker_transfer_place_plate_ep2 | 29 | 172 |
| 47 | pick_mouse_basket | 3 | 13 |
| 48 | pick_mouse_place_laptop | 3 | 13 |
| 49 | pick_object_place_left_box_ep1  /  pick_object_place_left_box_ep2 | 25 | 175 |
| 50 | pick_orange_block_place_into_microwave | 3 | 247 |
| 51 | pick_orange_block_place_pot | 3 | 13 |
| 52 | pick_pen_transfer_plate | 3 | 13 |
| 53 | pick_pepsi_place_bowl | 3 | 13 |
| 54 | pick_pepsi_transfer_place_plate_ep1 | 25 | 113 |
| 55 | pick_place_chem_ep1  /  pick_place_chem_ep2 | 17 | 483 |
| 56 | pick_plate_from_drawer_put_pink_cube_ep1 | 25 | 115 |
| 57 | pick_red_marker_place_tray | 3 | 13 |
| 58 | pick_remote_controller_transfer_board | 3 | 12 |
| 59 | pick_spoon_place_rice_cooker | 3 | 13 |
| 60 | pick_tape_thread_marker | 3 | 13 |
| 61 | pick_test_tube_place_left_slot | 3 | 13 |
| 62 | pick_test_tube_place_middle_slot | 3 | 13 |
| 63 | pick_vial_place_middle_slot | 3 | 13 |
| 64 | pick_vial_place_right_slot | 3 | 13 |
| 65 | place_block_into_drawer | 2 | 30 |
| 66 | place_cube_pot_lid | 3 | 13 |
| 67 | place_doll_stapler_swap | 3 | 13 |
| 68 | place_duck_on_block | 1 | 15 |
| 69 | place_green_duck_from_drawer_to_pot | 3 | 13 |
| 70 | place_knife_in_drawer | 3 | 13 |
| 71 | place_pen_in_drawer | 3 | 13 |
| 72 | place_spoon_drawer_push | 3 | 13 |
| 73 | place_spoon_into_pot_cover_lid | 3 | 13 |
| 74 | place_spoon_on_plate | 3 | 13 |
| 75 | pour_cubes_into_box | 3 | 13 |
| 76 | pour_sausage_into_basket | 4 | 12 |
| 77 | pour_sausage_into_bowl | 3 | 13 |
| 78 | pour_sausage_into_pot | 1 | 33 |
| 79 | pour_water_transparent_cup_ep1  /  pour_water_transparent_cup_ep2 | 25 | 160 |
| 80 | pull_bottom_drawer_put_can_ep1  /  pull_bottom_drawer_put_can_ep2 | 20 | 182 |
| 81 | pull_bottom_drawer_put_duck_into_pot | 3 | 13 |
| 82 | pull_open_bottom_drawer | 3 | 12 |
| 83 | pull_open_drawer | 2 | 30 |
| 84 | pull_top_drawer_put_controller | 3 | 13 |
| 85 | push_middle_drawer | 3 | 13 |
| 86 | put_blackboard_eraser_in_transparent_box | 3 | 13 |
| 87 | put_doll_pink_plate_stapler_purple_plate_ep1 | 25 | 125 |
| 88 | put_mouse_basket_from_tray_ep1 | 25 | 125 |
| 89 | put_mouse_on_pot | 3 | 13 |
| 90 | put_pen_in_basket | 3 | 13 |
| 91 | put_stapler_blue_plate | 3 | 13 |
| 92 | put_stapler_top_drawer_and_close | 3 | 13 |
| 93 | put_two_objects_into_plate_and_box | 3 | 13 |
| 94 | stack_cup_cola | 5 | 245 |
| 95 | stack_cup_on_book | 3 | 13 |
| 96 | stack_green_cup_into_purple_cup | 1 | 14 |
| 97 | stack_pepsi_can_cup | 3 | 13 |
| 98 | stack_three_block | 2 | 47 |
| 99 | stack_three_color_cubes_ep1  /  stack_three_color_cubes_ep2 | 25 | 175 |

## Duplicates and quality exclusions

No repeated `source_hdf5` identity or exact Parquet-file content hash is present. However, episode/global-index metadata make Parquet hashes insufficient to detect repeated measurements. There are **18 exact video-content duplicate groups**, representing **six duplicate episode pairs**, with identical published sensor-statistic signatures and consistent failed outcomes. These are disclosed in GROUP_INDEPENDENCE_AUDIT.md. No raw files were deleted or relabeled.

A conservative provisional screen quarantining 173 constant-position episodes and retaining one representative per exact duplicate pair leaves **5,023 rows (4,377 failure / 646 success), still with both classes in all 100 canonical tasks**. This is a metadata-based planning count, **not a certified full multimodal cohort**. Raw per-episode QC and a frozen exclusion policy are required before evaluation.
