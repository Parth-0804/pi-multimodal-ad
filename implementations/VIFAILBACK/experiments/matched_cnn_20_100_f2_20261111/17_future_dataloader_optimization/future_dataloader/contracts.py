"""Metadata-only context and bounded, CPU-only real-frame contract validation.

No feature bank, model, optimizer, checkpoint, cache or active configuration is
written or loaded here. Real-frame validation must run in a separate process
with CUDA hidden before importing PyTorch. The original frozen loader is the
reference, not a reimplementation of its image processing.
"""
from __future__ import annotations

from collections import Counter
import csv
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import time


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def load_contract_context():
    """Validate original metadata/source hashes without touching feature banks.

    This context is also usable by an independently admitted future benchmark.
    Native annotations and every role are checked, but episode selection and
    loader validation use only the fixed proper-training T role.
    """
    from matched_vifailback.common import PROJECT, STUDY, legacy_config, protocol, read_json, relative, resolve, sha256
    from matched_vifailback.data import (CAMERAS, manifest_identity, verify_native_labels,
                                        verify_rows, verify_splits)

    frozen = protocol()
    config = legacy_config()
    manifest = PROJECT / '03_preprocessing/processed_manifests' / config['run_id'] / 'eligible.json'
    splits = PROJECT / '04_evaluation_splits/train_validation_test' / config['run_id'] / 'fit_partitions.json'
    _require(sha256(manifest) == frozen['cohort_sha256'], 'Frozen cohort SHA mismatch')
    _require(sha256(splits) == frozen['splits_sha256'], 'Frozen split SHA mismatch')
    source_manifest = read_json(STUDY / '01_protocol_and_source_evidence/AUTHORITATIVE_SOURCE_MANIFEST.json')
    checked_sources = {}
    for entry in source_manifest['entries']:
        path = entry['path']
        if path.startswith('VIFAILBACK/src/') or path.startswith('VIFAILBACK/configs/'):
            actual = sha256(resolve(path))
            _require(actual == entry['sha256'], 'Original loader dependency changed: ' + path)
            checked_sources[path] = actual
    _require(config == read_json(PROJECT / 'configs/experiment.json'), 'Legacy configuration snapshot drift')
    freeze = read_json(STUDY / '13_reproducibility/IMPLEMENTATION_FREEZE.json')
    for path, expected in freeze['implementation'].items():
        actual = sha256(resolve(path))
        _require(actual == expected, 'Frozen study implementation changed: ' + path)
        checked_sources[path] = actual
    _require(tuple(config['cameras']) == CAMERAS and config['frames_per_camera'] == 16,
             'Original camera/frame contract drift')
    targets, native_evidence = verify_native_labels(config)
    rows = read_json(manifest)
    cohort = verify_rows(rows, targets, frozen['cohort_expected'])
    jobs_list = read_json(splits)
    roles = verify_splits(jobs_list, rows)
    excluded_path = manifest.parent / 'exclusions.csv'
    exclusions = list(csv.DictReader(excluded_path.open(newline='')))
    excluded_ids = {int(row['episode_index']) for row in exclusions}
    eligible_ids = {int(row['episode_index']) for row in rows}
    _require(len(exclusions) == len(excluded_ids) == 820 and not excluded_ids & eligible_ids,
             'Exclusion identities changed')
    _require(excluded_ids | eligible_ids == set(targets), 'Native cohort partition incomplete')
    _require(sha256(excluded_path) == read_json(manifest.parent / 'COMPLETE.json')['exclusions_sha256'],
             'Exclusions source SHA mismatch')
    return {
        'config': config, 'rows': rows,
        'lookup': {int(row['episode_index']): row for row in rows},
        'index': {int(row['episode_index']): index for index, row in enumerate(rows)},
        'jobs': {job['id']: job for job in jobs_list},
        'verification': {
            'cohort_source': manifest_identity(manifest), 'split_source': manifest_identity(splits),
            'legacy_config_source': manifest_identity(STUDY / '01_protocol_and_source_evidence/legacy_config_snapshot.json'),
            'cohort': cohort, 'roles': roles, 'native_labels': native_evidence,
            'checked_source_sha256': checked_sources,
            'feature_banks_opened': False, 'selection_role': 'outer0_inner0/T',
        },
    }


