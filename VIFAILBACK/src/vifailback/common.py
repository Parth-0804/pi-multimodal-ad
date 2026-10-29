"""Portable paths, immutable source identities and new-run state journals."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import importlib.metadata

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parent


def config(path=None):
    return json.loads(Path(path or PROJECT / 'configs/experiment.json').read_text())


def resolve(path):
    path = Path(path)
    return path if path.is_absolute() else REPO / path


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    """Atomic live journal update, limited to the newly authorized domain root."""
    path = Path(path)
    assert path.resolve().is_relative_to(PROJECT.resolve()), path
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.writing.{os.getpid()}')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def csv_write(path, rows):
    path = Path(path)
    assert path.resolve().is_relative_to(PROJECT.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', newline='') as stream:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def core(c):
    rows = list(csv.DictReader(resolve(c['core_manifest']).open(newline='')))
    for row in rows:
        for key in ('episode_index', 'canonical_task_id', 'label', 'frame_count'):
            row[key] = int(row[key])
    assert len(rows) == 4384 and Counter(row['label'] for row in rows) == {1: 3755, 0: 629}
    assert len({row['canonical_task_id'] for row in rows}) == 99
    assert not any(row['canonical_task_id'] == 55 for row in rows)
    return rows


def disk_reserve(c, future_bytes=0):
    free = shutil.disk_usage(PROJECT).free
    if free - future_bytes < c['minimum_free_GiB'] * 1024**3:
        raise RuntimeError('STORAGE_RESERVE_BLOCKER')
    return free


def video_path(c, relative):
    old = resolve(c['historical_root']) / 'source_evidence/vifailback' / relative
    return old if old.is_file() else resolve(c['video_cache']) / relative


def event(c, stage, **extra):
    path = PROJECT / 'logs' / c['run_id'] / 'events.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {'utc': utc(), 'stage': stage, **extra}
    with path.open('a') as stream:
        stream.write(json.dumps(row, allow_nan=False) + '\n')
        stream.flush()
    print(json.dumps(row), flush=True)


def code_identity():
    return {str(p.relative_to(REPO)):sha(p) for folder in [PROJECT/'src',PROJECT/'scripts',PROJECT/'configs']
            for p in sorted(folder.rglob('*')) if p.is_file() and p.suffix in ['.py','.json']}


def provenance(c):
    from .reference import identities
    packages={}
    for package in ['torch','transformers','numpy','scipy','scikit-learn','pyarrow','opencv-python','Pillow','requests','pytest']:
        try:packages[package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:packages[package]='not installed as named'
    return {'utc':utc(),'configuration':c,'command':sys.argv,'python':sys.version,'packages':packages,
            'git_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
            'git_dirty':bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=REPO,text=True)),
            'implementation':code_identity(),'reused_source':identities(),
            'warnings':['Task independence only; session/operator identities unknown',
                        'Native intervention exclusions do not establish absence of incidental humans',
                        'Relative converted clock alignment is not independently measured hardware synchronization']}
