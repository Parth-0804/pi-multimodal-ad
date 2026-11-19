# Recorded training and validation gap

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

| Model | Epoch | TRAINING weighted BCE | VALIDATION weighted BCE | VALIDATION AP | VALIDATION AUROC |
| --- | --- | --- | --- | --- | --- |
| B_frozen100 | 1 | 1.927891 | 1.701719 | 0.136769 | 0.602788 |
| B_frozen100 | 14 | 0.505134 | 6.751437 | 0.281486 | 0.627515 |
| B_frozen100 | 100 | 0.005231 | 17.493164 | 0.170159 | 0.605636 |
| C_full_finetuned16 | 1 | 2.311212 | 1.184002 | 0.149848 | 0.583879 |
| C_full_finetuned16 | 47 | 0.038439 | 23.394478 | 0.277859 | 0.608909 |
| C_full_finetuned16 | 100 | 0.000000 | 26.145111 | 0.218015 | 0.582970 |


The recorded curves show a pronounced training/validation gap. Training loss approaches zero while validation weighted BCE rises substantially. This supports an overfitting/poor raw validation-probability diagnostic under these logged objectives,not an inference about every unseen cohort. AP measures ranking while BCE measures probability errors; the objectives need not improve together. The source selects by validation AP,so14/47 remain the evaluated selected checkpoints even though100 epochs executed. Epoch100 is not the reported best held-out model. Calibration is a later training-side operation;these epoch curves do not show a post-calibration held-out trajectory.

The pilot's observed held-out AP improvement therefore does not justify saying that longer training improved all generalization metrics. No per-epoch test curve was computed,as that would repeatedly inspect the assessment set. All points above come from saved histories;no training or inference was rerun.
