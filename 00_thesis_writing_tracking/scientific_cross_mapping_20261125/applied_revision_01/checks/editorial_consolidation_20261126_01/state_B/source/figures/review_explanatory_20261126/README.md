# Explanatory figures for the Manav review

Added 26 November 2026 at section headings, with manuscript captions and stable labels:

| Source | Section | Meaning |
| --- | --- | --- |
| `prediction_availability.tex` | 2.2.4, Retrospective Assessment and Online Monitoring | Same-action observation and computation timelines; early warning is hypothetical. |
| `sensor_patch_tokens.tex` | 3.3.3, Patching, Sequence Length, Padding, and Aggregation | Two overlapping patches from one synthetic sensor channel. Positions are action progress, not elapsed time. |
| `stacker_recording_flow.tex` | 4.6.2, Out-of-Fold Predictions and Learned Fusion | Reused development OOF bank and separate outer assessment path. |

Each source imports `figures/tikz_style.tex` from the thesis root and has an adjacent vector PDF. Canvas widths are 159.20 mm; heights are 82, 90 and 100 mm respectively. The sensor trace is synthetic and uses no dataset payload. Timings are schematic rather than measured. The stacker diagram describes the original REASSEMBLE procedure; it does not imply strict independence within internal stacker validation.

The supplied synthesis redesign is separately preserved as `figures/fusion_research_gap.tex` and `.pdf`. The original label `fig:ch02-synthesis-requirements` and supplied alias `fig:fusion-research-gap` identify that same figure. Numbering is automatic: adding the earlier timing diagram renumbers the former Figure 2.1. The accompanying supplied paragraph and five-study scope table appear at the start of “Implications for the Empirical Investigations.” The original synthesis asset remains preserved but is no longer included.

From the thesis root, compile an editable figure with `latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build/figures/<unique-run> figures/review_explanatory_20261126/<source>.tex`. Copy its verified final vector PDF beside the source, then compile `manav_review.tex`. The synthesis source is compiled similarly from `figures/fusion_research_gap.tex`.

Standalone 150 dpi previews and build logs are under `build/figures/review_explanatory_20261126/`. The delivery check record records final manuscript page numbers, source/PDF identities and the page previews opened after compilation. These are explanatory figures, not new experimental results.
