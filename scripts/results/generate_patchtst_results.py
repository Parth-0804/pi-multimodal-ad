#!/usr/bin/env python3
"""Generate the pinned professor-ready initial PatchTST result package."""

from __future__ import annotations

import argparse
import json
import shutil
import sys

import pandas as pd

from pi_multimodal_ad.reporting.patchtst_results import write_patchtst_results_run
from pi_multimodal_ad.utils.artifacts import load_pinned_run
from pi_multimodal_ad.utils.config import ConfigError, load_yaml_config
from pi_multimodal_ad.utils.provenance import create_run_context


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_patchtst_results.yaml"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        specifications = data["source_runs"]
        features = load_pinned_run(
            config.repository_root,
            specifications["sensor_features"],
            required_artifacts=(
                "tables/minute_feature_table.parquet",
                "tables/sensor_run_sequences.parquet",
                "tables/channel_availability.parquet",
                "reports/sensor_feature_summary.json",
            ),
        )
        patchtst = load_pinned_run(
            config.repository_root,
            specifications["patchtst"],
            required_artifacts=(
                "tables/predictions.parquet",
                "tables/training_history.parquet",
                "tables/architecture_tensor_shapes.parquet",
                "reports/feature_normalizer.json",
                "reports/training_summary.json",
                "reports/environment.json",
            ),
        )
        image = load_pinned_run(
            config.repository_root,
            specifications["image_regression"],
            required_artifacts=("tables/run_predictions.parquet",),
        )
        minute = pd.read_parquet(
            features.artifact_path("tables/minute_feature_table.parquet")
        )
        run_summary = pd.read_parquet(
            features.artifact_path("tables/sensor_run_sequences.parquet")
        )
        availability = pd.read_parquet(
            features.artifact_path("tables/channel_availability.parquet")
        )
        predictions = pd.read_parquet(
            patchtst.artifact_path("tables/predictions.parquet")
        )
        history = pd.read_parquet(
            patchtst.artifact_path("tables/training_history.parquet")
        )
        architecture = pd.read_parquet(
            patchtst.artifact_path("tables/architecture_tensor_shapes.parquet")
        )
        feature_normalizer = json.loads(
            patchtst.artifact_path("reports/feature_normalizer.json").read_text()
        )
        training_summary = json.loads(
            patchtst.artifact_path("reports/training_summary.json").read_text()
        )
        environment = json.loads(
            patchtst.artifact_path("reports/environment.json").read_text()
        )
        image_predictions = pd.read_parquet(
            image.artifact_path("tables/run_predictions.parquet")
        )
        if len(run_summary) != 20 or predictions.sequence_id.nunique() != 20:
            raise ValueError("expected exactly 20 matching run sequences")
        test_rows = predictions[
            predictions.split.eq("test")
            & predictions.model_name.eq("patchtst_sensor_regression")
        ]
        if len(test_rows) != 8 or set(test_rows.experiment) != {"EXP-F"}:
            raise ValueError("PatchTST test rows do not match the pinned EXP-F split")
        starting_free = shutil.disk_usage(config.repository_root).free
        if starting_free < int(data["storage_limits"]["minimum_free_bytes"]):
            raise RuntimeError("minimum free-space gate is not satisfied")
        plan = {
            "feature_run_id": features.run_id,
            "patchtst_run_id": patchtst.run_id,
            "image_run_id": image.run_id,
            "minute_count": len(minute),
            "run_count": len(run_summary),
            "test_count": len(test_rows),
            "starting_free_bytes": starting_free,
            "would_write": not args.dry_run,
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
                "scripts/results/generate_patchtst_results.py",
                "--config",
                config.relative_path,
            ),
            input_roots=(),
            package_names=(
                "numpy",
                "pandas",
                "pyarrow",
                "scipy",
                "matplotlib",
                "PyYAML",
            ),
            source_runs=tuple(
                pinned.source_record(path)
                for pinned in (features, patchtst, image)
                for path in sorted(pinned.verified_hashes)
            ),
        )
        run.create_layout()
        inputs = [
            pinned.source_record(path)
            for pinned in (features, patchtst, image)
            for path in sorted(pinned.verified_hashes)
        ]
        artifacts = write_patchtst_results_run(
            minute=minute,
            run_summary=run_summary,
            channel_availability=availability,
            predictions=predictions,
            history=history,
            architecture=architecture,
            feature_normalizer=feature_normalizer,
            training_summary=training_summary,
            environment=environment,
            image_predictions=image_predictions,
            bootstrap_repetitions=int(data["evaluation"]["bootstrap_repetitions"]),
            seed=int(data["seed"]),
            starting_free_bytes=starting_free,
            run=run,
            resolved_config={
                "schema_version": "1.0.0",
                "experiment_config": data,
                "execution": plan,
            },
            input_manifest=inputs,
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
                "figure_png_count": len(
                    list((run.run_directory / "figures").glob("*.png"))
                ),
                "figure_svg_count": len(
                    list((run.run_directory / "figures").glob("*.svg"))
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
