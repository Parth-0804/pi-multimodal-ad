"""Actual source imagery, blinded QC sheets and held-out prediction illustrations."""
from collections import defaultdict
import html
import json
import numpy as np
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .common import PROJECT,config,read,sha,signature,video_path,write
from .cohort import finalize
from .sensors import load_episode,sensor_sources
from .video import rgb_frames


def sheet(images,path,crop=False,times=None):
    if path.exists():return
    canvas=Image.new('RGB',(960,4*202),'white');draw=ImageDraw.Draw(canvas)
    for i,image in enumerate(images):
        pic=Image.fromarray(image)
        if crop:
            w,h=pic.size;pic=pic.crop((int(w*.15),int(h*.05),int(w*.85),int(h*.9)))
        pic.thumbnail((240,180));x=(i%4)*240;y=(i//4)*202
        canvas.paste(pic,(x,y));draw.text((x+4,y+181),f'{i+1:02d}  '+(f'{times[i]:.2f}s' if times is not None else ''),fill='black')
    path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path,quality=88)


def entry(c,row,root,anonymous):
    name='B'+signature(['blinded',row['episode_index']])[:10] if anonymous else f'episode_{row["episode_index"]:06d}'
    items=[];identities=[]
    for cam,key in zip(c['cameras'],['video_high','video_left','video_right']):
        frames=rgb_frames(video_path(c,row[key]),row['frame_indices'])
        paths=[]
        for crop in [False,True]:
            path=root/'assets'/f'{name}_{cam}_{"center_enlargement" if crop else "full"}.jpg'
            sheet(frames,path,crop,row['frame_times_seconds']);paths.append(path.relative_to(root).as_posix())
            identities.append({'path':paths[-1],'sha256':sha(path),'source_video_sha256':sha(video_path(c,row[key])),
                               'frame_indices':row['frame_indices'],'view':'fixed central crop' if crop else 'full view'})
        items.append(f'<h4>{cam}</h4><p>Full camera view</p><img src="{paths[0]}"><p>Fixed central enlargement (not a verified object bounding box)</p><img src="{paths[1]}">')
    return name,'\n'.join(items),identities


