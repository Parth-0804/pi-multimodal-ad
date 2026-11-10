"""Seal provenance for this audit without reading withdrawn-candidate payloads."""
import hashlib
import json
import platform
import shutil
import subprocess
import zipfile
from datetime import datetime,timezone
from pathlib import Path
import requests,h5py,pandas,numpy,PIL,cv2
from acquisition import ROOT


if __name__=='__main__':
    source=ROOT/'source_evidence';records=[];acquired=0
    for name in ['robofac','robofac_code','failure','failure_code','papers']:
        for receipt in sorted((source/name).rglob('*.receipt.json')):
            if receipt.name.startswith('MAIA_'):continue
            data=json.loads(receipt.read_text());records.append({'local_receipt':str(receipt.relative_to(ROOT)),**data})
            acquired+=data.get('bytes',0)
    members=[]
    with zipfile.ZipFile(source/'failure/annotation.zip') as z:
        for info in z.infolist():
            raw=z.read(info.filename);members.append({'filename':info.filename,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'archive':'source_evidence/failure/annotation.zip'})
    active=ROOT/'config';active.mkdir(exist_ok=True)
    config={'task':'Labels-first independent dataset feasibility audit','active_candidates':['RoboFAC','FAILURE'],
        'withdrawn_candidate':'CRIA; previously acquired evidence retained without further analysis',
        'no_training':True,'no_CNN_extraction':True,'no_GPU_experiments':True,'maximum_new_acquisition_bytes':500_000_000,
        'minimum_free_bytes':20*1024**3,
        'RoboFAC_dataset_revision':'d18353ab36db82ff888ebc9e8485c9fa77e1b25b',
        'RoboFAC_code_revision':'638eb5320d409e4072710a0db26f1c0d68cef3de',
        'FAILURE_code_annotation_revision':'8196217bf52d17fdb7193e57619bd855b1723d4e',
        'FAILURE_archive':'http://160.75.159.4/data/failure.zip','duplicate_policy':'Report, group related identities; never delete sources',
        'prediction_unit':'One original action, not a frame','split_screening':'Episode path and observed timestamp-derived date; sessions unverified'}
    (active/'audit_config.json').write_text(json.dumps(config,indent=2)+'\n')
    # Files acquired before the CRIA withdrawal stay preserved. Only filesystem
    # byte totals are included for the global budget; no excluded contents are read.
    source_disk_bytes=sum(p.stat().st_size for p in source.rglob('*') if p.is_file())
    root=ROOT.parents[1]
    provenance={'created_utc':datetime.now(timezone.utc).isoformat(),'project_relative_run':str(ROOT.relative_to(root)),
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'git_tracked_changes_at_start':['README.md','REPO_MAP.md','docs/thesis_research_direction/THESIS_EVIDENCE_GAPS.md'],
        'historical_outputs_modified':False,'staged_or_committed':False,'configuration':config,
        'software':{'python':platform.python_version(),'requests':requests.__version__,'h5py':h5py.__version__,'pandas':pandas.__version__,'numpy':numpy.__version__,'Pillow':PIL.__version__,'OpenCV':cv2.__version__},
        'active_source_acquisition_bytes_from_receipts':acquired,
        'all_preserved_source_directory_bytes_including_receipts_and_excluded_sources':source_disk_bytes,
        'storage_free_bytes_at_completion':shutil.disk_usage(ROOT).free,
        'annotation_archive_members':members,'sources':records,
        'failure_archive_identity':json.loads((ROOT/'checks/failure_archive_head.json').read_text()),
        'limitations':['Full FAILURE archive SHA-256 not available; only bounded ranges and sample/member hashes verified',
            'RoboFAC real numerical data not present in the complete listing',
            'Simulation outcome flags and intended-task QA answers are different native sources with unresolved disagreements',
            'FAILURE physical force/joint channels absent; audio architecture needs explicit scope acknowledgement',
            'FAILURE session/operator identities and exact WAV start times unavailable',
            'Raw FAILURE archive licensing not explicitly established',
            'CRIA explicitly withdrawn; earlier material retained, omitted from active evidence review'],
        'execution_commands':['ma_thesis_env/bin/python -B code/acquisition.py (initial discovery; GitHub API rate limit recorded)',
            'git ls-remote official RoboFAC and fino-net repositories HEAD refs/heads/main',
            'ma_thesis_env/bin/python -B code/acquire_annotations.py (initial scope; later restricted to RoboFAC)',
            'ma_thesis_env/bin/python -B code/inspect_failure_archive.py',
            'ma_thesis_env/bin/python -B code/audit_sources.py',
            'ma_thesis_env/bin/python -B code/inspect_numerical_samples.py (initial scope; later CRIA disabled)',
            'ma_thesis_env/bin/python -B code/screen_failure_groups.py',
            'ma_thesis_env/bin/python -B code/build_source_previews.py',
            'ma_thesis_env/bin/python -B code/plan_failure_pilot.py',
            'ma_thesis_env/bin/python -B code/write_reports.py',
            'ma_thesis_env/bin/python -B code/validate_delivery.py',
            'ma_thesis_env/bin/python -B -m pip check','git diff --check'],
        'network_method':'Anonymous public requests; trust_env=False; no credentials consulted; HTTP ranges require 206',
        'validation_summary':{k:v for k,v in json.loads((ROOT/'checks/validation.json').read_text()).items() if k!='results'}}
    command_prefix='ma_thesis_env/bin/python -B '+str(ROOT.relative_to(root))+'/'
    provenance['execution_commands']=[command.replace('ma_thesis_env/bin/python -B code/',command_prefix+'code/') for command in provenance['execution_commands']]
    provenance['execution_commands'].insert(6,command_prefix+'code/screen_robofac_identities.py')
    provenance['configuration']['source_acquisition_scope_change']='Initial three-candidate task; CRIA was explicitly withdrawn before visual review and subsequent work uses only RoboFAC/FAILURE'
    dest=ROOT/'SOURCE_PROVENANCE.json'
    if dest.exists():raise FileExistsError(dest)
    dest.write_text(json.dumps(provenance,indent=2,ensure_ascii=False)+'\n')
    manifest=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or p==ROOT/'OUTPUT_MANIFEST.json':continue
        rel=p.relative_to(ROOT)
        if rel.parts[0]=='source_evidence':continue
        # Historical withdrawn check artifacts are preserved but not re-read.
        if rel.parts[0]=='checks' and (p.name.startswith('cria_') or p.name.startswith('annotation_acquisition') or p.name=='native_label_audit.log'):continue
        raw=p.read_bytes();manifest.append({'path':str(rel),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    (ROOT/'OUTPUT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'sources':len(records),'active_acquisition_bytes':acquired,'all_source_directory_bytes':source_disk_bytes,'free_GiB':shutil.disk_usage(ROOT).free/1024**3,'output_files':len(manifest)}))
