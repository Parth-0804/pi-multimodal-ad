"""Section 1B: frozen branch controls and nested two-probability stacking."""
import argparse
import copy
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score,balanced_accuracy_score
from sklearn.model_selection import StratifiedGroupKFold
from threadpoolctl import threadpool_limits
import torch
from .section1_features import sha
from .section1_models import load_features,verify_splits,permute_labels,evaluate_model,neural_fit,logistic_fit,calibrate,sigmoid


def write_json(path,obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')


def progress(config,stage):
    run=Path(config['run_dir']);now=datetime.now(timezone.utc).isoformat()
    (run/'live_status.json').write_text(json.dumps({'utc':now,'stage':stage},indent=2)+'\n')
    Path('docs/reassemble/SECTION_1B_CONTINUATION.md').write_text('# Section 1B continuation\n\n'+now+'\n\nRun: `'+str(run)+'`.\nStatus: **'+stage+'**.\nConfig: configs/reassemble/section1b.json; protocol: docs/reassemble/SECTION_1B_PROTOCOL.md.\nCommand: `ma_thesis_env/bin/python -B scripts/reassemble/07_section1b.py`.\nLog: '+str(run/'execution.log')+'.\nCheck running processes and live_status.json before resuming. Completed outer fits and\npermutation runs are preserved. Do not change implementation mid-run. Section1 files,\nincluding its original CONTINUATION.md, are frozen. The current task ends at\nartifacts/reassemble/reports/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md; STOP there.\nNo full fusion architecture search, fine-tuning, corruption or audio is authorized.\n')
    print(now,stage,flush=True)


def verify_section1(config):
    source=Path(config['section1_run']);manifest=json.loads((source/'final_output_manifest.json').read_text())
    for e in manifest['files']:
        p=Path(e['path']);assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],str(p)
    return len(manifest['files'])


def index_plan(frame,outer):
    return [(np.flatnonzero(frame.recording_id.isin(i['train_recordings'])),np.flatnonzero(frame.recording_id.isin(i['validation_recordings']))) for i in outer['inner']]


def guard_partition(frame,train,test,plan):
    tr=set(train);te=set(test);groups=frame.recording_id.to_numpy();covered=set()
    assert not tr&te and not set(groups[train])&set(groups[test])
    for a,b in plan:
        assert set(a)|set(b)==tr and not set(a)&set(b)
        assert not set(groups[a])&set(groups[b]) and not covered&set(b)
        covered.update(b)
    assert covered==tr


def subfolds(frame,train,seed):
    g=frame.recording_id.to_numpy();y=frame.failure.to_numpy()
    plan=[]
    for a,b in StratifiedGroupKFold(4,shuffle=True,random_state=seed).split(np.zeros(len(train)),y[train],g[train]):
        aa,bb=train[a],train[b]
        assert len(np.unique(y[aa]))==2 and len(np.unique(y[bb]))==2
        plan.append((aa,bb))
    return plan


def fit_branch(kind,x,y,train,test,plan,base,seed_base,refit_seed):
    candidates=base['visual']['epochs'] if kind=='rtdetr' else base['logistic_C']
    oof={c:np.full(len(y),np.nan) for c in candidates};scores={c:[] for c in candidates};fit_log=[]
    for i,(it,iv) in enumerate(plan):
        if kind=='rtdetr':outputs,info=neural_fit(kind,x,y,it,iv,candidates,base,seed_base+i)
        else:outputs={c:(logistic_fit(x,y,it,iv,c)[0],None) for c in candidates};info={}
        for c in candidates:
            oof[c][iv]=outputs[c][0];scores[c].append(float(average_precision_score(y[iv],sigmoid(outputs[c][0]))))
        fit_log.append(info)
    selected=max(candidates,key=lambda c:np.mean(scores[c]));assert np.isfinite(oof[selected][train]).all()
    if kind=='rtdetr':out,info=neural_fit(kind,x,y,train,test,[selected],base,refit_seed);raw=out[selected][0]
    else:raw,info=logistic_fit(x,y,train,test,selected)
    probability,threshold,calibration=calibrate(oof[selected][train],y[train],raw)
    return probability,{'selected':selected,'inner_AP':scores,'calibration':calibration,'inner_fit':fit_log,'refit':info,'refit_seed':refit_seed}


