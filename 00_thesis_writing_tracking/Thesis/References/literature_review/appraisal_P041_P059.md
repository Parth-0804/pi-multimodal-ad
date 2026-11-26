# Full-text appraisal: P041–P059

Reviewed2026-11-18. Nineteen supplied files, eighteen unique PDFs; P047 is an exact duplicate of P046. Relevant methods/results appraised; no experiment reproduction. Companion JSON holds identity/version/hashes and exact locators.

## Synthesis

Physical visual–machine-sensor comparators are P045 (post-pass tool photographs plus acoustic signal) and P048 (thermal camera plus vibration). P046/P053 are acoustic–vibration: signal-to-image representations are not physical cameras. P051 uses visible/thermal imagery; P054/P056 RGB/geometry. Native MSM/ViFailback dataset facts do not replace admitted thesis cohorts.

Missingness, noise and shift remain distinct. P051 tests incomplete federated clients, not a separately documented unexpected test-camera-outage matrix. P046 tests one noisy branch but lacks matched noisy static/unimodal controls. P058 has actual non-industrial quality-corruption experiments and conditional theory. P054/P056 training perturbations are not sensor-corruption validation.

Negative findings: P045 and P046 have multimodal alternatives below strong unimodal controls. Medical P044 attention variants trail concatenation/best unimodal at full labels but reuse validation. P058 clean and corrupted rankings differ; P054 image gain accompanies slightly lower AUPRO. Neither these findings nor favorable mean scores establish a universally superior fusion family.

SQ4 requires calibrated probability interfaces/proper scores, stated validation exposure and dependence-aware uncertainty. Attention heatmaps are not causal explanations. RTDETR CNN backbone extraction is distinct from full detector adaptation.

## P041 — On Calibration of Modern Neural Networks

**Role:** foundation; retain outside core fusion denominator.

**Version / access:** PMLR conference paper; PDF2–8; Table1 PDF6. DOI not asserted.

**Inputs / target:** Conventional image/text neural classification, no industrial fusion. Top-label confidence versus correctness.

**Method:** Post-hoc calibration on frozen network; positive scalar temperature preserves argmax. Platt learned slope/intercept need not preserve ranking if slope is negative.

**Protocol:** Separate validation fitting; §4 PDF4 explicitly assumes identical train/validation/test distribution. ECE uses15equal-width bins; diagrams omit bin counts. Supplied10page main article, not all referenced supplementary experiments.

**Locatable findings:**
- Table1 PDF6: ECE percent — CIFAR100 ResNet11016.53→1.26 temperature; Reuters DAN0.85→0.91, so no universal improvement.

**Robustness:** No controlled missing/noisy modality or shifted calibration experiment; IID calibration does not establish OOD reliability.

**Limits:** ECE depends on finite bins/support and is not a strictly proper scoring rule. NLL/probability quality, accuracy and calibration are distinct.

**Admissible conclusion:** Validation-fitted temperature is a defensible calibration baseline; confidence must be checked empirically, especially after shift.

## P042 — Adaptive vibration-based bearing fault diagnosis for mud pumps using MSESSA-optimized variational mode decomposition

**Role:** background single-modality; exclude core fusion denominator.

**Version / access:** Publisher journal article; PDF12–14,23–30; Table5 PDF28. DOI 10.21595/jve.2026.26008.

**Inputs / target:** Single vibration stream, CWRU four bearing states and simulated mud-pump target; no camera or multimodal fusion.

**Method:** MSESSA optimizes VMD using reconstruction error/envelope entropy; selected IMF energy/peak factors feed statistical features and LightGBM.

**Protocol:** CWRU12kHz10240sample windows,595/885/885/900 samples; random80/20 per class PDF23, no bearing/run disjointness. Synthetic mud pump600rpm with load modulation/colored+Gaussian noise; PDF27 says30train+10test per class. No real field pump test.

**Locatable findings:**
- PDF23: reported CWRU accuracy — 99.57%; no fusion interpretation.
- PDF28–30: reported simulated accuracy — 96.14%; unresolved test-denominator/count conflict, not admitted as a precise comparative fusion estimate.

**Robustness:** Synthetic vibration noise; not missing modality. VMD parameters reused with target-specific supervised training, not zero-shot learned-weight transfer.

**Limits:** Table5 PDF28 assigns different reused VMD settings per known class; unknown-class inference parameter selection not explained (potential label-dependent preprocessing, not proven leakage). PDF30 discusses15inner→outer plus4outer→inner errors despite stated10test/class;96.14% is not integer fraction of40 without unreported aggregation. Window-random CWRU split risks recording dependence.

