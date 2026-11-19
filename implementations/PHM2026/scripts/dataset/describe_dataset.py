#!/usr/bin/env python3
"""Generate the artifact-only PHM D1.5 dataset description."""

from __future__ import annotations

from pathlib import Path
import sys

REPOSITORY_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").is_file() and (p / "pyproject.toml").is_file())
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from phm2026.cli import describe_dataset_main

if __name__ == "__main__":
    raise SystemExit(describe_dataset_main())
