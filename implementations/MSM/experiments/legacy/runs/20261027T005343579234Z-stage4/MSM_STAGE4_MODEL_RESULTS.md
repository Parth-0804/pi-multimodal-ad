# MSM Stage 4 model results

**Status: BLOCKED_COHORT_AND_SOURCE. No held-out model result is available.** The authorized Stage 4 execution validated the existing artifacts and stopped at scientific admission checks. It did not run a replacement design, promote Stage 3 smoke scores, or manufacture predictions/checkpoints/training curves. The user's Stage 4 instruction supplies execution authorization; the historical Stage 3 `full_matrix_authorized=false` flag is not the blocker.

Dataset **`manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`**, Kaggle ID 8392825; [official dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), [publication](https://www.nature.com/articles/s41597-026-07255-7). Run `MILLING DATASET/runs/20261027T005343579234Z-stage4`, recorded UTC **2026-10-27T00:56:02.004172+00:00**. This report is a measured dependency audit, not a completed independent evaluation.

## Preconditions checked before fitting

1. **Stage 1–3 integrity passed.** Rechecked 176 unique recorded artifact/source identities: 41 Stage 1, 100 Stage 2, 35 Stage 3. All **104 local MSM raw source files** (69 labels and 35 previously acquired pilot modalities/metadata) matched their recorded SHA-256. No source files, prior output, raw data, Phase 1 active fit or credentials were changed/read beyond the authorized dataset/checkpoint evidence. Shared early-stage navigation/ignore hashes were excluded where they had intentionally evolved; current Stage 3 identities matched.
2. **Input construction reconfirmed.** All 114 admitted annotation/frame-selection policies revalidated. Rebuilt all 114 × 90 actual MTC statistics with maximum absolute difference **0.0** versus the recorded Stage 2 features. Native interval membership and all source/target associations remain traceable. No new video decode, feature extraction, fitting or model scoring was needed for this audit.
3. **Frozen split failed.** 114 intervals in five experiment folders, but only two folders contain native label 1. The frozen three-outer/two-inner experiment-disjoint design requires both classes in each fitting and assessment partition. Its implementation raises `Insufficient positive/negative experiment groups for requested folds`. No seed search, fold reduction, interval shuffle, within-experiment split or test-driven cohort replacement was used.
4. **Source dependency failed.** Phase 1 had **0 completed C/full-backbone fits** at snapshot. One completed B/frozen-head fit is not an R source; an active C checkpoint has no completion receipt. Source-domain numerical preflight passed, but its diagnostic weights are not a completed training-selected source model. Details: `MSM_CNN_WEIGHT_TRANSFER.md`.

## Actual counts and metrics availability

Native classes: **93 label 0 / 10 label 1 / 11 label 2**. For the frozen cutting-abnormality target, label 1 is positive and labels 0/2 are stable-cutting negatives: **104 negative / 10 positive**, cohort prevalence **10/114 = 0.0877192982**. This is observed cohort prevalence, not an outer-test metric. Label 2 means a defective tool during stable cutting, not automatically abnormal cutting.

| Initialization | Visual-only | Matched sensor-only | Static F2 |
| --- | --- | --- | --- |
| P: original pretrained CNN | Not run: cohort gate | Not run: cohort gate | Not run: cohort/OOF gate |
| R: completed full-backbone REASSEMBLE CNN | Not run: cohort + source gates | Not run: cohort gate; same matched sensor contract | Not run: cohort + source/OOF gates |

**AP, AUROC, held-out prevalence, Brier/log loss, per-fold/per-seed scores, paired effects and uncertainty intervals are unavailable.** Missing values in tables are blank/NA, never zero scores. No model is declared superior or inferior; no best fold or seed was selected. Interval-resampled confidence intervals cannot repair absent independent positive groups.

The predeclared label-2-exclusion sensitivity also fails: **103 intervals / four folders / two positive folders**, still ten positive intervals. It cannot rescue the evaluation and was not selected after inspecting performance.

## Frozen controlled comparison retained

Both conditions would use the same eligible intervals, original source-frame indices/PTS, aspect-preserving 640×640 preprocessing, 16-frame mean pooling, exact group partitions, 896→128→1 newly initialized MSM head, training-only standardization, weighted BCE, AdamW LR 0.001/decay 0.001, batch 32, clipping 1, ten fixed epochs, threshold 0.5, and all three MSM seeds **42, 123, 20261023**. Both CNNs remain **frozen/eval** per Stage 3. Full-backbone *source* training does not authorize changing MSM freezing rules for only R.

The sensor model remains the identical 90-feature balanced logistic C=1. Separately fit P-F2 and R-F2, each unweighted logistic C=1 over its own `[p_visual,p_sensor]` probabilities from strictly group-held-out inner fits. No source-domain head, scaler, calibrator or F2 coefficient transfers. Source R's canonical role was fixed without MSM results. No calibration or threshold search is added to the frozen protocol.

If dependencies eventually pass, the primary P/R comparison implies **54 visual-head fits** (27 per initialization), 18 F2 fits and nine unique deterministic sensor partitions that can be shared across conditions/seeds. This is a planned count, not completed work. A new matched eligibility/split manifest and validated resumable execution path would be needed before long fitting; Stage 3's inference/development checkpoint is not a resumable full-matrix artifact. No arbitrary GPU-hour cutoff caused this stop.

## Artifacts delivered

| Artifact | Actual content |
| --- | --- |
| `manifests/planned_results_status.csv` | All 54 requested initialization × seed × outer-fold × model result slots marked blocked, blank metrics |
| `manifests/predictions.csv` | Explicit prediction schema, **zero data rows**; no invented scores |
| `manifests/paired_differences_status.csv` | All requested P/R and fusion-vs-branch AP/AUROC comparisons per seed marked unavailable, blank intervals |
| `manifests/selected_checkpoints.json` | Empty selection with gate reasons; Stage 3 development checkpoint not promoted |
| `manifests/training_curves.csv` | Schema, **zero data rows**; no MSM Stage 4 training occurred |
| `figures/cohort_class_coverage.png` | Actual five-experiment native-label coverage plot; **not** a learning curve |
| `config/resolved_config.json` | Stage 4 authorization, matching rules and source selection |
| `config/stage3_protocol.original.json` | Exact preserved frozen scientific configuration bytes |
| `provenance.json`, `validation.json`, manifests | Runtime, CPU/GPU observation, versions, SHA-256, commands and tests |

There are no selected MSM Stage 4 checkpoints or trained-model curves to provide. Existing Stage 3 smoke checkpoints and source Phase 1 curves remain historical evidence, not substitutes for missing requested deliverables. Bulk media/checkpoints remain Git-ignored.

## Costs and validation

Stage 4 measured audit body: **2.991 s wall / 2.950 s CPU**, excluding interpreter/import startup. CPU resident memory at completion about **929.1 MiB**. The provenance key `audit_peak_RSS_bytes` records an end-of-body RSS observation, not a sampled peak; do not interpret it as peak memory. Original and diagnostic CNN states were inspected on CPU. **No CUDA context was created**, no MSM training GPU time accrued, and no MSM forward/inference/training throughput was measured in Stage 4.

The visible T4 had another Phase 1 process using about **9,264 MiB** and device-wide **100%** utilization. That is its workload, not MSM utilization. It continued untouched. Prior Stage 3 throughput/smoke costs remain in its own report and are not charged as Stage 4 training or independent accuracy evidence.

**61 synthetic/regression tests passed in 8.25 s**, including 15 new CNN transfer/source-consistency cases. `pip check` and `git diff --check` passed. Prior tracked Git diff remains three pre-existing files / 22 insertions. New files are confined to `MILLING DATASET/`; nothing staged/committed and no environment packages installed.

## Answers to the eight research questions

1. **Does the architecture work on MSM?** Its aligned interval construction and bounded forward/gradient/checkpoint pipeline work on the filtered subset. Predictive adaptation success under independent evaluation is **not established**.
2. **Does F2 improve over unimodal components?** **Unknown**; no held-out F2 or matched branch scores exist.
3. **Does REASSEMBLE initialization help or hurt?** **Unknown**; there is no admissible completed R checkpoint and no matched MSM evaluation.
4. **Stable across seeds?** **Unknown**; the three-seed evaluation was not run. A single Stage 3 development seed does not establish stability.
5. **Evidence of overfitting?** **Not assessed for MSM.** No Stage 4 learning/test curves exist; architecture size, the source-domain learning curve or a tiny smoke loss cannot establish MSM overfitting.
6. **Computational cost?** Audit cost above; **zero Stage 4 MSM model fits, optimizer steps, predictions and training GPU seconds**. Full evaluation cost is unmeasured.
7. **Cross-domain representation claim?** **Unsupported.** Tensor compatibility is software evidence, not demonstrated transfer benefit or causal representation generality.
8. **Exploratory/inconclusive findings?** Coarse visual context and MTC feature construction are validated engineering findings. Transfer efficacy, fusion gain, independent generalization, seed stability and calibration remain **inconclusive**. Corrupted/missing-modality robustness was not evaluated and is not claimed.

**Stop after this Stage 4 dependency-limited execution.** Prerequisites for a future evaluation: expand and independently audit positive laboratory experiments, resolve physical grouping, freeze a valid three-outer/two-inner assignment, obtain the completed canonical Phase 1 C checkpoint and validate the resumable matched runner. The present output does not claim completion of the experimental matrix.
