"""Resume-safe bounded job queue; no outcome-dependent budgets or winner combination."""
from pathlib import Path
import os
import sys
import json
import time
import fcntl
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from .common import config,read,write,identity

MODULE='reassemble.additional_improvements.'
LOCK=threading.Lock()
CHILDREN={}
STOP=threading.Event()

def log(message):
    print(datetime.now(timezone.utc).isoformat(),message,flush=True)

def active_module(fragment):
    text=subprocess.check_output(['ps','-eo','args='],text=True)
    return any('ma_thesis_env/bin/python -B -m '+MODULE+fragment in line and not line.startswith('/bin/bash') for line in text.splitlines())

def wait_existing(root):
    for task,fragment in [(1,'unimodal --task 1'),(2,'unimodal --task 2')]:
        folder=root/('01_temporal_visual' if task==1 else '02_patchtst_training_budget')
        while active_module(fragment):time.sleep(10)
        assert (folder/'comparison/results.json').exists(),f'Existing primary task{task} did not complete; inspect its preserved execution log'

def run(name,module,args=(),optional_cache=False):
    c=config();root=Path(c['run_dir']);logs=root/'00_protocol_and_preservation/execution_logs';logs.mkdir(exist_ok=True)
    with LOCK:
        existing=sorted(logs.glob(name+'_attempt*.json'))
        if existing and read(existing[-1]).get('returncode')==0:
            log('REUSED completed '+name);return
        attempt=len(existing);out=logs/f'{name}_attempt{attempt}.log';meta=out.with_suffix('.json')
    command=[sys.executable,'-B','-m',MODULE+module,*args]
    record=dict(name=name,command=command,started_UTC=datetime.now(timezone.utc).isoformat(),source=identity(Path('src/reassemble/additional_improvements')/(module+'.py')),
                git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    write(meta,record);log('START '+name)
    with out.open('x') as stream:
        process=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':'src'})
        with LOCK:CHILDREN[name]=process
        while process.poll() is None:
            if STOP.wait(5):process.terminate();process.wait();raise RuntimeError('Stopped after another execution failure')
        with LOCK:CHILDREN.pop(name,None)
    record.update(returncode=process.returncode,finished_UTC=datetime.now(timezone.utc).isoformat());write(meta,record,replace=True)
    if process.returncode:
        content=out.read_text()
        if optional_cache and ('STORAGE BLOCKER' in content or 'Prefix cache storage estimate' in content or 'OutOfMemoryError' in content):
            write(root/'01_temporal_visual/prefix_cache_fallback.json',dict(reason='Approved optional cache could not satisfy resource policy; original pixel-based FT remains authorized',attempt=identity(meta),log=str(out)))
            log('CACHE FALLBACK: preserve partial cache; use live pixels');return
        STOP.set();raise RuntimeError(f'{name} failed; retained log {out}')
    log('COMPLETE '+name)

def wait_sensor_banks(root):
    folder=root/'04_corruption_training/sensor_bank'
    while len(list(folder.glob('*.npz')))<105 or len(list(folder.glob('*.json')))<105:
        logs=list((root/'04_corruption_training').glob('sensor_bank_shard*.log'))
        if any('Traceback (most recent call last)' in p.read_text() for p in logs):raise RuntimeError('Sensor corruption worker failed; inspect preserved shard logs')
        if not any(active_module('branch_banks sensor --shard '+str(i)) for i in range(4)):
            raise RuntimeError('Sensor banks incomplete and no workers active; resume missing bounded shards')
        if STOP.wait(10):raise RuntimeError('Stopped after another execution failure')

def main():
    c=config();root=Path(c['run_dir']);lock=(root/'supervisor.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    write(root/'supervisor_state.json',dict(pid=os.getpid(),state='waiting_for_primary_jobs',started_UTC=datetime.now(timezone.utc).isoformat()),replace=True)
    try:
        wait_existing(root)
        # Empirical profiles: PatchTST0.55GiB + arrays; frozen backbone2.3GiB;
        # FT2.72GiB. Two GPU processes reserve at least4GiB on16GiB T4.
        write(root/'00_protocol_and_preservation/parallel_resource_schedule.json',dict(maximum_real_GPU_jobs=2,profiles=['parallel_resource_audit.json','parallel_resource_audit_visual_heads.json','../01_temporal_visual/finetune_gradient_audit.json'],
              conservative_total_GPU_GiB=8,reserved_GPU_GiB_at_least=4,total_GPU_GiB=16,CPU='two GPU jobs4threads each, four sensor workers one BLAS thread each; cached FT adds two I/O threads; at most14/16 nominal CPUthreads',
              rationale='Measured independent model memory fits with ample reserve; all numerical seeds and budgets unchanged. No third real GPU job.'))
        def fusion_chain():
            run('recover_original_branches','branch_banks',['recover'])
            if not (root/'01_temporal_visual/prefix_cache_fallback.json').exists():
                run('frozen_prefix_cache','prefix_cache',['extract'],optional_cache=True)
            run('visual_corruption_bank','corruptions',['visual'])
            run('score_visual_corruptions','branch_banks',['visual'])
            wait_sensor_banks(root)
            run('matched_robust_fusion','robust_fusion')
            run('historical_robustness_references','historical_robustness')
            run('robust_report','robust_report')
        def representation_chain():
            run('strict_sensor_hybrid','hybrid')
            run('sensor_report','unimodal_report',['--task','2'])
            # Prefix extraction belongs to the other queue; never silently use a
            # partial cache while an authorized complete one is still being built.
            while not (root/'01_temporal_visual/frozen_prefix/complete.json').exists() and not (root/'01_temporal_visual/prefix_cache_fallback.json').exists():
                if STOP.wait(10):raise RuntimeError('Prefix preparation did not complete')
            run('bounded_visual_finetuning','finetune')
            run('visual_report','unimodal_report',['--task','1'])
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(fusion_chain),pool.submit(representation_chain)]
            for future in futures:future.result()
        run('final_consolidation','finalize')
        write(root/'supervisor_state.json',dict(pid=os.getpid(),state='complete',finished_UTC=datetime.now(timezone.utc).isoformat()),replace=True);log('ALL BOUNDED TASKS COMPLETE — STOP')
    except BaseException as exc:
        STOP.set()
        with LOCK:
            for process in CHILDREN.values():
                if process.poll() is None:process.terminate()
        write(root/'supervisor_state.json',dict(pid=os.getpid(),state='failed_requires_review',error=repr(exc),UTC=datetime.now(timezone.utc).isoformat()),replace=True)
        log('STOP: '+repr(exc));raise

if __name__=='__main__':main()
