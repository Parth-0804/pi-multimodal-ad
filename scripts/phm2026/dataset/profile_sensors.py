#!/usr/bin/env python3
"""Repository entry point for D1.2 bounded PHM sensor profiling."""

from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from pi_multimodal_ad.cli import profile_sensors_main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(profile_sensors_main())
