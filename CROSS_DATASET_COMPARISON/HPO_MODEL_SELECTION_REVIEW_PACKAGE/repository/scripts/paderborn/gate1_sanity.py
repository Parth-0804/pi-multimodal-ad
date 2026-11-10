#!/usr/bin/env python3
"""GATE 1 (ARCH-VAL-PB) -- does the data port reproduce a known result?

3-class fault classification (healthy / inner race / outer race) from
VIBRATION ALONE, within a SINGLE operating condition, conventional split.

Two protocols are reported, deliberately:

  A. CONVENTIONAL  stratified random split over windows. This is the protocol
     the high published accuracies are obtained under, so it is the one that
     answers "is the port broken?". Windows from the same recording and the
     same bearing fall on both sides, so it is optimistic by construction.

  B. BEARING-DISJOINT  no bearing appears in both train and test. Honest, and
     reported so the leakage in protocol A is visible rather than implied.

Gate 1 is judged on A, because that is what the published figure measures.
"""
from __future__ import annotations
import argparse
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.metrics import accuracy_score, confusion_matrix

VIB = [f"vib_{s}" for s in ("mean","std","rms","skew","kurt","p2p","crest","shape")]

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--features", default="data/paderborn/features.parquet")
    p.add_argument("--condition", default="N15_M07_F10")
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)

    df = pd.read_parquet(a.features)
    d = df[df.condition.eq(a.condition)].copy()
    if d.empty:
        raise SystemExit(f"no rows for condition {a.condition}")
    X, y, g = d[VIB].to_numpy(), d.fault.to_numpy(), d.bearing.to_numpy()

    print("="*70); print(f"GATE 1 -- vibration-only 3-class, condition {a.condition}")
    print("="*70)
    print(f"  windows {len(d)}   bearings {d.bearing.nunique()}   features {len(VIB)}")
    print("  class counts:", dict(pd.Series(y).value_counts()))
    print(f"  bearings per class:",
          {k: v.bearing.nunique() for k, v in d.groupby('fault')})

    def run(splitter, groups, label):
        accs, cms = [], []
        for tr, te in splitter.split(X, y, groups):
            m = RandomForestClassifier(n_estimators=300, random_state=a.seed, n_jobs=-1)
            m.fit(X[tr], y[tr])
            pred = m.predict(X[te])
            accs.append(accuracy_score(y[te], pred))
            cms.append(confusion_matrix(y[te], pred, labels=["healthy","inner","outer"]))
        accs = np.array(accs)
        print(f"\n  {label}")
        print(f"    accuracy per fold: {np.round(accs,4)}")
        print(f"    mean {accs.mean():.4f}  sd {accs.std():.4f}")
        cm = sum(cms)
        print("    confusion (rows true healthy/inner/outer):")
        for name, row in zip(["healthy","inner","outer"], cm):
            print(f"      {name:8s} {row}  (recall {row[list(['healthy','inner','outer']).index(name)]/row.sum():.3f})")
        return accs.mean()

    acc_a = run(StratifiedKFold(5, shuffle=True, random_state=a.seed), None,
                "A. CONVENTIONAL stratified random split (5-fold)")
    acc_b = run(GroupKFold(n_splits=min(5, len(np.unique(g)))), g,
                "B. BEARING-DISJOINT split (GroupKFold by bearing)")

    print("\n" + "="*70); print("GATE 1 VERDICT"); print("="*70)
    print(f"  conventional-protocol accuracy : {acc_a:.1%}")
    print(f"  bearing-disjoint accuracy      : {acc_b:.1%}")
    print(f"  leakage gap                    : {acc_a-acc_b:+.1%}")
    print("\n  Published comparison: work on this dataset reports ~95-99% for")
    print("  within-condition 3-class vibration classification under the")
    print("  conventional split (Lessmeier et al. 2016 and subsequent).")
    print(f"  -> port {'REPRODUCES' if acc_a >= 0.90 else 'DOES NOT REPRODUCE'} "
          f"broadly comparable performance.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
