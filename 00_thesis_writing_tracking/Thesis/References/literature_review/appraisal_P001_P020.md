# Full-text appraisal P001–P020

Twenty papers were appraised from relevant full-text methods/results and decisive visual inspection. Numerical claims refer to supplied-version PDF pages. This is source verification, not experiment reproduction or an exhaustive review of every appendix. No Zotero changes were made by this subtask.

## P001 — EPIDIR: Integrating external frequency prompts and internal statistical decoupling for infrared image restoration

**Role:** Out-of-core single-modal IR restoration. **Questions:** SQ1 peripheral;SQ3 indirect. **Decision:** Exclude core fusion.

**Read version:** Publisher version; Neurocomputing 701 (2026), article 134552; available online 20 July 2026.

**Target/unit:** IR image restoration; image/patch PSNR and SSIM.

**Physical inputs:** Infrared imagery only.

**Fusion:** Frequency-prompt/SNR image restoration, not physical multimodal fusion.

**Controls:** Other IR restoration networks, including AdaIR.

**Split/independence:** 80/20 train/validation images; independent test not established.

**Robustness:** missing: Not tested; noisy: Synthetic noise, blur, contrast, coupled image corruption; shifted: No machine/domain shift established.

**Reported evidence:** PDF p8 Table2 hard USM PSNR17.7434/SSIM0.6064. Table1 HM blur PSNR31.5635 below AdaIR31.7097, SSIM0.9136 above0.9101.

**Limits:** No fault labels. Means/SD do not alone establish significance. Exclude core fusion.

Text pages: [3, 7, 8]; decisive visual pages: [8]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\1-s2.0-S0925231226019508-main.pdf`; SHA256 `b3cdae4fb292379f57081b4bd416cd365100952277700b4109a8b70492650fcd`.

## P002 — Rotating machinery fault diagnosis based on convolutional neural network and infrared thermal imaging

**Role:** Direct industrial unimodal thermal diagnosis. **Questions:** SQ1 CNN;SQ2 unimodal;SQ4 split. **Decision:** Retain background, not fusion.

**Read version:** Publisher version; Chinese Journal of Aeronautics 33(2) (2020), 427–438; available online 5 September 2019.

**Target/unit:** Ten-state rotating-machine classification; thermal frame.

**Physical inputs:** Thermal camera only in main classifier; vibration separately.

**Fusion:** CNN; pooling temperature-region examples is not modality fusion.

**Controls:** DBN/DNN/SAE thermal comparators; separate vibration entropy classifier is not matched.

**Split/independence:** 35/65 percent thermal image split,20 trials; independent runs/sessions not established.

**Robustness:** missing: Not tested; noisy: Temperature/warm-up variation; no controlled sensor corruption; shifted: Fixed3000rpm rig; no cross-machine test.

**Reported evidence:** PDF p9 Table8 CNN98.59percent(3845/3900),SD0.00591. Separate vibration75.38percent(489/650), pp8/10.

**Limits:** Different vibration denominator/representation. Prose/table disagreements: CNN98.64 vs98.59; SAE88.20 vs87.18. IR+vibration fusion future work.

Text pages: [5, 6, 7, 8, 9, 10]; decisive visual pages: [9]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\1-s2.0-S1000936119303127-main.pdf`; SHA256 `2e0166b63050f2d555050920b088ed5561a33e7120c9d3e503fa08d46e3e7fec`.

## P003 — DMAW: A Dynamic Multimodal Measurement Fusion Network With Attention for Reliable Welding Process Monitoring Under Harsh Industrial Environments

**Role:** Direct industrial visual-acoustic welding. **Questions:** SQ1 encoders;SQ2 fusion;SQ3 motivation only;SQ4 latency. **Decision:** Retain priority, qualified.

**Read version:** Author postprint in KITopen; article IEEE Sensors Journal 26(2) (2026), 2347–2358; article DOI independently confirmed by KITopen.

**Target/unit:** Four welding-state classification;20-frame/audio pair, total pair count unclear.

**Physical inputs:** Process images plus audio, not continuous machine telemetry.

**Fusion:** Frozen adapted ViT branches; self/cross attention, category-dependent prediction mixture, gradient balancing.