**Admissible conclusion:** Optional vibration preprocessing background only; reporting conflicts preclude using apparent near-perfect scores as multimodal evidence.

## P043 — WILDS: A Benchmark of in-the-Wild Distribution Shifts

**Role:** foundation and TRANSFERABLE (non-industrial); retain outside core denominator.

**Version / access:** PMLR conference paper; PDF2,7–9; Tables1–2. DOI not asserted.

**Inputs / target:** Ten diverse WILDS datasets and domain/subpopulation shifts; not an industrial fusion experiment.

**Method:** Standardized dataset-specific ERM/robustness comparisons; average and worst-group outcomes differ.

**Protocol:** Four ID comparison constructions: fixed train, fixed test, randomized, average. OOD validation used for early stopping/hyperparameters PDF9; not zero target information. At least3replicates and SD. Referenced detailed appendicesG/H not contained in supplied main paper.

**Locatable findings:**
- Table1 PDF7: iWildCam macroF1 — Fixed-train ID47.0(SD1.4),OOD31.0(SD1.3). Different datasets use different metrics.
- Table2 PDF8: finding — Robust algorithms do not consistently beat ERM; iWildCam CORAL32.8 versus ERM31.0 is an explicit improvement exception.

**Robustness:** Explicit domain/subpopulation shift; not missing channels or sensor-noise matrix.

**Limits:** Purposively selected impactful shifts do not estimate field failure frequency. Limited OOD domains and benchmark reuse permit test overfitting. Worst-group accuracy and aggregate accuracy are different estimands; SD is not SE.

**Admissible conclusion:** Report domain/group definitions and all target validation exposure; do not pool heterogeneous metrics or import numerical gaps into industrial fusion.

## P044 — Dual warm-start fusion versus attention-based fusion in low-label ECG–PCG classification: a controlled ablation study

**Role:** TRANSFERABLE (non-industrial), medical counterexample; retain narrowly.

**Version / access:** Publisher article with IOP download cover sheet; PDF5–7,9–11,13–14,18,20; Tables4,6,11; printedpage=PDF−1. DOI 10.1088/1361-6579/ae85b7.

**Inputs / target:** Paired ECG waveforms and PCG log-mel spectra, CinC2016 TrainingA404recordings/1151segments(342normal809abnormal); cardiac abnormality classification.

**Method:** External dual warm starts, F00/F10/F01/F11 concatenation, eight-head attention and gated attention; SupCon/DeepJDOT alternative initialization.

**Protocol:** Fixed recording-level80/20:323train/81validation,922/229segments. No independent test. Best validation-AUROC epoch is evaluated on SAME validation. Twenty seeds main,10 alternatives; segment bootstrap1000 and paired Wilcoxon, no multiplicity correction found. Weighted CE plus balanced sampler;25epochs,all encoders fine-tuned. DeepJDOT uses unlabeled target training PCG, not validation.

**Locatable findings:**
- Table4 PDF11: full-label validation AUROC mean±SD — ECGwarm.9062±.0207;F11.9028±.0125;Attn.8900±.0153;GAttn.8888±.0115;F10.9120.
- Table6 PDF14: finding — Attn−F11−.013 and gated−F11−.014 reported significant;F11−bestuni−.003±.025 nonsignificant, not equivalence.
- Table11 PDF18: full-label validation AUPRC — F11.9665,attention.9600,gated.9603.

**Robustness:** Training augmentations only; clean evaluation. Alternative warm-start sources are not controlled missing/noisy sensor tests.

**Limits:** Medical task; transfer design principle only. Repeated selection/evaluation on validation, no independent test. Twenty seeds are not twenty independent cohorts; segment bootstrap omits record clustering. Prose varies on per-seed versus fixed best-unimodal selection; avoid stronger precision than tables.

**Admissible conclusion:** Initialization and strong unimodal controls can dominate fusion complexity in this setting; not a universal anti-attention result.

## P045 — A Tool Wear Prediction Network Fusing Visual-Acoustic Cross-Attention and Interval Guidance

**Role:** direct industrial physical visual–acoustic; retain core with caveats.

**Version / access:** Publisher journal article; supplied filename v2 is not evidence of scientific revision number; PDF5–8,19–29; Tables1–2 PDF24–25. DOI 10.3390/machines14070826.

**Inputs / target:** MATWI post-pass tool photographs (camera acquired during shutdown after each cut) paired with preceding active-cut acoustic emission; flank wear0–450micrometres. Not live video. Other numeric channels exist; AE preferred, max-variance backup if invalid.

