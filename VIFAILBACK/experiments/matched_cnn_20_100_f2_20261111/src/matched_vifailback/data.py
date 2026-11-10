"""Verified read-only native inputs and unchanged task-disjoint fitting roles.

Original manifests, images, cached features and historical fits are never written.
The pilot retains inner-job A as its meta bank; outer assessment IDs are separate.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
import csv
import hashlib
import json
import math
import os

import numpy as np

from .common import (PROJECT, REPO, STUDY, immutable_json, legacy_config,
                     protocol, read_json, relative, resolve, sha256, signature)

CAMERAS = ('cam_high', 'cam_left_wrist', 'cam_right_wrist')
VIDEO_KEYS = ('video_high', 'video_left', 'video_right')
SOURCE_PHASE1 = Path('26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability')
SOURCE_STOP = SOURCE_PHASE1 / '26102026_c_only_20epoch_revision_01/02112026_stop_after25fits_01/STOP_AFTER_25_COMPLETE.json'
ORIGINAL_WEIGHTS_SHA = 'fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def old_signature(value):
    """Historical signatures used default JSON separators; preserve that scheme."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def manifest_identity(path):
    path = Path(path)
    return {'path': relative(path), 'bytes': path.stat().st_size, 'sha256': sha256(path)}


def verify_frame_contract(row):
    n = int(row['frame_count'])
    expected = np.round(np.linspace(0, n - 1, 16)).astype(int).tolist()
    require(n >= 16 and len(set(expected)) == 16, 'Fewer than16 unique frame indices')
    require(row['frame_indices'] == expected, 'Label-blind uniform frame identities changed')
    require(len(row['camera_sha256']) == 3 and len(row['camera_bytes']) == 3,
            'Three-camera source identity missing')
    require(len(row['camera_mtime_ns']) == 3, 'Three-camera source metadata missing')
    require(len(row['selected_RGB_sha256']) == 3 and all(len(v) == 16 for v in row['selected_RGB_sha256']),
            'Expected16 source-frame identities for each of3 cameras')
    require(all(isinstance(x, str) and len(x) == 64 for v in row['selected_RGB_sha256'] for x in v),
            'Invalid selected RGB content hash')
    require(np.allclose(row['frame_times_seconds'], np.asarray(expected) / 25, rtol=0, atol=1e-12),
            'Converted frame times disagree with25Hz index contract')
    return expected


def verify_rows(rows, native_labels=None, expected=None):
    ids = [int(r['episode_index']) for r in rows]
    require(len(ids) == len(set(ids)), 'Duplicate native episode identity')
    require(all(r['label'] in (0, 1) for r in rows), 'Only native binary labels are admissible')
    for row in rows:
        verify_frame_contract(row)
        if native_labels is not None:
            require(row['label'] == native_labels[row['episode_index']], 'Native episode label mismatch')
    counts = Counter(r['label'] for r in rows)
    tasks = set(r['canonical_task_id'] for r in rows)
    require(55 not in tasks, 'Quarantined task55 was restored')
    if expected is not None:
        require(len(rows) == expected['episodes'], 'Eligible cohort size changed')
        require(counts == {1: expected['failures'], 0: expected['successes']}, 'Native class counts changed')
        require(len(tasks) == expected['canonical_tasks'], 'Canonical task count changed')
    return {'episodes': len(rows), 'failures': counts[1], 'successes': counts[0],
            'canonical_tasks': len(tasks), 'failure_prevalence': counts[1] / len(rows)}


