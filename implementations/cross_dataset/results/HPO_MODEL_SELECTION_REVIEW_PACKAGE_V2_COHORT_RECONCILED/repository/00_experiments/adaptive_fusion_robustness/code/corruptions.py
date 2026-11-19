"""Deterministic native-input perturbations; no fitted state or labels used."""
import math
import numpy as np
from scipy.ndimage import gaussian_filter
from common import signature,config


def rng(seed,key,family,identity=''):
    digest=signature({'seed':int(seed),'sample_key':list(key),'family':family,'identity':identity})
    return np.random.default_rng(int(digest[:16],16))

def remove_count(n,fraction):
    if n<=1:raise ValueError('INSUFFICIENT_SUPPORT')
    return min(n-1,max(1,math.floor(fraction*n+.5)))

def survivors(n,fraction,seed,key,family):
    removed=rng(seed,key,family).permutation(n)[:remove_count(n,fraction)]
    return np.array([i for i in range(n) if i not in set(removed)],int),removed

def image_fault(image,family,severity,seed,key,frame_id):
    original=np.asarray(image)
    x=original.astype('float32')/255. if original.dtype==np.uint8 else original.astype('float32').copy()
    assert x.ndim==3 and x.shape[2]==3 and np.isfinite(x).all() and x.min()>=0 and x.max()<=1
    if severity==0 or family=='clean':return x,{'clipped_fraction':0.,'rms_change':0.}
    if family=='image_noise':
        z=rng(seed,key,family,int(frame_id)).standard_normal(x.shape).astype('float32')
        raw=x+np.float32(severity)*z;out=np.clip(raw,0,1)
        clipped=float(np.mean((raw<0)|(raw>1)))
    elif family=='image_blur':
        out=gaussian_filter(x,sigma=(severity,severity,0),radius=(math.ceil(3*severity),math.ceil(3*severity),0),mode='reflect');clipped=0.
    else:raise ValueError(family)
    return out.astype('float32'),{'clipped_fraction':clipped,'rms_change':float(np.sqrt(np.mean((out-x)**2))),'native_shape':list(x.shape)}

def time_bounds(start,end,fraction,seed,key):
    center=float(rng(seed,key,'sensor_time_loss').uniform(.25,.75))
    return start+(center-fraction/2)*(end-start),start+(center+fraction/2)*(end-start)

def sensor_fault(streams,names,family,severity,seed,key,start,end,scales=None):
    """streams: list(name,timestamps,values), each values is native time x channels."""
    output=[];count=0;affected=[];total_channels=sum(x.shape[1] for _,_,x in streams)
    missing_indices=set()
    if family=='sensor_channel_loss':
        _,lost=survivors(total_channels,severity,seed,key,family);missing_indices=set(lost.tolist());affected=[names[i] for i in sorted(missing_indices)]
    bounds=time_bounds(start,end,severity,seed,key) if family=='sensor_time_loss' else None
    offset=0
    for stream,t,x in streams:
        y=x.copy();inside=(t>=start)&(t<=end);mask=np.zeros(x.shape,dtype=bool)
        for col in range(x.shape[1]):
            index=offset+col;valid=inside&np.isfinite(x[:,col])
            if family=='sensor_noise':
                scale=float(scales[index])
                if not np.isfinite(scale):raise ValueError('UNDEFINED_RAW_TRAINING_SCALE')
                draw=rng(seed,key,family,names[index]).standard_normal(len(t))
                y[valid,col]+=severity*scale*draw[valid];count+=int(valid.sum())
            elif family=='sensor_channel_loss' and index in missing_indices:mask[inside,col]=True
            elif family=='sensor_time_loss':mask[inside&(t>=bounds[0])&(t<=bounds[1]),col]=True
            elif family not in ('clean','sensor_channel_loss','sensor_time_loss'):raise ValueError(family)
        y[mask]=np.nan;count+=int(mask.sum());offset+=x.shape[1]
        assert np.array_equal(y[~inside],x[~inside],equal_nan=True)
        output.append((stream,t.copy(),y,mask))
    return output,{'affected_native_values':count,'affected_channels':affected,'time_bounds':list(bounds) if bounds else None,'channels_remaining':total_channels-len(missing_indices)}