**Method:** EfficientNetV2 ROI384 and sensor CNN256, whole-pass128sample GAF, bidirectional cross-attention, interval-guided wear experts. UAL global homoscedastic task-loss balancing is not per-sample modality calibration.

**Protocol:** PDF20 says17tool lifecycles1663samples; explicit PDF21 split lists7train+3validation+3test=13tools,4disposition unknown. Reimplemented comparators from scratch150epochs,batch8,AdamW3e−4; original MATWI MAE19 imported externally. PDF20 says GAF+wavelet two channels, PDF21–22 single GAF, unresolved input description.

**Locatable findings:**
- Table1 PDF24: MAE/RMSE micrometres — Proposed6.6183/12.5657; visualResNet50 8.3002/15.4149; acousticCABLSTM60.5118/89.6246; multimodalSwin45.0145/75.2110 and StageLSTM48.4795/72.0207. Multiple multimodal models below strong visual baseline.
- Table2 PDF25: MAE sequential ablation — Basic7.5252→ROI/GAF7.0207→BCA6.9636→IGL6.8028→UAL6.6183; no repeated-training CI.
- PDF29: computation only — 5.52ms preprocessing+36.96forward=42.48ms; excludes acquisition and shutdown wait.

**Robustness:** No controlled missing/noisy/shift matrix. Backup-channel rule is not demonstrated dropout robustness. PDF28–29 qualitative chipping/occlusion and noisy gate-oscillation failures.

**Limits:** Tool split coverage ambiguous. Architectures/capacity vary, so fusion effect not isolated. ExternalMAE19 unmatched; prose27% reduction conflicts with65% abstract arithmetic. No repeated-seed CI; qualitative90% band not demonstrated predictive calibration. Whole-pass resampling not demonstrated lossless; attention does not identify physical causality.

**Admissible conclusion:** A direct image–acoustic comparator with strong vision and concrete negative fusion counterexamples; retain post-pass horizon and unresolved split coverage.

## P046 — Multimodal Heterogeneous CNN with Adaptive Modality Fusion for Intelligent Fault Diagnosis of Bearings

**Role:** direct industrial acoustic–vibration; retain core; P047 duplicate.

**Version / access:** Publisher journal article; PDF6–11,14,18,21–25; Tables3,5–7. DOI 10.3390/machines14080875.

**Inputs / target:** Ottawa microphone and accelerometer paired42kHz10s bearing recordings; seven classes. Bearing photos are illustrations, no physical camera input.

**Method:** Heterogeneous1D CNN branches, bidirectional cross-attention, sample-wise softmax modality weights and weighted feature concatenation.

**Protocol:** Nonoverlapping2048point windows, paired recording positions; random1/5/10/15/20training windows per class, remaining test. No bearing/recording group holdout demonstrated. Ten random-seed mean±SD.

**Locatable findings:**
- Table3 PDF14: accuracy percent — 10/class95.82±1.25;1/class56.20±7.13;20/class97.83±2.52.
- Table7 PDF23: accuracy percent,10/class — Vibration89.48±3.52;acoustic62.63±5.58;concat89.65±2.55;+crossattention91.87±2.73;+weight90.38±2.92;full95.82±1.25.
- Table5 PDF18: test-only one-branch Gaussian noise — Clean95.82;acoustic0dB91.03±2.67;vibration0dB90.88±2.51,other branch clean.
- Tables6–7 PDF22–23: finding — Homogeneous shallow fusion88.79,MRCFN83.60,MSLN77.22 below vibration-only89.48.

**Robustness:** Test-only Gaussian on one branch20/10/0dB. Only proposed has reported noise table, so adaptive-versus-static corruption benefit not isolated. Missing input not tested; variable speed/load future work PDF25.

**Limits:** Window-random evaluation does not establish unseen-bearing/machine generalization. Seed SD does not quantify independent bearing uncertainty. Weights track injected noise but are not calibrated probabilities/physical importance.

**Admissible conclusion:** Bounded acoustic–vibration fusion and test-time corruption evidence; no camera input, dropout test or cross-machine transfer.

## P047 — Multimodal Heterogeneous CNN with Adaptive Modality Fusion for Intelligent Fault Diagnosis of Bearings

ExactSHAduplicate P046; no independent study.

## P048 — A sensor fusion based approach for bearing fault diagnosis of rotating machine

**Role:** direct industrial thermal image–vibration; retain early-fusion core.

**Version / access:** Publisher article; issue2022, copyright/first-online2021; PDF3–13 (printed663–673); Table11 PDF13. DOI 10.1177/1748006X211044843.

**Inputs / target:** FLIRP640thermal7fps640×480 and vibration6.4kHz, five laboratory bearing conditions at19/23/29Hz,10kgload; five-class diagnosis.

