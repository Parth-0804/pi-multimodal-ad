#!/usr/bin/env python3
"""Run bounded pretrained RT-DETR inference after a blocked PHM target gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from pi_multimodal_ad.models.rtdetr_feasibility import (  # noqa: E402
    RTDETRFeasibilityOptions,
    download_checkpoint,
    run_inference,
    select_balanced_images,
    write_rtdetr_feasibility_run,
)
from pi_multimodal_ad.profiling.images import load_image_sources  # noqa: E402
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)
from pi_multimodal_ad.utils.seeding import set_reproducible_seed  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_rtdetr_feasibility.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        source_specs = data["source_runs"]
        required = {
            "asset_inventory": (
                "tables/asset_inventory.parquet",
                "tables/archive_members.parquet",
            ),
            "image_profile": (
                "tables/image_profile.parquet",
                "reports/image_summary.json",
            ),
            "target_audit": (
                "tables/target_audit.csv",
                "reports/target_definition.md",
                "reports/target_blockers.json",
            ),
        }
        pinned = {
            name: load_pinned_run(
                config.repository_root, source_specs[name], required_artifacts=paths
            )
            for name, paths in required.items()
        }
        target_blockers = json.loads(
            pinned["target_audit"]
            .artifact_path("reports/target_blockers.json")
            .read_text(encoding="utf-8")
        )
        if (
            target_blockers.get("classification")
            != "BLOCKED_REQUIRES_PROFESSOR_OR_PROVIDER_DECISION"
            or target_blockers.get("rtdetr_regression_authorized") is not False
        ):
            raise ConfigError("fallback requires the exact blocked T2.1 classification")
        model_data = data["rtdetr"]
        options = RTDETRFeasibilityOptions(
            seed=int(data["seed"]),
            images_per_experiment=int(model_data["images_per_experiment"]),
            image_size=int(model_data["image_size"]),
            confidence_threshold=float(model_data["confidence_threshold"]),
            max_detections=int(model_data["max_detections"]),
            device=model_data["device"],
            max_member_bytes=int(model_data["max_member_bytes"]),
            checkpoint_name=str(model_data["checkpoint_name"]),
            checkpoint_url=str(model_data["checkpoint_url"]),
            checkpoint_sha256=str(model_data["checkpoint_sha256"]),
            checkpoint_size_bytes=int(model_data["checkpoint_size_bytes"]),
            trace_layers=tuple(model_data["trace_layers"]),
        )
        image_frame = pd.read_parquet(
            pinned["image_profile"].artifact_path("tables/image_profile.parquet")
        )
        selected = select_balanced_images(
            image_frame,
            images_per_experiment=options.images_per_experiment,
            seed=options.seed,
        )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "branch": model_data["branch"],
                        "target_classification": target_blockers["classification"],
                        "selected_image_count": len(selected),
                        "counts_by_experiment": selected["experiment"]
                        .value_counts()
                        .sort_index()
                        .to_dict(),
                        "checkpoint_url": options.checkpoint_url,
                        "would_download_checkpoint": True,
                        "would_open_raw_archives": False,
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
            pinned["asset_inventory"].artifact_path("tables/archive_members.parquet"),
            asset_inventory=pinned["asset_inventory"].artifact_path(
                "tables/asset_inventory.parquet"
            ),
            data_root=data_root,
        )
        sources_by_member = {source.source_member_id: source for source in sources}
        set_reproducible_seed(options.seed)
        output_root = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
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
            study=str(data["study"]),
            output_root=output_root,
            config=config,
            seed=options.seed,
            command=["scripts/training/run_rtdetr_feasibility.py", *(argv or sys.argv[1:])],
            input_roots=(
                pinned["image_profile"].relative_directory,
                pinned["asset_inventory"].relative_directory,
                pinned["target_audit"].relative_directory,
                dataset_data["dataset"]["data_root"],
            ),
            package_names=(
                "torch",
                "torchvision",
                "ultralytics",
                "opencv-python-headless",
                "numpy",
                "pandas",
                "pyarrow",
                "Pillow",
                "matplotlib",
                "PyYAML",
            ),
            source_runs=source_runs,
        )
        run.create_layout()
        checkpoint_directory = run.run_directory / "checkpoints"
        checkpoint_directory.mkdir()
        checkpoint = download_checkpoint(
            checkpoint_directory / options.checkpoint_name, options
        )
        result = run_inference(
            checkpoint=checkpoint,
            selected=selected,
            sources_by_member_id=sources_by_member,
            options=options,
        )
        input_manifest = [
            item.source_record(path)
            for item in pinned.values()
            for path in sorted(item.verified_hashes)
        ] + [
            {
                "source_type": "external_pretrained_checkpoint",
                "url": options.checkpoint_url,
                "sha256": options.checkpoint_sha256,
                "size_bytes": options.checkpoint_size_bytes,
            },
            *[
                {
                    "source_type": "selected_phm_image",
                    "image_id": row["image_id"],
                    "source_member_id": row["source_member_id"],
                    "source_relative_path": row["source_relative_path"],
                }
                for row in result.selected_images
            ],
        ]
        resolved = {
            "schema_version": "1.0.0",
            "task": "R3_feasibility_fallback",
            "target_classification": target_blockers["classification"],
            "experiment_config": data,
            "dataset_config_sha256": dataset_config.sha256,
            "execution": {
                "training_performed": False,
                "bounded_selected_images": len(selected),
                "device": result.environment["device"],
            },
        }
        artifacts = write_rtdetr_feasibility_run(
            result,
            run=run,
            checkpoint=checkpoint,
            resolved_config=resolved,
            input_manifest=input_manifest,
        )
    except (
        ConfigError,
        KeyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "summary": dict(result.summary),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
