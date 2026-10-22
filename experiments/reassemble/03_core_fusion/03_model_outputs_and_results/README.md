# 03 — Predictions, evaluation and results

**What the model predicts:** a probability of recorded action failure. `p` is the calibrated/fused failure probability; `hard` is the binary decision using that fold's selected threshold; `y` is the recorded outcome; `fold` identifies the outer held-out fold. Single-modality files also contain `raw` logits and `[4530,128]` learned embeddings. Arrays retain the frozen cohort order. The IDs are in the cohort table, not repeated in every NPZ file.

**The example sample (cohort row 3326):** saved failure probability **0.099589**, predicted failure **0**, recorded failure **1**, outer fold **4**. This is a lookup of a previously saved prediction, not fresh inference. One sample cannot validate aggregate performance.

| Metric over all 4,530 held-out predictions | Saved estimate | 95% recording-bootstrap interval |
|---|---:|---|
| AUROC | 0.7950 | 0.7727–0.8178 |
| AUPRC | 0.4473 | 0.3968–0.5019 |
| balanced_accuracy | 0.7117 | 0.6875–0.7343 |
| macro_F1 | 0.6340 | 0.6161–0.6527 |
| failure_recall | 0.6110 | 0.5603–0.6582 |
| failure_precision | 0.2920 | 0.2640–0.3225 |
| Brier | 0.0784 | 0.0713–0.0858 |
| ECE | 0.0138 | 0.0118–0.0251 |

`AUPRC` in these reports is implemented as average precision. AUROC/AP assess probability ranking; balanced accuracy, F1, recall and precision use the saved thresholded decisions. Brier score assesses probability error; ECE uses 15 bins. Intervals resample whole recordings (2,000 bootstrap replicates), accounting for samples sharing a recording.

**Interpretation:** Section 1B recorded FUSION GO under its separately declared admissibility protocol. F2 AP is 0.4473 versus 0.4294 for the sensor-statistics branch. This does not retroactively make the original unimodal gate pass, and it does not establish performance on new sites or external datasets.

| Open | What it contains |
|---|---|
| [Saved predictions](../../../../runs/reassemble/20260927T175336Z-section1b/stacking/oof.npz) | Binary NPZ arrays; 4,530 rows aligned to the cohort |
| [Full recorded results](../../../../runs/reassemble/20260927T175336Z-section1b/assessment/results.json) | Multiple models, intervals, comparisons and control/gate evidence; select `metrics.minimal_late_fusion` |
| [Original assessment report](../../../../runs/reassemble/20260927T175336Z-section1b/assessment/SECTION_1B_FUSION_ADMISSIBILITY_HANDOFF.md) | Human-readable methods and interpretation |
| [Frozen cohort](../../../../runs/reassemble/20260927T154732Z-section1/cohort.parquet) | Row identity and recorded outcomes |

[Compare all core fusion variants F1–F6](04_core_fusion_comparisons.md)

**To validate your understanding:** locate the sample by both IDs, use the feature archive `row_index` to find its inputs, inspect the architecture and the corresponding fold parameters, then join saved predictions to the cohort by row order. Read the whole-cohort metrics and intervals separately from this illustrative sample.

[Back to the experiment](../README.md)
