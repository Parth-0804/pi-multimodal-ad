# Chapter 3 workflow delivery

The five pages of the supplied `Chapter_3_fusion_workflows.pdf` are included unchanged in the working LaTeX source and source ZIP. They appear under §§3.5.1–3.5.5 as Figures 3.3–3.7 on Manav pages 52–56. The existing overview is kept before the PHM subsection. F1 and F2 now have separate subsections, matching the supplied workflow sequence.

Only `chapters/03_foundations.tex` and the working `README.md` changed among pre-existing working files. The five-page PDF is the sole new source asset. All 57 original body paragraphs, 18 citation commands, nine evidence references, three equations, three tables and original labels are retained. Caption notes distinguish engineered PHM predictor inputs from photographic targets, fold-specific F2 fitting, and the anchored clean comparison from missing-input fallback.

## Builds and checks

- Manav: 71 pages. Complete review: 131 pages. Full thesis: 187 pages.
- No unresolved citations/references, Biber warnings, duplicate labels, missing glyphs or overfull boxes. Both review editions have no LaTeX warnings. The full thesis retains the pre-existing Appendix F caption/hypcap warning.
- Standalone workflow pages and final manuscript pages 50–59 rendered at 150 dpi and visually inspected; all five diagrams, captions, notes and arrows are readable and unclipped.
- The supplied PDF's visible text uses embedded Latin Modern fonts; an unused Helvetica resource is retained without changing the supplied artwork.
- Abstract and Chapters 1–2 match the preceding review's first 43 pages. All 71 Manav pages match the corresponding complete-review pages. Chapters 1–4 match the full thesis after footer normalization.
- The 72-file source ZIP passes integrity and byte-for-byte working-source checks, and includes every local input recorded by the three builds.

[Validation](final_validation.json), [source preservation](source_verification.json), [PDF consistency](pdf_consistency.json), [figure page mapping](workflow_pages.json), [source diff](chapter3_workflows.patch).

The preceding PDFs, ZIP and affected source files are retained in `before/`. No experiment, dependency installation, commit or push was performed. Existing scientific and citation-review limitations remain unchanged.

Git checks: the literal `git diff --check` flags retained CRLF line endings in the existing dirty tree. The check with `core.whitespace=cr-at-eol` passes across the full tree. The scoped check passes. Git status and check outputs are preserved alongside these notes.
