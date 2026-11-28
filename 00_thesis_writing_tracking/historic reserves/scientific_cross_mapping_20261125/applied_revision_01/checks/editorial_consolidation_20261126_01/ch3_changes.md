# Chapter 3 editorial consolidation ledger

Authoritative input: `state_A/source/chapters/03_foundations.tex`. Only redundant material was deleted; no scientific replacement prose was introduced. Retained prose, citations, equation/figure/table contents and locators remain verbatim. Source CRLF line endings are preserved.

- Approximate same-method token-word count: **7,430 → 5,952** (1,478 fewer; 19.9%). Citation commands and internal EvidenceRefs are excluded; headings, captions and table text are included. This is not a formal linguistic word count.
- Main section headings: **6 → 6**. Subsection headings: **20 → 19**; only the redundant fusion-interface recap heading was removed.
- Academic citation commands and their optional locators: identical multisets before/after. Internal `EvidenceRef` commands and locators: identical multisets. All labels and complete equation, figure and table environments: byte-identical in sequence.
- The original list of investigated fusion mechanisms is retained before “These mechanisms differ…” to preserve its antecedent. No added transitions. One sentence was deleted from a two-sentence paragraph narrating Equation `eq:gate`; its retained constraint sentence is unchanged.
- No figures or tables removed or redesigned. All original numerical configurations and trainable parameter counts remain.

## Removed material and retained counterpart

### C3-01 — state A line 26

**Reason:** The procedure is explained in the dedicated methodological section; the technical probability qualification remains.

**Retained counterpart:** Chapter 4, Model Fitting, Selection, Calibration, and Threshold Procedures: probability-calibration explanation; Chapter 3 retains the preceding sigmoid/calibration qualification.

**Removed passage (verbatim):**

```latex
Calibration requires a separate fitting or assessment procedure that examines the relationship between predicted probabilities and observed outcomes.
```

### C3-02 — state A line 32

**Reason:** Repeated methodological roadmap.

**Retained counterpart:** Chapter 4 study protocols; Chapter 3 introduction already points to dataset preparation, fitting and assessment in Chapter 4 and empirical chapters.

**Removed passage (verbatim):**

```latex
Each empirical study specifies its prediction target, input representations, trainable components, calibration procedure, and fusion interface. This prevents architectural terminology from obscuring differences between the implemented predictive systems.
```

### C3-03 — state A line 36

**Reason:** Generic introductory statement repeats the literature chapter without adding an implementation detail.

**Retained counterpart:** Chapter 2, Visual and Video Observations; Chapter 3 retains the task-specific sample/pretraining rationale immediately after this paragraph.

**Removed passage (verbatim):**

```latex
Visual observations give information about object appearance, spatial configuration, and changes occurring during a physical operation. Their predictive usefulness depends on how well the selected representation captures the relevant observations.
```

### C3-04 — state A line 42

**Reason:** Roadmap duplicates the visible section structure.

**Retained counterpart:** The retained subsection headings immediately following it.

**Removed passage (verbatim):**

```latex
This section examines convolutional feature extraction, the component structure of RT-DETR, temporal aggregation, and alternative encoder adaptation procedures.
```

### C3-05 — state A line 70

**Reason:** The concrete executed boundary is stronger than the repeated generic checkpoint explanation.

**Retained counterpart:** Chapter 3, Backbone Extraction Versus Hybrid-Encoder or Full-Detector Execution: extracted/frozen backbone and explicitly bypassed encoder, decoder and heads.

**Removed passage (verbatim):**

```latex
A pretrained object detection checkpoint therefore contains components that can be used for different downstream purposes. Its convolutional backbone can be extracted and reused independently of the detection encoder, decoder, and prediction heads.
```

### C3-06 — state A line 72

**Reason:** Repeats the warning already made concrete by the executed path.

**Retained counterpart:** Chapter 3, Backbone Extraction Versus Hybrid-Encoder or Full-Detector Execution: explicit components bypassed in the core experiment.

**Removed passage (verbatim):**

