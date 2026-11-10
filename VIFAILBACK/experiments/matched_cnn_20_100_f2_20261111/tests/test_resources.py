"""Resource refusal and schedule guards, using tiny synthetic states only."""
from types import SimpleNamespace
import pytest
from matched_vifailback import common, controller, resources


def test_writes_cannot_escape_study():
    with pytest.raises(ValueError, match='outside isolated'):
        common.destination(common.PROJECT / '01_original_dataset' / 'not_written.json')
    with pytest.raises(ValueError):
        common.fit_root('FULL20', 42, '../../escape')


def test_seed_and_condition_are_predeclared():
    with pytest.raises(ValueError):
        common.fit_root('NEW_HPO', 42, 'outer0_final')
    with pytest.raises(ValueError):
        common.fit_root('FULL20', 100, 'outer0_final')


def test_immutable_configuration_cannot_be_replaced(tmp_path, monkeypatch):
    monkeypatch.setattr(common, 'STUDY', tmp_path)
    path = tmp_path / 'configuration.json'
    common.immutable_json(path, {'epochs': 20})
    common.immutable_json(path, {'epochs': 20})
    with pytest.raises(ValueError, match='Immutable'):
        common.immutable_json(path, {'epochs': 2})
    assert common.read_json(path) == {'epochs': 20}


def test_no_unadmitted_seeds_or_extra100_scope(monkeypatch):
    monkeypatch.setattr(controller, 'admission', lambda: {'admitted_twenty_epoch_seeds': [42]})
    gpu = controller.schedule('gpu'); cpu = controller.schedule('cpu')
    assert len(gpu) == 13 and len(cpu) == 26
    assert gpu[0] == ('FULL100', 42, 'outer0_inner0')
    assert len([x for x in gpu if x[0].endswith('100')]) == 1
    assert len({job for condition, seed, job in gpu if condition == 'FULL20'}) == 12
    assert {seed for _, seed, _ in cpu + gpu} == {42}


def test_disk_gate_reserves_space_before_write(monkeypatch):
    monkeypatch.setattr(resources.shutil, 'disk_usage', lambda p: SimpleNamespace(free=21 * resources.GIB))
    monkeypatch.setattr(resources, 'source_processes', lambda: [])
    assert resources.gate(extra_bytes=resources.GIB, require_gpu=False)['ready']
    result = resources.gate(extra_bytes=resources.GIB + 1, require_gpu=False)
    assert result['reasons'] == ['DISK_RESERVE']


def test_competing_source_and_gpu_jobs_refuse_admission(monkeypatch):
    monkeypatch.setattr(resources.shutil, 'disk_usage', lambda p: SimpleNamespace(free=100 * resources.GIB))
    monkeypatch.setattr(resources, 'source_processes', lambda: [{'pid': 101}])
    monkeypatch.setattr(resources, 'gpu_snapshot', lambda: {'devices': [{}], 'other_compute_pids': [102]})
    state = resources.gate()
    assert not state['ready']
    assert state['reasons'] == ['OTHER_GPU_WORK', 'SOURCE_CONTROLLER_ACTIVE']


def test_failed_gradient_benchmark_cannot_admit_training():
    with pytest.raises(ValueError, match='has not passed'):
        resources.prospective_admission({}, {'status': 'FAIL'})


def test_worker_identity_checks_creation_time():
    import os
    import psutil
    state = {'pid': os.getpid(), 'create_time': psutil.Process().create_time()}
    assert controller.worker_alive(state)
    assert not controller.worker_alive(dict(state, create_time=state['create_time'] + 1))
    assert not controller.worker_alive({})


def test_input_verification_failure_is_terminal_status(tmp_path, monkeypatch):
    import matched_vifailback.data as data
    monkeypatch.setattr(common, 'STUDY', tmp_path)
    monkeypatch.setattr(controller, 'RUNTIME', tmp_path)
    monkeypatch.setattr(controller, 'check_frozen_code', lambda: None)
    monkeypatch.setattr(controller, 'schedule', lambda lane: [('FROZEN100', 42, 'outer0_inner0')])
    def fail(**kwargs):
        raise ValueError('synthetic identity mismatch')
    monkeypatch.setattr(data, 'load_context', fail)
    with pytest.raises(ValueError, match='identity mismatch'):
        controller.run('cpu')
    result = common.read_json(tmp_path / 'CPU_CONTROLLER_STATUS.json')
    assert result['stage'] == 'FAILED' and 'identity mismatch' in result['error']
