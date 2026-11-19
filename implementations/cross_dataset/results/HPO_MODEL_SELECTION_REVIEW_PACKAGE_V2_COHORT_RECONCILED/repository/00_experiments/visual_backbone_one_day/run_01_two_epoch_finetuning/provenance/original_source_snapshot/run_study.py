"""Study-specific foreground commands. Status never initializes training."""
import argparse,fcntl,json,os,sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,config,read,write,event,resources,check_originals

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','preflight','train','resume','evaluate','package','status','stop']);a=p.parse_args()
 if a.command=='status':print(json.dumps(read(ROOT/'progress.json'),indent=2));return
 if a.command=='stop':write(ROOT/'STOP.json',{'requested':'stop at next safe checkpoint'});return
 with (ROOT/'study_writer.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  check_originals();resources()
  try:
   if a.command=='prepare':
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
    from reporting import package
    package()
  except BaseException as exc:
   if not isinstance(exc,KeyboardInterrupt):
    d=read(ROOT/'progress.json');failures=d.get('failures',[]);failures.append({'command':a.command,'error':repr(exc)});event('BLOCKED',failures=failures,blocker=repr(exc))
   traceback.print_exc();raise
if __name__=='__main__':main()
