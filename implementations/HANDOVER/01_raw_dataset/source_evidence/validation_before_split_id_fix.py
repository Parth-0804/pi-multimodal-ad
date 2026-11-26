"""Trial-level full Handover audit; no model/score-dependent admission rules."""
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import cv2
import numpy as np
import pandas as pd

sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
from stage2.audit_sensors import new_accumulator,accumulate,finalize
from msm.splits import grouped_plan
from external_eval.io import write_json,csv_rows,sha,utc

ROOT=Path('HANDOVER');RAW=ROOT/'01_raw_dataset/official_dataset'
CHANNELS=['force_x','force_y','force_z','torque_x','torque_y','torque_z']
STATS=['mean','std','rms','min','max','peak_to_peak']


def trial(folder,split,label_path,label,classes):
    checkpoint=ROOT/'02_labels_and_alignment/trial_checkpoints'/(folder.name+'.json')
    if checkpoint.exists():return json.loads(checkpoint.read_text())
    source=json.loads((folder/'task_info.json').read_text());native=int(label['outcome'])
    if source['task']!=label['task'] or source['robot']!=label['robot'] or native not in (0,1,2,3):raise ValueError('Unverifiable trial label identity')
    outcome_names=classes['human to robot handover outcomes' if source['task']=='human to robot handover' else 'robot to human handover outcomes']
    files=[folder/name for name in ['task_info.json','head_cam.mp4','head_cam_ts.npy','wrench.npy','wrench_ts.npy','wrench_resampled.npy']]+[label_path]
    missing=[str(p) for p in files if not p.exists()]
    identity=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files if p.exists()]
    reasons=[]
    if missing:reasons.append('missing_required_file')
    record={'sample_id':folder.name,'interval_id':folder.name,'group_id':folder.name,
        'group_id_role':'trial identity for traceability only; not a verified participant grouping',
        'official_split':split,'participant_id':'','participant_identity_status':'not supplied by native task/label metadata',
        'native_label':native,'native_label_name':outcome_names[native],'target':int(native!=0),
        'robot':source['robot'],'task':source['task'],'trial_folder':str(folder),'label_file':str(label_path),'label_sha256':sha(label_path),
        'video_file':str(folder/'head_cam.mp4'),'start_s':None,'end_s':None,'duration_s':None,
        'frame_indices_json':'[]','video_pts_s_json':'[]','mapped_sensor_pts_s_json':'[]',
        'sar_num':1,'sar_den':1,'mtc_rows_inside_cut':0,'sensor_dimensions':36,
        'sensor_file':str(folder/'wrench_resampled.npy'),'exclusion_reasons':'','eligible':False}
    frames=[];feature=None;clock={}
    if not reasons:
        t=np.load(folder/'head_cam_ts.npy',allow_pickle=False);wt=np.load(folder/'wrench_ts.npy',allow_pickle=False)
        raw=np.load(folder/'wrench.npy',allow_pickle=False);aligned=np.load(folder/'wrench_resampled.npy',allow_pickle=False)
        if t.ndim!=1 or len(t)<16 or not np.isfinite(t).all() or np.any(np.diff(t)<=0):reasons.append('invalid_camera_source_clock')
        if aligned.shape!=(len(t),6) or not np.isfinite(aligned).all():reasons.append('invalid_common_wrench_shape_or_values')
        if wt.ndim!=1 or raw.shape!=(len(wt),6) or not np.isfinite(wt).all() or not np.isfinite(raw).all() or np.any(np.diff(wt)<0):
            reasons.append('invalid_raw_wrench_clock_or_values')
        if not reasons:
            # This is exactly the author's public resample.py rule, including ties.
            nearest=np.array([np.argmin(abs(wt-v)) for v in t]);gap=np.abs(wt[nearest]-t)
            diff=float(np.max(abs(raw[nearest]-aligned)))
            if diff!=0:reasons.append('provided_resampling_not_exact_nearest_raw')
            if float(gap.max())>.1:reasons.append('wrench_nearest_time_gap_exceeds_0.1s')
            clock={'max_nearest_wrench_gap_s':float(gap.max()),'provided_vs_nearest_max_abs_difference':diff,
                'source_clock_span':[float(t[0]),float(t[-1])],'raw_wrench_rows':len(wt),'aligned_rows':len(t)}
            targets=t[0]+(np.arange(16)+.5)/16*(t[-1]-t[0]);indices=np.searchsorted(t,targets).clip(0,len(t)-1)
            prev=np.maximum(indices-1,0);indices=np.where(abs(t[prev]-targets)<abs(t[indices]-targets),prev,indices)
            if len(set(indices))!=16:reasons.append('fewer_than_16_distinct_native_frames')
            cap=cv2.VideoCapture(str(folder/'head_cam.mp4'),cv2.CAP_FFMPEG,[cv2.CAP_PROP_N_THREADS,1])
            header=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));sar=(int(cap.get(cv2.CAP_PROP_SAR_NUM)),int(cap.get(cv2.CAP_PROP_SAR_DEN)))
            if not cap.isOpened() or header!=len(t) or min(sar)<1:reasons.append('video_source_clock_count_or_geometry_mismatch')
            wanted=set(map(int,indices));pts=[];hashes={};i=0;native_times={}
            while cap.grab():
                current=cap.get(cv2.CAP_PROP_POS_MSEC)/1000;pts.append(current)
                if i in wanted:
                    ok,image=cap.retrieve()
                    if not ok:reasons.append('selected_native_frame_decode_failed');break
                    hashes[i]=hashlib.sha256(image.tobytes()).hexdigest();native_times[i]=current
                i+=1
            cap.release()
            if i!=len(t) or np.any(np.diff(pts)<=0):reasons.append('decoded_video_pts_invalid_or_count_mismatch')
            if len(hashes)!=16 or len(set(hashes.values()))!=16:reasons.append('repeated_or_missing_selected_frame_content')
            end=float(t[-1]+np.median(np.diff(t)));bound=max(float(gap.max()),float(np.median(np.diff(t))/2))
            if np.any(t[indices]-bound<t[0]) or np.any(t[indices]+bound>=end):reasons.append('frame_timing_guard_crosses_observation_horizon')
            record.update(start_s=float(t[0]),end_s=end,duration_s=end-float(t[0]),mtc_rows_inside_cut=len(t),
                frame_indices_json=json.dumps(indices.tolist()),video_pts_s_json=json.dumps([native_times.get(int(j)) for j in indices]),
                mapped_sensor_pts_s_json=json.dumps(t[indices].tolist()),sar_num=sar[0],sar_den=sar[1],
                timing_bound_s=bound,clock_mapping='native frame index -> supplied head_cam_ts -> supplied wrench_resampled row',
                video_sha256=next(x['sha256'] for x in identity if x['path']==str(folder/'head_cam.mp4')))
            if not reasons:
                values=[]
                for column in aligned.T:
                    state=new_accumulator();accumulate(state,column);s=finalize(state);values.extend(s[name] for name in STATS)
                feature={'interval_id':folder.name,**dict(zip([f'{c}__{s}' for c in CHANNELS for s in STATS],np.asarray(values,np.float32).tolist()))}
                for order,j in enumerate(indices):frames.append({'sample_id':folder.name,'interval_id':folder.name,'group_id':folder.name,
                    'frame_order':order,'native_frame_index':int(j),'video_pts_s':native_times[int(j)],
                    'mapped_sensor_time_s':float(t[j]),'decoded_frame_sha256':hashes[int(j)],'native_label':native})
    record['eligible']=not reasons;record['exclusion_reasons']=';'.join(sorted(set(reasons)))
    result={'record':record,'frames':frames,'features':feature,'clock':clock,'inputs':identity,'metadata_keys':sorted(set(source)|set(label)),
        'participant_mapping':{k:v for k,v in {**source,**label}.items() if any(a in k.lower() for a in ['person','participant','subject'])}}
    write_json(checkpoint,result);print(split,folder.name,'eligible',record['eligible'],record['exclusion_reasons'],flush=True)
    return result


