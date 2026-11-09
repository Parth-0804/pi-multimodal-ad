#!/usr/bin/env python3
"""Audit native MSM intervals and file coverage without reading sensor/media payloads."""
import argparse
import collections
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import median

MEANINGS = {0: "normal/stable cutting", 1: "abnormal cutting requiring intervention",
            2: "defective tool during stable cutting"}


def number(value):
    try:
        parsed = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def validate_rows(rows):
    """Keep every row, distinguish invalid targets/times from contextual warnings."""
    result, seen, prior_start, prior_end = [], set(), None, None
    for source_row, row in enumerate(rows, 2):
        errors, warnings = [], []
        start, end, label = (number(row.get(k)) for k in ("start", "end", "label"))
        if label not in (Decimal(0), Decimal(1), Decimal(2)):
            errors.append("invalid_or_missing_label")
        if start is None or end is None:
            errors.append("invalid_or_missing_time")
        elif start < 0 or end <= start:
            errors.append("negative_start_or_nonpositive_duration")
        key = json.dumps(row, sort_keys=True)
        if key in seen:
            warnings.append("duplicate_annotation_row")
        seen.add(key)
        if start is not None and end is not None:
            if prior_start is not None and start < prior_start:
                warnings.append("source_rows_not_sorted_by_start")
            if prior_end is not None and start < prior_end:
                warnings.append("overlaps_earlier_interval")
            prior_start = start
            prior_end = end if prior_end is None else max(prior_end, end)
        if None in row:
            errors.append("extra_csv_fields")
        missing_context = [k for k, v in row.items() if k not in ("start", "end", "label") and v in (None, "")]
        if missing_context:
            warnings.append("missing_context:" + ",".join(missing_context))
        result.append({"source_row": source_row, "native": row, "start": start, "end": end,
                       "label": int(label) if label in (Decimal(0), Decimal(1), Decimal(2)) else None,
                       "duration": end - start if start is not None and end is not None else None,
                       "errors": errors, "warnings": warnings})
    return result


def duration_stats(values):
    values = sorted(float(v) for v in values)
    if not values:
        return {"n": 0}
    return {"n": len(values), "min_s": min(values), "median_s": median(values),
            "max_s": max(values), "sum_s": sum(values)}


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def modality(name):
    filename = Path(name).name
    if filename == "label.csv":
        return "label"
    if filename.endswith(".mp4"):
        return "video"
    if filename.endswith(".wav"):
        return "audio_" + Path(filename).stem.rsplit("_", 1)[-1]
    if filename.endswith(".csv"):
        return Path(filename).stem.rsplit("_", 1)[-1]
    return Path(filename).suffix.lstrip(".")


