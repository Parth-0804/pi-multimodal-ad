#!/usr/bin/env python3
"""Safely acquire selected files from the official MSM Kaggle dataset.

Preview-only by default. KaggleHub >= 1.0.3 is needed for its folder backend.
The Stage 1 public-api backend uses only the standard library, a verified
inventory, and a pinned version, and permits small label.csv files only.
The dataset handle must be taken from the canonical Kaggle page for dataset
DOI 10.34740/kaggle/ds/8392825; it is intentionally not guessed here.

Examples:
    python download_msm.py --handle OWNER/SLUG --dest data/raw/msm --mode labels
    python download_msm.py --handle OWNER/SLUG --dest data/raw/msm --mode labels --run
    python download_msm.py --handle OWNER/SLUG --dest data/raw/msm --mode pilot --run
    python download_msm.py --handle OWNER/SLUG --dest data/raw/msm --mode path \
        --item imi_vm20i/dataset7/label.csv --run
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


# Experiment-folder counts were read from the supplied dataset_summary.xlsx.
# The live dataset manifest must still be checked before interpreting failures.
EXPERIMENT_COUNTS = {
    "imi_vm20i": 37,
    "imi_vmx30ui": 19,
    "tmf_vf10": 13,
}

PILOT_FOLDERS = [
    "imi_vm20i/dataset1",     # Tool marked defective in dataset summary
    "imi_vm20i/dataset5",     # No special remark; label unknown
    "imi_vm20i/dataset7",     # Clamp failure remark
    "imi_vm20i/dataset8",     # Excessive vibration remark
    "imi_vmx30ui/dataset9",   # Excessive vibration, second lab machine
    "tmf_vf10/dataset1",      # Industrial blown-insert remark
]


def valid_handle(value: str) -> str:
    pattern = r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/versions/[0-9]+)?$"
    if not re.fullmatch(pattern, value):
        raise argparse.ArgumentTypeError(
            "Use the verified Kaggle handle OWNER/DATASET or "
            "OWNER/DATASET/versions/N, not a DOI or URL."
        )
    return value


def valid_dataset_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or "\\" in value or any(
        part in ("", ".", "..") for part in value.split("/")
    ):
        raise argparse.ArgumentTypeError("Dataset path must be safe and relative")
    return str(path)


def get_targets(mode: str, item: str | None) -> list[str | None]:
    if mode == "labels":
        return [
            f"{machine}/dataset{i}/label.csv"
            for machine, count in EXPERIMENT_COUNTS.items()
            for i in range(1, count + 1)
        ]
    if mode == "pilot":
        return list(PILOT_FOLDERS)
    if mode == "path":
        if item is None:
            raise ValueError("--item is required for --mode path")
        return [valid_dataset_path(item)]
    if mode == "full":
        return [None]
    raise ValueError(f"Unknown mode: {mode}")


def check_kagglehub_version() -> object:
    try:
        raw_version = importlib.metadata.version("kagglehub")
    except importlib.metadata.PackageNotFoundError as exc:
        raise RuntimeError(
            "kagglehub is not installed. In the target environment, install "
            "a permitted version >= 1.0.3 and rerun."
        ) from exc
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", raw_version)
    if not match or tuple(map(int, match.groups())) < (1, 0, 3):
        raise RuntimeError(
            f"kagglehub {raw_version} detected; use >= 1.0.3 for folder mode."
        )
    import kagglehub

    return kagglehub


def count_local_files(path: Path) -> tuple[int, int]:
    if path.is_file():
        return 1, path.stat().st_size
    if path.is_dir():
        files = [p for p in path.rglob("*") if p.is_file()]
        return len(files), sum(p.stat().st_size for p in files)
    return 0, 0


def public_label_bytes(handle: str, relative_path: str, expected_bytes: int) -> bytes:
    """Use Kaggle's public, pinned single-file API without loading credentials."""
    owner_slug, version = handle.split("/versions/")
    if not relative_path.endswith("/label.csv") or not 0 < expected_bytes <= 2_000_000:
        raise ValueError("Public backend is limited to small label.csv files")
    query = urllib.parse.urlencode({"datasetVersionNumber": version, "fileName": relative_path})
    url = "https://www.kaggle.com/api/v1/datasets/download/" + owner_slug + "?" + query
    with urllib.request.urlopen(url, timeout=45) as response:
        body = response.read(expected_bytes + 1)
    if len(body) != expected_bytes:
        raise ValueError("Response size differs from official inventory")
    reader = csv.DictReader(io.StringIO(body.decode("utf-8-sig")))
    if not {"start", "end", "label"}.issubset(reader.fieldnames or []):
        raise ValueError("Response is not the expected annotation CSV")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handle", type=valid_handle, required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument(
        "--mode", choices=("labels", "pilot", "path", "full"), default="labels"
    )
    parser.add_argument("--item", help="Dataset-relative file/folder for --mode path")
    parser.add_argument("--run", action="store_true", help="Actually download; otherwise preview")
    parser.add_argument("--backend", choices=("kagglehub", "public-api"), default="kagglehub")
    parser.add_argument("--inventory", type=Path, help="Verified version-pinned official file inventory")
    parser.add_argument(
        "--confirm-full", action="store_true",
        help="Required with --mode full --run, which may transfer a very large dataset",
    )
    parser.add_argument(
        "--min-free-gb", type=float, default=None,
        help="Minimum free disk GB to require before each transfer",
    )
    args = parser.parse_args()

    if args.mode != "path" and args.item is not None:
        parser.error("--item is only for --mode path")
    try:
        targets = get_targets(args.mode, args.item)
    except ValueError as exc:
        parser.error(str(exc))
    inventory = None
    if args.inventory:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        if inventory["handle"] != args.handle or inventory["dataset_id"] != 8392825:
            parser.error("Inventory handle or dataset ID mismatch")
        inventory = {entry["name"]: entry["bytes"] for entry in inventory["files"]}
        missing = [target for target in targets if target not in inventory]
        if missing:
            parser.error(f"Selected paths absent from official inventory: {missing}")
    if args.backend == "public-api" and (
        args.mode != "labels" or inventory is None or "/versions/" not in args.handle
    ):
        parser.error("Public backend requires --mode labels, a pinned handle, and --inventory")
    dest = args.dest.expanduser().resolve()
    print(f"MSM dataset handle: {args.handle}")
    print(f"Destination: {dest}")
    print(f"Mode: {args.mode}; selected entries: {len(targets)}")
    print("The handle must refer to Kaggle dataset ID 8392825; verify it first.")
    if inventory is not None:
        print(f"Verified selected bytes: {sum(inventory[target] for target in targets)}")
    for target in targets[:10]:
        print(f"  {target or '[entire dataset]'}")
    if len(targets) > 10:
        print(f"  ... plus {len(targets) - 10} entries")
    if not args.run:
        print("PREVIEW ONLY. Pass --run after checking the handle and storage.")
        return 0

    if args.mode == "full" and not args.confirm_full:
        parser.error("Full download requires --confirm-full as well as --run")
    if args.mode == "full" and dest.exists() and any(dest.iterdir()):
        parser.error("Full download requires a new/empty destination directory")
    kagglehub = check_kagglehub_version() if args.backend == "kagglehub" else None
    dest.mkdir(parents=True, exist_ok=True)
    minimum_free_gb = (
        args.min_free_gb
        if args.min_free_gb is not None
        else (1.0 if args.mode == "labels" else 10.0)
    )
    if minimum_free_gb < 0:
        parser.error("--min-free-gb must be nonnegative")

    report = {
        "dataset_doi": "10.34740/kaggle/ds/8392825",
        "handle": args.handle,
        "mode": args.mode,
        "destination": str(args.dest),
        "backend": args.backend,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "results": [],
    }
    failures = 0
    for index, relative_path in enumerate(targets, 1):
        label = relative_path or "[entire dataset]"
        target_path = dest / relative_path if relative_path else dest
        if relative_path and target_path.exists() and (
            target_path.is_symlink() or (inventory is not None and (
                not target_path.is_file() or target_path.stat().st_size != inventory[relative_path]
            ))
        ):
            print(f"[{index}/{len(targets)}] Existing path fails verification; preserved: {label}")
            report["results"].append({"path": label, "status": "existing_path_needs_audit"})
            failures += 1
            continue
        if relative_path and target_path.is_file() and target_path.stat().st_size > 0:
            print(f"[{index}/{len(targets)}] Existing file, skipped: {label}")
            report["results"].append({"path": label, "status": "existing_file", "bytes": target_path.stat().st_size,
                                      "sha256": hashlib.sha256(target_path.read_bytes()).hexdigest()})
            continue
        if relative_path and target_path.is_dir():
            print(f"[{index}/{len(targets)}] Existing directory requires audit: {label}")
            report["results"].append({"path": label, "status": "existing_directory_needs_audit"})
            failures += 1
            continue
        free_gb = shutil.disk_usage(dest).free / (1024**3)
        if free_gb < minimum_free_gb:
            print(f"Insufficient free space ({free_gb:.1f} GB), stopping safely.")
            report["results"].append({"path": label, "status": "insufficient_free_space"})
            failures += 1
            break
        print(f"[{index}/{len(targets)}] Downloading {label} (free {free_gb:.1f} GB)")
        try:
            if args.backend == "public-api":
                target_path.resolve().relative_to(dest)
                body = public_label_bytes(args.handle, relative_path, inventory[relative_path])
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with target_path.open("xb") as stream:
                    stream.write(body)
                report["results"].append({"path": label, "status": "downloaded", "files": 1,
                                          "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
                continue
            resolved = Path(
                kagglehub.dataset_download(
                    args.handle,
                    path=relative_path,
                    output_dir=str(dest),
                    force_download=False,
                )
            ).resolve()
            resolved.relative_to(dest)
            count, total_bytes = count_local_files(resolved)
            if count == 0:
                raise RuntimeError("No downloaded files found at returned path")
            report["results"].append(
                {"path": label, "status": "downloaded", "files": count, "bytes": total_bytes}
            )
        except urllib.error.HTTPError as exc:
            failures += 1
            report["results"].append({"path": label, "status": "failed", "http_status": exc.code})
            print(f"  FAILED: HTTP {exc.code}", file=sys.stderr)
            if exc.code in (401, 403):
                print("Authentication/permission required; stopping without retries.", file=sys.stderr)
                break
        except Exception as exc:
            failures += 1
            report["results"].append(
                {"path": label, "status": "failed", "error_type": type(exc).__name__}
            )
            print(f"  FAILED: {type(exc).__name__}", file=sys.stderr)

    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["failures"] = failures
    receipt = dest / (
        "_msm_download_receipt_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json"
    )
    receipt.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Receipt: {receipt}")
    print(f"Failed or needing audit: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
