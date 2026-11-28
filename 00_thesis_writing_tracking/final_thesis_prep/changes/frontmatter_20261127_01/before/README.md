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
- [Validation](VALIDATION.json): copy integrity and static dependency checks.
- [Source Git status](SOURCE_GIT_STATUS.txt): changes already present before copying.

`LaTeX_Project/` includes all source and supporting files outside `build/` and
`chapters_pdfs/`, including editable figures, bibliographies, evidence/literature
CSV indexes, style files, build configuration and project instructions. Draft
figure assets retain their existing names and status; they are not newly approved
for use. `context/` contains selected dated writing/review records.

All copied source bytes are preserved. The copied project README, context notes,
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

This command is provided for the next editing session; no compilation was run
for this copy task. The full thesis source is newer than the source identities in
the last literature-integration build manifest, so an older PDF must not be treated
as a rendering of this exact snapshot. Full-thesis PDFs and build caches were not
copied. The DRAFT watermark and existing title/date remain unchanged.

## Repository evidence and boundaries

Use the current [repository instructions](../../AGENTS.md),
[thesis-to-code map](../../docs/THESIS_CODE_MAP.md),
[data boundaries](../../docs/data_boundaries.md),
[output policy](../../docs/output_policy.md) and
[active scope](../../docs/active_scope.md). Experiment artifacts remain in their
existing locations; no datasets, environments, checkpoints or downloaded
publications were copied. Nothing was staged, committed or pushed.
