"""Evidence-preserving T2.1 target audit and blocker visualizations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

from ..utils.provenance import ArtifactRecord, RunContext
from .common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
    write_csv,
)

SCHEMA_VERSION = "1.0.0"
BLOCKED = "BLOCKED_REQUIRES_PROFESSOR_OR_PROVIDER_DECISION"


@dataclass(frozen=True, slots=True)
class TargetAuditResult:
    candidates: tuple[dict[str, Any], ...]
    blockers: Mapping[str, Any]
    candidate_markdown: str
    definition_markdown: str
    figure_sources: Mapping[str, list[dict[str, Any]]]
    source_index: tuple[dict[str, Any], ...]
    summary: Mapping[str, Any]


def _source_fields(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_run_id": source.get("source_run_id"),
        "source_artifact_path": source.get("artifact_path"),
        "source_artifact_sha256": source.get("artifact_sha256"),
    }


def _match_paths(frame: pd.DataFrame, patterns: Sequence[str]) -> pd.DataFrame:
    if not patterns:
        return frame.iloc[0:0]
    selected = (
        frame["hdf5_path"]
        .astype(str)
        .map(lambda value: any(fnmatchcase(value, pattern) for pattern in patterns))
    )
    return frame[selected]


def _candidate_row(
    definition: Mapping[str, Any],
    sensors: pd.DataFrame,
    images: pd.DataFrame,
    source: Mapping[str, Any],
) -> dict[str, Any]:
    patterns = tuple(str(value) for value in definition.get("source_patterns", ()))
    matched = _match_paths(sensors, patterns)
    units = sorted(
        {
            str(value)
            for value in matched["unit"].dropna().tolist()
            if str(value).strip()
        }
    )
    rates = sorted(
        {
            float(value)
            for value in pd.to_numeric(
                matched["sampling_rate_hz"], errors="coerce"
            ).dropna()
        }
    )
    source_established = bool(patterns and not matched.empty)
    type_established = str(definition["candidate_type"]) not in {
        "continuous_unknown",
        "continuous_or_ordinal_unknown",
    }
    meaning_established = definition["candidate_id"] in {
        "operating_context",
        "oil_particle_counts",
        "lifecycle_identity",
        "image_quality_proxy",
    }
    unit_established = str(definition["unit"]) not in {
        "unknown",
        "mixed_or_unknown",
        "g_or_unknown_by_path",
    }
    dimensions = {
        "meaning": meaning_established,
        "unit": unit_established,
        "source": source_established,
        "type": type_established,
        "target_time": False,
        "six_hour_meaning": False,
        "image_pairing": False,
        "inference_availability": False,
        "leakage_boundary": False,
    }
    completeness = sum(dimensions.values()) / len(dimensions)
    invalid_proxy = definition["candidate_id"] in {
        "operating_context",
        "lifecycle_identity",
        "image_quality_proxy",
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": definition["candidate_id"],
        "variable_name": definition["variable_name"],
        "physical_meaning": definition["physical_meaning"],
        "unit": definition["unit"],
        "candidate_type": definition["candidate_type"],
        "exact_source_paths": json.dumps(patterns, separators=(",", ":")),
        "observed_profile_paths": json.dumps(
            sorted(matched["hdf5_path"].astype(str).unique().tolist()),
            separators=(",", ":"),
        ),
        "observed_dataset_rows": int(len(matched)),
        "observed_hdf5_member_count": int(matched["hdf5_member_id"].nunique()),
        "observed_units": json.dumps(units, separators=(",", ":")),
        "observed_sampling_rates_hz": json.dumps(rates, separators=(",", ":")),
        "timestamp_or_pairing_identifier": "NONE_AUTHORIZED_FOR_IMAGE_TARGET_PAIRING",
        "cadence": "UNKNOWN_AS_TARGET; recorded sensor rates are not target cadence",
        "directly_measured_or_derived": definition["direct_or_derived"],
        "missingness": "UNKNOWN_METADATA_ONLY_NO_TARGET_VALUES",
        "inference_time_availability": definition["inference_availability"],
        "image_pairing_feasibility": "NOT_COMPUTABLE_CLOCK_DOMAIN_UNVERIFIED",
        "verified_image_pair_count": 0,
        "profiled_image_count": int(len(images)),
        "leakage_risk": (
            "INVALID_PROXY_AS_TARGET"
            if invalid_proxy
            else "HIGH_IF_CANDIDATE_IS_ALSO_AVAILABLE_AS_INPUT_OR_SELECTED_POST_HOC"
        ),
        "supporting_evidence": definition["supporting_evidence"],
        "contradicting_evidence": definition["contradicting_evidence"],
        "meaning_evidence_complete": meaning_established,
        "unit_evidence_complete": unit_established,
        "source_evidence_complete": source_established,
        "type_evidence_complete": type_established,
        "target_time_evidence_complete": False,
        "six_hour_evidence_complete": False,
        "image_pairing_evidence_complete": False,
        "inference_availability_evidence_complete": False,
        "leakage_boundary_evidence_complete": False,
        "evidence_completeness_fraction": completeness,
        "target_decision": (
            "REJECT_AS_PROXY" if invalid_proxy else "UNRESOLVED_CANDIDATE"
        ),
        **_source_fields(source),
    }


def _candidate_markdown(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# PHM target candidates",
        "",
        f"Decision: **{BLOCKED}**",
        "",
        "No candidate satisfies the target pass criteria. Condition indicators remain diagnostic candidates; they are not selected automatically.",
        "",
        "| Candidate | Observed source evidence | Meaning/unit | Pairing | Decision |",
        "|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['variable_name']} | {row['observed_dataset_rows']} representative rows | "
            f"{row['physical_meaning']} / {row['unit']} | {row['image_pairing_feasibility']} | {row['target_decision']} |"
        )
    lines.extend(
        [
            "",
            "## Ranked scientific options requiring a decision",
            "",
            "1. Obtain an authoritative quantitative tooth-damage measurement and image/inspection pairing key.",
            "2. If a named condition indicator is intended, obtain its formula, unit, timestamp semantics, inference availability, six-hour rule, and image association from the professor/provider.",
            "3. If RUL is intended, obtain the failure criterion and authoritative RUL construction.",
            "",
            "Experiment/run/stage, operating context, and image-quality measures are explicitly rejected as convenient proxy targets.",
        ]
    )
    return "\n".join(lines) + "\n"


def _definition_markdown(blockers: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# PHM target definition",
            "",
            f"Status: **{BLOCKED}**",
            "",
            "No `TargetRecord`, target computation, transformed target, sample manifest, split, regression metric, or regression model is authorized.",
            "",
            "## Unresolved contract",
            "",
            "- Exact target: UNKNOWN",
            "- Physical meaning and unit: UNKNOWN",
            "- Target type: UNKNOWN",
            "- Current-state versus future prediction: UNKNOWN",
            "- Six-hour interpretation: UNKNOWN (cadence, input history, forecast horizon, or another meaning)",
            "- Image-to-target pairing rule: UNKNOWN",
            "- Prediction horizon and input cutoff: UNKNOWN",
            "- Target scaling/inverse scaling: NOT APPLICABLE UNTIL TARGET APPROVAL",
            "- Inference-time target availability: UNKNOWN",
            "- Leakage boundary: UNKNOWN",
            "",
            "## Evidence boundary",
            "",
            "D1.4 found zero verified UTC image timestamps, so local-naive image timestamps remain unconverted and no temporal image–sensor/target join is authorized. No authoritative local/provider specification defining the scalar or six-hour statement was found in the repository evidence reviewed for T2.1.",
            "",
            "## Required decisions",
            "",
            *[
                f"{index}. {question}"
                for index, question in enumerate(blockers["questions"], 1)
            ],
            "",
        ]
    )


def build_target_audit(
    *,
    sensors: pd.DataFrame,
    images: pd.DataFrame,
    alignment_blockers: Mapping[str, Any],
    candidate_definitions: Sequence[Mapping[str, Any]],
    sources: Mapping[str, Mapping[str, Any]],
) -> TargetAuditResult:
    rows = tuple(
        _candidate_row(definition, sensors, images, sources["sensor_profile"])
        for definition in candidate_definitions
    )
    questions = (
        "What exact scalar should be predicted, with physical meaning and unit?",
        "Is the task current-state estimation, six-hour-ahead forecasting, or another horizon?",
        "Does six hours mean observation cadence, input history, forecast horizon, or something else?",
        "What authoritative identifier or clock rule pairs each image/inspection with the target?",
        "Would the target and all target-construction inputs exist at real inference time?",
        "If a CI is selected, what formula/version produces it and which input channels must be excluded to prevent tautological leakage?",
        "Are quantitative tooth-damage labels, RUL values, or external annotations supplied outside the reviewed archives?",
    )
    blockers = {
        "schema_version": SCHEMA_VERSION,
        "classification": BLOCKED,
        "pass_criteria_met": False,
        "exact_target": "UNKNOWN",
        "regression_valid": False,
        "six_hour_interpretation": "UNKNOWN",
        "prediction_mode": "UNKNOWN",
        "image_target_pairing_rule": "UNKNOWN",
        "prediction_horizon": "UNKNOWN",
        "input_cutoff": "UNKNOWN",
        "target_scaling": "NOT_APPLICABLE_UNTIL_TARGET_APPROVAL",
        "inference_time_availability": "UNKNOWN",
        "leakage_boundary": "UNKNOWN",
        "candidate_count": len(rows),
        "verified_image_utc_count": int(
            alignment_blockers["image_clock_audit"]["verified_utc_images"]
        ),
        "candidate_scalar_target_count_from_d1_4": 0,
        "t2_2_authorized": False,
        "t2_3_authorized": False,
        "rtdetr_regression_authorized": False,
        "questions": list(questions),
    }
    comparison_rows = []
    completeness_rows = []
    missingness_rows = []
    availability_rows = []
    pairing_rows = []
    dimensions = (
        "meaning",
        "unit",
        "source",
        "type",
        "target_time",
        "six_hour",
        "image_pairing",
        "inference_availability",
        "leakage_boundary",
    )
    for row in rows:
        for dimension in dimensions:
            key = f"{dimension}_evidence_complete"
            comparison_rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "dimension": dimension,
                    "complete": bool(row[key]),
                }
            )
        completeness_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "evidence_completeness_fraction": row["evidence_completeness_fraction"],
            }
        )
        missingness_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "observed_dataset_rows": row["observed_dataset_rows"],
                "value_missingness_fraction": None,
                "missingness_status": row["missingness"],
            }
        )
        availability_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "availability": row["inference_time_availability"],
                "verified_available_as_target": False,
            }
        )
        pairing_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "verified_image_pairs": 0,
                "profiled_images": len(images),
                "pairing_status": row["image_pairing_feasibility"],
            }
        )
    figure_sources = {
        "candidate_target_comparison_matrix": comparison_rows,
        "candidate_evidence_completeness": completeness_rows,
        "candidate_missingness": missingness_rows,
        "candidate_inference_availability": availability_rows,
        "candidate_image_pairing_coverage": pairing_rows,
        "six_hour_interpretation_decision": [
            {"option": option, "evidence_status": "UNRESOLVED", "selected": False}
            for option in (
                "observation cadence",
                "input history",
                "forecast horizon",
                "another meaning",
            )
        ],
    }
    source_index = tuple(
        {
            "schema_version": SCHEMA_VERSION,
            "source_name": name,
            **_source_fields(source),
        }
        for name, source in sorted(sources.items())
    )
    summary = {
        "schema_version": SCHEMA_VERSION,
        "classification": BLOCKED,
        "candidate_count": len(rows),
        "target_records_created": 0,
        "sample_records_created": 0,
        "regression_authorized": False,
        "raw_archives_opened": False,
    }
    return TargetAuditResult(
        candidates=rows,
        blockers=blockers,
        candidate_markdown=_candidate_markdown(rows),
        definition_markdown=_definition_markdown(blockers),
        figure_sources=figure_sources,
        source_index=source_index,
        summary=summary,
    )


def _comparison_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    frame = pd.DataFrame(rows)
    candidates = frame["candidate_id"].drop_duplicates().tolist()
    dimensions = frame["dimension"].drop_duplicates().tolist()
    matrix = (
        frame.pivot(index="candidate_id", columns="dimension", values="complete")
        .reindex(index=candidates, columns=dimensions)
        .astype(float)
    )
    figure, axis = plt.subplots(figsize=(12, 7))
    axis.imshow(matrix, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    axis.set_xticks(range(len(dimensions)), dimensions, rotation=35, ha="right")
    axis.set_yticks(range(len(candidates)), candidates)
    axis.set_title("Candidate-target evidence matrix (1 = established, 0 = unresolved)")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            axis.text(
                column,
                row,
                str(int(matrix.iloc[row, column])),
                ha="center",
                va="center",
                color="white" if matrix.iloc[row, column] else "#333333",
            )
    figure.tight_layout()
    return figure


def _completeness_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    frame = pd.DataFrame(rows).sort_values("evidence_completeness_fraction")
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.barh(
        frame["candidate_id"],
        frame["evidence_completeness_fraction"] * 100,
        color=ACADEMIC_COLORS[0],
    )
    axis.set_xlim(0, 100)
    axis.set_xlabel("Pass-criterion evidence established (%)")
    axis.set_title("Target-candidate evidence completeness")
    figure.tight_layout()
    return figure


def _status_figure(
    rows: Sequence[Mapping[str, Any]], *, title: str, status_column: str
) -> plt.Figure:
    frame = pd.DataFrame(rows)
    figure, axis = plt.subplots(figsize=(11, 6))
    axis.barh(frame["candidate_id"], np.zeros(len(frame)), color=ACADEMIC_COLORS[4])
    axis.set_xlim(0, 1)
    axis.set_xticks([])
    axis.set_title(title)
    for index, row in frame.reset_index(drop=True).iterrows():
        axis.text(0.02, index, str(row[status_column]), va="center", fontsize=8.5)
    axis.grid(False)
    figure.tight_layout()
    return figure


def _pairing_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    frame = pd.DataFrame(rows)
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.barh(
        frame["candidate_id"], frame["verified_image_pairs"], color=ACADEMIC_COLORS[4]
    )
    axis.set_xlabel("Verified image–target pairs")
    axis.set_title("Candidate image-pairing coverage: zero authorized pairs")
    axis.set_xlim(0, 1)
    for index in range(len(frame)):
        axis.text(
            0.02,
            index,
            "0 / 1,311 — clock/pairing rule unresolved",
            va="center",
            fontsize=8.5,
        )
    figure.tight_layout()
    return figure


def _six_hour_figure(rows: Sequence[Mapping[str, Any]]) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(11, 4))
    axis.axis("off")
    axis.text(
        0.5,
        0.86,
        "What does ‘six hours’ mean?",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        transform=axis.transAxes,
    )
    for index, row in enumerate(rows):
        x = 0.03 + index * 0.245
        patch = FancyBboxPatch(
            (x, 0.35),
            0.21,
            0.27,
            boxstyle="round,pad=0.015",
            facecolor="#F7D7DC",
            edgecolor=ACADEMIC_COLORS[4],
            transform=axis.transAxes,
        )
        axis.add_patch(patch)
        axis.text(
            x + 0.105,
            0.49,
            row["option"],
            ha="center",
            va="center",
            fontsize=10,
            transform=axis.transAxes,
        )
        axis.text(
            x + 0.105,
            0.40,
            "UNRESOLVED",
            ha="center",
            va="center",
            fontsize=8,
            transform=axis.transAxes,
        )
    axis.text(
        0.5,
        0.14,
        "No observed/authoritative evidence selects an interpretation; no horizon or cadence is inferred.",
        ha="center",
        fontsize=9.5,
        transform=axis.transAxes,
    )
    return figure


def _figure_index() -> str:
    names = (
        "candidate_target_comparison_matrix",
        "candidate_evidence_completeness",
        "candidate_missingness",
        "candidate_inference_availability",
        "candidate_image_pairing_coverage",
        "six_hour_interpretation_decision",
    )
    lines = [
        "# T2.1 target-audit figure index",
        "",
        f"Status: **{BLOCKED}**",
        "",
        "No figure presents a candidate as the approved target.",
        "",
    ]
    for name in names:
        lines.extend(
            [
                f"## `{name}`",
                "",
                f"Source: `tables/{name}.csv`",
                f"Figures: `figures/{name}.png`, `figures/{name}.svg`",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def write_target_audit_run(
    result: TargetAuditResult,
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
    run.create_layout()
    apply_academic_style()
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    input_path = run.write_input_manifest(input_manifest)
    artifacts.extend(
        [
            run.artifact(config_path, role="resolved_configuration"),
            run.artifact(input_path, role="input_manifest"),
        ]
    )
    audit_path = run.run_directory / "tables/target_audit.csv"
    write_csv(audit_path, result.candidates)
    artifacts.append(run.artifact(audit_path, role="target_audit"))
    for name, rows in result.figure_sources.items():
        path = run.run_directory / f"tables/{name}.csv"
        write_csv(path, rows)
        artifacts.append(run.artifact(path, role=f"{name}_source_csv"))
    source_path = run.run_directory / "tables/artifact_source_index.csv"
    write_csv(source_path, result.source_index)
    artifacts.append(run.artifact(source_path, role="artifact_source_index"))
    reports = {
        "target_candidates.md": result.candidate_markdown,
        "target_definition.md": result.definition_markdown,
        "target_figure_index.md": _figure_index(),
    }
    for name, content in reports.items():
        path = run.run_directory / f"reports/{name}"
        path.write_text(content, encoding="utf-8")
        artifacts.append(run.artifact(path, role=name.removesuffix(".md")))
    blockers_path = run.run_directory / "reports/target_blockers.json"
    blockers_path.write_text(json_text(dict(result.blockers)), encoding="utf-8")
    summary_path = run.run_directory / "reports/target_audit_summary.json"
    summary_path.write_text(json_text(dict(result.summary)), encoding="utf-8")
    artifacts.extend(
        [
            run.artifact(blockers_path, role="target_blockers"),
            run.artifact(summary_path, role="target_audit_summary"),
        ]
    )
    figures = {
        "candidate_target_comparison_matrix": _comparison_figure(
            result.figure_sources["candidate_target_comparison_matrix"]
        ),
        "candidate_evidence_completeness": _completeness_figure(
            result.figure_sources["candidate_evidence_completeness"]
        ),
        "candidate_missingness": _status_figure(
            result.figure_sources["candidate_missingness"],
            title="Candidate missingness evidence",
            status_column="missingness_status",
        ),
        "candidate_inference_availability": _status_figure(
            result.figure_sources["candidate_inference_availability"],
            title="Candidate availability at real inference time",
            status_column="availability",
        ),
        "candidate_image_pairing_coverage": _pairing_figure(
            result.figure_sources["candidate_image_pairing_coverage"]
        ),
        "six_hour_interpretation_decision": _six_hour_figure(
            result.figure_sources["six_hour_interpretation_decision"]
        ),
    }
    for name, figure in figures.items():
        for path in save_figure_pair(figure, run.run_directory / f"figures/{name}"):
            artifacts.append(run.artifact(path, role=f"{name}_{path.suffix[1:]}"))
    return finalize_run(run, artifacts)
