#!/usr/bin/env python3
"""TOOTH-SECTOR Steps 2+3 -- the three-row screen, with sign discipline.

Protocol identical to D1 / RAW-VIB: run-level aggregation by mean, target
raw_top3_mean_pct, |rho| >= 0.5, permutation null of 300 draws, sign
consistency across the three experiments. The DAQ summary row is RECOMPUTED
every time as the protocol check.

SIGN DISCIPLINE. Every indicator here is an energy, spread or impulsiveness
measure of the TSA residual. Localised tooth damage should RAISE all of them,
so the physically expected sign is POSITIVE for every feature without
exception. A strong negative survivor is evidence of run-order confounding,
not damage, and is excluded from the L1 count and reported separately.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import sys
sys.path.insert(0, str(Path(__file__).parent))
from l1_screen import screen, run_level_physics, SENSOR, EXPERIMENTS, THRESH

EXPECTED_SIGN = +1   # see module docstring: all indicators rise with damage


def sign_audit(joined: pd.DataFrame, feats: list[str], target: str,
               label: str) -> dict:
    """Per-feature rho in each experiment, then the sign verdict."""
    per = {}
    for e in EXPERIMENTS:
        s = joined[joined.experiment.eq(e)]
        per[e] = {c: spearmanr(s[c].to_numpy(float), s[target]).statistic
                  for c in feats
                  if np.ptp(s[c].to_numpy(float)) > 0
                  and np.isfinite(s[c].to_numpy(float)).all()}
    t = pd.DataFrame(per).dropna()
    same = (np.sign(t).nunique(axis=1) == 1)
    strong = (t.abs() >= THRESH).all(axis=1)
    surv = t[same & strong]
    print(f"\n  SIGN AUDIT -- {label}")
    if not len(surv):
        print("    no sign-consistent, strong-everywhere survivors to audit")
        return {"survivors": [], "correct_sign": [], "wrong_sign": []}
    right, wrong = [], []
    for name, row in surv.iterrows():
        obs = np.sign(row.iloc[0])
        ok = obs == EXPECTED_SIGN
        (right if ok else wrong).append(name)
        print(f"    {name:32s} {row.values.round(3)}  expected + / observed "
              f"{'+' if obs>0 else '-'}  -> {'MATCHES' if ok else 'BACKWARDS'}")
    if wrong:
        print(f"    {len(wrong)} survivor(s) BACKWARDS -> run-order confounding, "
              f"NOT counted toward L1")
    return {"survivors": list(surv.index), "correct_sign": right, "wrong_sign": wrong}


def accel_agreement(joined: pd.DataFrame, feats: list[str], target: str) -> None:
    """A real mechanical effect should show on both accelerometers."""
    pairs = [(c, c.replace("a1", "a2", 1)) for c in feats
             if c.startswith("a1") and c.replace("a1", "a2", 1) in feats]
    if not pairs:
        return
    print(f"\n  ACCEL 1 vs ACCEL 2 agreement ({len(pairs)} paired features)")
    for e in EXPERIMENTS:
        s = joined[joined.experiment.eq(e)]
        r1, r2 = [], []
        for c1, c2 in pairs:
            for c, acc in ((c1, r1), (c2, r2)):
                v = s[c].to_numpy(float)
                acc.append(spearmanr(v, s[target]).statistic
                           if np.ptp(v) > 0 and np.isfinite(v).all() else np.nan)
        r1, r2 = np.array(r1), np.array(r2)
        m = np.isfinite(r1) & np.isfinite(r2)
        agree = float((np.sign(r1[m]) == np.sign(r2[m])).mean()) if m.sum() else np.nan
        corr = spearmanr(r1[m], r2[m]).statistic if m.sum() > 2 else np.nan
        print(f"    {e}: sign agreement {agree:.0%} of {m.sum()} pairs; "
              f"rho(rho_a1, rho_a2) = {corr:+.3f}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sector", default="data/rawvib/sector_file_features.parquet")
    p.add_argument("--physics", default="data/rawvib/file_features.parquet")
    p.add_argument("--draws", type=int, default=300)
    p.add_argument("--seed", type=int, default=20260912)
    p.add_argument("--out", default="data/rawvib/sector_screen.json")
    a = p.parse_args(argv)

    summary = pd.read_parquet(f"{SENSOR}/tables/sensor_run_sequences.parquet")
    tg = summary[["experiment", "run", "raw_top3_mean_pct"]].copy()
    tg["run"] = tg["run"].astype(int)
    T = "raw_top3_mean_pct"
    results = {}

    # ---------- row 1: DAQ summaries, recomputed protocol check ----------
    minute = pd.read_parquet(f"{SENSOR}/tables/minute_feature_table.parquet")
    daq_feats = [c for c in minute.columns
                 if c.endswith(("_mean", "_std", "_median", "_min", "_max", "_last",
                                "_slope_per_sample", "_missing"))]
    daq = minute.groupby(["experiment", "run"])[daq_feats].mean().reset_index()
    daq["run"] = daq["run"].astype(int)
    results["daq"] = screen(daq.merge(tg, on=["experiment", "run"]), daq_feats, T,
                            "ROW 1 - DAQ summaries (recomputed protocol check)",
                            a.draws, a.seed)

    # ---------- row 2: physics, revolution-averaged ----------
    phys = run_level_physics(pd.read_parquet(a.physics), True)
    phys["run"] = phys["run"].astype(int)
    pf = [c for c in phys.columns if c not in ("experiment", "run")]
    j2 = phys.merge(tg, on=["experiment", "run"])
    print()
    results["rev_avg"] = screen(j2, pf, T,
                                "ROW 2 - physics, revolution-averaged", a.draws, a.seed)
    results["rev_avg_signs"] = sign_audit(j2, pf, T, "revolution-averaged")

    # ---------- row 3: physics, per-tooth-sector order statistics ----------
    sec = pd.read_parquet(a.sector)
    ours = [c for c in sec.columns if c.startswith(("a1", "a2"))]
    run_sec = sec.groupby(["experiment", "run"])[ours].mean().reset_index()
    run_sec["run"] = run_sec["run"].astype(int)
    j3 = run_sec.merge(tg, on=["experiment", "run"])
    top3 = [c for c in ours if c.endswith(("_top1", "_top3", "_conc", "_spread"))]
    print()
    results["sector"] = screen(j3, top3, T,
                               "ROW 3 - physics, per-tooth-sector order statistics",
                               a.draws, a.seed)
    results["sector_signs"] = sign_audit(j3, top3, T, "per-tooth-sector")
    accel_agreement(j3, top3, T)

    # ---------- Step 3: the DAQ's own unused Transforms ----------
    daqc = [c for c in sec.columns if c.startswith("daq")]
    out_daq = {}
    if daqc:
        rd = sec.groupby(["experiment", "run"])[daqc].mean().reset_index()
        rd["run"] = rd["run"].astype(int)
        j4 = rd.merge(tg, on=["experiment", "run"])
        dsec = [c for c in daqc if c.endswith(("_top1", "_top3", "_conc", "_spread"))]
        drev = [c for c in daqc if c.endswith("_revmean")]
        print()
        out_daq["revmean"] = screen(j4, drev, T,
                                    "STEP 3 - DAQ Transforms, revolution-averaged",
                                    a.draws, a.seed)
        print()
        out_daq["sector"] = screen(j4, dsec, T,
                                   "STEP 3 - DAQ Transforms, per-tooth-sector",
                                   a.draws, a.seed)
    results["daq_transforms"] = out_daq

    # ---------- the table ----------
    print("\n" + "=" * 84)
    print("THE THREE ROWS  (observed / null median; p = P(null >= observed))")
    print("=" * 84)
    print(f"  {'feature set':38s} {'EXP-A':>14s} {'EXP-B':>14s} {'EXP-F':>14s}  sign-consistent")
    order = [("daq", "DAQ summaries"),
             ("rev_avg", "physics, revolution-averaged"),
             ("sector", "physics, per-sector top-3")]
    for key, name in order:
        r = results[key]
        cells = "".join(
            f"{r['per_experiment'][e]['observed']:>5d}/"
            f"{r['per_experiment'][e]['null_median']:<3.0f} p{r['per_experiment'][e]['p']:<4.2f}"
            for e in EXPERIMENTS)
        print(f"  {name+' ('+str(r['n_features'])+')':38s} {cells}  "
              f"{r['same_sign']}/{r['n_common']} (chance {r['sign_chance']:.0f})")
    for key, name in (("revmean", "DAQ Transforms, revolution-avg"),
                      ("sector", "DAQ Transforms, per-sector")):
        if key in out_daq:
            r = out_daq[key]
            cells = "".join(
                f"{r['per_experiment'][e]['observed']:>5d}/"
                f"{r['per_experiment'][e]['null_median']:<3.0f} p{r['per_experiment'][e]['p']:<4.2f}"
                for e in EXPERIMENTS)
            print(f"  {name+' ('+str(r['n_features'])+')':38s} {cells}  "
                  f"{r['same_sign']}/{r['n_common']} (chance {r['sign_chance']:.0f})")

    f_sec = results["sector"]["per_experiment"]["EXP-F"]
    f_rev = results["rev_avg"]["per_experiment"]["EXP-F"]
    print(f"\n  THE COMPARISON THAT MATTERS -- EXP-F, row 3 vs row 2:")
    print(f"    revolution-averaged : {f_rev['observed']} vs null {f_rev['null_median']:.0f}, p = {f_rev['p']:.3f}")
    print(f"    per-sector top-3    : {f_sec['observed']} vs null {f_sec['null_median']:.0f}, p = {f_sec['p']:.3f}")
    clean = [s for s in results["sector_signs"]["correct_sign"]]
    passed = f_sec["p"] < 0.05 and f_sec["observed"] > f_sec["null_median"]
    print(f"\n  L1 (per-sector, EXP-F): {'PASS' if passed else 'NEGATIVE'}"
          f"   correctly-signed survivors: {len(clean)}")
    results["L1_sector_pass_expf"] = bool(passed)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(results, indent=2, default=str))
    print(f"  wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
