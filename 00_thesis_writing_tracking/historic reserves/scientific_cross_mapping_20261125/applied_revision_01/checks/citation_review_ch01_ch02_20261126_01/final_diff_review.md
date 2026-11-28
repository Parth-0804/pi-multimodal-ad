# Independent review of the citation correction diff

Reviewed `citation_corrections.patch` against the preserved pre-task sources in `before/` and the active working manuscript on 2026-11-26. This is a source and scientific-scope review, not a compilation or rendering check. No manuscript or bibliography edits were made by this reviewer.

## Outcome

The actual diff stays within the requested citation corrections. Chapter 1 changes only seven `\citep` commands to native APA `\parencite`. Chapter 2 changes citation commands, 14 narrative author attributions, verified locators, and removes one unsupported reference from the terminology sentence about “late fusion.” The shared bibliography has only the P013 publication metadata correction and the Ting DOI addition.

Independent checks established:

- The patch reproduces the current differences from `before/` exactly.
- Exactly four of the 79 working-source files in `before.json` changed: Chapters 1–2 and the two bibliography files. `main.tex`, the abstract, other chapters, tables, figures and supporting sources retain their recorded hashes.
- All 56 files in the preserved revision baseline retain their recorded hashes.
- Chapter 1 citation-key occurrence counts are unchanged. Chapter 2 removes exactly one occurrence of `Xie2025Audiovisual`; no citation key was added or otherwise removed. Its narrative citation in the acoustic-observations section remains.
- After excluding citation commands and the two explicit author-year strings replaced by narrative citations, the numerical-token sequence is identical in both chapters. Scientific numerical results, counts and table data were preserved.
- Existing `\ev`, `\EvidenceRef`, `\label` and `\ref` token sequences are unchanged. Embedded tabular content is unchanged.
- No `\citep` remains in Chapters 1–2.

## Narrative citation review

All 14 narrative conversions are grammatical in their surrounding sentences. The changes replace literal author names or author-year strings with `\textcite`, with only the local word order and punctuation needed for that substitution. They do not add or remove scientific claims.

| Current Chapter 2 line | Narrative key | Grammar and attribution check |
|---|---|---|
| 76 | `Baltrusaitis2019Multimodal` | “The taxonomy of [authors (year)] is…”; avoids duplicated year |
| 99 | `Ting1999Issues` | “paper by [authors (year)] was included…” |
| 201 | `AlDulaimi2019A` | Plural author subject with “look” |
| 206 | `Altinses2025Performance` | “benchmarks of [authors (year)] examine…” |
| 220 | `Petrich2021Multimodal` | “study by [authors (year)]” |
| 221 | `Li2022A` | “quality classes in [authors (year)]” |
| 222 | `Pandiyan2022Deep` | “labels in [authors (year)]” |
| 319 | `Kullu2022A` | Plural author subject with “combine” |
| 320 | `Wan2024Pipeline` | Plural author subject with “derive” |
| 321 | `Wang2025A` | Plural author subject with “combine” |
| 343 | `Li2022A` | “the study by [authors (year)] is…” |
| 344 | `Xie2025Audiovisual` | Plural author subject with “use” |
| 956 | `Petrich2021Multimodal` | Plural author subject with “report”; numbers unchanged |
| 1389 | `Zeng2026ViFailback` | Plural author subject with “use”; verified Tables 2–4 retained |

## Locators and shared metadata

P006 Section 3.1/Table 2, P035 printed pages 6659/6661 and P038 printed page 149226 match the direct PDF checks in `claims_papers.json`. P051 Figure 8 correctly avoids conflating its PDF page 30 location with the adjacent missingness paragraph on page 29 of the browser printout. Source-specific table references retained for welding and thermal-vibration results avoid misleading pagination. Other changed locators are supported by the root and industrial source-check records; no unverified new numerical claim appears in the diff.

The reference removed from the late-fusion terminology sentence is only `Xie2025Audiovisual`. The retained Wang paper explicitly uses “late fusion” for concatenation before the classifier. Xie remains cited where the passage concerns its actual camera observations.

The official [CVF Video Swin page](https://openaccess.thecvf.com/content/CVPR2022/html/Liu_Video_Swin_Transformer_CVPR_2022_paper.html) was independently retrieved through `urllib` after the browser tool returned 403. Its embedded citation metadata and BibTeX confirm 2022, CVPR, pages 3202–3211 and all seven listed authors. The shared P013 key is retained. Its uses in Chapter 3 and the literature matrix contain no literal conflicting year; they inherit the corrected bibliography year. The earlier local 2021 preprint attachment remains separately identified in the provenance notes.

The original [JAIR article page](https://www.jair.org/index.php/jair/article/view/10228) independently confirms Ting and Witten, publication in May 1999, volume 10, and DOI `10.1613/jair.594`. Adding that DOI leaves the existing key and other record fields intact.

## Open prose decision, outside this citation-only diff

The existing sentence in Chapter 2, Feature Concatenation, reads:

> M3DM's direct concatenation ablation is worse than its point cloud reference, while the full hybrid system outperforms both individual inputs.

The “worse” clause needs an endpoint qualifier. Table 4 of the M3DM paper gives direct concatenation (“w/o UFF”) image AUROC .857 versus .874 for point cloud alone, but AUPRO .944 versus .906 and pixel AUROC .987 versus .970. The full system improves all three endpoints over each individual input. Therefore the first clause is supported specifically for **image AUROC**, not all performance metrics. This wording predates the task and is unchanged in the citation patch. The researcher should approve adding “in image AUROC” rather than silently broadening a citation correction into a claim edit.

## Traceability log

The interference-only Table 3 repair is now explicitly anchored by its sentence and current line in `edits.json`. The actual patch changes only that interference result and retains Tables 1–3 for clean accuracy. Chapter 1’s original CRLF line endings were also retained; its content changes are exactly seven citation-command substitutions.
