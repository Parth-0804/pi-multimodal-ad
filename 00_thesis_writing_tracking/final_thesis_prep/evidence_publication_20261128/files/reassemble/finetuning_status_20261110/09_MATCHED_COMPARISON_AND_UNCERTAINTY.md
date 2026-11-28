# Matched comparisons, sensor/F2 protocols and uncertainty

Audit date: 2026-11-10. **VERIFIED FROM SOURCE/ARTIFACTS:** all central point estimates below were recomputed directly from original saved probability files with CPU NumPy/scikit-learn. No training, coefficient refit or neural inference ran. Existing interval endpoints are **REPORTED BUT NOT INDEPENDENTLY RESAMPLED** in this audit; their sampling implementation and input identities were inspected. The direct recomputation covers original, early16/32, matched2, C20, native100, CNN100 follow-up, encoder comparison, temporal heads and boundary variants.

[07_VISUAL_ONLY_RESULTS.csv](07_VISUAL_ONLY_RESULTS.csv) contains per-fold and pooled visual metrics. [08_STATIC_SENSOR_AND_F2_RESULTS.csv](08_STATIC_SENSOR_AND_F2_RESULTS.csv) contains 74 separate comparison rows; [all metrics](support/RESULTS_ALL_RECOMPUTED_METRICS.csv) contains 380 score/cohort evaluations, including Brier, log loss, F1, precision, recall, balanced accuracy and confusion counts at common 0.5. Native original threshold results are separate columns. Repeated original/follow-up rows are explicit provenance views, never additional independent trials.

## Identity and role reconciliation

The original saved cohort has **4,530 unique recording::segment action keys,509 failures and 148 recordings**. The five outer fold sizes are753,964,1037,906,870. Every current central prediction key was checked against that canonical identity and native label, with no duplicate within a model's assessment set. Action-set and ordered-probability SHA-256 values are in the result CSVs. These audit hashes use sorted native keys, followed by newline, and little-endian float64 scores; they are distinct from original files' SHA-256 hashes.

The selected100 job uses the following mutually disjoint groups:

| Role | Actions | Failures | Recordings |
|---|---:|---:|---:|
| Gradient training |1752|198|60|
| Checkpoint validation |419|44|15|
| Visual calibration C |686|93|19|
| Inner-held-out F2 fitting bank |920|97|28|
| Outer assessment, original fold0 |753|77|26|

The five roles partition all 4,530 actions and 148 recordings. The 920 bank is disjoint from training, validation, C and outer753 at both action and recording levels. It is held out for the visual base models, but **is training data for final F2 coefficients**. Its F2 apparent scores are training metrics; its meta-cross-fitted scores are training-side diagnostics, not outer753 evaluation. The earlier long-frozen job0 has a different inner977 assessment, explicitly labeled `outer0_inner0`; it is not a pooled outer result.

A historical metadata inconsistency remains in `PHASE1_SELECTED_JOB.json`: `prediction_recordings` lists 28 inner920 recordings, while `predict` indexes 753 outer actions from 26 recordings. The actual saved prediction identifiers and `outer_E_recordings` confirm the outer753 role. The stale field must not control cohort interpretation. It was preserved unchanged.

[RESULTS_ROLE_PROOF.json](support/RESULTS_ROLE_PROOF.json) records exact role hashes and groups; [canonical action manifest](support/RESULTS_CANONICAL_ROLE_MANIFEST.csv) resolves every action; [987 group/score checks](support/RESULTS_GROUP_SAFETY_CHECKS.csv) verify original nested subfolds, early/matched partitions, phase plans, original sensor reuse and matched OOF/outer disjointness. No group overlap was detected in those audited role arrays. This does not erase the adaptive history of repeatedly examining this dataset.

## What can be compared

