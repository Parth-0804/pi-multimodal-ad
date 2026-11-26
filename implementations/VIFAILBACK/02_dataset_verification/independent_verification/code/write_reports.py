"""Build human-readable evidence reports; never train or modify raw sources."""
import csv,json
from pathlib import Path
from sources import ROOT,REV,HF
from original_annotations import ORIGINAL_REV


def load(name):return json.loads((ROOT/'checks'/name).read_text())
def rows(name):return list(csv.DictReader((ROOT/'checks'/name).open()))
def write(name,text):
    p=ROOT/name
    with p.open('x') as f:f.write(text.strip()+'\n')
def table(head,values):
    clean=lambda v:str(v).replace('|',' / ').replace('\n',' ')
    return '| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |\n'+'\n'.join('| '+' | '.join(clean(v) for v in row)+' |' for row in values)


if __name__=='__main__':
    labels=load('native_label_summary.json');original=load('original_native_annotation_comparison.json')
    numerical=load('pilot_numerical_audit.json');media=load('pilot_media_audit.json');qc=load('group_and_quality_screen.json')
    provisional=load('provisional_cohort_screen.json');origin=load('constant_state_origin_audit.json');blind=load('post_unblinding_observability.json')
    identities=json.loads((ROOT/'MATCHED_EXAMPLE_GALLERY/UNBLINDING/SOURCE_LABEL_KEY.json').read_text())
    max_error=max(x['video_sensor_selected_timestamp_max_error_s'] for x in numerical)
    source_url=f'https://huggingface.co/datasets/{HF}/tree/{REV}'
    original_url=f'https://huggingface.co/datasets/sii-rhos-ai/ViFailback-Dataset/tree/{ORIGINAL_REV}'
    pairvalues=[]
    for pair in range(1,11):
        members=[x for x in identities if x['pair']==pair];s=next(x for x in members if x['episode_success']=='success');f=next(x for x in members if x['episode_success']=='failure')
        pairvalues.append([pair,s['source_task'],s['blind_id']+' / '+s['episode_index'],f['blind_id']+' / '+f['episode_index'],f['failure_type'],s['num_frames']+' / '+f['num_frames']])
    pairs=table(['Pair','Original task directory','Success blind ID / episode','Failure blind ID / episode','Native failure category','Frames: success / failure'],pairvalues)
    write('README.md',f'''
# ViFailback independent verification

**Decision: CONDITIONAL GO for episode-level visual plus measured robot-observation fusion.** ViFailback is a substantially better match to the requested modality contract than a video/audio dataset. Labels and episode joins pass; full-cohort telemetry QC and a second human visual review remain necessary before a full experiment. No model was trained or CNN features extracted.

Native labels independently counted in **109 original author annotation files** and the conversion: **5,202 episodes, 657 successes, 4,545 failures**, 100 canonical task instructions; all 100 have both outcomes. The 109 source directories include variants of nine canonical tasks. All 5,202 complete nested original annotations agree with the conversion.

The matched pilot contains **10 same-task success/failure pairs**, **20 executions**, **320 distinct temporal positions**, and **960 RGB images** across three cameras. All 60 videos and 20 sensor tables passed the pilot checks. The source identity key is separate from the label-free gallery. Two extra QC episodes are not counted as gallery examples.

## Start with the blinded gallery

Open [MATCHED_EXAMPLE_GALLERY/index.html](MATCHED_EXAMPLE_GALLERY/index.html). Each case provides all three full camera sequences, fixed-region enlargements, an interactive synchronized frame slider, sensor plots, frame indices and episode-relative times. Original identities/outcomes are in the separate `UNBLINDING/` key. Save your own observations before opening that key or reading our observability report. A blank human review form is included.

The initial masked-key analyst screen found clear physical failure evidence in **9/10** native failed examples; one drawing-task case remained uncertain. This is an AI-assisted descriptive screen, not independent human validation, a model score, or an estimate of corpus-wide observability.

## Material limitations

- Six pairs of distinct episode IDs share identical three-camera videos and identical published sensor-statistic signatures. Group/deduplicate derived evaluation units; preserve raw files.
- 173 episodes have completely constant position telemetry in published statistics. Two actual tables/videos confirm positions fixed while arms visibly move; bounded original HDF5 reads show the defect is already in the original recordings.
- Only the two gripper effort channels vary in the pilot; twelve arm-joint effort fields are zero. Two gripper velocity fields are zero. Corpus statistics show the same placeholder pattern. This is not wrist force/torque sensing.
- Converted timestamps agree by frame index; original checked HDF5 files have no per-device hardware timestamps. The sub-microsecond index agreement is not a hardware synchronization guarantee.
- Session/operator/date/object-instance identities are unavailable. Use canonical task groups for held-out-task evaluation; do not claim new-robot/session generalization.

The secondary Zenodo dataset is **NO-GO for supervised binary training under its published split**: training and validation contain only successful trials. Two original test annotations with frame intervals were actually retrieved; the complete archive label counts were not independently recounted.

## Reports

- [NATIVE_LABEL_AUDIT.md](NATIVE_LABEL_AUDIT.md)
- [MODALITY_AND_ALIGNMENT_AUDIT.md](MODALITY_AND_ALIGNMENT_AUDIT.md)
- [GROUP_INDEPENDENCE_AUDIT.md](GROUP_INDEPENDENCE_AUDIT.md)
- [VISUAL_OBSERVABILITY_REVIEW.md](VISUAL_OBSERVABILITY_REVIEW.md)
- [SECONDARY_CANDIDATE_AUDIT.md](SECONDARY_CANDIDATE_AUDIT.md)
- [FINAL_RESEARCH_DECISION.md](FINAL_RESEARCH_DECISION.md)
- [RESEARCHER_HANDOFF.md](RESEARCHER_HANDOFF.md)
- [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json)

Pinned conversion: `{REV}`. Pinned original: `{ORIGINAL_REV}`. Source receipts preserve original URLs, paths, byte ranges, sizes and SHA-256 hashes. Reports and code are new files in this directory; existing project datasets/results and active REASSEMBLE jobs were not changed. Excluded datasets were not investigated. No files were staged or committed.
''')
    tasktable=table(['Task index','Source directories','Success','Failure'],[[x['task_index'],x['source_directories'],x['success'],x['failure']] for x in rows('class_counts_by_task.csv')])
    write('NATIVE_LABEL_AUDIT.md',f'''
# Native outcome and annotation audit

## Pinned sources and actual annotation verification

Official [conversion]({source_url}): **{REV}**. Official [original dataset]({original_url}): **{ORIGINAL_REV}**. Both dataset cards declare MIT licensing. The complete conversion inventory contains 20,815 files and **29,215,133,223 bytes**; 5,202 Parquet files, 15,606 MP4 videos and seven other files. Full payload acquisition was not performed.

Native conversion records: `meta/vifailback_annotations.jsonl` (15,553,675 bytes), `meta/episodes.jsonl` (943,651 bytes), `meta/tasks.jsonl` (12,738 bytes), `meta/info.json` (7,427 bytes). Additionally, **all 109** original `annotated_data/<task>/<task>_annotations.json` files were discovered from pinned directory listings and downloaded. Their exact original paths, sizes, HTTP receipts and SHA-256 identities are retained. The source files contain 5,202 records with no duplicate original video identities. **Every complete nested original annotation object equals the corresponding preserved conversion object**, not merely its label string.

Native `annotation.failure_detection` is literally **`yes` for a failed episode** and **`no` for a successful episode**. The conversion normalizes these to `episode_success = failure/success`. These are direct native fields, not inferred QA answers, folder-name labels, generated labels or LLM-created supervision.

| Native outcome | Original records | Converted records |
|---|---:|---:|
| `failure_detection=yes` / `episode_success=failure` | 4,545 | 4,545 |
| `failure_detection=no` / `episode_success=success` | 657 | 657 |
| Total | 5,202 | 5,202 |

Failure prevalence is **{4545/5202:.6%}**. Prediction units are episodes, not 1,297,146 frames or the 960 exported pilot images. The source annotations are manually authored/assisted according to the paper's annotation workflow; agreement with the release is not independent verification of every physical outcome. The pilot supplies an initial visual plausibility check.

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

{tasktable}

## Duplicates and quality exclusions

No repeated `source_hdf5` identity or exact Parquet-file content hash is present. However, episode/global-index metadata make Parquet hashes insufficient to detect repeated measurements. There are **18 exact video-content duplicate groups**, representing **six duplicate episode pairs**, with identical published sensor-statistic signatures and consistent failed outcomes. These are disclosed in GROUP_INDEPENDENCE_AUDIT.md. No raw files were deleted or relabeled.

A conservative provisional screen quarantining 173 constant-position episodes and retaining one representative per exact duplicate pair leaves **5,023 rows (4,377 failure / 646 success), still with both classes in all 100 canonical tasks**. This is a metadata-based planning count, **not a certified full multimodal cohort**. Raw per-episode QC and a frozen exclusion policy are required before evaluation.
''')
    names=json.loads((ROOT/'source_evidence/vifailback/meta/info.json').read_text())['features']['observation.state']['names'][0]
    channel_table=table(['Index','Channel name','State','Velocity','Effort'],[[i,name,'position observation','zero placeholder' if i in [6,13] else 'velocity observation','gripper effort, units unverified' if i in [6,13] else 'zero placeholder'] for i,name in enumerate(names)])
    source_checks=load('original_hdf5_conversion_audit.json');psnr=[v['PSNR_dB'] for x in source_checks for v in x['image_comparisons']]
    write('MODALITY_AND_ALIGNMENT_AUDIT.md',f'''
# Measured modalities and alignment

## Actual same-episode evidence

The matched pilot downloaded **20 Parquet tables and 60 AV1 MP4 videos**, totaling **127,669,857 bytes**. It contains 5,255 sensor rows and 15,765 camera frames across the three streams. The three cameras are `cam_high`, `cam_left_wrist`, `cam_right_wrist`, each 640×480 RGB at 25 fps. Filenames, episode/task fields and lengths agree for every sampled execution. All sixty clips decoded sixteen requested positions through their last frame without reported decode errors. All **960** selected decoded images are distinct within their own sixteen-frame sequences.

One same-task original success/failure pair (`pick_marker_draw_line`, episodes 2 and 6) was independently downloaded as original HDF5, **110,957,834 bytes total**. Both files declare `sim=False`; the stored puppet-arm arrays `observations/qpos`, `observations/qvel`, `observations/effort` match `observation.state`, `observation.velocity`, `observation.effort` **exactly**, with maximum absolute conversion error zero for all six comparisons. This demonstrates source observation provenance, not solely a README claim.

Original HDF5 images and converted frames were compared at three uniform positions in each camera of both episodes: **18 comparisons**, expected lossy-conversion differences, PSNR **{min(psnr):.2f}–{max(psnr):.2f} dB**. They support camera/episode/index mapping in those samples; they are not a content scan of the full release. Source image decoding follows the author's stored-RGB convention, with no extra channel swap.

## Sensor meaning and channel availability

State is current puppet-arm joint position, velocity is joint telemetry and effort is the native effort feedback field. These are separate from `action`, `action_leader`, target end-effector action and base commands. None of the command fields, labels, keyframe flags, correction text, source IDs or task IDs is admissible as an ordinary sensor input in the proposed primary experiment.

There are 42 stored observation fields (three 14-D arrays), but they are **not 42 informative independent channels**. All 5,202 published statistic records and the 20 actual pilot tables show the following structural zeros: gripper velocity indices 6/13, and twelve non-gripper effort indices. Only the two gripper effort fields vary in the pilot; each pose/state stream has at least seven varying channels per sampled episode and velocity at least twelve. There are **28 non-placeholder fields by this source screen**: 14 positions, 12 arm velocities, 2 gripper effort signals. Some legitimately inactive-arm fields are constant within an execution.

{channel_table}

Physical calibration/units are not included in the inspected HDF5 attributes or conversion feature metadata. Do not label effort as calibrated Nm or contact force, or state that wrist six-axis force/torque is provided. Retain raw units and document the lack of calibration; statistical scaling must be fitted inside training groups. Gripper positions/effort cannot be assumed dimensionally equivalent to arm joint positions/torques. No audio is used or substituted.

## Time-index alignment and its limits

For every pilot table, `frame_index` is exactly 0..N−1; `timestamp` is strictly increasing and agrees with index/25. All actual row/global indices and episode/task associations pass. Selected FFmpeg video presentation times align with the corresponding table times with a maximum absolute difference of **{max_error:.12f} seconds ({max_error*1e6:.3f} microseconds)**. The same sixteen indices and presentation times are used in all three cameras.

This is agreement on the **converted, regular 25 Hz time index**. The checked original HDF5 files have no explicit per-camera capture times, robot hardware timestamp vector or independently calibrated clock offset. Video FPS is assigned on conversion. Camera-to-robot hardware latency and capture jitter therefore remain **unquantified**, not bounded by 0.92 microseconds or proven below one frame (40 ms). The source arrays and camera lengths provide strong episode/index pairing evidence, sufficient to consider retrospective action classification; precise failure-onset prediction/closed-loop anticipation needs additional timing evidence. No offset was estimated from labels or anomaly correspondence.

## Defects and unresolved samples

The complete listing contains no missing episode modality paths. The sampled good cohort has no missing/nonfinite observed values, no ordering mismatch, no repeated selected decoded image, and no flagged decoder error. This does not establish every full-data payload is intact or free of within-video repetition.

**Constant position telemetry:** published records flag 173 episodes (162 failure, 11 success) with all fourteen positions fixed. Actual tables for episodes **1294** and **3325** confirm this. Their high-camera videos show clear robot arm/object motion while positions remain constant; velocity and gripper effort still vary. Bounded reads of the original HDF5 observation arrays reproduce exactly the converted arrays in both cases. The issue is therefore present upstream, not introduced by this conversion. Original source paths are `raw_data/pick_coke_bottle_place_plate_ep1/episode_24.hdf5` and `raw_data/pick_plate_from_drawer_put_pink_cube_ep1/episode_72.hdf5`.

These two are confirmed unreliable position records. Quarantine all 173 flagged cases until reviewed; do not automatically claim all 173 are defective, since genuinely stationary executions require separate judgment. Do not integrate velocities to invent replacement ground-truth positions. The two QC cases are additional to the 20 matched examples. Evidence: `checks/constant_state_actual_sample_audit.json`, `constant_state_origin_audit.json`, `constant_state_QC_1294.jpg`, `constant_state_QC_3325.jpg`.

This combination of strong valid pilot pairing and explicit upstream defects supports a **conditional**, quality-controlled cohort rather than unconditional use of all 5,202 episodes.
''')
    dup_table=table(['Shared-video episode IDs','Canonical-source relationship'],[[', '.join(map(str,c)),'same original task; same failed outcome; all three cameras identical'] for c in qc['duplicate_episode_components']])
    write('GROUP_INDEPENDENCE_AUDIT.md',f'''
# Group independence and leakage screening

## What is genuinely identified

5,202 native source episodes are uniquely indexed; each has one original HDF5 path and three converted views. All views, frames, crops, statistics and any future windows of one source episode must remain together. There are **100 canonical task groups**, not 109 independent tasks; all 100 have successes and failures. The canonical task mapping combines nine source-directory variants, including the `_ep1`/`_ep2` variants. Directory suffixes are not verified session IDs.

No original operator, collection-date, robot-serial, recording-session, scene-instance or object-instance identity field was found in the annotation/episode metadata. The checked original HDF5 attributes contain no such identifiers. Publication/repository timestamps must not be used as collection dates. The platform/setup and objects are shared across tasks, and demonstrations may be intentionally perturbed or collected in batches. Distinct filenames are not proof of statistically independent executions.

The [original paper, v3](https://arxiv.org/html/2512.02787v3) describes its own ALOHA collection: 4,995 teleoperated trajectories and 207 policy rollouts. These are author-reported collection totals; no reliable per-episode teleoperation/policy tag was found in the audited metadata. ViFailback's independent publication and original trajectory provenance support an external-dataset study, but an exhaustive cross-dataset near-duplicate comparison against REASSEMBLE was not performed. Do not claim independent operators, robots, or collection regimes from the source identity alone, or infer a policy/session from an `_ep2` suffix.

## Exact duplicate components

All 5,202 Parquet file hashes are different, partly because episode/global-index fields differ. The video inventory has 18 byte-identical pairs: the same six episode pairs repeat independently across all three views. The six complete published sensor-statistic signatures also repeat for these pairs. No conflicting native outcome was found in these components.

{dup_table}

Preserve all raw files. For a prospective evaluation, either retain a deterministic representative per fully verified duplicate component or give the entire component one group and explicitly avoid double-weighting duplicates in reported performance. Native counts remain 5,202. A file hash on the Parquet alone is not a sufficient leakage guard.

The provisional exclusion of the higher-index copy from each pair and quarantine of 173 constant-position episodes removes **179** rows, with no overlap between these two flags. It leaves **5,023** metadata candidates, **4,377 failed / 646 successful**, and both outcomes in **all 100 task groups**. These are planning counts pending complete raw-data QC; no model-ready full cohort is certified.

## Defensible prospective splits

The conversion supplies only `train: 0:5202`; it has no author-provided independent supervised train/validation/test partition. Do not treat the directory named train as a held-out protocol or select split settings from outer-test performance.

Primary proposal: freeze the eligible cohort and group map before model work, then use **five outer task-disjoint folds**, with **four inner task-disjoint folds** restricted to each outer-training partition. Canonical task IDs serve as grouping metadata only, not ordinary predictors. All directory variants, episode views and duplicate components stay together. Verify class support and every train/validation/test intersection by assertion. All outer-test outcomes remain assessment-only; any architecture/hyperparameter/calibration/threshold/fusion choice uses inner data.

Because every canonical task has both outcomes before and after the provisional screen, class support across reasonable multi-task folds is feasible. Exact fold assignments and cohort exclusions are **not frozen in this feasibility stage**. Low success counts in some tasks make within-task repeated nested folds fragile; avoid treating three camera views or sixteen frames as independent class support.

A secondary episode-disjoint, within-task analysis can estimate new-execution performance under similar tasks, but cannot establish new-task/session independence. A stronger object/scene-family split needs an independently curated, verified group map; natural-language task names are insufficient proof of object-instance identity. Neither design supports new-robot robustness or unrestricted cross-domain generalization on its own.

Use paired task-cluster uncertainty for model differences and report all seeds/folds. Do not count overlapping folds, seeds, video views or frames as independent replicates. This audit checked duplicate source identities and exact inventory hashes, not all near-duplicate trajectories or hidden session dependencies.
''')
    observed=table(['Blind ID','Native outcome after unblinding','Native category','Initial physical failure evidence','Observation'],[[x['blind_id'],x['native_outcome'],x['native_failure_type'],x['physical_failure_evidence'],x['notes']] for x in blind['rows']])
    write('VISUAL_OBSERVABILITY_REVIEW.md',f'''
# Real visual observability review

**Open the label-free gallery before reading this report or the source key.** The gallery is [MATCHED_EXAMPLE_GALLERY/index.html](MATCHED_EXAMPLE_GALLERY/index.html).

## Sampling and review procedure

Ten task-matched success/failure pairs were selected from native records to cover gripper pose, gripper state, task planning and an external-intervention control. Within each chosen original task directory, select the success/failure combination with the closest frame length; tie by original converted episode index. Task/object matching is a design constraint, not proof that poses, distractors, lighting or conditions are identical.

Per-execution frame policy: **floor(k×(N−1)/15), k=0..15**. Both outcomes use the same sixteen chronological positions from first to last. All three cameras use those same indices. No avoid/correct keyframe, failure type, frame-label mask, sensor anomaly or outer-test result determines frame positions, crop, or time offset. There are **320 timepoints / 960 camera images**, not 960 independent prediction examples. Each source image can be opened at original 640×480 resolution.

The enlarged-region view is a fixed center crop (x/y 20–80%) for every camera/class. It is supplementary and can omit an off-center object; full views remain authoritative. There are twenty corresponding sensor plots, with uniform sampled times marked and no outcome/keyframe marks in the blinded pages.

Per-case identities/outcomes were masked with a seeded random permutation. Initial analyst observations were recorded and SHA-256 locked before opening the per-case native key. All 20 three-camera overviews and task instructions were examined; ambiguous cases B09, B11, B18 and B02 additionally received full-size **already selected** sequences. No new favorable frames were selected. The record is `MATCHED_EXAMPLE_GALLERY/INITIAL_BLINDED_SCREEN.json`; its lock hash is `{blind['blind_screen_sha256']}`.

This is an **AI-assisted initial analyst screen**, not an independent human experiment or inter-rater validation. The analyst knew the selection was balanced; per-case outcome mapping remained masked until judgments were saved. The researcher and second reviewer should complete the blank review form independently before seeing the key or these notes.

## What was observed

After unblinding, **9 of the 10 native failures** had clear physical failure evidence in the fixed frames. The remaining native failure, **B02**, has visible marker pickup/return but the required drawing stroke is ambiguous at these sixteen positions. This is a descriptive observability count, not classifier accuracy, recall, an exhaustive failure taxonomy or a corpus-wide rate.

Examples include apparent failed grasps (B08/B09/B15/B18), cube outside its intended basket after transfer (B06), wrong-target placement (B19), unsuccessful/incorrect contact or object interaction (B03/B07), and visible external human interference (B20). Fine alignment/contact success can still be partially obscured. Sparse frames do not establish failure-onset time or prove that a short drop event occurred between sampled positions. Native category labels remain unchanged even when our observed physical description is different in granularity.

{observed}

## Pair identities, conditions and limits

The table below is **unblinded**. Original full paths, videos, source frame indices and timestamps are retained in the separate key and audit manifests.

{pairs}

The target objects are comparable within each task, but initial object positions, workspace arrangements, distractors, duration and arm poses visibly differ across some pairs. In particular, different drawer/pot/plate placements and extra distractor cubes prevent claiming exact condition matching. Source directory names can be imperfect descriptions: the `grasp_cube_place_shelf` samples' native task instruction and images concern a test tube/rack. Use the original instruction and source identity rather than deriving semantics from that directory name.

The high camera usually exposes task progress and outcome context; wrist cameras can reveal grasp/connector contact but often face away or become occluded. All three perspectives are provided; none is declared universally informative. The human-intervention example contains an obvious person and should be analyzed separately from endogenous manipulation failure. B02 is retained as uncertain, not relabeled or swapped for a clearer positive.

Recommendation: obtain independent human ratings of failure visibility, object/gripper visibility and context matching. Freeze any observability-based subset transparently, retain exclusions and acknowledge spectrum/selection bias; do not use pilot visibility judgments to cherry-pick model test examples. The pilot selection is intentionally balanced and covers chosen tasks, unlike the full 87.37% failure-prevalence release.
''')
    secondary=load('secondary_bounded_native_audit.json')
    nativeexamples=table(['Original archive member','Native Outcomes','Native Anomalies'],[[x['name'],json.loads(x['text']).get('Outcomes'),json.loads(x['text']).get('Anomalies')] for x in secondary['metadata_members']])
    write('SECONDARY_CANDIDATE_AUDIT.md',f'''
# Secondary candidate: Zenodo 4578539

**NO-GO for the intended supervised binary comparison using the published partition.** This is not a blanket claim that the dataset cannot support other designs.

Official source: [A robot dataset of successful and failed placement executions](https://zenodo.org/records/4578539), DOI **10.5281/zenodo.4578539**, published version **v1**, CC BY 4.0 per the downloaded Zenodo metadata. The Toyota HSR places a book on a shelf; recorded modalities include RGB/depth, rendered robot images, force/torque and joint telemetry according to the publisher. No audio substitution is proposed.

## Published partition, not an independently recounted corpus

| Published split | Successful trials | Anomalous trials |
|---|---:|---:|
| Training | 48 | 0 |
| Validation | 6 | 0 |
| Test | 7 | 60 |
| Total | 61 | 60 |

The archive sizes from the record API are **3,387,726,028** training bytes, **365,983,836** validation bytes and **4,384,127,358** test bytes. Author MD5 values and URLs are preserved in `source_evidence/zenodo_api.json`. No full archive was downloaded; a full-archive SHA-256/MD5 was not computed. The numbers above are **author-reported trial counts**, not verified from every source member.

## Actual native annotations retrieved

Gzip has no random-access central directory. Bounded HTTP prefixes were preserved, totaling 256 MiB of the test stream plus smaller initial test/validation prefixes; the logical inspected test prefix contains 5,067 tar members. Expected premature end-of-stream reflects bounded acquisition, not an asserted corrupt archive. Two actual original `annotation.json` members were decoded and individually SHA-256 recorded:

{nativeexamples}

The native schema has a list of textual outcome/event descriptions and `Anomalies` frame-index intervals. Author source code, pinned at **204d91e1ea0f7012e27400fb0842e44debc035f2**, maps inclusive intervals onto the ordered RGB frames and marks anomaly frames 1. These are **frame-level anomaly/event labels**, not a native yes/no episode-success field. External collision or camera occlusion can be anomalous without being identical to final task failure. Do not silently collapse those concepts.

The two positive native examples support the existence/schema of annotations, not a complete positive/negative recount or a validated sensor/video cohort. No full numerical schema, synchronization, payload integrity or negative-label audit was completed for this secondary candidate; it was deprioritized after the published partition failed the intended supervised training contract.

## Why the original split does not support supervised binary training

Training and validation contain no anomalous trials under the published split. A binary discriminative visual/sensor classifier and learned probability fusion cannot be trained/selected on both classes using those partitions. Training on frames/labels from the published test set would compromise that benchmark. A nominal-only anomaly detector is a different experiment; a new trial-disjoint supervised partition would require explicit redesign, complete native label/sensor verification and preservation of the original split identity. Neither was performed here.

Actual source records, partial-stream limitations, original member filenames and hashes are in `checks/secondary_bounded_native_audit.json`; member inventory in `checks/secondary_256MiB_member_listing.json`; source code in `source_evidence/secondary_code.zip`. No file contents were inferred from directory names or supplied by an LLM.
''')
    write('FINAL_RESEARCH_DECISION.md',f'''
# Final research decision

**CONDITIONAL GO: ViFailback supports an episode-level REASSEMBLE-style visual/proprioceptive fusion study, subject to a frozen quality-controlled cohort and independent human review.** It does not establish hardware-accurate failure-onset localization or an unconditional model-ready 5,202-example cohort. The secondary candidate is NO-GO for supervised binary training under its published normal-only training/validation split.

## Answers supported by actual evidence

1. **Native outcomes:** 657 success and 4,545 failure labels agree exactly across all 109 original annotation files and the conversion. Labels are episode outcomes; sparse reference keyframes do not define a temporal failure mask.
2. **Paired modalities:** actual 20-episode tables and 60 videos pass same-ID/length/index checks. Both downloaded original HDF5 episodes exactly reproduce all three observation arrays, and 18 original-image comparisons support camera/index correspondence after lossy encoding.
3. **Visible failures:** nine of ten native failed pilot cases show clear physical evidence in the fixed samples; one drawing case is uncertain. This is a masked-key AI-assisted screen requiring an independent human review, not a measured model benefit.
4. **Independent groups:** 100 canonical task groups all contain both classes; task-disjoint nested evaluation is feasible. Session/operator/object-instance independence remains unverified. Six duplicate episode pairs must be grouped or represented once.
5. **Within-task class overlap:** all 100 task instructions have both outcomes; 104/109 source directories do. Nine task variants must remain combined.
6. **Architecture adaptation:** reuse the verified CNN feature extractor/loading/model interfaces; fit new dataset-specific visual and sensor heads and new fusion parameters. No current training, source-head reuse, weight-transfer claim or inherited F2 coefficients is justified by this audit.
7. **Fair comparisons:** paired fixed cohorts, frame/camera policy, grouped folds, initialization rules, budgets, inner selection and seeds are required; no result is predicted in advance.

## Cohort and input contract to freeze next

Prediction unit: one whole original execution; target failure=1, success=0 from the native field. Preserve all three camera perspectives for review. A prospective shared-CNN three-view variant takes **B×3 cameras×16 timestamps×3 RGB channels×H×W**, pools the sixteen frame features per view and then averages view features before a new visual head. This is 48 source images per episode, not 48 labels. Alternatively, retain the original sixteen-image architecture using a fixed primary camera and make three-view pooling a separately declared ablation; select the camera rule from training-side/pilot evidence before outer-test results exist.

Numerical input is the same episode's observed time series. There are 42 stored fields with 14 structural-zero placeholders; a source-informed candidate mask retains 14 positions, 12 joint velocities and 2 gripper effort values. Physical units are not validated. Use configurable channel identities/statistical extraction, not REASSEMBLE's channel count. Fit scaling, imputation and any learned feature selection within training partitions only. Do not use commands, `episode_index`, global/source IDs, task IDs, failure flags, avoid/correct markers, annotation text or final outcomes as ordinary predictors. Duration/frame counts can be powerful completion shortcuts; exclude them as ordinary features in the primary specification or declare a matched ablation, and do not disguise them as quality features.

Raw source count is 5,202. The validated matched input pilot is **20** executions. The conservative metadata QC proposal is **5,023** candidates (4,377 failure, 646 success) after 173 constant-position flags and six duplicate copies; this candidate cohort is not fully payload-validated. The two actual QC defects are upstream. Preserve all exclusions and decide before model work whether to quarantine all flags, repair only with original valid evidence, or study missing-state masks separately. Do not invent repaired sensor values.

External human intervention and high-level task-planning errors need explicit strata. A predeclared pose/state-only physical-failure analysis is plausible but changes the target population and prevalence. Do not silently omit difficult or nonvisible positives; report all strata and observability exclusions.

## Fair visual/sensor/fusion comparisons

| Model | Fair prospective definition |
|---|---|
| Visual only | Same fixed 16-timepoint/camera policy, verified extractor and newly trained ViFailback head; same initialization/freezing/fine-tuning rule across paired comparisons |
| Sensor only | Same execution cohort, measured observation statistics, newly fitted classifier and training-only scaling/selection |
| Averaging | Nonlearned 0.5×p_visual + 0.5×p_sensor, with the same branch calibration policy |
| F2 static fusion | Reuse the project's two-probability L2 logistic stacking definition (C=1 reference): sigmoid(b + w_v p_v + w_s p_s); refit three parameters on leakage-safe grouped OOF probabilities only |
| Quality-aware fusion | A small declared gate using target-free availability/quality indicators, the same branch predictions and training groups; no failure keyframes, labels, task ID, or test-adaptive optimization |

Existing `src/reassemble/section2_report.py` and `section2_models.py` establish the static/quality-gate interfaces read-only; nothing there was edited or executed for training. For any F2/gate selection, the probability for a training episode must come from a branch whose training, tuning and calibration exclude that episode's entire group. Hyperparameter selection for stacking/gating needs the additional nested training-only level; outer-test labels cannot fit branches, calibration, thresholds, stackers or quality weights. Refit F2 separately for each visual initialization/seed condition; never reuse REASSEMBLE coefficients.

Use identical outer task folds and inner task folds for every model, deterministic seeds such as 42/123/20261023, and a predeclared common budget/selection rule; exact assignments and budgets remain for the next reviewed protocol. Report all folds/seeds with paired task-cluster intervals. Primary failure AP must be accompanied by failure prevalence (**87.370% native**) and a constant-score baseline; also report AUROC, success-class AP, balanced accuracy, classwise recall, Brier and calibration estimates with support/limitations. Do not choose only the best seed or fold, or treat seeds as independent datasets.

Quality-awareness does not imply robustness. Corrupted/missing-modality claims require a separately authorized held-out perturbation protocol; none was run here. Strong sensors, visible failures or a flexible gate do not guarantee improved fusion.

## Full-study resource implications and stop condition

The complete converted release is **29.215 GB decimal (~27.21 GiB)**. It spans 14.41 execution-hours, with three camera streams. Full native-resolution decoded pixels would require about **230.1 GB** for three views and sixteen images/episode even as uint8; do not materialize such a cache on this workspace. Resized 224×224 uint8 three-view samples would be about **37.6 GB**, excluding video originals, models and metadata; stream/decode bounded batches instead. Compact pooled-feature/statistic caches are much smaller, but exact dimensions/cache budgets belong to implementation planning.

Only the selected source evidence and pilot were acquired. No original full HDF5 collection, full Zenodo archive, CNN extraction, GPU benchmark or model training was run. Training-time/GPU-hour estimates would be unsupported without an authorized benchmark. Full acquisition can fit only with an explicit reserve/cache/checkpoint plan and a fresh storage check, preserving at least 20 GiB; ongoing REASSEMBLE work has priority.

Stop now for independent research review of labels, QC policy, visual observations, grouping, actual measured channels and the proposed target. No full acquisition or experiment matrix starts automatically.
''')
    write('RESEARCHER_HANDOFF.md',f'''
# Researcher handoff — independent review

**Decision to review: CONDITIONAL GO for ViFailback whole-execution visual + measured robot-observation fusion.** No audio substitution. Excluded datasets were not accessed for this investigation. The secondary Zenodo release does not support supervised binary training under its published partition.

Before reading the native key or our observations, open [the blinded gallery](MATCHED_EXAMPLE_GALLERY/index.html) and complete `MATCHED_EXAMPLE_GALLERY/HUMAN_REVIEW_FORM.csv`. It contains twenty deidentified executions, all three cameras, sixteen uniform positions per camera, full views, fixed-region enlargements, timestamps and sensor plots. Then inspect `UNBLINDING/index.html` for original episode identities and native labels. The AI-assisted masked-key screen found clear physical evidence in 9/10 failed cases; B02 remains uncertain. This is not human validation or model evidence.

## What was independently checked

- All 5,202 native annotation records: original yes/no counts 4,545/657, complete nested object equality, unique joins, listed modalities, task mapping and valid normalized keyframes.
- All 100 canonical tasks have both outcomes; 109 source directory variants mapped explicitly.
- Actual 20-episode/60-video pilot: 5,255 measured rows, finite observation arrays, exact IDs/indices/flag joins and 960 distinct selected images; converted selected timestamp disagreement below 0.92 microseconds.
- Two original HDF5 files: exact qpos/qvel/effort matches; eighteen original/converted camera-frame comparisons. The absence of original hardware timestamps was explicitly checked in those files.
- Six exact duplicate episode components through video hashes and matching sensor-statistic fingerprints; repeated identities must remain grouped.
- Two extra QC tables/videos: frozen positions despite moving robot; bounded original HDF5 reads confirm the upstream defect. 173 cases flagged by published stats require quarantine/review, not invented repairs.
- Secondary: two actual test annotation records with textual Outcomes and frame-index Anomalies; published normal-only training/validation split inspected. Full secondary class recount and modality audit were not performed.

## Decisions still required before implementation

1. Confirm episode-level outcome as the target; sparse avoid/correct frames are not temporal ground truth.
2. Review twenty cases independently for visible failure, uncertain tasks and object/condition matching. Preserve B02 and all exclusions in the audit trail.
3. Freeze telemetry QC: quarantine 173 flags, deterministic duplicate treatment, structural-zero mask and any further full-input integrity checks. The proposed remaining 5,023 examples are not certified valid payloads.
4. Confirm that 14 positions, 12 velocities and 2 gripper effort observations meet the scientific goal; calibrated joint torque/wrist F/T is not available here.
5. Freeze canonical-task grouping, nested folds, camera policy, preprocessing, classifier/fusion selection rules, budgets, seeds, uncertainty estimates and intervention/planning strata before any outer-test evaluation.
6. Keep frame/crop selection label-blind and identical across both outcomes and all model comparisons. No annotation-guided positive-only improvement.
7. Independently acknowledge unquantified camera/robot hardware latency and missing session/operator/object-instance IDs. Do not call converted index agreement a hardware timing calibration.

## Artifact map and provenance

Reports: README.md, NATIVE_LABEL_AUDIT.md, MODALITY_AND_ALIGNMENT_AUDIT.md, GROUP_INDEPENDENCE_AUDIT.md, VISUAL_OBSERVABILITY_REVIEW.md, SECONDARY_CANDIDATE_AUDIT.md, FINAL_RESEARCH_DECISION.md and this handoff.

Source revisions: conversion `{REV}`, original `{ORIGINAL_REV}`, secondary Zenodo DOI 10.5281/zenodo.4578539 v1. Individual source URLs, original filenames, byte-range responses, publisher identities, sizes and SHA-256 hashes are in SOURCE_PROVENANCE.json and source receipts. Archive-prefix samples are partial, not complete-archive integrity verification. Actual sample exclusions and all 100-task counts are in `checks/`; gallery/native label key is separate from the label-free pages.

Core source checks can be recomputed from preserved inputs using the code in `code/`: `audit_labels.py`, `screen_groups_and_quality.py`, `verify_original_samples.py`, `inspect_secondary.py`, and `validate_delivery.py`. Acquisition scripts are bounded and reuse verified existing files; no source payload should be overwritten. The frozen initial blind screen is intentionally not rerun or rewritten. A fresh whole-dataset acquisition reproduction was not attempted.

All work is new under this folder. Existing raw data, historical reports, trained weights and active REASSEMBLE processes were not modified. No models were trained, no CNN embeddings extracted and no GPU tests run. No files were staged/committed. Stop for the requested four-eye review before full data acquisition or training.
''')
    with (ROOT/'MATCHED_EXAMPLE_GALLERY/HUMAN_REVIEW_FORM.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['blind_id','object_visibility','gripper_visibility','interaction_visibility','physical_failure_evidence','apparent_task_completion','confidence','notes'])
        writer.writeheader();writer.writerows({'blind_id':f'B{i:02d}'} for i in range(1,21))
    print('Eight reports and blank human review form written; provenance and final checks next.')
