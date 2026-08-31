from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd

from pi_multimodal_ad.profiling.alignment_artifacts import write_blocker_artifacts
from pi_multimodal_ad.profiling.alignment_pipeline import (
    AlignmentPipelineOptions,
    build_alignment_pipeline,
    write_alignment_run,
)
from pi_multimodal_ad.utils import create_run_context, load_yaml_config

UTC = timezone.utc


def _profiles() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    hdf5_members = pd.DataFrame(
        [
            {
                "hdf5_member_id": "hf_member_1",
                "modality": "high_frequency",
                "status": "ok",
                "experiment": "EXP-A",
                "run": 1,
                "start_timestamp_utc": "2026-01-01T12:00:00+00:00",
                "timestamp_source": "wf_start_time",
                "archive_asset_id": "archive_hf_1",
                "archive_relative_path": "synthetic/exp-a-run-1.zip",
                "hdf5_member_path": "GearRun1_001.h5",
            }
        ]
    )
    sensor_profile = pd.DataFrame(
        [
            {
                "sensor_id": "ci_sensor_1",
                "hdf5_member_id": "hf_member_1",
                "channel_role": "condition_indicator",
                "experiment": "EXP-A",
                "run": 1,
                "start_timestamp_utc": "2026-01-01T12:00:00+00:00",
                "timestamp_source": "wf_start_time",
                "archive_asset_id": "archive_hf_1",
                "archive_relative_path": "synthetic/exp-a-run-1.zip",
                "hdf5_member_path": "GearRun1_001.h5",
                "hdf5_path": "/CI/FM4",
                "error": None,
            }
        ]
    )
    image_profile = pd.DataFrame(
        [
            {
                "image_id": "image_1",
                "source_member_id": "image_member_1",
                "experiment": "EXP-A",
                "run": 1,
                "timestamp_status": "timezone_unknown",
                "timestamp_raw": "20260101_13_00_00",
                "timestamp_local_naive": "2026-01-01T13:00:00",
                "timestamp_source": "member_filename",
                "timestamp_evidence": "synthetic local-naive filename token",
                "archive_asset_id": "archive_photo_1",
                "archive_relative_path": "synthetic/exp-a-photos-run-1.zip",
                "source_relative_path": "synthetic/exp-a-photos-run-1.zip::WIN_20260101_13_00_00_Pro.jpg",
                "outer_archive_member": "WIN_20260101_13_00_00_Pro.jpg",
                "inspection_id": "inspection_1",
                "inspection_stage": "run_1",
                "tooth_id": "1",
                "image_role": "camera_sequence",
            },
            {
                "image_id": "image_2",
                "source_member_id": "image_member_2",
                "experiment": "EXP-A",
                "run": 1,
                "timestamp_status": "missing",
                "timestamp_raw": None,
                "timestamp_local_naive": None,
                "timestamp_source": None,
                "timestamp_evidence": None,
                "archive_asset_id": "archive_photo_1",
                "archive_relative_path": "synthetic/exp-a-photos-run-1.zip",
                "source_relative_path": "synthetic/exp-a-photos-run-1.zip::Tooth 01.jpg",
                "outer_archive_member": "Tooth 01.jpg",
                "inspection_id": "inspection_1",
                "inspection_stage": "run_1",
                "tooth_id": "1",
                "image_role": "canonical_tooth",
            },
        ]
    )
    return hdf5_members, sensor_profile, image_profile


