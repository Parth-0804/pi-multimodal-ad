#!/usr/bin/env python3
"""RAW-VIB Step 1+2 -- angular-domain features from the 102.4 kHz channels.

These channels (Vibration/Accel 1, Accel 2, Encoder) have never been read by
the pipeline, which used only the DAQ's /Context/ and /CI/ summaries.

KINEMATICS, measured in Step 0 and NOT as the task assumed
----------------------------------------------------------
  shaft frequency   23.3334 Hz (1400 rpm)   -- task expected ~3.697 Hz/222 rpm
  mesh frequency    653.32 Hz
  ratio             27.999 -> 28 teeth CONFIRMED (harmonics at 56.0/84.0/112.0)
  samples available 4,389 per revolution    -- task assumed ~28,000
  revolutions/file  ~1,400                  -- task assumed ~88

Because only 4,389 samples/rev exist, the angular grid is 4,096 samples/rev
(2^12), NOT the 2^15 the task suggested: 2^15 would be 7.5x UPSAMPLING and
would manufacture detail that is not in the data. 4,096/rev resolves orders to
2,048, far above the order-112 content of interest. The DAQ's own TSA uses
M=4096, which corroborates the choice.

Archives are read in memory; nothing is ever extracted in place.
"""
from __future__ import annotations
import argparse, io, json, os, sys, zipfile
from pathlib import Path
import h5py, numpy as np, pandas as pd
from scipy.signal import hilbert

FS = 1.0 / 9.765625e-06          # 102400 Hz
N_REV = 4096                     # angular grid, samples per revolution
TEETH = 28
MESH_HARMONICS = (1, 2, 3)       # orders 28, 56, 84
SIDEBANDS = (1, 2, 3)            # +/- k shaft orders, for the SER
CHANNELS = ("Accel 1", "Accel 2")
TAG = {"Accel 1": "a1", "Accel 2": "a2"}


def angular_resample(accel: np.ndarray, enc_deg: np.ndarray) -> np.ndarray:
    """Resample onto a uniform angular grid using the encoder's absolute angle.

    The encoder is an ABSOLUTE ANGLE in degrees (0-360, wrapping), not a pulse
    train, so the shaft angle is obtained by unwrapping rather than by counting
    edges. Returns (n_rev, N_REV); incomplete final revolution dropped.
    """
    theta = np.unwrap(np.deg2rad(enc_deg)) / (2 * np.pi)     # revolutions
    theta -= theta[0]
    if theta[-1] < 2:
        return np.empty((0, N_REV))
    # enforce monotonicity: encoder noise can produce tiny backward steps,
    # which would break np.interp's requirement on the x-coordinate
    theta = np.maximum.accumulate(theta)
    n_rev = int(np.floor(theta[-1]))
    grid = np.arange(n_rev * N_REV, dtype=np.float64) / N_REV
    return np.interp(grid, theta, accel).reshape(n_rev, N_REV)


def order_spectrum(rev: np.ndarray) -> np.ndarray:
    """Complex order spectrum of one averaged revolution. Index = shaft order."""
    return np.fft.rfft(rev) / len(rev)


def residual_of(tsa: np.ndarray) -> np.ndarray:
    """TSA residual: remove mesh harmonics and their first-order sidebands.

    'mesh frequency and its first 3 harmonics' is read as orders 28, 56, 84
    (harmonic indices 1-3). Each is removed together with its first-order
    sidebands at +/- 1 shaft order. Flagged as an interpretation in the report.
    """
    spec = order_spectrum(tsa)
    kill = set()
    for h in MESH_HARMONICS:
        base = h * TEETH
        for off in (-1, 0, 1):
            if 0 <= base + off < len(spec):
                kill.add(base + off)
    spec[list(kill)] = 0
    return np.fft.irfft(spec, n=len(tsa)) * len(tsa)


def moments(x: np.ndarray) -> tuple[float, float, float]:
    d = x - x.mean()
    var = float(np.mean(d**2))
    return var, float(np.mean(d**4)), float(np.mean(d**6))


def crest(x: np.ndarray) -> float:
    r = float(np.sqrt(np.mean(x**2)))
    return float(np.max(np.abs(x)) / r) if r > 0 else np.nan


