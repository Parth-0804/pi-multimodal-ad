from __future__ import annotations

import numpy as np
import pandas as pd
from PIL import Image
import torch
from torch import nn

from pi_multimodal_ad.models.rtdetr_multitask import (
    PseudoBoxScalarDataset,
    RTDETRMultitask,
    collate_multitask,
    normalized_rtdetr_predictions,
)


class _FakeDetector(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.model = nn.ModuleList(
            [
                nn.Conv2d(3, 4, 3, padding=1),
                nn.Conv2d(4, 6, 3, padding=1),
                nn.Conv2d(6, 2, 1),
            ]
        )

    def _features(self, images: torch.Tensor) -> torch.Tensor:
        value = images
        for layer in self.model:
            value = torch.relu(layer(value))
        return value

    def loss(self, batch: dict[str, torch.Tensor]):
        value = self._features(batch["img"])
        detection = value.square().mean()
        return detection, {
            name: detection.detach() for name in ("giou_loss", "cls_loss", "l1_loss")
        }

    def predict(self, images: torch.Tensor):
        return self._features(images).mean(dim=(-2, -1))


def test_multitask_outputs_gradients_freezing_and_optimizer_step() -> None:
    detector = _FakeDetector()
    model = RTDETRMultitask(
        detector, feature_layer=1, feature_dimension=6, hidden_dimension=4, dropout=0.0
    )
    summary = model.freeze_detector_prefix(1)
    assert summary["detector_trainable_parameters"] > 0
    assert not any(p.requires_grad for p in detector.model[0].parameters())
    assert all(p.requires_grad for p in detector.model[1].parameters())
    batch = {
        "img": torch.randn(3, 3, 16, 16),
        "scalar_target": torch.tensor([1.0, 2.0, 3.0]),
    }
    result = model.training_loss(
        batch, target_mean=2.0, target_scale=1.0, lambda_regression=0.5
    )
    assert result.scalar_prediction.shape == (3,)
    assert result.total.ndim == 0
    result.total.backward()
    assert all(p.grad is None for p in detector.model[0].parameters())
    assert any(p.grad is not None for p in detector.model[1].parameters())
    assert all(p.grad is not None for p in model.scalar_head.parameters())
    before = model.scalar_head.network[0].weight.detach().clone()
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=1e-3
    )
    optimizer.step()
    assert not torch.equal(before, model.scalar_head.network[0].weight)
    model.close()


def test_multitask_inference_requires_no_target_tensor() -> None:
    model = RTDETRMultitask(
        _FakeDetector(),
        feature_layer=1,
        feature_dimension=6,
        hidden_dimension=4,
        dropout=0.0,
    )
    detection, scalar = model.inference(
        torch.randn(2, 3, 12, 12), target_mean=5.0, target_scale=2.0
    )
    assert detection.shape == (2, 2)
    assert scalar.shape == (2,)
    model.close()


def test_multitask_dataset_collation_and_native_box_conversion(tmp_path) -> None:
    image_path = tmp_path / "image.jpg"
    label_path = tmp_path / "image.txt"
    Image.fromarray(np.full((8, 16, 3), 128, dtype=np.uint8)).save(image_path)
    label_path.write_text("0 0.5 0.5 0.25 0.5\n", encoding="utf-8")
    frame = pd.DataFrame(
        [
            {
                "sample_id": "sample-1",
                "image_id": "image-1",
                "cache_image_path": image_path.name,
                "yolo_label_path": label_path.name,
                "target_value_pct": 2.5,
                "experiment": "EXP-B",
                "run": 1,
                "tooth_id": 2,
                "view_role": "canonical_tooth",
                "split": "train",
                "width": 16,
                "height": 8,
            }
        ]
    )
    dataset = PseudoBoxScalarDataset(
        frame, run_directory=tmp_path, image_size=12, augment=False, seed=7
    )
    batch = collate_multitask([dataset[0]])
    assert batch["img"].shape == (1, 3, 12, 12)
    assert batch["bboxes"].shape == (1, 4)
    assert batch["scalar_target"].tolist() == [2.5]
    raw = torch.tensor([[[0.5, 0.5, 0.25, 0.5, 0.8, 0.0]]])
    rows = normalized_rtdetr_predictions(
        raw, batch["metadata"], confidence_threshold=0.5, maximum_detections=10
    )
    assert len(rows) == 1
    assert rows[0]["x_min"] == 6.0
    assert rows[0]["x_max"] == 10.0
    assert rows[0]["y_min"] == 2.0
    assert rows[0]["y_max"] == 6.0
