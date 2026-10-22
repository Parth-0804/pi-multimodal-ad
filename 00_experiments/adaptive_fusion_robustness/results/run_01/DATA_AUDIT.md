# DATA_AUDIT — passed with semantic limitations

Native high-level actions, not low-level sub-actions. All 4863 success fields are scalar Boolean. The accepted parser permits Boolean or integer 0/1 only, rejects strings/missing/floats/unsupported values, and maps failure=1-success. Native start/end, text-derived action identity and target match the old inventory exactly. Labels are source annotations, not model or sensor-derived targets.

Counts: 4551 native primary actions, 516 failures; the existing dual-complete cohort retains 4530 actions, 509 failures from 148 recordings. Exactly 21 primary actions were excluded upstream. No new relabeling or exclusions. Original eligibility requires a recognized action and valid interval, selected hand-camera usability and every selected sensor usable; the saved common cohort then requires >=32 interval frames while this experiment uses the unchanged 16-frame subset. The native/keyed reconciliation and each exclusion are in checks/native_annotation_audit.csv.

## Official issues reconciled against local native data

Official source read: https://github.com/TUWIEN-ASL/REASSEMBLE#%EF%B8%8F-file-comments (access record in provenance/official_dataset_notes.json). The source warns about final-action force/torque, camera coverage and hardware problems. Exact local final non-idle actions:

| recording_id | segment_id | text | failure | included | official_note |
| --- | --- | --- | --- | --- | --- |
| 2025-01-10-15-28-50 | 18 | Insert small gear. | 0 | True | hand camera missing initially |
| 2025-01-10-16-17-40 | 2 | Insert BNC. | 0 | False | hand camera unavailable |
| 2025-01-10-17-10-38 | 33 | Insert square peg 1. | 0 | True | hand camera missing initially |
| 2025-01-11-14-45-48 | 31 | Insert medium gear. | 1 | False | last action force/torque invalid |
| 2025-01-11-15-27-19 | 31 | Place waterproof. | 0 | False | last action force/torque invalid |
| 2025-01-11-15-35-08 | 14 | Insert small gear. | 1 | False | last action force/torque invalid |
| 2025-01-13-11-16-17 | 16 | Remove bolt 4. | 1 | False | gripper broke during last action |
| 2025-01-13-11-18-57 | 22 | Place square peg 2. | 0 | True | pose unavailable for last action |

The three warned force/torque final actions (31, 31 and 14 respectively) are already outside this cohort. In 2025-01-11-15-27-19 the preceding action 30 also lacks sufficient measured force/torque interval coverage and is excluded. Earlier actions remain. The gripper-break final action is excluded by the existing sensor-availability rule. The final missing-pose action is included: pose is not one of the five selected streams. Finite values never establish physical validity. Official warnings do not prove that every earlier action is unaffected; this residual uncertainty remains.

Camera warnings reconcile at action level: 2025-01-10-15-28-50 retains 16/18 actions, 2025-01-10-16-17-40 retains 0/2, and 2025-01-10-17-10-38 retains 31/33. No recording-wide exclusion was newly applied. Nonempty initial actions are keyed by native IDs, not assumed to start at segment 1.

## Images, time and sensor alignment

Camera: native hand MP4. All retained 16-frame lists match the exact native in-interval index formula: rounded linspace over eligible frame positions. This is uniform in frame index, not necessarily elapsed time. All selected timestamps are within native action bounds. The 16 predetermined fold_01/inner_fold_01 G examples span four action types, both outcomes and 16 distinct recordings, selected before viewing images or errors. Their native embedded MP4 payloads and cached files have identical SHA256; independently decoded same-codec frames have maximum pixel difference 0. All 32 original support-frame processed hashes match; the unchanged 16 are selected afterward. These bounded checks do not decode all videos again.

OpenCV BGR is explicitly converted to RGB. The exact installed processor configuration is checks/image_processor.json: resize={'height': 640, 'width': 640}, rescale=0.00392156862745098, normalize=False. Native corruption is quantized back to uint8 by nearest integer before this same processor. Sensor timestamps use the native shared absolute-time action interval; each stream retains its own clock. The frozen branch uses 512-point within-interval interpolation, no extrapolation, with long gaps masked; explicit fault masks additionally prevent bridging missing time. Existing float32 statistics and saved imputation remain unchanged. Three training-only native replays reproduce sensor features exactly; image probability error is below the fixed 1e-5 bound (checks/end_to_end_benchmark.json).

See audit_examples/ for 16 contact sheets, selected timestamps/native annotations and aligned 22-channel summaries. Machine checks cover all 16. Assistant visual observations cover examples 1,8,10,15 only, recorded in checks/visual_observations.json. Independent human semantic adjudication remains outstanding; these checks do not prove every annotation correct.

## Fixed branches, splits and encoder diagnostics

All 75 saved CNN/encoder/sensor fits (25 roles for each) were verified by component SHA256 and reconstructed fit IDs against exact memberships. Five outer assessment partitions are disjoint and cover the cohort; four inner held-out partitions cover T separately within each outer fold. G/C/prediction recordings are disjoint; E is excluded from each relevant inner fit/calibration. CNN OOF banks have exact T coverage and hash-bound historical F2 stackers. Existing noise run_02's 51 prediction hashes and lock were verified, but those outer predictions are excluded from new fusion fitting and normalization.

Source inspection and recorded upstream runtime evidence show that the hybrid encoder receives spatial backbone maps via projections, executes AIFI and FPN/PAN, then spatial means per returned scale are concatenated and 16 frame vectors are arithmetically averaged. CNN width 896; encoder width 768. Frame averaging discards temporal order. The decoder/proposal/detection paths are guarded; the new experiment executes CNN only. Native map shapes and upstream trace are referenced by identity in checks/encoder_path_evidence.json.

Training-only cached encoder diagnostics across all 25 saved roles: finite values throughout; near-constant (SD<=1e-6) dimensions 0–0; normalizer floors match saved G-only statistics; maximum absolute standardized values 6.436622–8.099807. Final saved head evaluation-mode weighted G training BCE ranges 1.063525–2.188748. This is not a retrained/tuned encoder or an assessment-score diagnostic.

## Decision

No concrete label-mapping, selected-frame alignment, cache identity or split defect was found in these bounded checks. Proceed under the locked resource and replay gates, retaining source-annotation/physical-validity uncertainty. No previous scientific file, cohort, result, deadline or STOP marker was changed.
