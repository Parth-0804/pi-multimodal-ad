# Chapters 5 and 6 reconciliation receipt

Only `chapters/06_reassemble.tex` was edited. Chapter 5 was reviewed against the actual external file and retained byte-for-byte: its external-only substantive change was the unsupported negative-control characterization, and its chapter label already existed. The seven-section PHM and eight-section REASSEMBLE organization remains.

The inputs were the current canonical files, checked against the [preserved starting copies](../before/chapters/), and the [copied external files](../external/), checked against the supplied files in `Temp_dump/27112026_ch_reworked_some/`. They matched at inspection. The earlier comparison report informed the review but was not substituted for reading the actual inputs.

## Edits and external wording retained

- Chapter 6's synthesis now follows the external version's shorter, connected explanation of the core result, separate favorable follow-ups and remaining questions.
- The external explanation of selection bias from combining components after inspecting their results on the same recordings was adapted. It is an inference about the proposed combination, not a claim that such a joint model was executed. The need to fix a joint pipeline before evaluating untouched recordings remains prospective.
- The external reference to a second-stage calibration control was made precise as a second-stage control: the current implemented F2 stacking description is unchanged, including its absence of an additional post-stacker calibration stage.
- The positive within-fold visual-term finding and its bounded interpretation remain in the conclusion and in the full E113 discussion. The missing matched sensor-only control still limits attribution of the pooled gain.
- The same-head-size comparison and possible pooling explanations were moved from the old synthesis into the visual-pooling subsection, beside their results. The explanation explicitly remains noncausal: concentrated outcome cues and less dilution were not isolated.
- Repeated numerical summaries were shortened in the conclusion; their original result paragraphs, intervals and tables remain. In particular, the old unsigned wording `0.1441 below statistics` remains as the signed `-0.1441` contrast with its interval in the sensor-budget subsection.
- The bridge to the MSM chapter is byte-for-byte unchanged. The chapter still distinguishes dataset-specific fitting from generalization of an already fitted model.

## Results and claim checks before wording changes

These are **VERIFIED source/report correspondence checks**, not fresh score recomputation or experimental reproduction. Underlying scientific results remain **REPORTED by the inspected chapter, appendix and retained reports**.

| Reconciled statement | Support inspected | Boundary retained |
| --- | --- | --- |
| F2 improves over statistics; F2 versus averaging is unresolved | Chapter 6's fusion-results paragraph/table, and Appendix D's `tab:f2-fold-audit` | Pooled contrast and within-fold ordering remain different; no causal modality-importance claim or refitted sensor-only control is invented. |
| Visual term affects within-fold ordering | Appendix D, “Saved-Prediction Check of the Core F2 Visual Term,” including positive coefficients, all five AUROC changes and the negative fold-3 AP change | Detailed E113 explanation is untouched; the synthesis does not claim AP improves in every fold. |
| Longer PatchTST training helps but remains below statistics; same-sensor hybrid helps | Chapter 6 follow-up map and sensor-budget subsection; retained `ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md`, Tasks 2–3 | Same sensing modality; matched budget comparison; no combination with the visual/adaptive follow-ups. |
| Last-quarter and whole-action heads have equal size | `BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md`, sections D–E: V0 and V3 each report 114,945 parameters | Equality concerns this head comparison, not all pooling variants; no temporal-causality or early-warning claim. |
| Anchored adjustment improves ranking but lowers recall and increases calibration error | Current adaptive-extension paragraph and `ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md` clean comparison and interpretation | The anchor and constant-adjustment control remain distinct; this is not retrospective success of F6. |
| Spatial processing or fine-tuning need not improve fusion | Current follow-up table, spatial comparison and matched tuning paragraphs; Appendix D's matched-cohort table | Distinct recipes/cohorts and unresolved intervals remain; no equivalence claim. |
| Augmentation-matched and quality-interaction robustness effects remain unresolved | Current follow-up table and unchanged detailed adaptive/quality-interaction paragraphs | Condition-mean AP and their realization protocols remain distinct from ordinary pooled AP. |
| No executed combination of the strongest follow-ups | Current study definitions and both retained handoff reports | The external selection-bias explanation concerns future combination and validation; no new final architecture is claimed. |

Inspected retained reports are under `implementations/REASSEMBLE/results/artifacts/reports/`. Earlier report verification dates remain their own dates; no training, inference, preprocessing, calibration fit, experiment resumption or new literature verification occurred.

## Exact preservation checks

| Check | Chapter 5 | Chapter 6 |
| --- | --- | --- |
| Complete starting file preserved | Yes, byte-identical | Only pooling explanation and synthesis changed |
| All existing table environments byte-identical | 2 of 2 | 4 of 4 |
| All labels preserved in original order | Yes | Yes |
| Existing evidence IDs removed | None | None; E038/E039 also cited in the synthesis |
| Section count | 7 | 8 |
| CRLF line endings retained without bare LF | Yes | Yes |

PHM's fixed-split result, visual/scalar/multitask/detector results, selected appearance comparison, E027/E126 correction, E131/E132 lineage qualification, Ridge appendix link, four-arm leak description and `sec:phm-diagnostics` are unchanged.

REASSEMBLE's complete F2 diagnostic, permutation outcomes, all seven strongest corruption operators plus both absence rows, follow-up comparison map, numerical follow-up paragraphs, completion/partial-execution limits, original figures and their placement are unchanged. The pre-synthesis chapter text changes only by insertion of the four-line pooling interpretation; no earlier result block was replaced.

## File identities

- `05_phm.tex` before: `18c502b1dff720b651fcc3c2565c334cfd8c312d734292ee64c84b6c10cca286`
- `05_phm.tex` after: `18c502b1dff720b651fcc3c2565c334cfd8c312d734292ee64c84b6c10cca286`
- `06_reassemble.tex` before: `bfc15d2f6bc647df9395f7debdd53254e5e1c7454015f509822611169baeda15`
- `06_reassemble.tex` after: `6de3c6a57bfb5d3cc730c3d8b70d080e3c5038963b763fdfe05e610faf0a8000`

The exact task diff was inspected against the preserved starting copy. The chapter prefix, after removing only the inserted pooling paragraph, and the concluding MSM bridge exactly match the starting bytes. All report links resolve. Standard `git diff --check` exits 2 because it treats the preserved CRLF endings as trailing whitespace across the existing dirty chapters (1,003 notices); `git -c core.whitespace=cr-at-eol diff --check` passed for both owned chapters. No appendix, table file, figure asset, bibliography or other chapter was edited by this agent. No unresolved scientific choice was introduced. Parent-agent compilation and rendered review remain pending; this receipt makes no new PDF/layout claim.
