"""Predeclared F2-minus-branch contrasts from fixed completed predictions only."""
import datetime
import hashlib
import json
import os
import time
from pathlib import Path

for name in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"]:
    os.environ[name] = "2"
if hasattr(os, "sched_getaffinity"):
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

RUN = Path(__file__).resolve().parent.parent
KEYS = ["recording_id", "segment_id"]


def read(path):
    return json.loads(path.read_text())


def main():
    assert read(RUN / "progress.json")["status"] == "COMPLETE_ON_PILOT_COVERAGE"
    config = read(RUN.parent.parent / "config.json")
    deadline = datetime.datetime.fromisoformat(config["started_utc"]).timestamp()+config["wall_seconds"]-config["report_reserve_seconds"]
    groups = {}
    for marker in sorted((RUN / "predictions").glob("**/complete.json")):
        info = read(marker); job = info["job"]
        if job["family"] == "missing_modality":
            continue
        path = marker.parent / "predictions.csv"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == info["predictions_sha256"]
        frame = pd.read_csv(path, dtype={key: str for key in KEYS},
                            usecols=KEYS+["failure", "p_fused", "p_sensor", "p_visual", "status"])
        assert (frame.status == "OK").all() and not frame.duplicated(KEYS).any()
        groups.setdefault((job["family"], job["level"]), []).append(frame.sort_values(KEYS).reset_index(drop=True))
    assert len(groups) == 19
    clean = groups[("clean", "clean")][0]
    y = clean.failure.to_numpy()
    recording = clean.recording_id.to_numpy()
    unique = np.unique(recording)
    per_recording = [np.flatnonzero(recording == value) for value in unique]
    rng = np.random.default_rng(314159); draws = []; skipped = 0; digest = hashlib.sha256()
    for _ in range(2000):
        selection = rng.integers(0, len(unique), len(unique))
        digest.update(selection.astype("<i8").tobytes())
        rows = np.concatenate([per_recording[index] for index in selection])
        if len(np.unique(y[rows])) < 2:
            skipped += 1
        else:
            draws.append(rows)
    sensitivity = pd.read_csv(RUN / "comparison/modality_sensitivity.csv")
    results = []; started = time.perf_counter()
    for (family, level), frames in sorted(groups.items()):
        assert len(frames) == (1 if family in ["clean", "image_blur"] else 3)
        for frame in frames:
            assert frame[KEYS].equals(clean[KEYS]) and np.array_equal(frame.failure, y)
        values = [frame[["p_fused", "p_sensor", "p_visual"]].to_numpy() for frame in frames]

        def contrast(rows):
            ap = np.mean([[average_precision_score(y[rows], value[rows, branch])
                           for branch in range(3)] for value in values], axis=0)
            return ap[0]-ap[1:]

        observed = contrast(np.arange(len(y)))
        saved = sensitivity.loc[(sensitivity.family == family) & (sensitivity.level == level)]
        assert len(saved) == len(frames)
        np.testing.assert_allclose(observed, saved[["fusion_minus_sensor_AP", "fusion_minus_visual_AP"]].mean().to_numpy(), atol=1e-12, rtol=0)
        sampled = []
        for index, rows in enumerate(draws):
            if index % 200 == 0:
                assert time.time() < deadline, "ORIGINAL_REPORT_RESERVE_REACHED"
            sampled.append(contrast(rows))
        low, high = np.percentile(sampled, [2.5, 97.5], axis=0)
        for index, branch in enumerate(["sensor", "visual"]):
            results.append(dict(family=family, level=level, contrast="F2_minus_"+branch,
                                AP_difference=float(observed[index]), lower95=float(low[index]), upper95=float(high[index]),
                                realizations=len(frames), requested_replicates=2000,
                                effective_replicates=len(draws), skipped_replicates=skipped, seed=314159,
                                exposure="DEVELOPMENT-EXPOSED; exploratory, unadjusted"))
        print(f"Branch intervals complete: {family}/{level}", flush=True)
    pd.DataFrame(results).to_csv(RUN / "comparison/branch_contrast_intervals.csv", index=False, float_format="%.17g")
    (RUN / "checks/branch_contrast_bootstrap.json").write_text(json.dumps({
        "passed": True, "seed": 314159, "requested_replicates": 2000,
        "effective_replicates": len(draws), "skipped_replicates": skipped,
        "recording_draws_sha256": digest.hexdigest(), "contrasts": len(results),
        "same_recording_multiplicities_for_all_contrasts": True,
        "stochastic_aggregation": "Mean of three separately computed AP differences within each recording resample",
        "seconds": time.perf_counter()-started}, indent=2)+"\n")


if __name__ == "__main__":
    main()
