"""Compare this reconciliation with its saved working-tree starting point."""
from pathlib import Path
import collections
import difflib
import hashlib
import json
import re

audit = Path(__file__).resolve().parent
project = audit.parent / "Thesis/LaTeX_Project"
external = audit.parent.parent / "Temp_dump/27112026_ch_reworked_some"
manifest = json.loads((audit / "starting_project_manifest.json").read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
changed = [name for name, identity in manifest.items()
           if not (project / name).is_file() or sha(project / name) != identity["sha256"]]
allowed = {"README.md", *("chapters/" + name for name in (
    "01_introduction.tex", "02_literature_review.tex", "03_foundations.tex",
    "04_methodology.tex", "06_reassemble.tex"))}
unexpected = sorted(set(changed) - allowed)
external_unchanged = {p.name: p.read_bytes() == (external / p.name).read_bytes()
                      for p in (audit / "external").glob("*.tex")}
diff_dir = audit / "diffs"
diff_dir.mkdir(exist_ok=True)
for name in changed:
    before, after = audit / "before" / name, project / name
    if before.is_file() and after.is_file():
        diff = difflib.unified_diff(before.read_text().splitlines(True),
                                    after.read_text().splitlines(True),
                                    fromfile="starting-tree/" + name,
                                    tofile="reconciled/" + name)
        (diff_dir / (name.replace("/", "__") + ".diff")).write_text("".join(diff))

block_checks = {}
for name in ("05_phm.tex", "06_reassemble.tex"):
    before = (audit / "before/chapters" / name).read_bytes()
    after = (project / "chapters" / name).read_bytes()
    checks = {"byte_identical": before == after}
    for env in (b"table", b"figure"):
        pattern = rb"\\begin\{" + env + rb"\*?\}.*?\\end\{" + env + rb"\*?\}"
        a, b = re.findall(pattern, before, re.S), re.findall(pattern, after, re.S)
        checks[env.decode() + "s"] = {"count_before": len(a), "count_after": len(b),
                                       "all_byte_identical": a == b}
    for kind, pattern in (
        ("labels", rb"\\label\{([^{}]+)\}"),
        ("references", rb"\\(?:ref|eqref|autoref|cref|Cref)\{([^{}]+)\}"),
        ("evidence_ids", rb"\bE\d{3}\b")):
        old = collections.Counter(re.findall(pattern, before))
        new = collections.Counter(re.findall(pattern, after))
        checks["removed_" + kind] = [key.decode() for key in (old - new)]
    block_checks[name] = checks

# Scope is only the TeX files actually read by the completed main build.
fls = project / "build/chapter_reconciliation_20261127_01/thesis/main.fls"
active = set()
if fls.exists():
    for line in fls.read_text().splitlines():
        if line.startswith("INPUT "):
            p = (project / line[6:]).resolve()
            if p.is_relative_to(project) and p.suffix == ".tex" and "build" not in p.relative_to(project).parts:
                active.add(p)
def tex_text(path):
    return re.sub(r"(?<!\\)%[^\n]*", "", path.read_text())
texts = {str(p.relative_to(project)): tex_text(p) for p in sorted(active)}
bib_keys = set()
for name in ("references.bib", "references_additions.bib"):
    bib_keys.update(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", (project / name).read_text()))
labels = collections.defaultdict(list)
refs, cites = set(), set()
for name, content in texts.items():
    for key in re.findall(r"\\label\{([^{}]+)\}", content):
        labels[key].append(name)
    refs.update(re.findall(r"\\(?:ref|eqref|autoref|cref|Cref)\{([^{}]+)\}", content))
    for citation in re.findall(r"\\(?:[A-Za-z]*cite[A-Za-z]*)\*?(?:\s*\[[^\]]*\])*\s*\{([^{}]+)\}", content):
        cites.update(key.strip() for key in citation.split(","))
ch2 = tex_text(project / "chapters/02_literature_review.tex")
ch4 = tex_text(project / "chapters/04_methodology.tex")
summary = {
    "baseline_project_files": len(manifest),
    "changed_project_files": changed,
    "unexpected_changes_or_missing_files": unexpected,
    "external_sources_unchanged": external_unchanged,
    "empirical_preservation": block_checks,
    "active_main_tex_inputs": sorted(texts),
    "duplicate_literal_labels": {k: v for k, v in labels.items() if len(v) > 1},
    "unresolved_literal_references": sorted(refs - labels.keys()),
    "unresolved_citations": sorted(cites - bib_keys),
    "ch2_requirement_tags": re.findall(r"\bR[1-5]\b", ch2),
    "ch4_requirement_paragraphs": re.findall(r"\\textbf\{(R[1-5])\.", ch4),
    "mapping_table_owners": labels.get("tab:fusion-study-scope", []),
    "remaining_ch2_page_checks": (project / "chapters/02_literature_review.tex").read_text().count("[VERIFY PAGES]"),
    "final_project_manifest": {name: {"sha256": sha(project / name), "bytes": (project / name).stat().st_size}
                               for name in manifest if (project / name).is_file()},
}
(audit / "preservation_checks.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: v for k, v in summary.items() if k not in ("final_project_manifest", "active_main_tex_inputs")}, indent=2))
assert not unexpected
assert all(external_unchanged.values())
assert block_checks["05_phm.tex"]["byte_identical"]
assert all(block_checks[name][env]["all_byte_identical"]
           for name in block_checks for env in ("tables", "figures"))
assert not summary["ch2_requirement_tags"]
assert summary["ch4_requirement_paragraphs"] == ["R1", "R2", "R3", "R4", "R5"]
if texts:
    assert not summary["duplicate_literal_labels"]
    assert not summary["unresolved_literal_references"]
    assert not summary["unresolved_citations"]
