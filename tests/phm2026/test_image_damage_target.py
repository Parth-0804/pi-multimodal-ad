from __future__ import annotations

import numpy as np

from pi_multimodal_ad.targets.image_damage import (
    ImageDamageOptions,
    aggregate_targets,
    measure_damage_candidate,
)


def _options() -> ImageDamageOptions:
    return ImageDamageOptions(
        roi_normalized_xyxy=(0.1, 0.1, 0.9, 0.8),
        clahe_clip_limit=2.0,
        background_sigma_pixels=5.0,
        residual_z_threshold=1.5,
        gradient_z_threshold=1.0,
        minimum_component_fraction=0.0001,
        damaged_tooth_threshold_pct=2.0,
        minimum_valid_teeth=28,
        near_duplicate_hamming=4,
        max_member_bytes=1_000_000,
        overlay_jpeg_quality=85,
    )


def test_measurement_is_deterministic_and_marks_dark_textured_candidate() -> None:
    image = np.full((200, 300, 3), 180, dtype=np.uint8)
    image[60:72, 60:240] = 30
    first, mask, roi = measure_damage_candidate(image, _options())
    second, second_mask, second_roi = measure_damage_candidate(image, _options())
    assert first == second
    assert np.array_equal(mask, second_mask)
    assert roi == second_roi
    assert first["damage_candidate_area_pct"] > 0
    assert first["measurement_status"].startswith("provisional")


def test_run_target_keeps_raw_and_causal_monotonic_values() -> None:
    rows = []
    for run, base in ((1, 5.0), (2, 2.0)):
        for tooth in range(1, 29):
            rows.append(
                {
                    "decoding_status": "ok",
                    "experiment": "EXP-X",
                    "run": run,
                    "tooth_id": str(tooth),
                    "image_id": f"r{run}-t{tooth}",
                    "damage_candidate_area_pct": base + tooth / 100,
                    "largest_component_ratio_pct": base / 2,
                    "overlay_path": f"overlays/r{run}-t{tooth}.jpg",
                    "segmentation_confidence": 0.8,
                    "pairing_evidence": "synthetic",
                    "near_duplicate_group": None,
                }
            )
    teeth, targets, review = aggregate_targets(rows, _options())
    assert len(teeth) == 56
    assert len(review) == 56
    assert targets[0]["raw_top3_mean_pct"] > targets[1]["raw_top3_mean_pct"]
    assert (
        targets[1]["causal_monotonic_top3_mean_pct"] == targets[0]["raw_top3_mean_pct"]
    )
    assert all(row["valid_tooth_count"] == 28 for row in targets)
