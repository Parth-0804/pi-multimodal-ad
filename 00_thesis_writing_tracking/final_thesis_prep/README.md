# Final thesis preparation

Prepared on 27 November 2026 from the current working-tree manuscript in
`00_thesis_writing_tracking/Thesis/LaTeX_Project`, including its uncommitted edits.
This is the requested preparation copy for a new chat. Existing repository
navigation still identifies the original project as the canonical manuscript;
creating this folder does not change that navigation or approve the thesis.

## Start here

- [Complete thesis source](LaTeX_Project/main.tex): all ten chapters, abstract,
  references, appendices and supporting figures are in this project.
- [New-chat handoff](NEW_CHAT_HANDOFF.md): current entry points, known issues and
  a suggested first message.
- [Copy manifest](COPY_MANIFEST.json): original paths, sizes and SHA-256 hashes
  for every copied file, plus the source Git revision.
- [Initial copy validation](VALIDATION.json): copy integrity and static dependency checks
  recorded before the front-matter update.
- [Front-matter update](changes/frontmatter_20261127_01/README.md): supplied title
  page and declaration, acknowledgements, integration diff and build checks.
- [Source Git status](SOURCE_GIT_STATUS.txt): changes already present before copying.

`LaTeX_Project/` includes all source and supporting files outside `build/` and
`chapters_pdfs/`, including editable figures, bibliographies, evidence/literature
CSV indexes, style files, build configuration and project instructions. Draft
figure assets retain their existing names and status; they are not newly approved
for use. `context/` contains selected dated writing/review records.

The initial copy identities are preserved in `COPY_MANIFEST.json`. The prepared
`main.tex` now includes the supplied front matter; its before/after identities are
recorded in the front-matter update. Original source files remain unchanged.
The copied project README, context notes,
scripts and evidence indexes retain their original wording and original path
conventions. For inherited links outside the copied project, use the original
source path in the manifest; the links in this README and the handoff are the
navigation for this preparation folder. Copied historical instructions and saved
commands do not authorize new experiments or overwrite current repository policy.

## Build

From the repository root, with an available XeLaTeX/Biber/latexmk toolchain:

```bash
cd 00_thesis_writing_tracking/final_thesis_prep/LaTeX_Project
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build/final_prep main.tex
```

The initial copy task did not compile the thesis. The later front-matter update
records its own compilation and preview checks in the linked update report. The
[current compiled PDF](LaTeX_Project/build/frontmatter_20261127_01/main.pdf)
has 194 pages. Older
PDFs must not be treated as renderings of the current prepared source. The DRAFT
watermark remains enabled. The supplied title page and declaration retain their
`xx November 2026` submission/signing placeholders; fill those before submission.

The full edition uses this order: title page, declaration, abstract,
acknowledgements, contents, lists of figures/tables, then Chapters 1–10.
The declaration is unnumbered; Roman page numbering starts at the abstract.
Acknowledgements appear in the contents. The review editions keep their existing
abstract/chapter scope. This ordering is an editorial choice, not a verified
university requirement. The current abstract leaves its keywords on a second
page; this inherited layout issue is recorded for the final editing pass.

## Repository evidence and boundaries

Use the current [repository instructions](../../AGENTS.md),
[thesis-to-code map](../../docs/THESIS_CODE_MAP.md),
[data boundaries](../../docs/data_boundaries.md),
[output policy](../../docs/output_policy.md) and
[active scope](../../docs/active_scope.md). Experiment artifacts remain in their
existing locations; no datasets, environments, checkpoints or downloaded
publications were copied. Nothing was staged, committed or pushed.
