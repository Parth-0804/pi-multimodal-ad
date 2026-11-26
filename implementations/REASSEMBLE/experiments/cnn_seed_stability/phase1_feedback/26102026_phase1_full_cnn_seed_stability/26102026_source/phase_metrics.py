"""Shared, keyed evaluation arithmetic; no fitting or model selection."""
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss, log_loss


def metrics(y, probability):
    y, p = np.asarray(y, int), np.asarray(probability, float)
    assert len(y) == len(p) and np.isfinite(p).all() and ((p >= 0) & (p <= 1)).all()
    assert set(np.unique(y)) <= {0, 1}
    return {'n': len(y), 'failures': int(y.sum()), 'prevalence': float(y.mean()),
            'AP': float(average_precision_score(y, p)) if y.sum() else None,
            'AUROC': float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
            'Brier': float(brier_score_loss(y, p)),
            'log_loss': float(log_loss(y, np.clip(p, 1e-7, 1-1e-7), labels=[0, 1]))}


def better(candidate, incumbent):
    if incumbent is None:
        return True
    return (candidate['validation_AP'], -candidate['validation_loss'], -candidate['epoch']) > (
        incumbent['validation_AP'], -incumbent['validation_loss'], -incumbent['epoch'])


def stop_after_epoch(epoch, best_epoch, minimum=25, maximum=50, patience=10):
    return epoch >= maximum or (epoch >= minimum and epoch - best_epoch >= patience)


def aligned_keys(rows, expected):
    keys = [r['sample_id'] for r in rows]
    assert len(keys) == len(set(keys)) and set(keys) == set(expected), 'PREDICTION_ALIGNMENT_FAILURE'
    return {r['sample_id']: r for r in rows}
