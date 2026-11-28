# Chapters 1–2 citation review — 26 November 2026

Applied to the working `applied_revision_01/working/LaTeX_Project` source. `main.tex` includes `chapters/01_introduction.tex` and `chapters/02_literature_review.tex`; both use `references.bib` and `references_additions.bib` with Biber and `style=apa`. The pre-edit files are in `before/`; the exact four-file diff is [citation_corrections.patch](citation_corrections.patch).

## Coverage and source access

The original inventory contains **155 commands, 248 key occurrences and 79 works**. The final inventory retains 155 commands and 79 works, with 247 key occurrences after removing one inaccurate attribution. No missing keys or exact DOI/title duplicates were found in the active bibliographies. There are no nested chapter sources, footnotes or inserted figure captions. Both synthesis-table captions and all table content were checked; they contain no separate citations. No orphan bracketed PDF numbers or paper IDs were found. `Pxxx` keys remain stable internal citation keys. Evidence IDs E001–E004 and their register links are unchanged.

**Zotero Desktop/API/connector were unavailable.** No profile or settings were changed. The recorded native `Zotero_2026-11-24_export.bib` was not available. Matching therefore depends on the existing curated/reconstructed `review_references` and `original37_references` BibTeX/CSL files, the citation/PDF registers and archived attachment provenance. These do not independently establish current thesis-collection membership or parent Zotero item IDs. Archived storage keys identify attachments, not confirmed parent records.

Seventy registered local PDF identities and hashes were checked; original cited passages were inspected, with original HTML/manuscripts used for four works lacking local PDFs. Ting’s original JAIR facsimile was checked separately. Official pages support the software, metadata-service and PHM references. Final-source follow-ups resolved P017 and Sui. Metadata printed in the inspected source is independently checked; fields absent from its header remain export-supported. Full per-key details are in [citation_record_crosswalk.csv](citation_record_crosswalk.csv), [metadata_review.json](metadata_review.json) and the three `claims_*.json` reports. This is a citation/source audit, not a rerun of the published experiments.

## Compact change log

Line numbers refer to the preserved pre-edit sources. The [complete command-level log](citation_change_log.csv) gives original and final commands and both line locations.

