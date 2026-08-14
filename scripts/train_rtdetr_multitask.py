#!/usr/bin/env python3
"""Train and evaluate genuine RT-DETR detection plus a shared scalar head."""

from __future__ import annotations

import argparse
import copy
import gc
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader
from ultralytics import RTDETR
import ultralytics

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pi_multimodal_ad.evaluation.regression import regression_metrics  # noqa: E402
from pi_multimodal_ad.models.rtdetr_detection import (  # noqa: E402
    average_precision,
    deterministic_example_rows,
    select_confidence_threshold,
    sliced_metrics,
)
from pi_multimodal_ad.models.rtdetr_multitask import (  # noqa: E402
    MULTITASK_STATUS,
    PseudoBoxScalarDataset,
    RTDETRMultitask,
    collate_multitask,
    move_multitask_batch,
    normalized_rtdetr_predictions,
)
from pi_multimodal_ad.models.rtdetr_regression import (  # noqa: E402
    aggregate_predictions,
)
from pi_multimodal_ad.reporting.common import (  # noqa: E402
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
)
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
    set_reproducible_seed,
)


def _device_information() -> dict[str, Any]:
    try:
        nvidia = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free,driver_version",
                "--format=csv,noheader",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        nvidia = "unavailable"
    return {
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "ultralytics_version": ultralytics.__version__,
        "nvidia_smi": nvidia,
    }


def _loader(
    frame: pd.DataFrame,
    *,
    pseudo_directory: Path,
    image_size: int,
    batch_size: int,
    workers: int,
    augment: bool,
    seed: int,
    shuffle: bool,
) -> DataLoader:
    dataset = PseudoBoxScalarDataset(
        frame,
        run_directory=pseudo_directory,
        image_size=image_size,
        augment=augment,
        seed=seed,
    )
    generator = torch.Generator().manual_seed(seed)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=workers,
        collate_fn=collate_multitask,
        generator=generator,
        pin_memory=True,
        persistent_workers=workers > 0,
    )


def _model(checkpoint: Path, config: dict[str, Any], device: torch.device):
    detector = RTDETR(str(checkpoint)).model.to(device)
    model = RTDETRMultitask(
        detector,
        feature_layer=int(config["feature_layer"]),
        feature_dimension=int(config["feature_dimension"]),
        hidden_dimension=int(config["scalar_hidden_dimension"]),
        dropout=float(config["scalar_dropout"]),
    ).to(device)
    return model


def _set_training_mode(model: RTDETRMultitask, frozen_layers: int) -> None:
    model.train()
    for layer in model.detector.model[:frozen_layers]:
        layer.eval()


def _gradient_norm(gradients: tuple[torch.Tensor | None, ...]) -> float:
    finite = [
        value.detach().float().norm().square()
        for value in gradients
        if value is not None
    ]
    if not finite:
        return 0.0
    return float(torch.stack(finite).sum().sqrt().cpu())


def _balance_lambda(
    model: RTDETRMultitask,
    batch: dict[str, Any],
    *,
    target_mean: float,
    target_scale: float,
    minimum: float,
    maximum: float,
) -> dict[str, float]:
    model.zero_grad(set_to_none=True)
    result = model.training_loss(
        batch,
        target_mean=target_mean,
        target_scale=target_scale,
        lambda_regression=1.0,
    )
    shared = tuple(
        parameter
        for parameter in model.detector.parameters()
        if parameter.requires_grad
    )
    detection_gradient = torch.autograd.grad(
        result.detection, shared, retain_graph=True, allow_unused=True
    )
    regression_gradient = torch.autograd.grad(
        result.regression, shared, retain_graph=False, allow_unused=True
    )
    detection_norm = _gradient_norm(detection_gradient)
    regression_norm = _gradient_norm(regression_gradient)
    if not np.isfinite(regression_norm) or regression_norm <= 0:
        raise RuntimeError("scalar loss has no finite gradient into the shared encoder")
    raw = detection_norm / regression_norm
    selected = float(np.clip(raw, minimum, maximum))
    model.zero_grad(set_to_none=True)
    return {
        "detection_loss": float(result.detection.detach().cpu()),
        "regression_loss": float(result.regression.detach().cpu()),
        "detection_shared_gradient_norm": detection_norm,
        "regression_shared_gradient_norm": regression_norm,
        "raw_gradient_balance_ratio": raw,
        "lambda_regression": selected,
        "selection_evidence": "first deterministic EXP-B training batch only",
    }


