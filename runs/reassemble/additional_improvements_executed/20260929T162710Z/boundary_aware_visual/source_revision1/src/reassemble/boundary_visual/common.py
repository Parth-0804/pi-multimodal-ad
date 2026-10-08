import json,os,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone

def read(p):return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def identity(p):return {'path':str(p),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def write(p,value,mutable=False):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and not mutable:
  if read(p)!=value:raise ValueError('Immutable output differs: '+str(p))
  return
 tmp=p.with_name(p.name+f'.pending.{os.getpid()}');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');os.replace(tmp,p)
def status(run,state,stage):
 data={'UTC':datetime.now(timezone.utc).isoformat(),'state':state,'stage':stage,'pid':os.getpid()};write(run/'status.json',data,True)
 (run/'CONTINUATION.md').write_text('# Boundary-aware visual experiment\n\n'+state+': '+stage+'\n\nRun: `'+str(run)+'`. Resume with `PYTHONPATH=src OPENBLAS_NUM_THREADS=16 OMP_NUM_THREADS=4 MKL_NUM_THREADS=16 ma_thesis_env/bin/python -B -m reassemble.boundary_visual.runner --run '+str(run)+'`. Check processes first. Task 4 must finish successfully before training. Task 1 stays paused. No automatic boot startup is configured. Fixed configuration, source signatures and completed fits must match; stop on mismatch. Read protocol.md, validation and logs; never relax parity tolerances to proceed. Human-review identities, ratings and flags are not model inputs.\n')
 print(data['UTC'],state,stage,flush=True)
def storage(run):
 free=shutil.disk_usage(run).free/2**30
 if free<20:raise RuntimeError('Storage below 20 GiB; no cleanup authorized')
 return free
def atomic_npz(path,**arrays):
 import numpy as np
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():
  with np.load(p,allow_pickle=False) as old:
   assert set(old.files)==set(arrays),'Existing array keys differ'
   for key,value in arrays.items():
    value=np.asarray(value);assert old[key].dtype==value.dtype and np.array_equal(old[key],value,equal_nan=value.dtype.kind in 'fc'),'Existing array values differ: '+key
  return
 tmp=p.with_name(p.name+f'.pending.{os.getpid()}')
 with tmp.open('xb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def snapshot(roots):
 entries=[]
 for root in roots:
  for p in sorted(Path(root).rglob('*')):
   if p.is_symlink():entries.append({'path':str(p),'link':os.readlink(p)});continue
   if not p.is_file():continue
   st=p.stat();entry={'path':str(p),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns}
   # Large checkpoint/cache/HDF5 payloads use immutable metadata + audited hashes
   # where referenced by the cache preflight; avoid re-reading tens of GiB.
   if st.st_size<4*1024**2:entry['sha256']=sha(p)
   entries.append(entry)
 return entries

def verify_snapshot(entries):
 for entry in entries:
  p=Path(entry['path'])
  if 'link' in entry:assert p.is_symlink() and os.readlink(p)==entry['link'],str(p)
  else:
   st=p.stat();assert st.st_size==entry['bytes'] and st.st_mtime_ns==entry['mtime_ns'],str(p)
   if 'sha256' in entry:assert sha(p)==entry['sha256'],str(p)
 return {'verified_entries':len(entries),'small_files_hashed':sum('sha256' in e for e in entries),'large_files':'size/mtime preservation; not a fresh full-content rehash','passed':True}
