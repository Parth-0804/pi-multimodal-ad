"""Serial, restartable execution lanes; all writes belong to the new study."""
from __future__ import annotations
import os
import platform
import subprocess
import sys
import threading
import time
import traceback
import psutil
from .common import STUDY, PROTOCOL_SHA256, protocol, read_json, write_json, immutable_json, fit_root, exclusive_lock, code_identity, utc, git_commit
from .resources import gate, gpu_snapshot, GIB

RUNTIME = STUDY / '13_reproducibility/runtime'


def admission():
    result = read_json(STUDY / '01_protocol_and_source_evidence/RESOURCE_ADMISSION.json')
    if result['status'] != 'ADMITTED' or result['protocol_sha256'] != PROTOCOL_SHA256:
        raise ValueError('Resource admission missing or stale')
    return result


def schedule(lane):
    seeds = admission()['admitted_twenty_epoch_seeds']
    jobs = [f'outer{o}_{r}' for o in range(3) for r in ['final', 'inner0', 'inner1', 'inner2']]
    if lane == 'cpu':
        return [('FROZEN100', 42, 'outer0_inner0'), ('DONOR100', 42, 'outer0_inner0')] + [
            (condition, seed, job) for seed in seeds for job in jobs for condition in ['FROZEN20', 'DONOR20']]
    if lane == 'gpu':
        return [('FULL100', 42, 'outer0_inner0')] + [('FULL20', seed, job) for seed in seeds for job in jobs]
    raise ValueError(lane)


def process_identity():
    p = psutil.Process()
    return {'pid': p.pid, 'create_time': p.create_time(), 'git_commit': git_commit(), 'python': platform.python_version()}


def status(lane, stage, **extra):
    return write_json(RUNTIME / f'{lane.upper()}_CONTROLLER_STATUS.json',
                      {'utc': utc(), 'lane': lane, 'stage': stage, **process_identity(), **extra})


def check_frozen_code():
    path = STUDY / '13_reproducibility/IMPLEMENTATION_FREEZE.json'
    saved = read_json(path)
    if saved['protocol_sha256'] != PROTOCOL_SHA256 or saved['implementation'] != code_identity():
        raise ValueError('Frozen implementation changed; do not silently resume with different code')


def freeze_code():
    import importlib.metadata
    versions = {}
    for name in ['torch', 'torchvision', 'transformers', 'numpy', 'scipy', 'scikit-learn', 'pandas', 'psutil', 'av']:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = 'not installed'
    path = STUDY / '13_reproducibility/IMPLEMENTATION_FREEZE.json'
    if path.exists():
        check_frozen_code()
        return read_json(path)
    value = {'utc': utc(), 'protocol_sha256': PROTOCOL_SHA256, 'implementation': code_identity(),
             'git_commit': git_commit(), 'git_dirty': bool(subprocess.check_output(['git','status','--porcelain'], cwd=STUDY, text=True).strip()), 'python': sys.version, 'packages': versions,
             'command': 'ma_thesis_env/bin/python -B VIFAILBACK/experiments/matched_cnn_20_100_f2_20261111/scripts/study.py run --lane cpu|gpu',
             'input_manifest': '02_dataset_and_splits/DATASET_AND_SPLIT_VERIFICATION.json',
             'no_push': True}
    immutable_json(path, value)
    return value


