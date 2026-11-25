"""Fit original F2 on a group-held-out bank, then unblind fixed test metrics."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'

import csv
import json
import warnings

import numpy as np
from scipy.special import expit
from scipy.stats import rankdata
from sklearn.metrics import (average_precision_score, roc_auc_score, precision_score,
    recall_score, f1_score, brier_score_loss, log_loss, confusion_matrix, classification_report)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression

from common import ROOT, REPO, BASE, STUDY, RUN, CONFIG, read, write, sha, relative, utc
from common import cohort, job, arm_folder, identity, status
from original_api import load

NAMES = {'M1_frozen100': 'Frozen CNN only', 'M2_finetuned100': 'Fine-tuned CNN only',
         'M3_sensor': 'Static sensor only', 'M4_F2_frozen': 'Frozen CNN + F2',
         'M5_F2_finetuned': 'Fine-tuned CNN + F2', 'M6_average_frozen': 'Frozen CNN + averaging',
         'M7_average_finetuned': 'Fine-tuned CNN + averaging'}
PAIRS = {
    'A_visual_finetuned_minus_frozen': ('M2_finetuned100', 'M1_frozen100'),
    'B_F2_finetuned_minus_frozen': ('M5_F2_finetuned', 'M4_F2_frozen'),
    'C_F2_finetuned_minus_sensor': ('M5_F2_finetuned', 'M3_sensor'),
    'D_F2_frozen_minus_sensor': ('M4_F2_frozen', 'M3_sensor'),
    'E_F2_finetuned_minus_visual': ('M5_F2_finetuned', 'M2_finetuned100'),
    'F_F2_frozen_minus_visual': ('M4_F2_frozen', 'M1_frozen100'),
    'G_F2_frozen_minus_average': ('M4_F2_frozen', 'M6_average_frozen'),
    'H_F2_finetuned_minus_average': ('M5_F2_finetuned', 'M7_average_finetuned')}


def align(records, ids):
    keys = [r['sample_id'] for r in records]
    assert len(keys) == len(set(keys)), 'DUPLICATE_PREDICTION_ID'
    assert set(keys) == set(ids) and len(ids) == len(set(ids)), 'PREDICTION_ID_SET_MISMATCH'
    lookup = {r['sample_id']: r for r in records}
    return [lookup[key] for key in ids]


def ece(y, p, bins=15):
    result, rows = 0., []
    for b in range(bins):
        mask = (p >= b/bins) & ((p < (b+1)/bins) if b < bins-1 else (p <= 1))
        count = int(mask.sum())
        pred, observed = (float(p[mask].mean()), float(y[mask].mean())) if count else (None, None)
        if count:
            result += count/len(y)*abs(pred-observed)
        rows.append({'bin': b, 'lower': b/bins, 'upper': (b+1)/bins,
                     'count': count, 'mean_probability': pred, 'fraction_failure': observed})
    return float(result), rows


def metrics(y, p, threshold=.5):
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    assert y.shape == p.shape and np.isfinite(p).all() and ((p >= 0)&(p <= 1)).all()
    h = p >= threshold
    calibration, bins = ece(y, p)
    return {'AP': float(average_precision_score(y, p)), 'AUROC': float(roc_auc_score(y, p)),
            'precision': float(precision_score(y, h, zero_division=0)),
            'recall': float(recall_score(y, h, zero_division=0)), 'F1': float(f1_score(y, h, zero_division=0)),
            'Brier': float(brier_score_loss(y, p)), 'log_loss': float(log_loss(y, p, labels=[0, 1])),
            'ECE15': calibration, 'calibration_bins': bins, 'threshold': threshold,
            'actions': len(y), 'positives': int(y.sum()), 'negatives': int((1-y).sum()),
            'prevalence': float(y.mean()), 'confusion_matrix_TN_FP_FN_TP': confusion_matrix(y, h, labels=[0, 1]).ravel().tolist(),
            'classification_report': classification_report(y, h, labels=[0, 1], target_names=['nonfailure', 'failure'], output_dict=True, zero_division=0)}


def independent_metrics(y, p, threshold=.5):
    """Separate NumPy/rank implementation with explicit tie-group AP semantics."""
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    order = np.argsort(-p, kind='stable')
    sy, sp = y[order], p[order]
    ends = np.r_[np.flatnonzero(np.diff(sp)), len(sp)-1]
    tp = np.cumsum(sy)[ends]
    ap = np.sum((tp/(ends+1))*np.diff(np.r_[0, tp]))/y.sum()
    npos, nneg = y.sum(), (1-y).sum()
    auc = (rankdata(p)[y == 1].sum()-npos*(npos+1)/2)/(npos*nneg)
    h = p >= threshold
    TP, FP, FN = int(np.sum(h & (y == 1))), int(np.sum(h & (y == 0))), int(np.sum(~h & (y == 1)))
    q = np.clip(p, np.finfo(float).eps, 1-np.finfo(float).eps)
    return {'AP': float(ap), 'AUROC': float(auc), 'precision': TP/max(TP+FP, 1),
            'recall': TP/max(TP+FN, 1), 'F1': 2*TP/max(2*TP+FP+FN, 1),
            'Brier': float(np.mean((p-y)**2)), 'log_loss': float(-np.mean(y*np.log(q)+(1-y)*np.log1p(-q)))}


def meta_plan(labels, groups):
    return list(StratifiedGroupKFold(4, shuffle=True, random_state=read(CONFIG)['meta_crossfit_diagnostic']['seed'])
                .split(np.zeros(len(labels)), labels, groups))


def fitting_bank():
    # The fitting path opens only the training-side probability/label banks and
    # ID/group audit metadata. The full cohort (including outer labels) is not
    # needed here and is read only after the fitted-model lock in main().
    audit = read(ROOT/'02_checkpoint_verification/VERIFICATION.json')['roles']
    ids = audit['original_inner_prediction_indices']['sample_ids']
    frozen = align(read(ROOT/'04_training_side_predictions/FROZEN100_HELDOUT.json'), ids)
    full = align(read(ROOT/'04_training_side_predictions/FINETUNED100_HELDOUT.json'), ids)
    sensor = align(read(ROOT/'03_static_sensor_evidence/CANONICAL_TRAINING_BANK_PREDICTIONS.json')['data'], ids)
    labels = np.array([r['failure'] for r in frozen])
    groups = np.array([r['recording_id'] for r in frozen])
    for bank in [frozen, full, sensor]:
        for entry, reference in zip(bank, frozen):
            assert all(entry[k] == reference[k] for k in ['sample_id', 'recording_id', 'segment_id', 'failure'])
    assert set(groups) == set(audit['original_inner_prediction_indices']['recording_ids'])
    for role in ['training', 'validation', 'C', 'predict']:
        assert not set(groups) & set(audit[role]['recording_ids']), 'BASE_MODEL_HOLDOUT_LEAKAGE'
    ps = np.array([r['p_sensor'] for r in sensor])
    probabilities = {'frozen': np.column_stack(([r['p_visual'] for r in frozen], ps)),
                     'finetuned': np.column_stack(([r['p_visual'] for r in full], ps))}
    assert np.array_equal(probabilities['frozen'][:, 1], probabilities['finetuned'][:, 1])
    entries = [dict(sample_id=ids[k], recording_id=groups[k], failure=int(labels[k]),
                    p_frozen=float(probabilities['frozen'][k, 0]),
                    p_finetuned=float(probabilities['finetuned'][k, 0]), p_sensor=float(ps[k]))
               for k in range(len(ids))]
    return entries, labels, groups, probabilities


def fit_fusions():
    """No outer test probabilities or labels are arguments or read here."""
    fusion, _ = load()
    import sys
    sys.path.insert(0, str(REPO/'src'))
    from reassemble.section1b import fit_stacker
    settings = read(REPO/'configs/reassemble/section1b.json')['stacker']
    assert read(ROOT/'03_static_sensor_evidence/CANONICAL_SENSOR_VERIFICATION.json')['passed']
    assert read(ROOT/'04_training_side_predictions/INFERENCE_RECEIPT.json')['actions_per_arm'] == 920
    entries, y, groups, probability = fitting_bank()
    write(ROOT/'04_training_side_predictions/EXACT_F2_INPUT_PROBABILITIES.json', entries)
    plan = meta_plan(y, groups)
    metadata = []
    models, crossfit = {}, {}
    for arm in ['frozen', 'finetuned']:
        x = probability[arm]
        # Execute the earliest original F2 fitter, including its training-only
        # meta-cross-fitted threshold. A fixed dummy prediction row avoids
        # opening any outer probabilities before the model lock is written.
        _, _, model = fit_stacker(x, y, np.arange(len(y)), plan, np.array([[.5, .5]]), settings)
        # Independent sklearn construction checks exact probability formula and
        # coefficient learning; original function remains the executed fitter.
        direct = LogisticRegression(C=1., class_weight=None, solver='lbfgs',
                                    max_iter=2000, random_state=0).fit(x, y)
        assert np.allclose(direct.coef_[0], model['coefficient'], atol=1e-12, rtol=0)
        assert abs(direct.intercept_[0]-model['intercept']) < 1e-12
        p = fusion.fused(x, model)
        assert np.max(np.abs(p-direct.predict_proba(x)[:, 1])) < 1e-12
        heldout = np.full(len(y), np.nan)
        for fold, (train, test) in enumerate(plan):
            assert not set(groups[train]) & set(groups[test])
            small = LogisticRegression(C=1., class_weight=None, solver='lbfgs', max_iter=2000, random_state=0).fit(x[train], y[train])
            heldout[test] = small.predict_proba(x[test])[:, 1]
            if arm == 'frozen':
                metadata.append({'fold': fold, 'training_sample_ids': [entries[i]['sample_id'] for i in train],
                                 'assessment_sample_ids': [entries[i]['sample_id'] for i in test],
                                 'training_recordings': sorted(set(groups[train])), 'assessment_recordings': sorted(set(groups[test]))})
        assert np.isfinite(heldout).all()
        crossfit[arm] = heldout
        models[arm] = model
        path = ROOT/f'05_fusion_models/F2_{arm.upper()}100.json'
        payload = {'fitted_utc': utc(), 'model': model, 'columns': ['p_visual', 'p_sensor'],
                   'seed': 42, 'estimator_random_state': 0,
                   'formula': read(CONFIG)['fusion_formula'], 'threshold': model['threshold'],
                   'common_comparison_threshold': .5,
                   'training_role': 'one original inner-fold held-out bank; not full nested4-fold OOF',
                   'training_actions': len(y), 'training_recordings': sorted(set(groups)),
                   'training_sample_ids': [r['sample_id'] for r in entries],
                   'protocol_sha256': sha(CONFIG), 'fitting_source': 'src/reassemble/section1b.py::fit_stacker',
                   'fitting_source_sha256': sha(REPO/'src/reassemble/section1b.py'),
                   'outer_test_labels_used': False, 'outer_test_probabilities_used': False,
                   'input_probability_sha256': sha(ROOT/'04_training_side_predictions/EXACT_F2_INPUT_PROBABILITIES.json')}
        if path.exists():
            old = read(path)
            assert old['model'] == model and old['protocol_sha256'] == sha(CONFIG)
        else:
            write(path, payload)
        for row, apparent, outofit in zip(entries, p, heldout):
            row[f'p_F2_{arm}_apparent_fit'] = float(apparent)
            row[f'p_F2_{arm}_meta_crossfit'] = float(outofit)
    write(ROOT/'04_training_side_predictions/F2_APPARENT_AND_META_CROSSFIT.json', entries)
    write(ROOT/'05_fusion_models/META_CROSSFIT_DIAGNOSTIC_SPLITS.json', metadata)
    locked = {'utc': utc(), 'locked_before_new_outer_metrics': True,
              'models': {k: identity(ROOT/f'05_fusion_models/F2_{k.upper()}100.json') for k in models},
              'protocol_identity': identity(CONFIG), 'evaluation_source_identity': identity(__file__),
              'primary_common_comparison_threshold': .5, 'native_thresholds_preserved': True,
              'new_outer_model_metrics_seen_before_this_receipt': False}
    receipt = ROOT/'05_fusion_models/FUSION_FIT_LOCK.json'
    if not receipt.exists():
        write(receipt, locked)
    else:
        assert read(receipt)['protocol_identity']['sha256'] == sha(CONFIG)
    return models, entries


def bootstrap(labels, recordings, probabilities, scores):
    settings = read(CONFIG)['bootstrap']
    group_names = sorted(set(recordings))
    grouped = [np.flatnonzero(recordings == name) for name in group_names]
    rng = np.random.default_rng(settings['seed'])
    distribution = {name: {metric: [] for metric in ['AP', 'AUROC']} for name in probabilities}
    for b in range(settings['replicates']):
        index = np.concatenate([grouped[g] for g in rng.integers(len(grouped), size=len(grouped))])
        y = labels[index]
        if np.unique(y).size < 2:
            continue
        for name, p in probabilities.items():
            distribution[name]['AP'].append(float(average_precision_score(y, p[index])))
            distribution[name]['AUROC'].append(float(roc_auc_score(y, p[index])))
        if (b+1)%250 == 0:
            print('BOOTSTRAP', b+1, '/', settings['replicates'], flush=True)
    differences = {}
    for name, (treatment, control) in PAIRS.items():
        differences[name] = {'treatment': treatment, 'control': control}
        for metric in ['AP', 'AUROC']:
            difference = np.array(distribution[treatment][metric])-np.array(distribution[control][metric])
            lo, hi = np.quantile(difference, [.025, .975])
            differences[name][metric] = {'estimate': scores[treatment][metric]-scores[control][metric],
                'lower95': float(lo), 'upper95': float(hi), 'valid_draws': len(difference),
                'interval_excludes_zero': bool(lo > 0 or hi < 0)}
    valid = len(next(iter(distribution.values()))['AP'])
    return {'settings': settings, 'assessment_groups': len(group_names), 'differences': differences,
            'excluded_single_class_resamples': settings['replicates']-valid,
            'not_adjusted_for_multiple_comparisons': True}, distribution


def historical(rows, selected):
    folder = REPO/'runs/reassemble/20260927T175336Z-section1b/stacking'
    with np.load(folder/'outer0.npz', allow_pickle=False) as z:
        ix, probabilities, hard = z['test_rows'], z['p'], z['hard']
    assert np.array_equal(ix, selected['predict'])
    old_rows = __import__('pandas').read_parquet(REPO/'runs/reassemble/20260927T154732Z-section1/cohort.parquet')
    for i in ix:
        assert str(old_rows.iloc[i].recording_id) == rows[i]['recording_id']
        assert str(old_rows.iloc[i].segment_id) == str(rows[i]['segment_id'])
        assert int(old_rows.iloc[i].failure) == rows[i]['failure']
    model = read(folder/'outer0.json')['stacker']
    y = np.array([rows[i]['failure'] for i in ix])
    assert np.array_equal(hard, probabilities >= model['threshold'])
    result = metrics(y, probabilities, threshold=model['threshold'])
    result['recordings'] = len({rows[i]['recording_id'] for i in ix})
    with np.load(folder/'oof.npz', allow_pickle=False) as z:
        pooled = {'AP': float(average_precision_score(z['y'], z['p'])),
                  'AUROC': float(roc_auc_score(z['y'], z['p'])), 'actions': len(z['y'])}
    reasons = ['Same753 test IDs/native labels/recordings and16-frame rule are verified.',
        'Original section1b uses full nested4-fold branch OOF, inner hyperparameter search and outer branch refits.',
        'The primary sensor is exactly this original selected-C/nested-OOF-calibrated branch; its saved test probabilities are identical. Later clean-CNN separate-C sensor models are retained only as reference evidence.',
        'Original frozen visual extraction uses FP16 autocast,5/10-epoch head selection and its original seed; current CNN100 features/training use FP32 and seed42.',
        'The same original F2 fitter/threshold-selection rule is used, but its new fitting bank covers one held-out inner fold rather than all3777 outer-training OOF rows. Main common-threshold scores and original native-threshold scores are both retained.',
        'Therefore M8 is a matched-cohort historical reference, not a controlled visual-fine-tuning treatment; pooled4530-action AP is a separate historical summary.']
    output = {'M8_matched_outer1_historical_reference': result, 'historical_all_folds_pooled': pooled,
              'model': model, 'directly_controlled_comparison': False, 'comparability_findings': reasons,
              'sources': [identity(folder/'outer0.npz'), identity(folder/'outer0.json'), identity(folder/'oof.npz')]}
    write(ROOT/'07_evaluation_results/HISTORICAL_COMPARABILITY.json', output)
    write(ROOT/'06_held_out_predictions/M8_HISTORICAL_REFERENCE.json',
          [dict(sample_id=rows[i]['sample_id'], recording_id=rows[i]['recording_id'],
                failure=int(y[k]), p_historical_F2=float(probabilities[k])) for k, i in enumerate(ix)])
    return output


def main():
    models, train_entries = fit_fusions()  # Freeze first; only then read outer data.
    fusion, _ = load()
    selected, rows = job(), cohort()
    ids = [rows[i]['sample_id'] for i in selected['predict']]
    frozen = align(read(arm_folder('frozen')/'PHASE1_PREDICTIONS.json'), ids)
    full = align(read(arm_folder('finetuned')/'PHASE1_PREDICTIONS.json'), ids)
    sensor = align(read(ROOT/'03_static_sensor_evidence/CANONICAL_OUTER_TEST_PREDICTIONS.json')['data'], ids)
    for bank in [frozen, full, sensor]:
        for entry, index in zip(bank, selected['predict']):
            assert all(entry[k] == rows[index][k] for k in ['sample_id', 'recording_id', 'segment_id', 'failure'])
    y = np.array([r['failure'] for r in frozen])
    groups = np.array([r['recording_id'] for r in frozen])
    pf, pc, ps = [np.array([r[column] for r in bank]) for bank, column in
                  [(frozen, 'p_visual'), (full, 'p_visual'), (sensor, 'p_sensor')]]
    p = {'M1_frozen100': pf, 'M2_finetuned100': pc, 'M3_sensor': ps,
         'M4_F2_frozen': fusion.fused(np.column_stack([pf, ps]), models['frozen']),
         'M5_F2_finetuned': fusion.fused(np.column_stack([pc, ps]), models['finetuned']),
         'M6_average_frozen': (pf+ps)/2, 'M7_average_finetuned': (pc+ps)/2}
    output = []
    for k, index in enumerate(selected['predict']):
        row = rows[index]
        output.append({**{name: row[name] for name in ['sample_id', 'recording_id', 'segment_id', 'failure', 'action', 'start', 'end']},
                       **{name: float(value[k]) for name, value in p.items()}})
    write(ROOT/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.json', output)
    with (ROOT/'06_held_out_predictions/ALL_MODELS_IDENTICAL_OUTER_IDS.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0])); writer.writeheader(); writer.writerows(output)
    scores, parity = {}, {}
    for name, values in p.items():
        scores[name] = dict(metrics(y, values), recordings=len(set(groups)), display_name=NAMES[name])
        independent = independent_metrics(y, values)
        delta = {metric: abs(scores[name][metric]-v) for metric, v in independent.items()}
        assert max(delta.values()) < 1e-12, (name, 'INDEPENDENT_METRIC_MISMATCH', delta)
        parity[name] = {'independent_metrics': independent, 'absolute_differences': delta, 'passed': True}
    write(ROOT/'07_evaluation_results/ALL_MODEL_METRICS.json', scores)
    native_thresholds = {'M1_frozen100': .5, 'M2_finetuned100': .5,
        'M3_sensor': read(ROOT/'03_static_sensor_evidence/CANONICAL_OUTER_TEST_MODEL.json')['model']['native_threshold'],
        'M4_F2_frozen': models['frozen']['threshold'], 'M5_F2_finetuned': models['finetuned']['threshold'],
        'M6_average_frozen': .5, 'M7_average_finetuned': .5}
    write(ROOT/'07_evaluation_results/ORIGINAL_NATIVE_THRESHOLD_METRICS.json',
          {name: dict(metrics(y, values, native_thresholds[name]), display_name=NAMES[name]) for name, values in p.items()})
    write(ROOT/'09_reproducibility/INDEPENDENT_METRIC_RECOMPUTATION.json', parity)
    paired, distribution = bootstrap(y, groups, p, scores)
    write(ROOT/'07_evaluation_results/PAIRED_RECORDING_BOOTSTRAP.json', paired)
    write(ROOT/'07_evaluation_results/BOOTSTRAP_METRIC_DRAWS.json', distribution)
    history = historical(rows, selected)
    train_y = np.array([r['failure'] for r in train_entries])
    train_prob = {'M1_frozen100': np.array([r['p_frozen'] for r in train_entries]),
                 'M2_finetuned100': np.array([r['p_finetuned'] for r in train_entries]),
                 'M3_sensor': np.array([r['p_sensor'] for r in train_entries])}
    train_prob.update(M4_F2_frozen_apparent_fit=np.array([r['p_F2_frozen_apparent_fit'] for r in train_entries]),
                      M5_F2_finetuned_apparent_fit=np.array([r['p_F2_finetuned_apparent_fit'] for r in train_entries]),
                      M4_F2_frozen_meta_crossfit=np.array([r['p_F2_frozen_meta_crossfit'] for r in train_entries]),
                      M5_F2_finetuned_meta_crossfit=np.array([r['p_F2_finetuned_meta_crossfit'] for r in train_entries]))
    write(ROOT/'07_evaluation_results/TRAINING_SIDE_DIAGNOSTIC_METRICS.json',
          {'role_warning': 'Base predictions are genuinely held out from base fitting. F2 apparent-fit metrics reuse its fitting labels; meta-crossfit is a separate group diagnostic. No diagnostic changes primary models.',
           'scores': {name: metrics(train_y, values) for name, values in train_prob.items()}})
    all_metrics = []
    for name, values in scores.items():
        all_metrics.append({'model': name, **{k: v for k, v in values.items() if not isinstance(v, (dict, list))}})
    with (ROOT/'07_evaluation_results/MODEL_COMPARISON.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_metrics[0]));writer.writeheader();writer.writerows(all_metrics)
    status('FUSION_FITTING_AND_OUTER_EVALUATION_COMPLETE', models=7, assessment_actions=753,
           assessment_recordings=26, paired_bootstrap=2000, independent_metrics_verified=True)
    print('EVALUATION_COMPLETE', json.dumps({k: v['AP'] for k, v in scores.items()}), flush=True)


if __name__ == '__main__':
    main()
