# Thesis experiment inventory

TASK 4 · 2026-10-26, Europe/Berlin · inspected repository HEAD `3c4fb20bee369c77d16cf5d7b0679605fb349cbc`.

This is the consolidated index for thesis use, not certification that every historical run is reproducible. It covers the significant PHM and REASSEMBLE implementations supported by the inspected sources, including feasibility studies and controls. A script's existence alone is not evidence of execution. Scratch variants and superseded snapshots are retained without being promoted to thesis results.

The [original exposé](../../MA_Exposé_Ravaliya_Parth.pdf), §3, defines Main RQ and SQ1–SQ4. The [TASK 2B charter](RESEARCH_CHARTER.md) and [alignment decisions](EXPOSE_ALIGNMENT_DECISION.md) preserve architecture/fusion as the center. The researcher-reported supervisor agreement to PHM + REASSEMBLE is accepted; documentary approval of a final title is not established. PHM investigates provisional supervision and sensor prediction; REASSEMBLE is the principal visual–sensor architecture/fusion case. The [TASK 3 matrix](TASK3_LITERATURE_EXPERIMENT_MATRIX.md), [claim audit](TASK3_CLAIM_AUDIT.md), [experiment decisions](TASK3_EXPERIMENT_DECISIONS.md) and [handoff](TASK3_EXECUTIVE_HANDOFF.md) remain unchanged.

Evidence labels throughout this five-document package:

| Label | Exact meaning |
|---|---|
| **V — verified here** | Bounded source/metadata inspection or independently recomputed saved-artifact arithmetic in TASK 4. Does not mean new training, raw-data adjudication or full reproduction. |
| **R — reported** | Historical result, interval, execution/replay/test/cost claim read in its named artifact. Not independently rerun here. |
| **I — inferred** | Explicit interpretation or algebraic consequence of inspected evidence; its assumptions must be stated. |
| **P — proposed** | Suggested interpretation, chapter choice, approval decision or future design; not an executed result. |
| **U — untested/unknown** | No qualifying execution evidence, or the inspected sources cannot resolve the property. |

All numerical values and uncertainty below resolve to the protocol-separated [master results](THESIS_MASTER_RESULTS.md). The [contribution ledger](THESIS_CONTRIBUTION_LEDGER.md) distinguishes implementation, adaptation, observation, negative findings, inconclusive comparisons and untested hypotheses. The [evidence gaps](THESIS_EVIDENCE_GAPS.md) record checks and approval boundaries.

## Shared data and evaluation contracts

| Contract | Target, observations and fitting/evaluation |
|---|---|
| **PHM-v3** | EXP-A 1–5, B 1–7, F 1–8: 20 runs. `phm2026_image_damage_v3`, 24 teeth 5–28; one deterministic image view per tooth; run target = mean of three largest candidate-area percentages. This is post-run proxy regression, not validated physical spall area, remaining life or a six-hour forecast. [Version ledger](../thesis/TARGET_VERSION_LEDGER.md), [target code](../../src/phm2026/targets/image_damage.py). |
| **PHM-LOEO** | Predict A: train F/validate B; predict B: train F/validate A; predict F: train B/validate A. One remaining experiment trains, the third validates; not training on both remaining experiments. Training-side feature/target scaling, SmoothL1, max 80 epochs/patience 10/batch 4/lr .001/decay .0001, seed 20260814. 20 run predictions; historical 10,000 run bootstrap draws. Only three experiment domains, previously exposed; run intervals do not establish uncertainty over new gear domains. [Runner](../../scripts/phm2026/results/loeo_evaluation.py), [run summary](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json). |
| **PHM-v2-image** | August RT-DETR studies: train B 448 views, validate A 323, assess F 224. Image-derived v2 scalar and heuristic pseudo-boxes, 28 teeth, maximum across views then top-three run aggregation. Different target/level from v3 LOEO. Historically one test pass within that stage; EXP-F subsequently assessed repeatedly. |
| **RE-core** | Native high-level `failure = 1 − success`; completed pick/insert/remove/place intervals. 4,530 actions, 509 failures, 148 recordings, 11.24% prevalence. Frozen five outer/four inner recording folds; deeper branch cross-fitting for stackers/gates; training-side preprocessing, selection, calibration and thresholds. Core heads select by mean inner AP. Fixed-score paired recording bootstrap, 2,000 draws; three-seed mean for F3–F6, one original branch seed family. Same-cohort exploratory programme. [S1](../reassemble/SECTION_1_PROTOCOL.md), [S1B](../reassemble/SECTION_1B_PROTOCOL.md), [S2](../reassemble/SECTION_2_PROTOCOL.md). |
| **RE-stress** | RE-core frozen clean-trained branches/heads; native pixel/sensor faults with timestamps unchanged; recompute quality; frozen clean thresholds except explicit complete-loss fallback. One seeded realization per original graded condition. [Protocol](../reassemble/SECTION_3_CORRUPTION_PROTOCOL.md), [configuration](../../configs/reassemble/section3_corruptions.json). |
| **RE-September** | Same cohort/folds, later separately declared exploratory recipes, generally three seeds and training-side selection. Their scores, thresholds, corruption exposures and uncertainty must retain their own identifiers. [Execution config](../../configs/reassemble/additional_improvements/execution.json), [final handoff](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md). |
| **RE-October** | Same exposed cohort but separate G/C/E fitting/calibration procedures, fixed budgets and threshold .5. G fits a branch; disjoint C calibrates it; E is outer assessment. Full-cohort encoder/tuning studies and 753-action noise/quality pilots are different protocols. Do not replace core probabilities with these values. |

**V:** The small retained cohort table has 4,863 annotations/4,551 primary actions; filtering `primary_task & dual_complete` gives the declared 4,530 rows/148 recordings. Its ordered labels, unique recording/segment keys and five outer/twenty inner membership partitions agree with saved core arrays. This establishes consistency of these artifacts, not the complete historical raw-to-cache chain. Arrays lack native row keys. [Cohort](../../runs/reassemble/20260927T141645Z-inventory/tables_v2/cohort.parquet), [splits](../../artifacts/reassemble/audits/nested_splits.json), [native audit report](../../00_experiments/adaptive_fusion_robustness/results/run_01/DATA_AUDIT.md).

## PHM implementations

### P00 — image-derived target and pseudo-localization

