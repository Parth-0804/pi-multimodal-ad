"""Evaluate only directly keyed, genuinely held-out predictions on paired folds."""
import json,time
import numpy as np,pandas as pd
from sklearn.metrics import (average_precision_score,roc_auc_score,precision_score,
 recall_score,balanced_accuracy_score,f1_score,brier_score_loss,precision_recall_curve)
from common import ROOT,CONDITIONS,read,write,sha,event,save_csv,config

BRANCHES=('visual','sensor','fused')
def metrics(y,p):
 y=np.asarray(y,int);p=np.asarray(p,float)
 assert len(y)==len(p) and len(y)>0 and np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
 d=p>=.5;both=len(np.unique(y))==2
 return {'AP':float(average_precision_score(y,p)) if y.sum()>0 else None,
  'AUROC':float(roc_auc_score(y,p)) if both else None,'precision':float(precision_score(y,d,zero_division=0)),
  'recall':float(recall_score(y,d,zero_division=0)),'balanced_accuracy':float(balanced_accuracy_score(y,d)) if both else None,
  'macro_F1':float(f1_score(y,d,labels=[0,1],average='macro',zero_division=0)),
  'Brier':float(brier_score_loss(y,p)),'samples':len(y),'failures':int(y.sum()),'prevalence':float(y.mean()),'threshold':.5}
def paired_predictions():
 folds=[];sources={};tables={name:[] for name in CONDITIONS}
 for k in range(1,6):
  fold=f'fold_{k:02d}'
  if not all((ROOT/name/fold/'condition_complete.json').exists() for name in CONDITIONS):continue
  group={}
  for name in CONDITIONS:
   path=ROOT/name/fold/'assessment_predictions.csv';done=read(path.parent/'condition_complete.json')
   assert sha(path)==done['assessment_sha256']
   z=pd.read_csv(path,dtype={'recording_id':str,'segment_id':str}).sort_values('sample_id').reset_index(drop=True)
   assert not z.sample_id.duplicated().any() and (z.fold_name==fold).all()
   group[name]=z;sources[str(path.relative_to(ROOT))]=sha(path)
  reference=group[CONDITIONS[0]]
  for name,z in group.items():
   assert z[['sample_id','recording_id','segment_id','failure']].equals(reference[['sample_id','recording_id','segment_id','failure']])
   assert np.allclose(z.p_sensor,reference.p_sensor,rtol=0,atol=1e-14),'UNSHARED_SENSOR_PREDICTIONS'
   tables[name].append(z)
  folds.append(fold)
 if not folds:return folds,{},sources
 result={name:pd.concat(rows,ignore_index=True).sort_values('sample_id').reset_index(drop=True) for name,rows in tables.items()}
 assert not result[CONDITIONS[0]].sample_id.duplicated().any(),'REPEATED_OUTER_SAMPLE'
 return folds,result,sources
def contrasts(values):
 out={}
 for b in ['visual','fused']:
  a,c,d,e=[values[(name,b)] for name in CONDITIONS]
  out[b+':fine_tuned16_minus_frozen16']=c-a
  out[b+':frozen32_minus_frozen16']=d-a
  out[b+':fine_tuned32_minus_fine_tuned16']=e-c
  out[b+':interaction']=(e-d)-(c-a)
 for name in CONDITIONS:out[name+':F2_minus_sensor']=values[(name,'fused')]-values[(name,'sensor')]
 return out
