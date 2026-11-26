# Proposed manuscript revisions for review

**PROPOSED; none applied.** Locations refer to the current working-copy manuscript, whose hashes are in [manuscript_before.json](manuscript_before.json). Section titles are the durable anchors; line numbers are navigation aids for this snapshot. Evidence classifications and exact sources are in the linked analyses. Replace existing interpretation where indicated rather than append a second version of the same argument.

The manuscript already contains most numerical comparisons and many appropriate cautions. The revisions concentrate on the logical connection between them, the newly verified F2 distinction, two consequential chronology omissions and the later ViFailback evidence. Existing figures/tables need not be expanded into a larger leaderboard.

## R01 — Explain what the architecture publications actually justify

**Location:** [Chapter 2](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters/02_literature_review.tex), §§2.4.2–2.4.3, lines 104–113. Replace general bridging language after the existing paper-specific results; retain their exact benchmark context.

**Weakness:** the papers motivate components, but the relationship between their original tasks and the thesis's altered components is dispersed across Chapters 2–3.

**Evidence:** [L1–L2](ARCHITECTURE_AND_LITERATURE.md); original RT-DETR and PatchTST methods inspected; [C1–C4](SCIENTIFIC_CROSS_MAPPING.md) provide task-specific results.

**Proposed text:**

```latex
These publications motivate candidate representations rather than establish
their suitability for completed-action failure classification. RT-DETR's
detector results concern a pipeline extending beyond the CNN features used
in the core comparison \citep{Zhao2024RTDETR}. PatchTST's forecasting evidence
likewise does not validate the scratch-trained classifier, normalization
and aggregation used here \citep{Nie2023PatchTST}. Chapter~3 specifies those
adaptations; Chapter~6 tests their consequences through training-budget,
aggregation and fusion comparisons.
```

**Why stronger:** makes the literature-to-experiment link explicit without transferring benchmark superiority to a different task.

**Remaining limits:** neither paper supplies a historical reason for choosing this exact checkpoint or proves it optimal. No new general model ranking is proposed.

## R02 — Supply the missing foundation for F2

**Location:** Chapter 2 §2.5.3, “Prediction-Level and Late Fusion,” line 139; replace the final generic sentence about a fitting bank with the following.

**Weakness:** the existing discussion identifies the need for a fitting bank but lacks a direct foundational stacking reference.

**Evidence:** [L4](ARCHITECTURE_AND_LITERATURE.md); Ting and Witten's original 1999 paper; Section 1B protocol/source. This is the single proposed bibliography addition.

**Proposed text:**

```latex
Stacked generalization constructs a second-stage learning problem from
first-stage predictions, using cross-validated outputs rather than their
in-sample counterparts \citep{Ting1999Issues}. In the present application,
the exclusions must additionally preserve recording groups. F2 fits a
logistic map to branch probabilities; it is neither a convex weighted
average nor a direct measure of modality importance. Its interpretation
depends on the construction of the fitting bank, calibration and subsequent
selection, not merely on the combiner's name.
```

**Why stronger:** connects F2 to a relevant original method while identifying the application-specific validity requirements.

**Remaining limits:** the cited paper evaluates a different combiner. It does not validate C=1, the thesis's groups or every meta-validation dependency. The proposed key must be added from [proposed_bibliography.bib](proposed_bibliography.bib) before compilation.

## R03 — Separate quality-aware motivation from an established reliability mechanism

**Location:** Chapter 2 §2.6.4, “Quality-Aware and Uncertainty-Aware Fusion,” line 173; use as the closing interpretation, replacing any generic claim that dynamic allocation should improve reliability.

**Weakness:** the link from theoretical quality-aware fusion to the implemented proxy-conditioned gates needs an explicit inferential boundary.

**Evidence:** [L5](ARCHITECTURE_AND_LITERATURE.md), original QMF and Ovadia papers; [C6–C7](SCIENTIFIC_CROSS_MAPPING.md).

**Proposed text:**

```latex
The theoretical motivation for dynamic fusion depends on how its weights
relate to unimodal errors; observable quality descriptors do not establish
that relationship by themselves \citep{Zhang2023QMF}. Clean calibration is
also insufficient evidence of probability reliability after a distribution
shift \citep{P008}. The relevant empirical question is therefore whether
conditioning improves decisions against a static model with comparable
corruption exposure, while preserving an acceptable level of clean
performance. Changes in gate weights alone cannot answer that question.
```

