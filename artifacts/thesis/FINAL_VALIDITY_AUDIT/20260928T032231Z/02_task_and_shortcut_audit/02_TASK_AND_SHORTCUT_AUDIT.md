# Task boundary and shortcut audit

**Automated task-boundary/diagnostic work complete; human review pending.**

Source: actual inventory/alignment/features and gate input paths, recorded timestamps, sealed cohort and feature indices. The input_availability.csv ledger distinguishes verified availability from assumptions. The task is retrospective classification of completed, annotated segments. It does not establish online early warning or independently verified physical anomaly truth.

## Boundary checks

27180 stream/segment timestamp-count checks and 4,530 saved visual-frame selections matched. Selected sensor timestamp windows and visual frames stay inside the inclusive annotated [start,end] interval. Sensor values/features were not regenerated. The gap policy uses whole-recording cadence metadata; exact execution of every old extraction is not replayed.

Adjacent annotation audit found47 touching/overlapping pairs, of which14 have positive overlap. Full pair follow-up finds3 positive pairs affecting primary rows in two recordings: two exact repeated input windows and one contained partial window, all same action/outcome and same recording/fold. No cross-fold leakage is implied; no 4,530-unique-physical-action claim is justified. See ANNOTATION_ADJUDICATION_REQUEST.md. No historical row was removed or relabelled.

Annotation end availability, duration, progress resampling, quality and visible failure consequences are legitimate full-segment inputs within this declared task. Whether trailing idle or boundaries reflect annotation errors requires human review. Neither their use nor diagnostic metadata performance alone proves improper leakage or absence of signal.

## Three fixed diagnostic models

| model | status | AUPRC | AUROC | Brier |
| --- | --- | --- | --- | --- |
| D0 | COMPLETED_FIXED_SPECIFICATION | 0.1813982989622315 | 0.685645938391226 | 0.0950529993098224 |
| D1 | COMPLETED_FIXED_SPECIFICATION | 0.1972092248252361 | 0.6980633110355311 | 0.0950051099265216 |
| D2 | COMPLETED_FIXED_SPECIFICATION | 0.1898232700986339 | 0.6922346287100776 | 0.0953531943164775 |
| Historical_action | REUSED_FROZEN_PREDICTIONS | 0.1808053265895123 | 0.6850899183999132 | 0.0950522844139225 |
| U1 | REUSED_FROZEN_PREDICTIONS | 0.4293918693680272 | 0.7793245578590592 | 0.0804481477118429 |
| F2 | REUSED_FROZEN_PREDICTIONS | 0.4472985514404897 | 0.794968361094431 | 0.0784430122174486 |


| contrast | estimate | lower_95 | upper_95 |
| --- | --- | --- | --- |
| D1 minus D0 | 0.0158109258630045 | 0.004173650289136 | 0.0345195130929032 |
| D2 minus D1 | -0.0073859547266021 | -0.0133488623151182 | -0.0025384365824448 |
| D0 minus Historical_action | 0.0005929723727192 | -0.0025967379855954 | 0.0038641639739584 |
| D0 minus U1 | -0.2479935704057956 | -0.2939680879500956 | -0.2021039275288625 |
| D0 minus F2 | -0.2659002524782581 | -0.3131297544733246 | -0.2204533916762762 |
| D1 minus U1 | -0.2321826445427911 | -0.2763546998328107 | -0.1840669320398525 |
| D1 minus F2 | -0.2500893266152536 | -0.2960284353642402 | -0.2022862274802745 |
| D2 minus U1 | -0.2395685992693932 | -0.2845626304137352 | -0.1907197809722345 |
| D2 minus F2 | -0.2574752813418558 | -0.3042378511726466 | -0.2093303148050966 |

All three were fixed before outcomes, with one C1/L2/unweighted/lbfgs specification and no feature/search grid. Inner OOF calibration/thresholds and all transforms use training data only. D0’s class weighting/C policy differs from the historical action baseline. Interpretation: duration has predictive metadata value; additional eligible coverage fields do not improve this fixed diagnostic. Every diagnostic stays below frozen sensors and F2. This does not establish which mechanism U1/F2 uses.

## Human materials

64 clips and both independent-order sheets are prepared. Recorded labels, scores and source identifiers are absent from reviewer exports. No ratings are filled. Human status is PENDING_HUMAN_REVIEW; detailed workflow is ../04_human_review/HUMAN_REVIEW_STATUS.md. Two exact-window annotation pairs and the contained span receive a separate adjudication request; the frozen qualitative sample was not altered to favor or target findings.