def bootstrap(tables):
 c=config();reference=tables[CONDITIONS[0]];y=reference.failure.to_numpy(int)
 ids=sorted(reference.recording_id.unique());lookup={v:i for i,v in enumerate(ids)};cluster=reference.recording_id.map(lookup).to_numpy(int)
 point={(n,b):float(average_precision_score(y,z['p_'+b])) for n,z in tables.items() for b in BRANCHES}
 delta=contrasts(point);samples={key:[] for key in delta};rng=np.random.default_rng(c['evaluation_seed']);draw_rows=[];valid=0
 # Integer per-recording multiplicities retain every segment and repeated clusters.
 for rep in range(c['bootstrap_replicates']):
  counts=np.bincount(rng.integers(0,len(ids),len(ids)),minlength=len(ids));w=counts[cluster];positive=int(w@y);total=int(w.sum());ok=0<positive<total
  draw_rows.append({'replicate':rep,'valid_two_classes':ok,'weighted_samples':total,'weighted_failures':positive,'recording_multiplicities':json.dumps(counts.tolist(),separators=(',',':'))})
  if not ok:continue
  values={};sensor=None
  for n,z in tables.items():
   for b in BRANCHES:
    if b=='sensor' and sensor is not None:values[(n,b)]=sensor;continue
    values[(n,b)]=float(average_precision_score(y,z['p_'+b],sample_weight=w))
    if b=='sensor':sensor=values[(n,b)]
  for key,value in contrasts(values).items():samples[key].append(value)
  valid+=1
  if (rep+1)%250==0:event('EVALUATING_PAIRED_BOOTSTRAP',replicates=rep+1,valid=valid)
 save_csv(ROOT/'comparison/bootstrap_draws.csv',pd.DataFrame(draw_rows));write(ROOT/'comparison/bootstrap_recording_order.json',ids)
 rows=[]
 for key,value in delta.items():
  v=samples[key];lo,hi=np.percentile(v,[2.5,97.5]) if v else [None,None]
  rows.append({'contrast':key,'AP_difference':value,'percentile_95_low':lo,'percentile_95_high':hi,'replicates_requested':c['bootstrap_replicates'],'valid_replicates':valid,'undefined_discarded':c['bootstrap_replicates']-valid,'seed':c['evaluation_seed'],'primary':key=='fused:fine_tuned16_minus_frozen16','interpretation':'Conditional recording-cluster sampling uncertainty; secondary intervals unadjusted/exploratory; no repeated-training uncertainty'})
 write(ROOT/'comparison/bootstrap_policy.json',{'seed':c['evaluation_seed'],'replicates':c['bootstrap_replicates'],'valid':valid,'undefined_discarded':c['bootstrap_replicates']-valid,'undefined_policy':'Discard resamples lacking either truth class; fixed draw count, no replacement draws','recording_order_sha256':sha(ROOT/'comparison/bootstrap_recording_order.json'),'draws_sha256':sha(ROOT/'comparison/bootstrap_draws.csv'),'all_methods_share_multiplicities':True})
 return pd.DataFrame(rows)
def examples(tables):
 a=tables['frozen_16_frames'];b=tables['fine_tuned_16_frames'];out=a[['sample_id','recording_id','segment_id','failure','action','start','end','fold_name']].copy();eps=np.finfo(float).eps
 for tag,z in [('frozen16',a),('fine_tuned16',b)]:
  for branch in BRANCHES:out[tag+'_p_'+branch]=z['p_'+branch].to_numpy()
  true=np.where(z.failure.to_numpy()==1,z.p_fused,1-z.p_fused);out[tag+'_true_class_log_loss']=-np.log(np.clip(true,eps,1))
 out['log_loss_reduction']=out.frozen16_true_class_log_loss-out.fine_tuned16_true_class_log_loss
 frame={s['sample_id']:s for s in read(ROOT/'data_manifests/cohort_and_frames.json')};selected=[];coverage=[]
 for truth in [0,1]:
  for direction,ascending in [('improvement',False),('deterioration',True)]:
   z=out.loc[(out.failure==truth)&((out.log_loss_reduction>0) if direction=='improvement' else (out.log_loss_reduction<0))].sort_values(['log_loss_reduction','sample_id'],ascending=[ascending,True]).head(3).copy();z['selection']=direction
   coverage.append({'truth':truth,'direction':direction,'requested':3,'available_selected':len(z)});selected.append(z)
 chosen=pd.concat(selected,ignore_index=True)
 for key in ['frames16','frames32','timestamps16','timestamps32']:chosen[key]=chosen.sample_id.map(lambda i:json.dumps(frame[i][key],separators=(',',':')))
 save_csv(ROOT/'comparison/changed_predictions.csv',chosen)
 write(ROOT/'comparison/changed_prediction_policy.json',{'selection':'For each truth class, three greatest strictly positive and three greatest strictly negative F2 true-class log-loss reductions, fine_tuned16 versus frozen16; ties ascending sample_id; zero changes excluded','endpoint':'F2 probability','selected':len(chosen),'overlap':bool(chosen.sample_id.duplicated().any()),'coverage':coverage,'interpretation':'Deliberately selected illustrations, not independent statistical evidence'})
