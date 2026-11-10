"""Task-disjoint probability F2; immutable fit lock precedes outer-score evaluation."""
from __future__ import annotations
from pathlib import Path
import warnings
import numpy as np
from scipy.special import expit
from scipy.stats import spearmanr, kendalltau
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
from vifailback.metrics import metrics, independent_check
from .common import (STUDY, PROJECT, read_json, sha256, write_json, immutable_json,
                     protocol, fit_root, signature, relative, resolve, utc, exclusive_lock)

MODELS = ['visual', 'sensor_LR', 'average', 'F2', 'historical_HGB', 'historical_V1']


def fitted_f2(probabilities, labels):
    x, y = np.asarray(probabilities, dtype=np.float64), np.asarray(labels, dtype=int)
    if x.shape != (len(y), 2) or set(np.unique(y)) != {0, 1}:
        raise ValueError('F2 needs two probability columns and both native classes')
    if not np.isfinite(x).all() or not ((x >= 0) & (x <= 1)).all():
        raise ValueError('F2 inputs must be finite probabilities, not logits')
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        model = LogisticRegression(C=1., penalty='l2', solver='lbfgs', max_iter=2000,
                                   class_weight=None, random_state=42).fit(x, y)
    result = {'coefficient': model.coef_[0].tolist(), 'intercept': float(model.intercept_[0]),
              'iterations': model.n_iter_.tolist(), 'C': 1., 'penalty': 'l2', 'solver': 'lbfgs',
              'max_iter': 2000, 'class_weight': None, 'random_state': 42,
              'columns': ['visual_probability', 'sensor_probability'],
              'input_precision': 'float64 saved probabilities', 'postfusion_calibration': False}
    assert np.max(abs(f2_probability(x, result) - model.predict_proba(x)[:, 1])) < 1e-12
    return result


