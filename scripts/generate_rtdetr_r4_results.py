#!/usr/bin/env python3
"""Create the hash-pinned professor-facing R4 RT-DETR result package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pi_multimodal_ad.reporting.common import (  # noqa: E402
    ACADEMIC_COLORS,
    apply_academic_style,
    finalize_run,
    json_text,
    save_figure_pair,
)
from pi_multimodal_ad.utils import (  # noqa: E402
    ConfigError,
    create_run_context,
    load_pinned_run,
    load_yaml_config,
)


def _write_frame(frame: pd.DataFrame, stem: Path) -> list[Path]:
    csv = stem.with_suffix(".csv")
    parquet = stem.with_suffix(".parquet")
    frame.to_csv(csv, index=False)
    frame.to_parquet(parquet, index=False)
    return [csv, parquet]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", default="configs/experiments/phm2026_rtdetr_r4_results.yaml"
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_yaml_config(args.config)
        data = config.mutable_copy()
        pins = {
            name: load_pinned_run(
                config.repository_root,
                specification,
                required_artifacts=tuple(specification["artifacts"]),
            )
            for name, specification in data["source_runs"].items()
        }
        target_images = pd.read_parquet(
            pins["target"].artifact_path("tables/image_manifest.parquet")
        )
        teeth = pd.read_parquet(
            pins["target"].artifact_path("tables/per_tooth_damage.parquet")
        )
        run_targets = pd.read_parquet(
            pins["target"].artifact_path("tables/run_damage_targets.parquet")
        )
        samples = pd.read_parquet(
            pins["dataset"].artifact_path("tables/model_sample_manifest.parquet")
        )
        pseudo_quality = json.loads(
            pins["pseudo_boxes"]
            .artifact_path("reports/annotation_quality.json")
            .read_text()
        )
        model_a_detection = pd.read_parquet(
            pins["detector"].artifact_path("tables/detection_metrics.parquet")
        )
        model_b_detection = pd.read_parquet(
            pins["multitask"].artifact_path("tables/detection_metrics.parquet")
        )
        comparison = pd.read_parquet(
            pins["multitask"].artifact_path(
                "tables/level_matched_model_comparison.parquet"
            )
        )
        model_b_environment = json.loads(
            pins["multitask"]
            .artifact_path("reports/environment_device.json")
            .read_text()
        )
        split_counts = samples.groupby(["split", "experiment"]).size().to_dict()
        expected = {
            ("train", "EXP-B"): 448,
            ("validation", "EXP-A"): 323,
            ("test", "EXP-F"): 224,
        }
        if split_counts != expected:
            raise ConfigError(f"final package split mismatch: {split_counts}")
        funnel = pd.DataFrame(
            [
                {"stage": "discovered source images", "count": len(target_images)},
                {"stage": "model-ready image views", "count": len(samples)},
                {"stage": "tooth/run records", "count": len(teeth)},
                {"stage": "run targets", "count": len(run_targets)},
            ]
        )
        expected_funnel = [1311, 995, 560, 20]
        if funnel["count"].tolist() != expected_funnel:
            raise ConfigError(
                f"final package funnel mismatch: {funnel['count'].tolist()}"
            )
        if pseudo_quality["box_count"] != 30628:
            raise ConfigError("pseudo-box count mismatch")
        if int(model_b_environment["exp_f_test_evaluation_passes"]) != 1:
            raise ConfigError("multitask EXP-F evaluation-count mismatch")
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "funnel": expected_funnel,
                        "split_counts": {
                            f"{split}/{experiment}": int(count)
                            for (split, experiment), count in split_counts.items()
                        },
                        "pseudo_box_count": pseudo_quality["box_count"],
                        "model_a_run": pins["detector"].run_id,
                        "model_b_run": pins["multitask"].run_id,
                        "would_write": False,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        output_root = config.resolve_repository_path(
            args.output_dir or data["output_root"], field="output_root"
        )
        source_runs = [
            {
                "name": name,
                "run_id": pinned.run_id,
                "directory": pinned.relative_directory,
                "artifacts": dict(pinned.verified_hashes),
            }
            for name, pinned in pins.items()
        ]
        run = create_run_context(
            study=data["study"],
            output_root=output_root,
            config=config,
            seed=int(data["seed"]),
            command=["scripts/generate_rtdetr_r4_results.py", *(argv or sys.argv[1:])],
            input_roots=tuple(pinned.relative_directory for pinned in pins.values()),
            package_names=("pandas", "pyarrow", "matplotlib", "PyYAML"),
            source_runs=source_runs,
        )
        run.create_layout()
        artifacts = []
        resolved = {
            "schema_version": "1.0.0",
            "status": "PROVISIONAL_PSEUDO_LABEL_AGREEMENT_ONLY",
            "source_run_ids": {name: value.run_id for name, value in pins.items()},
            "funnel": funnel.to_dict(orient="records"),
            "split_counts": {
                f"{split}/{experiment}": int(count)
                for (split, experiment), count in split_counts.items()
            },
            "exp_f_used_for_tuning": False,
            "multitask_exp_f_evaluation_passes": 1,
        }
        config_path = run.write_resolved_config(resolved)
        inputs = [
            pinned.source_record(path)
            for pinned in pins.values()
            for path in sorted(pinned.verified_hashes)
        ]
        input_path = run.write_input_manifest(inputs)
        artifacts.extend(
            [
                run.artifact(config_path, role="resolved_configuration"),
                run.artifact(input_path, role="input_manifest"),
            ]
        )
        detector_rows = []
        for model_name, frame in (
            ("genuine_rtdetr_detector", model_a_detection),
            ("multitask_rtdetr_detection_head", model_b_detection),
        ):
            overall = frame[frame.scope.eq("all")].iloc[0].to_dict()
            overall["model_name"] = model_name
            detector_rows.append(overall)
        detection_comparison = pd.DataFrame(detector_rows)
        artifact_index = pd.DataFrame(
            [
                {
                    "source_name": name,
                    "run_id": pinned.run_id,
                    "run_directory": pinned.relative_directory,
                    "artifact_path": path,
                    "sha256": hash_value,
                }
                for name, pinned in pins.items()
                for path, hash_value in sorted(pinned.verified_hashes.items())
            ]
        )
        tables = {
            "dataset_annotation_funnel": funnel,
            "detection_model_comparison": detection_comparison,
            "level_matched_scalar_comparison": comparison,
            "source_artifact_index": artifact_index,
        }
        for name, frame in tables.items():
            for path in _write_frame(frame, run.run_directory / "tables" / name):
                artifacts.append(run.artifact(path, role=name))
        apply_academic_style()
        scoped = comparison[
            comparison.split.eq("test")
            & comparison.evaluation_level.isin(["image_view", "run_raw_top3"])
        ].copy()
        plot_source_paths = _write_frame(
            scoped,
            run.run_directory / "tables/plot_source_exp_f_level_matched_mae",
        )
        artifacts.extend(
            run.artifact(path, role="plot_source_exp_f_level_matched_mae")
            for path in plot_source_paths
        )
        fig, ax = plt.subplots(figsize=(11, 5))
        labels = scoped.model_name + "\n" + scoped.evaluation_level
        ax.bar(labels, scoped.mae, color=ACADEMIC_COLORS[0])
        ax.set(
            title="EXP-F level-matched scalar MAE",
            ylabel="MAE (percentage points of provisional candidate area)",
        )
        ax.tick_params(axis="x", rotation=35, labelsize=7)
        for path in save_figure_pair(
            fig, run.run_directory / "figures/exp_f_level_matched_mae"
        ):
            artifacts.append(run.artifact(path, role="exp_f_level_matched_mae"))

        paths = {
            "pseudo": pins["pseudo_boxes"].relative_directory,
            "detector": pins["detector"].relative_directory,
            "multitask": pins["multitask"].relative_directory,
        }
        figure_rows = [
            (
                "Dataset/annotation funnel",
                paths["pseudo"] + "/figures/dataset_annotation_funnel.png",
                paths["pseudo"] + "/tables/plot_source_dataset_annotation_funnel.csv",
            ),
            (
                "Pseudo-box counts by split/view",
                paths["pseudo"] + "/figures/box_count_by_split_view_role.png",
                paths["pseudo"]
                + "/tables/plot_source_box_count_by_split_view_role.csv",
            ),
            (
                "Pseudo-box area distribution",
                paths["pseudo"] + "/figures/box_area_distribution.png",
                paths["pseudo"] + "/tables/plot_source_box_area_distribution.csv",
            ),
            (
                "Deterministic annotation contact sheet",
                paths["pseudo"] + "/figures/annotation_contact_sheet.png",
                paths["pseudo"] + "/tables/plot_source_annotation_contact_sheet.csv",
            ),
            (
                "Model A training/validation losses",
                paths["detector"] + "/figures/training_validation_losses.png",
                paths["detector"]
                + "/tables/plot_source_training_validation_losses.csv",
            ),
            (
                "Model A precision/recall",
                paths["detector"] + "/figures/precision_recall_curve.png",
                paths["detector"] + "/tables/plot_source_precision_recall_curve.csv",
            ),
            (
                "Model A AP by IoU",
                paths["detector"] + "/figures/map_by_iou_threshold.png",
                paths["detector"] + "/tables/plot_source_map_by_iou_threshold.csv",
            ),
            (
                "Model A deterministic detection outcomes",
                paths["detector"] + "/figures/deterministic_detection_examples.png",
                paths["detector"] + "/tables/deterministic_examples.csv",
            ),
            (
                "Multitask architecture/tensors",
                paths["multitask"] + "/figures/architecture_tensor_shapes.png",
                paths["multitask"] + "/tables/tensor_shapes.csv",
            ),
            (
                "Multitask losses",
                paths["multitask"] + "/figures/training_validation_losses.png",
                paths["multitask"]
                + "/tables/plot_source_training_validation_losses.csv",
            ),
            (
                "Multitask precision/recall",
                paths["multitask"] + "/figures/precision_recall_curve.png",
                paths["multitask"] + "/tables/plot_source_precision_recall_curve.csv",
            ),
            (
                "Multitask AP by IoU",
                paths["multitask"] + "/figures/map_by_iou_threshold.png",
                paths["multitask"] + "/tables/plot_source_map_by_iou_threshold.csv",
            ),
            (
                "Multitask prediction vs target",
                paths["multitask"] + "/figures/prediction_vs_target.png",
                paths["multitask"] + "/tables/plot_source_prediction_vs_target.csv",
            ),
            (
                "Multitask residual distribution",
                paths["multitask"] + "/figures/residual_distribution.png",
                paths["multitask"] + "/tables/plot_source_residual_distribution.csv",
            ),
            (
                "Multitask residual vs prediction",
                paths["multitask"] + "/figures/residual_vs_prediction.png",
                paths["multitask"] + "/tables/plot_source_residual_vs_prediction.csv",
            ),
            (
                "EXP-F run trajectory",
                paths["multitask"] + "/figures/exp_f_run_trajectory.png",
                paths["multitask"] + "/tables/plot_source_exp_f_run_trajectory.csv",
            ),
            (
                "Model B deterministic detection outcomes",
                paths["multitask"] + "/figures/deterministic_detection_examples.png",
                paths["multitask"] + "/tables/deterministic_examples.csv",
            ),
            (
                "Multitask latency",
                paths["multitask"] + "/figures/latency_distribution.png",
                paths["multitask"] + "/tables/plot_source_latency_distribution.csv",
            ),
            (
                "Final level-matched MAE comparison",
                run.run_directory.relative_to(run.repository_root).as_posix()
                + "/figures/exp_f_level_matched_mae.png",
                run.run_directory.relative_to(run.repository_root).as_posix()
                + "/tables/plot_source_exp_f_level_matched_mae.csv",
            ),
        ]
        figure_index = (
            "# R4 figure index\n\nAll numerical plots are provisional pseudo-label agreement evidence. PNG files have matching SVG files unless the item is a raster contact sheet/montage.\n\n"
            + "\n".join(
                f"- **{title}:** `{figure}`; source `{source}`."
                for title, figure, source in figure_rows
            )
            + "\n"
        )
        figure_index_path = run.run_directory / "reports/FIGURE_INDEX.md"
        figure_index_path.write_text(figure_index, encoding="utf-8")
        artifacts.append(run.artifact(figure_index_path, role="figure_index"))

        a = detection_comparison.set_index("model_name")
        b = comparison[
            comparison.split.eq("test")
            & comparison.model_name.eq("multitask_rtdetr_detector_scalar_head")
        ].set_index("evaluation_level")
        report = f"""# Professor report: genuine and multitask RT-DETR on PHM images