def cost_tables():
 rows=[];lineage=[]
 for name in CONDITIONS:
  for path in sorted((ROOT/name).glob('fold_*/**/visual_fit/complete.json')):
   d=read(path);row={'condition':name,'fold':d['job']['fold_name'],'role':d['job']['role'],'fit_id':d['fit_id'],'G_samples':len(d['job']['G']),'C_samples':len(d['job']['C']),'prediction_samples':len(d['job']['predict'])}
   for key in ['epochs_complete','optimizer_updates','training_segments_presentations','training_wall_seconds','cuda_event_seconds_including_host_gaps','peak_cuda_bytes','head_parameters','loaded_backbone_parameters','trainable_backbone_parameters']:row[key]=d[key]
   row['C_prediction_seconds']=d['raw_prediction_cost_C']['seconds'];row['V_prediction_seconds']=d['raw_prediction_cost_V']['seconds'];row['model_bytes']=path.with_name('model.pt').stat().st_size;rows.append(row)
   row['full_pixel_replay_seconds']=d['replay']['inference_cost']['seconds'];row['full_pixel_replay_segments']=len(d['replay']['sample_ids']);row['calibrator_fit_seconds']=d.get('calibrator_fit_seconds',0.);row['total_branch_parameters']=d['loaded_backbone_parameters']+d['head_parameters'];row['total_trainable_parameters']=d['trainable_backbone_parameters']+d['head_parameters']
   row['cuda_model_optimizer_seconds_excluding_pixel_load']=d['cuda_model_optimizer_seconds_excluding_pixel_load']
   lineage.append({'fit_id':d['fit_id'],'kind':'visual','condition':name,'fold':d['job']['fold_name'],'role':d['job']['role'],'manifest':str(path.relative_to(ROOT)),'manifest_sha256':sha(path),'model':str(path.with_name('model.pt').relative_to(ROOT)),'model_sha256':d['model_sha256']})
 for path in sorted((ROOT/'sensor_reference').glob('fold_*/*/complete.json')):
  d=read(path);lineage.append({'fit_id':d['fit_id'],'kind':'sensor','fold':d['job']['fold_name'],'role':d['job']['role'],'manifest':str(path.relative_to(ROOT)),'manifest_sha256':sha(path)})
 for name in CONDITIONS:
  for path in sorted((ROOT/name).glob('fold_*/F2_stacker.json')):
   d=read(path);lineage.append({'fit_id':d['fit_id'],'kind':'F2_probability_stacker','condition':name,'fold':path.parent.name,'manifest':str(path.relative_to(ROOT)),'manifest_sha256':sha(path),'raw_branch_lineage':d['lineage']})
 save_csv(ROOT/'comparison/fit_costs_and_parameters.csv',pd.DataFrame(rows));write(ROOT/'data_manifests/fit_lineage_index.json',lineage)
 return pd.DataFrame(rows)
