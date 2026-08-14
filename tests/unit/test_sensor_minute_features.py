from __future__ import annotations

from pathlib import Path
import zipfile

import h5py
import numpy as np
import pandas as pd

from pi_multimodal_ad.features.sensor_minutes import (
    ChannelSpec,
    ExtractionOptions,
    extract_minute_features,
)
from pi_multimodal_ad.preprocessing.timeseries import (
    build_run_sequences,
    collate_run_sequences,
    fit_feature_normalizer,
)


def _hdf(
    path: Path, timestamp: str | None, value: float, *, missing_ci: bool = False
) -> None:
    with h5py.File(path, "w") as handle:
        speed = handle.create_dataset("/Context/PAU Speed", data=np.arange(4) + value)
        if timestamp is not None:
            speed.attrs["wf_start_time"] = timestamp
        speed.attrs["unit_string"] = "rpm"
        if not missing_ci:
            ci = handle.create_dataset("/CI/FM4", data=np.full(4, value))
            if timestamp is not None:
                ci.attrs["wf_start_time"] = timestamp


def test_nested_extraction_orders_by_verified_timestamp_and_keeps_missing(
    tmp_path: Path,
) -> None:
    inner = tmp_path / "inner.zip"
    inputs = []
    for name, timestamp, value in (
        ("minute-b.h5", "2026-01-01T00:01:00+00:00", 2.0),
        ("minute-a.h5", "2026-01-01T00:00:00+00:00", 1.0),
        ("minute-c.h5", None, 3.0),
    ):
        path = tmp_path / name
        _hdf(path, timestamp, value, missing_ci=name == "minute-b.h5")
        inputs.append(path)
    with zipfile.ZipFile(inner, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in inputs:
            archive.write(path, arcname=path.name)
    outer = tmp_path / "outer.zip"
    with zipfile.ZipFile(outer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(inner, arcname="Exp-X_HDF5_Run-1_LF.zip")
    with zipfile.ZipFile(outer) as archive:
        info = archive.getinfo("Exp-X_HDF5_Run-1_LF.zip")
    containers = pd.DataFrame(
        [
            {
                "archive_relative_path": "outer.zip",
                "archive_member": info.filename,
                "member_file_type": "zip",
                "modality": "low_frequency",
                "experiment": "EXP-X",
                "run": 1,
                "compressed_size_bytes": info.compress_size,
                "uncompressed_size_bytes": info.file_size,
                "checksum": f"{info.CRC:08x}",
            }
        ]
    )
    targets = pd.DataFrame(
        [
            {
                "experiment": "EXP-X",
                "run": 1,
                "target_definition_version": "test",
                "target_verification_status": "synthetic",
                "raw_top3_mean_pct": 4.0,
                "causal_monotonic_top3_mean_pct": 5.0,
            }
        ]
    )
    channels = [
        ChannelSpec("rpm", "/Context/PAU Speed", "context"),
        ChannelSpec("fm4", "/CI/FM4", "condition_indicator"),
    ]
    minute, summary, evidence = extract_minute_features(
        containers,
        targets,
        data_root=tmp_path,
        channels=channels,
        split_by_experiment={"EXP-X": "train"},
        options=ExtractionOptions(max_member_bytes=1_000_000),
    )
    assert len(minute) == 3
    included = minute[minute.sequence_inclusion_status.eq("included")]
    assert included.sequence_position.tolist() == [1, 2]
    assert included.hdf5_member_path.tolist() == ["minute-a.h5", "minute-b.h5"]
    assert minute.sequence_inclusion_status.value_counts().to_dict() == {
        "included": 2,
        "excluded": 1,
    }
    assert bool(
        minute.loc[minute.hdf5_member_path.eq("minute-b.h5"), "fm4_missing"].iloc[0]
    )
    assert summary.included_minute_count.tolist() == [2]
    assert evidence[evidence.channel.eq("rpm")].unit.dropna().unique().tolist() == [
        "rpm"
    ]


def test_training_only_normalizer_and_variable_length_collation() -> None:
    rows = []
    for experiment, split, run, count, offset in (
        ("EXP-B", "train", 1, 3, 0.0),
        ("EXP-A", "validation", 1, 2, 1000.0),
    ):
        for position in range(1, count + 1):
            rows.append(
                {
                    "experiment": experiment,
                    "run": run,
                    "split": split,
                    "sequence_inclusion_status": "included",
                    "sequence_position": position,
                    "minute_id": f"{experiment}-{position}",
                    "value": offset + position,
                }
            )
    minute = pd.DataFrame(rows)
    summary = pd.DataFrame(
        [
            {
                "sequence_id": "b",
                "experiment": "EXP-B",
                "run": 1,
                "split": "train",
                "raw_top3_mean_pct": 1.0,
                "causal_monotonic_top3_mean_pct": 1.5,
            },
            {
                "sequence_id": "a",
                "experiment": "EXP-A",
                "run": 1,
                "split": "validation",
                "raw_top3_mean_pct": 2.0,
                "causal_monotonic_top3_mean_pct": 2.5,
            },
        ]
    )
    normalizer = fit_feature_normalizer(minute, feature_columns=["value"])
    assert normalizer.means == (2.0,)
    sequences = build_run_sequences(minute, summary, normalizer=normalizer)
    batch = collate_run_sequences(sequences)
    assert batch["inputs"].shape == (2, 3, 1)
    assert batch["time_mask"].sum(dim=1).tolist() == [2, 3]
    assert not batch["time_mask"][0, -1]
