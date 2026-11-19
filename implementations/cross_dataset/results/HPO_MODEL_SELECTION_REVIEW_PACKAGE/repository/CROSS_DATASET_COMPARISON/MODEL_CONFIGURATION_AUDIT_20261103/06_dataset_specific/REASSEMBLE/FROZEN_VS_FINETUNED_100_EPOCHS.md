# Frozen versus full-CNN100epoch evidence

Audit date: 2026-11-03. Read-only reconstruction; no new model fitting, feature extraction or experiment changes.

| Model | Executed / selected epoch | T/V/C/assessment | Training h | Peak allocated GiB | Mean TRAINING compute % | AP | AUROC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B_frozen100 | 100 /14 | 1752/419/686/753 | 0.060992 | 0.080301 | 21.461300 | 0.193776 | 0.664605 |
| C_full_finetuned16 | 100 /47 | 1752/419/686/753 | 23.964191 | 7.770030 | 99.713245 | 0.212585 | 0.675325 |


Both use fresh original pretrained CNN and fresh seed42head;16frames/FP32, headLR0.001, wd0.001, clip1, effectivebatch8, micro1,100epochcosine multiplier1→.1, workers4, decoderthreads2, pinned/persistentprefetch2, no augmentation. CbackboneLR1e-5; allCNNconvolutions and FrozenBNaffine trainable, running moments fixed. AdamWbetas(.9,.999), eps1e-8 were recovered from actual resumable optimizer metadata without executing pickle. The frozen model operates on cached CNN features; its tiny head-training GPU memory/time omit feature extraction. Bprefix training order checks and Cgradient checks were previously retained.

The audit verifies100consecutiveepochs and selectedbest epochs14/47, receipt/statehash correspondence and saved prediction metrics on identical nativeIDs. `EPOCH_HISTORIES.csv` contains every epoch's training/validationloss, validationAP/AUROC, LR, updates, seconds, VRAM/utilization where recorded. The figures beside this report use those exact rows. Best checkpoints are PHASE1_BEST_MODEL.pt in each execution arm; last-state pointers are PHASE1_LATEST_EPOCH.json with hash-identified rotating recovery slots. Full paths/hashes remain in the checkpoint/run CSVs, and original held-out predictions remain linked in RESULTS_PROVENANCE.csv.

Visual AP difference is **+0.01880892572409615** on this selected cohort. It supports an observed improvement under this matched pilot recipe. It does not establish the average effect across folds/seeds or explain differences from the earlier short frozen study, which used batch128, short epochs and different fitting roles. No comparison interval is fabricated. Both branch probability calibrators are training-side, but pilot selection/test reuse makes later inference exploratory.

Ctraining23.964191h, validation1.629115h, inference/calibration.062891h. The process-attempt record has B271.338s and C10646.992+30.070+82269.026s: **pair active child wall25.89373h**, C-only25.81836h. These are neither pure GPU kernel hours nor uninterrupted calendar duration. Mean per-epoch sampled TRAINING NVML utilization99.713% is an activity statistic; it is not VRAM utilization. Peak allocated7.770GiB is a memory statistic, not reservedVRAM or compute percent. There is no defensible all-history GPU-hours grand total because many historical stages lack allocation/telemetry records.

Checkpoint chain is complete for saved-state/prediction/metric verification; no expensive inference or training was replayed. Single seed42, onepreviouslyexposedouterfold and preselection of fit3 are material limitations. Stronger independent effect estimation would require an agreed fresh/grouped assessment design; this audit neither chooses nor launches it.

## Training/validation diagnostic

The logged curves show strong overfitting: at epoch100,training weighted BCE is0.005231 frozen and approximately1.4e-9 full CNN,while validation weighted BCE is17.493164 and26.145111. AP-based selection still uses epochs14/47. See [the exact selected/final-epoch table](TRAINING_GENERALIZATION_DIAGNOSTICS.md). A100-epoch budget is not evidence that the final epoch generalizes best.

## Evidence anchors

- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json](../../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_configuration/PHASE1_COMPARISON_CONFIG.json) — effective shared100 horizon; head/backbone LR.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py](../../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_source/phase_model.py) — all CNN stages, FrozenBN affine promotion; fixed running moments.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py](../../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_source/compare100_train.py) — training100/checkpoint selection/recovery.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json](../../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_B_frozen100_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json) — history/best/executed_epochs, T/V/C/assessment sample identities.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json](../../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/26102026_C_full_finetuned16_seed42_selectedjob02/PHASE1_FIT_COMPLETE.json) — history/best/executed_epochs, T/V/C/assessment sample identities.
- [26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/PHASE1_COMPARISON_PROCESS_ATTEMPTS.json](../../../../26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability/26102026_bestfit_100epoch_frozen_vs_full_cnn/26102026_execution/PHASE1_COMPARISON_PROCESS_ATTEMPTS.json) — active child attempts and restart overhead.