**Method:** Hilbert1D/2D transforms,15statistics/branch,30feature concatenation, NCA+Relief selects6,quadratic SVM.

**Protocol:** One-hour steady state then5minute capture. Vibration640sample100ms windows50%overlap PDF5; precise thermal multirate pairing unspecified. Five-fold CV, no bearing/run grouping or feature-selection nesting demonstrated. Speeds evaluated separately, not an unseen-speed transfer.

**Locatable findings:**
- PDF10: unimodal accuracy percent19/23/29Hz — Vibration98.4/97.8/97.4;thermal98.8/98.6/98.8.
- Table11 PDF13: accuracy percent19/23/29Hz — Proposed100/100/99.6;CCAconcat99.6/99.6/99.4;CCAsum82.6/83.2/89;DWT99.6/99.6/100. DWT better at29Hz.

**Robustness:** No controlled missing/noisy modality tests; multiple separately evaluated speeds do not prove shift robustness.

**Limits:** Overlapping windows and unspecified group split create dependence risk, not proof of leakage. No seed/CI; selector/scaler isolation unclear. Cross-paper Table12 not matched evidence; box-constraint plot average precision should not be equated with ranking AP.

**Admissible conclusion:** Feature concatenation can improve reported thermal/vibration classification under this laboratory protocol; no universal fusion superiority or field-shift claim.

## P049 — Attention is not Explanation

**Role:** TRANSFERABLE (non-industrial) interpretability counterexample.

**Version / access:** ACL Anthology published conference paper; PDF2–8; Tables1–2; Algorithms1–3; Figures3–4. DOI 10.18653/v1/N19-1357.

**Inputs / target:** NLP sentiment/classification, QA and NLI tokens; tests explanatory meaning of attention, no physical multimodal data.

**Method:** BiLSTM/CNN/average embeddings with simple additive or dot-product attention; Kendall correlation with gradient/leave-one-out importance,100random permutations, adversarial alternative attention with fixed latent states.

**Protocol:** Interpretation experiments on test examples. Output TVD tolerance.01classification/.05QA. Authors restrict scope from richer biattentive models PDF3 and concede gradient/erasure measures are not complete explanations PDF5.

**Locatable findings:**
- Table2 PDF4: Kendall tau mean±SD over examples — SSTclass0 gradient-attention BiLSTM.34±.21 versus average encoder.61±.20;20Newsclass0.07±.17 versus.79±.07.
- PDF6–8 Figures3–4: finding — Many very different attention distributions preserve outputs; positive diabetes predictions explicitly show a meaningful perturbation exception.

**Robustness:** Attention perturbation is an interpretability intervention, not sensor corruption/dropout or machine shift.

**Limits:** Empirical critique of specified NLP models, not a theorem for all attention/explanation. Fixed-representation attention intervention does not prove causal raw-sensor effects.

**Admissible conclusion:** Attention weights alone do not establish unique or causal physical explanation; do not claim every attention mechanism is uninterpretable.

## P050 — Multimodal Transformer for Unaligned Multimodal Language Sequences

**Role:** TRANSFERABLE (non-industrial) crossmodal architecture foundation.

**Version / access:** ACL Anthology published conference paper; PDF2–8,11–12; Tables1–5. DOI 10.18653/v1/P19-1656.

**Inputs / target:** GloVe text, Facet facial video features, COVAREP74D acoustic features, MOSI/MOSEI/IEMOCAP sentiment/emotion; strongest individual branch is text.

**Method:** MulT six directed crossmodal stacks with target queries and low-level source keys/values, temporal convolution/positions and target-wise concatenation plus self-attention predictor.

**Protocol:** Aligned P2FA word averages versus native unaligned12.5/20Hzacoustic and15Hzvideo; CTC-trained adaptations for baselines needing alignment. Approx200kparameters matched. AppendixTable5 hyperparameters, validation grid/LR decay. Supplied main text does not establish group-disjoint split details or retraining CI.

**Locatable findings:**
- Table4 PDF8: unaligned MOSEI binaryaccuracy/F1/MAE — Text77.4/78.2/.653;audio65.6/68.8/.764;vision66.4/69.3/.759;lateTransformer78.6/78.5/.636;early78.9/78.8/.648;MulT81.6/81.6/.591.
- Tables2/4 PDF6/8: finding — MulT correlation.694 versus.691 differs across tables; do not silently combine.
- Table3 PDF7: finding — Aligned sad accuracy MulT86.7<MFM88.4, so not best on all metrics/tasks.

