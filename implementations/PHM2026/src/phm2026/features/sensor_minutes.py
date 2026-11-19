"""Bounded minute-level features from PHM nested low-frequency archives.

The generic extractor receives all PHM path knowledge as ``ChannelSpec``
instances.  It materializes one inner ZIP and one HDF5 payload at a time,
retains source identity, and never persists source arrays.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

import h5py
import numpy as np
import pandas as pd

from ..data_contracts.identifiers import deterministic_id
from ..profiling.archive_io import (
    ArchiveMemberRef,
    iter_materialized_nested_members,
)

SENSOR_FEATURE_SCHEMA_VERSION = "1.0.0"
CHANNEL_STATISTICS = ("mean", "std", "median", "min", "max", "last", "slope_per_sample")


@dataclass(frozen=True, slots=True)
class ChannelSpec:
    """One configured HDF5 path and its analysis-safe feature prefix."""

    name: str
    hdf5_path: str
    role: str
    expected_unit: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.replace("_", "").isalnum():
            raise ValueError("channel name must be a non-empty identifier")
        if not self.hdf5_path.startswith("/"):
            raise ValueError("hdf5_path must be absolute within the HDF5 file")


@dataclass(frozen=True, slots=True)
class ExtractionOptions:
    max_member_bytes: int = 16 * 1024 * 1024
    max_values_per_channel: int = 100_000
    timestamp_attribute: str = "wf_start_time"
    unit_attributes: tuple[str, ...] = (
        "unit_string",
        "NI_UnitDescription",
        "unit",
        "units",
    )

    def __post_init__(self) -> None:
        if self.max_member_bytes <= 0 or self.max_values_per_channel <= 0:
            raise ValueError("extraction bounds must be positive")


def feature_columns(channels: Sequence[ChannelSpec]) -> list[str]:
    """Return deterministic model feature columns, including channel masks."""

    values = [
        f"{channel.name}_{statistic}"
        for channel in channels
        for statistic in CHANNEL_STATISTICS
    ]
    return values + [f"{channel.name}_missing" for channel in channels]


def _scalar_text(value: object) -> str | None:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or None
    if isinstance(value, np.ndarray) and value.size == 1:
        return _scalar_text(value.reshape(-1)[0])
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_utc_timestamp(value: object) -> tuple[str | None, str]:
    raw = _scalar_text(value)
    if raw is None:
        return None, "missing"
    try:
        parsed = pd.Timestamp(raw)
    except (TypeError, ValueError):
        return None, "unparseable"
    if parsed.tzinfo is None:
        return None, "timezone_unknown"
    return parsed.tz_convert("UTC").isoformat(), "verified_utc"


def _unit(dataset: h5py.Dataset, aliases: Sequence[str]) -> tuple[str | None, str]:
    for alias in aliases:
        if alias in dataset.attrs:
            value = _scalar_text(dataset.attrs[alias])
            if value:
                return value, f"dataset_attribute:{alias}"
    return None, "not_observed"


def _bounded_values(
    dataset: h5py.Dataset, *, max_values: int
) -> tuple[np.ndarray, str]:
    if dataset.dtype.kind not in "biufc":
        raise TypeError(f"nonnumeric dtype {dataset.dtype}")
    count = int(np.prod(dataset.shape, dtype=np.int64)) if dataset.shape else 1
    if count == 0:
        return np.empty(0, dtype=np.float64), "complete_empty"
    values = np.asarray(dataset[()]).reshape(-1)
    if count > max_values:
        indexes = np.linspace(0, count - 1, max_values, dtype=np.int64)
        values = values[indexes]
        scope = "deterministic_even_sample"
    else:
        scope = "complete_low_frequency_array"
    return values.astype(np.float64, copy=False), scope


def _statistics(values: np.ndarray) -> dict[str, float | None]:
    finite = values[np.isfinite(values)]
    if not len(finite):
        return {name: None for name in CHANNEL_STATISTICS}
    if len(finite) == 1:
        slope = 0.0
    else:
        x = np.arange(len(finite), dtype=np.float64)
        centered_x = x - x.mean()
        denominator = float(np.dot(centered_x, centered_x))
        slope = float(np.dot(centered_x, finite - finite.mean()) / denominator)
    return {
        "mean": float(finite.mean()),
        "std": float(finite.std(ddof=0)),
        "median": float(np.median(finite)),
        "min": float(finite.min()),
        "max": float(finite.max()),
        "last": float(finite[-1]),
        "slope_per_sample": slope,
    }


def _first_timestamp(
    handle: h5py.File,
    selected: Sequence[h5py.Dataset],
    attribute: str,
) -> tuple[str | None, str, str | None]:
    for dataset in selected:
        if attribute in dataset.attrs:
            value, status = _parse_utc_timestamp(dataset.attrs[attribute])
            return value, status, dataset.name
    found: list[tuple[str | None, str, str]] = []

    def visitor(_name: str, item: h5py.Dataset | h5py.Group) -> None:
        if found or not isinstance(item, h5py.Dataset):
            return
        if attribute in item.attrs:
            value, status = _parse_utc_timestamp(item.attrs[attribute])
            found.append((value, status, item.name))

    handle.visititems(visitor)
    return found[0] if found else (None, "missing", None)


def _profile_hdf5(
    path: Path,
    *,
    channels: Sequence[ChannelSpec],
    options: ExtractionOptions,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    row: dict[str, Any] = {}
    evidence: list[dict[str, Any]] = []
    with h5py.File(path, "r") as handle:
        selected: list[h5py.Dataset] = []
        for channel in channels:
            dataset = handle.get(channel.hdf5_path)
            if not isinstance(dataset, h5py.Dataset):
                for statistic in CHANNEL_STATISTICS:
                    row[f"{channel.name}_{statistic}"] = None
                row[f"{channel.name}_missing"] = True
                evidence.append(
                    {
                        "channel": channel.name,
                        "hdf5_path": channel.hdf5_path,
                        "available": False,
                        "unit": None,
                        "unit_evidence": "dataset_missing",
                        "statistics_scope": "not_computed",
                        "sampled_value_count": 0,
                    }
                )
                continue
            selected.append(dataset)
            unit, unit_evidence = _unit(dataset, options.unit_attributes)
            try:
                values, scope = _bounded_values(
                    dataset, max_values=options.max_values_per_channel
                )
                statistics = _statistics(values)
                for statistic, value in statistics.items():
                    row[f"{channel.name}_{statistic}"] = value
                row[f"{channel.name}_missing"] = not any(
                    value is not None for value in statistics.values()
                )
                error = None
            except (OSError, RuntimeError, TypeError, ValueError) as exc:
                for statistic in CHANNEL_STATISTICS:
                    row[f"{channel.name}_{statistic}"] = None
                row[f"{channel.name}_missing"] = True
                values = np.empty(0)
                scope = "error"
                error = f"{type(exc).__name__}: {exc}"
            evidence.append(
                {
                    "channel": channel.name,
                    "hdf5_path": channel.hdf5_path,
                    "available": error is None,
                    "unit": unit,
                    "unit_evidence": unit_evidence,
                    "statistics_scope": scope,
                    "sampled_value_count": int(len(values)),
                    "error": error,
                }
            )
        timestamp, status, source_path = _first_timestamp(
            handle, selected, options.timestamp_attribute
        )
    row.update(
        {
            "start_timestamp_utc": timestamp,
            "timestamp_status": status,
            "timestamp_source_kind": (
                f"hdf5_dataset_attribute:{options.timestamp_attribute}"
                if source_path
                else None
            ),
            "timestamp_source_path": source_path,
        }
    )
    return row, evidence


def _container_reference(row: pd.Series, data_root: Path) -> ArchiveMemberRef:
    return ArchiveMemberRef(
        archive_path=data_root / str(row.archive_relative_path),
        archive_relative_path=str(row.archive_relative_path),
        member_path=str(row.archive_member),
        expected_compressed_size_bytes=int(row.compressed_size_bytes),
        expected_uncompressed_size_bytes=int(row.uncompressed_size_bytes),
        expected_crc32=str(row.checksum),
    )


def extract_minute_features(
    containers: pd.DataFrame,
    targets: pd.DataFrame,
    *,
    data_root: Path,
    channels: Sequence[ChannelSpec],
    split_by_experiment: Mapping[str, str],
    options: ExtractionOptions = ExtractionOptions(),
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Extract one compact row per nested HDF5 file and order by verified time."""

    required = {
        "archive_relative_path",
        "archive_member",
        "experiment",
        "run",
        "modality",
    }
    missing = sorted(required - set(containers.columns))
    if missing:
        raise ValueError(f"container table is missing columns: {missing}")
    selected = containers[
        containers.modality.eq("low_frequency") & containers.member_file_type.eq("zip")
    ].copy()
    target_index = targets.set_index(["experiment", "run"])
    rows: list[dict[str, Any]] = []
    channel_rows: list[dict[str, Any]] = []
    for _, container in selected.sort_values(["experiment", "run"]).iterrows():
        experiment = str(container.experiment)
        run_number = int(container.run)
        if (experiment, run_number) not in target_index.index:
            raise ValueError(f"missing target for {experiment} run {run_number}")
        reference = _container_reference(container, data_root)
        for payload in iter_materialized_nested_members(
            reference,
            suffixes={".h5", ".hdf5"},
            max_member_bytes=options.max_member_bytes,
        ):
            identity = {
                "archive_relative_path": reference.archive_relative_path,
                "outer_archive_member": reference.member_path,
                "hdf5_member_path": payload.reference.nested_member_path,
                "hdf5_member_occurrence": payload.reference.nested_member_occurrence,
                "crc32": payload.reference.expected_crc32,
            }
            minute_id = deterministic_id("sensor_minute", identity)
            base: dict[str, Any] = {
                "schema_version": SENSOR_FEATURE_SCHEMA_VERSION,
                "minute_id": minute_id,
                "experiment": experiment,
                "run": run_number,
                "split": split_by_experiment.get(experiment),
                **identity,
                "source_hash_algorithm": "zip_crc32",
                "source_hash": payload.reference.expected_crc32,
                "uncompressed_size_bytes": payload.reference.expected_uncompressed_size_bytes,
                "extraction_status": "error" if payload.error else "ok",
                "extraction_error": payload.error,
            }
            if payload.path is None:
                profile = {
                    column: None
                    for column in feature_columns(channels)
                    if not column.endswith("_missing")
                }
                profile.update(
                    {
                        column: True
                        for column in feature_columns(channels)
                        if column.endswith("_missing")
                    }
                )
                profile.update(
                    {
                        "start_timestamp_utc": None,
                        "timestamp_status": "source_error",
                        "timestamp_source_kind": None,
                        "timestamp_source_path": None,
                    }
                )
                evidence = []
            else:
                try:
                    profile, evidence = _profile_hdf5(
                        payload.path, channels=channels, options=options
                    )
                except (OSError, RuntimeError, ValueError) as exc:
                    base["extraction_status"] = "error"
                    base["extraction_error"] = f"{type(exc).__name__}: {exc}"
                    profile = {
                        column: None
                        for column in feature_columns(channels)
                        if not column.endswith("_missing")
                    }
                    profile.update(
                        {
                            column: True
                            for column in feature_columns(channels)
                            if column.endswith("_missing")
                        }
                    )
                    profile.update(
                        {
                            "start_timestamp_utc": None,
                            "timestamp_status": "hdf5_error",
                            "timestamp_source_kind": None,
                            "timestamp_source_path": None,
                        }
                    )
                    evidence = []
            rows.append({**base, **profile})
            for item in evidence:
                channel_rows.append(
                    {
                        "schema_version": SENSOR_FEATURE_SCHEMA_VERSION,
                        "minute_id": minute_id,
                        "experiment": experiment,
                        "run": run_number,
                        **item,
                    }
                )
    minute = pd.DataFrame(rows)
    if minute.empty:
        raise ValueError("no low-frequency HDF5 members were extracted")
    minute["timestamp_parsed"] = pd.to_datetime(
        minute.start_timestamp_utc, utc=True, errors="coerce"
    )
    minute["sequence_inclusion_status"] = np.where(
        minute.extraction_status.eq("ok") & minute.timestamp_parsed.notna(),
        "included",
        "excluded",
    )
    minute["sequence_exclusion_reason"] = np.where(
        minute.extraction_status.ne("ok"),
        "source_or_hdf5_error",
        np.where(minute.timestamp_parsed.isna(), "verified_timestamp_missing", None),
    )
    minute["sequence_position"] = pd.Series(pd.NA, index=minute.index, dtype="Int64")
    included = minute[minute.sequence_inclusion_status.eq("included")].sort_values(
        ["experiment", "run", "timestamp_parsed", "minute_id"], kind="stable"
    )
    positions = included.groupby(["experiment", "run"]).cumcount() + 1
    minute.loc[included.index, "sequence_position"] = positions.astype("Int64")
    for target_column in (
        "target_definition_version",
        "target_verification_status",
        "raw_top3_mean_pct",
        "causal_monotonic_top3_mean_pct",
    ):
        mapping = target_index[target_column].to_dict()
        minute[target_column] = [
            mapping[(experiment, int(run))]
            for experiment, run in zip(minute.experiment, minute.run)
        ]
    minute = minute.drop(columns="timestamp_parsed").sort_values(
        ["experiment", "run", "sequence_position", "minute_id"],
        na_position="last",
        kind="stable",
    )
    run_summary = summarize_feature_run(minute, channels=channels)
    channel_evidence = pd.DataFrame(channel_rows).sort_values(
        ["experiment", "run", "minute_id", "channel"], kind="stable"
    )
    return (
        minute.reset_index(drop=True),
        run_summary,
        channel_evidence.reset_index(drop=True),
    )


