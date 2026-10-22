"""Small existing-table consistency check; does NOT identify anonymous bank rows.
No project imports, new labels, thresholds, inference or fitting. Refuses overwrite.
"""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import pyarrow.parquet as pq

OUT = Path(__file__).resolve().parent
COHORT = Path('runs/reassemble/20260927T141645Z-inventory/tables_v2/cohort.parquet')
SPLITS = Path('artifacts/reassemble/audits/nested_splits.json')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    start=time.monotonic()
    files=[COHORT,SPLITS]
    assert all(p.is_file() and not p.is_symlink() for p in files)
    ids={str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files}
    assert sum(p.stat().st_size for p in files) + 2720232 <= 512*1024**2
    pf=pq.ParquetFile(COHORT)
    decoded=sum(pf.metadata.row_group(i).total_byte_size for i in range(pf.metadata.num_row_groups))
    assert decoded <= 128*1024**2
    columns=['recording_id','segment_id','primary_task','dual_complete','failure']
    table=pf.read(columns=columns,use_threads=False).to_pydict()
    rows=[i for i,(a,b) in enumerate(zip(table['primary_task'],table['dual_complete'])) if a and b]
    recordings=[table['recording_id'][i] for i in rows]
    keys=[(table['recording_id'][i],str(table['segment_id'][i])) for i in rows]
    labels=np.array([table['failure'][i] for i in rows],dtype=int)
    assert len(set(keys)) == len(keys)
    saved=json.loads(SPLITS.read_text());expected=np.full(len(rows),-1);coverage=set()
    for fold in saved['folds']:
        train,test=set(fold['train_recordings']),set(fold['test_recordings'])
        assert not train & test and train | test == set(recordings)
        assert not coverage & test;coverage |= test
        for part in fold['inner']:
            it,iv=set(part['train_recordings']),set(part['validation_recordings'])
            assert not it & iv and it | iv == train and not (it | iv) & test
        for i,rec in enumerate(recordings):
            if rec in test:expected[i]=fold['fold']
    assert coverage == set(recordings) and (expected>=0).all()
    banks=json.loads((OUT/'NPZ_HEADER_PREFLIGHT.json').read_text())['files']
    checks=[]
    for b in banks:
        p=Path(b['path']);assert sha(p)==b['sha256']
        with np.load(p,allow_pickle=False) as z:
            checks.append({'path':str(p),'saved_label_vector_equal_current_cohort_order':bool(np.array_equal(z['y'],labels)),
                           'saved_fold_vector_equal_split_in_current_cohort_order':bool(np.array_equal(z['fold'],expected)),
                           'direct_row_key_binding':False})
    assert all(x['saved_label_vector_equal_current_cohort_order'] and x['saved_fold_vector_equal_split_in_current_cohort_order'] for x in checks)
    assert all(sha(Path(p))==v['sha256'] for p,v in ids.items())
    result={'scope':'Current saved cohort and split consistency only. Labels/folds agree in source-defined order; anonymous prediction files still lack direct row keys. No raw annotation validation or producing-run identity proof.',
            'inputs':ids,'parquet_total_uncompressed_bytes':decoded,'cohort_rows':len(rows),'failures':int(labels.sum()),'recordings':len(set(recordings)),
            'cohort_key_order_sha256':hashlib.sha256(json.dumps(keys,separators=(',',':')).encode()).hexdigest(),
            'unique_keys':True,'outer_recording_sets_disjoint':True,'inner_partitions_inside_outer_train':True,'banks':checks,
            'seconds':time.monotonic()-start,'pyarrow_version':__import__('pyarrow').__version__,
            'evidence_status':'VERIFIED_WITHIN_SCOPE_CURRENT_TABLE_CONSISTENCY; historical row identity remains INFERRED/UNKNOWN'}
    with (OUT/'MEMBERSHIP_CONSISTENCY.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ['cohort_rows','failures','recordings','seconds','parquet_total_uncompressed_bytes']}))


if __name__ == '__main__':
    main()
