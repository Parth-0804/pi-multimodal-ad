#!/usr/bin/env python3
"""Phase 4, item 8: qualitative backbone/encoder activation check.

Reuses the forward-hook machinery from
tutorials/rtdetr_storybook/rtdetr_storybook.py (StorybookHooks,
_find_first_module, _activation_heatmap) by importing that tutorial module
directly, rather than re-implementing hook registration. Runs the ACTUAL
fine-tuned best_detector.pt from the pinned detection run (not the stock
rtdetr-l.pt baseline the storybook tutorial uses) on the same representative
EXP-F images used in phase4_03's error taxonomy, to see whether the Eyes/
Brain stages are already localizing to the damage-streak region before the
head's box-scale mismatch (found in items 1-2) causes IoU@0.5 to fail.
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from PIL import Image
from ultralytics import RTDETR

REPO_ROOT = Path(__file__).resolve().parents[3]
STORYBOOK_DIR = REPO_ROOT / "tutorials" / "rtdetr_storybook"
sys.path.insert(0, str(STORYBOOK_DIR))
from rtdetr_storybook import StorybookHooks, _activation_heatmap  # noqa: E402

PSEUDO_RUN = (
    REPO_ROOT / "runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794"
)
DETECTION_RUN = (
    REPO_ROOT / "runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af"
)
OUT_DIR = Path(__file__).resolve().parents[1] / "analysis" / "04_activation_hooks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXAMPLE_STEMS = [
    "true_positive_present_image_sample_9ac",
    "true_positive_present_image_sample_02a",
    "false_negative_only_image_sample_000",
    "false_negative_only_image_sample_003",
]


def main() -> None:
    images = pd.read_parquet(PSEUDO_RUN / "tables/annotation_image_manifest.parquet")
    test_images = images[images.split == "test"].set_index("sample_id")
    examples_summary = pd.read_csv(
        Path(__file__).resolve().parents[1]
        / "analysis"
        / "03_error_taxonomy"
        / "per_image_category_summary.csv"
    )

    checkpoint = DETECTION_RUN / "checkpoints" / "best_detector.pt"
    model = RTDETR(str(checkpoint))
    print("Loaded fine-tuned checkpoint:", checkpoint)

    tp_ids = examples_summary[examples_summary.category == "true_positive_present"].sample_id.head(2)
    fn_ids = examples_summary[examples_summary.category == "false_negative_only"].sample_id.head(2)
    selected = list(tp_ids) + list(fn_ids)
    categories = ["true_positive_present"] * len(tp_ids) + ["false_negative_only"] * len(fn_ids)

    for sample_id, category in zip(selected, categories):
        meta = test_images.loc[sample_id]
        image_path = PSEUDO_RUN / meta.cache_image_path
        hooks = StorybookHooks(model.model)
        for label, class_name in hooks.found_modules.items():
            if class_name is None:
                print(f"  [note] could not find a layer for '{label}' on this checkpoint")
        results = model.predict(
            source=str(image_path), device="cpu", conf=0.0005, max_det=300, verbose=False
        )
        hooks.remove()

        with Image.open(image_path) as source:
            original = source.convert("RGB")

        eyes = hooks.captures.get("eyes")
        brain = hooks.captures.get("brain")
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(original)
        axes[0].set_title("Original photo")
        axes[0].axis("off")
        if eyes and eyes["output_tensor"] is not None:
            heat = _activation_heatmap(eyes["output_tensor"], original.size)
            axes[1].imshow(heat, cmap="magma")
        axes[1].set_title(f"Eyes (backbone: {hooks.found_modules.get('eyes')})")
        axes[1].axis("off")
        if brain and brain["output_tensor"] is not None:
            heat = _activation_heatmap(brain["output_tensor"], original.size)
            axes[2].imshow(heat, cmap="magma")
        axes[2].set_title(f"Brain (AIFI encoder: {hooks.found_modules.get('brain')})")
        axes[2].axis("off")
        fig.suptitle(
            f"{category}: {sample_id[:20]}... exp={meta.experiment} run={meta.run} "
            f"tooth={meta.tooth_id} — fine-tuned best_detector.pt activation energy"
        )
        fig.tight_layout()
        out_path = OUT_DIR / f"{category}_{sample_id[:16]}_activation.png"
        fig.savefig(out_path, dpi=130)
        plt.close(fig)
        print("wrote", out_path)

    print("\nWrote:")
    for path in sorted(OUT_DIR.iterdir()):
        print(" ", path)


if __name__ == "__main__":
    main()
