# Figure style installation and verification

25 November 2026. Setup and synthetic smoke verification only.

## Location and merge

Installed in the editable project identified by the revision README:
`00_thesus_writing_tracking/scientific_cross_mapping_20261125/applied_revision_01/working/LaTeX_Project/`.
Its `main.tex` reads the local `chapters/` and `figures/` directories. The other
project under `applied_revision_01/baseline/` is explicitly the unchanged baseline.

Source: `../../thesis_figure_style_for_applied_revision_01.zip`, SHA-256
`a0e34e2e73b9174e17b7cd9cb857556f4d9f8bdb1e79f5968cadfd8b22325986`.
Starting repository HEAD: `e2037412036c5bbfc01fb2323215a37ef0b2e090`;
the working thesis already consisted of untracked files.

| Installed file | Merge result |
|---|---|
| [VISUAL_STYLE.md](VISUAL_STYLE.md) | Added; aligned provenance, native-font commands and PDF checks with this revision |
| [tikz_style.tex](tikz_style.tex) | Added byte-for-byte from the payload |
| [thesis.mplstyle](thesis.mplstyle) | Added byte-for-byte from the payload |
| [smoke/style_smoke.tex](smoke/style_smoke.tex) | Added; records font selection and asserts the verified text width |
| [smoke/style_smoke.py](smoke/style_smoke.py) | Added; native XeLaTeX option, robust PDF-width check and refusal to overwrite output PDFs |
| [../AGENTS.md](../AGENTS.md) | Added a thesis-scoped supplement containing the payload's Figure verification section verbatim; repository instructions retained |
| This report | Added installation, validation and handoff evidence |

No matching destination filenames existed and no merge conflict requires a
researcher decision. The approved eleven-role semantic palette is unchanged.
The [exact payload adaptation diff](../build/figures/verification_20261125_01/payload_adaptations.patch)
records all changes to the incoming files.

## Verified layout and typography

**VERIFIED:** the [layout probe](../build/figures/verification_20261125_01/active_layout_probe.tex)
copies the active `main.tex` preamble, then invokes its chapter-body `\apaprose`.
It was compiled from the thesis root with the existing XeLaTeX toolchain.

| Property | Measured result |
|---|---|
| Class and page | `report[12pt,a4paper,oneside]`, A4 |
| Geometry | `margin=1in`; zero odd/even side-margin offsets |
| Normal `\textwidth` and `\linewidth` | 452.9679 TeX pt = 159.20 mm |
| Half width | 226.48395 TeX pt = 79.60 mm |
| `\textheight` | 700.50687 TeX pt |
| Body font | Latin Modern Roman 12 Regular/Bold at 12 TeX pt |
| Normal chapter baseline skip | 23.99748 TeX pt after `\apaprose` |

These measurements match the supplied v3 dimensions. No thesis preamble or margin
change was needed. Inside narrower containers, use the local `\linewidth`.
See [probe console](../build/figures/verification_20261125_01/layout_console.txt)
and [probe fonts](../build/figures/verification_20261125_01/layout_pdffonts.txt).

## Smoke results

**VERIFIED:** both smoke checks executed from this thesis root. All accepted PDFs
are single-page vector output with zero image objects and all fonts embedded.
Their text sizes are 9, 10 and 11 PDF pt. The Matplotlib script checked every
color-to-role mapping against both the guide and TikZ definitions.

| Example | Width check | PDF and opened 150 dpi preview |
|---|---|---|
| TikZ | Full and half picture boxes equal their respective `\linewidth`; the containing PDF remains A4 | [PDF](../build/figures/verification_20261125_01/final/tikz/style_smoke.pdf), [PNG](../build/figures/verification_20261125_01/final/style_smoke-preview.png) |
| Matplotlib full | 451.28 PDF pt = 159.2016 mm; within 0.01 PDF pt of target | [PDF](../build/figures/verification_20261125_01/final/matplotlib_native_v2/style_smoke_full.pdf), [PNG](../build/figures/verification_20261125_01/final/style_smoke_full_native-preview.png) |
| Matplotlib half | 225.64 PDF pt = 79.6008 mm; within 0.01 PDF pt of target | [PDF](../build/figures/verification_20261125_01/final/matplotlib_native_v2/style_smoke_half.pdf), [PNG](../build/figures/verification_20261125_01/final/style_smoke_half_native-preview.png) |

