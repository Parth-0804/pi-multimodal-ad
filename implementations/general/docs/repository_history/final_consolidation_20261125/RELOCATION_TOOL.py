"""One-off, lossless structural relocation prepared on 2026-11-25.

Only metadata is inspected. No source payload is read, hashed or copied.
The protected move is pending path-specific approval; execution is disabled.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
MAPPINGS = [
    ("DATASET_RESEARCH/VIFAILBACK_VERIFICATION", "implementations/VIFAILBACK/02_dataset_verification/independent_verification"),
    ("MSM", "implementations/MSM"),
    ("HANDOVER", "implementations/HANDOVER"),
    ("REBOOT", "implementations/REBOOT"),
    ("VIFAILBACK", "implementations/VIFAILBACK"),
    ("MILLING DATASET", "implementations/MSM/experiments/legacy"),
    ("CROSS_DATASET_COMPARISON", "implementations/cross_dataset/results"),
    ("DATASET_RESEARCH", "implementations/general/docs/dataset_research"),
    ("26.10.2026_feedback_experiments", "implementations/REASSEMBLE/experiments/cnn_seed_stability/phase1_feedback"),
    ("parth_ws_bootstrap", "implementations/REASSEMBLE/experiments/bootstrap"),
    ("experiments", "implementations/PHM2026/experiments"),
]
# Preserve both colliding files rather than overwriting either.
SPECIAL = {
    "VIFAILBACK/README.md": "implementations/VIFAILBACK/docs/WORKSPACE_BEFORE_CONSOLIDATION.md",
    "MILLING DATASET/.gitignore": str((RUN / "preserved_collisions/milling_root.gitignore").relative_to(ROOT)),
    "CROSS_DATASET_COMPARISON/.gitignore": str((RUN / "preserved_collisions/cross_dataset_root.gitignore").relative_to(ROOT)),
}
SKIP = {".git", "ma_thesis_env", ".aws", ".codex", ".agents"}


def write(name, obj):
    path = RUN / name
    with path.open("x") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def mapped(relative):
    relative = str(relative)
    if relative in SPECIAL:
        return SPECIAL[relative]
    for old, new in MAPPINGS:
        if relative == old or relative.startswith(old + "/"):
            return new + relative[len(old):]
    return relative


def identity(path):
    s = path.lstat()
    result = {"device": s.st_dev, "inode": s.st_ino, "size": s.st_size,
              "mode": s.st_mode, "mtime_ns": s.st_mtime_ns}
    if stat.S_ISLNK(s.st_mode):
        result["target"] = os.readlink(path)
    return result


def walk(path):
    yield path
    if path.is_dir() and not path.is_symlink():
        for parent, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                yield Path(parent) / name


def all_links():
    result = []
    for parent, dirs, files in os.walk(ROOT, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in dirs + files:
            p = Path(parent) / name
            if p.is_symlink():
                target = os.readlink(p)
                absolute = Path(os.path.normpath(target if os.path.isabs(target) else p.parent / target))
                result.append({"path": str(p.relative_to(ROOT)), "target": target,
                               "absolute_target": str(absolute), "existed": p.exists()})
    return result


def main():
    os.chdir(ROOT)
    if not (RUN / "APPROVAL.json").is_file():
        raise RuntimeError("Path-specific protected relocation approval is still pending; no moves allowed")
    if (RUN / "AUTHORIZATION.json").exists():
        raise RuntimeError("This one-off relocation has already been prepared; inspect its journal.")
    gpu = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"],
                         capture_output=True, text=True, check=True)
    if gpu.stdout.strip():
        raise RuntimeError("GPU process present; relocation gate failed")
    auth = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "researcher_instruction": "move them, Just overrite removing but for the structural thing you can move things it's all good, just update it in relative documentation where is what.",
        "context": "Direct response to the enumerated remaining dataset, frozen-study and protected historical roots outside implementations/.",
        "scope": MAPPINGS,
        "superseded_for_this_task_only": "AGENTS.md and data_boundaries.md prohibitions on moving the listed raw-data/historical subtrees; retained default protection applies at their new identities.",
        "operations": "Same-filesystem directory/file renames, verified proxy-symlink replacement, empty source-container removal, relative-link repair and current documentation/path adapter updates.",
        "excluded_operations": "No payload deletion, overwrite, extraction, recompression, raw-content read/hash, model execution, environment changes, commit or push.",
        "gates": "No active training; collision-free destinations or explicit preservation; same filesystem; metadata identities verified after move; no new broken links.",
        "retention_recovery": "All regular files preserve device/inode/size/mode/mtime; mappings and action journal support reversal after collision checks. Frozen records and original raw content remain unchanged.",
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    }
    write("AUTHORIZATION.json", auth)
    write("PATH_MAPPING.json", {"prefix_moves": MAPPINGS, "individual_file_moves": SPECIAL})
    status = subprocess.check_output(["git", "status", "--short", "--branch", "--untracked-files=all"], text=True).splitlines()
    from collections import Counter
    write("GIT_BEFORE.json", {"branch": status[0], "status_counts": dict(Counter(x[:2] for x in status[1:]))})
    links = all_links()
    write("SYMLINKS_BEFORE.json", links)
    records = []
    seen = set()
    for old, _ in MAPPINGS:
        for path in walk(ROOT / old):
            rel = str(path.relative_to(ROOT))
            if rel in seen:
                continue
            seen.add(rel)
            meta = identity(path)
            if stat.S_ISREG(meta["mode"]) or stat.S_ISLNK(meta["mode"]):
                records.append({"old": rel, "new": mapped(rel), **meta})
    with (RUN / "FILE_METADATA_BEFORE.jsonl").open("x") as stream:
        for record in records:
            stream.write(json.dumps(record) + "\n")

    actions = []
    proxies = set()

    def plan(a, b):
        if b.is_symlink():
            if b.resolve() != a.resolve():
                raise RuntimeError(f"Conflicting destination symlink: {b}")
            proxies.add(str(b.relative_to(ROOT)))
            actions.append({"operation": "remove_verified_proxy", "path": str(b.relative_to(ROOT)), "target": os.readlink(b)})
            actions.append({"operation": "rename", "old": str(a.relative_to(ROOT)), "new": str(b.relative_to(ROOT))})
        elif not b.exists():
            if a.lstat().st_dev != b.parent.stat().st_dev:
                raise RuntimeError("Cross-filesystem rename refused")
            actions.append({"operation": "rename", "old": str(a.relative_to(ROOT)), "new": str(b.relative_to(ROOT))})
        elif a.is_dir() and not a.is_symlink() and b.is_dir():
            for child in sorted(a.iterdir()):
                destination = ROOT / mapped(child.relative_to(ROOT))
                destination.parent.mkdir(parents=True, exist_ok=True)
                plan(child, destination)
            actions.append({"operation": "rmdir_empty", "path": str(a.relative_to(ROOT))})
        else:
            raise RuntimeError(f"Conflicting destination: {b}")

    # The VIFAILBACK source is being merged after its historical verification bundle.
    # Replace its proxy for 02_dataset_verification before creating any child there.
    proxy = ROOT / "implementations/VIFAILBACK/02_dataset_verification"
    if not proxy.is_symlink() or proxy.resolve() != (ROOT / "VIFAILBACK/02_dataset_verification").resolve():
        raise RuntimeError("Unexpected VIFAILBACK verification proxy")
    # Plan VIFAILBACK first; other nested destinations can then be prepared safely.
    ordered = sorted(MAPPINGS, key=lambda pair: 0 if pair[0] == "VIFAILBACK" else 1)
    for old, new in ordered:
        target = ROOT / new
        # Do not create children through the not-yet-replaced browsing proxy.
        if old == "DATASET_RESEARCH/VIFAILBACK_VERIFICATION":
            actions.append({"operation": "rename", "old": old, "new": new})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        plan(ROOT / old, target)
    # The nested verification source was separately moved and must not be planned twice.
    nested = "DATASET_RESEARCH/VIFAILBACK_VERIFICATION"
    actions = [a for a in actions if not (a.get("old") == nested and a.get("new") != mapped(nested))]
    # DATASET_RESEARCH recursive planning includes the nested source again: discard that duplicate.
    unique = []
    renamed = set()
    for action in actions:
        if action["operation"] == "rename":
            if action["old"] in renamed:
                continue
            renamed.add(action["old"])
        unique.append(action)
    actions = unique
    write("MOVE_PLAN.json", actions)
    with (RUN / "ACTIONS.jsonl").open("x") as journal:
        for action in actions:
            if action["operation"] == "remove_verified_proxy":
                p = ROOT / action["path"]
                if not p.is_symlink() or os.readlink(p) != action["target"]:
                    raise RuntimeError("Proxy changed after preflight")
                p.unlink()
            elif action["operation"] == "rename":
                a, b = ROOT / action["old"], ROOT / action["new"]
                b.parent.mkdir(parents=True, exist_ok=True)
                if b.exists() or b.is_symlink():
                    raise RuntimeError(f"Destination appeared: {b}")
                os.rename(a, b)
            else:
                (ROOT / action["path"]).rmdir()
            journal.write(json.dumps(action) + "\n")
            journal.flush()

    mismatches = []
    for record in records:
        p = ROOT / record["new"]
        actual = identity(p)
        expected = {k: record[k] for k in actual}
        if actual != expected:
            mismatches.append(record["new"])
    write("PRESERVATION.json", {"regular_files_and_symlinks": len(records), "mismatches": mismatches,
                               "method": "lstat device/inode/size/mode/mtime and link-text comparison; no payload reads or hashes"})
    if mismatches:
        raise RuntimeError("Preservation gate failed")

    repairs = []
    for link in links:
        if link["path"] in proxies:
            continue
        path = ROOT / mapped(link["path"])
        old_target = Path(link["absolute_target"])
        try:
            target = ROOT / mapped(old_target.relative_to(ROOT))
        except ValueError:
            target = old_target
        # If a pre-existing relative target already resolves correctly after the move, retain it.
        current_target = Path(os.path.normpath(os.readlink(path) if os.path.isabs(os.readlink(path)) else path.parent / os.readlink(path)))
        if current_target == target:
            continue
        new_target = os.path.relpath(target, path.parent)
        path.unlink()
        path.symlink_to(new_target)
        repairs.append({"path": str(path.relative_to(ROOT)), "before": link["target"], "after": new_target})
    write("SYMLINK_REPAIRS.json", repairs)
    after = all_links()
    write("SYMLINKS_AFTER.json", after)
    newly_broken = []
    old_existed = {mapped(x["path"]): x["existed"] for x in links if x["path"] not in proxies}
    for link in after:
        if not link["existed"] and old_existed.get(link["path"], False):
            newly_broken.append(link["path"])
    leftovers = [old for old, _ in MAPPINGS if (ROOT / old).exists() or (ROOT / old).is_symlink()]
    write("RELOCATION_STATUS.json", {"stage": "MOVED", "utc": datetime.now(timezone.utc).isoformat(),
                                     "actions": len(actions), "files_preserved": len(records),
                                     "symlinks_repaired": len(repairs), "newly_broken_links": newly_broken,
                                     "old_root_leftovers": leftovers, "documentation_and_checks": "pending"})
    if leftovers or newly_broken:
        raise RuntimeError("Relocation completion gate failed")
    print(json.dumps({"actions": len(actions), "preserved": len(records), "symlink_repairs": len(repairs)}))


if __name__ == "__main__":
    raise SystemExit("NOT EXECUTED: protected relocation requires path-specific approval. See MOVE_PLAN.md.")
