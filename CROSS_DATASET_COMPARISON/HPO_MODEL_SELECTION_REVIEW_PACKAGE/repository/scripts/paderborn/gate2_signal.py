#!/usr/bin/env python3
"""GATE 2 (ARCH-VAL-PB) -- is there anything to fuse?

Target : damage severity from the official fact sheets (ordinal, healthy = 0)
Protocol: leave-one-operating-condition-out, primary variant ALSO holding out
          bearings (see common.py for why: severity is constant per bearing)
Arms   : constant (training mean) | vibration | motor current | context
Intervals: bearing-clustered bootstrap

GATE CRITERION: vibration alone must beat the constant with a paired
bearing-clustered interval excluding zero.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import GROUPS, folds, fit_predict, cluster_bootstrap, paired_bootstrap

mae = lambda y, p: float(np.mean(np.abs(y - p)))
mse = lambda y, p: float(np.mean((y - p) ** 2))

def run_arm(df, cols, seed, disjoint, nfolds, epochs):
    pred = np.full(len(df), np.nan)
    d = df.reset_index(drop=True)
    for tr, te, _ in folds(d, nfolds, disjoint, seed=seed):
        if cols is None:                              # constant = training mean
            pred[te] = d.severity.to_numpy()[tr].mean()
        else:
            pred[te] = fit_predict(d.loc[tr, cols].to_numpy(),
                                   d.loc[tr, "severity"].to_numpy(float),
                                   d.loc[te, cols].to_numpy(), seed, epochs=epochs)
    return pred

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--features", default="data/paderborn/features.parquet")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--folds", type=int, default=4)
    p.add_argument("--epochs", type=int, default=120)
    p.add_argument("--boot", type=int, default=2000)
    p.add_argument("--out", default="data/paderborn/gate2.json")
    a = p.parse_args(argv)

    df = pd.read_parquet(a.features).reset_index(drop=True)
    print("="*74); print("GATE 2 -- signal check, target = fact-sheet damage severity")
    print("="*74)
    print(f"  rows {len(df)}  bearings {df.bearing.nunique()}  "
          f"conditions {df.condition.nunique()}")
    print("  severity distribution (by bearing):")
    per_b = df.groupby("bearing").severity.first()
    for s, c in per_b.value_counts().sort_index().items():
        print(f"    severity {s}: {c} bearings")
    truth = df.severity.to_numpy(float)

    results = {}
    for disjoint, label in ((True, "PRIMARY: condition + bearing held out"),
                            (False, "SECONDARY: condition held out only (bearings shared)")):
        print("\n" + "="*74); print(label); print("="*74)
        print(f"  {'arm':22s} {'MAE':>7s} {'95% CI':>18s} {'MSE':>8s}")
        arms = {}
        for name, cols in (("constant (train mean)", None), ("vibration only", GROUPS["vib"]),
                           ("motor current only", GROUPS["cur"]), ("context only", GROUPS["ctx"])):
            pred = run_arm(df, cols, a.seed, disjoint, a.folds, a.epochs)
            pt, lo, hi = cluster_bootstrap(df, pred, truth, mae, a.boot, a.seed)
            arms[name] = pred
            print(f"  {name:22s} {pt:7.4f} [{lo:6.4f},{hi:6.4f}] {mse(truth,pred):8.4f}")
            results[f"{'disjoint' if disjoint else 'shared'}|{name}"] = {
                "mae": pt, "ci": [lo, hi], "mse": mse(truth, pred)}
        # paired: vibration vs constant
        d_pt, d_lo, d_hi = paired_bootstrap(df, arms["vibration only"],
                                            arms["constant (train mean)"], truth,
                                            mae, a.boot, a.seed)
        beats = d_hi < 0
        print(f"\n  PAIRED  MAE(vibration) - MAE(constant) = {d_pt:+.4f} "
              f"[{d_lo:+.4f},{d_hi:+.4f}]")
        print(f"  -> vibration {'BEATS' if beats else 'does NOT beat'} the constant "
              f"(interval {'excludes' if beats else 'includes'} zero)")
        results[f"{'disjoint' if disjoint else 'shared'}|paired_vib_minus_const"] = {
            "diff": d_pt, "ci": [d_lo, d_hi], "beats": bool(beats)}

    gate = results["disjoint|paired_vib_minus_const"]["beats"]
    print("\n" + "="*74); print("GATE 2 VERDICT"); print("="*74)
    print(f"  {'PASS -- proceed to Gate 3' if gate else 'FAIL -- stop; the setting is uninformative'}")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(results, indent=2))
    print(f"  wrote {a.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
