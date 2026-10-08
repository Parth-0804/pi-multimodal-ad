from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from pi_multimodal_ad.profiling.alignment import (
    AlignmentOptions,
    CanonicalEvent,
    align_event_modalities,
    audit_timelines,
    timestamps_are_comparable,
)

UTC = timezone.utc
ORIGIN = datetime(2026, 1, 1, tzinfo=UTC)


def _event(
    event_id: str,
    seconds: float | None,
    *,
    modality: str = "image",
    experiment: str = "EXP-A",
    run: int = 1,
    status: str = "verified_utc",
    clock_domain: str | None = "shared_verified_utc",
    sequence_index: int | None = None,
) -> CanonicalEvent:
    timestamp = ORIGIN + timedelta(seconds=seconds) if seconds is not None else None
    timestamp_raw = "20260101_000000" if status == "timezone_unknown" else None
    return CanonicalEvent(
        event_id=event_id,
        experiment=experiment,
        run=run,
        modality=modality,
        timestamp_utc=timestamp,
        timestamp_status=status,  # type: ignore[arg-type]
        timestamp_source="synthetic_test",
        timestamp_evidence=(
            "synthetic explicit UTC clock" if status == "verified_utc" else None
        ),
        clock_domain=clock_domain if status == "verified_utc" else None,
        timestamp_raw=timestamp_raw,
        source_references=(f"synthetic/{event_id}",),
        sequence_index=sequence_index,
    )


def _rows_by_anchor(events: list[CanonicalEvent], **option_values: object):
    options = AlignmentOptions(
        anchor_modality="image",
        candidate_modality="sensor",
        tolerance_seconds=option_values.pop("tolerance_seconds", 5),
        **option_values,  # type: ignore[arg-type]
    )
    result = align_event_modalities(events, options)
    return result, {row.anchor_event_id: row for row in result.alignments}


def test_canonical_event_requires_evidence_backed_aware_utc() -> None:
    with pytest.raises(ValueError, match="explicit timezone"):
        CanonicalEvent(
            event_id="naive",
            experiment="EXP-A",
            run=1,
            modality="image",
            timestamp_utc=datetime(2026, 1, 1),
            timestamp_status="verified_utc",
            timestamp_evidence="synthetic",
            clock_domain="shared",
        )
    with pytest.raises(ValueError, match="clock_domain"):
        CanonicalEvent(
            event_id="unsupported-clock",
            experiment="EXP-A",
            run=1,
            modality="image",
            timestamp_utc=ORIGIN,
            timestamp_status="verified_utc",
            timestamp_evidence="synthetic",
        )

    local_camera = _event(
        "local-camera",
        None,
        status="timezone_unknown",
        clock_domain=None,
    )
    assert local_camera.timestamp_utc is None
    assert not local_camera.has_verified_timestamp


def test_comparability_requires_matching_verified_clock_domain() -> None:
    left = _event("left", 0)
    same_clock = _event("same-clock", 1, modality="sensor")
    other_clock = _event(
        "other-clock", 1, modality="sensor", clock_domain="unrelated_clock"
    )
    unknown = _event(
        "unknown",
        None,
        modality="sensor",
        status="timezone_unknown",
        clock_domain=None,
    )

    assert timestamps_are_comparable(left, same_clock)
    assert not timestamps_are_comparable(left, other_clock)
    assert not timestamps_are_comparable(left, unknown)


def test_timeline_audit_reports_missing_duplicates_nonmonotonic_and_cadence() -> None:
    events = [
        _event("later-first", 20, sequence_index=0),
        _event("duplicate-a", 10, sequence_index=1),
        _event("duplicate-b", 10, sequence_index=2),
        _event(
            "timezone-unknown",
            None,
            status="timezone_unknown",
            clock_domain=None,
            sequence_index=3,
        ),
        _event(
            "aware-but-unverified",
            30,
            status="unverified",
            clock_domain=None,
            sequence_index=4,
        ),
    ]

    result = audit_timelines(events)
    assert len(result.groups) == 1
    group = result.groups[0]
    assert group.event_count == 5
    assert group.verified_timestamp_count == 3
    assert group.missing_timestamp_count == 1
    assert group.noncomparable_timestamp_count == 1
    assert group.earliest_timestamp_utc == ORIGIN + timedelta(seconds=10)
    assert group.latest_timestamp_utc == ORIGIN + timedelta(seconds=20)
    assert group.duplicate_timestamp_group_count == 1
    assert group.duplicate_timestamp_event_count == 2
    assert group.duplicate_timestamp_event_ids == (("duplicate-a", "duplicate-b"),)
    assert group.non_monotonic_transition_count == 1
    assert group.non_monotonic_transitions == (("later-first", "duplicate-a", -10.0),)
    assert group.observed_cadence_seconds == (0.0, 10.0)
    assert group.cadence_seconds_median == 5.0
    assert group.ordering_basis == "sequence_index"


