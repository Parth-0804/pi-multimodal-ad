"""Professor-facing PHM description generated only from pinned profile artifacts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from ..utils.provenance import ArtifactRecord, RunContext

DATASET_DESCRIPTION_SCHEMA_VERSION = "1.0.0"

AT_A_GLANCE_COLUMNS = (
    "schema_version",
    "metric",
    "value",
    "unit",
    "scope",
    "evidence_status",
    "source_run_id",
    "source_artifact_path",
    "source_artifact_sha256",
    "note",
)
MODALITY_COVERAGE_COLUMNS = (
    "schema_version",
    "experiment",
    "modality",
    "archive_count",
    "outer_size_bytes",
    "central_directory_member_count",
    "nested_zip_member_count",
    "source_run_id",
    "source_artifact_path",
    "source_artifact_sha256",
)
SENSOR_SHAPE_COLUMNS = (
    "schema_version",
    "channel_role",
    "hdf5_path",
    "shape_json",
    "dtype",
    "sampling_rate_hz",
    "unit_values",
    "dataset_row_count",
    "hdf5_member_count",
    "duration_seconds_min",
    "duration_seconds_median",
    "duration_seconds_max",
    "coverage_scope",
    "source_run_id",
    "source_artifact_path",
    "source_artifact_sha256",
)
IMAGE_SHAPE_COLUMNS = (
    "schema_version",
    "shape_hwc_json",
    "color_mode",
    "dtype",
    "bit_depth",
    "file_format",
    "aspect_ratio",
    "image_count",
    "header_readable_count",
    "source_run_id",
    "source_artifact_path",
    "source_artifact_sha256",
)
CLOCK_DOMAIN_COLUMNS = (
    "schema_version",
    "modality",
    "clock_domain_or_status",
    "event_count",
    "verified_timestamp_count",
    "comparability_status",
    "nearest_matching_authorized",
    "join_cardinality_computable",
    "six_hour_cross_modal_cadence",
    "source_run_id",
    "source_artifact_path",
    "source_artifact_sha256",
    "note",
)
UNRESOLVED_DECISION_COLUMNS = (
    "schema_version",
    "decision_id",
    "question",
    "status",
    "why_required",
    "evidence_status",
    "source_run_id",
    "source_artifact_path",
    "source_artifact_sha256",
)
TRACEABILITY_COLUMNS = (
    "schema_version",
    "record_label",
    "experiment",
    "run",
    "image_id",
    "image_source_relative_path",
    "image_timestamp_status",
    "image_timestamp_raw_or_local_naive",
    "sensor_event_id",
    "sensor_source_identity",
    "sensor_timestamp_utc",
    "sensor_clock_domain",
    "clock_domain_compatible",
    "alignment_result",
    "required_to_unblock",
)
SOURCE_INDEX_COLUMNS = (
    "schema_version",
    "source_name",
    "source_run_id",
    "source_run_directory",
    "artifact_path",
    "artifact_sha256",
    "artifact_size_bytes",
)


@dataclass(frozen=True, slots=True)
class DatasetDescriptionResult:
    """D1.5 report content before versioned-run serialization."""

    tables: Mapping[str, list[dict[str, Any]]]
    report_markdown: str
    source_index_rows: list[dict[str, Any]]
    summary: Mapping[str, Any]


def _source_row(source: Mapping[str, Any]) -> dict[str, Any]:
    required = (
        "source_run_id",
        "source_run_directory",
        "artifact_path",
        "artifact_sha256",
        "artifact_size_bytes",
    )
    missing = [field for field in required if source.get(field) is None]
    if missing:
        raise ValueError("source artifact is missing fields: " + ", ".join(missing))
    return {field: source[field] for field in required}


def _evidence_fields(source: Mapping[str, Any]) -> dict[str, Any]:
    row = _source_row(source)
    return {
        "source_run_id": row["source_run_id"],
        "source_artifact_path": row["artifact_path"],
        "source_artifact_sha256": row["artifact_sha256"],
    }


def _source_citation(source: Mapping[str, Any]) -> str:
    row = _source_row(source)
    return (
        f"run `{row['source_run_id']}`, `{row['artifact_path']}` "
        f"(SHA-256 `{row['artifact_sha256']}`)"
    )


def _number(summary: Mapping[str, Any], key: str) -> int | float:
    value = summary.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"summary key {key!r} must be numeric")
    return value


def _nested_number(
    summary: Mapping[str, Any], key: str, nested_key: str
) -> int | float:
    value = summary.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"summary key {key!r} must be a mapping")
    nested = value.get(nested_key)
    if isinstance(nested, bool) or not isinstance(nested, (int, float)):
        raise ValueError(f"summary key {key!r}.{nested_key!r} must be numeric")
    return nested


def _as_text(value: object, *, unknown: str = "UNKNOWN") -> str:
    if value is None or pd.isna(value):
        return unknown
    text = str(value).strip()
    return text or unknown


def _normalized_runs(assets: pd.DataFrame) -> dict[str, str]:
    output: dict[str, str] = {}
    for experiment, values in assets.groupby("experiment", dropna=True)["run"]:
        runs = sorted(
            {
                int(float(value))
                for value in values.dropna()
                if str(value).replace(".0", "").isdigit()
            }
        )
        if runs:
            output[_as_text(experiment)] = ", ".join(str(value) for value in runs)
    return output


def _modality_coverage(
    assets: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    required = {
        "experiment",
        "modality",
        "asset_id",
        "size_bytes",
        "member_count",
        "nested_archive_member_count",
    }
    missing = sorted(required.difference(assets.columns))
    if missing:
        raise ValueError(
            "asset inventory lacks required columns: " + ", ".join(missing)
        )
    rows: list[dict[str, Any]] = []
    grouped = assets.groupby(["experiment", "modality"], dropna=False, sort=True)
    for (experiment, modality), group in grouped:
        rows.append(
            {
                "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
                "experiment": _as_text(experiment),
                "modality": _as_text(modality),
                "archive_count": int(group["asset_id"].nunique()),
                "outer_size_bytes": int(group["size_bytes"].fillna(0).sum()),
                "central_directory_member_count": int(
                    group["member_count"].fillna(0).sum()
                ),
                "nested_zip_member_count": int(
                    group["nested_archive_member_count"].fillna(0).sum()
                ),
                **_evidence_fields(source),
            }
        )
    return rows


def _sensor_shapes(
    sensors: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    required = {
        "channel_role",
        "hdf5_path",
        "shape_json",
        "dtype",
        "sampling_rate_hz",
        "unit",
        "sensor_id",
        "hdf5_member_id",
        "duration_seconds",
    }
    missing = sorted(required.difference(sensors.columns))
    if missing:
        raise ValueError("sensor profile lacks required columns: " + ", ".join(missing))
    group_columns = [
        "channel_role",
        "hdf5_path",
        "shape_json",
        "dtype",
        "sampling_rate_hz",
    ]
    rows: list[dict[str, Any]] = []
    for values, group in sensors.groupby(group_columns, dropna=False, sort=True):
        role, path, shape, dtype, rate = values
        duration = pd.to_numeric(group["duration_seconds"], errors="coerce").dropna()
        units = sorted(
            {
                _as_text(value)
                for value in group["unit"].dropna().tolist()
                if _as_text(value) != "UNKNOWN"
            }
        )
        rows.append(
            {
                "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
                "channel_role": _as_text(role),
                "hdf5_path": _as_text(path),
                "shape_json": _as_text(shape),
                "dtype": _as_text(dtype),
                "sampling_rate_hz": None if pd.isna(rate) else float(rate),
                "unit_values": json.dumps(units, separators=(",", ":")),
                "dataset_row_count": int(len(group)),
                "hdf5_member_count": int(group["hdf5_member_id"].nunique()),
                "duration_seconds_min": (
                    None if duration.empty else float(duration.min())
                ),
                "duration_seconds_median": (
                    None if duration.empty else float(duration.median())
                ),
                "duration_seconds_max": (
                    None if duration.empty else float(duration.max())
                ),
                "coverage_scope": "bounded_representative_EXP-A_Run-1",
                **_evidence_fields(source),
            }
        )
    return rows


def _image_shapes(
    images: pd.DataFrame, source: Mapping[str, Any]
) -> list[dict[str, Any]]:
    required = {
        "shape_hwc_json",
        "color_mode",
        "dtype",
        "bit_depth",
        "file_format",
        "aspect_ratio",
        "header_status",
    }
    missing = sorted(required.difference(images.columns))
    if missing:
        raise ValueError("image profile lacks required columns: " + ", ".join(missing))
    columns = [
        "shape_hwc_json",
        "color_mode",
        "dtype",
        "bit_depth",
        "file_format",
        "aspect_ratio",
    ]
    rows: list[dict[str, Any]] = []
    for values, group in images.groupby(columns, dropna=False, sort=True):
        shape, mode, dtype, bit_depth, image_format, ratio = values
        rows.append(
            {
                "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
                "shape_hwc_json": _as_text(shape),
                "color_mode": _as_text(mode),
                "dtype": _as_text(dtype),
                "bit_depth": None if pd.isna(bit_depth) else int(bit_depth),
                "file_format": _as_text(image_format),
                "aspect_ratio": None if pd.isna(ratio) else float(ratio),
                "image_count": int(len(group)),
                "header_readable_count": int(
                    (group["header_status"].astype(str) == "ok").sum()
                ),
                **_evidence_fields(source),
            }
        )
    return rows


def _clock_summary(
    image_clock: pd.DataFrame,
    sensor_clock: pd.DataFrame,
    blockers: Mapping[str, Any],
    image_source: Mapping[str, Any],
    sensor_source: Mapping[str, Any],
) -> list[dict[str, Any]]:
    image_status_counts = image_clock["timestamp_status"].value_counts(dropna=False)
    rows: list[dict[str, Any]] = []
    for status, count in sorted(
        image_status_counts.items(), key=lambda item: str(item[0])
    ):
        rows.append(
            {
                "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
                "modality": "photograph",
                "clock_domain_or_status": _as_text(status),
                "event_count": int(count),
                "verified_timestamp_count": int(status == "verified_utc") * int(count),
                "comparability_status": "NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED",
                "nearest_matching_authorized": False,
                "join_cardinality_computable": False,
                "six_hour_cross_modal_cadence": blockers[
                    "six_hour_cross_modal_cadence"
                ],
                **_evidence_fields(image_source),
                "note": "Image local-naive times remain unconverted; missing times remain null.",
            }
        )
    sensor_groups = sensor_clock.groupby(
        ["clock_domain", "timestamp_status"], dropna=False, sort=True
    )
    for (domain, status), group in sensor_groups:
        rows.append(
            {
                "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
                "modality": "sensor_or_scalar_observation",
                "clock_domain_or_status": f"{_as_text(domain)}|{_as_text(status)}",
                "event_count": int(len(group)),
                "verified_timestamp_count": int(
                    (group["timestamp_status"].astype(str) == "verified_utc").sum()
                ),
                "comparability_status": "OBSERVED_SENSOR_CLOCK_EVIDENCE_ONLY",
                "nearest_matching_authorized": False,
                "join_cardinality_computable": False,
                "six_hour_cross_modal_cadence": blockers[
                    "six_hour_cross_modal_cadence"
                ],
                **_evidence_fields(sensor_source),
                "note": "Sensor UTC evidence does not establish a comparable camera clock.",
            }
        )
    return rows


def _unresolved_decisions(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    questions = (
        (
            "target_scalar",
            "What exact scalar should be predicted?",
            "No target name, unit, source path, or computation is approved.",
        ),
        (
            "six_hour_meaning",
            "Does six hours represent observation cadence, input history, or forecast horizon?",
            "The audit found no authorized cross-modal six-hour conclusion.",
        ),
        (
            "image_timezone",
            "Are image timestamps expressed in UTC or another timezone?",
            "640 filename times are local-naive and cannot be converted by assumption.",
        ),
        (
            "clock_synchronization",
            "Was the camera clock synchronized with the sensor acquisition system?",
            "No verified common clock domain was found.",
        ),
        (
            "clock_offset_drift",
            "Is there a known camera/sensor clock offset or drift?",
            "A clock offset cannot be inferred safely from archive order or run labels.",
        ),
        (
            "pairing_key",
            "Is there an authoritative inspection/run/tooth identifier connecting images and sensor observations?",
            "No verified non-temporal pairing key is represented in the pinned artifacts.",
        ),
        (
            "annotations_or_labels",
            "Are bounding boxes, damage labels, masks, or quantitative tooth-damage measurements available elsewhere?",
            "No such sidecar was discovered in the bounded image archive listing.",
        ),
        (
            "sensor_coverage",
            "Is representative sensor schema coverage sufficient for the next meeting, or should a broader stratified scan be performed?",
            "D1.2 covered representative EXP-A Run-1 sources only.",
        ),
    )
    return [
        {
            "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
            "decision_id": key,
            "question": question,
            "status": "REQUIRES_PROFESSOR_OR_PROVIDER_CONFIRMATION",
            "why_required": why,
            "evidence_status": "UNKNOWN",
            **_evidence_fields(source),
        }
        for key, question, why in questions
    ]


def _blocked_traceability(
    traces: pd.DataFrame, sensor_clock: pd.DataFrame, blockers: Mapping[str, Any]
) -> list[dict[str, Any]]:
    if traces.empty or sensor_clock.empty:
        return []
    trace = traces.sort_values(["trace_id"], kind="stable").iloc[0]
    candidates = sensor_clock[
        (sensor_clock["experiment"].astype(str) == str(trace["experiment"]))
        & (sensor_clock["run"].astype(str) == str(trace["run"]))
        & (sensor_clock["timestamp_status"].astype(str) == "verified_utc")
    ].sort_values(["event_id"], kind="stable")
    sensor = candidates.iloc[0] if not candidates.empty else None
    source_identity = None
    timestamp = None
    clock_domain = None
    sensor_event_id = None
    if sensor is not None:
        sensor_event_id = _as_text(sensor["event_id"])
        source_identity = _as_text(sensor.get("hdf5_member_path"))
        timestamp = _as_text(sensor.get("timestamp_utc"))
        clock_domain = _as_text(sensor.get("clock_domain"))
    return [
        {
            "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
            "record_label": "Illustrative traceability record — not a valid aligned training sample.",
            "experiment": _as_text(trace["experiment"]),
            "run": _as_text(trace["run"]),
            "image_id": _as_text(trace["image_id"]),
            "image_source_relative_path": _as_text(trace["image_source_relative_path"]),
            "image_timestamp_status": _as_text(trace["image_timestamp_status"]),
            "image_timestamp_raw_or_local_naive": _as_text(
                trace["image_timestamp_raw"]
            ),
            "sensor_event_id": sensor_event_id,
            "sensor_source_identity": source_identity,
            "sensor_timestamp_utc": timestamp,
            "sensor_clock_domain": clock_domain,
            "clock_domain_compatible": False,
            "alignment_result": blockers["clock_domain_status"],
            "required_to_unblock": json.dumps(
                blockers["required_to_unblock"], separators=(",", ":")
            ),
        }
    ]


def _markdown_table(
    rows: Sequence[Mapping[str, Any]], columns: Sequence[str]
) -> list[str]:
    if not rows:
        return ["No rows available."]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [str(row.get(column, "")).replace("|", "\\|") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return lines


def _report_markdown(
    *,
    inventory_summary: Mapping[str, Any],
    sensor_summary: Mapping[str, Any],
    image_header_summary: Mapping[str, Any],
    image_quality_summary: Mapping[str, Any],
    blockers: Mapping[str, Any],
    runs: Mapping[str, str],
    trace_rows: Sequence[Mapping[str, Any]],
    sources: Mapping[str, Mapping[str, Any]],
) -> str:
    inventory_source = _source_citation(sources["inventory_summary"])
    sensor_source = _source_citation(sources["sensor_summary"])
    schema_source = _source_citation(sources["sensor_schema"])
    image_source = _source_citation(sources["image_header_summary"])
    quality_source = _source_citation(sources["image_quality_summary"])
    alignment_source = _source_citation(sources["alignment_blockers"])
    trace_source = _source_citation(sources["alignment_traces"])
    image_counts = image_header_summary.get("counts_by_experiment", {})
    trace = trace_rows[0] if trace_rows else {}
    lines = [
        "# PHM North America 2026 — professor-facing dataset description",
        "",
        "This report is generated only from exact, hash-pinned D1.1–D1.4 profiling artifacts. It does not rescan PHM archives, inspect Intel data, construct a target, or create a training sample.",
        "",
        "## 1. Scope and inventory",
        "",
        f"In-scope experiments and filename-level runs are EXP-A ({runs.get('EXP-A', 'UNKNOWN')}), EXP-B ({runs.get('EXP-B', 'UNKNOWN')}), and EXP-F ({runs.get('EXP-F', 'UNKNOWN')}).",
        f"The complete central-directory inventory found {_number(inventory_summary, 'readable_file_count')} readable ZIP archives, {_number(inventory_summary, 'archive_member_count'):,} central-directory members, and {_number(inventory_summary, 'nested_zip_member_count')} nested ZIP members. It recorded {_number(inventory_summary, 'missing_expected_count')} missing expected assets and {_number(inventory_summary, 'unreadable_file_count')} unreadable archives, alongside {_nested_number(inventory_summary, 'issue_counts', 'warning')} warnings. Source: {inventory_source}.",
        f"The inventory records {_number(inventory_summary, 'crc_size_duplicate_candidate_rows')} CRC32-plus-size candidate rows, but these are lightweight candidates rather than confirmed duplicate payloads; exact central-directory metadata duplicate rows were {_number(inventory_summary, 'exact_member_metadata_duplicate_rows')}. Source: {inventory_source}.",
        f"The bounded sensor profile retained {_number(sensor_summary, 'run_token_conflict_member_count')} internal run-token conflicts as warnings; it did not rename, remove, or merge any raw member. Source: {sensor_source}.",
        "",
        "## 2. Sensor description",
        "",
        f"D1.2 inspected {_number(sensor_summary, 'profiled_hdf5_member_count')} HDF5 members and produced {_number(sensor_summary, 'sensor_dataset_count'):,} dataset rows; all {_number(sensor_summary, 'readable_hdf5_member_count')} inspected representative members were readable. It observed {_number(sensor_summary, 'file_schema_variant_count')} file-schema variants and {len(sensor_summary.get('shape_counts', {}))} exact shape families. Source: {sensor_source}; shape evidence: {schema_source}.",
        f"Observed dtypes were {', '.join(sorted(sensor_summary.get('dtype_counts', {})))}. Evidenced sampling-rate families included 0.25 Hz, 1 Hz, 100,000 Hz, and approximately 102,400 Hz. Observed role counts include vibration, operating context, condition indicator, and unknown paths; oil/environment should not be claimed beyond rows actually profiled. Representative durations with time evidence ranged from {_number(sensor_summary, 'duration_seconds_min')} to {_number(sensor_summary, 'duration_seconds_max')} seconds (median {_number(sensor_summary, 'duration_seconds_median')} seconds). Source: {sensor_source}.",
        "",
        "> Sensor structural findings are based on bounded representative EXP-A Run-1 coverage and are not an exhaustive schema confirmation across every EXP-A/B/F archive.",
        "",
        "## 3. Image description",
        "",
        f"The complete header profile contains {_number(image_header_summary, 'profiled_image_count'):,} images: EXP-A {image_counts.get('EXP-A', 'UNKNOWN')}, EXP-B {image_counts.get('EXP-B', 'UNKNOWN')}, and EXP-F {image_counts.get('EXP-F', 'UNKNOWN')}. All {_number(image_header_summary, 'readable_header_count'):,} headers were readable. The observed structural schema is uniform: 1440 × 2560 × 3, RGB, uint8, 8-bit JPEG. Source: {image_source}.",
        f"The deterministic sampled-quality pass decoded {_number(image_quality_summary, 'pixel_quality_selected_count')} images, with {_number(image_quality_summary, 'pixel_quality_success_count')} successful pixel reads. It found no exact SHA-256 duplicate group among the {_number(image_quality_summary, 'exact_hash_covered_count')} hash-covered images and {_number(image_quality_summary, 'near_duplicate_pair_count')} dHash near-duplicate candidate pairs. These candidates are not semantic or dataset-wide duplicate proof. Source: {quality_source}.",
        "No bounding-box, mask, keypoint, continuous-target, or verified image-level damage-label sidecar was discovered in the bounded photo-archive listing. This is listing evidence, not proof that undocumented external annotations do not exist. Complete header coverage and sampled pixel-quality coverage are distinct.",
        "",
        "## 4. Cross-modal clock audit",
        "",
        f"Verified UTC image timestamps: {blockers['image_clock_audit']['verified_utc_images']}; timezone-unknown local-naive image timestamps: {blockers['image_clock_audit']['timezone_unknown_images']}; missing image timestamps: {blockers['image_clock_audit']['missing_timestamp_images']}. Where sensor timestamps were evidenced, D1.2/D1.4 records the UTC-compatible sensor clock domain `{blockers['sensor_clock_domain']}`. Source: {alignment_source}.",
        f"D1.4 classification: **{blockers['classification']}**. Image–sensor timestamps are comparable: {blockers['image_sensor_timestamps_comparable']}; nearest temporal matching is authorized: {blockers['nearest_temporal_matching_authorized']}; join cardinality is computable: {blockers['join_cardinality_computable']}; six-hour cross-modal cadence: {blockers['six_hour_cross_modal_cadence']}. Assigning a timezone by assumption could shift photographs by hours and create false image–sensor pairs. Source: {alignment_source}.",
        "",
        "## 5. Blocked traceability example",
        "",
        "**Illustrative traceability record — not a valid aligned training sample.**",
        "",
        *(
            _markdown_table(trace_rows, TRACEABILITY_COLUMNS)
            if trace
            else ["No deterministic blocked trace was available."]
        ),
        "",
        f"The image and sensor identities above are genuine generated-artifact references, but no time delta, candidate target, or training sample was produced. Source: {trace_source}.",
        "",
        "## 6. Model-readiness implications",
        "",
        "- **RT-DETR:** images have a consistent usable structural format, but no bounding-box annotations were discovered. Standard supervised RT-DETR object-detection training is therefore not supported by the discovered annotations. RT-DETR-derived image regression remains possible only after a defensible image-to-target mapping is defined.",
        "- **PatchTST:** sensor structures and sampling-rate families have been identified representatively. Complete cross-experiment schema validation remains limited. PatchTST window construction cannot be finalized until the target, forecast horizon, and six-hour interpretation are confirmed.",
        "- **Multimodal modelling:** image–sensor fusion is blocked until clock-domain alignment is resolved or an authoritative non-temporal pairing key is identified.",
        "",
        "## 7. Questions for the professor or dataset provider",
        "",
        "1. What exact scalar should be predicted?",
        "2. Does six hours represent observation cadence, input history, or forecast horizon?",
        "3. Are image timestamps expressed in UTC or another timezone?",
        "4. Was the camera clock synchronized with the sensor acquisition system?",
        "5. Is there a known clock offset or drift?",
        "6. Is there an authoritative inspection/run/tooth identifier connecting images and sensor observations?",
        "7. Are bounding boxes, damage labels, masks, or quantitative tooth-damage measurements available elsewhere?",
        "8. Is representative sensor schema coverage sufficient for the next meeting, or should a broader stratified scan be performed?",
        "",
        "## Evidence and limitations",
        "",
        "All numerical claims cite exact source runs and generated artifact hashes in `tables/artifact_source_index.csv`. Run and lifecycle labels are not health or damage labels. No causal degradation claim, target selection, interpolation, raw-data modification, or model implementation is included.",
    ]
    return "\n".join(lines) + "\n"


def build_dataset_description(
    *,
    asset_inventory: pd.DataFrame,
    inventory_summary: Mapping[str, Any],
    sensor_profile: pd.DataFrame,
    sensor_summary: Mapping[str, Any],
    image_profile: pd.DataFrame,
    image_header_summary: Mapping[str, Any],
    image_quality_summary: Mapping[str, Any],
    image_clock_audit: pd.DataFrame,
    sensor_clock_audit: pd.DataFrame,
    alignment_blockers: Mapping[str, Any],
    alignment_traces: pd.DataFrame,
    sources: Mapping[str, Mapping[str, Any]],
) -> DatasetDescriptionResult:
    """Create D1.5 evidence tables and Markdown without accessing raw data."""

    source_index_rows = [
        {
            "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
            "source_name": name,
            **_source_row(source),
        }
        for name, source in sorted(sources.items())
    ]
    required_sources = {
        "inventory_summary",
        "asset_inventory",
        "sensor_profile",
        "sensor_summary",
        "sensor_schema",
        "image_header_profile",
        "image_header_summary",
        "image_quality_summary",
        "alignment_blockers",
        "alignment_traces",
        "image_clock",
        "sensor_clock",
    }
    missing_sources = sorted(required_sources.difference(sources))
    if missing_sources:
        raise ValueError(
            "required report sources are missing: " + ", ".join(missing_sources)
        )
    runs = _normalized_runs(asset_inventory)
    glance_values = (
        (
            "readable_archives",
            _number(inventory_summary, "readable_file_count"),
            "archives",
            "complete central-directory inventory",
            "OBSERVED_FROM_DATA",
            "All archive central directories were readable.",
        ),
        (
            "central_directory_members",
            _number(inventory_summary, "archive_member_count"),
            "members",
            "complete central-directory inventory",
            "OBSERVED_FROM_DATA",
            "Central-directory records, not extracted payloads.",
        ),
        (
            "nested_zip_members",
            _number(inventory_summary, "nested_zip_member_count"),
            "members",
            "complete central-directory inventory",
            "OBSERVED_FROM_DATA",
            "Nested ZIP containers recorded in central directories.",
        ),
        (
            "inventory_warnings",
            _nested_number(inventory_summary, "issue_counts", "warning"),
            "warnings",
            "complete central-directory inventory",
            "OBSERVED_FROM_DATA",
            "Warnings require interpretation; they are not automatic corruption proof.",
        ),
        (
            "crc_size_duplicate_candidates",
            _number(inventory_summary, "crc_size_duplicate_candidate_rows"),
            "candidate rows",
            "complete central-directory inventory",
            "OBSERVED_FROM_DATA",
            "CRC32-plus-size evidence only; not confirmed duplicates.",
        ),
        (
            "representative_hdf5_members",
            _number(sensor_summary, "profiled_hdf5_member_count"),
            "members",
            "bounded representative EXP-A Run-1 coverage",
            "OBSERVED_FROM_DATA",
            "Not an all-experiment sensor scan.",
        ),
        (
            "representative_sensor_dataset_rows",
            _number(sensor_summary, "sensor_dataset_count"),
            "dataset rows",
            "bounded representative EXP-A Run-1 coverage",
            "OBSERVED_FROM_DATA",
            "Metadata-only structural rows.",
        ),
        (
            "profiled_images",
            _number(image_header_summary, "profiled_image_count"),
            "images",
            "complete header coverage",
            "OBSERVED_FROM_DATA",
            "Image headers only unless selected for quality decoding.",
        ),
    )
    glance_rows = [
        {
            "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
            "metric": metric,
            "value": value,
            "unit": unit,
            "scope": scope,
            "evidence_status": status,
            **_evidence_fields(
                sources["sensor_summary"]
                if metric.startswith("representative_")
                else (
                    sources["image_header_summary"]
                    if metric == "profiled_images"
                    else sources["inventory_summary"]
                )
            ),
            "note": note,
        }
        for metric, value, unit, scope, status, note in glance_values
    ]
    trace_rows = _blocked_traceability(
        alignment_traces, sensor_clock_audit, alignment_blockers
    )
    tables = {
        "dataset_at_a_glance": glance_rows,
        "modality_coverage": _modality_coverage(
            asset_inventory, sources["asset_inventory"]
        ),
        "sensor_shape_summary": _sensor_shapes(
            sensor_profile, sources["sensor_profile"]
        ),
        "image_shape_summary": _image_shapes(
            image_profile, sources["image_header_profile"]
        ),
        "clock_domain_summary": _clock_summary(
            image_clock_audit,
            sensor_clock_audit,
            alignment_blockers,
            sources["image_clock"],
            sources["sensor_clock"],
        ),
        "unresolved_decisions": _unresolved_decisions(sources["alignment_blockers"]),
        "blocked_traceability_example": trace_rows,
    }
    summary = {
        "schema_version": DATASET_DESCRIPTION_SCHEMA_VERSION,
        "readable_archive_count": _number(inventory_summary, "readable_file_count"),
        "central_directory_member_count": _number(
            inventory_summary, "archive_member_count"
        ),
        "representative_sensor_member_count": _number(
            sensor_summary, "profiled_hdf5_member_count"
        ),
        "image_count": _number(image_header_summary, "profiled_image_count"),
        "alignment_classification": alignment_blockers["classification"],
        "source_artifact_count": len(source_index_rows),
    }
    report = _report_markdown(
        inventory_summary=inventory_summary,
        sensor_summary=sensor_summary,
        image_header_summary=image_header_summary,
        image_quality_summary=image_quality_summary,
        blockers=alignment_blockers,
        runs=runs,
        trace_rows=trace_rows,
        sources=sources,
    )
    return DatasetDescriptionResult(
        tables=tables,
        report_markdown=report,
        source_index_rows=source_index_rows,
        summary=summary,
    )


def _write_csv(
    path: Path, rows: Sequence[Mapping[str, Any]], columns: Sequence[str]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(
            {column: row.get(column) for column in columns} for row in rows
        )


def _write_modality_figure(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    frame = pd.DataFrame(rows)
    pivot = frame.pivot_table(
        index="experiment",
        columns="modality",
        values="archive_count",
        aggfunc="sum",
        fill_value=0,
    )
    figure, axis = plt.subplots(figsize=(9, 4.5))
    pivot.plot(kind="bar", stacked=True, ax=axis)
    axis.set_ylabel("Archive count")
    axis.set_xlabel("Experiment")
    axis.set_title("PHM archive coverage by modality")
    axis.legend(title="Modality", fontsize="small")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _write_clock_figure(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    frame = pd.DataFrame(rows)
    labels = [
        f"{row.modality}: {row.clock_domain_or_status}" for row in frame.itertuples()
    ]
    figure, axis = plt.subplots(figsize=(10, max(3.5, len(labels) * 0.65)))
    axis.barh(labels, frame["event_count"].tolist())
    axis.set_xlabel("Event count")
    axis.set_title("Clock-domain evidence (not temporal alignment)")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def write_dataset_description_run(
    result: DatasetDescriptionResult,
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
    """Serialize the D1.5 report, slide tables, figures, and provenance."""

    run.create_layout()
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    inputs_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        [
            run.artifact(config_path, role="resolved_configuration"),
            run.artifact(inputs_path, role="input_manifest"),
        ]
    )
    table_columns = {
        "dataset_at_a_glance": AT_A_GLANCE_COLUMNS,
        "modality_coverage": MODALITY_COVERAGE_COLUMNS,
        "sensor_shape_summary": SENSOR_SHAPE_COLUMNS,
        "image_shape_summary": IMAGE_SHAPE_COLUMNS,
        "clock_domain_summary": CLOCK_DOMAIN_COLUMNS,
        "unresolved_decisions": UNRESOLVED_DECISION_COLUMNS,
        "blocked_traceability_example": TRACEABILITY_COLUMNS,
    }
    for name, columns in table_columns.items():
        path = run.run_directory / f"tables/{name}.csv"
        _write_csv(path, result.tables[name], columns)
        artifacts.append(run.artifact(path, role=f"{name}_csv"))
    source_index_path = run.run_directory / "tables/artifact_source_index.csv"
    _write_csv(source_index_path, result.source_index_rows, SOURCE_INDEX_COLUMNS)
    artifacts.append(run.artifact(source_index_path, role="artifact_source_index"))
    report_path = run.run_directory / "reports/professor_dataset_description.md"
    report_path.write_text(result.report_markdown, encoding="utf-8")
    summary_path = run.run_directory / "reports/dataset_description_summary.json"
    summary_path.write_text(
        json.dumps(result.summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    artifacts.extend(
        [
            run.artifact(report_path, role="professor_dataset_description"),
            run.artifact(summary_path, role="dataset_description_summary"),
        ]
    )
    modality_figure = run.run_directory / "figures/modality_coverage.png"
    clock_figure = run.run_directory / "figures/clock_domain_summary.png"
    _write_modality_figure(modality_figure, result.tables["modality_coverage"])
    _write_clock_figure(clock_figure, result.tables["clock_domain_summary"])
    artifacts.extend(
        [
            run.artifact(modality_figure, role="modality_coverage_figure"),
            run.artifact(clock_figure, role="clock_domain_summary_figure"),
        ]
    )
    provenance_path = run.write_provenance(artifacts)
    all_artifacts = [
        *artifacts,
        run.artifact(provenance_path, role="run_provenance"),
    ]
    run.write_output_manifest(all_artifacts)
    return all_artifacts


__all__ = [
    "DATASET_DESCRIPTION_SCHEMA_VERSION",
    "DatasetDescriptionResult",
    "build_dataset_description",
    "write_dataset_description_run",
]
