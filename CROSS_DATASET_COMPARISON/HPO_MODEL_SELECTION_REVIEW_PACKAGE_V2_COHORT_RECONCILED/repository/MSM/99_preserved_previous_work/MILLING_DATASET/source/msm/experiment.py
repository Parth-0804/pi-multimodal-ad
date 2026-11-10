"""Reusable leakage-safe composition, independently usable by a later evaluator.

No command in this module starts the outer experimental matrix.
"""
import numpy as np
from .models import fit_visual, predict_visual, SensorClassifier, StaticF2
from .splits import verify_plan


def fit_branches(visual, sensor, target, train, config, seed, epochs=None):
    model, scaler, log = fit_visual(visual[train], target[train], config["visual"], seed, epochs)
    sensor_model = SensorClassifier().fit(sensor[train], target[train])
    return model, scaler, sensor_model, log


def branch_probabilities(fit, visual, sensor, rows):
    model, scaler, sensor_model = fit[:3]
    return np.column_stack([predict_visual(model, scaler, visual[rows]), sensor_model.predict(sensor[rows])])


def fit_oof_fusion(frame, visual, sensor, train, plan, config, seed, epochs=None):
    """Only declared train rows and validation OOF are accessible to F2."""
    train = np.asarray(train, int)
    verify_plan(frame, train, plan)
    target = frame.target.to_numpy(int)
    bank = np.full((len(frame), 2), np.nan)
    provenance, logs = {}, []
    for k, (a, b) in enumerate(plan):
        fit = fit_branches(visual, sensor, target, a, config, seed + k, epochs)
        bank[b] = branch_probabilities(fit, visual, sensor, b)
        fit_groups = sorted(set(frame.iloc[a].group_id))
        for i in b:
            provenance[frame.iloc[i].interval_id] = {
                branch: {"fit_groups": fit_groups, "selection_groups": [], "fold": k, "seed": seed + k}
                for branch in ("visual", "sensor")}
        logs.append(fit[3])
    if not np.isfinite(bank[train]).all() or np.isfinite(bank[np.setdiff1d(np.arange(len(frame)), train)]).any():
        raise ValueError("OOF bank coverage or outer isolation failed")
    fusion = StaticF2().fit(bank[train], target[train], frame.iloc[train].interval_id.tolist(),
                            frame.iloc[train].group_id.tolist(), provenance)
    final_fit = fit_branches(visual, sensor, target, train, config, seed + 99, epochs)
    return final_fit, fusion, bank, provenance, logs + [final_fit[3]]
