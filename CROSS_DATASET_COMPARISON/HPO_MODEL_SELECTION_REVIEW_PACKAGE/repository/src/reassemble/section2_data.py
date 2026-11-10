"""Reuse frozen inputs; obtain strictly nested branch inputs for fusion selection."""
import json
from pathlib import Path
import numpy as np
import torch
from .section1_features import sha
from .section1_models import VisualHead, neural_fit
from .section1b import fit_branch, guard_partition, write_json


def verify_manifest(path):
    manifest = json.loads(Path(path).read_text())
    for e in manifest['files']:
        p = Path(e['path'])
        assert p.stat().st_size == e['bytes'] and sha(p) == e['sha256'], str(p)
    return len(manifest['files'])


def quality_features(frame, base, config):
    names = ['hand.' + k for k in config['quality_visual']]
    names += [n + '.' + k for n in base['sensor']['channels'] for k in config['quality_sensor']]
    rows = {}
    wanted = set(zip(frame.recording_id, frame.segment_id))
    paths = []
    for rid in sorted(frame.recording_id.unique()):
        path = Path(base['audit_run']) / 'records' / (rid + '.json')
        record = json.loads(path.read_text())
        paths.append({'path': str(path), 'sha256': sha(path)})
        for segment in record['segments']:
            key = (rid, segment['segment_id'])
            if key not in wanted:
                continue
            values = [segment['video']['hand'].get(k) for k in config['quality_visual']]
            values += [segment['sensor'][n].get(k) for n in base['sensor']['channels'] for k in config['quality_sensor']]
            rows[key] = values
    quality = np.asarray([rows[(r.recording_id, r.segment_id)] for r in frame.itertuples()], dtype='float32')
    assert quality.shape == (len(frame), len(names))
    return quality, names, paths


def frozen_visual(base, fold, x):
    path = Path(base['run_dir']) / 'checkpoints' / f'rtdetr_fold{fold}.pt'
    checkpoint = torch.load(path, map_location='cpu', weights_only=True)
    model = VisualHead(checkpoint['width'], base).cuda()
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    normalized = np.nan_to_num((x - checkpoint['normalizer_mean'].numpy()) / checkpoint['normalizer_std'].numpy(), nan=0, posinf=0, neginf=0)
    with torch.inference_mode():
        z = np.concatenate([model(torch.tensor(a, device='cuda'))[1].cpu().numpy() for a in np.array_split(normalized, max(1, len(x) // 256))])
    return z


def inner_inputs(config, base, frame, arrays, outer, inner, progress):
    """Reuse saved subfolds: each training prediction excludes its recording and inner assessment."""
    k, j = outer['fold'], inner
    folder = Path(config['run_dir']) / 'inputs'
    path = folder / f'outer{k}_inner{j}.npz'
    detail_path = path.with_suffix('.json')
    if path.exists():
        with np.load(path) as z:
            return {key: z[key] for key in z.files}
    source = Path(config['section1b_run']) / 'stacking' / f'outer{k}_inner{j}'
    detail = json.loads(source.with_suffix('.json').read_text())
    y = frame.failure.to_numpy(dtype=int)
    indices = lambda groups: np.flatnonzero(frame.recording_id.isin(groups))
    tr = indices(detail['train_recordings'])
    va = indices(detail['validation_recordings'])
    plan = [(indices(s['train_recordings']), indices(s['validation_recordings'])) for s in detail['subfolds']]
    guard_partition(frame, tr, va, plan)
    probabilities = np.full((len(frame), 2), np.nan)
    logs = []
    for subindex, (st, sv) in enumerate(plan):
        deeper = [(np.intersect1d(a, st), b) for t, (a, b) in enumerate(plan) if t != subindex]
        guard_partition(frame, st, sv, deeper)
        cache = folder / f'outer{k}_inner{j}_sub{subindex}.npz'
        if cache.exists():
            with np.load(cache) as z:
                assert np.array_equal(z['rows'], sv)
                probabilities[sv] = z['probabilities']
            logs.append(json.loads(cache.with_suffix('.json').read_text()))
            continue
        entry = {'subfold': subindex, 'train_rows': st.tolist(), 'test_rows': sv.tolist(),
                 'selection_partitions': [{'train_rows': a.tolist(), 'validation_rows': b.tolist()} for a, b in deeper], 'branches': {}}
        for column, (kind, key) in enumerate([('rtdetr', 'visual'), ('sensor_statistics', 'statistics')]):
            seed = config['seed'] + 100000 + k * 10000 + j * 1000 + subindex * 100
            probabilities[sv, column], entry['branches'][kind] = fit_branch(kind, arrays[key], y, st, sv, deeper, base, seed, seed + 99)
        np.savez_compressed(cache, rows=sv, probabilities=probabilities[sv])
        write_json(cache.with_suffix('.json'), entry)
        logs.append(entry)
        progress(config, f'Outer {k+1}/5 inner {j+1}/4 nested branch inputs {subindex+1}/4')
    assert np.isfinite(probabilities[tr]).all() and np.isnan(probabilities[va]).all()
    with np.load(source.with_suffix('.npz')) as z:
        assert np.array_equal(z['validation_rows'], va)
        probabilities[va] = z['probabilities']
    # Same already-selected head and seed as Section 1B; only representations are newly saved.
    visual_info = detail['branches']['rtdetr']
    joined = np.concatenate([tr, va])
    output, refit = neural_fit('rtdetr', arrays['visual'], y, tr, joined,
                               [visual_info['selected']], base, visual_info['refit_seed'])
    raw, representation = output[visual_info['selected']]
    calibration = visual_info['calibration']
    p = 1 / (1 + np.exp(-np.clip(raw[len(tr):] * calibration['coefficient'] + calibration['intercept'], -40, 40)))
    difference = float(np.max(abs(p - probabilities[va, 0])))
    assert difference < 1e-5, ('inner visual parity', k, j, difference)
    result = {'train_rows': tr, 'validation_rows': va, 'train_probabilities': probabilities[tr],
              'validation_probabilities': probabilities[va], 'train_visual': representation[:len(tr)],
              'validation_visual': representation[len(tr):]}
    np.savez_compressed(path, **result)
    write_json(detail_path, {'source': str(source), 'max_visual_probability_difference': difference,
                            'visual_refit': refit, 'subfolds': [f'outer{k}_inner{j}_sub{t}.json' for t in range(4)],
                            'selection_fold_count_at_extra_depth': 3})
    return result
