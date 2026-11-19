#!/usr/bin/env python3
"""Build the Stage 1 review documents from the native annotation audit."""
import argparse
import collections
import csv
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from audit_annotations import MEANINGS, modality, number, write_csv

PILOT = {
    "imi_vm20i/dataset1": "Abnormal cutting with defective tool; 12 label-1 intervals",
    "imi_vm20i/dataset4": "Stable defective-tool control; 12 label-2 intervals",
    "imi_vm20i/dataset19": "Normal control; 19 label-0 intervals; test video offset",
    "imi_vmx30ui/dataset9": "Second-machine mixed experiment; 12 label-0 and 2 label-1 intervals",
    "imi_vmx30ui/dataset8": "Second-machine normal control; 64 label-0 intervals",
    "tmf_vf10/dataset1": "Optional industrial diagnostic; 5 label-0 and 1 label-1 intervals; no video",
}


def table(headers, rows):
    return "\n".join(["| " + " | ".join(map(str, headers)) + " |",
                      "| " + " | ".join("---" for _ in headers) + " |"] +
                     ["| " + " | ".join(map(str, row)) + " |" for row in rows])


def write_new(path, text):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(text.rstrip() + "\n")


def main(run):
    cfg = json.loads((run / "config/resolved_config.json").read_text())
    summary = json.loads((run / "manifests/audit_summary.json").read_text())
    files = json.loads((run / "manifests/official_file_inventory.json").read_text())["files"]
    groups = list(csv.DictReader((run / "manifests/experiment_summary.csv").open()))
    intervals = list(csv.DictReader((run / "MSM_INTERVAL_MANIFEST.csv").open()))
    lookup = {g["group_id"]: g for g in groups}
    by_machine = summary["by_machine"]
    source = "https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly"
    paper = "https://www.nature.com/articles/s41597-026-07255-7"
    stamp = datetime.now(timezone.utc)
    counts = collections.Counter({k: sum(v[k] for v in by_machine.values()) for k in ("label_0", "label_1", "label_2")})
    machine_table = table(["Machine", "Experiments", "Intervals", "Label 0", "Label 1", "Label 2", "Label-1 groups"],
                          [[m, v["experiments"], v["valid_intervals"], v["label_0"], v["label_1"], v["label_2"], len(v["positive_groups"])] for m, v in by_machine.items()] +
                          [["TOTAL", len(groups), len(intervals), counts["label_0"], counts["label_1"], counts["label_2"], sum(len(v["positive_groups"]) for v in by_machine.values())]])
    context_issues, markers = [], collections.Counter()
    tools = collections.defaultdict(set)
    for row in intervals:
        context = json.loads(row["native_context_json"])
        for field in ("N", "ap", "ae", "F", "Z", "D"):
            value = number(context.get(field))
            if value is None or value <= 0:
                context_issues.append({"interval_id": row["interval_id"], "field": field, "value": context.get(field)})
        if context.get("direction") not in ("UP", "DOWN"):
            context_issues.append({"interval_id": row["interval_id"], "field": "direction"})
        markers[(row["native_label"], "*" in context["Tool"])] += 1
        tools[context["Tool"]].add(row["group_id"])
    date_groups = collections.defaultdict(list)
    for f in files:
        if modality(f["name"]) == "mtc":
            machine, experiment, filename = f["name"].split("/")
            date_groups[(machine, filename.split("_")[0])].append(machine + "/" + experiment)
    date_rows = [{"machine": m, "filename_reference_date": day, "experiment_groups": len(gs),
                  "label_1_groups": sum(int(lookup[g]["label_1"]) > 0 for g in gs), "groups": ";".join(gs)}
                 for (m, day), gs in sorted(date_groups.items())]
    write_csv(run / "manifests/reference_date_groups.csv", date_rows)
    context_audit = {"context_issues": context_issues,
                     "tool_marker_counts": {f"label_{k[0]}/star_{k[1]}": v for k, v in markers.items()},
                     "groups_per_tool_id": {k: len(v) for k, v in tools.items()},
                     "date_grouping_is_proxy_not_verified_session_identity": True}
    write_new(run / "manifests/context_audit.json", json.dumps(context_audit, indent=2))

    pilot_files = []
    for f in files:
        group = "/".join(f["name"].split("/")[:2])
        mod = modality(f["name"])
        selected = group in PILOT and mod in ("label", "mtc", "ct", "audio_s0", "video", "nc")
        metadata = "/" not in f["name"] and mod in ("xml", "xlsx")
        if selected or metadata:
            cohort = "industrial_optional" if group.startswith("tmf_") else "lab_primary" if selected else "metadata"
            pilot_files.append({"name": f["name"], "bytes": f["bytes"], "modality": mod, "cohort": cohort,
                                "acquisition_status": "already_acquired" if mod == "label" else "proposed_only"})
    write_csv(run / "manifests/pilot_file_plan.csv", pilot_files)
    incremental = sum(f["bytes"] for f in pilot_files if f["acquisition_status"] != "already_acquired")
    primary = sum(f["bytes"] for f in pilot_files if f["cohort"] != "industrial_optional" and f["acquisition_status"] != "already_acquired")
    optional = incremental - primary
    optional_acc = sum(f["bytes"] for f in files if "/".join(f["name"].split("/")[:2]) in PILOT and modality(f["name"]) == "acc")
    pilot_table = table(["Experiment", "0 / 1 / 2", "Role", "Proposed new bytes"],
                        [[g, " / ".join(lookup[g][f"label_{k}"] for k in range(3)), purpose,
                          sum(f["bytes"] for f in pilot_files if f["name"].startswith(g + "/") and f["acquisition_status"] != "already_acquired")]
                         for g, purpose in PILOT.items()])
    write_new(run / "manifests/pilot_storage.json", json.dumps({"primary_lab_and_metadata_new_bytes": primary,
               "optional_industrial_new_bytes": optional, "combined_new_bytes": incremental,
               "optional_primary_accelerometer_bytes": optional_acc,
               "combined_plus_accelerometer_bytes": incremental + optional_acc,
               "pilot_files_are_not_downloaded_in_stage1": True}, indent=2))
    duration_table = table(["Machine / label", "n", "Min s", "Median s", "Max s", "Total s"],
                           [[k, v["n"], f"{v['min_s']:.3f}", f"{v['median_s']:.4f}", f"{v['max_s']:.3f}", f"{v['sum_s']:.3f}"]
                            for k, v in sorted(summary["durations_by_machine_and_class"].items())])
    group_table = table(["Experiment", "Intervals", "Label 0", "Label 1", "Label 2", "Invalid", "Warnings"],
                        [[g["group_id"], g["rows"], g["label_0"], g["label_1"], g["label_2"], g["invalid_rows"], g["warning_rows"]] for g in groups])
    write_new(run / "MSM_LABEL_AUDIT.md", f"""# MSM Stage 1 label audit

Audit date: {stamp.astimezone(ZoneInfo('Europe/Berlin')).isoformat()}. Dataset ID **8392825**, pinned handle **`{cfg['handle']}`**. Counts below come from all 69 actual downloaded `label.csv` files, not spreadsheet remarks. Source bytes and SHA-256 hashes are in `manifests/input_manifest.json`; every native row is preserved in `MSM_INTERVAL_MANIFEST.csv`.

## Native meanings and target interpretation

The [publication]({paper}) defines 0 as stable normal cutting, 1 as abnormal cutting warranting intervention, and 2 as a defective tool cutting stably. Abnormal cutting overrides the tool-defect category. The [Kaggle data card]({source}) abbreviates label 2 as tool defect; that abbreviation must not be used to combine labels 1 and 2 automatically.

The audit preserves all three native categories. A later intervention-detection target could compare 1 against {{0,2}}, with a separately declared 1-versus-0 sensitivity analysis. Neither mapping is approved for training here. Tool marks, label fields, remarks, and stop outcomes must not become unrestricted predictors.

## Counts and actual prediction units

{machine_table}

There are **2,575 native labeled intervals**, grouped into **69 experiments/operations**. Treat one interval as one candidate example before any windowing. A 1-versus-0-only cohort would contain 2,398 intervals; retaining all native classes gives 2,575. Sensor/video payloads were not acquired: **zero multimodal examples have yet passed pairing, timing, coverage, or signal-quality validation**. Window counts are therefore undefined and would not increase the number of independent experiment groups.

The laboratory subset has 2,512 intervals, including 458 label-1 intervals in 25 positive-containing folders, with video listed for every folder. The industrial subset has 63 intervals, including 7 label-1 intervals in 5 folders, and no listed videos. These units differ: laboratory labels typically describe short cutting passes; industrial annotations can segment longer machining paths. Interval-level and duration-weighted metrics would answer different questions.

## Integrity and publication consistency

All 69 files have the same 12-column header: `start,end,label,direction,N,ap,ae,F,Z,D,Tool,Workpiece`. All 2,575 rows have finite, nonnegative start times, strictly later end times, and labels in {{0,1,2}}. No annotation files, mandatory cells, context cells, overlapping intervals, out-of-order rows, duplicate rows within a file, or identical annotation-file hashes were found missing/invalid. There are **0 invalid rows and 0 annotation warning rows**. Blank lines are ignored by the CSV parser; original bytes are preserved.

All numeric context fields inspected (`N,ap,ae,F,Z,D`) are finite and positive; every direction is UP or DOWN. Context validation found {len(context_issues)} issues. Every one of the 177 label-2 rows has a starred tool ID, and all 1,933 label-0 rows have unstarred IDs. Of the label-1 rows, 59 have starred and 406 have unstarred tools. This agrees with the stated override rule; it does not independently verify experts' judgments. Without signals/media, timing accuracy and the physical cause of each anomaly remain unaudited. Interval duration is `end - start` in seconds, calculated using decimal arithmetic; no formulas or source values were corrected.

## Duration distributions

{duration_table}

Across all intervals: minimum 0.533 s, median 3.008 s, maximum 408.529 s; summed annotated cutting time 17,078.305 s (4.744 h). Duration summaries describe annotated cuts only, not complete recording lengths. Do not label gaps as normal. Industrial transitions share some endpoints; use a documented half-open interval policy if converting to windows, without rewriting annotations.

## Group-disjoint feasibility and dependence

**30 experiment folders contain label 1** (19 + 6 + 5). This establishes nominal group counts, not independence of physical trials. All three machines have labels 0 and 1. Both laboratory machines also have label 2; the industrial machine has none. There are 4 label-2-containing groups on each laboratory machine. `imi_vm20i` has the strongest abnormal-group support; `imi_vmx30ui` has only 6 positive groups, and `tmf_vf10` has only 7 positive intervals across 5 groups. Industrial estimates will be especially unstable.

Experiment-disjoint splitting is feasible in principle if every interval/window from a folder stays together and class coverage is checked. A provisional 3-fold grouped design is more plausible than many folds; it is a proposal, not a generated or validated split. Five-fold industrial evaluation would leave roughly one positive group per test fold and very few abnormal intervals. Three-class folds additionally need explicit label-2 support. Do not claim machine-held-out three-class coverage when holding out `tmf_vf10`.

Reference dates in MTConnect filenames reveal only **12 machine/date clusters**: 3 for `imi_vm20i`, 4 for `imi_vmx30ui`, and 5 for `tmf_vf10`; respectively 3, 4, and 4 contain positives. The two laboratory machines together span only 5 distinct calendar dates. These are filename-derived proxies, not verified session IDs. See `manifests/reference_date_groups.csv`. Shared dates, tool IDs, workpieces, repeated NC programs, and adjacent production cycles can create dependence across folders. IDs such as G1/G2 recur throughout industry data, but an ID alone does not establish physical-tool identity. Confirm chronology and physical tool/workpiece/session links before finalizing groups; use stronger groups when dependence is established. Sensor-level duplicates were not assessed.

Positive-containing experiments, in native folder numbering:

""" + "\n\n".join(f"- **{m}**: " + ", ".join(v["positive_groups"]) for m, v in by_machine.items()) + f"""

## Counts for every experiment

{group_table}

## Next bounded pilot

{pilot_table}

The five laboratory groups provide 121 intervals (95 label 0, 14 label 1, 12 label 2), including pure normal and stable defective-tool controls. The optional industrial group adds 6 intervals (5 label 0, 1 label 1). This is an ingestion/alignment pilot, not an evaluation cohort: only two laboratory positive groups are selected, and no performance claim or training is justified by the pilot alone.

The supplied script's original pilot list would emphasize abnormal experiments: `imi_vm20i/dataset5` actually has 5 label-1 intervals, while datasets 7 and 8 each have just one interval. The revised proposal adds explicit controls and retains a second-machine mixed experiment. Full experiment folders are unnecessary for the initial timing check; see the exact file plan and storage in `MSM_FILE_AVAILABILITY.md`.

Stage 1 stops here. The researcher must review the native-label target, stronger grouping needs, and video pairing evidence before authorizing Stage 2.
""")

    modality_counts, modality_bytes = collections.Counter(), collections.Counter()
    for f in files:
        mod = modality(f["name"])
        modality_counts[mod] += 1
        modality_bytes[mod] += f["bytes"]
    coverage = table(["Machine", "Experiments", "Labels", "MP4", "S0 / S1 / S2", "ACC", "MTC", "CT", "NC", "Bytes"],
                     [[m, by_machine[m]["experiments"], by_machine[m]["experiments"],
                       sum(f["name"].startswith(m + "/") and modality(f["name"]) == "video" for f in files),
                       " / ".join(str(sum(f["name"].startswith(m + "/") and modality(f["name"]) == "audio_s" + str(k) for f in files)) for k in range(3)),
                       *[sum(f["name"].startswith(m + "/") and modality(f["name"]) == mod for f in files) for mod in ("acc", "mtc", "ct", "nc")],
                       sum(f["bytes"] for f in files if f["name"].startswith(m + "/"))] for m in by_machine])
    file_table = table(["Modality / type", "Files", "Bytes"], [[k, modality_counts[k], modality_bytes[k]] for k in sorted(modality_counts)])
    availability_rows = []
    for g in groups:
        group_files = [f for f in files if f["name"].startswith(g["group_id"] + "/")]
        availability_rows.append([g["group_id"], len(group_files), g["modalities"], g["all_files_bytes"], "label.csv only"])
    availability_table = table(["Experiment", "Files", "Listed modalities", "Total bytes", "Locally acquired"], availability_rows)
    plan_table = table(["Proposed file (dataset relative)", "Bytes", "Cohort", "Status"],
                       [[f["name"], f["bytes"], f["cohort"], f["acquisition_status"]] for f in pilot_files])
    write_new(run / "MSM_FILE_AVAILABILITY.md", f"""# MSM Stage 1 file availability

Official source: [Kaggle dataset]({source}), dataset ID 8392825, **version 2**. The version-pinned public file-list API was paginated to completion (3 pages, 481 unique files), and the sum of listed sizes equals the official dataset total: **40,412,136,430 bytes** (40.412 GB; 37.637 GiB). No full archive was requested. `manifests/official_file_inventory.json` retains every remote path, byte size, and creation date; `manifests/file_inventory.csv` adds modality and local status. Listed size is not a cryptographic checksum or validation of payload readability.

## Verified hierarchy

The dataset root has `dataset_summary.xlsx` (11,784 bytes), `imi_vm20i.xml` (16,596), `imi_vmx30ui.xml` (13,831), and `tmf_vf10.xml` (4,859). Machine folders contain contiguous `dataset1` through `dataset37`, `dataset19`, and `dataset13`, respectively. Each experiment has one `label.csv`, one timestamped `*_mtc.csv`, and `*_s0.wav` plus `*_s2.wav`. Both lab machines have MP4 and NC files for every experiment. VM20i additionally has `*_acc.csv` and `*_s1.wav`; TMF has `*_ct.csv`. Extra PNG figures occur only in VM20i datasets 6 and 7.

{coverage}

{file_table}

## Missing versus intentionally unacquired

**No expected annotation files are missing**: 69/69 are local, totaling 173,594 bytes. The other **412 listed files are intentionally not downloaded**. The spreadsheet and XML files are listed but were not acquired during this annotation-only stage. Only the pasted downloader was supplied with this task; no local MSM summary workbook was located. The stated spreadsheet counts were independently checked against the complete hierarchy and actual labels.

All 13 industrial experiments lack listed MP4 and NC files. The publication explicitly withholds industrial NC programs; it describes videos for laboratory data. These are modality limitations, not failed downloads. Accelerometers are absent from the second lab and industry folders; S1 is VM20i-only. Every experiment has S0/S2 audio listed. No media or sensor file has been checked for decoding, completeness, sampling rate, missing values, or annotation coverage.

Video pairing remains a material gate. Filenames already differ from sensor reference timestamps: VM20i dataset1 video is approximately +2.213 s, VM20i dataset19 video approximately -75.487 s, and VMX30Ui dataset9 video approximately -143.523 s relative to its sensor filename reference, **if** the naming clocks and formats are comparable. These arithmetic differences are not calibrated offsets and cannot be applied to labels. Later inspection must establish video start, editing/compression effects, drift, coverage of each cutting interval, and useful visibility. Sensor synchronization described by the publication does not establish smartphone-video alignment.

Industrial CT CSVs total only 21,607 bytes across 13 recordings. Their small size makes schema and temporal-resolution inspection essential before treating them as an appropriate continuous sensor branch. MTConnect channel availability likewise requires payload inspection.

## Per-experiment availability

{availability_table}

## Exact proposed next-pilot files — not downloaded

{plan_table}

The primary five-laboratory-experiment plan uses one S0 audio channel, the MTC table, MP4, and NC program from each selected folder, plus the summary workbook and the two laboratory machine XML models for semantic/grouping context. Existing labels require no further transfer. The optional TMF diagnostic adds S0, MTC, CT, and the TMF XML model; it cannot provide a visual-sensor pair. Additional S1/S2 audio channels and high-volume accelerometers can wait until synchronization and branch choice are established. This selection is for inspection, not a claim that MTC has the needed channels or rates.

- Primary laboratory plan plus metadata: **{primary:,} new bytes** ({primary / 1e6:.3f} MB; {primary / 1024**2:.3f} MiB).
- Optional industrial diagnostic: **{optional:,} new bytes** ({optional / 1e6:.3f} MB).
- Combined proposed transfer: **{incremental:,} new bytes** ({incremental / 1e6:.3f} MB; {incremental / 1024**2:.3f} MiB).
- Optional VM20i accelerometer files for the three selected VM20i folders add **{optional_acc:,} bytes**; combined plan with these becomes **{incremental + optional_acc:,} bytes** ({(incremental + optional_acc) / 1024**3:.3f} GiB).

These are sums of official per-file sizes for direct selective downloads, not compressed-transfer estimates. Budget at least 1 GiB free for the base inspection plan (2 GiB if adding ACC), plus separate space for any later derived frames/features. Do not pre-extract video frames. The machine-readable file plan is `manifests/pilot_file_plan.csv`; storage totals are in `manifests/pilot_storage.json`. Researcher review must precede all pilot media downloads.
""")

    free = shutil.disk_usage(run).free
    versions = {}
    for name in ("pip", "pytest", "pandas", "requests", "kagglehub", "kaggle"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not installed"
    provenance = {"created_utc": stamp.isoformat(), "created_berlin": stamp.astimezone(ZoneInfo('Europe/Berlin')).isoformat(),
                  "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                  "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
                  "python": platform.python_version(), "packages": versions, "free_bytes_after": free,
                  "config": str(run / "config/resolved_config.json"),
                  "source_identity": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('MILLING DATASET/source').glob('*.py'))},
                  "methodology": "native-interval-audit-v1; no label remapping; Decimal durations; experiment-folder groups provisional",
                  "training_performed": False, "media_downloaded": False,
                  "warnings": ["Physical independence of experiment folders unverified", "Video alignment and coverage unverified",
                               "Only 7 industrial positive intervals", "Pre-existing dirty worktree preserved"]}
    write_new(run / "provenance.json", json.dumps(provenance, indent=2))
    write_new(run / "MSM_STAGE1_ACQUISITION_REPORT.md", f"""# MSM Stage 1 acquisition report

**Status: annotation acquisition and native-label audit complete; review required before Stage 2.** No neural network was trained, no full video/audio/sensor payload was downloaded, and no complete-dataset archive was requested.

Dataset: **`{cfg['handle']}`**. Official dataset ID **8392825**. Audit date: {stamp.astimezone(ZoneInfo('Europe/Berlin')).isoformat()}.

## Official identity and version provenance

The [dataset DOI](https://doi.org/10.34740/kaggle/ds/8392825) resolves to the [official Kaggle page]({source}). The official public metadata endpoint returns `id=8392825`, `ref=manufuturetoday/multi-sensor-for-metal-milling-anomaly`, and `currentVersionNumber=2`. DataCite independently links the DOI to Kaggle dataset ID 8392825. Version **2**, created **2026-03-13T20:01:40.34Z**, was Ready and current at access. Its release note says the summary workbook corrected the machine name `imi_vm30i` to `imi_vmx30ui`, with no changes to raw sensor data. Every file-list and label request supplied `datasetVersionNumber=2`; an unversioned latest download was not used. Dataset license reported by Kaggle: CC BY 4.0.

The authoritative [data descriptor]({paper}) was retrieved from the publisher and inspected for native-label rules, interval interpretation, sensor synchronization, and laboratory video acquisition. Public access worked without reading credentials, local auth configuration, cookies, or session files. A failed unencoded nested-path request (404) was resolved using Kaggle's supported single-file query (`fileName` plus `datasetVersionNumber`); no access restriction was bypassed. Signed download redirect URLs were neither recorded nor exposed.

Evidence is under `evidence/`: public Kaggle metadata, DataCite metadata, source-access records, and an exact-byte copy of the supplied downloader. Publisher and landing-page HTML snapshots are local ignored evidence. The official inventory contains 481 unique entries and its 40,412,136,430-byte sum matches the official dataset total.

## Repository, persistent data, and preservation

The repository was already dirty at revision `{provenance['git_commit']}`. Existing modified README/REPO_MAP/thesis evidence files and pre-existing untracked experiment/maintenance work were preserved. The initial status snapshot is `evidence/git_status_before.txt`. Repository/filename searches found no existing MSM dataset, annotation audit, or downloader; prior literature notes contained conceptual MSM discussion only. Protected PHM, Intel, REASSEMBLE, and historical experiment contents were not changed or scanned for payloads.

Per researcher instruction, all new work is contained in **`MILLING DATASET/`**. Persistent raw annotations are in **`{cfg['data_root']}`**. Versioned outputs are in **`{run}`**. The folder-local `.gitignore` excludes the entire `data/` subtree, including future media, NC/XML, receipts, and spreadsheets; raw inputs must never be committed. Small derived audit CSV files are narrowly allow-listed, while local source HTML and logs remain ignored. Nothing was staged or committed.

Preflight `df -h` reported 77G free (the downloader measured 76.6 GiB, approximately 82.2 decimal GB); free space at report generation was {free / 1024**3:.3f} GiB. Public DOI, publisher, DataCite, Kaggle metadata, file-list, and single-label endpoints were reachable. The default shell sandbox could not initialize its network namespace; approved execution outside that broken sandbox allowed the checks. KaggleHub and Kaggle CLI were absent. No dependencies were installed and no authentication blocker occurred.

## Selective acquisition and focused downloader changes

The supplied downloader's 69 paths exactly match the official version-2 hierarchy: 37 VM20i, 19 VMX30Ui, 13 VF10 experiments, with no numbering gaps. The preview verified **173,594 selected bytes**, then the selective run acquired **69 label files, 0 failures**. Their sizes match the pinned official inventory. Input SHA-256 values and the acquisition receipt provide local content identities; Kaggle's listing does not expose an official checksum, so do not describe size checks as independent cryptographic verification. Existing verified labels are skipped; mismatching existing paths are preserved for audit.

`source/download_msm.py` retains the supplied selection logic and adds an optional standard-library `public-api` backend restricted to small `label.csv` files. It requires a pinned handle and matching dataset-ID inventory, validates path membership, limits response bytes, validates CSV headers before exclusive file creation, and stops on HTTP 401/403. It also records hashes and preserves existing mismatches/zero-length paths. The original KaggleHub backend remains available for future reviewed use; it was not executed. No formula, native label, or experimental selection was silently corrected. Compare `evidence/download_msm.supplied.py` against the current source for the exact focused diff.

Commands, run from repository root:

```bash
ma_thesis_env/bin/python -B 'MILLING DATASET/source/inspect_official.py' --run '{run}'

# Preview first; --backend and --inventory are the documented local additions.
ma_thesis_env/bin/python -B 'MILLING DATASET/source/download_msm.py' \\
  --handle {cfg['handle']} \\
  --dest '{cfg['data_root']}' --mode labels --backend public-api \\
  --inventory '{run}/manifests/official_file_inventory.json'

# Selective annotation download, after the successful preview.
# Repeat the preceding command with --run.

ma_thesis_env/bin/python -B 'MILLING DATASET/source/audit_annotations.py' --run '{run}'
ma_thesis_env/bin/python -B 'MILLING DATASET/source/build_reports.py' --run '{run}'
```

Use a fresh versioned output directory for a new audit; table/report writers refuse existing targets. The command ledger and final verification record are in `manifests/commands.json` and `validation.json`. The receipt is preserved in raw storage and copied to `evidence/download_receipt.json` for review. Software versions, config, Git identity, dirty status, and source hashes are in `provenance.json`; input/output identities are under `manifests/`.

## Acquisition result and initial feasibility

{machine_table}

There are **2,575 candidate interval examples**, including **465 label-1 intervals in 30 nominal experiment groups**. The two laboratory machines support all native classes; industry supports labels 0/1 only and has limited positives. Label meanings and starred-tool behavior agree with the publication. Labels alone support a provisional experiment-disjoint design, but do not establish independence of physical tools/sessions. All 56 laboratory experiments have listed video and sound; 13 industrial groups have sound and CT/MTC but no video. No paired multimodal example is validated yet.

Missing expected annotation files: **none**. Other 412 files: intentionally unacquired. Publication/label consistency, every-experiment counts, intervals, duration distributions, and grouping limitations are documented in `MSM_LABEL_AUDIT.md`. Exact hierarchy, missing modalities, per-file sizes, and next-pilot filenames are in `MSM_FILE_AVAILABILITY.md`.

## Proposed next action — wait for researcher review

Review the five laboratory groups **VM20i datasets 1, 4, 19; VMX30Ui datasets 9, 8**, plus optional **VF10 dataset1** for an industrial diagnostic. Obtain only the exact file plan in `manifests/pilot_file_plan.csv`, after approval. The primary laboratory plan plus metadata needs **{primary:,} bytes**; the industrial option adds **{optional:,} bytes**, for **{incremental:,} bytes** total ({incremental / 1e6:.3f} MB). Optional ACC increases that total to **{incremental + optional_acc:,} bytes**. No proposed pilot files were downloaded here.

Stage 2 should first inspect schemas and video/audio/sensor clocks, validate interval coverage and visual usefulness, reconcile physical tool/workpiece/session identities, and predeclare labels/grouping before any model fitting. This Stage 1 task grants no neural-network training authorization.

## Deliverables

- `MSM_STAGE1_ACQUISITION_REPORT.md` — this report.
- `MSM_LABEL_AUDIT.md` — native-label, duration, integrity, feasibility, and per-experiment audit.
- `MSM_INTERVAL_MANIFEST.csv` — all 2,575 rows with native labels, source row/hash, machine, experiment, time boundaries, duration, and unmodified context.
- `MSM_FILE_AVAILABILITY.md` — verified hierarchy, per-experiment modalities, and exact proposed pilot file/storage plan.

All four reside in `{run}`. Preserve downloaded files and wait for researcher review before Stage 2.
""")
    print(json.dumps({"reports": str(run), "primary_pilot_bytes": primary, "optional_industry_bytes": optional,
                      "combined_pilot_bytes": incremental, "optional_acc_bytes": optional_acc}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    main(parser.parse_args().run)
