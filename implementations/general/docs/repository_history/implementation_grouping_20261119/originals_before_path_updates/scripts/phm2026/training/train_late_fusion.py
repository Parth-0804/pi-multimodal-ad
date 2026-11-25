#!/usr/bin/env python3
"""Late fusion over sensor sub-modalities, per PREREGISTRATION_20260912T053329Z.

Eight variants, identical budget, fixed seed. Trained on EXP-B, selected on
EXP-A raw MAE. EXP-F is loaded only after selection is final and scored exactly
once, for the single selected variant.

The quarantine is structural rather than a matter of discipline: `train_variant`
is never given the test sequences, so no code path can score EXP-F during
training or selection even by mistake.
"""

from __future__ import annotations

# Source-tree entry point; no installed package is required.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3] / "src"))


import argparse
import json
import sys
import time
from copy import deepcopy
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn

from phm2026.evaluation.monotonic import monotonic_metrics
from phm2026.evaluation.regression import regression_metrics
from phm2026.fusion.late_fusion import (
    SUB_MODALITY_CHANNELS,
    LateFusionRegressor,
    sub_modality_column_indices,
)
from phm2026.models.patchtst.model import PatchTSTConfig, PatchTSTRegressor
from phm2026.preprocessing.timeseries import (
    FeatureNormalizer,
    build_run_sequences,
    collate_run_sequences,
    fit_feature_normalizer,
)
from phm2026.reporting.common import finalize_run, json_text
from phm2026.utils.artifacts import load_pinned_run
from phm2026.utils.config import load_yaml_config
from phm2026.utils.provenance import create_run_context

PREREGISTRATION = "docs/thesis/PREREGISTRATION_20260912T053329Z.md"
ALL_GROUPS = tuple(SUB_MODALITY_CHANNELS)

# Exactly the eight variants fixed in the pre-registration, in that order.
VARIANTS: tuple[tuple[str, tuple[str, ...] | None], ...] = (
    ("solo_process_context", ("process_context",)),
    ("solo_organiser_rms", ("organiser_rms",)),
    ("solo_condition_indicators", ("condition_indicators",)),
    ("fused_all_three", ALL_GROUPS),
    ("single_encoder_all_9ch", None),  # None -> the baseline architecture
    ("loo_drop_process_context", ("organiser_rms", "condition_indicators")),
    ("loo_drop_organiser_rms", ("process_context", "condition_indicators")),
    ("loo_drop_condition_indicators", ("process_context", "organiser_rms")),
)


def build_model(groups, *, feature_columns, model_config, seed):
    torch.manual_seed(seed)
    if groups is None:
        return PatchTSTRegressor(model_config)
    indices = {
        name: sub_modality_column_indices(feature_columns, SUB_MODALITY_CHANNELS[name])
        for name in groups
    }
    return LateFusionRegressor(model_config, group_indices=indices)


