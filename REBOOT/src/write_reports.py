"""Evidence-grounded feasibility reports. Does not fit or evaluate any model."""
from pathlib import Path
from collections import Counter,defaultdict
import datetime as dt
import hashlib
import html
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys

import pandas as pd

from source_audit import ROOT,REPO,RUN,write


def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()

def put(path,text):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)


def main():
 inventory=json.loads((ROOT/'00_dataset_overview/PINNED_DATASET_INVENTORY.json').read_text())
 gate=json.loads((ROOT/'02_labels_and_annotations/LABEL_GATE_SUMMARY.json').read_text())
 pilot=json.loads((ROOT/'00_dataset_overview/PILOT_SELECTION.json').read_text())
 numeric=json.loads((ROOT/'03_video_sensor_alignment/NUMERICAL_ACQUISITION_MANIFEST.json').read_text())
 gallery=json.loads((ROOT/'04_visual_failure_review/GALLERY_COMPLETE.json').read_text())
 videos=json.loads((ROOT/'01_raw_dataset/PILOT_VIDEO_DOWNLOAD_MANIFEST.json').read_text())
 metadata_checks=json.loads((RUN/'manifests/REPOSITORY_METADATA_VALIDATION.json').read_text())
 metadata_limits=[r for r in metadata_checks if r['status']!='PARSEABLE']
 metadata_note='''The episode-index Parquet for `REBOOT26/usbc_recovery_install` at `0ef0b37f0601fbafcc3bab07195a1fb5e756c6b4` cannot be parsed: its196,608 published bytes lack the required Parquet footer. The local file exactly matches the official LFS size and SHA256 (`c2edd7790273c14ba3ff63d7dbb1d0368d8ca3086503e66277c0edd3de2af160`), and a second HTTP206 request confirms the same final8 bytes. It is a published-file limitation, not an unverified local truncation; the bytes remain unchanged. Episode indices and frame-length totals match native `info.json` for the other37 repositories (2,103 entries). The USB-C recovery-install collection's33 episodes/29,633 frames remain **info-declared, not independently index-verified**. None of the ten selected pilot demonstrations uses this file. Evidence: `runs/20261028T113139848361Z-independent-feasibility-v1/evidence/USBC_METADATA_SOURCE_IDENTITY_RECHECK.json` and the run's `manifests/REPOSITORY_METADATA_VALIDATION.json`.'''
 sample=next(r for r in inventory if r['repo_id']=='REBOOT26/sample_recovery-demonstration')
 full=next(r for r in inventory if r['repo_id']=='REBOOT26/16mm-cylinder_recovery_install')
 rows=[];duplicates=defaultdict(list);by_repo={}
 for r in inventory:
  tree=[x for x in json.loads((REPO/r['file_tree']).read_text()) if x['type']=='file'];by_repo[r['repo_id']]={x['path']:x for x in tree}
  tasks=pd.read_parquet(REPO/r['local_root']/'meta/tasks.parquet');native_tasks=[str(x) for x in tasks.index]
  rows.append({'repo_id':r['repo_id'],'revision':r['revision'],'episodes':r['total_episodes'],'frames':r['total_frames'],'fps':r['fps'],
   'remote_bytes':r['total_remote_bytes'],'native_task_descriptions_json':json.dumps(native_tasks),
   'is_recovery_named_collection':'recovery' in r['repo_id'].lower(),'is_sample_named_collection':'sample' in r['repo_id'].lower(),
   'native_failure_annotation_files_json':json.dumps(r['annotation_candidates']),
   'numerical_features_json':json.dumps([k for k,v in r['features'].items() if v.get('dtype')!='video']),
   'depth_feature_count':sum('depth' in k for k in r['features']),
   'rgb_camera_count':sum(v.get('dtype')=='video' and not v.get('info',{}).get('video.is_depth_map',False) for v in r['features'].values())})
  for f in tree:
   if f['path'].startswith('videos/'):
    duplicates[f['lfs']['oid']].append({'repo_id':r['repo_id'],'revision':r['revision'],'path':f['path'],'bytes':f['size']})
 coverage=[]
 for item in rows:
  slug=item['repo_id'].split('/')[-1].lower()
  if 'sample' in slug:continue
  if '16mm-cylinder' in slug:obj='16mm-cylinder'
  elif '16mm-bar' in slug:obj='16mm-bar'
  elif 'm12' in slug:obj='M12'
  elif 'rj45' in slug:obj='RJ45'
  elif 'nema' in slug:obj='NEMA1-15'
  elif 'han10e' in slug:obj='HAN10E'
  elif 'rca' in slug:obj='RCA'
  elif 'usbc' in slug or 'usb-c' in slug:obj='USB-C'
  elif 'usb-a' in slug or 'usba' in slug:obj='USB-A'
  else:obj='UNRESOLVED'
  coverage.append({'repo_id':item['repo_id'],'object_inferred_from_repo_name':obj,'direction_inferred_from_repo_name':'remove' if 'remove' in slug else 'install',
   'collection_role_inferred_from_repo_name':'recovery' if item['is_recovery_named_collection'] else 'expert_candidate','episode_entries':item['episodes'],
   'not_a_physical_session_or_label_identity':True})
 pd.DataFrame(coverage).to_csv(ROOT/'00_dataset_overview/OBJECT_TASK_COLLECTION_COVERAGE.csv',index=False)
 pd.DataFrame(rows).to_csv(ROOT/'00_dataset_overview/SOURCE_REPOSITORY_INVENTORY.csv',index=False)
 dup_rows=[{'sha256':digest,'sources':entries} for digest,entries in duplicates.items() if len(entries)>1]
 write(ROOT/'06_evaluation_feasibility/DUPLICATE_VIDEO_IDENTITIES.json',dup_rows)
 a=by_repo[sample['repo_id']];b=by_repo[full['repo_id']]
 shared=[p for p,r in a.items() if p.startswith('videos/') and p in b and r['lfs']['oid']==b[p]['lfs']['oid']]
 def episodes(r):return pd.concat([pd.read_parquet(p) for p in (REPO/r['local_root']/'meta/episodes').rglob('*.parquet')]).set_index('episode_index')
 aa,bb=episodes(sample),episodes(full)
 same=[]
 for i in aa.index:
  fields=['length']+[f'videos/{camera}/{key}' for camera in ['observation.images.cam_high','observation.images.cam_low','observation.images.cam_left_wrist','observation.images.cam_right_wrist'] for key in ['chunk_index','file_index','from_timestamp','to_timestamp']]
  if all(aa.loc[i,k]==bb.loc[i,k] for k in fields):same.append(int(i))
 write(ROOT/'06_evaluation_feasibility/SAMPLE_FULL_RECORDING_ALIAS_EVIDENCE.json',{'shared_exact_video_chunks':len(shared),'sample_video_chunks':sum(p.startswith('videos/') for p in a),
  'all_sample_videos_are_exact_original_recovery_video_copies':len(shared)==sum(p.startswith('videos/') for p in a),
  'identical_episode_video_mapping_and_lengths':same,'sample_repo_id':sample['repo_id'],'full_recovery_repo_id':full['repo_id'],
  'action':'Keep all source files unchanged; use one recording identity group for aliases in any future split; no raw deduplication'})
 if len(same)==60:upper_unique=gate['sum_repository_episode_counts_including_sample_not_unique_demonstrations']-60
 else:upper_unique=None
 specification={'source_project':'https://nanayawoa.github.io/REBOOT/','source_collection':'https://huggingface.co/REBOOT26/datasets',
  'repository_inventory_revision_keys':'SOURCE_REPOSITORY_INVENTORY.csv','repositories':len(inventory),
  'sum_repository_episodes_not_unique':sum(r['total_episodes'] for r in inventory),'upper_bound_after_known_sample_alias_only':upper_unique,
  'episode_count_basis':'Sum of native info.json declarations;37 repository episode indices agree; one published index is unparseable',
  'parseable_repository_episode_indices_confirmed':len(metadata_checks)-len(metadata_limits),
  'independently_index_verified_episode_entries':sum(r.get('episode_rows',0) for r in metadata_checks),
  'published_episode_metadata_limitations':metadata_limits,
  'claimed_project_demonstrations':2160,'expert_named_repository_count':18,'expert_named_episode_entries':1090,'recovery_named_episode_entries_including_sample':1046,'recovery_named_episode_entries_excluding_sample':986,'native_task_description_strings':sorted({x for r in rows for x in json.loads(r['native_task_descriptions_json'])}),
  'camera_features':['cam_high','cam_low','cam_left_wrist','cam_right_wrist'],'nominal_fps':30,
  'verified_numerical_columns':numeric[0]['native_schema_columns'],'feedback_position_dimensions':14,
  'verified_force_torque_columns':[],'command_column':'action; excluded from proposed primary sensor features',
  'depth_payload_validation':'Four depth columns in full-release schema and metadata; deliberately not downloaded for RGB/state feasibility',
  'collection_time_driver_revision_and_physical_exposure_timestamps':'not supplied in inspected release metadata',
  'native_sensor_units':'Position field names supplied; exact units/calibration not declared in native feature contract',
  'normal_failure_binary_target_available_for_training':False}
 write(ROOT/'00_dataset_overview/DATASET_SPECIFICATION.json',specification)
 counts=pd.read_csv(ROOT/'02_labels_and_annotations/PHASE_PILOT_SUPPORT_COUNTS.csv')
 phase_table='| Requested phase | Native candidate records | Onset inside phase under tested one-based interpretation | Verified pairs | Diagnostic recovery episodes |\n|---|---:|---:|---:|---:|\n'
 for r in counts.itertuples():phase_table+=f'| {r.phase} | {r.native_failure_candidates} | {r.phase_onset_consistent_diagnostic_candidates} | 0/5 | {r.selected_diagnostic_recovery_episodes} |\n'
 source=f'''# REBOOT source and release audit

Snapshot: {dt.datetime.now(dt.timezone.utc).isoformat()}. Public primary sources only: [official project](https://nanayawoa.github.io/REBOOT/), [official collection](https://huggingface.co/REBOOT26/datasets), pinned dataset commits and the linked author repository. All downloaded metadata have byte counts and SHA256; no login, token or credential file was used.

The project describes 18 assembly tasks, expert/recovery demonstrations, four RGB-D viewpoints and five phases. The actual inspected collection has **38 repositories and 2,136 info-declared repository episode entries**, including the sample. The sample's **18 video chunks are exact SHA256 duplicates** of `16mm-cylinder_recovery_install`, with all60 episode video mappings/lengths identical. Removing just this known alias gives an upper bound of **2,076 distinct trajectories among the declared entries**; this is not a proof that every other entry is unique. The advertised2,160 count is not independently reproduced. Split repositories, nonstandard episode counts and sample duplication require reconciliation rather than silently truncating to the advertised count.

## Published episode-index limitation

{metadata_note}

By repository naming,18 expert-name collections contain1,090 entries and20 recovery-name collections (including the60-entry duplicate sample) contain1,046 entries; recovery-name entries excluding the sample sum986. These are source-name role assignments, not independently verified phase outcomes. Name-based object/direction coverage yields18 expert task combinations and17 recovery combinations; no RCA recovery-remove collection was found. The bar-recovery-remove repository contains18 episodes. `OBJECT_TASK_COLLECTION_COVERAGE.csv` makes this limited inference explicit. Native task prompts have36 distinct strings/wording variants, which must not be treated as36 independent physical tasks.

Only `sample_recovery-demonstration` releases `meta/phase.json` in the38 inspected pinned trees. Its60 records all declare `episode_type=recovery`; the other37 repositories have no discovered native phase/failure file. Expert/recovery membership of the other collections is inferred from repository naming and the project description, not a native per-phase success label. Native task instructions, repository IDs, original episode/frame indices and file mappings are preserved.

Four RGB streams are present: high, low, left wrist and right wrist. The decoded pilot uses640×480 AV1 at nominal30Hz. Full-release Parquet schemas contain four depth columns, while the sample omits depth. Depth arrays were not downloaded because this task requires RGB and numerical feedback, and the full depth-heavy data files are roughly0.5–0.6GB per episode. The numerical primary candidate is `observation.state`,14 joint/gripper position values; `action` is a distinct14-value command vector. No force/torque, velocity, effort or motor-current field exists in the inspected native feature schemas. Depth presence is schema/metadata verified, not calibrated-value verified.

The source fork is pinned in `runs/.../manifests/author_code_receipts.json`. Its current linked vendor plugin separately implements observations from driver joint outputs and target commands through `send_action`; this supports the state/command distinction. The actual collection-time plugin revision and explicit units/calibration are not recorded. Current vendor camera code reads latest frames asynchronously; it is supporting implementation context, not proof of the exact acquisition hardware timing used for these recordings.

The sample annotation supplies native operator IDs `op-00`/`op-01` and session strings `2026-04-15`/`initial`. They are preserved. Corresponding identifiers were not found for all expert/full-release episodes and cannot be invented from filenames. Native repository `train:0:N` slices are publication organization, not evidence of an independent evaluation split.

## What was actually acquired

- Pinned info/statistics/tasks/episode metadata and README files for all38 repositories; the official project page, author code and selected vendor source are saved as evidence.
- **10 diagnostic demonstrations**, covering two recovery candidates per requested phase and two same-object install expert-name candidates; **zero certified normal/failure pairs**.
- **16 complete shared video chunks**, {sum(r['bytes'] for r in videos):,} bytes ({sum(r['bytes'] for r in videos)/1024**3:.3f}GiB), all verified against official LFS SHA256 and size. A required chunk contains neighboring episodes; those neighbors are not selected or counted as reviewed examples.
- Eight complete small original sample Parquet files. For two expert episodes, only numerical columns and Parquet footer/pages were retrieved through validated HTTP206 byte ranges, totaling {sum(r['source_receipt'].get('range_bytes_downloaded',0) for r in numeric):,} bytes rather than two full depth-heavy files. Unmodified range fragments, Content-Range checks, individual hashes, pinned URL and official whole-file hash references are retained. **The whole large expert Parquet files were not downloaded or globally hash-verified**; the projected numerical columns have separate complete row/schema/hash checks.
- No whole-dataset download, CNN inference, classifier fitting or training.

See the metadata/video manifests under01, numerical acquisition under03 and the versioned run manifests for exact file paths, commits, bytes and hashes. Dataset cards state Apache2.0 while the project page states CC-BY4.0; the source declarations are preserved rather than silently reconciled.
'''
 put('00_dataset_overview/REBOOT_SOURCE_AUDIT.md',source)
 labels='''# Native annotation contract and limits

The authentic released file is preserved unchanged. It describes `phase_names`, six `tau_0..tau_5` boundaries, episode type/duration, `failure.originating_phase`, categorical `failure_mode`, `induced_at_frame`, `recovery_started_at_frame`, language descriptions, native operator and collection-session strings. It does not supply a certified negative interval, per-frame binary array, failure-resolution frame, explicit expert/recovery pair registry or annotation confidence.

A recovery demonstration is not failed throughout its duration. Neither induction-to-recovery-start nor the remainder of a phase is automatically a verified binary failure interval; recovery-start is not proof of failure-end. Expert-name membership also does not certify the temporal boundaries of a clean comparison phase. No binary target has been assigned to the diagnostic examples.

## Findings requiring resolution

- All60 `duration_frames` values are897; actual released lengths are898(54 episodes) or899(6). This may include a last-index versus count convention; that convention is not documented. It is reported, not silently corrected.
- The originating-phase values include0 and21 alongside1–5. No automatic0→1 or21→2 repair is applied.
-38 induction times lie outside the declared phase under a **tested one-based occurrence interpretation**. Because the field is named *originating* phase, it could refer to an earlier causal phase; this discrepancy requires an author definition and is **not proof that all38 labels are false**.
- Three records put recovery at/before induction under a shared-frame-clock interpretation, and one has nonmonotonic phase boundaries.
- The JSON names the plural `sample_recovery-demonstrations`, while the actual repository is singular `sample_recovery-demonstration`. The exact shared videos bind the sample to the full cylinder-recovery recording, but do not validate every annotation value or establish the undocumented plural alias.

Full per-record diagnostics, including original values, are in NATIVE_PHASE_RECORD_AUDIT.csv/JSON. All60 source annotations remain available. No frame-level labels, participant identities, success outcomes or corrected event times are invented.

## Requested pilot support

'''+phase_table+'''
The onset consistency column is a diagnostic filter, not a certified-label count. Only four raw Transport-origin records exist in this annotation file before any validity checks, so even five positive candidates for that phase cannot be obtained here. Complete metadata inspection found no phase-matched negative labels. Therefore the requested20 verified pairs cannot be assembled from the verified release evidence.

Ten diagnostic examples were still inspected to assess cameras and measurements. Candidate recovery windows include context before induction and after recovery-start; expert candidates show whole episodes. They are **not phase-matched comparisons or training-ready examples**. Window lengths/source collections can affect blind-review difficulty; no diagnostic review accuracy or fusion efficacy is calculated.
'''
 put('02_labels_and_annotations/ANNOTATION_CONTRACT_AND_LIMITATIONS.md',labels)
 align=f'''# Video and numerical-state validation

Ten demonstrations,8,980 numerical rows,40 camera views and640 selected original frames were validated. Every view has16 distinct native frame indices **and16 distinct decoded RGB contents**. Four source viewpoints are decoded with the existing CPU `libdav1d` FFmpeg binary, whose identity/hash is recorded. OpenCV's installed AV1 decoder failed, so it was not used; no environment/package or running-training modification was made.

For each source episode, the Parquet frame index is contiguous, timestamps are finite/monotone, and14-position state/command vectors have the expected shape. Video-file/chunk/episode offsets come from native episode metadata. Selected frame positions join native frame index/timestamp to original encoded video PTS; the largest nominal residual is **{gallery['maximum_nominal_dataset_to_encoded_PTS_residual_seconds']:.9f} seconds**.

This tiny residual reflects floating-point/printed PTS and nominal30Hz clock arithmetic. It is **not physical camera/sensor synchronization accuracy**. The release does not provide independently timestamped per-camera exposure/robot-feedback clocks, calibrated hardware latency, or complete camera synchronization traces, so physical timing uncertainty remains unverified. Selected-frame rows retain both native episode seconds and global source-video PTS.

`observation.state` and `action` differ in every selected example (mean absolute differences about0.0018–0.0047 in undeclared native position units). This proves distinct stored arrays, not an independently calibrated force sensor. Current vendor code supports position-feedback versus commanded-target semantics; the collection-time driver revision is unknown. No force/torque signal is substituted or invented.

The frame manifest binds each PNG/RGB hash to native sample/frame/time, source video, repository revision and fixed review crop. Source videos remain byte-identical to official hashes. H264 preview clips are labeled re-encoded review derivatives with original interval mappings; they are never used as model inputs. Context crops are display enlargements and are unsuitable for calibrated submillimetre geometry measurements. Source full-camera PNGs and original media remain available.

The entire decoded window and all four cameras are available in the randomized review gallery. Successful nominal timing checks alone do not establish visible abnormality or valid outcome labels.
'''
 put('03_video_sensor_alignment/VIDEO_SENSOR_ALIGNMENT_REPORT.md',align)
 review='''# Blinded researcher review protocol

Open `galleries/blinded_pilot_v1/index.html` first. The deterministic seed20261028 randomizes ten examples as B001–B010. Initial HTML contains no outcome/source-collection identity key. Four native camera names, full/context16-frame sequences, neutral motion clips and numerical position plots are available for each example. The manipulated object is the16mm cylinder; the intended target is its assembly-task-board fixture. A reviewer must identify the exact physical target and any occlusion; there is no invented object box or frame-level anomaly annotation.

Complete RESEARCHER_VISUAL_REVIEW_SHEET.csv (40 example/view rows) with reviewer/date, observed phase/event, visibility confidence, event-time estimate, occlusion and ambiguity. Keep failure visibility separate from nominal timestamp validity. Do not infer collision force, submillimetre clearance or physical cause from unavailable measurements. Then open UNBLINDED_LABEL_KEY.html / UNBLINDING_KEY.json to compare with the native descriptions and known annotation limitations.

The review is label-blinded at the initial display, not a controlled diagnostic-accuracy experiment: diagnostic windows differ in duration and expert candidates lack phase matching. Source collections can also differ visually. Do not calculate a certified visibility rate or classifier accuracy from these examples. Raw videos can contain laboratory context; no human identity is inferred. Human review cells remain blank.

Automated Codex observations in PRELIMINARY_AUTOMATED_OBSERVATIONS.md are separate, explicitly uncertified, and must not be copied into a supposedly independent human review. No model prediction exists in this task.
'''
 put('04_visual_failure_review/BLINDED_VISUAL_REVIEW_PROTOCOL.md',review)
 observations='''# Preliminary automated visual observations — not human certification

These notes come from Codex inspection of actual source-derived16-frame contact sheets, not from an independent human reviewer, trained anomaly model or native ground-truth replacement. The human review sheet remains blank and no new frame labels are created.

| Example/view | Preliminary observation | Limitation |
|---|---|---|
| B003, right wrist | At sampled frame270 the cylinder is between the fingers; by284 it is outside the open gripper and subsequently lies on the wood before being reapproached. This is a visibly useful coarse release/drop candidate. | The native induction is frame300; the visible transition between270 and284 may precede it. This is a coarse observation to review, not a corrected event label. |
| B003, high / left wrist | Overhead shows global arm motion but the contact region is small; the left wrist mostly shows the other arm/background. | A timestamp-correct view can have weak physical-event visibility. |
| B008, right wrist | Cylinder and approaching fingers are visible; gripper/object offset changes during the candidate pickup window. | Misalignment cause and exact onset are not independently certified. |
| B002, right wrist | Approach/closure and a cylinder remaining near the tray are visible. | A specific collision/jamming or force explanation cannot be certified from these images. |
| B002, low | The task board is distant and much relevant gripper motion is at/outside the top of view. | This view is a poor default for fine engagement inspection in this example. |
| B006, right wrist | Cylinder, gripper and target board region are visible during the short placement window. | Submillimetre alignment and true contact/seating are visually ambiguous; no force/torque channel resolves them. |
| B001, right wrist | Whole expert-name episode shows approach, transport and placement context. | Repository membership and a sparse sequence do not independently certify every phase as normal or the terminal outcome. |

The right wrist is a promising view for coarse cylinder-release events; this is a development-pilot observation, not a universal view ranking or held-out model result. The overhead camera supplies scene context. All four views, including unhelpful ones, are retained. Do not select a best test camera after examining model scores. Further review should prioritize the clearly observable Transport drop and macro pickup errors; fine placement/force-dependent failures require stronger native labels and human checks.
'''
 put('04_visual_failure_review/PRELIMINARY_AUTOMATED_OBSERVATIONS.md',observations)
 compatibility='''# REASSEMBLE/MSM architecture compatibility

Inspected actual sources: `src/reassemble/section1_features.py`, `section1_models.py`, `section1b.py`, `section2_models.py`, `MILLING DATASET/source/msm/{data,models,splits}.py` and `CROSS_DATASET_COMPARISON/src/external_eval/{features,data,models,evaluate}.py`. Their exact hashes are in the run software provenance. None were changed.

| Branch/component | Feasible reuse | Required REBOOT-specific work/gate |
|---|---|---|
| RGB input |16 real640×480 RGB frames from a fixed chosen view | New pinned LeRobot-v3 episode/video offset adapter; CPU AV1 decoder; retain original frame/time mapping. Freeze view and observation window before evaluation. |
| Frozen visual CNN | Existing pinned PekingU/rtdetr_r18vd ResNet R18vd backbone, spatial means of last3 maps→896 and16-frame temporal mean | New fold-fitted standardizer and896→128→1 head after trustworthy labels. No detector transformer or bounding-box head; no CNN executed here. |
| Numerical measurements |14 observed joint/gripper positions | New feedback-only allowlist and unit/clock documentation; mean, population std, RMS, min, max and peak-to-peak would give84 values. This differs from MSM90 and Handover36. Standardization must be fitted within training folds. |
| Commanded actions | Preserved for audit only | `action` must not be passed off as an independent measured sensor. Exclude from primary sensor model; any command-conditioned control needs separate explicit experimental labeling. |
| Sensor baselines | Balanced logistic and fixed strong sensor-only classifier can use verified position statistics | New labels/domain coefficients and train-only scaling; no force/torque, effort or velocity fabrication. Units/angular wrap handling need explicit methodology. |
| Averaging / F2 | Existing two-probability averaging; newly fitted logistic F2 on true group-OOF probabilities | No source fusion coefficients transferred; identity-safe2-inner OOF and3-outer design must first pass actual group/class gates. Currently blocked. |
| Quality-aware fusion | Existing DecisionGate plus explicit new label-free quality adapter could be investigated |14-channel quality context and availability flags differ from previous domains. Requires enough independent OOF support and matched static/augmentation controls; no evidence currently justifies training it. |
| Depth | Four full-release schema columns exist | Not needed for the requested RGB/state baseline; sample has none. Using depth would be a separate new architecture experiment and requires actual value/calibration validation. |

The existing16-frame mean is order-invariant. A visibly dynamic drop does not prove that this representation models temporal order; a separately preregistered temporal ablation may be useful later. Do not silently replace the representation or claim motion understanding.

Position feedback can encode robot phase and human recovery behavior. Diagnostic windows deliberately include recovery context and are not classification-ready inputs. A future detection protocol must define whether it is retrospective event recognition or early warning, freeze the causal time horizon and prevent recovery/future-action leakage. The current task trains no model and transfers no learned weights.
'''
 put('05_architecture_compatibility/REASSEMBLE_ARCHITECTURE_COMPATIBILITY.md',compatibility)
 feasibility=f'''# Leakage-safe evaluation feasibility

**Current supervised evaluation gate: BLOCKED.** Zero phase-matched normal/failure pairs and zero training-eligible binary examples are certified. This means unverified support, not that the dataset contains no physical failures. There is no scientifically valid split to materialize yet.

The38 repository entries do not define38 independent groups. All18 sample video chunks duplicate the full cylinder-recovery release, and all60 sample/full episode video offsets/lengths match. They must share recording identity in future splitting. Raw files are preserved; only non-destructive alias evidence is recorded. Expert/recovery relationships and paired events cannot be inferred from matching episode numbers across different repositories.

The released annotation metadata has two operator strings and two session strings (one `initial`), heavily imbalanced. The selected recovery diagnostics all share the provided `op-01`/`2026-04-15` metadata. Expert/session assignments are missing. Operators are not automatically physical experimental independence; task/object and collection session can be confounded. Native `train` slices are not a published leakage-safe classification evaluation.

With only this annotated object/session support and no verified negatives, three outer/two inner folds cannot pass. Splitting windows from the same episode, distributing identical sample/full copies, treating all recovery frames as positive, or inventing session IDs would be invalid fixes. No split-seed search, group substitution or fold reduction was performed.

## Defensible next protocol after prerequisites

1. Obtain/correct native phase conventions, event intervals and clean same-phase controls; retain original annotations plus a separately versioned, reviewer-signed correction/admission table. Audit onset versus cause semantics and failure-resolution meaning.
2. Bind stable episode, physical recording, paired expert/recovery run, operator, collection session and task/object IDs. Collapse exact media aliases only in an analysis registry; preserve raw files.
3. Use this visually inspected pilot as development data. Freeze camera, preprocessing, observation horizon, target and feature allowlist before assessing new holdouts. The current mismatched diagnostic windows cannot become model inputs without a separately reviewed protocol.
4. If sufficient independently collected groups with both classes remain in every training/assessment partition, preregister3 outer×2 inner group folds, seeds42/123/20261023, new frozen-CNN heads, feedback-only sensor models, averaging and true OOF F2. Group every window of the same physical recording/recovery pair together; assess at the native event/phase unit, not repeated frames. Apply train-only standardizers and group-aware uncertainty.
5. If that support does not exist, continue a qualitative feasibility study or collect a fixed new-session/task/object holdout. A task/object-disjoint alternative requires labels for several objects and explicitly changes the generalization claim. An exploratory recording-disjoint study can only make within-collection claims after duplicate/pair binding and class support; it does not certify session/task generalization.
6. Add quality gating only after clean OOF fusion is defensible, with predefined label-free quality variables, missing-branch behavior, unimodal/strong-sensor controls and exposure-matched augmentation.

Report all blocked/negative outcomes, per-group/per-seed counts and prevalence. Do not call position/recovery-behavior discrimination physical force anomaly detection or early failure prediction. No hypothetical fold/model metric is reported as an executed experiment.

Known sample/full deduplication reduces the2,136 repository-entry sum to an upper bound of{upper_unique}; remaining uniqueness, advertised-count reconciliation and full-release session binding remain open.
'''
 put('06_evaluation_feasibility/EVALUATION_FEASIBILITY.md',feasibility)
 proposed={'status':'PROPOSED_ONLY_BLOCKED_PENDING_LABEL_VISIBILITY_AND_GROUP_GATES','training_allowed':False,
  'primary_sensor_allowlist':list(next(r for r in inventory if r['repo_id']=='REBOOT26/sample_recovery-demonstration')['features']['observation.state']['names']),
  'primary_sensor_statistics':['mean','population_std_ddof0','rms','minimum','maximum','peak_to_peak'],'primary_sensor_dimensions':84,
  'excluded_primary_inputs':['action_commands','task_object_identity','operator_session_ids','future_recovery_information','invented_force_torque'],
  'visual_frames':16,'CNN':'Frozen original pinned RT-DETR R18vd CNN only','CNN_pooling':'Last3 spatial means and16-frame mean',
  'candidate_baselines':['visual','sensor_logistic','strong_sensor_only','averaging','F2_group_OOF'],
  'quality_gate':'Deferred until independent OOF support and matched controls justified',
  'outer_inner_target':[3,2],'seeds_if_feasible':[42,123,20261023],
  'grouping':'Verified physical recording/session and paired-run aliases, never raw repository membership alone',
  'split_definitions_created':False,'current_verified_binary_examples':0,'current_verified_pairs':0,
  'required_prerequisites':['resolved native annotation semantics/defects','verified matched clean/failure intervals','human visibility review','physical group/pair identities','independent class support','physical timing uncertainty and sensor unit clarification'],
  'alternative':'Qualitative pilot or new independent session/task/object holdout; no forced folds'}
 write(ROOT/'06_evaluation_feasibility/PROPOSED_EVALUATION_PROTOCOL.json',proposed)
 decision='''# REBOOT research decision

**CONDITIONAL GO — for further data curation and independent visual review. Model training is not authorized or scientifically ready.**

REBOOT has promising real, visibly observable coarse failures and usable14-position robot-state records, but the currently verified release does not yet provide trustworthy matched phase targets and independent evaluation support for the requested fusion experiment.

## Findings supported by actual files

1. **Contents:**38 pinned repositories with four RGB viewpoints, numerical joint/gripper positions, commanded actions and depth in full-release schema. The2,136 info-declared repository-entry count does not reproduce the advertised2,160; sample/full duplication must be accounted for. Episode indices verify2,103 entries across37 repositories; the remaining33 are declared in an info file whose published episode index is unparseable.
2. **Downloaded:** metadata for all38; ten bounded diagnostic demonstrations via16 shared original video chunks (about2.733GiB), eight small complete sample Parquet files and two expert numerical projections obtained from225,771 exact HTTP range bytes instead of unused depth. All full videos match official LFS hashes; projections have complete row/schema hashes and explicit partial-source limits.
3. **Native labels:** one released phase file with60 recovery records, phase bounds, origin/mode/induction/recovery descriptions and limited operator/session metadata. No certified phase-negative/control registry or full-release pairing table was found.
4. **Trustworthiness:** original labels are authentic released bytes, but indexing0/21, boundary/duration conventions, event ordering, causal-phase semantics and repository-name binding require resolution. Recovery membership is not whole-trial failure ground truth. No source value was corrected or used to manufacture binary labels.
5. **Visible events:** actual right-wrist frames show a useful cylinder release/drop candidate (B003). Other views can be occluded, distant or off-target. Fine placement/contact causes remain ambiguous. These are preliminary Codex observations; **independent human certification is pending**.
6. **Numerical measurements:**14 observed position fields and distinct14 commanded positions; no verified force/torque channel. Supporting current vendor source reads joint feedback separately from commands; collection-time revision, units/calibration and hardware timing remain undocumented.
7. **Alignment:** all40 views decode;640 distinct selected frames map to original nominal dataset timestamps and encoded PTS with a maximum1.22343µs arithmetic residual. This is **not hardware synchronization accuracy**. Physical exposure/feedback timing cannot be independently bounded from the supplied metadata.
8. **Eligible counts:** zero certified training examples/normal-failure pairs, ten technical/visual diagnostic examples. The four requested phases have14/13/4/14 native candidate records; available onset-consistent diagnostic counts are2/12/3/5 under an explicit unconfirmed one-based interpretation. No five-pair-per-phase claim is made.
9. **Architecture:** the frozen16-frame CNN and newly fitted head plus84 feedback statistics and new domain classifiers are technically plausible adaptations. F2 requires valid group-OOF targets/provenance first; quality gating is not yet justified. No model, feature-CNN forward or fusion fit was run.
10. **Unresolved:** corrected/clarified native annotations and clean controls, independent human visibility judgments, physical recording/session/pair binding, duplicate-safe class support, sensor units and physical timing uncertainty.
11. **Exact proposed experiments:** once these gates pass, freeze a primary camera/window/target and independent development/holdout boundary; compare newly fitted visual head, feedback-only logistic/strong sensor models, averaging and genuine OOF F2 under the feasible group design. Three-outer/two-inner folds and three seeds are conditional on real group/class support, not imposed. Quality-aware/missing-modality experiments require a later explicit protocol. The proposed configuration is in06; no experiment was launched.

The strongest next action is researcher review of the blinded gallery and annotation clarification/repair through a separately versioned evidence process, not training on the recovery/expert directory names. If those prerequisites cannot be resolved, the requested supervised REBOOT fusion evaluation should be a NO-GO; retain the qualitative findings rather than forcing a positive research result.
'''
 decision+='\n## Additional source-integrity limitation\n\n'+metadata_note+'\n'
 put('07_research_decision/REBOOT_RESEARCH_DECISION.md',decision)
 handoff='''# Researcher handoff — REBOOT

**Decision: CONDITIONAL GO for curation/visual review; training gate remains closed.**

The requested feasibility investigation is complete. All source data and earlier REASSEMBLE/MSM/Handover results are preserved. No training, CNN inference or fusion fitting occurred.

## Read/review in this order

- [Blind review gallery](../04_visual_failure_review/galleries/blinded_pilot_v1/index.html): ten neutral IDs, four cameras each, full/context16-frame views, actual motion clips and original numerical-state plots. Do not open the key first.
- [Blank human review sheet](../04_visual_failure_review/RESEARCHER_VISUAL_REVIEW_SHEET.csv):40 view/example rows; human review has not been filled by Codex.
- [Unblinding key after review](../04_visual_failure_review/UNBLINDED_LABEL_KEY.html) and [native annotation audit](../02_labels_and_annotations/NATIVE_PHASE_RECORD_AUDIT.csv).
- [Full research decision](REBOOT_RESEARCH_DECISION.md), [alignment findings](../03_video_sensor_alignment/VIDEO_SENSOR_ALIGNMENT_REPORT.md), [architecture changes](../05_architecture_compatibility/REASSEMBLE_ARCHITECTURE_COMPATIBILITY.md) and [evaluation gate](../06_evaluation_feasibility/EVALUATION_FEASIBILITY.md).

Real right-wrist imagery includes a promising physical drop, unlike a purely force-only hypothetical failure. That observation is preliminary and does not certify the annotation onset or every phase. Low/left-wrist views can be unhelpful; fine alignment remains uncertain. The native phase source has defects/semantic ambiguities, no verified phase-negative labels are available, and all sample video chunks duplicate the full cylinder-recovery repository. It would be invalid to assign all recovery frames positive labels or split sample/full copies apart.

The pilot therefore contains **10 diagnostic demonstrations, not20 verified normal/failure pairs**. Three-outer/two-inner group support is not established. Available sample operator/session metadata do not cover all collections. Numerical features are joint/gripper positions; force/torque is not present. Nominal clocks match, but hardware exposure synchronization is unverified.

Review the visible evidence, obtain authoritative label/group clarifications, then create a separately versioned corrected/admitted cohort before any approved modeling. All proposed models, gates and alternatives are documented; no synthetic labels, hidden positive claims, source rewrites or full dataset download were used.
'''
 handoff+='\n## Published metadata limitation\n\n'+metadata_note+'\n'
 put('07_research_decision/RESEARCHER_HANDOFF.md',handoff)
 readme='''# REBOOT independent multimodal feasibility investigation

**CONDITIONAL GO for further curation and independent visual review. Training remains blocked.**

- [Research decision](07_research_decision/REBOOT_RESEARCH_DECISION.md)
- [Researcher handoff](07_research_decision/RESEARCHER_HANDOFF.md)
- [Blinded four-view gallery](04_visual_failure_review/galleries/blinded_pilot_v1/index.html)
- [Human review sheet](04_visual_failure_review/RESEARCHER_VISUAL_REVIEW_SHEET.csv)
- [Source/release audit](00_dataset_overview/REBOOT_SOURCE_AUDIT.md)
- [Label contract and limitations](02_labels_and_annotations/ANNOTATION_CONTRACT_AND_LIMITATIONS.md)
- [Video/state alignment](03_video_sensor_alignment/VIDEO_SENSOR_ALIGNMENT_REPORT.md)
- [Architecture compatibility](05_architecture_compatibility/REASSEMBLE_ARCHITECTURE_COMPATIBILITY.md)
- [Evaluation feasibility](06_evaluation_feasibility/EVALUATION_FEASIBILITY.md)
- [Shared dataset workspace](../DATASET_RESEARCH/README.md)

Metadata for38 pinned repositories and a bounded ten-demonstration diagnostic pilot were audited. Only one phase-annotation source was found; it needs clarification and contains defects.16 original camera files were downloaded and hash checked,640 frames decoded, and14-position feedback separated from commands. No force/torque was invented. No binary targets, training splits or model scores were fabricated.

Folder conventions follow the previous MSM/Handover work: numbered research stages, immutable versioned inputs under01, source and tests, a unique run with configuration/evidence/manifests/reports/logs and a final decision/handoff. Exact source commits/hashes, download manifests, range-projection limits and human-review status are retained. All earlier dataset folders remain canonical in place; DATASET_RESEARCH supplies relative links rather than moving historical work.
'''
 readme+='\nThe final metadata audit confirms37 parseable episode indexes and flags one pinned USB-C recovery-install index whose published bytes lack a Parquet footer. Its source hashes match; its33 entries remain info-declared. See the source audit and handoff for the exact identity.\n'
 put('README.md',readme)
 # Separate, explicitly unmatched qualitative side-by-side comparison.
 key=json.loads((ROOT/'04_visual_failure_review/UNBLINDING_KEY.json').read_text())['examples'];expert=next(r for r in key if r['source_collection']=='non_recovery_named_repository')
 cards=['<meta charset="utf-8"><style>body{font:16px system-ui;margin:2rem}td{vertical-align:top}video{max-width:45vw}</style><h1>Expert/recovery candidate comparisons — unblinded diagnostics only</h1><p>These are not verified normal/failure pairs. The same whole expert-name episode is reused for context; no expert phase boundary or binary negative has been certified. Do not count the repeated expert as independent evidence. Review the blinded gallery first.</p>']
 for item in key:
  if item['native_annotation'] is None:continue
  cards.append('<h2>'+html.escape(item['investigated_phase'])+' / '+item['masked_id']+'</h2><table><tr><th>Expert-name whole-episode context (unverified phase negative)</th><th>Native recovery candidate / annotated context (unverified target)</th></tr><tr>')
  for ident in [expert['masked_id'],item['masked_id']]:cards.append('<td><video controls preload="none" width="600" src="galleries/blinded_pilot_v1/'+ident+'/cam_right_wrist/preview.mp4"></video></td>')
  cards.append('</tr></table>')
 put('04_visual_failure_review/UNBLINDED_CANDIDATE_COMPARISONS.html',''.join(cards))
 # Consolidate only downloaded source bytes; projected data remain explicitly derived.
 receipts=json.loads((ROOT/'01_raw_dataset/METADATA_DOWNLOAD_MANIFEST.json').read_text())
 download_rows=[{'source_url':r['url'],'local_path':r['path'],'bytes':r['bytes'],'sha256':r['sha256'],'scope':'complete source metadata/file'} for r in receipts]
 download_rows +=[{'source_url':r['url'],'local_path':r['local_path'],'bytes':r['bytes'],'sha256':r['sha256'],'scope':'complete original video; official LFS hash verified'} for r in videos]
 for r in numeric:
  sr=r['source_receipt']
  if 'range_receipts' in sr:
   for part in sr['range_receipts']:download_rows.append({'source_url':part['source_url'],'local_path':part['raw_fragment_path'],'bytes':part['bytes'],'sha256':part['sha256'],'scope':part['Content-Range']+'; full-file hash unverified'})
  else:download_rows.append({'source_url':sr['url'],'local_path':sr['path'],'bytes':sr['bytes'],'sha256':sr['sha256'],'scope':'complete original sample data Parquet; official LFS hash verified'})
 pd.DataFrame(download_rows).to_csv(ROOT/'01_raw_dataset/DOWNLOAD_MANIFEST.csv',index=False)
 write(RUN/'config/resolved_config.json',{'task':'Independent REBOOT multimodal feasibility; no training','source_inventory':str((ROOT/'00_dataset_overview/PINNED_DATASET_INVENTORY.json').relative_to(REPO)),
  'pilot_selection':pilot,'maximum_requested_pairs':20,'actual_verified_pairs':0,'actual_diagnostic_episodes':10,'minimum_free_disk_bytes':15*1024**3,
  'camera_names':list(gallery.keys()) if False else ['cam_high','cam_low','cam_left_wrist','cam_right_wrist'],'frames_per_view':16,
  'blinded_random_seed':20261028,'temporal_alignment':'Native row timestamp + native episode video offset; physical exposure uncertainty not established',
  'training_allowed':False,'binary_targets_assigned':False,'independent_human_review':'PENDING'})
 source_paths=[*(ROOT/'src').glob('*.py'),*(ROOT/'tests').glob('*.py')]
 relevant=[REPO/p for p in ['src/reassemble/section1_features.py','src/reassemble/section1_models.py','src/reassemble/section1b.py','src/reassemble/section2_models.py',
 'MILLING DATASET/source/msm/data.py','MILLING DATASET/source/msm/models.py','MILLING DATASET/source/msm/splits.py',
 'CROSS_DATASET_COMPARISON/src/external_eval/features.py','CROSS_DATASET_COMPARISON/src/external_eval/data.py','CROSS_DATASET_COMPARISON/src/external_eval/models.py','CROSS_DATASET_COMPARISON/src/external_eval/evaluate.py']]
 write(RUN/'software_provenance.json',{'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=REPO).strip(),
  'tracked_git_status':subprocess.check_output(['git','status','--short','--untracked-files=no'],text=True,cwd=REPO),'python':sys.version,
  'packages':{p:importlib.metadata.version(p) for p in ['numpy','pandas','pyarrow','pillow','matplotlib','pytest']},
  'commands':['REBOOT/src/source_audit.py','REBOOT/src/select_pilot.py','REBOOT/src/acquire_pilot.py','REBOOT/src/build_gallery.py','REBOOT/src/write_reports.py','REBOOT/src/validate_feasibility.py'],
  'execution_environment':'ma_thesis_env/bin/python -B; all acquisition/decoding/projection/plotting on CPU',
  'new_source_hashes':{str(p.relative_to(REPO)):sha(p) for p in source_paths},'inspected_existing_implementation_hashes':{str(p.relative_to(REPO)):sha(p) for p in relevant if p.exists()},
  'FFmpeg':{'path':gallery['decoder_path'],'sha256':gallery['decoder_sha256'],'software_decoder':'libdav1d','GPU_used':False},
  'no_model_training_or_CNN_inference':True,'existing_datasets_results_checkpoints_modified':False})
 write(ROOT/'07_research_decision/DECISION_STATUS.json',{'decision':'CONDITIONAL_GO','scope':'Further curation and independent human visual review only',
  'training_allowed':False,'verified_training_examples':0,'verified_matched_pairs':0,'technical_diagnostic_demonstrations':10,
  'human_visibility_review':'PENDING','full_model_training_started':False,'next_action':'Researcher blinded review plus authoritative label/group clarification',
  'pipeline_stage':'FEASIBILITY_INVESTIGATION_COMPLETE'})
 print('REPORTS_COMPLETE','CONDITIONAL_GO','training_allowed=False',flush=True)


if __name__=='__main__':main()
