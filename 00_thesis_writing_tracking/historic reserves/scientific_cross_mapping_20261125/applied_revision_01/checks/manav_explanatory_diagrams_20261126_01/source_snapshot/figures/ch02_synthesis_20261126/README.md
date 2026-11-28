# Chapter 2.8 synthesis figure

Updated 26 November 2026 after the researcher's figure review.

- [TikZ source](fig_ch02_synthesis.tex)
- [Vector PDF](fig_ch02_synthesis.pdf)
- [Opened 150 dpi preview](../../build/figures/ch02_synthesis_20261126_04/figure-preview.png)
- [Updated thesis figure page](../../build/figures/ch02_synthesis_20261126_04/figure_in_chapter.pdf)
- [Full thesis PDF](../../build/figures/ch02_synthesis_20261126_04/thesis/main.pdf)

Installed in `applied_revision_01/working/LaTeX_Project/`. Chapter 2 includes the
figure at `width=\linewidth`, with label `fig:ch02-synthesis-requirements`.
The shared semantic palette and the 159.20 × 125.00 mm canvas are retained.

## Top-left arrangement

The latest block uses “Missing-input gap (SQ3)” at 10 PDF pt bold, the 13.5%
callout at 18 PDF pt, and centered supporting text at 9 PDF pt. “Most studies
assume intact sensors” wraps across two lines; “→ Motivates R4” is italic.
The exact denominator appears in the actual LaTeX caption as “5 of 37 initial
full-text papers,” rather than inside the diagram. The figure note defines the
PA/SD categories. The original short title is retained in the list of figures.

## Requirements card

One centered downward arrow connects “Conditional fusion effectiveness” to a
single rounded neutral card. The former branch arrows and upward dashed support
arrows are removed. Five ordered rows use bold 10 PDF pt tags, regular 10 PDF pt
descriptions, and right-aligned muted italic source labels at 9 PDF pt:

| Tag | Description | Source |
|---|---|---|
| R1 | Target validity and aligned pairing | (Sec. 2.2–2.3) |
| R2 | Representation suitability and fitting budget | (SQ1) |
| R3 | Incremental fusion vs. matched controls | (SQ2) |
| R4 | Reliability under absence, noise, and shift | (SQ3) |
| R5 | Grouped splits, calibration, and claim bounds | (SQ4) |

Each row fits on one line. Row centers are 6 mm apart; the smallest measured
description-to-source gap is 13.53 mm. Four 0.5 PDF pt hairlines use the same
neutral color as the bottom-right table. The shared corner radius and arrow
style are retained.

## Retained marker conventions

- PHM's photo proxy target uses a hollow blue ring; predictor inputs retain solid
  markers. The LaTeX figure note explains the distinction.
- HANDOVER reads “Learned stacking omitted”; the note identifies the unavailable
  participant-to-trial mapping.
- Its location reads “Appendix” without a hardcoded letter.
- The record-count block and its explanatory slogan are replaced by the verified
  coverage statistic below.

## Basis of the percentage

**13.5% = 5/37 × 100**, rounded to one decimal place. The diagram uses the shorthand
“Tested missing inputs”; its note defines this as planned missing-input inference
or simulated dropout. The caption gives the **initial 37-paper full-text review**
denominator, and the note refers to Table `tab:literature-matrix`.

[verify_review_coverage.py](verify_review_coverage.py) reads the active
[CSV matrix](../../tables/literature_matrix.csv), checks the same codes in the
[printed matrix](../../tables/literature_matrix.tex), and selects `missing_code`
values `PA` or `SD`. It generates [the figure macros](review_coverage.tex) and a
[machine-readable audit](../../build/figures/ch02_synthesis_20261126_02/coverage/review_coverage.json)
containing all 37 records, the counting rule and source hashes. The chapter note
uses the same generated count macros as the standalone figure.

| Code | Meaning | Count |
|---|---|---:|
| PA | Planned missing-input inference | 4 |
| SD | Simulated dropout | 1 |
| N | No controlled trial established | 28 |
| TR | Missing training images, complete tests | 1 |
| GS | Generated substitution | 1 |
| RS | Retrained input subsets | 1 |
| NA | Survey | 1 |