def epoch_ids(ctx, seed=42, epoch_index=0, job_id='outer0_inner0'):
    """Exact frozen zero-based epoch ordering; no global NumPy RNG draw."""
    import numpy as np
    _require(type(epoch_index) is int and epoch_index >= 0, 'epoch_index must be nonnegative integer')
    ids = ctx['jobs'][job_id]['ids']['T']
    return np.asarray(ids)[np.random.default_rng(int(seed) + epoch_index * 100003).permutation(len(ids))].tolist()


def select_contract_ids(ctx, count=4, job_id='outer0_inner0'):
    """Label-blind frame-count quantiles from proper T, including both extremes."""
    import numpy as np
    _require(type(count) is int and 1 <= count <= 4, 'Live preparation is bounded to at most four episodes')
    values = sorted(ctx['jobs'][job_id]['ids']['T'], key=lambda eid: (ctx['lookup'][eid]['frame_count'], eid))
    _require(len(values) >= count, 'Not enough training episodes')
    return [int(values[i]) for i in np.linspace(0, len(values) - 1, count).round().astype(int)]


def validation_binding(ctx, config_names):
    """Bind receipts to the immutable data contract and this isolated code."""
    from matched_vifailback.common import PROTOCOL_SHA256, relative, sha256
    from .settings import PRESETS
    names = list(config_names)
    _require(names and len(names) == len(set(names)) and set(names) <= set(PRESETS), 'Unknown/repeated loader preset')
    root = Path(__file__).resolve().parent
    source_hashes = {relative(root / name): sha256(root / name)
                     for name in ('contracts.py', 'loader.py', 'settings.py')}
    evidence = ctx['verification']
    return {
        'protocol_sha256': PROTOCOL_SHA256,
        'cohort_sha256': evidence['cohort_source']['sha256'],
        'splits_sha256': evidence['split_source']['sha256'],
        'legacy_config_sha256': evidence['legacy_config_source']['sha256'],
        'original_source_sha256': evidence['checked_source_sha256'],
        'isolated_source_sha256': source_hashes,
        'configurations': {name: PRESETS[name].as_dict() for name in names},
    }


def check_cpu_receipt(path, ctx, config_names):
    """Authorize only the future benchmark's equivalence stage, never timing.

    A small CPU subset is deliberately not evidence for every future benchmark
    episode. The benchmark must verify all of its own pixels before timing.
    """
    from matched_vifailback.common import read_json, signature
    value = read_json(path)
    _require(value.get('schema') == 1 and value.get('status') == 'PASS', 'CPU contract receipt is not PASS')
    old = value['binding']
    _require(signature(old) == value.get('binding_sha256'), 'CPU receipt binding digest mismatch')
    expected = validation_binding(ctx, config_names)
    _require(all(old.get(key) == val for key, val in expected.items() if key != 'configurations'),
             'CPU receipt source/data binding drift')
    _require(all(old['configurations'].get(name) == config for name, config in expected['configurations'].items()),
             'Requested preset lacks matching CPU contract validation')
    _require(set(config_names) <= set(value['checked_config_names']), 'CPU receipt missing requested configurations')
    checked_ids = value['selected_episode_ids']
    _require(checked_ids and set(checked_ids) <= set(ctx['jobs']['outer0_inner0']['ids']['T']),
             'CPU receipt includes unknown/nontraining episode IDs')
    return value


