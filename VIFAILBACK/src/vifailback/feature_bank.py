"""Resumable small frozen feature bank; never persist a full decoded RGB dataset."""
import gc
import time
import numpy as np
import torch

from .common import PROJECT,config,disk_reserve,event,read,sha,signature,write,code_identity
from .cohort import finalize
from .visual import backbone,features,pixels
from .corruptions import visual_quality


def build(c=None,condition='V1',device='cpu'):
    c=c or config();rows=finalize(c)
    root=PROJECT/'03_preprocessing/visual_preprocessing/features'/c['run_id']/condition
    root.mkdir(parents=True,exist_ok=True)
    done=root/'COMPLETE.json'
    if done.exists():
        receipt=read(done);assert sha(root/'features.npy')==receipt['sha256']
        assert receipt['configuration_sha256']==signature(c) and receipt['implementation']==code_identity()
        return receipt
    path=root/'features.npy';shape=(len(rows),3,16,896)
    if path.exists():
        array=np.lib.format.open_memmap(path,mode='r+');assert array.shape==shape
    else:
        disk_reserve(c,int(np.prod(shape))*4)
        array=np.lib.format.open_memmap(path,mode='w+',dtype='float32',shape=shape)
    identity=signature({'episode_ids':[r['episode_index'] for r in rows],
                        'camera_sha256':[r['camera_sha256'] for r in rows],
                        'condition':condition,'config':c})
    progress=root/'PROGRESS.json';state=read(progress) if progress.exists() else {'next':0,'identity':identity}
    assert state['identity']==identity
    qpath=root/'quality.npy'
    quality=np.lib.format.open_memmap(qpath,mode='r+' if qpath.exists() else 'w+',dtype='float32',shape=(len(rows),6))
    cnn=backbone(c,condition,device);torch.set_num_threads(c['cpu_threads']);started=time.perf_counter();previous_seconds=state.get('cumulative_processing_seconds',0.)
    for i in range(state['next'],len(rows)):
        x=pixels(c,rows[i]).to(device)
        with torch.inference_mode():z=features(cnn,x,c['cnn_frame_chunk']).reshape(3,16,896)
        array[i]=z.cpu().numpy();array.flush();quality[i]=visual_quality(x);quality.flush()
        write(progress,{'next':i+1,'identity':identity,'cumulative_processing_seconds':previous_seconds+time.perf_counter()-started})
        if (i+1)%25==0:event(c,'FROZEN_FEATURE_BANK',condition=condition,episodes=i+1,total=len(rows),device=device)
    del array,quality,cnn;gc.collect()
    receipt={'path':str(path.relative_to(PROJECT.parent)),'sha256':sha(path),'identity':identity,
             'configuration_sha256':signature(c),'implementation':code_identity(),
             'shape':list(shape),'quality_sha256':sha(qpath),'device':device,'elapsed_this_resume_seconds':time.perf_counter()-started,
             'total_completed_processing_seconds':read(progress)['cumulative_processing_seconds'],
             'source':'original CNN' if condition!='V3' else 'verified donor CNN only',
             'preprocessing':'RGB bilinear640 /255, no image normalization',
             'pooling':'equal spatial/time/camera mean; keep per-frame features for label-blind frozen corruption controls'}
    write(done,receipt)
    return receipt


def pooled_bank(c,condition):
    high_only=condition=='V1_high_only'
    root=PROJECT/'03_preprocessing/visual_preprocessing/features'/c['run_id']/('V1' if high_only else condition)
    receipt=read(root/'COMPLETE.json');assert sha(root/'features.npy')==receipt['sha256']
    array=np.load(root/'features.npy',mmap_mode='r',allow_pickle=False)
    return pool(array,high_only),receipt


def pool(array,high_only=False):
    return np.asarray(array[:,0].mean(1) if high_only else array.mean((1,2)),dtype='float32')
