#!/usr/bin/env python3
"""Score a completed blind tooth inspection. Run only after sorting is done.

Copied into _KEY_DO_NOT_OPEN/ as score_inspection.py by the preparation script,
and expects to sit inside that directory with key.csv beside it.

The within-experiment breakdown is the important part. Overall accuracy can
look good while the researcher was really sorting by experiment appearance --
lighting, camera setup -- rather than by damage. If overall accuracy is high
but within-experiment accuracy sits at chance, that is what happened, and the
label is partly encoding experiment identity.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

CLEAN, UNSURE, DAMAGED = "clean", "unsure", "damaged"
CALL_VALUE = {CLEAN: 0, UNSURE: 1, DAMAGED: 2}


def binomial_two_sided(successes: int, trials: int, probability: float = 0.5) -> float:
    """Exact two-sided binomial test; no SciPy dependency."""
    if trials == 0:
        return float("nan")

    def pmf(k: int) -> float:
        return math.comb(trials, k) * probability ** k * (1 - probability) ** (trials - k)

    observed = pmf(successes)
    return min(1.0, sum(pmf(k) for k in range(trials + 1) if pmf(k) <= observed + 1e-12))


def spearman(x: list[float], y: list[float]) -> float:
    def rank(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        index = 0
        while index < len(order):
            stop = index
            while stop + 1 < len(order) and values[order[stop + 1]] == values[order[index]]:
                stop += 1
            average = (index + stop) / 2 + 1
            for position in range(index, stop + 1):
                ranks[order[position]] = average
            index = stop + 1
        return ranks

    if len(x) < 3:
        return float("nan")
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    numerator = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denominator = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return numerator / denominator if denominator else float("nan")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None,
                        help="inspection workspace root (default: parent of this file)")
    args = parser.parse_args(argv)

    here = Path(__file__).resolve().parent
    root = Path(args.root) if args.root else here.parent
    key_path = here / "key.csv" if (here / "key.csv").exists() else root / "_KEY_DO_NOT_OPEN/key.csv"

    remaining = sorted((root / "to_sort").glob("*.jpg"))
    if remaining:
        print(f"REFUSING TO SCORE: {len(remaining)} image(s) still in to_sort/.")
        print("Finish sorting every image into sorted_damaged/, sorted_clean/ or")
        print("sorted_unsure/ first. Nothing has been revealed.")
        return 1

    with open(key_path) as handle:
        key = {row["token"]: row for row in csv.DictReader(handle)}

    placement = {}
    for call, folder in ((DAMAGED, "sorted_damaged"), (CLEAN, "sorted_clean"),
                         (UNSURE, "sorted_unsure")):
        for path in (root / folder).glob("*.jpg"):
            placement[path.name] = call

    unplaced = [t for t in key if t not in placement]
    if unplaced:
        print(f"WARNING: {len(unplaced)} image(s) from the key were not found in any "
              f"sorted folder; excluded from scoring.")

    def correct(token: str) -> bool:
        expected = DAMAGED if key[token]["group"] == "high" else CLEAN
        return placement[token] == expected

    scored = [t for t in key if t in placement and placement[t] != UNSURE]
    unsure = [t for t in key if placement.get(t) == UNSURE]
    hits = sum(correct(t) for t in scored)

    print("=" * 66)
    print("BLIND INSPECTION RESULT")
    print("=" * 66)
    print(f"  images in key            : {len(key)}")
    print(f"  sorted, excluding unsure : {len(scored)}")
    print(f"  marked unsure (excluded) : {len(unsure)}")
    if scored:
        accuracy = hits / len(scored)
        print(f"\n  OVERALL accuracy : {hits}/{len(scored)} = {accuracy:.1%}")
        print(f"  two-sided binomial vs 50%: p = {binomial_two_sided(hits, len(scored)):.4f}")
    else:
        accuracy = float("nan")
        print("\n  nothing to score outside the unsure pile.")

    print("\n  WITHIN EXPERIMENT (the confound check)")
    per_experiment = defaultdict(list)
    for token in scored:
        per_experiment[key[token]["experiment"]].append(token)
    within = {}
    for experiment in sorted(per_experiment):
        tokens = per_experiment[experiment]
        good = sum(correct(t) for t in tokens)
        within[experiment] = good / len(tokens)
        print(f"    {experiment}: {good}/{len(tokens)} = {good/len(tokens):.1%}   "
              f"p = {binomial_two_sided(good, len(tokens)):.4f}")

    calls = [CALL_VALUE[placement[t]] for t in key if t in placement]
    scores = [float(key[t]["damage_score"]) for t in key if t in placement]
    rho = spearman(calls, scores)
    print(f"\n  rank correlation, three-way call vs damage score: rho = {rho:+.4f}")

    wrong = sorted((t for t in scored if not correct(t)),
                   key=lambda t: float(key[t]["damage_score"]))
    print(f"\n  MISCLASSIFIED ({len(wrong)}) — the most informative output here")
    for token in wrong:
        row = key[token]
        print(f"    {token}  {row['experiment']} run {row['run']} tooth {row['tooth_id']}  "
              f"score {float(row['damage_score']):.3f}  group {row['group']} -> "
              f"called {placement[token]}")
    if unsure:
        print(f"\n  UNSURE ({len(unsure)})")
        for token in sorted(unsure, key=lambda t: float(key[t]["damage_score"])):
            row = key[token]
            print(f"    {token}  {row['experiment']} run {row['run']} tooth {row['tooth_id']}  "
                  f"score {float(row['damage_score']):.3f}  group {row['group']}")

    print("\n" + "=" * 66)
    print("VERDICT")
    print("=" * 66)
    chance_within = [e for e, a in within.items() if a < 0.65]
    if scored and accuracy >= 0.80 and not chance_within:
        print("  The label tracks visible damage. Human judgement agrees with the")
        print("  heuristic well above chance, within every experiment as well as")
        print("  overall, so the confound check passes. Negative sensor results are")
        print("  then cleanly about the sensors, not about a broken target.")
    elif scored and accuracy >= 0.80 and chance_within:
        print("  MIXED: overall accuracy is high but within-experiment accuracy is at")
        print(f"  or near chance for {', '.join(chance_within)}.")
        print("  That pattern means the sorting was driven by experiment appearance --")
        print("  lighting, camera setup -- rather than by damage, and the label partly")
        print("  encodes experiment identity. Treat the overall number as misleading.")
    elif scored and accuracy <= 0.62:
        print("  The label does NOT track visible damage. Human judgement is at or")
        print("  near chance against the heuristic, so the pseudo-label is not")
        print("  measuring what it claims. The thesis becomes a study of a broken")
        print("  pseudo-label -- which is a legitimate and reportable finding.")
    else:
        print("  Intermediate. Accuracy is above chance but short of convincing.")
        print("  Read the misclassified list above: if the errors cluster near the")
        print("  score boundary the label is noisy rather than wrong.")
    print("\n  Sample size is small; treat the p-values as indicative.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
