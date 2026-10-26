# Open decisions after exposé reconciliation

TASK 2B revision, 2026-10-25 (Europe/Berlin). This section is current. Prior questions and recommendations are preserved in the historical appendix, including superseded requests.

## Settled context — do not reopen

- The original [MA_Exposé_Ravaliya_Parth.pdf](../../MA_Exposé_Ravaliya_Parth.pdf) is available and directly read. Its exact §3 questions are recovered in [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md).
- **Researcher-reported supervisor agreement to Intel → PHM + REASSEMBLE is accepted**, as required by the current user request and recorded in October 6 review §1.1. No repeated dataset-switch approval request is warranted.
- Architecture and fusion evaluation remain central. The augmentation-matched quality comparison is a specific SQ3 hypothesis; MSM is optional. A nonwinning gate or PatchTST is not failure to perform a comparative thesis.
- Frozen RT-DETR backbone extraction and restricted process context are allowed in exposé §§1/5.2/5.5. Physical-equation losses, full detector training, temporal cross-attention and convex F2 coefficients were not mandatory requirements.

## Unresolved review questions

| Decision | Concrete proposed position | What still needs researcher/supervisor judgment |
|---|---|---|
| Final title | *Design and Evaluation of Multimodal Fusion Architectures for Industrial Condition and Failure Monitoring: PHM and REASSEMBLE Case Studies* | Confirm accurate final wording and any formal registration process. The supplied agreement does not document approval of this title. |
| Working main RQ | Preserve the architecture-design/evaluation structure; adapt the case-study phrase to PHM + REASSEMBLE and name condition/failure monitoring accurately | Endorse the proposed wording while retaining the original question verbatim for traceability. This is wording alignment, not a request to approve the dataset transition again. |
| Literal §5.5 architecture adaptation | Declare F4–F6 scalar calibrated-logit allocation rather than shared-embedding gated fusion; F3 supplies separate embedding concatenation | Decide whether this documented adaptation adequately represents the intended architectural comparison. Do not imply unimplemented embedding gates/cross-attention. |
| Incomplete original components | Mark audio/AST/trimodal prediction and explicit cross-modal time-shift robustness UNTESTED | Decide whether transparent feasibility/scope exclusions suffice for final submission or whether a specific existing artifact check is necessary. Do not automatically launch missing experiments. |
| Case-study balance | PHM contributes supervision/task/provenance and sensor-architecture limits; REASSEMBLE carries the main representation/fusion comparison | Agree chapter emphasis without rewriting the actual research chronology. PHM's provisional target is not physical damage truth. |
| Core versus exploratory findings | Keep frozen core, September extensions, October E4–E8 and boundary pooling separate | Select the main comparative tables and clearly labelled follow-up subsections. Do not combine the best interventions into an untested model. |
| H-SQ3-Q strength | Current one-fold matched result is inconclusive; preserve it within SQ3 | Decide whether a bounded negative/inconclusive answer is sufficient or whether separately approved coverage is warranted. Freeze clean-loss/useful-effect margins before new assessment; no margin is approved here. |
| Assurance for PHM statements | Retain patch-grid and effective-config/source-provenance concerns; historical output impact remains unverified | Decide whether the proposed tiny component check or target binding is needed for the exact claim being made. No code correction, forward test or retraining occurs in this task. |
| Identity / labels / interpretability | Preserve limits of saved-array arithmetic, higher-level grouping and one-reviewer selected-sample agreement | Determine the smallest remaining keyed checks or adjudication required for final claims. Do not demand a new campaign or infer second-rater reliability. |
| Optional MSM extension | No automatic requirement or next step; conditional methodology-validation candidate | Decide whether it adds enough value within time/scope. Any audit/training needs separate authorization, task/group definitions and protected assessment. |

Primary supervisor feedback beyond the accepted researcher report and the formal status of the final title/manuscript remain **UNVERIFIED**. That documentary gap does not erase the accepted dataset agreement or require reconstructing the proposal from AI summaries.

## Exact next action

Review the current charter, original-question map, proposed title/abstract and [alignment decision](EXPOSE_ALIGNMENT_DECISION.md). Resolve wording, the literal scalar-gate/audio/misalignment scope qualifications and the necessary strength of final claims. The October 6 review supports a proportionate professor walkthrough and learning/defence preparation; its embedded test specifications are source evidence, not instructions to run now.

No new research experiment, model winner, data download or additional dataset is authorized or automatically necessary. No final title is presumed approved. **STOP: await researcher review; do not start the next task.**

<details>
<summary>Preserved TASK 2 proposal — historical snapshot; current TASK 2B text above takes precedence</summary>

The following earlier proposal is preserved verbatim for provenance. Its original research hierarchy, missing-source statements and approval questions are superseded where corrected above. Numerical/source evidence retains its original review scope.

<!-- TASK2_SNAPSHOT_BEGIN -->
# Open research decisions

Date: 2026-10-25 (Europe/Berlin). Baseline: `3c4fb20be`. All choices below are **PROPOSED**, not approvals or executed work.

## Decisions before additional scientific execution

