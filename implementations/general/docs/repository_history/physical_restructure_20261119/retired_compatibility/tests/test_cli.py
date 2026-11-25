"""Safe old/new CLI equivalence: only argument parsing and passive module execution."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import os
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
ROWS = list(csv.DictReader((ROOT / 'docs/repository_restructure/path_mapping.csv').open()))
SCRIPTS = [r for r in ROWS if r['status'] == 'moved' and r['old_path'].startswith('scripts/')]


def invoke(args, cwd=ROOT):
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    env.update(OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
               PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable, '-B', *args], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=60)


def record(row, old, new):
    directory = os.environ.get('COMPATIBILITY_AUDIT_DIRECTORY')
    if directory:
        out = Path(directory) / 'cli_results'
        out.mkdir(exist_ok=True)
        name = row['old_path'].replace('/', '_')
        (out / (name + '.json')).write_text(json.dumps({
            'legacy': row['old_path'], 'canonical': row['new_path'],
            'arguments': ['--help'], 'legacy_exit': old.returncode, 'canonical_exit': new.returncode,
            'stdout_equal': old.stdout == new.stdout, 'stderr_equal': old.stderr == new.stderr,
            'stdout_sha256': hashlib.sha256(new.stdout.encode()).hexdigest(),
            'stderr_sha256': hashlib.sha256(new.stderr.encode()).hexdigest(),
        }, indent=2))
        (out / (name + '.stdout.log')).write_text(new.stdout)
        (out / (name + '.stderr.log')).write_text(new.stderr)


@pytest.mark.parametrize('row', SCRIPTS, ids=lambda r: r['old_path'])
def test_every_old_new_script_help_has_equal_output_and_exit(row):
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(invoke, [row['old_path'], '--help'])
        b = pool.submit(invoke, [row['new_path'], '--help'])
        old, new = a.result(), b.result()
    record(row, old, new)
    assert old.returncode == new.returncode == 0, (old.stderr, new.stderr)
    assert old.stdout == new.stdout
    assert old.stderr == new.stderr


def test_legacy_wrapper_preserves_nonzero_argument_error_exit():
    old = invoke(['scripts/training/train_patchtst.py', '--compatibility-invalid-option'])
    new = invoke(['scripts/phm2026/training/train_patchtst.py', '--compatibility-invalid-option'])
    assert old.returncode == new.returncode == 2
    assert old.stdout == new.stdout
    assert old.stderr == new.stderr


@pytest.mark.parametrize('prefix', ['scripts/training', 'scripts/phm2026/training'])
def test_absolute_cli_help_outside_repository(prefix, tmp_path):
    result = invoke([str(ROOT / prefix / 'train_patchtst.py'), '--help'], cwd=tmp_path)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('old,new', [
    ('pi_multimodal_ad.cli', 'phm2026.cli'),
    ('pi_multimodal_ad.models.rtdetr_regression', 'phm2026.models.rtdetr.regression'),
    ('scripts.training.train_patchtst', 'scripts.phm2026.training.train_patchtst'),
])
def test_representative_legacy_and_new_module_execution(old, new):
    # The first two are historically passive modules; --help launches no workflow.
    a, b = invoke(['-m', old, '--help']), invoke(['-m', new, '--help'])
    assert a.returncode == b.returncode == 0, (a.stderr, b.stderr)
    assert a.stdout == b.stdout
    assert a.stderr == b.stderr
