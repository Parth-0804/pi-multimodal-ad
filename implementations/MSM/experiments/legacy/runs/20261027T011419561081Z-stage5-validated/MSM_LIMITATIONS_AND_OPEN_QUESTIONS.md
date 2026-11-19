# MSM limitations and open questions

**The current evidence cannot support an external predictive validation or learned-weight-transfer claim.** This is a boundary on inference, not evidence that the architecture cannot learn milling. Full quantitative checks and source links are in `MSM_FINAL_EVIDENCE_REVIEW.md`.

## 1. Material limitations and their effect

| Limitation | Verified evidence / scope | Consequence |
| --- | --- | --- |
| Positive experiment support | 114 paired examples, ten positives in two nominal folders; removing label2 still leaves two positive folders | Frozen three-outer/two-inner validation cannot run. Intervals/seeds cannot substitute for independent positive groups |
| Physical independence unresolved | Five folders collapse to three machine/reference-date clusters, two positive clusters; tool/session identity incomplete | Folder-disjoint does not imply independent tools, days, scenes or physical experiments |
| Native task semantics | REASSEMBLE failure is completed-action outcome; MSM label1 is intervention-worthy cutting abnormality; label2 is stable defective-tool operation | No unified physical “damage/failure” target or direct cross-task score ranking |
| Prevalence and selection | REASSEMBLE 11.2362%; full MSM annotations 18.0583%; eligible MSM 8.7719%; selected smoke 41.6667% | AP/precision/calibration and difficulty are not directly comparable; smoke is not a prevalence estimate |
| Visual visibility | Accepted frames show spindle/workpiece/milling context, often with coolant/window occlusion | Data construction does not show that the abnormality itself is visually observable |
| Smartphone timing | Corrected acoustic mapping and empirical support/bounds; no external optical fiducial; original transcode history incompletely observable | Strong shared-audio evidence is not proof of zero systematic AV/annotation error or robustness to alignment shifts |
| MTC aggregation | Row-level coverage passes, but values are held/pre-aggregated with unknown internal windows/latency | Statistics represent coarse controller context, not guaranteed fresh high-rate within-cut measurements |
| Contract heterogeneity | Common-MTC and raw-ACC cohorts differ; only 39 separate paired ACC examples, overlapping MTC | Do not add cohort counts or concatenate differing feature contracts without a new declared design |
| Industry lacks video | All 13 industrial folders have no listed video; CT/MTC schema and material/machine conditions differ | An industrial sensor-only experiment cannot establish generalization of the visual-plus-sensor architecture |
| Source R unavailable | No completed canonical full-backbone Phase 1 C checkpoint; preflight/active/B-head files are inadmissible | No conclusion that learned REASSEMBLE CNN initialization helps, hurts or transfers |
| Development exposure | Same REASSEMBLE cohort supports many follow-ups; some fits/branches/predictions reused | Later comparisons remain exploratory; repetition of the same F2 score is not independent confirmation |
| Unequal/limited budgets | Initial fine-tuning recipes had five frozen vs two tuned epochs; matched follow-up has only two epochs/two seeds | Initial attribution is confounded; later recipe is bounded, not converged/universal or a source-seed distribution |
| Gate mechanism differences | Core scalar-logit convex gates, static-anchored adaptation and quality interactions are distinct models/objectives | Do not merge their claims. Weight changes/quality terms are not causal reliability explanations |
| Missing robustness trials on MSM | No corruption, missing-modality, misalignment or adaptive-gate comparison | Independent dataset status provides no adaptive-robustness evidence |
| Cost evidence | Stage 3 short shared-T4 loading benchmark, startup effects; Stage 4 zero training; Stage 5 CPU arithmetic only | No full-MSM training cost, sustained GPU utilization or production-latency certification |

The VM20i source XML's `S_Axis_Load` type/units inconsistency remains flagged and uncorrected; source numerical identity is preserved, but physical interpretation needs care. Labels and raw data have not been rewritten to improve coverage.

## 2. Leakage protections and residual qualification

Current audit verified REASSEMBLE whole-recording fold separation (5 outer, 20 inner, 80 sub-inner), saved label/fold identity and F2 coefficient replay. It does not prove the raw labels or physical-session independence. Core F2 threshold cross-fitting uses a prebuilt global branch-OOF bank within outer training, so those internal threshold scores are dependent; no outer-test leakage was newly found, and no redesigned fitting procedure was silently substituted.

MSM excludes target-containing metadata from feature vectors: native labels, Tool/Workpiece, label-sheet process parameters, remarks, filenames, NC/program/outcome fields, timestamps, duration and IDs do not become ordinary predictors. Group/time metadata still governs alignment, quality control and partitioning. Measured speed/feed channels can encode operating-regime confounding despite being legitimate signals. Scalers/class weights/parameters must fit training partitions only.

