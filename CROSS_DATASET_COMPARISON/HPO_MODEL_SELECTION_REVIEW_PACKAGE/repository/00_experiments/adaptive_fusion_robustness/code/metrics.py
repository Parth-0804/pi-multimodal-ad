"""Matched per-fold/pooled metrics and within-fold recording bootstrap."""
import numpy as np,pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,precision_score,recall_score,confusion_matrix
from common import *
from study import MODELS
ALL_MODELS=MODELS+['visual','sensor']
PRIMARY=['image_noise','sensor_noise']
KEYS=['recording_id','segment_id']
def metrics(y,p):
 d=p>=.5;tn,fp,fn,tp=confusion_matrix(y,d,labels=[0,1]).ravel()
 return {'AP':float(average_precision_score(y,p)),'AUROC':float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,'Brier':float(brier_score_loss(y,p)),'precision':float(precision_score(y,d,zero_division=0)),'recall':float(recall_score(y,d,zero_division=0)),'TN':int(tn),'FP':int(fp),'FN':int(fn),'TP':int(tp)}
def weighted_bootstrap_ap(y,p,weights):
 """Exactly weighted AP, including ties and repeated-record multiplicities."""
 order=np.argsort(-p,kind='stable');y=np.asarray(y)[order];p=np.asarray(p)[order];ends=np.r_[np.flatnonzero(np.diff(p)!=0),len(p)-1];out=[]
 for offset in range(0,len(weights),100):
  w=weights[offset:offset+100][:,order];tp=np.cumsum(w*y,axis=1)[:,ends];total=np.cumsum(w,axis=1)[:,ends];increments=np.diff(np.c_[np.zeros(len(w)),tp],axis=1);precision=np.divide(tp,total,out=np.zeros_like(tp),where=total>0);denominator=tp[:,-1]
  out.extend(np.divide(np.sum(increments*precision,axis=1),denominator,out=np.full(len(w),np.nan),where=denominator>0))
 return np.asarray(out)
def hierarchy(values):
 # values maps fold -> family -> severity -> repeat -> metric (scalar or vector).
 return np.mean([np.mean([np.mean([np.mean(list(repeats.values()),axis=0) for repeats in levels.values()],axis=0) for levels in families.values()],axis=0) for families in values.values()],axis=0)
def aggregate(banks,model,select):
 tree={}
 for (fold,family,level,repeat),scores in banks.items():
  if select(family,level,repeat) and model in scores:tree.setdefault(fold,{}).setdefault(family,{}).setdefault(level,{})[repeat]=scores[model]
 assert tree;return hierarchy(tree)
