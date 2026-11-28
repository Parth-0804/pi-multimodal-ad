# LTeX+ before/after checks

Both checks completed with LTeX+ LS 19.0.0 / Java 21.0.10, the same frozen British-English settings and vocabulary, and the bundled local LanguageTool 6.8 checker. Exit code 3 means suggestions were found; it is not a tool failure.

| Chapter source | Before | After |
|---|---:|---:|
| 01_introduction.tex | 8 | 5 |
| 02_literature_review.tex | 93 | 86 |
| 03_foundations.tex | 23 | 22 |
| 04_methodology.tex | 25 | 25 |

Total: 149 → 138. No new diagnostic signatures appeared.

Counts are checker suggestions, including false positives and style preferences. Their reduction is not a score of scientific correctness, writing quality, human authorship, or AI detectability. Line shifts are ignored when comparing signatures.

Raw unfiltered records, exact commands, input hashes, configuration hashes and tool versions are retained in the matching `ltex_original` and `ltex_reworked` files. Suggestions were manually reviewed; none were applied automatically.
