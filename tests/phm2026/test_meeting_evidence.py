from __future__ import annotations

import pandas as pd

from pi_multimodal_ad.reporting.dataset_evidence import build_dataset_evidence


def _source(name: str) -> dict[str, object]:
    return {
        "source_run_id": f"run-{name}",
        "artifact_path": f"tables/{name}.parquet",
        "artifact_sha256": name[0] * 64,
    }


def test_dataset_evidence_preserves_coverage_boundaries() -> None:
    assets = pd.DataFrame(
        [
            {
                "experiment": "EXP-A",
                "run": 1,
                "modality": "high_frequency",
                "member_count": 2,
                "nested_archive_member_count": 0,
                "size_bytes": 100,
            },
            {
                "experiment": "EXP-A",
                "run": 1,
                "modality": "image",
                "member_count": 3,
                "nested_archive_member_count": 0,
                "size_bytes": 50,
            },
            {
                "experiment": "EXP-A",
                "run": None,
                "modality": "low_frequency",
                "member_count": 1,
                "nested_archive_member_count": 1,
                "size_bytes": 20,
            },
        ]
    )
    hdf5 = pd.DataFrame([{"status": "ok", "file_schema_id": "schema-a"}])
    sensors = pd.DataFrame([{"shape_json": "[10]", "sampling_rate_hz": 1.0}])
    images = pd.DataFrame(
        [
            {
                "experiment": "EXP-A",
                "shape_hwc_json": "[2,2,3]",
                "color_mode": "RGB",
                "dtype": "uint8",
                "bit_depth": 8,
                "file_format": "JPEG",
                "timestamp_status": "missing",
            }
        ]
    )
    sources = {
        name: _source(name)
        for name in (
            "asset_inventory",
            "sensor_profile",
            "image_profile",
            "alignment_audit",
            "professor_description",
        )
    }
    result = build_dataset_evidence(
        assets=assets,
        hdf5_members=hdf5,
        sensors=sensors,
        images=images,
        sources=sources,
    )

    assert result.summary["raw_archives_opened"] is False
    assert result.summary["archive_members_are_model_samples"] is False
    sensor_rows = result.tables["sensor_shape_family_counts"]
    assert sensor_rows[0]["coverage_scope"].startswith("bounded representative")
    assert result.tables["image_counts_by_experiment"][0]["image_count"] == 1