**Why stronger:** identifies the testable implication rather than treating a theoretical motivation as validation of a different implementation.

**Remaining limits:** the thesis does not test QMF's assumptions directly, and the matched-exposure comparisons still differ in capacity or optimization.

## R04 — Preserve historical selection without inventing retrospective intent

**Location:** [Chapter 3](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters/03_foundations.tex), §3.6 “Component Selection Criteria and Implementation Mapping,” line 121; replace the generic selection rationale with the following synthesis while retaining any required dataset-specific details.

**Weakness:** practical choices, literature-based reasons and later experimental evidence can otherwise appear to be one historical decision.

**Evidence:** [Section 1 protocol](../../implementations/REASSEMBLE/docs/SECTION_1_PROTOCOL.md), [Section 1B protocol](../../implementations/REASSEMBLE/docs/SECTION_1B_PROTOCOL.md), [L1–L5](ARCHITECTURE_AND_LITERATURE.md).

**Proposed text:**

```latex
The initial REASSEMBLE protocol fixed a bounded comparison: a pretrained
visual backbone with a fitted head, compact sensor statistics and a
scratch-trained patch encoder. It explicitly limited what the short neural
training budget could establish. The recorded choices define the historical
starting point; the available record does not establish that this backbone
was selected after a comparative search over all plausible alternatives.

Scientifically, these choices test different restrictions on the retained
information. Frozen spatial features separate head fitting from backbone
adaptation, statistical summaries restrict temporal detail, and a patch
encoder permits learned sequence summaries. Later experiments test specific
limitations of that starting point. Their outcomes justify conclusions
about the evaluated recipes, not retrospective reasons for the original
selection or a final architecture combining their strongest components.
```

**Why stronger:** gives architectural decisions a falsifiable role while preserving the sequence of decisions and findings.

**Remaining limits:** limited budgets are documented; a particular hardware-cost rationale for every initial choice is not. Do not add one without a contemporaneous source. Section 1B's statistics selection followed initial results and must remain visible in Chapter 6's selection history.

## R05 — Give the statistical representation an exact scientific role

**Location:** Chapter 3 §3.3.1, line 34; replace the REASSEMBLE-specific paragraph, retaining the separate MSM/PHM distinctions.

**Weakness:** “ten statistics” is numerically exact but leaves the information retained and discarded too implicit. Generic sensor literature does not validate this precise vector.

**Evidence:** [L3](ARCHITECTURE_AND_LITERATURE.md); inspected `statistics()` implementation; [C1–C2](SCIENTIFIC_CROSS_MAPPING.md).

**Proposed text:**

```latex
REASSEMBLE uses ten summaries for each of 22 progress-resampled channels:
mean, standard deviation, median, extrema, lower and upper quartiles,
range, RMS and linear progress slope. The resulting 220 features retain
location, spread, magnitude and a coarse trend while discarding most
temporal order. This restriction makes the representation a useful
reference for the learned sequence model; it does not assume that temporal
information is irrelevant. Its adequacy is tested empirically, including
whether the PatchTST and statistical predictions improve when combined.
```

**Why stronger:** justifies the baseline through an explicit information restriction and a corresponding experiment.

**Remaining limits:** individual statistics are not causal features, and progress-resampled RMS is not a claim about preserved physical frequency content.

## R06 — Replace the overly broad F2 recalibration caveat

**Location:** [Chapter 6](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters/06_reassemble.tex), §6.7.6 “Interpretation and Comparison Limits,” first paragraph at line 153. Retain its second paragraph on the original versus anchored gates.

**Weakness:** the draft treats the visual contribution as merely plausible until a sensor-only second-stage control exists. Saved-model arithmetic now establishes a narrower but direct ordering contribution.

**Evidence:** [new F2 audit](F2_VERIFICATION.md) and [results.json](f2_verification/results.json), **VERIFIED here**. Existing paired intervals remain attributed to E047/E048, not newly recalculated uncertainty.

**Proposed replacement:**

