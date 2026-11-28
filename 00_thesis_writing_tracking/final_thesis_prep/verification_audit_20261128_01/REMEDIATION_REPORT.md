# Final Thesis Verification and Remediation

The authorised text audit and four result plots are complete. The final **204-page draft** builds successfully with XeLaTeX and Biber. The [item-by-item verification table](VERIFICATION_TRIAGE.md) was saved before manuscript edits; its line references point to the preserved pre-audit source snapshot.

[Open the revised thesis PDF](../LaTeX_Project/build/final_audit_20261128_01/final/main.pdf) · [Resolved LaTeX log](final_main.log) · [Biber log](final_main.blg) · [Machine-readable validation](build_verification.json)

## Changes and decisions

- Fixed the Appendix B font leak, promoted shared RGB preprocessing to numbered subsection **C.1.1**, scoped chapter evidence references through the existing opt-in macro, removed the literal E078 tag and the discussion figure’s internal filename, and corrected the caption-anchor warning. `longtable*`, the literature-table reference and distinct legacy label aliases were valid and retained.
- Corrected the MSM comparison to name both HGB-leading protocols, verified the seed-42 F2 AP, unified stacker coefficients, added the gate’s availability domain, clarified implemented patch/mask behaviour, and applied the verified count-macro, wording and glossary corrections.
- Removed source-only audit commentary while preserving it in this audit directory. Reframed the empirical chapters and chronology in author-owned language without deleting raw-overlap, target-validity, selection, missing-evidence, incomplete-training or inconclusive-result limitations.
- Applied UK spelling and British hyphenation, Title Case headings, leading zeros, interval spacing, mathematical minus signs, booktabs rules and consistent citation commands. Short literature-review paragraphs were merged. Existing six-decimal results were retained: the accuracy guardrail takes precedence over rounding every value to four decimals.
- Kept the Faculty I acknowledgements and official cover unchanged. Kept the unnumbered AI disclosure and **Appendix I**, whose file remains `J_prompt_record.tex`; its contents are explicitly retrospective prompt/task summaries, not authentic transcripts. The thesis-structure summary and review-edition reference mappings now match that arrangement.
- Added one within-study result plot to each of Chapters 5–8. No model training, inference, raw-data processing or new uncertainty estimation was run.

## Validation

| Check | Final result |
|---|---|
| XeLaTeX / Biber | Successful; 204 pages; Biber 2.19, `en-GB` locale |
| Undefined citations / references | 0 / 0; PDF contains no `??` placeholders |
| Duplicate labels | 0; literature synthesis resolves to Table 2.1 |
| Overfull / underfull boxes | 0 / 0 |
| Main-chapter tracking IDs | No visible `E###` tags; Appendix F intentionally retains its evidence register |
| Appendix B and C body font | Normal 12-point body text restored; PDF extraction reports size 18 at 1.5 scale after the table and in Appendix C |
| Existing result-table decimals | All 28 checked tables preserve their pre-audit decimal values |
| Bibliography / declaration / acknowledgements | Byte-identical to the pre-audit snapshot |
| Official title PDF | Byte-identical to its pre-existing Git index blob |
| Review-edition references | All explicit outside-label mappings agree with the resolved full-edition AUX; a separate full review-edition PDF was not built |
| Visual review | Four standalone vector plots and their 150-dpi previews inspected; affected thesis pages checked, including captions, the gate equation, Appendix B/C, disclosure and prompt summaries |
| Git safety | Changes confined to thesis preparation; no staging, commit, reset, push, scientific-code edits or experiment mutation |

One intentional LaTeX warning remains: the signing date must be filled in on submission day. The PDF driver also warns about the unchanged supplied cover’s PDF 1.7 version and tag metadata. These are not undefined-reference or compilation failures.

`git diff --check` was run. Its default output flags retained CRLF line endings as trailing whitespace; the CRLF-aware check (`git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check`) passes. Existing line endings were preserved. The repository already contained extensive staged and unstaged work, including bibliography changes; [the audit-only diff](manuscript_changes.patch) compares against the saved starting files and separates this audit from that work. [Audit-only change counts](audit_diff_stat.json) cover 28 existing source files; plot sources and outputs are additional new files.

## Result plots

| Chapter | Vector plot | Interpretation boundary |
|---|---|---|
| 5 — PHM2026 | [MAE comparison](../LaTeX_Project/figures/results_20261128_01/vector/phm_results.pdf) | Existing run-cluster 95% intervals; provisional photographic target; individual-score intervals |
| 6 — REASSEMBLE | [Clean-input AP](../LaTeX_Project/figures/results_20261128_01/vector/reassemble_results.pdf) | Existing recording-cluster 95% intervals; fixed fitted models and exploratory selection history |
| 7 — MSM | [Clean-input AP across seeds](../LaTeX_Project/figures/results_20261128_01/vector/msm_results.pdf) | Bars are sample SD across three fixed seeds, not confidence intervals |
| 8 — ViFailback | [Class-specific and macro AP](../LaTeX_Project/figures/results_20261128_01/vector/vifailback_results.pdf) | Original seed-42 pooled scores; no uncertainty bars or equivalence claim |

[Plot script](../LaTeX_Project/figures/results_20261128_01/plot_results.py) · [Exact source values and hashes](../LaTeX_Project/figures/results_20261128_01/vector/plot_data_and_sources.json) · [Supporting factual checks](SUPPLEMENTAL_EVIDENCE.md)

FM4, NA4, M6A and ALR remain the organiser’s channel labels with descriptive glossary entries; undocumented expansions and units were not invented. The earlier AI model version, exact original prompt wording and unresolved scientific limitations remain explicitly unknown. This audit does not certify university acceptance or reproduce model training.

The protected `\thesisdrafttrue`, `xx November 2026` and `xx. November 2026` remain in place. Changing them is a final-day task, not part of this audit. No author decision remains pending from the four questions answered during the audit.

## Build command

From the active `LaTeX_Project` directory, using the existing retained toolchain:

```bash
source /tmp/chapter_resource_build_20261126_4oux9axd/toolchain/env.sh
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
  -outdir=build/final_audit_20261128_01/final main.tex
```

The plot script uses the existing `/home/student/Master_Thesis_WS/.venv/bin/python` environment. No dependencies or fonts were installed. To reproduce its exports, select a fresh output directory; it refuses to overwrite existing result PDFs.
