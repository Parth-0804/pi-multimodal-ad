#!/usr/bin/env python3
"""Stream pilot sensor tables, audit clocks/missingness, and compute interval diagnostics."""
import argparse
import collections
import csv
import json
import os
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import pandas as pd
import soundfile as sf

COMMON_MTC = ["watt", "Spindle_Speed", "S_Axis_Load", "Feed_Rate", "X_Axis_Load", "Y_Axis_Load", "Z_Axis_Load",
              "smarms", "xmarms", "ymarms", "zmarms", "smvrms", "xmvrms", "ymvrms", "zmvrms"]
INDUSTRY_MTC = ["s_load", "s_speed", "xpm", "xpw", "ypm", "ypw", "zpm", "zpw"]


def dump(path, value):
    def clean(x):
        if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)): return [clean(v) for v in x]
        if isinstance(x, np.generic): x = x.item()
        if isinstance(x, float) and not np.isfinite(x): return None
        return x
    with path.open("x") as stream:
        json.dump(clean(value), stream, indent=2, allow_nan=False); stream.write("\n")


def csv_output(path, rows):
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def new_accumulator():
    return {"n": 0, "missing": 0, "sum": 0., "sum2": 0., "min": float("inf"), "max": -float("inf")}


def accumulate(state, values):
    finite = values[np.isfinite(values)]
    state["n"] += len(finite); state["missing"] += len(values)-len(finite)
    if len(finite):
        state["sum"] += float(np.sum(finite, dtype=np.float64))
        state["sum2"] += float(np.dot(finite, finite))
        state["min"] = min(state["min"], float(finite.min()))
        state["max"] = max(state["max"], float(finite.max()))


def finalize(state):
    n = state["n"]
    if not n:
        return {"n": 0, "missing": state["missing"], "mean": None, "std": None, "rms": None, "min": None, "max": None, "peak_to_peak": None}
    mean = state["sum"]/n
    return {"n": n, "missing": state["missing"], "mean": mean, "std": float(np.sqrt(max(0., state["sum2"]/n-mean*mean))),
            "rms": float(np.sqrt(state["sum2"]/n)), "min": state["min"], "max": state["max"], "peak_to_peak": state["max"]-state["min"]}