```latex
This distinction is particularly important when understanding the role of RT-DETR in a downstream classification architecture. Loading a Transformer-based detection checkpoint does not establish that every component of the original detector participates in the executed prediction path.
```

### C3-07 — state A line 86

**Reason:** Restates that complete path without adding configuration.

**Retained counterpart:** Immediately preceding two paragraphs specify frozen extraction, three pooled maps, 896 dimensions, sixteen frames, averaging and binary head.

**Removed passage (verbatim):**

```latex
The principal visual prediction path therefore processes input video frames through the frozen ResNet18-vd backbone, followed by multiscale feature extraction, spatial pooling, temporal averaging, and binary classification.
```

### C3-08 — state A line 96

**Reason:** Repeats the two just-described implementation paths.

**Retained counterpart:** The retained REASSEMBLE and PHM extraction paragraphs in the same subsection; Table tab:ch3-representations.

**Removed passage (verbatim):**

```latex
The REASSEMBLE implementation therefore uses a backbone-only extraction pathway for completed-action classification, whereas the PHM implementation uses intermediate features collected during the detector prediction path for regression.
```

### C3-09 — state A line 98

**Reason:** Concluding restatement of component scope.

**Retained counterpart:** The retained explicit bypass paragraph, PHM prediction-path paragraph, and original-publication transfer limitation in RT-DETR Architecture and Component Roles.

**Removed passage (verbatim):**

```latex
These distinctions establish which components generate the evaluated representations and prevent the results from being interpreted as equivalent applications of the complete RT-DETR detection architecture.
```

### C3-10 — state A line 104

**Reason:** Repeated introduction to spatial and temporal information.

**Retained counterpart:** Chapter 3, Convolutional Feature Extraction and Spatial Pooling: spatial pooling and frame-order restriction; following sampling/aggregation paragraphs.

**Removed passage (verbatim):**

```latex
Video observations contain spatial information within individual frames and temporal information across successive frames. The representation must determine how these two sources of information are retained.
```

### C3-11 — state A line 110

**Reason:** Repeats the already established aggregation mechanism.

**Retained counterpart:** Chapter 3, Convolutional Feature Extraction and Spatial Pooling: temporal averaging and invariance to frame order.

**Removed passage (verbatim):**

```latex
Temporal mean pooling aggregates frame descriptors without learning relationships between their positions. This makes it a low-capacity reference for predicting an outcome associated with a complete observation window.
```

### C3-12 — state A line 154

**Reason:** Generic summary precedes a more informative complete feature definition.

**Retained counterpart:** Retained exact ten-feature list and 220-dimensional configuration in the same subsection.

**Removed passage (verbatim):**

```latex
Statistical feature extraction transforms a sequence of measurements into a compact set of descriptors. Common features include measures of central tendency, dispersion, amplitude, extrema, and temporal change.
```

### C3-13 — state A line 156

**Reason:** The retained passage defines these features together with the other recorded statistics.

**Retained counterpart:** Retained paragraph starting “The mean and median describe…” after the exact REASSEMBLE feature list.

**Removed passage (verbatim):**

```latex
The mean describes the average measurement level, while the root-mean-square amplitude summarizes the magnitude of the observations. Other summaries, including standard deviation, quantiles, range, and linear trend, describe different properties of the observed measurements.
```

### C3-14 — state A line 170

**Reason:** Repeated representation-complementarity rationale.

**Retained counterpart:** Chapter 3 sensor-section introduction retains the comparison of information restrictions; Representation Learning Versus Direct Prediction retains the same-physical-stream complementarity distinction.

**Removed passage (verbatim):**

```latex
The comparison does not assume that temporal information is irrelevant. The subsequent PatchTST and statistical-feature combination investigates whether the learned temporal representation contains complementary predictive information.
```

### C3-15 — state A line 194

**Reason:** Generic patch-count introduction repeated by the more precise configuration and padding caveat.

**Retained counterpart:** Retained width/stride definition, exact configuration and unpadded patch-count qualification; Figure fig:sensor-patch-tokens.

