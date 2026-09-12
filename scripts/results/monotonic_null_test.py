#!/usr/bin/env python3
"""Null calibration for in-sample monotonic-MSE at n=8.

Re-scoring under the organizer's metric appears to reverse the headline
result: PatchTST's monotonic-MSE on EXP-F beats the constant's, while its raw
MAE loses. This script checks whether that means anything.

The transform is fitted on the same points it scores, as the organizer
specifies. With n=8 an isotonic fit has enough freedom to track noise, and the
constant is the one predictor that provably cannot exploit this -- no monotonic
function reshapes a flat vector. So the comparison is structurally asymmetric
and needs a null before it can be read as evidence.

Two nulls, both against the real EXP-F targets:
  1. predictions drawn as pure noise, unrelated to the target
  2. the real predictions, permuted -- same values, order destroyed

If noise routinely beats the constant, "beats the constant under monotonic-MSE"
is not a finding. Run this before citing any monotonic-MSE comparison at this
sample size.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from pi_multimodal_ad.evaluation.monotonic import monotonic_metrics

CANONICAL_PATCHTST = (
    "runs/phm2026_patchtst_baseline/20260911T193200607744Z-433d4154"
    "/tables/predictions.parquet"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", default=CANONICAL_PATCHTST)
    parser.add_argument("--model", default="patchtst_sensor_regression")
    parser.add_argument("--split", default="test")
    parser.add_argument("--target", default="y_true_raw")
    parser.add_argument("--draws", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args(argv)

    frame = pd.read_parquet(args.predictions)
    scoped = frame[frame.split.eq(args.split) & frame.model_name.eq(args.model)]
    truth = scoped[args.target].to_numpy(dtype=np.float64)
    prediction = scoped.y_pred.to_numpy(dtype=np.float64)

    constant = monotonic_metrics(truth, np.full(len(truth), truth.mean()))
    actual = monotonic_metrics(truth, prediction)
    rng = np.random.default_rng(args.seed)

    noise = np.array(
        [
            monotonic_metrics(truth, rng.normal(size=len(truth)))["monotonic_mse"]
            for _ in range(args.draws)
        ]
    )
    permuted = np.array(
        [
            monotonic_metrics(truth, rng.permutation(prediction))["monotonic_mse"]
            for _ in range(args.draws)
        ]
    )

    print(f"n = {len(truth)}  ({args.model}, split={args.split}, target={args.target})")
    print(f"constant monotonic-MSE : {constant['monotonic_mse']:.4f}")
    print(f"model    monotonic-MSE : {actual['monotonic_mse']:.4f}")
    print(f"apparent improvement   : {constant['monotonic_mse'] - actual['monotonic_mse']:+.4f}")
    print()
    print(f"pure-noise null ({args.draws} draws):")
    print(f"  P(noise beats constant) = {(noise < constant['monotonic_mse']).mean():.4f}")
    print(f"  P(noise beats model)    = {(noise <= actual['monotonic_mse']).mean():.4f}")
    print()
    print(f"permutation null ({args.draws} draws):")
    print(f"  P(permuted beats constant) = {(permuted < constant['monotonic_mse']).mean():.4f}")
    print(f"  P(permuted <= actual)      = {(permuted <= actual['monotonic_mse']).mean():.4f}"
          "   <- permutation p-value")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
