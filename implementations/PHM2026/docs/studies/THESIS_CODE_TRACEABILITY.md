# PHM2026: Chapter 5 investigation-to-code traceability

Prepared on 2026-11-26 for the approved repository consolidation. This is the
scientific foundation for a later Chapter 5 writing review; it does not rewrite
that chapter. [Dataset guide](../../README.md) ·
[Repository thesis-to-code map](../../../../docs/THESIS_CODE_MAP.md) ·
[Saved-evidence verification receipt](THESIS_SAVED_EVIDENCE_VERIFICATION_20261126.json)

## Scope and five-sentence verified summary

The inspected PHM workspace contains a 20-run EXP-A/B/F condition-proxy study,
with provisional photographic supervision and distinct visual and sensor
investigations.
The implemented v3 target selects one deterministic photograph per retained
tooth, excludes teeth 1–4, and averages the three largest candidate-area
percentages; the 480 saved tooth measurements reproduce all 20 saved run
targets within floating-point tolerance.
The principal sensor fusion implementation combines PatchTST embeddings from
three groups of machine measurements and uses no photographs at inference.
Recalculation of the saved principal leave-one-experiment-out predictions gives
run-level MAE 0.804156 for the training mean, 0.823786 for feature fusion and
0.941455 for the single-encoder PatchTST, with the paired fusion-minus-constant
95% run-bootstrap interval spanning −0.196189 to +0.227769 percentage points.
These checks verify saved-table arithmetic and inspected implementation
behavior, while independent physical-damage validity, complete historical
source lineage and training reproduction remain unestablished.

**Evidence language.** VERIFIED means direct inspection or the bounded
recalculation identified here; REPORTED means a retained report's result;
INFERRED marks interpretation; PROPOSED marks future manuscript changes;
UNKNOWN marks a missing identity or execution record. A linked implementation
is not, by itself, proof that a run executed it. No model was loaded, trained,
fitted or used for inference during this check. No raw archive, image or sensor
payload was read. The verification reads compact derived targets and saved
predictions; this does not regenerate photographic measurements.

The assessment unit is a completed run's current condition proxy, not an
online event or a six-hour-ahead forecast. Its units are percentage points of
visible-flank candidate area. There is no positive class or class prevalence
for this continuous-regression task. EXP-A has 5 runs, EXP-B 7 and EXP-F 8;
run numbering is not a physical damage label. The organizer's separate
reference is not available in these local evaluations.

## Identity, evidence IDs and historical chronology

The current manuscript's existing Appendix F IDs **E020–E037** remain the
register for PHM. The approved additions E124–E133 extend that same register:
E124 feature-fusion source, E125 v3 target configuration, E126 principal LOEO
configuration, E127 predictions, E128 summary JSON, E129 run targets, E130 tooth
targets, E131 this guide, E132 verification receipt and E133 verification script.
This guide uses descriptive investigation headings, not a new evidence numbering
scheme. E022 refers to the claim matrix and E025 to
the walkthrough; they do not substitute for a run manifest. Historical names
such as `runs/`, `src/pi_multimodal_ad/` and `docs/thesis/` in frozen records
remain unchanged. Links below resolve their present locations.

| Identity | Meaning and verified boundary |
|---|---|
| Published browsing source | `e2037412036c5bbfc01fb2323215a37ef0b2e090` in `Parth-0804/pi-multimodal-ad`. The selected source/report bytes in the verification receipt equal this Git object's bytes. Remote publication/accessibility was checked in the consolidation assessment; the verifier itself checks local Git objects. |
| Local HEAD when checked | `7274a0ec3b163de1e3ca66a09e2a164693be7c75`; this identifies the checkout, not an experiment-producing revision or a publication commit for these new documents. |
| Historical experiment-producing source | Use each run's recorded revision **and** dirty/untracked state, source snapshot and available hashes. A recorded revision is not sufficient when relevant source was untracked. |
| Verified source snapshot/hash | SHA-256 identities of selected present source files, pinned-target tables, configurations and saved results are in the receipt. They establish checked bytes, not retrospective execution. |
| Publication commit for this document/verifier/receipt | Pending review and a later authorized commit. No future hash or final permalink is invented. |
| Unknown lineage | Fixed fusion and principal LOEO recorded commits omit their respective entry points; exact untracked source bytes at execution have not been recovered. |

**E027 correction.** Keep E027 attached to
[`phm2026_patchtst_baseline/20260912T053924941825Z-4235307c/config/resolved_config.yaml`](../../results/runs/phm2026_patchtst_baseline/20260912T053924941825Z-4235307c/config/resolved_config.yaml).
Its [provenance](../../results/runs/phm2026_patchtst_baseline/20260912T053924941825Z-4235307c/provenance.json)
records `scripts/training/train_late_fusion.py --device cpu`. It is an initial
fusion run written under the wrong study directory, **not** an independently
identified single-encoder baseline. The
[initial study report](TARGET_AND_FUSION_INITIAL_STUDY.md) records the subsequent
correctly named rerun. Do not repoint E027 to another file to hide the mistake.