```latex
Independent recomputation separates within-fold ordering from cross-fold
score alignment. All five saved F2 sensor coefficients are positive, so
omitting the visual term while retaining the fitted intercept and sensor
coefficient, $q_{s,k}=\sigma(b_k+\alpha_{s,k}p_s)$, preserves the sensor
branch's ranking within fold $k$. The reduced scores reproduce its
within-fold AP and AUROC. Including vision improves AUROC in all five
folds and AP in four; the remaining AP difference is $-0.00469$.
The visual term therefore supplies beneficial ordering changes on the
evaluated actions beyond a strictly increasing transformation of the same sensor
probability, although the AP improvement is not uniform.

Pooled sensor, reduced-score and complete-F2 AP are .42939, .43092 and
.44730. The reduced score changes pooled AP without changing any within-fold
ranking, because fold-specific transformations can reorder cases across
folds. This omission is an arithmetic diagnostic of a jointly fitted model,
not an independently fitted sensor-only second-stage control. It neither
uniquely attributes the pooled gain to vision nor estimates causal modality
importance. The folds also share training populations. Historical paired
intervals condition on the fitted models and omit the repeated selection
history; they do not establish population-wide superiority or an advantage
of F2 over equal averaging.
% Review source: scientific_cross_mapping_20261125/F2_VERIFICATION.md
% Add this audit to the existing evidence register if this revision is accepted.
```

**Why stronger:** recognizes evidence actually present while retaining the control's legitimate purpose. It prevents calibration, ranking and causal information claims from being interchanged.

**Remaining limits:** direct original visual-prediction-file parity is unavailable; the audit verifies Section 1B to Section 2 reuse. No training, bootstrap or independent-population validation was repeated.

**Required consistency replacements:**

- §6.6.5, line 103, replace the sentence beginning “Isolating the contribution of video” with: `The contribution of the saved visual term to within-fold ordering is examined in Section~6.7.6; attribution of the complete pooled gain remains limited by the absent matched sensor-only second-stage control.`
- §6.7.1, line 109, replace the broad attribution sentence with: `The comparison changes both the inputs and the fitted probability map. Within-fold ordering can nevertheless identify a visual contribution beyond strictly increasing transformation of the sensor score, while a matched sensor-only second-stage model remains necessary for a stronger attribution of the full pipeline contrast.`
- Chapter 2 §2.8.3, line 228, replace its second-stage caveat with: `A fitted combiner should be assessed for incremental within-fold ordering as well as pooled performance; a matched single-input second-stage control further limits ambiguity about its additional fitted map.`

These replace repetitions of the old caveat; they are not three new standalone discussions.

## R07 — Convert the follow-up catalogue into a scientific argument

**Location:** Chapter 6 §6.10 “Study Synthesis and Remaining Questions,” lines 233–236; replace its two paragraphs. Keep the detailed results in §6.9.

**Weakness:** the draft lists favorable follow-ups and correctly warns against combining them, but does not fully explain their joint implications or the explanations they constrain.

**Evidence:** [C1–C7](SCIENTIFIC_CROSS_MAPPING.md); E040/E042/E047/E048/E062 and the new F2 audit.

**Proposed replacement:**

```latex
The controlled comparisons distinguish representation suitability from
complementary information and from the ability of a fusion rule to use it.
Longer PatchTST training improves the temporal branch but does not close its
deficit to statistics under the tested recipe. Training duration therefore
contributes to the original result without fully explaining it. Yet combining
the two sensor representations improves AP over statistics alone: weaker
standalone prediction does not imply that a representation is redundant.
The visual branch provides a related result. Its contribution to F2 includes
verified within-fold ordering improvements, while the comparison of F2 with
equal averaging remains inconclusive.

Changing visual pooling improves both the selected visual model and its
separate static-fusion comparison. Because last-quarter and whole-action
pooling have the same fitted head size, increased parameter count cannot
explain that contrast. Concentrated outcome cues or reduced dilution remain
plausible explanations, but the experiment does not isolate their mechanism
or establish prediction before completion. The spatial-encoder and matched
adaptation studies further show that adding components or updating weights
does not automatically improve the downstream combination.

Fusion formulation also matters. Anchored context-dependent adjustment
improves clean AP over both its static anchor and constant-adjustment control,
but changes in recall and calibration qualify that gain. Matched corruption
exposure leaves the principal adaptive robustness contrasts unresolved.
Thus, a clean benefit and visible changes in coefficients do not establish
that the model recognizes unreliable inputs. Known absence is a separate
case because the tested routing rules return the same surviving prediction.

These interventions were evaluated separately on an already examined
population. No experiment combines boundary pooling, the same-sensor hybrid
and anchored adaptation. Their results identify distinct limitations of the
starting pipeline; they do not constitute an independently confirmed final
architecture. Uncertainty remains about new recordings, natural sensing
faults, earlier prediction horizons and selection beyond the fixed fits.
```

