#!/usr/bin/env python3
"""Build a tiny, real-image demo set with Markdown (.md) target files.

WHAT THIS SCRIPT IS
--------------------
This is a *tutorial* helper, not part of the governed PHM 2026 thesis
pipeline. It does exactly one thing: it copies a small, deterministic
handful of *real* PHM 2026 gear-tooth photos (and their provisional
pseudo-box targets) out of an existing, already-generated run directory,
and rewrites the targets as beginner-friendly ``.md`` sidecar files.

It never touches raw/immutable data and never modifies the source run:
everything below only *reads* from the pinned run directory and *writes*
brand-new files under ``tutorials/rtdetr_storybook/demo_data/``.

WHERE THE IMAGES AND BOXES COME FROM
-------------------------------------
Source run (read-only): ``runs/phm2026_rtdetr_pseudo_boxes/<run-id>/``
  - ``tables/coco_annotations.json`` — pixel-space bounding boxes plus
    experiment/run/tooth/split metadata for 995 cached images.
  - ``cache/images/<split>/<sample_id>.jpg`` — the matching real JPEG.

IMPORTANT — these boxes are PROVISIONAL PSEUDO-LABELS
-------------------------------------------------------
The boxes are candidate "damage" regions produced by a heuristic image
mask (see docs/planning/R4_PSEUDO_BOX_CHECKPOINT.md), not organizer
ground truth and not expert-reviewed. Every ``.md`` file this script
writes says so explicitly. Do not present them, or anything trained on
them, as validated physical damage measurements.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

# The pinned, canonical pseudo-box run referenced in PROJECT_STATE.md /
# R4_PSEUDO_BOX_CHECKPOINT.md. We read from it but never write into it.
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_RUN = (
    REPO_ROOT
    / "runs"
    / "phm2026_rtdetr_pseudo_boxes"
    / "20260814T040854991567Z-3fa0f794"
)
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "demo_data"

# Real images range from 0 to dozens of candidate boxes. We only require
# "at least a few" so there is something to look at; we do NOT cap the
# maximum here, because EXP-F (test split) images genuinely tend to carry
# many more candidate boxes than EXP-A/EXP-B (see PROJECT_STATE.md's notes
# on A/B-vs-F imaging protocol differences) — hiding that by filtering
# would misrepresent the real data. The visualization script caps how many
# boxes it *draws* for legibility and says so on-screen.
MIN_BOXES_FOR_DEMO = 3

# How many demo images to keep per dataset split. Kept small on purpose:
# this is a teaching aid, not a training set.
IMAGES_PER_SPLIT = 2


def load_coco_annotations(source_run: Path) -> dict:
    """Read the pinned run's COCO-style annotation file (read-only)."""
    annotations_path = source_run / "tables" / "coco_annotations.json"
    if not annotations_path.exists():
        raise FileNotFoundError(
            f"Expected pseudo-box annotations at {annotations_path}. "
            "Point --source-run at a valid phm2026_rtdetr_pseudo_boxes run "
            "directory (it must contain tables/coco_annotations.json)."
        )
    with annotations_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def select_demo_images(coco: dict) -> list[dict]:
    """Deterministically pick a small, readable subset of real images.

    Selection is fully deterministic (sorted by sample_id) so re-running
    this script always produces the same demo set — no randomness, no
    cherry-picking bias.
    """
    boxes_by_image_id: dict[int, list[dict]] = {}
    for annotation in coco["annotations"]:
        boxes_by_image_id.setdefault(annotation["image_id"], []).append(annotation)

    candidates = [
        image
        for image in coco["images"]
        if len(boxes_by_image_id.get(image["id"], [])) >= MIN_BOXES_FOR_DEMO
    ]
    candidates.sort(key=lambda image: image["sample_id"])

    selected: list[dict] = []
    per_split_count: dict[str, int] = {}
    for image in candidates:
        split = image["split"]
        if per_split_count.get(split, 0) >= IMAGES_PER_SPLIT:
            continue
        image = dict(image)
        image["boxes"] = boxes_by_image_id[image["id"]]
        selected.append(image)
        per_split_count[split] = per_split_count.get(split, 0) + 1

    return selected


