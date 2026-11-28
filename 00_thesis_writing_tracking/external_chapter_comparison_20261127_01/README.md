# External chapter comparison — 27 November 2026

**Both versions are preserved. No manuscript file was merged or overwritten.** The external files contain useful editorial changes, but replacing the current chapters wholesale would remove local evidence, corrections and cross-references. A selective merge is the recommended next step.

The comparison covers the five supplied chapters in `Temp_dump/27112026_ch_reworked_some/` against the authoritative manuscript in `00_thesis_writing_tracking/Thesis/LaTeX_Project/`. Chapters 3 and 7–10 were not supplied externally; they remain part of the current manuscript and were checked for preservation.

The saved starting point of the local November 27 revision was also compared. It identifies additions made in that local pass and older material worth preserving. It does **not** establish the external files' ancestry or the author's intention. Source differences are VERIFIED within the inspected files; recommendations are editorial judgments. Existing scientific results retain their earlier evidence classifications and have not been independently recomputed in this review.

## Chapter-by-chapter findings

| Chapter | External work and structural differences | Current work that a wholesale replacement would lose | Recommendation |
|---|---|---|---|
| **1 — Introduction** | Small changes: dynamic chapter references and a clearer roadmap to the five requirements in Chapter 4. | The November 27 explanation of MSM's completed external comparison, ViFailback's representation transfer/partial adaptation, and HANDOVER's participant-safe stacking limitation. | Keep the external navigation improvements and the current study-role paragraph. [Detailed review](reviews/chapters_01_02.md). |
| **2 — Literature review** | A more direct opening, fewer thesis-implementation interruptions, and a stronger final table of concrete cited findings and limits. The 13.5% observation moves beside the missing-input literature. Requirements, the welding-gap figure and five-study table move to external Chapter 4. | Local study-role qualifications and useful literature-to-study bridges need to survive the compression. Citation keys change throughout, and page-verification reminders disappear. | Retain the external editorial improvements while reconciling Chapters 2 and 4 together, bibliography identities and unresolved checks. [Detailed review](reviews/chapters_01_02.md). |
| **4 — Methodology** | Expanded, question-led R1–R5 explanations; study-scope material moved from Chapter 2; clearer decision-time and fresh-assessment explanations. Some longer examples restore pre-revision wording. | Current MSM/ViFailback role distinctions, concrete computing/resource evidence, and useful diagnostic/follow-up cross-references. | Combine the external explanations with current evidence and boundaries. Keep one home for the relocated material. [Detailed review](reviews/chapter_04.md). |
| **5 — PHM** | Mostly matches the saved pre-revision text after ignoring wrapping; restores its section structure and opening figure position. Adds a retrospective “methodological negative control” characterization. | Local fixed-split results; visual/detector/appearance outcomes; provenance corrections; explicit Ridge/four-arm appendix navigation; consolidated seven-section structure. | Retain the current chapter as the base. Preserve the diagnostic role rather than adopting the negative-control characterization. [Detailed review](reviews/chapters_05_06.md). |
| **6 — REASSEMBLE** | Shorter synthesis with a useful warning against assembling a model from separately selected best follow-ups; earlier section structure and fuller method reminders. Most detailed follow-up prose survives. | The older F2 visual-term diagnostic, November 27 corruption table, permutation outcomes, follow-up comparison table and navigation. | Keep those local findings and tables; adapt the external selection-bias explanation and selected concise synthesis wording. [Detailed review](reviews/chapters_05_06.md). |

## Material to preserve before any integration

1. **PHM results and provenance.** Current Chapter 5 adds the distinct fixed-split result (MAE 0.6548 versus 0.7348, with its criterion and interval), visual/detector/appearance results, the E027/E126 attribution correction and historical-lineage limits. The external chapter retains the principal LOEO table but omits these additions. The fixed-split and LOEO findings must remain separate.
2. **REASSEMBLE's full reporting.** Keep the seven-operator corruption table and both absence routes, the nineteen-permutation outcomes, and the follow-up table separating populations, controls, intervals and completion status. The external file still contains most follow-up studies; the losses are specific results and the compact comparison map, not the entire research programme.
3. **The existing F2 diagnostic.** The external chapter substitutes a general missing-control caveat for the saved-score within-fold analysis already present before November 27. Keep both the bounded observed visual ordering contribution and the limitation that there was no refitted sensor-only second-stage control. Current Appendix D still contains the diagnostic, so the chapter should remain consistent with it. This review inspected the manuscript description; it did not rerun the audit.
4. **Study roles, resource evidence and navigation.** Preserve the current MSM/ViFailback/HANDOVER scope distinctions, Chapter 4's concrete computing/resource account and the new chapter-to-appendix links. These can coexist with shorter, clearer external prose.

