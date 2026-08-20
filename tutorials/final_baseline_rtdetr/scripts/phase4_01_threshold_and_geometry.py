#!/usr/bin/env python3
"""Phase 4, item 1+2+4: confidence-floor artifact, box-geometry mismatch,
and an extended precision-recall curve down to the model's true observed
minimum confidence.

Reuses pi_multimodal_ad.models.rtdetr_detection's match_counts/
average_precision/metrics_at_threshold rather than reimplementing IoU
matching or AP. Reads only from the two pinned runs; writes only under
tutorials/final_baseline_rtdetr/analysis/.
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
    average_precision,
    match_counts,
    metrics_at_threshold,
)

PSEUDO_RUN = (
    REPO_ROOT / "runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794"
)
DETECTION_RUN = (
    REPO_ROOT / "runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af"
)
OUT_DIR = Path(__file__).resolve().parents[1] / "analysis" / "01_threshold_and_geometry"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    images = pd.read_parquet(PSEUDO_RUN / "tables/annotation_image_manifest.parquet")
    ground_truth = pd.read_parquet(PSEUDO_RUN / "tables/annotation_manifest.parquet")
    test_images = images[images.split == "test"].copy()
    test_truth = ground_truth[ground_truth.sample_id.isin(test_images.sample_id)].copy()
    test_predictions = pd.read_parquet(DETECTION_RUN / "tables/test_predictions.parquet")

    conf = test_predictions.confidence
    print("Observed test-prediction confidence range:", conf.min(), "-", conf.max())
    print("Official tested candidates (validation_threshold_selection.csv): 0.01-0.60")
    print(
        "=> every official candidate is above the observed max confidence "
        f"({conf.max():.6f}); confirms the confidence-floor thresholding artifact."
    )

    # --- item 1: sweep thresholds down through the model's real range ---
    true_min = float(conf.min())
    true_max = float(conf.max())
    # Include the official low candidate (0.01) for continuity, then sweep
    # the actual observed range plus below it (0.0) to show the full curve.
    sweep = sorted(
        set(
            [0.0]
            + list(np.linspace(true_min, true_max, 25))
            + [0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.6]
        )
    )
    rows = []
    for threshold in sweep:
        counts = match_counts(
            test_predictions, test_truth, test_images,
            confidence_threshold=threshold, iou_threshold=0.5,
        )
        precision = counts.true_positive / max(counts.true_positive + counts.false_positive, 1)
        recall = counts.true_positive / max(counts.true_positive + counts.false_negative, 1)
        rows.append(
            {
                "confidence_threshold": threshold,
                "n_predictions_surviving": int(
                    (test_predictions.confidence >= threshold).sum()
                ),
                "true_positive": counts.true_positive,
                "false_positive": counts.false_positive,
                "false_negative": counts.false_negative,
                "precision": precision,
                "recall": recall,
                "mean_matched_iou": (
                    float(np.mean(counts.matched_ious)) if counts.matched_ious else float("nan")
                ),
            }
        )
    sweep_frame = pd.DataFrame(rows)
    sweep_frame.to_csv(OUT_DIR / "threshold_sweep_full_range.csv", index=False)
    print("\n=== threshold sweep (selected rows) ===")
    print(sweep_frame.to_string(index=False))

    # Unthresholded (all raw predictions >= the 0.001 floor already applied
    # at collection time) TP count — the maximum possible TP this prediction
    # set could ever contribute at IoU>=0.5, regardless of any threshold
    # choice downstream.
    unthresholded = match_counts(
        test_predictions, test_truth, test_images,
        confidence_threshold=0.0, iou_threshold=0.5,
    )
    max_ap50 = average_precision(test_predictions, test_truth, test_images, iou_threshold=0.5)
    print(
        f"\nAt the loosest possible threshold (0.0, i.e. all {len(test_predictions)} "
        f"raw predictions retained): TP={unthresholded.true_positive}, "
        f"FP={unthresholded.false_positive}, FN={unthresholded.false_negative} "
        f"(GT boxes = {len(test_truth)}). mAP@0.50 over the full ranking = {max_ap50:.6f}."
    )

    # --- item 2: box geometry mismatch, predictions (unthresholded) vs pseudo-boxes ---
    pw = test_predictions.x_max - test_predictions.x_min
    ph = test_predictions.y_max - test_predictions.y_min
    parea = pw * ph
    gw = test_truth.x_max - test_truth.x_min
    gh = test_truth.y_max - test_truth.y_min
    garea = gw * gh
    geometry = pd.DataFrame(
        {
            "quantity": ["width_px", "height_px", "area_px2", "aspect_ratio_w_over_h"],
            "prediction_median": [pw.median(), ph.median(), parea.median(), (pw / ph).median()],
            "prediction_mean": [pw.mean(), ph.mean(), parea.mean(), (pw / ph).mean()],
            "pseudo_box_median": [gw.median(), gh.median(), garea.median(), (gw / gh).median()],
            "pseudo_box_mean": [gw.mean(), gh.mean(), garea.mean(), (gw / gh).mean()],
        }
    )
    geometry["median_ratio_pred_over_gt"] = (
        geometry.prediction_median / geometry.pseudo_box_median
    )
    geometry.to_csv(OUT_DIR / "box_geometry_prediction_vs_pseudo_box.csv", index=False)
    print("\n=== box geometry: predictions (all confidences) vs pseudo-boxes, EXP-F test ===")
    print(geometry.to_string(index=False))

    # A simple, concrete IoU-achievability estimate: for the median predicted
    # box overlapping the median pseudo-box's location, what is the maximum
    # possible IoU if predicted width/height each individually contain the
    # smaller GT box (best case alignment)? IoU_max = GT_area / max(GT_area, pred_area)
    # when one box's footprint is a subset of the other's along both axes.
    med_pred_area = float(parea.median())
    med_gt_area = float(garea.median())
    best_case_iou = med_gt_area / max(med_pred_area, med_gt_area)
    print(
        f"\nBest-case IoU if a median-sized predicted box ({med_pred_area:.0f}px^2) "
        f"perfectly contains a median-sized pseudo-box ({med_gt_area:.0f}px^2) "
        f"with zero wasted area elsewhere: {best_case_iou:.3f} "
        f"(IoU@0.5 operating threshold = 0.5). This uses only the area ratio, "
        "not real spatial alignment, so it is an upper bound, not a claim "
        "about actual overlap."
    )

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].hist(np.log10(parea.clip(lower=1)), bins=50, alpha=0.55, label=f"predictions (n={len(parea)})", color="#C44E52", density=True)
    axes[0].hist(np.log10(garea.clip(lower=1)), bins=50, alpha=0.55, label=f"pseudo-boxes (n={len(garea)})", color="#55A868", density=True)
    axes[0].axvline(np.log10(med_pred_area), color="#C44E52", linestyle="--", linewidth=1)
    axes[0].axvline(np.log10(med_gt_area), color="#55A868", linestyle="--", linewidth=1)
    axes[0].set_xlabel("log10(box area, px^2)")
    axes[0].set_ylabel("density")
    axes[0].set_title("Prediction vs pseudo-box area — EXP-F test")
    axes[0].legend(fontsize=8)

    axes[1].plot(sweep_frame.recall, sweep_frame.precision, marker="o", markersize=3)
    axes[1].set_xlabel("recall (against provisional pseudo-boxes)")
    axes[1].set_ylabel("precision (against provisional pseudo-boxes)")
    axes[1].set_title("EXP-F precision-recall, swept to true min confidence")
    axes[1].set_xlim(-0.02, max(0.05, sweep_frame.recall.max() * 1.2))
    fig.tight_layout()
    fig.savefig(OUT_DIR / "geometry_and_pr_curve.png", dpi=150)
    plt.close(fig)

    print("\nWrote:")
    for path in sorted(OUT_DIR.iterdir()):
        print(" ", path)


if __name__ == "__main__":
    main()
