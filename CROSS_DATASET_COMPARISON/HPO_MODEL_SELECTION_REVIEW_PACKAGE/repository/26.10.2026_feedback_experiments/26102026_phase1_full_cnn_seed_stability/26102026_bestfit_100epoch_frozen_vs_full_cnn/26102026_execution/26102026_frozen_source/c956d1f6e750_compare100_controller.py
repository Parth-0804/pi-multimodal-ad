"""Cooperative epoch pause, isolated comparison, and automatic original resumption."""
import fcntl
import os
import shutil
import subprocess
import sys
import time
import traceback

import psutil

from compare100_common import BASE,DETOUR,MAIN_REVISION,MAIN_EXEC,REPO,EVIDENCE,RUN,REPORTS,CONFIG,JOB
from compare100_common import read,write,sha,utc,configuration,environment,status,folder_for
from phase_common import foreign_gpu_processes
from phase_training import folder_for as main_folder_for,run_identity as main_identity
from phase_checkpoint import EpochRecovery
from compare100_report import refresh,finalize,output_manifest

PROOF=DETOUR/'26102026_evidence/PHASE1_PAUSE_COMPLETE.json'
PROVENANCE=DETOUR/'26102026_evidence/PHASE1_COMPARISON_PROVENANCE.json'
MAIN_STATUS=MAIN_REVISION/'26102026_execution/PHASE1_C_ONLY_STATUS.json'


def alive(pid):
    try:
        p=psutil.Process(pid)
        return p.is_running() and p.status()!=psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False


def main_sources_ok():
    original=read(EVIDENCE/'PHASE1_EXECUTION_PROVENANCE.json')['sources']
    revision=read(MAIN_REVISION/'26102026_evidence/PHASE1_C_ONLY_PROVENANCE.json')['revision_sources']
    assert all(sha(REPO/path)==value for path,value in {**original,**revision}.items()),'MAIN_SOURCE_OR_INPUT_DRIFT'


def sources():
    paths=[*(DETOUR/'26102026_source').glob('*.py'),*(DETOUR/'26102026_tests').glob('*.py'),
           *(DETOUR/'26102026_configuration').glob('*.json'),REPORTS/'PHASE1_100EPOCH_PROTOCOL.md',
           DETOUR/'26102026_evidence/PHASE1_VALIDATION.json',DETOUR/'26102026_evidence/PHASE1_FIT_SELECTION.json']
    return {str(p.relative_to(REPO)):sha(p) for p in paths}


def frozen():
    main_sources_ok()
    assert sources()==read(PROVENANCE)['sources'],'COMPARISON_SOURCE_DRIFT'


def main_job():
    initial=read(DETOUR/'26102026_evidence/PHASE1_MAIN_STATUS_AT_REQUEST.json')
    plan=read(EVIDENCE/'PHASE1_FIT_PLAN.json')
    return initial,next(j for j in plan if j['job_index']==initial['job_index'])


def own_stop(marker,request):
    assert marker.exists() and read(marker).get('request_id')==request['request_id'],'DIFFERENT_STOP_REQUEST_MUST_BE_HONORED'


def wait_original():
    if PROOF.exists():return
    initial,_=main_job()
    while alive(initial['controller_pid']) or alive(initial['child_pid']):
        frozen()
        own_stop(BASE/'STOP_AFTER_EPOCH.json',read(DETOUR/'26102026_evidence/PHASE1_PAUSE_REQUEST.json'))
        refresh(status('WAITING_FOR_ORIGINAL_COMPLETED_EPOCH',controller_pid=os.getpid(),
                       original_controller_pid=initial['controller_pid'],original_child_pid=initial['child_pid']))
        time.sleep(15)


