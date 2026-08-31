#!/usr/bin/env python3
"""Run the artifact-only PHM D1.4 clock and alignment audit."""

from __future__ import annotations

from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from pi_multimodal_ad.cli import audit_alignment_main

if __name__ == "__main__":
    raise SystemExit(audit_alignment_main())