**Robustness:** Unequal sample rates/unaligned word features, not controlled hardware clock shift, sensor dropout or image corruption.

**Limits:** Non-industrial language tasks; approximate parameter matching not full optimization equivalence. Attention visualization is qualitative, not causal explanation.

**Admissible conclusion:** Crossmodal attention can relate unequal-length streams without forced word alignment; industrial temporal-offset robustness remains a separate empirical question.

## P051 — Real-Time Federated Fault Detection for Substations With Incomplete Multimodal Data

**Role:** direct industrial incomplete visible/thermal clients; retain with access limits.

**Version / access:** Browser print of complete publisher webpage; not canonical typeset PDF; Browser-print PDF2–32; Table2 PDF21–22; Table5 PDF28; Figures8–9 PDF29–30. DOI 10.1049/tje2.70222.

**Inputs / target:** Visible and infrared images, NOT numeric process sensors.48650pairs(32420normal16230fault),five substations,Jan2022–Dec2024; six-class fault object detection.

**Method:** FED-MFD dualYOLOv12-S, four-region bidirectional attention, lightweight head, frozen absent branch, bimodal-teacher feature distillation/MLP hallucination; quality-weighted federated aggregation.

**Protocol:** 15clients,Dirichletalpha.5,default20%single-modality clients,3seeds42/123/456. No recoverable train/validation/test ratios or station/time/event disjointness. Private data request only. Quality coefficients conflict PDF18 .4/.3/.3 versus PDF21 .5/.3/.2; image-size and rounds/epoch descriptions differ.

**Locatable findings:**
- Table2 browserPDF22: mAP@.5 percent — IR78.34±.19,VIS81.72±.17,early86.17±.23,late88.53±.26. Final row clipped in supplied browser table, not reconstructed.
- Table5 PDF28: mAP@.5 percent — DBFEN83.62;+BRAM87.24;+LDH87.93;+distillation89.47;+MHM90.73;+quality91.83±.29. ± not assumed CI.
- Fig8 discussion PDF29: finding — Up to80%incomplete clients reports8.1point decline; not separately specified sudden test-only camera outage.
- Fig9 PDF30: mAP versus Gaussian sigma — 0/10/20/30/40:91.8/90.5/88.3/84.8/81.9. Sigma scale unreconciled with [0,1] normalization.

**Robustness:** Missingness is federated-client incompleteness; deployment hallucination described without separate unexpected-outage matrix. Gaussian image noise tested, affected stream/scale unclear. Adverse-weather subset described, no separate result located. Non-IID clients not independent cross-machine transfer.

**Limits:** 40page browser capture has horizontally/bottom clipped Table2 (visually confirmed PDF22). Centralized complete-data baselines versus federated incomplete protocol do not isolate fusion/capacity/exposure. Missing split details/coefficient conflicts limit reproduction.

**Admissible conclusion:** Industrial missing-data evidence is incomplete visible/thermal clients, with bounded image-noise results; not calibrated modality reliability or numeric machine-sensor fusion.

## P052 — Multi-sensor and MTConnect dataset of metal cutting anomaly in milling from laboratory and industry settings

**Role:** direct industrial dataset foundation; not fusion-result denominator.

**Version / access:** Publisher Data Descriptor; PDF2–12; Tables3–4 PDF9–11. DOI 10.1038/s41597-026-07255-7.

**Inputs / target:** HurcoVM20i/VMX30Ui lab and HaasVF10 industry;48kHzaudio,51.2kHzlab vibration,MTConnect,power/low-frequency features,current. Smartphone door-window video LAB ONLY. Native0stable/1intervention-worthyabnormal/2defective-toolbutstablecut.

**Method:** Dataset descriptor, no predictive architecture. Label1 overrides2 if defective-tool cut abnormal. Experts use machining/sound/sensors; boundaries initializedNC/position then sound-refined.

**Protocol:** NTP common computer times; reference crop. Controller roughly.1slab,adapterpower/vibration~1s,industry1Hz/current10s; polling.1s not all fresh channels. Native release stats separate from admitted thesis adapter cohort. DatasetDOI10.34740/kaggle/ds/8392825.

**Locatable findings:**
- Table4 PDF11: native label0/1/2 percentages — VM20i69.17/26.33/4.5;VMX64.48/27.71/7.8;VF1097.49/2.51/0. Total8h12m23s,58%cut; not admitted model counts.

**Robustness:** Multiple domains enable research but no model missing/noise/transfer validation.

**Limits:** No unimodal/fusion benchmark. NTP claim does not independently validate camera-frame alignment. Published:xx xx xxxx placeholder PDF12; retain2026volume/DOI, do not invent exact date.

