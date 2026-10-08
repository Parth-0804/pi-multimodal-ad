#!/usr/bin/env python3
"""AnomalyDINO-style change detection on the 42 blind-validated images only.

Question: could a different labelling method agree with human judgement better
than the CV heuristic's 78.9%?

Method. For each validated image, the nominal reference is THE SAME TOOTH
photographed at baseline (break_in / test_start / pre_run) in the same
experiment. DINOv2 patch features are extracted over the same ROI the
heuristic measures; each query patch is matched to its nearest baseline patch
by cosine distance; the image score is the mean of the top-q% patch distances.

Using a per-tooth bank makes this true change detection rather than generic
anomaly detection: a benign machining mark present at baseline is nominal for
that tooth and is not flagged. Nearest-neighbour patch matching also tolerates
the camera misalignment between sessions that would defeat pixel differencing.

The bank is per-experiment-and-tooth, never pooled across experiments, so the
rig/lighting confound is not reintroduced through the reference.

To compare like with like, the score is converted to a call using the SAME
construction the heuristic used: within each experiment, rank the 14 validated
images and call the top 7 damaged and the bottom 7 clean.
"""

from __future__ import annotations

import argparse
import csv
import io
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from scipy.stats import spearmanr

V3 = "runs/phm2026_image_target/20260912T052857044116Z-c936a4e3"
DATA_ROOT = "gtc-data-experiment"
ROI = (0.08, 0.12, 0.92, 0.50)
BASELINE_STAGES = ("break_in", "test_start", "pre_run")
PATCH = 14
WIDTH, HEIGHT = 728, 182          # multiples of 14; preserves the wide ROI aspect
TOP_Q = 0.01                      # AnomalyDINO aggregates the worst 1% of patches


def load_roi(archive_path: str, member: str, handles: dict) -> Image.Image:
    if archive_path not in handles:
        handles[archive_path] = zipfile.ZipFile(Path(DATA_ROOT) / archive_path, "r")
    with handles[archive_path].open(member, "r") as source:
        data = source.read()
    image = Image.open(io.BytesIO(data)).convert("RGB")
    width, height = image.size
    box = (int(round(ROI[0] * width)), int(round(ROI[1] * height)),
           int(round(ROI[2] * width)), int(round(ROI[3] * height)))
    return image.crop(box).resize((WIDTH, HEIGHT), Image.LANCZOS)


def features(model, images: list[Image.Image], mean, std) -> torch.Tensor:
    batch = []
    for image in images:
        array = torch.from_numpy(np.asarray(image, dtype=np.float32) / 255.0)
        batch.append(((array.permute(2, 0, 1) - mean) / std))
    with torch.no_grad():
        out = model(pixel_values=torch.stack(batch)).last_hidden_state[:, 1:, :]
    return torch.nn.functional.normalize(out, dim=-1)


