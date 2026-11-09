"""Study-local state and admission; no service, scheduler or training."""
from pathlib import Path
import datetime as dt
import hashlib,json,os,shutil,subprocess,time
STUDY=Path(__file__).resolve().parents[1]
REPO=STUDY.parents[1]
RUN=STUDY/'results/run_01'
_STORAGE_SCAN_AT=0.
_STORAGE_USED=0

def read(p):return json.loads(Path(p).read_text())
def config():return read(STUDY/'config.json')
def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def elapsed():return (dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(config()['started_utc'])).total_seconds()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(2**20),b''):h.update(block)
    return h.hexdigest()
def signature(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def local(p):
    p=Path(p)
    if not p.resolve().is_relative_to(STUDY.resolve()):raise ValueError('WRITE_OUTSIDE_STUDY')
    p.parent.mkdir(parents=True,exist_ok=True);return p

def write(p,x):
    p=local(p);tmp=local(p.with_name(p.name+'.writing'))
    with tmp.open('w') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def write_text(p,x):
    p=local(p);tmp=local(p.with_name(p.name+'.writing'));tmp.write_text(x);os.replace(tmp,p)
def csv(p,x):
    p=local(p);tmp=local(p.with_name(p.name+'.writing'));x.to_csv(tmp,index=False,float_format='%.17g');os.replace(tmp,p)
def event(status,**fields):
    p=RUN/'progress.json';d=read(p) if p.exists() else {'failures':{},'completed_jobs':[]}
    d.update(status=status,updated_utc=utc(),elapsed_seconds=elapsed(),**fields);write(p,d)
    with local(RUN/'logs/events.jsonl').open('a') as f:f.write(json.dumps({'utc':utc(),'status':status,**fields})+'\n')
    print(status,json.dumps(fields)[:400],flush=True)
def budget(extra=0,scientific=True):
    global _STORAGE_SCAN_AT,_STORAGE_USED
    c=config();now=time.monotonic()
    if now-_STORAGE_SCAN_AT>=30 or not scientific:
        _STORAGE_USED=sum(p.stat().st_size for p in STUDY.rglob('*') if p.is_file() and not p.is_symlink());_STORAGE_SCAN_AT=now
    used=_STORAGE_USED;free=shutil.disk_usage(STUDY).free
    rss={l.split(':')[0]:int(l.split()[1])*1024 for l in Path('/proc/self/status').read_text().splitlines() if l.startswith(('VmRSS:','VmHWM:'))}
    if used+extra+(128*2**20 if scientific else 0)>c['storage_cap_bytes'] or free-extra<c['minimum_free_bytes']:raise RuntimeError('STORAGE_LIMIT')
    if rss.get('VmRSS',0)>c['host_memory_ceiling_bytes']:raise RuntimeError('HOST_MEMORY_LIMIT')
    if scientific and elapsed()>c['wall_seconds']-c['report_reserve_seconds']:raise RuntimeError('DEADLINE_REPORT_RESERVE')
    return {'study_bytes':used,'free_bytes':free,'elapsed_seconds':elapsed(),'storage_scan_policy':'at most30s old with128MiB safety margin; exact during reporting; disk free/RSS/deadline checked each call',**rss}
def command(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=30);return {'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
def code_identity():return {str(p.relative_to(STUDY)):sha(p) for p in [*sorted((STUDY/'code').glob('*.py')),STUDY/'run_experiment.py']}
def readiness():
    path=RUN/'checks/readiness.json'
    if path.exists():
        old=read(path)
        age=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(old['checked_utc'])).total_seconds()
        if age<60:return old
    c=config();terminal={'COMPLETE','PARTIAL','BLOCKED','WAITING_FOR_GPU','WAITING_FOR_INPUT_MANIFEST'}
    states={};active=[]
    for name,key in [('visual','visual_run'),('encoder','encoder_run')]:
        p=REPO/c[key]/'progress.json';states[name]=read(p) if p.exists() else {'status':'MISSING'}
        if states[name].get('status') not in terminal:active.append(name+':'+str(states[name].get('status')))
    processes=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        try:
            if (p/'comm').read_text().strip() not in ('python','python3','python3.12','bash'):continue
            args=(p/'cmdline').read_bytes()
            if ((b'visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames' in args and (b'run_study.py' in args or b'study.sh' in args)) or
                (b'rt_detr_encoder_comparison/run_experiment.py' in args and (b'run\0' in args or b'resume\0' in args))):
                processes.append({'pid':int(p.name),'identity':'upstream scientific worker'})
        except (FileNotFoundError,PermissionError,ProcessLookupError):pass
    gpu=command(['nvidia-smi','--query-gpu=index,uuid,name,memory.used','--format=csv,noheader,nounits'])
    apps=command(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'])
    occupied=[s for s in apps['stdout'].splitlines() if c['gpu_uuid'] in s and f', {os.getpid()},' not in s]
    d={'checked_utc':utc(),'terminal_inputs':not active and not processes,'gpu_available':gpu['returncode']==apps['returncode']==0 and c['gpu_uuid'] in gpu['stdout'] and not occupied and not processes,
       'upstream_states':{k:{x:v.get(x) for x in ['status','full_visual_fits_completed','completed_paired_folds','background_worker','queued']} for k,v in states.items()},
       'nonterminal':active,'priority_processes':processes,'gpu':gpu,'applications':apps}
    write(path,d);return d
