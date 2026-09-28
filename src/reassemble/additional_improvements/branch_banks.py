"""Reconstruct original branch fits and score partition-safe corruptions."""
from pathlib import Path
import argparse
import time
import joblib
import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
from reassemble.section1_models import Standardizer,VisualHead,neural_fit,sigmoid
from reassemble.section3_sensor import sensor_probability
from reassemble.section1b import index_plan,guard_partition
from .common import setup,inputs,read,write,storage,progress,identity
from .corruptions import SensorSource,sensor_features,sensor_conditions

def specifications(c,base,frame,splits):
    c2=read(c['section2_config']);original=Path(c2['section1b_run'])/'stacking';jobs=[]
    for outer in splits['folds']:
        k=outer['fold'];plan=index_plan(frame,outer)
        with np.load(original/f'outer{k}.npz') as z:
            jobs.append(dict(name=f'outer{k}',level='outer',outer=k,train=z['train_rows'],test=z['test_rows'],expected=z['test_branch_probabilities'],branches=read(original/f'outer{k}.json')['refits']))
        for j,(it,iv) in enumerate(plan):
            meta=read(original/f'outer{k}_inner{j}.json')
            with np.load(original/f'outer{k}_inner{j}.npz') as z:
                assert np.array_equal(z['validation_rows'],iv)
                jobs.append(dict(name=f'outer{k}_inner{j}',level='inner_assessment',outer=k,inner=j,train=it,test=iv,expected=z['probabilities'],branches=meta['branches']))
            for t in range(4):
                path=Path(c2['run_dir'])/'inputs'/f'outer{k}_inner{j}_sub{t}.json';meta=read(path)
                with np.load(path.with_suffix('.npz')) as z:
                    assert np.array_equal(z['rows'],meta['test_rows'])
                    jobs.append(dict(name=f'outer{k}_inner{j}_sub{t}',level='inner_training',outer=k,inner=j,sub=t,train=np.array(meta['train_rows']),test=np.array(meta['test_rows']),expected=z['probabilities'],branches=meta['branches']))
    for job in jobs:
        tr,te=job['train'],job['test'];assert not set(frame.recording_id.iloc[tr])&set(frame.recording_id.iloc[te]);assert not set(tr)&set(te)
    return jobs

def recover():
    c=setup();c,base,frame,arrays,splits=inputs();root=Path(c['run_dir'])/'04_corruption_training';out=root/'branches';out.mkdir(exist_ok=True)
    jobs=specifications(c,base,frame,splits);y=frame.failure.to_numpy(int)
    for ordinal,job in enumerate(jobs):
        path=out/job['name'];meta=path.with_suffix('.json')
        if meta.exists():continue
        storage();t0=time.perf_counter();tr,te=job['train'],job['test'];branches=job['branches'];vi=branches['rtdetr'];si=branches['sensor_statistics']
        vpath=path.parent/(path.name+'_visual.pt')
        if job['level']=='outer':
            source=Path(base['run_dir'])/'checkpoints'/f'rtdetr_fold{job["outer"]}.pt';vpath=source
            cp=torch.load(source,map_location='cpu',weights_only=True);model=VisualHead(cp['width'],base).cuda();model.load_state_dict(cp['state_dict']);model.eval()
            x=np.nan_to_num((arrays['visual'][te]-cp['normalizer_mean'].numpy())/cp['normalizer_std'].numpy(),nan=0,posinf=0,neginf=0)
            with torch.inference_mode():raw=np.concatenate([model(torch.tensor(xx,device='cuda'))[0].cpu().numpy() for xx in np.array_split(x,max(1,int(np.ceil(len(x)/128))))])
            del model;torch.cuda.empty_cache()
        else:
            with threadpool_limits(limits=16):
                result,detail=neural_fit('rtdetr',arrays['visual'],y,tr,te,[vi['selected']],base,vi['refit_seed'],save=vpath)
            raw=result[vi['selected']][0]
        visual=sigmoid(vi['calibration']['coefficient']*raw+vi['calibration']['intercept'])
        with threadpool_limits(limits=16):
            scaler=Standardizer().fit(arrays['statistics'][tr]);model=LogisticRegression(C=si['selected'],class_weight='balanced',max_iter=2000,random_state=0).fit(scaler.transform(arrays['statistics'][tr]),y[tr])
        checkpoint=dict(model=model,mean=scaler.mean,std=scaler.std,calibration=si['calibration'],
                 sigma=np.nanstd(arrays['sensor'][tr].astype(np.float64),axis=(0,1)),median=np.nanmedian(arrays['sensor'][tr],axis=(0,1)),train_rows=tr,test_rows=te)
        sensor=sensor_probability(checkpoint,arrays['statistics'][te]);actual=np.column_stack([visual,sensor]);difference=np.max(abs(actual-job['expected']),axis=0)
        assert np.all(difference<=1e-5),('BRANCH PARITY BLOCKER',job['name'],difference)
        spath=path.parent/(path.name+'_sensor.joblib');joblib.dump(checkpoint,spath)
        write(meta,dict(name=job['name'],level=job['level'],train_rows=tr.tolist(),test_rows=te.tolist(),visual_checkpoint=identity(vpath),sensor_checkpoint=identity(spath),visual_calibration=vi['calibration'],sensor_calibration=si['calibration'],clean_max_abs=difference.tolist(),seconds=time.perf_counter()-t0))
        progress(4,f'Frozen branch recovery {ordinal+1}/{len(jobs)} complete')