def train_variant(
    name, groups, *, train, validation, feature_columns, model_config, options, seed, device
) -> dict[str, Any]:
    """Train one variant. Deliberately has no access to the test split."""

    model = build_model(
        groups, feature_columns=feature_columns, model_config=model_config, seed=seed
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=options["learning_rate"], weight_decay=options["weight_decay"]
    )
    scaler_values = np.asarray([item.target_raw for item in train], dtype=np.float64)
    scale = float(scaler_values.std(ddof=0)) or 1.0
    scaler = {"mean": float(scaler_values.mean()), "scale": scale}

    def scaled(batch):
        return (batch["targets_raw"].to(device) - scaler["mean"]) / scaler["scale"]

    generator = torch.Generator().manual_seed(seed)
    order = torch.randperm(len(train), generator=generator).tolist()
    best_loss, best_state, wait, best_epoch = float("inf"), None, 0, 0
    history: list[dict[str, float]] = []
    started = time.perf_counter()
    diverged = False

    for epoch in range(1, options["max_epochs"] + 1):
        model.train()
        rotated = order[epoch % len(order):] + order[: epoch % len(order)]
        losses = []
        for start in range(0, len(rotated), options["batch_size"]):
            batch = collate_run_sequences(
                [train[i] for i in rotated[start : start + options["batch_size"]]]
            )
            optimizer.zero_grad()
            prediction = model(batch["inputs"].to(device), batch["time_mask"].to(device))
            loss = nn.functional.smooth_l1_loss(prediction, scaled(batch))
            if not torch.isfinite(loss):
                diverged = True
                break
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
        if diverged:
            break
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
        history.append(
            {"epoch": epoch, "train_loss": float(np.mean(losses)), "validation_loss": validation_loss}
        )
        if validation_loss < best_loss - 1e-8:
            best_loss, wait, best_epoch = validation_loss, 0, epoch
            best_state = deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()})
        else:
            wait += 1
        if wait >= options["patience"]:
            break

    if diverged or best_state is None:
        return {"variant": name, "status": "diverged", "groups": list(groups or ["all_9ch"])}

    model.load_state_dict(best_state)
    model.eval()
    validation_batch = collate_run_sequences(validation)
    with torch.no_grad():
        predicted = (
            model(
                validation_batch["inputs"].to(device),
                validation_batch["time_mask"].to(device),
            ).cpu().numpy()
            * scaler["scale"]
            + scaler["mean"]
        )
    truth = validation_batch["targets_raw"].numpy()
    raw = regression_metrics(truth, predicted)
    mono = monotonic_metrics(truth, predicted)
    return {
        "variant": name,
        "status": "ok",
        "groups": list(groups or ["all_9ch"]),
        "parameter_count": int(sum(p.numel() for p in model.parameters())),
        "epochs_completed": len(history),
        "best_epoch": best_epoch,
        "training_seconds": time.perf_counter() - started,
        "validation_mae": raw["mae"],
        "validation_mse": raw["mse"],
        "validation_spearman": raw["spearman"],
        "validation_monotonic_mse": mono["monotonic_mse"],
        "validation_degeneracy": mono["degeneracy"],
        "_state": best_state,
        "_scaler": scaler,
        "_history": history,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/experiments/phm2026_fusion_latefusion.yaml")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)

    config = load_yaml_config(args.config)
    data = config.mutable_copy()
    sensor = load_pinned_run(
        config.repository_root,
        data["source_runs"]["sensor_features"],
        required_artifacts=("tables/minute_feature_table.parquet", "tables/sensor_run_sequences.parquet"),
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
    normalizer = fit_feature_normalizer(minute, feature_columns=feature_columns)
    sequences = build_run_sequences(minute, run_summary, normalizer=normalizer)
    train = [s for s in sequences if s.split == "train"]
    validation = [s for s in sequences if s.split == "validation"]
    # Held back deliberately; not passed to train_variant under any branch.
    test = [s for s in sequences if s.split == "test"]

    seed = int(data["seed"])
    training = data["training"]
    options = {
        "max_epochs": int(training["max_epochs"]),
        "patience": int(training["patience"]),
        "batch_size": int(training["batch_size"]),
        "learning_rate": float(training["learning_rate"]),
        "weight_decay": float(training["weight_decay"]),
    }
    model_config = PatchTSTConfig(
        input_channels=len(feature_columns),
        patch_length=int(data["model"]["patch_length"]),
        patch_stride=int(data["model"]["patch_stride"]),
        d_model=int(data["model"]["d_model"]),
        n_heads=int(data["model"]["n_heads"]),
        encoder_layers=int(data["model"]["encoder_layers"]),
        feedforward_dimension=int(data["model"]["feedforward_dimension"]),
        dropout=float(data["model"]["dropout"]),
        head_hidden_dimension=int(data["model"]["head_hidden_dimension"]),
    )

    run = create_run_context(
        study=data["study"],
        output_root=config.resolve_repository_path(data["output_root"], field="output_root"),
        config=config,
        seed=seed,
        command=["scripts/phm2026/training/train_late_fusion.py", *(argv or sys.argv[1:])],
        input_roots=(sensor.relative_directory,),
        package_names=("numpy", "pandas", "pyarrow", "torch", "scikit-learn", "PyYAML"),
        source_runs=[
            {
                "name": "sensor_features",
                "run_id": sensor.run_id,
                "directory": sensor.relative_directory,
                "artifacts": dict(sensor.verified_hashes),
            }
        ],
    )
    run.create_layout()

    print(f"run_directory: {run.run_directory.relative_to(config.repository_root)}")
    print(f"train={len(train)} validation={len(validation)} test={len(test)} (test untouched until selection)")
    results = []
    for name, groups in VARIANTS:
        outcome = train_variant(
            name, groups,
            train=train, validation=validation,
            feature_columns=feature_columns, model_config=model_config,
            options=options, seed=seed, device=args.device,
        )
        results.append(outcome)
        if outcome["status"] == "ok":
            print(f"  {name:32s} val MAE {outcome['validation_mae']:.4f}  "
                  f"val mono-MSE {outcome['validation_monotonic_mse']:.4f}  "
                  f"rho {outcome['validation_spearman']}  epochs {outcome['epochs_completed']}")
        else:
            print(f"  {name:32s} {outcome['status'].upper()}")

    # ---- selection: EXP-A raw MAE only, per pre-registration section 4 ----
    usable = [r for r in results if r["status"] == "ok"]
    if not usable:
        print("no variant trained successfully; skipping the EXP-F evaluation")
        selected = None
    else:
        selected = min(usable, key=lambda r: (r["validation_mae"], r["variant"]))
        print(f"\nselected on EXP-A raw MAE: {selected['variant']} ({selected['validation_mae']:.4f})")

    # ---- the single, pre-declared EXP-F evaluation ----
    test_row = None
    if selected is not None:
        model = build_model(
            dict(VARIANTS)[selected["variant"]],
            feature_columns=feature_columns, model_config=model_config, seed=seed,
        ).to(args.device)
        model.load_state_dict(selected["_state"])
        model.eval()
        batch = collate_run_sequences(test)
        with torch.no_grad():
            predicted = (
                model(batch["inputs"].to(args.device), batch["time_mask"].to(args.device))
                .cpu().numpy() * selected["_scaler"]["scale"] + selected["_scaler"]["mean"]
            )
        truth = batch["targets_raw"].numpy()
        raw = regression_metrics(truth, predicted)
        mono = monotonic_metrics(truth, predicted)
        constant = float(np.mean([s.target_raw for s in train]))
        constant_raw = regression_metrics(truth, np.full(len(truth), constant))
        constant_mono = monotonic_metrics(truth, np.full(len(truth), constant))
        test_row = {
            "variant": selected["variant"],
            "split": "test",
            "sample_count": raw["sample_count"],
            "mae": raw["mae"],
            "mse": raw["mse"],
            "spearman": raw["spearman"],
            "monotonic_mse": mono["monotonic_mse"],
            "constant_mae": constant_raw["mae"],
            "constant_monotonic_mse": constant_mono["monotonic_mse"],
            "mae_delta_vs_constant": raw["mae"] - constant_raw["mae"],
            "evaluations_performed": 1,
        }
        print(f"\n=== the one EXP-F evaluation ({selected['variant']}) ===")
        print(f"  MAE {raw['mae']:.4f}   constant {constant_raw['mae']:.4f}   "
              f"delta {test_row['mae_delta_vs_constant']:+.4f}")
        print(f"  monotonic-MSE {mono['monotonic_mse']:.4f}   constant {constant_mono['monotonic_mse']:.4f}")
        print("  (pre-registered: |delta| < 0.15 pp is reported as indistinguishable)")

    table = pd.DataFrame(
        [{k: v for k, v in r.items() if not k.startswith("_")} for r in results]
    )
    artifacts = [run.artifact(run.write_resolved_config(data), role="resolved_configuration")]
    for suffix, writer in ((".csv", table.to_csv), (".parquet", table.to_parquet)):
        path = run.run_directory / f"tables/variant_validation{suffix}"
        writer(path, index=False)
        artifacts.append(run.artifact(path, role="variant_validation"))
    summary_path = run.run_directory / "reports/late_fusion_summary.json"
    summary_path.write_text(
        json_text(
            {
                "schema_version": "1.0.0",
                "preregistration": PREREGISTRATION,
                "target_definition_version": str(run_summary.target_definition_version.unique()[0]),
                "selection_rule": "lowest EXP-A (validation) raw MAE; EXP-F not consulted",
                "selected_variant": None if selected is None else selected["variant"],
                "exp_f_evaluations_performed": 0 if test_row is None else 1,
                "variants": [
                    {k: v for k, v in r.items() if not k.startswith("_")} for r in results
                ],
                "test_result": test_row,
            }
        ),
        encoding="utf-8",
    )
    artifacts.append(run.artifact(summary_path, role="summary"))
    finalize_run(run, artifacts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
