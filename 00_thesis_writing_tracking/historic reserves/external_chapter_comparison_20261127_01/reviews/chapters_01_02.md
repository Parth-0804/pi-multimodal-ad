# Comparison of external Chapters 1 and 2

Reviewed 27 November 2026. This is a comparison of the preserved snapshots, not an integration or a new scientific-source audit. No manuscript source was edited or compiled. Repository HEAD was `2ae0c76e3d377a0fae3361c00f2e7d65f704545a`; substantial pre-existing changes were present.

The **current** and **pre_revision** snapshots establish which changes were made locally during the November 27 revision. The external files' ancestry is unknown. A passage matching `pre_revision` shows textual correspondence, not why the external author used it or when their work began. Source anchors below name snapshot files followed by line numbers; abbreviated `current/` and `external/` paths are under `snapshots/` in this comparison directory.

## Recommended integration order

1. Retain the current Chapter 1 study-scope paragraph and the November 27 MSM/ViFailback table additions. Adopt the external dynamic references and clearer methodology roadmap around them.
2. Consider the external Chapter 2 editorial structure together with its Chapter 4 relocation. It removes repeated thesis-specific explanations and replaces the generic synthesis table with concrete, cited findings and limitations. Do not apply Chapter 2 independently of the corresponding Chapter 4 material.
3. Reconcile citation identities, the HANDOVER table qualification, and figure/table ownership before any build. Preserve verification questions separately; deleting a source comment does not resolve it.
4. Compile the combined proposal and inspect the moved floats and rewritten longtable before accepting it. This review makes no claim about rendered layout or original-paper verification.

## Chapter 1: small changes, with one local addition to preserve

The external Chapter 1 differs from the current file only within the thesis-structure section. No citation keys, figures, or labels change.

| Finding | Evidence | Recommendation |
| --- | --- | --- |
| Dynamic Chapter 2 and Chapter 4 references improve maintenance. The Chapter 4 description now names the requirements and empirical mapping in its opening section. | `snapshots/external/01_introduction.tex:299`, `:307`; current equivalent at `snapshots/current/01_introduction.tex:299`, `:307`. | Adopt these changes if the relocated requirements are adopted. The `sec:ch4-design` label exists in both methodology versions, but the new wording specifically describes the external organization. |
| Blind replacement loses the current description of MSM's completed manufacturing comparison, ViFailback's task-disjoint assessment, donor transfer, bounded adaptation and unexecuted corruption, and HANDOVER's missing participant identities for learned-fusion OOF fitting. The external shorter paragraph matches the pre-revision wording. | Current `01_introduction.tex:315–320`; external `01_introduction.tex:316–319`; `diffs/01_introduction.tex.pre_revision_to_current.diff`. | Preserve the current scope information, with modest shortening if desired. It distinguishes completed, bounded and unexecuted work without requiring readers to infer it from later chapters. |

All 10 unique citation keys used by external Chapter 1 exist in the canonical bibliography files.

## Chapter 2: meaningful editorial improvements

**VERIFIED — source comparison.** Current Chapter 2 has 1,523 lines and the external chapter 1,123; source-line counts include wrapping and are not word-count or quality measures. Most earlier passages retain their scientific content while citation keys change throughout.

- The opening becomes a direct question about complementary information, reducing repetition of the welding audit and thesis roadmap (`snapshots/external/02_literature_review.tex:30–32`; current `:30–45`). The audit is retained elsewhere in the supplied material, including external Chapter 4 at `:98–107`.
- Section headings omit the repeated SQ suffixes, and explanations of local implementations are reduced. The outside literature remains the focus. For example, the stacking passage describes Ting and Witten's linear least-squares combiner without interrupting it with F2 implementation details (`external/02_literature_review.tex:620–629`; current `:649–664`). This is editorial separation, not evidence that the local F2 caveats can be discarded; external Chapter 4 retains them at `:179–183`.
- The five-of-37 / 13.5% observation moves beside the missing-input discussion (`external/02_literature_review.tex:710`; current `:1319–1321`). It still distinguishes planned missing-input inference from simulated dropout. The denominator and restricted coding categories survive.
- The final synthesis table improves traceability by naming concrete studies, providing citations in each row, and stating limits directly. It separates target-specific refitting from unchanged-predictor transfer and avoids treating the non-industrial gating example as direct industrial validation (`external/02_literature_review.tex:1096–1123`; current table `:1147–1170`). Preserve these improvements after reconciling citation keys.
- The removed acoustic exclusion explanations are not lost across the supplied material: external Chapter 1 at `:260–264` and Chapter 6 at `:26` retain them. The literature-review cuts are reasonable deduplication within that combined structure.

