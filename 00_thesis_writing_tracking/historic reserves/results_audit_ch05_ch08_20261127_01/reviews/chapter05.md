# Chapter 5 saved-results and supporting-file audit

Audit date: 2026-11-27. Scope: current canonical Chapter 5, its PHM supplementary passages in Appendix D, and the named source, configuration, report and compact saved-result dependencies. No manuscript, source, configuration, historical result, raw data or model file was changed. No training, fitting, inference, image processing or experiment rerun was performed.

**Outcome:** no numerical contradiction was found in the Chapter 5 results checked. The principal LOEO table, its paired interval, target-version constants and visual regression scores agree with the inspected saved evidence at the manuscript's precision. The main remaining issues concern historical protocol/source provenance and the strength of reproducibility wording, rather than replacement scores.

The current [chapter source](../../Thesis/LaTeX_Project/chapters/05_phm.tex) is byte-identical to `before/chapters/05_phm.tex`: SHA-256 `18c502b1dff720b651fcc3c2565c334cfd8c312d734292ee64c84b6c10cca286`. All chapter line anchors below refer to those bytes. The [support inventory](chapter05_support.json) lists exact repository-relative files, their claim roles, priorities and inspection status. It is a review list, not a publication manifest or authorization to upload.

## Findings and support limits

1. **Historical protocol discrepancy, not a manuscript metric error.** The fixed-fusion plan `implementations/PHM2026/docs/studies/SENSOR_LATE_FUSION_PREREGISTRATION.md`, §3, specifies seed **20260912**. Its executed run's `config/resolved_config.yaml` and `provenance.json` record **20260814**. Chapter 5:281–287 accurately reports the result and declared 0.15-point criterion, and does not claim the seed or complete protocol compliance. A later supporting link should nevertheless disclose this discrepancy instead of describing every aspect of that run as matching its plan. This audit did not establish an amendment explaining the changed seed.

2. **Prior assessment exposure deserves an explicit sentence near the principal protocol/limitations.** Chapter 5:263–278 and 315–330 preserve experiment grouping, source gaps and conditional uncertainty, but do not expressly say that EXP-F had already informed development before the September fusion/LOEO studies. The fixed-fusion plan's §4 explicitly discusses an earlier EXP-F isotonic/null analysis; the target/fusion study and traceability guide also retain that history. “One evaluation” describes the selected fixed-fusion model's assessment, not the complete history of those runs. The present chapter does not assert a pristine test population, but an explicit boundary would prevent that inference. The historical feature-subset caveat at 335–341 does not fully cover this earlier target/evaluation-design exposure.

3. **Reproducibility wording is stronger than this audit establishes.** Chapter 5:202–204 says the retained visual work establishes “reproducible implementation.” Source availability, saved metrics, and the calculations below establish inspectability and saved-output arithmetic. They do not reproduce fitting or recover the complete dirty-tree source for the August visual runs. Prefer a bounded description in a later authorized writing pass, or attach a specifically executed reproduction record. No training reproduction was attempted here.

4. **Fixed-fusion uncertainty remains REPORTED.** Chapter 5:284–285 matches `TARGET_AND_FUSION_INITIAL_STUDY.md`'s interval `[-0.548,+0.414]`. The selected fixed-fusion run contains its summary JSON, validation comparison, configuration, provenance and output manifest; no per-run test-prediction table was located there. The summary gives the model MAE but not the bootstrap replicates/interval. The interval was therefore checked against the historical report, not independently recalculated. This is an evidence limitation, not evidence that the interval is wrong.

5. **The chapter correctly preserves consequential limitations already present in the records.** These include photographic proxy validity; sensor-only inference in the principal experiment; v2 visual versus v3 sensor targets; image/tooth/run units; fixed split versus LOEO; the R3 latency covariate; E027's misnamed run; exact untracked source gaps; run versus experiment independence; four-arm preprocessing exposure; and the difference between absent improvement and absent sensor information. These qualifiers should remain beside any GitHub links.