def verify_roles(job, lookup, extra_ids=None):
    """Check IDs, declared groups, class support and optional separate outer bank."""
    ids = {k: list(job['ids'][k]) for k in ('T', 'V', 'C', 'A')}
    if extra_ids is not None:
        ids['OUTER'] = list(extra_ids)
    groups = {}
    result = {}
    for role, values in ids.items():
        require(values and len(values) == len(set(values)), f'Empty or repeated IDs in {role}')
        require(all(e in lookup for e in values), f'Unknown native ID in {role}')
        groups[role] = {lookup[e]['canonical_task_id'] for e in values}
        expected_ids = {e for e, row in lookup.items() if row['canonical_task_id'] in groups[role]}
        require(set(values) == expected_ids, f'Incomplete task membership in {role}')
        counts = Counter(lookup[e]['label'] for e in values)
        require(set(counts) == {0, 1}, f'Single-class fitting role {role}')
        if role != 'OUTER':
            require(groups[role] == set(job['groups'][role]), f'Declared group membership mismatch in {role}')
            if 'class_counts' in job:
                declared = {int(k): v for k, v in job['class_counts'][role].items()}
                require(counts == declared, f'Class-count evidence mismatch in {role}')
        result[role] = {'episodes': len(values), 'tasks': len(groups[role]), 'class_counts': dict(counts),
                        'ordered_episode_ids_sha256': old_signature(values), 'task_ids': sorted(groups[role])}
    for i, a in enumerate(ids):
        for b in list(ids)[i + 1:]:
            require(not set(ids[a]) & set(ids[b]), f'Episode leakage between {a} and {b}')
            require(not groups[a] & groups[b], f'Task leakage between {a} and {b}')
    return result


def get_job(context, job_id):
    require(job_id in context['jobs'], f'Unknown frozen job {job_id}')
    return deepcopy(context['jobs'][job_id])


def pilot_outer_ids(context):
    outer = protocol()['pilot']['outer']
    return list(context['jobs'][f'outer{outer}_final']['ids']['A'])


def verify_splits(jobs, rows):
    lookup = {r['episode_index']: r for r in rows}
    require(len(jobs) == 12 and len({j['id'] for j in jobs}) == 12, 'Expected12 distinct original jobs')
    reports = {j['id']: verify_roles(j, lookup) for j in jobs}
    outer_ids = []
    for outer in range(3):
        fits = [j for j in jobs if j['outer'] == outer]
        require({j['inner'] for j in fits} == {-1, 0, 1, 2}, 'Missing outer/inner role')
        final = next(j for j in fits if j['inner'] == -1)
        require(set(sum(final['ids'].values(), [])) == set(lookup), 'Outer role omits eligible episodes')
        inner_a = [e for j in fits if j['inner'] >= 0 for e in j['ids']['A']]
        require(len(inner_a) == len(set(inner_a)), 'Duplicated inner OOF assessment')
        require(set(inner_a) == set(sum([final['ids'][k] for k in ('T', 'V', 'C')], [])),
                'Incomplete or contaminated inner OOF coverage')
        require(not set(inner_a) & set(final['ids']['A']), 'Outer assessment contaminates OOF bank')
        outer_ids.extend(final['ids']['A'])
    require(len(outer_ids) == len(set(outer_ids)) == len(rows), 'Outer assessments do not partition cohort')
    return reports


def pool_bank(array):
    require(array.ndim == 4 and tuple(array.shape[1:]) == (3, 16, 896), 'Wrong multiview feature geometry')
    require(array.dtype == np.float32 and np.isfinite(array).all(), 'Nonfinite or non-FP32 cached features')
    result = np.asarray(array.mean((1, 2)), dtype=np.float32)
    result.flags.writeable = False
    return result


def sensor_join(episode_ids, features, eligible_ids):
    ids = [int(e) for e in episode_ids]
    require(len(ids) == len(set(ids)), 'Duplicate sensor episode identity')
    require(features.shape == (len(ids), 280), 'Expected280 sensor features per episode')
    require(np.isfinite(features).all(), 'Nonfinite sensor statistic')
    index = {e: i for i, e in enumerate(ids)}
    require(set(eligible_ids) <= set(index), 'Eligible episode lacks sensor features')
    return index


