"""Actual four-view, label-blinded diagnostic gallery; no inferred binary labels."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import html
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from source_audit import ROOT,REPO,RUN,write
from acquire_pilot import CAMERAS

GALLERY=ROOT/'04_visual_failure_review/galleries/blinded_pilot_v1'
FFMPEG=next(p for p in (REPO/'MILLING DATASET/.tools').rglob('ffmpeg-*') if p.is_file() and p.stat().st_mode&0o111)
# Fixed broad task-board interaction crops, applied identically across examples.
CROP={'cam_high':(.08,.12,.95,.95),'cam_low':(.1,.06,.98,.8),
      'cam_left_wrist':(.05,.05,.95,.95),'cam_right_wrist':(.05,.05,.95,.95)}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def command(args,log):
 r=subprocess.run([str(FFMPEG),'-nostdin','-hide_banner',*args],capture_output=True,text=True,cwd=REPO)
 log.parent.mkdir(parents=True,exist_ok=True);log.write_text(r.stderr)
 assert r.returncode==0,'FFmpeg failed; inspect '+str(log.relative_to(REPO))
 return r.stderr


def sheet(images,labels,path,title):
 canvas=Image.new('RGB',(960,840),'white');draw=ImageDraw.Draw(canvas);draw.text((8,8),title,fill='black')
 for k,(p,label) in enumerate(zip(images,labels)):
  image=Image.open(p).convert('RGB');image.thumbnail((232,174))
  x=(k%4)*240;y=40+(k//4)*200;canvas.paste(image,(x+(240-image.width)//2,y))
  draw.text((x+4,y+176),label,fill='black')
 canvas.save(path)


def decode_view(job):
 masked,row,numerical,camera=job;name=camera.rsplit('.',1)[1];dest=GALLERY/masked/name;dest.mkdir(parents=True,exist_ok=True)
 v=numerical['video_metadata'][camera]
 original=Path(row['local_root'])/f'videos/{camera}/chunk-{v["chunk_index"]:03d}/file-{v["file_index"]:03d}.mp4'
 frames=pd.read_parquet(REPO/numerical['projection_path'])
 native_indices=np.rint(np.linspace(row['window_start_frame'],row['window_end_frame_exclusive']-1,16)).astype(int)
 assert len(np.unique(native_indices))==16
 timestamps=frames.timestamp.to_numpy(float)[native_indices]
 global_indices=round(v['from_timestamp']*30)+native_indices;base=max(0,int(global_indices[0])-1)
 expression='+'.join('eq(n,'+str(int(i)-base)+')' for i in global_indices)
 expression=expression.replace(',',r'\,')
 log=RUN/'logs/decoding'/f'{masked}_{name}_frames.log'
 marker=dest/'VIEW_COMPLETE.json'
 if marker.exists():return json.loads(marker.read_text())
 full=sorted(dest.glob('frame_*_full.png'))
 if len(full)!=16:
  assert len(full)==0,'Partial frame output must be inspected; never overwrite generated evidence silently'
  text=command(['-loglevel','info','-threads','2','-c:v','libdav1d','-ss',f'{max(0,base/30-.00001):.8f}',
    '-t',f'{(int(global_indices[-1])-base+2)/30:.8f}','-copyts','-i',str(original),'-vf',f'select={expression},showinfo',
    '-fps_mode','vfr','-frames:v','16',str(dest.relative_to(REPO)/'frame_%02d_full.png')],log)
 else:text=log.read_text()
 actual=np.array([float(x) for x in re.findall(r'\bn:\s*\d+.*?pts_time:([-+0-9.eE]+)',text)])
 assert len(actual)==16 and np.max(abs(actual-global_indices/30))<1e-5
 full=sorted(dest.glob('frame_*_full.png'));assert len(full)==16
 contexts=[];records=[]
 for k,(path,frame_index,pts,when) in enumerate(zip(full,native_indices,actual,timestamps),1):
  image=Image.open(path).convert('RGB');w,h=image.size;roi=CROP[name];box=(round(roi[0]*w),round(roi[1]*h),round(roi[2]*w),round(roi[3]*h))
  out=path.with_name(f'frame_{k:02d}_context.png')
  image.crop(box).resize((640,480),Image.Resampling.LANCZOS).save(out);contexts.append(out)
  records.append({'masked_id':masked,'camera':name,'frame_order':k-1,'native_frame_index':int(frame_index),
   'native_timestamp_s':float(when),'source_video_pts_s':float(pts),'expected_source_video_pts_s':float(v['from_timestamp']+when),
   'source_video':str(original),'source_episode':row['episode_index'],'repo_id':row['repo_id'],'revision':row['revision'],
   'full_frame':str(path.relative_to(REPO)),'full_png_sha256':sha(path),
   'decoded_RGB24_sha256':hashlib.sha256(image.tobytes()).hexdigest(),'context_frame':str(out.relative_to(REPO)),'context_crop_box_xyxy':box,
   'context_png_sha256':sha(out),'frame_level_binary_label':None})
 labels=[f'frame {i}; t={t:.3f}s' for i,t in zip(native_indices,timestamps)]
 sheet(full,labels,dest/'full_sequence.png',masked+' / '+name+' / original full camera view')
 sheet(contexts,labels,dest/'context_sequence.png',masked+' / '+name+' / fixed enlarged interaction region')
 clip=dest/'preview.mp4';start=(round(v['from_timestamp']*30)+row['window_start_frame'])/30
 duration=(row['window_end_frame_exclusive']-row['window_start_frame'])/30
 if not clip.exists():
  command(['-loglevel','error','-threads','2','-c:v','libdav1d','-ss',f'{start:.8f}','-i',str(original),'-t',f'{duration:.8f}',
   '-an','-c:v','libx264','-preset','ultrafast','-crf','23','-threads','2','-movflags','+faststart',str(clip.relative_to(REPO))],RUN/'logs/decoding'/f'{masked}_{name}_clip.log')
 result={'masked_id':masked,'camera':name,'source_video':str(original),'source_revision':row['revision'],'source_episode':row['episode_index'],
  'records':records,'maximum_encoded_PTS_residual_seconds':float(np.max(abs(actual-(v['from_timestamp']+timestamps)))),
  'distinct_native_frame_indices':len(set(native_indices)),'distinct_decoded_RGB_contents':len({r['decoded_RGB24_sha256'] for r in records}),
  'preview':str(clip.relative_to(REPO)),'preview_sha256':sha(clip),'preview_is_reencoded_review_derivative':True,
  'fixed_context_crop':CROP[name],'hardware_exposure_synchronization_independently_verified':False}
 write(marker,result);print('DECODED',masked,name,'RGB_contents',result['distinct_decoded_RGB_contents'],flush=True)
 return result


def main():
 selected=json.loads((ROOT/'00_dataset_overview/PILOT_SELECTION.json').read_text())
 numeric=json.loads((ROOT/'03_video_sensor_alignment/NUMERICAL_ACQUISITION_MANIFEST.json').read_text())
 lookup={(r['repo_id'],r['episode_index']):r for r in numeric}
 rng=np.random.default_rng(20261028);order=rng.permutation(len(selected));jobs=[];key=[]
 GALLERY.mkdir(parents=True,exist_ok=True)
 for rank,index in enumerate(order,1):
  row=selected[index];masked=f'B{rank:03d}';n=lookup[(row['repo_id'],row['episode_index'])]
  key.append({'masked_id':masked,**row})
  for cam in CAMERAS:jobs.append((masked,row,n,cam))
  data=pd.read_parquet(REPO/n['projection_path']);state=np.stack(data['observation.state']);action=np.stack(data['action'])
  ix=np.arange(row['window_start_frame'],row['window_end_frame_exclusive']);t=data.timestamp.to_numpy(float)
  fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True,layout='constrained')
  for arm,ax in enumerate(axes):
   for j in range(7):ax.plot(t[ix],state[ix,7*arm+j],label=f'joint/actuator {j}')
   for when in t[np.rint(np.linspace(ix[0],ix[-1],16)).astype(int)]:ax.axvline(when,color='grey',alpha=.15)
   ax.set_ylabel('Released position values\nunits not declared');ax.legend(ncol=4,fontsize=7);ax.grid(alpha=.2)
  axes[-1].set_xlabel('Original episode timestamp (s)');axes[0].set_title(masked+' / observation.state; left and right arms / no outcome label shown')
  dest=GALLERY/masked;dest.mkdir(exist_ok=True);fig.savefig(dest/'sensor_timeline.png',dpi=120);plt.close(fig)
 write(ROOT/'04_visual_failure_review/UNBLINDING_KEY.json',{'random_seed':20261028,'examples':key,'binary_targets_verified':False,
    'warning':'Collection/annotation status is shown after review; these are not certified normal/failure labels or matched pairs.'})
 results=[]
 with ThreadPoolExecutor(max_workers=3) as pool:
  for result in pool.map(decode_view,jobs):results.append(result);write(ROOT/'03_video_sensor_alignment/FOUR_VIEW_DECODE_AUDIT.json',results)
 allframes=[r for view in results for r in view['records']]
 pd.DataFrame(allframes).to_csv(ROOT/'03_video_sensor_alignment/SELECTED_FRAME_MANIFEST.csv',index=False)
 reviews=[];sections=[];revealed=[]
 for item in key:
  masked=item['masked_id'];sections.append(f'<section><h2>{masked}</h2><p>Object: 16 mm cylinder. Intended target: matching cylindrical fixture on the assembly task board. Identify the actual object/target and any occlusion from these views; no image-level damage annotation is claimed.</p>')
  sections.append(f'<img loading="lazy" width="800" src="{masked}/sensor_timeline.png" alt="Original numerical robot positions">')
  for camera in [c.rsplit('.',1)[1] for c in CAMERAS]:
   sections.append(f'<details><summary>{masked} — {camera}: motion, full view and enlarged context</summary><video controls preload="none" width="640" src="{masked}/{camera}/preview.mp4"></video><p>Review derivative; original videos and timestamps are preserved separately.</p><img loading="lazy" width="960" src="{masked}/{camera}/full_sequence.png"><img loading="lazy" width="960" src="{masked}/{camera}/context_sequence.png"></details>')
   reviews.append({'masked_id':masked,'camera':camera,'reviewer_id':'','review_date':'','object_and_target_identified':'','observed_motion_phase':'',
    'failure_visible_yes_no_uncertain':'','observed_failure_description':'','estimated_event_start_s':'','estimated_event_end_s':'',
    'visibility_confidence_1_to_5':'','occlusion_none_partial_full':'','force_only_or_visually_ambiguous':'','camera_usefulness':'','notes':''})
  sections.append('</section>')
  annotation=item['native_annotation'];revealed.append('<h2>'+masked+'</h2><p>'+html.escape(item['label_status'])+'</p><pre>'+html.escape(json.dumps(item,indent=2))+'</pre>')
 style='<meta charset="utf-8"><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}section{border-top:2px solid #aaa;margin-top:2rem}img{max-width:100%;height:auto}video{max-width:100%}summary{padding:1rem;cursor:pointer}pre{white-space:pre-wrap}</style>'
 (GALLERY/'index.html').write_text(style+'<title>REBOOT blinded diagnostic review</title><h1>REBOOT: blinded diagnostic review</h1><p>Randomized source ordering; class labels and source collection identities are not embedded in this initial gallery. This is a feasibility review, not a controlled blinded accuracy experiment: windows are not verified phase-matched and their durations differ. Complete the review sheet before opening the separate label key.</p><p><a href="../../RESEARCHER_VISUAL_REVIEW_SHEET.csv">Blank researcher review sheet</a> · <a href="../../UNBLINDED_LABEL_KEY.html">Reveal native annotation and source identities after review</a></p>'+''.join(sections))
 (ROOT/'04_visual_failure_review/UNBLINDED_LABEL_KEY.html').write_text(style+'<title>REBOOT native annotation key</title><h1>Native source annotation and identity key</h1><p>These source records have known integrity limitations. Recovery collection membership does not label an entire trial or interval as failed. Expert-name membership does not certify a negative phase. Human visibility review is pending.</p>'+''.join(revealed))
 pd.DataFrame(reviews).to_csv(ROOT/'04_visual_failure_review/RESEARCHER_VISUAL_REVIEW_SHEET.csv',index=False)
 write(ROOT/'04_visual_failure_review/GALLERY_COMPLETE.json',{'examples':len(key),'camera_views':len(results),'selected_frames':len(allframes),
  'masked_order_random_seed':20261028,'human_certified_visibility_judgments':0,'binary_training_eligible':0,
  'decoder_path':str(FFMPEG.relative_to(REPO)),'decoder_sha256':sha(FFMPEG),
  'minimum_distinct_RGB_contents_per_view':min(r['distinct_decoded_RGB_contents'] for r in results),
  'maximum_nominal_dataset_to_encoded_PTS_residual_seconds':max(r['maximum_encoded_PTS_residual_seconds'] for r in results)})
 print('GALLERY_COMPLETE',len(key),len(results),len(allframes),flush=True)


if __name__=='__main__':main()
