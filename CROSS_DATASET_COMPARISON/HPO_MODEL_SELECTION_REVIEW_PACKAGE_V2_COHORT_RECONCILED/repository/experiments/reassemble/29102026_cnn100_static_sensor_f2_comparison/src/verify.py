"""Verify original checkpoints, labels, calibration, groups and saved AP first."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '2'

import numpy as np
import torch
from scipy.special import expit
from sklearn.metrics import average_precision_score, roc_auc_score

from common import ROOT, REPO, BASE, COMPARISON, STUDY, EVIDENCE, RUN, CONFIG
from common import read, write, relative, identity, sha, utc, cohort, job, arm_folder, status
from original_api import load

# This is the preserved pre-analysis visual/checkpoint audit. Later canonical
# sensor/F2 clarification has its own independently verified protocol03.
CONFIG = ROOT/'01_experiment_definition/LOCKED_PROTOCOL_02.json'


def independent_ap(y, p):
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    order = np.argsort(-p, kind='stable')
    y, p = y[order], p[order]
    ends = np.r_[np.flatnonzero(np.diff(p)), len(p)-1]
    tp = np.cumsum(y)[ends]
    return float(np.sum((tp/(ends+1))*np.diff(np.r_[0, tp]))/y.sum())


def main():
    fusion, models = load()
    torch.set_num_threads(2)
    rows, selected = cohort(), job()
    y = np.array([r['failure'] for r in rows], dtype=int)
    roles = {name: selected[name] for name in ['training', 'validation', 'C', 'predict', 'original_inner_prediction_indices']}
    groups = {name: {rows[i]['recording_id'] for i in index} for name, index in roles.items()}
    for a in groups:
        for b in groups:
            if a < b:
                assert not groups[a] & groups[b], (a, b, 'GROUP_LEAKAGE')
    assert len(rows) == 4530 and len(selected['predict']) == 753
    assert len(selected['original_inner_prediction_indices']) == 920
    assert len({r['sample_id'] for r in rows}) == len(rows)
    assert all(len(set(rows[i]['frames16'])) == 16 for i in selected['predict']+selected['original_inner_prediction_indices'])
    original_job = next(j for j in read(EVIDENCE/'PHASE1_FIT_PLAN.json') if j['job_index'] == 2)
    assert original_job['predict'] == selected['original_inner_prediction_indices']
    assert original_job['G'] == selected['G'] and original_job['C'] == selected['C']
    sources = [COMPARISON/'26102026_configuration/PHASE1_SELECTED_JOB.json',
               COMPARISON/'26102026_configuration/PHASE1_COMPARISON_CONFIG.json',
               EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json', EVIDENCE/'PHASE1_FIT_PLAN.json',
               STUDY/'source/fusion.py', STUDY/'source/visual_model.py',
               BASE/'26102026_source/phase_model.py', BASE/'26102026_source/phase_training.py',
               REPO/'src/reassemble/section1_features.py', REPO/'src/reassemble/section1b.py',
               REPO/'configs/reassemble/section1.json', REPO/'configs/reassemble/section1b.json']
    verification = {}
    for arm, expected_epoch, expected_ap in [('frozen', 14, 0.19377562225054495), ('finetuned', 47, 0.2125845479746411)]:
        folder = arm_folder(arm)
        complete = read(folder/'PHASE1_FIT_COMPLETE.json')
        receipt = read(folder/'PHASE1_COMPARISON_ARM_COMPLETE.json')
        predictions = read(folder/'PHASE1_PREDICTIONS.json')
        calibrator = read(folder/'PHASE1_CALIBRATOR.json')
        history = read(folder/'PHASE1_LEARNING_CURVE.json')
        assert complete['executed_epochs'] == receipt['epochs'] == 100
        assert complete['best']['epoch'] == receipt['selected_epoch'] == expected_epoch
        assert len(history) == 100 and [r['epoch'] for r in history] == list(range(1, 101))
        assert sha(folder/'PHASE1_PREDICTIONS.json') == complete['predictions_sha256'] == receipt['predictions_sha256']
        assert sha(folder/'PHASE1_BEST_MODEL.pt') == complete['selected_model_sha256'] == receipt['selected_model_sha256']
        ids = [rows[i]['sample_id'] for i in selected['predict']]
        assert [r['sample_id'] for r in predictions] == ids and len(set(ids)) == 753
        for item, index in zip(predictions, selected['predict']):
            assert all(item[k] == rows[index][k] for k in ['sample_id', 'recording_id', 'segment_id', 'failure'])
        assert complete['T_sample_ids'] == [rows[i]['sample_id'] for i in selected['training']]
        assert complete['V_sample_ids'] == [rows[i]['sample_id'] for i in selected['validation']]
        assert complete['C_sample_ids'] == calibrator['C_sample_ids'] == [rows[i]['sample_id'] for i in selected['C']]
        assert calibrator['T'] == selected['training'] and calibrator['V'] == selected['validation']
        fitted_cal = fusion.calibrate(np.array(calibrator['raw_calibration_logits']), y[selected['C']])
        assert np.allclose(fitted_cal['coefficient'], calibrator['calibrator']['coefficient'], atol=1e-12, rtol=0)
        assert abs(fitted_cal['intercept']-calibrator['calibrator']['intercept']) < 1e-12
        p = np.array([r['p_visual'] for r in predictions])
        reconstructed = fusion.calibrated(np.array([r['raw_visual_logit'] for r in predictions]), calibrator['calibrator'])
        assert np.max(np.abs(p-reconstructed)) < 1e-12
        labels = np.array([r['failure'] for r in predictions])
        ap = float(average_precision_score(labels, p))
        assert abs(ap-independent_ap(labels, p)) < 1e-12
        # Verify the user-reported rounded value without assuming more precision.
        expected_six = 0.193776 if arm == 'frozen' else 0.212585
        assert round(ap, 6) == expected_six
        payload = torch.load(folder/'PHASE1_BEST_MODEL.pt', map_location='cpu', weights_only=True)
        assert payload['fit_identity'] == complete['fit_identity'] == receipt['fit_identity']
        assert payload['selected_epoch'] == expected_epoch
        model = models.make_model('C_full_finetuned16' if arm == 'finetuned' else 'B_frozen100', selected['training'], 42, device='cpu')
        loaded = model.load_state_dict(payload['model'], strict=True)
        assert not loaded.missing_keys and not loaded.unexpected_keys
        assert all(torch.isfinite(v).all() for v in model.state_dict().values())
        actual_mean = model.mean.detach().numpy()
        actual_std = model.std.detach().numpy()
        features = np.load(STUDY/'shared_cache/original_features_16.npy', allow_pickle=False)
        mean, std = fusion.standardizer(features[selected['training']])
        assert np.array_equal(actual_mean, mean) and np.array_equal(actual_std, std)
        raw_parity = None
        if arm == 'frozen':
            model.eval()
            with torch.inference_mode():
                raw = model(torch.from_numpy(features[selected['predict']])).numpy()
            raw_parity = float(np.max(np.abs(raw-np.array([r['raw_visual_logit'] for r in predictions]))))
            assert raw_parity < 1e-4
        verification[arm] = {'AP': ap, 'independent_AP': independent_ap(labels, p),
            'AUROC': float(roc_auc_score(labels, p)), 'epochs_executed': 100,
            'selected_epoch': expected_epoch, 'assessment_actions': len(p), 'positives': int(labels.sum()),
            'assessment_recordings': len(groups['predict']), 'strict_checkpoint_load': 'PASS',
            'finite_all_checkpoint_tensors': True, 'training_only_normalizer_exact': True,
            'calibrator_refit_matches': True, 'frozen_CPU_logit_max_abs': raw_parity,
            'checkpoint_identity': payload['fit_identity']}
        for name in ['PHASE1_BEST_MODEL.pt', 'PHASE1_FIT_COMPLETE.json', 'PHASE1_COMPARISON_ARM_COMPLETE.json',
                     'PHASE1_PREDICTIONS.json', 'PHASE1_CALIBRATOR.json', 'PHASE1_LEARNING_CURVE.json']:
            sources.append(folder/name)
        del model, payload
    sensor_folder = BASE/'26102026_execution/26102026_main_run_01/26102026_sensor_outer1_inner_fold_03'
    sensor = read(sensor_folder/'PHASE1_SENSOR_MODEL.json')
    assert sensor['G'] == selected['G'] and sensor['C'] == selected['C']
    assert sensor['prediction'] == selected['original_inner_prediction_indices']
    sensor_path = STUDY/'shared_cache/sensor_statistics.npy'
    assert sha(sensor_path) == sensor['input_sha256'] == read(EVIDENCE/'PHASE1_SENSOR_INPUT_IDENTITY.json')['sha256']
    x = np.load(sensor_path, allow_pickle=False)
    assert x.shape == (4530, 220)
    _, probabilities = fusion.sensor_predict(x[sensor['prediction']], sensor['model'])
    saved_sensor = read(sensor_folder/'PHASE1_SENSOR_PREDICTIONS.json')
    assert sha(sensor_folder/'PHASE1_SENSOR_PREDICTIONS.json') == sensor['predictions_sha256']
    assert [r['sample_id'] for r in saved_sensor] == [rows[i]['sample_id'] for i in sensor['prediction']]
    assert np.max(np.abs(probabilities-np.array([r['p_sensor'] for r in saved_sensor]))) < 1e-12
    outer_job = next(j for j in read(EVIDENCE/'PHASE1_FIT_PLAN.json')
                     if j['outer_fold_original'] == 0 and j['role'] == 'outer_assessment')
    outer_sensor_folder = sensor_folder.parent/'26102026_sensor_outer1_outer_assessment'
    outer_sensor = read(outer_sensor_folder/'PHASE1_SENSOR_MODEL.json')
    outer_predictions = read(outer_sensor_folder/'PHASE1_SENSOR_PREDICTIONS.json')
    assert outer_sensor['G'] == outer_job['G'] and outer_sensor['C'] == outer_job['C']
    assert outer_sensor['prediction'] == selected['predict'] == outer_job['predict']
    assert outer_sensor['input_sha256'] == sensor['input_sha256']
    assert sha(outer_sensor_folder/'PHASE1_SENSOR_PREDICTIONS.json') == outer_sensor['predictions_sha256']
    assert not groups['predict'] & {rows[i]['recording_id'] for i in outer_sensor['G']+outer_sensor['C']}
    assert [r['sample_id'] for r in outer_predictions] == [rows[i]['sample_id'] for i in selected['predict']]
    _, outer_replay = fusion.sensor_predict(x[outer_sensor['prediction']], outer_sensor['model'])
    assert np.max(np.abs(outer_replay-np.array([r['p_sensor'] for r in outer_predictions]))) < 1e-12
    sources += [sensor_folder/'PHASE1_SENSOR_MODEL.json', sensor_folder/'PHASE1_SENSOR_PREDICTIONS.json', sensor_path,
                STUDY/'shared_cache/original_features_16.npy', STUDY/'provenance/original_pretrained_identity.json',
                outer_sensor_folder/'PHASE1_SENSOR_MODEL.json', outer_sensor_folder/'PHASE1_SENSOR_PREDICTIONS.json']
    protocol = {'protocol': 'REASSEMBLE-SELECTED-CNN100-STATIC-SENSOR-HOLDOUT-F2-v1', 'seed': 42,
        'models': ['M1_frozen100', 'M2_finetuned100', 'M3_sensor', 'M4_F2_frozen', 'M5_F2_finetuned', 'M6_average_frozen', 'M7_average_finetuned'],
        'positive_label': 'Native failure=1; no label modification', 'frames': 16,
        'fusion_source': relative(STUDY/'source/fusion.py'),
        'fusion_formula': 'sigmoid(intercept + w_visual*p_visual + w_sensor*p_sensor)',
        'fusion_estimator': {'C': 1.0, 'class_weight': None, 'solver': 'lbfgs', 'max_iter': 2000, 'random_state': 42},
        'coefficient_constraints': 'None; no probability-to-logit transform or meta-standardization',
        'primary_threshold': 0.5, 'threshold_provenance': 'Matches frozen100/full-CNN Phase1 and preserved original clean-CNN F2 primitive',
        'historical_section1b_threshold': 'Different: training meta-cross-fitted balanced-accuracy threshold; report M8 separately',
        'sensor': 'Original220-statistics balanced C1 logistic with separate C calibration: saved inner3 fit for held-out F2 inputs; saved full outer-training fit for identical M3-M7 test probabilities',
        'sensor_test_fit_role': 'outer_assessment', 'sensor_fitting_bank_role': 'inner_fold_03',
        'sensor_training_sizes': {'F2_bank_G': len(sensor['G']), 'F2_bank_C': len(sensor['C']),
                                 'test_G': len(outer_sensor['G']), 'test_C': len(outer_sensor['C'])},
        'sensor_branch_calibration': 'Original separate686-action inner C and811-action outer C; identical sensor predictions reused across both F2 arms',
        'branch_calibration': 'Visual arms reuse independently reproduced original unweighted C1 sigmoid on the same disjoint686-action C; sensor keeps its original inner/outer G/C recipe',
        'fusion_training_bank': 'Original held-out inner-fold3:920 actions/28 recordings; excluded from selected base models training, checkpoint selection and calibration',
        'training_bank_indices': selected['original_inner_prediction_indices'], 'outer_test_indices': selected['predict'],
        'OOF_coverage_limitation': 'One original inner-fold held-out bank, not complete four-fold nested OOF replication. No replacement CNN fit is needed for this fixed-model holdout-stacking comparison.',
        'selection_limitation': 'Selected original fit3 based on prior20-epoch training-side validation; previously examined outer fold; exploratory, not confirmatory',
        'meta_crossfit_diagnostic': {'folds': 4, 'group': 'recording_id', 'seed': 20261029, 'changes_primary_fit': False},
        'bootstrap': {'replicates': 2000, 'seed': 20261029, 'unit': 'recording', 'interval': 'percentile95', 'conditional_on': 'selected split and fitted models'},
        'ece_bins': 15, 'CPU_only_new_inference': True, 'torch_CPU_threads': 2,
        'existing_GPU_study_interruptions_allowed': False, 'new_CNN_training': False,
        'locked_before_new_fusion_test_metrics': True}
    if CONFIG.exists():
        assert read(CONFIG) == protocol, 'Protocol changes require a new experiment version'
    else:
        write(CONFIG, protocol)
    write(RUN/'config/resolved_config.json', protocol)
    write(ROOT/'02_checkpoint_verification/VERIFICATION.json', {'utc': utc(), 'passed': True,
        'arms': verification, 'roles': {name: {'actions': len(index), 'recordings': len(groups[name]),
        'positives': int(y[index].sum()), 'sample_ids': [rows[i]['sample_id'] for i in index], 'recording_ids': sorted(groups[name])}
        for name, index in roles.items()}, 'role_recording_intersections': 0, 'saved_sensor_predictions_reproduced': True,
        'sensor_dimensions': 220, 'outer_sensor_predictions_reproduced': True,
        'source_checkpoint_weights_modified': False, 'protocol_sha256': sha(CONFIG)})
    write(RUN/'manifests/INPUT_IDENTITIES.json', [identity(p) for p in sources])
    text = '# Existing experiment verification — PASS\n\n'
    text += 'Verified actual checkpoint bytes/identities, strict CPU state loading with no missing/unexpected tensors, finite tensors, 100 history rows, selected epochs, original training-only normalizers, saved prediction IDs/labels and independently recomputed AP. Original C calibrators were refitted from their saved training-side logits and reproduced exactly.\n\n'
    text += '| Arm | Epochs | Selected | Assessment AP | Actions | Recordings |\n|---|---:|---:|---:|---:|---:|\n'
    for arm, v in verification.items():
        text += f"| {arm} | 100 | {v['selected_epoch']} | {v['AP']:.9f} | 753 | 26 |\n"
    text += '\nAll 753 assessment actions (77 failures/676 nonfailures) are recording-disjoint from gradient training, checkpoint selection, branch calibration and the proposed F2 fitting bank. The pre-existing selected-job field `prediction_recordings` refers to its original inner holdout; actual new outer prediction IDs/recordings were checked against the cohort instead of trusting that stale field.\n\n'
    text += 'A valid untouched training-side bank exists:920 actions from28 recordings, with97 failures. Reusing it needs only new inference, not new CNN fitting. It is one original inner-fold holdout, not complete four-fold nested OOF coverage. Both fusion arms will use the same bank, sensor probabilities, fitting function and fixed threshold. The departure from historical all-inner-fold coverage is explicit in LOCKED_PROTOCOL_02.json. No in-sample base predictions or calibration-fit rows enter F2 fitting.\n\n'
    text += 'The saved static sensor branch uses220 statistics, balanced C1 logistic on G and independent unweighted sigmoid calibration on C. The original inner3 model supplies genuine out-of-fit F2-training inputs (G2171/C686); the original outer-assessment model supplies the unchanged M3-M7 baseline test probabilities (G2966/C811). This preserves the original inner-fit/outer-refit stacking roles instead of weakening the sensor baseline to the smaller inner fit. Both saved prediction banks reproduce to1e-12. Original checkpoints and the running75-fit study remain unchanged. New computations will use CPU only.\n'
    (ROOT/'02_checkpoint_verification/VERIFICATION_REPORT.md').write_text(text)
    status('VERIFICATION_COMPLETE_PROTOCOL_LOCKED', new_CNN_training=False, CPU_inference_pending=True,
           fusion_training_actions=920, outer_test_actions=753)
    print('VERIFICATION_PASS', verification, flush=True)


if __name__ == '__main__':
    main()
