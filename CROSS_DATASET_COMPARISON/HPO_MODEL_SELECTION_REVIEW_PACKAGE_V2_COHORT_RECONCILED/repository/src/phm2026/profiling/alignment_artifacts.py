"""Additional D1.4 blocker-audit artifacts derived from canonical event rows."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from ..utils.provenance import ArtifactRecord, RunContext
from .alignment_pipeline import (
    ALIGNMENT_PIPELINE_SCHEMA_VERSION,
    EVENT_COLUMNS,
    HDF5_EXPLICIT_UTC_CLOCK,
    AlignmentPipelineResult,
    _serialize_cell,
)


def _write_table_pair(
    csv_path: Path,
    parquet_path: Path,
    rows: Sequence[Mapping[str, Any]],
) -> None:
    serialised = [
        {column: _serialize_cell(column, row.get(column)) for column in EVENT_COLUMNS}
        for row in rows
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EVENT_COLUMNS))
        writer.writeheader()
        writer.writerows(serialised)
    pd.DataFrame(serialised, columns=EVENT_COLUMNS).to_parquet(
        parquet_path, index=False
    )


def _source_index_rows(
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
            "source_index": index,
            "source_run_id": source.get("source_run_id"),
            "source_run_directory": source.get("source_run_directory"),
            "artifact_path": source.get("artifact_path"),
            "artifact_sha256": source.get("artifact_sha256"),
            "artifact_size_bytes": source.get("artifact_size_bytes"),
        }
        for index, source in enumerate(input_manifest)
    ]


def write_blocker_artifacts(
    result: AlignmentPipelineResult,
    *,
    run: RunContext,
    input_manifest: Sequence[Mapping[str, Any]],
    existing_artifacts: Sequence[ArtifactRecord],
) -> list[ArtifactRecord]:
    """Add explicit clock/blocker tables and replace manifests with final evidence."""

    image_rows = [row for row in result.event_rows if row["modality"] == "photograph"]
    sensor_modalities = {
        "high_frequency_recording",
        "low_frequency_observation",
        "condition_indicator",
        "operating_context",
        "oil",
        "environment",
    }
    sensor_rows = [
        row for row in result.event_rows if row["modality"] in sensor_modalities
    ]
    written: list[ArtifactRecord] = []
    for stem, rows, role in (
        ("modality_events", result.event_rows, "modality_events"),
        ("image_clock_audit", image_rows, "image_clock_audit"),
        ("sensor_clock_audit", sensor_rows, "sensor_clock_audit"),
    ):
        csv_path = run.run_directory / f"tables/{stem}.csv"
        parquet_path = run.run_directory / f"tables/{stem}.parquet"
        _write_table_pair(csv_path, parquet_path, rows)
        written.extend(
            [
                run.artifact(csv_path, role=f"{role}_csv"),
                run.artifact(parquet_path, role=f"{role}_parquet"),
            ]
        )

    summary = result.summary()
    image_status = summary["image_timestamp_status_counts"]
    blockers = {
        "schema_version": ALIGNMENT_PIPELINE_SCHEMA_VERSION,
        "classification": summary["status"],
        "image_clock_audit": {
            "total_images": sum(image_status.values()),
            "verified_utc_images": image_status.get("verified_utc", 0),
            "timezone_unknown_images": image_status.get("timezone_unknown", 0),
            "missing_timestamp_images": image_status.get("missing", 0),
            "timezone_policy": "local_naive_image_timestamps_are_not_converted_to_utc",
        },
        "sensor_clock_domain": HDF5_EXPLICIT_UTC_CLOCK,
        "image_sensor_timestamps_comparable": summary[
            "image_sensor_timestamps_comparable"
        ],
        "nearest_temporal_matching_authorized": summary[
            "nearest_temporal_matching_authorized"
        ],
        "join_cardinality_computable": summary["join_cardinality_computable"],
        "six_hour_cross_modal_cadence": "UNRESOLVED",
        "clock_domain_status": "NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED",
        "missing_timestamp_status": "NOT_COMPUTABLE_TIMESTAMP_MISSING",
        "target_status": "NOT_COMPUTABLE_TARGET_UNRESOLVED",
        "observed_evidence_status": "OBSERVED_FROM_DATA",
        "unknown_status": "UNKNOWN",
        "required_to_unblock": [
            "authoritative timezone for camera filename timestamps",
            "evidence of camera/sensor clock synchronization or documented offset/drift",
            "an authoritative non-temporal image-to-sensor pairing key if clocks are not comparable",
            "scalar target definition including unit, timestamp, and six-hour interpretation",
        ],
    }
    blockers_path = run.run_directory / "reports/alignment_blockers.json"
    blockers_path.write_text(
        json.dumps(blockers, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written.append(run.artifact(blockers_path, role="alignment_blockers"))

    index_rows = _source_index_rows(input_manifest)
    index_path = run.run_directory / "tables/source_artifact_index.csv"
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        columns = [
            "schema_version",
            "source_index",
            "source_run_id",
            "source_run_directory",
            "artifact_path",
            "artifact_sha256",
            "artifact_size_bytes",
        ]
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(index_rows)
    written.append(run.artifact(index_path, role="source_artifact_index"))

    retained = [
        artifact for artifact in existing_artifacts if artifact.role != "run_provenance"
    ]
    all_without_provenance = [*retained, *written]
    provenance_path = run.write_provenance(all_without_provenance)
    all_artifacts = [
        *all_without_provenance,
        run.artifact(provenance_path, role="run_provenance"),
    ]
    run.write_output_manifest(all_artifacts)
    return all_artifacts


__all__ = ["write_blocker_artifacts"]
