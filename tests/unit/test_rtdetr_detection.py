from __future__ import annotations

import pandas as pd
import pytest

from pi_multimodal_ad.models.rtdetr_detection import (
    average_precision,
    box_iou,
    match_counts,
    metrics_at_threshold,
    select_confidence_threshold,
    sliced_metrics,
)


def _frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    images = pd.DataFrame(
        [
            {"sample_id": "a", "view_role": "canonical_tooth", "run": 1},
            {"sample_id": "b", "view_role": "camera_sequence", "run": 1},
            {"sample_id": "negative", "view_role": "canonical_tooth", "run": 2},
        ]
    )
    truth = pd.DataFrame(
        [
            {"sample_id": "a", "x_min": 0, "y_min": 0, "x_max": 10, "y_max": 10},
            {"sample_id": "b", "x_min": 20, "y_min": 20, "x_max": 40, "y_max": 40},
        ]
    )
    predictions = pd.DataFrame(
        [
            {
                "prediction_id": "p1",
                "sample_id": "a",
                "confidence": 0.9,
                "x_min": 0,
                "y_min": 0,
                "x_max": 10,
                "y_max": 10,
            },
            {
                "prediction_id": "p2",
                "sample_id": "b",
                "confidence": 0.8,
                "x_min": 21,
                "y_min": 21,
                "x_max": 39,
                "y_max": 39,
            },
            {
                "prediction_id": "p3",
                "sample_id": "negative",
                "confidence": 0.2,
                "x_min": 1,
                "y_min": 1,
                "x_max": 4,
                "y_max": 4,
            },
        ]
    )
    return predictions, truth, images


def test_iou_and_greedy_matching_retain_negative_images() -> None:
    predictions, truth, images = _frames()
    assert box_iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    counts = match_counts(
        predictions,
        truth,
        images,
        confidence_threshold=0.1,
        iou_threshold=0.5,
    )
    assert counts.true_positive == 2
    assert counts.false_positive == 1
    assert counts.false_negative == 0
    assert counts.false_positive_images == 1
    assert counts.false_negative_images == 0


def test_ap_and_operating_metrics_are_level_consistent() -> None:
    predictions, truth, images = _frames()
    ap = average_precision(predictions, truth, images, iou_threshold=0.5)
    assert ap == pytest.approx(1.0)
    metrics = metrics_at_threshold(predictions, truth, images, confidence_threshold=0.5)
    assert metrics["image_count"] == 3
    assert metrics["ground_truth_box_count"] == 2
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0
    assert metrics["map50"] == pytest.approx(1.0)
    assert "pseudo-boxes" in metrics["metric_interpretation"]


def test_threshold_selection_and_slices_are_deterministic() -> None:
    predictions, truth, images = _frames()
    selected, curve = select_confidence_threshold(
        predictions,
        truth,
        images,
        candidates=[0.1, 0.5, 0.85],
    )
    assert selected == 0.5
    assert len(curve) == 3
    sliced = sliced_metrics(
        predictions,
        truth,
        images,
        confidence_threshold=selected,
    )
    assert set(sliced.scope) == {
        "all",
        "view_role:canonical_tooth",
        "view_role:camera_sequence",
        "run:1",
        "run:2",
    }
