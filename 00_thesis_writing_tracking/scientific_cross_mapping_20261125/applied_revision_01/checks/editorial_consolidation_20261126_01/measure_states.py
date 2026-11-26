#!/usr/bin/env python3
"""Measure already-built editorial states; never compiles or changes sources.

Run using the repository's existing ma_thesis_env Python (pypdf is required).
The default directory is this script's directory. All outputs are confined to
state_metrics.json and STATE_METRICS.md there, or in an explicit --root directory.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from pypdf import PdfReader


CHAPTERS = [
    "01_introduction.tex", "02_literature_review.tex", "03_foundations.tex",
    "04_methodology.tex", "05_phm.tex", "06_reassemble.tex", "07_msm.tex",
    "08_vifailback.tex", "09_discussion.tex", "10_conclusion.tex",
]
EDITIONS = {
    "full": ("main_build", "main", 10),
    "review": ("review_build", "review", 10),
    "manav": ("manav_review_build", "manav_review", 4),
}
WORD_METHOD = (
    "Approximate source-word tokens, calculated identically for A/B/C. Expand "
    "local input/include files; remove comments, inline/display mathematics, "
    "equation/align/verbatim/code environments, citation and cross-reference "
    "arguments, EvidenceRef calls, graphic paths and layout arguments. Retain "
    "ordinary prose, headings, captions, display notes and table-cell text. "
    "Replace ReviewWorkCount by its source-defined number. Count Unicode "
    "letter/number sequences with internal apostrophes, hyphens or decimal "
    "punctuation as single tokens. This is a consistent approximation, not a "
    "formal natural-language word count; source paths/identifiers in visible "
    "text can contribute tokens. Abstract counts exclude the root-file keywords."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def group(text: str, pos: int, opener: str = "{", closer: str = "}"):
    """Return a balanced TeX group and the first position after it."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != opener:
        raise ValueError(f"Expected {opener!r} near {text[pos:pos + 60]!r}")
    start, depth = pos + 1, 1
    pos += 1
    while pos < len(text):
        if text[pos] == "\\":
            pos += 2
            continue
        if text[pos] == opener:
            depth += 1
        elif text[pos] == closer:
            depth -= 1
            if not depth:
                return text[start:pos], pos + 1
        pos += 1
    raise ValueError("Unbalanced TeX group")


def skip_options(text: str, pos: int) -> int:
    while True:
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text) or text[pos] != "[":
            return pos
        _, pos = group(text, pos, "[", "]")


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def remove_commands(text: str, commands: dict[str, int]) -> str:
    pattern = re.compile(r"\\(" + "|".join(sorted(map(re.escape, commands), key=len, reverse=True)) + r")\*?(?![A-Za-z])")
    result, last = [], 0
    for match in pattern.finditer(text):
        if match.start() < last:
            continue
        end = skip_options(text, match.end())
        try:
            for _ in range(commands[match.group(1)]):
                _, end = group(text, end)
        except ValueError:
            # A command token without its required argument is unexpected in the
            # manuscript; fail rather than silently skew its word count.
            raise ValueError(f"Cannot parse {match.group(0)} near {text[match.start():match.start()+100]!r}")
        result.append(text[last:match.start()])
        result.append(" ")
        last = end
    result.append(text[last:])
    return "".join(result)


def expanded_source(path: Path, source_root: Path, seen=None):
    seen = [] if seen is None else seen
    resolved = path.resolve()
    if resolved in seen:
        raise ValueError(f"Recursive input: {path}")
    text = strip_comments(path.read_text())
    inputs = {str(path.relative_to(source_root)): sha256(path)}

    def expand(match):
        target = match.group(1)
        target = target if Path(target).suffix else target + ".tex"
        candidates = [source_root / target, path.parent / target]
        selected = next((p for p in candidates if p.is_file()), None)
        if selected is None:
            raise FileNotFoundError(f"Unresolved input {target} in {path}")
        child, child_inputs = expanded_source(selected, source_root, seen + [resolved])
        inputs.update(child_inputs)
        return child

    text = re.sub(r"\\(?:input|include)\s*\{([^}]+)\}", expand, text)
    return text, inputs


