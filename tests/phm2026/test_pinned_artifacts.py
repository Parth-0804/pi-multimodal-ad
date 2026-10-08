from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest

from pi_multimodal_ad.utils import ConfigError, load_pinned_run, sha256_file


def _json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _fake_run(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    root = tmp_path / "repository"
    root.mkdir()
    run_id = "20260101T000000000000Z-deadbeef"
    run = root / "runs/study" / run_id
    artifact = run / "tables/source.parquet"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"synthetic generated artifact")
    artifact_hash = sha256_file(artifact)
    _json(
        run / "provenance.json",
        {"schema_version": "1.0.0", "run_id": run_id},
    )
    _json(
        run / "manifests/outputs.json",
        {
            "schema_version": "1.0.0",
            "run_id": run_id,
            "artifacts": [
                {
                    "path": "tables/source.parquet",
                    "sha256": artifact_hash,
                    "size_bytes": artifact.stat().st_size,
                    "role": "synthetic",
                }
            ],
        },
    )
    specification: dict[str, object] = {
        "run_id": run_id,
        "directory": f"runs/study/{run_id}",
        "artifacts": {"tables/source.parquet": artifact_hash},
    }
    return root, specification


def test_pinned_run_requires_exact_artifact_hash(tmp_path: Path) -> None:
    root, specification = _fake_run(tmp_path)
    pinned = load_pinned_run(
        root, specification, required_artifacts=("tables/source.parquet",)
    )
    assert pinned.run_id == specification["run_id"]
    assert (
        pinned.artifact_path("tables/source.parquet")
        .read_bytes()
        .startswith(b"synthetic")
    )
    assert pinned.source_record("tables/source.parquet")["artifact_sha256"]


def test_pinned_run_rejects_hash_mismatch_and_missing_pin(tmp_path: Path) -> None:
    root, specification = _fake_run(tmp_path)
    bad = dict(specification)
    bad["artifacts"] = {"tables/source.parquet": "0" * 64}
    with pytest.raises(ConfigError, match="hash mismatch"):
        load_pinned_run(root, bad, required_artifacts=("tables/source.parquet",))
    with pytest.raises(ConfigError, match="missing required hash pins"):
        load_pinned_run(
            root, specification, required_artifacts=("tables/other.parquet",)
        )


def test_streaming_hash_matches_reference(tmp_path: Path) -> None:
    path = tmp_path / "artifact.bin"
    payload = b"0123456789" * 1000
    path.write_bytes(payload)
    assert sha256_file(path, block_bytes=17) == sha256(payload).hexdigest()
