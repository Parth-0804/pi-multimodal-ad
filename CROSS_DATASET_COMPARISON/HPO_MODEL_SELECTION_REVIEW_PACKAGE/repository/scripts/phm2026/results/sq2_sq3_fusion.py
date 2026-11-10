#!/usr/bin/env python3
"""SQ2/SQ3: four-arm fusion comparison over sensor sub-modalities, plus
missing-modality robustness. Real PHM data, v3 target, LOEO, clustered CIs.

Arms: A1 unimodal (one per group), A2 concatenation (single encoder over all
channels), A3 modular late fusion (decision level), A4 process-aware gated
fusion (gate conditioned on process context).

Robustness, A3 and A4 only: drop M1, drop M3, noise on M1+M2 at 10 dB and
0 dB, drop M4. A dropped modality is zeroed in place so the architecture stays
valid at inference, which is what a real sensor dropout looks like.
"""

from __future__ import annotations

# Source-tree entry point; no installed package is required.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3] / "src"))


import argparse
import json
from copy import deepcopy

import numpy as np
import pandas as pd
import torch
from torch import nn

from phm2026.evaluation.regression import regression_metrics
from phm2026.fusion.modality_fusion import (
    SUB_MODALITY_PROVENANCE,
    DecisionLevelFusion,
    ProcessAwareGatedFusion,
    group_column_indices,
    resolve_groups,
)
from phm2026.models.patchtst.model import PatchTSTConfig, PatchTSTRegressor
from phm2026.preprocessing.timeseries import (
    RunSequence, build_run_sequences, collate_run_sequences, fit_feature_normalizer,
)

SENSOR = "runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee"
LOEO_TRAIN = {"EXP-A": "EXP-F", "EXP-B": "EXP-F", "EXP-F": "EXP-B"}
FROZEN = {"max_epochs": 80, "patience": 10, "batch_size": 4,
          "learning_rate": 1e-3, "weight_decay": 1e-4}
SEEDS = (1, 2, 3)


def clustered_ci(errors, *, draws=10000, seed=20260912):
    rng = np.random.default_rng(seed)
    out = np.empty(draws)
    for i in range(draws):
        picked = rng.integers(0, len(errors), len(errors))
        out[i] = errors[picked].mean()
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def paired_ci(a, b, *, draws=10000, seed=20260912):
    rng = np.random.default_rng(seed)
    out = np.empty(draws)
    for i in range(draws):
        picked = rng.integers(0, len(a), len(a))
        out[i] = a[picked].mean() - b[picked].mean()
    return float(out.mean()), float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def build_model(arm, *, config, groups, seed):
    torch.manual_seed(seed)
    if arm == "A2_concatenation":
        return PatchTSTRegressor(config)
    if arm == "A3_modular_late":
        return DecisionLevelFusion(config, group_indices=groups)
    if arm == "A4_gated":
        return ProcessAwareGatedFusion(config, group_indices=groups)
    if arm.startswith("A1_"):
        name = arm[len("A1_"):]
        return DecisionLevelFusion(config, group_indices={name: groups[name]})
    raise ValueError(arm)


def degrade(sequences, condition, groups, *, seed):
    """Apply a real missing/degraded-modality condition to held-out inputs."""
    if condition == "none":
        return sequences
    rng = np.random.default_rng(seed)
    out = []
    for s in sequences:
        values = s.values.copy()
        if condition.startswith("drop_"):
            name = condition[len("drop_"):]
            if name in groups:
                values[:, groups[name]] = 0.0
        elif condition.startswith("noise_"):
            snr_db = float(condition.split("_")[1].replace("dB", ""))
            sigma = float(np.sqrt(1.0 / (10 ** (snr_db / 10.0))))
            for name in ("M1_accel1", "M2_accel2"):
                if name in groups:
                    idx = groups[name]
                    values[:, idx] += rng.normal(scale=sigma, size=values[:, idx].shape).astype(np.float32)
        else:
            raise ValueError(condition)
        out.append(RunSequence(
            sequence_id=s.sequence_id, experiment=s.experiment, run=s.run, split=s.split,
            values=values, target_raw=s.target_raw, target_monotonic=s.target_monotonic,
            minute_ids=s.minute_ids))
    return out


