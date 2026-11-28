"""Read-only local/Git/remote publication inventory for reviewed evidence candidates."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import subprocess

audit = Path(__file__).resolve().parent
root = audit.parent.parent
remote_info = json.loads((audit / "checks/remote_refs.json").read_text())
main_sha = remote_info["refs"]["refs/heads/main"]
review_ref = "refs/heads/thesis/manav-review-diagrams-20261126"
review_sha = remote_info["refs"][review_ref]
records = []
for chapter in [5, 6, 7, 8]:
    records.extend(json.loads((audit / f"reviews/chapter{chapter:02}_support.json").read_text()))
grouped = collections.defaultdict(list)
for rec in records:
    path = rec["path"]
    assert not Path(path).is_absolute() and ".." not in Path(path).parts, path
    grouped[path].append(rec)
paths = sorted(grouped)

remote_blobs = {}
complete_prefixes = []
for p in (audit / "checks").glob("github_main*_tree.json"):
    data = json.loads(p.read_text())
    prefix = data.get("audit_prefix", "")
    if not data.get("truncated", True):
        complete_prefixes.append(prefix)
    for item in data.get("tree", []):
        name = prefix + "/" + item["path"] if prefix else item["path"]
        if item["type"] == "blob":
            remote_blobs[name] = item
root_entries = {x["path"] for x in json.loads((audit / "checks/github_main_root_nonrecursive.json").read_text())["tree"]}

def git(args, stdin=None):
    result = subprocess.run(["git", *args], cwd=root, input=stdin, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    allowed = {0, 1} if args[0] == "check-ignore" else {0}
    if result.returncode not in allowed:
        raise RuntimeError(f"git {args[0]} failed: {result.stderr.decode()}")
    return result.stdout

def tree(sha):
    result = {}
    for row in git(["ls-tree", "-rz", sha, "--", *paths]).split(b"\0"):
        if row:
            meta, name = row.split(b"\t", 1)
            mode, kind, blob = meta.split()
            result[name.decode()] = blob.decode()
    return result
review_tree = tree(review_sha)
head_tree = tree("HEAD")
index = {}
for row in git(["ls-files", "--stage", "-z", "--", *paths]).split(b"\0"):
    if row:
        meta, name = row.split(b"\t", 1)
        index[name.decode()] = meta.split()[1].decode()
ignore = {}
data = git(["check-ignore", "--no-index", "-v", "-z", "--stdin"], b"\0".join(p.encode() for p in paths) + b"\0").split(b"\0")
for i in range(0, len(data)-3, 4):
    source, line, pattern, path = [v.decode() for v in data[i:i+4]]
    ignore[path] = {"rule": f"{source}:{line}:{pattern}", "ignored": not pattern.startswith("!")}

rows = []
priority_order = {"core": 0, "supporting": 1, "optional": 2}
for path in paths:
    candidates = grouped[path]
    p = root / path
    priority = min((r["priority"] for r in candidates), key=lambda x: priority_order[x])
    role = "; ".join(sorted({r["role"] for r in candidates}))
    notes = " | ".join(dict.fromkeys(r.get("note", "") for r in candidates if r.get("note")))
    forbidden = p.suffix.lower() in {".pt", ".pth", ".ckpt", ".safetensors", ".h5", ".hdf5"}
    exists = p.is_file()
    blob = sha = ""
    if exists and not forbidden:
        content = p.read_bytes()
        sha = hashlib.sha256(content).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    if not exists:
        local = "missing"
    elif path in index:
        local = "tracked_unchanged" if index[path] == blob else "tracked_worktree_modified"
    else:
        local = "ignored" if ignore.get(path, {}).get("ignored") else "untracked"
    remote_item = remote_blobs.get(path)
    if remote_item:
        remote = "identical" if remote_item["sha"] == blob else "different_content"
    elif any(path.startswith(prefix + "/") or not prefix for prefix in complete_prefixes) or path.split("/")[0] not in root_entries:
        remote = "absent"
    else:
        remote = "unknown_truncated_metadata"
    review = "absent" if path not in review_tree else ("identical" if review_tree[path] == blob else "different_content")
    if not exists:
        action = "recover_or_resolve_missing_source"
    elif forbidden:
        action = "exclude_payload"
    elif remote == "identical":
        action = "already_on_main_no_upload_needed"
    elif remote == "different_content":
        action = "review_local_update_before_upload"
    elif remote == "absent":
        action = "candidate_to_add_after_review"
    else:
        action = "verify_remote_path_before_deciding"
    if forbidden:
        gate = "excluded raw/model payload; metadata only"
    elif any(w in role.lower() for w in ["prediction", "manifest", "label", "split"]):
        gate = "review derived IDs/labels and dataset terms; exact allow-list if ignored"
    else:
        gate = "review exact file and lineage; exact allow-list if ignored"
    rows.append({"path": path, "chapters": ";".join(f"{x:02d}" for x in sorted({int(r["chapter"]) for r in candidates})),
                 "claim_or_section": " | ".join(dict.fromkeys(r["claim_or_section"] for r in candidates)),
                 "role": role, "priority": priority, "exists": exists,
                 "bytes": p.stat().st_size if exists else None, "sha256": sha,
                 "git_blob_sha1": blob, "local_git_state": local,
                 "ignore_rule": ignore.get(path, {}).get("rule", ""),
                 "head_blob": head_tree.get(path, ""),
                 "github_main_state": remote, "github_main_blob": remote_item["sha"] if remote_item else "",
                 "github_review_branch_state": review, "action": action,
                 "publication_review": gate, "inspected": all(r.get("inspected", False) for r in candidates), "notes": notes})
rows.sort(key=lambda r: (priority_order[r["priority"]], r["chapters"], r["path"]))
(audit / "supporting_file_inventory.json").write_text(json.dumps(rows, indent=2) + "\n")
with (audit / "supporting_file_inventory.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
summary = {"remote_main_commit": main_sha, "remote_review_branch_commit": review_sha,
           "candidate_files": len(rows), "by_priority": dict(collections.Counter(r["priority"] for r in rows)),
           "by_action": dict(collections.Counter(r["action"] for r in rows)),
           "core_by_action": dict(collections.Counter(r["action"] for r in rows if r["priority"] == "core")),
           "by_local_state": dict(collections.Counter(r["local_git_state"] for r in rows))}
(audit / "checks/inventory_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
