"""Real held-out examples; no generated images or image-based anomaly claims."""
import hashlib
import html
import json
import os
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from external_eval.io import sha,write_json

MATCHED=Path('MILLING DATASET/runs/20261027T190717486889Z-matched-visual-review')


def relative(path,base):return os.path.relpath(path,base)


def montage(images,captions,path,title):
    """A contact sheet is a display derivative, never an input to the model."""
    thumb_w=240;thumb_h=300;header=65;footer=30
    out=Image.new('RGB',(4*thumb_w,header+4*(thumb_h+footer)),(242,242,242));draw=ImageDraw.Draw(out)
    draw.text((10,10),title,fill='black')
    for k,(image,caption) in enumerate(zip(images,captions)):
        im=image.copy();im.thumbnail((thumb_w-8,thumb_h-8),Image.Resampling.LANCZOS)
        x=(k%4)*thumb_w;y=header+(k//4)*(thumb_h+footer)
        out.paste(im,(x+(thumb_w-im.width)//2,y+(thumb_h-im.height)//2))
        draw.text((x+5,y+thumb_h),caption,fill='black')
    out.save(path)


def sensor_plot(root,row,channels,path):
    if row.dataset_name=='MSM':
        raw=pd.read_csv(row.mtc_file,usecols=['time',*channels]);t=raw.time.to_numpy(float)
        keep=(t>=row.start_s)&(t<row.end_s);x=raw.loc[keep,channels].to_numpy(float);t=t[keep]
        groups=[['watt','Spindle_Speed','S_Axis_Load','Feed_Rate'],['X_Axis_Load','Y_Axis_Load','Z_Axis_Load'],
            ['smarms','xmarms','ymarms','zmarms'],['smvrms','xmvrms','ymvrms','zmvrms']]
        fig,axes=plt.subplots(4,1,figsize=(12,9),sharex=True,layout='constrained')
        # Differently scaled MTC quantities are explicitly standardized for display.
        for ax,names in zip(axes,groups):
            for name in names:
                z=x[:,channels.index(name)];sd=z.std();ax.plot(t-row.start_s,(z-z.mean())/(sd if sd else 1),label=name)
            ax.set_ylabel('Within-cut z\n(display only)');ax.legend(fontsize=8,ncol=4)
    else:
        folder=Path(row.trial_folder);indices=np.array(json.loads(row.sensor_row_indices_json),int)
        t=np.load(folder/'head_cam_ts.npy',allow_pickle=False).reshape(-1)[indices]
        x=np.load(row.sensor_file,allow_pickle=False)[indices]
        fig,axes=plt.subplots(2,1,figsize=(12,7),sharex=True,layout='constrained')
        for k,ax in enumerate(axes):
            for j in range(k*3,(k+1)*3):ax.plot(t-row.start_s,x[:,j],label=channels[j])
            ax.legend(ncol=3);ax.set_ylabel('Force (N)' if k==0 else 'Torque (N m)')
        fig.suptitle('Released wrench: measured on HSR, joint-torque-estimated on Gen3')
    for ax in axes:
        for when in json.loads(row.mapped_sensor_pts_s_json):ax.axvline(when-row.start_s,color='grey',alpha=.2,lw=.6)
        ax.grid(alpha=.2)
    axes[-1].set_xlabel('Seconds from common observation-window start; vertical lines = 16 selected frames')
    axes[0].set_title(f'{row.sample_id}; native label {row.native_label}; one interval/trial-level target {row.target}')
    fig.savefig(path,dpi=140);plt.close(fig)


def make_examples(root,predictions,primary):
    root=Path(root);config=json.loads((root/'04_experiment_protocol/experiment_config.json').read_text());dataset=config['dataset']
    base=root/'08_visual_examples_and_eda';dest=base/'prediction_examples';dest.mkdir(parents=True,exist_ok=True)
    done=dest/'EXAMPLES_COMPLETE.json'
    if done.exists():
        for p,h in json.loads(done.read_text())['hashes'].items():
            if sha(p)!=h:raise ValueError('Qualitative evidence changed')
        return
    manifest=pd.read_csv(root/'03_processed_model_inputs/final_sample_manifest.csv',keep_default_na=False).set_index('sample_id',drop=False)
    alignment=pd.read_csv(root/'02_labels_and_alignment/alignment_manifest.csv')
    id_column='sample_id' if 'sample_id' in alignment else 'interval_id'
    source_hashes={(getattr(f,id_column),int(f.native_frame_index)):f.decoded_frame_sha256 for f in alignment.itertuples()}
    clean=predictions[(predictions.protocol==primary)&(predictions.role=='test')&(predictions.corruption=='clean')&
        (predictions.initialization=='P')&(predictions.seed==42)]
    if dataset=='MSM':
        cuts=pd.read_csv(MATCHED/'CUT_MANIFEST.csv');selected=cuts.interval_id.tolist()
        frames=pd.read_csv(MATCHED/'FRAME_MANIFEST.csv');rationale='The five preserved parameter-matched normal/abnormal pairs were selected before this evaluation. Both laboratory machines are included. Each pair matches eight cutting fields but direction differs (normal DOWN/abnormal UP); these are examination examples, not a direction-controlled causal comparison.'
    else:
        test=manifest[manifest.official_split=='test'];selected=[]
        # Label-stratified identification is only for post-evaluation examination.
        for target in [0,1]:selected.extend(sorted(test[test.target==target].sample_id)[:5])
        rationale='The first five official-test native successes and first five failures by split-qualified ID. This deterministic post-evaluation gallery is for examination, not frame selection or model tuning. Both robots appear when present among those IDs. The same fixed lower-camera context crop (0–85% width,30–100% height) is shown throughout; it is not a detected object or anomaly annotation.'
    # Add systematic error examples instead of presenting only correct decisions.
    reference_model='F2' if dataset=='MSM' else 'averaging'
    reference=clean[clean.model==reference_model].set_index('sample_id')
    additional=[]
    for target in [0,1]:
        errors=reference[(reference.target==target)&((reference.probability>=.5).astype(int)!=reference.target)]
        additional.extend([ident for ident in sorted(errors.index) if ident not in selected][:2])
    selected+=additional
    selected=list(dict.fromkeys(selected));records=[];frame_rows=[];sections=[]
    for n,ident in enumerate(selected):
        row=manifest.loc[ident].copy();row['dataset_name']=dataset;key=f'example_{n+1:02d}';example=dest/key;example.mkdir(exist_ok=True)
        context='';pair_id=''
        if dataset=='MSM':
            match=cuts[cuts.interval_id==ident]
            if len(match):
                native_match=match.iloc[0];pair_id=native_match.pair_id
                context=f'Pair {pair_id}; machine {row.machine}; direction {row.direction}. Matched native cutting fields: '+', '.join(f'{name}={native_match[name]}' for name in ['N','ap','ae','F','Z','D','Tool','Workpiece'])+'. Direction differs within each pair.'
            else:context=f'Additional model-error example; machine {row.machine}, direction {row.direction}. Not a matched-parameter pair.'
        else:context=f'{row.robot}; {row.task}; native outcome {row.native_label_name}. Participant identity is unavailable.'
        probabilities=clean[clean.sample_id==ident].set_index('model').probability.to_dict()
        full=[];crops=[];links=[];captions=[]
        indices=json.loads(row.frame_indices_json);pts=json.loads(row.video_pts_s_json);times=json.loads(row.mapped_sensor_pts_s_json)
        if dataset=='MSM' and ident in set(frames.interval_id):
            native=frames[frames.interval_id==ident].sort_values('frame_order')
            if native.native_frame_index.tolist()!=indices:raise ValueError('Preserved matched frames differ from model input')
            for j,f in enumerate(native.itertuples()):
                fp=MATCHED/f.full_image;rp=MATCHED/f.roi_image
                if sha(fp)!=f.full_image_sha256 or sha(rp)!=f.roi_image_sha256:raise ValueError('Preserved preview changed')
                full.append(Image.open(fp).convert('RGB'));crops.append(Image.open(rp).convert('RGB'));links.append((fp,rp))
        else:
            cap=cv2.VideoCapture(row.video_file,cv2.CAP_FFMPEG,[cv2.CAP_PROP_N_THREADS,1])
            for j,index in enumerate(indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,bgr=cap.read()
                if not ok or abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-pts[j])>1e-6:raise ValueError('Qualitative source frame mismatch')
                if hashlib.sha256(bgr.tobytes()).hexdigest()!=source_hashes[(ident,int(index))]:raise ValueError('Qualitative decoded source bytes mismatch')
                im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB));im=im.resize((round(im.width*row.sar_num/row.sar_den),im.height),Image.Resampling.LANCZOS)
                # New MSM error examples use a declared central contextual crop.
                box=(0,round(im.height*.3),round(im.width*.85),im.height) if dataset=='HANDOVER' else (round(im.width*.15),round(im.height*.2),round(im.width*.95),round(im.height*.8))
                crop=im.crop(box);fp=example/f'frame_{j+1:02d}_full.png';rp=example/f'frame_{j+1:02d}_context.png'
                im.save(fp);crop.save(rp);full.append(im);crops.append(crop);links.append((fp,rp))
            cap.release()
        for j,(fp,rp) in enumerate(links):
            captions.append(f'{j+1:02d}: frame {indices[j]}, PTS {pts[j]:.3f}s')
            frame_rows.append({'sample_id':ident,'native_label':row.native_label,'target':row.target,'frame_order':j,
                'native_frame_index':indices[j],'video_pts_s':pts[j],'source_clock_s':times[j],
                'full_view':str(fp),'context_view':str(rp),'full_view_sha256':sha(fp),'context_view_sha256':sha(rp),
                'frame_label':'No frame-level ground truth; original interval/trial label only'})
        montage(full,captions,example/'full_sequence.png',f'{ident}; native label {row.native_label}; FULL CAMERA, 16 model frames')
        montage(crops,captions,example/'context_sequence.png',f'{ident}; ENLARGED CONTEXT; crop is for examination only')
        sensor_plot(root,row,config['sensor_channels'],example/'sensor_timeline.png')
        p=float(probabilities[reference_model]);correct=int(p>=.5)==row.target
        records.append({'sample_id':ident,'pair_id':pair_id,'native_label':row.native_label,'target':row.target,'reference_model':reference_model,
            'reference_probability':p,'correct_at_frozen_0_5_threshold':bool(correct),'primary_matched_or_native_gallery':n<10,
            **{'P_seed42_'+k:float(v) for k,v in probabilities.items()}})
        native_table='<table><tr><th>Model</th><th>Positive probability</th></tr>'+''.join(f'<tr><td>{html.escape(k)}</td><td>{v:.6f}</td></tr>' for k,v in sorted(probabilities.items()))+'</table>'
        images=''.join(f'<figure><a href="{html.escape(relative(fp,dest))}"><img src="{html.escape(relative(fp,dest))}" loading="lazy"></a><a href="{html.escape(relative(rp,dest))}"><img src="{html.escape(relative(rp,dest))}" loading="lazy"></a><figcaption>{html.escape(captions[j])}; source clock {times[j]:.3f}s</figcaption></figure>' for j,(fp,rp) in enumerate(links))
        sections.append(f'<section><h2>{html.escape(ident)} — native {row.native_label}, binary {row.target}</h2><p>{html.escape(context)}</p><p>{reference_model} at0.5: {"correct" if correct else "error"}. One probability per entire native example. Start/end {row.start_s:.6f}/{row.end_s:.6f}s.</p>{native_table}<img class="timeline" src="{key}/sensor_timeline.png"><p><a href="{key}/full_sequence.png">Full-camera contact sheet</a> · <a href="{key}/context_sequence.png">Enlarged context sheet</a></p><div class="frames">{images}</div></section>')
    primary_examples=pd.DataFrame(records).iloc[:10]
    if primary_examples.target.value_counts().to_dict()!={0:5,1:5}:raise ValueError('Primary examination cohort is not five negatives/five positives')
    primary_frames=pd.DataFrame(frame_rows);primary_frames=primary_frames[primary_frames.sample_id.isin(primary_examples.sample_id)]
    if len(primary_frames)!=160:raise ValueError('Primary examination gallery must contain160 native frames')
    primary_examples.to_csv(dest/'primary_10_examples.csv',index=False);primary_frames.to_csv(dest/'primary_160_frames.csv',index=False)
    pd.DataFrame(records).to_csv(dest/'example_predictions.csv',index=False);pd.DataFrame(frame_rows).to_csv(dest/'example_frame_manifest.csv',index=False)
    page=f'<!doctype html><html><head><meta charset="utf-8"><title>{dataset}: real held-out examination examples</title><style>body{{font:16px system-ui;max-width:1500px;margin:auto;padding:24px}}section{{border-top:2px solid #ccc;margin-top:36px}}.frames{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}figure{{margin:0}}figure img{{max-width:49%;max-height:300px}}figcaption{{font-size:12px}}.timeline{{max-width:100%}}table{{border-collapse:collapse}}td,th{{padding:5px 14px;border:1px solid #ddd}}@media(max-width:900px){{.frames{{grid-template-columns:repeat(2,1fr)}}}}</style></head><body><h1>{dataset}: real held-out examples</h1><p>{html.escape(rationale)}</p><p>Clean P initialization, fixed seed42, frozen threshold0.5. Neither contacts, crops nor human overlays were model inputs. Native frames remain ordered; zooming creates no new detail. Vertical timeline marks show the actual selected frame clock. Additional examples are the first available false-positive/false-negative IDs, at most two of each.</p>{"".join(sections)}</body></html>'
    (dest/'index.html').write_text(page)
    (base/'README.md').write_text(f'# {dataset} examination materials\n\nOpen [the full gallery](prediction_examples/index.html). It contains five negative and five positive native examples, 16 real frames each, full-camera/context views, synchronized sensor plots and measured held-out probabilities. Additional deterministic error examples are labeled separately.\n\n{rationale}\n\nThese examples are for researcher review; no frame-level anomaly labels or proof of visual observability is implied.\n')
    paths=[p for p in dest.rglob('*') if p.is_file()]
    write_json(done,{'dataset':dataset,'gallery_native_examples':10,'additional_error_examples':len(selected)-10,'gallery_distinct_native_frames':160,
        'source_frame_order_and_timestamps_preserved':True,'reference_model':reference_model,'selection':rationale,
        'hashes':{str(p):sha(p) for p in paths}})
