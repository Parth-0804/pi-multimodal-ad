"""Exact no-bridge mask acceleration for run_02; unchanged clean input path."""
import numpy as np
import corruptions
_original_resample=corruptions.resample


def resample(t,x,start,end,positions=512,explicit_mask=None,time_block=None):
    if explicit_mask is None or not np.asarray(explicit_mask).any():
        return _original_resample(t,x,start,end,positions,explicit_mask,time_block)
    t=np.asarray(t,dtype='float64');x=np.asarray(x,float)
    assert t.ndim==1 and np.isfinite(t).all() and np.all(np.diff(t)>0)
    if x.ndim==1:x=x[:,None]
    indices=np.flatnonzero((t>=start)&(t<=end));grid=np.linspace(start,end,positions)
    out=np.full((positions,x.shape[1]),np.nan)
    native=np.median(np.diff(t)) if len(t)>1 else 0
    for col in range(x.shape[1]):
        valid=indices[np.isfinite(x[indices,col])]
        if len(valid)<2:continue
        tv=t[valid];v=np.interp(grid,tv,x[valid,col],left=np.nan,right=np.nan)
        right=np.searchsorted(tv,grid,side='left');slots=np.flatnonzero((right>0)&(right<len(tv)));rr=right[slots]
        gap=(tv[rr]-tv[rr-1]>5*native)&(grid[slots]!=tv[rr]);v[slots[gap]]=np.nan
        masked_times=t[np.asarray(explicit_mask)[:,col]]
        if len(masked_times):
            # Exactly the original strict test: any masked time in (a,b).
            before_b=np.searchsorted(masked_times,tv[1:],side='left')
            through_a=np.searchsorted(masked_times,tv[:-1],side='right')
            forbidden=before_b>through_a
            inside_edge=(grid[slots]>tv[rr-1])&(grid[slots]<tv[rr])
            v[slots[forbidden[rr-1]&inside_edge]]=np.nan
        if time_block is not None:v[(grid>=time_block[0])&(grid<=time_block[1])]=np.nan
        out[:,col]=v
    return out


_bindings={}

def fold_binding(selected,fold):
    from common import REPO,read,signature
    parts=selected['components'][fold];key=signature(parts)
    if key not in _bindings:
        _bindings[key]={
            'visual_fit_id':read(REPO/parts['visual_complete']['path'])['fit_id'],
            'sensor_fit_id':read(REPO/parts['sensor_complete']['path'])['fit_id'],
            'stacker_fit_id':read(REPO/parts['stacker']['path'])['fit_id']}
    return _bindings[key]


def install():
    from common import RUN,REPO,read,write,local,sha
    import shutil,inference,selection
    assert RUN.name=='run_02','ADAPTER_IS_RUN_02_ONLY'
    corruptions.resample=resample
    original_cache=inference.cache_frames
    def checked_cache(path,features,identity):
        original_cache(path,features,identity)
        np.testing.assert_array_equal(np.load(path,allow_pickle=False),features)
        record=read(path.with_suffix('.json'));record['live_cache_bitwise_equal']=True
        write(path.with_suffix('.json'),record)
    inference.cache_frames=checked_cache
    original_row=inference.row
    def identified_row(sample,fold,selected,job,*args,**kwargs):
        record=original_row(sample,fold,selected,job,*args,**kwargs)
        record.update(fold_binding(selected,fold));return record
    inference.row=identified_row
    original_select=selection.select
    def select_with_component_evidence():
        selected=original_select();summary={}
        for fold,parts in selected['components'].items():
            copied={}
            for name,item in parts.items():
                source=REPO/item['path']
                if source.suffix!='.json':continue
                target=local(RUN/'provenance/selected_components'/fold/(name+'.json'))
                if target.exists():assert sha(target)==item['sha256'],'COPIED_COMPONENT_DRIFT'
                else:shutil.copyfile(source,target)
                assert sha(target)==item['sha256']
                copied[name]={'path':str(target.relative_to(RUN)),'sha256':item['sha256']}
            summary[fold]={'fit_ids':fold_binding(selected,fold),'fixed_F2':read(REPO/parts['stacker']['path'])['model'],
                           'thresholds':selected['thresholds'],'copied_small_components':copied}
        write(RUN/'model_selection/selected_fold_components.json',summary)
        return selected
    selection.select=select_with_component_evidence