def summarize_feature_run(
    minute: pd.DataFrame, *, channels: Sequence[ChannelSpec]
) -> pd.DataFrame:
    """Create one traceable sequence-summary row per experiment/run."""

    rows: list[dict[str, Any]] = []
    for (experiment, run_number), scoped in minute.groupby(["experiment", "run"]):
        included = scoped[scoped.sequence_inclusion_status.eq("included")].sort_values(
            "sequence_position"
        )
        timestamps = pd.to_datetime(included.start_timestamp_utc, utc=True)
        deltas = timestamps.diff().dt.total_seconds().dropna()
        row: dict[str, Any] = {
            "schema_version": SENSOR_FEATURE_SCHEMA_VERSION,
            "sequence_id": deterministic_id(
                "sensor_sequence",
                {
                    "experiment": experiment,
                    "run": int(run_number),
                    "schema_version": SENSOR_FEATURE_SCHEMA_VERSION,
                },
            ),
            "experiment": experiment,
            "run": int(run_number),
            "split": str(scoped.split.iloc[0]),
            "source_member_count": int(len(scoped)),
            "included_minute_count": int(len(included)),
            "excluded_minute_count": int(len(scoped) - len(included)),
            "first_timestamp_utc": (
                timestamps.min().isoformat() if len(timestamps) else None
            ),
            "last_timestamp_utc": (
                timestamps.max().isoformat() if len(timestamps) else None
            ),
            "timestamp_span_seconds": (
                float((timestamps.max() - timestamps.min()).total_seconds())
                if len(timestamps) > 1
                else None
            ),
            "median_cadence_seconds": float(deltas.median()) if len(deltas) else None,
            "max_gap_seconds": float(deltas.max()) if len(deltas) else None,
            "duplicate_timestamp_count": int(timestamps.duplicated().sum()),
            "raw_top3_mean_pct": float(scoped.raw_top3_mean_pct.iloc[0]),
            "causal_monotonic_top3_mean_pct": float(
                scoped.causal_monotonic_top3_mean_pct.iloc[0]
            ),
            "target_definition_version": scoped.target_definition_version.iloc[0],
            "target_verification_status": scoped.target_verification_status.iloc[0],
            "sequence_member_ids_json": json.dumps(
                included.minute_id.tolist(), separators=(",", ":")
            ),
        }
        for channel in channels:
            row[f"{channel.name}_available_minutes"] = int(
                (~included[f"{channel.name}_missing"].astype(bool)).sum()
            )
            row[f"{channel.name}_missing_fraction"] = (
                float(included[f"{channel.name}_missing"].astype(float).mean())
                if len(included)
                else None
            )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["experiment", "run"]).reset_index(drop=True)
