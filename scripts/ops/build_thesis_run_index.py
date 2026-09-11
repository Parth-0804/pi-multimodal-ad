#!/usr/bin/env python3
"""Build a sequential, thesis-citable index of every versioned run.

Reads `provenance.json` from every run directory, orders them chronologically,
and writes a Markdown index. Optionally relocates superseded runs into an
archive root.

Archiving refuses to move any run that is still pinned as a `source_runs`
dependency by a config, because `load_pinned_run` resolves those by directory
path and would break.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class RunRecord:
    directory: Path
    relative_directory: str
    run_id: str
    study: str
    timestamp_utc: str
    command: tuple[str, ...]
    git_commit: str | None
    git_dirty: bool | None
    git_untracked_present: bool | None
    schema_version: str
    config_path: str
    config_sha256: str
    seed: int | None
    artifact_count: int
    source_run_ids: tuple[str, ...]
    report_files: tuple[str, ...]


def load_runs(runs_root: Path) -> list[RunRecord]:
    records: list[RunRecord] = []
    for provenance_path in sorted(runs_root.glob("*/*/provenance.json")):
        try:
            payload = json.loads(provenance_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"skipping unreadable provenance {provenance_path}: {exc}")
            continue
        directory = provenance_path.parent
        git = payload.get("git") or {}
        config = payload.get("config") or {}
        sources = payload.get("source_runs") or []
        source_ids = []
        for source in sources:
            run_id = source.get("source_run_id")
            if isinstance(run_id, str) and run_id not in source_ids:
                source_ids.append(run_id)
        reports = sorted(
            path.name
            for path in (directory / "reports").glob("*")
            if path.is_file() and path.suffix in {".md", ".json"}
        )
        records.append(
            RunRecord(
                directory=directory,
                relative_directory=directory.relative_to(
                    REPOSITORY_ROOT
                ).as_posix(),
                run_id=str(payload.get("run_id", directory.name)),
                study=str(payload.get("study", directory.parent.name)),
                timestamp_utc=str(payload.get("timestamp_utc", "")),
                command=tuple(payload.get("command") or ()),
                git_commit=git.get("commit"),
                git_dirty=git.get("dirty"),
                git_untracked_present=git.get("untracked_present"),
                schema_version=str(payload.get("schema_version", "")),
                config_path=str(config.get("path", "")),
                config_sha256=str(config.get("sha256", "")),
                seed=payload.get("seed"),
                artifact_count=len(payload.get("produced_artifacts") or ()),
                source_run_ids=tuple(source_ids),
                report_files=tuple(reports),
            )
        )
    records.sort(key=lambda record: (record.timestamp_utc, record.run_id))
    return records


def pinned_directories(configs_root: Path) -> dict[str, str]:
    """Map every config-pinned run directory to the config that pins it."""

    pinned: dict[str, str] = {}
    for config_path in sorted(configs_root.rglob("*.yaml")):
        try:
            data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(data, dict):
            continue
        sources = data.get("source_runs")
        if not isinstance(sources, dict):
            continue
        relative_config = config_path.relative_to(REPOSITORY_ROOT).as_posix()
        for spec in sources.values():
            if isinstance(spec, dict) and isinstance(spec.get("directory"), str):
                pinned.setdefault(spec["directory"], relative_config)
    return pinned


def render_index(
    records: list[RunRecord],
    *,
    canonical: set[str],
    pinned: dict[str, str],
) -> str:
    consumers: dict[str, list[str]] = defaultdict(list)
    for record in records:
        for source_id in record.source_run_ids:
            consumers[source_id].append(record.run_id)

    # Provenance before schema 1.1.0 collapsed "modified tracked file" and
    # "untracked file present" into one flag. Every run writes a new untracked
    # output directory, so that flag reads true after almost any run and cannot
    # be read as evidence that the code was uncommitted.
    ambiguous = [
        record
        for record in records
        if record.git_dirty and record.git_untracked_present is None
    ]
    dirty = [
        record
        for record in records
        if record.git_dirty and record.git_untracked_present is not None
    ]
    by_study: dict[str, list[RunRecord]] = defaultdict(list)
    for record in records:
        by_study[record.study].append(record)

    lines: list[str] = [
        "# Thesis run index",
        "",
        "Generated by `scripts/ops/build_thesis_run_index.py` from the",
        "`provenance.json` written by every versioned run. Ordered oldest to",
        "newest. Numbering is stable for citation as long as no earlier run is",
        "added retroactively.",
        "",
        "## Summary",
        "",
        f"- Runs indexed: **{len(records)}**",
        f"- Studies: **{len(by_study)}**",
        f"- Marked canonical: **{len(canonical)}**",
        f"- Tracked code modified at run time (schema >= 1.1.0): **{len(dirty)}**",
        f"- Git state unresolvable (schema < 1.1.0): **{len(ambiguous)}**",
        f"- Still pinned by a config (must not be archived): **{len(pinned)}**",
        "",
    ]

    if canonical:
        lines += ["## Canonical baselines", ""]
        for record in records:
            if record.run_id in canonical:
                flag = " — ⚠ DIRTY TREE" if record.git_dirty else ""
                lines.append(
                    f"- `{record.study}` / `{record.run_id}`{flag}  \n"
                    f"  `{record.relative_directory}`"
                )
        lines.append("")

    if dirty:
        lines += [
            "## ⚠ Runs with modified tracked code",
            "",
            "A tracked source file was modified when these ran, so the committed",
            "code does not fully describe what produced them. Any number cited",
            "from these needs a clean re-run or an explicit caveat.",
            "",
        ]
        for record in dirty:
            lines.append(
                f"- `{record.study}` / `{record.run_id}` "
                f"(commit `{(record.git_commit or '?')[:8]}`)"
            )
        lines.append("")

    if ambiguous:
        lines += [
            "## Runs whose git state cannot be resolved",
            "",
            "These predate provenance schema 1.1.0, which collapsed *modified",
            "tracked file* and *untracked file present* into a single `dirty`",
            "flag. Because every run writes a new untracked output directory,",
            "that flag reads true after almost any run. For these runs it is",
            "therefore **not** evidence that the code was uncommitted — it is",
            "simply uninformative in both directions. Reproducibility has to be",
            "established by re-running, not read off the record.",
            "",
        ]
        for record in ambiguous:
            lines.append(
                f"- `{record.study}` / `{record.run_id}` "
                f"(commit `{(record.git_commit or '?')[:8]}`)"
            )
        lines.append("")

    lines += ["## Sequential index", ""]
    for number, record in enumerate(records, start=1):
        status: list[str] = []
        if record.run_id in canonical:
            status.append("**CANONICAL**")
        if record.relative_directory in pinned:
            status.append(f"pinned by `{pinned[record.relative_directory]}`")
        if record.git_dirty:
            status.append("⚠ dirty tree")
        downstream = consumers.get(record.run_id, [])
        if downstream:
            status.append(f"consumed by {len(downstream)} run(s)")
        if not status:
            status.append("superseded / exploratory")

        lines += [
            f"### {number:03d} — {record.study}",
            "",
            f"- Run ID: `{record.run_id}`",
            f"- When: {record.timestamp_utc}",
            f"- Path: `{record.relative_directory}`",
            f"- Status: {', '.join(status)}",
            f"- Command: `{' '.join(record.command) or 'n/a'}`",
            f"- Config: `{record.config_path}` (sha256 `{record.config_sha256[:12]}`)",
            f"- Git: `{(record.git_commit or 'unknown')[:12]}`"
            f" ({'dirty' if record.git_dirty else 'clean'})",
            f"- Seed: {record.seed if record.seed is not None else 'n/a'}",
            f"- Artifacts: {record.artifact_count}",
        ]
        if record.source_run_ids:
            lines.append(
                "- Consumes: "
                + ", ".join(f"`{value}`" for value in record.source_run_ids)
            )
        if record.report_files:
            lines.append(
                "- Reports: "
                + ", ".join(f"`{value}`" for value in record.report_files)
            )
        lines.append("")

    return "\n".join(lines)


def archive(
    records: list[RunRecord],
    *,
    canonical: set[str],
    pinned: dict[str, str],
    archive_root: Path,
    apply: bool,
    protect_latest: bool = True,
) -> int:
    """Relocate superseded runs.

    Selection is an inverse allowlist, so the protections decide everything.
    Config-pinning protects a run because something still *depends* on it,
    which is a functional guarantee and says nothing about whether the run is
    scientifically current — a stale run can be pinned and a freshly produced
    one unpinned. `protect_latest` covers that gap by never auto-archiving
    the newest run of a study, which is the one most likely to be the current
    result rather than a superseded duplicate.
    """

    latest_per_study: dict[str, str] = {}
    for record in records:
        latest_per_study[record.study] = record.run_id

    movable: list[RunRecord] = []
    protected: list[tuple[RunRecord, str]] = []
    for record in records:
        if archive_root.name in record.directory.parts:
            continue
        if record.run_id in canonical:
            protected.append((record, "marked canonical"))
            continue
        if record.relative_directory in pinned:
            protected.append(
                (record, f"pinned by {pinned[record.relative_directory]}")
            )
            continue
        if protect_latest and latest_per_study.get(record.study) == record.run_id:
            protected.append((record, "newest run of its study"))
            continue
        movable.append(record)

    if protected:
        print(f"protected from archiving ({len(protected)}):")
        for record, reason in protected:
            print(f"  {record.study}/{record.run_id} — {reason}")
        print()

    if not movable:
        print("nothing to archive: every run is canonical or config-pinned")
        return 0

    print(f"{'MOVING' if apply else 'DRY RUN — would move'} {len(movable)} run(s):")
    manifest: list[dict[str, Any]] = []
    for record in movable:
        destination = archive_root / record.study / record.run_id
        print(f"  {record.relative_directory}  ->  "
              f"{destination.relative_to(REPOSITORY_ROOT).as_posix()}")
        manifest.append(
            {
                "run_id": record.run_id,
                "study": record.study,
                "from": record.relative_directory,
                "to": destination.relative_to(REPOSITORY_ROOT).as_posix(),
                "timestamp_utc": record.timestamp_utc,
            }
        )
        if not apply:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            print(f"    refusing: destination already exists")
            continue
        result = subprocess.run(
            ["git", "mv", record.relative_directory,
             destination.relative_to(REPOSITORY_ROOT).as_posix()],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            shutil.move(str(record.directory), str(destination))

    if apply:
        archive_root.mkdir(parents=True, exist_ok=True)
        manifest_path = archive_root / "ARCHIVE_MANIFEST.json"
        manifest_path.write_text(
            json.dumps(
                {"schema_version": "1.0.0", "moved": manifest}, indent=2
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {manifest_path.relative_to(REPOSITORY_ROOT).as_posix()}")
    else:
        print("\nre-run with --apply to actually move these")
    return len(movable)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", default="runs")
    parser.add_argument("--configs-root", default="configs")
    parser.add_argument("--output", default="docs/thesis/RUN_INDEX.md")
    parser.add_argument(
        "--canonical",
        action="append",
        default=[],
        metavar="RUN_ID",
        help="mark a run as a canonical baseline; repeatable",
    )
    parser.add_argument(
        "--archive-to",
        metavar="PATH",
        help="relocate non-canonical, non-pinned runs under this root",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually move files; without it archiving is a dry run",
    )
    parser.add_argument(
        "--no-protect-latest",
        action="store_true",
        help="allow archiving the newest run of a study (protected by default)",
    )
    args = parser.parse_args(argv)

    runs_root = REPOSITORY_ROOT / args.runs_root
    if not runs_root.is_dir():
        print(f"runs root not found: {runs_root}", file=sys.stderr)
        return 2

    records = load_runs(runs_root)
    if not records:
        print("no provenance.json found under the runs root", file=sys.stderr)
        return 2
    pinned = pinned_directories(REPOSITORY_ROOT / args.configs_root)
    canonical = set(args.canonical)

    unknown = canonical - {record.run_id for record in records}
    if unknown:
        print(f"unknown canonical run id(s): {', '.join(sorted(unknown))}",
              file=sys.stderr)
        return 2

    output_path = REPOSITORY_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_index(records, canonical=canonical, pinned=pinned),
        encoding="utf-8",
    )
    print(f"indexed {len(records)} run(s) -> {args.output}")
    print(f"  canonical: {len(canonical)}")
    resolved_dirty = sum(
        1 for r in records if r.git_dirty and r.git_untracked_present is not None
    )
    unresolvable = sum(
        1 for r in records if r.git_dirty and r.git_untracked_present is None
    )
    print(f"  tracked code modified: {resolved_dirty}")
    print(f"  git state unresolvable (pre-1.1.0 provenance): {unresolvable}")
    print(f"  config-pinned (protected): {len(pinned)}")

    if args.archive_to:
        print()
        archive(
            records,
            canonical=canonical,
            pinned=pinned,
            archive_root=REPOSITORY_ROOT / args.archive_to,
            apply=args.apply,
            protect_latest=not args.no_protect_latest,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