- **Task/inputs:** measure dark candidate regions in post-run gear images, then supply tooth/run regression labels and pseudo-boxes. No organizer/expert physical ground truth is introduced.
- **Forward/training:** Lab lightness → CLAHE → Gaussian background minus enhanced lightness → robust residual z score → threshold → morphology and shape/area filtering; candidate pixels divided by ROI area. v3 selects one view and top-three of 24 teeth. Connected components supply detection boxes in the older v2 work. Deterministic processing; no trained neural component.
- **Precedent/difference:** classical contrast enhancement, background subtraction, robust thresholding and morphology, not one reproduced learned research method. The complete target operator and its view/tooth aggregation are task-specific engineering choices, not established damage metrology or algorithmic novelty.
- **Protocol/result:** versioned target artifacts; **V** all saved PHM LOEO CSV truth values match the retained v3 run-target table within `1e-12`. **R** selected human review concerns 42 images/38 determinate calls, not quantitative area accuracy. Version changes and unavailable median-28 artifact prohibit pooling old results.
- **Sources/conclusion:** [code](../../src/phm2026/targets/image_damage.py), [ledger](../thesis/TARGET_VERSION_LEDGER.md), [v3 targets](../../runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/tables/run_damage_targets.parquet). A traceable proxy is available; physical validity remains U. Separate raw and cumulative-maximum targets; cumulative maximum does not validate physical monotonicity.

### P01 — frozen RT-DETR-L scalar image regression

