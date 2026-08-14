"Multitask RT-DETR core with genuine detection loss and scalar damage head."

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image
import torch
from torch import nn
from torch.utils.data import Dataset
from torch.nn import functional as F

MULTITASK_SCHEMA_VERSION = "1.0.0"
MULTITASK_STATUS = "PROVISIONAL_PSEUDO_TARGET_AGREEMENT_ONLY"


class ScalarDamageHead(nn.Module):
    "Global-pool an encoder feature map and predict one scalar per image."

    def __init__(
        self, feature_dimension: int, hidden_dimension: int = 128, dropout: float = 0.1
    ) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(feature_dimension, hidden_dimension),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dimension, 1),
        )

    def forward(self, feature: torch.Tensor) -> torch.Tensor:
        if feature.ndim == 4:
            feature = feature.mean(dim=(-2, -1))
        if feature.ndim != 2:
            raise RuntimeError(
                f"expected a BCHW or BC encoder feature, got {tuple(feature.shape)}"
            )
        return self.network(feature).squeeze(-1)


@dataclass(frozen=True, slots=True)
class MultitaskLoss:
    total: torch.Tensor
    detection: torch.Tensor
    regression: torch.Tensor
    scalar_prediction: torch.Tensor
    detection_items: dict[str, torch.Tensor]


