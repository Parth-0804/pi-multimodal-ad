# Final bounded validity audit handoff

**AUTOMATED VALIDITY AUDIT COMPLETE — HUMAN REVIEW PENDING**

Run: `artifacts/thesis/FINAL_VALIDITY_AUDIT/20260928T032231Z`. Original sealed core only; active additional-improvements queue unchanged and excluded from prediction comparisons. Independent computational checking, not independent human certification, new-data validation or full training reproduction.

## 1. Numerical reproduction

216 core full-precision metric rows,30 paired uncertainty rows and8 PHM MAE/RMSE rows reproduce at absolute tolerance 1e−8. NumPy AP groups ties; AUROC uses positive-negative pair credit; Brier/ECE and saved decisions independently reconstructed and library-crosschecked. The historical 2,000 recording-cluster draws and intervals reproduce with no invalid core draws. No unexplained material numerical discrepancy was found. Source identities join on recording+segment after binding legacy anonymous NPZs to sealed cohort/per-fold artifacts, not simply array lengths.

| contrast | metric | estimate | lower_95 | upper_95 |
| --- | --- | --- | --- | --- |
| F2 minus U1 | AUPRC | 0.0179066820724625 | 0.0086026998472449 | 0.0282842795373873 |
| F2 minus U1 | AUROC | 0.0156438032353718 | 0.0060298898814543 | 0.0254650875232092 |
| F6 minus F2 | AUPRC | -0.0059426608102209 | -0.0247957883607326 | 0.0136945015440087 |
| F6 minus F2 | AUROC | -0.0194450646874048 | -0.028800779228553 | -0.0102389366939672 |

## 2. Fitting scope

All 20 inner and 80 additional subfold manifests were checked for recording exclusion. Outer0/inner0/sub0 was the deterministic deeper source/provenance trace; its final F6 quality scaler matches outer-training metadata. No required assessment overlap was identified. Missing original S1 statistical fitted state and optimizer-event logs are provenance gaps: this does not certify every execution operation. F2 threshold-only crossfitting is explicitly conditional on its branch OOF bank, as originally documented, and does not constitute unbiased full-pipeline inner performance. Outer-test labels remain excluded.

## 3. Input/target boundary

Completed annotated-segment retrospective classification is the supported task. Full duration, segment end, progress normalization and some quality/content inputs require completion; action availability at action start is not established by these annotation fields. No selected timestamp was outside the annotated boundary in 27,180 stream checks; all 4,530 saved frame selections matched. Inclusive endpoints and whole-recording cadence metadata are disclosed. Three overlapping primary pairs in two recordings include two exact repeated inputs; this requires qualification of distinct-action counts and annotation adjudication, not a fabricated cross-fold leakage diagnosis.

## 4. Alternative explanations

| model | AUPRC | AUROC | Brier |
| --- | --- | --- | --- |
| D0 | 0.1813982989622315 | 0.685645938391226 | 0.0950529993098224 |
| D1 | 0.1972092248252361 | 0.6980633110355311 | 0.0950051099265216 |
| D2 | 0.1898232700986339 | 0.6922346287100776 | 0.0953531943164775 |
| Historical_action | 0.1808053265895123 | 0.6850899183999132 | 0.0950522844139225 |
| U1 | 0.4293918693680272 | 0.7793245578590592 | 0.0804481477118429 |
| F2 | 0.4472985514404897 | 0.794968361094431 | 0.0784430122174486 |

D1−D0 AP +0.015811 [0.004174,0.034520]; D2−D1 −0.007386 [−0.013349,−0.002538]. Duration carries metadata information under the fixed diagnostic; adding eligible coverage/missingness worsens it. These models remain far below U1/F2. This does not prove whether original models use duration or another shortcut, or whether physical signals lack information.

## 5. Human review

PENDING_HUMAN_REVIEW. All 64 blinded silent clips and two independently ordered blank sheets are ready; no actual ratings exist. Clip total62.21MiB, within 2 GiB. Installed MPEG4 encoding replaced unavailable H264 without package installation; every in-segment frame is preserved, with average timestamp cadence and maximum local timing deviation0.255s disclosed. Nine recordings recur across strata (at most two cases each); the sample is structured and balanced, not a population-random error estimate. Do not invent a second rater or merge AI judgments into human evidence.

## 6. Sensitivity of fusion gain