- **Task/inputs:** predict a v2 heuristic image-area scalar from that image; aggregate views/tooth/run afterward. This tests proxy emulation across image acquisition protocols, not independent sensor–image fusion.
- **Forward/pretraining:** COCO-pretrained Ultralytics RT-DETR-L; the inspected extractor calls full `model.predict(...)` and captures intermediate maps with hooks. It does not implement a decoder-bypassing prefix. The scalar uses only spatial means of three 256-channel backbone/hybrid maps → 768 → trained128-unit MLP; detector outputs are discarded. Extractor weights are not fine-tuned. Full extraction execution and the narrower scalar representation path must be distinguished.
- **Precedent/difference:** [RT-DETR](https://arxiv.org/html/2304.08069v3) is a full object detector; replacing detection outputs with pooled scalar regression materially changes objective, localization and evaluation. Reusing its encoder is a known adaptation.
- **Protocol/result:** PHM-v2-image, train-fitted feature/target scaling, MSE head/validation stopping. **R** frozen image MAE .894 and raw run MAE 1.347; separate historical references only. Later reaggregation of R4 multitask predictions against v3 covers 13 runs and is not this frozen baseline or LOEO.
- **Sources/conclusion:** [regression source](../../src/phm2026/models/rtdetr/regression.py), [August run](../../runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8), [matched historical discussion](../planning/R4_RTDETR_MULTITASK_CHECKPOINT.md). Proxy prediction feasibility; no physical-damage or general Transformer advantage established.

### P02 — genuine RT-DETR-L one-class detection

- **Task/inputs:** detect heuristic pseudo-components in images; target boxes come from P00, not expert localization.
- **Forward/pretraining:** retain pretrained backbone, hybrid encoder, Transformer decoder/object queries, class and box heads. Freeze first nine layers, then bounded detector fine-tuning; configured 25,156,067 trainable/6,829,728 frozen parameters.
- **Precedent/difference:** original RT-DETR detection path is retained; task classes, pseudo-box granularity, short schedule and gear imagery differ from COCO research. This is known-method application, not the REASSEMBLE CNN branch.
- **Protocol/result:** PHM-v2-image; validation-selected confidence .60. **R** 224 F images/9,883 pseudo-boxes: TP=FP=0, FN=9,883; mAP50 .000083. T4 training 234.19 s. No new metric recomputation here.
- **Sources/conclusion:** [detection code](../../src/phm2026/models/rtdetr/detection.py), [checkpoint report](../planning/R4_RTDETR_DETECTION_CHECKPOINT.md), [run](../../runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af). Informative poor pseudo-box agreement under this recipe; neither detector-family impossibility nor physical damage detection follows.

### P03 — joint detection and scalar RT-DETR

- **Task/inputs:** v2 pseudo-box agreement plus per-image proxy regression.
- **Forward/pretraining:** P02 checkpoint; encoder layer 27 (`256×20×20`) → spatial mean → 256→128→1, without detach. Loss `Ldet + λ SmoothL1(scaled scalar, scaled target)`, λ=58.261490 from training gradient balance; shared encoder and scalar head trained, first nine detector layers frozen.
- **Precedent/difference:** RT-DETR plus standard auxiliary multitask supervision; extra scalar objective/gradient balancing is a task adaptation. No controlled loss/head ablation establishes a novel method or unique explanation.
- **Protocol/result:** PHM-v2-image, selected epoch 2/stop 4. **R** image MAE .732990, run-cluster interval [.656733,.838133]; raw run MAE 1.627254, worse than frozen P01's reported 1.347. Detection mAP50 .000054; TP88/FP57,606/FN9,795 at .01. T4 160.62 s, peak allocation 2.65 GB.
- **Sources/conclusion:** [multitask code](../../src/phm2026/models/rtdetr/multitask.py), [report](../planning/R4_RTDETR_MULTITASK_CHECKPOINT.md), [run](../../runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099). Image-level proxy gain does not imply run-level gain or validated localization.

### P04 — minute-feature pipeline and custom PatchTST scalar regressor

- **Task/inputs:** PHM-v3 current post-run proxy from variable-length sequences of 72 minute features: seven statistics plus missingness for nine process/RMS/condition-indicator channels. These are derived summaries, not the raw high-frequency waveform.
- **Forward/pretraining:** scratch channel-independent shared Transformer: patch16/stride8 → width32, two encoder layers/four heads/FF64, sinusoidal positions → valid-patch mean → channel concatenation → LayerNorm/64-unit GELU head → scalar. No pretrained time-series checkpoint.
- **Precedent/difference:** [PatchTST](https://arxiv.org/html/2211.14730v2) supplies channel-independent patch encoding. Local variable-length zero padding/any-valid patch masks, masked mean, scalar regression and external scaling differ from its fixed-context forecasting/flattened forecast head and pretraining options. These changes alter what is represented and masked, but are adaptations rather than certified novelty.
- **Protocol/result:** PHM-LOEO; **V** MAE .941455 versus constant .804156; historical paired interval spans both directions. The current YAML still says target v2/device CUDA while this runner consumes pinned v3 sensor-summary labels and has its own CPU default: an effective-provenance discrepancy, not permission to relabel the result or infer actual runtime device from the YAML.
- **Sources/conclusion:** [model](../../src/phm2026/models/patchtst/model.py), [preprocessing](../../src/phm2026/preprocessing/timeseries.py), [config](../../configs/experiments/phm2026_fusion_latefusion.yaml), [runner](../../scripts/phm2026/results/loeo_evaluation.py). No demonstrated predictive improvement. The patch grid uses padded batch length; output/score impact is U, not an established harmlessness or failure result.

### P05 — sorted tooth-profile head

- **Task/inputs:** predict the sorted distribution of tooth proxy values from P04's sensor representation; tooth identity is discarded.
- **Forward/pretraining:** `y1=b(z)`, successive outputs `y(k)=y1+Σ softplus(dj(z))`; head initialized to the training mean sorted profile with target-scale correction. `L = L1(profile) + .5 L1(top-three mean)`. Scratch encoder/head; ascending rank, not time monotonicity.
- **Precedent/difference:** PatchTST-style encoding with a standard positive-increment ordered output parameterization; no single exact original full-model reproduction was identified. Structural ordering and initialization are practical adaptations.
- **Protocol/result:** historical profile development includes repeatedly assessed EXP-F and target-version changes. **V** component/loss exists; **R** profile diagnostics document the work. A defensible matched incremental profile-head benefit is not established in this consolidation; do not substitute old v2 or missing median-28 numbers.
- **Sources/conclusion:** [head/loss](../../src/phm2026/models/patchtst/model.py), [profile diagnostics](../thesis/PROFILE_DIAGNOSTICS_V3.json), [target ledger](../thesis/TARGET_VERSION_LEDGER.md). Useful implementation record; physical tooth localization or an independent contribution from ordering is unsupported.

### P06 — retained three-group sensor feature fusion (`fused_all_three`)

- **Task/inputs:** PHM-v3 run regression; separate context (rpm/torque/temperature), RMS (axial/radial) and CI (FM4/NA4/M6A/ALR) groups from the same sensing pipeline.
- **Forward/pretraining:** separate scratch PatchTST encoder per group → pooled channel embeddings → concatenate → one scalar MLP. Despite `LateFusionRegressor`, this is feature concatenation after grouped encoding, not a stacker of branch predictions.
- **Precedent/difference:** modular representation fusion plus PatchTST; group-specific weights replace globally shared channel-encoder weights. Equal final embedding width does not make encoder capacity/weight sharing equal. This is neither visual–sensor fusion nor a pure fusion-operator isolation.
- **Protocol/result:** PHM-LOEO; **V** MAE .823786, direct Δ vs constant +.019629. **R** bootstrap-mean Δ +.017668, interval [−.196189,.227769]. Distinguish the stored bootstrap mean from the empirical difference.
- **Sources/conclusion:** [fusion source](../../src/phm2026/fusion/late_fusion.py), [CSV](../../runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv), [report](../thesis/FUSION_RESULTS_20260912T111025Z.md). No demonstrated improvement; no equivalence, absence-of-information or physical damage claim.

### P07–P10 — separate four-arm PHM sensor-fusion experiment

Shared evidence: [source](../../src/phm2026/fusion/modality_fusion.py), [execution script](../../scripts/phm2026/results/sq2_sq3_fusion.py), [JSON](../thesis/SQ2_SQ3_RESULTS.json), [report](../thesis/SQ2_SQ3_RESULTS_20260913T053509Z.md). PHM-v3/LOEO experiment rule, three seeds, run-level MAE and reported run-bootstrap intervals. Four nonempty groups: M1 axial RMS 8, M2 radial RMS 8, M4 context 24, M5 CI 32; M3 encoder has **zero** columns. All neural components train from scratch.

| ID | Implemented architecture / closest precedent and exact difference | Measurement (R) and bounded conclusion |
|---|---|---|
| **P07 / A1** | One PatchTST-style regressor for each nonempty sensor group; known unimodal reference adapted to run proxy regression. | M1 .8811, M2 .8289, M4 .8832, M5 .9399 MAE; none demonstrates improvement over constant .8042. |
| **P08 / A2** | Existing single shared channel-independent encoder across all 72 features, then concatenated channel outputs/head; called “concatenation.” It is not attention jointly across channels or P06's separate group encoders. | MAE .9643 ± .0779 seed SD. Grouping/parameter sharing and fitting differ from A3/A4; no pure fusion-mechanism causal attribution. |
| **P09 / A3** | One group encoder and scalar head per group; unrestricted learned affine combination of four scalars, initialized uniformly. Decision-level modular fusion, related to established stacking/ensembles; components trained jointly here rather than Wolpert-style independent OOF meta-fitting. | MAE .8288 ± .0106; marginal A3−A4 [−.1619,−.0046]. One of 28 pairwise comparisons, three experimental domains; do not claim multiplicity-adjusted universal superiority. |
| **P10 / A4** | Each group encoder projected to shared width32; M4 encoded context → softmax gate; weighted embedding sum → regression head. [GMU](https://arxiv.org/html/1702.01992v1)-related representation gating, but scalar group weights, context-only gate, regression and separate projections differ from GMU's featurewise bimodal units. | MAE .9074 ± .0745. Reported zero/noise ablations do not establish useful robustness. M1/M2 faults cannot directly alter this M4-only gate; zeroing M4 retains positional/mask/length pathways, so the “bias-only fallback” code comment is insufficient. |

All four arms predict the provisional scalar; none is the REASSEMBLE F-series. M3-drop is a vacuous control. The untrained length probe bounds a possible mechanism; it does not prove the trained gate uses length or ignores values. Flat losses around a weak predictor do not establish robustness.

### P11 — AnomalyDINO-style image change diagnostic

- **Task/inputs:** compare selected tooth images against same-experiment, same-tooth nominal baseline (`break_in/test_start/pre_run`); assess agreement with the 42-image human-review sample, 38 determinate calls.
- **Forward/pretraining:** frozen pretrained DINOv2 patch14 features, L2 normalization; each query patch's minimum cosine distance to baseline patches; top-q mean. No learned local detector/head. ROI resize 728×182. Within each experiment rank 14 selected images, top seven called damaged; not a transferable calibrated threshold.
- **Precedent/difference:** [AnomalyDINO, WACV 2025](https://openaccess.thecvf.com/content/WACV2025/papers/Damm_AnomalyDINO_Boosting_Patch-Based_Few-Shot_Anomaly_Detection_with_DINOv2_WACV_2025_paper.pdf): nominal patch memory/nearest-neighbor scoring reused; per-tooth baseline conditioning, cropped geometry and selected balanced rank-call evaluation change the task. No paper benchmark replication.
- **Protocol/result:** **R** prespecified small/per-tooth/top1% agreement 60.5%; best of twenty 76.3%, heuristic 78.9%. Best selected on the same 38 calls; no reliable inferiority/equivalence or physical-area validation established. Global mean performing best and brightness association motivate a confounding hypothesis, not proof of exclusive brightness dependence.
- **Sources/conclusion:** [scoring source](../../scripts/phm2026/results/anomalydino_validated.py), [sweep](../../scripts/phm2026/results/anomalydino_sweep.py), [aggregate report](../thesis/ANOMALYDINO_RESULT_20260913T215556Z.md). Diagnostic negative/inconclusive evidence; no new raw images or private review mappings read here. This sample is separate from the REASSEMBLE 64-clip review.

### P12 — raw vibration/angular diagnostic features

- **Task/inputs:** screen association with PHM-v3 run proxy; historical bounded sample of native 102.4 kHz Accel1/Accel2/absolute encoder, 472 steady files across 20 runs. No fresh raw access in TASK 4.
- **Forward/pretraining:** unwrap angle, enforce nondecreasing angle, interpolate 4,096 samples/revolution, average revolutions, remove specified mesh orders/sidebands, compute moments/envelope/sideband/broadband measures, aggregate 50 run features. No trained representation.
- **Precedent/difference:** classical time-synchronous gear diagnostics; [Lewicki et al., NASA/TM-2009-215667](https://ntrs.nasa.gov/api/citations/20090039501/downloads/20090039501.pdf), Appendix A, is a concrete primary comparator, not the original invention of every indicator. Local “NA4” uses run-wide variance and the same mesh/±1-removed signal as local “FM4”; the cited residual keeps first sidebands and uses a running variance. Formula names therefore do not establish exact replication.
- **Protocol/result:** **R** run-mean |Spearman|≥.5 screen, 300 within-experiment label permutations; EXP-F 16/50 passes versus null median11, exceedance fraction .223. EXP-B zero observed exceedances is not a probability of zero. No L2/L3 predictive model executed after the gate failed.
- **Sources/conclusion:** [angular source](../../scripts/rawvib/angular_features.py), [screen](../../scripts/rawvib/l1_screen.py), [report](../thesis/RAW_VIB_20260927T095726Z.md). No established association under this screen; not evidence that all raw vibration lacks damage information. Formula/sampling/target and small-domain limits remain material.

### P13 — tooth-sector order-statistic diagnostic

- **Task/inputs:** same historical TSA file list, including DAQ transforms; contrast revolution-wide with concentrated sector summaries against the run proxy.
- **Forward/pretraining:** cut 4,096 points at `round(k·4096/28)` into 28 sectors, compute RMS/kurtosis/crest/range/energy fraction, then top1/top3/concentration/spread. Deterministic; no learning. Sorting values is invariant to sector permutation, but arbitrary phase shifts can change which samples fall inside sectors; exact continuous rotation invariance is not proved.
- **Precedent/difference:** established synchronous diagnostics plus task-specific upper-order aggregation. No physical tooth registration; 28 sectors versus target's 24 teeth; aggregation and indicator definitions differ from a localization method.
- **Protocol/result:** **R** same L1 screen, EXP-F 26/80 versus null median17, .223; DAQ sector .09. DAQ/own TSA best circular correlation median .997 is useful transform agreement, not external prediction validation or a complete feature-formula audit.
- **Sources/conclusion:** [sector code](../../scripts/rawvib/sector_features.py), [screen](../../scripts/rawvib/sector_screen.py), [report](../thesis/TOOTH_SECTOR_20260927T102354Z.md). This attempted aggregation did not pass its gate. Positive sign for every indicator is an assumption, not a universal physical law; do not conclude dilution is universally irrelevant or inverse associations impossible.

### P14 — teacher/oracle and odd/even photo diagnostics

- **Task/inputs:** assess what image predictions might supply to sensor supervision; saved R4 predictions cover A/F only, 13 runs. Proxy labels remain image-derived.
- **Forward/pretraining:** postprocess frozen predictions into tooth/run ranks; train-side rank mapping and odd/even twelve-tooth splits. No new encoder trained in these diagnostics. Proposed real-data distillation was not built.
- **Precedent/difference:** privileged-information/teacher diagnostics and rank mapping, not a deployed multimodal model or uniquely identified information decomposition.
- **Protocol/result:** **R** computable rank oracle on five A runs: MAE .5724 versus matched constant .7430; broad individual intervals. Odd/even correlations .3736/.4011, exceedance .105/.087 on 13 runs. Split teeth do not remove shared run/lighting effects; correlation changes do not estimate a precise artifact fraction.
- **Sources/conclusion:** [teacher analysis](../../scripts/phm2026/results/analyze_teacher_identity.py), [closing diagnostics](../../scripts/phm2026/results/closing_tasks_a_b.py), [report](../thesis/CLOSING_EXPERIMENTS_20260912T171608Z.md). Incomplete exploratory feasibility evidence; no deployable oracle gain, independent physical truth or executed image–sensor distillation contribution.

### P15 — synthetic signal/rank-distillation controls (not PHM prediction results)

- **Task/inputs:** artificial features generated from run targets: `x=α z(target)+sqrt(1−α²) ε`; synthetic teacher with β=.678. Real run lengths/split skeleton, deliberately target-derived synthetic inputs.
- **Forward/pretraining:** scratch P04 student plus optional `Σ softplus(−sign(ti−tj)(si−sj))` ranking loss. [RankNet](https://www.microsoft.com/en-us/research/publication/learning-to-rank-using-gradient-descent/) is a closest pairwise-logistic precedent; here teacher-derived pair signs supplement regression rather than human search relevance training. Known loss adaptation, not a new ranking method.
- **Protocol/result:** **R** injection controls and later α/weight/noise-granularity grids exist; original strong-signal regime saturates and rank transfer is mixed/harmful in some cells. Repeated minute noise averages away; per-run noise changes the experiment. These controls do not prove absence of real-data signal or absence of leakage in every real pipeline.
- **Sources/conclusion:** [control](../../scripts/phm2026/results/closing_task_c.py), [retest](../../scripts/phm2026/results/closing_task_c3_retest.py), [synthetic report](../thesis/CLOSING_EXPERIMENTS_20260912T171608Z.md), [retest grid](../thesis/CLOSING_C3_RETEST_grid_per_minute.json). Appendix control evidence only, always in a separately labelled synthetic table. No generated target-aligned input is a valid real predictor.

### P16 — feature/target diagnostics and historical monotonic rescoring

- **Task/inputs:** diagnose within-experiment feature association, target trajectories/repeated-photo variability, and the interpretation of saved fixed-split scores; not a new physical-damage predictor.
- **Forward/fitting:** D1 run-mean feature/rank screens and D2 isotonic target-versus-run diagnostics; separate rescoring fits a nondecreasing map from saved predictions to the **same assessment targets**. This is standard isotonic regression used retrospectively, not a deployable training-fitted calibrator or a new method. Exact original-method/official-challenge specification verification is not established here.
- **Protocol/result:** **R** historical eight-run EXP-F rescoring reverses raw-MAE ranking, but its retained null report says noise matches/beats the model's monotonic score about48% of the time. These old fixed-split/target-version results are not current v3 LOEO performance. No new null draws were run in TASK4.
- **Sources/conclusion:** [D1/D2 source](../../scripts/phm2026/results/diagnose_signal_and_monotonicity.py), [rescore](../../scripts/phm2026/results/rescore_monotonic.py), [metric](../../src/phm2026/evaluation/monotonic.py), [null source](../../scripts/phm2026/results/monotonic_null_test.py), [historical report](../thesis/OVERNIGHT_20260912T054144Z.md). Informative metric/proxy feasibility diagnostics, not evidence of generalization or independent calibration. Do not equate target cumulative maximum, isotonic score mapping, sorted tooth rank and physical time progression.

## REASSEMBLE retained implementation

### R00 — cohort, trivial/action controls and conditional permutations

- **Task/inputs:** completed-action failure; native labels, selected hand-camera and 22 sensor channels. Prior/majority; action-only four-way one-hot logistic control. IDs, free text, object strings and absolute time are excluded predictors; action identity is explicitly allowed only in designated controls/context.
- **Forward/training:** simple prior/constant or train-fitted logistic model; all neural branches below have separate fits. Nineteen historical circular label-shift full refits within recording/action preserve those strata, not IID exchangeability.
- **Precedent/difference:** standard negative/reference controls, nested grouped selection and conditional randomization; no novel statistical test is claimed.
- **Protocol/result:** RE-core; **V** action AP .180805/AUROC .685090. **R** observed visual/PatchTST/statistics AP exceed their nineteen nulls (plus-one p=.05, minimum resolution); neither original deep branch satisfied the joint AP-and-AUROC gate versus action-only. This history motivated Section 1B's revised bounded admission test.
- **Sources/conclusion:** [label/grouping audit](../../artifacts/reassemble/audits/label_audit.md), [fitting](../../src/reassemble/section1_models.py), [S1 report](../../artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md), [S1B report](../../artifacts/reassemble/reports/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md). Controls support scoped signal comparisons; they do not rule out shared acquisition effects or prove unique modality information.

### R01 — frozen pretrained CNN visual branch U2

- **Task/inputs:** completed-action failure from 16 deterministic hand-camera frames sampled over the full known interval.
- **Forward/pretraining:** pinned `PekingU/rtdetr_r18vd`, revision `ac77a11ff0170a41b771c03264987f8ce2b0d753`; resize640 RGB/255, no ImageNet normalization; execute `.model.backbone.model` only. Spatial means from three maps concatenate to896, frame mean → trainable128 ReLU/dropout .1 → binary head. Frozen COCO-pretrained **CNN**; no hybrid encoder, decoder, boxes or temporal attention in this path.
- **Precedent/difference:** RT-DETR feature reuse; replace detection with segment pooling/classification. Exposé §5.2 explicitly permits meaningful pretrained backbone extraction; the resulting retained branch is not a visual Transformer execution claim.
- **Protocol/result:** RE-core weighted BCE, AdamW .001/decay .001/batch128, 5/10 epochs selected inside training, sigmoid calibration. **V** AP .230658/AUROC .697795; **R** head114,945 parameters, selected budgets 5/5/10/10/5.
- **Sources/conclusion:** [features](../../src/reassemble/section1_features.py), [head](../../src/reassemble/section1_models.py), [config](../../configs/reassemble/section1.json), [S1 run](../../runs/reassemble/20260927T154732Z-section1). Useful bounded branch; completed-action support does not establish causal early warning or pretrained Transformer superiority.

### R02 — engineered-statistic sensor branch U1

- **Task/inputs:** completed-action failure from force3/torque3/gripper2/joint efforts7/joint velocities7; 22 channels.
- **Forward/pretraining:** within-interval interpolation to512 progress positions with gap/availability treatment, then ten statistics/channel =220: mean, population SD, median, min/max, quartiles, range, RMS and progress slope. Training-side standardization → balanced logistic C∈{.1,1,10} → sigmoid calibration. No Transformer or pretrained sensor encoder executes.
- **Precedent/difference:** established feature-based classification, task-specific sensor summaries; no single original research method is replicated and no novelty claim follows.
- **Protocol/result:** RE-core mean inner AP selects C; original branch thresholds. **V** AP .429392/AUROC .779325, strongest tested standalone core branch; **R** conditional permutation evidence above.
- **Sources/conclusion:** [statistics](../../src/reassemble/section1_features.py), [fit/calibration](../../src/reassemble/section1_models.py), [S1B](../../artifacts/reassemble/reports/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md). Establishes a strong reference under this recipe, not universal superiority of statistics.

### R03 — scratch HF PatchTST classification candidate

- **Task/inputs:** same task/sensors as R02; 512×22 standardized sequence and observed mask.
- **Forward/pretraining:** fresh `PatchTSTModel(PatchTSTConfig(...))`, patch32/stride16,width32,two layers/four heads/FF64, mean patch pooling/channel flatten →128 head. No `from_pretrained` time-series weights; Transformer execution is real but local training is from scratch. Observed masks do not suppress temporal attention in the retained recipe.
- **Precedent/difference:** PatchTST forecasting backbone adapted to binary classification, smaller capacity/budget, mean pooling and external scaling rather than the paper's original forecast/pretraining programme. Different from PHM's custom masking and variable-length implementation.
- **Protocol/result:** RE-core, 3/6-epoch choice, all outer folds choose6, weighted BCE/calibration; **V** AP .241591/AUROC .705351; **R**109,505 trainable parameters. Statistics' paired AP advantage is reported positive; the budget limitation is real.
- **Sources/conclusion:** [SensorHead](../../src/reassemble/section1_models.py), [config](../../configs/reassemble/section1.json), [S1 report](../../artifacts/reassemble/reports/SECTION_1_UNIMODAL_HANDOFF.md). Bounded negative candidate result; neither absence of temporal information nor failed pretrained transfer was tested.

### R04–R07 — original clean fusion F1–F6

Shared contract: RE-core R01/R02 branches, trained/calibrated within proper partitions; no new backbone or sensor encoder trained for fusion. [S1B implementation](../../src/reassemble/section1b.py), [S2 heads](../../src/reassemble/section2_models.py), [config](../../configs/reassemble/section2.json), [S2 report](../../artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md), [saved OOF](../../runs/reassemble/20260927T192852Z-section2/predictions/oof.npz).

| ID | Exact forward path / prior / material adaptation | Fitting, measurement and conclusion |
|---|---|---|
| **R04 / F1** | `(pv+ps)/2`, linear opinion pool; standard probability averaging. No fusion parameter or context. | Training-side decision threshold; **V** AP .445742/AUROC .795061. Its AP advantage over U1 has a reported interval crossing zero; not interchangeable with F2's admission result. |
| **R05 / F2** | `σ(b+av pv+as ps)`, unrestricted affine probability stacker. Closest: [Wolpert's stacking](https://cafri-labs.github.io/lab-manual/papers/wolpert1992.pdf). Binary logistic head on calibrated branch probabilities, not a convex trust-weight mean. | C1/unweighted L2 logistic, strict nested branch OOF inputs, no extra fused calibrator. Three fitted parameters. **V** AP .447299/AUROC .794968; ΔAP vs U1 +.017907, **R** [.008603,.028284]. F2−F1 discrimination unresolved; reported probability scores favor F2. |
| **R06 / F3** | Frozen visual128 and sensor statistics220 → separate128 ReLU projections → concatenate256/LayerNorm → selected hidden32/64/dropout/classifier. Established representation concatenation; does not fuse two Transformer embeddings or implement shared-embedding gates. | Two candidates, weighted BCE, per-seed sigmoid calibration, three-seed probability mean; **V** AP .412231/AUROC .785584. No demonstrated AP gain over U1; distinct loss/capacity/calibration prevents a pure fusion-operator attribution. |
| **R07a / F4** | Action4+availability2 → MLP8/16 → masked softmax weights → calibrated branch **logits** → weighted sum/sigmoid. | Unweighted BCE40 epochs, no final bias/calibrator, three-seed mean; **V** AP .443725/AUROC .781506. Action changes weights, not proven useful process awareness. |
| **R07b / F5** | Same operator; observable quality36+availability2, no direct quality-classifier bypass. | **V** AP .444549/AUROC .775987. Some clean quality ablations improve AUROC; quality-to-reliability interpretation unvalidated. |
| **R07c / F6** | Same operator; action4+quality36+availability2. | **V** AP .441356/AUROC .775523. No original gate meets declared clean incremental criteria; their AP differences versus F2 remain unresolved, not equivalence. |

The closest **combination mathematics** for R07 is [Heskes' logarithmic opinion pooling](https://proceedings.neurips.cc/paper_files/paper/1997/file/59f51fd6937412b7e56ded1ea2470c25-Paper.pdf); contextual allocation is conceptually related to GMU. **I:** for each seed,

`pG = σ(Σ wm(u) logit(pm)) = Π pm^wm / (Π pm^wm + Π (1−pm)^wm)`.

Nonnegative weights sum to one, so the per-seed probability lies between the clipped branch probabilities. Averaging three seed probabilities preserves that bound; it is not generally sigmoid of the mean weights. **V:** saved ensembles satisfy it within float32-scale tolerance. F2 can extrapolate and has an intercept; the original gates cannot. Link, constraints, loss, calibration, capacity and optimization change together. These are scientifically material family differences; they do not identify why a gate failed. The original exposé's representation-space gate is not literally implemented by REASSEMBLE R07; PHM P10 is a different representation gate on sensor subgroups.

### R08 — original frozen-model robustness suite

- **Task/inputs:** same annotated action target and fitted models U1/U2/F1/F2/F5/F6; single-modality pixel noise, blur, frame removal, sensor noise, channel removal, time-block removal, stuck force/torque and complete absence. Faults are synthetic interventions, not new industrial acquisitions.
- **Forward/pretraining:** frozen branch and fusion inference; recompute quality, keep fitted normalization/calibration/thresholds. Full loss explicitly returns surviving calibrated branch; both absent is unavailable by policy, not an estimated probability.
- **Precedent/difference:** established corruption/availability evaluation, related motivation from [QMF](https://proceedings.mlr.press/v202/zhang23ar/zhang23ar.pdf), [MultiBench](https://arxiv.org/html/2107.07502v2), [EmbraceNet](https://arxiv.org/html/1904.09078v1). No QMF energy/ranking reliability regularizer or EmbraceNet stochastic docking is reproduced.
- **Protocol/result:** RE-stress, original 22 conditions including clean, single realization; **V** saved condition AP/AUROC/Brier/ECE agree with historical estimates. **R**0/12 graded family/gate checks meet joint expected weight-response plus outcome criterion. S2/S3 sometimes down-weight damaged sensors appropriately, without qualifying outcome advantage.
- **Sources/conclusion:** [evaluation](../../src/reassemble/section3_evaluate.py), [sensor faults](../../src/reassemble/section3_sensor.py), [visual faults](../../src/reassemble/section3_visual.py), [report](../../artifacts/reassemble/reports/SECTION_3_ROBUSTNESS_HANDOFF.md), [results](../../runs/reassemble/20260927T204649Z-section3/results.json). Informative bounded negative. No clock-offset, external-industrial or learned missing-information recovery conclusion.

### R09 — completed original modality-dropout F6 (D6)

- **Task/inputs:** R07c architecture and frozen branches; training masks .15 visual absent/.15 sensor absent/.70 both present, never both absent.
- **Forward/pretraining:** retrain only the same small gate, three seeds, selected original settings, training-side thresholds. Singleton softmax fixes the sole weight to1 and gives zero gate-parameter gradient on missing states.
- **Precedent/difference:** [ModDrop](https://arxiv.org/html/1501.00102v2) motivates modality dropping, but trains a richer progressively fused representation. Local score-level masking cannot change the surviving branch predictor; not a replication of ModDrop's recovery mechanism.
- **Protocol/result:** original folds, 75 historical gate fits; **V** eleven saved conditions reproduced, clean AP .437651/Δ vs ordinary F6 −.003705; **R** CI [−.008546,.000288]. Mixed secondary sensor-channel improvement and image-noise harm; full-loss equality structural.
- **Sources/conclusion:** [source](../../src/reassemble/modality_dropout.py), [handoff](../../artifacts/reassemble/reports/MODALITY_DROPOUT_HANDOFF.md), [results](../../runs/reassemble/20260927T204649Z-modality-dropout/results.json). A completed original robustness extension, not September Gaussian augmentation and not unexecuted merely because the Section 3 handoff omitted it.

### R10 — calibration, feasibility and component-efficiency evaluation

- **Task/inputs:** evaluate probability quality/decisions, branch interfaces, audio eligibility, object grouping and bounded costs; these are not additional outcome models.
- **Forward/fitting:** unweighted affine sigmoid calibration on training-side OOF logits; balanced-accuracy threshold search .01–.99 in the core. [Guo et al.](https://proceedings.mlr.press/v70/guo17a/guo17a.pdf) is a calibration precedent, but affine Platt-style fitting is not exactly temperature-only scaling. Feasibility graph/clock checks and warm timings need no new learned representation.
- **Protocol/result:** **V** core Brier/ECE15 and hard decisions recomputed; **R** three-segment T4/four-CPU-thread component sum F2 504.693 ms versus U1 26.267 ms. Audio has zero independently verified annotation-to-waveform mappings despite substantial nominal coverage; no AST trained. Seventeen object categories connect all148 recordings in one graph; no qualifying physical-instance OOD model executed.
- **Sources/conclusion:** [calibration code](../../src/reassemble/section1_models.py), [efficiency source](../../src/reassemble/completion_efficiency.py), [feasibility source](../../src/reassemble/completion_gates.py), [efficiency](../../artifacts/reassemble/reports/EFFICIENCY_HANDOFF.md), [audio](../../artifacts/reassemble/reports/AUDIO_FEASIBILITY_HANDOFF.md), [object audit](../../artifacts/reassemble/reports/OBJECT_GENERALIZATION_FEASIBILITY.md). Substantial SQ4 evaluation, not prospective usability, clean-environment reproduction or plant latency certification.

## Separate September exploratory implementations

### R11 — longer-budget PatchTST

- **Task/inputs/forward:** same R03 task, 512×22 inputs and scratch architecture; S-6 retains3/6 epochs, S-LONG max100/min10/patience12; outer budgets use median inner best epochs per seed, sigmoid calibration.
- **Precedent/difference:** PatchTST application with a changed training budget, not an architectural invention. This can test whether the original short cap constrained this recipe.
- **Protocol/result:** RE-September, three seeds, **R** S-LONG AP .2853 vs matched S-6 .2557; Δ+.0297 [.0122,.0451], still below statistics .4294. Original one-seed historical .2416 is not the matched S-6 value.
- **Sources/conclusion:** [unimodal execution](../../src/reassemble/additional_improvements/unimodal.py), [handoff](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md), [run](../../runs/reassemble/additional_improvements_executed/20260928T000346Z/02_patchtst_training_budget). Budget sensitivity is supported historically; no standalone Transformer win.

### R12 — same-sensor hybrid

- **Task/inputs/forward:** C1 logistic stacker on nested S-LONG and statistics probabilities, both representing the same sensor modality; three parameters, frozen branch outputs at meta-fitting.
- **Precedent/difference:** Wolpert-style stacking across representations, not visual–sensor fusion or a novel multimodal architecture.
- **Protocol/result:** own proper nested branch matrices in RE-September; **R** AP .4403/AUROC .7948; versus statistics ΔAP+.0110 [.0054,.0181]. This highlights useful combination despite a weaker standalone branch; matched sensor-only meta-calibration control remains relevant to mechanism attribution.
- **Sources/conclusion:** [hybrid code](../../src/reassemble/additional_improvements/hybrid.py), [September report](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md). Task-specific empirical observation, not evidence of an additional sensing modality.

### R13 — static-anchored coefficient adaptation

- **Task/inputs:** R05 probabilities plus action4/quality36/availability2 context. Frozen, proper-partition F2 anchor.
- **Forward/training:** `σ(b+Σ am[1+tanh(hm(u))]pm)`; adaptive42→16→2 with zero final initialization, or two learned constant adjustments. Anchor bias fixed, sign of each coefficient preserved, scale between0 and2. BCE+λ mean(δ²), λ∈{.01,.1,1}, inner stopping/selection, three seeds.
- **Precedent/difference:** restricted weight generation related to [HyperNetworks](https://arxiv.org/pdf/1609.09106) and conditional affine modulation, not the original normalized gates or a reproduction of a full HyperNetwork. Anchor, bounded two-coefficient variation and exact initial parity are engineering controls.
- **Protocol/result:** RE-September, **R** adaptive AP .4683 vs A0 .4473; Δ+.0210 [.0015,.0419]; vs constant-adjustment +.0226 [.0036,.0432]. AUROC gain unresolved; failure recall lower/ECE higher. A0 thresholds differ from historical F2 even when probability parity holds.
- **Sources/conclusion:** [model](../../src/reassemble/additional_improvements/models.py), [fitting](../../src/reassemble/additional_improvements/anchored.py), [report](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md). Preserve a positive exploratory clean comparison; do not say all adaptation failed or infer robustness/reliability.

### R14 — matched Gaussian augmentation comparison

- **Task/inputs/forward:** original branches and separate clean/augmented F2, F6 and R13 adaptive heads; 50% clean/25% image Gaussian/25% sensor Gaussian fitting exposure. Quality recomputed; no fault identity predictor.
- **Precedent/difference:** established robustness augmentation, matched static reference; different model families and direct coefficient constraints remain. Gaussian training exposure differs from R09 whole-modality dropout and October's mixture.
- **Protocol/result:** RE-September, five stochastic assessment repeats where specified; **R** primary six seen-family-condition adaptive−augmented-static mean AP+.0097 [−.0034,.0228]. Harm under some held-out channel/time faults; clean noninferiority criteria not met. `clean_F6` is a separate refit, not historical F6.
- **Sources/conclusion:** [robust fusion code](../../src/reassemble/additional_improvements/robust_fusion.py), [report](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md), [run](../../runs/reassemble/additional_improvements_executed/20260928T000346Z/04_corruption_training). Inconclusive primary robustness; selective favorable conditions cannot establish general advantage.

### R15 — boundary-aware pooling and one conditional static-fusion follow-up

- **Task/inputs:** retrospective completed-action failure from the same cached frame features. V0 full mean; V1 first/second halves; V2 three bins; V3 last quarter; V4 early/late; V5 ordered GRU64/fixed positions.
- **Forward/pretraining:** frozen CNN; V1–4 shared896→128 per-bin projection then concatenate/classify; V3 has the same114,945 head parameters as V0. V5 changes recurrent family/capacity to82,433. [Temporal Segment Networks](https://wanglimin.github.io/papers/WangXWQLTV_ECCV16.pdf) is a temporal-consensus precedent, but trains snippet class scores; ours pools frozen features before a classifier. No literal TSN reproduction.
- **Protocol/result:** separate same-cohort protocol, one historical seed family, V0–4 budgets5/10 and V5 5/10/20. **R** V3 visual AP .319146 vs .230658; Δ+.0885 [.0424,.1293], positive simultaneous lower bound across five comparisons. V3-selected static F2 follow-up .493437 vs .447299; Δ+.0461 [.0260,.0632]. V5 AP change unresolved.
- **Sources/conclusion:** [models](../../src/reassemble/boundary_visual/models.py), [training](../../src/reassemble/boundary_visual/training.py), [report](../../artifacts/reassemble/reports/BOUNDARY_AWARE_VISUAL_POOLING_HANDOFF.md). Strong exploratory evidence that observation location/aggregation matters. V3 does not learn sequence order; neither causal timing nor online detection follows. Not combined with new sensor hybrid/anchor winners.

## Separate October implementations

### R16 — frozen CNN versus spatial hybrid encoder (E4)

- **Task/inputs/forward:** same 16 frames; frozen backbone-only896 versus backbone→input projections→hybrid spatial AIFI/FPN/PAN→means768. Guarded stopping before decoder/proposals. Both frame averages discard temporal order.
- **Pretraining/difference:** both pretrained frozen RT-DETR prefixes, trained128-unit heads; different feature width, active parameters and compute. A real spatial Transformer executes in the encoder arm, unlike retained R01. This is whole-representation comparison, not isolated attention.
- **Protocol/result:** RE-October, G/C calibration, fixed five-epoch heads, threshold .5, one seed family/full fivefold coverage. **R** F2 .440764 CNN vs .424979 encoder; Δ−.015785 [−.024804,−.005800]. Not the core F2 .447299 procedure.
- **Sources/conclusion:** [extractor](../../00_experiments/rt_detr_encoder_comparison/code/features.py), [config](../../00_experiments/rt_detr_encoder_comparison/config.json), [report](../../00_experiments/rt_detr_encoder_comparison/results/run_01/comparison/RESULTS_SUMMARY.md). Negative under the fixed recipe; no general anti-attention conclusion or temporal Transformer evidence.

### R17 — asymmetric-budget final CNN-stage fine-tuning (E7)

- **Task/inputs/forward:** completed-action failure;16/32 full-action frames, original CNN path/mean pooling, no detector/temporal Transformer. Frozen heads5 epochs versus final CNN stage+head2 joint epochs; earlier weights/normalization buffers frozen.
- **Precedent/difference:** ordinary pretrained feature transfer/fine-tuning, task-specific limited adaptation and duration. Epoch/compute differ; this cannot uniquely identify fine-tuning's effect.
- **Protocol/result:** RE-October full fivefold cohort, one seed family,100 completed visual fits, fixed .5. **R** tuned16−frozen16 F2 Δ−.003159 [−.012573,.008052]; no demonstrated fusion improvement. Fine-tuned32 visual point higher than frozen16 but fusion point does not improve.
- **Sources/conclusion:** [retained forward source](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/source/visual_model.py), [config](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/config/resolved_config.json), [report](../../00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/comparison/RESULTS_SUMMARY.md). Completed October study; distinct from cancelled September Task1. Inconclusive benefit, not proof frozen models are universally better.

### R18 — matched two-epoch32-frame tuning diagnosis (E8)

- **Task/inputs/forward:** same two CNN arms,32 frames and two epochs, seeds42/20261023. Equal data/epochs, unequal compute/parameter training. Fixed sensor branch.
- **Precedent/difference:** standard fine-tuning/ensemble controls plus calibration/complementarity diagnostics; no new architecture. Uniform probability mean and F2 are both measured.
- **Protocol/result:** RE-October, all five folds for both seeds;75 new/25 reused fits. **R** F2 tuned−frozen −.000796 [−.006424,.006072] and −.002822 [−.008285,.003602]. Visual sign varies by seed; proposed causes remain unresolved. Two seeds share recordings and are not independent dataset replications.
- **Sources/conclusion:** [pipeline](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/code/pipeline.py), [protocol](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/PROTOCOL.md), [report](../../00_experiments/frozen32_vs_finetuned32_fusion_diagnosis/results/comparison/RESULTS_SUMMARY.md). Informative inconclusive controlled follow-up; no convergence, equivalence or causal calibration conclusion.

### R19 — selected static F2 raw-noise pilot (E5)

- **Task/inputs/forward:** frozen16 F2 selected on pre-noise eligible common coverage; native pixels/sensors corrupted, fixed branches/calibrators/threshold .5; no training or adaptive switching for partial faults.
- **Precedent/difference:** standard fixed-predictor sensitivity assessment, not a learned reliability method. Complete absence is a separately declared surviving-branch policy.
- **Protocol/result:** October fold_01 only753 actions/77 failures/26 recordings;51 saved realizations, three repeats where stochastic. **R** clean AP .307929; strong image .284640, strong sensor .169409. Sensor AP-drop interval [.070831,.221115]; “harmful fusion” versus unchanged branch point contrasts all have zero-containing intervals.
- **Sources/conclusion:** [noise code](../../00_experiments/fusion_noise_test/code), [report](../../00_experiments/fusion_noise_test/results/run_02/comparison/RESULTS_SUMMARY.md). Bounded sensitivity, not adaptive superiority or a fivefold robustness result.

### R20 — augmentation-matched quality-interaction pilot (E6)

- **Task/inputs:** same pilot target/coverage as R19; fixed calibrated visual/sensor probabilities, eight observable q: image gradient/clipping/contrast/unique-frame fraction and sensor finite fraction/channel availability/max gap/relative variation.
- **Forward/pretraining:** A `σ(b+a·p)` (3 parameters); B `σ(b+a·p+c·q)` (11); C `σ(b+a·p+c·q+Σm pm dm·q)` (27). q uses weighted train-only standardization and ±10 clipping. C has conditional affine probability coefficients plus a direct q pathway, not a normalized original gate. Closest algebra: [FiLM](https://arxiv.org/html/1709.07871v2) conditional affine modulation; logistic second-order features rather than deep feature-map FiLM. QMF is motivation, not the implementation.
- **Fitting:** C1 unweighted logistic with parent weights .5 clean/.25 image fault/.25 sensor fault; frozen branches, no new calibrator, threshold .5. **V**11,331 rows/3,777 parents, exact per-parent weights, training/assessment recording separation and saved quality-normalizer moments. Small logistic fitting still counts as training; no new fit here.
- **Protocol/result:**34 assessment tables/25,602 parent-realization rows, including753 explicitly both-absent unavailable rows; **V**196 finite AP/AUROC/Brier sets. Equal-repeat/severity/Gaussian-family mean AP C .257009 vs A .253996, Δ+.003012; **R**[−.026711,.032165]. Clean Δ+.004771 [−.034258,.044544]; no demonstrated zero-cost clean preservation.
- **Sources/conclusion:** [quality/design/routing source](../../00_experiments/adaptive_fusion_robustness/code/quality_fusion.py), [protocol](../../00_experiments/adaptive_fusion_robustness/results/run_01/PROTOCOL.md), [report](../../00_experiments/adaptive_fusion_robustness/results/run_01/RESULTS_SUMMARY.md), [index](../../00_experiments/adaptive_fusion_robustness/results/run_01/comparison/coverage_and_prediction_index.csv). Inconclusive specific SQ3 hypothesis. Observable q is not validated reliability; direct q, interaction capacity, target content and calibration are alternative pathways.

## Administrative and scope exclusions

- September additional-improvements Task1 was partly attempted, then cancelled by the researcher on 2026-09-30. Preserve partial caches/checkpoints; do not score it as a completed negative or restart it. [Final scope disposition](../../artifacts/reassemble/reports/ADDITIONAL_IMPROVEMENTS_EXECUTED_HANDOFF.md). R15/R17/R18 are separate completed studies.
- Audio/AST, trimodal models, true native clock offsets/drift, prospective alarms, physical-instance OOD and independent MSM fusion validation have no qualifying predictive result here. Feasibility exclusion is not measured model failure.
- [Paderborn architecture-feasibility study](../thesis/ARCH_VAL_PB_20260926T224859Z.md) is adjacent historical evidence on another dataset. Its bearing-sharing/bearing-disjoint protocols and stopped transfer gate do not validate the PHM/REASSEMBLE fusion architecture. Keep it in an optional appendix if needed; it is outside tables A–F and was not reaudited numerically here.
- Earlier PHM fixed-split/sorted-profile/tutorial values, particularly untraceable 1.011 and missing median-28 numbers, remain historical, not retained headline evidence. The original [run index](../thesis/RUN_INDEX.md) is a dated index, not proof that only its twenty entries exist now.
- No modification is called novel because it has different code. No local comparison above is a strict reproduction of an original paper's benchmark protocol. Literature consistency is a qualitative relationship unless an actual replication design is demonstrated.

**STOP:** inventory and reporting only. No training, GPU, model forward replay, dataset/model download, raw payload scan, historical rewrite, commit or push was performed for TASK 4.
