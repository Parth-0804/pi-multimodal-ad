# Thesis baseline for the professor copy

The supplied [full draft](PDFs/DRAFT_Thesis_2026-11-20_FULL.pdf) is the 20 November 2026 v2 release. It matches the archived full draft and the PDF embedded in the original evidence bundle byte for byte. The [review edition](PDFs/DRAFT_Thesis_REVIEW%20CHAPTERS.pdf) also matches the corresponding bundled PDF. The full draft SHA-256 is `30a55e9fd13fe0878b0d067ffa28ba1d787e8fe3b8db47ae2dbfec9faad70bd7`.

## Working source

- Open [main.tex](LaTeX_Project/main.tex) for the complete thesis or [review.tex](LaTeX_Project/review.tex) for the review edition. Both use the original [references.bib](LaTeX_Project/references.bib).
- The project contains all 53 files from the matching Overleaf release, including ten chapter PDFs, plus three source assets from the bundled manuscript. All 41 shared files match byte for byte.
- Both editions built from a clean copy with the recovered XeTeX and Biber toolchain. Compared with the release PDFs, all 193 full-draft pages and all 132 review pages matched in extracted text and rendered appearance. Biber resolved 107 citations in each build.
- The [original v2 evidence bundle](Release/Thesis_2026-11-20_v2_LaTeX_and_Evidence.zip) preserves the release record, chapter Markdown and supporting evidence for this version.

## References

The [citation index](References/CITATION_PDFS.csv) covers all 110 BibTeX entries and identifies the 107 printed references. Recovered PDFs cover 90 of those 107 references. The remaining 17 entries are flagged and retain their bibliography metadata and identifiers where available. [PDF provenance](References/PDF_PROVENANCE.csv) identifies each recovered file and its checksum. The 37-work and 94-work literature registers are under [literature_review](References/literature_review/).

[SHA256SUMS.txt](SHA256SUMS.txt) records the bytes at import for comparison with later revisions.