**Controls:** Image ViT90.2percent and audio ViT84.4percent; fusion variants.

**Split/independence:** 13,000 images,37fps,44.1kHz audio,20-frame pairs; split/group unit, repeats and CI not specified.

**Robustness:** missing: No controlled absence test found; noisy: Harsh-environment motivation; no graded noise experiment found; shifted: No held-out machine/condition or synchronization-shift protocol found.

**Reported evidence:** PDF p7 TableIII DMAW accuracy96.1/precision96.4/recall96.3/F1 96.8percent; averaging undefined. p9 TableV sum90.5/gate92.6/FiLM93.7/gradient control93.4/dynamic96.1.

**Limits:** Parameter/thickness by class and unknown split confound claims. Pulsed-MIG setup prose versus laser parameters inconsistent. p8 TableIV64.3M/27.27GFLOPs;26.2ms latency excludes calculated20/37=0.54s observation window.

Text pages: [2, 3, 5, 6, 7, 8, 9, 10]; decisive visual pages: [6, 7, 8, 9]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\1000189165.pdf`; SHA256 `03dcd61ce44d64beea0c80fd1012ea404cd0a2b8b4e1f7de87a6c10489277139`.

## P004 — Bias in error estimation when using cross-validation for model selection

**Role:** Transferable evaluation foundation, older seminal exception. **Questions:** SQ2 selection;SQ4 evaluation. **Decision:** Retain methods.

**Read version:** Publisher version; BMC Bioinformatics 7:91; published 23 February 2006.

**Target/unit:** Simulated binary classification; individual IID sample.

**Physical inputs:** Gene-like Gaussian features; no physical modalities.

**Fusion:** Evaluation/model-selection method, not fusion.

**Controls:** Shrunken-centroid and SVM.

**Split/independence:** 40 samples,6000features;>=1000 simulations;20,000 independent test samples; nested leave-one-out evaluation.

**Robustness:** missing: Not applicable; noisy: Not a noise robustness trial; shifted: IID simulation, not machine/domain shift.

**Reported evidence:** PDF p5 Table1 selected CV errors37.8/41.7percent against true50percent; biases12.2/8.3points. p6 nested estimates can be pessimistic.

**Limits:** Older seminal2006 exception. Does not certify project strict nesting or group independence.

Text pages: [2, 3, 4, 5, 6]; decisive visual pages: [5]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\1471-2105-7-91.pdf`; SHA256 `573198025179f340870428087dd3a980a5c2cbdab890ace3d155e0cf8fcd6e1b`.

## P005 — ModDrop: adaptive multi-modal gesture recognition

**Role:** Transferable seminal missing-modality method. **Questions:** SQ2 structuredfusion;SQ3 missing/noisy;SQ4 transfer. **Decision:** Retain ModDrop2015version.

**Read version:** arXiv v2, 6 June 2015; journal-style manuscript, no journal venue or article DOI asserted from supplied PDF.

**Target/unit:** Gesture classification and quarter-MNIST digit classification.

**Physical inputs:** RGB/depth/mocap; extended audio. MNIST quadrants are pseudo-modalities.

**Fusion:** Pretrained branches, staged block-structured fusion, Bernoulli whole-modality dropout.

**Controls:** Without ModDrop and individual-block comparisons.

**Split/independence:** Challenge official development/validation/test distinctions; Table10 independent test identity unclear.

**Robustness:** missing: Whole branches removed at evaluation after dropout training; noisy: Artificial salt/pepper and other corruptions; shifted: No natural machine/domain shift.

**Reported evidence:** PDF p12 Table8 two MNIST quarters absent error35.91to7.19percent; clean1.02 both. p13 Table10 absent mocap accuracy38.41to92.82; absent audio84.10to92.59.

**Limits:** NoCI in quoted table. Training exposure is not automatic reliability estimation. Non-industrial transferable older method.

