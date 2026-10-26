# Evidence map aligned to the original exposé

TASK 2B revision, 2026-10-25 (Europe/Berlin); code baseline `3c4fb20be`. **Current alignment layer.** The original TASK 2 evidence map is preserved verbatim in the historical appendix below. Its numerical checks remain prior-review evidence; its statements that the exposé or dataset-transition agreement were unavailable are superseded.

## Authority and evidence levels

The [original exposé](../../MA_Exposé_Ravaliya_Parth.pdf), §3 pp.2–3, defines the original main RQ/SQ1–SQ4. Exact quotations and the proposed dataset-adapted main wording are in [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md). The October 6 review §1.1 records **RESEARCHER-CONFIRMED CONTEXT**: supervisor agreement to PHM + REASSEMBLE. Accept that agreement; do not convert it into documentary final-title approval or reopen it as a permission gap.

In this revision, **VERIFIED** identifies direct PDF/source/config inspection; **VERIFIED IN TASK 2** identifies the earlier bounded saved-output checks preserved below. **REPORTED** identifies a run report or another review's checks not repeated here. **INFERRED**, **PROPOSED**, and **UNKNOWN/UNVERIFIED** remain distinct. The October 6 report's “VERIFIED IN THIS REVIEW” describes that earlier review, not a newly performed TASK 2B check. Its export restrictions do not prove files are missing from the live repository. No new training, model inference, bootstrap, raw-data audit or full cohort join was performed for this reconciliation.

## Question-to-experiment alignment

| Original question / objective | Actual experiments and result | Answer status and limits | Primary inspected source |
|---|---|---|---|
| Main: process-aware architecture design/evaluation | E1 PHM target/sensor pipeline; E2/E3 REASSEMBLE representations and F1–F6; E4/E7/E8 architecture diagnostics; E5/E6 synthetic robustness | **PARTIALLY ANSWERED under agreed cases.** A modular pipeline and comparative evaluation exist. Physical defect truth, online operation and universal robustness are not established. | Exposé §§3–6; actual feature/model/gate code linked below |
| SQ1: visual representation suitability | Core CNN features; E4 CNN vs spatial hybrid encoder: F2 AP 0.440764 vs 0.424979 under its own fixed recipe; E7/E8 frame/fine-tuning controls | **ANSWERED for tested alternatives; PARTIAL overall.** Backbone extraction is allowed. E4 executes a spatial Transformer path, not temporal video attention; E7's unequal epoch budgets and E8's two seeds restrict conclusions. | `section1_features.py::load_visual/extract`; encoder `features.py::forward`; E4/E7/E8 configs/results in preserved map |
| SQ1: sensor suitability | Core PatchTST AP 0.241591 vs statistics 0.429392. September S-LONG improves over its matched short recipe but remains below statistics; same-sensor hybrid reports a gain | **ANSWERED for tested budgets.** Evidence against selecting standalone tested PatchTST as the strongest core branch, not against all Transformers or the sensor modality. | `section1_models.py::SensorHead/logistic_fit`; Section 1 config; later extension handoff |
| SQ1: audio/AST and broad candidate review | Audio timing feasibility exclusion; no predictive audio/AST/trimodal comparison established | **UNTESTED predictively / PARTIAL modality scope.** Not a failed audio model. The exposé lists candidates, not a requirement to train every named family. | Exposé §5.2; October 6 §§3,7; retained research contract/audio feasibility records |
| SQ2: unimodal, concatenation, late and process-aware gated fusion | Core U1/U2; F1 uniform AP 0.445742; F2 stacker 0.447299; F3 concatenation 0.412231; F4 action 0.443725; F5 quality 0.444549; F6 combined 0.441356 | **ANSWERED for adapted bimodal comparison; PARTIAL literal §5.5 design.** F2–U1 AP +0.017907 with REPORTED interval [0.008603,0.028284]. No original gate qualifies for the specified clean increment. Scalar-logit gates are not the projected-embedding design verbatim. | `section1b.py::fit_stacker`; `section2_models.py`; `section2.json`; retained Section 2 results |
| SQ3: original gate robustness expectation | Core F5/F6: no one of 12 high-severity family/gate checks establishes the combined directional-mechanism/outcome criterion | **BOUNDED NEGATIVE for tested original mechanism; PARTIALLY ANSWERED question.** Do not state universal adaptive failure or claim causal isolation from F2's different function class/calibration. | [Core robustness handoff](../../artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md), mechanism table; `section3_corruptions.json` |
| SQ3: declared complete modality loss | Known-absence masks and explicit surviving-branch fallback; both absent abstains/raises at component boundary | **STRUCTURAL POLICY TESTED/REPORTED**, not evidence that a learned gate predicts missingness or outperforms identical fallback. TASK 2 checked the October pilot's routing arithmetic; core full-system parity was not newly checked. | `DecisionGate.forward`; pilot `quality_fusion.py::route`; core config missingness policy |
| SQ3: partial degradation follow-ups | E5 noise sensitivity; E6 augmentation-matched quality interaction AP delta +0.003012, CI [-0.026711,+0.032165] on 26 assessment recordings | **INCONCLUSIVE incremental adaptive result.** This is H-SQ3-Q, not the main RQ. Different uncertainty, families, branch recipes and coverage from core/September work. | E5/E6 protocol, config, saved-table checks and report paths preserved below |
| SQ3: misaligned streams and external validity | No cross-modal clock-shift or external industrial validation established by these sources | **UNTESTED.** Temporal block dropout, frame loss, last-quarter pooling and missingness do not simulate sensor-clock offset. External validation was not a mandatory original §5.6 test. | Exposé §5.6; actual core corruption config; October 6 §3 |
| SQ4: broader evaluation | AP/AUROC, threshold confusion counts, Brier/ECE, ablations, interfaces/provenance and warm component compute/timings | **PARTIALLY ANSWERED.** Allocation is inspectable but not causal interpretability; no production latency SLA, operator usability trial or unrestricted hot-swap validation. | Exposé §5.7; Section 2 code/config; October 6 §§5–9 |

