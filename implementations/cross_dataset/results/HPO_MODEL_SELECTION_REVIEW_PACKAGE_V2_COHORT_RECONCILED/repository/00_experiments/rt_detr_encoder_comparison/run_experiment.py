#!/usr/bin/env python3
"""Foreground entry point for this single bounded experiment only."""
from pathlib import Path
import os
import sys
STUDY=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k]='2'
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
for key,sub in [('TMPDIR','tmp'),('MPLCONFIGDIR','matplotlib'),('XDG_CACHE_HOME','xdg'),('HF_HOME','huggingface')]:
    p=STUDY/'results/run_01/cache'/sub;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
sys.path.insert(0,str(STUDY/'code'))
if hasattr(os,'sched_getaffinity'):
    allowed=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,allowed[:2])
import argparse
import time
from common import RUN,REPO,read,write,write_text,sha,config,elapsed,budget,event,readiness,code_identity,signature


def scientific_stage(name, operation):
    state=read(RUN/'progress.json')
    failures=state.get('scientific_stage_failures',{})
    if failures.get(name,0)>=1+config()['technical_repair_cap_per_stage']:
        raise RuntimeError('TECHNICAL_REPAIR_CAP '+name)
    try:
        return operation()
    except Exception:
        state=read(RUN/'progress.json');counts=state.setdefault('scientific_stage_failures',{})
        counts[name]=counts.get(name,0)+1;write(RUN/'progress.json',state)
        raise


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('command',choices=['prepare','test','run','resume','status','evaluate'])
    parser.add_argument('--wait-seconds',type=int,default=0,help='Bounded foreground wait; never extends the original 24h deadline.')
    args=parser.parse_args()
    assert args.wait_seconds>=0
    if args.command=='status':
        print(__import__('json').dumps({'progress':read(RUN/'progress.json') if (RUN/'progress.json').exists() else {},'readiness':readiness()},indent=2));return
    if args.command=='test':
        import subprocess
        p=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(STUDY/'tests'),'-v'],cwd=REPO,capture_output=True,text=True,env=os.environ.copy())
        write_text(RUN/'checks/focused_tests.txt',p.stdout+p.stderr)
        write(RUN/'checks/focused_tests.json',{'passed':p.returncode==0,'returncode':p.returncode,'command':p.args,'source_hashes':code_identity(),'scope':'lightweight CPU tests; no scientific GPU extraction/fits'})
        print(p.stdout+p.stderr);raise SystemExit(p.returncode)
    from data import prepare,frame,check_input_stats
    from evaluation import evaluate,package
    if args.command=='evaluate':
        evaluate();package();return
    try:
        prepare()
        if args.command=='prepare':
            ready=readiness()
            event('PREPARED' if ready['available'] else 'WAITING_FOR_GPU',blocker=None if ready['available'] else 'Priority visual-backbone process still owns the sole allocated GPU; no competing work started.')
            return
        budget()
        tests=read(RUN/'checks/focused_tests.json')
        assert tests['passed'] and tests['source_hashes']==code_identity(),'RUN_FOCUSED_TESTS_AFTER_CODE_CHANGES'
        # Only one foreground scientific writer in this study.
        import fcntl
        with (RUN/'provenance/writer.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            wait_start=time.monotonic()
            while True:
                budget()
                ready=readiness()
                if ready['available']:break
                event('WAITING_FOR_GPU',blocker='Priority study/process still owns allocated device; extraction/fitting not started.',foreground_pid=os.getpid(),waiting_seconds=time.monotonic()-wait_start)
                if time.monotonic()-wait_start>=args.wait_seconds:return
                time.sleep(min(60,args.wait_seconds-(time.monotonic()-wait_start)))
            # Interrupted atomic writes are detected, retained and never treated
            # as completed artifacts or silently overwritten on restart.
            partials=[p for p in RUN.rglob('*') if p.is_file() and '.writing' in p.name]
            if partials:
                write(RUN/'checks/partial_files.json',{'files':[{'path':str(p.relative_to(RUN)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in partials]})
                raise RuntimeError('PARTIAL_ATOMIC_FILES_PRESERVED_REVIEW_REQUIRED')
            # Stable data/weights required after waiting as well.
            prepare();f=frame();check_input_stats(f)
            assert read(RUN/'checks/focused_tests.json')['source_hashes']==code_identity(), 'CODE_CHANGED_DURING_WAIT'
            import torch
            torch.set_num_threads(2);torch.set_num_interop_threads(1)
            torch.use_deterministic_algorithms(True)
            torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False
            torch.cuda.set_device(config()['gpu_index'])
            assert torch.cuda.is_available() and torch.cuda.device_count()==1,'ALLOCATED_DEVICE_AMBIGUITY'
            identity={'inputs':sha(RUN/'provenance/input_identity.json'),'code':code_identity(),'config':sha(STUDY/'config.json')}
            pinned=RUN/'provenance/scientific_identity.json'
            if pinned.exists():assert read(pinned)==identity,'SCIENTIFIC_IDENTITY_DRIFT'
            else:write(pinned,identity)
            from features import original,preflight,extract
            from data import Pixels
            from fitting import run_folds
            jobs=read(RUN/'data/fit_partitions.json');j=next(j for j in jobs if j['outer_fold_original']==0 and j['role']=='outer_assessment')
            extractor=original('cuda');pixels=Pixels()
            evidence=scientific_stage('preflight',lambda:preflight(extractor,pixels,f,j))
            estimated_extract=max(r['seconds_per_segment_after_warmup'] for r in evidence['results'])*len(f)
            estimated_storage=sum(r['dimension']*len(f)*4 for r in evidence['results'])+512*2**20
            write(RUN/'provenance/resource_estimate.json',{'estimated_extraction_compute_seconds':estimated_extract,'estimated_new_bytes_plus_512MiB_reserve':estimated_storage,'excludes_unknown_decode_time':True,'head_fitting_estimate':'small cached heads; measured by first real fit, no epoch reduction','resource_enforcement':'2 CPU affinity/BLAS threads; no loader workers; one device; storage/RSS monitored; deadline checked during fitting/extraction; no service or background queue'})
            budget(estimated_storage)
            if estimated_extract>config()['wall_seconds']-elapsed()-config()['report_reserve_seconds']:raise RuntimeError('INSUFFICIENT_REMAINING_EXTRACTION_BUDGET')
            arrays=scientific_stage('extraction',lambda:extract(extractor,pixels,f))
            scientific_stage('fitting',lambda:run_folds(f,jobs,arrays,extractor,pixels,identity))
            pixels.close();event('COMPLETE',blocker=None)
    except Exception as exc:
        event('BLOCKED',blocker=repr(exc))
        import traceback
        with (RUN/'logs/failures.txt').open('a') as f:traceback.print_exc(file=f)
        raise
    finally:
        if (RUN/'progress.json').exists():
            state=read(RUN/'progress.json');state.update(foreground_pid=None, background_worker=False, queued=False);write(RUN/'progress.json',state)
            evaluate();package()


if __name__=='__main__':main()
