from __future__ import annotations

from datetime import timezone
from pathlib import Path

import pytest
import yaml

from pi_multimodal_ad.data_contracts import ContractValidationError
from pi_multimodal_ad.datasets import (
    PHM2026Adapter,
    UnverifiedTargetSemanticsError,
)


@pytest.fixture
def adapter() -> PHM2026Adapter:
    return PHM2026Adapter()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("EXP A", "EXP-A"), ("EXP-B", "EXP-B"), ("Exp_F", "EXP-F")],
)
def test_experiment_normalization(
    adapter: PHM2026Adapter, raw: str, expected: str
) -> None:
    assert adapter.normalize_experiment(raw) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [("Run-1", 1), ("Exp-B_Photos_Run 7.zip", 7), ("Pre-Run", None)],
)
def test_run_parsing(adapter: PHM2026Adapter, text: str, expected: int | None) -> None:
    assert adapter.parse_run(text) == expected


def test_adapter_emits_generic_asset_record(adapter: PHM2026Adapter) -> None:
    record = adapter.make_asset_record(
        "gtc-data-experiment/high_frequency/EXP B/Exp-B_HDF5_Run-7.zip",
        size_bytes=42,
    )
    assert record.dataset == "phm2026"
    assert record.relative_path == "high_frequency/EXP B/Exp-B_HDF5_Run-7.zip"
    assert record.modality == "high_frequency"
    assert record.experiment == "EXP-B"
    assert record.run == 7
    assert record.asset_kind == "archive"


def test_adapter_rejects_out_of_scope_run(adapter: PHM2026Adapter) -> None:
    with pytest.raises(ContractValidationError, match="outside the configured scope"):
        adapter.parse_asset_identity("high_frequency/EXP A/Exp-A_HDF5_Run-6.zip")


def test_adapter_rejects_intel_boundary(adapter: PHM2026Adapter) -> None:
    with pytest.raises(ContractValidationError, match="Intel dataset"):
        adapter.parse_asset_identity("data/Full Dataset/example.csv")


def test_archive_member_path_must_be_safe(adapter: PHM2026Adapter) -> None:
    with pytest.raises(ContractValidationError, match="safe relative member path"):
        adapter.make_asset_record(
            "high_frequency/EXP A/Exp-A_HDF5_Run-1.zip",
            archive_member="../outside.h5",
        )


def test_sensor_aliases_are_phm_specific(adapter: PHM2026Adapter) -> None:
    assert adapter.sensor_path_aliases("vibration") == ("/Vibration",)
    assert adapter.sensor_path_aliases("condition_indicator") == ("/CI", "/CI_4s")


def test_photo_stage_labels_remain_distinct(adapter: PHM2026Adapter) -> None:
    test_start = adapter.parse_photo_identity(
        "photos/EXP-A/Exp-A_Photos_0 Hours - Test Start.zip",
        "Tooth_03_View_02_2026-01-02T03-04-05Z.jpg",
    )
    pre_run = adapter.parse_photo_identity(
        "photos/EXP-F/Exp-F_Photos_Pre-Run.zip",
        "tooth-3.jpg",
    )
    assert test_start.inspection_stage == "test_start"
    assert pre_run.inspection_stage == "pre_run"
    assert test_start.inspection_stage != pre_run.inspection_stage
    assert test_start.tooth_id == "3"
    assert test_start.sequence == 2
    assert test_start.timestamp is not None
    assert test_start.timestamp.tzinfo == timezone.utc


def test_break_in_spelling_variants_normalize_without_changing_raw_label(
    adapter: PHM2026Adapter,
) -> None:
    hyphenated = adapter.parse_photo_identity(
        "photos/EXP-A/Exp-A_Photos_Break-In.zip", "tooth_1.jpg"
    )
    spaced = adapter.parse_photo_identity(
        "photos/EXP-B/Exp-B_Photos_Break In.zip", "tooth_1.jpg"
    )
    assert hyphenated.inspection_stage == spaced.inspection_stage == "break_in"
    assert hyphenated.raw_inspection_stage == "Break-In"
    assert spaced.raw_inspection_stage == "Break In"