def blinded(c=None):
    c=c or config();rows=finalize(c);qc=read(PROJECT/'02_dataset_verification/video_audit/runs'/c['run_id']/'VIDEO_QC_COMPLETE.json')
    root=PROJECT/'08_visual_examples_and_eda/real_examples/generated'/c['run_id']/'BLINDED_QC_GALLERY'
    if (root/'COMPLETE.json').exists():return read(root/'COMPLETE.json')
    tasks=defaultdict(list)
    for row in rows:tasks[row['canonical_task_id']].append(row)
    selected={min(values,key=lambda r:signature(['task_sheet',r['episode_index']]))['episode_index'] for values in tasks.values()}
    # Extra label-blind extremes across QC quality, without selecting by outcome.
    for key in ['median_laplacian_variance_160x120','black_fraction','adjacent_identical_fraction']:
        order=sorted(qc['cameras'],key=lambda r:r.get('quality',{}).get(key,0))
        selected.update(r['episode_index'] for r in order[:5]+order[-5:])
    pages=[];manifest=[];mapping=[]
    for row in rows:
        if row['episode_index'] not in selected:continue
        name,content,files=entry(c,row,root,True)
        pages.append(f'<article><h2>{name}</h2><p>16 fixed timestamps per camera; time is relative to episode start.</p>{content}<p>Semantic review: visibility, occlusion and incidental human presence remain to be assessed.</p></article>')
        manifest+=files;mapping.append({'blinded_id':name,'episode_index':row['episode_index'],'canonical_task_id':row['canonical_task_id']})
    root.mkdir(parents=True,exist_ok=True)
    (root/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Blinded technical QC gallery</title><style>body{font-family:sans-serif;max-width:1100px;margin:auto}img{max-width:100%}article{border-top:3px solid #333;margin:2em 0}</style><h1>Blinded three-camera QC gallery</h1><p>Systematic task coverage and quality extremes; selected without outcomes. Fixed central enlargements can miss a task-specific object. Keep the full view as context.</p>'+''.join(pages))
    write(root/'ASSET_MANIFEST.json',manifest)
    # Mapping is deliberately separate from the blinded image folder.
    write(PROJECT/'02_dataset_verification/video_audit'/c['run_id']/'BLINDED_QC_IDENTITY_MAP.json',mapping)
    receipt={'examples':len(pages),'tasks':len(tasks),'index':str((root/'index.html').relative_to(PROJECT.parent)),
             'asset_manifest_sha256':sha(root/'ASSET_MANIFEST.json'),'semantic_human_review':'PENDING'}
    write(root/'COMPLETE.json',receipt);return receipt


def prediction_gallery(c=None,conditions=('V1','V2','V3')):
    c=c or config();lookup={r['episode_index']:r for r in finalize(c)};inventory=sensor_sources(c)
    for condition in conditions:
        root=PROJECT/'08_visual_examples_and_eda/prediction_galleries/generated'/c['run_id']/condition
        if (root/'COMPLETE.json').exists():continue
        base=PROJECT/'06_training_experiments/fusion_experiments/runs'/c['run_id']/condition/'seed42'
        records=[r for p in sorted(base.glob('outer*/predictions.json')) for r in read(p)]
        augmented_base=PROJECT/'06_training_experiments/fusion_experiments/augmentation/runs'/c['run_id']/condition/'seed42'
        augmented={r['episode_index']:r for p in sorted(augmented_base.glob('outer*/predictions.json')) if p.with_name('COMPLETE.json').exists() for r in read(p)}
        records=[{**r,**{k:v for k,v in augmented.get(r['episode_index'],{}).items() if k in ['F2_aug_probability','gate_aug_probability','gate_static_aug_probability']}} for r in records]
        if not records:raise RuntimeError('SAVED_HELD_OUT_PREDICTIONS_NOT_AVAILABLE')
        groups=defaultdict(list)
        for r in records:
            v=(r['visual_probability']>=.5)==bool(r['label']);s=(r['sensor_probability']>=.5)==bool(r['label'])
            f=(r['F2_probability']>=.5)==bool(r['label'])
            categories=['both_correct' if v and s else 'both_incorrect' if not v and not s else 'vision_correct_sensor_wrong' if v else 'sensor_correct_vision_wrong']
            if f and not(v and s):categories+=['fusion_corrects_unimodal_error']
            if not f and (v or s):categories+=['fusion_introduces_error']
            for category in categories:groups[category].append(r)
        pages=[];manifest=[];selection=[]
        for category in ['both_correct','both_incorrect','vision_correct_sensor_wrong','sensor_correct_vision_wrong','fusion_corrects_unimodal_error','fusion_introduces_error']:
            candidates=sorted(groups[category],key=lambda r:signature(['posthoc_gallery',r['episode_index']]))[:1]
            if not candidates:pages.append(f'<h2>{category}</h2><p>No matching saved held-out example.</p>');continue
            prediction=candidates[0];row=lookup[prediction['episode_index']]
            name,content,files=entry(c,row,root,False);manifest+=files
            values,clock=load_episode(c,row,inventory)
            figure,axes=plt.subplots(3,1,figsize=(12,7),sharex=True)
            for ax,columns,title in zip(axes,[range(14),range(14,26),range(26,28)],['joint/gripper position fields','joint velocities','gripper-effort fields (not force/torque)']):
                ax.plot(clock,values[:,list(columns)],linewidth=.7);ax.set_ylabel(title);ax.grid(alpha=.2)
                for t in row['frame_times_seconds']:ax.axvline(t,color='grey',alpha=.1)
            axes[-1].set_xlabel('converted relative seconds');figure.tight_layout()
            plot=root/'assets'/f'{name}_sensors.png';plot.parent.mkdir(parents=True,exist_ok=True);figure.savefig(plot,dpi=110);plt.close(figure)
            manifest.append({'path':plot.relative_to(root).as_posix(),'sha256':sha(plot),'sensor_source':row['data'],
                             'sensor_source_sha256':inventory[row['data']]['expected_sha256']})
            selection.append({'category':category,**prediction})
            pages.append(f'<article><h2>{category}: {name}</h2><pre>{html.escape(json.dumps(prediction,indent=2))}</pre>{content}<h3>Measured sensor timeline</h3><img src="assets/{plot.name}"></article>')
        stress=PROJECT/'07_robustness_experiments/combined_corruption/runs'/c['run_id']/condition/'seed42'
        changes=[]
        for path in sorted(stress.glob('outer*/predictions.json')):
            values=read(path);clean={r['episode_index']:r for r in values if r['scenario']=='clean'}
            for r in values:
                original=clean.get(r['episode_index'])
                if r.get('status')!='PREDICTED' or not original or r['scenario']=='clean':continue
                if any((r[k]>=.5)!=(original[k]>=.5) for k in ['F2_probability','gate_probability']):changes.append((r,original))
        if changes:
            changed,original=min(changes,key=lambda pair:signature(['stress_gallery',pair[0]['episode_index'],pair[0]['scenario']]))
            from .corruptions import SCENARIOS,alter_visual
            from .visual import pixels
            row=lookup[changed['episode_index']];scenario=next(s for s in SCENARIOS if s['name']==changed['scenario'])
            x,_=alter_visual(pixels(c,row),row['episode_index'],scenario)
            frames=np.rint(x.numpy().transpose(0,1,3,4,2)*255).clip(0,255).astype('uint8');pictures=[]
            for cam,images in zip(c['cameras'],frames):
                path=root/'assets'/f'changed_{row["episode_index"]:06d}_{cam}.jpg';sheet(images,path,times=row['frame_times_seconds'])
                pictures.append(f'<h4>{cam}</h4><img src="assets/{path.name}">')
                manifest.append({'path':path.relative_to(root).as_posix(),'sha256':sha(path),'scenario':scenario})
            selection.append({'category':'degradation_changes_prediction','clean':original,'corrupted':changed})
            pages.append('<h2>Degradation changes a saved prediction</h2><pre>'+html.escape(json.dumps({'clean':original,'corrupted':changed},indent=2))+'</pre>'+''.join(pictures))
        else:pages.append('<h2>Degradation changes a prediction</h2><p>No qualifying change found in the available saved seed42 stress predictions.</p>')
        root.mkdir(parents=True,exist_ok=True)
        (root/'index.html').write_text('<!doctype html><meta charset="utf-8"><style>body{font-family:sans-serif;max-width:1100px;margin:auto}img{max-width:100%}</style><h1>Saved held-out prediction illustrations</h1><p>Seed42, all outer folds. Post-hoc examples are explanatory only and cannot tune any model. Fixed central crops are not object detections.</p>'+''.join(pages))
        write(root/'SELECTION_AND_PREDICTIONS.json',selection);write(root/'ASSET_MANIFEST.json',manifest)
        write(root/'COMPLETE.json',{'condition':condition,'examples':len(selection),'prediction_files':{str(p.relative_to(PROJECT.parent)):sha(p) for p in sorted(base.glob('outer*/predictions.json'))}})
