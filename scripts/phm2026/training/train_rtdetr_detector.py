#!/usr/bin/env python3
"""Train and evaluate one genuine RT-DETR detector on pinned PHM pseudo-boxes."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

import numpy as np
import pandas as pd
import torch
import yaml
from ultralytics import RTDETR
import ultralytics

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pi_multimodal_ad.models.rtdetr_detection import (  # noqa: E402
    average_precision,
    collect_predictions,
    deterministic_example_rows,
    select_confidence_threshold,
    sliced_metrics,
    write_detection_results,
)
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
    set_reproducible_seed,
)
from pi_multimodal_ad.utils.artifacts import sha256_file  # noqa: E402


def _device_information(device: int | str) -> dict[str, Any]:
    try:
        nvidia = subprocess.run(
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
        nvidia = "unavailable"
    return {
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "ultralytics_version": ultralytics.__version__,
        "device_request": str(device),
        "nvidia_smi": nvidia,
    }


def _validate_cache(
    pseudo_directory: Path, cache_manifest: pd.DataFrame
) -> dict[str, int]:
    image_count = label_count = total_bytes = 0
    for row in cache_manifest.sort_values("sample_id").itertuples(index=False):
        image = pseudo_directory / row.cache_image_path
        label = pseudo_directory / row.yolo_label_path
        if not image.is_file() or not label.is_file():
            raise ConfigError(f"missing cache image/label for {row.sample_id}")
        if sha256_file(image) != str(row.source_sha256):
            raise ConfigError(f"materialized cache hash mismatch for {row.sample_id}")
        image_count += 1
        label_count += 1
        total_bytes += image.stat().st_size + label.stat().st_size
    return {
        "cache_image_count": image_count,
        "cache_label_count": label_count,
        "cache_total_bytes": total_bytes,
    }


def _write_runtime_dataset(run_directory: Path, pseudo_directory: Path) -> Path:
    path = run_directory / "config/ultralytics_dataset_runtime.yaml"
    payload = {
        "path": str((pseudo_directory / "cache").resolve()),
        "train": "images/train",
        "val": "images/validation",
        "test": "images/test",
        "names": {0: "damage_candidate"},
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _augmentation(config: dict[str, Any]) -> dict[str, Any]:
    return {name: float(value) for name, value in config.items()}


def _common_train_kwargs(
    *,
    data_yaml: Path,
    run_directory: Path,
    model_config: dict[str, Any],
    training: dict[str, Any],
    seed: int,
) -> dict[str, Any]:
    return {
        "data": str(data_yaml),
        "imgsz": int(model_config["image_size"]),
        "batch": int(model_config["batch_size"]),
        "workers": int(model_config["workers"]),
        "device": model_config["device"],
        "seed": seed,
        "deterministic": bool(training["deterministic"]),
        "optimizer": training["optimizer"],
        "amp": bool(training["amp"]),
        "project": str(run_directory / "logs"),
        "exist_ok": False,
        "save_period": -1,
        "plots": False,
        "val": True,
        "cache": False,
        "max_det": int(model_config["max_detections"]),
        "verbose": False,
        **_augmentation(training["augmentation"]),
    }


def _read_history(directory: Path, stage: str) -> pd.DataFrame:
    path = directory / "results.csv"
    if not path.is_file():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    frame.columns = [column.strip() for column in frame]
    frame.insert(0, "stage", stage)
    frame.insert(1, "stage_epoch", np.arange(1, len(frame) + 1))
    return frame


def _parameter_counts(model: RTDETR, frozen_layers: int) -> dict[str, int]:
    layers = model.model.model
    total = sum(parameter.numel() for parameter in model.model.parameters())
    frozen = sum(
        parameter.numel()
        for layer in layers[:frozen_layers]
        for parameter in layer.parameters()
    )
    return {
        "total_parameters": total,
        "configured_frozen_parameters": frozen,
        "configured_trainable_parameters": total - frozen,
        "configured_frozen_layer_count": frozen_layers,
    }


def _shape_payload(value: Any) -> Any:
    if isinstance(value, torch.Tensor):
        return list(value.shape)
    if isinstance(value, (list, tuple)):
        return [_shape_payload(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _shape_payload(item) for key, item in value.items()}
    return type(value).__name__


def _trace_shapes(
    checkpoint: Path,
    sample_path: Path,
    *,
    image_size: int,
    device: int | str,
) -> pd.DataFrame:
    model = RTDETR(str(checkpoint))
    captured: dict[int, Any] = {}
    handles = [
        model.model.model[index].register_forward_hook(
            lambda _module, _inputs, output, index=index: captured.__setitem__(
                index, output
            )
        )
        for index in (21, 24, 27, 28)
    ]
    try:
        model.predict(
            source=str(sample_path),
            imgsz=image_size,
            device=device,
            conf=0.25,
            verbose=False,
        )
    finally:
        for handle in handles:
            handle.remove()
    rows = [
        {
            "stage": "input_tensor",
            "shape_json": json.dumps([1, 3, image_size, image_size]),
            "meaning": "RGB float32/255 after Ultralytics resize",
        }
    ]
    for index in (21, 24, 27):
        rows.append(
            {
                "stage": f"multiscale_encoder_layer_{index}",
                "shape_json": json.dumps(_shape_payload(captured[index])),
                "meaning": "RT-DETR multiscale encoder feature",
            }
        )
    rows.append(
        {
            "stage": "decoder_and_detection_heads",
            "shape_json": json.dumps(_shape_payload(captured[28])),
            "meaning": "transformer decoder queries, class scores and boxes",
        }
    )
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_rtdetr_detection.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        pseudo = load_pinned_run(
            config.repository_root,
            data["source_runs"]["pseudo_boxes"],
            required_artifacts=(
                "tables/annotation_image_manifest.parquet",
                "tables/annotation_manifest.parquet",
                "tables/coco_annotations.json",
                "reports/annotation_quality.json",
                "manifests/materialized_cache.parquet",
            ),
        )
        pretrained = load_pinned_run(
            config.repository_root,
            data["source_runs"]["pretrained"],
            required_artifacts=("checkpoints/rtdetr-l.pt",),
        )
        images = pd.read_parquet(
            pseudo.artifact_path("tables/annotation_image_manifest.parquet")
        )
        ground_truth = pd.read_parquet(
            pseudo.artifact_path("tables/annotation_manifest.parquet")
        )
        cache_manifest = pd.read_parquet(
            pseudo.artifact_path("manifests/materialized_cache.parquet")
        )
        quality = json.loads(
            pseudo.artifact_path("reports/annotation_quality.json").read_text()
        )
        if quality["status"] != "PROVISIONAL_PSEUDO_BOXES_FOR_ENGINEERING_BASELINE":
            raise ConfigError("pseudo-box quality gate did not pass")
        actual_splits = images.groupby(["split", "experiment"]).size().to_dict()
        expected_splits = {
            ("train", "EXP-B"): 448,
            ("validation", "EXP-A"): 323,
            ("test", "EXP-F"): 224,
        }
        if actual_splits != expected_splits:
            raise ConfigError(f"frozen split mismatch: {actual_splits}")
        cache_validation = _validate_cache(pseudo.directory, cache_manifest)
        usage = shutil.disk_usage(config.repository_root)
        minimum_free = int(data["storage_limits"]["minimum_free_bytes"])
        if usage.free < minimum_free:
            raise ConfigError("free disk is below 50 GiB")
        device_info = _device_information(data["model"]["device"])
        if not device_info["cuda_available"]:
            raise ConfigError("canonical RT-DETR training requires the available GPU")
        if ultralytics.__version__ != str(data["model"]["version"]):
            raise ConfigError(
                "installed Ultralytics version differs from configuration"
            )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "split_counts": {
                            split: int(count)
                            for split, count in images.groupby("split").size().items()
                        },
                        "cache_validation": cache_validation,
                        "pseudo_box_count": len(ground_truth),
                        "disk_free_bytes": usage.free,
                        "device": device_info,
                        "would_train": False,
                        "would_evaluate_test": False,
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
        source_runs = [
            {
                "name": name,
                "run_id": pinned.run_id,
                "directory": pinned.relative_directory,
                "artifacts": dict(pinned.verified_hashes),
            }
            for name, pinned in (("pseudo_boxes", pseudo), ("pretrained", pretrained))
        ]
        run = create_run_context(
            study=data["study"],
            output_root=output_root,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/training/train_rtdetr_detector.py", *(argv or sys.argv[1:])],
            input_roots=(pseudo.relative_directory, pretrained.relative_directory),
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
        (run.run_directory / "checkpoints").mkdir()
        data_yaml = _write_runtime_dataset(run.run_directory, pseudo.directory)
        model_config = data["model"]
        training = data["training"]
        common = _common_train_kwargs(
            data_yaml=data_yaml,
            run_directory=run.run_directory,
            model_config=model_config,
            training=training,
            seed=int(data["seed"]),
        )
        checkpoint = pretrained.artifact_path("checkpoints/rtdetr-l.pt")
        set_reproducible_seed(int(data["seed"]))
        training_started = time.perf_counter()
        smoke = training["smoke"]
        smoke_kwargs = {
            **common,
            "batch": int(smoke["batch_size"]),
        }
        RTDETR(str(checkpoint)).train(
            **smoke_kwargs,
            name="smoke",
            epochs=int(smoke["epochs"]),
            fraction=float(smoke["fraction"]),
            freeze=int(smoke["frozen_layers"]),
            lr0=float(training["warmup"]["learning_rate"]),
            save=False,
        )
        gc.collect()
        torch.cuda.empty_cache()
        warm = training["warmup"]
        RTDETR(str(checkpoint)).train(
            **common,
            name="warmup",
            epochs=int(warm["epochs"]),
            freeze=int(warm["frozen_layers"]),
            lr0=float(warm["learning_rate"]),
            lrf=0.1,
            warmup_epochs=0.0,
            save=True,
        )
        gc.collect()
        torch.cuda.empty_cache()
        warm_best = run.run_directory / "logs/warmup/weights/best.pt"
        if not warm_best.is_file():
            raise RuntimeError("warm-up best checkpoint was not produced")
        fine = training["finetune"]
        RTDETR(str(warm_best)).train(
            **common,
            name="finetune",
            epochs=int(fine["maximum_epochs"]),
            patience=int(fine["patience"]),
            freeze=int(fine["frozen_layers"]),
            lr0=float(fine["learning_rate"]),
            lrf=float(fine["final_learning_rate_fraction"]),
            weight_decay=float(fine["weight_decay"]),
            warmup_epochs=1.0,
            save=True,
        )
        gc.collect()
        torch.cuda.empty_cache()
        training_seconds = time.perf_counter() - training_started
        fine_weights = run.run_directory / "logs/finetune/weights"
        fine_best = fine_weights / "best.pt"
        fine_last = fine_weights / "last.pt"
        if not fine_best.is_file() or not fine_last.is_file():
            raise RuntimeError("fine-tuning did not produce best and last checkpoints")
        best_checkpoint = run.run_directory / "checkpoints/best_detector.pt"
        last_checkpoint = run.run_directory / "checkpoints/last_detector.pt"
        shutil.copyfile(fine_best, best_checkpoint)
        shutil.copyfile(fine_last, last_checkpoint)
        best_model = RTDETR(str(best_checkpoint))
        validation_images = images[images.split.eq("validation")].copy()
        test_images = images[images.split.eq("test")].copy()
        validation_truth = ground_truth[
            ground_truth.sample_id.isin(validation_images.sample_id)
        ].copy()
        test_truth = ground_truth[
            ground_truth.sample_id.isin(test_images.sample_id)
        ].copy()
        validation_predictions, _ = collect_predictions(
            best_model,
            validation_images,
            pseudo_run_directory=pseudo.directory,
            image_size=int(model_config["image_size"]),
            batch_size=int(model_config["batch_size"]),
            device=model_config["device"],
            minimum_confidence=float(model_config["minimum_inference_confidence"]),
            max_detections=int(model_config["max_detections"]),
        )
        selected_confidence, threshold_curve = select_confidence_threshold(
            validation_predictions,
            validation_truth,
            validation_images,
            candidates=data["validation_selection"]["confidence_candidates"],
        )
        # This is the sole EXP-F model inference/evaluation pass.
        test_predictions, test_latency = collect_predictions(
            best_model,
            test_images,
            pseudo_run_directory=pseudo.directory,
            image_size=int(model_config["image_size"]),
            batch_size=int(model_config["batch_size"]),
            device=model_config["device"],
            minimum_confidence=float(model_config["minimum_inference_confidence"]),
            max_detections=int(model_config["max_detections"]),
        )
        test_metrics = sliced_metrics(
            test_predictions,
            test_truth,
            test_images,
            confidence_threshold=selected_confidence,
        )
        ap_by_iou = pd.DataFrame(
            {
                "iou_threshold": np.linspace(0.5, 0.95, 10),
                "average_precision": [
                    average_precision(
                        test_predictions,
                        test_truth,
                        test_images,
                        iou_threshold=float(value),
                    )
                    for value in np.linspace(0.5, 0.95, 10)
                ],
                "status": "pseudo_box_agreement_only",
            }
        )
        examples = deterministic_example_rows(
            test_predictions,
            test_truth,
            test_images,
            confidence_threshold=selected_confidence,
        )
        example_truth = {
            str(sample_id): group[["x_min", "y_min", "x_max", "y_max"]]
            .astype(float)
            .values.tolist()
            for sample_id, group in test_truth[
                test_truth.sample_id.isin(examples.sample_id)
            ].groupby("sample_id")
        }
        history = pd.concat(
            (
                _read_history(run.run_directory / "logs/warmup", "warmup"),
                _read_history(run.run_directory / "logs/finetune", "finetune"),
            ),
            ignore_index=True,
        )
        trace_sample = (
            pseudo.directory
            / validation_images.sort_values("sample_id").iloc[0].cache_image_path
        )
        tensor_shapes = _trace_shapes(
            best_checkpoint,
            trace_sample,
            image_size=int(model_config["image_size"]),
            device=model_config["device"],
        )
        environment = {
            **device_info,
            "training_seconds": training_seconds,
            "peak_cuda_memory_allocated_bytes": int(torch.cuda.max_memory_allocated()),
            "smoke": _parameter_counts(
                RTDETR(str(checkpoint)), int(smoke["frozen_layers"])
            ),
            "warmup": _parameter_counts(
                RTDETR(str(warm_best)), int(warm["frozen_layers"])
            ),
            "finetune": _parameter_counts(best_model, int(fine["frozen_layers"])),
            "optimizer_groups": {
                "optimizer": training["optimizer"],
                "warmup_lr": warm["learning_rate"],
                "finetune_lr": fine["learning_rate"],
                "weight_decay": fine["weight_decay"],
            },
            "test_evaluation_passes": 1,
            "exp_f_used_for_tuning": False,
            "cache_validation": cache_validation,
        }
        resolved = {
            "schema_version": "1.0.0",
            "experiment_config": data,
            "execution": {
                "starting_free_bytes": usage.free,
                "training_seconds": training_seconds,
                "selected_confidence_from_exp_a": selected_confidence,
                "exp_f_evaluation_passes": 1,
                "exp_f_used_for_tuning": False,
                "raw_archives_opened": False,
                "raw_archives_modified": False,
            },
            "example_ground_truth": example_truth,
        }
        inputs = [
            pinned.source_record(path)
            for pinned in (pseudo, pretrained)
            for path in sorted(pinned.verified_hashes)
        ]
        artifacts = write_detection_results(
            run=run,
            validation_predictions=validation_predictions,
            test_predictions=test_predictions,
            validation_thresholds=threshold_curve,
            test_metrics=test_metrics,
            latency=test_latency,
            history=history,
            tensor_shapes=tensor_shapes,
            examples=examples,
            ap_by_iou=ap_by_iou,
            pseudo_run_directory=pseudo.directory,
            confidence_threshold=selected_confidence,
            resolved_config=resolved,
            input_manifest=inputs,
            environment=environment,
            extra_artifacts=(
                (data_yaml, "ultralytics_runtime_dataset"),
                (best_checkpoint, "best_detector_checkpoint"),
                (last_checkpoint, "last_detector_checkpoint"),
            ),
        )
        # Only final best/last checkpoints are retained; these directories are
        # temporary products made by this command and have already been hashed.
        for weights in (run.run_directory / "logs").glob("*/weights"):
            shutil.rmtree(weights)
    except (
        ConfigError,
        KeyError,
        OSError,
        RuntimeError,
        subprocess.CalledProcessError,
        TypeError,
        ValueError,
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
                "selected_validation_confidence": selected_confidence,
                "test_metrics": test_metrics.to_dict(orient="records"),
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
