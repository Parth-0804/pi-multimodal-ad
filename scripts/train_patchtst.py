#!/usr/bin/env python3
"""Train and evaluate the initial sensor-only PatchTST-style baseline."""

from __future__ import annotations

import argparse
import json
import shutil
import sys

import pandas as pd
import torch

from pi_multimodal_ad.models.patchtst import PatchTSTConfig
from pi_multimodal_ad.models.patchtst_regression import (
    TrainingOptions,
    run_patchtst_baseline,
    write_patchtst_run,
)
from pi_multimodal_ad.preprocessing.timeseries import (
    build_run_sequences,
    fit_feature_normalizer,
)
from pi_multimodal_ad.utils.artifacts import load_pinned_run
from pi_multimodal_ad.utils.config import ConfigError, load_yaml_config
from pi_multimodal_ad.utils.provenance import create_run_context
from pi_multimodal_ad.utils.seeding import set_reproducible_seed


def _feature_columns(data: dict) -> list[str]:
    columns = [
        f"{name}_{statistic}"
        for name in data["feature_names"]
        for statistic in data["channel_statistics"]
    ]
    if data["include_channel_missingness_masks"]:
        columns.extend(f"{name}_missing" for name in data["feature_names"])
    return columns


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_patchtst_baseline.yaml"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--device")
    parser.add_argument("--max-epochs", type=int)
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        sources = data["source_runs"]
        feature_run = load_pinned_run(
            config.repository_root,
            sources["sensor_features"],
            required_artifacts=(
                "tables/minute_feature_table.parquet",
                "tables/sensor_run_sequences.parquet",
                "reports/feature_schema.json",
            ),
        )
        target_run = load_pinned_run(
            config.repository_root,
            sources["target"],
            required_artifacts=("tables/run_damage_targets.parquet",),
        )
        dataset_run = load_pinned_run(
            config.repository_root,
            sources["model_dataset"],
            required_artifacts=(
                "tables/split_manifest.parquet",
                "reports/split_validation.json",
            ),
        )
        image_run = load_pinned_run(
            config.repository_root,
            sources["image_regression"],
            required_artifacts=("tables/run_predictions.parquet",),
        )
        minute = pd.read_parquet(
            feature_run.artifact_path("tables/minute_feature_table.parquet")
        )
        run_summary = pd.read_parquet(
            feature_run.artifact_path("tables/sensor_run_sequences.parquet")
        )
        targets = pd.read_parquet(
            target_run.artifact_path("tables/run_damage_targets.parquet")
        )
        image_predictions = pd.read_parquet(
            image_run.artifact_path("tables/run_predictions.parquet")
        )
        expected_split = {
            str(value): key
            for key, value in data["split"].items()
            if key != "random_split_used"
        }
        if expected_split != {"EXP-B": "train", "EXP-A": "validation", "EXP-F": "test"}:
            raise ValueError(
                "configured split differs from the authorized experiment split"
            )
        actual_split = (
            run_summary[["experiment", "split"]]
            .drop_duplicates()
            .set_index("experiment")
            .split.to_dict()
        )
        if actual_split != expected_split:
            raise ValueError("feature run split identities do not match configuration")
        if len(run_summary) != 20 or run_summary.groupby(
            "experiment"
        ).size().to_dict() != {
            "EXP-A": 5,
            "EXP-B": 7,
            "EXP-F": 8,
        }:
            raise ValueError("expected exactly 20 A/B/F run sequences")
        joined = run_summary.merge(
            targets[
                [
                    "experiment",
                    "run",
                    "raw_top3_mean_pct",
                    "causal_monotonic_top3_mean_pct",
                ]
            ],
            on=["experiment", "run"],
            suffixes=("_feature", "_target"),
            validate="one_to_one",
        )
        for name in ("raw_top3_mean_pct", "causal_monotonic_top3_mean_pct"):
            if not (
                joined[f"{name}_feature"].round(12)
                == joined[f"{name}_target"].round(12)
            ).all():
                raise ValueError(f"feature-run target mismatch for {name}")
        columns = _feature_columns(data)
        missing_columns = sorted(set(columns) - set(minute.columns))
        if missing_columns:
            raise ValueError(
                f"feature table is missing configured columns: {missing_columns}"
            )
        if len(columns) != int(data["model"]["input_channels"]):
            raise ValueError("configured input_channels does not match feature schema")
        normalizer = fit_feature_normalizer(minute, feature_columns=columns)
        sequences = build_run_sequences(minute, run_summary, normalizer=normalizer)
        device = args.device or data["training"]["device"]
        if device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("configured CUDA device is unavailable")
        free = shutil.disk_usage(config.repository_root).free
        minimum = int(data["storage_limits"]["minimum_free_bytes"])
        if free < minimum:
            raise RuntimeError("minimum free-space gate is not satisfied")
        plan = {
            "sequence_count": len(sequences),
            "split_counts": pd.Series([item.split for item in sequences])
            .value_counts()
            .to_dict(),
            "feature_count": len(columns),
            "sequence_lengths": {
                f"{item.experiment}/run-{item.run}": len(item.minute_ids)
                for item in sequences
            },
            "device": device,
            "free_bytes": free,
            "target": data["target"],
            "would_write": not args.dry_run,
            "test_used_for_tuning": False,
        }
        if args.dry_run:
            print(json.dumps(plan, indent=2))
            return 0
        set_reproducible_seed(int(data["seed"]))
        run = create_run_context(
            study=data["study"],
            output_root=config.resolve_repository_path(
                data["output_root"], field="output_root"
            ),
            config=config,
            seed=int(data["seed"]),
            command=("scripts/train_patchtst.py", "--config", config.relative_path),
            input_roots=(),
            package_names=(
                "numpy",
                "pandas",
                "pyarrow",
                "torch",
                "scikit-learn",
                "scipy",
                "matplotlib",
                "PyYAML",
            ),
            source_runs=tuple(
                pinned.source_record(path)
                for pinned in (feature_run, target_run, dataset_run, image_run)
                for path in sorted(pinned.verified_hashes)
            ),
        )
        run.create_layout()
        model_config = PatchTSTConfig(**data["model"])
        training_data = dict(data["training"])
        training_data.pop("device")
        if args.max_epochs is not None:
            if args.max_epochs <= 0:
                raise ValueError("--max-epochs must be positive")
            training_data["max_epochs"] = args.max_epochs
        result = run_patchtst_baseline(
            sequences,
            model_config=model_config,
            training_options=TrainingOptions(**training_data),
            ridge_alphas=data["ridge"]["alpha_candidates"],
            seed=int(data["seed"]),
            device=device,
            rtdetr_run_predictions=image_predictions,
        )
        resolved = {
            "schema_version": "1.0.0",
            "experiment_config": data,
            "execution": plan,
            "model_device": device,
            "test_evaluated_after_validation_selection": True,
        }
        inputs = [
            pinned.source_record(path)
            for pinned in (feature_run, target_run, dataset_run, image_run)
            for path in sorted(pinned.verified_hashes)
        ]
        artifacts = write_patchtst_run(
            result,
            run=run,
            resolved_config=resolved,
            input_manifest=inputs,
            feature_normalizer=normalizer.as_dict(),
            feature_run_summary=run_summary,
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
                "training_summary": result.training_summary,
                "test_metrics": result.metrics[result.metrics.split.eq("test")].to_dict(
                    orient="records"
                ),
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
