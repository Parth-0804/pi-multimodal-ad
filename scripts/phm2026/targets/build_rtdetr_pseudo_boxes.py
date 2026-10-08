#!/usr/bin/env python3
"""Replay the pinned v2 masks and build traceable RT-DETR pseudo-box data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pi_multimodal_ad.profiling.images import load_image_sources  # noqa: E402
from pi_multimodal_ad.targets.image_damage import ImageDamageOptions  # noqa: E402
from pi_multimodal_ad.targets.pseudo_boxes import (  # noqa: E402
    PSEUDO_BOX_ALGORITHM_VERSION,
    build_pseudo_box_dataset,
    validate_pseudo_box_result,
    write_pseudo_box_run,
)
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)


def _preflight(root: Path) -> dict[str, object]:
    usage = shutil.disk_usage(root)
    zips = tuple((root / "gtc-data-experiment").rglob("*.zip"))
    runs = root / "runs"
    return {
        "disk_total_bytes": usage.total,
        "disk_used_bytes": usage.used,
        "disk_free_bytes": usage.free,
        "raw_zip_count": len(zips),
        "raw_zip_bytes": sum(path.stat().st_size for path in zips),
        "existing_runs_bytes": sum(
            path.stat().st_size for path in runs.rglob("*") if path.is_file()
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_rtdetr_pseudo_boxes.yaml"
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
        target = load_pinned_run(
            config.repository_root,
            specs["target"],
            required_artifacts=(
                "config/resolved_config.yaml",
                "tables/image_manifest.parquet",
                "tables/per_tooth_damage.parquet",
                "tables/run_damage_targets.parquet",
                "reports/target_quality_report.json",
            ),
        )
        model_dataset = load_pinned_run(
            config.repository_root,
            specs["model_dataset"],
            required_artifacts=(
                "tables/model_sample_manifest.parquet",
                "tables/split_manifest.parquet",
                "reports/split_validation.json",
            ),
        )
        image_manifest = pd.read_parquet(
            target.artifact_path("tables/image_manifest.parquet")
        )
        samples = pd.read_parquet(
            model_dataset.artifact_path("tables/model_sample_manifest.parquet")
        )
        split_manifest = pd.read_parquet(
            model_dataset.artifact_path("tables/split_manifest.parquet")
        )
        split_validation = json.loads(
            model_dataset.artifact_path("reports/split_validation.json").read_text()
        )
        target_config = yaml.safe_load(
            target.artifact_path("config/resolved_config.yaml").read_text()
        )
        expected = data["expected"]
        if len(image_manifest) != int(expected["source_images"]):
            raise ConfigError("source image count differs from the pinned R4 contract")
        if len(samples) != int(expected["model_samples"]):
            raise ConfigError("model sample count differs from the pinned R4 contract")
        joined = samples[["sample_id", "split"]].merge(
            split_manifest[["sample_id", "split"]],
            on="sample_id",
            suffixes=("_sample", "_persisted"),
            validate="one_to_one",
        )
        if len(joined) != len(samples) or not joined.split_sample.equals(
            joined.split_persisted
        ):
            raise ConfigError("model samples differ from the persisted split manifest")
        actual_splits = samples.groupby("split").size().astype(int).to_dict()
        if actual_splits != {
            str(key): int(value) for key, value in expected["split_counts"].items()
        }:
            raise ConfigError(f"unexpected split counts: {actual_splits}")
        if not split_validation.get("valid") or split_validation.get(
            "random_split_used"
        ):
            raise ConfigError(
                "upstream split validation is not a deterministic experiment split"
            )
        if data["pseudo_boxes"]["algorithm_version"] != PSEUDO_BOX_ALGORITHM_VERSION:
            raise ConfigError("pseudo-box algorithm version mismatch")
        preflight = _preflight(config.repository_root)
        minimum_free = int(data["storage_limits"]["minimum_free_bytes"])
        if int(preflight["disk_free_bytes"]) < minimum_free:
            raise ConfigError("free disk is below the configured 50 GiB floor")
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
        selected_sources = [
            sources_by_id[str(value)] for value in samples.source_member_id
        ]
        projected_cache = sum(source.encoded_size_bytes for source in selected_sources)
        if projected_cache > int(data["storage_limits"]["max_image_cache_bytes"]):
            raise ConfigError("projected JPEG cache exceeds 12 GiB")
        if int(preflight["disk_free_bytes"]) - projected_cache < minimum_free:
            raise ConfigError("projected cache would reduce free disk below 50 GiB")
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "source_image_count": len(image_manifest),
                        "model_sample_count": len(samples),
                        "split_counts": actual_splits,
                        "projected_cache_bytes": projected_cache,
                        "preflight": preflight,
                        "would_open_raw_images": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        measurement = target_config["image_measurement"]
        target_definition = target_config["target_definition"]
        options = ImageDamageOptions(
            roi_normalized_xyxy=tuple(measurement["roi_normalized_xyxy"]),
            clahe_clip_limit=float(measurement["clahe_clip_limit"]),
            background_sigma_pixels=float(measurement["background_sigma_pixels"]),
            residual_z_threshold=float(measurement["residual_z_threshold"]),
            gradient_z_threshold=float(measurement["gradient_z_threshold"]),
            minimum_component_fraction=float(measurement["minimum_component_fraction"]),
            damaged_tooth_threshold_pct=float(
                target_definition["damaged_tooth_threshold_pct"]
            ),
            minimum_valid_teeth=int(target_definition["minimum_valid_teeth"]),
            near_duplicate_hamming=int(measurement["near_duplicate_hamming"]),
            max_member_bytes=int(measurement["max_member_bytes"]),
            overlay_jpeg_quality=int(measurement["overlay_jpeg_quality"]),
        )
        output_root = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
        pinned = {
            "inventory": inventory,
            "target": target,
            "model_dataset": model_dataset,
        }
        source_runs = [
            {
                "name": name,
                "run_id": item.run_id,
                "directory": item.relative_directory,
                "artifacts": dict(item.verified_hashes),
            }
            for name, item in pinned.items()
        ]
        run = create_run_context(
            study=data["study"],
            output_root=output_root,
            config=config,
            seed=int(data["seed"]),
            command=[
                "scripts/targets/build_rtdetr_pseudo_boxes.py",
                *(argv or sys.argv[1:]),
            ],
            input_roots=tuple(item.relative_directory for item in pinned.values())
            + (dataset_data["dataset"]["data_root"],),
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
        result = build_pseudo_box_dataset(
            image_manifest,
            samples,
            sources_by_id,
            options=options,
            source_mask_run_id=target.run_id,
            source_mask_artifact_sha256=target.verified_hashes[
                "tables/image_manifest.parquet"
            ],
            cache_root=run.run_directory / "cache",
        )
        quality = validate_pseudo_box_result(
            result,
            expected_split_counts={
                str(key): int(value) for key, value in expected["split_counts"].items()
            },
            split_validation=split_validation,
        )
        resolved = {
            "schema_version": "1.0.0",
            "experiment_config": data,
            "source_target_measurement": target_config["image_measurement"],
            "preflight": preflight,
            "projected_cache_bytes": projected_cache,
            "execution": {
                "exp_f_used_for_parameter_selection": False,
                "raw_archives_modified": False,
                "status": quality["status"],
            },
        }
        input_manifest = [
            item.source_record(path)
            for item in pinned.values()
            for path in sorted(item.verified_hashes)
        ]
        artifacts = write_pseudo_box_run(
            result,
            quality,
            run=run,
            resolved_config=resolved,
            input_manifest=input_manifest,
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
                "quality": quality,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if quality["status"] != "BLOCKED_PSEUDO_BOX_QUALITY_GATE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
