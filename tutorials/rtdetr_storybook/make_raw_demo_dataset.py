#!/usr/bin/env python3
"""Build a demo set straight from RAW PHM archives — no cache involved.

============================================================================
 WHAT THIS SCRIPT IS
============================================================================
This is the "real" data-loading path for the storybook tutorial. Unlike
make_demo_dataset.py (which copies already-cached images from a previous
run under runs/phm2026_rtdetr_pseudo_boxes/), this script opens the raw,
immutable challenge archives directly:

    gtc-data-experiment/photos/EXP-A/Exp-A_Photos_Run-<n>.zip
    gtc-data-experiment/photos/EXP-B/Exp-B_Photos_Run-<n>.zip
    gtc-data-experiment/photos/EXP-F/Exp-F_Photos_Run-<n>.zip

(exact filenames vary; this script discovers them with a glob rather than
assuming one, see discover_run_archive() below).

It reads read-only, one image member at a time, via this repo's own
archive_io.materialize_archive_member() — the same bounded, non-extracting
helper the governed profiling pipeline uses. It NEVER calls
zipfile.ZipFile.extract(), never writes into gtc-data-experiment/, and
never uses any cached run under runs/. Per AGENTS.md, gtc-data-experiment/
is immutable; this script only ever opens it for reading.

============================================================================
 PREPROCESSING AND TARGET DEFINITION — reusing the real thesis pipeline
============================================================================
A raw PHM gear-tooth photo cannot be handed to a detector as-is and it has
no organizer-provided label at all (see docs/planning/
T2_TARGET_FORMULATION_DECISION.md: "The challenge archives provide no
organizer damage boxes"). Two things have to happen first, and this script
does them by calling the SAME functions the governed pipeline uses —
it does not reimplement or invent new image-processing rules:

  1. Preprocessing (pi_multimodal_ad.targets.image_damage.measure_damage_
     candidate): crop to a fixed "visible flank" region of interest (ROI),
     contrast-normalize it (CLAHE), estimate a smooth local background
     (Gaussian blur) and subtract it to find a "dark residual", threshold
     that residual with a robust (median/MAD-based) z-score, clean up the
     result with morphological open/close, then keep only the resulting
     blobs that are wide-and-flat ("horizontal") — spall/pitting damage on
     a gear tooth tends to look like a horizontal streak, not a dot.

  2. Target definition (`phm2026_image_damage_v2`, decision-dated
     2026-08-14): the surviving pixels define a "damage_candidate"
     percentage of the ROI. That percentage — and the boxes drawn around
     each surviving blob — is a PROVISIONAL PSEUDO-LABEL, not organizer
     ground truth, not expert-reviewed. See docs/planning/
     T2_TARGET_FORMULATION_DECISION.md and R4_PSEUDO_BOX_CHECKPOINT.md for
     the full, honest accounting of what this standard can and cannot
     support today.

All numeric parameters below (ROI box, CLAHE clip limit, blur sigma,
z-score threshold, ...) are read from the same pinned configuration file
the real pipeline uses: configs/experiments/phm2026_image_target.yaml.
This script does not invent its own numbers.

============================================================================
 WHY THIS MATTERS FOR "GETTING SOMETHING VALUABLE OUT OF RT-DETR"
============================================================================
Training or evaluating RT-DETR against an arbitrary box format teaches you
the *mechanics* of object detection, but the boxes only become scientifically
useful once you can say precisely: where did they come from, what do they
measure, and what is still missing before they mean "real damage"? That's
exactly what T2_TARGET_FORMULATION_DECISION.md's "Human validation" section
spells out: mask/ROI review, per-tooth correction, reviewer identity and
timestamp, before anything here may be called validated. This script's .md
files carry that status forward explicitly so nobody downstream forgets it.

============================================================================
 THIS SCRIPT WAS NOT EXECUTED AGAINST REAL DATA
============================================================================
It was written and syntax-checked in a sandbox that has neither
gtc-data-experiment/ nor opencv/numpy/PIL/pandas installed. Run it in your
real thesis environment (where the raw archives are mounted) and read the
console output carefully the first time — see this folder's README.md.

============================================================================
 SETUP
============================================================================
    pip install -r ../../requirements.txt   # opencv-python, numpy, pillow,
                                              # pandas, matplotlib, pyyaml
    python make_raw_demo_dataset.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

_MISSING_DEPENDENCIES: list[str] = []
try:
    import numpy as np
except ImportError:
    _MISSING_DEPENDENCIES.append("numpy")
try:
    from PIL import Image
except ImportError:
    _MISSING_DEPENDENCIES.append("pillow")
try:
    import yaml
except ImportError:
    _MISSING_DEPENDENCIES.append("pyyaml")

try:
    from pi_multimodal_ad.datasets.phm2026 import PHM2026Adapter
    from pi_multimodal_ad.profiling.archive_io import (
        ArchiveMaterializationError,
        ArchiveMemberRef,
        materialize_archive_member,
    )
    # image_damage.py itself imports cv2/matplotlib/pandas at module scope,
    # so importing it also exercises those dependencies.
    from pi_multimodal_ad.targets.image_damage import (
        ImageDamageOptions,
        measure_damage_candidate,
    )
except ImportError as exc:
    _MISSING_DEPENDENCIES.append(f"pi_multimodal_ad import failed ({exc})")

RAW_ROOT_DEFAULT = REPO_ROOT / "gtc-data-experiment"
TARGET_CONFIG_DEFAULT = REPO_ROOT / "configs" / "experiments" / "phm2026_image_target.yaml"
OUTPUT_DIR_DEFAULT = Path(__file__).resolve().parent / "raw_demo_data"

# Mirrors the real thesis train/validation/test split convention (see
# docs/planning/T2_2_CHECKPOINT.md): EXP-B trains, EXP-A validates, EXP-F
# tests. Using the same split here — even for a 6-image demo — means the
# "why we care about EXP-F acting differently" lesson stays real, not a toy.
DEFAULT_SPLITS = (("EXP-B", "train"), ("EXP-A", "validation"), ("EXP-F", "test"))
IMAGES_PER_EXPERIMENT = 2
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def _require_dependencies() -> None:
    if _MISSING_DEPENDENCIES:
        print(
            "This script needs a few extra libraries that aren't installed "
            f"yet: {', '.join(_MISSING_DEPENDENCIES)}.\n\n"
            "From the repo root, install them with:\n\n"
            "    pip install -r requirements.txt\n\n"
            "Then re-run this script.",
            file=sys.stderr,
        )
        raise SystemExit(1)


def load_pinned_image_measurement_options(config_path: Path) -> ImageDamageOptions:
    """Read the SAME pinned parameters the governed pipeline trains against.

    See configs/experiments/phm2026_image_target.yaml. We deliberately read
    this file instead of hard-coding numbers here, so a future change to
    the thesis's target definition automatically flows into this tutorial
    too, and so nobody mistakes this for an independently-invented rule.
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Expected the pinned target config at {config_path}. This "
            "tutorial reuses the real thesis parameters rather than "
            "inventing its own; without this file it can't proceed."
        )
    with config_path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    measurement = config["image_measurement"]
    target = config["target_definition"]
    return ImageDamageOptions(
        roi_normalized_xyxy=tuple(measurement["roi_normalized_xyxy"]),
        clahe_clip_limit=float(measurement["clahe_clip_limit"]),
        background_sigma_pixels=float(measurement["background_sigma_pixels"]),
        residual_z_threshold=float(measurement["residual_z_threshold"]),
        gradient_z_threshold=float(measurement["gradient_z_threshold"]),
        minimum_component_fraction=float(measurement["minimum_component_fraction"]),
        damaged_tooth_threshold_pct=float(target["damaged_tooth_threshold_pct"]),
        minimum_valid_teeth=int(target["minimum_valid_teeth"]),
        near_duplicate_hamming=int(measurement["near_duplicate_hamming"]),
        max_member_bytes=int(measurement["max_member_bytes"]),
        overlay_jpeg_quality=int(measurement["overlay_jpeg_quality"]),
    )