def main(run):
    config = json.loads((run / "config/resolved_config.json").read_text()); root = Path(config["data_root"])
    audit, interval_stats = {}, []
    for group in config["selected_groups"]:
        folder = root / group; labels = pd.read_csv(folder / "label.csv"); record = {}
        for mod in ("mtc", "acc", "ct"):
            path = next(folder.glob("*_" + mod + ".csv"), None)
            if path is None:
                record[mod] = {"available": False}; continue
            columns = list(pd.read_csv(path, nrows=0).columns)
            selected = [c for c in (COMMON_MTC if group.startswith("imi_") else INDUSTRY_MTC) if c in columns] if mod == "mtc" else [c for c in columns if c != "time"]
            channel_stats = {c: new_accumulator() for c in selected}
            interval_acc = {(i, c): new_accumulator() for i in labels.index for c in selected}
            row_count, missing_times, duplicate_times, reversed_times = 0, 0, 0, 0
            first_time, last_time, prior_time, max_gap = None, None, None, 0.
            dt_sample, semantic_unavailable, missing_cells = [], collections.Counter(), collections.Counter()
            changed = collections.Counter(); prior_values = {}; change_gaps = collections.defaultdict(list); prior_change = {}
            trace_time, trace_values = [], {c: [] for c in selected}
            for chunk in pd.read_csv(path, chunksize=200_000):
                row_count += len(chunk)
                missing_cells.update(chunk.isna().sum().to_dict())
                for c in chunk.select_dtypes(include=["object"]).columns:
                    semantic_unavailable[c] += int(chunk[c].isin(["UNAVAILABLE", "Unavailable", "unavailable"]).sum())
                t = pd.to_numeric(chunk["time"], errors="coerce").to_numpy(dtype=float)
                missing_times += int((~np.isfinite(t)).sum()); finite_t = t[np.isfinite(t)]
                if not len(finite_t): continue
                if first_time is None: first_time = float(finite_t[0])
                last_time = float(finite_t[-1])
                dt = np.diff(np.r_[prior_time, finite_t] if prior_time is not None else finite_t)
                prior_time = float(finite_t[-1]); duplicate_times += int((dt == 0).sum()); reversed_times += int((dt < 0).sum())
                if len(dt): max_gap = max(max_gap, float(dt.max()))
                if len(dt_sample) < 100_000: dt_sample.extend(dt[:100_000-len(dt_sample)].tolist())
                values = {c: pd.to_numeric(chunk[c], errors="coerce").to_numpy(dtype=float) for c in selected}
                for c, y in values.items():
                    accumulate(channel_stats[c], y)
                    if mod == "mtc":
                        prev = prior_values.get(c, y[0]); flags = np.r_[y[0] != prev, y[1:] != y[:-1]] & np.isfinite(y)
                        changed[c] += int(flags.sum()); prior_values[c] = y[-1]
                        for tm in t[flags]:
                            if c in prior_change: change_gaps[c].append(float(tm-prior_change[c]))
                            prior_change[c] = float(tm)
                # Source clocks are monotonic in this pilot; slices preserve native timestamps.
                for i, label in labels.iterrows():
                    a, b = np.searchsorted(t, [label.start, label.end], side="left")
                    for c in selected: accumulate(interval_acc[(i, c)], values[c][a:b])
                if mod == "acc":
                    bins = np.floor(t*10).astype(int)
                    unique, starts, counts = np.unique(bins, return_index=True, return_counts=True)
                    trace_time.extend((unique/10).tolist())
                    for c, y in values.items(): trace_values[c].extend(np.sqrt(np.add.reduceat(y*y, starts)/counts).tolist())
                else:
                    trace_time.extend(t.tolist())
                    for c, y in values.items(): trace_values[c].extend(y.tolist())
            dt_sample = np.asarray(dt_sample); median_dt = float(np.median(dt_sample[dt_sample > 0]))
            if reversed_times or missing_times:
                raise ValueError("Nonmonotonic/invalid sensor times require a separate ingestion policy: " + str(path))
            record[mod] = {"available": True, "path": str(path), "columns": columns, "diagnostic_channels": selected,
                           "rows": row_count, "time_start_s": first_time, "time_end_s": last_time,
                           "median_dt_s": median_dt, "nominal_rows_per_second": 1/median_dt, "max_gap_s": max_gap,
                           "missing_time_rows": missing_times, "duplicate_time_rows": duplicate_times, "reversed_time_rows": reversed_times,
                           "missing_cells_by_column": dict(missing_cells), "unavailable_cells_by_column": dict(semantic_unavailable),
                           "channels": {c: finalize(a) for c, a in channel_stats.items()},
                           "changed_value_counts": dict(changed),
                           "median_changed_value_gap_s": {c: float(np.median(g)) for c, g in change_gaps.items() if g}}
            np.savez_compressed(run / "cache" / (group.replace("/", "_")+"_"+mod+"_trace.npz"), time=np.asarray(trace_time), **{c: np.asarray(y) for c, y in trace_values.items()})
            for (i, c), state in interval_acc.items():
                interval_stats.append({"group_id": group, "source_row": i+2, "interval_id": f"{group}/row{i+2}",
                                       "native_label": int(labels.iloc[i].label), "modality": mod, "channel": c,
                                       "start_s": labels.iloc[i].start, "end_s": labels.iloc[i].end, **finalize(state)})
            print(group, mod, row_count, first_time, last_time, "median_dt", median_dt, flush=True)
        audio_records = []
        for path in folder.glob("*.wav"):
            info = sf.info(path); accum = new_accumulator(); clipped = 0
            for block in sf.blocks(path, blocksize=192_000, dtype="float32", always_2d=True):
                accumulate(accum, block.astype(float).ravel()); clipped += int((np.abs(block) >= 32767/32768).sum())
            audio_records.append({"path": str(path), "sample_rate": info.samplerate, "channels": info.channels,
                                  "frames": info.frames, "duration_s": info.frames/info.samplerate, "subtype": info.subtype,
                                  "sample_stats": finalize(accum), "clipped_sample_fraction": clipped/(info.frames*info.channels)})
            if path.name.endswith("_s0.wav"):
                with sf.SoundFile(path) as source:
                    for i, label in labels.iterrows():
                        a, b = round(label.start*info.samplerate), round(label.end*info.samplerate)
                        source.seek(max(0, a)); y = source.read(max(0, min(b, info.frames)-a), dtype="float64", always_2d=True)
                        state = new_accumulator(); accumulate(state, y.ravel())
                        interval_stats.append({"group_id": group, "source_row": i+2, "interval_id": f"{group}/row{i+2}",
                                               "native_label": int(label.label), "modality": "audio", "channel": "s0",
                                               "start_s": label.start, "end_s": label.end, **finalize(state)})
        record["audio"] = audio_records; audit[group] = record
    dump(run / "manifests/sensor_audit.json", audit)
    csv_output(run / "manifests/sensor_interval_statistics.csv", interval_stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--run", type=Path, required=True)
    main(parser.parse_args().run)