| Period | Evidence-led reconstruction | Boundary |
|---|---|---|
| Original objective | The original exposé concerned robust multimodal industrial anomaly monitoring, initially robotic welding; PHM later supplied a gear-condition investigation. | The precise first decision/date selecting PHM is UNKNOWN in the inspected records. Do not invent a clean chronological replacement narrative or call PHM a deliberately designed negative control. |
| Initial preparation, by August 2026 | Protected EXP-A Runs 1/3/5 EDA and the D1/T2 audit sequence examined acquisition, schema, labels and pairing. | The narrower historical EDA is not the current A/B/F cohort and remains protected. |
| 2026-08-14 | [Target-formulation decision](../research_history/checkpoints/T2_TARGET_FORMULATION_DECISION.md) corrects the early assumption that absence of a supplied scalar necessarily blocks the challenge: participants were expected to derive a photographic trajectory; the organizer retained its separate reference. | This resolves task semantics, not validity of the chosen image heuristic. |
| 2026-08-14 | v1/v2 targets, visual regression, pseudo-box detector, multitask model and sensor preparation/initial PatchTST records. | Many records identify dirty trees. Visual results use v2, not the later principal v3 target. |
| 2026-09-12 | v3 target repair, monotonic-score null check, predefined fixed-split feature fusion and principal LOEO. | Historical EXP-F exposure is explicitly acknowledged. LOEO does not erase development/selection history. |
| 2026-09-12–13 | Profile/teacher diagnostics, synthetic controls, four-arm sensor fusion, blind visual inspection and DINOv2 comparison. | Separate protocols and purposes; synthetic controls and selected visual inspection are not independent physical labels. |
| Late September 2026 | Raw-vibration and tooth-sector screens preserve failed feature gates and unexecuted later stages. | Failure of the specified screen is not proof that all physical information is absent. |
| Subsequent studies | [REASSEMBLE handoff](../../../REASSEMBLE/results/artifacts/reports/FINAL_REASSEMBLE_HANDOFF.md) records the move toward annotated outcomes and simultaneously available inference modalities. | This is a change in empirical suitability and task, not proof that architecture transfer or universal superiority was achieved. |

## Investigation map

Section numbers below follow the current Chapter 5 headings: §§5.1–5.4 context
and preparation, §5.5 target versions, §5.6 photographic assessment, §5.7 sensor
prediction, §5.8 diagnostics, and §§5.9–5.10 conclusions/next-study rationale.
They are proposed insertion boundaries, not new chapter text. Each investigation
follows **scientific motivation → investigation → supported finding → limitation**;
the technical route is **input → middle → output → result**.

### Dataset selection, acquisition, association and initial EDA — §§5.1–5.4; E020, E021, E025

- **Motivation:** determine whether industrial machine measurements and post-run
  photographs support condition estimation with traceable supervision.
- **Input → middle → output:** scoped A/B/F archives and acquisition identities →
  dataset inventory, bounded schema/alignment checks and exploratory summaries →
  source manifests and candidate run/tooth associations. The protected initial
  EDA covers EXP-A Runs 1, 3 and 5 only.
- **Implementation/configuration:** [dataset configuration](../../configs/dataset.yaml),
  [data contracts](../../src/phm2026/data_contracts),
  [profiling](../../src/phm2026/profiling),
  [dataset scripts](../../scripts/dataset), and the protected
  [initial EDA](../../experiments/exp_a_initial_eda_r1_r3_r5/).
- **Evaluation/result:** [D1.2](../research_history/checkpoints/D1_2_CHECKPOINT.md),
  [D1.3](../research_history/checkpoints/D1_3_CHECKPOINT.md) and
  [T2.1](../research_history/checkpoints/T2_1_CHECKPOINT.md) preserve the
  REPORTED feasibility findings and changed label interpretation. Later models
  provide run-level outputs; EDA alone supplies no predictive result.
- **Limitation:** no new raw-data audit was performed. The organizer warning of
  311 overlapping EXP-A Run-2 files remains REPORTED, not independently counted
  here; preserve both runs. Filename/run association is not hardware
  synchronization. The initial selection rationale is incompletely recovered.

### Task formulation and missing physical ground truth — §§5.3, 5.5; E020, E023, E035

- **Motivation:** define an estimand when released quantitative tooth-damage
  ground truth is unavailable to the participant.
- **Input → middle → output:** post-run photographs associated by experiment,
  run and tooth → deterministic visible-flank candidate-area measurement →
  provisional per-tooth percentages and a top-three run proxy.
- **Implementation/configuration:**
  [`measure_damage_candidate` and `aggregate_targets`](../../src/phm2026/targets/image_damage.py),
  [original formulation](../research_history/checkpoints/T2_TARGET_FORMULATION_DECISION.md),
  [target ledger](TARGET_VERSION_LEDGER.md).
- **Evaluation/result:** VERIFIED source distinguishes raw top-three mean from
  causal cumulative-maximum fields; the principal saved predictions use the
  raw v3 target. Participant-derived supervision is compatible with the stated
  challenge task, but physical measurement validity remains unestablished.
- **Limitation:** do not equate candidate-area percentage with independently
  measured spall area, a validated damage class or remaining useful life.
  Photographs supervise the sensor experiment; they are not its inference input.

### Photographic measurement and v1/v2 target production — §§5.5–5.6; E023, E035

- **Motivation:** make the proposed label construction explicit and repeatable.
- **Input → middle → output:** RGB flank ROI → LAB luminance, CLAHE, Gaussian
  background subtraction, robust residual threshold, morphological opening
  (5×5 ellipse) and closing (21×5 rectangle), then sufficiently large horizontal
  connected components → `100 × candidate pixels / ROI pixels` per image.
  v1/v2 use maximum candidate ratio across views, then the mean of the three
  largest tooth values per run.
- **Implementation/configuration:**
  [`measure_damage_candidate`, lines 114–194](../../src/phm2026/targets/image_damage.py),
  [target configuration](../../configs/experiments/phm2026_image_target.yaml),
  [derivation entry point](../../scripts/targets/derive_image_targets.py).
- **Execution/evidence:** v1
  [`20260814T011051111606Z-e7600a8a`](../../results/superseded/phm2026_image_target/20260814T011051111606Z-e7600a8a)
  and v2
  [`20260814T012054997053Z-e195f6d9`](../../results/runs/phm2026_image_target/20260814T012054997053Z-e195f6d9);
  the ledger reports recorded revision `d3ce4808` with a dirty tree.
- **Result/limitation:** v1→v2 narrows the vertical ROI from 0.08–0.72 to
  0.12–0.50 and changes residual threshold 2.2→2.0; scales differ substantially.
  VERIFIED source computes `gradient_z` but does not use it in the mask, despite
  a configured gradient threshold. Do not describe a gradient-constrained mask.
  Multiple close-ups of A/B teeth 1–4 make maximum-over-views protocol-sensitive.

