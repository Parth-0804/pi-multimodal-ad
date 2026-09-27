#!/usr/bin/env python3
"""RAW-VIB Step 3 (L1) -- screen the physics features exactly as D1 screened
the DAQ summaries, so the head-to-head is like-for-like.

D1's protocol, reproduced from scripts/results/diagnose_signal_and_monotonicity.py:
  * aggregate to run level by MEAN
  * target = raw_top3_mean_pct from the sensor run-sequence table
  * count features with |rho| >= 0.5 within each experiment
  * permutation null: shuffle the target within the experiment, 300 draws
  * sign consistency across all three experiments (chance ~ n/4)

The DAQ row is RECOMPUTED here, never transcribed from the task statement.
The two feature sets are screened separately and never merged into one table.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

SENSOR = "runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee"
EXPERIMENTS = ("EXP-A", "EXP-B", "EXP-F")
THRESH = 0.5
HELPERS = ("_na4_m4", "_na4_var", "_nb4_m4", "_nb4_var")


def run_level_physics(df: pd.DataFrame, steady_only: bool) -> pd.DataFrame:
    d = df[df.status.eq("ok")].copy()
    d["steady"] = d["steady"].astype(bool)   # stored as object dtype
    if steady_only:
        d = d[d.steady]
    feats = [c for c in d.columns if c.startswith(("a1_", "a2_"))
             and not c.endswith(HELPERS)]
    agg = d.groupby(["experiment", "run"])[feats].mean()
    # NA4 / NB4 use a run-level mean variance in the denominator, which is the
    # point of those indicators; they cannot be formed per file in isolation.
    for tag in ("a1", "a2"):
        for name, m4c, vc in ((f"{tag}_NA4", f"{tag}_na4_m4", f"{tag}_na4_var"),
                              (f"{tag}_NB4run", f"{tag}_nb4_m4", f"{tag}_nb4_var")):
            m4 = d.groupby(["experiment", "run"])[m4c].mean()
            v = d.groupby(["experiment", "run"])[vc].mean()
            agg[name] = m4 / v**2
    return agg.reset_index()


def screen(joined: pd.DataFrame, feats: list[str], target: str, label: str,
           draws: int, seed: int) -> dict:
    print("=" * 78); print(f"{label}   ({len(feats)} features)"); print("=" * 78)
    rng = np.random.default_rng(seed)
    per_exp, out = {}, {"label": label, "n_features": len(feats), "per_experiment": {}}
    for exp in EXPERIMENTS:
        s = joined[joined.experiment.eq(exp)]
        rhos = {}
        for c in feats:
            v = s[c].to_numpy(float)
            if np.ptp(v) == 0 or not np.isfinite(v).all():
                continue
            rhos[c] = spearmanr(v, s[target]).statistic
        per_exp[exp] = pd.Series(rhos).dropna()
        obs = int((per_exp[exp].abs() >= THRESH).sum())
        # permutation null
        tgt = s[target].to_numpy(float)
        mat = s[list(per_exp[exp].index)].to_numpy(float)
        counts = []
        for _ in range(draws):
            sh = rng.permutation(tgt)
            r = np.array([spearmanr(mat[:, j], sh).statistic for j in range(mat.shape[1])])
            counts.append(int((np.abs(r) >= THRESH).sum()))
        counts = np.array(counts)
        p = float((counts >= obs).mean())
        print(f"  {exp} (n={len(s)} runs): {obs}/{len(rhos)} reach |rho|>={THRESH}; "
              f"null median {np.median(counts):.0f}, null p95 {np.percentile(counts,95):.0f}, "
              f"P(null>=obs) = {p:.3f}; max |rho| {per_exp[exp].abs().max():.3f}")
        out["per_experiment"][exp] = {"observed": obs, "n_tested": len(rhos),
                                      "null_median": float(np.median(counts)),
                                      "null_p95": float(np.percentile(counts, 95)),
                                      "p": p,
                                      "max_abs_rho": float(per_exp[exp].abs().max())}
    table = pd.DataFrame(per_exp).dropna()
    same = (np.sign(table).nunique(axis=1) == 1)
    strong_all = (table.abs() >= THRESH).all(axis=1)
    print(f"\n  same sign in all three : {same.sum()} of {len(table)} "
          f"(chance ~ {len(table)*0.25:.0f})")
    print(f"  |rho|>={THRESH} in all three: {strong_all.sum()}")
    surv = table[same & strong_all]
    if len(surv):
        print("  SURVIVORS (consistent sign AND strong everywhere):")
        print(surv.round(3).to_string())
    else:
        print("  no feature is both consistently signed and strong in all three")
    print("\n  strongest by mean |rho|:")
    print(table.assign(mean_abs=table.abs().mean(axis=1))
          .sort_values("mean_abs", ascending=False).head(8).round(3).to_string())
    out.update({"same_sign": int(same.sum()), "n_common": int(len(table)),
                "sign_chance": float(len(table) * 0.25),
                "strong_all": int(strong_all.sum()),
                "survivors": list(surv.index)})
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--physics", default="data/rawvib/file_features.parquet")
    p.add_argument("--draws", type=int, default=300)
    p.add_argument("--seed", type=int, default=20260912)
    p.add_argument("--steady-only", action="store_true", default=True)
    p.add_argument("--out", default="data/rawvib/l1_screen.json")
    a = p.parse_args(argv)

    summary = pd.read_parquet(f"{SENSOR}/tables/sensor_run_sequences.parquet")
    targets = summary[["experiment", "run", "raw_top3_mean_pct"]].copy()
    targets["run"] = targets["run"].astype(int)

    results = {}
    # ---- arm 1: DAQ summaries, recomputed ----
    minute = pd.read_parquet(f"{SENSOR}/tables/minute_feature_table.parquet")
    daq_feats = [c for c in minute.columns
                 if c.endswith(("_mean", "_std", "_median", "_min", "_max", "_last",
                                "_slope_per_sample", "_missing"))]
    daq = minute.groupby(["experiment", "run"])[daq_feats].mean().reset_index()
    daq["run"] = daq["run"].astype(int)
    results["daq"] = screen(daq.merge(targets, on=["experiment", "run"]),
                            daq_feats, "raw_top3_mean_pct",
                            "ARM 1 - DAQ summaries (recomputed, never transcribed)",
                            a.draws, a.seed)

    # ---- arm 2: physics-informed angular-domain features ----
    print()
    phys_raw = pd.read_parquet(a.physics)
    phys = run_level_physics(phys_raw, a.steady_only)
    phys["run"] = phys["run"].astype(int)
    pf = [c for c in phys.columns if c not in ("experiment", "run")]
    nfiles = phys_raw[phys_raw.status.eq("ok") & phys_raw.steady].groupby(
        ["experiment", "run"]).size()
    print(f"(physics run-level from {int(nfiles.sum())} steady files; "
          f"{nfiles.min()}-{nfiles.max()} per run)")
    results["physics"] = screen(phys.merge(targets, on=["experiment", "run"]),
                                pf, "raw_top3_mean_pct",
                                "ARM 2 - physics-informed angular-domain features",
                                a.draws, a.seed)

    # ---- head-to-head ----
    print("\n" + "=" * 78); print("HEAD-TO-HEAD  (observed / null median)"); print("=" * 78)
    print(f"  {'feature set':34s} {'EXP-A':>12s} {'EXP-B':>12s} {'EXP-F':>12s}  sign-consistent")
    for key, name in (("daq", "DAQ summaries"), ("physics", "physics-informed")):
        r = results[key]
        cells = "".join(f"{r['per_experiment'][e]['observed']:>6d}/"
                        f"{r['per_experiment'][e]['null_median']:<5.0f}" for e in EXPERIMENTS)
        print(f"  {name+' ('+str(r['n_features'])+')':34s} {cells}  "
              f"{r['same_sign']}/{r['n_common']} (chance {r['sign_chance']:.0f})")
    fe = results["physics"]["per_experiment"]["EXP-F"]
    print(f"\n  EXP-F is the row that matters (largest, most trustworthy):")
    print(f"    physics observed {fe['observed']}, null median {fe['null_median']:.0f}, "
          f"P(null>=obs) = {fe['p']:.3f}")
    passed = fe["p"] < 0.05 and fe["observed"] > fe["null_median"]
    print(f"\n  L1 VERDICT: {'PASS' if passed else 'NEGATIVE'} in EXP-F")
    results["L1_pass_expf"] = bool(passed)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(results, indent=2, default=str))
    print(f"  wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
