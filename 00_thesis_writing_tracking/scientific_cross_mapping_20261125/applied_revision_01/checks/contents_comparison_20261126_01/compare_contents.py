"""Compare the preserved baseline index with the latest compiled Manav extract.

Read-only with respect to the manuscripts and PDFs. Outputs live beside this file.
Run from the repository root with ma_thesis_env/bin/python.
"""

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


OUT = Path(__file__).resolve().parent
REVISION = OUT.parents[1]
REPO = Path.cwd().resolve()
BASE_TOC = REVISION / "checks/baseline_build/main.toc"
LATEST_AUX = REVISION / "checks/manav_abstract_layout_20261126_01/manav_build/manav_review.aux"
BASE_PDF = REVISION / "checks/baseline_build/main.pdf"
LATEST_PDF = REVISION / "Manav_review_Abstract_Chapters_1-4.pdf"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def braced(text, pos):
    while pos < len(text) and text[pos].isspace():
        pos += 1
    assert text[pos] == "{", (text, pos)
    start = pos + 1
    depth = 1
    pos += 1
    while depth:
        if text[pos] == "{" and text[pos - 1] != "\\":
            depth += 1
        elif text[pos] == "}" and text[pos - 1] != "\\":
            depth -= 1
        pos += 1
    return text[start : pos - 1], pos


def plain(text):
    return text.replace("---", "—").replace("--", "–").replace("~", " ").strip()


def parse(path):
    entries = []
    chapter = None
    for line in path.read_text().splitlines():
        if "\\@writefile{" in line and "\\@writefile{toc}" not in line:
            continue
        marker = "\\contentsline "
        if marker not in line:
            continue
        pos = line.index(marker) + len(marker)
        fields = []
        for _ in range(4):
            value, pos = braced(line, pos)
            fields.append(value)
        level, title, page, anchor = fields
        assert level in ("chapter", "section", "subsection", "subsubsection", "paragraph"), level
        number = ""
        if title.startswith("\\numberline "):
            number, end = braced(title, len("\\numberline "))
            title = title[end:]
        if level == "chapter":
            chapter = int(number) if number.isdigit() else None
        if chapter in (1, 2, 3, 4):
            entries.append(dict(chapter=chapter, level=level, number=number,
                                title=plain(title), page=int(page), anchor=anchor))
    return entries


base = parse(BASE_TOC)
latest = parse(LATEST_AUX)
base_reader, latest_reader = PdfReader(BASE_PDF), PdfReader(LATEST_PDF)
assert len(latest_reader.pages) == 126
assert digest(LATEST_PDF) == json.loads(
    (REVISION / "checks/manav_abstract_layout_20261126_01/validation.json").read_text()
)["pdf_sha256"]

# Verify every indexed entry against the destination in its corresponding PDF.
verified = []
for edition, entries, reader, offset in [
    ("baseline", base, base_reader, 11), ("latest", latest, latest_reader, 0)
]:
    for entry in entries:
        destination = reader.named_destinations[entry["anchor"]]
        physical = reader.get_destination_page_number(destination) + 1
        assert physical == entry["page"] + offset, (edition, entry, physical)
        verified.append(dict(edition=edition, anchor=entry["anchor"],
                             printed_page=entry["page"], pdf_page=physical))


def by_number(entries):
    return {entry["number"]: entry for entry in entries if entry["number"]}


bmap, lmap = by_number(base), by_number(latest)


def spans(entries, chapter_ends):
    result = {}
    for chapter in (1, 2, 3, 4):
        sections = [e for e in entries if e["chapter"] == chapter and e["level"] == "section" and e["number"]]
        for i, entry in enumerate(sections):
            next_page = sections[i + 1]["page"] if i + 1 < len(sections) else chapter_ends[chapter]
            result[entry["number"]] = dict(start=entry["page"], next=next_page, span=next_page-entry["page"])
    return result


bs = spans(base, {1: 8, 2: 35, 3: 48, 4: 58})
ls = spans(latest, {1: 9, 2: 56, 3: 88, 4: 127})

# Chapter 1 was restructured: map by topic rather than the coincident number.
chapter1_mapping = [(["1.1"], "1.1"), (["1.2"], "1.2"),
                    (["1.3", "1.4"], "1.3"), (["1.6"], "1.4"),
                    (["1.5"], "1.5"), (["1.7"], "1.6")]
rows = []


def add_row(old, new, note=""):
    rows.append(dict(
        chapter=(new or old[0])["chapter"],
        level=(new or old[0])["level"],
        baseline_number=" / ".join(e["number"] for e in old),
        baseline_title=" / ".join(e["title"] for e in old),
        baseline_page=" / ".join(str(e["page"]) for e in old),
        latest_number=new["number"] if new else "",
        latest_title=new["title"] if new else "",
        latest_page=new["page"] if new else "",
        note=note,
    ))