### Median-28 code state and v3 target repair — §5.5, §5.6.4; E023, E035

- **Motivation:** address unequal photographic measurement protocols without
  pretending the revised target became independent physical ground truth.
- **Input → middle → output:** retained image measurements → canonical view
  where available, otherwise earliest camera-sequence view, with deterministic
  tie-breaking; omit teeth 1–4 → 24 tooth values per run and top-three mean.
- **Implementation/configuration:** [`aggregate_targets`](../../src/phm2026/targets/image_damage.py),
  [v3 resolved configuration](../../results/runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/config/resolved_config.yaml),
  [v3 run](../../results/runs/phm2026_image_target/20260912T052857044116Z-c936a4e3).
- **Evaluation/result:** VERIFIED 480 saved tooth rows reproduce all 20 run
  targets (maximum difference below `1e-12`); every saved principal LOEO truth
  equals v3. The v3 target Parquet hash matches the configuration's pinned
  `e5e098…e92f1`. Recorded target revision is
  `246024367e8b8a0b2463274115d760fb579ef50c`, dirty=false,
  untracked_present=true.
- **Limitation:** the ledger's median-28 code state at `8a9ac7a` retained a v2
  string but has no located production artifact; it is not another executed
  target run. The v3 repair is motivated by protocol comparability, not by
  making held-out distributions agree; EXP-F had already informed development.

### Frozen RT-DETR-derived scalar regression — §5.6; E024, E033

- **Motivation:** test whether pretrained visual representations predict the
  photographic proxy, separately from whether sensors predict it.
- **Input → middle → output:** tooth image → full `RTDETR.predict` inference
  with hooks at layers 21/24/27, spatial average pooling of three 256-channel
  maps → fitted scalar MLP and per-image/tooth/run predictions.
- **Implementation/configuration:**
  [`extract_features`, `train_head`, `predict_all`](../../src/phm2026/models/rtdetr/regression.py),
  [regression configuration](../../configs/experiments/phm2026_rtdetr_regression.yaml),
  [training entry point](../../scripts/training/train_rtdetr_regression.py).
- **Execution/result:**
  [`20260814T020338751021Z-d0f225c8`](../../results/runs/phm2026_rtdetr_regression/20260814T020338751021Z-d0f225c8),
  [R3 report](../research_history/checkpoints/R3_RTDETR_CHECKPOINT.md),
  REPORTED v2 image MAE ≈0.894 and run MAE ≈1.347. The pretrained model is
  frozen; the scalar head is fitted. This differs from REASSEMBLE's backbone-only
  extraction path.
- **Limitation:** [confirmed feature-selection defect](../../experiments/walkthrough/01_rtdetr_scalar_regression/KNOWN_IMPLEMENTATION_ISSUES.md):
  the `feature_` selector also includes `feature_latency_ms`, yielding 769 inputs
  and 98,689 head parameters. Do not describe the retained fit as solely 768
  image features. Its effect size is UNKNOWN; no correction/retraining occurred.
  The run records a dirty historical tree, not a complete immutable source snapshot.

### Heuristic masks and pseudo-box supervision — §5.6, §5.8; E035, E036

- **Motivation:** investigate localization despite absence of independently
  annotated damage boxes.
- **Input → middle → output:** photographic candidate masks → connected-component
  box conversion and split-preserving detector dataset → one-class pseudo-boxes.
- **Implementation/configuration:** [pseudo-box source](../../src/phm2026/targets/pseudo_boxes.py),
  [builder](../../scripts/targets/build_rtdetr_pseudo_boxes.py),
  [configuration](../../configs/experiments/phm2026_rtdetr_pseudo_boxes.yaml).
- **Execution/result:**
  [`20260814T040854991567Z-3fa0f794`](../../results/runs/phm2026_rtdetr_pseudo_boxes/20260814T040854991567Z-3fa0f794)
  and [checkpoint report](../research_history/checkpoints/R4_PSEUDO_BOX_CHECKPOINT.md)
  retain the generated training supervision.
- **Limitation:** these are heuristic pseudo-boxes, not expert annotations.
  Agreement with them cannot validate physical damage localization. Successful
  conversion is an implementation achievement, not a detection finding.

### Genuine RT-DETR detector fine-tuning — §5.6, §5.8; E036

- **Motivation:** test object-detection learning against the available pseudo-box
  formulation rather than only a frozen feature head.
- **Input → middle → output:** RGB images and pseudo-boxes → RT-DETR-L backbone,
  hybrid encoder, decoder and box/class heads, first nine layers frozen during
  the reported fine-tuning stage → ranked detections and thresholded boxes.
- **Implementation/configuration:** [training](../../scripts/training/train_rtdetr_detector.py),
  [matching/AP/threshold evaluation](../../src/phm2026/models/rtdetr/detection.py),
  [configuration](../../configs/experiments/phm2026_rtdetr_detection.yaml).
- **Execution/result:** canonical
  [`20260814T043751107678Z-7f1e13af`](../../results/runs/phm2026_rtdetr_detection/20260814T043751107678Z-7f1e13af);
  [report](../research_history/checkpoints/R4_RTDETR_DETECTION_CHECKPOINT.md)
  records four fine-tuning epochs, selected epoch 1, validation-selected
  confidence 0.60, test TP=0/FP=0/FN=9,883 over 224 images, and very small
  rank-based AP. Preserve the earlier failed attempt as historical evidence.
- **Limitation:** a functional detector did not establish useful pseudo-box
  detection, still less physical damage accuracy. Low-confidence rank AP and
  zero detections at the operating threshold are different quantities. Epochs,
  timing and checkpoint hashes here are REPORTED, not newly retrained/measured.

### Joint detection and scalar multitask model — §5.6, §5.8; E036

- **Motivation:** retain localization while learning the scalar condition proxy
  from shared visual features.
