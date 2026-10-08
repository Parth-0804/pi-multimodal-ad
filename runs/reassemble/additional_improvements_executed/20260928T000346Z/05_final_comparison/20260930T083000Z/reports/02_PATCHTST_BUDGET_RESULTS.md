# Task 2 — PatchTST training budget

ADDITIONAL EXPLORATORY EXPERIMENTS. [VERIFIED EXECUTION]

Question: was the original six-epoch cap limiting, or do engineered statistics remain stronger after bounded convergence-oriented training? Original PatchTST selected six in every original outer fold; S-HIST remains sealed evidence. S-6 repeats original3/6 selection with three seeds. S-LONG changes only maximum training100, min10/patience12. Architecture, channels512×22, patch32/stride16, width32, layers2/heads4/FF64, pooling, missing-observation mask, train-only channel scaling and mean imputation are unchanged. S-STATS remains the established reference; this extension does not rewrite the historical negative result.

Training uses original class-weighted BCE, AdamW lr.001/decay.001, clip1, effective batch128. Seeds20260927–29. Outer refit epochs are rounded median inner best epochs per seed (S-6 retains its explicitly requested mean-inner-AP3/6 selection). Each seed uses training-only sigmoid logistic calibration; final predictions average calibrated seed probabilities. Thresholds retain the original balanced-accuracy grid and tie rule. No outer labels select fitting, calibration or thresholds.

| Model | AUROC | AUPRC | balanced_accuracy | macro_F1 | failure_recall | failure_precision | Brier | ECE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S-6 | 0.7155 | 0.2557 | 0.6410 | 0.5360 | 0.6090 | 0.1908 | 0.0929 | 0.0114 |
| S-LONG | 0.7298 | 0.2853 | 0.6609 | 0.5688 | 0.5914 | 0.2173 | 0.0919 | 0.0156 |
| S-HIST | 0.7054 | 0.2416 | 0.6352 | 0.5463 | 0.5639 | 0.1956 | 0.0937 | 0.0067 |
| S-STATS | 0.7793 | 0.4294 | 0.7056 | 0.6223 | 0.6149 | 0.2765 | 0.0804 | 0.0174 |

| Contrast | ΔAP, marginal95% | ΔAUROC, marginal95% | AP interpretation |
| --- | --- | --- | --- |
| S-LONG minus S-6 | +0.0297 [+0.0122,+0.0451] | +0.0142 [+0.0033,+0.0247] | supported improvement |
| S-LONG minus S-STATS | -0.1441 [-0.1861,-0.1009] | -0.0496 [-0.0760,-0.0237] | supported deterioration |
| S-6 minus S-HIST | +0.0141 [-0.0045,+0.0338] | +0.0102 [-0.0031,+0.0233] | inconclusive difference |

AP is average precision. Intervals use2000 paired recording-cluster resamples, conditional on fitted models, without full retraining or outcome-informed study-selection uncertainty. Fold metrics and paired fold changes are in `comparison/results.json`; `per_seed_fold_metrics.csv` gives individual seed/fold results. No non-significant comparison establishes equivalence.

Convergence: 0 long-budget inner fits reached epoch100. `selected_epochs.csv`, every-epoch `learning_curves.csv`, and `learning_curves.{png,pdf}` show selections/loss/AP; inner AUROC is retained too. Reaching the cap permits an undertraining limitation, not automatic extra epochs. Compute/parameter records are in `fit_compute.csv`; refit timings and checkpoint/prediction hashes are in every `fits/<variant>/outer*/branch.json`.

Secondary S-HYBRID−S-STATS: ΔAP +0.0110,95% [+0.0054,+0.0181]; supported improvement.

The C1 logistic hybrid uses calibrated S-LONG and statistics with nested branch predictions; even its inner threshold predictions use deeper training-only branch selection/calibration. These are two representations of one sensor modality. Selected S-6 inner checkpoints are retained via reuse or one deterministic replay to the already-selected3/6 epoch, requiring parity with saved logits; original predictions are untouched (selected_S6_checkpoint_retention.json). It does not replace the statistics branch in Tasks3/4.

Interpretation is bounded by matched controls, seed/fold variation and paired intervals. Report supported improvements, deteriorations and inconclusive effects equally. This outcome-informed same-cohort extension is not independent confirmation. No winning changes are automatically combined. Exact protocol/config, implementation commits and artifact manifests are under the new root only; completed original study files and external Reasoning Record are unchanged.

Versioned sensor completion report; previous summaries are preserved. Original fitting/comparison evidence: `runs/reassemble/additional_improvements_executed/20260928T000346Z/02_patchtst_training_budget`. New curves and tables are beside this file.