The TikZ preview is 1241 × 1754 pixels; plot previews are 941 × 330 and 471 × 330.
Pixel dimensions include renderer rounding. PDF dimensions are authoritative.
The three accepted previews and all three archive reference previews were opened.
Visual inspection found no clipping, overlapping labels, obstructed legends or
ambiguous arrow directions. The half-width labels remain readable; marker shapes
and line patterns accompany the semantic colors. This is inspection of the smoke
examples, not a review of chapter figures or the full manuscript.

The first direct Matplotlib run used `cmr10.ttf` for both normal and bold text,
so it was not accepted as a thesis-font match. Native `--tex-fonts` export uses
PGF/XeLaTeX and the existing Latin Modern OTF fonts, with Computer Modern math
matching the thesis's TeX math family. No font conversion or dependency installation
was performed. The direct TrueType alternative lacks `lmroman12-regular.ttf` and
`lmroman12-bold.ttf` locally; it is not required by the accepted native route.

The first native export exposed the archive's raw-text MediaBox parser limitation:
XeLaTeX compresses PDF page objects and rounds dimensions to hundredths of a PDF
point. The script now reads MediaBox through `pypdf` with a 0.01-point tolerance.
A further size check found discrete TeX math sizes slightly below 9 PDF pt;
`fix-cm` enables the intended sizes. The native preamble also suppresses the
standalone page number. Earlier attempts and logs are retained in the same
verification directory, distinct from the accepted `matplotlib_native_v2` outputs.
No requested validation remains blocked by a missing dependency.

## Toolchain and commands

Existing environment: XeTeX/TeX Live 2023, latexmk 4.83, Python 3.12.3 and
Matplotlib 3.11.1. `pypdf`, Pillow and Poppler were already available. The existing
isolated TeX environment was loaded from `/tmp/thesis_tex_20261125/env.sh`;
Python was `../../../../../ma_thesis_env/bin/python` relative to this thesis root.
The temporary TeX location is execution evidence, not a new portable default.
The guide uses tools on `PATH` and the selected project Python environment.

Commands executed from the thesis root after loading that environment:

```sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir=build/figures/verification_20261125_01/layout \
  build/figures/verification_20261125_01/active_layout_probe.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir=build/figures/verification_20261125_01/final/tikz \
  figures/smoke/style_smoke.tex
MPLCONFIGDIR=build/figures/verification_20261125_01/mpl-cache \
  PYTHONDONTWRITEBYTECODE=1 ../../../../../ma_thesis_env/bin/python \
  figures/smoke/style_smoke.py --tex-fonts \
  --outdir build/figures/verification_20261125_01/final/matplotlib_native_v2
```

Each accepted PDF was inspected with `pdfinfo`, `pdffonts` and `pdfimages -list`,
then rendered with `pdftoppm -r 150 -png -singlefile`. Dimensions, actual text
sizes, page counts and absence of raster objects were also checked with `pypdf`.
[Machine-readable validation](../build/figures/verification_20261125_01/validation.json)
records the accepted paths and hashes; adjacent `accepted_*` reports retain the
Poppler output. Use a new run directory when repeating the checks.

## Preservation and handoff

**VERIFIED:** all ten pre-existing figure assets retain their starting SHA-256
identities. This pass wrote only new style/instruction/report files and isolated
build outputs. It did not edit chapters, the abstract or `main.tex`.

The [starting manifest](../build/figures/verification_20261125_01/project_before.json)
covered 47 existing project files. A later comparison detected concurrent changes
outside this pass to `main.tex`, `frontmatter/abstract.tex` and
`chapters/01_introduction.tex`; those edits were left untouched. Their identities
are recorded in `validation.json`. The current normalized preamble still exactly
matches the measured preamble. Consequently this report does not claim that the
entire working project remained byte-for-byte unchanged during the task.

`build/` is ignored by the existing repository rule; the verification artifacts
remain local. The archive and original assets remain in place. No files were
staged, committed or pushed. Final Git checks and installed-file identities are
recorded in the verification directory. Since these sources were untracked,
ordinary `git diff --stat` does not enumerate the additions; the file table and
payload diff above do.

The separate `02_REDO_CHAPTERS_01_04.md` task has not been executed. The installed
guide, shared styles and verified smoke examples are ready for that later task.
