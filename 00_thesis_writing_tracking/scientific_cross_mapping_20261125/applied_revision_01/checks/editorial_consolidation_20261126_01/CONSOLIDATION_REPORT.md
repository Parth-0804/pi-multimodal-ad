# Editorial consolidation and formatting — completed 26 November 2026

The latest November 26 source was used throughout. The unchanged starting manuscript is preserved in [state_A/source](state_A/source/). [State B](state_B/source/) contains the editorial changes alone; [State C](state_C/source/) adds the shared formatting. The original November 20 baseline was not substituted or edited.

## Measured reductions

| Edition | A: current November 26 | B: consolidation only | C: final formatting | Saved by consolidation | Additional saved by formatting |
|---|---:|---:|---:|---:|---:|
| Manav: Abstract + Chapters 1–4 | 126 | 107 | **82** | 19 | 25 |
| Review: Abstract + Chapters 1–10 | 205 | 186 | **142** | 19 | 44 |
| Complete thesis | 275 | 256 | **199** | 19 | 57 |

| Chapter | A pages | B pages | C pages | A approximate words | B/C approximate words | Numbered sections/subsections, A → B/C |
|---|---:|---:|---:|---:|---:|---|
| 1 | 7 | 7 | 6 | 1,622 | 1,622 | 6/0 → 6/0 |
| 2 | 47 | 47 | 36 | 10,691 | 10,691 | 8/37 → 8/37 |
| 3 | 32 | 27 | 20 | 7,272 | 5,796 | 6/20 → 6/19 |
| 4 | 39 | 25 | 19 | 8,388 | 5,917 | 11/30 → 11/7 |

The final Manav chapter ranges are 2–7, 8–43, 44–63 and 64–82; its Abstract is page 1. [All ten chapters, exact printed/PDF ranges, word-count method and three-state heading counts](STATE_METRICS.md) are recorded separately. Formatting-only reductions in protected chapters do not indicate text deletion. The final widow/orphan controls use one additional page compared with the initial 81-page formatting preview, keeping the research-question item together.

## Editorial changes

Chapter 3 retains all six principal sections. The redundant §3.5.7 recap heading and prose were removed while its comparison table remains. Cuts remove repeated RT-DETR path recaps, aggregation descriptions, textbook predictor explanations, table/figure narration and component-selection summaries. The statistical-feature rationale was relocated intact after its feature definition. The brief OOF/outer-assessment qualification remains; Chapter 4 retains the full procedural explanation. [Chapter 3 deletion ledger](ch3_changes.md).

Chapter 4 retains all eleven principal sections. The subsections of §§4.1, 4.5, 4.7, 4.10 and 4.11 are integrated into their parent sections. Section 4.6 retains three headings for training-side procedures, OOF fitting and assessment cohorts/exposure; §§4.8 and 4.9 retain two each. Repeated study-to-requirement introductions, dataset-admission summaries, metric explanations and the concluding methodological synthesis were removed. Related authored sentences were joined without new prose. [Chapter 4 deletion ledger](ch4_changes.md).

Retained wording was preserved: all 328 final Chapter 3 sentence units match the starting text; 351 of 352 Chapter 4 units match exactly. The remaining sentence only deletes the dangling word “therefore.” Headings and display blocks are checked separately. This comparison allows verbatim relocation and collapsed paragraph whitespace; it is not a formal linguistic or plagiarism assessment.

## Scientific content retained

The exact equations, figures, tables, labels, citation commands/postnotes and evidence references/locators remain. This includes executed RT-DETR component boundaries and the PHM/REASSEMBLE difference; sensor-feature definitions; PatchTST initialization, dimensions, padding/masking qualifications and parameter counts; probability/logit/calibration distinctions; all fusion formulations; historical selection versus retrospective justification; and R1–R5 links.

