"""Read-only scientific/preservation checks; write a new Section 1B audit."""
import json
from pathlib import Path
import subprocess
import sys
import shutil
from datetime import datetime, timezone
from importlib.metadata import version

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
import numpy as np
import pandas as pd
from reassemble.section1_features import cohort, sha
from reassemble.section1b import verify_section1, guard_partition, index_plan
from reassemble.section1_models import permute_labels


def main():
    config = json.loads(Path('configs/reassemble/section1b.json').read_text())
    run = Path(config['run_dir'])
    base = json.loads(Path(config['section1_config']).read_text())
    old = Path(config['section1_run'])
    entries = verify_section1(config)
    for name in ['training_implementation.json']:
        for path, expected in json.loads((old / name).read_text())['source_sha256'].items():
            assert sha(Path(path)) == expected, path
    for path, expected in json.loads((run / 'implementation.json').read_text())['source_sha256'].items():
        assert sha(Path(path)) == expected, path
    protected = json.loads(Path('/tmp/phm_retirement_protected_before.json').read_text())
    for entry in protected:
        stat = Path(entry['path']).lstat()
        assert (stat.st_size, stat.st_mtime_ns, stat.st_mode) == (entry['size'], entry['mtime_ns'], entry['mode']), entry['path']
    raw = pd.read_parquet('runs/reassemble/20260927T141645Z-inventory/recordings.parquet')
    for row in raw.itertuples():
        stat = (Path('../datasets/REASSEMBLE/raw/data') / row.filename).stat()
        assert (stat.st_size, stat.st_mtime_ns) == (row.size_bytes, row.mtime_ns), row.filename
    blob = int(subprocess.check_output(['git', 'cat-file', '-s', '284ccffbfe2b61f2abc91d97f5db0d0ee7abd628']))
    assert blob == 14047735808
    frame = cohort(base)
    splits = json.loads(Path(base['splits']).read_text())
    y = frame.failure.to_numpy(dtype=int)
    with np.load(old / 'predictions/sensor_statistics_perm00.npz') as z:
        frozen_folds = z['fold'].copy()
    for permutation in range(config['permutations'] + 1):
        expected = y if permutation == 0 else permute_labels(frame, base['seed'] + 10000 + permutation)
        with np.load(run / f'sensor_controls/predictions/sensor_statistics_perm{permutation:02d}.npz') as z:
            assert np.array_equal(z['y'], expected) and np.array_equal(z['fold'], frozen_folds)
            assert len(z['p']) == len(frame) and np.isfinite(z['p']).all()
    parity = []
    with np.load(run / 'stacking/oof.npz') as final:
        assert np.array_equal(final['y'], y) and np.array_equal(final['fold'], frozen_folds)
        assert np.isfinite(final['p']).all()
        for outer in splits['folds']:
            k = outer['fold']
            tr = np.flatnonzero(frame.recording_id.isin(outer['train_recordings']))
            te = np.flatnonzero(frame.recording_id.isin(outer['test_recordings']))
            guard_partition(frame, tr, te, index_plan(frame, outer))
            detail = json.loads((run / f'stacking/outer{k}.json').read_text())
            with np.load(run / f'stacking/outer{k}.npz') as z:
                assert np.array_equal(z['train_rows'], tr) and np.array_equal(z['test_rows'], te)
                assert np.array_equal(z['p'], final['p'][te]) and np.array_equal(z['hard'], final['hard'][te])
                assert z['training_branch_oof'].shape == (len(tr), 2)
                assert np.isfinite(z['training_branch_oof']).all()
                for column, name in enumerate(['rtdetr', 'sensor_statistics']):
                    with np.load(old / f'predictions/{name}_perm00.npz') as original:
                        difference = float(np.max(abs(z['test_branch_probabilities'][:, column] - original['p'][te])))
                    assert difference <= 1e-5
                    assert difference == detail['refits'][name]['max_frozen_probability_difference']
                    parity.append({'fold': k, 'branch': name, 'max_probability_difference': difference})
                for j, inner in enumerate(detail['inner']):
                    it = np.flatnonzero(frame.recording_id.isin(inner['train_recordings']))
                    iv = np.flatnonzero(frame.recording_id.isin(inner['validation_recordings']))
                    plan = [(np.flatnonzero(frame.recording_id.isin(s['train_recordings'])), np.flatnonzero(frame.recording_id.isin(s['validation_recordings']))) for s in inner['subfolds']]
                    guard_partition(frame, it, iv, plan)
                    assert not (set(it) | set(iv)) & set(te)
                    with np.load(run / f'stacking/outer{k}_inner{j}.npz') as checkpoint:
                        assert np.array_equal(checkpoint['validation_rows'], iv)
                        assert np.array_equal(checkpoint['probabilities'], z['training_branch_oof'][np.searchsorted(tr, iv)])
            assert len(detail['stacker']['coefficient']) == 2
            assert np.isfinite(detail['stacker']['coefficient']).all()
    log = (run / 'execution.log').read_text()
    assert not any(word in log for word in ['Traceback', 'ConvergenceWarning', 'RuntimeWarning'])
    pip = subprocess.run([sys.executable, '-B', '-m', 'pip', 'check'], capture_output=True, text=True)
    assert pip.returncode == 0, pip.stdout
    subprocess.run(['git', 'diff', '--check'], check=True)
    audit = {
        'utc': datetime.now(timezone.utc).isoformat(),
        'command': 'ma_thesis_env/bin/python -B scripts/reassemble/08_validate_section1b.py',
        'implementation_commit': json.loads((run / 'implementation.json').read_text())['git_commit'],
        'section1_manifest_entries_unchanged': entries,
        'protected_entries_metadata_unchanged': len(protected),
        'protected_check': 'lstat: size, mtime_ns, mode; no credential contents read',
        'raw_hdf5_metadata_unchanged': len(raw),
        'raw_check': 'stat only: size and mtime_ns; no source payload read',
        'retained_git_blob_bytes': blob,
        'sensor_control_runs_validated': config['permutations'] + 1,
        'inner_branch_partitions_validated': 20,
        'branch_parity': parity,
        'outer_predictions': len(frame),
        'tests': {'prior_preexecution_result': '47 passed in 7.18s', 'scope': 'tests/reassemble; includes six Section1B tests'},
        'pip_check': pip.stdout.strip(),
        'git_diff_check': 'passed',
        'runtime_warning_scan': 'no Traceback, ConvergenceWarning or RuntimeWarning in successful run',
        'free_bytes': shutil.disk_usage('.').free,
        'versions': {name: version(name) for name in ['numpy', 'pandas', 'scipy', 'scikit-learn', 'torch', 'threadpoolctl']},
        'limitations': 'Cluster bootstrap conditions on fitted models; same-cohort adaptive exploratory follow-up; 19 permutations give minimum p=0.05.',
    }
    with (run / 'validation.json').open('x') as f:
        json.dump(audit, f, indent=2)
        f.write('\n')
    print(json.dumps({k: audit[k] for k in ['section1_manifest_entries_unchanged', 'protected_entries_metadata_unchanged', 'raw_hdf5_metadata_unchanged', 'outer_predictions', 'pip_check']}))


if __name__ == '__main__':
    main()