def words(text: str, review_count: str) -> int:
    text = text.replace(r"\ReviewWorkCount{}", review_count)
    text = re.sub(r"\\begin\{(equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|verbatim\*?|lstlisting|minted|tikzpicture)\}.*?\\end\{\1\}", " ", text, flags=re.S)
    text = re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]|\$\$.*?\$\$|(?<!\\)\$(?:\\.|[^$])*?(?<!\\)\$", " ", text, flags=re.S)
    citation_names = set(re.findall(r"\\((?:[Pp]aren|[Tt]ext|[Aa]uto|[Ff]oot|[Ss]mart)?cite[a-zA-Z]*|[Cc]ite[a-zA-Z]*)\*?", text))
    commands = {name: 1 for name in citation_names}
    commands.update({
        "label": 1, "ref": 1, "pageref": 1, "autoref": 1, "cref": 1,
        "Cref": 1, "eqref": 1, "EvidenceRef": 2, "includegraphics": 1,
        "url": 1, "addcontentsline": 3, "setlength": 2, "addtolength": 2,
        "setstretch": 1, "fontsize": 2, "hspace": 1, "vspace": 1,
        "rule": 2, "enlargethispage": 1,
    })
    text = remove_commands(text, commands)
    # Remove local environment/layout declarations while retaining their cells.
    text = re.sub(r"\\begin\{tabularx\}\s*\{[^}]*\}\s*\{(?:[^{}]|\{[^{}]*\})*\}", " ", text)
    text = re.sub(r"\\begin\{(?:tabular|longtable)\}\s*\{(?:[^{}]|\{[^{}]*\})*\}", " ", text)
    text = re.sub(r"\\(?:begin|end)\{[^}]*\}(?:\[[^]]*\])?", " ", text)
    text = re.sub(r"\\(?:newcommand|renewcommand)\s*\{[^}]*\}(?:\[[^]]*\])?\s*\{[^}]*\}", " ", text)
    text = re.sub(r"\\(?:multirow|multicolumn)\s*\{[^}]*\}\s*\{[^}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^]]*\])?", " ", text)
    return len(re.findall(r"[^\W_]+(?:[.,’'\-][^\W_]+)*", text, flags=re.UNICODE))


def source_metrics(source_root: Path):
    review_text = (source_root / "tables/review_counts.tex").read_text()
    match = re.search(r"\\(?:newcommand|renewcommand)\{\\ReviewWorkCount\}\{(\d+)\}", review_text)
    if not match:
        raise ValueError("Cannot identify source-defined ReviewWorkCount")
    result = {}
    for key, relative in [("abstract", "frontmatter/abstract.tex")] + [(str(i), "chapters/" + name) for i, name in enumerate(CHAPTERS, 1)]:
        text, inputs = expanded_source(source_root / relative, source_root)
        headings = Counter((m.group(1), bool(m.group(2))) for m in re.finditer(r"\\(chapter|section|subsection|subsubsection|paragraph)(\*)?\s*(?:\[[^]]*\])?\{", text))
        result[key] = {
            "source": relative,
            "sha256": inputs[relative],
            "input_sha256": inputs,
            "approximate_words": words(text, match.group(1)),
            "principal_sections": headings[("section", False)],
            "subsections": headings[("subsection", False)],
            "subsubsections": headings[("subsubsection", False)],
            "paragraph_headings": headings[("paragraph", False)],
            "unnumbered_headings": sum(n for (kind, starred), n in headings.items() if starred),
        }
    return result


def toc_chapters(aux: Path):
    """Read only TOC chapter writes: never LOF/LOT entries or newlabel lines."""
    result = []
    for line in aux.read_text().splitlines():
        if not line.startswith(r"\@writefile{toc}{"):
            continue
        kind, end = group(line, len(r"\@writefile"))
        assert kind == "toc"
        payload, _ = group(line, end)
        match = re.match(r"\s*\\contentsline\s*", payload)
        if not match:
            continue
        args, pos = [], match.end()
        for _ in range(4):
            value, pos = group(payload, pos)
            args.append(value)
        if args[0] != "chapter":
            continue
        title, number = args[1], None
        if title.startswith(r"\numberline"):
            number, pos = group(title, len(r"\numberline"))
            title = title[pos:]
        result.append({"number": number, "title": title.strip(), "printed_start": args[2], "anchor": args[3]})
    return result


