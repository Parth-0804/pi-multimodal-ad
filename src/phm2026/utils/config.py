"""Portable YAML loading and repository-relative path resolution."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml


class ConfigError(ValueError):
    """A configuration error with field-level context."""


def find_repository_root(start: Path | None = None) -> Path:
    """Find the nearest parent containing both ``.git`` and ``AGENTS.md``."""

    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / ".git").exists() and (directory / "AGENTS.md").is_file():
            return directory
    raise ConfigError(f"repository root not found from {candidate}")


def _immutable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _immutable(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_immutable(item) for item in value)
    return value


def _mutable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _mutable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_mutable(item) for item in value]
    return deepcopy(value)


@dataclass(frozen=True, slots=True)
class ResolvedConfig:
    """Loaded YAML plus its portable identity and repository root."""

    data: Mapping[str, Any]
    path: Path
    repository_root: Path
    sha256: str

    @property
    def relative_path(self) -> str:
        try:
            return self.path.relative_to(self.repository_root).as_posix()
        except ValueError as exc:
            raise ConfigError(
                "configuration file must be inside the repository"
            ) from exc

    def mutable_copy(self) -> dict[str, Any]:
        copy = _mutable(self.data)
        if not isinstance(copy, dict):
            raise ConfigError("configuration root must be a mapping")
        return copy

    def require_mapping(self, key: str) -> Mapping[str, Any]:
        value = self.data.get(key)
        if not isinstance(value, Mapping):
            raise ConfigError(f"{key}: must be a mapping")
        return value

    def require_text(self, key: str) -> str:
        value = self.data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"{key}: must be a non-empty string")
        if value != value.strip():
            raise ConfigError(f"{key}: must not contain surrounding whitespace")
        return value

    def resolve_repository_path(
        self, value: object, *, field: str, must_exist: bool = False
    ) -> Path:
        """Resolve one configured relative path without permitting root escape."""

        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"{field}: must be a non-empty relative path")
        configured = Path(value)
        if configured.is_absolute():
            raise ConfigError(
                f"{field}: absolute paths are not allowed in configuration"
            )
        resolved = (self.repository_root / configured).resolve()
        try:
            resolved.relative_to(self.repository_root)
        except ValueError as exc:
            raise ConfigError(f"{field}: path escapes the repository root") from exc
        if must_exist and not resolved.exists():
            raise ConfigError(f"{field}: path does not exist: {value}")
        return resolved


def load_yaml_config(
    path: str | Path, *, repository_root: Path | None = None
) -> ResolvedConfig:
    """Load a UTF-8 YAML mapping and validate its schema-version envelope."""

    root = (repository_root or find_repository_root()).resolve()
    configured_path = Path(path)
    resolved_path = (
        configured_path.resolve()
        if configured_path.is_absolute()
        else (root / configured_path).resolve()
    )
    try:
        resolved_path.relative_to(root)
    except ValueError as exc:
        raise ConfigError("configuration file must be inside the repository") from exc
    if not resolved_path.is_file():
        raise ConfigError(f"configuration file not found: {configured_path}")
    raw = resolved_path.read_bytes()
    try:
        loaded = yaml.safe_load(raw.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ConfigError(f"invalid UTF-8 YAML in {configured_path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ConfigError("configuration root must be a mapping")
    schema_version = loaded.get("schema_version")
    if schema_version != "1.0.0":
        raise ConfigError("schema_version: expected '1.0.0'")
    return ResolvedConfig(
        data=_immutable(loaded),
        path=resolved_path,
        repository_root=root,
        sha256=sha256(raw).hexdigest(),
    )
