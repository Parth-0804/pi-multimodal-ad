"""Long frozen/full-CNN fits using the existing representation and F2 primitives."""
import argparse
import gc
import hashlib
import json
import random
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, roc_auc_score

from phase_common import ROOT, AUDIT, STUDY, EXEC, EVIDENCE, CONFIG, config, read, write, sha, signature, utc, foreign_gpu_processes, host_resources
from phase_model import make_model, make_optimizer, make_scheduler, snapshot, gradient_evidence, calibrate, calibrated
from phase_loader import EpochLoader, epoch_order
from phase_checkpoint import EpochRecovery, atomic_torch_save, cpu_tree, restore_rng, selected_payloads, restore_selections
from phase_metrics import better, stop_after_epoch
sys.path.insert(0, str(AUDIT / 'source'))
from gpu_audit import Monitor


def folder_for(arm, seed, job):
    role = job['role'].replace('_', '')
    return EXEC / f"26102026_seed{seed}_{arm}_outer{job['outer_fold_original']+1}_{role}"


def run_identity(arm, seed, job):
    return signature({'arm': arm, 'seed': seed, 'job': job, 'configuration': sha(CONFIG),
                      'input_manifest': sha(EVIDENCE / 'PHASE1_INPUT_IDENTITY_MANIFEST.json'),
                      'features': read(EVIDENCE / 'PHASE1_INPUT_VERIFICATION_STATUS.json')['original_features16_sha256']})


def tensor_equal_tree(a, b):
    if torch.is_tensor(a):
        return torch.equal(a.detach().cpu(), b.detach().cpu())
    if isinstance(a, np.ndarray):
        return np.array_equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(tensor_equal_tree(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(tensor_equal_tree(x, y) for x, y in zip(a, b))
    return a == b


def train_epoch(model, optimizer, order, labels, features, loader, pos_weight, *, inspect=False, progress=None):
    model.train()
    if loader is not None:
        loader.set_order(order)
        stream = iter(loader)
    else:
        stream = iter((None, None, None, int(row)) for row in order)
    losses_sum, count, updates, loading_wait, compute_ms = 0.0, 0, 0, 0.0, 0.0
    observed, first_state, first_grad = [], snapshot(model) if inspect else None, None
    for offset in range(0, len(order), 8):
        actual = min(8, len(order) - offset)
        optimizer.zero_grad(set_to_none=True)
        losses, events = [], []
        for _ in range(actual):
            start = time.perf_counter()
            x, target, key, row = next(stream)
            loading_wait += time.perf_counter() - start
            row = int(row)
            assert row == int(order[count]), 'TRAINING_SAMPLE_ORDER_DRIFT'
            observed.append(row)
            if model.full:
                x = x.unsqueeze(0).to('cuda', non_blocking=True)
                target = target.to('cuda', non_blocking=True)
            else:
                x = features[row:row+1]
                target = labels[row:row+1]
            a, b = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
            a.record()
            logit = model(x)
            loss = torch.nn.functional.binary_cross_entropy_with_logits(logit, target, pos_weight=pos_weight)
            (loss / actual).backward()
            b.record()
            losses.append(loss.detach())
            events.append((a, b))
            count += 1
        if inspect and first_grad is None:
            first_grad = gradient_evidence(model)
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), config()['gradient_clip'])
        assert bool(torch.isfinite(norm) & torch.isfinite(torch.stack(losses)).all()), 'UNSAFE_TRAINING_NUMERICS'
        optimizer.step()
        losses_sum += float(torch.stack(losses).sum())
        torch.cuda.synchronize()
        compute_ms += sum(a.elapsed_time(b) for a, b in events)
        updates += 1
        if progress and updates % 25 == 0:
            progress(count, len(order), updates)
    if loader is not None:
        try:
            next(stream)
            raise AssertionError('TRAINING_LOADER_HAS_EXTRA_ACTIONS')
        except StopIteration:
            pass
    assert observed == np.asarray(order).tolist()
    evidence = None
    if inspect:
        after = snapshot(model)
        changed = [name for name in first_state if not torch.equal(first_state[name], after[name])]
        assert any(name.startswith('head.') for name in changed)
        if model.full:
            for prefix in ['backbone.embedder.', 'backbone.encoder.stages.0.', 'backbone.encoder.stages.1.',
                           'backbone.encoder.stages.2.', 'backbone.encoder.stages.3.']:
                assert any(name.startswith(prefix) for name in changed), ('UNCHANGED_BACKBONE_SCOPE', prefix)
            assert not any('running_mean' in name or 'running_var' in name for name in changed)
        evidence = {'gradient_parameters': first_grad, 'changed_state_names': changed,
                    'running_statistics_unchanged': True, 'all_parameters_trainable': all(p.requires_grad for p in model.parameters()),
                    'CNN_parameters': sum(p.numel() for p in model.backbone.parameters()) if model.full else 0,
                    'head_parameters': sum(p.numel() for p in model.head.parameters())}
    return {'training_loss': losses_sum / count, 'actions': count, 'optimizer_updates': updates,
            'loading_wait_seconds': loading_wait, 'forward_backward_cuda_event_seconds': compute_ms / 1000,
            'order_sha256': hashlib.sha256(np.asarray(observed, dtype=np.int64).tobytes()).hexdigest(),
            'gradient_evidence': evidence}