| action | metric | segments | failures | failure_recordings | F2_minus_U1 | lower_95 | upper_95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pick | AUPRC | 1190 | 98 | 55 | 0.00883788570501 | -0.0079615127790629 | 0.0281154997731049 |
| pick | AUROC | 1190 | 98 | 55 | 0.0053449951409134 | -0.0204967545966341 | 0.0308005378730214 |
| insert | AUPRC | 1156 | 243 | 70 | 0.0140840265445428 | 0.0015752689138355 | 0.0260675523320034 |
| insert | AUROC | 1156 | 243 | 70 | 0.0009555618658697 | -0.0135320845563444 | 0.0154609625266777 |
| remove | AUPRC | 1096 | 146 | 55 | 0.0026132638693695 | -0.0119629334233115 | 0.0186904235250515 |
| remove | AUROC | 1096 | 146 | 55 | 0.0114203316510453 | -0.0078771565932159 | 0.0319102826780858 |
| place | AUPRC | 1088 | 22 | 21 | 0.0514648211634107 | -0.0008417436757352 | 0.1329709055447471 |
| place | AUROC | 1088 | 22 | 21 | 0.0360736824151457 | -0.039825514588586 | 0.1307667795398744 |

All four AP point effects are positive, but only insert has a marginal AP interval excluding zero. Place is retained with 22 failures across 21 recordings and wide uncertainty. The original branch-overlap table is not this actual fusion comparison.

| analysis | metric | weighted_positive_prevalence | U1 | F2 | F2_minus_U1 | lower_95 | upper_95 | valid_replicates | undefined_replicates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| recording-balanced sensitivity analysis | AUPRC | 0.1238208216305156 | 0.431672146976423 | 0.4507323266570945 | 0.0190601796806715 | -0.0004051740521968 | 0.0367870258717871 | 2000 | 0 |
| recording-balanced sensitivity analysis | AUROC | 0.1238208216305156 | 0.7702004573043821 | 0.7780416831054865 | 0.0078412258011043 | -0.0222566130443678 | 0.0299181726117033 | 2000 | 0 |
| recording-balanced sensitivity analysis | Brier | 0.1238208216305156 | 0.0885376527578312 | 0.0861388475034 | -0.0023988052544311 | -0.0043553599969899 | -0.000392408540345 | 2000 | 0 |

Recording-balanced AP/AUROC gains remain positive in point estimate but are unresolved by their intervals. Brier improvement remains supported. The primary segment-weighted result is preserved, with a population-weighting qualification; no favorable alternative replaces it.

## 7. Practical operating points

| model | TP | FP | TN | FN | true_failures_per_100_flags | misses_per_100_failures | false_flags_per_100_successes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | 313 | 819 | 3202 | 196 | 27.65017667844523 | 38.50687622789784 | 20.36806764486446 |
| U2 | 337 | 1525 | 2496 | 172 | 18.098818474758325 | 33.7917485265226 | 37.92588908231783 |
| F2 | 311 | 754 | 3267 | 198 | 29.2018779342723 | 38.89980353634578 | 18.75155433971649 |
| F6 | 291 | 675 | 3346 | 218 | 30.124223602484477 | 42.82907662082515 | 16.786868938075106 |

F2 flags 1,065 annotation rows:311 true failures and754 successful rows, misses198 of509 failures, and rejects3267 of4021 successes. Thus29.2 true failures per 100 flags, 38.9 missed cases per 100 actual failures, and18.75 false flags per 100 successes. These describe a training-selected threshold procedure across folds, not one universal deployed cutoff, prospective warnings or alarms/hour.

## 8. Claim impact

Core numerical claims remain valid for their frozen task/estimand; qualify action consistency, recording weighting, execution-trace coverage, retrospective availability and unique-action counts. No checked numerical claim requires suspension for a material metric discrepancy or required-fitting overlap. Unsupported early-warning/physical-truth/nonoverlapping-action interpretations must not be introduced. Full claim IDs and allowable wording: CLAIM_IMPACT_MATRIX.csv. Existing thesis matrices, reproducibility documents and external master were preserved. User-named additional-improvements integration files were not located at the specified names; none was invented or edited.

## 9. Irremovable limitations with current evidence

Adaptive same-cohort study selection, shared scene/day/objects, provisional PHM target and exposed history, fixed-model conditional bootstrap, one core corruption realization, no audio/OOD feasibility repair, missing optimizer-level execution logs, no independent human ratings, and no prospective deployment evidence remain. Additional bootstrap or diagnostics do not create independent confirmation.

## 10. Correction versus another experiment

No model/result rewrite is warranted by the numerical checks. A concrete annotation adjudication request identifies three overlapping primary pairs; only a separately approved correction protocol may change annotations or evaluate a deduplicated cohort. Keep the existing results unchanged. Add the task/weighting/action/operating-point qualifications now through the supplied storyline addendum; do not tune architectures to rescue outcomes. Finish the real human review and preserve returned sheets through the tested ingestion script.

## Check-by-check evidence register

