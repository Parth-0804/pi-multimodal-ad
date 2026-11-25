"""Bounded Task 1 worker with interruption recovery; never launches Task 4."""
import argparse
from datetime import datetime,timezone
import fcntl
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
from .common import config,identity,progress,read,storage,write
from .sensor_resume import pause_deadline,verify
from .training_recovery import TrainingPaused,request_pause


def main():
    p=argparse.ArgumentParser();p.add_argument('--attempt-dir',type=Path,required=True)
    a=p.parse_args();attempt=a.attempt_dir;attempt.mkdir(parents=True,exist_ok=True)
    if (attempt/'preflight.json').exists():raise FileExistsError('Use a new timestamped attempt directory')
    c=config();root=Path(c['run_dir']);task=root/'01_temporal_visual'
    lock=(task/'visual_worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    deadline=pause_deadline(datetime.now(timezone.utc));storage()
    os.environ['REASSEMBLE_VISUAL_PAUSE_AT']=deadline.isoformat()
    signal.signal(signal.SIGTERM,request_pause);signal.signal(signal.SIGINT,request_pause)
    complete=read(task/'frozen_prefix/complete.json')
    for key in ['manifest','model','equivalence']:
        if identity(complete[key]['path'])!=complete[key]:raise ValueError('Frozen-prefix provenance changed')
    cache=read(task/'frozen_prefix/manifest.json')['files'];validation=attempt/'cache_validation.json'
    if validation.exists():
        if not read(validation)['passed'] or read(validation)['complete_identity']!=identity(task/'frozen_prefix/complete.json'):raise ValueError('Invalid cache verification')
    else:
        verify(cache);write(validation,dict(passed=True,segments=len(cache),bytes=sum(x['bytes'] for x in cache),complete_identity=identity(task/'frozen_prefix/complete.json'),UTC=datetime.now(timezone.utc).isoformat()))
    params=read(task/'finetune_gradient_audit.json')['trainable_parameters']
    reserve_estimate=75*params*4*(8+1)*1.15/2**30
    free=shutil.disk_usage('.').free/2**30
    if free-reserve_estimate<c['minimum_free_GiB']:raise RuntimeError(f'STORAGE BLOCKER: {free:.2f} GiB free; conservative remaining recovery/selected checkpoint estimate {reserve_estimate:.2f} GiB')
    cached={x['path']:x for x in cache};preserved=[]
    for item in task.rglob('*'):
        if not item.is_file() or item.name in ['status.json','visual_worker.lock']:continue
        relative=item.relative_to(task)
        if relative.parts[0]=='training_recovery' or ('V-FT' in relative.parts):continue
        preserved.append(cached[str(item)] if str(item) in cached else identity(item))
    preserved += [identity(x) for x in (root/'reports').glob('01_TEMPORAL*')]
    snapshot=attempt/'source';snapshot.mkdir()
    for path in Path('src/reassemble/additional_improvements').glob('*.py'):shutil.copyfile(path,snapshot/path.name)
    record=dict(pid=os.getpid(),scope='Remaining bounded V-FT in Task 1; existing primary comparisons reused; Task 4 stopped',UTC=datetime.now(timezone.utc).isoformat(),git_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_files=[identity(x) for x in snapshot.iterdir()],preserved_files=preserved,config=identity('configs/reassemble/additional_improvements/execution.json'),pause_UTC=deadline.isoformat(),free_GiB=free,conservative_recovery_plus_selected_GiB=reserve_estimate,checkpoint_policy='Two mutable atomic slots per fit; optimizer-step boundary every five minutes and each completed epoch; restore optimizer, AMP, random state, sample order/offset and selection state. No budget reset.',automatic_reboot_restart_installed=False)
    write(attempt/'preflight.json',record)
    (attempt/'source_changes.diff').write_text(subprocess.check_output(['git','diff','--','src/reassemble/additional_improvements/finetune.py','src/reassemble/additional_improvements/fit_summaries.py','src/reassemble/additional_improvements/unimodal_report.py'],text=True))
    def status(state,detail):
        write(attempt/'status.json',dict(state=state,detail=detail,pid=os.getpid(),UTC=datetime.now(timezone.utc).isoformat()),replace=True)
        progress(1,detail,state)
        (root/'reports/VISUAL_EXECUTION.md').write_text('# Task 1 visual continuation\n\n'+state+': '+detail+'\n\nAttempt: `'+str(attempt)+'`; worker.log, preflight.json and source snapshot are inside. Only original bounded V-FT runs; completed primary visual controls are reused. Recovery states are in `01_temporal_visual/training_recovery/`, selected checkpoints in `fits/V-FT/`.\n\nA disconnect may lose work since the last atomic checkpoint (target five minutes plus the current optimizer batch, or an unfinished validation pass). SIGTERM and the 05:50 Europe/Berlin deadline request a saved pause. No automatic reboot startup is installed. Resume this module with a NEW timestamped --attempt-dir after checking processes; never launch a duplicate visual worker. Final report will be in `'+str(attempt/'report')+'`.\n')
    try:
        status('running','Bounded visual fine-tuning with verified cache and interruption recovery')
        from . import finetune,unimodal_report
        if not (task/'finetune_comparison/results.json').exists():finetune.main()
        if not (task/'finetune_comparison/results.json').exists():raise RuntimeError('V-FT comparison incomplete; inspect status')
        status('reporting','V-FT fits complete; writing versioned Task 1 report')
        sys.argv=['unimodal_report','--task','1','--output-dir',str(attempt/'report')];unimodal_report.main()
        verify(preserved)
        files=[p for p in (task/'fits/V-FT').rglob('*') if p.is_file()]+list((attempt/'report').iterdir())
        write(attempt/'completion_manifest.json',dict(preservation_passed=True,preserved_count=len(preserved),files=[identity(x) for x in files],UTC=datetime.now(timezone.utc).isoformat()))
        status('complete','Task 1 complete; original bounded comparisons and report saved')
    except TrainingPaused as exc:
        status('paused_with_recovery_checkpoint',str(exc))
    except BaseException as exc:
        status('failed_requires_review',repr(exc));raise


if __name__=='__main__':main()