def sensor_bank(job_index=None):
    c=setup();c,base,frame,arrays,splits=inputs();c2=read(c['section2_config']);root=Path(c['run_dir'])/'04_corruption_training';out=root/'sensor_bank';out.mkdir(exist_ok=True);storage(large=True)
    jobs=specifications(c,base,frame,splits);source=SensorSource(base,frame)
    if job_index is not None:jobs=[jobs[job_index]]
    for ordinal,job in enumerate(jobs):
        path=out/(job['name']+'.npz')
        if path.exists():assert identity(path)==read(path.with_suffix('.json'))['output'];continue
        storage();t0=time.perf_counter();checkpoint=joblib.load(root/'branches'/(job['name']+'_sensor.joblib'))
        conditions=sensor_conditions('test') if job['level']=='outer' else sensor_conditions('train')+(sensor_conditions('validation') if job['level']=='inner_assessment' else [])
        rows=job['test'];features=np.empty((len(conditions),len(rows),220),np.float32);quality=np.empty((len(conditions),len(rows),30),np.float32);warnings=0
        for i,idx in enumerate(rows):
            row=frame.iloc[idx];streams=source.segment(row)
            for j,condition in enumerate(conditions):
                features[j,i],quality[j,i],count=sensor_features(c,c2,row,streams,condition,checkpoint['sigma'],checkpoint['median']);warnings+=count
        probability=np.stack([sensor_probability(checkpoint,f) for f in features])
        np.savez_compressed(path,rows=rows,p=probability,quality=quality,names=np.array([v['name'] for v in conditions]))
        write(path.with_suffix('.json'),dict(output=identity(path),checkpoint=identity(root/'branches'/(job['name']+'_sensor.joblib')),conditions=conditions,expected_NaN_statistic_warnings=warnings,seconds=time.perf_counter()-t0,
                  statistics_features_retained=False,scale_fit_rows=job['train'].tolist(),source_native_rate='full recording timestamps, exactly as sealed implementation'))
        progress(4,f'Partition-safe raw sensor noise {job["name"]} complete')

def score_visual():
    c=setup();c,base,frame,arrays,splits=inputs();root=Path(c['run_dir'])/'04_corruption_training';out=root/'visual_probabilities';out.mkdir(exist_ok=True)
    blocks=[]
    for path in sorted((root/'visual_bank').glob('*.npz')):
        with np.load(path) as z:blocks.append({key:z[key] for key in z.files if key!='severities'})
    rows=np.concatenate([z['row_index'] for z in blocks]);assert sorted(rows)==list(range(len(frame)));order=np.argsort(rows)
    features=np.concatenate([z['features'] for z in blocks],axis=1)[:,order];quality=np.concatenate([z['quality'] for z in blocks],axis=1)[:,order];names=blocks[0]['names']
    assert all(np.array_equal(z['names'],names) for z in blocks)
    for job in specifications(c,base,frame,splits):
        path=out/(job['name']+'.npz')
        if path.exists():assert identity(path)==read(path.with_suffix('.json'))['output'];continue
        meta=read(root/'branches'/(job['name']+'.json'));cp=torch.load(meta['visual_checkpoint']['path'],map_location='cpu',weights_only=True)
        model=VisualHead(cp['width'],base).cuda();model.load_state_dict(cp['state_dict']);model.eval();rows=job['test'];indices=[i for i,name in enumerate(names) if name.startswith('test_' if job['level']=='outer' else 'train_') or (job['level']=='inner_assessment' and name.startswith('validation_'))]
        probability=[]
        for index in indices:
            values=np.nan_to_num((features[index,rows]-cp['normalizer_mean'].numpy())/cp['normalizer_std'].numpy(),nan=0,posinf=0,neginf=0)
            with torch.inference_mode():raw=np.concatenate([model(torch.tensor(x,device='cuda'))[0].cpu().numpy() for x in np.array_split(values,max(1,int(np.ceil(len(rows)/128))))])
            cal=meta['visual_calibration'];probability.append(sigmoid(cal['coefficient']*raw+cal['intercept']))
        np.savez_compressed(path,rows=rows,p=np.stack(probability),quality=quality[indices][:,rows],names=names[indices])
        write(path.with_suffix('.json'),dict(output=identity(path),checkpoint=meta['visual_checkpoint']));del model;torch.cuda.empty_cache()
    progress(4,'All nested visual corruption probabilities complete')

def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['recover','sensor','visual']);p.add_argument('--job-index',type=int);a=p.parse_args()
    if a.operation=='recover':recover()
    elif a.operation=='sensor':sensor_bank(a.job_index)
    else:score_visual()

if __name__=='__main__':main()
