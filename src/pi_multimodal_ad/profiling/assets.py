"""Generic file and ZIP-central-directory asset inventory.

ZIP payloads are never extracted, decompressed, or fully hashed here. CRC32 and
sizes come from central-directory metadata and therefore constitute duplicate
evidence, not cryptographic confirmation of payload equality.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from hashlib import sha256
import csv
import fnmatch
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any, Literal
import zipfile

import pandas as pd

from ..data_contracts import ContractValidationError, deterministic_id
from ..datasets import BaseDatasetAdapter
from ..utils.config import ConfigError, ResolvedConfig
from ..utils.provenance import ArtifactRecord, RunContext

INVENTORY_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class InventoryIssue:
    severity: Literal["info", "warning", "error"]
    code: str
    relative_path: str | None
    message: str


@dataclass(frozen=True, slots=True)
class InventoryPlan:
    repository_root: Path
    data_root: Path
    data_root_reference: str
    dataset_name: str
    modality_roots: Mapping[str, tuple[str, ...]]
    experiments: Mapping[str, tuple[int, ...]]
    allowed_extensions: tuple[str, ...]
    excluded_globs: tuple[str, ...]
    expectation_mode_by_modality: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class DiscoveredAsset:
    modality_hint: str
    path: Path
    relative_path: str
    allowed_extension: bool
    size_bytes: int


@dataclass(slots=True)
class InventoryResult:
    archives: list[dict[str, Any]]
    members: list[dict[str, Any]]
    issues: list[InventoryIssue]
    missing_expected: list[dict[str, Any]]
    discovered_count: int
    limited: bool

    def summary(self) -> dict[str, Any]:
        readable = sum(bool(row["readable"]) for row in self.archives)
        archive_rows = [row for row in self.archives if row["file_type"] == "zip"]
        issue_counts = Counter(issue.severity for issue in self.issues)
        by_scope: dict[str, dict[str, int]] = {}
        for row in archive_rows:
            scope_run = row["run"] if row["run"] is not None else "aggregate"
            key = f"{row['experiment']}|{scope_run}|{row['modality']}"
            bucket = by_scope.setdefault(
                key,
                {
                    "archive_count": 0,
                    "size_bytes": 0,
                    "member_count": 0,
                    "uncompressed_member_bytes": 0,
                },
            )
            bucket["archive_count"] += 1
            bucket["size_bytes"] += int(row["size_bytes"])
            bucket["member_count"] += int(row["member_count"] or 0)
            bucket["uncompressed_member_bytes"] += int(
                row["uncompressed_member_bytes"] or 0
            )
        return {
            "schema_version": INVENTORY_SCHEMA_VERSION,
            "discovered_file_count": self.discovered_count,
            "profiled_file_count": len(self.archives),
            "zip_archive_count": len(archive_rows),
            "readable_file_count": readable,
            "unreadable_file_count": len(self.archives) - readable,
            "outer_size_bytes": sum(int(row["size_bytes"]) for row in self.archives),
            "archive_member_count": len(self.members),
            "member_uncompressed_bytes": sum(
                int(row["uncompressed_size_bytes"]) for row in self.members
            ),
            "nested_zip_member_count": sum(
                bool(row["is_nested_archive"]) for row in self.members
            ),
            "crc_size_duplicate_candidate_rows": sum(
                int(row["crc_size_duplicate_count"] or 0) > 1 for row in self.members
            ),
            "exact_member_metadata_duplicate_rows": sum(
                bool(row["exact_member_metadata_duplicate"]) for row in self.members
            ),
            "missing_expected_count": len(self.missing_expected),
            "issue_counts": {
                "info": issue_counts["info"],
                "warning": issue_counts["warning"],
                "error": issue_counts["error"],
            },
            "limited": self.limited,
            "by_experiment_run_modality": dict(sorted(by_scope.items())),
        }


def _require_mapping(parent: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = parent.get(key)
    if not isinstance(value, Mapping):
        raise ConfigError(f"{key}: must be a mapping")
    return value


def _text_sequence(value: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or not value:
        raise ConfigError(f"{field}: must be a non-empty sequence")
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ConfigError(f"{field}[{index}]: must be a non-empty string")
        items.append(item)
    return tuple(items)


def build_inventory_plan(
    dataset_config: ResolvedConfig, *, data_root_override: str | None = None
) -> InventoryPlan:
    """Validate the generic inventory portion of a dataset configuration."""

    dataset = dataset_config.require_mapping("dataset")
    include = dataset_config.require_mapping("include")
    exclude = dataset_config.require_mapping("exclude")
    dataset_name = dataset.get("name")
    if not isinstance(dataset_name, str) or not dataset_name:
        raise ConfigError("dataset.name: must be a non-empty string")
    root_value: object = data_root_override or dataset.get("data_root")
    data_root = dataset_config.resolve_repository_path(
        root_value, field="dataset.data_root", must_exist=True
    )
    root_reference = data_root.relative_to(dataset_config.repository_root).as_posix()
    excluded_roots = dataset.get("excluded_repository_roots", ())
    if not isinstance(excluded_roots, (list, tuple)):
        raise ConfigError("dataset.excluded_repository_roots: must be a sequence")
    for index, excluded in enumerate(excluded_roots):
        excluded_path = dataset_config.resolve_repository_path(
            excluded,
            field=f"dataset.excluded_repository_roots[{index}]",
            must_exist=False,
        )
        if data_root == excluded_path or excluded_path in data_root.parents:
            raise ConfigError(
                "dataset.data_root resolves inside an excluded repository root"
            )
    raw_modality_roots = _require_mapping(include, "modality_roots")
    modality_roots = {
        str(modality): _text_sequence(roots, field=f"include.modality_roots.{modality}")
        for modality, roots in raw_modality_roots.items()
    }
    for modality, roots in modality_roots.items():
        for index, relative in enumerate(roots):
            candidate = (data_root / relative).resolve()
            try:
                candidate.relative_to(data_root)
            except ValueError as exc:
                raise ConfigError(
                    f"include.modality_roots.{modality}[{index}]: escapes data root"
                ) from exc
            if not candidate.is_dir():
                raise ConfigError(
                    f"include.modality_roots.{modality}[{index}]: directory not found"
                )
    raw_experiments = _require_mapping(include, "experiments")
    experiments: dict[str, tuple[int, ...]] = {}
    for experiment, details in raw_experiments.items():
        if not isinstance(details, Mapping):
            raise ConfigError(f"include.experiments.{experiment}: must be a mapping")
        runs = details.get("runs")
        if not isinstance(runs, (list, tuple)) or not runs:
            raise ConfigError(
                f"include.experiments.{experiment}.runs: must be non-empty"
            )
        normalized_runs: list[int] = []
        for run in runs:
            if isinstance(run, bool) or not isinstance(run, int) or run <= 0:
                raise ConfigError(
                    f"include.experiments.{experiment}.runs: runs must be positive integers"
                )
            normalized_runs.append(run)
        if len(set(normalized_runs)) != len(normalized_runs):
            raise ConfigError(f"include.experiments.{experiment}.runs: duplicate run")
        experiments[str(experiment)] = tuple(normalized_runs)
    extensions = _text_sequence(
        include.get("file_extensions"), field="include.file_extensions"
    )
    allowed_extensions = tuple(
        extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        for extension in extensions
    )
    raw_modes = _require_mapping(include, "expectation_mode_by_modality")
    expectation_modes: dict[str, str] = {}
    for modality in modality_roots:
        mode = raw_modes.get(modality)
        if mode not in {"runs", "experiments", "none"}:
            raise ConfigError(
                f"include.expectation_mode_by_modality.{modality}: expected runs, experiments, or none"
            )
        expectation_modes[modality] = str(mode)
    excluded_globs_raw = exclude.get("path_globs", ())
    if not isinstance(excluded_globs_raw, (list, tuple)):
        raise ConfigError("exclude.path_globs: must be a sequence")
    excluded_globs = tuple(str(pattern) for pattern in excluded_globs_raw)
    return InventoryPlan(
        repository_root=dataset_config.repository_root,
        data_root=data_root,
        data_root_reference=root_reference,
        dataset_name=dataset_name,
        modality_roots=modality_roots,
        experiments=experiments,
        allowed_extensions=allowed_extensions,
        excluded_globs=excluded_globs,
        expectation_mode_by_modality=expectation_modes,
    )


def discover_inventory_paths(
    plan: InventoryPlan,
) -> tuple[list[DiscoveredAsset], list[InventoryIssue]]:
    """Discover only configured modality roots, without opening any file."""

    discovered: dict[str, DiscoveredAsset] = {}
    issues: list[InventoryIssue] = []
    for modality, roots in sorted(plan.modality_roots.items()):
        for relative_root in sorted(roots):
            absolute_root = plan.data_root / relative_root
            for directory, directory_names, file_names in os.walk(
                absolute_root, followlinks=False
            ):
                directory_path = Path(directory)
                kept_directories: list[str] = []
                for name in sorted(directory_names):
                    candidate = directory_path / name
                    if candidate.is_symlink():
                        relative = candidate.relative_to(plan.data_root).as_posix()
                        issues.append(
                            InventoryIssue(
                                severity="warning",
                                code="symlink_skipped",
                                relative_path=relative,
                                message="symlinked directory was not followed",
                            )
                        )
                    else:
                        kept_directories.append(name)
                directory_names[:] = kept_directories
                for name in sorted(file_names):
                    candidate = directory_path / name
                    relative = candidate.relative_to(plan.data_root).as_posix()
                    if any(
                        fnmatch.fnmatch(relative, pattern)
                        for pattern in plan.excluded_globs
                    ):
                        continue
                    if candidate.is_symlink():
                        issues.append(
                            InventoryIssue(
                                severity="warning",
                                code="symlink_skipped",
                                relative_path=relative,
                                message="symlinked file was not inspected",
                            )
                        )
                        continue
                    stat = candidate.stat()
                    asset = DiscoveredAsset(
                        modality_hint=modality,
                        path=candidate,
                        relative_path=relative,
                        allowed_extension=candidate.suffix.lower()
                        in plan.allowed_extensions,
                        size_bytes=stat.st_size,
                    )
                    previous = discovered.get(relative)
                    if previous is not None and previous.modality_hint != modality:
                        issues.append(
                            InventoryIssue(
                                severity="error",
                                code="overlapping_modality_roots",
                                relative_path=relative,
                                message="file was discovered under multiple modality definitions",
                            )
                        )
                    discovered[relative] = asset
    return [discovered[key] for key in sorted(discovered)], issues


def _member_file_type(name: str) -> str:
    suffix = PurePosixPath(name).suffix.lower()
    return suffix.removeprefix(".") or "no_extension"


def _central_directory_fingerprint(infos: Sequence[zipfile.ZipInfo]) -> str:
    canonical = [
        {
            "filename": info.filename,
            "crc32": f"{info.CRC:08x}",
            "compressed_size": info.compress_size,
            "uncompressed_size": info.file_size,
            "compression_method": info.compress_type,
            "flag_bits": info.flag_bits,
            "is_directory": info.is_dir(),
        }
        for info in infos
    ]
    canonical.sort(
        key=lambda row: (
            str(row["filename"]),
            str(row["crc32"]),
            int(row["uncompressed_size"]),
            int(row["compressed_size"]),
        )
    )
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return sha256(payload).hexdigest()


def _profile_one(
    discovered: DiscoveredAsset,
    *,
    adapter: BaseDatasetAdapter,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[InventoryIssue]]:
    issues: list[InventoryIssue] = []
    identity_error: str | None = None
    try:
        identity = adapter.parse_asset_identity(discovered.relative_path)
        asset_record = adapter.make_asset_record(
            discovered.relative_path, size_bytes=discovered.size_bytes
        )
        asset_id = asset_record.asset_id
        experiment = identity.experiment
        run = identity.run
        modality = identity.modality
        naming_pattern = adapter.asset_naming_pattern(discovered.relative_path)
    except (ContractValidationError, ValueError) as exc:
        identity_error = str(exc)
        asset_id = deterministic_id(
            "unparsed_asset", {"relative_path": discovered.relative_path}
        )
        experiment = None
        run = None
        modality = discovered.modality_hint
        naming_pattern = None
        issues.append(
            InventoryIssue(
                severity="error",
                code="asset_identity_unparsed",
                relative_path=discovered.relative_path,
                message=identity_error,
            )
        )
    file_type = _member_file_type(discovered.relative_path)
    base: dict[str, Any] = {
        "schema_version": INVENTORY_SCHEMA_VERSION,
        "asset_id": asset_id,
        "relative_path": discovered.relative_path,
        "file_name": discovered.path.name,
        "file_type": file_type,
        "naming_pattern": naming_pattern,
        "modality": modality,
        "experiment": experiment,
        "run": run,
        "size_bytes": discovered.size_bytes,
        "readable": False,
        "unexpected_extension": not discovered.allowed_extension,
        "empty_file": discovered.size_bytes == 0,
        "member_count": None,
        "directory_entry_count": None,
        "nested_archive_member_count": None,
        "compressed_member_bytes": None,
        "uncompressed_member_bytes": None,
        "central_directory_sha256": None,
        "central_directory_comment_bytes": None,
        "metadata_duplicate_group_id": None,
        "metadata_duplicate_count": 0,
        "error": identity_error,
    }
    if not discovered.allowed_extension:
        issues.append(
            InventoryIssue(
                severity="warning",
                code="unexpected_extension",
                relative_path=discovered.relative_path,
                message=(
                    f"extension {discovered.path.suffix or '<none>'!r} is not configured"
                ),
            )
        )
        return base, [], issues
    if discovered.size_bytes == 0:
        issues.append(
            InventoryIssue(
                severity="error",
                code="empty_file",
                relative_path=discovered.relative_path,
                message="file is empty",
            )
        )
        return base, [], issues
    members: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(discovered.path, mode="r", allowZip64=True) as archive:
            infos = archive.infolist()
            comment_size = len(archive.comment)
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        base["error"] = f"{type(exc).__name__}: {exc}"
        issues.append(
            InventoryIssue(
                severity="error",
                code="unreadable_archive",
                relative_path=discovered.relative_path,
                message=base["error"],
            )
        )
        return base, [], issues
    file_infos = [info for info in infos if not info.is_dir()]
    directory_infos = [info for info in infos if info.is_dir()]
    base.update(
        {
            "readable": True,
            "member_count": len(file_infos),
            "directory_entry_count": len(directory_infos),
            "nested_archive_member_count": sum(
                PurePosixPath(info.filename).suffix.lower() == ".zip"
                for info in file_infos
            ),
            "compressed_member_bytes": sum(info.compress_size for info in file_infos),
            "uncompressed_member_bytes": sum(info.file_size for info in file_infos),
            "central_directory_sha256": _central_directory_fingerprint(infos),
            "central_directory_comment_bytes": comment_size,
            "error": identity_error,
        }
    )
    occurrences: Counter[str] = Counter()
    member_run_parse_errors: list[str] = []
    member_archive_run_conflicts: list[str] = []
    for info in file_infos:
        occurrences[info.filename] += 1
        member_run: int | None = None
        member_run_error: str | None = None
        try:
            member_run = adapter.parse_run(PurePosixPath(info.filename).name)
        except (ContractValidationError, ValueError) as exc:
            member_run_error = str(exc)
            member_run_parse_errors.append(info.filename)
        member_run_matches_archive: bool | None = None
        if run is not None and member_run is not None:
            member_run_matches_archive = member_run == run
            if not member_run_matches_archive:
                member_archive_run_conflicts.append(info.filename)
        member_id = deterministic_id(
            "archive_member",
            {
                "archive_asset_id": asset_id,
                "member": info.filename,
                "occurrence": occurrences[info.filename],
            },
        )
        members.append(
            {
                "schema_version": INVENTORY_SCHEMA_VERSION,
                "member_id": member_id,
                "archive_asset_id": asset_id,
                "archive_relative_path": discovered.relative_path,
                "archive_member": info.filename,
                "member_file_type": _member_file_type(info.filename),
                "modality": modality,
                "experiment": experiment,
                "run": run if run is not None else member_run,
                "member_run_token": member_run,
                "member_run_matches_archive": member_run_matches_archive,
                "member_run_parse_error": member_run_error,
                "compressed_size_bytes": info.compress_size,
                "uncompressed_size_bytes": info.file_size,
                "compression_method": info.compress_type,
                "encrypted": bool(info.flag_bits & 0x1),
                "checksum_algorithm": "zip_crc32",
                "checksum": f"{info.CRC:08x}",
                "is_nested_archive": PurePosixPath(info.filename).suffix.lower()
                == ".zip",
                "crc_size_duplicate_group_id": None,
                "crc_size_duplicate_count": 0,
                "exact_member_metadata_duplicate": False,
                "duplicate_evidence": None,
            }
        )
    if member_run_parse_errors:
        issues.append(
            InventoryIssue(
                severity="warning",
                code="member_run_unparsed",
                relative_path=discovered.relative_path,
                message=(
                    f"{len(member_run_parse_errors)} member name(s) contain conflicting "
                    "run tokens; archive scope was retained. Examples: "
                    + ", ".join(repr(name) for name in member_run_parse_errors[:3])
                ),
            )
        )
    if member_archive_run_conflicts:
        issues.append(
            InventoryIssue(
                severity="warning",
                code="member_archive_run_conflict",
                relative_path=discovered.relative_path,
                message=(
                    f"{len(member_archive_run_conflicts)} member name(s) encode a run "
                    f"different from archive run {run}; archive scope was retained. "
                    "Examples: "
                    + ", ".join(repr(name) for name in member_archive_run_conflicts[:3])
                ),
            )
        )
    return base, members, issues


def _annotate_duplicates(
    archives: list[dict[str, Any]], members: list[dict[str, Any]]
) -> None:
    archive_groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in archives:
        fingerprint = row.get("central_directory_sha256")
        if fingerprint:
            archive_groups[(int(row["size_bytes"]), str(fingerprint))].append(row)
    for signature, rows in archive_groups.items():
        if len(rows) <= 1:
            continue
        group_id = deterministic_id(
            "archive_metadata_duplicate",
            {"size_bytes": signature[0], "central_directory_sha256": signature[1]},
        )
        for row in rows:
            row["metadata_duplicate_group_id"] = group_id
            row["metadata_duplicate_count"] = len(rows)

    candidate_groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    exact_metadata_groups: dict[
        tuple[str, str, int, int, str], list[dict[str, Any]]
    ] = defaultdict(list)
    for row in members:
        candidate_groups[
            (int(row["uncompressed_size_bytes"]), str(row["checksum"]))
        ].append(row)
        exact_metadata_groups[
            (
                str(row["archive_relative_path"]),
                str(row["archive_member"]),
                int(row["compressed_size_bytes"]),
                int(row["uncompressed_size_bytes"]),
                str(row["checksum"]),
            )
        ].append(row)
    for signature, rows in candidate_groups.items():
        if len(rows) <= 1:
            continue
        group_id = deterministic_id(
            "crc_size_duplicate",
            {"uncompressed_size_bytes": signature[0], "crc32": signature[1]},
        )
        for row in rows:
            row["crc_size_duplicate_group_id"] = group_id
            row["crc_size_duplicate_count"] = len(rows)
            row["duplicate_evidence"] = "zip_crc32+uncompressed_size"
    for rows in exact_metadata_groups.values():
        if len(rows) <= 1:
            continue
        for row in rows:
            row["exact_member_metadata_duplicate"] = True
            row["duplicate_evidence"] = "identical_central_directory_entry"


def _missing_expected(
    plan: InventoryPlan, archives: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    observed = {
        (row.get("modality"), row.get("experiment"), row.get("run"))
        for row in archives
        if not row.get("unexpected_extension") and row.get("experiment") is not None
    }
    missing: list[dict[str, Any]] = []
    for modality, mode in sorted(plan.expectation_mode_by_modality.items()):
        if mode == "none":
            continue
        for experiment, runs in sorted(plan.experiments.items()):
            expected_runs: Sequence[int | None] = runs if mode == "runs" else (None,)
            for run in expected_runs:
                if (modality, experiment, run) not in observed:
                    missing.append(
                        {
                            "schema_version": INVENTORY_SCHEMA_VERSION,
                            "modality": modality,
                            "experiment": experiment,
                            "run": run,
                            "expectation_mode": mode,
                        }
                    )
    return missing


def profile_asset_inventory(
    plan: InventoryPlan,
    adapter: BaseDatasetAdapter,
    *,
    limit: int | None = None,
) -> InventoryResult:
    """Read filesystem metadata and ZIP central directories for configured assets."""

    if limit is not None and (
        isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0
    ):
        raise ValueError("limit must be a positive integer or null")
    discovered, issues = discover_inventory_paths(plan)
    selected = discovered if limit is None else discovered[:limit]
    archives: list[dict[str, Any]] = []
    members: list[dict[str, Any]] = []
    for asset in selected:
        archive_row, member_rows, asset_issues = _profile_one(asset, adapter=adapter)
        archives.append(archive_row)
        members.extend(member_rows)
        issues.extend(asset_issues)
    _annotate_duplicates(archives, members)
    missing = [] if limit is not None else _missing_expected(plan, archives)
    for row in missing:
        issues.append(
            InventoryIssue(
                severity="error",
                code="missing_expected_scope",
                relative_path=None,
                message=(
                    f"missing {row['modality']} archive for {row['experiment']} "
                    f"run {row['run'] if row['run'] is not None else 'aggregate'}"
                ),
            )
        )
    return InventoryResult(
        archives=archives,
        members=members,
        issues=issues,
        missing_expected=missing,
        discovered_count=len(discovered),
        limited=limit is not None,
    )


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_parquet(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    pd.DataFrame(list(rows)).to_parquet(path, index=False)


def _summary_markdown(
    summary: Mapping[str, Any], issues: Sequence[InventoryIssue]
) -> str:
    issue_counts = summary["issue_counts"]
    scope_rows = summary["by_experiment_run_modality"]
    lines = [
        "# PHM 2026 asset inventory",
        "",
        f"Schema version: `{summary['schema_version']}`",
        "",
        "This report inventories filesystem metadata and ZIP central directories only. "
        "No archive member was extracted, decompressed, or payload-hashed.",
        "",
        "## Totals",
        "",
        f"- Discovered files: {summary['discovered_file_count']}",
        f"- Profiled files: {summary['profiled_file_count']}",
        f"- ZIP archives: {summary['zip_archive_count']}",
        f"- Archive members: {summary['archive_member_count']}",
        f"- Outer compressed bytes: {summary['outer_size_bytes']}",
        f"- Member uncompressed bytes: {summary['member_uncompressed_bytes']}",
        f"- Nested ZIP members: {summary['nested_zip_member_count']}",
        f"- Missing expected combinations: {summary['missing_expected_count']}",
        f"- Issues: {issue_counts['error']} errors, {issue_counts['warning']} warnings, "
        f"{issue_counts['info']} informational",
        "",
        "## Experiment, run, and modality totals",
        "",
        "| Experiment | Run | Modality | Archives | Bytes | Members | Uncompressed member bytes |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for key, values in scope_rows.items():
        experiment, run, modality = key.split("|", 2)
        lines.append(
            f"| {experiment} | {run} | {modality} | {values['archive_count']} | "
            f"{values['size_bytes']} | {values['member_count']} | "
            f"{values['uncompressed_member_bytes']} |"
        )
    lines.extend(
        [
            "",
            "## Duplicate evidence",
            "",
            f"- Rows in CRC32 + uncompressed-size candidate groups: "
            f"{summary['crc_size_duplicate_candidate_rows']}",
            f"- Repeated identical central-directory member rows: "
            f"{summary['exact_member_metadata_duplicate_rows']}",
            "- CRC32 evidence is lightweight and is not cryptographic proof of equal payloads.",
            "",
            "## Issues",
            "",
        ]
    )
    if not issues:
        lines.append("No issues recorded.")
    else:
        lines.extend(["| Severity | Code | Path | Message |", "|---|---|---|---|"])
        for issue in issues:
            message = issue.message.replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {issue.severity} | {issue.code} | "
                f"{issue.relative_path or ''} | {message} |"
            )
    return "\n".join(lines) + "\n"


def write_inventory_run(
    result: InventoryResult,
    *,
    run: RunContext,
    resolved_config: Mapping[str, Any],
    input_manifest: Sequence[Mapping[str, Any]],
) -> list[ArtifactRecord]:
    """Write a complete versioned D1.1 run and finalize its provenance."""

    run.create_layout()
    artifacts: list[ArtifactRecord] = []
    config_path = run.write_resolved_config(resolved_config)
    artifacts.append(run.artifact(config_path, role="resolved_configuration"))
    inputs_path = run.write_input_manifest(input_manifest)
    artifacts.append(run.artifact(inputs_path, role="input_manifest"))

    archive_csv = run.run_directory / "tables/asset_inventory.csv"
    archive_parquet = run.run_directory / "tables/asset_inventory.parquet"
    member_csv = run.run_directory / "tables/archive_members.csv"
    member_parquet = run.run_directory / "tables/archive_members.parquet"
    _write_csv(archive_csv, result.archives)
    _write_parquet(archive_parquet, result.archives)
    _write_csv(member_csv, result.members)
    _write_parquet(member_parquet, result.members)
    artifacts.extend(
        [
            run.artifact(archive_csv, role="asset_inventory_csv"),
            run.artifact(archive_parquet, role="asset_inventory_parquet"),
            run.artifact(member_csv, role="archive_member_inventory_csv"),
            run.artifact(member_parquet, role="archive_member_inventory_parquet"),
        ]
    )

    summary = result.summary()
    summary_path = run.run_directory / "reports/summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path = run.run_directory / "reports/summary.md"
    report_path.write_text(_summary_markdown(summary, result.issues), encoding="utf-8")
    warning_path = run.run_directory / "reports/warnings.json"
    warning_path.write_text(
        json.dumps(
            {
                "schema_version": INVENTORY_SCHEMA_VERSION,
                "issues": [asdict(issue) for issue in result.issues],
                "missing_expected": result.missing_expected,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    artifacts.extend(
        [
            run.artifact(summary_path, role="inventory_summary_json"),
            run.artifact(report_path, role="inventory_summary_markdown"),
            run.artifact(warning_path, role="warnings"),
        ]
    )
    provenance_path = run.write_provenance(artifacts)
    artifacts_with_provenance = [
        *artifacts,
        run.artifact(provenance_path, role="run_provenance"),
    ]
    run.write_output_manifest(artifacts_with_provenance)
    return artifacts_with_provenance
