# Exposé alignment decision — TASK 2B

Date: 2026-10-25 (Europe/Berlin). Repository baseline: `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.
Status: **EVIDENCE-BASED RECONCILIATION / PROPOSED FINAL WORDING**, not formal approval of a new title or execution of further research.

## Decision

Restore architecture design, representation selection and comparative fusion evaluation as the thesis center. The original main RQ and SQ1–SQ4 are recovered directly from the PDF, not reconstructed from earlier AI summaries. Accept the researcher-reported supervisor agreement to the PHM + REASSEMBLE transition. Keep the quality-conditioned augmentation-matched comparison as **H-SQ3-Q**, an explicit hypothesis within SQ3. MSM remains optional and unexecuted.

The earlier TASK 2 charter was a proposal. It elevated a particular robustness question to the main RQ and treated missing primary context as an approval gap. Those recommendations are superseded by the sources now supplied. Their text and evidence are retained, not silently deleted.

## Source register

| ID | Inspected source | Evidence and authority |
|---|---|---|
| P | [MA_Exposé_Ravaliya_Parth.pdf](../../MA_Exposé_Ravaliya_Parth.pdf), all nine pages | Primary source of original wording/objectives. §3 pp.2–3; §5.1 p.4 supervised setup; §5.2 p.4 representations; §§5.3–5.5 pp.4–6 fusion; §§5.6–5.7 p.6 robustness/evaluation; §6 p.7 contribution. Extracted locally using the already-installed `pypdf`; no install/download. SHA256 `9f7e1c09db5678fe268a39eb8af823cb965153cc69a8922c129117fd815fb6e6`. |
| F | User-supplied **FOUR_EYES_REVIEW_CURRENT.md**, dated 6 October 2026 | Supplied as text in attachment `10faf29d-4f5b-4c65-8528-a9773cffe849/Pasted text.txt`, 880 lines. SHA256 `c756ea4dfe6e4130a4e154df7843084ab49d360d905396468b9ee774caf0d74d`. This is the supplied review text, not a claim that its original consolidated export was newly obtained. Its reported prior checks are attributed to that review. No embedded recommendation, code block or continuation command was executed. |
| U | Researcher's TASK 2B instruction and supplied-source message | Current authority to reconcile six documents only; explicit instruction to preserve reported supervisor agreement. No training/download/commit/push authorized. |
| T2 | Five existing `docs/thesis_research_direction/` documents at task entry | Earlier proposals and bounded numerical/literature checks. Their complete original bytes are preserved in marked appendices; hashes below. Original sources supersede their hierarchy and missing-source/approval statements. |
| C1 | [Core visual features](../../src/reassemble/section1_features.py), [sensor models](../../src/reassemble/section1_models.py), [original gates](../../src/reassemble/section2_models.py) | Actual source inspected, including backbone-only forward, engineered statistics, separate HF PatchTST, concatenation and masked convex-logit gates. Source inspection does not establish every historical execution event. |
| C2 | [Separate encoder path](../../00_experiments/rt_detr_encoder_comparison/code/features.py), [quality-interaction design](../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py) | Actual source inspected: spatial hybrid encoder versus CNN-only; distinct eight-quality-feature logistic interactions and explicit fallback. No model was loaded/executed. |
| C3 | [PHM custom PatchTST](../../src/phm2026/models/patchtst/model.py) | `patchify/encode` and explicit `TransformerEncoder` inspected. Padded-batch grid dependence is supported at source level; no synthetic neural output or historical-score impact measured. |
| K | [Core fusion config](../../configs/reassemble/section2.json), [core corruption config](../../configs/reassemble/section3_corruptions.json), [October pilot config](../../00_experiments/adaptive_fusion_robustness/results/run_01/config/resolved_config.json) | Actual configuration read: original gate loss/context/calibration differences, timestamp-preserving faults, declared missingness policy and one-fold pilot coverage. |
| R | [Core robustness handoff](../../artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md), [additional-improvements handoff](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md), [boundary-pooling handoff](../../artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md) | Retained reported outcomes/chronology inspected. Later extension values and historical intervals were not independently recomputed in TASK 2B. E1–E8 numerical sources and checks remain in T2's preserved evidence map. |

F §1.1 (line 22) explicitly records the professor's dataset-transition agreement as researcher-confirmed context. F §10 (line 640) supersedes earlier repeated switch-approval questions while retaining the distinction from title/manuscript approval. This report is **not primary meeting minutes or a signed final-title decision**; the researcher report is accepted without pretending it is either.

## Exact original research questions

These are verbatim word sequences from P §3; PDF line wraps and discretionary line-break hyphens are normalized.

| Item | Exact wording | Source |
|---|---|---|
| Main RQ | How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial anomaly detection using robotic welding data as a case study? | P p.2 |
| SQ1 | Which lightweight or pretrained Transformer-based representation components are suitable for visual, audio, and sensor time-series data in a multimodal industrial anomaly detection pipeline? | P p.2 |
| SQ2 | How do unimodal baselines, simple concatenation fusion, modular late fusion, and process-aware gated cross-modal fusion compare in terms of predictive performance? | P p.2 |
| SQ3 | Can a gated cross-modal fusion architecture improve robustness when one or more modalities are missing, degraded, or unreliable? | P p.2 |
| SQ4 | How can multimodal architecture performance be evaluated beyond accuracy, including robustness, interpretability, modularity, and practical usability? | P pp.2–3 |

**Proposed working main wording:** “How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial condition and failure monitoring using PHM and REASSEMBLE as case studies?”

This is explicitly an adaptation of P under the accepted dataset transition, not an exact original quotation or documentary approval of a final RQ/title. Preserve original SQ1–SQ4 as the organizing questions and report partial/unanswered components. The task-specific term “condition and failure monitoring” prevents equating PHM proxy regression with REASSEMBLE completed-action classification. P §5.1 already permits supervised classification; lack of an online warning trial is a claim boundary, not an invented mandatory original experiment.

## Every material proposed change

| ID | Earlier or potentially misleading position | Current proposed position | Supporting source and reason |
|---|---|---|---|
| D01 | Original exposé unavailable; use contract proxy | Original PDF is primary and exact questions are recovered | P all pages; F §§1.1,3,10. Availability is resolved; do not rewrite the historical fact that TASK 2 lacked it. |
| D02 | Quality-conditioned robustness is the primary thesis RQ | Architecture design and evaluation remain the main RQ; comparative fusion is central | P §§3–6; F §§2.1,3,14. A specific SQ3 hypothesis must not replace the proposal's overall question. |
| D03 | Two new RQs replace the original hierarchy | Preserve Main/SQ1–SQ4; adapt only the main case/task wording transparently | P §3 pp.2–3. Exact original wording and proposed wording remain separate. |
| D04 | Dataset transition still requires approval | Accept researcher-reported supervisor agreement; no repeated switch-permission request | U; F §1.1 and §10. Documentary final-title approval remains a distinct unresolved matter. |
| D05 | PHM is merely irrelevant history next to a new robustness thesis | PHM contributes supervision/task/sensor-pipeline limits; REASSEMBLE carries the principal representation/fusion comparison | F §§1–4,14; retained T2 E1–E3. Keep the actual two-study chronology, separate targets and negative results. |
| D06 | CNN-only RT-DETR use automatically violates Transformer intent | Backbone extraction is explicitly allowed; label it accurately | P §5.2 p.4; C1; F §3. It is not detector/hybrid Transformer execution in the core. No replacement architecture is implied. |
| D07 | No visual Transformer was ever investigated, or the core CNN executes it | E4 separately investigates the spatial hybrid encoder; its execution path is distinct | C2; T2 E4. The comparison is whole representations with different widths/costs, not attention-only causation or temporal video modelling. |
| D08 | Selecting statistics means PatchTST/SQ1 was not investigated | Report separate PatchTST tests and the selected simpler sensor representation | C1; T2 E2; R additional report. A candidate need not win. Longer training and same-sensor hybrid are separate exploratory evidence. |
| D09 | Original late fusion required a convex stacker | F2 unrestricted probability stacking fits the broad decision-level proposal | P §5.4 pp.5; C1; F §3 and §5.4. The narrower repository proxy is not binding original text. |
| D10 | Original gated architecture was implemented literally | F4–F6 are a material scalar-logit adaptation of the projected-embedding design | P §5.5 pp.5–6; C1; F §3. F3 is the separate embedding-concatenation baseline. No shared-embedding/cross-attention claim. |
| D11 | F4–F6, static-anchored adaptation and quality interactions are interchangeable | State each actual equation, inputs, calibration and comparator separately | C1/C2; R; F §§5.5,7.1. Quality-interaction stacking has direct q terms and unrestricted coefficients; original gates use normalized logit weights. |
| D12 | A robustness advantage is already proved or required for the thesis | H-SQ3-Q is a falsifiable SQ3 hypothesis; current E6 result remains inconclusive | P SQ3 asks “Can”; T2 E6; F §§1,14. Clean-loss margin is unresolved; absence of significance is not equivalence. |
| D13 | All adaptive models failed, or a later clean gain proves robustness | Bound original-gate negatives; retain separate anchored clean positive and inconclusive matched robustness | R; F §§7–7.1. Original F6, September anchored Task 3/4 and October E6 are separate procedures. |
| D14 | Completed-action prediction proves online anomaly detection, or supervised classification was outside the proposal | Retain the declared offline task and explicitly exclude prospective warning claims | P §5.1; C1; F §5.1,§9.1. Known complete boundaries/trajectories are legitimate for that task. |
| D15 | Synthetic faults establish external industrial reliability | Restrict robustness to named operators, realizations, models and groups | P §5.6; K; R. Synthetic degradation is not a field-failure distribution or external acquisition validation. |
| D16 | Time-block dropout/temporal pooling answers misalignment robustness | Explicit cross-modal clock-shift robustness remains UNTESTED | P §5.6; K keeps timestamps unchanged; F §3. Record this original operator-scope gap without launching a test. |
| D17 | Missing audio is a predictive failure or was fully evaluated | Audio/AST/trimodal performance remains UNTESTED, with a documented feasibility exclusion | P §§5.2–5.3; F §§3,7. Preserve it as partial modality coverage. |
| D18 | Broader evaluation can be replaced with the new primary AP comparison | Keep SQ4: calibration, threshold costs, robustness, modularity, interpretability limits, provenance and feasible computation | P §5.7; F §§5–9. Warm timings are not end-to-end production guarantees; gate plots are not causal explanations. |
| D19 | No human review exists, or selected agreement establishes population accuracy | Preserve the reported one-reviewer 64-clip status and 57/59 determinate agreement only | F §9.3. Raw adjudication and second-rater reliability were not established; no private mapping/ratings read here. |
| D20 | Old source concerns force a new research campaign or can be silently repaired | Retain PHM patch-grid/effective-config and historical-source limitations with unmeasured impact | C3; F §§8–9,13. No code fix, forward test, retraining or revised score is part of TASK 2B. |
| D21 | October 6 export omissions are live-repository absence, or its date covers later experiments | Attribute evidence to its review scope and date; preserve later TASK 2 checks separately | F §1.4,§6; T2. PHM row MAE was subsequently recomputed, but full original target/core identity/training reproduction is not thereby closed. |
| D22 | External MSM validation is the second main RQ or automatic next task | Optional extension to the architecture/SQ3 evidence after a separate decision | P §§5.6–6; U; F §14; T2 literature access limits. Dataset-specific fitting differs from zero-shot transfer. |
| D23 | Original welding/all-Transformer/physics wording is automatically an accurate final title | Propose a task-accurate architecture/fusion title and abstract, with approval status explicit | P pp.1,4–7; C1/C2; F §3. Restricted process context is allowed, but no physical equations/all-Transformer retained system/welding deployment is implied. |
| D24 | Historical proposal/evidence should be overwritten or silently sanitized | Preserve all five TASK 2 documents verbatim inside labelled historical appendices; edit only six authorized documentation files | U; repository preservation policy; entry hashes below. Old code, raw data, reports, PDF and supplied review remain unchanged. |

## Answer status and contradictions

The main RQ is **partially answered** through implemented design/evaluation under the adapted case studies. SQ1 is **partially answered** overall: tested representations have bounded findings, while audio and broader candidate coverage remain incomplete. SQ2 is **answered within the adapted bimodal/scalar-gate comparison**, and **partial** against literal projected-embedding/trimodal scope. SQ3 is **partially answered** by synthetic tests and structural fallback, with original-gate negative and later contrast-specific positive/inconclusive findings. SQ4 is **partially answered** through quantitative/architectural evaluation without prospective usability certification.

Open questions themselves are not “contradicted” by a negative model result. Particular expectations or descriptions can be: original-gate superiority is not supported under the specified criterion; “the retained core is all-Transformer,” “PHM fused_all_three is image+sensor fusion,” and “the whole-segment system demonstrates online warning” contradict inspected implementation/task descriptions. Universal adaptive failure, physical label truth and general field reliability are unsupported extrapolations, not established negative findings.

## Working title and abstract disposition

**Proposed title:** *Design and Evaluation of Multimodal Fusion Architectures for Industrial Condition and Failure Monitoring: PHM and REASSEMBLE Case Studies*

The [complete draft abstract](RESEARCH_CHARTER.md#working-title-and-abstract--proposed-wording) centers the implemented modular pipeline and representation/fusion comparison, names task-specific supervision, distinguishes original scalar gates from exploratory extensions, and qualifies synthetic robustness and deployment limits. It does not claim MSM evidence or a universal adaptive advantage. Formal approval of this title/wording/manuscript is **UNVERIFIED**; the accepted dataset-transition agreement is preserved separately.

## File disposition and preservation

| Authorized document | Current content / change |
|---|---|
| [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md) | Exact original RQ/SQs; proposed working main; architecture contracts; H-SQ3-Q; title/full abstract; historical original appendix |
| [EXISTING_EVIDENCE_MAP.md](EXISTING_EVIDENCE_MAP.md) | Every original question mapped to E1–E8 and relevant September extensions, statuses, sources and review-level boundaries; original map retained |
| [LITERATURE_POSITIONING.md](LITERATURE_POSITIONING.md) | Architecture/SQ1–SQ4 roles and optional MSM scope; original nine source records/access caveats retained |
| [OPEN_RESEARCH_DECISIONS.md](OPEN_RESEARCH_DECISIONS.md) | Settled dataset agreement separated from title, literal scope and assurance decisions; superseded prior questions retained historically |
| [EXECUTIVE_REVIEW.md](EXECUTIVE_REVIEW.md) | Current architecture-centered summary, evidence and risks; original summary retained |
| [EXPOSE_ALIGNMENT_DECISION.md](EXPOSE_ALIGNMENT_DECISION.md) | This source-grounded decision record |

The preserved TASK 2 originals are bounded by `TASK2_SNAPSHOT_BEGIN` / `TASK2_SNAPSHOT_END` comments in each corresponding document. Their exact content hashes at TASK 2B entry are:

| Original document | SHA256 |
|---|---|
| `RESEARCH_CHARTER.md` | `934b277af5abf9bef5202416efe3d0f847d8377347187bfef7d2fa51bbdca002` |
| `EXISTING_EVIDENCE_MAP.md` | `2392bd05374c6825ff3ff96a1cfe4e29e519979a7b46f195f14751105f1a404b` |
| `LITERATURE_POSITIONING.md` | `c68362ceb84948fe9d1c41210699954b4418a5c06e9e4aef2f71960298ce4022` |
| `OPEN_RESEARCH_DECISIONS.md` | `df0c3558501cd4d5b02429a3e08a7170a10184d1848be3435f2fe31460e26a64` |
| `EXECUTIVE_REVIEW.md` | `26651a46389431acd01a471fdccf970e9284e273a3ce6ec09f0c26f5b0fe37d0` |

The original PDF was already untracked when supplied; it is not staged, rewritten or copied into a different repository location. The supplied review remains in its attachment location. Neither source is treated as an instruction to run old tests, historical Task 4, queues or supervisors. No historical results, cancelled-task disposition or scientific formula is changed.

## Validation and remaining decisions

Handoff validation completed on 2026-10-25:

- **PASS:** all five original questions match PDF pp.2–3 after removing page-number footers and normalizing extraction whitespace/line-break hyphenation; quoted wording was also read directly.
- **PASS:** all five earlier proposals are preserved byte-for-byte in their marked historical appendices, matching the entry SHA256 values above.
- **PASS:** all 13 protected PDF/review/source/config/report hashes match the task-entry manifest. No code, configuration, historical result, dataset or source PDF was changed.
- **PASS:** exactly six authorized documentation files; 113 local link targets and three current-section anchors checked; no new trailing whitespace or conflict markers.
- **PASS:** `git diff --check`; `ma_thesis_env/bin/python -B -m pip check` returned `No broken requirements found.` No packages were installed.
- **Scope:** `git status --short --branch --untracked-files=all` shows only the supplied PDF, the five pre-existing untracked proposals, and the new alignment document. `git diff --stat` is empty because these documents are untracked; no staging/commit/push was performed. Relative to the task-entry snapshots, all five proposals contain additions only; their original text remains intact.

No training tests, model inference, bootstrap, raw-data processing or project entry points were run. These are document/source-preservation and environment checks, not renewed scientific validation of historical experiments.

Remaining decisions: final title and adapted main wording; whether the explicitly declared scalar-gate/audio/misalignment limitations suffice for the final submission; chapter balance and which protocol-specific comparisons are primary; assurance needed for named claims; and whether any optional MSM work is proportionate. These are **not** a renewed request to approve the already agreed PHM + REASSEMBLE transition.

**STOP — no next task is started.**
