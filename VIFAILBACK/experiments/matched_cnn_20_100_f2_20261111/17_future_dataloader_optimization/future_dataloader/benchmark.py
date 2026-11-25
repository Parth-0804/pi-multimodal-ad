"""Manual future loader benchmark; no automatic scheduling or live-job changes.

Only this module's explicitly called run_benchmark can allocate CUDA, and only
inside guards.benchmark_lease after completion of all 37 protected CNN fits.
Numerical proof runs separately from performance timing. No model checkpoint is
written and no performance result changes an existing fit or controller.
"""
from __future__ import annotations

from datetime import datetime, timezone
import gc
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import sys
import time

from .guards import (AdmissionBlocked, LOCAL_ROOT, STUDY, assert_no_other_gpu_processes,
                     benchmark_lease)


def _sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def _write_new(path, value):
    """Every receipt is new; repeated invocations require a new output directory."""
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def _tree_digest(value):
    """Exact tensor/state identity, without sampling or RNG consumption."""
    import numpy as np
    import torch
    digest = hashlib.sha256()

    def visit(node):
        if torch.is_tensor(node):
            array = node.detach().cpu().contiguous().numpy()
            digest.update(f'TENSOR:{array.dtype}:{array.shape}:'.encode())
            digest.update(memoryview(array).cast('B'))
        elif isinstance(node, np.ndarray):
            array = np.ascontiguousarray(node)
            digest.update(f'ARRAY:{array.dtype}:{array.shape}:'.encode())
            digest.update(memoryview(array).cast('B'))
        elif isinstance(node, dict):
            digest.update(b'DICT:')
            for key in sorted(node, key=lambda k: (type(k).__name__, repr(k))):
                visit(key)
                visit(node[key])
        elif isinstance(node, (tuple, list)):
            digest.update(f'{type(node).__name__}:{len(node)}:'.encode())
            for item in node:
                visit(item)
        elif node is None or isinstance(node, (str, int, float, bool)):
            digest.update(f'{type(node).__name__}:{repr(node)};'.encode())
        else:
            raise TypeError(f'Unsupported exact-state digest type: {type(node).__name__}')

    visit(value)
    return digest.hexdigest()


def _original_bank(ctx):
    """Read only the existing original feature bank; retain no frame cache."""
    import numpy as np
    from matched_vifailback.common import PROJECT, read_json
    from matched_vifailback.data import pool_bank
    root = PROJECT / '03_preprocessing/visual_preprocessing/features' / ctx['config']['run_id'] / 'V1'
    receipt = read_json(root / 'COMPLETE.json')
    path = root / 'features.npy'
    if _sha(path) != receipt['sha256']:
        raise ValueError('Original T-moment feature-bank digest mismatch')
    values = np.load(path, mmap_mode='r', allow_pickle=False)
    if values.shape[0] != len(ctx['index']):
        raise ValueError('Original feature bank row identity mismatch')
    return pool_bank(values), {'sha256': receipt['sha256'], 'bytes': path.stat().st_size,
                               'receipt_sha256': _sha(root / 'COMPLETE.json')}


def _host_memory():
    import psutil
    process = psutil.Process()
    children = process.children(recursive=True)
    child_rss = 0
    for child in children:
        try:
            child_rss += child.memory_info().rss
        except psutil.NoSuchProcess:
            pass
    return {'main_RSS_bytes': process.memory_info().rss,
            'children_RSS_sum_bytes': child_rss,
            'children_RSS_note': 'sum includes potentially shared mappings; not unique resident memory',
            'host_RAM_available_bytes': psutil.virtual_memory().available,
            'child_process_count': len(children)}


