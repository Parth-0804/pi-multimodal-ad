#!/usr/bin/env python3
"""Task A: rank-mapped oracle. Task B: odd/even tooth split.

Both reuse existing R4 predictions; neither trains anything.

Task A maps the image branch's RANKS (not its values) onto the training
experiment's target distribution. It requires photographs at inference and is
therefore an ORACLE, never a deployable result.

Task B asks whether the image branch's run-level rank correlation is real
run-level signal or an artefact of scoring a label computed from the same
photographs the model saw. Computing the target from odd teeth and the
prediction from even teeth makes per-photo noise independent across the two
sides while leaving true run-level damage shared.
"""

from __future__ import annotations

# Source-tree entry point; no installed package is required.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3] / "src"))


import argparse

import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr

R4_SCALAR = ("runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099"
             "/tables/scalar_predictions.parquet")
V3 = "runs/phm2026_image_target/20260912T052857044116Z-c936a4e3"
VALUE = "per_tooth_damage_candidate_pct"
LOEO_TRAIN = {"EXP-A": "EXP-F", "EXP-B": "EXP-F", "EXP-F": "EXP-B"}


def run_target(teeth: pd.DataFrame, tooth_subset=None) -> pd.Series:
    scoped = teeth if tooth_subset is None else teeth[teeth.tooth_id.isin(tooth_subset)]
    return scoped.groupby(["experiment", "run"])[VALUE].apply(
        lambda s: float(np.sort(s.to_numpy())[-3:].mean())
    )


def run_prediction(preds: pd.DataFrame, tooth_subset=None) -> pd.Series:
    scoped = preds if tooth_subset is None else preds[preds.tooth_id.isin(tooth_subset)]
    per_tooth = scoped.groupby(["experiment", "run", "tooth_id"])["y_pred"].median()
    return per_tooth.groupby(level=[0, 1]).apply(
        lambda s: float(np.sort(s.to_numpy())[-3:].mean())
    )


def clustered_ci(errors, *, draws=10000, seed=20260912):
    rng = np.random.default_rng(seed)
    values = np.empty(draws)
    for i in range(draws):
        picked = rng.integers(0, len(errors), len(errors))
        values[i] = errors[picked].mean()
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def task_a(teeth, preds) -> None:
    print("=" * 78)
    print("TASK A — rank-mapped ORACLE (requires photographs; not deployable)")
    print("=" * 78)
    targets = run_target(teeth)
    image = run_prediction(preds)
    covered = sorted({e for e, _ in image.index})
    print(f"image-branch coverage: {covered} "
          f"({len(image)} runs of {len(targets)})\n")

    rows = []
    for held_out, train_exp in LOEO_TRAIN.items():
        held_has_image = held_out in covered
        train_has_image = train_exp in covered
        if not held_has_image:
            print(f"  fold predict {held_out}: NOT COMPUTABLE — no image predictions "
                  f"to rank the held-out runs")
            continue
        if not train_has_image:
            print(f"  fold predict {held_out} (train {train_exp}): NOT COMPUTABLE as "
                  f"specified — lambda must be fit on {train_exp}, which has no image "
                  f"predictions")
            continue
        train_target = targets.loc[train_exp].to_numpy(dtype=float)
        train_image = image.loc[train_exp].to_numpy(dtype=float)
        mu, sigma = train_target.mean(), train_target.std(ddof=0)

        # lambda fitted on the TRAINING experiment only
        n_train = len(train_image)
        z_train = norm.ppf((pd.Series(train_image).rank().to_numpy() - 0.5) / n_train)
        denominator = float(np.sum((sigma * z_train) ** 2))
        lam = float(np.sum((train_target - mu) * sigma * z_train) / denominator) if denominator else 0.0

        held_target = targets.loc[held_out].to_numpy(dtype=float)
        held_image = image.loc[held_out].to_numpy(dtype=float)
        n = len(held_image)
        z = norm.ppf((pd.Series(held_image).rank().to_numpy() - 0.5) / n)
        predicted = mu + lam * sigma * z
        errors = np.abs(predicted - held_target)
        constant_errors = np.abs(mu - held_target)
        print(f"  fold predict {held_out} (train {train_exp}): lambda={lam:.4f}, "
              f"n={n}, oracle MAE {errors.mean():.4f} vs constant {constant_errors.mean():.4f}")
        rows.append((held_out, errors, constant_errors))

    if not rows:
        print("\n  TASK A NOT COMPUTABLE on any fold.")
        return
    all_errors = np.concatenate([e for _, e, _ in rows])
    all_constant = np.concatenate([c for _, _, c in rows])
    low, high = clustered_ci(all_errors)
    clow, chigh = clustered_ci(all_constant)
    folds = ", ".join(f for f, _, _ in rows)
    print(f"\n  ORACLE over {len(all_errors)} runs (folds: {folds})")
    print(f"    oracle   MAE {all_errors.mean():.4f}  clustered 95% CI [{low:.4f}, {high:.4f}]")
    print(f"    constant MAE {all_constant.mean():.4f}  clustered 95% CI [{clow:.4f}, {chigh:.4f}]")
    print(f"    prediction was ~0.59 against the constant's 0.8042 (full 20-run LOEO)")
    print(f"  NOTE lambda is fitted on TRAIN, so a held-out loss to the constant is")
    print(f"  possible and is not by itself an implementation error.")


