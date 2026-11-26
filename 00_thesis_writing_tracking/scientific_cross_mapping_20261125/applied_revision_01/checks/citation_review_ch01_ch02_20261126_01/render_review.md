# Citation rendering check

Both editions compiled successfully with the existing XeLaTeX/Biber toolchain. Full edition:223pages. Review edition:155pages. Final logs contain no unresolved citations/references, Biber warnings/errors, overfull boxes or missing characters. The full edition retains the previously recorded appendixD caption `hypcap=true` warning; the review edition has no LaTeX warnings.

Opened110dpi previews of full-PDF pages13,22,23,25,30,31,40,41,50,62,174,178 and review-PDF pages3,52. These cover the Chapter1 parenthetical citations, narrative author/year conversions, corrected printed-page/table/equation locators, Zeng’s narrative table citation, VideoSwin’s2022 bibliography entry and Ting’s DOI. No clipping or overlap was observed on these pages. All Chapter1–2 rendered text (fullPDF13–63) was extracted for inspection in `citation_render_text.txt`; visual inspection was sampled rather than page-by-page.

The full bibliography correctly distinguishes the HANDOVER **dataset** (Thoduka et al.,2024a,Zenodo DOI10.5281/zenodo.10708763) from the **conference paper** (2024b,IEEE DOI10.1109/ICRA57147.2024.10610143). These are different citable objects, not duplicate entries. The paper renders2024b in the checked body citations. Initials added to Li/Wang/Zhang citations follow APA name disambiguation and match the associated bibliography entries.

Confirmed render examples:

- “Baltrušaitis et al.(2019)” and “Ting and Witten(1999)” occur once in the revised narrative passages.
- Kullu and Cinar(2022) now renders the two authors from the record, replacing the manuscript’s generic “Kullu et al.” author phrase.
- P035 renders printed6659/6661; Hua renders printed6708/6711 or verified table locators.
- The learned-scalar equation renders An et al.(2026),p.149226,Eq.8.
- The substation citation renders Figure8 without the incorrect viewer-page29 association.
- Bengio and Grandvalet renders pp.1096–1098,1102–1104.
- Zeng renders2026,Tables2–4 once with the author name.
- VideoSwin lists2022 and3202–3211; the long official CVF URL wraps within the text width.
- Ting lists1999 and DOI10.1613/jair.594.

No source prose was changed during rendering review. The two flagged scientific wording decisions remain in `CHANGELOG.md`. Compiler results, PDF hashes and inspection scope are in `build_validation.json`. Older top-level delivery PDFs/archives were not replaced by this citation task; use the new PDFs in this check directory.
