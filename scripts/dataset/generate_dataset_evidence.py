#!/usr/bin/env python3
"""Generate professor-ready dataset figures from pinned D artifacts only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from pi_multimodal_ad.reporting.dataset_evidence import (  # noqa: E402
    build_dataset_evidence,
    write_dataset_evidence_run,
)
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_meeting_evidence.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        specifications = data.get("source_runs")
        if not isinstance(specifications, dict):
            raise ConfigError("source_runs must be a mapping")
        requirements = {
            "asset_inventory": (
                "tables/asset_inventory.parquet",
                "reports/summary.json",
            ),
            "sensor_profile": (
                "tables/hdf5_members.parquet",
                "tables/sensor_profile.parquet",
                "reports/sensor_summary.json",
            ),
            "image_profile": (
                "tables/image_profile.parquet",
                "reports/image_summary.json",
            ),
            "alignment_audit": ("reports/alignment_blockers.json",),
            "professor_description": (
                "tables/dataset_at_a_glance.csv",
                "reports/professor_dataset_description.md",
            ),
        }
        pinned = {
            name: load_pinned_run(
                config.repository_root, specifications[name], required_artifacts=paths
            )
            for name, paths in requirements.items()
        }
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "source_runs": {
                            name: value.run_id for name, value in pinned.items()
                        },
                        "would_open_raw_archives": False,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        sources = {
            "asset_inventory": pinned["asset_inventory"].source_record(
                "tables/asset_inventory.parquet"
            ),
            "sensor_profile": pinned["sensor_profile"].source_record(
                "tables/sensor_profile.parquet"
            ),
            "image_profile": pinned["image_profile"].source_record(
                "tables/image_profile.parquet"
            ),
            "alignment_audit": pinned["alignment_audit"].source_record(
                "reports/alignment_blockers.json"
            ),
            "professor_description": pinned["professor_description"].source_record(
                "tables/dataset_at_a_glance.csv"
            ),
        }
        result = build_dataset_evidence(
            assets=pd.read_parquet(
                pinned["asset_inventory"].artifact_path(
                    "tables/asset_inventory.parquet"
                )
            ),
            hdf5_members=pd.read_parquet(
                pinned["sensor_profile"].artifact_path("tables/hdf5_members.parquet")
            ),
            sensors=pd.read_parquet(
                pinned["sensor_profile"].artifact_path("tables/sensor_profile.parquet")
            ),
            images=pd.read_parquet(
                pinned["image_profile"].artifact_path("tables/image_profile.parquet")
            ),
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
        ]
        resolved = {
            "schema_version": "1.0.0",
            "task": "dataset_definition_figures",
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
            command=["scripts/dataset/generate_dataset_evidence.py", *(argv or sys.argv[1:])],
            input_roots=tuple(item.relative_directory for item in pinned.values()),
            package_names=("pandas", "pyarrow", "matplotlib", "numpy", "PyYAML"),
            source_runs=source_runs,
        )
        artifacts = write_dataset_evidence_run(
            result, run=run, resolved_config=resolved, input_manifest=input_manifest
        )
    except (ConfigError, KeyError, OSError, ValueError) as exc:
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