- **Input → middle → output:** image, pseudo-boxes and v2 scalar → RT-DETR with
  a non-detached layer-27 pooled feature and 256→128→1 scalar head, detection
  loss plus weighted SmoothL1 → detections and scalar predictions.
- **Implementation/configuration:** [`RTDETRMultitask`](../../src/phm2026/models/rtdetr/multitask.py),
  [training](../../scripts/training/train_rtdetr_multitask.py),
  [configuration](../../configs/experiments/phm2026_rtdetr_multitask.yaml).
- **Execution/result:**
  [`20260814T050026535618Z-9b00f099`](../../results/runs/phm2026_rtdetr_multitask/20260814T050026535618Z-9b00f099);
  [R4 report](../research_history/checkpoints/R4_RTDETR_MULTITASK_CHECKPOINT.md)
  records first nine layers frozen, different detector/head learning rates,
  selected epoch 2 and stop after 4. REPORTED EXP-F image MAE 0.732990 and
  run-top-three MAE 1.627254 concern different units; detection remained poor.
- **Limitation:** lower image error did not imply lower run error. Images remain
  an inference modality in this diagnostic, unlike the principal sensor route.
  Its 13-run reused visual row in the later LOEO table was **not retrained under
  LOEO**, lacks EXP-B predictions and is not a paired 20-run comparator.

### Sensor feature extraction and temporal input construction — §5.7.1; E031, E032

- **Motivation:** produce an inference-time machine-measurement representation
  independent of photographs while retaining run/time identities.
- **Input → middle → output:** rpm, torque, temperature, axial/radial RMS and
  FM4/NA4/M6A/ALR → seven per-minute statistics plus missingness flags for each
  of nine variables → 72 channels in ordered variable-length run sequences.
- **Implementation/configuration:** [`extract_minute_features`](../../src/phm2026/features/sensor_minutes.py),
  [`fit_feature_normalizer`, `build_run_sequences`](../../src/phm2026/preprocessing/timeseries.py),
  [v2 configuration](../../configs/experiments/phm2026_sensor_features.yaml),
  [v3 configuration](../../configs/experiments/phm2026_sensor_features_v3.yaml).
- **Execution/result:** v2
  [`20260814T121146792755Z-4016432b`](../../results/runs/phm2026_sensor_features/20260814T121146792755Z-4016432b)
  and v3
  [`20260912T053550461436Z-69f2e5ee`](../../results/runs/phm2026_sensor_features/20260912T053550461436Z-69f2e5ee)
  retain schemas, summaries and input identities. Feature construction is not
  itself a predictive result.
- **Limitation:** this principal representation uses compact machine-summary
  channels, not the raw 102.4 kHz vibration waveform. Scaling/imputation must be
  fitted to each training partition. Missingness masks describe available
  inputs; they do not create an absent encoder modality or physical labels.

### Single-encoder PatchTST and conventional reference models — §§5.7.2–5.7.4; E031, E032

- **Motivation:** compare a learned temporal representation with simple
  training-side reference predictors before attributing value to fusion.
- **Input → middle → output:** 72-channel run sequence → per-channel patches
  (length 16, stride 8), shared linear patch projection, positional encoding,
  two Transformer layers (width 32, four heads), masked pooling and scalar head
  → a run-level proxy prediction. Parameters are fitted from scratch.
- **Implementation/configuration:** [`PatchTSTRegressor.patchify/encode/forward`](../../src/phm2026/models/patchtst/model.py),
  [`ridge_predictions`, `train_patchtst`](../../src/phm2026/models/patchtst/regression.py),
  [baseline configuration](../../configs/experiments/phm2026_patchtst_baseline.yaml),
  [naive reference evaluation](../../scripts/results/evaluate_naive_baselines.py).
  Ridge selects alpha from 0.01/0.1/1/10/100 using validation; training mean and
  median are separate reference predictors.
- **Execution/result:** [P4 checkpoint](../research_history/checkpoints/P4_PATCHTST_BASELINE_CHECKPOINT.md)
  preserves initial runs; the ledger rejects the incompletely identified old
  1.011 number as a clean citable result. The principal v3 LOEO single-encoder
  MAE 0.941455 is independently recalculated below.
- **Limitation:** this is a task-fitted PatchTST-style regressor, not a reused
  pretrained forecasting foundation model. Conventional fixed-split reference
  scores are not automatically LOEO scores. E027 is not this baseline's run.

### Predefined fixed-split sensor-group feature fusion — §§5.7.2–5.7.5; E027 provenance caveat

- **Motivation:** test whether separately encoding process context, organizer
  RMS and condition indicators adds predictive value over their joint encoder.
- **Input → middle → output:** 72 derived channels partitioned into three
  machine-measurement groups → one PatchTST encoder per group, pooled embeddings
  concatenated, one fitted scalar head → end-of-run proxy.
- **Implementation/configuration:** [`LateFusionRegressor.forward`, lines 58–125](../../src/phm2026/fusion/late_fusion.py),
  [training](../../scripts/training/train_late_fusion.py),
  [configuration](../../configs/experiments/phm2026_fusion_latefusion.yaml),
  [preregistration](SENSOR_LATE_FUSION_PREREGISTRATION.md).
- **Evaluation/result:** train EXP-B, select among eight variants on EXP-A,
  evaluate the selected variant on EXP-F; seed 20260814. Run
  [`20260912T054016807597Z-e1911d4f`](../../results/runs/phm2026_fusion_latefusion/20260912T054016807597Z-e1911d4f)
  and [report](TARGET_AND_FUSION_INITIAL_STUDY.md) give REPORTED MAE 0.6548
  versus the v3 training-mean 0.7348, an observed improvement ≈0.0800 pp,
  below the declared 0.15 pp criterion, with paired interval [−0.548,+0.414].
