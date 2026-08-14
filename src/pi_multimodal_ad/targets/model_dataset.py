"""Traceable manifests and experiment-level splits for provisional PHM targets."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
from typing import Any

import pandas as pd

from ..data_contracts.identifiers import deterministic_id
from ..reporting.common import finalize_run, json_text
from ..utils.provenance import ArtifactRecord, RunContext

DATASET_SCHEMA_VERSION = "1.0.0"


def build_sensor_manifests(
    archive_members: pd.DataFrame, run_targets: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    members = archive_members[
        archive_members.member_file_type.eq("hdf5")
        & archive_members.modality.eq("high_frequency")
    ].copy()
    members = members.sort_values(
        ["experiment", "run", "archive_member", "member_id"], kind="stable"
    )
    members["sequence_position_within_run"] = (
        members.groupby(["experiment", "run"]).cumcount() + 1
    )
    sensor = pd.DataFrame(
        {
            "schema_version": DATASET_SCHEMA_VERSION,
            "sensor_file_id": members.member_id,
            "experiment": members.experiment,
            "run": members.run.astype(int),
            "archive_path": members.archive_relative_path,
            "archive_member": members.archive_member,
            "sequence_position_within_run": members.sequence_position_within_run,
            "start_timestamp_utc": None,
            "end_timestamp_utc": None,
            "duration_seconds": 60.0,
            "duration_evidence": "official_challenge_one_hdf5_file_per_minute",
            "available_channel_families": "unknown_without_full_payload_profile",
            "quality_flags": members.member_run_parse_error.fillna("").astype(str),
            "source_hash_algorithm": members.checksum_algorithm,
            "source_hash": members.checksum,
            "source_hash_scope": "zip_member_crc32_not_cryptographic_payload_hash",
            "uncompressed_size_bytes": members.uncompressed_size_bytes,
        }
    )
    run_rows: list[dict[str, Any]] = []
    target_index = run_targets.set_index(["experiment", "run"])
    for (experiment, run), scoped in sensor.groupby(["experiment", "run"]):
        target = target_index.loc[(experiment, run)]
        ordered_ids = scoped.sort_values(
            "sequence_position_within_run"
        ).sensor_file_id.tolist()
        observed = len(ordered_ids)
        run_rows.append(
            {
                "schema_version": DATASET_SCHEMA_VERSION,
                "sensor_run_id": deterministic_id(
                    "sensor_run", {"experiment": experiment, "run": int(run)}
                ),
                "experiment": experiment,
                "run": int(run),
                "expected_nominal_duration_seconds": 21600,
                "observed_duration_seconds": observed * 60,
                "duration_evidence": "one_minute_files_times_observed_count",
                "one_minute_hdf5_count": observed,
                "ordered_sensor_file_ids_json": json.dumps(
                    ordered_ids, separators=(",", ":")
                ),
                "image_inspection_key": f"{experiment}/run-{int(run)}",
                "target_definition_version": target.target_definition_version,
                "raw_top3_mean_pct": target.raw_top3_mean_pct,
                "causal_monotonic_top3_mean_pct": target.causal_monotonic_top3_mean_pct,
                "valid_tooth_count": int(target.valid_tooth_count),
                "target_verification_status": target.target_verification_status,
                "input_cutoff": "end_of_same_run",
                "inclusion_status": target.inclusion_status,
                "exclusion_reason": target.exclusion_reason,
            }
        )
    feature_status = sensor[
        ["sensor_file_id", "experiment", "run", "sequence_position_within_run"]
    ].copy()
    feature_status["feature_extraction_status"] = "not_computed_in_image_baseline_task"
    feature_status["feature_values_available"] = False
    feature_status["reason"] = (
        "full compact feature extraction requires a separate bounded streaming sensor job"
    )
    return sensor, pd.DataFrame(run_rows), feature_status


def build_image_samples(
    image_manifest: pd.DataFrame,
    *,
    split_config: Mapping[str, Sequence[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    images = image_manifest[
        image_manifest.decoding_status.eq("ok") & image_manifest.run.notna()
    ].copy()
    experiment_to_split = {
        experiment: split
        for split, experiments in split_config.items()
        for experiment in experiments
    }
    images["split"] = images.experiment.map(experiment_to_split)
    images["sample_id"] = images.apply(
        lambda row: deterministic_id(
            "image_sample",
            {
                "target_definition_version": row.target_definition_version,
                "image_id": row.image_id,
            },
        ),
        axis=1,
    )
    samples = pd.DataFrame(
        {
            "schema_version": DATASET_SCHEMA_VERSION,
            "sample_id": images.sample_id,
            "image_id": images.image_id,
            "source_member_id": images.source_member_id,
            "image_source": images.archive_path.astype(str)
            + "!"
            + images.archive_member.astype(str),
            "experiment": images.experiment,
            "run": images.run.astype(int),
            "inspection_id": images.inspection_id,
            "tooth_id": images.tooth_id.astype(int),
            "image_type": images.image_type,
            "per_image_damage_candidate_pct": images.damage_candidate_area_pct,
            "target_unit": "percent_visible_flank_candidate_area",
            "target_definition_version": images.target_definition_version,
            "target_verification_status": "provisional_pending_human_review",
            "pairing_evidence": images.pairing_evidence,
            "input_cutoff": "image_captured_after_same_run",
            "near_duplicate_group": images.near_duplicate_group,
            "split_group": images.experiment.astype(str)
            + "/run-"
            + images.run.astype(int).astype(str),
            "split": images.split,
            "inclusion_status": "included_provisional",
            "exclusion_reason": None,
        }
    ).sort_values(["split", "experiment", "run", "tooth_id", "image_id"])
    if samples.split.isna().any():
        raise ValueError("one or more experiments lack a persisted split assignment")
    run_splits = samples.groupby(["experiment", "run"]).split.nunique()
    duplicate_splits = (
        samples.dropna(subset=["near_duplicate_group"])
        .groupby("near_duplicate_group")
        .split.nunique()
    )
    validation = {
        "schema_version": DATASET_SCHEMA_VERSION,
        "valid": bool(
            run_splits.max() == 1
            and (duplicate_splits.max() if len(duplicate_splits) else 1) == 1
        ),
        "sample_count": len(samples),
        "counts_by_split": samples.split.value_counts()
        .sort_index()
        .astype(int)
        .to_dict(),
        "counts_by_experiment": samples.experiment.value_counts()
        .sort_index()
        .astype(int)
        .to_dict(),
        "experiment_run_cross_split_violations": int((run_splits > 1).sum()),
        "near_duplicate_cross_split_violations": int((duplicate_splits > 1).sum()),
        "random_split_used": False,
        "split_policy": "strict_experiment_level",
    }
    split = samples[
        [
            "sample_id",
            "experiment",
            "run",
            "inspection_id",
            "tooth_id",
            "near_duplicate_group",
            "split_group",
            "split",
        ]
    ].copy()
    return samples, split, validation


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv_path, parquet_path = stem.with_suffix(".csv"), stem.with_suffix(".parquet")
    frame.to_csv(csv_path, index=False)
    frame.to_parquet(parquet_path, index=False)
    return [csv_path, parquet_path]


def write_dataset_run(
    tables: Mapping[str, pd.DataFrame],
    *,
    split_validation: Mapping[str, Any],
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    inputs_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        (
            run.artifact(config_path, role="resolved_configuration"),
            run.artifact(inputs_path, role="input_manifest"),
        )
    )
    for name, frame in tables.items():
        for path in _write_frame(frame, run.run_directory / f"tables/{name}"):
            artifacts.append(run.artifact(path, role=name))
    split_path = run.run_directory / "reports/split_validation.json"
    split_path.write_text(json_text(dict(split_validation)), encoding="utf-8")
    artifacts.append(run.artifact(split_path, role="split_validation"))
    sample_contract = """# Sample contract

