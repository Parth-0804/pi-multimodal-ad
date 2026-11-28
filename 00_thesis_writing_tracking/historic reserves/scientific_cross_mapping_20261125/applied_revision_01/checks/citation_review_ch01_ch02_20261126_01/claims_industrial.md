# Chapters 1–2: industrial citation passage audit

Inspected 30 assigned existing works: 26 local PDFs, three MDPI publisher HTML originals, Chen’s author-uploaded manuscript, and the final Sui VOR obtained from DTU Orbit. No manuscript, bibliography, library or existing attachment was changed.

## Verified locator repairs

|Chapter/file line|Key|Original locator|Verified replacement|
|---|---|---|---|
|chapters/02_literature_review.tex:159|Hua2026Weld|PDF pp.~12, 15|6708, 6711|
|chapters/02_literature_review.tex:567|Hua2026Weld|PDF pp.~18, 22, Tables~1--3|Tables~1--3|
|chapters/02_literature_review.tex:788|Hua2026Weld|PDF pp.~18, 22, Tables~1--3|Table~3|
|chapters/02_literature_review.tex:1396|Zeng2026ViFailback|PDF pp.~7--8, Tables~2--4|Tables~2--4|
|chapters/02_literature_review.tex:630|Huo2022Multisensor|PDF p.~7, Table~VII|Table~VII|
|chapters/02_literature_review.tex:782|Huo2022Multisensor|PDF p.~7, Table~VIII|Table~VIII|

## Open decisions

### C2-IND-01: Chen2023Multisensor, Chapter 2 line 368

Keep the interpretive wording or approve a narrower statement that TCP positions register sensor features/predictions and are not one of the 27 listed sensor features. Current broad claim about position not being predictive is stronger than what this experiment establishes.

Exact manuscript passage: The digital twin study maps sensor features to robot TCP positions, showing how position can establish correspondence even if it is not, in any normal sense, a predictive feature \citep{Chen2023Multisensor}.

Source basis: Author manuscript §§3.4–3.5, pp. 19–21; publisher VOR inaccessible; manuscript-to-VOR equivalence not verified.

### C2-IND-02: Xie2025Audiovisual, Chapter 2 line 643

Remove Xie from exact late fusion terminology claim, or approve late or decision-level fusion wording while retaining its representation-leveldescription. Do not silently alter scientific prose under citation-only scope.

Exact manuscript passage: Some papers also use the term 'late fusion' to describe representation-level integration prior to classification \citep{Wang2020What,Xie2025Audiovisual}. That underlines the importance of knowing what information you are actually fusing.

Source basis: Original author manuscript§4.2 printed p. 22 and Figure 7 printed p. 21 uses decision-level fusion. No literal late fusion term found; cited method does concatenate representations.

## Resolved version boundary

Sui2026Incomplete: final author-institution VOR confirms the 2026 publication year, Information Fusion 126, Article 103572 and DOI 10.1016/j.inffus.2025.103572. Printed pp. 3–4 (§3, §3.2 and Fig. 2), corresponding to PDF viewers 4–5, support multimodal training and single-input inference. Retain the existing key and final-publication metadata. The older local cmdiad.pdf was not replaced.

## Source-level verification

### AlDulaimi2019A — VERIFIED

Version of record, Computers in Industry 108 (2019), 186–196. PDF viewers 5–7 = printed 190–192; viewer 9 = printed 194, Tables 2–3.

Both CNN/LSTM branches process selected telemetry; C-MAPSS is simulated; 14 channels, window lengths 30/15 and RMSE/asymmetric score documented. The differing observation-window results are supported.

### Altinses2023Fuzzy — VERIFIED

IECON 2023 conference author/manuscript PDF with IEEE DOI banner. PDF viewer 3, failure augmentations; viewers 4–5, dataset/setup. No visible printed page numbers..

Gazebo synthetic UR5 pose regression; twenty-step, stride-one windows; randomly selected 75/25 train/test examples. Full replacement by noise/zero/one is documented separately from partial corruption. The overlap/dependence caveat is an inference from this protocol, not an observed leakage measurement.

### Altinses2025Performance — VERIFIED

Version of record, Machine Learning with Applications 21 (2025) 100691. Printed/viewer 13–14, Table 7.

Synthetic benchmark reconstruction/cross-modal/downstream tasks are documented. Table 7 test MSE ×10^-3: clean 2.1745±0.8084; Base+CGAN 13.472±2.4016; fine-tuned baseline+CGAN 2.7228±1.6322. Existing clean-vs-unadapted replacement comparison is accurate.

