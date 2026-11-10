"""Verify original episode/time columns without downloading depth-heavy files.

This produces derived identity evidence, not a replacement episode index or
new ground-truth annotations. Exact original HTTP206 fragments are retained.
"""
import argparse
import concurrent.futures
import json
import pathlib
import shutil

import numpy as np
import pyarrow.parquet as pq

from acquire_pilot import RangeFile

PROJECT = pathlib.Path(__file__).resolve().parents[2]


class BoundedIdentityFile(RangeFile):
    def read(self, n=-1):
        if n < 0 or n > 1_000_000 or self.total_bytes + n > 1_000_000:
            raise ValueError('Identity-only per-file download budget exceeded')
        if shutil.disk_usage(PROJECT).free < 20_001_000_000:
            raise ValueError('Free-space reserve')
        return super().read(n)


def check_identity_rows(rows):
    groups = {}
    for row in rows:
        groups.setdefault(int(row['episode_index']), []).append(row)
    result = []
    for episode, records in sorted(groups.items()):
        frame = np.array([r['frame_index'] for r in records], dtype=np.int64)
        index = np.array([r['index'] for r in records], dtype=np.int64)
        times = np.array([r['timestamp'] for r in records], dtype=float)
        result.append({'episode_index': episode, 'rows': len(records), 'first_global_index': int(index[0]),
                       'last_global_index': int(index[-1]), 'frame_indices_contiguous_zero_based': bool(np.array_equal(frame, np.arange(len(records)))),
                       'global_indices_contiguous': bool(np.all(np.diff(index) == 1)),
                       'timestamps_finite_strictly_increasing': bool(np.isfinite(times).all() and np.all(np.diff(times) > 0)),
                       'max_nominal_30Hz_timestamp_residual_s': float(np.max(np.abs(times - frame / 30))),
                       'task_indices': sorted({int(r['task_index']) for r in records})})
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', required=True, type=pathlib.Path)
    args = p.parse_args()
    run = args.run.resolve()
    entry = next(e for e in json.loads((PROJECT / 'REBOOT/00_dataset_overview/PINNED_DATASET_INVENTORY.json').read_text())
                 if e['repo_id'] == 'REBOOT26/usbc_recovery_install')
    tree = json.loads((PROJECT / entry['file_tree']).read_text())
    files = [e for e in tree if e['type'] == 'file' and e['path'].startswith('data/') and e['path'].endswith('.parquet')]

    def inspect(file):
        url = f"https://huggingface.co/datasets/{entry['repo_id']}/resolve/{entry['revision']}/{file['path']}"
        reader = BoundedIdentityFile(url, file['size'], run / 'evidence/usbc_identity_ranges' / pathlib.Path(file['path']).stem)
        rec = {'repo_id': entry['repo_id'], 'revision': entry['revision'], 'path': file['path'],
               'source_file_bytes': file['size'], 'official_whole_file_sha256_reference': file['lfs']['oid'],
               'whole_file_hash_verified': False, 'full_depth_payload_downloaded': False}
        try:
            pf = pq.ParquetFile(reader, pre_buffer=False)
            rec['footer_rows'] = pf.metadata.num_rows
            rec['schema_names'] = pf.schema_arrow.names
            # Values, rather than filename/row-count assumptions, establish IDs and timing.
            table = pf.read(columns=['episode_index', 'frame_index', 'timestamp', 'index', 'task_index'], use_threads=False)
            rec['episodes'] = check_identity_rows(table.to_pylist())
            rec['identity_columns_verified'] = True
        except Exception as exc:
            rec.update(identity_columns_verified=False, error=type(exc).__name__ + ': ' + str(exc)[:180])
        rec.update(range_bytes_downloaded=reader.total_bytes, range_receipts=reader.receipts)
        print(file['path'], rec['identity_columns_verified'], reader.total_bytes, flush=True)
        return rec

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(inspect, files))
    target = run / 'reports/USBC_INDEPENDENT_IDENTITY_VERIFICATION.json'
    with target.open('x') as f:
        json.dump({'source': entry['repo_id'], 'revision': entry['revision'], 'files': results,
                   'total_range_bytes': sum(r['range_bytes_downloaded'] for r in results),
                   'original_episode_index_repaired': False,
                   'annotations_or_video_offsets_reconstructed': False}, f, indent=2)


if __name__ == '__main__':
    main()
