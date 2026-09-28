"""Strictly nested two-representation sensor stacking; no new sensor modality."""
from pathlib import Path
import numpy as np
from reassemble.section1b import index_plan,guard_partition,choose_threshold
from reassemble.section1_models import sigmoid
from .common import setup,inputs,read,write,progress,identity
from .neural import branch
from .anchored import anchor
from .reporting import comparison

def main():
    c=setup();c,base,frame,arrays,splits=inputs();c2=read(c['section2_config'])
    root=Path(c['run_dir'])/'02_patchtst_training_budget';y=frame.failure.to_numpy(int);n=len(y);x=arrays['sensor']
    p=np.full(n,np.nan);hard=np.zeros(n,int);fold=np.full(n,-1)
    for outer in splits['folds']:
        k=outer['fold'];plan=index_plan(frame,outer);original=Path(c2['section1b_run'])/'stacking'
        with np.load(original/f'outer{k}.npz') as z:tr=z['train_rows'];te=z['test_rows'];statistics_train=z['training_branch_oof'][:,1];statistics_test=z['test_branch_probabilities'][:,1]
        guard_partition(frame,tr,te,plan);fold[te]=k
        temporal_train=np.full(n,np.nan);inner_hybrid=np.full(n,np.nan);inner_details=[]
        for j,(it,iv) in enumerate(plan):
            detail=read(original/f'outer{k}_inner{j}.json');idx=lambda groups:np.flatnonzero(frame.recording_id.isin(groups))
            sub=[(idx(s['train_recordings']),idx(s['validation_recordings'])) for s in detail['subfolds']]
            guard_partition(frame,it,iv,sub)
            assessment,ainfo=branch(root/'fits/S-HYBRID'/f'outer{k}_inner{j}_assessment','S-LONG',x,y,frame,it,iv,sub,base)
            temporal_train[iv]=assessment['p']
            # Gate/stacker threshold uses genuinely held-out inner predictions too.
            meta_temporal=np.full(n,np.nan)
            for t,(st,sv) in enumerate(sub):
                deeper=[(np.intersect1d(a,st),b) for v,(a,b) in enumerate(sub) if v!=t]
                guard_partition(frame,st,sv,deeper)
                res,info=branch(root/'fits/S-HYBRID'/f'outer{k}_inner{j}_train_sub{t}','S-LONG',x,y,frame,st,sv,deeper,base)
                meta_temporal[sv]=res['p']
                progress(2,f'S-HYBRID outer{k+1}/5 inner{j+1}/4 strict training subfold{t+1}/4 complete')
            with np.load(Path(c2['run_dir'])/'inputs'/f'outer{k}_inner{j}.npz') as z:
                assert np.array_equal(z['train_rows'],it) and np.array_equal(z['validation_rows'],iv)
                mt=np.column_stack([meta_temporal[it],z['train_probabilities'][:,1]])
                mv=np.column_stack([assessment['p'],z['validation_probabilities'][:,1]])
            a,b=anchor(mt,y[it]);inner_hybrid[iv]=sigmoid(b+mv@a)
            inner_details.append(dict(inner=j,coefficient=a.tolist(),intercept=b,assessment=ainfo))
        final,info=branch(root/'fits/S-LONG'/f'outer{k}','S-LONG',x,y,frame,tr,te,plan,base)
        meta_train=np.column_stack([temporal_train[tr],statistics_train]);meta_test=np.column_stack([final['p'],statistics_test])
        a,b=anchor(meta_train,y[tr]);threshold=choose_threshold(y[tr],inner_hybrid[tr]);p[te]=sigmoid(b+meta_test@a);hard[te]=p[te]>=threshold
        np.savez_compressed(root/f'hybrid_outer{k}.npz',train_rows=tr,test_rows=te,training_probabilities=meta_train,test_probabilities=meta_test,inner_hybrid=inner_hybrid[tr],p=p[te],hard=hard[te])
        write(root/f'hybrid_outer{k}.json',dict(fold=k,coefficient=a.tolist(),intercept=b,threshold=threshold,inner=inner_details,outer_branch=info))
        progress(2,f'S-HYBRID outer{k+1}/5 complete')
    np.savez_compressed(root/'S-HYBRID_predictions.npz',p=p,hard=hard,fold=fold,y=y)
    with np.load(Path(base['run_dir'])/'predictions/sensor_statistics_perm00.npz') as z:stats={key:z[key] for key in ['p','hard']}
    comparison(frame,fold,{'S-HYBRID':dict(p=p,hard=hard),'S-STATS':stats},[('S-HYBRID','S-STATS')],root/'hybrid_comparison')
    progress(2,'All sensor variants including strictly nested hybrid complete; final report pending')

if __name__=='__main__':main()
