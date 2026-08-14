from __future__ import annotations

import pandas as pd

from pi_multimodal_ad.reporting.target_audit import BLOCKED, build_target_audit


def test_target_audit_blocks_without_target_timing_pairing_and_six_hour_evidence() -> (
    None
):
    sensors = pd.DataFrame(
        [
            {
                "hdf5_path": "/CI/FM4",
                "hdf5_member_id": "member-1",
                "unit": None,
                "sampling_rate_hz": 1.0,
            }
        ]
    )
    images = pd.DataFrame([{"image_id": "image-1"}])
    definitions = [
        {
            "candidate_id": "fm4",
            "variable_name": "FM4",
            "physical_meaning": "gear condition indicator",
            "unit": "unknown",
            "candidate_type": "continuous",
            "source_patterns": ["/CI/FM4"],
            "direct_or_derived": "derived",
            "inference_availability": "unknown",
            "supporting_evidence": "path exists",
            "contradicting_evidence": "not a target definition",
        }
    ]
    sources = {
        "sensor_profile": {
            "source_run_id": "sensor-run",
            "artifact_path": "tables/sensor.parquet",
            "artifact_sha256": "a" * 64,
        }
    }
    result = build_target_audit(
        sensors=sensors,
        images=images,
        alignment_blockers={"image_clock_audit": {"verified_utc_images": 0}},
        candidate_definitions=definitions,
        sources=sources,
    )

    assert result.blockers["classification"] == BLOCKED
    assert result.blockers["t2_2_authorized"] is False
    assert result.blockers["rtdetr_regression_authorized"] is False
    assert result.summary["target_records_created"] == 0
    assert result.candidates[0]["verified_image_pair_count"] == 0