def main():
    complete=ROOT/'01_raw_dataset/source_evidence/full_acquisition.json'
    if not complete.exists():raise ValueError('Official full acquisition has not completed')
    cv2.setNumThreads(1);classes=json.loads((RAW/'archives/class_names.json').read_text())
    tasks=[];label_inventory=[];seen=set()
    for split,count in [('train',337),('validation',101),('test',151)]:
        labels={p.stem:(p,json.loads(p.read_text())) for p in (RAW/'labels'/split).rglob('trial*.json')}
        folders={p.parent.name:p.parent for p in (RAW/'data'/split).rglob('task_info.json')}
        if len(labels)!=count or set(labels)!=set(folders):raise ValueError('Official trial/label/split identity mismatch')
        if seen&set(labels):raise ValueError('Actual trial leakage across official partitions')
        seen|=set(labels)
        for name,(p,label) in sorted(labels.items()):
            label_inventory.append({'sample_id':name,'official_split':split,'native_outcome':label['outcome'],
                'task':label['task'],'robot':label['robot'],'path':str(p),'sha256':sha(p)})
            tasks.append((folders[name],split,p,label,classes))
    assert len(seen)==589
    results=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(trial,*t) for t in tasks]
        for f in as_completed(futures):results.append(f.result())
    results.sort(key=lambda x:x['record']['sample_id'])
    frame=pd.DataFrame([x['record'] for x in results]);eligible=frame[frame.eligible].reset_index(drop=True)
    # Identical source video in two partitions is a genuine held-out leakage blocker.
    repeated=frame.groupby('video_sha256').official_split.nunique()
    if (repeated>1).any():raise ValueError('Actual duplicate video leakage across official splits')
    csv_rows(ROOT/'02_labels_and_alignment/original_label_inventory.csv',label_inventory)
    frame.to_csv(ROOT/'02_labels_and_alignment/validated_labels.csv',index=False)
    frame[~frame.eligible].to_csv(ROOT/'02_labels_and_alignment/excluded_examples.csv',index=False)
    eligible.to_csv(ROOT/'03_processed_model_inputs/final_sample_manifest.csv',index=False)
    csv_rows(ROOT/'02_labels_and_alignment/alignment_manifest.csv',[r for x in results for r in x['frames']])
    csv_rows(ROOT/'03_processed_model_inputs/sensor_features/interval_statistics.csv',[x['features'] for x in results if x['features'] is not None])
    mapping_present=all(bool(x['participant_mapping']) for x in results)
    inventory=ROOT/'01_raw_dataset/source_evidence'
    metadata_candidates=[]
    for p in inventory.glob('*_set.tar.gz.members.json'):
        metadata_candidates.extend(r['member'] for r in json.loads(p.read_text()) if any(k in r['member'].lower() for k in ['participant','subject','person']))
    gate={'passed_input_contract':True,'raw_trials':589,'native_label_files':589,'usable_examples':len(eligible),
        'native_outcomes':{str(k):int(v) for k,v in frame.native_label.value_counts().items()},
        'eligible_binary_counts':{str(k):int(v) for k,v in eligible.target.value_counts().items()},
        'official_partitions':{s:{'native_trials':int((frame.official_split==s).sum()),'eligible_trials':int((eligible.official_split==s).sum()),
            'positive':int(eligible.loc[eligible.official_split==s].target.sum())} for s in ['train','validation','test']},
        'robots':sorted(frame.robot.unique()),'participants_reported_by_datasheet':17,'participant_mapping_present':mapping_present,
        'participant_independence':'Official subject-based partition claim verified in datasheet; identity-level disjointness not independently testable without participant IDs.',
        'participant_named_members':metadata_candidates,'native_metadata_keys':sorted(set(k for x in results for k in x['metadata_keys'])),
        'participant_oof_passed':False,'participant_oof_blocker':'No explicit participant-to-trial mapping in official native metadata or author code; no trial-number/face grouping is invented.',
        'allowed_models':['prevalence','sensor_logistic','sensor_histgradient','visual','averaging'],
        'blocked_models':{name:'Participant-disjoint OOF training probabilities cannot be verified without participant IDs.' for name in ['F2','F2_aug','QG_clean','QG_aug']},
        'exclusion_counts':frame.loc[~frame.eligible,'exclusion_reasons'].value_counts().to_dict(),
        'sensor_channels':CHANNELS,'sensor_statistics':STATS,'sensor_width':36,
        'clock_validation':'Every admitted provided wrench_resampled array is exactly reproduced using closest raw wrench timestamp, as in author resample.py; max nearest-source gap <=0.1s.',
        'video_policy':'16 equal source-clock bin centers over complete trial; no human/robot action or outcome annotations used for sampling',
        'no_test_label_model_selection':True}
    for split in ['train','validation','test']:
        if set(eligible.loc[eligible.official_split==split].target)!={0,1}:raise ValueError('Official split lacks both classes after technical admission')
    write_json(ROOT/'02_labels_and_alignment/validation_gate.json',gate)
    write_json(ROOT/'02_labels_and_alignment/input_manifest.json',[r for x in results for r in x['inputs']])
    settings=json.loads(Path('CROSS_DATASET_COMPARISON/configs/frozen_core.json').read_text())
    config={**settings,'dataset':'HANDOVER','dataset_doi':'10.5281/zenodo.10708763','pinned_record':10708763,
        'primary_target':'0 success, 1 any native nonzero failure outcome','sensor_channels':CHANNELS,'sensor_statistics':STATS,
        'sample_manifest_sha256':sha(ROOT/'03_processed_model_inputs/final_sample_manifest.csv'),
        'sensor_contract':'36 channel-major statistics from exact source-verified official 6D aligned wrench; robot-specific gripper joints are omitted',
        'alignment_gate':'exact provided nearest-source resampling, max timing gap <=.1s, ordered native video/frame timestamps and content hashes',
        'official_training_only':True,'validation_use':'predeclared fixed settings; report separately, no selection or refit using validation',
        'participant_oof_gate':gate['participant_oof_blocker'],'OOF_fusion_status':'BLOCKED; other official-split models continue',
        'independent_inference_limitation':'Participant-level CIs unavailable; reported trial-bootstrap CIs, if any, are explicitly exploratory. Primary model differences remain paired point estimates.'}
    write_json(ROOT/'04_experiment_protocol/experiment_config.json',config)
    plan={'official':{'target':'primary','grouping':'official_partitions','sample_ids':eligible.sample_id.tolist(),
        'plan':[{'train':eligible.index[eligible.official_split=='train'].tolist(),'validation':eligible.index[eligible.official_split=='validation'].tolist(),
            'test':eligible.index[eligible.official_split=='test'].tolist(),'inner':None}],
        'participant_group_ids_available':False,'no_trial_level_oof_substitution':True}}
    write_json(ROOT/'03_processed_model_inputs/split_manifests/frozen_splits.json',plan)
    print(json.dumps(gate,indent=2),flush=True)


if __name__=='__main__':main()
