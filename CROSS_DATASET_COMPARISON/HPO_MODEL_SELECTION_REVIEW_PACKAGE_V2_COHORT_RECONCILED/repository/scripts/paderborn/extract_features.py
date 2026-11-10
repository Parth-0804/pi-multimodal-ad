#!/usr/bin/env python3
"""Paderborn KAt bearing dataset -> per-window feature table (ARCH-VAL-PB).

Why this exists rather than using `paderborn-bearing` directly
-------------------------------------------------------------
The pip package's SIGNAL extraction was verified correct against the official
per-bearing fact sheets (see the report): its channel indexing recovers
phase_current_1/2 and vibration_1 properly. It is nonetheless unusable for
this task, because its public surface is only `.vibration_sens`,
`.motor_current` and `.labels`, and it therefore:

  1. attaches NO provenance -- no bearing code, no operating condition, no
     measurement index. Leave-one-operating-condition-out and a
     bearing-clustered bootstrap are both impossible without these.
  2. drops the context channels (speed, torque, force, temperature) entirely,
     which are M_context in this experiment.
  3. derives labels positionally from os.walk directory order, assuming an
     equal file count per bearing.
  4. pads short recordings by repeating the final window.

This module keeps provenance, selects channels BY NAME rather than by
position, and never fabricates samples.

Citation (CC BY-NC 4.0, required by the licence):
  Lessmeier, C., Kimotho, J.K., Zimmer, D., Sextro, W. (2016). Condition
  Monitoring of Bearing Damage in Electromechanical Drive Systems by Using
  Motor Current Signals of Electric Motors: A Benchmark Data Set for
  Data-Driven Classification. European Conference of the PHM Society, 3(1).
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.io import loadmat
from scipy.stats import kurtosis, skew

# channels selected BY NAME, never by position
HIGH_RATE = {"vibration_1": "vib", "phase_current_1": "cur1", "phase_current_2": "cur2"}
CONTEXT   = {"speed": "speed", "torque": "torque", "force": "force",
             "temp_2_bearing_module": "temp"}
FNAME = re.compile(r"^(N\d{2}_M\d{2}_F\d{2})_(K[AIB]?\d+)_(\d+)\.mat$")

# Damage severity from the official fact sheets (Lessmeier et al. 2016 Tab. 4/5).
# Healthy = 0. Artificial and real damages carry a 1-3 extent rating.
SEVERITY = {
    "K001":0,"K002":0,"K003":0,"K004":0,"K005":0,"K006":0,
    "KA01":1,"KA03":2,"KA05":1,"KA06":2,"KA07":1,"KA09":2,
    "KI01":1,"KI03":1,"KI05":1,"KI07":2,"KI08":2,
    "KA04":1,"KA15":1,"KA16":2,"KA22":1,"KA30":1,
    "KI04":1,"KI14":1,"KI16":3,"KI17":1,"KI18":2,"KI21":1,
}
FAULT = {**{f"K00{i}":"healthy" for i in range(1,7)},
         **{c:"outer" for c in ["KA01","KA03","KA05","KA06","KA07","KA09",
                                "KA04","KA15","KA16","KA22","KA30"]},
         **{c:"inner" for c in ["KI01","KI03","KI05","KI07","KI08",
                                "KI04","KI14","KI16","KI17","KI18","KI21"]}}
ORIGIN = {**{f"K00{i}":"healthy" for i in range(1,7)},
          **{c:"artificial" for c in ["KA01","KA03","KA05","KA06","KA07","KA09",
                                      "KI01","KI03","KI05","KI07","KI08"]},
          **{c:"real" for c in ["KA04","KA15","KA16","KA22","KA30",
                                "KI04","KI14","KI16","KI17","KI18","KI21"]}}

def read_channels(path: Path) -> dict[str, np.ndarray]:
    mat = loadmat(path)
    key = [k for k in mat if not k.startswith("__")][0]
    y = mat[key][0, 0]["Y"]
    out = {}
    for i in range(y.shape[1]):
        ch = y[0, i]
        name = str(ch["Name"][0]) if ch["Name"].size else ""
        if name in HIGH_RATE or name in CONTEXT:
            out[name] = np.asarray(ch["Data"], dtype=np.float64).ravel()
    return out

def hi_stats(x: np.ndarray, tag: str) -> dict[str, float]:
    """8 statistics per high-rate channel, mirroring the PHM per-sensor block."""
    if x.size == 0:
        return {f"{tag}_{s}": np.nan for s in
                ("mean","std","rms","skew","kurt","p2p","crest","shape")}
    absx = np.abs(x); rms = float(np.sqrt(np.mean(x**2))); am = float(absx.mean())
    return {f"{tag}_mean": float(x.mean()), f"{tag}_std": float(x.std()),
            f"{tag}_rms": rms, f"{tag}_skew": float(skew(x)),
            f"{tag}_kurt": float(kurtosis(x)),
            f"{tag}_p2p": float(x.max() - x.min()),
            f"{tag}_crest": float(absx.max() / rms) if rms > 0 else np.nan,
            f"{tag}_shape": float(rms / am) if am > 0 else np.nan}

def ctx_stats(x: np.ndarray, tag: str) -> dict[str, float]:
    """6 statistics per context channel."""
    if x.size == 0:
        return {f"{tag}_{s}": np.nan for s in
                ("mean","std","min","max","range","median")}
    return {f"{tag}_mean": float(x.mean()), f"{tag}_std": float(x.std()),
            f"{tag}_min": float(x.min()), f"{tag}_max": float(x.max()),
            f"{tag}_range": float(x.max() - x.min()),
            f"{tag}_median": float(np.median(x))}

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw", default=str(Path.home()/"Datasets/Paderborn/raw"))
    p.add_argument("--out", default="data/paderborn/features.parquet")
    p.add_argument("--windows", type=int, default=4, help="windows per 4 s recording")
    args = p.parse_args(argv)

    files = sorted(Path(args.raw).glob("K*/*.mat"))
    if not files:
        print(f"no .mat under {args.raw}", file=sys.stderr); return 1
    rows, skipped = [], []
    for n, path in enumerate(files):
        m = FNAME.match(path.name)
        if not m:
            skipped.append((path.name, "filename")); continue
        cond, code, meas = m.group(1), m.group(2), int(m.group(3))
        if code not in FAULT:
            skipped.append((path.name, "bearing not in single-fault scope")); continue
        try:
            ch = read_channels(path)
        except Exception as exc:
            skipped.append((path.name, f"read: {exc}")); continue
        vib = ch.get("vibration_1", np.array([]))
        if vib.size == 0:
            skipped.append((path.name, "no vibration")); continue
        # windows are TRUNCATED to equal length, never padded by repetition
        w = vib.size // args.windows
        for k in range(args.windows):
            lo, hi = k*w, (k+1)*w
            feat = {}
            for name, tag in HIGH_RATE.items():
                sig = ch.get(name, np.array([]))
                seg = sig[lo:hi] if sig.size >= hi else np.array([])
                feat.update(hi_stats(seg, tag))
                feat[f"mask_{tag}"] = float(seg.size > 0)
            for name, tag in CONTEXT.items():
                sig = ch.get(name, np.array([]))
                if sig.size >= args.windows:      # slice proportionally
                    cw = sig.size // args.windows
                    seg = sig[k*cw:(k+1)*cw]
                else:                              # too short to window (temp)
                    seg = sig
                feat.update(ctx_stats(seg, tag))
                feat[f"mask_{tag}"] = float(seg.size > 0)
            rows.append({"bearing": code, "condition": cond, "measurement": meas,
                         "window": k, "fault": FAULT[code], "origin": ORIGIN[code],
                         "severity": SEVERITY[code], **feat})
        if n % 200 == 0:
            print(f"  {n}/{len(files)} files", flush=True)

    df = pd.DataFrame(rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.out, index=False)
    meta = ["bearing","condition","measurement","window","fault","origin","severity"]
    feats = [c for c in df.columns if c not in meta]
    print(f"\nwrote {args.out}")
    print(f"  rows {len(df)}  bearings {df.bearing.nunique()}  "
          f"conditions {df.condition.nunique()}  features {len(feats)}")
    print(f"  masks {len([c for c in feats if c.startswith('mask_')])}, "
          f"numeric {len([c for c in feats if not c.startswith('mask_')])}")
    if skipped:
        print(f"  skipped {len(skipped)}: {skipped[:5]}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