> **All masks, boxes, and scalar targets in this package are provisional pseudo-labels pending expert review. Detection metrics measure pseudo-label agreement; scalar metrics measure pseudo-target agreement. Neither is validated physical-spall performance.**

## Question-first summary

**What entered the models?** Exactly 995 post-run gear-tooth image views: EXP-B 448 for training, EXP-A 323 for validation/model selection, and EXP-F 224 for the single held-out test. Images were decoded from the one bounded versioned cache and scale-filled to `B×3×640×640` RGB float tensors. Sensor data was not used.

**What was predicted?** Model A predicted one-class `damage_candidate` boxes/classes/confidences. Model B retained those genuine RT-DETR outputs and added one scalar per image from the shared layer-27 encoder feature. The scalar is the exact pinned `phm2026_image_damage_v2` candidate-area percentage, not organizer ground truth.

**What was comparison truth?** Pseudo-boxes were connected components from the deterministic mask replay inside the visible-flank ROI. Per-view scalar predictions were compared with the corresponding provisional candidate-area value. Multiple views of a tooth aggregate by maximum; 28 tooth values aggregate by the mean of the three largest. A causal cumulative maximum is reported separately. The task estimates the current state after a run, not six-hour-ahead damage.

**Was the split random?** No. It was persisted before these models: EXP-B train / EXP-A validation / EXP-F test, with no run, inspection, tooth group, or known near-duplicate group crossing. EXP-F was not used for tuning.

