"""C-only20 schedule, retaining the original numerical training implementation."""
import datetime as dt
import fcntl
import os
import shutil
import subprocess
import sys
import time
import traceback

import psutil

from c20_common import ARM, BASE, REVISION, RUN, REPORTS, EXEC, EVIDENCE, REV_CONFIG
from c20_common import configuration, schedule, receipt_for, read, write, sha, utc, status
from phase_common import REPO, foreign_gpu_processes, environment
from phase_training import folder_for, run_identity
from c20_report import refresh, finalize
from phase_reporting import output_manifest


def alive(pid):
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False


def sources():
    paths = [* (REVISION/'26102026_source').glob('*.py'), * (REVISION/'26102026_tests').glob('*.py'),
             REV_CONFIG, REPORTS/'PHASE1_EXPERIMENT_PROTOCOL.md', REVISION/'26102026_evidence/PHASE1_VALIDATION.json']
    return {str(p.relative_to(REPO)): sha(p) for p in paths}


def assert_frozen(expected):
    assert sources() == expected, 'C_ONLY_SOURCE_DRIFT'
    original = read(EVIDENCE/'PHASE1_EXECUTION_PROVENANCE.json')['sources']
    assert all(sha(REPO/path) == value for path,value in original.items()), 'ORIGINAL_TRAINING_SOURCE_OR_INPUT_DRIFT'


def wait_gpu(expected):
    while True:
        assert_frozen(expected)
        if (BASE/'STOP_AFTER_EPOCH.json').exists():
            raise InterruptedError('REQUESTED_STOP_AFTER_COMPLETED_EPOCH')
        busy = foreign_gpu_processes()
        if not busy:
            return
        refresh(status('WAITING_FOR_OTHER_GPU_JOB', other_gpu_process_ids=busy))
        time.sleep(30)


def transition():
    marker = REVISION/'26102026_evidence/PHASE1_TRANSITION_COMPLETE.json'
    if marker.exists():
        return
    initial = read(REVISION/'26102026_evidence/ORIGINAL_PHASE1_CONTROLLER_STATUS.json')
    controller, child = initial['controller_pid'], initial['child_pid']
    # This transition sends no signals. The original control file requests a
    # cooperative stop after committing the current epoch and closing workers.
    while alive(controller) or alive(child):
        refresh(status('WAITING_FOR_ORIGINAL_COMPLETED_EPOCH', original_controller_pid=controller,
                       original_C_child_pid=child))
        time.sleep(15)
    latest = read(EXEC/'PHASE1_CONTROLLER_STATUS.json')
    assert latest['stage'] == 'STOPPED_AT_COMPLETED_BOUNDARY', 'ORIGINAL_RUN_DID_NOT_STOP_AT_EXPECTED_BOUNDARY'
    progress = read(EXEC/'PHASE1_PROGRESS.json')
    job = next(j for _,j in schedule() if j['job_index'] == initial['job_index'])
    folder = folder_for(ARM, initial['seed'], job)
    pointer = read(folder/'PHASE1_LATEST_EPOCH.json')
    assert pointer['completed_epoch'] <= 20 and pointer['fit_identity'] == run_identity(ARM, initial['seed'], job)
    assert sha(folder/pointer['slot']) == pointer['sha256']
    retained = RUN/'26102026_transition_checkpoint'
    retained.mkdir(parents=True, exist_ok=True)
    target = retained/pointer['slot']
    if not target.exists():
        shutil.copyfile(folder/pointer['slot'], target)
    assert sha(target) == pointer['sha256']
    write(retained/'PHASE1_PRIOR_CHECKPOINT_POINTER.json', pointer)
    request = read(REVISION/'26102026_evidence/PHASE1_TRANSITION_REQUEST.json')
    stop = BASE/'STOP_AFTER_EPOCH.json'
    assert read(stop)['request_id'] == request['request_id'], 'DIFFERENT_STOP_REQUEST_MUST_BE_HONORED'
    stop.rename(REVISION/'26102026_evidence/PHASE1_TRANSITION_STOP_COMPLETED.json')
    write(marker, {'utc':utc(),'status':'COMPLETE','seed':initial['seed'],'job_index':initial['job_index'],
          'retained_completed_epoch':pointer['completed_epoch'],'checkpoint_sha256':pointer['sha256'],
          'model_optimizer_scheduler_rng_and_next_sampler_preserved':True,'B_pending_fits_removed':True,
          'original_source_configuration_changed':False})
    write(EXEC/'PHASE1_CONTROLLER_STATUS.json', {'utc':utc(),'status':'SUPERSEDED',
          'stage':'SUPERSEDED_BY_C_ONLY_20_EPOCH_REVISION','prior_complete_epoch':pointer['completed_epoch'],
          'replacement_status':str((RUN/'PHASE1_C_ONLY_STATUS.json').relative_to(BASE)),
          'historical_B_artifacts_preserved':True})