def _tiny_overfit(
    model: RTDETRMultitask,
    batch: dict[str, Any],
    *,
    target_mean: float,
    target_scale: float,
    steps: int,
    learning_rate: float,
) -> dict[str, float]:
    initial_state = copy.deepcopy(model.scalar_head.state_dict())
    model.eval()
    with torch.no_grad():
        model._feature = None
        model.detector.predict(batch["img"])
        feature = model._feature.detach()
    target_scaled = (
        batch["scalar_target"].to(feature.dtype) - target_mean
    ) / target_scale
    optimizer = torch.optim.AdamW(model.scalar_head.parameters(), lr=learning_rate)
    model.scalar_head.train()
    with torch.no_grad():
        initial = float(F.smooth_l1_loss(model.scalar_head(feature), target_scaled))
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = F.smooth_l1_loss(model.scalar_head(feature), target_scaled)
        loss.backward()
        optimizer.step()
    model.scalar_head.eval()
    with torch.no_grad():
        final = float(F.smooth_l1_loss(model.scalar_head(feature), target_scaled))
    model.scalar_head.load_state_dict(initial_state)
    if not final < initial:
        raise RuntimeError("tiny-batch scalar overfit did not reduce regression loss")
    return {
        "steps": steps,
        "initial_smooth_l1": initial,
        "final_smooth_l1": final,
        "used_exp_f": False,
    }


def _epoch(
    model: RTDETRMultitask,
    loader: DataLoader,
    *,
    device: torch.device,
    target_mean: float,
    target_scale: float,
    lambda_regression: float,
    optimizer: torch.optim.Optimizer | None,
    scaler: torch.amp.GradScaler | None,
    frozen_layers: int,
    gradient_clip_norm: float,
    amp: bool,
) -> dict[str, float]:
    training = optimizer is not None
    if training:
        _set_training_mode(model, frozen_layers)
    else:
        model.eval()
    values: list[tuple[float, float, float]] = []
    context = torch.enable_grad if training else torch.no_grad
    with context():
        for cpu_batch in loader:
            batch = move_multitask_batch(cpu_batch, device)
            if training:
                optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=amp):
                result = model.training_loss(
                    batch,
                    target_mean=target_mean,
                    target_scale=target_scale,
                    lambda_regression=lambda_regression,
                )
            if training:
                assert scaler is not None
                scaler.scale(result.total).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(
                    [
                        parameter
                        for parameter in model.parameters()
                        if parameter.requires_grad
                    ],
                    gradient_clip_norm,
                )
                scaler.step(optimizer)
                scaler.update()
            values.append(
                (
                    float(result.total.detach().cpu()),
                    float(result.detection.detach().cpu()),
                    float(result.regression.detach().cpu()),
                )
            )
    array = np.asarray(values, dtype=np.float64)
    return {
        "total": float(array[:, 0].mean()),
        "detection": float(array[:, 1].mean()),
        "regression": float(array[:, 2].mean()),
        "batch_count": int(len(array)),
    }