## Traceability and count reduction

The exact evidence funnel is 1,311 discovered JPGs → 995 model-ready views → 560 tooth/run records → 20 run targets. Extra EXP-A/B close-ups are combined at tooth level; excluded baseline/break-in/unpaired records never become model samples. EXP-F is a canonical-view-only acquisition protocol, so it is also a domain shift.

The pseudo-box run retained {int(pseudo_quality['box_count']):,} boxes over all 995 images, with zero negative images and zero whole-ROI boxes. This dense all-positive result is a central scientific limitation: the heuristic frequently describes texture/surface candidates rather than expert-confirmed spalls.

## Genuine detector result (Model A)

The real RT-DETR-L detection architecture was fine-tuned; this was not frozen pooled-feature regression. EXP-A selected confidence 0.60, but every validation threshold had zero true positives. The one EXP-F pass produced TP=0, FP=0, FN=9,883 at that operating point, mAP@0.50={a.loc['genuine_rtdetr_detector','map50']:.6f}, and mAP@0.50:0.95={a.loc['genuine_rtdetr_detector','map50_95']:.6f}. This is a valid negative result.

## Multitask result (Model B)

The multitask model jointly optimized the standard Ultralytics RT-DETR detection loss and a SmoothL1 scalar loss. Encoder layer 27 (`B×256×20×20`) feeds a global-pool 256→128→1 head without detachment. A train-only shared-gradient ratio selected λ={model_b_environment['lambda_selection']['lambda_regression']:.6f}. EXP-A early stopping selected epoch {int(model_b_environment['best_epoch'])}; EXP-F was then evaluated once.