**Removed passage (verbatim):**

```latex
The number of patches generated from a time series depends on the sequence length, patch width, stride, and padding procedure.
```

### C3-16 — state A line 198

**Reason:** The figure communicates this relationship directly.

**Retained counterpart:** Figure fig:sensor-patch-tokens and unchanged caption show patch positions, shared positions and stride.

**Removed passage (verbatim):**

```latex
For overlapping patches, the stride is smaller than the patch width. This allows neighbouring tokens to share observations and represent partially overlapping temporal structures.
```

### C3-17 — state A line 202

**Reason:** Second explanation of patch embedding and Transformer processing.

**Retained counterpart:** PatchTST Architecture retains the paragraph beginning “Each patch is transformed into a learned embedding…” and the original channel-independent mechanism.

**Removed passage (verbatim):**

```latex
A patch embedding projects the values within a subsequence into a hidden representation. Positional information and Transformer blocks subsequently support the processing of relationships between patches.
```

### C3-18 — state A line 260

**Reason:** Transition repeats what the following concrete distinction already explains.

**Retained counterpart:** The retained generic-pretrained versus target-supervised encoder paragraphs immediately following.

**Removed passage (verbatim):**

```latex
These roles determine how supervision enters the modelling procedure.
```

### C3-19 — state A line 266

**Reason:** Duplicate methodological leakage explanation; Chapter 3 retains the requirement that supervised encoding respect evaluation partitions.

**Retained counterpart:** Chapter 4, Grouped Assessment, Data Splits, and Leakage Prevention: data-dependent modelling operations, supervised representation learning and protected development populations.

**Removed passage (verbatim):**

```latex
Fitting a supervised encoder using the complete labelled population before constructing evaluation folds can introduce target information into the resulting representations, even if the final prediction head is subsequently fitted within each fold.
```

### C3-20 — state A line 268

**Reason:** Repeated methodological checklist.

**Retained counterpart:** Chapter 4, Grouped Assessment, Data Splits, and Leakage Prevention: complete fitting/preprocessing/calibration/selection dependency list.

**Removed passage (verbatim):**

```latex
The evaluation must consequently account for which samples influence preprocessing, representation learning, prediction-head fitting, calibration, and model selection.
```

### C3-21 — state A line 274

**Reason:** Repeated general motivation for baselines.

**Retained counterpart:** The retained next paragraph requiring a credible alternative under available data/fitting conditions; Chapter 2 unimodal references discussion.

**Removed passage (verbatim):**

```latex
Reference predictors provide the basis for determining whether an investigated representation or fusion mechanism contributes measurable predictive value.
```

### C3-22 — state A line 278

**Reason:** The list is already directly visible in headings and table.

**Retained counterpart:** The four retained predictor subsections and Table tab:ch3-reference-predictors.

**Removed passage (verbatim):**

```latex
The thesis therefore considers constant predictors, regularized linear models, neural prediction heads, and nonlinear conventional classifiers.
```

### C3-23 — state A line 282

**Reason:** Generic reference explanation adds no detail to the retained formulations and historical boundary.

**Retained counterpart:** Retained loss-minimizing constants and historical PHM mean-reference caveat; Table tab:ch3-reference-predictors.

**Removed passage (verbatim):**

```latex
Constant predictors establish a minimum reference for determining whether a learned model improves on a simple description of the training target distribution.
```

### C3-24 — state A line 288

**Reason:** Table preserves the same reference rule and scientific role.

**Retained counterpart:** Table tab:ch3-reference-predictors, “Class prevalence and context” row; Chapter 4 metrics discussion retains prevalence interpretation.

**Removed passage (verbatim):**

```latex
For binary classification, a constant probability can be estimated from the positive-outcome prevalence in the training population. Such a reference helps distinguish discrimination from performance associated with the target distribution.
```

### C3-25 — state A line 296

**Reason:** Generic model introduction repeated by retained definitions and table.

**Retained counterpart:** Table tab:ch3-reference-predictors, regularized linear models row; subsequent retained Ridge/logistic definitions.

