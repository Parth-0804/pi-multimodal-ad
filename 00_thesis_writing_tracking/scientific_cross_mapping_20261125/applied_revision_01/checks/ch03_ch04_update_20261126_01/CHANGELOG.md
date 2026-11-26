# Chapters 3–4 update — 26 November 2026

Applied the two supplied chapter files to the active `working/LaTeX_Project` manuscript. The author's rewritten structure and prose are retained. The previous versions and exact submitted files are preserved in `before/` and `submitted/`.

Changed manuscript files:

- `chapters/03_foundations.tex`: replaced with the supplied “Technical Foundations and Possible Models.”
- `chapters/04_methodology.tex`: replaced with the supplied “Research Design and Shared Methodology.”
- `appendices/F_reproducibility.tex`: corrected one stale coverage statement and added its existing evidence references.

This task changed only the three files above. The registered title, `main.tex`, abstract, Chapter1, Chapters5–10 and bibliography remain unchanged. A separate concurrent update changed Chapter2’s synthesis-figure source/PDF and its note; those changes were preserved and included in the builds. The document snapshot used for the deliverables records them in `concurrent_sources_at_snapshot.json`. The original baseline remains unchanged.

## Small repairs to the submitted text

The exact repairs are in [submitted_text_repairs.patch](submitted_text_repairs.patch) and [local_repairs.json](local_repairs.json).

- Reused the verified existing `Ting1999Issues` key in both chapters in place of the unresolved `Ting1999StackedGeneralization`. No reference was added.
- Restored `EvidenceRef` commands for E112/E114 in Chapter3 and E113/E115/E116 in Chapter4. Retained the existing precise E019 and E004 implementation locators.
- Defined the logit and the symbols used in the three retained fusion equations. The equations themselves, their labels and coefficients were not changed.
- Typeset the unchanged source commit as code.
- Added one local page-height adjustment to prevent a single closing line of Chapter4 spilling onto an otherwise empty page.
- Retained the workflow figure's existing clarification that Intel holdout exposure arose from earlier context work, rather than a new trained-model test in the foundation review.

AppendixF had still excluded FULL20 and FULL100 entirely. The narrow correction now includes the completed one-fold FULL20 comparison and FULL100 pilot while keeping the remaining FULL20 fits and corruption tests unfinished. The November24 E115 completed-scope report and E116 closure record were read directly for this correction. This was documentary checking; no training, inference or new result analysis was run.

## Figures and the Manav review

The current Chapter2 synthesis diagram is retained. The supplied Chapter3 fusion-interface figure and Chapter4 research-workflow figure use their existing assets. The optional Chapter1/2 draft figures remain separate; the date-free draft Figure3 is unchanged.

[Manav review: Abstract + Chapters1–4](Manav_review_Abstract_Chapters_1-4.pdf) uses the same chapter sources, preamble and review settings as the manuscript. Its generated root [manav_review.tex](source_snapshot/manav_review.tex) is a derivative of the unchanged `main.tex`; no new manuscript workflow was introduced. References to omitted chapters/appendices render as plain numbers. The full manuscript's citation context is retained for consistent APA author/year disambiguation. The excerpt ends after Chapter4.

The full and existing Chapters1–10 review editions were also rebuilt. Final PDFs are in `final_full_build/main.pdf` and `final_review_build/review.pdf`. Because Chapter2 and its diagram were changing concurrently, the final editions compile the fixed `source_snapshot/` documented in `snapshot_manifest.json`. The initial live-source builds remain as intermediate records. The [updated source archive](updated_LaTeX_Project.zip) contains this compilable snapshot. Older top-level delivery PDFs/archives were not overwritten.

## Checks

All36 citation commands in Chapters3–4 resolve, as do their cross-references. No duplicate labels were found in the actual manuscript input graph. The three new Chapter3 tables, three displayed equations and figure environment match the submission exactly. The independent preservation check is in [final_source_review.md](final_source_review.md).

The established integrity checker was run against both the submitted files and previous working versions. Its review flags cover the author's intended replacement and the recorded citation, notation and evidence repairs. The full manuscript diff is [chapter_update.patch](chapter_update.patch). Compilation results, PDF hashes and rendered-page checks are recorded in [validation.json](validation.json).

Final builds: full thesis272pages, Chapters1–10 review202pages, Manav excerpt124pages. All108 bibliography keys in the common citation context resolve. Final logs contain no unresolved citations/references, Biber warnings/errors, overfull boxes or missing characters. The full edition retains the pre-existing appendixD caption warning; both review editions have no warnings. The final closing page and retained figures were opened as previews; AppendixF’s corrected paragraph was also inspected in the full PDF.

The final live-file check confirms that Chapter2 and its synthesis-figure source/PDF match the captured review packet.
