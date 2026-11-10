"""Only authorized new fitting: fixed D0/D1/D2 grouped logistic diagnostics."""
import argparse,warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
from .common import read,write,textfile,csvfile,table,config_for,freeze_revision
from .metrics import metrics,paired_bootstrap,interval
from .numerical import load_cohort

class TrainingTransform:
 def fit(self,x):
  x=np.asarray(x,float);valid=np.isfinite(x);counts=valid.sum(0)
  self.mean=np.divide(np.where(valid,x,0).sum(0),counts,out=np.zeros(x.shape[1]),where=counts>0)
  filled=np.where(valid,x,self.mean);self.std=filled.std(0);self.std=np.where(self.std>1e-12,self.std,1.)
  return self
 def transform(self,x):
  x=np.asarray(x,float);return (np.where(np.isfinite(x),x,self.mean)-self.mean)/self.std

def fit_base(action,continuous,y,train,test):
 transform=TrainingTransform().fit(continuous[train])
 design=lambda rows:np.column_stack([action[rows],transform.transform(continuous[rows])])
 with warnings.catch_warnings(record=True) as captured:
  warnings.simplefilter('always')
  model=LogisticRegression(C=1,penalty='l2',solver='lbfgs',max_iter=2000,class_weight=None,random_state=0).fit(design(train),y[train])
 if any(issubclass(w.category,ConvergenceWarning) for w in captured):raise RuntimeError('Diagnostic did not converge at frozen cap; no budget expansion')
 return model.decision_function(design(test)),{'mean':transform.mean.tolist(),'std':transform.std.tolist(),'coef':model.coef_.tolist(),'intercept':model.intercept_.tolist(),'iterations':model.n_iter_.tolist(),'training_rows':np.asarray(train).tolist(),'assessment_rows':np.asarray(test).tolist()}

def choose_threshold(y,p):
 thresholds=np.arange(.01,1,.01);y=np.asarray(y);p=np.asarray(p)
 positives=y==1;negative=~positives;scores=np.array([.5*((p[positives]>=t).mean()+(p[negative]<t).mean()) for t in thresholds])
 tied=thresholds[np.isclose(scores,scores.max(),rtol=0,atol=1e-12)]
 return float(tied[np.argmin(abs(tied-.5))])

def features(c,frame):
 action=np.column_stack([(frame.action==a).astype(float) for a in c['diagnostic']['action_order']]);duration=(frame.end-frame.start).to_numpy();assert np.all(duration>0)
 quality={}
 for rid in sorted(frame.recording_id.unique()):
  rec=read(Path(c['sources']['inventory'])/'records'/f'{rid}.json')
  for seg in rec['segments']:
   values=[]
   for field in c['diagnostic']['coverage_columns']:
    stream,key=field.split('.');value=seg['video']['hand'].get(key) if stream=='hand' else seg['sensor'][stream].get(key)
    values.append(np.nan if value is None else value)
   quality[(rid,str(seg['segment_id']))]=values
 q=np.asarray([quality[(r.recording_id,r.segment_id)] for r in frame.itertuples()],float)
 return action,{'D0':np.empty((len(frame),0)),'D1':np.log(duration)[:,None],'D2':np.column_stack([np.log(duration),q])}

