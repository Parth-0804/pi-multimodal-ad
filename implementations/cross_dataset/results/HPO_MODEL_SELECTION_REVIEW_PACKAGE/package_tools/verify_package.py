"""Standalone export verifier. Standard library only; never imports research code."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import re
import sys
import urllib.parse

csv.field_size_limit(256*1024**2)
FORBIDDEN={'.pt','.pth','.ckpt','.safetensors','.pkl','.pickle','.joblib','.npz','.npy','.h5','.hdf5','.parquet','.mp4','.avi','.mkv','.mov','.7z','.tar','.rar'}


def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024**2),b''):h.update(chunk)
    return h.hexdigest()


def verify_manifest(root):
    root=Path(root).resolve();seen=set();total=0
    with (root/'PACKAGE_MANIFEST.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            p=root/row['package_path'];assert p.resolve().is_relative_to(root)
            assert row['package_path'] not in seen;seen.add(row['package_path'])
            assert p.is_file(),row['package_path'];assert p.stat().st_size==int(row['bytes'])
            assert digest(p)==row['sha256'],row['package_path'];total+=p.stat().st_size
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='PACKAGE_MANIFEST.csv'}
    assert seen==actual,{'unmanifested':sorted(actual-seen),'missing':sorted(seen-actual)}
    return {'hashed_files':len(seen),'hashed_bytes':total,'all_hashes_match':True}


def verify_content(root):
    root=Path(root).resolve();links=0;csv_files=0;json_files=0;csvrows={};files=0
    for p in sorted(root.rglob('*')):
        if not p.is_file():continue
        if p.name in {'PACKAGE_MANIFEST.csv','EXPORT_VALIDATION.json'}:continue
        files+=1
        assert p.suffix.lower() not in FORBIDDEN,('FORBIDDEN_BINARY',str(p))
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)\n]+)\)',p.read_text()):
                if link.startswith(('https:','http:','mailto:','data:','#')):continue
                target=urllib.parse.unquote(link.strip('<>').split('#',1)[0])
                if not target:continue
                dest=(p.parent/target).resolve()
                assert dest.is_relative_to(root) and dest.exists(),('BROKEN_INTERNAL_REFERENCE',str(p.relative_to(root)),target)
                links+=1
        if p.suffix=='.csv':
            csv_files+=1;n=0
            with p.open(newline='') as f:
                for row in csv.DictReader(f):assert None not in row,('CSV_PARSE',str(p));n+=1
            csvrows[str(p.relative_to(root))]=n
        if p.suffix=='.json':json.loads(p.read_text());json_files+=1
        if p.suffix=='.jsonl':
            with p.open() as f:
                for line in f:
                    if line.strip():json.loads(line)
    audit=root/'repository/CROSS_DATASET_COMPARISON/MODEL_CONFIGURATION_AUDIT_20261103'
    assert len(list((audit/'06_dataset_specific').rglob('*.png')))==11
    # Counts come from the completed audit,not recomputed model experiments.
    expected=json.loads((audit/'provenance/EXTRACTION_SUMMARY.json').read_text())
    pref=str(audit.relative_to(root))+'/'
    assert csvrows[pref+'05_results/ALL_RECORDED_METRICS_LONG.csv']==expected['numeric_metric_records']
    assert csvrows[pref+'03_hyperparameter_configuration/ALL_RUN_HYPERPARAMETERS.csv']==expected['run_records']
    assert csvrows[pref+'04_training_and_checkpoints/ALL_DATASET_EPOCH_HISTORIES.csv']==expected['epoch_history_rows']
    configurations=json.loads((audit/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json').read_text())
    assert len(configurations)==expected['run_records']
    c20=[r for r in configurations if r['experiment_id']=='REASSEMBLE_PHASE1_C20'];assert len(c20)==25
    assert all(r['effective_configuration']['executed_epochs']==20 for r in c20)
    return {'content_files_checked':files,'internal_markdown_references':links,'CSV_files':csv_files,'JSON_files':json_files,
        'all_internal_file_references_resolve':True,'all_CSV_rows_preserved':True,
        'numeric_metric_records':expected['numeric_metric_records'],'effective_configuration_records':len(configurations),
        'epoch_history_rows':expected['epoch_history_rows'],'C20_complete_configurations':len(c20),
        'large_checkpoint_or_raw_dataset_binaries_present':False}


if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    print(json.dumps({'manifest':verify_manifest(root),'content':verify_content(root)},indent=2))
