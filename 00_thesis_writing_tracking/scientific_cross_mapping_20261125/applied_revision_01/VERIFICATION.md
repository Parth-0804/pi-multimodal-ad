# Chapter 3 workflow insertion — 26 November 2026

Five supplied workflows are placed under §§3.5.1–3.5.5, as Figures 3.3–3.7 on Manav pages **52–56**. Captions, labels and prose references were added. Existing Chapter 3 body paragraphs, equations, tables, citations and evidence links are preserved; the overview now precedes the subsections. Abstract and Chapters 1–2 and 4–10 are unchanged.

Current PDFs: **Manav 71 pages; Chapters 1–10 review 131; full thesis 187**. The refreshed ZIP contains **72 source/assets files**. [Delivery notes](checks/ch3_workflows_20261126_01/DELIVERY_NOTES.md), [source diff](checks/ch3_workflows_20261126_01/chapter3_workflows.patch), [validation](checks/ch3_workflows_20261126_01/final_validation.json). The previous delivery is preserved in [before/](checks/ch3_workflows_20261126_01/before/).

The following entries are historical; their page counts describe earlier versions.

---

# Latest author-chapter delivery — 26 November 2026

The supplied Chapters 3–4 are integrated into the 67-page Manav review. The refreshed full thesis has 183 pages and the Chapters 1–10 review 127. The 71-file source ZIP matches the compiled inputs. [Current changes and checks](checks/manav_author_ch34_20261126_01/DELIVERY_NOTES.md), [source diff](checks/manav_author_ch34_20261126_01/author_ch34_revision.patch), [validation](checks/manav_author_ch34_20261126_01/final_validation.json).

The earlier material below describes the preceding delivery. Its former page counts are retained as history; use the current README and linked checks for this version.

# Latest editorial consolidation verification — 26 November 2026

Current PDFs: **Manav 82 pages; Chapters 1–10 review 142; full thesis 199**. The unchanged current source was preserved before editing. Editorial consolidation alone saved 19 pages; formatting saved 25 further Manav pages and 57 further full-thesis pages. Only Chapters 3–4 underwent textual consolidation; 90 other source/assets files are unchanged.

[Final report](checks/editorial_consolidation_20261126_01/CONSOLIDATION_REPORT.md), [measurements](checks/editorial_consolidation_20261126_01/STATE_METRICS.md), [wording preservation](checks/editorial_consolidation_20261126_01/WORDING_PRESERVATION.md) and [separate diffs](checks/editorial_consolidation_20261126_01/combined_A_to_C.patch) document the scope. All nine builds passed. No unresolved citations/references or Biber warnings; the full edition retains its pre-existing appendix caption/hypcap warning. The 71-file source ZIP and reversible patches reconstruct exactly. University formatting approval remains unverified.

The records below describe earlier deliveries and retain their historical scope and page numbers. Their PDFs and source archive are preserved in [state_A](checks/editorial_consolidation_20261126_01/state_A/).

---

# Latest Manav abstract layout check

The current Manav PDF has **126 pages**. Its centered Abstract heading was moved upward locally; all unchanged abstract text and keywords now fit on page 1. Chapter 1 starts on page 2. All 125 chapter pages retain their prior extracted content after footer renumbering. The two opening pages were rendered at 150 dpi and opened; no clipping or overlap was observed. XeLaTeX/Biber completed without warnings or unresolved citations/references. Font size and double spacing remain unchanged.

Only `manav_review.tex` changed among the 70 packaged source/assets files. The source ZIP and cumulative patch were refreshed and verified. The full and Chapters 1–10 editions retain their prior layout. [Current validation](checks/manav_abstract_layout_20261126_01/validation.json) and [preserved previous files](checks/manav_abstract_layout_20261126_01/before/) document this local follow-up. No new commit or push was made.

The earlier diagram-delivery record below describes the pre-layout, 127-page Manav edition. Its scientific and source checks retain their original scope; diagram page numbers in that edition are one greater than in the current PDF.

---

# Current diagram delivery verification — 26 November 2026

[Validation record](checks/manav_explanatory_diagrams_20261126_01/validation.json) covers the current PDFs and 70-file source ZIP. The previous delivery files are preserved in [before/](checks/manav_explanatory_diagrams_20261126_01/before/).

All three editions were rebuilt successfully with the existing authorized XeLaTeX/TeX Live 2023, Biber 2.19 and latexmk 4.83 toolchain. Manav's Abstract–Chapter 4 PDF is 127 pages, the Chapters 1–10 review is 205, and the full thesis is 275. There are no unresolved citations/references, Biber warnings/errors, duplicate-label warnings, overfull boxes or missing characters. Both review editions have no LaTeX warnings. The full edition retains its pre-existing appendix caption/hypcap warning. All PDF fonts are embedded.

The three explanatory figures and supplied redesign are vector PDFs with no raster objects. All use the existing shared thesis style and a 159.20 mm canvas width. Standalone previews and final manuscript pages were rendered at 150 dpi and opened. The requested pages are 19, 69 and 104; the redesigned synthesis and scope table are on pages 55 and 51. Labels, arrows, hatching, patch overlap, stride, bank-reuse note and assessment separation are readable without clipping or overlap. These checks do not constitute a page-by-page visual audit of the thesis.

The 108-key APA citation context agrees across all three Biber files. All 127 Manav text pages match the start of the complete review edition, and the final Chapter 4 paragraph is intact. Omitted material retains plain full-edition reference numbers. The original synthesis label and the supplied alias identify the same Figure 2.2.

The supplied redesign source is unchanged from the ZIP. Its rebuilt PDF has the same extracted text as the supplied PDF. Its welding values agree with the existing Chapter 2 and previous source-PDF checks: P003 Table III, and Hua Tables 1–3. No new literature discovery or experimental execution was performed. Early warning remains hypothetical and the sensor trace synthetic.

A separate source-delta review reconstructed the before Chapters 2–4 after removing only the authorized figure additions, references, supplied paragraph/table and synthesis replacement. All other content matches byte-for-byte. The established integrity checker flags those intentional figure, numeric and reference additions as review required; this is not a zero-change integrity pass. [Integration review](checks/manav_explanatory_diagrams_20261126_01/integration_review.md) records the reconciliation.

The source ZIP passes integrity checks and matches all 70 fixed source/assets files byte-for-byte. The cumulative binary patch passes `git apply --check` and reconstructs those files exactly from a temporary baseline. All 56 original and preserved baseline files remain unchanged. Local build directories and historical chapter PDFs are excluded from the source package and publication staging.

Earlier scientific and citation limits remain in the [prior verification](checks/manav_explanatory_diagrams_20261126_01/before/VERIFICATION.md) and [Chapter 1–2 citation record](checks/citation_review_ch01_ch02_20261126_01/CHANGELOG.md), including export-based Zotero provenance and the two pending Chapter 2 wording decisions. Those passages were not silently revised during this figure task. No training, inference, fitting, dependency installation or raw-data processing occurred.