Text pages: [6, 8, 9, 10, 12, 13]; decisive visual pages: [12, 13]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\1501.00102v2.pdf`; SHA256 `6dc50a534ddbccdbcf7f03dd4cf77f53ce5537003d23e8c646970db71d79bde4`.

## P006 — Gated Multimodal Units for Information Fusion

**Role:** Transferable gated intermediate-fusion foundation. **Questions:** SQ2 gates;SQ3 motivation;SQ4 classnegatives. **Decision:** Retain GMU.

**Read version:** arXiv v1; first-page header Workshop track - ICLR 2017.

**Target/unit:** Multi-label movie genre classification; movie.

**Physical inputs:** Poster image and plot text.

**Fusion:** Elementwise sigmoid gate over tanh hidden representations; intermediate fusion.

**Controls:** Text, visual, concatenation, probability average.

**Split/independence:** 15,552 train/2,608 dev/7,799 test;23 genres;25 random hyperparameter candidates.

**Robustness:** missing: No controlled missing-modality trial established; noisy: Synthetic modality informativeness, not factory corruption; shifted: No industrial cross-domain test.

**Reported evidence:** PDF p11 Table2 macroF1 GMU0.541/concat0.521/average0.491/text0.488/visual0.284. Table3 Biography0.25<text0.40, History0.29<0.35.

**Limits:** Aggregate gain does not hold for every genre. Gate activations are not calibrated reliability or causal explanations.

Text pages: [4, 5, 7, 9, 11, 12]; decisive visual pages: [11]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\1702.01992v1.pdf`; SHA256 `86a32379bc86f4ffb63e121473fc65c9b9878dd420b372bae8e4946a6708bc17`.

## P007 — EmbraceNet: A robust deep learning architecture for multimodal classification

**Role:** Transferable sensor missing-data foundation. **Questions:** SQ2 stochasticfusion;SQ3 absent/block;SQ4 availability. **Decision:** Retain EmbraceNet priority.

**Read version:** arXiv v1, 19 April 2019; supplied PDF is a preprint and does not establish a final publication DOI.

**Target/unit:** Gas chemical classification; wearable locomotion/gesture; sensor sequence.

**Physical inputs:** 72 gas sensors in8types;19 wearable sensors.

**Fusion:** Stochastic per-coordinate categorical branch selection with known availability-mask renormalization.

**Controls:** Late fusion, mean fill, autoencoder and others.

**Split/independence:** Gas locations1,3,5 train/2val/4test; location6excluded. OPP four subjects, source task protocol;50percent average training modality loss.

**Robustness:** missing: All255 nonempty gas combinations; sampled OPP combinations;10–30s blocks; noisy: Missing blocks evaluated; no automatic bad-present-sensor detector; shifted: Gas held-out location split; no direct visual-machine fault transfer.

**Reported evidence:** PDF p12 Table2 OPP locomotion80percent absent F1 0.810 vs late0.793; gesture late0.785 exceeds Embrace0.782; clean autoencoder better on both tasks.

**Limits:** Not universal winner; all-absent mask undefined. Availability differs from uncertainty. Published DOI separately verified; empirical pages supplied preprint.

Text pages: [3, 4, 6, 9, 12]; decisive visual pages: [12]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\1904.09078v1.pdf`; SHA256 `ead0b525f4a7fc86a55d480554ca8fba4e016f91c5ab86172e7363416f0db4b6`.

## P008 — Can You Trust Your Model’s Uncertainty? Evaluating Predictive Uncertainty Under Dataset Shift

**Role:** Transferable uncertainty-under-shift benchmark. **Questions:** SQ3 confidenceundershift;SQ4 propermetrics. **Decision:** Retain qualification.

**Read version:** arXiv v2, 17 December 2019; first page names 33rd Conference on Neural Information Processing Systems (NeurIPS 2019).

**Target/unit:** Classification/uncertainty across images, text and tabular tasks.

**Physical inputs:** Each benchmark mainly unimodal; no industrial fusion.

**Fusion:** Uncertainty estimators, temperature scaling, dropout, SVI, ensembles.

**Controls:** Vanilla and alternative uncertainty methods.

**Split/independence:** MNIST ten runs; image16types x5severities; other task-specific splits and tuning budgets.

**Robustness:** missing: Not a missing-fusion test; noisy: Controlled image corruption and categorical randomization; shifted: Synthetic distribution shifts and OOD text.

**Reported evidence:** PDF p6 Fig2 accuracy/calibration degrade; temperature scaling fails to preserve shift calibration. p9 ensembles usually strong, not universal; Criteo dropout better Brier above60percent randomization.

**Limits:** No digitized plot coordinates. ECE not proper and can favor uninformative marginal prediction; no industrial reliability gate validation.

Text pages: [3, 4, 5, 6, 8, 9]; decisive visual pages: [6]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\1906.02530v2.pdf`; SHA256 `1610d04d7f69d10751f0e9ff1db9fbd8b3fdf5306798879016192eb2dbf17a6f`.