| Comparison | Classification | Reason |
|---|---|---|
| Matched2 frozen32 versus final-stage32, separately within seed42 or20261023 |DIRECTLY MATCHED|Same4,530 assessment actions, splits, two epochs,32frames and fixed sensor probabilities; different trainable CNN scope. Equal epochs are not equal GPU cost.|
| Frozen100 versus Full100, and their F2 contrasts |DIRECTLY MATCHED within the selected study|Same753 assessment actions, selected original training job,100epochs, initial pretrained CNN, independent selected checkpoints, calibration partitions and fixed canonical sensor. Only one selected job/outer fold/seed is covered.|
| Early frozen16 versus frozen32; early final-stage16 versus final-stage32 |DIRECTLY MATCHED within each scope|Same assessment examples and within-scope budget; frame count changes.|
| Early frozen versus final-stage, same frame count |PARTIALLY COMPARABLE|Same assessment cohort and sensor but five frozen-head epochs versus two adaptation epochs.|
| C20 versus original/early visual on4,530 |PARTIALLY COMPARABLE|Same assessment actions, different fitting budgets, training partition/selection and calibration protocols; not a controlled20epoch frozen/full comparison.|
| Original outer0 F2 versus CNN100 F2 |PARTIALLY COMPARABLE|Same753 assessment actions and exact canonical sensor probabilities, but different visual fitting and F2 fitting bank: original full 3777-row nested OOF versus one 920-row bank.|
| Pooled4,530 AP versus one-fold753 AP |NOT DIRECTLY COMPARABLE|Different population/prevalence; use exact original outer0 subset only if an historical same-cohort reference is wanted.|
| Inner920/inner977 diagnostic AP versus outer753/pooled4530 AP |NOT DIRECTLY COMPARABLE|Different examples and fitting/evaluation roles.|
| C20 F2 against any completed F2 |INSUFFICIENT EVIDENCE|Prepared C20 visual/sensor scores exist; no completed actual C20 F2 result was found.|

Seeds reuse the same recordings. Do not pool their rows as additional assessment examples or treat two seeds as a reliable seed-variance estimate. Seed42 final-stage32 in the matched study reuses the25 early final-stage fits; it is not an independent replication.

## Pooled AP and mean-fold AP

| Visual condition |Seed|Pooled AP,4530|Mean of five fold APs|
|---|---:|---:|---:|
|Original frozen16|20260927|0.230658|0.241544|
|Early frozen16,5epochs|42|0.221644|0.231541|
|Early frozen32,5epochs|42|0.219427|0.225568|
|Early final-stage16,2epochs|42|0.224466|0.231442|
|Early final-stage32,2epochs|42|0.230609|0.242172|
|Matched frozen32,2epochs|42|0.222708|0.228864|
|Matched final-stage32,2epochs|42|0.230609|0.242172|
|Matched frozen32,2epochs|20261023|0.216799|0.222990|
|Matched final-stage32,2epochs|20261023|0.200517|0.203281|
|C20 full CNN16|42|0.312127|0.308619|

Pooled AP combines all saved outer scores, while mean-fold AP averages five independently computed APs without weighting. They answer different questions. Single-fold100 APs are0.19377557761499092 frozen and0.21258450333908707 full; they do not belong in the pooled4530 table.

## Exact static sensor contract

**The verified feature count is220, not192:**22 sensor channels times10 per-action statistics. Channels are measured force3, measured torque3, gripper positions2, joint efforts7 and joint velocities7. Statistics, in feature-block order, are mean, population standard deviation, median, minimum, maximum,25th percentile,75th percentile, range, RMS and least-squares slope over normalized action progress. Original extraction resamples each action to512 positions; no fitted population quantities enter these statistics. Source: `src/reassemble/section1_features.py::statistics/extract`; actual saved arrays and names are recorded in [sensor contract](support/RESULTS_SENSOR_FEATURE_CONTRACT.json).

Original `src/reassemble/section1_models.py::logistic_fit` fits training-only per-feature mean/std, replacing invalid or very small std with1 and replacing transformed nonfinite values with0. The classifier is balanced L2 logistic regression, lbfgs default, max_iter2000, random_state0. C is selected from[0.1,1,10] using mean inner-fold AP. The selected branch is refit on all corresponding branch-training actions. Unweighted sigmoid logistic calibration (C1,max_iter1000) is learned from selected-C group-OOF raw logits. Native threshold maximizes OOF balanced accuracy over0.01..0.99, ties nearest0.5. It is not fixed0.5 in the original experiment.

