# Wording and scientific-content preservation

Compared the frozen A, B and C sources. A is the latest November 26 manuscript, B contains editorial consolidation only, and C adds the shared formatting configuration. The November 20 manuscript was not substituted.

## Authorized file boundaries

- A → B: exactly **2 files**: `03_foundations.tex` and `04_methodology.tex`.
- B → C: exactly the new `thesis-formatting.tex` plus formatting wiring in `main.tex`, `manav_review.tex` and `chapter-preview.tex`.
- **90 other source/assets files are byte-identical in A, B and C**. This includes the Abstract, Chapters 1–2 and 5–10, all appendices, the bibliography, every figure source/PDF/style asset and evidence infrastructure.
- The editorial chapters themselves are byte-identical in B and C. All root-document changes are visible in the separate formatting patch.
- State A already has a one-page abstract in the Manav extract and a two-page abstract in the full/review editions, following the earlier Manav-specific layout request. That difference is formatting, not different Abstract wording. Protected-content hashes are identical.

## Verbatim authored wording

Headings and technical display blocks were checked separately. For prose comparison, heading commands, ordinary TeX comments, labels and display blocks were omitted; paragraph whitespace was collapsed. Final sentence units were matched as exact substrings of the state A text, so unchanged relocation is allowed. This lexical test does not judge whether a deleted passage was scientifically redundant; the chapter ledgers record that review.

| Chapter | Final sentence units | Exact original wording | Minimal transition adjustment | Unmatched units |
|---|---:|---:|---:|---:|
| 3 | 328 | 328 | 0 | 0 |
| 4 | 352 | 351 | 1 | 0 |

- Chapter 3 introduces no new prose. The statistical-feature rationale beginning “Such features provide…” is relocated intact after the 220-feature definition. One equation-narration sentence is removed while the original following coefficient-constraint sentence remains.
- Chapter 4 changes one prose sentence only: “Each empirical comparison **therefore** identifies…” becomes “Each empirical comparison identifies…”. The single dangling transition word is deleted. Other retained sentences remain verbatim, including relocated paragraphs and sentences joined without new wording.
- Chapter 4 relocations also include the PHM historical preprocessing qualification into the training-side subsection, the absent sensor-only control into the fitting/ranking discussion, and probability metrics before aggregation. Revised subsection headings organize those original passages; the eleven principal section titles remain.
- No candidate prose tokens require newly generated wording under this alignment. Paragraph merging and exact relocation do not count as paraphrasing. The token method is documented in the JSON; it is not a formal linguistic or plagiarism assessment.

## Scientific identifiers and displays

| Chapter | Citation commands, including postnotes | EvidenceRef commands and locators | Labels | All inline/display math blocks | Display equations | Figure/table environments |
|---|---:|---:|---:|---:|---:|---:|
| 3 | 22 | 9 | 9 | 17 | 3 | 5 |
| 4 | 14 | 16 | 12 | 0 | 0 | 2 |

Each column is preserved exactly between A and B; B and C chapter bytes match. The same command, math and figure/table checks were also performed separately for all **21 chapter, appendix and frontmatter source files**; their counts and results are in the JSON. Citation and evidence commands retain their keys, all optional postnotes and locators. Math blocks are identical as multisets; complete display equations and figure/table environments are also identical in sequence and bytes. No figure, table, source asset, equation or label is removed or regenerated.

## Conservative checker flags: reviewed, not hidden

The existing `verify_tex_integrity.py` logs correctly require review because it protects occurrence counts as well as scientific values. It was **not** treated as a clean pass.

- **Chapter 3:** fewer occurrences of `18`, `2`, `6`, `F2`, `PHM`, `PatchTST`, `REASSEMBLE` and `ResNet18-vd` arise in removed duplicate path/selection recaps and the repeated Chapter 6/F2 methodological cross-reference. One ordinary `\ref{ch:methodology}` occurrence is removed. The actual configurations, exact fusion formulas, positive-class distinction, model parameter counts and methodological references remain.
- **Chapter 4:** fewer occurrences of chapter numbers, dates, AUROC/Brier and dataset names arise in deleted repeated study lists, the duplicate reporting-cutoff paragraph and the methodological synthesis. One `\ref{sec:ch4-reproducibility}` occurrence is removed. The labeled section and its complete reporting boundary remain.
- **No distinct numeric token is lost under the repository checker’s convention**, which also matches digits inside identifiers such as F2. With a separate standalone-number convention, Chapter 4 loses only the literal **2** from the introductory “Chapter 2” navigation reference. It is not an experimental value. All scientific numerical values remain in their substantive contexts.
- The full **24 November 2026** experimental reporting cutoff and **25 November 2026** saved-prediction verification remain, along with completed, incomplete and inconclusive study boundaries.
- Exact old/new numeric occurrence contexts and the complete checker reconciliation are retained in `editorial_integrity.json`. The detailed reasons and retained counterparts for deleted passages are in `ch3_changes.md` and `ch4_changes.md`.

## Reversible patches

Patches use paths relative to the LaTeX project. Line endings are preserved, including CRLF in the original chapters. Each patch was applied forward and reversed in a separate `/tmp` copy; every resulting file hash matched the intended frozen state, and reversal recovered every original hash.

| Patch | Scope | Forward and reverse hash reconstruction |
|---|---|---|
| `editorial_A_to_B.patch` | Chapter 3–4 consolidation only | Passed |
| `formatting_B_to_C.patch` | Shared formatting and root wiring | Passed |
| `combined_A_to_C.patch` | Both independently reviewable changes | Passed |

From a copy of the corresponding source state, use `patch --binary --batch -p1 -i /absolute/path/to/PATCH`. Add `-R` to reverse. Do not apply these to preserved snapshot directories.

## Limits

This report verifies source identities, exact retained wording, identifiers, displays and reversible deltas. It does not reproduce training, independently revalidate the earlier empirical findings or cited PDFs, certify university typography approval, or replace the parent task’s compilation and rendered-page inspection. No experiment or build was run by this integrity subtask.