## P009 — Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program)

**Role:** Reproducibility/provenance foundation. **Questions:** SQ4 auditability. **Decision:** Retain methodology,notensembles.

**Read version:** JMLR publisher PDF; volume 22 (2021), 1–20; first-page footer identifies jmlr.org/papers/v22/20-303.html.

**Target/unit:** Conference reproducibility programme; papers/reports.

**Physical inputs:** Not a physical-data experiment.

**Fusion:** Reporting/checklist/code policy, not fusion.

**Controls:** Not applicable.

**Split/independence:** Observational surveys and voluntary challenge; selection/self-report limits.

**Robustness:** missing: Not applicable; noisy: Not applicable; shifted: Not applicable.

**Reported evidence:** PDF p9 Table1 code availability40to74.4percent submission-to-camera-ready; Table2 173papers/73institutions/84reviewed reports.

**Limits:** Code availability not correctness or independent reproduction. No causal policy estimate and no industrial metric.

Text pages: [7, 9, 13]; decisive visual pages: [9]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\20-303.pdf`; SHA256 `09e3ba1d1c3dc7111bc3dc112f40c5d0f3d9dbc4b8198ef8bdc48eb852f4da29`.

## P010 — An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale

**Role:** Transferable visual Transformer foundation. **Questions:** SQ1 visualcandidate;SQ4 pretrainbudget. **Decision:** Retain ViT.

**Read version:** arXiv v2, 3 June 2021; first-page header Published as a conference paper at ICLR 2021.

**Target/unit:** Image classification; image.

**Physical inputs:** RGB images only.

**Fusion:** Patch-token ViT; hybrid CNN token variant.

**Controls:** CNN/ResNet and different pretraining/model sizes.

**Split/independence:** ImageNet1.3M/21K14M/JFT303M; authors report dedup; three fine-tuning seeds.

**Robustness:** missing: Not tested; noisy: Not main controlled robustness result appraised; shifted: Pretraining-size/data-regime comparisons, not machine shift.

**Reported evidence:** PDF p6 Table2 ImageNet ViTH14/JFT88.55+/-0.04percent;L16/JFT87.76+/-0.03;L16/21K85.30+/-0.02. p7 low-data CNN advantage.

**Limits:** H14 about2500 TPUv3-core-days. Finetuning SD is not repeated pretraining. Candidate, not executed thesis backbone.

Text pages: [3, 4, 6, 7, 9]; decisive visual pages: [6]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2010.11929v2.pdf`; SHA256 `8ce7b83971a14508ca711a27c875c9b6914c4f6767cf3150fb1ca6c07aa056d6`.

## P011 — AST: Audio Spectrogram Transformer

**Role:** Transferable audio Transformer foundation. **Questions:** SQ1 acousticcandidate;SQ4 pretrain/ensemblebudget. **Decision:** Retain AST.

**Read version:** arXiv v3, 8 July 2021; conference name absent from first-page header; existing Zotero record gives Interspeech 2021.

**Target/unit:** Audio event classification; audio clip.

**Physical inputs:** Audio log-Mel spectrogram only.

**Fusion:** Overlapping spectrogram patches into ImageNet-initialized AST encoder.

**Controls:** PANN/CNN-attention and no-pretrain AST.

**Split/independence:** Official AudioSet sets;3seeds, ESC50fivefold, SpeechCommands official split.

**Robustness:** missing: Not tested; noisy: No factory background-noise protocol verified; shifted: Cross-task pretraining transfer, not industrial machine shift.

**Reported evidence:** PDF p3 Table1 single weight-averaged mAP0.459 vs last-epoch0.448; six-model ensemble0.485. Table2 pretrain0.347/0.459 vs no-pretrain0.148/0.366. p4 SpeechCommands AudioSet-pretrain97.88 below image-init98.11percent.

