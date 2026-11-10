"""Recover and verify the earliest Section1b static-sensor/OOF calibration recipe."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '16'
os.environ['OMP_NUM_THREADS'] = '1'
os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[-4:])
import sys
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
from common import ROOT, REPO, STUDY, RUN, CONFIG, read, write, identity, sha, relative, cohort, job, utc
sys.path.insert(0, str(REPO/'src'))
from reassemble.section1_models import Standardizer, logistic_fit, calibrate


def main():
    assert not (ROOT/'05_fusion_models/FUSION_FIT_LOCK.json').exists()
    rows, selected = cohort(), job()
    frame = pd.read_parquet(REPO/'runs/reassemble/20260927T154732Z-section1/cohort.parquet')
    x = np.load(STUDY/'shared_cache/sensor_statistics.npy', allow_pickle=False)
    y = frame.failure.to_numpy(dtype=int)
    folder = REPO/'runs/reassemble/20260927T175336Z-section1b/stacking'
    outer_log = read(folder/'outer0.json')
    inner_log = read(folder/'outer0_inner2.json')
    split = read(REPO/'artifacts/reassemble/audits/nested_splits.json')['folds'][0]
    outer_plan = [{'train_recordings': p['train_recordings'], 'validation_recordings': p['validation_recordings']} for p in split['inner']]
    recipes = [('TRAINING_BANK', inner_log['branches']['sensor_statistics'], inner_log['train_recordings'],
                selected['original_inner_prediction_indices'], inner_log['subfolds'], folder/'outer0_inner2.npz'),
               ('OUTER_TEST', outer_log['refits']['sensor_statistics'], split['train_recordings'],
                selected['predict'], outer_plan, folder/'outer0.npz')]
    receipts = []
    for name, log, training_groups, target, plans, source in recipes:
        train = np.flatnonzero(frame.recording_id.isin(training_groups))
        target = np.asarray(target, dtype=int)
        assert not set(frame.iloc[train].recording_id) & set(frame.iloc[target].recording_id)
        C = float(log['selected'])
        best = max(log['inner_AP'], key=lambda c: np.mean(log['inner_AP'][c]))
        assert float(best) == C
        raw_oof = np.full(len(frame), np.nan)
        coverage = set()
        plan_receipts = []
        for p in plans:
            a = np.flatnonzero(frame.recording_id.isin(p['train_recordings']))
            b = np.flatnonzero(frame.recording_id.isin(p['validation_recordings']))
            assert set(a)|set(b) == set(train) and not set(a)&set(b)
            assert not set(frame.iloc[a].recording_id)&set(frame.iloc[b].recording_id)
            assert not coverage & set(b);coverage.update(b.tolist())
            raw_oof[b], _ = logistic_fit(x, y, a, b, C)
            plan_receipts.append({'training_recordings': p['train_recordings'],
                                  'assessment_recordings': p['validation_recordings']})
        assert coverage == set(train) and np.isfinite(raw_oof[train]).all()
        scaler = Standardizer().fit(x[train])
        estimator = LogisticRegression(C=C, class_weight='balanced', max_iter=2000, random_state=0)
        estimator.fit(scaler.transform(x[train]), y[train])
        raw = estimator.decision_function(scaler.transform(x[target]))
        replay, threshold, replay_cal = calibrate(raw_oof[train], y[train], raw)
        original_cal = log['calibration']
        cal_difference = max(abs(replay_cal[k]-original_cal[k]) for k in ['coefficient', 'intercept'])
        assert cal_difference < 1e-5 and abs(threshold-original_cal['threshold']) < 1e-12
        with np.load(source, allow_pickle=False) as z:
            if name == 'TRAINING_BANK':
                assert np.array_equal(z['validation_rows'], target)
                stored = z['probabilities'][:, 1]
            else:
                assert np.array_equal(z['test_rows'], target)
                stored = z['test_branch_probabilities'][:, 1]
        saved_parameter_replay = expit(original_cal['coefficient']*raw+original_cal['intercept'])
        error = float(np.max(abs(saved_parameter_replay-stored)))
        assert error < 1e-5, ('CANONICAL_SENSOR_REPLAY_MISMATCH', name, error)
        model = {'mean': scaler.mean.tolist(), 'std': scaler.std.tolist(),
                 'raw': {'coefficient': estimator.coef_[0].tolist(), 'intercept': float(estimator.intercept_[0]),
                         'C': C, 'balanced': True, 'iterations': estimator.n_iter_.tolist(), 'random_state': 0},
                 'calibrator': original_cal, 'native_threshold': original_cal['threshold']}
        predictions = [dict(sample_id=rows[i]['sample_id'], recording_id=rows[i]['recording_id'],
                            segment_id=rows[i]['segment_id'], failure=rows[i]['failure'],
                            raw_sensor_logit=float(raw[k]), p_sensor=float(stored[k]))
                       for k,i in enumerate(target)]
        model_path = ROOT/f'03_static_sensor_evidence/CANONICAL_{name}_MODEL.json'
        pred_path = ROOT/f'03_static_sensor_evidence/CANONICAL_{name}_PREDICTIONS.json'
        write(model_path, {'model': model, 'training_indices': train.tolist(), 'prediction_indices': target.tolist(),
              'training_sample_ids': [rows[i]['sample_id'] for i in train], 'OOF_calibration_indices': train.tolist(),
              'OOF_calibration_raw_logits': raw_oof[train].tolist(), 'OOF_calibration_splits': plan_receipts,
              'source_prediction_archive': identity(source), 'source_log': identity(source.with_suffix('.json')),
              'reconstructed_original_model_weights': True, 'original_weights_not_saved_by_original_logistic_fit': True,
              'saved_original_probabilities_used_for_scientific_evaluation': True,
              'reconstructed_probability_max_abs': error, 'calibrator_refit_max_abs': cal_difference,
              'native_labels': 'failure=1', 'outer_test_labels_used_for_training_or_calibration': False})
        write(pred_path, {'data': predictions, 'source_archive': identity(source), 'source_column':
              'probabilities[:,1]' if name == 'TRAINING_BANK' else 'test_branch_probabilities[:,1]'})
        receipts.append({'role': name, 'training_actions': len(train), 'prediction_actions': len(target),
                         'selected_C': C, 'native_threshold': threshold, 'OOF_calibration_reproduced': True,
                         'reconstructed_probability_max_abs': error, 'model': identity(model_path),
                         'predictions': identity(pred_path), 'original_source': identity(source)})
        print('CANONICAL_SENSOR_VERIFIED', name, 'C', C, 'error', error, flush=True)
    # Independent tie to the earliest sensor-only prediction bank.
    with np.load(REPO/'runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00.npz', allow_pickle=False) as z:
        earliest = z['p'][selected['predict']]
    sensor = np.array([r['p_sensor'] for r in read(ROOT/'03_static_sensor_evidence/CANONICAL_OUTER_TEST_PREDICTIONS.json')['data']])
    assert np.max(abs(sensor-earliest)) < 1e-5
    write(ROOT/'03_static_sensor_evidence/CANONICAL_SENSOR_VERIFICATION.json',
          {'utc': utc(), 'passed': True, 'earliest_section1_sensor_only_prediction_parity_max_abs': float(np.max(abs(sensor-earliest))),
           'recipes': receipts, 'source': identity(REPO/'src/reassemble/section1_models.py'),
           'original_source_files_modified': False, 'primary_recipe': 'Earliest original Section1b nested OOF-calibrated static sensor',
           'later_clean_CNN_C1_separate_calibration_recipe': 'Retained only as provenance/reference; not substituted for original primary sensor'})
    original_inputs = [REPO/'src/reassemble/section1_models.py', REPO/'src/reassemble/section1b.py',
        REPO/'artifacts/reassemble/audits/nested_splits.json', REPO/'configs/reassemble/section1b.json',
        REPO/'runs/reassemble/20260927T154732Z-section1/cohort.parquet',
        REPO/'runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00.npz',
        folder/'outer0.json', folder/'outer0.npz', folder/'outer0_inner2.json', folder/'outer0_inner2.npz']
    write(RUN/'manifests/CANONICAL_INPUT_IDENTITIES.json', [identity(p) for p in original_inputs])


if __name__ == '__main__':
    with threadpool_limits(limits=16):
        main()
