# Literature positioning under the original architecture questions

TASK 2B revision, 2026-10-25 (Europe/Berlin). **Current alignment layer; no new literature search or paper reproduction was performed.** All prior paper records, citations and access limitations are preserved verbatim below.

## Contribution framing

The [original exposé](../../MA_Exposé_Ravaliya_Parth.pdf), §§3–6, centers a feasible reference architecture, representation selection, unimodal/concatenation baselines, modular late fusion, process-aware gating and robustness/broader evaluation. The narrow quality-interaction comparison belongs to **H-SQ3-Q** in [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md); it is not the whole contribution or an authoritative replacement main RQ.

The contribution proposed for review is an implemented modular pipeline and a bounded architecture/fusion comparison in the agreed PHM + REASSEMBLE case studies, including valid negative results and explicit task/validation limits. Architectural novelty and superiority are not established by implementation differences. Do not invent a gap such as “earlier work never controlled augmentation” from a targeted reading list.

## Literature roles by original question

| Original question | Role of retained reading / original references | What remains necessary for final writing |
|---|---|---|
| Main / architecture | The exposé's references [1–3,12–13] motivate multimodal systems, attention/fusion and data validation. Retained L1/L5 show architecture and evaluation precedents. | Source-grounded justification of the actual modular choices and limits, not a claim to invent multimodal architecture comparison. |
| SQ1 representations | Exposé references [6–11] name ViT, Video Swin, TimeSformer, PatchTST, AST and RT-DETR. These are candidate/reference families; §5.2 expressly permits RT-DETR backbone extraction. | Explain CNN-only versus separate spatial encoder execution, statistics versus tested PatchTST, and the audio feasibility exclusion. The prior TASK 2 list is not a completed systematic review of every representation family. |
| SQ2 fusion | Retained L1/L3/L5 supply examples of feature/decision/evidential fusion; exposé §§5.3–5.5 define its planned comparison. | Compare actual mathematical families: F3 embeddings, F2 affine probability stacking, F4–F6 convex-logit allocation, and separate anchored/interaction extensions. Original §5.4 does not mandate convex F2 weights. |
| SQ3 robustness | L2 QMF, L3 TMC, L4 EmbraceNet and L9 screening motivate reliability and missingness research; L5 supplies evaluation context. | Distinguish uncertainty theory from observable proxies; known-mask fallback from learned robustness; partial degradation from clock shifts; clean-AP gains from corrupted-input improvements. H-SQ3-Q needs matched exposure and a clean-loss margin. |
| SQ4 broader evaluation | L5 MultiBench and L6 WILDS motivate costs, imperfections and independent-domain evaluation. | Bound interpretability and usability claims to actual measurements. External validation can strengthen evidence without being an automatic original thesis requirement. |

The descriptions above identify the **role** of the original bibliography, not a new claim that all cited papers were fully reviewed in TASK 2B. The exact accessible-text levels for TASK 2 sources L1–L9 remain as originally recorded in the appendix. The October 6 review is a technical evidence review, not a scientific paper or documentary title approval.

## MSM's revised role

MSM remains **PROPOSED, OPTIONAL**, conditional on separate authorization and a data audit. The accepted PHM + REASSEMBLE transition is not contingent on selecting MSM. The exposé §§5.6–5.7 called for controlled robustness and practical evaluation; it did not require a third dataset or zero-shot transfer.

A later MSM study could test the transportability of a frozen comparison after declared dataset-specific branch fitting. That is independent methodology validation only with protected groups and declared adaptation rules; it is not reuse of an unchanged fitted REASSEMBLE predictor. Video timing, paired coverage, label mapping and group support remain unverified at file level. The original MSM source's partial-text access limit remains; this task neither downloads nor audits it.

The previous conceptual properties, label distinctions and caveats are preserved in the appendix. Their feasibility reasoning may inform a later decision; its old statement that the next step is necessarily an MSM audit is superseded. The immediate next step is review of the aligned architecture/fusion storyline and remaining claim requirements.

<details>
<summary>Preserved TASK 2 proposal — historical snapshot; current TASK 2B text above takes precedence</summary>