**Why stronger:** builds a sequence of bounded deductions instead of another performance summary.

**Remaining limits:** the hybrid's fold analysis and follow-up intervals are reported checks; only the core F2 arithmetic is newly recomputed. Statistical complementarity is conditional usefulness, not causal information decomposition.

## R08 — Link representation findings back to SQ1 without overclaiming

**Location:** [Chapter 9](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters/09_discussion.tex), §9.1, replace the second paragraph beginning “Across 4,530 completed REASSEMBLE actions,” line 11. Keep the PHM and external-study paragraphs.

**Weakness:** the answer foregrounds the original short-budget ranking and only briefly mentions pooling/adaptation, leaving the longer-budget and same-sensor hybrid implications underused.

**Evidence:** [C1–C4](SCIENTIFIC_CROSS_MAPPING.md), [L1–L3](ARCHITECTURE_AND_LITERATURE.md).

**Proposed replacement:**

```latex
REASSEMBLE qualifies representation suitability by the information retained
and the fitting budget. Statistics remain stronger than the tested
scratch-trained PatchTST after its training budget is extended, but their
combined predictions improve over statistics alone. The result supports
useful differences between these sensor representations without making the
temporal model the stronger standalone predictor. For vision, the core
RT-DETR checkpoint supplies frozen CNN maps rather than an executed detection
Transformer. Changing the pooling of those maps improves a separate
completed-action comparison at unchanged head size. This implicates the
aggregation rule without isolating outcome visibility from other content
differences. Matched adaptation comparisons do not establish a consistent
fusion AP improvement. SQ1 is therefore answered for particular component,
aggregation and budget choices; it remains open for audio and pretrained
time-series weights, and for prediction before the operation is complete.
```

**Why stronger:** directly answers suitability while preserving the distinction between standalone strength, incremental usefulness and untested representations.

**Remaining limits:** no general conclusion about Transformers versus CNNs or all frozen versus adapted representations follows.

## R09 — Carry the refined F2 interpretation into comparative fusion

**Location:** Chapter 9 §9.2, replace the paragraph at line 22 beginning “Attributing that gain specifically to visual information.”

**Weakness:** it now understates the directly verified contribution and risks contradicting revised Chapter 6.

**Evidence:** [F2 verification](F2_VERIFICATION.md); existing formulations in Chapter 3.

**Proposed replacement:**

```latex
The F2 gain includes a verified within-fold contribution from vision:
AUROC improves in five folds and AP in four when the saved visual term is
included. It therefore extends beyond fold-specific strictly increasing transformation
of the sensor scores. Attribution of the full pooled gain remains limited
by jointly fitted coefficients and the absent matched sensor-only second
stage. The original gates also differ from F2 in their logit inputs and
constraints, while concatenation changes both representation and capacity.
These comparisons establish properties of fitted systems, not an isolated
causal effect of adaptivity or visual information.
```

**Why stronger:** preserves the central empirical finding without removing model-comparison confounding.

**Remaining limits:** four positive fold AP changes do not imply uniform benefit; fixed-fit intervals and repeated cohort exposure remain relevant.

## R10 — State exactly what matched robustness controls resolve

**Location:** Chapter 9 §9.3, replace the paragraph beginning “A later context-conditioned adjustment,” line 37. Keep numerical tables in Chapter 6.

**Weakness:** the existing paragraph is accurate but does not explain why the constant control and matched exposure change the strength of the argument.

**Evidence:** [C6–C7](SCIENTIFIC_CROSS_MAPPING.md); [L5](ARCHITECTURE_AND_LITERATURE.md).

**Proposed replacement:**

```latex
The anchored follow-up narrows the clean-data explanation: its AP gain
exceeds that of both the unchanged F2 anchor and a constant-adjustment
control. This supports the evaluated context-dependent function, while
leaving capacity and the meaning of its context variables unresolved.
Giving static and adaptive models comparable corruption exposure then
addresses a different question. Both that comparison and the later
quality-interaction pilot leave their primary robustness increments
unresolved, including the stated clean-performance requirements. These
results cannot be collapsed into either a general success or a general
failure of gating. They identify a clean benefit for one construction
and insufficient evidence that the tested quality conditioning reliably
improves predictions under degraded but present inputs.
```