def test_blocked_pipeline_preserves_clock_status_and_never_creates_a_join(
    tmp_path: Path,
) -> None:
    hdf5_members, sensor_profile, image_profile = _profiles()
    result = build_alignment_pipeline(
        hdf5_members,
        sensor_profile,
        image_profile,
        options=AlignmentPipelineOptions(
            tolerance_seconds=21_600,
            direction="past_only",
            six_hour_reference_seconds=21_600,
            six_hour_tolerance_seconds=60,
            trace_example_count=2,
        ),
    )

    summary = result.summary()
    assert summary["status"] == (
        "PARTIALLY_COMPLETE_BLOCKED_BY_UNVERIFIED_IMAGE_CLOCK_DOMAIN"
    )
    assert summary["image_timestamp_status_counts"] == {
        "missing": 1,
        "timezone_unknown": 1,
    }
    assert not summary["image_sensor_timestamps_comparable"]
    assert not summary["nearest_temporal_matching_authorized"]
    assert not summary["join_cardinality_computable"]
    assert all(
        row["selected_candidate_event_id"] is None for row in result.alignment_rows
    )
    assert all(row["signed_delta_seconds"] is None for row in result.alignment_rows)
    assert {row["status"] for row in result.trace_rows} == {"BLOCKED"}
    assert {row["clock_blocker"] for row in result.trace_rows} == {
        "image_acquisition_timestamp_missing",
        "image_local_naive_timestamp_has_no_evidenced_timezone",
    }

    repository = tmp_path / "repository"
    config_path = repository / "configs/experiment.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "schema_version: '1.0.0'\nstudy: synthetic_alignment_audit\n",
        encoding="utf-8",
    )
    config = load_yaml_config(config_path, repository_root=repository)
    run = create_run_context(
        study="synthetic_alignment_audit",
        output_root=repository / "runs/synthetic_alignment_audit",
        config=config,
        seed=17,
        command=("scripts/dataset/audit_alignment.py",),
        input_roots=("runs/synthetic-source",),
        now=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        package_names=(),
        source_runs=({"run_id": "synthetic-source-run"},),
    )
    input_manifest = [
        {
            "source_run_id": "synthetic-source-run",
            "source_run_directory": "runs/synthetic-source",
            "artifact_path": "tables/synthetic.parquet",
            "artifact_sha256": "0" * 64,
            "artifact_size_bytes": 1,
        }
    ]
    artifacts = write_alignment_run(
        result,
        run=run,
        resolved_config={"schema_version": "1.0.0", "task": "D1.4"},
        input_manifest=input_manifest,
    )
    artifacts = write_blocker_artifacts(
        result,
        run=run,
        input_manifest=input_manifest,
        existing_artifacts=artifacts,
    )

    image_clock_csv = pd.read_csv(run.run_directory / "tables/image_clock_audit.csv")
    image_clock_parquet = pd.read_parquet(
        run.run_directory / "tables/image_clock_audit.parquet"
    )
    assert len(image_clock_csv) == len(image_clock_parquet) == 2
    assert image_clock_csv["timestamp_utc"].isna().all()
    blockers = json.loads(
        (run.run_directory / "reports/alignment_blockers.json").read_text(
            encoding="utf-8"
        )
    )
    assert blockers["classification"] == summary["status"]
    assert blockers["clock_domain_status"] == ("NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED")
    assert blockers["target_status"] == "NOT_COMPUTABLE_TARGET_UNRESOLVED"
    output_manifest = json.loads(
        (run.run_directory / "manifests/outputs.json").read_text(encoding="utf-8")
    )
    roles = {row["role"] for row in output_manifest["artifacts"]}
    assert {
        "modality_events_csv",
        "modality_events_parquet",
        "image_clock_audit_csv",
        "image_clock_audit_parquet",
        "sensor_clock_audit_csv",
        "sensor_clock_audit_parquet",
        "alignment_blockers",
        "source_artifact_index",
        "run_provenance",
    } <= roles
    assert len(artifacts) == len(output_manifest["artifacts"])


def test_verified_image_time_without_a_matching_clock_domain_stays_unjoined() -> None:
    hdf5_members, sensor_profile, image_profile = _profiles()
    image_profile.loc[:, "timestamp_status"] = "verified_utc"
    image_profile.loc[:, "timestamp_utc"] = "2026-01-01T12:00:00+00:00"
    image_profile.loc[:, "timestamp_clock_domain"] = "camera_utc_unverified"
    image_profile.loc[:, "timestamp_local_naive"] = None

    result = build_alignment_pipeline(hdf5_members, sensor_profile, image_profile)

    assert all(
        row["selected_candidate_event_id"] is None for row in result.alignment_rows
    )
    assert any(row["status"] == "incomparable_clock" for row in result.alignment_rows)
