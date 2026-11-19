"""Recalculate published point estimates from retained assessment predictions."""
from pathlib import Path
import re
import numpy as np
from reassemble.section1_report import METRICS, metrics
from .common import read, identity, TASKS


def vector(values):
    return np.array([values[m]['estimate'] if isinstance(values[m], dict) else values[m] for m in METRICS], float)


def check(actual, reported, label):
    np.testing.assert_allclose(actual, vector(reported), atol=1e-12, rtol=1e-12, err_msg=label)


def audit(c, frame):
    root = Path(c['run_dir']); base = read(c['section1_config'])
    y = frame.failure.to_numpy(int); records = []; cached = {}
    historical = {'V-HIST': 'rtdetr', 'S-HIST': 'patchtst', 'S-STATS': 'sensor_statistics'}
    def predictions(task, name):
        key = task, name
        if key not in cached:
            if name in historical:
                path = Path(base['run_dir'])/'predictions'/(historical[name]+'_perm00.npz')
            else:
                path = root/TASKS[task-1]/('predictions.npz' if task == 3 else name+'_predictions.npz')
            with np.load(path) as z:
                if task == 3:
                    value = {field: z[name+'_'+field] for field in ['p', 'hard', 'seed_p', 'seed_hard']}
                    value['fold'] = z['fold']
                else:
                    assert np.array_equal(z['y'], y), path
                    value = {field: z[field] for field in z.files}
            assert np.isfinite(value['p']).all() and np.all((value['p'] >= 0) & (value['p'] <= 1)), path
            for _, rows in frame.groupby('recording_id'):
                assert len(np.unique(value['fold'][rows.index])) == 1, path
            if 'seed_p' in value:
                np.testing.assert_allclose(value['p'], value['seed_p'].mean(0), rtol=0, atol=1e-12)
            cached[key] = value
            records.append(identity(path))
        return cached[key]
    audited = []
    for task, relative in [(1, 'comparison'), (1, 'finetune_comparison'), (2, 'comparison'), (2, 'hybrid_comparison'), (3, 'comparison')]:
        path = root/TASKS[task-1]/relative/'results.json'
        if not path.exists():
            continue
        report = read(path); points = {}
        for name, record in report['models'].items():
            p = predictions(task, name)
            points[name] = np.asarray(metrics(y, p['p'], p['hard']))
            check(points[name], record['metrics'], str(path)+' '+name)
            for fold, values in record['folds'].items():
                ix = p['fold'] == int(fold)
                check(metrics(y[ix], p['p'][ix], p['hard'][ix]), values, name+' fold'+fold)
            for index, seed in enumerate(c['seeds']):
                if str(seed) in record['seeds']:
                    check(metrics(y, p['seed_p'][index], p['seed_hard'][index]), record['seeds'][str(seed)], name+' seed'+str(seed))
        for contrast, record in report['contrasts'].items():
            a, b = contrast.split(' minus ')
            check(points[a]-points[b], record['metrics'], contrast)
            for fold, values in record['fold_differences'].items():
                check(vector(report['models'][a]['folds'][fold])-vector(report['models'][b]['folds'][fold]), values, contrast+' fold'+fold)
        audited.append(identity(path))
    robust = root/TASKS[3]/'results.json'
    if robust.exists():
        from .robust_report import LABELS
        report = read(robust); assembled = {}; names = None; branch = None; thresholds = np.zeros((len(y), 2))
        for label in LABELS:
            for k in range(5):
                path = root/TASKS[3]/f'outer{k}_{label}.npz'
                with np.load(path) as z:
                    if names is None:
                        names = z['names'].copy(); branch = np.zeros((len(names), len(y), 2))
                    assert np.array_equal(names, z['names'])
                    rows = z['rows']
                    if label not in assembled:
                        assembled[label] = {v: np.zeros((len(names), len(y))) for v in ['p', 'hard']}
                    for v in ['p', 'hard']:
                        assembled[label][v][:, rows] = z[v]
                    branch[:, rows] = z['branch_p']; thresholds[rows] = z['branch_thresholds']
                records.append(identity(path))
        for i, label in enumerate(['U_VISUAL', 'U_SENSOR']):
            assembled[label] = dict(p=branch[:, :, i], hard=branch[:, :, i] >= thresholds[:, i])
        groups = {}
        for i, name in enumerate(names):
            groups.setdefault(re.sub(r'_r\d+$', '', str(name)), []).append(i)
        points = {}
        for condition, models in report['absolute'].items():
            for label, values in models.items():
                p = assembled[label]
                actual = np.mean([metrics(y, p['p'][i], p['hard'][i]) for i in groups[condition]], axis=0)
                check(actual, values, condition+' '+label); points[condition, label] = actual
        for condition, comparisons in report['paired'].items():
            for contrast, values in comparisons.items():
                if contrast.endswith(' degraded minus clean'):
                    label = contrast.removesuffix(' degraded minus clean')
                    actual = points[condition, label]-points['clean', label]
                else:
                    a, b = contrast.split(' minus '); b = b.removeprefix('remaining ')
                    actual = points[condition, a]-points[condition, b]
                check(actual, values, condition+' '+contrast)
        primary = np.mean([points[key, 'augmented_A-ADAPTIVE']-points[key, 'augmented_F2'] for key in report['seen_conditions']], axis=0)
        check(primary, report['primary_seen_family_contrast'], 'Task4 primary')
        audited.append(identity(robust))
    videos = read(root/'00_protocol_and_preservation/encoded_video_metadata.json')
    for entry in videos['entries']:
        stat = Path(entry['path']).stat()
        assert stat.st_size == entry['size_bytes'] and stat.st_mtime_ns == entry['mtime_ns'], entry['path']
    return dict(passed=True, point_metric_reports=audited, prediction_files=records, encoded_videos_unchanged=len(videos['entries']),
                tolerance=1e-12, scope='Recomputed all primary/secondary comparison point metrics, clean fold/seed results, paired point differences, and robustness means directly from predictions. Confidence intervals retain the declared deterministic paired-bootstrap implementation.')
