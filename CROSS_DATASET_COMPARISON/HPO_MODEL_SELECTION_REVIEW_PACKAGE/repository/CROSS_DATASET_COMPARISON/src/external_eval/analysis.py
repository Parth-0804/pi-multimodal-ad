"""Prediction/metric consistency and paired group-level uncertainty."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

from external_eval.evaluate import metrics
from external_eval.io import sha,write_json


def read_predictions(root):
    root=Path(root);parts=[];checks=[];cases=[]
    for path in sorted((root/'06_evaluation_results').glob('*_EVALUATION_COMPLETE.json')):
        complete=json.loads(path.read_text())
        for case in complete['cases']:
            for p,h in case['output_hashes'].items():
                if sha(p)!=h:raise ValueError('Completed model output changed')
            prediction=pd.read_csv(case['predictions'],float_precision='round_trip');saved=pd.read_csv(case['metrics'],float_precision='round_trip')
            for key,g in prediction.groupby(['role','corruption','model'],sort=False):
                if g.sample_id.duplicated().any():raise ValueError('Repeated prediction unit in fold/model/view')
                actual=metrics(g.target,g.probability)
                row=saved[(saved.role==key[0])&(saved.corruption==key[1])&(saved.model==key[2])]
                if len(row)!=1:raise ValueError('Missing/duplicated metric record')
                for name,value in actual.items():
                    expected=row.iloc[0].get(name)
                    if value is None:
                        if not pd.isna(expected):raise ValueError('Undefined metric reported as defined')
                    elif not np.isclose(float(value),float(expected),rtol=0,atol=1e-12):raise ValueError('Saved metric differs from predictions: '+name)
                checks.append({'case':case['case_id'],'role':key[0],'corruption':key[1],'model':key[2],'passed':True})
            parts.append(prediction);cases.append(case)
    if not parts:raise ValueError('No completed held-out evaluation exists')
    frame=pd.concat(parts,ignore_index=True)
    rows=[]
    keys=['initialization','protocol','role','corruption','seed','model']
    for key,g in frame.groupby(keys,sort=True):
        if g.sample_id.duplicated().any():raise ValueError('Prediction unit occurs in multiple outer tests')
        rows.append({**dict(zip(keys,key)),**metrics(g.target,g.probability)})
    return frame,pd.DataFrame(rows),checks,cases


def weighted_bootstrap_ap(y,p,group_ids,draws):
    """Exact weighted AP with tie thresholds; draws are cluster multiplicities."""
    y=np.asarray(y,int);p=np.asarray(p,float);group_ids=np.asarray(group_ids,int)
    order=np.argsort(-p,kind='stable');ys=y[order];ps=p[order];gs=group_ids[order]
    ends=np.r_[np.flatnonzero(np.diff(ps)!=0),len(ps)-1]
    values=[]
    for start in range(0,len(draws),128):
        w=draws[start:start+128,gs].astype(float)
        positive=np.cumsum(w*ys,axis=1)[:,ends]
        mass=np.cumsum(w,axis=1)[:,ends]
        total_positive=positive[:,-1];total_negative=mass[:,-1]-total_positive
        recall=np.divide(positive,total_positive[:,None],out=np.zeros_like(positive),where=total_positive[:,None]>0)
        precision=np.divide(positive,mass,out=np.zeros_like(positive),where=mass>0)
        increment=np.diff(np.c_[np.zeros(len(w)),recall],axis=1)
        ap=(increment*precision).sum(1);ap[(total_positive==0)|(total_negative==0)]=np.nan
        values.append(ap)
    return np.concatenate(values)


def paired_uncertainty(predictions,manifest,grouping,replicates=2000,seed=20261027):
    clean=predictions[(predictions.role=='test')&(predictions.corruption=='clean')]
    results=[]
    for (condition,protocol),data in clean.groupby(['initialization','protocol']):
        ids=sorted(data.sample_id.unique());metadata=manifest.set_index('sample_id').loc[ids]
        if grouping not in metadata or metadata[grouping].eq('').any():continue
        groups,group_ids=np.unique(metadata[grouping].astype(str),return_inverse=True)
        rng=np.random.default_rng(seed);draws=rng.multinomial(len(groups),np.full(len(groups),1/len(groups)),size=replicates)
        models=sorted(data.model.unique());seeds=sorted(data.seed.unique());boot={};point={}
        y=None
        for model in models:
            values=[];points=[]
            for run_seed in seeds:
                rows=data[(data.model==model)&(data.seed==run_seed)].set_index('sample_id').loc[ids]
                this_y=rows.target.to_numpy(int)
                if y is None:y=this_y
                if not np.array_equal(this_y,y):raise ValueError('Unpaired outcome identities')
                p=rows.probability.to_numpy(float)
                values.append(weighted_bootstrap_ap(y,p,group_ids,draws));points.append(metrics(y,p)['AP'])
            boot[model]=np.mean(values,axis=0);point[model]=float(np.mean(points))
            valid=boot[model][np.isfinite(boot[model])]
            results.append({'initialization':condition,'protocol':protocol,'grouping':grouping,'groups':len(groups),
                'comparison':model,'point_AP_or_difference':point[model],'lower_95':float(np.quantile(valid,.025)),
                'upper_95':float(np.quantile(valid,.975)),'valid_bootstrap_replicates':len(valid),'seeds_averaged_not_independent':True})
        for first in ['F2','QG_clean','QG_aug','F2_aug','averaging']:
            if first not in boot:continue
            for second in ['visual','sensor_logistic','sensor_histgradient','averaging','F2','F2_aug']:
                if second not in boot or first==second:continue
                difference=boot[first]-boot[second];valid=difference[np.isfinite(difference)]
                results.append({'initialization':condition,'protocol':protocol,'grouping':grouping,'groups':len(groups),
                    'comparison':first+' minus '+second,'point_AP_or_difference':point[first]-point[second],
                    'lower_95':float(np.quantile(valid,.025)),'upper_95':float(np.quantile(valid,.975)),
                    'valid_bootstrap_replicates':len(valid),'seeds_averaged_not_independent':True})
    return pd.DataFrame(results)


def summarize(root):
    root=Path(root);frame,pooled,checks,cases=read_predictions(root)
    metrics_dir=root/'06_evaluation_results/metrics'
    pooled.to_csv(metrics_dir/'pooled_heldout_metrics.csv',index=False)
    clean=pooled[(pooled.role=='test')&(pooled.corruption=='clean')]
    summary=clean.groupby(['initialization','protocol','model']).AP.agg(['mean','std','min','max']).reset_index().rename(columns={'mean':'AP_mean','std':'AP_seed_std','min':'AP_min','max':'AP_max'})
    summary.to_csv(metrics_dir/'clean_seed_summary.csv',index=False)
    pairs=[]
    for key,g in clean.groupby(['initialization','protocol','seed']):
        values=g.set_index('model').AP
        for first in ['F2','QG_clean','QG_aug','F2_aug','averaging']:
            if first not in values:continue
            for second in ['visual','sensor_logistic','sensor_histgradient','averaging','F2','F2_aug']:
                if second in values and first!=second:pairs.append({'initialization':key[0],'protocol':key[1],'seed':key[2],
                    'comparison':first+' minus '+second,'AP_difference':float(values[first]-values[second])})
    pd.DataFrame(pairs).to_csv(metrics_dir/'paired_seed_differences.csv',index=False)
    if {'P','R'}<=set(clean.initialization):
        matching=clean.pivot(index=['protocol','seed','model'],columns='initialization',values='AP').reset_index()
        matching['R_minus_P_AP']=matching.R-matching.P
        matching.to_csv(metrics_dir/'paired_R_minus_P.csv',index=False)
    robustness=[]
    lookup=pooled.set_index(['initialization','protocol','role','seed','model','corruption'])
    for r in pooled.itertuples():
        base=lookup.loc[(r.initialization,r.protocol,r.role,r.seed,r.model,'clean')]
        robustness.append({'initialization':r.initialization,'protocol':r.protocol,'role':r.role,'seed':r.seed,'model':r.model,
            'corruption':r.corruption,'clean_AP':float(base.AP),'AP':r.AP,'absolute_AP_degradation':float(base.AP-r.AP),
            'relative_AP_degradation_percent':float((base.AP-r.AP)/base.AP*100) if base.AP else None})
    pd.DataFrame(robustness).to_csv(root/'07_robustness_experiments/robustness_metrics.csv',index=False)
    manifest=pd.read_csv(root/'03_processed_model_inputs/final_sample_manifest.csv',keep_default_na=False)
    if json.loads((root/'04_experiment_protocol/experiment_config.json').read_text())['dataset']=='MSM':
        # Protocol-specific grouping CIs plus date-proxy CIs for the primary nominal model.
        cis=[]
        for grouping in ['group_id','calendar_date_group']:
            cis.append(paired_uncertainty(frame,manifest,grouping))
        pd.concat(cis,ignore_index=True).to_csv(metrics_dir/'paired_group_bootstrap_95ci.csv',index=False)
    else:
        write_json(metrics_dir/'participant_uncertainty_unavailable.json',{'reason':'No native participant IDs; no pseudo-independent trial CI is substituted. Point estimates and training-seed variability only.'})
    write_json(root/'06_evaluation_results/metric_reproduction.json',{'checks':len(checks),'all_saved_fold_metrics_match_predictions':True,
        'tolerance':1e-12,'models_or_thresholds_not_selected_from_scores':True,'case_count':len(cases)})
    return frame,pooled,summary,cases