**Admissible conclusion:** Use native acquisition/label provenance; actual adapter manifests govern cohort counts, timing and target mapping. Label2 is not automatically a process anomaly.

## P053 — A Multi-Channel Multi-Scale Spatiotemporal Convolutional Cross-Attention Fusion Network for Bearing Fault Diagnosis

**Role:** direct industrial acoustic–vibration; retain core with protocol caveats.

**Version / access:** Publisher journal article; filename v2 alone is not scientific revision evidence; PDF6,10–18,20–24; Tables1–10. DOI 10.3390/s25185923.

**Inputs / target:** Microphone and accelerometer Morlet-CWT images, no camera. Ottawa42kHz1750rpm400N9classes;KAIST25.6/51.2kHz5classes.

**Method:** MMSTCCAFN multiscale temporal vibration and multiscale spatial acoustic branches, channel/spatial cross-attention,GAP/FC. Sigmoid temporal gate is not calibrated modality quality.

**Protocol:** Ottawa350train50test/class;KAIST250train50test/class. Framework says train/validation/test but validation counts/windowstride and bearing/recording group separation not recovered. Batch32,200epochs,Adam.001,10trials. KAIST microphone zero-load only to avoid brake noise; paired-load admission unclear. Each dataset fit separately.

**Locatable findings:**
- Table3 PDF16: Ottawa accuracy percent mean(SD) — Vibration93.70(.9316),acoustic91.02(.9918),fusion99.56(.0993). Table5 PDF17 sum-fusion98.16(.3392).
- Table8 PDF23: KAIST accuracy percent mean(SD) — Vibration94.05(.9176),acoustic91.74(.8993),fusion99.91(.0722).Table9 PDF24 sum-fusion98.73(.2354).

**Robustness:** No explicit missing/noise stress matrix. Noise-robustness asserted; zero-load collection avoids noise rather than validates it. Separately fitted datasets are not learned-weight transfer.

**Limits:** Independent bearing/recording holdout not shown. Reported extrema99.64/99.76 not straightforward fractions of stated450/250test without unreported aggregation. PDF17 prose direction conflicts Table5 lower removed-module results; use table. Single-branch models smaller than full, not capacity-isolated comparison.

**Admissible conclusion:** Acoustic–vibration fusion improves reported within-dataset bearing classification; spectral images do not make this visual-camera evidence.

## P054 — Discrepancy-Guided Complementary Fusion for Unsupervised Multimodal Anomaly Detection

**Role:** direct industrial RGB plus geometry; retain core; identity corrected.

**Version / access:** Publisher journal article; filename v2 alone is not scientific revision evidence; PDF5–13; Tables1–6; Table4 PDF12 visually checked. DOI 10.3390/s26123757.

**Inputs / target:** RGB and surface normals, MVTec3Ddepth-derived/Eyecandiesprovided, not process timeseries; normal-only anomaly detection/localization.

**Method:** DGCF dualWideResNet50/OCBE reconstruction, absolute-discrepancy complementary injections, bounded alpha; N2F Gaussian training-feature noise. Validation-fixed z-normalized per-modality anomaly maps summed late; image maximum.

**Protocol:** 256square,200epochs,batch16,lr.005,seed42. Split counts/groups not given. Early baseline pixelwise equal RGB/normal sum into one encoder; full dual encoders increases capacity. Five timing repeats are not training-seed replicates.

**Locatable findings:**
- Tables1–2 PDF10–11: imageAUROC/pixelAUROC/AUPRO percent — MVTec97.3/99.6/97.6;Eyecandies94.8/98.6/93.4.
- Table3 PDF12: early versus DGCF — MVTec96.5/99.5/97.3→97.3/99.6/97.6;Eyecandies90.3/98.1/91.6→94.8/98.6/93.4.
- Table4 PDF12: finding — Neither module95.8/99.6/97.7 versus full97.3/99.6/97.6 MVTec: image gain while AUPRO decreases.1point.
- Table6 PDF13: resource change — 369.1→528.8Mparams,1581.8→2222.9MBVRAM,102.8±.9→114.1±.7ms RTX3090batch1.

**Robustness:** N2F training perturbation/hyperparameter sensitivity is not test-input corruption. No missing/shift tests.

**Limits:** No unimodal control located. Fusion and capacity co-vary; fixed training seed. P054 is DGCF, not bearing paper (P053).

**Admissible conclusion:** A discrepancy-guided RGB/normal reconstruction fusion example with metric/resource tradeoffs, not machine-timeseries or proven degradation robustness.

## P055 — Strictly Proper Scoring Rules, Prediction, and Estimation

