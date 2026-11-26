"""Read-only source-study interlock and prospective compute/storage admission."""
from __future__ import annotations
import os
from pathlib import Path
import shutil
import subprocess
import psutil
from .common import REPO, STUDY, protocol, read_json, sha256, relative, utc, write_json, immutable_json

SOURCE = REPO / '26.10.2026_feedback_experiments/26102026_phase1_full_cnn_seed_stability'
REVISION = SOURCE / '26102026_c_only_20epoch_revision_01'
STOP = REVISION / '02112026_stop_after25fits_01'
SOURCE_SCRIPTS = {'c20_controller.py', 'c20_train.py', 'stop_after25_controller.py',
                  'phase_controller.py', 'phase_training.py', 'run_phase1.py',
                  'compare100_controller.py', 'compare100_train.py',
                  'run_pipeline.py', 'run_full_pipeline.py'}
GIB = 1024 ** 3


def verify_source_stop():
    terminal_path = STOP / 'STOP_AFTER_25_COMPLETE.json'
    terminal = read_json(terminal_path)
    required = {'completed_C_fits': 25, 'allowed_seed': 42, 'epochs_per_fit': 20,
                'original_75_fit_study_complete': False, 'deferred_fits': 50,
                'additional_CNN_training_launched_after_cap': False,
                'all25_completion_and_model_prediction_hashes_verified': True}
    for key, value in required.items():
        if terminal.get(key) != value:
            raise ValueError(f'Source approved-stop identity failed: {key}')
    config = REVISION / '26102026_configuration/PHASE1_C_ONLY_CONFIG.json'
    config_sha = sha256(config)
    if config_sha != terminal['original_training_configuration_sha256']:
        raise ValueError('Source training configuration changed')
    plan = read_json(SOURCE / '26102026_evidence/PHASE1_FIT_PLAN.json')
    if len(plan) != 25:
        raise ValueError('Unexpected source role count')
    evidence = []
    for job in plan:
        receipt_path = REVISION / '26102026_execution' / f'PHASE1_C_ONLY_COMPLETE_SEED42_JOB{job["job_index"]:02d}.json'
        receipt = read_json(receipt_path)
        if not (receipt['status'] == 'COMPLETE' and receipt['seed'] == 42
                and receipt['job_index'] == job['job_index'] and receipt['executed_epochs'] == 20
                and receipt['revision_configuration_sha256'] == config_sha):
            raise ValueError('Source fit receipt failed')
        role = job['role'].replace('_', '')
        root = SOURCE / '26102026_execution/26102026_main_run_01' / f'26102026_seed42_C_full_finetuned16_outer{job["outer_fold_original"]+1}_{role}'
        for name, key in [('PHASE1_PREDICTIONS.json', 'predictions_sha256'),
                          ('PHASE1_BEST_MODEL.pt', 'selected_model_sha256')]:
            path = root / name
            if sha256(path) != receipt[key]:
                raise ValueError(f'Source completed artifact changed: {relative(path)}')
        evidence.append({'receipt': relative(receipt_path), 'sha256': sha256(receipt_path),
                         'selected_model_sha256': receipt['selected_model_sha256'],
                         'predictions_sha256': receipt['predictions_sha256']})
    return {'verified': True, 'approved_stop_receipt': relative(terminal_path),
            'approved_stop_sha256': sha256(terminal_path), 'complete_fits': 25,
            'deferred_fits': 50, 'original_75_fit_complete': False, 'fits': evidence,
            'authority': 'Current explicit user training authorization and prior approved25fitstop; legacy75gate unchanged'}


def source_processes():
    result = []
    for process in psutil.process_iter(['pid', 'create_time', 'cmdline', 'status']):
        try:
            info = process.info
            if info['pid'] == os.getpid() or info['status'] == psutil.STATUS_ZOMBIE:
                continue
            args = info['cmdline'] or []
            names = [Path(arg).name for arg in args if len(arg) < 512 and '\n' not in arg]
            matches = sorted(set(names) & SOURCE_SCRIPTS)
            if matches:
                result.append({'pid': info['pid'], 'create_time': info['create_time'], 'scripts': matches})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return result


def gpu_snapshot(allowed_pids=()):
    allowed = {os.getpid(), *map(int, allowed_pids)}
    query = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,utilization.gpu,uuid',
                            '--format=csv,noheader,nounits'], check=True, capture_output=True, text=True)
    devices = []
    for line in query.stdout.splitlines():
        index, name, total, used, util, uuid = [x.strip() for x in line.split(',')]
        devices.append({'index': int(index), 'name': name, 'memory_total_MiB': int(total),
                        'memory_used_MiB': int(used), 'utilization_percent': int(util), 'uuid': uuid})
    processes = subprocess.run(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader,nounits'],
                               check=True, capture_output=True, text=True)
    pids = [int(x.strip()) for x in processes.stdout.splitlines() if x.strip().isdigit()]
    return {'utc': utc(), 'devices': devices, 'compute_pids': pids,
            'other_compute_pids': [pid for pid in pids if pid not in allowed]}


