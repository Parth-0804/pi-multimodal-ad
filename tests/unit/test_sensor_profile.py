from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
import json
from pathlib import Path
import zipfile

import h5py
import numpy as np
import pandas as pd
import pytest

from pi_multimodal_ad.datasets import PHM2026Adapter
from pi_multimodal_ad.profiling.sensors import (
    SensorProfileOptions,
    SensorProfileResult,
    SensorSource,
    _full_blocks,
    build_hdf5_schema,
    profile_hdf5_file,
    profile_sensor_sources,
    write_sensor_run,
)
from pi_multimodal_ad.utils import create_run_context, load_yaml_config

UTC = timezone.utc


def _source(
    tmp_path: Path,
    *,
    archive_path: Path | None = None,
    outer_member_path: str = "Run-1/Dyno Gear233Run1_00000.hdf5",
    authoritative_run: int | None = 1,
    internal_run_token: int | None = 1,
    compressed_size_bytes: int = 1,
    uncompressed_size_bytes: int = 1,
    crc32: str = "00000000",
    modality: str = "high_frequency",
    is_nested_container: bool = False,
) -> SensorSource:
    path = archive_path or tmp_path / "unused.zip"
    return SensorSource(
        inventory_member_id="archive_member_synthetic",
        archive_asset_id="asset_synthetic",
        archive_relative_path=(
            "high_frequency/EXP A/Exp-A_HDF5_Run-1.zip"
            if modality == "high_frequency"
            else "low-frequency (CIs)/Exp-A_HDF5_CI.zip"
        ),
        archive_path=path,
        outer_member_path=outer_member_path,
        modality=modality,
        experiment="EXP-A",
        authoritative_outer_run=authoritative_run,
        nested_archive_run_token=None,
        inventory_internal_run_token=internal_run_token,
        inventory_internal_run_matches_outer=True,
        inventory_internal_run_parse_error=None,
        member_occurrence=1,
        compressed_size_bytes=compressed_size_bytes,
        uncompressed_size_bytes=uncompressed_size_bytes,
        crc32=crc32,
        is_nested_container=is_nested_container,
    )


def _create_dataset(
    handle: h5py.File, path: str, *args: object, **kwargs: object
) -> h5py.Dataset:
    group_path, name = path.rsplit("/", 1)
    group = handle.require_group(group_path or "/")
    return group.create_dataset(name, *args, **kwargs)


def _profile_file(
    path: Path,
    *,
    source: SensorSource,
    options: SensorProfileOptions,
) -> tuple[dict[str, dict[str, object]], dict[str, object], list[object]]:
    rows, member, issues = profile_hdf5_file(
        path,
        source=source,
        nested_member_path=None,
        materialized_bytes=path.stat().st_size,
        adapter=PHM2026Adapter(),
        options=options,
    )
    return {str(row["hdf5_path"]): row for row in rows}, member, issues


def test_metadata_profile_preserves_shapes_roles_attributes_and_evidence(
    tmp_path: Path,
) -> None:
    hdf5_path = tmp_path / "metadata.hdf5"
    with h5py.File(hdf5_path, "w") as handle:
        acceleration = _create_dataset(
            handle,
            "/Vibration/Accel 1",
            data=np.arange(12, dtype=">f4").reshape(6, 2),
            chunks=(3, 2),
            compression="gzip",
        )
        acceleration.attrs["unit_string"] = "g"
        acceleration.attrs["wf_increment"] = 0.25
        acceleration.attrs["wf_start_time"] = "2026-01-02T03:04:05Z"
        _create_dataset(
            handle,
            "/Context/Temperature",
            data=np.asarray([20.0, 21.0], dtype=np.float32),
        )
        _create_dataset(handle, "/Unmapped/Value", data=np.asarray([1, 2, 3]))

    source = _source(
        tmp_path,
        outer_member_path="Run-1/Dyno Gear233Run2_00000.hdf5",
        internal_run_token=2,
    )
    options = SensorProfileOptions(
        mode="metadata",
        expected_paths={
            "high_frequency": {"required": ["/Vibration/Accel 1", "/Vibration/Accel 2"]}
        },
    )
    rows, member, issues = _profile_file(hdf5_path, source=source, options=options)

    acceleration = rows["/Vibration/Accel 1"]
    assert json.loads(str(acceleration["shape_json"])) == [6, 2]
    assert acceleration["rank"] == 2
    assert acceleration["dtype"] == ">f4"
    assert acceleration["byte_order"] == ">"
    assert json.loads(str(acceleration["chunks_json"])) == [3, 2]
    assert acceleration["compression"] == "gzip"
    assert json.loads(str(acceleration["attributes_json"]))["unit_string"] == "g"
    assert acceleration["channel_role"] == "vibration"
    assert acceleration["unit"] == "g"
    assert acceleration["sample_count"] == 6
    assert acceleration["channel_count"] == 2
    assert acceleration["sampling_rate_hz"] == pytest.approx(4.0)
    assert acceleration["sampling_rate_evidence"] == (
        "derived:1/dataset_attribute:wf_increment"
    )
    assert acceleration["duration_seconds"] == pytest.approx(1.5)
    assert acceleration["duration_evidence"] == "sample_count/sampling_rate_hz"
    assert acceleration["start_timestamp_utc"] == "2026-01-02T03:04:05+00:00"
    assert acceleration["end_timestamp_utc"] == "2026-01-02T03:04:06.250000+00:00"
    assert acceleration["statistics_scope"] == "metadata_only"
    assert acceleration["minimum"] is None
    assert acceleration["nan_count"] is None
    assert acceleration["constant_array"] is None
    assert acceleration["empty_array"] is False

    assert rows["/Context/Temperature"]["channel_role"] == "operating_context"
    assert rows["/Context/Temperature"]["rank"] == 1
    assert rows["/Unmapped/Value"]["channel_role"] == "unknown"
    assert member["run"] == 1
    assert member["authoritative_outer_run"] == 1
    assert member["internal_run_token"] == 2
    assert member["internal_run_matches_authoritative"] is False
    assert json.loads(str(member["missing_expected_paths_json"])) == [
        "/Vibration/Accel 2"
    ]
    assert {getattr(issue, "code") for issue in issues} == {
        "internal_run_conflict",
        "missing_expected_paths",
    }
    assert len({row["file_schema_id"] for row in rows.values()}) == 1


