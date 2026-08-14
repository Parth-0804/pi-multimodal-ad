"""Deterministic provisional image-derived PHM damage target construction.

The masks emitted here are deliberately named damage *candidates*. They become
physical spall annotations only after human review; the challenge supplies no
participant-visible organizer ground truth.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
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

TARGET_SCHEMA_VERSION = "1.0.0"
TARGET_DEFINITION_VERSION = "phm2026_image_damage_v2"
TARGET_STATUS = "PASS_PROVISIONAL_FOR_ENGINEERING_BASELINE"


@dataclass(frozen=True, slots=True)
class ImageDamageOptions:
    roi_normalized_xyxy: tuple[float, float, float, float]
    clahe_clip_limit: float
    background_sigma_pixels: float
    residual_z_threshold: float
    gradient_z_threshold: float
    minimum_component_fraction: float
    damaged_tooth_threshold_pct: float
    minimum_valid_teeth: int
    near_duplicate_hamming: int
    max_member_bytes: int
    overlay_jpeg_quality: int

    def __post_init__(self) -> None:
        x0, y0, x1, y1 = self.roi_normalized_xyxy
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            raise ValueError("ROI coordinates must be ordered fractions in [0, 1]")
        if not 1 <= self.minimum_valid_teeth <= 28:
            raise ValueError("minimum_valid_teeth must be in [1, 28]")
        if not 0 <= self.near_duplicate_hamming <= 64:
            raise ValueError("near_duplicate_hamming must be in [0, 64]")


def _robust_z(values: np.ndarray) -> np.ndarray:
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    scale = max(1.4826 * mad, 1e-6)
    return (values - median) / scale


def _components(mask: np.ndarray, minimum_pixels: int) -> tuple[np.ndarray, int, int]:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    kept = np.zeros_like(mask)
    areas: list[int] = []
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area >= minimum_pixels:
            kept[labels == label] = 255
            areas.append(area)
    return kept, len(areas), max(areas, default=0)


def measure_damage_candidate(
    rgb: np.ndarray, options: ImageDamageOptions
) -> tuple[dict[str, Any], np.ndarray, tuple[int, int, int, int]]:
    """Measure a deterministic dark/textured candidate area in a fixed flank ROI."""

    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8:
        raise ValueError("expected an H x W x 3 uint8 RGB image")
    height, width = rgb.shape[:2]
    x0f, y0f, x1f, y1f = options.roi_normalized_xyxy
    x0, y0 = int(round(x0f * width)), int(round(y0f * height))
    x1, y1 = int(round(x1f * width)), int(round(y1f * height))
    roi = rgb[y0:y1, x0:x1]
    lab = cv2.cvtColor(roi, cv2.COLOR_RGB2LAB)
    luminance = lab[..., 0]
    clahe = cv2.createCLAHE(
        clipLimit=options.clahe_clip_limit, tileGridSize=(8, 8)
    ).apply(luminance)
    sigma = options.background_sigma_pixels
    background = cv2.GaussianBlur(clahe, (0, 0), sigmaX=sigma, sigmaY=sigma)
    dark_residual = background.astype(np.float32) - clahe.astype(np.float32)
    gx = cv2.Sobel(clahe, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(clahe, cv2.CV_32F, 0, 1, ksize=3)
    gradient = cv2.magnitude(gx, gy)
    residual_z = _robust_z(dark_residual)
    gradient_z = _robust_z(gradient)
    candidate = (residual_z >= options.residual_z_threshold).astype(np.uint8) * 255
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
    horizontal = np.zeros_like(candidate)
    areas: list[int] = []
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        component_width = int(stats[label, cv2.CC_STAT_WIDTH])
        component_height = int(stats[label, cv2.CC_STAT_HEIGHT])
        if area >= minimum_pixels and component_width >= 2 * component_height:
            horizontal[labels == label] = 255
            areas.append(area)
    candidate = horizontal
    component_count = len(areas)
    largest = max(areas, default=0)
    damage_pixels = int(np.count_nonzero(candidate))
    roi_pixels = int(candidate.size)
    ratio = 100.0 * damage_pixels / roi_pixels
    largest_ratio = 100.0 * largest / roi_pixels
    border = np.concatenate(
        (candidate[0], candidate[-1], candidate[:, 0], candidate[:, -1])
    )
    border_fraction = float(np.count_nonzero(border) / max(border.size, 1))
    exposure = float(np.mean((luminance <= 5) | (luminance >= 250), dtype=np.float64))
    confidence = float(np.clip(1.0 - 1.5 * border_fraction - 1.5 * exposure, 0.0, 1.0))
    full_mask = np.zeros((height, width), dtype=np.uint8)
    full_mask[y0:y1, x0:x1] = candidate
    return (
        {
            "damage_candidate_area_pct": ratio,
            "largest_component_ratio_pct": largest_ratio,
            "damage_candidate_pixels": damage_pixels,
            "visible_flank_roi_pixels": roi_pixels,
            "component_count": component_count,
            "segmentation_confidence": confidence,
            "border_contact_fraction": border_fraction,
            "extreme_exposure_fraction": exposure,
            "measurement_status": "provisional_pseudo_label_pending_human_review",
        },
        full_mask,
        (x0, y0, x1, y1),
    )


def _dhash(rgb: np.ndarray) -> str:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    small = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
    bits = small[:, 1:] > small[:, :-1]
    value = 0
    for bit in bits.reshape(-1):
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def _hamming(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def _duplicate_groups(rows: list[dict[str, Any]], threshold: int) -> None:
    exact: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        exact[str(row["source_sha256"])].append(index)
    for digest, indexes in exact.items():
        group = "exact-" + digest[:16] if len(indexes) > 1 else None
        for index in indexes:
            rows[index]["exact_duplicate_group"] = group
    parents = list(range(len(rows)))

    def root(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        a, b = root(left), root(right)
        if a != b:
            parents[max(a, b)] = min(a, b)

    scoped: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        scoped[(str(row["experiment"]), str(row["run"]), str(row["tooth_id"]))].append(
            index
        )
    for indexes in scoped.values():
        for offset, left in enumerate(indexes):
            for right in indexes[offset + 1 :]:
                if (
                    _hamming(
                        rows[left]["perceptual_hash"], rows[right]["perceptual_hash"]
                    )
                    <= threshold
                ):
                    union(left, right)
    groups: dict[int, list[int]] = defaultdict(list)
    for index in range(len(rows)):
        groups[root(index)].append(index)
    for indexes in groups.values():
        group = None
        if len(indexes) > 1:
            key = "|".join(sorted(rows[index]["image_id"] for index in indexes))
            group = "near-" + sha256(key.encode()).hexdigest()[:16]
        for index in indexes:
            rows[index]["near_duplicate_group"] = group


def _overlay(
    rgb: np.ndarray,
    mask: np.ndarray,
    roi: tuple[int, int, int, int],
    text: str,
) -> Image.Image:
    output = rgb.copy()
    tint = np.zeros_like(output)
    tint[..., 0] = 255
    selected = mask.astype(bool)
    output[selected] = (0.45 * output[selected] + 0.55 * tint[selected]).astype(
        np.uint8
    )
    image = Image.fromarray(output)
    draw = ImageDraw.Draw(image)
    draw.rectangle(roi, outline=(0, 255, 120), width=7)
    draw.rectangle((10, 10, min(image.width - 10, 1460), 82), fill=(0, 0, 0))
    draw.text((22, 24), text, fill=(255, 255, 255), font=ImageFont.load_default())
    return image


def profile_target_images(
    image_profile: pd.DataFrame,
    sources: Mapping[str, ImageSource],
    *,
    options: ImageDamageOptions,
    overlay_directory: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    overlay_directory.mkdir(parents=True, exist_ok=False)
    rows: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    materialization_options = ImageProfileOptions(
        mode="full",
        max_member_bytes=options.max_member_bytes,
        max_pixels=20_000_000,
    )
    ordered = image_profile.sort_values("image_id", kind="stable")
    for _, source_row in ordered.iterrows():
        image_id = str(source_row["image_id"])
        source = sources.get(str(source_row["source_member_id"]))
        base = {
            "schema_version": TARGET_SCHEMA_VERSION,
            "target_definition_version": TARGET_DEFINITION_VERSION,
            "image_id": image_id,
            "source_member_id": source_row["source_member_id"],
            "experiment": source_row["experiment"],
            "run": source_row["run"],
            "inspection_id": source_row["inspection_id"],
            "inspection_stage": source_row["inspection_stage"],
            "tooth_id": source_row["tooth_id"],
            "archive_path": source_row["archive_relative_path"],
            "archive_member": source_row["outer_archive_member"],
            "image_type": source_row["image_role"],
            "timestamp_text": source_row["timestamp_raw"],
            "timestamp_clock_status": source_row["timestamp_status"],
            "pairing_evidence": "parsed_experiment_run_tooth_from_archive_and_member",
            "width": source_row["width"],
            "height": source_row["height"],
            "decoding_status": "pending",
            "inclusion_status": "pending_measurement",
            "exclusion_reason": None,
        }
        if source is None or pd.isna(source_row["tooth_id"]):
            base.update(
                decoding_status="not_opened",
                inclusion_status="excluded",
                exclusion_reason="missing_source_or_tooth_identity",
            )
            exclusions.append(dict(base))
            rows.append(base)
            continue
        try:
            with materialize_image_source(
                source, options=materialization_options
            ) as path:
                digest = sha256_file(path)
                with Image.open(path) as image:
                    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
            metrics, mask, roi = measure_damage_candidate(rgb, options)
            overlay_name = f"{image_id}.jpg"
            overlay = _overlay(
                rgb,
                mask,
                roi,
                f"{source_row['experiment']} run={source_row['run']} tooth={source_row['tooth_id']} candidate={metrics['damage_candidate_area_pct']:.3f}% PROVISIONAL",
            )
            overlay.save(
                overlay_directory / overlay_name,
                format="JPEG",
                quality=options.overlay_jpeg_quality,
                optimize=True,
            )
            base.update(
                source_sha256=digest,
                perceptual_hash=_dhash(rgb),
                decoding_status="ok",
                inclusion_status="candidate_measurement",
                overlay_path=f"overlays/{overlay_name}",
                **metrics,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            base.update(
                decoding_status="error",
                inclusion_status="excluded",
                exclusion_reason=f"decode_or_measurement_error:{type(exc).__name__}:{exc}",
            )
            exclusions.append(dict(base))
        rows.append(base)
    valid = [row for row in rows if row["decoding_status"] == "ok"]
    _duplicate_groups(valid, options.near_duplicate_hamming)
    return rows, exclusions


def aggregate_targets(
    image_rows: Sequence[Mapping[str, Any]], options: ImageDamageOptions
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    run_images = [
        row
        for row in image_rows
        if row.get("decoding_status") == "ok" and pd.notna(row.get("run"))
    ]
    grouped: dict[tuple[str, int, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in run_images:
        grouped[(str(row["experiment"]), int(row["run"]), int(row["tooth_id"]))].append(
            row
        )
    teeth: list[dict[str, Any]] = []
    for (experiment, run, tooth), views in sorted(grouped.items()):
        selected = max(
            views,
            key=lambda row: (
                float(row["damage_candidate_area_pct"]),
                str(row["image_id"]),
            ),
        )
        values = [float(row["damage_candidate_area_pct"]) for row in views]
        teeth.append(
            {
                "schema_version": TARGET_SCHEMA_VERSION,
                "target_definition_version": TARGET_DEFINITION_VERSION,
                "target_verification_status": "provisional_pending_human_review",
                "experiment": experiment,
                "run": run,
                "tooth_id": tooth,
                "per_tooth_damage_candidate_pct": max(values),
                "largest_connected_candidate_pct": float(
                    selected["largest_component_ratio_pct"]
                ),
                "view_count": len(views),
                "view_aggregation": "maximum_candidate_ratio",
                "selected_image_id": selected["image_id"],
                "selected_overlay_path": selected["overlay_path"],
                "segmentation_confidence": selected["segmentation_confidence"],
                "pairing_evidence": selected["pairing_evidence"],
                "near_duplicate_group": selected.get("near_duplicate_group"),
                "human_review_status": "pending",
            }
        )
    per_run: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in teeth:
        per_run[(row["experiment"], row["run"])].append(row)
    targets: list[dict[str, Any]] = []
    cumulative: dict[str, float] = defaultdict(float)
    for (experiment, run), observations in sorted(per_run.items()):
        values = sorted(
            (float(row["per_tooth_damage_candidate_pct"]) for row in observations),
            reverse=True,
        )
        raw_top3 = float(np.mean(values[:3])) if len(values) >= 3 else np.nan
        cumulative[experiment] = max(cumulative[experiment], raw_top3)
        valid_teeth = len({int(row["tooth_id"]) for row in observations})
        included = valid_teeth >= options.minimum_valid_teeth
        targets.append(
            {
                "schema_version": TARGET_SCHEMA_VERSION,
                "target_definition_version": TARGET_DEFINITION_VERSION,
                "target_verification_status": "provisional_pending_human_review",
                "experiment": experiment,
                "run": run,
                "valid_tooth_count": valid_teeth,
                "minimum_required_teeth": options.minimum_valid_teeth,
                "inspection_complete": valid_teeth == 28,
                "raw_top1_pct": values[0] if values else np.nan,
                "raw_top3_mean_pct": raw_top3,
                "causal_monotonic_top3_mean_pct": cumulative[experiment],
                "raw_top5_mean_pct": (
                    float(np.mean(values[:5])) if len(values) >= 5 else np.nan
                ),
                "raw_all_tooth_mean_pct": float(np.mean(values)) if values else np.nan,
                "total_damage_burden_pct_points": float(np.sum(values)),
                "damaged_tooth_threshold_pct": options.damaged_tooth_threshold_pct,
                "damaged_tooth_count": sum(
                    value >= options.damaged_tooth_threshold_pct for value in values
                ),
                "monotonic_correction_pct_points": cumulative[experiment] - raw_top3,
                "inclusion_status": "included_provisional" if included else "excluded",
                "exclusion_reason": None if included else "insufficient_valid_teeth",
            }
        )
    review = [
        {
            **row,
            "review_status": "pending",
            "reviewer_decision": "",
            "corrected_damage_value": "",
            "reviewer_notes": "",
            "review_timestamp": "",
        }
        for row in teeth
    ]
    return teeth, targets, review


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv_path, parquet_path = stem.with_suffix(".csv"), stem.with_suffix(".parquet")
    frame.to_csv(csv_path, index=False)
    frame.to_parquet(parquet_path, index=False)
    return [csv_path, parquet_path]


def _save_plot_source(frame: pd.DataFrame, run: RunContext, name: str) -> Path:
    path = run.run_directory / f"tables/plot_source_{name}.csv"
    frame.to_csv(path, index=False)
    return path


def _bar(frame: pd.DataFrame, x: str, y: str, title: str, ylabel: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.bar(frame[x].astype(str), frame[y], color=ACADEMIC_COLORS[0])
    ax.set(title=title, xlabel=x.replace("_", " ").title(), ylabel=ylabel)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def _line(frame: pd.DataFrame, columns: Sequence[str], title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    for experiment, scoped in frame.groupby("experiment"):
        for index, column in enumerate(columns):
            ax.plot(
                scoped["run"],
                scoped[column],
                marker="o",
                color=ACADEMIC_COLORS[index % len(ACADEMIC_COLORS)],
                linestyle=(
                    "-" if len(columns) == 1 else ("-", "--", ":", "-.")[index % 4]
                ),
                label=f"{experiment} {column}",
            )
    ax.set(title=title, xlabel="Run", ylabel="Provisional candidate area (%)")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    return fig


def _heatmap(teeth: pd.DataFrame) -> plt.Figure:
    ordered = teeth.assign(group=lambda d: d.experiment + " R" + d.run.astype(str))
    matrix = ordered.pivot(
        index="group", columns="tooth_id", values="per_tooth_damage_candidate_pct"
    )
    fig, ax = plt.subplots(figsize=(14, 7))
    image = ax.imshow(matrix, aspect="auto", cmap="magma")
    ax.set(
        title="Provisional per-tooth damage-candidate heatmap",
        xlabel="Tooth",
        ylabel="Experiment/run",
    )
    ax.set_xticks(range(len(matrix.columns)), matrix.columns)
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    fig.colorbar(image, ax=ax, label="Candidate area (% ROI)")
    fig.tight_layout()
    return fig


def _pipeline_figure() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(14, 3.4))
    ax.axis("off")
    labels = [
        "Post-run image",
        "Fixed visible-flank ROI",
        "Illumination-normalized\ndark/textured candidate",
        "Per-tooth pseudo-label",
        "Top-3 run aggregate",
        "Human verification",
    ]
    for index, label in enumerate(labels):
        x = 0.02 + index * 0.16
        ax.add_patch(
            plt.Rectangle(
                (x, 0.35),
                0.13,
                0.3,
                transform=ax.transAxes,
                facecolor="#EAF0F5",
                edgecolor=ACADEMIC_COLORS[0],
            )
        )
        ax.text(
            x + 0.065,
            0.5,
            label,
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=9,
        )
        if index < len(labels) - 1:
            ax.annotate(
                "",
                xy=(x + 0.16, 0.5),
                xytext=(x + 0.13, 0.5),
                xycoords=ax.transAxes,
                arrowprops={"arrowstyle": "->"},
            )
    ax.set_title("Provisional target-definition pipeline (not organizer ground truth)")
    return fig


def _timeline_figure() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis("off")
    labels = [
        "Run sensor minutes",
        "Run end / input cutoff",
        "Post-run 28-tooth inspection",
        "Current-state scalar",
    ]
    xs = [0.08, 0.39, 0.65, 0.88]
    ax.plot([0.05, 0.93], [0.5, 0.5], transform=ax.transAxes, color=ACADEMIC_COLORS[0])
    for x, label in zip(xs, labels, strict=True):
        ax.scatter([x], [0.5], transform=ax.transAxes, s=100, color=ACADEMIC_COLORS[1])
        ax.text(x, 0.67, label, ha="center", transform=ax.transAxes)
    ax.set_title(
        "End-of-run current-state estimation; six hours is cadence, not forecast horizon"
    )
    return fig


def _contact_sheets(teeth: pd.DataFrame, run: RunContext) -> list[Path]:
    outputs: list[Path] = []
    directory = run.run_directory / "figures/contact_sheets"
    directory.mkdir(parents=True)
    for (experiment, run_number), scoped in teeth.groupby(["experiment", "run"]):
        canvas = Image.new("RGB", (1600, 1200), "white")
        draw = ImageDraw.Draw(canvas)
        for index, (_, row) in enumerate(scoped.sort_values("tooth_id").iterrows()):
            image = Image.open(
                run.run_directory / row["selected_overlay_path"]
            ).convert("RGB")
            image.thumbnail((220, 230))
            x, y = (index % 7) * 225 + 12, (index // 7) * 285 + 35
            canvas.paste(image, (x, y))
            draw.text(
                (x, y + 235),
                f"T{row['tooth_id']} {row['per_tooth_damage_candidate_pct']:.2f}%",
                fill="black",
            )
        draw.text(
            (12, 8),
            f"{experiment} Run {run_number} — PROVISIONAL pseudo-labels",
            fill="black",
        )
        path = directory / f"{experiment.lower()}_run_{int(run_number)}.jpg"
        canvas.save(path, quality=88, optimize=True)
        outputs.append(path)
    return outputs


def write_target_run(
    image_rows: list[dict[str, Any]],
    teeth_rows: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    exclusions: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
    preflight: Mapping[str, Any],
) -> list[ArtifactRecord]:
    apply_academic_style()
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    input_path = run.write_input_manifest(input_manifest)
    artifacts += [
        run.artifact(config_path, role="resolved_configuration"),
        run.artifact(input_path, role="input_manifest"),
    ]
    frames = {
        "image_manifest": pd.DataFrame(image_rows),
        "per_tooth_damage": pd.DataFrame(teeth_rows),
        "run_damage_targets": pd.DataFrame(target_rows),
        "excluded_target_observations": pd.DataFrame(exclusions),
        "human_review_queue": pd.DataFrame(review_rows),
    }
    for name, frame in frames.items():
        for path in _write_frame(frame, run.run_directory / f"tables/{name}"):
            artifacts.append(run.artifact(path, role=name))
    target_definition = {
        "schema_version": TARGET_SCHEMA_VERSION,
        "target_definition_version": TARGET_DEFINITION_VERSION,
        "status": TARGET_STATUS,
        "unit": "percent_visible_flank_candidate_area",
        "per_image": "100 * damage_candidate_pixels / fixed_visible_flank_roi_pixels",
        "per_tooth_multi_view": "maximum candidate ratio across available views",
        "raw_run_target": "mean of three largest per-tooth ratios",
        "monotonic_run_target": "causal cumulative maximum of raw run target within experiment",
        "minimum_valid_teeth": resolved_config["target_definition"][
            "minimum_valid_teeth"
        ],
        "human_verification_required": True,
        "organizer_ground_truth": False,
    }
    definition_path = run.run_directory / "config/target_definition.yaml"
    definition_path.write_text(
        yaml.safe_dump(target_definition, sort_keys=False), encoding="utf-8"
    )
    artifacts.append(run.artifact(definition_path, role="target_definition"))
    targets = frames["run_damage_targets"]
    teeth = frames["per_tooth_damage"]
    images = frames["image_manifest"]
    report = {
        "schema_version": TARGET_SCHEMA_VERSION,
        "classification": TARGET_STATUS,
        "target_definition_version": TARGET_DEFINITION_VERSION,
        "image_record_count": len(images),
        "decoded_image_count": int(images.decoding_status.eq("ok").sum()),
        "excluded_image_count": int(images.decoding_status.ne("ok").sum()),
        "per_tooth_record_count": len(teeth),
        "run_target_count": len(targets),
        "included_run_target_count": int(
            targets.inclusion_status.eq("included_provisional").sum()
        ),
        "human_review_pending_count": len(review_rows),
        "counts_by_experiment": images.groupby("experiment")
        .size()
        .astype(int)
        .to_dict(),
        "image_protocol_by_experiment": {
            "EXP-A": "ten close-ups for teeth 1-4 plus canonical teeth 5-28; Run 5 has three extra canonical views",
            "EXP-B": "ten close-ups for teeth 1-4 plus canonical teeth 5-28",
            "EXP-F": "one canonical view per tooth",
        },
        "physical_validity": "provisional pseudo-label; mask and ROI require human verification",
        "preflight": dict(preflight),
        "raw_archives_modified": False,
    }
    quality_path = run.run_directory / "reports/target_quality_report.json"
    quality_path.write_text(json_text(report), encoding="utf-8")
    provenance_path = run.run_directory / "manifests/target_provenance_manifest.json"
    provenance_path.write_text(
        json_text(
            {
                "schema_version": TARGET_SCHEMA_VERSION,
                "official_source": resolved_config["official_challenge"],
                "target_definition": target_definition,
                "inputs": list(input_manifest),
            }
        ),
        encoding="utf-8",
    )
    guide = """# Human target review guide

