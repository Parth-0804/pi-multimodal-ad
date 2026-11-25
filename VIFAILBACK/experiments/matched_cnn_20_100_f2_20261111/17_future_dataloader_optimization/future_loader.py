#!/usr/bin/env python3
"""Explicit isolated preparation; never modifies or schedules the protected fits."""
from __future__ import annotations
import argparse
import dataclasses
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
REPO = STUDY.parents[2]
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
for path in [ROOT, STUDY/'src', REPO/'VIFAILBACK/src', REPO/'src']:
    sys.path.insert(0, str(path))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, default=str, allow_nan=False)
        stream.write('\n')


def freeze_check():
    saved = json.loads((STUDY/'13_reproducibility/IMPLEMENTATION_FREEZE.json').read_text())
    actual = {str(p.relative_to(REPO)): sha(p) for p in
              list((STUDY/'src').rglob('*.py')) + list((STUDY/'scripts').glob('*.py'))}
    if actual != saved['implementation']:
        raise RuntimeError('Protected source freeze changed; preparation refused')
    if sha(STUDY/'01_protocol_and_source_evidence/protocol.json') != saved['protocol_sha256']:
        raise RuntimeError('Protected protocol changed; preparation refused')
    return saved


def cpu_limits():
    # Affect this new process and its spawned workers only. Never set trainer affinity.
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    for name in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        os.environ[name] = '1'
    affinity = sorted(os.sched_getaffinity(0))[:2]
    os.sched_setaffinity(0, affinity)
    os.nice(max(0, 10-os.getpriority(os.PRIO_PROCESS, 0)))
    return {'CUDA_visible_devices': '', 'affinity': affinity, 'nice': os.getpriority(os.PRIO_PROCESS, 0),
            'BLAS_threads': 1, 'scope': 'This preparation process and its children only'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['inspect', 'validate-cpu', 'benchmark-status', 'benchmark-gpu', 'export-config'])
    parser.add_argument('--configs', nargs='+', default=['baseline_w2_p1','w4_p1','w4_p2','w2_p4'])
    parser.add_argument('--run-id', help='Unique name for a new results subdirectory')
    parser.add_argument('--cpu-validation', type=Path, help='PASS CPU contract receipt for future GPU benchmark')
    parser.add_argument('--benchmark-receipt', type=Path, help='Completed qualifying GPU_BENCHMARK.json for config export')
    parser.add_argument('--rounds', type=int, default=4)
    parser.add_argument('--episodes', type=int, default=32)
    parser.add_argument('--warmup-episodes', type=int, default=8)
    args = parser.parse_args()
    from future_dataloader.settings import PRESETS
    if len(args.configs) != len(set(args.configs)) or any(n not in PRESETS for n in args.configs):
        parser.error('Use unique declared preset names')
    if 'baseline_w2_p1' not in args.configs:
        parser.error('The unchanged baseline must be included')
    run_id = args.run_id or dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+args.command
    if not re.fullmatch(r'[A-Za-z0-9_-]+', run_id):
        parser.error('Run ID must contain only letters, digits, hyphens and underscores')
    frozen = freeze_check()
    limits = cpu_limits() if args.command != 'benchmark-gpu' else None
    if args.command == 'benchmark-gpu':
        for name in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
            os.environ[name] = '2'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    destination = ROOT/'results'/run_id
    destination.mkdir(parents=True, exist_ok=False)
    packages = {}
    for name in ['torch','torchvision','transformers','numpy','psutil','av','Pillow','pytest']:
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name] = 'not installed'
    provenance = {'utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                  'command': sys.argv, 'git_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
                  'git_working_tree_dirty': bool(subprocess.check_output(
                      ['git','status','--porcelain','--untracked-files=normal'],cwd=REPO,text=True).strip()),
                  'methodology_version': 'future-loader-isolated-v1',
                  'run_identity_policy': 'Unique exclusive-create output directory; never resume or overwrite',
                  'data_identity_policy': 'Original ViFailback episode/camera/frame identities; no deduplication or split changes',
                  'python': sys.version, 'packages': packages,
                  'protected_protocol_sha256': frozen['protocol_sha256'],
                  'protected_implementation': frozen['implementation'],
                  'isolated_implementation': {str(p.relative_to(REPO)):sha(p) for p in ROOT.rglob('*.py')},
                  'configs': {n:dataclasses.asdict(PRESETS[n]) for n in args.configs},
                  'CPU_preparation_limits': limits,
                  'effective_thread_environment': {key:os.environ.get(key) for key in
                      ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS','TOKENIZERS_PARALLELISM']},
                  'process_affinity':sorted(os.sched_getaffinity(0)),
                  'process_nice':os.getpriority(os.PRIO_PROCESS,0),
                  'no_training_queue_changes': True,
                  'no_model_optimizer_seed_epoch_split_changes': True, 'no_push': True}
    save(destination/'PREPARATION_PROVENANCE.json', provenance)
    try:
        if args.command == 'inspect':
            result = {'status':'PREPARED', 'presets':provenance['configs'],
                      'max_episode_queue':{n:PRESETS[n].max_prefetched_episodes for n in args.configs},
                      'protected_source_freeze':'PASS','GPU_benchmark':'PENDING',
                      'recommended_configuration':None,'measured_speedup':None}
        elif args.command == 'validate-cpu':
            from future_dataloader.contracts import validate_cpu
            result = validate_cpu(destination, args.configs)
        elif args.command == 'benchmark-status':
            from future_dataloader.guards import inspect_admission
            state = inspect_admission()
            result = {'status':'READY_FOR_MANUAL_BENCHMARK' if state['ready'] else 'PENDING',
                      'admission':state,'measured_speedup':None,'recommended_configuration':None,
                      'automatic_launch':False}
        elif args.command == 'export-config':
            if not args.benchmark_receipt:
                raise ValueError('export-config requires --benchmark-receipt')
            from future_dataloader.activation import export_config
            result = export_config(args.benchmark_receipt, destination)
        else:
            # Only a manual future invocation reaches this branch; benchmark performs
            # admission and takes cooperative locks before any CUDA/model work.
            from future_dataloader.benchmark import run_benchmark
            result = run_benchmark(destination/'gpu_benchmark', args.configs,
                       {'rounds':args.rounds,'episodes':args.episodes,'warmup_episodes':args.warmup_episodes,
                        'cpu_validation':str(args.cpu_validation.resolve()) if args.cpu_validation else None})
        freeze_check()
        save(destination/'COMMAND_RESULT.json', result)
    except BaseException as exc:
        save(destination/'COMMAND_ERROR.json', {'type':type(exc).__name__,'error':str(exc),
                                              'protected_source_freeze_unchanged': bool(freeze_check())})
        raise
    finally:
        outputs = [{'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':sha(p)}
                   for p in sorted(destination.rglob('*')) if p.is_file()]
        save(destination/'OUTPUT_MANIFEST.json', {'outputs':outputs,'self_excluded':True})
    concise = {key:result[key] for key in ['status','selected_episode_ids','real_decoded_episodes',
               'checked_config_names','measured_speedup','recommended_configuration','recommendation',
               'numerical_equivalence_pass'] if key in result}
    if 'admission' in result:
        concise['admission_reasons'] = result['admission']['reasons']
    print(json.dumps({'output':str(destination.relative_to(REPO)),'result':concise},indent=2,default=str))


if __name__ == '__main__':
    main()
