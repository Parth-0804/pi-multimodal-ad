"""Write this source audit's human-readable reports from measured artifacts."""
import csv
import hashlib
import io
import json
import platform
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from acquisition import ROOT


def load(name):return json.loads((ROOT/'checks'/name).read_text())
def write(name,text):
    path=ROOT/name
    if path.exists():raise FileExistsError(path)
    path.write_text(text.strip()+'\n')
def mdtable(columns,rows):
    return '| '+' | '.join(columns)+' |\n| '+' | '.join(['---']*len(columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in rows)


if __name__=='__main__':
    robo=load('robofac_counts.json');identity=load('robofac_extended_identity_screen.json');failure=load('failure_counts.json')
    groups=load('failure_candidate_date_groups.json');pilot=load('FAILURE_PROPOSED_PILOT.json')
    rsha=robo['revision'];gsha='638eb5320d409e4072710a0db26f1c0d68cef3de';fsha='8196217bf52d17fdb7193e57619bd855b1723d4e'
    rurl=f'https://huggingface.co/datasets/MINT-SJTU/RoboFAC-dataset/tree/{rsha}'
    furl=f'https://github.com/ardai/fino-net/tree/{fsha}'
    compressed=sum(x['compressed_payload_bytes'] for x in pilot);expanded=sum(x['uncompressed_payload_bytes'] for x in pilot)
    comparison=mdtable(['Candidate','Verified native counts','Same-example numerical data','Visual evidence','Verdict'],[
        ['RoboFAC — real','480 failed / 122 successful actions; 1,204 camera videos','None listed for these actions','Actual grasp failure/success pair inspected','NO-GO for current real-world fusion objective'],
        ['RoboFAC — simulation','9,890 false / 4,729 true success flags in 14,619 metadata rows; not a clean cohort','HDF5 actions and privileged simulated states; two files checked','One linked simulated video inspected','NO-GO now; label/identity resolution needed'],
        ['FAILURE','147 failed / 82 successful joined recordings; 252 annotation rows overall','Audio; RGB/depth/timestamps joined by action and recording ID','Official pour demonstrations inspected; corpus review pending','GO FOR VISUAL PILOT for RGB+audio; full study conditional'],
    ])
    write('README.md',f'''
# Independent dataset selection — labels first, 2026-10-28

This is a source-level feasibility audit for Parth's REASSEMBLE-derived fusion study. Final active candidates: **RoboFAC and FAILURE**. The researcher withdrew CRIA during the audit. Previously acquired CRIA files are retained unchanged and excluded from the decision; no further CRIA inspection, acquisition or visual review was undertaken after that instruction. No CRIA report is produced.

**Recommended next step: a blinded FAILURE RGB-plus-audio visual pilot.** This is permission to propose a pilot, not evidence that fusion improves performance or approval to implement/train an audio architecture. If measured robot proprioception or force/torque is mandatory, neither remaining candidate currently passes.

{comparison}

Read [DATASET_COMPARISON.md](DATASET_COMPARISON.md), [ROBOFAC_LABEL_AUDIT.md](ROBOFAC_LABEL_AUDIT.md), [FAILURE_LABEL_AUDIT.md](FAILURE_LABEL_AUDIT.md), [GROUP_INDEPENDENCE_SCREENING.md](GROUP_INDEPENDENCE_SCREENING.md), [VISUAL_FEASIBILITY_SCREENING.md](VISUAL_FEASIBILITY_SCREENING.md), [FINAL_DATASET_RECOMMENDATION.md](FINAL_DATASET_RECOMMENDATION.md) and [RESEARCHER_HANDOFF.md](RESEARCHER_HANDOFF.md).

Original sources and HTTP range evidence are preserved in `source_evidence/` with individual SHA-256 receipts. Recounted tables and exceptions are in `checks/`. Inspect [NATIVE_LABEL_EXAMPLES.csv](NATIVE_LABEL_EXAMPLES.csv) and [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json). Source-frame contact sheets are in `visual_screening/`; these are an unblinded source screen, not a blinded validation experiment.

No complete dataset or pilot was downloaded. No neural network, CNN feature extraction, training, or GPU experiment was run. Existing MSM, Handover, REBOOT, REASSEMBLE and historical pilot evidence were not changed. No files were staged or committed.
''')
    write('DATASET_COMPARISON.md',f'''
# Candidate comparison

Final scope is RoboFAC and FAILURE; CRIA was explicitly withdrawn by the researcher.

{comparison}

| Criterion | RoboFAC | FAILURE |
|---|---|---|
| Official sources | [Dataset, pinned]({rurl}); [code, pinned](https://github.com/MINT-SJTU/RoboFAC/tree/{gsha}) | [Author project](https://air.cs.itu.edu.tr/projects/finonet.html); [repository, pinned]({furl}) |
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
''')
    simsources='`source_evidence/robofac/files/simulation_data/**/*.json` (679 original trajectory sidecars)'
    tasktable=mdtable(['Real-world task path','Failed actions','Successful actions'],[[k,v.get('No.',0),v.get('Yes.',0)] for k,v in identity['realworld_classes_by_task'].items()])
    write('ROBOFAC_LABEL_AUDIT.md',f'''
# RoboFAC native-label and data audit

**Decision: NO-GO for the current real-world visual-plus-numerical experiment.** A simulated study is a different scientific question and is not recommended before resolving the native label and identity issues below.

## Source identity and license

The official [Hugging Face release]({rurl}) is pinned to **{rsha}**. The official code is pinned to **{gsha}**. The dataset card declares MIT and the repository includes an MIT license. The complete `dataset_files_with_sizes.json` inventory contains 12,739 files, totaling 25,771,018,505 bytes. `file_tree.json` is a 1,000-entry preliminary page and was **not** used as a complete inventory. Complete `siblings` metadata with sizes and LFS hashes was used instead.

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

{tasktable}

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
''')
    actiontable=mdtable(['Action','All labeled: failed / success','Joined: failed / success','Joined total'],[[x['action'],f"{x['failed_label_1']} / {x['successful_label_0']}",f"{x['joined_failure']} / {x['joined_success']}",x['all_modalities_listed']] for x in failure['per_action']])
    missingtable=mdtable(['Action','Labeled IDs missing a complete join'],[['place','6, 47'],['push','18 (depth present; RGB/audio absent)'],['put_on','31–50']])
    head=load('failure_archive_head.json')
    write('FAILURE_LABEL_AUDIT.md',f'''
# FAILURE / FINO-Net native-label and data audit

**Decision: GO FOR VISUAL PILOT for episode-level RGB-plus-audio classification.** Full architecture adaptation is conditional; this release supplies no robot proprioception or force/torque. No model result is inferred from this audit.

## Pinned original sources and release identity

The [author project](https://air.cs.itu.edu.tr/projects/finonet.html) links the [official repository]({furl}) and `annotation.zip`. Repository revision: **{fsha}**. The annotation ZIP is **1,121 bytes** and contains five original text members. Their byte sizes and individual SHA-256 values are recorded in `SOURCE_PROVENANCE.json`.

The official data URL is `http://160.75.159.4/data/failure.zip`. Anonymous HEAD and bounded HTTP Range requests succeed. Its size is **10,197,520,375 bytes**; Last-Modified is `{head['headers']['Last-Modified']}` and ETag is `{head['headers']['ETag']}`. This is an unversioned data URL: the ETag and central-directory digest are acquisition identifiers, not a publisher's semantic version or full ZIP SHA-256. The complete ZIP was not downloaded or hashed. Its **53,165** directory entries enumerate **20,267,899,623** uncompressed bytes. This listing was read using roughly 6.78 MB of ZIP64/central-directory ranges.

The repository includes MIT licensing. No explicit separate license for the externally hosted raw archive was located; verify data-use terms before redistribution/full study. There is no authentication bypass. The GitHub API was rate-limited; public Git and pinned raw files provided the same official repository evidence.

## Annotation schema and label meanings

The original ZIP contains `place_annotation.txt`, `pour_annotation.txt`, `push_annotation.txt`, `put_in_annotation.txt`, `put_on_annotation.txt`. Each is CSV text with **`name,label`** only. The native target is an entire action/recording outcome. Source notebook cell 4 explicitly treats `bag_label==0` as successful and `bag_label==1` as failed. Its source URL is pinned in the provenance.

The archive has **252 distinct labeled identities: 163 failure (1), 89 success (0)**. No duplicate composite `(action,name)` or invalid binary class was found. The actual complete-modality cohort has **229 recordings: 147 failure, 82 success**, positive prevalence **{147/229:.6%}**. This matches the original FINO-Net paper's 229-recording table, not the annotation ZIP's larger inventory.

{actiontable}

The [original paper](https://arxiv.org/html/2011.05817v2) defines goal-oriented failure and treats small target deviations as success. It reports synchronized RGB/depth/audio and 16 kHz audio. The [extended paper](https://arxiv.org/html/2305.04639) discusses additional recordings and failure types; those results do not establish that the old downloadable ZIP contains the extension. The hosted file is dated 2021, and no extended failure-type or onset archive was located. Its 229 joined recordings must not be reported as the later extended dataset.

## Original-file join and missing records

The verified join is composite action and recording ID:

```text
annotation.zip!<action>_annotation.txt: name,label
failnet_dataset/rgb_imgs/<action>/<name>/frame*.png
failnet_dataset/rgb_imgs/<action>/<name>/frame*.txt
failnet_dataset/depth_imgs/<action>/<name>/frame*.tiff
failnet_dataset/audio/<action>/<name>.wav
```

For all 229 eligible labeled recordings, every stored RGB frame has a same-stem depth image and timestamp file, and a nonempty WAV is listed. The stored RGB sequences contain **34–138 frames**, so sixteen distinct source file positions exist for every joined recording. No RGB/depth or RGB/timestamp stem discrepancy occurs within this cohort. These are inventory checks, not full payload decodes, full audio validation or a duplicate-content scan.

There are **23** labeled IDs without complete modalities:

{missingtable}

Two additional recordings, `place/28` and `put_in/28`, have payload entries but no original binary annotation. They are excluded. There are 231 WAVs and 229 RGB recording directories in the source listing. An identity is not labeled by its directory name or inferred from neighboring IDs.

All source rows and exceptions are preserved in `checks/failure_native_annotation_records.csv`, `failure_counts_by_action.csv`, `failure_counts.json`, and `failure_archive_inventory.json`.

## Audio, timestamps and numerical channels

Only **measured audio** is available as a suitable nonvisual numerical stream. A selectively extracted original `audio/push/5.wav` has **16,000 Hz**, one channel, 16-bit PCM, 1,075,840 samples and **67.24 seconds**. ZIP CRC verification and SHA-256 identify that exact payload. Counts do not assume all WAVs share its encoding; that remains a pilot check.

No force, torque, joint-state, kinematic or commanded-action files were found in the complete ZIP directory. RGB/depth image intensities are not substitutes for those measurements. PCM sample amplitude has digital units; calibration to acoustic pressure is not provided. Depth physical units/calibration were not verified.

First and last original RGB timestamp text files were read and CRC-checked for **all 229** eligible recordings. Endpoints are finite and strictly ordered, spanning **34.90–135.77 seconds**. This establishes endpoint ordering only; interior timestamps were not all retrieved. The sampled `push/5` RGB endpoints span 66.40 seconds while its audio spans 67.24 seconds. There is no corresponding absolute WAV start timestamp in the release listing. The 0.84-second difference cannot be assigned to either endpoint. Do not claim precise audio/video alignment or attach arbitrary local failure labels to full-action audio.

The public notebook expects an annotation `start` field and string-like recording names, while the linked original annotation ZIP has integer names and **no `start` column**. That loader cannot be reproduced unchanged from these released annotations. No event onset, failure mode, recovery interval or frame-level label is available in this ZIP. A valid initial target is **whole-action outcome**, using sixteen ordered frames covering that same recorded action and audio statistics from its paired WAV. A time-local failure classifier needs additional native onset and alignment evidence.

## Independent groups and observability

There are seven candidate UTC recording dates, obtained from original timestamp values; every date contains both outcomes. These are observed dates, not asserted author-provided session IDs. Several actions occur on only one date, so held-out date performance can conflate task and date shift. The robot is Baxter; operator and object-instance identity tables were not found.

Official successful and failed pour GIFs show a gripper, cups, interaction and spilled material. Their exact recording IDs and audio counterparts are not supplied. They show that the physical failure can be visible in some source demonstrations, not that all 147 failures are observable or that the released RGB camera matches these crops. Objects/backgrounds differ across these demonstrations and may confound outcome. Blinded corpus-linked review remains essential.

The next proposed pilot is ten complete recording identities (five successful/failed action pairs), matched on action, timestamp-derived day and endpoint duration. Object/view matching remains UNKNOWN until reviewed. Proposed files require **{compressed:,} compressed member bytes** and **{expanded:,} extracted bytes**; HTTP/local-header overhead and optional depth are additional. This pilot is planned only and was not acquired.
''')
    grouptable=mdtable(['UTC date','Failed (1)','Successful (0)','Total'],[[k,v.get('1',0),v.get('0',0),sum(v.values())] for k,v in sorted(groups.items())])
    write('GROUP_INDEPENDENCE_SCREENING.md',f'''
# Group-independence screening

This is feasibility screening, not a frozen evaluation protocol. No frame-level random split is proposed. All source windows, crops, modalities and camera views of an action must share a group, and all preprocessing/model selection/fusion fitting must remain inside training groups.

## FAILURE

Use `(action, recording_id)` as the minimum source identity: numeric recording ID alone collides across actions. There are 229 labeled complete-modality recordings. Original first/last timestamp files were retrieved for every recording and verified against ZIP CRCs; seven observed UTC dates contain both classes:

{grouptable}

Seven-fold leave-date-out evaluation is class-defined on both sides in every fold: all held-out dates and their complements contain failures and successes. This is a possible outer sensitivity analysis; it does not establish seven independent operators or true sessions. Group-based inner validation must use only the remaining dates. Splits need no test-result inspection to define them.

Important confounding: push occurs only on 2018-02-17, place only on 2018-02-18, and put_on only on 2018-03-19. Pour covers 2018-07-11/12; put_in covers 2018-02-18 and 2018-07-04/05. Holding out some dates also holds out an action; report this explicitly. Leave-action-out across five actions has both classes in every fold but tests task shift, not same-task replication. Episode-disjoint stratified grouping is possible, but weaker concerning shared recording conditions. Object IDs, operator IDs and camera-session reset identities remain unavailable.

Avoid letting adjacent recordings from one session cross partitions when session boundaries can later be established. Timestamp dates are a transparent conservative proxy, not proof of absence of duplicates. All payload members must be hash-screened in the actual pilot before claiming duplicate-free examples. No full corpus payload hash scan occurred here.

## RoboFAC

Real data have 602 episode-path groups and two views per group. Every one of six task directories has both outcomes; counts are in ROBOFAC_LABEL_AUDIT.md. Keep views together. No corresponding real numerical recording exists in the audited release.

Simulation metadata reuse 326 UUIDs; 76 UUIDs have conflicting success flags. Scene, original reset seed, camera variations and related injected-error trajectories can create dependent examples. Union repeated UUIDs and original scene/reset lineage when available. Exact kinematic content hashes are distinct for all 679 HDF5 files, which does not prove independent resets. No defensible independent numerical cohort or class-support split is frozen for this candidate while the label/link issues remain unresolved.

The official training and test QA files overlap by 6,715 video paths. Reusing that division would leak source episodes into both partitions for this classifier.
''')
    write('VISUAL_FEASIBILITY_SCREENING.md','''
# Initial visual-feasibility screen

Only RoboFAC and FAILURE were visually reviewed. CRIA was withdrawn and its downloaded previews were not examined.

This screen uses genuine source recordings and deterministic contact sheets, with no generated imagery, CNN features or learned predictions. Eight ordered source positions span each preview. Contact sheets are unblinded and are not evidence of independent human rater agreement. Uniform eight-frame previews can miss short events; native clips must be watched during the next review.

| Source example | Object and gripper | Relevant event | Assessment |
|---|---|---|---|
| RoboFAC real InsertCylinder episode 0, above camera | Cylinder, fixture and gripper visible | Failed grasp/no object transfer is visible in the sampled sequence | VISIBLE for this failure; full corpus UNKNOWN |
| RoboFAC real InsertCylinder episode 100, above camera | Lift and transfer visible | Placement/insertion visible; exact hole contact partly occluded | PARTIALLY VISIBLE for fine contact; task progress visible |
| RoboFAC simulated UprightStack trajectory UUID 24df13c8… | Robot and objects visible at a distance | Object displacement/fall visible late in sequence | PARTIALLY VISIBLE; simulator state cannot be called physical sensing |
| FAILURE author pour_s GIF | Gripper, source cup and receiving vessel visible | Material transfer and final placement visible | VISIBLE demonstration; original recording identity UNKNOWN |
| FAILURE author pour_f GIF | Gripper, vessels and spilled material visible | Material remains/spills outside intended vessel | VISIBLE demonstration; original recording identity UNKNOWN |

Artifacts:

- [RoboFAC simulation](visual_screening/RoboFAC_source_01.jpg)
- [RoboFAC real native No. answer](visual_screening/RoboFAC_source_02.jpg)
- [RoboFAC real native Yes. answer](visual_screening/RoboFAC_source_03.jpg)
- [FAILURE official successful pour](visual_screening/FAILURE_official_pour_s.jpg)
- [FAILURE official failed pour](visual_screening/FAILURE_official_pour_f.jpg)

Exact source filenames, frame counts and sampled indices are in `checks/source_preview_audit.json`; source hashes and pinned URLs are in provenance. The existing OpenCV decoder could read container properties but failed to decode AV1 pixels. The existing repository FFmpeg binary then decoded only the three selected RoboFAC clips on CPU, with hardware acceleration disabled and one decoder/filter thread. No environment packages were installed. ffprobe was unavailable on PATH, so reported preview timing is container frame count/fps rather than a full packet-timestamp audit.

The two FAILURE GIFs differ in vessel appearance and background. They are not matched comparison pairs and cannot validate visual learnability or episode labels. The next pilot must retrieve source RGB frames linked to native annotations and paired audio, retain the full camera view, and include contact-region crops only as supplementary views. A reviewer must see label-free chronological sequences before accessing the native key. Rate object/gripper visibility and actual failure observability separately. Record UNKNOWN if a failure cannot be judged, and keep exclusions independent of model performance.

RoboFAC's visible real failures do not repair its missing numerical modality. FAILURE's visible demos justify a corpus-linked visual pilot, not a completed multimodal cohort or a claim that audio adds value.
''')
    pilotrows=[]
    for pair in range(1,6):
        normal,failed=[x for x in pilot if x['pair']==pair]
        pilotrows.append([pair,normal['action'],normal['recording_id'],failed['recording_id'],normal['first_timestamp_date_UTC'],f"{normal['span_seconds']:.2f} / {failed['span_seconds']:.2f}"])
    pilottable=mdtable(['Pair','Action','Success ID (0)','Failure ID (1)','UTC date','RGB endpoint span s: success / failure'],pilotrows)
    write('FINAL_DATASET_RECOMMENDATION.md',f'''
# Final dataset recommendation

**Recommend FAILURE for the next small blinded visual-plus-audio pilot.** This recommendation is based on independently verified original labels and same-action modality inventories, not publication performance. No candidate currently establishes a real-world visual-plus-force/joint-state cohort. CRIA was removed at the researcher's request.

RoboFAC is NO-GO for the current real-world multimodal target because numerical counterparts are absent. Its simulation data have unresolved label/identity issues and contain simulator states rather than the required real observations. FAILURE receives **GO FOR VISUAL PILOT** for a clearly declared RGB+audio question; the eventual experiment remains CONDITIONAL GO until visual observability, modality completeness, licensing and group design are reviewed.

## Proposed prediction target

One prediction per complete original manipulation recording: native **1=failed action, 0=successful action**. Use sixteen ordered RGB frames from that same action and statistical summaries of its paired measured audio. An outcome label must not be propagated as a time-local failure label to arbitrary partial windows. There is no valid released failure-onset timestamp in the annotation ZIP. The detector target differs from failure-mode classification, anomaly anticipation and robot-sensor fusion.

This is an explicit audio adaptation to be reviewed, not an automatic replacement of the numerical modality. If the thesis requires measured proprioception/force as its second modality, the recommendation is **NO-GO for both remaining candidates pending new data**, and this audio pilot should not be represented as fulfilling that requirement.

## Minimum corpus-linked review

Five successful/failed pairs, one per action, chosen by same date and nearest endpoint duration, with lower numeric IDs breaking ties. This uses no model performance and makes no assumption that objects or views match:

{pilottable}

For each of these ten identities obtain sixteen uniformly spaced existing RGB frame files, the same-stem original timestamp files, and the corresponding WAV. There are **160 RGB images, 160 timestamp text files and 10 WAVs**. All proposed original members and byte sizes are enumerated in `checks/FAILURE_PROPOSED_PILOT_MEMBERS.json`. Proposed compressed member bytes total **{compressed:,} ({compressed/1e6:.3f} MB)**; extracted bytes total **{expanded:,} ({expanded/1e6:.3f} MB)**. Allow about **0.25 GB** for payload plus retained compressed ranges, additional small metadata, and diagnostic contact sheets; all estimates exclude optional depth. Fetching the complete ZIP is unnecessary if byte ranges remain supported.

Required supporting source files are the already preserved original annotation ZIP, original central-directory inventory and timestamp-derived identity table. Preserve original CRCs and compute per-member SHA-256 on acquisition. Verify every decoded image and WAV, distinct frame positions, ordering, timestamps, audio duration, object/view matching, and duplicate-content hashes. Do not label-reorder frames or optimize offsets against outcomes.

Object identity is currently UNKNOWN; closest duration does not establish scene matching. A blinded reviewer should explicitly rate it. The sample is for diagnosing feasibility, not estimating accuracy: it has 50% failures by design whereas the joined cohort has 64.192% failures. If the sparse frames miss the failure, add a declared denser sequence from the same action rather than changing its ground truth.

Before a full experiment, confirm data-use terms, characterize alignment uncertainty, choose a group-disjoint design accounting for task/date confounding, freeze the training-only selection/fusion protocol, and obtain researcher review. This audit does not authorize acquisition of that pilot or any training.
''')
    examples=[]
    common={'dataset_revision':fsha,'source_file':'source_evidence/failure/annotation.zip'}
    native=list(csv.DictReader((ROOT/'checks/failure_native_annotation_records.csv').open()))
    for row in pilot:
        src=next(x for x in native if x['action']==row['action'] and x['recording_id']==row['recording_id'])
        examples.append(dict(dataset='FAILURE',**common,original_member=src['source_member'],source_locator='line '+src['source_line'],
            record_identity=row['action']+'/'+row['recording_id'],native_label_field='label',native_label_value=row['native_label'],
            native_meaning='failure' if row['native_label'] else 'success',same_example_numerical='WAV listed; payload validation remains pilot-wide',notes='whole action; no native onset'))
    real=list(csv.DictReader((ROOT/'checks/robofac_test_native_detection_records.csv').open()))
    for video in load('robofac_source_preview_selection.json'):
        if not video.startswith('realworld_data/'):continue
        row=next(x for x in real if x['video']==video)
        examples.append(dict(dataset='RoboFAC real',dataset_revision=rsha,source_file='source_evidence/robofac/files/'+row['source_files'].split(' | ')[0],
            original_member='',source_locator=row['uuid']+'/annos/Failure detection',record_identity=video,native_label_field='assistant answer to success question',
            native_label_value=row['native_failure_detection_answer'],native_meaning='failure' if row['native_failure_detection_answer']=='No.' else 'success',
            same_example_numerical='NOT RELEASED',notes='do not join to simulated HDF5'))
    trajectory=list(csv.DictReader((ROOT/'checks/robofac_native_trajectory_records.csv').open()))
    for row in [x for x in trajectory if x['video_listed']=='True'][:3]:
        examples.append(dict(dataset='RoboFAC simulation',dataset_revision=rsha,source_file='source_evidence/robofac/files/'+row['source'],original_member='',
            source_locator='episodes/episode_id='+row['episode_id'],record_identity=row['video'],native_label_field='success',native_label_value=row['success'],
            native_meaning='environment success flag; not a frame anomaly label',same_example_numerical=row['h5'],notes='listed join; exact internal HDF5 join not verified for this row'))
    with (ROOT/'NATIVE_LABEL_EXAMPLES.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(examples[0]));writer.writeheader();writer.writerows(examples)
    write('RESEARCHER_HANDOFF.md',f'''
# Independent researcher handoff

Final candidates: RoboFAC and FAILURE. CRIA was withdrawn after initial acquisition and was not considered further. No existing historical study, trained checkpoint, raw corpus or running REASSEMBLE process was changed. No pilot acquisition, model training or GPU experimentation was started.

**Decision to review:** FAILURE is the best justified next visual pilot, specifically for action-level **RGB plus audio**, using 229 originally labeled joined recordings (147 failure, 82 success). It is not a force/proprioception dataset. RoboFAC has 602 real action path groups (480 failed, 122 successful) but no real numerical payload; its simulation flags cannot currently be treated as a clean replacement cohort.

Review these questions before authorizing a pilot:

1. Is measured audio an acceptable thesis modality, explicitly distinct from force/joint-state fusion? If not, neither remaining candidate qualifies.
2. Do independent recomputations recover 252 annotation identities and 229 complete joins, rather than the later paper's extended cohort?
3. Are whole-action labels appropriate? The ZIP has no onset field, and the source notebook expects a missing `start` column.
4. Are same-date/action pairs sufficiently comparable in object and camera context? The planned member list currently cannot establish that.
5. Which grouping claims are defensible? Seven observed dates have both classes, but task/date confounding and unknown operator/object identity remain.
6. Can use of the externally hosted raw data be confirmed under appropriate terms?

The exact proposed ten-example pilot is in FINAL_DATASET_RECOMMENDATION.md and `checks/FAILURE_PROPOSED_PILOT*.json`. It requires {compressed/1e6:.3f} MB compressed member data or {expanded/1e6:.3f} MB extracted, plus range/header/diagnostic overhead. No full ZIP download is needed. No candidate was selected from test/model performance.

## Four-eye reproduction from preserved evidence

Review all native examples in NATIVE_LABEL_EXAMPLES.csv against the original files and their SHA-256 receipts. Recompute counts with:

```bash
ma_thesis_env/bin/python -B DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/code/audit_sources.py
ma_thesis_env/bin/python -B DATASET_RESEARCH/NEW_DATASET_SELECTION_20261028/code/validate_delivery.py
```

These commands use preserved active-candidate sources and regenerate this audit's check tables. They do not train or download a dataset. Historical CRIA functions remain in source as an execution trace but are disabled in all entry points. `acquire_annotations.py`, `inspect_failure_archive.py` and `screen_failure_groups.py` document exact bounded network methods; they are not necessary for recounting the preserved evidence. Public API discovery hit GitHub's rate limit; pinned raw/Git HTTPS evidence was used. A fresh full acquisition reproduction was not performed.

Read SOURCE_PROVENANCE.json, `checks/validation.json`, and the individual source receipts for hashes, software, commands, HTTP statuses, byte ranges and limitations. Preview images are an unblinded initial screen; ask the second reviewer for blinded corpus-linked visibility judgments before any modeling decision. No accuracy, AP, fusion benefit, robustness, or learned-weight-transfer result is supplied by this audit.

## Deliverables

- README.md
- DATASET_COMPARISON.md
- ROBOFAC_LABEL_AUDIT.md
- FAILURE_LABEL_AUDIT.md
- NATIVE_LABEL_EXAMPLES.csv
- SOURCE_PROVENANCE.json
- GROUP_INDEPENDENCE_SCREENING.md
- VISUAL_FEASIBILITY_SCREENING.md
- FINAL_DATASET_RECOMMENDATION.md
- RESEARCHER_HANDOFF.md

Sources, checks, code and five initial source contact sheets are kept in their named subdirectories. CRIA_LABEL_AUDIT.md is intentionally omitted under the revised scope. Stop here for independent researcher review.
''')
    print('Reports and native examples written; provenance/validation finalized separately.')
