"""Dataset-neutral, evidence-gated timeline and nearest-alignment audits.

This module deliberately produces audit records, not model samples.  In
particular, it has no dependency on ``SampleRecord`` or on target semantics.
Only events whose timestamps have a verified UTC basis and the same explicit
clock-comparability domain can participate in an alignment.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import math
from statistics import median
from typing import Any, Literal

from ..data_contracts import deterministic_id

ALIGNMENT_SCHEMA_VERSION = "1.0.0"

TimestampStatus = Literal["verified_utc", "timezone_unknown", "missing", "unverified"]
MatchDirection = Literal["nearest", "past_only"]
MatchStatus = Literal[
    "matched",
    "ambiguous",
    "no_match",
    "missing_modality",
    "anchor_timestamp_unusable",
    "candidate_timestamp_unusable",
    "incomparable_clock",
]
MatchKind = Literal["exact", "nearest", "none"]

_TIMESTAMP_STATUSES = {
    "verified_utc",
    "timezone_unknown",
    "missing",
    "unverified",
}


def _require_text(field: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{field} must be a non-empty stripped string")
    return value


def _run_sort_key(value: int | str) -> tuple[str, str]:
    return type(value).__name__, str(value)


@dataclass(frozen=True, slots=True)
class CanonicalEvent:
    """One traceable event on a potentially alignable timeline.

    ``clock_domain`` is a comparability claim, not merely a device name. Two
    events are considered temporally comparable only when both have
    ``timestamp_status='verified_utc'`` and the same non-empty clock domain.
    Local-naive timestamps belong in ``timestamp_raw`` with
    ``timestamp_status='timezone_unknown'`` and no ``timestamp_utc`` value.
    """

    event_id: str
    experiment: str
    run: int | str
    modality: str
    timestamp_utc: datetime | None
    timestamp_status: TimestampStatus
    timestamp_source: str | None = None
    timestamp_evidence: str | None = None
    clock_domain: str | None = None
    timestamp_raw: str | None = None
    source_references: tuple[str, ...] = ()
    sequence_index: int | None = None
    schema_version: str = ALIGNMENT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text("event_id", self.event_id)
        _require_text("experiment", self.experiment)
        _require_text("modality", self.modality)
        if isinstance(self.run, bool) or not isinstance(self.run, (int, str)):
            raise ValueError("run must be an integer or non-empty string")
        if isinstance(self.run, str):
            _require_text("run", self.run)
        if self.timestamp_status not in _TIMESTAMP_STATUSES:
            raise ValueError(
                "timestamp_status must be verified_utc, timezone_unknown, "
                "missing, or unverified"
            )
        if self.timestamp_utc is not None:
            if not isinstance(self.timestamp_utc, datetime):
                raise ValueError("timestamp_utc must be a datetime or null")
            if (
                self.timestamp_utc.tzinfo is None
                or self.timestamp_utc.utcoffset() is None
            ):
                raise ValueError("timestamp_utc must carry an explicit timezone")
            object.__setattr__(
                self,
                "timestamp_utc",
                self.timestamp_utc.astimezone(timezone.utc),
            )
        if self.timestamp_status == "verified_utc":
            if self.timestamp_utc is None:
                raise ValueError("verified_utc requires timestamp_utc")
            _require_text("clock_domain", self.clock_domain)
            _require_text("timestamp_evidence", self.timestamp_evidence)
        elif self.timestamp_status in {"timezone_unknown", "missing"}:
            if self.timestamp_utc is not None:
                raise ValueError(
                    f"{self.timestamp_status} must not provide timestamp_utc"
                )
        if self.timestamp_status == "timezone_unknown":
            _require_text("timestamp_raw", self.timestamp_raw)
        for field_name, value in (
            ("timestamp_source", self.timestamp_source),
            ("timestamp_evidence", self.timestamp_evidence),
            ("clock_domain", self.clock_domain),
            ("timestamp_raw", self.timestamp_raw),
        ):
            if value is not None:
                _require_text(field_name, value)
        references = tuple(self.source_references)
        for reference in references:
            _require_text("source_references item", reference)
        if len(set(references)) != len(references):
            raise ValueError("source_references must not contain duplicates")
        object.__setattr__(self, "source_references", references)
        if self.sequence_index is not None and (
            isinstance(self.sequence_index, bool)
            or not isinstance(self.sequence_index, int)
            or self.sequence_index < 0
        ):
            raise ValueError("sequence_index must be a non-negative integer or null")
        if self.schema_version != ALIGNMENT_SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {ALIGNMENT_SCHEMA_VERSION!r}")

    @property
    def has_verified_timestamp(self) -> bool:
        """Whether the event carries an evidence-backed UTC timestamp."""

        return (
            self.timestamp_status == "verified_utc" and self.timestamp_utc is not None
        )


def timestamps_are_comparable(left: CanonicalEvent, right: CanonicalEvent) -> bool:
    """Return whether two events may be compared on the same verified clock."""

    return (
        left.has_verified_timestamp
        and right.has_verified_timestamp
        and left.clock_domain == right.clock_domain
    )


@dataclass(frozen=True, slots=True)
class TimelineGroupAudit:
    """Timestamp coverage and ordering diagnostics for one event scope."""

    experiment: str
    run: int | str
    modality: str
    event_count: int
    verified_timestamp_count: int
    missing_timestamp_count: int
    noncomparable_timestamp_count: int
    earliest_timestamp_utc: datetime | None
    latest_timestamp_utc: datetime | None
    clock_domains: tuple[str, ...]
    duplicate_timestamp_group_count: int
    duplicate_timestamp_event_count: int
    duplicate_timestamp_event_ids: tuple[tuple[str, ...], ...]
    non_monotonic_transition_count: int
    non_monotonic_transitions: tuple[tuple[str, str, float], ...]
    observed_cadence_seconds: tuple[float, ...]
    cadence_seconds_min: float | None
    cadence_seconds_median: float | None
    cadence_seconds_max: float | None
    ordering_basis: Literal["sequence_index", "input_sequence"]
    schema_version: str = ALIGNMENT_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class TimelineAuditResult:
    """Complete deterministic timeline diagnostics."""

    groups: tuple[TimelineGroupAudit, ...]
    schema_version: str = ALIGNMENT_SCHEMA_VERSION

    def summary(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "group_count": len(self.groups),
            "event_count": sum(group.event_count for group in self.groups),
            "verified_timestamp_count": sum(
                group.verified_timestamp_count for group in self.groups
            ),
            "missing_timestamp_count": sum(
                group.missing_timestamp_count for group in self.groups
            ),
            "noncomparable_timestamp_count": sum(
                group.noncomparable_timestamp_count for group in self.groups
            ),
            "duplicate_timestamp_group_count": sum(
                group.duplicate_timestamp_group_count for group in self.groups
            ),
            "non_monotonic_transition_count": sum(
                group.non_monotonic_transition_count for group in self.groups
            ),
        }

    def as_rows(self) -> list[dict[str, Any]]:
        return [asdict(group) for group in self.groups]


def _validated_events(events: Sequence[CanonicalEvent]) -> list[CanonicalEvent]:
    values = list(events)
    if any(not isinstance(event, CanonicalEvent) for event in values):
        raise TypeError("events must contain only CanonicalEvent instances")
    identifiers = [event.event_id for event in values]
    duplicates = sorted(
        identifier for identifier, count in Counter(identifiers).items() if count > 1
    )
    if duplicates:
        raise ValueError("event_id values must be unique: " + ", ".join(duplicates))
    return values


def audit_timelines(events: Sequence[CanonicalEvent]) -> TimelineAuditResult:
    """Audit timestamp coverage, duplicates, cadence, and observed ordering.

    Duplicate and cadence calculations never combine different clock domains.
    Non-monotonic transitions use ``sequence_index`` when every event in the
    group supplies it; otherwise the caller-provided input order is retained
    and reported as such.
    """

    values = _validated_events(events)
    grouped: dict[tuple[str, int | str, str], list[tuple[int, CanonicalEvent]]] = (
        defaultdict(list)
    )
    for input_index, event in enumerate(values):
        grouped[(event.experiment, event.run, event.modality)].append(
            (input_index, event)
        )

    audits: list[TimelineGroupAudit] = []
    scope_keys = sorted(
        grouped,
        key=lambda key: (key[0], _run_sort_key(key[1]), key[2]),
    )
    for experiment, run, modality in scope_keys:
        indexed_events = grouped[(experiment, run, modality)]
        if indexed_events and all(
            event.sequence_index is not None for _, event in indexed_events
        ):
            ordered = sorted(
                indexed_events,
                key=lambda pair: (pair[1].sequence_index, pair[1].event_id),
            )
            ordering_basis: Literal["sequence_index", "input_sequence"] = (
                "sequence_index"
            )
        else:
            ordered = indexed_events
            ordering_basis = "input_sequence"

        verified = [
            event for _, event in indexed_events if event.has_verified_timestamp
        ]
        missing = [event for _, event in indexed_events if event.timestamp_utc is None]
        noncomparable = [
            event
            for _, event in indexed_events
            if event.timestamp_utc is not None and not event.has_verified_timestamp
        ]
        by_clock: dict[str, list[CanonicalEvent]] = defaultdict(list)
        for event in verified:
            # CanonicalEvent validation guarantees a non-null clock domain here.
            by_clock[str(event.clock_domain)].append(event)

        duplicate_groups: list[tuple[str, ...]] = []
        cadences: list[float] = []
        for domain in sorted(by_clock):
            clock_events = by_clock[domain]
            timestamp_groups: dict[datetime, list[str]] = defaultdict(list)
            for event in clock_events:
                assert event.timestamp_utc is not None
                timestamp_groups[event.timestamp_utc].append(event.event_id)
            duplicate_groups.extend(
                tuple(sorted(identifiers))
                for _, identifiers in sorted(timestamp_groups.items())
                if len(identifiers) > 1
            )
            chronological = sorted(
                clock_events,
                key=lambda event: (event.timestamp_utc, event.event_id),
            )
            cadences.extend(
                (current.timestamp_utc - previous.timestamp_utc).total_seconds()
                for previous, current in zip(chronological, chronological[1:])
                if previous.timestamp_utc is not None
                and current.timestamp_utc is not None
            )

        previous_by_clock: dict[str, CanonicalEvent] = {}
        transitions: list[tuple[str, str, float]] = []
        for _, event in ordered:
            if not event.has_verified_timestamp:
                continue
            domain = str(event.clock_domain)
            previous = previous_by_clock.get(domain)
            if (
                previous is not None
                and previous.timestamp_utc is not None
                and event.timestamp_utc is not None
                and event.timestamp_utc < previous.timestamp_utc
            ):
                transitions.append(
                    (
                        previous.event_id,
                        event.event_id,
                        (event.timestamp_utc - previous.timestamp_utc).total_seconds(),
                    )
                )
            previous_by_clock[domain] = event

        verified_timestamps = [
            event.timestamp_utc for event in verified if event.timestamp_utc is not None
        ]
        duplicate_groups.sort()
        audits.append(
            TimelineGroupAudit(
                experiment=experiment,
                run=run,
                modality=modality,
                event_count=len(indexed_events),
                verified_timestamp_count=len(verified),
                missing_timestamp_count=len(missing),
                noncomparable_timestamp_count=len(noncomparable),
                earliest_timestamp_utc=(
                    min(verified_timestamps) if verified_timestamps else None
                ),
                latest_timestamp_utc=(
                    max(verified_timestamps) if verified_timestamps else None
                ),
                clock_domains=tuple(sorted(by_clock)),
                duplicate_timestamp_group_count=len(duplicate_groups),
                duplicate_timestamp_event_count=sum(
                    len(group) for group in duplicate_groups
                ),
                duplicate_timestamp_event_ids=tuple(duplicate_groups),
                non_monotonic_transition_count=len(transitions),
                non_monotonic_transitions=tuple(transitions),
                observed_cadence_seconds=tuple(sorted(cadences)),
                cadence_seconds_min=min(cadences) if cadences else None,
                cadence_seconds_median=median(cadences) if cadences else None,
                cadence_seconds_max=max(cadences) if cadences else None,
                ordering_basis=ordering_basis,
            )
        )
    return TimelineAuditResult(groups=tuple(audits))


@dataclass(frozen=True, slots=True)
class AlignmentOptions:
    """Configuration for one directional modality-to-modality audit."""

    anchor_modality: str
    candidate_modality: str
    tolerance_seconds: float
    direction: MatchDirection = "nearest"

    def __post_init__(self) -> None:
        _require_text("anchor_modality", self.anchor_modality)
        _require_text("candidate_modality", self.candidate_modality)
        if (
            isinstance(self.tolerance_seconds, bool)
            or not isinstance(self.tolerance_seconds, (int, float))
            or not math.isfinite(float(self.tolerance_seconds))
            or float(self.tolerance_seconds) < 0
        ):
            raise ValueError("tolerance_seconds must be a finite non-negative number")
        object.__setattr__(self, "tolerance_seconds", float(self.tolerance_seconds))
        if self.direction not in {"nearest", "past_only"}:
            raise ValueError("direction must be nearest or past_only")


@dataclass(frozen=True, slots=True)
class NearestAlignment:
    """One anchor's transparent nearest-candidate audit record."""

    alignment_id: str
    anchor_event_id: str
    experiment: str
    run: int | str
    anchor_modality: str
    candidate_modality: str
    anchor_timestamp_utc: datetime | None
    selected_candidate_event_id: str | None
    selected_candidate_timestamp_utc: datetime | None
    signed_delta_seconds: float | None
    absolute_delta_seconds: float | None
    status: MatchStatus
    match_kind: MatchKind
    comparable_candidate_count: int
    within_tolerance_candidate_ids: tuple[str, ...]
    nearest_candidate_event_ids: tuple[str, ...]
    candidate_anchor_counts: tuple[tuple[str, int], ...]
    ambiguous: bool
    missing_match: bool
    missing_modality: bool
    anchor_timestamp_missing: bool
    candidate_timestamp_missing_count: int
    candidate_timestamp_unverified_count: int
    incomparable_clock_candidate_count: int
    future_candidate_rejected_count: int
    one_to_one: bool
    one_to_many: bool
    many_to_one: bool
    cardinality: Literal[
        "none", "one_to_one", "one_to_many", "many_to_one", "many_to_many"
    ]
    schema_version: str = ALIGNMENT_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class AlignmentAuditResult:
    """Deterministic nearest-alignment output plus aggregate diagnostics."""

    options: AlignmentOptions
    alignments: tuple[NearestAlignment, ...]
    schema_version: str = ALIGNMENT_SCHEMA_VERSION

    def summary(self) -> dict[str, Any]:
        statuses = Counter(row.status for row in self.alignments)
        kinds = Counter(row.match_kind for row in self.alignments)
        cardinalities = Counter(row.cardinality for row in self.alignments)
        return {
            "schema_version": self.schema_version,
            "anchor_modality": self.options.anchor_modality,
            "candidate_modality": self.options.candidate_modality,
            "tolerance_seconds": self.options.tolerance_seconds,
            "direction": self.options.direction,
            "anchor_count": len(self.alignments),
            "matched_anchor_count": sum(
                row.selected_candidate_event_id is not None for row in self.alignments
            ),
            "status_counts": dict(sorted(statuses.items())),
            "match_kind_counts": dict(sorted(kinds.items())),
            "cardinality_counts": dict(sorted(cardinalities.items())),
            "ambiguous_anchor_count": sum(row.ambiguous for row in self.alignments),
            "missing_match_count": sum(row.missing_match for row in self.alignments),
        }

    def as_rows(self) -> list[dict[str, Any]]:
        return [asdict(row) for row in self.alignments]