**Role:** foundation; retain outside fusion denominator.

**Version / access:** Publisher article with Taylor & Francis cover sheet; PDF2–3,8,15; printed359–360,365,372. DOI 10.1198/016214506000001437.

**Inputs / target:** General probability forecasts/outcomes, no industrial experimental dataset.

**Method:** Proper expected reward maximized at truth; strict unique optimum. Paper reward orientation reversed for minimized NLL/Brier losses.

**Protocol:** Theoretical expected propriety does not establish empirical calibration for finite learned forecasts. §7.2 PDF15 discusses unordered exchangeable observations/random-fold CV, not independent CVfolds.

**Locatable findings:**
- Table1 PDF8/printed365: finding — Binary logarithmic rewards logp/log(1−p) and Brier−(1−p)^2/−p^2 support mean NLL and mean(p−y)^2 with explicit loss sign.

**Robustness:** No missing/noisy/shift experiment or transferred calibration guarantee.

**Limits:** Scores reflect more than calibration alone. Do not cite as valid naive fold-independent SE proof. Publication2007; publisher cover online2012 not citation year.

**Admissible conclusion:** NLL/Brier are proper probability losses with explicit orientation/prevalence; pair with discrimination/calibration and dependence-aware uncertainty.

## P056 — CAFM: A Cross-Modal Local Alignment Fusion Method for RGB-3D Industrial Anomaly Detection

**Role:** direct industrial RGB–3D preprint; retain provisionally.

**Version / access:** Version1 preprint, posted2026-09-24; not peer-reviewed journal publication; PDF6–20; printedpage=PDF−1; Tables1–7. DOI 10.21203/rs.3.rs-10461475/v1.

**Inputs / target:** RGB DINO ViTb/8 and PointMAE pointcloud, normal-only anomaly detection/localization; ResearchSquarev1 posted24Sep2026, not peer-reviewed claim.

**Method:** CAFM local3Dquery-toRGBkey/value attention radius1,positionencoding,symmetricInfoNCE,bottleneck dropout; RGB/3D/fused memory banks,10%coreset,one-class linear SVM late aggregation.

**Protocol:** 40epochs,AdamW.003,batch32;per-category head1000iterations. Target-normal learned memory/head means not zero-shot. Best performance checkpoint population unclear; fixed seeds mentioned, no retraining variance. Separate dataset-specific fits.

**Locatable findings:**
- Tables1–3 PDF15–17: imageAUROC/AUPRO — MVTecimage.981vsM3DM.945;Eyecandies.901vs.897. MVTecAUPRO.977<G2SF.979.
- Table4 PDF18: MVTec imageAUROC — PC.857,RGB.857,fusedbank.914,RGB+PClate.932,threebankslate.981.
- Table5 PDF19: fusion-only sensitivity — Temperature.2=.914 versus.4=.523,belowunimodal.857; configuration sensitivity, not universal fusion inferiority.
- Table7 PDF20: imageAUROC ablation — M3DM.945,+bottleneck.958,+localfusion.981; multiple changes not purely local-attention effect.

**Robustness:** Unimodal-bank ablations not missing-input deployment tests; training dropout not sensor corruption; separate fitted datasets not learned-weight transfer.

**Limits:** Preprint status and checkpoint-selection/split details limit inference. No repeated-training CI.

**Admissible conclusion:** Local RGB–3D alignment with multi-bank late aggregation and strong bank controls; not zero-shot, camera–machine-timeseries or tested missing/noisy robustness.

## P057 — Diagnose, Correct, and Learn from Manipulation Failures via Visual Symbols

**Role:** robot dataset/visual representation foundation; retain outside core sensor-fusion results.

**Version / access:** CVF open-access conference paper; exact title/authors agree with existing publisher-linked record; PDF3–8; Tables2–4. DOI not asserted.

**Inputs / target:** ALOHA head+two wrist cameras, visual/language symbols.5202trajectories100tasks,4545fail657success,58128VQA; completed action outcomes/reasons/guidance, no engineered machine-sensor statistics in paper model.

**Method:** Seven visual symbols, generated reasoning manually verified; Qwen3VL8BLoRA1epoch ViFailback8B uses headcamera; PMC/VSF separate policy interventions.

**Protocol:** Train4702trajectories95tasks52418VQA;benchmark500trajectories22tasks. Not all task-disjoint:95+22>100native tasks. Real robot3unseen tasks21trials/task matched layouts. Native paper counts not thesis admitted adapter counts.

