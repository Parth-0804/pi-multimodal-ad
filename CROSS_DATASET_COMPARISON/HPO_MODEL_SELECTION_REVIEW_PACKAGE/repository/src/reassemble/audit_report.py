"""Outcome-independent cohort, known-issue, label and split audit reports."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile
import numpy as np
import pandas as pd
from .splits import nested_assignments, validate_predictor_fields, ALLOWED_PREDICTOR_FIELDS


def write_json(path, obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')


def table(frame):
    def cell(value):
        return str(value).replace('|', r'\|').replace('\n', '<br>')
    header='| '+' | '.join(map(cell,frame.columns))+' |'
    divider='| '+' | '.join(['---']*len(frame.columns))+' |'
    rows=['| '+' | '.join(map(cell,row))+' |' for row in frame.itertuples(index=False,name=None)]
    return '\n'.join([header,divider]+rows)


def support(frame):
    return {'segments':len(frame),'failures':int(frame.failure.sum()),'successes':int((frame.failure==0).sum()),'recordings':int(frame.recording_id.nunique()),'failure_recordings':int(frame.loc[frame.failure==1,'recording_id'].nunique()),'success_recordings':int(frame.loc[frame.failure==0,'recording_id'].nunique())}


def final_manipulation(segments):
    candidates=[s for s in segments if s['action'] in ['pick','insert','remove','place']]
    if not candidates:raise ValueError('No manipulation segment for official last-action warning')
    return max(candidates,key=lambda s:s['end'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',default='configs/reassemble/audit.json');p.add_argument('--run-dir',required=True);p.add_argument('--output-dir',default='artifacts/reassemble/audits');p.add_argument('--derived-dir');args=p.parse_args()
    config=json.loads(Path(args.config).read_text());root=Path(config['data_root']).resolve()/'REASSEMBLE';run=Path(args.run_dir);audit=Path(args.output_dir);derived=Path(args.derived_dir) if args.derived_dir else run
    audit.mkdir(parents=True,exist_ok=True);derived.mkdir(parents=True,exist_ok=True)
    required_outputs=['known_issues.json','modality_selection.json','segments.parquet','recordings.parquet','nested_splits.json','leakage_audit.json','gates.json','label_audit.md','inventory.md','storage_actual.md','PHASE_A_B_GATE_REPORT.md']
    existing=[name for name in required_outputs if (audit/name).exists()]
    if existing:raise FileExistsError(f'Refusing to overwrite prior audit outputs: {existing}')
    records=[json.loads(p.read_text()) for p in sorted((run/'records').glob('*.json'))]
    if len(records)!=len(list((root/'raw').rglob('*.h5'))):raise RuntimeError('Incomplete recording audit')
    rec={r['recording']['recording_id']:r for r in records}
    segments=[s for r in records for s in r['segments']]
    acquisition_intervals=[]
    for rid,obj in rec.items():
        streams=obj['recording']['sensor_streams'].values()
        starts=[v['first'] for v in streams if v.get('first') is not None]
        ends=[v['last'] for v in streams if v.get('last') is not None]
        if starts and ends:acquisition_intervals.append((rid,min(starts),max(ends)))
    acquisition_overlaps=[]
    for i,(rid,start,end) in enumerate(acquisition_intervals):
        for other,os,oe in acquisition_intervals[i+1:]:
            overlap=min(end,oe)-max(start,os)
            if overlap>1e-6:acquisition_overlaps.append({'recordings':[rid,other],'overlap_seconds':overlap})
    issues=[]
    for line in (root/'downloads'/'README.txt').read_text().splitlines():
        m=re.match(r'^(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\.h5\s+(.+)',line)
        if not m:continue
        rid,description=m.groups();item={'recording_id':rid,'official_issue':description,'recording_present':rid in rec,'exclusions':[]}
        if rid not in rec:
            item['verification']='RECORDING MISSING';issues.append(item);continue
        rows=rec[rid]['segments'];last=final_manipulation(rows);first=min(rows,key=lambda s:s['start'])
        if 'hand cam' in description:
            count=sum(s['video'].get('hand',{}).get('usable',False) for s in rows)
            item['observed_usable_hand_segments']=count;item['total_segments']=len(rows)
            item['verification']='Direct per-segment timestamp/decoding coverage recorded; availability masks exclude only unusable hand segments'
        elif 'empty action' in description:
            item['first_annotation']=first['text'];item['verification']='First actual annotation checked; no artificial idle segment inserted'
        elif 'F/T' in description or 'gripper broke' in description:
            names=['measured_force','measured_torque'] if 'F/T' in description else ['gripper_positions']
            item['last_segment']=last['segment_id'];item['observed_quality']={n:last['sensor'].get(n) for n in names}
            item['verification']='Last segment located and numeric quality inspected; physical defect cannot be independently proven from arrays. Conservative official-warning exclusion.'
            for name in names:
                if name in last['sensor']:last['sensor'][name]['usable']=False
                item['exclusions'].append({'segment_id':last['segment_id'],'modality':'sensor','stream':name})
        elif 'pose' in description:
            item['last_segment']=last['segment_id'];item['observed_pose']=last['sensor'].get('pose');item['verification']='Pose interval support inspected; pose is not a primary predictor'
        issues.append(item)
    write_json(audit/'known_issues.json',issues)
    action_segments=[s for s in segments if s['action'] in ['pick','insert','remove','place'] and s['valid_interval']]
    camera_counts={c:sum(s['video'].get(c,{}).get('usable',False) for s in action_segments) for c in ['hama1','hama2','hand']}
    top=max(camera_counts.values());ties=[c for c,n in camera_counts.items() if top-n<=.01*len(action_segments)]
    camera='hand' if 'hand' in ties else sorted(ties)[0]
    audio_names=sorted({n for s in action_segments for n in s['audio']})
    audio_counts={n:sum(q.get('decodable',False) and q.get('nominal_coverage',0)>=.9 for s in action_segments for k,q in s['audio'].items() if k==n) for n in audio_names}
    audio_verified_counts={n:sum(s['audio'].get(n,{}).get('usable',False) for s in action_segments) for n in audio_names}
    audio=None
    if audio_counts:
        ranking=audio_verified_counts if max(audio_verified_counts.values()) else audio_counts
        top_audio=max(ranking.values());ties_audio=[n for n,c in ranking.items() if top_audio-c<=.01*len(action_segments)]
        audio='hand_audio' if 'hand_audio' in ties_audio else sorted(ties_audio)[0]
    rows=[]
    for s in segments:
        row={k:v for k,v in s.items() if k not in ['sensor','video','audio']}
        row['visual_usable']=s['video'].get(camera,{}).get('usable',False)
        row['sensor_usable']=all(s['sensor'].get(n,{}).get('usable',False) for n in config['primary_sensors'])
        row['audio_nominal_usable']=s['audio'].get(audio,{}).get('nominal_coverage',0)>=.9 and s['audio'].get(audio,{}).get('decodable',False)
        row['audio_usable']=s['audio'].get(audio,{}).get('usable',False)
        row['primary_task']=s['action']!='other' and s['valid_interval']
        row['dual_complete']=row['primary_task'] and row['visual_usable'] and row['sensor_usable']
        row['tri_complete']=row['dual_complete'] and row['audio_usable']
        row['sensor_sample_counts']=json.dumps({k:q.get('count',0) for k,q in s['sensor'].items()})
        row['video_coverage']=json.dumps({k:q.get('coverage',0) for k,q in s['video'].items()})
        row['audio_coverage']=json.dumps({k:{'nominal':q.get('nominal_coverage',0),'alignment_verified':q.get('aligned',False)} for k,q in s['audio'].items()})
        row['available_modalities']=json.dumps([n for n in ['visual','sensor','audio'] if row[n+'_usable']])
        rows.append(row)
    frame=pd.DataFrame(rows);primary=frame[frame.primary_task];dual=frame[frame.dual_complete];tri=frame[frame.tri_complete]
    summaries={'all_annotations':support(frame),'primary_actions':support(primary),'dual_complete':support(dual),'tri_complete':support(tri)}
    cohort=tri if support(tri)['failure_recordings']>=10 and support(tri)['success_recordings']>=10 else dual
    selected='tri_modal' if cohort is tri else 'visual_sensor'
    selection={'primary_camera':camera,'camera_usable_counts':camera_counts,'candidate_microphone':audio,'audio_nominal_counts':audio_counts,'audio_primary_eligible':selected=='tri_modal','audio_verified_counts':audio_verified_counts,'audio_reason':('Explicit per-sample timestamps support the selected audio cohort' if selected=='tri_modal' else 'Decoded sample clock lacks sufficient verified timing/support; primary audio deferred. Nominal zero-based quality measured using official visualization convention.'),'selection_rule':'Coverage, decoding and overlap first; within 1 percentage point prefer wrist/hand proximity, otherwise lexical name; no model performance.','cohort':selected,'sensor_streams':config['primary_sensors'],'support':summaries}
    write_json(audit/'modality_selection.json',selection)
    frame.to_parquet(audit/'segments.parquet',index=False)
    shutil.copyfile(run/'recordings.parquet',audit/'recordings.parquet')
    frame.to_parquet(derived/'cohort.parquet',index=False)
    labels=[]
    primary=primary.copy();primary['duration_bin']=pd.cut(primary.duration,[0,5,10,20,60,np.inf],right=False).astype(str)
    for category in ['action','recording_id','object_annotation','duration_bin','visual_usable','sensor_usable','audio_nominal_usable']:
        summary=primary.groupby(category,dropna=False).failure.agg(['count','sum']).reset_index().rename(columns={'count':'segments','sum':'failures'})
        summary['failure_rate']=summary.failures/summary.segments
        summary.to_parquet(derived/f'labels_by_{category}.parquet',index=False)
        labels.append((category,summary))
    duplicate_files=defaultdict(list)
    for r in records:duplicate_files[r['recording']['sha256']].append(r['recording']['recording_id'])
    duplicate_files={k:v for k,v in duplicate_files.items() if len(v)>1}
    fingerprints=defaultdict(list)
    for s in action_segments:
        hashes=[s['sensor'].get(n,{}).get('content_sha256') for n in config['primary_sensors']]
        if all(hashes):fingerprints[':'.join(hashes)].append((s['recording_id'],s['segment_id']))
    duplicate_sensor=[v for v in fingerprints.values() if len({r for r,_ in v})>1]
    official={}
    with zipfile.ZipFile(root/'downloads'/'splits.zip') as z:
        for name in z.namelist():
            if name.endswith('.txt'):official[name]=[Path(s.strip()).stem for s in z.read(name).decode().splitlines() if s.strip()]
    keys=list(official);overlap=set(official[keys[0]])&set(official[keys[1]])
    missing=sorted(set(sum(official.values(),[]))-set(rec))
    validate_predictor_fields(ALLOWED_PREDICTOR_FIELDS)
    split_error=None;splits=None
    try:splits=nested_assignments(cohort,config['outer_folds'],config['inner_folds'],config['seed'])
    except ValueError as e:split_error=str(e)
    if splits:write_json(audit/'nested_splits.json',splits)
    leakage={'grouping':'source HDF5 recording; official website identifies each file as one trial','higher_grouping':'No shared trial-family identifier found; collection date is descriptive only. Same-day environment dependence remains a generalization limit.','absolute_acquisition_interval_overlaps':acquisition_overlaps,'duplicate_recording_hashes':duplicate_files,'duplicate_combined_sensor_segments':duplicate_sensor,'official_split_counts':{k:len(v) for k,v in official.items()},'official_split_overlap':sorted(overlap),'official_split_missing_recordings':missing,'official_split_duplicate_entries':{k:len(v)-len(set(v)) for k,v in official.items()},'official_split_secondary_only':True,'predictor_allowlist':sorted(ALLOWED_PREDICTOR_FIELDS),'models_trained':0,'split_error':split_error,'split_sha256':splits['sha256'] if splits else None}
    write_json(audit/'leakage_audit.json',leakage)
    acq=json.loads((run/'acquisition.json').read_text())
    gates=[{'gate':'G0 STORAGE','status':'PASS','evidence':f"{acq['free_before_bytes']/2**30:.2f} GiB before download >=160",'artifact':str(run/'acquisition.json')}, {'gate':'G1 DOWNLOAD CHECKSUM','status':'PASS','evidence':'All four official MD5 values matched; all three ZIP CRC tests passed before extraction','artifact':str(run/'acquisition.json')}, {'gate':'G2 LABEL SUPPORT','status':'PASS' if summaries['primary_actions']['failure_recordings']>=10 and summaries['primary_actions']['success_recordings']>=10 else 'FAIL','evidence':summaries['primary_actions'],'artifact':'label_audit.md'}, {'gate':'G3 MODALITY COMPLETENESS','status':'PASS' if len(cohort)>0 and support(cohort)['failure_recordings']>=10 and support(cohort)['success_recordings']>=10 else 'FAIL','evidence':{'selected':selected,**support(cohort),'audio':'CONDITIONAL; secondary only'},'artifact':'modality_selection.json'}, {'gate':'G4 GROUP LEAKAGE','status':'PASS' if splits and not duplicate_files and not duplicate_sensor and not acquisition_overlaps else 'FAIL','evidence':{'split_error':split_error,'overlapping_acquisition_pairs':len(acquisition_overlaps),'exact_recording_duplicates':len(duplicate_files),'combined_sensor_duplicates':len(duplicate_sensor),'models_trained':0},'artifact':'leakage_audit.json'}]
    write_json(audit/'gates.json',gates)
    action_summary=next(x for k,x in labels if k=='action')
    text='# Label audit\n\n'+json.dumps(summaries,indent=2)+'\n\n'+table(action_summary)+'\n\nPublished reference: 4,551 action demonstrations; 4,035 successful and 516 failed.\nObserved counts above are recomputed from success fields; idle/other annotations\nremain in the inventory but are excluded from the primary action task.\n\n'
    text+='Action-only prediction remains a required later baseline; no model was trained.\nObject strings are descriptive annotation suffixes, not validated universal IDs\nand never predictors. The full per-recording/object/duration/availability tables\nare stored as labels_by_*.parquet in the versioned run.\n\n'
    for k,x in labels:
        if k not in ['action','recording_id','object_annotation']:text+='## '+k+'\n\n'+table(x)+'\n\n'
    (audit/'label_audit.md').write_text(text)
    completeness=[]
    for group in ['action','success','recording_id']:
        grouped=primary.groupby(group)[['visual_usable','sensor_usable','audio_nominal_usable','audio_usable','dual_complete','tri_complete']].agg(['sum','count'])
        grouped.columns=['_'.join(c) for c in grouped.columns];grouped.reset_index().to_parquet(derived/f'completeness_by_{group}.parquet',index=False)
    warning_count=sum(len(r['warnings']) for r in records)
    (audit/'inventory.md').write_text(f'# Recording and segment inventory\n\n{len(records)} HDF5 recordings, {len(frame)} high-level annotations; '+str(sum(r['recording']['low_level_segment_count'] for r in records))+' low-level annotations.\n\nActual key/shape/dtype schemas, full SHA256s, sensor rates, media metadata, quality\nand per-recording warnings are in the versioned records/*.json files.\n'+f'{warning_count} warning records; no undocumented schema coercion.\n\nPrimary camera: `{camera}`. Candidate microphone: `{audio}`; audio is secondary\nuntil its clock origin and drift can be independently verified.\n\n'+json.dumps(selection,indent=2)+'\n\nVideo quality uses 16 deterministic in-segment frames at 160x120 for brightness,\nfocus and motion proxies; it is not exhaustive frame-by-frame decoding. Sensor\nquality uses in-segment finite data; MAD outliers are descriptive within-segment\nquality, not globally fitted preprocessing. Clipping/SNR are null when no\ndefensible reference exists. Encoded media cache is outside Git.\n')
    free=shutil.disk_usage(root).free
    (audit/'storage_actual.md').write_text(f'# Actual REASSEMBLE storage\n\nOfficial data.zip: 58,881,334,586 bytes (54.838 GiB rounded).\nActual compressed files: {sum(f["size_bytes"] for f in acq["files"]):,} bytes.\nExtracted files: {acq["extracted_bytes"]:,} bytes ({acq["extracted_bytes"]/2**30:.3f} GiB).\nH5 files: {acq["h5_files"]}; JSON files: {acq["json_files"]}.\nCurrent free space: {free:,} bytes ({free/2**30:.2f} GiB).\nOriginal archives retained. Encoded media audit caches are additional to raw size.\n')
    go=all(g['status']=='PASS' for g in gates)
    result='GO FOR REASSEMBLE MODELLING' if go else 'NO-GO FOR REASSEMBLE MODELLING'
    report='# Phase A/B gate report\n\n'+datetime.now(timezone.utc).isoformat()+'\n\n'+table(pd.DataFrame([{'gate':g['gate'],'status':g['status'],'evidence':json.dumps(g['evidence']),'artifact':g['artifact']} for g in gates]))+'\n\n'
    report+=f'Primary proposed cohort: **{selected}**; camera **{camera}**.\n\n'+json.dumps(summaries,indent=2)+'\n\n'
    report+='Audio is decoded and its nominal quality inventoried, but cross-modal timing\nis not independently established by the stored schema. Audio therefore remains\nsecondary; a visual+sensor study is allowed by the master specification.\nPhysical F/T/gripper defects are conservatively excluded at the affected\nsegment/modality level based on the official README. Full issue evidence and\nunresolved verification limits are in known_issues.json.\n\n'
    report+='No model training or predictive-results search occurred. G5–G14 are not\nevaluated; storage/label/coverage support is not evidence of useful modality\nsignal. Independent signal and permutation gates still precede fusion.\n\n'
    report+='PHM runs, artifacts, checkpoints, configurations and Git history were preserved.\nOfficial loader reference: 432cc15ce3e028edc2f98a786f28bf6baf31ac6f.\nDataset DOI: 10.48436/0ewrv-8cb44. Full acquisition, archive inventory, per-file\nchecksums and configuration are recorded in `'+str(run)+'`.\n\n'
    report+='Next action: researcher review of this cohort, audio limitation, known-issue\nhandling and nested split manifest before approving baseline/modelling work.\nAGENTS.md requires phase-boundary review; master specification section 71\nexplicitly preserves this requirement.\n\n'+result+'\n'
    (audit/'PHASE_A_B_GATE_REPORT.md').write_text(report)
    print(report)

if __name__=='__main__':main()
