#!/usr/bin/env python3
"""Shared protocol for ARCH-VAL-PB Gates 2 and 3.

THE PROTOCOL PROBLEM, and why the evaluation is what it is
----------------------------------------------------------
The Gate 2 target (damage severity) is CONSTANT PER BEARING. Under plain
leave-one-operating-condition-out, every bearing appears in training under the
other three conditions, so a model can identify the bearing from its vibration
signature and emit the severity it memorised. That would pass Gate 2 without
any generalisation at all.

So the primary protocol holds out BOTH axes at once:

    test = (held-out operating condition) AND (held-out bearings)
    train = (the other three conditions)  AND (the other bearings)

Every row is predicted exactly once, because each row has one condition and
its bearing sits in exactly one bearing fold. Plain condition-only LOOCO is
also reported, to show how large the memorisation effect is.

Bootstrap intervals resample BEARINGS with replacement, since measurements
from one bearing are not independent.
"""
from __future__ import annotations
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

HI = ("mean","std","rms","skew","kurt","p2p","crest","shape")
CX = ("mean","std","min","max","range","median")
VIB = [f"vib_{s}" for s in HI] + ["mask_vib"]
CUR = [f"cur1_{s}" for s in HI] + [f"cur2_{s}" for s in HI] + ["mask_cur1","mask_cur2"]
CTX = [f"{c}_{s}" for c in ("speed","torque","force","temp") for s in CX] \
      + [f"mask_{c}" for c in ("speed","torque","force","temp")]
GROUPS = {"vib": VIB, "cur": CUR, "ctx": CTX}
META = ["bearing","condition","measurement","window","fault","origin","severity"]


class MLP(nn.Module):
    """Frozen architecture for every arm: 2 hidden layers, 64 -> 32."""
    def __init__(self, n_in: int, hidden=(64, 32), p_drop=0.1):
        super().__init__()
        layers, prev = [], n_in
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(p_drop)]
            prev = h
        layers += [nn.Linear(prev, 1)]
        self.net = nn.Sequential(*layers)
    def forward(self, x):
        return self.net(x).squeeze(-1)


def pairwise_rank_loss(pred: torch.Tensor, teacher: torch.Tensor) -> torch.Tensor:
    """Pairwise rank distillation -- COPIED from the PHM implementation in
    scripts/phm2026/results/closing_task_c.py so the mechanism under test is the same
    one, not a re-derivation of it.

    Logistic pairwise ranking loss: order predictions like the teacher.
    """
    diff_pred = pred.unsqueeze(0) - pred.unsqueeze(1)
    diff_teacher = teacher.unsqueeze(0) - teacher.unsqueeze(1)
    mask = diff_teacher.abs() > 1e-12
    if not mask.any():
        return pred.sum() * 0.0
    return nn.functional.softplus(
        -diff_pred[mask] * torch.sign(diff_teacher[mask])
    ).mean()


def fit_predict(Xtr, ytr, Xte, seed, epochs=150, lr=1e-3, wd=1e-4,
                teacher_tr=None, distill_weight=0.0, batch=256):
    """Train one MLP and predict. distill_weight=0 must reduce exactly to the
    plain regression arm -- verified by test in gate3."""
    torch.manual_seed(seed); np.random.seed(seed)
    # Near-constant features (e.g. speed_std inside one operating condition)
    # make StandardScaler divide by ~0, which sends held-out-condition inputs
    # to enormous z-scores and blows the MLP up. Floor the scale and clip the
    # transformed range. Applied identically to every arm.
    sc = StandardScaler().fit(Xtr)
    sc.scale_ = np.maximum(sc.scale_, 1e-3)
    Xtr_t = torch.tensor(np.clip(sc.transform(Xtr), -10, 10), dtype=torch.float32)
    Xte_t = torch.tensor(np.clip(sc.transform(Xte), -10, 10), dtype=torch.float32)
    ytr_t = torch.tensor(ytr, dtype=torch.float32)
    tt = torch.tensor(teacher_tr, dtype=torch.float32) if teacher_tr is not None else None

    model = MLP(Xtr.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    n = len(Xtr_t)
    g = torch.Generator().manual_seed(seed)
    model.train()
    for _ in range(epochs):
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, batch):
            idx = perm[i:i+batch]
            opt.zero_grad()
            out = model(Xtr_t[idx])
            loss = nn.functional.mse_loss(out, ytr_t[idx])
            if distill_weight > 0 and tt is not None:
                loss = loss + distill_weight * pairwise_rank_loss(out, tt[idx])
            loss.backward(); opt.step()
    model.eval()
    with torch.no_grad():
        return model(Xte_t).numpy()


def folds(df: pd.DataFrame, n_bearing_folds: int, bearing_disjoint: bool, seed=0):
    """Yield (train_idx, test_idx, test_condition) covering every row once."""
    conds = sorted(df.condition.unique())
    bearings = np.array(sorted(df.bearing.unique()))
    rng = np.random.default_rng(seed)
    shuffled = bearings[rng.permutation(len(bearings))]
    bfolds = np.array_split(shuffled, n_bearing_folds)
    for c in conds:
        if not bearing_disjoint:
            tr = df.index[df.condition.ne(c)].to_numpy()
            te = df.index[df.condition.eq(c)].to_numpy()
            yield tr, te, c
        else:
            for bf in bfolds:
                held = set(bf)
                tr = df.index[df.condition.ne(c) & ~df.bearing.isin(held)].to_numpy()
                te = df.index[df.condition.eq(c) &  df.bearing.isin(held)].to_numpy()
                if len(tr) and len(te):
                    yield tr, te, c


def cluster_bootstrap(df: pd.DataFrame, pred: np.ndarray, truth: np.ndarray,
                      metric, n_boot=2000, seed=0):
    """Resample BEARINGS with replacement; return (point, lo, hi)."""
    rng = np.random.default_rng(seed)
    bearings = df.bearing.to_numpy()
    uniq = np.unique(bearings)
    idx_by = {b: np.flatnonzero(bearings == b) for b in uniq}
    point = metric(truth, pred)
    stats = []
    for _ in range(n_boot):
        pick = rng.choice(uniq, len(uniq), replace=True)
        idx = np.concatenate([idx_by[b] for b in pick])
        stats.append(metric(truth[idx], pred[idx]))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return point, lo, hi


def paired_bootstrap(df: pd.DataFrame, pred_a: np.ndarray, pred_b: np.ndarray,
                     truth: np.ndarray, metric, n_boot=2000, seed=0):
    """Bearing-clustered CI for metric(a) - metric(b), paired on the same rows."""
    rng = np.random.default_rng(seed)
    bearings = df.bearing.to_numpy()
    uniq = np.unique(bearings)
    idx_by = {b: np.flatnonzero(bearings == b) for b in uniq}
    point = metric(truth, pred_a) - metric(truth, pred_b)
    stats = []
    for _ in range(n_boot):
        pick = rng.choice(uniq, len(uniq), replace=True)
        idx = np.concatenate([idx_by[b] for b in pick])
        stats.append(metric(truth[idx], pred_a[idx]) - metric(truth[idx], pred_b[idx]))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return point, lo, hi
