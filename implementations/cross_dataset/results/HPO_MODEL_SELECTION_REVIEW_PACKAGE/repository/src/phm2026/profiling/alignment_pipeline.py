"""Generated-artifact pipeline for evidence-gated cross-modal alignment.

This module consumes only D1.2/D1.3 profile tables.  It never opens raw data,
never constructs model samples, and never assigns meaning to the unresolved
six-hour statement.  The output is an audit of timestamp evidence and candidate
joins, not a training manifest.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import csv
import json
import math
from pathlib import Path
from typing import Any, Literal, TypeAlias

import numpy as np
import pandas as pd

from ..data_contracts import deterministic_id
from ..utils.provenance import ArtifactRecord, RunContext
from .alignment import (
    ALIGNMENT_SCHEMA_VERSION,
    AlignmentAuditResult,
    AlignmentOptions,
    CanonicalEvent,
    TimelineAuditResult,
    align_event_modalities,
    audit_timelines,
)

ALIGNMENT_PIPELINE_SCHEMA_VERSION = "1.0.0"
HDF5_EXPLICIT_UTC_CLOCK = "phm_hdf5_explicit_utc"

ProfileTable: TypeAlias = pd.DataFrame | Path | str
Direction = Literal["nearest", "past_only"]

_SENSOR_EVENT_MODALITIES = (
    "high_frequency_recording",
    "low_frequency_observation",
    "condition_indicator",
    "operating_context",
    "oil",
    "environment",
)
_ALIGNMENT_CANDIDATE_MODALITIES = (*_SENSOR_EVENT_MODALITIES, "candidate_scalar")
_VERIFIED_IMAGE_TIMESTAMP_STATUSES = {
    "verified",
    "verified_utc",
    "utc_verified",
    "explicit_utc",
}

EVENT_COLUMNS = (
    "schema_version",
    "event_id",
    "experiment",
    "run",
    "modality",
    "timestamp_utc",
    "timestamp_status",
    "timestamp_source",
    "timestamp_evidence",
    "clock_domain",
    "timestamp_raw",
    "timestamp_local_naive",
    "sequence_index",
    "source_table",
    "source_id",
    "source_references_json",
    "archive_asset_id",
    "archive_relative_path",
    "outer_archive_member",
    "nested_archive_member",
    "hdf5_member_id",
    "hdf5_member_path",
    "sensor_id",
    "hdf5_path",
    "image_id",
    "source_member_id",
    "source_relative_path",
    "inspection_id",
    "inspection_stage",
    "tooth_id",
    "image_role",
    "channel_role",
)

TIMELINE_COLUMNS = (
    "schema_version",
    "experiment",
    "run",
    "modality",
    "event_count",
    "verified_timestamp_count",
    "missing_timestamp_count",
    "noncomparable_timestamp_count",
    "earliest_timestamp_utc",
    "latest_timestamp_utc",
    "clock_domains_json",
    "duplicate_timestamp_group_count",
    "duplicate_timestamp_event_count",
    "duplicate_timestamp_event_ids_json",
    "non_monotonic_transition_count",
    "non_monotonic_transitions_json",
    "observed_cadence_seconds_json",
    "cadence_seconds_min",
    "cadence_seconds_median",
    "cadence_seconds_max",
    "ordering_basis",
    "six_hour_reference_seconds",
    "six_hour_tolerance_seconds",
    "observed_interval_count",
    "observed_six_hour_interval_count",
    "observed_six_hour_spacing",
    "six_hour_evidence_basis",
    "expected_cadence_seconds",
    "coverage_gap_count",
    "coverage_gap_status",
)

ALIGNMENT_COLUMNS = (
    "schema_version",
    "alignment_id",
    "anchor_event_id",
    "experiment",
    "run",
    "anchor_modality",
    "candidate_modality",
    "anchor_timestamp_utc",
    "selected_candidate_event_id",
    "selected_candidate_timestamp_utc",
    "signed_delta_seconds",
    "absolute_delta_seconds",
    "status",
    "match_kind",
    "comparable_candidate_count",
    "within_tolerance_candidate_ids_json",
    "nearest_candidate_event_ids_json",
    "candidate_anchor_counts_json",
    "ambiguous",
    "missing_match",
    "missing_modality",
    "anchor_timestamp_missing",
    "candidate_timestamp_missing_count",
    "candidate_timestamp_unverified_count",
    "incomparable_clock_candidate_count",
    "future_candidate_rejected_count",
    "one_to_one",
    "one_to_many",
    "many_to_one",
    "cardinality",
    "tolerance_seconds",
    "direction",
)

CANDIDATE_TARGET_COLUMNS = (
    "schema_version",
    "candidate_target_id",
    "experiment",
    "run",
    "timestamp_utc",
    "target_name",
    "target_value",
    "target_unit",
    "six_hour_interpretation",
    "source_id",
    "source_references_json",
    "status",
)

SAMPLE_OPTION_COLUMNS = (
    "schema_version",
    "option_id",
    "sample_unit",
    "input_unit",
    "grouping_keys_json",
    "anchor_time_requirement",
    "sensor_history_requirement",
    "image_requirement",
    "target_requirement",
    "advantages",
    "limitations",
    "status",
    "decision",
)

TRACE_COLUMNS = (
    "schema_version",
    "trace_id",
    "status",
    "experiment",
    "run",
    "image_event_id",
    "image_id",
    "image_source_relative_path",
    "inspection_id",
    "tooth_id",
    "image_timestamp_status",
    "image_timestamp_raw",
    "selected_sensor_event_id",
    "signed_delta_seconds",
    "absolute_delta_seconds",
    "target_event_id",
    "target_value",
    "target_unit",
    "clock_blocker",
    "target_blocker",
    "candidate_alignment_ids_json",
    "source_references_json",
)


@dataclass(frozen=True, slots=True)
class AlignmentPipelineOptions:
    """Bounded, explicit settings for alignment and cadence evidence."""

    tolerance_seconds: float = 300.0
    direction: Direction = "nearest"
    six_hour_reference_seconds: float = 6 * 60 * 60
    six_hour_tolerance_seconds: float = 60.0
    trace_example_count: int = 5

    def __post_init__(self) -> None:
        for field, value in (
            ("tolerance_seconds", self.tolerance_seconds),
            ("six_hour_reference_seconds", self.six_hour_reference_seconds),
            ("six_hour_tolerance_seconds", self.six_hour_tolerance_seconds),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or float(value) < 0
            ):
                raise ValueError(f"{field} must be a finite non-negative number")
            object.__setattr__(self, field, float(value))
        if self.six_hour_reference_seconds <= 0:
            raise ValueError("six_hour_reference_seconds must be positive")
        if self.direction not in {"nearest", "past_only"}:
            raise ValueError("direction must be nearest or past_only")
        if (
            isinstance(self.trace_example_count, bool)
            or not isinstance(self.trace_example_count, int)
            or self.trace_example_count < 0
        ):
            raise ValueError("trace_example_count must be a non-negative integer")


@dataclass(slots=True)
class AlignmentPipelineResult:
    """Machine-readable D1.4 audit artifacts before they are written."""

    options: AlignmentPipelineOptions
    events: list[CanonicalEvent]
    event_rows: list[dict[str, Any]]
    timeline_audit: TimelineAuditResult
    timeline_rows: list[dict[str, Any]]
    alignment_audits: list[AlignmentAuditResult]
    alignment_rows: list[dict[str, Any]]
    candidate_target_rows: list[dict[str, Any]]
    sample_definition_rows: list[dict[str, Any]]
    trace_rows: list[dict[str, Any]]
    input_row_counts: dict[str, int]

    def summary(self) -> dict[str, Any]:
        event_counts = Counter(event.modality for event in self.events)
        verified_counts = Counter(
            event.modality for event in self.events if event.has_verified_timestamp
        )
        sensor_candidates = set(_SENSOR_EVENT_MODALITIES)
        comparable_image_sensor_joins = sum(
            row["selected_candidate_event_id"] is not None
            and row["candidate_modality"] in sensor_candidates
            for row in self.alignment_rows
        )
        image_event_rows = [
            row for row in self.event_rows if row["modality"] == "photograph"
        ]
        image_timestamp_counts = Counter(
            str(row["timestamp_status"]) for row in image_event_rows
        )
        status = (
            "PARTIALLY_COMPLETE_BLOCKED_BY_UNVERIFIED_IMAGE_CLOCK_DOMAIN"
            if comparable_image_sensor_joins == 0
            else "ALIGNMENT_EVIDENCE_AVAILABLE_TARGET_UNRESOLVED"
        )
        six_hour_groups = sum(
            int(row["observed_six_hour_spacing"] is True) for row in self.timeline_rows
        )
        return {
            "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
            "status": status,
            "input_row_counts": dict(sorted(self.input_row_counts.items())),
            "event_count": len(self.events),
            "event_counts_by_modality": dict(sorted(event_counts.items())),
            "verified_timestamp_counts_by_modality": dict(
                sorted(verified_counts.items())
            ),
            "timeline_group_count": len(self.timeline_rows),
            "alignment_row_count": len(self.alignment_rows),
            "comparable_image_sensor_join_count": comparable_image_sensor_joins,
            "image_timestamp_status_counts": dict(
                sorted(image_timestamp_counts.items())
            ),
            "image_sensor_timestamps_comparable": comparable_image_sensor_joins > 0,
            "nearest_temporal_matching_authorized": comparable_image_sensor_joins > 0,
            "join_cardinality_computable": comparable_image_sensor_joins > 0,
            "candidate_target_count": len(self.candidate_target_rows),
            "target_definition_status": "unresolved",
            "sample_definition_option_count": len(self.sample_definition_rows),
            "trace_example_count": len(self.trace_rows),
            "blocked_trace_example_count": sum(
                row["status"] == "BLOCKED" for row in self.trace_rows
            ),
            "six_hour_reference_seconds": self.options.six_hour_reference_seconds,
            "six_hour_tolerance_seconds": self.options.six_hour_tolerance_seconds,
            "timeline_groups_with_observed_six_hour_spacing": six_hour_groups,
            "six_hour_interpretation": (
                "observed_cadence_comparison_only_not_target_horizon"
            ),
            "coverage_gap_count": None,
            "coverage_gap_status": "not_inferable_without_expected_cadence",
            "blockers": [
                "image_and_sensor_clocks_require_verified_comparability",
                "candidate_scalar_target_name_value_unit_and_time_are_unresolved",
                "six_hour_statement_semantics_are_unresolved",
            ],
        }


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        return False
    return bool(missing) if isinstance(missing, (bool, np.bool_)) else False


def _value(row: Mapping[str, Any], key: str) -> Any | None:
    value = row.get(key)
    return None if _is_missing(value) else value


def _text(row: Mapping[str, Any], key: str) -> str | None:
    value = _value(row, key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _canonical_run(value: object, *, stage: str = "unresolved") -> int | str:
    if _is_missing(value):
        return f"stage:{stage or 'unresolved'}"
    if isinstance(value, (int, np.integer)) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return int(value)
    text = str(value).strip()
    if text.isdigit():
        return int(text)
    return text or f"stage:{stage or 'unresolved'}"


def _aware_utc(value: object) -> datetime | None:
    if _is_missing(value):
        return None
    if isinstance(value, pd.Timestamp):
        parsed = value.to_pydatetime()
    elif isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if not text:
            return None
        normalized = text[:-1] + "+00:00" if text.endswith(("Z", "z")) else text
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _references(*values: object) -> tuple[str, ...]:
    references: list[str] = []
    for value in values:
        if _is_missing(value):
            continue
        text = str(value).strip()
        if text and text not in references:
            references.append(text)
    return tuple(references)


def load_profile_table(table: ProfileTable, *, name: str) -> pd.DataFrame:
    """Return a defensive DataFrame copy from a CSV/Parquet generated artifact."""

    if isinstance(table, pd.DataFrame):
        return table.copy(deep=True)
    path = Path(table)
    if not path.is_file():
        raise FileNotFoundError(f"{name} profile table does not exist: {path}")
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"{name} profile table must be CSV or Parquet: {path}")


def _event_row(
    event: CanonicalEvent,
    *,
    source_table: str,
    source_id: str,
    source: Mapping[str, Any],
    timestamp_local_naive: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
        "event_id": event.event_id,
        "experiment": event.experiment,
        "run": event.run,
        "modality": event.modality,
        "timestamp_utc": event.timestamp_utc,
        "timestamp_status": event.timestamp_status,
        "timestamp_source": event.timestamp_source,
        "timestamp_evidence": event.timestamp_evidence,
        "clock_domain": event.clock_domain,
        "timestamp_raw": event.timestamp_raw,
        "timestamp_local_naive": timestamp_local_naive,
        "sequence_index": event.sequence_index,
        "source_table": source_table,
        "source_id": source_id,
        "source_references_json": event.source_references,
        "archive_asset_id": _text(source, "archive_asset_id"),
        "archive_relative_path": _text(source, "archive_relative_path"),
        "outer_archive_member": _text(source, "outer_archive_member"),
        "nested_archive_member": _text(source, "nested_archive_member"),
        "hdf5_member_id": _text(source, "hdf5_member_id"),
        "hdf5_member_path": _text(source, "hdf5_member_path"),
        "sensor_id": _text(source, "sensor_id"),
        "hdf5_path": _text(source, "hdf5_path"),
        "image_id": _text(source, "image_id"),
        "source_member_id": _text(source, "source_member_id"),
        "source_relative_path": _text(source, "source_relative_path"),
        "inspection_id": _text(source, "inspection_id"),
        "inspection_stage": _text(source, "inspection_stage"),
        "tooth_id": _text(source, "tooth_id"),
        "image_role": _text(source, "image_role"),
        "channel_role": _text(source, "channel_role"),
    }


def _source_id(
    row: Mapping[str, Any],
    *,
    preferred: str,
    namespace: str,
    identity: Mapping[str, Any],
) -> str:
    existing = _text(row, preferred)
    return existing or deterministic_id(namespace, identity)


def _sensor_timestamp(
    row: Mapping[str, Any], *, source_table: str
) -> tuple[datetime | None, str, str | None, str | None, str | None, str | None]:
    raw_value = _value(row, "start_timestamp_utc")
    timestamp = _aware_utc(raw_value)
    if timestamp is not None:
        source = _text(row, "timestamp_source") or (
            f"{source_table}.start_timestamp_utc"
        )
        evidence = (
            f"D1.2 explicit-timezone evidence from {source}; mapped without clock "
            "or timezone inference"
        )
        return (
            timestamp,
            "verified_utc",
            source,
            evidence,
            HDF5_EXPLICIT_UTC_CLOCK,
            str(raw_value),
        )
    if raw_value is not None:
        return (
            None,
            "unverified",
            _text(row, "timestamp_source") or f"{source_table}.start_timestamp_utc",
            "D1.2 timestamp value was not an explicit timezone-aware instant",
            None,
            str(raw_value),
        )
    return (
        None,
        "missing",
        _text(row, "timestamp_source"),
        None,
        None,
        _text(row, "timestamp_raw"),
    )


def _image_timestamp(
    row: Mapping[str, Any],
) -> tuple[
    datetime | None,
    str,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
]:
    status = (_text(row, "timestamp_status") or "missing").lower()
    raw_utc = _value(row, "timestamp_utc")
    timestamp = _aware_utc(raw_utc)
    source = _text(row, "timestamp_source")
    evidence = _text(row, "timestamp_evidence")
    raw = _text(row, "timestamp_raw")
    local_naive = _text(row, "timestamp_local_naive")
    if status in _VERIFIED_IMAGE_TIMESTAMP_STATUSES and timestamp is not None:
        clock_domain = _text(row, "timestamp_clock_domain") or _text(
            row, "clock_domain"
        )
        return (
            timestamp,
            "verified_utc",
            source or "image_profile.timestamp_utc",
            evidence or "D1.3 verified explicit UTC image timestamp",
            clock_domain or "image_verified_utc_clock_unverified_against_sensor",
            raw or str(raw_utc),
            None,
        )
    if local_naive is not None or status == "timezone_unknown":
        return (
            None,
            "timezone_unknown",
            source or "image_profile.timestamp_local_naive",
            evidence,
            None,
            raw or local_naive,
            local_naive,
        )
    if raw_utc is not None:
        return (
            None,
            "unverified",
            source or "image_profile.timestamp_utc",
            evidence or "image timestamp status did not verify the UTC value",
            None,
            raw or str(raw_utc),
            None,
        )
    return None, "missing", source, evidence, None, raw, None


def _add_event(
    events: list[CanonicalEvent],
    rows: list[dict[str, Any]],
    *,
    event: CanonicalEvent,
    source_table: str,
    source_id: str,
    source: Mapping[str, Any],
    timestamp_local_naive: str | None = None,
) -> None:
    events.append(event)
    rows.append(
        _event_row(
            event,
            source_table=source_table,
            source_id=source_id,
            source=source,
            timestamp_local_naive=timestamp_local_naive,
        )
    )


def _member_events(
    members: pd.DataFrame,
    *,
    events: list[CanonicalEvent],
    event_rows: list[dict[str, Any]],
) -> None:
    modality_map = {
        "high_frequency": "high_frequency_recording",
        "low_frequency": "low_frequency_observation",
    }
    for input_index, row in enumerate(members.to_dict("records")):
        source_modality = _text(row, "modality")
        modality = modality_map.get(source_modality or "")
        if modality is None:
            continue
        if (_text(row, "status") or "ok").lower() != "ok":
            continue
        source_id = _source_id(
            row,
            preferred="hdf5_member_id",
            namespace="alignment_source",
            identity={
                "table": "hdf5_members",
                "archive": _text(row, "archive_relative_path"),
                "member": _text(row, "hdf5_member_path"),
                "row": input_index,
            },
        )
        event_id = deterministic_id(
            "canonical_event", {"modality": modality, "source_id": source_id}
        )
        timestamp, status, source, evidence, clock, raw = _sensor_timestamp(
            row, source_table="hdf5_members"
        )
        references = _references(
            source_id,
            _value(row, "inventory_member_id"),
            _value(row, "archive_asset_id"),
            _value(row, "archive_relative_path"),
            _value(row, "outer_archive_member"),
            _value(row, "nested_archive_member"),
            _value(row, "hdf5_member_path"),
        )
        event = CanonicalEvent(
            event_id=event_id,
            experiment=_text(row, "experiment") or "UNKNOWN",
            run=_canonical_run(_value(row, "run")),
            modality=modality,
            timestamp_utc=timestamp,
            timestamp_status=status,  # type: ignore[arg-type]
            timestamp_source=source,
            timestamp_evidence=evidence,
            clock_domain=clock,
            timestamp_raw=raw,
            source_references=references,
        )
        _add_event(
            events,
            event_rows,
            event=event,
            source_table="hdf5_members",
            source_id=source_id,
            source=row,
        )


def _sensor_role_events(
    sensors: pd.DataFrame,
    *,
    events: list[CanonicalEvent],
    event_rows: list[dict[str, Any]],
) -> None:
    role_map = {
        "condition_indicator": "condition_indicator",
        "operating_context": "operating_context",
        "oil": "oil",
        "environment": "environment",
    }
    for input_index, row in enumerate(sensors.to_dict("records")):
        role = _text(row, "channel_role")
        modality = role_map.get(role or "")
        if modality is None or _text(row, "error") is not None:
            continue
        source_id = _source_id(
            row,
            preferred="sensor_id",
            namespace="alignment_source",
            identity={
                "table": "sensor_profile",
                "member": _text(row, "hdf5_member_id"),
                "path": _text(row, "hdf5_path"),
                "row": input_index,
            },
        )
        event_id = deterministic_id(
            "canonical_event", {"modality": modality, "source_id": source_id}
        )
        timestamp, status, source, evidence, clock, raw = _sensor_timestamp(
            row, source_table="sensor_profile"
        )
        references = _references(
            source_id,
            _value(row, "contract_sensor_id"),
            _value(row, "hdf5_member_id"),
            _value(row, "inventory_member_id"),
            _value(row, "archive_asset_id"),
            _value(row, "archive_relative_path"),
            _value(row, "outer_archive_member"),
            _value(row, "nested_archive_member"),
            _value(row, "hdf5_member_path"),
            _value(row, "hdf5_path"),
        )
        event = CanonicalEvent(
            event_id=event_id,
            experiment=_text(row, "experiment") or "UNKNOWN",
            run=_canonical_run(_value(row, "run")),
            modality=modality,
            timestamp_utc=timestamp,
            timestamp_status=status,  # type: ignore[arg-type]
            timestamp_source=source,
            timestamp_evidence=evidence,
            clock_domain=clock,
            timestamp_raw=raw,
            source_references=references,
        )
        _add_event(
            events,
            event_rows,
            event=event,
            source_table="sensor_profile",
            source_id=source_id,
            source=row,
        )


def _image_events(
    images: pd.DataFrame,
    *,
    events: list[CanonicalEvent],
    event_rows: list[dict[str, Any]],
) -> None:
    for input_index, row in enumerate(images.to_dict("records")):
        source_id = _source_id(
            row,
            preferred="image_id",
            namespace="alignment_source",
            identity={
                "table": "image_profile",
                "source": _text(row, "source_relative_path"),
                "row": input_index,
            },
        )
        stage = _text(row, "inspection_stage") or "unclassified"
        run = _canonical_run(_value(row, "run"), stage=stage)
        event_id = deterministic_id(
            "canonical_event", {"modality": "photograph", "source_id": source_id}
        )
        timestamp, status, source, evidence, clock, raw, local_naive = _image_timestamp(
            row
        )
        references = _references(
            source_id,
            _value(row, "contract_image_id"),
            _value(row, "source_member_id"),
            _value(row, "archive_asset_id"),
            _value(row, "source_relative_path"),
            _value(row, "archive_relative_path"),
            _value(row, "outer_archive_member"),
            _value(row, "nested_archive_member"),
            _value(row, "inspection_id"),
        )
        event = CanonicalEvent(
            event_id=event_id,
            experiment=_text(row, "experiment") or "UNKNOWN",
            run=run,
            modality="photograph",
            timestamp_utc=timestamp,
            timestamp_status=status,  # type: ignore[arg-type]
            timestamp_source=source,
            timestamp_evidence=evidence,
            clock_domain=clock,
            timestamp_raw=raw,
            source_references=references,
        )
        _add_event(
            events,
            event_rows,
            event=event,
            source_table="image_profile",
            source_id=source_id,
            source=row,
            timestamp_local_naive=local_naive,
        )


def _inspection_timestamp(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[
    datetime | None,
    str,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
]:
    parsed = [(_image_timestamp(row), row) for row in rows]
    verified = [item for item in parsed if item[0][1] == "verified_utc"]
    if verified:
        chosen, _ = min(
            verified,
            key=lambda item: item[0][0] or datetime.max.replace(tzinfo=timezone.utc),
        )
        timestamp = chosen[0]
        assert timestamp is not None
        return (
            timestamp,
            "verified_utc",
            "derived:earliest_verified_photograph_timestamp",
            "Earliest verified photograph timestamp in this archive-level inspection",
            HDF5_EXPLICIT_UTC_CLOCK,
            chosen[5],
            None,
        )
    local = [item for item in parsed if item[0][1] == "timezone_unknown"]
    if local:
        chosen, _ = min(local, key=lambda item: item[0][6] or item[0][5] or "")
        return (
            None,
            "timezone_unknown",
            "derived:earliest_local_naive_photograph_timestamp",
            "Earliest local-naive photograph token; timezone remains unknown",
            None,
            chosen[5] or chosen[6],
            chosen[6],
        )
    return None, "missing", None, None, None, None, None


def _inspection_events(
    images: pd.DataFrame,
    *,
    events: list[CanonicalEvent],
    event_rows: list[dict[str, Any]],
) -> None:
    groups: dict[tuple[str, int | str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in images.to_dict("records"):
        experiment = _text(row, "experiment") or "UNKNOWN"
        stage = _text(row, "inspection_stage") or "unclassified"
        run = _canonical_run(_value(row, "run"), stage=stage)
        inspection_id = _text(row, "inspection_id") or deterministic_id(
            "archive_inspection",
            {
                "experiment": experiment,
                "run": run,
                "archive": _text(row, "archive_relative_path"),
            },
        )
        groups[(experiment, run, inspection_id)].append(row)
    for experiment, run, inspection_id in sorted(
        groups, key=lambda key: (key[0], str(key[1]), key[2])
    ):
        group = groups[(experiment, run, inspection_id)]
        first = group[0]
        timestamp, status, source, evidence, clock, raw, local_naive = (
            _inspection_timestamp(group)
        )
        event_id = deterministic_id(
            "canonical_event",
            {"modality": "archive_inspection", "inspection_id": inspection_id},
        )
        references = _references(
            inspection_id,
            _value(first, "archive_asset_id"),
            _value(first, "archive_relative_path"),
            *(_value(row, "image_id") for row in group),
            *(_value(row, "source_relative_path") for row in group),
        )
        event = CanonicalEvent(
            event_id=event_id,
            experiment=experiment,
            run=run,
            modality="archive_inspection",
            timestamp_utc=timestamp,
            timestamp_status=status,  # type: ignore[arg-type]
            timestamp_source=source,
            timestamp_evidence=evidence,
            clock_domain=clock,
            timestamp_raw=raw,
            source_references=references,
        )
        source_row = dict(first)
        source_row["inspection_id"] = inspection_id
        _add_event(
            events,
            event_rows,
            event=event,
            source_table="image_profile:archive_inspection",
            source_id=inspection_id,
            source=source_row,
            timestamp_local_naive=local_naive,
        )


def build_canonical_events(
    hdf5_members: ProfileTable,
    sensor_profile: ProfileTable,
    image_profile: ProfileTable,
) -> tuple[list[CanonicalEvent], list[dict[str, Any]]]:
    """Build source-traceable events strictly from generated profile evidence."""

    members = load_profile_table(hdf5_members, name="hdf5_members")
    sensors = load_profile_table(sensor_profile, name="sensor_profile")
    images = load_profile_table(image_profile, name="image_profile")
    events: list[CanonicalEvent] = []
    rows: list[dict[str, Any]] = []
    _member_events(members, events=events, event_rows=rows)
    _sensor_role_events(sensors, events=events, event_rows=rows)
    _image_events(images, events=events, event_rows=rows)
    _inspection_events(images, events=events, event_rows=rows)
    identifiers = [event.event_id for event in events]
    duplicates = sorted(
        identifier for identifier, count in Counter(identifiers).items() if count > 1
    )
    if duplicates:
        raise ValueError(
            "generated canonical event IDs are not unique: " + ", ".join(duplicates)
        )
    return events, rows


def _timeline_rows(
    audit: TimelineAuditResult, options: AlignmentPipelineOptions
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in audit.groups:
        cadences = tuple(float(value) for value in group.observed_cadence_seconds)
        six_hour_count = sum(
            abs(value - options.six_hour_reference_seconds)
            <= options.six_hour_tolerance_seconds
            for value in cadences
        )
        rows.append(
            {
                "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
                "experiment": group.experiment,
                "run": group.run,
                "modality": group.modality,
                "event_count": group.event_count,
                "verified_timestamp_count": group.verified_timestamp_count,
                "missing_timestamp_count": group.missing_timestamp_count,
                "noncomparable_timestamp_count": (group.noncomparable_timestamp_count),
                "earliest_timestamp_utc": group.earliest_timestamp_utc,
                "latest_timestamp_utc": group.latest_timestamp_utc,
                "clock_domains_json": group.clock_domains,
                "duplicate_timestamp_group_count": (
                    group.duplicate_timestamp_group_count
                ),
                "duplicate_timestamp_event_count": (
                    group.duplicate_timestamp_event_count
                ),
                "duplicate_timestamp_event_ids_json": (
                    group.duplicate_timestamp_event_ids
                ),
                "non_monotonic_transition_count": (
                    group.non_monotonic_transition_count
                ),
                "non_monotonic_transitions_json": (group.non_monotonic_transitions),
                "observed_cadence_seconds_json": cadences,
                "cadence_seconds_min": group.cadence_seconds_min,
                "cadence_seconds_median": group.cadence_seconds_median,
                "cadence_seconds_max": group.cadence_seconds_max,
                "ordering_basis": group.ordering_basis,
                "six_hour_reference_seconds": options.six_hour_reference_seconds,
                "six_hour_tolerance_seconds": options.six_hour_tolerance_seconds,
                "observed_interval_count": len(cadences),
                "observed_six_hour_interval_count": six_hour_count,
                "observed_six_hour_spacing": (
                    bool(six_hour_count) if cadences else None
                ),
                "six_hour_evidence_basis": (
                    "observed_adjacent_verified_timestamps_only_not_target_horizon"
                ),
                "expected_cadence_seconds": None,
                "coverage_gap_count": None,
                "coverage_gap_status": ("not_inferable_without_expected_cadence"),
            }
        )
    return rows


def _alignment_rows(
    events: Sequence[CanonicalEvent], options: AlignmentPipelineOptions
) -> tuple[list[AlignmentAuditResult], list[dict[str, Any]]]:
    audits: list[AlignmentAuditResult] = []
    rows: list[dict[str, Any]] = []
    for candidate_modality in _ALIGNMENT_CANDIDATE_MODALITIES:
        alignment_options = AlignmentOptions(
            anchor_modality="photograph",
            candidate_modality=candidate_modality,
            tolerance_seconds=options.tolerance_seconds,
            direction=options.direction,
        )
        audit = align_event_modalities(events, alignment_options)
        audits.append(audit)
        for alignment in audit.alignments:
            row = asdict(alignment)
            row.pop("schema_version", None)
            rows.append(
                {
                    "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
                    **row,
                    "within_tolerance_candidate_ids_json": row.pop(
                        "within_tolerance_candidate_ids"
                    ),
                    "nearest_candidate_event_ids_json": row.pop(
                        "nearest_candidate_event_ids"
                    ),
                    "candidate_anchor_counts_json": row.pop("candidate_anchor_counts"),
                    "tolerance_seconds": options.tolerance_seconds,
                    "direction": options.direction,
                }
            )
    rows.sort(
        key=lambda row: (
            str(row["experiment"]),
            str(row["run"]),
            str(row["anchor_event_id"]),
            str(row["candidate_modality"]),
        )
    )
    return audits, rows


def _sample_definition_rows() -> list[dict[str, Any]]:
    definitions = (
        (
            "one_image",
            "one image",
            "single photograph",
            ("experiment", "run_or_stage", "image_id"),
            "verified comparable image acquisition timestamp",
            "optional aligned sensor context",
            "one readable image",
            "resolved scalar target at an evidenced time",
            "Preserves a direct image-to-source relationship.",
            "Images within one inspection are correlated; image UTC is currently unavailable.",
        ),
        (
            "one_tooth_inspection",
            "one tooth inspection",
            "all views of one tooth in one inspection",
            ("experiment", "run_or_stage", "inspection_id", "tooth_id"),
            "verified inspection or member acquisition timestamp",
            "optional aligned sensor context",
            "one or more evidenced views of the same tooth",
            "resolved scalar target with tooth/system scope specified",
            "Keeps multiple views of one tooth together.",
            "No verified rule currently proves view simultaneity or a tooth-level target.",
        ),
        (
            "all_images_in_inspection",
            "all images from an inspection",
            "archive-level photograph inspection",
            ("experiment", "run_or_stage", "inspection_id"),
            "verified inspection boundary and clock",
            "optional aligned sensor context",
            "all readable images in one source inspection archive",
            "resolved inspection-level scalar target",
            "Retains the complete visual inspection context.",
            "Inspection archives are groupings, not proven instantaneous acquisition sessions.",
        ),
        (
            "one_hf_recording",
            "one sensor recording",
            "one high-frequency HDF5 recording",
            ("experiment", "run", "hdf5_member_id"),
            "verified recording start/end timestamps",
            "the recording itself",
            "none required",
            "resolved scalar target and temporal relationship",
            "Preserves source recording boundaries and high-frequency channels.",
            "A target time, input window, and aggregation rule remain undefined.",
        ),
        (
            "one_lf_observation",
            "one low-frequency observation",
            "one timestamped low-frequency HDF5 member",
            ("experiment", "run", "hdf5_member_id"),
            "verified member timestamp",
            "optional contemporaneous or historical HF input",
            "none required",
            "resolved scalar target distinct from input context",
            "Retains the observed low-frequency cadence without interpolation.",
            "Member cadence is evidence only and does not identify a target variable.",
        ),
        (
            "one_condition_indicator_observation",
            "one condition-indicator observation",
            "one profiled CI dataset at an evidenced time",
            ("experiment", "run", "sensor_id"),
            "verified dataset/member timestamp",
            "optional historical sensor input",
            "none required",
            "decision whether CI is an input, target, or diagnostic only",
            "Maintains the exact CI source dataset and time evidence.",
            "Treating an existing CI as the prediction target could create leakage or a tautology.",
        ),
        (
            "history_to_inspection",
            "historical window ending at an inspection",
            "past-only sensor history plus an inspection anchor",
            ("experiment", "run_or_stage", "inspection_id"),
            "verified comparable inspection and sensor clocks",
            "window duration and channels must be specified",
            "inspection images at the window endpoint",
            "resolved target time relative to the inspection",
            "Could support leakage-controlled multimodal context.",
            "Camera timezone/clock comparability, window length, and target semantics are unresolved.",
        ),
        (
            "history_to_target",
            "historical window ending at a target time",
            "past-only sensor/image history before a scalar observation",
            ("experiment", "run", "candidate_target_id"),
            "verified target and input clocks",
            "window duration and channels must be specified",
            "optional images strictly before the target cutoff",
            "resolved scalar name, unit, scope, timestamp, and six-hour meaning",
            "Would make leakage controls and prediction timing explicit.",
            "No candidate scalar observations or verified six-hour interpretation currently exist.",
        ),
    )
    rows: list[dict[str, Any]] = []
    for (
        key,
        sample_unit,
        input_unit,
        grouping_keys,
        anchor_requirement,
        history_requirement,
        image_requirement,
        target_requirement,
        advantages,
        limitations,
    ) in definitions:
        rows.append(
            {
                "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
                "option_id": deterministic_id(
                    "sample_definition_option",
                    {
                        "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
                        "key": key,
                    },
                ),
                "sample_unit": sample_unit,
                "input_unit": input_unit,
                "grouping_keys_json": grouping_keys,
                "anchor_time_requirement": anchor_requirement,
                "sensor_history_requirement": history_requirement,
                "image_requirement": image_requirement,
                "target_requirement": target_requirement,
                "advantages": advantages,
                "limitations": limitations,
                "status": "BLOCKED_REQUIRES_RESEARCH_DECISION",
                "decision": "not_selected",
            }
        )
    return rows


def _trace_rows(
    event_rows: Sequence[Mapping[str, Any]],
    alignment_rows: Sequence[Mapping[str, Any]],
    *,
    maximum: int,
) -> list[dict[str, Any]]:
    alignments_by_anchor: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in alignment_rows:
        alignments_by_anchor[str(row["anchor_event_id"])].append(row)
    candidates = sorted(
        (
            row
            for row in event_rows
            if row["modality"] == "photograph"
            and row["experiment"] == "EXP-A"
            and row["run"] == 1
        ),
        key=lambda row: (
            str(row.get("source_relative_path") or ""),
            str(row["event_id"]),
        ),
    )[:maximum]
    traces: list[dict[str, Any]] = []
    for image in candidates:
        event_id = str(image["event_id"])
        related = sorted(
            alignments_by_anchor.get(event_id, []),
            key=lambda row: str(row["candidate_modality"]),
        )
        status = str(image["timestamp_status"])
        if status == "timezone_unknown":
            clock_blocker = "image_local_naive_timestamp_has_no_evidenced_timezone"
        elif status == "missing":
            clock_blocker = "image_acquisition_timestamp_missing"
        elif status != "verified_utc":
            clock_blocker = "image_timestamp_not_verified_for_alignment"
        elif any(row["selected_candidate_event_id"] is not None for row in related):
            clock_blocker = "none_for_at_least_one_candidate_modality"
        else:
            clock_blocker = "no_verified_comparable_sensor_candidate_within_tolerance"
        trace_id = deterministic_id(
            "candidate_sample_trace",
            {
                "image_event_id": event_id,
                "status": "BLOCKED",
                "target_status": "unresolved",
            },
        )
        traces.append(
            {
                "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
                "trace_id": trace_id,
                "status": "BLOCKED",
                "experiment": image["experiment"],
                "run": image["run"],
                "image_event_id": event_id,
                "image_id": image.get("image_id"),
                "image_source_relative_path": image.get("source_relative_path"),
                "inspection_id": image.get("inspection_id"),
                "tooth_id": image.get("tooth_id"),
                "image_timestamp_status": status,
                "image_timestamp_raw": image.get("timestamp_raw"),
                "selected_sensor_event_id": None,
                "signed_delta_seconds": None,
                "absolute_delta_seconds": None,
                "target_event_id": None,
                "target_value": None,
                "target_unit": None,
                "clock_blocker": clock_blocker,
                "target_blocker": (
                    "candidate_scalar_target_name_value_unit_timestamp_and_"
                    "six_hour_semantics_unresolved"
                ),
                "candidate_alignment_ids_json": tuple(
                    str(row["alignment_id"]) for row in related
                ),
                "source_references_json": image["source_references_json"],
            }
        )
    return traces


def build_alignment_pipeline(
    hdf5_members: ProfileTable,
    sensor_profile: ProfileTable,
    image_profile: ProfileTable,
    *,
    options: AlignmentPipelineOptions | None = None,
) -> AlignmentPipelineResult:
    """Construct the complete D1.4 audit without reading any raw payload."""

    active_options = options or AlignmentPipelineOptions()
    members = load_profile_table(hdf5_members, name="hdf5_members")
    sensors = load_profile_table(sensor_profile, name="sensor_profile")
    images = load_profile_table(image_profile, name="image_profile")
    events, event_rows = build_canonical_events(members, sensors, images)
    timeline_audit = audit_timelines(events)
    timeline_rows = _timeline_rows(timeline_audit, active_options)
    alignment_audits, alignment_rows = _alignment_rows(events, active_options)
    sample_rows = _sample_definition_rows()
    trace_rows = _trace_rows(
        event_rows, alignment_rows, maximum=active_options.trace_example_count
    )
    return AlignmentPipelineResult(
        options=active_options,
        events=events,
        event_rows=event_rows,
        timeline_audit=timeline_audit,
        timeline_rows=timeline_rows,
        alignment_audits=alignment_audits,
        alignment_rows=alignment_rows,
        candidate_target_rows=[],
        sample_definition_rows=sample_rows,
        trace_rows=trace_rows,
        input_row_counts={
            "hdf5_members": len(members),
            "sensor_profile": len(sensors),
            "image_profile": len(images),
        },
    )


# Descriptive aliases keep call sites readable without changing semantics.
build_alignment_audit = build_alignment_pipeline
run_alignment_pipeline = build_alignment_pipeline


def _jsonable(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, (datetime, pd.Timestamp)):
        parsed = value.to_pydatetime() if isinstance(value, pd.Timestamp) else value
        return parsed.isoformat()
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if _is_missing(value):
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _serialize_cell(column: str, value: object) -> object:
    normalized = _jsonable(value)
    if column == "run" and normalized is not None:
        return str(normalized)
    if column.endswith("_json"):
        return json.dumps(
            normalized if normalized is not None else [],
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=isinstance(normalized, Mapping),
        )
    if isinstance(normalized, (list, dict)):
        return json.dumps(
            normalized,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=isinstance(normalized, dict),
        )
    return normalized


def _serialized_rows(
    rows: Sequence[Mapping[str, Any]], columns: Sequence[str]
) -> list[dict[str, object]]:
    return [
        {column: _serialize_cell(column, row.get(column)) for column in columns}
        for row in rows
    ]


def _write_table_pair(
    csv_path: Path,
    parquet_path: Path,
    rows: Sequence[Mapping[str, Any]],
    columns: Sequence[str],
) -> None:
    serialized = _serialized_rows(rows, columns)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(serialized)
    pd.DataFrame(serialized, columns=columns).to_parquet(parquet_path, index=False)


def _sample_options_markdown(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# Candidate sample-definition options",
        "",
        "Status: **no option selected**. These are research-design alternatives, not model samples.",
        "",
        "| Sample unit | Input unit | Anchor-time requirement | Status |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['sample_unit']} | {row['input_unit']} | "
            f"{row['anchor_time_requirement']} | {row['status']} |"
        )
    lines.extend(
        [
            "",
            "## Decision boundaries",
            "",
            "- No `SampleRecord` or training manifest is created by this audit.",
            "- Candidate scalar target name, physical meaning, unit, timestamp, and scope remain unresolved.",
            "- Six-hour proximity is reported only when observed between adjacent verified timestamps; it is not interpreted as an input window or prediction horizon.",
            "- Past-only alignment can be audited, but no interpolation, aggregation, or final sample choice is performed.",
        ]
    )
    return "\n".join(lines) + "\n"


def _summary_markdown(summary: Mapping[str, Any]) -> str:
    return (
        "\n".join(
            [
                "# Cross-modal timeline and candidate-alignment audit",
                "",
                f"Status: **{summary['status']}**",
                "",
                "## Evidence coverage",
                "",
                f"- Canonical events: {summary['event_count']}",
                f"- Timeline groups: {summary['timeline_group_count']}",
                f"- Image-to-sensor/scalar audit rows: {summary['alignment_row_count']}",
                f"- Verified comparable image-to-sensor joins: {summary['comparable_image_sensor_join_count']}",
                f"- Images with verified UTC timestamps: {summary['image_timestamp_status_counts'].get('verified_utc', 0)}",
                f"- Images with local-naive timezone-unknown timestamps: {summary['image_timestamp_status_counts'].get('timezone_unknown', 0)}",
                f"- Images with missing timestamps: {summary['image_timestamp_status_counts'].get('missing', 0)}",
                f"- Candidate scalar targets: {summary['candidate_target_count']}",
                f"- Blocked raw-source traces: {summary['blocked_trace_example_count']}",
                "",
                "## Six-hour cadence evidence",
                "",
                f"- Reference interval for observed comparison: {summary['six_hour_reference_seconds']} seconds",
                f"- Configured comparison tolerance: {summary['six_hour_tolerance_seconds']} seconds",
                f"- Timeline groups with at least one observed matching interval: {summary['timeline_groups_with_observed_six_hour_spacing']}",
                "- Interpretation: observed adjacent-timestamp cadence evidence only; no target-horizon claim.",
                "- Coverage-gap count: not inferable because no expected cadence contract is established.",
                "",
                "## Scientific blockers",
                "",
                "- Image timestamps may be local-naive or missing and cannot be joined to UTC sensor time without evidenced clock comparability.",
                "- The candidate scalar target name, physical meaning, unit, scope, and timestamp are unresolved.",
                "- The six-hour statement has not been established as cadence, history length, or forecast horizon.",
                "",
                "No interpolation, target synthesis, model sample, or damage/health label was produced.",
            ]
        )
        + "\n"
    )


def _write_coverage_figure(path: Path, events: Sequence[CanonicalEvent]) -> None:
    import matplotlib.pyplot as plt

    modalities = sorted({event.modality for event in events})
    total = Counter(event.modality for event in events)
    verified = Counter(
        event.modality for event in events if event.has_verified_timestamp
    )
    if not modalities:
        modalities = ["no_events"]
    positions = np.arange(len(modalities))
    figure, axis = plt.subplots(figsize=(10, max(4, len(modalities) * 0.45)))
    axis.barh(
        positions + 0.18,
        [total.get(modality, 0) for modality in modalities],
        height=0.34,
        label="all events",
    )
    axis.barh(
        positions - 0.18,
        [verified.get(modality, 0) for modality in modalities],
        height=0.34,
        label="verified UTC",
    )
    axis.set_yticks(positions, modalities)
    axis.set_xlabel("Event count")
    axis.set_title("Canonical event and verified-timestamp coverage")
    axis.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def write_alignment_run(
    result: AlignmentPipelineResult,
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
    """Write versioned D1.4 artifacts with stable schemas and provenance."""

    if not isinstance(result, AlignmentPipelineResult):
        raise TypeError("result must be an AlignmentPipelineResult")
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
    tables = (
        (
            "canonical_events",
            result.event_rows,
            EVENT_COLUMNS,
            "canonical_events",
        ),
        (
            "timeline_audit",
            result.timeline_rows,
            TIMELINE_COLUMNS,
            "timeline_audit",
        ),
        (
            "alignment_audit",
            result.alignment_rows,
            ALIGNMENT_COLUMNS,
            "alignment_audit",
        ),
        (
            "candidate_targets",
            result.candidate_target_rows,
            CANDIDATE_TARGET_COLUMNS,
            "candidate_targets_unresolved",
        ),
        (
            "sample_definition_options",
            result.sample_definition_rows,
            SAMPLE_OPTION_COLUMNS,
            "sample_definition_options",
        ),
        (
            "candidate_sample_traces",
            result.trace_rows,
            TRACE_COLUMNS,
            "candidate_sample_traces_blocked",
        ),
    )
    for stem, rows, columns, role in tables:
        csv_path = run.run_directory / f"tables/{stem}.csv"
        parquet_path = run.run_directory / f"tables/{stem}.parquet"
        _write_table_pair(csv_path, parquet_path, rows, columns)
        artifacts.extend(
            [
                run.artifact(csv_path, role=f"{role}_csv"),
                run.artifact(parquet_path, role=f"{role}_parquet"),
            ]
        )

    options_path = run.run_directory / "reports/sample_definition_options.md"
    options_path.write_text(
        _sample_options_markdown(result.sample_definition_rows), encoding="utf-8"
    )
    summary = result.summary()
    summary_json = run.run_directory / "reports/alignment_summary.json"
    summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary_md = run.run_directory / "reports/alignment_summary.md"
    summary_md.write_text(_summary_markdown(summary), encoding="utf-8")
    coverage_figure = run.run_directory / "figures/alignment_coverage.png"
    _write_coverage_figure(coverage_figure, result.events)
    for path, role in (
        (options_path, "sample_definition_options_markdown"),
        (summary_json, "alignment_summary_json"),
        (summary_md, "alignment_summary_markdown"),
        (coverage_figure, "alignment_coverage_figure"),
    ):
        artifacts.append(run.artifact(path, role=role))

    provenance_path = run.write_provenance(artifacts)
    with_provenance = [
        *artifacts,
        run.artifact(provenance_path, role="run_provenance"),
    ]
    run.write_output_manifest(with_provenance)
    return with_provenance


__all__ = [
    "ALIGNMENT_PIPELINE_SCHEMA_VERSION",
    "ALIGNMENT_SCHEMA_VERSION",
    "HDF5_EXPLICIT_UTC_CLOCK",
    "ALIGNMENT_COLUMNS",
    "CANDIDATE_TARGET_COLUMNS",
    "EVENT_COLUMNS",
    "SAMPLE_OPTION_COLUMNS",
    "TIMELINE_COLUMNS",
    "TRACE_COLUMNS",
    "AlignmentPipelineOptions",
    "AlignmentPipelineResult",
    "build_alignment_audit",
    "build_alignment_pipeline",
    "build_canonical_events",
    "load_profile_table",
    "run_alignment_pipeline",
    "write_alignment_run",
]
