"""Execute matched visual and sensor controls, leaving all old fits untouched."""
from pathlib import Path
import argparse
import numpy as np
from reassemble.section1b import index_plan
from .common import setup,inputs,read,write,progress,identity
from .neural import branch
from .reporting import comparison

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',type=int,choices=[1,2],required=True);args=parser.parse_args()
    c=setup();c,base,frame,arrays,splits=inputs();root=Path(c['run_dir'])/('01_temporal_visual' if args.task==1 else '02_patchtst_training_budget')
    if args.task==1:
        blocks=[]
        for p in sorted((root/'features').glob('*.npz')):
            with np.load(p) as z:blocks.append((z['row_index'],z['features'],z['valid']))
        ids=np.concatenate([v[0] for v in blocks]);assert sorted(ids)==list(range(len(frame)))
        assert all(v[2].all() for v in blocks),'Use valid-frame masks if cohort changes; no silent imputation'
        sequence=np.concatenate([v[1] for v in blocks])[np.argsort(ids)]
        # Shared sequence-mean normalization for the budget-matched control.
        assert np.max(abs(sequence.mean(1)-arrays['visual']))<5e-5
        variants={'V-MEAN':sequence.mean(1),'V-TEMP':sequence,'V-NOPOS':sequence}
    else:variants={'S-6':arrays['sensor'],'S-LONG':arrays['sensor']}
    y=frame.failure.to_numpy(int);n=len(frame);predictions={};fold=np.full(n,-1)
    for name,x in variants.items():
        values=dict(p=np.full(n,np.nan),hard=np.zeros(n,int),seed_p=np.full((3,n),np.nan),seed_hard=np.zeros((3,n),int))
        if args.task==1:values.update(reverse=np.full(n,np.nan),permute=np.full(n,np.nan))
        for outer in splits['folds']:
            k=outer['fold'];tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']));fold[te]=k
            output,info=branch(root/'fits'/name/f'outer{k}',name,x,y,frame,tr,te,index_plan(frame,outer),base)
            for key in values:
                if values[key].ndim==1:values[key][te]=output[key]
                else:values[key][:,te]=output[key]
            progress(args.task,f'{name} outer {k+1}/5 complete')
        predictions[name]=values
        np.savez_compressed(root/(name+'_predictions.npz'),y=y,fold=fold,**values)
    hist={'V-HIST':'rtdetr'} if args.task==1 else {'S-HIST':'patchtst','S-STATS':'sensor_statistics'}
    for name,source in hist.items():
        with np.load(Path(base['run_dir'])/'predictions'/(source+'_perm00.npz')) as z:
            assert np.array_equal(z['y'],y) and np.array_equal(z['fold'],fold)
            predictions[name]={key:z[key] for key in ['p','hard']}
    contrasts=[('V-TEMP','V-MEAN'),('V-TEMP','V-NOPOS'),('V-MEAN','V-HIST')] if args.task==1 else [('S-LONG','S-6'),('S-LONG','S-STATS'),('S-6','S-HIST')]
    comparison(frame,fold,predictions,contrasts,root/'comparison')
    if args.task==1:
        diagnostics={name:{key:float(np.max(abs(values[key]-values['p']))) for key in ['reverse','permute']} for name,values in predictions.items() if key_available(values)}
        write(root/'order_diagnostics.json',diagnostics)
    progress(args.task,'Primary unimodal fits and paired comparisons complete; secondary subtask/report pending')

def key_available(values):return 'reverse' in values

if __name__=='__main__':main()