def test_phm_role_classification_covers_ci_variants_and_preserves_unknowns(
    tmp_path: Path,
) -> None:
    hdf5_path = tmp_path / "roles.h5"
    with h5py.File(hdf5_path, "w") as handle:
        for path in (
            "/CI/FM4",
            "/CI_4s/NA4",
            "/Oil/Particle Count",
            "/Environment/Ambient Temperature",
            "/Timestamp/UTC",
            "/VendorSpecific/Value",
        ):
            _create_dataset(handle, path, data=np.asarray([1.0]))

    rows, member, issues = _profile_file(
        hdf5_path,
        source=_source(tmp_path),
        options=SensorProfileOptions(mode="metadata"),
    )

    assert member["status"] == "ok"
    assert not issues
    assert rows["/CI/FM4"]["channel_role"] == "condition_indicator"
    assert rows["/CI_4s/NA4"]["channel_role"] == "condition_indicator"
    assert rows["/Oil/Particle Count"]["channel_role"] == "oil"
    assert rows["/Environment/Ambient Temperature"]["channel_role"] == "environment"
    assert rows["/Timestamp/UTC"]["channel_role"] == "timestamp"
    assert rows["/VendorSpecific/Value"]["channel_role"] == "unknown"


def test_sampled_statistics_are_bounded_and_deterministic(tmp_path: Path) -> None:
    hdf5_path = tmp_path / "sampled.h5"
    with h5py.File(hdf5_path, "w") as handle:
        _create_dataset(
            handle,
            "/Vibration/Accel 1",
            data=np.arange(1000, dtype=np.float64),
        )

    source = _source(tmp_path)

    def sampled(seed: int) -> dict[str, object]:
        rows, member, issues = _profile_file(
            hdf5_path,
            source=source,
            options=SensorProfileOptions(
                mode="sampled",
                seed=seed,
                sample_points=17,
                max_block_bytes=128,
            ),
        )
        assert member["status"] == "ok"
        assert not issues
        return rows["/Vibration/Accel 1"]

    first = sampled(123)
    repeated = sampled(123)
    different_seed = sampled(124)
    fields = (
        "sampled_value_count",
        "finite_count",
        "nan_count",
        "inf_count",
        "minimum",
        "maximum",
        "mean",
        "standard_deviation",
        "constant_array",
    )
    assert {field: first[field] for field in fields} == {
        field: repeated[field] for field in fields
    }
    assert first["statistics_scope"] == "sampled"
    assert first["sampled_value_count"] == 17
    assert first["finite_count"] == 17
    assert first["mean"] != different_seed["mean"]


class _CountingDataset:
    def __init__(self) -> None:
        self.values = np.arange(20, dtype=np.float64)
        self.shape = self.values.shape
        self.size = self.values.size
        self.dtype = self.values.dtype
        self.read_count = 0

    def __getitem__(self, key: object) -> np.ndarray:
        self.read_count += 1
        return self.values[key]


