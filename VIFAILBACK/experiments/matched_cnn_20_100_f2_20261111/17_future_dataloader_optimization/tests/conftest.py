"""Test isolation: CUDA hidden before collection, at most two CPU cores."""
import os
from pathlib import Path
import sys

os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
sys.dont_write_bytecode = True
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key] = '1'
os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])
os.nice(max(0,10-os.getpriority(os.PRIO_PROCESS,0)))
root = Path(__file__).resolve().parents[1]
study = root.parent
repo = study.parents[2]
for path in [root, study/'src', repo/'VIFAILBACK/src', repo/'src']:
    sys.path.insert(0,str(path))