def evaluate():
 folds=config()['locked_folds'];rng=np.random.default_rng(314159);tables={};points={};boots={};rows=[];coverage=[];replicates=2000;invalid=np.zeros(replicates,dtype=bool);draw_hashes={}
 for fold in folds:
  done=read(RUN/'predictions'/fold/'complete.json');clean_path=RUN/'predictions'/fold/'clean/clean/repeat_00/predictions.csv';clean=pd.read_csv(clean_path,dtype={k:str for k in KEYS}).sort_values(KEYS).reset_index(drop=True);y=clean.failure.to_numpy();groups=clean.recording_id.to_numpy();unique=np.unique(groups);counts=rng.multinomial(len(unique),np.ones(len(unique))/len(unique),size=replicates);weights=counts[:,np.searchsorted(unique,groups)].astype(float);pos=weights@y;neg=weights@(1-y);invalid|=(pos==0)|(neg==0);draw_hashes[fold]=__import__('hashlib').sha256(counts.astype('<i8').tobytes()).hexdigest()
  for relative,digest in done['outputs'].items():
   path=RUN/'predictions'/fold/relative;assert sha(path)==digest;t=pd.read_csv(path,dtype={k:str for k in KEYS}).sort_values(KEYS).reset_index(drop=True);assert not t.duplicated(KEYS).any() and t[KEYS].equals(clean[KEYS]) and np.array_equal(t.failure,y);family,level,repeat=t.family.iloc[0],t.level.iloc[0],int(t.repeat.iloc[0]);key=(fold,family,level,repeat);tables[key]=t;points[key]={};boots[key]={}
   assert len(t)==len(clean);coverage.append({'fold':fold,'family':family,'level':level,'repeat':repeat,'expected':len(clean),'actual':len(t),'OK':int(t.status.eq('OK').sum()),'unavailable':int(t.status.eq('UNAVAILABLE').sum()),'failed':int((~t.status.isin(['OK','UNAVAILABLE'])).sum()),'path':str(path.relative_to(RUN)),'sha256':digest})
   if family in ['image_noise','image_blur']:np.testing.assert_array_equal(t.p_sensor,clean.p_sensor)
   if family in ['sensor_noise','sensor_time_loss']:np.testing.assert_array_equal(t.p_visual,clean.p_visual)
   for model in ALL_MODELS:
    p=t['p_'+model].to_numpy(float);finite=np.isfinite(p);record={'fold':fold,'scope':'fold','family':family,'level':level,'repeat':repeat,'model':model,'samples':len(t),'finite_predictions':int(finite.sum())}
    if not finite.all():rows.append({**record,'status':'UNAVAILABLE_OR_INCOMPLETE'});continue
    assert (p>=0).all() and (p<=1).all();m=metrics(y,p);rows.append({**record,'status':'COMPLETE',**m});points[key][model]=m['AP'];boots[key][model]=weighted_bootstrap_ap(y,p,weights)
  guard(scientific=False)
 # Pooled scores remain separate from equal-weight mean-fold scores.
 for family,level,repeat in sorted({key[1:] for key in tables}):
  t=pd.concat([tables[(fold,family,level,repeat)] for fold in folds]);assert not t.duplicated(KEYS).any()
  for model in ALL_MODELS:
   p=t['p_'+model].to_numpy(float)
   if np.isfinite(p).all():rows.append({'fold':'all','scope':'pooled','family':family,'level':level,'repeat':repeat,'model':model,'samples':len(t),'finite_predictions':len(t),'status':'COMPLETE',**metrics(t.failure.to_numpy(),p)})
 out=RUN/'comparison';out.mkdir(exist_ok=True);pd.DataFrame(rows).to_csv(out/'per_condition_metrics.csv',index=False,float_format='%.17g');pd.DataFrame(coverage).to_csv(out/'coverage_and_prediction_index.csv',index=False)
 contrasts=[]
 def contrast(name,a,b,selector,primary=False):
  point=float(aggregate(points,a,selector)-aggregate(points,b,selector));values=aggregate(boots,a,selector)-aggregate(boots,b,selector);valid=(~invalid)&np.isfinite(values);lo,hi=np.percentile(values[valid],[2.5,97.5]) if valid.any() else (np.nan,np.nan)
  contrasts.append({'contrast':name,'primary':primary,'AP_difference':point,'lower95':float(lo),'upper95':float(hi),'requested_replicates':replicates,'valid_replicates':int(valid.sum()),'invalid_replicates':int((~valid).sum()),'folds':len(folds),'aggregation':'repeats -> severities -> families -> folds; equal weights at every level'})
 primary=lambda family,level,repeat:family in PRIMARY
 contrast('interaction_minus_augmented_static_PRIMARY','quality_interaction','static_augmented',primary,True)
 contrast('interaction_minus_additive_PRIMARY','quality_interaction','quality_additive',primary)
 contrast('augmented_static_minus_historical_PRIMARY','static_augmented','historical_static',primary)
 for a,b in [('quality_interaction','static_augmented'),('quality_interaction','historical_static'),('quality_additive','static_augmented'),('static_augmented','historical_static')]:contrast(a+'_minus_'+b+'_CLEAN',a,b,lambda fa,le,re:fa=='clean')
 for family in ['image_noise','sensor_noise','image_blur','sensor_time_loss']:
  for level in ['mild','medium','strong']:
   contrast('interaction_minus_augmented_static_'+family+'_'+level,'quality_interaction','static_augmented',lambda fa,le,re,ff=family,ll=level:fa==ff and le==ll)
 summary=[]
 for model in ALL_MODELS:
  family_scores={fa:float(aggregate(points,model,lambda family,level,repeat,ff=fa:family==ff)) for fa in ['image_noise','sensor_noise','image_blur','sensor_time_loss']}
  summary.append({'model':model,'primary_mean_fold_AP':float(aggregate(points,model,primary)),'clean_mean_fold_AP':float(aggregate(points,model,lambda fa,le,re:fa=='clean')),'worst_primary_family_AP':min(family_scores[fa] for fa in PRIMARY),'worst_all_fault_family_AP':min(family_scores.values()),**{fa+'_AP':v for fa,v in family_scores.items()}})
 pd.DataFrame(summary).to_csv(out/'model_comparison.csv',index=False,float_format='%.17g');pd.DataFrame(contrasts).to_csv(out/'paired_intervals.csv',index=False,float_format='%.17g')
 write(RUN/'checks/bootstrap.json',{'seed':314159,'requested':replicates,'recording_draws_sha256':draw_hashes,'invalid_any_fold':int(invalid.sum()),'method':'Multinomial recording multiplicities independently within each fold; same draws for every model, family, severity and realization; exact weighted AP with ties.','uncertainty':'Conditional on fixed fits and realizations; development-exposed; secondary intervals unadjusted.'});state('EVALUATED',completed_folds=folds)
