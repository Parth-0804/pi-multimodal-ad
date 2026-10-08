from __future__ import annotations
import pandas as pd
import pytest
from pi_multimodal_ad.evaluation.regression import naive_predictions, regression_metrics


def test_regression_metrics_and_training_only_naive_fit() -> None:
    metrics = regression_metrics([1, 2, 3], [1, 2, 4])
    assert metrics["mae"] == pytest.approx(1 / 3)
    assert metrics["rmse"] == pytest.approx((1 / 3) ** 0.5)
    rows = []
    for index, (split, value) in enumerate(
        (("train", 1.0), ("train", 3.0), ("test", 100.0))
    ):
        rows.append(
            {
                "sample_id": str(index),
                "image_id": str(index),
                "experiment": "E",
                "run": 1,
                "tooth_id": index + 1,
                "split": split,
                "per_image_damage_candidate_pct": value,
                "target_unit": "pct",
                "target_definition_version": "v",
                "target_verification_status": "provisional",
            }
        )
    predictions = naive_predictions(pd.DataFrame(rows))
    test = predictions[predictions.split.eq("test")]
    assert set(test.y_pred) == {2.0}