def choose_threshold(y,p):
    t=np.arange(.01,1,.01);scores=np.array([balanced_accuracy_score(y,p>=v) for v in t])
    tied=t[np.isclose(scores,scores.max(),rtol=0,atol=1e-12)]
    return float(tied[np.argmin(abs(tied-.5))])


def fit_stacker(meta,y,train,plan,test_probabilities,settings):
    """No access to outer-test labels; only two branch-probability columns."""
    assert meta.ndim==2 and meta.shape[1]==2 and test_probabilities.shape[1]==2
    def estimator():return LogisticRegression(C=settings['C'],class_weight=None,solver=settings['solver'],max_iter=settings['max_iter'],random_state=0)
    validation=np.full(len(y),np.nan)
    for it,iv in plan:
        model=estimator().fit(meta[it],y[it]);validation[iv]=model.predict_proba(meta[iv])[:,1]
    assert np.isfinite(validation[train]).all()
    threshold=choose_threshold(y[train],validation[train])
    model=estimator().fit(meta[train],y[train])
    p=model.predict_proba(test_probabilities)[:,1]
    return p,(p>=threshold).astype(int),{'coefficient':model.coef_[0].tolist(),'intercept':float(model.intercept_[0]),'threshold':threshold,'meta_crossfit_Brier':float(np.mean((validation[train]-y[train])**2))}


def frozen_predictions(config,name):
    with np.load(Path(config['section1_run'])/'predictions'/f'{name}_perm00.npz') as z:return {k:z[k] for k in ['p','hard','y','fold']}


def stacking(config,base,frame,arrays,splits):
    run=Path(config['run_dir']);out=run/'stacking';out.mkdir(exist_ok=True);y=frame.failure.to_numpy(dtype=int)
    originals={m:frozen_predictions(config,m) for m in ['rtdetr','sensor_statistics']}
    p=np.full(len(y),np.nan);hard=np.zeros(len(y),dtype=int);folds=np.full(len(y),-1)
    for outer in splits['folds']:
        k=outer['fold'];path=out/f'outer{k}.npz';report=out/f'outer{k}.json'
        tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']));plan=index_plan(frame,outer);guard_partition(frame,tr,te,plan)
        if path.exists():
            with np.load(path) as z:assert np.array_equal(z['test_rows'],te);p[te]=z['p'];hard[te]=z['hard']
            folds[te]=k;continue
        started=time.time();meta=np.full((len(y),2),np.nan);logs={'fold':k,'meta_columns':['p_rtdetr','p_sensor_statistics'],'inner':[],'refits':{}}
        for j,(it,iv) in enumerate(plan):
            checkpoint=out/f'outer{k}_inner{j}.npz';detail=checkpoint.with_suffix('.json')
            if checkpoint.exists():
                with np.load(checkpoint) as z:assert np.array_equal(z['validation_rows'],iv);meta[iv]=z['probabilities']
                logs['inner'].append(json.loads(detail.read_text()));continue
            seed=config['seed']+config['subfold_seed_offset']+100*k+j;sub=subfolds(frame,it,seed);guard_partition(frame,it,iv,sub)
            entry={'inner_fold':j,'train_recordings':sorted(set(frame.iloc[it].recording_id)),'validation_recordings':sorted(set(frame.iloc[iv].recording_id)),'subfold_seed':seed,'subfolds':[{'train_recordings':sorted(set(frame.iloc[a].recording_id)),'validation_recordings':sorted(set(frame.iloc[b].recording_id))} for a,b in sub],'branches':{}}
            for column,(name,key) in enumerate([('rtdetr','visual'),('sensor_statistics','statistics')]):
                s=config['seed']+config['subfit_seed_offset']+1000*k+100*j
                meta[iv,column],entry['branches'][name]=fit_branch(name,arrays[key],y,it,iv,sub,base,s,s+99)
            write_json(detail,entry);np.savez_compressed(checkpoint,validation_rows=iv,probabilities=meta[iv]);logs['inner'].append(entry)
            progress(config,f'Stacking outer {k+1}/5: inner branch OOF {j+1}/4 complete')
        assert np.isfinite(meta[tr]).all() and np.isnan(meta[te]).all()
        outer_probs=np.zeros((len(te),2))
        for col,(name,key) in enumerate([('rtdetr','visual'),('sensor_statistics','statistics')]):
            outer_probs[:,col],logs['refits'][name]=fit_branch(name,arrays[key],y,tr,te,plan,base,base['seed']+100*k,base['seed']+100*k+99)
            delta=float(np.max(np.abs(outer_probs[:,col]-originals[name]['p'][te])));logs['refits'][name]['max_frozen_probability_difference']=delta
            expected=json.loads((Path(config['section1_run'])/'predictions'/f'{name}_perm00_fold{k}.json').read_text())['selected']
            assert logs['refits'][name]['selected']==expected and delta<=1e-5,(name,k,delta,'Section1 parity failed')
        p[te],hard[te],logs['stacker']=fit_stacker(meta,y,tr,plan,outer_probs,config['stacker']);folds[te]=k
        logs['seconds']=time.time()-started;write_json(report,logs)
        np.savez_compressed(path,test_rows=te,p=p[te],hard=hard[te],train_rows=tr,training_branch_oof=meta[tr],test_branch_probabilities=outer_probs)
        progress(config,f'Stacking outer {k+1}/5 complete')
    assert np.isfinite(p).all() and np.all(folds>=0)
    final=out/'oof.npz'
    if not final.exists():np.savez_compressed(final,p=p,hard=hard,y=y,fold=folds)


