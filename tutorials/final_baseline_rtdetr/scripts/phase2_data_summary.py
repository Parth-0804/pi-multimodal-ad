#!/usr/bin/env python3
"""Phase 2: read-only data-summary tables for the pinned RT-DETR split.

Reads only from the two pinned, already-generated runs named in PLAN.md
(pseudo-box run and detection run). Writes summary tables/figures under
tutorials/final_baseline_rtdetr/data_summary/. Never writes into runs/,
never extracts/copies raw PHM images, never modifies gtc-data-experiment/.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
PSEUDO_RUN = (
    REPO_ROOT
    / "runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794"
)
OUT_DIR = Path(__file__).resolve().parents[1] / "data_summary"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    images = pd.read_parquet(PSEUDO_RUN / "tables/annotation_image_manifest.parquet")
    boxes = pd.read_parquet(PSEUDO_RUN / "tables/annotation_manifest.parquet")
    boxes = boxes.assign(
        box_width=boxes.x_max - boxes.x_min,
        box_height=boxes.y_max - boxes.y_min,
        box_area=(boxes.x_max - boxes.x_min) * (boxes.y_max - boxes.y_min),
    )

    # --- 1. split x experiment x view_role composition ---
    composition = (
        images.groupby(["split", "experiment", "view_role"])
        .size()
        .reset_index(name="image_count")
        .sort_values(["split", "experiment", "view_role"])
    )
    composition.to_csv(OUT_DIR / "split_view_role_composition.csv", index=False)

    view_role_share = (
        images.groupby(["split", "view_role"]).size().unstack(fill_value=0)
    )
    view_role_share_pct = (
        100 * view_role_share.div(view_role_share.sum(axis=1), axis=0)
    ).round(1)
    view_role_share_pct.to_csv(OUT_DIR / "view_role_share_pct_by_split.csv")

    # --- 2. per-split, per-image box-count and box-size summary ---
    # `images.box_count` is the manifest's own pinned column; cross-check it
    # against a fresh groupby of the box table to confirm they agree before
    # trusting it.
    recomputed = boxes.groupby("sample_id").size().rename("recomputed_box_count")
    check = images.set_index("sample_id")[["box_count"]].join(recomputed, how="left")
    check["recomputed_box_count"] = check["recomputed_box_count"].fillna(0).astype(int)
    mismatches = int((check.box_count != check.recomputed_box_count).sum())
    if mismatches:
        raise RuntimeError(
            f"{mismatches} images have annotation_manifest box counts that "
            "disagree with annotation_image_manifest.box_count; investigate "
            "before trusting either."
        )
    images_with_counts = images.set_index("sample_id")

    split_summary_rows = []
    for split, group in images_with_counts.groupby("split"):
        experiment = group.experiment.iloc[0]
        split_boxes = boxes[boxes.sample_id.isin(group.index)]
        split_summary_rows.append(
            {
                "split": split,
                "experiment": experiment,
                "image_count": len(group),
                "total_box_count": len(split_boxes),
                "mean_boxes_per_image": float(group.box_count.mean()),
                "median_boxes_per_image": float(group.box_count.median()),
                "min_boxes_per_image": int(group.box_count.min()),
                "max_boxes_per_image": int(group.box_count.max()),
                "median_box_width_px": float(split_boxes.box_width.median()),
                "median_box_height_px": float(split_boxes.box_height.median()),
                "median_box_area_px2": float(split_boxes.box_area.median()),
                "mean_box_area_px2": float(split_boxes.box_area.mean()),
                "p90_box_area_px2": float(split_boxes.box_area.quantile(0.90)),
                "pct_camera_sequence_views": float(
                    100
                    * (group.view_role == "camera_sequence").sum()
                    / len(group)
                ),
                "pct_canonical_tooth_views": float(
                    100
                    * (group.view_role == "canonical_tooth").sum()
                    / len(group)
                ),
            }
        )
    split_summary = pd.DataFrame(split_summary_rows).sort_values(
        "split", key=lambda s: s.map({"train": 0, "validation": 1, "test": 2})
    )
    split_summary.to_csv(OUT_DIR / "split_summary.csv", index=False)

    # --- 3. box-size distribution by split, for the figure + the report ---
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for split, color in zip(["train", "validation", "test"], ["#4C72B0", "#DD8452", "#55A868"]):
        split_ids = images[images.split == split].sample_id
        areas = boxes[boxes.sample_id.isin(split_ids)].box_area
        axes[0].hist(
            np.log10(areas.clip(lower=1)),
            bins=40,
            alpha=0.55,
            label=f"{split} (n={len(areas)})",
            color=color,
            density=True,
        )
    axes[0].set_xlabel("log10(pseudo-box area, px^2)")
    axes[0].set_ylabel("density")
    axes[0].set_title("Pseudo-box area distribution by split")
    axes[0].legend(fontsize=8)

    for split, color in zip(["train", "validation", "test"], ["#4C72B0", "#DD8452", "#55A868"]):
        split_ids = images[images.split == split].sample_id
        counts = images_with_counts.loc[
            images_with_counts.index.isin(split_ids), "box_count"
        ]
        axes[1].hist(
            counts, bins=30, alpha=0.55, label=f"{split} (n={len(counts)})", color=color, density=True
        )
    axes[1].set_xlabel("pseudo-boxes per image")
    axes[1].set_ylabel("density")
    axes[1].set_title("Boxes-per-image distribution by split")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "box_size_and_count_by_split.png", dpi=150)
    plt.close(fig)

    print("Wrote:")
    for path in sorted(OUT_DIR.iterdir()):
        print(" ", path)
    print("\n=== split_summary ===")
    print(split_summary.to_string(index=False))
    print("\n=== view_role_share_pct_by_split (%) ===")
    print(view_role_share_pct.to_string())


if __name__ == "__main__":
    main()