def edition_metrics(state_dir: Path, edition: str):
    folder, job, expected = EDITIONS[edition]
    build = state_dir / folder
    pdf, aux, log = [build / f"{job}.{suffix}" for suffix in ("pdf", "aux", "log")]
    for path in (pdf, aux, log):
        if not path.is_file():
            raise FileNotFoundError(f"Build not complete: missing {path}")
    if "Output written on" not in log.read_text(errors="replace"):
        raise ValueError(f"No completed XeLaTeX output recorded in {log}")
    reader = PdfReader(pdf)
    page_labels = reader.page_labels
    destinations = reader.named_destinations
    entries = toc_chapters(aux)
    for entry in entries:
        if entry["anchor"] not in destinations:
            raise ValueError(f"Missing PDF destination {entry['anchor']} in {pdf}")
        entry["physical_start"] = reader.get_destination_page_number(destinations[entry["anchor"]]) + 1
        actual_label = page_labels[entry["physical_start"] - 1]
        if actual_label != entry["printed_start"]:
            raise ValueError(f"AUX/PDF printed-label disagreement for {entry}: {actual_label}")
    for left, right in zip(entries, entries[1:]):
        if left["physical_start"] >= right["physical_start"]:
            raise ValueError(f"Non-increasing chapter boundaries in {pdf}: {left}, {right}")
    numeric = [entry for entry in entries if entry["number"] and entry["number"].isdigit()]
    if [int(entry["number"]) for entry in numeric] != list(range(1, expected + 1)):
        raise ValueError(f"Unexpected numbered chapter sequence in {aux}")
    chapters = {}
    for entry in entries:
        index = entries.index(entry)
        next_start = entries[index + 1]["physical_start"] if index + 1 < len(entries) else len(reader.pages) + 1
        if entry["title"] == "Abstract":
            # Contents and lists do not have TOC chapter entries; their PDF
            # chapter destinations nevertheless delimit the full Abstract.
            later = [reader.get_destination_page_number(dest) + 1 for name, dest in destinations.items() if name.startswith(("chapter.", "chapter*.")) and reader.get_destination_page_number(dest) + 1 > entry["physical_start"]]
            next_start = min(later)
        end = next_start - 1
        measured = dict(entry, physical_end=end, printed_end=page_labels[end - 1], pages=end - entry["physical_start"] + 1)
        key = entry["number"] if entry["number"] and entry["number"].isdigit() else entry["title"]
        chapters[key] = measured
    body_pages = sum(chapters[str(i)]["pages"] for i in range(1, expected + 1))
    return {
        "pdf": str(pdf.relative_to(state_dir.parent)), "pdf_sha256": sha256(pdf),
        "aux": str(aux.relative_to(state_dir.parent)), "aux_sha256": sha256(aux),
        "log": str(log.relative_to(state_dir.parent)),
        "total_physical_pages": len(reader.pages), "numbered_chapter_pages": body_pages,
        "chapter_1_to_4_pages": sum(chapters[str(i)]["pages"] for i in range(1, 5)),
        "non_numbered_chapter_pages": len(reader.pages) - body_pages,
        "chapters": chapters,
        "chapter_10_boundary": chapters.get("10", {}).get("physical_end"),
    }


