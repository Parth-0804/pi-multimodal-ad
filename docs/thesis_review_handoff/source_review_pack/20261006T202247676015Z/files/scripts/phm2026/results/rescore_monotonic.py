#!/usr/bin/env python3
"""Re-score pinned predictions under raw MAE and the organizer's monotonic-MSE.

Reads a pinned prediction table and scores it two ways. Trains nothing, selects
nothing, and therefore cannot leak EXP-F into any decision -- the test rows are
scored only because they already exist in the pinned table.
"""

from __future__ import annotations

# Source-tree entry point; no installed package is required.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3] / "src"))


import argparse
import sys
from pathlib import Path

import pandas as pd

from phm2026.evaluation.monotonic import monotonic_metrics
from phm2026.evaluation.regression import regression_metrics
from phm2026.utils.artifacts import load_pinned_run
from phm2026.utils.config import load_yaml_config
from phm2026.utils.provenance import create_run_context
from phm2026.reporting.common import finalize_run, json_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_monotonic_rescoring.yaml"
    )
    args = parser.parse_args(argv)

    config = load_yaml_config(args.config)
    data = config.mutable_copy()
    pinned = load_pinned_run(
        config.repository_root,
        data["source_runs"]["patchtst"],
        required_artifacts=("tables/predictions.parquet",),
    )
    predictions = pd.read_parquet(pinned.artifact_path("tables/predictions.parquet"))

    run = create_run_context(
        study=data["study"],
        output_root=config.resolve_repository_path(
            data["output_root"], field="output_root"
        ),
        config=config,
        seed=int(data["seed"]),
        command=["scripts/phm2026/results/rescore_monotonic.py", *(argv or sys.argv[1:])],
        input_roots=(pinned.relative_directory,),
        package_names=("numpy", "pandas", "pyarrow", "scikit-learn", "PyYAML"),
        source_runs=[
            {
                "name": "patchtst",
                "run_id": pinned.run_id,
                "directory": pinned.relative_directory,
                "artifacts": dict(pinned.verified_hashes),
            }
        ],
    )
    run.create_layout()

    rows: list[dict[str, object]] = []
    for variant, column in (
        ("raw_top3_mean_pct", "y_true_raw"),
        ("causal_monotonic_top3_mean_pct", "y_true_monotonic"),
    ):
        for (model, split), scoped in predictions.groupby(["model_name", "split"]):
            raw = regression_metrics(scoped[column], scoped.y_pred)
            mono = monotonic_metrics(scoped[column], scoped.y_pred)
            rows.append(
                {
                    "model_name": model,
                    "split": split,
                    "target_variant": variant,
                    "evaluation_level": "experiment_run",
                    "sample_count": raw["sample_count"],
                    "mae": raw["mae"],
                    "mse": raw["mse"],
                    "spearman": raw["spearman"],
                    "monotonic_mse": mono["monotonic_mse"],
                    "monotonic_rmse": mono["monotonic_rmse"],
                    "monotonic_r2": mono["monotonic_r2"],
                    "degeneracy": mono["degeneracy"],
                    "fitted_on_evaluation_set": mono["fitted_on_evaluation_set"],
                }
            )
    table = pd.DataFrame(rows).sort_values(
        ["target_variant", "split", "monotonic_mse"], kind="stable"
    )

    artifacts = []
    config_path = run.write_resolved_config(data)
    artifacts.append(run.artifact(config_path, role="resolved_configuration"))
    for suffix, writer in ((".csv", table.to_csv), (".parquet", table.to_parquet)):
        path = run.run_directory / f"tables/monotonic_rescoring{suffix}"
        writer(path, index=False)
        artifacts.append(run.artifact(path, role="monotonic_rescoring"))

    summary_path = run.run_directory / "reports/monotonic_rescoring.json"
    summary_path.write_text(
        json_text(
            {
                "schema_version": "1.0.0",
                "metric": "MSE after optimal monotonic (isotonic) rescale",
                "fitted_on_evaluation_set": True,
                "note": (
                    "A constant prediction carries no rank information, so no "
                    "monotonic transform can improve it beyond the target mean; "
                    "those rows are labelled with a degeneracy string rather "
                    "than a NaN."
                ),
                "source_run": pinned.run_id,
                "rows": table.to_dict(orient="records"),
            }
        ),
        encoding="utf-8",
    )
    artifacts.append(run.artifact(summary_path, role="summary"))
    finalize_run(run, artifacts)

    print(f"run_directory: {run.run_directory.relative_to(config.repository_root)}")
    with pd.option_context("display.width", 200, "display.max_columns", 30):
        for variant in table.target_variant.unique():
            print(f"\n=== {variant} ===")
            print(
                table[table.target_variant.eq(variant)][
                    ["model_name", "split", "sample_count", "mae", "monotonic_mse",
                     "spearman", "degeneracy"]
                ].to_string(index=False)
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