def train_fold(arm, train, validation, *, config, groups, seed, device):
    model = build_model(arm, config=config, groups=groups, seed=seed).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=FROZEN["learning_rate"],
                                  weight_decay=FROZEN["weight_decay"])
    values = np.asarray([s.target_raw for s in train], dtype=np.float64)
    mu, sigma = float(values.mean()), float(values.std(ddof=0)) or 1.0
    generator = torch.Generator().manual_seed(seed)
    order = torch.randperm(len(train), generator=generator).tolist()
    best, best_state, wait = float("inf"), None, 0
    for epoch in range(1, FROZEN["max_epochs"] + 1):
        model.train()
        rotated = order[epoch % len(order):] + order[: epoch % len(order)]
        for start in range(0, len(rotated), FROZEN["batch_size"]):
            batch = collate_run_sequences([train[i] for i in rotated[start:start + FROZEN["batch_size"]]])
            optimizer.zero_grad()
            loss = nn.functional.smooth_l1_loss(
                model(batch["inputs"].to(device), batch["time_mask"].to(device)),
                (batch["targets_raw"].to(device) - mu) / sigma)
            loss.backward()
            optimizer.step()
        model.eval()
        batch = collate_run_sequences(validation)
        with torch.no_grad():
            value = float(nn.functional.smooth_l1_loss(
                model(batch["inputs"].to(device), batch["time_mask"].to(device)),
                (batch["targets_raw"].to(device) - mu) / sigma).item())
        if value < best - 1e-8:
            best, wait = value, 0
            best_state = deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()})
        else:
            wait += 1
        if wait >= FROZEN["patience"]:
            break
    model.load_state_dict(best_state)
    model.eval()
    return model, mu, sigma