The new phrase “94 appraised works” at external Chapter 2 line 1098 is consistent with the **current** Appendix A, lines 12–20, which describes 57 additional works and a total of 94 across two appraisal stages. It should not be mislabeled an error solely because the original full-text cohort was 37. The 13.5% statistic remains restricted to the 37-paper initial cohort. This comparison checked manuscript consistency, not the underlying appraisal records or each paper again.

## Material moved, compressed, and actually omitted

| Current location | External location | Interpretation |
| --- | --- | --- |
| Chapter 2 requirements, `:1193–1309` | Chapter 4 `:28–36`, with methodological explanation later in that chapter | R1–R5 are moved and heavily compressed, not simply deleted. The general design conditions become concrete questions illustrated with thesis studies. |
| Chapter 2 `sec:literature-study-gaps` at `:1313` | Chapter 4 `:12` | Label transferred to the methodology design section. |
| Five-study table at Chapter 2 `:1330–1367` | Chapter 4 `:38–75` | Table moved, with content changes requiring reconciliation below. |
| Welding-to-requirements figure at Chapter 2 `:1508–1518` | Chapter 4 `:16–26` | Same PDF dependency and both existing labels retained; placement changes from `[htbp]` to `[H]`. |
| Detailed study-to-literature bridges at Chapter 2 `:1375–1503` | Condensed design text and table in external Chapter 4 | These paragraphs are not transferred verbatim. The nearest published precedents and exact open comparison for each study are less explicit in the relocated summary. Preserve any necessary literature-to-question links in the relevant empirical chapter rather than restoring the entire repetition automatically. |

The active current snapshot uses `figures/fusion_research_gap.pdf`; it does not include the earlier standalone `figures/ch02_synthesis_20261126/fig_ch02_synthesis.pdf` at this location. The external relocation uses the same current fusion-gap asset. Historical figure discussions should not be used to overwrite this later manuscript state inadvertently.

## Reconciliation priorities

**High — bibliography compatibility.** External Chapter 2 uses 75 unique citation keys; **72 are absent from both bibliography files loaded by canonical `main.tex`** (`references.bib` and `references_additions.bib`, declared at main lines 10–11). The current chapter's 79 keys are all present. Examples are `baltrusaitis_multimodal_2019` at external line 14 versus current `Baltrusaitis2019Multimodal`, and `fan_dmaw_2026` at external line 30 versus current `P003`. No matching alias declaration was found in the inspected main/bibliography files. These appear predominantly to be identifier changes, but spelling alone is not proof of bibliographic identity. Map them against the existing records or obtain the matching external bibliography; do not add duplicate references solely to silence missing-key warnings. The relocated Chapter 4 text also introduces these keys.

**High — local November 27 scope updates.** External Chapter 4's relocated MSM row (`:58–61`) and ViFailback row (`:62–64`) retain the pre-revision descriptions instead of current Chapter 2's additions (`:1350–1357`). Keep the current completed MSM comparison and its sensitivities/controlled corruption, plus ViFailback's task-disjoint assessment, donor transfer and bounded target adaptation. The unexecuted ViFailback corruption qualification is already preserved externally.

**Medium — HANDOVER table wording.** External Chapter 4 line 67 states that “the participant-disjoint test split supports the fixed rule.” Its own line 136 correctly attributes participant separation to the dataset publication and says it could not be reconstructed independently. Current Chapter 2 lines 1482–1488 make the same distinction. Qualify the table as the *published official split, reported as participant-disjoint*, and retain the missing inner participant grouping limitation. This is a local inconsistency to repair; the qualification has not disappeared from the external chapter as a whole.

**Medium — verification markers and source claims.** Current Chapter 2 contains 29 `[VERIFY PAGES]` comments; the external chapter contains none. Some cited passages move or disappear, and retained passages remove the marker (for example, current `:188–191` versus external `:176–179`). This review found no accompanying evidence that all page checks were performed. Preserve unresolved checks in a review record and clear only those supported by an actual source check. Do not represent the comment cleanup as newly verified citations.

**Medium — combined integration and layout.** External Chapter 2 removes four labels that are all present in external Chapter 4: `sec:literature-study-gaps`, `tab:fusion-study-scope`, `fig:ch02-synthesis-requirements`, and `fig:fusion-research-gap`. Replacing only one chapter risks losing the material or creating duplicate labels. Move it once, preserve stable references, and allow chapter-based figure/table numbering to change. The forced `[H]` figure/table placements and longer citation-bearing longtable require a rendered check. The prediction-availability figure remains in external Chapter 2 at line 256, so not every figure is being relocated.

## Verification boundary

The review inspected both chapter diffs, the local pre-revision deltas, substantive passages in both chapter snapshots, relevant external Chapter 4/6 passages, canonical bibliography key definitions, canonical `main.tex` bibliography declarations, and the current Appendix A count explanation. It did not verify scientific findings against original publications, rebuild PDFs, merge sources, or infer external authorship or ancestry. Only this review artifact was written.
