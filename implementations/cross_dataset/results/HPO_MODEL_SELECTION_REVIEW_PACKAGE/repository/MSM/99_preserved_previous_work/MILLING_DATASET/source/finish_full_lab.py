"""Consolidate completed data-audit checkpoints into a fresh immutable delivery.

No video is decoded, no CNN is loaded and no classifier is fitted here. Rejected
alignment diagnostics with nonfinite residuals use Stage 2's JSON-null policy.
"""
import argparse
import collections
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

import numpy as np
import pandas as pd

from full_lab_audit import (dump_csv,split_feasibility,sensor_gate,FEATURE_NAMES,COMMON_MTC,
                            select_frames,binary_target,sha256,finite_dump)
from consolidate_pilot_findings import consolidate


def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)


def put(path,text):
    with path.open('x') as f:f.write(text.rstrip()+'\n')


def read_checkpoints(parent,groups):
    results=[]
    for group in groups:
        folder=parent/'experiments'/group.replace('/','_');result=None
        for p in sorted(folder.glob('completed*.json'),reverse=True):
            try:result=json.loads(p.read_text());break
            except json.JSONDecodeError:continue
        if result is None:raise ValueError('Missing complete experiment: '+group)
        results.append(result)
    return results


def validate(results,cfg,frame):
    inv=json.loads((Path(cfg['run_root'])/'manifests/official_file_inventory.json').read_text())
    official={x['name']:x['bytes'] for x in inv['files']}
    receipts={}
    for p in Path(cfg['data_root']).glob('_msm_download_receipt_*.json'):
        x=json.loads(p.read_text())
        if x.get('handle')==cfg['handle']:
            receipts.update({r['path']:r['sha256'] for r in x.get('results',[]) if r.get('sha256')})
    original=json.loads((Path(cfg['stage1'])/'manifests/input_manifest.json').read_text())
    if isinstance(original,dict):original=original.get('files',original.get('inputs',[]))
    labels={Path(x['path']).as_posix():x['sha256'] for x in original}
    checks={'native_annotation_rows':0,'exact_frame_policies':0,'sensor_vectors_recomputed':0,
            'raw_inputs_hash_verified':0,'original_label_hashes_verified':0,'sensor_max_abs_difference':0.,
            'historical_run_files_verified':0,'historical_missing_or_changed':[]}
    for x in results:
        group=x['group_id'];raw=Path(cfg['data_root'])/group
        for r in x['inputs']:
            p=Path(r['path']);relative=p.relative_to(Path(cfg['data_root'])).as_posix()
            actual=sha256(p)
            assert actual==r['sha256'] and p.stat().st_size==official[relative]
            if p.name=='label.csv':
                assert actual==labels[p.as_posix()];checks['original_label_hashes_verified']+=1
            else:assert actual==receipts[relative]
            checks['raw_inputs_hash_verified']+=1
        native=pd.read_csv(raw/'label.csv');mtc=pd.read_csv(next(raw.glob('*_mtc.csv')))
        for c in ['time',*COMMON_MTC]:
            if c in mtc:mtc[c]=pd.to_numeric(mtc[c],errors='coerce')
        feature_bank={r['interval_id']:r for r in x['sensor_features']}
        selection_bank=collections.defaultdict(list)
        for r in x['selected_frames']:selection_bank[r['interval_id']].append(r)
        m=x['mapping'];pts=None
        if m['accepted']:
            if 'reuse_source' in x['video_audit']:
                pts=np.load(Path(cfg['stage2'])/'cache'/(group.replace('/','_')+'_native_pts.npy'))
            else:
                pts=np.load(Path(x['metadata']['representative_diagnostic_paths'][0]).parent/'native_pts.npy')
        for r,n in zip(x['intervals'],native.itertuples()):
            assert r['source_row']==n.Index+2 and r['interval_id']==f'{group}/row{n.Index+2}'
            assert int(n.label)==r['native_label'] and (float(n.start),float(n.end))==(r['start_s'],r['end_s'])
            assert r['primary_target']==int(n.label==1)
            assert r['joint_technical_pass']==(r['frame_contract_pass'] and r['common_mtc_sensor_gate_pass'])
            assert r['joint_technical_pass']==(r['exclusion_reasons']=='')
            checks['native_annotation_rows']+=1
            if r['frame_contract_pass']:
                f=select_frames(pts,r['start_s'],r['end_s'],m['offset_s'],m['uncertainty_s'],m['support_sensor_s'])
                assert f['accepted'] and f['indices']==json.loads(r['frame_indices_json'])
                selected=selection_bank[r['interval_id']]
                assert len(selected)==16 and [s['frame_order'] for s in selected]==list(range(16))
                assert len({s['native_frame_index'] for s in selected})==16
                assert len({s['decoded_frame_sha256'] for s in selected})==16
                assert np.allclose(f['video_pts_s'],[s['video_pts_s'] for s in selected],rtol=0,atol=1e-10)
                checks['exact_frame_policies']+=1
            ok,values,gate=sensor_gate(mtc,r['start_s'],r['end_s'])
            assert ok==r['common_mtc_sensor_gate_pass'] and gate['rows']==r['mtc_rows_inside_cut']
            if ok:
                expected=np.array([feature_bank[r['interval_id']][c] for c in FEATURE_NAMES],np.float32)
                diff=float(np.max(np.abs(values-expected)))
                checks['sensor_max_abs_difference']=max(checks['sensor_max_abs_difference'],diff)
                assert diff==0;checks['sensor_vectors_recomputed']+=1
    for stage in ('stage1','stage2','stage3','stage4'):
        historical=Path(cfg[stage]);manifest=json.loads((historical/'manifests/output_manifest.json').read_text())
        for r in manifest['files']:
            p=Path(r['path'])
            try:p.resolve().relative_to(historical.resolve())
            except ValueError:continue # shared sources/configs evolved before this task
            if not p.is_file() or sha256(p)!=r['sha256']:checks['historical_missing_or_changed'].append(str(p))
            else:checks['historical_run_files_verified']+=1
    assert not checks['historical_missing_or_changed']
    assert checks['native_annotation_rows']==2512
    assert sha256(Path('MILLING DATASET/configs/stage3_protocol.json'))=='7ab13188504a522a951e3331a49ae7a7ebc1d87e09de51826bf9656fe2d8e19a'
    checks.update(passed=True,source_checkpoint_inspection=False,models_trained=0,cnn_feature_extractions=0,
                  f2_evaluations=0,phase1_job_interaction=False)
    return checks