def task_b(teeth, preds, *, draws, seed) -> None:
    print("\n" + "=" * 78)
    print("TASK B — odd/even tooth split: run-level signal or shared-photo artefact?")
    print("=" * 78)
    odd = [t for t in range(5, 29) if t % 2 == 1]
    even = [t for t in range(5, 29) if t % 2 == 0]
    print(f"odd teeth  ({len(odd)}): {odd}")
    print(f"even teeth ({len(even)}): {even}")
    print(f"balance: {len(odd)} vs {len(even)} -> {'balanced' if len(odd)==len(even) else 'UNBALANCED'}\n")

    baseline_target = run_target(teeth)
    baseline_image = run_prediction(preds)
    shared = baseline_image.index.intersection(baseline_target.index)
    rho_all = spearmanr(baseline_image.loc[shared], baseline_target.loc[shared]).statistic
    print(f"baseline (all 24 teeth both sides), n={len(shared)}: rho = {rho_all:+.4f}")
    print("  (this is the number under test; the committed LOEO figure is +0.659)\n")

    rng = np.random.default_rng(seed)
    for label, target_teeth, pred_teeth in (
        ("target=ODD, prediction=EVEN", odd, even),
        ("target=EVEN, prediction=ODD", even, odd),
    ):
        t = run_target(teeth, target_teeth)
        p = run_prediction(preds, pred_teeth)
        keys = p.index.intersection(t.index)
        rho = spearmanr(p.loc[keys], t.loc[keys]).statistic
        # permutation null on the same n
        null = np.array([spearmanr(rng.permutation(p.loc[keys].to_numpy()),
                                   t.loc[keys].to_numpy()).statistic
                         for _ in range(draws)])
        print(f"{label}: n={len(keys)}, rho = {rho:+.4f}  "
              f"(null 95% within [{np.percentile(null,2.5):+.3f}, {np.percentile(null,97.5):+.3f}], "
              f"P(null>=obs) = {(null>=rho).mean():.4f})")
        verdict = ("SURVIVES -> run-level signal" if rho >= 0.5
                   else "COLLAPSES -> largely shared-photo" if rho <= 0.2
                   else "INTERMEDIATE")
        print(f"    verdict: {verdict}")
    print("\n  LIMITATION: if lighting varies per SESSION rather than per photo, session")
    print("  effects are shared across the split and survive regardless. This test")
    print("  separates per-photo noise from run-level effects; it CANNOT distinguish")
    print("  run-level damage from run-level lighting.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args(argv)

    teeth = pd.read_parquet(f"{V3}/tables/per_tooth_damage.parquet")
    teeth["run"] = teeth["run"].astype(int)
    teeth["tooth_id"] = teeth["tooth_id"].astype(int)
    preds = pd.read_parquet(R4_SCALAR)
    preds["run"] = preds["run"].astype(int)
    preds["tooth_id"] = preds["tooth_id"].astype(int)
    preds = preds[preds.tooth_id.isin(teeth.tooth_id.unique())]

    task_a(teeth, preds)
    task_b(teeth, preds, draws=args.draws, seed=args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
