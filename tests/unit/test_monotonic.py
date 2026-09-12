"""Monotonic-rescale scoring, including the degenerate constant-prediction case."""

from __future__ import annotations

import numpy as np
import pytest

from pi_multimodal_ad.evaluation.monotonic import (
    DEGENERATE_CONSTANT_PREDICTION,
    monotonic_metrics,
    monotonic_rescale,
)


def test_perfectly_ranked_predictions_score_zero_however_scaled():
    truth = [1.0, 2.0, 3.0, 4.0, 5.0]
    # wrong scale, wrong offset, perfectly right order
    prediction = [100.0, 200.0, 300.0, 400.0, 500.0]
    result = monotonic_metrics(truth, prediction)
    assert result["monotonic_mse"] == pytest.approx(0.0, abs=1e-12)
    assert result["degeneracy"] is None


def test_monotonic_score_ignores_offset_that_mae_punishes():
    truth = np.array([1.0, 2.0, 3.0, 4.0])
    prediction = truth + 50.0
    raw_mae = float(np.mean(np.abs(prediction - truth)))
    result = monotonic_metrics(truth, prediction)
    assert raw_mae == pytest.approx(50.0)
    assert result["monotonic_mse"] == pytest.approx(0.0, abs=1e-12)


def test_constant_prediction_is_labelled_not_nan():
    truth = [1.0, 2.0, 3.0, 4.0]
    result = monotonic_metrics(truth, [7.0, 7.0, 7.0, 7.0])
    assert result["degeneracy"] == DEGENERATE_CONSTANT_PREDICTION
    assert np.isfinite(result["monotonic_mse"])
    # best a constant can do is the target mean -> variance of the target
    assert result["monotonic_mse"] == pytest.approx(np.var(truth))


def test_constant_prediction_value_does_not_matter():
    truth = [1.0, 2.0, 3.0, 4.0]
    low = monotonic_metrics(truth, [0.0] * 4)["monotonic_mse"]
    high = monotonic_metrics(truth, [999.0] * 4)["monotonic_mse"]
    assert low == pytest.approx(high)


def test_reversed_ranking_is_penalised():
    truth = [1.0, 2.0, 3.0, 4.0, 5.0]
    reversed_prediction = [5.0, 4.0, 3.0, 2.0, 1.0]
    result = monotonic_metrics(truth, reversed_prediction)
    # an increasing isotonic fit on anti-correlated input collapses to the mean
    assert result["monotonic_mse"] == pytest.approx(np.var(truth))


def test_weak_rank_signal_beats_a_constant():
    """The asymmetry that makes this metric worth computing."""

    rng = np.random.default_rng(0)
    truth = rng.normal(size=40)
    noisy = truth + rng.normal(scale=1.5, size=40)  # weak but real rank signal
    weak = monotonic_metrics(truth, noisy)["monotonic_mse"]
    constant = monotonic_metrics(truth, np.full(40, truth.mean()))["monotonic_mse"]
    assert weak < constant


def test_rejects_mismatched_or_nonfinite_input():
    with pytest.raises(ValueError):
        monotonic_rescale([1.0, 2.0], [1.0])
    with pytest.raises(ValueError):
        monotonic_rescale([1.0, 2.0], [1.0, np.nan])
    with pytest.raises(ValueError):
        monotonic_rescale([], [])