**Limits:** 87M parameters and overlap cost; pretraining task-dependent. Proposed audio candidate, not completed thesis audio branch.

Text pages: [2, 3, 4]; decisive visual pages: [3]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2104.01778v3.pdf`; SHA256 `c237e981755e9ba5047e7290ffcb7d38d8292e166730ae3cd180b7833f184303`.

## P012 — TS2Vec: Towards Universal Representation of Time Series

**Role:** Transferable self-supervised CNN time-series foundation. **Questions:** SQ1 strongnonTransformer;SQ3 timestampmissing;SQ4 negatives. **Decision:** Retain TS2Vec.

**Read version:** arXiv v4, 3 February 2022; first page copyright Association for the Advancement of Artificial Intelligence 2022.

**Target/unit:** Time-series classification and separate anomaly benchmarks; series/timestamp.

**Physical inputs:** Univariate/multivariate time series, not physical camera fusion.

**Fusion:** Hierarchical contrastive dilated CNN, not Transformer.

**Controls:** T-Loss/TST/TS-TCC, RBF-SVM on320D, backbone ablations.

**Split/independence:** 125UCR/29UEA comparisons;128UCR ablation; missing experiment four large UCR datasets.

**Robustness:** missing: Training AND test timestamp masks, not unseen entire sensor absence; noisy: Augmentation ablations, not calibrated machine-noise detector; shifted: Separate benchmark transfer; not industrial cross-machine validation.

**Reported evidence:** PDF p4 Table1 UCR accuracy0.830/UEA0.712. p6 Table5 CNN0.829/LSTM0.779/Transformer0.647; generic augmentations can hurt. p7 Fig6 50percent timestamp loss modest drops on selected series.

**Limits:** Archive subsets differ. Partial timestamp robustness not whole-modality robustness. Anomaly F1 not action-failure AP.

Text pages: [2, 3, 4, 6, 7]; decisive visual pages: [6, 7]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2106.10466v4.pdf`; SHA256 `24783992080266234820e077f29a49de36d44fc71bf4c9553ffe6afd1207f4ff`.

## P013 — Video Swin Transformer

**Role:** Transferable video Transformer foundation. **Questions:** SQ1 videocandidate;SQ4 views/budget. **Decision:** Retain VideoSwin.

**Read version:** arXiv v1, 24 June 2021, explicitly Preprint; existing record refers to the 2022 CVPR publication of the same work.

**Target/unit:** Human video action recognition; clip/multiview prediction.

**Physical inputs:** RGB video.

**Fusion:** Local shifted-window3D Transformer with spatial hierarchy.

**Controls:** Video CNNs, TimeSformer/ViViT and Swin variants.

**Split/independence:** Kinetics/SSv2 official protocols, heterogeneous pretraining/views;32frames typical.

**Robustness:** missing: Not tested; noisy: Not appraised as a corruption trial; shifted: Task/pretraining comparisons, not industrial machine shift.

**Reported evidence:** PDF p6 Table1 SwinT78.8percent/28.2M/88GFLOPs per view x4clips x3crops;SwinB1K80.6 vs21K82.7. Largest84.9 uses2107GFLOPs/view x50views.

**Limits:** Per-view cost not total. No CI selected table. Candidate video architecture, not project executed model.