def verify_native_labels(config):
    base = resolve(config['historical_root']) / 'source_evidence'
    originals = {}
    sources = []
    for path in sorted((base / 'original/annotated_data').rglob('*_annotations.json')):
        identity = manifest_identity(path)
        require(identity['sha256'] == read_json(path.with_name(path.name + '.receipt.json'))['sha256'],
                'Native annotation SHA drift')
        sources.append(identity)
        for row in read_json(path):
            require(row['video'] not in originals, 'Ambiguous original native episode')
            require(row['failure_detection'] in ('yes', 'no'), 'Unexpected native label')
            originals[row['video']] = row
    metadata = base / 'vifailback/meta/vifailback_annotations.jsonl'
    identity = manifest_identity(metadata)
    require(identity['sha256'] == read_json(metadata.with_name(metadata.name + '.receipt.json'))['sha256'],
            'Converted native annotation SHA drift')
    sources.append(identity)
    episode_path = base / 'vifailback/meta/episodes.jsonl'
    episodes = {r['episode_index']: r for r in map(json.loads, episode_path.open())}
    sources.append(manifest_identity(episode_path))
    targets = {}
    for row in map(json.loads, metadata.open()):
        annotation = row['annotation']; native = originals[annotation['video']]
        require(all(annotation.get(k) == v for k, v in native.items()), 'Native-to-converted annotation mismatch')
        eid = row['episode_index']
        require(eid not in targets, 'Duplicate converted native episode')
        targets[eid] = int(native['failure_detection'] == 'yes')
        require(row['episode_success'] == ('failure' if targets[eid] else 'success'), 'Native outcome mismatch')
        require(episodes[eid]['length'] == row['num_frames'] and native['task'] in episodes[eid]['tasks'],
                'Native episode length/task join mismatch')
    require(len(originals) == len(targets) == len(episodes) == 5202, 'Native cohort count drift')
    require(Counter(targets.values()) == {1: 4545, 0: 657}, 'Native label count drift')
    return targets, {'native_episodes': 5202, 'failure': 4545, 'success': 657,
                     'annotation_files': len(sources) - 2, 'sources': sources}


def verify_videos(config, rows):
    count = 0
    byte_total = 0
    content_rechecks = []
    sensor_inventory = {r['path']: r for r in read_json(resolve(config['sensor_inventory']))}
    sensor_missing = []
    for row in rows:
        sensor_path = resolve(config['historical_root']) / sensor_inventory[row['data']]['local_path']
        if not sensor_path.is_file():
            sensor_missing.append(row['episode_index'])
        for view, key in enumerate(VIDEO_KEYS):
            old = resolve(config['historical_root']) / 'source_evidence/vifailback' / row[key]
            path = old if old.is_file() else resolve(config['video_cache']) / row[key]
            require(path.is_file(), f'Missing camera stream for episode{row["episode_index"]}')
            stat = path.stat()
            require(stat.st_size == row['camera_bytes'][view], 'Camera size drift since verified frame audit')
            if stat.st_mtime_ns != row['camera_mtime_ns'][view]:
                require(sha256(path) == row['camera_sha256'][view], 'Camera payload changed since frame audit')
                content_rechecks.append(relative(path))
            count += 1; byte_total += stat.st_size
    require(not sensor_missing, 'Missing original numerical telemetry payloads')
    return {'camera_streams': count, 'source_bytes_referenced_not_copied': byte_total,
            'size_mtime_metadata_matches': count - len(content_rechecks),
            'changed_mtime_payload_hash_rechecks': content_rechecks,
            'sensor_episode_files_present': len(rows),
            'scope': 'Current metadata recheck against original complete decode+selected-frame SHA audit; actual selected frames checked again on every live decode'}


def selection_epoch(history):
    return max(history, key=lambda h: (h['V_macro_AP'], -h['V_weighted_BCE_same_T_positive_weight'], -h['epoch']))['epoch']


