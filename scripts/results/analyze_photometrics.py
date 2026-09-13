#!/usr/bin/env python3
"""Do the blind-validation disagreements have a photometric cause?

The 12 disagreements concentrate in EXP-B run 4 (3 of 3) and EXP-F run 5
(3 of 4) while being flat across experiments, which points at per-run
photographic conditions rather than at a uniformly unreliable damage score.

Computes four per-image statistics over the same ROI the damage heuristic
measures, for all 480 selected images in the v3 target, and reports them per
run. Nothing is fitted and the target is not touched. Photographs are read out
of the archives in memory; nothing is extracted in place.

A null result closes the item: if no run stands out and no statistic tracks
the score, the clustering is more likely chance.
"""

from __future__ import annotations

import argparse
import io
import zipfile
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

V3_RUN = "runs/phm2026_image_target/20260912T052857044116Z-c936a4e3"
DATA_ROOT = "gtc-data-experiment"
ROI = (0.08, 0.12, 0.92, 0.50)
VALUE = "per_tooth_damage_candidate_pct"
STATS = ("mean_intensity", "rms_contrast", "saturated_fraction", "laplacian_variance")
# runs holding the blind-validation disagreements, from INSPECTION_RESULT
DISAGREEMENT_RUNS = {("EXP-B", 4), ("EXP-F", 5)}


def photometrics(rgb: np.ndarray) -> dict[str, float]:
    height, width = rgb.shape[:2]
    x0, y0 = int(round(ROI[0] * width)), int(round(ROI[1] * height))
    x1, y1 = int(round(ROI[2] * width)), int(round(ROI[3] * height))
    grey = cv2.cvtColor(rgb[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY)
    values = grey.astype(np.float64)
    bright = int(np.count_nonzero(grey > 250))
    dark = int(np.count_nonzero(grey < 5))
    return {
        "mean_intensity": float(values.mean()),
        "rms_contrast": float(values.std()),
        "saturated_fraction": float((bright + dark) / values.size),
        "laplacian_variance": float(cv2.Laplacian(grey, cv2.CV_64F).var()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="docs/thesis/PHOTOMETRICS.csv")
    args = parser.parse_args(argv)

    teeth = pd.read_parquet(f"{V3_RUN}/tables/per_tooth_damage.parquet")
    manifest = pd.read_parquet(f"{V3_RUN}/tables/image_manifest.parquet")
    frame = teeth.merge(manifest[["image_id", "archive_path", "archive_member"]],
                        left_on="selected_image_id", right_on="image_id", how="left")
    frame["run"] = frame["run"].astype(int)

    rows = []
    handles: dict[str, zipfile.ZipFile] = {}
    for record in frame.itertuples():
        path = str(record.archive_path)
        if path not in handles:
            handles[path] = zipfile.ZipFile(Path(DATA_ROOT) / path, "r")
        with handles[path].open(record.archive_member, "r") as source:
            data = source.read()
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rows.append({"experiment": record.experiment, "run": int(record.run),
                     "tooth_id": int(record.tooth_id),
                     "damage_score": float(getattr(record, VALUE)),
                     **photometrics(rgb)})
    for handle in handles.values():
        handle.close()
    data = pd.DataFrame(rows)
    data.to_csv(args.out, index=False)
    print(f"computed photometrics for {len(data)} images -> {args.out}\n")

    print("=" * 78)
    print("1. PER-RUN MEANS, with z within each experiment (|z| > 2 flagged)")
    print("=" * 78)
    flagged: set[tuple[str, int]] = set()
    for experiment, scoped in data.groupby("experiment"):
        per_run = scoped.groupby("run")[list(STATS)].mean()
        print(f"\n  {experiment}  ({len(per_run)} runs)")
        header = "   run " + "".join(f"{s[:14]:>17s}" for s in STATS)
        print(header)
        z_scores = {}
        for stat in STATS:
            column = per_run[stat]
            spread = column.std(ddof=0)
            z_scores[stat] = (column - column.mean()) / spread if spread > 0 else column * 0
        for run in per_run.index:
            cells = ""
            for stat in STATS:
                z = z_scores[stat].loc[run]
                mark = "*" if abs(z) > 2 else " "
                if abs(z) > 2:
                    flagged.add((experiment, int(run)))
                cells += f"{per_run.loc[run, stat]:12.2f}{mark}z{z:+.1f}"[:17].rjust(17)
            print(f"   {run:3d} {cells}")
    print(f"\n  runs flagged at |z| > 2: {sorted(flagged) if flagged else 'NONE'}")
    print("  (n = 5, 7 and 8 runs per experiment, so a 2 SD rule is weak here)")

    print("\n" + "=" * 78)
    print("2. THE TWO DISAGREEMENT RUNS, within their own experiment")
    print("=" * 78)
    for experiment, run in sorted(DISAGREEMENT_RUNS):
        scoped = data[data.experiment.eq(experiment)]
        per_run = scoped.groupby("run")[list(STATS)].mean()
        print(f"\n  {experiment} run {run}")
        for stat in STATS:
            column = per_run[stat]
            spread = column.std(ddof=0)
            z = (column.loc[run] - column.mean()) / spread if spread > 0 else 0.0
            rank = int(column.rank().loc[run])
            print(f"    {stat:20s} {column.loc[run]:10.2f}   z = {z:+5.2f}   "
                  f"rank {rank}/{len(column)} within {experiment}")

    print("\n" + "=" * 78)
    print("3. PHOTOMETRIC STATISTIC vs DAMAGE SCORE, within experiment (Spearman)")
    print("=" * 78)
    print(f"  {'':22s}" + "".join(f"{e:>12s}" for e in sorted(data.experiment.unique())))
    for stat in STATS:
        line = f"  {stat:20s}  "
        for experiment in sorted(data.experiment.unique()):
            scoped = data[data.experiment.eq(experiment)]
            rho = spearmanr(scoped[stat], scoped.damage_score).statistic
            line += f"{rho:+12.3f}"
        print(line)
    print("\n  (n = 120, 168 and 192 images; |rho| > ~0.2 is nominally significant here,")
    print("   so read magnitude rather than significance)")

    print("\n" + "=" * 78)
    print("4. OVERLAP: flagged runs vs runs holding the disagreements")
    print("=" * 78)
    overlap = flagged & DISAGREEMENT_RUNS
    print(f"  photometrically flagged : {sorted(flagged) if flagged else 'none'}")
    print(f"  disagreement runs       : {sorted(DISAGREEMENT_RUNS)}")
    print(f"  overlap                 : {sorted(overlap) if overlap else 'NONE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
