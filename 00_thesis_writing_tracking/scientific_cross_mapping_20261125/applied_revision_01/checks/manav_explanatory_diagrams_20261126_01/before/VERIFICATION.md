# Current delivery verification — 26 November 2026

The current [validation record](checks/final_manav_delivery_20261126_01/validation.json) covers the PDFs and source ZIP linked in the package README. Previous delivery files and reports are preserved in [before/](checks/final_manav_delivery_20261126_01/before/); older records describe their own dated versions.

All three editions were rebuilt successfully from the same [fixed source snapshot](checks/final_manav_delivery_20261126_01/source_snapshot/), using the existing authorized isolated XeLaTeX/TeX Live 2023, Biber 2.19 and latexmk 4.83 toolchain. No dependency installation was needed.

| Edition | Root | Pages | Final checks |
| --- | --- | --- | --- |
| Complete thesis | `main.tex` | 272 | No unresolved citations/references, Biber warnings/errors, duplicate-label warnings, overfull boxes or missing characters. One pre-existing appendix caption/hypcap warning remains. |
| Abstract + Chapters 1–10 | `review.tex` | 202 | Same checks passed; no LaTeX warnings. |
| Manav: Abstract + Chapters 1–4 | `manav_review.tex` | 124 | Same checks passed; no LaTeX warnings. |

All fonts are embedded. All 108 keys in the shared APA citation context agree across the three Biber control files. Each of Manav's 124 extracted text pages matches the corresponding page of the complete review edition. The excerpt starts with the Abstract and ends with the complete final paragraph of Chapter 4; later chapters are not included. References to omitted material retain plain full-edition numbers. The full thesis retains the reference list; review editions retain in-text citations.

The latest Chapter 2 figure page and Chapter 4 closing page were rendered and opened for this delivery. The diagram, caption and note fit without clipping; the final paragraph stays on page 124. Unchanged tables, equations, figures and citation rendering were inspected in the [Chapter 3–4 record](checks/ch03_ch04_update_20261126_01/validation.json) and [Chapter 1–2 citation record](checks/citation_review_ch01_ch02_20261126_01/build_validation.json). This is bounded visual inspection, not a page-by-page visual audit of the thesis.

The 60-member source ZIP passes ZIP integrity checks and matches the build snapshot byte-for-byte. It contains all three build roots, shared bibliography, included figures and their available source/support files. Temporary builds, stale historical chapter PDFs and unselected draft diagrams are excluded. The [snapshot manifest](checks/final_manav_delivery_20261126_01/snapshot_manifest.json) records identities; a documentation-only concurrent figure-README update was included after the build inputs were frozen. Final packaged sources match their active working versions.

The cumulative revision patch includes the binary vector figure. `git apply --check` passed, and applying it to a temporary baseline reconstructed all 60 packaged files exactly. Original baseline-only historical files were retained. The [baseline check](checks/final_manav_delivery_20261126_01/baseline_check.json) confirms all 56 baseline identities. The established integrity checker reports **review required**, as expected for the approved author chapter replacements and earlier scientific/citation changes. This is not a zero-change integrity pass. The [integrity report](checks/final_manav_delivery_20261126_01/pipeline_integrity.txt) is reconciled by the earlier dated change/citation records and the unchanged final build inputs; the extra Manav root duplicates the approved preamble and excerpt sources.

The scientific checks were not repeated as training or new experimental analysis. The earlier [F2 saved-score audit](checks/f2_recheck/results.json), [ViFailback saved-score check](checks/vif_saved_score_recheck.json), and [original scientific verification](checks/final_manav_delivery_20261126_01/before/VERIFICATION.md) retain their stated scopes and limitations. The final packaging pass changed no scientific prose or results.

The [citation review](checks/citation_review_ch01_ch02_20261126_01/CHANGELOG.md) used curated/reconstructed exports, local source PDFs and archived Zotero attachment provenance because Zotero Desktop and the native current export were unavailable. It does not verify current collection membership. Two previously flagged Chapter 2 wording decisions remain for the author: the TCP-position claim's generality, and the missing image-AUROC qualifier in the M3DM concatenation comparison. Neither was silently rewritten during packaging. Other version/provenance limits remain in that review.

The DRAFT watermark, manuscript scope limits, negative and unfinished findings, and human submission-review requirements remain applicable. No model training, inference, new fitting or new literature discovery was performed. No Git commit or push was made.