| check | question | reason | method | source | result | uncertainty | limitation | consequence | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Numerical reconstruction | Do core scores and uncertainty reproduce? | Detect reporting/metric mistakes independently. | NumPy tie-group AP, pair-credit AUROC, Brier/ECE/confusion metrics; installed sklearn crosscheck; original paired recording RNG | sealed S1/S1B/S2/S3/dropout predictions and result JSONs | 216 core metrics + 30 paired rows + 8 PHM error rows reproduce | 2000 recording draws, seed20310927; all checked core replicates valid | Conditional retained-model audit; no full retraining or independent cohort | Retain bounded core numerical claims | VERIFIED_NUMERICALLY |
| Fitting scope | Were assessment recordings excluded from required fits? | File naming is not proof of nested fitting. | All 20 inner +80 extra subfold memberships; deterministic outer0/inner0/sub0 source trace; outer0 F6 scaler parity | fitting_scope_checks.json, original sources/manifests | No required assessment overlap found; inspected sources match training identities | Not statistical | No replay of all optimizer/sample events; original S1 statistical model/scaler not retained at its original fit | State scope and PROVENANCE_GAP explicitly, not universal execution certification | COMPLETED_WITH_PROVENANCE_LIMITATIONS |
| Task boundary | What inputs are available when, and do windows obey their annotations? | Separate retrospective outcome classification from prospective warning. | 27180 timestamp/count checks,4530 saved frame-index checks; source inspection and overlap follow-up | boundary_checks.json, input_availability.csv, overlap_followup.json | No selected timestamp outside annotation window; closed endpoints; three overlapping primary pairs within recordings | Annotation semantics/human labels pending | Whole-recording cadence metadata; raw signal extraction not reexecuted; trailing idle cannot be decided from timestamps | Retrospective annotation-row task; targeted adjudication before any correction | COMPLETE WITH QUALIFICATIONS |
| Metadata diagnostics | Can permitted action/duration/coverage predict failures? | Quantify a plausible alternative explanation without new architecture search. | Three fixed logistic models; same nested recording folds, training-only transforms/calibration/thresholds | D0/D1/D2 keyed OOF files and fitting logs | D1 AP improves over D0; D2 decreases from D1; every diagnostic remains below U1/F2 | Paired recording2000-draw intervals, post-hoc | Does not prove original model mechanism; historical action baseline specification differs | Add metadata caveat without claiming sensor information absence | COMPLETE |
| Action sensitivity | Does actual F2 gain generalize across actions? | Complementarity is not actual subgroup fusion improvement. | All four actions; whole-recording draws then filter; support/invalid draw counts | per_action_fusion.csv | All AP point deltas positive; only insert marginal AP interval excludes zero | Marginal exploratory intervals; place22 failures/21 recordings | Small subgroup precision, no simultaneous positive claim or new macro-AP headline | No uniform per-action gain assertion | COMPLETE |
| Recording weighting | Does gain depend on recording contribution? | Large recordings carry more segment mass in the primary estimand. | Weighted pooled metrics with1/n_r; bootstrap k/n_r | recording_weight_sensitivity.csv | Positive AP/AUROC point gains but CIs include zero; weighted Brier gain persists | 2000 paired recording draws | Alternative target weighting; does not replace primary result | Qualify gain as supported under original segment weighting | COMPLETE |
| Operating points | What do issued flags and misses mean? | AP does not specify decision workload or missed-case burden. | Saved decisions/verified fold thresholds; explicit confusion counts/denominators | operating_points.csv | F2 about29.2 true failures per 100 flags;38.9 missed per 100 failures | Descriptive conditional counts, no new optimized cutoff | Retrospective segments; no validated time-exposure denominator | Report false flags per 100 successes, not per hour | COMPLETE |
| Human review | Do independent reviewers find outcomes and boundaries defensible? | Automated label consistency is not annotation truth. | Seeded64-case recording-spread balanced sample; blinded silent clips; two orders; tested ingestion | review_export_manifest.json and blank sheets; no actual returns | 64 clips ready,62.2MiB, ratings remain blank | Human responses missing | Source familiarity, encoding, average cadence and biased-to-balance qualitative sampling; no invented second reviewer | Keep human review pending; no annotation validation claim | PENDING_HUMAN_REVIEW |

## Preservation and resource scope

3665 retained source artifacts were re-hashed unchanged;148 accessed raw recording metadata identities are unchanged. CPU-side operations with application/BLAS/OpenCV thread limits1; no GPU call, queue modification, new dataset, deep-model retraining, label correction or package upgrade. Codec backend scheduling was not separately instrumented. Human clips/key remain outside Git; do not accidentally export the private key. Source/config/script revisions, corrections, tests and manifests accompany the audit. Stop here.
