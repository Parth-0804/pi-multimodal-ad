"""Bounded read-only AP reconciliation of FOUR preselected exposed banks.

No project imports, raw inputs, fits, threshold changes or uncertainty calculations.
Run from repository root with existing venv Python -I -B. Outputs refuse overwrite.
"""
from pathlib import Path
import csv
import hashlib
import json
import time
import zipfile
import numpy as np
import sklearn
from sklearn.metrics import average_precision_score

OUT = Path(__file__).resolve().parent
REPO = Path.cwd().resolve()
assert (REPO / 'AGENTS.md').is_file()
BASE = Path('runs/reassemble/20260927T204649Z-section3')
ANCHOR = Path('runs/reassemble/additional_improvements_executed/20260928T000346Z/03_static_anchored_adaptation')
FILES = [BASE/'predictions'/f'{x}.npz' for x in ['clean', 'V1_0.1', 'S1_1.0']] + [ANCHOR/'predictions.npz']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def headers(p):
    assert not p.is_symlink() and p.resolve().is_relative_to(REPO)
    with zipfile.ZipFile(p) as z:
        members = z.infolist()
        assert len({m.filename for m in members}) == len(members)
        assert sum(m.file_size for m in members) <= 128*1024**2
        for m in members:
            assert '/' not in m.filename and m.filename.endswith('.npy')
            with z.open(m) as f:
                version = np.lib.format.read_magic(f)
                assert version in [(1, 0), (2, 0)]
                read = np.lib.format.read_array_header_1_0 if version == (1, 0) else np.lib.format.read_array_header_2_0
                shape, order, dtype = read(f, max_header_size=10000)
                assert not dtype.hasobject and dtype.kind in 'biufUS'
                count = 1
                for dim in shape:
                    assert 0 <= dim <= 128*1024**2
                    count *= dim
                assert count * dtype.itemsize <= m.file_size <= 128*1024**2
        return [m.filename[:-4] for m in members]


def main():
    start = time.monotonic()
    pre = json.loads((OUT/'NPZ_HEADER_PREFLIGHT.json').read_text())
    expected = {x['path']: x['sha256'] for x in pre['files']}
    assert sum(p.stat().st_size for p in FILES) <= 512*1024**2
    sources = [BASE/'results.json', ANCHOR/'comparison/results.json', ANCHOR/'execution.json']
    report = json.loads(sources[0].read_text())
    anchored = json.loads(sources[1].read_text())
    execution = json.loads(sources[2].read_text())
    rows, checks = [], []
    clean_y, clean_fold = None, None
    for p in FILES:
        assert time.monotonic()-start < 1800
        before = sha(p)
        assert before == expected[str(p)]
        names = headers(p)
        is_anchor = p == FILES[-1]
        models = ['A0', 'A-CONSTANT', 'A-ADAPTIVE'] if is_anchor else ['U1', 'U2', 'F2', 'F6']
        info = {'path':str(p), 'sha256':before, 'members':names,
                'sample_keys_present':[k for k in ['recording_id','segment_id','rows','row_index'] if k in names],
                'evidence_status':'CONDITIONAL_ARRAY_ARITHMETIC',
                'identity_limit':'No recording/segment/row keys stored. Matching labels/folds cannot establish cohort identity or source execution.'}
        with np.load(p, allow_pickle=False) as bank:
            y, fold = bank['y'], bank['fold']
            assert y.ndim == fold.ndim == 1 and len(y) == len(fold)
            assert np.isin(y, [0, 1]).all() and len(np.unique(y)) == 2
            assert np.isin(fold, [0, 1, 2, 3, 4]).all()
            if clean_y is None:
                clean_y, clean_fold = y.copy(), fold.copy()
            assert np.array_equal(y, clean_y) and np.array_equal(fold, clean_fold)
            info.update(rows=len(y), positives=int(y.sum()), labels_equal_clean=True, folds_equal_clean=True,
                        fold_counts={str(k):int((fold==k).sum()) for k in np.unique(fold)})
            for model in models:
                prob = bank[model+'_p']
                assert prob.shape == y.shape and np.isfinite(prob).all()
                assert ((prob>=0)&(prob<=1)).all()
                value = float(average_precision_score(y, prob, pos_label=1))
                saved = float((anchored['models'][model]['metrics'] if is_anchor else report['conditions'][p.stem]['metrics'][model])['AUPRC']['estimate'])
                rows.append({'comparison_set':'anchored_clean' if is_anchor else 'section3_one_modality',
                             'bank':str(p),'condition':'clean' if is_anchor else p.stem,'model':model,
                             'metric':'sklearn average_precision_score; positive=1=failure; pooled saved rows',
                             'recomputed':value,'reported':saved,'difference':value-saved,
                             'arithmetic_agreement_1e-12':abs(value-saved)<=1e-12,
                             'evidence_status':'CONDITIONAL_ARRAY_ARITHMETIC'})
        if not is_anchor:
            side = p.with_suffix('.json');sources.append(side)
            info['bank_sidecar_sha_matches'] = json.loads(side.read_text())['sha256'] == before
            assert info['bank_sidecar_sha_matches']
        else:
            info['execution_prediction_binding'] = execution['predictions']
        assert before == sha(p)
        checks.append(info)
    for rel in ['src/reassemble/section1_report.py','src/reassemble/section3_report.py',
                'src/reassemble/section3_evaluate.py','src/reassemble/additional_improvements/reporting.py',
                'src/reassemble/additional_improvements/anchored.py','src/reassemble/inventory.py']:
        sources.append(Path(rel))
    with (OUT/'METRIC_RECONCILIATION.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    result={'scope':'Conditional saved-array AP arithmetic only; no reproduction of inference/training/targets/splits or confidence intervals.',
            'selected_comparison_sets':2,'banks':checks,'metric_rows':len(rows),'all_agree_1e-12':all(x['arithmetic_agreement_1e-12'] for x in rows),
            'numpy_version':np.__version__,'sklearn_version':sklearn.__version__,'seconds':time.monotonic()-start,
            'input_total_bytes':sum(p.stat().st_size for p in FILES),
            'supporting_identities':{str(p):sha(p) for p in sources},'unchecked':'All other models/conditions/banks; thresholds/calibration/CI; raw target/split membership; complete fit/source producing chain; Task4 untouched.'}
    with (OUT/'NUMERICAL_RESULT.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ['metric_rows','all_agree_1e-12','seconds','input_total_bytes']}))


if __name__ == '__main__':
    main()
