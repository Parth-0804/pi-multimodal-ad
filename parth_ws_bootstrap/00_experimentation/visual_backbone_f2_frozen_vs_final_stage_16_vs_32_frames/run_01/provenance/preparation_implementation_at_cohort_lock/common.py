"""Study-local identities, resources and atomic state. Never writes old paths."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
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
 used=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink())
 if used+extra>c['new_storage_cap_bytes']:raise RuntimeError('STUDY_STORAGE_CAP_BLOCKER')
 return {'new_bytes':used,'free_bytes':free}
def event(stage,**fields):
 p=ROOT/'progress.json';d=read(p);d.update(status=stage,updated_utc=utc(),**fields);write(p,d)
 with (ROOT/'provenance/events.jsonl').open('a') as f:f.write(json.dumps({'utc':utc(),'stage':stage,**fields})+'\n');f.flush()
 print(utc(),stage,json.dumps(fields,default=str)[:500],flush=True)
def check_originals():
 d=read(ROOT/'provenance/initial_state.json')
 for p,h in d['hashes'].items():
  if sha(REPO/p)!=h:raise RuntimeError('ORIGINAL_INPUT_DRIFT '+p)
def save_csv(path,frame):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.writing');frame.to_csv(tmp,index=False);os.replace(tmp,path)
