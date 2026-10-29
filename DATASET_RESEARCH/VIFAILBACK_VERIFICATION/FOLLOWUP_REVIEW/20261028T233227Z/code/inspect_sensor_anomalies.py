"""Bounded original-HDF5 checks for input-detected numerical anomalies."""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import io
import hashlib
import json
import h5py
import numpy as np
import pandas as pd
import requests

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent
REV = '21df46c2585c52e5a62df5f4b946bae6cbc6fed7'
REPO = 'sii-rhos-ai/ViFailback-Dataset'


def get(url, maximum, headers=None):
    session = requests.Session()
    session.trust_env = False
    try:
        with session.get(url, headers={'User-Agent': 'ViFailback-numerical-QC/2.0', **(headers or {})}, timeout=(20, 90), stream=True) as response:
            response.raise_for_status()
            if headers:
                assert response.status_code == 206, 'Server did not honor bounded range; refuse body'
            if int(response.headers.get('Content-Length', 0)) > maximum:
                raise RuntimeError('Refuse body above bounded audit size')
            output = bytearray()
            for block in response.iter_content(65536):
                output.extend(block)
                assert len(output) <= maximum
            return bytes(output), {'url': url, 'request_headers': headers or {}, 'status': response.status_code,
                                   'content_range': response.headers.get('Content-Range'), 'bytes': len(output),
                                   'sha256': hashlib.sha256(output).hexdigest()}
    finally:
        session.close()


class Ranges(io.RawIOBase):
    def __init__(self, url, size, directory):
        self.url, self.size, self.directory = url, size, directory
        self.position, self.bytes = 0, 0
        self.directory.mkdir(exist_ok=False)

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position

    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        assert 0 <= self.position <= self.size
        return self.position

    def read(self, count=-1):
        count = self.size - self.position if count < 0 else min(count, self.size - self.position)
        if not count: return b''
        assert count <= 1_000_000 and self.bytes + count <= 4_000_000
        begin, end = self.position, self.position + count - 1
        path = self.directory / f'{begin}_{end}.bin'
        if path.exists():
            data = path.read_bytes()
        else:
            data, receipt = get(self.url, count, {'Range': f'bytes={begin}-{end}'})
            assert len(data) == count
            with path.open('xb') as stream: stream.write(data)
            with path.with_suffix('.receipt.json').open('x') as stream: json.dump(receipt, stream, indent=2)
            self.bytes += count
        self.position += len(data)
        return data

    def readinto(self, buffer):
        data = self.read(len(buffer))
        buffer[:len(data)] = data
        return len(data)


def sample(eid):
    try:
        annotations = {row['episode_index']: row for row in map(json.loads, (SOURCE / 'source_evidence/vifailback/meta/vifailback_annotations.jsonl').open())}
        a = annotations[eid]
        task = a['source_task']
        url = f'https://huggingface.co/api/datasets/{REPO}/tree/{REV}/raw_data/{task}?recursive=false'
        data, receipt = get(url, 2_000_000)
        tree_path = RUN / f'source_evidence/original_tree_{eid}.json'
        with tree_path.open('xb') as stream: stream.write(data)
        with tree_path.with_suffix('.receipt.json').open('x') as stream: json.dump(receipt, stream, indent=2)
        entry = next(row for row in json.loads(data) if row['path'] == a['source_hdf5'])
        original_url = f'https://huggingface.co/datasets/{REPO}/resolve/{REV}/{entry["path"]}'
        ranges = Ranges(original_url, entry['size'], RUN / f'source_evidence/original_sensor_ranges_{eid}')
        inventory = json.loads((RUN / 'provenance/SENSOR_TABLE_INVENTORY.json').read_text())
        item = next(row for row in inventory if row['path'].endswith(f'episode_{eid:06d}.parquet'))
        converted = pd.read_parquet(SOURCE / item['local_path'])
        checks = []
        with h5py.File(ranges, 'r') as h:
            for feature, key in [('observation.state', 'observations/qpos'), ('observation.velocity', 'observations/qvel'), ('observation.effort', 'observations/effort')]:
                old = h[key][:]
                new = np.stack(converted[feature])
                checks.append({'feature': feature, 'shape': list(old.shape),
                               'max_abs_conversion_error': float(np.max(np.abs(old - new))),
                               'original_min': np.min(old, axis=0).tolist(), 'original_max': np.max(old, axis=0).tolist()})
        return {'episode_index': eid, 'source_hdf5': a['source_hdf5'], 'status': 'VERIFIED',
                'original_lfs': entry.get('lfs'), 'full_source_bytes': entry['size'], 'range_bytes_downloaded': ranges.bytes,
                'checks': checks}
    except Exception as error:
        return {'episode_index': eid, 'status': 'BLOCKED', 'error': str(error)}


if __name__ == '__main__':
    rows = list(ThreadPoolExecutor(max_workers=2).map(sample, [2791, 3034, 5080]))
    with (RUN / '03_SENSOR_QUALITY/ADDITIONAL_ORIGINAL_SENSOR_CHECKS.json').open('x') as stream:
        json.dump(rows, stream, indent=2)
    print(json.dumps([{key: value for key, value in row.items() if key != 'checks'} for row in rows], indent=2))
