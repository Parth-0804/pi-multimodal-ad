#!/usr/bin/env python3
"""Robustness sweep for the AnomalyDINO change-detection result.

A single configuration scoring below the heuristic proves little -- it could be
one bad choice of aggregation, reference bank or backbone. This sweeps all
three and reports agreement for every combination, so the conclusion rests on
the shape of the whole table rather than on one cell.

  bank         per-tooth   the same tooth at baseline (2 references, strict
                           change detection)
               per-exp     every baseline image in that experiment (~50-130
                           references, richer nominal model, but no longer
                           tooth-specific)
  aggregation  top1/5/10%  mean of the worst q% of patch distances
               mean/max    whole-image mean, single worst patch
  backbone     dinov2-small (384d) and dinov2-base (768d)

Calls are formed exactly as the heuristic's were: within each experiment the 14
validated images are ranked and split top-7 damaged / bottom-7 clean. Agreement
is against the 38 non-unsure human calls. The heuristic's 78.9% is the
reference line.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import torch

_spec = importlib.util.spec_from_file_location(
    "base", Path(__file__).resolve().parent / "anomalydino_validated.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

AGGREGATIONS = ("top1%", "top5%", "top10%", "mean", "max")
HEURISTIC = 30 / 38


def aggregate(distance: torch.Tensor, how: str) -> float:
    if how == "mean":
        return float(distance.mean())
    if how == "max":
        return float(distance.max())
    fraction = {"top1%": 0.01, "top5%": 0.05, "top10%": 0.10}[how]
    k = max(1, int(len(distance) * fraction))
    return float(torch.topk(distance, k).values.mean())


def nearest(query: torch.Tensor, bank: torch.Tensor) -> torch.Tensor:
    best = torch.full((len(query),), -1.0)
    for start in range(0, len(bank), 20000):
        best = torch.maximum(best, (query @ bank[start:start + 20000].T).max(dim=1).values)
    return 1.0 - best


def agreement(data: pd.DataFrame, column: str) -> tuple[int, int, dict[str, str]]:
    call = {}
    for experiment, scoped in data.groupby("experiment"):
        ranked = scoped.sort_values(column)
        for token in ranked.token[:7]:
            call[token] = "clean"
        for token in ranked.token[7:]:
            call[token] = "damaged"
    scored = data[data.human.ne("unsure")]
    hits = sum(call[t] == h for t, h in zip(scored.token, scored.human))
    return hits, len(scored), call


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", default="scratch/blind_inspection/_KEY_DO_NOT_OPEN/key.csv")
    parser.add_argument("--result", default="scratch/blind_inspection/"
                        "INSPECTION_RESULT_20260913T204715Z.md")
    parser.add_argument("--models", nargs="*",
                        default=["facebook/dinov2-small", "facebook/dinov2-base"])
    parser.add_argument("--max-refs", type=int, default=80,
                        help="cap on per-experiment bank size, for tractability")
    args = parser.parse_args(argv)

    from transformers import AutoModel
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

    key = {r["token"]: r for r in csv.DictReader(open(args.key))}
    calls = base.reconstruct_calls(Path(args.result), key)

    manifest = pd.read_parquet(f"{base.V3}/tables/image_manifest.parquet")
    teeth = pd.read_parquet(f"{base.V3}/tables/per_tooth_damage.parquet")
    teeth["run"] = teeth["run"].astype(int)
    teeth["tooth_id"] = teeth["tooth_id"].astype(int)
    lookup = manifest.set_index("image_id")[["archive_path", "archive_member"]]
    baseline = manifest[manifest.inspection_stage.isin(base.BASELINE_STAGES)].copy()
    baseline["tooth_id"] = baseline["tooth_id"].astype(int)

    # ---- resolve every image path once, then load pixels once ----
    handles: dict = {}
    queries, meta = {}, []
    for token, record in key.items():
        experiment, tooth = record["experiment"], int(record["tooth_id"])
        selected = teeth[teeth.experiment.eq(experiment)
                         & teeth.run.eq(int(record["run"]))
                         & teeth.tooth_id.eq(tooth)].iloc[0]
        source = lookup.loc[selected.selected_image_id]
        queries[token] = base.load_roi(source.archive_path, source.archive_member, handles)
        meta.append({"token": token, "experiment": experiment, "run": int(record["run"]),
                     "tooth_id": tooth, "group": record["group"],
                     "heuristic_score": float(record["damage_score"]),
                     "human": calls[token]})
    data = pd.DataFrame(meta)

    tooth_refs: dict[tuple[str, int], list] = {}
    for record in data.itertuples():
        bank_key = (record.experiment, record.tooth_id)
        if bank_key in tooth_refs:
            continue
        refs = baseline[baseline.experiment.eq(record.experiment)
                        & baseline.tooth_id.eq(record.tooth_id)]
        tooth_refs[bank_key] = [base.load_roi(r.archive_path, r.archive_member, handles)
                                for r in refs.itertuples()]

    rng = np.random.default_rng(20260913)
    exp_refs: dict[str, list] = {}
    for experiment in sorted(data.experiment.unique()):
        refs = baseline[baseline.experiment.eq(experiment)]
        if len(refs) > args.max_refs:
            refs = refs.iloc[rng.choice(len(refs), args.max_refs, replace=False)]
        exp_refs[experiment] = [base.load_roi(r.archive_path, r.archive_member, handles)
                                for r in refs.itertuples()]
    for handle in handles.values():
        handle.close()
    print(f"loaded {len(queries)} queries, "
          f"{sum(len(v) for v in tooth_refs.values())} per-tooth refs, "
          f"{sum(len(v) for v in exp_refs.values())} per-experiment refs\n")

    table = []
    for model_name in args.models:
        model = AutoModel.from_pretrained(model_name).eval()

        def encode(images: list) -> torch.Tensor:
            out = []
            for start in range(0, len(images), 8):
                out.append(base.features(model, images[start:start + 8], mean, std))
            return torch.cat(out)

        query_features = {t: encode([i])[0] for t, i in queries.items()}
        tooth_banks = {k: encode(v).reshape(-1, encode(v[:1]).shape[-1])
                       for k, v in tooth_refs.items()}
        exp_banks = {k: encode(v).reshape(-1, list(tooth_banks.values())[0].shape[-1])
                     for k, v in exp_refs.items()}

        for bank_name, banks, selector in (
                ("per-tooth", tooth_banks, lambda r: (r.experiment, r.tooth_id)),
                ("per-exp", exp_banks, lambda r: r.experiment)):
            distances = {r.token: nearest(query_features[r.token], banks[selector(r)])
                         for r in data.itertuples()}
            for how in AGGREGATIONS:
                column = f"{model_name.split('-')[-1]}|{bank_name}|{how}"
                data[column] = [aggregate(distances[t], how) for t in data.token]
                hits, n, _ = agreement(data, column)
                table.append({"model": model_name.split("-")[-1], "bank": bank_name,
                              "aggregation": how, "hits": hits, "n": n,
                              "agreement": hits / n})
                print(f"  {column:34s} {hits:2d}/{n} = {hits/n:6.1%}")
        del model

    print("\n" + "=" * 72)
    print("SWEEP SUMMARY — agreement with human judgement (n = 38)")
    print("=" * 72)
    summary = pd.DataFrame(table).sort_values("agreement", ascending=False)
    for record in summary.itertuples():
        flag = "  >= heuristic" if record.agreement >= HEURISTIC else ""
        print(f"  {record.model:6s} {record.bank:10s} {record.aggregation:7s} "
              f"{record.hits:2d}/{record.n} = {record.agreement:6.1%}{flag}")
    print(f"\n  CV heuristic reference : 30/38 = {HEURISTIC:.1%}")
    print(f"  best configuration     : {summary.iloc[0].agreement:.1%}")
    print(f"  worst configuration    : {summary.iloc[-1].agreement:.1%}")
    print(f"  median configuration   : {summary.agreement.median():.1%}")
    print(f"  configurations at or above the heuristic: "
          f"{int((summary.agreement >= HEURISTIC).sum())} of {len(summary)}")

    out = "docs/thesis/ANOMALYDINO_SWEEP.csv"
    summary.to_csv(out, index=False)
    data.to_csv("docs/thesis/ANOMALYDINO_SCORES.csv", index=False)
    print(f"\nwrote {out} and docs/thesis/ANOMALYDINO_SCORES.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