def test_full_block_iterator_is_lazy_and_respects_the_byte_budget() -> None:
    dataset = _CountingDataset()
    blocks = _full_blocks(dataset, max_block_bytes=32)  # type: ignore[arg-type]
    assert isinstance(blocks, Iterator)
    assert iter(blocks) is blocks
    assert dataset.read_count == 0
    first = next(blocks)
    assert dataset.read_count == 1
    assert first.nbytes <= 32
    remaining = list(blocks)
    assert all(block.nbytes <= 32 for block in remaining)
    np.testing.assert_array_equal(np.concatenate([first, *remaining]), dataset.values)


def test_full_statistics_are_exact_for_multidimensional_scalar_empty_and_nonfinite(
    tmp_path: Path,
) -> None:
    hdf5_path = tmp_path / "full.h5"
    mixed = np.asarray(
        [
            1.0,
            np.nan,
            np.inf,
            -np.inf,
            3.0,
            3.0,
            3.0,
            3.0,
            5.0,
            5.0,
            5.0,
            5.0,
            7.0,
            7.0,
            7.0,
            7.0,
        ],
        dtype=np.float64,
    ).reshape(2, 8)
    with h5py.File(hdf5_path, "w") as handle:
        _create_dataset(handle, "/Vibration/Mixed", data=mixed)
        _create_dataset(handle, "/Context/Constant", data=np.full(9, 4.0))
        _create_dataset(handle, "/Context/Scalar", data=np.asarray(7.0))
        _create_dataset(handle, "/Context/Empty", shape=(0,), dtype=np.float64)

    rows, member, issues = _profile_file(
        hdf5_path,
        source=_source(tmp_path),
        options=SensorProfileOptions(mode="full", max_block_bytes=24),
    )
    assert member["status"] == "ok"
    assert not issues

    mixed_row = rows["/Vibration/Mixed"]
    finite = mixed[np.isfinite(mixed)]
    assert mixed_row["statistics_scope"] == "full"
    assert mixed_row["sampled_value_count"] == mixed.size
    assert mixed_row["finite_count"] == finite.size
    assert mixed_row["nan_count"] == 1
    assert mixed_row["inf_count"] == 2
    assert mixed_row["minimum"] == pytest.approx(float(finite.min()))
    assert mixed_row["maximum"] == pytest.approx(float(finite.max()))
    assert mixed_row["mean"] == pytest.approx(float(finite.mean()))
    assert mixed_row["standard_deviation"] == pytest.approx(float(finite.std()))
    assert mixed_row["constant_array"] is False

    constant = rows["/Context/Constant"]
    assert constant["statistics_scope"] == "full"
    assert constant["constant_array"] is True
    assert constant["mean"] == pytest.approx(4.0)
    assert constant["standard_deviation"] == pytest.approx(0.0)

    scalar = rows["/Context/Scalar"]
    assert json.loads(str(scalar["shape_json"])) == []
    assert scalar["rank"] == 0
    assert scalar["sample_count"] == 1
    assert scalar["channel_count"] == 1
    assert scalar["constant_array"] is True
    assert scalar["mean"] == pytest.approx(7.0)

    empty = rows["/Context/Empty"]
    assert empty["empty_array"] is True
    assert empty["statistics_scope"] == "full"
    assert empty["sampled_value_count"] == 0
    assert empty["finite_count"] == 0
    assert empty["nan_count"] == 0
    assert empty["inf_count"] == 0
    assert empty["constant_array"] is None


def _write_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member, payload in members.items():
            archive.writestr(member, payload)


def _source_from_zip(
    archive_path: Path, member_path: str, *, tmp_path: Path
) -> SensorSource:
    with zipfile.ZipFile(archive_path, "r") as archive:
        info = archive.getinfo(member_path)
    return _source(
        tmp_path,
        archive_path=archive_path,
        outer_member_path=member_path,
        compressed_size_bytes=info.compress_size,
        uncompressed_size_bytes=info.file_size,
        crc32=f"{info.CRC:08x}",
    )


def test_corrupt_member_is_recorded_and_later_member_continues_with_cleanup(
    tmp_path: Path,
) -> None:
    valid_hdf5 = tmp_path / "valid.h5"
    with h5py.File(valid_hdf5, "w") as handle:
        _create_dataset(handle, "/Vibration/Accel 1", data=np.asarray([1.0, 2.0]))
    archive_path = tmp_path / "sources.zip"
    members = {
        "Run-1/Dyno Gear233Run1_00000.hdf5": b"not-an-hdf5-file",
        "Run-1/Dyno Gear233Run1_00001.hdf5": valid_hdf5.read_bytes(),
    }
    _write_zip(archive_path, members)
    sources = [
        _source_from_zip(archive_path, member, tmp_path=tmp_path) for member in members
    ]
    temp_root = tmp_path / "temporary"
    temp_root.mkdir()

    result = profile_sensor_sources(
        sources,
        adapter=PHM2026Adapter(),
        options=SensorProfileOptions(mode="metadata", temp_root=temp_root),
    )

    assert [row["status"] for row in result.hdf5_members] == ["error", "ok"]
    assert len(result.sensors) == 1
    assert result.sensors[0]["hdf5_path"] == "/Vibration/Accel 1"
    assert any(issue.code == "unreadable_hdf5_member" for issue in result.issues)
    assert not list(temp_root.glob("pi_multimodal_archive_*"))


