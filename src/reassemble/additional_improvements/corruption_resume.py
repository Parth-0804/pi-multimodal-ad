"""Task-4-only continuation, with preserved outputs and safe unit boundaries."""
import argparse
from contextlib import contextmanager
from datetime import datetime,timedelta,timezone
import fcntl
import importlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time
from zoneinfo import ZoneInfo
import numpy as np
from .common import config,identity,progress,read,storage,write

STOP=False
PAUSED=75
STAGES={'visual':('corruptions',['visual']),'score':('branch_banks',['visual']),
        'fusion':('robust_fusion',[]),'references':('historical_robustness',[]),'report':('robust_report',[])}


def stop_requested(*unused):
    global STOP
    STOP=True


def deadline():
    now=datetime.now(ZoneInfo('Europe/Berlin'))
    cutoff=now.replace(hour=5,minute=30,second=0,microsecond=0)
    if cutoff<=now<now.replace(hour=6,minute=10,second=0,microsecond=0):raise RuntimeError('Inside daily reset pause window')
    if cutoff<=now:cutoff+=timedelta(days=1)
    return cutoff.astimezone(timezone.utc)


@contextmanager
def atomic_npz_outputs():
    """Preserve equal completed arrays; publish new outputs with an atomic rename."""
    original=np.savez_compressed
    def save(file,*args,**values):
        if hasattr(file,'write'):return original(file,*args,**values)
        path=Path(file)
        if path.suffix!='.npz':path=Path(str(path)+'.npz')
        arrays={f'arr_{i}':v for i,v in enumerate(args)};arrays.update(values)
        if path.exists():
            with np.load(path,allow_pickle=False) as old:
                if set(old.files)!=set(arrays):raise ValueError('Existing output keys differ: '+str(path))
                for key,value in arrays.items():
                    arr=np.asarray(value);nan=arr.dtype.kind in 'fc'
                    if not np.array_equal(old[key],arr,equal_nan=nan):raise ValueError('Existing output values differ: '+str(path))
            return
        pending=path.with_name(path.name+f'.pending.{os.getpid()}.{time.time_ns()}')
        with pending.open('xb') as handle:
            original(handle,**arrays);handle.flush();os.fsync(handle.fileno())
        os.replace(pending,path)
    np.savez_compressed=save
    try:yield
    finally:np.savez_compressed=original


def canonical_write(path,value,replace=False):
    # JSON stores tuples as arrays; compare persisted values using that same form.
    # Unequal values still fail common.write's immutable-output assertion.
    return write(path,json.loads(json.dumps(value,allow_nan=False)),replace=replace)


def worker(args):
    signal.signal(signal.SIGTERM,stop_requested);signal.signal(signal.SIGINT,stop_requested)
    limit=datetime.fromisoformat(args.deadline)
    if datetime.now(timezone.utc)>=limit:return PAUSED
    if args.stage.startswith('sensor'):
        name='branch_banks';argv=['sensor','--shard',args.stage[-1],'--shards','4']
    else:name,argv=STAGES[args.stage]
    module=importlib.import_module('reassemble.additional_improvements.'+name)
    previous=module.progress
    module.write=canonical_write
    def after_unit(*a,**kw):
        previous(*a,**kw)
        if STOP or datetime.now(timezone.utc)>=limit:raise SystemExit(PAUSED)
    module.progress=after_unit;sys.argv=[name,*argv]
    with atomic_npz_outputs():module.main()
    return 0


