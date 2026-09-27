#!/usr/bin/env python3
"""TOOTH-SECTOR prerequisite: persist the TSA arrays RAW-VIB discarded.

RAW-VIB stored only scalar per-file indicators, so the averaged revolutions
themselves are gone. This re-reads EXACTLY the 472 steady files RAW-VIB used
(taken from its output table, not re-selected) and recomputes the TSA with the
IDENTICAL functions imported from angular_features.py, so this is the same TSA
rather than a second, differently-parameterised extraction.

It also pulls the DAQ's own Transforms/{TSA,residual,difference,e_op}, which
exist in every file and have never been used, averaged over the file's 60
one-second rows to match the granularity of our own TSA. That supports the
Step 3 cross-check on the port.

Archives are read in memory; nothing is extracted in place.
"""
from __future__ import annotations
import argparse, io, zipfile
from pathlib import Path
import h5py, numpy as np, pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent))
from angular_features import angular_resample, residual_of, CHANNELS, TAG, N_REV

DAQ_KEYS = ("TSA", "residual", "difference", "e_op")


def process(task):
    exp, run, idx, zpath, member = task
    try:
        with zipfile.ZipFile(zpath) as z:
            blob = z.read(member)
        out = {"experiment": exp, "run": run, "file_index": idx, "member": member}
        arrays = {}
        with h5py.File(io.BytesIO(blob), "r") as h:
            enc = h["Vibration/Encoder"][:].astype(np.float64)
            for ch in CHANNELS:
                rev = angular_resample(h[f"Vibration/{ch}"][:].astype(np.float64), enc)
                if rev.shape[0] < 20:
                    return None
                tsa = rev.mean(axis=0)
                arrays[f"{TAG[ch]}_tsa"] = tsa.astype(np.float32)
                arrays[f"{TAG[ch]}_res"] = residual_of(tsa).astype(np.float32)
            for k in DAQ_KEYS:
                p = f"Transforms/{k}"
                arrays[f"daq_{k}"] = (h[p][:].astype(np.float64).mean(axis=0).astype(np.float32)
                                      if p in h else np.full(N_REV, np.nan, np.float32))
        return out, arrays
    except Exception as exc:
        print(f"  fail {member}: {type(exc).__name__}: {exc}", flush=True)
        return None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--features", default="data/rawvib/file_features.parquet")
    p.add_argument("--root", default="gtc-data-experiment/high_frequency")
    p.add_argument("--workers", type=int, default=12)
    p.add_argument("--out", default="data/rawvib/tsa_arrays.npz")
    p.add_argument("--index", default="data/rawvib/tsa_index.parquet")
    a = p.parse_args(argv)

    df = pd.read_parquet(a.features)
    df = df[df.status.eq("ok")].copy()
    df["steady"] = df["steady"].astype(bool)
    df = df[df.steady]
    zmap = {}
    for expdir, exp in (("EXP A", "EXP-A"), ("EXP B", "EXP-B"), ("EXP F", "EXP-F")):
        for zp in sorted(Path(a.root, expdir).glob("*.zip")):
            zmap[(exp, int(str(zp.stem).rsplit("Run-", 1)[-1]))] = str(zp)
    tasks = [(r.experiment, int(r.run), int(r.file_index),
              zmap[(r.experiment, int(r.run))], r.member) for r in df.itertuples()]
    print(f"recomputing TSA for {len(tasks)} steady files (same list as RAW-VIB)",
          flush=True)

    from multiprocessing import Pool
    rows, store = [], {}
    with Pool(a.workers) as pool:
        for i, res in enumerate(pool.imap(process, tasks, chunksize=1), 1):
            if res is None:
                continue
            meta, arrays = res
            rows.append(meta)
            for k, v in arrays.items():
                store.setdefault(k, []).append(v)
            if i % 50 == 0:
                print(f"  {i}/{len(tasks)}", flush=True)
    index = pd.DataFrame(rows)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, **{k: np.stack(v) for k, v in store.items()})
    index.to_parquet(a.index, index=False)
    print(f"\nwrote {a.out} and {a.index}")
    print(f"  files {len(index)}   arrays {sorted(store)}")
    print(f"  shape per array {np.stack(store['a1_tsa']).shape}")
    daq_ok = np.isfinite(np.stack(store['daq_TSA'])).all(axis=1).sum()
    print(f"  DAQ Transforms present in {daq_ok}/{len(index)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