Text pages: [3, 6, 7, 9]; decisive visual pages: [6]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2106.13230v1.pdf`; SHA256 `9680fb44c5acbcfd63e84bad7c15470cdf3e1ea558c0bd57729171e282ccdd59`.

## P014 — Attention Bottlenecks for Multimodal Fusion

**Role:** Transferable audiovisual attention fusion. **Questions:** SQ1 candidates;SQ2 intermediate;SQ3 restrictedasync;SQ4 cost. **Decision:** Retain MBT.

**Read version:** arXiv v3, 30 November 2022; first page identifies 35th Conference on Neural Information Processing Systems (NeurIPS 2021); publication year 2021 distinct from supplied revision year 2022.

**Target/unit:** Audio/video event/action classification; clip.

**Physical inputs:** Audio spectrogram and RGB video.

**Fusion:** Four bottleneck tokens mediate cross-modal attention; selected intermediate fusion depth.

**Controls:** Audio-only, visual-only; early/late/vanilla attention variants.

**Split/independence:** AS500K/MiniAS/VGGSound/EpicKitchens; task-specific tuning, four test crops.

**Robustness:** missing: No whole-modality absence test; noisy: No direct factory noise validation; shifted: Independent audio/video windows inside same labeled clip; limited asynchronous sampling, not clock drift.

**Reported evidence:** PDF p9 Table1 AS500K audio41.5/visual31.3/AV49.6mAP; Table2 action40.7to43.4; Table3 VGGtop1 52.3/51.2/64.1. pp15–16 Fig8 async broadly robust.

**Limits:** Three of60strongest classes do not improve over audio. Fusion depth task-specific. Attention maps not causal; no continuous machine telemetry.

Text pages: [3, 4, 6, 7, 8, 9, 10, 15, 16]; decisive visual pages: [9]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2107.00135v3.pdf`; SHA256 `bfaab1347c8d88f0e8a2f0d09c7529ab70f7b5c4146b4532702762ed04fb8b18`.

## P015 — MultiBench: Multiscale Benchmarks for Multimodal Representation Learning

**Role:** Transferable multimodal benchmark foundation. **Questions:** SQ2 baselines;SQ3 corruption/missing;SQ4 cost. **Decision:** Retain MultiBench.

**Read version:** arXiv v2, 10 November 2021; first page identifies NeurIPS 2021 Track on Datasets and Benchmarks; 97-page manuscript includes supplementary material.

**Target/unit:** 15 datasets/20 tasks; units and metrics differ.

**Physical inputs:** 10 modality types including image, force, proprioception, text, audio.

**Fusion:** Standardized multimodal methods; source LF label includes representation concatenation.

**Controls:** Best unimodal, simple LF, within/out-domain-origin methods refitted per task.

**Split/independence:** Clean training/corrupted test; task-specific splits. Out-domain method origin is not same-weight zero-shot transfer.

**Robustness:** missing: Whole-modality drop, structured temporal drop; noisy: Modality-specific and correlated synthetic imperfections; shifted: Natural distribution shift and uncertainty metrics future work in this version.

**Reported evidence:** PDF p7 Table2 MuJoCoMSE unimodal0.334/indomain0.290/outdomain0.402;Kinetics56.5unimodal>56.1indomain. p9 Fig4 absolute versus clean-adjusted robustness differ.

**Limits:** Appendixpp53–54 relative/effective robustness curves; do not pool rawMSE/AP. LF competitive but not always best. No industrial field deployment proof.

Text pages: [3, 4, 6, 7, 8, 9, 10, 53, 54]; decisive visual pages: [9]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2107.07502v2.pdf`; SHA256 `02a411c4143e2a5b9559c824b519fdc250108f6eb9d71b0cc56f503298789df1`.

## P016 — Are Multimodal Transformers Robust to Missing Modality?

**Role:** Transferable missing-modality Transformer/counterexample. **Questions:** SQ2 fusiondepth;SQ3 missing;SQ4 fallback. **Decision:** Retain highpriority.

**Read version:** arXiv v1, 12 April 2022; existing record gives CVPR 2022; title and arXiv identifier establish same work.

**Target/unit:** Genre/food/meme classification; example with optional text.

**Physical inputs:** Image and text.

**Fusion:** ViLT masked image/text/joint multitask tokens; bilevel searched fusion-start depth.

**Controls:** Independently trained image/text; complete-trained ViLT; naive missing-trained baseline.

**Split/independence:** Complete training;10–100percent examples have observed text, all have image; separate validation for policy.

**Robustness:** missing: Explicit test modality absence and robustness training; noisy: Not a factory noise experiment; shifted: No natural machine shift.

**Reported evidence:** PDF p7 Fig2 MMIMDb10percent text baseline macroF1 23.1<image35.0; proposed37.3. Food58.4baseline/73.3proposed/image71.5 from p3Table4/Fig2.

**Limits:** Nearby Food prose inconsistent on unimodal73.3. Missing means example availability, not word dropout. Dataset-optimal depth not instance reliability; no universal fusion depth.

Text pages: [1, 2, 3, 4, 5, 6, 7, 8]; decisive visual pages: [7]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2204.05454v1.pdf`; SHA256 `baf3728f95d339ff25e25d7e81b36170049cbaf60a21ac4e5a91551df925e620`.

