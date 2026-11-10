"""Study-local identities, resources and atomic state. Never writes old paths."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
CONDITIONS=('frozen_16_frames','fine_tuned_16_frames','frozen_32_frames','fine_tuned_32_frames')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def signature(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
 p=Path(p);assert p.resolve().is_relative_to(ROOT.resolve())
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.writing')
 with tmp.open('w') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def config():return read(ROOT/'config/resolved_config.json')
def code_id():return {p.name:sha(p) for p in sorted((ROOT/'source').glob('*.py'))}
def resources(extra=0):
 c=config();free=shutil.disk_usage(ROOT).free
 if free-extra<c['minimum_free_bytes']:raise RuntimeError('DISK_FREE_RESERVE_BLOCKER')
 roots=[ROOT,REPO/c['original_run']]
 used=sum(p.stat().st_size for root in roots for p in root.rglob('*') if p.is_file() and not p.is_symlink())
 if used+extra>c['new_storage_cap_bytes']:raise RuntimeError('STUDY_STORAGE_CAP_BLOCKER')
 rss=0
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith('VmRSS:'):rss=int(line.split()[1])*1024
 if rss>c['host_memory_ceiling_bytes']:raise RuntimeError('HOST_RSS_CEILING_BLOCKER')
 return {'new_bytes':used,'free_bytes':free,'host_RSS_bytes':rss,'host_memory_policy':'Monitored process RSS; not claimed OS hard limit'}
def event(stage,**fields):
 p=ROOT/'progress.json';d=read(p);d.update(status=stage,updated_utc=utc(),**fields)
 d['total_elapsed_seconds']=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(d['started_utc'])).total_seconds()
 d['remaining_full_visual_fit_starts']=d['full_visual_fit_cap']-d['full_visual_fits_started'];d['remaining_disposable_optimizer_steps']=d['preflight_optimizer_step_cap']-d['preflight_optimizer_steps']
 d['elapsed_seconds_scope']='elapsed_seconds describes an individual stage invocation when supplied; total_elapsed_seconds includes the full task from its approximate recorded start';write(p,d)
 with (ROOT/'provenance/events.jsonl').open('a') as f:f.write(json.dumps({'utc':utc(),'stage':stage,**fields})+'\n');f.flush()
 print(utc(),stage,json.dumps(fields,default=str)[:500],flush=True)
def check_originals():
 d=read(ROOT/'provenance/initial_state.json')
 for p,h in d['hashes'].items():
  if sha(REPO/p)!=h:raise RuntimeError('ORIGINAL_INPUT_DRIFT '+p)
def save_csv(path,frame):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.writing');frame.to_csv(tmp,index=False);os.replace(tmp,path)