The following earlier proposal is preserved verbatim for provenance. Its original research hierarchy, missing-source statements and approval questions are superseded where corrected above. Numerical/source evidence retains its original review scope.

<!-- TASK2_SNAPSHOT_BEGIN -->
# Literature positioning and MSM conceptual feasibility

Review date: 2026-10-25 (Europe/Berlin). Status: targeted critical review, **not an exhaustive systematic review**. No dataset was downloaded or processed.

## Search and verification boundaries

Search topics: industrial multimodal anomaly detection; static/dynamic quality-aware fusion; missing/degraded modalities; reliability-aware classification; robustness benchmarks and distribution shifts; REASSEMBLE; MSM milling. Primary sources were publisher proceedings, author preprints, dataset publications and the official REASSEMBLE repository. Search summaries from unrelated implementations were not used as methodological evidence.

**FULL TEXT** below means accessible original-paper methods/evaluation sections were inspected; it does not mean the method was reproduced or every proof/appendix audited. **PARTIAL FULL TEXT** means identified indexed excerpts beyond the abstract were available but the complete article could not be fetched. **ABSTRACT ONLY** cannot support detailed claims about evaluation fairness or baselines. Citation existence and the support for a particular claim are separate checks. No novelty claim follows from this search.

## Original research records

### L1 — Industrial multimodal anomaly detection

