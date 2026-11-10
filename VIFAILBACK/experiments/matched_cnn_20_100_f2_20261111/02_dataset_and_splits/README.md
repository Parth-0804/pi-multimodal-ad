# Verified dataset and fitting roles

The current eligible cohort contains **4,382 native episodes:3,753 failures,629 successes,99 canonical tasks**. Failure prevalence is0.8564582382. All eligible labels were joined back to109 original annotation files and the native-to-converted metadata. The original5,202 episodes contain4,545 failures and657 successes. The820 exclusions remain excluded; no episode or task55 was restored.

The cohort SHA-256 is `69ef64b012f683c5c8be7882c7e047675f88ed6a448f53c3aa21f432e9858560`. The unchanged original12-job split manifest SHA-256 is `ad003bba25de31072612b6a3346690087ecb9f8c94f9558d2663fe99da150231`. Split assignment is label-blind and canonical-task-disjoint. Session/operator/object-instance independence is unverified.

The first frozen outer identity is0 and its first inner identity is0. No performance metric selects these identities. The pilot preserves `outer0_inner0` exactly:its original `ids.A` remains the788-episode fusion meta bank. Its final outer assessment is obtained separately from `outer0_final.ids.A`.

| Pilot role | Episodes | Tasks | Failures | Successes |
| --- | ---: | ---: | ---: | ---: |
| Gradient training T |1430|26|1250|180|
| Checkpoint selection V |534|9|461|73|
| Probability calibration C |523|9|477|46|
| Fusion meta bank, original inner A |788|22|666|122|
| Final outer assessment |1107|33|899|208|

All five pilot roles have distinct episode IDs and disjoint task groups. Each role includes every eligible episode belonging to its declared tasks. Full20 uses all12 unchanged original jobs:one final refit and three inner assessments for each of three outer folds. For every outer fold, the three inner A sets cover the outer-training pool exactly once and exclude outer assessment.

Every visual condition uses the same16 label-blind uniformly rounded timestamps in each of`cam_high`, `cam_left_wrist`, `cam_right_wrist`:48 images form one episode. Source-frame indices,times and48 RGB hashes are retained in the referenced original manifest. All13,146 eligible camera streams are present with unchanged sizes/mtimes; the original full-decode/frame audit is preserved. Actual live decoding rechecks selected RGB hashes. No video dataset or decoded-frame cache was duplicated.

Both original-pretrained and REASSEMBLE-donor feature banks are complete,finite,FP32 and hash-verified with shape`[4382,3,16,896]`. This module pools with the exact historical NumPy`array.mean((1,2))` operation to`[4382,896]`; returned pooled arrays are read-only. The sensor bank contains4,384 original conservative-core rows and280 features. Native episode IDs select the4,382 eligible rows, preserving source order explicitly. The28 channels are14 measured positions,12 nonplaceholder velocities and2 gripper-effort fields; they are not calibrated force/torque. The10 statistics are stat-major mean,std,median,min,max,q25,q75,range,RMS,and normalized-progress slope. No population standardizer is fitted by data preparation.

All36 original multiview V1 fits retain100 consecutive epochs,source/configuration identities and valid selected/final/prediction hashes. Every historical selected epoch also satisfies this study's macro-AP/lower-weighted-BCE/earliest selection rule. The pilot seed42/outer0_inner0 checkpoint selected epoch11. Reuse additionally checks the retained FP32 classifier,114,945 head parameters,AdamW settings,cosine100 final state,RNG state and exact T-only feature moments. The trainer's bounded numerical equivalence preflight remains a separate prerequisite; these artifact checks alone do not establish execution equivalence.

The donor is the completed REASSEMBLE full-CNN seed42/job2 fit:100 executed epochs,selected47. Its selected checkpoint SHA is`5700e8912cf360c845087923e4b417631a886daf928e1655b1031c9ac27c8ce0`. All115 CNN tensor names/shapes/dtypes are compatible with the pinned original archive. Learned values differ in the stem and every convolutional stage, while running moments remain unchanged. Only CNN tensors transfer; target heads and target T-only moments are new. Source classifiers,scalers,calibrators,sensor models and F2 coefficients do not transfer.

The frozen protocol deliberately retains source-pilot sensor role semantics:meta probabilities use the existinginner0 sensor fit and outer probabilities use the existingouter-final sensor fit. These are distinct fitted sensor models,shared identically across paired visual arms. This is disclosed in fusion reporting and must not be described as a single sensor model applied to both roles.

Evidence files:

- `DATASET_AND_SPLIT_VERIFICATION.json`:current native joins,source hashes,role counts,feature banks,video availability and reuse proofs.
- `EXCLUSION_AND_SCHEMA_VERIFICATION.json`:additional exclusion and exact280-feature schema checks,preserving the first immutable evidence file.
- `FIT_PARTITIONS.json`:the12 exact original jobs,including episode IDs and task groups.
- `PILOT_ROLES.json`:unchanged pilot source job,meta IDs and separate outer assessment IDs.
- `../01_protocol_and_source_evidence/FROZEN100_REUSE_VERIFICATION.json`:all36 checked V1 histories and pilot optimizer/checkpoint identities.
- `../01_protocol_and_source_evidence/DONOR_SOURCE_VERIFICATION.json`:source receipt,selected checkpoint,original archive hashes,compatible tensor shapes and changed CNN tensors.
- `../01_protocol_and_source_evidence/APPROVED_SOURCE_STOP_VERIFICATION.json`:the approved25-fit REASSEMBLE stop and all25 current completion/model/prediction hash chains. Process and GPU occupancy checks remain separately required before training.

Preparation is CPU-only and idempotent. It creates compact evidence only inside this study namespace. Original inputs,features,models,configuration and historical reports remain read-only.