**Why stronger:** identifies which alternative explanation each control addresses, and separates uncertainty from a negative universal finding.

**Remaining limits:** matching exposure is not full capacity/optimization matching; fixed synthetic faults do not establish natural-fault robustness.

## R11 — Strengthen cross-dataset interpretation without causal storytelling

**Location:** Chapter 9 §9.6 “Lessons Across Datasets and Limits of Comparison,” after the existing table and in place of the paragraph beginning “MSM and HANDOVER reused,” line 77.

**Weakness:** the draft distinguishes reuse and transfer correctly but leaves the combined scientific interpretation too brief. Its table's ViFailback boundary is also stale.

**Evidence:** [C8](SCIENTIFIC_CROSS_MAPPING.md) and [chronology/update](RESEARCH_CHRONOLOGY.md); dataset-specific handoffs and 24 November closure.

**Proposed replacement:**

```latex
The reversal of the within-study fusion comparison across datasets supports
a conditional claim. The outcome definition, observation window, branch
representations and fitting procedure jointly determine whether the
evaluated combination helps. These factors differ together across studies;
the score pattern cannot identify one of them as the cause. In particular,
weak visual performance can reflect limited outcome visibility or an
unsuitable representation, while a strong sensor model can leave little
usable improvement for a particular fusion rule. These remain explanations
to distinguish, not mechanisms established by the cross-dataset comparison.

Class distribution and assessment also change the question. Failure AP in
REASSEMBLE and MSM cannot be equated with ViFailback's both-class macro AP,
and HANDOVER's missing participant mapping prevents its stipulated learned
fusion comparison. Architecture reuse with new dataset-specific fits is
distinct from transferring REASSEMBLE-supervised CNN weights and fitting
new ViFailback components. The latter is supervised representation transfer,
not evaluation of an unchanged predictor. Later ViFailback full-backbone
comparisons add one-fold adaptation evidence with inconclusive effects;
they do not establish general target-adaptation or cross-dataset superiority.
```

**Table cell replacements:**

- REASSEMBLE “Supported lesson”: `Stacking improves on sensors, including within-fold visual ordering; advantage over averaging unresolved`.
- REASSEMBLE “Principal boundary”: `Exposed cohort, fixed-fit uncertainty and pooled-score attribution`.
- ViFailback “Principal boundary”: `Full-backbone coverage limited to one fold; corruption untested`.

**Why stronger:** specifies what heterogeneous outcomes establish, and what competing explanations remain unidentified.

**Remaining limits:** class prevalence alone does not explain the direction of within-study fusion effects. Do not describe architecture reuse as source-weight transfer where the study used only generic pretrained features.

## R12 — Correct PHM's negative-control terminology

**Location:** [Chapter 5](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters/05_phm.tex), opening paragraph, line 4; replace the sentence calling PHM a “methodological negative control.”

**Weakness:** the phrase implies an intentionally designed negative-control experiment, unsupported by the recorded historical purpose.

**Evidence:** [PHM chronology](RESEARCH_CHRONOLOGY.md), Chapter 5's existing target construction and E004/E023. Initial selection reason remains unknown.

**Proposed replacement:**

```latex
PHM provides a diagnostic case concerning proxy-target validity and the
limits of architecture comparison. Its methodological value emerged through
the investigation; it was not designed as a negative-control experiment.
Predicting a photograph-derived target does not by itself validate physical
damage, and an unresolved comparison with a constant baseline is a result
about that evaluated task rather than proof that a modality should fail.
```

**Why stronger:** preserves the scientific value of the study without retrospectively changing its intent.

**Remaining limits:** this is not an independent validation of the photographic proxy. Retain the separate principal and leakage-affected diagnostic protocols.

## R13 — Complete the consequential chronology economically

**Location:** [Appendix G](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/appendices/G_chronology.tex). Add the PADERBORN paragraph before the September follow-ups; add REBOOT and the milling identity sentence in the external-study chronology. Qualify the existing Intel sentence as below.