## Additional retained evidence that narrows blanket conclusions

The [September additional-improvements handoff](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md) was inspected directly in TASK 2B. Values below are **REPORTED**, not newly recomputed:

- **Sensor training/representation:** S-LONG−S-6 AP +0.0297 [0.0122,0.0451]; S-LONG AP 0.2853 remains below statistics 0.4294. S-HYBRID−statistics +0.0110 [0.0054,0.0181] combines two representations of the same sensor modality, not new multimodal evidence.
- **Static-anchored adaptation:** A-ADAPTIVE AP 0.4683 versus matched A0 0.4473; delta +0.0210 [0.0015,0.0419]. This separate exploratory clean result prevents “adaptive fusion never helped.” AUROC improvement remains unresolved and recall/ECE trade-offs remain.
- **Historical September Task 4:** augmentation-matched mean six-condition adaptive−static AP +0.0097 [-0.0034,0.0228], inconclusive. It is distinct from October E6 and is not a current execution instruction.
- **Boundary pooling:** [separate handoff](../../artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md) reports last-quarter visual AP 0.319146 and a selected static-fusion AP 0.493437 versus its original F2 0.447299. This is a separate same-cohort follow-up with one historical seed, not a combined sensor-hybrid/anchored winner or prospective warning model.
- **Cancelled versus completed work:** the September extension Task 1 was discontinued; October E7 and E8 are separate completed studies. Do not transfer cancellation status, budgets or scores across these protocols.

These results have different comparator families and selection histories. Neither the original-gate negatives nor later exploratory positives can be generalized to every adaptive architecture. Do not create a new leaderboard by pooling core, September extension and October studies.

## Required implementation distinctions — source-inspected in TASK 2B

1. [Core visual extraction](../../src/reassemble/section1_features.py) takes `.model.backbone.model`, pools `feature_maps`, then averages frames. Exposé p.4 allows this. The [separate encoder forward](../../00_experiments/rt_detr_encoder_comparison/code/features.py) calls projections and `.encoder`; it supplies spatial attention, not temporal attention or full detection.
2. [Sensor code](../../src/reassemble/section1_models.py) separates statistical logistic fitting from `SensorHead(PatchTSTModel(...))`. The PHM [custom Transformer](../../src/phm2026/models/patchtst/model.py) is a different variable-length implementation. Selecting statistics does not erase the executed PatchTST comparisons.
3. [Original gates](../../src/reassemble/section2_models.py) allocate convex weights to calibrated logits. [October quality interactions](../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py) use a logistic design matrix of probabilities, quality and interactions, with a direct quality term. F2 is unrestricted affine probability stacking. They do not share a single mathematical “adaptive gate.”
4. Complete segments and known annotation boundaries define the REASSEMBLE task. This fits the exposé's allowance for supervised classification (§5.1) but does not establish online anomaly warning. PHM predicts a provisional end-of-run image score; it is not simultaneously deployed image+sensor fusion.
5. The inspected [core corruption configuration](../../configs/reassemble/section3_corruptions.json) perturbs signals without changing timestamps. Synthetic input faults and retrospective labels do not provide external field validation.

## October 6 assurance concerns retained without automatic execution

