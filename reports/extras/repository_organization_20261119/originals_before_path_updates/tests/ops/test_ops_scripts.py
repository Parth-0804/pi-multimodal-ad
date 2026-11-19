"""Tests for the repository-maintenance scripts under `scripts/ops/`."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

CONFIG = """schema_version: "1.0.0"
study: example
source_runs:
  upstream:
    run_id: OLD-RUN
    directory: runs/example/OLD-RUN
    artifacts:
      tables/one.parquet: aaaa
      reports/two.json: bbbb
  sibling:
    run_id: KEEP-RUN
    directory: runs/other/KEEP-RUN
    artifacts:
      tables/three.parquet: cccc
evaluation:
  repetitions: 2000
"""


def _load(name: str) -> ModuleType:
    path = REPOSITORY_ROOT / "scripts" / "ops" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repin_rewrites_only_the_named_source_entry() -> None:
    repin = _load("repin_source_run")
    rewritten = "".join(
        repin.rewrite(
            CONFIG.splitlines(keepends=True),
            source_key="upstream",
            new_run_id="NEW-RUN",
            new_directory="runs/example/NEW-RUN",
            new_hashes={
                "tables/one.parquet": "a1" * 32,
                "reports/two.json": "b2" * 32,
            },
        )
    )
    parsed = yaml.safe_load(rewritten)

    upstream = parsed["source_runs"]["upstream"]
    assert upstream["run_id"] == "NEW-RUN"
    assert upstream["directory"] == "runs/example/NEW-RUN"
    assert upstream["artifacts"]["tables/one.parquet"] == "a1" * 32
    assert upstream["artifacts"]["reports/two.json"] == "b2" * 32

    # A sibling entry that happens to pin a different run must not be touched.
    sibling = parsed["source_runs"]["sibling"]
    assert sibling["run_id"] == "KEEP-RUN"
    assert sibling["artifacts"]["tables/three.parquet"] == "cccc"

    # Nothing outside source_runs may move.
    assert parsed["schema_version"] == "1.0.0"
    assert parsed["evaluation"]["repetitions"] == 2000

    changed = [
        index
        for index, (before, after) in enumerate(
            zip(CONFIG.splitlines(), rewritten.splitlines())
        )
        if before != after
    ]
    assert len(changed) == 4, changed


def test_repin_leaves_artifacts_it_was_not_given() -> None:
    """An artifact absent from new_hashes keeps its existing pin."""

    repin = _load("repin_source_run")
    rewritten = "".join(
        repin.rewrite(
            CONFIG.splitlines(keepends=True),
            source_key="upstream",
            new_run_id="NEW-RUN",
            new_directory="runs/example/NEW-RUN",
            new_hashes={"tables/one.parquet": "a1" * 32},
        )
    )
    upstream = yaml.safe_load(rewritten)["source_runs"]["upstream"]
    assert upstream["artifacts"]["tables/one.parquet"] == "a1" * 32
    assert upstream["artifacts"]["reports/two.json"] == "bbbb"
