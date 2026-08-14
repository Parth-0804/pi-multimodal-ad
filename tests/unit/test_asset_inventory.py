from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import zipfile

import pandas as pd
import pytest

from pi_multimodal_ad.datasets import PHM2026Adapter
from pi_multimodal_ad.profiling import (
    build_inventory_plan,
    discover_inventory_paths,
    profile_asset_inventory,
    write_inventory_run,
)
from pi_multimodal_ad.utils import ConfigError, create_run_context, load_yaml_config


def _fake_repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    root.mkdir()
    (root / ".git").mkdir()
    (root / "AGENTS.md").write_text("synthetic instructions\n", encoding="utf-8")
    (root / "synthetic_raw/high_frequency/EXP A").mkdir(parents=True)
    return root


def _write_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)


def _write_dataset_config(root: Path, *, runs: str = "[1, 2]") -> Path:
    path = root / "dataset.yaml"
    path.write_text(
        "\n".join(
            [
                "schema_version: '1.0.0'",
                "dataset:",
                "  name: phm2026",
                "  data_root: synthetic_raw",
                "  excluded_repository_roots: [data/Full Dataset]",
                "include:",
                "  experiments:",
                f"    EXP-A: {{runs: {runs}}}",
                "  modality_roots:",
                "    high_frequency: [high_frequency/EXP A]",
                "  file_extensions: [.zip]",
                "  expectation_mode_by_modality:",
                "    high_frequency: runs",
                "exclude:",
                "  path_globs: ['**/*.part']",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _plan(root: Path, *, runs: str = "[1, 2]"):
    config = load_yaml_config(
        _write_dataset_config(root, runs=runs), repository_root=root
    )
    return config, build_inventory_plan(config)


def test_inventory_profiles_central_directory_and_duplicate_evidence(
    tmp_path: Path,
) -> None:
    root = _fake_repository(tmp_path)
    archive_root = root / "synthetic_raw/high_frequency/EXP A"
    fixture = Path(__file__).resolve().parents[1] / "fixtures/synthetic_multimodal"
    repeated = (fixture / "records.json").read_bytes()
    _write_zip(
        archive_root / "Exp-A_HDF5_Run-1.zip",
        {"run1/sensor.h5": repeated, "run1/readme.txt": b"synthetic"},
    )
    _write_zip(
        archive_root / "Exp-A_HDF5_Run-2.zip",
        {"run2/sensor.h5": repeated},
    )
    config, plan = _plan(root)
    discovered, discovery_issues = discover_inventory_paths(plan)
    assert not discovery_issues
    assert [asset.relative_path for asset in discovered] == [
        "high_frequency/EXP A/Exp-A_HDF5_Run-1.zip",
        "high_frequency/EXP A/Exp-A_HDF5_Run-2.zip",
    ]
    result = profile_asset_inventory(plan, PHM2026Adapter())
    summary = result.summary()
    assert summary["profiled_file_count"] == 2
    assert summary["archive_member_count"] == 3
    assert summary["unreadable_file_count"] == 0
    assert summary["missing_expected_count"] == 0
    duplicate_rows = [
        row for row in result.members if row["crc_size_duplicate_count"] == 2
    ]
    assert len(duplicate_rows) == 2
    assert {row["duplicate_evidence"] for row in duplicate_rows} == {
        "zip_crc32+uncompressed_size"
    }
    assert all(row["checksum_algorithm"] == "zip_crc32" for row in result.members)
    assert all(row["central_directory_sha256"] for row in result.archives)
    assert config.relative_path == "dataset.yaml"


def test_inventory_reports_unreadable_empty_unexpected_and_missing(
    tmp_path: Path,
) -> None:
    root = _fake_repository(tmp_path)
    archive_root = root / "synthetic_raw/high_frequency/EXP A"
    (archive_root / "Exp-A_HDF5_Run-1.zip").write_bytes(b"not-a-zip")
    (archive_root / "Exp-A_HDF5_Run-3.zip").write_bytes(b"")
    (archive_root / "unexpected.txt").write_text("synthetic", encoding="utf-8")
    _, plan = _plan(root, runs="[1, 2]")
    result = profile_asset_inventory(plan, PHM2026Adapter())
    codes = {issue.code for issue in result.issues}
    assert {
        "unreadable_archive",
        "empty_file",
        "unexpected_extension",
        "asset_identity_unparsed",
        "missing_expected_scope",
    }.issubset(codes)
    assert result.missing_expected == [
        {
            "schema_version": "1.0.0",
            "modality": "high_frequency",
            "experiment": "EXP-A",
            "run": 2,
            "expectation_mode": "runs",
        }
    ]


def test_inventory_limit_does_not_claim_missing_scope(tmp_path: Path) -> None:
    root = _fake_repository(tmp_path)
    archive_root = root / "synthetic_raw/high_frequency/EXP A"
    _write_zip(archive_root / "Exp-A_HDF5_Run-1.zip", {"sensor.h5": b"one"})
    _write_zip(archive_root / "Exp-A_HDF5_Run-2.zip", {"sensor.h5": b"two"})
    _, plan = _plan(root)
    result = profile_asset_inventory(plan, PHM2026Adapter(), limit=1)
    assert result.limited
    assert result.discovered_count == 2
    assert len(result.archives) == 1
    assert not result.missing_expected


def test_inventory_records_member_run_conflicts_without_aborting(
    tmp_path: Path,
) -> None:
    root = _fake_repository(tmp_path)
    archive_path = root / "synthetic_raw/high_frequency/EXP A/Exp-A_HDF5_Run-1.zip"
    _write_zip(
        archive_path,
        {
            "outer-run-1/GearRun-2_sensor.h5": b"different run token",
            "outer-run-1/GearRun-1_Run-2_sensor.h5": b"conflicting tokens",
        },
    )
    _, plan = _plan(root, runs="[1]")

    result = profile_asset_inventory(plan, PHM2026Adapter())

    assert {issue.code for issue in result.issues} == {
        "member_archive_run_conflict",
        "member_run_unparsed",
    }
    by_name = {row["archive_member"]: row for row in result.members}
    mismatch = by_name["outer-run-1/GearRun-2_sensor.h5"]
    assert mismatch["run"] == 1
    assert mismatch["member_run_token"] == 2
    assert mismatch["member_run_matches_archive"] is False
    unparsed = by_name["outer-run-1/GearRun-1_Run-2_sensor.h5"]
    assert unparsed["run"] == 1
    assert unparsed["member_run_token"] is None
    assert "conflicting run tokens" in unparsed["member_run_parse_error"]


def test_inventory_rejects_excluded_data_root_override(tmp_path: Path) -> None:
    root = _fake_repository(tmp_path)
    (root / "data/Full Dataset").mkdir(parents=True)
    config = load_yaml_config(_write_dataset_config(root), repository_root=root)
    with pytest.raises(ConfigError, match="excluded"):
        build_inventory_plan(config, data_root_override="data/Full Dataset")


def test_inventory_writes_versioned_csv_parquet_reports_and_provenance(
    tmp_path: Path,
) -> None:
    root = _fake_repository(tmp_path)
    archive_path = root / "synthetic_raw/high_frequency/EXP A/Exp-A_HDF5_Run-1.zip"
    _write_zip(archive_path, {"run1/sensor.h5": b"synthetic"})
    config, plan = _plan(root, runs="[1]")
    result = profile_asset_inventory(plan, PHM2026Adapter())
    run = create_run_context(
        study="synthetic_inventory",
        output_root=root / "runs/synthetic_inventory",
        config=config,
        seed=11,
        command=("profile_dataset.py", "--limit", "1"),
        input_roots=("synthetic_raw",),
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    artifacts = write_inventory_run(
        result,
        run=run,
        resolved_config=config.mutable_copy(),
        input_manifest=[{"relative_path": archive_path.name}],
    )
    assert (run.run_directory / "tables/asset_inventory.csv").is_file()
    assert (run.run_directory / "tables/archive_members.parquet").is_file()
    assert (run.run_directory / "reports/summary.md").is_file()
    assert (run.run_directory / "manifests/outputs.json").is_file()
    assert (run.run_directory / "provenance.json").is_file()
    table = pd.read_parquet(run.run_directory / "tables/asset_inventory.parquet")
    assert table.loc[0, "experiment"] == "EXP-A"
    provenance = json.loads(
        (run.run_directory / "provenance.json").read_text(encoding="utf-8")
    )
    assert provenance["seed"] == 11
    assert len(artifacts) == 10
