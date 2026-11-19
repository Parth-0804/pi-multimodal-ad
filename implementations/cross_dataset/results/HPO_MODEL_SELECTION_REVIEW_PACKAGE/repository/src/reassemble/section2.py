"""Frozen-branch clean fusion, with checkpointed nested selection and three seeds."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import torch
from sklearn.metrics import average_precision_score
from threadpoolctl import threadpool_limits
from .section1_features import sha
from .section1_models import load_features, verify_splits, calibrate, sigmoid
from .section1b import write_json, choose_threshold, index_plan, guard_partition
from .section2_data import verify_manifest, quality_features, inner_inputs, frozen_visual
from .section2_models import fit_head


def progress(config, stage):
    now = datetime.now(timezone.utc).isoformat()
    run = Path(config['run_dir'])
    (run / 'live_status.json').write_text(json.dumps({'utc': now, 'stage': stage}, indent=2) + '\n')
    Path('docs/reassemble/SECTION_2_CONTINUATION.md').write_text(
        '# Section 2 continuation\n\n' + now + '\n\nStatus: **' + stage + '**.\n\n'
        'Run: `' + str(run) + '`. Config: `configs/reassemble/section2.json`.\n'
        'Protocol: `docs/reassemble/SECTION_2_PROTOCOL.md`.\n'
        'Entry point: `ma_thesis_env/bin/python -B scripts/reassemble/09_section2.py`.\n'
        'Inspect execution.log, live_status.json and active processes before resuming.\n'
        'The driver resumes completed input and fit checkpoints; do not edit fitted code/config.\n'
        'Section 1 and 1B evidence and their continuation files remain frozen.\n'
        'No corruption, audio, PatchTST tuning or backbone fine-tuning is authorized.\n'
        'Complete the A–V report at artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md,\n'
        'then STOP before Section 3.\n')
    print(now, stage, flush=True)


def bundle(rows, visual, probabilities, arrays, quality, action):
    return {'visual': visual, 'statistics': arrays['statistics'][rows],
            'probabilities': probabilities, 'quality': quality[rows],
            'action': action[rows], 'availability': np.ones((len(rows), 2), dtype='float32')}


def cached_fit(path, kind, train, test, labels, settings, config, seed, ablations=None):
    if path.exists():
        with np.load(path) as z:
            return {key: z[key] for key in z.files}, json.loads(path.with_suffix('.json').read_text())
    output, info = fit_head(kind, train, test, labels, settings, config, seed, ablations,
                            path.with_suffix('.pt') if ablations is not None else None)
    flat = {k: v for k, v in output.items() if k != 'ablations'}
    for name, result in output.get('ablations', {}).items():
        for key, values in result.items():
            flat[name + '_' + key] = values
    write_json(path.with_suffix('.json'), info)
    np.savez_compressed(path, **flat)
    return flat, info


def train_outer(config, base, frame, arrays, quality, action, outer):
    run = Path(config['run_dir'])
    k = outer['fold']
    final = run / 'predictions' / f'outer{k}.npz'
    if final.exists():
        return
    started = time.perf_counter()
    tr = np.flatnonzero(frame.recording_id.isin(outer['train_recordings']))
    te = np.flatnonzero(frame.recording_id.isin(outer['test_recordings']))
    guard_partition(frame, tr, te, index_plan(frame, outer))
    y = frame.failure.to_numpy(dtype=int)
    n = len(y)
    kinds = ['F3', 'F4', 'F5', 'F6']
    candidates = {kind: config['concat_configs'] if kind == 'F3' else config['gate_configs'] for kind in kinds}
    inner_raw = {kind: np.full((len(candidates[kind]), 3, n), np.nan) for kind in kinds}
    scores = {kind: [[] for _ in candidates[kind]] for kind in kinds}
    inner_timing = {kind: 0. for kind in kinds}
    for j in range(4):
        data = inner_inputs(config, base, frame, arrays, outer, j, progress)
        it, iv = data['train_rows'], data['validation_rows']
        train = bundle(it, data['train_visual'], data['train_probabilities'], arrays, quality, action)
        test = bundle(iv, data['validation_visual'], data['validation_probabilities'], arrays, quality, action)
        for kind in kinds:
            for c, settings in enumerate(candidates[kind]):
                for s, seed in enumerate(config['seeds']):
                    path = run / 'fits' / f'{kind}_outer{k}_inner{j}_c{c}_s{s}.npz'
                    result, metadata = cached_fit(path, kind, train, test, y[it], settings, config, seed + 1000 * k + 100 * j)
                    inner_raw[kind][c, s, iv] = result['raw']
                    inner_timing[kind] += metadata['training_seconds']
                score = average_precision_score(y[iv], sigmoid(inner_raw[kind][c][:, iv]).mean(0))
                scores[kind][c].append(float(score))
        progress(config, f'Outer {k+1}/5 inner {j+1}/4: all fusion candidates and three seeds complete')
    # Fold-specific Section 1 representation and exact Section 1B branch probabilities.
    visual = frozen_visual(base, k, arrays['visual'])
    with np.load(Path(config['section1b_run']) / 'stacking' / f'outer{k}.npz') as z:
        assert np.array_equal(z['train_rows'], tr) and np.array_equal(z['test_rows'], te)
        train_probs, test_probs = z['training_branch_oof'].copy(), z['test_branch_probabilities'].copy()
    train = bundle(tr, visual[tr], train_probs, arrays, quality, action)
    test = bundle(te, visual[te], test_probs, arrays, quality, action)
    result = {'test_rows': te, 'y': y[te]}
    uniform_threshold = choose_threshold(y[tr], train_probs.mean(1))
    result['F1_p'] = test_probs.mean(1)
    result['F1_hard'] = (result['F1_p'] >= uniform_threshold).astype(int)
    summary = {'fold': k, 'uniform_threshold': uniform_threshold, 'models': {}}
    permutation = np.random.default_rng(config['seed'] + 90000 + k).permutation(len(te))
    result['action_permutation'] = permutation
    for kind in kinds:
        selected = int(np.argmax([np.mean(v) for v in scores[kind]]))
        inner = inner_raw[kind][selected][:, tr]
        assert np.isfinite(inner).all()
        ablation_names = []
        if kind in ['F4', 'F6']:
            ablation_names += ['action_permuted', 'action_zero']
        if kind in ['F5', 'F6']:
            ablation_names += ['quality_neutral']
        seed_predictions, seed_weights, inner_probabilities, fit_details = [], [], [], []
        ablation_predictions = {name: [] for name in ablation_names}
        ablation_weights = {name: [] for name in ablation_names}
        for s, seed in enumerate(config['seeds']):
            path = run / 'fits' / f'{kind}_outer{k}_final_s{s}.npz'
            output, info = cached_fit(path, kind, train, test, y[tr], candidates[kind][selected], config,
                                      seed + 1000 * k + 99, {'names': ablation_names, 'permutation': permutation})
            if kind == 'F3':
                p, _, calibration = calibrate(inner[s], y[tr], output['raw'])
                ip = sigmoid(inner[s] * calibration['coefficient'] + calibration['intercept'])
                info = {**info, 'calibration': calibration}
            else:
                p, ip = sigmoid(output['raw']), sigmoid(inner[s])
                seed_weights.append(output['weights'])
                for name in ablation_names:
                    ablation_predictions[name].append(sigmoid(output[name + '_raw']))
                    ablation_weights[name].append(output[name + '_weights'])
            seed_predictions.append(p)
            inner_probabilities.append(ip)
            fit_details.append(info)
        p = np.mean(seed_predictions, axis=0)
        threshold = choose_threshold(y[tr], np.mean(inner_probabilities, axis=0))
        result[kind + '_p'], result[kind + '_hard'] = p, (p >= threshold).astype(int)
        result[kind + '_seed_p'] = np.stack(seed_predictions)
        if seed_weights:
            result[kind + '_seed_weights'] = np.stack(seed_weights)
            result[kind + '_weights'] = np.mean(seed_weights, axis=0)
        for name in ablation_names:
            result[kind + '_' + name + '_p'] = np.mean(ablation_predictions[name], axis=0)
            result[kind + '_' + name + '_weights'] = np.mean(ablation_weights[name], axis=0)
        summary['models'][kind] = {'selected_config': selected, 'settings': candidates[kind][selected],
                                  'inner_AP': scores[kind], 'threshold': threshold,
                                  'inner_training_seconds': inner_timing[kind], 'final_fits': fit_details}
    summary['outer_seconds'] = time.perf_counter() - started
    write_json(final.with_suffix('.json'), summary)
    np.savez_compressed(final, **result)
    progress(config, f'Outer {k+1}/5 clean fusion and context ablations complete')


def collect(config, base, frame):
    run = Path(config['run_dir'])
    dest = run / 'predictions/oof.npz'
    if dest.exists():
        return
    result = {'y': frame.failure.to_numpy(dtype=int), 'fold': np.full(len(frame), -1)}
    for k in range(5):
        with np.load(run / 'predictions' / f'outer{k}.npz') as z:
            te = z['test_rows']
            result['fold'][te] = k
            for name in z.files:
                if name in ['test_rows', 'y', 'action_permutation']:
                    continue
                values = z[name]
                if '_seed_' in name:
                    if name not in result:
                        result[name] = np.full((3, len(frame)) + values.shape[2:], np.nan)
                    result[name][:, te] = values
                else:
                    if name not in result:
                        result[name] = np.full((len(frame),) + values.shape[1:], np.nan)
                    result[name][te] = values
    for name, path in [('U1', Path(base['run_dir']) / 'predictions/sensor_statistics_perm00.npz'),
                       ('U2', Path(base['run_dir']) / 'predictions/rtdetr_perm00.npz'),
                       ('F2', Path(config['section1b_run']) / 'stacking/oof.npz')]:
        with np.load(path) as z:
            assert np.array_equal(z['y'], result['y']) and np.array_equal(z['fold'], result['fold'])
            for key in ['p', 'hard']:
                result[name + '_' + key] = z[key]
    assert all(np.isfinite(a).all() for a in result.values())
    np.savez_compressed(dest, **result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/reassemble/section2.json')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    run = Path(config['run_dir'])
    import fcntl
    lock = (run / 'execution.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert config == json.loads((run / 'config.json').read_text())
    base = json.loads(Path(config['section1_config']).read_text())
    manifests = [Path(base['run_dir']) / 'final_output_manifest.json', Path(config['section1b_run']) / 'output_manifest.json']
    for path in manifests:
        verify_manifest(path)
    for folder in ['inputs', 'fits', 'predictions']:
        (run / folder).mkdir(exist_ok=True)
    torch.set_num_threads(config['threads'])
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    frame, arrays = load_features(base)
    del arrays['sensor']
    splits = json.loads(Path(base['splits']).read_text())
    verify_splits(frame, splits)
    quality, names, identities = quality_features(frame, base, config)
    action = np.stack([(frame.action == a).to_numpy(dtype='float32') for a in config['actions']], axis=1)
    source_paths = sorted(Path('src/reassemble').glob('section*.py')) + [Path('scripts/reassemble/09_section2.py')]
    implementation = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                      'source_sha256': {str(p): sha(p) for p in source_paths}, 'split_sha256': splits['sha256'],
                      'command': ['scripts/reassemble/09_section2.py', '--config', args.config],
                      'config_sha256': sha(run / 'config.json'), 'quality_fields': names,
                      'constant_quality_fields': [name for j, name in enumerate(names) if np.nanstd(quality[:, j]) < 1e-6],
                      'quality_source_identities': identities, 'frozen_manifests': {str(p): sha(p) for p in manifests},
                      'device': torch.cuda.get_device_name(), 'utc': datetime.now(timezone.utc).isoformat()}
    target = run / 'implementation.json'
    if target.exists():
        previous = json.loads(target.read_text())
        assert previous['source_sha256'] == implementation['source_sha256']
        assert previous['config_sha256'] == implementation['config_sha256']
    else:
        write_json(target, implementation)
    with threadpool_limits(limits=config['blas_threads'], user_api='blas'):
        for outer in splits['folds']:
            train_outer(config, base, frame, arrays, quality, action, outer)
        collect(config, base, frame)
        from .section2_report import assess
        assess(config, frame)
    for path in manifests:
        verify_manifest(path)
    progress(config, 'Section 2 computation complete; final preservation audit and report review pending')


if __name__ == '__main__':
    main()
