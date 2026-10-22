"""Study-only writes, explicit budgets, identities and admission. No scheduler."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import time

STUDY = Path(__file__).resolve().parents[1]
REPO = STUDY.parents[1]
RUN = STUDY / 'results/run_01'
CONDITIONS = ('cnn_only', 'cnn_plus_encoder')


def read(path):
    return json.loads(Path(path).read_text())


def config():
    return read(STUDY / 'config.json')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(2**20), b''):
            h.update(b)
    return h.hexdigest()


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def local(path):
    p = Path(path)
    if not p.resolve().is_relative_to(STUDY.resolve()):
        raise ValueError('WRITE_OUTSIDE_STUDY ' + str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write(path, value):
    p = local(path)
    tmp = local(p.with_name(p.name + '.writing'))
    with tmp.open('w') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


def write_text(path, value):
    p = local(path)
    tmp = local(p.with_name(p.name + '.writing'))
    tmp.write_text(value)
    os.replace(tmp, p)


def save_csv(path, frame):
    p = local(path)
    tmp = local(p.with_name(p.name + '.writing'))
    frame.to_csv(tmp, index=False, float_format='%.17g')
    os.replace(tmp, p)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def elapsed():
    return (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(config()['started_utc'])).total_seconds()


def budget(extra=0, scientific=True):
    c = config()
    used = sum(p.stat().st_size for p in STUDY.rglob('*') if p.is_file() and not p.is_symlink())
    free = shutil.disk_usage(STUDY).free
    rss = {line.split(':')[0]: int(line.split()[1])*1024
           for line in Path('/proc/self/status').read_text().splitlines() if line.startswith(('VmRSS:', 'VmHWM:'))}
    if used + extra > c['new_storage_cap_bytes'] or free - extra < c['minimum_free_bytes']:
        raise RuntimeError('STORAGE_RESERVE_BLOCKER')
    if rss.get('VmRSS', 0) > c['host_memory_ceiling_bytes']:
        raise RuntimeError('HOST_MEMORY_BLOCKER')
    if scientific and elapsed() > c['wall_seconds'] - c['report_reserve_seconds']:
        raise RuntimeError('DEADLINE_REPORT_RESERVE')
    return dict(study_bytes=used, free_bytes=free, elapsed_seconds=elapsed(), **rss)


def event(status, **kwargs):
    p = RUN / 'progress.json'
    d = read(p) if p.exists() else {'attempts': {}, 'calibrator_fits': 0, 'preflight_steps': 0}
    d.update(status=status, updated_utc=utc(), elapsed_seconds=elapsed(), **kwargs)
    write(p, d)
    with local(RUN / 'logs/events.jsonl').open('a') as f:
        f.write(json.dumps(dict(utc=utc(), status=status, **kwargs)) + '\n')
    print(status, json.dumps(kwargs)[:400], flush=True)


def consume(kind, fit_id):
    caps = {'visual': 'full_visual_fit_cap', 'sensor': 'raw_sensor_fit_cap', 'stacker': 'stacker_fit_cap'}
    d = read(RUN / 'progress.json')
    records = d.setdefault('attempts', {})
    attempts = records.setdefault(kind, [])
    if len(attempts) >= config()[caps[kind]]:
        raise RuntimeError('FIT_CAP ' + kind)
    if sum(x['fit_id'] == fit_id for x in attempts) >= 1 + config()['technical_repair_cap_per_stage']:
        raise RuntimeError('REPAIR_CAP ' + fit_id)
    attempts.append({'fit_id': fit_id, 'started_utc': utc()})
    write(RUN / 'progress.json', d)


def prior():
    return REPO / config()['prior_run']


def command(args):
    r = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return {'returncode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}


def readiness():
    """No CUDA initialization. A process owns the device even during idle kernels."""
    c = config()
    g = command(['nvidia-smi', '--query-gpu=index,uuid,name,memory.used,utilization.gpu', '--format=csv,noheader,nounits'])
    a = command(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid,process_name,used_memory', '--format=csv,noheader,nounits'])
    state = read(prior() / 'progress.json') if (prior() / 'progress.json').exists() else {}
    # /proc command line is read only for public scientific entrypoint identity;
    # never dump it or inspect any process environment.
    priority = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name) == os.getpid():
            continue
        try:
            if (p / 'comm').read_text().strip() not in ('python', 'python3', 'python3.12', 'bash'):
                continue
            cmd = (p / 'cmdline').read_bytes().replace(b'\0', b' ')
            if b'visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames' in cmd and (b'run_study.py' in cmd or b'study.sh' in cmd):
                priority.append({'pid': int(p.name), 'comm': (p / 'comm').read_text().strip(), 'identity': 'priority visual-backbone study'})
        except (PermissionError, FileNotFoundError, ProcessLookupError):
            pass
    active = [s for s in a['stdout'].splitlines() if c['gpu_uuid'] in s and f', {os.getpid()},' not in s]
    available = (g['returncode'] == a['returncode'] == 0 and c['gpu_uuid'] in g['stdout'] and not active and not priority)
    # The first observed priority PID also blocks if still a live non-zombie.
    pstat = Path('/proc') / str(c['priority_pid_observed']) / 'stat'
    observed_alive = pstat.exists() and pstat.read_text().split(') ', 1)[1].split()[0] != 'Z'
    available = available and not observed_alive
    d = dict(checked_utc=utc(), available=available, gpu=g, applications=a,
             priority_processes=priority, observed_priority_pid_alive=observed_alive,
             priority_status=state.get('status'), priority_active_job=state.get('active_job'),
             priority_full_fits_started=state.get('full_visual_fits_started'),
             priority_full_fits_completed=state.get('full_visual_fits_completed'))
    write(RUN / 'checks/readiness.json', d)
    return d


def code_identity():
    return {str(p.relative_to(STUDY)): sha(p) for p in sorted(STUDY.glob('code/*.py'))} | {'run_experiment.py': sha(STUDY / 'run_experiment.py')}
