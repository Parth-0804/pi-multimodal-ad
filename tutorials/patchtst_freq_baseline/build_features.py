#!/usr/bin/env python3
"""Phase 2: build one 72-dim spectral feature row per HF minute-member,
for every member in every one of the 20 pinned-split runs.

Processes ONE member at a time (materialize -> featurize -> delete);
never holds a full run's raw waveform in memory. Writes each run's
features to disk as soon as that run finishes (incremental, not buffered
across runs). Checks free disk space before starting and before each run.
Read-only against gtc-data-experiment/; never writes there.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import extract_member_features  # noqa: E402
from reader import (  # noqa: E402
    discover_hf_run_archives,
    free_disk_bytes,
    list_hdf5_members,
    materialize_member,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT_DEFAULT = REPO_ROOT / "gtc-data-experiment"
OUTPUT_DIR_DEFAULT = Path(__file__).resolve().parent / "features"
MAX_MEMBER_BYTES = 600 * 1024 * 1024  # largest known direct HF member ~527MiB (Phase 0/D1.2)
MINIMUM_FREE_BYTES = 20 * 1024 * 1024 * 1024  # 20 GiB safety gate


def process_run(
    experiment: str,
    run: int,
    archive_path: Path,
    output_dir: Path,
    log_handle,
    *,
    limit_members: int | None = None,
) -> dict:
    members = list_hdf5_members(archive_path)
    if limit_members is not None:
        members = members[:limit_members]
    rows: list[dict] = []
    excluded: list[dict] = []
    started = time.perf_counter()
    for member_name in members:
        with materialize_member(
            archive_path, member_name, max_member_bytes=MAX_MEMBER_BYTES
        ) as local_path:
            result = extract_member_features(local_path)
        record = {
            "experiment": experiment,
            "run": run,
            "member_name": member_name,
        }
        log_handle.write(
            json.dumps(
                {
                    **record,
                    "wf_start_time": (
                        result.wf_start_time.isoformat()
                        if result.wf_start_time
                        else None
                    ),
                    "duration_seconds": result.duration_seconds,
                    "sample_count": result.sample_count,
                    "sample_rate_hz": result.sample_rate_hz,
                    "channel_errors": result.channel_errors,
                    "exclusion_reason": result.exclusion_reason,
                }
            )
            + "\n"
        )
        if result.feature_row is None:
            excluded.append({**record, "reason": result.exclusion_reason})
            continue
        rows.append(
            {
                **record,
                "wf_start_time": result.wf_start_time.isoformat(),
                **result.feature_row,
            }
        )
    elapsed = time.perf_counter() - started

    run_frame = pd.DataFrame(rows)
    if not run_frame.empty:
        run_frame = run_frame.sort_values("wf_start_time", kind="stable").reset_index(
            drop=True
        )
    out_path = output_dir / "per_run" / f"{experiment}_run{run}.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run_frame.to_parquet(out_path, index=False)

    return {
        "experiment": experiment,
        "run": run,
        "archive": str(archive_path),
        "member_count": len(members),
        "included_count": len(rows),
        "excluded_count": len(excluded),
        "excluded_reasons": excluded,
        "elapsed_seconds": elapsed,
        "output_path": str(out_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, default=RAW_ROOT_DEFAULT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR_DEFAULT)
    parser.add_argument(
        "--limit-members-per-run",
        type=int,
        default=None,
        help="For a quick smoke test only: cap members processed per run.",
    )
    args = parser.parse_args(argv)

    if not args.raw_root.is_dir():
        print(f"Raw data root not found: {args.raw_root}", file=sys.stderr)
        return 1

    free_start = free_disk_bytes(args.raw_root)
    print(f"Free disk at start: {free_start / 1e9:.1f} GB")
    if free_start < MINIMUM_FREE_BYTES:
        print("Free disk below the 20 GiB safety gate; aborting.", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_archives = discover_hf_run_archives(args.raw_root)
    print(f"Discovered {len(run_archives)} HF run archives.")

    log_path = args.output_dir / "build_log.jsonl"
    summary_path = args.output_dir / "run_summary.json"
    summaries = []
    overall_started = time.perf_counter()
    with log_path.open("w", encoding="utf-8") as log_handle:
        for index, run_archive in enumerate(run_archives, start=1):
            free_now = free_disk_bytes(args.raw_root)
            if free_now < MINIMUM_FREE_BYTES:
                print(
                    f"Free disk dropped below 20 GiB before {run_archive.experiment} "
                    f"run {run_archive.run}; stopping early.",
                    file=sys.stderr,
                )
                break
            print(
                f"[{index}/{len(run_archives)}] {run_archive.experiment} run "
                f"{run_archive.run} ({run_archive.archive_path.name}) - "
                f"free disk {free_now / 1e9:.1f} GB"
            )
            summary = process_run(
                run_archive.experiment,
                run_archive.run,
                run_archive.archive_path,
                args.output_dir,
                log_handle,
                limit_members=args.limit_members_per_run,
            )
            summaries.append(summary)
            log_handle.flush()
            print(
                f"    -> included={summary['included_count']} "
                f"excluded={summary['excluded_count']} "
                f"elapsed={summary['elapsed_seconds']:.1f}s"
            )
            summary_path.write_text(
                json.dumps(summaries, indent=2, default=str), encoding="utf-8"
            )

    overall_elapsed = time.perf_counter() - overall_started
    total_included = sum(s["included_count"] for s in summaries)
    total_excluded = sum(s["excluded_count"] for s in summaries)
    total_members = sum(s["member_count"] for s in summaries)
    print(
        f"\nDone. {len(summaries)} runs processed, {total_members} members seen, "
        f"{total_included} included, {total_excluded} excluded, "
        f"{overall_elapsed:.1f}s total ({overall_elapsed/60:.1f} min)."
    )
    print(f"Free disk at end: {free_disk_bytes(args.raw_root) / 1e9:.1f} GB")
    summary_path.write_text(json.dumps(summaries, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