def _timestamp_evidence(ctx, ids):
    """Verify actual QC PTS against freshly hashed unchanged video payloads.

    These timestamps came from the historical complete FFmpeg decode. Reading
    that evidence is not a new decode-time PTS measurement; matching current
    payload hashes establishes timestamp identity for the exact same media.
    """
    import numpy as np
    from matched_vifailback.common import PROJECT, read_json, relative, sha256
    from matched_vifailback.data import CAMERAS, VIDEO_KEYS, verify_frame_contract
    from vifailback.common import video_path

    root = PROJECT / '02_dataset_verification/video_audit/runs' / ctx['config']['run_id'] / 'per_camera'
    evidence = []
    for eid in ids:
        row = ctx['lookup'][eid]
        positions = verify_frame_contract(row)
        for camera_index, (camera, key) in enumerate(zip(CAMERAS, VIDEO_KEYS)):
            media = video_path(ctx['config'], row[key])
            qc_path = root / f'{eid:06d}_{camera}.json'
            qc = read_json(qc_path)
            _require(media.stat().st_size == row['camera_bytes'][camera_index], 'Video size changed')
            actual_hash = sha256(media)
            _require(actual_hash == row['camera_sha256'][camera_index] == qc['source_sha256'],
                     'Video SHA does not bind saved actual frame PTS')
            _require(qc['technical_valid'] and qc['episode_index'] == eid and qc['camera'] == camera,
                     'Historical QC identity/validity mismatch')
            _require(qc['source_path'] == row[key] and qc['decoded_frames'] == row['frame_count'],
                     'Historical QC path/frame count mismatch')
            _require(qc['selected_frame_indices'] == positions and
                     qc['selected_RGB_sha256'] == row['selected_RGB_sha256'][camera_index],
                     'Historical selected frame identity mismatch')
            pts = np.asarray(qc['frame_PTS_seconds'], dtype=np.float64)
            _require(len(pts) == row['frame_count'] and np.isfinite(pts).all() and (np.diff(pts) > 0).all(),
                     'Historical actual PTS invalid')
            selected = pts[positions]
            max_error = float(np.max(np.abs(selected - np.asarray(row['frame_times_seconds']))))
            _require(max_error <= 5e-5, 'Actual selected PTS differs from frozen nominal frame time')
            evidence.append({
                'episode_index': eid, 'camera': camera, 'camera_index': camera_index,
                'video_path': relative(media), 'video_sha256_checked_now': actual_hash,
                'historical_QC_path': relative(qc_path), 'historical_QC_sha256': sha256(qc_path),
                'selected_frame_indices': positions,
                'actual_selected_PTS_seconds_from_bound_historical_decode': selected.tolist(),
                'nominal_selected_times_seconds': row['frame_times_seconds'],
                'maximum_nominal_vs_actual_difference_seconds': max_error,
                'source_RGB_sha256': row['selected_RGB_sha256'][camera_index],
                'timestamp_scope': 'Historical complete-decode actual PTS, bound to freshly hashed unchanged media; no fresh PTS decode',
            })
    return evidence


def tensor_identity(tensor):
    """Hash every FP32 byte plus each ordered frame without copying an episode."""
    import torch
    _require(tuple(tensor.shape) == (3, 16, 3, 640, 640), 'Transformed tensor shape drift')
    _require(tensor.dtype == torch.float32 and tensor.device.type == 'cpu', 'Expected CPU float32 pixels')
    _require(tensor.is_contiguous(), 'Original contiguous tensor contract changed')
    array = tensor.detach().numpy()
    frame_hashes = []
    for camera in range(3):
        hashes = []
        for frame in range(16):
            _require(bool(torch.isfinite(tensor[camera, frame]).all()), 'Nonfinite transformed pixel')
            hashes.append(hashlib.sha256(memoryview(array[camera, frame]).cast('B')).hexdigest())
        frame_hashes.append(hashes)
    return {'shape': list(tensor.shape), 'dtype': str(tensor.dtype),
            'bytes': tensor.numel() * tensor.element_size(),
            'sha256_all_tensor_bytes': hashlib.sha256(memoryview(array).cast('B')).hexdigest(),
            'ordered_camera_frame_sha256': frame_hashes,
            'all_finite': True, 'is_pinned': bool(tensor.is_pinned())}