**Removed passage (verbatim):**

```latex
Regularized linear models provide compact prediction mechanisms that can be fitted without learning high-capacity representations.
```

### C3-26 — state A line 308

**Reason:** Definition repeated in the dedicated fusion subsection.

**Retained counterpart:** Chapter 3, Logistic Stacking: exact F2 mechanism, equation and coefficient constraints.

**Removed passage (verbatim):**

```latex
Logistic regression can also serve as a prediction-level fusion mechanism when its inputs are the probabilities produced by separately fitted branch models. Such a model is a logistic stacker rather than a sensor representation.
```

### C3-27 — state A line 314

**Reason:** Repeated head definition.

**Retained counterpart:** Chapter 3, Common Mathematical Notation and Prediction Formulation: encoder/head distinction; following retained affine/nonlinearity/dropout description.

**Removed passage (verbatim):**

```latex
A neural prediction head maps an extracted representation to the desired regression or classification output.
```

### C3-28 — state A line 318

**Reason:** Restates the same mechanism and frozen-encoder use.

**Retained counterpart:** Retained affine-plus-nonlinear-head paragraph and frozen-extraction paragraph; Table tab:ch3-reference-predictors.

**Removed passage (verbatim):**

```latex
The prediction head allows nonlinear relationships between representation features and the target to be learned without necessarily modifying the underlying encoder.
```

### C3-29 — state A line 322

**Reason:** Repeats the implication already explicit in the fitting configuration.

**Retained counterpart:** Immediately preceding retained exact class-weighted versus unweighted cross-entropy configuration.

**Removed passage (verbatim):**

```latex
The weighting procedure is therefore another difference between the evaluated fitting configurations.
```

### C3-30 — state A line 334

**Reason:** Standard model description duplicates the table.

**Retained counterpart:** Table tab:ch3-reference-predictors retains additive tree model on binned numerical features; next paragraphs retain the stronger-sensor-comparator motivation and study-specific selection.

**Removed passage (verbatim):**

```latex
The method fits an additive ensemble of decision trees using binned feature values, enabling nonlinear relationships and interactions between statistical features to be represented without fitting a temporal sequence encoder.
```

### C3-31 — state A line 340

**Reason:** Concluding restatement of the reference role.

**Retained counterpart:** Immediately preceding retained explanation of nonlinear sensor references and the ViFailback/MSM protocol distinction.

**Removed passage (verbatim):**

```latex
These comparisons broaden the evaluation of sensor representations beyond a single classifier family.
```

### C3-32 — state A line 365

**Reason:** Repeated fusion definition.

**Retained counterpart:** Chapter 3, Common Mathematical Notation and Prediction Formulation defines feature- and prediction-level fusion; six following fusion subsections.

**Removed passage (verbatim):**

```latex
Multimodal fusion determines how information from different representations or prediction branches is combined.
```

### C3-33 — state A line 375

**Reason:** Repeated definition.

**Retained counterpart:** Chapter 3, Common Mathematical Notation and Prediction Formulation; following retained concatenation paragraph.

**Removed passage (verbatim):**

```latex
Feature-level fusion combines modality representations before the final prediction stage.
```

### C3-34 — state A line 393

**Reason:** Generic introductory sentence repeats the precise definition.

**Retained counterpart:** Immediately following retained arithmetic-mean definition and no-fitted-combination-parameters qualification.

**Removed passage (verbatim):**

```latex
Uniform averaging provides a simple prediction-level fusion mechanism.
```

### C3-35 — state A line 428

**Reason:** Repeated requirement for branch-excluded second-stage predictions.

**Retained counterpart:** Retained stacked-generalization publication paragraph; Chapter 4 grouped OOF construction.

**Removed passage (verbatim):**

```latex
The construction of the stacker’s training data is particularly important. First-stage predictions supplied to the second-stage learner should be generated using models that exclude the corresponding observation or dependence group from their fitting.
```

### C3-36 — state A line 436

**Reason:** Repeated calibration/attribution interpretation.

