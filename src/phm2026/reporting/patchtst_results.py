"""Professor-ready figures and report for the initial sensor PatchTST baseline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Callable
import json
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..evaluation.regression import regression_metrics
from ..evaluation.sensor_regression import sensor_metric_table
from .common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
)
from ..utils.provenance import ArtifactRecord, RunContext


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv_path, parquet_path = stem.with_suffix(".csv"), stem.with_suffix(".parquet")
    frame.to_csv(csv_path, index=False)
    frame.to_parquet(parquet_path, index=False)
    return [csv_path, parquet_path]


def _figure(
    frame: pd.DataFrame,
    *,
    run: RunContext,
    name: str,
    draw: Callable[[plt.Axes, pd.DataFrame], None],
    size: tuple[float, float] = (9.2, 5.2),
) -> list[Path]:
    source = run.run_directory / f"tables/plot_source_{name}.csv"
    frame.to_csv(source, index=False)
    apply_academic_style()
    figure, axis = plt.subplots(figsize=size)
    draw(axis, frame)
    return [source, *save_figure_pair(figure, run.run_directory / f"figures/{name}")]


def _image_metric_row(image: pd.DataFrame) -> dict[str, Any]:
    scoped = image[image.split.eq("test")]
    return {
        "model_name": "rtdetr_frozen_encoder_image_regression",
        "split": "test",
        "evaluation_level": "experiment_run",
        "target_variant": "raw_top3_mean_pct",
        "unit": "percentage_points_visible_flank_candidate_area",
        **regression_metrics(scoped.y_true_raw_top3_mean, scoped.y_pred_raw_top3_mean),
        "target_min": float(scoped.y_true_raw_top3_mean.min()),
        "target_max": float(scoped.y_true_raw_top3_mean.max()),
        "prediction_min": float(scoped.y_pred_raw_top3_mean.min()),
        "prediction_max": float(scoped.y_pred_raw_top3_mean.max()),
        "source_modality": "post_run_tooth_images",
    }


def write_patchtst_results_run(
    *,
    minute: pd.DataFrame,
    run_summary: pd.DataFrame,
    channel_availability: pd.DataFrame,
    predictions: pd.DataFrame,
    history: pd.DataFrame,
    architecture: pd.DataFrame,
    feature_normalizer: Mapping[str, Any],
    training_summary: Mapping[str, Any],
    environment: Mapping[str, Any],
    image_predictions: pd.DataFrame,
    bootstrap_repetitions: int,
    seed: int,
    starting_free_bytes: int,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
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
    metrics = sensor_metric_table(
        predictions, repetitions=bootstrap_repetitions, seed=seed
    )
    image_row = _image_metric_row(image_predictions)
    comparison = metrics[
        metrics.split.eq("test") & metrics.target_variant.eq("raw_top3_mean_pct")
    ].copy()
    comparison["source_modality"] = "within_run_sensor_history"
    comparison = pd.concat([comparison, pd.DataFrame([image_row])], ignore_index=True)
    for name, frame in (
        ("run_level_predictions", predictions),
        ("run_level_metrics_with_intervals", metrics),
        ("matching_modality_comparison", comparison),
        ("sensor_run_sequences", run_summary),
        ("channel_availability", channel_availability),
    ):
        for path in _write_frame(frame, run.run_directory / f"tables/{name}"):
            artifacts.append(run.artifact(path, role=name))

    figures: list[Path] = []
    funnel = pd.DataFrame(
        [
            {"stage": "LF HDF5 source records", "count": len(minute)},
            {
                "stage": "Verified chronological records",
                "count": int(minute.sequence_inclusion_status.eq("included").sum()),
            },
            {"stage": "Independent run sequences", "count": len(run_summary)},
            {
                "stage": "Train runs (EXP-B)",
                "count": int(run_summary.split.eq("train").sum()),
            },
            {
                "stage": "Validation runs (EXP-A)",
                "count": int(run_summary.split.eq("validation").sum()),
            },
            {
                "stage": "Test runs (EXP-F)",
                "count": int(run_summary.split.eq("test").sum()),
            },
        ]
    )
    figures += _figure(
        funnel,
        run=run,
        name="sensor_dataset_funnel",
        draw=lambda axis, frame: (
            axis.barh(frame.stage, frame["count"], color=ACADEMIC_COLORS[0]),
            axis.invert_yaxis(),
            axis.set_title(
                "Sensor dataset funnel: records are not independent samples"
            ),
            axis.set_xlabel("Count"),
        ),
    )

    lengths = run_summary[
        ["experiment", "run", "split", "included_minute_count"]
    ].copy()
    lengths["label"] = lengths.experiment + " R" + lengths.run.astype(str)
    figures += _figure(
        lengths,
        run=run,
        name="minute_records_per_run",
        draw=lambda axis, frame: (
            axis.bar(
                frame.label,
                frame.included_minute_count,
                color=[
                    ACADEMIC_COLORS[["EXP-A", "EXP-B", "EXP-F"].index(value)]
                    for value in frame.experiment
                ],
            ),
            axis.tick_params(axis="x", rotation=65, labelsize=8),
            axis.set(
                title="Verified minute records per run",
                ylabel="Minute-level HDF5 records",
                xlabel="Experiment/run",
            ),
        ),
    )
    duration = run_summary[["experiment", "run", "timestamp_span_seconds"]].copy()
    duration["duration_hours"] = duration.timestamp_span_seconds / 3600
    figures += _figure(
        duration,
        run=run,
        name="run_duration_distribution",
        draw=lambda axis, frame: (
            axis.hist(
                frame.duration_hours,
                bins=8,
                color=ACADEMIC_COLORS[1],
                edgecolor="white",
            ),
            axis.axvline(
                6, linestyle="--", color=ACADEMIC_COLORS[3], label="Nominal six hours"
            ),
            axis.set(
                title="Observed timestamp-span distribution",
                xlabel="First-to-last verified timestamp span (hours)",
                ylabel="Run count",
            ),
            axis.legend(),
        ),
    )
    heat_rows = []
    channel_names = [
        column.removesuffix("_missing_fraction")
        for column in run_summary.columns
        if column.endswith("_missing_fraction")
    ]
    for row in run_summary.itertuples():
        for channel in channel_names:
            heat_rows.append(
                {
                    "experiment": row.experiment,
                    "run": row.run,
                    "channel": channel,
                    "available_fraction": 1.0
                    - float(getattr(row, f"{channel}_missing_fraction")),
                }
            )
    heat = pd.DataFrame(heat_rows)

    def draw_heat(axis: plt.Axes, frame: pd.DataFrame) -> None:
        matrix = frame.pivot(
            index=["experiment", "run"], columns="channel", values="available_fraction"
        )
        image = axis.imshow(
            matrix.to_numpy(), aspect="auto", vmin=0, vmax=1, cmap="viridis"
        )
        axis.set_xticks(
            np.arange(len(matrix.columns)), matrix.columns, rotation=35, ha="right"
        )
        axis.set_yticks(
            np.arange(len(matrix.index)), [f"{e} R{r}" for e, r in matrix.index]
        )
        axis.set_title("Channel availability by experiment/run")
        axis.figure.colorbar(image, ax=axis, label="Available fraction")

    figures += _figure(
        heat, run=run, name="channel_availability_heatmap", draw=draw_heat
    )

    example = minute[
        minute.experiment.eq("EXP-A")
        & minute.run.eq(1)
        & minute.sequence_inclusion_status.eq("included")
    ].sort_values("sequence_position")
    normalizer_columns = list(feature_normalizer["feature_columns"])
    normalizer_mean = np.asarray(feature_normalizer["means"])
    normalizer_scale = np.asarray(feature_normalizer["scales"])
    example_rows = []
    for feature in ("rpm_mean", "torque_mean", "temperature_mean"):
        index = normalizer_columns.index(feature)
        values = (
            example[feature].to_numpy(float) - normalizer_mean[index]
        ) / normalizer_scale[index]
        example_rows.extend(
            {
                "sequence_position": int(position),
                "feature": feature,
                "normalized_value": float(value),
                "selection_rule": "lexicographically_first_validation_run_EXP-A_run-1",
            }
            for position, value in zip(example.sequence_position, values)
        )
    example_frame = pd.DataFrame(example_rows)
    figures += _figure(
        example_frame,
        run=run,
        name="example_normalized_sensor_sequence",
        draw=lambda axis, frame: (
            [
                axis.plot(
                    scoped.sequence_position,
                    scoped.normalized_value,
                    label=name,
                    linewidth=1,
                )
                for name, scoped in frame.groupby("feature")
            ],
            axis.set(
                title="Deterministic example: normalized EXP-A Run 1 context",
                xlabel="Verified chronological minute position",
                ylabel="EXP-B-normalized value",
            ),
            axis.legend(),
        ),
    )
    target = run_summary[
        [
            "experiment",
            "run",
            "split",
            "raw_top3_mean_pct",
            "causal_monotonic_top3_mean_pct",
        ]
    ].copy()
    figures += _figure(
        target,
        run=run,
        name="target_distribution_by_split",
        draw=lambda axis, frame: (
            [
                axis.scatter(
                    [split] * len(scoped),
                    scoped.raw_top3_mean_pct,
                    label=split,
                    color=ACADEMIC_COLORS[index],
                )
                for index, (split, scoped) in enumerate(frame.groupby("split"))
            ],
            axis.set(
                title="Provisional raw top-3 target by fixed split",
                xlabel="Split",
                ylabel="Percentage points of visible-flank candidate area",
            ),
        ),
    )

    def draw_arch(axis: plt.Axes, frame: pd.DataFrame) -> None:
        axis.axis("off")
        axis.text(
            0.02,
            0.62,
            "  →  ".join(frame.stage),
            fontsize=11,
            weight="bold",
            transform=axis.transAxes,
        )
        axis.text(
            0.02,
            0.38,
            "  →  ".join(frame["shape"]),
            fontsize=9,
            transform=axis.transAxes,
        )
        axis.set_title("Compact channel-independent PatchTST tensor flow")

    figures += _figure(
        architecture,
        run=run,
        name="patchtst_architecture_tensor_shapes",
        draw=draw_arch,
        size=(11, 4),
    )
    loss = history.rename(
        columns={
            "training_scaled_smooth_l1": "training",
            "validation_scaled_smooth_l1": "validation",
        }
    ).melt(
        id_vars="epoch",
        value_vars=["training", "validation"],
        var_name="series",
        value_name="scaled_smooth_l1",
    )
    figures += _figure(
        loss,
        run=run,
        name="training_validation_loss",
        draw=lambda axis, frame: (
            [
                axis.plot(
                    scoped.epoch,
                    scoped.scaled_smooth_l1,
                    marker="o",
                    label=name,
                    color=ACADEMIC_COLORS[index],
                )
                for index, (name, scoped) in enumerate(frame.groupby("series"))
            ],
            axis.set(
                title="PatchTST training and validation loss",
                xlabel="Epoch",
                ylabel="Scaled smooth L1 loss",
            ),
            axis.legend(),
        ),
    )
    test = predictions[
        predictions.split.eq("test")
        & predictions.model_name.eq("patchtst_sensor_regression")
    ].copy()
    figures += _figure(
        test,
        run=run,
        name="prediction_vs_target_scatter",
        draw=lambda axis, frame: (
            axis.scatter(frame.y_true_raw, frame.y_pred, color=ACADEMIC_COLORS[0]),
            axis.plot(
                [
                    min(frame.y_true_raw.min(), frame.y_pred.min()),
                    max(frame.y_true_raw.max(), frame.y_pred.max()),
                ],
                [
                    min(frame.y_true_raw.min(), frame.y_pred.min()),
                    max(frame.y_true_raw.max(), frame.y_pred.max()),
                ],
                "--",
                color="#555555",
            ),
            axis.set(
                title="EXP-F PatchTST prediction versus provisional target (N=8)",
                xlabel="Raw top-3 target (percentage points)",
                ylabel="Prediction (percentage points)",
            ),
        ),
    )
    residual = test.assign(residual=test.y_pred - test.y_true_raw)
    figures += _figure(
        residual,
        run=run,
        name="residual_vs_prediction",
        draw=lambda axis, frame: (
            axis.scatter(frame.y_pred, frame.residual, color=ACADEMIC_COLORS[4]),
            axis.axhline(0, linestyle="--", color="#555555"),
            axis.set(
                title="EXP-F PatchTST residuals",
                xlabel="Prediction (percentage points)",
                ylabel="Prediction − target (percentage points)",
            ),
        ),
    )
    trajectory = predictions[
        predictions.split.eq("test")
        & predictions.model_name.eq("patchtst_sensor_regression")
    ].copy()
    trajectory = pd.concat(
        [
            trajectory.assign(series="PatchTST", value=trajectory.y_pred),
            trajectory.assign(series="provisional target", value=trajectory.y_true_raw),
        ]
    )
    figures += _figure(
        trajectory,
        run=run,
        name="exp_f_target_prediction_trajectory",
        draw=lambda axis, frame: (
            [
                axis.plot(
                    scoped.run,
                    scoped.value,
                    marker="o",
                    label=name,
                    color=ACADEMIC_COLORS[index],
                )
                for index, (name, scoped) in enumerate(frame.groupby("series"))
            ],
            axis.set(
                title="EXP-F end-of-run damage-state trajectory",
                xlabel="Run",
                ylabel="Percentage points",
            ),
            axis.legend(),
        ),
    )
    sensor_compare = metrics[
        metrics.split.eq("test") & metrics.target_variant.eq("raw_top3_mean_pct")
    ][["model_name", "mae", "rmse", "sample_count"]].copy()
    figures += _figure(
        sensor_compare,
        run=run,
        name="sensor_baseline_comparison",
        draw=lambda axis, frame: (
            axis.bar(
                np.arange(len(frame)) - 0.18,
                frame.mae,
                0.36,
                label="MAE",
                color=ACADEMIC_COLORS[0],
            ),
            axis.bar(
                np.arange(len(frame)) + 0.18,
                frame.rmse,
                0.36,
                label="RMSE",
                color=ACADEMIC_COLORS[2],
            ),
            axis.set_xticks(
                np.arange(len(frame)), frame.model_name, rotation=20, ha="right"
            ),
            axis.set(
                title="EXP-F sensor baselines on identical run targets (N=8)",
                ylabel="Percentage points",
            ),
            axis.legend(),
        ),
    )
    modality = comparison[
        comparison.model_name.isin(
            ["patchtst_sensor_regression", "rtdetr_frozen_encoder_image_regression"]
        )
    ][["model_name", "mae", "rmse", "sample_count", "source_modality"]].copy()
    figures += _figure(
        modality,
        run=run,
        name="image_rtdetr_vs_sensor_patchtst",
        draw=lambda axis, frame: (
            axis.bar(
                np.arange(len(frame)) - 0.18,
                frame.mae,
                0.36,
                label="MAE",
                color=ACADEMIC_COLORS[1],
            ),
            axis.bar(
                np.arange(len(frame)) + 0.18,
                frame.rmse,
                0.36,
                label="RMSE",
                color=ACADEMIC_COLORS[3],
            ),
            axis.set_xticks(
                np.arange(len(frame)), frame.model_name, rotation=15, ha="right"
            ),
            axis.set(
                title="Separate-modality comparison at matching EXP-F run level (N=8)",
                ylabel="Percentage points",
            ),
            axis.legend(),
        ),
    )
    for path in figures:
        artifacts.append(
            run.artifact(
                path, role="plot_source" if path.suffix == ".csv" else "figure"
            )
        )

    test_metrics = metrics[
        metrics.split.eq("test") & metrics.target_variant.eq("raw_top3_mean_pct")
    ].sort_values("mae")
    metric_lines = "\n".join(
        f"- `{row.model_name}`: MAE {row.mae:.3f}, RMSE {row.rmse:.3f}, Spearman {row.spearman}, R² {row.r2}, N={row.sample_count}."
        for row in test_metrics.itertuples()
    )
    report = run.run_directory / "reports/professor_patchtst_baseline.md"
    report.write_text(
        "# Professor report: initial sensor-only PatchTST baseline\n\n"
        "## Scientific formulation\n\nThe model estimates the **current post-run damage state** from sensor history collected during that run. Six hours is a typical run/cadence description, not a forecast horizon. The primary response is the provisional image-derived `raw_top3_mean_pct` from `phm2026_image_damage_v2`; it is not organizer ground truth or validated physical spall area.\n\n"
        "## Dataset and split\n\nThere are 20 independent run sequences: EXP-B (7) trains, EXP-A (5) validates/early-stops, and EXP-F (8) is evaluated once after configuration selection. The 7,119 chronological minute records are repeated observations within those 20 samples, not independent labels. Five timestamp-missing EXP-F records remain traceable but are excluded.\n\n"
        "## Inputs and preprocessing\n\nThe initial bounded baseline uses RPM, torque, temperature, organizer axial/radial RMS, and FM4/NA4/M6A/ALR from LF archives. Each minute/channel contributes mean, population standard deviation, median, min, max, last, and slope per within-file sample index plus a channel missingness mask. EXP-B alone supplies imputation medians and scaling statistics. No raw high-frequency waveform or FFT cache is used.\n\n"
        "## EXP-F raw-target results\n\n"
        + metric_lines
        + "\n\nPatchTST does **not** outperform the constant sensor baselines on EXP-F in this canonical seed. Ridge is severely unstable because the summary dimension is large relative to seven training runs. Negative results are retained without EXP-F tuning. Run-bootstrap intervals are included but are intrinsically unstable at N=8.\n\n"
        "## Interpretation\n\nThis result does not establish that sensor history lacks damage information. It shows that this compact initial representation/model, trained on seven runs under strong domain separation, does not beat a constant baseline on the provisional target. The image-only RT-DETR comparison is descriptive and uses the same EXP-F run target rows, but it is a separate modality.\n\n"
        "## Next gate\n\nBefore any complex PatchTST or fusion work: complete human review of the image-derived target, review LF channel/path/unit coverage, and pre-register a small number of train/validation-only changes. Do not use EXP-F to select them.\n",
        encoding="utf-8",
    )
    index = run.run_directory / "reports/FIGURE_INDEX.md"
    index.write_text(
        "# Figure index\n\nAll figures have same-stem source CSV tables under `tables/` and both 300-DPI PNG and SVG forms.\n\n"
        + "\n".join(
            f"- `{path.stem}` — deterministic plot generated from `tables/plot_source_{path.stem}.csv`."
            for path in figures
            if path.suffix == ".png"
        )
        + "\n",
        encoding="utf-8",
    )
    ending_free = shutil.disk_usage(run.repository_root).free
    warnings = {
        "schema_version": "1.0.0",
        "warnings": [
            "Target is provisional pending human image review.",
            "Only 20 independent runs exist; neural and confidence-interval estimates are unstable.",
            "EXP-F was evaluated once and was not used for selection.",
            "PatchTST did not outperform constant baselines on the primary EXP-F target.",
            "Raw high-frequency vibration is intentionally absent from this initial bounded baseline.",
        ],
    }
    disk = {
        "starting_free_bytes": starting_free_bytes,
        "free_bytes_before_final_manifest": ending_free,
        "minimum_required_free_bytes": 53_687_091_200,
        "gate_satisfied": ending_free >= 53_687_091_200,
    }
    summary = {
        "schema_version": "1.0.0",
        "feature_run_id": "20260814T121146792755Z-4016432b",
        "model_run_id": "20260814T121641338050Z-433d4154",
        "independent_run_count": 20,
        "split_counts": {"train_EXP-B": 7, "validation_EXP-A": 5, "test_EXP-F": 8},
        "primary_target": "raw_top3_mean_pct",
        "secondary_target": "causal_monotonic_top3_mean_pct",
        "target_status": "provisional_pending_human_review",
        "training_summary": dict(training_summary),
        "environment": dict(environment),
        "test_metrics": test_metrics.to_dict(orient="records"),
        "scientific_conclusion": "PatchTST did not outperform constant baselines on untouched EXP-F in the canonical initial run.",
    }
    for name, payload in (
        ("warnings.json", warnings),
        ("disk_usage.json", disk),
        ("patchtst_results_summary.json", summary),
    ):
        path = run.run_directory / f"reports/{name}"
        path.write_text(json_text(payload), encoding="utf-8")
        artifacts.append(run.artifact(path, role=name.removesuffix(".json")))
    artifacts.extend(
        (
            run.artifact(report, role="professor_report"),
            run.artifact(index, role="figure_index"),
        )
    )
    return finalize_run(run, artifacts)
