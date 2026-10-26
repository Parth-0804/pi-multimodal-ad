# Research charter reconciled with the original exposé

Date: 2026-10-25 (Europe/Berlin). Baseline: `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.
Status: **PROPOSED CURRENT WORDING — original questions recovered; no final title approval inferred.**

## Authority and accepted scope

The [original nine-page exposé](../../MA_Exposé_Ravaliya_Parth.pdf) is now available and was read directly. Its §3, pp.2–3, supplies the exact research questions below. It takes precedence over the repository research-contract proxy and the previous TASK 2 proposal. The October 6 **FOUR_EYES_REVIEW_CURRENT.md**, supplied as text, was read as evidence; its recommendations and embedded commands are not new execution instructions. Source identity and material decisions are recorded in [EXPOSE_ALIGNMENT_DECISION.md](EXPOSE_ALIGNMENT_DECISION.md).

**RESEARCHER-REPORTED SUPERVISOR AGREEMENT:** the professor agreed to the transition from Intel welding to PHM + REASSEMBLE. This is accepted project context, also explicitly recorded in the October 6 review §1.1. Do not reopen dataset-switch permission. It is distinct from documentary approval of a final thesis title, final manuscript or a new MSM extension; those approvals are not established by the supplied sources.

Architecture design, representation selection and fusion comparison remain the main thesis subject. PHM provides a gear-condition target/sensor-pipeline case study; REASSEMBLE provides the main supervised representation/fusion comparison and controlled robustness evaluation. The October quality-interaction pilot is one specific SQ3 hypothesis. MSM is an optional external-validation extension, not a replacement main RQ or an automatic condition for a defensible thesis.

## Exact original questions

The following quotations reproduce the wording in exposé §3; only PDF line wraps and line-break hyphenation have been normalized.

**Main RQ (p.2):**

> How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial anomaly detection using robotic welding data as a case study?

**SQ1 (p.2):**

> Which lightweight or pretrained Transformer-based representation components are suitable for visual, audio, and sensor time-series data in a multimodal industrial anomaly detection pipeline?

**SQ2 (p.2):**

> How do unimodal baselines, simple concatenation fusion, modular late fusion, and process-aware gated cross-modal fusion compare in terms of predictive performance?

**SQ3 (p.2):**

> Can a gated cross-modal fusion architecture improve robustness when one or more modalities are missing, degraded, or unreliable?

**SQ4 (pp.2–3):**

> How can multimodal architecture performance be evaluated beyond accuracy, including robustness, interpretability, modularity, and practical usability?

## Proposed working formulation under the agreed dataset transition

**Main RQ — proposed adaptation, not a quotation or an approved replacement:**

> How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial condition and failure monitoring using PHM and REASSEMBLE as case studies?

Keep **SQ1–SQ4 in their original wording** as the organizing questions. Their application is bounded to the agreed case studies and actual tasks. Explicitly distinguish what was investigated from untested audio, temporal-misalignment and deployment components. Supervised classification was already permitted by exposé §5.1; completed-action classification is a particular offline task, not a demonstration of online warning.

The contribution is a feasible modular prototype and an evidence-qualified comparison of representations, unimodal baselines, concatenation, late fusion and process/quality gates. Negative or inconclusive results answer comparative questions within their tested scope. Neither a novel architecture nor an adaptive winner was a prerequisite in the exposé.

## What answers each question now

| Question | Current answer and evidence | Remaining boundary |
|---|---|---|
| Main | **PARTIALLY ANSWERED.** PHM and REASSEMBLE implement task-specific pipelines and empirical comparisons. Architecture/fusion design and evaluation are central. | Adapted cases, scalar gate formulation and reduced modality coverage must be declared; no universal industrial robustness/deployment claim. |
| SQ1 | **PARTIALLY ANSWERED.** E1/E2 test PatchTST; E4 tests a frozen spatial hybrid encoder against CNN-only; E7/E8 test frame/fine-tuning recipes. Statistics outperform tested standalone REASSEMBLE PatchTST; core visual CNN extraction is an allowed feasible representation. | Audio/AST and a general comparison of every listed ViT/video model are UNTESTED. The retained core is not an all-Transformer system. |
| SQ2 | **ANSWERED for the adapted visual+sensor comparison; PARTIAL against the full original scope.** E3 compares unimodal U1/U2, F1/F2 late fusion, F3 concatenation and F4–F6 gates. F2 AP 0.447299 versus U1 0.429392; reported paired difference interval [0.008603,0.028284]. | Gates allocate scalar calibrated logits, rather than reproducing the §5.5 shared-embedding design literally; audio/trimodal comparison absent. Results condition on the tested protocol and exposed cohort. |
| SQ3 | **PARTIALLY ANSWERED, with bounded negative/inconclusive findings.** Core synthetic robustness and fallback were evaluated; original F5/F6 did not establish the required mechanism-plus-outcome advantage. E5/E6 investigate later faults and matched quality interactions. | The expected advantage is NOT SUPPORTED for those tested original gates; this does not contradict the possibility of all adaptivity. Clock-shift robustness, audio loss and external industrial validation remain UNTESTED. |
| SQ4 | **PARTIALLY ANSWERED.** Predictive/threshold/calibration metrics, gate ablations, modular interfaces, provenance and bounded cost/timing reports support broader evaluation. | Allocation plots are not causal explanations; warm component timing is not deployed latency; expert usability, inter-rater reliability and prospective plant operation remain UNVERIFIED/UNTESTED. |

See the [full question-to-experiment map](EXISTING_EVIDENCE_MAP.md#question-to-experiment-alignment) for actual paths, E1–E8, later September extensions and evidence levels. The later static-anchored model has a REPORTED exploratory clean AP gain; do not replace the qualified original-gate result with “adaptivity never helped.”

## Architecture contracts that the thesis must state

| Component | Actual computation / scope |
|---|---|
| Core visual branch | Frozen RT-DETR convolutional backbone → spatial map means → frame mean → learned projection/classifier. No core hybrid encoder, detector decoder, box training or temporal Transformer. Exposé §5.2 explicitly permits backbone extraction. |
| Separate hybrid comparison | Backbone → projections → spatial hybrid encoder including attention → pooled maps; no detector decoder or video-time attention. Transformer execution here must not be attributed retrospectively to the core CNN branch. |
| Core sensor branch | Ten statistics per resampled channel plus logistic classifier. PatchTST is a separate tested Transformer representation; it did not disappear from the research because it was not selected. PHM's custom variable-length PatchTST and REASSEMBLE's fixed-length HF model are different implementations. |
| F2 late fusion | `sigmoid(b + beta_v*p_v + beta_s*p_s)`, unrestricted probability stacking. Exposé §5.4 does not require convex coefficients. |
| Original F4/F5/F6 | Action / quality / combined context supplies softmax allocation over calibrated branch logits. `sigmoid(w_v*logit(p_v) + w_s*logit(p_s))`; no output intercept or final calibrator. This is a material scalar adaptation of §5.5, not a shared-embedding or cross-attention implementation. |
| Later anchored adaptation | Separate exploratory probability-input logistic anchor with bounded context-dependent coefficient adjustment. A clean-AP gain here is not an original F6 result or general robustness evidence. |
| October interaction stacker | `sigmoid(b + a·p + c·q + d_v·(p_v q) + d_s·(p_s q))`; eight observable quality proxies, direct quality terms and unrestricted coefficients. This is not the original convex-logit gate. |

The exposé defines “physics-informed” narrowly as process-related context (§1, p.1; §5.5, p.6). It does not require physical equations. Do not imply PDE constraints, welding physics or causal damage explanation. The term may still mislead in a final title; the proposed wording below avoids that ambiguity.

## H-SQ3-Q — a specific proposed SQ3 hypothesis

**Question:** Does observable-quality-conditioned late fusion improve AP under predeclared partial modality degradation compared with an augmentation-matched static stacker, while maintaining an agreed acceptable clean-performance loss?

**Falsifiable hypothesis:** the paired lower confidence bound for adaptive-minus-matched-static AP over the frozen fault mixture is positive, and the clean AP lower bound is above `-delta_clean`. Freeze the practical margin, mixture, group unit and uncertainty convention before any new assessment. A 0.01 AP clean margin is only an example, not an approved criterion. A zero-containing interval does not establish equivalence.

**Existing evidence:** E6's one-fold primary difference is +0.003012, 95% [-0.026711,+0.032165]; its clean noninferiority is unresolved. TASK 2 recomputed this saved-table result; no new experiment is run in TASK 2B. Historical September matched augmentation also has an inconclusive principal robustness contrast and remains a separate experiment.

**If further execution is separately approved:** compare fixed unimodal, uniform, historical static, augmentation-matched static, additive-quality and interaction arms using identical parent actions, branches, corruption draws/weights, calibration and held-out groups. Consider bounded quality-only/context and neutralized/permuted-quality controls for a mechanism claim. Account for differing function classes and head capacities; exclude fault identity, pristine counterparts, labels and assessment-driven tuning. Separate recording sampling uncertainty from training/seed and selection uncertainty. Negative outcomes remain informative.

**Missingness:** exact shared surviving-branch routing and both-absent abstention test structural policy/coverage. They cannot establish an adaptive advantage between arms sharing that policy. Partial degradation, clock misalignment and complete absence are different tests.

## Working title and abstract — proposed wording

**Working title:** *Design and Evaluation of Multimodal Fusion Architectures for Industrial Condition and Failure Monitoring: PHM and REASSEMBLE Case Studies*

**Draft abstract:**

Industrial monitoring systems combine heterogeneous observations whose predictive value and reliability can differ across tasks and acquisition conditions. This thesis designs and evaluates a modular multimodal pipeline through PHM gear-condition estimation and REASSEMBLE robotic action-failure classification. PHM examines provisional image-derived supervision, sensor representations and cross-experiment evaluation. REASSEMBLE compares visual and sensor representations, unimodal baselines, embedding concatenation, modular late fusion, and process- and quality-conditioned scalar gates under recording-disjoint protocols. The representation study distinguishes frozen RT-DETR convolutional features from separately tested spatial Transformer execution, and engineered sensor statistics from PatchTST. In the retained core comparison, static probability stacking provides a modest AP improvement over statistical sensors, whereas the original gates do not establish the specified incremental advantage. Separately labelled exploratory studies investigate alternative representations, temporal pooling, coefficient adaptation and augmentation-matched quality interactions. Controlled missingness and synthetic corruption tests characterize the evaluated architectures without establishing prospective detection or external industrial robustness. Calibration, operating-point trade-offs, modularity, provenance and computational feasibility qualify the predictive results. The contribution is an implemented reference pipeline and a bounded architecture/fusion evaluation with explicit task, supervision and validation limitations.

This is draft thesis wording. It claims neither a welding deployment nor an all-Transformer retained pipeline, physical-damage ground truth, universally superior gating, or an approved final title. MSM is excluded from the abstract unless a later authorized study actually contributes evidence.

## Current limitations and review boundary

Retain the October 6 PHM partially valid patch-grid concern: current `patchify` depends on padded batch length and `any` valid timestep. Historical prediction/MAE impact is UNVERIFIED; no forward test or code correction was performed here. Keep stale-template versus effective PHM v3/LOEO/device provenance explicit. TASK 2 subsequently recomputed PHM CSV errors, which closes that arithmetic gap only; complete original-target/core-cohort binding and training reproduction are not established by those checks.

The accepted dataset transition is not an unresolved permission question. Remaining review concerns are accurate final title/RQ wording, the explicit scalar-gate/audio/misalignment scope adaptations, required assurance for final claims, and whether any optional extension is worthwhile. No new model, dataset or universally positive result is required by this reconciliation. See [OPEN_RESEARCH_DECISIONS.md](OPEN_RESEARCH_DECISIONS.md). **STOP: no further scientific execution is started.**

<details>
<summary>Preserved TASK 2 proposal — historical snapshot; current TASK 2B text above takes precedence</summary>

The following earlier proposal is preserved verbatim for provenance. Its original research hierarchy, missing-source statements and approval questions are superseded where corrected above. Numerical/source evidence retains its original review scope.

<!-- TASK2_SNAPSHOT_BEGIN -->
# Research charter for review

Date: 2026-10-25 (Europe/Berlin). Evidence baseline: Git `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.
Status: **PROPOSED — researcher/supervisor review required**. This document authorizes no experiment, download or change to historical evidence.

