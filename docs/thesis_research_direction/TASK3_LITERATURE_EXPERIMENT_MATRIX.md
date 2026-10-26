# TASK 3 — literature, implementation and experimental evidence

Date: 2026-10-25, Europe/Berlin. Code baseline: `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`. Status: research synthesis, not authorization for further execution.

## Authority and evidence labels

The [original nine-page exposé](../../MA_Exposé_Ravaliya_Parth.pdf), §3 pp.2–3, controls the original questions. [TASK 2B alignment](EXPOSE_ALIGNMENT_DECISION.md) supersedes the earlier proposal. The [charter](RESEARCH_CHARTER.md), [evidence map](EXISTING_EVIDENCE_MAP.md), [literature positioning](LITERATURE_POSITIONING.md), [open decisions](OPEN_RESEARCH_DECISIONS.md) and [executive review](EXECUTIVE_REVIEW.md) were consulted without alteration. Researcher-reported supervisor agreement to PHM + REASSEMBLE is accepted; documentary final-title approval is a separate matter.

The supplied review was read in full: [critical_literature_review.pdf](../../critical_literature_review.pdf), 34 pages, SHA256 `11d1d56cb63550a1f548298e905755a4136fdeafc928f515b23cfed5c416bce7`. This is the file the researcher explicitly supplied, despite the attachment instruction's `(2)` filename. It is a secondary synthesis, not primary experimental evidence. Its embedded recommendations do not authorize execution. Paper IDs below retain its R-numbers; R37 is the additional MBGN screen.

- **T:** mathematical/methodological argument, with assumptions; **P:** published empirical result, limited to its own task/protocol.
- **V3-SOURCE:** source/configuration inspected in TASK 3; this does not prove historical execution.
- **V3-NUM:** independently recomputed here from saved predictions, without fitting or inference.
- **REPORTED:** retained report, interval, prior audit or execution claim not independently reproduced here.
- **PROPOSED / UNTESTED / UNKNOWN:** design, absent test, or insufficient evidence respectively.

Access levels distinguish **FT-selected** (specified methods/results passages of an original paper inspected), **PARTIAL** (primary indexed text/preview), and **RECORD/ABSTRACT**. None means independent reproduction or an exhaustive proof/appendix audit. Primary-source access was checked on 2026-10-25; blocked full text is not silently replaced by an AI summary. Several DOI resolver links were inaccessible even when the corresponding author/proceedings paper was readable; metadata verification and successful live DOI resolution are distinct. ModDrop's journal DOI is retained from the supplied catalogue and corroborating bibliographic records; direct IEEE/HAL journal-record verification was blocked. Its methods are supported by the accessible original author preprint.

## Controlling questions and case-study roles

**Exact original main RQ:** “How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial anomaly detection using robotic welding data as a case study?”

**TASK 2B proposed working adaptation:** “How can a process-aware multimodal AI architecture be designed and evaluated for robust industrial condition and failure monitoring using PHM and REASSEMBLE as case studies?”

Architecture, representation selection, comparative fusion, robustness and broader evaluation remain central. H-SQ3-Q is a particular hypothesis under SQ3. PHM is provisional image-target/sensor-prediction feasibility work; it did not demonstrate visual–sensor fusion. REASSEMBLE carries the actual visual–sensor fusion comparison and completed-action failure task. Their metrics and targets cannot be pooled.

## Corrections and qualifications to the supplied review

| Review location | Assessment after source/project inspection |
|---|---|
| pp.3,12,14: narrow quality RQ described as the current charter | **Superseded context.** TASK 2B already recovered the exposé and restored the architecture-led hierarchy. The review's warning applies to the preserved older proposal, not the current charter. Its matching-name local-copy provenance caveat remains its own limitation. |
| pp.4–5: core and pilot point estimates | **Confirmed at saved-output arithmetic level here.** V3-NUM reproduces core AP/AUROC, PHM CSV MAE and the 34-table pilot AP aggregation. Historical intervals remain REPORTED; no bootstrap was run here. |
| pp.4,13: 21 REASSEMBLE exclusions not inspected | The [pilot data audit](../../00_experiments/adaptive_fusion_robustness/results/run_01/DATA_AUDIT.md) reports a native/keyed reconciliation and 21 exclusions. The [native exclusion table](../../00_experiments/adaptive_fusion_robustness/results/run_01/checks/native_annotation_audit.csv) exists. Its raw-data derivation was not re-audited here. Distinguish review access limits from live-repository absence. |
| pp.11–12: adaptive benefit unresolved | Correct for the October matched robustness hypothesis. Add the separate September anchored model's REPORTED clean AP gain and its inconclusive matched robustness contrast. A blanket “adaptation never helped” is false; no general robustness win follows either. |
| pp.13,26: original TMC methods inaccessible | **Access improved:** original v1 HTML methods and six-dataset setup are readable now. Do not conflate the 2021 paper with its later journal extension. |
| p.23: Wolpert experiments unavailable | **Access improved:** original journal scan on an academic mirror, including §3.2, inspected. Publisher full text remains blocked; original-paper content is distinct from a secondary explanation. |
| pp.10,25: QMF theorem | Theorem 2 explicitly orders risk **upper bounds**, subject to mean-weight and weight–loss correlation conditions. It neither guarantees actual-risk ordering nor AP improvement for our unrestricted interaction head. |
| pp.13,17: DMAW robustness and application language | Direct postprint confirms dynamic audiovisual fusion, training-time gradient balancing and 20-frame sample groups. Run/session-disjoint assessment and a sufficiently explicit independent corruption protocol remain unestablished in inspected sections. “Laser” wording alongside a pulsed-MIG apparatus is a reporting ambiguity, not grounds to invent a corrected apparatus. |
| p.34: MSM details unavailable | New primary indexed Methods excerpts support acquisition/label descriptions beyond metadata. Complete direct full-text access still fails. No file-level pairing, timestamps, label audit or protected split is established. MSM remains optional. |
| General: narrow adaptive novelty | Stacking, feature gating and dynamic industrial fusion are prior art; MBGN adds close electrical–visual GMAW evidence. Methodological comparability must still be assessed, not assumed from titles or high scores. |