def resample(t,x,start,end,positions=512,explicit_mask=None,time_block=None):
    """Original within-interval linear/gap policy plus non-bridging fault masks."""
    t=np.asarray(t,dtype='float64');x=np.asarray(x,float)
    assert t.ndim==1 and np.isfinite(t).all() and np.all(np.diff(t)>0)
    if x.ndim==1:x=x[:,None]
    indices=np.flatnonzero((t>=start)&(t<=end));grid=np.linspace(start,end,positions);out=np.full((positions,x.shape[1]),np.nan)
    native=np.median(np.diff(t)) if len(t)>1 else 0
    for col in range(x.shape[1]):
        valid=indices[np.isfinite(x[indices,col])]
        if len(valid)<2:continue
        tv=t[valid];v=np.interp(grid,tv,x[valid,col],left=np.nan,right=np.nan);right=np.searchsorted(tv,grid,side='left')
        slots=np.flatnonzero((right>0)&(right<len(tv)));rr=right[slots]
        gap=(tv[rr]-tv[rr-1]>5*native)&(grid[slots]!=tv[rr]);v[slots[gap]]=np.nan
        if explicit_mask is not None:
            # Even a short deliberately missing region must not be interpolated.
            masked_times=t[np.asarray(explicit_mask)[:,col]]
            if len(masked_times):
                for a,b,k in zip(tv[:-1],tv[1:],range(len(tv)-1)):
                    if np.any((masked_times>a)&(masked_times<b)):v[(grid>a)&(grid<b)]=np.nan
        if time_block is not None:v[(grid>=time_block[0])&(grid<=time_block[1])]=np.nan
        out[:,col]=v
    return out

def _original_statistics(x):
    # Preserve dtype and memory layout: the saved pipeline reduces float32 arrays.
    q=np.nanquantile(x,[.25,.5,.75],axis=0);lo,hi=np.nanmin(x,axis=0),np.nanmax(x,axis=0)
    t=np.linspace(0,1,len(x))[:,None];valid=np.isfinite(x);n=valid.sum(0);tx=np.where(valid,t,0).sum(0)/np.maximum(n,1)
    xm=np.nanmean(x,axis=0);tc=t-tx;slope=np.nansum(tc*(x-xm),0)/np.maximum(np.where(valid,tc**2,0).sum(0),1e-12)
    return np.concatenate([xm,np.nanstd(x,axis=0),q[1],lo,hi,q[0],q[2],hi-lo,np.sqrt(np.nanmean(x*x,0)),slope]).astype('float32')

def statistics(x):
    """Exact original clean reductions; unsupported fault channels emit NaNs."""
    x=np.asarray(x);supported=np.isfinite(x).any(0)
    if supported.all():return _original_statistics(x)
    result=np.full((10,x.shape[1]),np.nan,dtype='float32')
    if supported.any():result[:,supported]=_original_statistics(x[:,supported]).reshape(10,-1)
    return result.ravel()

def statistics_for(streams,start,end,time_block=None):
    x=np.concatenate([resample(t,x,start,end,explicit_mask=mask,time_block=time_block) for _,t,x,mask in streams],axis=1).astype('float32')
    return statistics(x)

def routing(pv,ps,stacker,visual_available=True,sensor_available=True):
    from scipy.special import expit
    if not visual_available and not sensor_available:raise ValueError('UNAVAILABLE_ABSTAIN')
    if not visual_available:return float(ps),'sensor_only_fallback'
    if not sensor_available:return float(pv),'visual_only_fallback'
    return float(expit(stacker['intercept']+np.dot(stacker['coefficient'],[pv,ps]))),'F2'

def schedule():
    c=config();jobs=[dict(family='clean',level='clean',severity=0.,repeat=0,seed=None)]
    # Gaussian families paired by repeat and level, each block spans all folds.
    for repeat,seed in enumerate(c['realization_seeds'],1):
        for i,level in enumerate(['mild','medium','strong']):
            for family in ['image_noise','sensor_noise']:jobs.append(dict(family=family,level=level,severity=c[family][i],repeat=repeat,seed=seed))
    for family in ['image_blur','frame_loss','sensor_channel_loss','sensor_time_loss']:
        for i,level in enumerate(['mild','medium','strong']):
            for repeat,seed in ([(0,None)] if family=='image_blur' else list(enumerate(c['realization_seeds'],1))):jobs.append(dict(family=family,level=level,severity=c[family][i],repeat=repeat,seed=seed))
    for missing in ['image_absent','sensor_absent']:jobs.append(dict(family='missing_modality',level=missing,severity=1.,repeat=0,seed=None))
    assert len(jobs)==51
    return jobs
