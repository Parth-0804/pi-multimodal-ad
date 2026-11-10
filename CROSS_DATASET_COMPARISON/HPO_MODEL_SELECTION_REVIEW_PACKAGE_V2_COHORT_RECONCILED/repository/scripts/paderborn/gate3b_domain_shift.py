#!/usr/bin/env python3
"""ARCH-VAL-PB secondary -- the harder domain shift.

Train on ARTIFICIALLY damaged bearings, test on NATURALLY (fatigue) damaged
ones. This is the documented hard case for this dataset and the closest
analogue to the PHM cross-gear problem.

Reported SEPARATELY from Gate 3 and never merged with it: the protocol is
different (no leave-one-condition-out; the held-out axis is damage origin),
so the numbers are not comparable to the Gate 3 table.

Healthy bearings are placed in TRAIN only, since they belong to neither
damage origin and the test set is meant to be naturally damaged bearings.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import GROUPS, fit_predict, cluster_bootstrap, paired_bootstrap

mae = lambda y, p: float(np.mean(np.abs(y - p)))

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--features", default="data/paderborn/features.parquet")
    p.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    p.add_argument("--epochs", type=int, default=120)
    p.add_argument("--boot", type=int, default=2000)
    p.add_argument("--weight", type=float, default=1.0)
    p.add_argument("--out", default="data/paderborn/gate3b.json")
    a = p.parse_args(argv)

    df = pd.read_parquet(a.features).reset_index(drop=True)
    tr = df.index[df.origin.isin(["artificial", "healthy"])].to_numpy()
    te = df.index[df.origin.eq("real")].to_numpy()
    y = df.severity.to_numpy(float)
    test = df.loc[te]
    print("="*74); print("SECONDARY -- artificial (+healthy) -> real damage"); print("="*74)
    print(f"  train {len(tr)} rows / {df.loc[tr].bearing.nunique()} bearings")
    print(f"  test  {len(te)} rows / {test.bearing.nunique()} bearings")

    both = GROUPS["vib"] + GROUPS["cur"]
    preds = {k: [] for k in ("constant", "vib", "distill", "oracle")}
    for s in a.seeds:
        preds["constant"].append(np.full(len(te), y[tr].mean()))
        preds["vib"].append(fit_predict(df.loc[tr, GROUPS["vib"]].to_numpy(), y[tr],
                                        df.loc[te, GROUPS["vib"]].to_numpy(), s, epochs=a.epochs))
        preds["oracle"].append(fit_predict(df.loc[tr, both].to_numpy(), y[tr],
                                           df.loc[te, both].to_numpy(), s, epochs=a.epochs))
        Xc = df.loc[tr, GROUPS["cur"]].to_numpy()
        teacher = fit_predict(Xc, y[tr], Xc, s, epochs=a.epochs)
        preds["distill"].append(fit_predict(
            df.loc[tr, GROUPS["vib"]].to_numpy(), y[tr],
            df.loc[te, GROUPS["vib"]].to_numpy(), s, epochs=a.epochs,
            teacher_tr=teacher, distill_weight=a.weight))
    arms = {k: np.mean(v, axis=0) for k, v in preds.items()}
    truth = y[te]

    res = {}
    print(f"\n  {'arm':44s} {'MAE':>7s} {'95% CI':>18s}")
    for label, k in (("1 constant (training mean)", "constant"),
                     ("2 vibration only", "vib"),
                     (f"3 vibration + rank distillation (w={a.weight})", "distill"),
                     ("4 oracle: vibration + current", "oracle")):
        pt, lo, hi = cluster_bootstrap(test, arms[k], truth, mae, a.boot, 0)
        print(f"  {label:44s} {pt:7.4f} [{lo:6.4f},{hi:6.4f}]")
        res[label] = {"mae": pt, "ci": [lo, hi]}
    d = paired_bootstrap(test, arms["distill"], arms["vib"], truth, mae, a.boot, 0)
    o = paired_bootstrap(test, arms["oracle"], arms["vib"], truth, mae, a.boot, 0)
    print(f"\n  row 3 - row 2 : {d[0]:+.4f} [{d[1]:+.4f},{d[2]:+.4f}]")
    print(f"  ORACLE GAP    : {o[0]:+.4f} [{o[1]:+.4f},{o[2]:+.4f}]")
    res["paired_distill_minus_vib"] = {"diff": d[0], "ci": [d[1], d[2]]}
    res["oracle_gap"] = {"diff": o[0], "ci": [o[1], o[2]]}
    Path(a.out).write_text(json.dumps(res, indent=2))
    print(f"\n  wrote {a.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
