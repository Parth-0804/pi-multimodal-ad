"""Training, baselines, evaluation, and artifacts for the sensor PatchTST baseline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
import torch
from torch import nn

from ..evaluation.regression import regression_metrics
from ..preprocessing.timeseries import RunSequence, collate_run_sequences
from ..reporting.common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
)
from ..utils.provenance import ArtifactRecord, RunContext
from .patchtst import PatchTSTConfig, PatchTSTRegressor

PATCHTST_RESULT_SCHEMA_VERSION = "1.0.0"
TARGET_UNIT = "percentage_points_visible_flank_candidate_area"


@dataclass(frozen=True, slots=True)
class TrainingOptions:
    max_epochs: int = 80
    patience: int = 10
    batch_size: int = 4
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    tiny_overfit_steps: int = 80


@dataclass(slots=True)
class PatchTSTResult:
    model_config: PatchTSTConfig
    history: pd.DataFrame
    predictions: pd.DataFrame
    metrics: pd.DataFrame
    comparison: pd.DataFrame
    architecture: pd.DataFrame
    training_summary: Mapping[str, Any]
    environment: Mapping[str, Any]
    best_state: Mapping[str, torch.Tensor]
    last_state: Mapping[str, torch.Tensor]
    target_scaler: Mapping[str, float]
    ridge_summary: Mapping[str, Any]


def _split(sequences: Sequence[RunSequence], name: str) -> list[RunSequence]:
    scoped = [sequence for sequence in sequences if sequence.split == name]
    if not scoped:
        raise ValueError(f"{name} sequence split is empty")
    return scoped


def _target_scaler(sequences: Sequence[RunSequence]) -> dict[str, float]:
    values = np.asarray([item.target_raw for item in sequences], dtype=np.float64)
    scale = float(values.std(ddof=0))
    return {"mean": float(values.mean()), "scale": scale if scale > 1e-8 else 1.0}


def _scaled_target(
    batch: Mapping[str, Any], scaler: Mapping[str, float], device: str
) -> torch.Tensor:
    return (batch["targets_raw"].to(device) - float(scaler["mean"])) / float(
        scaler["scale"]
    )


def _summary_vector(sequence: RunSequence) -> np.ndarray:
    values = sequence.values.astype(np.float64)
    return np.concatenate(
        (
            values.mean(axis=0),
            values.std(axis=0),
            values.min(axis=0),
            values.max(axis=0),
            values[-1],
        )
    )


def ridge_predictions(
    sequences: Sequence[RunSequence], *, alphas: Sequence[float]
) -> tuple[dict[str, float], Mapping[str, Any]]:
    """Select Ridge alpha on EXP-A validation and evaluate EXP-F once later."""

    train, validation = _split(sequences, "train"), _split(sequences, "validation")
    train_x = np.stack([_summary_vector(item) for item in train])
    train_y = np.asarray([item.target_raw for item in train])
    validation_x = np.stack([_summary_vector(item) for item in validation])
    validation_y = np.asarray([item.target_raw for item in validation])
    trials = []
    best: tuple[float, float, Ridge] | None = None
    for alpha in alphas:
        model = Ridge(alpha=float(alpha))
        model.fit(train_x, train_y)
        predicted = model.predict(validation_x)
        mae = float(np.mean(np.abs(predicted - validation_y)))
        trials.append({"alpha": float(alpha), "validation_mae": mae})
        candidate = (mae, float(alpha), model)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    if best is None:
        raise ValueError("at least one Ridge alpha is required")
    predictions = {
        item.sequence_id: float(best[2].predict(_summary_vector(item)[None, :])[0])
        for item in sequences
    }
    return predictions, {
        "selected_alpha": best[1],
        "selection_split": "validation_EXP-A",
        "test_used_for_selection": False,
        "trials": trials,
        "feature_definition": "per-normalized-minute-feature mean/std/min/max/last",
    }


def train_patchtst(
    sequences: Sequence[RunSequence],
    *,
    model_config: PatchTSTConfig,
    options: TrainingOptions,
    seed: int,
    device: str,
) -> tuple[
    PatchTSTRegressor,
    pd.DataFrame,
    Mapping[str, torch.Tensor],
    Mapping[str, torch.Tensor],
    Mapping[str, float],
    Mapping[str, Any],
]:
    """Train on EXP-B, early-stop on EXP-A, and keep best/last only."""

    torch.manual_seed(seed)
    np.random.seed(seed)
    train = _split(sequences, "train")
    validation = _split(sequences, "validation")
    scaler = _target_scaler(train)
    compute = torch.device(device)

    tiny = PatchTSTRegressor(model_config).to(compute)
    tiny_batch = collate_run_sequences(train[: min(2, len(train))])
    tiny_optimizer = torch.optim.Adam(tiny.parameters(), lr=options.learning_rate)
    tiny_target = _scaled_target(tiny_batch, scaler, device)
    tiny.train()
    initial = float(
        nn.functional.smooth_l1_loss(
            tiny(tiny_batch["inputs"].to(compute), tiny_batch["time_mask"].to(compute)),
            tiny_target,
        ).item()
    )
    for _ in range(options.tiny_overfit_steps):
        tiny_optimizer.zero_grad()
        prediction = tiny(
            tiny_batch["inputs"].to(compute), tiny_batch["time_mask"].to(compute)
        )
        loss = nn.functional.smooth_l1_loss(prediction, tiny_target)
        loss.backward()
        tiny_optimizer.step()
    tiny.eval()
    with torch.no_grad():
        final = float(
            nn.functional.smooth_l1_loss(
                tiny(
                    tiny_batch["inputs"].to(compute),
                    tiny_batch["time_mask"].to(compute),
                ),
                tiny_target,
            ).item()
        )
    if not final < initial:
        raise RuntimeError("tiny-batch overfit did not reduce robust loss")

    model = PatchTSTRegressor(model_config).to(compute)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=options.learning_rate, weight_decay=options.weight_decay
    )
    generator = torch.Generator().manual_seed(seed)
    order = torch.randperm(len(train), generator=generator).tolist()
    history: list[dict[str, Any]] = []
    best_loss = float("inf")
    best_state: Mapping[str, torch.Tensor] | None = None
    wait = 0
    for epoch in range(1, options.max_epochs + 1):
        model.train()
        epoch_order = order[epoch % len(order) :] + order[: epoch % len(order)]
        losses = []
        for start in range(0, len(epoch_order), options.batch_size):
            batch = collate_run_sequences(
                [
                    train[index]
                    for index in epoch_order[start : start + options.batch_size]
                ]
            )
            optimizer.zero_grad()
            prediction = model(
                batch["inputs"].to(compute), batch["time_mask"].to(compute)
            )
            loss = nn.functional.smooth_l1_loss(
                prediction, _scaled_target(batch, scaler, device)
            )
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
        model.eval()
        validation_batch = collate_run_sequences(validation)
        with torch.no_grad():
            validation_prediction = model(
                validation_batch["inputs"].to(compute),
                validation_batch["time_mask"].to(compute),
            )
            validation_loss = float(
                nn.functional.smooth_l1_loss(
                    validation_prediction,
                    _scaled_target(validation_batch, scaler, device),
                ).item()
            )
        history.append(
            {
                "epoch": epoch,
                "training_scaled_smooth_l1": float(np.mean(losses)),
                "validation_scaled_smooth_l1": validation_loss,
                "learning_rate": float(optimizer.param_groups[0]["lr"]),
            }
        )
        if validation_loss < best_loss - 1e-8:
            best_loss = validation_loss
            best_state = deepcopy(
                {key: value.detach().cpu() for key, value in model.state_dict().items()}
            )
            wait = 0
        else:
            wait += 1
        if wait >= options.patience:
            break
    if best_state is None:
        raise RuntimeError("training produced no best state")
    last_state = deepcopy(
        {key: value.detach().cpu() for key, value in model.state_dict().items()}
    )
    model.load_state_dict(best_state)
    best_epoch = int(
        min(history, key=lambda item: item["validation_scaled_smooth_l1"])["epoch"]
    )
    summary = {
        "epochs_completed": len(history),
        "best_epoch": best_epoch,
        "best_validation_scaled_smooth_l1": best_loss,
        "early_stopped": len(history) < options.max_epochs,
        "patience": options.patience,
        "tiny_overfit_initial_loss": initial,
        "tiny_overfit_final_loss": final,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "trainable_parameter_count": sum(
            parameter.numel()
            for parameter in model.parameters()
            if parameter.requires_grad
        ),
        "test_used_for_tuning": False,
    }
    return model, pd.DataFrame(history), best_state, last_state, scaler, summary


def _patchtst_predictions(
    model: PatchTSTRegressor,
    sequences: Sequence[RunSequence],
    *,
    target_scaler: Mapping[str, float],
    device: str,
) -> dict[str, tuple[float, float]]:
    model.eval()
    rows: dict[str, tuple[float, float]] = {}
    with torch.no_grad():
        for sequence in sequences:
            batch = collate_run_sequences([sequence])
            started = time.perf_counter()
            scaled = model(
                batch["inputs"].to(device), batch["time_mask"].to(device)
            ).item()
            elapsed = (time.perf_counter() - started) * 1_000
            prediction = scaled * float(target_scaler["scale"]) + float(
                target_scaler["mean"]
            )
            rows[sequence.sequence_id] = (float(prediction), float(elapsed))
    return rows


def build_predictions(
    sequences: Sequence[RunSequence],
    *,
    patchtst: Mapping[str, tuple[float, float]],
    ridge: Mapping[str, float],
) -> pd.DataFrame:
    train_targets = np.asarray(
        [sequence.target_raw for sequence in sequences if sequence.split == "train"]
    )
    constants = {
        "sensor_training_mean": float(train_targets.mean()),
        "sensor_training_median": float(np.median(train_targets)),
    }
    rows: list[dict[str, Any]] = []
    for sequence in sequences:
        predictions = {
            **{name: (value, 0.0) for name, value in constants.items()},
            "sensor_ridge_run_summary": (ridge[sequence.sequence_id], 0.0),
            "patchtst_sensor_regression": patchtst[sequence.sequence_id],
        }
        for model_name, (value, latency) in predictions.items():
            rows.append(
                {
                    "schema_version": PATCHTST_RESULT_SCHEMA_VERSION,
                    "sequence_id": sequence.sequence_id,
                    "experiment": sequence.experiment,
                    "run": sequence.run,
                    "split": sequence.split,
                    "target_name": "raw_top3_mean_pct",
                    "target_definition_version": "phm2026_image_damage_v2",
                    "target_verification_status": "provisional_pending_human_review",
                    "target_unit": TARGET_UNIT,
                    "y_true_raw": sequence.target_raw,
                    "y_true_monotonic": sequence.target_monotonic,
                    "y_pred": value,
                    "model_name": model_name,
                    "latency_ms": latency,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["model_name", "experiment", "run"], kind="stable"
    )


def build_metric_table(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model_name, split), scoped in predictions.groupby(["model_name", "split"]):
        for target_variant, column in (
            ("raw_top3_mean_pct", "y_true_raw"),
            ("causal_monotonic_top3_mean_pct", "y_true_monotonic"),
        ):
            rows.append(
                {
                    "schema_version": PATCHTST_RESULT_SCHEMA_VERSION,
                    "model_name": model_name,
                    "split": split,
                    "evaluation_level": "experiment_run",
                    "target_variant": target_variant,
                    "unit": TARGET_UNIT,
                    **regression_metrics(scoped[column], scoped.y_pred),
                }
            )
    return pd.DataFrame(rows).sort_values(["target_variant", "split", "model_name"])


def run_patchtst_baseline(
    sequences: Sequence[RunSequence],
    *,
    model_config: PatchTSTConfig,
    training_options: TrainingOptions,
    ridge_alphas: Sequence[float],
    seed: int,
    device: str,
    rtdetr_run_predictions: pd.DataFrame | None = None,
) -> PatchTSTResult:
    ridge, ridge_summary = ridge_predictions(sequences, alphas=ridge_alphas)
    model, history, best, last, target_scaler, training = train_patchtst(
        sequences,
        model_config=model_config,
        options=training_options,
        seed=seed,
        device=device,
    )
    patchtst = _patchtst_predictions(
        model, sequences, target_scaler=target_scaler, device=device
    )
    predictions = build_predictions(sequences, patchtst=patchtst, ridge=ridge)
    metrics = build_metric_table(predictions)
    comparison = metrics[
        metrics.split.eq("test") & metrics.target_variant.eq("raw_top3_mean_pct")
    ].copy()
    comparison["source"] = "sensor_run_pipeline"
    if rtdetr_run_predictions is not None:
        image = rtdetr_run_predictions.copy()
        if {"split", "y_true_raw_top3_mean", "y_pred_raw_top3_mean"}.issubset(image):
            image = image[image.split.eq("test")]
            image_metrics = regression_metrics(
                image.y_true_raw_top3_mean, image.y_pred_raw_top3_mean
            )
            comparison = pd.concat(
                [
                    comparison,
                    pd.DataFrame(
                        [
                            {
                                "schema_version": PATCHTST_RESULT_SCHEMA_VERSION,
                                "model_name": "rtdetr_frozen_encoder_image_regression",
                                "split": "test",
                                "evaluation_level": "experiment_run",
                                "target_variant": "raw_top3_mean_pct",
                                "unit": TARGET_UNIT,
                                **image_metrics,
                                "source": "pinned_existing_image_run",
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
    architecture = pd.DataFrame(
        [
            {
                "stage": "input",
                "shape": "B x T x C",
                "detail": "variable verified minute sequence",
            },
            {
                "stage": "patching",
                "shape": "B x C x N x P",
                "detail": f"P={model_config.patch_length}, stride={model_config.patch_stride}",
            },
            {
                "stage": "projection",
                "shape": "(B*C) x N x D",
                "detail": f"D={model_config.d_model}",
            },
            {
                "stage": "transformer",
                "shape": "(B*C) x N x D",
                "detail": f"layers={model_config.encoder_layers}, heads={model_config.n_heads}",
            },
            {
                "stage": "mask_pool",
                "shape": "B x C x D",
                "detail": "padding-excluding mean over valid patches",
            },
            {
                "stage": "regression",
                "shape": "B",
                "detail": "scalar current end-of-run damage state",
            },
        ]
    )
    environment = {
        "torch_version": torch.__version__,
        "device": device,
        "device_name": (
            torch.cuda.get_device_name(0) if device.startswith("cuda") else "CPU"
        ),
        "cuda_available": torch.cuda.is_available(),
        "max_cuda_memory_allocated_bytes": (
            int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0
        ),
    }
    return PatchTSTResult(
        model_config,
        history,
        predictions,
        metrics,
        comparison,
        architecture,
        training,
        environment,
        best,
        last,
        target_scaler,
        ridge_summary,
    )


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv_path, parquet_path = stem.with_suffix(".csv"), stem.with_suffix(".parquet")
    frame.to_csv(csv_path, index=False)
    frame.to_parquet(parquet_path, index=False)
    return [csv_path, parquet_path]


def _plot_pair(
    frame: pd.DataFrame,
    *,
    run: RunContext,
    name: str,
    x: str,
    y: str,
    title: str,
    xlabel: str,
    ylabel: str,
    kind: str = "line",
) -> list[Path]:
    source = run.run_directory / f"tables/plot_source_{name}.csv"
    frame.to_csv(source, index=False)
    apply_academic_style()
    figure, axis = plt.subplots(figsize=(8.2, 4.8))
    if kind == "scatter":
        for index, (label, scoped) in enumerate(frame.groupby("model_name")):
            axis.scatter(
                scoped[x],
                scoped[y],
                label=label,
                color=ACADEMIC_COLORS[index % len(ACADEMIC_COLORS)],
            )
        limits = [
            min(frame[x].min(), frame[y].min()),
            max(frame[x].max(), frame[y].max()),
        ]
        axis.plot(limits, limits, linestyle="--", color="#555555", linewidth=1)
    else:
        for index, (label, scoped) in enumerate(frame.groupby("model_name")):
            axis.plot(
                scoped[x],
                scoped[y],
                marker="o",
                label=label,
                color=ACADEMIC_COLORS[index % len(ACADEMIC_COLORS)],
            )
    axis.set(title=title, xlabel=xlabel, ylabel=ylabel)
    axis.legend(fontsize=8)
    return [source, *save_figure_pair(figure, run.run_directory / f"figures/{name}")]


def write_patchtst_run(
    result: PatchTSTResult,
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
    feature_normalizer: Mapping[str, Any],
    feature_run_summary: pd.DataFrame,
) -> list[ArtifactRecord]:
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    inputs_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        (
            run.artifact(config_path, role="resolved_configuration"),
            run.artifact(inputs_path, role="input_manifest"),
        )
    )
    tables = {
        "training_history": result.history,
        "predictions": result.predictions,
        "metrics": result.metrics,
        "model_comparison": result.comparison,
        "architecture_tensor_shapes": result.architecture,
        "feature_run_summary": feature_run_summary,
    }
    for name, frame in tables.items():
        for path in _write_frame(frame, run.run_directory / f"tables/{name}"):
            artifacts.append(run.artifact(path, role=name))
    for name, payload in (
        ("feature_normalizer.json", feature_normalizer),
        ("target_scaler.json", result.target_scaler),
        ("training_summary.json", dict(result.training_summary)),
        ("ridge_selection.json", dict(result.ridge_summary)),
        ("environment.json", dict(result.environment)),
    ):
        path = run.run_directory / f"reports/{name}"
        path.write_text(json_text(payload), encoding="utf-8")
        artifacts.append(run.artifact(path, role=name.removesuffix(".json")))
    for state_name, state in (("best", result.best_state), ("last", result.last_state)):
        path = run.run_directory / f"{state_name}_patchtst.pt"
        torch.save(
            {
                "schema_version": PATCHTST_RESULT_SCHEMA_VERSION,
                "model_config": asdict(result.model_config),
                "state_dict": state,
                "target_scaler": dict(result.target_scaler),
                "target_name": "raw_top3_mean_pct",
                "target_definition_version": "phm2026_image_damage_v2",
            },
            path,
        )
        artifacts.append(run.artifact(path, role=f"{state_name}_checkpoint"))

    loss_source = result.history.rename(
        columns={
            "training_scaled_smooth_l1": "train",
            "validation_scaled_smooth_l1": "validation",
        }
    )
    loss_long = loss_source.melt(
        id_vars="epoch",
        value_vars=["train", "validation"],
        var_name="model_name",
        value_name="loss",
    )
    figure_paths = _plot_pair(
        loss_long,
        run=run,
        name="training_validation_loss",
        x="epoch",
        y="loss",
        title="PatchTST training and validation loss",
        xlabel="Epoch",
        ylabel="Scaled smooth L1 loss",
    )
    test_patch = result.predictions[
        result.predictions.split.eq("test")
        & result.predictions.model_name.eq("patchtst_sensor_regression")
    ].copy()
    figure_paths += _plot_pair(
        test_patch,
        run=run,
        name="exp_f_prediction_scatter",
        x="y_true_raw",
        y="y_pred",
        title="EXP-F run target: prediction versus provisional target",
        xlabel="Provisional raw top-3 target (percentage points)",
        ylabel="PatchTST prediction (percentage points)",
        kind="scatter",
    )
    trajectory = result.predictions[
        result.predictions.split.eq("test")
        & result.predictions.model_name.isin(
            ["patchtst_sensor_regression", "sensor_ridge_run_summary"]
        )
    ].copy()
    truth = test_patch.assign(
        model_name="provisional_target", y_pred=test_patch.y_true_raw
    )
    trajectory = pd.concat([trajectory, truth], ignore_index=True)
    figure_paths += _plot_pair(
        trajectory,
        run=run,
        name="exp_f_run_trajectory",
        x="run",
        y="y_pred",
        title="EXP-F end-of-run damage-state trajectory",
        xlabel="EXP-F run",
        ylabel="Percentage points",
    )
    comparison = result.comparison[["model_name", "mae", "rmse", "sample_count"]].copy()
    source = run.run_directory / "tables/plot_source_test_model_comparison.csv"
    comparison.to_csv(source, index=False)
    apply_academic_style()
    figure, axis = plt.subplots(figsize=(9, 4.8))
    indexes = np.arange(len(comparison))
    width = 0.36
    axis.bar(
        indexes - width / 2,
        comparison.mae,
        width,
        label="MAE",
        color=ACADEMIC_COLORS[0],
    )
    axis.bar(
        indexes + width / 2,
        comparison.rmse,
        width,
        label="RMSE",
        color=ACADEMIC_COLORS[2],
    )
    axis.set_xticks(indexes, comparison.model_name, rotation=20, ha="right")
    axis.set_ylabel("Percentage points")
    axis.set_title("EXP-F run-level comparison on matching target and N")
    axis.legend()
    figure_paths += [
        source,
        *save_figure_pair(figure, run.run_directory / "figures/test_model_comparison"),
    ]
    source = run.run_directory / "tables/plot_source_architecture_tensor_shapes.csv"
    result.architecture.to_csv(source, index=False)
    apply_academic_style()
    figure, axis = plt.subplots(figsize=(10, 3.8))
    axis.axis("off")
    axis.text(
        0.02,
        0.55,
        "  →  ".join(result.architecture.stage),
        fontsize=11,
        weight="bold",
        transform=axis.transAxes,
    )
    axis.text(
        0.02,
        0.34,
        "  →  ".join(result.architecture["shape"]),
        fontsize=9,
        transform=axis.transAxes,
    )
    axis.set_title("PatchTST sensor-regression tensor flow")
    figure_paths += [
        source,
        *save_figure_pair(
            figure, run.run_directory / "figures/architecture_tensor_shapes"
        ),
    ]
    for path in figure_paths:
        artifacts.append(
            run.artifact(
                path, role="plot_source" if path.suffix == ".csv" else "figure"
            )
        )

    summary = {
        "schema_version": PATCHTST_RESULT_SCHEMA_VERSION,
        "formulation": "sensor_only_patchtst_style_run_regression",
        "prediction_task": "current end-of-run damage-state estimation, not forecasting",
        "primary_target": "raw_top3_mean_pct",
        "target_status": "provisional_pending_human_review",
        "split": {"train": "EXP-B", "validation": "EXP-A", "test": "EXP-F"},
        "sequence_count": int(result.predictions.sequence_id.nunique()),
        "test_run_count": int(test_patch.sequence_id.nunique()),
        "test_used_for_tuning": False,
        "limitations": [
            "Only low-frequency/context/condition-indicator summaries are used; raw HF vibration is out of this initial baseline.",
            "The image-derived target remains provisional and is not physical ground truth.",
            "Twenty run-level samples make neural-model estimates high variance.",
            "EXP-A Run 2 is retained despite the organizer overlap warning and is reported non-destructively.",
        ],
    }
    report = run.run_directory / "reports/patchtst_baseline_report.md"
    report.write_text(
        "# Initial sensor-only PatchTST baseline\n\n"
        "This run estimates the **current end-of-run** provisional image-derived damage state from compact, chronological one-minute sensor features. It is not six-hour-ahead forecasting.\n\n"
        "The fixed split is EXP-B train, EXP-A validation, and untouched EXP-F test. The primary target is `raw_top3_mean_pct` from `phm2026_image_damage_v2`; it remains provisional pending human image review.\n\n"
        "The initial input deliberately excludes raw 102.4-kHz vibration. It uses bounded LF context, organizer RMS, and FM4/NA4/M6A/ALR summaries. Missing values are training-median imputed and standardized using EXP-B only.\n\n"
        "Metrics in the accompanying tables compare training mean, training median, Ridge, PatchTST, and the pinned image-only RT-DETR result only at matching run-level target and split. With only eight EXP-F test runs, results are descriptive rather than conclusive.\n",
        encoding="utf-8",
    )
    summary_path = run.run_directory / "reports/patchtst_baseline_summary.json"
    summary_path.write_text(json_text(summary), encoding="utf-8")
    artifacts.extend(
        (
            run.artifact(report, role="professor_report"),
            run.artifact(summary_path, role="summary"),
        )
    )
    return finalize_run(run, artifacts)
