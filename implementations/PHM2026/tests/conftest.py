from __future__ import annotations

from pathlib import Path
import sys

SRC = next(p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").is_file() and (p / "pyproject.toml").is_file()) / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