### Bevans2023Heterogeneous — VERIFIED

Version of record, Virtual and Physical Prototyping, 2023. Printed/viewer 8–9, §2.3; 23–24, validation results.

Separate third validation build with modified orientation/layout and processing conditions is documented. Some validation geometries lacked porosity; authors explicitly reserve false-negative/F-score validation under excessive porosity. The current distinction of assessment-domain access is supported.

### Chen2023Multisensor — VERIFIED_WITH_VERSION_LIMIT

Author-uploaded 37-page manuscript (uploaded by Lequn Chen 28 May 2023); VOR publisher access failed (403). Author manuscript pp. 19–21, §§3.4–3.5; Figure 11.

Freshly read original author manuscript in ResearchGate full-text HTML. TCP positions register features and prediction outputs to spatial locations, with Approximate Time Synchronizer and 33-ms threshold. Predictor feature list is 27 sensor features (4 thermal, 9 vision, 14 acoustic). Manuscript-to-VOR equivalence is not verified.

Original source: https://www.researchgate.net/publication/371110062_Multisensor_fusion-based_digital_twin_for_localized_quality_prediction_in_robotic_laser-directed_energy_deposition

### Chu2024A — VERIFIED_PUBLISHER_HTML

Publisher version of record, Sensors 24(16) (2024), 5120. §§2.1, 3.4, 4.1–4.3 (HTML; no PDF pagination used).

Official publisher full text verifies labeled source/unlabeled target domain adaptation with acoustic/vibration signals across speed/load conditions. This is target-adaptive transfer, not unchanged-model assessment without target access.

Original source: https://www.mdpi.com/1424-8220/24/16/5120

### Goodarzi2023Deep — VERIFIED

Local author-preprint, Deep convolutional neural networks for cyclic sensor data, 2023. PDF viewer 3, §III results and Fig. 3; no visible printed pagination.

Hydraulic CNN all-17-sensor error 20.5%; best single sensor PS1 error 1.7%; conventional independently engineered baseline all-sensor error 1%. Current comparison accurately identifies the CNN result; do not generalize the all-sensor loss to every representation.

### Gu2024Improved — VERIFIED_PUBLISHER_HTML

Publisher version of record, Applied Sciences 14(5) (2024), 2182. §§3.2, 4; Table 3 (HTML; no PDF pagination used).

Table 3 SE-ResNet50 composite class 99.31% vibration vs 99.50% fusion. §4 prose reports a different composite-fault improvement; §3.2 states validation:test=3:7, not a clear complete training partition. Caution about small effects and reporting ambiguity is supported; repetitions are not explicitly established.

Original source: https://www.mdpi.com/2076-3417/14/5/2182

### Hua2026Weld — VERIFIED

Publisher version of record with cover: Nondestructive Testing and Evaluation 41(10) (2026), 6698–6721; online 2025. Cover viewer 1; viewers 12/15 = printed 6708/6711; viewer 18 = printed 6714 Tables 1–2; viewer 22 = printed 6718 Table 3.

Tables 1–2 report Ours audio/image each 100%; Table 3 Ours fused clean 100%, interference 93.33%. §3.1 gives 600 paired acquisitions; §3.2 later describes 600 images and 600 GASF per state and 560/20/20 split. Acquisition/training counts are inconsistent in the source. VMD/GASF and molten-pool images documented. No verified weld-run-disjoint split.

### Huang2026Rolling — VERIFIED

Publisher version of record, Electronics 15 (2026), 1631, Huang and Tong. Printed/viewer 10–13, student/weighting; 18 target split; 23 online description; 24–26, gated/noise ablations.

GAF-Net uses gated progressive feedback and distillation. Training describes 278 mixed features including 256 teacher dimensions, whereas online description says 22 handcrafted inputs and no teacher; retained ambiguity is warranted. Source training/target-validation/target-test roles and Gaussian test-noise experiments are explicit.

### Huo2022Multisensor — VERIFIED

Version of record, IEEE TIM 71 (2022), article 3500412. PDF/internal article page 6 (fixed alpha=0.5 and 10-fold CV); page 7 Tables VII–VIII; pp. 8–9 bias/stuck faults. Headers show article ID, not a journal page range..

Opened/rendered original page 7. Table VII: 100% fused, 99.06% CNN-IRT, 96.32% CNN-vibration. Table VIII at -2dB: 95.26→97.6% with fault-free vibration; 36.86→94.2% with fault-free IRT. Fixed equal evidence-discount weights; no online adaptive quality inference established.

