"""Adopt an active fit and stop the unchanged C20 study after seed 42 only."""
from pathlib import Path
import fcntl
import json
import os
import signal
import sys
import time
import traceback

import psutil

HERE = Path(__file__).resolve().parent


def allowed_schedule(schedule, request):
    allowed = [(seed, job) for seed, job in schedule
               if seed == request['allowed_seed']]
    assert len(allowed) == request['stop_after_completed_fits'] == 25
    assert [job['job_index'] for _, job in allowed] == list(range(25))
    return allowed


def live(identity):
    try:
        p = psutil.Process(identity['pid'])
        return (p.is_running() and p.status() != psutil.STATUS_ZOMBIE
                and p.create_time() == identity['create_time'])
    except psutil.NoSuchProcess:
        return False


def process_identity(pid):
    p = psutil.Process(pid)
    return {'pid': pid, 'create_time': p.create_time(), 'command': p.cmdline()}


def checked_controller(identity, expected_script):
    assert live(identity), 'CONTROLLER_NOT_ALIVE_OR_PID_REUSED'
    p = psutil.Process(identity['pid'])
    assert p.cmdline() == identity['command'], 'CONTROLLER_COMMAND_CHANGED'
    assert str(expected_script.resolve()) in p.cmdline(), 'WRONG_CONTROLLER'
    assert p.uids().real == os.getuid(), 'DIFFERENT_PROCESS_OWNER'
    return p


def checked_child(identity, trainer, seed, job_index):
    assert live(identity), 'TRAINING_CHILD_NOT_ALIVE_OR_PID_REUSED'
    args = psutil.Process(identity['pid']).cmdline()
    assert str(trainer.resolve()) in args, 'WRONG_TRAINING_SCRIPT'
    assert args[args.index('--seed') + 1] == str(seed), 'WRONG_CHILD_SEED'
    assert args[args.index('--job') + 1] == str(job_index), 'WRONG_CHILD_JOB'
    return psutil.Process(identity['pid'])


def release_controller(controller, identity):
    # Deliberately signal one process, never a process group or its children.
    controller.send_signal(signal.SIGTERM)
    try:
        controller.wait(timeout=10)
    except psutil.TimeoutExpired:
        raise RuntimeError('ORIGINAL_CONTROLLER_DID_NOT_RELEASE_CONTROL')
    assert not live(identity)


def verify_receipt(receipt, seed, job, config_sha, folder, sha):
    assert receipt['status'] == 'COMPLETE'
    assert receipt['seed'] == seed and receipt['job_index'] == job['job_index']
    assert receipt['executed_epochs'] == 20, 'INCOMPLETE_FIT'
    assert receipt['revision_configuration_sha256'] == config_sha, 'CONFIG_DRIFT'
    assert sha(folder/'PHASE1_PREDICTIONS.json') == receipt['predictions_sha256']
    assert sha(folder/'PHASE1_BEST_MODEL.pt') == receipt['selected_model_sha256']


