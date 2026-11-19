"""Run-level sensor regression metrics with small-sample uncertainty evidence."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .regression import regression_metrics


def run_grouped_intervals(
    truth: np.ndarray,
    prediction: np.ndarray,
    *,
    repetitions: int,
    seed: int,
) -> dict[str, float]:
    """Bootstrap independent run rows, acknowledging that very small N is unstable."""

    if repetitions <= 0:
        raise ValueError("repetitions must be positive")
    generator = np.random.default_rng(seed)
    mae = np.empty(repetitions)
    rmse = np.empty(repetitions)
    for index in range(repetitions):
        selected = generator.integers(0, len(truth), len(truth))
        error = prediction[selected] - truth[selected]
        mae[index] = np.mean(np.abs(error))
        rmse[index] = np.sqrt(np.mean(error**2))
    return {
        "mae_ci95_low": float(np.quantile(mae, 0.025)),
        "mae_ci95_high": float(np.quantile(mae, 0.975)),
        "rmse_ci95_low": float(np.quantile(rmse, 0.025)),
        "rmse_ci95_high": float(np.quantile(rmse, 0.975)),
    }


def sensor_metric_table(
    predictions: pd.DataFrame, *, repetitions: int, seed: int
) -> pd.DataFrame:
    """Evaluate matching run rows for raw and causal-monotonic targets."""

    rows: list[dict[str, Any]] = []
    for (model_name, split), scoped in predictions.groupby(["model_name", "split"]):
        for target_variant, column in (
            ("raw_top3_mean_pct", "y_true_raw"),
            ("causal_monotonic_top3_mean_pct", "y_true_monotonic"),
        ):
            truth = scoped[column].to_numpy(np.float64)
            prediction = scoped.y_pred.to_numpy(np.float64)
            rows.append(
                {
                    "schema_version": "1.0.0",
                    "model_name": model_name,
                    "split": split,
                    "evaluation_level": "experiment_run",
                    "target_variant": target_variant,
                    "unit": "percentage_points_visible_flank_candidate_area",
                    **regression_metrics(truth, prediction),
                    "target_min": float(truth.min()),
                    "target_max": float(truth.max()),
                    "prediction_min": float(prediction.min()),
                    "prediction_max": float(prediction.max()),
                    **run_grouped_intervals(
                        truth,
                        prediction,
                        repetitions=repetitions,
                        seed=seed,
                    ),
                    "confidence_interval_method": "independent_run_row_resampling",
                    "confidence_interval_warning": "unstable_with_very_small_run_count",
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["target_variant", "split", "model_name"], kind="stable"
    )
