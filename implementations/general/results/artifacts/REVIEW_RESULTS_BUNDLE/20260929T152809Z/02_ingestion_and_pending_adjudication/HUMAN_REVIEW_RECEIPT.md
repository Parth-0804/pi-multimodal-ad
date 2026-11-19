# Human review receipt — Reviewer A

**HUMAN_RETURNS_RECEIVED_NOT_ADJUDICATED**

64 complete ratings received from one real reviewer. No second reviewer has submitted; inter-rater agreement cannot be calculated. Original CSV bytes are preserved as `reviewer_1_submitted.csv`.

## Outcome agreement

- 57 / 59 determinate ratings agree with recorded labels (96.6%).
- 2 / 59 determinate ratings disagree (3.4%).
- 5 / 64 outcomes are indeterminate (7.8%).
- Agreement across all presented clips: 57 / 64 (89.1%); the other seven comprise two disagreements and five indeterminate outcomes.

| Action | Agree | Disagree | Indeterminate | Total |
|---|---:|---:|---:|---:|
| pick | 13 | 0 | 3 | 16 |
| insert | 14 | 1 | 1 | 16 |
| remove | 15 | 0 | 1 | 16 |
| place | 15 | 1 | 0 | 16 |

## Follow-up

Boundary ratings: 60 acceptable, 3 questionable, 1 indeterminate. Possible recording/presentation artifacts: 4. Visibility was rated adequate for all 64. Flag categories overlap; 10 unique clips need follow-up. See [FLAGGED_CASES.csv](FLAGGED_CASES.csv) for the supplied reasons and exact blind review IDs.

Adjudication is requested, not completed. Revisit flagged cases against the original clips and annotation boundaries with the researcher. A disagreement does not establish which judgement is correct. Original MP4s can help distinguish browser-copy issues; reasons alone do not establish the cause. No ratings have been repaired or inferred. Keep this analysis and flag list away from any additional reviewer until they finish independently.

## Interpretation and limits

This supports substantial reviewer–label agreement on the clips that were judgeable, while identifying two outcome disagreements and several ambiguous or flagged cases. It does not establish population label accuracy, physical ground truth, absence of shortcuts, or validity of every cohort annotation. The sample is balanced and recording-spread, not a population-random sample. One reviewer supplies no independent inter-rater reliability estimate. The author had access to generic assistant-provided wording examples; no assistant-generated clip ratings were substituted.

Historical performance metrics, labels, predictions and conclusions remain unchanged. Do not resolve discrepancies by removing clips or tuning thresholds. Any correction requires a separate approved protocol.

## Validation and continuation

Required fields, enums, unique IDs and reasons passed validation; three existing ingestion tests passed. Original action/clip mapping and order match the blank sheet. Independent standard-library counting reproduced the reported totals and all eight outcome/action strata. 115 sealed historical files retain their recorded hashes. Submitted bytes match the original CSV hash.

The historical audit snapshot still says human review was pending at sealing; it has deliberately not been overwritten. This receipt records the later submission and outstanding adjudication. Next: review FLAGGED_CASES.csv with the researcher; optionally collect reviewer B independently. No model rerun is triggered.