- **PHM token grid:** inspected current `PatchTSTRegressor.patchify` uses padded batch length for the minimum-cover grid and any-real-point validity. This supports the reported static concern; no neural output or historical-score impact was measured here. It is not cross-sample attention or a demonstrated REASSEMBLE defect.
- **Effective metadata:** PHM inherited v2/fixed-split/GPU fields must be distinguished from pinned v3 targets, effective LOEO folds and the recorded CPU command. Frozen metadata is not rewritten.
- **Identity:** October 6 lacked a Parquet reader and did not execute the core cohort-to-array join. TASK 2 later recomputed PHM CSV errors and separately checked keyed October prediction banks/25 jobs. Those checks do not automatically close original target binding, the full core identity chain or historical producing-source gaps.
- **F2 internal threshold qualification:** October 6 §5.4 describes dependency through the already-built global branch OOF matrix, confined to outer training. It is an accepted disclosed limitation, not a newly demonstrated outer-test leak. No deeper threshold procedure is silently substituted.
- **Human review:** October 6 §9.3 reports one returned 64-clip audit, 57/59 determinate agreements, five indeterminate and two disagreements; no second-rater reliability or final adjudication established. “No human returns” is superseded; population label accuracy remains unverified. No raw ratings/private mapping were read here.

## Relation to prior checks and preservation

All E1–E8 numbers, source paths, caveats, reproduction examples and compact hashes from TASK 2 remain intact below. “VERIFIED” in that preserved document refers to TASK 2's stated checks, not new calculations in this revision. Statements about absent original sources or needing dataset-switch approval are historical and superseded by the current layer. See [EXPOSE_ALIGNMENT_DECISION.md](EXPOSE_ALIGNMENT_DECISION.md) for source identities, every material change and preservation validation.

<details>
<summary>Preserved TASK 2 proposal — historical snapshot; current TASK 2B text above takes precedence</summary>

The following earlier proposal is preserved verbatim for provenance. Its original research hierarchy, missing-source statements and approval questions are superseded where corrected above. Numerical/source evidence retains its original review scope.

<!-- TASK2_SNAPSHOT_BEGIN -->
# Existing evidence map