def reconstruct_calls(report: Path, key: dict[str, dict]) -> dict[str, str]:
    """Recover the 42 human calls from the ingested inspection report.

    The report is lossless about this even though it never lists the calls as
    such: it names every MISCLASSIFIED token (call = the opposite of its group)
    and every UNSURE token, and by construction each remaining token was called
    the way its group predicts. The counts it prints are used as a checksum, so
    a mis-parse fails loudly instead of silently relabelling images.
    """
    expected = {"high": "damaged", "low": "clean"}
    opposite = {"damaged": "clean", "clean": "damaged"}
    calls: dict[str, str] = {}
    section = None
    for line in report.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("MISCLASSIFIED"):
            section = "wrong"
            continue
        if stripped.startswith("UNSURE"):
            section = "unsure"
            continue
        if not stripped.startswith("img_"):
            if stripped.startswith("="):
                section = None
            continue
        token = stripped.split()[0]
        if token not in key:
            raise SystemExit(f"report names {token}, which is not in the key")
        if section == "wrong":
            calls[token] = opposite[expected[key[token]["group"]]]
        elif section == "unsure":
            calls[token] = "unsure"
    parsed_wrong = sum(1 for t, c in calls.items()
                       if c != "unsure" and c != expected[key[t]["group"]])
    parsed_unsure = sum(1 for c in calls.values() if c == "unsure")
    if (parsed_wrong, parsed_unsure) != (8, 4):
        raise SystemExit(f"checksum failed: parsed {parsed_wrong} misclassified and "
                         f"{parsed_unsure} unsure; the report states 8 and 4")
    for token, record in key.items():
        calls.setdefault(token, expected[record["group"]])
    agree = sum(1 for t, c in calls.items()
                if c != "unsure" and c == expected[key[t]["group"]])
    scored = sum(1 for c in calls.values() if c != "unsure")
    if (agree, scored) != (30, 38):
        raise SystemExit(f"checksum failed: reconstructed {agree}/{scored}; "
                         f"the report states 30/38")
    print(f"reconstructed 42 human calls from {report.name} "
          f"(checksum 30/38 agreement, 4 unsure -- matches the report)\n")
    return calls


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", default="scratch/blind_inspection/_KEY_DO_NOT_OPEN/key.csv")
    parser.add_argument("--result", default="scratch/blind_inspection/"
                        "INSPECTION_RESULT_20260913T204715Z.md",
                        help="ingested blind-inspection report; human calls are "
                             "reconstructed from its MISCLASSIFIED and UNSURE lists")
    parser.add_argument("--model", default="facebook/dinov2-small")
    args = parser.parse_args(argv)

    from transformers import AutoModel
    model = AutoModel.from_pretrained(args.model).eval()
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

    key = {r["token"]: r for r in csv.DictReader(open(args.key))}
    calls = reconstruct_calls(Path(args.result), key)

    manifest = pd.read_parquet(f"{V3}/tables/image_manifest.parquet")
    teeth = pd.read_parquet(f"{V3}/tables/per_tooth_damage.parquet")
    teeth["run"] = teeth["run"].astype(int)
    teeth["tooth_id"] = teeth["tooth_id"].astype(int)
    lookup = manifest.set_index("image_id")[["archive_path", "archive_member"]]
    baseline = manifest[manifest.inspection_stage.isin(BASELINE_STAGES)].copy()
    baseline["tooth_id"] = baseline["tooth_id"].astype(int)

    handles: dict = {}
    banks: dict[tuple[str, int], torch.Tensor] = {}
    rows = []
    print(f"scoring {len(key)} validated images against per-tooth baselines\n")
    for token, record in key.items():
        experiment, tooth = record["experiment"], int(record["tooth_id"])
        bank_key = (experiment, tooth)
        if bank_key not in banks:
            refs = baseline[baseline.experiment.eq(experiment) & baseline.tooth_id.eq(tooth)]
            images = [load_roi(r.archive_path, r.archive_member, handles)
                      for r in refs.itertuples()]
            if not images:
                raise SystemExit(f"no baseline for {bank_key}")
            banks[bank_key] = features(model, images, mean, std).reshape(-1, 384)
        selected = teeth[teeth.experiment.eq(experiment)
                         & teeth.run.eq(int(record["run"]))
                         & teeth.tooth_id.eq(tooth)].iloc[0]
        source = lookup.loc[selected.selected_image_id]
        query = features(model, [load_roi(source.archive_path, source.archive_member, handles)],
                         mean, std)[0]
        distance = 1.0 - (query @ banks[bank_key].T).max(dim=1).values
        worst = torch.topk(distance, max(1, int(len(distance) * TOP_Q))).values
        rows.append({"token": token, "experiment": experiment,
                     "run": int(record["run"]), "tooth_id": tooth,
                     "group": record["group"],
                     "heuristic_score": float(record["damage_score"]),
                     "human": calls[token],
                     "dino_score": float(worst.mean()),
                     "n_baseline": len(banks[bank_key]) // (WIDTH // PATCH * (HEIGHT // PATCH))})
    for handle in handles.values():
        handle.close()
    data = pd.DataFrame(rows)

    # same construction the heuristic used: top 7 / bottom 7 within each experiment
    data["dino_call"] = ""
    for experiment, scoped in data.groupby("experiment"):
        ranked = scoped.sort_values("dino_score")
        data.loc[ranked.index[:7], "dino_call"] = "clean"
        data.loc[ranked.index[7:], "dino_call"] = "damaged"

    scored = data[data.human.ne("unsure")]
    dino_hits = int((scored.dino_call == scored.human).sum())
    heur_hits = int((scored.group.map({"high": "damaged", "low": "clean"}) == scored.human).sum())
    n = len(scored)

    print("=" * 70)
    print("AGREEMENT WITH HUMAN JUDGEMENT (unsure excluded)")
    print("=" * 70)
    print(f"  n scored                     : {n}  ({len(data) - n} unsure excluded)")
    print(f"  CV heuristic                 : {heur_hits}/{n} = {heur_hits/n:.1%}")
    print(f"  AnomalyDINO change detection : {dino_hits}/{n} = {dino_hits/n:.1%}")
    print(f"  difference                   : {(dino_hits-heur_hits)/n:+.1%} "
          f"({dino_hits-heur_hits:+d} images)")

    print("\n  within experiment:")
    for experiment, scoped in scored.groupby("experiment"):
        d = int((scoped.dino_call == scoped.human).sum())
        h = int((scoped.group.map({"high": "damaged", "low": "clean"}) == scoped.human).sum())
        print(f"    {experiment}: heuristic {h}/{len(scoped)}   dino {d}/{len(scoped)}")

    human_numeric = scored.human.map({"clean": 0, "damaged": 1})
    print("\n  rank correlation with the human call (n = %d):" % n)
    print(f"    heuristic score vs human : rho = "
          f"{spearmanr(scored.heuristic_score, human_numeric).statistic:+.3f}")
    print(f"    dino score      vs human : rho = "
          f"{spearmanr(scored.dino_score, human_numeric).statistic:+.3f}")
    print(f"    dino vs heuristic score  : rho = "
          f"{spearmanr(data.dino_score, data.heuristic_score).statistic:+.3f}")

    print("\n  where the two methods disagree with each other:")
    split = data[data.dino_call != data.group.map({"high": "damaged", "low": "clean"})]
    for record in split.sort_values("heuristic_score").itertuples():
        print(f"    {record.experiment} run {record.run:>2} tooth {record.tooth_id:>2}  "
              f"heuristic {record.heuristic_score:6.3f} -> "
              f"{'damaged' if record.group == 'high' else 'clean':>7}   "
              f"dino {record.dino_score:.4f} -> {record.dino_call:>7}   "
              f"human {record.human}")

    out = "docs/thesis/ANOMALYDINO_VALIDATED.csv"
    data.to_csv(out, index=False)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
