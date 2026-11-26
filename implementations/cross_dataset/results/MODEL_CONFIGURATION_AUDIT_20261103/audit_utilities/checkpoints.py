"""Stream hashes and inspect tensor-only checkpoints on CPU; never unpickle models."""
from pathlib import Path
import csv
import gc
import hashlib
import json
import pickletools
import time
import zipfile

from discover import OUT, REPO


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024**2), b''):
            digest.update(chunk)
    return digest.hexdigest()


def static_pickle_keys(path):
    result = []
    try:
        with zipfile.ZipFile(path) as archive:
            member = next(n for n in archive.namelist() if n.endswith('/data.pkl'))
            data = archive.read(member)
        wanted = {'model', 'state_dict', 'optimizer', 'scheduler', 'random', 'rng',
                  'completed_epoch', 'completed_epochs', 'selected_epoch', 'history',
                  'config', 'configuration', 'seed', 'identity', 'fit_identity'}
        for operation, value, position in pickletools.genops(data):
            if operation.name in {'SHORT_BINUNICODE', 'BINUNICODE', 'UNICODE'} and value in wanted:
                result.append(value)
    except (ValueError, KeyError, StopIteration, zipfile.BadZipFile, OSError):
        pass
    return sorted(set(result))


def json_value(value, depth=0):
    import torch
    if torch.is_tensor(value):
        return {'tensor_shape': list(value.shape), 'dtype': str(value.dtype)}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if depth > 6: return 'DEPTH_LIMIT_METADATA_ONLY'
    if isinstance(value, dict):
        return {str(k): json_value(v, depth+1) for k, v in value.items() if k != 'params'}
    if isinstance(value, (list, tuple)):
        if len(value) > 100:
            return {'sequence_length': len(value), 'values_not_copied': True}
        return [json_value(v, depth+1) for v in value]
    return {'python_type': type(value).__name__, 'not_deserialized_further': True}


def inspect(path):
    import torch
    result = {'inspection_method': 'torch.load(weights_only=True,map_location=cpu)',
              'static_archive_metadata_keys': static_pickle_keys(path)}
    try:
        value = torch.load(path, map_location='cpu', weights_only=True, mmap=True)
    except Exception as exc:
        result.update(inspection_status='PARTIALLY VERIFIED',
                      inspection_note='Safe CPU loader declined payload; no unsafe fallback executed.',
                      safe_load_error=str(exc).split('\n')[0][:400])
        return result
    if not isinstance(value, dict):
        result.update(inspection_status='PARTIALLY VERIFIED', payload_type=type(value).__name__)
        return result
    result['inspection_status'] = 'VERIFIED'
    result['top_level_keys'] = list(map(str, value.keys()))[:100]
    for key in ['selected_epoch', 'epoch', 'epochs', 'completed_epoch', 'completed_epochs',
                'best_epoch', 'kind', 'condition', 'arm', 'seed', 'width', 'context_width',
                'hidden', 'identity', 'fit_identity', 'config', 'configuration', 'metadata']:
        if key in value: result[key] = json_value(value[key])
    optimizer = value.get('optimizer', value.get('optimizer_state_dict'))
    if isinstance(optimizer, dict):
        result['optimizer_param_groups'] = json_value(optimizer.get('param_groups', []))
    for key in ['scheduler', 'scheduler_state_dict']:
        if key in value: result['scheduler_state'] = json_value(value[key])
    for key in ['history', 'training_history', 'loss_by_epoch']:
        if isinstance(value.get(key), (dict, list, tuple)):
            result[key+'_length'] = len(value[key])
    for key in ['model', 'state_dict', 'model_state_dict', 'state', 'visual']:
        state = value.get(key)
        if isinstance(state, dict) and any(torch.is_tensor(v) for v in state.values()):
            tensors = {str(n): {'shape': list(v.shape), 'elements': v.numel(), 'dtype': str(v.dtype)}
                       for n, v in state.items() if torch.is_tensor(v)}
            result['model_state_key'] = key
            result['state_tensor_shapes'] = tensors
            result['state_elements_including_buffers'] = sum(v['elements'] for v in tensors.values())
            result['parameter_count_scope_note'] = 'State elements include buffers; trainability requires forward/source evidence.'
            break
    del value
    gc.collect()
    return result


def main():
    import torch
    torch.set_num_threads(2)
    rows = json.loads((OUT/'provenance/CHECKPOINT_CANDIDATE_PATHS.json').read_text())
    seen = {}
    metadata = {}
    inventory = []
    start = time.monotonic()
    with (OUT/'provenance/CHECKPOINT_INSPECTION.jsonl').open('w') as detail:
        for index, row in enumerate(rows):
            path = REPO/row['path']
            before = path.stat()
            digest = sha(path)
            duplicate = seen.get(digest, '')
            seen.setdefault(digest, row['path'])
            inspection = {'inspection_status': 'NOT RECORDED'}
            if duplicate:
                inspection = {'inspection_status': 'VERIFIED_HASH_ALIAS', 'original': duplicate}
            elif path.suffix.lower() in {'.pt', '.pth', '.ckpt'}:
                inspection = inspect(path)
            elif path.suffix.lower() == '.safetensors':
                inspection = {'inspection_status': 'HASH_VERIFIED_NO_GPU_LOADING'}
            else:
                inspection = {'inspection_status': 'HASH_VERIFIED_PICKLE_NOT_EXECUTED'}
            after = path.stat()
            stable = before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns
            record = {**row, 'sha256': digest, 'hash_alias_of': duplicate,
                      'stable_during_hash': stable, 'metadata': inspection}
            detail.write(json.dumps(record, allow_nan=False)+'\n')
            detail.flush()
            inventory.append({**row, 'sha256': digest, 'hash_alias_of': duplicate,
                              'stable_during_hash': stable,
                              'inspection_status': inspection['inspection_status'],
                              'selected_epoch': inspection.get('selected_epoch', 'NOT RECORDED'),
                              'final_epoch': inspection.get('completed_epoch', inspection.get('completed_epochs', inspection.get('epochs', 'NOT RECORDED'))),
                              'model_state_available': bool(inspection.get('model_state_key')),
                              'optimizer_state_evidence': 'optimizer' in inspection.get('static_archive_metadata_keys', []) or 'optimizer_param_groups' in inspection,
                              'scheduler_state_evidence': 'scheduler' in inspection.get('static_archive_metadata_keys', []) or 'scheduler_state' in inspection,
                              'RNG_state_evidence': bool(set(inspection.get('static_archive_metadata_keys', [])) & {'random', 'rng'})})
            if (index+1) % 250 == 0:
                print('CHECKPOINTS', index+1, '/', len(rows), 'unique', len(seen),
                      'seconds', round(time.monotonic()-start, 1), flush=True)
    with (OUT/'04_training_and_checkpoints/CHECKPOINT_INVENTORY.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(inventory[0]))
        writer.writeheader()
        writer.writerows(inventory)
    summary = {'checkpoint_candidate_files': len(rows), 'unique_file_hashes': len(seen),
               'alias_files': len(rows)-len(seen), 'all_hash_inputs_stable': all(r['stable_during_hash'] for r in inventory),
               'safe_cpu_model_state_inspections': sum(r['model_state_available'] for r in inventory),
               'GPU_memory_used_by_audit': 0, 'unsafe_pickle_fallbacks': 0,
               'seconds': time.monotonic()-start,
               'counts_include_pretrained_tutorial_disposable_and_historical_artifacts': True}
    (OUT/'provenance/CHECKPOINT_SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
