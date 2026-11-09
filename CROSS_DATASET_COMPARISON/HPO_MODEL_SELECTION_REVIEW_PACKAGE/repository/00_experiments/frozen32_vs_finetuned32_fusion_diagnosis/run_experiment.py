"""Explicit local entry point: prepare, checks, run, or report. Never schedules work."""
from pathlib import Path
import argparse
import os
import sys

ROOT=Path(__file__).resolve().parent
for key,value in {'CUBLAS_WORKSPACE_CONFIG':':4096:8','OMP_NUM_THREADS':'4','MKL_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'4',
                  'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','TOKENIZERS_PARALLELISM':'false',
                  'MPLCONFIGDIR':str(ROOT/'results/provenance/matplotlib_cache'),'PYTHONDONTWRITEBYTECODE':'1'}.items():os.environ.setdefault(key,value)
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:4]))
sys.path.insert(0,str(ROOT/'code'))
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stage',choices=['prepare','checks','run','report']);args=parser.parse_args()
if args.stage=='prepare':
    from prepare import prepare
    prepare()
elif args.stage=='checks':
    import unittest
    from common import write
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    write(ROOT/'results/checks/focused_tests.json',{'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'New seed/membership, arithmetic, training prefix policy and checkpoint/RNG mechanics; no old test suite repeated'})
    sys.exit(0 if result.wasSuccessful() else 1)
elif args.stage=='run':
    from pipeline import run
    run()
else:
    from analysis import report
    report('REPORT_ONLY')