def verify_frozen_reuse(config, jobs, original, index):
    import torch
    root = PROJECT / '06_training_experiments/visual_frozen/runs' / config['run_id']
    config_sha = old_signature(config)
    evidence = []
    code_hashes = {}
    for path in sorted(root.glob('seed*/*/COMPLETE.json')):
        receipt = read_json(path); history = read_json(path.parent / 'HISTORY.json')
        require([h['epoch'] for h in history] == list(range(1, 101)), 'Incomplete historical100-epoch trajectory')
        require(receipt['configuration_sha256'] == config_sha, 'Historical frozen configuration changed')
        for source, digest in receipt['implementation'].items():
            if source not in code_hashes:
                code_hashes[source] = sha256(resolve(source))
            require(code_hashes[source] == digest, 'Historical source implementation changed')
        for filename, key in [('BEST_MODEL.pt', 'best_checkpoint_sha256'),
                              ('FINAL_EPOCH100.pt', 'final_checkpoint_sha256'),
                              ('predictions.json', 'prediction_sha256')]:
            require(sha256(path.parent / filename) == receipt[key], 'Historical frozen completion hash mismatch')
        require(selection_epoch(history) == receipt['selected_epoch'], 'New tie rule selects a different historical checkpoint')
        require(jobs[receipt['fit_id']]['ids']['A'] == [r['episode_index'] for r in read_json(path.parent / 'predictions.json')],
                'Historical frozen assessment identity mismatch')
        evidence.append({'receipt': manifest_identity(path), 'seed': receipt['seed'], 'job_id': receipt['fit_id'],
                         'executed_epochs': 100, 'selected_epoch': receipt['selected_epoch'],
                         'selected_under_new_tie_rule': True, 'best_checkpoint_sha256': receipt['best_checkpoint_sha256'],
                         'final_checkpoint_sha256': receipt['final_checkpoint_sha256']})
    require(len(evidence) == 36, 'Expected36 retained multiview V1 fits')
    pilot = protocol()['pilot']; folder = root / f'seed{pilot["seed"]}' / pilot['base_job_id']
    best = torch.load(folder / 'BEST_MODEL.pt', map_location='cpu', weights_only=True)
    final = torch.load(folder / 'FINAL_EPOCH100.pt', map_location='cpu', weights_only=True)
    job = jobs[pilot['base_job_id']]
    require(best['job'] == job and final['job'] == job, 'Pilot checkpoint fitting roles changed')
    require(best['condition'] == final['condition'] == 'V1' and best['seed'] == final['seed'] == pilot['seed'],
            'Pilot frozen condition/seed mismatch')
    model = best['model']; head = {k: v for k, v in model.items() if k.startswith('head.')}
    require(sum(v.numel() for v in head.values()) == 114945, 'Frozen classifier parameter count mismatch')
    require(all(v.dtype == torch.float32 and torch.isfinite(v).all() for v in model.values()), 'Invalid frozen checkpoint tensors')
    require(set(model) == set(head) | {'mean', 'std'}, 'Unexpected transferred backbone/source classifier state')
    group = final['optimizer']['param_groups']; require(len(group) == 1, 'Frozen optimizer must contain only classifier')
    g = group[0]
    for key, value in [('initial_lr', .001), ('lr', .0001), ('weight_decay', .001), ('eps', 1e-8), ('amsgrad', False)]:
        require(g[key] == value, f'Historical optimizer setting differs: {key}')
    require(tuple(g['betas']) == (.9, .999), 'Historical Adam betas differ')
    require(final['completed_epochs'] == final['scheduler']['last_epoch'] == 100, 'Incomplete final optimizer/scheduler state')
    features = original[[index[e] for e in job['ids']['T']]]
    mean = np.nanmean(features, axis=0).astype('float32'); std = np.nanstd(features, axis=0).astype('float32')
    std = np.where(np.isfinite(std) & (std > 1e-6), std, 1.).astype('float32')
    require(np.array_equal(model['mean'].numpy(), mean) and np.array_equal(model['std'].numpy(), std),
            'Frozen scaler not fitted on exact pilot T-only features')
    return {'fits': evidence, 'pilot_job_id': job['id'], 'pilot_selected_epoch': best['selected_epoch'],
            'pilot_best': manifest_identity(folder / 'BEST_MODEL.pt'),
            'pilot_final': manifest_identity(folder / 'FINAL_EPOCH100.pt'),
            'optimizer': {k: v for k, v in g.items() if k != 'params'},
            'scheduler': final['scheduler'], 'RNG_state_present': sorted(final['rng']),
            'scope': 'Reuse requires new trainer CPU head/RNG/batch equivalence preflight; no historical head retraining',
            'all_new_tie_rule_selections_agree': True}


