#!/usr/bin/env python3
"""Build a blind image-inspection set for human validation of the pseudo-label.

The question is whether the CV heuristic's damage score corresponds to anything
a human can see. That test is only worth running if the researcher sorts the
images knowing nothing about their scores, so everything here is arranged to
keep the scores out of view until the sorting is finished.

Selection is balanced WITHIN experiment -- 7 highest and 7 lowest per
experiment -- rather than globally. A global top-40/bottom-40 could put most
high scores in one experiment and most low scores in another, letting the
researcher sort correctly by recognising lighting or camera setup instead of
damage, which would look like success and mean nothing.

Reads photographs straight out of the archives into memory. Nothing is
extracted in place and nothing under gtc-data-experiment/ is written.

Prints counts, score ranges and the high/low gap. Prints nothing that links a
token to a group.
"""

from __future__ import annotations

# Source-tree entry point; no installed package is required.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3] / "src"))


import argparse
import csv
import hashlib
import io
import os
import random
import shutil
import zipfile
from pathlib import Path

import pandas as pd
from PIL import Image

V3_RUN = "runs/phm2026_image_target/20260912T052857044116Z-c936a4e3"
DATA_ROOT = "gtc-data-experiment"
VALUE = "per_tooth_damage_candidate_pct"
EXPERIMENTS = ("EXP-A", "EXP-B", "EXP-F")
ROI = (0.08, 0.12, 0.92, 0.50)          # v3 resolved_config image_measurement
CROP_SIZE = (1600, 407)                 # uniform; sources are all 2560x1440
FIXED_MTIME = 1_600_000_000             # identical on every exported file

README = """BLIND TOOTH INSPECTION
======================

There are 42 images in to_sort/. Each is a cropped view of one gear tooth
flank -- the same region the automatic damage measurement looked at.

WHAT TO DO
  1. Look at each image in to_sort/.
  2. Decide: does this tooth look damaged?
  3. Move the file into exactly one of:
         sorted_damaged/   visible damage
         sorted_clean/     no visible damage
         sorted_unsure/    genuinely cannot tell
     Use sorted_unsure/ only when you really cannot decide. How many end up
     there is itself a useful result, so do not force a guess.
  4. If a crop is ambiguous, look up the SAME filename in
     to_sort_fullphoto/ to see the whole photograph.

WHAT YOU ARE NOT TOLD
  The split is not necessarily even. You are not told how many are damaged.
  The filenames are random and encode nothing -- not experiment, run, tooth,
  score, or order. Sorting the directory tells you nothing.

WHEN YOU ARE DONE
  to_sort/ should be empty. Then, and only then, open _KEY_DO_NOT_OPEN/ and
  run:
      python _KEY_DO_NOT_OPEN/score_inspection.py

  The script refuses to run while anything is still left in to_sort/.

  Please note roughly how long the sorting took. Write it here:

      time taken: ______________

Opening the key early invalidates the experiment. There is no way to recover
the blinding once it is broken.
"""


def select(frame: pd.DataFrame, per_group: int) -> pd.DataFrame:
    chosen = []
    print("STEP 1 — selection, balanced within experiment")
    stop = False
    for experiment in EXPERIMENTS:
        scoped = frame[frame.experiment.eq(experiment)].sort_values(VALUE)
        low = scoped.head(per_group).assign(group="low")
        high = scoped.tail(per_group).assign(group="high")
        chosen += [low, high]
        low_range = (low[VALUE].min(), low[VALUE].max())
        high_range = (high[VALUE].min(), high[VALUE].max())
        gap = high_range[0] - low_range[1]
        overlapping = high_range[0] <= low_range[1]
        shared = sorted(set(low.tooth_id) & set(high.tooth_id))
        print(f"  {experiment}: low  [{low_range[0]:.3f}, {low_range[1]:.3f}]   "
              f"high [{high_range[0]:.3f}, {high_range[1]:.3f}]")
        print(f"    gap (lowest high - highest low) = {gap:+.3f}   overlap = {overlapping}")
        print(f"    n = {len(low)} low + {len(high)} high")
        print(f"    teeth appearing in BOTH groups (different runs): "
              f"{shared if shared else 'none'}")
        stop = stop or overlapping
    if stop:
        raise SystemExit(
            "STOP: the high and low groups overlap in score within an experiment. "
            "The selection is not separating anything; the test needs a different design."
        )
    selected = pd.concat(chosen, ignore_index=True)
    print(f"\n  total {len(selected)}; per experiment "
          f"{selected.experiment.value_counts().to_dict()}; "
          f"groups {selected.group.value_counts().to_dict()}")
    return selected