**Retained counterpart:** Chapter 4, Within-Fold Ranking and Pooled Prediction Scores: additional information versus additional fitted transformation.

**Removed passage (verbatim):**

```latex
Logistic stacking also introduces a distinction between the effects of additional predictive information and those of an additional fitted probability transformation.
```

### C3-37 — state A line 438

**Reason:** Duplicated detailed methodological caveat, preserved in its dedicated location.

**Retained counterpart:** Chapter 4, Within-Fold Ranking and Pooled Prediction Scores retains monotonicity, independently fitted fold maps, pooled-score effects and limitations; Chapter 6 retained empirical investigation.

**Removed passage (verbatim):**

```latex
A strictly increasing transformation of a sensor score preserves within-fold ranking. Fold-specific transformations can nevertheless change ranking after predictions from different folds are pooled. Chapter~\ref{ch:methodology} establishes the methodological implications of this distinction, while Chapter~6 examines its relevance to the evaluated F2 model.
```

### C3-38 — state A line 442

**Reason:** Repeated static/adaptive introduction.

**Retained counterpart:** Table tab:ch3-fusion-interfaces; retained gate mechanism and static/observation-dependent distinction in fusion introduction.

**Removed passage (verbatim):**

```latex
Static fusion mechanisms use a fixed integration rule or globally fitted coefficients. Context-conditioned gating introduces the possibility that the relative usefulness of each branch varies between observations.
```

### C3-39 — state A line 448

**Reason:** Remove verbal repetition of the equation while preserving its explicit coefficient constraints.

**Retained counterpart:** Unchanged Equation eq:gate; retained following sentence states nonnegative weights summing to one.

**Removed passage (verbatim):**

```latex
For the available branches, the original context-conditioned gate calculates a weighted combination of their logits and transforms the resulting value through a sigmoid function.
```

### C3-40 — state A line 462

**Reason:** Repeats the same scalar-versus-token distinction.

**Retained counterpart:** Retained paragraph on Gated Multimodal Units and multimodal attention bottlenecks explicitly states the mathematical non-equivalence to scalar gates.

**Removed passage (verbatim):**

```latex
Their implementation is therefore distinct from architectures that perform token-level cross-modal attention.
```

### C3-41 — state A line 474

**Reason:** Generic adaptive-fusion motivation repeats the cited, more precise explanation.

**Retained counterpart:** Retained QMF theoretical motivation and its conditions; earlier context-conditioned gate mechanism.

**Removed passage (verbatim):**

```latex
Quality-aware fusion is motivated by situations in which the reliability or predictive usefulness of a modality changes across observations.
```

### C3-42 — state A line 499

**Reason:** Summary sentence repeats the mechanism comparison.

**Retained counterpart:** Retained exact gate, F2 and anchored equations; Table tab:ch3-fusion-interfaces; retained empirical-reliability qualification.

**Removed passage (verbatim):**

```latex
The scientific distinction between these mechanisms concerns the information controlling the adjustment and whether the resulting adaptation improves the prediction.
```

### C3-43 — state A line 513

**Reason:** Duplicate robustness framing.

**Retained counterpart:** Chapter 4, Robustness Evaluation Design retains known absence versus degraded-available observations; Chapter 3 retains exact routing and identical-fallback limitation.

**Removed passage (verbatim):**

```latex
Modality absence represents a different reliability problem from degradation of an input that remains available.
```

### C3-44 — state A line 519

**Reason:** Restates the explicit deterministic routing procedure.

**Retained counterpart:** Immediately preceding retained explicit evaluator rule and threshold; following retained same-survivor-performance limitation.

**Removed passage (verbatim):**

```latex
This procedure establishes deterministic fallback behaviour.
```

### C3-45 — state A line 527

**Reason:** Alternative literature mechanisms are explained in the literature review and are not implementations evaluated here.

**Retained counterpart:** Chapter 2, Modality Dropout, Augmentation, and Fallback Mechanisms already distinguishes distillation and imputation.