def plots(tables,metric_rows,costs):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 target=ROOT/'comparison/plots';target.mkdir(exist_ok=True)
 fig,ax=plt.subplots(figsize=(8,6))
 for name,z in tables.items():
  for branch,style in [('visual','--'),('fused','-')]:
   pr,re,_=precision_recall_curve(z.failure,z['p_'+branch]);ax.plot(re,pr,style,label=f'{name} {branch}')
 z=tables[CONDITIONS[0]];pr,re,_=precision_recall_curve(z.failure,z.p_sensor);ax.plot(re,pr,color='black',label='shared sensor');ax.axhline(z.failure.mean(),color='gray',linestyle=':',label='prevalence');ax.set(xlabel='Failure recall',ylabel='Failure precision',title='Pooled held-out precision–recall on paired folds');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(target/'pooled_precision_recall.png',dpi=160);plt.close(fig)
 reliability=[]
 for name,z in tables.items():
  for branch in BRANCHES:
   p=z['p_'+branch].to_numpy();y=z.failure.to_numpy();bins=np.minimum((p*10).astype(int),9)
   for k in range(10):
    keep=bins==k;reliability.append({'condition':name,'branch':branch,'bin':k,'lower_inclusive':k/10,'upper_exclusive_except_one':(k+1)/10,'samples':int(keep.sum()),'mean_probability':p[keep].mean() if keep.any() else np.nan,'observed_failure_fraction':y[keep].mean() if keep.any() else np.nan})
 r=pd.DataFrame(reliability);save_csv(ROOT/'comparison/reliability_bins.csv',r);fig,ax=plt.subplots(figsize=(7,6));ax.plot([0,1],[0,1],':',color='gray')
 for name in CONDITIONS:
  for branch,style in [('visual','--'),('fused','-')]:
   q=r.loc[(r.condition==name)&(r.branch==branch)&(r.samples>0)];ax.plot(q.mean_probability,q.observed_failure_fraction,style,marker='o',markersize=3,label=f'{name} {branch}')
 q=r.loc[(r.condition==CONDITIONS[0])&(r.branch=='sensor')&(r.samples>0)];ax.plot(q.mean_probability,q.observed_failure_fraction,color='black',marker='o',label='shared sensor');ax.set(xlabel='Mean predicted probability',ylabel='Observed failure fraction',title='Reliability: ten fixed equal-width bins');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(target/'pooled_reliability.png',dpi=160);plt.close(fig)
 curves=[]
 for name in CONDITIONS:
  for p in sorted((ROOT/name).glob('fold_*/**/visual_fit/learning_curve.csv')):
   q=pd.read_csv(p);q['condition']=name;q['source']=str(p.relative_to(ROOT));curves.append(q)
 if curves:
  curves=pd.concat(curves,ignore_index=True);save_csv(ROOT/'comparison/all_training_loss_curves.csv',curves);fig,ax=plt.subplots(figsize=(7,5))
  for name,z in curves.groupby('condition'):
   g=z.groupby('epoch').training_BCE_mean;ax.plot(g.mean().index,g.mean().values,marker='o',label=name)
  ax.set(xlabel='Epoch (final weights always epoch 5)',ylabel='Mean of fit training BCE means',title='Training losses; no assessment-based stopping');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(target/'training_loss_trajectories.png',dpi=160);plt.close(fig)
def evaluate():
 started=time.perf_counter();folds,tables,sources=paired_predictions();costs=cost_tables();rows=[]
 if tables:
  for name,z in tables.items():
   for branch in BRANCHES:
    for fold,q in [('pooled',z),*list(z.groupby('fold_name'))]:rows.append({'condition':name,'branch':branch,'scope':fold,'recordings':q.recording_id.nunique(),'completed_paired_folds':len(folds),'base_seed':42,**metrics(q.failure,q['p_'+branch])})
  paired=bootstrap(tables);examples(tables);plots(tables,rows,costs)
 else:
  paired=pd.DataFrame(columns=['contrast','AP_difference','percentile_95_low','percentile_95_high']);save_csv(ROOT/'comparison/changed_predictions.csv',pd.DataFrame(columns=['sample_id','recording_id','segment_id','selection']))
 m=pd.DataFrame(rows,columns=['condition','branch','scope','recordings','completed_paired_folds','base_seed','AP','AUROC','precision','recall','balanced_accuracy','macro_F1','Brier','samples','failures','prevalence','threshold']);save_csv(ROOT/'comparison/comparison_metrics.csv',m);save_csv(ROOT/'comparison/paired_comparisons.csv',paired)
 four=[]
 for name in CONDITIONS:
  z={'condition':name,'completed_paired_folds':len(folds),'status':'COMPLETE' if len(folds)==5 else 'PARTIAL' if folds else 'NOT_RUN_OR_UNPAIRED','samples':len(tables[name]) if tables else 0}
  for b in BRANCHES:
   q=m.loc[(m.condition==name)&(m.branch==b)]
   z[b+'_pooled_AP']=float(q.loc[q.scope=='pooled','AP'].iloc[0]) if len(q) else None;z[b+'_mean_fold_AP']=float(q.loc[q.scope!='pooled','AP'].mean()) if len(q) else None
  four.append(z)
 save_csv(ROOT/'comparison/four_condition_comparison.csv',pd.DataFrame(four))
 write(ROOT/'comparison/evaluation.json',{'status':'COMPLETE' if len(folds)==5 else 'PARTIAL' if folds else 'INCOMPLETE','paired_folds':folds,'prediction_sources':sources,'common_samples':len(next(iter(tables.values()))) if tables else 0,'comparison':four,'evaluation_seconds':time.perf_counter()-started,'AP_definition':'sklearn.metrics.average_precision_score; stepwise AP, not trapezoidal PR area','threshold':.5,'bootstrap_seed':314159,'no_unpaired_condition_ranking':True,'code':sha(ROOT/'source/evaluation.py')})
 event('EVALUATION_COMPLETE',completed_paired_folds=len(folds))
