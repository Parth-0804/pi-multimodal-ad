# LTeX+ pilot: Chapters 1–4

Prepared on 27 November 2026 from the active thesis working tree, including its uncommitted edits. The chapter sources used by `00_thesis_writing_tracking/Thesis/LaTeX_Project/main.tex` were copied from its `chapters/` directory. The original files and active thesis are unchanged; SHA-256 checks are recorded in `reports/preservation_checks.json`.

## Files to read

- `reworked/tex/`: revised Chapter 1–4 LaTeX source copies.
- `reworked/txt/`: four content-only chapter exports and `Chapters_01_04.txt` containing all four in order.
- `original/tex/` and `original/txt/`: matching before-edit versions for comparison.
- `CHANGES.md`: all 30 edits, with their before/after wording and origin.
- `reports/source_changes.diff`: complete source diff.
- `reports/ltex_comparison.md`: before/after checker results.

The entire pilot folder is excluded by the root `.gitignore`. Git reports no tracked files within it. The only repository file changed for this pilot is `.gitignore`; pre-existing work was preserved. Nothing was committed or pushed.

## Review method and outcome

Official LTeX+ LS 19.0.0 ran locally with its bundled LanguageTool 6.8 and Java 21.0.10. British English and a small scientific dictionary were fixed before the original check and reused unchanged for the revised check. The checker used its bundled engine; thesis text was not sent to a remote checking service. Its installation, release checksum, commands and input identities are saved under `reports/` and `tools/`.

| Chapter | LTeX+ flags before | Flags after | Accepted tool-prompted edits | Manual edits |
|---|---:|---:|---:|---:|
| 1: Introduction | 8 | 5 | 3 | 6 |
| 2: Literature review | 93 | 86 | 6 | 10 |
| 3: Technical foundations | 23 | 22 | 1 | 2 |
| 4: Methodology | 25 | 25 | 0 | 2 |
| Total | 149 | 138 | 10 | 20 |

Suggestions were reviewed individually. Retained flags concern technical names, code identifiers, custom-command parsing, acceptable British spelling, deliberate structure or valid wording. Chapter 2's conditional-sentence correction was adapted rather than inserted verbatim. One manual simplification also removed a flag, explaining the reduction of 11 flags from 10 accepted diagnostics. No new diagnostic signatures appeared. These counts describe checker output, not a score of scientific quality or authorship.

Codex made the recorded copyedits, reviewed the resulting diff and prepared the plain-text exports. The edits preserve the author's interpretation and paraphrased wording around the changed phrases. Results, qualifications and methodological boundaries were reviewed in the diff; the underlying experiments and cited papers were not re-analysed for this language pilot.

## Source and export checks

The source checks passed for numeric tokens, citation commands, references and labels, headings, mathematical expressions, tables, diagrams and figure calls. All 30 edits are accounted for in the change log. Active chapter hashes still match their starting snapshots. `git diff --check` passed. No compilation, rendering or PDF regeneration was run.

The same source-to-text conversion was applied to both versions. TXT files contain headings, prose, readable citations and references, captions, table content and linear equations. LaTeX formatting, comments, graphic paths and evidence-only annotation blocks are removed. Chapter 2 includes the figure's seven topic-count rows, four coding categories and explanatory note, plus all eight closing-table questions. Diagram graphics themselves are not transcribed. Reference numbers and citation forms come from existing compilation records and bibliography metadata; no new build was performed. No unresolved references or citations remain in the exports. Details and limitations are in `reports/text_export.json`.

These chapter copies form a proofreading pilot, not a separate complete build project. Supporting files in `support/` are snapshots used for text conversion; the active thesis remains the build project.

## Repeating checks

From this pilot folder:

```sh
python3 scripts/check_preservation.py
python3 scripts/export_text.py
```

The LTeX+ commands are documented in `tools/README.md`; their runner protects completed reports against overwrite. All downloaded tools and conversion dependencies are isolated inside this ignored folder.
