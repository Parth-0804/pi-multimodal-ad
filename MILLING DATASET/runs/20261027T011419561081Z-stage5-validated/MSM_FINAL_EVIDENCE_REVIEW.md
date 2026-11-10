# MSM final evidence review

**Scientific verdict:** MSM supports a versioned, alignment-audited engineering feasibility case for a coarse visual-plus-sensor interval classifier. It does **not** currently establish independent predictive adaptation, REASSEMBLE-trained CNN transfer, F2 benefit on MSM, seed stability or modality robustness. REASSEMBLE separately retains bounded representation/fusion evidence. These conclusions are different and must remain separate in the thesis.

Review UTC: **2026-10-27T01:15:26.436497+00:00**. Run `MILLING DATASET/runs/20261027T011419561081Z-stage5-validated`. No model was trained, no optimizer update ran, no raw CNN inference was performed and no CUDA context was created. Frozen MSM dataset: **`manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`**, Kaggle ID 8392825, [dataset DOI](https://doi.org/10.34740/kaggle/ds/8392825); [publication](https://www.nature.com/articles/s41597-026-07255-7). Stage 1 established official identity and version; this consolidation checks the retained pinned evidence, not a new live download.

## 1. Sources, chronology and evidence language

Primary question wording was read directly from [original nine-page exposé](<../../../MA_Exposé_Ravaliya_Parth.pdf>), pp.2–3; PDF SHA-256 **9f7e1c09db5678fe268a39eb8af823cb965153cc69a8922c129117fd815fb6e6**. The repository's October 25 alignment record accurately recovers those questions. Its historical statement that MSM was unexecuted is superseded by October 27 Stages 1–4 for acquisition/implementation, **not** by a successful MSM accuracy evaluation. Earlier original-question proxy statements are not treated as newer authority than the PDF.

Reviewed MSM evidence: [MSM native-label audit](<../20261026T230520276818Z-stage1/MSM_LABEL_AUDIT.md>); [validated MSM alignment](<../20261027T001047876764Z-stage2-validated/MSM_VIDEO_ALIGNMENT_REPORT.md>); [frozen MSM protocol](<../20261027T003527238586Z-stage3/MSM_STAGE3_EXPERIMENT_PROTOCOL.md>); [MSM Stage 4 status](<../20261027T005343579234Z-stage4/MSM_STAGE4_MODEL_RESULTS.md>); their acquisition, architecture, implementation, transfer/generalization, validation, manifest and checkpoint artifacts. Relevant REASSEMBLE evidence: [REASSEMBLE unimodal metrics](<../../../runs/reassemble/20260927T154732Z-section1/assessment/results.json>), [REASSEMBLE static-fusion metrics](<../../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json>), [REASSEMBLE clean-fusion comparison](<../../../runs/reassemble/20260927T192852Z-section2/assessment/results.json>), [REASSEMBLE corruption results](<../../../runs/reassemble/20260927T204649Z-section3/results.json>), temporal pooling, encoder comparison, matched 32-frame fine-tuning, longer sensor training, anchored clean adaptation, quality-aware robustness pilot and the live Phase 1 completed-fit receipts.

Use these evidence levels throughout:

| Level | What it means here | What it does not mean |
| --- | --- | --- |
| Independently recalculated from native MSM inputs | Re-read 69 actual label files; recounted classes/groups/durations; recomputed 114 × 90 cut statistics directly from actual MTC rows using independent NumPy formulas | Independent expert label adjudication, physical sensor synchronization or model retraining |
| Recalculated from saved predictions | Recomputed point metrics, exact coefficient arithmetic and two selected 2,000-draw bootstrap comparisons | Raw-input-to-trained-model replication or fresh external confirmation |
| Saved-artifact consistency/provenance checked | Hashes, row IDs, group memberships, budgets, checkpoints, selected epochs and stated execution status agree | Proof that every producing code path executed exactly as reported or every physical group is independent |
| Retained historical execution evidence | Reports/receipts document prior decode, gradients, recovery and throughput checks | Those operations were rerun in Stage 5 |
| Unperformed / unresolved | Required data/source/evaluation or experiment is absent | A zero accuracy result, negative transfer, equivalence or universal methodological failure |

## 2. Why MSM was selected and what preceded implementation

MSM provides a second industrial process and native cutting-interval annotations, laboratory process video/audio and numerical machine signals. That made it a plausible test of whether modular visual/sensor interfaces can be adapted beyond robotic assembly. Selection was based on those testable data properties, not known MSM outer-test superiority. It is an independent dataset, not automatically an independent *evaluation* or robustness test. This distinction follows the actual staged work, rather than retrospectively describing every failed prerequisite as a planned contribution.

Stage 1 resolved the exact official handle and pinned version, inspected 481 listed files totaling 40,412,136,430 bytes, verified the 37/19/13 machine-folder counts and acquired all 69 labels. Native annotations yield **2,575 candidate cuts**, labels **0=1,933; 1=465; 2=177**, with label 1 in 30 nominal folders. Duration min/median/max: **0.533 / 3.008 / 408.529 s**. Candidate labeled cuts are not all paired visual examples. Stage 5 independently reproduced the native totals and checked all **104 acquired source files** against their hashes.

Stage 2 selectively acquired 35 pilot modality/metadata files (about 1.196 GB), not the 40.4 GB archive. It verified actual schemas, audio/video durations, non-square video pixels, label-blind acoustic alignment, native frame identities, sensor coverage and camera visibility. Its final **114 common-MTC examples** have native counts **93/10/11**. The separate 39-example raw-ACC contract overlaps the MTC cohort and must not be added to it. VF10 industry has no video.

The exploratory VMX30Ui/dataset9 offset near +16.04 s was rejected after an inappropriate whole-record overlap rule excluded the correct offset. Corrected calibration/held-out acoustic evidence fixes **+49.73 s ±0.10 s**. Exploratory counts/frames were superseded by the validated Stage 2 revision. Stage 5 checked the corrected saved-PTS/guard and native-annotation association, **not** new acoustic fitting or video decoding. Coolant often hides the actual interface; accepted frames show milling context, not necessarily visible anomaly/tool damage.

Stage 3 reviewed those constraints before adapting the verified model primitives. Its bounded smoke checked forward/gradient paths, prediction units, OOF group provenance and checkpoint serialization. Current audit independently reconstructed all MTC statistics: maximum absolute difference **6.1035156e-05** in native feature units, within the declared numerical tolerance. That arithmetic agreement does not resolve unknown MTC aggregation-window latency.

## 3. Architecture portability versus learned-weight transfer

Reused: existing REASSEMBLE local pretrained **R18vd ResNet CNN** (11,190,112 parameters), spatial mean pooling of the final three maps to 896 values, temporal mean over 16 frames, the existing 128-unit head constructor/standardizer and the static two-probability stacking pattern. The detector, hybrid encoder/Transformer and learned temporal attention are not executed in the retained core. Calling the reused CNN a visual Transformer would be inaccurate.

MSM-specific work: immutable native interval/label adapter, corrected frame/clock selection, SAR-preserving 640×640 letterboxing, MTC loading/coverage, six statistics over 15 configured numerical channels, stable-cutting label mapping and experiment groups. REASSEMBLE's robot sensor identities, 512-position sequence and 220-statistic vector were not imposed on MSM. Group/timestamp/tool/remark/label-sheet metadata does not enter the predictor arrays.

Components requiring new fitting: visual classifier **896→128→1**, sensor logistic classifier and scalers, and **three-parameter static F2** from group-held-out branch probabilities. The Stage 3 development smoke fitted these components for its small plumbing test; **full held-experiment fitting never ran**. No REASSEMBLE failure-classification head, source-domain scaler, calibrator or F2 coefficient was reused. Original pretrained CNN reuse across tasks is distinct from transferring CNN weights learned on REASSEMBLE.

Stage 4's R condition required a completed, validation-selected full-backbone Phase 1 C checkpoint. No such admissible source existed then; at this audit there are **0 completed C fits**, and the fixed canonical R role's completion receipt exists: **False**. One completed B fit only trains a head while keeping the original CNN frozen. Active C files and full-CNN preflight weights cannot substitute for a completed source model.

Stage 4 found all **115 diagnostic CNN tensors structurally compatible**, excluding the four source head tensors and `mean/std`. Normalization affine values retain state-dict names despite source Parameter promotion, so they can map into the frozen target's buffers. This is serialization compatibility. Diagnostic tensors were never used as R on MSM, and Stage 5 only checks that saved compatibility/provenance evidence and unchanged file identities. **Learned-weight transfer success or failure is unmeasured.**

## 4. Tasks and class prevalence are different

| Property | REASSEMBLE primary study | MSM |
| --- | --- | --- |
| Prediction unit | Completed high-level action segment | Completed annotated cutting interval |
| Native positive | `failure = 1 - success`, four assembly action types | Native label 1: abnormal cutting warranting intervention |
| Other native classes | Success | Label 0 stable normal; label 2 defective tool during stable cutting |
| Retained binary target | Failure vs success | Label 1 vs stable cutting labels 0/2; exclude-2 sensitivity declared separately |
| Counts / prevalence | 509/4,530 = **11.2362%** failure; 148 recordings | Full labels: 465/2,575 = **18.0583%**; eligible pilot: 10/114 = **8.7719%**, five folders |
| Actual learning-test status | Saved recording-disjoint held-out predictions exist; repeatedly exposed exploratory sequence | Only a 24-example development smoke; zero held-out Stage 4 predictions |
| Main limits | Recording grouping is not independent session/site/object evidence; full action boundaries known | Only two positive folders, unclear physical dependencies, coarse visual/MTC timing contract |

The smoke deliberately used ten positives in 24 samples (41.67%); it is not an estimate of deployment prevalence. The 103-example exclude-label-2 sensitivity still has only two positive groups and cannot rescue evaluation. AUROC/AP from different tasks are not a cross-domain ranking; AP also depends on prevalence and cohort composition. Neither offline complete-segment task demonstrates prospective early warning. Label 2 is not silently recoded as abnormal.

## 5. Verified REASSEMBLE discrimination and fusion evidence

Stage 5 independently recalculated **1654 saved point metric values**, including core folds/seeds, named corruption conditions, temporal/encoder/controlled-32 and later sensor/anchored comparisons; maximum absolute difference **1.11e-16**. Audit table: `manifests/metric_recalculation_checks.csv`. This is fixed-prediction reproducibility, not retraining.

| Core model | AP | AUROC | Interpretation |
| --- | ---: | ---: | --- |
| Sensor statistics | 0.429392 | 0.779325 | Strongest tested original unimodal sensor reference |
| Frozen CNN | 0.230658 | 0.697795 | Standalone prediction weaker; incremental complementary information possible |
| Short PatchTST | 0.241591 | 0.705351 | Does not beat statistics at its tested budget |
| Static F2 | 0.447299 | 0.794968 | Bounded improvement over original sensor reference |

Reconstructed 2,000 paired recording-cluster draws give **F2 minus sensor AP +0.017907 [0.008603, 0.028284]**, AUROC **+0.015644 [0.006030, 0.025465]**. Brier improves by **-0.002005 [-0.003099, -0.000908]**. Exact saved F2 coefficient arithmetic reproduces with maximum error **0.0**. Source [REASSEMBLE static-fusion metrics](<../../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json>); recalculation `manifests/REASSEMBLE_core_audit.json`.

The branches are unchanged when static F2 is added; this is fusion complementarity, not an improved CNN. Core F2 is reused exactly in later core sections, so repeated appearances of AP 0.447299 are **not independent replications**. Original F4/F5/F6 do not meet their clean incremental-AP/AUROC criteria. That bounded result is not universal adaptive-fusion failure.

Later results prevent blanket summaries: longer PatchTST reaches **0.285311 AP**, improving its matched short reference **0.255658**, but still below statistics; same-sensor hybrid AP **0.440347** is not image/sensor fusion. Separately anchored clean adaptation reaches **0.468312 AP** versus A0 **0.447299**; saved ΔAP interval **[0.0015,0.0419]** supports that bounded clean comparison, while its AUROC gain remains unresolved. Those later point metrics were recalculated; their historical contrast intervals were read and identified, not regenerated here. They use different selection/threshold rules and cannot be merged into a new best-model tournament.

## 6. Visual improvement is not automatically fusion improvement

The controlled 32-frame follow-up used matching two-epoch action budgets per recipe, two fixed seeds and identical sensor scores. New calculation from its saved assessment tables:

| Seed | Visual AP, frozen → final-stage tuned | F2 AP, frozen → final-stage tuned |
| --- | --- | --- |
| 42 | 0.222708 → 0.230609 | 0.439363 → 0.438566 |
| 20261023 | 0.216799 → 0.200517 | 0.435202 → 0.432380 |

At seed 42, the visual point gain coexists with a lower F2 point score; at the second seed visual improvement itself disappears. Saved F2-difference intervals span zero for both seeds. No causal explanation or equivalence is established. All **100 fit receipts/checkpoint hashes** match their index and all report two epochs; 25 fits were reused rather than independently repeated. Equal action/epoch budgets do not imply equal compute. Source [controlled two-epoch 32-frame results](<../../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results/comparison/fusion_results.csv>).

There is also a different positive exploratory representation result: last-quarter pooling increases visual AP **0.230658→0.319146**, and its newly fitted F2 reaches **0.493437**. This retains pretrained CNN weights, changes retrospective temporal aggregation, and selects on repeatedly studied data under a single base-seed policy. It is not evidence of full-CNN learned-weight transfer or three-seed robustness, nor a reason to silently replace MSM's fixed whole-cut frame policy. The frozen hybrid-encoder comparison is a separate negative: visual AP **0.221644→0.171915**, fused AP **0.440764→0.424979**, with a shared sensor reference. Different head widths/costs prevent an attention-only causal conclusion.

## 7. Robustness evidence stays domain- and protocol-specific

All point metrics across the original **22 REASSEMBLE clean/fault conditions** were recalculated from saved predictions. Original F5/F6 have **0/12** joint adaptation/smaller-degradation criterion successes at the highest tested family severities. This does not erase condition-specific results or prove every adaptive method fails. Complete absence uses an explicit surviving-branch policy; mask-enforced weight changes are not learned reliability or recovered information. Source [REASSEMBLE corruption results](<../../../runs/reassemble/20260927T204649Z-section3/results.json>).

The later augmentation-matched quality-interaction pilot has **34 hash-verified tables**, **196 AP values** exactly reproduced and **70,029 probabilities** reconstructed from saved coefficients (maximum error **7.77e-16**). Its exact original multinomial draws reproduce mean AP C−A **+0.003012**, 95% **[-0.026711, 0.032165]**. It remains inconclusive on one exposed fold/26 recordings; clean noninferiority is not demonstrated. Source [quality-pilot contrasts](<../../../00_experiments/adaptive_fusion_robustness/results/run_01/comparison/paired_intervals.csv>).

**MSM has no corrupted/missing-modality evaluation, no adaptive-gate evaluation and no learned-weight transfer result. Merely being an independent dataset answers none of those robustness questions.** Acoustic timing validation is also not a test of model robustness to cross-modal misalignment. Synthetic REASSEMBLE faults do not establish field-failure distributions or MSM resilience.

## 8. Grouping, leakage, budgets and selected epochs

Checked core REASSEMBLE cohort identities, five whole-recording outer folds, **20 inner partitions** and **80 sub-inner partitions** used for F2 branch selection/calibration exclusion. Saved predictions match cohort labels and group/fold assignments. This checks the declared group separation, not the original raw annotation binding or physical-session independence. F2 threshold cross-fitting conditions on an already-constructed branch OOF matrix; its internal threshold scores are not unbiased independent validation. That disclosed training-side dependence is not a newly demonstrated outer-test leak. Repeated adaptive use of the same outer outcomes also limits confirmatory claims.

MSM's five nominal folders collapse to three machine/reference-date clusters; only two positive clusters exist and physical tool/session identities remain unclear. Three outer tests cannot each contain positives from two positive folders. Holding one positive folder out leaves one positive training folder, insufficient for two-fold group-held-out F2 construction. Both laboratory machine-held-out directions fail that same inner support check. Industry cannot supply a matched visual cohort. No fallback split or sensor-only substitution was executed.

| Study | Budget / seeds / selection verified or source-inspected |
| --- | --- |
| REASSEMBLE core CNN | Epoch candidates 5/10; selected outer epochs **5,5,10,10,5**; original base seed 20260927 with recorded fold/refit offsets, not a three-seed stability experiment |
| Core PatchTST / statistics | Epoch candidates 3/6; selected **6,6,6,6,6**; sensor C grid 0.1/1/10 selects **1,0.1,10,0.1,0.1** |
| Core fusion/gates | Seeds **20260927,20260928,20260929**; declared finite inner-selected head grids; seed metrics checked; static F2 has no neural epoch budget |
| Controlled 32-frame follow-up | Exactly **two epochs**, both recipes, seeds **42,20261023**; 100 indexed receipts/weights checked; not full-backbone Phase 1 |
| Full-backbone Phase 1 | Fixed seeds **42,123,20261023**, 25–50 epochs with training-side validation selection. At audit only completed B seed42/job0: **25 executed, epoch9 selected**. No final C source available; active values are not final selections |
| MSM frozen protocol | Ten fixed head epochs, no search/early stopping, seeds **42,123,20261023**; three outer/two inner intended, never admitted |
| MSM actual Stage 3 smoke | Root seed42; two epochs per development fit, six pipeline head updates plus four CPU/CUDA head-check updates = **10 total**; **528 CNN frame forwards**. Not the intended seed/fold matrix |
| MSM Stage 4 / Stage 5 | **Zero fitted models or optimizer updates**; missing results are explicit, not silently omitted |

## 9. Independent reproduction limits and unsuccessful work

The audit reproduced *from native files* the MSM annotation and statistical-feature calculations. From *saved predictions* it reproduced metric arithmetic, fold/seed values, exact F2/quality-head formulas and two selected conditional cluster intervals. It checked original pretrained identities, completed Phase 1 and controlled-study checkpoint hashes and MSM development checkpoint structure/scaler IDs; independent NumPy forward arithmetic yields finite probabilities, without scoring the development labels.

It did **not** rerun raw CNN/video extraction, acoustic offset fitting, model training, historical optimizer/gradient/recovery events, raw corruption generation, physical-label adjudication, all historical bootstrap intervals or the raw REASSEMBLE target join. In particular, Stage 3's historical save/reload zero-error check is retained execution evidence: the original final-refit probability array was not preserved, so its historical execution comparison cannot be independently replayed from that array. Current saved-checkpoint arithmetic is a narrower check. No new training is essential to the bounded conclusions above, and none was requested or performed.

Retain negative/inconclusive findings: original unimodal gate conditional; tested short/long PatchTST below statistics; hybrid visual encoder loss; original clean scalar gates not qualifying; original synthetic mechanism criterion not met; quality-pilot broad interval; initial fine-tuning budget confound and mixed matched-budget seed effects; rejected MSM exploratory alignment; Stage 4 cohort/source block. A blocked experiment is **not** a failed model-accuracy or negative-transfer result. Non-significance is not equivalence.

The [preserved first Stage 5 audit attempt](<../20261027T010816468715Z-stage5>) is preserved because its first quality-bootstrap replay used the same bootstrap law but a different RNG method (`integers` rather than the original `multinomial`). The guard correctly rejected deterministic parity. The validated run restores the original draw sequence, SHA-256 **952337616b24490835679c3506fac73498115a2f9e3b922275ea9da72bdb59bc**. No historical evidence, target, fitted model or conclusion was changed to obtain agreement.

## 10. Mapping to the four original exposé subquestions

The original main question centers architecture design/evaluation. SQ1 asks about suitable lightweight/pretrained representations; SQ2 compares unimodal, concatenation, late and process-aware gated fusion; SQ3 asks about missing/degraded/unreliable modalities; SQ4 asks about evaluation beyond accuracy. The original PDF's wording, original welding case study and later task/domain changes should be stated explicitly; no final-title approval is inferred from this audit.

| Research question | REASSEMBLE evidence | MSM evidence | Defensible conclusion | Remaining limitation |
| --- | --- | --- | --- | --- |
| SQ1: Representations | Recalculated core AP: statistics 0.429392, frozen CNN 0.230658, short PatchTST 0.241591. Longer PatchTST 0.285311 still trails statistics; separate hybrid visual encoder loses its fixed comparison. Boundary pooling is a separate positive exploratory visual result. | 16 aligned frames plus 90 statistics are feasible for 114 intervals; new-head/sensor/F2 smoke works. No held-experiment performance; no audio classifier. | Tested representations can be implemented and compared, and simpler representations can be competitive under specific budgets. MSM adds engineering feasibility, not external predictive validation. | The retained RT-DETR path is a ResNet CNN, not its Transformer/detector. Audio/AST and literal trimodal scope remain untested; richer candidates, budgets and causal explanations are incomplete. |
| SQ2: Fusion strategies | Core F2 AP 0.447299 versus sensor 0.429392; paired gain +0.017907 [0.008603,0.028284]. Original gates do not meet their clean incremental criteria. Later anchored adaptation improves clean AP under its separate protocol. | Fresh static F2 is implemented and smoke-fitted from group-OOF branch probabilities; Stage 4 has zero held-out predictions. No MSM adaptive gate comparison. | Small learned late fusion adds bounded value in REASSEMBLE; visual gains and fusion gains must be measured separately. No MSM F2-value conclusion is available. | Repeated same-cohort development; different protocols must not be pooled. Original scalar-logit gates materially adapt the exposé's projected-representation proposal. No universal static/adaptive ranking. |
| SQ3: Robustness | Original F5/F6 satisfy neither joint mechanism/outcome criterion across all tested highest-severity family comparisons (0/12 successes). Exact missing-branch fallback is imposed. Later augmentation-matched quality pilot: +0.003012 AP, CI [-0.026711,0.032165], inconclusive. | No missing/degraded/corrupted-modality experiment; an independent dataset and valid clock mapping do not test adaptive reliability. | Robustness is partially investigated on REASSEMBLE under named synthetic faults; MSM contributes no adaptive-robustness evidence. | Synthetic faults, exposed data, limited realizations, and untested cross-modal clock shifts/field failures. No clean noninferiority or universal reliability awareness. |
| SQ4: Evaluation | Recording-group folds, OOF stacking, calibration/threshold metrics, cost records and modularity are auditable. Selected metrics/intervals reproduce from saved predictions. | Version pinning, native labels, timing/visibility gates, raw statistics, strict split/source admission and explicit unavailable results prevent unsupported external claims. | Strong contribution in traceable evaluation and research software; operational assurance is a distinct unresolved question. | Recording/folder separation does not prove physical-session independence. Gate weights are not causal explanations; warm/shared GPU timings do not certify deployment or prospective warning. |

## 11. Thesis disposition

Use REASSEMBLE for the protocol-labeled representation/fusion and bounded synthetic robustness results. Include MSM as an external feasibility/portability and evaluation-boundary case, with official provenance, corrected alignment, native labels, actual cohort size, new adapters and explicit blocked Stage 4. Do not place fabricated MSM AP values in a comparative accuracy table or title MSM as successful external validation/weight transfer.

The companion contribution, limitations and presentation reports provide admissible wording. Sources and audit inputs are hashed in `manifests/input_manifest.json`; reproducibility scope is in `validation.json`. Raw data, original reports/checkpoints and active training remain unchanged. No novelty, universal superiority, out-of-domain predictive generalization or deployment-robustness conclusion follows beyond the named evidence.
