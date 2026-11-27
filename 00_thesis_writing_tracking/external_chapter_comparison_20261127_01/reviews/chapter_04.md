# Chapter 4 comparison: Research Design and Shared Methodology

Reviewed the saved `current`, `external`, and `pre_revision` copies of `04_methodology.tex`, with the current Chapter 2 used to distinguish relocated material from new material. This is a source comparison only: no chapter was merged, no thesis was compiled, and no scientific result was independently revalidated. The pre-revision copy establishes what changed in the local November 27 pass; it does not establish the external file's ancestry.

**Recommendation:** reconcile Chapter 4 together with Chapter 2. The external version offers a useful question-led R1–R5 introduction, but copying the whole file would remove concrete resource evidence and recent local study-role refinements. Importing Chapter 4 alone would also duplicate four labels already in current Chapter 2.

All line references below address the frozen files under this comparison directory, so they remain stable if the working thesis changes.

## Highest-priority differences

| Priority | Difference and evidence | Practical reconciliation |
|---|---|---|
| High | **Chapter 2 material moves into Chapter 4.** External Chapter 4 lines 12–75 add the requirements section label, welding-gap figure, and study-scope table. The corresponding current locations are Chapter 2 lines 1313, 1333, 1511–1513. The figure still uses the existing `figures/fusion_research_gap.pdf`; it is not a newly supplied figure asset. | Decide the single home for this material across Chapters 2 and 4. A move to methodology is coherent with the external question-led framing, but retain a short literature-to-methodology bridge in Chapter 2 and only one occurrence of each label. Figure/table numbering will change with the move. |
| High | **Specific resource and implementation evidence disappears.** Current Chapter 4 lines 472–499 record HFU server use; a 16 GiB Tesla T4; acquisition/cache recovery costs; approximately 303.8 controller elapsed hours; a 43 GPU-day remaining-work estimate with 47-day planning allowance; the stop-decision context; and provenance comments. External lines 244–251 replace this with general limits and prospective validation advice. The same concrete resource section is already present in `pre_revision` lines 483–510, so this is preservation of existing work, not only a new-November-27 conflict. | Keep the concrete resource evidence and its attribution limits. The external explanation of acquisition-to-decision latency at line 249 is useful and can be retained alongside it. If shortening Chapter 4, move the detailed resource paragraph to an appropriate appendix with a cross-reference rather than silently deleting it. These figures are existing manuscript reports, not measurements verified in this comparison. |
| High | **Local study-role refinements are weakened or omitted.** Current Chapter 4 lines 31–40 explicitly identify MSM as the primary completed external manufacturing comparison with six target/grouping sensitivities and controlled corruption; ViFailback as task-disjoint assessment plus specified REASSEMBLE representation transfer, with partial target-CNN adaptation; and HANDOVER's participant-safe OOF limitation. External Chapter 4 lines 50–67 compress these into the moved scope table. MSM becomes a generic laboratory-interval comparison; ViFailback retains unexecuted corruption but loses its transfer/adaptation distinction. | Preserve the current roles and completion limits in the moved table or adjacent prose. The external rewrite should not make completed MSM work less visible or make ViFailback's completed and incomplete stages indistinguishable. |
| High | **HANDOVER wording becomes too categorical in the moved table.** External line 67 says “The participant-disjoint test split supports the fixed rule.” External line 136, however, correctly attributes that separation to the dataset publication and says it cannot be independently reconstructed from the available records. Current Chapter 2 lines 1475–1482 and Chapter 4's assessment discussion preserve that distinction. | Attribute the table's split claim to the dataset authors, and keep the missing participant-to-trial mapping/participant-safe stacking limitation. This is a consistency issue within the incoming chapter, not a newly verified finding about the dataset. |
| High | **Incoming bibliography keys do not resolve against either active bibliography.** Fourteen keys newly used in external Chapter 4 are absent as exact entry keys in `references.bib` and `references_additions.bib`, both declared by active `main.tex` lines 10–11. | Map to existing verified entries or obtain the matching bibliography entries before integration. Do not treat a visually plausible author-year key as evidence that the reference has been supplied. No compilation was attempted in this comparison. |

## External work worth retaining

- **Explicit, question-led R1–R5 explanations:** external lines 28–36 replace the brief current overview at lines 42–47. They make the requirements operational: target timing, information retained by representations, incremental fusion value, absence versus degradation, and dependable comparisons. This is materially more explanatory than the current short list.
- **Sharper R3 architecture distinction:** external line 32 describes F3 as projecting a 128-dimensional visual representation and 220 sensor statistics into two 128-dimensional vectors before concatenation, distinguishes that from two sensor representations, and retains the caveat about fitting/calibration differences. This assertion should remain tied to the existing implementation evidence when integrated; the source comparison did not independently inspect the executed architecture.
- **Safer chapter references:** the external scope table uses `\ref{ch:phm}`, `\ref{ch:reassemble}`, `\ref{ch:msm}`, and `\ref{ch:vifailback}` at lines 50–62, replacing hardcoded chapter numbers in current Chapter 2's table.
- **Decision-time explanation:** external line 249 explicitly separates head timing, frame/feature work, and the time waiting for an action to finish. It can complement the concrete current resource account.
- **Clear fresh-assessment conditions:** external line 251 explains that a fresh test needs the target, decision time, groups, models, fault conditions, and main metric fixed before opening new assessment data. It complements the retained exploratory-study limitations.