def load_photograph(archive_path: str, member: str) -> Image.Image:
    """Read one photograph out of its archive in memory. Never extracts."""
    full = Path(DATA_ROOT) / archive_path
    with zipfile.ZipFile(full, "r") as archive:
        with archive.open(member, "r") as handle:
            data = handle.read()
    return Image.open(io.BytesIO(data)).convert("RGB")


def strip_and_save(image: Image.Image, destination: Path) -> None:
    """Re-encode from raw pixels so no EXIF or embedded metadata survives."""
    clean = Image.new("RGB", image.size)
    clean.putdata(list(image.getdata()))
    clean.save(destination, format="JPEG", quality=95)
    os.utime(destination, (FIXED_MTIME, FIXED_MTIME))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="scratch/blind_inspection")
    parser.add_argument("--per-group", type=int, default=7)
    parser.add_argument("--seed", type=int, default=20260913)
    args = parser.parse_args(argv)

    teeth = pd.read_parquet(f"{V3_RUN}/tables/per_tooth_damage.parquet")
    manifest = pd.read_parquet(f"{V3_RUN}/tables/image_manifest.parquet")
    frame = teeth.merge(
        manifest[["image_id", "archive_path", "archive_member"]],
        left_on="selected_image_id", right_on="image_id", how="left",
    )
    frame["run"] = frame["run"].astype(int)
    frame["tooth_id"] = frame["tooth_id"].astype(int)
    selected = select(frame, args.per_group)

    # locate every source photograph BEFORE exporting anything
    missing = []
    for archive_path, group in selected.groupby("archive_path"):
        full = Path(DATA_ROOT) / str(archive_path)
        if not full.is_file():
            missing += [(archive_path, m, "archive missing") for m in group.archive_member]
            continue
        with zipfile.ZipFile(full, "r") as archive:
            names = set(archive.namelist())
        missing += [(archive_path, m, "member missing")
                    for m in group.archive_member if m not in names]
    if missing:
        print("\nSTOP: source photographs could not be located:")
        for archive_path, member, reason in missing:
            print(f"  {reason}: {archive_path} :: {member}")
        raise SystemExit(1)
    print(f"  all {len(selected)} source photographs located\n")

    root = Path(args.out)
    if root.exists():
        shutil.rmtree(root)
    to_sort = root / "to_sort"
    full_photo = root / "to_sort_fullphoto"
    key_dir = root / "_KEY_DO_NOT_OPEN"
    for directory in (to_sort, full_photo, key_dir,
                      root / "sorted_damaged", root / "sorted_clean",
                      root / "sorted_unsure"):
        directory.mkdir(parents=True, exist_ok=True)

    # tokens from a seeded shuffle: reproducible, and unrelated to score order
    rng = random.Random(args.seed)
    order = list(range(len(selected)))
    rng.shuffle(order)
    tokens = []
    for position in order:
        digest = hashlib.sha256(f"{args.seed}:{position}".encode()).hexdigest()[:8]
        tokens.append(digest)
    if len(set(tokens)) != len(tokens):
        raise SystemExit("token collision; change --seed")

    print("STEP 2/3 — exporting ROI crops and full photographs, anonymised")
    rows = []
    for token, (_, record) in zip(tokens, selected.iterrows()):
        photo = load_photograph(record.archive_path, record.archive_member)
        width, height = photo.size
        box = (int(round(ROI[0] * width)), int(round(ROI[1] * height)),
               int(round(ROI[2] * width)), int(round(ROI[3] * height)))
        crop = photo.crop(box).resize(CROP_SIZE, Image.LANCZOS)
        strip_and_save(crop, to_sort / f"img_{token}.jpg")
        strip_and_save(photo, full_photo / f"img_{token}.jpg")
        rows.append({
            "token": f"img_{token}.jpg", "experiment": record.experiment,
            "run": int(record.run), "tooth_id": int(record.tooth_id),
            "damage_score": float(record[VALUE]), "group": record.group,
            "original_relative_path": f"{record.archive_path}::{record.archive_member}",
        })

    with open(key_dir / "key.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    scorer = Path(__file__).resolve().parent / "score_blind_inspection.py"
    shutil.copy(scorer, key_dir / "score_inspection.py")
    (root / "README.txt").write_text(README, encoding="utf-8")

    crops = sorted(to_sort.glob("*.jpg"))
    sizes = {Image.open(p).size for p in crops}
    print(f"  to_sort/           {len(crops)} crops, dimensions {sizes}")
    print(f"  to_sort_fullphoto/ {len(list(full_photo.glob('*.jpg')))} full frames")
    print(f"  identical mtime on every file: "
          f"{len({p.stat().st_mtime for p in crops}) == 1}")
    print(f"  workspace: {root}")
    print("\n(no token-to-group information printed by design)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
