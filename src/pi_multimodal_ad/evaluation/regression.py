"""Deterministic regression metrics and inference-safe naive baselines."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr


def regression_metrics(
    y_true: Sequence[float], y_pred: Sequence[float]
) -> dict[str, Any]:
    truth = np.asarray(y_true, dtype=np.float64)
    prediction = np.asarray(y_pred, dtype=np.float64)
    if truth.shape != prediction.shape or truth.ndim != 1 or not len(truth):
        raise ValueError("truth and prediction must be nonempty equal-length vectors")
    if not np.isfinite(truth).all() or not np.isfinite(prediction).all():
        raise ValueError("metrics require finite values")
    error = prediction - truth
    absolute = np.abs(error)
    mse = float(np.mean(error**2))
    variance = float(np.sum((truth - truth.mean()) ** 2))
    r2 = (
        None
        if len(truth) < 3 or variance <= 0
        else 1.0 - float(np.sum(error**2)) / variance
    )
    spearman = spearmanr(truth, prediction).statistic if len(truth) >= 3 else np.nan
    kendall = kendalltau(truth, prediction).statistic if len(truth) >= 3 else np.nan
    return {
        "sample_count": int(len(truth)),
        "mse": mse,
        "mae": float(np.mean(absolute)),
        "rmse": float(np.sqrt(mse)),
        "median_absolute_error": float(np.median(absolute)),
        "bias": float(np.mean(error)),
        "r2": None if r2 is None else float(r2),
        "spearman": None if not np.isfinite(spearman) else float(spearman),
        "kendall": None if not np.isfinite(kendall) else float(kendall),
    }


def bootstrap_mae_interval(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    *,
    repetitions: int,
    seed: int,
) -> tuple[float, float]:
    truth = np.asarray(y_true, dtype=np.float64)
    prediction = np.asarray(y_pred, dtype=np.float64)
    generator = np.random.default_rng(seed)
    values = np.empty(repetitions, dtype=np.float64)
    for index in range(repetitions):
        selected = generator.integers(0, len(truth), len(truth))
        values[index] = np.mean(np.abs(prediction[selected] - truth[selected]))
    return float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def naive_predictions(samples: pd.DataFrame) -> pd.DataFrame:
    training = samples[samples.split.eq("train")]
    if training.empty:
        raise ValueError("training split is empty")
    target = "per_image_damage_candidate_pct"
    constants = {
        "training_mean": float(training[target].mean()),
        "training_median": float(training[target].median()),
    }
    rows: list[dict[str, Any]] = []
    for model_name, value in constants.items():
        for _, row in samples.iterrows():
            rows.append(
                {
                    "sample_id": row.sample_id,
                    "image_id": row.image_id,
                    "experiment": row.experiment,
                    "run": int(row.run),
                    "tooth_id": int(row.tooth_id),
                    "split": row.split,
                    "y_true_raw": float(row[target]),
                    "y_true_monotonic": None,
                    "y_pred": value,
                    "physical_unit": row.target_unit,
                    "target_definition_version": row.target_definition_version,
                    "target_verification_status": row.target_verification_status,
                    "model_name": model_name,
                    "model_run_id": "deterministic_naive_baseline",
                    "latency_ms": 0.0,
                    "confidence_or_uncertainty": None,
                }
            )
    return pd.DataFrame(rows)


def metric_table(
    predictions: pd.DataFrame, *, repetitions: int, seed: int
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (model, split, experiment), scoped in predictions.groupby(
        ["model_name", "split", "experiment"], dropna=False
    ):
        metrics = regression_metrics(scoped.y_true_raw, scoped.y_pred)
        low, high = bootstrap_mae_interval(
            scoped.y_true_raw, scoped.y_pred, repetitions=repetitions, seed=seed
        )
        rows.append(
            {
                "model_name": model,
                "split": split,
                "experiment": experiment,
                "evaluation_level": "image_view",
                "unit": "percentage_points_visible_flank_candidate_area",
                **metrics,
                "mae_ci95_low": low,
                "mae_ci95_high": high,
            }
        )
    return pd.DataFrame(rows)
