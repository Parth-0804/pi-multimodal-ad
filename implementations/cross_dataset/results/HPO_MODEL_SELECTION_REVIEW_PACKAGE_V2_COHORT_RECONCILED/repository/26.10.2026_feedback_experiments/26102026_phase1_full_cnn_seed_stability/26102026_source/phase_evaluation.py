"""Reuse historical sensor/F2 primitives with directly keyed, held-out banks."""
from collections import defaultdict
from pathlib import Path
import json

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

from phase_common import ROOT, STUDY, EXEC, EVIDENCE, config, read, write, sha, signature, utc
from phase_model import sensor_fit, sensor_predict, stacker, fused
from phase_training import folder_for, run_identity
from phase_metrics import metrics, aligned_keys


def sensor(job):
    folder = EXEC / f"26102026_sensor_outer{job['outer_fold_original']+1}_{job['role']}"
    path = folder / 'PHASE1_SENSOR_PREDICTIONS.json'
    identity = read(EVIDENCE / 'PHASE1_SENSOR_INPUT_IDENTITY.json')
    assert sha(STUDY/'shared_cache/sensor_statistics.npy') == identity['sha256']
    if path.exists() and (folder/'PHASE1_SENSOR_MODEL.json').exists():
        record = read(folder/'PHASE1_SENSOR_MODEL.json')
        assert record['input_sha256'] == identity['sha256']
        assert record['predictions_sha256'] == sha(path)
        return read(path)
    rows = read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    x = np.load(STUDY/'shared_cache/sensor_statistics.npy', allow_pickle=False)
    y = np.array([row['failure'] for row in rows])
    model = sensor_fit(x[job['G']], y[job['G']], x[job['C']], y[job['C']])
    raw, p = sensor_predict(x[job['predict']], model)
    predictions = [{k: rows[i][k] for k in ['sample_id', 'recording_id', 'segment_id', 'failure']} for i in job['predict']]
    for row, logit, probability in zip(predictions, raw, p):
        row.update(raw_sensor_logit=float(logit), p_sensor=float(probability))
    write(path, predictions)
    write(folder/'PHASE1_SENSOR_MODEL.json', {'model': model, 'job_index': job['job_index'],
        'G': job['G'], 'C': job['C'], 'prediction': job['predict'], 'input_sha256': identity['sha256'],
        'predictions_sha256': sha(path)})
    return predictions


def visual(job, seed, arm, short=False):
    folder = folder_for(arm, seed, job)
    done = read(folder/'PHASE1_FIT_COMPLETE.json')
    assert done['fit_identity'] == run_identity(arm, seed, job)
    assert sha(folder/'PHASE1_PREDICTIONS.json') == done['predictions_sha256']
    assert sha(folder/'PHASE1_BEST_MODEL.pt') == done['selected_model_sha256']
    name = 'PHASE1_MATCHED_SHORT_PREDICTIONS.json' if short else 'PHASE1_PREDICTIONS.json'
    if short:
        assert sha(folder/name) == done['short_predictions_sha256']
    result = read(folder/name)
    expected = read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    expected_keys = [expected[i]['sample_id'] for i in job['predict']]
    aligned_keys(result, expected_keys)
    lookup = {row['sample_id']: row for row in expected}
    for row in result:
        assert all(row[k] == lookup[row['sample_id']][k] for k in ['failure', 'recording_id', 'segment_id'])
    return result


def assert_oof_lineage(job, predictions, cohort):
    expected = [cohort[i]['sample_id'] for i in job['predict']]
    aligned_keys(predictions, expected)
    assessment = {r['recording_id'] for r in predictions}
    for scope in ['training', 'validation', 'G', 'C']:
        used = {cohort[i]['recording_id'] for i in job[scope]}
        assert not assessment & used, ('OOF_BRANCH_LEAKAGE', scope)