def test_exact_alignment_stays_within_experiment_run_and_clock() -> None:
    events = [
        _event("anchor", 10),
        _event("exact", 10, modality="sensor"),
        _event("other-run", 10, modality="sensor", run=2),
        _event("other-experiment", 10, modality="sensor", experiment="EXP-B"),
        _event(
            "other-clock",
            10,
            modality="sensor",
            clock_domain="unrelated_clock",
        ),
    ]

    result, rows = _rows_by_anchor(events, tolerance_seconds=0)
    row = rows["anchor"]
    assert row.status == "matched"
    assert row.match_kind == "exact"
    assert row.selected_candidate_event_id == "exact"
    assert row.signed_delta_seconds == 0
    assert row.comparable_candidate_count == 1
    assert row.incomparable_clock_candidate_count == 1
    assert row.one_to_one
    assert row.cardinality == "one_to_one"
    assert result.summary()["matched_anchor_count"] == 1


def test_nearest_match_includes_exact_tolerance_boundary() -> None:
    events = [
        _event("anchor", 10),
        _event("boundary", 7, modality="sensor"),
        _event("outside", 6.999, modality="sensor"),
    ]

    _, rows = _rows_by_anchor(events, tolerance_seconds=3)
    row = rows["anchor"]
    assert row.status == "matched"
    assert row.match_kind == "nearest"
    assert row.selected_candidate_event_id == "boundary"
    assert row.signed_delta_seconds == -3
    assert row.absolute_delta_seconds == 3
    assert row.within_tolerance_candidate_ids == ("boundary",)


def test_equidistant_candidates_are_retained_as_deterministic_ambiguity() -> None:
    events = [
        _event("anchor", 10),
        _event("z-future", 11, modality="sensor"),
        _event("a-past", 9, modality="sensor"),
    ]

    _, rows = _rows_by_anchor(list(reversed(events)), tolerance_seconds=2)
    row = rows["anchor"]
    assert row.status == "ambiguous"
    assert row.ambiguous
    assert row.nearest_candidate_event_ids == ("a-past", "z-future")
    assert row.selected_candidate_event_id == "a-past"
    assert row.one_to_many
    assert row.cardinality == "one_to_many"


def test_missing_unusable_incomparable_and_out_of_tolerance_are_distinct() -> None:
    events = [
        _event(
            "anchor-missing-time",
            None,
            run=1,
            status="missing",
            clock_domain=None,
        ),
        _event("sensor-for-missing-anchor", 0, modality="sensor", run=1),
        _event("anchor-missing-modality", 0, run=2),
        _event("anchor-too-far", 20, run=3),
        _event("far-sensor", 0, modality="sensor", run=3),
        _event("anchor-candidate-no-time", 0, run=4),
        _event(
            "sensor-no-time",
            None,
            modality="sensor",
            run=4,
            status="missing",
            clock_domain=None,
        ),
        _event("anchor-other-clock", 0, run=5),
        _event(
            "sensor-other-clock",
            0,
            modality="sensor",
            run=5,
            clock_domain="unrelated_clock",
        ),
    ]

    _, rows = _rows_by_anchor(events, tolerance_seconds=5)
    assert rows["anchor-missing-time"].status == "anchor_timestamp_unusable"
    assert rows["anchor-missing-time"].anchor_timestamp_missing
    assert rows["anchor-missing-modality"].status == "missing_modality"
    assert rows["anchor-missing-modality"].missing_modality
    assert rows["anchor-too-far"].status == "no_match"
    assert rows["anchor-too-far"].missing_match
    assert rows["anchor-candidate-no-time"].status == "candidate_timestamp_unusable"
    assert rows["anchor-candidate-no-time"].candidate_timestamp_missing_count == 1
    assert rows["anchor-other-clock"].status == "incomparable_clock"
    assert rows["anchor-other-clock"].incomparable_clock_candidate_count == 1


def test_past_only_rejects_closer_future_event_to_prevent_leakage() -> None:
    events = [
        _event("anchor", 10),
        _event("future", 11, modality="sensor"),
        _event("past-boundary", 7, modality="sensor"),
    ]

    _, nearest_rows = _rows_by_anchor(events, tolerance_seconds=3)
    _, past_rows = _rows_by_anchor(
        events,
        tolerance_seconds=3,
        direction="past_only",
    )
    assert nearest_rows["anchor"].selected_candidate_event_id == "future"
    assert nearest_rows["anchor"].signed_delta_seconds == 1
    assert past_rows["anchor"].selected_candidate_event_id == "past-boundary"
    assert past_rows["anchor"].signed_delta_seconds == -3
    assert past_rows["anchor"].future_candidate_rejected_count == 1


def test_many_anchors_using_one_candidate_are_flagged_many_to_one() -> None:
    events = [
        _event("anchor-a", 9),
        _event("anchor-b", 11),
        _event("shared-sensor", 10, modality="sensor"),
    ]

    _, rows = _rows_by_anchor(events, tolerance_seconds=2)
    for anchor_id in ("anchor-a", "anchor-b"):
        row = rows[anchor_id]
        assert row.selected_candidate_event_id == "shared-sensor"
        assert row.many_to_one
        assert not row.one_to_one
        assert row.cardinality == "many_to_one"
        assert row.candidate_anchor_counts == (("shared-sensor", 2),)


def test_duplicate_event_ids_are_rejected_before_audit_or_alignment() -> None:
    events = [_event("duplicate-id", 0), _event("duplicate-id", 1)]
    with pytest.raises(ValueError, match="event_id values must be unique"):
        audit_timelines(events)
    with pytest.raises(ValueError, match="event_id values must be unique"):
        align_event_modalities(
            events,
            AlignmentOptions("image", "sensor", tolerance_seconds=1),
        )