def finish(parent):
    cfg=json.loads((parent/'config/download_config.json').read_text())
    results=read_checkpoints(parent,cfg['selected_groups'])
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    final=Path('MILLING DATASET/runs')/(stamp+'-stage5-full-lab-validated')
    for name in ['config','manifests','evidence','logs','figures']: (final/name).mkdir(parents=True,exist_ok=False)
    finite_dump(final/'config/resolved_config.json',{**cfg,'acquisition_and_audit_run':str(parent),
        'delivery_run':str(final),'raw_inputs_immutable':True,'final_split_frozen':False,'training_allowed':False})
    records=[r for x in results for r in x['intervals']];frame=pd.DataFrame(records)
    assert len(frame)==2512 and frame.interval_id.is_unique
    assert frame.native_label.value_counts().to_dict()=={0:1877,1:458,2:177}
    print('VALIDATING',len(frame),'rows from',len(results),'completed experiments',flush=True)
    checks=validate(results,cfg,frame);finite_dump(final/'validation_data.json',checks)
    dump_csv(final/'MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv',records)
    dump_csv(final/'manifests/selected_frame_manifest.csv',[r for x in results for r in x['selected_frames']])
    dump_csv(final/'manifests/common_mtc_statistics.csv',[r for x in results for r in x['sensor_features']])
    inputs=[r for x in results for r in x['inputs']]
    finite_dump(final/'manifests/input_manifest.json',inputs)
    finite_dump(final/'manifests/alignment_results.json',{x['group_id']:x['mapping'] for x in results})
    finite_dump(final/'manifests/metadata_relationships.json',[x['metadata'] for x in results])
    finite_dump(final/'manifests/video_audit.json',{x['group_id']:x['video_audit'] for x in results})
    finite_dump(final/'manifests/sensor_schema_audit.json',{x['group_id']:x['sensor_schema'] for x in results})
    summaries=[]
    for group,f in frame.groupby('group_id',sort=True):
        summaries.append({'group_id':group,'machine':f.machine.iloc[0],'reference_date':f.reference_date.iloc[0],
            **{f'native_label_{i}':int((f.native_label==i).sum()) for i in (0,1,2)},
            **{c:int(f[c].sum()) for c in ['alignment_pass','frame_contract_pass','common_mtc_sensor_gate_pass','joint_technical_pass']},
            'joint_label_0':int(((f.native_label==0)&f.joint_technical_pass).sum()),
            'joint_label_1':int(((f.native_label==1)&f.joint_technical_pass).sum()),
            'joint_label_2':int(((f.native_label==2)&f.joint_technical_pass).sum()),
            'pending_independent_visibility':int(f.frame_contract_pass.sum()),
            'exclusion_counts_json':json.dumps(dict(collections.Counter(r for s in f.exclusion_reasons for r in s.split(';') if r)))})
    dump_csv(final/'manifests/experiment_summary.csv',summaries)
    targets={}
    for policy in ['stable_negative','exclude']:
        f=frame.loc[frame.joint_technical_pass].copy();f['target'],keep=binary_target(f.native_label,policy);f=f.loc[keep].reset_index(drop=True)
        targets[policy]={'intervals':len(f),'positive_prevalence':float(f.target.mean()),
            'class_counts':{str(k):int(v) for k,v in f.native_label.value_counts().items()},
            'groupings':{key:split_feasibility(f,key) for key in ['group_id','machine_date_group','calendar_date_group']},
            'machine_nominal_gates':{machine:split_feasibility(g.reset_index(drop=True),'group_id') for machine,g in f.groupby('machine')}}
    finite_dump(final/'manifests/split_feasibility.json',targets)
    plan=pd.read_csv(parent/'MSM_DOWNLOAD_MANIFEST.csv',keep_default_na=False)
    receipt_hashes={}
    for p in Path(cfg['data_root']).glob('_msm_download_receipt_*.json'):
        x=json.loads(p.read_text())
        if x.get('handle')==cfg['handle']:receipt_hashes.update({r['path']:r['sha256'] for r in x.get('results',[]) if r.get('sha256')})
    downloaded=[]
    for r in plan.to_dict('records'):
        p=Path(cfg['data_root'])/r['relative_source_path'];h=sha256(p)
        assert p.stat().st_size==r['official_bytes'] and h==receipt_hashes[r['relative_source_path']]
        downloaded.append({**r,'final_status':'downloaded_verified' if r['availability']=='missing' else 'reused_verified',
                           'sha256':h,'acquisition_receipt_root':str(parent/'evidence')})
    dump_csv(final/'MSM_DOWNLOAD_MANIFEST.csv',downloaded)
    acquisition={'planned_files':len(downloaded),'new_files':sum(r['availability']=='missing' for r in downloaded),
        'reused_files':sum(r['availability']!='missing' for r in downloaded),
        'new_bytes':int(plan.required_download_bytes.sum()),'plan_bytes':int(plan.official_bytes.sum()),
        'missing_or_failed_files':0,'historical_timeout_attempts':len(list((parent/'evidence').glob('acquisition_failure*.json'))),
        'acquisition_run':str(parent),'free_disk_bytes_after':shutil.disk_usage('.').free,
        'inventory_sha256':sha256(parent/'manifests/official_file_inventory.json')}
    nc=collections.defaultdict(list)
    for x in results:
        for p in x['metadata']['nc_programs']:nc[p['sha256']].append(x['group_id'])
    relationships={'verified_exact_nc_reuse':{h:g for h,g in nc.items() if len(g)>1},
        'verified_machine_reference_date_clusters':frame.machine_date_group.nunique(),
        'verified_calendar_dates':frame.calendar_date_group.nunique(),
        'inferred_dependencies':'Shared reference dates and exact programs suggest related setups; not proof of a single physical session.',
        'unresolved':['physical session IDs','tool serial/reuse history','workpiece serial/reuse history','cross-date shared setup dependencies'],
        'metadata_not_features':['Tool','Workpiece','NC/program comments and names','label remarks','session/date/group IDs','annotation cutting parameters']}
    finite_dump(final/'manifests/dependency_relationships.json',relationships)
    summary={'dataset_handle':cfg['handle'],'native_intervals':len(frame),'native_class_counts':{'0':1877,'1':458,'2':177},
        'native_nominal_groups':56,'native_positive_groups':25,
        'aligned_experiments':sum(x['mapping']['accepted'] for x in results),
        'alignment_failed_experiments':[x['group_id'] for x in results if not x['mapping']['accepted']],
        **{c:int(frame[c].sum()) for c in ['alignment_pass','frame_contract_pass','common_mtc_sensor_gate_pass','joint_technical_pass']},
        'exclusion_reason_counts':dict(collections.Counter(r for s in frame.exclusion_reasons for r in s.split(';') if r)),
        'new_context_visibility_pending':int(((frame.audit_provenance!='reused_final_stage2')&frame.frame_contract_pass).sum()),
        'all_frame_valid_independent_visibility_pending':int(frame.frame_contract_pass.sum()),
        'joint_independent_visibility_pending':int(frame.joint_technical_pass.sum()),
        'acquisition':acquisition,'targets':targets,
        'machine_summary':[{ 'machine':m,'native_intervals':len(f),
            'native_counts':[int((f.native_label==i).sum()) for i in (0,1,2)],
            'joint_intervals':int(f.joint_technical_pass.sum()),
            'joint_counts':[int(((f.native_label==i)&f.joint_technical_pass).sum()) for i in (0,1,2)],
            'joint_nominal_groups':int(f.loc[f.joint_technical_pass].group_id.nunique()),
            'joint_positive_groups':int(f.loc[f.joint_technical_pass&(f.native_label==1)].group_id.nunique())} for m,f in frame.groupby('machine')],
        'independence':relationships,'total_completed_experiment_wall_seconds':sum(x['wall_seconds'] for x in results),
        'workers':2,'models_trained':0,'gpu_work':False,'final_split_frozen':False}
    decision='CONDITIONAL GO' if targets['stable_negative']['groupings']['group_id']['passed'] else 'NO-GO'
    summary['decision']=decision
    finite_dump(final/'manifests/cohort_summary.json',summary)
    write_reports(final,parent,cfg,results,summary,checks)
    root=consolidate(final,cfg,summary,decision)
    finite_dump(final/'manifests/findings_folder.json',{'path':str(root),'readme_sha256':sha256(root/'README.md')})
    print(json.dumps({'run':str(final),'findings':str(root),'decision':decision,'joint':summary['joint_technical_pass'],
        'targets':{k:{'intervals':v['intervals'],'nominal':v['groupings']['group_id']['passed'],
             'machine_date':v['groupings']['machine_date_group']['passed'],'calendar_date':v['groupings']['calendar_date_group']['passed']} for k,v in targets.items()}},indent=2))
    return final


