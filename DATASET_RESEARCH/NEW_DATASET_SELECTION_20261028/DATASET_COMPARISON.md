# Candidate comparison

Final scope is RoboFAC and FAILURE; CRIA was explicitly withdrawn by the researcher.

| Candidate | Verified native counts | Same-example numerical data | Visual evidence | Verdict |
| --- | --- | --- | --- | --- |
| RoboFAC — real | 480 failed / 122 successful actions; 1,204 camera videos | None listed for these actions | Actual grasp failure/success pair inspected | NO-GO for current real-world fusion objective |
| RoboFAC — simulation | 9,890 false / 4,729 true success flags in 14,619 metadata rows; not a clean cohort | HDF5 actions and privileged simulated states; two files checked | One linked simulated video inspected | NO-GO now; label/identity resolution needed |
| FAILURE | 147 failed / 82 successful joined recordings; 252 annotation rows overall | Audio; RGB/depth/timestamps joined by action and recording ID | Official pour demonstrations inspected; corpus review pending | GO FOR VISUAL PILOT for RGB+audio; full study conditional |

| Criterion | RoboFAC | FAILURE |
|---|---|---|
| Official sources | [Dataset, pinned](https://huggingface.co/datasets/MINT-SJTU/RoboFAC-dataset/tree/d18353ab36db82ff888ebc9e8485c9fa77e1b25b); [code, pinned](https://github.com/MINT-SJTU/RoboFAC/tree/638eb5320d409e4072710a0db26f1c0d68cef3de) | [Author project](https://air.cs.itu.edu.tr/projects/finonet.html); [repository, pinned](https://github.com/ardai/fino-net/tree/8196217bf52d17fdb7193e57619bd855b1723d4e) |
| Label types | Simulated episode `success` flag; original per-video success-detection QA; many other QA types have no binary outcome | Action/recording outcome; 1=failure, 0=success; no released intervals in annotation ZIP |
| Raw versus usable counts | 14,619 simulated metadata rows include duplicates and unmatched paths; real 602 action path groups lack numerical files | 252 labeled identities (163 failed, 89 successful); 229 have all listed modalities (147 failed, 82 successful) |
| Real/simulated distinction | 1,204 real-world camera videos; 10,120 simulated videos; all 679 HDF5 files are under simulation | Real Baxter tabletop executions; no simulation used for this audit |
| Numerical modality | Sampled simulated actions 8-D, articulation state 31-D, object state 13-D; no real sensor observations in checked files | Measured audio; one actual WAV verified mono, 16 kHz, PCM16; depth is an image modality, not joint/force measurements |
| Label/video/numerical joins | JSON `unique_id` to video; `episode_id` to `traj_N`; 31 trajectory groups verified in two HDF5 files, not all 679 | Composite `(action, recording_id)` joins annotation, RGB, depth, timestamps, WAV for 229 identities; precise sub-action audio timing unresolved |
| Independent groups | Keep camera views, UUID aliases, scene/reset-seed variants together; operator/session IDs unavailable | 229 recording groups, seven timestamp-derived UTC dates with both classes; dates are not verified session/operator identities |
| Download size | Released files total **25,771,018,505 bytes**; do not acquire in full | Official ZIP **10,197,520,375 bytes**; central-directory uncompressed sum **20,267,899,623 bytes** |
| Licensing | Dataset card declares MIT; code MIT | GitHub repository MIT; separately hosted data archive has no explicit data license located |
| Main limitations | No real-world numerical counterpart; disagreement between native labels; repeated identities; training/test QA video overlap | Small cohort; no force/joint state; no published session mapping; action/date/object confounding; missing 23 labeled recordings; event times unavailable |

No original labels were generated or inferred from names. RoboFAC failure-detection QA was used only after checking its five original prompt forms: every one asks whether the task succeeded. `Yes.` therefore means success and `No.` failure. Other QA categories and directory names were not converted into ground truth. This audit reports original flag/answer differences without deciding which source should override the other.

The proposed FAILURE pilot tests observability and episode-level RGB/audio feasibility. It does not establish equivalence to a visual-plus-proprioceptive/force architecture. Full-study readiness remains conditional on the handoff gates.
