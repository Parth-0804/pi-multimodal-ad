from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

import numpy as np
import pandas as pd
from PIL import Image

from pi_multimodal_ad.datasets.base import (
    AssetIdentity,
    BaseDatasetAdapter,
    ImageSourceIdentity,
)
from pi_multimodal_ad.profiling.images import (
    ImageProfileOptions,
    ImageSource,
    build_image_schema,
    profile_image_sources,
    select_quality_source_ids,
    write_image_run,
)
from pi_multimodal_ad.utils import create_run_context, load_yaml_config

UTC = timezone.utc


class _SyntheticImageAdapter(BaseDatasetAdapter):
    """Small dataset-neutral adapter used only for generated image fixtures."""

    dataset_name = "synthetic_images"

    def normalize_experiment(self, value: str) -> str:
        return value.upper().replace("_", "-").replace(" ", "-")

    def parse_run(self, value: str) -> int | None:
        match = re.search(r"run[-_ ]?(\d+)", value, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def parse_asset_identity(
        self,
        relative_path: str | PurePosixPath,
        *,
        archive_member: str | None = None,
    ) -> AssetIdentity:
        path = PurePosixPath(relative_path)
        return AssetIdentity(
            relative_path=path,
            modality="image",
            experiment="EXP-A",
            run=self.parse_run(path.as_posix()),
            asset_kind="archive_member" if archive_member else "file",
            archive_member=(
                PurePosixPath(archive_member) if archive_member is not None else None
            ),
        )

    def sensor_path_aliases(self, channel_role: str) -> tuple[str, ...]:
        return ()

    def asset_naming_pattern(self, relative_path: str | PurePosixPath) -> str:
        return "synthetic"

    def parse_image_identity(
        self,
        relative_path: str | PurePosixPath,
        *,
        archive_member: str | None = None,
    ) -> ImageSourceIdentity:
        member = archive_member or PurePosixPath(relative_path).name
        tooth_match = re.search(r"tooth[-_ ]?0*(\d+)", member, re.IGNORECASE)
        sequence_match = re.search(
            r"(?:view|image)[-_ ]?0*(\d+)", member, re.IGNORECASE
        )
        tooth_id = str(int(tooth_match.group(1))) if tooth_match else None
        sequence_id = (
            str(int(sequence_match.group(1))) if sequence_match is not None else None
        )
        run = self.parse_run(str(relative_path))
        return ImageSourceIdentity(
            experiment="EXP-A",
            run=run,
            raw_inspection_stage="Run-1" if run is not None else None,
            inspection_stage="run" if run is not None else "unclassified",
            inspection_id=f"EXP-A:{'run-' + str(run) if run else 'unclassified'}",
            inspection_id_source="synthetic_filename_parser",
            tooth_id=tooth_id,
            image_role="canonical_tooth" if tooth_id is not None else "unknown",
            sequence_id=sequence_id,
            raw_sequence_token=(
                sequence_match.group(0) if sequence_match is not None else None
            ),
            timestamp_utc=None,
            timestamp_local_naive=None,
            timestamp_raw=None,
            timestamp_source=None,
            timestamp_status="missing",
            timestamp_clock_domain=None,
            timestamp_evidence=None,
            internal_run_token=None,
            internal_run_conflict=None,
            internal_run_parse_error=None,
        )


def _rgb_png(width: int, height: int, *, offset: int = 0) -> bytes:
    y, x = np.indices((height, width))
    array = np.stack(
        (
            (x * 17 + offset) % 256,
            (y * 29 + offset * 3) % 256,
            ((x + y) * 11 + offset * 5) % 256,
        ),
        axis=-1,
    ).astype(np.uint8)
    output = BytesIO()
    Image.fromarray(array, mode="RGB").save(output, format="PNG")
    return output.getvalue()


def _grayscale_png(width: int, height: int) -> bytes:
    array = np.arange(width * height, dtype=np.uint8).reshape(height, width)
    output = BytesIO()
    Image.fromarray(array, mode="L").save(output, format="PNG")
    return output.getvalue()


def _rgb_jpeg(width: int, height: int, *, offset: int = 0) -> bytes:
    y, x = np.indices((height, width))
    array = np.stack(
        (
            (x * 17 + offset) % 256,
            (y * 29 + offset * 3) % 256,
            ((x + y) * 11 + offset * 5) % 256,
        ),
        axis=-1,
    ).astype(np.uint8)
    output = BytesIO()
    Image.fromarray(array, mode="RGB").save(output, format="JPEG", quality=90)
    return output.getvalue()


def _uint16_png(width: int, height: int) -> bytes:
    array = np.linspace(0, 65535, width * height, dtype=np.uint16).reshape(
        height, width
    )
    output = BytesIO()
    Image.fromarray(array).save(output, format="PNG")
    return output.getvalue()


def _write_image(path: Path, payload: bytes) -> Path:
    path.write_bytes(payload)
    return path


def _file_source(
    path: Path,
    *,
    source_member_id: str | None = None,
    source_relative_path: str | None = None,
    archive_group: str | None = None,
) -> ImageSource:
    return ImageSource(
        source_member_id=source_member_id or f"source_{path.stem}",
        archive_asset_id=f"asset_{path.stem}",
        source_kind="file",
        source_relative_path=source_relative_path or path.name,
        file_path=path,
        archive_path=None,
        archive_relative_path=archive_group,
        outer_member_path=None,
        nested_member_path=None,
        member_occurrence=1,
        nested_member_occurrence=1,
        experiment="EXP-A",
        authoritative_outer_run=1,
        compressed_size_bytes=None,
        encoded_size_bytes=path.stat().st_size,
        crc32=None,
    )


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return output.getvalue()


def _archive_sources(tmp_path: Path) -> tuple[list[ImageSource], Path]:
    direct_member = "Tooth_03_View_02.png"
    nested_container = "camera_bundle.zip"
    nested_member = "unknown_name.png"
    direct_payload = _rgb_png(13, 9, offset=1)
    nested_payload = _grayscale_png(8, 12)
    nested_payload_zip = _zip_bytes({nested_member: nested_payload})
    archive_path = tmp_path / "images.zip"
    archive_path.write_bytes(
        _zip_bytes(
            {
                direct_member: direct_payload,
                nested_container: nested_payload_zip,
            }
        )
    )
    with zipfile.ZipFile(archive_path) as archive:
        direct_info = archive.getinfo(direct_member)
    with zipfile.ZipFile(BytesIO(nested_payload_zip)) as nested_archive:
        nested_info = nested_archive.getinfo(nested_member)
    archive_relative = "photos/EXP-A/Exp-A_Photos_Run-1.zip"
    direct = ImageSource(
        source_member_id="direct_image",
        archive_asset_id="photo_archive",
        source_kind="zip_member",
        source_relative_path=f"{archive_relative}!{direct_member}",
        file_path=None,
        archive_path=archive_path,
        archive_relative_path=archive_relative,
        outer_member_path=direct_member,
        nested_member_path=None,
        member_occurrence=1,
        nested_member_occurrence=1,
        experiment="EXP-A",
        authoritative_outer_run=1,
        compressed_size_bytes=direct_info.compress_size,
        encoded_size_bytes=direct_info.file_size,
        crc32=f"{direct_info.CRC:08x}",
    )
    nested = ImageSource(
        source_member_id="nested_image",
        archive_asset_id="photo_archive",
        source_kind="nested_zip_member",
        source_relative_path=(f"{archive_relative}!{nested_container}!{nested_member}"),
        file_path=None,
        archive_path=archive_path,
        archive_relative_path=archive_relative,
        outer_member_path=nested_container,
        nested_member_path=nested_member,
        member_occurrence=1,
        nested_member_occurrence=1,
        experiment="EXP-A",
        authoritative_outer_run=1,
        compressed_size_bytes=nested_info.compress_size,
        encoded_size_bytes=nested_info.file_size,
        crc32=f"{nested_info.CRC:08x}",
    )
    return [direct, nested], archive_path


def test_header_mode_profiles_rgb_grayscale_resolutions_and_uint16_png(
    tmp_path: Path,
) -> None:
    sources = [
        _file_source(
            _write_image(tmp_path / "Tooth_01_View_01.png", _rgb_png(13, 9)),
            source_member_id="rgb",
        ),
        _file_source(
            _write_image(tmp_path / "gray.png", _grayscale_png(7, 11)),
            source_member_id="gray",
        ),
        _file_source(
            _write_image(tmp_path / "depth16.png", _uint16_png(5, 6)),
            source_member_id="depth16",
        ),
    ]

    result = profile_image_sources(
        sources,
        adapter=_SyntheticImageAdapter(),
        options=ImageProfileOptions(mode="header"),
    )
    rows = {row["source_member_id"]: row for row in result.images}

    assert not result.issues
    assert result.quality_selected_count == 0
    assert (rows["rgb"]["width"], rows["rgb"]["height"]) == (13, 9)
    assert json.loads(rows["rgb"]["shape_hwc_json"]) == [9, 13, 3]
    assert rows["rgb"]["color_mode"] == "RGB"
    assert rows["rgb"]["dtype"] == "uint8"
    assert rows["rgb"]["bit_depth"] == 8
    assert rows["rgb"]["is_grayscale"] is False
    assert json.loads(rows["gray"]["shape_hwc_json"]) == [11, 7, 1]
    assert rows["gray"]["color_mode"] == "L"
    assert rows["gray"]["is_grayscale"] is True
    assert json.loads(rows["depth16"]["shape_hwc_json"]) == [6, 5, 1]
    assert rows["depth16"]["bit_depth"] == 16
    assert rows["depth16"]["dtype"] == "uint16"
    assert rows["depth16"]["is_grayscale"] is True
    assert all(row["file_format"] == "PNG" for row in rows.values())
    assert all(row["extension_matches_format"] is True for row in rows.values())
    assert all(row["pixel_status"] == "not_selected" for row in rows.values())

    schema = build_image_schema(result.images)
    assert schema["shape_hwc_counts"] == {"[11,7,1]": 1, "[6,5,1]": 1, "[9,13,3]": 1}
    assert schema["mode_counts"] == {"I;16": 1, "L": 1, "RGB": 1}


def test_direct_and_nested_zip_members_profile_and_cleanup_temp_files(
    tmp_path: Path,
) -> None:
    sources, _ = _archive_sources(tmp_path)
    temp_root = tmp_path / "temporary"
    temp_root.mkdir()

    result = profile_image_sources(
        sources,
        adapter=_SyntheticImageAdapter(),
        options=ImageProfileOptions(mode="full", temp_root=temp_root),
    )
    rows = {row["source_member_id"]: row for row in result.images}

    assert not result.issues
    assert rows["direct_image"]["header_status"] == "ok"
    assert rows["direct_image"]["pixel_status"] == "ok"
    assert rows["direct_image"]["source_kind"] == "zip_member"
    assert rows["direct_image"]["tooth_id"] == "3"
    assert rows["direct_image"]["sequence_id"] == "2"
    assert rows["nested_image"]["header_status"] == "ok"
    assert rows["nested_image"]["pixel_status"] == "ok"
    assert rows["nested_image"]["source_kind"] == "nested_zip_member"
    assert rows["nested_image"]["nested_archive_member"] == "unknown_name.png"
    assert not list(temp_root.glob("pi_multimodal_archive_*"))


def test_corrupt_header_and_truncated_pixel_stream_are_distinguished_and_continue(
    tmp_path: Path,
) -> None:
    valid_payload = _rgb_jpeg(64, 48, offset=7)
    sources = [
        _file_source(
            _write_image(tmp_path / "corrupt.png", b"not an image"),
            source_member_id="corrupt",
        ),
        _file_source(
            _write_image(tmp_path / "truncated.jpg", valid_payload[:-2]),
            source_member_id="truncated",
        ),
        _file_source(
            _write_image(tmp_path / "valid.jpg", valid_payload),
            source_member_id="valid",
        ),
    ]

    result = profile_image_sources(
        sources,
        adapter=_SyntheticImageAdapter(),
        options=ImageProfileOptions(mode="full"),
    )
    rows = {row["source_member_id"]: row for row in result.images}

    assert rows["corrupt"]["header_status"] == "error"
    assert rows["corrupt"]["header_error"]
    assert rows["truncated"]["header_status"] == "ok"
    assert rows["truncated"]["pixel_status"] == "error"
    assert rows["truncated"]["pixel_error"]
    assert rows["valid"]["header_status"] == "ok"
    assert rows["valid"]["pixel_status"] == "ok"
    assert {issue.code for issue in result.issues} == {
        "image_header_failed",
        "pixel_decode_failed",
    }


def test_full_mode_records_exact_duplicates_and_deterministic_dhash(
    tmp_path: Path,
) -> None:
    payload = _rgb_png(24, 18, offset=9)
    sources = [
        _file_source(
            _write_image(tmp_path / "Tooth_01_View_01.png", payload),
            source_member_id="left",
        ),
        _file_source(
            _write_image(tmp_path / "Tooth_02_View_01.png", payload),
            source_member_id="right",
        ),
    ]
    options = ImageProfileOptions(mode="full", near_duplicate_hamming=0)

    first = profile_image_sources(
        sources, adapter=_SyntheticImageAdapter(), options=options
    )
    repeated = profile_image_sources(
        sources, adapter=_SyntheticImageAdapter(), options=options
    )
    first_rows = {row["source_member_id"]: row for row in first.images}
    repeated_rows = {row["source_member_id"]: row for row in repeated.images}

    assert first_rows["left"]["exact_sha256"] == first_rows["right"]["exact_sha256"]
    assert (
        first_rows["left"]["exact_duplicate_group_id"]
        == first_rows["right"]["exact_duplicate_group_id"]
    )
    assert first_rows["left"]["exact_duplicate_count"] == 2
    assert first_rows["right"]["exact_duplicate_count"] == 2
    assert (
        first_rows["left"]["perceptual_hash"] == first_rows["right"]["perceptual_hash"]
    )
    assert len(first.near_duplicate_pairs) == 1
    assert first.near_duplicate_pairs[0]["hamming_distance"] == 0
    for source_id in first_rows:
        for field in (
            "perceptual_hash",
            "intensity_mean",
            "intensity_std",
            "blur_laplacian_variance",
            "dark_pixel_fraction",
            "overexposed_pixel_fraction",
        ):
            assert first_rows[source_id][field] == repeated_rows[source_id][field]


def test_sampled_quality_selection_is_seeded_bounded_and_reproducible(
    tmp_path: Path,
) -> None:
    sources = []
    for index in range(6):
        path = _write_image(
            tmp_path / f"image_{index}.png", _rgb_png(12, 10, offset=index + 1)
        )
        sources.append(
            _file_source(
                path,
                source_member_id=f"image_{index}",
                source_relative_path=f"group/image_{index}.png",
                archive_group="synthetic/archive.zip",
            )
        )
    options = ImageProfileOptions(mode="sampled", seed=1729, sample_size=2)

    selected = select_quality_source_ids(
        sources, mode=options.mode, sample_size=options.sample_size, seed=options.seed
    )
    repeated_selected = select_quality_source_ids(
        list(reversed(sources)),
        mode=options.mode,
        sample_size=options.sample_size,
        seed=options.seed,
    )
    assert selected == repeated_selected
    assert len(selected) == 2

    first = profile_image_sources(
        sources, adapter=_SyntheticImageAdapter(), options=options
    )
    repeated = profile_image_sources(
        sources, adapter=_SyntheticImageAdapter(), options=options
    )
    assert first.quality_selected_count == 2
    assert {
        row["source_member_id"] for row in first.images if row["pixel_status"] == "ok"
    } == selected
    assert [
        (row["source_member_id"], row["quality_selected"], row["perceptual_hash"])
        for row in first.images
    ] == [
        (row["source_member_id"], row["quality_selected"], row["perceptual_hash"])
        for row in repeated.images
    ]


def test_unknown_filename_preserves_missing_identity_and_annotation_evidence(
    tmp_path: Path,
) -> None:
    source = _file_source(
        _write_image(tmp_path / "mystery.png", _grayscale_png(5, 4)),
        source_member_id="mystery",
        source_relative_path="photos/EXP-A/unclassified/mystery.png",
    )

    result = profile_image_sources(
        [source],
        adapter=_SyntheticImageAdapter(),
        options=ImageProfileOptions(mode="header"),
    )
    row = result.images[0]

    assert row["header_status"] == "ok"
    assert row["inspection_stage"] == "unclassified"
    assert row["tooth_id"] is None
    assert row["image_role"] == "unknown"
    assert row["sequence_id"] is None
    assert row["timestamp_utc"] is None
    assert row["timestamp_local_naive"] is None
    assert row["timestamp_status"] == "missing"
    assert row["annotation_status"] == "none_discovered_in_archive_listing"
    assert json.loads(row["annotation_types_json"]) == []
    assert json.loads(row["annotation_refs_json"]) == []


def test_image_run_writer_keeps_csv_parquet_schema_and_provenance_consistent(
    tmp_path: Path,
) -> None:
    payload = _rgb_png(16, 12, offset=3)
    sources = [
        _file_source(
            _write_image(tmp_path / "Tooth_01_View_01.png", payload),
            source_member_id="writer_left",
        ),
        _file_source(
            _write_image(tmp_path / "Tooth_02_View_01.png", payload),
            source_member_id="writer_right",
        ),
    ]
    adapter = _SyntheticImageAdapter()
    options = ImageProfileOptions(mode="full", seed=17)
    result = profile_image_sources(sources, adapter=adapter, options=options)

    repository = tmp_path / "repository"
    config_path = repository / "configs/experiment.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "schema_version: '1.0.0'\nstudy: synthetic_image_profile\n",
        encoding="utf-8",
    )
    config = load_yaml_config(config_path, repository_root=repository)
    run = create_run_context(
        study="synthetic_image_profile",
        output_root=repository / "runs/synthetic_image_profile",
        config=config,
        seed=17,
        command=("scripts/dataset/profile_images.py", "--mode", "full"),
        input_roots=("tests/synthetic",),
        now=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        package_names=(),
        source_runs=(
            {
                "task": "D1.1",
                "run_id": "synthetic-source-run",
                "artifact_sha256": "0" * 64,
            },
        ),
    )

    artifacts = write_image_run(
        result,
        run=run,
        resolved_config={"schema_version": "1.0.0", "mode": "full"},
        input_manifest=[{"source": "synthetic-only"}],
        adapter=adapter,
        options=options,
    )

    image_csv = pd.read_csv(run.run_directory / "tables/image_profile.csv")
    image_parquet = pd.read_parquet(run.run_directory / "tables/image_profile.parquet")
    assert list(image_csv.columns) == list(image_parquet.columns)
    assert len(image_csv) == len(image_parquet) == 2
    assert image_csv["image_id"].tolist() == image_parquet["image_id"].tolist()
    assert (
        image_csv["shape_hwc_json"].tolist() == image_parquet["shape_hwc_json"].tolist()
    )
    assert image_csv["exact_sha256"].tolist() == image_parquet["exact_sha256"].tolist()
    generated_schema = json.loads(
        (run.run_directory / "reports/image_schema.json").read_text(encoding="utf-8")
    )
    assert generated_schema == build_image_schema(result.images)
    generated_summary = json.loads(
        (run.run_directory / "reports/image_summary.json").read_text(encoding="utf-8")
    )
    assert generated_summary["counts_by_experiment"] == {"EXP-A": 2}
    assert len(generated_summary["counts_by_inspection"]) == 1
    assert generated_summary["aspect_ratio_counts"] == {"1.33333333333": 2}
    assert generated_summary["unusual_shape_or_mode_count"] == 0
    assert generated_summary["exact_hash_covered_count"] == 2
    assert generated_summary["perceptual_hash_covered_count"] == 2
    assert generated_summary["annotation_type_counts"] == {}
    output_manifest = json.loads(
        (run.run_directory / "manifests/outputs.json").read_text(encoding="utf-8")
    )
    roles = {artifact["role"] for artifact in output_manifest["artifacts"]}
    assert {
        "image_profile_csv",
        "image_profile_parquet",
        "near_duplicate_pairs_csv",
        "near_duplicate_pairs_parquet",
        "image_schema",
        "image_summary_markdown",
        "representative_contact_sheet",
        "quality_outlier_contact_sheet",
        "run_provenance",
    } <= roles
    assert len(artifacts) == len(output_manifest["artifacts"])
    provenance = json.loads(
        (run.run_directory / "provenance.json").read_text(encoding="utf-8")
    )
    assert provenance["source_runs"][0]["run_id"] == "synthetic-source-run"
