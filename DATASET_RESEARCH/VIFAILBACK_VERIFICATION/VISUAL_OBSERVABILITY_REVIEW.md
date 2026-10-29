# Real visual observability review

**Open the label-free gallery before reading this report or the source key.** The gallery is [MATCHED_EXAMPLE_GALLERY/index.html](MATCHED_EXAMPLE_GALLERY/index.html).

## Sampling and review procedure

Ten task-matched success/failure pairs were selected from native records to cover gripper pose, gripper state, task planning and an external-intervention control. Within each chosen original task directory, select the success/failure combination with the closest frame length; tie by original converted episode index. Task/object matching is a design constraint, not proof that poses, distractors, lighting or conditions are identical.

Per-execution frame policy: **floor(k×(N−1)/15), k=0..15**. Both outcomes use the same sixteen chronological positions from first to last. All three cameras use those same indices. No avoid/correct keyframe, failure type, frame-label mask, sensor anomaly or outer-test result determines frame positions, crop, or time offset. There are **320 timepoints / 960 camera images**, not 960 independent prediction examples. Each source image can be opened at original 640×480 resolution.

The enlarged-region view is a fixed center crop (x/y 20–80%) for every camera/class. It is supplementary and can omit an off-center object; full views remain authoritative. There are twenty corresponding sensor plots, with uniform sampled times marked and no outcome/keyframe marks in the blinded pages.

Per-case identities/outcomes were masked with a seeded random permutation. Initial analyst observations were recorded and SHA-256 locked before opening the per-case native key. All 20 three-camera overviews and task instructions were examined; ambiguous cases B09, B11, B18 and B02 additionally received full-size **already selected** sequences. No new favorable frames were selected. The record is `MATCHED_EXAMPLE_GALLERY/INITIAL_BLINDED_SCREEN.json`; its lock hash is `76fa95ab3d2e1df110ec41599e1f572408497958ab42d3757c5801846760c5a7`.

This is an **AI-assisted initial analyst screen**, not an independent human experiment or inter-rater validation. The analyst knew the selection was balanced; per-case outcome mapping remained masked until judgments were saved. The researcher and second reviewer should complete the blank review form independently before seeing the key or these notes.

## What was observed

After unblinding, **9 of the 10 native failures** had clear physical failure evidence in the fixed frames. The remaining native failure, **B02**, has visible marker pickup/return but the required drawing stroke is ambiguous at these sixteen positions. This is a descriptive observability count, not classifier accuracy, recall, an exhaustive failure taxonomy or a corpus-wide rate.

Examples include apparent failed grasps (B08/B09/B15/B18), cube outside its intended basket after transfer (B06), wrong-target placement (B19), unsuccessful/incorrect contact or object interaction (B03/B07), and visible external human interference (B20). Fine alignment/contact success can still be partially obscured. Sparse frames do not establish failure-onset time or prove that a short drop event occurred between sampled positions. Native category labels remain unchanged even when our observed physical description is different in granularity.

