"""Study-owned I/O and compatibility interface for unchanged scientific primitives."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import shutil
import time

STUDY=Path(__file__).resolve().parents[1]
REPO=STUDY.parents[1]
# Unchanged model/pixel primitives expect ROOT/provenance and own cache paths.
ROOT=STUDY/'results'
PRIOR=REPO/'00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning'
CONDITIONS=('frozen32_two_epochs','finetuned32_two_epochs')
LAST_STORAGE_SCAN=0.

def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()
def signature(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,obj):
    path=Path(path);assert path.resolve().is_relative_to(STUDY.resolve())
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.writing')
    with tmp.open('w') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
def config():return read(STUDY/'resolved_config.json')
def save_csv(path,frame):
    path=Path(path);assert path.resolve().is_relative_to(STUDY.resolve());path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.writing');frame.to_csv(temp,index=False,float_format='%.17g');os.replace(temp,path)
def csv(path):
    import pandas as pd
    return pd.read_csv(path,dtype={'sample_id':str,'recording_id':str,'segment_id':str},float_precision='round_trip')
def clock():return read(ROOT/'provenance/task_clock.json')
class StopStudy(RuntimeError):pass
def guard(training=True):
    now=dt.datetime.now(dt.timezone.utc);key='training_cutoff_utc' if training else 'deadline_utc'
    if now>=dt.datetime.fromisoformat(clock()[key]):raise StopStudy('TRAINING_CUTOFF' if training else 'FINAL_DEADLINE')
    if (STUDY/'STOP.json').exists():raise StopStudy('USER_STOP_REQUESTED')
def resources(extra=0):
    global LAST_STORAGE_SCAN
    c=config();free=shutil.disk_usage(STUDY).free
    if free-extra<c['minimum_free_bytes']:raise StopStudy('DISK_FREE_RESERVE')
    rss=0
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith('VmRSS:'):rss=int(line.split()[1])*1024
    if rss>c['host_memory_ceiling_bytes']:raise StopStudy('HOST_MEMORY_CEILING')
    if time.monotonic()-LAST_STORAGE_SCAN>=60:
        used=sum(p.stat().st_size for p in STUDY.rglob('*') if p.is_file() and not p.is_symlink())
        if used+extra>c['new_storage_cap_bytes']:raise StopStudy('NEW_STUDY_STORAGE_CAP')
        LAST_STORAGE_SCAN=time.monotonic()
    return {'free_bytes':free,'RSS_bytes':rss}
def event(stage,**fields):
    path=STUDY/'STATE.json';state=read(path) if path.exists() else {}
    state.update(status=stage,updated_utc=utc(),**fields);write(path,state)
    with (ROOT/'provenance/events.jsonl').open('a') as f:f.write(json.dumps({'utc':utc(),'stage':stage,**fields},default=str)+'\n');f.flush()
    print(utc(),stage,json.dumps(fields,default=str)[:750],flush=True)
def role_seed(family,job):return int(signature({'base':family,'outer':job['outer_fold_original'],'role':job['role']})[:8],16)%(2**31-1)
def install_prior_primitives():
    import sys
    # unittest discovery may prepend tests/. Keep the study's I/O adapters
    # ahead of historical modules in every entry mode, not just normal runs.
    own=str(STUDY/'code');path=str(PRIOR/'source')
    for value in [own,path]:
        while value in sys.path:sys.path.remove(value)
    sys.path.insert(0,own);sys.path.insert(1,path)
    expected=read(STUDY/'existing_evidence/scientific_fit_lock.json')['sources']
    for name in ['visual_model.py','fusion.py','pixel_access.py','fast_input.py']:
        assert sha(PRIOR/'source'/name)==expected[name],('PRIMITIVE_SOURCE_DRIFT',name)

