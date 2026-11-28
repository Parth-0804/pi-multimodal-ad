# Architecture-specific justification

This is a targeted check of consequential arguments, using the existing [bibliography](../../00_thesis_writing_tracking/Thesis/LaTeX_Project/references.bib), [literature appraisals](../../00_thesis_writing_tracking/Thesis/References/literature_review/) and Chapters 2–3. It does not restart the literature review. The local Zotero API/connector was unavailable; no live-library completeness claim is possible. Original publications were inspected through public primary-paper copies. Locally stored PDF contents were not newly parsed. Bibliographic presence is distinct from full-text inspection.

## L1. RT-DETR: provenance is not the executed architecture

**Original source inspected:** Zhao et al., *DETRs Beat YOLOs on Real-time Object Detection*, CVPR 2024; [author paper, §§4.1–4.2, Figure 4 and §6](https://arxiv.org/html/2304.08069v3). Existing key `Zhao2024RTDETR`.

The paper describes a CNN backbone, attention-based within-scale interaction, convolutional cross-scale fusion and a detection decoder. Its accuracy/speed evidence concerns detection benchmarks and the complete detector; small-object performance remains a stated limitation. It does not evaluate this thesis's backbone-only, pooled-frame action classifier.

**Historical evidence:** the [frozen Section 1 protocol](../../implementations/REASSEMBLE/docs/SECTION_1_PROTOCOL.md) records the official R18vd checkpoint, deterministic sampling and a modest head-training budget. **UNKNOWN:** a contemporaneous comparison establishing why that checkpoint was selected over every plausible alternative. Do not invent such a decision.

**Scientific rationale, INFERRED:** fixed pretrained spatial features permit a bounded test under limited target supervision and repeated grouped fitting. **Demonstrated suitability:** C3–C5 in the [cross-map](SCIENTIFIC_CROSS_MAPPING.md) support conditional visual usefulness; the later spatial-component comparison favors its tested CNN configuration. Neither establishes the globally best encoder, inherited detector latency, or a Transformer executing in the core visual path.

**Manuscript action:** retain Chapter 3's precise component description; replace generic architecture prestige with the provenance/task distinction and the historical protocol boundary.

## L2. PatchTST: architecture adaptation, not forecasting-result transfer

**Original source inspected:** Nie et al., *A Time Series is Worth 64 Words: Long-term Forecasting with Transformers*, ICLR 2023; [paper §§3.1–3.2, §4.3/Table 7](https://arxiv.org/pdf/2211.14730). Existing key `Nie2023PatchTST`.

Patching and shared channel-independent encoding motivate the proposed temporal representation. The published forecasting route uses instance normalization, positional embeddings and a flattened forecasting head with squared-error supervision; its self-supervised route uses masked patch reconstruction. Table 7 tests architectural choices within forecasting. These results do not establish action-failure classification performance.

**Historical evidence:** the protocol explicitly calls the scratch classifier a bounded initial model and warns against excluding benefits of longer training. **Implementation inspected:** [SensorHead](../../implementations/REASSEMBLE/src/reassemble/section1_models.py) uses external standardization, disabled internal scaling, layer normalization, patch averaging and channel concatenation before classification. This is a consequential adaptation. The observed-value argument alone is not proof of attention masking.

**Scientific rationale, INFERRED:** a compact patch encoder tests whether sequence-derived summaries improve on engineered statistics. **Demonstrated suitability:** C1 shows a budget effect, C2 a useful hybrid, while the standalone long-budget model remains weaker than statistics. No forecasting checkpoint was transferred. Chapter 2's forecasting caveat is already sound; the needed improvement is to connect it to these empirical outcomes.

## L3. Statistical features and aggregation: operational justification is essential

Chapter 2 §2.4.1's broad sensor/representation citations do not directly validate the exact REASSEMBLE 220-feature vector. That is a precise support gap, not a reason to search for a publication that happens to use the same dimension.

**Implementation VERIFIED:** [statistics()](../../implementations/REASSEMBLE/src/reassemble/section1_features.py) computes per-channel mean, standard deviation, median, minimum, maximum, lower/upper quartiles, range, RMS and linear progress slope, over 22 channels resampled to 512 progress positions. Location, spread, magnitude and linear trend are preserved; detailed temporal order is not. RMS here is a summary of a progress-resampled channel, not a separately validated physical frequency feature. Population imputation/scaling belongs to training partitions; the descriptive summaries themselves do not fit a population model.

**Historical evidence:** these summaries are named in the original protocol as a baseline. **Scientific rationale, INFERRED:** compactness and a restricted hypothesis class are useful contrasts to learned sequences. **Demonstrated suitability:** their strong results and the C2 hybrid support a task-specific baseline, not universal sufficiency or causal interpretation of individual features.

For frame means, the argument should likewise be operational: the mean is permutation invariant and cheap to fit repeatedly. C3 supplies evidence about a limitation of that baseline; it must not be retroactively described as the reason for selecting mean pooling. No further pooling citation is necessary to establish this algebraic property. A claim that last-quarter pooling is generally optimal would require evidence absent here.

## L4. F2: a consequential, narrowly fillable literature gap

A bounded search of the existing bibliography/register text found no direct Wolpert/Ting stacking foundation. One Elicit query located candidates; their search summaries were not used as methodological evidence. The inspected original source is Ting and Witten, *Issues in Stacked Generalization*, **JAIR 10 (1999), 271–289**, [§§2–3](https://arxiv.org/pdf/1105.5466). The arXiv deposit date is not the publication year.

The paper constructs level-one learning inputs from cross-validated predictions and examines probability inputs, using a multiresponse least-squares combiner in its experiments. It supports the general fitting logic, not this thesis's logistic C=1 choice, group definition or calibration scheme. Add only the [proposed entry](proposed_bibliography.bib), key `Ting1999Issues`, after review.

**Historical evidence:** [Section 1B](../../implementations/REASSEMBLE/docs/SECTION_1B_PROTOCOL.md) follows the initial unimodal results; the statistics choice therefore retains that outcome-informed chronology. **Implementation VERIFIED:** [fit_stacker](../../implementations/REASSEMBLE/src/reassemble/section1b.py) fits an unrestricted, unweighted logistic model to visual and sensor probabilities. The coefficients need not sum to one and are not importance percentages. The later training-side reuse of an OOF bank limits meta-validation independence without proving outer-test fitting leakage. See C5 for the newly verified inference-time contribution.

## L5. Adaptive mechanisms: related literature does not validate the exact gate

Three existing sources are sufficient to sharpen the argument without a new broad search:

- **GMU, key `P006`:** Arevalo et al., [*Gated Multimodal Units for Information Fusion*, §3.1](https://arxiv.org/pdf/1702.01992). It mixes transformed hidden features using learned gates, evaluated with movie posters and plot text for genres. This is a precedent for learned gating, not the thesis's scalar probability/logit rules or evidence of industrial fault reliability.
- **QMF, key `Zhang2023QMF`:** Zhang et al., [*Provable Dynamic Fusion for Low-Quality Multimodal Data*, §§3–6](https://proceedings.mlr.press/v202/zhang23ar/zhang23ar.pdf). Its comparison of generalization bounds depends on conditions linking dynamic weights and unimodal losses, and its method uses an energy-based uncertainty construction and regularization. A favorable bound under assumptions is not proof that any quality-conditioned gate reduces realized error. The thesis does not demonstrate that its proxy descriptors and fitted coefficients satisfy those assumptions.
- **Shift/calibration, key `P008`:** Ovadia et al., [*Can You Trust Your Model's Uncertainty?*, §§4–5](https://arxiv.org/pdf/1906.02530). Its dataset-shift experiments motivate testing probability quality after corruption; clean post-hoc calibration does not guarantee calibration under shift. This is a reason for empirical checks, not a diagnosis of the thesis's particular gates.

**Historical evidence:** the anchored model is a follow-up to the original gate comparisons. It preserves a successful fitted probability link while testing bounded context-dependent coefficient changes. **Demonstrated suitability:** C6 supports clean AP for that function class against its anchor and constant adjustment; C7 does not establish a general robustness gain.

**Remaining gap:** neither the corpus nor this targeted inspection establishes literature priority for the exact anchored equation. Describe it as the evaluated construction, not a first-of-its-kind contribution. Establishing novelty would require a separate, consequential prior-art investigation; it is unnecessary for the empirical thesis claim proposed here.

## Decision for Chapters 2 and 3

The corpus is sufficient for the representation and robustness motivation after sharpening the task/component distinctions. It is insufficient for a direct foundational stacking explanation until the single proposed citation is added. It cannot supply missing historical reasons, prove the exact feature vector optimal, or certify novelty of the anchored gate. Those are different gaps and should not be disguised by adding more general citations.

Preserve three layers in the prose: **what the contemporaneous protocol chose; why the choice is scientifically interpretable; what the subsequent experiments actually established.** These layers can agree without being the same evidence.
