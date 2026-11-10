#!/usr/bin/env python3
"""Phase 2 — the immutable session-disjoint split, plus leakage tests.

The final-test sessions are chosen ONCE, deterministically, from the session
list alone. No model is involved and no seed is searched on performance: the
seed is fixed at 20260927 and the selection rule is a single stratified pass.

Population: samples carrying all three deployable modalities (audio + video +
sensor). The Phase 1 inventory shows modality availability is systematic by
class, so that restriction is a documented finding, not a convenience.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

AUD = Path("artifacts/intel_welding/audits")
SPL = Path("artifacts/intel_welding/splits")
SEED = 20260927


def h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--test-frac", type=float, default=0.20)
    ap.add_argument("--folds", type=int, default=5)
    a = ap.parse_args(argv)

    inv = pd.read_parquet(AUD / "dataset_inventory.parquet")
    d = inv[inv.complete_deployable].copy()
    d["is_defect"] = (d.CATEGORY != "Good").astype(int)
    d["session"] = d["DIRECTORY"]

    # session-level table; label is constant within session (Phase 1 finding)
    sess = (d.groupby("session")
              .agg(n=("SUBDIRS", "size"), category=("CATEGORY", "first"),
                   is_defect=("is_defect", "first")).reset_index())
    assert d.groupby("session").CATEGORY.nunique().max() == 1, \
        "category not constant within session"

    # deterministic stratified selection of ~20% of sessions, stratified by
    # CATEGORY so every category keeps representation where it can
    rng = np.random.default_rng(SEED)
    test = []
    for cat, grp in sess.groupby("category"):
        ids = np.sort(grp.session.values)
        k = int(round(len(ids) * a.test_frac))
        if len(ids) >= 3:
            k = max(1, k)          # keep at least one test session if possible
        else:
            k = 0                  # too few sessions: keep all in development
        if k:
            test.extend(rng.permutation(ids)[:k].tolist())
    test = sorted(test)
    dev = sorted(set(sess.session) - set(test))

    SPL.mkdir(parents=True, exist_ok=True)
    (SPL / "final_test_sessions.txt").write_text("\n".join(test) + "\n")
    (SPL / "development_sessions.txt").write_text("\n".join(dev) + "\n")

    dev_rows = d[d.session.isin(dev)]
    test_rows = d[d.session.isin(test)]

    # development CV folds, fixed now so they cannot drift later
    folds = []
    skf = StratifiedGroupKFold(n_splits=a.folds, shuffle=True, random_state=SEED)
    for i, (tr, va) in enumerate(skf.split(dev_rows, dev_rows.is_defect,
                                           dev_rows.session)):
        folds.append({"fold": i,
                      "train_sessions": sorted(set(dev_rows.iloc[tr].session)),
                      "val_sessions": sorted(set(dev_rows.iloc[va].session))})

    manifest = {
        "seed": SEED,
        "rule": "per-category deterministic permutation, ~20% of sessions, "
                "categories with <3 sessions kept entirely in development",
        "manifest_sha256": json.loads((AUD / "dataset_summary.json").read_text())["manifest_sha256"],
        "population": "complete_deployable (audio+video+sensor present)",
        "n_samples": int(len(d)), "n_sessions": int(len(sess)),
        "n_dev_sessions": len(dev), "n_test_sessions": len(test),
        "n_dev_samples": int(len(dev_rows)), "n_test_samples": int(len(test_rows)),
        "final_test_sessions": test,
        "development_sessions": dev,
        "cv_folds": folds,
        "split_sha256": h("|".join(test) + "##" + "|".join(dev)),
    }
    (SPL / "split_manifest.json").write_text(json.dumps(manifest, indent=2))

    print("=" * 72); print("SPLIT"); print("=" * 72)
    print(f"  population      : {len(d)} samples / {len(sess)} sessions")
    print(f"  development     : {len(dev_rows)} samples / {len(dev)} sessions")
    print(f"  FINAL TEST      : {len(test_rows)} samples / {len(test)} sessions")
    print(f"  split_sha256    : {manifest['split_sha256'][:32]}…")
    print("\n  per-category session allocation:")
    print(f"    {'category':34s} {'dev':>5s} {'test':>5s}")
    for cat, grp in sess.groupby("category"):
        nt = sum(s in test for s in grp.session)
        print(f"    {cat:34s} {len(grp)-nt:5d} {nt:5d}")
    print(f"\n  binary balance  dev: Good {int((dev_rows.is_defect==0).sum())} / "
          f"Defect {int((dev_rows.is_defect==1).sum())}")
    print(f"                  test: Good {int((test_rows.is_defect==0).sum())} / "
          f"Defect {int((test_rows.is_defect==1).sum())}")

    # ---------------- GATE 3 leakage tests ----------------
    print("\n" + "=" * 72); print("GATE 3 — LEAKAGE TESTS"); print("=" * 72)
    checks = []
    def chk(name, ok, detail="", kind="test"):
        checks.append({"check": name, "pass": bool(ok), "detail": detail,
                       "kind": kind})
        tag = {"test": "PASS" if ok else "FAIL", "note": "NOTE"}[kind]
        print(f"  [{tag}] {name}" + (f" — {detail}" if detail else ""))

    chk("dev ∩ test sessions empty", not (set(dev) & set(test)))
    for f in folds:
        if set(f["train_sessions"]) & set(f["val_sessions"]):
            chk(f"fold {f['fold']} train ∩ val empty", False); break
    else:
        chk("every CV fold train ∩ val empty", True, f"{len(folds)} folds")
    chk("no test session in any CV fold", not any(
        set(f["train_sessions"] + f["val_sessions"]) & set(test) for f in folds))

    for col, label in (("audio_sha1", "audio"), ("video_sha1", "video"),
                       ("csv_sha1", "sensor")):
        if col not in d.columns:
            continue
        dd = d[d[col].notna()]
        cross = (dd.groupby(col).session.nunique() > 1).sum()
        both = dd.assign(part=np.where(dd.session.isin(test), "test", "dev"))
        crosspart = (both.groupby(col).part.nunique() > 1).sum()
        chk(f"no duplicate {label} content across dev/test", crosspart == 0,
            f"{crosspart} hashes span partitions; {cross} span sessions")

    sub = d.SUBDIRS.astype(str)
    chk("sample IDs unique", sub.nunique() == len(sub))
    # can path/filename trivially reveal category?
    cat_in_path = d.apply(
        lambda r: r.CATEGORY.split("_")[0].lower() in str(r.DIRECTORY).lower(), axis=1).mean()
    chk("directory name encodes category", True,
        f"{cat_in_path:.0%} of rows carry the category word in DIRECTORY. This "
        f"is how the label is defined, not a partition leak; it is recorded as "
        f"a HARD CONSTRAINT that no path component may ever be used as a "
        f"feature", kind="note")

    (SPL / "leakage_tests.json").write_text(json.dumps(checks, indent=2))
    allpass = all(c["pass"] for c in checks)
    print(f"\n  ALL LEAKAGE TESTS {'PASS' if allpass else 'FAIL'}")
    print(f"  wrote {SPL}/split_manifest.json, leakage_tests.json")
    return 0 if allpass else 1


if __name__ == "__main__":
    raise SystemExit(main())