def audit(run):
    cfg = json.loads((run / "config/resolved_config.json").read_text())
    inventory = json.loads((run / "manifests/official_file_inventory.json").read_text())
    if inventory["handle"] != cfg["handle"] or inventory["dataset_id"] != cfg["dataset_id"]:
        raise ValueError("Inventory/config identity mismatch")
    remote = {f["name"]: f for f in inventory["files"]}
    data_root = Path(cfg["data_root"])
    expected = [f"{m}/dataset{i}/label.csv" for m, n in cfg["expected_experiments"].items() for i in range(1, n + 1)]
    actual_labels = {p for p in remote if p.endswith("/label.csv")}
    if set(expected) != actual_labels:
        raise ValueError("Official annotation hierarchy differs from expected experiments")
    interval_rows, groups, issues, inputs, hashes = [], [], [], [], collections.defaultdict(list)
    valid_durations, native_context = collections.defaultdict(list), set()
    for relative in expected:
        path = data_root / relative
        machine, experiment, _ = relative.split("/")
        group = machine + "/" + experiment
        source_files = [f for f in inventory["files"] if f["name"].startswith(group + "/")]
        record = {"machine": machine, "experiment": experiment, "group_id": group,
                  "rows": 0, "valid_intervals": 0, "label_0": 0, "label_1": 0, "label_2": 0,
                  "invalid_rows": 0, "warning_rows": 0, "annotation_status": "missing",
                  "modalities": ";".join(sorted({modality(f["name"]) for f in source_files})),
                  "all_files_bytes": sum(f["bytes"] for f in source_files)}
        if not path.is_file():
            issues.append({"group": group, "error": "missing_annotation"})
            groups.append(record)
            continue
        body = path.read_bytes()
        sha = hashlib.sha256(body).hexdigest()
        hashes[sha].append(group)
        inputs.append({"path": str(path), "dataset_relative_path": relative, "bytes": len(body),
                       "official_bytes": remote[relative]["bytes"], "sha256": sha})
        if len(body) != remote[relative]["bytes"]:
            raise ValueError("Annotation length differs from pinned inventory: " + relative)
        with path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames or []
            if len(fields) != len(set(fields)) or not {"start", "end", "label"}.issubset(fields):
                raise ValueError("Invalid CSV header: " + relative)
            parsed = validate_rows(list(reader))
        native_context.update(k for k in fields if k not in ("start", "end", "label"))
        record.update(rows=len(parsed), annotation_status="present")
        if not parsed:
            issues.append({"group": group, "error": "empty_annotation"})
        for row in parsed:
            native = row["native"]
            item = {"dataset_id": cfg["dataset_id"], "dataset_version": cfg["version"],
                    "dataset_handle": cfg["handle"], "machine": machine, "experiment": experiment,
                    "group_id": group, "interval_id": f"{group}/row{row['source_row']}",
                    "label_file": relative, "label_file_sha256": sha, "source_row": row["source_row"],
                    "start_s": native.get("start", ""), "end_s": native.get("end", ""),
                    "duration_s": str(row["duration"]) if row["duration"] is not None else "",
                    "native_label": native.get("label", ""), "native_label_meaning": MEANINGS.get(row["label"], "invalid"),
                    "valid": not row["errors"], "errors": ";".join(row["errors"]), "warnings": ";".join(row["warnings"]),
                    "native_context_json": json.dumps({k: v for k, v in native.items() if k not in ("start", "end", "label")}, sort_keys=True)}
            interval_rows.append(item)
            if row["errors"]:
                record["invalid_rows"] += 1
            else:
                record["valid_intervals"] += 1
                record[f"label_{row['label']}"] += 1
                valid_durations[(machine, row["label"])].append(row["duration"])
            if row["warnings"]:
                record["warning_rows"] += 1
            if row["warnings"] or row["errors"]:
                issues.append({"group": group, "source_row": row["source_row"], "errors": row["errors"], "warnings": row["warnings"]})
        groups.append(record)
    counts = {}
    for machine in cfg["expected_experiments"]:
        subset = [g for g in groups if g["machine"] == machine]
        counts[machine] = {k: sum(g[k] for g in subset) for k in ("rows", "valid_intervals", "label_0", "label_1", "label_2", "invalid_rows", "warning_rows")}
        counts[machine].update(experiments=len(subset), positive_groups=[g["experiment"] for g in subset if g["label_1"]],
                               normal_only_groups=[g["experiment"] for g in subset if g["label_0"] and not g["label_1"] and not g["label_2"]],
                               tool_defect_groups=[g["experiment"] for g in subset if g["label_2"]],
                               mixed_binary_groups=[g["experiment"] for g in subset if g["label_1"] and (g["label_0"] or g["label_2"])])
    summary = {"dataset_id": cfg["dataset_id"], "version": cfg["version"], "handle": cfg["handle"],
               "experiments": len(groups), "annotation_files": len(inputs), "rows": len(interval_rows),
               "valid_intervals": sum(g["valid_intervals"] for g in groups), "by_machine": counts,
               "durations_by_machine_and_class": {f"{m}/label_{k}": duration_stats(v) for (m, k), v in valid_durations.items()},
               "duration_all": duration_stats([v for vs in valid_durations.values() for v in vs]),
               "invalid_rows": sum(g["invalid_rows"] for g in groups),
               "warning_rows": sum(g["warning_rows"] for g in groups), "issues": issues,
               "identical_annotation_hash_groups": [v for v in hashes.values() if len(v) > 1],
               "native_context_columns": sorted(native_context)}
    write_csv(run / "MSM_INTERVAL_MANIFEST.csv", interval_rows)
    write_csv(run / "manifests/experiment_summary.csv", groups)
    write_csv(run / "manifests/file_inventory.csv", [{**f, "modality": modality(f["name"]),
                                                     "local_status": "present" if (data_root / f["name"]).is_file() else "not_downloaded"} for f in inventory["files"]])
    (run / "manifests/input_manifest.json").write_text(json.dumps(inputs, indent=2) + "\n")
    (run / "manifests/audit_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (run / "manifests/warnings.json").write_text(json.dumps(issues, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    audit(parser.parse_args().run)
