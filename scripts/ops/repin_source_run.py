#!/usr/bin/env python3
"""Re-point one `source_runs` entry in a config at a different run.

Rewrites the entry's `run_id`, `directory`, and every artifact SHA-256 pin,
leaving the rest of the file byte-identical. Hashes are computed from the
files themselves rather than copied out of the new run's output manifest, so
the result is what `load_pinned_run` will actually verify.

The set of pinned artifact paths is preserved exactly. If the new run does not
contain one of them, nothing is written.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import sys

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def sha256_file(path: Path, *, block_bytes: int = 1024 * 1024) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_bytes):
            digest.update(block)
    return digest.hexdigest()


def rewrite(
    lines: list[str],
    *,
    source_key: str,
    new_run_id: str,
    new_directory: str,
    new_hashes: dict[str, str],
) -> list[str]:
    """Replace only the fields inside `source_runs.<source_key>`."""

    output = list(lines)
    in_source_runs = False
    in_target = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        if indent == 0:
            in_source_runs = stripped == "source_runs:"
            in_target = False
            continue
        if not in_source_runs:
            continue
        if indent == 2 and stripped.endswith(":"):
            in_target = stripped[:-1] == source_key
            continue
        if not in_target:
            continue

        if indent == 4 and stripped.startswith("run_id:"):
            output[index] = f"    run_id: {new_run_id}\n"
        elif indent == 4 and stripped.startswith("directory:"):
            output[index] = f"    directory: {new_directory}\n"
        elif indent == 6 and ":" in stripped:
            artifact_path = stripped.split(":", 1)[0].strip()
            if artifact_path in new_hashes:
                output[index] = f"      {artifact_path}: {new_hashes[artifact_path]}\n"
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="repository-relative config path")
    parser.add_argument("source_key", help="key under source_runs, e.g. patchtst")
    parser.add_argument("new_run", help="repository-relative new run directory")
    parser.add_argument(
        "--apply", action="store_true", help="write the file; default is a dry run"
    )
    args = parser.parse_args(argv)

    config_path = REPOSITORY_ROOT / args.config
    new_run = REPOSITORY_ROOT / args.new_run
    if not config_path.is_file():
        print(f"config not found: {args.config}", file=sys.stderr)
        return 2
    if not new_run.is_dir():
        print(f"new run directory not found: {args.new_run}", file=sys.stderr)
        return 2

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    sources = (data or {}).get("source_runs")
    if not isinstance(sources, dict) or args.source_key not in sources:
        available = ", ".join(sorted(sources or {}))
        print(
            f"'{args.source_key}' is not a source_runs key; available: {available}",
            file=sys.stderr,
        )
        return 2

    entry = sources[args.source_key]
    old_run_id = entry.get("run_id")
    pinned_paths = sorted(entry.get("artifacts") or {})
    if not pinned_paths:
        print(f"'{args.source_key}' pins no artifacts", file=sys.stderr)
        return 2

    new_run_id = new_run.name
    if old_run_id == new_run_id:
        print(f"already pinned to {new_run_id}; nothing to do")
        return 0

    # Every currently-pinned artifact must exist in the new run, or the
    # downstream stage would lose an input it depends on.
    missing = [rel for rel in pinned_paths if not (new_run / rel).is_file()]
    if missing:
        print(
            f"refusing: the new run is missing {len(missing)} pinned artifact(s):",
            file=sys.stderr,
        )
        for rel in missing:
            print(f"  {rel}", file=sys.stderr)
        return 1

    new_hashes = {rel: sha256_file(new_run / rel) for rel in pinned_paths}

    print(f"config      : {args.config}")
    print(f"source key  : {args.source_key}")
    print(f"run_id      : {old_run_id}  ->  {new_run_id}")
    print(f"directory   : {entry.get('directory')}  ->  {args.new_run}")
    print("artifacts   :")
    unchanged = 0
    for rel in pinned_paths:
        old = (entry.get("artifacts") or {}).get(rel, "")
        new = new_hashes[rel]
        if old == new:
            unchanged += 1
            print(f"  = {rel}  (identical content)")
        else:
            print(f"  ~ {rel}")
            print(f"      {old[:16]}...  ->  {new[:16]}...")
    if unchanged:
        print(f"({unchanged} artifact(s) byte-identical between the two runs)")

    updated = rewrite(
        config_path.read_text(encoding="utf-8").splitlines(keepends=True),
        source_key=args.source_key,
        new_run_id=new_run_id,
        new_directory=args.new_run,
        new_hashes=new_hashes,
    )

    if not args.apply:
        print("\ndry run — re-run with --apply to write the file")
        return 0

    config_path.write_text("".join(updated), encoding="utf-8")

    # Re-read through the real loader so a malformed write fails here, loudly,
    # rather than inside the next training run.
    check = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    rewritten = check["source_runs"][args.source_key]
    if rewritten["run_id"] != new_run_id or rewritten["artifacts"] != new_hashes:
        print("post-write verification FAILED; inspect the file", file=sys.stderr)
        return 1
    print(f"\nwrote {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
