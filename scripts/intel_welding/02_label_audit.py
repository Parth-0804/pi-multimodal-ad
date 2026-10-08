#!/usr/bin/env python3
"""Phase 1 — label audit and process-confound (shortcut) audit.

Two questions, in order:

1. LABEL STRUCTURE. Is CATEGORY constant within a session? How many
   independent sessions support each category? Is a category tied to one
   material, thickness, weld type or process setting?

2. SHORTCUT. Can the label be predicted from the PROCESS RECIPE alone -- the
   legitimate manifest variables a plant would know before welding? If so, a
   multimodal model that appears to "detect defects" may only be recognising
   the recipe intended to produce them.

The shortcut classifier may see only: WELD_TYPE, THICKNESS_MM, STEEL_TYPE,
CURRENT_A, VOLTAGE_V, GAS_BAR, ROBOT_SPEED_CPM. Never CATEGORY, paths,
DIRECTORY, SUBDIRS, SPLIT or anything derived from them.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score, f1_score, balanced_accuracy_score, confusion_matrix
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.inspection import permutation_importance

ROOT = Path("data/Full Dataset")
OUT = Path("artifacts/intel_welding/audits")
CAT = ["WELD_TYPE", "STEEL_TYPE"]
NUM = ["THICKNESS_MM", "CURRENT_A", "VOLTAGE_V", "GAS_BAR", "ROBOT_SPEED_CPM"]
PROC = CAT + NUM
FORBIDDEN = {"CATEGORY", "DIRECTORY", "SUBDIRS", "SPLIT", "SAMPLES",
             "is_defect", "session"}


def build(model):
    return Pipeline([("prep", ColumnTransformer([
        ("c", OneHotEncoder(handle_unknown="ignore"), CAT),
        ("n", StandardScaler(), NUM)])), ("m", model)])


def cv_eval(X, y, groups, model_fn, binary: bool, seed=0, folds=5):
    """Session-disjoint CV. Every transform is fitted inside the fold."""
    n_classes = len(np.unique(y))
    folds = min(folds, int(pd.Series(y).value_counts().min()), len(np.unique(groups)))
    if folds < 2:
        return None
    skf = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=seed)
    oof = np.full(len(y), -1, dtype=int)
    proba = np.zeros((len(y), n_classes))
    for tr, te in skf.split(X, y, groups):
        m = build(model_fn())
        m.fit(X.iloc[tr], y[tr])
        oof[te] = m.predict(X.iloc[te])
        pr = m.predict_proba(X.iloc[te])
        for j, c in enumerate(m.classes_):
            proba[te, list(np.unique(y)).index(c)] = pr[:, j]
    res = {"macro_f1": float(f1_score(y, oof, average="macro")),
           "balanced_acc": float(balanced_accuracy_score(y, oof)),
           "accuracy": float((oof == y).mean())}
    if binary:
        res["auroc"] = float(roc_auc_score(y, proba[:, 1]))
    else:
        try:
            res["auroc_ovr"] = float(roc_auc_score(y, proba, multi_class="ovr",
                                                   average="macro"))
        except Exception:
            res["auroc_ovr"] = float("nan")
    return res, oof


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(OUT / "context_shortcut_audit.md"))
    ap.add_argument("--complete-only", action="store_true",
                    help="restrict to samples carrying all three deployable "
                         "modalities -- the actual modelling population")
    a = ap.parse_args(argv)

    m = pd.read_csv(ROOT / "manifest.csv")
    if a.complete_only:
        inv = pd.read_parquet(OUT / "dataset_inventory.parquet")
        keep = set(inv.loc[inv.complete_deployable, "SUBDIRS"])
        m = m[m.SUBDIRS.isin(keep)].reset_index(drop=True)
    m["session"] = m["DIRECTORY"]
    m["is_defect"] = (m.CATEGORY != "Good").astype(int)
    L: list[str] = []
    def w(s=""): print(s); L.append(s)

    w("# Label and process-confound audit")
    w()
    w(f"Manifest rows: {len(m)} · sessions (DIRECTORY): {m.session.nunique()} "
      f"· categories: {m.CATEGORY.nunique()}")
    w()
    w("## 1. Label structure")
    w()
    w("### Category counts and session support")
    w()
    w("| category | samples | sessions | binary |")
    w("|---|---|---|---|")
    for c, n in m.CATEGORY.value_counts().items():
        s = m[m.CATEGORY.eq(c)].session.nunique()
        w(f"| {c} | {n} | **{s}** | {'Good' if c=='Good' else 'Defect'} |")
    w()
    b = m.groupby("is_defect").agg(samples=("CATEGORY", "size"),
                                   sessions=("session", "nunique"))
    w(f"Binary: Good {b.loc[0,'samples']} samples / {b.loc[0,'sessions']} sessions; "
      f"Defect {b.loc[1,'samples']} samples / {b.loc[1,'sessions']} sessions.")
    w()
    g = m.groupby("session").CATEGORY.nunique()
    w(f"**Categories per session:** {int((g==1).sum())} of {len(g)} sessions "
      f"carry exactly one category; {int((g>1).sum())} carry more than one.")
    if (g > 1).sum() == 0:
        w()
        w("> CATEGORY is **constant within every session**. The label is a "
          "session-level property, so any sample-level split lets a model "
          "recover the label from session identity. Session-disjoint "
          "evaluation is mandatory, not merely preferable.")
    w()
    sz = m.groupby("session").size()
    w(f"Session size: min {sz.min()}, median {int(sz.median())}, max {sz.max()}.")
    w()
    w("### Supplied SPLIT")
    w()
    sp = m.groupby("session").SPLIT.nunique()
    w(f"Sessions whose samples all share one SPLIT: **{int((sp==1).sum())}** "
      f"of {len(sp)}. Sessions spanning multiple SPLIT values: "
      f"**{int((sp>1).sum())}**.")
    w()
    w("| SPLIT | samples |")
    w("|---|---|")
    for k, v in m.SPLIT.value_counts().items():
        w(f"| {k} | {v} |")
    w()
    if (sp > 1).sum() > 0:
        w("> The supplied SPLIT is **NOT session-disjoint**. Samples from the "
          "same session — and therefore the same label — appear in different "
          "splits. It cannot serve as the primary protocol, and it is not "
          "retained as a secondary comparability protocol either, because "
          "results obtained under it are not comparable to session-disjoint "
          "results. Recorded as a dataset finding.")
    w()
    w("### Category against process variables")
    w()
    for col in PROC:
        ct = pd.crosstab(m.CATEGORY, m[col])
        uniq = (ct > 0).sum(axis=1)
        tied = uniq[uniq == 1]
        w(f"**{col}** — {m[col].nunique()} distinct values; "
          f"{len(tied)} of {len(uniq)} categories occur at exactly one value"
          + (f" ({', '.join(tied.index[:6])}{'…' if len(tied)>6 else ''})" if len(tied) else ""))
    w()
    combo = m.groupby("CATEGORY")[PROC].apply(lambda d: d.drop_duplicates().shape[0])
    w("Distinct process-setting combinations per category "
      "(1 means the category has a single unique recipe):")
    w()
    w("| category | distinct recipes | sessions |")
    w("|---|---|---|")
    for c in combo.index:
        w(f"| {c} | {combo[c]} | {m[m.CATEGORY.eq(c)].session.nunique()} |")
    w()
    recipe = m[PROC].astype(str).agg("|".join, axis=1)
    rc = m.assign(r=recipe).groupby("r").CATEGORY.nunique()
    w(f"**Recipe → category:** {len(rc)} distinct recipes; "
      f"{int((rc==1).sum())} map to exactly one category "
      f"({(rc==1).mean():.0%}).")
    w()

    w("## 2. Context-only shortcut classifier")
    w()
    w("Inputs: " + ", ".join(PROC) + ". Excluded: " + ", ".join(sorted(FORBIDDEN)) + ".")
    assert not (set(PROC) & FORBIDDEN)
    models = {"A prior/majority": lambda: DummyClassifier(strategy="prior"),
              "B logistic regression": lambda: LogisticRegression(max_iter=2000),
              "C decision tree (depth 5)": lambda: DecisionTreeClassifier(
                  max_depth=5, random_state=a.seed),
              "D random forest": lambda: RandomForestClassifier(
                  n_estimators=300, random_state=a.seed, n_jobs=-1)}
    results = {}
    sess_per_cat = m.groupby("CATEGORY").session.nunique()
    weak = sorted(sess_per_cat[sess_per_cat < 3].index)
    mc = m[~m.CATEGORY.isin(weak)]
    tasks = [("binary Good vs Defect", m, m.is_defect.values, True),
             (f"multiclass diagnosis ({mc.CATEGORY.nunique()} of "
              f"{m.CATEGORY.nunique()} categories with >=3 sessions)",
              mc, pd.factorize(mc.CATEGORY)[0], False)]
    if weak:
        w()
        w(f"> Categories excluded from the multiclass CV for having fewer than "
          f"three independent sessions: **{', '.join(weak)}**. They are NOT "
          f"merged into other classes; they are reported as unsupported.")
    for task, mm, y, binary in tasks:
        X = mm[PROC]; groups = mm.session.values
        w()
        w(f"### {task} — session-disjoint 5-fold CV")
        w()
        head = "| model | " + ("AUROC | " if binary else "AUROC(ovr) | ") + \
               "macro-F1 | balanced acc | accuracy |"
        w(head); w("|---|---|---|---|---|")
        for name, fn in models.items():
            out = cv_eval(X, y, groups, fn, binary, a.seed)
            if out is None:
                w(f"| {name} | insufficient folds | | | |"); continue
            r, oof = out
            key = "auroc" if binary else "auroc_ovr"
            results[f"{task}|{name}"] = r
            w(f"| {name} | {r.get(key, float('nan')):.3f} | {r['macro_f1']:.3f} "
              f"| {r['balanced_acc']:.3f} | {r['accuracy']:.3f} |")
        w()

    # permutation importance for the strongest model, fitted session-disjoint
    w("### Permutation importance (random forest, binary, held-out fold)")
    w()
    Xb, gb, yb = m[PROC], m.session.values, m.is_defect.values
    skf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=a.seed)
    tr, te = next(iter(skf.split(Xb, yb, gb)))
    pipe = build(RandomForestClassifier(n_estimators=300, random_state=a.seed, n_jobs=-1))
    pipe.fit(Xb.iloc[tr], yb[tr])
    pi = permutation_importance(pipe, Xb.iloc[te], yb[te],
                                n_repeats=10, random_state=a.seed, scoring="roc_auc")
    w("| variable | mean AUROC drop when permuted | sd |")
    w("|---|---|---|")
    for i in np.argsort(pi.importances_mean)[::-1]:
        w(f"| {PROC[i]} | {pi.importances_mean[i]:+.4f} | {pi.importances_std[i]:.4f} |")
    w()

    # session-identity probe
    w("### Session-identity probe")
    w()
    w("How strongly do process settings identify the session? A high value "
      "means the recipe is close to a session fingerprint.")
    w()
    sess_y = pd.factorize(m.session)[0]
    rf = build(RandomForestClassifier(n_estimators=200, random_state=a.seed, n_jobs=-1))
    # train/test on random sample split here ON PURPOSE: the question is
    # in-principle identifiability of the session, not generalisation
    from sklearn.model_selection import train_test_split
    counts = pd.Series(sess_y).value_counts()
    ok = np.isin(sess_y, counts[counts >= 2].index)
    idx = np.flatnonzero(ok)
    itr, ite = train_test_split(idx, test_size=0.3, random_state=a.seed,
                                stratify=sess_y[idx])
    Xp = m[PROC]
    rf.fit(Xp.iloc[itr], sess_y[itr])
    acc = float((rf.predict(Xp.iloc[ite]) == sess_y[ite]).mean())
    n_s = int(len(np.unique(sess_y[idx])))
    w(f"Session-ID accuracy from process settings alone: **{acc:.3f}** "
      f"over {n_s} sessions with >=2 samples (chance = 1/{n_s} = {1/n_s:.4f}).")
    w()
    results["session_probe_accuracy"] = acc

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(L) + "\n")
    (OUT / "context_shortcut_metrics.json").write_text(json.dumps(results, indent=2))
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