for entry in latest:
    if entry["chapter"] == 1:
        if entry["level"] == "chapter":
            add_row([bmap["1"]], entry)
        else:
            old_numbers = next(old for old, new in chapter1_mapping if new == entry["number"])
            note = "Combined former aim/objectives and research-question sections" if entry["number"] == "1.3" else ""
            if entry["number"] == "1.4":
                note = "Former contributions section; methodology overview added"
            add_row([bmap[n] for n in old_numbers], entry, note)
    elif entry["number"]:
        old = bmap.get(entry["number"])
        note = "New numbered subsection; not necessarily wholly new content" if old is None else ""
        if entry["number"] == "4.1":
            note = "Broadened parent section; original title now appears at 4.1.1"
        if entry["number"] == "4.1.1":
            note = "Original 4.1 heading moved to this subsection"
        if entry["number"] in ("2.8.2", "2.8.3", "2.8.4"):
            note = "Same numbered slot, reframed scope; not a one-to-one paragraph correspondence"
        add_row([old] if old else [], entry, note)
    else:
        old = next(e for e in base if e["chapter"] == entry["chapter"] and e["level"] == entry["level"] and not e["number"])
        add_row([old], entry, "Unnumbered opening subtitle renamed")


def esc(text):
    return str(text).replace("|", "\\|")


def table(headers, records):
    return ["| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |"] + [
                "| " + " | ".join(esc(v) for v in record) + " |" for record in records]


chapter_rows = [
    ("Abstract", "i", 1, "1", 1, "+0"),
    ("1 Introduction", "1–7", 7, "2–8", 7, "+0"),
    ("2 Critical Literature Review", "8–34", 27, "9–55", 47, "+20"),
    ("3 Technical Foundations", "35–47", 13, "56–87", 32, "+19"),
    ("4 Research Design and Methodology", "48–57", 10, "88–126", 39, "+29"),
    ("Chapters 1–4 total", "1–57", 57, "2–126", 125, "+68"),
]
md = ["# Baseline versus latest Manav extract: contents comparison", "",
      "Verified against the compiled contents records and PDF destinations on 26 November 2026. Manuscript sources and PDFs were not changed.", "",
      "Baseline: preserved `baseline/LaTeX_Project` edition, compiled as [baseline main.pdf](../baseline_build/main.pdf). Latest: [Manav_review_Abstract_Chapters_1-4.pdf](../../Manav_review_Abstract_Chapters_1-4.pdf), 126 pages, after the one-page abstract layout correction.", "",
      "Page convention: baseline numbers are printed body pages (physical PDF page = body page + 11). Latest Manav numbers are both the printed and physical PDF pages. Its Abstract is page 1; Chapter 1 begins on page 2. Baseline front matter, contents, bibliography and later chapters are excluded from the chapter-length comparison.", "",
      "## Exact chapter page ranges", ""]
md += table(["Chapter", "Baseline pages", "Count", "Latest Manav pages", "Count", "Added pages"], chapter_rows)
md += ["", "The chapters grew from 57 to 125 pages (+68, approximately 119%). The latest extract is 126 pages including its one-page Abstract. Chapter 4 accounts for 29 of the added pages; Chapters 3 and 4 together account for 48 (71%).", "",
       "## Main-section index and distribution of growth", "",
       "Start pages are exact. The span columns count from a heading's starting page to the next numbered main section's starting page (or the next chapter). They show where pagination expands, not exact text occupancy: adjacent sections can share a page, and a span of zero does not mean an absent or empty section. Figures and tables that float across a heading boundary can also affect this attribution. The final Chapter 4 boundary is one past the extract's last page (127).", ""]

growth = []
for chapter in (1, 2, 3, 4):
    md += [f"### Chapter {chapter}", ""]
    selected = [r for r in rows if r["chapter"] == chapter and r["level"] == "section" and r["latest_number"]]
    if chapter == 1:
        md += table(["Baseline section", "Baseline start", "Latest section", "Manav start"], [
            (r["baseline_number"] + " " + r["baseline_title"], r["baseline_page"],
             r["latest_number"] + " " + r["latest_title"], r["latest_page"]) for r in selected])
    else:
        data = []
        for r in selected:
            num = r["latest_number"]
            b, l = bs[num], ls[num]
            delta = l["span"] - b["span"]
            growth.append(dict(number=num, title=r["latest_title"], baseline_start=b["start"],
                               latest_start=l["start"], baseline_span=b["span"], latest_span=l["span"], delta=delta))
            data.append((num + " " + r["latest_title"], b["start"], l["start"],
                         f'{b["span"]} → {l["span"]}', f"{delta:+d}"))
        md += table(["Section (latest wording)", "Baseline start", "Manav start", "Boundary span B → M", "Change"], data)
    md.append("")

assert sum(g["delta"] for g in growth if g["number"].startswith("2.")) == 20
assert sum(g["delta"] for g in growth if g["number"].startswith("3.")) + 1 == 19
assert sum(g["delta"] for g in growth if g["number"].startswith("4.")) == 29

