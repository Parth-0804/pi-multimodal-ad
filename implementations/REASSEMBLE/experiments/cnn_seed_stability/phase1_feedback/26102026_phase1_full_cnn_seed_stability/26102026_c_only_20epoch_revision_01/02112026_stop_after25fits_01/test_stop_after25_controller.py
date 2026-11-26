import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest

spec = importlib.util.spec_from_file_location('cap', Path(__file__).with_name('stop_after25_controller.py'))
cap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cap)


def test_only_first_complete_seed_can_be_scheduled():
    plan = [(s, {'job_index': j}) for s in [42, 123, 20261023] for j in range(25)]
    allowed = cap.allowed_schedule(plan, {'allowed_seed': 42, 'stop_after_completed_fits': 25})
    assert len(allowed) == 25
    assert {s for s, _ in allowed} == {42}
    assert allowed[-1][1]['job_index'] == 24


def test_missing_or_duplicate_jobs_are_not_a_complete_seed():
    plan = [(42, {'job_index': j}) for j in range(24)]
    request = {'allowed_seed': 42, 'stop_after_completed_fits': 25}
    with pytest.raises(AssertionError):
        cap.allowed_schedule(plan, request)
    with pytest.raises(AssertionError):
        cap.allowed_schedule(plan + [(42, {'job_index': 23})], request)


def test_partial_epoch_fit_is_not_counted_as_complete(tmp_path):
    row = {'status': 'COMPLETE', 'seed': 42, 'job_index': 0, 'executed_epochs': 19}
    with pytest.raises(AssertionError, match='INCOMPLETE_FIT'):
        cap.verify_receipt(row, 42, {'job_index': 0}, 'sha', tmp_path, lambda p: '')


def test_completed_receipt_must_match_model_and_prediction_hashes(tmp_path):
    row = {'status': 'COMPLETE', 'seed': 42, 'job_index': 0, 'executed_epochs': 20,
           'revision_configuration_sha256': 'config', 'predictions_sha256': 'p',
           'selected_model_sha256': 'm'}
    hashes = {'PHASE1_PREDICTIONS.json': 'p', 'PHASE1_BEST_MODEL.pt': 'm'}
    cap.verify_receipt(row, 42, {'job_index': 0}, 'config', tmp_path, lambda p: hashes[p.name])
    hashes['PHASE1_BEST_MODEL.pt'] = 'corrupted'
    with pytest.raises(AssertionError):
        cap.verify_receipt(row, 42, {'job_index': 0}, 'config', tmp_path, lambda p: hashes[p.name])


def test_unrelated_stop_request_cannot_be_overwritten(tmp_path):
    path = tmp_path/'STOP_AFTER_EPOCH.json'
    cap.exclusive_stop(path, {'request_id': 'existing'})
    before = path.read_bytes()
    with pytest.raises(AssertionError):
        cap.exclusive_stop(path, {'request_id': 'different'})
    assert path.read_bytes() == before
    cap.exclusive_stop(path, {'request_id': 'existing'})
    assert json.loads(path.read_text()) == {'request_id': 'existing'}


def test_pid_reuse_never_selects_a_process(monkeypatch):
    class Process:
        def is_running(self): return True
        def status(self): return 'running'
        def create_time(self): return 200
    monkeypatch.setattr(cap.psutil, 'Process', lambda pid: Process())
    assert not cap.live({'pid': 5, 'create_time': 100})
    with pytest.raises(AssertionError, match='PID_REUSED'):
        cap.checked_controller({'pid': 5, 'create_time': 100}, Path('/tmp/controller.py'))


def test_unrelated_controller_is_never_selected(monkeypatch):
    class Process:
        def cmdline(self): return ['python', '/tmp/unrelated.py']
    identity = {'pid': 5, 'create_time': 100, 'command': ['python', '/tmp/unrelated.py']}
    monkeypatch.setattr(cap, 'live', lambda value: True)
    monkeypatch.setattr(cap.psutil, 'Process', lambda pid: Process())
    with pytest.raises(AssertionError, match='WRONG_CONTROLLER'):
        cap.checked_controller(identity, Path('/tmp/real_controller.py'))


def test_controller_handoff_leaves_separate_session_child_alive(tmp_path):
    """Exercise real processes without touching the GPU or scientific job."""
    marker = tmp_path/'child_pid.json'
    script = tmp_path/'synthetic_controller.py'
    script.write_text(
        'import subprocess,sys,time,json\n'
        'from pathlib import Path\n'
        'p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(20)"],'
        'start_new_session=True)\n'
        'Path(sys.argv[1]).write_text(json.dumps(p.pid))\n'
        'p.wait()\n')
    parent = subprocess.Popen([sys.executable, str(script), str(marker)])
    child = None
    try:
        for _ in range(100):
            if marker.exists():
                break
            time.sleep(.02)
        child = cap.process_identity(json.loads(marker.read_text()))
        identity = cap.process_identity(parent.pid)
        controller = cap.checked_controller(identity, script)
        cap.release_controller(controller, identity)
        assert cap.live(child), 'Synthetic training child was interrupted'
    finally:
        if parent.poll() is None:
            parent.terminate()
        parent.wait(timeout=5)
        if child and cap.live(child):
            cap.psutil.Process(child['pid']).terminate()