**Removed passage (verbatim):**

```latex
Distillation provides an alternative in which information from multiple modalities during training is used to improve a model deployed with fewer inputs. Imputation instead estimates a replacement for an unavailable observation or representation.
```

### C3-46 — state A line 529

**Reason:** Repeated general comparator requirement for the just-removed literature recap.

**Retained counterpart:** Chapter 2 missing-input mechanism comparison and baseline requirement; retained reference models and Chapter 4 robustness design.

**Removed passage (verbatim):**

```latex
These mechanisms address different acquisition and deployment conditions. Their suitability requires comparison with a predictor trained directly on the available observations.
```

### C3-47 — state A line 531

**Reason:** Repeated closing distinction.

**Retained counterpart:** Retained original evaluator routing paragraph and identical-prediction limitation; Chapter 4 known-absence versus degraded-input distinction.

**Removed passage (verbatim):**

```latex
The explicit fallback investigated in this thesis provides a defined response to known absence. Recognizing unreliable but available observations remains a separate adaptive-fusion question.
```

### C3-48 — state A line 533

**Reason:** Prose repeats the immediately following figure note verbatim in substance.

**Retained counterpart:** Unchanged Figure fig:fusion-interfaces displaynote and Table tab:ch3-fusion-interfaces displaynote retain the exact branch parity, separate PatchTST comparator and calibrated-probability/logit conversion.

**Removed passage (verbatim):**

```latex
The core stacker and all three original context-conditioned gates use the statistical sensor predictor. PatchTST is evaluated separately as a sensor-only comparator in the core experiment. Each branch supplies a calibrated probability, which the original gates convert into logits before weighting.
```

### C3-49 — state A line 543

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
\subsection{Comparison of the Investigated Fusion Interfaces}
```

### C3-50 — state A line 545

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
The investigated fusion mechanisms can be distinguished according to the location of information exchange and the constraints governing their combination.
```

### C3-51 — state A line 547

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
Feature concatenation combines embeddings and learns their joint predictive use through a fitted prediction head. It does not introduce an explicitly defined observation-dependent weighting mechanism.
```

### C3-52 — state A line 549

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
Uniform averaging combines branch probabilities through a fixed arithmetic operation without learning combination parameters.
```

### C3-53 — state A line 551

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
Logistic stacking also receives probabilities but learns a globally fitted combination with an intercept and separate branch coefficients. These parameters remain fixed across observations.
```

### C3-54 — state A line 553

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
The original context-conditioned gates instead combine logits using observation-dependent normalized weights. The anchored adaptive extension operates on probabilities and modifies the coefficients of an existing static fusion model according to the available context.
```

### C3-55 — state A line 555

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
The mechanisms therefore represent different hypotheses concerning how complementary information can be used.
```

### C3-56 — state A line 557

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
Feature concatenation investigates joint prediction from combined representations. Uniform averaging tests whether a simple fixed integration rule is sufficient. Logistic stacking examines whether a fitted static combination provides additional predictive value. Context-conditioned gating and anchored adaptation investigate whether observation-dependent allocation improves the resulting predictions.
```

### C3-57 — state A line 559

**Reason:** Redundant subsection summary repeats the individual mechanisms and their retained comparison table.

**Retained counterpart:** Retained Sections 3.5.1–3.5.6 and unchanged Table tab:ch3-fusion-interfaces; exact F2, gate and anchored equations remain.

**Removed passage (verbatim):**

```latex
The experiments must account for these structural distinctions when interpreting differences in performance.
```

### C3-58 — state A line 582

**Reason:** Repeated scope statement; the stronger explicit combination caveat remains.

**Retained counterpart:** Chapter introduction retains separate component comparisons; retained final Section 3.6 paragraph explicitly rejects an unevaluated combined final architecture.

**Removed passage (verbatim):**

```latex
The investigated components form a set of candidate representation and fusion mechanisms rather than a predetermined final architecture.
```

### C3-59 — state A line 584

**Reason:** Generic introduction restates the content of the section.