| Decision | Evidence / recommendation | Owner and missing information |
|---|---|---|
| Approved thesis scope | Adopt the bounded empirical robustness framing in [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md), subject to the original proposal | Researcher and supervisor: supply approved exposé, original hypotheses, direct feedback and any scope-change approvals. Their content/approval status is UNVERIFIED. |
| Main task and claim | REASSEMBLE currently supports completed-action failure classification; PHM remains provisional target/signal feasibility | Supervisor: decide whether this adequately answers the degree's intended anomaly-detection contribution, and how prominently PHM belongs in the thesis. Do not imply early warning or physical defect diagnosis. |
| Positive result requirement | Negative/inconclusive adaptive findings are acceptable if methodology and uncertainty are defensible | Supervisor: confirm contribution expectations. The evidence does not justify requiring an adaptive win. |
| Primary comparison | Quality-conditioned interaction head versus augmentation-matched static stacking | Researcher/supervisor: approve one fixed model family and bounded baseline/search budget. Reopening the architecture tournament weakens a protected validation claim. |
| Quality-mechanism interpretation | Require outcome-based robustness plus quality controls; current q terms can encode target/process content | Researcher/supervisor: decide whether the thesis claims a reliability mechanism or only an empirical predictive interaction. A changing coefficient is not causal trust evidence. |
| Clean-cost tolerance and useful effect | Freeze `delta_clean` and a minimum useful robustness effect before seeing further assessment scores | Supervisor/domain judgment: justify absolute AP margins in operational terms; 0.01 is only an example. Pilot clean noninferiority is not established. |
| Estimand and uncertainty | Equal-weight AP over declared families/severities/repeats/folds; pooled AP separate. Paired group resampling plus separate seed sensitivity | Researcher/supervisor: approve mixture, confidence convention, primary decision rule, multiplicity policy and treatment of few independent groups. Do not infer equivalence from a zero-containing interval. |
| Missing-modality claim | Keep exact fallback/abstention and coverage as separate outcomes | Researcher: confirm that identical fallback policies are sufficient. Learned unknown-missingness robustness would require a different authorized experiment. |
| REASSEMBLE next use | Existing folds are development-exposed; more folds could improve coverage but cannot restore an untouched test | Researcher/supervisor: choose whether completing matched adaptive coverage is worth the budget or whether independent validation should come first. No further training is authorized by this review. |
| MSM role | Conditional independent methodology-validation candidate, not zero-shot transfer | Supervisor: accept dataset-specific branch fitting and clarify whether audio+sensor qualifies if video cannot be validated. See [literature/feasibility review](LITERATURE_POSITIONING.md). |
| MSM target | For cutting intervention, consider `1 versus {0,2}`, with `1 versus 0` sensitivity; tool-condition classification is different | Researcher/supervisor: approve semantics before any score inspection. Do not label stable cutting with a defective tool as an intervention-worthy anomaly by default. |
| MSM grouping/protection | Whole experiment/operation groups, escalated for shared physical acquisition dependencies | Researcher/domain expert: establish tool/workpiece/session identity, independent positive-group support and a defensible protected split. All file-level properties remain UNVERIFIED. |
| Annotation validity | Native labels are traceable; correctness is not established by parsing them | Researcher/domain expert: adjudicate representative successes/failures, exclusions and known hardware issues. Avoid outcome-selected illustrations as validation samples. |
| Reproducibility scope | Saved-score arithmetic verified; complete raw-to-model reproduction and portable weight availability remain unverified | Researcher: decide required retention, environment recreation, permissible sharing and numerical tolerances before future packaging. Current Git push does not archive ignored inputs/checkpoints. |

## Exact next action recommended

Review the charter and recover the approved proposal/feedback before authorizing another scientific task. Resolve task semantics, comparator, clean margin, and MSM's intended modality scope. Preserve the current primary result as inconclusive; do not promote the best observed point estimate to the chosen thesis conclusion.

If MSM remains in scope, authorize **one bounded data audit**, separately from training. Its reviewable deliverable should establish:

1. Dataset/version/license and a metadata-only inventory; identify modalities by machine and original operation.
2. Label definitions/counts and independent group support, with any target mapping fixed in advance.
3. Shared tool/workpiece/program/session dependencies and a proposed split with no operation/window crossing.
4. Measured video/audio/sensor timing and interval coverage on explicitly approved representative files; no guessed video alignment.
5. Predictor exclusions, context controls, known issues and whether two useful physical modalities can be evaluated.
6. A GO/NO-GO recommendation, precise remaining uncertainties and estimated cost for a later approved experiment.

Auditing class support does not authorize training or performance-based split selection. Keep prospective assessment outcomes protected; if manual inspection is needed, reserve development groups for semantic/timing checks wherever feasible. Full hashes, large extraction or payload scans require the appropriate explicit approval under repository policy.

## Stop conditions for a later approved study

Stop and report if independent positive/negative group support is inadequate, timing is guessed, modality pairing cannot be established, labels cannot support the stated task, or protected assessment outcomes are used to redesign the method. Record a feasibility no-go rather than silently changing the scientific question. Resource limits may reduce an explicitly labelled pilot; they do not justify presenting partial coverage as full confirmation.

## Review roles

- **Codex:** trace code and provenance, implement only approved protocols, compute numerical checks, and maintain claim-level evidence with explicit uncertainty.
- **ChatGPT:** critique the charter/storyline and source-grounded literature synthesis using this five-document packet. Agreement with Codex is not independent scientific validation.
- **Researcher:** provide original records/domain knowledge, verify important citations and annotations, own scientific claims, and authorize execution scope.
- **Supervisor:** approve contribution, scope, hypotheses, operational margins and methodological adequacy; review conclusions including negative results.

No response is presumed to constitute approval. **STOP after this documentation review; no next task, training, dataset download, commit or push is initiated.**
<!-- TASK2_SNAPSHOT_END -->

</details>