| Chapter/location | Original reference | Applied correction | Basis |
|---|---|---|---|
| Ch1, all seven citation commands | `\citep` | `\parencite`, same keys and postnotes | Native APA parenthetical command; original source matches retained |
| Ch2, throughout | `\citep`; literal author names followed by another author–date citation | 134 `\parencite` and 14 `\textcite` commands | Named authors now render once with the record’s year; includes Baltrušaitis, Ting/Witten, Al-Dulaimi, Altinses/Schwung, Petrich, Li, Pandiyan, Kullu, Wan, Wang, Xie and Zeng |
| Ch2 §2.1.5, line159 | Hua `PDF pp.12,15`; P035 `PDF p.10` | Hua printed pp.6708,6711; P035 p.6661, Tables IV,VI–VII | Publisher cover offsets checked; source inconsistencies preserved |
| Ch2 §2.2.1, line188 | P035 `PDF p.8` | `\parencite[6659]{P035}` | Printed6659=viewer8; anomalous-label supervision |
| Ch2 §§2.4.1 and2.7.5, lines410/1048 | P035 `PDF p.10,TableV` | p.6661,TableV | Original parameter/timing table |
| Ch2 §2.5.1, line567 | Hua `PDF pp.18,22,Tables1–3` | Tables1–3 | Clean comparisons at printed6714/6718; no viewer index needed |
| Ch2 §§2.5.3 and2.6.2, lines630/782 | Huo `PDF p.7,TableVII/VIII` | TableVII/VIII | Original tables; article-ID pagination avoided |
| Ch2 §2.5.3, line643 | Wang2020 + Xie2025 for the exact term “late fusion” | `\parencite{Wang2020What}` | Wang explicitly uses that term for representation concatenation; Xie calls its method “decision-level fusion.” Xie remains cited for its actual camera/audio method |
| Ch2 §2.5.4, line666 | P006 Section3,Table2 | Section3.1,Table2 | Method subsection and numerical comparison verified |
| Ch2 §2.5.4, line684 | P038 `PDF p.3,Eq.8` | printed p.149226,Eq.8 | Original equation and printed page |
| Ch2 §2.6.1, line755 | P051 `PDF p.29,Figure8` | Figure8 | Missingness prose on viewer29; figure on viewer30; browser footer is not article pagination |
| Ch2 §2.6.2, line788 | Hua Tables1–3 | Table3 | Interference result specifically in Table3, printed6718 |
| Ch2 §2.6.4, line838 | QMF `PDF pp.4–5` | Sections3.1–3.2 | Distribution assumption begins on viewer3; theorem follows on viewer4 |
| Ch2 §2.7.3, line990 | Bengio `PDF pp.8–10` | printed pp.1096–1098,1102–1104 | Covariance/theorem and underestimation discussion checked |
| Ch2 §2.8.4, line1396 | Zeng author text + `PDF pp.7–8,Tables2–4` | `\textcite[Tables~2--4]{Zeng2026ViFailback}` | Original tables at printed42392–42393; one narrative attribution |
| Shared bibliography, P013 | 2021 arXiv year with CVPR venue | **2022**, pp.3202–3211, official CVF URL; key retained | [Official CVPR publication and BibTeX](https://openaccess.thecvf.com/content/CVPR2022/html/Liu_Video_Swin_Transformer_CVPR_2022_paper.html). Chapter3 and the appendix matrix share this key; neither hard-codes a conflicting year |
| Shared additions, Ting1999Issues | Correct1999 record without DOI | Added **10.1613/jair.594**; key retained | [Original JAIR publisher record](https://jair.org/index.php/jair/article/view/10228). No duplicate/new work introduced |

All other verified locators were retained, including explicit **PDF** indices where the inspected version lacks usable printed pagination. A table or section locator is used where it avoids version-dependent page offsets. Quantitative results, research questions, labels, evidence links, table data and qualifications were preserved. No new references were added.

## Two author decisions remain open

### C2-01 — Ch2 §2.3.4, original lines366–368

> The digital twin study maps sensor features to robot TCP positions, showing how position can establish correspondence even if it is not, in any normal sense, a predictive feature.

**Source:** Chen’s author-uploaded manuscript §§3.4–3.5, pp.19–21. TCP positions register features and prediction outputs; the predictor lists27 sensor features. The publisher version was inaccessible, and manuscript-to-published equivalence was not verified. This supports the registration role but does not establish that position cannot be predictive in general.

**Decision:** approve narrowing the last clause to the study-specific feature list, for example: “TCP positions register sensor features and prediction outputs; they are not among the study’s27 listed sensor features.” The current wording was left unchanged.

### C2-02 — Ch2 §2.5.2, original lines601–602

> M3DM's direct concatenation ablation is worse than its point cloud reference, while the full hybrid system outperforms both individual inputs.

**Source:** Wang et al., Table4, printed8038/viewer7. The statement holds for **image AUROC**: .857 direct concatenation versus .874 pointcloud and .945 full model. It does not hold for all reported metrics: concatenation AUPRO .944 exceeds pointcloud .906.

**Decision:** approve adding “For image-level AUROC,” to this sentence. The current wording and numerical table were left unchanged.

## Remaining access/version limits

- Baltrušaitis: local2017v2 preprint; final2019 record/abstract checked. No preprint page number was presented as final pagination.
- P017: local2022v1, but the **final2023 Patterns full text** was also inspected through NCBI’s BioC endpoint; preprocessing, feature-selection and dependent-unit leakage claims are supported there.
- Sui: local2024v3; the **final Information Fusion126(2026),103572 PDF** was additionally checked. Its method supports multimodal training/single-input inference. Retain the2026 key/year.
- HANDOVER: the local2025v2 carries the published2024 IEEE work’s cover. Viewer-page locators explicitly identify this inspected version. Full equivalence to the original2024 proceedings PDF was not independently established.
- MADFlow: the inspected accepted/preprint manuscript supports the concatenation/alignment discussion; final Neurocomputing pagination and full version equivalence were not independently established. The published record remains, with this limitation recorded.
- Current Zotero collection completeness and fields absent from inspected primary headers remain unverified; the per-record crosswalk separates these from checked source fields.

## Validation

Build and rendering results are recorded in [build_validation.json](build_validation.json) and [render_review.md](render_review.md). The existing temporary XeLaTeX/Biber toolchain was reused; no dependencies were installed. Fresh full and review builds use these edited sources. The original56-file baseline is unchanged, as are all working files outside the two chapters and two bibliography files. The integrity checker flags the intentional citation/year/locator changes; protected-content checks confirm unchanged non-citation numerical evidence, tables, math, research questions and evidence links. See [source_validation.json](source_validation.json) and [final_diff_review.md](final_diff_review.md).
