"""Bounded pretrained RT-DETR inference when the PHM target gate is blocked."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Any
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from ..profiling.images import (
    ImageProfileOptions,
    ImageSource,
    materialize_image_source,
)
from ..reporting.common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
    write_csv,
)
from ..utils.artifacts import sha256_file
from ..utils.provenance import ArtifactRecord, RunContext

SCHEMA_VERSION = "1.0.0"
BRANCH = "PRETRAINED_STANDARD_RTDETR_INFERENCE_FEASIBILITY"


@dataclass(frozen=True, slots=True)
class RTDETRFeasibilityOptions:
    seed: int
    images_per_experiment: int
    image_size: int
    confidence_threshold: float
    max_detections: int
    device: int | str
    max_member_bytes: int
    checkpoint_name: str
    checkpoint_url: str
    checkpoint_sha256: str
    checkpoint_size_bytes: int
    trace_layers: tuple[Mapping[str, Any], ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("images_per_experiment", self.images_per_experiment),
            ("image_size", self.image_size),
            ("max_detections", self.max_detections),
            ("max_member_bytes", self.max_member_bytes),
            ("checkpoint_size_bytes", self.checkpoint_size_bytes),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not 0 <= self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be in [0, 1]")
        if len(self.checkpoint_sha256) != 64:
            raise ValueError("checkpoint_sha256 must be a SHA-256 hex digest")


@dataclass(slots=True)
class RTDETRFeasibilityResult:
    selected_images: list[dict[str, Any]]
    detections: list[dict[str, Any]]
    tensor_shapes: list[dict[str, Any]]
    class_counts: list[dict[str, Any]]
    qualitative_rows: list[dict[str, Any]]
    annotated_images: Mapping[str, np.ndarray]
    original_images: Mapping[str, np.ndarray]
    preprocessed_images: Mapping[str, np.ndarray]
    architecture_rows: list[dict[str, Any]]
    environment: Mapping[str, Any]
    summary: Mapping[str, Any]


def _stable_rank(seed: int, key: str) -> str:
    return sha256(f"{seed}:{key}".encode("utf-8")).hexdigest()


def select_balanced_images(
    image_profile: pd.DataFrame,
    *,
    images_per_experiment: int,
    seed: int,
) -> pd.DataFrame:
    """Round-robin deterministic selections across stage/role within each experiment."""

    required = {
        "image_id",
        "source_member_id",
        "experiment",
        "inspection_stage",
        "image_role",
        "header_status",
    }
    missing = required.difference(image_profile.columns)
    if missing:
        raise ValueError("image profile missing columns: " + ", ".join(sorted(missing)))
    available = image_profile[image_profile["header_status"].eq("ok")].copy()
    selected: list[pd.Series] = []
    for experiment in sorted(available["experiment"].astype(str).unique()):
        scoped = available[available["experiment"].astype(str).eq(experiment)].copy()
        groups: dict[tuple[str, str], list[pd.Series]] = defaultdict(list)
        for _, row in scoped.iterrows():
            groups[(str(row["inspection_stage"]), str(row["image_role"]))].append(row)
        for rows in groups.values():
            rows.sort(
                key=lambda row: (
                    _stable_rank(seed, str(row["image_id"])),
                    str(row["image_id"]),
                )
            )
        positions: Counter[tuple[str, str]] = Counter()
        keys = sorted(groups)
        while sum(1 for row in selected if str(row["experiment"]) == experiment) < min(
            images_per_experiment, len(scoped)
        ):
            changed = False
            for key in keys:
                position = positions[key]
                if position < len(groups[key]):
                    selected.append(groups[key][position])
                    positions[key] += 1
                    changed = True
                    if sum(
                        1 for row in selected if str(row["experiment"]) == experiment
                    ) >= min(images_per_experiment, len(scoped)):
                        break
            if not changed:
                break
    result = pd.DataFrame(selected)
    return result.sort_values(
        ["experiment", "inspection_stage", "image_role", "image_id"],
        kind="stable",
    ).reset_index(drop=True)


def download_checkpoint(path: Path, options: RTDETRFeasibilityOptions) -> Path:
    """Download one exact checkpoint with size and SHA-256 validation."""

    if path.exists():
        raise FileExistsError(f"checkpoint destination already exists: {path}")
    request = Request(
        options.checkpoint_url, headers={"User-Agent": "pi-multimodal-ad/1.0"}
    )
    written = 0
    digest = sha256()
    try:
        with urlopen(request, timeout=60) as response, path.open("xb") as handle:
            while block := response.read(1024 * 1024):
                written += len(block)
                if written > options.checkpoint_size_bytes:
                    raise ValueError("checkpoint exceeded configured size")
                handle.write(block)
                digest.update(block)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    if written != options.checkpoint_size_bytes:
        path.unlink(missing_ok=True)
        raise ValueError(
            f"checkpoint size mismatch: expected {options.checkpoint_size_bytes}, found {written}"
        )
    if digest.hexdigest() != options.checkpoint_sha256:
        path.unlink(missing_ok=True)
        raise ValueError("checkpoint SHA-256 mismatch")
    return path


def _shapes(value: object) -> object:
    import torch

    if isinstance(value, torch.Tensor):
        return list(value.shape)
    if isinstance(value, (tuple, list)):
        return [_shapes(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _shapes(item) for key, item in value.items()}
    return type(value).__name__


def _architecture_rows() -> list[dict[str, Any]]:
    return [
        {
            "option": "standard_detection_training",
            "required_evidence": "authoritative boxes and classes",
            "status": "REJECTED_FOR_SUPERVISED_PHM_EVALUATION",
            "reason": "D1.3 discovered no boxes/classes in the bounded archive listing",
        },
        {
            "option": "rtdetr_derived_scalar_regression",
            "required_evidence": "verified scalar target and image-target pairing",
            "status": "BLOCKED",
            "reason": "T2.1 target, six-hour meaning, pairing and leakage boundary are unresolved",
        },
        {
            "option": "pretrained_standard_inference_feasibility",
            "required_evidence": "readable images and executable pretrained checkpoint",
            "status": "SELECTED",
            "reason": "tests architecture execution only; no PHM predictive-performance claim",
        },
    ]


def run_inference(
    *,
    checkpoint: Path,
    selected: pd.DataFrame,
    sources_by_member_id: Mapping[str, ImageSource],
    options: RTDETRFeasibilityOptions,
) -> RTDETRFeasibilityResult:
    """Materialize and infer one selected PHM image at a time."""

    import cv2
    import torch
    import ultralytics
    from ultralytics import RTDETR

    if not torch.cuda.is_available() and str(options.device) not in {"cpu", "-1"}:
        raise RuntimeError("configured CUDA device is unavailable")
    model = RTDETR(str(checkpoint))
    parameter_count = sum(parameter.numel() for parameter in model.model.parameters())
    selected_rows: list[dict[str, Any]] = []
    detections: list[dict[str, Any]] = []
    shape_rows: list[dict[str, Any]] = []
    annotated: dict[str, np.ndarray] = {}
    originals: dict[str, np.ndarray] = {}
    preprocessed: dict[str, np.ndarray] = {}
    trace: dict[int, object] = {}
    handles = []
    for definition in options.trace_layers:
        index = int(definition["index"])
        handles.append(
            model.model.model[index].register_forward_hook(
                lambda _module, _inputs, output, index=index: trace.__setitem__(
                    index, _shapes(output)
                )
            )
        )
    image_options = ImageProfileOptions(
        mode="header", max_member_bytes=options.max_member_bytes
    )
    try:
        for image_index, row in selected.iterrows():
            source = sources_by_member_id.get(str(row["source_member_id"]))
            if source is None:
                raise ValueError(
                    f"selected source member not found: {row['source_member_id']}"
                )
            if source.archive_path is None:
                raise ValueError("PHM fallback expects archive image sources")
            before = source.archive_path.stat()
            wall_start = time.perf_counter()
            materialize_start = time.perf_counter()
            with materialize_image_source(source, options=image_options) as image_path:
                materialization_ms = (time.perf_counter() - materialize_start) * 1000
                with Image.open(image_path) as image:
                    rgb = np.asarray(image.convert("RGB"))
                bgr = np.ascontiguousarray(rgb[..., ::-1])
                results = model.predict(
                    bgr,
                    imgsz=options.image_size,
                    conf=options.confidence_threshold,
                    max_det=options.max_detections,
                    device=options.device,
                    verbose=False,
                )
            after = source.archive_path.stat()
            immutable = (
                before.st_size == after.st_size
                and before.st_mtime_ns == after.st_mtime_ns
            )
            result = results[0]
            image_id = str(row["image_id"])
            detection_count = len(result.boxes)
            speed = {str(key): float(value) for key, value in result.speed.items()}
            total_wall_ms = (time.perf_counter() - wall_start) * 1000
            selected_row = {
                "schema_version": SCHEMA_VERSION,
                "selection_index": int(image_index),
                "image_id": image_id,
                "source_member_id": str(row["source_member_id"]),
                "source_relative_path": str(row["source_relative_path"]),
                "experiment": str(row["experiment"]),
                "run": None if pd.isna(row["run"]) else int(row["run"]),
                "inspection_stage": str(row["inspection_stage"]),
                "tooth_id": None if pd.isna(row["tooth_id"]) else int(row["tooth_id"]),
                "image_role": str(row["image_role"]),
                "original_height": int(rgb.shape[0]),
                "original_width": int(rgb.shape[1]),
                "original_channels": int(rgb.shape[2]),
                "preprocessed_tensor_shape": json.dumps(
                    [1, 3, options.image_size, options.image_size],
                    separators=(",", ":"),
                ),
                "preprocessed_dtype": "float32",
                "preprocessed_value_range": "[0,1]",
                "resize_policy": "scale_fill_to_square_no_padding",
                "pixel_mask": "not_used_by_ultralytics_rtdetr_predictor",
                "detection_count": detection_count,
                "preprocess_ms": speed.get("preprocess"),
                "inference_ms": speed.get("inference"),
                "postprocess_ms": speed.get("postprocess"),
                "materialization_ms": materialization_ms,
                "total_wall_ms": total_wall_ms,
                "source_archive_unchanged": immutable,
                "result_status": (
                    "detections_retained"
                    if detection_count
                    else "no_retained_detections"
                ),
            }
            selected_rows.append(selected_row)
            boxes = result.boxes
            for detection_index in range(detection_count):
                xyxy = boxes.xyxy[detection_index].detach().cpu().tolist()
                class_id = int(boxes.cls[detection_index].detach().cpu().item())
                confidence = float(boxes.conf[detection_index].detach().cpu().item())
                detections.append(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "image_id": image_id,
                        "detection_index": detection_index,
                        "class_id": class_id,
                        "class_name": str(model.names[class_id]),
                        "confidence": confidence,
                        "x_min_pixels": float(xyxy[0]),
                        "y_min_pixels": float(xyxy[1]),
                        "x_max_pixels": float(xyxy[2]),
                        "y_max_pixels": float(xyxy[3]),
                        "box_format": "xyxy_original_image_pixels",
                        "ground_truth_available": False,
                        "phm_relevance_status": "UNVERIFIED_COCO_PREDICTION",
                    }
                )
            if len(annotated) < 12:
                annotated[image_id] = result.plot()[..., ::-1]
                originals[image_id] = rgb
                preprocessed[image_id] = cv2.resize(
                    rgb,
                    (options.image_size, options.image_size),
                    interpolation=cv2.INTER_LINEAR,
                )
    finally:
        for handle in handles:
            handle.remove()
    if not all(row["source_archive_unchanged"] for row in selected_rows):
        raise RuntimeError("a source archive size or modification time changed")
    for definition in options.trace_layers:
        index = int(definition["index"])
        shape_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "stage_order": index,
                "stage": str(definition["stage"]),
                "module_index": index,
                "output_shape_json": json.dumps(
                    trace.get(index), separators=(",", ":")
                ),
                "shape_scope": "first_selected_image_batch_size_1",
            }
        )
    class_counts = Counter(row["class_name"] for row in detections)
    class_rows = [
        {"schema_version": SCHEMA_VERSION, "class_name": name, "detection_count": count}
        for name, count in class_counts.most_common()
    ]
    sorted_images = sorted(
        selected_rows,
        key=lambda row: (-int(row["detection_count"]), str(row["image_id"])),
    )
    qualitative = []
    if sorted_images:
        qualitative.append(
            {
                "category": "retained_prediction_relevance_unverified",
                "image_id": sorted_images[0]["image_id"],
                "reason": "highest retained detection count; no PHM ground truth",
            }
        )
    if detections:
        highest = max(detections, key=lambda row: (row["confidence"], row["image_id"]))
        qualitative.append(
            {
                "category": "domain_mismatch_risk",
                "image_id": highest["image_id"],
                "reason": f"COCO class {highest['class_name']} has no established PHM tooth-damage semantics",
            }
        )
    empty = [row for row in selected_rows if not row["detection_count"]]
    if empty:
        qualitative.append(
            {
                "category": "no_retained_detection",
                "image_id": empty[0]["image_id"],
                "reason": "no prediction exceeded the configured confidence threshold",
            }
        )
    environment = {
        "schema_version": SCHEMA_VERSION,
        "library": "ultralytics",
        "library_version": ultralytics.__version__,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "device": str(model.predictor.device),
        "device_name": (
            torch.cuda.get_device_name(options.device)
            if torch.cuda.is_available() and str(options.device) not in {"cpu", "-1"}
            else "CPU"
        ),
        "model_parameter_count": parameter_count,
        "checkpoint_sha256": sha256_file(checkpoint),
        "checkpoint_size_bytes": checkpoint.stat().st_size,
        "pretrained_dataset": "COCO",
        "class_count": len(model.names),
        "fp16": bool(model.predictor.model.fp16),
        "max_cuda_memory_allocated_bytes": (
            int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0
        ),
    }
    latency = [float(row["inference_ms"]) for row in selected_rows]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "branch": BRANCH,
        "selected_image_count": len(selected_rows),
        "counts_by_experiment": dict(
            sorted(Counter(row["experiment"] for row in selected_rows).items())
        ),
        "total_detection_count": len(detections),
        "images_with_no_retained_detection": sum(
            not row["detection_count"] for row in selected_rows
        ),
        "retained_class_count": len(class_counts),
        "confidence_threshold": options.confidence_threshold,
        "inference_latency_ms_median": float(np.median(latency)),
        "inference_latency_ms_min": float(np.min(latency)),
        "inference_latency_ms_max": float(np.max(latency)),
        "raw_archives_opened": True,
        "raw_archives_modified": False,
        "training_performed": False,
        "phm_detection_ground_truth": False,
        "map_precision_recall_computed": False,
        "scalar_predictive_performance_computed": False,
    }
    return RTDETRFeasibilityResult(
        selected_images=selected_rows,
        detections=detections,
        tensor_shapes=shape_rows,
        class_counts=class_rows,
        qualitative_rows=qualitative,
        annotated_images=annotated,
        original_images=originals,
        preprocessed_images=preprocessed,
        architecture_rows=_architecture_rows(),
        environment=environment,
        summary=summary,
    )


def _basic_bar(
    frame: pd.DataFrame, label: str, value: str, title: str, ylabel: str
) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(frame[label].astype(str), frame[value], color=ACADEMIC_COLORS[0])
    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.tick_params(axis="x", rotation=35)
    figure.tight_layout()
    return figure


def _latency_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    frame = pd.DataFrame(rows)
    figure, axis = plt.subplots(figsize=(9, 5))
    for column, color in zip(
        ["preprocess_ms", "inference_ms", "postprocess_ms"],
        ACADEMIC_COLORS[:3],
        strict=True,
    ):
        axis.plot(
            range(1, len(frame) + 1),
            frame[column],
            marker="o",
            label=column,
            color=color,
        )
    axis.set_xlabel("Deterministic image index")
    axis.set_ylabel("Milliseconds")
    axis.set_title("RT-DETR preprocessing, inference and postprocessing latency")
    axis.legend()
    figure.tight_layout()
    return figure


def _montage(
    images: Mapping[str, np.ndarray], rows: Sequence[Mapping[str, Any]], title: str
) -> plt.Figure:
    chosen = [row for row in rows if row["image_id"] in images][:9]
    figure, axes = plt.subplots(3, 3, figsize=(12, 9))
    for axis in axes.flat:
        axis.axis("off")
    for axis, row in zip(axes.flat, chosen, strict=False):
        axis.imshow(images[str(row["image_id"])])
        axis.set_title(
            f"{row['experiment']} / {row['inspection_stage']}\n{row['detection_count']} retained",
            fontsize=8,
        )
        axis.axis("off")
    figure.suptitle(title)
    figure.tight_layout()
    return figure


def _preprocess_qa(result: RTDETRFeasibilityResult) -> plt.Figure:
    image_id = next(iter(result.original_images))
    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(result.original_images[image_id])
    axes[0].set_title("Original RGB: 1440×2560×3")
    axes[1].imshow(result.preprocessed_images[image_id])
    axes[1].set_title("Scale-filled model input visualization: 640×640×3")
    for axis in axes:
        axis.axis("off")
    figure.suptitle("Checkpoint-compatible preprocessing QA (source remains unchanged)")
    figure.tight_layout()
    return figure


def _qualitative_figure(result: RTDETRFeasibilityResult) -> plt.Figure:
    figure, axes = plt.subplots(1, 3, figsize=(15, 5))
    for axis in axes:
        axis.axis("off")
    for axis, row in zip(axes, result.qualitative_rows, strict=False):
        image = result.annotated_images.get(str(row["image_id"]))
        if image is not None:
            axis.imshow(image)
        axis.set_title(str(row["category"]).replace("_", " "), fontsize=10)
        axis.text(
            0.5,
            -0.05,
            str(row["reason"]),
            ha="center",
            va="top",
            wrap=True,
            transform=axis.transAxes,
            fontsize=8,
        )
    figure.suptitle(
        "Qualitative inference cases — no PHM ground truth or relevance labels"
    )
    figure.tight_layout()
    return figure


def _tensor_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(14, 4))
    axis.axis("off")
    stages = [
        "Input\n[1,3,640,640]",
        *[f"{row['stage']}\n{row['output_shape_json']}" for row in rows],
    ]
    for index, stage in enumerate(stages):
        x = 0.01 + index * (0.98 / len(stages))
        width = 0.88 / len(stages)
        patch = plt.Rectangle(
            (x, 0.35),
            width,
            0.32,
            facecolor="#EAF0F5",
            edgecolor=ACADEMIC_COLORS[0],
            transform=axis.transAxes,
        )
        axis.add_patch(patch)
        axis.text(
            x + width / 2,
            0.51,
            stage,
            ha="center",
            va="center",
            fontsize=7.5,
            transform=axis.transAxes,
            wrap=True,
        )
        if index < len(stages) - 1:
            axis.annotate(
                "",
                xy=(x + width + 0.012, 0.51),
                xytext=(x + width, 0.51),
                xycoords=axis.transAxes,
                arrowprops={"arrowstyle": "->"},
            )
    axis.set_title("RT-DETR tensor trace (first selected image, batch size 1)")
    return figure


def _architecture_markdown(result: RTDETRFeasibilityResult) -> str:
    lines = [
        "# RT-DETR architecture decision",
        "",
        "Selected branch: **Option 3 — pretrained standard RT-DETR inference feasibility**",
        "",
        "T2.1 is blocked, so no scalar regression target, image-target sample, split or training run is scientifically authorized. D1.3 discovered no authoritative boxes/classes, so supervised PHM detection evaluation is also unavailable.",
        "",
        "| Option | Status | Reason |",
        "|---|---|---|",
    ]
    for row in result.architecture_rows:
        lines.append(f"| {row['option']} | {row['status']} | {row['reason']} |")
    lines.extend(
        [
            "",
            "The selected standard checkpoint emits up to 300 COCO predictions per image in `[cx, cy, w, h, score, class]` decoder form, filtered by confidence and converted to original-image `xyxy` boxes. These outputs do not constitute PHM damage predictions.",
        ]
    )
    return "\n".join(lines) + "\n"


def _report_markdown(result: RTDETRFeasibilityResult) -> str:
    summary = result.summary
    environment = result.environment
    return "\n".join(
        [
            "# RT-DETR pretrained inference feasibility report",
            "",
            "> **Inference/architecture feasibility only — not PHM damage-prediction performance.**",
            "",
            "## Scientific status",
            "",
            "- No PHM detection ground truth was discovered; mAP, precision and recall are not computed.",
            "- T2.1 did not establish a scalar target or image pairing; scalar predictive performance is not computed.",
            "- No training, fine-tuning, sample split, naive regression baseline or test-set tuning occurred.",
            "- COCO classes have no established gear-tooth damage semantics.",
            "",
            "## Execution",
            "",
            f"- Checkpoint: `rtdetr-l.pt`, SHA-256 `{environment['checkpoint_sha256']}`",
            f"- Library: Ultralytics `{environment['library_version']}`; Torch `{environment['torch_version']}`",
            f"- Device: `{environment['device']}` ({environment['device_name']})",
            f"- Parameters: {environment['model_parameter_count']:,}",
            f"- Deterministic balanced subset: {summary['selected_image_count']} images ({summary['counts_by_experiment']})",
            f"- Confidence threshold: {summary['confidence_threshold']}",
            f"- Retained detections: {summary['total_detection_count']}; images with none: {summary['images_with_no_retained_detection']}",
            f"- Median model inference: {summary['inference_latency_ms_median']:.2f} ms/image (range {summary['inference_latency_ms_min']:.2f}–{summary['inference_latency_ms_max']:.2f} ms)",
            "",
            "## Preprocessing and tensors",
            "",
            "Ultralytics reads BGR arrays, scale-fills each 1440×2560 RGB source to 640×640 (aspect ratio is not preserved), converts BGR→RGB, transposes BHWC→BCHW, converts to float32 on CUDA and divides by 255. No padding/pixel mask is used by this predictor configuration. Exact traced shapes are in `tables/tensor_shapes.csv`.",
            "",
            "## Interpretation",
            "",
            "Retained boxes/classes/confidences prove that the installed standard RT-DETR architecture executes reproducibly on bounded PHM inputs. They do not show tooth-damage localization, target association, maintenance usefulness or generalization. A valid supervised baseline still requires either authoritative boxes/classes or a target-cleared RT-DETR-derived regression formulation.",
            "",
        ]
    )


def _figure_index() -> str:
    figures = (
        "detections_per_image",
        "confidence_distribution",
        "predicted_class_distribution",
        "images_with_no_retained_detections",
        "latency_distribution",
        "representative_detection_montage",
        "qualitative_inference_cases",
        "preprocessing_qa",
        "architecture_tensor_trace",
    )
    lines = [
        "# RT-DETR feasibility figure index",
        "",
        "All plots describe standard pretrained inference, not PHM predictive accuracy.",
        "",
    ]
    for name in figures:
        lines.extend(
            [f"- `figures/{name}.png` (300 DPI)", f"- `figures/{name}.svg`", ""]
        )
    return "\n".join(lines)


def write_rtdetr_feasibility_run(
    result: RTDETRFeasibilityResult,
    *,
    run: RunContext,
    checkpoint: Path,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
    apply_academic_style()
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    input_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        [
            run.artifact(config_path, role="resolved_configuration"),
            run.artifact(input_path, role="input_manifest"),
            run.artifact(checkpoint, role="pretrained_checkpoint"),
        ]
    )
    tables = {
        "inference_images": result.selected_images,
        "detections": result.detections,
        "tensor_shapes": result.tensor_shapes,
        "predicted_class_counts": result.class_counts,
        "architecture_options": result.architecture_rows,
        "qualitative_review": result.qualitative_rows,
    }
    for name, rows in tables.items():
        path = run.run_directory / f"tables/{name}.csv"
        write_csv(path, rows)
        artifacts.append(run.artifact(path, role=name))
    environment_path = run.run_directory / "reports/environment_device.json"
    environment_path.write_text(json_text(dict(result.environment)), encoding="utf-8")
    summary_path = run.run_directory / "reports/rtdetr_feasibility_summary.json"
    summary_path.write_text(json_text(dict(result.summary)), encoding="utf-8")
    architecture_path = run.run_directory / "reports/architecture_decision.md"
    architecture_path.write_text(_architecture_markdown(result), encoding="utf-8")
    report_path = run.run_directory / "reports/rtdetr_feasibility_report.md"
    report_path.write_text(_report_markdown(result), encoding="utf-8")
    figure_index_path = run.run_directory / "reports/figure_index.md"
    figure_index_path.write_text(_figure_index(), encoding="utf-8")
    for path, role in (
        (environment_path, "environment_device"),
        (summary_path, "rtdetr_feasibility_summary"),
        (architecture_path, "architecture_decision"),
        (report_path, "rtdetr_feasibility_report"),
        (figure_index_path, "figure_index"),
    ):
        artifacts.append(run.artifact(path, role=role))
    image_frame = pd.DataFrame(result.selected_images)
    detection_frame = pd.DataFrame(result.detections)
    figures: dict[str, plt.Figure] = {
        "detections_per_image": _basic_bar(
            image_frame,
            "image_id",
            "detection_count",
            "Retained pretrained detections per PHM image",
            "Detections",
        ),
        "images_with_no_retained_detections": _basic_bar(
            image_frame.assign(
                no_detection=image_frame["detection_count"].eq(0).astype(int)
            ),
            "image_id",
            "no_detection",
            "Images with no retained detections",
            "Indicator (1 = none)",
        ),
        "latency_distribution": _latency_figure(result.selected_images),
        "representative_detection_montage": _montage(
            result.annotated_images,
            result.selected_images,
            "Representative standard RT-DETR predictions (COCO; PHM relevance unverified)",
        ),
        "qualitative_inference_cases": _qualitative_figure(result),
        "preprocessing_qa": _preprocess_qa(result),
        "architecture_tensor_trace": _tensor_figure(result.tensor_shapes),
    }
    if detection_frame.empty:
        confidence = pd.DataFrame({"confidence": []})
    else:
        confidence = detection_frame
    confidence_figure, confidence_axis = plt.subplots(figsize=(8.5, 4.8))
    confidence_axis.hist(
        confidence.get("confidence", pd.Series(dtype=float)),
        bins=10,
        color=ACADEMIC_COLORS[1],
        edgecolor="white",
    )
    confidence_axis.set_title("Retained confidence distribution")
    confidence_axis.set_xlabel("Confidence")
    confidence_axis.set_ylabel("Detections")
    figures["confidence_distribution"] = confidence_figure
    class_frame = pd.DataFrame(result.class_counts)
    if class_frame.empty:
        class_frame = pd.DataFrame(
            {"class_name": ["No retained classes"], "detection_count": [0]}
        )
    figures["predicted_class_distribution"] = _basic_bar(
        class_frame.head(15),
        "class_name",
        "detection_count",
        "Retained pretrained COCO class distribution",
        "Detections",
    )
    for name, figure in figures.items():
        for path in save_figure_pair(figure, run.run_directory / f"figures/{name}"):
            artifacts.append(run.artifact(path, role=f"{name}_{path.suffix[1:]}"))
    return finalize_run(run, artifacts)