The five included records are `Yang2024Fault`, `Li2025PGMTKD`,
`Sui2026Incomplete`, `Xu2025ModalityResilient` and `Xie2025Audiovisual`.
Their positive code meanings were also checked against local primary PDFs by a
second reviewer; [source paths, hashes and PDF pages](../../build/figures/ch02_synthesis_20261126_02/positive_code_source_checks.json)
are retained. Xu's dropout allocation wording remains ambiguous, as recorded in
its appraisal. This was not a new appraisal of all 37 studies.

**VERIFIED:** the recount, agreement between the CSV and printed codes, and the
five positive source checks. The percentage describes protocol coverage within
this initial cohort. It is not a rate of successful fusion, a share of all 94
registered works, or field prevalence. The remaining 32 include other missing-input
regimes; they must not be labelled “no missing-input testing.” Planned inference
also includes privileged training for fixed single-input deployment, rather than
necessarily an unexpected sensor outage.

## Standalone verification

The PDF is vector output with zero raster objects. All font subsets are
embedded: Latin Modern text and Computer Modern math. Labels are 9–11 PDF pt;
the numeric percentage is 18 PDF pt. The measured canvas is 159.1980 × 124.9998 mm,
within 0.01 mm of the target. The final build has no font substitution, overfull
or underfull warnings. The final 150 dpi preview was opened and checked for the
hollow marker, single centered arrow, label spacing and clipping. An independent
reviewer also opened the preview and confirmed the five single-line rows.

[PDF validation](../../build/figures/ch02_synthesis_20261126_04/figure_validation.json)
records hashes, dimensions, text sizes, fonts, row spacing and alignment. Pixel
comparison against the preceding preview confirms that only the requirements
card and its connector changed.

## Integration and preservation

The full thesis build passed after two XeLaTeX passes and Biber. Figure 2.1 remains
on printed page 52 (PDF page 66) of the 272-page thesis. The denominator is in the
caption above the diagram. Both the standalone preview and the
[integrated 150 dpi preview](../../build/figures/ch02_synthesis_20261126_04/integrated-preview.png)
were opened; text, caption and note fit without clipping or overlap.
The existing draft watermark is retained.

The final log has no undefined references or citations, overfull/underfull boxes
or oversized floats. The existing Appendix F `hypcap=true` caption warning
remains. No dependency blocked validation.
[Integration validation](../../build/figures/ch02_synthesis_20261126_04/integration_validation.json)
records the current PDF identity and page numbers.

This pass changes the top-right requirements layout, the generated PDF and this
report. The Chapter 2 source, caption/note, top-left block, counting rule, evidence
files, shared styles and other figure assets remain unchanged.
[Preservation checks](../../build/figures/ch02_synthesis_20261126_04/preservation_validation.json)
and exact diffs are retained in the run directory. `git diff --check` passed;
these thesis sources are untracked, so ordinary Git diff output does not list
the changes.

## Rebuilding

Run from the thesis root with the existing XeLaTeX, latexmk, Biber and Poppler
on `PATH`. This pass used `/tmp/thesis_tex_20261125/env.sh`; no dependencies were
installed. Choose a new output directory for another verification pass.

```sh
figure_run=build/figures/ch02_synthesis_YYYYMMDD_01
python figures/ch02_synthesis_20261126/verify_review_coverage.py \
  --outdir "$figure_run/coverage"
# Review generated counts before updating the included review_coverage.tex.
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir="$figure_run/figure" figures/ch02_synthesis_20261126/fig_ch02_synthesis.tex
pdftoppm -r 150 -png -singlefile \
  "$figure_run/figure/fig_ch02_synthesis.pdf" "$figure_run/figure-preview"
# Inspect the preview, then update the included figure PDF before the thesis build.
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir="$figure_run/thesis" main.tex
```

The previous source, PDF, chapter and report are preserved in
`build/figures/ch02_synthesis_20261126_04/before/`. The original supplied source and
first integration remain under `build/figures/ch02_synthesis_20261126_01/`.
Build outputs are ignored; no files were staged, committed or pushed.