def test_schema_variations_and_csv_parquet_writer_are_consistent(
    tmp_path: Path,
) -> None:
    hdf5_path = tmp_path / "writer.h5"
    with h5py.File(hdf5_path, "w") as handle:
        signal = _create_dataset(
            handle,
            "/Vibration/Accel 1",
            data=np.asarray([1.0, 2.0, 3.0], dtype=np.float32),
        )
        signal.attrs["sampling_rate"] = 10.0
    rows, member, issues = profile_hdf5_file(
        hdf5_path,
        source=_source(tmp_path),
        nested_member_path=None,
        materialized_bytes=hdf5_path.stat().st_size,
        adapter=PHM2026Adapter(),
        options=SensorProfileOptions(mode="metadata"),
    )
    variant = dict(rows[0])
    variant.update(
        {
            "sensor_id": "sensor_profile_variant",
            "hdf5_member_id": "hdf5_member_variant",
            "shape_json": "[3,2]",
            "dtype": "float64",
            "sampling_rate_hz": 20.0,
            "file_schema_id": "hdf5_file_schema_variant",
        }
    )
    schema = build_hdf5_schema([rows[0], variant])
    path_schema = schema["dataset_paths"]["/Vibration/Accel 1"]
    assert path_schema["shapes"] == {"[3,2]": 1, "[3]": 1}
    assert path_schema["dtypes"] == {"float32": 1, "float64": 1}
    assert path_schema["sampling_rates_hz"] == {"10.0": 1, "20.0": 1}
    assert len(schema["file_schema_counts"]) == 2

    repository = tmp_path / "repository"
    config_path = repository / "configs/experiment.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "schema_version: '1.0.0'\nstudy: synthetic_sensor_profile\n",
        encoding="utf-8",
    )
    config = load_yaml_config(config_path, repository_root=repository)
    run = create_run_context(
        study="synthetic_sensor_profile",
        output_root=repository / "runs/synthetic_sensor_profile",
        config=config,
        seed=17,
        command=("scripts/profile_sensors.py", "--mode", "metadata"),
        input_roots=("tests/synthetic",),
        now=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        package_names=(),
        source_runs=(
            {
                "task": "D1.1",
                "run_id": "synthetic-source-run",
                "artifact_sha256": "0" * 64,
            },
        ),
    )
    result = SensorProfileResult(
        sensors=[rows[0], variant],
        hdf5_members=[member],
        issues=issues,
        mode="metadata",
        discovered_source_count=1,
        selected_source_count=1,
        limited=True,
        elapsed_seconds=0.25,
    )
    artifacts = write_sensor_run(
        result,
        run=run,
        resolved_config={"schema_version": "1.0.0", "mode": "metadata"},
        input_manifest=[{"source": "synthetic-only"}],
    )

    sensor_csv = pd.read_csv(run.run_directory / "tables/sensor_profile.csv")
    sensor_parquet = pd.read_parquet(
        run.run_directory / "tables/sensor_profile.parquet"
    )
    assert list(sensor_csv.columns) == list(sensor_parquet.columns)
    assert len(sensor_csv) == len(sensor_parquet) == 2
    assert sensor_csv["hdf5_path"].tolist() == sensor_parquet["hdf5_path"].tolist()
    generated_schema = json.loads(
        (run.run_directory / "reports/hdf5_schema.json").read_text(encoding="utf-8")
    )
    assert generated_schema == schema
    output_manifest = json.loads(
        (run.run_directory / "manifests/outputs.json").read_text(encoding="utf-8")
    )
    roles = {artifact["role"] for artifact in output_manifest["artifacts"]}
    assert {
        "sensor_profile_csv",
        "sensor_profile_parquet",
        "hdf5_schema",
        "sensor_summary_markdown",
        "run_provenance",
    } <= roles
    assert len(artifacts) == len(output_manifest["artifacts"])
    provenance = json.loads(
        (run.run_directory / "provenance.json").read_text(encoding="utf-8")
    )
    assert provenance["source_runs"][0]["run_id"] == "synthetic-source-run"
