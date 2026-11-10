"""Finalize reports from completed artifacts, without changing fitted components."""
import collections
import datetime
import json
import os
from pathlib import Path

for name in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"]:
    os.environ[name] = "2"
if hasattr(os, "sched_getaffinity"):
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

RUN = Path(__file__).resolve().parent.parent
STUDY = RUN.parent.parent


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    progress = read(RUN / "progress.json")
    assert progress["status"] == "COMPLETE"
    summary = pd.read_csv(RUN / "comparison/comparison_table.csv").set_index("condition")
    metrics = pd.read_csv(RUN / "comparison/metrics.csv")
    verified = []
    costs = []
    replay = []
    for condition in ["cnn_only", "cnn_plus_encoder"]:
        table = pd.read_csv(RUN / f"comparison/identified_outer_predictions_{condition}.csv",
                            dtype={"recording_id": str, "segment_id": str})
        assert len(table) == 4530 and not table.duplicated(["recording_id", "segment_id"]).any()
        assert len(table.fold_name.unique()) == 5
        for scope, frame in [("pooled", table)] + list(table.groupby("fold_name")):
            for branch in ["visual", "sensor", "fused"]:
                value = float(average_precision_score(frame.failure, frame["p_" + branch]))
                saved = metrics.loc[(metrics.condition == condition) & (metrics.scope == scope) & (metrics.branch == branch)]
                assert len(saved) == 1 and abs(value - saved.AP.iloc[0]) < 1e-12
                verified.append(dict(condition=condition, scope=scope, branch=branch, AP=value))
        fits = [read(p) for p in (RUN / condition).glob("**/complete.json")]
        counts = collections.Counter(fit["status"] for fit in fits)
        costs.append(dict(condition=condition, new_heads=counts["NEW"], reused_heads=counts["REUSED"],
                          new_head_training_seconds=sum(fit.get("seconds", 0) for fit in fits)))
        for p in (RUN / condition).glob("fold_*/**/full_saved_model_replay.json"):
            replay.append(read(p))
    assert len(replay) == 10 and all(item["passed"] for item in replay)
    write(RUN / "checks/independent_encoder_metrics.json", {"passed": True, "metrics": verified, "outer_replay_records": len(replay)})
    sensor_fits = [read(p) for p in (RUN / "sensor_reference").glob("**/complete.json")]
    extraction = read(RUN / "provenance/completed_feature_extraction.json")
    preflight = read(RUN / "checks/real_extractor_preflight.json")
    for cost, measured in zip(costs, preflight["results"]):
        cost.update({key: measured[key] for key in ["dimension", "active_frozen_parameters", "trainable_head_parameters", "seconds_per_segment_after_warmup", "peak_cuda_bytes"]})
    pd.DataFrame(costs).to_csv(RUN / "comparison/costs.csv", index=False, float_format="%.17g")
    write(RUN / "comparison/execution_cost.json", {
        "feature_extraction": extraction,
        "sensor_fit_statuses": dict(collections.Counter(fit["status"] for fit in sensor_fits)),
        "sensor_fit_seconds": sum(fit.get("seconds", 0) for fit in sensor_fits),
        "stacker_fit_seconds": sum(read(p).get("seconds", 0) for p in RUN.glob("cnn*/fold_*/F2_stacker.json")),
        "cost_table": costs,
        "limitations": "Per-action extraction benchmarks exclude decoding. CNN whole-cohort cache was reused. Host high-water observations and CUDA preflight peaks are measured separately; wall-clock enforcement is cooperative."
    })
    now = datetime.datetime.now(datetime.timezone.utc)
    config = read(STUDY / "config.json")
    start = datetime.datetime.fromisoformat(config["started_utc"])
    progress.update(completed_paired_folds=5, completed_segments=4530,
                    actual_scientific_visual_fit_starts=len(progress["attempts"]["visual"]),
                    actual_scientific_sensor_fit_starts=len(progress["attempts"]["sensor"]),
                    actual_scientific_stacker_fit_starts=len(progress["attempts"]["stacker"]),
                    total_elapsed_seconds=(now-start).total_seconds(),
                    remaining_wall_seconds=max(0,config["wall_seconds"]-(now-start).total_seconds()),
                    updated_utc=now.isoformat(), blocker=None)
    for kind, cap in [("visual",55),("sensor",30),("stacker",12)]:
        progress[f"remaining_{kind}_fit_cap"] = cap-len(progress["attempts"][kind])
    if progress.get("safe_stop_reason"):
        progress["historical_safe_stop_reason"] = progress.pop("safe_stop_reason")
    write(RUN / "progress.json", progress)
    rows = ["| Condition | Visual AP | Sensor AP | F2 AP | Paired folds | Heads new / reused |",
            "|---|---:|---:|---:|---:|---:|"]
    for cost in costs:
        condition=cost["condition"]; r=summary.loc[condition]
        rows.append(f"| {condition} | {r.visual_AP:.6f} | {r.sensor_AP:.6f} | {r.F2_AP:.6f} | 5 | {cost['new_heads']} / {cost['reused_heads']} |")
    table = "\n".join(rows)
    findings = f"""The hybrid-encoder representation reduced pooled visual AP by 0.049729 and F2 AP by 0.015785 relative to CNN-only on 4,530 actions, 509 failures and 148 recordings. The paired recording-bootstrap 95% interval for the F2 difference is [-0.024804, -0.005800]; all 2,000 replicates were valid. This supports CNN-only under this fixed protocol, without establishing that attention or transformers are generally unhelpful.

{table}

All five matched folds completed. The 16 input frames were identical across conditions. Extractor weights and buffers stayed frozen; runtime traces show encoder projections, attention, FPN and PAN executing only on the encoder path. Guards excluded detector, proposal and decoder execution. Ten outer-condition saved-model replay checks passed on three identified actions each, using live pixels and cached sensor statistics. Cached-head probabilities were also replayed from saved components. This is not a claim that all actions were decoded a second time.

New encoder extraction took {extraction['new_extraction_wall_seconds']/60:.2f} minutes including decoding; its recorded compute time was {extraction['compute_seconds_this_invocation']['cnn_plus_encoder']:.2f} seconds. Training-only extractor benchmarks were 0.121970 seconds/action for CNN-only and 0.192610 seconds/action with the encoder, excluding decoding. Active frozen parameters were 11,190,112 versus 16,155,232; head parameters were 114,945 versus 98,561. This compares complete representations with different feature widths and compute, not isolated attention or matched capacity. New head fitting totalled {sum(c['new_head_training_seconds'] for c in costs):.2f} seconds. See `comparison/costs.csv`, `comparison/execution_cost.json`, and the resource observations for details.

Reuse: all compatible CNN feature rows and five CNN heads; five sensor fits were reused, with 20 sensor fits newly fitted. Forty-five visual heads and ten F2 stackers were newly fitted. No extractor fine-tuning occurred. No scientific extraction/fitting failure remains unresolved. Earlier resource-wait records are historical; the user later explicitly authorized checkpoint-pausing the separate visual study.

Uncertainty: the intervals condition on one fitted seed family and this exposed cohort. Secondary contrasts are exploratory; no external validation, temporal modelling, or robustness conclusion follows from this encoder comparison. The separately authorized noise study makes its own pre-noise choice on the fixed eligible common coverage.

Recommended next decision: require complete matched coverage and independent validation before adopting a different visual representation.

"""
    path = RUN / "comparison/RESULTS_SUMMARY.md"
    original = path.read_text()
    if "# Encoder comparison — " in original:
        original = original[original.index("# Encoder comparison — "):]
    original = original.replace("Still uncertain: any unexecuted extraction, full fitting, replay and paired effect.",
                                "Still uncertain: seed-to-seed variability, unseen recordings and external generalization.")
    path.write_text("# Completed findings\n\n"+findings+original)
    (RUN / "README_FIRST.md").write_text("# COMPLETE — five paired folds\n\n"
        "CNN-only performed better on the fixed clean-input comparison: 4,530 actions, 509 failures, 148 recordings, identical 16-frame inputs. Encoder-minus-CNN fused AP was −0.015785 (paired recording-bootstrap 95% interval [−0.024804, −0.005800]; 2,000 valid resamples).\n\n"+table+"\n\n"
        "Extractor weights stayed frozen. Runtime traces verified encoder attention/cross-scale execution and guarded the decoder/proposal paths. All ten outer-condition replay checks passed on three identified actions each. Thirty-six pooled/per-fold AP values were independently recalculated. No scientific stage remains incomplete.\n\n"
        "Costs: 71.00 minutes for new encoder extraction including decoding; compatible CNN features were reused. Detailed compute, head capacity, fit reuse and timings are in the results and cost tables.\n\n"
        "Review: [Results](comparison/RESULTS_SUMMARY.md), [metrics](comparison/metrics.csv), [paired intervals](comparison/paired_comparisons.csv), [CNN predictions](comparison/identified_outer_predictions_cnn_only.csv), [encoder predictions](comparison/identified_outer_predictions_cnn_plus_encoder.csv), [review package](REVIEW_PACKAGE.zip).\n\n"
        "Limits: one fitted seed family, exposed data, unequal feature widths/compute, and no external validation. Recommended next decision: require full matched coverage and independent validation before adopting a different representation.\n\n"
        "Evidence checked: real extraction, frozen-state guards, fits, saved-state replay and independently recalculated AP. Still uncertain: generalization and training variability. Defensible conclusion: CNN-only performed better on this fixed clean-input comparison.\n")
    print(table)


if __name__ == "__main__":
    main()