def _predict(
    model: RTDETRMultitask,
    loader: DataLoader,
    *,
    device: torch.device,
    target_mean: float,
    target_scale: float,
    confidence: float,
    maximum_detections: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    model.eval()
    detection_rows: list[dict[str, Any]] = []
    scalar_rows: list[dict[str, Any]] = []
    latency_rows: list[dict[str, Any]] = []
    with torch.no_grad():
        for cpu_batch in loader:
            batch = move_multitask_batch(cpu_batch, device)
            torch.cuda.synchronize()
            started = time.perf_counter()
            detection, scalar = model.inference(
                batch["img"], target_mean=target_mean, target_scale=target_scale
            )
            torch.cuda.synchronize()
            per_image_ms = (
                (time.perf_counter() - started) * 1000 / len(batch["metadata"])
            )
            detection_rows.extend(
                normalized_rtdetr_predictions(
                    detection,
                    batch["metadata"],
                    confidence_threshold=confidence,
                    maximum_detections=maximum_detections,
                )
            )
            truth = cpu_batch["scalar_target"].numpy()
            predicted = scalar.detach().cpu().numpy()
            for identity, y_true, y_pred in zip(
                batch["metadata"], truth, predicted, strict=True
            ):
                scalar_rows.append(
                    {
                        "sample_id": identity["sample_id"],
                        "image_id": identity["image_id"],
                        "experiment": identity["experiment"],
                        "run": identity["run"],
                        "tooth_id": identity["tooth_id"],
                        "view_role": identity["view_role"],
                        "split": identity["split"],
                        "y_true_raw": float(y_true),
                        "y_pred": float(y_pred),
                        "physical_unit": "percent_visible_flank_candidate_area",
                        "target_definition_version": identity[
                            "target_definition_version"
                        ],
                        "target_verification_status": identity[
                            "target_verification_status"
                        ],
                        "model_name": "multitask_rtdetr_detector_scalar_head",
                        "status": MULTITASK_STATUS,
                        "latency_ms": per_image_ms,
                        "source_archive": identity["source_archive"],
                        "source_member": identity["source_member"],
                    }
                )
                latency_rows.append(
                    {
                        "sample_id": identity["sample_id"],
                        "split": identity["split"],
                        "experiment": identity["experiment"],
                        "latency_ms": per_image_ms,
                    }
                )
    detection_columns = (
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
        "batch_image_index",
    )
    return (
        pd.DataFrame(detection_rows, columns=detection_columns),
        pd.DataFrame(scalar_rows),
        pd.DataFrame(latency_rows),
    )


def _metric_rows(
    predictions: pd.DataFrame,
    tooth: pd.DataFrame,
    runs: pd.DataFrame,
    *,
    model_name: str,
    repetitions: int,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for level, frame, true_column, prediction_column in (
        ("image_view", predictions, "y_true_raw", "y_pred"),
        ("tooth", tooth, "y_true_raw", "y_pred"),
        ("run_raw_top3", runs, "y_true_raw_top3_mean", "y_pred_raw_top3_mean"),
        (
            "run_monotonic_top3",
            runs,
            "y_true_monotonic_top3_mean",
            "y_pred_monotonic_top3_mean",
        ),
    ):
        for (split, experiment), scoped in frame.groupby(["split", "experiment"]):
            metrics = regression_metrics(scoped[true_column], scoped[prediction_column])
            generator = np.random.default_rng(seed)
            run_ids = np.asarray(sorted(scoped.run.unique()))
            bootstrap = []
            for _ in range(repetitions):
                selected = generator.choice(run_ids, size=len(run_ids), replace=True)
                truth_values: list[float] = []
                prediction_values: list[float] = []
                for run_id in selected:
                    part = scoped[scoped.run.eq(run_id)]
                    truth_values.extend(part[true_column].astype(float))
                    prediction_values.extend(part[prediction_column].astype(float))
                bootstrap.append(
                    float(
                        np.mean(
                            np.abs(
                                np.asarray(prediction_values) - np.asarray(truth_values)
                            )
                        )
                    )
                )
            rows.append(
                {
                    "model_name": model_name,
                    "evaluation_level": level,
                    "split": split,
                    "experiment": experiment,
                    "unit": "percentage_points_visible_flank_candidate_area",
                    **metrics,
                    "mae_run_grouped_ci95_low": float(np.quantile(bootstrap, 0.025)),
                    "mae_run_grouped_ci95_high": float(np.quantile(bootstrap, 0.975)),
                    "bootstrap_repetitions": repetitions,
                }
            )
    return pd.DataFrame(rows)


def _naive_predictions(
    images: pd.DataFrame, *, target_value: float, model_name: str
) -> pd.DataFrame:
    scoped = images[images.split.isin(["validation", "test"])].copy()
    return pd.DataFrame(
        {
            "sample_id": scoped.sample_id,
            "image_id": scoped.image_id,
            "experiment": scoped.experiment,
            "run": scoped.run.astype(int),
            "tooth_id": scoped.tooth_id.astype(int),
            "split": scoped.split,
            "y_true_raw": scoped.target_value_pct.astype(float),
            "y_pred": float(target_value),
            "model_name": model_name,
        }
    )


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv = stem.with_suffix(".csv")
    parquet = stem.with_suffix(".parquet")
    frame.to_csv(csv, index=False)
    frame.to_parquet(parquet, index=False)
    return [csv, parquet]


def _write_results(
    *,
    run,
    model: RTDETRMultitask,
    best_state: dict[str, torch.Tensor],
    last_state: dict[str, torch.Tensor],
    frames: dict[str, pd.DataFrame],
    resolved: dict[str, Any],
    inputs: list[dict[str, Any]],
    environment: dict[str, Any],
    pseudo_directory: Path,
    selected_confidence: float,
) -> list[Any]:
    artifacts = []
    config_path = run.write_resolved_config(resolved)
    input_path = run.write_input_manifest(inputs)
    artifacts.extend(
        [
            run.artifact(config_path, role="resolved_configuration"),
            run.artifact(input_path, role="input_manifest"),
        ]
    )
    checkpoint_directory = run.run_directory / "checkpoints"
    checkpoint_directory.mkdir(exist_ok=True)
    metadata = {
        "target_mean": resolved["target_scaler"]["mean"],
        "target_scale": resolved["target_scaler"]["scale"],
        "feature_layer": resolved["model"]["feature_layer"],
        "status": MULTITASK_STATUS,
    }
    for name, state in (("best_multitask", best_state), ("last_multitask", last_state)):
        path = checkpoint_directory / f"{name}.pt"
        torch.save({"model_state_dict": state, "metadata": metadata}, path)
        artifacts.append(run.artifact(path, role=f"{name}_checkpoint"))
    environment_path = run.run_directory / "reports/environment_device.json"
    environment_path.write_text(json_text(environment), encoding="utf-8")
    artifacts.append(run.artifact(environment_path, role="environment_device"))
    for name, frame in frames.items():
        for path in _write_frame(frame, run.run_directory / "tables" / name):
            artifacts.append(run.artifact(path, role=name))
    apply_academic_style()
    history = frames["training_history"]
    scalar = frames["scalar_predictions"]
    test_scalar = scalar[scalar.split.eq("test")].copy()
    test_runs = frames["run_predictions"]
    comparison = frames["level_matched_model_comparison"]
    latency = frames["latency"]
    threshold = frames["validation_threshold_selection"]
    ap = frames["ap_by_iou_threshold"]
    figure_sources: dict[str, pd.DataFrame] = {}
    figures: dict[str, plt.Figure] = {}

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, name in zip(axes, ("total", "detection", "regression"), strict=True):
        ax.plot(history.epoch, history[f"train_{name}_loss"], label="train")
        ax.plot(history.epoch, history[f"validation_{name}_loss"], label="validation")
        ax.set(title=name.capitalize(), xlabel="Epoch", ylabel="Loss")
        ax.legend()
    fig.suptitle("Multitask RT-DETR loss components")
    figures["training_validation_losses"] = fig
    figure_sources["training_validation_losses"] = history

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(test_scalar.y_true_raw, test_scalar.y_pred, s=16, alpha=0.55)
    low = min(test_scalar.y_true_raw.min(), test_scalar.y_pred.min())
    high = max(test_scalar.y_true_raw.max(), test_scalar.y_pred.max())
    ax.plot([low, high], [low, high], "--", color="black")
    ax.set(
        title="EXP-F per-view provisional target agreement",
        xlabel="Pseudo-target candidate area (%)",
        ylabel="Multitask prediction (%)",
    )
    figures["prediction_vs_target"] = fig
    figure_sources["prediction_vs_target"] = test_scalar

    residual = test_scalar.assign(residual=test_scalar.y_pred - test_scalar.y_true_raw)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(residual.residual, bins=25, color=ACADEMIC_COLORS[1])
    ax.set(
        title="EXP-F residual distribution",
        xlabel="Prediction − provisional pseudo-target (percentage points)",
        ylabel="Views",
    )
    figures["residual_distribution"] = fig
    figure_sources["residual_distribution"] = residual

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(residual.y_pred, residual.residual, s=16, alpha=0.55)
    ax.axhline(0, linestyle="--", color="black")
    ax.set(
        title="EXP-F residual versus prediction",
        xlabel="Prediction (%)",
        ylabel="Residual (percentage points)",
    )
    figures["residual_vs_prediction"] = fig
    figure_sources["residual_vs_prediction"] = residual

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        test_runs.run,
        test_runs.y_true_raw_top3_mean,
        marker="o",
        label="pseudo-target raw top-3",
    )
    ax.plot(
        test_runs.run,
        test_runs.y_pred_raw_top3_mean,
        marker="x",
        label="multitask raw top-3",
    )
    ax.plot(
        test_runs.run,
        test_runs.y_true_monotonic_top3_mean,
        linestyle="--",
        label="pseudo-target monotonic",
    )
    ax.plot(
        test_runs.run,
        test_runs.y_pred_monotonic_top3_mean,
        linestyle=":",
        label="prediction monotonic",
    )
    ax.set(title="EXP-F run trajectory", xlabel="Run", ylabel="Candidate area (%)")
    ax.legend(fontsize=8)
    figures["exp_f_run_trajectory"] = fig
    figure_sources["exp_f_run_trajectory"] = test_runs

    scoped_comparison = comparison[
        comparison.split.eq("test")
        & comparison.evaluation_level.isin(["image_view", "run_raw_top3"])
    ].copy()
    fig, ax = plt.subplots(figsize=(11, 5))
    labels = scoped_comparison.model_name + "\n" + scoped_comparison.evaluation_level
    ax.bar(labels, scoped_comparison.mae, color=ACADEMIC_COLORS[0])
    ax.set(title="Level-matched EXP-F MAE comparison", ylabel="MAE (percentage points)")
    ax.tick_params(axis="x", rotation=35, labelsize=7)
    figures["level_matched_model_comparison"] = fig
    figure_sources["level_matched_model_comparison"] = scoped_comparison

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(
        latency[latency.split.eq("test")].latency_ms, bins=25, color=ACADEMIC_COLORS[2]
    )
    ax.set(
        title="EXP-F joint inference latency",
        xlabel="Milliseconds/image",
        ylabel="Images",
    )
    figures["latency_distribution"] = fig
    figure_sources["latency_distribution"] = latency

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(threshold.recall, threshold.precision, marker="o")
    ax.set(
        title="EXP-A pseudo-box precision–recall", xlabel="Recall", ylabel="Precision"
    )
    figures["precision_recall_curve"] = fig
    figure_sources["precision_recall_curve"] = threshold

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(ap.iou_threshold, ap.average_precision, marker="o")
    ax.set(
        title="EXP-F AP by IoU (pseudo-label agreement)",
        xlabel="IoU threshold",
        ylabel="AP",
    )
    figures["map_by_iou_threshold"] = fig
    figure_sources["map_by_iou_threshold"] = ap

    tensor_shapes = frames["tensor_shapes"]
    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.axis("off")
    for index, row in enumerate(tensor_shapes.itertuples(index=False)):
        x = 0.02 + index * 0.19
        ax.add_patch(
            plt.Rectangle(
                (x, 0.32),
                0.16,
                0.36,
                transform=ax.transAxes,
                facecolor="#EAF0F5",
                edgecolor=ACADEMIC_COLORS[0],
            )
        )
        ax.text(
            x + 0.08,
            0.5,
            f"{row.stage}\n{row.shape}",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=8,
        )
    ax.set_title("Genuine RT-DETR detection plus shared encoder scalar head")
    figures["architecture_tensor_shapes"] = fig
    figure_sources["architecture_tensor_shapes"] = tensor_shapes

    for name, figure in figures.items():
        for path in _write_frame(
            figure_sources[name], run.run_directory / "tables" / f"plot_source_{name}"
        ):
            artifacts.append(run.artifact(path, role=f"plot_source_{name}"))
        for path in save_figure_pair(figure, run.run_directory / "figures" / name):
            artifacts.append(run.artifact(path, role=f"figure_{name}"))

    examples = frames["deterministic_examples"]
    truth = frames["test_ground_truth"]
    predictions = frames["test_detection_predictions"]
    montage = Image.new("RGB", (1280, max(1, len(examples)) * 350), "white")
    for position, row in enumerate(examples.itertuples(index=False)):
        image_row = frames["test_images"][
            frames["test_images"].sample_id.eq(row.sample_id)
        ].iloc[0]
        with Image.open(pseudo_directory / image_row.cache_image_path) as source:
            image = source.convert("RGB")
        draw = ImageDraw.Draw(image)
        for box in truth[truth.sample_id.eq(row.sample_id)].itertuples(index=False):
            draw.rectangle(
                (box.x_min, box.y_min, box.x_max, box.y_max), outline="green", width=8
            )
        for box in predictions[
            predictions.sample_id.eq(row.sample_id)
            & predictions.confidence.ge(selected_confidence)
        ].itertuples(index=False):
            draw.rectangle(
                (box.x_min, box.y_min, box.x_max, box.y_max), outline="red", width=8
            )
        image.thumbnail((1280, 310))
        canvas = Image.new("RGB", (1280, 350), "white")
        canvas.paste(image, ((1280 - image.width) // 2, 35))
        ImageDraw.Draw(canvas).text(
            (8, 8),
            f"{row.category}: {row.sample_id}; green=pseudo-label, red=prediction",
            fill="black",
        )
        montage.paste(canvas, (0, position * 350))
    montage_path = run.run_directory / "figures/deterministic_detection_examples.png"
    montage.save(montage_path, dpi=(300, 300))
    artifacts.append(
        run.artifact(montage_path, role="deterministic_detection_examples")
    )

    overall_detection = frames["detection_metrics"].query("scope == 'all'").iloc[0]
    scalar_test = frames["scalar_metrics"].query(
        "model_name == 'multitask_rtdetr_detector_scalar_head' and split == 'test'"
    )
    image_metric = scalar_test[scalar_test.evaluation_level.eq("image_view")].iloc[0]
    run_metric = scalar_test[scalar_test.evaluation_level.eq("run_raw_top3")].iloc[0]
    report = f"""# Multitask genuine RT-DETR engineering baseline

> **PROVISIONAL PSEUDO-BOXES AND PSEUDO-TARGETS — NOT PHYSICAL-DAMAGE GROUND TRUTH.**

This run retains genuine RT-DETR classification and box heads and attaches a differentiable scalar head to encoder layer 27 (`B×256×20×20`, global-average pooled to `B×256`). Standard Ultralytics classification/L1/GIoU detection losses are optimized jointly with a SmoothL1 scalar loss. The scalar target is the exact pinned `target_value_pct` (`phm2026_image_damage_v2`) used by the earlier frozen-encoder baseline. View predictions aggregate by maximum to a tooth; tooth predictions aggregate by run top-3 mean, with a separately retained causal cumulative maximum.

Training used EXP-B only (448 views), validation/model selection used EXP-A only (323), and EXP-F (224) was evaluated once after selection. No EXP-F statistic selected the loss balance, epoch, checkpoint, or confidence threshold. The current task is post-run state estimation, not six-hour-ahead forecasting.

Detection on EXP-F at validation-selected confidence {selected_confidence:.4f}: precision={overall_detection.precision:.6f}, recall={overall_detection.recall:.6f}, F1={overall_detection.f1:.6f}, mAP@0.50={overall_detection.map50:.6f}, mAP@0.50:0.95={overall_detection.map50_95:.6f}. These are agreement with mask-derived pseudo-boxes only. Scalar EXP-F view MAE={image_metric.mae:.6f} pp (N={int(image_metric.sample_count)}); raw run top-3 MAE={run_metric.mae:.6f} pp (N={int(run_metric.sample_count)}). Physical validity requires expert review of the masks and boxes.

EXP-F is also an acquisition-protocol/domain shift: it contains canonical tooth views rather than the EXP-A/EXP-B canonical-plus-close-up protocol. Generic COCO detections are not treated as gear damage. Exact metrics, hashes, environment, trainable/frozen parameter counts, optimizer groups, loss balance, and the one-pass test declaration are machine-readable in this run.
"""
    report_path = run.run_directory / "reports/rtdetr_multitask_report.md"
    report_path.write_text(report, encoding="utf-8")
    artifacts.append(run.artifact(report_path, role="multitask_report"))
    return finalize_run(run, artifacts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_rtdetr_multitask.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        required = {
            "pseudo_boxes": (
                "tables/annotation_image_manifest.parquet",
                "tables/annotation_manifest.parquet",
                "reports/annotation_quality.json",
                "manifests/materialized_cache.parquet",
            ),
            "detector": (
                "checkpoints/best_detector.pt",
                "tables/detection_metrics.parquet",
                "manifests/outputs.json",
            ),
            "frozen_regression": (
                "tables/metrics.parquet",
                "tables/predictions.parquet",
            ),
            "naive_baselines": (
                "tables/baseline_metrics.parquet",
                "tables/baseline_predictions.parquet",
            ),
        }
        pins = {
            name: load_pinned_run(
                config.repository_root,
                data["source_runs"][name],
                required_artifacts=paths,
            )
            for name, paths in required.items()
        }
        pseudo = pins["pseudo_boxes"]
        images = pd.read_parquet(
            pseudo.artifact_path("tables/annotation_image_manifest.parquet")
        )
        ground_truth = pd.read_parquet(
            pseudo.artifact_path("tables/annotation_manifest.parquet")
        )
        expected = {
            ("train", "EXP-B"): 448,
            ("validation", "EXP-A"): 323,
            ("test", "EXP-F"): 224,
        }
        if images.groupby(["split", "experiment"]).size().to_dict() != expected:
            raise ConfigError("pinned split identity/count mismatch")
        if len(images) != 995 or images.sample_id.nunique() != 995:
            raise ConfigError("model-ready sample identity mismatch")
        quality = json.loads(
            pseudo.artifact_path("reports/annotation_quality.json").read_text()
        )
        if quality["status"] != "PROVISIONAL_PSEUDO_BOXES_FOR_ENGINEERING_BASELINE":
            raise ConfigError("pseudo-box quality gate did not pass")
        usage = shutil.disk_usage(config.repository_root)
        if usage.free < int(data["storage_limits"]["minimum_free_bytes"]):
            raise ConfigError("free disk is below the required 50 GiB")
        environment = _device_information()
        if not environment["cuda_available"]:
            raise ConfigError("multitask training requires the available GPU")
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "sample_count": len(images),
                        "pseudo_box_count": len(ground_truth),
                        "split_counts": {
                            name: int(value)
                            for name, value in images.groupby("split").size().items()
                        },
                        "free_bytes": usage.free,
                        "would_train": False,
                        "would_evaluate_exp_f": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        output_root = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
        source_runs = [
            {
                "name": name,
                "run_id": pinned.run_id,
                "directory": pinned.relative_directory,
                "artifacts": dict(pinned.verified_hashes),
            }
            for name, pinned in pins.items()
        ]
        run = create_run_context(
            study=data["study"],
            output_root=output_root,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/train_rtdetr_multitask.py", *(argv or sys.argv[1:])],
            input_roots=tuple(pinned.relative_directory for pinned in pins.values()),
            package_names=(
                "torch",
                "torchvision",
                "ultralytics",
                "opencv-python-headless",
                "numpy",
                "pandas",
                "pyarrow",
                "Pillow",
                "matplotlib",
            ),
            source_runs=source_runs,
        )
        run.create_layout()
        set_reproducible_seed(int(data["seed"]))
        device = torch.device(data["training"]["device"])
        model_config = data["model"]
        training = data["training"]
        train_frame = images[images.split.eq("train")].copy()
        validation_frame = images[images.split.eq("validation")].copy()
        test_frame = images[images.split.eq("test")].copy()
        target_mean = float(train_frame.target_value_pct.mean())
        target_scale = float(train_frame.target_value_pct.std(ddof=0)) or 1.0
        loader_kwargs = {
            "pseudo_directory": pseudo.directory,
            "image_size": int(model_config["image_size"]),
            "batch_size": int(training["batch_size"]),
            "workers": int(training["workers"]),
            "seed": int(data["seed"]),
        }
        train_loader = _loader(
            train_frame,
            **loader_kwargs,
            augment=bool(training["augmentation"]["horizontal_flip"]),
            shuffle=True,
        )
        validation_loader = _loader(
            validation_frame, **loader_kwargs, augment=False, shuffle=False
        )
        test_loader = _loader(test_frame, **loader_kwargs, augment=False, shuffle=False)
        model = _model(
            pins["detector"].artifact_path("checkpoints/best_detector.pt"),
            model_config,
            device,
        )
        frozen_layers = int(training["frozen_detector_layers"])
        parameter_summary = model.freeze_detector_prefix(frozen_layers)
        first_batch = move_multitask_batch(next(iter(train_loader)), device)
        _set_training_mode(model, frozen_layers)
        balance = _balance_lambda(
            model,
            first_batch,
            target_mean=target_mean,
            target_scale=target_scale,
            minimum=float(training["lambda_balance_minimum"]),
            maximum=float(training["lambda_balance_maximum"]),
        )
        tiny_batch_size = int(training["tiny_overfit_batch_size"])
        tiny_batch = {
            key: (
                value[:tiny_batch_size]
                if isinstance(value, torch.Tensor) and key in {"img", "scalar_target"}
                else value
            )
            for key, value in first_batch.items()
        }
        tiny = _tiny_overfit(
            model,
            tiny_batch,
            target_mean=target_mean,
            target_scale=target_scale,
            steps=int(training["tiny_overfit_steps"]),
            learning_rate=float(training["scalar_head_learning_rate"]),
        )
        model.freeze_detector_prefix(frozen_layers)
        detector_parameters = [
            parameter
            for parameter in model.detector.parameters()
            if parameter.requires_grad
        ]
        head_parameters = list(model.scalar_head.parameters())
        optimizer = torch.optim.AdamW(
            [
                {
                    "params": detector_parameters,
                    "lr": float(training["detector_learning_rate"]),
                    "group_name": "unfrozen_rtdetr",
                },
                {
                    "params": head_parameters,
                    "lr": float(training["scalar_head_learning_rate"]),
                    "group_name": "scalar_head",
                },
            ],
            weight_decay=float(training["weight_decay"]),
        )
        scaler = torch.amp.GradScaler("cuda", enabled=bool(training["amp"]))
        history_rows = []
        best_loss = float("inf")
        best_state = None
        wait = 0
        training_started = time.perf_counter()
        for epoch in range(1, int(training["maximum_epochs"]) + 1):
            train_values = _epoch(
                model,
                train_loader,
                device=device,
                target_mean=target_mean,
                target_scale=target_scale,
                lambda_regression=balance["lambda_regression"],
                optimizer=optimizer,
                scaler=scaler,
                frozen_layers=frozen_layers,
                gradient_clip_norm=float(training["gradient_clip_norm"]),
                amp=bool(training["amp"]),
            )
            validation_values = _epoch(
                model,
                validation_loader,
                device=device,
                target_mean=target_mean,
                target_scale=target_scale,
                lambda_regression=balance["lambda_regression"],
                optimizer=None,
                scaler=None,
                frozen_layers=frozen_layers,
                gradient_clip_norm=float(training["gradient_clip_norm"]),
                amp=bool(training["amp"]),
            )
            history_rows.append(
                {
                    "epoch": epoch,
                    **{
                        f"train_{name}_loss": value
                        for name, value in train_values.items()
                        if name != "batch_count"
                    },
                    **{
                        f"validation_{name}_loss": value
                        for name, value in validation_values.items()
                        if name != "batch_count"
                    },
                    "detector_learning_rate": optimizer.param_groups[0]["lr"],
                    "scalar_head_learning_rate": optimizer.param_groups[1]["lr"],
                }
            )
            if validation_values["total"] < best_loss - 1e-8:
                best_loss = validation_values["total"]
                best_state = {
                    key: value.detach().cpu().clone()
                    for key, value in model.state_dict().items()
                }
                wait = 0
            else:
                wait += 1
            print(json.dumps(history_rows[-1], sort_keys=True), flush=True)
            if wait >= int(training["patience"]):
                break
        training_seconds = time.perf_counter() - training_started
        last_state = {
            key: value.detach().cpu().clone()
            for key, value in model.state_dict().items()
        }
        if best_state is None:
            raise RuntimeError("multitask training produced no best state")
        model.load_state_dict(best_state)
        gc.collect()
        torch.cuda.empty_cache()

        validation_detection, validation_scalar, validation_latency = _predict(
            model,
            validation_loader,
            device=device,
            target_mean=target_mean,
            target_scale=target_scale,
            confidence=float(model_config["minimum_inference_confidence"]),
            maximum_detections=int(model_config["maximum_detections"]),
        )
        validation_truth = ground_truth[
            ground_truth.sample_id.isin(validation_frame.sample_id)
        ].copy()
        selected_confidence, threshold_curve = select_confidence_threshold(
            validation_detection,
            validation_truth,
            validation_frame,
            candidates=data["validation_selection"]["confidence_candidates"],
        )
        # Sole EXP-F inference/evaluation pass for this multitask model.
        test_detection, test_scalar, test_latency = _predict(
            model,
            test_loader,
            device=device,
            target_mean=target_mean,
            target_scale=target_scale,
            confidence=float(model_config["minimum_inference_confidence"]),
            maximum_detections=int(model_config["maximum_detections"]),
        )
        test_truth = ground_truth[
            ground_truth.sample_id.isin(test_frame.sample_id)
        ].copy()
        detection_metrics = sliced_metrics(
            test_detection,
            test_truth,
            test_frame,
            confidence_threshold=selected_confidence,
        )
        ap_by_iou = pd.DataFrame(
            {
                "iou_threshold": np.linspace(0.5, 0.95, 10),
                "average_precision": [
                    average_precision(
                        test_detection,
                        test_truth,
                        test_frame,
                        iou_threshold=float(value),
                    )
                    for value in np.linspace(0.5, 0.95, 10)
                ],
                "status": "pseudo_box_agreement_only",
            }
        )
        scalar_predictions = pd.concat(
            [validation_scalar, test_scalar], ignore_index=True
        )
        tooth_predictions, run_predictions = aggregate_predictions(scalar_predictions)
        repetitions = int(data["evaluation"]["bootstrap_repetitions"])
        scalar_metrics = _metric_rows(
            scalar_predictions,
            tooth_predictions,
            run_predictions,
            model_name="multitask_rtdetr_detector_scalar_head",
            repetitions=repetitions,
            seed=int(data["seed"]),
        )
        baseline_predictions = []
        baseline_metrics = []
        for name, value in (
            ("training_mean", target_mean),
            ("training_median", float(train_frame.target_value_pct.median())),
        ):
            prediction = _naive_predictions(images, target_value=value, model_name=name)
            tooth, runs = aggregate_predictions(prediction)
            baseline_predictions.append(prediction)
            baseline_metrics.append(
                _metric_rows(
                    prediction,
                    tooth,
                    runs,
                    model_name=name,
                    repetitions=repetitions,
                    seed=int(data["seed"]),
                )
            )
        naive_prediction_frame = pd.concat(baseline_predictions, ignore_index=True)
        naive_metric_frame = pd.concat(baseline_metrics, ignore_index=True)
        frozen_metrics = pd.read_parquet(
            pins["frozen_regression"].artifact_path("tables/metrics.parquet")
        )
        level_matched = pd.concat(
            [naive_metric_frame, frozen_metrics, scalar_metrics],
            ignore_index=True,
            sort=False,
        )
        examples = deterministic_example_rows(
            test_detection,
            test_truth,
            test_frame,
            confidence_threshold=selected_confidence,
        )
        history = pd.DataFrame(history_rows)
        best_epoch = int(history.loc[history.validation_total_loss.idxmin(), "epoch"])
        tensor_shapes = pd.DataFrame(
            [
                {"stage": "source", "shape": "1440×2560×3", "meaning": "JPEG RGB"},
                {
                    "stage": "input",
                    "shape": "B×3×640×640",
                    "meaning": "float32/255 scale-fill",
                },
                {
                    "stage": "encoder",
                    "shape": "B×256×20×20",
                    "meaning": "shared layer 27",
                },
                {
                    "stage": "decoder",
                    "shape": "B×300×6",
                    "meaning": "queries: xywh/conf/class",
                },
                {"stage": "scalar", "shape": "B×1", "meaning": "global pool + MLP"},
            ]
        )
        environment.update(
            {
                "training_seconds": training_seconds,
                "peak_cuda_memory_allocated_bytes": int(
                    torch.cuda.max_memory_allocated()
                ),
                "parameter_summary": parameter_summary,
                "frozen_detector_layer_count": frozen_layers,
                "optimizer_groups": [
                    {
                        "name": "unfrozen_rtdetr",
                        "learning_rate": training["detector_learning_rate"],
                        "parameter_count": sum(p.numel() for p in detector_parameters),
                    },
                    {
                        "name": "scalar_head",
                        "learning_rate": training["scalar_head_learning_rate"],
                        "parameter_count": sum(p.numel() for p in head_parameters),
                    },
                ],
                "lambda_selection": balance,
                "tiny_overfit": tiny,
                "best_epoch": best_epoch,
                "exp_f_test_evaluation_passes": 1,
                "exp_f_used_for_tuning": False,
            }
        )
        resolved = {
            "schema_version": "1.0.0",
            "status": MULTITASK_STATUS,
            "model": model_config,
            "training": training,
            "target_scaler": {
                "fit_split": "EXP-B/train only",
                "mean": target_mean,
                "scale": target_scale,
                "unit": "percent_visible_flank_candidate_area",
            },
            "lambda_selection": balance,
            "tiny_overfit": tiny,
            "selection": {
                "best_epoch": best_epoch,
                "confidence_threshold": selected_confidence,
                "selection_experiment": "EXP-A",
                "exp_f_used_for_tuning": False,
                "exp_f_evaluation_passes": 1,
            },
            "execution": {
                "starting_free_bytes": usage.free,
                "training_seconds": training_seconds,
                "raw_archives_opened": False,
                "raw_archives_modified": False,
            },
        }
        inputs = [
            pinned.source_record(path)
            for pinned in pins.values()
            for path in sorted(pinned.verified_hashes)
        ]
        frames = {
            "training_history": history,
            "validation_detection_predictions": validation_detection,
            "test_detection_predictions": test_detection,
            "validation_threshold_selection": threshold_curve,
            "detection_metrics": detection_metrics,
            "ap_by_iou_threshold": ap_by_iou,
            "scalar_predictions": scalar_predictions,
            "tooth_predictions": tooth_predictions,
            "run_predictions": run_predictions,
            "scalar_metrics": scalar_metrics,
            "naive_predictions": naive_prediction_frame,
            "naive_metrics": naive_metric_frame,
            "level_matched_model_comparison": level_matched,
            "latency": pd.concat([validation_latency, test_latency], ignore_index=True),
            "tensor_shapes": tensor_shapes,
            "deterministic_examples": examples,
            "test_ground_truth": test_truth,
            "test_images": test_frame,
        }
        artifacts = _write_results(
            run=run,
            model=model,
            best_state=best_state,
            last_state=last_state,
            frames=frames,
            resolved=resolved,
            inputs=inputs,
            environment=environment,
            pseudo_directory=pseudo.directory,
            selected_confidence=selected_confidence,
        )
        model.close()
    except (
        ConfigError,
        KeyError,
        OSError,
        RuntimeError,
        subprocess.CalledProcessError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "selected_confidence": selected_confidence,
                "best_epoch": best_epoch,
                "exp_f_evaluations": 1,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