- **Limitation:** the class name “LateFusion” describes **feature-level
  concatenation**, not scalar/probability-level fusion. It is sensor-group
  fusion, not visual–sensor inference. The recorded revision lacks this source
  (see lineage table); the current config's `target.definition_version` still
  says v2 while its pinned target directory/hash is v3. Preserve this frozen
  metadata inconsistency and resolve target identity using actual pinned bytes.

### Principal leave-one-experiment-out comparison — §§5.7.3–5.7.5; E026, E028

- **Motivation:** assess the selected architectural question across all 20 runs
  while acknowledging repeated prior use of EXP-F.
- **Input → middle → output:** saved v3 feature/target inputs → three held-out
  experiment folds with training-side imputation/scaling and validation early
  stopping → one prediction for each of 20 runs per sensor model/reference.
- **Implementation/configuration:** [`loeo_evaluation.py`](../../scripts/results/loeo_evaluation.py),
  [resolved configuration](../../results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/config/resolved_config.yaml),
  [provenance](../../results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/provenance.json).
  `main`, lines 227–258, fits the normalizer **inside** each fold; `train_fold`
  scales training targets and selects by validation loss.
- **Evaluation/result:**
  [`20260912T110848985882Z-e1911d4f`](../../results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f),
  [predictions](../../results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/tables/loeo_predictions.csv),
  [summary](../../results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json).
  VERIFIED saved-score arithmetic gives 0.804156/0.823786/0.941455 MAE for
  training mean/fusion/single encoder. No improvement over the mean is established.
- **Limitation:** not training on both remaining experiments: one trains, one
  validates. Three experiments provide limited independence; run-bootstrap
  intervals condition on the existing fitted models and omit selection/training
  uncertainty. This is not a fresh untouched external test or an equivalence
  result. Recorded source lineage is incomplete and actual per-fold selected
  epochs are not established merely by the configured cap of 80.

### Alternative scalar-combination and process-conditioned fusion — §5.8; E029, E030

- **Motivation:** compare single-group, concatenation, modular scalar-combination
  and process-conditioned feature-gating designs using the sensor channels.
- **Input → middle → output:** groups M1 acceleration RMS, M2 acceleration RMS,
  M4 process context and M5 condition indicators → separate scalar heads with
  affine combination (`DecisionLevelFusion`) or context-conditioned feature
  weighting (`ProcessAwareGatedFusion`) → run-level predictions.
- **Implementation/configuration:** [`modality_fusion.py`](../../src/phm2026/fusion/modality_fusion.py),
  [`sq2_sq3_fusion.py`](../../scripts/results/sq2_sq3_fusion.py) includes the
  architecture, seed and corruption settings; [numeric report](SQ2_SQ3_RESULTS.json),
  [narrative report](SENSOR_REPRESENTATION_FUSION_RESULTS.md).
- **Evaluation/result:** REPORTED three-seed mean MAEs: modular scalar fusion
  0.8288, gated 0.9074, concatenation 0.9643; constant 0.8042. These are a
  separate experiment from principal fusion MAE 0.8238.
- **Limitation:** VERIFIED current script fits preprocessing once before the
  rotated folds from the original split's training rows. Thus held-out EXP-B
  can influence its preprocessing; this concern does **not** apply to the
  principal fold-local implementation. This limits a clean LOEO interpretation.
  M3 encoder has zero channels, so its “drop” condition is vacuous. Nearly flat
  corruption scores do not establish robust predictive information, and gate
  changes alone do not measure trustworthy modality importance.

### Independent raw-HF/spectral PatchTST tutorial — §5.8; E037

- **Motivation:** test whether a richer waveform/spectral representation helps
  where compact machine-summary features did not establish improvement.
- **Input → middle → output:** raw accelerometer waveforms in the historical
  run → tutorial-specific spectral features and from-scratch temporal model →
  v2 run-target predictions, followed by feature-subset ablations.
- **Implementation/configuration:** [tutorial source and frozen artifacts](../tutorials/patchtst_freq_baseline),
  `reader.py`, `features.py`, `build_features.py`, `model.py`, `train.py`,
  `analysis/ablation.py`; [report](../tutorials/patchtst_freq_baseline/REPORT.md).
- **Evaluation/result:** REPORTED all-72-feature fixed-split MAE 1.2203 versus
  v2 training mean 0.6797; selected subsets improved on that full representation
  without establishing a constant-baseline win.
- **Limitation:** separate source, target version and selection history from
  principal v3 LOEO. The tutorial's comparison with old 1.011 inherits that
  baseline's unresolved identity. Later subset/test inspection limits an
  untouched-test interpretation. Historical claims of duplicate raw content
  are not newly verified by this documentation check.

### Sorted tooth-profile heads and representation diagnostics — §5.8; E023, E031

- **Motivation:** test whether predicting richer tooth distributions provides a
  useful intermediate supervision structure.
- **Input → middle → output:** sensor sequence and **sorted** per-run tooth
  values → [`SortedProfileHead` and `profile_loss`](../../src/phm2026/models/patchtst/model.py),
  with [profile attachment](../../src/phm2026/preprocessing/timeseries.py) →
  ordered statistics whose top three can be reduced to a scalar.
- **Evaluation/evidence:** [profile diagnostics](PROFILE_DIAGNOSTICS.json),
  [v3 diagnostics](PROFILE_DIAGNOSTICS_V3.json),
  [tooth-profile analysis](../../scripts/targets/analyze_tooth_profiles.py).
- **Supported finding:** the target ledger establishes that the mean training
  profile's top-three scalar equals the scalar training mean by linearity;
  these are not competing run-level baselines. Profile coordinates do not
  preserve physical tooth identity.
- **Limitation:** exact fitted-source/checkpoint lineage of every exploratory
  profile variant is incomplete. Repeated-photograph SD near 0.796 pp is a
  REPORTED variability diagnostic, **not** a demonstrated irreducible run-MAE
  floor; avoid the ledger's stronger “inside label noise” interpretation.

### Monotonic rescoring and null calibration — §5.8

