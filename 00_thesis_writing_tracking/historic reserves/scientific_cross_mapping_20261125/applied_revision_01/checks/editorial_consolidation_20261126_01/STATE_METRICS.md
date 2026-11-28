# Editorial and formatting state measurements

A = unchanged November 26 source; B = consolidated Chapters 3–4 with A formatting; C = the same consolidated chapter text with central formatting changes.

All page counts below come from the rebuilt PDFs. Chapter ranges use PDF named destinations, cross-checked against TOC-only AUX entries and PDF printed page labels. Counts include figures, tables and any page space up to the next chapter; they are exact pagination spans, not estimates of prose occupancy.

## PDF totals

| Edition | A | B | C | Saved by consolidation (A−B) | Additional saved by formatting (B−C) |
|---|---:|---:|---:|---:|---:|
| Full manuscript | 275 | 256 | 199 | 19 | 57 |
| Review edition, Abstract + Chapters 1–10 | 205 | 186 | 142 | 19 | 44 |
| Manav, Abstract + Chapters 1–4 | 126 | 107 | 82 | 19 | 25 |

## Chapter pages in the full manuscript

Printed starts are the page numbers shown in the thesis. Physical ranges are PDF viewer pages. States A and B retain the existing two-page Abstract in the full/review editions and the previously approved one-page Manav Abstract. State C uses the shared compact heading across all editions; the Abstract wording is unchanged.

| Part | A: printed start; PDF range; count | B: printed start; PDF range; count | C: printed start; PDF range; count | A−B | B−C |
|---|---|---|---|---:|---:|
| Abstract | i; 2–3; **2** | i; 2–3; **2** | i; 2–2; **1** | 0 | 1 |
| Chapter 1 | 1; 15–21; **7** | 1; 15–21; **7** | 1; 14–19; **6** | 0 | 1 |
| Chapter 2 | 8; 22–68; **47** | 8; 22–68; **47** | 7; 20–55; **36** | 0 | 11 |
| Chapter 3 | 55; 69–100; **32** | 55; 69–95; **27** | 43; 56–75; **20** | 5 | 7 |
| Chapter 4 | 87; 101–139; **39** | 82; 96–120; **25** | 63; 76–94; **19** | 14 | 6 |
| Chapter 5 | 126; 140–152; **13** | 107; 121–133; **13** | 82; 95–104; **10** | 0 | 3 |
| Chapter 6 | 139; 153–176; **24** | 120; 134–157; **24** | 92; 105–122; **18** | 0 | 6 |
| Chapter 7 | 163; 177–187; **11** | 144; 158–168; **11** | 110; 123–131; **9** | 0 | 2 |
| Chapter 8 | 174; 188–198; **11** | 155; 169–179; **11** | 119; 132–139; **8** | 0 | 3 |
| Chapter 9 | 185; 199–212; **14** | 166; 180–193; **14** | 127; 140–150; **11** | 0 | 3 |
| Chapter 10 | 199; 213–217; **5** | 180; 194–198; **5** | 138; 151–154; **4** | 0 | 1 |

Chapter 10 ends before the following **AI Assistance Disclosure**. The disclosure, bibliography, appendices and frontmatter are included in the full-PDF total but are not assigned to Chapter 10. The JSON lists their separate TOC-based boundaries.

## Manav chapter ranges

| Part | A: printed/PDF range; pages | B: printed/PDF range; pages | C: printed/PDF range; pages |
|---|---|---|---|
| Abstract | 1–1; **1** | 1–1; **1** | 1–1; **1** |
| Chapter 1 | 2–8; **7** | 2–8; **7** | 2–7; **6** |
| Chapter 2 | 9–55; **47** | 9–55; **47** | 8–43; **36** |
| Chapter 3 | 56–87; **32** | 56–82; **27** | 44–63; **20** |
| Chapter 4 | 88–126; **39** | 83–107; **25** | 64–82; **19** |

## Source words and headings

Approximate source-word tokens, calculated identically for A/B/C. Expand local input/include files; remove comments, inline/display mathematics, equation/align/verbatim/code environments, citation and cross-reference arguments, EvidenceRef calls, graphic paths and layout arguments. Retain ordinary prose, headings, captions, display notes and table-cell text. Replace ReviewWorkCount by its source-defined number. Count Unicode letter/number sequences with internal apostrophes, hyphens or decimal punctuation as single tokens. This is a consistent approximation, not a formal natural-language word count; source paths/identifiers in visible text can contribute tokens. Abstract counts exclude the root-file keywords.

Columns ‘sections/subsections’ count numbered source commands. Other heading types are separately retained in the JSON. B and C have identical chapter/Abstract source hashes, word counts and heading counts.

| Part | A approximate words | B approximate words | C approximate words | A sections/subsections | B sections/subsections | C sections/subsections |
|---|---:|---:|---:|---:|---:|---:|
| Abstract | 252 | 252 | 252 | 0/0 | 0/0 | 0/0 |
| Chapter 1 | 1622 | 1622 | 1622 | 6/0 | 6/0 | 6/0 |
| Chapter 2 | 10691 | 10691 | 10691 | 8/37 | 8/37 | 8/37 |
| Chapter 3 | 7272 | 5796 | 5796 | 6/20 | 6/19 | 6/19 |
| Chapter 4 | 8388 | 5917 | 5917 | 11/30 | 11/7 | 11/7 |
| Chapter 5 | 3045 | 3045 | 3045 | 10/9 | 10/9 | 10/9 |
| Chapter 6 | 6058 | 6058 | 6058 | 10/28 | 10/28 | 10/28 |
| Chapter 7 | 2592 | 2592 | 2592 | 8/4 | 8/4 | 8/4 |
| Chapter 8 | 2729 | 2729 | 2729 | 9/5 | 9/5 | 9/5 |
| Chapter 9 | 3566 | 3566 | 3566 | 8/0 | 8/0 | 8/0 |
| Chapter 10 | 1312 | 1312 | 1312 | 4/0 | 4/0 | 4/0 |

Source hashes identify exactly which files were measured. Source-word totals include only the named Abstract/chapter files, not the bibliography, root keywords or appendices. Formatting-only pagination changes in protected chapters do not indicate textual changes.

## Measurement provenance

`state_metrics.json` records input PDF/AUX hashes, source hashes, every chapter destination and its printed and physical boundaries. This helper reads existing builds and never compiles, modifies manuscript sources, or runs experiments.

Generated at 2026-11-26T02:50:52.457821+00:00.
