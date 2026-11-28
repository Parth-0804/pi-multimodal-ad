# Literature figure and table integration — 27 November 2026

## Baseline and active build

The active root is `00_thesis_writing_tracking/Thesis/LaTeX_Project/main.tex`.
Its Chapter 2 input is `chapters/02_literature_review.tex`. The tree was clean at
commit `9f7395b6c26052ea940fdfbe6b9ae6d8f8091c74` before this task.

The active chapter was used as the latest baseline after comparing content and
history with the external chapter in `Temp_dump/27112026_ch_reworked_some/`,
preserved external copies, and the earlier applied-revision/reconciliation copies.
The external rewrite was already incorporated. Its remaining differences from the
active chapter, after the earlier citation-key reconciliation, were the retained
seven citation-page cautions and a later corrected TCP description. No independent
newer chapter text was identified. Upload time was not used to choose the baseline.
The earlier pre-reconciliation chapter was not restored.

The [preserved baseline](before/chapters/02_literature_review.tex) has SHA-256
`474c5161de33814e11bdd4e547a4fec4c1017d9d5d5943207d4718b97107b666`.
See [starting manifest](starting_manifest.json), [starting HEAD](head.txt), and
[starting status](git_status_before.txt).

The uploaded source is `Temp_dump/review_figure_table.tex`, SHA-256
`9a5328ff4f211208d14f38b77566076d25d59e5f757a9426cdf3bf9060d0ddf0`.
It remains unchanged; a [copy](before/review_figure_table.uploaded.tex) is retained.

## Integration

- [Chapter 2](../Thesis/LaTeX_Project/chapters/02_literature_review.tex): inserted
  the training-strategy lead-in and one figure call after the concluding conditional-
  benefit paragraph in §2.8.1, immediately before §2.8.2. The lead-in uses 60 of 94
  described/used and 28 of 94 directly tested (29.8%).
- [Editable visual source](../Thesis/LaTeX_Project/figures/review_figure_table.tex):
  installed from the upload, adapted to the shared TikZ style and embedded mode.
  The seven topic labels, all 28 counts, and four coding categories are unchanged.
  Every row sums to 94; papers may contribute to multiple topics. The note states
  that “No treatment recorded” describes the author's appraisal, not proof that the
  paper omitted a topic. Grayscale and hatching encode appraisal categories.
- The same editable source defines the consolidated three-column longtable under
  `tab:literature-synthesis`. Its seven topic rows and qualitative credibility row
  retain all eleven prior table citation keys, the positive welding result, the
  clean welding tie, the negative handover contrast, and the existing limitations.
  Uploaded bibliography aliases were reconciled to the existing canonical keys.
  Follow-up questions concern specific comparison or evidence limits; frequency
  alone is not presented as research priority. Coverage counts remain in the figure.
- §2.9 retains the exact heading and original synthesis paragraph, followed by the
  single consolidated table. The rest of Chapter 2 is byte-identical outside the
  two integration blocks, including the seven citation-page cautions and earlier
  five-of-37/13.5% passage, which concerns a separate initial-review scope.
- [Shared preamble](../Thesis/LaTeX_Project/thesis-formatting.tex): loads the source
  using `figures/review_figure_table.tex` with `ThesisLiteratureEmbedded` defined.
  The source imports `figures/tikz_style.tex`; neither the main build nor the installed
  source depends on Temp_dump. The main root and other chapter sources are unchanged.
- [AI disclosure](../Thesis/LaTeX_Project/appendices/I_ai_assistance.tex): states that
  Codex helped prepare the figure and table and that the appraisals and interpretation
  are the author's. No appraisal recoding or independent scientific-paper audit is
  claimed for this integration.

Machine-readable source checks are in [source_checks.json](source_checks.json).

## Build and visual verification

Builds ran from the active thesis root with the existing XeLaTeX/Biber/latexmk
configuration, after sourcing the available toolchain environment at
`/tmp/chapter_resource_build_20261126_4oux9axd/toolchain/env.sh`.
No dependencies were installed. The toolchain is latexmk 4.83, XeTeX/TeX Live 2023,
Biber 2.19, and Poppler 24.02. Commands:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir=build/figures/literature_review_integration_20261127_01/thesis main.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir=build/figures/literature_review_integration_20261127_01/standalone \
  figures/review_figure_table.tex
```

The full [compiled thesis](../Thesis/LaTeX_Project/build/figures/literature_review_integration_20261127_01/thesis/main.pdf)
is 191 A4 pages. The standalone proof is three A4 pages, with the figure using the
159.20 mm text width. An exact-preamble measurement confirmed textwidth and normal
linewidth of 452.9679 TeX pt (159.20 mm), and Latin Modern Roman at 12 pt. Figure
labels use 10 bp, annotations/legend 9 bp, and panel headings 11 bp. The initially
reported math script-size substitution was fixed locally for the 9 bp annotation
size. All fonts used on the affected thesis pages are embedded and subset.

| Object | Location | PDF page(s) | Printed page(s) |
| --- | --- | --- | --- |
| Figure 2.2, `fig:review-depth` | §2.8.1, before the research-gap subsection | 44 | 32 |
| Table 2.1, `tab:literature-synthesis` | §2.9 | 46–47 | 34–35 |
| Original final synthesis paragraph | §2.9 | 45 | 33 |
| Updated AI disclosure | AI Assistance Disclosure | 143 | 131 |

The final log has no undefined citations/references, duplicate labels, overfull or
underfull boxes, or font-substitution warnings. Biber reports no warnings or errors.
The sole remaining LaTeX warning is the pre-existing Appendix F caption warning:
`hypcap=true` ignored for its caption at line 122.

Opened and inspected 150 dpi PNGs of final thesis PDF pages 43–48 and 143, and all
three standalone proof pages. Figure labels, legend, hatching, counts, spacing and
bounds are readable without clipping or overlap. The figure occurs once before
the research-gap heading. The closing section has exactly one synthesis paragraph
and one table. The table continues with repeated column headings, complete rows,
and a continuation notice. Chapter 3 follows the table. The existing DRAFT watermark
is retained. Previews, PDF text, font listing and build logs are under
[the build directory](../Thesis/LaTeX_Project/build/figures/literature_review_integration_20261127_01/).

These are verified source, arithmetic, compilation, reference-resolution and layout
checks. The appraisal classifications and literature interpretation remain the
researcher's supplied work; they were not independently recoded or re-audited.

## Fast editing preview and final handoff

The eight new citation groups were also added to `chapter-preview.tex`, using the
exact author/year/disambiguation forms in the compiled main thesis. The new figure
reference cache is 2.2, printed page 32. The default preview chapter remains 1.
The original preview root is preserved in [before/chapter-preview.tex](before/chapter-preview.tex).

A supplementary attempt to build Chapter 2 through that fast preview root was
blocked by its pre-existing missing `\textcite` command at unchanged Chapter 2
line 64. The original root defines citep/citet/parencite but not textcite. This
predates the integration and does not affect the successful main or standalone
builds. The unrelated preview-system repair was not included in this task.
The failed attempt's log remains under the build directory's `fast-preview/`.

`git diff --check` passes. Reviewed the exact changed-source diff and checked the
new documentation links. All changes are local and unstaged; no commit or push
was made. No experiment, dataset, chapter outside Chapter 2, existing figure asset,
bibliography file, or main root was modified. The existing disclosure, shared
preamble, editing-preview cache and project README received the supporting changes
listed above. [Final manifest](final_manifest.json) records source and PDF identities;
[integration.diff](integration.diff) records the tracked-source changes and upload-to-installed-source adaptation.
