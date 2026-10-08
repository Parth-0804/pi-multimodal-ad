"""Genuine RT-DETR detection evaluation for provisional PHM pseudo-boxes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import time
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from ..reporting.common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
)
from ..utils.provenance import ArtifactRecord, RunContext

DETECTION_SCHEMA_VERSION = "1.0.0"
DETECTION_STATUS = "PROVISIONAL_PSEUDO_BOX_AGREEMENT_ONLY"


@dataclass(frozen=True, slots=True)
class MatchCounts:
    true_positive: int
    false_positive: int
    false_negative: int
    matched_ious: tuple[float, ...]
    false_positive_images: int
    false_negative_images: int


def box_iou(left: Sequence[float], right: Sequence[float]) -> float:
    lx0, ly0, lx1, ly1 = map(float, left)
    rx0, ry0, rx1, ry1 = map(float, right)
    ix0, iy0 = max(lx0, rx0), max(ly0, ry0)
    ix1, iy1 = min(lx1, rx1), min(ly1, ry1)
    intersection = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    left_area = max(0.0, lx1 - lx0) * max(0.0, ly1 - ly0)
    right_area = max(0.0, rx1 - rx0) * max(0.0, ry1 - ry0)
    union = left_area + right_area - intersection
    return intersection / union if union > 0 else 0.0


def _iou_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    if len(left) == 0 or len(right) == 0:
        return np.zeros((len(left), len(right)), dtype=np.float64)
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    intersection_min = np.maximum(left[:, None, :2], right[None, :, :2])
    intersection_max = np.minimum(left[:, None, 2:], right[None, :, 2:])
    intersection_wh = np.maximum(intersection_max - intersection_min, 0.0)
    intersection = intersection_wh[..., 0] * intersection_wh[..., 1]
    left_area = np.prod(np.maximum(left[:, 2:] - left[:, :2], 0.0), axis=1)
    right_area = np.prod(np.maximum(right[:, 2:] - right[:, :2], 0.0), axis=1)
    union = left_area[:, None] + right_area[None, :] - intersection
    return np.divide(
        intersection,
        union,
        out=np.zeros_like(intersection),
        where=union > 0,
    )


def _greedy_image_matches(
    predictions: pd.DataFrame,
    ground_truth: pd.DataFrame,
    *,
    confidence_threshold: float,
    iou_threshold: float,
) -> tuple[int, int, int, list[float]]:
    selected = predictions[predictions.confidence.ge(confidence_threshold)].sort_values(
        ["confidence", "prediction_id"], ascending=[False, True], kind="stable"
    )
    prediction_boxes = selected[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
    truth_boxes = ground_truth[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
    ious = _iou_matrix(prediction_boxes, truth_boxes)
    unmatched = np.ones(len(truth_boxes), dtype=bool)
    matched_ious: list[float] = []
    false_positive = 0
    for row in ious:
        available = np.flatnonzero(unmatched)
        if not len(available):
            false_positive += 1
            continue
        best_position = int(available[np.argmax(row[available])])
        best_iou = float(row[best_position])
        if best_iou >= iou_threshold:
            unmatched[best_position] = False
            matched_ious.append(best_iou)
        else:
            false_positive += 1
    return len(matched_ious), false_positive, int(unmatched.sum()), matched_ious


def match_counts(
    predictions: pd.DataFrame,
    ground_truth: pd.DataFrame,
    images: pd.DataFrame,
    *,
    confidence_threshold: float,
    iou_threshold: float = 0.5,
) -> MatchCounts:
    true_positive = false_positive = false_negative = 0
    matched_ious: list[float] = []
    false_positive_images = false_negative_images = 0
    for sample_id in images.sample_id.astype(str):
        scoped_predictions = predictions[predictions.sample_id.eq(sample_id)]
        scoped_truth = ground_truth[ground_truth.sample_id.eq(sample_id)]
        tp, fp, fn, ious = _greedy_image_matches(
            scoped_predictions,
            scoped_truth,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
        )
        true_positive += tp
        false_positive += fp
        false_negative += fn
        matched_ious.extend(ious)
        false_positive_images += int(fp > 0)
        false_negative_images += int(fn > 0)
    return MatchCounts(
        true_positive,
        false_positive,
        false_negative,
        tuple(matched_ious),
        false_positive_images,
        false_negative_images,
    )


def average_precision(
    predictions: pd.DataFrame,
    ground_truth: pd.DataFrame,
    images: pd.DataFrame,
    *,
    iou_threshold: float,
) -> float:
    total_truth = len(ground_truth)
    if total_truth == 0:
        return float("nan")
    truth_by_image = {
        str(sample_id): group[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
        for sample_id, group in ground_truth.groupby("sample_id")
    }
    matched = {
        str(sample_id): np.zeros(
            len(truth_by_image.get(str(sample_id), ())), dtype=bool
        )
        for sample_id in images.sample_id.astype(str)
    }
    ordered = predictions.sort_values(
        ["confidence", "prediction_id"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    iou_rows: dict[int, np.ndarray] = {}
    for sample_id, group in ordered.groupby("sample_id", sort=False):
        prediction_boxes = group[["x_min", "y_min", "x_max", "y_max"]].to_numpy()
        matrix = _iou_matrix(
            prediction_boxes, truth_by_image.get(str(sample_id), np.empty((0, 4)))
        )
        for position, order_index in enumerate(group.index):
            iou_rows[int(order_index)] = matrix[position]
    tp: list[int] = []
    fp: list[int] = []
    for order_index, row in ordered.iterrows():
        sample_id = str(row.sample_id)
        available = np.flatnonzero(~matched[sample_id])
        ious = iou_rows[int(order_index)]
        if len(available):
            best_index = int(available[np.argmax(ious[available])])
            is_match = float(ious[best_index]) >= iou_threshold
        else:
            best_index = -1
            is_match = False
        if is_match:
            matched[sample_id][best_index] = True
        tp.append(int(is_match))
        fp.append(int(not is_match))
    if not tp:
        return 0.0
    cumulative_tp = np.cumsum(tp)
    cumulative_fp = np.cumsum(fp)
    recall = cumulative_tp / total_truth
    precision = cumulative_tp / np.maximum(cumulative_tp + cumulative_fp, 1)
    recall_grid = np.linspace(0.0, 1.0, 101)
    interpolated = [
        float(precision[recall >= value].max()) if np.any(recall >= value) else 0.0
        for value in recall_grid
    ]
    return float(np.mean(interpolated))


def metrics_at_threshold(
    predictions: pd.DataFrame,
    ground_truth: pd.DataFrame,
    images: pd.DataFrame,
    *,
    confidence_threshold: float,
    scope: str = "all",
    compute_ap: bool = True,
) -> dict[str, Any]:
    counts = match_counts(
        predictions,
        ground_truth,
        images,
        confidence_threshold=confidence_threshold,
        iou_threshold=0.5,
    )
    precision = counts.true_positive / max(
        counts.true_positive + counts.false_positive, 1
    )
    recall = counts.true_positive / max(counts.true_positive + counts.false_negative, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    map50 = (
        average_precision(predictions, ground_truth, images, iou_threshold=0.5)
        if compute_ap
        else float("nan")
    )
    aps = (
        [
            average_precision(
                predictions, ground_truth, images, iou_threshold=float(threshold)
            )
            for threshold in np.linspace(0.5, 0.95, 10)
        ]
        if compute_ap
        else []
    )
    finite_aps = [value for value in aps if np.isfinite(value)]
    return {
        "schema_version": DETECTION_SCHEMA_VERSION,
        "status": DETECTION_STATUS,
        "scope": scope,
        "image_count": len(images),
        "ground_truth_box_count": len(ground_truth),
        "prediction_count_all_confidences": len(predictions),
        "confidence_threshold": confidence_threshold,
        "iou_operating_threshold": 0.5,
        "true_positive": counts.true_positive,
        "false_positive": counts.false_positive,
        "false_negative": counts.false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "map50": map50,
        "map50_95": float(np.mean(finite_aps)) if finite_aps else float("nan"),
        "mean_matched_iou": (
            float(np.mean(counts.matched_ious)) if counts.matched_ious else float("nan")
        ),
        "false_positive_images": counts.false_positive_images,
        "false_negative_images": counts.false_negative_images,
        "metric_interpretation": "agreement with provisional pseudo-boxes, not physical damage accuracy",
    }


def select_confidence_threshold(
    predictions: pd.DataFrame,
    ground_truth: pd.DataFrame,
    images: pd.DataFrame,
    *,
    candidates: Iterable[float],
) -> tuple[float, pd.DataFrame]:
    rows = [
        metrics_at_threshold(
            predictions,
            ground_truth,
            images,
            confidence_threshold=float(value),
            scope="validation_threshold_selection",
            compute_ap=False,
        )
        for value in candidates
    ]
    frame = pd.DataFrame(rows)
    selected = frame.sort_values(
        ["f1", "confidence_threshold"], ascending=[False, False], kind="stable"
    ).iloc[0]
    return float(selected.confidence_threshold), frame


def sliced_metrics(
    predictions: pd.DataFrame,
    ground_truth: pd.DataFrame,
    images: pd.DataFrame,
    *,
    confidence_threshold: float,
) -> pd.DataFrame:
    rows = [
        metrics_at_threshold(
            predictions,
            ground_truth,
            images,
            confidence_threshold=confidence_threshold,
            scope="all",
        )
    ]
    for view_role, scoped_images in images.groupby("view_role"):
        ids = set(scoped_images.sample_id.astype(str))
        rows.append(
            metrics_at_threshold(
                predictions[predictions.sample_id.isin(ids)],
                ground_truth[ground_truth.sample_id.isin(ids)],
                scoped_images,
                confidence_threshold=confidence_threshold,
                scope=f"view_role:{view_role}",
            )
        )
    for run, scoped_images in images.groupby("run"):
        ids = set(scoped_images.sample_id.astype(str))
        rows.append(
            metrics_at_threshold(
                predictions[predictions.sample_id.isin(ids)],
                ground_truth[ground_truth.sample_id.isin(ids)],
                scoped_images,
                confidence_threshold=confidence_threshold,
                scope=f"run:{int(run)}",
                compute_ap=False,
            )
        )
    return pd.DataFrame(rows)


def collect_predictions(
    model: Any,
    images: pd.DataFrame,
    *,
    pseudo_run_directory: Path,
    image_size: int,
    batch_size: int,
    device: int | str,
    minimum_confidence: float = 0.001,
    max_detections: int = 300,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ordered = images.sort_values("sample_id", kind="stable")
    paths = [
        str(pseudo_run_directory / relative) for relative in ordered.cache_image_path
    ]
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    latency_rows: list[dict[str, Any]] = []
    ordered_rows = list(ordered.itertuples(index=False))
    for start in range(0, len(paths), batch_size):
        chunk_paths = paths[start : start + batch_size]
        chunk_rows = ordered_rows[start : start + batch_size]
        results = model.predict(
            source=chunk_paths,
            imgsz=image_size,
            batch=batch_size,
            device=device,
            conf=minimum_confidence,
            max_det=max_detections,
            verbose=False,
            stream=False,
        )
        for image_row, result in zip(chunk_rows, results, strict=True):
            speed = dict(result.speed)
            latency_rows.append(
                {
                    "sample_id": image_row.sample_id,
                    "preprocess_ms": float(speed.get("preprocess", 0.0)),
                    "inference_ms": float(speed.get("inference", 0.0)),
                    "postprocess_ms": float(speed.get("postprocess", 0.0)),
                    "total_ms": float(sum(speed.values())),
                }
            )
            if result.boxes is None:
                continue
            xyxy = result.boxes.xyxy.detach().cpu().numpy()
            confidence = result.boxes.conf.detach().cpu().numpy()
            classes = result.boxes.cls.detach().cpu().numpy().astype(int)
            for position, (box, score, class_id) in enumerate(
                zip(xyxy, confidence, classes, strict=True)
            ):
                rows.append(
                    {
                        "schema_version": DETECTION_SCHEMA_VERSION,
                        "prediction_id": f"{image_row.sample_id}:{position:04d}",
                        "sample_id": image_row.sample_id,
                        "image_id": image_row.image_id,
                        "experiment": image_row.experiment,
                        "run": int(image_row.run),
                        "tooth_id": int(image_row.tooth_id),
                        "view_role": image_row.view_role,
                        "split": image_row.split,
                        "class_id": int(class_id),
                        "class_name": "damage_candidate",
                        "confidence": float(score),
                        "x_min": float(box[0]),
                        "y_min": float(box[1]),
                        "x_max": float(box[2]),
                        "y_max": float(box[3]),
                        "status": DETECTION_STATUS,
                    }
                )
    latency = pd.DataFrame(latency_rows)
    latency.attrs["elapsed_seconds"] = time.perf_counter() - started
    prediction_columns = (
        "schema_version",
        "prediction_id",
        "sample_id",
        "image_id",
        "experiment",
        "run",
        "tooth_id",
        "view_role",
        "split",
        "class_id",
        "class_name",
        "confidence",
        "x_min",
        "y_min",
        "x_max",
        "y_max",
        "status",
    )
    return pd.DataFrame(rows, columns=prediction_columns), latency


def deterministic_example_rows(
    predictions: pd.DataFrame,
    ground_truth: pd.DataFrame,
    images: pd.DataFrame,
    *,
    confidence_threshold: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for image in images.sort_values("sample_id").itertuples(index=False):
        p = predictions[predictions.sample_id.eq(image.sample_id)]
        g = ground_truth[ground_truth.sample_id.eq(image.sample_id)]
        tp, fp, fn, ious = _greedy_image_matches(
            p,
            g,
            confidence_threshold=confidence_threshold,
            iou_threshold=0.5,
        )
        if fn:
            category = "false_negative"
        elif fp:
            category = "false_positive"
        elif tp:
            category = "true_positive"
        else:
            category = "true_negative"
        rows.append(
            {
                "sample_id": image.sample_id,
                "experiment": image.experiment,
                "run": int(image.run),
                "tooth_id": int(image.tooth_id),
                "view_role": image.view_role,
                "category": category,
                "true_positive": tp,
                "false_positive": fp,
                "false_negative": fn,
                "mean_matched_iou": float(np.mean(ious)) if ious else np.nan,
                "selection_rule": "stable first sample_id per outcome category",
                "cache_image_path": image.cache_image_path,
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values(["category", "sample_id"], kind="stable")
        .groupby("category", as_index=False)
        .head(4)
        .reset_index(drop=True)
    )


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv_path = stem.with_suffix(".csv")
    parquet_path = stem.with_suffix(".parquet")
    frame.to_csv(csv_path, index=False)
    frame.to_parquet(parquet_path, index=False)
    return [csv_path, parquet_path]


def write_detection_results(
    *,
    run: RunContext,
    validation_predictions: pd.DataFrame,
    test_predictions: pd.DataFrame,
    validation_thresholds: pd.DataFrame,
    test_metrics: pd.DataFrame,
    latency: pd.DataFrame,
    history: pd.DataFrame,
    tensor_shapes: pd.DataFrame,
    examples: pd.DataFrame,
    ap_by_iou: pd.DataFrame,
    pseudo_run_directory: Path,
    confidence_threshold: float,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
    environment: Mapping[str, Any],
    extra_artifacts: Sequence[tuple[Path, str]] = (),
) -> list[ArtifactRecord]:
    artifacts: list[ArtifactRecord] = []
    frames = {
        "validation_predictions": validation_predictions,
        "test_predictions": test_predictions,
        "validation_threshold_selection": validation_thresholds,
        "detection_metrics": test_metrics,
        "latency": latency,
        "training_history": history,
        "tensor_shapes": tensor_shapes,
        "deterministic_examples": examples,
        "ap_by_iou_threshold": ap_by_iou,
    }
    for name, frame in frames.items():
        for path in _write_frame(frame, run.run_directory / "tables" / name):
            artifacts.append(run.artifact(path, role=name))
    config_path = run.write_resolved_config(resolved_config)
    input_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        (
            run.artifact(config_path, role="resolved_config"),
            run.artifact(input_path, role="input_manifest"),
        )
    )
    environment_path = run.run_directory / "reports/environment_device.json"
    environment_path.write_text(json_text(dict(environment)), encoding="utf-8")
    artifacts.append(run.artifact(environment_path, role="environment_device"))
    apply_academic_style()
    figure_sources = {
        "training_validation_losses": history.copy(),
        "precision_recall_curve": validation_thresholds[
            ["confidence_threshold", "precision", "recall", "f1"]
        ].copy(),
        "map_by_iou_threshold": ap_by_iou.copy(),
        "latency_distribution": latency.copy(),
    }
    for name, source in figure_sources.items():
        for path in _write_frame(
            source, run.run_directory / "tables" / f"plot_source_{name}"
        ):
            artifacts.append(run.artifact(path, role="plot_source"))
    if not history.empty:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for column in [name for name in history if "loss" in name.lower()]:
            ax.plot(history.index + 1, history[column], label=column)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Ultralytics loss")
        ax.set_title("Genuine RT-DETR training and validation losses")
        ax.legend(fontsize=7)
        for path in save_figure_pair(
            fig, run.run_directory / "figures/training_validation_losses"
        ):
            artifacts.append(run.artifact(path, role="figure"))
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(validation_thresholds.recall, validation_thresholds.precision, marker="o")
    ax.scatter(
        validation_thresholds.loc[
            validation_thresholds.confidence_threshold.eq(confidence_threshold),
            "recall",
        ],
        validation_thresholds.loc[
            validation_thresholds.confidence_threshold.eq(confidence_threshold),
            "precision",
        ],
        color=ACADEMIC_COLORS[4],
        label=f"selected conf={confidence_threshold:.3f}",
    )
    ax.set_xlabel("Recall against provisional pseudo-boxes")
    ax.set_ylabel("Precision against provisional pseudo-boxes")
    ax.set_title("Validation precision–recall operating curve")
    ax.legend()
    for path in save_figure_pair(
        fig, run.run_directory / "figures/precision_recall_curve"
    ):
        artifacts.append(run.artifact(path, role="figure"))
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        ap_by_iou.iou_threshold,
        ap_by_iou.average_precision,
        marker="o",
        color=ACADEMIC_COLORS[1],
    )
    ax.set_xlabel("IoU threshold")
    ax.set_ylabel("Average precision")
    ax.set_title("EXP-F AP by IoU threshold (pseudo-label agreement)")
    ax.set_xlim(0.49, 0.96)
    ax.set_ylim(bottom=0.0)
    for path in save_figure_pair(
        fig, run.run_directory / "figures/map_by_iou_threshold"
    ):
        artifacts.append(run.artifact(path, role="figure"))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(latency.inference_ms, bins=30, color=ACADEMIC_COLORS[0])
    ax.set_xlabel("Inference latency per image (ms)")
    ax.set_ylabel("Images")
    ax.set_title("EXP-F genuine RT-DETR inference latency")
    for path in save_figure_pair(
        fig, run.run_directory / "figures/latency_distribution"
    ):
        artifacts.append(run.artifact(path, role="figure"))
    montage = Image.new("RGB", (1280, max(1, len(examples)) * 360), "white")
    for position, row in enumerate(examples.itertuples(index=False)):
        with Image.open(pseudo_run_directory / row.cache_image_path) as source:
            image = source.convert("RGB")
        draw = ImageDraw.Draw(image)
        for truth in resolved_config["example_ground_truth"].get(row.sample_id, []):
            draw.rectangle(tuple(truth), outline=(0, 220, 100), width=8)
        selected = test_predictions[
            test_predictions.sample_id.eq(row.sample_id)
            & test_predictions.confidence.ge(confidence_threshold)
        ]
        for prediction in selected.itertuples(index=False):
            draw.rectangle(
                (
                    prediction.x_min,
                    prediction.y_min,
                    prediction.x_max,
                    prediction.y_max,
                ),
                outline=(255, 40, 40),
                width=8,
            )
        image.thumbnail((1280, 320), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (1280, 360), "white")
        canvas.paste(image, ((1280 - image.width) // 2, 36))
        ImageDraw.Draw(canvas).text(
            (8, 8),
            f"{row.category}: {row.sample_id} green=pseudo-label red=prediction",
            fill=(0, 0, 0),
            font=ImageFont.load_default(),
        )
        montage.paste(canvas, (0, position * 360))
    montage_path = run.run_directory / "figures/deterministic_detection_examples.png"
    montage.save(montage_path, dpi=(300, 300))
    artifacts.append(
        run.artifact(montage_path, role="deterministic_detection_examples")
    )
    for path, role in extra_artifacts:
        artifacts.append(run.artifact(path, role=role))
    report_path = run.run_directory / "reports/rtdetr_detection_report.md"
    overall = test_metrics[test_metrics.scope.eq("all")].iloc[0]
    report_path.write_text(
        "# Genuine RT-DETR damage-candidate detector\n\n"
        "> Bounding boxes are pseudo-boxes derived from provisional masks. All metrics measure pseudo-label agreement, not physical-damage validity.\n\n"
        f"The one-class RT-DETR detector was selected using EXP-A validation only and evaluated once on EXP-F at confidence {confidence_threshold:.4f}. EXP-F represents an acquisition-protocol/domain shift. Overall test N={int(overall.image_count)} images: precision={overall.precision:.4f}, recall={overall.recall:.4f}, F1={overall.f1:.4f}, mAP@0.50={overall.map50:.4f}, mAP@0.50:0.95={overall.map50_95:.4f}. Full RT-DETR detection retains the backbone, multiscale encoder, transformer decoder/object queries, class head and box head; it is different from the earlier frozen-encoder scalar regression. Physical validity requires expert review.\n",
        encoding="utf-8",
    )
    artifacts.append(run.artifact(report_path, role="detection_report"))
    return finalize_run(run, artifacts)
