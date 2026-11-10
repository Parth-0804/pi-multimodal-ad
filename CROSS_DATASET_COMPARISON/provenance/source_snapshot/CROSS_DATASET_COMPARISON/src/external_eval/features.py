"""Resumable FP32 CNN-only caches, with real RGB corruption before extraction."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
import cv2
import numpy as np
import pandas as pd
import torch
from msm.models import verified_backbone
from msm.transfer import transfer_completed_cnn
from msm.data import letterbox_rgb
from external_eval.io import write_json,sha,utc


def variants(config):
    rows=[('clean','clean',None)]
    for key in ['gaussian_blur','brightness_contrast','partial_occlusion']:
        rows.extend((key+'_'+str(i+1),key,value) for i,value in enumerate(config['corruptions'][key]))
    return rows


def content_box(bgr,sar,size=640):
    h,w=bgr.shape[:2];display_w=round(w*sar[0]/sar[1]);scale=size/max(h,display_w)
    tw,th=round(display_w*scale),round(h*scale)
    return (size-tw)//2,(size-th)//2,tw,th


def altered(image,box,kind,value):
    out=image.copy();left,top,w,h=box;part=out[top:top+h,left:left+w]
    if kind=='gaussian_blur':
        k=int(np.ceil(value*6))|1;part[:]=cv2.GaussianBlur(part,(k,k),sigmaX=value,sigmaY=value)
    elif kind=='brightness_contrast':
        brightness,contrast=value
        part[:]=np.clip(((part.astype(np.float32)-127.5)*contrast+127.5)*brightness,0,255).round().astype(np.uint8)
    elif kind=='partial_occlusion':
        ow=max(1,round(w*np.sqrt(value)));oh=max(1,round(h*np.sqrt(value)))
        x=(w-ow)//2;y=(h-oh)//2;part[y:y+oh,x:x+ow]=0
    elif kind!='clean':raise ValueError('Unknown pixel corruption')
    return out


def quality(image,box):
    x,y,w,h=box;part=image[y:y+h,x:x+w]
    gray=cv2.cvtColor(part,cv2.COLOR_RGB2GRAY)
    return np.array([gray.mean()/255,gray.std()/255,np.log1p(cv2.Laplacian(gray,cv2.CV_64F).var()),
        np.mean(gray<13),np.mean(gray>242)],np.float32)


class Decoder:
    def __init__(self):self.cap=None;self.path=None;self.index=0
    def close(self):
        if self.cap is not None:self.cap.release()
        self.cap=None;self.path=None;self.index=0
    def frames(self,row,expected):
        path=row['video_file'];indices=json.loads(row['frame_indices_json']);timestamps=json.loads(row['video_pts_s_json'])
        if self.path!=path:
            self.close();self.cap=cv2.VideoCapture(path,cv2.CAP_FFMPEG,[cv2.CAP_PROP_N_THREADS,1]);self.path=path
            if not self.cap.isOpened():raise ValueError('Source video cannot open')
        if indices[0]<self.index:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,int(indices[0]));self.index=indices[0]
        elif self.index==0 and indices[0]>90:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,int(indices[0]));self.index=indices[0]
        pixels=[];boxes=[]
        for j,pts in zip(indices,timestamps):
            while self.index<=j:
                if not self.cap.grab():raise ValueError('Missing native source frame')
                this=self.index;self.index+=1
                if this==j:
                    ok,image=self.cap.retrieve()
                    if not ok:raise ValueError('Native source frame decode failed')
            actual=self.cap.get(cv2.CAP_PROP_POS_MSEC)/1000
            if abs(actual-pts)>1e-6 or hashlib.sha256(image.tobytes()).hexdigest()!=expected[j]:
                raise ValueError('Source native frame hash/PTS mismatch')
            sar=(int(row.get('sar_num',1)),int(row.get('sar_den',1)))
            boxes.append(content_box(image,sar));pixels.append(letterbox_rgb(image,sar))
        return pixels,boxes


def run(dataset,condition='P'):
    root=Path(dataset);config=json.loads((root/'04_experiment_protocol/experiment_config.json').read_text())
    frame=pd.read_csv(root/'03_processed_model_inputs/final_sample_manifest.csv').sort_values(['video_file','start_s']).reset_index(drop=True)
    selected=pd.read_csv(root/'02_labels_and_alignment/alignment_manifest.csv')
    # Every frame's source hash was verified during data admission and again here.
    id_col='sample_id' if 'sample_id' in selected else 'interval_id'
    hashes={}
    for ident,g in selected.groupby(id_col):hashes[ident]={int(r.native_frame_index):r.decoded_frame_sha256 for r in g.itertuples()}
    out=root/'03_processed_model_inputs/visual_features'/condition;out.mkdir(parents=True,exist_ok=True)
    identity_path=out/'identity.json'
    options=variants(config)
    signature=hashlib.sha256(json.dumps({'dataset':dataset,'condition':condition,'frame_manifest':sha(root/'02_labels_and_alignment/alignment_manifest.csv'),
        'source':sha(__file__),'options':options,'preprocessing':'Stage3 letterbox_rgb640 RGB /255 FP32 no normalization',
        'revision':config['pretrained_revision'],'microbatch':config['cnn_microbatch']},sort_keys=True).encode()).hexdigest()
    if identity_path.exists() and json.loads(identity_path.read_text())['signature']!=signature:raise ValueError('Feature cache identity mismatch')
    torch.set_num_threads(1);cv2.setNumThreads(1);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
    free,total=torch.cuda.mem_get_info()
    if free<config['gpu_free_reserve_mib']*1024**2:raise RuntimeError('GPU reserve gate blocked; other jobs preserved')
    torch.cuda.set_per_process_memory_fraction(min(.12,config['gpu_process_cap_mib']*1024**2/total))
    legacy=config['msm_stage3_configuration']
    _,backbone,weight_identity=verified_backbone(legacy)
    transfer=None
    if condition=='R':transfer=transfer_completed_cnn(backbone,config['source_R']['folder'],42,4)
    elif condition!='P':raise ValueError('Unknown source condition')
    backbone.eval().requires_grad_(False)
    if not identity_path.exists():write_json(identity_path,{'signature':signature,'condition':condition,'options':options,'weight_identity':weight_identity,
        'transfer':transfer,'created_utc':utc(),'feature_shape_per_example':[len(options),16,896],
        'GPU':torch.cuda.get_device_name(),'tensor_memory_cap_bytes':int(min(.12*total,config['gpu_process_cap_mib']*1024**2))})
    before=time.perf_counter();decoder=Decoder();new_count=0;times=[]
    try:
        for n,row in enumerate(frame.to_dict('records')):
            ident=row['sample_id'];key=hashlib.sha256(ident.encode()).hexdigest()[:24];dest=out/(key+'.npz')
            if dest.exists():
                with np.load(dest,allow_pickle=False) as z:
                    if str(z['signature'])!=signature or str(z['sample_id'])!=ident or z['features'].shape!=(len(options),16,896):raise ValueError('Existing cache differs')
                continue
            free,_=torch.cuda.mem_get_info()
            if free<config['gpu_free_reserve_mib']*1024**2:raise RuntimeError('GPU reserve consumed by another job; partial cache preserved')
            started=time.perf_counter();pixels,boxes=decoder.frames(row,hashes[ident]);decode_s=time.perf_counter()-started
            values=[];qualities=[];forward_s=0
            for _,kind,value in options:
                images=[altered(image,box,kind,value) for image,box in zip(pixels,boxes)]
                qualities.append(np.stack([quality(im,box) for im,box in zip(images,boxes)]))
                batch=torch.from_numpy(np.stack(images)).permute(0,3,1,2).contiguous()
                chunks=[];start_gpu=time.perf_counter()
                with torch.inference_mode():
                    for chunk in batch.split(config['cnn_microbatch']):
                        maps=backbone(chunk.to('cuda',dtype=torch.float32).div_(255)).feature_maps
                        chunks.append(torch.cat([m.float().mean((-2,-1)) for m in maps],dim=1).cpu().numpy())
                torch.cuda.synchronize();forward_s+=time.perf_counter()-start_gpu
                values.append(np.concatenate(chunks))
            features=np.stack(values).astype(np.float32);q=np.stack(qualities)
            assert features.shape==(len(options),16,896) and np.isfinite(features).all() and np.isfinite(q).all()
            part=dest.with_suffix('.writing.npz')
            with part.open('xb') as f:
                np.savez_compressed(f,features=features,quality=q,sample_id=ident,signature=signature,
                    frame_indices=np.array(json.loads(row['frame_indices_json'])),video_pts=np.array(json.loads(row['video_pts_s_json'])),
                    option_names=np.array([x[0] for x in options]),decode_seconds=decode_s,forward_seconds=forward_s)
                f.flush();os.fsync(f.fileno())
            os.link(part,dest)
            times.append(time.perf_counter()-started);new_count+=1
            if new_count%5==0 or n+1==len(frame):
                print(dataset,condition,n+1,'/',len(frame),'new',new_count,'last_s',round(times[-1],2),
                    'frames/s',round(new_count*16*len(options)/(time.perf_counter()-before),2),
                    'peakMiB',round(torch.cuda.max_memory_allocated()/1024**2),flush=True)
    finally:decoder.close()
    # Store ordered cache identities once complete; it is safe to resume prior examples.
    index=[]
    for row in frame.to_dict('records'):
        p=out/(hashlib.sha256(row['sample_id'].encode()).hexdigest()[:24]+'.npz')
        index.append({'sample_id':row['sample_id'],'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
    write_json(out/'cache_index.json',index)
    write_json(out/'complete.json',{'signature':signature,'examples':len(frame),'conditions':len(options),'new_examples_this_invocation':new_count,
        'wall_seconds_this_invocation':time.perf_counter()-before,'frames_forwarded_this_invocation':new_count*16*len(options),
        'peak_allocated_mib':torch.cuda.max_memory_allocated()/1024**2,'peak_reserved_mib':torch.cuda.max_memory_reserved()/1024**2,
        'GPU':torch.cuda.get_device_name(),'shared_gpu':True,'device_utilization_is_not_our_utilization':True,'finished_utc':utc()})
    print(dataset,condition,'FEATURES COMPLETE',len(frame),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',choices=['MSM','HANDOVER'],required=True);p.add_argument('--condition',default='P');a=p.parse_args();run(a.dataset,a.condition)