def _blank_alignment(
    anchor: CanonicalEvent,
    options: AlignmentOptions,
    *,
    status: MatchStatus,
    scope_candidates: Sequence[CanonicalEvent],
    comparable_count: int,
    incomparable_clock_count: int,
    future_rejected_count: int = 0,
) -> NearestAlignment:
    return NearestAlignment(
        alignment_id=deterministic_id(
            "alignment",
            {
                "schema_version": ALIGNMENT_SCHEMA_VERSION,
                "anchor_event_id": anchor.event_id,
                "anchor_modality": options.anchor_modality,
                "candidate_modality": options.candidate_modality,
                "tolerance_seconds": options.tolerance_seconds,
                "direction": options.direction,
            },
        ),
        anchor_event_id=anchor.event_id,
        experiment=anchor.experiment,
        run=anchor.run,
        anchor_modality=options.anchor_modality,
        candidate_modality=options.candidate_modality,
        anchor_timestamp_utc=anchor.timestamp_utc,
        selected_candidate_event_id=None,
        selected_candidate_timestamp_utc=None,
        signed_delta_seconds=None,
        absolute_delta_seconds=None,
        status=status,
        match_kind="none",
        comparable_candidate_count=comparable_count,
        within_tolerance_candidate_ids=(),
        nearest_candidate_event_ids=(),
        candidate_anchor_counts=(),
        ambiguous=False,
        missing_match=True,
        missing_modality=not scope_candidates,
        anchor_timestamp_missing=anchor.timestamp_utc is None,
        candidate_timestamp_missing_count=sum(
            candidate.timestamp_utc is None for candidate in scope_candidates
        ),
        candidate_timestamp_unverified_count=sum(
            candidate.timestamp_utc is not None and not candidate.has_verified_timestamp
            for candidate in scope_candidates
        ),
        incomparable_clock_candidate_count=incomparable_clock_count,
        future_candidate_rejected_count=future_rejected_count,
        one_to_one=False,
        one_to_many=False,
        many_to_one=False,
        cardinality="none",
    )