At EXP-A-selected confidence 0.01, EXP-F detection yielded precision={a.loc['multitask_rtdetr_detection_head','precision']:.6f}, recall={a.loc['multitask_rtdetr_detection_head','recall']:.6f}, F1={a.loc['multitask_rtdetr_detection_head','f1']:.6f}, mAP@0.50={a.loc['multitask_rtdetr_detection_head','map50']:.6f}, and mAP@0.50:0.95={a.loc['multitask_rtdetr_detection_head','map50_95']:.6f}. It therefore did not solve the dense pseudo-box task.

Scalar EXP-F results were view MAE={b.loc['image_view','mae']:.6f} percentage points (N={int(b.loc['image_view','sample_count'])}, run-grouped 95% bootstrap interval {b.loc['image_view','mae_run_grouped_ci95_low']:.6f}–{b.loc['image_view','mae_run_grouped_ci95_high']:.6f}), RMSE={b.loc['image_view','rmse']:.6f}, Spearman={b.loc['image_view','spearman']:.6f}, and R²={b.loc['image_view','r2']:.6f}. Raw run-top-3 MAE was {b.loc['run_raw_top3','mae']:.6f} pp (N=8); causal-monotonic run MAE was {b.loc['run_monotonic_top3','mae']:.6f} pp (N=8).

