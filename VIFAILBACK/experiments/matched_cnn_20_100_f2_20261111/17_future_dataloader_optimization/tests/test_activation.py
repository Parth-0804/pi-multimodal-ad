"""Synthetic receipt verification only; never import torch or execute training."""
from copy import deepcopy
import builtins
import hashlib
import json

import pytest

from future_dataloader import activation
from future_dataloader.benchmark import compare_throughput
from future_dataloader.settings import PRESETS


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True))


def case(name, numerical, duration, ids):
    rows = []
    for offset in range(0, len(ids), 8):
        row = {'offset': offset, 'episodes': 8, 'warmup': offset < 8,
               'loader_wait_GPU_quiescent_seconds': 1., 'compute_wall_seconds': 4.,
               'GPU_stream_elapsed_ms': 3500., 'guard_overhead_seconds': .1}
        if numerical:
            proof = {key: 'a' * 64 for key in (
                'labels_sha256', 'loss_sha256', 'logits_sha256', 'unclipped_gradients_sha256',
                'model_sha256', 'optimizer_sha256', 'scheduler_sha256', 'RNG_sha256')}
            proof.update(global_gradient_norm=1., inputs=[
                {'episode_index': eid, 'label': eid % 2, 'tensor_sha256': 'b' * 64, 'is_pinned': True}
                for eid in ids[offset:offset + 8]])
            row['proof'] = proof
        rows.append(row)
    value = {'config': name, 'numerical_proof_pass': numerical,
             'initial_state_sha256': '1' * 64, 'final_state_sha256': '2' * 64,
             'scheduler_boundary_probe_sha256': '3' * 64,
             'measured_episodes': 16, 'measurement_seconds': duration,
             'episodes_per_second': 16 / duration, 'batches': rows,
             'loader_wait_GPU_quiescent_seconds': 2., 'compute_wall_seconds': 8.,
             'guard_overhead_seconds_inside_measurement': .1}
    if numerical and name != '__reference__':
        value['exact_reference_equivalence'] = True
    return value