No missing software dependency blocked the bounded calculations. Checks not performed below were outside the declared audit method or lacked the named execution/input record; they were not silently counted as passed.

## Evidence classifications used here

- **VERIFIED—recomputed:** arithmetic independently evaluated from the specifically identified saved rows in this pass. This does not validate their original acquisition, labels or fitting.
- **VERIFIED—source correspondence:** the current implementation/configuration or saved aggregate contains the stated fact. Current source alone is not proof of the historical executed path.
- **REPORTED:** a historical report or prior audit states the result, with the underlying computation not repeated here.
- **INFERRED/UNKNOWN:** interpretation or a missing identity is stated explicitly. Absence of an independent damage reference in the reviewed evidence is not a claim to have exhaustively searched every possible external source.

The repository `AGENTS.md`, `REPO_MAP.md`, `README.md`, `docs/data_boundaries.md`, `docs/output_policy.md`, the thesis `AGENTS.md`, PHM guide, walkthrough and investigation traceability were consulted. Protected raw archives/images/waveforms and the historical initial EDA outputs were not scanned or modified. Git/remote/publication status is owned by the parent audit and is not newly certified here.

## Section-by-section claim coverage

### 5.1 Study objective — lines 3–22

The principal result's negative comparison is **VERIFIED—recomputed** from all 20 saved run keys per principal model. Sensor-only inference and context/RMS/condition-indicator embedding fusion are **VERIFIED—source correspondence** in `src/phm2026/fusion/late_fusion.py` and the pinned fusion configuration. Photographs provide the target rather than an inference branch in that path. The claim that a nearly constant prediction can be insensitive to corruption is methodological reasoning, not a separately measured PHM robustness result here. Physical-damage validity remains unestablished; the chapter does not equate proxy prediction with physical damage measurement.

### 5.2 Dataset and supervision — lines 24–58

| Current lines | Claim | Audit outcome and boundary |
|---|---|---|
| 25–31 | A1–5, B1–7, F1–8; 20 nominal runs; distinct observational units | **VERIFIED—source correspondence/recomputed counts.** Dataset configuration and saved run targets identify 5/7/8 runs and 20 unique experiment/run keys. No raw acquisition census performed. |
| 33–40 | Run-level association rather than proven hardware synchronization | Consistent with inspected target/feature identity fields and the existing source map. The chapter correctly declares incomplete raw reinspection. |
| 43–48 | Tooth/view confounding and v3 exclusion of teeth 1–4 | Current target source/configuration explicitly documents the confound and exclusion; 480 saved v3 tooth rows contain exactly teeth 5–28 for every run. Underlying image-role acquisition was not independently re-viewed. |
| 50–58 | Organizer-reported Run-2 overlap and reported 372×72 derived equality | Dataset configuration marks the organizer warning as unverified. The HF tutorial reports 372 equal derived rows across 72 features. **REPORTED**, not independently re-compared feature arrays or byte-identical archives. The chapter's rejection of the report's stronger raw-duplication conclusion is appropriate. |

### 5.3 Preparation and target lineage — lines 60–106

Historical EXP-A 1/3/5 exploration at 64–67 is a provenance statement supported by navigation/history, not a new EDA reproduction. Current feature source retains archive/member, experiment/run and measurement identities; no raw payload was processed. The distinction between the principal minute features and separate HF spectral features is supported.

Table `tab:phm-target-lineage` at 85–97 agrees with retained v1/v2/v3 tooth CSV row counts: **560/560/480**. Their saved run CSVs each contain 20 rows. The median-28 “not materialized” row is **REPORTED** from the target ledger and its source history; no global missing-artifact proof was attempted.

Current `image_damage.py` confirms luminance/CLAHE/background subtraction, residual threshold, morphology, horizontal component filtering, deterministic canonical/earliest-view selection, exclusion and top-three aggregation. It does not independently validate the rule as physical damage. The ledger supports the approximate sixfold v1→v2 scale description and differing ROI/threshold; the audit's fixed training means are 0.748580 (v1), 4.947947 (v2) and 4.477895 (v3), illustrating the scale/version distinction rather than a universal sixfold factor per observation.

