#!/usr/bin/env python3
"""GATE 3 (ARCH-VAL-PB) -- does the fusion architecture transfer?

Runs exactly the four arms fixed in the pre-registration, under the Gate 2
protocol, with frozen hyperparameters and shared seeds.

  1 constant                                   the bar
  2 vibration only                             deployable baseline
  3 vibration + rank distillation from current THE ARCHITECTURE
  4 vibration + current at inference            ORACLE (not deployable)

The headline is the paired difference row 3 (at the pre-specified w = 1.0)
minus row 2. The oracle gap is row 4 minus row 2.

w = 0 must reduce row 3 exactly to row 2; this is asserted numerically.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import GROUPS, folds, fit_predict, cluster_bootstrap, paired_bootstrap

mae = lambda y, p: float(np.mean(np.abs(y - p)))
PRIMARY_W = 1.0

def oof(df, seed, nfolds, epochs, weights):
    """One seed: out-of-fold predictions for every arm."""
    d = df.reset_index(drop=True)
    n = len(d)
    out = {"constant": np.full(n, np.nan), "vib": np.full(n, np.nan),
           "oracle": np.full(n, np.nan),
           **{f"distill_w{w}": np.full(n, np.nan) for w in weights}}
    y = d.severity.to_numpy(float)
    for tr, te, _ in folds(d, nfolds, bearing_disjoint=True, seed=0):
        Xv_tr, Xv_te = d.loc[tr, GROUPS["vib"]].to_numpy(), d.loc[te, GROUPS["vib"]].to_numpy()
        Xc_tr = d.loc[tr, GROUPS["cur"]].to_numpy()
        both = GROUPS["vib"] + GROUPS["cur"]
        out["constant"][te] = y[tr].mean()
        out["vib"][te] = fit_predict(Xv_tr, y[tr], Xv_te, seed, epochs=epochs)
        out["oracle"][te] = fit_predict(d.loc[tr, both].to_numpy(), y[tr],
                                        d.loc[te, both].to_numpy(), seed, epochs=epochs)
        # teacher: privileged modality, trained on the training fold only,
        # its in-sample predictions on the training rows are the rank signal
        teacher = fit_predict(Xc_tr, y[tr], Xc_tr, seed, epochs=epochs)
        for w in weights:
            out[f"distill_w{w}"][te] = fit_predict(
                Xv_tr, y[tr], Xv_te, seed, epochs=epochs,
                teacher_tr=teacher, distill_weight=w)
    return out

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--features", default="data/paderborn/features.parquet")
    p.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    p.add_argument("--folds", type=int, default=4)
    p.add_argument("--epochs", type=int, default=120)
    p.add_argument("--boot", type=int, default=2000)
    p.add_argument("--weights", type=float, nargs="*", default=[0.0, 0.1, 0.3, 1.0, 3.0])
    p.add_argument("--exclude", nargs="*", default=[], help="bearings to drop")
    p.add_argument("--out", default="data/paderborn/gate3.json")
    a = p.parse_args(argv)

    df = pd.read_parquet(a.features)
    if a.exclude:
        df = df[~df.bearing.isin(a.exclude)]
    df = df.reset_index(drop=True)
    truth = df.severity.to_numpy(float)
    print("="*78); print("GATE 3 -- does the fusion architecture transfer?")
    print("="*78)
    print(f"  rows {len(df)}  bearings {df.bearing.nunique()}  seeds {a.seeds}"
          + (f"  excluded {a.exclude}" if a.exclude else ""))

    per_seed = {}
    for s in a.seeds:
        print(f"  running seed {s} ...", flush=True)
        per_seed[s] = oof(df, s, a.folds, a.epochs, a.weights)

    # w=0 must reduce exactly to the vibration-only arm
    print("\n" + "-"*78)
    ok = True
    for s in a.seeds:
        same = np.allclose(per_seed[s]["distill_w0.0"], per_seed[s]["vib"],
                           rtol=0, atol=0)
        mx = float(np.max(np.abs(per_seed[s]["distill_w0.0"] - per_seed[s]["vib"])))
        print(f"  REDUCTION TEST seed {s}: w=0 identical to vibration-only: "
              f"{same}  (max abs diff {mx:.3e})")
        ok &= same
    if not ok:
        print("\n  REDUCTION TEST FAILED -- run is void per the pre-registration.")
        return 1

    arms = {k: np.mean([per_seed[s][k] for s in a.seeds], axis=0)
            for k in per_seed[a.seeds[0]]}
    results = {"per_seed_mae": {k: {str(s): mae(truth, per_seed[s][k]) for s in a.seeds}
                                for k in arms}}

    print("\n" + "="*78); print("FOUR ARMS (seed-averaged predictions)"); print("="*78)
    print(f"  {'arm':44s} {'MAE':>7s} {'95% CI':>18s}")
    order = [("1 constant (training mean)", "constant"),
             ("2 vibration only", "vib"),
             (f"3 vibration + rank distillation (w={PRIMARY_W})", f"distill_w{PRIMARY_W}"),
             ("4 oracle: vibration + current at inference", "oracle")]
    for label, key in order:
        pt, lo, hi = cluster_bootstrap(df, arms[key], truth, mae, a.boot, 0)
        print(f"  {label:44s} {pt:7.4f} [{lo:6.4f},{hi:6.4f}]")
        results[label] = {"mae": pt, "ci": [lo, hi]}

    print("\n" + "="*78); print("THE RESULT -- paired differences, bearing-clustered")
    print("="*78)
    d_pt, d_lo, d_hi = paired_bootstrap(df, arms[f"distill_w{PRIMARY_W}"], arms["vib"],
                                        truth, mae, a.boot, 0)
    transfers = d_hi < 0
    print(f"  row 3 - row 2  (distillation vs vibration-only, w={PRIMARY_W})")
    print(f"      {d_pt:+.4f}  95% CI [{d_lo:+.4f}, {d_hi:+.4f}]   width {d_hi-d_lo:.4f}")
    print(f"      -> {'HELPS' if transfers else 'does NOT help'} "
          f"(interval {'excludes' if transfers else 'includes'} zero)")
    o_pt, o_lo, o_hi = paired_bootstrap(df, arms["oracle"], arms["vib"], truth,
                                        mae, a.boot, 0)
    oracle_real = o_hi < 0
    print(f"\n  ORACLE GAP  row 4 - row 2  (what the privileged modality is worth)")
    print(f"      {o_pt:+.4f}  95% CI [{o_lo:+.4f}, {o_hi:+.4f}]   width {o_hi-o_lo:.4f}")
    print(f"      -> privileged modality {'HELPS' if oracle_real else 'does NOT help'} "
          f"even when fully available")
    results["paired_distill_minus_vib"] = {"diff": d_pt, "ci": [d_lo, d_hi],
                                           "helps": bool(transfers)}
    results["oracle_gap"] = {"diff": o_pt, "ci": [o_lo, o_hi], "helps": bool(oracle_real)}

    print("\n" + "="*78); print("DISTILLATION WEIGHT SWEEP (descriptive; best-of-sweep is")
    print("selected on held-out data and is therefore optimistically biased)")
    print("="*78)
    for w in a.weights:
        k = f"distill_w{w}"
        pt = mae(truth, arms[k])
        dp, dl, dh = paired_bootstrap(df, arms[k], arms["vib"], truth, mae, 500, 0)
        star = "  <- pre-specified primary" if w == PRIMARY_W else ""
        print(f"  w={w:<5g} MAE {pt:.4f}   vs row 2: {dp:+.4f} [{dl:+.4f},{dh:+.4f}]{star}")
        results[f"sweep_w{w}"] = {"mae": pt, "diff": dp, "ci": [dl, dh]}

    print("\n" + "="*78); print("VERDICT (pre-registered categories)"); print("="*78)
    if transfers:
        v = "(a) THE ARCHITECTURE TRANSFERS"
    elif oracle_real:
        v = "(b) MECHANISM-LEVEL NEGATIVE -- privileged modality carries information\n      this distillation mechanism does not transfer"
    elif abs(o_pt) < 0.02:
        v = "(c) PRIVILEGED MODALITY ADDS LITTLE even when fully available"
    else:
        v = "(d) UNDERPOWERED -- intervals span zero; no direction claimed"
    print(f"  {v}")
    print(f"\n  interval widths: distillation {d_hi-d_lo:.4f}, oracle {o_hi-o_lo:.4f}")
    results["verdict"] = v
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(results, indent=2))
    print(f"  wrote {a.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
