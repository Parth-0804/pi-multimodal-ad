"""Paired fixed-prediction recording uncertainty; no model selection here."""
from pathlib import Path
import numpy as np
import pandas as pd
from reassemble.cluster_metrics import draws,weighted_metrics,intervals
from reassemble.section1_report import metrics,METRICS
from .common import config,write,identity

def comparison(frame, fold, predictions, contrasts, out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);c=config()
    y=frame.failure.to_numpy(int);weights=draws(frame.recording_id.to_numpy(),c['bootstrap_replicates'],c['bootstrap_seed'])
    records={};boots={};points={};rows=[]
    for name,values in predictions.items():
        p,hard=values['p'],values['hard'];assert p.shape==y.shape and np.isfinite(p).all()
        points[name]=np.asarray(metrics(y,p,hard));boots[name]=weighted_metrics(y,p,hard,weights)
        records[name]=dict(metrics=intervals(points[name],boots[name]),folds={},seeds={})
        for k in np.unique(fold):
            ii=fold==k;v=metrics(y[ii],p[ii],hard[ii]);records[name]['folds'][str(k)]=dict(zip(METRICS,map(float,v)))
        for seed,ps in enumerate(values.get('seed_p',[])):
            hs=values.get('seed_hard',np.tile(hard,(3,1)))[seed]
            records[name]['seeds'][str(c['seeds'][seed])]=dict(zip(METRICS,map(float,metrics(y,ps,hs))))
        rows.append(dict(model=name,**dict(zip(METRICS,points[name]))))
    differences={}
    for a,b in contrasts:
        key=f'{a} minus {b}';result=intervals(points[a]-points[b],boots[a]-boots[b])
        ap=result['AUPRC'];interpretation='supported improvement' if ap['lower_95']>0 else ('supported deterioration' if ap['upper_95']<0 else 'inconclusive difference')
        differences[key]=dict(metrics=result,AP_interpretation=interpretation,
             fold_differences={str(k):{m:records[a]['folds'][str(k)][m]-records[b]['folds'][str(k)][m] for m in METRICS} for k in np.unique(fold)})
    result=dict(metric_note='AUPRC field is sklearn average precision, not trapezoidal PR area',
                models=records,contrasts=differences,uncertainty='2000 paired recording-cluster replicates; marginal 95%; conditional on fitted models; does not include retraining or study selection')
    write(out/'results.json',result)
    pd.DataFrame(rows).to_csv(out/'metrics.csv',index=False)
    return result