## P017 — Leakage and the Reproducibility Crisis in ML-based Science

**Role:** Transferable leakage/evaluation foundation. **Questions:** SQ2 baselinevalidity;SQ4 grouping/targets. **Decision:** Retain methods,version-sensitive.

**Read version:** arXiv v1, 14 July 2022; supplied manuscript is the 2022 preprint, not a verified final journal version.

**Target/unit:** Scientific literature audit and civil-war prediction case study.

**Physical inputs:** No industrial modality fusion.

**Fusion:** Leakage taxonomy/model-information sheet and reanalysis.

**Controls:** Complex ML versus logistic regression in case study.

**Split/independence:** Selected literature inventory, not all-science prevalence; temporal/preprocessing/target-proxy dependencies.

**Robustness:** missing: Not applicable; noisy: Not applicable; shifted: Temporal validation leakage examined; not industrial shift trial.

**Reported evidence:** Supplied PDF p3 Fig1 correcting leakage removes claimed ML advantage in examined studies. Supplied2022v1 inventory329papers; final2023Patterns294papers.

**Limits:** Title/year/count version-sensitive. Does not prove project outer-test leakage; use project-specific code/ledger evidence.

Text pages: [1, 2, 3, 4, 5, 6, 7, 8]; decisive visual pages: [3]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2207.07048v1.pdf`; SHA256 `c433bceda841ca09fe2fd7ddf857fc0818fdf98553e62e54a37cc394c6f70c42`.

## P018 — MOMENT: A Family of Open Time-series Foundation Models

**Role:** Transferable time-series foundation-model candidate. **Questions:** SQ1 pretrainedTS;SQ2 baselines;SQ4 budget/metrics. **Decision:** Retain MOMENTcandidate.

**Read version:** arXiv v3, 10 October 2024; first-page footer Proceedings of the 41st International Conference on Machine Learning, PMLR 235, 2024.

**Target/unit:** Forecasting/imputation/classification/anomaly; series/patch.

**Physical inputs:** Time series; channels processed independently.

**Fusion:** Masked-reconstruction pretrained Transformer40M/125M/385M.

**Controls:** PatchTST, TS2Vec, shallow interpolation/KNN and others.

**Split/independence:** Authors train-only pretraining; creator splits else60/10/30;long time split/short whole series; seed13; downstream access differs.

**Robustness:** missing: Imputation timestamp masks, not whole physical modality loss; noisy: Not direct machine-noise reliability validation; shifted: Multiple datasets and adaptation access, not visual-sensor industrial shift.

**Reported evidence:** PDF p8 Table4 classification M0accuracy0.794<TS2Vec0.851. p9 Table7 adjustedF1 LP0.628>KNN0.554 but VUSROC KNN0.706>LP0.684. p6 Weather96MSE LP0.154>PatchTST0.149.

**Limits:** Frozen-encoder classification still trains supervised SVM. Large pretraining and metrics matter; not uniformly best or executed thesis component.

Text pages: [3, 4, 5, 6, 8, 9]; decisive visual pages: [9]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2402.03885v3.pdf`; SHA256 `037108e4be01e9ae7643bbe54bd4f65c9b5710d53f336c05054e68be645124e2`.

## P019 — REASSEMBLE: A Multimodal Dataset for Contact-rich Robotic Assembly and Disassembly

**Role:** Direct robotic contact-rich dataset. **Questions:** SQ1 modalities/alignment;SQ2 taskdistinction;SQ4 unit/annotation. **Decision:** Retain coredataset.

**Read version:** arXiv v2, 28 April 2025; repository manuscript; title and arXiv ID match the existing dataset record.

**Target/unit:** Contact-rich robotic assembly/disassembly dataset; action/skill and native task benchmarks.

**Physical inputs:** Three RGB/three audio,6axis force-torque,proprio,event camera,mocap; released depth excluded.

**Fusion:** Dataset; native wrist visual+flow TAS and visual condition checks, not definitive target-matched fusion test.

