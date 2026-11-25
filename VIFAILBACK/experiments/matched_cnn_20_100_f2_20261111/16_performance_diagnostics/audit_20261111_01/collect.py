"""Read-only six-minute audit. No torch import, profiler, signal, or training call."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

import psutil

OUT = Path(__file__).resolve().parent
STUDY = OUT.parents[1]
REPO = STUDY.parents[2]
SECONDS = 360
INTERVAL = 2
STATUS = STUDY / '13_reproducibility/runtime/GPU_CONTROLLER_STATUS.json'
FIT = STUDY / '06_full100/seed42/outer0_inner0'


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path):
    return json.loads(path.read_text())


def save(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def proc_snapshot(p):
    with p.oneshot():
        times = p.cpu_times()._asdict()
        memory = p.memory_info()._asdict()
        io = p.io_counters()._asdict()
        name = p.name()
        result = dict(pid=p.pid, ppid=p.ppid(), name=name, create_time=p.create_time(),
                      cpu_times=times, memory=memory, io=io, threads=p.num_threads(),
                      affinity=p.cpu_affinity(), status=p.status())
    if name.startswith('ffmpeg'):
        args = p.cmdline()
        result['decoder_flags'] = {k: args[args.index(k)+1] for k in
                                  ['-threads', '-filter_threads', '-hwaccel'] if k in args}
    return result


def pressure():
    return {name: Path('/proc/pressure', name).read_text().strip()
            for name in ['cpu', 'memory', 'io']}


def cgroups(pid):
    group = Path(f'/proc/{pid}/cgroup').read_text().strip()
    relative = group.split('::', 1)[-1].lstrip('/')
    current = Path('/sys/fs/cgroup') / relative
    result = {'membership': group, 'ancestors': {}}
    while current.is_relative_to('/sys/fs/cgroup'):
        result['ancestors'][str(current)] = {name: (current / name).read_text().strip()
            for name in ['cpu.max', 'cpu.stat', 'cpuset.cpus.effective', 'memory.max',
                         'memory.high', 'memory.current', 'memory.events', 'io.stat']
            if (current / name).is_file()}
        if current == Path('/sys/fs/cgroup'):
            break
        current = current.parent
    return result


def gpu():
    fields = ['timestamp', 'index', 'utilization.gpu', 'utilization.memory',
              'memory.total', 'memory.used', 'memory.free', 'power.draw', 'power.limit',
              'temperature.gpu', 'clocks.sm', 'clocks.mem', 'pstate']
    p = subprocess.run(['nvidia-smi', '--query-gpu=' + ','.join(fields),
                        '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=5)
    if p.returncode:
        return {'error': p.stderr.strip()}
    return [dict(zip(fields, [v.strip() for v in line.split(',')])) for line in p.stdout.splitlines()]


def snapshot_existing(suffix):
    for name, path in [('controller', STATUS), ('batch', FIT / 'BATCH_PROGRESS.json'),
                       ('history', FIT / 'HISTORY.json'), ('recovery', FIT / 'RECOVERY_POINTER.json'),
                       ('gpu_telemetry', STUDY / '13_reproducibility/runtime/GPU_TELEMETRY.json'),
                       ('watch', STUDY / '13_reproducibility/runtime/WATCH_STATUS.json')]:
        save(f'{name}_{suffix}.json', read_json(path))


def main():
    state = read_json(STATUS)
    trainer = psutil.Process(state['pid'])
    if abs(trainer.create_time() - state['create_time']) > .01:
        raise RuntimeError('Training PID identity mismatch')
    save('provenance.json', dict(start_utc=utc(), duration_seconds=SECONDS,
         sampling_seconds=INTERVAL, command=f'ma_thesis_env/bin/python -B {Path(__file__).relative_to(REPO)}',
         python=platform.python_version(), psutil=psutil.__version__, kernel=platform.release(),
         git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
         git_status=subprocess.check_output(['git', 'status', '--short', '--untracked-files=no'], cwd=REPO, text=True),
         logical_cpus=psutil.cpu_count(), physical_cpus=psutil.cpu_count(logical=False),
         collector_pid=os.getpid(), trainer_identity=state, cgroups=cgroups(trainer.pid),
         read_only_scope='OS counters and existing journals only; no CUDA context or model imports',
         no_secrets_read=True))
    snapshot_existing('start')
    psutil.cpu_times_percent(percpu=True)
    start = time.monotonic()
    count = 0
    with (OUT / 'samples.jsonl').open('x', buffering=1) as stream:
        while time.monotonic() - start < SECONDS:
            row = dict(utc=utc(), monotonic=time.monotonic(),
                       cpu_per_core=[v._asdict() for v in psutil.cpu_times_percent(percpu=True)],
                       memory=psutil.virtual_memory()._asdict(), swap=psutil.swap_memory()._asdict(),
                       pressure=pressure(), loadavg=os.getloadavg(),
                       disk={k: v._asdict() for k, v in psutil.disk_io_counters(perdisk=True).items()},
                       free_bytes=psutil.disk_usage(STUDY).free,
                       collector=proc_snapshot(psutil.Process()), gpu=gpu())
            procs = []
            try:
                row['trainer_identity_valid'] = abs(trainer.create_time() - state['create_time']) < .01
                for p in [trainer] + trainer.children(recursive=True):
                    try:
                        procs.append(proc_snapshot(p))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except psutil.NoSuchProcess:
                row['trainer_identity_valid'] = False
            row['processes'] = procs
            row['batch'] = read_json(FIT / 'BATCH_PROGRESS.json')
            row['controller'] = read_json(STATUS)
            row['cgroup_cpu_stat'] = {k: v.get('cpu.stat') for k, v in cgroups(trainer.pid)['ancestors'].items()}
            stream.write(json.dumps(row, separators=(',', ':')) + '\n')
            count += 1
            if count % 15 == 0:
                print(json.dumps({'utc': row['utc'], 'samples': count, 'epoch': row['batch']['epoch'],
                                  'episodes': row['batch']['episodes'], 'descendants_seen': len(procs)-1}), flush=True)
            delay = start + count * INTERVAL - time.monotonic()
            if delay > 0:
                time.sleep(delay)
    snapshot_existing('end')
    save('end.json', dict(utc=utc(), samples=count, elapsed_seconds=time.monotonic()-start,
                          cgroups=cgroups(trainer.pid), collector=proc_snapshot(psutil.Process())))
    print('READ_ONLY_COLLECTION_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
