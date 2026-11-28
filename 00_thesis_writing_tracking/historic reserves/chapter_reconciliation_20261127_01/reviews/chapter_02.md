# Chapter 2 reconciliation

The [active literature review](../../Thesis/LaTeX_Project/chapters/02_literature_review.tex) now follows the supplied literature-focused wording and cited synthesis table. The [starting chapter](../before/chapters/02_literature_review.tex) and [external chapter](../external/02_literature_review.tex) were re-read and checked against the actual active and supplied files before editing. Both remained byte-identical to the comparison snapshots; no ancestry was inferred from that correspondence.

Only active Chapter 2 was edited by this agent. Its existing LF line endings were preserved. Chapter 4 was coordinated with its owning agent; no other chapter, bibliography, figure source or asset was changed here.

## What changed

- Adopted the external opening, literature-focused section text, and final table of concrete cited findings and limits. The table keeps the distinction between industrial evidence and transferable methods, and between target-specific fitting and unchanged-model transfer.
- Retained the literature finding that four of the initial 37 appraised papers examined planned missing-input inference and one examined simulated dropout: five of 37, or 13.5%, at line 710. It is not presented as the rate in the expanded 94-work appraisal or the entire research field.
- Removed thesis-specific R1–R5 derivation, study-selection/mapping text, and the welding-to-requirements figure from Chapter 2. Chapter 4's owner retained their useful substance in its opening design section, including the current MSM/ViFailback scope and HANDOVER limitations. The four relocated labels are owned there: `sec:literature-study-gaps`, `tab:fusion-study-scope`, `fig:ch02-synthesis-requirements`, and `fig:fusion-research-gap`.
- Preserved Chapter 2's own labels: `ch:literature`, `fig:prediction-availability`, and `tab:literature-synthesis`. The prediction-availability PDF remains its sole figure dependency.
- Narrowed the TCP-position statement at lines 359–361. It now says that the inspected author manuscript uses TCP positions for spatial registration and does not list them among its 27 sensor features. It no longer claims that position is generally not predictive. This correction follows the earlier [industrial source audit](../../scientific_cross_mapping_20261125/applied_revision_01/checks/citation_review_ch01_ch02_20261126_01/claims_industrial.md), item C2-IND-01. Manuscript-to-version-of-record equivalence remains unverified; this pass did not recheck the original publication.

Apart from that necessary scientific qualification, canonical citation identities, and retained unresolved page comments, the external Chapter 2 wording was preserved.

## Citation reconciliation

The [citation map and evidence receipt](chapter_02_citation_map.json) records all 75 external citation keys: 72 renamed keys and three unchanged keys. Every mapping was derived from at least one exactly aligned passage after replacing only the citation-key contents and ignoring the existing page-check comment. Repeated alignments produced no conflicting mapping. The receipt includes original and external line anchors, existing bibliography titles and identifiers, and source hashes.

All mapped keys exist in the two bibliography files loaded by the active project. No bibliography entry was added or changed. Existing corrected page, table and section locators were retained. This establishes source and bibliography consistency; it is not new verification of 75 papers.

The phrase “94 appraised works” in the external final summary is retained because current Appendix A explicitly describes 57 additional works and 94 total across the two appraisal stages. The initial 37-work percentage remains separate.

## Page-check comments

Seven `[VERIFY PAGES]` comments remain because the earlier source records identify viewer-only pagination or a version limitation that the later syntax cleanup did not resolve:

| Active Chapter 2 line | Citation and retained locator |
| --- | --- |
| 234 | `Thoduka2024Handover`, page 7 and Section VI |
| 243 | `P003`, pages 6–7 |
| 614 | `Thoduka2024Handover`, pages 5–7 |
| 645 | `P026`, pages 3–5 |
| 849 | `Altinses2023Fuzzy`, pages 3–5 |
| 882 | `Altinses2023Fuzzy`, pages 4–5 |
| 917 | `P031`, page 7 |

Of the original 29 comments, five retained passages had printed pagination already established by the November 26 [primary-source audit](../../scientific_cross_mapping_20261125/applied_revision_01/checks/citation_review_ch01_ch02_20261126_01/claims_papers.json): P021, P022, P024, P025 and P045. Those comments were cleared by reference to that prior evidence, not a new source check. Twelve comments accompanied table-only locators after their page numbers had already been removed, so the pagination question no longer applied. Five other comments belonged to removed or relocated thesis-mapping passages; the Chapter 4 owner was told about the unresolved Sliwowski page locator and did not transplant an unverified page number. The receipt records every disposition individually.

## Checks performed

- Actual active bytes matched the preserved starting copy immediately before replacement; no concurrent Chapter 2 edit was overwritten.
- All 75 resulting unique citation keys resolve to existing bibliography records; each mapping has alignment evidence and a recorded title.
- Reviewed the complete substantive difference against the citation-reconciled external text: the TCP correction and seven retained comments are the only remaining text differences.
- Simple TeX brace balance and ordered environment nesting passed. The three retained labels are unique within the chapter; moved labels are absent.
- The remaining literal figure path exists. No diagram asset was modified.
- Scoped `git diff --check` passed. The resulting file has 1,123 lines with LF line endings and SHA-256 `474c5161de33814e11bdd4e547a4fec4c1017d9d5d5943207d4718b97107b666`.

No PDF was built by this agent. The parent agent owns the combined thesis build and rendered inspection, including the longer cited synthesis table and relocated Chapter 4 floats. The seven pagination/version questions above remain open; no publication re-verification or experimental reproduction is claimed.
