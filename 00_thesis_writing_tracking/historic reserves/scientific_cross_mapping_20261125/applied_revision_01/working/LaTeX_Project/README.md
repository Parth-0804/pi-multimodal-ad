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

Chapter 2 includes the literature synthesis table, the supplied welding-to-requirements diagram and five-study scope table. Three explanatory diagrams are added by section heading: prediction availability (§2.2.4), overlapping sensor patches (§3.3) and the stacker recording flow (§4.6.2). Chapter 3 retains its three comparison tables and fusion-interface overview. Five supplied vector workflows are placed under §§3.5.1–3.5.5: PHM feature concatenation, F1 equal averaging, F2 logistic stacking, context-based gating and anchored adjustment. The unchanged five-page source is included as `figures/fusion_workflows_20261126.pdf`. Chapter 4 retains the research-workflow figure. Editable figures and build details are documented in `figures/review_explanatory_20261126/README.md`. Unselected diagrams under `figures/draft_chapters_01_02/` remain drafts and are excluded from the delivery source ZIP. The date-free draft Figure 3 is preserved separately.

The DRAFT watermark remains controlled by `\thesisdrafttrue` in `main.tex` and in the Manav root. Historical chapter PDFs remain in the unchanged baseline and are excluded from this package. Appendix F and `tables/evidence_register.tex` retain the evidence index; empty publication URL fields remain empty rather than inventing links. The disclosure is in `appendices/I_ai_assistance.tex`.