- **Motivation:** examine whether the challenge-style monotonic scoring changes
  conclusions without confusing fitted score transformations with prediction.
- **Input → middle → output:** existing predictions and targets → monotonic
  transformation/scoring and noise/permutation controls → alternative scores
  and null comparisons.
- **Implementation/configuration:** [monotonic implementation](../../src/phm2026/evaluation/monotonic.py),
  [rescoring](../../scripts/results/rescore_monotonic.py),
  [null test](../../scripts/results/monotonic_null_test.py),
  [configuration](../../configs/experiments/phm2026_monotonic_rescoring.yaml).
- **Execution/result:**
  [`20260912T053108724500Z-c0b86e16`](../../results/runs/phm2026_monotonic_rescoring/20260912T053108724500Z-c0b86e16);
  [initial study](TARGET_AND_FUSION_INITIAL_STUDY.md) reports noise beating the
  constant ≈87% and matching/beating PatchTST ≈48% under this small-sample
  rescoring, undermining the apparent ranking reversal.
- **Limitation:** the transform uses the same eight assessment points; these
  alternative scores are not independent predictive improvement. Retain raw
  MAE and target-version distinctions. No new null simulation was run here.

### Teacher identity, rank oracle and odd/even checks — §5.8

- **Motivation:** determine whether visual predictions contain useful additional
  structure before attempting sensor distillation.
- **Input → middle → output:** retained teacher predictions and tooth targets →
  within-run correlations, disjoint odd/even tooth summaries and a rank-mapped
  diagnostic oracle → estimates of teacher signal and a conditional build gate.
- **Implementation/evidence:** [`analyze_teacher_identity.py`](../../scripts/results/analyze_teacher_identity.py),
  [`closing_tasks_a_b.py` (`task_a`, `task_b`)](../../scripts/results/closing_tasks_a_b.py),
  [closing report](CLOSING_EXPERIMENTS.md), [v3 diagnostics](PROFILE_DIAGNOSTICS_V3.json).
- **Result:** REPORTED moderate within-run relationships (approximately
  0.37/0.44) and a five-run EXP-A oracle MAE 0.5724 versus 0.7430 illustrate
  conditional signal, not a deployable sensor improvement. The conditional
  later real-data distillation build was not established as executed.
- **Limitation:** no teacher predictions for EXP-B, no verified absolute tooth
  registration/keyphasor and photo-dependent oracle input. Sorted profile shape
  can create near-tautological agreement. Odd/even splits do not separate
  run-level lighting from true damage or validate physical labels.

### Synthetic pipeline and distillation controls — §5.8

- **Motivation:** test pipeline sensitivity under constructed signal, separately
  from any inference about naturally occurring PHM damage information.
- **Input → middle → output:** deliberately generated feature/target relations →
  calibration, sparsity and distillation-control sweeps → synthetic errors and
  gate diagnostics.
- **Implementation/evidence:** [`closing_task_c.py`](../../scripts/results/closing_task_c.py),
  [`closing_task_c3_retest.py`](../../scripts/results/closing_task_c3_retest.py),
  [synthetic summary](CLOSING_TASK_C_SYNTHETIC.json),
  [calibration retest](CLOSING_C3_RETEST_calibration_per_minute.json),
  [grid retest](CLOSING_C3_RETEST_grid_per_minute.json),
  [extension](CLOSING_C3_RETEST_grid_extension.json).
- **Result/limitation:** the [closing report](CLOSING_EXPERIMENTS.md) preserves
  failed stated predictions and the distinction between calibration and
  distillation mechanisms. Every number here is **SYNTHETIC**. Positive controls
  do not establish absence of natural sensor signal; aggregate-only records
  do not establish complete fit/checkpoint lineage. They are supporting
  diagnostics, not a PHM model leaderboard.

### Blind visual inspection, photometrics and DINOv2 alternatives — §§5.6.3–5.6.4, 5.8

- **Motivation:** challenge the heuristic's visual plausibility and investigate
  a possible learned replacement before claiming trustworthy labels.
- **Input → middle → output:** seven highest and seven lowest proxy images per
  experiment (42 total) → blinded calls, uncertainty exclusions and photometric
  diagnostics; separate DINOv2 baseline-to-query patch matching → agreement
  statistics and alternative change scores.
- **Implementation/evidence:** [prepare](../../scripts/targets/prepare_blind_inspection.py),
  [ingest](../../scripts/targets/ingest_blind_inspection.py),
  [score](../../scripts/targets/score_blind_inspection.py),
  [photometrics](../../scripts/results/analyze_photometrics.py),
  [DINO validation](../../scripts/results/anomalydino_validated.py),
  [sweep](../../scripts/results/anomalydino_sweep.py),
  [blind report](BLIND_INSPECTION_RESULTS.md),
  [DINO report](DINOV2_CHANGE_DETECTION_COMPARISON.md).
- **Result:** REPORTED heuristic agreement 30/38 (78.9%) with four unsure
  exclusions; best of 20 DINO configurations 29/38 (76.3%). No tested replacement
  demonstrated an improvement. Photometric checks did not support the specific
  hypothesis explaining the disputed-run clustering.
- **Limitation:** selected extremes, one reviewer, unsampled middle and repeated
  selection on the same small set. The one-image difference does not establish
  method superiority/equivalence or calibration to physical area. Calling a
  proxy-ranked “high” image “actually damaged” would confuse selection with
  ground truth. Do not generalize the reports' stronger claims about all
  foundation models or all possible label improvements.

### Raw-vibration and tooth-sector feature screens; stopped follow-ups — §5.8

- **Motivation:** check whether raw angular-domain mechanics or localized
  tooth-sector aggregation recover associations missed by summary features.
- **Input → middle → output:** historically sampled raw acceleration/encoder
  signals → angular resampling at 4,096 points/revolution, TSA/residual and
  physics indicators; later 28-sector upper-order-statistic summaries → feature
  screens against the photographic run proxy.