**Controls:** Native DiffAct/ConditionNET, not thesis binary-failure matched sensor comparator.

**Split/independence:** Raw streams retain timestamps; not postprocessed into synchronized arrays. Fixed board/objects; operator annotations; no run-independent failure split established here.

**Robustness:** missing: Not evaluated; noisy: Not controlled sensor-noise evaluation; shifted: No demonstrated cross-machine fault transfer.

**Reported evidence:** PDFpp7,13 4551actions/10195skills/4035success=>516failures calculated. pp10–11 DiffAct accuracy61.5/EDIT47.8/F1@50 44.1percent. pp12–13 visual condition checks~96percent.

**Limits:** Published cohort differs from thesis4530. Retrospective labels, object/action prevalence, narration shortcut risk; native metrics not binary AP. Multimodal TAS preliminary/future comprehensive analysis.

Text pages: [4, 6, 7, 8, 9, 10, 11, 12, 13]; decisive visual pages: [9, 11]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2502.05086v2.pdf`; SHA256 `5a01295ce17aea2a24e2da4cc57afef675751219443814dcf1fddf0ec9afbf60`.

## P020 — Multimodal Negative Learning

**Role:** Transferable noise-robust fusion and explicit negatives. **Questions:** SQ2 late/dynamicfusion;SQ3 noisy;SQ4 negatives/cost. **Decision:** Retain MNL.

**Read version:** arXiv v1, 23 October 2025; first-page footer 39th Conference on Neural Information Processing Systems (NeurIPS 2025).

**Target/unit:** Multimodal classification under noise; example.

**Physical inputs:** MVSA/Food image-text;NYU RGB-depth;CREMA audio-video.

**Fusion:** Negative-learning auxiliary loss added to static/dynamic fusion.

**Controls:** Unimodal branches, static LF, PDF/QMF and other dynamic baselines.

**Split/independence:** 50percent modalities perturbed;epsilon0/5/10 modality-specific Gaussian/salt/blank/SNR;5seeds stated.

**Robustness:** missing: Future work, not demonstrated whole-modality loss; noisy: Explicit synthetic noisy-present modalities; shifted: Natural domain drift not established.

**Reported evidence:** PDF p7 Table1 MVSAepsilon5 LF63.46<text69.50,LF+MNL74.03. Negative PDF74.40to74.07; Food QMF76.03to75.41.

**Limits:** Small adverse differences not resolved without SD; selected SD appendix not read. No universal improvement. No added inference component does not remove training cost.

Text pages: [1, 3, 4, 5, 6, 7, 8, 9, 10]; decisive visual pages: [7]. Source: `C:\Users\Parth\Downloads\Additional Papers to be linked in Yotero\2510.20877v1.pdf`; SHA256 `6ab96676e709e538cf5a1ba2809c6ddf77b75c007c1c169bffd508d0dd51c653`.

## Citation/version corrections

- P003: {"doi": "10.1109/JSEN.2025.3634585", "venue": "IEEE Sensors Journal26(2)(2026)2347–2358", "source": "Primary KITopen association already documented inStep1;suppliedPDFno printedDOI"}
- P007: {"doi": "10.1016/j.inffus.2019.02.010", "year": 2019, "venue": "InformationFusion51:259–270", "url": "https://www.sciencedirect.com/science/article/pii/S1566253517308242", "source": "Primarypublisherchecked2026-11-18;supppliedpreprintversionretained"}
- P016: {"year": 2022, "venue": "CVPR2022", "pages": "18177–18186", "url": "https://openaccess.thecvf.com/content/CVPR2022/html/Ma_Are_Multimodal_Transformers_Robust_to_Missing_Modality_CVPR_2022_paper.html", "source": "PrimaryCVFchecked2026-11-18;DOInotassertedfromsecondary;empiricallocatorsarXivv1"}
- P017: {"doi": "10.1016/j.patter.2023.100804", "title": "Leakage and the reproducibility crisis in machine-learning-based science", "year": 2023, "venue": "Patterns4(9)100804", "url": "https://doi.org/10.1016/j.patter.2023.100804", "source": "Primarypublisherchecked2026-11-18;final294papersvssupplied2022v1329papers;keepversion/title/year/countdistinct"}