Early and matched studies use the distinct fixed-C1 balanced sensor model in `.../run_01_two_epoch_finetuning/source/fusion.py::sensor_fit`: standardizer and raw classifier fit on G; C is a separate recording-held-out calibration set; unweighted C1 sigmoid calibrator max_iter2000; random_state42. Their pooled sensor AP is 0.42080289, different from the original0.42939187. The matched pipeline reuses one exact early sensor score bank across both arms and both seeds; this bitwise equality is independently checked. Across the original early tables, frozen16 differs from the other three sensor copies in 635 of 4,530 scores by at most 9.89e-17, so its exact vector hash differs despite identical fitted protocol and reported AP. Phase/C20 uses that frozen16-precision vector. These serialization-level differences are preserved, not silently rounded away. Phase/C20 prepared sensor scores have the same0.420803 pooled result; their presence does not imply a finalized C20 stacker.

CNN100 primary sensor scores instead reuse the **earliest original** branch. For inner920, the original outer0/inner2 branch trains on2857 actions, selectsC0.1 and calibrates using original subfold OOF logits. For outer753, the original outer0 refit trains on3777 actions, selectsC1 and calibrates using original inner OOF logits. Current score equality to those original banks was independently checked exactly. Outer753 AP is0.3277045645055636. The later separate-C sensor states retained alongside the follow-up are provenance references, not its primary sensor.

The original routine did not serialize logistic coefficients. CNN100 stores explicitly reconstructed original sensor states for the selected inner and outer branches, alongside the authoritative original probabilities; these are not newly fit in this audit. [57 sensor identities](support/RESULTS_SENSOR_MODEL_IDENTITIES.csv) contains model/prediction paths, hashes, selected C and calibration details. Historical original fits lacking coefficients are marked unavailable rather than implying all original sensor weights are recoverable.

## F2 equation and fitting differences

All audited central F2 conditions use calibrated branch **probabilities**, not branch logits:

`p_F2 = sigmoid(b + w_visual * p_visual + w_sensor * p_sensor)`.

The F2 objective is unweighted L2 logistic regression,C1,lbfgs,max_iter2000. There is no additional post-stacker calibration. Original/CNN100 estimator random_state is0; early/matched helper specifies42. [RESULTS_F2_COEFFICIENTS.csv](support/RESULTS_F2_COEFFICIENTS.csv) contains47 per-fold fitted coefficient triples and fitted-source hashes. Substitution of original saved branch probabilities reconstructs every audited F2 probability to maximum error below1e-12; no coefficient fitting was performed.

Original section1b builds all outer-training OOF rows via four inner held-out branches. Each inner branch itself performs four recording-disjoint subfolds for visual5/10epoch or sensorC selection and calibration, then refits on inner training data. Final outer branch refits match the original section1 scores. F2 is fit on all outer-training OOF probability pairs; meta-cross-fitting on that bank chooses its native balanced-accuracy threshold, then final F2 coefficients fit all bank rows. Original outer training bank sizes are3777,3566,3493,3624,3660.

Early/matched F2 also receives the complete four-inner-fold OOF bank but its branches use fixed epochs and separate G/C fitting. F2 fits the full bank once; evaluation uses fixed0.5. Matched seed42 final-stage F2 model itself is reused and arithmetically checked, not refitted.

CNN100 executes the **original `fit_stacker` function** but on only the920-action bank, rather than all3777 original outer-training OOF rows. Four group-aware meta splits serve threshold selection and diagnostic scores; final coefficients fit all920. Model files, input bank hash and a pre-evaluation fit lock are saved under `experiments/reassemble/29102026_cnn100_static_sensor_f2_comparison/05_fusion_models/`. The common threshold is0.5; the preserved native thresholds are0.10 frozen and0.14 full.

|F2 condition|Outer fold0 coefficient_visual|coefficient_sensor|intercept|
|---|---:|---:|---:|
|Original frozen16, full nested bank|3.114287|6.555474|-3.462646|
|Frozen100, single920 bank|0.944388|5.071543|-3.081964|
|Full100, single920 bank|1.133452|5.075055|-3.100495|

These coefficients have different branch score scales and bank populations. Their magnitude is not a modality importance ranking. The exact full-precision values, all original folds,20 early and20 matched stackers are in the linked coefficient CSV.

## Paired uncertainty and interpretation

Saved intervals use2,000 paired **recording-cluster** resamples. They condition on fixed fitted checkpoints, coefficients, selected model/split and available evaluation recordings. They capture recording sampling uncertainty only. They do not refit models, repeat checkpoint selection, account for seed variability, or remove uncertainty from choosing this dataset/fold after earlier analyses. Secondary contrasts are unadjusted for multiplicity.

