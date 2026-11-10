"""New-run-only bookkeeping and shared immutable inputs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone
import numpy as np
from reassemble.section1_features import sha

CONFIG = Path('configs/reassemble/additional_improvements/execution.json')
TASKS = ['01_temporal_visual', '02_patchtst_training_budget', '03_static_anchored_adaptation', '04_corruption_training']

def read(path):
    return json.loads(Path(path).read_text())

def config():
    return read(CONFIG)

def write(path, value, replace=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not replace:
        assert read(path) == value, f'Immutable result already exists: {path}'
        return
    tmp = path.with_suffix(path.suffix + f'.writing.{os.getpid()}')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)

def storage(large=False):
    c = config()
    free = shutil.disk_usage(c['run_dir']).free / 2**30
    minimum = c['large_cache_minimum_free_GiB'] if large else c['minimum_free_GiB']
    if free < minimum:
        raise RuntimeError(f'STORAGE BLOCKER: {free:.2f} GiB free < {minimum}; no deletion authorized')
    return free

def progress(task, stage, state='running'):
    c = config(); root = Path(c['run_dir']); now = datetime.now(timezone.utc).isoformat()
    record = dict(utc=now, task=task, stage=stage, state=state, pid=os.getpid())
    write(root / TASKS[task-1] / 'status.json', record, replace=True)
    states = {p: read(root / p / 'status.json') for p in TASKS}
    write(root / 'status.json', dict(utc=now, label=c['status_label'], tasks=states), replace=True)
    (root / 'reports/CONTINUATION.md').write_text(
        '# Additional exploratory experiments — continuation\n\n'
        f'Run: `{root}`. Config: `{CONFIG}`.\n\n'
        'Original evidence and external Reasoning Record are immutable. Check running processes before resuming.\n'
        'Use the same source commit/config; existing per-fit checkpoints are resumable. Never overwrite completed fits.\n\n'
        + '\n'.join(f'- {k}: **{v["state"]}** — {v["stage"]}' for k,v in states.items())
        + '\n\nCommands and provenance: `00_protocol_and_preservation/EXPLORATORY_PROTOCOL.md`.\n'
        'No extra budgets, winner combinations, audio, or OOD experiments.\n')
    print(now, task, stage, flush=True)

def identity(path):
    p = Path(path)
    return dict(path=str(p), sha256=sha(p), bytes=p.stat().st_size)

def setup():
    import torch
    import cv2
    c=config()
    torch.set_num_threads(c['threads']); cv2.setNumThreads(1)
    torch.use_deterministic_algorithms(True); torch.backends.cudnn.benchmark=False
    return c

def inputs():
    from reassemble.section1_models import load_features, verify_splits
    c=config(); base=read(c['section1_config']); frame, arrays=load_features(base)
    splits=read(base['splits']); verify_splits(frame, splits)
    return c, base, frame, arrays, splits
