"""Record final audit provenance and checksums without changing prior artifacts."""
import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

from prepare_full_lab import write,sha256


def command(args):
    r=subprocess.run(args,capture_output=True,text=True)
    return {'command':args,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}


def main(final):
    cfg=json.loads((final/'config/resolved_config.json').read_text());parent=Path(cfg['acquisition_and_audit_run'])
    data_checks=json.loads((final/'validation_data.json').read_text())
    tests=(final/'logs/data_tests.txt').read_text()
    assert '39 passed' in tests
    pip=command([sys.executable,'-B','-m','pip','check'])
    diff=command(['git','diff','--check'])
    status=command(['git','status','--short','--branch','--untracked-files=no'])
    assert pip['returncode']==diff['returncode']==status['returncode']==0
    raw=Path(cfg['data_root']);raw_files=[str(p) for p in raw.rglob('*') if p.is_file()]
    ignored=subprocess.run(['git','check-ignore','--stdin'],input='\n'.join(raw_files)+'\n',capture_output=True,text=True)
    assert set(ignored.stdout.splitlines())==set(raw_files)
    tracked=command(['git','ls-files','--',str(raw)])
    assert not tracked['stdout']
    stage2=Path(cfg['stage2'])
    source=Path('MILLING DATASET/source')
    sources=[source/n for n in ['prepare_full_lab.py','acquire_full_lab.py','full_lab_audit.py',
                  'finish_full_lab.py','consolidate_pilot_findings.py','seal_full_lab.py']]
    sources.extend([source/'msm/data.py',source/'msm/splits.py',*sorted((source/'stage2').glob('*.py'))])
    sources.extend(sorted(Path('MILLING DATASET/tests').glob('test_*audit*.py')))
    sources.extend([Path('MILLING DATASET/tests/test_stage2_contract.py'),Path('MILLING DATASET/tests/test_stage2_acquisition.py'),
                    Path('MILLING DATASET/tests/test_download_msm.py'),Path('MILLING DATASET/configs/stage3_protocol.json')])
    identity=[]
    snapshot=final/'evidence/source_snapshot';snapshot.mkdir()
    for p in sorted(set(sources)):
        target=snapshot/p.relative_to('MILLING DATASET');target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(p.read_bytes())
        identity.append({'path':str(p),'sha256':sha256(p),'snapshot':str(target),'bytes':p.stat().st_size})
    write(final/'manifests/source_identity.json',identity)
    # Preserve the exact two executed source revisions as well as the final serialization repair.
    executed=[]
    for p in parent.glob('evidence/full_lab_audit_before*.py'):
        executed.append({'path':str(p),'sha256':sha256(p)})
    command_records=[
      "ma_thesis_env/bin/python -B 'MILLING DATASET/source/prepare_full_lab.py'",
      "ma_thesis_env/bin/python -B 'MILLING DATASET/source/stage2/download_msm.py' --handle manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2 --dest 'MILLING DATASET/data/raw/msm/versions/2' --mode pilot --config '"+str(parent)+"/config/download_config.json'",
      "ma_thesis_env/bin/python -B 'MILLING DATASET/source/acquire_full_lab.py' --run '"+str(parent)+"' --execute (initial attempt and one timeout retry)",
      "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH='MILLING DATASET/source' ma_thesis_env/bin/python -B 'MILLING DATASET/source/full_lab_audit.py' --run '"+str(parent)+"' (initial attempt and checkpoint resume)",
      "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH='MILLING DATASET/source' ma_thesis_env/bin/python -B 'MILLING DATASET/source/finish_full_lab.py' --parent '"+str(parent)+"'",
      "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH='MILLING DATASET/source' ma_thesis_env/bin/python -B -m pytest -q 'MILLING DATASET/tests/test_download_msm.py' 'MILLING DATASET/tests/test_audit_annotations.py' 'MILLING DATASET/tests/test_stage2_acquisition.py' 'MILLING DATASET/tests/test_stage2_contract.py' 'MILLING DATASET/tests/test_full_lab_audit.py'",
      "ma_thesis_env/bin/python -B 'MILLING DATASET/source/seal_full_lab.py' --final '"+str(final)+"'"
    ]
    write(final/'manifests/commands.json',command_records)
    failures=[{'path':str(p),'sha256':sha256(p)} for pattern in ['evidence/*failure*.json','logs/full_lab_audit*.txt','logs/acquisition*.txt'] for p in parent.glob(pattern)]
    write(final/'manifests/execution_failures.json',{'preserved_attempt_evidence':failures,'executed_source_revisions':executed,
         'network_failure':'One timeout before response, resumed using per-file receipts; zero final missing files.',
         'serialization_failures':'Rejected mapping residual infinity caused two strict-JSON roll-up failures. No acceptance, label, timing, feature or split calculation changed. Completed checkpoints were reused and normalized through the existing Stage 2 null policy.',
         'partial_checkpoint':'Preserved incomplete original completed.json for VM20i/dataset2; complete marker v2 is atomic.',
         'final_delivery':'Fresh run built entirely from all 56 completed checkpoints; no repeated successful video decodes or model work.'})
    software={name:importlib.metadata.version(name) for name in ['numpy','pandas','scipy','matplotlib','Pillow','opencv-python','soundfile','scikit-learn','pytest','psutil']}
    provenance={'completed_utc':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'git_status':status,'preexisting_tracked_diff_unchanged':True,'git_diff_stat':command(['git','diff','--stat']),
        'dataset_handle':cfg['handle'],'dataset_id':8392825,'version':2,
        'official_inventory':{'path':str(parent/'manifests/official_file_inventory.json'),'sha256':sha256(parent/'manifests/official_file_inventory.json')},
        'official_metadata':{'path':str(parent/'evidence/kaggle_metadata.json'),'sha256':sha256(parent/'evidence/kaggle_metadata.json')},
        'resolved_config_sha256':sha256(final/'config/resolved_config.json'),'python':platform.python_version(),'software':software,
        'cpu_audit_resource_snapshot':json.loads((parent/'evidence/resource_snapshot_cpu_only.json').read_text()),
        'cpu_workers':2,'threads_per_decoder':1,'blas_threads':1,
        'run_start_utc':json.loads((parent/'provenance_initial.json').read_text())['started_utc'],
        'run_start_note':'Timestamp was recorded after official inventory/plan preparation; directory ID predates it.',
        'models_trained':0,'gpu_work':False,'phase1_checkpoint_or_execution_tools_used':False,
        'prediction_metrics_reported':False,'final_split_frozen':False,'files_staged_or_committed':False,
        'shared_source_protocol_sha256':sha256(Path('MILLING DATASET/configs/stage3_protocol.json'))}
    write(final/'provenance.json',provenance)
    write(final/'validation.json',{'data_checks':data_checks,'tests':tests,'tests_passed':39,
        'excluded_test_suites':'Stage 3 model-fitting tests and Stage 4 model-state tests intentionally not executed.',
        'pip_check':pip,'git_diff_check':diff,'raw_files_and_receipts_git_ignored':len(raw_files),
        'raw_files_tracked':0,'source_snapshot_hashes_match':True,'passed':True})
    # Human-readable execution/methodology notes are supplemental, not edits to copied reports.
    notes='''# Execution and methodology notes

The full laboratory audit uses the final corrected Stage 2 estimator and fixed Stage 3 data/split contracts. The only additional synchronization acceptance gate rejects equally voted distant calibration aliases with independent validation support. This conservative gate rejects VM20i/dataset12; it does not optimize timing or select a model result. Existing pilot mappings are reused unchanged. All new AAC time origins were explicitly checked. No target label or cutting boundary participates in calibration.

One public acquisition request timed out. Per-file hashes/receipts allowed a safe retry, with no overwrite and no final missing file. Interrupted attempts remain preserved.

Rejected recordings can have an infinite residual when no validation anchor survives. Strict JSON initially refused this diagnostic. The failure exposed a report-serialization defect, not a scientific result change. Existing Stage 2 finite-value serialization now maps undefined residuals to null. A synthetic regression covers this case. Complete markers are published atomically; the incomplete earlier marker remains preserved. All 56 complete checkpoints were consolidated into this fresh validated run without repeating valid video decodes. Exact executed source preimages, logs and hashes are indexed in manifests/execution_failures.json.

The extra data support seven machine/reference-date groups and five calendar-date groups. Both label definitions pass the existing fixed three-outer/two-inner construction under both proxies and nominal folders. Five dates remain a small basis for uncertainty estimation; date proxies do not resolve physical tool/workpiece reuse across dates. No final split is frozen. The researcher must approve the target and grouping before future evaluation.

The 1,895 technically paired intervals are not independently certified visually informative. Contact sheets for every experiment are available, but only representative new sequences were generated. A representative view cannot certify all intervals; independent review remains pending. The original pilot's Codex context assessment is retained as historical evidence, not expert anomaly-observability validation.

All 280 experiment input hashes and 56 original label identities were rechecked. Two XML files are also hash-verified against their acquisition receipts in the download manifest. The actual MTC vectors were independently recomputed with the existing fixed implementation: maximum difference 0.0 in the float32 contract. These checks reproduce data eligibility and saved-statistic consistency, not model efficacy.

No CNN features, model fits, F2 evaluation, new source checkpoint audit, Phase 1 execution command, GPU benchmark or model-performance claim was produced. All changes remain under MILLING DATASET/. Three pre-existing tracked edits (22 insertions) are unchanged; nothing is staged or committed. Raw data, decoded caches and bulky per-experiment checkpoints remain local generated evidence.
'''
    with (final/'METHODOLOGY_AND_EXECUTION_NOTES.md').open('x') as f:f.write(notes)
    findings=Path('MILLING DATASET/PILOT_FINDINGS')
    index='# Full laboratory tables and execution evidence\n\n'
    for name in ['MSM_FULL_LAB_ELIGIBILITY_MANIFEST.csv','MSM_DOWNLOAD_MANIFEST.csv','manifests/selected_frame_manifest.csv',
                 'manifests/common_mtc_statistics.csv','validation.json','provenance.json','METHODOLOGY_AND_EXECUTION_NOTES.md']:
        p=final/name;index+=f'- [{name}]({os.path.relpath(p,findings)}) — {p.stat().st_size:,} bytes; SHA-256 `{sha256(p)}`.\n'
    index+='\n[Per-experiment contact sheets](05_FULL_LABORATORY_FEASIBILITY/diagnostics/README.md) are representative diagnostics; independent interval visibility review remains pending.\n'
    with (findings/'TABLE_AND_DIAGNOSTIC_INDEX.md').open('x') as f:f.write(index)
    with (findings/'.gitignore').open('x') as f:f.write('# Generated visual diagnostics remain local until researcher review.\n/05_FULL_LABORATORY_FEASIBILITY/diagnostics/*.jpg\n')
    files=[]
    for base in [final,findings]:
        for p in sorted(base.rglob('*')):
            if p.is_file():files.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha256(p)})
    write(final/'manifests/output_manifest.json',{'self_excluded':True,'files':files,
          'acquisition_and_raw_receipts':str(parent),'raw_inputs_not_duplicated':True})
    print(json.dumps({'final':str(final),'files_sealed':len(files),'tests':39,'historical_artifacts_unchanged':175,'raw_files_git_ignored':len(raw_files)},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--final',type=Path,required=True);main(p.parse_args().final)
