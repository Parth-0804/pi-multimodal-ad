"""Dataset-neutral, bounded structural profiling of HDF5 sensor members."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from itertools import product
import csv
import json
import math
from pathlib import Path
import time
from typing import Any, Literal

import h5py
import numpy as np
import pandas as pd

from ..data_contracts import SensorRecord, deterministic_id
from ..datasets import BaseDatasetAdapter
from ..utils.provenance import ArtifactRecord, RunContext
from .archive_io import (
    ArchiveMaterializationError,
    ArchiveMemberRef,
    MaterializedArchiveMember,
    iter_materialized_nested_members,
    materialize_archive_member,
)

SENSOR_PROFILE_SCHEMA_VERSION = "1.0.0"
SensorMode = Literal["metadata", "sampled", "full"]
_HDF_SUFFIXES = {".h5", ".hdf5"}


@dataclass(frozen=True, slots=True)
class SensorProfileIssue:
    severity: Literal["info", "warning", "error"]
    code: str
    source: str | None
    message: str


@dataclass(frozen=True, slots=True)
class SensorProfileOptions:
    mode: SensorMode = "metadata"
    seed: int = 0
    sample_points: int = 4096
    max_block_bytes: int = 16 * 1024 * 1024
    max_member_bytes: int | None = None
    temp_root: Path | None = None
    expected_paths: Mapping[str, Any] | None = None
    full_scan_authorized: bool = False

    def __post_init__(self) -> None:
        if self.mode not in {"metadata", "sampled", "full"}:
            raise ValueError("mode must be metadata, sampled, or full")
        for field_name, value in (
            ("sample_points", self.sample_points),
            ("max_block_bytes", self.max_block_bytes),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{field_name} must be a positive integer")
        if self.max_member_bytes is not None and (
            isinstance(self.max_member_bytes, bool)
            or not isinstance(self.max_member_bytes, int)
            or self.max_member_bytes <= 0
        ):
            raise ValueError("max_member_bytes must be positive or null")
        if self.temp_root is not None:
            object.__setattr__(self, "temp_root", Path(self.temp_root))


@dataclass(frozen=True, slots=True)
class SensorSource:
    inventory_member_id: str
    archive_asset_id: str
    archive_relative_path: str
    archive_path: Path
    outer_member_path: str
    modality: str
    experiment: str
    authoritative_outer_run: int | None
    nested_archive_run_token: int | None
    inventory_internal_run_token: int | None
    inventory_internal_run_matches_outer: bool | None
    inventory_internal_run_parse_error: str | None
    member_occurrence: int
    compressed_size_bytes: int
    uncompressed_size_bytes: int
    crc32: str
    is_nested_container: bool

    @property
    def source_key(self) -> str:
        return f"{self.archive_relative_path}!{self.outer_member_path}"


@dataclass(slots=True)
class SensorProfileResult:
    sensors: list[dict[str, Any]]
    hdf5_members: list[dict[str, Any]]
    issues: list[SensorProfileIssue]
    mode: SensorMode
    discovered_source_count: int
    selected_source_count: int
    limited: bool
    elapsed_seconds: float

    def summary(self) -> dict[str, Any]:
        roles = Counter(str(row["channel_role"]) for row in self.sensors)
        shapes = Counter(str(row["shape_json"]) for row in self.sensors)
        dtypes = Counter(str(row["dtype"]) for row in self.sensors)
        statistics = Counter(str(row["statistics_scope"]) for row in self.sensors)
        issues = Counter(issue.severity for issue in self.issues)
        readable_members = sum(row["status"] == "ok" for row in self.hdf5_members)
        channels_by_run: dict[str, Counter[str]] = defaultdict(Counter)
        sampling_rates: Counter[str] = Counter()
        sampling_evidence: Counter[str] = Counter()
        unknown_paths: Counter[str] = Counter()
        path_shapes: dict[str, set[str]] = defaultdict(set)
        path_dtypes: dict[str, set[str]] = defaultdict(set)
        path_rates: dict[str, set[str]] = defaultdict(set)
        durations: list[float] = []
        for row in self.sensors:
            run_label = (
                f"run-{int(row['run'])}" if row["run"] is not None else "run-unresolved"
            )
            key = f"{row['experiment']}/{run_label}"
            channels_by_run[key][str(row["channel_role"])] += 1
            path = str(row["hdf5_path"])
            path_shapes[path].add(str(row["shape_json"]))
            path_dtypes[path].add(str(row["dtype"]))
            if row["sampling_rate_hz"] is not None:
                rate = str(row["sampling_rate_hz"])
                sampling_rates[rate] += 1
                path_rates[path].add(rate)
            if row["sampling_rate_evidence"] is not None:
                sampling_evidence[str(row["sampling_rate_evidence"])] += 1
            if row["duration_seconds"] is not None:
                durations.append(float(row["duration_seconds"]))
            if row["channel_role"] == "unknown":
                unknown_paths[path] += 1
        missing_expected: Counter[str] = Counter()
        unreadable_sources: list[str] = []
        conflict_sources: list[str] = []
        for row in self.hdf5_members:
            if row["status"] != "ok":
                unreadable_sources.append(str(row["hdf5_member_path"]))
            if row["internal_run_matches_authoritative"] is False:
                conflict_sources.append(str(row["hdf5_member_path"]))
            try:
                missing = json.loads(str(row["missing_expected_paths_json"]))
            except (TypeError, json.JSONDecodeError):
                missing = []
            for value in missing:
                missing_expected[str(value)] += 1
        variable_paths = {
            path: {
                "shapes": sorted(path_shapes[path]),
                "dtypes": sorted(path_dtypes[path]),
                "sampling_rates_hz": sorted(path_rates[path]),
            }
            for path in sorted(path_shapes)
            if len(path_shapes[path]) > 1
            or len(path_dtypes[path]) > 1
            or len(path_rates[path]) > 1
        }
        file_schema_ids = {
            str(row["file_schema_id"])
            for row in self.hdf5_members
            if row["file_schema_id"] is not None
        }
        return {
            "schema_version": SENSOR_PROFILE_SCHEMA_VERSION,
            "mode": self.mode,
            "discovered_source_count": self.discovered_source_count,
            "selected_source_count": self.selected_source_count,
            "profiled_hdf5_member_count": len(self.hdf5_members),
            "readable_hdf5_member_count": readable_members,
            "unreadable_hdf5_member_count": len(self.hdf5_members) - readable_members,
            "unreadable_member_paths": sorted(unreadable_sources),
            "sensor_dataset_count": len(self.sensors),
            "unknown_path_count": roles["unknown"],
            "unknown_path_counts": dict(sorted(unknown_paths.items())),
            "empty_dataset_count": sum(
                bool(row["empty_array"]) for row in self.sensors
            ),
            "statistics_scope_counts": dict(sorted(statistics.items())),
            "channel_role_counts": dict(sorted(roles.items())),
            "channels_by_experiment_run": {
                key: dict(sorted(values.items()))
                for key, values in sorted(channels_by_run.items())
            },
            "shape_counts": dict(sorted(shapes.items())),
            "dtype_counts": dict(sorted(dtypes.items())),
            "sampling_rate_counts_hz": dict(sorted(sampling_rates.items())),
            "sampling_rate_evidence_counts": dict(sorted(sampling_evidence.items())),
            "sampling_rate_observed_count": sum(sampling_rates.values()),
            "duration_observed_count": len(durations),
            "duration_seconds_min": min(durations) if durations else None,
            "duration_seconds_median": (
                float(np.median(np.asarray(durations))) if durations else None
            ),
            "duration_seconds_max": max(durations) if durations else None,
            "timestamped_dataset_count": sum(
                row["start_timestamp_utc"] is not None for row in self.sensors
            ),
            "file_schema_variant_count": len(file_schema_ids),
            "variable_path_schemas": variable_paths,
            "missing_expected_path_counts": dict(sorted(missing_expected.items())),
            "run_token_conflict_member_count": len(conflict_sources),
            "run_token_conflict_member_paths": sorted(conflict_sources),
            "issue_counts": {
                "info": issues["info"],
                "warning": issues["warning"],
                "error": issues["error"],
            },
            "limited": self.limited,
            "elapsed_seconds": self.elapsed_seconds,
            "materialized_bytes": sum(
                int(row["materialized_bytes"] or 0) for row in self.hdf5_members
            ),
        }


def _nullable_int(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(value)


def _nullable_bool(value: object) -> bool | None:
    if value is None or pd.isna(value):
        return None
    return bool(value)


def load_sensor_sources(
    inventory_members: Path,
    *,
    data_root: Path,
    asset_inventory: Path | None = None,
    modalities: Sequence[str] | None = None,
) -> list[SensorSource]:
    """Load direct HDF5 members and nested ZIP containers from D1.1 output."""

    table = pd.read_parquet(inventory_members)
    required = {
        "member_id",
        "archive_asset_id",
        "archive_relative_path",
        "archive_member",
        "member_file_type",
        "modality",
        "experiment",
        "run",
        "member_run_token",
        "member_run_matches_archive",
        "member_run_parse_error",
        "compressed_size_bytes",
        "uncompressed_size_bytes",
        "checksum",
        "is_nested_archive",
    }
    missing = sorted(required - set(table.columns))
    if missing:
        raise ValueError(
            "inventory member table is missing columns: " + ", ".join(missing)
        )
    asset_path = asset_inventory or inventory_members.with_name(
        "asset_inventory.parquet"
    )
    assets = pd.read_parquet(asset_path)
    asset_required = {"asset_id", "experiment", "run", "modality"}
    asset_missing = sorted(asset_required - set(assets.columns))
    if asset_missing:
        raise ValueError(
            "asset inventory table is missing columns: " + ", ".join(asset_missing)
        )
    outer_run_by_asset = {
        str(row["asset_id"]): _nullable_int(row["run"])
        for row in assets.to_dict("records")
    }
    allowed_modalities = set(
        modalities or ("high_frequency", "low_frequency", "condition_indicator")
    )
    rows = table[
        table["modality"].isin(allowed_modalities)
        & (
            table["member_file_type"].isin(["h5", "hdf5"])
            | table["is_nested_archive"].astype(bool)
        )
    ]
    sources: list[SensorSource] = []
    occurrences: Counter[tuple[str, str]] = Counter()
    root = data_root.resolve()
    for row in rows.sort_values(
        ["modality", "experiment", "run", "archive_relative_path", "archive_member"],
        na_position="first",
        kind="mergesort",
    ).to_dict("records"):
        occurrence_key = (str(row["archive_asset_id"]), str(row["archive_member"]))
        occurrences[occurrence_key] += 1
        is_nested = bool(row["is_nested_archive"])
        archive_path = (root / str(row["archive_relative_path"])).resolve()
        try:
            archive_path.relative_to(root)
        except ValueError as exc:
            raise ValueError("inventory archive path escapes the data root") from exc
        sources.append(
            SensorSource(
                inventory_member_id=str(row["member_id"]),
                archive_asset_id=str(row["archive_asset_id"]),
                archive_relative_path=str(row["archive_relative_path"]),
                archive_path=archive_path,
                outer_member_path=str(row["archive_member"]),
                modality=str(row["modality"]),
                experiment=str(row["experiment"]),
                authoritative_outer_run=outer_run_by_asset.get(
                    str(row["archive_asset_id"])
                ),
                nested_archive_run_token=(
                    _nullable_int(row["member_run_token"]) if is_nested else None
                ),
                inventory_internal_run_token=(
                    None if is_nested else _nullable_int(row["member_run_token"])
                ),
                inventory_internal_run_matches_outer=_nullable_bool(
                    row["member_run_matches_archive"]
                ),
                inventory_internal_run_parse_error=(
                    None
                    if row["member_run_parse_error"] is None
                    or pd.isna(row["member_run_parse_error"])
                    else str(row["member_run_parse_error"])
                ),
                member_occurrence=occurrences[occurrence_key],
                compressed_size_bytes=int(row["compressed_size_bytes"]),
                uncompressed_size_bytes=int(row["uncompressed_size_bytes"]),
                crc32=str(row["checksum"]),
                is_nested_container=is_nested,
            )
        )
    return sources


def select_sensor_sources(
    sources: Sequence[SensorSource],
    *,
    limit: int | None = None,
    limit_per_modality: int | None = None,
) -> list[SensorSource]:
    if limit is not None and (
        isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0
    ):
        raise ValueError("limit must be a positive integer or null")
    if limit_per_modality is not None and (
        isinstance(limit_per_modality, bool)
        or not isinstance(limit_per_modality, int)
        or limit_per_modality <= 0
    ):
        raise ValueError("limit_per_modality must be a positive integer or null")
    selected: list[SensorSource] = []
    counts: Counter[str] = Counter()
    for source in sources:
        if (
            limit_per_modality is not None
            and counts[source.modality] >= limit_per_modality
        ):
            continue
        selected.append(source)
        counts[source.modality] += 1
        if limit is not None and len(selected) >= limit:
            break
    return selected


def _jsonable(value: object, *, max_items: int = 64) -> object:
    if isinstance(value, np.generic):
        return _jsonable(value.item(), max_items=max_items)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.ndarray):
        flat = value.reshape(-1)
        values = [_jsonable(item, max_items=max_items) for item in flat[:max_items]]
        if flat.size > max_items:
            return {"values": values, "truncated": True, "total_items": int(flat.size)}
        return values
    if isinstance(value, (list, tuple)):
        values = [_jsonable(item, max_items=max_items) for item in value[:max_items]]
        if len(value) > max_items:
            return {"values": values, "truncated": True, "total_items": len(value)}
        return values
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not math.isfinite(value):
            return str(value)
        return value
    return repr(value)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _attribute_mapping(dataset: h5py.Dataset) -> dict[str, object]:
    return {str(key): _jsonable(dataset.attrs[key]) for key in sorted(dataset.attrs)}


def _attribute(
    dataset: h5py.Dataset, aliases: Sequence[str]
) -> tuple[str | None, object | None]:
    keys = {str(key).lower(): str(key) for key in dataset.attrs}
    for alias in aliases:
        actual = keys.get(alias.lower())
        if actual is not None:
            return actual, dataset.attrs[actual]
    return None, None


def _positive_float(value: object) -> float | None:
    try:
        array = np.asarray(value)
        if array.size != 1:
            return None
        number = float(array.reshape(-1)[0])
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _sampling_metadata(
    dataset: h5py.Dataset, adapter: BaseDatasetAdapter
) -> tuple[float | None, str | None]:
    key, value = _attribute(dataset, adapter.sensor_attribute_aliases("sampling_rate"))
    direct = _positive_float(value)
    if direct is not None:
        return direct, f"dataset_attribute:{key}"
    key, value = _attribute(
        dataset, adapter.sensor_attribute_aliases("sampling_interval")
    )
    interval = _positive_float(value)
    if interval is not None:
        derived = 1.0 / interval
        if math.isfinite(derived) and derived > 0:
            return derived, f"derived:1/dataset_attribute:{key}"
    return None, None


def _unit_metadata(
    dataset: h5py.Dataset, adapter: BaseDatasetAdapter
) -> tuple[str | None, str | None]:
    key, value = _attribute(dataset, adapter.sensor_attribute_aliases("unit"))
    if key is None:
        return None, None
    normalized = _jsonable(value)
    if isinstance(normalized, list) and len(normalized) == 1:
        normalized = normalized[0]
    text = str(normalized).strip()
    return (text, f"dataset_attribute:{key}") if text else (None, None)


def _timestamp_metadata(
    dataset: h5py.Dataset, adapter: BaseDatasetAdapter
) -> tuple[datetime | None, str | None, str | None]:
    key, value = _attribute(
        dataset, adapter.sensor_attribute_aliases("start_timestamp")
    )
    if key is None:
        return None, None, None
    raw = _jsonable(value)
    if isinstance(raw, list) and len(raw) == 1:
        raw = raw[0]
    parsed = adapter.parse_sensor_timestamp(raw)
    return (
        parsed,
        f"dataset_attribute:{key}" if parsed is not None else None,
        str(raw),
    )


@dataclass(slots=True)
class _Accumulator:
    count: int = 0
    mean: float = 0.0
    m2: float = 0.0
    minimum: float | None = None
    maximum: float | None = None
    nan_count: int = 0
    inf_count: int = 0
    sampled_value_count: int = 0

    def update(self, values: np.ndarray) -> None:
        array = np.asarray(values)
        self.sampled_value_count += int(array.size)
        floats = array.astype(np.float64, copy=False).reshape(-1)
        self.nan_count += int(np.isnan(floats).sum())
        self.inf_count += int(np.isinf(floats).sum())
        finite = floats[np.isfinite(floats)]
        if not finite.size:
            return
        batch_count = int(finite.size)
        batch_mean = float(finite.mean())
        differences = finite - batch_mean
        batch_m2 = float(np.dot(differences, differences))
        if self.count == 0:
            self.count = batch_count
            self.mean = batch_mean
            self.m2 = batch_m2
        else:
            total = self.count + batch_count
            delta = batch_mean - self.mean
            self.m2 += batch_m2 + delta * delta * self.count * batch_count / total
            self.mean += delta * batch_count / total
            self.count = total
        batch_min = float(finite.min())
        batch_max = float(finite.max())
        self.minimum = (
            batch_min if self.minimum is None else min(self.minimum, batch_min)
        )
        self.maximum = (
            batch_max if self.maximum is None else max(self.maximum, batch_max)
        )

    def result(self, scope: str, *, reason: str | None = None) -> dict[str, Any]:
        return {
            "statistics_scope": scope,
            "statistics_reason": reason,
            "sampled_value_count": self.sampled_value_count,
            "finite_count": self.count,
            "nan_count": self.nan_count,
            "inf_count": self.inf_count,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "mean": self.mean if self.count else None,
            "standard_deviation": (
                math.sqrt(max(0.0, self.m2 / self.count)) if self.count else None
            ),
            "constant_array": (
                self.minimum == self.maximum and self.count == self.sampled_value_count
                if self.sampled_value_count and scope in {"sampled", "full"}
                else None
            ),
        }


def _metadata_statistics() -> dict[str, Any]:
    return {
        "statistics_scope": "metadata_only",
        "statistics_reason": None,
        "sampled_value_count": None,
        "finite_count": None,
        "nan_count": None,
        "inf_count": None,
        "minimum": None,
        "maximum": None,
        "mean": None,
        "standard_deviation": None,
        "constant_array": None,
    }


def _sample_values(
    dataset: h5py.Dataset, *, points: int, seed: int, max_block_bytes: int
) -> tuple[np.ndarray | None, str | None]:
    if dataset.size == 0:
        return np.asarray([], dtype=dataset.dtype), None
    if max(1, dataset.dtype.itemsize) > max_block_bytes:
        return None, "one dataset value exceeds max_block_bytes"
    if dataset.shape == ():
        return np.asarray([dataset[()]]), None
    sample_count = min(int(dataset.size), points)
    if sample_count == dataset.size:
        linear_indices = np.arange(dataset.size, dtype=np.int64)
    else:
        rng = np.random.default_rng(seed)
        linear_indices = np.sort(
            rng.choice(dataset.size, size=sample_count, replace=False)
        )
    if dataset.ndim == 1:
        return np.asarray(dataset[linear_indices]), None
    coordinates = np.unravel_index(linear_indices, dataset.shape)
    values = np.empty(sample_count, dtype=dataset.dtype)
    for index in range(sample_count):
        coordinate = tuple(int(axis[index]) for axis in coordinates)
        values[index] = dataset[coordinate]
    return values, None


def _block_slices(
    shape: tuple[int, ...], *, itemsize: int, max_block_bytes: int
) -> Iterator[tuple[slice, ...]]:
    if not shape or any(dimension == 0 for dimension in shape):
        return
    maximum_elements = max(1, max_block_bytes // max(1, itemsize))
    block_shape = list(shape)
    while math.prod(block_shape) > maximum_elements:
        axis = max(range(len(block_shape)), key=block_shape.__getitem__)
        if block_shape[axis] <= 1:
            raise ValueError("one dataset value exceeds max_block_bytes")
        block_shape[axis] = max(1, block_shape[axis] // 2)
    starts = (range(0, size, block) for size, block in zip(shape, block_shape))
    for origin in product(*starts):
        yield tuple(
            slice(start, min(size, start + block))
            for start, size, block in zip(origin, shape, block_shape)
        )


def _full_blocks(
    dataset: h5py.Dataset, *, max_block_bytes: int
) -> Iterator[np.ndarray]:
    if dataset.shape == ():
        if max(1, dataset.dtype.itemsize) > max_block_bytes:
            raise ValueError("one dataset value exceeds max_block_bytes")
        yield np.asarray([dataset[()]])
        return
    for selection in _block_slices(
        tuple(int(value) for value in dataset.shape),
        itemsize=dataset.dtype.itemsize,
        max_block_bytes=max_block_bytes,
    ):
        yield np.asarray(dataset[selection])


def _statistics(
    dataset: h5py.Dataset,
    *,
    options: SensorProfileOptions,
    identity: str,
) -> dict[str, Any]:
    if options.mode == "metadata":
        return _metadata_statistics()
    if dataset.is_virtual or dataset.external:
        result = _metadata_statistics()
        result.update(
            {
                "statistics_scope": "unsupported",
                "statistics_reason": (
                    "virtual or external-storage datasets are not dereferenced"
                ),
            }
        )
        return result
    if dataset.dtype.kind not in "biuf":
        result = _metadata_statistics()
        result.update(
            {
                "statistics_scope": "unsupported",
                "statistics_reason": f"dtype kind {dataset.dtype.kind!r} is not numeric",
            }
        )
        return result
    accumulator = _Accumulator()
    if options.mode == "sampled":
        digest = sha256(f"{options.seed}:{identity}".encode("utf-8")).digest()
        sample_seed = int.from_bytes(digest[:8], "big")
        values, reason = _sample_values(
            dataset,
            points=options.sample_points,
            seed=sample_seed,
            max_block_bytes=options.max_block_bytes,
        )
        if values is None:
            return _Accumulator().result("unsupported", reason=reason)
        accumulator.update(values)
        return accumulator.result("sampled")
    try:
        for block in _full_blocks(dataset, max_block_bytes=options.max_block_bytes):
            accumulator.update(block)
    except (OSError, ValueError) as exc:
        return accumulator.result("failed", reason=f"{type(exc).__name__}: {exc}")
    return accumulator.result("full")


def _shape_details(shape: tuple[int, ...]) -> tuple[int, int]:
    if shape == ():
        return 1, 1
    if not shape:
        return 0, 0
    sample_count = int(shape[0])
    channel_count = int(math.prod(shape[1:])) if len(shape) > 1 else 1
    return sample_count, channel_count


def _source_identity(
    source: SensorSource,
    *,
    nested_member_path: str | None,
    adapter: BaseDatasetAdapter,
) -> dict[str, Any]:
    nested_run = source.nested_archive_run_token
    internal_name = nested_member_path or source.outer_member_path
    if nested_member_path is None and source.inventory_internal_run_parse_error:
        internal_run = source.inventory_internal_run_token
        internal_error = source.inventory_internal_run_parse_error
    else:
        try:
            internal_run = (
                source.inventory_internal_run_token
                if nested_member_path is None
                and source.inventory_internal_run_token is not None
                else adapter.parse_run(Path(internal_name).name)
            )
            internal_error = None
        except ValueError as exc:
            internal_run = None
            internal_error = str(exc)
    run = (
        source.authoritative_outer_run
        if source.authoritative_outer_run is not None
        else nested_run
    )
    matches = (
        internal_run == run if internal_run is not None and run is not None else None
    )
    return {
        "run": run,
        "run_identity_source": (
            "outer_archive"
            if source.authoritative_outer_run is not None
            else "nested_archive"
        ),
        "authoritative_outer_run": source.authoritative_outer_run,
        "nested_archive_run_token": nested_run,
        "internal_run_token": internal_run,
        "internal_run_matches_authoritative": matches,
        "internal_run_parse_error": internal_error,
    }


def _missing_expected(
    paths: set[str], modality: str, expected: Mapping[str, Any] | None
) -> list[str]:
    if not expected:
        return []
    rules = expected.get(modality)
    if not isinstance(rules, Mapping):
        return []
    missing = [
        str(path) for path in rules.get("required", ()) if str(path) not in paths
    ]
    alternatives = rules.get("alternatives", {})
    if isinstance(alternatives, Mapping):
        for name, candidates in alternatives.items():
            if not any(str(candidate) in paths for candidate in candidates):
                missing.append(f"{name}:one_of({','.join(map(str, candidates))})")
    return missing


def profile_hdf5_file(
    path: Path,
    *,
    source: SensorSource,
    nested_member_path: str | None,
    materialized_bytes: int,
    adapter: BaseDatasetAdapter,
    options: SensorProfileOptions,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[SensorProfileIssue]]:
    """Profile one seekable HDF5 file and continue cleanly on member failure."""

    started = time.monotonic()
    source_name = (
        f"{source.source_key}!{nested_member_path}"
        if nested_member_path
        else source.source_key
    )
    identity = _source_identity(
        source, nested_member_path=nested_member_path, adapter=adapter
    )
    hdf_member_id = deterministic_id(
        "hdf5_member",
        {
            "archive_relative_path": source.archive_relative_path,
            "outer_member": source.outer_member_path,
            "nested_member": nested_member_path,
        },
    )
    member_row: dict[str, Any] = {
        "schema_version": SENSOR_PROFILE_SCHEMA_VERSION,
        "hdf5_member_id": hdf_member_id,
        "inventory_member_id": source.inventory_member_id,
        "archive_asset_id": source.archive_asset_id,
        "archive_relative_path": source.archive_relative_path,
        "outer_archive_member": source.outer_member_path,
        "nested_archive_member": nested_member_path,
        "hdf5_member_path": nested_member_path or source.outer_member_path,
        "experiment": source.experiment,
        **identity,
        "modality": source.modality,
        "status": "ok",
        "dataset_count": 0,
        "file_schema_id": None,
        "missing_expected_paths_json": "[]",
        "start_timestamp_utc": None,
        "end_timestamp_utc": None,
        "timestamp_source_count": 0,
        "timestamp_missing_count": None,
        "timestamp_duplicate_count": None,
        "timestamp_non_monotonic_count": None,
        "materialized_bytes": materialized_bytes,
        "elapsed_seconds": None,
        "error": None,
    }
    rows: list[dict[str, Any]] = []
    issues: list[SensorProfileIssue] = []
    try:
        with h5py.File(path, mode="r") as handle:
            datasets: list[tuple[str, h5py.Dataset]] = []

            def visitor(name: str, item: h5py.Dataset | h5py.Group) -> None:
                if isinstance(item, h5py.Dataset):
                    datasets.append(("/" + name, item))

            handle.visititems(visitor)
            dataset_paths = {name for name, _ in datasets}
            missing = _missing_expected(
                dataset_paths, source.modality, options.expected_paths
            )
            member_row["missing_expected_paths_json"] = _canonical_json(missing)
            timestamps: list[tuple[datetime, datetime]] = []
            schema_parts: list[dict[str, Any]] = []
            for hdf5_path, dataset in sorted(datasets, key=lambda item: item[0]):
                shape = tuple(int(value) for value in dataset.shape)
                role = adapter.classify_sensor_path(hdf5_path)
                sample_count, channel_count = _shape_details(shape)
                sampling_rate, sampling_evidence = _sampling_metadata(dataset, adapter)
                duration = (
                    sample_count / sampling_rate
                    if sampling_rate is not None and sample_count >= 0
                    else None
                )
                start, start_evidence, start_raw = _timestamp_metadata(dataset, adapter)
                end = (
                    start + timedelta(seconds=max(0, sample_count - 1) / sampling_rate)
                    if start is not None and sampling_rate is not None
                    else None
                )
                if start is not None:
                    timestamps.append((start, end or start))
                unit, unit_evidence = _unit_metadata(dataset, adapter)
                contract_asset_id = deterministic_id(
                    "sensor_source_asset",
                    {
                        "archive": source.archive_relative_path,
                        "outer_member": source.outer_member_path,
                        "nested_member": nested_member_path,
                    },
                )
                contract = SensorRecord(
                    asset_id=contract_asset_id,
                    hdf5_path=hdf5_path,
                    shape=shape,
                    dtype=str(dataset.dtype),
                    channel_role=role,
                    sampling_rate_hz=sampling_rate,
                    duration_seconds=duration,
                    unit=unit,
                    start_timestamp=start,
                    end_timestamp=end,
                )
                profile_id = deterministic_id(
                    "sensor_profile",
                    {
                        "hdf5_member_id": hdf_member_id,
                        "hdf5_path": hdf5_path,
                    },
                )
                statistics = _statistics(
                    dataset,
                    options=options,
                    identity=f"{source_name}:{hdf5_path}",
                )
                attributes = _attribute_mapping(dataset)
                row = {
                    "schema_version": SENSOR_PROFILE_SCHEMA_VERSION,
                    "sensor_id": profile_id,
                    "contract_sensor_id": contract.sensor_id,
                    "contract_asset_id": contract_asset_id,
                    "hdf5_member_id": hdf_member_id,
                    "inventory_member_id": source.inventory_member_id,
                    "archive_asset_id": source.archive_asset_id,
                    "archive_relative_path": source.archive_relative_path,
                    "outer_archive_member": source.outer_member_path,
                    "nested_archive_member": nested_member_path,
                    "hdf5_member_path": nested_member_path or source.outer_member_path,
                    "experiment": source.experiment,
                    **identity,
                    "modality": source.modality,
                    "hdf5_path": hdf5_path,
                    "channel_role": role,
                    "shape_json": _canonical_json(list(shape)),
                    "rank": dataset.ndim,
                    "dtype": str(dataset.dtype),
                    "byte_order": dataset.dtype.byteorder,
                    "chunks_json": (
                        _canonical_json(list(dataset.chunks))
                        if dataset.chunks is not None
                        else None
                    ),
                    "compression": dataset.compression,
                    "compression_options_json": (
                        _canonical_json(_jsonable(dataset.compression_opts))
                        if dataset.compression_opts is not None
                        else None
                    ),
                    "is_virtual": bool(dataset.is_virtual),
                    "external_storage_json": _canonical_json(
                        [
                            {"name": name, "offset": offset, "size": size}
                            for name, offset, size in (dataset.external or ())
                        ]
                    ),
                    "attributes_json": _canonical_json(attributes),
                    "unit": unit,
                    "unit_evidence": unit_evidence,
                    "element_count": int(dataset.size),
                    "sample_count": sample_count,
                    "channel_count": channel_count,
                    "sampling_rate_hz": sampling_rate,
                    "sampling_rate_evidence": sampling_evidence,
                    "duration_seconds": duration,
                    "duration_evidence": (
                        "sample_count/sampling_rate_hz"
                        if duration is not None
                        else None
                    ),
                    "start_timestamp_utc": (
                        start.astimezone(timezone.utc).isoformat() if start else None
                    ),
                    "end_timestamp_utc": (
                        end.astimezone(timezone.utc).isoformat() if end else None
                    ),
                    "timestamp_source_kind": (
                        "dataset_attribute" if start is not None else None
                    ),
                    "timestamp_source": start_evidence,
                    "timestamp_raw": start_raw,
                    "timestamp_count": None,
                    "cadence_seconds": (
                        1.0 / sampling_rate if sampling_rate is not None else None
                    ),
                    "cadence_evidence": sampling_evidence,
                    "timestamp_missing_count": None,
                    "timestamp_duplicate_count": None,
                    "timestamp_non_monotonic_count": None,
                    "empty_array": dataset.size == 0,
                    **statistics,
                    "dataset_schema_id": deterministic_id(
                        "hdf5_dataset_schema",
                        {
                            "hdf5_path": hdf5_path,
                            "shape": shape,
                            "dtype": str(dataset.dtype),
                            "chunks": dataset.chunks,
                            "compression": dataset.compression,
                            "role": role,
                            "sampling_rate_hz": sampling_rate,
                        },
                    ),
                    "file_schema_id": None,
                    "error": None,
                }
                rows.append(row)
                schema_parts.append(
                    {
                        "path": hdf5_path,
                        "shape": shape,
                        "dtype": str(dataset.dtype),
                        "role": role,
                        "sampling_rate_hz": sampling_rate,
                    }
                )
            file_schema_id = deterministic_id(
                "hdf5_file_schema", {"datasets": schema_parts}
            )
            for row in rows:
                row["file_schema_id"] = file_schema_id
            member_row["dataset_count"] = len(rows)
            member_row["file_schema_id"] = file_schema_id
            if timestamps:
                member_row["start_timestamp_utc"] = min(
                    item[0] for item in timestamps
                ).isoformat()
                member_row["end_timestamp_utc"] = max(
                    item[1] for item in timestamps
                ).isoformat()
                member_row["timestamp_source_count"] = len(timestamps)
            if missing:
                issues.append(
                    SensorProfileIssue(
                        "warning",
                        "missing_expected_paths",
                        source_name,
                        "Expected-path coverage is absent: " + ", ".join(missing),
                    )
                )
    except (OSError, RuntimeError, ValueError) as exc:
        member_row["status"] = "error"
        member_row["error"] = f"{type(exc).__name__}: {exc}"
        issues.append(
            SensorProfileIssue(
                "error",
                "unreadable_hdf5_member",
                source_name,
                member_row["error"],
            )
        )
    member_row["elapsed_seconds"] = time.monotonic() - started
    if identity["internal_run_matches_authoritative"] is False:
        issues.append(
            SensorProfileIssue(
                "warning",
                "internal_run_conflict",
                source_name,
                "Internal member run token differs from the authoritative run; "
                "the authoritative archive/nested-archive run was retained.",
            )
        )
    return rows, member_row, issues


def _direct_reference(source: SensorSource) -> ArchiveMemberRef:
    return ArchiveMemberRef(
        archive_path=source.archive_path,
        archive_relative_path=source.archive_relative_path,
        member_path=source.outer_member_path,
        member_occurrence=source.member_occurrence,
        expected_compressed_size_bytes=source.compressed_size_bytes,
        expected_uncompressed_size_bytes=source.uncompressed_size_bytes,
        expected_crc32=source.crc32,
    )


def profile_sensor_sources(
    sources: Sequence[SensorSource],
    *,
    adapter: BaseDatasetAdapter,
    options: SensorProfileOptions,
    discovered_source_count: int | None = None,
    limited: bool = False,
) -> SensorProfileResult:
    """Profile direct and one-level nested HDF5 members sequentially."""

    if options.mode == "full" and not options.full_scan_authorized:
        raise ValueError("full statistics require an explicit positive source limit")
    started = time.monotonic()
    sensors: list[dict[str, Any]] = []
    members: list[dict[str, Any]] = []
    issues: list[SensorProfileIssue] = []
    for source in sources:
        reference = _direct_reference(source)
        if not source.is_nested_container:
            try:
                with materialize_archive_member(
                    reference,
                    temp_root=options.temp_root,
                    max_member_bytes=options.max_member_bytes,
                ) as path:
                    rows, member, found = profile_hdf5_file(
                        path,
                        source=source,
                        nested_member_path=None,
                        materialized_bytes=path.stat().st_size,
                        adapter=adapter,
                        options=options,
                    )
            except (ArchiveMaterializationError, OSError) as exc:
                rows = []
                member = _failed_member_row(source, None, exc, adapter)
                found = [
                    SensorProfileIssue(
                        "error",
                        "member_materialization_failed",
                        source.source_key,
                        f"{type(exc).__name__}: {exc}",
                    )
                ]
            sensors.extend(rows)
            members.append(member)
            issues.extend(found)
            continue

        try:
            yielded = iter_materialized_nested_members(
                reference,
                suffixes=_HDF_SUFFIXES,
                temp_root=options.temp_root,
                max_member_bytes=options.max_member_bytes,
            )
            found_any = False
            for materialized in yielded:
                found_any = True
                if materialized.path is None:
                    members.append(
                        _failed_member_row(
                            source,
                            materialized.reference.nested_member_path,
                            RuntimeError(materialized.error or "nested payload failed"),
                            adapter,
                        )
                    )
                    issues.append(
                        SensorProfileIssue(
                            "error",
                            "nested_member_materialization_failed",
                            source.source_key,
                            materialized.error or "nested payload failed",
                        )
                    )
                    continue
                rows, member, found = profile_hdf5_file(
                    materialized.path,
                    source=source,
                    nested_member_path=materialized.reference.nested_member_path,
                    materialized_bytes=materialized.bytes_written,
                    adapter=adapter,
                    options=options,
                )
                sensors.extend(rows)
                members.append(member)
                issues.extend(found)
            if not found_any:
                issues.append(
                    SensorProfileIssue(
                        "warning",
                        "nested_archive_without_hdf5",
                        source.source_key,
                        "Nested ZIP contains no .h5 or .hdf5 members.",
                    )
                )
        except (ArchiveMaterializationError, OSError) as exc:
            members.append(_failed_member_row(source, None, exc, adapter))
            issues.append(
                SensorProfileIssue(
                    "error",
                    "nested_archive_failed",
                    source.source_key,
                    f"{type(exc).__name__}: {exc}",
                )
            )
    return SensorProfileResult(
        sensors=sensors,
        hdf5_members=members,
        issues=issues,
        mode=options.mode,
        discovered_source_count=(
            len(sources) if discovered_source_count is None else discovered_source_count
        ),
        selected_source_count=len(sources),
        limited=limited,
        elapsed_seconds=time.monotonic() - started,
    )


def _failed_member_row(
    source: SensorSource,
    nested_member_path: str | None,
    error: BaseException,
    adapter: BaseDatasetAdapter,
) -> dict[str, Any]:
    identity = _source_identity(
        source, nested_member_path=nested_member_path, adapter=adapter
    )
    return {
        "schema_version": SENSOR_PROFILE_SCHEMA_VERSION,
        "hdf5_member_id": deterministic_id(
            "hdf5_member",
            {
                "archive_relative_path": source.archive_relative_path,
                "outer_member": source.outer_member_path,
                "nested_member": nested_member_path,
            },
        ),
        "inventory_member_id": source.inventory_member_id,
        "archive_asset_id": source.archive_asset_id,
        "archive_relative_path": source.archive_relative_path,
        "outer_archive_member": source.outer_member_path,
        "nested_archive_member": nested_member_path,
        "hdf5_member_path": nested_member_path or source.outer_member_path,
        "experiment": source.experiment,
        **identity,
        "modality": source.modality,
        "status": "error",
        "dataset_count": 0,
        "file_schema_id": None,
        "missing_expected_paths_json": "[]",
        "start_timestamp_utc": None,
        "end_timestamp_utc": None,
        "timestamp_source_count": 0,
        "timestamp_missing_count": None,
        "timestamp_duplicate_count": None,
        "timestamp_non_monotonic_count": None,
        "materialized_bytes": 0,
        "elapsed_seconds": 0.0,
        "error": f"{type(error).__name__}: {error}",
    }


def build_hdf5_schema(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    paths: dict[str, dict[str, Any]] = {}
    file_schema_member_pairs: set[tuple[str, str]] = set()
    for row in rows:
        path = str(row["hdf5_path"])
        bucket = paths.setdefault(
            path,
            {
                "count": 0,
                "channel_roles": Counter(),
                "shapes": Counter(),
                "dtypes": Counter(),
                "byte_orders": Counter(),
                "chunks": Counter(),
                "compressions": Counter(),
                "sampling_rates_hz": Counter(),
                "sampling_rate_evidence": Counter(),
                "units": Counter(),
                "attribute_keys": Counter(),
            },
        )
        bucket["count"] += 1
        for key, value in (
            ("channel_roles", row["channel_role"]),
            ("shapes", row["shape_json"]),
            ("dtypes", row["dtype"]),
            ("byte_orders", row["byte_order"]),
            ("chunks", row["chunks_json"]),
            ("compressions", row["compression"]),
            ("sampling_rates_hz", row["sampling_rate_hz"]),
            ("sampling_rate_evidence", row["sampling_rate_evidence"]),
            ("units", row["unit"]),
        ):
            if value is not None:
                bucket[key][str(value)] += 1
        try:
            attributes = json.loads(str(row["attributes_json"]))
        except (TypeError, json.JSONDecodeError):
            attributes = {}
        if isinstance(attributes, Mapping):
            for key in attributes:
                bucket["attribute_keys"][str(key)] += 1
        if row["file_schema_id"] is not None:
            file_schema_member_pairs.add(
                (str(row["hdf5_member_id"]), str(row["file_schema_id"]))
            )
    serializable: dict[str, Any] = {}
    for path, bucket in sorted(paths.items()):
        serializable[path] = {
            "count": bucket["count"],
            **{
                key: dict(sorted(bucket[key].items()))
                for key in (
                    "channel_roles",
                    "shapes",
                    "dtypes",
                    "byte_orders",
                    "chunks",
                    "compressions",
                    "sampling_rates_hz",
                    "sampling_rate_evidence",
                    "units",
                    "attribute_keys",
                )
            },
        }
    return {
        "schema_version": SENSOR_PROFILE_SCHEMA_VERSION,
        "dataset_paths": serializable,
        "file_schema_counts": dict(
            sorted(Counter(schema for _, schema in file_schema_member_pairs).items())
        ),
    }


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _summary_markdown(summary: Mapping[str, Any], schema: Mapping[str, Any]) -> str:
    lines = [
        "# HDF5 and sensor profile",
        "",
        f"Schema version: `{summary['schema_version']}`",
        f"Mode: `{summary['mode']}`",
        "",
        "Each HDF5 member was materialized one at a time in a unique temporary "
        "directory and removed after inspection. No permanent extraction occurred.",
        "",
        "## Coverage",
        "",
        f"- Selected D1.1 source rows: {summary['selected_source_count']}",
        f"- Profiled HDF5 members: {summary['profiled_hdf5_member_count']}",
        f"- Readable members: {summary['readable_hdf5_member_count']}",
        f"- Unreadable members: {summary['unreadable_hdf5_member_count']}",
        f"- HDF5 datasets: {summary['sensor_dataset_count']}",
        f"- Unknown/unmapped paths: {summary['unknown_path_count']}",
        f"- Timestamped datasets: {summary['timestamped_dataset_count']}",
        "",
        "## Channels by experiment and run",
        "",
        "| Experiment/run | Role counts |",
        "|---|---|",
    ]
    for key, values in summary["channels_by_experiment_run"].items():
        detail = ", ".join(f"{role}: {count}" for role, count in values.items())
        lines.append(f"| {key} | {detail} |")
    lines.extend(
        ["", "## Exact array shapes", "", "| Shape | Dataset rows |", "|---|---:|"]
    )
    for shape, count in summary["shape_counts"].items():
        lines.append(f"| `{shape}` | {count} |")
    lines.extend(["", "## Dtypes", "", "| Dtype | Dataset rows |", "|---|---:|"])
    for dtype, count in summary["dtype_counts"].items():
        lines.append(f"| `{dtype}` | {count} |")
    lines.extend(
        [
            "",
            "## Sampling-frequency and duration evidence",
            "",
            f"- Evidenced sampling-rate rows: {summary['sampling_rate_observed_count']}",
            f"- Sampling rates (Hz): `{json.dumps(summary['sampling_rate_counts_hz'], sort_keys=True)}`",
            f"- Evidence sources: `{json.dumps(summary['sampling_rate_evidence_counts'], sort_keys=True)}`",
            f"- Evidenced durations: {summary['duration_observed_count']}",
            f"- Duration min/median/max seconds: {summary['duration_seconds_min']} / "
            f"{summary['duration_seconds_median']} / {summary['duration_seconds_max']}",
            "",
            "## Schema and coverage warnings",
            "",
            f"- File schema variants: {summary['file_schema_variant_count']}",
            f"- Distinct HDF5 dataset paths: {len(schema['dataset_paths'])}",
            f"- Variable path schemas: `{json.dumps(summary['variable_path_schemas'], sort_keys=True)}`",
            f"- Missing expected paths: `{json.dumps(summary['missing_expected_path_counts'], sort_keys=True)}`",
            f"- Unknown paths: `{json.dumps(summary['unknown_path_counts'], sort_keys=True)}`",
            f"- Run-token conflicts: {summary['run_token_conflict_member_count']}",
            f"- Conflict sources: `{json.dumps(summary['run_token_conflict_member_paths'])}`",
            f"- Unreadable sources: `{json.dumps(summary['unreadable_member_paths'])}`",
            "",
            "## Limitations",
            "",
            "- Metadata mode does not read array values; statistics and value-quality "
            "counts remain null.",
            "- Sampled statistics describe only deterministic sampled values and do "
            "not prove whole-array constancy or extrema.",
            "- Full statistics are chunk-bounded but are not run without an explicit "
            "positive source limit.",
            "- A missing expected path is a coverage warning, not evidence of corruption.",
            "- Sampling rates and UTC timestamps are recorded only when supported by "
            "attributes; no historical 102,400 Hz fallback is applied.",
            "- Internal run tokens remain separate from authoritative archive or "
            "nested-archive run identity.",
            "- For rank greater than one, sample count uses axis 0 and channel count "
            "uses the product of remaining axes; this layout inference must be reviewed "
            "for unknown transforms.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_sensor_run(
    result: SensorProfileResult,
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
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
    sensor_csv = run.run_directory / "tables/sensor_profile.csv"
    sensor_parquet = run.run_directory / "tables/sensor_profile.parquet"
    member_csv = run.run_directory / "tables/hdf5_members.csv"
    member_parquet = run.run_directory / "tables/hdf5_members.parquet"
    _write_csv(sensor_csv, result.sensors)
    pd.DataFrame(result.sensors).to_parquet(sensor_parquet, index=False)
    _write_csv(member_csv, result.hdf5_members)
    pd.DataFrame(result.hdf5_members).to_parquet(member_parquet, index=False)
    schema = build_hdf5_schema(result.sensors)
    schema_path = run.run_directory / "reports/hdf5_schema.json"
    schema_path.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = result.summary()
    summary_json = run.run_directory / "reports/sensor_summary.json"
    summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary_md = run.run_directory / "reports/sensor_summary.md"
    summary_md.write_text(_summary_markdown(summary, schema), encoding="utf-8")
    warnings_path = run.run_directory / "reports/warnings.json"
    warnings_path.write_text(
        json.dumps(
            {
                "schema_version": SENSOR_PROFILE_SCHEMA_VERSION,
                "issues": [asdict(issue) for issue in result.issues],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    for path, role in (
        (sensor_csv, "sensor_profile_csv"),
        (sensor_parquet, "sensor_profile_parquet"),
        (member_csv, "hdf5_member_profile_csv"),
        (member_parquet, "hdf5_member_profile_parquet"),
        (schema_path, "hdf5_schema"),
        (summary_json, "sensor_summary_json"),
        (summary_md, "sensor_summary_markdown"),
        (warnings_path, "warnings"),
    ):
        artifacts.append(run.artifact(path, role=role))
    provenance_path = run.write_provenance(artifacts)
    with_provenance = [
        *artifacts,
        run.artifact(provenance_path, role="run_provenance"),
    ]
    run.write_output_manifest(with_provenance)
    return with_provenance
