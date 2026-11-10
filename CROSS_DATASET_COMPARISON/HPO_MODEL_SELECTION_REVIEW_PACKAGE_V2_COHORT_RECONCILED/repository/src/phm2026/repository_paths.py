"""Dependency-free repository location used by PHM configuration and acquisition."""

from pathlib import Path


class RepositoryRootError(ValueError):
    """Repository markers were not found above the supplied starting location."""


def find_repository_root(start: Path | None = None) -> Path:
    """Find the nearest parent containing both .git and AGENTS.md."""
    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / ".git").exists() and (directory / "AGENTS.md").is_file():
            return directory
    raise RepositoryRootError(f"repository root not found from {candidate}")
