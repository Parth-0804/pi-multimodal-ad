# Thesis contribution ledger

TASK 4 · 2026-10-26 · baseline `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.

**P — recommended contribution framing:** this thesis contributes an implemented, task-specific architecture comparison and bounded empirical findings. Algorithmic novelty is not established. Different code, an extra gate or a new dataset does not itself constitute a new research method. “New empirical observation” below means a result of this project on its specified task/protocol; priority over all published observations has not been established.

The [original exposé](../../MA_Exposé_Ravaliya_Parth.pdf) remains the question authority. [TASK 2B](EXPOSE_ALIGNMENT_DECISION.md) accepts the researcher-reported supervisor agreement to PHM + REASSEMBLE; final title/manuscript approval is a separate matter. These documents consolidate evidence; they do not approve a revised research programme. [TASK 3's prior-art/access register](TASK3_LITERATURE_EXPERIMENT_MATRIX.md) remains the detailed literature foundation, including partial-access qualifications for MBGN and other sources.

Use **V** verified saved arithmetic/source/metadata, **R** historical report/interval, **I** inference, **P** proposed and **U** untested/unknown, as defined in the [inventory](THESIS_EXPERIMENT_INVENTORY.md). All intervals here are R. Source-linked numbers are in the [master results](THESIS_MASTER_RESULTS.md); unresolved requirements and minimum claim-specific validation are in [evidence gaps](THESIS_EVIDENCE_GAPS.md).

## Three strongest defensible contributions

| Proposed contribution | Evidence and scientific value | Classification and boundary |
|---|---|---|
| **1. Modular visual–sensor architecture and a controlled comparison against strong simple references.** | R01–R07 implement separate branches, representation concatenation, probability averaging/stacking and contextual logit gates. V: core F2 AP .447299 versus statistical sensors .429392, Δ+.017907; R interval [.008603,.028284]. Original gates do not qualify for added clean value. Equations expose substantive differences between the families. | Known-method implementation + task-specific adaptation + new task-specific empirical observation/informative negative finding. Not a novel universal architecture, unique visual-information proof or isolated causal effect of adaptation. |
| **2. Evidence that representation, observation location and fitting budget materially affect this task.** | V: statistics outperform the tested short-budget scratch PatchTST. R: longer matched training improves PatchTST by .0297 AP but remains below statistics; the separate frozen spatial encoder underperforms its CNN comparator. R: last-quarter pooling improves visual AP by .0885 and its selected static fusion by .0461. | New empirical observations, including negative comparisons and budget sensitivity. Compatible with known task dependence; no paper-benchmark replication, general Transformer ranking, learned-order attribution or pristine confirmation. |
| **3. A robustness evaluation that separates allocation response, predictive outcome, training exposure and missingness policy.** | R: original 0/12 joint mechanism/outcome qualifications; V: original corruption/dropout score arithmetic. R: matched September robustness interval spans zero. V: October C−A primary AP+.003012; R [−.026711,.032165], clean preservation unresolved. Deterministic fallback is identified algebraically. | Informative negative finding + inconclusive experiment + practical evaluation contribution. The framework is not claimed statistically novel; it prevents unsupported reliability and deployment conclusions. |

PHM's supervision/protocol feasibility findings are substantial supporting evidence, not a fourth algorithm invention or independent validation of the REASSEMBLE fusion result. Whether these bounded contributions satisfy the master's requirements is a researcher/supervisor decision; a positive adaptive winner was not required by the original questions.

## Contribution categories

| Category | Use in this thesis |
|---|---|
| **Known-method implementation** | Faithful use of an established idea/component, without claiming reproduction of its published benchmark. |
| **Task-specific architectural adaptation** | An explicitly described change to inputs, representation, head, objective, gate or protocol. Scientific meaning depends on what comparison it permits; novelty is a separate unanswered question. |
| **New empirical observation** | A measured, source-linked effect in this project's task/protocol, with evidence level, uncertainty and selection limits. No automatic field-wide priority claim. |
| **Informative negative finding** | The specified expectation/qualification did not hold under the tested recipe. This is not impossibility or equivalence. |
| **Inconclusive experiment** | Evidence still permits materially different conclusions; a zero-containing interval or unmet benefit criterion is not a demonstrated null effect. |
| **Untested hypothesis** | The relevant method, intervention, target or population was not evaluated. A failed feasibility gate does not manufacture a performance result. |

## Original main question

> How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial anomaly detection using robotic welding data as a case study?

Original exposé §3, p.2. **Partially answered under the accepted dataset transition and explicit task/architecture adaptations.** P: architecture and comparative evaluation remain central; PHM is provisional condition-proxy regression, REASSEMBLE is supervised completed-action failure classification. Original §5.1 permits supervised classification; it does not establish that our whole-segment implementation is online anomaly detection. “Process-aware” means specified context/metadata pathways, not physics equations. The charter's adapted main wording and title remain proposals, not silent replacements for this quotation.

## SQ1 — representations and suitability

> Which lightweight or pretrained Transformer-based representation components are suitable for visual, audio, and sensor time-series data in a multimodal industrial anomaly detection pipeline?

**Literature and findings.** [RT-DETR](https://arxiv.org/html/2304.08069v3) supplies pretrained detection representations; [PatchTST](https://arxiv.org/html/2211.14730v2) demonstrates channel-independent patch Transformers for forecasting with supervised/self-supervised options. Their original findings do not predict classification performance on our tasks. [MultiBench](https://arxiv.org/html/2107.07502v2) supports comparing simple and complex representations with cost/task dependence. [AnomalyDINO](https://openaccess.thecvf.com/content/WACV2025/papers/Damm_AnomalyDINO_Boosting_Patch-Based_Few-Shot_Anomaly_Detection_with_DINOv2_WACV_2025_paper.pdf) is a nominal patch-memory precedent, not physical target validation. Publication of an audio model such as [AST](https://www.isca-archive.org/interspeech_2021/gong21b_interspeech.pdf) does not establish locally valid audio supervision.

**Practical implementation and exact differences.** P01–P05/P11 and R01–R03/R11/R15–R18. Retained REASSEMBLE uses frozen RT-DETR **CNN only**, spatial/frame means and a small trained head; a separate October arm executes the spatial hybrid encoder. Engineered sensor statistics are not PatchTST. Both local PatchTST candidates are trained from scratch; PHM has a custom variable-length/masked-mean implementation, REASSEMBLE uses a fresh HF model on fixed512 positions. Forecasting heads/objectives, original normalization and pretraining are not reproduced. Pooling and fine-tuning change observation location or fitting recipe; V3's last-quarter mean has no learned temporal-order operator.

**What these differences let us investigate.** Feasible reuse, representation sufficiency at declared budgets, summary versus sequence encoding, spatial feature tap, training duration and boundary coverage. They do not isolate the causal contribution of attention, model-family capacity or pretraining unless those factors are matched.

**What was measured.** Same-task AP/AUROC, calibration/decisions and bounded costs in separate protocols; PHM proxy MAE and selected DINO agreement are different outcomes. V: core statistics AP .429392 versus scratch PatchTST .241591 and frozen CNN .230658. R: longer PatchTST, spatial encoder and boundary studies quantify their own contrasts. Fine-tuning benefit remains inconclusive, with substantial fitting cost.

| Implementation/comparison | Contribution classification | Relationship to literature/expectation |
|---|---|---|
| R01 frozen pretrained CNN; R02 statistics | Known-method implementation + task-specific adaptation | Feasible reference branches; component reuse is consistent with established transfer/feature engineering, not a strict published-result replication. |
| R03 short-budget PatchTST vs statistics | Informative negative finding + new empirical observation | Contradicts superiority of this tested sequence recipe; consistent with known task/budget dependence. Does not contradict PatchTST's forecasting findings. |
| R11 longer PatchTST; R12 same-sensor hybrid | New empirical observation | Budget and combination can matter even when the standalone candidate remains weaker. Representation stacking is established; not new multimodal sensing. |
| R16 spatial hybrid tap vs CNN | Informative negative finding | Contradicts an assumed improvement for this fixed tap/head recipe, not the original detection paper or attention generally. |
| R15 location pooling vs full mean | New empirical observation | Consistent with established temporal consensus ideas; measured task-specific magnitude, not a new temporal architecture. |
| R15 ordered GRU; R17/R18 fine-tuning | Inconclusive experiment | No reliable benefit under tested budgets. Absence of superiority does not show absence of temporal/image information. |
| P00/P05/P11 PHM supervision/profile diagnostics | Adaptation + negative/inconclusive feasibility evidence | Established image/ordering methods; selected human agreement and shape constraints do not validate physical damage. |
| Audio, pretrained sensor transfer, broad ViT/video families | Untested hypothesis | Audio alignment precondition failed; no predictive audio negative. A literature catalogue is not a requirement to implement every named model. |

**Unsupported remainder/status.** SQ1 is partly answered for selected visual/sensor recipes. Audio/pretrained time-series breadth remains incomplete. PHM padding-output impact and effective historical provenance remain unknown. More Transformer variants are not inherently needed if the bounded question coverage is accepted.

## SQ2 — comparison of fusion architectures

> How do unimodal baselines, simple concatenation fusion, modular late fusion, and process-aware gated cross-modal fusion compare in terms of predictive performance?

**Literature and findings.** [Wolpert (1992)](https://cafri-labs.github.io/lab-manual/papers/wolpert1992.pdf) establishes learning a combiner from held-out base predictions. [GMU](https://arxiv.org/html/1702.01992v1) learns featurewise representation gates. [Heskes](https://proceedings.neurips.cc/paper_files/paper/1997/file/59f51fd6937412b7e56ded1ea2470c25-Paper.pdf) gives logarithmic opinion-pool mathematics. [DMAW](https://isas.iar.kit.edu/pdf/Sensors2026_Fan.pdf) and [MBGN's primary publisher preview](https://www.sciencedirect.com/science/article/pii/S0888327026008538) establish industrial fusion/gating precedents; the latter's full protocol was not available in TASK3. No common task/split/metric permits their published accuracies to rank against our AP. A “first adaptive industrial fusion” claim is indefensible.

**Practical implementation/differences.** P06 feature concatenation is not its class name's implied decision fusion; P07–P10 supply a separate sensor-subgroup comparison. REASSEMBLE F1 averages probabilities; F2 fits an unrestricted affine probability stacker; F3 projects/concatenates visual features and statistics; F4–F6 mix calibrated scalar logits with contextual nonnegative normalized weights. These original gates differ materially from exposé §5.5's shared embeddings and from GMU. R13 later modulates two coefficients around F2; R20 is a regularized logistic interaction design.

For the three gate-related families, the exact distinction is:

| Family | Formula and consequential restriction | What the data can identify |
|---|---|---|
| Original R07 | `σ(Σ wm(u) logit(pm))`; masked softmax, no final intercept/calibrator. Per seed equivalent to a normalized geometric probability pool; prediction stays between clipped branches. | Whole-family predictive comparison, context sensitivity and fault response. Different link/loss/calibration/capacity confound “adaptation caused the difference.” |
| September R13 | `σ(b+Σ am[1+tanh(hm(u))]pm)`; anchor fixed, coefficient signs retained, individual scaling0–2, no normalization. | Added context-dependent freedom around an initially identical anchor, with constant-adjustment control. Different optimization/capacity still limit unique mechanism attribution. |
| October R20 C | `σ(b+c·q+Σm[am+dm·q]pm)`; unrestricted affine probability coefficients plus direct q effect. Can rewrite as conditional affine modulation followed by summation. | Relative predictive effect of this feature set at fixed C/augmentation; direct content, interaction, regularization and capacity effects are not separated by A/B/C alone. |

The latter two are related to restricted [HyperNetworks](https://arxiv.org/pdf/1609.09106) / [FiLM](https://arxiv.org/html/1709.07871v2) principles. Neither implements the original full paper architecture. These algebraic connections explain adaptations; they do not establish scientific novelty.

**What differences let us investigate.** Whether established small combinations exploit a useful pair of fitted predictors, whether contextual families earn their cost, whether preserving a successful anchor helps, and whether observed probabilities/decisions/calibration trade off. No assumption that one sophisticated family must win.

**What was measured/results contribute.** V: compatible core F1 .445742, F2 .447299, F3 .412231, F4 .443725, F5 .444549, F6 .441356 AP. R: F2−U1 interval positive; F2−F1 discrimination interval crosses zero, Brier/ECE differences favor F2 in post-hoc review. R: anchored adaptive clean AP+.0210 [.0015,.0419] versus A0 and+.0226 [.0036,.0432] versus constant adjustments, but recall/ECE trade-offs. P06 and additional PHM arms do not demonstrate lower MAE than their constant reference.

| Claim/comparison | Category | Thesis-safe contribution |
|---|---|---|
| R04/R05/R06 original implementation | Known method + task-specific adaptation | A modular, inspectable comparison with different exact combination levels; not a new fusion invention. |
| F2 versus U1 | New empirical observation | A bounded combined-pipeline AP/AUROC improvement on exposed retained data; descriptive complementary errors support interpretation. |
| F2 versus F1 | Inconclusive discrimination; reported probability-score improvement | A reason to retain F2 as calibrated static reference; not reliable AP superiority over simple averaging. |
| F4–F6 versus F2 | Informative negative finding | Original gate qualification criteria unmet; contradicts an asserted observed adaptive win, not every possible benefit. AP equivalence/inferiority is not established. |
| R13 anchored adaptation | Task adaptation + new exploratory empirical observation | Preserves the positive clean result; prevents the false conclusion that adaptation never helped. |
| P06/P07–P10 sensor subgroup fusion | Adaptation + negative/inconclusive comparison | Useful PHM feasibility evidence conditional on proxy targets; not a failed visual–sensor fusion trial or universal no-signal result. |

**Unsupported remainder/status.** SQ2 is substantially answered within the adapted bimodal/scalar-gate programme and partial against literal original embedding/trimodal scope. A sensor-only meta-calibration comparator is missing for a strong unique-information claim. Gate families are not matched sufficiently for adaptation-only causality. No combined-best model or strict reproduction of published benchmark findings exists.

## SQ3 — missing, degraded or unreliable modalities

> Can a gated cross-modal fusion architecture improve robustness when one or more modalities are missing, degraded, or unreliable?

**Literature and findings.** [ModDrop](https://arxiv.org/html/1501.00102v2) and [EmbraceNet](https://arxiv.org/html/1904.09078v1) establish training/architecture approaches to unavailable modalities; deterministic surviving-branch routing is a weaker property. [QMF](https://proceedings.mlr.press/v202/zhang23ar/zhang23ar.pdf) motivates informativeness of quality/reliability relations under its assumptions, but uses uncertainty/regularization mechanisms absent here. Its conditional bound is not a theorem that our interaction design improves actual AP. [Ovadia et al.](https://arxiv.org/html/1906.02530v2) distinguish in-distribution confidence from shifted predictive reliability.

**Practical implementation/differences.** Original frozen clean-trained corruption suite R08, categorical modality-dropout R09, September Gaussian-exposure R14, October static sensitivity R19 and A/B/C quality pilot R20. Quality36 and later quality8 are different observable feature sets. Neither is an experimentally validated error estimator. No original or later gate is automatically QMF, GMU, ModDrop or EmbraceNet replication.

**What the differences let us investigate.** Mechanism response separately from outcome retention; effect of corruption exposure versus adaptation; direct quality features versus interaction expansion; complete loss versus partial corruption. Conditional weights can vary because of action/label content. In particular C's `c·q` is a direct label pathway, while `pm dm·q` changes branch coefficients. Even an interaction-only benefit would not, by itself, prove causal trust or calibrated reliability.

**What was measured/results contribute.** Original six graded families×F5/F6 give R0/12 joint qualifications; some sensor faults shift weights correctly. V: original and dropout prediction arithmetic matches reports. R: dropout has mixed effects and structural complete-loss equality; September's mean adaptive−matched-static interval spans zero. V: October primary C−A+.003012; R [−.026711,.032165]. R clean interval admits meaningful harm. Strong synthetic sensor noise hurts the selected static pipeline, but sensitivity is not adaptive superiority.

| Result/hypothesis | Category | Relationship to existing knowledge |
|---|---|---|
| R08 original gates fail joint criterion | Informative negative finding | Contradicts the specified expected response-plus-benefit for these configurations. Known robustness methods do not guarantee success of our materially different family. |
| R09 modality dropout | Known-method adaptation + mixed/inconclusive observation | No automatic recovery from dropping a predictor whose surviving output is fixed. The zero-gradient singleton property is an architectural consequence, not a new robustness theorem. |
| R14 matched Gaussian exposure | Inconclusive experiment | Some beneficial and harmful conditions; equal exposure prevents attributing all changes to adaptation, but broader family confounding remains. |
| R19 static fault sensitivity | New empirical observation within pilot | Consistent with known shift vulnerability; not independent confirmation of another paper's numerical effect. |
| R20 C−A and clean constraint | Inconclusive experiment | Specific **H-SQ3-Q**, not the main thesis RQ. Does not establish superiority, equivalence or no clean cost. |
| q is modality reliability; clock offsets/audio faults; external MSM | Untested/unresolved hypotheses | Need distinct identifying evidence; synthetic noise, pooling and missing blocks cannot substitute for clock shifts or independent acquisition. |

**Unsupported remainder/status.** SQ3 has a defensible bounded negative/inconclusive answer, not a universal affirmative or impossibility claim. Explicit temporal shifts from exposé §5.6, predictive audio robustness, quality/content decomposition, independent field validation and prospective reliability remain unsupported. Wider existing folds could improve coverage but cannot restore pristine test status. These are scope boundaries to approve, not experiments automatically required to rescue a negative finding.

## SQ4 — evaluation beyond accuracy

> How can multimodal architecture performance be evaluated beyond accuracy, including robustness, interpretability, modularity, and practical usability?

**Literature and findings.** [Saito/Rehmsmeier](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432) motivate PR alongside class balance; [Guo et al.](https://proceedings.mlr.press/v70/guo17a/guo17a.pdf) motivate calibrated probabilities; [Gneiting/Raftery](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) distinguish proper probability scoring. [Varma/Simon](https://link.springer.com/article/10.1186/1471-2105-7-91), [Kapoor/Narayanan](https://arxiv.org/html/2207.07048v1), [Bengio/Grandvalet](https://jmlr.org/papers/v5/grandvalet04a.html) and [Pineau et al.](https://jmlr.org/papers/v22/20-303.html) motivate selection, dependence and provenance scrutiny. These methodological precedents do not certify this repository's correctness. TASK3 records which were full-text versus record/abstract checks.

**Practical implementation/differences.** Per-protocol AP/AUROC, balanced decisions, Brier/ECE, training-selected thresholds, recording/run pairing, seed descriptions, fault-response/weight ablations, explicit fallback/abstention, component costs and saved provenance. R10 audio/OOD gates prevent unsupported performance claims; P00/P11/P12/P13 establish task/measurement feasibility limits. R15 selective prediction uses computational confidence and training-side cutoffs, not human ambiguity labels.

**What differences let us investigate.** Whether a ranking gain improves probability quality or decisions, which inputs a gate functionally uses, what branch modularity permits, and where resource/measurement/split constraints bind. Reported timing excludes an observed acquisition window and uses cached/warm components; it cannot certify online latency. Source/manifest preservation is traceability evidence, not a clean-environment execution reproduction.

**What was measured/results contribute.** V: core eight metrics, confusion counts, fold-threshold metadata and saved cohort/split agreement. R: F2 lower Brier than U1/F1 while F2−F1 AP unresolved; anchored AP gain coexists with lower recall/higher ECE. R: about505ms sequential component sum F2 versus26ms statistics on three warm examples; October low-dimensional pilot ran CPU-only with reported resources. Reported label reviews remain selected and separate: PHM42/38, REASSEMBLE64/59.

| Evaluation element | Category | Supported contribution / unsupported extension |
|---|---|---|
| Per-protocol metric/calibration/decision tables | Known-method implementation + empirical trade-offs | Shows why AP/accuracy, calibrated probabilities and useful decisions differ. No chosen plant cost function or alarm policy validated. |
| Gating/context interventions | Descriptive empirical observation | Demonstrates functional sensitivity; weights are not causal importance or calibrated trust. Broader attention-explanation debate does not settle our specific interpretation. |
| Availability interfaces/component accounting | Task-specific implementation + bounded feasibility observation | Supports inspectable modular evaluation, not branch replacement without recalibration or measured operator usability. |
| Group/identity/provenance checks | Evidence/assurance contribution | Bounded consistency verified; no “leakage-free” or fully reproduced certification. Repeated assessment exposure remains. |
| PHM supervision and signal feasibility | Informative negative/inconclusive evidence | Demonstrates why target validity and experimental unit matter; not retrospective proof the whole modality lacks signal. |

**Unsupported remainder/status.** SQ4 is partly answered with a substantial, defensible evaluation framework. Prospective use, operator study, field reliability, independently adjudicated population labels, higher-level acquisition independence and complete producing-source reconstruction remain unknown/untested. No new experiment is necessary merely to label those limits accurately.

## Claim decisions controlling final prose

| Claim | Evidence verdict | Required final wording/disposition |
|---|---|---|
| “F2 outperforms F1” | Discrimination inconclusive; R probability-score contrasts favorable | Specify Brier/ECE and post-hoc status. Do not claim reliable AP/AUROC superiority. |
| “Visual information caused the F2 gain” | Predictive increment verified; causal/unique complementarity not isolated | Say the combined pipeline improved over the selected sensor baseline; report descriptive rescues separately. |
| “Gating/adaptation failed” | Original gate criteria unmet; later anchored clean positive exists | Name the exact family and metric. Reject universal negative wording. |
| “Quality is reliability” | U; no completed identifying controls | Use “observable quality proxies/context”; coefficients are not trust percentages. |
| “All-Transformer architecture” | Contradicted by retained forward paths | Frozen pretrained CNN + statistics; separately tested scratch/spatial Transformer candidates. |
| “Temporal modelling improved performance” | Location/aggregation gain reported; learned-order gain unresolved | Attribute V3 to last-quarter observation pooling, not learned sequence order. |
| “PHM damage labels validated” | U physical validity; artifact truth consistency V | Call provisional image-area targets. Do not cite REASSEMBLE64-clip agreement as PHM validation. |
| “PHM padding bug explains failure/is harmless” | U output impact; source-level concern V | Retain concern and avoid causal/harmlessness claims. No correction or revised score here. |
| “LOEO/new seeds mean independent final test” | Contradicted by development history | Say grouped/exposed exploratory assessment; neither more folds nor seeds erase exposure. |
| “Synthetic robustness is external industrial validation” | Untested external population | Name operators, groups, realizations and coverage; MSM remains optional/unrun. |
| “Fully reproducible/leakage-free” | U beyond bounded checks | State exactly which arithmetic/metadata checks passed and which historical evidence is only reported. |
| “Novel because implementation differs” | Not established | Remove novelty/first-use wording. Research value lies in justified adaptation, measurement and critical comparison. |

The central thesis result is the **original architecture/fusion comparison** with a strong static reference, not the largest AP discovered later and not an assumed quality-aware win. Supporting findings enrich that conclusion without changing which procedure produced it. The [chapter plan](THESIS_CHAPTER_PLAN.md) follows this hierarchy. **STOP; no new model experiment is authorized by this ledger.**