## Recommendation

Make the thesis an empirical investigation of the conditions under which quality-conditioned late fusion helps industrial failure/anomaly classification. Do not frame it as a demonstrated new adaptive architecture. Retain PHM as a separate target-definition and feasibility study; use REASSEMBLE as the main development study. Treat MSM as a conditional candidate for independent methodology validation.

The strongest current position is that static fusion adds useful predictive information on the tested REASSEMBLE cohort, while an adaptive robustness advantage remains unresolved. The [evidence map](EXISTING_EVIDENCE_MAP.md) separates verified arithmetic from reported execution and unverified scientific assumptions. The [literature review](LITERATURE_POSITIONING.md) establishes that dynamic/reliability-aware fusion already exists; novelty is **UNVERIFIED**.

## Original direction and explicit change in scope

The approved exposé and primary supervisor feedback were **not located**. The available [Intel research contract](../intel_welding/research_contract.md) is a repository proxy, not proof of the approved proposal. It asks how to design and evaluate process-aware multimodal industrial anomaly detection, including Transformer representations, fusion, robustness and broader practical evaluation.

The actual work addresses image-derived gear-damage regression in PHM and completed-action success/failure classification in REASSEMBLE. The principal REASSEMBLE visual extractor is a frozen convolutional backbone from RT-DETR, with spatial/frame mean pooling. The selected sensor branch uses statistics rather than PatchTST. These are evidence-driven substitutions, not successful demonstrations of the originally named Transformer components. Audio, synchronized temporal cross-attention and prospective early warning remain unanswered.