- **Implementation/evidence:** [`angular_features.py`](../../scripts/rawvib/angular_features.py),
  [`l1_screen.py`](../../scripts/rawvib/l1_screen.py),
  [`save_tsa.py`](../../scripts/rawvib/save_tsa.py),
  [`sector_features.py`](../../scripts/rawvib/sector_features.py),
  [`sector_screen.py`](../../scripts/rawvib/sector_screen.py),
  [raw-vibration report](RAW_VIBRATION_FEATURE_SCREENING.md),
  [sector report](TOOTH_SECTOR_FEATURE_SCREENING.md).
- **Evaluation/result:** REPORTED 577 queued/551 readable/472 steady files;
  L1 compares counts exceeding absolute correlation 0.5 with a 300-permutation
  null (seed 20260912). EXP-F p≈0.223 for both revolution-averaged and sector
  screens; the reported correctly signed cross-experiment survivors number
  zero. L2 rank and L3 level follow-ups stopped at the failed gate.
- **Limitation:** this bounded screen is not exhaustive raw-data coverage and
  does not prove physical damage information absent. Circular TSA agreement
  ≈0.997 is a reported transform check, not absolute physical tooth identity.
  Tiny `l1_screen.json` and `sector_screen.json` evidence needs explicit
  publication inclusion; large waveforms/features/checkpoints do not.

### Conditional or unlocated approaches and transition to later studies — §§5.9–5.10

- **Motivation:** preserve the difference between an implemented possibility,
  completed evidence and a future research proposal.
- **Input → middle → output:** [RT-DETR feasibility configuration](../../configs/experiments/phm2026_rtdetr_feasibility.yaml)
  and associated study plans describe conditional architecture checks; no
  corresponding completed run was established in this assessment. The proposed
  real-data distillation stage likewise has no verified completed fit here.