For v3, all 480 saved tooth measurements reproduce the 20 raw run targets, maximum absolute difference **8.88×10⁻¹⁶**. Every saved principal LOEO truth agrees with those targets. The target Parquet identity matches the pinned hash `e5e098e01822307791138b83c015307ae74a5b2fdaf80957e413170a343e92f1`. These are saved-table checks; the photographic measurement was not regenerated.

### 5.4 Visual target construction and assessment — lines 108–204

| Current lines | Claim | Audit outcome and boundary |
|---|---|---|
| 108–138 | Deterministic heuristic target, candidate ROI fraction, separate physical validity | **VERIFIED—source correspondence** for the measurement and aggregation. No expert mask/independent physical-area validation was established in the reviewed evidence. |
| 140–154 | RT-DETR-L prediction path; three intermediate maps; 768 image values plus latency | `extract_features` invokes `RTDETR.predict`, hooks selected layers, pools maps and writes `feature_latency_ms`; `train_head` includes every `feature_` column. Retained discrepancy record and training summary support 769 head inputs/98,689 parameters. Current-source and saved-record correspondence, not checkpoint reconstruction. The existing schematic was opened and its full-predict route, three pooled maps, latency input and proxy-output wording agree with these records. It was not edited or rebuilt. |
| 157–171 | Appearance assessments are not untouched physical-validation cohorts | Consistent with the blind report and DINO comparison's selected extremes and reuse. No re-adjudication of images or independent reviewer evaluation. |
| 174–178 | Fixed B→F constants .6797 v2 versus .7348 v3; profile/scalar distinction | **VERIFIED—recomputed** from the respective saved run targets. Sorted-profile top-three mean commutes with the training mean; this is not an explanation for the version-dependent difference. |
| 180–186 | R3/R4 image/run MAEs; detector TP0/FP0/FN9883 | Visual MAEs **VERIFIED—recomputed** below. Detector values **VERIFIED—source correspondence** in the `scope=all` aggregate at confidence .60/IoU .50 over 224 images. No box rematching or AP recomputation. |
| 188–193 | Blind 30/38 and best DINO 29/38 from 20 configurations, four exclusions | Blind report contains the count/exclusions and 42 selected extremes; arithmetic30/38 = 78.947% confirmed. Sweep CSV contains20 rows, highest hits 29/38 = 76.316%. Historical human calls/model scores were not regenerated; no superiority/equivalence conclusion follows. |
| 195–204 | Very small attainable recall, box-scale mismatch, reused visual row not LOEO | Compact detector sweep/geometry tables corroborate the report's descriptive observations. Unthresholded saved diagnostic row has145 matches/9,883 pseudo-boxes; this does not isolate the causal training failure. The 13-row reused visual comparison is explicitly `not_loeo` and lacks EXP-B. The chapter correctly avoids activation-energy localization overclaim. See reproducibility wording finding above. |

The four principal visual numbers were independently recalculated using the `split=test` rows, without clipping predictions or changing targets:

| Saved path relative to the visual run | Unit/count | Recomputed MAE | Chapter value |
|---|---:|---:|---:|
| R3 `tables/predictions.csv` | image/224 | 0.8938517043 | .8939 |
| R3 `tables/run_predictions.csv` | raw top-three run/8 | 1.3474477355 | 1.3474 |
| R4 `tables/scalar_predictions.csv` | image/224 | 0.7329897630 | .7330 |
| R4 `tables/run_predictions.csv` | raw top-three run/8 | 1.6272539000 | 1.6273 |

R3 is run `20260814T020338751021Z-d0f225c8`; R4 multitask is `20260814T050026535618Z-9b00f099`. The negligible difference between R3 CSV arithmetic and its stored full-precision metric (~1.6×10⁻⁹) is consistent with serialized prediction precision and does not affect the printed value. All are v2 visual diagnostics, not extra rows in the v3 sensor LOEO table.

### 5.5 Sensor prediction — lines 206–330