def child(seed, job, expected, attempts):
    while True:
        wait_gpu(expected)
        if receipt_for(seed,job).exists():
            return
        assert shutil.disk_usage(BASE).free >= configuration()['minimum_free_bytes'], 'DISK_LOW'
        attempt = sum(r.get('arm')==ARM and r.get('seed')==seed and r.get('job_index')==job['job_index'] for r in attempts)+1
        log = RUN/'26102026_logs'/f'PHASE1_C_SEED{seed}_JOB{job["job_index"]:02d}_ATTEMPT{attempt:03d}.log'
        log.parent.mkdir(parents=True,exist_ok=True)
        command = [sys.executable,'-B',str(REVISION/'26102026_source/c20_train.py'),'--seed',str(seed),'--job',str(job['job_index'])]
        record = {'arm':ARM,'seed':seed,'job_index':job['job_index'],'attempt':attempt,'started_utc':utc(),
                  'execution_protocol':configuration()['protocol'],'command':command,'log':str(log.relative_to(BASE)),'status':'RUNNING'}
        attempts.append(record)
        start = time.monotonic()
        with log.open('x') as output:
            process = subprocess.Popen(command,cwd=REPO,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
            record['child_pid'] = process.pid
            while process.poll() is None:
                try:
                    assert_frozen(expected)
                except (AssertionError,OSError):
                    if not (BASE/'STOP_AFTER_EPOCH.json').exists():
                        write(BASE/'STOP_AFTER_EPOCH.json',{'utc':utc(),'reason':'Frozen C-only source/input changed'})
                record['elapsed_seconds'] = time.monotonic()-start
                write(EXEC/'PHASE1_PROCESS_ATTEMPTS.json',attempts)
                status('C_ONLY_TRAINING',controller_pid=os.getpid(),child_pid=process.pid,seed=seed,
                       job_index=job['job_index'],outer_fold=job['outer_fold_original'],role=job['role'],
                       active_child_elapsed_seconds=record['elapsed_seconds'],log=str(log.relative_to(BASE)))
                time.sleep(30)
        record.update(elapsed_seconds=time.monotonic()-start,completed_utc=utc(),exit_code=process.returncode,
                      status='COMPLETE' if process.returncode==0 else 'INTERRUPTED_OR_FAILED')
        write(EXEC/'PHASE1_PROCESS_ATTEMPTS.json',attempts)
        if process.returncode == 0:
            assert receipt_for(seed,job).exists()
            return
        tail = log.read_text()[-12000:]
        if 'FOREIGN_GPU_WORKLOAD' in tail or 'GPU_BUSY: do not launch competing work' in tail:
            continue
        if 'REQUESTED_STOP_AFTER_COMPLETED_EPOCH' in tail:
            raise InterruptedError('REQUESTED_STOP_AFTER_COMPLETED_EPOCH')
        raise RuntimeError(f'C20_FIT_FAILED: inspect {log.relative_to(BASE)}')


def main():
    RUN.mkdir(parents=True,exist_ok=True)
    assert read(REVISION/'26102026_evidence/PHASE1_VALIDATION.json')['passed']
    try:
        transition()
        with (EXEC/'PHASE1_SINGLE_WRITER.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            provenance = REVISION/'26102026_evidence/PHASE1_C_ONLY_PROVENANCE.json'
            expected = sources()
            if provenance.exists():
                assert read(provenance)['revision_sources'] == expected
            else:
                current_environment=environment()
                assert current_environment['packages']==read(EVIDENCE/'PHASE1_EXECUTION_PROVENANCE.json')['packages'], 'SOFTWARE_VERSION_DRIFT'
                write(provenance,dict(current_environment,revision_sources=expected,configuration=configuration(),
                    original_provenance_sha256=sha(EVIDENCE/'PHASE1_EXECUTION_PROVENANCE.json'),
                    transition=read(REVISION/'26102026_evidence/PHASE1_TRANSITION_COMPLETE.json')))
                snapshot = RUN/'26102026_frozen_revision_source'
                snapshot.mkdir(exist_ok=True)
                for path,value in expected.items():
                    shutil.copyfile(REPO/path,snapshot/(value[:12]+'_'+(REPO/path).name))
            assert_frozen(expected)
            if (RUN/'PHASE1_C_ONLY_ALL_COMPLETE.json').exists():
                return
            attempts = read(EXEC/'PHASE1_PROCESS_ATTEMPTS.json')
            refresh(status('C_ONLY_TRAINING_PREPARATION',controller_pid=os.getpid()))
            for seed,job in schedule():
                assert_frozen(expected)
                if receipt_for(seed,job).exists():
                    result=read(receipt_for(seed,job)); folder=folder_for(ARM,seed,job)
                    assert result['executed_epochs']==20 and result['revision_configuration_sha256']==sha(REV_CONFIG)
                    assert sha(folder/'PHASE1_PREDICTIONS.json')==result['predictions_sha256']
                    assert sha(folder/'PHASE1_BEST_MODEL.pt')==result['selected_model_sha256']
                    continue
                child(seed,job,expected,attempts)
                refresh(status('C_ONLY_TRAINING',controller_pid=os.getpid()))
            refresh(status('C_ONLY_FUSION_ANALYSIS'))
            assert_frozen(expected)
            final=finalize()
            state=status('FINAL_REPORT_GENERATION')
            refresh(state,final=final)
            output_manifest()
            write(RUN/'PHASE1_C_ONLY_ALL_COMPLETE.json',{'utc':utc(),'status':'COMPLETE','C_fits':75,'epochs_each':20,
                  'new_B_fits':0,'F2_C_models':15,'metrics_sha256':sha(RUN/'PHASE1_C_ONLY_FINAL_METRICS.json')})
            status('COMPLETE',status='COMPLETE',controller_pid=os.getpid())
    except Exception as exc:
        state=status('STOPPED' if isinstance(exc,InterruptedError) else 'BLOCKED',status='PARTIAL',
                     error=repr(exc),traceback=traceback.format_exc(),controller_pid=os.getpid())
        refresh(state)
        raise


if __name__ == '__main__':
    main()
