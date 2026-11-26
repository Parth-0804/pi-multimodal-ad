"""Read-only metadata checks for the two caches evicted on 2026-10-26.

No array loading, decoding, GPU initialization, downloads or file writes.
This is an availability check, not numerical reproduction or run approval.
"""
import argparse
import json
from pathlib import Path

PREFIX = Path("runs/reassemble/additional_improvements_executed/20260928T000346Z/01_temporal_visual/frozen_prefix")
PIXEL_RUN = Path("parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01")
GUIDE = "docs/maintenance/REASSEMBLE_CACHE_RETENTION.md"


def read(path):
    return json.loads(path.read_text())


def cache_path(path, root):
    """Reject manifest paths or symlinks that escape the declared array cache."""
    path, root = path.resolve(), root.resolve()
    if not path.is_relative_to(root) or path.suffix != ".npz":
        raise ValueError("Array path escapes the declared cache or is not NPZ")
    return path


def check_prefix(repo):
    root = repo / PREFIX
    entries = read(root / "manifest.json")["files"]
    complete = read(root / "complete.json")
    if not entries or len(entries) != complete["segments"]:
        raise ValueError("Prefix manifest and historical segment count disagree")
    missing, changed, seen = [], [], set()
    for entry in entries:
        path = cache_path(repo / entry["path"], root)
        if path in seen:
            raise ValueError("Duplicate prefix manifest entry")
        seen.add(path)
        if not path.is_file():
            missing.append(entry["path"])
        elif path.stat().st_size != entry["bytes"]:
            changed.append(entry["path"])
    ok = not missing and not changed
    return dict(
        cache="prefix", ok=ok,
        status="READY_METADATA_ONLY" if ok else "BLOCKED_REGENERATION_REQUIRED",
        expected_arrays=len(entries), missing_arrays=len(missing),
        size_mismatches=len(changed), examples=(missing + changed)[:3],
        historical_complete_record=True,
        eviction_record_present=(root / "CACHE_EVICTED.json").is_file(),
        action="Task 1 remains cancelled. A cache-only rebuild needs a separate plan; do not run the legacy supervisor or generator in place.",
    )


def check_pixels(repo):
    run = repo / PIXEL_RUN
    root = run / "shared_cache/pixels"
    samples = read(run / "data_manifests/cohort_and_frames.json")
    config = read(run / "config/resolved_config.json")
    if not samples:
        raise ValueError("Empty pixel/frame manifest")
    videos, cached, seen = {}, 0, set()
    for sample in samples:
        path = cache_path(run / sample["pixel_cache"], root)
        if path in seen:
            raise ValueError("Duplicate pixel cache entry")
        seen.add(path)
        cached += path.is_file()
        if len(sample["frames32"]) != 32 or len(sample["positions16_in32"]) != 16:
            raise ValueError("Incomplete saved frame selection")
        digest = sample["pixel_content_sha256"]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Missing or invalid saved pixel-content hash")
        video = repo / sample["video_path"]
        stamp = sample["video_bytes"], sample["video_mtime_ns"]
        if video in videos and videos[video] != stamp:
            raise ValueError("Conflicting video identity records")
        videos[video] = stamp
    missing, changed = [], []
    for path, (size, mtime) in videos.items():
        if not path.is_file():
            missing.append(str(path.relative_to(repo)))
        else:
            stat = path.stat()
            if (stat.st_size, stat.st_mtime_ns) != (size, mtime):
                changed.append(str(path.relative_to(repo)))
    weights = repo / config["weights_dir"]
    missing_weights = [name for name in ("config.json", "preprocessor_config.json", "model.safetensors") if not (weights / name).is_file()]
    ok = not missing and not changed and not missing_weights
    return dict(
        cache="pixels", ok=ok,
        status=("READY_WITH_REDECODING" if cached < len(samples) else "READY_METADATA_ONLY") if ok else "BLOCKED_INPUTS_UNAVAILABLE_OR_CHANGED",
        manifest_samples=len(samples), cached_samples=cached,
        samples_needing_decode=len(samples) - cached, source_videos=len(videos),
        missing_videos=len(missing), changed_video_metadata=len(changed),
        missing_model_files=missing_weights, examples=(missing + changed)[:3],
        eviction_record_present=(root / "CACHE_EVICTED.json").is_file(),
        action="Exact decoding/hash checks already exist in the saved loaders. Reuse them in a new run; do not write through historical shared-cache symlinks. No run is authorized by this check.",
    )


def assess(repo, selection="all"):
    repo = Path(repo).resolve()
    results = []
    for name, check in (("prefix", check_prefix), ("pixels", check_pixels)):
        if selection not in ("all", name):
            continue
        try:
            results.append(check(repo))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            results.append(dict(cache=name, ok=False, status="BLOCKED_INVALID_OR_MISSING_MANIFEST", error=str(exc)))
    return dict(
        read_only=True, validation="metadata only; no contents decoded or hashed",
        guide=GUIDE, checks=results, ok=all(result["ok"] for result in results),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", choices=("prefix", "pixels", "all"), default="all")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    result = assess(args.repo_root, args.cache)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
