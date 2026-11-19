"""Full-backbone, sampler/epoch-resume, reload and sustained-performance gate."""
import gc
import os
import random
import subprocess
import sys
import time

import numpy as np
import torch

from phase_common import ROOT, AUDIT, STUDY, EXEC, EVIDENCE, config, read, write, sha, signature, utc, environment
from phase_model import make_model, make_optimizer, make_scheduler, snapshot
from phase_loader import EpochLoader, epoch_order, ActionDataset
from phase_checkpoint import EpochRecovery, atomic_torch_save, rng_state, restore_rng
from phase_training import train_epoch, predict, tensor_equal_tree
sys.path.insert(0, str(AUDIT / 'source'))
from gpu_audit import Monitor


def main():
    check = read(EVIDENCE / 'PHASE1_INPUT_VERIFICATION_STATUS.json')
    assert check['status'] == 'COMPLETE' and check['completed'] == 4530
    occupied = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip()
    assert not occupied, 'GPU_BUSY: wait for other job; do not contend'
    assert torch.cuda.device_count() == 1
    c = config()
    folder = EXEC / '26102026_full_cnn_preflight_01'
    folder.mkdir(exist_ok=True)
    write(folder / 'PHASE1_PREFLIGHT_PROVENANCE.json', dict(environment(),
          sources={p.name: sha(p) for p in (ROOT/'26102026_source').glob('*.py')},
          GPU=subprocess.check_output(['nvidia-smi', '--query-gpu=index,uuid,name,memory.total,driver_version', '--format=csv'], text=True),
          pretrained_identity=read(STUDY/'provenance/original_pretrained_identity.json'),
          input_manifest_sha256=sha(EVIDENCE/'PHASE1_INPUT_IDENTITY_MANIFEST.json')))
    jobs = read(EVIDENCE / 'PHASE1_FIT_PLAN.json')
    job = next(j for j in jobs if j['role'] == 'outer_assessment')
    selected = epoch_order(job['training'], 42, 1)[:24]
    rows = read(EVIDENCE / 'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    y = torch.tensor([r['failure'] for r in rows], dtype=torch.float32, device='cuda')
    features = torch.from_numpy(np.load(STUDY / 'shared_cache/original_features_16.npy', allow_pickle=False)).cuda()
    balance = torch.tensor(float((len(job['training']) - y[job['training']].sum()) / y[job['training']].sum()), device='cuda')
    model = make_model('C_full_finetuned16', job['training'], 42)
    frozen = make_model('B_long_frozen16', job['training'], 42)
    inputs = ActionDataset(selected[:3])
    initialization_errors = []
    model.eval()
    frozen.eval()
    observed_classes = set()
    hooks = [m.register_forward_hook(lambda m, a, out: observed_classes.add(type(m).__name__)) for m in model.backbone.modules()]
    with torch.no_grad():
        for i, row in enumerate(selected[:3]):
            x = inputs[i][0].unsqueeze(0).cuda()
            error = float((model(x) - frozen(features[row:row+1])).abs().max())
            assert error <= 1e-5, ('INITIAL_FEATURE_REPRESENTATION_MISMATCH', error)
            initialization_errors.append(error)
    for hook in hooks:
        hook.remove()
    assert not any(any(t in n.lower() for t in ['attention', 'decoder', 'detector']) for n in observed_classes)
    del inputs, frozen, x
    optimizer = make_optimizer(model)
    scheduler = make_scheduler(optimizer)
    initial = snapshot(model)
    recovery = EpochRecovery(folder, signature({'type': 'real-full-CNN-epoch-resume', 'seed': 42, 'training': selected.tolist()}))
    with EpochLoader(selected, folder, 'uninterrupted') as loader:
        first = train_epoch(model, optimizer, epoch_order(selected, 42, 1), y, features, loader, balance, inspect=True)
        scheduler.step()
        recovery.save({'model': model.state_dict(), 'optimizer': optimizer.state_dict(), 'scheduler': scheduler.state_dict(),
            'completed_epoch': 1, 'order': selected.tolist(), 'seed': 42, 'next_epoch': 2})
        second = train_epoch(model, optimizer, epoch_order(selected, 42, 2), y, features, loader, balance)
        scheduler.step()
    expected = snapshot(model)
    expected_optimizer = {k: v for k, v in optimizer.state_dict().items()}
    expected_scheduler = scheduler.state_dict()
    expected_rng = rng_state()
    saved = recovery.load()
    model.load_state_dict(saved['model'])
    optimizer = make_optimizer(model)
    scheduler = make_scheduler(optimizer)
    optimizer.load_state_dict(saved['optimizer'])
    scheduler.load_state_dict(saved['scheduler'])
    restore_rng(saved['random'])
    with EpochLoader(selected, folder, 'resumed_epoch') as loader:
        resumed = train_epoch(model, optimizer, epoch_order(saved['order'], saved['seed'], saved['next_epoch']), y, features, loader, balance)
        scheduler.step()
    assert first['actions'] == second['actions'] == resumed['actions'] == 24
    assert second['order_sha256'] == resumed['order_sha256']
    assert tensor_equal_tree(expected, model.state_dict()), 'FULL_CNN_RESUME_PARAMETER_MISMATCH'
    assert tensor_equal_tree(expected_optimizer, optimizer.state_dict()), 'FULL_CNN_RESUME_OPTIMIZER_MISMATCH'
    assert tensor_equal_tree(expected_scheduler, scheduler.state_dict())
    assert tensor_equal_tree(expected_rng, rng_state()), 'FULL_CNN_RESUME_RNG_MISMATCH'
    write(folder / 'PHASE1_FULL_CNN_GRADIENT_EVIDENCE.json', first['gradient_evidence'])
    write(folder / 'PHASE1_FULL_CNN_RESUME.json', {'passed': True, 'boundary': 'completed epoch',
          'uninterrupted_and_resumed_parameters_optimizer_scheduler_rng_exact': True,
          'sample_count_each_epoch': 24, 'epoch2_order_sha256': second['order_sha256'],
          'prefetched_draining_not_training': True})
    reload_path = folder / 'PHASE1_RELOAD_MODEL.pt'
    atomic_torch_save(reload_path, {'model': snapshot(model)})
    with EpochLoader(selected[:3], folder, 'reload_reference') as loader:
        before, _ = predict(model, selected[:3], y, features, loader)
    reloaded = make_model('C_full_finetuned16', job['training'], 42)
    reloaded.load_state_dict(torch.load(reload_path, map_location='cpu', weights_only=True)['model'])
    with EpochLoader(selected[:3], folder, 'reload_actual') as loader:
        after, _ = predict(reloaded, selected[:3], y, features, loader)
    error = float(np.max(np.abs(before-after)))
    assert error <= 1e-5
    write(folder / 'PHASE1_FULL_CNN_RELOAD.json', {'passed': True, 'maximum_logit_error': error, 'model_sha256': sha(reload_path)})
    del reloaded, optimizer, scheduler, saved, expected, expected_optimizer, initial
    gc.collect()
    torch.cuda.empty_cache()
    optimizer = make_optimizer(model)
    windows = []
    with EpochLoader(selected, folder, 'benchmark') as loader:
        for warmup in range(2):
            train_epoch(model, optimizer, epoch_order(selected, 42, warmup+10), y, features, loader, balance)
        for repetition in range(2):
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            start, count, updates, loading, compute = time.monotonic(), 0, 0, 0.0, 0.0
            with Monitor(.5) as monitor:
                while time.monotonic() - start < 60:
                    result = train_epoch(model, optimizer, epoch_order(selected, 42, 30+updates), y, features, loader, balance)
                    count += result['actions']
                    updates += result['optimizer_updates']
                    loading += result['loading_wait_seconds']
                    compute += result['forward_backward_cuda_event_seconds']
                torch.cuda.synchronize()
                seconds = time.monotonic() - start
            window = {'repetition': repetition, 'seconds': seconds, 'actions': count, 'actions_per_second': count/seconds,
                'optimizer_updates': updates, 'optimizer_updates_per_second': updates/seconds,
                'GPU_compute_percent': float(np.mean([r['gpu_compute_percent'] for r in monitor.rows])),
                'peak_allocated_bytes': torch.cuda.max_memory_allocated(), 'peak_reserved_bytes': torch.cuda.max_memory_reserved(),
                'peak_vram_MiB': max(r['vram_MiB'] for r in monitor.rows),
                'CPU_loading_wait_seconds': loading, 'forward_backward_cuda_event_seconds': compute,
                'representative_training_epoch_seconds': len(job['training'])*seconds/count,
                'reference_2966_action_epoch_seconds': 2966*seconds/count}
            windows.append(window)
            write(folder / f'PHASE1_BENCHMARK_GPU_WINDOW_{repetition}.json', monitor.rows)
            print(utc(), 'FULL_BACKBONE_BENCHMARK', window, flush=True)
    close_records = [read(p) for p in (folder/'26102026_checks').glob('*shutdown*.json')]
    assert close_records and all(r['passed'] for r in close_records)
    speed = sum(w['actions'] for w in windows)/sum(w['seconds'] for w in windows)
    train_actions_per_seed_epoch = sum(len(j['training']) for j in jobs)
    estimates = {'full_CNN_training_hours_min25': train_actions_per_seed_epoch*25*3/speed/3600,
                 'full_CNN_training_hours_max50': train_actions_per_seed_epoch*50*3/speed/3600,
                 'method': 'Measured full-backbone actions/s times exact T presentation counts; validation/inference/checkpoint overhead additional',
                 'T_actions_per_seed_epoch_over25fits': train_actions_per_seed_epoch,
                 'main_full_backbone_fits': 75, 'main_frozen_fits': 75,
                 'planning_hours_with_20_to_40_percent_overhead': [train_actions_per_seed_epoch*25*3/speed/3600*1.2,
                                                                 train_actions_per_seed_epoch*50*3/speed/3600*1.4]}
    write(EVIDENCE / 'PHASE1_FULL_CNN_BENCHMARK.json', {'windows': windows, 'actions_per_second': speed, 'time_estimates': estimates,
          'full_backbone': True, 'precision': 'float32', 'loader_workers': 4, 'frames': 16,
          'initial_frozen_feature_logit_errors': initialization_errors, 'observed_forward_classes': sorted(observed_classes),
          'all_workers_clean': True, 'source': 'new full-backbone workload; not the earlier final-stage benchmark'})
    write(EVIDENCE / 'PHASE1_FULL_CNN_GATE.json', {'utc': utc(), 'status': 'PASSED', 'full_matrix_allowed': True,
          'all4530_inputs_verified': True, 'whole_CNN_gradient_and_updates_verified': True,
          'epoch_boundary_resume_verified': True, 'saved_model_reload_verified': True,
          'two_full_backbone_sustained_windows': True, 'worker_shutdown_verified': True,
          'protocol_sha256': sha(ROOT/'26102026_configuration/PHASE1_CONFIG.json'),
          'fit_plan_sha256': sha(EVIDENCE/'PHASE1_FIT_PLAN.json'), 'time_estimates': estimates})
    print(utc(), 'FULL_CNN_PERFORMANCE_GATE_PASSED', estimates, flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        write(EVIDENCE / 'PHASE1_FULL_CNN_GATE.json', {'utc': utc(), 'status': 'BLOCKED_PREFLIGHT',
              'full_matrix_allowed': False, 'error': repr(exc)})
        raise
