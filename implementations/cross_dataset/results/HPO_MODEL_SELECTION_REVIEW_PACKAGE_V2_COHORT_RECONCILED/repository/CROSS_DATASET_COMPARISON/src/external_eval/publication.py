"""Human source indexes and sealed, allowlisted software/output provenance."""
import csv
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

from external_eval.io import sha,utc,write_json


def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_text()!=value:raise ValueError('Publication index differs; use a new version: '+str(path))
    else:path.write_text(value)


def prepare(root):
    root=Path(root);config=json.loads((root/'04_experiment_protocol/experiment_config.json').read_text());canonical=Path(config['dataset'])
    if config['dataset']=='MSM':
        preserved=Path('MSM/99_preserved_previous_work/MILLING_DATASET/runs/20261027T015205931708Z-stage5-full-lab-validated')
        import pandas as pd
        known={r['relative_source_path']:{'path':str(canonical/'01_raw_dataset/official_dataset'/r['relative_source_path']),
            'bytes':int(r['official_bytes']),'sha256':r['sha256'],'status':'reused_hash_verified','source':config['msm_stage3_configuration']['dataset_handle']}
            for r in pd.read_csv(preserved/'MSM_DOWNLOAD_MANIFEST.csv').to_dict('records')}
        for r in json.loads((preserved/'manifests/input_manifest.json').read_text()):
            if Path(r['path']).name=='label.csv':
                relative='/'.join(Path(r['path']).parts[-3:]);known[relative]={'path':str(canonical/'01_raw_dataset/official_dataset'/relative),
                    'bytes':r['bytes'],'sha256':r['sha256'],'status':'reused_hash_verified','source':config['msm_stage3_configuration']['dataset_handle']}
        entries=list(known.values());source='''# MSM source and reuse information

Official [Kaggle dataset](https://www.kaggle.com/datasets/manufuturetoday/multi-sensor-for-metal-milling-anomaly), dataset ID8392825, DOI10.34740/kaggle/ds/8392825. Version pinned to **2**, exact handle `manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2`.

The official owner/slug/version and file hierarchy were verified in the preserved Stage1 acquisition evidence. The complete laboratory native labels, video, MTC, S2 audio and program/XML sources already existed. This run independently checked 282 required minimal sources against their saved official identities and downloaded **zero** files. The 40GB complete archive and industrial VF10 were not downloaded. The versioned raw path is a relative symlink to unchanged historical storage; see MSM/MIGRATION_PLAN.md and the timestamped reuse-verification receipt under source_evidence.

The manifest below indexes the same source bytes used by the reproduced label/alignment gate. Additional original data and historic annotations remain preserved in MILLING DATASET. Sensor input is only the 15 explicitly named MTC channels, not program/tool metadata or audio.
'''
    else:
        entries=[json.loads(p.read_text()) for p in sorted((canonical/'01_raw_dataset/source_evidence/receipts').glob('*.json')) if '.failure.' not in p.name]
        entries=[{k:r.get(k,'') for k in ['file','path','bytes','sha256','official_checksum','source','utc','status']} for r in entries]
        source='''# Handover official source information

Official [Zenodo record10708763](https://zenodo.org/records/10708763), DOI10.5281/zenodo.10708763, release **v1**. The record JSON, source-access receipt, exact official file URLs, acquisition UTC times, MD5 and SHA-256 checksums are saved in source_evidence. The sample passed both-robot video/timestamp/wrench/label gates before the complete train/validation/test archives were downloaded automatically. The sample is not an independent test set. Complete official archives remain preserved; only required RGB/timestamp/wrench/metadata members were extracted.

Associated publication: Thoduka et al., *A Multimodal Handover Failure Detection Dataset and Baselines*, ICRA2024, DOI10.1109/ICRA57147.2024.10610143. Author reference code is pinned to Git commit6665d7ec6a1ee724b62dc32a5dd5c2e1afc7f5ef at https://github.com/sthoduka/handover_failure_detection. Its nearest-raw-time resampling rule was reproduced exactly for every admitted trial. The supplied wrench_stats.json is preserved but never used as a globally fitted model normalizer.

The native release reports17 participants but supplies no participant-to-trial mapping in the archives, label/task metadata or inspected author code. Official split identities are kept unchanged; participant independence and participant-safe inner OOF are not invented. All learned F2/quality-fusion comparisons consequently remain blocked while the five permissible official-split baselines continue.

Active cohort and all model outputs: HANDOVER/experiments/common_support_v2. Earlier full-video audit files at the canonical stage root are historical evidence, not the evaluated cohort. See the explicit pre-score COMMON_SUPPORT_AMENDMENT.json for the horizon correction.
'''
        # Old audits remain where written; active references never replace them.
        for stage in ['02_labels_and_alignment','03_processed_model_inputs','04_experiment_protocol','05_trained_models','06_evaluation_results','07_robustness_experiments','08_visual_examples_and_eda']:
            pointer=canonical/stage/'active_common_support_v2'
            target=root/stage
            if not pointer.exists():pointer.symlink_to(os.path.relpath(target,pointer.parent),target_is_directory=True)
            elif pointer.resolve()!=target.resolve():raise ValueError('Active cohort reference mismatch')
            put(canonical/stage/'ACTIVE_EXPERIMENT.md',f'# Active Handover experiment\n\nThe evaluated cohort is `{target}`. [Open active files](active_common_support_v2/). Root-stage earlier full-video files are preserved historical audit evidence; no result from that excluded-test-tail cohort was fitted or scored.\n')
    manifest=canonical/'01_raw_dataset/download_manifest.csv'
    import io
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(entries[0]),lineterminator='\n');writer.writeheader();writer.writerows(entries)
    put(manifest,stream.getvalue());put(canonical/'01_raw_dataset/source_information.md',source)
    put(root/'02_labels_and_alignment/data_validation_report.md',f'# Validated input gate\n\nRead `{canonical}/09_final_reports/DATASET_VALIDATION.md` for the scientific explanation. The exact machine-readable gate is validation_gate.json. Native annotations and every excluded unit with its unmodified native label are retained beside it. Active model cohort: `{root}/03_processed_model_inputs/final_sample_manifest.csv`.\n')