def retain_pause():
    if PROOF.exists():return
    frozen()
    initial,job=main_job()
    latest=read(MAIN_STATUS)
    assert latest['stage']=='STOPPED','MAIN_DID_NOT_STOP_COOPERATIVELY'
    folder=main_folder_for('C_full_finetuned16',initial['seed'],job)
    pointer=read(folder/'PHASE1_LATEST_EPOCH.json')
    assert pointer['completed_epoch']<=20
    checkpoint=EpochRecovery(folder,main_identity('C_full_finetuned16',initial['seed'],job)).load()
    assert all(k in checkpoint for k in ['model','optimizer','scheduler','random','history','selected_payloads','next_order_sha256'])
    assert len(checkpoint['history'])==pointer['completed_epoch']
    retained=RUN/'26102026_paused_study_checkpoint';retained.mkdir(exist_ok=True)
    target=retained/pointer['slot']
    if not target.exists():shutil.copyfile(folder/pointer['slot'],target)
    assert sha(target)==pointer['sha256']
    write(retained/'PHASE1_PAUSED_POINTER.json',pointer)
    write(DETOUR/'26102026_evidence/PHASE1_MAIN_STOPPED_STATUS.json',latest)
    proof={'utc':utc(),'status':'COMPLETE','seed':initial['seed'],'job_index':job['job_index'],
           'folder':str(folder.relative_to(BASE)),'pointer':pointer,'next_order_sha256':checkpoint['next_order_sha256'],
           'retained_checkpoint':str(target.relative_to(DETOUR)),
           'model_optimizer_scheduler_rng_sampler_and_best_preserved':True,'original_cap':20,'original_scheduler_horizon':50}
    write(PROOF,proof)
    write(MAIN_STATUS,{**latest,'utc':utc(),'stage':'TEMPORARILY_PAUSED_FOR_100_EPOCH_COMPARISON',
          'resume_completed_epoch':pointer['completed_epoch'],'comparison_status':str((RUN/'PHASE1_COMPARISON_STATUS.json').relative_to(BASE))})


def archive_pause_request():
    # Only the exact request created for this detour may be consumed.
    stop=BASE/'STOP_AFTER_EPOCH.json'
    archived=DETOUR/'26102026_evidence/PHASE1_PAUSE_STOP_COMPLETED.json'
    if archived.exists():
        assert not stop.exists(),'NEW_USER_STOP_MUST_BE_HONORED'
        return
    own_stop(stop,read(DETOUR/'26102026_evidence/PHASE1_PAUSE_REQUEST.json'))
    stop.rename(archived)


def no_stop():
    if (BASE/'STOP_AFTER_EPOCH.json').exists() or (DETOUR/'STOP_AFTER_EPOCH.json').exists():
        raise InterruptedError('EXPLICIT_STOP_REQUEST_MUST_BE_HONORED')


def wait_gpu():
    while True:
        frozen();no_stop()
        busy=foreign_gpu_processes()
        if not busy:return
        refresh(status('WAITING_FOR_OTHER_GPU_JOB',controller_pid=os.getpid(),other_gpu_process_ids=busy))
        time.sleep(30)


def check_receipt(arm):
    folder=folder_for(arm,configuration()['seed'],read(JOB))
    path=folder/'PHASE1_COMPARISON_ARM_COMPLETE.json'
    if not path.exists():return False
    r=read(path)
    assert r['epochs']==100 and r['configuration_sha256']==sha(CONFIG)
    assert sha(folder/'PHASE1_PREDICTIONS.json')==r['predictions_sha256']
    assert sha(folder/'PHASE1_BEST_MODEL.pt')==r['selected_model_sha256']
    return True