Review date: 2026-10-25 (Europe/Berlin). Baseline commit: `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.
Scope: read-only inspection of selected code/configuration, saved predictions, manifests and reports. No training, raw-input inference or checkpoint/pixel replay was performed; saved fusion coefficients were used only for arithmetic verification. No dataset was downloaded or substantially scanned. New writes are limited to the five review documents. This is a bounded audit, not certification of every repository file.

## Evidence vocabulary

| Status | Meaning in this review |
|---|---|
| VERIFIED | Directly inspected source/configuration, or independently recomputed a stated property from saved evidence; scope is specified |
| REPORTED | A retained report/receipt states the result or execution fact; not independently repeated here |
| INFERRED | Interpretation of inspected evidence; alternatives remain |
| PROPOSED | Future question, design or decision, not an executed result |
| UNKNOWN / UNVERIFIED | Required evidence was not located, accessed or established |

Verifying a stored prediction's arithmetic does not verify its raw input, true physical label or training history. Existing assistant self-review receipts remain REPORTED execution evidence; this review does not convert them into external scientific review.

## Git and previous-study delivery

Initial `git --no-optional-locks status --short --branch --untracked-files=all`: clean `main...origin/main`. Recent history includes encoder, noise, adaptive, backbone and diagnostic studies, followed by commit `3c4fb20be` on 2026-10-25, **Add frozen vs fine-tuned 32-frame study and findings**.

**VERIFIED:** `git log -- 00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/` assigns the controlled follow-up to full commit `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`. `git rev-parse HEAD`, local `refs/remotes/origin/main`, and a successful live `git ls-remote origin refs/heads/main` all returned that same hash. Thus the study's tracked delivery is committed and present on the remote branch; no commit/push was performed here. Ignored bulk, raw data, caches and weights are not thereby established as remotely archived. Its [GIT_COMMIT_REPORT.md](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/GIT_COMMIT_REPORT.md) describes an earlier prerequisite gate at `29b8ca4bc`, not the later study's own push status.

## Recovery of research direction

**UNKNOWN / UNVERIFIED:** the approved original exposé, direct supervisor feedback and supervisor approval of dataset/scope changes. A current repository filename search and tracked-path inventory located no original proposal or feedback document. The immediate workspace contains this repository and datasets; no broad raw/private-state search was performed. The retained [original_document_search.json](../../runs/thesis/documentation/20260928T025444Z/original_document_search.json) reports a broader earlier unsuccessful search. That historical search is REPORTED, not repeated here. Missing locally does not mean nonexistent elsewhere.

**VERIFIED repository wording:** [Intel research contract](../intel_welding/research_contract.md) defines a process-aware architecture question, Transformer suitability, unimodal/concatenation/late/gated comparisons, missing/degraded modalities, and calibration/interpretability/compute/usability. The [REASSEMBLE contract](../reassemble/RESEARCH_CONTRACT.md) narrows the task to annotated high-level action success/failure. The [prior exposé matrix](../thesis/EXPOSE_TO_FINAL_THESIS_MATRIX.md) explicitly calls its mapping provisional.

| Development | Evidence and assessment |
|---|---|
| PHM lifecycle exploration and image-derived targets | EDA asks about physically meaningful degradation; later target regression is a task-specific development, not validated physical damage ground truth. See E1. |
| Intel modelling stopped | [Gate report](../../artifacts/intel_welding/audits/PHASE_1_GATE_REPORT.md) REPORTED 216 supplied-split session crossings and prior exposure of the proposed holdout. Rejecting a clean-final-test claim is justified; this is not evidence of weak Intel model performance. |
| REASSEMBLE used as main fusion study | Annotated action outcomes and recording grouping make a different empirical task feasible. Semantic change from physical defects/degradation to completed-action failure must be explicit. Supervisor approval remains UNVERIFIED. |
| Statistics replace PatchTST in fusion | Supported for the tested budget by E2; not evidence that all temporal models are inferior. |
| Minimal fusion follows conditional unimodal gates | [Section 1B protocol](../reassemble/SECTION_1B_PROTOCOL.md) explicitly changes the question to incremental fusion benefit without rewriting the old gate. This is a same-cohort exploratory adaptation, not independent confirmation. |
| Architecture/noise/quality/fine-tuning follow-ups | Controlled diagnostics are useful, but repeated observation of the same outer outcomes prevents a fresh final-test interpretation. E7's unequal epoch budget is a confound; E8 addresses it prospectively for 32 frames, without proving a cause. |

No mistake is recast as a planned contribution. In particular, test exposure is an incident/limitation, target-version mismatch is a provenance defect, and an accidentally trivial sorted-profile rank statistic is a corrected metric error.

## Protocol boundaries common to the map

PHM final retained LOEO covers 20 run units across three experiments; its target is provisional image-derived regression. REASSEMBLE's main cohort is 4,530 actions, 509 failures, 148 recordings, with failure positive. A pilot subset is 753 actions, 77 failures, 26 recordings. Average precision is sklearn `average_precision_score`, not trapezoidal PR area.

Core Section 1/1B uses nested model selection and OOF calibration/threshold selection, then outer-training refits. Later encoder/backbone studies use fixed head budgets, a disjoint G fitting/C calibration split, no G+C refit, fixed threshold 0.5, and F2 fitted on inner branch-held-out probabilities. These are different training procedures even when the cohort size is identical. Core F2 AP 0.447299, encoder-reference F2 0.440764 and backbone-reference F2 0.440680 must retain their own protocol labels; their numerical differences are not isolated architecture effects.

Pooled AP differs from mean-fold AP and from mean AP over corruption realizations. Never pool repeated corruptions or seeds as independent subjects. Recording-bootstrap intervals condition on the fitted models; they omit architecture selection, repeated development and most training variability. Recording-disjoint does not by itself prove session-, scene-, object- or operator-disjoint independence.

## E1 — PHM exploratory work and retained target/sensor evaluation

- **Question/data/target:** initial EXP-A Runs 1/3/5 lifecycle exploration, then current-state gear-damage regression over EXP-A 1–5, EXP-B 1–7 and EXP-F 1–8. [Historical notes](../../experiments/exp_a_initial_eda_r1_r3_r5/EXPERIMENT_NOTES.md), representative [basic EDA code](../../experiments/exp_a_initial_eda_r1_r3_r5/basic_eda_phm2026.py), [target decision](../planning/T2_TARGET_FORMULATION_DECISION.md), [version ledger](../thesis/TARGET_VERSION_LEDGER.md).
- **Executed components:** notes REPORTED vibration/context/CI inspection, spectral/gear-mesh features, distributions, PCA and qualitative image review. The basic script explicitly selects the first sorted HDF5 member and uses the first ten seconds for basic statistics: this is illustrative sampling, not full-run evidence. No EDA outputs were regenerated here. The later retained predictor uses engineered sensor inputs with PatchTST or three sensor-submodality encoders; `fused_all_three` does **not** mean image+sensor fusion.
- **Training/evaluation:** [LOEO code](../../scripts/phm2026/results/loeo_evaluation.py) separates held-out experiment, training experiment and validation experiment; preprocessing fits on training only. Larger remaining experiment trains, smaller validates; max 80 epochs, patience 10, batch 4, LR 0.001. Version v3 uses deterministic image views of teeth 5–28, aggregated by mean of the worst three tooth scores. Labels measure an image algorithm's damage candidates, not independently adjudicated physical spall area.
- **VERIFIED results:** from [loeo_predictions.csv](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv), MAE constant **0.804156**, sensor-submodality fusion **0.823786**, single PatchTST **0.941455**, each 20 runs. [Summary JSON](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json) REPORTED fusion-minus-constant interval `[-0.196189,+0.227769]`; its stored +0.017668 point is a bootstrap mean, whereas the direct empirical MAE difference is +0.019629. Image R4 MAE **1.826411** covers 13 runs and is explicitly **not LOEO**.
- **Supported:** operating-state confounding needs control; tested sensor models did not establish improvement over the constant under retained LOEO. **Unsupported:** absence of all sensor signal, a validated physical health scale, tooth identity transfer without registration, a visual+sensor fusion benefit, or direct comparison with REASSEMBLE AP.
- **Threats:** only three experiments; dependent runs within experiments; extensively exposed EXP-F; target and imaging-protocol uncertainty; v1/v2/v3 incompatibility; duplicate warning for EXP-A Run 2 remains REPORTED rather than freshly verified. Sorting a tooth profile discards positional identity. Historical [FUSION_RESULTS](../thesis/FUSION_RESULTS_20260912T111025Z.md) contains stronger prose such as no ranking signal; negative observed correlations do not establish that general claim.

## E2 — REASSEMBLE visual and sensor baselines

- **Question/provenance:** do branches predict native high-level action failure beyond prior/action context? `failure = 1-success`; four action types. Source annotations, not model-created damage targets. [Contract](../reassemble/RESEARCH_CONTRACT.md), [Section 1 config](../../configs/reassemble/section1.json), [report](../../artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md), [model code](../../src/reassemble/section1_models.py), [split code](../../src/reassemble/splits.py).
- **Execution/setup:** frozen RT-DETR CNN maps, spatial/frame means over 16 images, 128-unit learned head; PatchTST from scratch over 512 positions/22 channels; 220 sensor statistics with logistic regression; prior/action controls. Five outer/four inner recording folds; visual budgets 5/10 and PatchTST 3/6 selected using inner AP; branch calibration and thresholds from training-side OOF predictions. Retained report states 19 conditional cyclic-label permutation controls per learned branch.
- **VERIFIED saved-array AP/AUROC:** statistics **0.429392 / 0.779325**; visual **0.230658 / 0.697795**; PatchTST **0.241591 / 0.705351**; action-only **0.180805 / 0.685090**. Recomputed from `runs/reassemble/20260927T154732Z-section1/predictions/{model}_perm00.npz`.
- **Supported:** statistics are the strongest tested sensor representation; visual and PatchTST have incremental AP over action-only as REPORTED paired intervals, but their AUROC contrasts remain unresolved and the original joint gate is conditional. **Unsupported:** all Transformers fail, all failure-relevant visual information is absent, two primary branches passed the original gate, or the input pipeline is a trained RT-DETR detector/temporal video Transformer.
- **Limitations:** bounded budgets (all PatchTST folds chose the maximum six epochs), one collection environment, conditional low-resolution permutation tests, unverified human semantic adjudication, and no independently established audio clock mapping.

## E3 — F2/static fusion and original adaptive gates

- **Question/provenance:** does a second branch add useful information to statistical sensors; do process/quality gates add more? Same REASSEMBLE annotation target. [Section 1B protocol](../reassemble/SECTION_1B_PROTOCOL.md), [config](../../configs/reassemble/section1b.json), [stacking code](../../src/reassemble/section1b.py), [gate code](../../src/reassemble/section2_models.py), [Section 2 results](../../runs/reassemble/20260927T192852Z-section2/assessment/results.json).
- **Executed/setup:** strict nested branch-held-out meta-features; unweighted C=1 logistic probability stacker F2, not convex percentage weights. F1 uniform; F3 embedding concatenation; F4 action, F5 quality and F6 action+quality convex logit gates with masked softmax, calibration and three neural seeds. Outer-test scores never fit F2, but the follow-up design was informed by earlier same-cohort results.
- **VERIFIED saved-array AP:** sensor **0.429392**, visual **0.230658**, F1 **0.445742**, F2 **0.447299**, F3 **0.412231**, F4 **0.443725**, F5 **0.444549**, F6 **0.441356**. F2-minus-sensor empirical AP difference **+0.017907**. [Section 1B JSON](../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json) REPORTED paired interval `[+0.008603,+0.028284]` and AUROC difference +0.015644 `[+0.006030,+0.025465]`.
- **Supported:** incremental static-fusion value on this cohort/procedure. Original gates did not satisfy incremental clean-performance criteria. **Unsupported:** independent confirmation, general adaptive robustness, causal/semantic interpretation of weights, or superiority of every static fusion design. This review did not recompute the historical core intervals or replay fitted networks.
- **Limits:** same-cohort adaptation, task/context shortcuts, constrained gate family, different model capacity/optimization/calibration, and unresolved higher-level dependence. E3's static gain does not isolate complementarity from adding a stacking/calibration stage.

## E4 — frozen CNN versus hybrid encoder

- **Question:** does adding RT-DETR's frozen spatial hybrid encoder improve the representation and F2 under a fixed recipe? [Config](../../00_experiments/rt_detr_encoder_comparison/results/run_01/resolved_config.json), [data/split code](../../00_experiments/rt_detr_encoder_comparison/code/data.py), [fusion code](../../00_experiments/rt_detr_encoder_comparison/code/fusion.py), [report](../../00_experiments/rt_detr_encoder_comparison/results/run_01/comparison/RESULTS_SUMMARY.md).
- **Executed/setup:** same 16 frames, 4,530 actions and five matched outer folds; CNN width 896 versus hybrid width 768, spatial pooling then frame mean. Both extractors frozen; five-epoch heads, G-only scaling/training and C-only sigmoid calibration. Hybrid projections/AIFI/FPN/PAN execution and pixel replays are REPORTED receipts; no detector decoder or temporal attention is claimed. F2 uses valid inner OOF probabilities; sensors identical between arms.
- **VERIFIED keyed CSV results:** CNN visual AP **0.221644**, sensor **0.420926**, F2 **0.440764**; hybrid visual **0.171915**, sensor **0.420926**, F2 **0.424979**. F2 difference **-0.015785**; interval `[-0.024804,-0.005800]` is REPORTED.
- **Supported:** the complete hybrid representation performed worse in this fixed comparison. **Unsupported:** attention itself caused the loss, general Transformer inferiority, robustness differences or matched-capacity efficiency conclusions. Different widths/head parameter counts and compute prevent attention-only attribution. One seed and exposed data limit generalization.

## E5 — selected-pipeline noise robustness

- **Question:** how does a selected fixed clean-trained pipeline respond to raw-input faults? [Run 02 plan](../../00_experiments/fusion_noise_test/results/run_02/experiment_plan.md), [config](../../00_experiments/fusion_noise_test/results/run_02/resolved_config.json), [report](../../00_experiments/fusion_noise_test/results/run_02/comparison/RESULTS_SUMMARY.md), [corruptions](../../00_experiments/fusion_noise_test/code/corruptions.py).
- **Executed/setup:** fold_01 only, 753/77/26. Frozen16 reference selected from eligible observed clean comparisons; incomplete/different-budget variants excluded. Six partial fault families, three severity levels, three repeats for stochastic faults, explicit full-modality fallback; no model/calibrator/threshold refit. Noise scales are training-side; thresholds fixed 0.5. Prior run_01 replay/precision problems are preserved, not treated as new scientific findings.
- **VERIFIED:** hashes for all **51** indexed prediction tables and **151** finite branch AP values; maximum AP discrepancy versus saved metrics `1.11e-16`. Clean fused AP **0.307929**; strong image-noise mean AP **0.284640**; strong sensor-noise mean AP **0.169409**. Means are over separately calculated AP values, not pooled repeated subjects. Sensor-noise drop **0.138520**, interval `[0.070831,0.221115]` REPORTED.
- **Supported:** substantial sensitivity to the named sensor corruption on this pilot. Negative fusion-minus-unchanged-branch point estimates suggest possible harmful fusion, but all four quoted intervals include zero. **Unsupported:** adaptive improvement, robust superiority over discarded encoders, production fault coverage or causal modality importance.
- **Limits:** one exposed fold, clean-score selection, synthetic single-modality faults, three fixed realizations, conditional recording uncertainty and no independent validation. Full absence invokes a policy rather than the original two-input F2 function.

## E6 — augmentation-matched quality-aware pilot

- **Question:** do observable quality and probability×quality interactions improve robustness beyond identical augmentation? [Protocol](../../00_experiments/adaptive_fusion_robustness/results/run_01/PROTOCOL.md), [config](../../00_experiments/adaptive_fusion_robustness/results/run_01/config/resolved_config.json), [quality formulas](../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py), [metric aggregation](../../00_experiments/adaptive_fusion_robustness/code/metrics.py), [data audit](../../00_experiments/adaptive_fusion_robustness/results/run_01/DATA_AUDIT.md), [report](../../00_experiments/adaptive_fusion_robustness/results/run_01/RESULTS_SUMMARY.md).
- **Executed/setup:** one fold selected by a REPORTED training-only runtime rule. Frozen16 visual and statistics branches reused; three new C=1 logistic heads: A static, B additive quality, C quality interactions. Same 3,777 parent OOF actions/11,331 augmented rows, weights 0.5 clean/0.25 image fault/0.25 sensor fault REPORTED. Eight observable proxies; weighted training-only normalization. No fault names, labels or pristine counterparts appear in the inspected predictor design. Complete absence routes identically for every arm.
- **VERIFIED:** 34 table hashes, exact matched keys/labels and 25,602 rows; 196 AP values and 70,029 new-head probabilities reconstructed (max errors `1.11e-16` and `7.77e-16`). Primary equal-weight mean AP: historical F2 **0.255937**, A **0.253996**, B **0.237360**, C **0.257009**. Independently reconstructed 2,000 recording draws give C−A **+0.003012326**, 95% `[-0.026710962,+0.032165450]`. Clean C−A **+0.004771136**; its REPORTED interval `[-0.034258,+0.044544]` does not establish no clean cost. Bootstrap draw SHA256: `952337616b24490835679c3506fac73498115a2f9e3b922275ea9da72bdb59bc`.
- **Supported:** the pilot is inconclusive; retain static F2 as reference. Image-side point gains coexist with sensor-side losses. **Unsupported:** adaptive superiority, clean noninferiority, calibrated trust weights or an architectural novelty claim. The interaction head has direct quality terms and unconstrained coefficients; it is not the same mechanism as F5/F6.
- **Limits:** only 26 assessment recordings; development exposure; quality/content confounding; unequal head capacity; limited fault mixture; incomplete four-fold coverage; native annotation/timing checks are retained reports, not repeated raw-data verification. Human semantic adjudication remains UNVERIFIED.

## E7 — frame count and original fine-tuning comparison

- **Question:** do 16→32 frames or final-CNN-stage adaptation improve completed-action classification/fusion? [Resolved config](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/config/resolved_config.json), [protocol amendment](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/protocol_amendment.md), [source](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/training.py), [report](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/comparison/RESULTS_SUMMARY.md).
- **Executed/setup:** four conditions, same cohort and five outer/four inner splits, fixed sensors, G fitting/C calibration and inner-OOF F2. REPORTED 100 completed visual fits. Frozen heads train **five epochs**, fine-tuned heads/final CNN stage **two**. Inspect `epoch_budgets`, not the legacy top-level `epochs: 5`. No raw-pixel/model replay was run in this review.
- **VERIFIED AP (visual / F2):** frozen16 **0.221644 / 0.440680**; fine-tuned16 **0.224466 / 0.437521**; frozen32 **0.219427 / 0.439584**; fine-tuned32 **0.230609 / 0.438566**. Shared sensor AP **0.420803**. Primary F2 fine-tuned16−frozen16 **-0.003159**; REPORTED interval `[-0.012573,+0.008052]`.
- **Supported:** no demonstrated fusion improvement from these recipes or frame contrasts. **Unsupported:** pure effect of fine-tuning under equal budgets, convergence, optimal frame count or universal frozen superiority. One seed, unequal duration/compute and exposed data remain material limitations; later completion does not retroactively remove them.

## E8 — controlled frozen32 versus fine-tuned32 follow-up

- **Question:** does the apparent visual/fusion discrepancy persist when both recipes receive two epochs, and do saved diagnostics resolve its cause? [Protocol](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/PROTOCOL.md), [config](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/resolved_config.json), [analysis code](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/code/analysis.py), [report](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results/comparison/RESULTS_SUMMARY.md).
- **Executed/setup:** same exact 32 frames/cohort/partitions, two epochs in each arm, seeds 42 and 20261023; five matched outer folds per seed. Sensors fixed across arms/seeds, no sensor refit. REPORTED 75 new and 25 reused visual fits; seed42 fine-tuned fits reused from E7. Equal action/epoch budgets do not imply equal compute or independent replication. Only visual training seed changes; G/C memberships stay fixed.

| Seed | Visual AP frozen → fine-tuned | Uniform AP frozen → fine-tuned | F2 AP frozen → fine-tuned | REPORTED F2 Δ 95% interval |
|---|---|---|---|---|
| 42 | 0.222708 → 0.230609 | 0.444720 → 0.440946 | 0.439363 → 0.438566 | [-0.006424,+0.006072] |
| 20261023 | 0.216799 → 0.200517 | 0.436495 → 0.428489 | 0.435202 → 0.432380 | [-0.008285,+0.003602] |

- **VERIFIED:** all pooled AP above recomputed from 20 identified assessment CSVs; assessment hashes matched receipts; exact uniform/F2 arithmetic error 0 with round-trip parsing; sensor probabilities bit-identical across arms/seeds. Independently inspected 25 fit jobs: G/C/prediction recordings disjoint, outer training/assessment recordings disjoint, and outer coverage exactly 4,530 unique rows. This does not prove different recordings are independent sessions.
- **Supported:** no reliable fusion improvement under this controlled recipe; visual point effects change sign by seed. **Unsupported:** a uniquely identified cause, seed-population uncertainty from two seeds, equivalence, or that better images can never help fusion. OOF branch rows are F2 training inputs, not independent F2 validation.
- **Additional operating-point limitation VERIFIED:** frozen visual recall at 0.5 is zero for both seeds; fine-tuned visual recalls are 4/509 and 3/509. Nontrivial AP does not imply useful operational recall at that fixed threshold. No threshold was changed here.
- **Conclusion:** retain **CAUSE_NOT_RESOLVED**. Calibration, complementarity and OOF transfer patterns remain candidate explanations, not causal findings. Historical pixel/gradient/replay checks are REPORTED receipts, not new checks in this review.

## What this review independently checked

Python commands used `ma_thesis_env/bin/python -B` with one-thread numerical settings, importing NumPy/pandas/scipy/sklearn only; no project module with side effects was executed. Recorded versions: Python 3.12.3, NumPy 2.4.6, pandas 2.3.3, SciPy 1.18.0, scikit-learn 1.7.2. Inline code read derived CSV/NPZ/JSON files, recomputed AP/MAE, reconstructed logistic probabilities, checked indexed SHA256 and compared manifest group sets. Bootstrap recreation used seed 314159, multinomial recording multiplicities, exact weighted AP including ties, equal condition weighting and percentile 2.5/97.5 bounds. No existing recalculation script was invoked because several write into historical output directories.

| Check | Result and boundary |
|---|---|
| PHM | Four retained MAEs reproduced; no target remeasurement or training reproduction |
| Core REASSEMBLE | Four unimodal AP/AUROC pairs and eight fusion APs reproduced; historical core intervals not rerun |
| Encoder/backbone | Keyed pooled branch AP reproduced; encoder sensor identity checked; no extractor/model replay |
| Noise | 51 indexed hashes and 151 finite APs checked; endpoint realization means reproduced |
| Quality pilot | 34 hashes, coverage, 196 APs, 70,029 probability reconstructions, shared absence fallback and primary 2,000-draw interval checked |
| Controlled32 | 20 assessment hashes, pooled metrics, arithmetic, sensor parity and 25 job split memberships checked |

No discrepancy requiring a change to stored scores was found in these checks. This does not establish absence of implementation errors outside the checked paths. Source-level guards do not independently prove that every historical fit used the declared inputs/code. Raw-label correctness, full training reproduction, complete higher-level grouping, and final human adjudication remain **UNVERIFIED**.

### Compact provenance identities

The following selected derived inputs were hashed in this review; no raw archives were hashed.

| Repository-relative input | SHA256 |
|---|---|
| `docs/intel_welding/research_contract.md` | `5dbfeb81585d91ecef9d1b7f9d4087126172674a71fb295b601d044308f3022b` |
| `runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv` | `b455864466c0aed759756c674d373d30c9f70905cdbb55e7c00ab53b565b72f4` |
| `runs/reassemble/20260927T192852Z-section2/predictions/oof.npz` | `e2ca736b2dccdb33a1dfc0cf33c2001a3b69cdb2d8ef82d5241c4f34b740995a` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/comparison/coverage_and_prediction_index.csv` | `6e145c452b1622eee36f7b5dda94f927722ea29708ba7b0ba805f824583f9e4f` |
| `00_experiments/adaptive_fusion_robustness/results/run_01/fusion_fits/fold_01/components.json` | `40fa849f9056d6bda21b18ca96c7bec4df02f9e5e5329f8feaf2316fbaa93652` |
| `00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/data_manifests/fit_partitions.json` | `d4c944874f7e24ee7f2107ae70d108a9e2116eec41ea519017e54e9bec805500` |