def discover_run_archive(raw_root: Path, experiment: str, run: int) -> Path | None:
    """Find the raw photo archive for one experiment/run by globbing + parsing.

    We deliberately do NOT hard-code an exact filename like
    "Exp-B_Photos_Run-1.zip": real archive naming has small, undocumented
    variations (spacing, dashes), so we glob every .zip under the
    experiment's photo folder and let PHM2026Adapter's own run-number
    parser (the same regex the governed pipeline trusts) decide which one
    matches, rather than guessing.
    """
    adapter = PHM2026Adapter()
    letter = experiment.removeprefix("EXP-")
    experiment_dir = raw_root / "photos" / f"EXP-{letter}"
    if not experiment_dir.is_dir():
        return None
    for candidate in sorted(experiment_dir.glob("*.zip")):
        try:
            parsed_run = adapter.parse_run(candidate.name)
        except Exception:  # noqa: BLE001 - a non-matching filename is expected, not an error
            continue
        if parsed_run == run:
            return candidate
    return None


def list_canonical_tooth_members(archive_path: Path, archive_relative: str) -> list[tuple[str, int]]:
    """List (member_name, tooth_id) pairs for canonical (non-close-up) tooth photos.

    We read only the ZIP's central directory here (zipfile.infolist()) —
    no payload bytes are touched yet. EXP-A/EXP-B archives mix ten
    close-up "WIN_..." images for teeth 1-4 with one canonical "TOOTH_n"
    image for teeth 5-28 (see T2_TARGET_FORMULATION_DECISION.md); EXP-F has
    one canonical image per tooth. We keep this demo to canonical images
    only, to sidestep the real pipeline's multi-view aggregation and keep
    the lesson focused on preprocessing + boxes, not view-aggregation.
    """
    adapter = PHM2026Adapter()
    results: list[tuple[str, int]] = []
    with zipfile.ZipFile(archive_path, mode="r") as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            suffix = Path(info.filename).suffix.lower()
            if suffix not in IMAGE_SUFFIXES:
                continue
            try:
                identity = adapter.parse_image_identity(
                    archive_relative, archive_member=info.filename
                )
            except Exception:  # noqa: BLE001 - skip anything the adapter can't classify
                continue
            if identity.image_role != "canonical_tooth" or identity.tooth_id is None:
                continue
            results.append((info.filename, int(identity.tooth_id)))
    results.sort(key=lambda item: item[1])
    return results