Temporal averaging over 16 frames is order-insensitive pooling, not temporal attention. Complete annotated boundaries and late process information are legitimate for the retrospective task, but cannot be described as online warning before a failure/cut ends. Correct frame-label association is necessary, not sufficient, for transferable class information.

## 3. Reproduction and provenance limits

**Recalculated now:** native MSM labels/counts/durations and independent MTC formulas; saved REASSEMBLE point metrics/folds/seeds for the audited families; exact saved F2/quality-head arithmetic; core F2-minus-sensor and quality-pilot primary recording-bootstrap intervals. The quality-pilot draw hash exactly matches its source receipt. No new model fit was involved.

**Consistency checked now:** previous MSM output/input hashes, current checkpoint IDs/weight hashes, source/budget selections, Stage 4 empty prediction/curve tables, current development checkpoint ID/scaler/finite-output arithmetic, and completed Phase 1 receipts. These checks rely on preserved artifacts and are not full execution replay.

**Not independently reproduced now:** raw REASSEMBLE annotation-to-array binding, raw video/CNN extraction, phone/audio offset estimation, expert labels, corruption generation, historical optimizer/gradient/recovery traces, all reported intervals, complete training/evaluation or field behavior. The Stage 3 historical reload comparison lacks a saved original final-refit probability vector; its zero-error claim remains a retained execution receipt, supplemented by narrower current checkpoint-arithmetic checks.

The initial Stage 5 bootstrap replay failed because the audit used a different RNG call sequence. Its source/evidence remain preserved; the validated audit uses the original multinomial draw generator. This was an audit reproduction issue, not evidence of a historical model or interval defect. No source result was edited.

## 4. Unsuccessful and inconclusive experiments to retain

- Stage 2's exploratory periodic-lag alias was invalid and corrected before the validated cohort. Report the correction, not the superseded mapping/count as a competing model result.
- Original REASSEMBLE unimodal gates were conditional; engineered statistics outperform the tested short/long PatchTST, even though longer training helps the latter. This is a bounded representation result, not universal Transformer inferiority.
- Hybrid encoder visual/fused scores are lower in the fixed comparison; different widths/costs prevent attention-only causation.
- Original clean scalar gates do not meet their incremental criteria, and original high-severity joint mechanism/outcome successes are 0/12. A later clean anchored AP gain prevents universal “adaptive fusion never helps” wording.
- Quality-pilot primary difference **+0.003012 [-0.026711,0.032165]** is inconclusive; clean noninferiority remains unresolved.
- Matched 32-frame fine-tuning has opposite visual point directions across seeds and no resolved F2 gain. Earlier unequal budgets and prior exposure remain documented.
- MSM Stage 4 was **not admitted**, not a failed classifier. Its 54 blocked result slots contain no AP/AUROC values, zero prediction rows and zero selected models.

Non-significance does not show equivalence. A missing experiment does not show absence of signal. A model/head being trainable does not establish useful learning or generalization. A lower Brier score under one protocol does not establish calibrated deployment risk on another dataset.

## 5. Open questions and proportional future evidence

| Question | Evidence needed before answering | Present status |
| --- | --- | --- |
| Does the adapted architecture predict MSM abnormal cuts? | Larger alignment/visibility/sensor-audited cohort; defensible dependency groups; valid frozen nested folds; all models/metrics under identical roles | Unanswered |
| Do REASSEMBLE-learned CNN parameters help? | Completed provenance-verified canonical source; same frozen/fine-tuning rule for P/R; new head/scalers; matched frames/roles/budgets/seeds | Unanswered; structural compatibility only |
| Does F2 add value on MSM? | Separate complete P/R training-side group-OOF probabilities, new stackers and untouched outer predictions; paired group uncertainty | Unanswered |
| Is an effect stable? | Report all predeclared seeds/folds, enough genuinely independent positive groups; distinguish MSM fit-seed variation from source checkpoint variation | Unanswered on MSM; source data cannot be multiplied by seed count |
| Can video contact or high-rate sensors improve the evidence? | Expert visibility review, known aggregation/latency or a separately declared ACC contract; no automatic cohort mixing | Engineering possibility, not a measured benefit |
| Can adaptive quality help under realistic failure? | A separately frozen matched-augmentation/gate comparison with sufficient groups and named missing/degraded conditions, including clock shifts if claimed | No MSM evidence; REASSEMBLE remains bounded/exploratory |
| Is deployment feasible? | Prospective boundary/latency assumptions, cold/end-to-end resource measurements, calibration under actual prevalence, operational costs and external sessions | Not established |

None of these questions mandates inventing a new experiment or expanding the thesis without review. Stage 5 authorizes consolidation only; no new fitting, threshold tuning, raw feature extraction or robustness campaign was run. The current defensible thesis can transparently report partial answers and explicit external-validation limits.
