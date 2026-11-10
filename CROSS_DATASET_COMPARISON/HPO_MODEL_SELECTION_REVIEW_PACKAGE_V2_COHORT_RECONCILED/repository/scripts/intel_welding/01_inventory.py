#!/usr/bin/env python3
"""Phase 1 — full inventory of the Intel Robotic Welding dataset.

Every property is MEASURED from the files, not taken from documentation or
from the manifest. Where the manifest and the files disagree, the files win
and the disagreement is recorded.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path("data/Full Dataset")
OUT = Path("artifacts/intel_welding/audits")


def probe_audio(p: Path) -> dict:
    try:
        import soundfile as sf
        info = sf.info(str(p))
        return {"audio_ok": True, "audio_sr": info.samplerate,
                "audio_frames": info.frames, "audio_channels": info.channels,
                "audio_seconds": info.frames / info.samplerate if info.samplerate else np.nan,
                "audio_format": info.format}
    except Exception as exc:
        return {"audio_ok": False, "audio_error": f"{type(exc).__name__}: {exc}"}


def probe_video(p: Path) -> dict:
    try:
        import cv2
        cap = cv2.VideoCapture(str(p))
        if not cap.isOpened():
            return {"video_ok": False, "video_error": "could not open"}
        fps = cap.get(cv2.CAP_PROP_FPS)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ok, _ = cap.read()
        cap.release()
        return {"video_ok": bool(ok), "video_fps": fps, "video_frames": n,
                "video_width": w, "video_height": h,
                "video_seconds": n / fps if fps else np.nan,
                "video_first_frame_readable": bool(ok)}
    except Exception as exc:
        return {"video_ok": False, "video_error": f"{type(exc).__name__}: {exc}"}


def probe_csv(p: Path) -> dict:
    try:
        df = pd.read_csv(p, low_memory=False)
        cols = [c.strip() for c in df.columns]
        out = {"csv_ok": True, "csv_rows": len(df), "csv_ncols": len(cols),
               "csv_columns": "|".join(cols)}
        # duration from the Time column if present
        tcol = next((c for c in df.columns if c.strip().lower() == "time"), None)
        if tcol is not None and len(df) > 1:
            try:
                t = pd.to_timedelta(df[tcol].astype(str).str.strip(), errors="coerce")
                span = (t.max() - t.min()).total_seconds()
                out["csv_seconds"] = float(span) if np.isfinite(span) else np.nan
                out["csv_rate_hz"] = len(df) / span if span and span > 0 else np.nan
            except Exception:
                out["csv_seconds"] = np.nan
        num = df.select_dtypes(include=[np.number])
        out["csv_numeric_cols"] = num.shape[1]
        out["csv_nan_frac"] = float(num.isna().mean().mean()) if num.shape[1] else np.nan
        out["csv_constant_cols"] = int((num.nunique(dropna=True) <= 1).sum()) if num.shape[1] else 0
        return out
    except Exception as exc:
        return {"csv_ok": False, "csv_error": f"{type(exc).__name__}: {exc}"}


def sha1(p: Path, cap: int = 4_000_000) -> str:
    h = hashlib.sha1()
    with open(p, "rb") as fh:
        h.update(fh.read(cap))
    return h.hexdigest()


def process(row: dict) -> dict:
    subdir = ROOT / row["SUBDIRS"]
    rec = dict(row)
    rec["sample_dir_exists"] = subdir.is_dir()
    if not subdir.is_dir():
        rec["status"] = "sample_dir_missing"
        return rec
    sid = subdir.name
    a, v, c = subdir / f"{sid}.flac", subdir / f"{sid}.avi", subdir / f"{sid}.csv"
    # fall back to any file of that type in the directory
    if not a.exists(): a = next(iter(subdir.glob("*.flac")), a)
    if not v.exists(): v = next(iter(subdir.glob("*.avi")), v)
    if not c.exists(): c = next(iter(subdir.glob("*.csv")), c)
    imgs = sorted((subdir / "images").glob("*")) if (subdir / "images").is_dir() else []
    imgs = [p for p in imgs if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")]

    rec.update({"sample_id": sid,
                "audio_path": str(a) if a.exists() else "",
                "video_path": str(v) if v.exists() else "",
                "csv_path": str(c) if c.exists() else "",
                "has_audio": a.exists(), "has_video": v.exists(), "has_csv": c.exists(),
                "n_images": len(imgs),
                "audio_bytes": a.stat().st_size if a.exists() else 0,
                "video_bytes": v.stat().st_size if v.exists() else 0,
                "csv_bytes": c.stat().st_size if c.exists() else 0})
    if a.exists():
        rec.update(probe_audio(a)); rec["audio_sha1"] = sha1(a)
    if v.exists():
        rec.update(probe_video(v)); rec["video_sha1"] = sha1(v)
    if c.exists():
        rec.update(probe_csv(c)); rec["csv_sha1"] = sha1(c)
    rec["n_deployable"] = int(bool(a.exists()) + bool(v.exists()) + bool(c.exists()))
    rec["complete_deployable"] = rec["n_deployable"] == 3
    rec["status"] = "ok"
    return rec


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workers", type=int, default=12)
    p.add_argument("--limit", type=int, default=0)
    a = p.parse_args(argv)

    man = pd.read_csv(ROOT / "manifest.csv")
    rows = man.to_dict("records")
    if a.limit:
        rows = rows[:a.limit]
    print(f"probing {len(rows)} manifest samples with {a.workers} workers", flush=True)
    from multiprocessing import Pool
    out = []
    with Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(process, rows, chunksize=8), 1):
            out.append(r)
            if i % 400 == 0:
                print(f"  {i}/{len(rows)}", flush=True)
    inv = pd.DataFrame(out)
    OUT.mkdir(parents=True, exist_ok=True)
    inv.to_parquet(OUT / "dataset_inventory.parquet", index=False)

    man_hash = hashlib.sha256((ROOT / "manifest.csv").read_bytes()).hexdigest()
    summary = {
        "manifest_sha256": man_hash,
        "n_manifest_rows": int(len(man)),
        "n_probed": int(len(inv)),
        "n_sessions_DIRECTORY": int(inv.DIRECTORY.nunique()),
        "n_unique_SUBDIRS": int(inv.SUBDIRS.nunique()),
        "category_counts": inv.CATEGORY.value_counts().to_dict(),
        "split_counts": inv.SPLIT.value_counts().to_dict(),
        "has_audio": int(inv.has_audio.sum()), "has_video": int(inv.has_video.sum()),
        "has_csv": int(inv.has_csv.sum()),
        "complete_deployable": int(inv.complete_deployable.sum()),
        "n_with_images": int((inv.n_images > 0).sum()),
        "total_images": int(inv.n_images.sum()),
        "audio_sr": inv.get("audio_sr", pd.Series(dtype=float)).value_counts().to_dict(),
        "video_fps": inv.get("video_fps", pd.Series(dtype=float)).round(2).value_counts().head(10).to_dict(),
        "csv_schemas": inv.get("csv_columns", pd.Series(dtype=str)).value_counts().head(5).to_dict(),
    }
    (OUT / "dataset_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps({k: v for k, v in summary.items() if k != "csv_schemas"},
                     indent=2, default=str)[:2600])
    print(f"\nwrote {OUT/'dataset_inventory.parquet'} and dataset_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
