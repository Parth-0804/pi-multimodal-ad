#!/usr/bin/env python3
"""Task C: synthetic signal injection — pipeline validation, NOT a PHM result.

D1 showed the sensor features carry no signal. That is a different claim from
"the pipeline could have found signal if it were there", and the thesis needs
both. Here the entire pipeline is held fixed — LOEO folds, model,
hyperparameters, clustered bootstrap — and only the per-minute features are
replaced by synthetic ones with a known, tunable amount of target information.

    f[m, j] = alpha * z_r + sqrt(1 - alpha^2) * eps[m, j],  eps ~ N(0, 1)

EVERY NUMBER PRODUCED HERE IS SYNTHETIC. The injection is built from the true
target by construction, which is exactly what makes it a control rather than a
result. No number from this script may appear in a table beside a real one.

C.1 alpha sweep, C.2 channel sparsity, C.3 rank-distillation control.
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

from phm2026.models.patchtst.model import PatchTSTConfig, PatchTSTRegressor
from phm2026.preprocessing.timeseries import RunSequence, collate_run_sequences

SENSOR = "runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee"
LOEO_TRAIN = {"EXP-A": "EXP-F", "EXP-B": "EXP-F", "EXP-F": "EXP-B"}
FROZEN = {"max_epochs": 80, "patience": 10, "batch_size": 4,
          "learning_rate": 1e-3, "weight_decay": 1e-4}


def real_skeleton():
    """Run identity, length, split and target from the real artifacts."""
    summary = pd.read_parquet(f"{SENSOR}/tables/sensor_run_sequences.parquet")
    minute = pd.read_parquet(f"{SENSOR}/tables/minute_feature_table.parquet")
    lengths = (minute[minute.sequence_inclusion_status.eq("included")]
               .groupby(["experiment", "run"]).size())
    rows = []
    for r in summary.itertuples():
        key = (r.experiment, r.run)
        if key not in lengths.index:
            continue
        rows.append({"experiment": r.experiment, "run": int(r.run),
                     "length": int(lengths.loc[key]),
                     "target": float(r.raw_top3_mean_pct),
                     "sequence_id": str(r.sequence_id)})
    return pd.DataFrame(rows).sort_values(["experiment", "run"]).reset_index(drop=True)


def synthesise(skeleton, *, alpha, seed, n_channels=72, informative=None):
    """Build RunSequences whose features carry a known amount of target signal.

    Generated once and reused across folds, so the LOEO protocol is intact.
    Features are unit-variance by construction, so no renormalisation is applied.
    """
    targets = skeleton.target.to_numpy(dtype=float)
    z = (targets - targets.mean()) / targets.std(ddof=0)
    rng = np.random.default_rng(seed)
    informative = n_channels if informative is None else informative
    sequences = []
    for row, z_r in zip(skeleton.itertuples(), z):
        noise = rng.normal(size=(row.length, n_channels))
        values = noise.copy()
        values[:, :informative] = (
            alpha * z_r + np.sqrt(max(0.0, 1 - alpha ** 2)) * noise[:, :informative]
        )
        sequences.append(RunSequence(
            sequence_id=row.sequence_id, experiment=row.experiment, run=row.run,
            split="", values=values.astype(np.float32), target_raw=row.target,
            target_monotonic=row.target, minute_ids=tuple(),
        ))
    return sequences


def pairwise_rank_loss(prediction, teacher):
    """Logistic pairwise ranking loss: order predictions like the teacher."""
    diff_pred = prediction.unsqueeze(0) - prediction.unsqueeze(1)
    diff_teacher = teacher.unsqueeze(0) - teacher.unsqueeze(1)
    mask = diff_teacher.abs() > 1e-12
    if not mask.any():
        return prediction.sum() * 0.0
    return nn.functional.softplus(
        -diff_pred[mask] * torch.sign(diff_teacher[mask])
    ).mean()


def train_and_predict(train, held, *, n_channels, seed, device, teacher=None, weight=0.0):
    torch.manual_seed(seed)
    config = PatchTSTConfig(input_channels=n_channels, patch_length=16, patch_stride=8,
                            d_model=32, n_heads=4, encoder_layers=2,
                            feedforward_dimension=64, dropout=0.1,
                            head_hidden_dimension=64)
    model = PatchTSTRegressor(config).to(device)
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
            picked = [train[i] for i in rotated[start : start + FROZEN["batch_size"]]]
            batch = collate_run_sequences(picked)
            optimizer.zero_grad()
            predicted = model(batch["inputs"].to(device), batch["time_mask"].to(device))
            scaled = (batch["targets_raw"].to(device) - mu) / sigma
            loss = nn.functional.smooth_l1_loss(predicted, scaled)
            if teacher is not None and weight > 0 and len(picked) > 1:
                signal = torch.tensor([teacher[(s.experiment, s.run)] for s in picked],
                                      dtype=torch.float32, device=device)
                loss = loss + weight * pairwise_rank_loss(predicted, signal)
            loss.backward()
            optimizer.step()
        # in-training selection uses the training experiment itself (no held-out peek)
        model.eval()
        batch = collate_run_sequences(train)
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
    batch = collate_run_sequences(held)
    with torch.no_grad():
        predicted = model(batch["inputs"].to(device),
                          batch["time_mask"].to(device)).cpu().numpy() * sigma + mu
    truth = np.array([s.target_raw for s in held])
    return np.abs(predicted - truth), np.abs(mu - truth)


def loeo(sequences, *, n_channels, seed, device, teacher=None, weight=0.0):
    model_errors, constant_errors = [], []
    for held_out, train_exp in LOEO_TRAIN.items():
        train = [s for s in sequences if s.experiment == train_exp]
        held = [s for s in sequences if s.experiment == held_out]
        m, c = train_and_predict(train, held, n_channels=n_channels, seed=seed,
                                 device=device, teacher=teacher, weight=weight)
        model_errors.extend(m.tolist())
        constant_errors.extend(c.tolist())
    return np.array(model_errors), np.array(constant_errors)


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seeds", type=int, nargs="*", default=[1, 2, 3])
    args = parser.parse_args(argv)
    skeleton = real_skeleton()
    print(f"skeleton: {len(skeleton)} runs; ALL FEATURES BELOW ARE SYNTHETIC\n")
    results = {"c1": [], "c2": [], "c3": []}

    print("=" * 78)
    print("C.1 alpha sweep (72 informative channels)")
    print("=" * 78)
    for alpha in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        per_seed = []
        for seed in args.seeds:
            sequences = synthesise(skeleton, alpha=alpha, seed=seed)
            model_errors, constant_errors = loeo(sequences, n_channels=72, seed=seed,
                                                 device=args.device)
            mean, low, high = paired_ci(model_errors, constant_errors)
            per_seed.append({"seed": seed, "mae": float(model_errors.mean()),
                             "constant": float(constant_errors.mean()),
                             "delta": mean, "ci_low": low, "ci_high": high,
                             "excludes_zero": bool(low > 0 or high < 0)})
        maes = [p["mae"] for p in per_seed]
        beats = sum(1 for p in per_seed if p["delta"] < 0 and p["excludes_zero"])
        print(f"  alpha={alpha:.1f}: MAE {np.mean(maes):.4f} +/- {np.std(maes):.4f}  "
              f"(constant {per_seed[0]['constant']:.4f})  "
              f"delta {np.mean([p['delta'] for p in per_seed]):+.4f}  "
              f"seeds beating constant with CI excluding 0: {beats}/{len(per_seed)}")
        results["c1"].append({"alpha": alpha, "per_seed": per_seed,
                              "mae_mean": float(np.mean(maes)),
                              "seeds_significant": beats})

    print("\n" + "=" * 78)
    print("C.2 channel sparsity at alpha=0.6")
    print("=" * 78)
    for k in (1, 8, 72):
        per_seed = []
        for seed in args.seeds:
            sequences = synthesise(skeleton, alpha=0.6, seed=seed, informative=k)
            model_errors, constant_errors = loeo(sequences, n_channels=72, seed=seed,
                                                 device=args.device)
            mean, low, high = paired_ci(model_errors, constant_errors)
            per_seed.append({"seed": seed, "mae": float(model_errors.mean()),
                             "delta": mean, "excludes_zero": bool(low > 0 or high < 0)})
        maes = [p["mae"] for p in per_seed]
        beats = sum(1 for p in per_seed if p["delta"] < 0 and p["excludes_zero"])
        print(f"  k={k:2d} informative of 72: MAE {np.mean(maes):.4f} +/- {np.std(maes):.4f}  "
              f"delta {np.mean([p['delta'] for p in per_seed]):+.4f}  significant {beats}/{len(per_seed)}")
        results["c2"].append({"k": k, "per_seed": per_seed, "mae_mean": float(np.mean(maes))})

    print("\n" + "=" * 78)
    print("C.3 rank-distillation control (synthetic teacher, beta=0.678)")
    print("=" * 78)
    targets = skeleton.target.to_numpy(dtype=float)
    z = (targets - targets.mean()) / targets.std(ddof=0)
    for alpha in (0.0, 0.3, 0.6):
        for seed in args.seeds[:2]:
            rng = np.random.default_rng(1000 + seed)
            beta = 0.678
            teacher_values = beta * z + np.sqrt(1 - beta ** 2) * rng.normal(size=len(z))
            teacher = {(r.experiment, r.run): float(v)
                       for r, v in zip(skeleton.itertuples(), teacher_values)}
            sequences = synthesise(skeleton, alpha=alpha, seed=seed)
            plain, constant_errors = loeo(sequences, n_channels=72, seed=seed,
                                          device=args.device)
            distilled, _ = loeo(sequences, n_channels=72, seed=seed, device=args.device,
                                teacher=teacher, weight=1.0)
            mean, low, high = paired_ci(distilled, plain)
            print(f"  alpha={alpha:.1f} seed={seed}: plain {plain.mean():.4f}  "
                  f"distilled {distilled.mean():.4f}  delta {mean:+.4f} "
                  f"[{low:+.4f}, {high:+.4f}]  helps={mean < 0 and high < 0}")
            results["c3"].append({"alpha": alpha, "seed": seed,
                                  "plain": float(plain.mean()),
                                  "distilled": float(distilled.mean()),
                                  "delta": mean, "ci_low": low, "ci_high": high})

    out = "docs/thesis/CLOSING_TASK_C_SYNTHETIC.json"
    with open(out, "w") as handle:
        json.dump({"WARNING": "ALL NUMBERS SYNTHETIC — control, not a PHM result",
                   "frozen_hyperparameters": FROZEN, "results": results}, handle, indent=2)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
