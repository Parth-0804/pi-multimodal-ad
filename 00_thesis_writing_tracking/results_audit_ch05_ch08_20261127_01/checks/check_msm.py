"""Read saved derived predictions; no model imports, fitting, inference or data writes."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
study = root / "implementations/MSM/results"
metrics_dir = study / "06_evaluation_results/metrics"
cases = sorted((study / "06_evaluation_results/predictions").glob("*/CASE_COMPLETE.json"))
parts, identities = [], []
for case_path in cases:
    case = json.loads(case_path.read_text())
    old = case["predictions"]
    p = study / old.removeprefix("MSM/")
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    assert actual == case["output_hashes"][old], str(p)
    identities.append({"path": str(p.relative_to(root)), "sha256": actual,
                       "bytes": p.stat().st_size, "case": case["case_id"]})
    columns = ["sample_id", "target", "model", "probability", "role", "seed",
               "fold", "protocol", "corruption", "group_id"]
    df = pd.read_csv(p, usecols=columns, float_precision="round_trip")
    keep = df.role.eq("test") & (df.corruption.eq("clean") | df.protocol.eq("primary__group_id"))
    parts.append(df.loc[keep].copy())
pred = pd.concat(parts, ignore_index=True)
rows = []
for key, df in pred.groupby(["protocol", "seed", "corruption", "model"]):
    assert not df.sample_id.duplicated().any(), key
    assert df.probability.notna().all(), key
    assert set(df.target.unique()) == {0, 1}, key
    rows.append(dict(zip(["protocol", "seed", "corruption", "model"], key)) | {
        "AP": average_precision_score(df.target, df.probability),
        "Brier": brier_score_loss(df.target, df.probability),
        "F1": f1_score(df.target, df.probability >= .5),
        "examples": len(df), "positive": int(df.target.sum())})
computed = pd.DataFrame(rows)
saved = pd.read_csv(metrics_dir / "pooled_heldout_metrics.csv", float_precision="round_trip")
matched = computed.merge(saved, on=["protocol", "seed", "corruption", "model"],
                         suffixes=("_computed", "_saved"), validate="one_to_one")
assert len(matched) == len(computed)
errors = {metric: float(abs(matched[metric + "_computed"] - matched[metric + "_saved"]).max())
          for metric in ["AP", "Brier", "F1", "examples", "positive"]}
assert all(v < 1e-12 for v in errors.values()), errors
clean = computed[computed.corruption.eq("clean")]
summary = clean.groupby(["protocol", "model"]).AP.agg(["mean", "std"])
stored = pd.read_csv(metrics_dir / "clean_seed_summary.csv").set_index(["protocol", "model"])
assert np.allclose(summary["mean"], stored.loc[summary.index, "AP_mean"], rtol=0, atol=1e-12)
assert np.allclose(summary["std"], stored.loc[summary.index, "AP_seed_std"], rtol=0, atol=1e-12)

# These rounded values are transcribed from the unchanged Chapter 7 tables.
models = ["visual", "sensor_logistic", "sensor_histgradient", "averaging", "F2", "F2_aug", "QG_clean", "QG_aug"]
clean_expected = [[.2989,.0109],[.8286,0],[.9013,0],[.7356,.0159],[.7569,.0111],[.7602,.0098],[.8374,.0134],[.8265,.0162]]
for model, expected in zip(models, clean_expected):
    assert np.allclose(summary.loc[("primary__group_id", model)].to_numpy(), expected, atol=.00005, rtol=0)
protocols = ["primary__group_id", "primary__machine_date_group", "primary__calendar_date_group",
             "exclude_label2__group_id", "exclude_label2__machine_date_group", "exclude_label2__calendar_date_group"]
sens_expected = [[.2989,.8286,.9013,.7569,.8374],[.5359,.8922,.8250,.7389,.8715],
                 [.5444,.8859,.8386,.8196,.8521],[.3164,.9403,.8965,.8235,.9308],
                 [.3396,.9265,.9098,.8562,.7372],[.4009,.8917,.9062,.5218,.6757]]
for protocol, expected in zip(protocols, sens_expected):
    actual = [summary.loc[(protocol, m), "mean"] for m in ["visual", "sensor_logistic", "sensor_histgradient", "F2", "QG_clean"]]
    assert np.allclose(actual, expected, atol=.00005, rtol=0), protocol
robustness = computed[computed.protocol.eq("primary__group_id")].groupby(["corruption", "model"]).AP.mean()
conditions = ["gaussian_blur_3", "brightness_contrast_3", "partial_occlusion_3", "frame_dropout_3",
              "sensor_noise_3", "channel_dropout_3", "missing_sensor_channels_3", "missing_visual", "missing_sensor"]
robust_expected = [[.8286,.7714,.7712,.6828,.9013],[.8286,.7700,.7688,.6787,.9013],
                   [.8286,.7708,.7709,.8332,.9013],[.8286,.7604,.7654,.8331,.9013],
                   [.2989,.2069,.2062,.2986,.6062],[.2989,.4198,.4188,.4754,.6466],
                   [.2989,.4477,.4469,.5115,.5460],[.8286,.8286,.8286,.8286,.9013],
                   [.2989,.2989,.2989,.2989,None]]
for cond, expected in zip(conditions, robust_expected):
    survivor = "visual" if cond.startswith(("sensor_noise", "channel_dropout", "missing_sensor")) else "sensor_logistic"
    actual = [robustness[("clean", survivor)]] + [robustness[(cond, m)] for m in ["F2", "F2_aug", "QG_aug"]]
    if expected[-1] is not None:
        actual.append(robustness[(cond, "sensor_histgradient")])
    assert np.allclose(actual, [x for x in expected if x is not None], atol=.00005, rtol=0), cond

counts = pred[pred.corruption.eq("clean") & pred.model.eq("visual") & pred.seed.eq(42)]
folds = counts.groupby(["protocol", "fold"]).target.agg(["sum", "count"])
expected_counts = [[[157,567],[37,730],[142,598]],[[38,468],[95,664],[203,763]],
                   [[157,422],[99,689],[80,784]],[[138,712],[122,429],[76,629]],
                   [[38,447],[95,641],[203,682]],[[99,645],[157,341],[80,784]]]
for protocol, expected in zip(protocols, expected_counts):
    assert np.array_equal(folds.loc[protocol].to_numpy(), expected), protocol
train = pd.read_csv(metrics_dir / "training_diagnostic_AP.csv")
train = train[train.protocol.eq("primary__group_id") & train.model.eq("visual")].training_in_sample_AP
assert len(train) == 9
assert np.allclose([train.mean(), train.min(), train.max()], [.9807,.9634,.9994], atol=.00005, rtol=0)
tradeoff = clean[clean.protocol.eq("primary__group_id") & clean.seed.eq(42)].set_index("model")
for model, expected in [("F2", [.0561,.8204]),("sensor_logistic", [.0617,.8113]),("QG_clean", [.0644,.7864])]:
    assert np.allclose(tradeoff.loc[model, ["Brier", "F1"]].to_numpy(dtype=float), expected, atol=.00005, rtol=0)

result = {"scope": "All six protocols' clean pooled AP/Brier/F1 plus all primary corruption conditions, recomputed from saved derived predictions; no fitting or inference",
          "cases_read": len(cases), "retained_prediction_rows": len(pred), "pooled_metric_rows": len(computed),
          "max_absolute_error": errors, "four_manuscript_tables_match_at_printed_precision": True,
          "nine_fit_training_diagnostic": {"mean": train.mean(), "min": train.min(), "max": train.max()},
          "table_numeric_cells_checked": 126, "prediction_files": identities}
(out / "msm_recomputation.json").write_text(json.dumps(result, indent=2) + "\n")
computed.to_csv(out / "msm_recomputed_metrics.csv", index=False)
print(json.dumps({k: v for k, v in result.items() if k != "prediction_files"}, indent=2))
