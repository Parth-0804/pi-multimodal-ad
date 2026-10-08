from __future__ import annotations
import pandas as pd
import torch
from pi_multimodal_ad.models.rtdetr_regression import (
    RegressionHead,
    aggregate_predictions,
)


def test_head_shape_gradient_and_run_aggregation() -> None:
    model = RegressionHead(12, 4, 0)
    x = torch.randn(3, 12)
    output = model(x)
    assert output.shape == (3,)
    output.sum().backward()
    assert all(parameter.grad is not None for parameter in model.parameters())
    rows = []
    for tooth in range(1, 29):
        for view in range(2):
            rows.append(
                {
                    "experiment": "E",
                    "run": 1,
                    "tooth_id": tooth,
                    "split": "train",
                    "image_id": f"{tooth}-{view}",
                    "y_true_raw": float(tooth + view),
                    "y_pred": float(tooth + view + 0.5),
                }
            )
    tooth, runs = aggregate_predictions(pd.DataFrame(rows))
    assert len(tooth) == 28
    assert runs.iloc[0].y_true_raw_top3_mean == 28.0
    assert runs.iloc[0].y_pred_raw_top3_mean == 28.5
