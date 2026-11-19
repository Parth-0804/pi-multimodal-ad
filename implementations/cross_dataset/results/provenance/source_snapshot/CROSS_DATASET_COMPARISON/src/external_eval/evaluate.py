"""Full fixed outer/official evaluation; resumes completed fits and cases."""
import argparse
import gzip
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
sys.path[:0]=['src','MSM/99_preserved_previous_work/MILLING_DATASET/source','CROSS_DATASET_COMPARISON/src']
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score,roc_auc_score,f1_score,precision_score,
    recall_score,balanced_accuracy_score,confusion_matrix,brier_score_loss,log_loss)
from threadpoolctl import threadpool_limits
from msm.splits import verify_plan
from external_eval.io import write_json,sha,utc
from external_eval.data import Store,TRAIN_VIEWS,all_views
from external_eval.models import fit_base,fit_fusions,predictions


def metrics(y,p):
    y=np.asarray(y,int);p=np.asarray(p,float)
    if len(y)!=len(p) or not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise ValueError('Invalid prediction probabilities/units')
    hard=p>=.5;tn,fp,fn,tp=confusion_matrix(y,hard,labels=[0,1]).ravel();both=set(y)=={0,1}
    return {'examples':len(y),'positive':int(y.sum()),'prevalence':float(y.mean()),
        'AP':float(average_precision_score(y,p)) if both else None,'AUROC':float(roc_auc_score(y,p)) if both else None,
        'F1':float(f1_score(y,hard,zero_division=0)),'precision':float(precision_score(y,hard,zero_division=0)),
        'recall':float(recall_score(y,hard,zero_division=0)),'balanced_accuracy':float(balanced_accuracy_score(y,hard)) if both else None,
        'specificity':float(tn/(tn+fp)) if tn+fp else None,'TN':int(tn),'FP':int(fp),'FN':int(fn),'TP':int(tp),
        'Brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,np.clip(p,1e-15,1-1e-15),labels=[0,1]))}


def execute_case(store,plan_name,definition,fold_index,fold,seed):
    root=store.root;config=store.config
    global_rows=np.array([store.index[s] for s in definition['sample_ids']],int)
    train=global_rows[np.asarray(fold['train'],int)];test=global_rows[np.asarray(fold['test'],int)]
    frame=store.frame.copy()
    if store.dataset=='MSM':frame['group_id']=frame[definition['grouping']]
    source={n:sha(Path(__file__).with_name(n)) for n in ['evaluate.py','models.py','data.py']}
    source['dataset_adapter']=store.adapter_identity
    signature=hashlib.sha256(json.dumps({'plan':definition,'fold':fold_index,'seed':seed,'config':config,
        'features':store.cache_identity['signature'],'native_inputs':getattr(store,'input_identity',None),'source':source},sort_keys=True).encode()).hexdigest()
    case=f'{store.condition}__{plan_name}__fold{fold_index}__seed{seed}__{signature[:10]}'
    destination=root/'06_evaluation_results/predictions'/case;marker=destination/'CASE_COMPLETE.json'
    if marker.exists():
        saved=json.loads(marker.read_text())
        for p,h in saved['output_hashes'].items():
            if sha(p)!=h:raise ValueError('Saved completed prediction/metric hash changed')
        print('REUSED',store.dataset,case,flush=True);return saved
    destination.mkdir(parents=True,exist_ok=True);attempt=destination/('attempt_'+utc().replace(':','').replace('+','').replace('.',''));attempt.mkdir()
    started=time.perf_counter();group_overlap=set(frame.iloc[train].group_id)&set(frame.iloc[test].group_id)
    if group_overlap and store.dataset=='MSM':raise ValueError('Actual outer group leakage')
    inner=fold.get('inner');fusions={};logs=[];provenance={}
    qdim=6+2*len(store.channels)
    if inner is not None:
        inner=[(global_rows[np.array(a,int)],global_rows[np.array(b,int)]) for a,b in inner]
        verify_plan(frame,train,inner)
        bank=np.full((len(TRAIN_VIEWS),len(frame),2),np.nan,np.float64)
        quality=np.full((len(TRAIN_VIEWS),len(frame),qdim),np.nan,np.float32)
        for k,(a,b) in enumerate(inner):
            fit=fit_base(store,a,config,seed+k,case,f'inner{k}',include_strong=False);logs.append(fit.metadata)
            fit_groups=sorted(set(frame.iloc[a].group_id))
            for vi,name in enumerate(TRAIN_VIEWS):
                view=store.view(name,b,a);bank[vi,b]=fit.probabilities(view);quality[vi,b]=view['quality']
            for i in b:
                provenance[frame.iloc[i].sample_id]={branch:{'fit_groups':fit_groups,'selection_groups':[],
                    'OOF_fold':k,'actual_seed':seed+k} for branch in ['visual','sensor']}
        fusion_root=root/'05_trained_models/f2_fusion'/case/attempt.name;fusion_root.mkdir(parents=True)
        fusions=fit_fusions(frame,bank,quality,train,provenance,config,seed,fusion_root)
        with (fusion_root/'OOF_bank.npz').open('xb') as f:np.savez_compressed(f,probabilities=bank[:,train],quality=quality[:,train],train_rows=train,
            targets=frame.iloc[train].target.to_numpy(int),sample_ids=frame.iloc[train].sample_id.to_numpy(str),view_names=np.array(TRAIN_VIEWS))
        write_json(fusion_root/'stacking_provenance.json',provenance)
        # F2/group invariants are checked on every native prediction unit, not only a subset.
        if len(provenance)!=len(train):raise ValueError('OOF coverage incomplete')
    else:
        if store.dataset!='HANDOVER':raise ValueError('MSM requires the frozen inner design')
        write_json(attempt/'SKIPPED_FUSIONS.json',{'models':['F2','F2_aug','QG_clean','QG_aug'],
            'reason':config['participant_oof_gate'],'no_trial_split_substitution':True})
    fit=fit_base(store,train,config,seed+99,case,'final_refit',include_strong=True);logs.append(fit.metadata)
    prevalence=float(frame.iloc[train].target.mean())
    training_view=store.view('clean',train,train)
    training_scores,_=predictions(fit,fusions,training_view,prevalence)
    training_diagnostics={name:metrics(frame.iloc[train].target,p) for name,p in training_scores.items()}
    write_json(attempt/'TRAINING_ONLY_DIAGNOSTICS.json',{'purpose':'in-sample overfitting diagnostic only; computed after all models were fitted; never used to fit F2 or select settings',
        'in_sample_base_prediction_metrics':training_diagnostics,
        'OOF_branch_metrics':{'visual':metrics(frame.iloc[train].target,bank[0,train,0]),'sensor_logistic':metrics(frame.iloc[train].target,bank[0,train,1])} if inner is not None else None,
        'no_in_sample_predictions_used_for_F2_fitting':True})
    roles={'test':test}
    if 'validation' in fold:roles['validation']=global_rows[np.asarray(fold['validation'],int)]
    metric_rows=[];prediction_frames=[];runtime=[];allocations=[]
    for role,assessment in roles.items():
        if set(assessment)&set(train):raise ValueError('Official assessment contamination')
        if set(frame.iloc[assessment].target)!={0,1}:raise ValueError('Both assessment classes required')
        for name in all_views(config):
            start=time.perf_counter();view=store.view(name,assessment,train)
            scores,branches=predictions(fit,fusions,view,prevalence)
            elapsed=time.perf_counter()-start
            runtime.append({'role':role,'condition':name,'seconds':elapsed,'examples':len(assessment)})
            if np.all(view['availability']==1):
                for gate_name in ['QG_clean','QG_aug']:
                    if gate_name in fusions:
                        _,weights=fusions[gate_name].predict(branches,view['quality'],view['availability'])
                        allocations.append({'role':role,'corruption':name,'model':gate_name,
                            'visual_weight_mean':float(weights[:,0].mean()),'visual_weight_std':float(weights[:,0].std()),
                            'visual_weight_min':float(weights[:,0].min()),'visual_weight_max':float(weights[:,0].max()),
                            'sensor_weight_mean':float(weights[:,1].mean()),'examples':len(assessment)})
            behavior='deterministic_unimodal_fallback' if name in ['missing_visual','missing_sensor'] else 'model'
            for model,p in scores.items():
                if not np.isfinite(p).all():
                    metric_rows.append({'dataset':store.dataset,'initialization':store.condition,'protocol':plan_name,'fold':fold_index,
                        'seed':seed,'role':role,'corruption':name,'model':model,'status':'UNAVAILABLE_MODALITY','examples':len(assessment)})
                    continue
                y=frame.iloc[assessment].target.to_numpy(int)
                result=metrics(y,p)
                metric_rows.append({'dataset':store.dataset,'initialization':store.condition,'protocol':plan_name,'fold':fold_index,
                    'seed':seed,'role':role,'corruption':name,'model':model,'status':'COMPLETE',**result})
                records=pd.DataFrame({'sample_id':frame.iloc[assessment].sample_id.to_numpy(),'target':y,
                    'native_label':frame.iloc[assessment].native_label.to_numpy(),'group_id':frame.iloc[assessment].group_id.to_numpy(),
                    'nominal_group_id':store.frame.iloc[assessment].group_id.to_numpy(),'case_id':case,'model':model,
                    'probability':p,'role':role,'seed':seed,'fold':fold_index,'protocol':plan_name,
                    'initialization':store.condition,'corruption':name,
                    'behavior':behavior if model in ['averaging','F2','F2_aug','QG_clean','QG_aug'] else 'model'})
                prediction_frames.append(records)
        # A direction-only nuisance baseline is a diagnostic; the metadata is
        # deliberately absent from every main visual/sensor/fusion feature vector.
        if store.dataset=='MSM':
            x=(frame.direction.to_numpy()=='UP').astype(float)[:,None]
            direction=LogisticRegression(C=1,class_weight='balanced',solver='lbfgs',max_iter=2000).fit(x[train],frame.iloc[train].target)
            p=direction.predict_proba(x[assessment])[:,1]
            metric_rows.append({'dataset':store.dataset,'initialization':store.condition,'protocol':plan_name,'fold':fold_index,
                'seed':seed,'role':role,'corruption':'clean','model':'direction_only_DIAGNOSTIC','status':'COMPLETE',**metrics(frame.iloc[assessment].target,p)})
            records=pd.DataFrame({'sample_id':frame.iloc[assessment].sample_id.to_numpy(),'target':frame.iloc[assessment].target.to_numpy(),
                'native_label':frame.iloc[assessment].native_label.to_numpy(),'group_id':frame.iloc[assessment].group_id.to_numpy(),
                'nominal_group_id':store.frame.iloc[assessment].group_id.to_numpy(),'case_id':case,'model':'direction_only_DIAGNOSTIC',
                'probability':p,'role':role,'seed':seed,'fold':fold_index,'protocol':plan_name,'initialization':store.condition,
                'corruption':'clean','behavior':'nuisance_diagnostic_not_primary_predictor'})
            prediction_frames.append(records)
            write_json(attempt/'direction_baseline.json',{'coef':direction.coef_.tolist(),'intercept':direction.intercept_.tolist(),'train_rows':train.tolist()})
    predictions_path=attempt/'predictions.csv.gz';pd.concat(prediction_frames,ignore_index=True).to_csv(predictions_path,index=False,compression='gzip')
    metrics_path=root/'06_evaluation_results/metrics'/(case+'.csv');pd.DataFrame(metric_rows).to_csv(metrics_path,index=False)
    fitlog=attempt/'training_and_runtime.json';write_json(fitlog,{'base_fits':logs,'inference':runtime,'quality_gate_allocation':allocations,
        'OOF_fusion_native_training_rows':len(provenance),'case_wall_seconds':time.perf_counter()-started,
        'host_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'heldout_results_never_used_for_fitting':True,'grouping':definition['grouping']})
    result={'case_id':case,'signature':signature,'dataset':store.dataset,'initialization':store.condition,'protocol':plan_name,
        'seed':seed,'fold':fold_index,'status':'COMPLETE','predictions':str(predictions_path),'metrics':str(metrics_path),
        'train_examples':len(train),'test_examples':len(test),'train_groups':frame.iloc[train].group_id.nunique() if store.dataset=='MSM' else None,
        'test_groups':frame.iloc[test].group_id.nunique() if store.dataset=='MSM' else None,
        'participant_counts_unverified':store.dataset=='HANDOVER','models':list(scores),'source_identity':source,
        'wall_seconds':time.perf_counter()-started,'output_hashes':{str(p):sha(p) for p in [predictions_path,metrics_path,fitlog]}}
    write_json(marker,result);print('CASE COMPLETE',store.dataset,case,'seconds',round(result['wall_seconds'],1),flush=True)
    return result


def run(dataset,condition='P'):
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    from external_eval.publication import prepare
    from external_eval.leakage import audit
    prepare(Path(dataset));audit(Path(dataset))
    store=Store(dataset,condition);definitions=json.loads((store.root/'03_processed_model_inputs/split_manifests/frozen_splits.json').read_text())
    completed=[]
    with threadpool_limits(limits=1):
        for name,definition in definitions.items():
            for seed in store.config['seeds']:
                for k,fold in enumerate(definition['plan']):completed.append(execute_case(store,name,definition,k,fold,seed))
    write_json(store.root/'06_evaluation_results'/f'{condition}_EVALUATION_COMPLETE.json',
        {'dataset':dataset,'initialization':condition,'cases':completed,'seeds':store.config['seeds'],'all_predeclared_cases_complete':True})
    print(dataset,condition,'EVALUATION COMPLETE',len(completed),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',choices=['MSM','HANDOVER'],required=True);p.add_argument('--condition',default='P');a=p.parse_args();run(a.dataset,a.condition)
