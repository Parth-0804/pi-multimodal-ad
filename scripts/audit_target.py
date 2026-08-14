#!/usr/bin/env python3
"""Execute T2.1 from exact generated artifacts and compact local documents."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from pi_multimodal_ad.reporting.target_audit import (  # noqa: E402
    build_target_audit,
    write_target_audit_run,
)
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)


def _verify_local(root: Path, specification: dict[str, object]) -> dict[str, object]:
    relative = str(specification["path"])
    path = (root / relative).resolve()
    path.relative_to(root)
    actual = sha256(path.read_bytes()).hexdigest()
    expected = str(specification["sha256"])
    if actual != expected:
        raise ConfigError(f"local document hash mismatch for {relative}")
    return {
        "source_run_id": "LOCAL_DOCUMENT",
        "artifact_path": relative,
        "artifact_sha256": actual,
        "authority": specification.get("authority"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_target_audit.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        source_specs = data["source_runs"]
        required = {
            "sensor_profile": (
                "tables/sensor_profile.parquet",
                "reports/sensor_summary.json",
            ),
            "image_profile": (
                "tables/image_profile.parquet",
                "reports/image_summary.json",
            ),
            "alignment_audit": (
                "tables/candidate_targets.parquet",
                "reports/alignment_blockers.json",
                "reports/alignment_summary.md",
            ),
        }
        pinned = {
            name: load_pinned_run(
                config.repository_root, source_specs[name], required_artifacts=paths
            )
            for name, paths in required.items()
        }
        local_sources = {
            name: _verify_local(config.repository_root, value)
            for name, value in data["local_documents"].items()
        }
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "source_runs": {
                            name: value.run_id for name, value in pinned.items()
                        },
                        "verified_local_documents": sorted(local_sources),
                        "would_open_raw_archives": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        blockers = json.loads(
            pinned["alignment_audit"]
            .artifact_path("reports/alignment_blockers.json")
            .read_text(encoding="utf-8")
        )
        sources = {
            "sensor_profile": pinned["sensor_profile"].source_record(
                "tables/sensor_profile.parquet"
            ),
            "image_profile": pinned["image_profile"].source_record(
                "tables/image_profile.parquet"
            ),
            "alignment_audit": pinned["alignment_audit"].source_record(
                "reports/alignment_blockers.json"
            ),
            **local_sources,
        }
        result = build_target_audit(
            sensors=pd.read_parquet(
                pinned["sensor_profile"].artifact_path("tables/sensor_profile.parquet")
            ),
            images=pd.read_parquet(
                pinned["image_profile"].artifact_path("tables/image_profile.parquet")
            ),
            alignment_blockers=blockers,
            candidate_definitions=data["target_audit"]["candidates"],
            sources=sources,
        )
        output_root = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
        source_runs = [
            {
                "name": name,
                "run_id": item.run_id,
                "directory": item.relative_directory,
                "artifacts": dict(item.verified_hashes),
            }
            for name, item in pinned.items()
        ]
        input_manifest = [
            item.source_record(path)
            for item in pinned.values()
            for path in sorted(item.verified_hashes)
        ] + [dict(value, source_name=name) for name, value in local_sources.items()]
        resolved = {
            "schema_version": "1.0.0",
            "task": "T2.1",
            "classification": result.blockers["classification"],
            "experiment_config": data,
            "execution": {
                "generated_artifacts_only": True,
                "raw_archives_opened": False,
            },
        }
        run = create_run_context(
            study=str(data["study"]),
            output_root=output_root,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/audit_target.py", *(argv or sys.argv[1:])],
            input_roots=tuple(item.relative_directory for item in pinned.values()),
            package_names=("pandas", "pyarrow", "matplotlib", "numpy", "PyYAML"),
            source_runs=source_runs,
        )
        artifacts = write_target_audit_run(
            result, run=run, resolved_config=resolved, input_manifest=input_manifest
        )
    except (
        ConfigError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "summary": dict(result.summary),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