def run_arm(arm):
    attempt_path=RUN/'PHASE1_COMPARISON_PROCESS_ATTEMPTS.json'
    attempts=read(attempt_path) if attempt_path.exists() else []
    while not check_receipt(arm):
        wait_gpu()
        assert shutil.disk_usage(BASE).free>=configuration()['minimum_free_bytes'],'DISK_LOW'
        number=sum(r['arm']==arm for r in attempts)+1
        log=RUN/'26102026_logs'/f'PHASE1_{arm}_ATTEMPT{number:03d}.log'
        log.parent.mkdir(exist_ok=True)
        command=[sys.executable,'-B',str(DETOUR/'26102026_source/compare100_train.py'),'--arm',arm]
        record={'arm':arm,'attempt':number,'started_utc':utc(),'command':[str(p).replace(str(REPO)+'/','') for p in command],
                'log':str(log.relative_to(DETOUR)),'status':'RUNNING'}
        attempts.append(record);start=time.monotonic();guard_error=None
        with log.open('x') as output:
            process=subprocess.Popen(command,cwd=REPO,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
            record['child_pid']=process.pid
            record['child_create_time']=psutil.Process(process.pid).create_time()
            write(attempt_path,attempts)
            while process.poll() is None:
                try:
                    frozen()
                    assert shutil.disk_usage(BASE).free>=configuration()['minimum_free_bytes'],'DISK_LOW'
                    no_stop()
                except Exception as exc:
                    guard_error=repr(exc)
                    if not (DETOUR/'STOP_AFTER_EPOCH.json').exists():
                        write(DETOUR/'STOP_AFTER_EPOCH.json',{'utc':utc(),'reason':guard_error})
                record['elapsed_seconds']=time.monotonic()-start
                write(attempt_path,attempts)
                state=status('COMPARISON_TRAINING',controller_pid=os.getpid(),child_pid=process.pid,arm=arm,
                             active_child_elapsed_seconds=record['elapsed_seconds'],guard_error=guard_error)
                refresh(state)
                time.sleep(30)
        record.update(elapsed_seconds=time.monotonic()-start,completed_utc=utc(),exit_code=process.returncode,
                      status='COMPLETE' if process.returncode==0 else 'INTERRUPTED_OR_FAILED')
        write(attempt_path,attempts)
        if guard_error:raise RuntimeError(guard_error)
        if process.returncode==0:
            assert check_receipt(arm)
            return
        tail=log.read_text()[-16000:]
        if 'FOREIGN_GPU_WORKLOAD' in tail or 'GPU_BUSY:' in tail:continue
        if 'REQUESTED_STOP_AFTER_COMPLETED_EPOCH' in tail:raise InterruptedError('COMPARISON_STOPPED_AT_COMPLETED_EPOCH')
        raise RuntimeError(f'COMPARISON_ARM_FAILED: inspect {log.relative_to(DETOUR)}')


def resume_command():
    return [sys.executable,'-B',str(MAIN_REVISION/'26102026_source/c20_controller.py')]


def resume_main():
    # Called after releasing the writer lock. Existing completion receipts and
    # the retained original checkpoint, never the new100-epoch weights, resume.
    main_sources_ok();no_stop()
    assert shutil.disk_usage(BASE).free>=configuration()['minimum_free_bytes'],'DISK_LOW'
    proof=read(PROOF);folder=BASE/proof['folder']
    path=RUN/'PHASE1_MAIN_STUDY_RESUMPTION_RECEIPT.json'
    if path.exists():
        old=read(path)
        if alive(old['controller_pid']):
            process=psutil.Process(old['controller_pid'])
            assert abs(process.create_time()-old['controller_create_time'])<.01
            assert str(MAIN_REVISION/'26102026_source/c20_controller.py') in process.cmdline()
            return old
        # A completed resumption is not repeated after a later deliberate stop.
        assert not old.get('recovery_verified'),'MAIN_ALREADY_RESUMED_THEN_STOPPED_INSPECT_STATUS'
    pointer=read(folder/'PHASE1_LATEST_EPOCH.json')
    assert pointer==proof['pointer'],'PAUSED_MAIN_CHECKPOINT_CHANGED'
    assert sha(folder/pointer['slot'])==pointer['sha256']
    command=resume_command()
    stamp=str(time.time_ns())
    log=RUN/'26102026_logs'/f'PHASE1_MAIN_RESUME_{stamp}.log'
    with log.open('x') as output:
        process=subprocess.Popen(command,cwd=REPO,stdin=subprocess.DEVNULL,stdout=output,
                                 stderr=subprocess.STDOUT,start_new_session=True)
    receipt={'utc':utc(),'controller_pid':process.pid,'controller_create_time':psutil.Process(process.pid).create_time(),
             'command':[str(p).replace(str(REPO)+'/','') for p in command],
             'log':str(log.relative_to(DETOUR)),'resumed_completed_epoch':pointer['completed_epoch'],
             'next_epoch':pointer['completed_epoch']+1,'next_order_sha256':proof['next_order_sha256'],
             'original_cap':20,'original_scheduler_horizon':50,'100_epoch_weights_reused':False,
             'recovery_verified':False}
    write(path,receipt)
    deadline=time.monotonic()+180
    while time.monotonic()<deadline and process.poll() is None:
        resume=folder/'PHASE1_RESUMPTION.json'
        if resume.exists():
            value=read(resume)
            if value['utc']>=receipt['utc']:
                assert value['completed_epoch']==pointer['completed_epoch']
                assert value['next_order_sha256']==proof['next_order_sha256']
                receipt.update(recovery_verified=True,recovery_receipt=value)
                write(path,receipt)
                break
        time.sleep(5)
    assert process.poll() is None,'MAIN_RESUME_CONTROLLER_EXITED_INSPECT_LOG'
    assert receipt['recovery_verified'],'MAIN_RESUME_NOT_VERIFIED_WITHIN180_SECONDS'
    write(BASE/'PHASE1_ACTIVE_REVISION.json',{'utc':utc(),'active_revision':str(MAIN_REVISION.relative_to(BASE)),
          'status':'C_ONLY_20_EPOCH_STUDY_RESUMED','completed_comparison':str(DETOUR.relative_to(BASE)),
          'comparison_status':str((RUN/'PHASE1_COMPARISON_STATUS.json').relative_to(BASE))})
    return receipt


def main():
    RUN.mkdir(exist_ok=True)
    assert read(DETOUR/'26102026_evidence/PHASE1_VALIDATION.json')['passed']
    with (RUN/'PHASE1_COMPARISON_SINGLE_WRITER.lock').open('a') as supervisor_lock:
        fcntl.flock(supervisor_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        frozen()
        try:
            wait_original()
            with (MAIN_EXEC/'PHASE1_SINGLE_WRITER.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                retain_pause();archive_pause_request()
                write(BASE/'PHASE1_ACTIVE_REVISION.json',{'utc':utc(),'active_revision':str(DETOUR.relative_to(BASE)),
                      'status':'TEMPORARY_100_EPOCH_COMPARISON','automatic_resume':str(MAIN_REVISION.relative_to(BASE))})
                for arm in configuration()['arms']:run_arm(arm)
                frozen();no_stop()
                final=finalize()
                write(RUN/'PHASE1_COMPARISON_ALL_COMPLETE.json',{'utc':utc(),'status':'COMPLETE','arms':2,'epochs_per_arm':100,
                      'metrics_sha256':sha(RUN/'PHASE1_100EPOCH_COMPARISON_METRICS.json')})
                refresh(status('COMPARISON_COMPLETE_PREPARING_MAIN_RESUME'),final)
            # The original controller acquires the same lock, so release first.
            receipt=resume_main()
            refresh(status('COMPLETE_MAIN_STUDY_RESUMED',status='COMPLETE',resumption=receipt),final)
            output_manifest()
        except Exception as exc:
            state=status('STOPPED' if isinstance(exc,InterruptedError) else 'BLOCKED',status='PARTIAL',
                         error=repr(exc),traceback=traceback.format_exc(),controller_pid=os.getpid(),
                         main_resume_pending=True)
            refresh(state);output_manifest()
            # Never conceal a failed comparison or integrity stop by launching
            # another GPU job. Checkpoints allow explicit safe continuation.
            raise


if __name__=='__main__':main()
