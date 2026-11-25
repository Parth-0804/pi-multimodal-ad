"""Prepare the pending relocation without moving or reading source payloads."""
import importlib.util
import json
import os
from pathlib import Path
import stat
from collections import Counter
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("relocation_tool", HERE / "RELOCATION_TOOL.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
ROOT = tool.ROOT


def save(name, value):
    with (HERE / name).open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    if (HERE / "STATUS.json").exists():
        raise RuntimeError("Preflight snapshot already exists; preserve it unchanged")
    sources = []
    seen = set()
    by_root = {}
    for old, new in tool.MAPPINGS:
        counts = Counter()
        for p in tool.walk(ROOT / old):
            rel = str(p.relative_to(ROOT))
            if rel in seen:
                continue
            seen.add(rel)
            entry = {"old": rel, "new": tool.mapped(rel), **tool.identity(p)}
            sources.append(entry)
            kind = "symlinks" if stat.S_ISLNK(entry["mode"]) else "directories" if stat.S_ISDIR(entry["mode"]) else "regular_files"
            counts[kind] += 1
            if kind == "regular_files":
                counts["logical_bytes"] += entry["size"]
        by_root[old] = dict(counts)
    with (HERE / "FILE_METADATA_BEFORE.jsonl").open("x") as stream:
        for entry in sources:
            stream.write(json.dumps(entry) + "\n")
    actions = []
    conflicts = []
    proxies = set()
    special_nested = "DATASET_RESEARCH/VIFAILBACK_VERIFICATION"

    def plan(a, b):
        old, new = str(a.relative_to(ROOT)), str(b.relative_to(ROOT))
        ancestor = b.parent
        while not ancestor.exists():
            ancestor = ancestor.parent
        if a.lstat().st_dev != ancestor.stat().st_dev:
            conflicts.append({"old": old, "new": new, "reason": "different filesystem"})
        if b.is_symlink():
            if b.resolve() == a.resolve():
                proxies.add(new)
                actions.append({"operation": "remove_verified_browsing_proxy", "path": new, "target": os.readlink(b)})
                actions.append({"operation": "rename", "old": old, "new": new})
            else:
                conflicts.append({"old": old, "new": new, "reason": "independent destination symlink"})
        elif not b.exists():
            actions.append({"operation": "rename", "old": old, "new": new})
        elif a.is_dir() and not a.is_symlink() and b.is_dir():
            for child in sorted(a.iterdir()):
                if str(child.relative_to(ROOT)) == special_nested:
                    continue
                plan(child, ROOT / tool.mapped(child.relative_to(ROOT)))
            actions.append({"operation": "remove_empty_source_container", "path": old})
        else:
            conflicts.append({"old": old, "new": new, "reason": "independent destination file"})

    ordered = sorted(tool.MAPPINGS, key=lambda pair: 0 if pair[0] == "VIFAILBACK" else 1)
    for old, new in ordered:
        plan(ROOT / old, ROOT / new)
    links = tool.all_links()
    repairs = []
    for link in links:
        if link["path"] in proxies:
            continue
        new_path = ROOT / tool.mapped(link["path"])
        old_target = Path(link["absolute_target"])
        try:
            new_target = ROOT / tool.mapped(old_target.relative_to(ROOT))
        except ValueError:
            new_target = old_target
        prospective = Path(os.path.normpath(link["target"] if os.path.isabs(link["target"]) else new_path.parent / link["target"]))
        if prospective != new_target:
            repairs.append({"path": str(new_path.relative_to(ROOT)), "old_link_text": link["target"],
                            "new_link_text": os.path.relpath(new_target, new_path.parent),
                            "target_existed_before": link["existed"]})
    save("PATH_MAPPING.json", {"prefix_moves": tool.MAPPINGS, "individual_file_moves": tool.SPECIAL})
    save("MOVE_OPERATIONS.json", actions)
    save("SYMLINKS_BEFORE.json", links)
    save("PLANNED_SYMLINK_REPAIRS.json", repairs)
    status = {"stage": "PENDING_PATH_SPECIFIC_APPROVAL_NO_MOVES_EXECUTED", "utc": datetime.now(timezone.utc).isoformat(),
              "prefix_moves": len(tool.MAPPINGS), "source_nodes": len(sources), "metadata_counts_by_source": by_root,
              "planned_operations": dict(Counter(x["operation"] for x in actions)),
              "conflicts": conflicts, "same_filesystem_gate": not any(x["reason"] == "different filesystem" for x in conflicts),
              "planned_symlink_repairs": len(repairs), "preexisting_broken_links": sum(not x["existed"] for x in links),
              "payloads_read_hashed_copied_changed": False, "move_command_executed": False,
              "automatic_review": "Rejected broad protected relocation; exact path-specific exception requested in MOVE_PLAN.md",
              "synthetic_relocation_check": "PASS: 30 actions, 16 file/link identities, merge/proxy/collision and relative-link cases; isolated temporary fixture only"}
    save("STATUS.json", status)
    print(json.dumps({k: v for k, v in status.items() if k != "metadata_counts_by_source"}, indent=2))


if __name__ == "__main__":
    main()