def main(args):
    c=config();root=Path(c['run_dir']);task=root/'04_corruption_training';attempt=args.attempt_dir
    attempt.mkdir(parents=True,exist_ok=True)
    if (attempt/'preflight.json').exists():raise FileExistsError('Use a fresh attempt directory')
    lock=(root/'supervisor.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    # Holding this lock proves the Task 1 worker has exited, without altering its state.
    visual_lock=(root/'01_temporal_visual/visual_worker.lock').open('a');fcntl.flock(visual_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    limit=deadline();storage(large=True)
    signal.signal(signal.SIGTERM,stop_requested);signal.signal(signal.SIGINT,stop_requested)
    preserved=[identity(p) for p in task.rglob('*') if p.is_file() and p.name!='status.json']
    preserved += [identity(root/'02_patchtst_training_budget/status.json'),identity(root/'03_static_anchored_adaptation/status.json')]
    checks=0
    for folder in ['visual_bank','sensor_bank','visual_probabilities']:
        for p in (task/folder).glob('*.npz'):
            meta=p.with_suffix('.json')
            if not meta.exists() or read(meta)['output']!=identity(p):raise ValueError('Incomplete/changed bank: '+str(p))
            checks+=1
    branches=[p for p in (task/'branches').glob('*.json') if not p.stem.endswith('_sensor')]
    if len(branches)!=105:raise ValueError('Original branch recovery is incomplete; inspect before resuming')
    for p in branches:
        info=read(p)
        for field in ['visual_checkpoint','sensor_checkpoint']:
            if identity(info[field]['path'])!=info[field]:raise ValueError('Changed recovered branch: '+str(p))
    snapshot=attempt/'source';snapshot.mkdir()
    for p in Path('src/reassemble/additional_improvements').glob('*.py'):shutil.copyfile(p,snapshot/p.name)
    write(attempt/'preflight.json',dict(UTC=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),git_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),config=identity('configs/reassemble/additional_improvements/execution.json'),source=[identity(p) for p in snapshot.iterdir()],preserved=preserved,verified_banks=checks,verified_original_branches=len(branches),pause_after_unit_UTC=limit.isoformat(),scope='Task 4 only; no Task 1/2 training or full final consolidation',automatic_boot_startup=False))
    children={};records={};streams=[]
    def status(state,detail):
        data=dict(state=state,detail=detail,pid=os.getpid(),UTC=datetime.now(timezone.utc).isoformat(),attempt=str(attempt),children={k:v.pid for k,v in children.items() if v.poll() is None})
        write(attempt/'status.json',data,replace=True);write(root/'supervisor_state.json',data,replace=True);progress(4,detail,state)
        (root/'reports/CURRENT_EXECUTION.md').write_text('# Current execution — Task 4 only\n\n'+state+': '+detail+'\n\nTask 1 is paused at user request with recovery checkpoints retained. Tasks 2 and 3 are complete. Task 4 has one GPU worker and four one-BLAS-thread sensor workers, followed by scoring, matched fusion, historical references and uncertainty/report generation.\n\nAttempt: `'+str(attempt)+'`. Stage logs, source snapshot, bank/branch checks and process identities are inside. Existing completed banks/fits are reused. No full supervisor or final all-task consolidation is launched.\n\nSafe stop is requested at 05:30 Europe/Berlin and workers finish the current committed recording/partition or stage. Some CPU partitions can be long; a VM reset may lose the unfinished unit, not completed banks. No automatic reboot startup is installed. To resume, check all worker processes then run `PYTHONPATH=src ma_thesis_env/bin/python -B -m reassemble.additional_improvements.corruption_resume --attempt-dir <NEW_TIMESTAMPED_DIR>`. Keep fixed seeds, budgets and configuration.\n')
    def launch(stage):
        command=[sys.executable,'-B','-m','reassemble.additional_improvements.corruption_resume','--stage',stage,'--deadline',limit.isoformat()]
        stream=(attempt/(stage+'.log')).open('x');streams.append(stream)
        env={**os.environ,'PYTHONPATH':'src','PYTHONUNBUFFERED':'1','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','OPENBLAS_NUM_THREADS':'1' if stage.startswith('sensor') else '4','OMP_NUM_THREADS':'1' if stage.startswith('sensor') else '4','MKL_NUM_THREADS':'1' if stage.startswith('sensor') else '4'}
        child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stream,stderr=stream,env=env)
        children[stage]=child;record=dict(stage=stage,pid=child.pid,command=command,started_UTC=datetime.now(timezone.utc).isoformat());records[stage]=record;write(attempt/(stage+'.json'),record)
        status('running','Task 4 stage started: '+stage)
    def collect():
        paused=False
        for stage,child in children.items():
            code=child.poll()
            if code is not None and 'returncode' not in records[stage]:
                records[stage].update(returncode=code,finished_UTC=datetime.now(timezone.utc).isoformat());write(attempt/(stage+'.json'),records[stage],replace=True)
            if code==PAUSED:paused=True
            elif code not in [None,0]:raise RuntimeError(f'{stage} failed with code {code}; inspect retained log')
        return paused
    def wait_for(stages):
        while any(children[s].poll() is None for s in stages):
            if collect() or STOP or datetime.now(timezone.utc)>=limit:raise InterruptedError('Pause after current committed units')
            time.sleep(5)
        if collect():raise InterruptedError('Worker reached pause boundary')
    try:
        for n in range(4):launch('sensor'+str(n))
        receipt=attempt/'external_visual.json'
        if receipt.exists():
            from .task4_external import ExternalVisual
            children['visual']=ExternalVisual(receipt);records['visual']=read(receipt)
            write(attempt/'visual.json',records['visual']);status('running','Adopted recorded visual worker; no duplicate GPU job')
        else:launch('visual')
        wait_for(['visual'])
        launch('score');wait_for(['score'])
        wait_for(['sensor'+str(n) for n in range(4)])
        for stage in ['fusion','references','report']:
            if STOP or datetime.now(timezone.utc)>=limit:raise InterruptedError('Pause before next stage')
            launch(stage);wait_for([stage])
        for item in preserved:
            if identity(item['path'])!=item:raise ValueError('Protected artifact changed: '+item['path'])
        write(attempt/'completion_manifest.json',dict(preserved_count=len(preserved),preservation_passed=True,files=[identity(p) for p in task.rglob('*') if p.is_file() and p.name!='status.json'],report=identity(root/'reports/04_CORRUPTION_TRAINING_RESULTS.md')))
        status('complete','Task 4 complete; Task 1 remains paused; no winner combination or new task launched')
    except BaseException as exc:
        for child in children.values():
            if child.poll() is None:child.send_signal(signal.SIGTERM)
        status('stopping_after_unit' if isinstance(exc,InterruptedError) else 'failed_requires_review',str(exc))
        # Graceful unit completion preserves banks. Never SIGKILL a writer.
        for child in children.values():child.wait()
        try:collect()
        except RuntimeError:pass
        if isinstance(exc,InterruptedError):status('paused_at_unit_boundary','Task 4 stopped after committed units; resume with a fresh attempt')
        else:
            status('failed_requires_review',str(exc));raise
    finally:
        for stream in streams:stream.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--attempt-dir',type=Path);parser.add_argument('--stage',choices=list(STAGES)+['sensor'+str(i) for i in range(4)]);parser.add_argument('--deadline')
    args=parser.parse_args()
    if args.stage:
        if not args.deadline:parser.error('--deadline required for a stage')
        raise SystemExit(worker(args))
    if args.attempt_dir is None:parser.error('--attempt-dir required')
    main(args)
