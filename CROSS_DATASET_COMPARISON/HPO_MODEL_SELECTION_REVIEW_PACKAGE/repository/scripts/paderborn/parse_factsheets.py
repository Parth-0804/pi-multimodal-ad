#!/usr/bin/env python3
"""Parse the official per-bearing fact-sheet PDFs shipped inside each archive.

The damage-severity target for Gate 2 must come from the fact sheets rather
than from a table typed out of the paper, so this reads them directly and
emits a machine-checkable CSV. It also cross-checks the hardcoded SEVERITY /
FAULT tables in extract_features.py and reports any disagreement.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
import pandas as pd
from pypdf import PdfReader

def field(text: str, label: str) -> str:
    m = re.search(re.escape(label) + r"[ \t]*([^\n]*)", text)
    return " ".join(m.group(1).split()) if m else ""

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw", default=str(Path.home()/"Datasets/Paderborn/raw"))
    p.add_argument("--out", default="data/paderborn/factsheets.csv")
    a = p.parse_args(argv)

    rows = []
    for pdf in sorted(Path(a.raw).glob("K*/K*.pdf")):
        if pdf.name.startswith("measuring_log"):
            continue
        code = pdf.stem
        try:
            text = "\n".join(pg.extract_text() for pg in PdfReader(pdf).pages)
        except Exception as exc:
            print(f"  {code}: unreadable ({exc})", file=sys.stderr); continue
        rows.append({
            "bearing": code,
            "n_damages": field(text, "Number of damages"),
            "mode": field(text, "Mode"),
            "component": field(text, "Component"),
            "extent": field(text, "Extent of damage"),
            "combination": field(text, "Damage combination"),
            "arrangement": field(text, "Arrangement of the"),
            "char": field(text, "Characteristic of"),
            "method": field(text, "Damage method"),
            "lifetime_h": field(text, "Lifetime h"),
        })
    df = pd.DataFrame(rows)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False)
    print(f"parsed {len(df)} fact sheets -> {a.out}\n")
    with pd.option_context("display.width", 200, "display.max_columns", None):
        print(df[["bearing","n_damages","mode","component","extent",
                  "combination","method"]].to_string(index=False))

    # cross-check against the hardcoded tables
    sys.path.insert(0, str(Path(__file__).parent))
    from extract_features import SEVERITY, FAULT
    print("\n" + "="*64); print("CROSS-CHECK vs hardcoded tables"); print("="*64)
    bad = 0
    for r in df.itertuples():
        if r.bearing not in SEVERITY:
            print(f"  {r.bearing}: in fact sheets, NOT in scope table "
                  f"(component={r.component!r} n_damages={r.n_damages!r})")
            continue
        want_sev = SEVERITY[r.bearing]
        got = re.findall(r"\d+", r.extent)
        sev = int(got[0]) if got else 0
        if FAULT[r.bearing] == "healthy":
            sev = 0
        if sev != want_sev:
            print(f"  MISMATCH {r.bearing}: factsheet extent={r.extent!r} -> {sev}, "
                  f"table says {want_sev}"); bad += 1
        comp = r.component.split()[0] if r.component else ""
        want_comp = {"inner":"IR","outer":"OR","healthy":""}[FAULT[r.bearing]]
        if want_comp and comp and comp != want_comp:
            print(f"  MISMATCH {r.bearing}: factsheet component={comp}, "
                  f"table says {want_comp}"); bad += 1
    print(f"\n  {'ALL AGREE' if bad==0 else str(bad)+' DISAGREEMENTS'} "
          f"over {len(df)} fact sheets")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
