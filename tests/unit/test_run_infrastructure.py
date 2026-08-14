from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import random

import numpy as np
import pytest

from pi_multimodal_ad.utils import (
    ConfigError,
    create_run_context,
    deterministic_group_split,
    load_yaml_config,
    set_reproducible_seed,
)


def _fake_repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    root.mkdir()
    (root / ".git").mkdir()
    (root / "AGENTS.md").write_text("synthetic instructions\n", encoding="utf-8")
    return root


def _write_config(root: Path, text: str) -> Path:
    path = root / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_config_loads_and_resolves_only_repository_paths(tmp_path: Path) -> None:
    root = _fake_repository(tmp_path)
    (root / "data").mkdir()
    config_path = _write_config(
        root,
        "schema_version: '1.0.0'\ninput_root: data\n",
    )
    config = load_yaml_config(config_path, repository_root=root)
    assert config.relative_path == "config.yaml"
    assert (
        config.resolve_repository_path(
            config.data["input_root"], field="input_root", must_exist=True
        )
        == root / "data"
    )
    assert len(config.sha256) == 64


@pytest.mark.parametrize(
    "text",
    [
        "- not\n- a\n- mapping\n",
        "schema_version: '2.0.0'\n",
        "schema_version: [broken\n",
    ],
)
def test_config_validation_is_clear(tmp_path: Path, text: str) -> None:
    root = _fake_repository(tmp_path)
    config_path = _write_config(root, text)
    with pytest.raises(ConfigError):
        load_yaml_config(config_path, repository_root=root)


def test_config_rejects_absolute_and_escaping_paths(tmp_path: Path) -> None:
    root = _fake_repository(tmp_path)
    config = load_yaml_config(
        _write_config(root, "schema_version: '1.0.0'\n"), repository_root=root
    )
    with pytest.raises(ConfigError, match="absolute paths"):
        config.resolve_repository_path("/tmp/outside", field="input_root")
    with pytest.raises(ConfigError, match="escapes"):
        config.resolve_repository_path("../outside", field="input_root")


def test_seed_reproduces_python_and_numpy_sequences() -> None:
    first_report = set_reproducible_seed(1234)
    first = (random.random(), np.random.random())
    second_report = set_reproducible_seed(1234)
    second = (random.random(), np.random.random())
    assert first == second
    assert first_report.seed == second_report.seed == 1234
    assert first_report.python_seeded
    assert first_report.numpy_seeded


def test_group_split_is_stable_and_seeded() -> None:
    fractions = {"train": 0.6, "validation": 0.2, "test": 0.2}
    first = deterministic_group_split("EXP-A/run-1", seed=17, fractions=fractions)
    second = deterministic_group_split("EXP-A/run-1", seed=17, fractions=fractions)
    assert first == second
    assert first in fractions
    assignments = {
        deterministic_group_split(f"group-{index}", seed=17, fractions=fractions)
        for index in range(100)
    }
    assert assignments == set(fractions)


def test_run_manifest_is_versioned_and_non_overwriting(tmp_path: Path) -> None:
    root = _fake_repository(tmp_path)
    config = load_yaml_config(
        _write_config(root, "schema_version: '1.0.0'\nstudy: synthetic\n"),
        repository_root=root,
    )
    context = create_run_context(
        study="synthetic_study",
        output_root=root / "runs/synthetic",
        config=config,
        seed=7,
        command=("script.py", "--dry-run"),
        input_roots=("synthetic_raw",),
        now=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        package_names=("PyYAML",),
        source_runs=(
            {
                "task": "D1.1",
                "run_id": "source-run",
                "artifact_sha256": "0" * 64,
            },
        ),
    )
    context.create_layout()
    resolved_path = context.write_resolved_config(config.mutable_copy())
    inputs_path = context.write_input_manifest([{"relative_path": "synthetic.zip"}])
    artifacts = [
        context.artifact(resolved_path, role="resolved_configuration"),
        context.artifact(inputs_path, role="input_manifest"),
    ]
    provenance_path = context.write_provenance(artifacts)
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    assert context.run_id == "20260102T030405000000Z-" + config.sha256[:8]
    assert provenance["command"] == ["script.py", "--dry-run"]
    assert provenance["config"]["sha256"] == config.sha256
    assert provenance["seed"] == 7
    assert provenance["input_roots"] == ["synthetic_raw"]
    assert provenance["source_runs"][0]["run_id"] == "source-run"
    assert provenance["python"]["version"]
    with pytest.raises(FileExistsError):
        context.create_layout()


def test_synthetic_multimodal_fixture_has_required_modalities() -> None:
    fixture_root = Path(__file__).resolve().parents[1] / "fixtures/synthetic_multimodal"
    payload = json.loads((fixture_root / "records.json").read_text(encoding="utf-8"))
    assert len(payload["records"]) == 2
    assert {record["group"] for record in payload["records"]} == {
        "group-a",
        "group-b",
    }
    for record in payload["records"]:
        assert len(record["sensor_values"]) == 4
        assert record["target_unit"] == "synthetic_unit"
        image_path = fixture_root / record["image"]
        assert image_path.read_text(encoding="ascii").startswith("P3\n2 2\n255\n")