class RTDETRMultitask(nn.Module):
    "Attach a scalar head to an RT-DETR encoder without detaching features."

    def __init__(
        self,
        detector: nn.Module,
        *,
        feature_layer: int,
        feature_dimension: int,
        hidden_dimension: int = 128,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if not hasattr(detector, "model"):
            raise TypeError("detector must expose its ordered RT-DETR model layers")
        self.detector = detector
        if getattr(self.detector, "criterion", None) is None and callable(
            getattr(self.detector, "init_criterion", None)
        ):
            self.detector.criterion = self.detector.init_criterion()
        self.feature_layer = int(feature_layer)
        self.scalar_head = ScalarDamageHead(
            feature_dimension, hidden_dimension, dropout
        )
        self._feature: torch.Tensor | None = None
        self._hook = self.detector.model[self.feature_layer].register_forward_hook(
            self._capture_feature
        )

    def _capture_feature(
        self, _module: nn.Module, _inputs: tuple[Any, ...], output: Any
    ) -> None:
        if not isinstance(output, torch.Tensor):
            raise RuntimeError(
                f"RT-DETR layer {self.feature_layer} returned a non-tensor feature"
            )
        self._feature = output

    def _scalar_scaled(self) -> torch.Tensor:
        if self._feature is None:
            raise RuntimeError("configured RT-DETR encoder feature was not produced")
        return self.scalar_head(self._feature)

    def freeze_detector_prefix(self, layer_count: int) -> dict[str, int]:
        layers = self.detector.model
        if layer_count < 0 or layer_count > len(layers):
            raise ValueError("invalid frozen detector layer count")
        for index, layer in enumerate(layers):
            trainable = index >= layer_count
            for parameter in layer.parameters():
                parameter.requires_grad = trainable
        return self.parameter_summary()

    def parameter_summary(self) -> dict[str, int]:
        detector_parameters = list(self.detector.parameters())
        head_parameters = list(self.scalar_head.parameters())
        return {
            "detector_parameters": sum(p.numel() for p in detector_parameters),
            "detector_trainable_parameters": sum(
                p.numel() for p in detector_parameters if p.requires_grad
            ),
            "scalar_head_parameters": sum(p.numel() for p in head_parameters),
            "scalar_head_trainable_parameters": sum(
                p.numel() for p in head_parameters if p.requires_grad
            ),
        }

    def training_loss(
        self,
        batch: dict[str, torch.Tensor],
        *,
        target_mean: float,
        target_scale: float,
        lambda_regression: float,
    ) -> MultitaskLoss:
        if lambda_regression < 0:
            raise ValueError("lambda_regression must be nonnegative")
        if target_scale <= 0:
            raise ValueError("target_scale must be positive")
        self._feature = None
        detection, detection_items = self.detector.loss(batch)
        scalar_scaled = self._scalar_scaled()
        target = batch["scalar_target"].to(
            scalar_scaled.device, dtype=scalar_scaled.dtype
        )
        target_scaled = (target - target_mean) / target_scale
        regression = F.smooth_l1_loss(scalar_scaled, target_scaled)
        total = detection + float(lambda_regression) * regression
        scalar = scalar_scaled * target_scale + target_mean
        return MultitaskLoss(
            total, detection, regression, scalar, dict(detection_items)
        )

    def inference(
        self,
        images: torch.Tensor,
        *,
        target_mean: float,
        target_scale: float,
    ) -> tuple[Any, torch.Tensor]:
        if target_scale <= 0:
            raise ValueError("target_scale must be positive")
        self._feature = None
        predictions = self.detector.predict(images)
        scalar = self._scalar_scaled() * target_scale + target_mean
        return predictions, scalar

    def close(self) -> None:
        self._hook.remove()


class PseudoBoxScalarDataset(Dataset[dict[str, Any]]):
    "Deterministic 640-square image, pseudo-box and scalar-target dataset."

    def __init__(
        self,
        manifest: pd.DataFrame,
        *,
        run_directory: Path,
        image_size: int,
        augment: bool,
        seed: int,
    ) -> None:
        required = {
            "sample_id",
            "cache_image_path",
            "yolo_label_path",
            "target_value_pct",
            "experiment",
            "run",
            "tooth_id",
            "view_role",
            "split",
            "width",
            "height",
            "image_id",
        }
        missing = sorted(required - set(manifest.columns))
        if missing:
            raise ValueError(f"multitask manifest missing columns: {missing}")
        self.frame = manifest.sort_values("sample_id", kind="stable").reset_index(
            drop=True
        )
        self.run_directory = Path(run_directory)
        self.image_size = int(image_size)
        self.augment = bool(augment)
        self.seed = int(seed)

    def __len__(self) -> int:
        return len(self.frame)

    def _flip(self, sample_id: str) -> bool:
        if not self.augment:
            return False
        digest = hashlib.sha256(
            f"{self.seed}:{sample_id}:horizontal_flip".encode()
        ).digest()
        return int.from_bytes(digest[:8], "big") < 2**63

    def __getitem__(self, index: int) -> dict[str, Any]:
        row = self.frame.iloc[index]
        image_path = self.run_directory / str(row.cache_image_path)
        label_path = self.run_directory / str(row.yolo_label_path)
        with Image.open(image_path) as source:
            rgb = source.convert("RGB").resize(
                (self.image_size, self.image_size), Image.Resampling.BILINEAR
            )
            image = np.asarray(rgb, dtype=np.uint8).copy()
        labels: list[list[float]] = []
        for line in label_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            values = [float(value) for value in line.split()]
            if len(values) != 5:
                raise ValueError(f"malformed YOLO row in {label_path}")
            labels.append(values)
        flipped = self._flip(str(row.sample_id))
        if flipped:
            image = np.ascontiguousarray(image[:, ::-1, :])
            for values in labels:
                values[1] = 1.0 - values[1]
        boxes = torch.tensor([value[1:] for value in labels], dtype=torch.float32)
        classes = torch.tensor([[value[0]] for value in labels], dtype=torch.float32)
        return {
            "img": torch.from_numpy(image).permute(2, 0, 1),
            "bboxes": boxes.reshape(-1, 4),
            "cls": classes.reshape(-1, 1),
            "scalar_target": torch.tensor(float(row.target_value_pct)),
            "sample_id": str(row.sample_id),
            "image_id": str(row.image_id),
            "experiment": str(row.experiment),
            "run": int(row.run),
            "tooth_id": int(row.tooth_id),
            "view_role": str(row.view_role),
            "split": str(row.split),
            "original_width": int(row.width),
            "original_height": int(row.height),
            "horizontal_flip": flipped,
            "target_definition_version": str(
                row.get("target_definition_version", "unknown")
            ),
            "target_verification_status": "provisional_pending_human_review",
            "source_archive": str(row.get("source_archive", "")),
            "source_member": str(row.get("source_member", "")),
        }


def collate_multitask(samples: list[dict[str, Any]]) -> dict[str, Any]:
    "Collate variable-count YOLO boxes and scalar targets."
    boxes = []
    classes = []
    batch_indices = []
    metadata = []
    for index, sample in enumerate(samples):
        count = len(sample["bboxes"])
        boxes.append(sample["bboxes"])
        classes.append(sample["cls"])
        batch_indices.append(torch.full((count,), index, dtype=torch.long))
        metadata.append(
            {
                key: value
                for key, value in sample.items()
                if key not in {"img", "bboxes", "cls", "scalar_target"}
            }
        )
    return {
        "img": torch.stack([sample["img"] for sample in samples]).float() / 255.0,
        "bboxes": torch.cat(boxes, dim=0),
        "cls": torch.cat(classes, dim=0),
        "batch_idx": torch.cat(batch_indices, dim=0),
        "scalar_target": torch.stack([sample["scalar_target"] for sample in samples]),
        "metadata": metadata,
    }


def move_multitask_batch(batch: dict[str, Any], device: torch.device) -> dict[str, Any]:
    "Move only tensor fields, preserving traceability metadata on CPU."
    return {
        key: (
            value.to(device, non_blocking=True)
            if isinstance(value, torch.Tensor)
            else value
        )
        for key, value in batch.items()
    }


def normalized_rtdetr_predictions(
    predictions: Any,
    metadata: list[dict[str, Any]],
    *,
    confidence_threshold: float,
    maximum_detections: int,
) -> list[dict[str, Any]]:
    "Convert RT-DETR normalized xywh outputs into source-image xyxy rows."
    raw = predictions[0] if isinstance(predictions, (list, tuple)) else predictions
    if not isinstance(raw, torch.Tensor) or raw.ndim != 3 or raw.shape[-1] != 6:
        raise RuntimeError("unexpected RT-DETR inference output shape")
    rows: list[dict[str, Any]] = []
    for image_index, (image_predictions, identity) in enumerate(
        zip(raw.detach().cpu(), metadata, strict=True)
    ):
        keep = image_predictions[:, 4].ge(confidence_threshold).nonzero().flatten()
        keep = keep[
            torch.argsort(image_predictions[keep, 4], descending=True, stable=True)
        ][:maximum_detections]
        for position, selected in enumerate(keep.tolist()):
            cx, cy, width, height, confidence, class_id = image_predictions[
                selected
            ].tolist()
            source_width = float(identity["original_width"])
            source_height = float(identity["original_height"])
            rows.append(
                {
                    "prediction_id": str(identity["sample_id"]) + f":{position:04d}",
                    "sample_id": identity["sample_id"],
                    "image_id": identity["image_id"],
                    "experiment": identity["experiment"],
                    "run": identity["run"],
                    "tooth_id": identity["tooth_id"],
                    "view_role": identity["view_role"],
                    "split": identity["split"],
                    "class_id": int(class_id),
                    "class_name": "damage_candidate",
                    "confidence": float(confidence),
                    "x_min": max(0.0, (cx - width / 2) * source_width),
                    "y_min": max(0.0, (cy - height / 2) * source_height),
                    "x_max": min(source_width, (cx + width / 2) * source_width),
                    "y_max": min(source_height, (cy + height / 2) * source_height),
                    "status": MULTITASK_STATUS,
                    "batch_image_index": image_index,
                }
            )
    return rows
