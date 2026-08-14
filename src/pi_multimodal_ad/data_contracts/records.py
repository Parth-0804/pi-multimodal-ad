"""Typed, validated, dataset-neutral metadata records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
import math
from typing import Any, Literal

from .identifiers import deterministic_id
from .validation import (
    fail,
    optional_aware_datetime,
    optional_text,
    require_aware_datetime,
    require_hdf5_path,
    require_relative_path,
    require_schema_version,
    require_text,
    require_token,
)

SCHEMA_VERSION = "1.0.0"
AssetKind = Literal["file", "archive", "archive_member"]


def _validate_non_negative_int(
    record_type: str, field_name: str, value: int | None
) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        fail(record_type, field_name, "must be a non-negative integer or null")


def _validate_positive_int(record_type: str, field_name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        fail(record_type, field_name, "must be a positive integer")


def _validated_number(
    record_type: str,
    field_name: str,
    value: object,
    *,
    allow_zero: bool,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(record_type, field_name, "must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        fail(record_type, field_name, "must be finite")
    if number < 0 or (number == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        fail(record_type, field_name, f"must be {qualifier}")
    return number


def _validate_reference(record_type: str, field_name: str, value: object) -> str:
    text = require_text(record_type, field_name, value)
    if "_" not in text:
        fail(record_type, field_name, "must be a namespaced deterministic record ID")
    return text


def _to_serializable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    if isinstance(value, Mapping):
        return {str(key): _to_serializable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_serializable(item) for item in value]
    if isinstance(value, list):
        return [_to_serializable(item) for item in value]
    if is_dataclass(value):
        return _to_serializable(asdict(value))
    return value


def record_to_dict(record: object) -> dict[str, Any]:
    """Serialize a contract dataclass to JSON-compatible primitives."""

    if not is_dataclass(record) or isinstance(record, type):
        raise TypeError("record_to_dict expects a dataclass instance")
    serialized = _to_serializable(asdict(record))
    if not isinstance(serialized, dict):
        raise TypeError("record serialization did not produce an object")
    return serialized


@dataclass(frozen=True, slots=True)
class AssetRecord:
    """Identity and storage metadata for a file, archive, or archive member."""

    dataset: str
    relative_path: str
    asset_kind: AssetKind
    modality: str
    experiment: str
    run: int | None = None
    archive_member: str | None = None
    size_bytes: int | None = None
    uncompressed_size_bytes: int | None = None
    checksum_algorithm: str | None = None
    checksum: str | None = None
    schema_version: str = SCHEMA_VERSION
    asset_id: str = field(init=False)

    def __post_init__(self) -> None:
        record_type = type(self).__name__
        require_schema_version(record_type, self.schema_version, SCHEMA_VERSION)
        require_token(record_type, "dataset", self.dataset)
        require_relative_path(record_type, "relative_path", self.relative_path)
        require_token(record_type, "modality", self.modality)
        require_text(record_type, "experiment", self.experiment)
        if self.asset_kind not in {"file", "archive", "archive_member"}:
            fail(record_type, "asset_kind", "must be file, archive, or archive_member")
        if self.run is not None:
            _validate_positive_int(record_type, "run", self.run)
        if self.asset_kind == "archive_member":
            if self.archive_member is None:
                fail(record_type, "archive_member", "is required for an archive member")
            require_relative_path(record_type, "archive_member", self.archive_member)
        elif self.archive_member is not None:
            fail(
                record_type,
                "archive_member",
                "must be null unless asset_kind is archive_member",
            )
        _validate_non_negative_int(record_type, "size_bytes", self.size_bytes)
        _validate_non_negative_int(
            record_type, "uncompressed_size_bytes", self.uncompressed_size_bytes
        )
        algorithm = (
            require_token(record_type, "checksum_algorithm", self.checksum_algorithm)
            if self.checksum_algorithm is not None
            else None
        )
        checksum = optional_text(record_type, "checksum", self.checksum)
        if (algorithm is None) != (checksum is None):
            fail(
                record_type,
                "checksum",
                "checksum_algorithm and checksum must either both be set or both be null",
            )
        object.__setattr__(
            self,
            "asset_id",
            deterministic_id(
                "asset",
                {
                    "schema_version": self.schema_version,
                    "dataset": self.dataset,
                    "relative_path": self.relative_path,
                    "asset_kind": self.asset_kind,
                    "archive_member": self.archive_member,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class ImageRecord:
    """Structural image metadata linked to one AssetRecord."""

    asset_id: str
    width: int
    height: int
    channels: int
    dtype: str
    timestamp: datetime | None = None
    tooth_id: str | None = None
    inspection_id: str | None = None
    annotation_types: tuple[str, ...] = ()
    annotation_refs: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION
    image_id: str = field(init=False)

    def __post_init__(self) -> None:
        record_type = type(self).__name__
        require_schema_version(record_type, self.schema_version, SCHEMA_VERSION)
        _validate_reference(record_type, "asset_id", self.asset_id)
        _validate_positive_int(record_type, "width", self.width)
        _validate_positive_int(record_type, "height", self.height)
        _validate_positive_int(record_type, "channels", self.channels)
        require_text(record_type, "dtype", self.dtype)
        optional_aware_datetime(record_type, "timestamp", self.timestamp)
        optional_text(record_type, "tooth_id", self.tooth_id)
        optional_text(record_type, "inspection_id", self.inspection_id)
        annotation_types = tuple(self.annotation_types)
        annotation_refs = tuple(self.annotation_refs)
        for index, value in enumerate(annotation_types):
            require_token(record_type, f"annotation_types[{index}]", value)
        for index, value in enumerate(annotation_refs):
            require_text(record_type, f"annotation_refs[{index}]", value)
        if len(set(annotation_refs)) != len(annotation_refs):
            fail(record_type, "annotation_refs", "must not contain duplicates")
        object.__setattr__(self, "annotation_types", annotation_types)
        object.__setattr__(self, "annotation_refs", annotation_refs)
        object.__setattr__(
            self,
            "image_id",
            deterministic_id(
                "image",
                {
                    "schema_version": self.schema_version,
                    "asset_id": self.asset_id,
                    "inspection_id": self.inspection_id,
                    "tooth_id": self.tooth_id,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class SensorRecord:
    """Structural metadata for one sensor dataset inside an HDF5 asset."""

    asset_id: str
    hdf5_path: str
    shape: tuple[int, ...]
    dtype: str
    channel_role: str
    sampling_rate_hz: float | None = None
    duration_seconds: float | None = None
    unit: str | None = None
    start_timestamp: datetime | None = None
    end_timestamp: datetime | None = None
    timestamp_hdf5_path: str | None = None
    schema_version: str = SCHEMA_VERSION
    sensor_id: str = field(init=False)

    def __post_init__(self) -> None:
        record_type = type(self).__name__
        require_schema_version(record_type, self.schema_version, SCHEMA_VERSION)
        _validate_reference(record_type, "asset_id", self.asset_id)
        require_hdf5_path(record_type, "hdf5_path", self.hdf5_path)
        shape = tuple(self.shape)
        for index, value in enumerate(shape):
            _validate_non_negative_int(record_type, f"shape[{index}]", value)
        object.__setattr__(self, "shape", shape)
        require_text(record_type, "dtype", self.dtype)
        require_token(record_type, "channel_role", self.channel_role)
        if self.sampling_rate_hz is not None:
            object.__setattr__(
                self,
                "sampling_rate_hz",
                _validated_number(
                    record_type,
                    "sampling_rate_hz",
                    self.sampling_rate_hz,
                    allow_zero=False,
                ),
            )
        if self.duration_seconds is not None:
            object.__setattr__(
                self,
                "duration_seconds",
                _validated_number(
                    record_type,
                    "duration_seconds",
                    self.duration_seconds,
                    allow_zero=True,
                ),
            )
        optional_text(record_type, "unit", self.unit)
        start = optional_aware_datetime(
            record_type, "start_timestamp", self.start_timestamp
        )
        end = optional_aware_datetime(record_type, "end_timestamp", self.end_timestamp)
        if start is not None and end is not None and end < start:
            fail(record_type, "end_timestamp", "must not precede start_timestamp")
        if self.timestamp_hdf5_path is not None:
            require_hdf5_path(
                record_type, "timestamp_hdf5_path", self.timestamp_hdf5_path
            )
        object.__setattr__(
            self,
            "sensor_id",
            deterministic_id(
                "sensor",
                {
                    "schema_version": self.schema_version,
                    "asset_id": self.asset_id,
                    "hdf5_path": self.hdf5_path,
                    "channel_role": self.channel_role,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class TargetRecord:
    """A versioned target definition at one timestamp and horizon."""

    target_name: str
    physical_meaning: str
    unit: str
    timestamp: datetime
    horizon_seconds: float
    source: str
    computation_version: str
    schema_version: str = SCHEMA_VERSION
    target_id: str = field(init=False)

    def __post_init__(self) -> None:
        record_type = type(self).__name__
        require_schema_version(record_type, self.schema_version, SCHEMA_VERSION)
        require_token(record_type, "target_name", self.target_name)
        require_text(record_type, "physical_meaning", self.physical_meaning)
        require_text(record_type, "unit", self.unit)
        require_aware_datetime(record_type, "timestamp", self.timestamp)
        horizon_seconds = _validated_number(
            record_type,
            "horizon_seconds",
            self.horizon_seconds,
            allow_zero=True,
        )
        object.__setattr__(self, "horizon_seconds", horizon_seconds)
        require_text(record_type, "source", self.source)
        require_text(record_type, "computation_version", self.computation_version)
        object.__setattr__(
            self,
            "target_id",
            deterministic_id(
                "target",
                {
                    "schema_version": self.schema_version,
                    "target_name": self.target_name,
                    "timestamp": self.timestamp,
                    "horizon_seconds": horizon_seconds,
                    "source": self.source,
                    "computation_version": self.computation_version,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class SensorWindowReference:
    """A half-open index window and/or closed timestamp interval."""

    sensor_record_id: str
    start_index: int | None = None
    end_index: int | None = None
    start_timestamp: datetime | None = None
    end_timestamp: datetime | None = None
    schema_version: str = SCHEMA_VERSION
    window_id: str = field(init=False)

    def __post_init__(self) -> None:
        record_type = type(self).__name__
        require_schema_version(record_type, self.schema_version, SCHEMA_VERSION)
        _validate_reference(record_type, "sensor_record_id", self.sensor_record_id)
        has_index_window = self.start_index is not None or self.end_index is not None
        has_time_window = (
            self.start_timestamp is not None or self.end_timestamp is not None
        )
        if not has_index_window and not has_time_window:
            fail(
                record_type,
                "start_index",
                "an index window, timestamp window, or both must be provided",
            )
        if has_index_window:
            if self.start_index is None or self.end_index is None:
                fail(
                    record_type,
                    "end_index",
                    "index boundaries must be provided together",
                )
            _validate_non_negative_int(record_type, "start_index", self.start_index)
            _validate_non_negative_int(record_type, "end_index", self.end_index)
            if self.end_index <= self.start_index:
                fail(record_type, "end_index", "must be greater than start_index")
        if has_time_window:
            if self.start_timestamp is None or self.end_timestamp is None:
                fail(
                    record_type,
                    "end_timestamp",
                    "timestamp boundaries must be provided together",
                )
            start = require_aware_datetime(
                record_type, "start_timestamp", self.start_timestamp
            )
            end = require_aware_datetime(
                record_type, "end_timestamp", self.end_timestamp
            )
            if end < start:
                fail(record_type, "end_timestamp", "must not precede start_timestamp")
        object.__setattr__(
            self,
            "window_id",
            deterministic_id(
                "sensor_window",
                {
                    "schema_version": self.schema_version,
                    "sensor_record_id": self.sensor_record_id,
                    "start_index": self.start_index,
                    "end_index": self.end_index,
                    "start_timestamp": self.start_timestamp,
                    "end_timestamp": self.end_timestamp,
                },
            ),
        )


@dataclass(frozen=True, slots=True)
class SampleRecord:
    """A leakage-auditable multimodal sample reference, without payload data."""

    input_cutoff: datetime
    sensor_windows: tuple[SensorWindowReference, ...]
    image_record_ids: tuple[str, ...]
    target_record_id: str
    group_keys: Mapping[str, str] | tuple[tuple[str, str], ...]
    split_key: str
    schema_version: str = SCHEMA_VERSION
    sample_id: str = field(init=False)

    def __post_init__(self) -> None:
        record_type = type(self).__name__
        require_schema_version(record_type, self.schema_version, SCHEMA_VERSION)
        cutoff = require_aware_datetime(record_type, "input_cutoff", self.input_cutoff)
        windows = tuple(self.sensor_windows)
        image_ids = tuple(self.image_record_ids)
        if not windows and not image_ids:
            fail(
                record_type,
                "sensor_windows",
                "at least one input reference is required",
            )
        for index, window in enumerate(windows):
            if not isinstance(window, SensorWindowReference):
                fail(
                    record_type,
                    f"sensor_windows[{index}]",
                    "must be a SensorWindowReference",
                )
            if window.end_timestamp is not None and window.end_timestamp > cutoff:
                fail(
                    record_type,
                    f"sensor_windows[{index}]",
                    "must end at or before input_cutoff",
                )
        if len({window.window_id for window in windows}) != len(windows):
            fail(record_type, "sensor_windows", "must not contain duplicate windows")
        for index, image_id in enumerate(image_ids):
            _validate_reference(record_type, f"image_record_ids[{index}]", image_id)
        if len(set(image_ids)) != len(image_ids):
            fail(record_type, "image_record_ids", "must not contain duplicates")
        _validate_reference(record_type, "target_record_id", self.target_record_id)
        if isinstance(self.group_keys, Mapping):
            group_keys = tuple(sorted(self.group_keys.items()))
        else:
            group_keys = tuple(sorted(self.group_keys))
        if not group_keys:
            fail(record_type, "group_keys", "must contain at least one grouping key")
        names: list[str] = []
        for index, pair in enumerate(group_keys):
            if not isinstance(pair, tuple) or len(pair) != 2:
                fail(
                    record_type, f"group_keys[{index}]", "must be a (name, value) pair"
                )
            name, value = pair
            require_token(record_type, f"group_keys[{index}].name", name)
            require_text(record_type, f"group_keys[{index}].value", value)
            names.append(name)
        if len(set(names)) != len(names):
            fail(record_type, "group_keys", "must not contain duplicate key names")
        require_text(record_type, "split_key", self.split_key)
        object.__setattr__(self, "sensor_windows", windows)
        object.__setattr__(self, "image_record_ids", image_ids)
        object.__setattr__(self, "group_keys", group_keys)
        object.__setattr__(
            self,
            "sample_id",
            deterministic_id(
                "sample",
                {
                    "schema_version": self.schema_version,
                    "input_cutoff": cutoff,
                    "sensor_window_ids": [window.window_id for window in windows],
                    "image_record_ids": image_ids,
                    "target_record_id": self.target_record_id,
                    "group_keys": group_keys,
                    "split_key": self.split_key,
                },
            ),
        )