def channel_features(raw_rev: np.ndarray, tag: str) -> dict[str, float]:
    """All angular-domain indicators for one accelerometer in one file."""
    f: dict[str, float] = {}
    tsa = raw_rev.mean(axis=0)                       # (b) TSA over ~1400 revs
    res = residual_of(tsa)                           # (c) TSA residual
    flat = raw_rev.ravel()

    # (g) broadband, on the raw angular-resampled signal
    f[f"{tag}_bb_rms"] = float(np.sqrt(np.mean(flat**2)))
    v, m4, _ = moments(flat)
    f[f"{tag}_bb_kurt"] = m4 / v**2 if v > 0 else np.nan
    f[f"{tag}_bb_crest"] = crest(flat)

    # TSA and residual shape descriptors
    for name, sig in (("tsa", tsa), ("res", res)):
        v, m4, m6 = moments(sig)
        f[f"{tag}_{name}_rms"] = float(np.sqrt(np.mean(sig**2)))
        f[f"{tag}_{name}_kurt"] = m4 / v**2 if v > 0 else np.nan
        f[f"{tag}_{name}_crest"] = crest(sig)
        f[f"{tag}_{name}_p2p"] = float(sig.max() - sig.min())

    # (d) indicators. FM4 = kurtosis of the residual. M6A = 6th-moment analogue.
    v_r, m4_r, m6_r = moments(res)
    f[f"{tag}_FM4"] = m4_r / v_r**2 if v_r > 0 else np.nan
    f[f"{tag}_M6A"] = m6_r / v_r**3 if v_r > 0 else np.nan
    # NA4 needs a run-level running variance; carry the parts, combine later
    f[f"{tag}_na4_m4"] = m4_r
    f[f"{tag}_na4_var"] = v_r
    # NB4: kurtosis of the envelope of the mesh-band-filtered TSA
    spec = order_spectrum(tsa)
    band = np.zeros_like(spec)
    lo, hi = TEETH - 4, TEETH + 4
    band[lo:hi + 1] = spec[lo:hi + 1]
    narrow = np.fft.irfft(band, n=len(tsa)) * len(tsa)
    env = np.abs(hilbert(narrow))
    v_e, m4_e, _ = moments(env)
    f[f"{tag}_NB4"] = m4_e / v_e**2 if v_e > 0 else np.nan
    f[f"{tag}_nb4_m4"] = m4_e
    f[f"{tag}_nb4_var"] = v_e
    # energy ratio: residual energy relative to the regular (mesh) signal
    reg = tsa - res
    rr, rg = float(np.sqrt(np.mean(res**2))), float(np.sqrt(np.mean(reg**2)))
    f[f"{tag}_energy_ratio"] = rr / rg if rg > 0 else np.nan

    # (e) sideband energy ratio at mesh +/- 1,2,3 shaft orders, harmonics 1-3
    mag = np.abs(spec)
    ser_all = []
    for h in MESH_HARMONICS:
        base = h * TEETH
        if base + max(SIDEBANDS) >= len(mag):
            continue
        sb = sum(mag[base - k] + mag[base + k] for k in SIDEBANDS)
        carrier = mag[base]
        val = float(sb / carrier) if carrier > 0 else np.nan
        f[f"{tag}_ser_h{h}"] = val
        ser_all.append(val)
    f[f"{tag}_ser_mean"] = float(np.nanmean(ser_all)) if ser_all else np.nan

    # (f) envelope spectrum of the residual, energy at tooth-passing harmonics
    env_r = np.abs(hilbert(res))
    env_spec = np.abs(order_spectrum(env_r - env_r.mean()))
    tot = float(env_spec.sum()) or np.nan
    for h in MESH_HARMONICS:
        o = h * TEETH
        f[f"{tag}_env_h{h}"] = float(env_spec[o] / tot) if o < len(env_spec) else np.nan
    f[f"{tag}_env_tpf_frac"] = float(
        sum(env_spec[h * TEETH] for h in MESH_HARMONICS
            if h * TEETH < len(env_spec)) / tot)
    return f


