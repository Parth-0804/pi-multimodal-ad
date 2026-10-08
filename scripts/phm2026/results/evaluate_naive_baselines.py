#!/usr/bin/env python3
"""Run T2.3 inference-safe naive baselines on the persisted provisional split."""

from __future__ import annotations

import argparse, json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pi_multimodal_ad.evaluation.regression import (
    metric_table,
    naive_predictions,
)  # noqa: E402
from pi_multimodal_ad.reporting.common import finalize_run, json_text  # noqa: E402
from pi_multimodal_ad.utils import (
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_evaluation.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        pinned = load_pinned_run(
            config.repository_root,
            data["source_run"],
            required_artifacts=(
                "tables/model_sample_manifest.parquet",
                "tables/split_manifest.parquet",
                "reports/split_validation.json",
            ),
        )
        samples = pd.read_parquet(
            pinned.artifact_path("tables/model_sample_manifest.parquet")
        )
        predictions = naive_predictions(samples)
        metrics = metric_table(
            predictions,
            repetitions=int(data["bootstrap_repetitions"]),
            seed=int(data["seed"]),
        )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "prediction_count": len(predictions),
                        "metric_row_count": len(metrics),
                        "would_write": False,
                    },
                    indent=2,
                )
            )
            return 0
        output = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
        run = create_run_context(
            study=data["study"],
            output_root=output,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/results/evaluate_naive_baselines.py", *(argv or sys.argv[1:])],
            input_roots=(pinned.relative_directory,),
            source_runs=(
                {
                    "name": "model_dataset",
                    "run_id": pinned.run_id,
                    "directory": pinned.relative_directory,
                    "artifacts": dict(pinned.verified_hashes),
                },
            ),
        )
        run.create_layout()
        artifacts = []
        cp = run.write_resolved_config(data)
        ip = run.write_input_manifest(
            [pinned.source_record(path) for path in sorted(pinned.verified_hashes)]
        )
        artifacts += [
            run.artifact(cp, role="resolved_configuration"),
            run.artifact(ip, role="input_manifest"),
        ]
        for name, frame in (
            ("baseline_predictions", predictions),
            ("baseline_metrics", metrics),
        ):
            for suffix in ("csv", "parquet"):
                path = run.run_directory / f"tables/{name}.{suffix}"
                (
                    frame.to_csv(path, index=False)
                    if suffix == "csv"
                    else frame.to_parquet(path, index=False)
                )
                artifacts.append(run.artifact(path, role=name))
        contract = """# Evaluation contract

Per-image-view metrics: MAE, RMSE, median absolute error and bias in percentage points of the provisional visible-flank candidate-area ratio; Spearman correlation; R² only with sufficient sample count/variance. Run-trajectory evaluation additionally uses MSE, Spearman/Kendall and monotonicity violations after versioned image→tooth→run aggregation.

All thresholds/scalers/baselines are fitted on EXP-B training only. EXP-A is validation and EXP-F is untouched test. Previous-run persistence is not run here because an image-derived previous target is unavailable in challenge sensor-only test inference. Results are provisional pseudo-target fidelity, not validated physical-spall accuracy.
"""
        validity = """# Real-world validity checklist

- Physical calibration and human mask validation: **not complete**.
- Unit: provisional percentage points of visible flank candidate area.
- Inference availability: the RT-DETR image model requires post-run images and is a target-automation baseline; the future challenge sensor model must not use images at inference.
- Protocol shift: EXP-A/B close-ups versus EXP-F canonical views requires explicit review.
- Maintenance threshold/actionability/false-alarm cost: unresolved.
- No elapsed-time proxy, test-statistic scaling, or random neighboring-image split is used.
"""
        schema = {
            "schema_version": "1.0.0",
            "required_columns": list(predictions.columns),
            "target_verification_status": "provisional_pending_human_review",
            "persistence_status": "not_run_not_inference_safe_for_sensor_only_challenge_test",
        }
        for name, text in (
            ("evaluation_contract.md", contract),
            ("real_world_validity_checklist.md", validity),
        ):
            path = run.run_directory / f"reports/{name}"
            path.write_text(text, encoding="utf-8")
            artifacts.append(run.artifact(path, role=Path(name).stem))
        schema_path = run.run_directory / "reports/prediction_result_schema.json"
        schema_path.write_text(json_text(schema), encoding="utf-8")
        artifacts.append(run.artifact(schema_path, role="prediction_result_schema"))
        artifacts = finalize_run(run, artifacts)
    except (ConfigError, KeyError, OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "run_directory": run.run_directory.relative_to(
                    run.repository_root
                ).as_posix(),
                "artifact_count": len(artifacts) + 1,
                "prediction_count": len(predictions),
                "metrics": metrics.to_dict(orient="records"),
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
