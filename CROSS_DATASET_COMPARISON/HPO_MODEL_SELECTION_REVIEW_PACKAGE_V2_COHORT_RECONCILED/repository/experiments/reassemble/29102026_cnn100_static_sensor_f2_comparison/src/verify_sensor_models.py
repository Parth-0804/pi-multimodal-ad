"""Replay original G/C sensor fits for verification; never replace saved fits."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '16'
os.environ['OMP_NUM_THREADS'] = '1'
# Match original OpenBLAS reduction partitions while bounding this verification
# process to four physical CPU slots; the main GPU study is never paused.
os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[-4:])
import numpy as np
from threadpoolctl import threadpool_info
from common import ROOT, REPO, BASE, STUDY, RUN, read, write, sha, relative, identity, cohort, arm_folder
from original_api import load


def main():
    fusion, _ = load()
    x = np.load(STUDY/'shared_cache/sensor_statistics.npy', allow_pickle=False)
    y = np.array([r['failure'] for r in cohort()])
    receipts = []
    for role, name in [('inner_holdout', '26102026_sensor_outer1_inner_fold_03'),
                       ('outer_assessment', '26102026_sensor_outer1_outer_assessment')]:
        folder = BASE/'26102026_execution/26102026_main_run_01'/name
        saved = read(folder/'PHASE1_SENSOR_MODEL.json')
        replay = fusion.sensor_fit(x[saved['G']], y[saved['G']], x[saved['C']], y[saved['C']])
        assert np.array_equal(replay['mean'], saved['model']['mean'])
        assert np.array_equal(replay['std'], saved['model']['std'])
        raw_error = float(np.max(np.abs(np.array(replay['raw']['coefficient'])-np.array(saved['model']['raw']['coefficient']))))
        intercept_error = abs(replay['raw']['intercept']-saved['model']['raw']['intercept'])
        _, p = fusion.sensor_predict(x[saved['prediction']], replay)
        original = read(folder/'PHASE1_SENSOR_PREDICTIONS.json')
        error = float(np.max(np.abs(p-np.array([r['p_sensor'] for r in original]))))
        assert raw_error < 1e-6 and intercept_error < 1e-6 and error < 1e-6
        receipts.append({'role': role, 'source_model': identity(folder/'PHASE1_SENSOR_MODEL.json'),
            'source_predictions': identity(folder/'PHASE1_SENSOR_PREDICTIONS.json'),
            'gradient_fit_actions': len(saved['G']), 'calibration_actions': len(saved['C']),
            'replay_parameter_max_abs': raw_error, 'replay_raw_intercept_abs': intercept_error,
            'replay_calibrated_probability_max_abs': error, 'numeric_tolerance': 1e-6,
            'normalizer_exact': True, 'original_saved_model_replaced': False, 'passed': True})
        print('SENSOR_REFIT_VERIFIED', role, raw_error, error, flush=True)
    write(ROOT/'03_static_sensor_evidence/ORIGINAL_SENSOR_FIT_REPLAY.json', {'passed': True,
          'verification_replays_only': True, 'fitting_recipe_changed': False, 'receipts': receipts,
          'original_OpenBLAS_reduction_threads_matched': 16,
          'verification_CPU_affinity_count': len(os.sched_getaffinity(0)),
          'numerical_libraries': [{k: os.path.relpath(v, REPO) if k == 'filepath' and v else v
                                    for k,v in info.items()} for info in threadpool_info()],
          'earlier_single_thread_replay_differences_preserved': 'SENSOR_REFIT_DIFFERENCE_DIAGNOSTIC.json'})
    path = arm_folder('finetuned')/'PHASE1_FIRST_EPOCH_GRADIENT_UPDATES.json'
    evidence = read(path)
    assert evidence['all_parameters_trainable'] and evidence['running_statistics_unchanged']
    assert all(r['finite'] for r in evidence['gradient_parameters'].values())
    for scope in ['backbone.embedder.', 'backbone.encoder.stages.0.', 'backbone.encoder.stages.1.',
                  'backbone.encoder.stages.2.', 'backbone.encoder.stages.3.', 'head.']:
        assert any(name.startswith(scope) for name in evidence['changed_state_names'])
        assert any(name.startswith(scope) and item['nonzero'] for name,item in evidence['gradient_parameters'].items())
    write(ROOT/'02_checkpoint_verification/ORIGINAL_FULL_CNN_GRADIENT_EVIDENCE.json',
          {'source': identity(path), 'passed': True, 'original_training_first_epoch_only': True,
           'all_CNN_scopes_and_head_changed': True, 'all_recorded_gradients_finite': True,
           'running_moments_preserved': True, 'data': evidence})


if __name__ == '__main__':main()