| Current lines | Claim | Audit outcome and boundary |
|---|---|---|
| 206–217 | Proxy prediction, sensor-only inference and multiple possible failure mechanisms | Supported by source/task definition; alternative explanations remain hypotheses rather than established causes. |
| 220–238 | Nine variables, seven summaries plus masks=72 columns; patch masks; E027 correction | Configuration and current feature/model source agree. Any-valid patch masks and masked pooling were inspected, but no historical batch/padding invariance was tested. E027's recorded command ends in `train_late_fusion.py`, confirming its directory name cannot identify a single-encoder run. |
| 240–260 | Ridge separate; custom PatchTST dimensions; sorted profile; feature-level fusion | Configured width 32, 2 layers, 4 heads, FF64, patch 16/stride 8 agree. Positive profile increments discard positional tooth identity. Separate encoder embeddings are concatenated; this is neither probability stacking nor image/sensor inference. Current four-arm numeric partition has empty M3. |
| 263–278 | Fixed B/A/F versus rotated train/validation/test experiments; local scaling; source/target metadata gaps | Saved LOEO summary and current runner agree on F/B/A, F/A/B, B/A/F. Normalization is inside each principal fold. Read-only verifier confirms recorded fixed-fusion and LOEO Git trees lack the named entry-point paths and have untracked-source indicators. Saved truths/pinned hash resolve v3 despite stale config string. Current-source inspection cannot restore exact historical entry-point bytes. |
| 281–287 | Fixed split .6548 versus .7348, improvement .0800 below .15, interval spans zero | Saved aggregate .654810578, constant .734766366, difference −.079955788 agree. Constant separately recomputed .734766399. Model error/interval retain the source levels described in findings1/4. |
| 289–305 | Principal 20-run table including Spearman and conditional run intervals | **VERIFIED—recomputed**, including Spearman not covered by the older verifier. Full results below. |
| 308–313 | Observed delta .0196 versus bootstrap mean .0177 and paired CI | **VERIFIED—recomputed** with paired run keys, 10,000 draws/seed 20260814. These are distinct statistics, correctly distinguished. |
| 315–330 | No established gain, not no sensor information; dependence and uncertainty limits | Supported bounded inference. Run resampling omits training/selection/target-design uncertainty and does not create 20 independent experiments. See explicit historical-exposure recommendation above. |

| Principal model | Unique runs | MAE | RMSE | Spearman | Recomputed 95% MAE interval |
|---|---:|---:|---:|---:|---|
| Training mean |20|0.804156266|0.960808478|−0.035399616|[0.576867095,1.036024250]|
| Single encoder |20|0.941455086|1.133743116|−0.205340368|[0.675433166,1.226432755]|
| Three-group fusion |20|0.823785650|1.033217414|−0.104550590|[0.552711731,1.101494938]|

All printed table entries match. Every training-mean prediction was checked against the mean target of its declared training experiment. Changing fold constants explains the constant's nonzero pooled Spearman; it does not give within-fold discrimination.

Paired fusion-minus-constant observed MAE difference: **+0.0196293842**. Bootstrap mean difference: **+0.0176676542**. Recomputed paired 95% interval: **[−0.196189430,+0.227768727]**. The saved JSON and replay agree within 1×10⁻¹². This interval includes improvements and deteriorations; it is not an equivalence result. The excluded visual row has 13 runs and MAE 1.826411277, consistent with its distinct assessment cohort and `NOT_loeo` label.

### 5.6 Supplementary diagnostics — lines 332–354 and Appendix D146–169

The HF/spectral model's eight stored test predictions give MAE **1.220283600** from their serialized decimals, matching 1.2203. The eight-row ablation table contains seven reduced-feature variants with MAEs 0.730390–0.996893, each below the full model and each above the independently checked v2 constant 0.679679861. This verifies the saved comparison, not the feature-selection procedure's independence. The chapter correctly identifies repeated test inspection and rejects the tutorial's stronger causal/whole-archive claims.

