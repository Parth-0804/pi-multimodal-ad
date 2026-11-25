# Task 1 — temporal visual representations

ADDITIONAL EXPLORATORY EXPERIMENTS. [VERIFIED EXECUTION]

Question: does frame order contribute beyond the original temporal mean, separately from increased capacity and training? The completed study retained only segment means. Actual 16-frame sequences were re-extracted at the identical saved frame positions with pinned RT-DETR and unchanged 640×640 preprocessing. Timestamps, valid masks, raw source/model/processor identities and mean-parity checks are saved per recording.

V-MEAN retains the original head. V-TEMP uses projection896→128, fixed sinusoidal positions, one four-head Transformer layer, FFN256/dropout.1, valid-frame mean and binary head. V-NOPOS has identical capacity without positional encoding. Normalization uses training-segment mean-vector moments.

Training uses original class-weighted BCE, AdamW lr.001/decay.001, clip1, effective batch128. Seeds20260927–29. Outer refit epochs are rounded median inner best epochs per seed (S-6 retains its explicitly requested mean-inner-AP3/6 selection). Each seed uses training-only sigmoid logistic calibration; final predictions average calibrated seed probabilities. Thresholds retain the original balanced-accuracy grid and tie rule. No outer labels select fitting, calibration or thresholds.

| Model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V-MEAN | 0.7111 | 0.2434 | 0.6548 | 0.5287 | 0.6699 | 0.1905 | 0.0937 | 0.0144 |
| V-TEMP | 0.8459 | 0.5752 | 0.7564 | 0.6836 | 0.6601 | 0.3621 | 0.0742 | 0.0372 |
| V-NOPOS | 0.8029 | 0.4891 | 0.7188 | 0.6059 | 0.6896 | 0.2573 | 0.0828 | 0.0417 |
| V-HIST | 0.6978 | 0.2307 | 0.6414 | 0.5153 | 0.6621 | 0.1810 | 0.0943 | 0.0070 |

| Contrast | ΔAP, marginal95% | ΔAUROC, marginal95% | AP interpretation |
| --- | --- | --- | --- |
| V-TEMP minus V-MEAN | +0.3318 [+0.2871,+0.3721] | +0.1347 [+0.1103,+0.1602] | supported improvement |
| V-TEMP minus V-NOPOS | +0.0860 [+0.0552,+0.1157] | +0.0430 [+0.0272,+0.0580] | supported improvement |
| V-MEAN minus V-HIST | +0.0127 [-0.0104,+0.0359] | +0.0133 [+0.0004,+0.0262] | inconclusive difference |

AP is average precision. Intervals use2000 paired recording-cluster resamples, conditional on fitted models, without full retraining or outcome-informed study-selection uncertainty. Fold metrics and paired fold changes are in `comparison/results.json`; `per_seed_fold_metrics.csv` gives individual seed/fold results. No non-significant comparison establishes equivalence.

Convergence: 0 long-budget inner fits reached epoch100. `selected_epochs.csv`, every-epoch `learning_curves.csv`, and `learning_curves.{png,pdf}` show selections/loss/AP; inner AUROC is retained too. Reaching the cap permits an undertraining limitation, not automatic extra epochs. Compute/parameter records are in `fit_compute.csv`; refit timings and checkpoint/prediction hashes are in every `fits/<variant>/outer*/branch.json`.

Fixed-weight reversal/permutation results are in `order_diagnostic_metrics.csv`; non-positional invariance tests precede execution. Score changes alone do not establish useful temporal reasoning. A temporal-order claim additionally requires V-TEMP improvement relative to V-NOPOS; improvement only against V-MEAN may reflect capacity.

[NOT RUN / INCOMPLETE] No completed five-fold V-FT comparison exists. The audit/status/attempt log records any actual blocker; pending work must not be described as completed or as a negative finding.

Interpretation is bounded by matched controls, seed/fold variation and paired intervals. Report supported improvements, deteriorations and inconclusive effects equally. This outcome-informed same-cohort extension is not independent confirmation. No winning changes are automatically combined. Exact protocol/config, implementation commits and artifact manifests are under the new root only; completed original study files and external Reasoning Record are unchanged.
