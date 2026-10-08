#!/usr/bin/env python3
"""Does the image branch identify WHICH teeth are damaged, or only how damaged?

A claim is in circulation -- and was reported to the supervisor -- that the
image model "correctly picks out which teeth are damaged but gets the severity
wrong". It traces to a teacher-profile check that computed a tooth-indexed
Spearman correlation POOLED across all runs of an experiment.

Pooling is the problem. If run 8 is more damaged than run 1 overall, every
tooth in run 8 outranks every tooth in run 1, so a model with zero ability to
tell teeth apart -- one that predicts only run-level severity -- still scores a
high pooled tooth-level correlation. The pooled number cannot separate "knows
which teeth" from "knows which runs".

Three quantities, which answer different questions:

  pooled rho        what the original claim measured; confounded as above
  within-run rho    per run, across its teeth. THIS is "which teeth", because
                    run severity is constant inside a run and cannot contribute
  between-run rho   run-mean predicted vs run-mean true; the severity signal
                    that pooling silently folds in

Plus shape agreement, which is what survives sorting and is therefore what a
sorted-profile sensor head could ever receive: correlation of the sorted
profiles, and agreement on concentration (top-3 share of run total).

A within-run null is computed by shuffling tooth identity inside each run.
"""

from __future__ import annotations

# Source-tree entry point; no installed package is required.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3] / "src"))


import argparse

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

R4_SCALAR = (
    "runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099"
    "/tables/scalar_predictions.parquet"
)
V3_TEETH = (
    "runs/phm2026_image_target/20260912T052857044116Z-c936a4e3"
    "/tables/per_tooth_damage.parquet"
)
VALUE = "per_tooth_damage_candidate_pct"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", default=R4_SCALAR)
    parser.add_argument("--truth", default=V3_TEETH)
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args(argv)

    preds = pd.read_parquet(args.predictions)
    truth = pd.read_parquet(args.truth)
    truth["run"] = truth["run"].astype(int)
    truth["tooth_id"] = truth["tooth_id"].astype(int)

    # per-tooth teacher value: median across that tooth's views
    teacher = (
        preds.groupby(["experiment", "run", "tooth_id"])["y_pred"].median().reset_index()
    )
    teacher["run"] = teacher["run"].astype(int)
    teacher["tooth_id"] = teacher["tooth_id"].astype(int)

    merged = teacher.merge(
        truth[["experiment", "run", "tooth_id", VALUE]],
        on=["experiment", "run", "tooth_id"],
        how="inner",
    )
    print("coverage after joining teacher to the v3 target:")
    print(
        merged.groupby("experiment")
        .agg(runs=("run", "nunique"), tooth_points=("tooth_id", "size"))
        .to_string()
    )
    missing = sorted(set(truth.experiment.unique()) - set(merged.experiment.unique()))
    if missing:
        print(f"NOT COVERED by the teacher at all: {missing}")
    print()

    rng = np.random.default_rng(args.seed)
    for experiment, scoped in merged.groupby("experiment"):
        pooled = spearmanr(scoped["y_pred"], scoped[VALUE]).statistic

        within, shape, null = [], [], []
        run_pred_means, run_true_means = [], []
        for _, run_rows in scoped.groupby("run"):
            predicted = run_rows["y_pred"].to_numpy(dtype=float)
            actual = run_rows[VALUE].to_numpy(dtype=float)
            if len(predicted) < 3 or np.ptp(predicted) == 0:
                continue
            within.append(spearmanr(predicted, actual).statistic)
            # Shape = what survives sorting. Spearman is useless here (two
            # sorted vectors always correlate +1 by construction), so compare
            # the profile SHAPE after dividing out the run's level: each sorted
            # profile normalised by its own mean, then Pearson between them.
            predicted_shape = np.sort(predicted) / predicted.mean()
            actual_shape = np.sort(actual) / actual.mean()
            shape.append(float(np.corrcoef(predicted_shape, actual_shape)[0, 1]))
            run_pred_means.append(predicted.mean())
            run_true_means.append(actual.mean())
            for _ in range(args.draws // 100):
                null.append(spearmanr(rng.permutation(predicted), actual).statistic)

        within = np.array(within, dtype=float)
        shape = np.array(shape, dtype=float)
        null = np.array(null, dtype=float)
        between = (
            spearmanr(run_pred_means, run_true_means).statistic
            if len(run_pred_means) >= 3
            else np.nan
        )

        print(f"=== {experiment} ({len(within)} runs) ===")
        print(f"  pooled rho (the original claim)   : {pooled:+.4f}")
        print(f"  within-run rho  ('which teeth')   : mean {np.nanmean(within):+.4f}  "
              f"median {np.nanmedian(within):+.4f}  range [{np.nanmin(within):+.4f}, {np.nanmax(within):+.4f}]")
        print(f"  within-run null (teeth shuffled)  : mean {np.nanmean(null):+.4f}  "
              f"95% of null within [{np.nanpercentile(null,2.5):+.4f}, {np.nanpercentile(null,97.5):+.4f}]")
        print(f"  P(null >= observed within-run)    : {(null >= np.nanmean(within)).mean():.4f}")
        print(f"  between-run rho (severity)        : {between:+.4f}")
        print(f"  level-free shape corr (sorted)    : mean {np.nanmean(shape):+.4f}  "
              f"median {np.nanmedian(shape):+.4f}")

        # concentration agreement: does the teacher know how spread the damage is?
        concentration = []
        for _, run_rows in scoped.groupby("run"):
            predicted = np.sort(run_rows["y_pred"].to_numpy(dtype=float))
            actual = np.sort(run_rows[VALUE].to_numpy(dtype=float))
            concentration.append(
                (predicted[-3:].sum() / predicted.sum(), actual[-3:].sum() / actual.sum())
            )
        pred_share, true_share = zip(*concentration)
        print(f"  top-3 share of run total          : teacher {np.mean(pred_share):.4f} "
              f"vs true {np.mean(true_share):.4f}; corr across runs "
              f"{spearmanr(pred_share, true_share).statistic:+.4f}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