- **Result/limitation:** label-validation and evaluation constraints, sensor
  baseline comparisons and stopped screens support seeking datasets with
  explicit outcome annotations and paired usable modalities. They do not
  constitute deliberately designed negative controls or proof that one model
  family cannot work. [REASSEMBLE's recorded study rationale](../../../REASSEMBLE/results/artifacts/reports/FINAL_REASSEMBLE_HANDOFF.md)
  is the evidence for the subsequent design choice; it remains a different
  completed-action classification task.

## Principal saved-result verification and uncertainty

The independent check uses
[`verify_thesis_saved_evidence.py`](verify_thesis_saved_evidence.py). It imports
NumPy and standard-library helpers only, not experiment modules. It reads the
named small prediction/target/config/provenance artifacts and selected source
files, checks unique run keys, reconstructs v3 top-three targets, validates
training-mean constants against fold training experiments, and recomputes MAE,
RMSE and the historical 10,000-draw bootstrap with seed 20260814. It also checks
the recorded Git trees and selected published browsing objects. It does not
recompute Spearman correlation, rerun target masks, inspect checkpoints or
reproduce model fitting.

Executed command, from repository root:

```bash
ma_thesis_env/bin/python -B implementations/PHM2026/docs/studies/verify_thesis_saved_evidence.py --output implementations/PHM2026/docs/studies/THESIS_SAVED_EVIDENCE_VERIFICATION_20261126.json
```

The output is created exclusively and cannot overwrite an existing receipt.
For a read-only recalculation use the same command without `--output`; the
current environment must already contain NumPy. The receipt records Python,
NumPy, UTC check time, HEAD, SHA-256/size of every checked file and scope.

| Held-out experiment | Train | Validation | Assessment runs |
|---|---|---|---:|
| EXP-A | EXP-F | EXP-B | 5 |
| EXP-B | EXP-F | EXP-A | 7 |
| EXP-F | EXP-B | EXP-A | 8 |

| Model | Runs | MAE | RMSE | 95% run-bootstrap MAE interval | Eligibility |
|---|---:|---:|---:|---|---|
| Training mean | 20 | 0.804156266 | 0.960808478 | [0.576867095, 1.036024250] | Principal LOEO comparator |
| Three-group embedding fusion | 20 | 0.823785650 | 1.033217414 | [0.552711731, 1.101494938] | Principal LOEO |
| Single-encoder PatchTST | 20 | 0.941455086 | 1.133743116 | [0.675433166, 1.226432755] | Principal LOEO |
| Reused R4 image model | 13 | 1.826411277 | 1.959511750 | [1.458354925, 2.220911840] | **Not LOEO; different cohort; reference only** |

All errors are percentage points of the v3 proxy, pooled over runs. Absolute
errors are computed per run, not pooled over teeth/minutes. Fusion's **observed**
MAE difference from the mean is **+0.019629384**; the stored
`mean_delta_vs_constant` is instead the Monte Carlo bootstrap mean
**+0.017667654**, with interval **[−0.196189430,+0.227768727]**. The single
encoder's observed difference is **+0.137298820** and bootstrap mean
**+0.135837533**, with interval **[−0.085422614,+0.355913311]**. These distinct
statistics must not be silently interchanged. Replay matches the historical
summary within `1e-12`; numerical agreement does not validate its uncertainty
design or recover missing training evidence.

Run resampling preserves prediction pairing but does not turn the 20 runs into
20 independent experiments. It conditions on three experimental trajectories,
the retained fitted models and the chosen target. No training randomness,
hyperparameter selection, target-design uncertainty or new independent dataset
is included. Historical test exposure and possible shared/duplicated source
measurements remain limitations. Intervals containing zero establish neither
equivalence nor absence of a potentially useful sensor signal.

## Critical source-lineage and reproducibility gaps

| Investigation | Recorded revision | Checked content and later containing revision | Interpretation |
|---|---|---|---|
| v3 targets | `246024367e8b8a0b2463274115d760fb579ef50c`; dirty=false, untracked=true | Historical implementation was under `src/pi_multimodal_ad/targets/image_damage.py`; current browsing source and target tables have separate hashes. | Target-table identity and aggregation verified; no raw-image regeneration performed. |
| Fixed fusion | `8c4ae3111c83d8f263c44496bb64a0b04c0fae60`; dirty=false, untracked=true | This tree contains neither `train_late_fusion.py` nor `fusion/late_fusion.py`. Later source-containing revision: `2425b22db553ab464a48c349caa77398aa78850f`. | Exact untracked source at execution UNKNOWN. The later commit is not asserted to be the executed implementation. |
| Principal LOEO | `c699cbd9727ed33f34f1785172db163eb74b071f`; dirty=false, untracked=true | This tree contains no `loeo_evaluation.py`. Later source-containing revision: `a2172ae2b286aad5245239b35b98b6526d501c4e`. | Saved predictions can be verified independently; precise producing entry-point bytes remain unresolved. |
| R3/R4 and early target records | Historical `d3ce4808…` records include dirty-tree state. | Reports identify architectures, commands and selected checkpoint/output hashes; no new checkpoint loading/hash sweep was performed. | Do not label a bare recorded commit a complete reproduction snapshot. |
| Four-arm alternatives / supplementary diagnostics | Study-local scripts and result reports; complete immutable execution snapshots not established here. | Current source inspection supports the stated implementation concern. | Retain REPORTED execution/results and explicit provenance limits; do not conflate these with principal LOEO. |

The principal resolved configuration retains `target.definition_version: v2`
while pinning the v3 source run/hash; saved truth values resolve the actual
comparison to v3. Existing result/configuration bytes remain untouched. The
scope of any future scientific correction must be separately reviewed, retain
original runs, and use new identities. Compiling a manuscript or navigating
these links does not repair an experiment or reproduce training.

## Proposed Chapter 5 implementation footnotes

These are prepared text and verified browsing resources, **not inserted into
Chapter 5**. Preserve existing Appendix F IDs and add only genuinely missing
resources through that same register. Each public URL below uses the verified
published browsing commit, **not a claim of exact historical execution**. The
consolidation's publication manifest records small targets/predictions awaiting
publication. Their final GitHub links must wait for an actual authorized commit.

| Proposed placement | Prepared footnote text and resources |
|---|---|
| §5.5 / §5.6.2, target definition | **Implementation: PHM photographic condition-proxy construction —** [candidate-area source, E035](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/src/phm2026/targets/image_damage.py#L114-L194) · [v3 configuration, E125](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/results/runs/phm2026_image_target/20260912T052857044116Z-c936a4e3/config/resolved_config.yaml). Generated tooth/run targets (E130/E129) and this independent aggregation check (E132): publication pending. |
| §5.6, visual diagnostic boundary | **Implementation: RT-DETR-derived scalar regression —** [feature extraction, E033](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/src/phm2026/models/rtdetr/regression.py#L73-L160) · [retained input-selection defect, E024](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/experiments/walkthrough/01_rtdetr_scalar_regression/KNOWN_IMPLEMENTATION_ISSUES.md). See the retained run for configuration and predictions; physical labels remain provisional. |
| §5.7.1–5.7.2, sensor representation | **Implementation: sensor sequence regression —** [PatchTST patching/encoding/head, E031](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/src/phm2026/models/patchtst/model.py#L176-L267) · [feature-group configuration](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/configs/experiments/phm2026_fusion_latefusion.yaml). The configuration's v2 text is stale; pinned data and saved targets are v3. |
| §5.7.2, fusion architecture | **Implementation: three-group sensor feature fusion —** [encoder routing and embedding concatenation, E124](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/src/phm2026/fusion/late_fusion.py#L58-L119) · [configuration](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/configs/experiments/phm2026_fusion_latefusion.yaml). Published browsing source; exact untracked execution source remains unresolved. |
| §5.7.3–5.7.4, principal evaluation | **Implementation and evidence: principal PHM LOEO comparison —** [fold-local preprocessing and assessment, E028](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/scripts/results/loeo_evaluation.py#L227-L258) · [saved summary, E128](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/results/runs/phm2026_loeo_evaluation/20260912T110848985882Z-e1911d4f/reports/loeo_summary.json). E026 summary CSV, per-run predictions (E127) and independent score-verification receipt (E132): publication pending. |
| §5.8, separate alternatives | **Implementation: supplementary scalar and process-conditioned fusion —** [evaluation setup, E029](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/scripts/results/sq2_sq3_fusion.py#L179-L225) · [saved results](https://github.com/Parth-0804/pi-multimodal-ad/blob/e2037412036c5bbfc01fb2323215a37ef0b2e090/implementations/PHM2026/docs/studies/SQ2_SQ3_RESULTS.json). Separate protocol with preprocessing-isolation concerns; not the principal fusion row. |

Before insertion, keep prose concise and move qualifications already explained
in the chapter to the relevant main-text limitation. Evidence footnotes should
preserve descriptive roles and source pinpoints, not just display filenames.
Neither adding new Appendix F resources nor enhancing macros should activate
previously suppressed Chapter 1–4 footnotes without a separate layout review.

## Publication and handoff

Include this guide, its read-only verification script and receipt after content
review. Narrow publication candidates are the principal LOEO prediction/summary
CSVs, v3 tooth/run target CSVs and small raw-vibration/sector screen summaries;
these are derived evidence, not raw waveforms or source images. Keep raw
datasets, bulk features, model weights, external copyrighted publications and
temporary build products excluded. A small file still requires a rights and
confidentiality check; existence or a content hash does not grant redistribution.

Use [raw-data recovery documentation](../RAW_DATA_RECOVERY.md) for the historical
source identity and retention boundary. Old commands and endpoints may require
path/access reconciliation; no raw recovery, download or restoration is
authorized by this guide. Existing raw-retirement records are narrow historical
exceptions, not reusable permission. The next scientific writing task is to
review Chapter 5 against this map, then insert the agreed investigation-boundary
footnotes; no new fitting is necessary to describe the retained evidence honestly.
