#!/usr/bin/env python3
"""Build bounded PHM LF minute features in a versioned run."""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import shutil
import sys

import pandas as pd

from pi_multimodal_ad.features.sensor_feature_run import write_sensor_feature_run
from pi_multimodal_ad.features.sensor_minutes import (
    ChannelSpec,
    ExtractionOptions,
    extract_minute_features,
)
from pi_multimodal_ad.utils.artifacts import load_pinned_run
from pi_multimodal_ad.utils.config import ConfigError, load_yaml_config
from pi_multimodal_ad.utils.provenance import create_run_context


def _snapshot(paths: list[Path]) -> dict[str, tuple[int, int]]:
    return {
        path.as_posix(): (path.stat().st_size, path.stat().st_mtime_ns)
        for path in paths
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_sensor_features.yaml"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit-containers", type=int)
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        dataset = load_yaml_config(
            data["dataset_config"], repository_root=config.repository_root
        )
        data_root = dataset.resolve_repository_path(
            dataset.data["dataset"]["data_root"],
            field="dataset.data_root",
            must_exist=True,
        )
        if data_root.name != "gtc-data-experiment":
            raise ConfigError("sensor extraction is restricted to the PHM raw root")
        source = data["source_runs"]
        inventory = load_pinned_run(
            config.repository_root,
            source["inventory"],
            required_artifacts=(
                "tables/archive_members.parquet",
                "tables/asset_inventory.parquet",
            ),
        )
        target = load_pinned_run(
            config.repository_root,
            source["target"],
            required_artifacts=("tables/run_damage_targets.parquet",),
        )
        model_dataset = load_pinned_run(
            config.repository_root,
            source["model_dataset"],
            required_artifacts=(
                "tables/sensor_file_manifest.parquet",
                "tables/sensor_run_manifest.parquet",
                "tables/split_manifest.parquet",
            ),
        )
        members = pd.read_parquet(
            inventory.artifact_path("tables/archive_members.parquet")
        )
        targets = pd.read_parquet(
            target.artifact_path("tables/run_damage_targets.parquet")
        )
        containers = members[
            members.modality.eq("low_frequency") & members.member_file_type.eq("zip")
        ].sort_values(["experiment", "run"])
        if args.limit_containers is not None:
            if args.limit_containers <= 0:
                raise ValueError("--limit-containers must be positive")
            containers = containers.head(args.limit_containers)
            targets = targets.merge(
                containers[["experiment", "run"]], on=["experiment", "run"], how="inner"
            )
        channels = [ChannelSpec(**item) for item in data["channels"]]
        paths = sorted(
            {data_root / value for value in containers.archive_relative_path}
        )
        before = _snapshot(paths)
        free = shutil.disk_usage(config.repository_root).free
        if free < int(data["storage_limits"]["minimum_free_bytes"]):
            raise RuntimeError("minimum free-space gate is not satisfied")
        plan = {
            "container_count": int(len(containers)),
            "experiments": sorted(containers.experiment.unique().tolist()),
            "channels": [item.name for item in channels],
            "raw_high_frequency_used": False,
            "would_write": not args.dry_run,
            "free_bytes": free,
        }
        if args.dry_run:
            print(json.dumps(plan, indent=2))
            return 0
        run = create_run_context(
            study=data["study"],
            output_root=config.resolve_repository_path(
                data["output_root"], field="output_root"
            ),
            config=config,
            seed=int(data["seed"]),
            command=(
                "scripts/build_sensor_features.py",
                "--config",
                config.relative_path,
            ),
            input_roots=(dataset.data["dataset"]["data_root"],),
            package_names=(
                "numpy",
                "pandas",
                "pyarrow",
                "h5py",
                "matplotlib",
                "PyYAML",
            ),
            source_runs=(
                inventory.source_record("tables/archive_members.parquet"),
                target.source_record("tables/run_damage_targets.parquet"),
                model_dataset.source_record("tables/split_manifest.parquet"),
            ),
        )
        run.create_layout()
        extraction = data["extraction"]
        minute, summary, evidence = extract_minute_features(
            containers,
            targets,
            data_root=data_root,
            channels=channels,
            split_by_experiment=data["split_by_experiment"],
            options=ExtractionOptions(
                max_member_bytes=int(extraction["max_member_bytes"]),
                max_values_per_channel=int(extraction["max_values_per_channel"]),
                timestamp_attribute=str(extraction["timestamp_attribute"]),
            ),
        )
        after = _snapshot(paths)
        invariance = {
            "valid": before == after,
            "checked_archive_count": len(paths),
            "before": before,
            "after": after,
        }
        if not invariance["valid"]:
            raise RuntimeError("one or more raw LF archives changed")
        inputs = [
            item.source_record(path)
            for item in (inventory, target, model_dataset)
            for path in sorted(item.verified_hashes)
        ]
        artifacts = write_sensor_feature_run(
            minute,
            summary,
            evidence,
            channels=channels,
            run=run,
            resolved_config={
                "schema_version": "1.0.0",
                "experiment_config": data,
                "dataset_config_sha256": dataset.sha256,
                "execution": plan,
            },
            input_manifest=inputs,
            raw_source_invariance=invariance,
        )
    except (ConfigError, KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "minute_count": len(minute),
                "included_minute_count": int(
                    minute.sequence_inclusion_status.eq("included").sum()
                ),
                "sequence_count": len(summary),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
