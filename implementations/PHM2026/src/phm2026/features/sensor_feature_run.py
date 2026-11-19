"""Versioned artifacts and figures for bounded sensor feature extraction."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..reporting.common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
)
from ..utils.provenance import ArtifactRecord, RunContext
from .sensor_minutes import ChannelSpec


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv_path, parquet_path = stem.with_suffix(".csv"), stem.with_suffix(".parquet")
    frame.to_csv(csv_path, index=False)
    frame.to_parquet(parquet_path, index=False)
    return [csv_path, parquet_path]


def write_sensor_feature_run(
    minute: pd.DataFrame,
    run_summary: pd.DataFrame,
    channel_evidence: pd.DataFrame,
    *,
    channels: Sequence[ChannelSpec],
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
    raw_source_invariance: Mapping[str, Any],
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
    for name, frame in (
        ("minute_feature_table", minute),
        ("sensor_run_sequences", run_summary),
        ("channel_evidence", channel_evidence),
    ):
        for path in _write_frame(frame, run.run_directory / f"tables/{name}"):
            artifacts.append(run.artifact(path, role=name))

    availability_rows = []
    for _, scoped in channel_evidence.groupby("channel"):
        availability_rows.append(
            {
                "channel": scoped.channel.iloc[0],
                "configured_path": scoped.hdf5_path.iloc[0],
                "available_minutes": int(scoped.available.sum()),
                "profiled_minutes": int(len(scoped)),
                "availability_fraction": float(scoped.available.mean()),
                "observed_units_json": json.dumps(
                    sorted(scoped.unit.dropna().astype(str).unique().tolist())
                ),
                "unit_status": (
                    "observed_from_dataset_attribute"
                    if scoped.unit.notna().any()
                    else "not_observed_do_not_infer"
                ),
            }
        )
    availability = pd.DataFrame(availability_rows)
    for path in _write_frame(
        availability, run.run_directory / "tables/channel_availability"
    ):
        artifacts.append(run.artifact(path, role="channel_availability"))
    feature_schema = {
        "schema_version": "1.0.0",
        "row_unit": "one nested low-frequency HDF5 member (officially approximately one minute)",
        "chronology": "verified UTC wf_start_time; archive order is not used for modelling",
        "channel_statistics": [
            "mean",
            "std",
            "median",
            "min",
            "max",
            "last",
            "slope_per_sample",
        ],
        "slope_unit": "value per within-file sample index; not physical time because within-file cadence is not verified",
        "channels": [
            {
                "name": channel.name,
                "hdf5_path": channel.hdf5_path,
                "role": channel.role,
                "expected_unit": channel.expected_unit,
            }
            for channel in channels
        ],
        "missingness": "explicit boolean mask per configured channel",
        "raw_high_frequency_used": False,
        "separate_ci_archive_used": False,
    }
    warnings = {
        "schema_version": "1.0.0",
        "warnings": [
            "Targets are provisional image-derived candidates pending human review.",
            "EXP-A Run 2 is included and retains the organizer-reported overlap warning.",
            "Records without a verified timestamp remain in the table but are excluded from model sequences.",
            "Channel physical units are not inferred when HDF5 unit attributes are absent.",
            "No raw high-frequency vibration features are included in this initial baseline.",
        ],
    }
    summary = {
        "schema_version": "1.0.0",
        "source_member_count": int(len(minute)),
        "included_sequence_minute_count": int(
            minute.sequence_inclusion_status.eq("included").sum()
        ),
        "excluded_sequence_minute_count": int(
            minute.sequence_inclusion_status.eq("excluded").sum()
        ),
        "run_sequence_count": int(len(run_summary)),
        "experiment_count": int(run_summary.experiment.nunique()),
        "counts_by_experiment": minute.groupby("experiment")
        .size()
        .astype(int)
        .to_dict(),
        "timestamp_status_counts": minute.timestamp_status.value_counts(dropna=False)
        .astype(int)
        .to_dict(),
        "raw_source_invariance": dict(raw_source_invariance),
    }
    for name, payload in (
        ("feature_schema.json", feature_schema),
        ("warnings.json", warnings),
        ("sensor_feature_summary.json", summary),
        ("raw_source_invariance.json", dict(raw_source_invariance)),
    ):
        path = run.run_directory / f"reports/{name}"
        path.write_text(json_text(payload), encoding="utf-8")
        artifacts.append(run.artifact(path, role=name.removesuffix(".json")))

    figure_sources: list[Path] = []
    duration_source = run_summary[
        [
            "experiment",
            "run",
            "included_minute_count",
            "excluded_minute_count",
            "timestamp_span_seconds",
        ]
    ].copy()
    path = run.run_directory / "tables/plot_source_sequence_length_by_run.csv"
    duration_source.to_csv(path, index=False)
    figure_sources.append(path)
    apply_academic_style()
    figure, axis = plt.subplots(figsize=(10, 5))
    labels = [f"{row.experiment}\nR{row.run}" for row in duration_source.itertuples()]
    colors = [
        ACADEMIC_COLORS[["EXP-A", "EXP-B", "EXP-F"].index(value)]
        for value in duration_source.experiment
    ]
    axis.bar(labels, duration_source.included_minute_count, color=colors)
    axis.set(
        title="Verified chronological minute records by experiment/run",
        ylabel="Included HDF5 records",
        xlabel="Experiment and run",
    )
    axis.tick_params(axis="x", labelsize=8)
    figure_sources.extend(
        save_figure_pair(figure, run.run_directory / "figures/sequence_length_by_run")
    )

    heat_rows = []
    for row in run_summary.itertuples():
        for channel in channels:
            heat_rows.append(
                {
                    "experiment": row.experiment,
                    "run": row.run,
                    "channel": channel.name,
                    "availability_fraction": 1.0
                    - getattr(row, f"{channel.name}_missing_fraction"),
                }
            )
    heat = pd.DataFrame(heat_rows)
    path = run.run_directory / "tables/plot_source_channel_availability_by_run.csv"
    heat.to_csv(path, index=False)
    figure_sources.append(path)
    matrix = heat.pivot(
        index=["experiment", "run"], columns="channel", values="availability_fraction"
    )
    apply_academic_style()
    figure, axis = plt.subplots(figsize=(10, 6))
    image = axis.imshow(
        matrix.to_numpy(), aspect="auto", vmin=0, vmax=1, cmap="viridis"
    )
    axis.set_xticks(
        np.arange(len(matrix.columns)), matrix.columns, rotation=35, ha="right"
    )
    axis.set_yticks(
        np.arange(len(matrix.index)), [f"{e} R{r}" for e, r in matrix.index]
    )
    axis.set_title("Configured channel availability by run")
    figure.colorbar(image, ax=axis, label="Available fraction")
    figure_sources.extend(
        save_figure_pair(
            figure, run.run_directory / "figures/channel_availability_by_run"
        )
    )
    for path in figure_sources:
        artifacts.append(
            run.artifact(
                path, role="plot_source" if path.suffix == ".csv" else "figure"
            )
        )

    report = run.run_directory / "reports/sensor_feature_report.md"
    report.write_text(
        "# Bounded PHM minute-feature extraction\n\n"
        f"The versioned table contains {len(minute):,} LF HDF5 source records across {len(run_summary)} experiment/runs. "
        f"{summary['included_sequence_minute_count']:,} have verified UTC `wf_start_time` and enter chronological model sequences; "
        f"{summary['excluded_sequence_minute_count']:,} remain traceable but excluded.\n\n"
        "Each source HDF5 file is materialized and processed one at a time from its nested ZIP. Only compact statistics are retained. "
        "No HDF5, waveform, or full sensor array is cached. The initial baseline deliberately uses LF context, organizer RMS, and four condition indicators; it does not use raw high-frequency vibration.\n\n"
        "Physical units are recorded only when present in source attributes. The target is the provisional `phm2026_image_damage_v2` end-of-run image-derived target and is not organizer ground truth.\n",
        encoding="utf-8",
    )
    artifacts.append(run.artifact(report, role="feature_report"))
    return finalize_run(run, artifacts)
