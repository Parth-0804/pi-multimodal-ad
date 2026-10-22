"""Study-specific foreground commands. Status never initializes training."""
import argparse,fcntl,json,os,sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,config,read,write,event,resources,check_originals

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','preflight','train','resume','evaluate','package','status','stop','benchmark','focused_checks','benchmark32','supervise']);a=p.parse_args()
 if a.command=='supervise':
  from supervisor import main as supervisor_main
  supervisor_main();return
 if a.command=='status':print(json.dumps(read(ROOT/'progress.json'),indent=2));return
 if a.command=='stop':write(ROOT/'STOP.json',{'requested':'stop at next safe checkpoint'});return
 with (ROOT/'study_writer.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  check_originals();resources()
  try:
   if a.command=='benchmark32':
    from benchmark32 import main as benchmark32_main
    benchmark32_main()
   elif a.command=='focused_checks':
    from focused_checks import main as checks_main
    checks_main()
   elif a.command=='benchmark':
    from benchmark import main as benchmark_main
    benchmark_main()
   elif a.command=='prepare':
    from data import prepare
    prepare()
   elif a.command=='preflight':
    from visual_model import preflight,extract_features
    preflight();extract_features()
   elif a.command in ['train','resume']:
    from training import run
    run(resume=a.command=='resume')
   elif a.command=='evaluate':
    from evaluation import evaluate
    evaluate()
   elif a.command=='package':
    from amendment_report import finish
    finish()
  except __import__('budget').BudgetStop as exc:
   event('PARTIAL_BUDGET_STOP',active_job=None,stop_reason=str(exc));print(str(exc),flush=True);raise SystemExit(75)
  except BaseException as exc:
   if not isinstance(exc,KeyboardInterrupt):
    d=read(ROOT/'progress.json');failures=d.get('failures',[]);failures.append({'command':a.command,'error':repr(exc)});event('BLOCKED',failures=failures,blocker=repr(exc))
   traceback.print_exc();raise
if __name__=='__main__':main()