**Locatable findings:**
- Table2 PDF7: Lite mean score — 93.70versusGemini54.64;failure-detection98.20versus93.13.
- Table3 PDF7: Hard score — 72.64versusGPT4o40.00;open-ended GPT4o-based judgments,notbinaryfailureAP.
- Table4 PDF8: real-robot success percent — Base50.8→PMC74.6(+23.8points);symbol52.4→VSF73.0(+20.6points);noCI.

**Robustness:** Headcamera versus3camera is not a visual–machine-sensor missingness comparison. No controlled sensor corruption. Unseen-task policy intervention not thesis frozen-CNN/sensor-head transfer.

**Limits:** Labels generated/verified visually, not independent physical failure instrumentation. Different tasks/inputs/metrics from thesis action-failure classifier; no imported AP.

**Admissible conclusion:** Use for native visual-symbol dataset provenance and completed-outcome semantics; adapter/cohort and actual transfer claims require thesis artifacts.

## P058 — Provable Dynamic Fusion for Low-Quality Multimodal Data

**Role:** TRANSFERABLE (non-industrial) reliability-aware method/theory; retain.

**Version / access:** PMLR conference paper; PDF3–9,14–17; Tables1–3,5; AppendixTable5 PDF16 visually checked. DOI not asserted.

**Inputs / target:** RGBDscene NYUD/SUN and image–text FOOD101/MVSA classification; non-industrial.50%modalities corrupted with Gaussian/saltpepper images or blank text.

**Method:** QMF energy/logsumexp uncertainty, negative-linear uncertainty weights and historical mean-training-loss ranking regularizer. Binary-logistic theoretical late-fusion bound.

**Protocol:** Theorem2 PDF4 compares UPPER BOUNDS assuming same joint train/testD,matched mean weights and nonpositive weight–loss covariance; not actual-risk guarantee. Assumption1 PDF5 requires uncertainty positively related to loss.10RGBD/3FOOD/5MVSA seeds; early stopping validation. Worst-case is worst seed, not population subgroup.

**Locatable findings:**
- MainTable1 PDF8: accuracy percent clean/noiseepsilon10 — NYUQMF70.09/55.60;concatclean70.30,TMC71.06/53.36,late noise51.99. MVSAconcatBERT65.59<BERT75.61;QMF78.07<MMBT78.50clean,but61.28>55.35noise10.

**Robustness:** Genuine non-industrial test-quality corruption, not explicit missing-hardware evaluation. TheoremIID assumption does not prove shifted reliability.

**Limits:** MainTable1 PDF8 versus AppendixTable5 PDF16 swaps NYU/SUN RGB/Depth rows;SUNconcat61.90versus62.48;mainNYUnoise55.60versusablationTable2PDF9 55.81. Preserve table-specific values. Table3 correlation sign versus |r| descriptions need care. §6PDF9 admits weak realRGBD uncertainty–loss correlation/unlearnable uncertainty cases. Energy and adaptive weights are not calibrated error probabilities.

**Admissible conclusion:** Dynamic quality weighting is conditional on a useful error-associated proxy; clean/noisy rankings differ. Never claim universally provable industrial superiority.

## P059 — DETRs Beat YOLOs on Real-time Object Detection

**Role:** foundation and TRANSFERABLE (non-industrial); retain architecture provenance.

**Version / access:** CVF open-access conference paper; exact title/authors agree with existing publisher-linked record; PDF4–8; Figure4; Tables2–5. DOI10.1109/CVPR52733.2024.01605 (publisher-deposited Crossref metadata verified2026-11-18; pages16965–16974).

**Inputs / target:** COCO single-image bounding-box detection; no timeseries/video fusion.

**Method:** ResNet backbone then hybrid encoder (S5AIFIattention+CNNCCFF) then Transformer query decoder/head. Backbone-only extraction is CNN representation, distinct from complete RTDETR. Query uncertainty is classification/localization discrepancy, not calibrated modality reliability.

**Protocol:** COCO72epochs,R50/R101,640square;T4TensorRTFP16batch1 speed. Comparator input sizes/training budgets vary; not thesis CPU or extracted-encoder latency.

**Locatable findings:**
- Table2 PDF7: COCOvalAP/FPS — R50 53.1/108;R10154.3/74 in paper full-detector setting.
- Tables4–5 PDF8: finding — Query selection47.9→48.7AP;6→5decoder layers53.1→53.0AP,9.3→8.8ms.

**Robustness:** No missing/noisy modalities or industrial shift experiment.

**Limits:** §6PDF8 weaker small-objectAP acknowledged. Pretrained object-detection architecture alone does not validate industrial anomaly representations.

**Admissible conclusion:** Name precisely which component is used; do not describe backbone extraction as an all-Transformer or a reproduced full-detector result.
