#!/usr/bin/env python3
"""Derive the versioned provisional PHM image target without changing raw data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from pi_multimodal_ad.profiling.images import load_image_sources  # noqa: E402
from pi_multimodal_ad.targets.image_damage import (  # noqa: E402
    ImageDamageOptions,
    aggregate_targets,
    profile_target_images,
    write_target_run,
)
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)


def _preflight(root: Path) -> dict[str, object]:
    usage = shutil.disk_usage(root)
    raw_bytes = sum(
        path.stat().st_size for path in (root / "gtc-data-experiment").rglob("*.zip")
    )
    run_bytes = sum(
        path.stat().st_size for path in (root / "runs").rglob("*") if path.is_file()
    )
    try:
        gpu = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free,driver_version",
                "--format=csv,noheader",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        gpu = "unavailable"
    return {
        "disk_total_bytes": usage.total,
        "disk_used_bytes": usage.used,
        "disk_free_bytes": usage.free,
        "raw_zip_count": sum(1 for _ in (root / "gtc-data-experiment").rglob("*.zip")),
        "raw_zip_bytes": raw_bytes,
        "existing_runs_bytes": run_bytes,
        "gpu": gpu,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_image_target.yaml"
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
            required_artifacts=(
                "tables/asset_inventory.parquet",
                "tables/archive_members.parquet",
            ),
        )
        images = load_pinned_run(
            config.repository_root,
            specs["images"],
            required_artifacts=(
                "tables/image_profile.parquet",
                "reports/image_summary.json",
            ),
        )
        image_frame = pd.read_parquet(
            images.artifact_path("tables/image_profile.parquet")
        )
        preflight = _preflight(config.repository_root)
        limits = data["storage_limits"]
        if preflight["disk_free_bytes"] < int(limits["minimum_free_bytes"]):
            raise ConfigError("free disk is below the configured 25 GiB safety floor")
        expected_overlay = int(image_frame["encoded_size_bytes"].sum())
        if expected_overlay > int(limits["max_overlay_cache_bytes"]):
            raise ConfigError("projected overlay cache exceeds the 12 GiB limit")
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "image_count": len(image_frame),
                        "projected_overlay_upper_bound_bytes": expected_overlay,
                        "preflight": preflight,
                        "would_open_raw_images": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        dataset_config = load_yaml_config(
            data["dataset_config"], repository_root=config.repository_root
        )
        dataset_data = dataset_config.mutable_copy()
        data_root = dataset_config.resolve_repository_path(
            dataset_data["dataset"]["data_root"],
            field="dataset.data_root",
            must_exist=True,
        )
        sources = load_image_sources(
            inventory.artifact_path("tables/archive_members.parquet"),
            asset_inventory=inventory.artifact_path("tables/asset_inventory.parquet"),
            data_root=data_root,
        )
        sources_by_id = {source.source_member_id: source for source in sources}
        image_options = data["image_measurement"]
        target_options = data["target_definition"]
        options = ImageDamageOptions(
            roi_normalized_xyxy=tuple(image_options["roi_normalized_xyxy"]),
            clahe_clip_limit=float(image_options["clahe_clip_limit"]),
            background_sigma_pixels=float(image_options["background_sigma_pixels"]),
            residual_z_threshold=float(image_options["residual_z_threshold"]),
            gradient_z_threshold=float(image_options["gradient_z_threshold"]),
            minimum_component_fraction=float(
                image_options["minimum_component_fraction"]
            ),
            damaged_tooth_threshold_pct=float(
                target_options["damaged_tooth_threshold_pct"]
            ),
            minimum_valid_teeth=int(target_options["minimum_valid_teeth"]),
            near_duplicate_hamming=int(image_options["near_duplicate_hamming"]),
            max_member_bytes=int(image_options["max_member_bytes"]),
            overlay_jpeg_quality=int(image_options["overlay_jpeg_quality"]),
        )
        output_root = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
        source_runs = [
            {
                "name": name,
                "run_id": pinned.run_id,
                "directory": pinned.relative_directory,
                "artifacts": dict(pinned.verified_hashes),
            }
            for name, pinned in (("inventory", inventory), ("images", images))
        ]
        run = create_run_context(
            study=data["study"],
            output_root=output_root,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/derive_image_targets.py", *(argv or sys.argv[1:])],
            input_roots=(
                inventory.relative_directory,
                images.relative_directory,
                dataset_data["dataset"]["data_root"],
            ),
            package_names=(
                "numpy",
                "pandas",
                "pyarrow",
                "Pillow",
                "opencv-python-headless",
                "matplotlib",
                "PyYAML",
            ),
            source_runs=source_runs,
        )
        run.create_layout()
        image_rows, exclusions = profile_target_images(
            image_frame,
            sources_by_id,
            options=options,
            overlay_directory=run.run_directory / "overlays",
        )
        teeth, targets, review = aggregate_targets(image_rows, options)
        input_manifest = [
            pinned.source_record(path)
            for pinned in (inventory, images)
            for path in sorted(pinned.verified_hashes)
        ] + [
            {
                "source_type": "official_challenge_description",
                **data["official_challenge"],
            }
        ]
        artifacts = write_target_run(
            image_rows,
            teeth,
            targets,
            exclusions,
            review,
            run=run,
            resolved_config=data,
            input_manifest=input_manifest,
            preflight=preflight,
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
                "image_records": len(image_rows),
                "per_tooth_records": len(teeth),
                "run_targets": len(targets),
                "status": "PASS_PROVISIONAL_FOR_ENGINEERING_BASELINE",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