def gate(extra_bytes=0, require_gpu=True):
    reserve = protocol()['resources']['minimum_free_GiB'] * GIB
    free = shutil.disk_usage(STUDY).free
    state = {'utc': utc(), 'free_bytes': free, 'minimum_free_bytes': reserve,
             'next_write_bytes': int(extra_bytes), 'source_processes': source_processes()}
    reasons = []
    if free - extra_bytes < reserve:
        reasons.append('DISK_RESERVE')
    if require_gpu:
        state['gpu'] = gpu_snapshot()
        if len(state['gpu']['devices']) != 1:
            reasons.append('EXPECTED_SINGLE_GPU')
        if state['gpu']['other_compute_pids']:
            reasons.append('OTHER_GPU_WORK')
        if state['source_processes']:
            reasons.append('SOURCE_CONTROLLER_ACTIVE')
    state['ready'] = not reasons
    state['reasons'] = reasons
    return state


def prospective_admission(context, benchmark):
    """Admit only from measured costs and disk, before examining new held-out scores."""
    if benchmark.get('status') != 'PASS':
        raise ValueError('Bounded full-backbone verification has not passed')
    source = verify_source_stop()
    live = gate(require_gpu=True)
    if not live['ready']:
        raise RuntimeError(f'Resource gate failed: {live["reasons"]}')
    batch = read_json(STUDY / '13_reproducibility/BOUNDED_BATCH8_THROUGHPUT.json')
    if batch.get('status') != 'PASS' or batch.get('training', {}).get('training_episodes') != 8:
        raise ValueError('Production8episode loader/update benchmark has not passed')
    train_cost = float(batch['training_seconds_per_episode'])
    inference_cost = float(batch['inference_seconds_per_episode'])
    if train_cost <= 0 or inference_cost <= 0:
        raise ValueError('Missing measured throughput')
    # Conservative persistent allowance includes full best plus final/recovery
    # (hardlinked final), optimizer moments and the transactional embedded best.
    fit_bytes = max(256 * 1024 ** 2, int(benchmark.get('full_fit_checkpoint_bytes_estimate', 0)))
    scratch = max(fit_bytes * 2, GIB)
    head_and_reports = GIB
    jobs = context['jobs']
    pilot = jobs[protocol()['pilot']['base_job_id']]
    pilot_seconds = 100 * (len(pilot['ids']['T']) * train_cost + len(pilot['ids']['V']) * inference_cost)
    pilot_seconds += (len(pilot['ids']['C']) + len(pilot['ids']['A']) + len(jobs['outer0_final']['ids']['A'])) * inference_cost
    per_seed_seconds = sum(20 * (len(j['ids']['T']) * train_cost + len(j['ids']['V']) * inference_cost)
                           + (len(j['ids']['C']) + len(j['ids']['A'])) * inference_cost for j in jobs.values())
    reserve = protocol()['resources']['minimum_free_GiB'] * GIB
    seeds = []
    for seed in protocol()['seeds']:
        projected = (1 + 12 * (len(seeds) + 1)) * fit_bytes + scratch + head_and_reports
        if live['free_bytes'] - projected >= reserve:
            seeds.append(seed)
        else:
            break
    if not seeds:
        raise RuntimeError('Insufficient storage for pilot plus complete primary12role seed42 matrix and reserve')
    result = {'schema': 1, 'utc': utc(), 'protocol_sha256': sha256(STUDY / '01_protocol_and_source_evidence/protocol.json'),
              'status': 'ADMITTED', 'source_stop': source, 'resource_snapshot': live,
              'admitted_twenty_epoch_seeds': seeds, 'deferred_twenty_epoch_seeds': [s for s in protocol()['seeds'] if s not in seeds],
              'pilot_seed': 42, 'pilot_outer': 0, 'full_fit_count': 1 + 12 * len(seeds),
              'full_fit_epoch_count': 100 + 240 * len(seeds),
              'full_fit_checkpoint_bytes_estimate': fit_bytes, 'atomic_and_benchmark_scratch_bytes': scratch,
              'head_and_reports_allowance_bytes': head_and_reports,
              'projected_additional_bytes': (1 + 12 * len(seeds)) * fit_bytes + scratch + head_and_reports,
              'projected_free_after_bytes': live['free_bytes'] - ((1 + 12 * len(seeds)) * fit_bytes + scratch + head_and_reports),
              'throughput_source': '13_reproducibility/BOUNDED_BATCH8_THROUGHPUT.json',
              'training_seconds_per_episode_including_loader': train_cost,
              'inference_seconds_per_episode_including_loader': inference_cost,
              'estimated_full100_hours': pilot_seconds / 3600,
              'estimated_full20_hours_per_seed': per_seed_seconds / 3600,
              'estimated_total_GPU_process_hours': (pilot_seconds + len(seeds) * per_seed_seconds) / 3600,
              'estimate_uncertainty': 'Bounded8episode batch includes loader startup and decoding, conservatively repeated in forecast; actual whole-epoch throughput and wall time replace this estimate. Decoding varies by episode. No lease duration was provided.',
              'selection_basis': 'Frozen ordered seeds plus measured disk/throughput only; no held-out results consulted',
              'epoch_reduction': False}
    immutable_json(STUDY / '01_protocol_and_source_evidence/RESOURCE_ADMISSION.json', result)
    return result
