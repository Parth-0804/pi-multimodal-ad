"""One foreground run-scoped child; absolute soft/hard deadlines, no scheduler."""
import sys,os,time,signal,subprocess,fcntl,datetime,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,REPO,read,write,event,config
from budget import remaining,clock

def action(now,cutoff,deadline,stopped_at=None):
 if now>=deadline:return 'hard_stop'
 if now>=cutoff:return 'kill' if stopped_at is not None and now-stopped_at>=60 else 'checkpoint_stop'
 return 'continue'

def main():
 with (ROOT/'supervisor.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  # Hold legacy writer lock too: original run cannot restart concurrently.
  with (REPO/config()['original_run']/'study_writer.lock').open('a') as oldlock:
   fcntl.flock(oldlock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   if remaining()<=180:event('REPORTING_ONLY_DEADLINE_OR_RESERVE');finalize();return
   d=clock();cutoff=datetime.datetime.fromisoformat(d['training_cutoff_utc']).timestamp()-90;deadline=datetime.datetime.fromisoformat(d['deadline_utc']).timestamp();stopped=None
   log=(ROOT/'logs/amended_training.log').open('a',buffering=1)
   command=['bash',str(ROOT/'source/study.sh'),'resume'];worker=subprocess.Popen(command,cwd=REPO,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   write(ROOT/'worker_status.json',{'supervisor_pid':os.getpid(),'worker_pid':worker.pid,'command':command,'cwd':str(REPO),'clock':d,'status':'RUNNING','launched_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
   try:
    while worker.poll() is None:
     todo=action(time.time(),cutoff,deadline,stopped)
     if todo=='checkpoint_stop' and stopped is None:os.killpg(worker.pid,signal.SIGTERM);stopped=time.time()
     elif todo in ['kill','hard_stop']:os.killpg(worker.pid,signal.SIGKILL)
     time.sleep(min(5,max(.01,deadline-time.time())))
   finally:
    if worker.poll() is None:
     os.killpg(worker.pid,signal.SIGTERM)
     try:worker.wait(timeout=30)
     except subprocess.TimeoutExpired:os.killpg(worker.pid,signal.SIGKILL);worker.wait()
   write(ROOT/'worker_status.json',{'supervisor_pid':os.getpid(),'worker_pid':worker.pid,'status':'STOPPED','returncode':worker.returncode,'clock':d,'stopped_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
   finalize()

def finalize():
 # Always produce a usable partial report; no training is launched here.
 from amendment_report import finish
 finish()
if __name__=='__main__':main()
