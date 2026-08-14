"""Versioned, non-overwriting run directories and provenance manifests."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
from typing import Any

import yaml

from .config import ConfigError, ResolvedConfig

RUN_SCHEMA_VERSION = "1.0.0"


def _json_text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _relative_to_root(path: Path, root: Path, *, field: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ConfigError(f"{field}: path must be inside the repository") from exc


def _git_state(repository_root: Path) -> tuple[str | None, bool | None]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None, None
    return commit, bool(status)


def _package_versions(names: Iterable[str]) -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in sorted(set(names)):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    path: str
    role: str
    size_bytes: int
    sha256: str


@dataclass(slots=True)
class RunContext:
    repository_root: Path
    run_directory: Path
    run_id: str
    study: str
    timestamp_utc: str
    command: tuple[str, ...]
    config: ResolvedConfig
    seed: int
    input_roots: tuple[str, ...]
    git_commit: str | None
    git_dirty: bool | None
    package_versions: Mapping[str, str | None]
    source_runs: tuple[Mapping[str, Any], ...]

    def create_layout(self) -> None:
        self.run_directory.mkdir(parents=True, exist_ok=False)
        for relative in ("config", "manifests", "reports", "tables", "figures", "logs"):
            (self.run_directory / relative).mkdir()

    def write_resolved_config(self, data: Mapping[str, Any]) -> Path:
        path = self.run_directory / "config/resolved_config.yaml"
        path.write_text(
            yaml.safe_dump(dict(data), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return path

    def write_input_manifest(self, inputs: Sequence[Mapping[str, Any]]) -> Path:
        path = self.run_directory / "manifests/inputs.json"
        path.write_text(
            _json_text({"schema_version": RUN_SCHEMA_VERSION, "inputs": list(inputs)}),
            encoding="utf-8",
        )
        return path

    def artifact(self, path: Path, *, role: str) -> ArtifactRecord:
        relative = path.resolve().relative_to(self.run_directory.resolve()).as_posix()
        data = path.read_bytes()
        return ArtifactRecord(
            path=relative,
            role=role,
            size_bytes=len(data),
            sha256=sha256(data).hexdigest(),
        )

    def write_provenance(self, artifacts: Sequence[ArtifactRecord]) -> Path:
        path = self.run_directory / "provenance.json"
        payload = {
            "schema_version": RUN_SCHEMA_VERSION,
            "run_id": self.run_id,
            "study": self.study,
            "timestamp_utc": self.timestamp_utc,
            "git": {"commit": self.git_commit, "dirty": self.git_dirty},
            "command": list(self.command),
            "config": {
                "path": self.config.relative_path,
                "sha256": self.config.sha256,
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
            },
            "packages": dict(self.package_versions),
            "seed": self.seed,
            "input_roots": list(self.input_roots),
            "source_runs": [dict(source) for source in self.source_runs],
            "output_root": _relative_to_root(
                self.run_directory, self.repository_root, field="output_root"
            ),
            "produced_artifacts": [asdict(artifact) for artifact in artifacts],
        }
        path.write_text(_json_text(payload), encoding="utf-8")
        return path

    def write_output_manifest(self, artifacts: Sequence[ArtifactRecord]) -> Path:
        path = self.run_directory / "manifests/outputs.json"
        path.write_text(
            _json_text(
                {
                    "schema_version": RUN_SCHEMA_VERSION,
                    "run_id": self.run_id,
                    "artifacts": [asdict(artifact) for artifact in artifacts],
                }
            ),
            encoding="utf-8",
        )
        return path


def create_run_context(
    *,
    study: str,
    output_root: Path,
    config: ResolvedConfig,
    seed: int,
    command: Sequence[str],
    input_roots: Sequence[str],
    now: datetime | None = None,
    package_names: Sequence[str] = ("numpy", "pandas", "pyarrow", "PyYAML"),
    source_runs: Sequence[Mapping[str, Any]] = (),
) -> RunContext:
    """Create metadata for a unique run; the caller explicitly creates its layout."""

    if not study or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for character in study
    ):
        raise ValueError(
            "study must contain only lowercase letters, digits, '_' or '-'"
        )
    root = config.repository_root
    resolved_output_root = output_root.resolve()
    _relative_to_root(resolved_output_root, root, field="output_root")
    timestamp = now or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("run timestamp must be timezone-aware")
    timestamp = timestamp.astimezone(timezone.utc)
    run_id = f"{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}-{config.sha256[:8]}"
    commit, dirty = _git_state(root)
    return RunContext(
        repository_root=root,
        run_directory=resolved_output_root / run_id,
        run_id=run_id,
        study=study,
        timestamp_utc=timestamp.isoformat(timespec="microseconds"),
        command=tuple(command),
        config=config,
        seed=seed,
        input_roots=tuple(input_roots),
        git_commit=commit,
        git_dirty=dirty,
        package_versions=_package_versions(package_names),
        source_runs=tuple(dict(source) for source in source_runs),
    )