def _collect(loader, ctx, ids):
    import torch
    state = torch.get_rng_state().clone()
    observed = []
    identities = {}
    for eid, pixels in loader:
        eid = int(eid)
        _require(eid not in identities, 'Duplicate emitted episode')
        observed.append(eid)
        identities[str(eid)] = dict(tensor_identity(pixels), label=int(ctx['lookup'][eid]['label']))
        del pixels
    _require(observed == list(ids), 'Delivered episode order changed')
    _require(torch.equal(state, torch.get_rng_state()), 'Loader consumed the main-process torch RNG')
    return {'delivered_episode_ids': observed, 'identities': identities, 'main_process_torch_rng_unchanged': True}


def _sampler_evidence(ctx, names):
    """Check complete T orders/batch boundaries without decoding large cohorts."""
    import numpy as np
    from matched_vifailback.common import signature
    from .loader import build_loader
    from .settings import PRESETS
    evidence = []
    original = ctx['jobs']['outer0_inner0']['ids']['T']
    for seed in (42, 123, 20261023):
        for epoch_index in (0, 1, 19, 99):
            ids = epoch_ids(ctx, seed, epoch_index)
            reference = np.asarray(original)[np.random.default_rng(seed + epoch_index * 100003).permutation(len(original))].tolist()
            _require(ids == reference and Counter(ids) == Counter(original), 'Training epoch order drift')
            batches = [ids[start:start + 8] for start in range(0, len(ids), 8)]
            _require(len(batches[-1]) == len(ids) % 8 and len(batches[-1]) == 6, 'Partial final minibatch drift')
            for name in names:
                loader = build_loader(ctx, ids, PRESETS[name])
                supplied = [loader.dataset.rows[index]['episode_index'] for index in loader.sampler]
                _require(supplied == reference and loader.batch_size is None and not loader.drop_last,
                         'Future loader order/drop-last contract drift')
                _require([ctx['lookup'][eid]['label'] for eid in supplied] ==
                         [ctx['lookup'][eid]['label'] for eid in reference], 'ID/label association drift')
            evidence.append({'seed': seed, 'epoch_index_zero_based': epoch_index,
                             'epoch_number_one_based': epoch_index + 1,
                             'ordered_T_ids_sha256': signature(ids),
                             'ordered_T_labels_sha256': signature([ctx['lookup'][eid]['label'] for eid in ids]),
                             'episodes': len(ids), 'optimizer_minibatches_at_size8': len(batches),
                             'final_partial_batch_size': len(batches[-1]),
                             'first_eight_episode_batches': batches[:8],
                             'final_partial_batch_ids': batches[-1]})
    return evidence