def verify_donor(config):
    import torch
    from safetensors import safe_open
    donor = protocol()['donor']; path = resolve(donor['checkpoint'])
    require(sha256(path) == donor['sha256'], 'Declared donor checkpoint SHA mismatch')
    receipt_path = path.parent / 'PHASE1_FIT_COMPLETE.json'; receipt = read_json(receipt_path)
    require(receipt['arm'] == 'C_full_finetuned16' and receipt['job_index'] == 2, 'Wrong donor source arm/job')
    require([h['epoch'] for h in receipt['history']] == list(range(1, 101)), 'Incomplete donor source history')
    require(receipt['executed_epochs'] == 100 and receipt['best']['epoch'] == 47 and receipt['seed'] == 42,
            'Donor completed source fit/selection mismatch')
    require(receipt['selected_model_sha256'] == donor['sha256'], 'Donor receipt/checkpoint mismatch')
    weights = resolve(config['pretrained_weights']) / 'model.safetensors'
    require(sha256(weights) == ORIGINAL_WEIGHTS_SHA, 'Pinned original safetensors SHA mismatch')
    state = torch.load(path, map_location='cpu', weights_only=True)
    require(state['arm'] == 'C_full_finetuned16', 'Wrong donor tensor payload arm')
    require(state['selected_epoch'] == 47 and state['seed'] == 42 and state['fit_identity'] == receipt['fit_identity'],
            'Donor tensor payload source identity mismatch')
    cnn = {k.removeprefix('backbone.'): v for k, v in state['model'].items() if k.startswith('backbone.')}
    require(len(cnn) == 115, 'Donor CNN tensor count mismatch')
    changed = []
    shapes = {}
    with safe_open(weights, framework='pt', device='cpu') as original:
        for key, tensor in cnn.items():
            source_key = 'model.backbone.model.' + key
            source = original.get_tensor(source_key)
            require(source.shape == tensor.shape and source.dtype == tensor.dtype, 'Donor/source tensor shape or dtype mismatch')
            require(torch.isfinite(tensor).all(), 'Nonfinite donor tensor')
            shapes[key] = list(tensor.shape)
            if not torch.equal(tensor, source):
                changed.append(key)
    require(changed and not any('running_' in k for k in changed), 'Donor CNN missing learned values or changed running moments')
    for prefix in ['embedder.'] + [f'encoder.stages.{i}.' for i in range(4)]:
        require(any(k.startswith(prefix) for k in changed), f'Donor CNN stage has no changed tensor:{prefix}')
    return {'source_receipt': manifest_identity(receipt_path), 'selected_checkpoint': manifest_identity(path),
            'original_safetensors': manifest_identity(weights), 'source_fit_identity': receipt['fit_identity'],
            'executed_epochs': 100, 'selected_epoch': 47, 'seed': 42, 'job_index': receipt['job_index'],
            'compatible_CNN_tensor_shapes': shapes, 'changed_CNN_tensors': changed,
            'running_moments_unchanged': True,
            'transfer_allowlist': 'Only115 backbone tensors; new target head and T-only target moments. No source scaler/calibrator/sensor/F2.',
            'source25epoch_validator': 'Unmodified; this100-executed-epoch donor satisfies its duration condition'}


def verify_source_stop():
    receipt = read_json(resolve(SOURCE_STOP))
    require(receipt['completed_C_fits'] == 25 and receipt['allowed_seed'] == 42 and receipt['epochs_per_fit'] == 20,
            'Approved source study cap changed')
    require(receipt['do_not_start_remaining_seeds'] and receipt['all25_completion_and_model_prediction_hashes_verified'],
            'Source stop approval is not complete')
    root = resolve(SOURCE_PHASE1 / '26102026_execution/26102026_main_run_01')
    fits = []
    for path in sorted(root.glob('26102026_seed42_C_full_finetuned16_*/PHASE1_FIT_COMPLETE.json')):
        j = read_json(path)
        require(j['seed'] == 42 and j['executed_epochs'] == 20, 'Unexpected source C20 receipt')
        require([h['epoch'] for h in j['history']] == list(range(1, 21)), 'Incomplete C20 source history')
        require(sha256(path.parent / 'PHASE1_BEST_MODEL.pt') == j['selected_model_sha256'], 'Source C20 selected model SHA mismatch')
        require(sha256(path.parent / 'PHASE1_PREDICTIONS.json') == j['predictions_sha256'], 'Source C20 predictions SHA mismatch')
        fits.append({'receipt': manifest_identity(path), 'fit_identity': j['fit_identity'], 'job_index': j['job_index'],
                     'best_checkpoint_sha256': j['selected_model_sha256'], 'predictions_sha256': j['predictions_sha256']})
    require(len(fits) == 25 and {f['job_index'] for f in fits} == set(range(25)), 'Expected25 distinct approved C20 source jobs')
    return {'approved_stop_receipt': manifest_identity(resolve(SOURCE_STOP)), 'scientific_fit_receipts': fits,
            'source_original75_study_complete': False, 'approved25_scope_complete': True,
            'resource_gate_policy': protocol()['resources']['source_gate'],
            'process_checks_required_separately': ['phase_controller.py', 'phase_training.py', 'c20_controller.py', 'c20_train.py', 'compare100_controller.py', 'compare100_train.py', 'stop_after25_controller.py']}


