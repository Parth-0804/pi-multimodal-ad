"""CPU-only admission regressions; fake resources never create a GPU context."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from future_dataloader import guards
from future_dataloader.benchmark import compare_throughput, run_benchmark


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


@pytest.fixture
def completed(tmp_path, monkeypatch):
    study = tmp_path / 'repo/VIFAILBACK/experiments/study'
    repo = study.parents[2]
    protocol = study / '01_protocol_and_source_evidence/protocol.json'
    write(protocol, {'test': 'synthetic only'})
    digest = guards._sha(protocol)
    monkeypatch.setattr(guards, 'PROTOCOL_SHA256', digest)
    write(study / '01_protocol_and_source_evidence/RESOURCE_ADMISSION.json', {
        'protocol_sha256': digest, 'admitted_twenty_epoch_seeds': [42, 123, 20261023],
        'full_fit_count': 37})
    for lane, count in [('GPU', 37), ('CPU', 74)]:
        write(study / f'13_reproducibility/runtime/{lane}_CONTROLLER_STATUS.json', {
            'stage': 'COMPLETE', 'completed_fits': count, 'planned_fits': count,
            'pid': 999999, 'create_time': 10.})
    (study / '13_reproducibility/runtime/gpu.lock').write_text('existing controller lock\n')
    monkeypatch.setattr(guards, '_process_state', lambda pid, ctime: 'ABSENT')
    host = {'disk_free_bytes': 30 * guards.GIB,
            'effective_RAM_available_bytes': 32 * guards.GIB,
            'shared_memory_free_bytes': 16 * guards.GIB,
            'GPU_compute_pids': [], 'CPU_affinity': list(range(16)),
            'GPU_devices': [{'index': 0, 'free_bytes': 16 * guards.GIB}]}
    monkeypatch.setattr(guards, '_resources', lambda _: host.copy())
    plans = [('FULL100', 42, 'outer0_inner0', 100)] + [
        ('FULL20', seed, f'outer{outer}_{role}', 20)
        for seed in (42, 123, 20261023) for outer in range(3)
        for role in ('final', 'inner0', 'inner1', 'inner2')]
    for condition, seed, job, budget in plans:
        root = study / ('06_full100' if budget == 100 else '04_full20') / f'seed{seed}' / job
        config = {'protocol_sha256': digest, 'epochs': budget}
        write(root / 'CONFIG.json', config)
        write(root / 'HISTORY.json', [{'epoch': epoch} for epoch in range(1, budget + 1)])
        write(root / 'predictions.json', [])
        write(root / 'OUTER_PREDICTIONS.json', [])
        (root / 'best.bin').write_bytes(b'synthetic checkpoint fixture')
        receipt = {'condition': condition, 'seed': seed, 'fit_id': job,
                   'executed_epochs': budget, 'configuration_sha256': guards._signature(config),
                   'history_sha256': guards._sha(root / 'HISTORY.json'),
                   'prediction_sha256': guards._sha(root / 'predictions.json'),
                   'outer_prediction_sha256': guards._sha(root / 'OUTER_PREDICTIONS.json')}
        for key in ('best', 'final'):
            receipt[f'{key}_checkpoint_path'] = str((root / 'best.bin').relative_to(repo))
            receipt[f'{key}_checkpoint_sha256'] = guards._sha(root / 'best.bin')
        write(root / 'COMPLETE.json', receipt)
    return study, host


def test_complete_and_idle_is_admissible(completed):
    study, _ = completed
    result = guards.inspect_admission(study)
    assert result['ready'] and result['completed_full_fits'] == 37


@pytest.mark.parametrize('stage', ['TRAINING', 'FAILED', 'INTERRUPTED', 'WAITING_RESOURCES'])
def test_not_complete_never_admitted_even_if_gpu_idle(completed, stage):
    study, _ = completed
    path = study / '13_reproducibility/runtime/GPU_CONTROLLER_STATUS.json'
    status = json.loads(path.read_text())
    status['stage'] = stage
    write(path, status)
    result = guards.inspect_admission(study)
    assert not result['ready'] and result['completed_full_fits'] == 0


@pytest.mark.parametrize('state', ['ALIVE', 'UNKNOWN'])
def test_complete_receipt_does_not_override_process_identity(completed, monkeypatch, state):
    study, _ = completed
    monkeypatch.setattr(guards, '_process_state', lambda pid, ctime: state)
    result = guards.inspect_admission(study)
    assert not result['ready']
    assert any('process identity' in text for text in result['reasons'])


def test_missing_last_queued_receipt_blocks(completed):
    study, _ = completed
    (study / '04_full20/seed20261023/outer2_inner2/COMPLETE.json').unlink()
    result = guards.inspect_admission(study)
    assert not result['ready']
    assert any('Protected-study verification failed' in text for text in result['reasons'])


def test_shortened_completed_budget_blocks(completed):
    study, _ = completed
    path = study / '06_full100/seed42/outer0_inner0/COMPLETE.json'
    receipt = json.loads(path.read_text())
    receipt['executed_epochs'] = 99
    write(path, receipt)
    assert not guards.inspect_admission(study)['ready']


def test_checkpoint_digest_drift_blocks(completed):
    study, _ = completed
    (study / '04_full20/seed20261023/outer2_inner2/best.bin').write_bytes(b'corrupt synthetic fixture')
    result = guards.inspect_admission(study)
    assert not result['ready']
    assert any('checkpoint hash mismatch' in text for text in result['reasons'])


@pytest.mark.parametrize('field,value', [
    ('GPU_compute_pids', [1234]),
    ('disk_free_bytes', 20 * guards.GIB),
    ('effective_RAM_available_bytes', 1 * guards.GIB),
    ('shared_memory_free_bytes', 1 * guards.GIB),
    ('CPU_affinity', [0]),
    ('GPU_devices', [{'index': 0, 'free_bytes': 4 * guards.GIB}]),
])
def test_resource_limits_fail_closed(completed, field, value):
    study, host = completed
    host[field] = value
    assert not guards.inspect_admission(study)['ready']


def test_gpu_query_failure_is_not_an_empty_gpu(completed, monkeypatch):
    study, _ = completed

    def unavailable(_):
        raise OSError('nvidia-smi unavailable')

    monkeypatch.setattr(guards, '_resources', unavailable)
    assert not guards.inspect_admission(study)['ready']


def test_existing_lock_is_preserved_and_competing_lock_blocks(completed):
    study, _ = completed
    lock = study / '13_reproducibility/runtime/gpu.lock'
    content = lock.read_bytes()
    with lock.open('r') as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(guards.AdmissionBlocked):
            with guards.benchmark_lease(study, study / 'future'):
                pytest.fail('Competing benchmark was admitted')
    with guards.benchmark_lease(study, study / 'future') as result:
        assert result['ready']
    assert lock.read_bytes() == content


def test_oversized_prefetch_configuration_rejected():
    with pytest.raises(ValueError, match='Unbounded'):
        guards.memory_bounds([{'num_workers': 4, 'prefetch_factor': 4}])


def test_probe_does_not_import_torch(completed, monkeypatch):
    import builtins
    study, _ = completed
    original = builtins.__import__

    def protected(name, *args, **kwargs):
        if name == 'torch' or name.startswith('torch.'):
            raise AssertionError('Admission must never import torch')
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', protected)
    assert guards.inspect_admission(study)['ready']


def test_pending_benchmark_does_not_import_torch(tmp_path, monkeypatch):
    import builtins
    from future_dataloader import benchmark
    original = builtins.__import__

    def protected(name, *args, **kwargs):
        if name == 'torch' or name.startswith('torch.'):
            raise AssertionError('Blocked benchmark must never import torch')
        return original(name, *args, **kwargs)

    @contextmanager
    def blocked(**kwargs):
        raise guards.AdmissionBlocked({'ready': False, 'reasons': ['synthetic active protected lane']})
        yield  # pragma: no cover

    monkeypatch.setattr(builtins, '__import__', protected)
    monkeypatch.setattr(benchmark, 'benchmark_lease', blocked)
    monkeypatch.setattr(benchmark, 'LOCAL_ROOT', tmp_path)
    result = run_benchmark(tmp_path / 'new', ['baseline_w2_p1', 'w4_p1'])
    assert result['status'] == 'PENDING' and not result['GPU_measurement_performed']
    assert not result['numerical_equivalence_pass']
    assert result['recommendation']['config'] is None
    assert (tmp_path / 'new/GPU_BENCHMARK.json').is_file()


def test_recommendation_requires_repeated_measured_improvement():
    names = ['baseline_w2_p1', 'w4_p1']
    good = [{'baseline_w2_p1': {'episodes_per_second': 1}, 'w4_p1': {'episodes_per_second': 1.1}} for _ in range(3)]
    assert compare_throughput(good, names)['config'] == 'w4_p1'
    good[1]['w4_p1']['episodes_per_second'] = .99
    assert compare_throughput(good, names)['config'] is None
    assert compare_throughput(good[:2], names)['config'] is None


def test_numerical_digest_covers_scalar_state_and_does_not_advance_rng():
    import random
    import torch
    from future_dataloader.benchmark import _tree_digest
    before_python, before_torch = random.getstate(), torch.get_rng_state().clone()
    state = {'parameter': torch.arange(8, dtype=torch.float32),
             'optimizer_step': torch.tensor(1.), 'nested': [('state', 3)]}
    original = _tree_digest(state)
    assert original == _tree_digest(state)
    state['optimizer_step'] = torch.tensor(2.)
    assert original != _tree_digest(state)
    assert random.getstate() == before_python
    assert torch.equal(torch.get_rng_state(), before_torch)