def _pass(ctx, ids, config_name, settings, mean, std, positive_weight, *, numerical,
          warmup_episodes, seed=42):
    """One independent model at a time, unchanged optimizer and minibatch math."""
    import numpy as np
    import torch
    from matched_vifailback.model_runtime import make_model, full_batch_backward, global_clip, optimizer_for
    from matched_vifailback.training import episode_loader, scheduler_for, Telemetry
    from vifailback.training import rng_state
    from .loader import build_loader

    assert_no_other_gpu_processes()
    random.seed(seed)
    np.random.seed(seed)
    model = make_model(mean, std, seed, full=True, device='cuda')
    model.train()
    optimizer = optimizer_for(model)
    # This is a prefix of future FULL20 epoch 1: cosine horizon stays 50. No
    # scheduler step is due during the prefix. A separate state digest proves
    # original scheduler initialization and the first boundary transition.
    scheduler = scheduler_for(optimizer, 50)
    initial = _tree_digest({'model': model.state_dict(), 'optimizer': optimizer.state_dict(),
                            'scheduler': scheduler.state_dict(), 'rng': rng_state()})
    loader = episode_loader(ctx, ids) if config_name == '__reference__' else build_loader(ctx, ids, settings)
    iterator = None
    examples = []
    rows = []
    measured_started = None
    warmup_seconds = None
    start = time.perf_counter()
    iterator_started = time.perf_counter()
    iterator = iter(loader)
    iterator_seconds = time.perf_counter() - iterator_started
    torch.cuda.reset_peak_memory_stats()
    try:
        with Telemetry(not numerical) as telemetry:
            for offset in range(0, len(ids), 8):
                batch_ids = ids[offset:offset + 8]
                check_started = time.perf_counter()
                assert_no_other_gpu_processes()
                guard_seconds = time.perf_counter() - check_started
                # Synchronization ensures every measured loader wait is a
                # quiescent-GPU host wait, not asynchronous outstanding compute.
                torch.cuda.synchronize()
                if offset == warmup_episodes:
                    warmup_seconds = time.perf_counter() - start
                    measured_started = time.perf_counter()
                loading_started = time.perf_counter()
                examples = []
                identities = []
                for expected in batch_ids:
                    eid, pixels = next(iterator)
                    if int(eid) != int(expected):
                        raise ValueError('Future loader episode-order drift')
                    if tuple(pixels.shape) != (3, 16, 3, 640, 640) or pixels.dtype != torch.float32:
                        raise ValueError('Future loader tensor contract drift')
                    if not pixels.is_pinned():
                        raise ValueError('Future GPU benchmark requires actually pinned episode tensors')
                    examples.append(pixels)
                    if numerical:
                        identities.append({'episode_index': int(eid),
                                           'tensor_sha256': _tree_digest(pixels),
                                           'is_pinned': bool(pixels.is_pinned()),
                                           'label': int(ctx['lookup'][int(eid)]['label'])})
                loading_seconds = time.perf_counter() - loading_started
                labels = torch.tensor([ctx['lookup'][int(e)]['label'] for e in batch_ids], dtype=torch.float32)
                event_start, event_end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                compute_started = time.perf_counter()
                event_start.record()
                optimizer.zero_grad(set_to_none=True)
                loss, logits = full_batch_backward(model, examples, labels, positive_weight)
                gradient_digest = _tree_digest({n: p.grad for n, p in model.named_parameters()}) if numerical else None
                norm = global_clip(model, 1.)
                optimizer.step()
                event_end.record()
                torch.cuda.synchronize()
                compute_seconds = time.perf_counter() - compute_started
                row = {'offset': offset, 'episodes': len(batch_ids),
                       'warmup': offset < warmup_episodes,
                       'loader_wait_GPU_quiescent_seconds': loading_seconds,
                       'compute_wall_seconds': compute_seconds,
                       'GPU_stream_elapsed_ms': event_start.elapsed_time(event_end),
                       'guard_overhead_seconds': guard_seconds}
                if numerical:
                    row['proof'] = {'inputs': identities,
                                    'labels_sha256': _tree_digest(labels),
                                    'loss_sha256': _tree_digest(loss), 'logits_sha256': _tree_digest(logits),
                                    'unclipped_gradients_sha256': gradient_digest,
                                    'global_gradient_norm': norm,
                                    'model_sha256': _tree_digest(model.state_dict()),
                                    'optimizer_sha256': _tree_digest(optimizer.state_dict()),
                                    'scheduler_sha256': _tree_digest(scheduler.state_dict()),
                                    'RNG_sha256': _tree_digest(rng_state())}
                rows.append(row)
                # Do not retain an eight-episode frame batch between passes.
                del examples[:]
                del pixels, labels, loss, logits
            torch.cuda.synchronize()
            measured_seconds = time.perf_counter() - measured_started
            try:
                next(iterator)
                raise ValueError('Unexpected additional episode from future loader')
            except StopIteration:
                pass
        full_seconds = time.perf_counter() - start
        measured = [row for row in rows if not row['warmup']]
        final_state = _tree_digest({'model': model.state_dict(), 'optimizer': optimizer.state_dict(),
                                   'scheduler': scheduler.state_dict(), 'rng': rng_state()})
        # A boundary-equivalence probe is separate from timing and is not a
        # claimed full epoch: the actual benchmark only executes an epoch prefix.
        scheduler.step()
        boundary_scheduler_digest = _tree_digest(scheduler.state_dict())
        result = {'config': config_name, 'numerical_proof_pass': numerical,
                  'initial_state_sha256': initial, 'final_state_sha256': final_state,
                  'scheduler_boundary_probe_sha256': boundary_scheduler_digest,
                  'iterator_start_seconds': iterator_seconds,
                  'warmup_seconds_including_worker_start': warmup_seconds,
                  'measurement_seconds': measured_seconds,
                  'all_loader_compute_seconds_including_warmup': full_seconds,
                  'measured_episodes': len(ids) - warmup_episodes,
                  'episodes_per_second': (len(ids) - warmup_episodes) / measured_seconds,
                  'loader_wait_GPU_quiescent_seconds': sum(r['loader_wait_GPU_quiescent_seconds'] for r in measured),
                  'compute_wall_seconds': sum(r['compute_wall_seconds'] for r in measured),
                  'GPU_stream_elapsed_ms': sum(r['GPU_stream_elapsed_ms'] for r in measured),
                  'guard_overhead_seconds_inside_measurement': sum(r['guard_overhead_seconds'] for r in measured[1:]),
                  'wait_scope': 'Guarded benchmark: between-batch nvidia-smi checks give prefetch a small head start; not an uninstrumented production waiting estimate',
                  'GPU_stream_elapsed_note': 'CUDA event span on the stream includes CPU dispatch gaps; it is not kernel-busy time',
                  'kernel_busy_samples': telemetry.rows,
                  'kernel_busy_source': 'existing noninvasive nvidia-smi utilization.gpu samples every 2 s' if not numerical else 'not sampled during numerical pass',
                  'peak_GPU_allocated_bytes': torch.cuda.max_memory_allocated(),
                  'peak_GPU_reserved_bytes': torch.cuda.max_memory_reserved(),
                  'host_memory_after_pass': _host_memory(), 'batches': rows}
        result['host_memory_sampling_scope'] = 'After-pass point snapshot; worker/pinned-memory resident peaks are not measured. Conservative admission envelopes apply.'
        return result
    finally:
        if iterator is not None and hasattr(iterator, '_shutdown_workers'):
            iterator._shutdown_workers()
        examples.clear()
        del iterator, loader, model, optimizer, scheduler
        gc.collect()
        torch.cuda.empty_cache()


