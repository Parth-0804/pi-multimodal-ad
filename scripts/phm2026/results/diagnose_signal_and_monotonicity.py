#!/usr/bin/env python3
"""D1: does any single feature track the target within experiments?
D2: is the target monotone in run index, and is the departure bigger than
    measurement noise?

D1 notes. Correlations are computed WITHIN each experiment, because pooling
reintroduces the level confound. That leaves n = 5 / 7 / 8 runs, where |rho|
>= 0.5 is cheap: with 72 features x 3 experiments there are 216 chances, so
some will clear any fixed threshold by luck. Two guards are therefore applied:
a permutation null giving the expected number of false passes, and a
sign-consistency test -- a feature carrying real signal should lean the same
way in all three experiments, which luck does not reproduce.

D2 notes. Spall does not heal, so a spall-area label should be non-decreasing
in run index. Isotonic regression of target on run index measures the
departure. The key question is whether that departure exceeds measurement
noise, which is estimable here without new data: a handful of teeth were
photographed more than once in the same run, and the spread across those
repeat photographs of an unchanged tooth is a direct repeatability estimate.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.isotonic import IsotonicRegression

SENSOR = "runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee"
IMAGE_V3 = "runs/phm2026_image_target/20260912T052857044116Z-c936a4e3"
VALUE = "per_tooth_damage_candidate_pct"
EXPERIMENTS = ("EXP-A", "EXP-B", "EXP-F")


def d1(minute: pd.DataFrame, targets: pd.DataFrame, *, draws: int, seed: int) -> None:
    feature_columns = [
        c for c in minute.columns
        if c.endswith(("_mean", "_std", "_median", "_min", "_max", "_last",
                       "_slope_per_sample", "_missing"))
    ]
    print(f"D1: {len(feature_columns)} feature columns, aggregated to run level by "
          "mean across each run's minutes\n")

    run_level = (
        minute.groupby(["experiment", "run"])[feature_columns].mean().reset_index()
    )
    joined = run_level.merge(targets, on=["experiment", "run"], how="inner")

    per_experiment: dict[str, pd.Series] = {}
    for experiment in EXPERIMENTS:
        scoped = joined[joined.experiment.eq(experiment)]
        rhos = {}
        for column in feature_columns:
            values = scoped[column].to_numpy(dtype=float)
            if np.ptp(values) == 0 or not np.isfinite(values).all():
                continue
            rhos[column] = spearmanr(values, scoped.raw_top3_mean_pct).statistic
        per_experiment[experiment] = pd.Series(rhos).dropna()
        n = len(scoped)
        strong = per_experiment[experiment].abs() >= 0.5
        print(f"  {experiment} (n={n} runs): {strong.sum()} of {len(rhos)} features "
              f"reach |rho| >= 0.5; max |rho| = {per_experiment[experiment].abs().max():.3f}")

    # permutation null: how many would clear 0.5 with the target shuffled?
    rng = np.random.default_rng(seed)
    print("\n  permutation null (target shuffled within experiment):")
    for experiment in EXPERIMENTS:
        scoped = joined[joined.experiment.eq(experiment)]
        counts = []
        target = scoped.raw_top3_mean_pct.to_numpy(dtype=float)
        matrix = scoped[list(per_experiment[experiment].index)].to_numpy(dtype=float)
        for _ in range(draws):
            shuffled = rng.permutation(target)
            rhos = np.array([spearmanr(matrix[:, j], shuffled).statistic
                             for j in range(matrix.shape[1])])
            counts.append(int((np.abs(rhos) >= 0.5).sum()))
        observed = int((per_experiment[experiment].abs() >= 0.5).sum())
        counts = np.array(counts)
        print(f"    {experiment}: observed {observed}, null median {np.median(counts):.0f}, "
              f"null 95th pct {np.percentile(counts, 95):.0f}, "
              f"P(null >= observed) = {(counts >= observed).mean():.3f}")

    # sign consistency: the real test
    table = pd.DataFrame(per_experiment).dropna()
    same_sign = (np.sign(table) .nunique(axis=1) == 1)
    all_strong = (table.abs() >= 0.5).all(axis=1)
    print(f"\n  features with the SAME SIGN in all three experiments: "
          f"{same_sign.sum()} of {len(table)}  (chance ~ {len(table) * 0.25:.0f})")
    print(f"  features with |rho| >= 0.5 in ALL three experiments: {all_strong.sum()}")
    survivors = table[same_sign & all_strong]
    if len(survivors):
        print("\n  survivors (consistent sign AND |rho| >= 0.5 everywhere):")
        print(survivors.round(3).to_string())
    else:
        print("\n  no feature is both consistently signed and strong in all three.")
    print("\n  strongest by mean |rho| across experiments:")
    print(table.assign(mean_abs=table.abs().mean(axis=1))
               .sort_values("mean_abs", ascending=False).head(8).round(3).to_string())


def d2(targets: pd.DataFrame, teeth: pd.DataFrame) -> None:
    print("\n\nD2: monotonicity of the target in run index\n")
    for experiment in EXPERIMENTS:
        scoped = targets[targets.experiment.eq(experiment)].sort_values("run")
        runs = scoped.run.to_numpy(dtype=float)
        values = scoped.raw_top3_mean_pct.to_numpy(dtype=float)
        fitted = IsotonicRegression(increasing=True).fit_transform(runs, values)
        residual = float(np.sum((values - fitted) ** 2))
        total = float(np.sum((values - values.mean()) ** 2))
        unexplained = residual / total if total > 0 else np.nan
        drops = int((np.diff(values) < 0).sum())
        print(f"  {experiment}: {' '.join(f'{v:.2f}' for v in values)}")
        print(f"    isotonic leaves {unexplained:6.1%} of variance unexplained; "
              f"{drops} of {len(values)-1} run-to-run steps go DOWN")

    # per-tooth monotonicity: spall on tooth k should not shrink
    print("\n  per-tooth trajectories (a tooth's own value across runs):")
    for experiment in EXPERIMENTS:
        scoped = teeth[teeth.experiment.eq(experiment)]
        decreases, steps, worst = 0, 0, 0.0
        for _, tooth_rows in scoped.groupby("tooth_id"):
            ordered = tooth_rows.sort_values("run")[VALUE].to_numpy(dtype=float)
            diffs = np.diff(ordered)
            decreases += int((diffs < 0).sum())
            steps += len(diffs)
            if len(diffs):
                worst = min(worst, float(diffs.min()))
        print(f"    {experiment}: {decreases}/{steps} tooth-to-next-run steps decrease "
              f"({decreases/steps:.1%}); largest single drop {worst:.3f} pp")


def measurement_noise(images: pd.DataFrame) -> None:
    print("\n  measurement repeatability, from teeth photographed more than once "
          "in the SAME run (the tooth cannot have changed between shots):")
    scoped = images[images.decoding_status.eq("ok") & images.run.notna()].copy()
    scoped["run"] = scoped["run"].astype(int)
    scoped["tooth_id"] = scoped["tooth_id"].astype(int)
    canonical = scoped[scoped.image_type.eq("canonical_tooth")]
    groups = canonical.groupby(["experiment", "run", "tooth_id"])["damage_candidate_area_pct"]
    repeats = groups.agg(["count", "min", "max", "std"])
    repeats = repeats[repeats["count"] > 1]
    if repeats.empty:
        print("    none found")
        return
    spread = (repeats["max"] - repeats["min"])
    print(f"    {len(repeats)} repeated canonical teeth; spread (max-min) "
          f"mean {spread.mean():.3f} pp, max {spread.max():.3f} pp")
    print(repeats.round(3).to_string())

    # close-ups repeat far more often; same logic, much larger sample
    closeup = scoped[scoped.image_type.eq("camera_sequence")]
    groups = closeup.groupby(["experiment", "run", "tooth_id"])["damage_candidate_area_pct"]
    repeats = groups.agg(["count", "min", "max", "std"])
    repeats = repeats[repeats["count"] > 1]
    spread = repeats["max"] - repeats["min"]
    print(f"\n    {len(repeats)} repeated close-up teeth (10 shots each): spread "
          f"mean {spread.mean():.3f} pp, median {spread.median():.3f} pp; "
          f"within-tooth std mean {repeats['std'].mean():.3f} pp")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args(argv)

    minute = pd.read_parquet(f"{SENSOR}/tables/minute_feature_table.parquet")
    summary = pd.read_parquet(f"{SENSOR}/tables/sensor_run_sequences.parquet")
    targets = summary[["experiment", "run", "raw_top3_mean_pct"]].copy()
    targets["run"] = targets["run"].astype(int)
    teeth = pd.read_parquet(f"{IMAGE_V3}/tables/per_tooth_damage.parquet")
    teeth["run"] = teeth["run"].astype(int)
    teeth["tooth_id"] = teeth["tooth_id"].astype(int)
    images = pd.read_parquet(f"{IMAGE_V3}/tables/image_manifest.parquet")

    d1(minute, targets, draws=args.draws, seed=args.seed)
    d2(targets, teeth)
    measurement_noise(images)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
