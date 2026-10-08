"""Task-4-dependent isolated execution; abort on cache or historical parity failure."""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
from pathlib import Path
import argparse,fcntl,json,shutil,signal,subprocess,sys,time
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
import numpy as np,torch
from threadpoolctl import threadpool_limits
from reassemble.section1b import index_plan,guard_partition,fit_stacker
from reassemble.section1_report import metrics
from .common import read,write,status,identity,sha,snapshot,verify_snapshot,atomic_npz,storage
from .preflight import load
from .training import branch
STOP=False

def stop(*unused):
 global STOP
 STOP=True

def deadline():
 now=datetime.now(ZoneInfo('Europe/Berlin'));cut=now.replace(hour=5,minute=30,second=0,microsecond=0)
 if cut<=now<now.replace(hour=6,minute=10,second=0,microsecond=0):raise InterruptedError('Daily reset pause window')
 if now>=cut:cut+=timedelta(days=1)
 return cut.astimezone(timezone.utc)

def signature():
 paths=list(Path('src/reassemble/boundary_visual').glob('*.py'))+[Path('src/reassemble')/n for n in ['section1_models.py','section1_features.py','section1b.py','section1_report.py','cluster_metrics.py','alignment.py']]
 return [identity(p) for p in sorted(paths)]

def wait_task4(run,c,pause):
 dep=Path(c['task4_dependency']);last=None
 while True:
  pause();s=read(dep/'status.json')['tasks']['04_corruption_training'];state=s['state']
  if state=='complete':
   manifests=sorted((dep/'recovery/task4').glob('*/completion_manifest.json'))
   assert manifests and read(manifests[-1])['preservation_passed'],'Task4 completion receipt missing'
   # Coordinator writes complete just before exiting; allow it to release its lock.
   with (dep/'supervisor.lock').open('r') as lock:
    try:fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
    except BlockingIOError:time.sleep(5);continue
   write(run/'task4_dependency_complete.json',{'task_status':s,'receipt':identity(manifests[-1])})
   return
  if state.startswith('failed'):raise RuntimeError('Task4 failed; follow-up must not start: '+s['stage'])
  if state!=last:status(run,'QUEUED_AFTER_TASK4','Task4 state: '+state);last=state
  time.sleep(15)

def preservation_roots(c):
 roots=[str(p) for p in Path('runs/reassemble').iterdir() if p.is_dir() and p.name!='additional_improvements_executed']
 roots += [c['task4_dependency'],'artifacts/reassemble/reports','artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z/04_human_review/submissions','../datasets/REASSEMBLE/raw/data']
 return roots

def run_visual(run,c,base,frame,splits,seq,mean,fold,pause):
 y=frame.failure.to_numpy(int);predictions={}
 with np.load(Path(base['run_dir'])/'predictions/rtdetr_perm00.npz') as z:historic={k:z[k] for k in ['p','hard','raw','y','fold']}
 for variant in ['V0','V1','V2','V3','V4','V5']:
  if variant!='V0':assert read(run/'control_parity.json')['passed']
  values={'p':np.full(len(y),np.nan),'hard':np.zeros(len(y),int),'raw':np.full(len(y),np.nan),'retained':np.zeros((3,len(y)),bool)};logs=[]
  for outer in splits['folds']:
   k=outer['fold'];tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']))
   out,info=branch(run,f'{variant}/outer{k}',variant,seq,mean,y,frame,tr,te,index_plan(frame,outer),base,base['seed']+100*k,base['seed']+100*k+99,pause)
   for key in ['p','hard','raw']:values[key][te]=out[key]
   for j,cut in enumerate(out['coverage_cutoffs']):values['retained'][j,te]=abs(out['p']-.5)>=cut
   logs.append(info)
   if variant=='V0':
    previous=read(Path(base['run_dir'])/'predictions'/f'rtdetr_perm00_fold{k}.json');delta=float(np.max(abs(out['p']-historic['p'][te])))
    check={'fold':k,'max_probability_difference':delta,'tolerance':1e-5,'selected_epochs_equal':info['selected']==previous['selected'],'hard_equal':bool(np.array_equal(out['hard'],historic['hard'][te]))}
    write(run/f'control_fold{k}_parity.json',check)
    assert delta<=1e-5 and check['selected_epochs_equal'] and check['hard_equal'],('Historical control parity failed',check)
   status(run,'RUNNING',f'{variant}: outer fold {k+1}/5 complete')
  values.update(y=y,fold=fold);path=run/'predictions'/(variant+'.npz')
  if not path.exists():atomic_npz(path,**values)
  else:
   with np.load(path) as z:
    for key in values:assert np.array_equal(z[key],values[key],equal_nan=True)
  write(run/'predictions'/(variant+'.json'),{'folds':logs,'output':identity(path)});predictions[variant]=values
  if variant=='V0':
   observed=metrics(y,values['p'],values['hard']);expected=metrics(y,historic['p'],historic['hard'])
   check={'passed':bool(np.max(abs(observed-expected))<=1e-5),'metric_max_abs':float(np.max(abs(observed-expected))),'max_probability_difference':float(np.max(abs(values['p']-historic['p']))),'historical_metrics':expected.tolist(),'reproduced_metrics':observed.tolist(),'probability_tolerance':1e-5}
   write(run/'control_parity.json',check);assert check['passed'],'Historical metric parity failed'
 return predictions

