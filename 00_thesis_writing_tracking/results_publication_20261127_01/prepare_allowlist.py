"""Open only reviewed evidence paths; preserve all other ignore protections."""
from pathlib import Path
import hashlib
import json
import subprocess

record = Path(__file__).resolve().parent
root = record.parent.parent
selected = json.loads((record / "selected_files.json").read_text())
paths = [row["path"] for row in selected]
backups = record / "checks/ignore_before"
backups.mkdir(exist_ok=True)
edits = {}


def ignored(names):
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-v", "-z", "--stdin"],
        cwd=root, input=b"\0".join(p.encode() for p in names) + b"\0",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.decode())
    parts = result.stdout.split(b"\0")
    answer = {}
    for i in range(0, len(parts) - 3, 4):
        source, line, pattern, path = (v.decode() for v in parts[i:i+4])
        if not pattern.startswith("!"):
            answer[path] = (source, line, pattern)
    return answer


for row in selected:
    p = root / row["path"]
    if p.is_symlink() or not p.resolve().is_relative_to(root):
        raise RuntimeError(f"Unsafe selected location: {row['path']}")
    if hashlib.sha256(p.read_bytes()).hexdigest() != row["sha256"]:
        raise RuntimeError(f"Selected bytes changed: {row['path']}")

for iteration in range(32):
    blocked = ignored(paths)
    if not blocked:
        break
    parents = sorted({str(p) for name in blocked for p in Path(name).parents if str(p) != "."})
    blocked_parents = ignored(parents)
    additions = {}
    for name, info in blocked.items():
        blocked_ancestors = [p for p in Path(name).parents if str(p) in blocked_parents]
        if blocked_ancestors:
            target = min(blocked_ancestors, key=lambda p: len(p.parts))
            source = blocked_parents[str(target)][0]
            directory = True
        else:
            target, source, directory = Path(name), info[0], False
        source_path = root / source
        if source_path.name != ".gitignore" or not source_path.resolve().is_relative_to(root):
            raise RuntimeError(f"Unexpected ignore source: {source}")
        relative = target.relative_to(Path(source).parent).as_posix()
        if any(c in relative for c in "*?[]\\\n\r"):
            raise RuntimeError(f"Path needs explicit escaping: {relative}")
        # Reopened directories stay closed to every unselected sibling.
        rules = [f"!/{relative}/", f"/{relative}/*"] if directory else [f"!/{relative}"]
        additions.setdefault(source, set()).add(tuple(rules))
    for source, rule_groups in sorted(additions.items()):
        dest = root / source
        if source not in edits:
            backup = backups / source
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(dest.read_bytes())
            edits[source] = []
        rules = [rule for group in sorted(rule_groups) for rule in group]
        newline = "\r\n" if b"\r\n" in dest.read_bytes() else "\n"
        header = ["", "# Reviewed result evidence, 2026-11-27: exact existing paths only.",
                  "# Selection and limits: 00_thesis_writing_tracking/results_publication_20261127_01/README.md"]
        if edits[source]:
            header = []
        original = dest.read_bytes()
        if original and not original.endswith(b"\n"):
            original += newline.encode()
        dest.write_bytes(original + (newline.join(header + rules) + newline).encode())
        edits[source].extend(rules)
else:
    raise RuntimeError("Ignore traversal exceeded expected depth")

remaining = ignored(paths)
if remaining:
    raise RuntimeError(f"Selected files remain ignored: {len(remaining)}")
(record / "checks/ignore_edits.json").write_text(json.dumps(edits, indent=2) + "\n")
print(json.dumps({"selected": len(paths), "ignore_files": len(edits),
                  "added_rules": sum(map(len, edits.values())), "remaining_ignored": len(remaining)}))
