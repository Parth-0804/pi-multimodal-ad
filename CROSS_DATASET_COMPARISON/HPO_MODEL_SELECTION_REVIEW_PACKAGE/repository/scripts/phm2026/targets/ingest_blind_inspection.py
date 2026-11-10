#!/usr/bin/env python3
"""Ingest a completed blind inspection and score it. PART B.

Accepts either form the result can come back in:

  FORM 1  a pasted BLIND_INSPECTION_RESULT_V1 block from the HTML sorter
  FORM 2  returned zip(s) of the sorted_* folders -- one combined zip, or one
          zip per folder. Filenames only are read; the images are not opened.

Everything is validated before anything is scored. A partial or renamed return
is refused loudly rather than scored approximately, because a silently dropped
token would bias the result in an invisible direction.

The statistics come from score_blind_inspection.py rather than being
reimplemented here. The one thing this script does differently is ORDER: the
within-experiment breakdown is printed before the overall figure, because a
high overall number with at-chance within-experiment accuracy means the sorter
was recognising the rig rather than the damage, and that reading has to be
available before the headline is seen.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
import io
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

SCORER = Path(__file__).resolve().parent / "score_blind_inspection.py"
_spec = importlib.util.spec_from_file_location("scorer", SCORER)
scorer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scorer)

FOLDER_CALL = {"sorted_damaged": "damaged", "sorted_clean": "clean",
               "sorted_unsure": "unsure"}
CALL_VALUE = {"clean": 0, "unsure": 1, "damaged": 2}


def from_zips(paths: list[Path]) -> tuple[dict[str, str], dict[str, float], list[str]]:
    """Membership from which folder each filename sits in. Images never opened."""
    calls: dict[str, list[str]] = defaultdict(list)
    problems: list[str] = []
    for path in paths:
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith("/") or name.endswith(".keep"):
                    continue
                parts = [p for p in name.split("/") if p and p != "."]
                if len(parts) < 2:
                    problems.append(f"{path.name}: entry not inside a sorted_* folder: {name}")
                    continue
                folder, filename = parts[-2], parts[-1]
                if folder not in FOLDER_CALL:
                    problems.append(f"{path.name}: unrecognised folder {folder!r} ({name})")
                    continue
                if not filename.lower().endswith(".jpg"):
                    problems.append(f"{path.name}: non-image file {name}")
                    continue
                calls[filename].append(FOLDER_CALL[folder])
    resolved = {token: values[0] for token, values in calls.items() if len(values) == 1}
    for token, values in calls.items():
        if len(values) > 1:
            problems.append(f"{token} appears in {len(values)} folders: {sorted(set(values))}")
    return resolved, {}, problems


def from_text(path: Path) -> tuple[dict[str, str], dict[str, float], list[str]]:
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    problems: list[str] = []
    if not lines or lines[0] != "BLIND_INSPECTION_RESULT_V1":
        problems.append("first line is not BLIND_INSPECTION_RESULT_V1")
    if lines and lines[-1] != "END":
        problems.append("last line is not END")
    calls, seconds = {}, {}
    for line in lines:
        if line in ("BLIND_INSPECTION_RESULT_V1", "END") or line.startswith("total_seconds="):
            continue
        parts = line.split(",")
        if len(parts) != 3:
            problems.append(f"malformed line: {line!r}")
            continue
        token, call, elapsed = parts[0].strip(), parts[1].strip().lower(), parts[2].strip()
        if call not in CALL_VALUE:
            problems.append(f"unknown call {call!r} for {token}")
            continue
        if token in calls:
            problems.append(f"{token} appears twice in the result block")
            continue
        calls[token] = call
        try:
            seconds[token] = float(elapsed)
        except ValueError:
            problems.append(f"unparseable time {elapsed!r} for {token}")
    return calls, seconds, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="scratch/blind_inspection")
    parser.add_argument("--zip", dest="zips", nargs="*", default=[],
                        help="returned zip(s) of the sorted_* folders (FORM 2)")
    parser.add_argument("--text", default=None,
                        help="returned BLIND_INSPECTION_RESULT_V1 file (FORM 1)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    key_path = root / "_KEY_DO_NOT_OPEN/key.csv"
    if not key_path.is_file():
        raise SystemExit(f"key not found at {key_path}")

    if args.text:
        calls, seconds, problems = from_text(Path(args.text))
        form = "FORM 1 (pasted result block)"
    elif args.zips:
        calls, seconds, problems = from_zips([Path(p) for p in args.zips])
        form = f"FORM 2 (returned zip{'s' if len(args.zips) > 1 else ''})"
    else:
        raise SystemExit("supply --zip or --text")

    with open(key_path) as handle:
        key = {row["token"]: row for row in csv.DictReader(handle)}

    # ---- validate before scoring ----
    print("=" * 68)
    print(f"VALIDATION — {form}")
    print("=" * 68)
    missing = sorted(set(key) - set(calls))
    unknown = sorted(set(calls) - set(key))
    if len(calls) != len(key):
        problems.append(f"expected {len(key)} tokens, found {len(calls)}")
    if missing:
        problems.append(f"{len(missing)} key token(s) never returned: {missing[:8]}"
                        + (" ..." if len(missing) > 8 else ""))
    if unknown:
        problems.append(f"{len(unknown)} returned name(s) not in the key "
                        f"(renamed or foreign?): {unknown[:8]}"
                        + (" ..." if len(unknown) > 8 else ""))
    counts = Counter(calls.values())
    print(f"  tokens in key          : {len(key)}")
    print(f"  tokens returned        : {len(calls)}")
    print(f"  damaged / clean / unsure: {counts.get('damaged',0)} / "
          f"{counts.get('clean',0)} / {counts.get('unsure',0)}")
    if problems:
        print("\n  REFUSING TO SCORE — validation failed:")
        for problem in problems:
            print(f"    - {problem}")
        print("\n  Nothing was scored and the key was not applied.")
        return 1
    print("  all checks passed: 42 tokens, all known, none duplicated\n")

    # ---- score, within-experiment FIRST ----
    scored = [t for t in calls if calls[t] != "unsure"]
    unsure = [t for t in calls if calls[t] == "unsure"]

    def correct(token: str) -> bool:
        expected = "damaged" if key[token]["group"] == "high" else "clean"
        return calls[token] == expected

    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit("=" * 68)
    emit("WITHIN EXPERIMENT — the confound check, read this first")
    emit("=" * 68)
    per_experiment = defaultdict(list)
    for token in scored:
        per_experiment[key[token]["experiment"]].append(token)
    within = {}
    for experiment in sorted(per_experiment):
        tokens = per_experiment[experiment]
        good = sum(correct(t) for t in tokens)
        within[experiment] = good / len(tokens)
        emit(f"  {experiment}: {good}/{len(tokens)} = {good/len(tokens):6.1%}   "
             f"p = {scorer.binomial_two_sided(good, len(tokens)):.4f}")

    hits = sum(correct(t) for t in scored)
    accuracy = hits / len(scored) if scored else float("nan")
    emit("")
    emit("=" * 68)
    emit("OVERALL")
    emit("=" * 68)
    emit(f"  accuracy (unsure excluded): {hits}/{len(scored)} = {accuracy:.1%}")
    emit(f"  two-sided binomial vs 50% : p = {scorer.binomial_two_sided(hits, len(scored)):.4f}")
    emit(f"  unsure, excluded          : {len(unsure)}")

    calls_numeric = [CALL_VALUE[calls[t]] for t in calls]
    scores = [float(key[t]["damage_score"]) for t in calls]
    rho = scorer.spearman(calls_numeric, scores)
    emit(f"  rank correlation (clean=0, unsure=1, damaged=2) vs score: rho = {rho:+.4f}")

    if seconds:
        values = sorted(seconds.values())
        median = values[len(values) // 2]
        emit(f"  time: total {sum(values):.0f}s, median {median:.1f}s per image")

    wrong = sorted((t for t in scored if not correct(t)),
                   key=lambda t: float(key[t]["damage_score"]))
    emit("")
    emit(f"MISCLASSIFIED ({len(wrong)})")
    for token in wrong:
        row = key[token]
        emit(f"  {token}  {row['experiment']} run {row['run']:>2} tooth {row['tooth_id']:>2}  "
             f"score {float(row['damage_score']):6.3f}  actually {row['group']:>4}  "
             f"called {calls[token]}")
    if unsure:
        emit("")
        emit(f"UNSURE ({len(unsure)})")
        for token in sorted(unsure, key=lambda t: float(key[t]["damage_score"])):
            row = key[token]
            emit(f"  {token}  {row['experiment']} run {row['run']:>2} tooth {row['tooth_id']:>2}  "
                 f"score {float(row['damage_score']):6.3f}  actually {row['group']}")

    emit("")
    emit("=" * 68)
    emit("VERDICT")
    emit("=" * 68)
    at_chance = [e for e, a in within.items() if a < 0.65]
    if accuracy >= 0.80 and not at_chance:
        emit("  The label TRACKS VISIBLE DAMAGE. Human judgement agrees with the")
        emit("  heuristic well above chance, within every experiment as well as")
        emit("  overall, so the confound check passes. The negative sensor results")
        emit("  are then cleanly about the sensors, not about a broken target.")
    elif accuracy >= 0.80 and at_chance:
        emit("  MIXED — the label partly encodes EXPERIMENT IDENTITY.")
        emit(f"  Overall accuracy is high but within-experiment accuracy is at or")
        emit(f"  near chance for: {', '.join(at_chance)}.")
        emit("  That means the sorting succeeded by recognising the rig -- lighting,")
        emit("  camera setup -- rather than by seeing damage. Treat the overall")
        emit("  number as misleading.")
    elif accuracy <= 0.62:
        emit("  The label DOES NOT TRACK VISIBLE DAMAGE. Human judgement is at or")
        emit("  near chance against the heuristic, so the pseudo-label is not")
        emit("  measuring what it claims. The work becomes a study of a broken")
        emit("  pseudo-label -- a legitimate and reportable finding.")
    else:
        emit("  INTERMEDIATE. Above chance but short of convincing. Read the")
        emit("  misclassified list: errors clustering near the score boundary mean")
        emit("  a noisy label; errors spread across the range mean a wrong one.")
    emit("")
    emit(f"  n = {len(scored)} scored, {len(unsure)} unsure. Treat p-values as indicative.")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = root / f"INSPECTION_RESULT_{stamp}.md"
    header = [f"# Blind inspection result — {stamp}", "",
              f"Source: {form}", f"Key: `{key_path}`", "",
              "```"]
    report.write_text("\n".join(header + lines + ["```", ""]), encoding="utf-8")
    print(f"\nwrote {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