**Weakness:** omitted studies remove evidence about why some tasks stopped before a final architecture comparison. “Milling Dataset” could be mistaken for another independent dataset.

**Evidence:** [chronology with exact source paths](RESEARCH_CHRONOLOGY.md); PADERBORN run `20260926T224859Z`; REBOOT decision v2 dated 28 October; Intel audit and MSM legacy README.

**Proposed additions/replacements:**

```latex
The PADERBORN investigation exposed a consequential dependence on the
definition of independence. Severity was fixed per bearing. The requested
condition-only comparison supported a vibration improvement, whereas the
later stricter bearing-and-condition comparison left that improvement
unresolved. The report's promotion of the stricter split is a protocol
change whose chronology must remain explicit. Bearing-identity prediction
made identity-related signal plausible, without proving that it explained
all performance. The subsequent distillation stage was not executed.

The REBOOT investigation stopped at a different boundary. Its 28 October
decision admitted no normal/abnormal windows or groups under the proposed
supervised protocol for the inspected annotation release, while independent
visual-observability review remained pending. No model-performance estimate
followed. This was a label and protocol feasibility decision, not a negative
architecture result.

Earlier records titled ``Milling Dataset'' belong to the MSM investigation;
they are not an additional independent dataset evaluation. Small-pilot
eligibility failures and later full-cohort results retain their separate
populations and protocols.
```

**Intel sentence replacement:**

```latex
The Intel audit identified intended welding categories without independently
verified defect ground truth, class-dependent modality availability and
sessions crossing the supplied partitions. Prior inspection of the proposed
holdout further prevented an untouched confirmatory interpretation; audit
exposure should not be equated with evidence that every observation trained
a model.
```

**Optional screening sentence, only if needed to explain narrowing:**

```latex
Other screening decisions concerned modality eligibility: RoboFAC lacked
the required real numerical counterpart, FAILURE supported only a proposed
RGB--audio pilot for a different modality question, and CRIA was removed at
the researcher's request.
```

**Why stronger:** distinguishes target validity, independence, feasibility, researcher choice and unexecuted work. These are material scientific decisions without becoming new principal chapters.

**Remaining limits:** the PADERBORN protocol change is not automatically an approved scope amendment; no “all performance was identity leakage” claim is warranted. The screening sentence does not claim that FAILURE's pilot ran.

## R14 — Amend ViFailback's dated execution boundary

**Location:** [Chapter 8](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters/08_vifailback.tex), §8.7 completion account/table at lines 44–66 and §8.7.3 after the existing frozen/donor 100-epoch pilot. Update dependent deferral statements at §§8.1, 8.5, 8.8 and 8.9.

**Weakness:** the draft's earlier cutoff is now incomplete: it says target-CNN adaptation was not evaluated. The later closure contains a completed, bounded comparison.

**Evidence:** [24 November closure and documentary conflict](RESEARCH_CHRONOLOGY.md). These performance/uncertainty results are **REPORTED from that closure**, not newly recomputed here.

**Proposed passage:**

```latex
A later evidence closure dated 24 November 2026 extends the earlier
reporting cutoff. It records 79 completed fits out of 111 planned:
36 FROZEN20, 36 DONOR20, four FULL20, and one each for FROZEN100,
FULL100 and DONOR100. The four FULL20 fits complete the outer-final and
three inner roles for seed 42, outer fold 0; the other 32 planned FULL20
fits remain unexecuted after the researcher-requested stop. Completion
of this bounded comparison does not complete the original matrix.

On the same 1,107 assessment episodes, FULL20 minus FROZEN20 changes
visual macro-AP by $+0.004946$ $[-0.027460,0.040927]$ and F2 macro-AP
by $-0.009260$ $[-0.026854,0.005016]$. The separate FULL100 minus
FROZEN100 pilot gives $-0.006662$ $[-0.027982,0.027078]$ for vision and
$+0.005040$ $[-0.019473,0.029255]$ for F2. These reported paired
task-cluster intervals are inconclusive, not equivalence results.
The 20-epoch comparison uses its complete inner-OOF bank; the 100-epoch
pilot uses a distinct predefined meta bank. Their differences do not
isolate training duration. Broader full-backbone stability and controlled
corruption effects remain unmeasured.
% Review source: 20261124 completed_scope_analysis/RESULT_ANALYSIS.md
% and the timestamped FINAL_STATUS.json; add to the existing evidence register.
```