### Kim2026MSM — VERIFIED

Version of record, Scientific Data 13 (2026), 945. Printed/viewer 2, overview; 9–10, labels/annotation/camera coverage.

Native labels: 0 normal, 1 abnormal requiring stoppage, 2 defective tool under otherwise normal cutting; if defective tool causes abnormal cutting assign1. Lab smartphone videos through automatic-door window and laboratory coverage are explicit. Current task-specific description is supported.

### Kullu2022A — VERIFIED_PUBLISHER_HTML

Publisher version of record, Machines 10(11) (2022), 1105. Abstract; §4; §§5–6 (HTML; no PDF pagination used).

Vibration/current raw series plus their STFT spectrogram representations, encoded with 1D/2D CNNs and concatenated, directly supported. Distinguish two sensors from four representation inputs.

Original source: https://www.mdpi.com/2075-1702/10/11/1105

### Li2022A — VERIFIED

Version of record, Journal of Manufacturing Processes 84 (2022), 913–926. Viewer 2 = printed914, reference labels; viewer8=920, registration limitation; viewer12=924, Table3.

Photodiode and microphone streams are encoded as images; no physical process camera stream. Microscopy/Archimedes density supply quality classes. Authors explicitly state data registration absent. Table3 includes gains and losses by architecture (e.g. LSTM fusion90.35 vs acoustic92.13). Existing bounded claims supported.

### Li2025MADFlow — VERIFIED_WITH_VERSION_LIMIT

Accepted/preprint manuscript with Highlights cover; body footer says Preprint submitted to Elsevier. Viewer 11 = body printed Page 10 of15; Table6.

Table6 compares direct concatenation, CMA-based addition, and CDCF; direct concatenation I-AUROC70.3 vs CDCF97.6 in MVTec 3D-AD ablations. Supports protocol-specific alignment/concatenation statement. VOR pagination/equivalence not checked.

### Li2025PGMTKD — VERIFIED

Version of record, MSSP 239 (2025), 113296. Printed/viewer3 overview; 4–5 physical pressure model;8 teacher-loss weighting.

Pressure/vibration multi-teachers transfer into pressure-only 1D-CNN student. Physics teacher explicitly models pressure; CE losses enter teacher weights during training. These are not deployment quality weights. Existing distinctions supported.

### Ma2025A — VERIFIED

Version of record, Measurement256 (2025),118278. Printed/viewer4 offline/online algorithm;8 case study.

Historical missing fault images are supplemented by AIGAN before classifier training; this is not simply inference-time removal of one stream from a frozen full-input model. The thesis correctly distinguishes an availability regime.

### Pandiyan2022Deep — VERIFIED

Version of record, Additive Manufacturing58 (2022),103007. Printed/viewer4–5 apparatus/X-ray confirmation;13 conclusion.

Operando X-ray confirms lack-of-fusion/conduction/keyhole regimes; optical emissions/acoustics and CNN–LSTM windows classify process states. Different input durations alone do not establish pre-event warning. Existing source attribution supported, early-warning limit is methodological inference.

### Petrich2021Multimodal — VERIFIED

Version of record, Additive Manufacturing48 (2021),102364. Printed/viewer4–6 registration/CT labels;11 Table3.

Post-build CT labels are registered to voxel grid; time-of-flight acoustic compensation and synchronized/rasterized modalities documented. Table3 threshold0.5 gives accuracy.9921/precision.2487 with295 flaws and113065 non-flaws; higher thresholds change precision/recall. Thesis numbers correct.

### Shangguan2025CPIR — VERIFIED

Version of record, Advanced Engineering Informatics65 (2025),103240. Printed/viewer5–6 mapping/scoring;8 Tables3–4 and §4.3.

Prediction/reconstruction discrepancy maps are aggregated (multiplication/add/max ablations), not necessarily probabilities. Table3 CPIR6.93FPS vs CFM12.29FPS, I-AUROC.974vs.954. Speed/performance trade-off statement supported within reported setup.

### Sliwowski2025REASSEMBLE — VERIFIED

arXiv 2502.05086v2, local author manuscript, 2025. PDF viewers10–11 TAS;12–13 ConditionNET execution/visual condition checks; no printed page numerals used.

Source benchmarks temporal action segmentation and ConditionNET precondition/effect/unsatisfied-state assessment from wrist RGB. This is distinct from thesis completed-action failureAP. Existing broad publication-task description supported.

