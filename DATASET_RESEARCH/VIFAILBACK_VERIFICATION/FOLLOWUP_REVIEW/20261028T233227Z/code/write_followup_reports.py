"""Consolidate measured audit results into a reviewable, unexecuted protocol."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv
import json

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent
REPO = SOURCE.parents[1]
V2 = '02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/'


def load(relative):
    return json.loads((RUN / relative).read_text())


def text(relative, content):
    with (RUN / relative).open('x') as stream:
        stream.write(content.strip() + '\n')


def md_table(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n|' + '|'.join(' --- ' for _ in headers) + '|\n' + ''.join('| ' + ' | '.join(str(v).replace('|', '/') for v in row) + ' |\n' for row in rows)


if __name__ == '__main__':
    now = datetime.now(ZoneInfo('Europe/Berlin')).isoformat()
    core = load(V2 + 'CORE_SUMMARY_V2.json')
    sensor = load('03_SENSOR_QUALITY/FULL_SENSOR_AND_COHORT_AUDIT.json')
    reference = load('04_REASSEMBLE_REFERENCE/REFERENCE_AUDIT.json')
    unblind = load('01_UNBLINDING/UNBLINDING_VERIFICATION.json')
    lock = load('00_LOCKED_REVIEW/REVIEW_LOCK.json')
    original_checks = load('03_SENSOR_QUALITY/ADDITIONAL_ORIGINAL_SENSOR_CHECKS.json')
    live = load('04_REASSEMBLE_REFERENCE/ACTIVE_STUDY_STATUS_SNAPSHOT.json')
    comparison = list(csv.DictReader((RUN / '01_UNBLINDING/LOCKED_PREDICTIONS_VS_NATIVE_LABELS.csv').open()))
    checkpoint = next(row for row in reference['completed_100epoch_checkpoint_audits'] if row['valid_full_backbone_transfer_source'])
    counts = core['core_counts']
    prevalence = counts['failure'] / core['core_episodes']
    high = core['required_rgb']['primary_high']
    all_rgb = core['required_rgb']['all_three_cameras']
    t_presentations = core['training_T_presentations_one_epoch_all25fits'] * 50 * 3
    extrapolated_hours = t_presentations / 2.032 / 3600

    proposal = {
        'protocol': 'VIFAILBACK-REASSEMBLE-PORTABILITY-PROPOSAL-v1', 'status': 'DRAFT_FOR_RESEARCHER_REVIEW_NO_TRAINING_AUTHORIZED',
        'dataset_revision': '619791b94f61667333fe179d471051e0bca0e06f',
        'original_revision': '21df46c2585c52e5a62df5f4b946bae6cbc6fed7',
        'cohort_manifest': str((RUN / (V2 + 'ELIGIBLE_CORE_EPISODES_V2.csv')).relative_to(REPO)),
        'cohort_version': core['version'], 'cohort_size': core['core_episodes'],
        'cohort_requires_full_visual_qc': True, 'unit': 'one original episode',
        'target': {'positive': 'original annotation.failure_detection == yes', 'negative': 'original annotation.failure_detection == no',
                   'conversion_field': 'episode_success is derived from failure_detection; not separately validated mechanical final success'},
        'seeds': [42, 123, 20261023], 'split_seed': 20261029,
        'split_manifest': str((RUN / (V2 + 'OUTER_INNER_SPLITS_V2.json')).relative_to(REPO)),
        'base_fit_manifest': str((RUN / (V2 + 'BASE_FIT_T_V_C_ASSESSMENT_V2.json')).relative_to(REPO)),
        'grouping': 'canonical task and exact duplicate components; no session/operator/robot independence claimed',
        'visual': {'backbone': 'PekingU/rtdetr_r18vd: model.backbone.model only',
                   'pretrained_revision': 'ac77a11ff0170a41b771c03264987f8ce2b0d753',
                   'weight_directory': reference['original_weights_directory'],
                   'primary_camera': 'cam_high', 'frames': 16, 'frame_rule': 'round(linspace(0,N-1,16)); assert unique and ordered; no annotation-keyframe access',
                   'input': '[B,16,3,640,640] float32, bilinear resize and /255, do_normalize=false',
                   'pooling': 'spatial mean of stage2,stage3,stage4 maps; concatenate128+256+512; temporal arithmetic mean',
                   'feature_width': 896, 'head': 'Linear(896,128),ReLU,Dropout(0.1),Linear(128,1)',
                   'backbone_rules': ['frozen', 'all_CNN_convolution_and_normalization_affine_trainable_running_moments_fixed'],
                   'epoch_budgets': [25, 50], 'schedule_horizon': 50,
                   'budget_sharing': 'A single50-epoch trajectory per rule/seed/fit can preserve independently selected <=25 and <=50 checkpoints; shared cosine50 prefix explicitly reported',
                   'selection': 'highest V AP within budget; tie lower weighted V BCE then earliest epoch',
                   'normalizer': 'fixed initial-backbone target T feature mean/std only; no source-domain feature moments transferred',
                   'head_lr': 0.001, 'backbone_lr': 1e-5, 'weight_decay': 0.001, 'gradient_clip': 1,
                   'precision': 'float32 reference until numerical parity is demonstrated', 'microbatch': 1, 'accumulation': 8,
                   'augmentation': 'none in portability reference', 'loss': 'BCEWithLogits pos_weight=N_negative/N_positive fitted on T'},
        'sensors': {'streams': {'observation.state': list(range(14)), 'observation.velocity': [0,1,2,3,4,5,7,8,9,10,11,12], 'observation.effort': [6,13]},
                    'measurement_semantics': 'native observed position/velocity and two gripper-effort fields; not force/torque',
                    'statistics': ['mean','std','median','min','max','q25','q75','range','RMS','slope_over_normalized_episode_progress'],
                    'feature_width': 280, 'interval': 'complete same original episode; no frame-level labels inferred',
                    'logistic': {'C_candidates': [0.1,1,10], 'class_weight': 'balanced', 'max_iter': 2000, 'selection': 'V AP'},
                    'nonlinear': {'class': 'HistGradientBoostingClassifier', 'max_leaf_nodes_candidates': [7,15,31], 'max_iter': 200,
                                  'learning_rate': 0.05, 'l2_regularization': 0.1, 'min_samples_leaf': 20,
                                  'early_stopping': False, 'sample_weight': 'inverse class frequency on T', 'selection': 'V AP'},
                    'normalization': 'T only; preserve feature behavior in reassemble.section1_features.statistics',
                    'calibration': 'unweighted sigmoid LogisticRegression C1 on C raw scores; same procedure for visual/sensor'},
        'fusion': {'averaging': '(p_visual+p_sensor)/2',
                   'F2': 'unweighted LogisticRegression C1 on two calibrated inner-OOF probabilities; newly fit per visual/sensor condition/seed/outer fold',
                   'quality_gate': 'reuse DecisionGate F5 quality-only context; hidden16,ReLU,two outputs,masked softmax; convex mixture of clipped branch logits',
                   'gate_training': 'fixed40 epochs,AdamW lr0.003 weight_decay0.001; unweighted BCE; no test-selected settings',
                   'quality_inputs': ['sampled RGB blur/brightness/contrast and decode coverage','sensor finite/constant/saturation/derivative-consistency summaries','availability masks'],
                   'forbidden_context': ['native outcome','failure category','human-intervention annotation','task/source ID','task instruction','annotation keyframes','collection metadata inferred from filenames'],
                   'threshold': 0.5, 'meta_selection': 'F2/gate fixed a priori; changing hyperparameters requires deeper nested, group-safe branch regeneration'},
        'metrics': {'primary': 'Average Precision for native failure',
                    'secondary': ['AP_success','macro_AP','macro_task_AP','AUROC','balanced_accuracy','MCC','macro_F1','per_class_precision_recall','Brier','log_loss','10_fixed_bin_ECE'],
                    'report': 'all outer folds and seeds plus pooled OOF; paired deltas and prevalence; no best-fold/seed selection',
                    'uncertainty': '2000 paired canonical-task-cluster bootstrap replicates of mean per-seed metric differences; seeds/folds not independent replicates'},
        'optional_source_transfer': {'status': 'controlled extension, not performed', 'source_checkpoint': checkpoint['path'],
                                     'source_sha256': checkpoint['sha256'], 'selected_source_epoch': checkpoint['selected_epoch'],
                                     'source_selection': 'Fixed existing REASSEMBLE validation selection; never choose using ViFailback outer tests',
                                     'load': 'compatible backbone tensors only; discard head, feature moments, calibrators, F2 and gate weights',
                                     'comparison': 'P/R share cohort, T/V/C/assessment, target heads, budget/freezing rule, seeds, metrics; same source checkpoint across target seeds'},
        'optional_camera_extension': 'All three cameras at the same16 positions =48 images, explicitly separate from primary16-image contract; same primary cohort and no test-driven camera selection',
        'training_performed': False,
    }
    with (RUN / 'config/EXPERIMENT_PROPOSAL.json').open('x') as stream:
        json.dump(proposal, stream, indent=2)
    matrix = []
    for sensor_name in ['sensor_logistic','sensor_HGB']:
        matrix.append({'stage':'core','system':sensor_name,'visual_initialization':'none','backbone_rule':'none','epochs':200 if sensor_name.endswith('HGB') else 'solver_convergence','sensor':sensor_name,'fusion':'none'})
    for initialization in ['P_original','R_REASSEMBLE_optional']:
        for rule in ['frozen','full_CNN']:
            for budget in [25,50]:
                vid=f'{initialization}_{rule}_{budget}'
                stage='core' if initialization.startswith('P_') else 'optional_transfer_extension'
                matrix.append({'stage':stage,'system':vid,'visual_initialization':initialization,'backbone_rule':rule,'epochs':budget,'sensor':'none','fusion':'none'})
                for sensor_name in ['sensor_logistic','sensor_HGB']:
                    for fusion in ['probability_average','F2_static','F5_quality_gate']:
                        matrix.append({'stage':stage,'system':vid+'_'+sensor_name+'_'+fusion,'visual_initialization':initialization,'backbone_rule':rule,'epochs':budget,'sensor':sensor_name,'fusion':fusion})
    with (RUN / '05_EXPERIMENT_PROPOSAL/EXPERIMENT_MATRIX.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(matrix[0]));writer.writeheader();writer.writerows(matrix)

    text('README.md', f'''# ViFailback follow-up verification and experiment proposal

Recorded {now} (Europe/Berlin). No model training or neural inference was performed.

Read [EXECUTIVE_VERDICT.md](EXECUTIVE_VERDICT.md) first. This is a new versioned
analysis; previous evidence, review predictions, exports and training runs remain
unchanged. Recommendations inside the supplied review were treated as review
content, not as authorization to execute experiments.

- [Locked review](00_LOCKED_REVIEW/INDEPENDENT_REVIEW_LOCKED.md) and [lock](00_LOCKED_REVIEW/REVIEW_LOCK.json).
- [Unblinding report](01_UNBLINDING/UNBLINDING_REPORT.md) and [all20 comparisons](01_UNBLINDING/LOCKED_PREDICTIONS_VS_NATIVE_LABELS.csv).
- [Cohort, grouping and availability](02_COHORT_AND_SPLITS/COHORT_READINESS_AND_GROUPING.md).
- [Conservative V2 episode list](02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/ELIGIBLE_CORE_EPISODES_V2.csv), [all exclusions](02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/CORE_ELIGIBILITY_AND_EXCLUSIONS_V2.csv), and [splits](02_COHORT_AND_SPLITS/V2_CONSERVATIVE_CORE/OUTER_INNER_SPLITS_V2.json).
- [Sensor quality](03_SENSOR_QUALITY/SENSOR_QUALITY_AUDIT.md) and [diagnostics](03_SENSOR_QUALITY/SENSOR_ANOMALY_DIAGNOSTICS.png).
- [REASSEMBLE implementation and checkpoint audit](04_REASSEMBLE_REFERENCE/REASSEMBLE_IMPLEMENTATION_AND_CHECKPOINT_AUDIT.md).
- [Reproducible experiment proposal](05_EXPERIMENT_PROPOSAL/REPRODUCIBLE_EXPERIMENT_PROPOSAL.md), [matrix](05_EXPERIMENT_PROPOSAL/EXPERIMENT_MATRIX.csv), and [configuration](config/EXPERIMENT_PROPOSAL.json).
- [Remaining blockers](UNRESOLVED_BLOCKERS.md). Generated validation/provenance records are under `provenance/`.

All episode lists retain original identities. V1 planning artifacts remain under
`02_COHORT_AND_SPLITS/`; proposed primary analyses refer specifically to the V2
subdirectory. A CSV saying eligible for acquisition is not proof that every
remote RGB payload has been decoded or checked for incidental human involvement.
''')

    text('EXECUTIVE_VERDICT.md', f'''# Executive verdict — ViFailback independent verification

**Scientific feasibility: GO for supervised RGB plus observed robot-state fusion
on an explicitly restricted cohort. Training readiness: NO-GO at this boundary.**
The remaining whole-video checks and researcher review are required before a
full experiment starts. This is not a dataset rejection, a trained result, or a
claim that fusion/weight transfer will help.

The independent AI-assisted visual review was locked byte-for-byte before key
comparison: SHA-256 `{lock['source_sha256']}`. All **19 decided judgments agree**
with the source labels; **zero decided disagreements**; **B02 remains uncertain**
and its native label is failure. Decision coverage is19/20. The selected pilot
does not estimate population accuracy, human annotation reliability or ML skill.

| Evidence level | Exact result |
| --- | --- |
| Native original annotation records and converted joins | 5,202; 4,545 native failures /657 no-failure records |
| Actual numerical payloads verified against source SHA-256 | 5,202 tables; 1,297,146 rows; no nonfinite measurements |
| Published RGB inventory and same-ID numerical joins | 15,606 videos; all three camera paths present per episode |
| Constant-position quarantine | 173 episodes, including11 no-failure records |
| Exact multimodal duplicate components | Six pairs; six higher-ID copies excluded from derived cohorts |
| Native human-intervention category | 141 episodes; restriction is outcome-derived, not independent human detection |
| New coordinate-convention quarantine | Entire canonical task55:500 episodes; 499 additional exclusions beyond V1 |
| Conservative V2 core | **{core['core_episodes']:,}: {counts['failure']:,} failure /{counts['success']:,} no-failure;99 tasks, all with both labels** |
| Union of excluded/quarantined native episodes | **818**; individual reasons overlap |
| V2 episodes already covered by decoded three-camera pilot | **19**; B02 retained despite visual abstention |
| V2 episodes awaiting full RGB payload checks | **4,365** |

The original 4,883-row screen is preserved, but it missed gross finite spikes and
a task-dependent coordinate relationship. Values include position33070.77734375,
position-292.6617431640625 and velocity28.92799949645996 in native units. For
input-selected episodes2791,3034,5080, all nine original-HDF5/converted observation
array comparisons have maximum error zero. Only160,512 numerical/metadata bytes
were ranged from their original files; original videos were not downloaded.
No signs or values were silently corrected. The conservative500-episode
quarantine means unresolved calibration, not that these labels are wrong.

Fourteen position, twelve nonplaceholder velocity and two gripper-effort fields
provide28 candidate measured channels. They are **not force/torque**. Native
units/calibration and per-device hardware clocks remain unverified.

Five outer and four inner task-disjoint partitions and25 base-fit T/V/C/
assessment plans are enumerated for V2. Canonical task groups do not establish
independent operators, sessions, scenes, object instances or robots.

REASSEMBLE's original extractor is RT-DETR-R18VD's CNN only; stage-map spatial
means concatenate to896 features and sixteen frames are averaged. The completed
100-epoch source study has a valid full-backbone checkpoint selected at epoch47:
115 compatible CNN tensors,69 changed, with updates across the stem and all four
stages; running moments unchanged. Its selected-split AP is0.2125845033 versus
0.1937755776 for the frozen control. The saved paired AP interval includes zero.
The larger active full-CNN study has **{len(reference['main_completed_C_fit_receipts'])}/75 completed fits** in
the timestamped snapshot. **No ViFailback weight transfer has been performed.**

The proposal includes visual-only; balanced sensor logistic; sensor HGB;
probability averaging; newly fitted static F2; quality-only F5 gating; frozen/
full-CNN25/50-epoch budgets; seeds42,123,20261023. All models use identical held-out
episodes and nested lineage. Native failure AP is primary, with success AP,
AUROC, calibration and grouped uncertainty because V2 failure prevalence is
{prevalence:.6%}. No results were inspected to choose this proposal; no model was fit.
''')

    comparison_table = md_table(['Case','Locked prediction','Native label','Comparison','Original episode','Native category'],[
        [row['blind_id'],row['locked_prediction'],row['native_outcome'],row['comparison'],row['episode_index'],row['native_failure_type'] or 'none'] for row in comparison])
    text('01_UNBLINDING/UNBLINDING_REPORT.md', f'''# Locked review versus native annotations

The supplied review is an AI-assisted independent interpretation, not a separate
human annotation. Its predictions were copied and hashed before opening the key
in this audit. Lock: `../00_LOCKED_REVIEW/REVIEW_LOCK.json`; source review hash:
`{lock['source_sha256']}`. The original review and its observation text are intact.

The preserved archive is
`DATASET_RESEARCH/VIFAILBACK_VERIFICATION/PORTABLE_REVIEW_EXPORTS/20261028T222841Z/VIFAILBACK_UNBLINDING.zip`.
Its SHA-256 is `{unblind['source_key_archive_sha256']}`. ZIP CRC, original export
receipt, and byte equality with the separate original key all pass. Every one
of20 key entries matches source episode identity, original HDF5 path, source
task/episode, native outcome and failure category in the pinned conversion.
All5,202 nested original annotations were separately rejoined to109 original
author JSON files and match exactly, with receipt hashes verified.

Conversion revision: `619791b94f61667333fe179d471051e0bca0e06f`.
Original revision: `21df46c2585c52e5a62df5f4b946bae6cbc6fed7`.
The comparison time and key/source hashes are in `UNBLINDING_VERIFICATION.json`;
the full original observations, confidence and identities are in
`LOCKED_PREDICTIONS_VS_NATIVE_LABELS.csv`.

{comparison_table}

Among ten native no-failure episodes, ten locked predictions say success.
Among ten native failure episodes, nine locked predictions say failure and
one abstains. **19 agreements,0 disagreements,1 uncertain; decided agreement19/19,
coverage19/20.** B02's drawing ambiguity remains a low-confidence abstention;
the newly revealed failure/task-planning label does not retrospectively change
it. No20/20 accuracy claim is warranted. Sparse frames may miss transient events,
and native failure detection is not independently verified final mechanical success.

B20 independently noted a human hand and noncompletion; the native category is
human intervention. It remains an agreed case in this comparison, while its
original episode4570 is excluded from the restricted training/acquisition core.
Human involvement cannot automatically be inferred absent from other records.
No notes, object descriptions or confidence judgments were rewritten after
unblinding. No extra reviewer decision was invented for B02.
''')

    split_counts = list(csv.DictReader((RUN / (V2 + 'SPLIT_CLASS_COUNTS_V2.csv')).open()))
    outer_rows = [row for row in split_counts if row['inner_fold']=='0']
    fold_table = md_table(['Outer test fold','Test tasks','Test episodes','Failure','No failure'],[
        [row['outer_fold'],row['test_tasks'],row['test_episodes'],row['test_failure'],row['test_success']] for row in outer_rows])
    text('02_COHORT_AND_SPLITS/COHORT_READINESS_AND_GROUPING.md', f'''# Complete release audit, conservative cohort and group independence

The whole pinned **metadata and numerical release** was audited, rather than
only the pilot. Every one of5,202 native labels matches original annotations;
episode/task/instruction/frame-length joins and all numerical row/global/frame
indices match. All15,606 published RGB paths exist in the pinned inventory.
Inventory presence and publisher SHA-256 identity are not whole-video decoding
or semantic proof that a camera sees the intended event. No source file was
removed or rewritten.

## Native semantics and counts

Native `annotation.failure_detection` yes/no is the primary target. The
conversion's `episode_success` is derived from that field. Do not equate it with
a separately mechanically measured end-state success label or frame-level fault
onset. Native counts are4,545 failures/657 no-failure episodes; categories are
2,771 gripper6D-pose,988 gripper-state,645 task-planning and141 human-intervention.
All100 canonical task instructions initially contain both labels;109 source
directories contain nine task variants. Source-directory suffixes are not
verified sessions.

## Eligibility versions and exclusions

All5,202 Parquet payloads match official release hashes and pass schema/identity/
finite-value checks. Scientific QC is stricter than valid parsing. V1 quarantines
173 fully constant position traces and six higher-ID exact duplicate copies,
then restricts away141 native human-intervention records:319 unique exclusions,
4,883 candidates. There is one overlap between the duplicate and native human
flags. This screen is retained unchanged.

V2 additionally quarantines canonical task55 (`pick_place_chem_ep1` and `_ep2`)
pending coordinate-convention clarification:500 native episodes,483 failures and
17 no-failure records. One was already a duplicate;499 additional V1 candidates
are removed. In498/500 episodes the median signed position-derivative/velocity
correlation is negative; group medians are approximately-0.91. This is a
systematic native-coordinate issue, not a conversion mismatch or established
bad-label finding. The input-derived rule requires at least20 diagnostics,
more than95% negative medians and group median below-0.5; it selects only task55.
Gross position/velocity spikes are also quarantined explicitly:3 position and6
velocity episodes,8 distinct. Those are already covered by task55 or a native
human flag. Threshold10 is in uncalibrated native units: a conservative
mixed-scale quarantine, not an asserted physical joint limit.

The proposed primary V2 core has **4,384 episodes:3,755 native failures/629
no-failure,99 tasks,all with both labels**. Its818 unique exclusions/quarantines
are enumerated with all overlapping reasons in
`V2_CONSERVATIVE_CORE/CORE_ELIGIBILITY_AND_EXCLUSIONS_V2.csv`.
`ELIGIBLE_CORE_EPISODES_V2.csv` gives every retained original identity. B02 is
retained: visual abstention does not invalidate an otherwise verified native label.

The native-human restriction explicitly uses outcome-derived annotation metadata.
It defines a restricted estimand, not label-blind QC, and cannot prove the
remaining clips have no people. The all-native and5,023-row sensor screen are
preserved for sensitivity planning; do not compare scores on different cohorts
as though they were paired architecture improvements.

## Exact duplicates and dependence

All three published camera hashes and all actual state/velocity/effort arrays
match for these six pairs:372/375,851/855,2345/2445,2462/2484,2841/2868,4114/4124.
Native labels agree within every pair. Keep the smaller original ID in derived
cohorts and preserve every raw copy. All Parquet files have distinct file hashes,
so per-file Parquet hashes alone would miss this duplication. The complete
numerical-content hash search finds exactly the same six components. A separate
32-position,3-decimal position-signature search yields additional candidates,
largely stationary/bad traces; it is not exhaustive near-duplicate detection.

Grouping transitively joins canonical task identities and exact numerical/video
components. No remaining cross-task exact component forces extra merges. There
are99 V2 task groups. Sessions/operators/dates/robot serials/object instances
are not supplied in the audited metadata; `_ep1`/`_ep2` are not session evidence.
Shared objects, setup and related instructions can cross task folds. This
protocol evaluates held-out tasks under the released setup, not new robots,
sites, operators, scenes or genuinely new physical object instances.

## Enumerated split plan

Five outer task-disjoint folds and four inner folds use a label-blind SHA-256
ordering of task-component IDs with seed20261029. Views, frames, sensor rows and
duplicates of an episode never split apart. Every fold has both labels. Actual
train/validation/test IDs are in `V2_CONSERVATIVE_CORE/OUTER_INNER_SPLITS_V2.json`;
all20 triples are complete, disjoint and independently asserted.

{fold_table}

`BASE_FIT_T_V_C_ASSESSMENT_V2.json` enumerates25 base fits per visual condition/
seed:four inner OOF fits and one outer-assessment fit for each outer fold.
Within each fitting pool, hashed task groups are assigned60% T(model/scalers),
20% V(epoch/hyperparameter choice),20% C(calibration). Assessment groups are
excluded from all three roles. Every role has both outcomes. The same plans
apply to sensors, visual branches, initialization conditions and all seeds.
Only inner-assessment probabilities become final F2/gate training rows. Fixed
fusion hyperparameters avoid leaky meta-selection; any later tuning requires
an additional nested level of branch predictions, not just a split of already
computed OOF rows.

## Availability and immediate acquisition requirements

**Remote published missing paths:0.** Local whole-RGB verification is different:
only19 V2 episodes have already decoded all three pilot views. **4,365 V2 episodes
remain unverified as actual video payloads**. V2 is therefore an exact
acquisition/protocol core, not a certified whole-visual training set.

| Scope | Files | Published bytes | Additional local files | Additional bytes |
| --- | ---: | ---: | ---: | ---: |
| Primary high camera | {high['files']:,} | {high['bytes']:,} | {high['missing_files']:,} | {high['missing_bytes']:,} |
| All three cameras | {all_rgb['files']:,} | {all_rgb['bytes']:,} | {all_rgb['missing_files']:,} | {all_rgb['missing_bytes']:,} |

Every required filename/size/SHA-256/local verification state is in
`V2_CONSERVATIVE_CORE/REQUIRED_RGB_FILE_MANIFEST_V2.csv`. All5,202 numerical tables
are present;5,180 new tables used213,092,922 bytes,22 existing tables were reused.
No full-corpus videos were downloaded in this follow-up. Later acquisition must
use the pinned revision, verify checksum/frame count/PTS/16-frame decoding and
document human/overlay/visibility QC independently of outcomes. Any changed
eligibility produces a new version and preserves the current manifests; never
reshuffle splits in response to model/test performance.
''')

    channel_table = md_table(['Input','Retained indices','Excluded structural placeholders','Interpretation'],[
        ['observation.state','0–13','none','14 native observed joint/gripper positions'],
        ['observation.velocity','0–5 and7–12','6 and13 globally zero','12 native joint-velocity fields'],
        ['observation.effort','6 and13','12 arm-joint fields globally zero','two native gripper-effort fields; not force/torque']])
    text('03_SENSOR_QUALITY/SENSOR_QUALITY_AUDIT.md', f'''# Full numerical sensor audit

All5,202 actual Parquet payloads,1,297,146 rows, were acquired/reused and verified
against the pinned public LFS SHA-256 inventory. Every state/velocity/effort array
is N-by14,finite,correctly keyed to episode/task/frame/global index; every repeated
episode-label flag and annotated avoid/correct index matches the native record.
Those target-containing fields were used only for audit and are forbidden inputs.
Published extrema match the actual arrays; published float32 mean/std are not
reused as model population normalization or sufficient proof of quality.

{channel_table}

These are observed source fields, not the separate `action` command arrays.
Previous original-HDF5 checks covered two pilot and two constant-position source
records. Three additional input-selected checks here cover2791,3034,5080. Their
nine qpos/qvel/effort comparisons have zero conversion error; total ranged bytes
160,512,without image extraction. This verifies stored source-observation
provenance in checked originals, not every sensor's physical calibration.
Receipts and source LFS identities are in
`ADDITIONAL_ORIGINAL_SENSOR_CHECKS.json` and `../source_evidence/`.

The 173 completely constant position episodes comprise162 native failures and11
no-failure records. The prior source/video checks demonstrate real robot motion
despite frozen positions in two such recordings. This makes blanket finite-value
or timestamp checks insufficient. Individual stationary joints and globally
placeholder effort channels are different and are not mislabeled as faults.

Three gross position episodes:2960,3034,3086. Six gross velocity episodes:
2761,2832,2928,2960,2982,5080. Raw extrema include33070.77734375,-292.6617431640625
and repeated28.92799949645996. The position absolute99.9th percentile across
episode-channel extrema is approximately2.68 native units, so the large mixed
scales are not ordinary bulk variation. The recorded values are preserved;
none were clipped, imputed or sign-flipped. Source record3034 contains the same
extreme position and5080 contains the same velocity spike before conversion.

For5023 nonconstant-position episodes, the median within-episode diagnostic
correlation between position finite differences and matching velocity fields
has corpus median about0.9655. However,528 episode medians are negative;
498 belong to canonical task55's500 episodes. Individual signed correlations in
2791 are about-0.99 for channels0,1,3,5 and positive for2,4, suggesting an
unresolved axis-convention difference rather than a universal delay. The original
HDF5 arrays reproduce these inputs exactly. The cause and intended coordinate
convention are **not established**. No automatic sign correction is scientifically
justified. V2 quarantines the entire task pending clarification. Other isolated
low/negative correlations remain diagnostics because noise/static axes/sampling
can affect this check; they are not asserted hardware defects.

See [SENSOR_ANOMALY_DIAGNOSTICS.png](SENSOR_ANOMALY_DIAGNOSTICS.png),
`GROSS_NUMERICAL_OUTLIERS.csv`, `TASK_POSITION_VELOCITY_CONSISTENCY.csv`, and
`ALL_EPISODE_CHANNEL_QC.csv`(218,484 episode/channel rows). The V2 policy is
`../config/COHORT_QC_POLICY_V2.json`, separately reviewable from the initial policy.

The maximum converted timestamp/index-over25 difference is
{sensor['maximum_converted_clock_error_seconds']:.12g} seconds. This verifies the
conversion's shared25-Hz frame-clock construction and valid joins. It does not
independently measure original camera-to-device hardware synchronization,
per-channel acquisition latency, sampling jitter or calibrated physical units.
Pilot video PTS evidence remains sample-limited, as documented in the original
modality report. No offset was fitted using outcomes or failure annotations.

**Usability:** native position, velocity and gripper-effort statistics are plausible
inputs in the restricted V2 study, with target-train-only scaling and explicit
quality limits. A velocity ablation and position-plus-gripper-effort sensitivity
analysis should accompany any later result. Do not call these wrist force,
torque, six-axis wrench, or calibrated contact force. Quality-aware fusion must
not hide defective sensors or assume that low variation means normal operation.
''')

    hist_table = md_table(['Saved REASSEMBLE system','N','Failure prevalence','AP','AUROC','Brier'],[
        [row['name'],row['n'],f"{row['prevalence']:.6f}",f"{row['AP']:.10f}",f"{row['AUROC']:.10f}",f"{row['Brier']:.10f}"] for row in reference['historical_metrics_recomputed']])
    text('04_REASSEMBLE_REFERENCE/REASSEMBLE_IMPLEMENTATION_AND_CHECKPOINT_AUDIT.md', f'''# Actual REASSEMBLE reference and source checkpoint audit

Source paths below are repository-relative unless explicitly beginning `../`.
All inspected source/config/weight/prediction identities are in
`../provenance/REASSEMBLE_SOURCE_AND_CHECKPOINT_HASHES.json`.

## Executed architecture

Original source: `PekingU/rtdetr_r18vd`,revision
`ac77a11ff0170a41b771c03264987f8ce2b0d753`; directory:
`{reference['original_weights_directory']}`.
`model.safetensors` SHA-256 is
`fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093`.
Its config and processor hashes also match the historical identity manifest.

The actual primitive is
`parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01/source/visual_model.py`:
`original()` returns only `RTDetrForObjectDetection.model.backbone.model`.
The detector transformer/encoder/decoder/class/bounding-box heads do not execute.
The CNN is RT-DETR ResNet18VD,depths2/2/2/2. Stage2/3/4 maps have128/256/512 channels;
each is spatially averaged,concatenated to896,then arithmetic-mean pooled across
16 ordered frames. No temporal attention is used in this mean-pooling reference.
The head is Linear896→128,ReLU,Dropout0.1,Linear128→1. Input resizing is bilinear
640×640 with /255 rescaling; `do_normalize=false`,despite mean/std values being
present in processor metadata. Feature standardization is fitted on T only.

`src/reassemble/section1_features.py:statistics` returns ten statistics per
channel:mean,std,median,min,max,q25,q75,range,RMS and slope against normalized
progress. It is the useful reusable primitive for ViFailback's28 native channels.
`.../run_01/source/fusion.py:sensor_fit` uses T/G-only normalization,balanced
logistic C1 and a separate unweighted sigmoid calibrator on C. The older
Section1 baseline selects C from0.1/1/10. The PatchTST branch in
`src/reassemble/section1_models.py` is a distinct sensor model and is not the
statistics/logistic branch used by the minimal F2 reference. Its source domain
includes actual force/torque fields that ViFailback does not supply.

## F2 and quality-aware implementations

`src/reassemble/section1b.py` builds nested group-held-out branch probabilities
and `fit_stacker` fits unweighted LogisticRegression C1 on two probability
columns. The later `.../run_01/source/fusion.py:stacker` is the same fixed form:
sigmoid(b+w_v*p_visual+w_s*p_sensor). This **F2 is a fusion model**,not the
F-beta2 metric. Its coefficients need not be positive or sum to one.
Calibration,feature scaling and branch selection have fit-local lineage.

`src/reassemble/section2_models.py:DecisionGate` is a different mechanism:
context→Linear(hidden)→ReLU→Linear2→availability-masked softmax weights;
output logit is the convex weighted sum of the two branch logits. F4 uses action
context,F5 quality context,F6 action+quality; all include availability. The
source action one-hots and domain-specific quality dimensions must not be
copied as ViFailback task IDs. Proposed transfer reuses F5's class/mechanism,
with native quality inputs and newly learned gate weights.

`src/reassemble/additional_improvements/models.py:AnchoredAdjustment` is another
existing implementation: frozen static-F2 coefficients multiplied by1+tanh(delta)
from a small context network. It is **not** DecisionGate. Any later use must
anchor newly fitted target-domain F2 rather than source coefficients. Neither
implementation proves adaptation or robustness on ViFailback.

## Saved results checked against prediction artifacts

All point estimates below were independently recomputed from saved probability
arrays and match stored AP/AUROC/Brier to within1e-12. No training,feature
extraction,calibration fitting or neural inference was rerun. Bootstrap interval
generation and the original experiments were not independently reproduced here.

{hist_table}

The clean F5 and F6 point APs do not exceed static F2. Do not claim that
quality-aware or adaptive fusion was superior from these reference artifacts.
These are same-cohort historical results,not independent cross-domain evidence.

## CNN fine-tuning completion and transfer eligibility

The separate100-epoch two-arm comparison is complete. Both arms executed100
epochs from the original initialization. Frozen selected epoch14; full-CNN
selected epoch47 by REASSEMBLE validation AP. Actual recorded T/V/C sample and
recording identities are disjoint from the753 assessment actions in26 recordings.
The selected-job config retains an old `prediction_recordings` field from its
original inner role; actual prediction IDs/`predict` rows establish the26-recording
assessment. This stale bookkeeping is documented,not silently rewritten.

Valid CNN donor checkpoint:
`{checkpoint['path']}`

SHA-256 `{checkpoint['sha256']}`;45,347,917 bytes. Completion receipts,predictions
and checkpoint hashes agree. CPU `weights_only=True` inspection finds115
compatible CNN tensors,69 changed versus original source and46 unchanged;
stem and all four stages changed,normalization running moments did not.
See `CHECKPOINT_TENSOR_CHANGES.csv`. Thus it is genuinely trained full-CNN state,
not an untrained head or silently assumed checkpoint. The frozen-control file
contains a head and feature moments but **no backbone**,so it is not a learned
CNN donor. No detector components or source classifier/fusion coefficients should transfer.

On the matched753-action assessment,AP frozen0.1937755776,full0.2125845033;
AUROC0.6646046261 versus0.6753246753. Saved paired AP difference0.0188089257 has
conditional recording-bootstrap95% interval[-0.0364453272,0.0969255849]. This is
a post-selected single-split,seed42 study; the interval includes zero.
No new F2 was fitted in that comparison. Full-CNN training took86,271.0883
seconds(23.9642h); frozen-head training219.5726seconds. These REASSEMBLE timings
and99.74% reported kernel-busy activity do not benchmark ViFailback.

The broader active C-only study is separate: snapshot `{live['utc']}`,
**{len(reference['main_completed_C_fit_receipts'])}/75 C fits complete**,20 executed epochs per completed fit,
with original cosine50 prefix. Its three-seed/five-fold evaluation is not complete.
`ACTIVE_STUDY_STATUS_SNAPSHOT.json` and completed receipt/checkpoint paths in
`REFERENCE_AUDIT.json` preserve the observed status; the ongoing job was not
paused,resumed or otherwise managed by this audit.

The epoch47 donor was fixed using source-domain validation,not ViFailback tests.
It can support a controlled optional target transfer experiment,but **no weight
transfer or target learning has yet been executed**. Source donor variability is
still only one selected seed/fit; target seeds cannot resolve that limitation.
REASSEMBLE has action-interval failures(509/4530,11.2362%);ViFailback has native
whole-episode failure detection(V2:3,755/4,384,{prevalence:.4%}). Absolute APs are
not directly comparable across these targets/prevalences.
''')

    text('05_EXPERIMENT_PROPOSAL/REPRODUCIBLE_EXPERIMENT_PROPOSAL.md', f'''# Proposed ViFailback portability experiment — not executed

**Status: DRAFT FOR RESEARCHER REVIEW. No training authorization is inferred.**
The exact settings are `../config/EXPERIMENT_PROPOSAL.json`;30 core evaluated
systems and28 optional transfer systems are enumerated in `EXPERIMENT_MATRIX.csv`.
The proposal reuses project primitives and introduces dataset-owned adapters;
it does not duplicate the model framework.

## Target, cohort and input/output contracts

One original episode is one prediction example. Positive is original native
failure_detection=yes;negative=no. Native labels are not copied onto arbitrary
individual frames. Final mechanical task completion is not a separately verified
target. The V2 core has4,384 episodes(3,755/629),99 task groups;all model arms use
the **same eligible held-out episodes**. Human-category restriction and task55
coordinate quarantine define the estimand and must be disclosed. Do not make
visual-only easier by retaining rows that sensor-only excludes.

Primary visual input is16 full-view cam_high frames,chosen uniformly from0..N-1
by the fixed rule in config. No failure annotations,keyframes,native types,
review confidence or end-state judgments affect selection. Ordered unique indices
and matching converted timestamps are mandatory. Input tensor[B,16,3,640,640]
FP32,/255,resize bilinear,no ImageNet normalization;CNN spatial-pool+concat+frame
mean gives[B,896],new head gives[B] logits and calibrated failure probabilities.
All-three-camera extension uses the same16 temporal positions but48 RGB images;
it is a separate compute/input condition,not silently called a16-image model.
No cropping is required by the primary classifier; gallery enlargements are review aids.

Numerical input is the complete same episode,14 positions+12 nonplaceholder
joint velocities+two gripper-effort channels. Apply the historical ten-statistic
function per channel to obtain[B,280]. No fixed REASSEMBLE channel identity or
count is required. Do not call these force/torque. Dataset adapters should own
annotation joins,source frame selection,measured-column loading,channel whitelist,
label mapping and canonical-task/duplicate groups in `src/vifailback/` if later
implementation is authorized. Reuse the visual head/pooling,F2 and DecisionGate
primitives and regression-test unchanged feature behavior.

Forbidden ordinary features/context:episode/task/source IDs,instructions,
failure types,annotations,avoid/correct keyframes,source labels,human category,
source checkpoints' classifier/calibrators,or metadata containing the target.
Raw action/command columns are excluded. Duration is not added as a metadata
feature. Whole-episode frames/statistics can still contain temporal/end-state
cues,so results are retrospective native-outcome recognition,not early warning.

## Splits and fit lineage

Use the exact5×4 task-disjoint V2 partitions and25 T/V/C/assessment base plans.
All seeds,heads,sensor families,budgets,freeze rules and P/R initialization share
those IDs. T fits features/models,V selects a finite candidate/epoch,C calibrates,
assessment is prediction-only. No sample/task in an assessment set appears in
that fit's T,V,C,scalers or calibration. Canonical-task identity is grouping only.
Session/operator/object-instance independence remains unknown.

Within each outer-training set,the four inner assessment sets produce one OOF
visual and sensor probability per training episode. Concatenate these pairs and
fit final F2 or fixed-policy gate. Refit the branches with the outer T/V/C plan
and evaluate outer-test episodes once. All calibration/selection for an OOF row
must exclude that row's entire task. Splitting already-created OOF pairs into
meta-folds is insufficient if branch construction saw those meta-held-out labels.
If fusion hyperparameters/thresholds are later tuned,regenerate deeper nested
branch predictions. Here C1,gate size/epochs and threshold0.5 are predeclared.

## Models and controlled budgets

- Visual:original pretrained CNN with new head;frozen versus full-CNN updates.
  Execute25 and50-epoch budget conditions with the same cosine50 LR prefix;
  a single50-epoch trajectory can preserve selected checkpoints for each budget.
  Report the shared-prefix relationship rather than counting independent25/50 runs.
- Sensor logistic:balanced class weighting;C0.1/1/10 chosen using V AP;max_iter2000.
- Strong nonlinear sensor baseline:HGB,200 iterations,lr0.05,L2=0.1,min_leaf20,
  max_leaf7/15/31 chosen on V. Disable sklearn's random internal early stopping.
  Use T-only inverse-frequency sample weights. Reuse deterministic fits across
  matching visual arms;do not treat repeated identical predictions as replication.
- Averaging:0.5*(p_visual+p_sensor),for each sensor family.
- F2:new unweighted C1 probability logistic,refitted separately for each visual/
  sensor condition and seed on group-held-out OOF pairs. No source coefficients.
- Quality-aware fusion:existing F5 DecisionGate with native quality+availability,
  hidden16,ReLU,masked softmax,weighted clipped branch logits;fixed40 epochs,
  AdamW lr0.003,weight_decay0.001,unweighted BCE. No task/action one-hots. Refit it
  on the same OOF pairs and no source gate weights.

Three model seeds:42,123,20261023. Visual AdamW head_lr1e-3,CNN_lr1e-5,
weight_decay1e-3,gradient clipping1,microbatch1,accumulation8,FP32,no augmentation
in the portability reference. Promote original FrozenBatchNorm affine values to
trainable parameters for full-CNN,keep its running moments fixed. Every CNN arm
starts from the same declared P/R source and matched newly seeded target head.
Feature moments are fitted on target T at initialization and kept fixed during
that fit. Never reuse source-domain feature moments or target-test statistics.
Select highest V AP within each budget,ties lower weighted V BCE then earlier
epoch. Both rules execute the same budget;no test-selected stopping. T loss
uses pos_weight=N_negative/N_positive because native failure is the majority.
Unweighted C-only sigmoid calibration restores the target fitted-population prior.

The optional R extension uses the verified source epoch47 checkpoint:
`{checkpoint['path']}`
with SHA-256 `{checkpoint['sha256']}`. Transfer115 compatible CNN tensors only;
discard source head,moments,calibration,F2/gate state. P and R share inputs,
groups,budgets,selection,trainable parameter rules and seeds. Fix this donor
before any target test;do not select another donor from target performance.
One source donor cannot establish stability across source-training seeds.

## Metrics, uncertainty and safeguards

Primary:failure Average Precision. Report prevalence({prevalence:.6%} in V2) and
the no-skill constant-score AP baseline. Because the positive class is dominant,
also report AP_success,macro AP,macro-task AP,AUROC,balanced accuracy,MCC,macroF1,
class-specific precision/recall,Brier,log loss and fixed10-bin ECE/reliability
diagrams. Threshold0.5 is predeclared. No test-optimal threshold or best-seed/fold
result is substituted for the full result table.

For each seed,pool its cross-fitted outer predictions and also show every fold.
Use2000 paired task-cluster bootstrap replicates for mean per-seed metric
differences,common resampled tasks across arms. Seeds/folds are not independent
samples;three-seed variability is descriptive. Separate visual benefit(P/R or
frozen/fine)from incremental F2 benefit over each matched unimodal branch.
Inspect train/V curves and calibration for overfitting;do not tune using outer
tests or exclude poorly performing tasks after seeing results.

Quality-only prediction and quality-neutral/permuted gate ablations are useful
prespecified controls for shortcuts. Clean-data quality gating alone is not a
robustness result. Corruption/missing-modality claims require a separately
specified paired corruption and availability evaluation;no such claim is made here.

## Loading, storage and computational feasibility

No ViFailback throughput/VRAM benchmark or smoke training was run. The GPU is
already used by a separate REASSEMBLE study;this task used CPU verification only.
After later authorization,benchmark actual ViFailback decoding/forward/training
on T-only samples with workers0/2/4,decoder threads1/2,pinned memory,persistent
workers and accumulation8;check numerical behavior,worker stability,CPU wait,
throughput,VRAM and recovery. Do not assume REASSEMBLE's utilization applies.

Primary high-camera missing payload is{high['missing_bytes']:,} bytes
({high['missing_bytes']/1024**3:.3f}GiB);all-three missing payload is
{all_rgb['missing_bytes']:,} bytes({all_rgb['missing_bytes']/1024**3:.3f}GiB).
The whole16-frame640×640 uint8 tensor cache for4,384 episodes would be about
80.27GiB before compression,so use bounded new-run caches,not a full resident
cache. Cache only immutable decoded pixels/frozen features with source/model/
processor/selection hashes;fine-tuned embeddings must be recomputed as CNN
weights change. Preserve all existing historical caches/data.

For one initialization and both backbone rules,the25 base fits×three seeds give
75 full-CNN50-epoch trajectories and75 frozen-head trajectories,with25-budget
snapshots sharing prefixes. The actual enumerated T sizes total43,061 per one
epoch over25 fits. Full-CNN50 across three seeds means{t_presentations:,}
episode presentations. At the **REASSEMBLE-only** rate2.032 episodes/s this is
about{extrapolated_hours:.1f}training GPU-hours before validation/calibration/I/O;
this is a planning extrapolation,not a ViFailback benchmark or promised runtime.
An R extension roughly doubles this CNN exposure. Selected full-CNN weights
alone occupy roughly3.4GB for75 fits;two180MB recovery generations per fit would
add about27GB,plus caches/raw videos/curves. Preflight storage and checkpoint
retention must be reviewed;do not silently delete completed evidence to fit.

## Required prelaunch acceptance checks

1. Researcher reviews V2 restrictions and protocol;resolve or retain documented
   coordinate quarantine without automatic sign correction.
2. Retrieve only needed pinned video paths;verify hashes,count/dimensions/PTS,
   all16 frames,frame/table association and visibility/overlays/human presence.
   Version any revised eligible cohort and preserve the current split maps.
3. Validate frame/sensor/label contracts,forward/gradient paths,save/reload,
   group disjointness,per-row OOF lineage,metric calculations and bounded loading.
4. Verify P/R CNN-only loading and reinitialized target head/moments/calibrators.
5. Freeze implementation/config/software/checkpoint hashes before outer assessment.

No training,neural inference,new model calibration or transfer result is supplied
by this verification task. This document is an executable research specification
for later implementation/authorization,not evidence that the architecture works.
''')

    text('UNRESOLVED_BLOCKERS.md', '''# Outstanding blockers and limits

**Full-cohort training readiness: NO-GO until the required gates below pass.**

1. Actual RGB payload QC remains for4,365 V2 episodes. Remote paths/hashes and
   numeric joins exist, but decoding/duration/PTS/content for these recordings
   were not certified. The nineteen paired core pilot examples are not4,384
   verified visual examples. No full-corpus video download was undertaken here.
2. Canonical task55's500 original trajectories have unresolved coordinate/sign
   conventions;gross native spikes occur in eight distinct episodes. V2
   quarantines them or their already-excluded records. Reinstatement requires
   documented source clarification/validation and another cohort version;
   no silent signs/values were repaired.
3. Native human-intervention categorization is not an exhaustive human-presence
   mask. Its outcome-derived exclusion changes the population. Independent,
   label-blind visual QC is still needed to assess incidental hands/overlays/
   visibility shortcuts. A blinded AI screen is not human-reliability evidence.
4. Original per-device timestamps and physical sensor calibration/units remain
   unverified. Converted-frame equality establishes index pairing,not hardware
   synchronization. Position/velocity/gripper effort must not be described as
   measured force/torque.
5. Session/operator/date/robot/object-instance identities are unavailable.
   Task-disjoint splits are explicit and leakage-safe for known identities;
   hidden session and near-duplicate dependencies cannot be ruled out.
6. A valid full-CNN donor exists, but the larger75-fit source study is incomplete
   and source donor variation is not evaluated. No ViFailback CNN transfer,
   sensor model,averaging,F2 or quality-aware model was trained. There is no
   target evidence of multimodal complementarity,transfer benefit or robustness.
7. The proposed matrix is computationally substantial. ViFailback throughput,
   memory,storage,worker reliability and numerical behavior require a later
   authorized preflight. The current unrelated REASSEMBLE job remains active.

No access/authentication blocker occurred for the pinned numerical release or
the bounded original checks. Existing data,experiments,blinded review and export
archives were preserved. Nothing was staged or committed.
''')
    print('Created review reports and unexecuted experiment proposal', now)
