# Executive review — exposé-aligned thesis direction

TASK 2B revision, 2026-10-25 (Europe/Berlin); baseline `3c4fb20be`. **Current proposal for review.** Previous TASK 2 wording and numerical-check record are preserved verbatim below.

## Main question and scope

The original exposé's §3 main RQ is:

> How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial anomaly detection using robotic welding data as a case study?

**Proposed working adaptation:**

> How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial condition and failure monitoring using PHM and REASSEMBLE as case studies?

Keep original SQ1–SQ4 as the structure: representation suitability; unimodal/concatenation/late/gated predictive comparison; robustness to missing/degraded/unreliable modalities; and evaluation beyond accuracy. Their exact wording is in [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md). The quality-conditioned, augmentation-matched comparison is **H-SQ3-Q**, not the main thesis RQ.

**Accepted context:** the researcher reports supervisor agreement to PHM + REASSEMBLE, also recorded in October 6 review §1.1. That transition is not reopened. Final-title/manuscript approval is a separate documentary question and is not established.

## What is answered

- **Main / SQ2:** a modular pipeline and an adapted bimodal architecture comparison are implemented. Core F2 AP 0.447299 versus statistical sensors 0.429392 supports a bounded static-fusion increment; audio/trimodal and literal shared-embedding gating scope remain partial.
- **SQ1:** CNN versus spatial hybrid encoder, PatchTST versus statistics, frame count and fine-tuning were investigated under their own protocols. Core CNN extraction is expressly permitted by exposé §5.2. Selecting statistics is a budget-specific result, not the absence of a Transformer experiment.
- **SQ3:** original synthetic gate tests did not establish the specified advantage. The later one-fold quality-interaction contrast +0.003012, CI [-0.026711,+0.032165], remains inconclusive. A separately reported static-anchored model's clean-AP gain qualifies any blanket statement that adaptation never helped; it does not establish general corrupted-input robustness.
- **SQ4:** calibration, threshold trade-offs, allocation ablations, modularity/provenance and bounded cost/timings were evaluated. Causal interpretability, prospective deployment and operator usability remain unestablished.

Complete-action classification uses known segment boundaries and complete trajectories. It is permitted as supervised classification under exposé §5.1, but it provides no online early-warning result. Synthetic corruption, temporal dropout and temporal pooling do not demonstrate cross-modal clock-shift robustness or independent industrial validation.

## Working title and abstract

**Proposed title:** *Design and Evaluation of Multimodal Fusion Architectures for Industrial Condition and Failure Monitoring: PHM and REASSEMBLE Case Studies*