At image/view level, the multitask MAE (0.733) is lower than training mean (1.020), training median (1.203), and earlier frozen-encoder RT-DETR regression (0.894). At raw run level, the earlier frozen model is lower (1.347) than multitask (1.627); therefore no blanket improvement claim is supported. Frozen-model confidence intervals were not recomputed, and all results depend on the same provisional pseudo-target.

## Reproducibility, resources, and limitations

Model A best checkpoint: `{pins['detector'].verified_hashes['checkpoints/best_detector.pt']}`. Model B best checkpoint: `{pins['multitask'].verified_hashes['checkpoints/best_multitask.pt']}`. Model B trained 160.62 seconds on a Tesla T4, peaked at {int(model_b_environment['peak_cuda_memory_allocated_bytes']):,} CUDA bytes, and retained best/last checkpoints only. PyTorch warned that CUDA grid-sampler backward is not bitwise deterministic; fixed seeds and persisted splits do not remove that kernel limitation.

Human/expert review must verify the ROI, mask, boxes, per-tooth values, and failure cases before these values can support physical-damage claims. The detector's near-zero pseudo-label agreement and all-positive/dense annotation pattern are evidence against presenting it as a successful damage detector. Generic COCO classes were never reinterpreted as damage. No PatchTST, sensor features, fusion, leaderboard, or official test modeling was performed.

See `reports/FIGURE_INDEX.md`, `tables/source_artifact_index.csv`, and the input/output manifests for exact evidence lineage.
"""
        report_path = run.run_directory / "reports/PROFESSOR_R4_RTDETR_REPORT.md"
        report_path.write_text(report, encoding="utf-8")
        artifacts.append(run.artifact(report_path, role="professor_report"))
        summary = {
            "status": "PROVISIONAL_PSEUDO_LABEL_AGREEMENT_ONLY",
            "source_image_count": 1311,
            "model_sample_count": 995,
            "tooth_run_count": 560,
            "run_target_count": 20,
            "split": {
                "train": "EXP-B/448",
                "validation": "EXP-A/323",
                "test": "EXP-F/224",
            },
            "pseudo_box_count": int(pseudo_quality["box_count"]),
            "model_a_run_id": pins["detector"].run_id,
            "model_b_run_id": pins["multitask"].run_id,
            "model_b_best_epoch": int(model_b_environment["best_epoch"]),
            "exp_f_used_for_tuning": False,
            "multitask_exp_f_evaluation_passes": 1,
            "physical_damage_validated": False,
        }
        summary_path = run.run_directory / "reports/result_summary.json"
        summary_path.write_text(json_text(summary), encoding="utf-8")
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
                "professor_report": report_path.relative_to(
                    run.repository_root
                ).as_posix(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
