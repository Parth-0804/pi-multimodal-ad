"""Presentation-ready dataset figures generated only from pinned D artifacts."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

from ..utils.provenance import ArtifactRecord, RunContext
from .common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
    write_csv,
)

SCHEMA_VERSION = "1.0.0"
SENSOR_SCOPE = "bounded representative EXP-A Run-1 coverage"


@dataclass(frozen=True, slots=True)
class DatasetEvidenceResult:
    tables: Mapping[str, list[dict[str, Any]]]
    source_index: tuple[dict[str, Any], ...]
    summary: Mapping[str, Any]


def _evidence(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_run_id": source["source_run_id"],
        "source_artifact_path": source["artifact_path"],
        "source_artifact_sha256": source["artifact_sha256"],
    }


def _image_counts(
    images: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    counts = images.groupby("experiment", dropna=False).size()
    return [
        {
            "schema_version": SCHEMA_VERSION,
            "experiment": str(experiment),
            "image_count": int(count),
            "coverage_scope": "complete image-header coverage",
            **_evidence(source),
        }
        for experiment, count in counts.sort_index().items()
    ]


def _run_coverage(
    assets: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    configured = {"EXP-A": range(1, 6), "EXP-B": range(1, 8), "EXP-F": range(1, 9)}
    rows: list[dict[str, Any]] = []
    for experiment, runs in configured.items():
        scoped = assets[assets["experiment"].eq(experiment)]
        for run in runs:
            run_values = pd.to_numeric(scoped["run"], errors="coerce")
            selected = scoped[run_values.eq(run)]
            rows.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "experiment": experiment,
                    "run_or_scope": f"Run {run}",
                    "high_frequency_archives": int(
                        selected["modality"].eq("high_frequency").sum()
                    ),
                    "image_archives": int(selected["modality"].eq("image").sum()),
                    "low_frequency_archives": 0,
                    "condition_indicator_archives": 0,
                    "scope_note": "filename-level run coverage",
                    **_evidence(source),
                }
            )
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "experiment": experiment,
                "run_or_scope": "Experiment aggregate",
                "high_frequency_archives": 0,
                "image_archives": int(
                    (scoped["modality"].eq("image") & scoped["run"].isna()).sum()
                ),
                "low_frequency_archives": int(
                    scoped["modality"].eq("low_frequency").sum()
                ),
                "condition_indicator_archives": int(
                    scoped["modality"].eq("condition_indicator").sum()
                ),
                "scope_note": "aggregate archives or non-run photo stages",
                **_evidence(source),
            }
        )
    return rows


def _inventory_summary(
    assets: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    rows = []
    for modality, group in assets.groupby("modality", sort=True):
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "modality": str(modality),
                "archive_count": int(len(group)),
                "central_directory_member_count": int(group["member_count"].sum()),
                "nested_zip_member_count": int(
                    group["nested_archive_member_count"].sum()
                ),
                "outer_size_gib": float(group["size_bytes"].sum() / 1024**3),
                "member_interpretation": "central-directory members; not model samples",
                **_evidence(source),
            }
        )
    return rows


def _schema_counts(
    hdf5_members: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    success = hdf5_members[hdf5_members["status"].eq("ok")]
    counts = success["file_schema_id"].fillna("UNKNOWN").value_counts()
    return [
        {
            "schema_version": SCHEMA_VERSION,
            "file_schema_id": str(schema_id),
            "hdf5_member_count": int(count),
            "coverage_scope": SENSOR_SCOPE,
            **_evidence(source),
        }
        for schema_id, count in counts.items()
    ]


def _shape_counts(
    sensors: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    counts = sensors["shape_json"].fillna("UNKNOWN").value_counts()
    return [
        {
            "schema_version": SCHEMA_VERSION,
            "shape_json": str(shape),
            "dataset_row_count": int(count),
            "coverage_scope": SENSOR_SCOPE,
            **_evidence(source),
        }
        for shape, count in counts.items()
    ]


def _rate_counts(
    sensors: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    rates = pd.to_numeric(sensors["sampling_rate_hz"], errors="coerce").dropna()
    counts = rates.value_counts().sort_index()
    return [
        {
            "schema_version": SCHEMA_VERSION,
            "sampling_rate_hz": float(rate),
            "dataset_row_count": int(count),
            "coverage_scope": SENSOR_SCOPE,
            **_evidence(source),
        }
        for rate, count in counts.items()
    ]


def _image_structure(
    images: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    columns = ["shape_hwc_json", "color_mode", "dtype", "bit_depth", "file_format"]
    counts = (
        images.groupby(columns, dropna=False).size().reset_index(name="image_count")
    )
    return [
        {
            "schema_version": SCHEMA_VERSION,
            **{column: row[column] for column in columns},
            "image_count": int(row["image_count"]),
            "coverage_scope": "complete image-header coverage",
            **_evidence(source),
        }
        for _, row in counts.iterrows()
    ]


def _timestamp_counts(
    images: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    mapping = {
        "verified_utc": "Verified UTC",
        "timezone_unknown": "Local-naive / timezone unknown",
        "missing": "Missing",
    }
    counts = images["timestamp_status"].fillna("missing").value_counts()
    return [
        {
            "schema_version": SCHEMA_VERSION,
            "timestamp_status": key,
            "display_label": label,
            "image_count": int(counts.get(key, 0)),
            "alignment_authorized": False,
            **_evidence(source),
        }
        for key, label in mapping.items()
    ]


def _confidence_matrix(
    sources: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    definitions = (
        (
            "Archive central-directory inventory",
            "complete",
            "All 52 archive central directories",
        ),
        ("Image headers", "complete", "All 1,311 discovered JPG headers"),
        ("Sensor structure", "representative", SENSOR_SCOPE),
        (
            "Sensor value statistics",
            "sampled",
            "One HF member; deterministic bounded values",
        ),
        ("Image pixel quality / hashes", "sampled", "104 deterministic images"),
        (
            "Image–sensor alignment",
            "blocked/unknown",
            "No verified comparable image clock",
        ),
        (
            "Scalar target and six-hour semantics",
            "blocked/unknown",
            "No authoritative definition",
        ),
    )
    source_lookup = {
        "complete": sources["professor_description"],
        "representative": sources["sensor_profile"],
        "sampled": sources["professor_description"],
        "blocked/unknown": sources["alignment_audit"],
    }
    return [
        {
            "schema_version": SCHEMA_VERSION,
            "evidence_item": item,
            "evidence_class": evidence_class,
            "scope": scope,
            **_evidence(source_lookup[evidence_class]),
        }
        for item, evidence_class, scope in definitions
    ]


def _pipeline_rows() -> list[dict[str, Any]]:
    stages = (
        (1, "D1.1 Inventory", "complete", "52 archives / 8,512 members"),
        (2, "D1.2 Sensors", "representative", "745 HDF5 members / 27,165 datasets"),
        (3, "D1.3 Images", "complete+sampled", "1,311 headers / 104 pixel samples"),
        (
            4,
            "D1.4 Alignment audit",
            "completed-blocked",
            "0 verified image UTC timestamps",
        ),
        (
            5,
            "T2.1 Target gate",
            "blocked/unknown",
            "target and six-hour meaning unresolved",
        ),
        (
            6,
            "RT-DETR",
            "feasibility fallback",
            "pretrained inference only if gate remains blocked",
        ),
    )
    return [
        {
            "schema_version": SCHEMA_VERSION,
            "stage_order": order,
            "stage": stage,
            "status": status,
            "evidence": evidence,
        }
        for order, stage, status, evidence in stages
    ]


def build_dataset_evidence(
    *,
    assets: pd.DataFrame,
    hdf5_members: pd.DataFrame,
    sensors: pd.DataFrame,
    images: pd.DataFrame,
    sources: Mapping[str, Mapping[str, Any]],
) -> DatasetEvidenceResult:
    required = {
        "asset_inventory",
        "sensor_profile",
        "image_profile",
        "alignment_audit",
        "professor_description",
    }
    missing = required.difference(sources)
    if missing:
        raise ValueError("missing evidence sources: " + ", ".join(sorted(missing)))
    tables = {
        "image_counts_by_experiment": _image_counts(images, sources["image_profile"]),
        "modality_coverage_by_experiment_run": _run_coverage(
            assets, sources["asset_inventory"]
        ),
        "archive_member_inventory_summary": _inventory_summary(
            assets, sources["asset_inventory"]
        ),
        "sensor_schema_family_counts": _schema_counts(
            hdf5_members, sources["sensor_profile"]
        ),
        "sensor_shape_family_counts": _shape_counts(sensors, sources["sensor_profile"]),
        "sensor_sampling_rate_families": _rate_counts(
            sensors, sources["sensor_profile"]
        ),
        "image_structural_summary": _image_structure(images, sources["image_profile"]),
        "image_timestamp_status": _timestamp_counts(images, sources["alignment_audit"]),
        "evidence_confidence_matrix": _confidence_matrix(sources),
        "pipeline_stages": _pipeline_rows(),
    }
    source_index = tuple(
        {"schema_version": SCHEMA_VERSION, "source_name": name, **_evidence(source)}
        for name, source in sorted(sources.items())
    )
    summary = {
        "schema_version": SCHEMA_VERSION,
        "figure_count": 10,
        "source_table_count": len(tables),
        "raw_archives_opened": False,
        "sensor_coverage_scope": SENSOR_SCOPE,
        "archive_members_are_model_samples": False,
    }
    return DatasetEvidenceResult(
        tables=tables, source_index=source_index, summary=summary
    )


def _bar_figure(
    rows: Sequence[Mapping[str, Any]],
    *,
    label: str,
    value: str,
    title: str,
    ylabel: str,
) -> plt.Figure:
    frame = pd.DataFrame(rows)
    figure, axis = plt.subplots(figsize=(8.5, 4.8))
    bars = axis.bar(
        frame[label].astype(str), frame[value], color=ACADEMIC_COLORS[: len(frame)]
    )
    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.set_xlabel("")
    for bar, number in zip(bars, frame[value], strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{int(number):,}",
            ha="center",
            va="bottom",
        )
    figure.tight_layout()
    return figure


def _run_coverage_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    frame = pd.DataFrame(rows)
    frame = frame[frame["run_or_scope"].str.startswith("Run")].copy()
    frame["label"] = frame["experiment"] + " " + frame["run_or_scope"]
    values = frame[["high_frequency_archives", "image_archives"]].to_numpy(float)
    figure, axis = plt.subplots(figsize=(11, 7))
    image = axis.imshow(
        values, aspect="auto", cmap="Blues", vmin=0, vmax=max(1, values.max())
    )
    axis.set_xticks([0, 1], ["HF archive", "Photo archive"])
    axis.set_yticks(range(len(frame)), frame["label"])
    axis.set_title("Filename-level modality coverage by experiment and run")
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            axis.text(
                column, row, str(int(values[row, column])), ha="center", va="center"
            )
    figure.colorbar(image, ax=axis, label="Archive count")
    figure.text(
        0.5,
        0.01,
        "LF and CI archives are experiment-level aggregates; archive presence is not sample count.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.035, 1, 1))
    return figure


def _inventory_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    frame = pd.DataFrame(rows).sort_values("archive_count", ascending=False)
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].bar(frame["modality"], frame["archive_count"], color=ACADEMIC_COLORS[0])
    axes[0].set_title("Archives")
    axes[0].set_ylabel("Count")
    axes[0].tick_params(axis="x", rotation=25)
    axes[1].bar(
        frame["modality"],
        frame["central_directory_member_count"],
        color=ACADEMIC_COLORS[1],
    )
    axes[1].set_title("Central-directory members")
    axes[1].set_ylabel("Member records (not model samples)")
    axes[1].tick_params(axis="x", rotation=25)
    figure.suptitle("PHM archive and member inventory")
    figure.tight_layout()
    return figure


def _horizontal_top(
    rows: Sequence[Mapping[str, Any]],
    *,
    label: str,
    value: str,
    title: str,
    top: int | None = None,
) -> plt.Figure:
    frame = pd.DataFrame(rows).sort_values(value, ascending=False)
    if top is not None:
        frame = frame.head(top)
    frame = frame.sort_values(value)
    figure, axis = plt.subplots(figsize=(10, max(4.5, len(frame) * 0.35)))
    axis.barh(frame[label].astype(str), frame[value], color=ACADEMIC_COLORS[0])
    axis.set_title(title)
    axis.set_xlabel("Dataset rows" if "shape" in label else "HDF5 members")
    figure.text(
        0.5,
        0.005,
        "Bounded representative EXP-A Run-1 coverage; not exhaustive across EXP-A/B/F.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.03, 1, 1))
    return figure


def _rates_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    frame = pd.DataFrame(rows)
    figure, axis = plt.subplots(figsize=(9, 4.8))
    axis.scatter(
        frame["sampling_rate_hz"],
        frame["dataset_row_count"],
        s=90,
        color=ACADEMIC_COLORS[1],
    )
    axis.set_xscale("log")
    axis.set_xlabel("Evidenced sampling rate (Hz, log scale)")
    axis.set_ylabel("Dataset rows")
    axis.set_title("Evidenced sensor sampling-rate families")
    for row in frame.itertuples():
        axis.annotate(
            f"{row.sampling_rate_hz:g} Hz\nn={row.dataset_row_count:,}",
            (row.sampling_rate_hz, row.dataset_row_count),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )
    figure.text(
        0.5,
        0.005,
        "Bounded representative EXP-A Run-1 coverage; rates retain recorded/derived evidence.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.03, 1, 1))
    return figure


def _image_structure_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    row = rows[0]
    figure, axis = plt.subplots(figsize=(10, 4.2))
    axis.axis("off")
    cards = [
        ("Images", f"{int(row['image_count']):,}"),
        ("Shape (H×W×C)", str(row["shape_hwc_json"])),
        ("Mode", str(row["color_mode"])),
        ("Data", f"{row['dtype']} / {int(row['bit_depth'])}-bit"),
        ("Format", str(row["file_format"])),
    ]
    for index, (name, value) in enumerate(cards):
        x = 0.02 + index * 0.195
        patch = FancyBboxPatch(
            (x, 0.28),
            0.17,
            0.43,
            boxstyle="round,pad=0.015",
            facecolor="#EEF3F7",
            edgecolor=ACADEMIC_COLORS[0],
            transform=axis.transAxes,
        )
        axis.add_patch(patch)
        axis.text(
            x + 0.085,
            0.57,
            name,
            ha="center",
            va="center",
            fontsize=10,
            transform=axis.transAxes,
        )
        axis.text(
            x + 0.085,
            0.42,
            value,
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            transform=axis.transAxes,
        )
    axis.set_title("Complete PHM image-header structural summary")
    return figure


def _timestamp_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    figure = _bar_figure(
        rows,
        label="display_label",
        value="image_count",
        title="Image timestamp evidence",
        ylabel="Images",
    )
    figure.axes[0].tick_params(axis="x", rotation=12)
    figure.text(
        0.5,
        0.01,
        "0 verified UTC timestamps: image–sensor temporal matching is not authorized.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.04, 1, 1))
    return figure


def _confidence_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    frame = pd.DataFrame(rows)
    classes = ["complete", "representative", "sampled", "blocked/unknown"]
    matrix = np.zeros((len(frame), len(classes)))
    for index, value in enumerate(frame["evidence_class"]):
        matrix[index, classes.index(value)] = 1
    figure, axis = plt.subplots(figsize=(10.5, 5.8))
    axis.imshow(matrix, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    axis.set_xticks(range(len(classes)), [value.title() for value in classes])
    axis.set_yticks(range(len(frame)), frame["evidence_item"])
    axis.set_title("Evidence-confidence matrix")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            if matrix[row, column]:
                axis.text(
                    column,
                    row,
                    "●",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=14,
                )
    figure.tight_layout()
    return figure


def _pipeline_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(14, 3.6))
    axis.axis("off")
    colors = {
        "complete": "#DDEFE3",
        "representative": "#FFF0C9",
        "complete+sampled": "#DDEFE3",
        "completed-blocked": "#F7D7DC",
        "blocked/unknown": "#F7D7DC",
        "feasibility fallback": "#E8E1F2",
    }
    for index, row in enumerate(rows):
        x = 0.015 + index * 0.165
        patch = FancyBboxPatch(
            (x, 0.32),
            0.14,
            0.38,
            boxstyle="round,pad=0.015",
            facecolor=colors[str(row["status"])],
            edgecolor="#4A4A4A",
            transform=axis.transAxes,
        )
        axis.add_patch(patch)
        axis.text(
            x + 0.07,
            0.58,
            row["stage"],
            ha="center",
            va="center",
            fontsize=9.5,
            fontweight="bold",
            transform=axis.transAxes,
        )
        axis.text(
            x + 0.07,
            0.43,
            row["status"],
            ha="center",
            va="center",
            fontsize=8,
            transform=axis.transAxes,
        )
        if index < len(rows) - 1:
            axis.annotate(
                "",
                xy=(x + 0.163, 0.51),
                xytext=(x + 0.143, 0.51),
                xycoords=axis.transAxes,
                arrowprops={"arrowstyle": "->", "color": "#555555"},
            )
    axis.set_title("Evidence pipeline and scientific target gate")
    return figure


def _figure_index(result: DatasetEvidenceResult, run_id: str) -> str:
    descriptions = (
        ("image_counts_by_experiment", "Complete D1.3 header counts by experiment."),
        (
            "modality_coverage_by_experiment_run",
            "Filename-level HF/photo run coverage; LF/CI remain experiment aggregates.",
        ),
        (
            "archive_member_inventory_summary",
            "Archive and central-directory records; members are not samples.",
        ),
        ("sensor_schema_family_counts", "Representative D1.2 file-schema variants."),
        ("sensor_shape_family_counts", "Representative D1.2 dataset shape families."),
        ("sensor_sampling_rate_families", "Evidenced rates on a logarithmic axis."),
        ("image_structural_summary", "Complete image-header structure."),
        ("image_timestamp_status", "Clock evidence and the zero-UTC blocker."),
        (
            "evidence_confidence_matrix",
            "Complete, representative, sampled, and blocked boundaries.",
        ),
        ("pipeline_stages", "Inventory-to-target-gate-to-RT-DETR sequence."),
    )
    lines = [
        "# Dataset-definition figure index",
        "",
        f"Run: `{run_id}`",
        "",
        "Every figure has a source CSV, 300-DPI PNG, SVG, and exact upstream run/hash fields.",
        "",
    ]
    for stem, description in descriptions:
        lines.extend(
            [
                f"## `{stem}`",
                "",
                description,
                "",
                f"- Source: `tables/{stem}.csv`",
                f"- Figures: `figures/{stem}.png`, `figures/{stem}.svg`",
                "",
            ]
        )
    lines.append(
        "Sensor figures are explicitly limited to bounded representative EXP-A Run-1 coverage. Archive-member counts are inventory records, never model-sample counts."
    )
    return "\n".join(lines) + "\n"


def write_dataset_evidence_run(
    result: DatasetEvidenceResult,
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
    run.create_layout()
    apply_academic_style()
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    input_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        [
            run.artifact(config_path, role="resolved_configuration"),
            run.artifact(input_path, role="input_manifest"),
        ]
    )
    for name, rows in result.tables.items():
        path = run.run_directory / f"tables/{name}.csv"
        write_csv(path, rows)
        artifacts.append(run.artifact(path, role=f"{name}_source_csv"))
    source_index_path = run.run_directory / "tables/artifact_source_index.csv"
    write_csv(source_index_path, result.source_index)
    artifacts.append(run.artifact(source_index_path, role="artifact_source_index"))

    figures = {
        "image_counts_by_experiment": _bar_figure(
            result.tables["image_counts_by_experiment"],
            label="experiment",
            value="image_count",
            title="PHM image counts by experiment",
            ylabel="Images (complete header coverage)",
        ),
        "modality_coverage_by_experiment_run": _run_coverage_figure(
            result.tables["modality_coverage_by_experiment_run"]
        ),
        "archive_member_inventory_summary": _inventory_figure(
            result.tables["archive_member_inventory_summary"]
        ),
        "sensor_schema_family_counts": _horizontal_top(
            result.tables["sensor_schema_family_counts"],
            label="file_schema_id",
            value="hdf5_member_count",
            title="Representative HDF5 file-schema families",
        ),
        "sensor_shape_family_counts": _horizontal_top(
            result.tables["sensor_shape_family_counts"],
            label="shape_json",
            value="dataset_row_count",
            title="Representative sensor shape families",
        ),
        "sensor_sampling_rate_families": _rates_figure(
            result.tables["sensor_sampling_rate_families"]
        ),
        "image_structural_summary": _image_structure_figure(
            result.tables["image_structural_summary"]
        ),
        "image_timestamp_status": _timestamp_figure(
            result.tables["image_timestamp_status"]
        ),
        "evidence_confidence_matrix": _confidence_figure(
            result.tables["evidence_confidence_matrix"]
        ),
        "pipeline_stages": _pipeline_figure(result.tables["pipeline_stages"]),
    }
    for name, figure in figures.items():
        for path in save_figure_pair(figure, run.run_directory / f"figures/{name}"):
            artifacts.append(run.artifact(path, role=f"{name}_{path.suffix[1:]}"))
    report_path = run.run_directory / "reports/dataset_figure_index.md"
    report_path.write_text(_figure_index(result, run.run_id), encoding="utf-8")
    summary_path = run.run_directory / "reports/dataset_evidence_summary.json"
    summary_path.write_text(json_text(dict(result.summary)), encoding="utf-8")
    artifacts.extend(
        [
            run.artifact(report_path, role="dataset_figure_index"),
            run.artifact(summary_path, role="dataset_evidence_summary"),
        ]
    )
    return finalize_run(run, artifacts)
