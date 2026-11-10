"""CPU-only, restartable laboratory feasibility audit; no model fitting.

Reuses Stage 2's corrected label-blind mapping and frame selector and Stage 3's
fixed statistics/split adapters. New video clips are decoded once forward. Header
CFR times are only a preselection optimization: every native PTS is subsequently
checked and the selector rerun on the actual complete decoded clock.
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
SOURCE=Path(__file__).parent
sys.path[:0]=[str(SOURCE),str(SOURCE/'stage2'),str(SOURCE.parent/'.tools')]
import cv2
import imageio_ffmpeg
import numpy as np
import pandas as pd
import soundfile as sf
from PIL import Image,ImageDraw
from scipy import signal
from align_audio import estimate_mapping
from calibration_consensus import correlations
from frame_contract import select_frames
from msm.data import interval_statistics, FEATURE_NAMES, COMMON_MTC, binary_target
from msm.splits import nested_plan
from probe_media import envelope,corrected_frame
from prepare_full_lab import write,sha256

cv2.setNumThreads(1)
PLOT_LOCK=threading.Lock()


def dump_csv(path,rows):
    if not rows: return
    with path.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def source_identity(label_path,source_row,native,start,end):
    """Fail closed on altered labels, row numbering or units of prediction."""
    actual=pd.read_csv(label_path).iloc[int(source_row)-2]
    if int(actual.label)!=native or not np.allclose([actual.start,actual.end],[start,end],rtol=0,atol=1e-10):
        raise ValueError('Native annotation identity mismatch')


def ambiguity_gate(vf,rf,mapping,protocol):
    """Conservative additional rejection of equally supported distant aliases.

    Calibration chooses/ranks candidates; validation never changes the estimate.
    An equally voted alias >1s away with independent held-out support is ambiguous.
    """
    if not mapping['accepted']: return {'checked':False,'reason':'base_mapping_rejected'}
    lags,scores=correlations(vf[2:3],rf[2:3],round(protocol['local_window_s']*100),protocol['local_min_correlation'])
    best=int(np.argmax(scores));best_votes=int(np.floor(scores[best]))
    other=scores.copy();other[np.abs(lags-lags[best])<=100]=-np.inf
    rivals=[]
    # No label/boundary inputs. Enumerate all equally voted separated calibration peaks.
    while np.isfinite(other.max()) and int(np.floor(other.max()))>=best_votes:
        idx=int(np.argmax(other));lag=int(lags[idx]);other[np.abs(lags-lag)<=100]=-np.inf
        valid=[]
        for a in range(800,rf.shape[1]-800+1,1600):
            if a+lag>=0 and a+800+lag<=vf.shape[1]:
                x,y=vf[2,a+lag:a+800+lag],rf[2,a:a+800]
                r=float(np.corrcoef(x,y)[0,1]) if x.std() and y.std() else 0
                if r>=protocol['local_min_correlation']:valid.append(a/100+4)
        rival={'offset_s':lag/100,'calibration_votes':int(np.floor(scores[idx])),
               'validation_anchors':len(valid),'validation_span_s':max(valid)-min(valid) if valid else 0}
        rivals.append(rival)
    ambiguous=any(r['validation_anchors']>=protocol['min_validation_anchors'] and
                  r['validation_span_s']>=protocol['min_anchor_span_s'] for r in rivals)
    return {'checked':True,'best_calibration_votes':best_votes,'equally_voted_distant_aliases':rivals,'ambiguous':ambiguous}


def align(video,wav,protocol,out):
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    header=subprocess.run([ffmpeg,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
    (out/'media_header.txt').write_text(header)
    pts_probe=[ffmpeg,'-nostdin','-hide_banner','-copyts','-threads','1','-i',str(video),
               '-map','0:a:0','-af','ashowinfo','-frames:a','1','-f','null','-']
    probe=subprocess.run(pts_probe,capture_output=True,text=True)
    first=re.search(r'ashowinfo.*?n:0\s+pts:\S+\s+pts_time:([-+\d.e]+)',probe.stderr)
    first_audio_pts=float(first.group(1)) if first else None
    command=[ffmpeg,'-nostdin','-v','error','-threads','1','-i',str(video),'-map','0:a:0','-vn','-ac','1','-ar','4000','-f','f32le','pipe:1']
    decoded=subprocess.run(command,capture_output=True,check=True)
    va=np.frombuffer(decoded.stdout,dtype='<f4')
    reference,fs=sf.read(wav,dtype='float32')
    if reference.ndim>1:reference=reference.mean(axis=1)
    rf=envelope(signal.resample_poly(reference,4000,fs));vf=envelope(va)
    mapping=estimate_mapping(vf,rf,protocol)
    mapping['reference']='audio_s2'
    mapping['ambiguity_audit']=ambiguity_gate(vf,rf,mapping,protocol)
    if mapping['ambiguity_audit'].get('ambiguous'):
        mapping['accepted']=False;mapping['reason']='ambiguous_equal_calibration_consensus'
    if first_audio_pts is None or abs(first_audio_pts)>1e-6:
        mapping['accepted']=False;mapping['reason']='unverified_or_nonzero_aac_time_origin'
    info=sf.info(wav)
    mapping['media_audio']={'reference_sample_rate':fs,'reference_channels':info.channels,
        'reference_duration_s':info.duration,'video_decoded_audio_duration_s':len(va)/4000,
        'reference_clipped_fraction':float(np.mean(np.abs(reference)>=32767/32768)),
        'reference_finite':bool(np.isfinite(reference).all()),'audio_decode_argv':command,
        'first_native_aac_pts_s':first_audio_pts,'audio_pts_probe_argv':pts_probe,
        'systematic_phone_av_skew':'unverified; engineering uncertainty is not a confidence interval',
        'cross_microphone_check':'not acquired for new cohort; fixed S2 only'}
    # Small acoustic diagnostic; no raw waveform or full decoded frame cache.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with PLOT_LOCK:
        fig,axs=plt.subplots(2,1,figsize=(10,5),layout='constrained')
        axs[0].plot(np.arange(rf.shape[1])/100,rf[2],lw=.5,label='S2')
        axs[0].plot(np.arange(vf.shape[1])/100-mapping.get('offset_s',0),vf[2],lw=.4,alpha=.65,label='AAC mapped')
        axs[0].legend();axs[0].set(ylabel='800–1800Hz log energy',xlabel='Sensor time (s)')
        for role,marker in [('calibration','o'),('validation','s')]:
            anchors=[a for a in mapping['anchors'] if a['role']==role and a.get('video_minus_sensor_s') is not None]
            axs[1].scatter([a['center_sensor_s'] for a in anchors],[a['video_minus_sensor_s'] for a in anchors],
                           marker=marker,s=12,c=['green' if a.get('accepted') else 'red' for a in anchors],label=role)
        axs[1].legend();axs[1].set(ylabel='Video − sensor (s)',xlabel='Sensor time (s)')
        fig.suptitle(f'{video.parent}: alignment accepted={mapping["accepted"]}')
        fig.savefig(out/'alignment.png',dpi=90);plt.close(fig)
    return mapping


def sensor_gate(table,start,end):
    missing=[c for c in ['time',*COMMON_MTC] if c not in table]
    if missing:return False,None,{'reasons':['missing_mtc_channels:'+','.join(missing)],'rows':0,'max_gap_s':None}
    t=table.time.to_numpy(float)
    if not np.isfinite(t).all() or np.any(np.diff(t)<=0):
        return False,None,{'reasons':['invalid_mtc_clock'],'rows':0,'max_gap_s':None}
    a,b=np.searchsorted(t,[start,end],side='left');inside=t[a:b]
    gap=float(np.max(np.diff(np.r_[start,inside,end])))
    reasons=[]
    if b-a<5:reasons.append('insufficient_mtc_rows')
    if gap>.5+1e-12:reasons.append('mtc_time_gap_exceeds_0.5s')
    if not np.isfinite(table[COMMON_MTC].iloc[a:b].to_numpy(float)).all():reasons.append('nonfinite_mtc_measurements')
    gate={'rows':int(b-a),'max_gap_s':gap,'reasons':reasons}
    if reasons:return False,None,gate
    values,verified=interval_statistics(table,start,end)
    assert len(values)==90 and np.isfinite(values).all()
    return True,values,gate


def distinct_content(record,hashes):
    if not record['accepted']:return record
    selected=[hashes.get(j) for j in record['indices']]
    record['unique_decoded_content']=len(set(x for x in selected if x is not None))
    if None in selected or len(set(selected))!=16:
        record['accepted']=False;record['reasons'].append('repeated_or_missing_decoded_frame_content')
    return record


def decode_once(video,labels,mapping,out):
    cap=cv2.VideoCapture(str(video),cv2.CAP_FFMPEG,[cv2.CAP_PROP_N_THREADS,1])
    if not cap.isOpened():raise ValueError('Cannot decode official video')
    fps=cap.get(cv2.CAP_PROP_FPS);count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sar=(cap.get(cv2.CAP_PROP_SAR_NUM),cap.get(cv2.CAP_PROP_SAR_DEN))
    if fps<=0 or count<16 or min(sar)<=0:raise ValueError('Invalid video header/geometry')
    predicted=np.arange(count)/fps
    pre=[];required=set()
    for row in labels.itertuples():
        r=select_frames(predicted,row.start,row.end,mapping['offset_s'],mapping['uncertainty_s'],mapping['support_sensor_s'])
        pre.append(r)
        if r['accepted']:required.update(r['indices'])
    # Representative first eligible example per native class; visibility remains pending.
    reps=[]
    for native in (1,0,2):
        candidates=[i for i,r in enumerate(pre) if r['accepted'] and int(labels.iloc[i].label)==native]
        if candidates:reps.append(candidates[0])
    thumbs_needed=set(j for i in reps for j in pre[i]['indices'])
    if not reps:thumbs_needed=set(np.linspace(0,count-1,16).round().astype(int))
    pts=[];hashes={};thumbs={};repeats=0;last=None;shape=None
    index=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        pts.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000);shape=list(frame.shape)
        h=hashlib.sha256(frame.tobytes()).hexdigest();repeats+=h==last;last=h
        if index in required:hashes[index]=h
        if index in thumbs_needed:
            image=Image.fromarray(corrected_frame(frame,*sar));image.thumbnail((84,145))
            thumbs[index]=image
        index+=1
    cap.release();pts=np.asarray(pts)
    np.save(out/'native_pts.npy',pts)
    valid_clock=len(pts)==count and np.all(np.diff(pts)>0) and np.allclose(pts,predicted,rtol=0,atol=1e-6)
    audit={'decoded_frames':len(pts),'header_frames':count,'fps':fps,'sample_aspect_ratio':list(sar),
           'coded_shape':shape,'strictly_increasing_pts':bool(np.all(np.diff(pts)>0)),
           'single_pass_header_clock_verified':bool(valid_clock),'decode_passes':1,
           'first_pts_s':float(pts[0]) if len(pts) else None,'last_pts_s':float(pts[-1]) if len(pts) else None,
           'consecutive_identical_decoded_frames':int(repeats)}
    records=[]
    for i,row in enumerate(labels.itertuples()):
        r=select_frames(pts,row.start,row.end,mapping['offset_s'],mapping['uncertainty_s'],mapping['support_sensor_s'])
        if not valid_clock:
            r['accepted']=False;r['reasons'].append('single_pass_native_clock_not_confirmed')
        if r['accepted'] and r['indices']!=pre[i]['indices']:
            r['accepted']=False;r['reasons'].append('native_pts_preselection_mismatch')
        records.append(distinct_content(r,hashes))
    sheet=Image.new('RGB',(1600,65+max(1,len(reps))*190),'white');draw=ImageDraw.Draw(sheet)
    draw.text((8,8),str(video.parent)+' — SAR-corrected representative frames; visibility PENDING',fill='black')
    draw.text((8,27),'Native labels shown for review only; they were not inputs to acoustic alignment.',fill='black')
    for n,i in enumerate(reps):
        r=records[i];row=labels.iloc[i];y=58+n*190
        draw.text((4,y),f'row{i+2}\ny={int(row.label)}\n{row.start:.3f}\n..{row.end:.3f}',fill='black')
        for order,j in enumerate(r.get('indices',[])):
            x=112+order*92
            if j in thumbs:sheet.paste(thumbs[j],(x,y))
            draw.text((x,y+147),f'{pts[j]:.2f}s',fill='black')
    if not reps:
        draw.text((6,58),'No timing-eligible interval; experiment overview only, NOT labeled examples.',fill='black')
        for n,j in enumerate(sorted(thumbs)):sheet.paste(thumbs[j],(112+n*92,85))
    sheet.save(out/'contact_sheet.jpg',quality=80)
    audit['contact_sheet_source_rows']=[i+2 for i in reps]
    return records,hashes,audit


def audit_experiment(group,cfg,run,signature,pilot):
    out=run/'experiments'/group.replace('/','_');out.mkdir(exist_ok=True)
    checkpoint=out/'completed.json'
    if checkpoint.exists():
        result=json.loads(checkpoint.read_text())
        if result['audit_signature']!=signature:raise ValueError('Resume source/config identity changed')
        for item in result['inputs']:
            if sha256(Path(item['path']))!=item['sha256']:raise ValueError('Completed input changed')
        print('REUSED checkpoint',group,flush=True);return result
    required=[Path(cfg['data_root'])/p['name'] for p in cfg['download_plan'] if str(Path(p['name']).parent)==group]
    deadline=time.monotonic()+1800
    while not all(p.is_file() for p in required):
        for failure in (run/'evidence').glob('acquisition_failure_*.json'):
            if json.loads(failure.read_text()).get('http_status') in (401,403):
                raise PermissionError('Official dataset access restricted; audit stopped')
        if time.monotonic()>deadline:raise TimeoutError('Required acquisition incomplete: '+group)
        time.sleep(5)
    # An interrupted experiment is kept intact; a new attempt folder avoids overwrites.
    attempt=out/('attempt_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));attempt.mkdir()
    start_wall=time.perf_counter();folder=Path(cfg['data_root'])/group
    labels_path=folder/'label.csv';labels=pd.read_csv(labels_path)
    if not labels.label.isin([0,1,2]).all() or not (np.isfinite(labels[['start','end']]).all().all() and (labels.end>labels.start).all()):
        raise ValueError('Invalid native annotation: stop for evidence review')
    video=next(folder.glob('*.mp4'));wav=next(folder.glob('*_s2.wav'));mtc=next(folder.glob('*_mtc.csv'))
    programs=sorted(folder.glob('*.nc'))
    inputs=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in [labels_path,video,wav,mtc,*programs]]
    table=pd.read_csv(mtc)
    for c in ['time',*COMMON_MTC]:
        if c in table:table[c]=pd.to_numeric(table[c],errors='coerce')
    reference_date=re.match(r'(\d{8})_',mtc.name).group(1)
    metadata={'machine':group.split('/')[0],'experiment':group.split('/')[1],
              'reference_date':reference_date,'machine_date_group':group.split('/')[0]+'/'+reference_date,
              'calendar_date_group':reference_date,'date_evidence':'VERIFIED filename reference date; physical session INFERRED',
              'tools':sorted(map(str,labels.Tool.unique())),'materials':sorted(map(str,labels.Workpiece.unique())),
              'nc_programs':[{'name':p.name,'sha256':sha256(p),'header':p.read_text(errors='replace').splitlines()[:4]} for p in programs],
              'mtc_program_names':sorted(set(str(x) for c in ['Program_Name_Running','Program_Name_Editing'] if c in table for x in table[c].dropna().unique())),
              'mtc_current_tools':sorted(set(map(str,table.Current_Tool.dropna().unique()))) if 'Current_Tool' in table else [],
              'physical_tool_serial':'UNRESOLVED','physical_workpiece_serial':'UNRESOLVED','physical_session_id':'UNRESOLVED'}
    if group in pilot['mappings']:
        mapping=pilot['mappings'][group]
        frame_records=[pilot['frames'][f'{group}/row{i+2}'] for i in range(len(labels))]
        hashes={int(r.native_frame_index):r.decoded_frame_sha256 for r in pilot['selected'].itertuples() if r.group_id==group}
        video_audit={**pilot['video'][group],'reuse_source':cfg['stage2'],'new_decode_passes':0}
        # Existing full interval atlases remain authoritative; selected positive examples indexed.
        diagnostic=Path(cfg['stage2'])/'figures/visibility_atlas'
        metadata['representative_diagnostic_paths']=[str(p) for p in sorted(diagnostic.glob(group.replace('/','_')+'_page*.jpg'))]
        provenance='reused_final_stage2'
    else:
        protocol=json.loads((Path(cfg['stage2'])/'config/alignment_protocol_final.json').read_text())
        mapping=align(video,wav,protocol,attempt)
        if mapping['accepted']:
            frame_records,hashes,video_audit=decode_once(video,labels,mapping,attempt)
        else:
            frame_records=[{'accepted':False,'reasons':['alignment_rejected:'+mapping['reason']]} for _ in range(len(labels))]
            hashes={};video_audit={'decode_passes':0,'reason':'alignment_rejected'}
            # One forward overview pass for rejected experiments, with no false labeled sequences.
            cap=cv2.VideoCapture(str(video),cv2.CAP_FFMPEG,[cv2.CAP_PROP_N_THREADS,1]);count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sar=(cap.get(cv2.CAP_PROP_SAR_NUM),cap.get(cv2.CAP_PROP_SAR_DEN));wanted=set(np.linspace(0,max(0,count-1),16).round().astype(int))
            canvas=Image.new('RGB',(1600,210),'white');draw=ImageDraw.Draw(canvas)
            draw.text((8,8),group+' — alignment REJECTED; overview only; visibility pending',fill='black')
            i=0;n=0
            while True:
                ok,img=cap.read()
                if not ok:break
                if i in wanted:
                    im=Image.fromarray(corrected_frame(img,*sar));im.thumbnail((84,145));canvas.paste(im,(100+n*92,45));n+=1
                i+=1
            cap.release();canvas.save(attempt/'contact_sheet.jpg',quality=80)
            video_audit.update(decoded_overview_frames=i,decode_passes=1,sample_aspect_ratio=list(sar))
        metadata['representative_diagnostic_paths']=[str(attempt/'contact_sheet.jpg')]
        provenance='new_label_blind_full_lab_audit'
    records=[];features=[];selected=[]
    label_hash=sha256(labels_path)
    for i,label in enumerate(labels.itertuples()):
        ident=f'{group}/row{i+2}';f=frame_records[i]
        sensor_ok,values,gate=sensor_gate(table,float(label.start),float(label.end))
        reasons=list(f['reasons'])+gate['reasons']
        joint=bool(f['accepted'] and sensor_ok)
        record={'dataset_id':8392825,'dataset_version':2,'dataset_handle':cfg['handle'],
            'group_id':group,'machine':metadata['machine'],'experiment':metadata['experiment'],
            'interval_id':ident,'source_row':i+2,'native_label':int(label.label),
            'start_s':float(label.start),'end_s':float(label.end),'duration_s':float(label.end-label.start),
            'label_file':str(labels_path),'label_file_sha256':label_hash,'video_file':str(video),'video_sha256':inputs[1]['sha256'],
            'mtc_file':str(mtc),'mtc_sha256':inputs[3]['sha256'],'s2_file':str(wav),'s2_sha256':inputs[2]['sha256'],
            'reference_date':reference_date,'machine_date_group':metadata['machine_date_group'],
            'calendar_date_group':reference_date,'native_tool':str(label.Tool),'native_workpiece':str(label.Workpiece),
            'physical_session_id':'UNRESOLVED','nc_sha256_json':json.dumps([p['sha256'] for p in metadata['nc_programs']]),
            'alignment_pass':bool(mapping['accepted']),'video_minus_sensor_s':mapping.get('offset_s'),
            'alignment_uncertainty_s':mapping.get('uncertainty_s'),'supported_sensor_regions_json':json.dumps(mapping.get('support_sensor_s',[])),
            'frame_contract_pass':bool(f['accepted']),'selected_frames':16 if f['accepted'] else 0,
            'frame_indices_json':json.dumps(f.get('indices',[])),'video_pts_s_json':json.dumps(f.get('video_pts_s',[])),
            'mapped_sensor_pts_s_json':json.dumps(f.get('sensor_pts_s',[])),
            'frame_temporal_coverage_fraction':f.get('temporal_coverage_fraction'),
            'mtc_rows_inside_cut':gate['rows'],'mtc_max_coverage_gap_s':gate['max_gap_s'],
            'common_mtc_sensor_gate_pass':sensor_ok,'joint_technical_pass':joint,
            'context_review_status':'prior_Codex_context_review_only' if provenance=='reused_final_stage2' and f['accepted'] else 'pending_unverified',
            'independent_visibility_review':'pending_unverified' if f['accepted'] else 'not_technically_eligible',
            'visual_anomaly_observability':'unverified','primary_target':int(label.label==1),
            'label2_exclusion_sensitivity_included':int(label.label)!=2,
            'exclusion_reasons':';'.join(sorted(set(reasons))),'audit_provenance':provenance}
        if joint:assert record['exclusion_reasons']==''
        records.append(record)
        if sensor_ok:features.append({'interval_id':ident,**dict(zip(FEATURE_NAMES,values.tolist()))})
        if f['accepted']:
            assert len(set(f['indices']))==16
            for order,(j,tv,ts) in enumerate(zip(f['indices'],f['video_pts_s'],f['sensor_pts_s'])):
                selected.append({'interval_id':ident,'group_id':group,'source_row':i+2,'native_label':int(label.label),
                    'frame_order':order,'native_frame_index':j,'video_pts_s':tv,'mapped_sensor_time_s':ts,
                    'alignment_uncertainty_s':mapping['uncertainty_s'],'decoded_frame_sha256':hashes[j]})
    schema={'columns':list(table.columns),'required_channels':COMMON_MTC,'missing_channels':[c for c in COMMON_MTC if c not in table],
        'rows':len(table),'time_range_s':[float(table.time.min()),float(table.time.max())] if 'time' in table else None,
        'nonfinite_by_channel':{c:int((~np.isfinite(table[c])).sum()) for c in COMMON_MTC if c in table},
        'adjacent_held_fraction':{c:float(np.mean(np.diff(table[c])==0)) for c in COMMON_MTC if c in table},
        'held_values_warning':'MTC polling is not fresh high-frequency independent measurements; internal aggregation latency unknown'}
    result={'group_id':group,'audit_signature':signature,'inputs':inputs,'metadata':metadata,'mapping':mapping,
        'video_audit':video_audit,'sensor_schema':schema,'intervals':records,'sensor_features':features,'selected_frames':selected,
        'wall_seconds':time.perf_counter()-start_wall,'finished_utc':datetime.now(timezone.utc).isoformat()}
    write(checkpoint,result)
    print(group,'aligned',mapping['accepted'],'native',len(records),'joint',sum(r['joint_technical_pass'] for r in records),
          'positive',sum(r['joint_technical_pass'] and r['native_label']==1 for r in records),flush=True)
    return result


def group_summary(frame,key):
    result=[]
    for g,f in frame.groupby(key,sort=True):
        counts=f.native_label.value_counts().to_dict()
        result.append({'group':g,'intervals':len(f),'label_0':int(counts.get(0,0)),'label_1':int(counts.get(1,0)),
            'label_2':int(counts.get(2,0)),'both_classes':set(f.target)=={0,1},
            'machines':','.join(sorted(f.machine.unique())),'nominal_folders':int(f.group_id.nunique())})
    return result


def split_feasibility(frame,key):
    f=frame.copy();f['group_id']=f[key]
    summary=group_summary(frame,key)
    result={'grouping':key,'groups':len(summary),'positive_groups':sum(x['label_1']>0 for x in summary),
        'mixed_groups':sum(x['both_classes'] for x in summary),'group_distribution':summary,
        'outer_folds':3,'inner_folds':2,'seed':42,'final_split_frozen':False}
    try:
        plan=nested_plan(f,outer=3,inner=2,seed=42)
        folds=[]
        for k,fold in enumerate(plan):
            train=frame.iloc[fold['train']];test=frame.iloc[fold['test']]
            overlaps={c:sorted(set(train[c])&set(test[c])) for c in ['machine_date_group','calendar_date_group']}
            inner_overlaps=[]
            for it,iv in fold['inner']:
                a,b=frame.iloc[it],frame.iloc[iv]
                inner_overlaps.append({c:sorted(set(a[c])&set(b[c])) for c in ['machine_date_group','calendar_date_group']})
            folds.append({'fold':k,'train_intervals':len(train),'test_intervals':len(test),
                'train_positive':int(train.target.sum()),'test_positive':int(test.target.sum()),
                'train_groups':int(f.iloc[fold['train']].group_id.nunique()),'test_groups':int(f.iloc[fold['test']].group_id.nunique()),
                'outer_related_date_overlaps':overlaps,'inner_related_date_overlaps':inner_overlaps,
                'complete_both_class_group_disjoint_oof':True})
        result.update(passed=True,reason='Frozen single-seed nested construction passes technical group/class gates',fold_summary=folds)
    except ValueError as exc:result.update(passed=False,reason=str(exc))
    return result


def main(run):
    before=time.perf_counter();cfg=json.loads((run/'config/download_config.json').read_text())
    source_files=[Path(__file__),SOURCE/'prepare_full_lab.py',SOURCE/'msm/data.py',SOURCE/'msm/splits.py',
                  *sorted((SOURCE/'stage2').glob('*.py'))]
    identity={str(p):sha256(p) for p in source_files}
    signature=hashlib.sha256(json.dumps({'config':cfg,'sources':identity},sort_keys=True).encode()).hexdigest()
    old=Path(cfg['stage2']);pilot={'mappings':json.loads((old/'manifests/video_alignment_final.json').read_text()),
        'frames':{r['interval_id']:r for r in json.loads((old/'manifests/frame_contract.json').read_text())},
        'video':json.loads((old/'manifests/native_video_audit.json').read_text()),
        'selected':pd.read_csv(old/'manifests/selected_frame_manifest.csv')}
    results=[]
    with ThreadPoolExecutor(max_workers=cfg['workers']) as pool:
        pending={pool.submit(audit_experiment,g,cfg,run,signature,pilot):g for g in cfg['selected_groups']}
        for future in as_completed(pending):
            try:results.append(future.result())
            except Exception as exc:
                stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                write(run/'evidence'/('audit_failure_'+stamp+'.json'),{'group':pending[future],'error_type':type(exc).__name__,'message':str(exc)})
                for f in pending:f.cancel()
                raise
    results.sort(key=lambda x:x['group_id'])
    records=[r for x in results for r in x['intervals']];frame=pd.DataFrame(records)
    assert len(frame)==2512 and frame.interval_id.is_unique
    assert frame.native_label.value_counts().to_dict()=={0:1877,1:458,2:177}
    dump_csv(run/'MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv',records)
    dump_csv(run/'manifests/selected_frame_manifest.csv',[r for x in results for r in x['selected_frames']])
    dump_csv(run/'manifests/common_mtc_statistics.csv',[r for x in results for r in x['sensor_features']])
    summaries=[]
    for group,f in frame.groupby('group_id',sort=True):
        row={'group_id':group,'machine':f.machine.iloc[0],'reference_date':f.reference_date.iloc[0],
             **{f'native_label_{n}':int((f.native_label==n).sum()) for n in (0,1,2)},
             **{c:int(f[c].sum()) for c in ['alignment_pass','frame_contract_pass','common_mtc_sensor_gate_pass','joint_technical_pass']},
             'joint_positive':int(((f.native_label==1)&f.joint_technical_pass).sum()),
             'pending_independent_visibility':int(f.frame_contract_pass.sum()),
             'exclusion_counts_json':json.dumps(dict(collections.Counter(reason for s in f.exclusion_reasons for reason in s.split(';') if reason)))}
        summaries.append(row)
    dump_csv(run/'manifests/experiment_summary.csv',summaries)
    write(run/'manifests/alignment_results.json',{x['group_id']:x['mapping'] for x in results})
    write(run/'manifests/metadata_relationships.json',[x['metadata'] for x in results])
    write(run/'manifests/sensor_schema_audit.json',{x['group_id']:x['sensor_schema'] for x in results})
    write(run/'manifests/video_audit.json',{x['group_id']:x['video_audit'] for x in results})
    write(run/'manifests/input_manifest.json',[r for x in results for r in x['inputs']])
    splits={}
    for policy in ['stable_negative','exclude']:
        f=frame.loc[frame.joint_technical_pass].copy();f['target'],keep=binary_target(f.native_label,policy);f=f.loc[keep].reset_index(drop=True)
        splits[policy]={'intervals':len(f),'class_counts':{str(k):int(v) for k,v in f.native_label.value_counts().items()},
            'groupings':{key:split_feasibility(f,key) for key in ['group_id','machine_date_group','calendar_date_group']}}
    write(run/'manifests/split_feasibility.json',splits)
    summary={'native_intervals':len(frame),'native_class_counts':{str(k):int(v) for k,v in frame.native_label.value_counts().items()},
        'native_nominal_groups':frame.group_id.nunique(),'native_positive_groups':frame.loc[frame.native_label==1].group_id.nunique(),
        'aligned_experiments':sum(x['mapping']['accepted'] for x in results),'alignment_failed_experiments':[x['group_id'] for x in results if not x['mapping']['accepted']],
        **{c:int(frame[c].sum()) for c in ['alignment_pass','frame_contract_pass','common_mtc_sensor_gate_pass','joint_technical_pass']},
        'exclusion_reason_counts':dict(collections.Counter(reason for s in frame.exclusion_reasons for reason in s.split(';') if reason)),
        'new_context_visibility_pending':int(((frame.audit_provenance!='reused_final_stage2')&frame.frame_contract_pass).sum()),
        'all_frame_valid_independent_visibility_pending':int(frame.frame_contract_pass.sum()),
        'joint_independent_visibility_pending':int(frame.joint_technical_pass.sum()),
        'wall_seconds':time.perf_counter()-before,'workers':cfg['workers'],'gpu_work':False,'ml_training':False,
        'audit_source_identity':identity,'audit_signature':signature}
    # JSON normalizer converts numpy scalars but never allows hidden NaN metrics.
    summary=json.loads(json.dumps(summary,default=lambda x:x.item()))
    write(run/'manifests/cohort_summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['audit_source_identity']},indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);main(p.parse_args().run)
