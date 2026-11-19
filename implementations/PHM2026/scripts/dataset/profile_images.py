#!/usr/bin/env python3
"""Repository entry point for D1.3 bounded PHM image profiling."""

from pathlib import Path
import sys

REPOSITORY_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").is_file() and (p / "pyproject.toml").is_file())
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from phm2026.cli import profile_images_main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(profile_images_main())
