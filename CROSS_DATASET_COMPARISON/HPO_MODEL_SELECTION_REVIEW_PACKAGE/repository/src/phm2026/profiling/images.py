"""Dataset-neutral, bounded image structure and quality profiling."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from hashlib import sha256
import csv
import json
import math
from pathlib import Path
import time
from typing import Any, Iterator, Literal

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError

from ..data_contracts import ImageRecord, deterministic_id
from ..datasets import BaseDatasetAdapter
from ..utils.provenance import ArtifactRecord, RunContext
from .archive_io import (
    ArchiveMaterializationError,
    ArchiveMemberRef,
    materialize_archive_member,
)

IMAGE_PROFILE_SCHEMA_VERSION = "1.0.0"
ImageMode = Literal["header", "sampled", "full"]
_IMAGE_SUFFIXES = {"jpg", "jpeg", "png", "tif", "tiff", "bmp"}
_ORIENTATION_NAMES = {
    1: "normal",
    2: "mirror_horizontal",
    3: "rotate_180",
    4: "mirror_vertical",
    5: "transpose",
    6: "rotate_90_cw",
    7: "transverse",
    8: "rotate_90_ccw",
}


@dataclass(frozen=True, slots=True)
class ImageProfileIssue:
    severity: Literal["info", "warning", "error"]
    code: str
    source: str | None
    message: str


@dataclass(frozen=True, slots=True)
class ImageProfileOptions:
    mode: ImageMode = "header"
    seed: int = 0
    sample_size: int = 104
    max_member_bytes: int | None = 8 * 1024 * 1024
    max_pixels: int = 50_000_000
    near_duplicate_hamming: int = 4
    temp_root: Path | None = None

    def __post_init__(self) -> None:
        if self.mode not in {"header", "sampled", "full"}:
            raise ValueError("mode must be header, sampled, or full")
        for field, value in (
            ("sample_size", self.sample_size),
            ("max_pixels", self.max_pixels),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{field} must be a positive integer")
        if self.max_member_bytes is not None and (
            isinstance(self.max_member_bytes, bool)
            or not isinstance(self.max_member_bytes, int)
            or self.max_member_bytes <= 0
        ):
            raise ValueError("max_member_bytes must be positive or null")
        if (
            isinstance(self.near_duplicate_hamming, bool)
            or not isinstance(self.near_duplicate_hamming, int)
            or not 0 <= self.near_duplicate_hamming <= 64
        ):
            raise ValueError("near_duplicate_hamming must be an integer from 0 to 64")
        if self.temp_root is not None:
            object.__setattr__(self, "temp_root", Path(self.temp_root))


@dataclass(frozen=True, slots=True)
class ImageSource:
    source_member_id: str
    archive_asset_id: str
    source_kind: Literal["file", "zip_member", "nested_zip_member"]
    source_relative_path: str
    file_path: Path | None
    archive_path: Path | None
    archive_relative_path: str | None
    outer_member_path: str | None
    nested_member_path: str | None
    member_occurrence: int
    nested_member_occurrence: int
    experiment: str
    authoritative_outer_run: int | None
    compressed_size_bytes: int | None
    encoded_size_bytes: int
    crc32: str | None
    annotation_status: str = "none_discovered_in_archive_listing"
    annotation_types: tuple[str, ...] = ()
    annotation_refs: tuple[str, ...] = ()

    @property
    def source_key(self) -> str:
        if self.source_kind == "file":
            return self.source_relative_path
        nested = f"!{self.nested_member_path}" if self.nested_member_path else ""
        return f"{self.archive_relative_path}!{self.outer_member_path}{nested}"


@dataclass(slots=True)
class ImageProfileResult:
    images: list[dict[str, Any]]
    near_duplicate_pairs: list[dict[str, Any]]
    issues: list[ImageProfileIssue]
    sources_by_image_id: dict[str, ImageSource]
    mode: ImageMode
    discovered_source_count: int
    selected_source_count: int
    quality_selected_count: int
    limited: bool
    elapsed_seconds: float

    def summary(self) -> dict[str, Any]:
        readable = [row for row in self.images if row["header_status"] == "ok"]
        counts_by_scope: dict[str, int] = Counter()
        counts_by_experiment: Counter[str] = Counter()
        counts_by_inspection: Counter[str] = Counter()
        tooth_counts: Counter[str] = Counter()
        annotation_type_counts: Counter[str] = Counter()
        anomaly_reason_counts: Counter[str] = Counter()
        for row in readable:
            run = (
                f"run-{int(row['run'])}"
                if row["run"] is not None
                else row["inspection_stage"]
            )
            counts_by_experiment[str(row["experiment"])] += 1
            counts_by_scope[f"{row['experiment']}/{run}"] += 1
            counts_by_inspection[
                f"{row['experiment']}/{run}/{row['inspection_id']}"
            ] += 1
            if row["tooth_id"] is not None:
                tooth_counts[f"{row['experiment']}/{run}/tooth-{row['tooth_id']}"] += 1
            for annotation_type in json.loads(str(row["annotation_types_json"])):
                annotation_type_counts[str(annotation_type)] += 1
            for reason in json.loads(str(row["anomaly_reasons_json"])):
                anomaly_reason_counts[str(reason)] += 1
        exact_groups = {
            str(row["exact_duplicate_group_id"])
            for row in readable
            if row["exact_duplicate_group_id"] is not None
        }
        return {
            "schema_version": IMAGE_PROFILE_SCHEMA_VERSION,
            "mode": self.mode,
            "discovered_source_count": self.discovered_source_count,
            "selected_source_count": self.selected_source_count,
            "profiled_image_count": len(self.images),
            "readable_header_count": len(readable),
            "unreadable_header_count": len(self.images) - len(readable),
            "pixel_quality_selected_count": self.quality_selected_count,
            "pixel_quality_success_count": sum(
                row["pixel_status"] == "ok" for row in self.images
            ),
            "counts_by_experiment": dict(sorted(counts_by_experiment.items())),
            "counts_by_experiment_run_or_stage": dict(sorted(counts_by_scope.items())),
            "counts_by_inspection": dict(sorted(counts_by_inspection.items())),
            "counts_by_tooth": dict(sorted(tooth_counts.items())),
            "shape_counts_hwc": dict(
                sorted(Counter(str(row["shape_hwc_json"]) for row in readable).items())
            ),
            "resolution_counts": dict(
                sorted(
                    Counter(
                        f"{row['width']}x{row['height']}" for row in readable
                    ).items()
                )
            ),
            "mode_counts": dict(
                sorted(Counter(str(row["color_mode"]) for row in readable).items())
            ),
            "dtype_counts": dict(
                sorted(Counter(str(row["dtype"]) for row in readable).items())
            ),
            "bit_depth_counts": dict(
                sorted(Counter(str(row["bit_depth"]) for row in readable).items())
            ),
            "format_counts": dict(
                sorted(Counter(str(row["file_format"]) for row in readable).items())
            ),
            "aspect_ratio_counts": dict(
                sorted(
                    Counter(
                        format(float(row["aspect_ratio"]), ".12g") for row in readable
                    ).items()
                )
            ),
            "annotation_status_counts": dict(
                sorted(
                    Counter(
                        str(row["annotation_status"]) for row in self.images
                    ).items()
                )
            ),
            "annotation_type_counts": dict(sorted(annotation_type_counts.items())),
            "anomaly_reason_counts": dict(sorted(anomaly_reason_counts.items())),
            "unusual_shape_or_mode_count": sum(
                "singleton_shape" in json.loads(str(row["anomaly_reasons_json"]))
                or "singleton_color_mode"
                in json.loads(str(row["anomaly_reasons_json"]))
                for row in readable
            ),
            "timestamp_status_counts": dict(
                sorted(
                    Counter(str(row["timestamp_status"]) for row in self.images).items()
                )
            ),
            "exact_duplicate_group_count": len(exact_groups),
            "exact_hash_covered_count": sum(
                row["exact_sha256"] is not None for row in self.images
            ),
            "near_duplicate_pair_count": len(self.near_duplicate_pairs),
            "perceptual_hash_covered_count": sum(
                row["perceptual_hash"] is not None for row in self.images
            ),
            "limited": self.limited,
            "elapsed_seconds": self.elapsed_seconds,
            "encoded_bytes": sum(
                int(row["encoded_size_bytes"] or 0) for row in self.images
            ),
            "issue_counts": dict(
                sorted(Counter(issue.severity for issue in self.issues).items())
            ),
        }


def _nullable_int(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    return int(value)


def load_image_sources(
    inventory_members: Path,
    *,
    asset_inventory: Path,
    data_root: Path,
) -> list[ImageSource]:
    members = pd.read_parquet(inventory_members)
    assets = pd.read_parquet(asset_inventory)
    required = {
        "member_id",
        "archive_asset_id",
        "archive_relative_path",
        "archive_member",
        "member_file_type",
        "modality",
        "experiment",
        "compressed_size_bytes",
        "uncompressed_size_bytes",
        "checksum",
    }
    missing = sorted(required - set(members.columns))
    if missing:
        raise ValueError(
            "inventory member table is missing columns: " + ", ".join(missing)
        )
    outer_runs = {
        str(row["asset_id"]): _nullable_int(row["run"])
        for row in assets.to_dict("records")
    }
    image_rows = members[
        members["modality"].eq("image")
        & members["member_file_type"].str.lower().isin(_IMAGE_SUFFIXES)
    ].sort_values(
        ["experiment", "run", "archive_relative_path", "archive_member"],
        na_position="first",
        kind="mergesort",
    )
    root = data_root.resolve()
    occurrences: Counter[tuple[str, str]] = Counter()
    sources: list[ImageSource] = []
    for row in image_rows.to_dict("records"):
        key = (str(row["archive_asset_id"]), str(row["archive_member"]))
        occurrences[key] += 1
        archive_path = (root / str(row["archive_relative_path"])).resolve()
        try:
            archive_path.relative_to(root)
        except ValueError as exc:
            raise ValueError("inventory image archive escapes data root") from exc
        sources.append(
            ImageSource(
                source_member_id=str(row["member_id"]),
                archive_asset_id=str(row["archive_asset_id"]),
                source_kind="zip_member",
                source_relative_path=f"{row['archive_relative_path']}!{row['archive_member']}",
                file_path=None,
                archive_path=archive_path,
                archive_relative_path=str(row["archive_relative_path"]),
                outer_member_path=str(row["archive_member"]),
                nested_member_path=None,
                member_occurrence=occurrences[key],
                nested_member_occurrence=1,
                experiment=str(row["experiment"]),
                authoritative_outer_run=outer_runs.get(str(row["archive_asset_id"])),
                compressed_size_bytes=int(row["compressed_size_bytes"]),
                encoded_size_bytes=int(row["uncompressed_size_bytes"]),
                crc32=str(row["checksum"]),
            )
        )
    return sources


def select_image_sources(
    sources: Sequence[ImageSource], *, limit: int | None = None
) -> list[ImageSource]:
    if limit is not None and (
        isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0
    ):
        raise ValueError("limit must be a positive integer or null")
    ordered = sorted(sources, key=lambda source: source.source_key)
    return ordered if limit is None else ordered[:limit]


def _stable_rank(seed: int, key: str) -> str:
    return sha256(f"{seed}:{key}".encode("utf-8")).hexdigest()


def select_quality_source_ids(
    sources: Sequence[ImageSource], *, mode: ImageMode, sample_size: int, seed: int
) -> set[str]:
    if mode == "header":
        return set()
    if mode == "full":
        return {source.source_member_id for source in sources}
    groups: dict[str, list[ImageSource]] = defaultdict(list)
    for source in sources:
        groups[source.archive_relative_path or source.source_relative_path].append(
            source
        )
    for values in groups.values():
        values.sort(
            key=lambda source: (
                _stable_rank(seed, source.source_key),
                source.source_key,
            )
        )
    selected: list[str] = []
    positions: Counter[str] = Counter()
    group_names = sorted(groups)
    while len(selected) < min(sample_size, len(sources)):
        changed = False
        for group in group_names:
            position = positions[group]
            if position < len(groups[group]):
                selected.append(groups[group][position].source_member_id)
                positions[group] += 1
                changed = True
                if len(selected) >= min(sample_size, len(sources)):
                    break
        if not changed:
            break
    return set(selected)


@contextmanager
def materialize_image_source(
    source: ImageSource, *, options: ImageProfileOptions
) -> Iterator[Path]:
    if source.source_kind == "file":
        if source.file_path is None:
            raise ValueError("ordinary image source has no file_path")
        yield source.file_path
        return
    if (
        source.archive_path is None
        or source.archive_relative_path is None
        or source.outer_member_path is None
    ):
        raise ValueError("archive image source is incomplete")
    reference = ArchiveMemberRef(
        archive_path=source.archive_path,
        archive_relative_path=source.archive_relative_path,
        member_path=source.outer_member_path,
        nested_member_path=source.nested_member_path,
        member_occurrence=source.member_occurrence,
        nested_member_occurrence=source.nested_member_occurrence,
        expected_compressed_size_bytes=(
            source.compressed_size_bytes if source.nested_member_path is None else None
        ),
        expected_uncompressed_size_bytes=source.encoded_size_bytes,
        expected_crc32=source.crc32,
    )
    with materialize_archive_member(
        reference,
        temp_root=options.temp_root,
        max_member_bytes=options.max_member_bytes,
    ) as path:
        yield path


def _mode_metadata(mode: str) -> tuple[int | None, str | None, str | None]:
    if mode == "1":
        return 1, "bool", "pillow_mode:1"
    if mode in {"L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV"}:
        return 8, "uint8", f"pillow_mode:{mode}"
    if mode.startswith("I;16"):
        return 16, "uint16", f"pillow_mode:{mode}"
    if mode == "I":
        return 32, "int32", "pillow_mode:I"
    if mode == "F":
        return 32, "float32", "pillow_mode:F"
    return None, None, None


def _luma(array: np.ndarray) -> tuple[np.ndarray, str]:
    values = np.asarray(array)
    if values.ndim == 2:
        luminance = values.astype(np.float64)
    elif values.ndim == 3 and values.shape[2] >= 3:
        rgb = values[..., :3].astype(np.float64)
        luminance = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    elif values.ndim == 3:
        luminance = values[..., 0].astype(np.float64)
    else:
        raise ValueError(f"unsupported decoded image shape {values.shape}")
    if np.issubdtype(values.dtype, np.integer):
        maximum = float(np.iinfo(values.dtype).max)
        basis = f"normalized_integer_luma/{maximum:g}"
    elif np.issubdtype(values.dtype, np.bool_):
        maximum = 1.0
        basis = "boolean_luma"
    else:
        finite = luminance[np.isfinite(luminance)]
        maximum = 1.0 if finite.size and float(finite.max()) <= 1.0 else 255.0
        basis = f"normalized_float_luma/{maximum:g}"
    return np.clip(luminance / maximum, 0.0, 1.0), basis


def _dhash(image: Image.Image) -> str:
    gray = ImageOps.grayscale(image).resize((9, 8), Image.Resampling.LANCZOS)
    array = np.asarray(gray, dtype=np.uint8)
    bits = array[:, 1:] > array[:, :-1]
    value = 0
    for bit in bits.reshape(-1):
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def _quality(path: Path, *, max_pixels: int) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
        if width * height > max_pixels:
            raise ValueError(
                f"image has {width * height} pixels, exceeding {max_pixels}"
            )
        oriented = ImageOps.exif_transpose(image)
        array = np.asarray(oriented)
        luminance, basis = _luma(array)
        center = luminance[1:-1, 1:-1]
        if center.size:
            laplacian = (
                -4.0 * center
                + luminance[:-2, 1:-1]
                + luminance[2:, 1:-1]
                + luminance[1:-1, :-2]
                + luminance[1:-1, 2:]
            )
            blur = float(laplacian.var())
        else:
            blur = None
        return {
            "pixel_status": "ok",
            "pixel_error": None,
            "quality_intensity_basis": basis,
            "intensity_min": float(luminance.min()),
            "intensity_max": float(luminance.max()),
            "intensity_mean": float(luminance.mean()),
            "intensity_std": float(luminance.std()),
            "blur_laplacian_variance": blur,
            "dark_pixel_fraction": float((luminance <= 0.05).mean()),
            "overexposed_pixel_fraction": float((luminance >= 0.95).mean()),
            "clipped_pixel_fraction": float(
                ((luminance <= 0.0) | (luminance >= 1.0)).mean()
            ),
            "perceptual_hash": _dhash(oriented),
            "perceptual_hash_algorithm": "dhash64-v1",
        }


def _quality_null(
    status: str = "not_selected", error: str | None = None
) -> dict[str, Any]:
    return {
        "pixel_status": status,
        "pixel_error": error,
        "quality_intensity_basis": None,
        "intensity_min": None,
        "intensity_max": None,
        "intensity_mean": None,
        "intensity_std": None,
        "blur_laplacian_variance": None,
        "dark_pixel_fraction": None,
        "overexposed_pixel_fraction": None,
        "clipped_pixel_fraction": None,
        "perceptual_hash": None,
        "perceptual_hash_algorithm": None,
    }


def _identity_dict(adapter: BaseDatasetAdapter, source: ImageSource) -> dict[str, Any]:
    identity = adapter.parse_image_identity(
        source.archive_relative_path or source.source_relative_path,
        archive_member=source.nested_member_path
        or source.outer_member_path
        or Path(source.source_relative_path).name,
    )
    values = asdict(identity)
    for key, value in list(values.items()):
        if hasattr(value, "isoformat"):
            values[key] = value.isoformat()
    return values


def _base_image_id(source: ImageSource) -> str:
    return deterministic_id(
        "image_profile",
        {"source": source.source_key, "occurrence": source.member_occurrence},
    )


def _profile_one(
    source: ImageSource,
    *,
    adapter: BaseDatasetAdapter,
    options: ImageProfileOptions,
    quality_selected: bool,
) -> tuple[dict[str, Any], list[ImageProfileIssue]]:
    image_id = _base_image_id(source)
    identity = _identity_dict(adapter, source)
    row: dict[str, Any] = {
        "schema_version": IMAGE_PROFILE_SCHEMA_VERSION,
        "image_id": image_id,
        "contract_image_id": None,
        "contract_asset_id": deterministic_id(
            "image_source_asset", {"source": source.source_key}
        ),
        "source_member_id": source.source_member_id,
        "archive_asset_id": source.archive_asset_id,
        "source_kind": source.source_kind,
        "source_relative_path": source.source_relative_path,
        "archive_relative_path": source.archive_relative_path,
        "outer_archive_member": source.outer_member_path,
        "nested_archive_member": source.nested_member_path,
        "member_occurrence": source.member_occurrence,
        "nested_member_occurrence": source.nested_member_occurrence,
        "authoritative_outer_run": source.authoritative_outer_run,
        **identity,
        "compressed_size_bytes": source.compressed_size_bytes,
        "encoded_size_bytes": source.encoded_size_bytes,
        "crc32": source.crc32,
        "header_status": "error",
        "header_error": None,
        "width": None,
        "height": None,
        "channels": None,
        "shape_hwc_json": None,
        "array_layout": "HWC",
        "color_mode": None,
        "is_grayscale": None,
        "is_rgb": None,
        "bit_depth": None,
        "bit_depth_evidence": None,
        "dtype": None,
        "file_format": None,
        "extension_matches_format": None,
        "aspect_ratio": None,
        "exif_orientation": None,
        "orientation_name": None,
        "annotation_status": source.annotation_status,
        "annotation_types_json": json.dumps(source.annotation_types),
        "annotation_refs_json": json.dumps(source.annotation_refs),
        "annotation_evidence": "D1.1_archive_central_directory_extensions",
        "annotation_assessment_scope": "members_listed_in_source_photo_archive",
        "quality_selected": quality_selected,
        "quality_scope": ("full_pixels" if quality_selected else "header_only"),
        "quality_selection_reason": (
            "full_mode"
            if options.mode == "full"
            else (
                "deterministic_archive_stratified_sample"
                if quality_selected
                else "not_selected"
            )
        ),
        **_quality_null(),
        "exact_sha256": None,
        "exact_duplicate_group_id": None,
        "exact_duplicate_count": None,
        "anomaly_reasons_json": "[]",
    }
    issues: list[ImageProfileIssue] = []
    try:
        with materialize_image_source(source, options=options) as path:
            with Image.open(path) as image:
                width, height = image.size
                channels = len(image.getbands())
                bit_depth, dtype, bit_evidence = _mode_metadata(image.mode)
                orientation = image.getexif().get(274)
                file_format = image.format
                extension = (
                    Path(
                        source.nested_member_path
                        or source.outer_member_path
                        or source.source_relative_path
                    )
                    .suffix.lower()
                    .lstrip(".")
                )
                compatible = {
                    "jpeg": {"jpg", "jpeg"},
                    "png": {"png"},
                    "tiff": {"tif", "tiff"},
                    "bmp": {"bmp"},
                }
                row.update(
                    {
                        "header_status": "ok",
                        "width": width,
                        "height": height,
                        "channels": channels,
                        "shape_hwc_json": json.dumps(
                            [height, width, channels], separators=(",", ":")
                        ),
                        "color_mode": image.mode,
                        "is_grayscale": image.mode in {"1", "L", "I", "F"}
                        or image.mode.startswith("I;16"),
                        "is_rgb": image.mode in {"RGB", "RGBA"},
                        "bit_depth": bit_depth,
                        "bit_depth_evidence": bit_evidence,
                        "dtype": dtype or "unknown",
                        "file_format": file_format,
                        "extension_matches_format": extension
                        in compatible.get(str(file_format).lower(), {extension}),
                        "aspect_ratio": width / height,
                        "exif_orientation": orientation,
                        "orientation_name": (
                            _ORIENTATION_NAMES.get(orientation)
                            if orientation is not None
                            else None
                        ),
                    }
                )
                timestamp = identity.get("timestamp_utc")
                if isinstance(timestamp, str):
                    from datetime import datetime

                    timestamp = datetime.fromisoformat(timestamp)
                contract = ImageRecord(
                    asset_id=row["contract_asset_id"],
                    width=width,
                    height=height,
                    channels=channels,
                    dtype=row["dtype"],
                    timestamp=timestamp,
                    tooth_id=identity.get("tooth_id"),
                    inspection_id=identity.get("inspection_id"),
                    annotation_types=source.annotation_types,
                    annotation_refs=source.annotation_refs,
                )
                row["contract_image_id"] = contract.image_id
            if quality_selected:
                row.update(_quality(path, max_pixels=options.max_pixels))
                digest = sha256()
                with path.open("rb") as handle:
                    while block := handle.read(1024 * 1024):
                        digest.update(block)
                row["exact_sha256"] = digest.hexdigest()
    except (
        ArchiveMaterializationError,
        OSError,
        RuntimeError,
        UnidentifiedImageError,
        ValueError,
    ) as exc:
        if row["header_status"] == "ok":
            row.update(_quality_null("error", f"{type(exc).__name__}: {exc}"))
            code = "pixel_decode_failed"
        else:
            row["header_error"] = f"{type(exc).__name__}: {exc}"
            code = "image_header_failed"
        issues.append(ImageProfileIssue("error", code, source.source_key, str(exc)))
    return row, issues


def _assign_anomaly_reasons(rows: list[dict[str, Any]]) -> None:
    readable = [row for row in rows if row["header_status"] == "ok"]
    shape_counts = Counter(str(row["shape_hwc_json"]) for row in readable)
    mode_counts = Counter(str(row["color_mode"]) for row in readable)
    for row in rows:
        reasons: list[str] = []
        if row["header_status"] != "ok":
            reasons.append("unreadable_header")
        else:
            if shape_counts[str(row["shape_hwc_json"])] <= 1:
                reasons.append("singleton_shape")
            if mode_counts[str(row["color_mode"])] <= 1:
                reasons.append("singleton_color_mode")
            if row["extension_matches_format"] is False:
                reasons.append("extension_format_mismatch")
        if row["pixel_status"] == "error":
            reasons.append("pixel_decode_error")
        if row["pixel_status"] == "ok":
            if float(row["dark_pixel_fraction"] or 0.0) >= 0.5:
                reasons.append("high_dark_pixel_fraction")
            if float(row["overexposed_pixel_fraction"] or 0.0) >= 0.5:
                reasons.append("high_overexposed_pixel_fraction")
        row["anomaly_reasons_json"] = json.dumps(reasons, separators=(",", ":"))


def _duplicate_evidence(
    rows: list[dict[str, Any]], threshold: int
) -> list[dict[str, Any]]:
    exact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["exact_sha256"]:
            exact[str(row["exact_sha256"])].append(row)
    for digest, group in exact.items():
        if len(group) < 2:
            continue
        group_id = deterministic_id("image_exact_duplicate", {"sha256": digest})
        for row in group:
            row["exact_duplicate_group_id"] = group_id
            row["exact_duplicate_count"] = len(group)
    quality = [row for row in rows if row["perceptual_hash"]]
    quality.sort(key=lambda row: str(row["image_id"]))
    pairs: list[dict[str, Any]] = []
    for left_index, left in enumerate(quality):
        left_hash = int(str(left["perceptual_hash"]), 16)
        for right in quality[left_index + 1 :]:
            distance = (left_hash ^ int(str(right["perceptual_hash"]), 16)).bit_count()
            if distance <= threshold:
                pairs.append(
                    {
                        "schema_version": IMAGE_PROFILE_SCHEMA_VERSION,
                        "left_image_id": left["image_id"],
                        "right_image_id": right["image_id"],
                        "hamming_distance": distance,
                        "threshold": threshold,
                        "algorithm": "dhash64-v1",
                        "interpretation": "candidate_evidence_not_duplicate_proof",
                    }
                )
    return pairs


def profile_image_sources(
    sources: Sequence[ImageSource],
    *,
    adapter: BaseDatasetAdapter,
    options: ImageProfileOptions,
    discovered_source_count: int | None = None,
    limited: bool = False,
) -> ImageProfileResult:
    started = time.monotonic()
    quality_ids = select_quality_source_ids(
        sources, mode=options.mode, sample_size=options.sample_size, seed=options.seed
    )
    rows: list[dict[str, Any]] = []
    issues: list[ImageProfileIssue] = []
    source_map: dict[str, ImageSource] = {}
    for source in sources:
        row, found = _profile_one(
            source,
            adapter=adapter,
            options=options,
            quality_selected=source.source_member_id in quality_ids,
        )
        rows.append(row)
        issues.extend(found)
        source_map[str(row["image_id"])] = source
    _assign_anomaly_reasons(rows)
    pairs = _duplicate_evidence(rows, options.near_duplicate_hamming)
    return ImageProfileResult(
        images=rows,
        near_duplicate_pairs=pairs,
        issues=issues,
        sources_by_image_id=source_map,
        mode=options.mode,
        discovered_source_count=(
            len(sources) if discovered_source_count is None else discovered_source_count
        ),
        selected_source_count=len(sources),
        quality_selected_count=len(quality_ids),
        limited=limited,
        elapsed_seconds=time.monotonic() - started,
    )


def build_image_schema(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    readable = [row for row in rows if row["header_status"] == "ok"]
    return {
        "schema_version": IMAGE_PROFILE_SCHEMA_VERSION,
        "shape_hwc_counts": dict(
            sorted(Counter(str(row["shape_hwc_json"]) for row in readable).items())
        ),
        "mode_counts": dict(
            sorted(Counter(str(row["color_mode"]) for row in readable).items())
        ),
        "dtype_counts": dict(
            sorted(Counter(str(row["dtype"]) for row in readable).items())
        ),
        "bit_depth_counts": dict(
            sorted(Counter(str(row["bit_depth"]) for row in readable).items())
        ),
        "format_counts": dict(
            sorted(Counter(str(row["file_format"]) for row in readable).items())
        ),
    }


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _summary_markdown(summary: Mapping[str, Any]) -> str:
    return (
        "\n".join(
            [
                "# Gear-tooth image structure and quality profile",
                "",
                f"Mode: `{summary['mode']}`",
                "",
                "## Coverage",
                "",
                f"- Profiled images: {summary['profiled_image_count']}",
                f"- Readable headers: {summary['readable_header_count']}",
                f"- Unreadable headers: {summary['unreadable_header_count']}",
                f"- Pixel-quality coverage: {summary['pixel_quality_success_count']} / {summary['profiled_image_count']}",
                f"- Images by experiment: `{json.dumps(summary['counts_by_experiment'], sort_keys=True)}`",
                f"- Inspection groups: {len(summary['counts_by_inspection'])}",
                "",
                "## Structure",
                "",
                f"- H × W × C shapes: `{json.dumps(summary['shape_counts_hwc'], sort_keys=True)}`",
                f"- Pillow modes: `{json.dumps(summary['mode_counts'], sort_keys=True)}`",
                f"- Dtypes: `{json.dumps(summary['dtype_counts'], sort_keys=True)}`",
                f"- Bit depths: `{json.dumps(summary['bit_depth_counts'], sort_keys=True)}`",
                f"- Formats: `{json.dumps(summary['format_counts'], sort_keys=True)}`",
                f"- Aspect ratios: `{json.dumps(summary['aspect_ratio_counts'], sort_keys=True)}`",
                f"- Unusual singleton shapes or modes: {summary['unusual_shape_or_mode_count']}",
                "",
                "## Annotations and duplicate evidence",
                "",
                f"- Annotation evidence: `{json.dumps(summary['annotation_status_counts'], sort_keys=True)}`",
                f"- Discovered annotation types: `{json.dumps(summary['annotation_type_counts'], sort_keys=True)}`",
                f"- Exact-hash coverage: {summary['exact_hash_covered_count']} / {summary['profiled_image_count']}",
                f"- Exact duplicate groups within hash-covered rows: {summary['exact_duplicate_group_count']}",
                f"- Perceptual-hash coverage: {summary['perceptual_hash_covered_count']} / {summary['profiled_image_count']}",
                f"- Perceptual near-duplicate candidate pairs: {summary['near_duplicate_pair_count']}",
                "",
                "## Timestamp evidence",
                "",
                f"- Status counts: `{json.dumps(summary['timestamp_status_counts'], sort_keys=True)}`",
                "- Local-naive camera filename timestamps are retained as timezone-unknown; they are not coerced to UTC.",
                "",
                "## Limitations",
                "",
                "- Header success does not prove that the complete pixel stream is readable.",
                "- Sampled quality metrics cover only a deterministic archive-stratified subset.",
                "- Brightness, darkness, overexposure, and Laplacian variance are acquisition-quality proxies, not damage labels.",
                "- CRC32/size, SHA-256, and dHash evidence have distinct coverage and must not be conflated.",
                "- No discovered sidecar annotation means none was found in the D1.1 archive listing; it is not a claim about undocumented external labels.",
            ]
        )
        + "\n"
    )


def _contact_sheet(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    result: ImageProfileResult,
    *,
    adapter: BaseDatasetAdapter,
    options: ImageProfileOptions,
    title: str,
    maximum: int = 24,
) -> list[dict[str, Any]]:
    selected = list(rows)[:maximum]
    cell_w, cell_h, label_h, columns = 240, 150, 42, 4
    rows_count = max(1, math.ceil(len(selected) / columns))
    canvas = Image.new(
        "RGB", (columns * cell_w, rows_count * (cell_h + label_h) + 30), "white"
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), title, fill="black")
    index_rows: list[dict[str, Any]] = []
    for index, row in enumerate(selected):
        image_id = str(row["image_id"])
        source = result.sources_by_image_id[image_id]
        x = (index % columns) * cell_w
        y = 30 + (index // columns) * (cell_h + label_h)
        status = "ok"
        try:
            with materialize_image_source(source, options=options) as source_path:
                with Image.open(source_path) as image:
                    preview = ImageOps.exif_transpose(image).convert("RGB")
                    preview.thumbnail(
                        (cell_w - 8, cell_h - 8), Image.Resampling.LANCZOS
                    )
                    canvas.paste(
                        preview,
                        (
                            x + (cell_w - preview.width) // 2,
                            y + (cell_h - preview.height) // 2,
                        ),
                    )
        except (
            OSError,
            RuntimeError,
            ValueError,
            UnidentifiedImageError,
            ArchiveMaterializationError,
        ) as exc:
            status = f"error:{type(exc).__name__}"
        label = (
            f"{row['experiment']} {row['inspection_stage']} T{row['tooth_id'] or '?'}"
        )
        draw.text((x + 4, y + cell_h + 2), label[:36], fill="black")
        draw.text((x + 4, y + cell_h + 18), image_id[-12:], fill="black")
        index_rows.append(
            {
                "sheet": path.name,
                "tile_index": index,
                "image_id": image_id,
                "source_relative_path": row["source_relative_path"],
                "preview_status": status,
            }
        )
    canvas.save(path, format="PNG")
    return index_rows


def _write_shape_figure(path: Path, summary: Mapping[str, Any]) -> None:
    import matplotlib.pyplot as plt

    values = list(summary["shape_counts_hwc"].items())
    figure, axis = plt.subplots(figsize=(8, max(3, 0.45 * len(values))))
    axis.barh([name for name, _ in values], [count for _, count in values])
    axis.set_xlabel("Images")
    axis.set_ylabel("H × W × C")
    axis.set_title("Image shape distribution")
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def write_image_run(
    result: ImageProfileResult,
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
    adapter: BaseDatasetAdapter,
    options: ImageProfileOptions,
) -> list[ArtifactRecord]:
    run.create_layout()
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    inputs_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        [
            run.artifact(config_path, role="resolved_configuration"),
            run.artifact(inputs_path, role="input_manifest"),
        ]
    )
    profile_csv = run.run_directory / "tables/image_profile.csv"
    profile_parquet = run.run_directory / "tables/image_profile.parquet"
    pairs_csv = run.run_directory / "tables/image_near_duplicate_pairs.csv"
    pairs_parquet = run.run_directory / "tables/image_near_duplicate_pairs.parquet"
    _write_csv(profile_csv, result.images)
    pd.DataFrame(result.images).to_parquet(profile_parquet, index=False)
    _write_csv(pairs_csv, result.near_duplicate_pairs)
    pd.DataFrame(result.near_duplicate_pairs).to_parquet(pairs_parquet, index=False)
    schema = build_image_schema(result.images)
    schema_path = run.run_directory / "reports/image_schema.json"
    schema_path.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = result.summary()
    summary_json = run.run_directory / "reports/image_summary.json"
    summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary_md = run.run_directory / "reports/image_summary.md"
    summary_md.write_text(_summary_markdown(summary), encoding="utf-8")
    warnings_path = run.run_directory / "reports/warnings.json"
    warnings_path.write_text(
        json.dumps(
            {
                "schema_version": IMAGE_PROFILE_SCHEMA_VERSION,
                "issues": [asdict(issue) for issue in result.issues],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    readable = [row for row in result.images if row["header_status"] == "ok"]
    representatives = sorted(
        readable,
        key=lambda row: (
            _stable_rank(options.seed, str(row["image_id"])),
            str(row["image_id"]),
        ),
    )
    quality = [row for row in readable if row["pixel_status"] == "ok"]
    anomalies = sorted(
        quality,
        key=lambda row: (
            -(
                float(row["dark_pixel_fraction"] or 0)
                + float(row["overexposed_pixel_fraction"] or 0)
            ),
            float(row["blur_laplacian_variance"] or 0),
            str(row["image_id"]),
        ),
    )
    representative_path = run.run_directory / "figures/contact_sheet_representative.png"
    anomaly_path = run.run_directory / "figures/contact_sheet_quality_outliers.png"
    contact_index = _contact_sheet(
        representative_path,
        representatives,
        result,
        adapter=adapter,
        options=options,
        title="Deterministic representative images",
    )
    contact_index += _contact_sheet(
        anomaly_path,
        anomalies,
        result,
        adapter=adapter,
        options=options,
        title="Quality-metric outliers (not damage labels)",
    )
    contact_index_path = run.run_directory / "tables/contact_sheet_index.csv"
    _write_csv(contact_index_path, contact_index)
    shape_figure = run.run_directory / "figures/image_shape_distribution.png"
    _write_shape_figure(shape_figure, summary)
    for path, role in (
        (profile_csv, "image_profile_csv"),
        (profile_parquet, "image_profile_parquet"),
        (pairs_csv, "near_duplicate_pairs_csv"),
        (pairs_parquet, "near_duplicate_pairs_parquet"),
        (contact_index_path, "contact_sheet_index"),
        (schema_path, "image_schema"),
        (summary_json, "image_summary_json"),
        (summary_md, "image_summary_markdown"),
        (warnings_path, "warnings"),
        (representative_path, "representative_contact_sheet"),
        (anomaly_path, "quality_outlier_contact_sheet"),
        (shape_figure, "image_shape_distribution"),
    ):
        artifacts.append(run.artifact(path, role=role))
    provenance_path = run.write_provenance(artifacts)
    with_provenance = [*artifacts, run.artifact(provenance_path, role="run_provenance")]
    run.write_output_manifest(with_provenance)
    return with_provenance