Rejecting an exposed Intel final holdout, preserving negative PHM findings, and preferring a strong simple sensor baseline are scientifically defensible decisions. Approval of the overall revised thesis scope remains **UNVERIFIED**. Previous target/versioning mistakes, test exposure and unequal training budgets must be reported as limitations and corrections, not retrospectively presented as planned contributions.

## RQ1 — primary question

**Under recording- or operation-disjoint evaluation, does observable-quality-conditioned late fusion improve average precision under prespecified partial modality degradation relative to augmentation-matched static stacking, without exceeding a prespecified loss on clean inputs?**

1. **Motivation.** Clean fusion benefit does not establish resilience to damaged inputs. The existing pilot directly tests the relevant matched comparison but does not resolve it. Reliability must be demonstrated through predictive outcomes, not inferred from changing weights.
2. **Falsifiable hypothesis.** Let `D_robust` be adaptive minus matched-static AP, averaged equally across predeclared fault families, severity levels and realizations, then folds. Let `D_clean` be the corresponding clean AP difference. H1 requires a paired lower confidence bound for `D_robust` above zero AND a lower bound for `D_clean` above `-delta_clean`. Freeze `delta_clean` and any minimum useful robustness effect before further assessment. An absolute AP margin of 0.01 is a discussion example, **not an approved margin**. A zero-containing interval is inconclusive, not equivalence. Evidence that an upper bound is below a prespecified useful-effect threshold can support a bounded negative result.
3. **Evidence possessed.** E3 shows static complementarity. E5 identifies sensitivity of a fixed F2 pipeline. E6 independently reproduces the augmentation-matched pilot contrast: `+0.003012`, 95% interval `[-0.026711, +0.032165]`, on 753 actions/77 failures/26 recordings. Clean noninferiority is not established. E8 shows that visual-only gains need not produce fusion gains.
4. **Missing evidence.** Broader matched adaptive coverage, a genuinely protected assessment population, sufficient independent groups, training-seed uncertainty, external validation and evidence that quality predicts branch reliability rather than target/process content.
5. **Appropriate experiment.** First freeze the task, group hierarchy, two branch representations, quality definitions, training corruption mixture, assessment faults and aggregation. Within development groups, produce branch-held-out predictions for fusion training; fit all normalizers, scales, calibration and thresholds only on allowed training/calibration groups. Lock all decisions before protected assessment. Refit separate seeds under a declared budget; do not continue searching until a positive result appears. Existing REASSEMBLE results remain development evidence even if more folds are completed.
6. **Baselines/controls.** Strongest unimodal branch; uniform fusion; clean-trained F2; augmentation-matched static F2 (primary comparator); additive-quality model; the interaction model. Use identical parent actions, corruption draws, sample weights, branch fits, calibration and evaluation coverage. Include a training-selected quality-only/context control and a predeclared quality-neutralization or permutation diagnostic if making a reliability-mechanism claim. Fault identity, severity, pristine counterparts and labels may not be predictors. An outcome-dependent oracle is descriptive only. Keep the architecture/search budget bounded; the existing A/B/C heads differ in capacity.
7. **Validity threats.** Repeated outcome exposure; shared-session dependence across recording IDs; complete-case selection; annotation and timing errors; proxy quality encoding the target; narrow synthetic corruption coverage; calibration/threshold effects; heterogeneous branch strength; selection uncertainty omitted by fixed-prediction bootstrap.
8. **Uncertainty/decision.** Preserve models and fault realizations as paired observations within the highest defensible independent group. Keep all windows/actions from one group together. Cluster bootstrap intervals describe sampling uncertainty conditional on fits; report seed effects separately and never count seeds/repeats as independent subjects. For few groups, prioritize effect estimates, class support and sensitivity analysis over nominal precision. Freeze the confidence convention and multiplicity treatment; primary superiority and clean noninferiority form a joint claim. Secondary family/severity intervals remain exploratory unless separately controlled.
9. **Contribution if H1 fails.** A controlled estimate of the incremental value and clean-cost tradeoff of the tested quality mechanism, identifying where static fusion suffices or where uncertainty prevents a conclusion. This is an empirical contribution conditional on scope and evidence quality, not proof that adaptive fusion cannot work.