def _same_proof(reference, candidate):
    return (reference['initial_state_sha256'] == candidate['initial_state_sha256']
            and reference['final_state_sha256'] == candidate['final_state_sha256']
            and reference['scheduler_boundary_probe_sha256'] == candidate['scheduler_boundary_probe_sha256']
            and [r['proof'] for r in reference['batches']] == [r['proof'] for r in candidate['batches']])


def compare_throughput(rounds, config_names, baseline='baseline_w2_p1'):
    """Prospective conservative repeated-improvement rule; no metric selection."""
    comparisons = {}
    qualifying = []
    for name in config_names:
        if name == baseline:
            continue
        gains = [round_[name]['episodes_per_second'] / round_[baseline]['episodes_per_second'] - 1
                 for round_ in rounds]
        median = statistics.median(gains)
        qualified = len(gains) >= 3 and all(gain >= .05 for gain in gains)
        comparisons[name] = {'relative_throughput_changes': gains, 'median_relative_change': median,
                             'all_repeated_runs_at_least_5_percent_faster': qualified}
        if qualified:
            qualifying.append((median, name))
    selected = max(qualifying)[1] if qualifying else None
    return {'status': 'MEASURED_CANDIDATE' if selected else 'NO_RECOMMENDATION',
            'config': selected, 'comparisons': comparisons,
            'rule': 'At least 3 balanced repeated measurements; every paired measured-throughput gain >=5%; all numerical checks must pass separately',
            'scope': 'Controlled fixed T-only episode prefix on this host; not a measured whole-epoch or end-to-end fit speedup',
            'does_not_activate_or_modify_any_fit': True}


