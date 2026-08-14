from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from pi_multimodal_ad.data_contracts import (
    AssetRecord,
    ContractValidationError,
    ImageRecord,
    SampleRecord,
    SensorRecord,
    SensorWindowReference,
    TargetRecord,
    deterministic_id,
    record_to_dict,
)

UTC = timezone.utc


def _asset(**overrides: object) -> AssetRecord:
    values: dict[str, object] = {
        "dataset": "synthetic_dataset",
        "relative_path": "sensors/run_1.zip",
        "asset_kind": "archive",
        "modality": "sensor",
        "experiment": "SYNTH-1",
        "run": 1,
        "size_bytes": 123,
    }
    values.update(overrides)
    return AssetRecord(**values)  # type: ignore[arg-type]


def test_deterministic_id_is_mapping_order_independent() -> None:
    first = deterministic_id("test", {"b": [2, 3], "a": 1})
    second = deterministic_id("test", {"a": 1, "b": [2, 3]})
    assert first == second
    assert first.startswith("test_")


def test_asset_id_uses_identity_not_late_metadata() -> None:
    without_checksum = _asset()
    with_checksum = _asset(checksum_algorithm="sha256", checksum="abc123")
    assert without_checksum.asset_id == with_checksum.asset_id


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        ({"relative_path": "/absolute/file.zip"}, "relative_path"),
        ({"relative_path": "../escape.zip"}, "relative_path"),
        ({"size_bytes": -1}, "size_bytes"),
        ({"checksum_algorithm": "sha256"}, "checksum"),
    ],
)
def test_asset_validation_errors_are_field_specific(
    overrides: dict[str, object], field: str
) -> None:
    with pytest.raises(ContractValidationError) as error:
        _asset(**overrides)
    assert error.value.field == field


def test_image_record_normalizes_annotation_sequences() -> None:
    image = ImageRecord(
        asset_id=_asset().asset_id,
        width=640,
        height=480,
        channels=3,
        dtype="uint8",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        tooth_id="7",
        inspection_id="inspection-1",
        annotation_types=["image_label"],  # type: ignore[arg-type]
        annotation_refs=["labels/inspection-1.json"],  # type: ignore[arg-type]
    )
    assert image.annotation_types == ("image_label",)
    assert image.image_id.startswith("image_")


def test_sensor_record_preserves_unknown_physical_metadata() -> None:
    sensor = SensorRecord(
        asset_id=_asset().asset_id,
        hdf5_path="/Signals/Channel 1",
        shape=(0,),
        dtype="float32",
        channel_role="unknown",
    )
    assert sensor.sampling_rate_hz is None
    assert sensor.duration_seconds is None
    assert sensor.unit is None


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), "10"])
def test_sensor_sampling_rate_must_be_a_finite_positive_number(value: object) -> None:
    with pytest.raises(ContractValidationError):
        SensorRecord(
            asset_id=_asset().asset_id,
            hdf5_path="/Signals/Channel 1",
            shape=(10,),
            dtype="float32",
            channel_role="vibration",
            sampling_rate_hz=value,  # type: ignore[arg-type]
        )


def test_target_requires_timezone_and_non_negative_horizon() -> None:
    with pytest.raises(ContractValidationError, match="explicit timezone"):
        TargetRecord(
            target_name="synthetic_value",
            physical_meaning="Synthetic scalar for a unit test",
            unit="arbitrary_unit",
            timestamp=datetime(2026, 1, 1),
            horizon_seconds=0,
            source="synthetic metadata",
            computation_version="test-v1",
        )


def test_sample_id_is_stable_for_group_mapping_order() -> None:
    asset = _asset()
    sensor = SensorRecord(
        asset_id=asset.asset_id,
        hdf5_path="/Signals/Channel 1",
        shape=(100,),
        dtype="float32",
        channel_role="vibration",
        sampling_rate_hz=10.0,
        duration_seconds=10.0,
    )
    cutoff = datetime(2026, 1, 2, tzinfo=UTC)
    window = SensorWindowReference(
        sensor_record_id=sensor.sensor_id,
        start_index=0,
        end_index=100,
        start_timestamp=cutoff - timedelta(seconds=10),
        end_timestamp=cutoff,
    )
    target = TargetRecord(
        target_name="synthetic_value",
        physical_meaning="Synthetic scalar for a unit test",
        unit="arbitrary_unit",
        timestamp=cutoff + timedelta(hours=1),
        horizon_seconds=3600,
        source="synthetic metadata",
        computation_version="test-v1",
    )
    first = SampleRecord(
        input_cutoff=cutoff,
        sensor_windows=(window,),
        image_record_ids=(),
        target_record_id=target.target_id,
        group_keys={"run": "1", "experiment": "SYNTH-1"},
        split_key="SYNTH-1/run-1",
    )
    second = SampleRecord(
        input_cutoff=cutoff,
        sensor_windows=(window,),
        image_record_ids=(),
        target_record_id=target.target_id,
        group_keys={"experiment": "SYNTH-1", "run": "1"},
        split_key="SYNTH-1/run-1",
    )
    assert first.sample_id == second.sample_id
    assert record_to_dict(first)["input_cutoff"].endswith("+00:00")


def test_sample_rejects_sensor_data_after_cutoff() -> None:
    cutoff = datetime(2026, 1, 2, tzinfo=UTC)
    window = SensorWindowReference(
        sensor_record_id="sensor_synthetic",
        start_timestamp=cutoff,
        end_timestamp=cutoff + timedelta(seconds=1),
    )
    with pytest.raises(ContractValidationError, match="input_cutoff"):
        SampleRecord(
            input_cutoff=cutoff,
            sensor_windows=(window,),
            image_record_ids=(),
            target_record_id="target_synthetic",
            group_keys={"experiment": "SYNTH-1"},
            split_key="SYNTH-1",
        )


def test_sample_rejects_untyped_window_reference() -> None:
    with pytest.raises(ContractValidationError, match="SensorWindowReference"):
        SampleRecord(
            input_cutoff=datetime(2026, 1, 2, tzinfo=UTC),
            sensor_windows=("not-a-window",),  # type: ignore[arg-type]
            image_record_ids=(),
            target_record_id="target_synthetic",
            group_keys={"experiment": "SYNTH-1"},
            split_key="SYNTH-1",
        )


def test_sensor_record_allows_scalar_hdf5_dataset_shape() -> None:
    sensor = SensorRecord(
        asset_id=_asset().asset_id,
        hdf5_path="/Context/Scalar",
        shape=(),
        dtype="float64",
        channel_role="operating_context",
    )
    assert sensor.shape == ()
