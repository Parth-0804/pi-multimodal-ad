"""Frozen RT-DETR multi-scale features with a provisional scalar regression head."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import time
from typing import Any

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
import torch
from torch import nn

from ..evaluation.regression import regression_metrics
from ..profiling.images import (
    ImageProfileOptions,
    ImageSource,
    materialize_image_source,
)
from ..reporting.common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
)
from ..utils.provenance import ArtifactRecord, RunContext

SCHEMA_VERSION = "1.0.0"
FORMULATION = "RTDETR_DERIVED_FROZEN_ENCODER_SCALAR_REGRESSION_PROVISIONAL"


class RegressionHead(nn.Module):
    def __init__(
        self, feature_dimension: int, hidden_dimension: int, dropout: float
    ) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(feature_dimension, hidden_dimension),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dimension, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features).squeeze(-1)


@dataclass(slots=True)
class RegressionResult:
    feature_rows: list[dict[str, Any]]
    history: list[dict[str, Any]]
    predictions: pd.DataFrame
    tooth_predictions: pd.DataFrame
    run_predictions: pd.DataFrame
    metrics: pd.DataFrame
    tensor_shapes: list[dict[str, Any]]
    environment: Mapping[str, Any]
    training_summary: Mapping[str, Any]
    best_state: Mapping[str, Any]
    last_state: Mapping[str, Any]
    feature_scaler: Mapping[str, Any]
    target_scaler: Mapping[str, Any]
    example_images: Mapping[str, np.ndarray]


def extract_features(
    checkpoint: Path,
    samples: pd.DataFrame,
    sources: Mapping[str, ImageSource],
    *,
    image_size: int,
    feature_layers: Sequence[int],
    device: int | str,
    max_member_bytes: int = 8_388_608,
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], dict[str, np.ndarray], Mapping[str, Any]
]:
    import ultralytics
    from ultralytics import RTDETR

    model = RTDETR(str(checkpoint))
    activations: dict[int, torch.Tensor] = {}
    handles = []
    for layer in feature_layers:
        handles.append(
            model.model.model[int(layer)].register_forward_hook(
                lambda _module, _inputs, output, layer=int(
                    layer
                ): activations.__setitem__(layer, output)
            )
        )
    rows: list[dict[str, Any]] = []
    shapes: list[dict[str, Any]] = []
    examples: dict[str, np.ndarray] = {}
    options = ImageProfileOptions(
        mode="full", max_member_bytes=max_member_bytes, max_pixels=20_000_000
    )
    try:
        for position, (_, sample) in enumerate(
            samples.sort_values("sample_id").iterrows()
        ):
            source = sources[str(sample.source_member_id)]
            before = (
                source.archive_path.stat().st_size,
                source.archive_path.stat().st_mtime_ns,
            )
            with materialize_image_source(source, options=options) as path:
                bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
                if bgr is None:
                    raise RuntimeError(f"unable to decode {sample.image_id}")
            activations.clear()
            started = time.perf_counter()
            model.predict(
                source=bgr, imgsz=image_size, device=device, verbose=False, conf=0.25
            )
            latency_ms = (time.perf_counter() - started) * 1000
            vectors = []
            for layer in feature_layers:
                value = activations[int(layer)]
                if not isinstance(value, torch.Tensor) or value.ndim != 4:
                    raise RuntimeError(f"unexpected feature output at layer {layer}")
                vectors.append(
                    value.detach().float().mean(dim=(-2, -1)).cpu().numpy()[0]
                )
                if position == 0:
                    shapes.append(
                        {
                            "stage": f"ultralytics_layer_{layer}",
                            "shape_json": json.dumps(list(value.shape)),
                            "aggregation": "global_average_pool_spatial_dimensions",
                        }
                    )
            feature = np.concatenate(vectors)
            row = {
                "sample_id": sample.sample_id,
                "image_id": sample.image_id,
                "experiment": sample.experiment,
                "run": int(sample.run),
                "tooth_id": int(sample.tooth_id),
                "split": sample.split,
                "target": float(sample.per_image_damage_candidate_pct),
                "feature_latency_ms": latency_ms,
                "original_height": int(bgr.shape[0]),
                "original_width": int(bgr.shape[1]),
                "source_archive_unchanged": before
                == (
                    source.archive_path.stat().st_size,
                    source.archive_path.stat().st_mtime_ns,
                ),
            }
            row.update(
                {
                    f"feature_{index:04d}": float(value)
                    for index, value in enumerate(feature)
                }
            )
            rows.append(row)
            if len(examples) < 12:
                examples[str(sample.image_id)] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    finally:
        for handle in handles:
            handle.remove()
    if not all(row["source_archive_unchanged"] for row in rows):
        raise RuntimeError("raw archive changed during feature extraction")
    shapes.insert(
        0,
        {
            "stage": "model_input",
            "shape_json": f"[1,3,{image_size},{image_size}]",
            "aggregation": "Ultralytics scale-fill; BGR-to-RGB; float32/255",
        },
    )
    shapes.append(
        {
            "stage": "concatenated_multiscale_feature",
            "shape_json": f"[1,{len(feature_layers)*256}]",
            "aggregation": "concatenate global-average-pooled layer features",
        }
    )
    environment = {
        "formulation": FORMULATION,
        "ultralytics_version": ultralytics.__version__,
        "torch_version": torch.__version__,
        "opencv_version": cv2.__version__,
        "device": str(model.predictor.device),
        "device_name": (
            torch.cuda.get_device_name(device) if torch.cuda.is_available() else "CPU"
        ),
        "encoder_parameters": sum(
            parameter.numel() for parameter in model.model.parameters()
        ),
        "encoder_trainable": False,
        "pretrained_dataset": "COCO",
        "input_preprocessing": "scale-fill to square; BGR to RGB; BCHW float32 divided by 255; no pixel mask",
    }
    return rows, shapes, examples, environment


def _arrays(
    frame: pd.DataFrame, feature_columns: Sequence[str], split: str
) -> tuple[np.ndarray, np.ndarray]:
    scoped = frame[frame.split.eq(split)]
    return scoped[list(feature_columns)].to_numpy(np.float32), scoped.target.to_numpy(
        np.float32
    )


def train_head(
    feature_rows: Sequence[Mapping[str, Any]],
    *,
    seed: int,
    hidden_dimension: int,
    dropout: float,
    max_epochs: int,
    patience: int,
    batch_size: int,
    learning_rate: float,
    weight_decay: float,
    tiny_overfit_steps: int,
    tiny_overfit_size: int,
    device: str,
) -> tuple[
    nn.Module,
    list[dict[str, Any]],
    Mapping[str, Any],
    Mapping[str, Any],
    Mapping[str, Any],
    Mapping[str, Any],
    Mapping[str, Any],
]:
    torch.manual_seed(seed)
    np.random.seed(seed)
    frame = pd.DataFrame(feature_rows)
    feature_columns = sorted(
        column for column in frame if column.startswith("feature_")
    )
    train_x, train_y = _arrays(frame, feature_columns, "train")
    val_x, val_y = _arrays(frame, feature_columns, "validation")
    mean = train_x.mean(axis=0)
    scale = train_x.std(axis=0)
    scale[scale < 1e-8] = 1
    target_mean = float(train_y.mean())
    target_scale = float(train_y.std()) or 1.0
    tx = (train_x - mean) / scale
    vx = (val_x - mean) / scale
    ty = (train_y - target_mean) / target_scale
    vy = (val_y - target_mean) / target_scale
    compute = torch.device(device)
    model = RegressionHead(len(feature_columns), hidden_dimension, dropout).to(compute)
    tiny = RegressionHead(len(feature_columns), hidden_dimension, 0.0).to(compute)
    optimizer = torch.optim.AdamW(tiny.parameters(), lr=learning_rate)
    tiny_x = torch.tensor(tx[:tiny_overfit_size], device=compute)
    tiny_y = torch.tensor(ty[:tiny_overfit_size], device=compute)
    initial = float(nn.functional.mse_loss(tiny(tiny_x), tiny_y).item())
    for _ in range(tiny_overfit_steps):
        optimizer.zero_grad()
        loss = nn.functional.mse_loss(tiny(tiny_x), tiny_y)
        loss.backward()
        optimizer.step()
    final = float(nn.functional.mse_loss(tiny(tiny_x), tiny_y).item())
    if not final < initial:
        raise RuntimeError("tiny-batch overfit did not reduce loss")
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    generator = torch.Generator().manual_seed(seed)
    loader = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(torch.tensor(tx), torch.tensor(ty)),
        batch_size=batch_size,
        shuffle=True,
        generator=generator,
        num_workers=0,
    )
    val_tensor = torch.tensor(vx, device=compute)
    val_target = torch.tensor(vy, device=compute)
    history = []
    best = float("inf")
    best_state = None
    wait = 0
    for epoch in range(1, max_epochs + 1):
        model.train()
        losses = []
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(compute), batch_y.to(compute)
            optimizer.zero_grad()
            loss = nn.functional.mse_loss(model(batch_x), batch_y)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
        model.eval()
        with torch.no_grad():
            val_loss = float(
                nn.functional.mse_loss(model(val_tensor), val_target).item()
            )
        history.append(
            {
                "epoch": epoch,
                "training_loss_scaled_mse": float(np.mean(losses)),
                "validation_loss_scaled_mse": val_loss,
                "learning_rate": optimizer.param_groups[0]["lr"],
            }
        )
        if val_loss < best - 1e-8:
            best = val_loss
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }
            wait = 0
        else:
            wait += 1
        if wait >= patience:
            break
    last_state = {
        key: value.detach().cpu().clone() for key, value in model.state_dict().items()
    }
    model.load_state_dict(best_state)
    summary = {
        "epochs_completed": len(history),
        "best_epoch": min(history, key=lambda row: row["validation_loss_scaled_mse"])[
            "epoch"
        ],
        "best_validation_scaled_mse": best,
        "early_stopped": len(history) < max_epochs,
        "patience": patience,
        "tiny_overfit_initial_loss": initial,
        "tiny_overfit_final_loss": final,
        "encoder_frozen": True,
        "head_parameter_count": sum(p.numel() for p in model.parameters()),
    }
    return (
        model,
        history,
        best_state,
        last_state,
        {
            "mean": mean.tolist(),
            "scale": scale.tolist(),
            "feature_columns": feature_columns,
        },
        {"mean": target_mean, "scale": target_scale},
        summary,
    )


def predict_all(
    model: nn.Module,
    rows: Sequence[Mapping[str, Any]],
    feature_scaler: Mapping[str, Any],
    target_scaler: Mapping[str, Any],
    *,
    device: str,
    model_run_id: str,
) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    columns = feature_scaler["feature_columns"]
    x = (
        frame[columns].to_numpy(np.float32) - np.asarray(feature_scaler["mean"])
    ) / np.asarray(feature_scaler["scale"])
    model.eval()
    started = time.perf_counter()
    with torch.no_grad():
        scaled = (
            model(torch.tensor(x, dtype=torch.float32, device=device)).cpu().numpy()
        )
    elapsed = (time.perf_counter() - started) * 1000 / len(frame)
    prediction = scaled * float(target_scaler["scale"]) + float(target_scaler["mean"])
    return pd.DataFrame(
        {
            "sample_id": frame.sample_id,
            "image_id": frame.image_id,
            "experiment": frame.experiment,
            "run": frame.run.astype(int),
            "tooth_id": frame.tooth_id.astype(int),
            "split": frame.split,
            "y_true_raw": frame.target,
            "y_true_monotonic": None,
            "y_pred": prediction,
            "physical_unit": "percent_visible_flank_candidate_area",
            "target_definition_version": "phm2026_image_damage_v2",
            "target_verification_status": "provisional_pending_human_review",
            "model_name": "rtdetr_derived_frozen_encoder_regression",
            "model_run_id": model_run_id,
            "latency_ms": elapsed,
            "confidence_or_uncertainty": None,
        }
    )


def aggregate_predictions(
    predictions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    tooth = predictions.groupby(
        ["experiment", "run", "tooth_id", "split"], as_index=False
    ).agg(
        y_true_raw=("y_true_raw", "max"),
        y_pred=("y_pred", "max"),
        view_count=("image_id", "size"),
    )
    run_rows = []
    for (experiment, run, split), scoped in tooth.groupby(
        ["experiment", "run", "split"]
    ):
        truth = np.sort(scoped.y_true_raw.to_numpy())[::-1]
        prediction = np.sort(scoped.y_pred.to_numpy())[::-1]
        run_rows.append(
            {
                "experiment": experiment,
                "run": int(run),
                "split": split,
                "y_true_raw_top3_mean": float(truth[:3].mean()),
                "y_pred_raw_top3_mean": float(prediction[:3].mean()),
                "y_true_top1": float(truth[0]),
                "y_pred_top1": float(prediction[0]),
                "valid_tooth_count": len(scoped),
            }
        )
    run_frame = pd.DataFrame(run_rows).sort_values(["experiment", "run"])
    run_frame["y_true_monotonic_top3_mean"] = run_frame.groupby(
        "experiment"
    ).y_true_raw_top3_mean.cummax()
    run_frame["y_pred_monotonic_top3_mean"] = run_frame.groupby(
        "experiment"
    ).y_pred_raw_top3_mean.cummax()
    return tooth, run_frame


def build_metrics(
    predictions: pd.DataFrame, tooth: pd.DataFrame, runs: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    for level, frame, true, pred in (
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
            rows.append(
                {
                    "model_name": "rtdetr_derived_frozen_encoder_regression",
                    "evaluation_level": level,
                    "split": split,
                    "experiment": experiment,
                    "unit": "percentage_points_visible_flank_candidate_area",
                    **regression_metrics(scoped[true], scoped[pred]),
                }
            )
    return pd.DataFrame(rows)


def _scatter(frame: pd.DataFrame, x: str, y: str, title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 6))
    for split, scoped in frame.groupby("split"):
        ax.scatter(scoped[x], scoped[y], label=split, alpha=0.65, s=18)
    low = min(frame[x].min(), frame[y].min())
    high = max(frame[x].max(), frame[y].max())
    ax.plot([low, high], [low, high], "--", color="black")
    ax.set(
        title=title,
        xlabel="True provisional candidate area (%)",
        ylabel="Predicted provisional candidate area (%)",
    )
    ax.legend()
    fig.tight_layout()
    return fig


def _line_loss(history: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(history.epoch, history.training_loss_scaled_mse, label="train")
    ax.plot(history.epoch, history.validation_loss_scaled_mse, label="validation")
    ax.set(
        title="Frozen-encoder regression-head training",
        xlabel="Epoch",
        ylabel="Scaled MSE",
    )
    ax.legend()
    fig.tight_layout()
    return fig


def write_regression_run(
    result: RegressionResult,
    *,
    run: RunContext,
    checkpoint: Path,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
    naive_metrics: pd.DataFrame,
) -> list[ArtifactRecord]:
    apply_academic_style()
    artifacts = []
    cp = run.write_resolved_config(resolved_config)
    ip = run.write_input_manifest(input_manifest)
    artifacts += [
        run.artifact(cp, role="resolved_configuration"),
        run.artifact(ip, role="input_manifest"),
        run.artifact(checkpoint, role="pretrained_encoder_checkpoint"),
    ]
    checkpoint_dir = run.run_directory / "checkpoints"
    best = checkpoint_dir / "best_head.pt"
    last = checkpoint_dir / "last_head.pt"
    torch.save(result.best_state, best)
    torch.save(result.last_state, last)
    artifacts += [
        run.artifact(best, role="best_model_checkpoint"),
        run.artifact(last, role="last_model_checkpoint"),
    ]
    state_path = run.run_directory / "config/preprocessing_target_scalers.json"
    state_path.write_text(
        json_text(
            {
                "feature_scaler": result.feature_scaler,
                "target_scaler": result.target_scaler,
            }
        ),
        encoding="utf-8",
    )
    artifacts.append(run.artifact(state_path, role="preprocessing_target_scalers"))
    tables = {
        "encoder_features": pd.DataFrame(result.feature_rows),
        "training_history": pd.DataFrame(result.history),
        "predictions": result.predictions,
        "tooth_predictions": result.tooth_predictions,
        "run_predictions": result.run_predictions,
        "metrics": result.metrics,
        "tensor_shapes": pd.DataFrame(result.tensor_shapes),
        "naive_metrics": naive_metrics,
    }
    for name, frame in tables.items():
        directory = "cache" if name == "encoder_features" else "tables"
        (run.run_directory / directory).mkdir(exist_ok=True)
        path = run.run_directory / f"{directory}/{name}.parquet"
        frame.to_parquet(path, index=False)
        artifacts.append(run.artifact(path, role=name))
        csv = run.run_directory / f"tables/{name}.csv"
        frame.to_csv(csv, index=False)
        artifacts.append(run.artifact(csv, role=name))
    env_path = run.run_directory / "reports/environment_device.json"
    env_path.write_text(json_text(dict(result.environment)), encoding="utf-8")
    summary_path = run.run_directory / "reports/training_summary.json"
    summary_path.write_text(json_text(dict(result.training_summary)), encoding="utf-8")
    artifacts += [
        run.artifact(env_path, role="environment_device"),
        run.artifact(summary_path, role="training_summary"),
    ]
    history = tables["training_history"]
    pred = result.predictions
    tooth = result.tooth_predictions
    runs = result.run_predictions
    residual = pred.assign(residual=pred.y_pred - pred.y_true_raw)
    figures = {
        "training_validation_loss": _line_loss(history),
        "per_tooth_predicted_vs_actual": _scatter(
            tooth, "y_true_raw", "y_pred", "Per-tooth provisional prediction"
        ),
        "run_predicted_vs_actual_trajectory": _scatter(
            runs,
            "y_true_raw_top3_mean",
            "y_pred_raw_top3_mean",
            "Run-level provisional top-3 prediction",
        ),
    }
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(residual.residual, bins=25, color=ACADEMIC_COLORS[1])
    ax.set(
        title="Residual distribution",
        xlabel="Prediction − provisional pseudo-target (percentage points)",
        ylabel="Images",
    )
    figures["residual_distribution"] = fig
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.scatter(residual.y_pred, residual.residual, s=14, alpha=0.55)
    ax.axhline(0, color="black", linestyle="--")
    ax.set(
        title="Residual versus prediction",
        xlabel="Prediction (%)",
        ylabel="Residual (percentage points)",
    )
    figures["residual_vs_prediction"] = fig
    comparison = pd.concat(
        [
            naive_metrics,
            result.metrics[result.metrics.evaluation_level.eq("image_view")],
        ],
        ignore_index=True,
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    scoped = comparison[comparison.split.isin(["validation", "test"])]
    labels = scoped.model_name + "/" + scoped.experiment
    ax.bar(labels, scoped.mae, color=ACADEMIC_COLORS[:1] * len(labels))
    ax.set(title="Naive versus RT-DETR-derived MAE", ylabel="MAE (percentage points)")
    ax.tick_params(axis="x", rotation=45)
    figures["naive_baseline_comparison"] = fig
    fig, ax = plt.subplots(figsize=(9, 5))
    for_plot = result.metrics[result.metrics.evaluation_level.eq("image_view")]
    ax.bar(for_plot.experiment, for_plot.mae, color=ACADEMIC_COLORS[0])
    ax.set(title="Image error by experiment", ylabel="MAE (percentage points)")
    figures["errors_by_experiment"] = fig
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(runs.run, runs.y_true_top1, marker="o", label="true top-1")
    ax.plot(runs.run, runs.y_true_raw_top3_mean, marker="o", label="true top-3 mean")
    ax.plot(runs.run, runs.y_pred_top1, marker="x", label="pred top-1")
    ax.plot(runs.run, runs.y_pred_raw_top3_mean, marker="x", label="pred top-3 mean")
    ax.set(
        title="Top-1/top-3 aggregation comparison",
        xlabel="Run",
        ylabel="Provisional candidate area (%)",
    )
    ax.legend()
    figures["top1_top3_aggregation_comparison"] = fig
    latency = pd.DataFrame(result.feature_rows)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(latency.feature_latency_ms, bins=25, color=ACADEMIC_COLORS[2])
    ax.set(
        title="Frozen RT-DETR encoder latency",
        xlabel="Milliseconds/image",
        ylabel="Images",
    )
    figures["latency_distribution"] = fig
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis("off")
    stages = [
        "1440×2560×3 RGB",
        "scale-fill 640×640",
        "B×3×640×640 float32",
        "P3/P4/P5 256-channel maps",
        "global average + concat 768",
        "MLP scalar B×1",
    ]
    for index, label in enumerate(stages):
        x = 0.02 + index * 0.16
        ax.add_patch(
            plt.Rectangle(
                (x, 0.35),
                0.13,
                0.3,
                transform=ax.transAxes,
                facecolor="#EAF0F5",
                edgecolor=ACADEMIC_COLORS[0],
            )
        )
        ax.text(
            x + 0.065,
            0.5,
            label,
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=8,
        )
    ax.set_title("RT-DETR-derived frozen-encoder tensor flow")
    figures["preprocessing_tensor_shape_diagram"] = fig
    split_counts = (
        pred.groupby(["split", "experiment"]).size().reset_index(name="sample_count")
    )
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(
        split_counts.split + "/" + split_counts.experiment,
        split_counts.sample_count,
        color=ACADEMIC_COLORS[0],
    )
    ax.set(title="Dataset and split summary", ylabel="Image-view samples")
    figures["dataset_split_summary"] = fig
    for name, figure in figures.items():
        source = run.run_directory / f"tables/plot_source_{name}.csv"
        (
            history
            if name == "training_validation_loss"
            else (
                pred
                if "predicted" in name or "residual" in name
                else (
                    runs
                    if "top1" in name
                    else (
                        result.metrics
                        if "comparison" in name or "errors" in name
                        else latency if name == "latency_distribution" else split_counts
                    )
                )
            )
        ).to_csv(source, index=False)
        artifacts.append(run.artifact(source, role=f"plot_source_{name}"))
        for path in save_figure_pair(figure, run.run_directory / f"figures/{name}"):
            artifacts.append(run.artifact(path, role=f"{name}_{path.suffix[1:]}"))
    errors = pred.assign(abs_error=(pred.y_pred - pred.y_true_raw).abs()).sort_values(
        "abs_error"
    )
    selected = pd.concat([errors.head(4), errors.tail(4)])
    montage = Image.new("RGB", (1200, 600), "white")
    draw = ImageDraw.Draw(montage)
    for index, (_, row) in enumerate(selected.iterrows()):
        image = result.example_images.get(str(row.image_id))
        if image is None:
            continue
        tile = Image.fromarray(image)
        tile.thumbnail((290, 240))
        x = (index % 4) * 300
        y = (index // 4) * 300
        montage.paste(tile, (x, y))
        draw.text(
            (x + 5, y + 245),
            f"true={row.y_true_raw:.2f} pred={row.y_pred:.2f} err={row.abs_error:.2f}",
            fill="black",
        )
    montage_path = run.run_directory / "figures/best_worst_predictions.png"
    montage.save(montage_path, dpi=(300, 300))
    artifacts.append(run.artifact(montage_path, role="best_worst_predictions_png"))
    banner = "**PROVISIONAL PSEUDO-TARGET — PENDING HUMAN MASK VALIDATION; NOT VALIDATED PHYSICAL SPALL PERFORMANCE.**"
    report = f"""# RT-DETR-derived image-regression baseline\n\n> {banner}\n\nFormulation: frozen COCO-pretrained RT-DETR-L backbone/hybrid encoder; global average pooling of three 256-channel multi-scale maps; 768→128→1 regression head. Each view predicts its own provisional candidate-area ratio. View predictions aggregate by maximum to a tooth and the 28 tooth predictions aggregate by top-3 mean to a run.\n\nTraining used EXP-B only; EXP-A was validation and EXP-F was untouched until evaluation. No test tuning, hyperparameter sweep, sensor input, PatchTST, or organizer ground truth was used. Exact metrics are in `tables/metrics.csv`; naive comparison is in `tables/naive_metrics.csv`. These quantify pseudo-label reproducibility across acquisition protocols, not calibrated gear damage.\n\nPreprocessing: BGR decoder input → Ultralytics scale-fill 640×640 → RGB/BCHW float32/255; no padding mask. Encoder frozen/precomputed; only the MLP head trained. Best and last head checkpoints are retained.\n"""
    report_path = run.run_directory / "reports/rtdetr_regression_report.md"
    report_path.write_text(report, encoding="utf-8")
    artifacts.append(run.artifact(report_path, role="rtdetr_regression_report"))
    return finalize_run(run, artifacts)
