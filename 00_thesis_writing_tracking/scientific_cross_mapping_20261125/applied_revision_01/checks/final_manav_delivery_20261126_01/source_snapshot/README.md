# Thesis project for chapter-by-chapter review

Updated 26 November 2026 with the author's Abstract and Chapters 1–4, the Chapter 1–2 citation corrections, and the integrated figures and tables. The accompanying delivery package contains the full thesis, the abstract-through-conclusion edition, and `Manav_review_Abstract_Chapters_1-4.pdf`.

Use XeLaTeX and Biber. All editions read the same chapter sources.

| Main document | Contents |
| --- | --- |
| `main.tex` | Complete thesis: title, abstract, contents, Chapters 1–10, disclosure, references and appendices. |
| `review.tex` | Abstract followed by Chapters 1–10. |
| `manav_review.tex` | Manav's review copy: Abstract followed by Chapters 1–4 only. |
| `chapter-preview.tex` | One-chapter editing preview; set `\PreviewChapter` on line 3. Its cached citation forms require a full build after citation changes. |

From this directory, run `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`, substituting `review.tex` or `manav_review.tex` for either review edition. Select the same root and XeLaTeX in Overleaf. Biber runs automatically through latexmk.

Edit `frontmatter/abstract.tex` and `chapters/`. The full manuscript prints the bibliography; both review copies retain author–date citations without a reference list. Omitted appendix/chapter references use plain full-edition numbers. Manav's generated root retains the full citation context for consistent APA disambiguation; regenerate it from `main.tex` if its preamble or shared citation context changes.

Chapter 2 includes the literature synthesis table and current vector synthesis diagram. Chapter 3 includes three comparison tables and the fusion-interface figure; Chapter 4 includes the research-workflow figure. Unselected diagrams under `figures/draft_chapters_01_02/` remain drafts and are excluded from the delivery source ZIP. The date-free draft Figure 3 is preserved separately.

The DRAFT watermark remains controlled by `\thesisdrafttrue` in `main.tex` and in the Manav root. Historical chapter PDFs remain in the unchanged baseline and are excluded from this package. Appendix F and `tables/evidence_register.tex` retain the evidence index; empty publication URL fields remain empty rather than inventing links. The disclosure is in `appendices/I_ai_assistance.tex`.
