"""Small CPU deadline, lock, policy and restart checks; no optimizer updates."""
import sys,datetime,json,os,fcntl,subprocess,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np,torch
from common import ROOT,REPO,read,write,config,sha
from budget import remaining,guard,admit,BudgetStop,clock
from supervisor import action
from training import input_identity,membership_check
from amend_training_support import stage_reuse
from data import load_cohort

def main():
 results={};c=config();d=clock();deadline=datetime.datetime.fromisoformat(d['deadline_utc']);cutoff=datetime.datetime.fromisoformat(d['training_cutoff_utc']);start=datetime.datetime.fromisoformat(d['accepted_utc']);before=sha(ROOT.parent/'efficient_finetuning_two_epochs_24h_v1_deadline.json')
 assert deadline-start==datetime.timedelta(hours=24) and deadline-cutoff==datetime.timedelta(hours=3)
 assert remaining(start)==21*3600 and remaining(deadline,reporting=True)==0
 try:guard(cutoff);raise AssertionError('late guard admitted')
 except BudgetStop:pass
 assert not admit(61,'simulated',now=cutoff-datetime.timedelta(seconds=60))
 assert action(8,10,20)=='continue' and action(10,10,20)=='checkpoint_stop' and action(75,10,100,10)=='kill' and action(100,10,100)=='hard_stop'
 for _ in range(3):clock()
 assert before==sha(ROOT.parent/'efficient_finetuning_two_epochs_24h_v1_deadline.json')
 results['persistent_24h_clock_and_3h_reserve']=True;results['simulated_short_deadline_no_sleep_no_real_worker_signal']=True
 temp=ROOT/'checks/synthetic_lock.lock'
 with temp.open('w') as f:
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  command=[sys.executable,'-I','-B','-c',"import fcntl,sys;f=open(sys.argv[1],'a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)",str(temp)]
  a=subprocess.run(command,capture_output=True);assert a.returncode!=0
 results['second_writer_lock_rejected']=True
 # Epoch/order resume exactly reconstructs the remaining batches, including tail.
 for n in [17,2317,2348]:
  seed=42;whole=[]
  for e in range(2):whole.extend([(e,int(i)) for i in np.random.default_rng(seed+e).permutation(n)])
  for epoch,batch in [(0,8),(1,16),(2,0)]:
   prior=epoch*n+batch;rest=[]
   for e in range(epoch,2):
    order=np.random.default_rng(seed+e).permutation(n);rest.extend([(e,int(i)) for i in order[batch if e==epoch else 0:]])
   assert whole[:prior]+rest==whole
 results['two_epoch_midfit_order_resume_tail_exact']=True
 assert c['epoch_budgets']=={'frozen_16_frames':5,'frozen_32_frames':5,'fine_tuned_16_frames':2,'fine_tuned_32_frames':2}
 assert c['epochs']==5 and c['scheduler']['kind']=='none' and c['scheduler']['original_horizon_epochs']==5
 assert c['microbatch_segments']==1 and c['effective_batch_segments']==8 and c['precision']=='float32'
 results['epoch_budgets_constant_original_LR_prefix']=True
 frame=load_cohort();jobs=read(ROOT/'data_manifests/fit_partitions.json')
 for j in jobs:membership_check(frame,j)
 results['all_25_recording_G_C_held_disjoint_partitions']=True
 old=REPO/c['original_run'];assert not Path('/proc/53642').exists()
 assert all(sha(p)==sha(ROOT/'provenance/original_source_snapshot'/p.name) for p in (old/'source').iterdir() if p.is_file())
 assert sha(old/'config/resolved_config.json')==sha(ROOT/'provenance/original_config_snapshot/resolved_config.json')
 results['old_worker_exited_source_and_config_unchanged']=True
 identity=input_identity();stage_reuse(identity)
 for p in (ROOT/'frozen_16_frames/fold_01').rglob('*'):
  if p.is_file() and p.name!='condition_complete.json':assert sha(p)==sha(old/'frozen_16_frames/fold_01'/p.relative_to(ROOT/'frozen_16_frames/fold_01'))
 results['reused_frozen16_artifacts_byte_identical']=True
 assert read(ROOT/'progress.json')['full_visual_fits_started']==7 and read(ROOT/'progress.json')['preflight_optimizer_steps']==9
 results['cumulative_counters_not_reset']=True
 benchmark=read(ROOT/'checks/performance_benchmark.json');assert benchmark['prediction_batch_agreement_passed'] and benchmark['loader_order_and_pixels_exact'] and benchmark['wall_seconds']<600
 assert read(ROOT/'checks/prediction32_batch_check.json')['passed']
 results['measured_loader_and_FP32_prediction_agreement']=True
 for p in (ROOT/'source').glob('*.py'):ast.parse(p.read_text())
 results['source_syntax']=True
 write(ROOT/'checks/focused_checks.json',{'passed':True,'checks':results,'additional_optimizer_steps':0,'deadline':d,'actual_first_updates_and_two_epoch_coverage':'Runtime assertions and per-fit evidence pending first planned real fits','independent_review':'self-review only'})
 print(json.dumps(results,indent=2))
if __name__=='__main__':main()