def f2_probability(probabilities, model):
    x = np.asarray(probabilities, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 2:
        raise ValueError('F2 requires visual and sensor columns in that order')
    return expit(x @ np.asarray(model['coefficient']) + model['intercept'])


def checked_records(records, expected_ids, lookup, probability_key, fit_id=None):
    ids = [int(r['episode_index']) for r in records]
    expected = list(map(int, expected_ids))
    if len(ids) != len(set(ids)) or set(ids) != set(expected) or len(expected) != len(set(expected)):
        raise ValueError('Duplicate or mismatched prediction identities')
    keyed = {int(r['episode_index']): r for r in records}
    ordered = [keyed[e] for e in expected]
    for e, r in zip(expected, ordered):
        if int(r['label']) != int(lookup[e]['label']):
            raise ValueError('Native label mismatch')
        if fit_id is not None and r['fit_id'] != fit_id:
            raise ValueError('Prediction fitted-role mismatch')
        p = float(r[probability_key])
        if not np.isfinite(p) or not 0 <= p <= 1:
            raise ValueError('Invalid prediction probability')
    return ordered


def verify_meta_isolation(job, meta_ids, outer_ids, lookup):
    meta, outer = set(meta_ids), set(outer_ids)
    if not meta or meta & outer:
        raise ValueError('Meta/outer episode overlap')
    fit = set(sum((list(job['ids'][k]) for k in ['T', 'V', 'C']), []))
    if meta != set(job['ids']['A']) or fit & meta or fit & outer:
        raise ValueError('Meta/outer contaminated by fitting, selection or calibration')
    groups = lambda ids: {int(lookup[e]['canonical_task_id']) for e in ids}
    if groups(meta) & groups(fit) or groups(meta) & groups(outer) or groups(fit) & groups(outer):
        raise ValueError('Meta/outer task-group leakage')
    return {'meta_N': len(meta), 'outer_N': len(outer), 'meta_tasks': sorted(groups(meta)),
            'outer_tasks': sorted(groups(outer)), 'fit_tasks': sorted(groups(fit)), 'passed': True}


def vector_identity(ids, probabilities):
    rows = sorted(zip(map(int, ids), map(float, probabilities)))
    return signature(rows)


def sensor_records(context, seed, job_id):
    run = protocol()['legacy_run_id']
    root = PROJECT / '06_training_experiments/sensor_baselines/runs' / run / f'seed{seed}' / job_id
    receipt = read_json(root / 'COMPLETE.json')
    from .data import old_signature
    if receipt['seed'] != seed or receipt['fit_id'] != job_id or receipt['split_sha256'] != old_signature(context['jobs'][job_id]):
        raise ValueError('Historical sensor fitted-role identity mismatch')
    if receipt['feature_sha256'] != context['verification']['sensor']['sha256']:
        raise ValueError('Historical sensor feature identity mismatch')
    for source, expected_sha in receipt['source_code'].items():
        if sha256(resolve(source)) != expected_sha:
            raise ValueError('Historical sensor source identity mismatch')
    if sha256(root / 'predictions.json') != receipt['prediction_sha256']:
        raise ValueError('Historical sensor prediction hash mismatch')
    if sha256(root / 'S3_MODEL.json') != receipt['S3_checkpoint_sha256']:
        raise ValueError('Historical canonical LR state hash mismatch')
    if sha256(root / 'S2_MODEL.joblib') != receipt['S2_checkpoint_sha256']:
        raise ValueError('Historical HGB state hash mismatch')
    records = checked_records(read_json(root / 'predictions.json'), context['jobs'][job_id]['ids']['A'],
                              context['lookup'], 'S3_probability', job_id)
    return records, {'fit_id': job_id, 'prediction_path': relative(root / 'predictions.json'),
                     'prediction_sha256': receipt['prediction_sha256'],
                     'S3_model_path': relative(root / 'S3_MODEL.json'),
                     'S3_model_sha256': receipt['S3_checkpoint_sha256'],
                     'S2_model_sha256': receipt['S2_checkpoint_sha256']}


def visual_records(context, condition, seed, job_id, outer=False):
    root = fit_root(condition, seed, job_id)
    receipt = read_json(root / 'COMPLETE.json')
    if receipt['condition'] != condition or receipt['seed'] != seed or receipt['fit_id'] != job_id:
        raise ValueError('Visual fitted-role identity mismatch')
    if sha256(resolve(receipt.get('best_checkpoint_path', relative(root / 'BEST_MODEL.pt')))) != receipt['best_checkpoint_sha256']:
        raise ValueError('Visual selected checkpoint hash mismatch')
    if receipt['executed_epochs'] != protocol()['epochs'][condition]:
        raise ValueError('Incomplete declared training budget')
    name = 'OUTER_PREDICTIONS.json' if outer else 'predictions.json'
    key = 'outer_prediction_sha256' if outer else 'prediction_sha256'
    if sha256(root / name) != receipt[key]:
        raise ValueError('Visual prediction hash mismatch')
    expected = context['jobs'][f"outer{receipt['outer']}_final"]['ids']['A'] if outer else context['jobs'][job_id]['ids']['A']
    records = checked_records(read_json(root / name), expected, context['lookup'], 'probability', job_id)
    calibration = read_json(root / 'CALIBRATOR.json')
    return records, {'fit_id': job_id, 'prediction_path': relative(root / name),
                     'calibrator_path': relative(root / 'CALIBRATOR.json'),
                     'calibrator_sha256': sha256(root / 'CALIBRATOR.json'),
                     'calibration_slope': float(calibration['coefficient'][0]),
                     'calibration_intercept': float(calibration['intercept']),
                     'prediction_sha256': receipt[key], 'checkpoint_sha256': receipt['best_checkpoint_sha256'],
                     'selected_epoch': receipt['selected_epoch'], 'executed_epochs': receipt['executed_epochs']}


def weighted_ap_kernel(y, p, group_index):
    order = np.argsort(-p, kind='stable')
    scores = p[order]
    ends = np.r_[np.flatnonzero(np.diff(scores) != 0), len(scores)-1]
    return np.asarray(y)[order], np.asarray(group_index)[order], ends


def weighted_ap(kernel, counts):
    y, gi, ends = kernel
    weights = counts[gi]
    tp = np.cumsum(weights*y)[ends]
    denominator = np.cumsum(weights)[ends]
    if tp[-1] == 0:
        return None
    precision = np.divide(tp, denominator, out=np.zeros_like(tp, dtype=float), where=denominator > 0)
    return float(np.sum(np.diff(np.r_[0., tp])*precision) / tp[-1])


def paired_uncertainty(y, treatment, control, tasks, repeats=2000, seed=20261111):
    """Paired task resampling of fixed scores. No seed averaging or model refits."""
    y = np.asarray(y, dtype=int); a = np.asarray(treatment, dtype=float); b = np.asarray(control, dtype=float)
    tasks = np.asarray(tasks); groups, gi = np.unique(tasks, return_inverse=True)
    if len(groups) < 2 or set(np.unique(y)) != {0, 1}:
        return {'status': 'INSUFFICIENT GROUP/CLASS SUPPORT', 'task_N': len(groups)}
    kernels = [[weighted_ap_kernel(target, score, gi) for target, score in [(y, p), (1-y, 1-p)]] for p in [a, b]]
    rng = np.random.default_rng(seed); draws = []
    for _ in range(repeats):
        counts = np.bincount(rng.integers(len(groups), size=len(groups)), minlength=len(groups))
        vals = [[weighted_ap(k, counts) for k in arm] for arm in kernels]
        if any(v is None for arm in vals for v in arm):
            continue
        delta_failure = vals[0][0] - vals[1][0]
        delta_success = vals[0][1] - vals[1][1]
        draws.append([(delta_failure+delta_success)/2, delta_failure, delta_success])
    ma, mb = metrics(y, a), metrics(y, b)
    result = {'unit': 'canonical_task_id', 'task_N': len(groups), 'requested': repeats,
              'valid': len(draws), 'discarded_single_class': repeats-len(draws), 'seed': seed,
              'scope': 'fixed fitted models and observed task clusters; excludes refitting, seed variability, donor selection, session/operator uncertainty',
              'multiplicity': 'exploratory; no multiple-comparison adjustment'}
    if not draws:
        result['status'] = 'NO VALID RESAMPLES'; return result
    for j, metric in enumerate(['macro_AP', 'AP_failure', 'AP_success']):
        lo, hi = np.quantile(np.asarray(draws)[:, j], [.025, .975])
        result[metric] = {'difference': ma[metric]-mb[metric], 'lower95': float(lo), 'upper95': float(hi),
                          'interpretation': 'positive conditional interval' if lo > 0 else 'negative conditional interval' if hi < 0 else 'inconclusive; not equivalence'}
    return result


def evaluate_scores(records):
    y = np.asarray([r['label'] for r in records], dtype=int)
    reports = {}
    for model in MODELS:
        p = np.asarray([r[model] for r in records], dtype=float)
        reports[model] = metrics(y, p)
        independent_check(y, p, reports[model])
    if all(r.get('raw_visual') is not None for r in records):
        raw = expit(np.asarray([r['raw_visual'] for r in records], dtype=float))
        reports['uncalibrated_visual'] = metrics(y, raw)
        independent_check(y, raw, reports['uncalibrated_visual'])
    return reports



def ranking_diagnostic(records):
    if not all(r.get('raw_visual') is not None for r in records):
        return {'status': 'RAW SCORES UNAVAILABLE'}
    raw = np.asarray([r['raw_visual'] for r in records], dtype=float)
    calibrated = np.asarray([r['visual'] for r in records], dtype=float)
    y = np.asarray([r['label'] for r in records], dtype=int)
    before, after = metrics(y, expit(raw)), metrics(y, calibrated)
    variable = len(np.unique(raw)) > 1 and len(np.unique(calibrated)) > 1
    return {'status': 'COMPLETE', 'score_spearman': float(spearmanr(raw, calibrated).statistic) if variable else None,
            'score_kendall_tau_b': float(kendalltau(raw, calibrated).statistic) if variable else None,
            'raw_macro_AP': before['macro_AP'], 'calibrated_macro_AP': after['macro_AP'],
            'macro_AP_delta': after['macro_AP']-before['macro_AP'],
            'raw_AP_failure': before['AP_failure'], 'calibrated_AP_failure': after['AP_failure'],
            'raw_AP_success': before['AP_success'], 'calibrated_AP_success': after['AP_success'],
            'interpretation': 'Within one positive-slope sigmoid, ranks should be preserved apart from numeric ties; pooled folds use distinct calibrated maps and may reorder cross-fold scores.'}


def verify_matched_sensor(meta_a, meta_b, outer_a, outer_b):
    """Both fitting and assessment vectors must match, including exact episode IDs."""
    for role, a, b, key in [('meta', meta_a, meta_b, 'sensor_probability'),
                           ('outer', outer_a, outer_b, 'sensor_LR')]:
        if vector_identity([r['episode_index'] for r in a], [r[key] for r in a]) != vector_identity([r['episode_index'] for r in b], [r[key] for r in b]):
            raise ValueError(f'Paired visual arms use different {role} sensor vectors or identities')
    return True

def evaluate_one(context, condition, seed, outer):
    p = protocol(); pilot = condition.endswith('100')
    final_id = f'outer{outer}_final'
    base_id = p['pilot']['base_job_id'] if pilot else final_id
    inner_ids = [base_id] if pilot else [f'outer{outer}_inner{i}' for i in p['inner_folds']]
    required = sorted(set(inner_ids + [base_id]))
    missing = [relative(fit_root(condition, seed, j) / 'COMPLETE.json') for j in required
               if not (fit_root(condition, seed, j) / 'COMPLETE.json').exists()]
    if missing:
        return None, {'condition': condition, 'seed': seed, 'outer': outer,
                      'status': 'PENDING VISUAL FITS', 'missing_completion_receipts': missing}
    root = STUDY / '09_f2_fusion' / condition / f'seed{seed}' / f'outer{outer}'
    # Deliberately do not open outer probabilities or labels until FIT_LOCK exists.
    outer_ids = context['jobs'][final_id]['ids']['A']
    meta = []; lineage = []; isolation = []
    for j in inner_ids:
        visual, vi = visual_records(context, condition, seed, j)
        sensor, si = sensor_records(context, seed, j)
        ids = [r['episode_index'] for r in visual]
        isolation.append(verify_meta_isolation(context['jobs'][j], ids, outer_ids, context['lookup']))
        assert ids == [r['episode_index'] for r in sensor]
        for v, s in zip(visual, sensor):
            meta.append({'episode_index': v['episode_index'], 'fit_id': j, 'label': v['label'],
                         'task_id': context['lookup'][v['episode_index']]['canonical_task_id'],
                         'visual_probability': v['probability'], 'sensor_probability': s['S3_probability']})
        lineage.append({'visual': vi, 'sensor': si})
    ids = [r['episode_index'] for r in meta]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicated meta episode')
    if not pilot:
        final = context['jobs'][final_id]
        expected = set(sum((list(final['ids'][k]) for k in ['T', 'V', 'C']), []))
        if set(ids) != expected:
            raise ValueError('Incomplete three-inner OOF coverage')
    lock_id = signature({'condition': condition, 'seed': seed, 'outer': outer, 'meta': meta,
                         'protocol': p, 'lineage': lineage})
    if (root / 'FIT_LOCK.json').exists():
        lock = read_json(root / 'FIT_LOCK.json')
        if lock['identity'] != lock_id or sha256(root / 'F2_COEFFICIENTS.json') != lock['coefficient_sha256'] or sha256(root / 'META_TRAINING_PREDICTIONS.json') != lock['meta_sha256']:
            raise ValueError('Completed F2 fitting evidence changed')
        model = read_json(root / 'F2_COEFFICIENTS.json')
    else:
        x = np.asarray([[r['visual_probability'], r['sensor_probability']] for r in meta])
        model = fitted_f2(x, [r['label'] for r in meta])
        immutable_json(root / 'META_TRAINING_PREDICTIONS.json', meta)
        immutable_json(root / 'F2_COEFFICIENTS.json', model)
        immutable_json(root / 'META_ISOLATION.json', isolation)
        immutable_json(root / 'FIT_LOCK.json', {'utc': utc(), 'identity': lock_id,
                       'coefficient_sha256': sha256(root / 'F2_COEFFICIENTS.json'),
                       'meta_sha256': sha256(root / 'META_TRAINING_PREDICTIONS.json'),
                       'outer_prediction_records_loaded_before_fit': False,
                       'outer_labels_used_in_fitting': False,
                       'meta_bank': 'single group-held-out bank' if pilot else 'complete three-inner OOF bank',
                       'meta_N': len(meta), 'lineage': lineage,
                       'sensor_policy': p['sensor'], 'threshold': .5})
    # Only now unblind evaluation inputs. Canonical pilot sensor outer refit is intentional.
    visual, vi = visual_records(context, condition, seed, base_id, outer=pilot)
    sensor, si = sensor_records(context, seed, final_id)
    legacy = PROJECT / '06_training_experiments/visual_frozen/runs' / p['legacy_run_id'] / f'seed{seed}' / final_id
    old_receipt = read_json(legacy / 'COMPLETE.json')
    if sha256(legacy / 'predictions.json') != old_receipt['prediction_sha256']:
        raise ValueError('Historical V1 reference changed')
    old = checked_records(read_json(legacy / 'predictions.json'), outer_ids, context['lookup'], 'probability', final_id)
    assert [r['episode_index'] for r in visual] == [r['episode_index'] for r in sensor] == outer_ids
    x = np.asarray([[v['probability'], s['S3_probability']] for v, s in zip(visual, sensor)])
    fused = f2_probability(x, model); records = []
    for v, s, h, pf in zip(visual, sensor, old, fused):
        e = int(v['episode_index']); y = int(v['label']); pv, ps = float(v['probability']), float(s['S3_probability'])
        records.append({'episode_index': e, 'task_id': int(context['lookup'][e]['canonical_task_id']),
                        'label': y, 'condition': condition, 'seed': seed, 'outer': outer,
                        'visual': pv, 'sensor_LR': ps, 'average': (pv+ps)/2, 'F2': float(pf),
                        'historical_HGB': float(s['S2_probability']), 'historical_V1': float(h['probability']),
                        'raw_visual': float(v['raw']) if 'raw' in v else None,
                        'sensor_error_corrected_by_visual': bool((ps >= .5) != y and (pv >= .5) == y),
                        'sensor_correct_broken_by_visual': bool((ps >= .5) == y and (pv >= .5) != y),
                        'sensor_error_corrected_by_F2': bool((ps >= .5) != y and (pf >= .5) == y),
                        'sensor_correct_broken_by_F2': bool((ps >= .5) == y and (pf >= .5) != y)})
    assessment = {'condition': condition, 'seed': seed, 'outer': outer, 'status': 'COMPLETE',
                  'evaluation_scope': 'single-bank exploratory pilot' if pilot else 'complete three-inner OOF F2',
                  'meta_N': len(meta), 'assessment_N': len(records), 'task_N': len({r['task_id'] for r in records}),
                  'metrics': evaluate_scores(records), 'f2_coefficients': model,
                  'calibration_ranking': ranking_diagnostic(records),
                  'visual_identity': vi, 'sensor_identity': si, 'fit_lock': relative(root / 'FIT_LOCK.json'),
                  'assessment_ids_sha256': signature(sorted(outer_ids)),
                  'sensor_vector_sha256': vector_identity(outer_ids, [r['sensor_LR'] for r in records]),
                  'meta_sensor_vector_sha256': vector_identity(ids, [r['sensor_probability'] for r in meta]),
                  'HGB_comparison': 'secondary retained historical outer-refit baseline; never used inside F2',
                  'pilot_sensor_semantics': 'inner0 source sensor for meta; distinct outer0_final source sensor for test; identical across paired arms' if pilot else None}
    immutable_json(root / 'OUTER_PREDICTIONS.json', records)
    immutable_json(root / 'metrics.json', assessment)
    immutable_json(root / 'COMPLETE.json', {'identity': lock_id, 'prediction_sha256': sha256(root / 'OUTER_PREDICTIONS.json'),
                                        'metrics_sha256': sha256(root / 'metrics.json')})
    return assessment, None


def cohort_contrasts(records, p):
    y = [r['label'] for r in records]; tasks = [r['task_id'] for r in records]
    pairs = [('F2', 'sensor_LR'), ('F2', 'visual'), ('F2', 'average'),
             ('F2', 'historical_HGB'), ('F2', 'historical_V1')]
    return {a+'_minus_'+b: paired_uncertainty(y, [r[a] for r in records], [r[b] for r in records], tasks,
                p['uncertainty']['draws'], p['uncertainty']['seed']) for a, b in pairs}


def summarize(completed, p):
    cohorts = []; keyed = {}; meta_banks = {}; fit_lineages = {}
    for item in completed:
        root = STUDY / '09_f2_fusion' / item['condition'] / f"seed{item['seed']}" / f"outer{item['outer']}"
        records = read_json(root / 'OUTER_PREDICTIONS.json')
        keyed[(item['condition'], item['seed'], str(item['outer']))] = records
        meta_banks[(item['condition'], item['seed'], str(item['outer']))] = read_json(root / 'META_TRAINING_PREDICTIONS.json')
        fit_lineages[(item['condition'], item['seed'], str(item['outer']))] = read_json(root / 'FIT_LOCK.json')['lineage']
        cohorts.append({**item, 'paired_contrasts': cohort_contrasts(records, p)})
    for condition in p['twenty_epoch']['conditions']:
        for seed in p['seeds']:
            if not all((condition, seed, str(k)) in keyed for k in p['outer_folds']):
                continue
            records = sum((keyed[(condition, seed, str(k))] for k in p['outer_folds']), [])
            if len(records) != len({r['episode_index'] for r in records}):
                raise ValueError('Overlapping outer assessments')
            keyed[(condition, seed, 'pooled3')] = records
            fold_metrics = [x['metrics'] for x in completed if x['condition'] == condition and x['seed'] == seed]
            cohorts.append({'condition': condition, 'seed': seed, 'outer': 'pooled3', 'status': 'COMPLETE',
                            'evaluation_scope': 'three outer folds pooled; not a larger cross-seed sample',
                            'assessment_N': len(records), 'task_N': len({r['task_id'] for r in records}),
                            'metrics': evaluate_scores(records),
                            'calibration_ranking': ranking_diagnostic(records),
                            'mean_fold_metrics': {m: {k: float(np.mean([f[m][k] for f in fold_metrics])) for k in ['macro_AP','AP_failure','AP_success','AUROC']} for m in MODELS},
                            'paired_contrasts': cohort_contrasts(records, p)})
    arm_contrasts = []
    for treatment, control in [('FULL20','FROZEN20'), ('FULL100','FROZEN100'),
                               ('DONOR20','FROZEN20'), ('DONOR100','FROZEN100')]:
        for (c, seed, fold), a in list(keyed.items()):
            if c != treatment or (control, seed, fold) not in keyed:
                continue
            b = keyed[(control, seed, fold)]; lookup = {r['episode_index']: r for r in b}
            if set(lookup) != {r['episode_index'] for r in a}:
                raise ValueError('Matched contrast assessment mismatch')
            b = [lookup[r['episode_index']] for r in a]
            folds = p['outer_folds'] if fold == 'pooled3' else [fold]
            for k in folds:
                ma = meta_banks[(treatment, seed, str(k))]
                mb = meta_banks[(control, seed, str(k))]
                verify_matched_sensor(ma, mb, a, b)
                sa = [row['sensor'] for row in fit_lineages[(treatment, seed, str(k))]]
                sb = [row['sensor'] for row in fit_lineages[(control, seed, str(k))]]
                if sa != sb:
                    raise ValueError('Paired meta sensor model/prediction lineage mismatch')
            result = {'treatment': treatment, 'control': control, 'seed': seed, 'fold': fold,
                      'assessment_N': len(a), 'same_sensor_verified': True, 'same_meta_sensor_verified': True}
            for model in ['visual', 'F2']:
                result[model] = paired_uncertainty([r['label'] for r in a], [r[model] for r in a],
                        [r[model] for r in b], [r['task_id'] for r in a], p['uncertainty']['draws'], p['uncertainty']['seed'])
            result['task_changes'] = []
            for task in sorted({r['task_id'] for r in a}):
                aa = [r for r in a if r['task_id'] == task]
                bb = [r for r in b if r['task_id'] == task]
                y = [r['label'] for r in aa]
                changes = {m: metrics(y, [r[m] for r in aa])['macro_AP']-metrics(y, [r[m] for r in bb])['macro_AP'] for m in ['visual','F2']} if len(set(y)) == 2 else None
                result['task_changes'].append({'task_id': task, 'N': len(aa), 'macro_AP_differences': changes})
            arm_contrasts.append(result)
    task_rows = []
    for (condition, seed, fold), records in keyed.items():
        if fold == 'pooled3':
            continue
        for task in sorted({r['task_id'] for r in records}):
            rows = [r for r in records if r['task_id'] == task]; y = [r['label'] for r in rows]
            task_rows.append({'condition': condition, 'seed': seed, 'outer': fold, 'task_id': task,
                'N': len(rows), 'failures': sum(y), 'both_classes': len(set(y)) == 2,
                'macro_AP': {m: metrics(y, [r[m] for r in rows])['macro_AP'] for m in ['visual','sensor_LR','F2','historical_HGB']} if len(set(y)) == 2 else None,
                'sensor_errors_corrected_by_visual': sum(r['sensor_error_corrected_by_visual'] for r in rows),
                'sensor_correct_broken_by_visual': sum(r['sensor_correct_broken_by_visual'] for r in rows),
                'sensor_errors_corrected': sum(r['sensor_error_corrected_by_F2'] for r in rows),
                'sensor_correct_broken': sum(r['sensor_correct_broken_by_F2'] for r in rows)})
    return cohorts, arm_contrasts, task_rows


def evaluate_available(context=None):
    from .data import load_context
    p = protocol(); context = context or load_context(); completed = []; pending = []
    with exclusive_lock(STUDY / '13_reproducibility/runtime/fusion.lock'):
        for condition in p['epochs']:
            seeds = [p['pilot']['seed']] if condition.endswith('100') else p['seeds']
            folds = [p['pilot']['outer']] if condition.endswith('100') else p['outer_folds']
            for seed in seeds:
                for outer in folds:
                    done, missing = evaluate_one(context, condition, seed, outer)
                    if done is not None: completed.append(done)
                    if missing is not None: pending.append(missing)
        identity = signature({'completed': completed, 'pending': pending, 'protocol': p,
                              'evaluation_code': sha256(Path(__file__))})
        path = STUDY / '11_metrics_and_statistics/CURRENT_RESULTS.json'
        if path.exists() and read_json(path).get('identity') == identity:
            return read_json(path)
        cohorts, contrasts, tasks = summarize(completed, p)
        result = {'utc': utc(), 'identity': identity, 'status': 'COMPLETE' if not pending else 'PARTIAL_OR_PENDING',
                  'completed_fusion_cohorts': len(completed), 'cohorts': cohorts, 'matched_contrasts': contrasts,
                  'pending': pending, 'uncertainty': p['uncertainty'], 'no_quality_gate': True}
        write_json(STUDY / '11_metrics_and_statistics/PER_TASK_DIAGNOSTICS.json', tasks)
        write_json(path, result)
        return result
