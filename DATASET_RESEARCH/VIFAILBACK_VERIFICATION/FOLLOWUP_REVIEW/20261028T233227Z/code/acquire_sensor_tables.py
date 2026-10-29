"""Read-only reuse plus anonymous, pinned, numerical-only acquisition."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import threading
import time
import requests

RUN = Path(__file__).resolve().parents[1]
SOURCE = RUN.parent.parent
REV = '619791b94f61667333fe179d471051e0bca0e06f'
REPO = 'sii-rhos-ai/vifailback-dataset-lerobot'
STOP = threading.Event()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def acquire(item):
    relative = item['rfilename']
    expected = item['lfs']['sha256']
    row = {'path': relative, 'expected_sha256': expected, 'expected_bytes': item['size'],
           'revision': REV, 'url': f'https://huggingface.co/datasets/{REPO}/resolve/{REV}/{relative}'}
    existing = SOURCE / 'source_evidence/vifailback' / relative
    fresh = RUN / 'source_evidence' / relative
    for candidate in (existing, fresh):
        if candidate.exists():
            data = candidate.read_bytes()
            if sha(data) != expected or len(data) != item['size']:
                return {**row, 'status': 'BLOCKED', 'error': 'Existing file fails source hash; preserved'}
            return {**row, 'status': 'VERIFIED_AVAILABLE', 'local_path': str(candidate.relative_to(SOURCE))}
    if STOP.is_set():
        return {**row, 'status': 'BLOCKED', 'error': 'Source access restriction encountered; acquisition stopped'}
    if shutil.disk_usage(RUN).free < 20 * 1024**3:
        STOP.set()
        return {**row, 'status': 'BLOCKED', 'error': 'Storage reserve reached'}
    session = requests.Session()
    session.trust_env = False
    try:
        for attempt in range(6):
            response = session.get(row['url'], timeout=(20, 90), headers={'User-Agent': 'ViFailback-scientific-verification/2.0'})
            if response.status_code in (401, 403):
                STOP.set()
                response.raise_for_status()
            if response.status_code == 429 or response.status_code >= 500:
                retry = response.headers.get('Retry-After', '')
                delay = min(60, int(retry)) if retry.isdigit() else min(60, 2**attempt + 2)
                time.sleep(delay)
                continue
            response.raise_for_status()
            data = response.content
            assert len(data) == item['size'] and sha(data) == expected, 'Published size/hash mismatch'
            fresh.parent.mkdir(parents=True, exist_ok=True)
            with fresh.open('xb') as stream:
                stream.write(data)
            return {**row, 'status': 'ACQUIRED_VERIFIED', 'local_path': str(fresh.relative_to(SOURCE)),
                    'http_status': response.status_code, 'sha256': sha(data), 'bytes': len(data),
                    'utc': datetime.now(timezone.utc).isoformat()}
        raise RuntimeError('Transient HTTP errors persist; no partial payload stored')
    except Exception as error:
        return {**row, 'status': 'BLOCKED', 'error': str(error)}
    finally:
        session.close()


if __name__ == '__main__':
    meta = json.loads((SOURCE / 'source_evidence/vifailback_files.json').read_text())
    assert meta['sha'] == REV
    items = [row for row in meta['siblings'] if row['rfilename'].endswith('.parquet')]
    assert len(items) == 5202 and sum(row['size'] for row in items) < 220_000_000
    config = {'repository': REPO, 'revision': REV, 'workers': 6, 'storage_reserve_GiB': 20,
              'requested_files': len(items), 'published_total_bytes': sum(row['size'] for row in items),
              'acquisition_scope': 'Numerical Parquet only; no videos or original HDF5',
              'credentials_used': False, 'existing_policy': 'Read and verify; never overwrite'}
    with (RUN / 'config/ACQUISITION_CONFIG.json').open('x') as stream:
        json.dump(config, stream, indent=2)
    rows = []
    with (RUN / 'provenance/SENSOR_ACQUISITION_RECEIPTS.jsonl').open('x') as receipt:
        with ThreadPoolExecutor(max_workers=config['workers']) as executor:
            futures = [executor.submit(acquire, item) for item in items]
            for future in as_completed(futures):
                row = future.result()
                rows.append(row)
                receipt.write(json.dumps(row) + '\n')
                receipt.flush()
                if len(rows) % 100 == 0:
                    print('Numerical inventory verified', len(rows), '/ 5202; blockers', sum(r['status'] == 'BLOCKED' for r in rows), flush=True)
    rows.sort(key=lambda row: row['path'])
    with (RUN / 'provenance/SENSOR_TABLE_INVENTORY.json').open('x') as stream:
        json.dump(rows, stream, indent=2)
    print('COMPLETE', len(rows), 'tables;', sum(row['status'] == 'BLOCKED' for row in rows), 'blocked', flush=True)