## Older detailed passages restored by the external version

These are not newly discovered facts. Their external wording matches the saved pre-revision text after normalizing whitespace, while the local November 27 pass shortened them and added cross-references:

| Topic | External passage | Current local passage | Reconciliation |
|---|---|---|---|
| MSM timing example | Chapter 4 line 116 restores accepted 49.73-second and rejected 16.04-second offsets plus the readable-but-wrong-clip explanation. | Lines 134–137 use a concise explanation and refer to Chapter 7 for the VMX9 correction. | Keep a short illustrative sentence here and the exact offset history in the dataset chapter, unless the longer shared-methodology example is deliberately preferred. Neither version changes the stated alignment direction. |
| PHM normalization diagnostic | Line 142 restores the separate diagnostic's shared-normalizer explanation and the need for a fold-local rerun to quantify its effect. | Lines 206–208 preserve the distinction and refer to `sec:phm-diagnostics`. | Keep the current link and optionally the useful plain-language explanation. Avoid duplicating the whole diagnostic narrative in both chapters. |
| REASSEMBLE follow-up population | Lines 168–172 restore the original 4,530-action/148-recording cohort, the 753-action follow-up, correction from 28 to 26 recordings, assessment-reuse caveat, and `E052`. | Lines 254–258 preserve 753/26 and the exploratory limit, referring to `sec:reassemble-followups` and `app:supplementary-results`. | Retain the corrected 26 recordings and assessment-history caveat. Keep the local cross-references even if the external narrative is preferred. The count was not recomputed in this comparison. |

## Dependencies and integration risks

The four labels introduced in external Chapter 4 already exist in current Chapter 2:

| Label | External Chapter 4 line | Current Chapter 2 line |
|---|---:|---:|
| `sec:literature-study-gaps` | 12 | 1313 |
| `tab:fusion-study-scope` | 41 | 1333 |
| `fig:ch02-synthesis-requirements` | 19 | 1511 |
| `fig:fusion-research-gap` | 20 | 1512 |

These labels are absent from the external Chapter 2 source. Thus the submitted Chapters 2 and 4 implement a coordinated move; mixing only external Chapter 4 with current Chapter 2 creates the duplication. Preserve inbound references when choosing the final location. The old `fig:ch02-...` internal name can continue working in Chapter 4, though its name then no longer describes its chapter.

External Chapter 4 introduces these unresolved exact citation keys:

`deng_tc-maf_2026`, `fan_dmaw_2026`, `horwitz_back_2023`, `hua_anti-interference_2026`, `kapoor_leakage_2023`, `kim_multi-sensor_2026`, `nie_time_2023`, `prognostics_and_health_management_society_phm_2026`, `roth_towards_2022`, `sliwowski_reassemble_2025`, `thoduka_multimodal_2024`, `varma_bias_2006`, `zeng_diagnose_2026`, `zhang_provable_2023`.

The original Chapter 4 citations remain. In the moved welding figure, the external keys `fan_dmaw_2026` and `hua_anti-interference_2026` replace current Chapter 2's `P003` and `Hua2026Weld`; bibliographic identity still needs an explicit reconciliation rather than a blind rename.

The moved figure and table change their float specifiers from `[htbp]` to `[H]`. That forces placement and should be visually reviewed after an eventual merge, especially with two substantial objects near the start of the methodology chapter. The existing research-workflow and stacker-flow figures remain in the incoming chapter.

External Chapter 4 removes direct references to `sec:phm-diagnostics`, `sec:reassemble-followups`, and `app:supplementary-results` when restoring the longer passages. These references are useful navigation added by the local pass; their removal is not required by the external wording.

## What remains substantively unchanged

Most of the apparent line churn is paragraph rewrapping: current Chapter 4 has 499 lines and external has 251, while the external source contains more whitespace-delimited words (4,894 versus 4,368). These are source counts, including LaTeX, not typeset word counts.

After normalizing paragraph whitespace, the dataset admission, target/decision-time discussion, official HANDOVER partition caveat, REASSEMBLE OOF bank and internal-validation dependence, F2 calibration/attribution limitation, metrics and aggregation, bootstrap limitations, missing/degraded-input protocols, matched corruption exposure, and saved-results-versus-retraining distinctions remain substantively unchanged. These important safeguards have not been lost in the external rewrite.

## Suggested reconciliation order

1. Treat the Chapter 2/4 requirements material as one structural change; select its single home and retain all inbound labels/references.
2. Use the external R1–R5 explanations while preserving the current MSM, ViFailback, and HANDOVER qualifications.
3. Retain the concrete current computing/resources section; incorporate the external latency and fresh-assessment explanations selectively.
4. Preserve the local diagnostic/follow-up cross-references; choose how much illustrative detail belongs in shared methodology.
5. Reconcile the fourteen citation keys against the supplied/current bibliographies, then compile and inspect the relocated floats only after a merge is authorized.

Findings marked as absent, moved, or unchanged above are VERIFIED within the inspected manuscript sources and local bibliography files. The recommended structure and wording choices are editorial recommendations; the underlying scientific claims remain attributed to their existing records.