def seal():
    """Snapshot only explicit research code; never inspect credentials or raw content."""
    provenance=Path('CROSS_DATASET_COMPARISON/provenance');done=provenance/'DELIVERY_COMPLETE.json'
    if done.exists():
        receipt=json.loads(done.read_text())
        for p,h in receipt['final_report_hashes'].items():
            if sha(p)!=h:raise ValueError('Sealed report changed')
        return
    code=[]
    for folder in ['CROSS_DATASET_COMPARISON/src','CROSS_DATASET_COMPARISON/tests','MSM/src','MSM/tests','HANDOVER/src','HANDOVER/tests']:
        code.extend(sorted(Path(folder).rglob('*.py')))
    code.extend(sorted(Path('MSM/99_preserved_previous_work/MILLING_DATASET/source/msm').glob('*.py')))
    code.extend(sorted(Path('MSM/99_preserved_previous_work/MILLING_DATASET/source/stage2').glob('*.py')))
    code.extend(sorted(Path('MSM/99_preserved_previous_work/MILLING_DATASET/source').glob('*.py')))
    code.extend(Path(p) for p in ['src/reassemble/section1_features.py','src/reassemble/section1_models.py','src/reassemble/section2_models.py'])
    snapshot=provenance/'source_snapshot';sources=[]
    for p in dict.fromkeys(code):
        if not p.is_file():raise ValueError('Required source missing: '+str(p))
        target=snapshot/p;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            if sha(target)!=sha(p):raise ValueError('Executed code changed after snapshot')
        else:shutil.copy2(p,target)
        sources.append({'path':str(p),'snapshot':str(target),'sha256':sha(p),'bytes':p.stat().st_size})
    versions={name:importlib.metadata.version(name) for name in ['torch','transformers','safetensors','numpy','pandas','scipy','scikit-learn','pillow','matplotlib','pytest','psutil','requests','joblib','threadpoolctl','soundfile']}
    import cv2,torch
    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu','--format=csv'],text=True,capture_output=True,check=True).stdout
    test_logs=[p for p in Path('CROSS_DATASET_COMPARISON/logs').glob('*.txt') if any(s in p.name for s in ['regression','integration','leakage_gate'])]
    commit=subprocess.run(['git','rev-parse','HEAD'],text=True,capture_output=True,check=True).stdout.strip()
    # Git reports paths/diff metadata only; no environment or session files read.
    dirty=subprocess.run(['git','status','--short','--untracked-files=no'],text=True,capture_output=True,check=True).stdout
    write_json(provenance/'software_and_source.json',{'utc':utc(),'git_commit':commit,'tracked_dirty_status':dirty,
        'python':platform.python_version(),'packages':versions,'sources':sources,
        'opencv':cv2.__version__,'CUDA':torch.version.cuda,'cuDNN':torch.backends.cudnn.version(),
        'GPU_snapshot_device_wide_not_our_utilization':gpu,'CPU_count':os.cpu_count(),'configured_threads':1,
        'validation_log_hashes':{str(p):sha(p) for p in test_logs},
        'task_authorization_sha256':sha(provenance/'task_authorization.txt'),
        'command':"OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH='src:MSM/99_preserved_previous_work/MILLING_DATASET/source:CROSS_DATASET_COMPARISON/src' ma_thesis_env/bin/python -B -m external_eval.run_all",
        'training':{'head_epochs':10,'gate_epochs':40,'head_selected_epoch':10,'seeds':[42,123,20261023]},
        'preserved_scope':'No PHM/Intel raw files or active REASSEMBLE outputs modified; no raw moves, deletion, staging or commits.'})
    report_hashes={};manifests={}
    for canonical,active in [(Path('MSM'),Path('MSM')),(Path('HANDOVER'),Path('HANDOVER/experiments/common_support_v2'))]:
        rows=[]
        for p in [canonical/'README.md',canonical/'01_raw_dataset/source_information.md',canonical/'01_raw_dataset/download_manifest.csv']:
            rows.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'stage':'source_and_handoff_index'})
            report_hashes[str(p)]=sha(p)
        for stage in ['02_labels_and_alignment','03_processed_model_inputs','04_experiment_protocol','05_trained_models','06_evaluation_results','07_robustness_experiments','08_visual_examples_and_eda']:
            for p in sorted((active/stage).rglob('*')):
                if p.is_symlink() or not p.is_file() or '__pycache__' in p.parts or '.writing' in p.name:continue
                rows.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'stage':stage})
        for p in sorted((canonical/'09_final_reports').rglob('*')):
            if p.is_file() and not p.name.endswith('.writing'):
                rows.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'stage':'09_final_reports'})
                report_hashes[str(p)]=sha(p)
        output=canonical/'09_final_reports/output_manifest.json';write_json(output,rows);manifests[str(output)]=sha(output)
    for p in Path('CROSS_DATASET_COMPARISON').glob('*.md'):report_hashes[str(p)]=sha(p)
    report_hashes['CROSS_DATASET_COMPARISON/comparison_tables.csv']=sha('CROSS_DATASET_COMPARISON/comparison_tables.csv')
    write_json(done,{'utc':utc(),'final_report_hashes':report_hashes,'output_manifest_hashes':manifests,
        'source_snapshot_manifest':'CROSS_DATASET_COMPARISON/provenance/software_and_source.json',
        'R_gate':'CROSS_DATASET_COMPARISON/provenance/R_source_gate_final.json','predictions_recomputed_metrics':True,
        'end_to_end_completed_permitted_models':True,'blocked_comparisons_not_imputed':True})
