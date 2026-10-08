"""Resume only the already-authorized sensor task; no visual/corruption queue."""
import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo
from .common import config, identity, progress, read, storage, write


class PlannedPause(Exception):
    pass


def pause_deadline(now):
    local=now.astimezone(ZoneInfo('Europe/Berlin'))
    start=local.replace(hour=5,minute=50,second=0,microsecond=0)
    end=local.replace(hour=6,minute=10,second=0,microsecond=0)
    if start<=local<end:
        raise PlannedPause('Daily reset window: do not start training before 06:10 Europe/Berlin')
    if local>=end:start+=timedelta(days=1)
    return start.astimezone(timezone.utc)


def verify(entries):
    for item in entries:
        if identity(item['path']) != item:
            raise ValueError('PROTECTED OUTPUT CHANGED: '+item['path'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt-dir',type=Path,required=True)
    args=parser.parse_args();attempt=args.attempt_dir
    if (attempt/'preflight.json').exists():raise FileExistsError('Use a fresh recovery attempt directory')
    attempt.mkdir(parents=True,exist_ok=True)
    c=config();root=Path(c['run_dir']);task=root/'02_patchtst_training_budget'
    lock=(root/'supervisor.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    deadline=pause_deadline(datetime.now(timezone.utc));storage()
    # Never edit neural/model/config signatures to force reuse of a completed fit.
    protected_code=[Path('src/reassemble/additional_improvements')/n for n in ['neural.py','models.py']]
    protected_code.append(Path('configs/reassemble/additional_improvements/execution.json'))
    dirty=subprocess.check_output(['git','diff','HEAD','--',*map(str,protected_code)],text=True)
    if dirty:raise ValueError('Frozen neural/model/config sources changed; inspect before resuming')
    existing=[p for p in task.rglob('*') if p.is_file() and p.name!='status.json']
    existing+=list((root/'reports').glob('02_PATCHTST*'))+protected_code
    preserved=[identity(p) for p in sorted(existing)]
    indexed={x['path']:x for x in preserved};checks=0
    for path in (task/'fits').rglob('*.json'):
        obj=read(path)
        for field in ['checkpoint','predictions']:
            item=obj.get(field)
            if isinstance(item,dict) and 'sha256' in item:
                if indexed.get(item['path'])!=item:raise ValueError('Checkpoint/prediction identity mismatch: '+str(path))
                checks+=1
    for path in (task/'fits').rglob('*.pt'):
        if not path.with_suffix('.json').exists():raise ValueError('Preserve and inspect incomplete fit: '+str(path))
    snapshot=attempt/'source';snapshot.mkdir()
    for path in Path('src/reassemble/additional_improvements').glob('*.py'):shutil.copyfile(path,snapshot/path.name)
    old_status={str(p):read(p) for p in [root/'status.json',root/'supervisor_state.json',*[root/name/'status.json' for name in ['01_temporal_visual','02_patchtst_training_budget','03_static_anchored_adaptation','04_corruption_training']]] if p.exists()}
    record=dict(started_UTC=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),scope='Sensor Task 2 only; visual and corruption work deferred',pause_before_new_fit_UTC=deadline.isoformat(),checkpoint_boundaries='Reuse complete original fits; no mid-fit state recovery added. At deadline finish current short fit then pause before next fit.',automatic_reboot_restart_installed=False,git_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),fitting_identities_verified=checks,preserved_files=preserved,prior_status=old_status,config=identity('configs/reassemble/additional_improvements/execution.json'),free_GiB=shutil.disk_usage('.').free/2**30,source_files=[identity(p) for p in snapshot.iterdir()],command=sys.argv,environment_threads={name:os.environ.get(name) for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']})
    write(attempt/'preflight.json',record)
    (attempt/'source_changes.diff').write_text(subprocess.check_output(['git','diff','--','src/reassemble/additional_improvements/hybrid.py','src/reassemble/additional_improvements/unimodal_report.py'],text=True))
    write(root/'supervisor_state.json',dict(state='sensor_task2_only',pid=os.getpid(),attempt=str(attempt),full_supervisor_running=False,UTC=datetime.now(timezone.utc).isoformat()),replace=True)
    progress(1,'Primary visual comparisons complete; V-FT deferred pending user decision','deferred_by_user')
    progress(4,'Interrupted by daily VM reset; not included in sensor-only resumption','not_running')
    def current(state,detail):
        write(attempt/'status.json',dict(state=state,detail=detail,pid=os.getpid(),UTC=datetime.now(timezone.utc).isoformat()),replace=True)
        (root/'reports/CURRENT_EXECUTION.md').write_text('# Current additional-improvements execution\n\nSensor Task 2 only. '+state+': '+detail+'\n\nAttempt: `'+str(attempt)+'`. Log: `'+str(attempt/'worker.log')+'`.\n\nOriginal neural.py, models.py and scientific configuration are unchanged. Completed folds/fits are reused. Visual Task 1 primary results already exist; V-FT and Task 4 are not running. No automatic restart after reboot is installed. Before 05:50 Europe/Berlin the current short fit may finish; no next fit is started after that deadline.\n\nThe versioned Task 2 completion report will be in `'+str(attempt/'report')+'`. Existing reports stay unchanged. Resume with a fresh timestamped attempt via `PYTHONPATH=src ma_thesis_env/bin/python -B -m reassemble.additional_improvements.sensor_resume --attempt-dir <NEW_ATTEMPT_DIR>` after checking processes; no full supervisor launch while visual work is deferred.\n')
    current('running','Preflight complete; resuming unfinished fixed sensor fits')
    from . import hybrid, neural, checkpoint_retention, unimodal_report
    def bounded(function):
        def call(*a,**kw):
            if datetime.now(timezone.utc)>=deadline:raise PlannedPause('Reached 05:50 Europe/Berlin; retained completed fits')
            return function(*a,**kw)
        return call
    neural.fit=bounded(neural.fit)
    checkpoint_retention._fit=bounded(checkpoint_retention._fit)
    try:
        if not (task/'hybrid_comparison/results.json').exists():hybrid.main()
        current('reporting','Sensor fits complete; selected checkpoint retention and versioned report')
        sys.argv=['unimodal_report','--task','2','--output-dir',str(attempt/'report')]
        unimodal_report.main()
        verify(preserved)
        fresh=[p for p in task.rglob('*') if p.is_file() and str(p) not in indexed and p.name!='status.json']
        fresh+=list((attempt/'report').iterdir())
        write(attempt/'completion_manifest.json',dict(preserved_count=len(preserved),preservation_passed=True,files=[identity(p) for p in fresh if p.is_file()],completed_UTC=datetime.now(timezone.utc).isoformat()))
        current('complete','Sensor Task 2 complete; visual and corruption tasks remain deferred')
        write(root/'supervisor_state.json',dict(state='sensor_task2_complete_other_work_deferred',attempt=str(attempt),full_supervisor_running=False,UTC=datetime.now(timezone.utc).isoformat()),replace=True)
    except PlannedPause as exc:
        verify(preserved);current('paused_before_daily_reset',str(exc));progress(2,str(exc),'paused_before_daily_reset')
        write(root/'supervisor_state.json',dict(state='paused_before_daily_reset',attempt=str(attempt),full_supervisor_running=False,UTC=datetime.now(timezone.utc).isoformat()),replace=True)
    except BaseException as exc:
        current('failed_requires_review',repr(exc));progress(2,repr(exc),'failed_requires_review')
        write(root/'supervisor_state.json',dict(state='failed_requires_review',attempt=str(attempt),full_supervisor_running=False,error=repr(exc),UTC=datetime.now(timezone.utc).isoformat()),replace=True)
        raise


if __name__=='__main__':main()
