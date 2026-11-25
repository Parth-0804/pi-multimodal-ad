"""Research reports grounded in saved probabilities, models and source receipts."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import json
import shutil
import sys
import datetime as dt
import subprocess
import importlib.metadata

import numpy as np

from common import ROOT, REPO, BASE, COMPARISON, STUDY, RUN, CONFIG
from common import read, write, relative, sha, identity, utc, cohort, job, status
from evaluate import NAMES


def put(name, text):
    path = ROOT/'10_final_research_report'/name
    for before, after in [('all4530', 'all 4,530'), ('original148', 'original 148'),
                          ('seed42', 'seed 42'), ('fit3', 'fit 3'), ('with77', 'with 77'),
                          ('across26', 'across 26'), ('same920', 'same 920'),
                          ('the920', 'the 920'), ('the753', 'the 753'),
                          ('within2857', 'within 2,857'), ('all3777', 'all 3,777'),
                          ('source/settings', 'source and settings'), ('threshold0.5', 'threshold 0.5')]:
        text = text.replace(before, after)
    path.write_text(text.strip()+'\n')
    return path


def metric_table(scores):
    text = '| Model | AP | AUROC | Precision | Recall | F1 | Brier | Log loss | ECE15 |\n'
    text += '|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    for name, values in scores.items():
        text += '| '+NAMES.get(name, name)+' | '+' | '.join(f'{values[k]:.6f}' for k in
                ['AP', 'AUROC', 'precision', 'recall', 'F1', 'Brier', 'log_loss', 'ECE15'])+' |\n'
    return text


def difference(row, metric='AP'):
    x = row[metric]
    return f"{x['estimate']:+.6f} [95% CI {x['lower95']:+.6f}, {x['upper95']:+.6f}]"


def conclusion(row):
    x = row['AP']
    if x['lower95'] > 0:
        return 'The conditional interval supports a positive difference on this selected split; independent confirmation remains absent.'
    if x['upper95'] < 0:
        return 'The conditional interval supports a negative difference on this selected split.'
    return 'The interval includes zero; an improvement is not established.'


def main():
    scores = read(ROOT/'07_evaluation_results/ALL_MODEL_METRICS.json')
    pairs = read(ROOT/'07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json')['differences']
    historical = read(ROOT/'07_evaluation_results/HISTORICAL_COMPARABILITY.json')
    verification = read(ROOT/'02_checkpoint_verification/VERIFICATION.json')
    models = {arm: read(ROOT/f'05_fusion_models/F2_{arm.upper()}100.json') for arm in ['frozen', 'finetuned']}
    rows, selected = cohort(), job()
    training = read(ROOT/'07_evaluation_results/TRAINING_SIDE_DIAGNOSTIC_METRICS.json')
    examples = read(ROOT/'08_visual_diagnostics/HELDOUT_DISAGREEMENT_EXAMPLES.json')
    primary = ['M3_sensor', 'M4_F2_frozen', 'M5_F2_finetuned']
    overview = f'''# REASSEMBLE CNN100 + original static-sensor F2 comparison

Completed {utc()}. **Executed exploratory single-split comparison; not independent confirmation.**

The central comparison is static sensors alone versus frozen CNN + F2 versus fully fine-tuned CNN + F2. Both fusion arms use exactly the same static-sensor probabilities, fitting actions, held-out test IDs, logistic F2 function, fixed 0.5 threshold and metrics. Only the selected visual branch differs between M4 and M5.

{metric_table({name: scores[name] for name in primary})}

The seven controlled predictions cover the same **753 actions, 77 failures, 676 nonfailures, 26 recordings**, prevalence **{77/753:.6f}**. F2 fitting uses a separate **920-action, 97-failure, 28-recording** training-side bank never used for the selected base models' gradient fitting, checkpoint selection or calibration. All existing models/results remain unchanged; no new CNN training was run.

The completed checkpoints were independently verified: frozen100 executed 100 epochs and selected 14; full CNN executed 100 and selected 47. Saved test AP values reproduce as {scores['M1_frozen100']['AP']:.9f} and {scores['M2_finetuned100']['AP']:.9f}. Original visual C calibrators and canonical sensor banks were independently verified; new CPU forward logits agree with saved GPU controls within the recorded tolerance.

This is **holdout stacking from one original inner fold**, not complete historical four-fold nested OOF replication. The 100-epoch models and test fold were already examined, and fit3 was selected from prior training-side validation. The adaptation, sensor-role clarification and CPU runtime benchmark are preserved in01. No in-sample base predictions, calibration-fit rows or test labels were substituted for the F2 bank.

Main artifacts: [all-model results](MODEL_COMPARISON_RESULTS.md), [paired intervals](PAIRED_STATISTICAL_COMPARISON.md), [conclusion](FINAL_SCIENTIFIC_CONCLUSION.md), [actual held-out diagnostic examples](../08_visual_diagnostics/HELDOUT_DISAGREEMENTS.html). Exact prediction rows, fitted coefficients/scalers/calibrators, checkpoint paths/hashes, group identities and source receipts accompany the reports.
'''
    put('EXPERIMENT_OVERVIEW.md', overview)
    original_feature_metadata = next(iter(sorted((REPO/'runs/reassemble/20260927T154732Z-section1/features').glob('*.json'))))
    channel_names = read(original_feature_metadata)['channel_names']
    statistics = ['nanmean', 'nanstd_ddof0', 'median', 'minimum', 'maximum',
                  'q25', 'q75', 'peak_to_peak', 'RMS', 'slope_over_normalized_action_progress']
    write(ROOT/'03_static_sensor_evidence/FEATURE_CONTRACT.json',
          {'channels': channel_names, 'statistics_in_block_order': statistics,
           'feature_count': 220, 'layout': '10 blocks of22 channels in the original channel order',
           'resampling': 'Original512 normalized-action-progress points; no change or new extraction',
           'source': identity(REPO/'src/reassemble/section1_features.py'),
           'channel_metadata_source': identity(original_feature_metadata),
           'feature_cache': identity(STUDY/'shared_cache/sensor_statistics.npy')})
    arch = f'''# Architecture verification

The executed primary F2 fitter is `src/reassemble/section1b.py::fit_stacker`; the later clean-CNN primitive is retained as a separately identified reference. The 100-epoch CNN extension is `{relative(BASE/'26102026_source/phase_model.py')}`; its inference/training recipe is `phase_training.py` in the same folder. Their source hashes and original checkpoint hashes are in the run input manifest. The earliest historical F2 is `src/reassemble/section1b.py`; differences are recorded below rather than treating later recipes as identical to every historical experiment.

## Static sensor branch — canonical earliest original implementation

`src/reassemble/section1_features.py::statistics` defines22 original sensor channels: measured force3, measured torque3, gripper positions2, joint efforts7 and joint velocities7. It computes10 blocks after the original512-point resampling: mean, population standard deviation, median, minimum, maximum, q25, q75, peak-to-peak, RMS and slope over normalized action progress. This gives220 features. All4530 cached rows match the original148 recording blocks exactly; no feature was changed or re-extracted.

The primary sensor uses the earliest `src/reassemble/section1_models.py` functions `Standardizer`, `logistic_fit` and `calibrate` and Section1b nested selection/calibration procedure. Standardizer fits nanmean/nanstd on its branch-training rows only, floors invalid or tiny standard deviations at1 and fills remaining transformed nonfinite values with0. Balanced logistic C is selected from0.1/1/10 on training-only recording folds. A separate unweighted sigmoid calibrator is fitted to genuine within-training OOF logits, then applied to the refitted branch's assessment logits.

The original inner3 branch uses2857 fit/OOF-calibration actions and selected C0.1; it generates the920 genuinely held-out F2 fitting probabilities. The original outer branch uses3777 fit/OOF-calibration actions and selected C1; it generates the753 test probabilities shared exactly by M3–M7. Its original native decision threshold is0.14. The original code did not persist raw logistic weights/scalers. These small states were reconstructed from the exact recorded training groups, using the original source/settings, and independently verified against the original saved probabilities and OOF calibrators. Scientific evaluation reuses the saved original probabilities rather than replacing them with the reconstructed outputs.

The later clean-CNN/Phase1 separate-C sensor variant (G2171/C686 and G2966/C811) was also audited and replayed exactly, but is retained as reference evidence only. It is **not substituted for the canonical original primary sensor**. Both historical recipes, source paths and the pre-test protocol clarification are preserved. Matching the original16-thread numerical-library context reproduces the original canonical probability banks exactly; no original source, checkpoint or result was modified.

## Visual branch

Sixteen distinct hand-camera frame indices per action, exact original resize/rescale and verified pixel hashes feed the pinned RT-DETR R18vd CNN. The last three backbone maps are spatially averaged/concatenated to896 dimensions, followed by the original 16-frame arithmetic mean and training-T-only standardization. The classifier is896→128, ReLU, dropout0.1, then128→1. The frozen arm reuses verified FP32 pooled features. The fine-tuned arm learned all executed CNN convolution and normalization-affine parameters plus the head; normalization running moments remained fixed. No detection transformer/head, PatchTST, audio or32-frame input is used.

Both arms executed 100 epochs from original pretrained initialization, seed42, with the same selected fit3 partitions, FP32 recipe, effective action batch8, AdamW, head LR0.001, backbone LR0.00001 where trainable, weight decay0.001, clipping1 and cosine100 schedule. Checkpoint selection used V only: frozen epoch14, full epoch47. Each visual calibrator was learned on the same separate686-action C bank. Saved calibrators are reused; no calibration is fitted on the F2 bank or test set.

The saved original first-epoch gradient receipt was checked directly: every CNN stage and the head had finite, nonzero gradient evidence and changed weights, while running normalization moments remained unchanged. No new gradient-training pass was used for verification.

## F2 method, not an F2 classification metric

The executed fitter is the original `src/reassemble/section1b.py::fit_stacker`. It fits unweighted C1 logistic regression (`lbfgs`, max_iter2000, random_state0) directly to `[p_visual,p_sensor]`, with unrestricted coefficients and intercept. Probabilities are not converted to logits or meta-standardized:

`p_F2 = sigmoid(intercept + w_visual*p_visual + w_sensor*p_sensor)`.

The same original function also selects a native threshold by maximizing balanced accuracy on recording-disjoint meta-cross-fitted training probabilities over0.01–0.99, ties nearest0.5. This original native threshold is saved and evaluated for each F2 arm. The primary common-threshold metric table additionally uses0.5 for every model so precision/recall/F1 share an identical convention. Native-threshold metrics are retained separately; no test-derived threshold is chosen.

To isolate fitting from evaluation, the original fitter receives only the920 training-side probability pairs/labels and a fixed dummy prediction row. Real outer probabilities are opened only after saving and hashing the fitted models. The two visual arms use the same920 rows, canonical sensor column and four recording-disjoint meta folds. Simple averaging is exactly `(p_visual+p_sensor)/2`.

Historical M8 uses the same canonical sensor, original F2 formulation and native threshold-selection rule, but has the old visual recipe and a complete3777-row nested branch-OOF fitting bank. The new fixed100-epoch checkpoints can supply one920-row genuine holdout bank; this explicit holdout-stacking adaptation is not presented as a complete historical nested-OOF reproduction.
'''
    put('ARCHITECTURE_VERIFICATION.md', arch)
    role_table = '| Role | Actions | Recordings | Failures |\n|---|---:|---:|---:|\n'
    labels = {'training': 'CNN gradient T', 'validation': 'CNN checkpoint V', 'C': 'Visual/inner sensor calibration C',
              'original_inner_prediction_indices': 'F2 base-model holdout', 'predict': 'Outer assessment E'}
    labels['C'] = 'Visual calibration C'
    for key in ['training', 'validation', 'C', 'original_inner_prediction_indices', 'predict']:
        r = verification['roles'][key]
        role_table += f"| {labels[key]} | {r['actions']} | {r['recordings']} | {r['positives']} |\n"
    leakage = f'''# Data split and leakage audit

{role_table}

These five roles partition all 4,530 eligible actions and148 recordings. Every pair has zero recording overlap. The outer753 IDs are identical across M1–M7 and have no duplicates. Native failure labels, recording IDs and segment IDs match the original cohort exactly.

The selected100-epoch CNNs use T for gradient fitting, V for checkpoint selection and686 C actions for calibration. Their original inner3 assessment bank (920 actions/28 recordings) is excluded from all three roles. The canonical inner sensor fits and calibrates from nested OOF within2857 actions that exclude these920 actions. Thus neither base branch uses its F2-bank assessment labels during fitting, selection, scaling or calibration.

For final outer prediction, the original sensor is refitted and OOF-calibrated on all3777 outer-training actions, including the F2-bank rows as ordinary outer training. This is the original stacking refit role, not test leakage: all753 test recordings remain excluded. F2 fitting itself opens only the920 training-side banks and ID/group audit metadata; the complete cohort and outer probability files are opened only after the coefficient lock.

This single held-out bank is not a complete four-fold cross-fitted branch bank. We deliberately report holdout stacking and retain the historical complete-OOF result separately. No additional CNN fit is scientifically required for this fixed-model holdout comparison; reproducing the complete historical nested training design would be a different, larger study. The fixed-model comparison does not borrow predictions from the ongoing20-epoch75-fit visual study.

Four recording-disjoint meta folds within the920 rows implement the original training-only F2 native-threshold rule and also provide an overfitting diagnostic. Their AP does not select hyperparameters or model weights. The common comparison table remains at0.5, and original native-threshold results are saved separately. Original fit3 was chosen from previously observed20-epoch training-side validation across differing splits, and the outer fold was already inspected in the100-epoch study. This is an exploratory, post-selected follow-up rather than independent confirmation. Prior dataset exposure and possible selection effects are not removed by conditional bootstrap intervals.

Before fitting, source inspection clarified a stale selected-job `prediction_recordings` field inherited from inner3. Actual outer prediction IDs/recordings were derived from the saved cohort and checked directly. The clarification and sensor-role amendment are preserved in01. The two F2 models and protocol were serialized/hashed in `05_fusion_models/FUSION_FIT_LOCK.json` before calculating any new outer sensor/fusion score. That receipt includes the fitting/evaluation source identity. No test-derived hyperparameter or threshold search was performed.
'''
    put('DATA_SPLIT_AND_LEAKAGE_AUDIT.md', leakage)
    native_scores = read(ROOT/'07_evaluation_results/ORIGINAL_NATIVE_THRESHOLD_METRICS.json')
    results = f'''# Model comparison results

All M1–M7 rows use the same 753 held-out actions,77 failures,676 nonfailures,26 recordings and failure prevalence {77/753:.6f}. Higher AP/AUROC/precision/recall/F1 is better; lower Brier/log loss/ECE is better. Precision, recall and F1 use the predefined0.5 threshold. ECE uses15 fixed equal-width probability bins and is descriptive: bins can contain few failures and no calibration superiority claim follows from ECE alone.

{metric_table(scores)}

All per-sample probabilities/labels/recording IDs are in06; every metric, confusion matrix and calibration-bin count is in `07_evaluation_results/ALL_MODEL_METRICS.json`. No result is averaged across seeds or folds. There is exactly one trained seed/fold context here.

## Historical M8, shown separately

On the verified same 753 IDs, historical Section1b F2 has AP{historical['M8_matched_outer1_historical_reference']['AP']:.6f}, AUROC{historical['M8_matched_outer1_historical_reference']['AUROC']:.6f}, and original training-selected threshold{historical['model']['threshold']:.2f}. Its full metrics and saved probabilities are included separately. Historical pooled-all-fold AP{historical['historical_all_folds_pooled']['AP']:.9f} is based on4530 actions and must not be compared as if it were a753-action score.

The test cohort/labels/frame count match, but visual branch selection, precision, visual calibration, seeds and full fusion OOF coverage differ; the canonical sensor test probabilities are identical. Therefore M8 is not a controlled treatment estimate against M4/M5 and is not placed into the primary paired-improvement table. Exact comparability findings are in `HISTORICAL_COMPARABILITY.json`.

## Visual evidence and plots

- [Primary sensor/F2 AP](../07_evaluation_results/figures/PRIMARY_SENSOR_AND_F2_COMPARISON.png)
- [All seven models with conditional AP intervals](../07_evaluation_results/figures/ALL_MODELS_AP.png)
- [Precision–recall curves](../07_evaluation_results/figures/PRECISION_RECALL_CURVES.png)
- [Training-side versus outer branch behavior](../07_evaluation_results/figures/TRAINING_SIDE_VS_OUTER_BRANCH_AP.png)
- [F2 apparent-fit/meta-crossfit/held-out behavior](../07_evaluation_results/figures/F2_FITTING_AND_HELDOUT_BEHAVIOR.png)
- [Paired differences](../07_evaluation_results/figures/PAIRED_AP_DIFFERENCES.png)
- [Branch disagreements](../07_evaluation_results/figures/BRANCH_DISAGREEMENTS.png)
- [Calibration](../07_evaluation_results/figures/CALIBRATION.png)

Every plotted number traces to a saved probability/metric/bootstrap artifact through `FIGURE_SOURCE_MANIFEST.json`. Training-side base scores are held out from base fitting; apparent F2 fitting scores reuse its fitting labels and are explicitly separated from meta-crossfit diagnostics. Different-cohort scores are not paired generalization gains.
'''
    results+='\n## Original native training-only thresholds\n\nThe primary table uses the same0.5 convention for every model. These additional rows retain the original sensor and F2 training-selected decision thresholds. AP/AUROC/Brier/log loss are unchanged; precision/recall/F1 reflect the respective native rules. No test threshold was selected.\n\n'+metric_table(native_scores)+'\n'
    results+='\nNative thresholds: '+', '.join(NAMES[name]+'='+format(values['threshold'],'.2f') for name,values in native_scores.items())+'.\n'
    put('MODEL_COMPARISON_RESULTS.md', results)
    pair_table = '| Contrast, treatment minus control | AP difference [95% CI] | AUROC difference [95% CI] |\n|---|---|---|\n'
    for name, result in pairs.items():
        pair_table += f"| {name.split('_', 1)[1].replace('_', ' ')} | {difference(result)} | {difference(result, 'AUROC')} |\n"
    statistical = f'''# Paired statistical comparison

{pair_table}

All comparisons use the same 2,000 paired recording-cluster resamples (seed20261029). Each draw samples 26 recordings with replacement and retains every action of each selected recording; repeated recordings repeat all their actions. Each model receives identical draw indices. This respects within-recording dependence and preserves the action-level estimand instead of treating753 actions as independent replicates.

Intervals are percentile95% intervals conditional on this selected split and these fitted models. They do not include retraining, seed/fold variation, prior test exposure or the original fit-selection process. The eight contrasts are exploratory, with no multiplicity adjustment and no new model selected from them. Resamples missing either native class are excluded because AUROC is undefined; excluded and valid draw counts plus full AP/AUROC draws are retained. Intervals crossing zero do not establish improvement; a positive conditional interval still does not constitute independent confirmation.

F2 fine-tuned minus frozen: **{difference(pairs['B_F2_finetuned_minus_frozen'])}**. {conclusion(pairs['B_F2_finetuned_minus_frozen'])}

F2 frozen minus sensor: **{difference(pairs['D_F2_frozen_minus_sensor'])}**. {conclusion(pairs['D_F2_frozen_minus_sensor'])}

F2 fine-tuned minus sensor: **{difference(pairs['C_F2_finetuned_minus_sensor'])}**. {conclusion(pairs['C_F2_finetuned_minus_sensor'])}
'''
    put('PAIRED_STATISTICAL_COMPARISON.md', statistical)
    coefficient = '# F2 coefficient analysis\n\nF2 is sigmoid(b+w_visual*p_visual+w_sensor*p_sensor). Coefficients act on probabilities, not logits; their signs are unconstrained and they are not normalized mixture weights.\n\n'
    coefficient += '| Arm | Visual coefficient | Sensor coefficient | Intercept |\n|---|---:|---:|---:|\n'
    coefficient_remarks = []
    train_inputs = read(ROOT/'04_training_side_predictions/EXACT_F2_INPUT_PROBABILITIES.json')
    details = {}
    for arm in ['frozen', 'finetuned']:
        m = models[arm]['model'];w = m['coefficient'];b = m['intercept']
        coefficient += f'| {arm} | {w[0]:.9f} | {w[1]:.9f} | {b:.9f} |\n'
        pv = np.array([r['p_'+arm] for r in train_inputs]);ps = np.array([r['p_sensor'] for r in train_inputs])
        details[arm] = {'training_probability_std_visual': float(pv.std()), 'training_probability_std_sensor': float(ps.std()),
                        'coefficient_times_training_std_visual': float(w[0]*pv.std()),
                        'coefficient_times_training_std_sensor': float(w[1]*ps.std()),
                        'training_visual_sensor_correlation': float(np.corrcoef(pv, ps)[0, 1])}
        coefficient_remarks.append(f'For {arm}, a +0.1 visual probability change adds {w[0]*.1:+.6f} to fused log odds when the sensor value is fixed; a +0.1 sensor change adds {w[1]*.1:+.6f}. This is the fitted model response, not a causal feature effect.')
    coefficient += '\n'+'\n\n'.join(coefficient_remarks)+'\n'
    write(ROOT/'05_fusion_models/COEFFICIENT_SCALE_DIAGNOSTICS.json', details)
    coefficient += '\nBranch calibration scales differ and predictions can be correlated, so raw coefficient magnitude alone is not evidence of visual usefulness or modality importance. Training probability spreads, coefficient×spread and branch correlation are retained separately. Regularization can shrink the visual contribution even when visual-only AP improves. The paired fusion scores, rather than an appealing coefficient, answer whether fusion improved. No coefficient was selected or altered after evaluating the test set.\n\nActual held-out disagreement examples and their failure labels, all seven probabilities, source identities,16 input frames and original timestamps are saved in08. Selection covers both native classes, both disagreement directions, fusion corrections and regressions when available; absent categories are reported, not manufactured. These are diagnostics after freezing the models and cannot establish a physical failure cause.\n'
    put('FUSION_COEFFICIENT_ANALYSIS.md', coefficient)
    Q = [('Q1 — Does fine-tuning improve visual-only prediction?', 'A_visual_finetuned_minus_frozen'),
         ('Q2 — Does frozen CNN F2 improve over sensors?', 'D_F2_frozen_minus_sensor'),
         ('Q3 — Does fine-tuned CNN F2 improve over sensors?', 'C_F2_finetuned_minus_sensor'),
         ('Q4 — Does fine-tuned F2 outperform frozen F2?', 'B_F2_finetuned_minus_frozen')]
    scientific = '# Final scientific conclusion\n\n**Completed exploratory single-split study. No superiority, novelty or independent confirmation is assumed.**\n\n'
    scientific += metric_table({name: scores[name] for name in primary})+'\n'
    for title, pair in Q:
        scientific += '## '+title+'\n\n'+difference(pairs[pair])+'. '+conclusion(pairs[pair])+'\n\n'
    scientific += '## Q5 — Does F2 outperform simple averaging?\n\n'
    scientific += 'Frozen: '+difference(pairs['G_F2_frozen_minus_average'])+'. '+conclusion(pairs['G_F2_frozen_minus_average'])+'\n\n'
    scientific += 'Fine-tuned: '+difference(pairs['H_F2_finetuned_minus_average'])+'. '+conclusion(pairs['H_F2_finetuned_minus_average'])+'\n\n'
    sign = 'also has a higher fusion AP point estimate' if pairs['B_F2_finetuned_minus_frozen']['AP']['estimate'] > 0 else 'does not produce a higher fusion AP point estimate'
    scientific += '## Q6 — Does better visual AP translate into better fusion?\n\n'
    scientific += f"Visual AP increased by {pairs['A_visual_finetuned_minus_frozen']['AP']['estimate']:+.6f}; fine-tuning {sign}. The paired fusion result is {difference(pairs['B_F2_finetuned_minus_frozen'])}. {conclusion(pairs['B_F2_finetuned_minus_frozen'])} A visual-only gain does not guarantee complementary information beyond sensors.\n\n"
    scientific += '## Q7 — How strong is the evidence?\n\nAll intervals are conditional on one selected fold and seed42, with77 failures across26 assessment recordings. The outer set was already inspected and original fit3 was post-selected from earlier validation. F2 training covers one genuinely held-out inner bank rather than all historical nested OOF folds. Sensor and visual final training sizes differ as documented; the M4/M5 sensor column and every comparison setting are held fixed. This does not justify a broader seed/fold, unseen recording-source, cross-dataset or deployment claim. The ongoing75-fit20-epoch study remains separate and was neither interrupted nor mixed into these results.\n\n'
    scientific += '## Q8 — What happens when branches disagree?\n\n'
    scientific += f'{len(examples)} unique real held-out cases are saved with predefined selection/support rules, actual native labels, probabilities from every fixed model,16 model-input frames, original frame/time mappings and source identities. The gallery includes correct and incorrect predictions where the corresponding category exists. F2 response follows the saved coefficient formula, not an oracle modality switch. [Open the disagreement gallery](../08_visual_diagnostics/HELDOUT_DISAGREEMENTS.html). These examples explain model behavior after fitting; they did not influence coefficients, calibration or model choice.\n\n'
    scientific += '| Sample ID | Native failure | Fine-tuned visual p | Sensor p | Fine-tuned F2 p |\n|---|---:|---:|---:|---:|\n'
    for example in examples:
        scientific += f"| {example['sample_id']} | {example['failure']} | {example['M2_finetuned100']:.6f} | {example['M3_sensor']:.6f} | {example['M5_F2_finetuned']:.6f} |\n"
    scientific += '\nThe sensor coefficient is about5.075 versus1.133 for the fine-tuned visual probability; these are probability-space coefficients, not normalized importance weights. In failure `dba477e8fcfd70e655841f61`, fine-tuned vision gives0.588149, the sensor0.073984 and fusion0.113208. Vision flags the failure at0.5, but fusion remains below its training-selected0.14 native threshold and misses it. In normal action `dab16299508458550630e2c4`, vision gives0.618485 (a false positive), the sensor0.055897 and fusion0.107571, below0.14, so fusion rejects the visual false alarm. Normal action `dbe71bb8aae5b4e7a4bbca2d` has a high sensor score0.838305 and fused score0.773525 despite a low visual score0.065614, retaining the false alarm. Thus the fitted model can suppress visual errors and useful visual exceptions; it does not always choose the correct branch. Common0.5 and original native-threshold decisions are both shown in the gallery. No mechanical cause is inferred from these probabilities or images.\n\n'
    scientific += '## What was executed and independently checked\n\nThe two original100-epoch selected checkpoints were loaded and hash-verified. Canonical original static-sensor states were reconstructed and verified against the original saved probability banks/calibrators, which were reused for evaluation. Missing base-held-out CNN predictions were generated on CPU using the original 16 frames and pixel hashes. Two original-formulation logistic F2 models and group meta-crossfit diagnostics were fitted. Seven models were evaluated on identical753 IDs; historical M8 was reproduced separately. NumPy/rank implementations independently reproduced AP, AUROC, precision, recall, F1, Brier and log loss. The original fitter was also checked against a separate sklearn logistic construction. Paired recording-bootstrap results, all metrics, probability rows and report/figure source hashes are retained. No new CNN fit or test-label fitting was used.\n'
    put('FINAL_SCIENTIFIC_CONCLUSION.md', scientific)
    reproduction = f'''# Reproducibility report

Use the repository environment from the project root. No network or new package is required. Existing selected models remain in `{relative(COMPARISON)}`; exact paths and SHA256 are in the run input manifest. Sensor models/scalers/calibrators and both saved sensor banks are included in03; fitted F2 coefficients are in05. Large CNN checkpoints and raw recordings are referenced rather than duplicated.

For a quick independent read-only verification, run `ma_thesis_env/bin/python -B {relative(ROOT/'src/recompute_metrics.py')}`. It reads only the exported CSV and metric/bootstrap artifacts, uses separate NumPy/rank formulas, prints every model's recalculated metrics and checks the paired intervals to1e-12. It needs no CNN weights or raw dataset and changes no file.

Commands executed:

```bash
ma_thesis_env/bin/python -B {relative(ROOT/'src/verify.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/verify_sensor_features.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/verify_sensor_models.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/verify_canonical_sensor.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/benchmark_cpu.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/infer.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/evaluate.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/plots.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/reports.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/validate.py')}
ma_thesis_env/bin/python -B {relative(ROOT/'src/seal.py')}
ma_thesis_env/bin/python -B -m pytest -q -p no:cacheprovider {relative(ROOT/'tests')}
```

The listed stage commands record the performed analysis. The CPU completion launcher `src/complete_pipeline.py` orchestrates evaluation, figures, reports and validation after inference and creates the pipeline receipts used by final sealing. A full replay must use a fresh versioned experiment directory with its own ACTIVE_RUN.json pointer and copied locked configuration/source; never direct new writes into this completed run.

The locked scientific protocol is01/LOCKED_PROTOCOL_03.json; earlier pre-analysis drafts and both original-recipe clarifications are preserved. The initial visual/checkpoint verification remains bound to protocol02 because the CNNs and input roles are unchanged. Reproduce into a new versioned directory, preserving this completed run. The original draft is preserved with its documented pre-analysis sensor-role clarification. CPU inference initially used2 threads; a calibration-control throughput benchmark selected8 available CPU threads with identical FP32 control output. An optional fixed-shape FP32 compiler was faster in one control benchmark but failed during full initialization (native exit139), before producing any scientific prediction rows. It was rejected. The active runtime is stable eager FP32 inference with8 threads, CPU_RUNTIME_03.json; attempted/earlier runtime receipts and per-row evidence are preserved. No learned parameter, frame, precision or model choice changed. All six saved-GPU controls were repeated for the active backend. Only this task's resumable CPU process was restarted, never the running GPU study. The16 model-input frames per example match their original pixel hashes. CPU/GPU forward parity, strict checkpoint loading, original calibrator refits and frozen-logit replay are recorded in02.

No outer-test labels or probabilities enter `fit_fusions()`; it reads only the training bank and ID/group audit metadata. The fusion-fit lock was created before new outer metrics and includes the fixed source/configuration/model hashes. A separate recording-group meta-crossfit is diagnostic only. The test table can be recomputed directly from06 without loading a CNN. Independent NumPy/rank-based metric calculations, including tied-score AP and rank AUROC, reproduce the sklearn table to1e-12; tests include tied and boundary probabilities and duplicate-ID rejection.

All commands write exclusively inside this new experiment. Raw data, original source code, existing checkpoints and previous reports are unchanged. Main-study execution receipts are observed only; no checkpoint or controller setting is changed. The final validation receipt and output manifest distinguish checked original source identities, derived artifacts and known scientific limitations. An output manifest is not a claim of independent dataset replication.

For sensor training replay, keep the recorded original16-thread OpenBLAS partitioning; the checker constrains its physical CPU affinity while retaining that numerical reduction configuration. The later-variant sensor replay reproduces its saved weights/probabilities exactly; the canonical original models were reconstructed and verified against their saved OOF/calibrated probabilities. The comparison uses the original canonical saved probabilities, never replacement-refit probabilities. Run the final sealing command after all stage logs and pipeline receipts are closed so their final hashes, rather than intermediate snapshots, enter the output manifest.

Limitations: previously inspected single test fold; selected original fit; one training-side holdout bank; no complete100-epoch4-fold branch OOF reproduction; no additional seed/fold validation; conditional uncertainty; ECE sparse-bin instability. The saved source identity is sufficient to audit the performed analysis but does not erase those limitations.
'''
    put('REPRODUCIBILITY_REPORT.md', reproduction)
    readme = '# REASSEMBLE: CNN100 + static-sensor F2 comparison\n\nCompleted exploratory single-split comparison.\n\n'
    for name in ['EXPERIMENT_OVERVIEW.md', 'ARCHITECTURE_VERIFICATION.md', 'DATA_SPLIT_AND_LEAKAGE_AUDIT.md',
                 'MODEL_COMPARISON_RESULTS.md', 'PAIRED_STATISTICAL_COMPARISON.md', 'FUSION_COEFFICIENT_ANALYSIS.md',
                 'REPRODUCIBILITY_REPORT.md', 'FINAL_SCIENTIFIC_CONCLUSION.md']:
        readme += f'- [{name}](10_final_research_report/{name})\n'
    readme += '\n'+metric_table({name: scores[name] for name in primary})
    readme += '\n[All keyed test probabilities](06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.csv) · [Real disagreement examples](08_visual_diagnostics/HELDOUT_DISAGREEMENTS.html) · [Checkpoint verification](02_checkpoint_verification/VERIFICATION_REPORT.md).\n'
    (ROOT/'README.md').write_text(readme)
    for p in (ROOT/'10_final_research_report').glob('*.md'):
        dest = RUN/'reports'/p.name;dest.write_bytes(p.read_bytes())
    write(RUN/'software_provenance.json', {'utc': utc(),
        'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        'tracked_git_status': subprocess.check_output(['git', 'status', '--short', '--untracked-files=no'], cwd=REPO, text=True),
        'python': sys.version, 'packages': {p: importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','torch','transformers','pillow','matplotlib','pytest']},
        'source_identities': [identity(p) for p in sorted((ROOT/'src').glob('*.py'))],
        'CPU_runtime': read(ROOT/'01_experiment_definition/CPU_RUNTIME_03.json'),
        'earlier_CPU_runtime_preserved': read(ROOT/'01_experiment_definition/CPU_RUNTIME.json'),
        'rejected_optional_CPU_compiler_runtime': read(ROOT/'01_experiment_definition/CPU_RUNTIME_02.json'),
        'raw_payloads_modified': False, 'existing_models_modified': False, 'GPU_jobs_interrupted': False,
        'additional_CNN_fits': 0, 'complete_nested100_epoch_OOF_reproduction': False,
        'scope': 'Executed heldout-stacking comparison, original clean-CNN F2 primitive, fixed one-fold100-epoch models'})
    status('REPORTS_AND_FIGURES_COMPLETE_VALIDATION_PENDING', models_evaluated=7,
           historical_reference_separate=True, reports=8, new_CNN_fits=0)
    print('REPORTS_COMPLETE', flush=True)


if __name__ == '__main__':main()
