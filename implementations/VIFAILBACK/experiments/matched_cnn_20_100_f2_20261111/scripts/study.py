#!/usr/bin/env python3
"""Explicit commands for the isolated matched ViFailback experiment."""
import argparse
import json
import os
from pathlib import Path
import sys

STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY / 'src'))
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ.setdefault(key, '2')
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('command', choices=['verify', 'benchmark', 'benchmark8', 'admit', 'freeze', 'pilot', 'run', 'evaluate', 'report', 'watch', 'status'])
    parser.add_argument('--lane', choices=['cpu', 'gpu'])
    args = parser.parse_args()
    from matched_vifailback.common import read_json
    if args.command == 'verify':
        from matched_vifailback.data import prepare
        context = prepare()
        result = {'cohort': context['verification']['cohort'], 'jobs': len(context['jobs']), 'pilot': context['verification']['pilot']}
    elif args.command in ['benchmark', 'benchmark8']:
        from matched_vifailback.resources import verify_source_stop, gate
        verify_source_stop()
        state = gate(extra_bytes=1024**3)
        if not state['ready']:
            raise RuntimeError(state)
        from matched_vifailback.benchmark import run, run_batch8
        result = run() if args.command == 'benchmark' else run_batch8()
    elif args.command == 'admit':
        path = STUDY / '01_protocol_and_source_evidence/RESOURCE_ADMISSION.json'
        if path.exists():
            from matched_vifailback.controller import admission
            result = admission()
        else:
            from matched_vifailback.resources import prospective_admission
            from matched_vifailback.data import load_context
            result = prospective_admission(load_context(), read_json(STUDY / '13_reproducibility/BOUNDED_GPU_BENCHMARK.json'))
    elif args.command == 'freeze':
        from matched_vifailback.controller import freeze_code
        result = freeze_code()
    elif args.command == 'pilot':
        from matched_vifailback.controller import check_frozen_code, admission
        from matched_vifailback.data import load_context
        from matched_vifailback.training import fit
        check_frozen_code(); admission()
        context = load_context(verify=True)
        result = [fit(condition, 42, 'outer0_inner0', context=context) for condition in ['FROZEN100','DONOR100']]
    elif args.command == 'run':
        if not args.lane:
            parser.error('run requires --lane cpu or gpu')
        from matched_vifailback.controller import run
        result = run(args.lane)
    elif args.command in ['evaluate', 'watch']:
        from matched_vifailback import controller
        result = getattr(controller, args.command)()
    elif args.command == 'report':
        from matched_vifailback.reporting import generate
        result = generate()
    else:
        from matched_vifailback.common import utc
        result = {'utc': utc()}
        runtime = STUDY / '13_reproducibility/runtime'
        for name in ['CPU_CONTROLLER_STATUS.json', 'GPU_CONTROLLER_STATUS.json', 'WATCH_STATUS.json', 'GPU_TELEMETRY.json']:
            result[name] = read_json(runtime / name) if (runtime / name).exists() else {'stage': 'NOT_LAUNCHED'}
    if result is not None:
        print(json.dumps(result, indent=2, default=str))


if __name__ == '__main__':
    main()
