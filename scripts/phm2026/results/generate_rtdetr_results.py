#!/usr/bin/env python3
"""Build corrected professor-ready RT-DETR result figures from saved tables."""

from __future__ import annotations

import argparse, json, shutil, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pi_multimodal_ad.reporting.common import (
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
)  # noqa: E402
from pi_multimodal_ad.utils import (
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
    sha256_file,
)  # noqa: E402

RT_ARTIFACTS = (
    "tables/predictions.parquet",
    "tables/run_predictions.parquet",
    "tables/metrics.parquet",
    "tables/training_history.parquet",
    "cache/encoder_features.parquet",
    "reports/environment_device.json",
    "reports/training_summary.json",
)


def _source(frame: pd.DataFrame, run, name: str, artifacts):
    path = run.run_directory / f"tables/plot_source_{name}.csv"
    frame.to_csv(path, index=False)
    artifacts.append(run.artifact(path, role=f"plot_source_{name}"))


def _save(fig, run, name, artifacts):
    for path in save_figure_pair(fig, run.run_directory / f"figures/{name}"):
        artifacts.append(run.artifact(path, role=f"{name}_{path.suffix[1:]}"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_rtdetr_results.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        required = {
            "target": (
                "tables/image_manifest.parquet",
                "tables/run_damage_targets.parquet",
                "reports/target_quality_report.json",
            ),
            "dataset": (
                "tables/model_sample_manifest.parquet",
                "reports/split_validation.json",
            ),
            "naive": ("tables/baseline_metrics.parquet",),
            "rtdetr": RT_ARTIFACTS,
        }
        pins = {
            name: load_pinned_run(
                config.repository_root,
                data["source_runs"][name],
                required_artifacts=paths,
            )
            for name, paths in required.items()
        }
        pred = pd.read_parquet(
            pins["rtdetr"].artifact_path("tables/predictions.parquet")
        )
        runs = pd.read_parquet(
            pins["rtdetr"].artifact_path("tables/run_predictions.parquet")
        )
        metrics = pd.read_parquet(
            pins["rtdetr"].artifact_path("tables/metrics.parquet")
        )
        features = pd.read_parquet(
            pins["rtdetr"].artifact_path("cache/encoder_features.parquet")
        )
        env = json.loads(
            pins["rtdetr"].artifact_path("reports/environment_device.json").read_text()
        )
        training = json.loads(
            pins["rtdetr"].artifact_path("reports/training_summary.json").read_text()
        )
        target_images = pd.read_parquet(
            pins["target"].artifact_path("tables/image_manifest.parquet")
        )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "prediction_count": len(pred),
                        "run_count": len(runs),
                        "target_status": training["target_status"],
                        "would_open_raw": False,
                        "would_write": False,
                    },
                    indent=2,
                )
            )
            return 0
        output = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
        source_runs = [
            {
                "name": name,
                "run_id": pin.run_id,
                "directory": pin.relative_directory,
                "artifacts": dict(pin.verified_hashes),
            }
            for name, pin in pins.items()
        ]
        run = create_run_context(
            study=data["study"],
            output_root=output,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/results/generate_rtdetr_results.py", *(argv or sys.argv[1:])],
            input_roots=tuple(pin.relative_directory for pin in pins.values()),
            source_runs=source_runs,
        )
        run.create_layout()
        apply_academic_style()
        artifacts = []
        cp = run.write_resolved_config(data)
        ip = run.write_input_manifest(
            [
                pin.source_record(path)
                for pin in pins.values()
                for path in sorted(pin.verified_hashes)
            ]
        )
        artifacts += [
            run.artifact(cp, role="resolved_configuration"),
            run.artifact(ip, role="input_manifest"),
        ]
        residual = pred.assign(
            residual=pred.y_pred - pred.y_true_raw,
            absolute_error=lambda d: (d.y_pred - d.y_true_raw).abs(),
        )
        by_run = residual.groupby(["experiment", "run", "split"], as_index=False).agg(
            mae=("absolute_error", "mean"),
            rmse=(
                "residual",
                lambda values: float(np.sqrt(np.mean(np.square(values)))),
            ),
            sample_count=("sample_id", "size"),
        )
        bins = pd.qcut(pred.y_true_raw, q=4, duplicates="drop")
        by_range = (
            residual.assign(damage_range=bins.astype(str))
            .groupby(["split", "damage_range"], observed=True, as_index=False)
            .agg(mae=("absolute_error", "mean"), sample_count=("sample_id", "size"))
        )
        sources = {
            "run_trajectory": runs,
            "errors_by_run": by_run,
            "errors_by_damage_range": by_range,
            "model_size_device": pd.DataFrame(
                [
                    {
                        "component": "frozen_encoder",
                        "parameters": env["encoder_parameters"],
                        "device": env["device_name"],
                    },
                    {
                        "component": "regression_head",
                        "parameters": training["head_parameter_count"],
                        "device": env["device_name"],
                    },
                ]
            ),
            "latency_summary": pd.DataFrame(
                [
                    {
                        "median_ms": features.feature_latency_ms.median(),
                        "p95_ms": features.feature_latency_ms.quantile(0.95),
                        "maximum_ms": features.feature_latency_ms.max(),
                    }
                ]
            ),
            "status_banner": pd.DataFrame(
                [
                    {
                        "status": training["target_status"],
                        "physical_validation": "pending_human_review",
                        "organizer_ground_truth": False,
                    }
                ]
            ),
        }
        figures = {}
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
        for axis, (experiment, scoped) in zip(
            axes, runs.groupby("experiment"), strict=True
        ):
            axis.plot(
                scoped.run,
                scoped.y_true_raw_top3_mean,
                marker="o",
                label="true pseudo-target",
            )
            axis.plot(
                scoped.run,
                scoped.y_pred_raw_top3_mean,
                marker="s",
                label="RT-DETR-derived",
            )
            axis.set(title=experiment, xlabel="Run")
            axis.legend(fontsize=8)
        axes[0].set_ylabel("Top-3 candidate area (%)")
        fig.suptitle("Run-level provisional target trajectory")
        fig.tight_layout()
        figures["run_trajectory"] = fig
        fig, ax = plt.subplots(figsize=(10, 5))
        labels = by_run.experiment + " R" + by_run.run.astype(str)
        ax.bar(labels, by_run.mae, color=ACADEMIC_COLORS[0])
        ax.set(
            title="RT-DETR-derived MAE by experiment/run",
            ylabel="MAE (provisional percentage points)",
        )
        ax.tick_params(axis="x", rotation=45)
        figures["errors_by_run"] = fig
        fig, ax = plt.subplots(figsize=(10, 5))
        for split, scoped in by_range.groupby("split"):
            ax.plot(scoped.damage_range, scoped.mae, marker="o", label=split)
        ax.set(
            title="Error by provisional target range",
            xlabel="Target quartile interval (%)",
            ylabel="MAE (percentage points)",
        )
        ax.tick_params(axis="x", rotation=25)
        ax.legend()
        fig.tight_layout()
        figures["errors_by_damage_range"] = fig
        fig, ax = plt.subplots(figsize=(8, 4.8))
        size = sources["model_size_device"]
        ax.bar(
            size.component,
            size.parameters,
            color=[ACADEMIC_COLORS[0], ACADEMIC_COLORS[2]],
        )
        ax.set_yscale("log")
        ax.set(
            title=f"Model size on {env['device_name']}", ylabel="Parameters (log scale)"
        )
        figures["model_size_device"] = fig
        fig, ax = plt.subplots(figsize=(8, 4.2))
        latency = sources["latency_summary"].iloc[0]
        ax.bar(
            ["median", "p95", "max/first-call"],
            [latency.median_ms, latency.p95_ms, latency.maximum_ms],
            color=ACADEMIC_COLORS[:3],
        )
        ax.set(title="Frozen encoder latency summary", ylabel="Milliseconds/image")
        figures["latency_summary"] = fig
        fig, ax = plt.subplots(figsize=(12, 2.8))
        ax.axis("off")
        ax.text(
            0.5,
            0.62,
            "PROVISIONAL ENGINEERING BASELINE",
            ha="center",
            va="center",
            fontsize=24,
            weight="bold",
            color="#B64D5B",
            transform=ax.transAxes,
        )
        ax.text(
            0.5,
            0.32,
            "Automated pseudo-target pending human mask review — not validated physical spall performance",
            ha="center",
            va="center",
            fontsize=12,
            transform=ax.transAxes,
        )
        figures["status_banner"] = fig
        for name, frame in sources.items():
            _source(frame, run, name, artifacts)
            _save(figures[name], run, name, artifacts)
        selected = pd.concat(
            [
                residual.nsmallest(4, "absolute_error"),
                residual.nlargest(4, "absolute_error"),
            ]
        )
        overlay_root = pins["target"].directory / "overlays"
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        for axis, (_, row) in zip(axes.flat, selected.iterrows(), strict=True):
            axis.imshow(Image.open(overlay_root / f"{row.image_id}.jpg"))
            axis.set_title(
                f"{row.experiment} R{row.run} T{row.tooth_id}\ntrue={row.y_true_raw:.2f} pred={row.y_pred:.2f} |e|={row.absolute_error:.2f}",
                fontsize=8,
            )
            axis.axis("off")
        fig.suptitle(
            "Best (top) and worst (bottom) provisional predictions with target masks"
        )
        fig.tight_layout()
        name = "best_worst_target_overlays"
        _source(
            selected[
                [
                    "image_id",
                    "experiment",
                    "run",
                    "tooth_id",
                    "y_true_raw",
                    "y_pred",
                    "absolute_error",
                ]
            ],
            run,
            name,
            artifacts,
        )
        _save(fig, run, name, artifacts)
        quantiles = (
            target_images[target_images.run.notna()]
            .sort_values("damage_candidate_area_pct")
            .iloc[
                np.linspace(
                    0, len(target_images[target_images.run.notna()]) - 1, 6, dtype=int
                )
            ]
        )
        fig, axes = plt.subplots(2, 3, figsize=(14, 8))
        for axis, (_, row) in zip(axes.flat, quantiles.iterrows(), strict=True):
            axis.imshow(Image.open(overlay_root / f"{row.image_id}.jpg"))
            axis.set_title(
                f"{row.experiment} R{int(row.run)} T{row.tooth_id}: {row.damage_candidate_area_pct:.2f}%",
                fontsize=9,
            )
            axis.axis("off")
        fig.suptitle("Provisional target overlays spanning measured values")
        fig.tight_layout()
        name = "target_overlay_examples"
        _source(
            quantiles[
                [
                    "image_id",
                    "experiment",
                    "run",
                    "tooth_id",
                    "damage_candidate_area_pct",
                ]
            ],
            run,
            name,
            artifacts,
        )
        _save(fig, run, name, artifacts)
        index = [
            "# RT-DETR result figure index",
            "",
            "> All target values and model metrics are provisional pending human review.",
            "",
        ]
        for name in (*sources, "best_worst_target_overlays", "target_overlay_examples"):
            index += [
                f"- `{name}`: `tables/plot_source_{name}.csv`, `figures/{name}.png`, `figures/{name}.svg`.",
                "",
            ]
        index_path = run.run_directory / "reports/figure_index.md"
        index_path.write_text("\n".join(index), encoding="utf-8")
        artifacts.append(run.artifact(index_path, role="figure_index"))
        test_metric = metrics[
            (metrics.evaluation_level == "image_view") & (metrics.experiment == "EXP-F")
        ].iloc[0]
        naive = pd.read_parquet(
            pins["naive"].artifact_path("tables/baseline_metrics.parquet")
        )
        naive_test = naive[
            (naive.model_name == "training_mean") & (naive.experiment == "EXP-F")
        ].iloc[0]
        storage = sum(
            path.stat().st_size
            for pin in pins.values()
            for path in pin.directory.rglob("*")
            if path.is_file()
        )
        report = f"""# Final PHM T2 and RT-DETR engineering report\n\n> **PROVISIONAL PSEUDO-TARGET — pending human mask validation; not organizer ground truth or validated physical spall performance.**\n\n## Official formulation\n\nThe official challenge requires a self-defined scalar from 28 post-run tooth images and a later sensor-only estimator. This work estimates end-of-run current damage state. Six hours is typical run/inspection/output cadence, not a six-hour-ahead horizon. Pairing uses verified experiment/run/tooth identity.\n\n## Target and dataset\n\nTarget version `phm2026_image_damage_v2`: elongated dark candidate pixels / normalized visible-flank ROI, maximum across views per tooth, raw top-3 tooth mean per run, plus causal cumulative-maximum alternative. All 1,311 images decoded; 560 tooth/run records and 20 run targets; 0 decode exclusions; 560 human reviews pending. EXP-A/B close-up protocol differs from EXP-F canonical views.\n\nThe image baseline has 995 view samples: 448 EXP-B train, 323 EXP-A validation, 224 untouched EXP-F test, with zero run/near-duplicate cross-split violations. T2.2 also records 7,124 one-minute HDF5 members and 20 run windows; compact sensor features were deliberately not fabricated or extracted in this image task.\n\n## Baselines and RT-DETR\n\nTraining-mean EXP-F MAE: {naive_test.mae:.3f} percentage points. The frozen RT-DETR-L encoder (32,148,140 parameters) plus 98,689-parameter head early-stopped after {training['epochs_completed']} epochs; best epoch {training['best_epoch']}. EXP-F image MAE {test_metric.mae:.3f}, RMSE {test_metric.rmse:.3f}, Spearman {test_metric.spearman:.3f}, R² {test_metric.r2:.3f}. Negative R² and out-of-range predictions show weak cross-protocol calibration despite improved MAE.\n\nPreprocessing: original 1440×2560×3 image → Ultralytics scale-fill 640×640 → RGB BCHW float32/255 → 80×80, 40×40, 20×20 256-channel maps → pooled 768-vector → scalar. Median encoder latency {features.feature_latency_ms.median():.2f} ms/image on {env['device_name']}.\n\n## Limitations and review\n\nMasks can include shadows/edges; no organizer labels or verified boxes exist; metrics quantify pseudo-label emulation only. Human reviewers must accept/reject/correct every selected overlay and assess A/B-versus-F acquisition bias before target freezing. No PatchTST, sensor-model training, fusion, leaderboard work, or official test/validation modelling occurred.\n\n## Reproduce\n\n```bash\nma_thesis_env/bin/python -B scripts/targets/derive_image_targets.py\nma_thesis_env/bin/python -B scripts/features/build_model_dataset.py\nma_thesis_env/bin/python -B scripts/results/evaluate_naive_baselines.py\nma_thesis_env/bin/python -B scripts/training/train_rtdetr_regression.py\nma_thesis_env/bin/python -B scripts/results/generate_rtdetr_results.py\n```\n\nExact source runs/hashes are in `config/resolved_config.yaml` and `manifests/inputs.json`; figure sources are indexed in `reports/figure_index.md`. Referenced source-run storage at report time: {storage/1073741824:.3f} GiB. Next gate before PatchTST: complete human target review, revise/freeze target, then run a separately bounded streaming sensor-feature build.\n"""
        report_path = run.run_directory / "reports/final_overnight_report.md"
        report_path.write_text(report, encoding="utf-8")
        artifacts.append(run.artifact(report_path, role="final_overnight_report"))
        summary_path = run.run_directory / "reports/result_summary.json"
        summary_path.write_text(
            json_text(
                {
                    "target_status": training["target_status"],
                    "target_version": "phm2026_image_damage_v2",
                    "sample_counts": {"train": 448, "validation": 323, "test": 224},
                    "exp_f_image_mae": test_metric.mae,
                    "exp_f_image_rmse": test_metric.rmse,
                    "exp_f_image_r2": test_metric.r2,
                    "naive_exp_f_mae": naive_test.mae,
                    "raw_archives_opened": False,
                    "training_rerun": False,
                }
            ),
            encoding="utf-8",
        )
        artifacts.append(run.artifact(summary_path, role="result_summary"))
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
                "report": "reports/final_overnight_report.md",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