**Retained counterpart:** Retained Section 3.6 historical protocol, selection-history caveat, R2–R4 mapping and implementation references.

**Removed passage (verbatim):**

```latex
Their selection is interpreted in relation to the literature-derived research design requirements, available physical observations, recorded experimental decisions, and computational conditions.
```

### C3-60 — state A line 596

**Reason:** Component-selection recap repeats the preceding technical justification.

**Retained counterpart:** Retained Sections 3.2.1–3.2.3 scientific motivation, frozen-feature feasibility, and separate hybrid-encoder investigation.

**Removed passage (verbatim):**

```latex
Frozen convolutional features investigate whether reusable spatial information supports the target-specific prediction task while allowing repeated head fitting under feasible computational conditions. The additional hybrid encoder investigates the value of further spatial feature interaction.
```

### C3-61 — state A line 598

**Reason:** Component-selection recap repeats the retained mechanisms and motives.

**Retained counterpart:** Retained Section 3.3 information restrictions, ten-feature definitions, PatchTST mechanism and Section 3.2.4 alternative aggregation rationale.

**Removed passage (verbatim):**

```latex
Statistical features investigate whether compact summaries retain sufficient information about an operation. Patch-based temporal encoding provides an alternative capable of learning representations from ordered subsequences. Alternative visual pooling procedures investigate the relevance of information retained from different parts of the observation window.
```

### C3-62 — state A line 610

**Reason:** Repeated list of literature candidates without additional technical or historical information.

**Retained counterpart:** Retained cited architectural explanations in Sections 3.2, 3.3 and the immediately preceding AST candidate/completion boundary.

**Removed passage (verbatim):**

```latex
Published studies concerning ViT, Video Swin, AST, PatchTST, and other learned representations establish alternative architectural mechanisms. The empirical evidence in this thesis instead concerns the particular convolutional, statistical, temporal, and fusion configurations that were executed.
```

### C3-63 — state A line 612

**Reason:** Repeated summary of literature motivation versus task-specific evidence.

**Retained counterpart:** Retained empirical suitability limits in cited component subsections, historical-selection caveat and implementation/experiment boundary at the end of Section 3.6.

**Removed passage (verbatim):**

```latex
Their mathematical foundations motivate the comparisons, while the empirical chapters establish their suitability under the corresponding observation windows, fitting conditions, targets, and assessment populations.
```

## Relocation and continuity

- The retained statistical-feature rationale beginning “Such features provide…” was moved intact after the 220-feature definition. This makes its antecedent explicit without changing any words.
- The brief original paragraph establishing recording-excluded branch OOF predictions and excluded outer assessment recordings is retained before the shared-bank limitation, preserving the contrast introduced by “However”.

## Scientific preservation and limits

- REASSEMBLE backbone-only versus PHM detector-prediction-hook execution, including the latency covariate, remains explicit.
- REASSEMBLE and PHM PatchTST initialization, widths, strides, channel/token aggregation, padding/masking qualifications and unmeasured PHM batch-length concern remain.
- Exact statistical feature list and definitions, channel identities, dimensions, model configurations, parameter counts, original gate inputs and all mathematical formulations remain.
- Historical starting protocol, bounded neural budget, exploratory sensor selection, lack of exhaustive search, candidate audio versus uncompleted branch, and unevaluated component-combination caveat remain.
- The shared prediction-bank limitation remains briefly in Chapter 3 with the existing methodological cross-reference. Its complete procedure and the within-fold versus pooled-score caveat remain in Chapter 4; the parent task must verify that chapter after parallel consolidation.
- Removed recap paragraphs sometimes repeat concepts also retained in figures/tables; those figures, tables and their notes are unchanged.
- No experiment was run. Compilation and final PDF inspection are delegated to the parent task.

State A SHA-256: `ec3d060ad44e00e19583fa3b16c257cc66e28803f2c4e113c6348ccca06a6479`
Consolidated Chapter 3 SHA-256: `b0a76153e8c3b6025448a4611feca7b23b7ade958de907fbd0360431c3c78388`