@pytest.fixture
def measured(tmp_path, monkeypatch):
    repo = tmp_path / 'repo'
    root = repo / 'VIFAILBACK/experiments/study/future'
    folder = root / 'results/benchmark'
    folder.mkdir(parents=True)
    (root / 'source.py').write_text('VERIFIED = True\n')
    (root / 'future_dataloader').mkdir()
    for filename in ('contracts.py', 'loader.py', 'settings.py'):
        (root / 'future_dataloader' / filename).write_text('# synthetic fixture\n')
    source = repo / 'VIFAILBACK/src/synthetic.py'
    source.parent.mkdir(parents=True)
    source.write_text('# synthetic original-source fixture\n')
    monkeypatch.setattr(activation, 'LOCAL_ROOT', root)
    names = ['baseline_w2_p1', 'w4_p1']
    ids = list(range(24))
    configs = {name: PRESETS[name].as_dict() for name in names}
    cpu = {'schema': 1, 'status': 'PASS', 'checked_config_names': names,
           'binding': {'configurations': configs, 'protocol_sha256': activation.PROTOCOL_SHA256,
                       'cohort_sha256': 'c' * 64, 'splits_sha256': 'd' * 64, 'legacy_config_sha256': 'e' * 64,
                       'isolated_source_sha256': {str(path.relative_to(repo)): activation._sha(path)
                                                for path in (root / 'future_dataloader').glob('*.py')},
                       'original_source_sha256': {str(source.relative_to(repo)): activation._sha(source)}}}
    cpu['binding_sha256'] = hashlib.sha256(json.dumps(cpu['binding'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    cpu_path = root / 'results/cpu.json'
    write(cpu_path, cpu)
    cases = {'numerical_reference.json': case('__reference__', True, 20., ids)}
    for name in names:
        cases[f'numerical_{name}.json'] = case(name, True, 20., ids)
    rounds = []
    for r in range(1, 5):
        values = {}
        for name in names:
            value = case(name, False, 20. if name == names[0] else 16., ids)
            values[name] = value
            cases[f'timing_round{r}_{name}.json'] = value
        rounds.append(values)
    for filename, value in cases.items():
        write(folder / filename, value)
    result = {'schema': 1, 'status': 'COMPLETE', 'GPU_measurement_performed': True,
              'numerical_equivalence_pass': True, 'configurations': configs,
              'baseline': names[0], 'options': {'rounds': 4, 'measured_episodes': 16, 'warmup_episodes': 8},
              'round_orders': [names, names[::-1], names, names[::-1]],
              'selected_episode_ids': ids, 'role': 'T', 'seed': 42, 'job_id': 'outer0_inner0',
              'numerical_checks': {name: True for name in names},
              'recommendation': compare_throughput(rounds, names),
              'isolated_source_sha256': {str(path.relative_to(root)): activation._sha(path) for path in root.rglob('*.py')},
              'case_receipts_sha256': {name: activation._sha(folder / name) for name in cases},
              'CPU_contract_receipt': str(cpu_path.relative_to(root.parent)),
              'CPU_contract_receipt_sha256': activation._sha(cpu_path)}
    receipt = folder / 'GPU_BENCHMARK.json'
    write(receipt, result)
    return root, receipt, result


def rewrite_case(receipt, result, name, mutate):
    path = receipt.parent / name
    value = json.loads(path.read_text())
    mutate(value)
    write(path, value)
    result['case_receipts_sha256'][name] = activation._sha(path)
    write(receipt, result)


def test_valid_evidence_recomputes_recommendation_without_torch(measured, monkeypatch):
    _, receipt, _ = measured
    original = builtins.__import__

    def no_torch(name, *args, **kwargs):
        if name == 'torch' or name.startswith('torch.'):
            raise AssertionError('Activation must not import torch')
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', no_torch)
    result, config = activation.checked_recommendation(receipt)
    assert config == PRESETS['w4_p1']
    assert result['recommendation']['comparisons']['w4_p1']['relative_throughput_changes'] == [.25] * 4


@pytest.mark.parametrize('field,value', [
    ('status', 'PENDING'), ('GPU_measurement_performed', False),
    ('numerical_equivalence_pass', False), ('numerical_checks', {'baseline_w2_p1': True}),
    ('baseline', 'w4_p1'), ('role', 'V'), ('seed', 123), ('job_id', 'outer0_final'),
    ('schema', 2), ('selected_episode_ids', list(range(23))),
])
def test_unmeasured_or_wrong_contract_is_rejected(measured, field, value):
    _, receipt, result = measured
    result[field] = value
    write(receipt, result)
    with pytest.raises(ValueError):
        activation.checked_recommendation(receipt)


@pytest.mark.parametrize('mutation', [
    lambda r: r['options'].update(rounds=3),
    lambda r: r['options'].update(measured_episodes=24),
    lambda r: r['options'].update(warmup_episodes=16),
    lambda r: r['round_orders'].__setitem__(1, r['round_orders'][0]),
    lambda r: r['round_orders'].pop(),
    lambda r: r['case_receipts_sha256'].pop('timing_round4_w4_p1.json'),
    lambda r: r['case_receipts_sha256'].pop('numerical_reference.json'),
    lambda r: r['recommendation']['comparisons']['w4_p1'].update(relative_throughput_changes=[.9] * 4),
    lambda r: r['recommendation']['comparisons']['w4_p1'].update(median_relative_change=.9),
    lambda r: r['configurations']['w4_p1'].update(prefetch_factor=2),
])
def test_incomplete_balancing_or_forged_summary_is_rejected(measured, mutation):
    _, receipt, result = measured
    mutation(result)
    write(receipt, result)
    with pytest.raises(ValueError):
        activation.checked_recommendation(receipt)


@pytest.mark.parametrize('mutation', [
    lambda c: c.update(episodes_per_second=10.),
    lambda c: c.update(measurement_seconds=-1.),
    lambda c: c.update(episodes_per_second=float('nan')),
    lambda c: c.update(final_state_sha256='4' * 64),
    lambda c: c.update(config='baseline_w2_p1'),
    lambda c: c.update(measured_episodes=8),
    lambda c: c['batches'].pop(),
    lambda c: c['batches'][1].update(offset=16),
    lambda c: c['batches'][1].update(proof={}),
    lambda c: c['batches'][1].update(compute_wall_seconds=100.),
])
def test_rehashed_but_inconsistent_timing_evidence_is_rejected(measured, mutation):
    _, receipt, result = measured
    rewrite_case(receipt, result, 'timing_round2_w4_p1.json', mutation)
    with pytest.raises(ValueError):
        activation.checked_recommendation(receipt)


def test_one_round_without_required_gain_cannot_be_hidden_by_claim(measured):
    _, receipt, result = measured
    rewrite_case(receipt, result, 'timing_round2_w4_p1.json',
                 lambda c: c.update(measurement_seconds=20., episodes_per_second=.8))
    with pytest.raises(ValueError, match='recommendation'):
        activation.checked_recommendation(receipt)


@pytest.mark.parametrize('mutation', [
    lambda c: c.update(exact_reference_equivalence=False),
    lambda c: c['batches'][0]['proof'].pop('RNG_sha256'),
    lambda c: c['batches'][0]['proof']['inputs'][0].update(label=7),
    lambda c: c['batches'][0]['proof']['inputs'][0].update(is_pinned=False),
    lambda c: c['batches'][0]['proof']['inputs'][0].update(tensor_sha256='c' * 64),
])
def test_incomplete_or_different_numerical_proof_is_rejected(measured, mutation):
    _, receipt, result = measured
    rewrite_case(receipt, result, 'numerical_w4_p1.json', mutation)
    with pytest.raises(ValueError):
        activation.checked_recommendation(receipt)


@pytest.mark.parametrize('target', ['source', 'timing', 'cpu'])
def test_stale_source_and_tampered_receipts_are_rejected(measured, target):
    root, receipt, _ = measured
    path = {'source': root / 'source.py', 'timing': receipt.parent / 'timing_round1_w4_p1.json',
            'cpu': root / 'results/cpu.json'}[target]
    path.write_text(path.read_text() + '\n# changed\n')
    with pytest.raises(ValueError):
        activation.checked_recommendation(receipt)


def test_duplicate_json_keys_cannot_hide_status(measured):
    _, receipt, _ = measured
    text = receipt.read_text()
    receipt.write_text(text.replace('"status": "COMPLETE"', '"status": "PENDING", "status": "COMPLETE"'))
    with pytest.raises(ValueError, match='Duplicate'):
        activation.checked_recommendation(receipt)


def test_malformed_nested_evidence_fails_closed(measured):
    _, receipt, result = measured
    result['recommendation'] = []
    write(receipt, result)
    with pytest.raises(ValueError, match='Malformed'):
        activation.checked_recommendation(receipt)


@pytest.mark.parametrize('mutation', [
    lambda c: c.update(status='PENDING'),
    lambda c: c['binding'].update(original_source_sha256={}),
    lambda c: c['binding'].update(isolated_source_sha256={}),
    lambda c: c['binding'].update(protocol_sha256='f' * 64),
])
def test_rehashed_but_incomplete_cpu_evidence_is_rejected(measured, mutation):
    root, receipt, result = measured
    path = root / 'results/cpu.json'
    cpu = json.loads(path.read_text())
    mutation(cpu)
    cpu['binding_sha256'] = hashlib.sha256(json.dumps(cpu['binding'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    write(path, cpu)
    result['CPU_contract_receipt_sha256'] = activation._sha(path)
    write(receipt, result)
    with pytest.raises(ValueError):
        activation.checked_recommendation(receipt)


def test_changed_original_dependency_invalidates_cpu_binding(measured):
    root, receipt, _ = measured
    (root.parents[3] / 'VIFAILBACK/src/synthetic.py').write_text('# changed dependency\n')
    with pytest.raises(ValueError, match='original-source binding is stale'):
        activation.checked_recommendation(receipt)


def test_export_rechecks_admission_and_does_not_overwrite(measured, monkeypatch):
    root, receipt, _ = measured
    out = root / 'export'
    out.mkdir()
    monkeypatch.setattr(activation, 'inspect_admission', lambda **_: {'ready': False, 'reasons': ['protected lane active']})
    with pytest.raises(ValueError, match='Protected queue'):
        activation.export_config(receipt, out)
    assert not list(out.iterdir())
    monkeypatch.setattr(activation, 'inspect_admission', lambda **_: {'ready': True})
    result = activation.export_config(receipt, out)
    assert result['production_training_started'] is False
    assert result['existing_controllers_modified'] is False
    with pytest.raises(FileExistsError):
        activation.export_config(receipt, out)
