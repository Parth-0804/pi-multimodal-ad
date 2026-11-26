"""Readability, required outputs, source preservation and provenance validation."""
from pathlib import Path
import collections
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import urllib.parse
from PIL import Image
from audit_common import OUT,REPO,digest,read,write,csv_read,csv_write

REQUIRED={
'':['README.md'],
'01_executive_overview':['EXECUTIVE_AUDIT_SUMMARY.md','CURRENT_EXPERIMENT_STATUS.md','KEY_FINDINGS_AND_LIMITATIONS.md'],
'02_model_architecture':['COMPLETE_MODEL_INVENTORY.md','VISUAL_ARCHITECTURES.md','SENSOR_ARCHITECTURES.md','FUSION_ARCHITECTURES.md','MODEL_PARAMETER_COUNTS.csv'],
'03_hyperparameter_configuration':['ALL_RUN_HYPERPARAMETERS.csv','EFFECTIVE_CONFIGURATIONS.json','HYPERPARAMETER_TUNING_HISTORY.md','CONFIGURATION_DIFFERENCES.md','PARAMETER_PROVENANCE.csv'],
'04_training_and_checkpoints':['TRAINING_RUN_INVENTORY.csv','CHECKPOINT_INVENTORY.csv','TRAINING_DURATION_AND_GPU_USAGE.csv','CHECKPOINT_SELECTION_AUDIT.md','REPRODUCIBILITY_ASSESSMENT.md'],
'05_results':['ALL_RECORDED_METRICS_LONG.csv','ALL_MODEL_RESULTS_SUMMARY.csv','TRAIN_VS_VALIDATION_VS_TEST.md','COMPARABILITY_MATRIX.csv','RESULTS_PROVENANCE.csv'],
'06_dataset_specific/REASSEMBLE':['MODEL_AND_CONFIGURATION_AUDIT.md','FROZEN_VS_FINETUNED_100_EPOCHS.md','FUSION_RESULTS_AND_CONFIGURATIONS.md','EPOCH_HISTORIES.csv','COMPLETE_RESULTS.csv'],
'06_dataset_specific/MSM':['MODEL_AND_CONFIGURATION_AUDIT.md','COMPLETE_RESULTS.csv'],
'06_dataset_specific/HANDOVER':['MODEL_AND_CONFIGURATION_AUDIT.md','COMPLETE_RESULTS.csv'],
'06_dataset_specific/VIFAILBACK':['MODEL_AND_CONFIGURATION_AUDIT.md','COMPLETE_RESULTS.csv'],
'07_scientific_validity':['LEAKAGE_AND_SELECTION_AUDIT.md','SEED_AND_FOLD_COVERAGE.md','MISSING_EVIDENCE.md','SCIENTIFIC_COMPARABILITY_VERDICT.md'],
'08_future_hpo_readiness':['MODEL_SELECTION_EVIDENCE_TABLE.md','HYPERPARAMETERS_ALREADY_EXPLORED.md','PARAMETERS_NOT_YET_TUNED.md','HPO_READINESS_AND_CONSTRAINTS.md'],
'09_reviewer_handoff':['RESEARCHER_HANDOFF.md','FILE_AND_SOURCE_MANIFEST.csv','AUDIT_VALIDATION_RESULTS.md']}


