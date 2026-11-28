# Thesis project for chapter-by-chapter review

Open any PDF in `chapter-pdfs/` to read that chapter as typeset in the review edition. These ten PDFs can be read on their own and do not require changing the project or compiling LaTeX. Their printed page numbers match the review PDF, which begins with the abstract on page 1. Recreate these PDF snapshots when preparing a new review edition.

The editable chapter sources are under `chapters/`. To preview edits to one chapter, choose XeLaTeX and `chapter-preview.tex` as the main document, set the chapter number on line 3, and recompile. The complete edition and the abstract-through-conclusion edition can also be built from this project.


Use XeLaTeX in Overleaf. The project has three main-document choices.

| Main document | Pages included |
| --- | --- |
| `main.tex` | Complete edition with title, abstract, contents, Chapters 1–10, disclosure, APA references and all appendices. |
| `review.tex` | Review draft starting with the abstract as page 1 and ending at the last paragraph of Chapter 10. Chapters, tables and figures present in the review copy are linked. Cross-references to omitted appendices use their full-edition numbers as plain text. |
| `chapter-preview.tex` | Fast preview of one chapter. Set the value of `\PreviewChapter` on line 3 to a number from 1 to 10. |

Edit the abstract in `frontmatter/abstract.tex` and chapters in `chapters/`. Both full and review builds read these same files. The chapter preview caches APA citation forms and cross-reference numbers for fast editing. Use a full XeLaTeX and Biber build to check new citations or numbering changes. The production PDFs have a DRAFT watermark controlled by `\thesisdrafttrue` in `main.tex`; the single-chapter preview has its own switch.

For a local full build, run `latexmk -xelatex main.tex`. For the abridged edition, run `latexmk -xelatex review.tex`. Each edition uses a separate job name and automatically runs Biber as needed. The full build prints the references. The abridged build keeps the same author–date forms in the body.

Appendix F in the complete edition identifies the project evidence files. Add each published GitHub file permalink between the vertical bars at the end of its row in `tables/evidence_register.tex`. A cited file with an empty field produces no footnote; a populated file produces a clickable filename.

The full manuscript prints the AI Assistance Disclosure after Chapter 10 and before References. Edit it in `appendices/I_ai_assistance.tex`. The review PDF ends at Chapter 10.
