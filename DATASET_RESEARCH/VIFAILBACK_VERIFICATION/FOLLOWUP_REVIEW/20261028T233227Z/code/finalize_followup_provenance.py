"""Final portable identities and validation receipts; fail rather than overwrite."""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent
REPO = SOURCE.parents[1]


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def save(relative, value):
    with (RUN / relative).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    validation = json.loads((RUN / 'provenance/FINAL_VALIDATION.json').read_text())
    assert validation['passed']
    source_files = [SOURCE / 'VIFAILBACK_INDEPENDENT_BLINDED_VISUAL_REVIEW.md', SOURCE / 'OUTPUT_MANIFEST.json', SOURCE / 'SOURCE_PROVENANCE.json',
                    SOURCE / 'source_evidence/vifailback_files.json']
    source_files += list((SOURCE / 'source_evidence/vifailback/meta').glob('*.json'))
    source_files += list((SOURCE / 'source_evidence/vifailback/meta').glob('*.jsonl'))
    source_files += [SOURCE / 'checks' / name for name in ['pilot_numerical_audit.json','pilot_media_audit.json',
                    'original_hdf5_conversion_audit.json','constant_state_origin_audit.json','original_publisher_identity_validation.json']]
    inputs = [{'path': str(path.relative_to(REPO)), 'bytes': path.stat().st_size, 'sha256': digest(path)} for path in source_files]
    save('provenance/INPUT_MANIFEST.json', {'metadata_review_and_prior_checks': inputs,
          'original_native_annotation_files': 'ORIGINAL_ANNOTATION_SOURCE_HASHES.json',
          'all_actual_numerical_inputs': 'SENSOR_TABLE_INVENTORY.json',
          'inspected_reassemble_inputs': 'REASSEMBLE_SOURCE_AND_CHECKPOINT_HASHES.json'})
    scripts = ['acquire_sensor_tables.py','audit_unblinding_and_labels.py','audit_sensors_and_splits.py',
               'audit_reassemble_reference.py','inspect_sensor_anomalies.py','refine_sensor_qc_v2.py',
               'plot_sensor_diagnostics.py','write_followup_reports.py','validate_followup.py','finalize_followup_provenance.py']
    package_names = ['numpy','pandas','pyarrow','h5py','requests','matplotlib','torch','safetensors','scikit-learn']
    package_versions = {name: importlib.metadata.version(name) for name in package_names}
    state = json.loads((RUN / 'provenance/INITIAL_REPOSITORY_STATE.json').read_text())
    tracked = subprocess.check_output(['git','status','--short','--untracked-files=no'],cwd=REPO,text=True)
    assert tracked == state['tracked_status']
    git_ignore = subprocess.run(['git','check-ignore',str(RUN / 'source_evidence/data/chunk-000/episode_000000.parquet'),str(RUN / 'EXECUTIVE_VERDICT.md')],cwd=REPO,text=True,capture_output=True)
    assert git_ignore.returncode == 0
    save('provenance/FINAL_PROVENANCE.json', {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'created_Europe_Berlin': datetime.now(ZoneInfo('Europe/Berlin')).isoformat(),
        'run_directory': str(RUN.relative_to(REPO)), 'git_commit': state['git_commit'],
        'tracked_status_unchanged': True, 'tracked_status': tracked,
        'tracked_diff_stat': subprocess.check_output(['git','diff','--stat'],cwd=REPO,text=True),
        'software': {'python': sys.version, 'platform': platform.platform(), 'packages': package_versions},
        'commands': ['ma_thesis_env/bin/python -B ' + str((RUN / 'code' / name).relative_to(REPO)) for name in scripts],
        'thread_overrides_for_numerical_audits': {'OMP_NUM_THREADS': '2', 'OPENBLAS_NUM_THREADS': '2'},
        'review_lock': {'method': 'Byte-identical copy and Markdown case-table parse before unblinding; timestamp and SHA preserved in00_LOCKED_REVIEW/REVIEW_LOCK.json',
                        'initial_header_parser_error': 'Corrected before lock completion and before comparison; original review untouched'},
        'configurations': [{'path': str(path.relative_to(RUN)), 'sha256': digest(path)} for path in sorted((RUN / 'config').glob('*.json'))],
        'new_acquisition_scope': 'All missing numerical Parquet tables plus three tiny original-HDF5 numerical/range checks and directory metadata',
        'new_parquet_files': 5180, 'new_parquet_bytes': 213092922, 'reused_verified_parquet_files': 22,
        'original_HDF5_range_bytes': 160512, 'full_videos_downloaded': 0,
        'model_training': False, 'neural_inference': False, 'calibration_or_fusion_fitted': False,
        'GPU_managed_or_initialized': False, 'existing_training_processes_managed': False,
        'source_evidence_rewritten_deleted_moved': False, 'staged_or_committed': False,
        'source_and_prior_export_hash_validation_passed': True, 'assertions_passed': validation['assertions'],
        'new_outputs_ignored_by_git': True, 'disk_free_bytes_at_completion': shutil.disk_usage(RUN).free,
        'limitations': ['Full RGB payload QC remains for4365 V2 episodes', 'Canonical-task55 coordinate conventions unresolved',
                        'Native human category is not exhaustive visual human detection', 'Device-clock calibration and hidden session/near-duplicate independence unverified',
                        'Source75-fit study incomplete; no ViFailback transfer/learning outcome exists']})
    outputs = []
    for path in sorted(RUN.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            outputs.append({'path': str(path.relative_to(RUN)), 'bytes': path.stat().st_size, 'sha256': digest(path)})
    save('provenance/OUTPUT_MANIFEST.json', {'self_excluded': True, 'files': outputs})
    for row in outputs:
        path = RUN / row['path']
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256']
    print(json.dumps({'outputs_manifest_entries': len(outputs), 'all_output_hashes_verified': True,
                      'validation_assertions': validation['assertions'], 'new_outputs_bytes': sum(row['bytes'] for row in outputs),
                      'disk_free_GiB': shutil.disk_usage(RUN).free / 1024**3}, indent=2))
