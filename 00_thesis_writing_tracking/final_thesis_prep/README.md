# Final thesis preparation

Prepared on 27 November 2026 from the current working-tree manuscript in
`00_thesis_writing_tracking/Thesis/LaTeX_Project`, including its uncommitted edits.
Since the researcher-authorized cleanup on 28 November 2026, this is the sole active
manuscript. Use `LaTeX_Project/main.tex`; earlier review/preview roots and redundant
loose manuscript copies were removed. Figure sources and supporting assets remain.
Source promotion does not imply thesis approval or a new compiled PDF.

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
- [Source cleanup record](SOURCE_CLEANUP_20261128.json): removed paths and hashes,
  checkpoint recovery for 423 files, and the separate local archive for 11 ignored files.

`LaTeX_Project/` includes all source and supporting files outside `build/` and
`chapters_pdfs/`, including editable figures, bibliographies, evidence/literature
CSV indexes, style files, build configuration and project instructions. Draft
figure assets retain their existing names and status; they are not newly approved
for use. `context/` contains selected dated writing/review records.

The initial copy identities are preserved in `COPY_MANIFEST.json`. The prepared
`main.tex` now includes the supplied front matter; its before/after identities are
recorded in the front-matter update. The initial copy left original files unchanged;
later source edits and cleanup have their own scope. Dated context notes, scripts and
evidence indexes retain their original path conventions. For inherited links outside the copied project, use the original
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
[front-matter build recorded on 27 November](LaTeX_Project/build/frontmatter_20261127_01/main.pdf)
had 194 pages. It predates later source edits and must not be treated as a rendering
of the current manuscript. The DRAFT
watermark remains enabled. The supplied title page and declaration retain their
`xx November 2026` submission/signing placeholders; fill those before submission.

The full edition uses this order: title page, declaration, abstract,
acknowledgements, contents, lists of figures/tables, then Chapters 1–10.
The declaration is unnumbered; Roman page numbering starts at the abstract.
Acknowledgements appear in the contents. This ordering is an editorial choice, not a
verified university requirement. The 27 November front-matter build placed the keywords
on a second abstract page; its layout observation is historical until a new build.

## Repository evidence and boundaries

Use the current [repository instructions](../../AGENTS.md),
[thesis-to-code map](../../docs/THESIS_CODE_MAP.md),
[data boundaries](../../docs/data_boundaries.md),
[output policy](../../docs/output_policy.md) and
[active scope](../../docs/active_scope.md). Experiment artifacts remain in their
existing locations; no datasets, environments, checkpoints or downloaded
publications were copied in the initial preparation task. Recovery of removed loose
manuscript files is documented in the [current state](../Thesis/revision_pipeline/THESIS_STATE.md).