def load_context(verify=True):
    frozen = protocol(); config = legacy_config(); run = config['run_id']
    require(tuple(config['cameras']) == CAMERAS and config['frames_per_camera'] == 16, 'Historical camera/frame policy changed')
    manifest = PROJECT / '03_preprocessing/processed_manifests' / run / 'eligible.json'
    splits = PROJECT / '04_evaluation_splits/train_validation_test' / run / 'fit_partitions.json'
    require(sha256(manifest) == frozen['cohort_sha256'] and sha256(splits) == frozen['splits_sha256'],
            'Frozen cohort or split source SHA changed')
    rows = read_json(manifest); index = {r['episode_index']: i for i, r in enumerate(rows)}
    lookup = {r['episode_index']: r for r in rows}; jobs_list = read_json(splits)
    evidence = {'cohort_source': manifest_identity(manifest), 'split_source': manifest_identity(splits)}
    targets = None
    if verify:
        targets, evidence['native_labels'] = verify_native_labels(config)
    evidence['cohort'] = verify_rows(rows, targets, frozen['cohort_expected'])
    excluded_path = manifest.parent / 'exclusions.csv'
    exclusions = list(csv.DictReader(excluded_path.open(newline='')))
    excluded_ids = {int(r['episode_index']) for r in exclusions}
    require(len(exclusions) == len(excluded_ids) == 820 and not excluded_ids & set(lookup), 'Exclusion identities changed')
    require(sha256(excluded_path) == read_json(manifest.parent / 'COMPLETE.json')['exclusions_sha256'], 'Exclusion source SHA drift')
    if targets is not None:
        require(excluded_ids | set(lookup) == set(targets), 'Native episodes missing from eligibility/exclusion partition')
    evidence['exclusions'] = {'source': manifest_identity(excluded_path), 'episodes': 820,
                             'reason_combinations': dict(Counter(r['final_exclusion_reasons'] for r in exclusions)),
                             'native_partition_complete': targets is not None, 'restored_excluded_episodes': 0}
    evidence['roles'] = verify_splits(jobs_list, rows)
    jobs = {j['id']: j for j in jobs_list}
    original = donor = None; bank_info = {}
    for name, condition in [('original', 'V1'), ('donor', 'V3')]:
        root = PROJECT / '03_preprocessing/visual_preprocessing/features' / run / condition
        receipt = read_json(root / 'COMPLETE.json'); path = root / 'features.npy'
        if verify:
            require(sha256(path) == receipt['sha256'], f'{name} feature-bank SHA mismatch')
            require(receipt['configuration_sha256'] == old_signature(config), 'Feature-bank configuration changed')
            for source, digest in receipt['implementation'].items():
                require(sha256(resolve(source)) == digest, 'Feature-bank producing source changed')
        array = np.load(path, mmap_mode='r', allow_pickle=False)
        require(array.shape[0] == len(rows), 'Feature-bank row count changed')
        pooled = pool_bank(array)
        if name == 'original': original = pooled
        else: donor = pooled
        bank_info[name] = {'receipt': manifest_identity(root / 'COMPLETE.json'), 'path': relative(path),
                           'sha256': receipt['sha256'], 'shape': list(array.shape), 'dtype': str(array.dtype),
                           'pooled_shape': list(pooled.shape), 'copied': False}
    evidence['feature_banks'] = bank_info
    sensor_path = PROJECT / '03_preprocessing/sensor_preprocessing/arrays' / run / 'statistics.npz'
    sensor_receipt = read_json(sensor_path.parent / 'COMPLETE.json')
    channels = ([f'observation.state.{i}' for i in range(14)] +
                [f'observation.velocity.{i}' for i in (0,1,2,3,4,5,7,8,9,10,11,12)] +
                ['observation.effort.6', 'observation.effort.13'])
    statistics = ['mean', 'std', 'median', 'min', 'max', 'q25', 'q75', 'range', 'RMS', 'normalized_progress_slope']
    require(sensor_receipt['channels'] == channels, 'Canonical28 measured sensor channels changed')
    require(sensor_receipt['features'] == [c + '.' + statistic for statistic in statistics for c in channels],
            'Canonical280 stat-major feature definitions changed')
    if verify:
        require(sha256(sensor_path) == sensor_receipt['sha256'], 'Sensor statistics SHA mismatch')
    with np.load(sensor_path, allow_pickle=False) as bank:
        sensor = bank['features'].copy(); sensor_index = sensor_join(bank['episode_ids'], sensor, index)
    sensor.flags.writeable = False
    require(sensor.shape == (4384, 280), 'Original sensor source cohort changed')
    evidence['sensor'] = {'receipt': manifest_identity(sensor_path.parent / 'COMPLETE.json'), 'path': relative(sensor_path),
                          'sha256': sensor_receipt['sha256'], 'shape': list(sensor.shape),
                          'eligible_join_count': len(rows), 'channels': sensor_receipt['channels'],
                          'feature_names': sensor_receipt['features'], 'not_force_torque': True}
    context = {'config': config, 'rows': rows, 'lookup': lookup, 'index': index, 'jobs': jobs,
               'original': original, 'donor': donor, 'sensor': sensor, 'sensor_index': sensor_index,
               'verification': evidence}
    pilot = get_job(context, frozen['pilot']['base_job_id'])
    evidence['pilot'] = verify_roles(pilot, lookup, pilot_outer_ids(context))
    for key, role in [('T', 'T'), ('V', 'V'), ('C', 'C'), ('meta', 'A'), ('outer_assessment', 'OUTER')]:
        require(evidence['pilot'][role]['episodes'] == frozen['pilot'][key], 'Prospectively frozen pilot role count changed')
    if verify:
        evidence['source_availability'] = verify_videos(config, rows)
        evidence['frozen100_reuse'] = verify_frozen_reuse(config, jobs, original, index)
        evidence['donor'] = verify_donor(config)
        evidence['approved_source_stop'] = verify_source_stop()
    return context