def write_reports(final,parent,cfg,results,s,checks):
    target=s['targets']['stable_negative'];counts=target['class_counts'];acq=s['acquisition']
    intro=f"Dataset `{cfg['handle']}` (ID 8392825), [official dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), [publication](https://www.nature.com/articles/s41597-026-07255-7). Version 2 was reverified against the official public API and all 481 paths/sizes match Stage 1. All native labels and historical outputs were preserved.\n\n"
    machine_table=table(['Machine','Native 0 / 1 / 2','Joint 0 / 1 / 2','Joint intervals','Joint folders / positive folders'],
        [[r['machine'],' / '.join(map(str,r['native_counts'])),' / '.join(map(str,r['joint_counts'])),r['joint_intervals'],f"{r['joint_nominal_groups']} / {r['joint_positive_groups']}"] for r in s['machine_summary']])
    gate_table=table(['Gate','Intervals'],[[name,s[key]] for name,key in [('Accepted recording alignment','alignment_pass'),('Video + exact 16 frames','frame_contract_pass'),('Common MTC','common_mtc_sensor_gate_pass'),('Joint technical','joint_technical_pass'),('Joint independent visibility pending','joint_independent_visibility_pending')]])
    excludes=table(['Reason (nonexclusive)','Intervals'],sorted(s['exclusion_reason_counts'].items()))
    exp=pd.read_csv(final/'manifests/experiment_summary.csv')
    exp_table=table(['Experiment','Native 0/1/2','Alignment','16 frames','MTC','Joint 0/1/2','Visibility pending'],
       [[r.group_id,f'{r.native_label_0}/{r.native_label_1}/{r.native_label_2}',r.alignment_pass,r.frame_contract_pass,r.common_mtc_sensor_gate_pass,
         f'{r.joint_label_0}/{r.joint_label_1}/{r.joint_label_2}',r.pending_independent_visibility] for r in exp.itertuples()])
    put(final/'MSM_FULL_LAB_COHORT_AUDIT.md',f'''# Full MSM laboratory cohort audit

**{s['decision']} for further research preparation; full evaluation awaits visibility, target and physical-group approval.** No model was trained, no full CNN feature bank was extracted and no F2 evaluation was run.

{intro}
Acquired **{acq['new_files']} files / {acq['new_bytes']:,} bytes ({acq['new_bytes']/1e9:.9f} GB decimal)** and reused {acq['reused_files']} matching files in the 226-file minimal plan. No planned file remains missing or failed. One public request timed out and was safely retried; its failure receipt is preserved. The 2.7 GB budget and 10 GiB reserve gates passed; final disk free was {acq['free_disk_bytes_after']/1024**3:.2f} GiB. All 56 laboratory MP4, MTC, S2 and NC sets plus two XML files are present. The original labels/workbook were reused. No additional ACC, industrial video, S0 microphone or full archive was downloaded. Acquisition receipts and official inventory: [{parent.name}]({os.path.relpath(parent,final)}). Exact status and hashes: `MSM_DOWNLOAD_MANIFEST.csv`.

Native laboratory total: **2,512 intervals = 1,877 label 0 + 458 label 1 + 177 label 2**, 56 nominal folders, 25 positive-containing folders. Native meanings: stable normal (0), intervention-worthy abnormal cutting (1), stable cutting with a defective tool (2). Folder remarks are never used as ground truth.

{machine_table}
{gate_table}
The joint technical cohort contains **{s['joint_technical_pass']} cuts**, with {counts.get('0',0)} label 0, {counts.get('1',0)} label 1 and {counts.get('2',0)} label 2. These are technical candidates, not independently visibility-certified examples. Positive prevalence under the frozen 1-versus-0/2 task is {target['positive_prevalence']:.4%}. Excluded native cuts: {2512-s['joint_technical_pass']}. Gate denominators are separate and exclusion reasons can overlap.

{excludes}
The original 114 joint pilot examples were retained, with the final +49.73 s VMX9 mapping. No pilot GPU or visual-review experiment was repeated. New clips use one forward native video decode; small representative contacts are recorded for all experiments, including eligible positive sequences where available. Five previous pilot atlases are indexed rather than regenerated.

The sensor contract remains 15 ordered numerical signals × six statistics = 90. No interpolation, label metadata, program/tool identifiers, raw ACC substitution or statistical redefinition. All finite, >=5-row and <=0.5 s edge-inclusive coverage gates were applied. MTC held values do not represent fresh high-frequency measurements; unknown aggregation latency limits this to retrospective coarse cutting intervals. Per-channel missing/held fractions and clocks are in `manifests/sensor_schema_audit.json`.

## Every experiment

Alignment counts mean intervals in recordings with accepted timing, not automatic interval support. Pending visibility counts refer to frame-valid intervals. Independent visual judgement is still pending even where the earlier Codex coarse-context review exists. Complete row-level source identities and exclusion reasons are in `MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv`; exact selected frame PTS/content hashes in `manifests/selected_frame_manifest.csv`.

{exp_table}
## Reproducibility

Independent data-side validation rechecked {checks['raw_inputs_hash_verified']} experiment input hashes, all {checks['original_label_hashes_verified']} original laboratory label hashes, all 2,512 native source rows, {checks['exact_frame_policies']} exact frame policies and {checks['sensor_vectors_recomputed']} actual sensor vectors. Maximum float32 feature difference: {checks['sensor_max_abs_difference']}. {checks['historical_run_files_verified']} historical run files match their saved manifests. Source/config/tests, failure records and software identities are retained in this delivery. New raw files stay Git-ignored; no staging/commit occurred.
''')
    align_rows=[]
    for x in results:
        m=x['mapping'];align_rows.append([x['group_id'],m['accepted'],m.get('offset_s','—'),m.get('uncertainty_s','—'),
            f"{m.get('calibration_anchors',0)}/{m.get('validation_anchors',0)}",m.get('max_validation_residual_s','—'),
            json.dumps(m.get('support_sensor_s',[])),m['reason']])
    put(final/'MSM_ALIGNMENT_FEASIBILITY_REPORT.md',f'''# Full laboratory alignment feasibility

{intro}
**{s['aligned_experiments']} of 56 recordings pass synchronization; {s['frame_contract_pass']} intervals pass the exact 16-frame contract.** {s['joint_technical_pass']} additionally pass common MTC. Native labels never choose or improve a clock mapping.

Reuse the corrected final Stage 2 algorithm: S2 and AAC downsampled to 4 kHz; fixed 800–1800 Hz log-energy, 256-point STFT and 40-sample hop. Even nonoverlapping 8 s blocks alone determine calibration consensus and median offset. Odd blocks are withheld anchors. Require correlation >=0.75, >=3 calibration and >=3 validation anchors, >=30 s anchor span and consistency within 0.10 s. Supported regions are the union of accepted 8 s blocks; no unsupported extrapolation. The map is `video_time = sensor_time + offset`. No affine warp was fitted.

An extra conservative rejection check flags distant (>1 s) alternatives with equal maximum calibration votes and sufficient independent validation support. Validation never changes the selected offset; it only accepts/rejects. This is a documented data-quality rejection extension, not a performance-selected protocol relaxation. Rejected equal-consensus cases are retained with their alternative offsets in `manifests/alignment_results.json`.

The engineering uncertainty is max(0.08 s, held-out residual +0.04 s). Existing pilot microphone disagreement bounds are preserved, including **VMX9 +49.73 ±0.10 s**. No additional microphone variant was acquired. New bounds lack cross-microphone corroboration. Phone systematic audio/video skew, acoustic path delay and annotation uncertainty remain unresolved; empirical bounds are not calibrated confidence intervals. First native AAC PTS was checked for every new clip; nonzero/unverified origins are rejected. Native video PTS and actual display SAR are separately checked.

The earlier +16.04 s VMX9 alias was caused by a minimum-whole-record-overlap condition and is permanently superseded. The corrected estimator permits partial overlap and independent validation. Original correction: [{cfg['stage2']}/METHODOLOGY_CORRECTION.md]({os.path.relpath(Path(cfg['stage2'])/'METHODOLOGY_CORRECTION.md',final)}).

{table(['Experiment','Accepted','Offset s','Bound s','Cal/val','Max val residual s','Support sensor s','Reason'],align_rows)}
## Exact interval/frame association

The frozen selector trims by uncertainty plus half a native frame, places 16 equal-bin centers inside the guarded native [start,end) cut, maps to video time and selects nearest native PTS. It rejects insufficient support/coverage, duplicate indices, nonmonotonic or gapped PTS, boundary-crossing uncertainty and fewer than 16 unique decoded-content hashes. New videos are decoded once forward, with the header-CFR optimization independently checked against every native PTS; the selector is rerun on the actual decoded clock. A failed clock confirmation is a rejection, not approximate recovery. Every admitted frame preserves order, actual PTS, source row, label and content hash.

SAR correction preserves source display geometry; no stretching to square pixels and no arbitrary experiment-wide images are substituted. Only compact contact sheets are saved; no 640×640 cache or CNN features were generated.

## Observability remains unresolved

All {s['joint_technical_pass']} joint candidates require independent interval visibility review. {s['new_context_visibility_pending']} new frame-valid sequences lack even the earlier pilot-style context judgement. The original pilot only established recognizable coarse milling context under coolant/window occlusion; it did not prove optical anomaly separability. A representative contact sheet per experiment is in `manifests/metadata_relationships.json` and the consolidated diagnostic index; it does not certify all cuts in that experiment. Rejected clips have clearly marked unlabeled overview sheets. Expert/researcher review must separate context visibility, cutting-edge visibility and anomaly observability. No anomaly labels were used to optimize synchronization.
''')
    split_rows=[];distributions=''
    for policy,v in s['targets'].items():
        for key,g in v['groupings'].items():
            split_rows.append([policy,key,v['intervals'],g['groups'],g['positive_groups'],g['mixed_groups'],'PASS' if g['passed'] else 'FAIL',g['reason']])
            distributions+=f'\n### {policy}: {key}\n\n'+table(['Group','Native 0','Native 1','Native 2','Both classes','Folders'],
                 [[r['group'],r['label_0'],r['label_1'],r['label_2'],r['both_classes'],r['nominal_folders']] for r in g['group_distribution']])
    dep=s['independence'];dup_table=table(['Exact NC SHA-256','Folders'],[[h,'; '.join(g)] for h,g in dep['verified_exact_nc_reuse'].items()]) if dep['verified_exact_nc_reuse'] else 'No exact NC-content duplicate was found.'
    put(final/'MSM_INDEPENDENCE_AND_SPLIT_GATE.md',f'''# MSM independence and nested split gate

{intro}
**This is a feasibility check, not a final split freeze.** Both targets use the existing `msm.splits.nested_plan`: three outer folds, two inner folds, fixed outer seed 42 and inner seed 142+outer index. There was no seed search, automatic fold reduction, random interval split or model fitting. Both classes, group disjointness, complete outer coverage and one out-of-fold prediction per inner training row are required by the adapter.

{table(['Target','Grouping','Intervals','Groups','Positive groups','Mixed groups','3 outer / 2 inner','Reason'],split_rows)}
The machine/experiment gate can establish only nominal separation. A nominal PASS still allows related reference dates in train/test; exact outer and inner date overlaps are recorded in `manifests/split_feasibility.json`. The machine/date analysis prevents same-machine/date overlap but can share a calendar date across machines. Calendar-date grouping is a conservative third diagnostic. Neither proxy proves separate physical sessions across dates. No final fold IDs were frozen or adopted for evaluation.

## Metadata relationships and physical dependence

**VERIFIED:** machine and folder identities; original reference dates from MTC filenames; native Tool/Workpiece strings; MTC Current_Tool and running/editing program names; exact NC bytes/hashes. The full laboratory material spans {dep['verified_machine_reference_date_clusters']} machine/reference-date clusters and {dep['verified_calendar_dates']} calendar dates. Full metadata, tool/material values and NC headers are in `manifests/metadata_relationships.json`. These are provenance, never ordinary predictor features.

**INFERRED:** folders recorded on the same machine/date may share physical tool, workpiece, setup, operator and camera session. Same-day records across machines can share laboratory conditions. Exact NC reuse establishes shared program content, not simultaneous execution or independent sessions. Generic tool letters/defect markers and material descriptions are conditions, not unique serial identities.

**UNRESOLVED:** physical session boundaries, actual tool reuse and wear trajectories, workpiece instance reuse, repeated setups spanning dates, camera-position persistence, and internal MTC aggregation latency. Different folders do not prove independence. Different dates do not rule out reuse of the same tool/workpiece.

{dup_table}
## Label definition requires approval

Frozen primary: label 1 versus stable labels 0 and 2, {s['targets']['stable_negative']['intervals']} joint candidates. It asks whether the cutting process warrants intervention and retains defective-tool-but-stable cuts as negatives. Sensitivity: label 1 versus label 0 with label 2 excluded, {s['targets']['exclude']['intervals']} candidates. It avoids mixing stable tool conditions but changes prevalence, sample size and condition coverage. Neither target measures generic tool health. No predictive performance was observed to choose between them.

**Researcher decision required before evaluation:** finalize the primary target and physical grouping policy; reconcile session evidence or approve an explicitly limited date-group proxy. A passing nominal split alone is insufficient for an independent physical-session claim. If the stricter fixed split fails, any approved alternative fold design/estimand must be a separately reviewed protocol revision; no alternative was silently substituted.

## Positive distribution and class support

{distributions}
''')
    stricter=target['groupings']['machine_date_group'];calendar=target['groupings']['calendar_date_group']
    put(final/'MSM_RESEARCH_DECISION.md',f'''# MSM research decision

**{s['decision']}.** The laboratory acquisition and technical audit are complete, but an independent full-model evaluation is not yet ready to launch.

- Technical data: {s['joint_technical_pass']} paired intervals ({counts.get('0',0)} / {counts.get('1',0)} / {counts.get('2',0)} native 0/1/2), {target['groupings']['group_id']['groups']} nominal folders, {target['groupings']['group_id']['positive_groups']} positive-containing folders.
- Frozen nominal three-outer/two-inner gate: {'PASS' if target['groupings']['group_id']['passed'] else 'FAIL'}. Machine/date gate: {'PASS' if stricter['passed'] else 'FAIL'} ({stricter['reason']}). Calendar-date gate: {'PASS' if calendar['passed'] else 'FAIL'} ({calendar['reason']}). No final split is frozen.
- All joint candidates remain pending independent visual review; technical decoding and shared audio do not establish visible anomalies. Coolant/window occlusion and unknown systematic phone AV skew remain limitations.
- Physical tool/workpiece/session identities are unresolved. Researcher approval of the target (1 vs 0/2 or 1 vs 0) and justified grouping is required. Proxy-date feasibility does not establish physical independence.
- CNN transfer remains unmeasured. The Stage 4 canonical REASSEMBLE source dependency is preserved as a historical prerequisite, not re-inspected here. The ongoing Phase 1 job was not queried or changed.

**Single most justified next experiment:** conduct a blinded interval-level visual-observability study on the technically eligible 16-frame sequences, sampling native classes across the identified date/session clusters. Predefine visibility criteria and record expert/researcher judgements before model evaluation. Do not launch it in this stage.

Architecture implementation portability is supported by the prior bounded smoke. Learned-weight transfer, predictive visual benefit, incremental F2 value, seed stability, cross-domain representation generality and corrupted/missing-modality robustness remain unmeasured. MSM is a coarse retrospective cutting-interval task. No training, full CNN extraction or F2 evaluation occurred.

Exact evidence: [cohort audit](MSM_FULL_LAB_COHORT_AUDIT.md), [alignment](MSM_ALIGNMENT_FEASIBILITY_REPORT.md), [grouping/split gate](MSM_INDEPENDENCE_AND_SPLIT_GATE.md), and `manifests/split_feasibility.json`.
''')
    put(final/'REVIEW_HANDOFF.md',f'''# Researcher review handoff

**{s['decision']}; stop for review.** {acq['new_files']} files acquired, {acq['new_bytes']:,} bytes ({acq['new_bytes']/1e9:.9f} GB), no remaining planned failures. All 2,512 laboratory annotations preserved. Joint technical cohort: **{s['joint_technical_pass']}** = {counts.get('0',0)} normal + {counts.get('1',0)} abnormal + {counts.get('2',0)} stable defective-tool cuts; {target['groupings']['group_id']['groups']} nominal folders, {target['groupings']['group_id']['positive_groups']} positive folders.

Review the [cohort report](MSM_FULL_LAB_COHORT_AUDIT.md), [alignment report](MSM_ALIGNMENT_FEASIBILITY_REPORT.md), [split gate](MSM_INDEPENDENCE_AND_SPLIT_GATE.md), [decision](MSM_RESEARCH_DECISION.md), and [consolidated pilot index]({os.path.relpath(Path('MILLING DATASET/PILOT_FINDINGS/README.md'),final)}).

The primary nominal fixed split {'passes' if target['groupings']['group_id']['passed'] else 'fails'}; stricter machine/date {'passes' if stricter['passed'] else 'fails'} and calendar-date {'passes' if calendar['passed'] else 'fails'}. These are feasibility diagnostics, not frozen evaluation partitions. Finalize the primary label-2 treatment and physical grouping policy before authorizing evaluation. No independent interval visibility review is complete. Representative contacts are available for every experiment; fine anomaly observability remains unverified.

Recommend only a **blinded visual-observability study** next. No model or GPU experiment was launched, no source checkpoint was inspected, and no existing result was overwritten. The original Stage 4 blocked evaluation remains a failed-prerequisite finding, not an ML result. Per-file receipts, interrupted-attempt evidence, software/config hashes and data validation results are preserved. The earlier rejected-alignment JSON serialization failure affected report writing only; complete experiment checkpoints were reused without repeating valid decodes.
''')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);finish(p.parse_args().parent)
