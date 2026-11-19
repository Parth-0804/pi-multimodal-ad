"""Synthetic regressions for the Intel structural audit; no raw data fixtures."""
import importlib.util
from pathlib import Path
import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location('intel_foundations', Path(__file__).resolve().parents[2] / 'scripts/intel_welding/04_foundations.py')
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def test_hash_includes_bytes_after_old_prefix_limit(tmp_path):
    a, b = tmp_path / 'a', tmp_path / 'b'
    prefix = b'x' * 4_000_000
    a.write_bytes(prefix + b'a')
    b.write_bytes(prefix + b'b')
    assert audit.digest(a) != audit.digest(b)


def test_timestamp_midnight_and_duplicate_detection():
    df = pd.DataFrame({'Date': ['1/1/2026', '1/2/2026', '1/2/2026'],
                       'Time': ['23:59:59.900', '00:00:00.000', '00:00:00.100']})
    t = audit.timing(df)
    assert t['timestamp_valid']
    assert t['sensor_seconds'] == pytest.approx(.2)
    assert t['sensor_rate_hz'] == pytest.approx(10)
    df.loc[2, 'Time'] = '00:00:00.000'
    assert not audit.timing(df)['timestamp_valid']


def test_path_escape_refused(tmp_path):
    with pytest.raises(ValueError):
        audit.checked_path(tmp_path, '../outside')


def test_missing_modalities_explicit(tmp_path):
    row = {'DIRECTORY': 'synthetic', 'SUBDIRS': 'synthetic/sample', 'CATEGORY': 'Good'}
    result, files = audit.inspect_sample(tmp_path, row)
    assert not result['complete_present']
    assert not result['complete_readable']
    assert result['audio_error'] == 'missing'
    assert files == []


def test_duplicate_leakage_checks_cv_and_test_images():
    inv = pd.DataFrame({'SUBDIRS': ['a/1', 'b/1', 'c/1'], 'session_id': ['a', 'b', 'c'],
                        'CATEGORY': ['Good', 'Defect', 'Good'], 'complete_readable': [True]*3})
    files = pd.DataFrame({'modality': ['image']*3, 'sha256': ['same']*3,
                         'session_id': ['a', 'b', 'c'], 'path': ['a/i', 'b/i', 'c/i']})
    split = {'development_sessions': ['a', 'b'], 'final_test_sessions': ['c'],
             'cv_folds': [{'fold': 0, 'train_sessions': ['a'], 'val_sessions': ['b']}]}
    checks = audit.audit_split(inv, files, split)
    assert checks['dev_test_session_disjoint']
    assert checks['cross_partition_duplicate_groups'][0]['dev_test']
    assert checks['cross_partition_duplicate_groups'][0]['cv_folds'] == [0]
    assert not checks['holdout_valid']


def test_output_refuses_overwrite(tmp_path):
    p = tmp_path / 'result.json'
    audit.save_json(p, {'first': True})
    with pytest.raises(FileExistsError):
        audit.save_json(p, {'second': True})
