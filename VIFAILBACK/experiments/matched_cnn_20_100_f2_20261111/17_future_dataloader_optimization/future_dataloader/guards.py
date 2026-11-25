"""Read-only, fail-closed admission for a manually requested future GPU benchmark.

Importing this module never imports torch or initializes CUDA. Completion of the
whole protected 37-fit lane is required: an epoch gap or crashed worker is not
GPU availability. No command in this module restarts or changes that lane.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

STUDY = Path(__file__).resolve().parents[2]
LOCAL_ROOT = Path(__file__).resolve().parents[1]
GIB = 1024 ** 3
EPISODE_BYTES = 3 * 16 * 3 * 640 * 640 * 4
PROTOCOL_SHA256 = '71cbb3b01b0adb47d2e055bf79391276f1f2f3a9dd339e5b0f07013932caa9c5'


class AdmissionBlocked(RuntimeError):
    def __init__(self, snapshot):
        self.snapshot = snapshot
        super().__init__('; '.join(snapshot['reasons']))


def _read(path):
    return json.loads(Path(path).read_text())


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def _process_state(pid, create_time):
    import psutil
    try:
        process = psutil.Process(int(pid))
        if abs(process.create_time() - float(create_time)) >= .01:
            return 'PID_REUSED'
        return 'ZOMBIE' if process.status() == psutil.STATUS_ZOMBIE else 'ALIVE'
    except psutil.NoSuchProcess:
        return 'ABSENT'
    except (psutil.AccessDenied, ValueError, TypeError):
        return 'UNKNOWN'


def gpu_processes():
    result = subprocess.run(
        ['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=10, check=True)
    return sorted({int(row.strip()) for row in result.stdout.splitlines() if row.strip()})


def assert_no_other_gpu_processes():
    """Called between bounded minibatches; a new competing context aborts us."""
    others = [pid for pid in gpu_processes() if pid != os.getpid()]
    if others:
        raise RuntimeError(f'Future benchmark aborted: competing GPU process(es) {others}')


def _resources(study):
    import psutil
    memory = psutil.virtual_memory()
    effective = int(memory.available)
    cgroup = []
    # Host MemAvailable alone can overstate a container's memory entitlement.
    mount = Path('/sys/fs/cgroup')
    membership = [line.split(':', 2)[2] for line in Path('/proc/self/cgroup').read_text().splitlines()
                  if line.startswith('0::')]
    if len(membership) != 1:
        raise ValueError('Cannot verify current cgroup v2 memory entitlement')
    current_base = (mount / membership[0].lstrip('/')).resolve()
    if current_base != mount and mount not in current_base.parents:
        raise ValueError('Current cgroup path escapes visible cgroup mount')
    # A cgroup namespace may expose its own root rather than the host path.
    if not current_base.is_dir():
        raise ValueError('Current cgroup memory limits are not visible')
    ancestors = [current_base] + [base for base in current_base.parents
                                  if base == mount or mount in base.parents]
    for base in ancestors:
        maximum, current = base / 'memory.max', base / 'memory.current'
        if maximum.exists() and current.exists():
            raw = maximum.read_text().strip()
            used = int(current.read_text().strip())
            cgroup.append({'path': str(base.relative_to(mount)),
                           'memory_max': raw, 'memory_current': used})
            if raw != 'max':
                effective = min(effective, max(0, int(raw) - used))
    devices = subprocess.run(
        ['nvidia-smi', '--query-gpu=index,memory.total,memory.free',
         '--format=csv,noheader,nounits'], capture_output=True, text=True,
        timeout=10, check=True)
    gpu = []
    for line in devices.stdout.splitlines():
        index, total, free = [int(value.strip()) for value in line.split(',')]
        gpu.append({'index': index, 'total_bytes': total * 1024 ** 2,
                    'free_bytes': free * 1024 ** 2})
    return {'disk_free_bytes': shutil.disk_usage(study).free,
            'RAM_available_bytes': int(memory.available),
            'effective_RAM_available_bytes': effective, 'cgroup': cgroup,
            'shared_memory_free_bytes': shutil.disk_usage('/dev/shm').free,
            'CPU_affinity': sorted(os.sched_getaffinity(0)),
            'GPU_devices': gpu, 'GPU_compute_pids': gpu_processes()}


def memory_bounds(configurations=None):
    """Conservative working envelopes, not claims of measured allocations.

    Account for a full eight-episode training minibatch, queued float32 episodes,
    copies into pinned memory, decoder/transformation temporaries, and model/
    interpreter/state hashing overhead. No persistent frame cache is permitted.
    """
    configs = configurations or [{'num_workers': 4, 'prefetch_factor': 2,
                                  'pin_memory': True}]
    rows = []
    for config in configs:
        values = asdict(config) if is_dataclass(config) else dict(config)
        workers = int(values['num_workers'])
        prefetch = int(values.get('prefetch_factor') or 0)
        if not 1 <= workers <= 4 or not 1 <= prefetch <= 4 or workers * prefetch > 8:
            raise ValueError('Unbounded loader worker/prefetch configuration')
        queue = workers * prefetch
        rows.append({'num_workers': workers, 'prefetch_factor': prefetch,
                     'RAM_required_bytes': (8 + 2 * queue + 3 * workers + 4) * EPISODE_BYTES + 2 * GIB,
                     'shared_memory_required_bytes': (queue + workers + 2) * EPISODE_BYTES})
    return {'per_configuration': rows,
            'RAM_required_bytes': max(row['RAM_required_bytes'] for row in rows),
            'shared_memory_required_bytes': max(row['shared_memory_required_bytes'] for row in rows),
            'disk_reserve_bytes': 20 * GIB, 'output_allowance_bytes': 256 * 1024 ** 2,
            'GPU_free_required_bytes': 8 * GIB}


def _protected_receipts(study):
    """Verify all prescribed budgets, configuration/history/prediction hashes.

    Weight files must exist with the expected digest. This check is reached only
    after both protected lanes are complete and their processes have exited.
    """
    jobs = [f'outer{o}_{role}' for o in range(3)
            for role in ('final', 'inner0', 'inner1', 'inner2')]
    plans = [('FULL100', 42, 'outer0_inner0', 100)] + [
        ('FULL20', seed, job, 20) for seed in (42, 123, 20261023) for job in jobs]
    repo = study.parents[2]
    results = []
    for condition, seed, job, budget in plans:
        parent = study / ('06_full100' if budget == 100 else '04_full20') / f'seed{seed}' / job
        receipt = _read(parent / 'COMPLETE.json')
        config = _read(parent / 'CONFIG.json')
        if (receipt['condition'], receipt['seed'], receipt['fit_id'], receipt['executed_epochs']) != (condition, seed, job, budget):
            raise ValueError(f'Protected fit identity/budget mismatch: {condition}/{seed}/{job}')
        if config['protocol_sha256'] != PROTOCOL_SHA256 or config['epochs'] != budget:
            raise ValueError('Protected completed configuration differs from frozen budget')
        if receipt['configuration_sha256'] != _signature(config):
            raise ValueError('Protected completed configuration hash mismatch')
        if _sha(parent / 'HISTORY.json') != receipt['history_sha256']:
            raise ValueError('Protected completed history hash mismatch')
        if [row['epoch'] for row in _read(parent / 'HISTORY.json')] != list(range(1, budget + 1)):
            raise ValueError('Protected epoch history incomplete')
        for filename, key in [('predictions.json', 'prediction_sha256')]:
            if _sha(parent / filename) != receipt[key]:
                raise ValueError('Protected prediction hash mismatch')
        if budget == 100 and _sha(parent / 'OUTER_PREDICTIONS.json') != receipt['outer_prediction_sha256']:
            raise ValueError('Protected outer prediction hash mismatch')
        for key in ('best', 'final'):
            path = Path(receipt[f'{key}_checkpoint_path'])
            path = path if path.is_absolute() else repo / path
            if study not in path.resolve().parents or not path.is_file():
                raise ValueError('Protected checkpoint path unavailable/outside study')
            if _sha(path) != receipt[f'{key}_checkpoint_sha256']:
                raise ValueError('Protected completed checkpoint hash mismatch')
        results.append({'condition': condition, 'seed': seed, 'fit_id': job,
                        'executed_epochs': budget, 'receipt_sha256': _sha(parent / 'COMPLETE.json')})
    return results


def inspect_admission(study=STUDY, configurations=None):
    """A read-only status probe; does not create a lock or import torch/CUDA."""
    study = Path(study).resolve()
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'ready': False,
              'status': 'PENDING', 'reasons': [], 'protected_lane_status': {},
              'completed_full_fits': 0, 'torch_imported_by_guard': False}
    reasons = result['reasons']
    try:
        protocol_path = study / '01_protocol_and_source_evidence/protocol.json'
        if _sha(protocol_path) != PROTOCOL_SHA256:
            raise ValueError('Frozen protocol digest changed')
        admission = _read(study / '01_protocol_and_source_evidence/RESOURCE_ADMISSION.json')
        if admission['protocol_sha256'] != PROTOCOL_SHA256 or admission['admitted_twenty_epoch_seeds'] != [42, 123, 20261023] or admission['full_fit_count'] != 37:
            raise ValueError('Protected 37-fit queue definition changed')
        for lane, expected in [('GPU', 37), ('CPU', 74)]:
            status = _read(study / f'13_reproducibility/runtime/{lane}_CONTROLLER_STATUS.json')
            alive = _process_state(status['pid'], status['create_time'])
            result['protected_lane_status'][lane] = {**status, 'observed_process_state': alive}
            if status['stage'] != 'COMPLETE' or status.get('completed_fits') != expected or status.get('planned_fits') != expected:
                reasons.append(f'{lane} protected lane is not completely finished ({expected} fits required)')
            if alive not in ('ABSENT', 'PID_REUSED', 'ZOMBIE'):
                reasons.append(f'{lane} controller is alive or its process identity cannot be verified: {alive}')
        if not reasons:
            result['protected_completed_fits'] = _protected_receipts(study)
            result['completed_full_fits'] = len(result['protected_completed_fits'])
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        reasons.append(f'Protected-study verification failed: {type(exc).__name__}: {exc}')
    try:
        bounds = memory_bounds(configurations)
        resources = _resources(study)
        result.update(resource_bounds=bounds, resources=resources)
        if resources['GPU_compute_pids']:
            reasons.append('GPU already has compute processes; idle samples do not permit admission')
        if len(resources['GPU_devices']) != 1:
            reasons.append('Benchmark requires the original single visible physical GPU')
        elif resources['GPU_devices'][0]['free_bytes'] < bounds['GPU_free_required_bytes']:
            reasons.append('Insufficient free GPU memory')
        if resources['disk_free_bytes'] - bounds['output_allowance_bytes'] < bounds['disk_reserve_bytes']:
            reasons.append('20 GiB storage reserve plus benchmark output allowance unavailable')
        if resources['effective_RAM_available_bytes'] < bounds['RAM_required_bytes']:
            reasons.append('Insufficient effective RAM for conservative loader envelope')
        if resources['shared_memory_free_bytes'] < bounds['shared_memory_required_bytes']:
            reasons.append('Insufficient /dev/shm for conservative loader envelope')
        if len(resources['CPU_affinity']) < 2:
            reasons.append('Fewer than two available CPU affinity slots')
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        reasons.append(f'Resource inspection failed closed: {type(exc).__name__}: {exc}')
    result['ready'] = not reasons
    result['status'] = 'ADMISSIBLE' if result['ready'] else 'PENDING'
    return result


@contextmanager
def benchmark_lease(study=STUDY, local_root=LOCAL_ROOT, configurations=None):
    """Acquire both advisory leases and repeat admission before any GPU import.

    The protected lock is opened read-only: its contents and timestamps are not
    rewritten. Locking protects against the existing cooperative controller;
    unrelated GPU jobs are also checked before every benchmark minibatch.
    """
    study, local_root = Path(study).resolve(), Path(local_root).resolve()
    if study not in local_root.parents or local_root == study:
        raise ValueError('Benchmark lock must be under the isolated study subdirectory')
    snapshot = inspect_admission(study, configurations)
    if not snapshot['ready']:
        raise AdmissionBlocked(snapshot)
    handles = []
    try:
        old = (study / '13_reproducibility/runtime/gpu.lock').open('r')
        handles.append(old)
        fcntl.flock(old, fcntl.LOCK_EX | fcntl.LOCK_NB)
        local_root.mkdir(parents=True, exist_ok=True)
        new = (local_root / 'future_benchmark.lock').open('a+')
        handles.append(new)
        fcntl.flock(new, fcntl.LOCK_EX | fcntl.LOCK_NB)
        snapshot = inspect_admission(study, configurations)
        if not snapshot['ready']:
            raise AdmissionBlocked(snapshot)
        yield snapshot
    except (BlockingIOError, FileNotFoundError) as exc:
        raise AdmissionBlocked({'ready': False, 'status': 'PENDING',
                                'reasons': [f'Exclusive benchmark lock unavailable: {exc}']}) from exc
    finally:
        for handle in reversed(handles):
            fcntl.flock(handle, fcntl.LOCK_UN)
            handle.close()
