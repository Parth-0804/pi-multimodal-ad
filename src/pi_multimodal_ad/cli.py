"""Thin command implementations for repository entry-point scripts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Sequence

import pandas as pd

from .datasets import PHM2026Adapter
from .profiling import (
    build_inventory_plan,
    discover_inventory_paths,
    ImageProfileOptions,
    SensorProfileOptions,
    load_image_sources,
    load_sensor_sources,
    profile_asset_inventory,
    profile_image_sources,
    profile_sensor_sources,
    select_image_sources,
    select_quality_source_ids,
    select_sensor_sources,
    write_image_run,
    write_inventory_run,
    write_sensor_run,
)
from .profiling.alignment_artifacts import write_blocker_artifacts
from .profiling.alignment_pipeline import (
    AlignmentPipelineOptions,
    build_alignment_pipeline,
    write_alignment_run,
)
from .profiling.dataset_description import (
    build_dataset_description,
    write_dataset_description_run,
)
from .utils import (
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)
from .utils.seeding import set_reproducible_seed


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def _nonnegative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "must be a finite non-negative number"
        ) from exc
    if not math.isfinite(parsed) or parsed < 0:
        raise argparse.ArgumentTypeError("must be a finite non-negative number")
    return parsed


def _profile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="profile_dataset.py",
        description=(
            "Inventory PHM filesystem metadata and ZIP central directories without "
            "extracting or reading archive-member payloads."
        ),
    )
    parser.add_argument(
        "--config",
        default="configs/experiments/phm2026_dataset_description.yaml",
        help="repository-relative dataset-description experiment YAML",
    )
    parser.add_argument(
        "--output-dir",
        help="repository-relative versioned-run parent; overrides the config",
    )
    parser.add_argument(
        "--data-root",
        help="repository-relative PHM data root override",
    )
    parser.add_argument("--limit", type=_positive_int, help="profile at most N files")
    parser.add_argument("--seed", type=int, help="override the configured seed")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate configuration and list planned files without opening ZIPs or writing output",
    )
    return parser


def _required_text(mapping: dict[str, Any], key: str, *, scope: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{scope}.{key}: must be a non-empty string")
    return value


def profile_dataset_main(argv: Sequence[str] | None = None) -> int:
    parser = _profile_parser()
    arguments = parser.parse_args(argv)
    try:
        experiment_config = load_yaml_config(arguments.config)
        experiment_data = experiment_config.mutable_copy()
        study = _required_text(experiment_data, "study", scope="config")
        dataset_config_value = _required_text(
            experiment_data, "dataset_config", scope="config"
        )
        dataset_config = load_yaml_config(
            dataset_config_value, repository_root=experiment_config.repository_root
        )
        plan = build_inventory_plan(
            dataset_config, data_root_override=arguments.data_root
        )
        discovered, discovery_issues = discover_inventory_paths(plan)
        planned = (
            discovered if arguments.limit is None else discovered[: arguments.limit]
        )
        if arguments.dry_run:
            print(
                json.dumps(
                    {
                        "schema_version": "1.0.0",
                        "dry_run": True,
                        "study": study,
                        "dataset_config": dataset_config.relative_path,
                        "data_root": plan.data_root_reference,
                        "discovered_file_count": len(discovered),
                        "planned_file_count": len(planned),
                        "planned_relative_paths": [
                            asset.relative_path for asset in planned
                        ],
                        "discovery_issue_count": len(discovery_issues),
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        output_value = arguments.output_dir or experiment_data.get("output_root")
        output_root = experiment_config.resolve_repository_path(
            output_value, field="output_root", must_exist=False
        )
        seed_value = (
            arguments.seed
            if arguments.seed is not None
            else experiment_data.get("seed")
        )
        if isinstance(seed_value, bool) or not isinstance(seed_value, int):
            raise ConfigError("seed: must be an integer")
        seed_report = set_reproducible_seed(seed_value)
        result = profile_asset_inventory(plan, PHM2026Adapter(), limit=arguments.limit)
        resolved = {
            "schema_version": "1.0.0",
            "study": study,
            "experiment_config": experiment_config.mutable_copy(),
            "dataset_config_path": dataset_config.relative_path,
            "dataset_config_sha256": dataset_config.sha256,
            "dataset_config": dataset_config.mutable_copy(),
            "execution": {
                "seed": seed_value,
                "seed_report": {
                    "python_seeded": seed_report.python_seeded,
                    "numpy_seeded": seed_report.numpy_seeded,
                    "torch_seeded": seed_report.torch_seeded,
                    "torch_deterministic_algorithms": seed_report.torch_deterministic_algorithms,
                },
                "limit": arguments.limit,
                "dry_run": False,
                "data_root": plan.data_root_reference,
                "output_root": output_root.relative_to(
                    experiment_config.repository_root
                ).as_posix(),
            },
        }
        command = ["scripts/profile_dataset.py", *(argv or sys.argv[1:])]
        run = create_run_context(
            study=study,
            output_root=output_root,
            config=experiment_config,
            seed=seed_value,
            command=command,
            input_roots=(plan.data_root_reference,),
        )
        input_manifest = [
            {
                "asset_id": row["asset_id"],
                "relative_path": row["relative_path"],
                "size_bytes": row["size_bytes"],
                "central_directory_sha256": row["central_directory_sha256"],
                "readable": row["readable"],
            }
            for row in result.archives
        ]
        artifacts = write_inventory_run(
            result,
            run=run,
            resolved_config=resolved,
            input_manifest=input_manifest,
        )
    except (ConfigError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "summary": result.summary(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _sensor_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="profile_sensors.py",
        description=(
            "Profile PHM HDF5 members one at a time from an exact pinned D1.1 "
            "inventory run."
        ),
    )
    parser.add_argument(
        "--config",
        default="configs/experiments/phm2026_dataset_description.yaml",
    )
    parser.add_argument(
        "--inventory-run",
        help="exact configured D1.1 run ID or repository-relative run directory",
    )
    parser.add_argument("--output-dir", help="repository-relative run parent")
    parser.add_argument("--data-root", help="repository-relative PHM root override")
    parser.add_argument(
        "--mode", choices=("metadata", "sampled", "full"), help="profiling mode"
    )
    parser.add_argument("--limit", type=_positive_int)
    parser.add_argument("--limit-per-modality", type=_positive_int)
    parser.add_argument(
        "--modality",
        action="append",
        choices=("high_frequency", "low_frequency", "condition_indicator"),
    )
    parser.add_argument("--sample-points", type=_positive_int)
    parser.add_argument("--max-block-bytes", type=_positive_int)
    parser.add_argument("--max-member-bytes", type=_positive_int)
    parser.add_argument("--seed", type=int)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verify exact inputs and selection without opening raw archives or writing",
    )
    return parser


def _source_run_specification(
    experiment_data: dict[str, Any], inventory_override: str | None
) -> dict[str, Any]:
    source_runs = experiment_data.get("source_runs")
    if not isinstance(source_runs, dict):
        raise ConfigError("source_runs: must be a mapping")
    specification = source_runs.get("asset_inventory")
    if not isinstance(specification, dict):
        raise ConfigError("source_runs.asset_inventory: must be a mapping")
    if inventory_override is not None and inventory_override not in {
        specification.get("run_id"),
        specification.get("directory"),
    }:
        raise ConfigError(
            "--inventory-run must exactly match the hash-pinned D1.1 run in config"
        )
    return dict(specification)


def profile_sensors_main(argv: Sequence[str] | None = None) -> int:
    parser = _sensor_parser()
    arguments = parser.parse_args(argv)
    try:
        experiment_config = load_yaml_config(arguments.config)
        experiment_data = experiment_config.mutable_copy()
        study = _required_text(experiment_data, "study", scope="config")
        dataset_config_value = _required_text(
            experiment_data, "dataset_config", scope="config"
        )
        dataset_config = load_yaml_config(
            dataset_config_value, repository_root=experiment_config.repository_root
        )
        plan = build_inventory_plan(
            dataset_config, data_root_override=arguments.data_root
        )
        specification = _source_run_specification(
            experiment_data, arguments.inventory_run
        )
        pinned = load_pinned_run(
            experiment_config.repository_root,
            specification,
            required_artifacts=(
                "tables/asset_inventory.parquet",
                "tables/archive_members.parquet",
            ),
        )
        all_sources = load_sensor_sources(
            pinned.artifact_path("tables/archive_members.parquet"),
            asset_inventory=pinned.artifact_path("tables/asset_inventory.parquet"),
            data_root=plan.data_root,
            modalities=arguments.modality,
        )
        selected = select_sensor_sources(
            all_sources,
            limit=arguments.limit,
            limit_per_modality=arguments.limit_per_modality,
        )
        sensor_config = experiment_data.get("sensor_profile")
        if not isinstance(sensor_config, dict):
            raise ConfigError("sensor_profile: must be a mapping")
        mode = arguments.mode or sensor_config.get("default_mode", "metadata")
        if mode not in {"metadata", "sampled", "full"}:
            raise ConfigError("sensor_profile.default_mode is invalid")
        explicit_limit = (
            arguments.limit is not None or arguments.limit_per_modality is not None
        )
        if mode == "full" and not explicit_limit:
            raise ConfigError(
                "full sensor statistics require --limit or --limit-per-modality"
            )
        sample_points = arguments.sample_points or int(
            sensor_config.get("sample_points", 4096)
        )
        max_block_bytes = arguments.max_block_bytes or int(
            sensor_config.get("max_block_bytes", 16 * 1024 * 1024)
        )
        seed_value = (
            arguments.seed
            if arguments.seed is not None
            else experiment_data.get("seed")
        )
        if isinstance(seed_value, bool) or not isinstance(seed_value, int):
            raise ConfigError("seed: must be an integer")
        selection_counts: dict[str, int] = {}
        for source in selected:
            selection_counts[source.modality] = (
                selection_counts.get(source.modality, 0) + 1
            )
        if arguments.dry_run:
            print(
                json.dumps(
                    {
                        "schema_version": "1.0.0",
                        "dry_run": True,
                        "study": study,
                        "mode": mode,
                        "source_run": pinned.source_record(
                            "tables/archive_members.parquet"
                        ),
                        "data_root": plan.data_root_reference,
                        "discovered_source_count": len(all_sources),
                        "selected_source_count": len(selected),
                        "selected_by_modality": selection_counts,
                        "would_open_raw_archives": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        output_value = arguments.output_dir or experiment_data.get("output_root")
        output_root = experiment_config.resolve_repository_path(
            output_value, field="output_root", must_exist=False
        )
        set_reproducible_seed(seed_value)
        options = SensorProfileOptions(
            mode=mode,
            seed=seed_value,
            sample_points=sample_points,
            max_block_bytes=max_block_bytes,
            max_member_bytes=arguments.max_member_bytes,
            expected_paths=sensor_config.get("expected_paths"),
            full_scan_authorized=explicit_limit,
        )
        result = profile_sensor_sources(
            selected,
            adapter=PHM2026Adapter(),
            options=options,
            discovered_source_count=len(all_sources),
            limited=len(selected) < len(all_sources),
        )
        source_run_record = {
            "run_id": pinned.run_id,
            "directory": pinned.relative_directory,
            "artifacts": dict(pinned.verified_hashes),
        }
        resolved = {
            "schema_version": "1.0.0",
            "study": study,
            "task": "D1.2",
            "experiment_config": experiment_data,
            "dataset_config_path": dataset_config.relative_path,
            "dataset_config_sha256": dataset_config.sha256,
            "dataset_config": dataset_config.mutable_copy(),
            "source_runs": {"asset_inventory": source_run_record},
            "execution": {
                "mode": mode,
                "seed": seed_value,
                "sample_points": sample_points,
                "max_block_bytes": max_block_bytes,
                "max_member_bytes": arguments.max_member_bytes,
                "limit": arguments.limit,
                "limit_per_modality": arguments.limit_per_modality,
                "modalities": arguments.modality,
                "dry_run": False,
                "data_root": plan.data_root_reference,
                "output_root": output_root.relative_to(
                    experiment_config.repository_root
                ).as_posix(),
            },
        }
        command = ["scripts/profile_sensors.py", *(argv or sys.argv[1:])]
        run = create_run_context(
            study=study,
            output_root=output_root,
            config=experiment_config,
            seed=seed_value,
            command=command,
            input_roots=(plan.data_root_reference,),
            package_names=("numpy", "pandas", "pyarrow", "PyYAML", "h5py"),
            source_runs=(source_run_record,),
        )
        input_manifest = [
            pinned.source_record("tables/asset_inventory.parquet"),
            pinned.source_record("tables/archive_members.parquet"),
            *(
                {
                    "inventory_member_id": source.inventory_member_id,
                    "archive_asset_id": source.archive_asset_id,
                    "archive_relative_path": source.archive_relative_path,
                    "outer_member_path": source.outer_member_path,
                    "member_occurrence": source.member_occurrence,
                    "modality": source.modality,
                    "experiment": source.experiment,
                    "authoritative_outer_run": source.authoritative_outer_run,
                    "nested_archive_run_token": source.nested_archive_run_token,
                    "uncompressed_size_bytes": source.uncompressed_size_bytes,
                    "crc32": source.crc32,
                }
                for source in selected
            ),
        ]
        artifacts = write_sensor_run(
            result,
            run=run,
            resolved_config=resolved,
            input_manifest=input_manifest,
        )
    except (ConfigError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "source_run_id": pinned.run_id,
                "summary": result.summary(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _image_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="profile_images.py",
        description=(
            "Profile PHM image headers and bounded pixel-quality evidence from an "
            "exact pinned D1.1 inventory run."
        ),
    )
    parser.add_argument(
        "--config",
        default="configs/experiments/phm2026_dataset_description.yaml",
    )
    parser.add_argument("--inventory-run")
    parser.add_argument("--output-dir")
    parser.add_argument("--data-root")
    parser.add_argument("--mode", choices=("header", "sampled", "full"))
    parser.add_argument("--limit", type=_positive_int)
    parser.add_argument("--sample-size", type=_positive_int)
    parser.add_argument("--max-member-bytes", type=_positive_int)
    parser.add_argument("--max-pixels", type=_positive_int)
    parser.add_argument("--near-duplicate-hamming", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def profile_images_main(argv: Sequence[str] | None = None) -> int:
    parser = _image_parser()
    arguments = parser.parse_args(argv)
    try:
        experiment_config = load_yaml_config(arguments.config)
        experiment_data = experiment_config.mutable_copy()
        study = _required_text(experiment_data, "study", scope="config")
        dataset_config = load_yaml_config(
            _required_text(experiment_data, "dataset_config", scope="config"),
            repository_root=experiment_config.repository_root,
        )
        plan = build_inventory_plan(
            dataset_config, data_root_override=arguments.data_root
        )
        specification = _source_run_specification(
            experiment_data, arguments.inventory_run
        )
        pinned = load_pinned_run(
            experiment_config.repository_root,
            specification,
            required_artifacts=(
                "tables/asset_inventory.parquet",
                "tables/archive_members.parquet",
            ),
        )
        all_sources = load_image_sources(
            pinned.artifact_path("tables/archive_members.parquet"),
            asset_inventory=pinned.artifact_path("tables/asset_inventory.parquet"),
            data_root=plan.data_root,
        )
        selected = select_image_sources(all_sources, limit=arguments.limit)
        image_config = experiment_data.get("image_profile")
        if not isinstance(image_config, dict):
            raise ConfigError("image_profile: must be a mapping")
        mode = arguments.mode or image_config.get("default_mode", "header")
        if mode not in {"header", "sampled", "full"}:
            raise ConfigError("image_profile.default_mode is invalid")
        if mode == "full" and arguments.limit is None:
            raise ConfigError("full image pixel analysis requires --limit")
        seed_value = (
            arguments.seed
            if arguments.seed is not None
            else experiment_data.get("seed")
        )
        if isinstance(seed_value, bool) or not isinstance(seed_value, int):
            raise ConfigError("seed: must be an integer")
        sample_size = arguments.sample_size or int(image_config.get("sample_size", 104))
        max_member_bytes = arguments.max_member_bytes or int(
            image_config.get("max_member_bytes", 8 * 1024 * 1024)
        )
        max_pixels = arguments.max_pixels or int(
            image_config.get("max_pixels", 50_000_000)
        )
        near_threshold = (
            arguments.near_duplicate_hamming
            if arguments.near_duplicate_hamming is not None
            else int(image_config.get("near_duplicate_hamming", 4))
        )
        options = ImageProfileOptions(
            mode=mode,
            seed=seed_value,
            sample_size=sample_size,
            max_member_bytes=max_member_bytes,
            max_pixels=max_pixels,
            near_duplicate_hamming=near_threshold,
        )
        quality_ids = select_quality_source_ids(
            selected, mode=mode, sample_size=sample_size, seed=seed_value
        )
        if arguments.dry_run:
            print(
                json.dumps(
                    {
                        "schema_version": "1.0.0",
                        "dry_run": True,
                        "study": study,
                        "mode": mode,
                        "source_run": pinned.source_record(
                            "tables/archive_members.parquet"
                        ),
                        "data_root": plan.data_root_reference,
                        "discovered_image_count": len(all_sources),
                        "selected_image_count": len(selected),
                        "pixel_quality_selected_count": len(quality_ids),
                        "encoded_bytes": sum(
                            source.encoded_size_bytes for source in selected
                        ),
                        "would_open_raw_archives": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        output_root = experiment_config.resolve_repository_path(
            arguments.output_dir or experiment_data.get("output_root"),
            field="output_root",
            must_exist=False,
        )
        set_reproducible_seed(seed_value)
        adapter = PHM2026Adapter()
        result = profile_image_sources(
            selected,
            adapter=adapter,
            options=options,
            discovered_source_count=len(all_sources),
            limited=len(selected) < len(all_sources),
        )
        source_run_record = {
            "run_id": pinned.run_id,
            "directory": pinned.relative_directory,
            "artifacts": dict(pinned.verified_hashes),
        }
        resolved = {
            "schema_version": "1.0.0",
            "study": study,
            "task": "D1.3",
            "experiment_config": experiment_data,
            "dataset_config_path": dataset_config.relative_path,
            "dataset_config_sha256": dataset_config.sha256,
            "dataset_config": dataset_config.mutable_copy(),
            "source_runs": {"asset_inventory": source_run_record},
            "execution": {
                "mode": mode,
                "seed": seed_value,
                "sample_size": sample_size,
                "max_member_bytes": max_member_bytes,
                "max_pixels": max_pixels,
                "near_duplicate_hamming": near_threshold,
                "limit": arguments.limit,
                "dry_run": False,
                "data_root": plan.data_root_reference,
                "output_root": output_root.relative_to(
                    experiment_config.repository_root
                ).as_posix(),
            },
        }
        command = ["scripts/profile_images.py", *(argv or sys.argv[1:])]
        run = create_run_context(
            study=study,
            output_root=output_root,
            config=experiment_config,
            seed=seed_value,
            command=command,
            input_roots=(plan.data_root_reference,),
            package_names=(
                "numpy",
                "pandas",
                "pyarrow",
                "PyYAML",
                "Pillow",
                "matplotlib",
            ),
            source_runs=(source_run_record,),
        )
        input_manifest = [
            pinned.source_record("tables/asset_inventory.parquet"),
            pinned.source_record("tables/archive_members.parquet"),
            *(
                {
                    "source_member_id": source.source_member_id,
                    "archive_asset_id": source.archive_asset_id,
                    "source_relative_path": source.source_relative_path,
                    "experiment": source.experiment,
                    "authoritative_outer_run": source.authoritative_outer_run,
                    "encoded_size_bytes": source.encoded_size_bytes,
                    "crc32": source.crc32,
                }
                for source in selected
            ),
        ]
        artifacts = write_image_run(
            result,
            run=run,
            resolved_config=resolved,
            input_manifest=input_manifest,
            adapter=adapter,
            options=options,
        )
    except (ConfigError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "source_run_id": pinned.run_id,
                "summary": result.summary(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _alignment_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audit_alignment.py",
        description=(
            "Audit PHM cross-modal clock evidence from exact pinned generated "
            "D1.1–D1.3 artifacts without reopening raw archives."
        ),
    )
    parser.add_argument(
        "--config",
        default="configs/experiments/phm2026_dataset_description.yaml",
    )
    parser.add_argument("--output-dir", help="repository-relative run parent")
    parser.add_argument("--join-tolerance-seconds", type=_nonnegative_float)
    parser.add_argument("--six-hour-tolerance-seconds", type=_nonnegative_float)
    parser.add_argument("--trace-example-count", type=_positive_int)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verify exact generated-artifact pins without reading raw data or writing output",
    )
    return parser


def _pinned_source_run(
    experiment_data: dict[str, Any],
    *,
    source_name: str,
    repository_root: Path,
    required_artifacts: tuple[str, ...],
):
    source_runs = experiment_data.get("source_runs")
    if not isinstance(source_runs, dict):
        raise ConfigError("source_runs: must be a mapping")
    specification = source_runs.get(source_name)
    if not isinstance(specification, dict):
        raise ConfigError(f"source_runs.{source_name}: must be a mapping")
    return load_pinned_run(
        repository_root, specification, required_artifacts=required_artifacts
    )


def audit_alignment_main(argv: Sequence[str] | None = None) -> int:
    """Run D1.4 solely from verified D1.1–D1.3 generated artifacts."""

    parser = _alignment_parser()
    arguments = parser.parse_args(argv)
    try:
        experiment_config = load_yaml_config(arguments.config)
        experiment_data = experiment_config.mutable_copy()
        study = _required_text(experiment_data, "study", scope="config")
        seed_value = experiment_data.get("seed")
        if isinstance(seed_value, bool) or not isinstance(seed_value, int):
            raise ConfigError("seed: must be an integer")
        alignment_config = experiment_data.get("alignment_audit")
        if not isinstance(alignment_config, dict):
            raise ConfigError("alignment_audit: must be a mapping")
        if alignment_config.get("require_verified_utc") is not True:
            raise ConfigError("alignment_audit.require_verified_utc must be true")
        if alignment_config.get("require_matching_clock_domain") is not True:
            raise ConfigError(
                "alignment_audit.require_matching_clock_domain must be true"
            )
        direction = alignment_config.get("match_direction")
        if direction != "past_only":
            raise ConfigError("alignment_audit.match_direction must be 'past_only'")
        tolerance_seconds = (
            arguments.join_tolerance_seconds
            if arguments.join_tolerance_seconds is not None
            else alignment_config.get("join_tolerance_seconds")
        )
        six_hour_tolerance_seconds = (
            arguments.six_hour_tolerance_seconds
            if arguments.six_hour_tolerance_seconds is not None
            else alignment_config.get("six_hour_tolerance_seconds")
        )
        six_hour_reference_seconds = alignment_config.get("six_hour_interval_seconds")
        options = AlignmentPipelineOptions(
            tolerance_seconds=float(tolerance_seconds),
            direction="past_only",
            six_hour_reference_seconds=float(six_hour_reference_seconds),
            six_hour_tolerance_seconds=float(six_hour_tolerance_seconds),
            trace_example_count=arguments.trace_example_count or 5,
        )
        pinned_inventory = _pinned_source_run(
            experiment_data,
            source_name="asset_inventory",
            repository_root=experiment_config.repository_root,
            required_artifacts=(
                "tables/asset_inventory.parquet",
                "tables/archive_members.parquet",
            ),
        )
        pinned_sensors = _pinned_source_run(
            experiment_data,
            source_name="sensor_profile",
            repository_root=experiment_config.repository_root,
            required_artifacts=(
                "tables/hdf5_members.parquet",
                "tables/sensor_profile.parquet",
            ),
        )
        pinned_images = _pinned_source_run(
            experiment_data,
            source_name="image_profile",
            repository_root=experiment_config.repository_root,
            required_artifacts=(
                "tables/image_profile.parquet",
                "reports/image_summary.json",
            ),
        )
        pinned_sources = {
            "asset_inventory": pinned_inventory,
            "sensor_profile": pinned_sensors,
            "image_profile": pinned_images,
        }
        if arguments.dry_run:
            print(
                json.dumps(
                    {
                        "schema_version": "1.0.0",
                        "dry_run": True,
                        "study": study,
                        "source_runs": {
                            name: {
                                "run_id": pinned.run_id,
                                "directory": pinned.relative_directory,
                                "verified_artifacts": dict(pinned.verified_hashes),
                            }
                            for name, pinned in pinned_sources.items()
                        },
                        "would_open_raw_archives": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        output_root = experiment_config.resolve_repository_path(
            arguments.output_dir or experiment_data.get("output_root"),
            field="output_root",
            must_exist=False,
        )
        set_reproducible_seed(seed_value)
        result = build_alignment_pipeline(
            pinned_sensors.artifact_path("tables/hdf5_members.parquet"),
            pinned_sensors.artifact_path("tables/sensor_profile.parquet"),
            pinned_images.artifact_path("tables/image_profile.parquet"),
            options=options,
        )
        source_run_records = [
            {
                "name": name,
                "run_id": pinned.run_id,
                "directory": pinned.relative_directory,
                "artifacts": dict(pinned.verified_hashes),
            }
            for name, pinned in pinned_sources.items()
        ]
        input_manifest = [
            pinned.source_record(path)
            for pinned in pinned_sources.values()
            for path in sorted(pinned.verified_hashes)
        ]
        resolved = {
            "schema_version": "1.0.0",
            "study": study,
            "task": "D1.4",
            "experiment_config": experiment_data,
            "source_runs": source_run_records,
            "execution": {
                "generated_artifacts_only": True,
                "raw_archives_opened": False,
                "seed": seed_value,
                "tolerance_seconds": options.tolerance_seconds,
                "direction": options.direction,
                "six_hour_reference_seconds": options.six_hour_reference_seconds,
                "six_hour_tolerance_seconds": options.six_hour_tolerance_seconds,
                "trace_example_count": options.trace_example_count,
                "output_root": output_root.relative_to(
                    experiment_config.repository_root
                ).as_posix(),
            },
        }
        command = ["scripts/audit_alignment.py", *(argv or sys.argv[1:])]
        run = create_run_context(
            study=study,
            output_root=output_root,
            config=experiment_config,
            seed=seed_value,
            command=command,
            input_roots=tuple(
                pinned.relative_directory for pinned in pinned_sources.values()
            ),
            package_names=("numpy", "pandas", "pyarrow", "PyYAML", "matplotlib"),
            source_runs=source_run_records,
        )
        artifacts = write_alignment_run(
            result,
            run=run,
            resolved_config=resolved,
            input_manifest=input_manifest,
        )
        artifacts = write_blocker_artifacts(
            result,
            run=run,
            input_manifest=input_manifest,
            existing_artifacts=artifacts,
        )
    except (ConfigError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "summary": result.summary(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _dataset_description_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="describe_dataset.py",
        description=(
            "Generate the PHM professor-facing D1.5 dataset description from "
            "exact pinned profiling artifacts only."
        ),
    )
    parser.add_argument(
        "--config",
        default="configs/experiments/phm2026_dataset_description.yaml",
    )
    parser.add_argument("--output-dir", help="repository-relative run parent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="verify exact generated-artifact pins without opening raw data or writing output",
    )
    return parser


def _json_mapping(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"{label} is unreadable JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a JSON object")
    return value


def describe_dataset_main(argv: Sequence[str] | None = None) -> int:
    """Run D1.5 exclusively from D1.1–D1.4 generated artifacts."""

    parser = _dataset_description_parser()
    arguments = parser.parse_args(argv)
    try:
        experiment_config = load_yaml_config(arguments.config)
        experiment_data = experiment_config.mutable_copy()
        study = _required_text(experiment_data, "study", scope="config")
        seed_value = experiment_data.get("seed")
        if isinstance(seed_value, bool) or not isinstance(seed_value, int):
            raise ConfigError("seed: must be an integer")
        pinned_inventory = _pinned_source_run(
            experiment_data,
            source_name="asset_inventory",
            repository_root=experiment_config.repository_root,
            required_artifacts=(
                "tables/asset_inventory.parquet",
                "tables/archive_members.parquet",
                "reports/summary.json",
            ),
        )
        pinned_sensors = _pinned_source_run(
            experiment_data,
            source_name="sensor_profile",
            repository_root=experiment_config.repository_root,
            required_artifacts=(
                "tables/sensor_profile.parquet",
                "reports/sensor_summary.json",
                "reports/hdf5_schema.json",
            ),
        )
        pinned_images = _pinned_source_run(
            experiment_data,
            source_name="image_profile",
            repository_root=experiment_config.repository_root,
            required_artifacts=(
                "tables/image_profile.parquet",
                "reports/image_summary.json",
            ),
        )
        pinned_quality = _pinned_source_run(
            experiment_data,
            source_name="image_quality_profile",
            repository_root=experiment_config.repository_root,
            required_artifacts=(
                "tables/image_profile.parquet",
                "reports/image_summary.json",
            ),
        )
        pinned_alignment = _pinned_source_run(
            experiment_data,
            source_name="alignment_audit",
            repository_root=experiment_config.repository_root,
            required_artifacts=(
                "tables/image_clock_audit.parquet",
                "tables/sensor_clock_audit.parquet",
                "tables/candidate_sample_traces.parquet",
                "reports/alignment_blockers.json",
                "reports/alignment_summary.json",
            ),
        )
        pinned_sources = {
            "asset_inventory": pinned_inventory,
            "sensor_profile": pinned_sensors,
            "image_profile": pinned_images,
            "image_quality_profile": pinned_quality,
            "alignment_audit": pinned_alignment,
        }
        if arguments.dry_run:
            print(
                json.dumps(
                    {
                        "schema_version": "1.0.0",
                        "dry_run": True,
                        "study": study,
                        "source_runs": {
                            name: {
                                "run_id": pinned.run_id,
                                "directory": pinned.relative_directory,
                                "verified_artifact_count": len(pinned.verified_hashes),
                            }
                            for name, pinned in pinned_sources.items()
                        },
                        "would_open_raw_archives": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        sources = {
            "inventory_summary": pinned_inventory.source_record("reports/summary.json"),
            "asset_inventory": pinned_inventory.source_record(
                "tables/asset_inventory.parquet"
            ),
            "sensor_profile": pinned_sensors.source_record(
                "tables/sensor_profile.parquet"
            ),
            "sensor_summary": pinned_sensors.source_record(
                "reports/sensor_summary.json"
            ),
            "sensor_schema": pinned_sensors.source_record("reports/hdf5_schema.json"),
            "image_header_profile": pinned_images.source_record(
                "tables/image_profile.parquet"
            ),
            "image_header_summary": pinned_images.source_record(
                "reports/image_summary.json"
            ),
            "image_quality_summary": pinned_quality.source_record(
                "reports/image_summary.json"
            ),
            "alignment_blockers": pinned_alignment.source_record(
                "reports/alignment_blockers.json"
            ),
            "alignment_traces": pinned_alignment.source_record(
                "tables/candidate_sample_traces.parquet"
            ),
            "image_clock": pinned_alignment.source_record(
                "tables/image_clock_audit.parquet"
            ),
            "sensor_clock": pinned_alignment.source_record(
                "tables/sensor_clock_audit.parquet"
            ),
        }
        result = build_dataset_description(
            asset_inventory=pd.read_parquet(
                pinned_inventory.artifact_path("tables/asset_inventory.parquet")
            ),
            inventory_summary=_json_mapping(
                pinned_inventory.artifact_path("reports/summary.json"),
                label="D1.1 inventory summary",
            ),
            sensor_profile=pd.read_parquet(
                pinned_sensors.artifact_path("tables/sensor_profile.parquet")
            ),
            sensor_summary=_json_mapping(
                pinned_sensors.artifact_path("reports/sensor_summary.json"),
                label="D1.2 sensor summary",
            ),
            image_profile=pd.read_parquet(
                pinned_images.artifact_path("tables/image_profile.parquet")
            ),
            image_header_summary=_json_mapping(
                pinned_images.artifact_path("reports/image_summary.json"),
                label="D1.3 image header summary",
            ),
            image_quality_summary=_json_mapping(
                pinned_quality.artifact_path("reports/image_summary.json"),
                label="D1.3 image quality summary",
            ),
            image_clock_audit=pd.read_parquet(
                pinned_alignment.artifact_path("tables/image_clock_audit.parquet")
            ),
            sensor_clock_audit=pd.read_parquet(
                pinned_alignment.artifact_path("tables/sensor_clock_audit.parquet")
            ),
            alignment_blockers=_json_mapping(
                pinned_alignment.artifact_path("reports/alignment_blockers.json"),
                label="D1.4 alignment blockers",
            ),
            alignment_traces=pd.read_parquet(
                pinned_alignment.artifact_path("tables/candidate_sample_traces.parquet")
            ),
            sources=sources,
        )
        output_root = experiment_config.resolve_repository_path(
            arguments.output_dir or experiment_data.get("output_root"),
            field="output_root",
            must_exist=False,
        )
        set_reproducible_seed(seed_value)
        source_run_records = [
            {
                "name": name,
                "run_id": pinned.run_id,
                "directory": pinned.relative_directory,
                "artifacts": dict(pinned.verified_hashes),
            }
            for name, pinned in pinned_sources.items()
        ]
        input_manifest = [
            pinned.source_record(path)
            for pinned in pinned_sources.values()
            for path in sorted(pinned.verified_hashes)
        ]
        resolved = {
            "schema_version": "1.0.0",
            "study": study,
            "task": "D1.5",
            "experiment_config": experiment_data,
            "source_runs": source_run_records,
            "execution": {
                "generated_artifacts_only": True,
                "raw_archives_opened": False,
                "seed": seed_value,
                "output_root": output_root.relative_to(
                    experiment_config.repository_root
                ).as_posix(),
            },
        }
        command = ["scripts/describe_dataset.py", *(argv or sys.argv[1:])]
        run = create_run_context(
            study=study,
            output_root=output_root,
            config=experiment_config,
            seed=seed_value,
            command=command,
            input_roots=tuple(
                pinned.relative_directory for pinned in pinned_sources.values()
            ),
            package_names=("pandas", "pyarrow", "PyYAML", "matplotlib"),
            source_runs=source_run_records,
        )
        artifacts = write_dataset_description_run(
            result,
            run=run,
            resolved_config=resolved,
            input_manifest=input_manifest,
        )
    except (ConfigError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "schema_version": "1.0.0",
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
