"""Non-destructive orchestration utilities for the final REASSEMBLE phases."""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import hashlib


def config():
    return json.loads(Path('configs/reassemble/completion.json').read_text())


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n')


def storage():
    free = shutil.disk_usage('.').free / 2**30
    if free < 20:
        raise RuntimeError(f'STORAGE BLOCK: {free:.2f} GiB; stop new jobs')
    return free


def seed_for(*values):
    return int.from_bytes(hashlib.sha256('|'.join(map(str, values)).encode()).digest()[:8], 'little')


def progress(stage):
    now = datetime.now(timezone.utc).isoformat()
    Path('docs/reassemble/AUTONOMOUS_CONTINUATION.md').write_text(
        '# Autonomous REASSEMBLE completion\n\n' + now + '\n\nCurrent stage: **' + stage + '**.\n\n'
        'All remaining non-destructive phases are explicitly authorized by the user; no routine approval pause.\n'
        'Configuration and unique phase paths: `configs/reassemble/completion.json`.\n'
        'Corruption specification: `docs/reassemble/SECTION_3_CORRUPTION_PROTOCOL.md`.\n'
        'Preserve all Section 1/1B/2 evidence and their continuation files.\n'
        'Inspect running jobs and per-phase execution logs before resuming; numerical stages checkpoint completed recordings/folds.\n'
        'Remaining order: Section 3 → modality dropout → audio gate → efficiency/object feasibility → final package and audit.\n'
        'Never delete raw or historical files. Stop new jobs below 20 GiB.\n')
    print(now, stage, flush=True)


def claim(path):
    import fcntl
    stream=Path(str(path)+'.lock').open('a')
    try:fcntl.flock(stream,fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        stream.close();return None
    return stream
