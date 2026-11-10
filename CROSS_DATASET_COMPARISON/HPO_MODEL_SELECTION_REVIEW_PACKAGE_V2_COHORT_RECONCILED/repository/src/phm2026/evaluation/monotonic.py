"""Scoring under the organizer's metric: MSE after an optimal monotonic rescale.

The challenge scores MSE *after* fitting an optimal monotonic transform of the
predictions, so only trajectory shape counts and absolute scale does not. Every
other number in this repository is raw MAE on a self-defined scale, which can
disagree sharply: a model that tracks shape well but sits at the wrong offset
scores badly on MAE and well here.

The asymmetry this creates is the point, and it is not a defect of the metric:
a constant prediction carries no rank information, so no monotonic transform
can recover anything from it beyond the best single constant. A model with even
weak rank signal can therefore overtake a constant here while losing on MAE.

The fit is in-sample by construction -- the transform is fitted on the same set
it scores, exactly as the organizer specifies -- so this is an optimistic bound
on shape agreement, not a generalization estimate. `fitted_on_evaluation_set`
is recorded on every result so that never has to be inferred.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from sklearn.isotonic import IsotonicRegression

DEGENERATE_CONSTANT_PREDICTION = "constant_prediction_no_rank_information"


def monotonic_rescale(
    y_true: Sequence[float], y_pred: Sequence[float]
) -> tuple[np.ndarray, str | None]:
    """Map predictions onto the target with the best non-decreasing transform.

    Returns the transformed predictions and a degeneracy note, which is None
    for the ordinary case. A prediction vector with no spread cannot be
    reshaped by any monotonic function, so the best it can do is the mean of
    the targets; that case is labelled rather than silently returning NaN.
    """

    truth = np.asarray(y_true, dtype=np.float64)
    prediction = np.asarray(y_pred, dtype=np.float64)
    if truth.shape != prediction.shape or truth.ndim != 1 or not len(truth):
        raise ValueError("truth and prediction must be nonempty equal-length vectors")
    if not np.isfinite(truth).all() or not np.isfinite(prediction).all():
        raise ValueError("monotonic rescaling requires finite values")

    if np.ptp(prediction) == 0.0:
        # Every monotonic transform of a constant is a constant; the optimal
        # one under squared error is the target mean.
        return np.full_like(truth, truth.mean()), DEGENERATE_CONSTANT_PREDICTION

    model = IsotonicRegression(increasing=True, out_of_bounds="clip")
    transformed = model.fit_transform(prediction, truth)
    return np.asarray(transformed, dtype=np.float64), None


def monotonic_metrics(
    y_true: Sequence[float], y_pred: Sequence[float]
) -> dict[str, Any]:
    """MSE and friends after the optimal monotonic rescale."""

    truth = np.asarray(y_true, dtype=np.float64)
    transformed, degeneracy = monotonic_rescale(truth, y_pred)
    error = transformed - truth
    mse = float(np.mean(error**2))
    variance = float(np.sum((truth - truth.mean()) ** 2))
    r2 = (
        None
        if len(truth) < 3 or variance <= 0
        else 1.0 - float(np.sum(error**2)) / variance
    )
    return {
        "sample_count": int(len(truth)),
        "monotonic_mse": mse,
        "monotonic_rmse": float(np.sqrt(mse)),
        "monotonic_mae": float(np.mean(np.abs(error))),
        "monotonic_r2": None if r2 is None else float(r2),
        "degeneracy": degeneracy,
        "fitted_on_evaluation_set": True,
    }
