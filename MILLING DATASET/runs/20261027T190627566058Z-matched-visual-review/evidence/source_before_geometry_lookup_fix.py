"""Extract ten audited cuts for direct human review, without fitting a model.

The 160 unique native frames are verified against the full laboratory audit.
Display images correct source sample aspect ratio; ROI derivatives are literal
pixel crops. No generative processing, deblurring, contrast enhancement or raw
data rewriting is performed.
"""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import cv2
import numpy as np
import pandas as pd
from PIL import Image

ROOT=Path('MILLING DATASET')
COHORT=ROOT/'runs/20261027T015205931708Z-stage5-full-lab-validated'
RAW=ROOT/'data/raw/msm/versions/2'
PARAMETERS=['N','ap','ae','F','Z','D','Tool','Workpiece']
PAIR_PLAN=[
    ('P01','imi_vm20i/dataset16',25,24),
    ('P02','imi_vm20i/dataset25',9,8),
    ('P03','imi_vm20i/dataset27',25,24),
    ('P04','imi_vmx30ui/dataset14',41,40),
    ('P05','imi_vmx30ui/dataset9',13,14),
]


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()


def write_json(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def write_csv(path,rows):
    with path.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def prepare():
    run=ROOT/'runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-matched-visual-review')
    for name in ('config','manifests','figures','frames','logs','evidence'):(run/name).mkdir(parents=True,exist_ok=False)
    with (run/'.gitignore').open('x') as f:f.write('/frames/\n/figures/\n/*.pdf\n/*.zip\n/logs/\n')
    cohort=pd.read_csv(COHORT/'MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv').set_index('interval_id')
    selected=pd.read_csv(COHORT/'manifests/selected_frame_manifest.csv')
    video_audits=json.loads((COHORT/'manifests/video_audit.json').read_text())
    cuts=[];frames=[];pairs=[];inputs={}
    cv2.setNumThreads(1)
    for pair_id,group,normal_row,abnormal_row in PAIR_PLAN:
        labels_path=RAW/group/'label.csv';labels=pd.read_csv(labels_path)
        group_cuts=[]
        for native,rowno in [(0,normal_row),(1,abnormal_row)]:
            ident=f'{group}/row{rowno}';r=cohort.loc[ident];annotation=labels.iloc[rowno-2]
            assert r.joint_technical_pass and r.native_label==native==annotation.label
            assert r.start_s==annotation.start and r.end_s==annotation.end
            assert digest(labels_path)==r.label_file_sha256
            video=Path(r.video_file)
            if str(video) not in inputs:
                inputs[str(video)]={'path':str(video),'sha256':digest(video),'bytes':video.stat().st_size}
            assert inputs[str(video)]['sha256']==r.video_sha256
            inputs[str(labels_path)]={'path':str(labels_path),'sha256':digest(labels_path),'bytes':labels_path.stat().st_size}
            name=f'{pair_id}_'+('normal' if native==0 else 'abnormal')
            cut={'cut_id':name,'pair_id':pair_id,'group_id':group,'interval_id':ident,'machine':r.machine,
                 'source_row':rowno,'native_label':native,'start_s':float(r.start_s),'end_s':float(r.end_s),
                 'duration_s':float(r.duration_s),'video_file':str(video),'video_sha256':r.video_sha256,
                 'label_file':str(labels_path),'label_file_sha256':r.label_file_sha256,
                 'offset_s':float(r.video_minus_sensor_s),'uncertainty_s':float(r.alignment_uncertainty_s),
                 'direction':annotation.direction,'parameters':{k:annotation[k].item() if hasattr(annotation[k],'item') else annotation[k] for k in PARAMETERS},
                 'mtc_rows':int(r.mtc_rows_inside_cut),'mtc_max_gap_s':float(r.mtc_max_coverage_gap_s),
                 'visibility_review':'pending; delivered for researcher examination',
                 'frames':[]}
            frame_rows=selected[selected.interval_id==ident].sort_values('frame_order').to_dict('records')
            assert len(frame_rows)==16 and len({x['decoded_frame_sha256'] for x in frame_rows})==16
            assert [int(x['frame_order']) for x in frame_rows]==list(range(16))
            assert [int(x['native_frame_index']) for x in frame_rows]==json.loads(r.frame_indices_json)
            cut['frames']=frame_rows;group_cuts.append(cut)
        normal,abnormal=group_cuts
        assert normal['parameters']==abnormal['parameters']
        pair={'pair_id':pair_id,'group_id':group,'normal':normal['cut_id'],'abnormal':abnormal['cut_id'],
              'normal_interval':normal['interval_id'],'abnormal_interval':abnormal['interval_id'],
              'matching_parameters':normal['parameters'],'normal_direction':normal['direction'],
              'abnormal_direction':abnormal['direction'],'direction_matched':normal['direction']==abnormal['direction'],
              'selection_note':'Same experiment, exact recorded numerical parameters, same generic tool/material; nearest timing among these matches in the chosen experiment. Direction differs.',
              'selection_basis':'metadata only; no visibility, CNN scores or predictive results used'}
        pairs.append(pair)
        # Decode one bounded contiguous range per experiment, retaining only audited indices.
        requested={int(f['native_frame_index']):(cut,f) for cut in group_cuts for f in cut['frames']}
        assert len(requested)==32
        first,last=min(requested),max(requested)
        cap=cv2.VideoCapture(normal['video_file'],cv2.CAP_FFMPEG,[cv2.CAP_PROP_N_THREADS,1])
        assert cap.isOpened()
        sar=(int(cap.get(cv2.CAP_PROP_SAR_NUM)),int(cap.get(cv2.CAP_PROP_SAR_DEN)))
        assert list(sar)==[int(x) for x in video_audits[group]['sample_aspect_ratio']]
        cap.set(cv2.CAP_PROP_POS_FRAMES,first)
        extracted=0
        for index in range(first,last+1):
            ok,bgr=cap.read()
            if not ok:raise ValueError('Missing native decoded frame')
            actual_index=int(round(cap.get(cv2.CAP_PROP_POS_FRAMES)))-1
            if actual_index!=index:raise ValueError('Native decoder index mismatch')
            if index not in requested:continue
            cut,f=requested[index];pts=cap.get(cv2.CAP_PROP_POS_MSEC)/1000
            assert abs(pts-f['video_pts_s'])<1e-6
            h=hashlib.sha256(bgr.tobytes()).hexdigest()
            assert h==f['decoded_frame_sha256']
            sensor=pts-cut['offset_s'];u=cut['uncertainty_s']
            assert sensor-u>=cut['start_s'] and sensor+u<cut['end_s']
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            display=Image.fromarray(rgb).resize((round(rgb.shape[1]*sar[0]/sar[1]),rgb.shape[0]),Image.Resampling.BILINEAR)
            dest=run/'frames'/cut['cut_id'];dest.mkdir(exist_ok=True)
            output=dest/f'frame_{int(f["frame_order"])+1:02d}_full.png'
            display.save(output)
            record={**f,'cut_id':cut['cut_id'],'pair_id':pair_id,'full_image':str(output.relative_to(run)),
                    'full_image_sha256':digest(output),'display_width':display.width,'display_height':display.height,
                    'source_sar_num':sar[0],'source_sar_den':sar[1]}
            frames.append(record);extracted+=1
        cap.release();assert extracted==32
        # Midpoint preview is only for selecting a common geometric ROI, never for cut selection.
        for cut in group_cuts:
            midpoint=next(x for x in frames if x['cut_id']==cut['cut_id'] and x['frame_order']==7)
            image=Image.open(run/midpoint['full_image'])
            image.save(run/'figures'/(cut['cut_id']+'_midpoint.png'))
        cuts.extend(group_cuts)
        print(pair_id,group,'extracted 32 verified frames',flush=True)
    assert len(cuts)==10 and len(frames)==160
    assert len({(f['group_id'],f['native_frame_index']) for f in frames})==160
    write_json(run/'config/review_plan.json',{'dataset_handle':'manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2',
        'authoritative_cohort':str(COHORT),'pairs':pairs,'pair_count':5,'normal_cuts':5,'abnormal_cuts':5,
        'source_frames':160,'normal_machine_count':{'imi_vm20i':3,'imi_vmx30ui':2},
        'selection_disclosure':'No exact complete nine-field match including native direction was found within eligible mixed-label experiments. Exact eight-field matches retained with direction mismatch explicitly reported.',
        'new_training':False,'new_downloads':False,'roi_policy':'Fixed shared rectangle per pair, chosen from both midpoint full views to encompass tool/workpiece context; not an anomaly localization.'})
    # Keep the per-cut metadata compact; frame records are stored separately.
    write_json(run/'manifests/cuts.json',[{k:v for k,v in c.items() if k!='frames'} for c in cuts])
    write_csv(run/'manifests/frames_full.csv',sorted(frames,key=lambda r:(r['cut_id'],r['frame_order'])))
    write_json(run/'manifests/inputs.json',list(inputs.values())+[
        {'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size} for p in [COHORT/'MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv',COHORT/'manifests/selected_frame_manifest.csv']])
    write_json(run/'provenance_initial.json',{'utc':datetime.now(timezone.utc).isoformat(),
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'tracked_status':subprocess.check_output(['git','status','--short','--untracked-files=no'],text=True),
        'command':sys.argv,'source_sha256':digest(Path(__file__)),'ml_training':False,'gpu_access':False})
    print(json.dumps({'run':str(run),'source_frames':len(frames)},indent=2))
    return run


if __name__=='__main__':
    prepare()