## Wording that needs reconciliation

- **PHM “negative control.”** External Chapter 5 line 5 calls the study a methodological negative control retrospectively. The pre-revision text expressly rejected a designed negative-control interpretation, and both versions retain the actual exploratory chronology. A negative result does not establish a known-null control design. Retain the diagnostic/target-validity description.
- **HANDOVER participant separation.** External Chapter 4's table at line 67 presents the participant-disjoint test split without attribution. Its own later paragraph at line 136 correctly says the dataset publication reports separation and the local records cannot independently reconstruct it. Qualify the table consistently; the caveat is not wholly absent from the external work.
- **F2 attribution.** The external missing-control warning is useful, but should not erase the narrower within-fold finding or imply that the current analysis identifies causal modality importance. Preserve the distinction between an arithmetic omission diagnostic, a separately refitted comparator and the full pooled pipeline contrast.
- **Citation verification reminders.** Current Chapter 2 has 29 `[VERIFY PAGES]` comments; the external chapter has none. The supplied files do not establish that all these checks were completed. Carry forward unresolved checks in a review record rather than treating comment removal as verification. The external “94 appraised works” wording is consistent with current Appendix A's two-stage total; the 13.5% statistic correctly retains its separate initial 37-paper denominator.

## Integration checks

These checks substituted external text **in memory only**, following literal inputs from the current `main.tex`. They are static checks, not a TeX build or visual layout validation. Full details and source locations are in [dependency_comparison.json](dependency_comparison.json).

| Check | Current manuscript | Hypothetical replacement of all five chapters |
|---|---|---|
| Missing exact citation keys | 0 | **76 distinct keys**: 72 used in external Chapter 2 and 14 in external Chapter 4, with overlap. |
| Undefined literal references | 0 | **1:** `sec:phm-diagnostics`, still used by Appendix D. |
| Duplicate literal labels | 0 | 0 when all five external files are considered together. |
| Missing literal input/figure/bibliography files | 0 | 0. The supplied files reference assets already available locally. |
| Undefined evidence identifiers | 0 | 0. This checks identifier existence, not the truth of each evidence claim. |

The 76 missing keys are **not necessarily 76 missing publications**. Several appear to be renamed references to existing works. The supplied folder contains only five `.tex` files, so no matching external bibliography was available. Before integration, map the changed keys to the current entries or reconcile an accompanying bibliography; do not silently invent entries.

Partial replacements have additional risks:

- External Chapter 4 with current Chapter 2 duplicates `sec:literature-study-gaps`, `tab:fusion-study-scope`, `fig:ch02-synthesis-requirements` and `fig:fusion-research-gap`.
- External Chapter 5 alone leaves references to `sec:phm-diagnostics` in current Chapter 4 and Appendix D unresolved.
- External Chapter 6 alone leaves current Chapter 4's reference to `sec:reassemble-followups` unresolved.

The relocated Chapter 4 figure and table use forced `[H]` placement. An eventual merge must be compiled to check the new numbering, page breaks and float placement. No figure assets were supplied or edited in this comparison.

## How to inspect the exact differences

- [Side-by-side comparison index](index.html): one visual source diff per chapter, with whitespace normalized by paragraph to reduce line-wrapping noise.
- [Exact line diffs](diffs/): `current_to_external.diff` shows what replacing the current file with the external file would remove and add. Separate `pre_revision_to_current` and `pre_revision_to_external` diffs show each version against the saved local starting point.
- [Source snapshots](snapshots/): byte-preserving copies of the five current, external and pre-revision chapters. These are comparison inputs, not a new working manuscript.
- [File inventory and identities](comparison_inventory.json), [normalized comparison](normalized_comparison.json), and [preservation checks](preservation_checks.json).

Line counts exaggerate the extent of some changes because the external files put long paragraphs on single lines. For example, external PHM has 122 lines versus 388 locally, yet most of the shared prose survives. The report and paragraph diffs account for this; they do not treat rewrapping as a scientific edit.

All ten canonical chapter files and all five external chapter files are byte-identical to their initial hashes. All fifteen comparison snapshots match their source identities, and local report links were checked. The standard `git diff --check` reports the existing manuscript's CRLF line endings as trailing whitespace; `git -c core.whitespace=cr-at-eol diff --check` passes. Original line endings were preserved. The whole-tree Git status/stat include earlier work, not just this review; no files were staged or committed. The check receipts are retained alongside the report.

Recommended integration order, if requested: reconcile Chapters 2/4 and their bibliography together; carry over Chapter 1's navigation edits; then adapt selected PHM/REASSEMBLE prose while retaining the current evidence, labels and limits. Review the resulting combined source and compile it before replacing any working outputs. This pass makes the differences reviewable and leaves that merge unperformed.