**Yue Wang, Jinlong Peng, Jiangning Zhang, Ran Yi, Yabiao Wang, Chengjie Wang (2023). Multimodal Industrial Anomaly Detection via Hybrid Fusion.** CVPR. [Original full text, arXiv v2](https://arxiv.org/html/2303.00601v2). **FULL TEXT**, particularly §§3–4 and appendices.

- **Question/method:** exploit RGB and 3D jointly without losing modality-specific information. M3DM combines aligned point/image features, contrastive feature fusion, separate memory banks and one-class decision fusion.
- **Evaluation/findings:** MVTec 3D-AD normal-training defect detection/localization; RGB/3D/fused comparisons using image AUROC and localization metrics. The paper reports advantages for its hybrid representation.
- **Limits/difference:** this is normal-only spatial inspection, not supervised completed-action failure prediction. The inspected benchmark does not establish robustness under our raw sensor/video degradations. Our possible contribution is a controlled reliability/robustness evaluation; implementing a different fusion head is not demonstrated novelty. Do not compare its AUROC/localization scores numerically with our AP.

### L2 — Quality-aware dynamic fusion

**Qingyang Zhang, Haitao Wu, Changqing Zhang, Qinghua Hu, Huazhu Fu, Joey Tianyi Zhou, Xi Peng (2023). Provable Dynamic Fusion for Low-Quality Multimodal Data.** ICML, PMLR 202:41753–41769. [Proceedings and metadata](https://proceedings.mlr.press/v202/zhang23ar.html), [original PDF](https://proceedings.mlr.press/v202/zhang23ar/zhang23ar.pdf). **FULL TEXT**, §§3–6, especially Theorem 2/Assumption 1.

- **Question/method:** when can dynamic decision fusion help? QMF uses energy-based uncertainty and sample-dependent weighting; the theory relates the bound to weight/loss covariance.
- **Evaluation/findings:** NYU Depth V2 and SUN RGB-D RGB/depth scene recognition; UPMC FOOD101 and MVSA image/text classification; corruption and repeated-seed accuracy comparisons. Reported robustness supports their formulation on those tasks.
- **Limits/difference:** its conditional bound requires informative uncertainty and other restrictions. A tighter upper bound does not itself order actual risks, and it gives no AP guarantee for our unconstrained probability×quality model. Quality estimation remains difficult. Our hypothesis needs empirical evidence under matched augmentation, group separation and clean-cost constraints; adaptive fusion itself is established prior art.

### L3 — Reliability through evidential fusion

**Zongbo Han, Changqing Zhang, Huazhu Fu, Joey Tianyi Zhou (2021). Trusted Multi-View Classification.** ICLR. [Original full text](https://arxiv.org/html/2102.02051v1), [conference record](https://openreview.net/forum?id=OOsR8BzCnl5). **FULL TEXT via author preprint**; direct conference PDF encountered a verification page.

- **Question/method:** integrate sample-specific view reliability. TMC maps evidence to Dirichlet opinions and combines views using Dempster–Shafer rules.
- **Evaluation/findings:** Handwritten, CUB, PIE, Caltech101, Scene15 and HMDB; accuracy, Gaussian view corruption and uncertainty diagnostics. The authors report stronger noisy-view classification and separation of clean/corrupted uncertainty.
- **Limits/difference:** these benchmarks do not validate our industrial grouping, target semantics or deployment faults. Evidential uncertainty is a model assumption, not physical ground truth. Our inspected implementation uses observable quality descriptors and logistic interactions, not TMC. It cannot inherit TMC's reliability claims merely by using the word adaptive.

### L4 — Missing modalities and data loss

**Jun-Ho Choi, Jong-Seok Lee (2019). EmbraceNet: A robust deep learning architecture for multimodal classification.** Information Fusion; [original full text](https://arxiv.org/html/1904.09078v1). **FULL TEXT**, §§3–7.

- **Question/method:** combine heterogeneous branches while tolerating absent inputs. Docking layers align feature widths; a stochastic embracement layer selects modality features and can exclude unavailable modalities.
- **Evaluation/findings:** gas sensor arrays and OPPORTUNITY activity recognition, including missing modalities and blockwise data loss. Gas data use location-based partitions; activity data follow the challenge session split. The paper reports improved missing-input performance.
- **Limits/difference:** activity evaluation is not universal unseen-subject validation, and missing-input experiments do not establish industrial fault robustness. Our hard surviving-branch fallback is a different, simpler mechanism. Identical fallback between our arms cannot demonstrate learned adaptive advantage. Missing-modality handling is already substantial prior art.

### L5 — Evaluation across tasks and imperfections

**Paul Pu Liang, Yiwei Lyu, Xiang Fan, Zetian Wu, Yun Cheng, Jason Wu, Leslie Chen, Peter Wu, Michelle A. Lee, Yuke Zhu, Ruslan Salakhutdinov, Louis-Philippe Morency (2021). MultiBench: Multiscale Benchmarks for Multimodal Representation Learning.** NeurIPS Datasets and Benchmarks. [Original full text](https://arxiv.org/html/2107.07502v2). **FULL TEXT**, §2.2, Appendix D and H.9–H.10.

- **Question/method:** standardize multimodal evaluation beyond one dataset's headline score. Fifteen datasets, ten modalities, twenty tasks and twenty implemented approaches span performance, computational cost and robustness to imperfections.
- **Findings:** simple late fusion can be competitive; methods vary across datasets, and clean performance and degradation curves require separate interpretation.
- **Limits/difference:** its synthetic imperfections and task-specific partitions are not a guarantee of prospective industrial validity. Our narrower contribution could be a traceable group-disjoint study with an augmentation-matched primary contrast and protected external evaluation. Comparing multiple architectures alone is not a new benchmark principle.

### L6 — Independent domains and natural distribution shifts

**Pang Wei Koh, Shiori Sagawa, Henrik Marklund, Sang Michael Xie, Marvin Zhang et al. (2021). WILDS: A Benchmark of in-the-Wild Distribution Shifts.** ICML, PMLR 139:5637–5664. [Proceedings with complete author list](https://proceedings.mlr.press/v139/koh21a.html), [original PDF](https://proceedings.mlr.press/v139/koh21a/koh21a.pdf). **FULL TEXT**, §§1–3 and benchmark design.

- **Question/method:** evaluate naturally occurring domain and subpopulation shifts through ten datasets with domain metadata and explicit split definitions.
- **Evaluation/findings:** settings include hospitals, cameras and geographic/time differences. Standard and specialized training methods retain substantial out-of-distribution performance gaps.
- **Limits/difference:** this is not evidence for any particular multimodal gate or milling model. It motivates matching the validation unit to the generalization claim. Our proposed second dataset would test a frozen comparison after declared retraining; it would not automatically demonstrate transfer of a fitted REASSEMBLE predictor or generalization to all machines.

### L7 — REASSEMBLE's actual task context

**Daniel Sliwowski, Shail Jadav, Sergej Stanovcic, Jędrzej Orbik, Johannes Heidersberger, Dongheui Lee (2025). REASSEMBLE: A Multimodal Dataset for Contact-rich Robotic Assembly and Disassembly.** [Original v2 full text](https://arxiv.org/html/2502.05086v2), DOI [10.48550/arXiv.2502.05086](https://doi.org/10.48550/arXiv.2502.05086). **FULL TEXT**, §§III–VI and dataset appendix.

- **Question/method/data:** a multimodal contact-rich manipulation resource with action/outcome annotations, RGB, robot state, force/torque, audio and events; 4,551 action demonstrations involving four actions and 17 objects.
- **Evaluation/findings:** action segmentation, policy learning and execution monitoring illustrate dataset utility. Its monitoring benchmark is a distinct task/protocol from our completed-segment binary classifier; its reported 96% figures are not comparators for our AP.
- **Limits/difference:** controlled task-board acquisition and similar objects constrain generalization. The original publication does not independently validate our filtered cohort, audio timing or failure classifier. Our work studies modality contribution and controlled corruption, not a reproduction of the paper's monitoring score.

The [official repository's file comments](https://github.com/TUWIEN-ASL/REASSEMBLE#%EF%B8%8F-file-comments) separately document camera, final-action force/torque and hardware issues. The local [pilot audit](../../00_experiments/adaptive_fusion_robustness/results/run_01/DATA_AUDIT.md) reconciles selected exclusions; that native-file reconciliation was not rerun here. Presence of audio in the publication does not establish usable local audio alignment.

### L8 — MSM dataset publication

**Eunseob Kim, Yuseop Sim, Adrian Shuai Li, Mir Imtiaz Mostafiz, Zachary Van Meter, Martin Byung-Guk Jun, Elisa Bertino, Ali Shakouri (2026). Multi-sensor and MTConnect dataset of metal cutting anomaly in milling from laboratory and industry settings.** Scientific Data 13:945. DOI [10.1038/s41597-026-07255-7](https://doi.org/10.1038/s41597-026-07255-7). [Publisher](https://www.nature.com/articles/s41597-026-07255-7); [bibliographic record](https://pubmed.ncbi.nlm.nih.gov/42026091/).

**PARTIAL FULL TEXT:** indexed original Methods/Data Records excerpts were inspected, including labeling and video descriptions. Direct publisher HTML/PDF redirected to inaccessible infrastructure; PMC encountered a browser challenge and Europe PMC retrieval failed. This is more than abstract-only access, but **complete full-text review is UNVERIFIED**. No model-performance finding is asserted. Dataset DOI: [10.34740/kaggle/ds/8392825](https://doi.org/10.34740/kaggle/ds/8392825); the [official Kaggle landing page](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly) exposed no readable inventory here.

Documented properties from those original excerpts are recorded once in the table below. Our proposed contribution differs by testing a frozen adaptive/static robustness comparison; the data descriptor alone establishes neither model superiority nor a protected split for our use.

### L9 — More recent reliability work, screening only

**Wei Liu, Yufei Chen, Xiaodong Yue (2025). Enhancing Testing-Time Robustness for Trusted Multi-View Classification in the Wild.** CVPR, pp.15508–15517. [Original proceedings abstract](https://openaccess.thecvf.com/content/CVPR2025/html/Liu_Enhancing_Testing-Time_Robustness_for_Trusted_Multi-View_Classification_in_the_Wild_CVPR_2025_paper.html).

**ABSTRACT ONLY:** search-indexed proceedings abstract/metadata accessible; direct HTML/PDF fetch returned 403. The abstract proposes filtering unreliable evidence with a multiple-testing/p-value mechanism compatible with several evidential fusion rules. It reports improved classification, but datasets, full protocol, limitations and augmentation matching are **UNVERIFIED**. Our current model is not an implementation of it. This paper prevents treating generic reliability filtering as an untouched idea; obtain full text before detailed comparison or selecting it as a baseline.

## Positioning and theoretical foundation

The reviewed literature supports three distinct concepts: complementary predictive information, sample-dependent reliability, and robustness under a specified shift. None implies the other two. Existing empirical E3 static gains motivate asking whether information remains useful after degradation; they do not prove that proxy quality identifies the trustworthy branch. L2 gives a theoretical reason to examine quality/loss association, while L3 shows that uncertainty is itself modelled rather than directly observed.

Our **PROPOSED contribution** is a bounded, auditable empirical investigation: fixed group-disjoint predictions; a competitive static reference trained with the same augmentation; separate additive-quality and interaction effects; clean-performance constraints; explicit missingness policy; and, if feasible, protected external methodology validation. It may produce a negative or inconclusive result. Whether this combination meets master's-thesis contribution requirements is a supervisor decision. It is **not established as novel** by this targeted search.

Do not claim that prior work universally omits matched augmentation, group controls or clean-cost assessment; this review has not established that universal gap. A defensible gap statement is narrower: **our current evidence does not establish whether quality conditioning adds useful robustness under those controls in the studied industrial tasks.**

## MSM conceptual feasibility — no file-level audit performed

The documented-fact column below summarizes L8's original excerpts; the other column is this review's assessment, not a dataset guarantee.

| Aspect | Documented property | Still UNVERIFIED / implication |
|---|---|---|
| Modalities | Sound, MTConnect/controller signals, vibration/power; accelerometers on `imi_vm20i`; industrial current-transformer data | Exact paired coverage, channels, units and independence of sensor streams |
| Video | Smartphone MP4 experiments through the door window in laboratory data | Video clock offsets, full cutting coverage, visibility and industrial video availability |
| Synchronization | Sensor streams cropped to a common experiment zero; WAV timing uses 48 kHz | Residual drift/offsets and whether that mapping includes smartphone video |
| Labels | 0 stable cutting; 1 abnormal cutting requiring intervention; 2 defective tool with stable cutting; abnormal cutting overrides 2 | Annotation consistency, class support and task mapping |
| Groups | Two laboratory mills (`imi_vm20i`, `imi_vmx30ui`) and one industrial mill (`tmf_vf10`); laboratory experiment/industrial operation units | Shared tools/workpieces/programs, chronology, duplicates and protected split support |

**INFERRED feasibility:** MSM is a reasonable candidate for testing a methodology on separately acquired milling data. It is not yet qualified for synchronized visual-sensor validation. If verified video fails, audio plus an independently acquired sensor stream could still test a broader multimodal robustness hypothesis, subject to explicit scope approval. Several channels of one instrument should not automatically be described as independent modalities.

**PROPOSED target:** if the goal is intervention-worthy cutting anomaly, discuss `1 versus {0,2}` as the primary target, with a predeclared `1 versus 0` sensitivity analysis. This treats label 2 as stable cutting for that operational question, not as a healthy tool. If the intended question is tool condition, it needs a different target. Do not choose a mapping based on model scores. Exclude label files, tool-defect markers, free-text remarks and stop/outcome metadata from unrestricted predictors; use process settings only in explicitly controlled context arms.

**PROPOSED grouping:** keep every window from an original experiment/operation together; escalate to shared physical tool/workpiece/session groups where dependence is established. Audit before choosing folds. Machine-held-out evaluation is a distinct secondary claim and may confound hardware/availability shift with generalization. With only a few machines, nominal cross-machine intervals would not justify population-wide industrial claims.

**Could test:** whether a fixed quality/static comparison remains useful after declared dataset-specific fitting on a new task/acquisition environment; whether it survives the predeclared synthetic degradations on protected MSM groups.

**Could not establish:** zero-shot transfer of the fitted REASSEMBLE model; benefit of visual fusion without validated video pairing; early warning from complete-cut labels alone; causal tool-damage measurement; universal machine/site generalization; or real production sensor-fault robustness merely from synthetic corruption performance.

Next step is the separately approved data audit specified in [OPEN_RESEARCH_DECISIONS.md](OPEN_RESEARCH_DECISIONS.md). No download, processing or training has been started.
<!-- TASK2_SNAPSHOT_END -->

</details>
