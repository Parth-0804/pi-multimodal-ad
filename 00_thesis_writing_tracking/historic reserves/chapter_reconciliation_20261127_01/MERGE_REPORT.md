# External chapter reconciliation — 27 November 2026

The external chapters were reconciled directly into the active project at
`00_thesis_writing_tracking/Thesis/LaTeX_Project`. The complete thesis is built by
that project's `main.tex`; its inputs are the files edited here.

The starting point was the existing working tree, including its uncommitted work,
at Git HEAD `2ae0c76e3d377a0fae3361c00f2e7d65f704545a`. The earlier comparison was a
guide, not a replacement source. Both actual versions were inspected before edits.
[Starting copies](before/), [external copies](external/), and the
[starting manifest](starting_project_manifest.json) preserve the comparison inputs.
The five supplied originals in `Temp_dump/27112026_ch_reworked_some` are unchanged.

## Chapter decisions applied

| Chapter | Incorporated | Latest local work preserved |
| --- | --- | --- |
| 1 | Clearer roadmap, automatic chapter references, and explicit navigation to the opening design section in Chapter 4. | The completed MSM comparison, bounded ViFailback transfer/adaptation, unexecuted corruption tests and HANDOVER's missing participant identities. Roadmap descriptions were checked against the destination chapters. |
| 2 | Tighter external literature discussion and a cited synthesis table of findings and limitations. Removed thesis-specific requirements and study mapping by meaning, including their figure and table. | Canonical citation identities, study-specific qualifications, missing-input count denominator, corrected locators and seven genuinely unresolved page/version comments. The TCP statement was narrowed according to the prior source audit. |
| 3 | Three hardcoded REASSEMBLE chapter numbers became automatic references. | All prose, comparisons, figures and tables otherwise unchanged. No stale requirements-map reference needed replacement. |
| 4 | One question-led R1–R5 sequence and the five-study mapping together in Section 4.1, with the relocated requirements figure. Added the external timing/fresh-assessment explanation. | Current study boundaries, exploratory chronology, fitting/calibration qualifications, diagnostic links, measured computing/resource evidence and resource provenance comments. Overlapping study explanations were consolidated. |
| 5 | Reviewed the supplied wording; no external change improved the current supported account. | Entire file byte-identical, including PHM results, provenance corrections, Ridge/four-arm diagnostics and appendix links. The external negative-control characterization was not imported. |
| 6 | Shorter conclusion with the selection-bias explanation for combining separately selected follow-ups. Kept the equal-head-size pooling explanation beside its result. | Complete F2 visual-term diagnostic, permutation results, corruption table, follow-up comparison map, numerical results and intervals, calibration/attribution limits, and the MSM transition. |

Detailed receipts: [Chapters 1/3](reviews/chapters_01_03.md),
[Chapter 2](reviews/chapter_02.md), [Chapter 4](reviews/chapter_04.md),
[Chapters 5/6](reviews/chapters_05_06.md).

## Requirements, mapping and transition

Both are in
[`chapters/04_methodology.tex`](../Thesis/LaTeX_Project/chapters/04_methodology.tex),
Section **4.1, “Research design and research questions”** (`sec:ch4-design`).
R1–R5 start at line 44. The five-study mapping is **Table 4.1, “Inputs and assessment
limits of the five thesis studies”** (`tab:fusion-study-scope`), whose environment
starts at line 109. Figure 4.1 retains the existing vector asset. Existing relocated
labels remain valid, including the legacy-named `sec:literature-study-gaps`.

The end of Chapter 2 and the opening of Chapter 4 were read consecutively after
reconciliation, with an independent second review. Chapter 2 ends with conditional
literature findings and a literature-only table. Chapter 4 explains how those findings
inform the questions, targets, controls and assessment limits of these investigations.
The historical qualification remains explicit: the requirements organize the evidence;
they do not imply every experiment was prospectively designed around this framework.
There is one requirements sequence and one five-study mapping table.

## Preservation and citation checks

[Exact task diffs](diffs/) compare the active sources with the saved starting working
tree, independently of the pre-existing Git changes. The
[machine-readable checks](preservation_checks.json) cover the 107-file starting
project manifest. Only Chapters 1, 2, 3, 4, 6 and the project README changed. All
appendix files, bibliography files, figure assets, other chapters and build roots
retain their starting identities. Chapter 5 is byte-identical. Chapter 6 retains
all four tables and its figure byte-for-byte, and loses no label, reference or
evidence identifier.

All 75 external Chapter 2 citation identities were reconciled with existing entries;
the [citation-map receipt](reviews/chapter_02_citation_map.json) records matching
passages and titles. Chapter 4's citation map is in its receipt. No new bibliography
entry was invented. Applicable P021 Tables IV–V, P045 Table 1 and ViFailback Tables
2–4 locators were retained in the shortened Chapter 4 bridge during final review.
The unresolved REASSEMBLE publication page locator was not transplanted.

The edited Chapter 6 result statements were checked against their existing tables,
Appendix D and retained reports. These are **VERIFIED manuscript/report correspondence
checks**, not new score recomputation, training reproduction or independent validation
of every scientific claim. Earlier paper-verification findings remain attributed to
their November 26 audit rather than relabelled as new verification.

## Build and rendered review

The build ran from the active project with the existing toolchain:

```bash
source /tmp/chapter_resource_build_20261126_4oux9axd/toolchain/env.sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir=build/chapter_reconciliation_20261127_01/thesis main.tex
```

Tool versions: latexmk 4.83, XeLaTeX from TeX Live 2023/Debian, Biber 2.19,
and Poppler 24.02.0 for previews. No dependencies or environments were installed
or changed. The toolchain bootstrap is an existing temporary location, so a future
machine/session may need an equivalent installed toolchain.

The build succeeded: **189 pages**, with resolved citations/references, no duplicate
label warnings and no overfull/underfull boxes. The only final TeX warning is the
pre-existing Appendix F `hypcap=true` caption warning. Biber reports no warning.
See the [current PDF](../Thesis/LaTeX_Project/build/chapter_reconciliation_20261127_01/thesis/main.pdf)
and [final build console](../Thesis/LaTeX_Project/build/chapter_reconciliation_20261127_01/main_console_final.log).

PNG previews were rendered at 150 dpi and opened for the Chapter 1 roadmap,
Chapter 2 ending and synthesis table, Chapter 4 opening/requirements/figure/mapping,
and Chapter 6 conclusion. The two tables fit with their complete contents; no clipping,
overlapping text or missing rows was observed. The existing draft watermark remains.
Only the main edition was rebuilt; historical delivery PDFs and review editions
were preserved. Previews are in the build's [preview directory](../Thesis/LaTeX_Project/build/chapter_reconciliation_20261127_01/previews/).

`git diff --check` was run before and after. Its default whitespace rules flag existing
CRLF line endings throughout the dirty tree. The CRLF-aware
`git -c core.whitespace=cr-at-eol diff --check` passes. Existing per-file line endings
were preserved. Git status and both whitespace-check outputs are recorded alongside
this report. No commit, reset, staging or push was performed.

## Remaining limitations

No unresolved merge conflict remains. Seven Chapter 2 page/version checks remain
open: Thoduka twice, P003, P026, Altinses twice and P031. Their exact locators and the
prior evidence are listed in the [Chapter 2 receipt](reviews/chapter_02.md). They
were not silently marked verified. No new experiment or comprehensive literature
re-verification was part of this reconciliation.