class GPUMonitor:
    def __init__(self):
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.samples = 0
        self.util_sum = 0
        self.peak_MiB = 0
        self.started = time.monotonic()
        self.identity = process_identity()
        self.session_path = RUNTIME / f'GPU_SESSION_{self.identity["pid"]}_{int(self.identity["create_time"])}.json'

    def run(self):
        while not self.stop.is_set():
            try:
                value = gpu_snapshot()
                self.samples += 1
                util = value['devices'][0]['utilization_percent']
                self.util_sum += util
                self.peak_MiB = max(self.peak_MiB, value['devices'][0]['memory_used_MiB'])
                value.update(samples=self.samples, mean_observed_utilization_percent=self.util_sum / self.samples,
                             peak_device_used_MiB=self.peak_MiB, current_process_hours=(time.monotonic()-self.started)/3600,
                             sampling_seconds=10, scope='device utilization during this controller process; elapsed includes decoding and validation')
                write_json(RUNTIME / 'GPU_TELEMETRY.json', value)
                write_json(self.session_path, {'utc': utc(), **self.identity, 'observed_process_seconds': time.monotonic()-self.started, 'stage': 'RUNNING', 'meaning': 'Observed elapsed process time includes decoding, training, validation and checkpointing; lower bound if process is killed.'})
                with (RUNTIME / 'GPU_TELEMETRY.jsonl').open('a') as stream:
                    import json
                    stream.write(json.dumps(value) + '\n')
            except Exception as exc:
                write_json(RUNTIME / 'GPU_MONITOR_WARNING.json', {'utc': utc(), 'error': repr(exc)})
            self.stop.wait(10)

    def __enter__(self):
        RUNTIME.mkdir(parents=True, exist_ok=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set()
        self.thread.join(timeout=15)
        write_json(self.session_path, {'utc': utc(), **self.identity, 'observed_process_seconds': time.monotonic()-self.started, 'stage': 'PROCESS_SESSION_ENDED', 'study_complete': False, 'meaning': 'Elapsed for this controller process session; scientific completion is determined by fit receipts.'})


def run(lane):
    from .data import load_context
    from .training import fit
    import contextlib
    check_frozen_code()
    with exclusive_lock(RUNTIME / f'{lane}.lock'):
        plans = schedule(lane)
        status(lane, 'VERIFYING_INPUTS', planned_fits=len(plans))
        completed = []
        monitor = GPUMonitor() if lane == 'gpu' else contextlib.nullcontext()
        try:
            context = load_context(verify=True)
            with monitor:
                for condition, seed, job in plans:
                    check_frozen_code()
                    while True:
                        state = gate(extra_bytes=512 * 1024 ** 2 if lane == 'gpu' else 16 * 1024 ** 2,
                                     require_gpu=lane == 'gpu')
                        write_json(RUNTIME / f'{lane.upper()}_RESOURCE_GATE.json', state)
                        if state['ready']:
                            break
                        status(lane, 'WAITING_RESOURCES', condition=condition, seed=seed, fit_id=job,
                               reasons=state['reasons'], completed_fits=len(completed), planned_fits=len(plans))
                        time.sleep(30)
                    status(lane, 'TRAINING', condition=condition, seed=seed, fit_id=job,
                           fit_directory=str(fit_root(condition, seed, job).relative_to(STUDY)),
                           completed_fits=len(completed), planned_fits=len(plans))
                    receipt = fit(condition, seed, job, context=context)
                    completed.append({'condition': condition, 'seed': seed, 'fit_id': job,
                                      'executed_epochs': receipt['executed_epochs']})
                    write_json(RUNTIME / f'{lane.upper()}_COMPLETED_FITS.json', completed)
                status(lane, 'COMPLETE', completed_fits=len(completed), planned_fits=len(plans))
        except BaseException as exc:
            status(lane, 'INTERRUPTED' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'FAILED',
                   error=repr(exc), completed_fits=len(completed), planned_fits=len(plans), traceback=traceback.format_exc(),
                   resume='Re-run this lane; completed receipts are checked and unfinished fits resume at committed epoch boundary.')
            raise


def completed_fingerprint():
    from .common import signature, sha256
    paths = []
    for root in ['03_frozen20', '04_full20', '05_frozen100', '06_full100', '07_reassemble_donor_transfer']:
        paths.extend((STUDY / root).rglob('COMPLETE.json'))
    return signature({str(p.relative_to(STUDY)): sha256(p) for p in sorted(paths)})


def evaluate():
    from .data import load_context
    from .fusion_evaluation import evaluate_available
    from .reporting import generate
    with exclusive_lock(RUNTIME / 'evaluation.lock'):
        context = load_context(verify=True)
        result = evaluate_available(context=context)
        generate()
        return result


def worker_alive(state):
    try:
        process = psutil.Process(state['pid'])
        return abs(process.create_time() - state['create_time']) < .01 and process.status() != psutil.STATUS_ZOMBIE
    except (KeyError, psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def watch():
    from .reporting import generate
    check_frozen_code()
    with exclusive_lock(RUNTIME / 'watch.lock'):
        last = None
        while True:
            fingerprint = completed_fingerprint()
            try:
                if fingerprint != last:
                    evaluate()
                    last = fingerprint
                else:
                    generate()
                states = [read_json(RUNTIME / f'{lane}_CONTROLLER_STATUS.json') if (RUNTIME / f'{lane}_CONTROLLER_STATUS.json').exists() else {} for lane in ['CPU','GPU']]
                stages = [s.get('stage', 'NOT_LAUNCHED') for s in states]
                missing_workers = [s.get('lane') for s in states if s.get('stage') in ['TRAINING','VERIFYING_INPUTS','WAITING_RESOURCES'] and not worker_alive(s)]
                if missing_workers:
                    write_json(RUNTIME / 'WATCH_STATUS.json', {'utc': utc(), 'stage': 'PARTIAL_AWAITING_RESUME', 'missing_workers': missing_workers, 'reason': 'Saved process identity is no longer alive; unfinished epoch remains resumable.'})
                    generate()
                    return
                write_json(RUNTIME / 'WATCH_STATUS.json', {'utc': utc(), 'stage': 'WATCHING', 'lane_stages': stages,
                           'evaluated_completion_fingerprint': last})
                if all(s == 'COMPLETE' for s in stages):
                    terminal_fingerprint = completed_fingerprint()
                    if terminal_fingerprint != last:
                        evaluate()
                        last = terminal_fingerprint
                    write_json(RUNTIME / 'WATCH_STATUS.json', {'utc': utc(), 'stage': 'COMPLETE'})
                    return
                if any(s in ['FAILED', 'INTERRUPTED'] for s in stages):
                    write_json(RUNTIME / 'WATCH_STATUS.json', {'utc': utc(), 'stage': 'PARTIAL_AWAITING_RESUME', 'lane_stages': stages})
                    return
            except Exception as exc:
                write_json(RUNTIME / 'WATCH_STATUS.json', {'utc': utc(), 'stage': 'EVALUATION_FAILED', 'error': repr(exc), 'traceback': traceback.format_exc()})
                raise
            time.sleep(60)
