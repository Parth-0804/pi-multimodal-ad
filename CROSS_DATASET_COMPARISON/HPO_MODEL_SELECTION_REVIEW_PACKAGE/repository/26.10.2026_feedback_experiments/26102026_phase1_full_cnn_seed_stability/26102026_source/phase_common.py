"""Phase 1 paths, immutable identities and study-local atomic output."""
from pathlib import Path
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
AUDIT = ROOT.parent
STUDY = REPO / 'parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01'
EXEC = ROOT / '26102026_execution/26102026_main_run_01'
EVIDENCE = ROOT / '26102026_evidence'
CONFIG = ROOT / '26102026_configuration/PHASE1_CONFIG.json'
sys.path.insert(0, str(REPO / 'src'))


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024**2), b''):
            h.update(chunk)
    return h.hexdigest()


def signature(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write(path, data):
    path = Path(path)
    assert path.resolve().is_relative_to(ROOT.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.writing')
    with temp.open('w') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def config():
    return read(CONFIG)


def environment():
    import torch
    return {'utc': utc(), 'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
            'git_status': subprocess.check_output(['git', 'status', '--short', '--untracked-files=all'], cwd=REPO, text=True),
            'python': sys.version, 'packages': {n: importlib.metadata.version(n) for n in
            ['torch', 'torchvision', 'transformers', 'numpy', 'scikit-learn', 'opencv-python', 'h5py', 'pytest', 'psutil']},
            'torch_cuda': torch.version.cuda, 'cudnn': torch.backends.cudnn.version(),
            'command': sys.argv, 'cpu_affinity': sorted(os.sched_getaffinity(0))}


def foreign_gpu_processes():
    output = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True)
    return [int(line.strip()) for line in output.splitlines() if line.strip().isdigit() and int(line.strip()) != os.getpid()]


def host_resources():
    import psutil
    root = psutil.Process()
    processes = [root, *root.children(recursive=True)]
    rss, threads = 0, 0
    for process in processes:
        try:
            rss += process.memory_info().rss
            threads += process.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return {'process_tree_RSS_GiB': rss/1024**3, 'process_tree_threads': threads,
            'system_available_RAM_GiB': psutil.virtual_memory().available/1024**3,
            'disk_free_GiB': psutil.disk_usage(ROOT).free/1024**3,
            'system_load_average': os.getloadavg()}
