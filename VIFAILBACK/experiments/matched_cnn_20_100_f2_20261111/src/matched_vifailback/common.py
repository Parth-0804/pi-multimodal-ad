"""Paths and atomic journals restricted to this prospectively frozen study."""
from __future__ import annotations
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

STUDY = Path(__file__).resolve().parents[2]
PROJECT = STUDY.parents[1]
REPO = PROJECT.parent
for _path in (PROJECT / 'src', REPO / 'src'):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
PROTOCOL_SHA256 = '71cbb3b01b0adb47d2e055bf79391276f1f2f3a9dd339e5b0f07013932caa9c5'
ARM_DIRECTORIES = {
    'FROZEN20': '03_frozen20', 'FULL20': '04_full20',
    'FROZEN100': '05_frozen100', 'FULL100': '06_full100',
    'DONOR20': '07_reassemble_donor_transfer/DONOR20',
    'DONOR100': '07_reassemble_donor_transfer/DONOR100',
}


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def relative(path):
    return os.path.relpath(Path(path).resolve(), REPO)


def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else REPO / p


def destination(path):
    path = Path(path).resolve()
    if path != STUDY and STUDY not in path.parents:
        raise ValueError(f'Write outside isolated study refused: {path}')
    return path


def _json_default(obj):
    if isinstance(obj, Path):
        return relative(obj)
    if hasattr(obj, 'tolist'):
        return obj.tolist()
    if hasattr(obj, 'item'):
        return obj.item()
    raise TypeError(type(obj).__name__)


def write_json(path, value):
    """Atomic replace of a new-study journal; never a historical artifact."""
    path = destination(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.writing.{os.getpid()}')
    with temp.open('w') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, default=_json_default, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return path


def immutable_json(path, value):
    path = destination(path)
    if path.exists():
        if read_json(path) != json.loads(json.dumps(value, default=_json_default, allow_nan=False)):
            raise ValueError(f'Immutable configuration changed: {relative(path)}')
        return path
    return write_json(path, value)


def protocol():
    path = STUDY / '01_protocol_and_source_evidence/protocol.json'
    if sha256(path) != PROTOCOL_SHA256:
        raise ValueError('Frozen protocol SHA-256 mismatch')
    return read_json(path)


def legacy_config():
    return read_json(STUDY / '01_protocol_and_source_evidence/legacy_config_snapshot.json')


def fit_root(condition, seed, job_id):
    if condition not in ARM_DIRECTORIES:
        raise ValueError(f'Unknown condition {condition}')
    if int(seed) not in protocol()['seeds'] or not str(job_id).replace('_', '').isalnum():
        raise ValueError('Unexpected seed or job identifier')
    return destination(STUDY / ARM_DIRECTORIES[condition] / f'seed{int(seed)}' / str(job_id))


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), default=_json_default, allow_nan=False).encode()).hexdigest()


def code_identity():
    paths = sorted((STUDY / 'src').rglob('*.py')) + sorted((STUDY / 'scripts').glob('*.py'))
    return {relative(p): sha256(p) for p in paths}


def git_commit():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()


@contextlib.contextmanager
def exclusive_lock(path):
    path = destination(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f'Another study process holds {relative(path)}') from exc
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
