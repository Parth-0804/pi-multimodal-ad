"""Seal source and output manifests for the verification handoff."""
import hashlib,json,platform,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
import cv2,h5py,numpy,pandas,PIL,requests
from sources import ROOT,HF,REV,MAX_BYTES,MIN_FREE
from original_annotations import ORIGINAL_REV


if __name__=='__main__':
    source=ROOT/'source_evidence';records=[]
    for receipt in sorted(source.rglob('*.receipt.json')):
        data=json.loads(receipt.read_text());records.append({'local_file':str(receipt.relative_to(ROOT)).removesuffix('.receipt.json'),'receipt':str(receipt.relative_to(ROOT)),**data})
    source_members=json.loads((ROOT/'checks/secondary_bounded_native_audit.json').read_text())['metadata_members']
    config={'task':'Independent ViFailback source labels, measured modalities and visual feasibility verification',
        'active_datasets':[HF,'Zenodo 4578539'],'conversion_revision':REV,'original_revision':ORIGINAL_REV,
        'prediction_unit':'Whole original episode','native_target_mapping':{'yes':1,'no':0},
        'pilot_policy':json.loads((ROOT/'config/pilot_policy.json').read_text()),'maximum_source_acquisition_bytes':MAX_BYTES,
        'minimum_free_bytes':MIN_FREE,'no_full_dataset':True,'no_training':True,'no_CNN_extraction':True,'no_GPU_experiment':True,
        'worker_limits':{'network_workers':4,'video_decode_processes':2,'FFmpeg_decoder_threads':1,'FFmpeg_filter_threads':1,'hardware_acceleration':'none'},
        'source_scope':'20 matched executions; two complete original HDF5 validation samples; two additional quality-control tables/high videos; bounded original QC HDF5 ranges; secondary archive prefixes only',
        'frame_selection':'floor(k*(N-1)/15), k=0..15, all views/classes','crop':[0.2,0.2,0.8,0.8],
        'cohort_status':'Only selected actual samples validated; 5023-row metadata QC cohort is provisional, not fully acquired/validated',
        'duplicate_policy':'Preserve raw sources; future representative/group policy to be frozen before training'}
    (ROOT/'config/verification_config.json').write_text(json.dumps(config,indent=2)+'\n')
    project=ROOT.parents[1];git=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    command_prefix='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ma_thesis_env/bin/python -B '+str(ROOT.relative_to(project))+'/code/'
    scripts=['sources.py','audit_labels.py','original_annotations.py','select_pilot.py','acquire_pilot.py','acquire_original_pair.py',
        'build_gallery.py','record_blind_screen.py','inspect_secondary.py','verify_original_samples.py','screen_groups_and_quality.py',
        'check_constant_state_origin.py','write_reports.py','validate_delivery.py','verify_original_publisher_ids.py','finalize_provenance.py']
    ffmpeg=project/'MILLING DATASET/.tools/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
    ff_version=subprocess.check_output([str(ffmpeg),'-version'],text=True).splitlines()[0]
    provenance={'created_utc':datetime.now(timezone.utc).isoformat(),'run_directory':str(ROOT.relative_to(project)),
        'git_commit':git,'pre_existing_tracked_changes':['README.md','REPO_MAP.md','docs/thesis_research_direction/THESIS_EVIDENCE_GAPS.md'],
        'tracked_diff_stat_at_completion':subprocess.check_output(['git','diff','--stat'],text=True),
        'historical_inputs_outputs_edited':False,'training_processes_managed':False,'staged_or_committed':False,
        'configuration':config,'source_records':records,
        'secondary_extracted_native_members':[{'name':m['name'],'bytes':m['bytes'],'sha256':m['sha256'],'parent_archive':'place_action_test.tar.gz','parent_record':'10.5281/zenodo.4578539','full_archive_downloaded_or_hashed':False} for m in source_members],
        'software':{'python':platform.python_version(),'numpy':numpy.__version__,'pandas':pandas.__version__,'h5py':h5py.__version__,'Pillow':PIL.__version__,'OpenCV':cv2.__version__,'requests':requests.__version__,'ffmpeg':ff_version},
        'commands':[command_prefix+name for name in scripts]+['ma_thesis_env/bin/python -B -m pip check','git diff --check','git status --short --untracked-files=normal -- DATASET_RESEARCH/VIFAILBACK_VERIFICATION'],
        'public_repository_refs':{'x1nyuzhou/ViFailback':'3be62c639b1a5a59bea201d646309d225eb00db9','sthoduka/motion_anomaly_detection':'204d91e1ea0f7012e27400fb0842e44debc035f2'},
        'source_acquisition_bytes':sum(r.get('bytes',0) for r in records),'free_bytes_at_completion':shutil.disk_usage(ROOT).free,
        'validation':{k:v for k,v in json.loads((ROOT/'checks/validation.json').read_text()).items() if k!='results'},
        'original_publisher_validation':{k:v for k,v in json.loads((ROOT/'checks/original_publisher_identity_validation.json').read_text()).items() if k!='rows'},
        'warnings':['Index/PTS agreement does not establish hardware capture synchronization or calibrated latency',
            '173 constant-position flags; two upstream defects confirmed; full-cohort QC not complete',
            'Structural-zero joint effort and gripper velocity fields are not useful physical sensing',
            'Six duplicate episode components; no exhaustive near-duplicate/cross-dataset overlap audit',
            'No verified per-episode session/operator/object-instance or teleoperation/policy mapping',
            'Masked-key initial screen is AI-assisted, not independent human validation',
            'Secondary partition counts publisher-reported; actual sample contains two anomalous trial annotations only',
            'Full archive checksums and full-dataset payload validation unavailable because only bounded sources were acquired'],
        'method':'Anonymous public HTTPS, pinned revisions, no credentials consulted; bounded Range requests must return 206; sources preserved without overwrite'}
    out=ROOT/'SOURCE_PROVENANCE.json'
    if out.exists():raise FileExistsError(out)
    out.write_text(json.dumps(provenance,indent=2)+'\n')
    manifest=[]
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path==ROOT/'OUTPUT_MANIFEST.json':continue
        relative=path.relative_to(ROOT)
        if relative.parts[0]=='source_evidence':continue
        data=path.read_bytes();manifest.append({'path':str(relative),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    (ROOT/'OUTPUT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'source_acquisition_bytes':provenance['source_acquisition_bytes'],'output_files':len(manifest),'free_GiB':provenance['free_bytes_at_completion']/1024**3,'source_records':len(records)}))
