"""Traceable pseudo-boxes replayed from the provisional v2 damage masks.

These annotations measure agreement with a deterministic image-processing rule.
They are not organizer ground truth and are not validated physical spall boxes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import Any

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import yaml

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
)
from ..utils.artifacts import sha256_file
from ..utils.provenance import ArtifactRecord, RunContext
from .image_damage import ImageDamageOptions, _robust_z, measure_damage_candidate

PSEUDO_BOX_SCHEMA_VERSION = "1.0.0"
PSEUDO_BOX_ALGORITHM_VERSION = "phm2026_pseudo_boxes_v1_from_image_damage_v2"
PSEUDO_BOX_STATUS = "PROVISIONAL_PSEUDO_BOXES_FOR_ENGINEERING_BASELINE"
PSEUDO_BOX_CLASS = "damage_candidate"
ROI_VERSION = "phm2026_visible_flank_roi_v2"


@dataclass(frozen=True, slots=True)
class ComponentDecision:
    component_label: int
    area_pixels: int
    left: int
    top: int
    width: int
    height: int
    retained: bool
    reason: str


@dataclass(frozen=True, slots=True)
class PseudoBoxResult:
    image_rows: list[dict[str, Any]]
    annotation_rows: list[dict[str, Any]]
    component_rows: list[dict[str, Any]]
    review_rows: list[dict[str, Any]]
    coco: Mapping[str, Any]
    mask_replay_mismatches: int


def replay_mask_with_components(rgb: np.ndarray, options: ImageDamageOptions) -> tuple[
    dict[str, Any],
    np.ndarray,
    tuple[int, int, int, int],
    list[ComponentDecision],
]:
    """Replay v2 exactly and expose every pre-filter connected component."""

    expected_metrics, expected_mask, roi_xyxy = measure_damage_candidate(rgb, options)
    x0, y0, x1, y1 = roi_xyxy
    roi = rgb[y0:y1, x0:x1]
    luminance = cv2.cvtColor(roi, cv2.COLOR_RGB2LAB)[..., 0]
    clahe = cv2.createCLAHE(
        clipLimit=options.clahe_clip_limit, tileGridSize=(8, 8)
    ).apply(luminance)
    background = cv2.GaussianBlur(
        clahe,
        (0, 0),
        sigmaX=options.background_sigma_pixels,
        sigmaY=options.background_sigma_pixels,
    )
    dark_residual = background.astype(np.float32) - clahe.astype(np.float32)
    gx = cv2.Sobel(clahe, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(clahe, cv2.CV_32F, 0, 1, ksize=3)
    gradient = cv2.magnitude(gx, gy)
    # Compute both evidenced fields even though v2 selection uses residual only.
    _ = _robust_z(gradient)
    candidate = (_robust_z(dark_residual) >= options.residual_z_threshold).astype(
        np.uint8
    ) * 255
    candidate = cv2.morphologyEx(
        candidate,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
    )
    candidate = cv2.morphologyEx(
        candidate,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (21, 5)),
    )
    minimum_pixels = max(
        24, int(round(candidate.size * options.minimum_component_fraction))
    )
    count, labels, stats, _ = cv2.connectedComponentsWithStats(candidate, 8)
    replayed_roi_mask = np.zeros_like(candidate)
    decisions: list[ComponentDecision] = []
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        left = int(stats[label, cv2.CC_STAT_LEFT])
        top = int(stats[label, cv2.CC_STAT_TOP])
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = int(stats[label, cv2.CC_STAT_HEIGHT])
        reasons: list[str] = []
        if area < minimum_pixels:
            reasons.append("below_v2_minimum_component_area")
        if width < 2 * height:
            reasons.append("fails_v2_horizontal_aspect_rule")
        retained = not reasons
        if retained:
            replayed_roi_mask[labels == label] = 255
        decisions.append(
            ComponentDecision(
                label,
                area,
                left,
                top,
                width,
                height,
                retained,
                "retained_by_v2" if retained else ";".join(reasons),
            )
        )
    replayed = np.zeros(rgb.shape[:2], dtype=np.uint8)
    replayed[y0:y1, x0:x1] = replayed_roi_mask
    if not np.array_equal(expected_mask, replayed):
        raise RuntimeError("pseudo-box replay differs from image_damage_v2 mask")
    return expected_metrics, replayed, roi_xyxy, decisions


def component_to_box(
    decision: ComponentDecision,
    *,
    roi_xyxy: tuple[int, int, int, int],
    image_width: int,
    image_height: int,
) -> tuple[int, int, int, int] | None:
    """Convert a retained ROI-local component to a clipped absolute xyxy box."""

    if not decision.retained:
        return None
    roi_x0, roi_y0, roi_x1, roi_y1 = roi_xyxy
    x0 = max(roi_x0, roi_x0 + decision.left)
    y0 = max(roi_y0, roi_y0 + decision.top)
    x1 = min(roi_x1, image_width, x0 + decision.width)
    y1 = min(roi_y1, image_height, y0 + decision.height)
    if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def validate_xyxy(
    box: Sequence[float],
    *,
    image_width: int,
    image_height: int,
    roi_xyxy: Sequence[int],
) -> None:
    if len(box) != 4 or not all(np.isfinite(float(value)) for value in box):
        raise ValueError("box must contain four finite values")
    x0, y0, x1, y1 = map(float, box)
    rx0, ry0, rx1, ry1 = map(float, roi_xyxy)
    if not (0 <= x0 < x1 <= image_width and 0 <= y0 < y1 <= image_height):
        raise ValueError("box is invalid or outside the image")
    if not (rx0 <= x0 < x1 <= rx1 and ry0 <= y0 < y1 <= ry1):
        raise ValueError("box lies outside the configured ROI")


def _quality_label(confidence: float) -> str:
    if confidence >= 0.8:
        return "high_structural_quality"
    if confidence >= 0.5:
        return "medium_structural_quality"
    return "low_structural_quality"


def build_pseudo_box_dataset(
    image_manifest: pd.DataFrame,
    model_samples: pd.DataFrame,
    sources: Mapping[str, ImageSource],
    *,
    options: ImageDamageOptions,
    source_mask_run_id: str,
    source_mask_artifact_sha256: str,
    cache_root: Path,
) -> PseudoBoxResult:
    """Materialize the pinned samples once and derive traceable pseudo-boxes."""

    if cache_root.exists():
        raise FileExistsError(f"cache already exists: {cache_root}")
    for relative in (
        "images/train",
        "images/validation",
        "images/test",
        "labels/train",
        "labels/validation",
        "labels/test",
    ):
        (cache_root / relative).mkdir(parents=True, exist_ok=False)
    image_index = image_manifest.set_index("image_id", verify_integrity=True)
    if (
        model_samples.sample_id.duplicated().any()
        or model_samples.image_id.duplicated().any()
    ):
        raise ValueError("model sample/image IDs must be unique")
    materialization_options = ImageProfileOptions(
        mode="full", max_member_bytes=options.max_member_bytes, max_pixels=20_000_000
    )
    algorithm_path = Path(__file__).with_name("image_damage.py")
    mask_algorithm_sha256 = sha256_file(algorithm_path)
    image_rows: list[dict[str, Any]] = []
    annotation_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    coco_images: list[dict[str, Any]] = []
    coco_annotations: list[dict[str, Any]] = []
    annotation_id = 1
    replay_mismatches = 0
    for coco_image_id, sample in enumerate(
        model_samples.sort_values("sample_id", kind="stable").itertuples(index=False),
        start=1,
    ):
        source_row = image_index.loc[str(sample.image_id)]
        source = sources.get(str(sample.source_member_id))
        if source is None:
            raise KeyError(f"missing source for {sample.source_member_id}")
        split = str(sample.split)
        cache_image = cache_root / "images" / split / f"{sample.sample_id}.jpg"
        label_path = cache_root / "labels" / split / f"{sample.sample_id}.txt"
        with materialize_image_source(source, options=materialization_options) as path:
            source_digest = sha256_file(path)
            if source_digest != str(source_row.source_sha256):
                raise RuntimeError(f"source hash mismatch for {sample.image_id}")
            shutil.copyfile(path, cache_image)
            with Image.open(path) as opened:
                rgb = np.asarray(opened.convert("RGB"), dtype=np.uint8)
        metrics, mask, roi, decisions = replay_mask_with_components(rgb, options)
        replay_matches = (
            int(metrics["damage_candidate_pixels"])
            == int(source_row.damage_candidate_pixels)
            and int(metrics["visible_flank_roi_pixels"])
            == int(source_row.visible_flank_roi_pixels)
            and abs(
                float(metrics["damage_candidate_area_pct"])
                - float(source_row.damage_candidate_area_pct)
            )
            <= 1e-12
        )
        if not replay_matches:
            replay_mismatches += 1
            raise RuntimeError(f"mask replay metric mismatch for {sample.image_id}")
        height, width = rgb.shape[:2]
        roi_area = (roi[2] - roi[0]) * (roi[3] - roi[1])
        mask_digest = sha256(mask.tobytes()).hexdigest()
        component_provenance = {
            "schema_version": PSEUDO_BOX_SCHEMA_VERSION,
            "pseudo_box_algorithm_version": PSEUDO_BOX_ALGORITHM_VERSION,
            "class_name": PSEUDO_BOX_CLASS,
            "sample_id": sample.sample_id,
            "image_id": sample.image_id,
            "source_member_id": sample.source_member_id,
            "source_archive": source_row.archive_path,
            "source_member": source_row.archive_member,
            "experiment": sample.experiment,
            "run": int(sample.run),
            "tooth_id": int(sample.tooth_id),
            "view_identifier": sample.image_id,
            "view_role": sample.image_type,
            "split": split,
            "source_sha256": source_digest,
            "source_mask_run_id": source_mask_run_id,
            "source_mask_artifact_sha256": source_mask_artifact_sha256,
            "source_mask_algorithm_sha256": mask_algorithm_sha256,
            "source_mask_sha256": mask_digest,
            "roi_version": ROI_VERSION,
            "roi_x_min": roi[0],
            "roi_y_min": roi[1],
            "roi_x_max": roi[2],
            "roi_y_max": roi[3],
            "target_definition_version": sample.target_definition_version,
            "box_confidence": float(metrics["segmentation_confidence"]),
            "box_quality_status": _quality_label(
                float(metrics["segmentation_confidence"])
            ),
            "human_review_status": "pending",
        }
        yolo_lines: list[str] = []
        image_annotation_count = 0
        for decision in decisions:
            box = component_to_box(
                decision,
                roi_xyxy=roi,
                image_width=width,
                image_height=height,
            )
            component_reason = decision.reason
            if decision.retained and box is None:
                component_reason = "rejected_invalid_or_zero_area_box"
            component_row = {
                **component_provenance,
                "component_label": decision.component_label,
                "component_area_pixels": decision.area_pixels,
                "component_left_roi": decision.left,
                "component_top_roi": decision.top,
                "component_width": decision.width,
                "component_height": decision.height,
                "retained": bool(decision.retained and box is not None),
                "decision_reason": component_reason,
            }
            component_rows.append(component_row)
            if box is None:
                continue
            validate_xyxy(box, image_width=width, image_height=height, roi_xyxy=roi)
            x0, y0, x1, y1 = box
            box_width, box_height = x1 - x0, y1 - y0
            center_x = (x0 + x1) / 2 / width
            center_y = (y0 + y1) / 2 / height
            normalized_width = box_width / width
            normalized_height = box_height / height
            yolo_lines.append(
                f"0 {center_x:.10f} {center_y:.10f} {normalized_width:.10f} {normalized_height:.10f}"
            )
            row = {
                **component_row,
                "annotation_id": f"pseudo_box_{annotation_id:08d}",
                "class_id": 0,
                "class_name": PSEUDO_BOX_CLASS,
                "x_min": x0,
                "y_min": y0,
                "x_max": x1,
                "y_max": y1,
                "box_width": box_width,
                "box_height": box_height,
                "box_area_pixels": box_width * box_height,
                "box_area_fraction_roi": (box_width * box_height) / roi_area,
                "component_fill_fraction": decision.area_pixels
                / (box_width * box_height),
                "box_confidence": float(metrics["segmentation_confidence"]),
                "box_quality_status": _quality_label(
                    float(metrics["segmentation_confidence"])
                ),
                "human_review_status": "pending",
            }
            annotation_rows.append(row)
            coco_annotations.append(
                {
                    "id": annotation_id,
                    "image_id": coco_image_id,
                    "category_id": 1,
                    "bbox": [x0, y0, box_width, box_height],
                    "area": box_width * box_height,
                    "iscrowd": 0,
                    "candidate_pixel_area": decision.area_pixels,
                    "provisional": True,
                }
            )
            annotation_id += 1
            image_annotation_count += 1
        label_path.write_text(
            "\n".join(yolo_lines) + ("\n" if yolo_lines else ""), encoding="utf-8"
        )
        base = {
            "schema_version": PSEUDO_BOX_SCHEMA_VERSION,
            "pseudo_box_algorithm_version": PSEUDO_BOX_ALGORITHM_VERSION,
            "class_name": PSEUDO_BOX_CLASS,
            "sample_id": sample.sample_id,
            "image_id": sample.image_id,
            "source_member_id": sample.source_member_id,
            "source_archive": source_row.archive_path,
            "source_member": source_row.archive_member,
            "experiment": sample.experiment,
            "run": int(sample.run),
            "tooth_id": int(sample.tooth_id),
            "view_identifier": sample.image_id,
            "view_role": sample.image_type,
            "split": split,
            "source_sha256": source_digest,
            "source_mask_run_id": source_mask_run_id,
            "source_mask_artifact_sha256": source_mask_artifact_sha256,
            "source_mask_algorithm_sha256": mask_algorithm_sha256,
            "source_mask_sha256": mask_digest,
            "roi_version": ROI_VERSION,
            "roi_x_min": roi[0],
            "roi_y_min": roi[1],
            "roi_x_max": roi[2],
            "roi_y_max": roi[3],
            "target_definition_version": sample.target_definition_version,
            "target_value_pct": float(sample.per_image_damage_candidate_pct),
            "replayed_target_value_pct": float(metrics["damage_candidate_area_pct"]),
            "mask_replay_match": replay_matches,
            "box_count": image_annotation_count,
            "annotation_status": (
                "positive_pseudo_boxes"
                if image_annotation_count
                else "valid_negative_zero_boxes"
            ),
            "box_quality_status": _quality_label(
                float(metrics["segmentation_confidence"])
            ),
            "human_review_status": "pending",
            "width": width,
            "height": height,
            "cache_image_path": cache_image.relative_to(cache_root.parent).as_posix(),
            "yolo_label_path": label_path.relative_to(cache_root.parent).as_posix(),
            "pairing_evidence": sample.pairing_evidence,
            "near_duplicate_group": sample.near_duplicate_group,
        }
        image_rows.append(base)
        review_rows.append(
            {
                **base,
                "review_status": "pending",
                "reviewer_name": "",
                "reviewer_decision": "",
                "corrected_boxes_xyxy_json": "",
                "reviewer_notes": "",
                "review_timestamp": "",
            }
        )
        coco_images.append(
            {
                "id": coco_image_id,
                "file_name": cache_image.relative_to(cache_root).as_posix(),
                "width": width,
                "height": height,
                "sample_id": sample.sample_id,
                "image_id": sample.image_id,
                "experiment": sample.experiment,
                "run": int(sample.run),
                "tooth_id": int(sample.tooth_id),
                "view_role": sample.image_type,
                "split": split,
            }
        )
    coco = {
        "info": {
            "description": "PHM provisional v2 damage-candidate pseudo-boxes",
            "version": PSEUDO_BOX_ALGORITHM_VERSION,
            "status": PSEUDO_BOX_STATUS,
            "source_mask_run_id": source_mask_run_id,
        },
        "licenses": [],
        "categories": [
            {"id": 1, "name": PSEUDO_BOX_CLASS, "supercategory": "provisional"}
        ],
        "images": coco_images,
        "annotations": coco_annotations,
    }
    return PseudoBoxResult(
        image_rows,
        annotation_rows,
        component_rows,
        review_rows,
        coco,
        replay_mismatches,
    )


def validate_pseudo_box_result(
    result: PseudoBoxResult,
    *,
    expected_split_counts: Mapping[str, int],
    split_validation: Mapping[str, Any],
) -> dict[str, Any]:
    images = pd.DataFrame(result.image_rows)
    boxes = pd.DataFrame(result.annotation_rows)
    actual_splits = images.groupby("split").size().astype(int).to_dict()
    errors: list[str] = []
    if actual_splits != dict(expected_split_counts):
        errors.append(f"split count mismatch: {actual_splits}")
    if len(images) != sum(expected_split_counts.values()):
        errors.append("model sample count mismatch")
    if result.mask_replay_mismatches:
        errors.append("mask replay mismatches")
    if not images.mask_replay_match.all():
        errors.append("not every image passed mask replay")
    if boxes.empty:
        errors.append("all images are empty pseudo-box negatives")
    elif (
        boxes[["x_min", "y_min", "x_max", "y_max"]]
        .apply(pd.to_numeric, errors="coerce")
        .isna()
        .any()
        .any()
    ):
        errors.append("non-finite box coordinate")
    whole_roi_fraction = (
        float((boxes.box_area_fraction_roi >= 0.8).mean()) if not boxes.empty else 0.0
    )
    positive_fraction = float(images.box_count.gt(0).mean())
    if whole_roi_fraction > 0.5:
        errors.append("predominantly whole-ROI boxes")
    if positive_fraction < 0.05:
        errors.append("predominantly empty boxes")
    if int(split_validation.get("experiment_run_cross_split_violations", -1)) != 0:
        errors.append("upstream experiment split leakage")
    if int(split_validation.get("near_duplicate_cross_split_violations", -1)) != 0:
        errors.append("upstream near-duplicate split leakage")
    return {
        "status": (
            PSEUDO_BOX_STATUS if not errors else "BLOCKED_PSEUDO_BOX_QUALITY_GATE"
        ),
        "errors": errors,
        "image_count": len(images),
        "box_count": len(boxes),
        "positive_image_count": int(images.box_count.gt(0).sum()),
        "negative_image_count": int(images.box_count.eq(0).sum()),
        "positive_image_fraction": positive_fraction,
        "whole_roi_box_fraction": whole_roi_fraction,
        "mask_replay_mismatch_count": result.mask_replay_mismatches,
        "split_counts": actual_splits,
        "test_used_for_parameter_selection": False,
        "human_review_status": "pending",
    }


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv_path = stem.with_suffix(".csv")
    parquet_path = stem.with_suffix(".parquet")
    frame.to_csv(csv_path, index=False)
    frame.to_parquet(parquet_path, index=False)
    return [csv_path, parquet_path]


def _contact_sheet(
    images: pd.DataFrame,
    boxes: pd.DataFrame,
    *,
    cache_root: Path,
    destination: Path,
) -> tuple[Path, Path, pd.DataFrame]:
    candidates: list[pd.Series] = []
    for _, group in images.groupby(
        ["experiment", "view_role", images.box_count.gt(0)], dropna=False
    ):
        candidates.append(group.sort_values("sample_id", kind="stable").iloc[0])
    selected = pd.DataFrame(candidates).sort_values("sample_id").head(24)
    tile_w, tile_h = 480, 300
    sheet = Image.new("RGB", (tile_w * 4, tile_h * 6), "white")
    index_rows: list[dict[str, Any]] = []
    for position, row in enumerate(selected.itertuples(index=False)):
        with Image.open(cache_root.parent / row.cache_image_path) as source:
            image = source.convert("RGB")
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            (row.roi_x_min, row.roi_y_min, row.roi_x_max, row.roi_y_max),
            outline=(0, 220, 100),
            width=8,
        )
        scoped = boxes[boxes.sample_id.eq(row.sample_id)]
        for box in scoped.itertuples(index=False):
            draw.rectangle(
                (box.x_min, box.y_min, box.x_max, box.y_max),
                outline=(255, 40, 40),
                width=8,
            )
        image.thumbnail((tile_w, tile_h - 34), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (tile_w, tile_h), "white")
        canvas.paste(image, ((tile_w - image.width) // 2, 28))
        ImageDraw.Draw(canvas).text(
            (6, 6),
            f"{row.experiment} R{row.run} T{row.tooth_id} {row.view_role} boxes={row.box_count}",
            fill=(0, 0, 0),
            font=ImageFont.load_default(),
        )
        sheet.paste(canvas, ((position % 4) * tile_w, (position // 4) * tile_h))
        index_rows.append(
            {
                "position": position,
                "sample_id": row.sample_id,
                "experiment": row.experiment,
                "run": row.run,
                "tooth_id": row.tooth_id,
                "view_role": row.view_role,
                "box_count": row.box_count,
                "selection_rule": "first stable sample per experiment/view_role/positive_status",
            }
        )
    sheet.save(destination.with_suffix(".png"), dpi=(300, 300))
    sheet.save(destination.with_suffix(".jpg"), quality=92)
    return (
        destination.with_suffix(".png"),
        destination.with_suffix(".jpg"),
        pd.DataFrame(index_rows),
    )


def write_pseudo_box_run(
    result: PseudoBoxResult,
    quality: Mapping[str, Any],
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
    artifacts: list[ArtifactRecord] = []
    images = pd.DataFrame(result.image_rows)
    boxes = pd.DataFrame(result.annotation_rows)
    components = pd.DataFrame(result.component_rows)
    reviews = pd.DataFrame(result.review_rows)
    for name, frame in (
        ("annotation_image_manifest", images),
        ("annotation_manifest", boxes),
        ("component_decisions", components),
        ("human_review_queue", reviews),
    ):
        for path in _write_frame(frame, run.run_directory / "tables" / name):
            artifacts.append(run.artifact(path, role=name))
    summary = images.groupby(
        ["split", "experiment", "run", "view_role"], as_index=False
    ).agg(
        images=("sample_id", "size"),
        positives=("box_count", lambda x: int((x > 0).sum())),
        boxes=("box_count", "sum"),
    )
    for path in _write_frame(summary, run.run_directory / "tables/annotation_summary"):
        artifacts.append(run.artifact(path, role="annotation_summary"))
    coco_path = run.run_directory / "tables/coco_annotations.json"
    coco_path.write_text(json_text(result.coco), encoding="utf-8")
    artifacts.append(run.artifact(coco_path, role="coco_annotations"))
    dataset_yaml = {
        "path": "cache",
        "train": "images/train",
        "val": "images/validation",
        "test": "images/test",
        "names": {0: PSEUDO_BOX_CLASS},
        "provisional_status": PSEUDO_BOX_STATUS,
    }
    dataset_path = run.run_directory / "config/ultralytics_dataset.yaml"
    dataset_path.write_text(
        yaml.safe_dump(dataset_yaml, sort_keys=False), encoding="utf-8"
    )
    artifacts.append(run.artifact(dataset_path, role="ultralytics_dataset_config"))
    config_path = run.write_resolved_config(resolved_config)
    inputs_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        (
            run.artifact(config_path, role="resolved_config"),
            run.artifact(inputs_path, role="input_manifest"),
        )
    )
    quality_path = run.run_directory / "reports/annotation_quality.json"
    quality_path.write_text(json_text(dict(quality)), encoding="utf-8")
    artifacts.append(run.artifact(quality_path, role="annotation_quality"))
    guide_path = run.run_directory / "reports/HUMAN_PSEUDO_BOX_REVIEW_GUIDE.md"
    guide_path.write_text(
        "# Human pseudo-box review guide\n\n"
        "> These are provisional boxes derived from the v2 damage-candidate mask, not physical-spall ground truth.\n\n"
        "Review deterministic contact-sheet examples and rows in `tables/human_review_queue.csv`. Confirm the green ROI, every red candidate box, zero-box negatives, and whether the region is tooth-flank damage rather than texture/background. Record `accept`, `correct`, or `reject`, corrected xyxy boxes when needed, notes, reviewer, and timestamp. Do not promote detection metrics to physical validity until representative canonical and close-up views from every experiment are reviewed.\n",
        encoding="utf-8",
    )
    artifacts.append(run.artifact(guide_path, role="human_review_guide"))
    apply_academic_style()
    funnel = pd.DataFrame(
        {
            "stage": ["source images", "model views", "tooth/run", "run targets"],
            "count": [1311, len(images), 560, 20],
        }
    )
    for path in _write_frame(
        funnel, run.run_directory / "tables/plot_source_dataset_annotation_funnel"
    ):
        artifacts.append(run.artifact(path, role="plot_source"))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(funnel.stage, funnel["count"], color=ACADEMIC_COLORS[:4])
    for i, value in enumerate(funnel["count"]):
        ax.text(i, value, f"{value:,}", ha="center", va="bottom")
    ax.set_ylabel("Records (archive members are not model samples)")
    ax.set_title("PHM image-to-target evidence funnel")
    for path in save_figure_pair(
        fig, run.run_directory / "figures/dataset_annotation_funnel"
    ):
        artifacts.append(run.artifact(path, role="figure"))
    count_source = images.groupby(
        ["split", "view_role"], as_index=False
    ).box_count.sum()
    for path in _write_frame(
        count_source,
        run.run_directory / "tables/plot_source_box_count_by_split_view_role",
    ):
        artifacts.append(run.artifact(path, role="plot_source"))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for index, (role, group) in enumerate(count_source.groupby("view_role")):
        ax.bar(
            np.arange(len(group)) + index * 0.32,
            group.box_count,
            width=0.32,
            label=role,
        )
    ax.set_xticks(
        np.arange(count_source.split.nunique()) + 0.16,
        sorted(count_source.split.unique()),
    )
    ax.set_ylabel("Pseudo-box count")
    ax.set_title("Pseudo-box count by frozen split and acquisition view")
    ax.legend()
    for path in save_figure_pair(
        fig, run.run_directory / "figures/box_count_by_split_view_role"
    ):
        artifacts.append(run.artifact(path, role="figure"))
    area_source = boxes[
        ["annotation_id", "split", "experiment", "view_role", "box_area_fraction_roi"]
    ].copy()
    for path in _write_frame(
        area_source, run.run_directory / "tables/plot_source_box_area_distribution"
    ):
        artifacts.append(run.artifact(path, role="plot_source"))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for split, group in area_source.groupby("split"):
        ax.hist(
            group.box_area_fraction_roi,
            bins=30,
            alpha=0.45,
            label=f"{split} N={len(group)}",
        )
    ax.set_xlabel("Bounding-box area / fixed ROI area")
    ax.set_ylabel("Pseudo-boxes")
    ax.set_title("Provisional pseudo-box area distribution")
    ax.legend()
    for path in save_figure_pair(
        fig, run.run_directory / "figures/box_area_distribution"
    ):
        artifacts.append(run.artifact(path, role="figure"))
    cache_root = run.run_directory / "cache"
    contact_png, contact_jpg, contact_index = _contact_sheet(
        images,
        boxes,
        cache_root=cache_root,
        destination=run.run_directory / "figures/annotation_contact_sheet",
    )
    for path in (contact_png, contact_jpg):
        artifacts.append(run.artifact(path, role="annotation_contact_sheet"))
    for path in _write_frame(
        contact_index, run.run_directory / "tables/plot_source_annotation_contact_sheet"
    ):
        artifacts.append(run.artifact(path, role="plot_source"))
    cache_manifest = images[
        ["sample_id", "cache_image_path", "source_sha256", "yolo_label_path", "split"]
    ]
    for path in _write_frame(
        cache_manifest, run.run_directory / "manifests/materialized_cache"
    ):
        artifacts.append(run.artifact(path, role="materialized_cache_manifest"))
    report_path = run.run_directory / "reports/pseudo_box_report.md"
    report_path.write_text(
        "# Provisional PHM damage-candidate pseudo-boxes\n\n"
        f"> Status: **{quality['status']}**. Boxes are algorithmic pseudo-labels, not organizer or physical-spall ground truth.\n\n"
        f"The exact v2 mask was replayed for {len(images):,} pinned model views with {quality['mask_replay_mismatch_count']} mismatch(es). The dataset contains {quality['positive_image_count']:,} positive and {quality['negative_image_count']:,} valid zero-box images, and {quality['box_count']:,} retained component boxes. EXP-F was not used to choose any mask or box parameter. Canonical and camera-sequence protocols remain separate in all summaries. Detection evaluation can measure only agreement with these pseudo-boxes until expert review.\n",
        encoding="utf-8",
    )
    artifacts.append(run.artifact(report_path, role="pseudo_box_report"))
    return finalize_run(run, artifacts)
