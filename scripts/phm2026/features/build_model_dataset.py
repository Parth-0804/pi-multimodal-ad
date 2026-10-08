#!/usr/bin/env python3
"""Build T2.2 traceability manifests and strict experiment-level splits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pi_multimodal_ad.targets.model_dataset import (  # noqa: E402
    build_image_samples,
    build_sensor_manifests,
    write_dataset_run,
)
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_model_dataset.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        specs = data["source_runs"]
        inventory = load_pinned_run(
            config.repository_root,
            specs["inventory"],
            required_artifacts=("tables/archive_members.parquet",),
        )
        target = load_pinned_run(
            config.repository_root,
            specs["target"],
            required_artifacts=(
                "tables/image_manifest.parquet",
                "tables/per_tooth_damage.parquet",
                "tables/run_damage_targets.parquet",
                "reports/target_quality_report.json",
            ),
        )
        image_manifest = pd.read_parquet(
            target.artifact_path("tables/image_manifest.parquet")
        )
        run_targets = pd.read_parquet(
            target.artifact_path("tables/run_damage_targets.parquet")
        )
        archive_members = pd.read_parquet(
            inventory.artifact_path("tables/archive_members.parquet")
        )
        samples, split, validation = build_image_samples(
            image_manifest, split_config=data["canonical_development_split"]
        )
        sensor_files, sensor_runs, minute_features = build_sensor_manifests(
            archive_members, run_targets
        )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "sensor_file_count": len(sensor_files),
                        "sensor_run_count": len(sensor_runs),
                        "image_sample_count": len(samples),
                        "split_validation": validation,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        output_root = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
        sources = [
            {
                "name": name,
                "run_id": pin.run_id,
                "directory": pin.relative_directory,
                "artifacts": dict(pin.verified_hashes),
            }
            for name, pin in (("inventory", inventory), ("target", target))
        ]
        run = create_run_context(
            study=data["study"],
            output_root=output_root,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/features/build_model_dataset.py", *(argv or sys.argv[1:])],
            input_roots=(inventory.relative_directory, target.relative_directory),
            source_runs=sources,
        )
        run.create_layout()
        excluded = samples.iloc[0:0].copy()
        artifacts = write_dataset_run(
            {
                "sensor_file_manifest": sensor_files,
                "sensor_run_manifest": sensor_runs,
                "minute_feature_table": minute_features,
                "model_sample_manifest": samples,
                "excluded_samples": excluded,
                "split_manifest": split,
            },
            split_validation=validation,
            run=run,
            resolved_config=data,
            input_manifest=[
                pin.source_record(path)
                for pin in (inventory, target)
                for path in sorted(pin.verified_hashes)
            ],
        )
    except (ConfigError, KeyError, OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "sensor_file_count": len(sensor_files),
                "sensor_run_count": len(sensor_runs),
                "image_sample_count": len(samples),
                "split_validation": validation,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
