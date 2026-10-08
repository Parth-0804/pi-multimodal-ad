import pandas as pd

from pi_multimodal_ad.evaluation.sensor_regression import sensor_metric_table


def test_run_metrics_include_ranges_counts_and_deterministic_intervals() -> None:
    predictions = pd.DataFrame(
        {
            "model_name": ["model"] * 4,
            "split": ["test"] * 4,
            "y_true_raw": [1.0, 2.0, 3.0, 4.0],
            "y_true_monotonic": [1.0, 2.0, 3.0, 4.0],
            "y_pred": [1.5, 2.5, 2.5, 3.5],
        }
    )
    first = sensor_metric_table(predictions, repetitions=100, seed=17)
    second = sensor_metric_table(predictions, repetitions=100, seed=17)
    pd.testing.assert_frame_equal(first, second)
    assert set(first.target_variant) == {
        "raw_top3_mean_pct",
        "causal_monotonic_top3_mean_pct",
    }
    assert first.sample_count.tolist() == [4, 4]
    assert first.target_min.tolist() == [1.0, 1.0]
    assert first.prediction_max.tolist() == [3.5, 3.5]
