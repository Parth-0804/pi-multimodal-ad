"""Outcome-independent Section 1 representations; immutable source inputs."""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path
import cv2
import h5py
import numpy as np
import pandas as pd
import torch
from transformers import RTDetrForObjectDetection, RTDetrImageProcessor
from .alignment import timestamps_1d, interval_indices, resample_progress


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def cohort(config):
    f=pd.read_parquet(Path(config['audit_run'])/'tables_v2/cohort.parquet')
    f=f.loc[f.primary_task & f.dual_complete].copy().reset_index(drop=True)
    assert len(f)==4530 and f.failure.sum()==509 and f.recording_id.nunique()==148
    assert not f.duplicated(['recording_id','segment_id']).any()
    return f


def statistics(x):
    """Per-segment channel statistics; no fitted population quantities."""
    q=np.nanquantile(x,[.25,.5,.75],axis=0)
    lo,hi=np.nanmin(x,axis=0),np.nanmax(x,axis=0)
    t=np.linspace(0,1,len(x))[:,None];valid=np.isfinite(x)
    n=valid.sum(0);tx=np.where(valid,t,0).sum(0)/np.maximum(n,1)
    xm=np.nanmean(x,axis=0);tc=t-tx
    slope=np.nansum(tc*(x-xm),0)/np.maximum(np.where(valid,tc**2,0).sum(0),1e-12)
    return np.concatenate([xm,np.nanstd(x,axis=0),q[1],lo,hi,q[0],q[2],hi-lo,np.sqrt(np.nanmean(x*x,0)),slope]).astype('float32')


def load_visual(config):
    v=config['visual'];folder=Path(config['data_root'])/'cache/section1_models'/v['revision'];folder.mkdir(parents=True,exist_ok=True)
    identities={}
    for name in ['config.json','preprocessor_config.json','model.safetensors']:
        p=folder/name
        if not p.exists():
            part=folder/(name+'.part')
            if part.exists():raise RuntimeError('Incomplete model download exists; preserve and inspect '+str(part))
            urllib.request.urlretrieve(f"https://huggingface.co/{v['model']}/resolve/{v['revision']}/{name}",part)
            part.rename(p)
        identities[name]={'sha256':sha(p),'size_bytes':p.stat().st_size}
    processor=RTDetrImageProcessor.from_pretrained(folder,local_files_only=True)
    model=RTDetrForObjectDetection.from_pretrained(folder,local_files_only=True).model.backbone.model.eval().cuda()
    model.requires_grad_(False)
    return processor,model,{'repo':v['model'],'revision':v['revision'],'files':identities,'processor':processor.to_dict(),'backbone_parameters':sum(p.numel() for p in model.parameters())}


def extract(config):
    torch.set_num_threads(config['threads']);cv2.setNumThreads(1)
    run=Path(config['run_dir']);out=run/'features';out.mkdir(exist_ok=True)
    f=cohort(config);root=Path(config['data_root']);rec=pd.read_parquet(Path(config['audit_run'])/'recordings.parquet').set_index('recording_id')
    processor,model,model_info=load_visual(config)
    p=run/'pretrained_model.json'
    if not p.exists():p.write_text(json.dumps(model_info,indent=2)+'\n')
    signature=hashlib.sha256((json.dumps(config,sort_keys=True)+sha(__file__)).encode()).hexdigest()
    start=time.time()
    for k,(rid,rows) in enumerate(f.groupby('recording_id',sort=True)):
        dest=out/(rid+'.npz');meta=out/(rid+'.json')
        if dest.exists():
            assert json.loads(meta.read_text())['signature']==signature,'Extraction code/config changed: use a fresh run'
            print('REUSED',k+1,148,rid,flush=True);continue
        source=root/'raw/data'/rec.loc[rid,'filename'];st=source.stat()
        assert st.st_size==int(rec.loc[rid,'size_bytes']) and st.st_mtime_ns==int(rec.loc[rid,'mtime_ns'])
        xs=[];ss=[];vs=[];frame_indices=[];names=[]
        video=root/'cache/encoded_media'/rec.loc[rid,'sha256']/'hand.mp4'
        cap=cv2.VideoCapture(str(video));assert cap.isOpened()
        with h5py.File(source,'r') as h:
            streams={n:(timestamps_1d(h['timestamps'][n][()]),np.asarray(h['robot_state'][n][()],dtype=np.float64)) for n in config['sensor']['channels']}
            vt=timestamps_1d(h['timestamps/hand'][()])
            assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==len(vt)
            for n,(_,x) in streams.items():names.extend([n+':'+str(i) for i in range(x.shape[1] if x.ndim==2 else 1)])
            for row in rows.itertuples():
                x=np.concatenate([resample_progress(t,a,row.start,row.end,512,5) for t,a in streams.values()],axis=1).astype('float32')
                assert np.isfinite(x).mean(axis=0).min()>=.89
                xs.append(x);ss.append(statistics(x))
                ii=interval_indices(vt,row.start,row.end);chosen=ii[np.linspace(0,len(ii)-1,16).round().astype(int)]
                assert len(np.unique(chosen))==16
                images=[]
                for index in chosen:
                    cap.set(cv2.CAP_PROP_POS_FRAMES,int(index));ok,img=cap.read()
                    if not ok:raise RuntimeError(f'Previously audited frame no longer decodes: {rid} {index}')
                    images.append(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
                batch=processor(images=images,return_tensors='pt')['pixel_values'].cuda()
                with torch.inference_mode(),torch.autocast('cuda',dtype=torch.float16):
                    maps=model(batch).feature_maps
                    z=torch.cat([m.float().mean((-2,-1)) for m in maps],dim=-1).mean(0)
                vs.append(z.cpu().numpy());frame_indices.append(chosen)
        cap.release()
        arrays={'row_index':rows.index.to_numpy(),'sensor':np.stack(xs),'statistics':np.stack(ss),'visual':np.stack(vs),'frame_indices':np.stack(frame_indices)}
        tmp=dest.with_suffix('.part.npz');np.savez_compressed(tmp,**arrays);tmp.rename(dest)
        meta.write_text(json.dumps({'signature':signature,'source_sha256':rec.loc[rid,'sha256'],'channel_names':names,'feature_sha256':sha(dest),'segments':len(rows),'visual_dim':arrays['visual'].shape[1]},indent=2)+'\n')
        print('EXTRACTED',k+1,148,rid,'segments',len(rows),'elapsed_s',round(time.time()-start,1),flush=True)
    f[['recording_id','segment_id','start','end','action','failure']].to_parquet(run/'cohort.parquet',index=False)
    print('FEATURES COMPLETE',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',default='configs/reassemble/section1.json');a=p.parse_args()
    extract(json.loads(Path(a.config).read_text()))

if __name__=='__main__':main()