def markdown(data):
    lines = ["# Editorial and formatting state measurements", "", "A = unchanged November 26 source; B = consolidated Chapters 3–4 with A formatting; C = the same consolidated chapter text with central formatting changes.", "", "All page counts below come from the rebuilt PDFs. Chapter ranges use PDF named destinations, cross-checked against TOC-only AUX entries and PDF printed page labels. Counts include figures, tables and any page space up to the next chapter; they are exact pagination spans, not estimates of prose occupancy.", "", "## PDF totals", "", "| Edition | A | B | C | Saved by consolidation (A−B) | Additional saved by formatting (B−C) |", "|---|---:|---:|---:|---:|---:|"]
    for edition, title in [("full", "Full manuscript"), ("review", "Review edition, Abstract + Chapters 1–10"), ("manav", "Manav, Abstract + Chapters 1–4")]:
        counts = [data["states"][s]["editions"][edition]["total_physical_pages"] for s in "ABC"]
        lines.append(f"| {title} | {counts[0]} | {counts[1]} | {counts[2]} | {counts[0]-counts[1]} | {counts[1]-counts[2]} |")
    lines += ["", "## Chapter pages in the full manuscript", "", "Printed starts are the page numbers shown in the thesis. Physical ranges are PDF viewer pages. States A and B retain the existing two-page Abstract in the full/review editions and the previously approved one-page Manav Abstract. State C uses the shared compact heading across all editions; the Abstract wording is unchanged.", "", "| Part | A: printed start; PDF range; count | B: printed start; PDF range; count | C: printed start; PDF range; count | A−B | B−C |", "|---|---|---|---|---:|---:|"]
    for key in ["Abstract"] + list(map(str, range(1, 11))):
        parts, counts = [], []
        for state in "ABC":
            item = data["states"][state]["editions"]["full"]["chapters"][key]
            parts.append(f"{item['printed_start']}; {item['physical_start']}–{item['physical_end']}; **{item['pages']}**")
            counts.append(item["pages"])
        lines.append(f"| {'Abstract' if key == 'Abstract' else 'Chapter '+key} | " + " | ".join(parts) + f" | {counts[0]-counts[1]} | {counts[1]-counts[2]} |")
    lines += ["", "Chapter 10 ends before the following **AI Assistance Disclosure**. The disclosure, bibliography, appendices and frontmatter are included in the full-PDF total but are not assigned to Chapter 10. The JSON lists their separate TOC-based boundaries.", "", "## Manav chapter ranges", "", "| Part | A: printed/PDF range; pages | B: printed/PDF range; pages | C: printed/PDF range; pages |", "|---|---|---|---|"]
    for key in ["Abstract", "1", "2", "3", "4"]:
        values = []
        for state in "ABC":
            item = data["states"][state]["editions"]["manav"]["chapters"][key]
            values.append(f"{item['printed_start']}–{item['printed_end']}; **{item['pages']}**")
        lines.append(f"| {'Abstract' if key == 'Abstract' else 'Chapter '+key} | " + " | ".join(values) + " |")
    lines += ["", "## Source words and headings", "", WORD_METHOD, "", "Columns ‘sections/subsections’ count numbered source commands. Other heading types are separately retained in the JSON. B and C have identical chapter/Abstract source hashes, word counts and heading counts.", "", "| Part | A approximate words | B approximate words | C approximate words | A sections/subsections | B sections/subsections | C sections/subsections |", "|---|---:|---:|---:|---:|---:|---:|"]
    for key in ["abstract"] + list(map(str, range(1, 11))):
        items = [data["states"][state]["sources"][key] for state in "ABC"]
        counts = " | ".join(str(item["approximate_words"]) for item in items)
        heads = " | ".join(f"{item['principal_sections']}/{item['subsections']}" for item in items)
        lines.append(f"| {'Abstract' if key == 'abstract' else 'Chapter '+key} | {counts} | {heads} |")
    lines += ["", "Source hashes identify exactly which files were measured. Source-word totals include only the named Abstract/chapter files, not the bibliography, root keywords or appendices. Formatting-only pagination changes in protected chapters do not indicate textual changes.", "", "## Measurement provenance", "", "`state_metrics.json` records input PDF/AUX hashes, source hashes, every chapter destination and its printed and physical boundaries. This helper reads existing builds and never compiles, modifies manuscript sources, or runs experiments.", "", f"Generated at {data['generated_utc']}.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--sources-only", action="store_true", help="Print source metrics without reading builds or writing reports")
    args = parser.parse_args()
    root = args.root.resolve()
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(), "word_count_method": WORD_METHOD, "page_count_method": "Physical PDF page differences between consecutive TOC chapter destinations, checked against printed PDF labels; Abstract ends at next PDF chapter destination (Contents in the full edition).", "states": {}}
    for state in "ABC":
        state_dir = root / f"state_{state}"
        item = {"sources": source_metrics(state_dir / "source")}
        if not args.sources_only:
            item["editions"] = {edition: edition_metrics(state_dir, edition) for edition in EDITIONS}
        result["states"][state] = item
    for key, source in result["states"]["B"]["sources"].items():
        if source != result["states"]["C"]["sources"][key]:
            raise ValueError(f"B/C chapter text or source metrics differ: {key}")
    protected = ["abstract", "1", "2"] + list(map(str, range(5, 11)))
    for key in protected:
        if any(result["states"][state]["sources"][key] != result["states"]["A"]["sources"][key] for state in "BC"):
            raise ValueError(f"Protected source changed: {key}")
    if args.sources_only:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    (root / "state_metrics.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    (root / "STATE_METRICS.md").write_text(markdown(result))
    for state in "ABC":
        totals = {edition: item["total_physical_pages"] for edition, item in result["states"][state]["editions"].items()}
        print(f"State {state}: {totals}")
    print(f"Wrote {root / 'state_metrics.json'} and {root / 'STATE_METRICS.md'}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as exc:
        print(f"Measurement stopped: {exc}", file=sys.stderr)
        raise SystemExit(1)
