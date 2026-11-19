#!/usr/bin/env python3
"""TOOTH-SECTOR Step 1 -- per-tooth-sector order statistics from the TSA.

The dilution being removed: RAW-VIB reduced a whole averaged revolution
(all 28 teeth) to one scalar, then compared it with a label that is the MEAN
OF THE 3 WORST of 24 teeth. A mean on the feature side against an upper order
statistic on the label side. Here the revolution is cut into 28 tooth sectors
and aggregated as an order statistic, so both sides match.

BOUNDARY HANDLING (the task's "4096/28 = 146" does not tile):
  4096 / 28 = 146.2857..., so 28 sectors of 146 samples cover only 4088.
  Boundaries are therefore placed at round(k * 4096 / 28) for k = 0..28,
  giving sectors that alternate between 146 and 147 samples, covering all
  4096 samples exactly with no gap and no overlap. Sector widths are equal to
  within one sample, which is 0.7% of a sector.

ROTATION INVARIANCE: the 28 sector values are SORTED before any statistic is
taken, so no keyphasor and no absolute tooth registration is needed or
assumed. Sector k does not correspond to physical tooth k.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd

TEETH = 28
N_REV = 4096
BOUNDS = np.round(np.arange(TEETH + 1) * N_REV / TEETH).astype(int)


def sector_stats(sig: np.ndarray) -> dict[str, np.ndarray]:
    """Per-sector indicators for one averaged revolution. Returns 28-vectors."""
    secs = [sig[BOUNDS[k]:BOUNDS[k + 1]] for k in range(TEETH)]
    rms = np.array([np.sqrt(np.mean(s**2)) for s in secs])
    p2p = np.array([s.max() - s.min() for s in secs])
    kurt = np.array([
        (np.mean((s - s.mean())**4) / np.mean((s - s.mean())**2)**2)
        if np.mean((s - s.mean())**2) > 0 else np.nan for s in secs])
    crest = np.array([np.max(np.abs(s)) / r if r > 0 else np.nan
                      for s, r in zip(secs, rms)])
    energy = np.array([np.sum(s**2) for s in secs])
    total = energy.sum()
    efrac = energy / total if total > 0 else np.full(TEETH, np.nan)
    return {"rms": rms, "p2p": p2p, "kurt": kurt, "crest": crest, "efrac": efrac}


def order_features(vals: np.ndarray, prefix: str) -> dict[str, float]:
    """Order statistics of the 28 sector values -- the label's own shape."""
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    if v.size < 4:
        return {f"{prefix}_{s}": np.nan
                for s in ("top1", "top3", "conc", "spread", "revmean")}
    srt = np.sort(v)[::-1]
    mean_all = float(v.mean())
    top3 = float(srt[:3].mean())
    return {f"{prefix}_top1": float(srt[0]),
            f"{prefix}_top3": top3,
            f"{prefix}_conc": top3 / mean_all if mean_all != 0 else np.nan,
            f"{prefix}_spread": float(srt.std()),
            f"{prefix}_revmean": mean_all}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arrays", default="data/rawvib/tsa_arrays.npz")
    p.add_argument("--index", default="data/rawvib/tsa_index.parquet")
    p.add_argument("--out", default="data/rawvib/sector_file_features.parquet")
    a = p.parse_args(argv)

    z = np.load(a.arrays)
    idx = pd.read_parquet(a.index)
    print(f"{len(idx)} files; arrays {sorted(z.files)}")
    print(f"sector widths: {np.unique(np.diff(BOUNDS))} samples "
          f"(counts {np.bincount(np.diff(BOUNDS))[146:148]}), "
          f"total {np.diff(BOUNDS).sum()} of {N_REV}")

    # signals to segment: our residual and TSA per channel, plus the DAQ's own
    signals = {"a1res": "a1_res", "a2res": "a2_res",
               "a1tsa": "a1_tsa", "a2tsa": "a2_tsa",
               "daqres": "daq_residual", "daqtsa": "daq_TSA",
               "daqdif": "daq_difference", "daqeop": "daq_e_op"}
    rows = []
    for i in range(len(idx)):
        row = {}
        for tag, key in signals.items():
            if key not in z.files:
                continue
            sig = z[key][i].astype(np.float64)
            if not np.isfinite(sig).all():
                continue
            st = sector_stats(sig)
            for ind, vals in st.items():
                row.update(order_features(vals, f"{tag}_{ind}"))
        rows.append(row)
    feat = pd.DataFrame(rows)
    out = pd.concat([idx.reset_index(drop=True), feat], axis=1)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(a.out, index=False)
    cols = [c for c in feat.columns]
    print(f"\nwrote {a.out}")
    print(f"  {len(out)} rows, {len(cols)} per-file sector features")
    for fam in ("top1", "top3", "conc", "spread", "revmean"):
        print(f"    {fam}: {sum(c.endswith('_'+fam) for c in cols)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