**Replacement status table content:** use the six-condition fit-coverage table in [the chronology](RESEARCH_CHRONOLOGY.md). Retain the complete frozen/donor results and historical primary results separately. Do not silently replace their metric rows with the matched study's rows or retain a stale aggregate fusion-assessment count.

**Exact consistency wording:**

- §§8.1/8.5: replace “no target-CNN adaptation” assertions with `The 24 November closure includes bounded target-CNN adaptation for seed 42, outer fold 0; the wider FULL20 matrix remains incomplete.`
- §8.8: `The completed frozen/donor studies test reuse and supervised representation transfer; the later one-fold FULL20 and FULL100 comparisons add inconclusive target-adaptation evidence.`
- §8.9: `Whether target adaptation produces a stable benefit across tasks and seeds remains open; the completed one-fold contrasts do not resolve it.`
- Chapter 9 §9.7, line 87: `ViFailback's later closure includes one-fold full-backbone comparisons with inconclusive effects; broader adaptation coverage and corruption effects remain untested.`
- Appendix G final sentence: `The 24 November closure subsequently adds bounded full-backbone comparisons while retaining the unfinished wider matrix.`

**Why stronger:** recognizes completed work without treating an administrative stop as scientific failure or a partial comparison as full coverage.

**Remaining limits:** new evidence extends the manuscript cutoff and must be visibly dated. Bootstrap checks are attributed to the prior audit. Its stale prospective inner2 sentence is superseded by the timestamped completion receipt, not treated as a reason to resume any job.

## R15 — Make the concluding contributions emerge from the comparisons

**Location:** [Chapter 10](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/chapters/10_conclusion.tex), §10.2 “Supported Contributions,” lines 15–22; replace the four existing SQ paragraphs.

**Weakness:** the current conclusion emphasizes initial rankings and gives less weight to the most informative controlled follow-ups. It can more explicitly identify what each original question has and has not answered.

**Evidence:** [integrated RQ mapping](SCIENTIFIC_CROSS_MAPPING.md), [architecture evidence](ARCHITECTURE_AND_LITERATURE.md), [F2 audit](F2_VERIFICATION.md), [chronology](RESEARCH_CHRONOLOGY.md).

**Proposed replacement:**

```latex
For representation suitability (SQ1), the contribution is a qualified
comparison of information restrictions and fitting choices. Longer
PatchTST training improves the tested temporal predictor without overtaking
statistics, while their combination improves on statistics alone. Changing
visual pooling improves a separate comparison without increasing head size.
These results show that standalone strength, aggregation and complementary
information require separate assessment. They do not identify a universally
best encoder; audio and pretrained time-series weights remain unresolved.

For comparative fusion (SQ2), the common REASSEMBLE cohort supports a
modest gain over its sensor branch, including a verified visual contribution
to within-fold ordering. Superiority of logistic stacking over equal
averaging remains unresolved. The lower stacking performance in MSM and
ViFailback, and the lower averaging performance in HANDOVER, limit any
general recommendation. HANDOVER's learned-fusion comparison remains
unexecuted because its mandatory participant grouping could not be formed.
The experiments compare the implemented scalar gates and feature fusion,
not every form of cross-modal attention proposed by the original question.

For robustness (SQ3), explicit routing handles known absence, but identical
fallback is not evidence of adaptive superiority. Anchored adaptation
improves clean AP in a distinct exploratory comparison; matched corruption
exposure does not establish its general robustness advantage. The later
quality-interaction pilot is also inconclusive on its primary contrast.
No single experiment combines these adaptive models with the strongest
pooling and same-sensor hybrid results.

For evaluation beyond accuracy (SQ4), the work demonstrates why target
provenance, group dependence, class-specific ranking, probability error,
threshold consequences and compute accounting belong in the same argument.
Feasibility gates and incomplete comparisons are retained because they
define what can be claimed. Inspectable coefficients and component timings
provide bounded evidence; they do not establish causal explanations,
operator usability or end-to-end deployment performance. The evaluation
method is substantially developed, while those practical questions remain
only partially answered.
```

**Why stronger:** contributions follow the controlled evidence, including informative negative and inconclusive results, rather than an obligation to recommend a winning architecture.

**Remaining limits:** preserve the original title and questions; this does not convert completed-action classification into online industrial anomaly detection or validate weld quality.