|Contrast, AP difference|Point estimate|Saved95% interval|
|---|---:|---:|
|Original F2 minus original sensor,4530|+0.017907|[+0.008603,+0.028284]|
|Early final16 minus frozen16 visual|+0.002823|[-0.033563,+0.037891]|
|Early final16 minus frozen16 F2|-0.003159|[-0.012573,+0.008052]|
|Matched2 seed42 final minus frozen visual|+0.007902|[-0.017312,+0.033219]|
|Matched2 seed42 final minus frozen F2|-0.000796|[-0.006424,+0.006072]|
|Matched2 seed20261023 final minus frozen visual|-0.016282|[-0.039636,+0.009790]|
|Matched2 seed20261023 final minus frozen F2|-0.002822|[-0.008285,+0.003602]|
|CNN100 full minus frozen visual, follow-up draws|+0.018809|[-0.036995,+0.095910]|
|CNN100 full F2 minus frozen F2|+0.014117|[-0.000773,+0.029089]|
|CNN100 full F2 minus sensor|+0.021390|[-0.000345,+0.036358]|
|CNN100 frozen F2 minus sensor|+0.007273|[-0.003151,+0.015377]|

Original F2 has a positive conditional AP interval against its sensor. Matched2 does not demonstrate a fine-tuning AP improvement, or equivalence, within either seed. Its visual direction reverses across the two seeds, and F2 point differences are slightly negative in both. It resolves the earlier unequal epoch budget for this two-epoch 32-frame contrast; it does not establish that longer or full-backbone fine-tuning cannot help.

CNN100 AP differences against frozen or sensor cross zero; they do not demonstrate an AP improvement or equivalence. Some saved CNN100 AUROC intervals exclude zero (full-F2 minus frozen-F2:+0.011623,[0.001070,0.022797]; full-F2 minus sensor:+0.016618,[0.004581,0.031573]), but these remain fixed-model, single-fold, unadjusted results. Its arithmetic averaging APs0.348007 frozen/0.358533 full exceed F2 point estimates0.334977/0.349094; paired F2-minus-average AP intervals also cross zero. Do not select an architecture from this already-inspected outer fold.

The native100 comparison used a different saved bootstrap run: visual AP difference95% interval[-0.036445,+0.096926]. The follow-up interval above is[-0.036995,+0.095910]. They have the same point estimate and should be attributed to their own files, not averaged. The limited historical V-FT outer0 also has 753 saved raw logits; its ranking AP 0.572880 / AUROC 0.818681 are directly recomputed in07. This is a different temporal-head architecture and a single completed outer fold, not evidence for choosing a mean-head CNN condition. Sigmoid-transformed raw-logit Brier/logloss/threshold results are explicitly uncalibrated diagnostics, since no finalized calibrated V-FT pooled bank or F2 was saved.

No C20 paired refit/seed uncertainty was found; its pooled point score alone does not establish a controlled gain.

Full preserved endpoints: [existing interval table](support/RESULTS_EXISTING_INTERVALS.csv), [original F2 uncertainty](support/RESULTS_ORIGINAL_F2_UNCERTAINTY.json), [CNN100 follow-up uncertainty](support/RESULTS_CNN100_UNCERTAINTY.json), [native100 comparison](support/RESULTS_CNN100_NATIVE_COMPARISON.json).

## Numerical and provenance limits

Current original `PHASE1_100EPOCH_COMPARISON_METRICS.json`, native100 saved scores and follow-up CSV agree exactly on AP0.19377557761499092/0.21258450333908707. The two probability vectors also agree exactly after ID alignment. An independent tie-aware NumPy AP calculation agrees to floating-point roundoff; neither vector has tied scores. Slightly different figures in earlier audit extractions are not evidence of changed inference or different selected checkpoints. See [numerical reconciliation](support/RESULTS_NUMERICAL_RECONCILIATION.json).

Original source paths, sizes and SHA-256 values are in [RESULTS_INPUTS.csv](support/RESULTS_INPUTS.csv) and [RESULTS_LINEAGE_INPUTS.csv](support/RESULTS_LINEAGE_INPUTS.csv). Audit scripts [results_direct.py](tools/results_direct.py) and [results_lineage.py](tools/results_lineage.py) use saved numbers only. Group checks establish the documented role separation; recovered historical fitted weights and preprocessing are not re-executed here. C20 F2 remains **NOT EXECUTED** in the verified artifact set, and no new C20 fusion score was fabricated.