The RT-DETR engineering sample is one post-run tooth image with its own provisional image-mask area ratio. Multiple views are separate view samples and are aggregated to a tooth with the versioned maximum-view rule; tooth predictions aggregate to a run with the top-3 mean. No run target is repeated across teeth.

Canonical development split: EXP-B train, EXP-A validation, EXP-F untouched test. No run, inspection, tooth group, or near-duplicate group crosses an experiment boundary. No random split is generated inside a loader.

The sensor-file and sensor-run manifests are traceability records. `minute_feature_table` records that compact signal features were not computed in this image-baseline task; it must not be treated as a feature dataset.
"""
    dataset_card = """# Provisional PHM model dataset card

Targets are automated dark/horizontally-textured damage-candidate masks pending human review, not organizer ground truth or calibrated spall area. All 20 run inspections have 28 tooth identities, but EXP-A/B use multiple close-ups for teeth 1–4 whereas EXP-F uses one canonical image per tooth. This acquisition-protocol shift is a major external-validity limitation.

HDF5 members are one-minute source records according to the official challenge description. Duration here is member count × 60 seconds, not a fully verified timestamp span. Full compact sensor features require a separate streaming job and remain unavailable.
"""
    review = tables["model_sample_manifest"][
        [
            "sample_id",
            "experiment",
            "run",
            "tooth_id",
            "image_id",
            "split",
            "target_verification_status",
        ]
    ].copy()
    review["review_status"] = "pending"
    review["reviewer_decision"] = ""
    review["reviewer_notes"] = ""
    review_path = run.run_directory / "tables/human_dataset_review.csv"
    review.to_csv(review_path, index=False)
    artifacts.append(run.artifact(review_path, role="human_dataset_review"))
    for name, text in (
        ("sample_contract.md", sample_contract),
        ("dataset_card.md", dataset_card),
        (
            "HUMAN_DATASET_REVIEW_GUIDE.md",
            "# Human dataset review guide\n\nVerify image/run/tooth identity, provisional target overlay, and persisted split. Reject ambiguous identity or protocol mismatch; never move a row across splits manually.\n",
        ),
    ):
        path = run.run_directory / f"reports/{name}"
        path.write_text(text, encoding="utf-8")
        artifacts.append(run.artifact(path, role=Path(name).stem))
    return finalize_run(run, artifacts)