def validate_cpu(output_dir, selected_config_names, *, episode_ids=None):
    """Validate up to four real T episodes against the frozen loader on CPU.

    Optional episode_ids may extend this only for a separately scheduled future
    CPU check; callers are responsible for admitting that extra workload.
    Neither durations nor CPU loader timings are claims about GPU throughput.
    """
    _require(os.environ.get('CUDA_VISIBLE_DEVICES') == '', 'Hide CUDA before starting CPU contract process')
    import torch
    _require(not torch.cuda.is_initialized() and not torch.cuda.is_available(), 'CPU validation must not access CUDA')
    torch.set_num_threads(1)
    from matched_vifailback.common import relative, signature, utc
    from matched_vifailback.training import episode_loader
    from .loader import build_loader
    from .settings import PRESETS
    out = Path(output_dir).resolve()
    allowed = Path(__file__).resolve().parents[1]
    _require(out.is_relative_to(allowed) and out != allowed, 'CPU evidence must use a new isolated output subdirectory')
    out.mkdir(parents=True, exist_ok=True)
    receipt_path = out / 'CPU_CONTRACT_VALIDATION.json'
    _require(not receipt_path.exists(), 'Do not overwrite an earlier CPU validation receipt')
    started = time.perf_counter()
    ctx = load_contract_context()
    names = list(selected_config_names)
    binding = validation_binding(ctx, names)
    ids = select_contract_ids(ctx) if episode_ids is None else [int(eid) for eid in episode_ids]
    _require(ids and len(ids) == len(set(ids)) and set(ids) <= set(ctx['jobs']['outer0_inner0']['ids']['T']),
             'Real validation IDs must be unique proper-training T episodes')
    _require(len(ids) <= 128, 'Even future extended validation must remain bounded')
    timestamps = _timestamp_evidence(ctx, ids)
    samplers = _sampler_evidence(ctx, names)
    reference_loader = episode_loader(ctx, ids)
    _require(reference_loader.num_workers == 2 and reference_loader.prefetch_factor == 1 and
             reference_loader.pin_memory and not reference_loader.persistent_workers,
             'Original frozen baseline loader settings changed')
    reference = _collect(reference_loader, ctx, ids)
    candidates = {}
    for name in names:
        value = _collect(build_loader(ctx, ids, PRESETS[name]), ctx, ids)
        _require(value == reference, 'Full-byte/order/label/RNG identity mismatch: ' + name)
        candidates[name] = {'full_tensor_and_per_camera_frame_hashes_equal_to_original': True,
                            'delivered_episode_ids': value['delivered_episode_ids'],
                            'main_process_torch_rng_unchanged': True,
                            'configuration': PRESETS[name].as_dict()}
    result = {
        'schema': 1, 'status': 'PASS', 'utc': utc(),
        'purpose': 'Bounded CPU data-contract validation, not a throughput benchmark',
        'binding': binding, 'binding_sha256': signature(binding),
        'checked_config_names': names, 'selected_episode_ids': ids,
        'selection': 'Proper T only; default frame-count quantiles without labels/performance; explicit IDs if separately admitted',
        'selected_rows': [{key: ctx['lookup'][eid][key] for key in
                           ('episode_index', 'canonical_task_id', 'label', 'frame_count', 'frame_indices', 'frame_times_seconds')}
                          for eid in ids],
        'real_decoded_episodes': len(ids) * (1 + len(names)),
        'real_decoded_camera_streams': 3 * len(ids) * (1 + len(names)),
        'reference': reference, 'configurations': candidates,
        'timestamps': timestamps, 'full_T_sampler_cases': samplers,
        'native_label_verification': ctx['verification']['native_labels'],
        'nominal_CPU_pin_memory_requested': True, 'actual_CUDA_pinning_test': 'PENDING_GPU_ADMISSION',
        'global_torch_rng_unchanged': True, 'CUDA_visible_devices': os.environ['CUDA_VISIBLE_DEVICES'],
        'CUDA_initialized': torch.cuda.is_initialized(), 'torch_threads': torch.get_num_threads(),
        'process_CPU_affinity': sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
        'wall_seconds_for_validation_only': time.perf_counter() - started,
        'packages': {name: importlib.metadata.version(name) for name in ('torch', 'numpy', 'transformers', 'Pillow')},
        'python': platform.python_version(), 'command': sys.argv,
        'warnings': [
            'CPU-hidden CUDA disables actual pinned allocation; GPU pinning and numerical update equivalence remain pending.',
            'Timestamp identity uses historical complete-decode actual PTS bound to newly hashed unchanged media, not a new PTS decode.',
            'Hashes cover all transformed bytes and every ordered camera/frame; no pixels or frame caches are written.',
            'Real decode covers the declared T subset; complete T orders use metadata/samplers without decoding every episode.',
            'CPU-only validation duration is not a measured GPU speedup or GPU waiting-time result.',
        ],
    }
    with receipt_path.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    return result
