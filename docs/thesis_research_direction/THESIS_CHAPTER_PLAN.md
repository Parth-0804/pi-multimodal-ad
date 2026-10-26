# Thesis chapter plan and professor-facing brief

TASK 4 · 2026-10-26 · **P: proposed structure and claim hierarchy, not final scope/title approval.** Baseline `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.

The thesis should explain an architecture investigation with an honest development history: what entered → what was implemented → what came out → how it was evaluated → what was concluded → why the next study was justified. Preserve the original exposé and the accepted PHM + REASSEMBLE transition. Distinguish a scientific explanation of the transition from an invented claim that every later diagnostic was planned at the outset.

The [experiment inventory](THESIS_EXPERIMENT_INVENTORY.md) defines implementation/protocol IDs and V/R/I/P evidence labels. The [master results](THESIS_MASTER_RESULTS.md) supplies separate A–F tables, [contribution ledger](THESIS_CONTRIBUTION_LEDGER.md) controls wording, and [evidence gaps](THESIS_EVIDENCE_GAPS.md) records uncertainty and approval decisions. Existing TASK2B/TASK3 documents are preserved; none is rewritten as the original exposé.

## Proposed argument and central result

**P:** organize the main result around the original REASSEMBLE architecture comparison: a small calibrated probability stacker improved the selected combined pipeline over strong sensor statistics, while the original contextual gates did not establish added value under their qualification criteria. This is a comparative result under declared recipes; it does not prove F2 discrimination superiority over uniform averaging, unique visual information or the isolated effect of adaptation.

**V:** core F2 AP .447299 versus U1 .429392, direct difference+.017907. **R:** paired interval [.008603,.028284]. F1 AP .445742 is close; F2−F1 AP is unresolved. **V/R:** original gate points/criteria and original robustness outcomes bound the expected adaptive advantage. This result connects architecture design, exact fusion operators, strong baselines and uncertainty, rather than selecting the largest later AP as the central claim.

The strongest separate exploratory positive is **R** last-quarter pooling and its own static F2 follow-up (.493437 versus .447299, paired Δ+.0461 [.0260,.0632]). Present it after the retained comparison. It cannot retroactively become the original architecture or an independently confirmed winner.

## Chapter 1 — research problem, original questions and accepted adaptation

- **What entered:** [original exposé](../../MA_Exposé_Ravaliya_Parth.pdf), §§1–6, and researcher-reported supervisor agreement to switch from Intel welding to PHM + REASSEMBLE, preserved in [TASK2B decisions](EXPOSE_ALIGNMENT_DECISION.md).
- **What was implemented:** a feasible representation/fusion/evaluation programme on two different tasks. Explain the restricted original use of “physics-informed”: process/sensor/metadata context, not physical equations.
- **What came out:** the declared main RQ and original SQ1–SQ4 remain the organizing framework. The [charter's](RESEARCH_CHARTER.md) adapted main wording/title are proposals, not literal original quotations or approved final text.
- **How evaluated:** map each question to the contribution ledger; define what would count as a bounded comparative answer. Negative and inconclusive findings are legitimate; architecture novelty or adaptive superiority is not presumed.
- **Conclusion:** the empirical center is completed-action visual–sensor classification/fusion on REASSEMBLE, with PHM as preliminary supervision/sensor feasibility work.
- **Why next:** precise foundations are needed to distinguish pretrained components, executed architectures, representation versus decision fusion and different meanings of robustness.

## Chapter 2 — theoretical foundation and closest research methods

- **What entered:** the primary papers/access qualifications in [TASK3](TASK3_LITERATURE_EXPERIMENT_MATRIX.md), supplemented by exact operator comparisons in the inventory.
- **What was implemented:** describe the concepts actually used: CNN transfer, channel-independent patch encoding, engineered summaries, stacking, representation concatenation, contextual logarithmic pooling, coefficient modulation and quality interactions. Use the original mathematical definition before the local adaptation.
- **What came out:** a method-to-code map identifying changed objective, input, pooling, training/pretraining, constraints and evaluation. Include industrial precedents DMAW/MBGN without comparing incompatible published accuracies to project AP.
- **How evaluated:** explain ranking versus probability scoring versus hard decisions; grouped nested fitting; fixed-score intervals; missingness coverage; exposure and selection. Distinguish conditional reliability assumptions from an AP guarantee.
- **Conclusion:** the practical implementations mainly use established methods with task-specific adaptations. A targeted prior-art review does not certify novelty.
- **Why next:** task/target/group definitions determine whether those methods can be evaluated meaningfully. No broad model-name catalogue should substitute for that evidence.

## Chapter 3 — datasets, targets, observation windows and evaluation units

- **What entered:** PHM image/sensor records and REASSEMBLE annotated high-level actions. Active PHM scope A1–5/B1–7/F1–8; A Run2's organizer-reported overlap warning remains non-destructive and configurable. [Scope](../active_scope.md), [data boundaries](../data_boundaries.md).
- **What was implemented:** P00 v3 proxy/version registry; RE cohort filtering, native label mapping, selected modalities/intervals and recording folds. State P04 minute features separately from P12 raw vibration. Explain PHM image-derived supervision versus RE native success annotations.
- **What came out:** PHM20 runs/three experiments; RE4,551 primary actions reduced to4,530/509 failures/148 recordings by existing eligibility. Record why21 actions were excluded; do not imply labels were corrected in TASK4.
- **How evaluated:** V saved cohort/labels/split consistency and PHM CSV truth-to-v3 agreement; R native audit/known hardware issues. Show outer fold denominators, temporal sampling/interpolation/masking, prediction cut-off and group hierarchy. Existing full-action endpoints are legitimate inputs for the offline task.
- **Conclusion:** these are different prediction problems and statistical units; they cannot share a leaderboard. Recording-disjoint assessment is narrower than unseen object/site validation; both programmes have exposed assessment histories.
- **Why next:** PHM required a supervision/feasibility assessment before architecture findings could be interpreted as physical condition prediction. REASSEMBLE supplies the stronger principal fusion case, with its own semantic limits.

## Chapter 4 — PHM practical investigation and its limits

- **What entered:** potential visual/process/RMS/CI/raw-vibration evidence but provisional quantitative supervision. Use [inventory P00–P16](THESIS_EXPERIMENT_INVENTORY.md) and results A.
- **What was implemented:** target operator; frozen RT-DETR scalar head; genuine RT-DETR detection and joint detection/regression; custom sensor PatchTST; grouped feature/decision/embedding-gated sensor models. Briefly cover AnomalyDINO and angular/tooth-sector diagnostics as separate approaches to the validity/feasibility problem.
- **What came out:** V retained LOEO constant .804156, grouped feature model .823786, PatchTST .941455 MAE. R v2 detection poor; multitask image and run results point in different directions. R selected DINO review and raw-feature screens do not establish validated physical supervision or useful out-of-experiment prediction.
- **How evaluated:** separate v2/v3, image/tooth/run levels, fixed-split/LOEO and real/synthetic evidence. Report three-domain dependence, repeated EXP-F assessment, teacher coverage, target repeatability, padding/effective-config concern. Use paired differences, not overlapping marginal intervals as a test.
- **Conclusion:** the tested PHM formulations did not establish useful improvement over the retained run reference; proxy validity and small grouped samples limit stronger claims. “No signal anywhere” and “fusion cannot work” exceed the evidence. Synthetic controls demonstrate sensitivity only to their constructed inputs.
- **Why next:** architecture/fusion evaluation required a case with a defensible action target, paired modalities and enough groups to compare branch predictions. This provides the evidence-based rationale for REASSEMBLE; it is not a retrospective claim that PHM was planned to fail.

Keep this chapter focused. Detailed pseudo-box metrics, formulas, profile/rank controls and raw-vibration screens belong in appendices, with a short main-text account of their methodological implications.

## Chapter 5 — retained REASSEMBLE architecture and fitting protocol

- **What entered:** fixed cohort/folds and selected hand-camera/sensor inputs; initial action/prior controls and candidate representations.
- **What was implemented:** R01 frozen pretrained CNN, R02 statistics and separate R03 scratch Transformer; F1–F6 exact equations/interfaces, contexts, availability masks, losses, calibration, selection and thresholds. Include dimensions and frozen/trained boundaries in one diagram per branch/fusion level.
- **What came out:** a modular bimodal prototype. Explain why statistics were retained after the initial short-budget sequence comparison, why decision-level gating preserved those validated branch predictions, and where this materially adapts the exposé's embedding-space gate.
- **How evaluated:** nested branch/meta-fitting boundaries, inner selection, three-seed mean for fusion heads, probability/hard decision provenance and conditional recording bootstrap. Document F2's training-side global-OOF threshold qualification.
- **Conclusion:** all implemented architectures are inspectable, but their links/constraints/loss/calibration differ. F2 versus F4–F6 is a comparison of practical families, not a clean adaptation-only intervention.
- **Why next:** compare the retained families on compatible outcomes, then test their behavior under fixed faults. Separate architecture diagrams from later exploratory coefficient/quality heads.

## Chapter 6 — retained comparative results, robustness and evaluation beyond accuracy

- **What entered:** the frozen branch/fusion procedures and their controls, before later representation/adaptation studies.
- **What was implemented:** original Section1/1B/2 assessments, Section3 frozen-model faults, completed D6 modality-dropout comparison, context ablations and R10 feasibility/cost accounting.
- **What came out:** present results B/C/D in that order: representation references; static/concatenation/gate comparison; robustness mechanism/outcome; decision/calibration/cost trade-offs. Include audio and physical-object evaluation gate outcomes without fabricated predictor scores.
- **How evaluated:** paired AP/AUROC intervals, post-hoc F1/F2 label, gate qualification/multiplicity, per-fold signs, threshold vectors, confusion counts, Brier/ECE15, timing scopes, fallback/abstention coverage. Original S3 has one fault realization, not repeated independent evidence.
- **Conclusion:** the simple static reference is justified in the tested architecture programme. Original gates do not demonstrate their anticipated advantage; some weight responses are correct without outcome benefit. Dropout is mixed and cannot improve absent information through a fixed surviving branch.
- **Why next:** the findings motivated specific questions about training budget, observation location, preserving F2's useful function class and matching corruption exposure. They did not authorize an unrestricted search for a winning gate.

This is the central results chapter. Use at least one figure showing uncertainty around compatible core comparisons and one calibrated/decision trade-off; draw them later only from the frozen table sources, without rerunning models.

## Chapter 7 — explicitly exploratory follow-ups

Keep September and October in distinct subsections with their own denominators, baselines and fitting recipes; use results E/F. Do not assemble a combined-best leaderboard.

| Subsection | What entered → implementation → output | Evaluation → conclusion → reason for next step |
|---|---|---|
| **7.1 Training budget and same-sensor combination** | Short PatchTST cap → S-LONG and same-sensor stacker → R improved matched sequence score and small hybrid gain. | Same-fold/separate three-seed procedure; sequence still below statistics. Supports a budget-qualified original negative and representation combination, not another modality. |
| **7.2 Anchored adaptation and Gaussian exposure** | Successful static function class → bounded coefficient modulation/constant control, then matched augmentation → R clean gain but robustness primary unresolved. | Preserve recall/ECE and clean-loss trade-offs. Distinguishes original logit gate from later adaptation; motivates a narrower quality/exposure question without promising a win. |
| **7.3 Observation location and pooling** | Possible dilution by whole-action means → fixed-bin/last-quarter/GRU comparison → R last-quarter gain and one selected static fusion follow-up. | Report multiplicity, one seed and same-cohort selection. Location/aggregation is supported; learned-order benefit and online timing are not. Do not portray this as completion of cancelled September Task1. |
| **7.4 Spatial encoder and fine-tuning** | Question about reused detector representations → October encoder tap and separate asymmetric/matched tuning studies → R encoder loss and inconclusive tuning benefit. | Full cohort but G/C fitting, fixed budgets/.5 thresholds; two seeds only in matched diagnosis. Causes remain unresolved. More complexity is not automatically useful. |
| **7.5 Static faults and quality interactions** | Selected static sensitivity → fixed native-fault pilot, then equally exposed A/B/C heads → V tiny primary difference, R broad interval/clean uncertainty. | One fold26 recordings;3/11/27 parameter counts and direct-q pathway. H-SQ3-Q remains a specific inconclusive SQ3 hypothesis. No automatic reliability, external validation or main-RQ replacement. |

End the chapter with the limits of iterative assessment: predeclaring a later recipe before its own outputs does not erase earlier outcome-informed study selection. Do not claim a sequential narrative proves any unmeasured causal mechanism.

## Chapter 8 — synthesis by original question and threats to validity

- **What entered:** retained comparison, separate exploratory studies and literature-to-method differences.
- **What was implemented:** use the contribution ledger to answer each original SQ in its exact wording; distinguish measured findings, algebraic consequences, interpretations and untested coverage.
- **What came out:** three bounded contributions; a justified static reference; representation sensitivity; honest negative/inconclusive robustness conclusions. PHM supports target/feasibility lessons, not independent confirmation of REASSEMBLE.
- **How evaluated:** discuss target/semantic validity, missing modality coverage, physical grouping, repeated assessment exposure, fixed-score uncertainty, model-family confounding, reviewer sampling and provenance. Identify which conclusions survive without another experiment.
- **Conclusion:** scope acceptance and precise claims make the evidence defensible. Novelty, causal trust, online deployment and industrial generalization remain unestablished.
- **Why next:** the conclusion should give design recommendations tied to observed evidence and clearly separate optional future work from required present claims.

## Chapter 9 — conclusions and bounded future work

- **What entered:** explicit answers to Main/SQ1–SQ4 and the accepted final scope after supervisor review.
- **What was implemented/produced:** summarize the practical prototype and its comparative evidence, with the exact case/task labels. No new main result appears in the conclusion.
- **How evaluated:** every concluding sentence must link back to a result/protocol/limitation in the preceding chapters. State the strongest negative and uncertainty as clearly as the positive result.
- **Conclusion:** lightweight static fusion is a defensible tested reference; contextual complexity needs evidence beyond varying weights; task/target/observation design can matter more than a model label.
- **What would follow:** optional claim-specific quality/content controls, explicit native clock shifts or independent acquisition study only if justified and separately approved. MSM is an optional feasibility/transportability extension, not an executed result or zero-shot transfer claim.

## Appendix allocation

| Appendix | Material and purpose |
|---|---|
| A | Exact original exposé questions, approved/reported/proposed scope distinctions, TASK2B alignment decisions. Preserve the approved PDF itself. |
| B | Complete PHM target-version/formula ledger, v2 detection/multitask and v3 LOEO tables with level/protocol labels. |
| C | PHM DINO, raw vibration/sector, profile/teacher/odd-even diagnostics; never substitute review agreement for physical target validation. |
| D | Clearly separated **synthetic** signal/rank controls and their retests; partial/cancelled work inventory. Optional Paderborn feasibility discussion only if needed, with its own protocols and no fusion-validation claim. |
| E | Full core folds, seeds, thresholds, decision/calibration bins, conditional permutation control and grouped uncertainty definitions. |
| F | All original robustness conditions, dropout results, allocation/context ablations, audio/object feasibility and coverage. |
| G | September/October exploratory full tables, curves, selected/reused fits, costs, deviations and selection limits. No combined winner. |
| H | Evidence paths/hashes, bounded TASK4 validation, reproducibility limits, failed-attempt records and unresolved gaps. Large caches/checkpoints remain referenced by identity, not copied. |

A shortened thesis should retain the original architecture comparison, its fitting boundaries, F1/F2 qualification, gate-family confounding, main robustness result and exposure/target limitations in the main text. Move numerical detail to appendices, not the caveats needed to understand the central claims.

## Concise professor-facing explanation

**P — proposed briefing wording, grounded in the retained evidence:**

> The agreed move to PHM and REASSEMBLE retained the thesis focus on AI architecture and fusion evaluation. PHM offered images and heterogeneous machine measurements, so it provided a practical setting to investigate supervision, sensor representations and fusion feasibility. Its quantitative target was derived from image-processing rules rather than independently validated physical damage. Under the retained twenty-run experiment-disjoint evaluation, the tested sensor models did not demonstrate an improvement over a training-mean reference. Separate detection, multitask, DINO and vibration studies provided useful diagnostics but did not remove the supervision and statistical limitations. These findings do not establish that PHM has no useful information.
>
> REASSEMBLE therefore provides the principal architecture/fusion case: native action-success annotations, paired visual and sensor inputs, and recording-level evaluation support a more substantial comparison. A small static stacker improved the selected combined pipeline over sensor statistics, while the original contextual gates did not establish added value. Later exploratory representation and anchored-adaptation results are preserved separately. Robustness is assessed with controlled synthetic faults; the quality-interaction pilot remains inconclusive. The task is completed-action failure classification, and neither online warning nor external industrial validation is claimed.

This is a defensible scientific rationale (**I/P**), not documentary proof of the researcher's original intention at every stage. The dataset-switch agreement itself is accepted as researcher-reported context; no new permission for that switch is requested.

## Decisions for the single next activity

**P — ONE recommended activity after TASK4:** conduct a researcher–supervisor **evidence and final-scope review** using these five documents. Its concrete output should be one agreed statement of final task/title scope, original-question coverage, the three contribution claims and which gaps are disclosed rather than experimentally expanded. No message or meeting has been scheduled or sent.

The review should resolve title wording; acceptance of bimodal/scalar-gate and offline-task coverage; untested audio/clock-shift/external-validation boundaries; whether any stronger claim truly requires an extra experiment; and which exploratory findings deserve main-text space. Documentary final-title approval is presently unverified. If this bounded scope is accepted, another model experiment is not scientifically compulsory; chapter drafting can then follow the agreed outline.

**STOP after documentation and findings.** No future experiment, cancelled-work restart, model execution or publication action is initiated by this plan.