The [charter's draft abstract](RESEARCH_CHARTER.md#working-title-and-abstract--proposed-wording) centers modular architecture, representation selection, comparative fusion and broader evaluation. It explicitly qualifies provisional PHM supervision, completed-action REASSEMBLE prediction and synthetic robustness. It claims neither an all-Transformer retained pipeline nor an approved final title. MSM is not included as completed work.

## Main scope risks

1. **Architecture/task overstatement:** CNN features versus spatial Transformer execution; statistics versus PatchTST; scalar-logit gates versus later coefficient/quality interactions; completed actions versus online warnings.
2. **Inference beyond evidence:** repeated cohort exposure, unresolved higher-level grouping/identity/label validity, and fixed-prediction rather than full selection/training uncertainty. Negative core and positive exploratory findings need separate protocol labels.
3. **Coverage and assurance gaps:** audio/AST, explicit clock shifts and external industrial validation are untested; PHM patch-grid/effective-config and historical-source concerns remain bounded limitations. They do not by themselves require a new research campaign.

MSM is optional and remains unqualified at file level. It could add an independent methodology-validation study after separate approval; it is not a replacement for the architecture/fusion thesis or a prerequisite inferred from the exposé.

## Remaining decisions and delivered files

Review final title/main wording, the explicit scalar-gate/audio/misalignment qualifications, thesis emphasis and the assurance needed for particular claims. Keep the dataset transition settled. Only after that review consider any specifically justified additional check or MSM extension.

- [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md): exact original questions, working main wording, SQ3 hypothesis, title and full draft abstract.
- [EXISTING_EVIDENCE_MAP.md](EXISTING_EVIDENCE_MAP.md): every question mapped to experiments, results, status and implementation distinctions.
- [LITERATURE_POSITIONING.md](LITERATURE_POSITIONING.md): architecture-centered positioning and optional MSM role; earlier citations/access limits preserved.
- [OPEN_RESEARCH_DECISIONS.md](OPEN_RESEARCH_DECISIONS.md): settled context separated from actual unresolved choices.
- [EXPOSE_ALIGNMENT_DECISION.md](EXPOSE_ALIGNMENT_DECISION.md): source register, all material proposed changes and preservation record.
- [EXECUTIVE_REVIEW.md](EXECUTIVE_REVIEW.md): this summary.

No training, raw-data processing, download, code/result change, commit or push was performed for this reconciliation. The PDF and supplied review are preserved; each of the five earlier proposed documents is retained exactly in its own historical appendix. **STOP — awaiting researcher review.**

<details>
<summary>Preserved TASK 2 proposal — historical snapshot; current TASK 2B text above takes precedence</summary>

The following earlier proposal is preserved verbatim for provenance. Its original research hierarchy, missing-source statements and approval questions are superseded where corrected above. Numerical/source evidence retains its original review scope.

<!-- TASK2_SNAPSHOT_BEGIN -->
# Executive review — thesis direction and evidence

Date: 2026-10-25 (Europe/Berlin). Repository baseline: `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`. Status: **review packet, not a training authorization**.

## Recommended primary question

**Under recording- or operation-disjoint evaluation, does observable-quality-conditioned late fusion improve average precision under prespecified partial modality degradation relative to augmentation-matched static stacking, without exceeding a prespecified loss on clean inputs?**

This fits the retained robustness question and the actual controlled pilot. It avoids requiring a new architecture or an adaptive victory. Assess complete absence separately: the implemented arms share the same surviving-branch fallback, so missingness performance cannot demonstrate an adaptive advantage between them. The clean-loss margin still requires approval.

## Strongest existing evidence

- **Static fusion:** core REASSEMBLE F2 AP **0.447299** versus statistical sensors **0.429392**; empirical difference **+0.017907**. Point estimates were independently recomputed here; retained paired interval **[+0.008603,+0.028284]** was inspected, not recomputed. This supports incremental value under that specific nested protocol and exposed cohort.
- **Matched adaptive pilot:** primary AP **0.257009** versus augmentation-matched static **0.253996**. This review independently reproduced **+0.003012**, 95% **[-0.026711,+0.032165]**, from saved predictions and 2,000 paired recording draws. It is **inconclusive**, on only 753 actions/77 failures/26 recordings. Clean noninferiority is also unresolved.
- **Controlled follow-up:** two-epoch frozen32/fine-tuned32 comparisons cover five matched folds per seed. F2 changes are **-0.000796** and **-0.002822** for the two seeds; retained intervals cross zero. No reliable fusion benefit or unique cause is established. Visual-only point gains do not automatically become fusion gains.

These APs belong to different evaluation procedures/coverage and must not be ranked against each other as if they were one experiment. PHM is a separate provisional-target regression study: retained LOEO sensor methods do not demonstrate improvement over the constant baseline.

## Three largest scientific weaknesses

1. **Independence and development exposure.** Repeated use of the same cohort for research decisions, unresolved dependence above recording IDs, and conditional rather than full selection/training uncertainty. More existing folds do not create a new untouched final test.
2. **Limited evidence for adaptation.** Only one matched robustness fold, wide intervals, uncertain clean cost, and quality proxies that can represent task content as well as measurement quality. No established adaptive advantage exists to claim or replicate.
3. **Task/construct validity and scope.** PHM targets are provisional image measurements; REASSEMBLE predicts completed-action annotations. Approved exposé/direct supervisor feedback were not located. Physical defect truth, early warning, and compliance with the original approved direction remain UNVERIFIED.

## Literature and contribution

QMF, TMC, EmbraceNet, M3DM, MultiBench and WILDS provide established precedents for dynamic fusion, missingness handling and robustness evaluation. A reasonable thesis contribution is the controlled empirical comparison, its failure boundaries and traceable evidence. Architectural novelty is **UNVERIFIED**; the review is targeted rather than systematic. Original sources, full-text access levels and method differences are in [LITERATURE_POSITIONING.md](LITERATURE_POSITIONING.md).

## MSM and the next decision

**MSM remains a conditional candidate.** It could test a frozen comparison after dataset-specific fitting if its task, pairing and independent groups pass a separate audit. A synchronized visual-sensor study is not yet established. Audio+sensor validation would require accepting that modality scope explicitly. It would test methodology transportability, not zero-shot transfer of a fitted REASSEMBLE predictor.

Next: researcher/supervisor review of the charter, original proposal and operational margins; then, only if approved, a bounded MSM data audit. Do not begin more training or another architecture search now.

## Previous study and this task's changes

**VERIFIED committed and pushed:** frozen32 versus fine-tuned32 study at `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`; local HEAD, tracking ref and live `origin/main` matched during this review. Initial working tree was clean. This task adds only the five documents below, uncommitted; no commit or push is performed. Remote Git delivery does not establish preservation of ignored datasets, caches or weights.

1. [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md)
2. [EXISTING_EVIDENCE_MAP.md](EXISTING_EVIDENCE_MAP.md)
3. [LITERATURE_POSITIONING.md](LITERATURE_POSITIONING.md)
4. [OPEN_RESEARCH_DECISIONS.md](OPEN_RESEARCH_DECISIONS.md)
5. [EXECUTIVE_REVIEW.md](EXECUTIVE_REVIEW.md)

## Evidence checked

Git status/history and live remote ref; research contracts and retained proposal-search record; PHM target ledger/LOEO source/predictions; core REASSEMBLE configs/models/saved arrays; encoder, noise, adaptive and frame/fine-tuning configs/reports/predictions; controlled32 assessment hashes/fusion arithmetic/25 split jobs; accessible original research papers and indexed MSM publication excerpts. Numerical verification details and exact source paths are in the evidence map.

No raw-data scan, raw-input model inference, training, dataset download, existing-result modification, commit or push occurred. Saved fusion arithmetic was reconstructed without running project predictors. No original proposal, primary supervisor feedback, independent external performance or complete raw-to-model reproduction was verified.

## Defensible conclusion

The tested REASSEMBLE branches support useful static fusion under a bounded protocol. Quality-conditioned robustness is a scientifically motivated but unresolved hypothesis. A master's thesis can investigate that uncertainty honestly; independent methodology validation remains a proposed next stage. **STOP — awaiting researcher review and approval.**
<!-- TASK2_SNAPSHOT_END -->

</details>
