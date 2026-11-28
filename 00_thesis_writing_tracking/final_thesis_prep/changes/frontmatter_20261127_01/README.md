# Front-matter integration — 27 November 2026

The researcher supplied the title page and declaration in `Temp_dump/` and the
acknowledgements in chat. Only the prepared thesis project is integrated here.
The source uploads and original `Thesis/LaTeX_Project` are preserved.

Full-edition order: title page, declaration, abstract, acknowledgements, contents,
list of figures, list of tables, then the numbered chapters. Roman numbering
starts at the abstract; the declaration has no printed page number. The
acknowledgements have a contents entry. Review editions retain their prior scope.
This is an editorial arrangement, not a verification of university requirements.

The two supplied files are copied byte-for-byte. Acknowledgement wording is
unchanged. The title page and declaration keep their `xx November 2026` date
placeholders and the declaration's signature line remains blank. The existing
DRAFT watermark remains enabled. No wording, identity or signature was invented.

- [Integration diff](integration.diff) records the exact edits and additions.
- [Starting manifest](starting_manifest.json) and [before copies](before/) retain
  the initial prepared state. The initial `COPY_MANIFEST.json` and `VALIDATION.json`
  are historical copy receipts; they are not rewritten as current-file claims.

## Build and validation

**VERIFIED:** the full prepared thesis compiled successfully with the existing
XeLaTeX/Biber/latexmk toolchain. The [PDF](../../LaTeX_Project/build/frontmatter_20261127_01/main.pdf)
has 194 A4 pages. No dependencies were installed or changed. Command from the
prepared LaTeX project:

```bash
source /tmp/chapter_resource_build_20261126_4oux9axd/toolchain/env.sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir=build/frontmatter_20261127_01 main.tex
```

The existing toolchain path is a temporary local build resource, not a portable
dependency requirement. The [console log](../../LaTeX_Project/build_frontmatter_20261127_01_console.log)
and generated build files are retained locally under the prepared project.

Rendered and opened PDF pages 1–6 at 110 dpi. The title page, declaration and
acknowledgements fit without clipping or overlap; the signature lines are intact.
The acknowledgements appear on PDF page 5, Roman page iii, directly before the
contents on PDF page 6, Roman page iv. The contents entry points to page iii.
The title and declaration have no visible page numbers; the abstract starts at i.
The existing DRAFT watermark remains visible.

The final LaTeX log contains the two intentional missing-date warnings and the
existing Appendix F caption `hypcap=true` warning. It contains no undefined
citation/reference, duplicate-label, missing-character, overfull-box or
underfull-box warning. Biber reports no warnings or errors.

**Remaining layout item:** the copied abstract's keywords occupy their own page
(PDF page 4 / Roman ii). Its source and the abstract/keyword formatting are
unchanged by this integration. Consider fitting the abstract and keywords on one
page during the final editing pass; no wording was shortened here.

Source checks confirm that all original files and both supplied uploads retain
their identities. `main.tex` is the only changed member of the initial 113-file
copy; three new front-matter sources were added. Review-edition scope is preserved
by the existing full-edition conditional; review PDFs were not rebuilt. The
initial-copy manifests remain unchanged. These checks validate integration and
layout, not declaration compliance, submission readiness or scientific claims.

See [validation](validation.json) and [updated file identities](final_manifest.json).
No experiment, staging, commit or push was performed.