md += ["## Largest expanded blocks", ""]
md += table(["Section", "Baseline start → next heading", "Manav start → next heading", "Added boundary span"], [
    (g["number"] + " " + g["title"], f'{g["baseline_start"]} → {g["baseline_start"]+g["baseline_span"]}',
     f'{g["latest_start"]} → {g["latest_start"]+g["latest_span"]}', f'+{g["delta"]}')
    for g in sorted(growth, key=lambda g: -g["delta"])[:10]])
md += ["", "Chapter 2 §2.8 alone accounts for 10 of that chapter's 20 added boundary pages. Chapter 3 §3.5 accounts for 7 of its 19 added pages. One additional Chapter 3 page precedes §3.1. Chapter 4 keeps its 11 main sections but now has 30 numbered subsections, compared with none in the baseline.", "",
       "## Complete side-by-side contents, including subsections", "",
       "Chapter 1 is matched by topic because its numbering changed. Elsewhere, corresponding numbers are aligned; changed titles and newly numbered subsections are shown explicitly. A new subsection heading does not prove that all of its material was absent from the baseline.", ""]
for chapter in (1, 2, 3, 4):
    md += [f"### Chapter {chapter}: full index", ""]
    data = []
    for r in rows:
        if r["chapter"] != chapter:
            continue
        old = (r["baseline_number"] + " " + r["baseline_title"]).strip() or "—"
        new = (r["latest_number"] + " " + r["latest_title"]).strip()
        data.append((old, r["baseline_page"] or "—", new, r["latest_page"], r["note"]))
    md += table(["Baseline entry", "Page", "Latest Manav entry", "Page", "Mapping note"], data) + [""]

# These unnumbered subheadings are visible in the PDF but not in its contents records.
supplement = [
    ("R1. Target validity and modality correspondence", None, 46),
    ("R2. Representation suitability under explicit fitting conditions", None, 46),
    ("R3. Incremental fusion value under comparable experimental conditions", None, 47),
    ("R4. Reliability-aware comparison of fusion mechanisms", None, 47),
    ("R5. Methodological validity and bounded cross-dataset interpretation", None, 48),
    ("PHM gear monitoring", 32, 50),
    ("REASSEMBLE robotic assembly", 33, 51),
    ("MSM milling", 33, 52),
    ("ViFailback manipulation", 34, 52),
    ("HANDOVER human–robot interaction", 34, 53),
]
for heading, _, page in supplement:
    assert heading in latest_reader.pages[page - 1].extract_text(), (heading, page)
md += ["## Additional visible Chapter 2 subheadings", "",
       "The latest PDF does not register these starred subheadings in the contents. The five study-specific headings had paragraph entries in the baseline contents. Page locations below were checked directly in the latest PDF text. Dashes mean there is no corresponding standalone baseline heading, not necessarily no related discussion.", ""]
md += table(["Heading (shortened for study names)", "Baseline page", "Manav page"],
            [(h, b or "—", l) for h, b, l in supplement])
md += ["", "## Reading the result", "",
       "The additional length is concentrated in expanded synthesis, model explanations and shared methodology. Chapter 1 has the same page count. Start-page shifts alone are not section growth: later sections inherit all expansion before them. Use the chapter totals and heading-boundary spans above to separate those effects.", "",
       "This is a pagination and contents comparison, not a judgement that every added page should be removed. No thesis text, figures, layout or PDF was edited for this comparison.", ""]

(OUT / "Baseline_vs_Manav_Index_Comparison.md").write_text("\n".join(md))
with (OUT / "Baseline_vs_Manav_Index_Comparison.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

inputs = [BASE_TOC, LATEST_AUX, BASE_PDF, LATEST_PDF]
for edition in ("baseline", "working"):
    inputs += [REVISION / edition / "LaTeX_Project" / "chapters" / name for name in
               ("01_introduction.tex", "02_literature_review.tex", "03_foundations.tex", "04_methodology.tex")]
provenance = dict(
    created_utc=datetime.now(timezone.utc).isoformat(),
    git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    command="ma_thesis_env/bin/python " + str(Path(__file__).resolve().relative_to(REPO)),
    inputs=[dict(path=str(p.relative_to(REPO)), sha256=digest(p)) for p in inputs],
    baseline_body_pdf_offset=11,
    latest_pages=len(latest_reader.pages),
    index_entries_verified_against_pdf_destinations=len(verified),
    verified_entries=verified,
    new_chapter4_subsections=sum(e["chapter"] == 4 and e["level"] == "subsection" for e in latest),
    section_boundary_growth=growth,
    scope="Contents/PDF inspection only. No source, figure or manuscript PDF changed.",
)
(OUT / "validation.json").write_text(json.dumps(provenance, indent=2) + "\n")
print(json.dumps(dict(chapter_pages_baseline=57, chapter_pages_latest=125,
                      added_chapter_pages=68, latest_extract_pages=126,
                      indexed_entries_verified=len(verified), comparison_rows=len(rows),
                      output=str(OUT.relative_to(REPO))), indent=2))