def predict(model, rows, labels, features, loader=None, *, pos_weight=None):
    model.eval()
    rows = np.asarray(rows, dtype=int)
    if loader is not None:
        loader.set_order(rows)
        iterator = iter(loader)
    else:
        iterator = iter((None, None, None, int(row)) for row in rows)
    values, observed = [], []
    with torch.inference_mode():
        for x, target, key, row in iterator:
            row = int(row)
            if model.full:
                x = x.unsqueeze(0).to('cuda', non_blocking=True)
            else:
                x = features[row:row+1]
            values.append(model(x).detach())
            observed.append(row)
    assert observed == rows.tolist(), 'PREDICTION_ORDER_DRIFT'
    raw = torch.cat(values)
    loss = None
    if pos_weight is not None:
        loss = float(torch.nn.functional.binary_cross_entropy_with_logits(raw, labels[rows], pos_weight=pos_weight))
    return raw.cpu().numpy().astype(float), loss


def fit(arm, seed, job):
    folder = folder_for(arm, seed, job)
    folder.mkdir(parents=True, exist_ok=True)
    identity = run_identity(arm, seed, job)
    done = folder / 'PHASE1_FIT_COMPLETE.json'
    if done.exists():
        d = read(done)
        assert d['fit_identity'] == identity
        assert sha(folder / 'PHASE1_PREDICTIONS.json') == d['predictions_sha256']
        assert sha(folder / 'PHASE1_BEST_MODEL.pt') == d['selected_model_sha256']
        return d
    c = config()
    assert read(EVIDENCE / 'PHASE1_FULL_CNN_GATE.json')['full_matrix_allowed']
    rows = read(EVIDENCE / 'PHASE1_INPUT_IDENTITY_MANIFEST.json')
    y = np.array([r['failure'] for r in rows], dtype=np.float32)
    train, valid = np.array(job['training']), np.array(job['validation'])
    features = torch.from_numpy(np.load(STUDY / 'shared_cache/original_features_16.npy', allow_pickle=False)).cuda()
    labels = torch.from_numpy(y).cuda()
    pos_weight = torch.tensor(float((len(train) - y[train].sum()) / y[train].sum()), device='cuda')
    random.seed(seed)
    np.random.seed(seed)
    model = make_model(arm, train, seed)
    optimizer, scheduler = None, None
    optimizer = make_optimizer(model)
    scheduler = make_scheduler(optimizer)
    recovery = EpochRecovery(folder, identity)
    state = recovery.load()
    history, best, short_best, completed, training_seconds = [], None, None, 0, 0.0
    best_ap_seen, ap_progress_epoch = -float('inf'), 0
    if state:
        restore_selections(folder, state)
        model.load_state_dict(state['model'])
        optimizer.load_state_dict(state['optimizer'])
        scheduler.load_state_dict(state['scheduler'])
        history, best, short_best = state['history'], state['best'], state['short_best']
        completed, training_seconds = state['completed_epoch'], state['training_seconds']
        best_ap_seen, ap_progress_epoch = state['best_ap_seen'], state['ap_progress_epoch']
        restore_rng(state['random'])
        write(folder / 'PHASE1_RESUMPTION.json', {'utc': utc(), 'completed_epoch': completed,
              'next_epoch': completed + 1, 'policy': 'Incomplete epoch rolled back; completed sample exposure never duplicated',
              'next_order_sha256': hashlib.sha256(epoch_order(train, seed, completed + 1).astype(np.int64).tobytes()).hexdigest()})
    def save_boundary(epoch):
        assert shutil.disk_usage(folder).free >= c['minimum_free_bytes']
        recovery.save({'model': model.state_dict(), 'optimizer': optimizer.state_dict(), 'scheduler': scheduler.state_dict(),
            'completed_epoch': epoch, 'history': history, 'best': best, 'short_best': short_best,
            'training_seconds': training_seconds, 'seed': seed,
            'best_ap_seen': best_ap_seen, 'ap_progress_epoch': ap_progress_epoch,
            'selected_payloads': selected_payloads(folder, best, short_best),
            'next_order_sha256': hashlib.sha256(epoch_order(train, seed, epoch+1).astype(np.int64).tobytes()).hexdigest(),
            'training_sample_ids': [rows[i]['sample_id'] for i in train], 'precision': 'float32', 'effective_batch_actions': 8})
    if state is None:
        save_boundary(0)
    train_loader = EpochLoader(train, folder, 'training') if model.full else None
    valid_loader = EpochLoader(valid, folder, 'validation') if model.full else None
    try:
        if completed < c['max_epochs'] and not (best and stop_after_epoch(completed, ap_progress_epoch)):
            for epoch in range(completed + 1, c['max_epochs'] + 1):
                def progress(count, total, updates):
                    write(EXEC / 'PHASE1_PROGRESS.json', {'utc': utc(), 'stage': 'CONTROLLED_TRAINING', 'arm': arm,
                        'seed': seed, 'outer_fold': job['outer_fold_original'], 'role': job['role'], 'epoch': epoch,
                        'actions_completed_in_incomplete_epoch': count, 'actions_in_epoch': total, 'updates': updates,
                        'completed_epoch': epoch-1, 'resumable_boundary': 'completed epoch', 'status': 'RUNNING'})
                    if foreign_gpu_processes():
                        raise InterruptedError('FOREIGN_GPU_WORKLOAD: rollback incomplete epoch and wait; never terminate other job')
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
                start = time.monotonic()
                with Monitor(.5) as monitor:
                    result = train_epoch(model, optimizer, epoch_order(train, seed, epoch), labels, features,
                                         train_loader, pos_weight, inspect=(epoch == 1), progress=progress)
                    torch.cuda.synchronize()
                    duration = time.monotonic() - start
                training_seconds += duration
                validation_start = time.monotonic()
                raw, val_loss = predict(model, valid, labels, features, valid_loader, pos_weight=pos_weight)
                validation_seconds = time.monotonic()-validation_start
                ap = float(average_precision_score(y[valid], raw))
                entry = {'epoch': epoch, 'validation_AP': ap, 'validation_loss': val_loss,
                    'validation_AUROC': float(roc_auc_score(y[valid], raw)),
                    'training_loss': result['training_loss'], 'training_actions': result['actions'],
                    'optimizer_updates': result['optimizer_updates'], 'learning_rates': [g['lr'] for g in optimizer.param_groups],
                    'training_seconds': duration, 'actions_per_second': len(train)/duration,
                    'validation_seconds': validation_seconds, 'host_resources': host_resources(),
                    'GPU_compute_percent': float(np.mean([r['gpu_compute_percent'] for r in monitor.rows])) if monitor.rows else None,
                    'peak_allocated_bytes': torch.cuda.max_memory_allocated(), 'order_sha256': result['order_sha256'],
                    'CPU_loading_wait_seconds': result['loading_wait_seconds'],
                    'forward_backward_cuda_event_seconds': result['forward_backward_cuda_event_seconds']}
                if result['gradient_evidence']:
                    write(folder / 'PHASE1_FIRST_EPOCH_GRADIENT_UPDATES.json', result['gradient_evidence'])
                if better(entry, best):
                    best = entry.copy()
                    atomic_torch_save(folder / 'PHASE1_BEST_MODEL.pt', {'model': snapshot(model), 'fit_identity': identity,
                                      'selected_epoch': epoch, 'validation': best, 'arm': arm, 'seed': seed})
                if ap > best_ap_seen:
                    best_ap_seen, ap_progress_epoch = ap, epoch
                if arm == 'B_long_frozen16' and epoch in (5, 10) and better(entry, short_best):
                    short_best = entry.copy()
                    atomic_torch_save(folder / 'PHASE1_MATCHED_SHORT_MODEL.pt', {'model': snapshot(model), 'fit_identity': identity,
                                      'selected_epoch': epoch, 'validation': short_best, 'arm': 'A_r_matched_short', 'seed': seed})
                history.append(entry)
                scheduler.step()
                save_boundary(epoch)
                write(folder / 'PHASE1_LEARNING_CURVE.json', history)
                write(folder / f'PHASE1_GPU_TELEMETRY_EPOCH_{epoch:02d}.json', monitor.rows)
                write(folder / f'PHASE1_TOTAL_TIMING_EPOCH_{epoch:02d}.json',
                      {'training_seconds': duration, 'validation_seconds': validation_seconds,
                       'epoch_wall_seconds_including_checkpoint': time.monotonic()-start})
                print(utc(), arm, seed, job['fold_name'], job['role'], 'epoch', epoch, 'validation_AP', ap, flush=True)
                if (ROOT / 'STOP_AFTER_EPOCH.json').exists():
                    raise InterruptedError('REQUESTED_STOP_AFTER_COMPLETED_EPOCH')
                if stop_after_epoch(epoch, ap_progress_epoch):
                    break
    finally:
        if train_loader is not None:
            train_loader.close()
        if valid_loader is not None:
            valid_loader.close()
    selected = torch.load(folder / 'PHASE1_BEST_MODEL.pt', weights_only=True, map_location='cpu')
    model.load_state_dict(selected['model'])
    targets = np.array(job['C'] + job['predict'], dtype=int)
    prediction_start = time.monotonic()
    loader = EpochLoader(targets, folder, 'calibration_and_prediction') if model.full else None
    try:
        logits, _ = predict(model, targets, labels, features, loader)
    finally:
        if loader is not None:
            loader.close()
    ncal = len(job['C'])
    cal = calibrate(logits[:ncal], y[job['C']])
    probabilities = calibrated(logits[ncal:], cal)
    predictions = [dict(rows[row], raw_visual_logit=float(logit), p_visual=float(p), fit_identity=identity)
                   for row, logit, p in zip(job['predict'], logits[ncal:], probabilities)]
    # Keep predictions compact and directly keyed; never copy video/raw arrays.
    allowed = ['sample_id', 'recording_id', 'segment_id', 'failure', 'action', 'raw_visual_logit', 'p_visual', 'fit_identity']
    predictions = [{k: r[k] for k in allowed} for r in predictions]
    write(folder / 'PHASE1_PREDICTIONS.json', predictions)
    write(folder / 'PHASE1_CALIBRATOR.json', {'calibrator': cal, 'C_sample_ids': [rows[i]['sample_id'] for i in job['C']],
          'raw_calibration_logits': logits[:ncal].tolist(), 'T': train.tolist(), 'V': valid.tolist()})
    if arm == 'B_long_frozen16':
        short = torch.load(folder / 'PHASE1_MATCHED_SHORT_MODEL.pt', weights_only=True, map_location='cpu')
        model.load_state_dict(short['model'])
        short_logits, _ = predict(model, targets, labels, features)
        short_cal = calibrate(short_logits[:ncal], y[job['C']])
        short_p = calibrated(short_logits[ncal:], short_cal)
        write(folder / 'PHASE1_MATCHED_SHORT_PREDICTIONS.json', [dict(p, raw_visual_logit=float(l), p_visual=float(s))
            for p, l, s in zip(predictions, short_logits[ncal:], short_p)])
        write(folder / 'PHASE1_MATCHED_SHORT_CALIBRATOR.json', {'calibrator': short_cal, 'selected_epoch': short['selected_epoch']})
    info = {'fit_identity': identity, 'arm': arm, 'seed': seed, 'job_index': job['job_index'], 'best': best,
        'short_best': short_best, 'executed_epochs': len(history), 'training_seconds': training_seconds,
        'inference_calibration_seconds': time.monotonic()-prediction_start, 'history': history,
        'predictions_sha256': sha(folder / 'PHASE1_PREDICTIONS.json'), 'selected_model_sha256': sha(folder / 'PHASE1_BEST_MODEL.pt'),
        'short_predictions_sha256': sha(folder/'PHASE1_MATCHED_SHORT_PREDICTIONS.json') if arm == 'B_long_frozen16' else None,
        'T_sample_ids': [rows[i]['sample_id'] for i in train], 'V_sample_ids': [rows[i]['sample_id'] for i in valid],
        'C_sample_ids': [rows[i]['sample_id'] for i in job['C']], 'prediction_sample_ids': [rows[i]['sample_id'] for i in job['predict']],
        'completed_utc': utc()}
    write(done, info)
    del model, optimizer, scheduler, features, labels
    gc.collect()
    torch.cuda.empty_cache()
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arm', required=True, choices=config()['arms'])
    parser.add_argument('--seed', required=True, type=int, choices=config()['seeds'])
    parser.add_argument('--job', required=True, type=int)
    args = parser.parse_args()
    jobs = read(EVIDENCE / 'PHASE1_FIT_PLAN.json')
    assert not foreign_gpu_processes(), 'GPU_BUSY: do not launch competing work'
    fit(args.arm, args.seed, jobs[args.job])


if __name__ == '__main__':
    main()