def evaluate(arm, sequences, *, config, groups, seed, device, condition="none"):
    errors, constants, gate_rows = [], [], []
    for held_out, train_exp in LOEO_TRAIN.items():
        train = [s for s in sequences if s.experiment == train_exp]
        validation = [s for s in sequences if s.experiment not in (train_exp, held_out)]
        held = [s for s in sequences if s.experiment == held_out]
        model, mu, sigma = train_fold(arm, train, validation, config=config,
                                      groups=groups, seed=seed, device=device)
        held = degrade(held, condition, groups, seed=seed)
        batch = collate_run_sequences(held)
        with torch.no_grad():
            predicted = model(batch["inputs"].to(device),
                              batch["time_mask"].to(device)).cpu().numpy() * sigma + mu
            if isinstance(model, ProcessAwareGatedFusion):
                weights = model.gate_weights(batch["inputs"].to(device),
                                             batch["time_mask"].to(device)).cpu().numpy()
                gate_rows.append(weights)
        truth = batch["targets_raw"].numpy()
        errors.extend(np.abs(predicted - truth).tolist())
        constants.extend(np.abs(mu - truth).tolist())
    gates = np.concatenate(gate_rows, axis=0) if gate_rows else None
    return np.array(errors), np.array(constants), gates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--out", default="docs/thesis/SQ2_SQ3_RESULTS.json")
    args = parser.parse_args(argv)

    minute = pd.read_parquet(f"{SENSOR}/tables/minute_feature_table.parquet")
    summary = pd.read_parquet(f"{SENSOR}/tables/sensor_run_sequences.parquet")
    feature_columns = [c for c in minute.columns
                       if c.endswith(("_mean", "_std", "_median", "_min", "_max",
                                      "_last", "_slope_per_sample", "_missing"))]
    groups = resolve_groups(feature_columns)

    print("SUB-MODALITY PARTITION (by HDF5 provenance)")
    assigned = set()
    for name, bases in SUB_MODALITY_PROVENANCE.items():
        idx = group_column_indices(feature_columns, bases)
        assigned |= set(idx)
        status = "EMPTY — no channel in the pipeline" if not idx else f"{len(idx)} columns"
        print(f"  {name:26s} bases={str(list(bases)):32s} {status}")
    unassigned = [feature_columns[i] for i in range(len(feature_columns)) if i not in assigned]
    print(f"  unassigned columns: {len(unassigned)} {unassigned}")
    print(f"  total {len(feature_columns)} columns; non-empty groups used: {list(groups)}\n")

    normalizer = fit_feature_normalizer(minute, feature_columns=feature_columns)
    sequences = build_run_sequences(minute, summary, normalizer=normalizer)
    config = PatchTSTConfig(input_channels=len(feature_columns), patch_length=16,
                            patch_stride=8, d_model=32, n_heads=4, encoder_layers=2,
                            feedforward_dimension=64, dropout=0.1, head_hidden_dimension=64)

    arms = [f"A1_{name}" for name in groups] + ["A2_concatenation", "A3_modular_late", "A4_gated"]
    payload = {"partition": {k: group_column_indices(feature_columns, v)
                             for k, v in SUB_MODALITY_PROVENANCE.items()},
               "unassigned": unassigned, "arms": {}, "robustness": {}, "gate": {}}

    print("FOUR-ARM COMPARISON (LOEO, v3 target, run-level MAE)")
    per_arm_errors = {}
    for arm in arms:
        maes, pooled = [], []
        for seed in SEEDS:
            errors, constants, _ = evaluate(arm, sequences, config=config, groups=groups,
                                            seed=seed, device=args.device)
            maes.append(float(errors.mean()))
            pooled.append(errors)
        stacked = np.mean(np.vstack(pooled), axis=0)
        per_arm_errors[arm] = stacked
        low, high = clustered_ci(stacked)
        print(f"  {arm:28s} MAE {np.mean(maes):.4f} +/- {np.std(maes):.4f}  CI [{low:.4f}, {high:.4f}]")
        payload["arms"][arm] = {"mae_mean": float(np.mean(maes)), "mae_std": float(np.std(maes)),
                                "ci_low": low, "ci_high": high, "per_seed": maes}
    _, constants, _ = evaluate(arms[0], sequences, config=config, groups=groups,
                               seed=SEEDS[0], device=args.device)
    low, high = clustered_ci(constants)
    print(f"  {'constant (per-fold train mean)':28s} MAE {constants.mean():.4f}  CI [{low:.4f}, {high:.4f}]")
    payload["constant"] = {"mae": float(constants.mean()), "ci_low": low, "ci_high": high}
    per_arm_errors["constant"] = constants

    print("\nPAIRWISE DIFFERENCES (clustered, paired by run)")
    names = list(per_arm_errors)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            mean, lo, hi = paired_ci(per_arm_errors[a], per_arm_errors[b])
            flag = "EXCLUDES ZERO" if (lo > 0 or hi < 0) else "ns"
            print(f"  {a:28s} - {b:28s} {mean:+.4f} [{lo:+.4f}, {hi:+.4f}]  {flag}")
            payload.setdefault("pairwise", []).append(
                {"a": a, "b": b, "delta": mean, "ci_low": lo, "ci_high": hi,
                 "excludes_zero": bool(lo > 0 or hi < 0)})

    print("\nROBUSTNESS (A3, A4 only; R2 drop_M3_encoder is vacuous — group is empty)")
    conditions = ["none", "drop_M1_accel1", "drop_M3_encoder",
                  "noise_10dB", "noise_0dB", "drop_M4_context"]
    for arm in ("A3_modular_late", "A4_gated"):
        for condition in conditions:
            maes, gates = [], []
            for seed in SEEDS:
                errors, _, gate = evaluate(arm, sequences, config=config, groups=groups,
                                           seed=seed, device=args.device, condition=condition)
                maes.append(float(errors.mean()))
                if gate is not None:
                    gates.append(gate)
            entry = {"mae_mean": float(np.mean(maes)), "mae_std": float(np.std(maes))}
            if gates:
                stacked = np.vstack(gates)
                entry["gate_mean"] = stacked.mean(axis=0).tolist()
                entry["gate_std"] = stacked.std(axis=0).tolist()
            payload["robustness"][f"{arm}|{condition}"] = entry
            extra = ""
            if gates:
                extra = "  gate=" + np.array2string(np.vstack(gates).mean(axis=0), precision=3)
            print(f"  {arm:18s} {condition:16s} MAE {np.mean(maes):.4f} +/- {np.std(maes):.4f}{extra}")
    payload["gate_group_order"] = list(groups)

    with open(args.out, "w") as handle:
        json.dump(payload, handle, indent=2)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