def controls(config,base,frame,arrays,splits):
    derived=copy.deepcopy(base);derived['run_dir']=str(Path(config['run_dir'])/'sensor_controls');Path(derived['run_dir']).mkdir(exist_ok=True)
    for permutation in range(config['permutations']+1):
        y=frame.failure.to_numpy(dtype=int) if permutation==0 else permute_labels(frame,base['seed']+10000+permutation)
        evaluate_model('sensor_statistics',frame,arrays,y,derived,splits,permutation)
        if permutation==0:
            old=frozen_predictions(config,'sensor_statistics')
            with np.load(Path(derived['run_dir'])/'predictions/sensor_statistics_perm00.npz') as z:
                difference=float(np.max(abs(z['p']-old['p'])));assert difference<=1e-5,('Sensor parity failed',difference)
            new=json.loads((Path(derived['run_dir'])/'predictions/sensor_statistics_perm00.json').read_text())
            previous=json.loads((Path(config['section1_run'])/'predictions/sensor_statistics_perm00.json').read_text())
            assert [x['selected'] for x in new['folds']]==[x['selected'] for x in previous['folds']]
            path=Path(config['run_dir'])/'sensor_reproduction.json'
            if not path.exists():write_json(path,{'max_probability_difference':difference,'selected_C_equal':True,'blas_threads':config['blas_threads']})
        progress(config,f'Statistical-sensor control {permutation}/{config["permutations"]} complete (0 = observed reproduction)')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',default='configs/reassemble/section1b.json');args=parser.parse_args();config=json.loads(Path(args.config).read_text());run=Path(config['run_dir'])
    import fcntl
    lock=(run/'execution.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert config==json.loads((run/'config.json').read_text())
    base=json.loads(Path(config['section1_config']).read_text());torch.set_num_threads(base['threads']);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
    evidence=verify_section1(config);frame,arrays=load_features(base);del arrays['sensor'];splits=json.loads(Path(base['splits']).read_text());verify_splits(frame,splits)
    implementation={'source_sha256':{str(p):sha(p) for p in sorted(Path('src/reassemble').glob('section1*.py'))},'config_sha256':sha(run/'config.json'),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'section1_entries_verified':evidence,'split_sha256':splits['sha256'],'command':['scripts/reassemble/07_section1b.py','--config',args.config]}
    target=run/'implementation.json'
    if target.exists():
        old=json.loads(target.read_text());assert old['source_sha256']==implementation['source_sha256'] and old['config_sha256']==implementation['config_sha256']
    else:write_json(target,implementation)
    with threadpool_limits(limits=config['blas_threads'],user_api='blas'):
        controls(config,base,frame,arrays,splits)
        stacking(config,base,frame,arrays,splits)
        from .section1b_report import assess
        assess(config,frame)
    assert verify_section1(config)==evidence
    progress(config,'Section1B computed; final validation and researcher review next')

if __name__=='__main__':main()