def run(c):
 root=Path(c['run']);out=root/'02_task_and_shortcut_audit';freeze_revision(root,'diagnostics_before_fitting')
 frame,splits=load_cohort(c);y=frame.failure.to_numpy();action,cont=features(c,frame);results={};logs={};rows=[];allfold=[]
 for name,x in cont.items():
  p=np.full(len(frame),np.nan);hard=np.full(len(frame),-1);logs[name]=[]
  for outer in splits['folds']:
   k=outer['fold'];tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']));inner_raw=np.full(len(frame),np.nan);innerlog=[]
   for part in outer['inner']:
    it=np.flatnonzero(frame.recording_id.isin(part['train_recordings']));iv=np.flatnonzero(frame.recording_id.isin(part['validation_recordings']))
    assert not set(frame.iloc[it].recording_id)&set(frame.iloc[iv].recording_id)
    inner_raw[iv],info=fit_base(action,x,y,it,iv);innerlog.append(info)
   assert np.isfinite(inner_raw[tr]).all() and np.isnan(inner_raw[te]).all()
   raw,outerlog=fit_base(action,x,y,tr,te)
   with warnings.catch_warnings(record=True) as captured:
    warnings.simplefilter('always');cal=LogisticRegression(C=1,solver='lbfgs',max_iter=1000,class_weight=None).fit(inner_raw[tr,None],y[tr])
   if any(issubclass(w.category,ConvergenceWarning) for w in captured):raise RuntimeError('Calibration nonconvergence at frozen cap')
   threshold=choose_threshold(y[tr],cal.predict_proba(inner_raw[tr,None])[:,1]);p[te]=cal.predict_proba(raw[:,None])[:,1];hard[te]=p[te]>=threshold
   logs[name].append({'outer_fold':k,'inner_fits':innerlog,'outer_fit':outerlog,'calibration_training_rows':tr.tolist(),'calibration_coef':cal.coef_.tolist(),'calibration_intercept':cal.intercept_.tolist(),'threshold':threshold})
   allfold.append({'model':name,'fold':k,**metrics(y[te],p[te],hard[te])})
  results[name]=p
  frame[['recording_id','segment_id','failure','fold']].assign(p=p,hard=hard).to_csv(out/f'{name}_OOF_predictions.csv',index=False)
  rows.append({'model':name,'status':'COMPLETED_FIXED_SPECIFICATION',**metrics(y,p,hard)})
 # Historical comparators stay frozen; their specification is deliberately distinguished.
 main=root/'01_independent_result_check'
 for model,filename in [('Historical_action','ACTION_HIST_identified.csv'),('U1','U1_identified.csv'),('F2','F2_identified.csv')]:
  q=pd.read_csv(main/filename,dtype={'recording_id':str,'segment_id':str})
  assert np.array_equal(q[['recording_id','segment_id']].values,frame[['recording_id','segment_id']].values)
  results[model]=q.p.to_numpy();rows.append({'model':model,'status':'REUSED_FROZEN_PREDICTIONS',**metrics(y,q.p,q.hard)})
 boot=paired_bootstrap(y,results,frame.recording_id,replicates=c['bootstrap_replicates'],seed=c['bootstrap_seed']);contrasts=[]
 pairs=[('D1','D0'),('D2','D1'),('D0','Historical_action')]+[(d,ref) for d in ['D0','D1','D2'] for ref in ['U1','F2']]
 points={r['model']:r for r in rows}
 for a,b in pairs:
  for j,m in enumerate(['AUPRC','AUROC','Brier']):contrasts.append({'contrast':a+' minus '+b,'metric':m,'estimate':points[a][m]-points[b][m],**interval(boot[a][:,j]-boot[b][:,j])})
 csvfile(out/'diagnostic_baselines.csv',rows);csvfile(out/'diagnostic_paired.csv',contrasts);csvfile(out/'diagnostic_fold_metrics.csv',allfold)
 write(out/'diagnostic_fitting_scope.json',{'features':c['diagnostic'],'fits':logs,'no_outer_labels_in_fit':True,'seed_note':'deterministic lbfgs random_state0; fold split identities fixed; no seed search','historical_difference':'D0 uses fixed C1/unweighted fit; original action-only used class-balanced fitting and C grid. Calibration/threshold rules are reused.'})
 textfile(out/'DIAGNOSTIC_RESULTS.md','# Fixed metadata diagnostic family\n\nQuestion: can action, full completed duration and audited coverage/missingness predict annotated failure? Reason: test an alternative explanation for observed task performance without asserting that a signal model uses it. No exact matching duration+coverage family was retained; the historical action model is reused as a separately specified comparator.\n\nD0 action only; D1 adds log positive duration; D2 adds the22 frozen coverage/missingness fields. Every fit uses fixed C1/L2/lbfgs/unweighted/max_iter2000. Training-only transforms, calibration and threshold selection; original outer/inner recording partitions. No tuning/search. Inputs and fit row identities are retained in diagnostic_fitting_scope.json; all OOF exports contain composite IDs.\n\n'+table(pd.DataFrame(rows))+'\n\n'+table(pd.DataFrame(contrasts))+'\nThese post-hoc diagnostics measure acquisition/task-metadata predictiveness. They do not show that U1/F2 exploits a particular shortcut, remove sensor information, or justify relabelling data. Fixed D0 differs from the historical balanced/C-selected action baseline. All results, including deterioration and uncertain differences, are retained. Duration is available after action completion, not at action start. Intervals use2000 paired recording draws and condition on these fitted models.')
 print('DIAGNOSTICS_COMPLETE',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();run(config_for(a.run))
