# Thesis revision state — v0.3

Updated 2026-11-24. The professor-submitted v2 draft is at tag `professor-submitted-2026-11-20-v2` (`47fdaae`). The `revision/academic-writing` branch records the Chapter 4 wording edits and the correction to the literature chronology. The structural decisions are listed in the [structural diagnosis](STRUCTURAL_DIAGNOSIS.md) for author review.

## Current scientific position

- Registered research question and four subquestions are retained in `00_THESIS_CANON.md`.
- Current gap statement: no new gap has been approved or synthesized by the editing task. Keep existing claim boundaries; any scientific correction requires evidence and an author decision.
- Claim ledger: C01–C09 remain provisional draft-reported anchors, not verified primary-source findings. No status upgrades in v0.3.
- Independent welding validation remains open; adjacent industrial/robotic results and exploratory comparisons retain their reported scope.

## Chapter status

| Chapter | Status |
|---|---|
| 1 Introduction | Phase 1 diagnosed. Earlier pilot §§1.2–1.3 remains unaccepted. |
| 2 Critical Literature Review | Phase 1 diagnosed. The chronology in §2.1.2 was corrected. Earlier pilot §§2.6.1–2.6.3 has pending source checks and remains unaccepted. |
| 3 Technical Foundations and Candidate Models | Phase 1 diagnosed. |
| 4 Research Design and Shared Methodology | Local wording revised in §§4.6–4.9. The placement of detailed fallback behavior awaits author review. |
| 5 PHM Case Study | Phase 1 diagnosed. |
| 6 REASSEMBLE Case Study | Phase 1 diagnosed. Earlier pilot §§6.7.1–6.7.4 raised scientific questions and remains unaccepted. |
| 7 MSM Case Study | Phase 1 diagnosed. |
| 8 ViFailback Case Study | Phase 1 diagnosed. |
| 9 Integrated Discussion | Phase 1 diagnosed. |
| 10 Conclusion and Future Work | Phase 1 diagnosed. |
| Abstract, front matter, disclosure, references and appendices | Abstract diagnosed. Routine and supporting material defaults to KEEP. |

The supplied checker compared 30 `.tex` files in the working project against the baseline tag and returned exit 0. Temporary copies exercised sign and precision, unit, citation, label, reference, equation, locked-term and table changes. All eight produced review flags. A wording-only test returned exit 0 and an invalid path returned exit 2. The released `references.bib` was compared separately and matched the tag byte for byte. The earlier pilots informed the editing rules. Phase 1 does not change the status of any draft-reported scientific anchor.

Both baseline editions rebuilt in a temporary copy with the recovered XeTeX and Biber kit. Each resolved 107 citation keys. The extracted text matched the corresponding release on all 193 full-edition pages and 132 review-edition pages.

## Open items (resolve only when relevant)

- The [source inventory](README.md#source-inventory) locates the recovered implementation, run archives and literature registers. Check the producing record for each consequential claim. The citation index flags 17 printed entries without a recovered local PDF.
- Earlier pilot flags: unavailable vs nonexistent evidence; known absence vs undetected corruption; grouped literature attributions, offset vs drift and specific corruption conditions; F3 candidate budgets and exact inputs; gate weights vs causal reliability; metric-specific gate performance. Preserve these safeguards; do not treat the questions as resolved.
- University AI policy and formatting requirements are not verified. Maintain an accurate disclosure.

## Decisions now in force

| Previous v0.1 approach | v0.3 decision |
|---|---|
| Paragraph/subsection revision as the central pilot operation | Diagnose systematically; KEEP adequate prose; use smallest sufficient edit |
| Global reference used in context-heavy variant | Short provisional scientific reference; retrieve only relevant constraints/evidence |
| Chapter preparation for local pilot only | Reverse-outline main-text argument before structural/linguistic editing |
| Fixed sliding-window defaults | Choose context based on actual argumentative need |
| AI auditor issues a pass/fail judgment | AI flags semantic deltas; primary-source checks and human acceptance decide |
| A/B trial of simple vs context-heavy rewriting as the starting point | Original retained as comparator; lean editing first; broader candidate only when justified |
| Revision history in working ledgers | Use existing diffs/Git and brief records of consequential decisions |
| Iterative targeted corrections | Explicit stop when adequate; escalate after two failed attempts |
| Structural and linguistic editing could overlap | Finish and verify approved structural changes before polishing affected prose |
| Mechanical verification could remain manual | Mandatory scripted source checks where editable LaTeX exists; PDF-only work remains provisional |
| General final author read-through | Mandatory human read-aloud of approximately 15–20 high-leverage pages, extending if needed |

## Next three actions

1. Author reviews the [reverse outline and triage](STRUCTURAL_DIAGNOSIS.md) and decides which cuts, moves and argument repairs to approve.
2. Complete and verify approved structural changes in a separate commit. Preserve evidence, caveats and citations at their retained locations. Clear the structural gate for each affected passage before polishing.
3. Run the smallest useful results and literature pilots, check the diff and primary evidence, and obtain author review before scaling. Use separate commits for linguistic work and verified scientific corrections.

## Pilot / decision record

| Passage | Stage | Evidence / author decision |
|---|---|---|
| §6.7.5 (results pilot) | Pending | Awaiting review of Chapter 6 structure. |
| §2.6.4 (literature pilot) | Pending | Awaiting Chapter 2 synthesis decision. |
| §4.9 (robustness wording) | First paragraph revised | Checked the availability distinction against `section3_evaluate.py` and `section3_corruptions.json`. The placement of the detailed fallback explanation remains open. |

Record only material decisions, unresolved evidence questions and actual progress here. Do not fabricate chapter completion or reviewer sign-off.