def process(task: tuple) -> dict | None:
    exp, run, zpath, member, idx = task
    try:
        with zipfile.ZipFile(zpath) as z:          # in memory; never extracted
            blob = z.read(member)
        with h5py.File(io.BytesIO(blob), "r") as h:
            enc = h["Vibration/Encoder"][:].astype(np.float64)
            row = {"experiment": exp, "run": run, "file_index": idx,
                   "member": member,
                   "wf_start_time": h["Vibration/Accel 1"].attrs
                                     .get("wf_start_time", b"").decode()
                   if isinstance(h["Vibration/Accel 1"].attrs.get("wf_start_time"), bytes)
                   else str(h["Vibration/Accel 1"].attrs.get("wf_start_time", "")),
                   "gear_id": str(h.attrs.get("Gear ID", ""))}
            theta = np.unwrap(np.deg2rad(enc)) / (2 * np.pi)
            n_rev_total = float(theta[-1] - theta[0])
            dur = len(enc) / FS
            row["n_rev"] = n_rev_total
            row["f_shaft_hz"] = n_rev_total / dur if dur > 0 else np.nan
            # Steady-state test. File index 0 of a run is a SPEED RAMP: it
            # averages ~3.697 Hz over ~88 revolutions, which is exactly the
            # figure the task expected, but at that speed mesh/shaft = 176.7,
            # not an integer. Angular features from a ramp are not comparable
            # with steady-state ones, so speed stability is measured and
            # recorded per file rather than assumed.
            seg = np.array_split(theta, 10)
            rates = np.array([(s[-1] - s[0]) / (len(s) / FS) for s in seg])
            row["f_shaft_min"] = float(rates.min())
            row["f_shaft_max"] = float(rates.max())
            row["speed_ratio"] = float(rates.max() / rates.min()) if rates.min() > 0 else np.inf
            row["steady"] = bool(rates.min() > 20.0 and row["speed_ratio"] < 1.10)
            if n_rev_total < 20:                    # startup/shutdown file
                row["status"] = "too_few_revolutions"
                return row
            for ch in CHANNELS:
                acc = h[f"Vibration/{ch}"][:].astype(np.float64)
                rev = angular_resample(acc, enc)
                if rev.shape[0] < 20:
                    row["status"] = "resample_failed"
                    return row
                row["n_rev_used"] = rev.shape[0]
                row.update(channel_features(rev, TAG[ch]))
            row["status"] = "ok"
            return row
    except Exception as exc:
        return {"experiment": exp, "run": run, "file_index": idx,
                "member": member, "status": f"error: {type(exc).__name__}: {exc}"}


def build_tasks(root: str, n_even: int, n_last: int) -> list[tuple]:
    tasks = []
    for expdir, exp in (("EXP A", "EXP-A"), ("EXP B", "EXP-B"), ("EXP F", "EXP-F")):
        for zpath in sorted(Path(root, expdir).glob("*.zip")):
            run = int(str(zpath.stem).rsplit("Run-", 1)[-1])
            with zipfile.ZipFile(zpath) as z:
                members = sorted(m for m in z.namelist() if m.endswith(".hdf5"))
            if not members:
                continue
            n = len(members)
            pick = set(np.linspace(0, n - 1, min(n_even, n)).round().astype(int))
            pick |= set(range(max(0, n - n_last), n))     # last 10: nearest the photo
            for i in sorted(pick):
                tasks.append((exp, run, str(zpath), members[i], i))
    return tasks


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default="gtc-data-experiment/high_frequency")
    p.add_argument("--even", type=int, default=20)
    p.add_argument("--last", type=int, default=10)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--out", default="data/rawvib/file_features.parquet")
    p.add_argument("--limit", type=int, default=0)
    a = p.parse_args(argv)

    tasks = build_tasks(a.root, a.even, a.last)
    if a.limit:
        tasks = tasks[:a.limit]
    print(f"{len(tasks)} files queued over "
          f"{len({(t[0],t[1]) for t in tasks})} runs; {a.workers} workers", flush=True)
    from multiprocessing import Pool
    rows = []
    with Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(process, tasks, chunksize=1), 1):
            if r: rows.append(r)
            if i % 25 == 0:
                ok = sum(1 for x in rows if x.get("status") == "ok")
                print(f"  {i}/{len(tasks)}  ok={ok}", flush=True)
    df = pd.DataFrame(rows)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(a.out, index=False)
    print(f"\nwrote {a.out}  rows={len(df)}  ok={(df.status=='ok').sum()}")
    bad = df[df.status != "ok"]
    if len(bad):
        print(f"  non-ok {len(bad)}:")
        print(bad.status.value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
