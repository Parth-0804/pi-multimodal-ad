"""v3 target definition: tooth exclusion and single-deterministic-view selection."""

from __future__ import annotations

import pytest

from phm2026.targets.image_damage import ImageDamageOptions, aggregate_targets


def _options(**overrides):
    base = dict(
        roi_normalized_xyxy=(0.08, 0.12, 0.92, 0.50),
        clahe_clip_limit=2.0,
        background_sigma_pixels=31.0,
        residual_z_threshold=2.0,
        gradient_z_threshold=2.0,
        minimum_component_fraction=0.00008,
        damaged_tooth_threshold_pct=2.0,
        minimum_valid_teeth=24,
        near_duplicate_hamming=4,
        max_member_bytes=8_388_608,
        overlay_jpeg_quality=88,
    )
    base.update(overrides)
    return ImageDamageOptions(**base)


def _image(tooth, value, *, image_id, image_type="canonical_tooth", timestamp="WIN_20240101_00_00_00_Pro"):
    return {
        "decoding_status": "ok",
        "experiment": "EXP-A",
        "run": 1,
        "tooth_id": tooth,
        "image_id": image_id,
        "image_type": image_type,
        "timestamp_text": timestamp,
        "damage_candidate_area_pct": value,
        "largest_component_ratio_pct": value / 2,
        "overlay_path": f"overlays/{image_id}.jpg",
        "segmentation_confidence": 0.9,
        "pairing_evidence": "test",
        "near_duplicate_group": None,
    }


def test_excluded_teeth_are_dropped_entirely():
    rows = [_image(tooth, 1.0 + tooth, image_id=f"i{tooth}") for tooth in range(1, 9)]
    teeth, _, _ = aggregate_targets(rows, _options(excluded_tooth_ids=(1, 2, 3, 4)))
    assert sorted(row["tooth_id"] for row in teeth) == [5, 6, 7, 8]


def test_single_deterministic_view_prefers_canonical_over_close_ups():
    rows = [
        # the close-up carries the larger value; max/median would pick it up
        _image(5, 9.0, image_id="closeup", image_type="camera_sequence",
               timestamp="WIN_20240101_00_00_00_Pro"),
        _image(5, 2.0, image_id="canonical", image_type="canonical_tooth",
               timestamp="WIN_20240101_09_00_00_Pro"),
    ]
    teeth, _, _ = aggregate_targets(rows, _options(view_selection="single_deterministic_view"))
    assert len(teeth) == 1
    assert teeth[0]["selected_image_id"] == "canonical"
    assert teeth[0]["per_tooth_damage_candidate_pct"] == pytest.approx(2.0)


def test_single_deterministic_view_falls_back_to_earliest_close_up():
    rows = [
        _image(5, 9.0, image_id="late", image_type="camera_sequence",
               timestamp="WIN_20240101_09_00_00_Pro"),
        _image(5, 2.0, image_id="early", image_type="camera_sequence",
               timestamp="WIN_20240101_00_00_00_Pro"),
    ]
    teeth, _, _ = aggregate_targets(rows, _options(view_selection="single_deterministic_view"))
    assert teeth[0]["selected_image_id"] == "early"
    assert teeth[0]["per_tooth_damage_candidate_pct"] == pytest.approx(2.0)


def test_view_count_cannot_change_a_single_view_value():
    """Ten views of a tooth must give the same value as one, under v3."""

    one = [_image(5, 3.0, image_id="a", image_type="camera_sequence")]
    many = one + [
        _image(5, 3.0 + index, image_id=f"b{index}", image_type="camera_sequence",
               timestamp=f"WIN_20240101_10_00_{index:02d}_Pro")
        for index in range(1, 10)
    ]
    options = _options(view_selection="single_deterministic_view")
    value_one = aggregate_targets(one, options)[0][0]["per_tooth_damage_candidate_pct"]
    value_many = aggregate_targets(many, options)[0][0]["per_tooth_damage_candidate_pct"]
    assert value_one == pytest.approx(value_many)


def test_v2_defaults_are_unchanged():
    """Defaults must still reproduce the committed v2 behaviour (median, all teeth)."""

    options = _options(minimum_valid_teeth=28)
    assert options.target_definition_version == "phm2026_image_damage_v2"
    assert options.view_selection == "median_candidate_ratio"
    assert options.excluded_tooth_ids == ()
    rows = [
        _image(1, 1.0, image_id="a"),
        _image(1, 5.0, image_id="b"),
        _image(1, 9.0, image_id="c"),
    ]
    teeth, _, _ = aggregate_targets(rows, options)
    assert teeth[0]["per_tooth_damage_candidate_pct"] == pytest.approx(5.0)
    assert teeth[0]["tooth_id"] == 1


def test_invalid_options_are_rejected():
    with pytest.raises(ValueError):
        _options(view_selection="not_a_rule")
    with pytest.raises(ValueError):
        _options(excluded_tooth_ids=(0,))
    with pytest.raises(ValueError):
        _options(excluded_tooth_ids=(29,))
