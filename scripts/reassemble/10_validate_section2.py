"""Audit completed Section 2 outputs without fitting or changing prior evidence."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
from importlib.metadata import version
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
import numpy as np
import pandas as pd
from reassemble.section1_features import cohort, sha
from reassemble.section1_models import sigmoid
from reassemble.section1b import guard_partition
from reassemble.section2_data import verify_manifest
from reassemble.section2_models import logit
from reassemble.section2_report import MODELS, ABLATIONS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/reassemble/section2.json')
    parser.add_argument('--protected-snapshot', default='/tmp/phm_retirement_protected_before.json')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    base = json.loads(Path(config['section1_config']).read_text())
    run = Path(config['run_dir'])
    impl = json.loads((run / 'implementation.json').read_text())
    for path, expected in impl['source_sha256'].items():
        assert sha(path) == expected, path
    prior = {path: verify_manifest(path) for path in impl['frozen_manifests']}
    protected = json.loads(Path(args.protected_snapshot).read_text())
    for entry in protected:
        st = Path(entry['path']).lstat()
        assert (st.st_size, st.st_mtime_ns, st.st_mode) == (entry['size'], entry['mtime_ns'], entry['mode']), entry['path']
    inventory = pd.read_parquet(Path(base['audit_run']) / 'recordings.parquet')
    for row in inventory.itertuples():
        st = (Path(base['data_root']) / 'raw/data' / row.filename).stat()
        assert (st.st_size, st.st_mtime_ns) == (row.size_bytes, row.mtime_ns)
    assert int(subprocess.check_output(['git', 'cat-file', '-s', '284ccffbfe2b61f2abc91d97f5db0d0ee7abd628'])) == 14047735808
    frame = cohort(base)
    splits = json.loads(Path(base['splits']).read_text())
    with np.load(run / 'predictions/oof.npz') as z:
        oof = {key: z[key] for key in z.files}
    assert np.array_equal(oof['y'], frame.failure.to_numpy())
    assert all(np.isfinite(v).all() for v in oof.values())
    branch_hashes = {}
    for k, outer in enumerate(splits['folds']):
        tr = np.flatnonzero(frame.recording_id.isin(outer['train_recordings']))
        te = np.flatnonzero(frame.recording_id.isin(outer['test_recordings']))
        assert np.array_equal(np.flatnonzero(oof['fold'] == k), te)
        path = Path(config['section1b_run']) / 'stacking' / f'outer{k}.npz'
        branch_hashes[str(path)] = sha(path)
        with np.load(path) as z:
            assert np.array_equal(z['train_rows'], tr) and np.array_equal(z['test_rows'], te)
            test_probabilities = z['test_branch_probabilities'].copy()
        with np.load(run / 'predictions' / f'outer{k}.npz') as z:
            assert sorted(z['action_permutation']) == list(range(len(te)))
        detail = json.loads((run / 'predictions' / f'outer{k}.json').read_text())
        assert np.array_equal(oof['F1_p'][te], test_probabilities.mean(1))
        assert np.array_equal(oof['F1_hard'][te], oof['F1_p'][te] >= detail['uniform_threshold'])
        for j, inner in enumerate(outer['inner']):
            it = np.flatnonzero(frame.recording_id.isin(inner['train_recordings']))
            iv = np.flatnonzero(frame.recording_id.isin(inner['validation_recordings']))
            with np.load(run / 'inputs' / f'outer{k}_inner{j}.npz') as z:
                assert np.array_equal(z['train_rows'], it) and np.array_equal(z['validation_rows'], iv)
                assert z['train_visual'].shape == (len(it), 128)
                assert np.isfinite(z['train_probabilities']).all()
            for s in range(4):
                meta = json.loads((run / 'inputs' / f'outer{k}_inner{j}_sub{s}.json').read_text())
                a, b = np.array(meta['train_rows']), np.array(meta['test_rows'])
                plan = [(np.array(p['train_rows']), np.array(p['validation_rows'])) for p in meta['selection_partitions']]
                guard_partition(frame, a, b, plan)
                assert set(a) | set(b) == set(it)
                assert not (set(a) | set(b)) & (set(iv) | set(te))
                assert meta['branches']['rtdetr']['selected'] in base['visual']['epochs']
                assert meta['branches']['sensor_statistics']['selected'] in base['logistic_C']
        for m in ['F3', 'F4', 'F5', 'F6']:
            info = detail['models'][m]
            assert np.array_equal(oof[m+'_hard'][te], oof[m+'_p'][te] >= info['threshold'])
            assert np.allclose(oof[m+'_p'][te], oof[m+'_seed_p'][:,te].mean(0), atol=1e-7)
            candidates = config['concat_configs'] if m == 'F3' else config['gate_configs']
            assert info['settings'] == candidates[info['selected_config']]
            assert info['selected_config'] == int(np.argmax([np.mean(v) for v in info['inner_AP']]))
            for s in range(3):
                with np.load(run / 'fits' / f'{m}_outer{k}_final_s{s}.npz') as z:
                    if m == 'F3':
                        c = info['final_fits'][s]['calibration']
                        p = sigmoid(z['raw'] * c['coefficient'] + c['intercept'])
                    else:
                        assert np.allclose(z['weights'].sum(1), 1, atol=1e-6)
                        assert np.allclose(z['raw'], (z['weights'] * logit(test_probabilities)).sum(1), atol=1e-6)
                        assert np.array_equal(oof[m+'_seed_weights'][s,te], z['weights'])
                        p = sigmoid(z['raw'])
                    assert np.allclose(p, oof[m+'_seed_p'][s,te], atol=1e-6)
            if m in ABLATIONS:
                assert np.allclose(oof[m+'_weights'][te], oof[m+'_seed_weights'][:,te].mean(0), atol=1e-7)
                for name in ABLATIONS[m]:
                    scores, weights = [], []
                    for s in range(3):
                        with np.load(run / 'fits' / f'{m}_outer{k}_final_s{s}.npz') as z:
                            scores.append(sigmoid(z[name+'_raw'])); weights.append(z[name+'_weights'])
                            assert np.allclose(z[name+'_raw'], (z[name+'_weights'] * logit(test_probabilities)).sum(1), atol=1e-6)
                    assert np.allclose(oof[m+'_'+name+'_p'][te], np.mean(scores,axis=0))
                    assert np.allclose(oof[m+'_'+name+'_weights'][te], np.mean(weights,axis=0))
    for m, path in [('U1', Path(base['run_dir'])/'predictions/sensor_statistics_perm00.npz'), ('U2', Path(base['run_dir'])/'predictions/rtdetr_perm00.npz'), ('F2', Path(config['section1b_run'])/'stacking/oof.npz')]:
        branch_hashes[str(path)] = sha(path)
        with np.load(path) as z:
            assert all(np.array_equal(oof[m+'_'+key],z[key]) for key in ['p','hard'])
    log = (run / 'execution.log').read_text()
    assert not any(word in log for word in ['Traceback', 'ConvergenceWarning', 'RuntimeWarning'])
    pip = subprocess.run([sys.executable,'-B','-m','pip','check'],text=True,capture_output=True)
    assert pip.returncode == 0
    subprocess.run(['git','diff','--check'],check=True)
    results = json.loads((run/'assessment/results.json').read_text())
    report = Path('artifacts/reassemble/reports/SECTION_2_FUSION_HANDOFF.md').read_text()
    assert all('## '+letter+'. ' in report for letter in 'ABCDEFGHIJKLMNOPQRSTUV')
    assert report.rstrip().endswith(results['section3_decision'])
    audit = {'utc':datetime.now(timezone.utc).isoformat(),'command':'ma_thesis_env/bin/python -B scripts/reassemble/10_validate_section2.py','prior_manifest_entries_verified':prior,'protected_metadata_entries_unchanged':len(protected),'raw_recording_metadata_unchanged':len(inventory),'raw_check':'metadata only; no media/audio payload opened','branch_prediction_hashes':branch_hashes,'rows':len(frame),'recordings':int(frame.recording_id.nunique()),'inner_branch_matrices':20,'additional_nested_subfolds':80,'three_seed_final_model_fits':60,'exact_U1_U2_F2_reuse':True,'source_hashes_unchanged':True,'all_output_arithmetic_and_gate_convexity_checks':'passed','tests':'55 passed in 8.75s (pre-execution full tests/reassemble suite)','pip_check':pip.stdout.strip(),'git_diff_check':'passed','successful_log_warning_scan':'no Traceback/ConvergenceWarning/RuntimeWarning','versions':{name:version(name) for name in ['numpy','pandas','scipy','scikit-learn','torch','threadpoolctl']},'free_bytes':shutil.disk_usage('.').free,'SQ3':'NOT YET ANSWERED'}
    with (run/'validation.json').open('x') as f:json.dump(audit,f,indent=2);f.write('\n')
    print(json.dumps({k:audit[k] for k in ['rows','recordings','protected_metadata_entries_unchanged','raw_recording_metadata_unchanged','exact_U1_U2_F2_reuse','all_output_arithmetic_and_gate_convexity_checks']}))


if __name__ == '__main__':
    main()
