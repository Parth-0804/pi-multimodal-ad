"""Frozen grouping, complete OOF coverage, and explicit cohort readiness gates."""
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold


def both_classes(frame, indices):
    return set(frame.iloc[indices].target) == {0, 1}


def verify_plan(frame, population, plan, require_validation_classes=True):
    population = set(map(int, population))
    groups = frame.group_id.to_numpy()
    covered = set()
    for train, valid in plan:
        train, valid = np.asarray(train, int), np.asarray(valid, int)
        a, b = set(train), set(valid)
        if not a or not b or a & b or a | b != population or set(groups[train]) & set(groups[valid]) or covered & b:
            raise ValueError("Non-disjoint/incomplete group split")
        if not both_classes(frame, train) or (require_validation_classes and not both_classes(frame, valid)):
            raise ValueError("Both classes required in every fit/validation partition")
        covered |= b
    if covered != population:
        raise ValueError("Every training prediction unit must occur exactly once out of fold")


def grouped_plan(frame, rows=None, folds=3, seed=42):
    rows = np.arange(len(frame)) if rows is None else np.asarray(rows, int)
    f = frame.iloc[rows]
    if f.loc[f.target == 1, "group_id"].nunique() < folds or f.loc[f.target == 0, "group_id"].nunique() < folds:
        raise ValueError("Insufficient positive/negative experiment groups for requested folds")
    split = StratifiedGroupKFold(folds, shuffle=True, random_state=seed)
    plan = [(rows[a], rows[b]) for a, b in split.split(np.zeros(len(f)), f.target, f.group_id)]
    verify_plan(frame, rows, plan)
    return plan


def nested_plan(frame, outer=3, inner=2, seed=42):
    """No seed search or automatic weakening of the declared split design."""
    plan = grouped_plan(frame, folds=outer, seed=seed)
    return [{"train": a.tolist(), "test": b.tolist(),
             "inner": [(it.tolist(), iv.tolist()) for it, iv in grouped_plan(frame, a, inner, seed + 100 + k)]}
            for k, (a, b) in enumerate(plan)]


def smoke_partition(frame):
    """Development-only OOF exercise; protected normal group never predicted."""
    held = set(frame.index[frame.group_id == "imi_vm20i/dataset19"])
    rows = np.array(sorted(set(frame.index) - held), int)
    first = {"imi_vm20i/dataset1", "imi_vm20i/dataset4"}
    a = np.array([i for i in rows if frame.iloc[i].group_id in first], int)
    b = np.array([i for i in rows if frame.iloc[i].group_id not in first], int)
    plan = [(b, a), (a, b)]
    verify_plan(frame, rows, plan)
    return rows, np.array(sorted(held), int), plan