Every value is a provisional pseudo-label, not organizer ground truth. Open the selected overlay using `selected_overlay_path`; the green rectangle is the fixed visible-flank candidate ROI and red pixels are the automated dark/textured candidate mask.

For every row in `tables/human_review_queue.csv`:

1. Set `review_status` to `reviewed` or `needs_second_review`.
2. Set `reviewer_decision` to `accept`, `reject`, or `correct`.
3. If corrected, enter a percentage in `corrected_damage_value` and explain the ROI/mask correction in `reviewer_notes`.
4. Record an ISO-8601 `review_timestamp` and reviewer identity in notes.
5. Reject glare, shadow, tooth-edge, framing, focus, or non-spall texture falsely selected as damage.

Do not promote this target version to scientifically verified until protocol differences (A/B close-ups versus F canonical views) and representative low/medium/high masks have been reviewed.
"""
    guide_path = run.run_directory / "reports/HUMAN_TARGET_REVIEW_GUIDE.md"
    guide_path.write_text(guide, encoding="utf-8")
    for path, role in (
        (quality_path, "target_quality_report"),
        (provenance_path, "target_provenance_manifest"),
        (guide_path, "human_target_review_guide"),
    ):
        artifacts.append(run.artifact(path, role=role))
    valid_counts = (
        teeth.groupby(["experiment", "run"])
        .tooth_id.nunique()
        .reset_index(name="valid_image_count")
    )
    coverage = valid_counts.rename(columns={"valid_image_count": "valid_tooth_count"})
    confidence = teeth[["experiment", "run", "tooth_id", "segmentation_confidence"]]
    corrections = targets[["experiment", "run", "monotonic_correction_pct_points"]]
    missing = targets[["experiment", "run", "valid_tooth_count", "inclusion_status"]]
    sources = {
        "valid_image_count_by_experiment_run": valid_counts,
        "tooth_coverage_by_run": coverage,
        "per_tooth_damage_heatmap": teeth[
            ["experiment", "run", "tooth_id", "per_tooth_damage_candidate_pct"]
        ],
        "raw_run_damage_trajectory": targets[
            ["experiment", "run", "raw_top3_mean_pct"]
        ],
        "monotonic_run_damage_trajectory": targets[
            ["experiment", "run", "causal_monotonic_top3_mean_pct"]
        ],
        "aggregation_comparison": targets[
            [
                "experiment",
                "run",
                "raw_top1_pct",
                "raw_top3_mean_pct",
                "raw_top5_mean_pct",
                "raw_all_tooth_mean_pct",
            ]
        ],
        "target_distribution_by_experiment": targets[
            ["experiment", "run", "raw_top3_mean_pct"]
        ],
        "target_increments_by_run": targets.assign(
            increment=targets.groupby("experiment").raw_top3_mean_pct.diff()
        )[["experiment", "run", "increment"]],
        "missing_excluded_target_observations": missing,
        "segmentation_confidence_distribution": confidence,
        "monotonic_corrections_applied": corrections,
        "target_definition_pipeline": pd.DataFrame(
            {
                "stage_order": range(1, 7),
                "stage": [
                    "post_run_image",
                    "visible_flank_roi",
                    "candidate_segmentation",
                    "per_tooth_pseudo_label",
                    "top3_run_aggregate",
                    "human_verification",
                ],
            }
        ),
        "current_state_estimation_timeline": pd.DataFrame(
            {
                "stage_order": range(1, 5),
                "stage": [
                    "run_sensor_minutes",
                    "run_end_cutoff",
                    "post_run_inspection",
                    "current_state_scalar",
                ],
            }
        ),
        "representative_segmentation_overlay_montage": teeth.sort_values(
            "per_tooth_damage_candidate_pct"
        ).iloc[[0, len(teeth) // 2, -1]][
            [
                "selected_image_id",
                "selected_overlay_path",
                "per_tooth_damage_candidate_pct",
                "segmentation_confidence",
            ]
        ],
    }
    for name, frame in sources.items():
        artifacts.append(
            run.artifact(
                _save_plot_source(frame, run, name), role=f"plot_source_{name}"
            )
        )
    figures: dict[str, plt.Figure] = {
        "valid_image_count_by_experiment_run": _bar(
            valid_counts.assign(
                group=valid_counts.experiment + " R" + valid_counts.run.astype(str)
            ),
            "group",
            "valid_image_count",
            "Valid provisional tooth observations by run",
            "Valid teeth",
        ),
        "tooth_coverage_by_run": _bar(
            coverage.assign(
                group=coverage.experiment + " R" + coverage.run.astype(str)
            ),
            "group",
            "valid_tooth_count",
            "Tooth coverage by run",
            "Unique teeth",
        ),
        "per_tooth_damage_heatmap": _heatmap(teeth),
        "raw_run_damage_trajectory": _line(
            targets, ["raw_top3_mean_pct"], "Raw provisional top-3 damage trajectory"
        ),
        "monotonic_run_damage_trajectory": _line(
            targets,
            ["causal_monotonic_top3_mean_pct"],
            "Causal monotonic provisional trajectory",
        ),
        "aggregation_comparison": _line(
            targets,
            [
                "raw_top1_pct",
                "raw_top3_mean_pct",
                "raw_top5_mean_pct",
                "raw_all_tooth_mean_pct",
            ],
            "Aggregation comparison (provisional)",
        ),
        "target_distribution_by_experiment": _bar(
            targets.groupby("experiment", as_index=False).raw_top3_mean_pct.mean(),
            "experiment",
            "raw_top3_mean_pct",
            "Mean provisional target by experiment",
            "Mean top-3 candidate area (%)",
        ),
        "target_increments_by_run": _bar(
            sources["target_increments_by_run"]
            .fillna(0)
            .assign(group=lambda d: d.experiment + " R" + d.run.astype(str)),
            "group",
            "increment",
            "Raw target increments by run",
            "Change (percentage points)",
        ),
        "missing_excluded_target_observations": _bar(
            missing.assign(group=lambda d: d.experiment + " R" + d.run.astype(str)),
            "group",
            "valid_tooth_count",
            "Target coverage and exclusions",
            "Valid teeth",
        ),
        "segmentation_confidence_distribution": plt.figure(figsize=(8, 4.8)),
        "monotonic_corrections_applied": _bar(
            corrections.assign(group=lambda d: d.experiment + " R" + d.run.astype(str)),
            "group",
            "monotonic_correction_pct_points",
            "Causal monotonic corrections",
            "Correction (percentage points)",
        ),
        "target_definition_pipeline": _pipeline_figure(),
        "current_state_estimation_timeline": _timeline_figure(),
    }
    ax = figures["segmentation_confidence_distribution"].subplots()
    ax.hist(confidence.segmentation_confidence, bins=15, color=ACADEMIC_COLORS[1])
    ax.set(
        title="Provisional segmentation-confidence distribution",
        xlabel="Heuristic confidence",
        ylabel="Tooth observations",
    )
    montage_rows = sources["representative_segmentation_overlay_montage"]
    montage = Image.new("RGB", (1500, 480), "white")
    for index, (_, row) in enumerate(montage_rows.iterrows()):
        image = Image.open(run.run_directory / row.selected_overlay_path).convert("RGB")
        image.thumbnail((490, 440))
        montage.paste(image, (index * 500 + (500 - image.width) // 2, 20))
    montage_path = (
        run.run_directory / "figures/representative_segmentation_overlay_montage.png"
    )
    montage.save(montage_path, dpi=(300, 300))
    artifacts.append(
        run.artifact(
            montage_path, role="representative_segmentation_overlay_montage_png"
        )
    )
    for name, figure in figures.items():
        for path in save_figure_pair(figure, run.run_directory / f"figures/{name}"):
            artifacts.append(run.artifact(path, role=f"{name}_{path.suffix[1:]}"))
    for path in _contact_sheets(teeth, run):
        artifacts.append(run.artifact(path, role="per_run_contact_sheet"))
    index_lines = [
        "# Target figure index",
        "",
        "> All values are provisional pseudo-labels pending human review.",
        "",
    ]
    for name in sources:
        index_lines += [
            f"- `{name}`: `tables/plot_source_{name}.csv`; `figures/{name}.png`/`.svg` where applicable.",
            "",
        ]
    index_path = run.run_directory / "reports/target_figure_index.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    artifacts.append(run.artifact(index_path, role="target_figure_index"))
    return finalize_run(run, artifacts)