Review timestamp recorded during input identification: 2026-10-25T19:42:44.523505+00:00. This is a documentation review with numerical checks, not a new model experiment. The exact analysis commands and output are retained in the associated conversation tool transcript; compact reproduction examples follow.

```python
# Read-only examples, run from the repository root with the repository Python.
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

p = Path('runs/reassemble/20260927T192852Z-section2/predictions/oof.npz')
with np.load(p, allow_pickle=False) as z:
    print({m: average_precision_score(z['y'], z[m + '_p'])
           for m in ['U1', 'U2', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6']})

p = Path('00_experiments/adaptive_fusion_robustness/results/run_01')
index = pd.read_csv(p / 'comparison/coverage_and_prediction_index.csv')
scores = []
for row in index.to_dict('records'):
    if row['family'] not in ['image_noise', 'sensor_noise']:
        continue
    t = pd.read_csv(p / row['path'], float_precision='round_trip')
    scores.append(average_precision_score(t.failure, t.p_quality_interaction)
                  - average_precision_score(t.failure, t.p_static_augmented))
print(np.mean(scores))  # equal weighting valid for this balanced one-fold grid
```

Environment metadata consistency passed (`pip check`); that is not runtime or scientific validation. The repository test suite was not run for this documentation-only change. New-document links and whitespace are checked separately at handoff.
<!-- TASK2_SNAPSHOT_END -->

</details>
