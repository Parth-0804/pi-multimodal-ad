#!/usr/bin/env python3
"""Train/evaluate the provisional frozen-encoder RT-DETR-derived baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pi_multimodal_ad.models.rtdetr_feasibility import (
    RTDETRFeasibilityOptions,
    download_checkpoint,
)  # noqa: E402
from pi_multimodal_ad.models.rtdetr_regression import (  # noqa: E402
    RegressionResult,
    aggregate_predictions,
    build_metrics,
    extract_features,
    predict_all,
    train_head,
    write_regression_run,
)
from pi_multimodal_ad.profiling.images import load_image_sources  # noqa: E402
from pi_multimodal_ad.utils import (
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
    set_reproducible_seed,
)  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_rtdetr_regression.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        required = {
            "inventory": (
                "tables/asset_inventory.parquet",
                "tables/archive_members.parquet",
            ),
            "model_dataset": (
                "tables/model_sample_manifest.parquet",
                "tables/split_manifest.parquet",
                "reports/split_validation.json",
            ),
            "target": (
                "tables/run_damage_targets.parquet",
                "tables/per_tooth_damage.parquet",
                "reports/target_quality_report.json",
            ),
            "naive": (
                "tables/baseline_metrics.parquet",
                "tables/baseline_predictions.parquet",
            ),
        }
        pinned = {
            name: load_pinned_run(
                config.repository_root,
                data["source_runs"][name],
                required_artifacts=paths,
            )
            for name, paths in required.items()
        }
        samples = pd.read_parquet(
            pinned["model_dataset"].artifact_path(
                "tables/model_sample_manifest.parquet"
            )
        )
        naive = pd.read_parquet(
            pinned["naive"].artifact_path("tables/baseline_metrics.parquet")
        )
        target_report = json.loads(
            pinned["target"]
            .artifact_path("reports/target_quality_report.json")
            .read_text()
        )
        if (
            target_report["classification"]
            != "PASS_PROVISIONAL_FOR_ENGINEERING_BASELINE"
        ):
            raise ConfigError(
                "RT-DETR regression requires the exact provisional engineering gate"
            )
        usage = shutil.disk_usage(config.repository_root)
        minimum = int(data["storage_limits"]["minimum_free_bytes"])
        if usage.free < minimum:
            raise ConfigError("free disk below configured 25 GiB floor")
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "formulation": data["model"]["formulation"],
                        "sample_count": len(samples),
                        "counts_by_split": samples.split.value_counts()
                        .sort_index()
                        .to_dict(),
                        "target_status": target_report["classification"],
                        "device_available": torch.cuda.is_available(),
                        "disk_free_bytes": usage.free,
                        "would_open_raw_images": False,
                        "would_train": False,
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
            pinned["inventory"].artifact_path("tables/archive_members.parquet"),
            asset_inventory=pinned["inventory"].artifact_path(
                "tables/asset_inventory.parquet"
            ),
            data_root=data_root,
        )
        sources_by_id = {source.source_member_id: source for source in sources}
        output = config.resolve_repository_path(
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
            study=data["study"],
            output_root=output,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/train_rtdetr_regression.py", *(argv or sys.argv[1:])],
            input_roots=tuple(item.relative_directory for item in pinned.values())
            + (dataset_data["dataset"]["data_root"],),
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
                "scipy",
                "PyYAML",
            ),
            source_runs=source_runs,
        )
        run.create_layout()
        checkpoint_dir = run.run_directory / "checkpoints"
        checkpoint_dir.mkdir()
        model_data = data["model"]
        download_options = RTDETRFeasibilityOptions(
            seed=int(data["seed"]),
            images_per_experiment=1,
            image_size=int(model_data["image_size"]),
            confidence_threshold=0.25,
            max_detections=300,
            device=model_data["device"],
            max_member_bytes=8_388_608,
            checkpoint_name=model_data["checkpoint_name"],
            checkpoint_url=model_data["checkpoint_url"],
            checkpoint_sha256=model_data["checkpoint_sha256"],
            checkpoint_size_bytes=int(model_data["checkpoint_size_bytes"]),
            trace_layers=(),
        )
        checkpoint = download_checkpoint(
            checkpoint_dir / model_data["checkpoint_name"], download_options
        )
        set_reproducible_seed(int(data["seed"]))
        feature_rows, tensor_shapes, examples, environment = extract_features(
            checkpoint,
            samples,
            sources_by_id,
            image_size=int(model_data["image_size"]),
            feature_layers=model_data["feature_layers"],
            device=model_data["device"],
        )
        train_data = data["training"]
        compute = "cuda:0" if torch.cuda.is_available() else "cpu"
        model, history, best, last, feature_scaler, target_scaler, training_summary = (
            train_head(
                feature_rows,
                seed=int(data["seed"]),
                hidden_dimension=int(model_data["hidden_dimension"]),
                dropout=float(model_data["dropout"]),
                max_epochs=int(train_data["max_epochs"]),
                patience=int(train_data["patience"]),
                batch_size=int(train_data["batch_size"]),
                learning_rate=float(train_data["learning_rate"]),
                weight_decay=float(train_data["weight_decay"]),
                tiny_overfit_steps=int(train_data["tiny_overfit_steps"]),
                tiny_overfit_size=int(train_data["tiny_overfit_size"]),
                device=compute,
            )
        )
        predictions = predict_all(
            model,
            feature_rows,
            feature_scaler,
            target_scaler,
            device=compute,
            model_run_id=run.run_id,
        )
        tooth, runs = aggregate_predictions(predictions)
        metrics = build_metrics(predictions, tooth, runs)
        environment = {
            **environment,
            "head_device": compute,
            "max_cuda_memory_allocated_bytes": (
                int(torch.cuda.max_memory_allocated())
                if torch.cuda.is_available()
                else 0
            ),
        }
        training_summary = {
            **training_summary,
            "target_status": target_report["classification"],
            "train_count": int(samples.split.eq("train").sum()),
            "validation_count": int(samples.split.eq("validation").sum()),
            "test_count": int(samples.split.eq("test").sum()),
            "test_used_for_tuning": False,
        }
        result = RegressionResult(
            feature_rows,
            history,
            predictions,
            tooth,
            runs,
            metrics,
            tensor_shapes,
            environment,
            training_summary,
            best,
            last,
            feature_scaler,
            target_scaler,
            examples,
        )
        resolved = {
            "schema_version": "1.0.0",
            "experiment_config": data,
            "target_status": target_report["classification"],
            "execution": {
                "device": compute,
                "encoder_frozen": True,
                "training_performed": True,
                "test_used_for_tuning": False,
                "starting_free_bytes": usage.free,
            },
        }
        inputs = [
            item.source_record(path)
            for item in pinned.values()
            for path in sorted(item.verified_hashes)
        ] + [
            {
                "source_type": "external_pretrained_checkpoint",
                "url": model_data["checkpoint_url"],
                "sha256": model_data["checkpoint_sha256"],
                "size_bytes": model_data["checkpoint_size_bytes"],
            }
        ]
        artifacts = write_regression_run(
            result,
            run=run,
            checkpoint=checkpoint,
            resolved_config=resolved,
            input_manifest=inputs,
            naive_metrics=naive,
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
                "training_summary": training_summary,
                "metrics": metrics.to_dict(orient="records"),
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