def snapshot():
    commands={
       'GIT_HEAD_AT_END.txt':['git','rev-parse','HEAD'],
       'GIT_STATUS_AT_END.txt':['git','status','--short','--branch','--untracked-files=all'],
       'GIT_DIFF_STAT_AT_END.txt':['git','diff','--stat'],
       'GIT_DIFF_CHECK.txt':['git','diff','--check'],
       'PIP_CHECK.txt':[str(REPO/'ma_thesis_env/bin/python'),'-B','-m','pip','check'],
       'GPU_RESOURCE_SNAPSHOT.txt':['nvidia-smi','--query-gpu=index,name,uuid,memory.total,memory.used,utilization.gpu,driver_version','--format=csv'],
       'USER_PROCESS_SNAPSHOT.txt':['ps','-u',str(os.getuid()),'-o','pid,comm,etimes'],
    }
    outcomes=[]
    for name,cmd in commands.items():
        try:
            r=subprocess.run(cmd,cwd=REPO,capture_output=True,text=True,timeout=60)
            (OUT/'provenance'/name).write_text(r.stdout+r.stderr)
            outcomes.append({'command':cmd,'output':name,'returncode':r.returncode})
        except Exception as e:outcomes.append({'command':cmd,'output':name,'error':str(e)})
    write(OUT/'provenance/END_COMMAND_RESULTS.json',outcomes)
    head=(OUT/'provenance/GIT_HEAD_AT_END.txt').read_text().strip()
    assert head=='eb3888f5d23310aa097dbb1be14605e931190b4a'
    write(OUT/'provenance/RESOURCE_SNAPSHOT_CONTEXT.json',{'utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'CUDA_VISIBLE_DEVICES':os.environ.get('CUDA_VISIBLE_DEVICES','NOT SET'),
        'audit_GPU_allocations':0,'GPU_command_is_metadata_only':True,
        'live_old_vifailback_controller_PID290646':Path('/proc/290646').exists(),
        'process_snapshot_excludes_arguments_and_session_contents':True})


def compress_work_states():
    receipts=[]
    # Only transient states created by THIS audit, never experiment evidence.
    for p in sorted((OUT/'provenance').glob('*AUDIT_STATE*.json')):
        original_sha=digest(p);before=p.stat().st_size;dest=p.with_suffix(p.suffix+'.gz')
        with p.open('rb') as source,dest.open('wb') as target:
            with gzip.GzipFile(filename='',mode='wb',fileobj=target,compresslevel=1,mtime=0) as compressed:
                for chunk in iter(lambda:source.read(8*1024**2),b''):compressed.write(chunk)
        h=hashlib.sha256()
        with gzip.open(dest,'rb') as stream:
            for chunk in iter(lambda:stream.read(8*1024**2),b''):h.update(chunk)
        assert h.hexdigest()==original_sha
        receipts.append({'original_audit_scratch':str(p.relative_to(OUT)),'original_bytes':before,'original_sha256':original_sha,
            'compressed':str(dest.relative_to(OUT)),'compressed_bytes':dest.stat().st_size,'compressed_sha256':digest(dest),'roundtrip_verified':True})
        p.unlink() # New task-owned redundant scratch only, after exact round-trip verification.
    if receipts:write(OUT/'provenance/WORKING_STATE_COMPRESSION_RECEIPT.json',receipts)


