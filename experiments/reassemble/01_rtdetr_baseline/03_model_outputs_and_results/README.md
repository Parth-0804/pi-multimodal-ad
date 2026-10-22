# 03 — Predictions, evaluation and results

**What the model predicts:** a probability of recorded action failure. `p` is the calibrated/fused failure probability; `hard` is the binary decision using that fold's selected threshold; `y` is the recorded outcome; `fold` identifies the outer held-out fold. Single-modality files also contain `raw` logits and `[4530,128]` learned embeddings. Arrays retain the frozen cohort order. The IDs are in the cohort table, not repeated in every NPZ file.

**The example sample (cohort row 3326):** saved failure probability **0.230252**, predicted failure **1**, recorded failure **1**, outer fold **4**. This is a lookup of a previously saved prediction, not fresh inference. One sample cannot validate aggregate performance.

| Metric over all 4,530 held-out predictions | Saved estimate | 95% recording-bootstrap interval |
|---|---:|---|
| AUROC | 0.6978 | 0.6716–0.7232 |
| AUPRC | 0.2307 | 0.1983–0.2701 |
| balanced_accuracy | 0.6414 | 0.6175–0.6658 |
| macro_F1 | 0.5153 | 0.4956–0.5355 |
| failure_recall | 0.6621 | 0.6149–0.7075 |
| failure_precision | 0.1810 | 0.1617–0.2013 |
| Brier | 0.0943 | 0.0862–0.1028 |
| ECE | 0.0070 | 0.0057–0.0184 |

`AUPRC` in these reports is implemented as average precision. AUROC/AP assess probability ranking; balanced accuracy, F1, recall and precision use the saved thresholded decisions. Brier score assesses probability error; ECE uses 15 bins. Intervals resample whole recordings (2,000 bootstrap replicates), accounting for samples sharing a recording.

**Interpretation:** the original unimodal gate was CONDITIONAL for both RT-DETR and PatchTST. Do not turn a positive metric estimate into a claim that all admissibility criteria passed. The `sensor_statistics` baseline has higher AP (0.4294) than these deep baselines. The original report explains the paired differences and 19 recording/action-conditioned label-shift controls. `perm00` means original labels; `perm01`–`perm19` are controls, not alternative primary results.

| Open | What it contains |
|---|---|
| [Saved predictions](../../../../runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00.npz) | Binary NPZ arrays; 4,530 rows aligned to the cohort |
| [Full recorded results](../../../../runs/reassemble/20260927T154732Z-section1/assessment/results.json) | Multiple models, intervals, comparisons and control/gate evidence; select `metrics.rtdetr` |
| [Original assessment report](../../../../runs/reassemble/20260927T154732Z-section1/assessment/SECTION_1_UNIMODAL_HANDOFF.md) | Human-readable methods and interpretation |
| [Frozen cohort](../../../../runs/reassemble/20260927T154732Z-section1/cohort.parquet) | Row identity and recorded outcomes |

**To validate your understanding:** locate the sample by both IDs, use the feature archive `row_index` to find its inputs, inspect the architecture and the corresponding fold parameters, then join saved predictions to the cohort by row order. Read the whole-cohort metrics and intervals separately from this illustrative sample.

[Back to the experiment](../README.md)
