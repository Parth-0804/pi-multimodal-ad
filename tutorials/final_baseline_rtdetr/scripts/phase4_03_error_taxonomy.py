#!/usr/bin/env python3
"""Phase 4, item 6: concrete true-positive / false-negative example images.

The existing run's deterministic_examples.parquet was generated at
confidence 0.60, where item-1's finding shows literally zero predictions
survive for any EXP-F image, so every category in it collapses to
false_negative trivially. This regenerates real qualitative examples at
threshold=0.0 (the only threshold where true positives exist at all, per
item 1), reusing the same greedy IoU-matching definition as the rest of
this analysis (via phase4_02's per_prediction_match_labels-equivalent
logic, applied directly here since it needs the drawing step too).
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))
from pi_multimodal_ad.models.rtdetr_detection import _iou_matrix  # noqa: E402

PSEUDO_RUN = (
    REPO_ROOT / "runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794"
)
DETECTION_RUN = (
    REPO_ROOT / "runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af"
)
OUT_DIR = Path(__file__).resolve().parents[1] / "analysis" / "03_error_taxonomy"
OUT_DIR.mkdir(parents=True, exist_ok=True)

IOU_THRESHOLD = 0.5
TOP_K_PREDICTIONS_DRAWN = 40


def match_for_image(pred_group: pd.DataFrame, truth_group: pd.DataFrame) -> np.ndarray:
    ordered = pred_group.sort_values(
        ["confidence", "prediction_id"], ascending=[False, True], kind="stable"
    )
    pred_boxes = ordered[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
    truth_boxes = truth_group[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
    ious = _iou_matrix(pred_boxes, truth_boxes)
    unmatched = np.ones(len(truth_boxes), dtype=bool)
    is_match = np.zeros(len(ordered), dtype=bool)
    for position in range(len(ordered)):
        available = np.flatnonzero(unmatched)
        if not len(available):
            break
        row = ious[position]
        best_position = int(available[np.argmax(row[available])])
        if float(row[best_position]) >= IOU_THRESHOLD:
            unmatched[best_position] = False
            is_match[position] = True
    return ordered.index.to_numpy()[is_match]


def draw_example(image_path: Path, truth: pd.DataFrame, predictions: pd.DataFrame, matched_ids: set, title: str, out_path: Path) -> None:
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    for row in truth.itertuples(index=False):
        draw.rectangle((row.x_min, row.y_min, row.x_max, row.y_max), outline=(0, 200, 0), width=4)
    top = predictions.sort_values("confidence", ascending=False).head(TOP_K_PREDICTIONS_DRAWN)
    for row in top.itertuples(index=False):
        color = (255, 220, 0) if row.prediction_id in matched_ids else (230, 30, 30)
        width = 8 if row.prediction_id in matched_ids else 3
        draw.rectangle((row.x_min, row.y_min, row.x_max, row.y_max), outline=color, width=width)
    image.thumbnail((1400, 900), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1400, 960), "white")
    canvas.paste(image, ((1400 - image.width) // 2, 50))
    ImageDraw.Draw(canvas).text((10, 10), title, fill=(0, 0, 0), font=ImageFont.load_default())
    canvas.save(out_path)


def main() -> None:
    images = pd.read_parquet(PSEUDO_RUN / "tables/annotation_image_manifest.parquet")
    ground_truth = pd.read_parquet(PSEUDO_RUN / "tables/annotation_manifest.parquet")
    test_images = images[images.split == "test"].set_index("sample_id")
    test_truth = ground_truth[ground_truth.sample_id.isin(test_images.index)]
    test_predictions = pd.read_parquet(DETECTION_RUN / "tables/test_predictions.parquet")

    rows = []
    matched_ids_by_sample: dict[str, set] = {}
    for sample_id, pred_group in test_predictions.groupby("sample_id"):
        truth_group = test_truth[test_truth.sample_id == sample_id]
        matched_prediction_ids = set(match_for_image(pred_group, truth_group))
        matched_ids_by_sample[sample_id] = matched_prediction_ids
        tp = len(matched_prediction_ids)
        rows.append(
            {
                "sample_id": sample_id,
                "gt_box_count": len(truth_group),
                "prediction_count": len(pred_group),
                "true_positive_count": tp,
                "category": "true_positive_present" if tp > 0 else "false_negative_only",
            }
        )
    summary = pd.DataFrame(rows).sort_values(
        ["category", "true_positive_count"], ascending=[True, False]
    )
    summary.to_csv(OUT_DIR / "per_image_category_summary.csv", index=False)
    print(summary.category.value_counts())

    tp_examples = summary[summary.category == "true_positive_present"].head(3)
    fn_examples = summary[summary.category == "false_negative_only"].head(3)
    print(f"\n{len(tp_examples)} true-positive-present examples out of "
          f"{(summary.category == 'true_positive_present').sum()} total "
          f"({(summary.category == 'true_positive_present').sum()}/224 EXP-F images "
          "have at least one IoU>=0.5 match at threshold=0.0).")

    for _, row in pd.concat([tp_examples, fn_examples]).iterrows():
        sample_id = row.sample_id
        image_meta = test_images.loc[sample_id]
        image_path = PSEUDO_RUN / image_meta.cache_image_path
        truth = test_truth[test_truth.sample_id == sample_id]
        predictions = test_predictions[test_predictions.sample_id == sample_id]
        matched_ids = matched_ids_by_sample[sample_id]
        title = (
            f"{row.category}: {sample_id[:24]}... exp={image_meta.experiment} "
            f"run={image_meta.run} tooth={image_meta.tooth_id} | "
            f"GT boxes={row.gt_box_count} TP={row.true_positive_count} "
            f"(green=pseudo-box, yellow=matched pred (IoU>=0.5), red=top-{TOP_K_PREDICTIONS_DRAWN} unmatched pred by confidence)"
        )
        out_path = OUT_DIR / f"{row.category}_{sample_id[:16]}.jpg"
        draw_example(image_path, truth, predictions, matched_ids, title, out_path)
        print("wrote", out_path)

    print("\nWrote:")
    for path in sorted(OUT_DIR.iterdir()):
        print(" ", path)


if __name__ == "__main__":
    main()