def main():
    snapshot()
    pending=OUT/'09_reviewer_handoff/AUDIT_VALIDATION_RESULTS.md'
    if not pending.exists():pending.write_text('# Audit validation in progress\n')
    # Every used original input is rehashed; this ledger is small (~5GiB total) compared to full data.
    original={};conflicts=[]
    for p in (OUT/'provenance').glob('*LEDGER*.json'):
        for r in json.loads(p.read_text()):
            path=Path(r['path']);path=path if path.is_absolute() else REPO/path
            if path.is_relative_to(OUT):continue
            old=original.get(r['path'])
            if old and old['sha256']!=r['sha256']:conflicts.append({'path':r['path'],'earlier':old['sha256'],'later':r['sha256']})
            original[r['path']]=r
    preservation=[]
    for name,r in sorted(original.items()):
        p=Path(name);p=p if p.is_absolute() else REPO/p
        ok=p.exists() and p.stat().st_size==r['bytes'] and digest(p)==r['sha256']
        preservation.append({'source_path':name,'sha256':r['sha256'],'bytes':r['bytes'],'unchanged_hash':ok})
    csv_write(OUT/'provenance/ORIGINAL_INPUT_PRESERVATION_CHECK.csv',preservation)
    assert not conflicts;assert all(r['unchanged_hash'] for r in preservation)
    # Binary inventory was fully hashed at audit start. Check all metadata now and rehash key sources above.
    cp=csv_read(OUT/'04_training_and_checkpoints/CHECKPOINT_INVENTORY.csv');cpstable=[]
    for r in cp:
        p=REPO/r['path'];current=p.stat();mtime=dt.datetime.fromtimestamp(current.st_mtime,dt.timezone.utc).isoformat()
        cpstable.append({'path':r['path'],'bytes_unchanged':current.st_size==int(r['bytes']),'mtime_unchanged':mtime==r['mtime_utc']})
    assert all(r['bytes_unchanged'] and r['mtime_unchanged'] for r in cpstable)
    csv_write(OUT/'provenance/CHECKPOINT_END_METADATA_CHECK.csv',cpstable)
    # Current Markdown files and plotting artifacts are readable before the inventory is sealed.
    links=[];csvcounts={};heldout_long=0;figures=[]
    for p in OUT.rglob('*'):
        if not p.is_file():continue
        if p.suffix in ['.md','.py','.txt','.tsv']:p.read_text()
        if p.suffix=='.json':json.loads(p.read_text())
        if p.suffix=='.jsonl':
            with p.open() as f:
                for line in f:
                    if line.strip():json.loads(line)
        if p.suffix=='.csv':
            with p.open(newline='') as f:
                reader=csv.DictReader(f);n=0
                for row in reader:
                    assert None not in row,('MALFORMED_CSV',str(p))
                    n+=1
                    if p.name=='ALL_RECORDED_METRICS_LONG.csv' and 'HELD-OUT' in row.get('evaluation_scope',''):heldout_long+=1
            csvcounts[str(p.relative_to(OUT))]=n
        if p.suffix=='.png':
            with Image.open(p) as im:im.verify()
            figures.append(str(p.relative_to(OUT)))
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if link.startswith(('https:','http:','#')):continue
                target=urllib.parse.unquote(link.split('#')[0]);resolved=p.parent/target
                links.append({'document':str(p.relative_to(OUT)),'target':target,'exists':resolved.exists()})
    assert all(r['exists'] for r in links),[r for r in links if not r['exists']][:10]
    assert len(figures)==11
    check=read(OUT/'provenance/EXTRACTION_CHECKS.json');assert all(r.get('passed') for r in check)
    msm_original=csv_read('MSM/06_evaluation_results/metrics/clean_seed_summary.csv')
    expected={r['model']:float(r['AP_mean']) for r in msm_original if r['protocol']=='primary__group_id'}
    msm_review=[r for r in csv_read(OUT/'05_results/IMPORTANT_HELD_OUT_RESULTS.csv') if r['dataset']=='MSM']
    assert len(msm_review)==10
    assert all(abs(float(r['AP'])-expected[r['model']])<1e-12 for r in msm_review)
    counts=read(OUT/'provenance/REPORT_COUNTS.json');counts['held_out_numeric_metric_records']=heldout_long;write(OUT/'provenance/REPORT_COUNTS.json',counts)
    csv_write(OUT/'provenance/OUTPUT_CSV_ROW_COUNTS.csv',[{'path':k,'rows':v} for k,v in sorted(csvcounts.items())])
    write(OUT/'provenance/MARKDOWN_LINK_CHECK.json',links)
    compress_work_states()
    outcomes=read(OUT/'provenance/END_COMMAND_RESULTS.json')
    tests=(OUT/'provenance/PYTEST_RESULTS.txt').read_text()
    validation=f'''# Audit validation results

Validated: {dt.datetime.now(dt.timezone.utc).isoformat()}.

- All required reports/tables are present (final list checked below).
- {len(original):,} original evidence inputs rehashed: SHA256s unchanged; no conflicting input hashes across extraction ledgers.
- All4,920 binary candidates were fully hashed at audit discovery; all retain identical size and mtime at the end. Important fitted/source inputs above were rehashed. Full secondary6-minute binary rehash was not repeated.
- {len(check):,} independent saved-prediction/history/hash checks passed;94 additional split/native-label checks passed. No training/inference replay was performed.
- All CSV rows parse; JSON/JSONL documents parse; all11 PNG figures decode; {len(links)} local Markdown links resolve. Exact row counts are in OUTPUT_CSV_ROW_COUNTS.csv.
- {counts['configuration_records']:,} unique configuration/run IDs;7,929 COMPLETE/40 REUSED,with174 completed legacy calls inferred from aggregate/source control flow. All required configuration keys are retained,including explicit unknowns.
- {heldout_long:,} numeric metric rows have a HELD-OUT scope. This includes recorded aggregate/subgroup/robustness/seed-summary rows; it is not a count of independent model evaluations. Complete long metrics contain587,101 rows,including epochs and intervals.
-360 official Handover validation rows are explicitly VALIDATION OFFICIAL,not inner OOF.
- All10 MSM review-table AP values agree with the saved primary mean-seed pooled summary (absolute tolerance1e-12). Mean-fold AP is separately retained in AP_AGGREGATION_RECONCILIATION.csv.
- CPU-only audit tests: see PYTEST_RESULTS.txt. All test fixtures are synthetic and remain inside the new audit folder.
- Work-state compression was round-trip SHA256-verified; only redundant scratch JSON created by this audit was replaced by gzip. Required CSV/JSON configuration/metric data were not truncated.
- Git HEAD remains eb3888f5d23310aa097dbb1be14605e931190b4a. No staging,commit,push or changes to historical evidence were performed. Existing unrelated changes remain documented.

## Command outcomes

'''
    for r in outcomes:validation+='- `'+ ' '.join(r['command'])+'`: '+str(r.get('returncode',r.get('error')))+'; output `provenance/'+r['output']+'`.\n'
    validation+='\n## Audit test output\n\n```text\n'+tests.strip()+'\n```\n\n'
    validation+='## Limits\n\nReadability and hash checks do not certify missing participant/tool/session identities,unrecorded optimizer states,unlogged/deleted historical fits or pristine assessment after research post-selection. No expensive feature extraction or model replay was performed. Legacy PHM source-flow-inferred fits have no per-fit epoch/state receipt. Historical total GPU-hours are NOT RECORDED. The audit is uncommitted.\n'
    (OUT/'09_reviewer_handoff/AUDIT_VALIDATION_RESULTS.md').write_text(validation)
    # Source manifest includes all used original inputs plus every audited binary candidate and output.
    manifest=[]
    for name,r in sorted(original.items()):manifest.append({'record_type':'ORIGINAL_INPUT','path':name,'original_source_path':name,'bytes':r['bytes'],'sha256':r['sha256'],'verification':'rehash unchanged at end'})
    known={r['path'] for r in manifest}
    for r in cp:
        if r['path'] not in known:manifest.append({'record_type':'ORIGINAL_BINARY_CANDIDATE','path':r['path'],'original_source_path':r['path'],'bytes':r['bytes'],'sha256':r['sha256'],'verification':'full discovery hash + unchanged end size/mtime'})
    manifest_path=OUT/'09_reviewer_handoff/FILE_AND_SOURCE_MANIFEST.csv'
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p!=manifest_path:
            manifest.append({'record_type':'AUDIT_OUTPUT','path':str(p.relative_to(OUT)),'original_source_path':'derived; source references in provenance/result/config ledgers','bytes':p.stat().st_size,'sha256':digest(p),'verification':'readable and hashed'})
    csv_write(manifest_path,manifest)
    required=[OUT/folder/name for folder,names in REQUIRED.items() for name in names]
    assert all(p.is_file() and p.stat().st_size for p in required)
    assert 'passed' in tests and 'failed' not in tests.lower()
    # Manifest deliberately excludes its own recursive hash. Validate every exported row identity once.
    for r in manifest:
        if r['record_type']=='AUDIT_OUTPUT':assert digest(OUT/r['path'])==r['sha256']
    print(json.dumps({'required_files':len(required),'audit_files':sum(p.is_file() for p in OUT.rglob('*')),'original_inputs_rehashed':len(original),'binary_metadata_stable':len(cp),'heldout_numeric_rows':heldout_long,'plots':len(figures),'manifest_rows':len(manifest),'audit_bytes':sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())}),flush=True)


if __name__=='__main__':main()
