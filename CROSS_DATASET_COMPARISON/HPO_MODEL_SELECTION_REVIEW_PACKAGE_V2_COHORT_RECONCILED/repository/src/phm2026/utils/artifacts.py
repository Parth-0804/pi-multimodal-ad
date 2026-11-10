"""Validation helpers for explicitly pinned upstream run artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from .config import ConfigError


def sha256_file(path: Path, *, block_bytes: int = 1024 * 1024) -> str:
    """Hash a generated artifact incrementally."""

    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_bytes):
            digest.update(block)
    return digest.hexdigest()


def _safe_relative_path(root: Path, value: object, *, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{field}: must be a non-empty repository-relative path")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ConfigError(f"{field}: escapes the repository root") from exc
    return candidate


@dataclass(frozen=True, slots=True)
class PinnedRun:
    """One exact upstream run with verified artifact identities."""

    directory: Path
    relative_directory: str
    run_id: str
    provenance: Mapping[str, Any]
    output_manifest: Mapping[str, Any]
    artifacts: Mapping[str, Mapping[str, Any]]
    verified_hashes: Mapping[str, str]

    def artifact_path(self, relative_path: str) -> Path:
        try:
            self.verified_hashes[relative_path]
        except KeyError as exc:
            raise ConfigError(
                f"source run artifact {relative_path!r} was not hash-pinned"
            ) from exc
        return self.directory / relative_path

    def source_record(self, relative_path: str) -> dict[str, Any]:
        path = self.artifact_path(relative_path)
        return {
            "source_run_id": self.run_id,
            "source_run_directory": self.relative_directory,
            "artifact_path": relative_path,
            "artifact_sha256": self.verified_hashes[relative_path],
            "artifact_size_bytes": path.stat().st_size,
        }


def load_pinned_run(
    repository_root: Path,
    specification: Mapping[str, Any],
    *,
    required_artifacts: tuple[str, ...],
) -> PinnedRun:
    """Load an exact run and verify every configured/required artifact hash."""

    root = repository_root.resolve()
    run_id = specification.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ConfigError("source run run_id: must be a non-empty string")
    directory = _safe_relative_path(
        root, specification.get("directory"), field="source run directory"
    )
    if not directory.is_dir():
        raise ConfigError(f"source run directory not found: {directory}")
    if directory.name != run_id:
        raise ConfigError("source run directory basename does not match run_id")

    provenance_path = directory / "provenance.json"
    output_manifest_path = directory / "manifests/outputs.json"
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        output_manifest = json.loads(output_manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"source run metadata is unreadable: {exc}") from exc
    if provenance.get("run_id") != run_id:
        raise ConfigError("source provenance run_id mismatch")
    if output_manifest.get("run_id") != run_id:
        raise ConfigError("source output manifest run_id mismatch")

    manifest_rows = output_manifest.get("artifacts")
    if not isinstance(manifest_rows, list):
        raise ConfigError("source output manifest artifacts must be a sequence")
    artifacts: dict[str, Mapping[str, Any]] = {}
    for row in manifest_rows:
        if not isinstance(row, Mapping) or not isinstance(row.get("path"), str):
            raise ConfigError("source output manifest contains an invalid artifact row")
        artifacts[str(row["path"])] = row

    configured = specification.get("artifacts")
    if not isinstance(configured, Mapping):
        raise ConfigError("source run artifacts: must map relative paths to SHA-256")
    missing_pins = [path for path in required_artifacts if path not in configured]
    if missing_pins:
        raise ConfigError(
            "source run is missing required hash pins: " + ", ".join(missing_pins)
        )

    verified: dict[str, str] = {}
    for relative, expected in configured.items():
        if not isinstance(relative, str) or not relative:
            raise ConfigError("source artifact path must be a non-empty string")
        if not isinstance(expected, str) or len(expected) != 64:
            raise ConfigError(f"source artifact {relative}: invalid SHA-256 pin")
        path = _safe_relative_path(directory, relative, field="source artifact")
        if not path.is_file():
            raise ConfigError(f"source artifact not found: {relative}")
        actual = sha256_file(path)
        if actual != expected:
            raise ConfigError(
                f"source artifact hash mismatch for {relative}: "
                f"expected {expected}, found {actual}"
            )
        if relative not in {"provenance.json", "manifests/outputs.json"}:
            manifest_row = artifacts.get(relative)
            if manifest_row is None:
                raise ConfigError(
                    f"source output manifest does not declare artifact {relative}"
                )
            if manifest_row.get("sha256") != expected:
                raise ConfigError(
                    f"source output manifest hash mismatch for {relative}"
                )
        verified[relative] = actual

    return PinnedRun(
        directory=directory,
        relative_directory=directory.relative_to(root).as_posix(),
        run_id=run_id,
        provenance=provenance,
        output_manifest=output_manifest,
        artifacts=artifacts,
        verified_hashes=verified,
    )