### Sui2026Incomplete — VERIFIED

Publisher version of record: Information Fusion 126 (2026), Article 103572; available online 12 August 2025. Retrieved read-only from author institution DTU Orbit; institution cover plus 13 article pages.. VOR printed p. 3, §3 (PDF viewer 4); printed p. 4, §3.2 and Fig. 2 (PDF viewer 5); results tables in §4. The institutional cover creates a one-page viewer offset..

The final VOR confirms multimodal training with single-modality inference: frozen RGB/point-cloud feature extractors, cross-modal distillation for hallucinated missing information, and memory-bank decision fusion. §3.2 specifies distillation from one available modality into missing inputs/features; Fig. 2 explicitly illustrates point-cloud-only inference. Thus the thesis reduced-input inference claim is supported by the final 2026 publication. Existing citation key and 2026 year are correct. Local cmdiad.pdf remains the older September 2024 v3; it was not replaced.

Original source: https://backend.orbit.dtu.dk/ws/portalfiles/portal/411468522/1-s2.0-S156625352500644X-main.pdf

Final VOR SHA-256: bdb39405dde1bd319cebef08b256e3c1c47eff070d743063ea1e564eaf59c321

### Thoduka2024Handover — VERIFIED_WITH_VERSION_LIMIT

ICRA 2024 work; local attachment is arXiv 2402.18319v2 dated 25 August 2025 with separate copyright cover. PDF viewer 4 participant split/classes; 5–6 fusion/5 runs;7 Tables III–V and §§V–VI; no printed page numerals visible.

Five outcomes; participant-disjoint337/101/151 split reported. Table III I3D-D video+FT 69.1±1.5 vs all three 67.9±3.3; five training runs on fixed test data. §VI explicitly says post-trial classifiers; online causal predictions future. Table V cross-robot fitting/assessment verified. Source does not supply thesis participant-ID mapping.

### Wan2024Pipeline — VERIFIED

Version of record, Machines12 (2024),921. Printed/viewer8–9, §3 and apparatus.

Two acoustic sensors provide both sound and statistical vibration descriptors, with CNN-derived features. Current distinction between physical input source and derived descriptors is supported.

### Wang2025A — VERIFIED

Version of record, Information Fusion115 (2025),102739. Printed/viewer3–4, §§2.1–2.2.

Source domains/target domain are vibration datasets from operating conditions/machines; feature and decision fusion are domain-level/adversarial operations. Supports domain fusion rather than a new physical camera/sensor modality.

### Xie2025Audiovisual — VERIFIED_WITH_ATTRIBUTION_ISSUE

Original author manuscript with own printed pages; VOR equivalence not checked. Printed/viewer8–9 apparatus;printed p. 22 §4.2 and Figure 7.

Coaxial CCD melt-pool camera and microphone are actual modalities. §4.2 calls representation concatenation without further hidden layers decision-level fusion; the literal term “late fusion” is absent in extracted original. Current citation supports terminology inconsistency but not exact attribution of the term “late fusion”.

### Xu2025ModalityResilient — VERIFIED

Version of record, Sensors25 (2025),6529. Printed/viewer19–20, significance prose andTables7–9.

Prose claims AST/BTF/ShapeGuided/M3DM p<.05, whereas Table7 reports.056/.051/.505/.071. Existing conflicting-significance caution is supported. Table8/9 df3 vsTable7df9 warrants explicit comparison-unitcare; do not call allthese independent training repetitions.

### Yang2024Fault — VERIFIED

Version of record, IEEE TII20(8) (2024),10366–10375. Viewers2/4–5=printed10367/10369–10370.

Harmonic-drive study combines vibration with servo signals including motor current/speed; trained full-modal information is used for missing-vibration inference. Source supports physical-modal distinction.

### Ying2025Trustworthy — VERIFIED

Version of record, Information Fusion124 (2025),103377. Printed/viewer3 evidence/Dirichlet combination;12 noise;17–19Table9.

Acoustic/IR image fusion uses Dirichlet evidence and simplified Dempster–Shafer aggregation. Synthetic Gaussian, impulse and periodic interference are evaluated. Broad thesis controlled-degradation/evidence-aggregation statements supported.

### Zeng2026ViFailback — VERIFIED

CVPR2026CVF open-access acceptedversion. Viewers7–8=printed 42392–42393,Tables2–4.

ViFailback benchmark evaluates failure-detection/localization/reasoning and low-/high-level correction VQA, then robot correction success. Current distinction from thesis binary episode classifier is supported.

