"""Independently recalculate the two Chapter 7 calendar-date bootstrap contrasts."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

root = Path(__file__).resolve().parents[3]
out = Path(__file__).parent
base = root / "implementations/MSM/results"
parts = []
for p in (base / "06_evaluation_results/predictions").glob("P__primary__group_id__*/CASE_COMPLETE.json"):
    case = json.loads(p.read_text())
    source = base / case["predictions"].removeprefix("MSM/")
    df = pd.read_csv(source, usecols=["sample_id", "target", "model", "probability", "role", "seed", "corruption"], float_precision="round_trip")
    parts.append(df[df.role.eq("test") & df.corruption.eq("clean") & df.model.isin(["F2", "sensor_logistic", "QG_clean"])])
pred = pd.concat(parts, ignore_index=True)
meta = pd.read_csv(base / "03_processed_model_inputs/final_sample_manifest.csv", usecols=["sample_id", "calendar_date_group"], dtype=str).set_index("sample_id")
ids = sorted(pred.sample_id.unique())
dates, membership = np.unique(meta.loc[ids, "calendar_date_group"], return_inverse=True)
assert len(dates) == 5
draws = np.random.default_rng(20261027).multinomial(5, [0.2] * 5, size=2000)
boots = {}
for model in ["F2", "sensor_logistic", "QG_clean"]:
    seed_boots = []
    for seed in [42, 123, 20261023]:
        rows = pred[pred.model.eq(model) & pred.seed.eq(seed)].set_index("sample_id").loc[ids]
        assert len(rows) == 1895
        y = rows.target.to_numpy(int); score = rows.probability.to_numpy(float)
        order = np.argsort(-score, kind="stable")
        ends = np.r_[np.flatnonzero(np.diff(score[order])), len(order)-1]
        weights = draws[:, membership[order]]
        cumulative_positive = np.cumsum(weights * y[order], axis=1)[:, ends]
        cumulative_total = np.cumsum(weights, axis=1)[:, ends]
        positive_increments = np.diff(np.c_[np.zeros(len(draws)), cumulative_positive], axis=1)
        precision = np.divide(cumulative_positive, cumulative_total,
                              out=np.zeros_like(cumulative_positive, dtype=float), where=cumulative_total > 0)
        aps = np.sum(positive_increments * precision, axis=1) / cumulative_positive[:, -1]
        for i in range(5):
            reference = average_precision_score(y, score, sample_weight=draws[i, membership])
            assert abs(aps[i] - reference) < 1e-12
        seed_boots.append(aps)
    boots[model] = np.mean(seed_boots, axis=0)
saved = pd.read_csv(base / "06_evaluation_results/metrics/paired_group_bootstrap_95ci.csv")
results = []
for model in ["F2", "QG_clean"]:
    contrast = model + " minus sensor_logistic"
    values = boots[model] - boots["sensor_logistic"]
    ci = np.quantile(values, [.025, .975])
    expected = saved[saved.protocol.eq("primary__group_id") & saved.grouping.eq("calendar_date_group") & saved.comparison.eq(contrast)].iloc[0]
    assert np.allclose(ci, expected[["lower_95", "upper_95"]].to_numpy(dtype=float), atol=1e-12, rtol=0)
    results.append({"comparison": contrast, "recomputed_95ci": ci.tolist(), "valid_replicates": len(values)})
result = {"scope": "Saved predictions only, fixed fits/splits; paired calendar-date multiplicities shared across models/seeds", "dates": 5, "replicates": 2000, "rng_seed": 20261027, "results": results}
(out / "msm_uncertainty_recomputation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