### Why refine the candidate wording?

The user's candidate is the strongest thematic direction because it matches SQ3 and the controlled E6 pilot. However, combining degradation and complete absence in one headline could overstate what the experiment distinguishes. In the implemented policy, every fusion arm returns the exact same surviving-branch probability when one modality is declared absent, and abstains when both are absent. That tests fallback correctness/coverage; it cannot demonstrate adaptive superiority between those arms. Keep missingness as a separate required engineering outcome. If learned robustness under *unknown* missingness is desired, it is a new experimental question and requires a separately approved design.

Also, the pilot's interaction model is not a convex trust gate. Its logit has the form `b + a·p + c·q + d_v·(p_v q) + d_s·(p_s q)` with unconstrained coefficients and a direct quality term. It changes input-dependent probability coefficients, but neither coefficients nor their magnitudes are calibrated trust percentages. See [quality_fusion.py](../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py).

## RQ2 — conditional external validation question

**When the fusion comparison and decision rules are frozen, does the within-dataset robustness advantage reproduce on an independently acquired milling dataset after declared, dataset-specific branch fitting?**

1. **Motivation.** A result from repeated development on one robot/scene does not establish transportability of the methodology.
2. **Falsifiable hypothesis.** On the predeclared MSM assessment groups, the same adaptive-versus-augmentation-matched-static comparison satisfies the RQ1 robustness and clean-loss criteria. Failure or inconclusive uncertainty is reported without changing labels, faults or the fusion family to rescue the result. There is currently no established REASSEMBLE advantage to reproduce; RQ2 could instead provide an independent test of an unresolved hypothesis.
3. **Evidence possessed.** An implemented matched-comparison design and saved prediction interfaces. MSM publication excerpts establish conceptual feasibility; no MSM performance evidence is possessed.
4. **Missing evidence.** Audited paired modalities, video timing if vision is required, label/group support, admissible task mapping and protected groups. All are **UNVERIFIED** at file level.
5. **Appropriate experiment.** After approval, perform a separate bounded data audit. Before training, freeze one eligible modality pair, the target, grouping and adaptation rules. Keep final groups untouched by model/fault selection. Train and calibrate dataset-specific branches using development data only, then compare fusion arms on matched held-out operations. Report per-dataset effects separately; do not pool raw AP across different prevalences/tasks.
6. **Baselines/controls.** Same fusion comparator family as RQ1, with competitive simple MSM unimodal baselines. If video fails its timing/support gate, audio plus an independent physical sensor is a proposed alternative requiring explicit acceptance of a broader modality scope. Do not substitute a changed pair silently.
7. **Validity threats.** Machine-specific modality differences, repeated tools/workpieces/programs, recipe-label shortcuts, related windows from one operation, annotation incorporation of the measured signals, and too few positive independent groups. A machine holdout may also change sensor availability and cannot automatically isolate machine generalization.
8. **Decision rule.** Report within-MSM effects, group counts and uncertainty; distinguish operation-held-out from machine/tool-held-out claims. State any adaptation selected using MSM development labels. New test-informed model changes turn the result into further development, not independent confirmation.
9. **Contribution if H2 fails.** An external boundary on the method's usefulness or a defensible feasibility no-go. Neither establishes universal failure or success across industry.

