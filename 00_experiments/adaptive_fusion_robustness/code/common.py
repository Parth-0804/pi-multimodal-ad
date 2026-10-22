"""Study-local paths, atomic evidence, and immutable clock accounting."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, time
STUDY=Path(__file__).resolve().parents[1]
REPO=STUDY.parents[1]
RUN=STUDY/'results/run_01'
ENC=REPO/'00_experiments/rt_detr_encoder_comparison/results/run_01'
NOISE=REPO/'00_experiments/fusion_noise_test/results/run_02'
def read(p): return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def signature(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def write(p,x):
 p=Path(p);assert p.resolve().is_relative_to(STUDY.resolve());p.parent.mkdir(parents=True,exist_ok=True)
 q=p.with_name(p.name+'.writing');q.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n');os.replace(q,p)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def remaining(scientific=True):
 c=read(RUN/'config/clock.json');key='scientific_cutoff_utc' if scientific else 'deadline_utc'
 return (datetime.datetime.fromisoformat(c[key])-datetime.datetime.now(datetime.timezone.utc)).total_seconds()-c['initial_audit_before_persist_seconds_allowance']
_last_storage_check=0.
def guard(extra=0,scientific=True):
 global _last_storage_check
 assert remaining(scientific)>0,'STUDY_DEADLINE_REACHED'
 assert shutil.disk_usage(STUDY).free-extra>=10*2**30,'FILESYSTEM_RESERVE'
 if time.monotonic()-_last_storage_check>60:
  used=sum(p.stat().st_size for p in STUDY.rglob('*') if p.is_file() and not p.is_symlink());assert used+extra<=30*2**30,'STUDY_STORAGE_CAP';_last_storage_check=time.monotonic()
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith('VmRSS:'):assert int(line.split()[1])*1024<=16*2**30,'MONITORED_RSS_LIMIT'
def folder(condition,job):return ENC/condition/job['fold_name']/('outer_assessment' if job['role']=='outer_assessment' else 'fusion_training/'+job['role'])
def state(status,**kw):
 d=read(RUN/'progress.json');observed={}
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith(('VmRSS:','VmHWM:')):observed[line.split(':')[0]]=int(line.split()[1])*1024
 observed['CPU_ids']=sorted(os.sched_getaffinity(0));observed['GPU_used']=False
 d.update(status=status,updated_utc=utc(),remaining_scientific_seconds=remaining(),remaining_total_seconds=remaining(False),resource_observation=observed,**kw);write(RUN/'progress.json',d)

def config():return read(RUN/'config/resolved_config.json')