def boxes_from_mask(mask: "np.ndarray") -> list[tuple[float, float, float, float]]:
    """Extract tight pixel-space boxes from an already-filtered candidate mask.

    measure_damage_candidate() has already applied every v2 acceptance rule
    (residual z-score threshold, morphology, "horizontal" shape filter), so
    every remaining nonzero blob here IS a retained candidate — we only
    need its bounding rectangle, via the same connected-components call
    used throughout the codebase (see targets/pseudo_boxes.py).
    """
    import cv2

    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    boxes: list[tuple[float, float, float, float]] = []
    for label in range(1, count):
        left = int(stats[label, cv2.CC_STAT_LEFT])
        top = int(stats[label, cv2.CC_STAT_TOP])
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = int(stats[label, cv2.CC_STAT_HEIGHT])
        boxes.append((float(left), float(top), float(left + width), float(top + height)))
    return boxes


def write_raw_demo_entry(
    *,
    raw_jpeg_bytes: bytes,
    stem: str,
    output_dir: Path,
    experiment: str,
    run: int,
    tooth_id: int,
    archive_relative: str,
    member_name: str,
    options: ImageDamageOptions,
    metrics: dict,
    boxes: list[tuple[float, float, float, float]],
    width: int,
    height: int,
) -> None:
    # The raw bytes are written out completely untouched — this is the
    # literal payload that came out of the ZIP, proving the image really
    # is "from raw", not a re-encoded or resized copy.
    (output_dir / f"{stem}.jpg").write_bytes(raw_jpeg_bytes)

    x0, y0, x1, y1 = options.roi_normalized_xyxy
    lines = [
        f"# Target labels for {stem}.jpg (derived from RAW archive data)",
        "",
        f"- Source (raw, read-only): gtc-data-experiment/{archive_relative} ! {member_name}",
        f"- Source: PHM 2026 Data Challenge, {experiment} Run {run}, tooth {tooth_id} "
        "(canonical_tooth view)",
        "- Status: PROVISIONAL pseudo-label — derived by directly re-running the "
        "governed phm2026_image_damage_v2 preprocessing/measurement pipeline "
        "(pi_multimodal_ad.targets.image_damage.measure_damage_candidate) on "
        "this raw image. NOT organizer ground truth, NOT expert-reviewed. See "
        "docs/planning/T2_TARGET_FORMULATION_DECISION.md and "
        "docs/planning/R4_PSEUDO_BOX_CHECKPOINT.md.",
        f"- Image size: {width} x {height} pixels",
        "",
        "## Preprocessing pipeline actually applied (pinned parameters)",
        "",
        f"1. Crop to the fixed visible-flank ROI: normalized box "
        f"({x0}, {y0}, {x1}, {y1}) of the full image.",
        f"2. Contrast-normalize the ROI's LAB lightness channel with CLAHE "
        f"(clip limit {options.clahe_clip_limit}).",
        f"3. Estimate a smooth local background with a Gaussian blur "
        f"(sigma {options.background_sigma_pixels} px) and subtract it from the "
        "CLAHE image to get a 'dark residual' (dark spots look brighter here).",
        f"4. Turn the dark residual into a robust z-score (median/MAD-based, "
        "resistant to outliers) and keep pixels at or above "
        f"z={options.residual_z_threshold}.",
        "5. Clean the resulting mask with morphological opening (5x5 ellipse) "
        "then closing (21x5 rectangle) to remove speckle and bridge small gaps.",
        f"6. Drop connected components smaller than "
        f"{options.minimum_component_fraction * 100:.4f}% of the ROI, and drop "
        "any component that isn't at least twice as wide as it is tall — real "
        "spall/pitting tends to read as a horizontal streak, not a dot.",
        "",
        "## What survived (this run's provisional measurement)",
        "",
        f"- damage_candidate_area_pct: {metrics['damage_candidate_area_pct']:.4f} "
        "(percent of the ROI covered by surviving pixels)",
        f"- component_count: {metrics['component_count']}",
        f"- segmentation_confidence (heuristic, not a probability): "
        f"{metrics['segmentation_confidence']:.4f}",
        f"- measurement_status: {metrics['measurement_status']}",
        "",
        "## Boxes (pixel coordinates in the ORIGINAL, uncropped image)",
        "",
        "| class | x_min | y_min | x_max | y_max |",
        "|---|---|---|---|---|",
    ]
    for x_min, y_min, x_max, y_max in boxes:
        lines.append(f"| damage_candidate | {x_min:.1f} | {y_min:.1f} | {x_max:.1f} | {y_max:.1f} |")
    lines.append("")
    (output_dir / f"{stem}.md").write_text("\n".join(lines), encoding="utf-8")