def test_target_semantics_are_explicitly_blocked(adapter: PHM2026Adapter) -> None:
    assert adapter.target_definition_status == "unverified"
    with pytest.raises(UnverifiedTargetSemanticsError, match="six-hour"):
        adapter.require_verified_target_definition()


def test_phm_config_is_relative_scoped_and_target_unverified() -> None:
    config_path = Path(__file__).resolve().parents[2] / "configs/datasets/phm2026.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert config["dataset"]["data_root"] == "gtc-data-experiment"
    assert config["dataset"]["excluded_repository_roots"] == ["data/Full Dataset"]
    assert config["include"]["experiments"]["EXP-A"]["runs"] == [1, 2, 3, 4, 5]
    assert config["target"]["status"] == "unverified"
    assert config["target"]["enabled"] is False
    assert config["target"]["six_hour_interpretation"] is None


def test_sensor_path_classification_and_attributes_are_adapter_owned(
    adapter: PHM2026Adapter,
) -> None:
    assert adapter.classify_sensor_path("/Vibration/Accel 1") == "vibration"
    assert adapter.classify_sensor_path("/Context/PAU Speed") == "operating_context"
    assert adapter.classify_sensor_path("/CI_4s/FM4") == "condition_indicator"
    assert adapter.classify_sensor_path("/Unmapped/Value") == "unknown"
    assert "wf_increment" in adapter.sensor_attribute_aliases("sampling_interval")


def test_sensor_timestamp_requires_explicit_timezone(adapter: PHM2026Adapter) -> None:
    assert adapter.parse_sensor_timestamp("2026-01-02T03:04:05Z") is not None
    assert adapter.parse_sensor_timestamp("2026-01-02T03:04:05+02:00") is not None
    assert adapter.parse_sensor_timestamp("2026-01-02T03:04:05") is None
    assert adapter.parse_sensor_timestamp(b"not-a-time") is None


def test_image_identity_preserves_win_local_naive_timestamp(
    adapter: PHM2026Adapter,
) -> None:
    identity = adapter.parse_image_identity(
        "photos/EXP-A/Exp-A_Photos_Run-1.zip",
        archive_member=("Run-1/Tooth 2/WIN_20240911_16_22_30_Pro (2).jpg"),
    )
    assert identity.experiment == "EXP-A"
    assert identity.run == 1
    assert identity.tooth_id == "2"
    assert identity.image_role == "camera_sequence"
    assert identity.timestamp_utc is None
    assert identity.timestamp_local_naive is not None
    assert identity.timestamp_local_naive.isoformat() == "2024-09-11T16:22:30"
    assert identity.timestamp_status == "timezone_unknown"
    assert identity.timestamp_clock_domain == "camera_local_timezone_unknown"
    assert identity.raw_sequence_token == "WIN_20240911_16_22_30_Pro (2)"


def test_image_identity_groups_archive_and_keeps_canonical_tooth(
    adapter: PHM2026Adapter,
) -> None:
    first = adapter.parse_image_identity(
        "photos/EXP-F/Exp-F_Photos_Pre-Run.zip",
        archive_member="Pre-Run/All Teeth/Tooth 01.jpg",
    )
    second = adapter.parse_image_identity(
        "photos/EXP-F/Exp-F_Photos_Pre-Run.zip",
        archive_member="Pre-Run/All Teeth/Tooth 02.jpg",
    )
    assert first.inspection_id == second.inspection_id
    assert first.inspection_id_source == "outer_photo_archive"
    assert first.inspection_stage == "pre_run"
    assert first.tooth_id == "1"
    assert first.image_role == "canonical_tooth"
    assert first.timestamp_status == "missing"
    assert first.timestamp_clock_domain is None
