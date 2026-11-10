"""Persistent amendment clock, conservative admission and run-only deadlines."""
import datetime,json,os,signal,time
from pathlib import Path
from common import ROOT,read,write,event
ID='efficient_finetuning_two_epochs_24h_v1'
CLOCK=ROOT.parent/(ID+'_deadline.json')
class BudgetStop(InterruptedError):pass

def clock():
 d=read(CLOCK);assert d['amendment_id']==ID
 start=datetime.datetime.fromisoformat(d['accepted_utc']);end=datetime.datetime.fromisoformat(d['deadline_utc'])
 assert (end-start).total_seconds()==86400
 return d

def remaining(now=None,reporting=False):
 d=clock();now=now or datetime.datetime.now(datetime.timezone.utc)
 end=datetime.datetime.fromisoformat(d['deadline_utc' if reporting else 'training_cutoff_utc'])
 return (end-now).total_seconds()

def guard(now=None):
 if remaining(now)<=90:raise BudgetStop('AMENDMENT_TRAINING_CUTOFF_CHECKPOINT_AND_REPORT')

def admit(seconds,scope,now=None):
 left=remaining(now);ok=seconds+180<left
 if now is None:write(ROOT/'checks/latest_admission.json',{'scope':scope,'conservative_end_to_end_seconds':seconds,'remaining_before_reporting_seconds':left,'admitted':ok,'includes':'startup, training, prediction, calibration, replay, checkpoint and fusion; reporting reserved separately'})
 return ok

def cost_estimate(job,frames):
 # Fit-specific costs updated from full end-to-end completed amendment fits.
 # Unobserved32 remains explicitly conservative, not a measured extrapolation.
 observed=[]
 for p in (ROOT/f'fine_tuned_{frames}_frames').glob('fold_*/**/visual_fit/complete.json'):
  d=read(p)
  if d.get('epochs_complete')!=2:continue
  n=len(d['job']['G']);pred=len(d['job']['C'])+len(d['job']['predict'])
  observed.append((d['training_wall_seconds']/(2*n), (d['raw_prediction_cost_C']['seconds']+d['raw_prediction_cost_V']['seconds'])/max(1,pred)))
 if observed:
  train=max(x[0] for x in observed)*1.35;predict=max(x[1] for x in observed)*1.35;basis='measured same-frame amended complete fits, 35% margin'
 else:
  train,predict=(.7,1.25) if frames==16 else (1.15,1.65);basis='unobserved conservative provisional estimate;32 not yet measured'
 return {'seconds':2*len(job['G'])*train+(len(job['C'])+len(job['predict']))*predict+180,'basis':basis,'frames':frames}
