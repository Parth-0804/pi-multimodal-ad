# Independent citation inventory completeness check

Read-only check against the active `working/LaTeX_Project/main.tex` and its Chapter 1–2 sources, performed before the planned citation-command edits. No manuscript or bibliography changes were made by this agent.

- `main.tex` loads `chapters/01_introduction.tex` and `chapters/02_literature_review.tex`, and both `references.bib` and `references_additions.bib`. Its bibliography configuration is `backend=biber,style=apa,natbib=true`.
- Chapter 1: **7 citation commands, 13 key instances, 10 unique keys**.
- Chapter 2: **148 citation commands, 235 key instances, 79 unique keys**.
- Combined: **155 commands, 248 key instances, 79 unique keys**. This independently matches `inventory_before.json` and `keys.json`; the symmetric difference in keys is empty.
- Neither chapter has nested `input`/`include` files, footnotes or inserted figures. Chapter 2 contains the synthesis longtable directly in the source. Its initial and continuation captions have no citations, and there are no table-note citations omitted from the inventory. The table’s claims are supported in the surrounding cited discussion; row-specific citation adequacy remains a scientific-review judgment rather than an inventory omission.
- No unconverted numeric reference brackets, numbered-PDF markers, `paper_N` markers or orphan `Pxxx`/`F-number` references were found outside citation-command arguments. Remaining square brackets are LaTeX list options, the empty continuation-caption option and row-spacing arguments.
- All keys resolve across the two loaded bibliographies. Retain Pxxx citation keys: their use inside a citation command is valid and not a visible paper-ID citation. Their source identities are mapped in `CITATION_PDFS.csv` and the literature crosswalk.

## Narrative citations requiring APA commands

Two literal author–year constructions duplicate nearby parenthetical citations:

| Chapter 2 line before edits | Literal reference | Existing correct key |
|---|---|---|
| 76 | Baltrušaitis et al. (2019) | `Baltrusaitis2019Multimodal` |
| 100 | Ting and Witten (1999) | `Ting1999Issues` |

Other named-author phrases with nearby parenthetical commands occur at lines 203 (Al-Dulaimi), 222 (Petrich), 223 (Li), 224 (Pandiyan), 321 (Kullu), 322 (Wan), 323 (Wang), 345 (Li), 346 (Xie), 961 (Petrich) and 1395 (Zeng). These have matched keys in the existing inventory and should become `textcite` constructions while preserving their existing claims and verified postnotes. Their current form is imprecise command choice rather than an unidentified source.

## Internal evidence register

Chapter 1 has five `EvidenceRef` instances using E001–E004. These are stable project evidence IDs rather than bibliographic references. `main.tex` loads `evidence_links.tex`, which loads `tables/evidence_register.tex`; E001, E002, E003 and E004 all exist there. Preserve their IDs and locators. Their currently empty external URLs are unrelated to Zotero citation-key resolution.

## Shared metadata dependencies

`P013` currently combines the 2021 arXiv read version with the CVPR proceedings venue. The published CVPR record is from 2022, subject to root’s official-source confirmation. The same key is used in Chapter 3 and `tables/expanded_literature_matrix.tex`. Neither location hard-codes a conflicting 2021 author–year reference. They describe Video Swin’s spatial/temporal mechanisms, so a verified published-year correction introduces no scientific-prose contradiction. Preserve the stable P013 key and retain the inspected 2021 preprint version in the audit record; publication metadata does not prove final-version passage identity.

`Ting1999Issues` is already loaded from `references_additions.bib`. Adding root’s independently primary-verified DOI `10.1613/jair.594` to this existing key does not require a new record. Shared references in Chapter 9, Appendix A and the separate draft-figure captions are consistent with 1999. The method addition remains distinct from the historical 94-work review count. There are no duplicate DOI or normalized-title records in the two current bibliographies.

This check establishes inventory completeness and shared-key dependencies. It does not replace the separate PDF passage and locator checks.
