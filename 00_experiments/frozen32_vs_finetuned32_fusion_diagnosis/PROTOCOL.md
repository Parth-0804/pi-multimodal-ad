# Matched two-epoch Frozen32 versus Fine-tuned32 fusion diagnosis

This protocol is fixed before new visual training. Exactly two visual conditions and two seed families (42, 20261023) are permitted. Equal epochs and action passes do not imply equal compute.

## Locked representation and training

Reuse the original 4,530 actions, 509 failures, 148 recordings, exact 32-frame selections, image preprocessing, five outer folds, four inner folds and G/C memberships. Seed42 role seeds match the previous implementation. Seed20261023 changes only visual initialization/dropout/sample order using the same role-seed formula with a different base seed; G/C splits remain fixed and never use the new seed.

Only the original CNN backbone forward path executes; the same spatial maps are mean-pooled over space and frames into 896 features. No hybrid encoder, detector decoder or temporal transformer is introduced. Head: Linear(896,128), ReLU, Dropout(0.1), Linear(128,1). Both recipes train the head for exactly two epochs. Frozen32 uses hash-checked original features and no trainable CNN. Fine-tuned32 updates the same five convolution tensors in the final CNN stage, plus the head; earlier weights and all running buffers remain fixed, with backbone evaluation mode preserved.

FP32; one physical action, effective batch eight; AdamW; head LR1e-3, final stage LR1e-5, decay1e-3, global gradient clipping1; no scheduler or augmentation. G-only frozen-feature normalisation remains fixed during adaptation. Positive BCE weight uses G labels only. Independent fits restart from original pretrained weights. Each epoch uses `default_rng(role_seed+epoch)` permutation. Exact checkpoint state includes optimizer, model, epoch/batch offset and Torch CPU/CUDA/Python RNG; no fit exceeds two epochs. New seed42 frozen losses are checked against the retained first-two-epoch prefix of its original five-epoch training logs.

## Reuse, calibration and sensors

All25 existing compatible fine-tuned32 two-epoch seed42 fits are reused after exact source/configuration, input, role, model and prediction checks. Their original replay/gradient checks are reused, not rerun. Frozen32 has only final five-epoch states; 25 two-epoch head fits are needed per seed. The new seed also needs25 fine-tuned fits:75 new visual fits in total,25 reused. No extra seed is searched.

Raw branches fit only G; sigmoid calibration fits recording-disjoint C; prediction rows are held-out V or outer E. There is no G+C refit. Canonical sensor probabilities come from the original fine-tuned32 OOF/assessment banks, with identified fit-specific model/calibrator references. The same exact sensor probability values are used across both visual conditions and seeds. No sensors are refit. CSV round-trip parsing/persistence preserves binary probability values; a tolerance1e-14 is used only for historical visual serialization reconciliation when reusing the original canonical bank.

## Fusion and evaluation

Uniform fusion is `0.5*p_visual+0.5*p_sensor`, with no fitting. F2 remains unscaled logistic stacking of `[p_visual,p_sensor]`, intercept enabled, C1, original solver/max-iteration/settings, no class weighting and no final recalibration. It fits only on the four valid inner OOF banks that cover outer T. Exact compatible seed42 fine-tuned F2 models are reused; the other15 F2 models fit new valid OOF probabilities. Outer E never enters raw fitting, calibration or F2 fitting.

Inner OOF visual scores are held out from branch training/calibration, but they are F2 training inputs. Any F2 score on those rows is training performance, not independent validation. OOF and outer assessment branch metrics are reported separately by seed/fold/condition, with AP, AUROC, Brier, log loss, fixed0.5 precision/recall, classwise probability summaries and ten fixed reliability bins.

Primary comparisons within each seed: fine-tuned32 minus frozen32 AP for visual, uniform fusion and F2. Report pooled AP, mean-fold AP, each fold and two-seed descriptive stability separately. Never pool the seeds as independent recordings. Use the original 2,000 paired recording-multiplicity draws and recording order for complete matched five-fold coverage; default percentile95 aggregation. New predictions require new contrasts; no old four-arm bootstrap is rerun. Incomplete matched coverage receives descriptive partial metrics with denominator clearly marked; full-cohort intervals are not claimed for incomplete seeds.

Secondary budget diagnostic: seed42 new frozen2 versus original frozen5 using the same keyed cohort and fixed fine-tuned2 reference. The resulting change in the fine-tuned-minus-frozen contrast is reported descriptively and, where complete, with a paired recording interval; it is a new contrast, not a rerun of the earlier old-vs-old bootstrap. Seed variation is descriptive; two seeds do not establish a seed-variance distribution.

Complementarity: 0.5 correctness overlaps by truth class; true-label Brier/log-loss changes on sensor-missed/detected failures and sensor-false-positive/correct successes. Do not compare subset AP across unequal prevalence or call coefficients causal importance.

## Predeclared interpretation

Pattern A: visual and uniform improve but F2 does not: calibration/OOF/F2 interaction is a candidate. Pattern B: visual improves but neither fusion improves: limited additional complementarity is a candidate. Pattern C: material seed-to-seed effect changes: seed instability is a candidate. Pattern D: the seed42 matched-budget contrast changes the earlier discrepancy: original duration is a candidate confound. Pattern E: OOF image deficit plus outer image improvement and reduced fitted visual influence: OOF transfer mismatch is a candidate.

Use `Supported` only for a candidate pattern that repeats in both seeds and at least four of five paired folds per seed, with relevant paired intervals supporting the asserted direction. Treat a seed-specific matched-budget finding as bounded evidence rather than a universal cause. Zero-containing intervals do not establish equivalence or absence of benefit. Other outcomes are `Weak evidence`, `Not supported`, or `Unresolved`, with reasons. Multiple candidate mechanisms may coexist; no diagnostic pattern alone is called causal. `CAUSE_NOT_RESOLVED` is a valid final answer.

## Execution and stopping

At most one GPU job, four CPU affinity slots, no installs/downloads/purchases. All outputs are study-local. Old source/weights/raw data/reports remain read-only. No old experiment or broad audit is repeated. New storage is capped at8GiB with10GiB filesystem free reserve. Saved numerical primitives are imported through explicit study-owned path/I/O adapters; historical files are never patched.

The stable task clock allows24h from this resumed execution and reserves the last2h for evaluation/reporting. Before the new seed, use the measured old25-fit 32-frame train/predict/replay sum with multiplier1.15 plus frozen-head allowance. Start only if the complete matched seed reasonably fits before the training cutoff. Complete both visual arms within an outer fold before proceeding. Do not silently reduce folds/epochs/samples or extend the task. Safe checkpointing on the cutoff yields `PARTIAL_NEW_SEED`; report actual coverage. New compact checkpoints replay on three fixed identified actions; only new model replays run. No further experiment or scheduling follows the final handoff. Historical Task4 remains excluded.