def build_raw_demo_dataset(
    *, raw_root: Path, output_dir: Path, options: ImageDamageOptions
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for experiment, split_name in DEFAULT_SPLITS:
        run = 1
        archive_path = discover_run_archive(raw_root, experiment, run)
        if archive_path is None:
            print(
                f"  [skip] no {experiment} Run {run} photo archive found under "
                f"{raw_root / 'photos' / experiment}"
            )
            continue
        archive_relative = archive_path.relative_to(raw_root).as_posix()
        members = list_canonical_tooth_members(archive_path, archive_relative)
        if not members:
            print(f"  [skip] no canonical tooth images found in {archive_path.name}")
            continue

        for member_name, tooth_id in members[:IMAGES_PER_EXPERIMENT]:
            reference = ArchiveMemberRef(
                archive_path=archive_path,
                archive_relative_path=archive_relative,
                member_path=member_name,
            )
            try:
                with materialize_archive_member(
                    reference, max_member_bytes=options.max_member_bytes
                ) as payload_path:
                    raw_jpeg_bytes = payload_path.read_bytes()
                    with Image.open(payload_path) as image:
                        rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
            except ArchiveMaterializationError as exc:
                print(f"  [skip] could not read {member_name}: {exc}")
                continue

            metrics, mask, _roi = measure_damage_candidate(rgb, options)
            boxes = boxes_from_mask(mask)
            height, width = rgb.shape[:2]
            stem = f"raw_{experiment.lower().replace('-', '')}_run{run}_tooth{tooth_id:02d}"
            write_raw_demo_entry(
                raw_jpeg_bytes=raw_jpeg_bytes,
                stem=stem,
                output_dir=output_dir,
                experiment=experiment,
                run=run,
                tooth_id=tooth_id,
                archive_relative=archive_relative,
                member_name=member_name,
                options=options,
                metrics=metrics,
                boxes=boxes,
                width=width,
                height=height,
            )
            written += 1
            print(
                f"  [ok] {split_name:>10} | tooth {tooth_id:2d} | "
                f"{len(boxes):2d} boxes | {metrics['damage_candidate_area_pct']:.3f}% "
                f"candidate area | {stem}.jpg"
            )
    return written


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=RAW_ROOT_DEFAULT,
        help="Path to the raw gtc-data-experiment/ directory (default: "
        f"{RAW_ROOT_DEFAULT}). Read-only; never modified.",
    )
    parser.add_argument(
        "--target-config",
        type=Path,
        default=TARGET_CONFIG_DEFAULT,
        help="Pinned target/preprocessing config to reuse (default: "
        "configs/experiments/phm2026_image_target.yaml).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR_DEFAULT,
        help="Where to write raw image copies + derived .md targets "
        "(default: ./raw_demo_data).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _require_dependencies()

    if not args.raw_root.is_dir():
        print(
            f"Raw data root not found: {args.raw_root}\n\n"
            "This script needs the actual PHM 2026 raw archives "
            "(gtc-data-experiment/photos/...) mounted locally — they are "
            "never checked into git (see AGENTS.md's data boundaries). Run "
            "this on the machine/environment where the raw challenge data "
            "actually lives, or pass --raw-root to point at it.",
            file=sys.stderr,
        )
        return 1

    options = load_pinned_image_measurement_options(args.target_config)
    print(f"Reading raw archives (read-only) under: {args.raw_root}")
    print(f"Reusing pinned preprocessing/target parameters from: {args.target_config}")
    print(f"Writing demo dataset to: {args.output_dir}\n")

    written = build_raw_demo_dataset(
        raw_root=args.raw_root, output_dir=args.output_dir, options=options
    )
    if written == 0:
        print(
            "\nNo images were written. Check that gtc-data-experiment/photos/ "
            "contains the expected Exp-*_Photos_Run-*.zip archives.",
            file=sys.stderr,
        )
        return 1
    print(
        f"\nDone. Wrote {written} raw image(s) with derived, provisional .md "
        "target files. Every box was produced by re-running the real, "
        "pinned phm2026_image_damage_v2 pipeline — not invented for this demo."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