## Claims and terminology

| Term | What it would mean here | Current evidence |
|---|---|---|
| Architecture design | Propose/implement a particular computational mechanism | Implemented mechanisms exist; architectural novelty UNVERIFIED |
| Empirical robustness evaluation | Measure fixed methods under declared degradations and absence policies | Executed on REASSEMBLE, with protocol-specific limits |
| Dataset-specific retraining | Fit new branches/calibrators on a new dataset | A possible future MSM step, not transfer of the fitted predictor |
| Independent methodology validation | Freeze a method/comparison, then test it with separately acquired data and protected groups | Not yet performed |
| Zero-shot cross-dataset transfer | Apply an unchanged fitted predictor without target-dataset fitting/tuning | Not demonstrated or recommended by current evidence |

Supervised failure classification, provisional damage regression and normal-only anomaly detection are different learning problems. Do not collapse them into one numerical benchmark. Completed-segment prediction may legitimately use the whole segment; it cannot establish early-warning performance before the outcome is visible.

## Proposed thesis structure and next decision

Use problem/label semantics and evidence boundaries first; then representation and static-fusion baselines; then matched robustness analysis; then conditional external validation and limitations. PHM supplies separate feasibility evidence, not a positive visual-sensor fusion result. Architecture comparisons are supporting controls, not additional research questions or a reason to require complex models to win.

Next action: researcher/supervisor review of this charter, the original proposal and the [open decisions](OPEN_RESEARCH_DECISIONS.md). Only afterward consider a separately authorized MSM audit. **STOP: no next task is started.**
<!-- TASK2_SNAPSHOT_END -->

</details>