| Blind ID | Native outcome after unblinding | Native category | Initial physical failure evidence | Observation |
| --- | --- | --- | --- | --- |
| B01 | success | success | none | Marker transfer into the opened drawer is visible; no definite failure observed. |
| B02 | failure | task planning | possible | Marker pickup and return are visible; the required line stroke cannot be judged confidently at these fixed temporal samples. |
| B03 | failure | gripper 6d-pose | clear | The book moves during interaction while the cup does not appear placed onto it; wrong-object/contact or placement deviation is visible. |
| B04 | success | success | none | Spoon goes into the pot and the lid is placed over it. |
| B05 | success | success | none | Pouring and material in the receiving basket are visible; complete material transfer cannot be verified from these samples. |
| B06 | failure | gripper state | clear | Blue cube appears outside the basket on the tabletop after the handoff/placement attempt; dropping or failed placement is visible. |
| B07 | failure | gripper 6d-pose | clear | No completed pour; food remains on the green plate, and the neighboring basket is displaced/lifted. |
| B08 | failure | gripper state | clear | Marker stays on the tabletop despite a grasp attempt; drawer operation does not complete the requested transfer. |
| B09 | failure | gripper state | clear | Tube remains beside the rack after an apparent empty/unsuccessful grasp; no upright placement is visible. |
| B10 | success | success | none | Marker is lifted, a dark line is visible, and the marker returns to the cup; detailed stroke semantics remain a limitation. |
| B11 | success | success | none | Wrist view shows the plug approaching and apparently seating in the socket; electrical connection is not independently measured. |
| B12 | success | success | none | Cube handoff followed by the cube being inside the basket is visible. |
| B13 | success | success | none | Tube is lifted and an upright tube is visible at the rack after release. |
| B14 | success | success | none | Cup is lifted and placed on the closed book. |
| B15 | failure | gripper 6d-pose | clear | Gripper approaches the tube but the tube remains in the source cup; no successful transfer occurs. |
| B16 | success | success | none | Mouse is moved from the tray into the basket. |
| B17 | success | success | none | Tube is lifted from the cup and placed into the rack. |
| B18 | failure | gripper 6d-pose | clear | The plug remains on the work surface rather than being successfully grasped/inserted; fine connector contact is partly occluded. |
| B19 | failure | task planning | clear | Spoon is placed onto the white plate rather than into the red pot; the requested lid closure is not completed. |
| B20 | failure | human intervention | clear | Human hands enter and interfere with the task; the robot does not complete the requested transfer. |

## Pair identities, conditions and limits

The table below is **unblinded**. Original full paths, videos, source frame indices and timestamps are retained in the separate key and audit manifests.

| Pair | Original task directory | Success blind ID / episode | Failure blind ID / episode | Native failure category | Frames: success / failure |
| --- | --- | --- | --- | --- | --- |
| 1 | hold_socket_plug | B11 / 521 | B18 / 532 | gripper 6d-pose | 395 / 238 |
| 2 | grasp_cube_place_shelf | B13 / 371 | B09 / 385 | gripper state | 236 / 142 |
| 3 | pick_cube_transfer_place_basket_ep1 | B12 / 1453 | B06 / 1574 | gripper state | 421 / 423 |
| 4 | pick_test_tube_place_left_slot | B17 / 3456 | B15 / 3467 | gripper 6d-pose | 259 / 227 |
| 5 | stack_cup_on_book | B14 / 4908 | B03 / 4918 | gripper 6d-pose | 173 / 173 |
| 6 | pour_sausage_into_basket | B05 / 3718 | B07 / 3723 | gripper 6d-pose | 269 / 139 |
| 7 | open_drawer_put_marker | B01 / 775 | B08 / 789 | gripper state | 464 / 233 |
| 8 | pick_marker_draw_line | B10 / 1823 | B02 / 1827 | task planning | 212 / 214 |
| 9 | place_spoon_into_pot_cover_lid | B04 / 3666 | B19 / 3669 | task planning | 413 / 285 |
| 10 | put_mouse_basket_from_tray_ep1 | B16 / 4428 | B20 / 4570 | human intervention | 170 / 169 |

The target objects are comparable within each task, but initial object positions, workspace arrangements, distractors, duration and arm poses visibly differ across some pairs. In particular, different drawer/pot/plate placements and extra distractor cubes prevent claiming exact condition matching. Source directory names can be imperfect descriptions: the `grasp_cube_place_shelf` samples' native task instruction and images concern a test tube/rack. Use the original instruction and source identity rather than deriving semantics from that directory name.

The high camera usually exposes task progress and outcome context; wrist cameras can reveal grasp/connector contact but often face away or become occluded. All three perspectives are provided; none is declared universally informative. The human-intervention example contains an obvious person and should be analyzed separately from endogenous manipulation failure. B02 is retained as uncertain, not relabeled or swapped for a clearer positive.

Recommendation: obtain independent human ratings of failure visibility, object/gripper visibility and context matching. Freeze any observability-based subset transparently, retain exclusions and acknowledge spectrum/selection bias; do not use pilot visibility judgments to cherry-pick model test examples. The pilot selection is intentionally balanced and covers chosen tasks, unlike the full 87.37% failure-prevalence release.
