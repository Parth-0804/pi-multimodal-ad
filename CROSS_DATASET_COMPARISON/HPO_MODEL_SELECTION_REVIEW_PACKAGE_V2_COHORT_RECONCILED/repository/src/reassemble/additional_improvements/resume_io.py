"""Reuse completed sensor folds without rewriting retained evidence."""
from pathlib import Path
import numpy as np
from .common import read


def completed_hybrid_fold(root, fold, train, test):
    stem = Path(root) / f'hybrid_outer{fold}'
    meta, pred = stem.with_suffix('.json'), stem.with_suffix('.npz')
    if not meta.exists() and not pred.exists():
        return None
    if not meta.exists() or not pred.exists():
        raise ValueError(f'Incomplete retained fold pair: {stem}')
    info = read(meta)
    if info['fold'] != fold:
        raise ValueError('Retained fold identity mismatch')
    with np.load(pred, allow_pickle=False) as saved:
        if not np.array_equal(saved['train_rows'], train) or not np.array_equal(saved['test_rows'], test):
            raise ValueError('Retained fold sample identity/order mismatch')
        p, hard = saved['p'].copy(), saved['hard'].copy()
    if p.shape != (len(test),) or hard.shape != p.shape or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError('Invalid retained fold predictions')
    if not np.array_equal(hard, p >= info['threshold']):
        raise ValueError('Retained decisions differ from saved threshold')
    return p, hard
