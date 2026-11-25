# Task 3 — static-anchored adaptation

ADDITIONAL EXPLORATORY EXPERIMENTS. [VERIFIED EXECUTION]

Question: can input-dependent coefficient changes improve the established probability-input logistic stacker while keeping its branch evidence and output link fixed? Original F6 changed this link and did not establish adaptive value, motivating this isolated test.

Method: original Section1B/2 strictly nested visual/statistics probabilities; each proper training partition independently fits C1 F2. Freeze b,a; output sigmoid(b + sum(a*(1+tanh(h(u)))*p)). A-CONSTANT has two global parameters; A-ADAPTIVE uses action4+training-scaled quality36+availability2, MLP42→16→2, zero final initialization. Lambdas .01/.1/1; AdamW .003, decay .001, max100/min10/patience12, batch128, clip1. Select mean-inner-fold AP of three-seed probabilities. Outer epochs are per-seed rounded median inner best epochs. Threshold uses training-only inner OOF balanced accuracy. No extra output calibration is added to the prespecified logistic link. Branch calibrators remain frozen in their proper partitions.

| Model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A0 | 0.7950 | 0.4473 | 0.7129 | 0.6379 | 0.6071 | 0.2977 | 0.0784 | 0.0138 |
| A-CONSTANT | 0.7950 | 0.4457 | 0.7111 | 0.6351 | 0.6071 | 0.2937 | 0.0785 | 0.0129 |
| A-ADAPTIVE | 0.7993 | 0.4683 | 0.7116 | 0.6464 | 0.5874 | 0.3118 | 0.0770 | 0.0180 |

| Contrast | ΔAP, marginal 95% | ΔAUROC, marginal 95% | AP interpretation |
| --- | --- | --- | --- |
| A-ADAPTIVE minus A0 | +0.0210 [+0.0015, +0.0419] | +0.0044 [-0.0031, +0.0115] | supported improvement |
| A-ADAPTIVE minus A-CONSTANT | +0.0226 [+0.0036, +0.0432] | +0.0043 [-0.0031, +0.0115] | supported improvement |
| A-CONSTANT minus A0 | -0.0016 [-0.0035, +0.0003] | +0.0001 [-0.0005, +0.0006] | inconclusive difference |

AP is average precision. Paired uncertainty resamples 148 recordings, 2000 times; conditional on fitted models, without retraining or study-selection uncertainty. Individual seeds are not independent recordings.

| Outer fold | Constant λ | Adaptive λ | ΔAP adaptive−A0 | ΔAUROC adaptive−A0 |
| --- | --- | --- | --- | --- |
| 0 | 0.01 | 0.1 | +0.0020 | +0.0164 |
| 1 | 0.1 | 0.1 | +0.0275 | +0.0121 |
| 2 | 1.0 | 0.1 | +0.0570 | +0.0109 |
| 3 | 1.0 | 0.01 | -0.0192 | -0.0234 |
| 4 | 0.01 | 0.1 | +0.0211 | +0.0105 |

[OBSERVED RESULT] Clean adaptive AP improves over both matched F2 and the constant-adjustment control with positive marginal paired intervals. The AP point gain exceeds the prespecified .01 practical reference; this is not an established industrial utility requirement. Other metrics, fold changes and calibration must be read together; there is no universal metric improvement claim.

Fixed-weight diagnostics and effective coefficients: `ablations.json`, `effective_coefficient_summary.csv`, and `effective_coefficients.csv`. These are associational coefficients, not causal explanations or normalized probability weights. Action-associated failure priors remain an alternative explanation. Single-modality fallback and total-loss abstention identities passed synthetic tests; no recovery benefit is inferred.

[CORRECTED] First attempt stopped at signature mismatch caused by decimal-penalty filename suffix handling. `correction_001.md` and original log/unused first-fit files are retained. The corrected complete run uses unique filenames. Anchor probabilities match sealed outer stacking to <1e-8; floating-point sigmoid ties can shift pooled AUROC by a few millionths, so the exact matched A0 values above are reported.

Artifacts: `predictions.npz`, five `outer*.json` selection/refit records, `fits/*.pt` checkpoints and `fits/*.json` every-epoch histories, `learning_curves.{png,pdf}`, `comparison/results.json`, `per_seed_fold_metrics.csv`, `input_identities.json`. Checkpoints and prediction hashes are embedded in each completed fit record; protocol commit 26ae3a7. Final implementation commit and output hashes are recorded by the extension manifest.

Limitations: same outcome-informed cohort; exploratory marginal intervals; three seeds do not exhaust training variability; no independent validation. This task does not establish robustness or authorize combining new branches with this gate. Task4 tests exposure-matched robustness separately. Original historical conclusions remain unchanged.
