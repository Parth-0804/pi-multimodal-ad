"""CPU-only checkpoint/metric audit. No inference, optimizer or trainer imports."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import json
import numpy as np
import torch
from safetensors import safe_open
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss, log_loss

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent
REPO = SOURCE.parents[1]
PHASE = REPO / '26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability'
HIST = REPO / 'parth_ws_bootstrap/00_experimentation/visual_backbone_f2_frozen_vs_final_stage_16_vs_32_frames/run_01'
DETOUR = PHASE / '26102026_bestfit_100epoch_frozen_vs_full_cnn'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def rel(path):
    import os
    return os.path.relpath(path, REPO)


def save(relative, data):
    with (RUN / relative).open('x') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')


def score(y, p):
    y, p = np.asarray(y, int), np.asarray(p, float)
    assert np.isfinite(p).all() and ((p >= 0) & (p <= 1)).all()
    return {'n': len(y), 'failures': int(y.sum()), 'prevalence': float(y.mean()),
            'AP': float(average_precision_score(y, p)), 'AUROC': float(roc_auc_score(y, p)),
            'Brier': float(brier_score_loss(y, p)), 'log_loss': float(log_loss(y, p))}


if __name__ == '__main__':
    torch.set_num_threads(2)
    identities = []
    def identity(path, role):
        row = {'path': rel(path), 'sha256': sha(path), 'bytes': path.stat().st_size, 'role': role}
        identities.append(row)
        return row
    code_paths = [HIST / 'source/visual_model.py', HIST / 'source/fusion.py', HIST / 'source/pixel_access.py',
                  REPO / 'src/reassemble/section1_features.py', REPO / 'src/reassemble/section1_models.py',
                  REPO / 'src/reassemble/section1b.py', REPO / 'src/reassemble/section2_models.py',
                  REPO / 'src/reassemble/section2_data.py', REPO / 'src/reassemble/additional_improvements/models.py',
                  REPO / 'src/reassemble/additional_improvements/robust_fusion.py',
                  PHASE / '26102026_source/phase_model.py', PHASE / '26102026_source/phase_training.py',
                  PHASE / '26102026_source/phase_evaluation.py', PHASE / '26102026_configuration/PHASE1_CONFIG.json',
                  DETOUR / '26102026_configuration/PHASE1_SELECTED_JOB.json',
                  DETOUR / '26102026_configuration/PHASE1_COMPARISON_CONFIG.json']
    for path in code_paths:
        identity(path, 'inspected implementation/configuration; not executed')
    configuration = load(HIST / 'config/resolved_config.json')
    weights = REPO / configuration['weights_dir']
    original = load(HIST / 'provenance/original_pretrained_identity.json')
    for name, expected in original['weights'].items():
        item = identity(weights / name, 'original pretrained source')
        assert item['sha256'] == expected['sha256'] and item['bytes'] == expected['bytes']
    source_tensors = safe_open(weights / 'model.safetensors', framework='pt', device='cpu')
    original_keys = set(source_tensors.keys())
    tensor_changes, metrics, checkpoint_rows = [], {}, []
    shared_ids = None
    cohort = load(HIST / 'data_manifests/cohort_and_frames.json')
    by_sample = {row['sample_id']: row for row in cohort}
    saved_results = load(DETOUR / '26102026_execution/PHASE1_100EPOCH_COMPARISON_METRICS.json')
    for arm in ['B_frozen100', 'C_full_finetuned16']:
        folder = DETOUR / f'26102026_execution/26102026_{arm}_seed42_selectedjob02'
        receipt = load(folder / 'PHASE1_FIT_COMPLETE.json')
        arm_receipt = load(folder / 'PHASE1_COMPARISON_ARM_COMPLETE.json')
        path = folder / 'PHASE1_BEST_MODEL.pt'
        checkpoint_id = identity(path, 'completed selected checkpoint; CPU read only')
        prediction_path = folder / 'PHASE1_PREDICTIONS.json'
        prediction_id = identity(prediction_path, 'saved probabilities; no inference rerun')
        assert checkpoint_id['sha256'] == receipt['selected_model_sha256'] == arm_receipt['selected_model_sha256']
        assert prediction_id['sha256'] == receipt['predictions_sha256'] == arm_receipt['predictions_sha256']
        identity(folder / 'PHASE1_FIT_COMPLETE.json', 'completed fit receipt')
        identity(folder / 'PHASE1_COMPARISON_ARM_COMPLETE.json', 'completed arm receipt')
        checkpoint = torch.load(path, map_location='cpu', weights_only=True)
        assert checkpoint['fit_identity'] == receipt['fit_identity'] and checkpoint['arm'] == arm
        assert checkpoint['selected_epoch'] == receipt['best']['epoch'] == arm_receipt['selected_epoch']
        assert receipt['executed_epochs'] == 100 and [row['epoch'] for row in receipt['history']] == list(range(1, 101))
        predictions = load(prediction_path)
        assert len({row['sample_id'] for row in predictions}) == len(predictions) == 753
        assert all(row['failure'] == by_sample[row['sample_id']]['failure'] and row['recording_id'] == by_sample[row['sample_id']]['recording_id'] for row in predictions)
        ids = {row['sample_id'] for row in predictions}
        if shared_ids is not None:
            assert ids == shared_ids
        shared_ids = ids
        assessed_recordings = {row['recording_id'] for row in predictions}
        roles = {name: set(receipt[name + '_sample_ids']) for name in ('T', 'V', 'C')}
        for values in roles.values():
            assert not values & ids
            assert not {by_sample[sample]['recording_id'] for sample in values} & assessed_recordings
        for a, b in [('T', 'V'), ('T', 'C'), ('V', 'C')]:
            assert not roles[a] & roles[b]
            assert not {by_sample[sample]['recording_id'] for sample in roles[a]} & {by_sample[sample]['recording_id'] for sample in roles[b]}
        values = score([row['failure'] for row in predictions], [row['p_visual'] for row in predictions])
        assert all(abs(values[name] - saved_results['metrics'][arm][name]) < 1e-12 for name in ('AP', 'AUROC', 'Brier', 'log_loss'))
        metrics[arm] = values
        model = checkpoint['model']
        backbone = {name.removeprefix('backbone.'): tensor for name, tensor in model.items() if name.startswith('backbone.')}
        changed, unchanged, incompatible = [], [], []
        for name, tensor in backbone.items():
            key = 'model.backbone.model.' + name
            if key not in original_keys or list(source_tensors.get_tensor(key).shape) != list(tensor.shape):
                incompatible.append(name)
                continue
            base = source_tensors.get_tensor(key)
            different = not torch.equal(base, tensor)
            (changed if different else unchanged).append(name)
            tensor_changes.append({'arm': arm, 'tensor': name, 'shape': str(list(tensor.shape)), 'changed': different,
                                   'max_abs_difference': float((tensor - base).abs().max()), 'elements': tensor.numel()})
        assert not incompatible
        if arm.startswith('C_'):
            assert changed and all(any(name.startswith(prefix) for name in changed) for prefix in ['embedder.', 'encoder.stages.0.', 'encoder.stages.1.', 'encoder.stages.2.', 'encoder.stages.3.'])
            assert not any('running_' in name for name in changed)
        else:
            assert not backbone, 'Frozen feature head checkpoint should not be claimed as a trained backbone'
        checkpoint_rows.append({**checkpoint_id, 'arm': arm, 'executed_epochs': 100,
                                'selected_epoch': checkpoint['selected_epoch'], 'training_seconds': receipt['training_seconds'],
                                'assessment_recordings': len(assessed_recordings), 'assessment_episodes_or_actions': len(predictions),
                                'backbone_tensors': len(backbone), 'changed_backbone_tensors': len(changed),
                                'unchanged_backbone_tensors': len(unchanged), 'incompatible_backbone_tensors': incompatible,
                                'changed_scopes': dict(Counter('embedder' if name.startswith('embedder.') else '.'.join(name.split('.')[:3]) for name in changed)),
                                'valid_full_backbone_transfer_source': arm.startswith('C_') and bool(changed),
                                'target_domain_transfer_executed': False})

    # Recompute historical reference point estimates directly from saved OOF arrays.
    historical = []
    references = [
        ('sensor_statistics', 'runs/reassemble/20260927T154732Z-section1/predictions/sensor_statistics_perm00.npz', 'sensor_statistics', 'runs/reassemble/20260927T154732Z-section1/assessment/results.json', 'p'),
        ('visual_frozen', 'runs/reassemble/20260927T154732Z-section1/predictions/rtdetr_perm00.npz', 'rtdetr', 'runs/reassemble/20260927T154732Z-section1/assessment/results.json', 'p'),
        ('F2_static', 'runs/reassemble/20260927T175336Z-section1b/stacking/oof.npz', 'minimal_late_fusion', 'runs/reassemble/20260927T175336Z-section1b/assessment/results.json', 'p'),
        ('F5_quality_gate', 'runs/reassemble/20260927T192852Z-section2/predictions/oof.npz', 'F5', 'runs/reassemble/20260927T192852Z-section2/assessment/results.json', 'F5_p'),
        ('F6_action_quality_gate', 'runs/reassemble/20260927T192852Z-section2/predictions/oof.npz', 'F6', 'runs/reassemble/20260927T192852Z-section2/assessment/results.json', 'F6_p'),
    ]
    for name, prediction_path, key, result_path, column in references:
        identity(REPO / prediction_path, 'historical OOF predictions; consistency only')
        identity(REPO / result_path, 'historical saved metric artifact')
        with np.load(REPO / prediction_path, allow_pickle=False) as bank:
            values = score(bank['y'], bank[column])
        expected = load(REPO / result_path)['metrics'][key]
        assert abs(values['AP'] - expected['AUPRC']['estimate']) < 1e-12
        assert abs(values['AUROC'] - expected['AUROC']['estimate']) < 1e-12
        assert abs(values['Brier'] - expected['Brier']['estimate']) < 1e-12
        historical.append({'name': name, 'prediction_path': prediction_path, **values,
                           'verification_scope': 'recomputed metrics from saved probabilities, not retraining or inference reproduction'})
    live_status = PHASE / '26102026_c_only_20epoch_revision_01/26102026_execution/PHASE1_C_ONLY_STATUS.json'
    status_bytes = live_status.read_bytes()
    save('04_REASSEMBLE_REFERENCE/ACTIVE_STUDY_STATUS_SNAPSHOT.json', json.loads(status_bytes))
    completed = []
    for receipt_path in sorted((PHASE / '26102026_execution/26102026_main_run_01').rglob('PHASE1_FIT_COMPLETE.json')):
        receipt = load(receipt_path)
        if receipt['arm'] != 'C_full_finetuned16':
            continue
        model_path = receipt_path.parent / 'PHASE1_BEST_MODEL.pt'
        assert sha(model_path) == receipt['selected_model_sha256']
        completed.append({'receipt': rel(receipt_path), 'checkpoint': rel(model_path), 'checkpoint_sha256': sha(model_path),
                          'seed': receipt['seed'], 'job_index': receipt['job_index'], 'executed_epochs': receipt['executed_epochs'],
                          'selected_epoch': receipt['best']['epoch']})
    save('04_REASSEMBLE_REFERENCE/REFERENCE_AUDIT.json', {
        'utc': datetime.now(timezone.utc).isoformat(), 'gpu_initialized_by_this_audit': torch.cuda.is_initialized(),
        'original_pretrained_revision': original['revision'], 'original_weights_directory': rel(weights),
        'completed_100epoch_checkpoint_audits': checkpoint_rows, 'completed_100epoch_metrics_recomputed': metrics,
        'historical_metrics_recomputed': historical, 'main_completed_C_fit_receipts': completed,
        'main_status_snapshot_sha256': hashlib.sha256(status_bytes).hexdigest(),
        'main_study_complete': len(completed) == 75,
        'no_model_training_or_inference': True, 'ViFailback_weight_transfer_performed': False,
        'selected_job_metadata_note': 'prediction_recordings in selected-job config retains original-inner bookkeeping; actual predictions use 26 outer-assessment recordings, checked directly against T/V/C sample identities'})
    save('provenance/REASSEMBLE_SOURCE_AND_CHECKPOINT_HASHES.json', identities)
    with (RUN / '04_REASSEMBLE_REFERENCE/CHECKPOINT_TENSOR_CHANGES.csv').open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(tensor_changes[0]))
        writer.writeheader()
        writer.writerows(tensor_changes)
    print(json.dumps({'checkpoints': checkpoint_rows, 'main_completed_C_fits': len(completed),
                      '100epoch_metrics': metrics, 'historical_metrics': historical}, indent=2))
