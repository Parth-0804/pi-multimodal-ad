"""Read-only GPU interlock: never borrow a gap between REASSEMBLE fits."""
import os
import subprocess
import time
import psutil
from .common import PROJECT,read,resolve,utc,write


def process_alive(receipt):
    """PID plus creation time avoids confusing a recycled unrelated process."""
    try:
        p=psutil.Process(receipt['pid'])
        return abs(p.create_time()-receipt['create_time'])<.01 and p.status()!=psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess,psutil.AccessDenied,KeyError):return False


def gpu_state(c):
    status_path=resolve(c['reassemble_status']);marker=status_path.with_name('PHASE1_C_ONLY_ALL_COMPLETE.json')
    state={'utc':utc(),'source_complete':False,'gpu_idle':False,'reason':'SOURCE_STUDY_NOT_COMPLETE'}
    if not marker.exists():return state
    terminal=read(marker)
    if terminal.get('status')!='COMPLETE' or terminal.get('C_fits')!=75 or terminal.get('epochs_each')!=20:return state
    # Verify the completion marker’s metric identity, rather than trusting its name.
    metrics=marker.with_name('PHASE1_C_ONLY_FINAL_METRICS.json')
    from .common import sha
    if not metrics.exists() or sha(metrics)!=terminal['metrics_sha256']:
        state['reason']='SOURCE_TERMINAL_IDENTITY_MISMATCH';return state
    state['source_complete']=True
    try:
        process=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
        other=[int(line.strip()) for line in process.stdout.splitlines() if line.strip().isdigit() and int(line.strip())!=os.getpid()]
        state.update(gpu_idle=not other,other_GPU_processes=other,reason='READY' if not other else 'OTHER_GPU_WORK_ACTIVE')
    except (OSError,subprocess.CalledProcessError):state['reason']='GPU_QUERY_FAILED'
    return state


def wait_for_gpu(c):
    last=None
    while True:
        state=gpu_state(c);write(PROJECT/'logs'/c['run_id']/'GPU_INTERLOCK.json',state)
        if state['source_complete'] and state['gpu_idle']:return state
        time.sleep(30)