def exclusive_stop(path, request):
    """Never replace an unrelated stop request."""
    if path.exists():
        assert json.loads(path.read_text())['request_id'] == request['request_id']
        return
    with path.open('x') as stream:
        json.dump(request, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def main():
    request = json.loads((HERE/'STOP_AFTER_25_REQUEST.json').read_text())
    revision = HERE.parent
    sys.path.insert(0, str(revision/'26102026_source'))
    import c20_controller as original
    from c20_common import (ARM, RUN, BASE, EXEC, EVIDENCE, REV_CONFIG,
                            schedule, receipt_for, read, write, sha, utc)
    from phase_training import folder_for
    from phase_common import host_resources

    allowed = allowed_schedule(schedule(), request)
    config_sha = sha(REV_CONFIG)
    expected = original.sources()
    assert read(revision/'26102026_evidence/PHASE1_C_ONLY_PROVENANCE.json')['revision_sources'] == expected
    original.assert_frozen(expected)
    stop = BASE/'STOP_AFTER_EPOCH.json'
    if stop.exists():
        assert read(stop).get('request_id') == request['request_id'], 'OTHER_STOP_REQUEST_PRESENT'
        assert (HERE/'STOP_AFTER_25_COMPLETE.json').exists(), 'CAP_STOP_NOT_FINALIZED'
        return

    def completed():
        return [(seed, job) for seed, job in allowed if receipt_for(seed, job).exists()]

    speed = read(EVIDENCE/'PHASE1_FULL_CNN_BENCHMARK.json')['actions_per_second']

    def publish(stage, **extra):
        done = completed()
        presentations = 0
        for seed, job in allowed:
            if receipt_for(seed, job).exists():
                continue
            pointer = folder_for(ARM, seed, job)/'PHASE1_LATEST_EPOCH.json'
            epoch = read(pointer)['completed_epoch'] if pointer.exists() else 0
            assert 0 <= epoch <= 20
            presentations += len(job['training'])*(20-epoch)
        hours = presentations/speed/3600
        value = {'utc': utc(), 'stage': stage, 'status': 'RUNNING', 'arm': ARM,
                 'epoch_budget': 20, 'pending_B_fits': 0,
                 'completed_C_fits': len(done), 'required_C_fits': 25,
                 'original_required_C_fits': 75, 'deferred_C_fits': 50,
                 'allowed_seed': request['allowed_seed'],
                 'remaining_CNN_training_hours': hours,
                 'remaining_planning_GPU_job_hours': [hours*1.2, hours*1.4],
                 'remaining_planning_days_exclusive_GPU': [hours*1.2/24, hours*1.4/24],
                 'stop_request_id': request['request_id'], 'controller_pid': os.getpid(),
                 'host_resources': host_resources(), **extra}
        write(RUN/'PHASE1_C_ONLY_STATUS.json', value)
        write(HERE/'STOP_AFTER_25_STATUS.json', value)
        return value

    # Reuse the exact training launcher. Only its status/report callbacks change.
    original.status = publish
    original.refresh = lambda value: value
    try:
        with (HERE/'STOP_AFTER_25_SINGLE_WRITER.lock').open('a') as guard_lock:
            fcntl.flock(guard_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state = read(RUN/'PHASE1_C_ONLY_STATUS.json')
            controller = None
            child_identity = None
            adopted = None
            if state.get('controller_pid') != os.getpid():
                pid = state.get('controller_pid')
                if pid and psutil.pid_exists(pid):
                    identity = process_identity(pid)
                    controller = checked_controller(identity, revision/'26102026_source/c20_controller.py')
                    assert state.get('seed') == request['allowed_seed']
                    adopted = next((s, j) for s, j in allowed
                                   if j['job_index'] == state['job_index'])
                    child_identity = process_identity(state['child_pid'])
                    child = checked_child(child_identity, revision/'26102026_source/c20_train.py',
                                          adopted[0], adopted[1]['job_index'])
                    assert child.ppid() == controller.pid, 'CHILD_PARENT_MISMATCH'
                    write(HERE/'CONTROLLER_HANDOFF_BEFORE.json',
                          {'utc': utc(), 'prior_status': state, 'controller': identity,
                           'child': child_identity, 'training_process_will_not_be_signaled': True})
                    # Children run in separate sessions. Signal the verified
                    # orchestrator PID only; the active fitter continues.
                    release_controller(controller, identity)
                elif state.get('child_pid') and psutil.pid_exists(state['child_pid']):
                    adopted = next((s, j) for s, j in allowed
                                   if s == state['seed'] and j['job_index'] == state['job_index'])
                    child_identity = process_identity(state['child_pid'])
                    checked_child(child_identity, revision/'26102026_source/c20_train.py',
                                  adopted[0], adopted[1]['job_index'])

            with (EXEC/'PHASE1_SINGLE_WRITER.lock').open('a') as study_lock:
                fcntl.flock(study_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                original.assert_frozen(expected)
                for seed, job in completed():
                    verify_receipt(read(receipt_for(seed, job)), seed, job, config_sha,
                                   folder_for(ARM, seed, job), sha)
                write(HERE/'CAP_ARMED.json', {'utc': utc(), 'controller_pid': os.getpid(),
                      'stop_after_completed_fits': 25, 'allowed_seed': 42,
                      'adopted_child': child_identity, 'original_sources_unchanged': True,
                      'epoch_budget_unchanged': 20, 'preexisting_completed_fits_verified': len(completed())})
                attempts = read(EXEC/'PHASE1_PROCESS_ATTEMPTS.json')
                if child_identity:
                    seed, job = adopted
                    while live(child_identity):
                        original.assert_frozen(expected)
                        if stop.exists():
                            raise InterruptedError('EXPLICIT_STOP_AFTER_EPOCH_REQUEST')
                        publish('C_ONLY_TRAINING', child_pid=child_identity['pid'], seed=seed,
                                job_index=job['job_index'], outer_fold=job['outer_fold_original'],
                                role=job['role'], adopted_existing_training_process=True,
                                active_child_elapsed_seconds=time.time()-child_identity['create_time'],
                                log=state.get('log'))
                        time.sleep(15)
                    assert receipt_for(seed, job).exists(), 'ADOPTED_FIT_EXITED_WITHOUT_COMPLETION'
                    verify_receipt(read(receipt_for(seed, job)), seed, job, config_sha,
                                   folder_for(ARM, seed, job), sha)
                    records = [row for row in attempts if row.get('child_pid') == child_identity['pid']]
                    assert len(records) == 1, 'ADOPTED_ATTEMPT_IDENTITY_MISMATCH'
                    records[0].update(status='COMPLETE', completed_utc=utc(),
                                      elapsed_seconds=time.time()-child_identity['create_time'],
                                      completion_verified_from_receipt=True,
                                      completion_observed_by_capped_controller=os.getpid())
                    write(EXEC/'PHASE1_PROCESS_ATTEMPTS.json', attempts)

                # No iteration over the remaining seeds is possible here.
                for seed, job in allowed:
                    if not receipt_for(seed, job).exists():
                        original.child(seed, job, expected, attempts)
                    verify_receipt(read(receipt_for(seed, job)), seed, job, config_sha,
                                   folder_for(ARM, seed, job), sha)
                    write(RUN/'PHASE1_C_ONLY_COMPLETED_INDEX.json',
                          [read(receipt_for(s, j)) for s, j in completed()])
                assert len(completed()) == 25
                assert len(list(RUN.glob('PHASE1_C_ONLY_COMPLETE_SEED*_JOB*.json'))) == 25
                stop_request = {'utc': utc(), 'request_id': request['request_id'],
                                'reason': 'User requested stop after 25 completed20-epoch fits',
                                'completed_C_fits': 25, 'allowed_seed': 42,
                                'do_not_start_remaining_seeds': True}
                exclusive_stop(stop, stop_request)
                write(HERE/'STOP_AFTER_25_COMPLETE.json', {
                    **stop_request, 'all25_completion_and_model_prediction_hashes_verified': True,
                    'five_outer_folds_complete': True, 'epochs_per_fit': 20,
                    'original_75_fit_study_complete': False, 'deferred_fits': 50,
                    'additional_CNN_training_launched_after_cap': False,
                    'original_training_configuration_sha256': config_sha})
                publish('STOPPED_AFTER_25_COMPLETED_FITS', status='STOPPED',
                        approved_fit_target_reached=True, complete_75_fit_study=False,
                        remaining_CNN_training_hours=0,
                        remaining_planning_GPU_job_hours=[0, 0],
                        remaining_planning_days_exclusive_GPU=[0, 0])
                write(HERE/'FINAL_COMPLETED_FIT_IDENTITIES.json',
                      [read(receipt_for(s, j)) for s, j in allowed])
    except Exception as exc:
        write(HERE/'CAP_FAILURE.json', {'utc': utc(), 'error': repr(exc),
                                      'traceback': traceback.format_exc()})
        publish('CAP_STOPPED' if isinstance(exc, InterruptedError) else 'CAP_BLOCKED',
                status='STOPPED' if isinstance(exc, InterruptedError) else 'PARTIAL', error=repr(exc))
        raise


if __name__ == '__main__':
    main()
