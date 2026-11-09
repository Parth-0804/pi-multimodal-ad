# REASSEMBLE CNN100 + original static-sensor F2 comparison

Completed 2026-10-29T01:20:55.777940+00:00. **Executed exploratory single-split comparison; not independent confirmation.**

The central comparison is static sensors alone versus frozen CNN + F2 versus fully fine-tuned CNN + F2. Both fusion arms use exactly the same static-sensor probabilities, fitting actions, held-out test IDs, logistic F2 function, fixed 0.5 threshold and metrics. Only the selected visual branch differs between M4 and M5.

| Model | AP | AUROC | Precision | Recall | F1 | Brier | Log loss | ECE15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Static sensor only | 0.327705 | 0.723680 | 0.666667 | 0.155844 | 0.252632 | 0.081479 | 0.292795 | 0.036268 |
| Frozen CNN + F2 | 0.334977 | 0.728675 | 0.615385 | 0.103896 | 0.177778 | 0.080453 | 0.289894 | 0.026295 |
| Fine-tuned CNN + F2 | 0.349094 | 0.740298 | 0.615385 | 0.103896 | 0.177778 | 0.080157 | 0.288338 | 0.028557 |


The seven controlled predictions cover the same **753 actions, 77 failures, 676 nonfailures, 26 recordings**, prevalence **0.102258**. F2 fitting uses a separate **920-action, 97-failure, 28-recording** training-side bank never used for the selected base models' gradient fitting, checkpoint selection or calibration. All existing models/results remain unchanged; no new CNN training was run.

The completed checkpoints were independently verified: frozen100 executed 100 epochs and selected 14; full CNN executed 100 and selected 47. Saved test AP values reproduce as 0.193775578 and 0.212584503. Original visual C calibrators and canonical sensor banks were independently verified; new CPU forward logits agree with saved GPU controls within the recorded tolerance.

This is **holdout stacking from one original inner fold**, not complete historical four-fold nested OOF replication. The 100-epoch models and test fold were already examined, and fit 3 was selected from prior training-side validation. The adaptation, sensor-role clarification and CPU runtime benchmark are preserved in01. No in-sample base predictions, calibration-fit rows or test labels were substituted for the F2 bank.

Main artifacts: [all-model results](MODEL_COMPARISON_RESULTS.md), [paired intervals](PAIRED_STATISTICAL_COMPARISON.md), [conclusion](FINAL_SCIENTIFIC_CONCLUSION.md), [actual held-out diagnostic examples](../../../../../EXTERNAL_REFERENCES.md). Exact prediction rows, fitted coefficients/scalers/calibrators, checkpoint paths/hashes, group identities and source receipts accompany the reports.