def write_markdown_target(image: dict, md_path: Path) -> None:
    """Write one beginner-friendly, still machine-parseable, .md target file.

    Format contract (read by rtdetr_storybook.py's parse_md_targets()):
      - A line starting with "- Image size:" gives "WIDTH x HEIGHT pixels".
      - A line starting with "- Status:" gives the provenance/status text.
      - A Markdown table under "## Boxes" with columns
        | class | x_min | y_min | x_max | y_max |
        holds one bounding box per data row (pixel coordinates).
    """
    lines = [
        f"# Target labels for {image['file_name'].split('/')[-1]}",
        "",
        f"- Source: PHM 2026 Data Challenge, {image['experiment']} "
        f"Run {image['run']}, tooth {image['tooth_id']} "
        f"({image['view_role']} view, {image['split']} split)",
        "- Status: PROVISIONAL pseudo-label — heuristic mask-derived "
        "candidate region, NOT organizer ground truth, NOT expert-reviewed. "
        "See docs/planning/R4_PSEUDO_BOX_CHECKPOINT.md for how these were made.",
        f"- Image size: {image['width']} x {image['height']} pixels",
        "",
        "## Boxes",
        "",
        "| class | x_min | y_min | x_max | y_max |",
        "|---|---|---|---|---|",
    ]
    for box in sorted(image["boxes"], key=lambda item: item["id"]):
        x_min, y_min, box_width, box_height = box["bbox"]
        x_max = x_min + box_width
        y_max = y_min + box_height
        lines.append(
            f"| damage_candidate | {x_min:.1f} | {y_min:.1f} "
            f"| {x_max:.1f} | {y_max:.1f} |"
        )
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def build_demo_dataset(source_run: Path, output_dir: Path) -> list[Path]:
    coco = load_coco_annotations(source_run)
    selected_images = select_demo_images(coco)
    if not selected_images:
        raise RuntimeError(
            f"No images had at least {MIN_BOXES_FOR_DEMO} candidate boxes. "
            "Check that the source run's coco_annotations.json is populated."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for image in selected_images:
        source_image_path = source_run / "cache" / image["file_name"]
        if not source_image_path.exists():
            print(
                f"  [skip] cached image missing on disk: {source_image_path}",
                file=sys.stderr,
            )
            continue

        stem = Path(image["file_name"]).stem
        destination_image_path = output_dir / f"{stem}.jpg"
        destination_md_path = output_dir / f"{stem}.md"

        # Copy the real JPEG bytes as-is. We never re-encode or modify
        # pixel data, and we never touch the source run directory.
        shutil.copyfile(source_image_path, destination_image_path)
        write_markdown_target(image, destination_md_path)

        written.append(destination_image_path)
        print(
            f"  [ok] {image['split']:>10} | {len(image['boxes']):2d} boxes | "
            f"{destination_image_path.name}"
        )

    return written


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-run",
        type=Path,
        default=DEFAULT_SOURCE_RUN,
        help="Pinned phm2026_rtdetr_pseudo_boxes run directory to read from "
        "(read-only; default: the canonical run pinned in PROJECT_STATE.md).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Where to write the demo images + .md files (default: "
        "tutorials/rtdetr_storybook/demo_data/).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print(f"Reading pinned pseudo-box run (read-only): {args.source_run}")
    print(f"Writing demo dataset to: {args.output_dir}\n")
    written = build_demo_dataset(args.source_run, args.output_dir)
    print(
        f"\nDone. Wrote {len(written)} real image(s) with matching .md "
        "target files. These are a teaching aid only — see this folder's "
        "README.md before using them for anything else."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
