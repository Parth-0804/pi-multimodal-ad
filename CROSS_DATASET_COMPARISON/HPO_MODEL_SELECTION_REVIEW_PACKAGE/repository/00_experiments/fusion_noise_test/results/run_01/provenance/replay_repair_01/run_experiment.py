#!/usr/bin/env python3
"""Foreground-only entry point for one fixed selected-model robustness study."""
import os,sys,time,json
from pathlib import Path
STUDY=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1';os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
for key,name in [('TMPDIR','tmp'),('MPLCONFIGDIR','matplotlib'),('XDG_CACHE_HOME','xdg'),('HF_HOME','huggingface')]:
    p=STUDY/'results/run_01/cache'/name;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
sys.path.insert(0,str(STUDY/'code'))
from common import RUN,REPO,config,read,write,write_text,event,budget,readiness,code_identity,utc


def stage(name,operation):
    p=read(RUN/'progress.json');failures=p.get('failures',{})
    if failures.get(name,0)>config()['technical_repair_cap']:raise RuntimeError('REPAIR_CAP '+name)
    try:return operation()
    except Exception:
        p=read(RUN/'progress.json');f=p.setdefault('failures',{});f[name]=f.get(name,0)+1;write(RUN/'progress.json',p);raise


def main():
    import argparse,subprocess
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('command',choices=['prepare','test','select','run','resume','evaluate','status']);parser.add_argument('--wait-seconds',type=int,default=0)
    args=parser.parse_args();assert 0<=args.wait_seconds<=3600
    if args.command=='status':print(json.dumps({'progress':read(RUN/'progress.json') if (RUN/'progress.json').exists() else None,'readiness':readiness()},indent=2));return
    if args.command=='test':
        result=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(STUDY/'tests'),'-v'],cwd=REPO,env=os.environ.copy(),capture_output=True,text=True)
        index=len(list((RUN/'checks').glob('test_attempt_*.txt')))+1
        write_text(RUN/'checks'/f'test_attempt_{index:02d}.txt',result.stdout+result.stderr)
        write(RUN/'checks/tests.json',{'passed':result.returncode==0,'returncode':result.returncode,'command':result.args,'source_identity':code_identity(),'scope':'CPU tests; no scientific selection, training or GPU inference'})
        print(result.stdout+result.stderr);raise SystemExit(result.returncode)
    from reporting import prepare,report,package
    from evaluation import evaluate
    if args.command=='evaluate':evaluate();report();package();return
    current_stage='prepare'
    try:
        prepare()
        if args.command=='prepare':
            ready=readiness();event('PREPARED' if ready['terminal_inputs'] else 'WAITING_FOR_PREVIOUS_RESULTS',blocker=None if ready['terminal_inputs'] else 'Visual-backbone study still active; encoder study has zero paired results. Selection deferred.');return
        checks=read(RUN/'checks/tests.json');assert checks['passed'] and checks['source_identity']==code_identity(),'FOCUSED_TESTS_REQUIRED'
        import fcntl
        with (RUN/'provenance/writer.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            remaining_wait=max(0,config()['max_wait_seconds']-read(RUN/'progress.json').get('total_wait_seconds',0.));requested=min(args.wait_seconds,remaining_wait)
            start=time.monotonic();waited=0.
            while True:
                budget();ready=readiness()
                if ready['terminal_inputs'] and (args.command=='select' or ready['gpu_available']):break
                status='WAITING_FOR_PREVIOUS_RESULTS' if not ready['terminal_inputs'] else 'WAITING_FOR_GPU'
                event(status,blocker='Upstream work is not terminal or allocated GPU remains owned; no selection or corrupted inference permitted.',foreground_pid=os.getpid())
                if waited>=requested:return
                before=time.monotonic();time.sleep(min(60,requested-waited));delta=time.monotonic()-before;waited+=delta
                state=read(RUN/'progress.json');state['total_wait_seconds']=state.get('total_wait_seconds',0.)+delta;write(RUN/'progress.json',state)
            assert read(RUN/'checks/tests.json')['source_identity']==code_identity(),'CODE_CHANGED_DURING_WAIT'
            partial=[str(p.relative_to(RUN)) for p in RUN.rglob('*') if p.is_file() and '.writing' in p.name]
            if partial:write(RUN/'checks/partial_files.json',{'preserved':partial});raise RuntimeError('PARTIAL_WRITES_REQUIRE_REVIEW')
            from selection import select
            current_stage='selection';selected=stage('selection',select)
            if args.command=='select':return
            import torch
            torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False
            assert torch.cuda.device_count()==1;torch.cuda.set_device(config()['gpu_index'])
            from inference import execute
            current_stage='inference';stage('inference',lambda:execute(selected))
    except Exception as exc:
        event('BLOCKED',blocker=repr(exc),failed_stage=current_stage)
        import traceback
        with (RUN/'logs/failures.txt').open('a') as f:traceback.print_exc(file=f)
        raise
    finally:
        if (RUN/'progress.json').exists():
            p=read(RUN/'progress.json');p.update(foreground_pid=None,background_worker=False,queued=False);write(RUN/'progress.json',p)
            evaluate();report();package()

if __name__=='__main__':main()
