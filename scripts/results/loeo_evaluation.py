#!/usr/bin/env python3
"""Leave-one-experiment-out evaluation with run-clustered intervals.

EXP-F is no longer a clean holdout -- it has been scored many times across this
project (historical baselines, multi-seed runs, a weight-decay sweep,
bootstraps, reproduction checks, rescoring). Eight contaminated points cannot
support the claim the thesis needs, so every run is instead predicted exactly
once by a model that never saw its experiment:

    predict EXP-A  <- train EXP-F, validate EXP-B
    predict EXP-B  <- train EXP-F, validate EXP-A
    predict EXP-F  <- train EXP-B, validate EXP-A

LOEO leaves no third experiment for early stopping, so within each fold the
larger remaining experiment trains and the smaller validates. The rule is
deterministic and never touches the held-out experiment. The EXP-F fold is
exactly the project's existing protocol (train EXP-B, validate EXP-A).

Hyperparameters are frozen at the committed config. Nothing is tuned inside or
outside the loop; given the EXP-F history, any tuning would invalidate this.

Intervals resample whole RUNS, never teeth or minutes: a run's teeth are a
deterministic function of one input sequence and are not independent
observations.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy

import numpy as np
import pandas as pd
import torch
from torch import nn

from pi_multimodal_ad.evaluation.regression import regression_metrics
from pi_multimodal_ad.models.late_fusion import (
    SUB_MODALITY_CHANNELS,
    LateFusionRegressor,
    sub_modality_column_indices,
)
from pi_multimodal_ad.models.patchtst import PatchTSTConfig, PatchTSTRegressor
from pi_multimodal_ad.preprocessing.timeseries import (
    build_run_sequences,
    collate_run_sequences,
    fit_feature_normalizer,
)
from pi_multimodal_ad.reporting.common import finalize_run, json_text
from pi_multimodal_ad.utils.artifacts import load_pinned_run
from pi_multimodal_ad.utils.config import load_yaml_config
from pi_multimodal_ad.utils.provenance import create_run_context

# predicted -> (train, validate). Larger remaining experiment trains.
FOLDS = {
    "EXP-A": ("EXP-F", "EXP-B"),
    "EXP-B": ("EXP-F", "EXP-A"),
    "EXP-F": ("EXP-B", "EXP-A"),
}
R4_SCALAR = (
    "runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099"
    "/tables/scalar_predictions.parquet"
)


def clustered_bootstrap(errors_by_run, *, draws, seed):
    """Resample whole runs. `errors_by_run` maps run key -> array of errors."""

    keys = list(errors_by_run)
    rng = np.random.default_rng(seed)
    values = np.empty(draws, dtype=np.float64)
    for index in range(draws):
        picked = rng.integers(0, len(keys), len(keys))
        values[index] = np.mean(
            np.concatenate([errors_by_run[keys[i]] for i in picked])
        )
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def paired_clustered_bootstrap(a_by_run, b_by_run, *, draws, seed):
    """CI on mean(|a|) - mean(|b|), resampling the same runs for both."""

    keys = list(a_by_run)
    rng = np.random.default_rng(seed)
    values = np.empty(draws, dtype=np.float64)
    for index in range(draws):
        picked = rng.integers(0, len(keys), len(keys))
        a = np.concatenate([a_by_run[keys[i]] for i in picked])
        b = np.concatenate([b_by_run[keys[i]] for i in picked])
        values[index] = a.mean() - b.mean()
    return (
        float(np.mean(values)),
        float(np.percentile(values, 2.5)),
        float(np.percentile(values, 97.5)),
    )


def build_model(kind, *, feature_columns, model_config, seed):
    torch.manual_seed(seed)
    if kind == "patchtst_single_encoder":
        return PatchTSTRegressor(model_config)
    indices = {
        name: sub_modality_column_indices(feature_columns, SUB_MODALITY_CHANNELS[name])
        for name in SUB_MODALITY_CHANNELS
    }
    return LateFusionRegressor(model_config, group_indices=indices)


def train_fold(kind, train, validation, *, feature_columns, model_config, options, seed, device):
    model = build_model(
        kind, feature_columns=feature_columns, model_config=model_config, seed=seed
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=options["learning_rate"], weight_decay=options["weight_decay"]
    )
    values = np.asarray([item.target_raw for item in train], dtype=np.float64)
    scaler = {"mean": float(values.mean()), "scale": float(values.std(ddof=0)) or 1.0}

    def scaled(batch):
        return (batch["targets_raw"].to(device) - scaler["mean"]) / scaler["scale"]

    generator = torch.Generator().manual_seed(seed)
    order = torch.randperm(len(train), generator=generator).tolist()
    best_loss, best_state, wait = float("inf"), None, 0
    for epoch in range(1, options["max_epochs"] + 1):
        model.train()
        rotated = order[epoch % len(order):] + order[: epoch % len(order)]
        for start in range(0, len(rotated), options["batch_size"]):
            batch = collate_run_sequences(
                [train[i] for i in rotated[start : start + options["batch_size"]]]
            )
            optimizer.zero_grad()
            loss = nn.functional.smooth_l1_loss(
                model(batch["inputs"].to(device), batch["time_mask"].to(device)), scaled(batch)
            )
            loss.backward()
            optimizer.step()
        model.eval()
        validation_batch = collate_run_sequences(validation)
        with torch.no_grad():
            validation_loss = float(
                nn.functional.smooth_l1_loss(
                    model(
                        validation_batch["inputs"].to(device),
                        validation_batch["time_mask"].to(device),
                    ),
                    scaled(validation_batch),
                ).item()
            )
        if validation_loss < best_loss - 1e-8:
            best_loss, wait = validation_loss, 0
            best_state = deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()})
        else:
            wait += 1
        if wait >= options["patience"]:
            break
    model.load_state_dict(best_state)
    model.eval()
    return model, scaler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/experiments/phm2026_fusion_latefusion.yaml")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--draws", type=int, default=10000)
    args = parser.parse_args(argv)

    config = load_yaml_config(args.config)
    data = config.mutable_copy()
    sensor = load_pinned_run(
        config.repository_root,
        data["source_runs"]["sensor_features"],
        required_artifacts=(
            "tables/minute_feature_table.parquet",
            "tables/sensor_run_sequences.parquet",
        ),
    )
    minute = pd.read_parquet(sensor.artifact_path("tables/minute_feature_table.parquet"))
    run_summary = pd.read_parquet(sensor.artifact_path("tables/sensor_run_sequences.parquet"))
    feature_columns = [
        column
        for column in minute.columns
        if any(
            column == f"{base}_missing" or column.startswith(f"{base}_")
            for group in SUB_MODALITY_CHANNELS.values()
            for base in group
        )
    ]
    seed = int(data["seed"])
    training = data["training"]
    options = {k: (int(training[k]) if k not in ("learning_rate", "weight_decay") else float(training[k]))
               for k in ("max_epochs", "patience", "batch_size", "learning_rate", "weight_decay")}
    model_config = PatchTSTConfig(
        input_channels=len(feature_columns),
        **{k: (float(data["model"][k]) if k == "dropout" else int(data["model"][k]))
           for k in ("patch_length", "patch_stride", "d_model", "n_heads",
                     "encoder_layers", "feedforward_dimension", "dropout",
                     "head_hidden_dimension")},
    )

    run = create_run_context(
        study="phm2026_loeo_evaluation",
        output_root=config.resolve_repository_path("runs/phm2026_loeo_evaluation", field="output_root"),
        config=config,
        seed=seed,
        command=["scripts/results/loeo_evaluation.py", *(argv or sys.argv[1:])],
        input_roots=(sensor.relative_directory,),
        package_names=("numpy", "pandas", "pyarrow", "torch", "scikit-learn", "PyYAML"),
        source_runs=[{"name": "sensor_features", "run_id": sensor.run_id,
                      "directory": sensor.relative_directory,
                      "artifacts": dict(sensor.verified_hashes)}],
    )
    run.create_layout()
    print(f"run_directory: {run.run_directory.relative_to(config.repository_root)}")
    print(f"frozen hyperparameters: {options}")

    rows: list[dict] = []
    for held_out, (train_exp, val_exp) in FOLDS.items():
        # normalizer fitted on the fold's TRAINING experiment only
        fold_minute = minute[minute.experiment.eq(train_exp)]
        normalizer = fit_feature_normalizer(
            fold_minute.assign(split="train"), feature_columns=feature_columns
        )
        sequences = build_run_sequences(minute, run_summary, normalizer=normalizer)
        train = [s for s in sequences if s.experiment == train_exp]
        validation = [s for s in sequences if s.experiment == val_exp]
        held = [s for s in sequences if s.experiment == held_out]

        constant = float(np.mean([s.target_raw for s in train]))
        for s in held:
            rows.append({"model": "constant_train_mean", "fold": held_out,
                         "experiment": s.experiment, "run": s.run,
                         "y_true": s.target_raw, "y_pred": constant})

        for kind in ("patchtst_single_encoder", "fused_all_three"):
            model, scaler = train_fold(
                kind, train, validation, feature_columns=feature_columns,
                model_config=model_config, options=options, seed=seed, device=args.device,
            )
            batch = collate_run_sequences(held)
            with torch.no_grad():
                predicted = (
                    model(batch["inputs"].to(args.device), batch["time_mask"].to(args.device))
                    .cpu().numpy() * scaler["scale"] + scaler["mean"]
                )
            for s, value in zip(held, predicted):
                rows.append({"model": kind, "fold": held_out, "experiment": s.experiment,
                             "run": s.run, "y_true": s.target_raw, "y_pred": float(value)})
        print(f"  fold predict {held_out} (train {train_exp}, val {val_exp}): done")

    predictions = pd.DataFrame(rows)

    # image baseline: cannot be retrained under LOEO here, and has no EXP-B
    # predictions at all. Included as a clearly-marked non-LOEO reference.
    image = pd.read_parquet(R4_SCALAR)
    truth = {(r.experiment, int(r.run)): r.target_raw
             for r in (s for s in build_run_sequences(
                 minute, run_summary,
                 normalizer=fit_feature_normalizer(
                     minute[minute.experiment.eq("EXP-B")].assign(split="train"),
                     feature_columns=feature_columns)))}
    image_rows = []
    per_tooth = image.groupby(["experiment", "run", "tooth_id"])["y_pred"].median().reset_index()
    for (experiment, run_number), scoped in per_tooth.groupby(["experiment", "run"]):
        key = (experiment, int(run_number))
        if key not in truth:
            continue
        top3 = np.sort(scoped["y_pred"].to_numpy())[-3:].mean()
        image_rows.append({"model": "rtdetr_r4_image_NOT_loeo", "fold": "not_loeo",
                           "experiment": experiment, "run": int(run_number),
                           "y_true": truth[key], "y_pred": float(top3)})
    predictions = pd.concat([predictions, pd.DataFrame(image_rows)], ignore_index=True)

    summary = []
    for model_name, scoped in predictions.groupby("model"):
        errors = {(r.experiment, r.run): np.array([abs(r.y_pred - r.y_true)])
                  for r in scoped.itertuples()}
        metrics = regression_metrics(scoped.y_true, scoped.y_pred)
        low, high = clustered_bootstrap(errors, draws=args.draws, seed=seed)
        summary.append({"model": model_name, "n_runs": len(scoped),
                        "mae": metrics["mae"], "rmse": metrics["rmse"],
                        "spearman": metrics["spearman"],
                        "mae_ci95_low": low, "mae_ci95_high": high})
    summary = pd.DataFrame(summary).sort_values("mae")

    print("\n=== LOEO, v3 target, run-level MAE, run-clustered 95% CI ===")
    print(summary.to_string(index=False))

    # the key question: fusion vs constant, paired on the same runs
    deltas = {}
    const = predictions[predictions.model.eq("constant_train_mean")].set_index(["experiment", "run"])
    for challenger in ("fused_all_three", "patchtst_single_encoder"):
        chal = predictions[predictions.model.eq(challenger)].set_index(["experiment", "run"])
        shared = const.index.intersection(chal.index)
        a = {k: np.array([abs(chal.loc[k].y_pred - chal.loc[k].y_true)]) for k in shared}
        b = {k: np.array([abs(const.loc[k].y_pred - const.loc[k].y_true)]) for k in shared}
        mean, low, high = paired_clustered_bootstrap(a, b, draws=args.draws, seed=seed)
        deltas[challenger] = {"mean_delta_vs_constant": mean, "ci95_low": low,
                              "ci95_high": high, "n_runs": len(shared),
                              "excludes_zero": bool(low > 0 or high < 0)}
        print(f"\n{challenger} minus constant: {mean:+.4f} pp  "
              f"95% CI [{low:+.4f}, {high:+.4f}]  excludes zero: {deltas[challenger]['excludes_zero']}")

    artifacts = [run.artifact(run.write_resolved_config(data), role="resolved_configuration")]
    for name, frame in (("loeo_predictions", predictions), ("loeo_summary", summary)):
        for suffix, writer in ((".csv", frame.to_csv), (".parquet", frame.to_parquet)):
            path = run.run_directory / f"tables/{name}{suffix}"
            writer(path, index=False)
            artifacts.append(run.artifact(path, role=name))
    report = run.run_directory / "reports/loeo_summary.json"
    report.write_text(json_text({
        "schema_version": "1.0.0",
        "protocol": "leave-one-experiment-out; larger remaining experiment trains, smaller validates",
        "folds": {k: {"train": v[0], "validate": v[1]} for k, v in FOLDS.items()},
        "frozen_hyperparameters": options,
        "bootstrap": {"kind": "clustered by run", "draws": args.draws},
        "target_definition_version": str(run_summary.target_definition_version.unique()[0]),
        "summary": summary.to_dict(orient="records"),
        "paired_deltas_vs_constant": deltas,
        "caveats": [
            "rtdetr_r4_image_NOT_loeo was trained on EXP-B and is not a LOEO row;"
            " it has no EXP-B predictions at all and covers only EXP-A and EXP-F.",
        ],
    }), encoding="utf-8")
    artifacts.append(run.artifact(report, role="summary"))
    finalize_run(run, artifacts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
