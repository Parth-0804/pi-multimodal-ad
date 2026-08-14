from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
import pytest

from pi_multimodal_ad.profiling.images import ImageSource
from pi_multimodal_ad.targets.image_damage import (
    ImageDamageOptions,
    measure_damage_candidate,
)
from pi_multimodal_ad.targets.pseudo_boxes import (
    ComponentDecision,
    build_pseudo_box_dataset,
    component_to_box,
    replay_mask_with_components,
    validate_pseudo_box_result,
    validate_xyxy,
)


def _options() -> ImageDamageOptions:
    return ImageDamageOptions(
        roi_normalized_xyxy=(0.08, 0.12, 0.92, 0.50),
        clahe_clip_limit=2.0,
        background_sigma_pixels=7.0,
        residual_z_threshold=2.0,
        gradient_z_threshold=2.0,
        minimum_component_fraction=0.00008,
        damaged_tooth_threshold_pct=2.0,
        minimum_valid_teeth=28,
        near_duplicate_hamming=4,
        max_member_bytes=8_388_608,
        overlay_jpeg_quality=88,
    )


def test_mask_replay_is_bit_exact_and_records_all_components() -> None:
    rgb = np.full((180, 320, 3), 180, dtype=np.uint8)
    rgb[45:52, 55:250] = 35
    rgb[75:100, 180:195] = 20
    expected_metrics, expected_mask, expected_roi = measure_damage_candidate(
        rgb, _options()
    )
    metrics, mask, roi, decisions = replay_mask_with_components(rgb, _options())
    assert np.array_equal(mask, expected_mask)
    assert metrics == expected_metrics
    assert roi == expected_roi
    assert decisions
    assert all(item.reason for item in decisions)
    assert sum(item.retained for item in decisions) == metrics["component_count"]


def test_component_box_clipping_and_validation() -> None:
    decision = ComponentDecision(1, 80, 10, 5, 40, 2, True, "retained_by_v2")
    box = component_to_box(
        decision, roi_xyxy=(20, 30, 120, 90), image_width=150, image_height=100
    )
    assert box == (30, 35, 70, 37)
    validate_xyxy(box, image_width=150, image_height=100, roi_xyxy=(20, 30, 120, 90))
    assert (
        component_to_box(
            ComponentDecision(2, 10, 0, 0, 2, 2, False, "too_small"),
            roi_xyxy=(0, 0, 10, 10),
            image_width=10,
            image_height=10,
        )
        is None
    )
    with pytest.raises(ValueError, match="outside the configured ROI"):
        validate_xyxy(
            (0, 0, 5, 5),
            image_width=20,
            image_height=20,
            roi_xyxy=(4, 4, 18, 18),
        )


def test_one_file_build_preserves_traceability_negative_or_positive(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "source.jpg"
    rgb = np.full((180, 320, 3), 175, dtype=np.uint8)
    rgb[45:52, 65:245] = 30
    Image.fromarray(rgb).save(image_path, quality=96)
    decoded = np.asarray(Image.open(image_path).convert("RGB"), dtype=np.uint8)
    metrics, _, _ = measure_damage_candidate(decoded, _options())
    digest = sha256(image_path.read_bytes()).hexdigest()
    image_id = "image_1"
    member_id = "member_1"
    sample_id = "sample_1"
    image_manifest = pd.DataFrame(
        [
            {
                "image_id": image_id,
                "source_member_id": member_id,
                "archive_path": "synthetic/source.jpg",
                "archive_member": "source.jpg",
                "source_sha256": digest,
                "damage_candidate_pixels": metrics["damage_candidate_pixels"],
                "visible_flank_roi_pixels": metrics["visible_flank_roi_pixels"],
                "damage_candidate_area_pct": metrics["damage_candidate_area_pct"],
            }
        ]
    )
    samples = pd.DataFrame(
        [
            {
                "sample_id": sample_id,
                "image_id": image_id,
                "source_member_id": member_id,
                "experiment": "EXP-B",
                "run": 1,
                "tooth_id": 1,
                "image_type": "canonical_tooth",
                "split": "train",
                "target_definition_version": "phm2026_image_damage_v2",
                "per_image_damage_candidate_pct": metrics["damage_candidate_area_pct"],
                "pairing_evidence": "synthetic",
                "near_duplicate_group": None,
            }
        ]
    )
    source = ImageSource(
        source_member_id=member_id,
        archive_asset_id="asset_1",
        source_kind="file",
        source_relative_path="source.jpg",
        file_path=image_path,
        archive_path=None,
        archive_relative_path=None,
        outer_member_path=None,
        nested_member_path=None,
        member_occurrence=1,
        nested_member_occurrence=1,
        experiment="EXP-B",
        authoritative_outer_run=1,
        compressed_size_bytes=None,
        encoded_size_bytes=image_path.stat().st_size,
        crc32=None,
    )
    result = build_pseudo_box_dataset(
        image_manifest,
        samples,
        {member_id: source},
        options=_options(),
        source_mask_run_id="target_run",
        source_mask_artifact_sha256="a" * 64,
        cache_root=tmp_path / "run/cache",
    )
    assert len(result.image_rows) == 1
    row = result.image_rows[0]
    assert row["source_sha256"] == digest
    assert row["mask_replay_match"] is True
    assert (
        Path(tmp_path / "run" / row["cache_image_path"]).read_bytes()
        == image_path.read_bytes()
    )
    assert Path(tmp_path / "run" / row["yolo_label_path"]).is_file()
    quality = validate_pseudo_box_result(
        result,
        expected_split_counts={"train": 1},
        split_validation={
            "experiment_run_cross_split_violations": 0,
            "near_duplicate_cross_split_violations": 0,
        },
    )
    assert quality["image_count"] == 1
    assert quality["mask_replay_mismatch_count"] == 0
