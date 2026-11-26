"""Single-GPU, single-writer Phase 1 execution with completed-epoch recovery."""
import fcntl
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

from phase_common import ROOT, REPO, AUDIT, STUDY, EXEC, EVIDENCE, CONFIG, config, read, write, sha, utc, environment, foreign_gpu_processes, host_resources


def source_paths():
    paths = list((ROOT/'26102026_source').glob('*.py'))
    paths += list((ROOT/'26102026_tests').glob('*.py'))
    paths += [CONFIG, EVIDENCE/'PHASE1_FIT_PLAN.json', EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json']
    paths += [ROOT/'26102026_reports/PHASE1_EXPERIMENT_PROTOCOL.md', EVIDENCE/'PHASE1_SOFTWARE_VALIDATION.json']
    paths += [STUDY/'shared_cache/original_features_16.npy', STUDY/'shared_cache/sensor_statistics.npy']
    paths += list((STUDY/'source').glob('*.py'))
    paths += [STUDY/'config/resolved_config.json', STUDY/'provenance/original_pretrained_identity.json']
    paths += [REPO/'src/reassemble/alignment.py']
    paths += [AUDIT/'source'/name for name in ['gpu_audit.py', 'managed_loader.py', 'isolated_decode.py']]
    return sorted(set(paths))


def frozen_sources():
    return {str(p.relative_to(REPO)): sha(p) for p in source_paths()}


def assert_frozen(expected):
    assert sources_match(expected), 'SOURCE_OR_INPUT_DRIFT: preserve active source and resume only with matching scientific implementation'


def sources_match(expected):
    try:
        return frozen_sources() == expected
    except OSError:
        return False


def remaining_estimate():
    from phase_training import folder_for
    speed = read(EVIDENCE/'PHASE1_FULL_CNN_BENCHMARK.json')['actions_per_second']
    minimum, maximum = 0, 0
    for seed in config()['seeds']:
        for job in read(EVIDENCE/'PHASE1_FIT_PLAN.json'):
            folder = folder_for('C_full_finetuned16', seed, job)
            if (folder/'PHASE1_FIT_COMPLETE.json').exists():
                continue
            pointer = folder/'PHASE1_LATEST_EPOCH.json'
            epoch = read(pointer)['completed_epoch'] if pointer.exists() else 0
            minimum += len(job['training'])*max(0, config()['min_epochs']-epoch)
            maximum += len(job['training'])*max(0, config()['max_epochs']-epoch)
    return {'remaining_planning_GPU_job_hours': [minimum/speed/3600*1.2, maximum/speed/3600*1.4],
            'basis': 'Remaining full-CNN presentations at measured pilot speed, plus20–40% overhead; exclusive GPU availability assumed'}


def save_status(stage, **extra):
    value = {'utc': utc(), 'stage': stage, 'controller_pid': os.getpid(), 'status': 'RUNNING',
             'host_resources': host_resources(), **remaining_estimate(), **extra}
    write(EXEC/'PHASE1_CONTROLLER_STATUS.json', value)
    return value


def freeze():
    path = EVIDENCE/'PHASE1_EXECUTION_PROVENANCE.json'
    sources = frozen_sources()
    if path.exists():
        value = read(path)
        assert value['sources'] == sources, 'SOURCE_DRIFT: frozen experiment implementation changed'
        return value
    snapshot = EXEC/'26102026_frozen_source_snapshot'
    for key in sources:
        source = REPO/key
        # Flat snapshot names avoid introducing undated directories. Keep the
        # original repo-relative identity and hash in the companion index.
        dest = snapshot / (sha(source)[:12] + '_' + source.name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    value = dict(environment(), sources=sources, configuration=config(),
        original_pretrained_identity=read(STUDY/'provenance/original_pretrained_identity.json'),
        full_CNN_gate=read(EVIDENCE/'PHASE1_FULL_CNN_GATE.json'),
        source_snapshot=str(snapshot.relative_to(ROOT)),
        warnings=['Previously studied dataset; not untouched confirmation',
                  'Only one GPU allocated; no concurrent GPU-heavy fits',
                  'No Phase 2/3, no commit or push'])
    write(path, value)
    return value


def wait_gpu(expected):
    from phase_reporting import refresh
    while True:
        assert_frozen(expected)
        if (ROOT/'STOP_AFTER_EPOCH.json').exists():
            raise InterruptedError('REQUESTED_STOP_AFTER_COMPLETED_EPOCH')
        busy = foreign_gpu_processes()
        if not busy:
            return
        state = save_status('WAITING_FOR_OTHER_GPU_JOB', other_gpu_process_ids=busy)
        refresh(state)
        # Controller-local sleep does not block the interactive agent.
        time.sleep(30)


def child(arm, seed, job, expected, attempts):
    from phase_training import folder_for
    from phase_reporting import refresh
    folder = folder_for(arm, seed, job)
    while True:
        wait_gpu(expected)
        assert shutil.disk_usage(ROOT).free >= config()['minimum_free_bytes'], 'DISK_LOW: preserve existing evidence; do not delete to continue'
        number = sum(r.get('arm') == arm and r.get('seed') == seed and r.get('job_index') == job['job_index'] for r in attempts) + 1
        log = EXEC/'26102026_logs'/f'PHASE1_SEED{seed}_{arm}_JOB{job["job_index"]:02d}_ATTEMPT{number:03d}.log'
        log.parent.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, '-B', str(ROOT/'26102026_source/phase_training.py'),
                   '--arm', arm, '--seed', str(seed), '--job', str(job['job_index'])]
        start = time.monotonic()
        record = {'arm': arm, 'seed': seed, 'job_index': job['job_index'], 'attempt': number,
                  'started_utc': utc(), 'command': command, 'log': str(log.relative_to(ROOT)), 'status': 'RUNNING'}
        attempts.append(record)
        with log.open('a', buffering=1) as output:
            process = subprocess.Popen(command, cwd=REPO, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            record['child_pid'] = process.pid
            write(EXEC/'PHASE1_PROCESS_ATTEMPTS.json', attempts)
            while process.poll() is None:
                if not sources_match(expected) and not (ROOT/'STOP_AFTER_EPOCH.json').exists():
                    write(ROOT/'STOP_AFTER_EPOCH.json', {'utc': utc(), 'reason': 'SOURCE_DRIFT detected; preserve completed boundary and stop affected work'})
                record['elapsed_seconds'] = time.monotonic() - start
                write(EXEC/'PHASE1_PROCESS_ATTEMPTS.json', attempts)
                save_status('CONTROLLED_TRAINING', arm=arm, seed=seed, job_index=job['job_index'],
                    outer_fold=job['outer_fold_original'], role=job['role'], child_pid=process.pid,
                    active_child_elapsed_seconds=record['elapsed_seconds'], log=str(log.relative_to(ROOT)),
                    completed_fit_count=sum((folder_for(a, s, j)/'PHASE1_FIT_COMPLETE.json').exists()
                        for s in config()['seeds'] for j in read(EVIDENCE/'PHASE1_FIT_PLAN.json') for a in config()['arms']))
                time.sleep(30)
        record.update(elapsed_seconds=time.monotonic()-start, completed_utc=utc(), exit_code=process.returncode,
                      status='COMPLETE' if process.returncode == 0 else 'INTERRUPTED_OR_FAILED')
        write(EXEC/'PHASE1_PROCESS_ATTEMPTS.json', attempts)
        if process.returncode == 0:
            assert (folder/'PHASE1_FIT_COMPLETE.json').exists()
            return
        tail = log.read_text()[-12000:]
        if 'FOREIGN_GPU_WORKLOAD' in tail or 'GPU_BUSY: do not launch competing work' in tail:
            refresh(save_status('WAITING_FOR_OTHER_GPU_JOB', interrupted_fit=record))
            continue
        if 'REQUESTED_STOP_AFTER_COMPLETED_EPOCH' in tail:
            raise InterruptedError('REQUESTED_STOP_AFTER_COMPLETED_EPOCH')
        raise RuntimeError(f'FIT_FAILED: {arm}, seed {seed}, job {job["job_index"]}; inspect {log.relative_to(ROOT)}. No accuracy conclusion.')


def main():
    EXEC.mkdir(parents=True, exist_ok=True)
    lock_path = EXEC/'PHASE1_SINGLE_WRITER.lock'
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (EXEC/'PHASE1_ALL_COMPLETE.json').exists():
            done = read(EXEC/'PHASE1_ALL_COMPLETE.json')
            assert sha(EXEC/'PHASE1_FINAL_METRICS.json') == done['final_metrics_sha256']
            print('Phase 1 already complete; no training or inference relaunched.', flush=True)
            return
        from phase_evaluation import sensor, summarize
        from phase_reporting import gpu_integration, refresh, output_manifest
        gate = read(EVIDENCE/'PHASE1_FULL_CNN_GATE.json')
        assert gate['status'] == 'PASSED' and gate['full_matrix_allowed']
        assert gate['protocol_sha256'] == sha(CONFIG)
        assert gate['fit_plan_sha256'] == sha(EVIDENCE/'PHASE1_FIT_PLAN.json')
        validation = read(EVIDENCE/'PHASE1_SOFTWARE_VALIDATION.json')
        assert validation['phase1_tests_passed'] and validation['git_diff_check_passed'] and validation['pip_check_passed']
        provenance = freeze()
        expected = provenance['sources']
        assert_frozen(expected)
        from phase_training import folder_for, run_identity
        jobs = read(EVIDENCE/'PHASE1_FIT_PLAN.json')
        assert len(jobs) == 25 and len(config()['seeds'])*len(jobs)*len(config()['arms']) == 150
        attempts_path = EXEC/'PHASE1_PROCESS_ATTEMPTS.json'
        attempts = read(attempts_path) if attempts_path.exists() else []
        # A prior controller crash may leave a live owned child. Never start a
        # duplicate; wait for its GPU context/process to finish before resume.
        for record in attempts:
            if record.get('status') == 'RUNNING':
                record['status'] = 'CONTROLLER_INTERRUPTED_LAST_OBSERVED_TIME_ONLY'
        write(attempts_path, attempts)
        gpu_integration()
        try:
            state = save_status('MATCHED_SENSOR_PREPARATION')
            refresh(state)
            for job in jobs:
                assert_frozen(expected)
                sensor(job)
            for seed in config()['seeds']:
                for job in jobs:
                    for arm in config()['arms']:
                        assert_frozen(expected)
                        done = folder_for(arm, seed, job)/'PHASE1_FIT_COMPLETE.json'
                        if done.exists():
                            value = read(done)
                            assert value['fit_identity'] == run_identity(arm, seed, job)
                            assert sha(done.parent/'PHASE1_PREDICTIONS.json') == value['predictions_sha256']
                            assert sha(done.parent/'PHASE1_BEST_MODEL.pt') == value['selected_model_sha256']
                            continue
                        child(arm, seed, job, expected, attempts)
                        refresh(save_status('CONTROLLED_TRAINING', last_completed={'arm': arm, 'seed': seed, 'job_index': job['job_index']}))
            state = save_status('FUSION_AND_PAIRED_EVALUATION')
            refresh(state)
            assert_frozen(expected)
            final = summarize(complete=True)
            wait_gpu(expected)
            from phase_inference import benchmark_inference
            benchmark_inference()
            state = save_status('FINAL_REPORT_GENERATION', status='RUNNING', completed_fit_count=150)
            refresh(state, final=final)
            output_manifest()
            write(EXEC/'PHASE1_ALL_COMPLETE.json', {'utc': utc(), 'status': 'COMPLETE', 'visual_fits': 150,
                  'main_F2_fits': 30, 'supplemental_short_F2_fits': 15, 'sensor_fits': 25,
                  'final_metrics_sha256': sha(EXEC/'PHASE1_FINAL_METRICS.json'),
                  'protocol_sha256': sha(CONFIG), 'phase2_or3_started': False})
            save_status('COMPLETE', status='COMPLETE', completed_fit_count=150)
        except Exception as exc:
            state = save_status('STOPPED_AT_COMPLETED_BOUNDARY' if isinstance(exc, InterruptedError) else 'BLOCKED',
                                status='PARTIAL', error=repr(exc), traceback=traceback.format_exc())
            refresh(state)
            output_manifest()
            raise


if __name__ == '__main__':
    main()