Chapter 4 retains outer exclusion, inner OOF generation and the reused prediction-bank dependency without claiming strict nesting; PHM preprocessing limitations; cohort reconciliation and repeated assessment exposure; within-fold versus pooled ranking and the missing refitted sensor-only control; prevalence, class-specific/macro AP and metric aggregation; bootstrap units and uncertainty limitations; matched corruption exposure, fallback and degraded-input distinctions; and the November 24 experimental cutoff, November 25 saved-score verification and unfinished ViFailback work.

**90 protected source/assets files are byte-identical**, including the Abstract, Chapters 1–2 and 5–10, every appendix, bibliography files and all figure/table assets. No scientific figure was redesigned or regenerated. The existing integrity checker correctly flags reduced occurrence counts in deleted duplicates; those flags are individually reconciled in [wording preservation](WORDING_PRESERVATION.md) and [integrity data](editorial_integrity.json), rather than reported as a zero-change pass.

## Central formatting

[thesis-formatting.tex](../../working/LaTeX_Project/thesis-formatting.tex) provides one-and-a-half body spacing, 6 mm indentation and zero paragraph spacing. It replaces the competing 1.22/double-spacing settings through minimal wiring in the main, Manav and chapter-preview roots; the review root inherits main. Latin Modern, 12 pt body text, A4, one-inch margins, heading fonts/numbering and APA configuration remain unchanged. Existing separate table, float and footnote spacing is retained.

Chapter opening gaps change from 50/20/40 pt to 24/12/24 pt; section/subsection gaps are moderately reduced while class no-break behavior remains. The centered Abstract uses positive spacing consistently across editions. Standard widow/orphan penalties and moderate float spacing/fractions improve page breaks. There are no new negative-offset or page-enlargement hacks.

No authoritative university formatting document was found in the available repository; the existing pipeline records those requirements as unverified. This is the author-requested working format, **subject to university approval**, not a certification of compliance.

## Build, layout and delivery checks

All nine A/B/C edition builds completed with the existing XeLaTeX/Biber workflow. Final reviews have no LaTeX or Biber warnings, unresolved citations/references, overfull boxes or missing characters. The full edition retains the same pre-existing appendix caption/hypcap warning at Appendix F's table caption; it was present in A and B. [Build warning comparison](build_warnings.json). The CRLF-aware Git whitespace check passes; the default check flags retained CRLF endings on moved/joined lines, which were preserved to avoid normalizing the authored files. [Final validation](final_validation.json).

All 82 final Manav pages were rendered at 150 dpi and screened through contact sheets. Selected full-resolution pages cover the Abstract, research-question break, literature table, scope table, synthesis diagram, patch-token diagram, stacker flow and methodology prose. Sixteen selected full-thesis pages cover Chapters 5–10, results/figures, references and appendix tables. No clipping, overlap or unreadable retained diagram labels were found in these checks. Some whitespace remains at chapter endings and around fixed or large floats; protected figure definitions were preserved. This was not a full-text proofread of every full-thesis page. [Visual check scope](visual_checks.json).

All fonts are embedded and every local compiled source input is included in the **71-file source ZIP**. The ZIP matches the final compiled source. Separate editorial and formatting patches, plus the combined patch, reconstruct and reverse to exact frozen-state hashes. The cumulative November-20-to-current binary patch also reconstructs the delivery source exactly. [Delivery checks](delivery_checks.json), [PDF consistency](pdf_consistency.json).

- [Final Manav PDF](../../Manav_review_Abstract_Chapters_1-4.pdf)
- [Final full thesis](../../revised_thesis.pdf)
- [Final Chapters 1–10 review](../../revised_review.pdf)
- [Editable source ZIP](../../revised_latex_source.zip)
- [Editorial-only patch](editorial_A_to_B.patch)
- [Formatting-only patch](formatting_B_to_C.patch)
- [Combined current-November-26-to-final patch](combined_A_to_C.patch)

The earlier PDFs, source archive, delivery notes and cumulative patch are retained in state_A. No new experiments, inference, training, dependency installation, Git commit or push was performed for this task.
