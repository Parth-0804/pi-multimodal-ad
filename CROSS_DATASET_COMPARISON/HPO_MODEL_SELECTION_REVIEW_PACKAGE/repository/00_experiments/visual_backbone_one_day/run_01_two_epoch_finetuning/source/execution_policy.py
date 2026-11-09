"""Explicit execution-only policy overlay; numerical checkpoint code stays fixed.

The user removed the24h limit after the checkpoint was created. Preserve the
historical clock/config/source hashes needed to validate that checkpoint, and
record the effective policy separately. No optimizer/model/data function is
replaced. The standard CLI installs this overlay before importing its worker.
"""
import math
from common import ROOT,config,read,write,sha

def install():
 path=ROOT/'execution_policy.json'
 if not path.exists():return False
 import budget
 expected=sha(path)
 if hasattr(budget,'effective_execution_policy_sha256'):
  assert budget.effective_execution_policy_sha256==expected,'EXECUTION_POLICY_DRIFT'
  return True
 policy=read(path)
 assert policy['policy_id']=='two_epoch_finetuning_unlimited_wall_time_user_amendment_v2'
 assert policy['wall_time_limit_seconds'] is None
 assert policy['no_counter_reset'] and policy['no_scientific_parameter_change']
 assert policy['epoch_budgets']==config()['epoch_budgets']
 historical_clock=budget.clock()
 def check():
  assert sha(path)==expected,'EXECUTION_POLICY_DRIFT'
 def effective_clock():
  check()
  return {**historical_clock,'deadline_utc':None,'training_cutoff_utc':None,
   'deadline_Europe_Berlin':None,'report_reserve_seconds':None,
   'wall_time_limit_seconds':None,'historical_clock':historical_clock,
   'effective_policy_id':policy['policy_id'],'effective_policy_sha256':expected,
   'effective_policy_authorized_utc':policy['authorized_utc']}
 def remaining(now=None,reporting=False):
  check();return None
 def guard(now=None):check()
 def admit(seconds,scope,now=None):
  check();assert math.isfinite(seconds) and seconds>=0
  if now is None:
   write(ROOT/'checks/latest_admission.json',{'scope':scope,
    'conservative_end_to_end_seconds':seconds,'remaining_before_reporting_seconds':None,
    'admitted':True,'basis':'User explicitly removed wall-time limit; fixed epochs and cumulative resource caps remain',
    'execution_policy_sha256':expected})
  return True
 budget.clock=effective_clock;budget.remaining=remaining
 budget.guard=guard;budget.admit=admit
 budget.effective_execution_policy_sha256=expected
 return True