def run_benchmark(output_dir, config_names, options=None):
    """Prepare a unique receipt; execute only under the future exclusive lease.

    options: cpu_validation (required path), rounds=4, episodes=32 measured,
    warmup_episodes=8. All passes use exactly the same seed42 epoch1 T prefix.
    The original training.episode_loader is an independent numerical reference.
    No datasets, checkpoints, source files, controllers or queues are changed.
    """
    from .settings import PRESETS
    options = dict(options or {})
    names = list(dict.fromkeys(config_names))
    # Find the named baseline from its immutable actual settings rather than
    # depending on an undocumented candidate name.
    baseline_matches = [name for name, value in PRESETS.items()
                        if value.num_workers == 2 and value.prefetch_factor == 1]
    if len(baseline_matches) != 1:
        raise ValueError('Exactly one original 2-worker/prefetch1 baseline is required')
    baseline = baseline_matches[0]
    if baseline not in names or len(names) < 2 or any(name not in PRESETS for name in names):
        raise ValueError('Benchmark must include the original baseline and at least one declared candidate')
    rounds = int(options.get('rounds', 4))
    episodes = int(options.get('episodes', 32))
    warmup = int(options.get('warmup_episodes', 8))
    if not 3 <= rounds <= 8 or rounds % len(names) or not 16 <= episodes <= 128 or episodes % 8 or warmup != 8:
        raise ValueError('Bounded benchmark requires 3–8 rounds divisible by number of configs, 16–128 measured episodes divisible by8, exactly8 warmup episodes')
    output = Path(output_dir).resolve()
    if LOCAL_ROOT.resolve() not in output.parents:
        raise ValueError('Benchmark output must be a new directory inside the isolated optimization folder')
    output.mkdir(parents=True, exist_ok=False)
    result = {'schema': 1, 'utc': datetime.now(timezone.utc).isoformat(), 'status': 'PENDING',
              'numerical_equivalence_pass': False,
              'recommendation': {'status': 'NO_RECOMMENDATION', 'config': None},
              'configurations': {name: PRESETS[name].as_dict() for name in names},
              'options': {'rounds': rounds, 'measured_episodes': episodes, 'warmup_episodes': warmup},
              'no_existing_fit_changes': True, 'no_checkpoint_writes': True,
              'GPU_measurement_performed': False, 'GPU_work_attempted': False,
              'GPU_numerical_reference_completed': False}
    result['environment'] = {key: os.environ.get(key) for key in (
        'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
        'NUMEXPR_NUM_THREADS', 'TOKENIZERS_PARALLELISM', 'CUDA_VISIBLE_DEVICES')}
    result['CPU_affinity'] = sorted(os.sched_getaffinity(0))
    try:
        with benchmark_lease(configurations=[PRESETS[name] for name in names]) as admitted:
            result['admission'] = admitted
            # These modules import torch only after all protected work is done.
            # A failed admission has already exited before this point.
            from .contracts import load_contract_context, epoch_ids, check_cpu_receipt
            from matched_vifailback.controller import check_frozen_code
            import numpy as np
            import torch
            from vifailback.reference import primitives
            check_frozen_code()
            ctx = load_contract_context()
            if not options.get('cpu_validation'):
                raise ValueError('An explicit current CPU-contract PASS receipt is required')
            cpu_path = Path(options['cpu_validation']).resolve()
            if LOCAL_ROOT.resolve() not in cpu_path.parents:
                raise ValueError('CPU contract receipt must belong to the isolated optimization folder')
            check_cpu_receipt(cpu_path, ctx, names)
            result['CPU_contract_receipt_sha256'] = _sha(cpu_path)
            result['CPU_contract_receipt'] = os.path.relpath(cpu_path, STUDY)
            result['isolated_source_sha256'] = {str(path.relative_to(LOCAL_ROOT)): _sha(path)
                                                for path in sorted(LOCAL_ROOT.rglob('*.py'))}
            bank, bank_identity = _original_bank(ctx)
            result['original_feature_bank'] = bank_identity
            all_ids = epoch_ids(ctx, seed=42, epoch_index=0, job_id='outer0_inner0')
            ids = [int(e) for e in all_ids[:warmup + episodes]]
            job = ctx['jobs']['outer0_inner0']
            if not set(ids) <= set(job['ids']['T']):
                raise ValueError('Benchmark may inspect only gradient-training T episodes')
            result['selected_episode_ids'] = ids
            result['seed'] = 42
            result['job_id'] = 'outer0_inner0'
            result['role'] = 'T'
            mean, std = primitives()['standardizer'](bank[[ctx['index'][int(e)] for e in job['ids']['T']]])
            labels = np.asarray([ctx['lookup'][int(e)]['label'] for e in job['ids']['T']], dtype=int)
            weight = torch.tensor((len(labels) - labels.sum()) / labels.sum(), dtype=torch.float32)
            result['T_standardization_sha256'] = _tree_digest((mean, std))
            result['T_positive_weight'] = float(weight)
            result['GPU_work_attempted'] = True
            proofs = {}
            reference = _pass(ctx, ids, '__reference__', None, mean, std, weight,
                              numerical=True, warmup_episodes=warmup)
            result['GPU_numerical_reference_completed'] = True
            expected_state_hashes = {key: reference[key] for key in (
                'initial_state_sha256', 'final_state_sha256', 'scheduler_boundary_probe_sha256')}
            _write_new(output / 'numerical_reference.json', reference)
            for name in names:
                candidate = _pass(ctx, ids, name, PRESETS[name], mean, std, weight,
                                  numerical=True, warmup_episodes=warmup)
                passed = _same_proof(reference, candidate)
                candidate['exact_reference_equivalence'] = passed
                _write_new(output / f'numerical_{name}.json', candidate)
                proofs[name] = passed
                if not passed:
                    raise ValueError(f'Exact numerical/data-contract equivalence failed for {name}; no timing recommendation is allowed')
            result['numerical_checks'] = proofs
            result['numerical_equivalence_pass'] = all(proofs.values())
            del reference, candidate
            measured = []
            result['round_orders'] = []
            # Balanced rotation changes which variant benefits from transient
            # conditions/page-cache warming; no page-cache eviction is used.
            for round_index in range(rounds):
                shift = round_index % len(names)
                order = names[shift:] + names[:shift]
                result['round_orders'].append(order)
                values = {}
                for name in order:
                    value = _pass(ctx, ids, name, PRESETS[name], mean, std, weight,
                                  numerical=False, warmup_episodes=warmup)
                    result['GPU_measurement_performed'] = True
                    if any(value[key] != digest for key, digest in expected_state_hashes.items()):
                        raise ValueError('Timed execution changed model/optimizer/scheduler/RNG state relative to the exact numerical reference')
                    _write_new(output / f'timing_round{round_index + 1}_{name}.json', value)
                    values[name] = value
                measured.append(values)
            result['recommendation'] = compare_throughput(measured, names, baseline)
            result['status'] = 'COMPLETE'
            result['baseline'] = baseline
            result['timing_notes'] = [
                'Numerical hashing runs are separate and excluded from timing comparisons.',
                'Each timed pass starts from identical pretrained weights, fresh optimizer and seed42 RNG; one model exists at a time.',
                '8 warmup and 32(default) measured T episodes are a bounded epoch1 prefix, not a full-epoch benchmark.',
                'Measured wait is host next(loader) time after CUDA synchronization; transfer/CPU-head gaps remain inside compute wall time.',
                'CUDA event spans are stream elapsed time, not GPU kernel-busy utilization.',
                'Existing nvidia-smi telemetry samples device kernel utilization separately.',
                'Video/page caches are not deleted; OS cache warmth may remain a confound despite paired rotations.',
                'No validation inference benchmark was run and no validation speedup is inferred.']
    except AdmissionBlocked as exc:
        result['admission'] = exc.snapshot
        result['pending_reason'] = 'Protected queue/resources/locks are not available; no CUDA work was started'
    except Exception as exc:
        result['status'] = 'FAILED'
        result['error'] = f'{type(exc).__name__}: {exc}'
        result['recommendation'] = {'status': 'NO_RECOMMENDATION', 'config': None}
    result['case_receipts_sha256'] = {path.name: _sha(path) for path in sorted(output.glob('*.json'))}
    result['finished_utc'] = datetime.now(timezone.utc).isoformat()
    _write_new(output / 'GPU_BENCHMARK.json', result)
    return result