def prepare():
    context = load_context(verify=True); evidence = context['verification']; out = STUDY / '02_dataset_and_splits'
    immutable_json(out / 'DATASET_AND_SPLIT_VERIFICATION.json', {k: v for k, v in evidence.items() if k != 'exclusions'})
    immutable_json(out / 'EXCLUSION_AND_SCHEMA_VERIFICATION.json', {'exclusions': evidence['exclusions'],
        'sensor_channels_exact': evidence['sensor']['channels'], 'sensor_features_exact': evidence['sensor']['feature_names'],
        'complete_task_membership_per_role_verified': True})
    immutable_json(out / 'FIT_PARTITIONS.json', list(context['jobs'].values()))
    pilot = protocol()['pilot']; original = get_job(context, pilot['base_job_id'])
    immutable_json(out / 'PILOT_ROLES.json', {'base_job_id': original['id'], 'base_job': original,
        'meta_bank_ids': original['ids']['A'], 'outer_assessment_ids': pilot_outer_ids(context),
        'choice': pilot['choice'], 'original_A_semantics_preserved': True,
        'single_bank_not_nested_OOF': True, 'role_checks': evidence['pilot']})
    immutable_json(STUDY / '01_protocol_and_source_evidence/DONOR_SOURCE_VERIFICATION.json', evidence['donor'])
    immutable_json(STUDY / '01_protocol_and_source_evidence/APPROVED_SOURCE_STOP_VERIFICATION.json', evidence['approved_source_stop'])
    immutable_json(STUDY / '01_protocol_and_source_evidence/FROZEN100_REUSE_VERIFICATION.json', evidence['frozen100_reuse'])
    return context


if __name__ == '__main__':
    ctx = prepare()
    print(json.dumps({'verified': ctx['verification']['cohort'], 'jobs': len(ctx['jobs']),
                      'pilot': {k: v['episodes'] for k, v in ctx['verification']['pilot'].items()},
                      'reused_frozen100_epoch': ctx['verification']['frozen100_reuse']['pilot_selected_epoch']}))