def fusion(run,c,base,frame,splits,seq,mean,fold,variant,predictions,pause):
 sb=read('configs/reassemble/section1b.json');old=Path(sb['run_dir'])/'stacking';y=frame.failure.to_numpy(int);n=len(y);p=np.full(n,np.nan);hard=np.zeros(n,int)
 with np.load(Path(base['run_dir'])/'predictions/sensor_statistics_perm00.npz') as z:
  assert np.array_equal(z['y'],y) and np.array_equal(z['fold'],fold);sensor=z['p'].copy()
 sources=[]
 for outer in splits['folds']:
  pause();k=outer['fold'];plan=index_plan(frame,outer);tr=np.flatnonzero(frame.recording_id.isin(outer['train_recordings']));te=np.flatnonzero(frame.recording_id.isin(outer['test_recordings']));meta=np.full((n,2),np.nan);original_meta=np.full((n,2),np.nan)
  for j,(it,iv) in enumerate(plan):
   file=old/f'outer{k}_inner{j}.npz';detail=read(file.with_suffix('.json'));sources.extend([identity(file),identity(file.with_suffix('.json'))])
   assert set(detail['train_recordings'])==set(frame.iloc[it].recording_id) and set(detail['validation_recordings'])==set(frame.iloc[iv].recording_id)
   sub=[(np.flatnonzero(frame.recording_id.isin(s['train_recordings'])),np.flatnonzero(frame.recording_id.isin(s['validation_recordings']))) for s in detail['subfolds']];guard_partition(frame,it,iv,sub)
   seed=sb['seed']+sb['subfit_seed_offset']+1000*k+100*j
   out,info=branch(run,f'fusion/{variant}/outer{k}/inner{j}',variant,seq,mean,y,frame,it,iv,sub,base,seed,seed+99,pause)
   with np.load(file) as z:
    assert np.array_equal(z['validation_rows'],iv);original_meta[iv]=z['probabilities'];meta[iv,1]=z['probabilities'][:,1]
   meta[iv,0]=out['p'];status(run,'RUNNING',f'Conditional static fusion outer{k+1}/5 inner{j+1}/4 complete')
  assert np.isfinite(meta[tr]).all() and np.isnan(meta[te]).all()
  # Reproduce original F2 before using exactly the same stacker on changed visual inputs.
  with np.load(old/f'outer{k}.npz') as z:
   assert np.array_equal(z['test_rows'],te) and np.array_equal(z['train_rows'],tr)
   assert np.array_equal(z['training_branch_oof'],original_meta[tr])
   rp,rh,_=fit_stacker(original_meta,y,tr,plan,z['test_branch_probabilities'],sb['stacker'])
   assert np.max(abs(rp-z['p']))<=1e-5 and np.array_equal(rh,z['hard']),'Original F2 parity failure'
  p[te],hard[te],log=fit_stacker(meta,y,tr,plan,np.c_[predictions[variant]['p'][te],sensor[te]],sb['stacker'])
  path=run/'fusion'/f'outer{k}.npz'
  if not path.exists():atomic_npz(path,p=p[te],hard=hard[te],train_rows=tr,test_rows=te,training_branch_oof=meta[tr])
  write(path.with_suffix('.json'),log)
 write(run/'fusion/input_identities.json',sources)
 path=run/'fusion/oof.npz'
 if not path.exists():atomic_npz(path,p=p,hard=hard,y=y,fold=fold)
 with np.load(old/'oof.npz') as z:original={key:z[key] for key in ['p','hard','y','fold']}
 assert np.array_equal(original['y'],y) and np.array_equal(original['fold'],fold)
 return {'p':p,'hard':hard,'y':y,'fold':fold},original

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True);args=parser.parse_args();run=args.run;c=read(run/'config.json');lock=(run/'execution.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  assert signature()==read(run/'source_signature.json'),'Implementation changed; explicit review required'
  limit=deadline()
  def pause():
   if STOP or datetime.now(timezone.utc)>=limit:raise InterruptedError('Safe pause before next fit/stage; resume after reset with same config/source')
  wait_task4(run,c,pause);pause();storage(run)
  if not (run/'preservation_before.json').exists():write(run/'preservation_before.json',snapshot(preservation_roots(c)))
  status(run,'PREFLIGHT','Verifying frozen frame cache, cohort and fold identities')
  c,base,frame,splits,seq,mean,fold,preflight=load(run);assert preflight==read(run/'cache_preflight.json'),'Preflight changed since registration'
  torch.set_num_threads(base['threads']);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False
  if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable; cannot reproduce historical GPU head')
  write(run/'runtime.json',{'torch':torch.__version__,'numpy':np.__version__,'gpu':torch.cuda.get_device_name(0),'blas_threads':16,'torch_threads':base['threads']})
  with threadpool_limits(limits=16,user_api='blas'):predictions=run_visual(run,c,base,frame,splits,seq,mean,fold,pause)
  from .report import analyse,finish
  pause();status(run,'ANALYSIS','Paired clustered comparisons and selective-prediction diagnostics')
  with threadpool_limits(limits=1):results=analyse(run,c,frame,fold,predictions)
  fusion_result=None
  if results['class']=='A':
   pause();status(run,'RUNNING','Class A triggered exactly one frozen-sensor/static-stacking follow-up')
   with threadpool_limits(limits=16,user_api='blas'):new,original=fusion(run,c,base,frame,splits,seq,mean,fold,results['fusion_variant'],predictions,pause)
   from .report import fusion_analysis
   with threadpool_limits(limits=1):fusion_result=fusion_analysis(run,c,frame,new,original)
  preservation=verify_snapshot(read(run/'preservation_before.json'));write(run/'preservation_after.json',preservation)
  finish(run,c,frame,predictions,results,fusion_result);status(run,'COMPLETE','All bounded variants, diagnostics and conditional follow-up complete; STOP')
  write(run/'output_manifest.json',{'files':[identity(p) for p in sorted(run.rglob('*')) if p.is_file() and p.name not in ['output_manifest.json','execution.log','execution.lock']]})
 except InterruptedError as e:status(run,'PAUSED_AT_UNIT_BOUNDARY',str(e))
 except BaseException as e:
  write(run/('failure_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json'),{'type':type(e).__name__,'error':str(e)})
  status(run,'BLOCKED_REQUIRES_REVIEW',str(e))
  message='# Boundary-aware visual experiment — BLOCKED\n\nNo completion or result class is claimed.\n\nBlocker: '+str(e)+'\n\nRun: `'+str(run)+'`. See protocol.md, status.json, failure logs and control/cache parity evidence. Stop dependent interpretation; no tolerance or scientific procedure was silently changed. Task1 stays paused and Task4 is not modified.\n'
  for name in ['BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md','BOUNDARY_AWARE_VISUAL_STATUS.md','BOUNDARY_AWARE_VISUAL_STORYLINE_ADDENDUM.md']:
   target=Path('artifacts/reassemble/reports')/name
   if not target.exists():target.write_text(message)
  raise
if __name__=='__main__':main()
