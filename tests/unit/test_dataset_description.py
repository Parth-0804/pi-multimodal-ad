from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd

from pi_multimodal_ad.profiling.dataset_description import (
    build_dataset_description,
    write_dataset_description_run,
)
from pi_multimodal_ad.utils import create_run_context, load_yaml_config

UTC = timezone.utc


def _source(name: str) -> dict[str, object]:
    return {
        "source_run_id": f"synthetic-{name}-run",
        "source_run_directory": f"runs/synthetic/{name}",
        "artifact_path": f"reports/{name}.json",
        "artifact_sha256": (name.encode("utf-8").hex() + "0" * 64)[:64],
        "artifact_size_bytes": 1,
    }


def test_professor_report_regenerates_from_fixture_profiles(tmp_path: Path) -> None:
    sources = {
        name: _source(name)
        for name in (
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
        )
    }
    assets = pd.DataFrame(
        [
            {
                "asset_id": "asset_hf",
                "experiment": "EXP-A",
                "run": 1,
                "modality": "high_frequency",
                "size_bytes": 10,
                "member_count": 3,
                "nested_archive_member_count": 0,
            },
            {
                "asset_id": "asset_photo",
                "experiment": "EXP-A",
                "run": 1,
                "modality": "image",
                "size_bytes": 2,
                "member_count": 2,
                "nested_archive_member_count": 0,
            },
        ]
    )
    sensors = pd.DataFrame(
        [
            {
                "sensor_id": "sensor_1",
                "hdf5_member_id": "member_1",
                "channel_role": "vibration",
                "hdf5_path": "/Vibration/Accel 1",
                "shape_json": "[16]",
                "dtype": "float32",
                "sampling_rate_hz": 102400.0,
                "unit": "g",
                "duration_seconds": 0.00015625,
            }
        ]
    )
    images = pd.DataFrame(
        [
            {
                "shape_hwc_json": "[12,16,3]",
                "color_mode": "RGB",
                "dtype": "uint8",
                "bit_depth": 8,
                "file_format": "JPEG",
                "aspect_ratio": 1.33333333333,
                "header_status": "ok",
            }
        ]
    )
    image_clock = pd.DataFrame(
        [
            {"timestamp_status": "timezone_unknown"},
            {"timestamp_status": "missing"},
        ]
    )
    sensor_clock = pd.DataFrame(
        [
            {
                "experiment": "EXP-A",
                "run": 1,
                "timestamp_status": "verified_utc",
                "clock_domain": "sensor_utc",
                "event_id": "sensor_event_1",
                "hdf5_member_path": "synthetic_member.h5",
                "timestamp_utc": "2026-01-01T12:00:00+00:00",
            }
        ]
    )
    traces = pd.DataFrame(
        [
            {
                "trace_id": "trace_1",
                "experiment": "EXP-A",
                "run": 1,
                "image_id": "image_1",
                "image_source_relative_path": "synthetic/photo.jpg",
                "image_timestamp_status": "timezone_unknown",
                "image_timestamp_raw": "20260101_130000",
            }
        ]
    )
    inventory_summary = {
        "readable_file_count": 52,
        "archive_member_count": 8512,
        "nested_zip_member_count": 40,
        "missing_expected_count": 0,
        "unreadable_file_count": 0,
        "issue_counts": {"warning": 13},
        "crc_size_duplicate_candidate_rows": 622,
        "exact_member_metadata_duplicate_rows": 0,
    }
    sensor_summary = {
        "profiled_hdf5_member_count": 745,
        "sensor_dataset_count": 27165,
        "readable_hdf5_member_count": 745,
        "file_schema_variant_count": 13,
        "shape_counts": {str(index): index for index in range(12)},
        "dtype_counts": {"float32": 1, "float64": 1, "uint16": 1},
        "duration_seconds_min": 0.00006,
        "duration_seconds_max": 60.0,
        "duration_seconds_median": 60.0,
        "run_token_conflict_member_count": 446,
    }
    image_header_summary = {
        "profiled_image_count": 1311,
        "readable_header_count": 1311,
        "counts_by_experiment": {"EXP-A": 455, "EXP-B": 576, "EXP-F": 280},
    }
    image_quality_summary = {
        "pixel_quality_selected_count": 104,
        "pixel_quality_success_count": 104,
        "exact_hash_covered_count": 104,
        "near_duplicate_pair_count": 127,
    }
    blockers = {
        "classification": "PARTIALLY_COMPLETE_BLOCKED_BY_UNVERIFIED_IMAGE_CLOCK_DOMAIN",
        "image_clock_audit": {
            "verified_utc_images": 0,
            "timezone_unknown_images": 640,
            "missing_timestamp_images": 671,
        },
        "sensor_clock_domain": "sensor_utc",
        "image_sensor_timestamps_comparable": False,
        "nearest_temporal_matching_authorized": False,
        "join_cardinality_computable": False,
        "six_hour_cross_modal_cadence": "UNRESOLVED",
        "clock_domain_status": "NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED",
        "required_to_unblock": ["authoritative camera timezone"],
    }
    result = build_dataset_description(
        asset_inventory=assets,
        inventory_summary=inventory_summary,
        sensor_profile=sensors,
        sensor_summary=sensor_summary,
        image_profile=images,
        image_header_summary=image_header_summary,
        image_quality_summary=image_quality_summary,
        image_clock_audit=image_clock,
        sensor_clock_audit=sensor_clock,
        alignment_blockers=blockers,
        alignment_traces=traces,
        sources=sources,
    )
    repeated = build_dataset_description(
        asset_inventory=assets,
        inventory_summary=inventory_summary,
        sensor_profile=sensors,
        sensor_summary=sensor_summary,
        image_profile=images,
        image_header_summary=image_header_summary,
        image_quality_summary=image_quality_summary,
        image_clock_audit=image_clock,
        sensor_clock_audit=sensor_clock,
        alignment_blockers=blockers,
        alignment_traces=traces,
        sources=sources,
    )
    assert repeated.report_markdown == result.report_markdown
    assert repeated.tables == result.tables
    assert result.summary["alignment_classification"] == blockers["classification"]
    assert "52 readable ZIP archives" in result.report_markdown
    assert "745 HDF5 members" in result.report_markdown
    assert "1,311 images" in result.report_markdown
    assert "not a valid aligned training sample" in result.report_markdown
    assert "PARTIALLY_COMPLETE_BLOCKED_BY_UNVERIFIED_IMAGE_CLOCK_DOMAIN" in (
        result.report_markdown
    )
    assert "RT-DETR" in result.report_markdown
    assert "PatchTST" in result.report_markdown
    assert "Multimodal modelling" in result.report_markdown

    repository = tmp_path / "repository"
    config_path = repository / "configs/experiment.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "schema_version: '1.0.0'\nstudy: synthetic_dataset_description\n",
        encoding="utf-8",
    )
    config = load_yaml_config(config_path, repository_root=repository)
    run = create_run_context(
        study="synthetic_dataset_description",
        output_root=repository / "runs/synthetic_dataset_description",
        config=config,
        seed=17,
        command=("scripts/describe_dataset.py",),
        input_roots=("runs/synthetic",),
        now=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        package_names=(),
    )
    artifacts = write_dataset_description_run(
        result,
        run=run,
        resolved_config={"schema_version": "1.0.0", "task": "D1.5"},
        input_manifest=list(sources.values()),
    )
    report_path = run.run_directory / "reports/professor_dataset_description.md"
    assert report_path.read_text(encoding="utf-8") == result.report_markdown
    expected_tables = {
        "dataset_at_a_glance",
        "modality_coverage",
        "sensor_shape_summary",
        "image_shape_summary",
        "clock_domain_summary",
        "unresolved_decisions",
        "artifact_source_index",
    }
    assert all(
        (run.run_directory / f"tables/{name}.csv").is_file() for name in expected_tables
    )
    output_manifest = json.loads(
        (run.run_directory / "manifests/outputs.json").read_text(encoding="utf-8")
    )
    assert len(artifacts) == len(output_manifest["artifacts"])
    assert any(
        row["role"] == "professor_dataset_description"
        for row in output_manifest["artifacts"]
    )