The four-arm script calls `fit_feature_normalizer(minute,...)` and assembles all sequences **before** rotated evaluation. The normalizer itself filters the original `split=train` rows; consequently the original EXP-B training measurements can enter preprocessing when EXP-B is later held out. This confirms the current-source leakage concern without attributing it to the separately inspected principal fold-local runner.

Appendix D:160–169's three-seed aggregate MAEs recalculate exactly from the stored `per_seed` values: modular scalar fusion **0.8288127025**, gated **0.9073629419**, concatenation **0.9642878691**. The saved constant is 0.8041563034. These checks do not reconstruct per-run four-arm fits or remove the preprocessing problem.

Appendix D:148–156's Ridge values independently recalculate from eight test prediction rows: raw-target MAE **5.0151004502**, causal-monotonic-target MAE **4.9356608005**. They remain a historical v2 fixed-split reference, not a fourth principal v3 LOEO model.

The other named raw-vibration/tooth-sector, teacher/oracle, odd/even, synthetic and monotonic diagnostics are maintained as separate investigations, with no new numeric result asserted by this chapter passage. Their detailed execution/metrics were not exhaustively re-audited here. The inventory marks uninspected optional report dependencies accordingly. No raw feature screen or model was rerun.

### 5.7 Synthesis — lines 356–388

The observed sensor-model ordering and unresolved paired interval follow the recomputed values. Proxy validity, prospective warning, RUL and natural-fault response remain open; they are not recast as failed model results. The cross-study report supports the interpretation boundary and change toward native-outcome paired data. Exact human decision chronology is historical/REPORTED, not independently reconstructed from execution artifacts. The chapter correctly avoids calling PHM a prespecified negative control or claiming a validated welding classifier.

## Checks performed and retained identities

The existing verifier was inspected before execution. Actual command:

```bash
ma_thesis_env/bin/python -B implementations/PHM2026/docs/studies/verify_thesis_saved_evidence.py
```

It completed successfully without `--output`, leaving historical receipts unchanged. It reads the named compact CSVs, target Parquet identity, configs/provenance and selected local source/Git objects; it imports NumPy and standard-library helpers, not model/experiment modules. Its output's `command` string is hardcoded to an earlier invocation with `--output`; the actual invocation above is authoritative for this pass.

Additional inline read-only Python used standard-library CSV/JSON, NumPy and `scipy.stats.spearmanr`. It evaluated MAE as `mean(abs(y_pred-y_true))`, RMSE as `sqrt(mean((y_pred-y_true)**2))`, Spearman with average ranks for ties, B-trained/F-tested target constants, visual test-row errors, Ridge raw/monotonic errors, the HF test prediction errors and arithmetic means of the three saved four-arm seed scores. No model package, checkpoint or source dataset payload was loaded. An initial Ridge check used an incorrect assumed column name and stopped with `KeyError`; after inspecting the header, the corrected calculation explicitly used `y_true_raw` and `y_true_monotonic`, producing the values above. No output was written by either calculation.

Selected checked prediction hashes:

| Artifact | SHA-256 |
|---|---|
| R3 image predictions | `2a43f8f136c600f509e8dc3a588d6991f236940e37ce185221f4abd7bf392b5d` |
| R3 run predictions | `a11601a14951bbef193cf2ab9960bf74618d62e3dbc9bcfcc39e0cfa65246adf` |
| R4 scalar predictions | `af4a0b6a8488886d25fab5c0b36e4e0dd97326dd6211fbd8b184ef0a74496a0e` |
| R4 run predictions | `51be59d16cf27da7ff5dcb96403fda6911f821b5bb71249650183469bfb40df5` |

Only this report and `chapter05_support.json` were created by this audit owner. The support list contains no raw image, waveform, checkpoint or full feature cache; its one manuscript PNG is an existing schematic. Per-example and tooth/run-derived evidence is explicitly marked for redistribution review. Some historical reports contain stronger claims than the manuscript adopts; linking one does not endorse every sentence in it. No final GitHub permalink, remote accessibility, publication permission or training-reproduction certification is supplied by this audit.
