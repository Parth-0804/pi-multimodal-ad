#!/usr/bin/env python3
"""Phase 4, item 3+5+7: confidence calibration, view_role/run/box-size slicing.

Reuses pi_multimodal_ad.models.rtdetr_detection's sliced_metrics,
metrics_at_threshold, and the module's own IoU-matrix helper (_iou_matrix)
for the per-prediction match labels calibration needs (match_counts only
returns aggregate counts, not which individual predictions matched, so this
is the smallest reuse of the existing IoU logic that gets per-prediction
labels without reimplementing IoU matching itself).
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))
from pi_multimodal_ad.models.rtdetr_detection import (  # noqa: E402
    _iou_matrix,
    sliced_metrics,
)

PSEUDO_RUN = (
    REPO_ROOT / "runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794"
)
DETECTION_RUN = (
    REPO_ROOT / "runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af"
)
OUT_DIR = Path(__file__).resolve().parents[1] / "analysis" / "02_calibration_and_slicing"
OUT_DIR.mkdir(parents=True, exist_ok=True)

IOU_THRESHOLD = 0.5


def per_prediction_match_labels(
    predictions: pd.DataFrame, ground_truth: pd.DataFrame
) -> pd.Series:
    """For every prediction (all confidences), is it the best-IoU greedy
    match for some still-unmatched ground-truth box at IoU>=0.5? Same
    greedy-by-confidence-then-id algorithm as
    rtdetr_detection._greedy_image_matches, just retaining a per-row label
    instead of only aggregate counts.
    """
    labels = pd.Series(False, index=predictions.index)
    for sample_id, group in predictions.groupby("sample_id"):
        truth = ground_truth[ground_truth.sample_id == sample_id]
        if truth.empty or group.empty:
            continue
        ordered = group.sort_values(
            ["confidence", "prediction_id"], ascending=[False, True], kind="stable"
        )
        pred_boxes = ordered[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
        truth_boxes = truth[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
        ious = _iou_matrix(pred_boxes, truth_boxes)
        unmatched = np.ones(len(truth_boxes), dtype=bool)
        for row_position, order_index in enumerate(ordered.index):
            available = np.flatnonzero(unmatched)
            if not len(available):
                continue
            row = ious[row_position]
            best_position = int(available[np.argmax(row[available])])
            if float(row[best_position]) >= IOU_THRESHOLD:
                unmatched[best_position] = False
                labels.loc[order_index] = True
    return labels


def main() -> None:
    images = pd.read_parquet(PSEUDO_RUN / "tables/annotation_image_manifest.parquet")
    ground_truth = pd.read_parquet(PSEUDO_RUN / "tables/annotation_manifest.parquet")
    test_images = images[images.split == "test"].copy()
    test_truth = ground_truth[ground_truth.sample_id.isin(test_images.sample_id)].copy()
    test_predictions = pd.read_parquet(DETECTION_RUN / "tables/test_predictions.parquet")

    # --- item 3: calibration ---
    matched = per_prediction_match_labels(test_predictions, test_truth)
    calibrated = test_predictions.assign(is_iou50_match=matched)
    calibrated["confidence_decile"] = pd.qcut(
        calibrated.confidence, 10, labels=False, duplicates="drop"
    )
    calibration_table = (
        calibrated.groupby("confidence_decile")
        .agg(
            n=("confidence", "size"),
            confidence_min=("confidence", "min"),
            confidence_max=("confidence", "max"),
            confidence_mean=("confidence", "mean"),
            match_rate=("is_iou50_match", "mean"),
            match_count=("is_iou50_match", "sum"),
        )
        .reset_index()
    )
    calibration_table.to_csv(OUT_DIR / "confidence_calibration_by_decile.csv", index=False)
    print("=== confidence calibration by decile (all EXP-F test predictions) ===")
    print(calibration_table.to_string(index=False))
    correlation = float(
        np.corrcoef(calibrated.confidence, calibrated.is_iou50_match.astype(float))[0, 1]
    )
    print(f"\nPearson correlation(confidence, is_IoU>=0.5_match) = {correlation:.5f}")
    with (OUT_DIR / "calibration_correlation.txt").open("w") as handle:
        handle.write(
            f"pearson_correlation_confidence_vs_iou50_match = {correlation:.6f}\n"
            f"n_predictions = {len(calibrated)}\n"
            f"overall_match_rate = {float(calibrated.is_iou50_match.mean()):.6f}\n"
        )

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(
        calibration_table.confidence_decile.astype(str),
        calibration_table.match_rate,
        color="#4C72B0",
    )
    ax.set_xlabel("confidence decile (low -> high, all within 0.00124-0.00150)")
    ax.set_ylabel("fraction that are an IoU>=0.5 greedy match")
    ax.set_title(
        f"Confidence calibration, EXP-F test (Pearson r={correlation:.4f})"
    )
    fig.tight_layout()
    fig.savefig(OUT_DIR / "calibration_by_decile.png", dpi=150)
    plt.close(fig)

    # --- item 5+7: slicing by view_role, run (via sliced_metrics), and box-size bucket ---
    # sliced_metrics needs a confidence_threshold; use 0.0 since item 1 showed
    # every official candidate is above the model's observed range and would
    # make every slice trivially empty.
    role_run_slices = sliced_metrics(
        test_predictions, test_truth, test_images, confidence_threshold=0.0
    )
    role_run_slices.to_csv(OUT_DIR / "sliced_metrics_view_role_and_run.csv", index=False)
    print("\n=== sliced_metrics (threshold=0.0) by scope ===")
    print(
        role_run_slices[
            ["scope", "image_count", "ground_truth_box_count", "true_positive",
             "false_positive", "false_negative", "precision", "recall", "f1"]
        ].to_string(index=False)
    )

    # box-size bucket slicing: tercile pseudo-box area buckets, evaluate
    # match rate for GT boxes in each bucket (does the model do better on
    # larger pseudo-boxes, closer to its own predicted-box scale?).
    test_truth = test_truth.assign(box_area=(test_truth.x_max - test_truth.x_min) * (test_truth.y_max - test_truth.y_min))
    test_truth["size_bucket"] = pd.qcut(
        test_truth.box_area, 3, labels=["small", "medium", "large"]
    )
    # Recompute per-GT-box matched status (symmetric to per-prediction): a
    # GT box counts as "recovered" if some prediction matched it in the
    # same greedy pass.
    gt_recovered = pd.Series(False, index=test_truth.index)
    for sample_id, group in test_predictions.groupby("sample_id"):
        truth = test_truth[test_truth.sample_id == sample_id]
        if truth.empty or group.empty:
            continue
        ordered = group.sort_values(
            ["confidence", "prediction_id"], ascending=[False, True], kind="stable"
        )
        pred_boxes = ordered[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
        truth_boxes = truth[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
        ious = _iou_matrix(pred_boxes, truth_boxes)
        unmatched = np.ones(len(truth_boxes), dtype=bool)
        for row_position in range(len(ordered)):
            available = np.flatnonzero(unmatched)
            if not len(available):
                break
            row = ious[row_position]
            best_position = int(available[np.argmax(row[available])])
            if float(row[best_position]) >= IOU_THRESHOLD:
                unmatched[best_position] = False
        recovered_local = ~unmatched
        gt_recovered.loc[truth.index[recovered_local]] = True
    test_truth = test_truth.assign(recovered=gt_recovered)
    size_bucket_recall = (
        test_truth.groupby("size_bucket", observed=True)
        .agg(
            gt_box_count=("recovered", "size"),
            recovered_count=("recovered", "sum"),
            recall=("recovered", "mean"),
            median_area_px2=("box_area", "median"),
        )
        .reset_index()
    )
    size_bucket_recall.to_csv(OUT_DIR / "recall_by_pseudo_box_size_tercile.csv", index=False)
    print("\n=== recall by pseudo-box size tercile, EXP-F test, IoU>=0.5, threshold=0.0 ===")
    print(size_bucket_recall.to_string(index=False))

    print("\nWrote:")
    for path in sorted(OUT_DIR.iterdir()):
        print(" ", path)


if __name__ == "__main__":
    main()