## R16 — Refine the main answer and modularity claim

**Location:** Chapter 10 §10.1, line 9 final attribution sentence and line 13 paragraph beginning “Taken together.”

**Weakness:** the first repeats the overbroad F2 caveat; the second can imply that modularity itself was the experimentally superior treatment.

**Evidence:** [F2 audit](F2_VERIFICATION.md), [C8 and RQ mapping](SCIENTIFIC_CROSS_MAPPING.md), research chronology.

**Proposed F2 sentence replacement:**

```latex
The saved visual term improves within-fold AUROC in five folds and AP in
four; the absence of a matched sensor-only second stage still limits
attribution of the full pooled gain.
```

**Proposed modularity paragraph replacement:**

```latex
Together, the studies motivate keeping target construction, representation,
aggregation, fusion and assessment separately inspectable and replaceable.
This is a modular design recommendation arising from heterogeneous tasks
and validity requirements, not experimentally demonstrated superiority of
modularity as an architectural intervention. The empirical contribution is
a set of conditional comparisons showing when the evaluated representations
and fusion rules help, when they do not, and when the data cannot support
the intended test. The main question is therefore partially answered at
the design and evaluation level. Independent weld-quality validation and
robust prediction before operation completion remain unresolved.
```

**Why stronger:** distinguishes a defensible design lesson from an unperformed architectural ablation and gives a candid answer to the original objective.

**Remaining limits:** maintain separately the empirical result, inferred design recommendation and proposed future welding study.

## Minimal cross-chapter and appendix consistency

These are dependencies of the revisions above, not additional research tasks:

| Existing location | Concrete treatment | Evidence / limitation |
|---|---|---|
| Chapter 1 and abstract | Keep the registered title and original questions. Where the number of studies is stated, distinguish five principal/supplementary evaluation cases from feasibility investigations. Suggested sentence for Chapter 1: `Feasibility and protocol investigations additionally explain why some candidate datasets did not enter the principal comparisons.` | R13 does not create additional comparable benchmarks. The abstract does not currently assert that all ViFailback adaptation was absent; no full rewrite is needed. |
| Chapter 4 uncertainty/calibration | Add only if the distinction is not already explicit: `Fold-specific strictly increasing score transformations preserve within-fold ranking but may change ranking after predictions from different folds are pooled.` | R06; does not imply improved calibration. |
| Chapter 7 | Preserve native 1 versus 0/2 mapping, label-2 sensitivity, the 17.73% cohort prevalence and five-date interval scope. Do not replace prevalence with the pooled training-prior AP. | C8; no new metrics required. |
| Appendix B | Retain principal dataset definitions. Place PADERBORN/REBOOT in chronology, not the common performance table. | R13 avoids inflated study counts. |
| Appendix C | Retain actual CNN, final-stage and full-backbone distinctions; update ViFailback execution status only with R14's scope. | Source-defined trainability is different from evidence that each planned fit ran. |
| Appendix D | Add the five-row F2 fold table from the audit, if R06 is accepted; use zero-based fold IDs and identify this as post-hoc saved-score analysis. Add the two completed ViFailback adaptation contrasts without merging pilot protocols. | No repeated corruptions or seeds become independent subjects. |
| Appendix F / existing evidence register | Register the new arithmetic audit and the 24 November ViFailback closure, plus their source hashes. Do not invent an E-number in advance or overwrite the old evidence source. | R06/R14 comments intentionally identify proposed additions without unresolved citation macros. |
| Appendix G | Apply R13 and dated R14 sentence. | Short consequential chronology, not a new dataset chapter. |
| Appendix H | Keep HANDOVER learned stacking/gates as NOT RUN due to the mandatory identity gate. | No model-performance inference from a failed eligibility gate. |
| Appendices I/J | If required by the existing disclosure policy, record this Codex-assisted source cross-mapping, original-paper inspection and saved-score arithmetic, with the user request and review date. | This records assistance; it does not certify scientific correctness or institutional compliance. |
| Literature register | Add the one verified stacking publication as a dated targeted addition if accepted. | Do not silently change the historical 94-full-text review claim to 95; a post-review addition and an original review count are different records. |

Before application, review these proposed passages as replacements within the existing revision pipeline. No branch switch, restructuring phase, new experimental plan or automatic manuscript patch is part of this package.
