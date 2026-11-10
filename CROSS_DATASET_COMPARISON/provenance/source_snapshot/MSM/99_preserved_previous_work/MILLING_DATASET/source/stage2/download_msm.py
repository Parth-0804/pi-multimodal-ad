#!/usr/bin/env python3
"""Stage 2 extension of the verified Stage 1 downloader: exact pilot files only."""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

spec = importlib.util.spec_from_file_location("stage1_downloader", Path(__file__).parents[1] / "download_msm.py")
stage1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage1)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_plan(config, inventory, dest):
    if config["handle"] != inventory["handle"] or inventory["dataset_id"] != 8392825:
        raise ValueError("Dataset identity mismatch")
    stage1.valid_handle(config["handle"])
    if "/versions/2" not in config["handle"]:
        raise ValueError("Stage 2 is pinned to the verified version 2")
    official = {f["name"]: f["bytes"] for f in inventory["files"]}
    known = {}
    for receipt in dest.glob("_msm_download_receipt_*.json"):
        data = json.loads(receipt.read_text())
        if data.get("handle") == config["handle"]:
            known.update({r["path"]: r["sha256"] for r in data["results"] if r.get("sha256")})
    rows = []
    for entry in config["download_plan"]:
        name = stage1.valid_dataset_path(entry["name"])
        if name not in official or official[name] != int(entry["bytes"]):
            raise ValueError("Planned file/size differs from pinned official inventory")
        path = dest / name
        path.resolve().relative_to(dest.resolve())
        status, digest = "missing", None
        if path.exists():
            if path.is_symlink() or not path.is_file() or path.stat().st_size != official[name]:
                raise ValueError("Existing path needs audit; preserved: " + name)
            digest = sha256(path)
            if name not in known or known[name] != digest:
                raise ValueError("Existing file has no matching acquisition hash; preserved: " + name)
            status = "verified_existing"
        rows.append({"path": name, "bytes": official[name], "status": status, "sha256": digest})
    if len({r["path"] for r in rows}) != len(rows):
        raise ValueError("Repeated pilot target")
    if sum(r["bytes"] for r in rows if r["status"] == "missing") > config["max_download_bytes"]:
        raise ValueError("Pilot transfer exceeds configured budget")
    return rows


def transfer(handle, row, dest, staging):
    owner_slug, version = handle.split("/versions/")
    query = urllib.parse.urlencode({"datasetVersionNumber": version, "fileName": row["path"]})
    url = "https://www.kaggle.com/api/v1/datasets/download/" + owner_slug + "?" + query
    staging_path = staging / row["path"]
    staging_path.parent.mkdir(parents=True, exist_ok=True)
    digest, count = hashlib.sha256(), 0
    with urllib.request.urlopen(url, timeout=90) as response, staging_path.open("xb") as output:
        while chunk := response.read(min(1024 * 1024, row["bytes"] - count + 1)):
            count += len(chunk)
            if count > row["bytes"]:
                raise ValueError("Response exceeds official file size")
            output.write(chunk)
            digest.update(chunk)
        output.flush()
        os.fsync(output.fileno())
    if count != row["bytes"]:
        raise ValueError("Incomplete download; staged bytes preserved")
    target = dest / row["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    # Atomic exclusive publication of fully verified bytes; neither link is ever rewritten.
    os.link(staging_path, target)
    return {**row, "status": "downloaded", "sha256": digest.hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handle", type=stage1.valid_handle, required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--mode", choices=["pilot"], required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if args.handle != config["handle"] or args.dest != Path(config["data_root"]):
        parser.error("CLI handle/destination differs from reviewed config")
    run = Path(config["run_root"])
    inventory = json.loads((run / "manifests/official_file_inventory.json").read_text())
    rows = audit_plan(config, inventory, args.dest)
    new_bytes = sum(r["bytes"] for r in rows if r["status"] == "missing")
    free = shutil.disk_usage(args.dest).free
    if free < new_bytes + config["free_space_reserve_gib"] * 1024**3:
        parser.error("Insufficient free space for selected files plus reserve")
    print(json.dumps({"handle": args.handle, "groups": config["selected_groups"], "files": len(rows),
                      "existing_verified": sum(r["status"] == "verified_existing" for r in rows),
                      "new_bytes": new_bytes, "free_bytes": free, "run": args.run}, indent=2), flush=True)
    for row in rows:
        print(row["status"], row["bytes"], row["path"], flush=True)
    if not args.run:
        print("PREVIEW ONLY: no raw-data writes or network requests.")
        return 0
    report = {"handle": args.handle, "mode": "stage2_exact_pilot", "destination": str(args.dest),
              "started_utc": datetime.now(timezone.utc).isoformat(), "results": [], "failures": 0}
    for row in rows:
        try:
            result = row if row["status"] == "verified_existing" else transfer(args.handle, row, args.dest, run / "staging")
            report["results"].append(result)
            print(result["status"], result["path"], flush=True)
        except Exception as exc:
            report["failures"] += 1
            report["results"].append({"path": row["path"], "status": "failed", "error_type": type(exc).__name__,
                                      "http_status": exc.code if isinstance(exc, urllib.error.HTTPError) else None})
            print("STOPPED", type(exc).__name__, "raw and staged files preserved", flush=True)
            break
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    receipt = args.dest / ("_msm_download_receipt_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    with receipt.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    with (run / "evidence" / receipt.name).open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print("Receipt", receipt, "failures", report["failures"], flush=True)
    return int(bool(report["failures"]))


if __name__ == "__main__":
    raise SystemExit(main())