## Primary-paper register

Each entry records citation/identifier, access, task, training/fusion, evaluation unit, finding, limitation and question relevance. Preprint DOIs identify preprints; no unverified proceedings DOI is invented. A paper without a verified DOI remains citable by its primary venue record. Published performance below is **P**, never a project result.

### R06 — RT-DETR

Yian Zhao, Wenyu Lv, Shangliang Xu, Jinman Wei, Guanzhong Wang, Qingqing Dang, Yi Liu and Jie Chen (2024). **DETRs Beat YOLOs on Real-time Object Detection.** CVPR, 16965–16974. Preprint DOI [10.48550/arXiv.2304.08069](https://doi.org/10.48550/arXiv.2304.08069); [original v3](https://arxiv.org/html/2304.08069v3), **FT-selected §§4–5**; CVF HTML returned 403.

COCO box detection uses a CNN backbone, spatial hybrid encoder and Transformer decoder, trained with detection supervision; evaluation units are benchmark images, not industrial recordings. Reported R50 detection AP/FPS concern the complete detector. **SQ1/SQ4:** justify a pretrained component and identify the executed tap; no action-failure, video-order or sensor-robustness guarantee follows. Core backbone extraction executes no hybrid encoder/decoder.

### R10 — PatchTST

Yuqi Nie, Nam H. Nguyen, Phanwadee Sinthong and Jayant Kalagnanam (2023). **A Time Series is Worth 64 Words: Long-term Forecasting with Transformers.** ICLR. Preprint DOI [10.48550/arXiv.2211.14730](https://doi.org/10.48550/arXiv.2211.14730); [original v2](https://arxiv.org/html/2211.14730v2), **FT-selected §§3–4 and experimental details**.

Temporal patches and shared channel-independent Transformer weights support supervised forecasting and masked pretraining. Eight forecasting datasets use chronological train/validation/test periods and MSE/MAE across forecast horizons; these are not independent factory trials. Competitive forecast results motivate representation testing. **SQ1:** our scratch classifier tests one adaptation/budget, not pretrained transfer or the whole model family. Channel independence is not cross-channel attention; no fusion robustness result is inherited.

### R13 — stacking

David H. Wolpert (1992). **Stacked Generalization.** Neural Networks 5(2), 241–259. DOI [10.1016/S0893-6080(05)80023-1](https://doi.org/10.1016/S0893-6080(05)80023-1); [publisher record](https://www.sciencedirect.com/science/article/pii/S0893608005800231), **indexed abstract**; [original journal scan](https://cafri-labs.github.io/lab-manual/papers/wolpert1992.pdf), **FT-selected introduction, construction and §3.2**.

A higher-level learner uses base predictions generated while their corresponding cases were excluded from base fitting. Experiments include surface fitting and a modified text-to-phoneme task; original sample partitions do not establish industrial group independence. Reported gains illustrate the construction, not universal superiority. **SQ2/SQ4:** F2 is established prediction stacking; all preprocessing, calibration and meta-feature provenance must respect the declared partitions. Stacking can also correct a single predictor, which limits automatic complementarity claims.

### R15 — GMU

John Arevalo, Thamar Solorio, Manuel Montes-y-Gómez and Fabio A. González (2017). **Gated Multimodal Units for Information Fusion.** ICLR workshop/author paper. Preprint DOI [10.48550/arXiv.1702.01992](https://doi.org/10.48550/arXiv.1702.01992); [original v1](https://arxiv.org/html/1702.01992v1), **FT-selected §§3–5**.

MM-IMDb movie-genre prediction combines transformed poster/plot representations through learned sigmoid multiplicative gates under supervised optimization. Movie-level stratified train/dev/test sizes are 15,552/2,608/7,799. Macro-F1 0.541 versus concatenation 0.521 is task-specific. **SQ2, indirectly SQ3:** feature gating is prior art and closer to the exposé's representation-level proposal than our scalar-logit gates. Neither semantic selection nor a synthetic demonstration certifies industrial reliability or calibrated trust.

### R18 — QMF

Qingyang Zhang, Haitao Wu, Changqing Zhang, Qinghua Hu, Huazhu Fu, Joey Tianyi Zhou and Xi Peng (2023). **Provable Dynamic Fusion for Low-Quality Multimodal Data.** ICML, PMLR 202, 41753–41769. Preprint DOI [10.48550/arXiv.2306.02050](https://doi.org/10.48550/arXiv.2306.02050); [proceedings](https://proceedings.mlr.press/v202/zhang23ar.html), [original PDF](https://proceedings.mlr.press/v202/zhang23ar/zhang23ar.pdf), **FT-selected Theorems 1–2, method, §5/Table 1**.

Energy-based uncertainty conditions decision weights with correlation-oriented learning. RGB/depth scene and image/text classification benchmarks use dataset-specific sample splits, Gaussian corruption and repeated runs, not held-out industrial sites. Reported noisy-input improvements support that formulation. **SQ3/SQ4:** its assumptions motivate checking reliability signals; its conditional bound and accuracy experiments do not validate our observable-q AP contrast. Clean results need not dominate every comparator.

### R19 — evidential uncertainty

Zongbo Han, Changqing Zhang, Huazhu Fu and Joey Tianyi Zhou (2021). **Trusted Multi-View Classification.** ICLR. Preprint DOI [10.48550/arXiv.2102.02051](https://doi.org/10.48550/arXiv.2102.02051); [original v1](https://arxiv.org/html/2102.02051v1), **FT-selected §3 and §4.1**.

Jointly learned per-view Dirichlet evidence is combined using Dempster–Shafer rules. Handwritten, CUB, Caltech101, PIE, Scene15 and HMDB classification/noisy-view experiments use benchmark instances; industrial run grouping is not established. Reported classification/robustness findings concern evidential models. **SQ2–SQ4:** uncertainty-aware fusion is prior art; our logistic proxies are not TMC, and evidence magnitude is not automatically calibrated reliability. No unchecked numerical comparison is transferred.

### R02 — DMAW, direct welding evidence

Jiawei Fan, Ting Yuan, Haonan Zhang, Songlin Li, Uwe D. Hanebeck, Zhuguo Li, Edmond Q. Wu and Jiuchao Qian (2026). **DMAW: A Dynamic Multimodal Measurement Fusion Network With Attention for Reliable Welding Process Monitoring Under Harsh Industrial Environments.** IEEE Sensors Journal 26(2), 2347–2358. DOI [10.1109/JSEN.2025.3634585](https://doi.org/10.1109/JSEN.2025.3634585); [institutional metadata](https://publikationen.bibliothek.kit.edu/1000189165), [author postprint](https://isas.iar.kit.edu/pdf/Sensors2026_Fan.pdf), **FT-selected §§II–III**.

Four welding-state classes use self-distilled ViT-Small audiovisual representations, cross-attention, dynamic decision weighting and training gradient balancing. The paper reports 13,000 synchronized image–audio observations, grouped in 20-frame samples, and 96.1% accuracy. Run/session independence and held-out fault design remain unclear in inspected text; application terminology is inconsistent. **SQ1–SQ4:** close industrial prior art, substantially different training/fusion/task from ours; no score comparison or deployment certification.

### R37 — MBGN, additional requested screen

Xuefeng Zhao, Yang She, Giulio Mattera, Lichao Hu, Zhen Sun, Yan Li and Xinghua Yu (2026). **MBGN: multimodal BiFPN gate network for in-process GMAW defect detection.** Mechanical Systems and Signal Processing 258, 114696; publisher issue date 15 August 2026. DOI [10.1016/j.ymssp.2026.114696](https://doi.org/10.1016/j.ymssp.2026.114696); [primary publisher preview](https://www.sciencedirect.com/science/article/pii/S0888327026008538), **PARTIAL: search-indexed abstract, introduction and section snippets; direct fetch 403, full paper unavailable**.

Electrical current/voltage 1-D CNN features and molten-pool ResNet features feed bidirectional feature aggregation and gate recalibration under supervised defect classification. Publisher abstract reports held-out accuracy 0.748 and macro-F1 0.719. Preview describes production acquisition, but partition unit, seam independence, tuning/calibration, corruption protocol and uncertainty construction are **UNKNOWN**. **SQ1–SQ3:** close visual–electrical industrial gating prior art, not evidence that its evaluation matches ours or that its gate measures reliability.

### R20 — EmbraceNet

Jun-Ho Choi and Jong-Seok Lee (2019). **EmbraceNet: A robust deep learning architecture for multimodal classification.** Information Fusion 51, 259–270. DOI [10.1016/j.inffus.2019.02.010](https://doi.org/10.1016/j.inffus.2019.02.010); [original preprint](https://arxiv.org/html/1904.09078v1), **FT-selected mechanism and §§6–7**.

Docking layers plus stochastic feature selection/availability renormalization are trained for multimodal classification. Gas-array experiments separate acquisition locations: 1/3/5 train, 2 validation, 4 test; OPPORTUNITY uses its session-based challenge protocol. Missing-modality/block-loss gains are reported. **SQ2/SQ3:** training-based resilience differs from our deterministic surviving-branch fallback. Activity-session testing is not automatically unseen-subject testing, and neither dataset certifies plant robustness.

### R21 — ModDrop

Natalia Neverova, Christian Wolf, Graham W. Taylor and Florian Nebout (2016; online 2015). **ModDrop: Adaptive Multi-Modal Gesture Recognition.** IEEE TPAMI 38(8), 1692–1706. DOI [10.1109/TPAMI.2015.2461544](https://doi.org/10.1109/TPAMI.2015.2461544); [author v2](https://arxiv.org/html/1501.00102v2), **FT-selected modality-dropping mechanism and experimental passages**.

Multiscale gesture branches are pretrained and gradually fused while whole input channels are randomly dropped. ChaLearn challenge video/sequence partitions and missing/noisy-channel tests support the reported resilience; no new industrial grouping claim is established. Challenge rank concerns the entire system, not isolated dropout. **SQ2/SQ3:** augmentation/availability learning is substantial prior art; robustness requires a competitive exposure-matched static reference, rather than attributing every gain to adaptive weighting.

### R23 — MultiBench

Paul Pu Liang, Yiwei Lyu, Xiang Fan, Zetian Wu, Yun Cheng, Jason Wu, Leslie Chen, Peter Wu, Michelle A. Lee, Yuke Zhu, Ruslan Salakhutdinov and Louis-Philippe Morency (2021). **MultiBench: Multiscale Benchmarks for Multimodal Representation Learning.** NeurIPS Datasets and Benchmarks. Preprint DOI [10.48550/arXiv.2107.07502](https://doi.org/10.48550/arXiv.2107.07502); [original v2](https://arxiv.org/html/2107.07502v2), **FT-selected §2.2, Appendix D, H.10; prior TASK 2 reading retained**.

Unified unimodal/fusion implementations span 15 datasets, ten modalities and 20 tasks, with dataset-specific splits/units. Performance, complexity and imperfect-input evaluation reveal task-dependent rankings and competitive simple baselines. **SQ1–SQ4:** supports broad evaluation, not obligatory complexity. Its “late fusion” can mean representation concatenation; use equations here. Heterogeneous benchmark protocols are not one independent industrial trial and supply no transferable AP effect size.

### R03 — REASSEMBLE

Daniel Sliwowski, Shail Jadav, Sergej Stanovcic, Jędrzej Orbik, Johannes Heidersberger and Dongheui Lee (2025). **REASSEMBLE: A Multimodal Dataset for Contact-rich Robotic Assembly and Disassembly.** Author publication v2. Paper DOI [10.48550/arXiv.2502.05086](https://doi.org/10.48550/arXiv.2502.05086); [original v2](https://arxiv.org/html/2502.05086v2), **FT-selected collection, statistics, benchmarks and limitations**.

The dataset reports 4,551 demonstrations/4,035 successes, four actions and 17 objects. Task-specific segmentation, policy and ConditionNET experiments use different observation windows/metrics; monitoring uses annotated action regions. Its collection describes spoken narration and raw timestamps without automatic postprocessing synchronization. **SQ1/SQ4:** motivates data/task choices and timing scrutiny. Neither its monitoring percentages nor public audio availability validate our filtered cohort, completed-action AP or mechanical-audio eligibility.

### R25 — nested selection

Sudhir Varma and Richard Simon (2006). **Bias in error estimation when using cross-validation for model selection.** BMC Bioinformatics 7, 91. DOI [10.1186/1471-2105-7-91](https://doi.org/10.1186/1471-2105-7-91); [primary full text](https://link.springer.com/article/10.1186/1471-2105-7-91), **FT-selected simulation, nested-CV construction and conclusion**.

Simulated classification, shrunken centroids/SVM tuning, independent large tests and nested evaluation demonstrate selection-induced optimism. Units are simulated cases/datasets, not industrial recordings; no fusion mechanism applies. **SQ2/SQ4:** evaluate the whole specified selection procedure within the training side. Nesting does not undo later human development on previously observed assessment results, and the paper's bias magnitude is not our measured bias.

### R26 — leakage

Sayash Kapoor and Arvind Narayanan (2023). **Leakage and the reproducibility crisis in machine-learning-based science.** Patterns 4(9), 100804. DOI [10.1016/j.patter.2023.100804](https://doi.org/10.1016/j.patter.2023.100804); [publisher primary text](https://doi.org/10.1016/j.patter.2023.100804), **PARTIAL indexed final article**; [original preprint](https://arxiv.org/html/2207.07048v1), **FT-selected taxonomy/case study**, not asserted byte-identical to final article.

Leakage taxonomy and an original civil-war reanalysis show that corrections can remove apparent complex-model advantages over logistic regression. Country/time and study-specific dependencies matter; no multimodal training mechanism applies. **SQ4:** justify predictors, chronology and target population, then inspect artifacts. This paper does not demonstrate leakage in our repository, and source-level safeguards do not prove its absence.

### R27 — calibration

Chuan Guo, Geoff Pleiss, Yu Sun and Kilian Q. Weinberger (2017). **On Calibration of Modern Neural Networks.** ICML, PMLR 70, 1321–1330. No proceedings DOI listed in inspected record; [primary record](https://proceedings.mlr.press/v70/guo17a.html), [paper](https://proceedings.mlr.press/v70/guo17a/guo17a.pdf), **FT-selected §§4–5**.

Image/document classifiers receive validation-fitted post-hoc calibrators and separate benchmark tests; units are images/documents under an assumed common distribution. Temperature scaling often improves reported calibration; it is not a fusion architecture. **SQ4:** probability quality requires its own evaluation and fitted-calibrator provenance. ECE depends on binning; in-distribution calibration is not proof of reliability under shift or useful alarm thresholds.

### R28 — uncertainty under shift

Yaniv Ovadia, Emily Fertig, Jie Ren, Zachary Nado, D Sculley, Sebastian Nowozin, Joshua V. Dillon, Balaji Lakshminarayanan and Jasper Snoek (2019). **Can You Trust Your Model's Uncertainty? Evaluating Predictive Uncertainty Under Dataset Shift.** NeurIPS. Preprint DOI [10.48550/arXiv.1906.02530](https://doi.org/10.48550/arXiv.1906.02530); [original v2](https://arxiv.org/html/1906.02530v2), **FT-selected §§3–5**.

Image, text and ad-click models compare ensembles and uncertainty/calibration procedures under dataset-specific corruptions/shifts. Validation tunes methods; evaluation uses shifted examples, not industrial-site replication. Uncertainty quality degrades and good in-distribution calibration need not persist. **SQ3/SQ4:** keep confidence, signal quality and observed branch reliability distinct; no method ranking or effect transfers to our head.

### R29 — precision and recall

Takaya Saito and Marc Rehmsmeier (2015). **The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets.** PLOS ONE 10(3), e0118432. DOI [10.1371/journal.pone.0118432](https://doi.org/10.1371/journal.pone.0118432); [primary full text](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432), **FT-selected metric argument and simulation/results**.

Synthetic and biological classification examples compare metric behavior across prevalence; no new fusion architecture/training mechanism applies. PR reveals positive-prediction quality hidden by misleading interpretations of ROC. **SQ4:** report AP with class balance, AUROC and decisions. This does not make ROC useless or define a deployment threshold. Our sklearn AP must not be relabelled trapezoidal PR-AUC.

### R34 — proper scoring

Tilmann Gneiting and Adrian E. Raftery (2007). **Strictly Proper Scoring Rules, Prediction, and Estimation.** JASA 102(477), 359–378. DOI [10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437); [author-hosted original paper](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf), **FT-selected definitions and score examples**.

Theory and illustrative forecasts characterize proper scoring; no shared classifier split or fusion mechanism applies. Strict propriety rewards the true distribution in expectation. **SQ4:** Brier and log scores evaluate probability forecasts, not ranking alone. They are not pure calibration measures and do not guarantee a fitted model's calibration or robustness.

### R33 — comparison uncertainty

Yoshua Bengio and Yves Grandvalet (2004). **No Unbiased Estimator of the Variance of K-Fold Cross-Validation.** JMLR 5, 1089–1105. No DOI listed in inspected record; [primary journal record](https://jmlr.org/papers/v5/grandvalet04a.html), **RECORD/ABSTRACT theorem and simulation summary**.

The universal variance-estimator impossibility result concerns correlated CV errors from overlapping fits; simulations illustrate underestimation by naive independence assumptions. There is no fusion model or industrial independence unit. **SQ4:** folds are not independent subjects. This abstract-level check does not audit every proof or itself invalidate/validate our particular clustered bootstrap.

### R30/R31 — interpretation, paired reading

Sarthak Jain and Byron C. Wallace (2019). **Attention is not Explanation.** NAACL-HLT, 3543–3556. DOI [10.18653/v1/N19-1357](https://doi.org/10.18653/v1/N19-1357); [primary record](https://aclanthology.org/N19-1357/). Sarah Wiegreffe and Yuval Pinter (2019). **Attention is not not Explanation.** EMNLP-IJCNLP, 11–20. DOI [10.18653/v1/D19-1002](https://doi.org/10.18653/v1/D19-1002); [primary record](https://aclanthology.org/D19-1002/). **Both RECORD/ABSTRACT; detailed task splits not audited here.**

NLP attention interventions/counterarguments concern whether particular importance interpretations are faithful, not industrial reliability; benchmark instances and interventions are the evaluation units. **SQ4:** expose the computation and test a specific explanatory claim. Neither universal rejection of explanations nor a trust interpretation of our gates follows. Detailed performance/protocol claims are withheld.

### R32 — reproducibility

Joelle Pineau, Philippe Vincent-Lamarre, Koustuv Sinha, Vincent Larivière, Alina Beygelzimer, Florence d'Alché-Buc, Emily Fox and Hugo Larochelle (2021). **Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program).** JMLR 22(164), 1–20. No DOI listed in inspected record; [primary journal record](https://jmlr.org/papers/v22/20-303.html), **RECORD/ABSTRACT**.

The contribution is a research programme/report, not a predictor: code, checklists and community reproduction practices make submissions inspectable. No multimodal mechanism, independent factory split or unchecked effect size applies. **SQ4:** supports reporting/provenance discipline; a completed checklist does not establish our data-to-result correctness or clean-environment reproduction.

### R35 — optional MSM source

Eunseob Kim, Yuseop Sim, Adrian Shuai Li, Mir Imtiaz Mostafiz, Zachary Van Meter, Martin Byung-Guk Jun, Elisa Bertino and Ali Shakouri (2026). **Multi-sensor and MTConnect dataset of metal cutting anomaly in milling from laboratory and industry settings.** Scientific Data 13, 945. DOI [10.1038/s41597-026-07255-7](https://doi.org/10.1038/s41597-026-07255-7); [primary publisher](https://www.nature.com/articles/s41597-026-07255-7), **PARTIAL indexed Methods/label text; direct full text blocked**.

This is a milling data descriptor, not demonstrated adaptive fusion. Indexed text describes experiment/operation acquisition and labels distinguishing stable cutting, abnormal cutting and tool defect. No qualifying project split, model result or synchronized visual–sensor pairing was audited. **SQ3/SQ4, optional:** external methodology validation needs native pairing, labels, clocks, shared-tool/workpiece groups and protected assessment before fitting; it would use declared dataset-specific learning, not zero-shot transfer.

### Further context, not a new experiment mandate

The review's R01 industrial audio/video anomaly paper and R04 RGB/3D M3DM paper were primary-source screened again ([Stemmer et al.](https://arxiv.org/html/2409.02290v1), [Wang et al.](https://arxiv.org/html/2303.00601v2)). They concern normal-trained whole-weld scoring and spatial product inspection respectively; their result tables are not new project baselines. R09 AST's [original paper](https://www.isca-archive.org/interspeech_2021/gong21b_interspeech.pdf), DOI [10.21437/Interspeech.2021-698](https://doi.org/10.21437/Interspeech.2021-698), was screened as a feasible spectrogram representation, not tested local audio. R16 MBT's [author v2](https://arxiv.org/html/2107.00135v2), preprint DOI [10.48550/arXiv.2107.00135](https://doi.org/10.48550/arXiv.2107.00135), was screened for representation-level attention. These supplementary screenings do not independently audit all their protocols. ViT/video/TS2Vec/MOMENT/MulT/R36 remain contextual sources from the supplied catalogue unless explicitly noted; their presence does not require implementation. The [MulT primary record](https://aclanthology.org/P19-1656/) was checked, but unequal sequence rates are not proof of arbitrary clock-drift tolerance.

## Project evidence identifiers and numerical audit

| ID | Exact source/config/run | What is established here |
|---|---|---|
| J1 / E1 | [PHM retained predictions](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv); [LOEO source](../../scripts/phm2026/results/loeo_evaluation.py); [target ledger](../thesis/TARGET_VERSION_LEDGER.md) | V3-NUM: 20-run MAE constant 0.804156266, sensor-subgroup fusion 0.823785650, PatchTST 0.941455086. Image-only 13-row MAE 1.826411277 is not LOEO. Original image-to-target binding/physical truth not established. |
| J2 / E2 | [feature source](../../src/reassemble/section1_features.py), [branch source](../../src/reassemble/section1_models.py), [Section 1 config](../../configs/reassemble/section1.json), [Section 1 run](../../runs/reassemble/20260927T154732Z-section1), [report](../../artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md) | V3-SOURCE: pretrained frozen CNN, 16-frame mean; 512×22 scratch PatchTST; 220 statistics/logistic. V3-NUM: AP/AUROC below; labels/folds agree across the four inspected branch arrays. |
| J3 / E3 | [stacker](../../src/reassemble/section1b.py), [Section 1B config](../../configs/reassemble/section1b.json), [F2 results](../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json), [gates](../../src/reassemble/section2_models.py), [Section 2 config](../../configs/reassemble/section2.json), [saved OOF arrays](../../runs/reassemble/20260927T192852Z-section2/predictions/oof.npz) | V3-SOURCE architecture/loss distinctions; V3-NUM eight model AP/AUROC. Three-seed averaging/selection and five outer/four inner recording folds are retained protocol/execution evidence. Complete source-cohort identity chain not newly proven. |
| J4 / original SQ3 | [corruption config](../../configs/reassemble/section3_corruptions.json), [protocol](../reassemble/SECTION_3_CORRUPTION_PROTOCOL.md), [handoff](../../artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md) | REPORTED: 0/12 F5/F6 high-severity checks satisfy combined mechanism/outcome criterion; timestamp-preserving faults and shared fallback. No raw perturbation replay here. |
| J5 / E4 | [encoder source](../../00_experiments/rt_detr_encoder_comparison/code/features.py), [resolved config](../../00_experiments/rt_detr_encoder_comparison/results/run_01/resolved_config.json), [report](../../00_experiments/rt_detr_encoder_comparison/results/run_01/comparison/RESULTS_SUMMARY.md) | Prior verified/REPORTED in TASK 3: CNN/hybrid F2 AP 0.440764/0.424979. Different widths and fixed downstream recipes; spatial encoder, no temporal Transformer. |
| J6 / E5 | [noise protocol](../../00_experiments/fusion_noise_test/results/run_02/experiment_plan.md), [report](../../00_experiments/fusion_noise_test/results/run_02/comparison/RESULTS_SUMMARY.md) | Prior verified/REPORTED here: selected one-fold static pipeline AP clean 0.307929, strong sensor noise mean 0.169409. Sensitivity only; no adaptive arm. |
| J7 / E6 | [locked protocol](../../00_experiments/adaptive_fusion_robustness/results/run_01/PROTOCOL.md), [config](../../00_experiments/adaptive_fusion_robustness/results/run_01/config/resolved_config.json), [quality source](../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py), [34-file index](../../00_experiments/adaptive_fusion_robustness/results/run_01/comparison/coverage_and_prediction_index.csv), [comparison](../../00_experiments/adaptive_fusion_robustness/results/run_01/comparison/model_comparison.csv), [intervals](../../00_experiments/adaptive_fusion_robustness/results/run_01/comparison/paired_intervals.csv) | V3-NUM: all 34 hashes, matched sample/recording/segment/label coverage, 196 finite AP values and repeat→severity→family primary aggregation. 753 actions/77 failures/26 recordings. Intervals are REPORTED, not rerun. |
| J8 / E7 | [config](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/config/resolved_config.json), [report](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/comparison/RESULTS_SUMMARY.md) | REPORTED/prior TASK 2 checks: frozen five epochs versus tuned two; F2 gain not established. Unequal budgets prevent pure tuning attribution. |
| J9 / E8 | [protocol/config](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/PROTOCOL.md), [resolved config](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/resolved_config.json), [report](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results/comparison/RESULTS_SUMMARY.md) | REPORTED/prior checks: matched two-epoch, 32-frame, two-seed comparison; F2 changes −0.000796/−0.002822, intervals include zero; cause remains unresolved. |
| J10 / September extensions | [handoff](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md), [execution config](../../configs/reassemble/additional_improvements/execution.json) | Report inspected, numbers REPORTED: S-LONG−short +0.0297; same-sensor hybrid−statistics +0.0110; anchored adaptive−A0 clean +0.0210; matched robustness +0.0097, interval includes zero. Distinct models/protocols. |
| J11 / pooling | [boundary-aware report](../../artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md) | REPORTED: selected last-quarter visual AP 0.319146; its separate static F2 AP 0.493437. Same-cohort selection, no combined-best model and no online result. |
| J12 / assurance | [TASK 2B decisions D19–D21](EXPOSE_ALIGNMENT_DECISION.md); [PHM patch source](../../src/phm2026/models/patchtst/model.py); [F2 protocol](../reassemble/SECTION_1B_PROTOCOL.md) | Preserve reported 64-clip one-reviewer audit (57/59 determinate agreements), PHM patch-grid/effective-config concern, and F2 global-OOF internal threshold qualification. No neural forward test, raw adjudication or code correction performed. |

### V3-NUM results: one compatible core comparison

Core arrays contain 4,530 rows, 509 failures, five fold IDs; 148 recordings is the retained cohort/protocol count, not independently recovered from identifier-free arrays. Failure prevalence is approximately 11.24%.

| Model / representation | AP | AUROC |
|---|---|---|
| Action-only | 0.180805327 | 0.685089918 |
| U1 statistics/logistic | 0.429391869 | 0.779324558 |
| U2 frozen CNN | 0.230658315 | 0.697794829 |
| Scratch PatchTST | 0.241591244 | 0.705351424 |
| F1 probability average | 0.445742313 | 0.795061194 |
| F2 probability stacker | 0.447298551 | 0.794968361 |
| F3 feature concatenation | 0.412231495 | 0.785584424 |
| F4 action gate | 0.443725322 | 0.781506130 |
| F5 quality gate | 0.444549294 | 0.775986972 |
| F6 combined gate | 0.441355891 | 0.775523296 |

F2−U1 AP = **+0.017906682** (V3-NUM); historical paired 95% interval **[+0.008602700,+0.028284280]** is REPORTED. F2 does not maximize every metric: F1's AUROC point is slightly higher. Do not interpret every decimal difference as established superiority.

October pilot primary mean AP (V3-NUM): augmented static A **0.253996215**, additive quality B **0.237359724**, interaction C **0.257008541**. C−A **+0.003012326**; REPORTED interval **[−0.026710962,+0.032165450]**. Clean C−A **+0.004771136**; REPORTED interval **[−0.034258,+0.044544]**. These do not establish superiority, equivalence or clean noninferiority. The pilot protocol's strict no-clean-cost claim used a zero-loss criterion; TASK 2B's example practical 0.01 margin was not approved for a new study.

**Audit method:** Python `-B`, NumPy/Pandas/sklearn only, no project imports. Read Section 2 `oof.npz` and four Section 1 `*_perm00.npz`; check equal labels/folds; calculate `average_precision_score` and `roc_auc_score`. Read each index-selected pilot table with `float_precision='round_trip'`, verify its SHA256 and sorted identity/label columns, compute AP on finite outputs, then average repetitions, severities and the two primary Gaussian-noise families equally. Compare those means to the saved table within `1e-12`. Compute mean absolute PHM CSV errors by model. Forty-two compact saved artifacts were hashed; no models, inputs, bootstrap or historical files were regenerated. The index retains all 34 per-table source hashes. These checks establish arithmetic/selected coverage, not raw supervision, historical fitting provenance or independent label truth.

Compact numerical-evidence identifiers: core Section 2 OOF SHA256 `e2ca736b2dccdb33a1dfc0cf33c2001a3b69cdb2d8ef82d5241c4f34b740995a`; pilot index SHA256 `6e145c452b1622eee36f7b5dda94f927722ea29708ba7b0ba805f824583f9e4f`. The SHA256 of the 42-entry input-path/hash dictionary, serialized as sorted-key compact JSON, is `591a494453ecada91474e855dc324de4e12f1de148a6000b2ae95d83853a4ed4`. Individual pilot file hashes remain available in the linked index. The separately inspected quality-training table's hash matches its completion record; only its header/hash were newly checked, not its entire training lineage.

## SQ1 evidence matrix

> Which lightweight or pretrained Transformer-based representation components are suitable for visual, audio, and sensor time-series data in a multimodal industrial anomaly detection pipeline?

| Requested field | Evidence and assessment |
|---|---|
| A — exact question | Quoted above from exposé p.2. Suitability includes target, budget, pretraining, temporal information and feasibility; it does not require every candidate to win. |
| B — foundations | Representation reuse differs from architecture execution. A pretrained detector can supply only CNN maps. Frame averaging is permutation-invariant; increasing coverage does not add temporal-order modelling. Scratch Transformer training is not pretrained transfer. |
| C — published evidence | R06/R10 justify candidate components for different original tasks. R23 shows suitability varies across tasks/costs. None establishes which branch must win here; audio-model feasibility does not establish local audio eligibility. |
| D — matching components | Frozen pretrained CNN→spatial means→16-frame mean→learned head; separate spatial hybrid encoder test. Statistics use ten values per 22 channels; separate scratch HF PatchTST classification. PHM has a different custom variable-length Transformer. |
| E — exact project evidence | J1/J2/J5/J8/J9/J10/J11; inspect `section1_features.py::load_visual/extract/statistics`, `section1_models.py::SensorHead`, encoder `features.py`, configs and run paths in the register. |
| F — measurements | V3-NUM core AP statistics 0.429392, PatchTST 0.241591, visual 0.230658. J5 REPORTED fixed-recipe hybrid F2 is lower than CNN. Longer PatchTST training improves its matched short recipe but remains below statistics; E8 tuning is inconclusive. |
| G — negative/contrary evidence | These results contradict superiority of the tested complex recipes within their protocols. They do not demonstrate that temporal information, audio or all Transformers are ineffective. Last-quarter pooling's REPORTED gain indicates appearance coverage matters. |
| H — not implemented | Predictive audio/AST/trimodal experiments; broad pretrained time-series transfer; core temporal visual attention; every candidate ViT/video family. No detection boxes were trained in the core. |
| I — answer strength | **PARTIALLY SUPPORTED overall; adequate bounded comparison of the selected visual/sensor recipes.** Architecture selection can favor statistics/CNN features. Original audio and pretrained-family breadth require explicit scope qualification. |
| J — remaining gap | Explain pretraining/source/checkpoint provenance and feasibility exclusions; get researcher/supervisor acceptance of coverage. Additional Transformer variants are unnecessary merely to satisfy a model-name list. |

## SQ2 evidence matrix

> How do unimodal baselines, simple concatenation fusion, modular late fusion, and process-aware gated cross-modal fusion compare in terms of predictive performance?

| Requested field | Evidence and assessment |
|---|---|
| A — exact question | Quoted above from exposé p.2. The adapted comparison is bimodal; literal projected-feature gating/trimodal coverage is incomplete. |
| B — foundations | Extra information can improve the best population predictor if its class contains the unimodal predictor; finite fitting, regularization and shift can reverse observed gains. Equation-level mechanisms matter more than inconsistent “early/late” terminology. |
| C — published evidence | R13 establishes stacking; R15 establishes feature gates; R02/R37 provide direct but differently evaluated industrial fusion; R23 supports comparisons including simple references. None predicts a universal winner here. |
| D — matching components | U1/U2; F1 probability mean; F2 unrestricted affine probability stacking; F3 representation concatenation; F4–F6 normalized scalar-logit gates. September anchored adaptation and October interactions are distinct follow-ups. |
| E — exact project evidence | J2/J3/J10, `section1b.py::fit_stacker`, `section2_models.py::ConcatHead/DecisionGate/context/fit_head`, `section2.json`, original OOF arrays. |
| F — measurements | V3-NUM core table above: F2 improves AP over U1; F3 and original gates do not surpass F2. J10 REPORTED anchored clean gain is +0.0210 [0.0015,0.0419], with recall/ECE trade-offs; J11 pooling is a separate selected static study. |
| G — negative/contrary evidence | Original-gate superiority fails the tested clean criterion. “All adaptation failed” conflicts with J10; a cross-protocol leaderboard or a combined-best architecture has no supporting run. F2's advantage alone does not isolate unique visual information from the added fitting/calibration stage. |
| H — not implemented | Literal shared-embedding gated architecture from §5.5, tri-modal comparison, or controlled matching of every function class/capacity/calibration. F3 uses projected visual features and sensor statistics, not a PatchTST-based multimodal embedding pair. |
| I — answer strength | **SUPPORTED WITHIN SCOPE for the comparative ranking of fixed recipes; PARTIALLY SUPPORTED against the full original architecture/modality programme.** Negative comparisons are legitimate answers. |
| J — remaining gap | Freeze the core table and protocol-specific follow-up labels. If claiming information complementarity rather than predictive increment, a matched sensor-only meta-calibration reference may be needed; no such new fit is performed here. |

### Exact fusion contracts

| Model | Actual combination and interpretation |
|---|---|
| F1 | `(p_v+p_s)/2`; probability averaging, not logit averaging. |
| F2 | `sigmoid(b + beta_v*p_v + beta_s*p_s)`; logistic stacker, unrestricted signs/magnitudes and an intercept. |
| F3 | Separately project the 128-dimensional visual representation and 220 sensor statistics to 128 dimensions, concatenate, then classify. Distinct training/loss/calibration from the scalar gates. |
| F4/F5/F6 | Softmax gate on action+availability / quality+availability / both; combine calibrated branch logits and sigmoid. No final intercept/calibrator. Context changes output through allocation only. |
| September anchor | Fixed F2 anchor with bounded multiplicative coefficient adjustments: `sigmoid(b + sum(a*(1+tanh(h(u)))*p))`. Coefficients are not normalized trust shares. |
| October A/B/C | A: two probabilities, 3 fitted parameters including intercept. B: probabilities+8 q, 11 parameters. C: probabilities+q+two sets of p×q terms, 27 parameters. Same parent weights/augmentation; unequal capacity. |

## SQ3 evidence matrix

> Can a gated cross-modal fusion architecture improve robustness when one or more modalities are missing, degraded, or unreliable?

| Requested field | Evidence and assessment |
|---|---|
| A — exact question | Quoted above from exposé p.2. H-SQ3-Q narrows this to observable quality versus matched static fusion under a declared fault mixture and clean constraint. |
| B — foundations | Measurement quality, model confidence and conditional prediction reliability differ. `E[w L]=E[w]E[L]+Cov(w,L)` motivates informative allocation; it is not an AP theorem. For C, `c·q` predicts directly while `d·(p q)` changes coefficients; either can track label content. |
| C — published evidence | R18's conditional bound, R19's evidence assumptions, R20/R21's availability training and R02/R37's industrial precedents justify controlled questions. They neither validate our quality proxies nor require positive adaptation. |
| D — matching components | Original F5/F6 stress tests, fixed-static noise pilot, explicit masks/fallback, September augmentation comparison, October A/B/C pilot. Eight observable q features are not eight verified reliability measurements. |
| E — exact project evidence | J4/J6/J7/J10; timestamp-preserving corruption config; `quality_fusion.py::design/route`; locked primary aggregation and [reported pilot contrasts](../../00_experiments/adaptive_fusion_robustness/results/run_01/comparison/paired_intervals.csv). |
| F — measurements | J4 REPORTED 0/12 combined success checks. V3-NUM C−A +0.003012; REPORTED interval spans −0.026711 to +0.032165. J10 matched robustness +0.0097 interval spans zero. Clean C−A interval also permits harm. |
| G — negative/contrary evidence | Correct-direction allocations for some original sensor faults do not yield a qualifying outcome advantage. E5 establishes static noise sensitivity only. Additive q hurts the pilot's primary AP; interaction recovery versus B is not proof of C superiority versus A or of reliability attribution. |
| H — not implemented | Explicit clock offsets/drift, predictive audio degradation, validated reliability/content decomposition, external industrial generalization. Shared missingness fallback cannot identify a difference between otherwise differently fitted heads. |
| I — answer strength | **PARTIAL with bounded negative and INCONCLUSIVE findings.** Current evidence is sufficient to say the original tested gates did not establish the specified advantage; H-SQ3-Q remains inconclusive. General dynamic-fusion impossibility is not supported. |
| J — remaining gap | Supervisor decision: accept the honest bounded answer or justify a specific claim requiring further controls. Wider existing-fold coverage improves precision/heterogeneity coverage but cannot restore pristine assessment status. No new training is automatically essential. |

Both-absent states must be reported as unavailable/abstain, with coverage denominators. A structural fallback's equality is by construction; it is not statistical evidence of general equivalence. Time-block dropout, frame loss, temporal pooling and true clock misalignment are separate interventions.

## SQ4 evidence matrix

> How can multimodal architecture performance be evaluated beyond accuracy, including robustness, interpretability, modularity, and practical usability?

| Requested field | Evidence and assessment |
|---|---|
| A — exact question | Quoted above from exposé pp.2–3. The question supports a critical evaluation framework, not a requirement to certify deployment. |
| B — foundations | AP measures ranking and is prevalence-sensitive; Brier/log scores measure probability quality; thresholds encode decisions. Clustered observations and overlapping training fits constrain uncertainty. A bootstrap of fixed scores does not cover the full learning/selection process. |
| C — published evidence | R25/R26 motivate selection/leakage audit; R27/R28/R34 separate calibration/probability quality/shift; R29 covers imbalance; R33 limits naive CV variance; R30/R31 require specific interpretation tests; R32/R23 motivate inspectable provenance and costs. |
| D — matching components | AP/AUROC, selected thresholds/confusion/recall/precision, Brier/ECE, paired recording resampling, context ablations, modular branches, manifests and warm component timings. |
| E — exact project evidence | J3/J4/J7/J9/J10/J12; `section2_models.py::fit_head` explicitly excludes branches/transfer/preprocessing from warm timing; [pilot runtime](../../00_experiments/adaptive_fusion_robustness/results/run_01/provenance/final_runtime.json); saved comparison/interval tables. |
| F — measurements | V3-NUM reproduces AP/AUROC and selected coverage only. Other decision/calibration/time values remain REPORTED. J10 anchored AP gain coincides with lower failure recall/higher ECE. E8's small threshold-0.5 recalls do not imply a signal-free ranking. |
| G — negative/contrary evidence | Repeated test exposure prevents a fresh-confirmatory label; folds/realizations/seeds are not new independent recordings. Gate weights are computation, not calibrated trust or causal importance. Warm timing excludes the acquisition window. |
| H — not implemented | Prospective online decisions, operator utility/usability study, calibrated shifted reliability guarantee, verified plug-and-play branch replacement, full clean-environment reproduction or population label adjudication. |
| I — answer strength | **PARTIALLY SUPPORTED; adequate framework and substantial reported evaluation, with remaining claim-specific assurance.** The absence of deployment validation must be stated rather than replaced with offline AP. |
| J — remaining gap | Consolidate compatible saved metrics, threshold provenance, cost trade-offs, group hierarchy and source/label limitations into the thesis evidence package. Retain F2's disclosed training-side global-OOF threshold qualification; it is not a newly proven outer-test leak. |

A globally strictly increasing score transformation preserves within-set AP (subject to ties/numerics), but separately fitted fold calibrators can change **pooled cross-fold** ordering. Therefore a pooled AP gain must not automatically be attributed solely to new modality information or solely to calibration. Do not fit/report a preferred threshold on exposed assessment labels as a validated operating point.

## Synthesis and stop boundary

The smallest defensible contribution is a modular implementation plus a careful comparison of selected representations/fusion mechanisms, with a bounded robustness answer and explicit feasibility/evaluation limits. PHM difficulties are development findings, not retrospectively planned novel contributions. A new dataset or model does not repair old provenance or recover an untouched REASSEMBLE test set.

The [claim audit](TASK3_CLAIM_AUDIT.md), [experiment decisions](TASK3_EXPERIMENT_DECISIONS.md) and [executive handoff](TASK3_EXECUTIVE_HANDOFF.md) use this same evidence hierarchy. No source PDF, historical result, code, dataset or TASK 2B document was changed. No training, GPU job, dataset download or new experiment was executed. **STOP after TASK 3 handoff.**