def evaluate_fold(seed, outer, method):
    arm = 'C_full_finetuned16' if method == 'C_full_finetuned16' else 'B_long_frozen16'
    short = method == 'A_r_matched_short'
    jobs = [j for j in read(EVIDENCE/'PHASE1_FIT_PLAN.json') if j['outer_fold_original'] == outer]
    final_job = next(j for j in jobs if j['role'] == 'outer_assessment')
    folder = EXEC/f'26102026_fusion_seed{seed}_{method}_outer{outer+1}'
    dest = folder/'PHASE1_OUTER_PREDICTIONS.json'
    receipt = folder/'PHASE1_F2_COMPLETE.json'
    if receipt.exists():
        record = read(receipt)
        assert sha(dest) == record['predictions_sha256']
        assert sha(folder/'PHASE1_OOF_BRANCH_PREDICTIONS.json') == record['OOF_sha256']
        assert sha(folder/'PHASE1_F2_MODEL.json') == record['model_sha256']
        return read(dest)
    oof = []
    for job in jobs:
        if job['role'] == 'outer_assessment':
            continue
        vp = visual(job, seed, arm, short=short)
        assert_oof_lineage(job, vp, read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json'))
        sp = aligned_keys(sensor(job), [r['sample_id'] for r in vp])
        for row in vp:
            item = dict(row, p_sensor=sp[row['sample_id']]['p_sensor'])
            assert item['failure'] == sp[row['sample_id']]['failure']
            oof.append(item)
    cohort = read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    allowed_recordings = set(final_job['A_recordings'])
    expected_oof = [r['sample_id'] for r in cohort if r['recording_id'] in allowed_recordings]
    aligned_keys(oof, expected_oof)
    model = stacker(np.array([[r['p_visual'], r['p_sensor']] for r in oof]), np.array([r['failure'] for r in oof]))
    outer_v = visual(final_job, seed, arm, short=short)
    assert_oof_lineage(final_job, outer_v, cohort)
    outer_s = aligned_keys(sensor(final_job), [r['sample_id'] for r in outer_v])
    output = [dict(r, p_sensor=outer_s[r['sample_id']]['p_sensor'], seed=seed, outer_fold=outer,
                   method=method) for r in outer_v]
    probabilities = fused(np.array([[r['p_visual'], r['p_sensor']] for r in output]), model)
    for row, probability in zip(output, probabilities):
        row['p_fused'] = float(probability)
    assert not allowed_recordings & {r['recording_id'] for r in output}
    write(folder/'PHASE1_F2_MODEL.json', {'model': model, 'seed': seed, 'outer_fold': outer, 'method': method,
        'OOF_training_sample_ids': [r['sample_id'] for r in oof], 'OOF_membership_sha256': signature(expected_oof),
        'feature_columns': ['p_visual', 'p_sensor'], 'outer_test_used_for_fitting': False,
        'short_reference': short, 'fit_metadata_source': 'matched training-side base-model banks'})
    write(folder/'PHASE1_OOF_BRANCH_PREDICTIONS.json', oof)
    write(dest, output)
    write(receipt, {'predictions_sha256': sha(dest), 'OOF_sha256': sha(folder/'PHASE1_OOF_BRANCH_PREDICTIONS.json'),
        'model_sha256': sha(folder/'PHASE1_F2_MODEL.json'), 'completed_utc': utc()})
    return output


def paired_uncertainty(banks, rows, bootstrap=2000, treatment='C_full_finetuned16', control='B_long_frozen16'):
    seeds = config()['seeds']
    groups = sorted(set(r['recording_id'] for r in rows))
    indices = [np.array([i for i, r in enumerate(rows) if r['recording_id'] == group]) for group in groups]
    y = np.array([r['failure'] for r in rows])
    rng = np.random.default_rng(config()['bootstrap_seed'])
    distribution = {name: [] for name in ['visual_AP', 'fusion_AP', 'visual_AUROC', 'fusion_AUROC']}
    for _ in range(bootstrap):
        ix = np.concatenate([indices[i] for i in rng.integers(len(groups), size=len(groups))])
        if len(np.unique(y[ix])) < 2:
            continue
        for kind, column in [('visual', 'p_visual'), ('fusion', 'p_fused')]:
            for metric_name, function in [('AP', average_precision_score), ('AUROC', roc_auc_score)]:
                difference = [function(y[ix], banks[(seed, treatment)][column][ix]) -
                              function(y[ix], banks[(seed, control)][column][ix]) for seed in seeds]
                distribution[kind+'_'+metric_name].append(float(np.mean(difference)))
    return {name: {'mean': float(np.mean(values)), 'lower95': float(np.quantile(values, .025)),
                   'upper95': float(np.quantile(values, .975)), 'valid_recording_bootstrap_draws': len(values),
                   'scope': 'mean paired difference over fixed three seeds; same recording draw across seeds; conditional on fitted models'}
            for name, values in distribution.items()}


def summarize(complete=False):
    c = config()
    fit_plan = read(EVIDENCE/'PHASE1_FIT_PLAN.json')
    fits = []
    for seed in c['seeds']:
        for job in fit_plan:
            for arm in c['arms']:
                path = folder_for(arm, seed, job)/'PHASE1_FIT_COMPLETE.json'
                if path.exists():
                    d = read(path)
                    fits.append({'seed': seed, 'job_index': job['job_index'], 'outer_fold': job['outer_fold_original'],
                                 'role': job['role'], 'arm': arm, 'executed_epochs': d['executed_epochs'],
                                 'selected_epoch': d['best']['epoch'], 'training_seconds': d['training_seconds'],
                                 'inference_calibration_seconds': d['inference_calibration_seconds']})
    write(EXEC/'PHASE1_COMPLETED_FIT_INDEX.json', fits)
    report = ROOT/'26102026_reports/PHASE1_TRAINING_RESULTS.md'
    title = 'COMPLETE' if len(fits) == 150 else 'PARTIAL — training in progress'
    text = f'# Phase 1 training results — {title}\n\nUpdated {utc()}. Completed {len(fits)}/150 required fits.\n\n'
    text += '| Model | Seed | Outer fold | Role | Executed epochs | Selected epoch | Training hours |\n|---|---:|---:|---|---:|---:|---:|\n'
    for d in fits:
        text += f"| {d['arm']} | {d['seed']} | {d['outer_fold']+1} | {d['role']} | {d['executed_epochs']} | {d['selected_epoch']} | {d['training_seconds']/3600:.4f} |\n"
    diagnostics = []
    text += '\n## Completed-fit convergence observations\n\n'
    for seed in c['seeds']:
        for job in fit_plan:
            for arm in c['arms']:
                folder = folder_for(arm, seed, job)
                if not (folder/'PHASE1_FIT_COMPLETE.json').exists():
                    continue
                done = read(folder/'PHASE1_FIT_COMPLETE.json')
                history = done['history']
                observed_gpu = [r['GPU_compute_percent'] for r in history if r['GPU_compute_percent'] is not None]
                record = {'arm': arm, 'seed': seed, 'job_index': job['job_index'],
                    'training_loss_first': history[0]['training_loss'], 'training_loss_last': history[-1]['training_loss'],
                    'validation_AP_selected': done['best']['validation_AP'], 'validation_AP_last': history[-1]['validation_AP'],
                    'selected_epoch': done['best']['epoch'], 'executed_epochs': len(history),
                    'budget_reached50': len(history) == 50,
                    'mean_GPU_compute_percent': float(np.mean(observed_gpu)) if observed_gpu else None,
                    'mean_actions_per_second': float(np.mean([r['actions_per_second'] for r in history])),
                    'peak_allocated_GiB': max(r['peak_allocated_bytes'] for r in history)/1024**3}
                diagnostics.append(record)
    write(EXEC/'PHASE1_CURVE_DIAGNOSTICS.json', diagnostics)
    if diagnostics:
        text += '| Model | Seed | Fit | First→last training BCE | Selected→last validation AP | Mean GPU compute | Mean actions/s | Peak allocated GiB |\n|---|---:|---:|---|---|---:|---:|---:|\n'
        for d in diagnostics:
            gpu = 'Unavailable' if d['mean_GPU_compute_percent'] is None else f"{d['mean_GPU_compute_percent']:.2f}%"
            text += f"| {d['arm']} | {d['seed']} | {d['job_index']} | {d['training_loss_first']:.4f}→{d['training_loss_last']:.4f} | {d['validation_AP_selected']:.4f}→{d['validation_AP_last']:.4f} | {gpu} | {d['mean_actions_per_second']:.3f} | {d['peak_allocated_GiB']:.3f} |\n"
        text += '\nDecreasing training loss accompanied by lower final validation AP is evidence compatible with overfitting; it is not proof of its cause. An early selected checkpoint shows that longer execution alone was not beneficial. Reaching50 epochs is a budget boundary, not evidence of convergence or superiority. Numerical failures are reported separately and never counted as valid poor accuracy. Every completed fit has exportable learning-curve PNG and JSON.\n'
    text += '\nEvery fit retains loss/AP/AUROC/LR/time/VRAM/utilization curves in PHASE1_LEARNING_CURVE.json and per-epoch telemetry. Selected checkpoints can precede the minimum25 executed epochs. Incomplete epochs are not counted as completed scientific exposure. Numerical failures are not valid negative accuracy results.\n'
    report.write_text(text)
    if not complete:
        return {'completed_fits': len(fits), 'status': title}
    assert len(fits) == 150
    cohort = read(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    keys = [r['sample_id'] for r in cohort]
    banks, scores, fold_scores = {}, [], []
    for seed in c['seeds']:
        for method in ['A_r_matched_short', *c['arms']]:
            combined = []
            for outer in range(5):
                values = evaluate_fold(seed, outer, method)
                combined += values
                for kind in ['visual', 'sensor', 'fused']:
                    fold_scores.append({'seed': seed, 'method': method, 'outer_fold': outer,
                        'kind': kind, **metrics([v['failure'] for v in values], [v['p_'+kind] for v in values])})
            indexed = aligned_keys(combined, keys)
            ordered = [indexed[k] for k in keys]
            banks[(seed, method)] = {column: np.array([v[column] for v in ordered]) for column in ['p_visual', 'p_sensor', 'p_fused']}
            for kind in ['visual', 'sensor', 'fused']:
                scores.append({'seed': seed, 'method': method, 'kind': kind,
                    **metrics([r['failure'] for r in cohort], banks[(seed, method)]['p_'+kind])})
            write(EXEC/f'PHASE1_POOLED_PREDICTIONS_SEED{seed}_{method}.json', ordered)
    uncertainty = paired_uncertainty(banks, cohort, c['bootstrap_replicates'])
    longer = paired_uncertainty(banks, cohort, c['bootstrap_replicates'], 'B_long_frozen16', 'A_r_matched_short')
    paired_seed_differences = []
    for seed in c['seeds']:
        for kind in ['visual', 'fused']:
            def score(method):
                return next(r['AP'] for r in scores if r['seed'] == seed and r['method'] == method and r['kind'] == kind)
            paired_seed_differences.append({'seed': seed, 'kind': kind,
                'C_minus_B_AP': score('C_full_finetuned16')-score('B_long_frozen16'),
                'B_minus_A_r_AP': score('B_long_frozen16')-score('A_r_matched_short')})
    stability = []
    for method in ['A_r_matched_short', *c['arms']]:
        for kind in ['visual', 'fused']:
            selected = [s for s in scores if s['method'] == method and s['kind'] == kind]
            values = np.array([s['AP'] for s in selected])
            stability.append({'method': method, 'kind': kind, 'AP_mean': float(values.mean()),
                              'AP_sample_sd_across3seeds': float(values.std(ddof=1)), 'AP_each_seed': values.tolist()})
    write(EXEC/'PHASE1_FINAL_METRICS.json', {'pooled': scores, 'fold_metrics': fold_scores,
          'seed_stability': stability, 'paired_C_minus_B': uncertainty, 'paired_B_minus_A_r': longer,
          'paired_AP_differences_each_seed': paired_seed_differences, 'cohort_n': 4530, 'failures': 509,
          'folds_and_seeds_are_not_independent_sampling_units': True})
    fusion_report = '# Phase 1 fusion results — COMPLETE\n\n'
    fusion_report += '| Model | Seed | Pooled visual AP | Pooled F2 AP | Visual AUROC | F2 AUROC |\n|---|---:|---:|---:|---:|---:|\n'
    for seed in c['seeds']:
        for method in ['A_r_matched_short', *c['arms']]:
            v = next(s for s in scores if s['seed'] == seed and s['method'] == method and s['kind'] == 'visual')
            f = next(s for s in scores if s['seed'] == seed and s['method'] == method and s['kind'] == 'fused')
            fusion_report += f"| {method} | {seed} | {v['AP']:.6f} | {f['AP']:.6f} | {v['AUROC']:.6f} | {f['AUROC']:.6f} |\n"
    fusion_report += '\n## Paired C minus B recording-cluster uncertainty\n\n```json\n'+json.dumps(uncertainty, indent=2)+'\n```\n'
    fusion_report += '\n## Paired long B minus reconstructed short A_r\n\n```json\n'+json.dumps(longer, indent=2)+'\n```\n'
    fusion_report += '\n## AP differences by fixed seed\n\n```json\n'+json.dumps(paired_seed_differences, indent=2)+'\n```\n'
    fusion_report += '\nOriginal historical F2 AP0.4472985514 and Frozen16 AP0.2306583150 are contextual, from a different precision/selection/calibration protocol. A_r is the explicitly reconstructed matched short horizon, not overwritten historical A. All main F2 models were refitted on their corresponding inner-held-out probability pairs. The sensor fits are identical across B/C and seeds.\n\nSeed mean/SD, per-fold versus pooled metrics, Brier/log loss and directly keyed probabilities are in PHASE1_FINAL_METRICS.json. Recording-bootstrap intervals condition on fitted models and the exposed dataset; three seeds are descriptive stochastic sensitivity. No robustness, unseen-site or cross-dataset transfer claim follows.\n'
    (ROOT/'26102026_reports/PHASE1_FUSION_RESULTS.md').write_text(fusion_report)
    return {'status': 'COMPLETE', 'scores': scores, 'stability': stability, 'uncertainty': uncertainty,
            'longer_uncertainty': longer, 'paired_seed_differences': paired_seed_differences, 'fits': fits}