def align_event_modalities(
    events: Sequence[CanonicalEvent], options: AlignmentOptions
) -> AlignmentAuditResult:
    """Find deterministic nearest candidates without crossing scope or clocks.

    Candidate timestamps exactly on the tolerance boundary are included.
    ``past_only`` excludes every candidate later than its anchor, preventing a
    future event from becoming an input by nearest-neighbour convenience.
    Tied nearest candidates are all retained as ambiguity evidence; the
    lexicographically smallest ID is exposed only as a deterministic trace,
    never as proof that the ambiguity is resolved.
    """

    if not isinstance(options, AlignmentOptions):
        raise TypeError("options must be an AlignmentOptions instance")
    values = _validated_events(events)
    anchors = sorted(
        (event for event in values if event.modality == options.anchor_modality),
        key=lambda event: (
            event.experiment,
            _run_sort_key(event.run),
            event.event_id,
        ),
    )
    candidates_by_scope: dict[tuple[str, int | str], list[CanonicalEvent]] = (
        defaultdict(list)
    )
    for event in values:
        if event.modality == options.candidate_modality:
            candidates_by_scope[(event.experiment, event.run)].append(event)
    for candidates in candidates_by_scope.values():
        candidates.sort(key=lambda event: event.event_id)

    drafts: list[NearestAlignment] = []
    for anchor in anchors:
        scope_candidates = [
            candidate
            for candidate in candidates_by_scope.get(
                (anchor.experiment, anchor.run), []
            )
            if candidate.event_id != anchor.event_id
        ]
        verified_candidates = [
            candidate
            for candidate in scope_candidates
            if candidate.has_verified_timestamp
        ]
        comparable = [
            candidate
            for candidate in verified_candidates
            if timestamps_are_comparable(anchor, candidate)
        ]
        incomparable_clock_count = len(verified_candidates) - len(comparable)

        if not anchor.has_verified_timestamp:
            drafts.append(
                _blank_alignment(
                    anchor,
                    options,
                    status="anchor_timestamp_unusable",
                    scope_candidates=scope_candidates,
                    comparable_count=0,
                    incomparable_clock_count=incomparable_clock_count,
                )
            )
            continue
        if not scope_candidates:
            drafts.append(
                _blank_alignment(
                    anchor,
                    options,
                    status="missing_modality",
                    scope_candidates=scope_candidates,
                    comparable_count=0,
                    incomparable_clock_count=0,
                )
            )
            continue
        if not comparable:
            status: MatchStatus = (
                "incomparable_clock"
                if incomparable_clock_count
                else "candidate_timestamp_unusable"
            )
            drafts.append(
                _blank_alignment(
                    anchor,
                    options,
                    status=status,
                    scope_candidates=scope_candidates,
                    comparable_count=0,
                    incomparable_clock_count=incomparable_clock_count,
                )
            )
            continue

        assert anchor.timestamp_utc is not None
        signed_candidates: list[tuple[CanonicalEvent, float]] = []
        future_rejected = 0
        for candidate in comparable:
            assert candidate.timestamp_utc is not None
            delta = (candidate.timestamp_utc - anchor.timestamp_utc).total_seconds()
            if options.direction == "past_only" and delta > 0:
                future_rejected += 1
                continue
            signed_candidates.append((candidate, delta))
        within = [
            pair
            for pair in signed_candidates
            if abs(pair[1]) <= options.tolerance_seconds
        ]
        within.sort(key=lambda pair: (abs(pair[1]), pair[0].event_id))
        if not within:
            drafts.append(
                _blank_alignment(
                    anchor,
                    options,
                    status="no_match",
                    scope_candidates=scope_candidates,
                    comparable_count=len(comparable),
                    incomparable_clock_count=incomparable_clock_count,
                    future_rejected_count=future_rejected,
                )
            )
            continue

        nearest_distance = abs(within[0][1])
        nearest = [pair for pair in within if abs(pair[1]) == nearest_distance]
        nearest.sort(key=lambda pair: pair[0].event_id)
        selected, selected_delta = nearest[0]
        ambiguous = len(nearest) > 1
        drafts.append(
            NearestAlignment(
                alignment_id=deterministic_id(
                    "alignment",
                    {
                        "schema_version": ALIGNMENT_SCHEMA_VERSION,
                        "anchor_event_id": anchor.event_id,
                        "anchor_modality": options.anchor_modality,
                        "candidate_modality": options.candidate_modality,
                        "tolerance_seconds": options.tolerance_seconds,
                        "direction": options.direction,
                    },
                ),
                anchor_event_id=anchor.event_id,
                experiment=anchor.experiment,
                run=anchor.run,
                anchor_modality=options.anchor_modality,
                candidate_modality=options.candidate_modality,
                anchor_timestamp_utc=anchor.timestamp_utc,
                selected_candidate_event_id=selected.event_id,
                selected_candidate_timestamp_utc=selected.timestamp_utc,
                signed_delta_seconds=selected_delta,
                absolute_delta_seconds=abs(selected_delta),
                status="ambiguous" if ambiguous else "matched",
                match_kind="exact" if nearest_distance == 0 else "nearest",
                comparable_candidate_count=len(comparable),
                within_tolerance_candidate_ids=tuple(
                    candidate.event_id for candidate, _ in within
                ),
                nearest_candidate_event_ids=tuple(
                    candidate.event_id for candidate, _ in nearest
                ),
                candidate_anchor_counts=(),
                ambiguous=ambiguous,
                missing_match=False,
                missing_modality=False,
                anchor_timestamp_missing=False,
                candidate_timestamp_missing_count=sum(
                    candidate.timestamp_utc is None for candidate in scope_candidates
                ),
                candidate_timestamp_unverified_count=sum(
                    candidate.timestamp_utc is not None
                    and not candidate.has_verified_timestamp
                    for candidate in scope_candidates
                ),
                incomparable_clock_candidate_count=incomparable_clock_count,
                future_candidate_rejected_count=future_rejected,
                one_to_one=False,
                one_to_many=len(within) > 1,
                many_to_one=False,
                cardinality="none",
            )
        )

    reverse_nearest_counts: Counter[str] = Counter(
        candidate_id
        for row in drafts
        for candidate_id in row.nearest_candidate_event_ids
    )
    completed: list[NearestAlignment] = []
    for row in drafts:
        counts = tuple(
            (candidate_id, reverse_nearest_counts[candidate_id])
            for candidate_id in row.nearest_candidate_event_ids
        )
        many_to_one = any(count > 1 for _, count in counts)
        one_to_many = row.one_to_many
        if one_to_many and many_to_one:
            cardinality = "many_to_many"
        elif one_to_many:
            cardinality = "one_to_many"
        elif many_to_one:
            cardinality = "many_to_one"
        elif row.selected_candidate_event_id is not None:
            cardinality = "one_to_one"
        else:
            cardinality = "none"
        completed.append(
            replace(
                row,
                candidate_anchor_counts=counts,
                many_to_one=many_to_one,
                one_to_one=cardinality == "one_to_one",
                cardinality=cardinality,
            )
        )
    return AlignmentAuditResult(options=options, alignments=tuple(completed))


__all__ = [
    "ALIGNMENT_SCHEMA_VERSION",
    "AlignmentAuditResult",
    "AlignmentOptions",
    "CanonicalEvent",
    "NearestAlignment",
    "TimelineAuditResult",
    "TimelineGroupAudit",
    "align_event_modalities",
    "audit_timelines",
    "timestamps_are_comparable",
]
