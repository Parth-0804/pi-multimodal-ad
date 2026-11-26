"""Fixed label-blind stress tests, never fitted to held-out outcomes."""
import warnings
import cv2
import numpy as np
import torch
from .common import signature

# Durations are episode-relative because no independent physical clock is known.
SCENARIOS=[{'name':'clean','visual':'none','sensor':'none','amount':0}]
for kind,amounts in [('missing_frames',[.25,.5]),('frame_drop_window',[.25,.5]),('blur',[5,15]),
                     ('occlusion',[.25,.5]),('camera_unavailable',[1,2]),('jpeg',[20,5]),('visual_shift',[.1,.25])]:
    SCENARIOS += [{'name':f'{kind}_{a}','visual':kind,'sensor':'none','amount':a} for a in amounts]
for kind,amounts in [('missing_channels',[.25,.5]),('missing_interval',[.2,.4]),('noise',[.5,1.]),
                     ('frozen_sensor',[1]),('sensor_shift',[.1,.25])]:
    SCENARIOS += [{'name':f'{kind}_{a}','visual':'none','sensor':kind,'amount':a} for a in amounts]
SCENARIOS += [{'name':'combined_partial','visual':'occlusion','sensor':'missing_channels','amount':.5},
              {'name':'visual_missing','visual':'all_missing','sensor':'none','amount':1},
              {'name':'sensor_missing','visual':'none','sensor':'all_missing','amount':1},
              {'name':'both_missing','visual':'all_missing','sensor':'all_missing','amount':1}]


def rng(episode,scenario):
    return np.random.default_rng(int(signature([20261029,int(episode),scenario['name']])[:16],16))


def visual_quality(x):
    """Input-only quality, computed identically for clean and corrupted frames."""
    images=np.rint(x.detach().cpu().numpy().transpose(0,1,3,4,2)*255).clip(0,255).astype('uint8')
    views=[]
    for camera in images:
        gray=np.stack([cv2.resize(cv2.cvtColor(f,cv2.COLOR_RGB2GRAY),(160,120),interpolation=cv2.INTER_AREA) for f in camera])
        brightness=gray.mean((1,2));contrast=gray.std((1,2));delta=np.abs(np.diff(gray.astype('float32'),axis=0)).mean((1,2))
        views.append([brightness.mean(),contrast.mean(),((brightness<3)&(contrast<2)).mean(),
                      np.median([cv2.Laplacian(f,cv2.CV_32F).var() for f in gray]),(delta<1e-6).mean(),delta.mean()])
    return np.mean(views,axis=0).astype('float32')


def alter_visual(x,episode,scenario):
    x=x.clone();kind=scenario['visual'];a=scenario['amount'];r=rng(episode,scenario)
    available=kind!='all_missing'
    if kind=='all_missing':x.zero_()
    elif kind=='missing_frames':
        index=r.choice(16,round(16*a),replace=False);x[:,index]=0
    elif kind=='frame_drop_window':
        n=round(16*a);start=int(r.integers(0,17-n));x[:,start:start+n]=0
    elif kind=='camera_unavailable':x[r.choice(3,int(a),replace=False)]=0
    elif kind=='visual_shift':
        offset=max(1,round(16*a));index=np.clip(np.arange(16)+offset,0,15);x=x[:,index]
    elif kind=='occlusion':
        h,w=x.shape[-2:];length=max(1,int(np.sqrt(a)*min(h,w)));top=int(r.integers(0,h-length+1));left=int(r.integers(0,w-length+1))
        x[:,:,:,top:top+length,left:left+length]=0
    elif kind in ['blur','jpeg']:
        array=np.rint(x.numpy().transpose(0,1,3,4,2)*255).clip(0,255).astype('uint8')
        for view in array:
            for i,f in enumerate(view):
                if kind=='blur':view[i]=cv2.GaussianBlur(f,(int(a),int(a)),0)
                else:
                    ok,encoded=cv2.imencode('.jpg',cv2.cvtColor(f,cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,int(a)])
                    assert ok;view[i]=cv2.cvtColor(cv2.imdecode(encoded,cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)
        x=torch.from_numpy(array.transpose(0,1,4,2,3).copy()).float()/255
    elif kind!='none':raise ValueError(kind)
    return x,available


def alter_sensor(values,episode,scenario,training_std):
    values=values.copy();r=rng(episode,scenario);kind=scenario['sensor'];a=scenario['amount'];available=kind!='all_missing'
    if kind=='all_missing':values[:]=np.nan
    elif kind=='missing_channels':values[:,r.choice(28,round(28*a),replace=False)]=np.nan
    elif kind=='missing_interval':
        n=max(1,round(len(values)*a));start=int(r.integers(0,len(values)-n+1));values[start:start+n]=np.nan
    elif kind=='noise':values+=r.normal(size=values.shape)*np.asarray(training_std)[None,:]*a
    elif kind=='frozen_sensor':values[:]=values[0]
    elif kind=='sensor_shift':values=values[np.clip(np.arange(len(values))+max(1,round(len(values)*a)),0,len(values)-1)]
    elif kind!='none':raise ValueError(kind)
    return values,available
