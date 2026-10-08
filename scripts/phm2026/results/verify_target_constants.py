#!/usr/bin/env python3
"""Recompute every target constant directly from the target artifacts.

Verification only: reads per_tooth_damage.parquet from each target run and
recomputes the constants from scratch. Nothing here copies a number from a
document, and nothing here writes or regenerates a target run.

Reports, per version:
  A per-experiment run-level distribution
  B scalar constant, fixed split (train EXP-B) -> run-level MAE on EXP-F
  C profile constant (mean of SORTED training profiles -- order statistics,
    tooth identity discarded) -> tooth-level and run-level MAE on EXP-F
  D LOEO constants (per-fold training mean) -> run-level MAE, clustered CI
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

VALUE = "per_tooth_damage_candidate_pct"
VERSIONS = {
    "v1": "runs/_superseded/phm2026_image_target/20260814T011051111606Z-e7600a8a",
    "v2": "runs/phm2026_image_target/20260814T012054997053Z-e195f6d9",
    "v3": "runs/phm2026_image_target/20260912T052857044116Z-c936a4e3",
}
# LOEO fold -> training experiment, matching scripts/results/loeo_evaluation.py
LOEO_TRAIN = {"EXP-A": "EXP-F", "EXP-B": "EXP-F", "EXP-F": "EXP-B"}


def run_level(teeth: pd.DataFrame) -> pd.DataFrame:
    """Run target = mean of the three largest per-tooth values."""
    rows = []
    for (experiment, run), scoped in teeth.groupby(["experiment", "run"]):
        values = np.sort(scoped[VALUE].to_numpy(dtype=float))
        rows.append({"experiment": experiment, "run": int(run),
                     "top3_mean": float(values[-3:].mean()),
                     "tooth_count": len(values)})
    return pd.DataFrame(rows).sort_values(["experiment", "run"])


def sorted_profiles(teeth: pd.DataFrame, experiment: str) -> np.ndarray:
    rows = []
    scoped = teeth[teeth.experiment.eq(experiment)]
    for _, run_rows in scoped.groupby("run"):
        rows.append(np.sort(run_rows[VALUE].to_numpy(dtype=float)))
    return np.vstack(rows)


def clustered_ci(errors, *, draws, seed):
    rng = np.random.default_rng(seed)
    values = np.empty(draws)
    for i in range(draws):
        picked = rng.integers(0, len(errors), len(errors))
        values[i] = np.mean(errors[picked])
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def report(label: str, directory: str, *, draws: int, seed: int) -> None:
    path = f"{directory}/tables/per_tooth_damage.parquet"
    teeth = pd.read_parquet(path)
    teeth["run"] = teeth["run"].astype(int)
    teeth["tooth_id"] = teeth["tooth_id"].astype(int)
    version = teeth.target_definition_version.unique()[0]
    aggregation = teeth.view_aggregation.unique()[0]
    tooth_ids = sorted(teeth.tooth_id.unique())

    print("=" * 78)
    print(f"{label}: {version}")
    print(f"  artifact : {path}")
    print(f"  across-views rule : {aggregation}")
    print(f"  teeth : {len(tooth_ids)} distinct ({min(tooth_ids)}-{max(tooth_ids)}), "
          f"{len(teeth)} tooth/run rows")
    print("=" * 78)

    runs = run_level(teeth)
    print("\nA. per-experiment run-level top-3 mean")
    print(runs.groupby("experiment").top3_mean.agg(["count", "mean", "std", "min", "max"])
          .round(4).to_string())

    # cross-check against the shipped run_damage_targets.parquet
    try:
        shipped = pd.read_parquet(f"{directory}/tables/run_damage_targets.parquet")
        shipped["run"] = shipped["run"].astype(int)
        merged = runs.merge(shipped[["experiment", "run", "raw_top3_mean_pct"]],
                            on=["experiment", "run"])
        delta = (merged.top3_mean - merged.raw_top3_mean_pct).abs().max()
        print(f"\n  cross-check vs run_damage_targets.parquet: max |diff| = {delta:.10f}")
    except Exception as exc:  # noqa: BLE001
        print(f"\n  cross-check unavailable: {type(exc).__name__}")

    train_runs = runs[runs.experiment.eq("EXP-B")]
    test_runs = runs[runs.experiment.eq("EXP-F")]

    print("\nB. scalar constant, fixed split (train EXP-B -> EXP-F)")
    for name, constant in (("train mean", float(train_runs.top3_mean.mean())),
                           ("train median", float(train_runs.top3_mean.median()))):
        errors = np.abs(test_runs.top3_mean.to_numpy() - constant)
        print(f"   {name:12s} predict {constant:.4f} -> EXP-F run-level MAE "
              f"{errors.mean():.4f}  (n={len(errors)})")

    print("\nC. profile constant = mean of SORTED training profiles")
    print("   (order statistics: each run's teeth sorted ascending BEFORE averaging,")
    print("    so tooth identity is discarded; this is not a positional mean)")
    train_profiles = sorted_profiles(teeth, "EXP-B")
    test_profiles = sorted_profiles(teeth, "EXP-F")
    mean_profile = train_profiles.mean(axis=0)
    tooth_errors = np.abs(test_profiles - mean_profile[None, :])
    tooth_mae = float(tooth_errors.mean())
    run_pred = float(mean_profile[-3:].mean())
    run_errors = np.abs(test_profiles[:, -3:].mean(axis=1) - run_pred)
    print(f"   profile length {len(mean_profile)} (= teeth per run); "
          f"train runs {train_profiles.shape[0]}, test runs {test_profiles.shape[0]}")
    print(f"   tooth-level MAE on EXP-F : {tooth_mae:.4f}  "
          f"(n = {tooth_errors.size} tooth points)")
    print(f"   run-level top-3 MAE      : {run_errors.mean():.4f}  (n = {len(run_errors)})")
    print(f"   NOTE profile top-3 predicts {run_pred:.4f}; scalar train mean predicts "
          f"{train_runs.top3_mean.mean():.4f} -> identical by linearity: "
          f"{np.isclose(run_pred, train_runs.top3_mean.mean())}")

    print("\nD. LOEO constants (per-fold training mean; folds match loeo_evaluation.py)")
    all_errors, detail = [], []
    for held_out, train_exp in LOEO_TRAIN.items():
        constant = float(runs[runs.experiment.eq(train_exp)].top3_mean.mean())
        held = runs[runs.experiment.eq(held_out)]
        errors = np.abs(held.top3_mean.to_numpy() - constant)
        all_errors.extend(errors.tolist())
        detail.append(f"     predict {held_out} (train {train_exp}): constant "
                      f"{constant:.4f}, MAE {errors.mean():.4f}, n={len(errors)}")
    print("\n".join(detail))
    all_errors = np.asarray(all_errors)
    low, high = clustered_ci(all_errors, draws=draws, seed=seed)
    print(f"   LOEO run-level MAE over all {len(all_errors)} runs: {all_errors.mean():.4f} "
          f" clustered 95% CI [{low:.4f}, {high:.4f}]")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args(argv)
    for label, directory in VERSIONS.items():
        report(label, directory, draws=args.draws, seed=args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
