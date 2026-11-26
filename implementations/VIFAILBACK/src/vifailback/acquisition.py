"""Anonymous, hash-verified selective acquisition; existing bytes are immutable."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import hashlib
import threading
import time
import requests

from .common import PROJECT, config, core, disk_reserve, event, read, resolve, sha, utc, video_path, write


def acquire_one(item, destination, *, url, minimum_free=None):
    """Return identity receipt; never write failed, partial or mismatched payloads."""
    from pathlib import Path
    destination = Path(destination)
    expected = item['lfs']['sha256']
    if destination.exists():
        if destination.stat().st_size != item['size'] or sha(destination) != expected:
            raise RuntimeError('EXISTING_SOURCE_IDENTITY_MISMATCH_PRESERVED')
        return {'status': 'VERIFIED_EXISTING', 'bytes': item['size'], 'sha256': expected}
    session = requests.Session()
    session.trust_env = False
    try:
        for attempt in range(8):
            if minimum_free:
                minimum_free(item['size'])
            with session.get(url, timeout=(20, 120), stream=True, headers={'User-Agent': 'ViFailback-reproducible-research/3.0'}) as response:
                if response.status_code in (401, 403):
                    raise PermissionError(f'PUBLIC_SOURCE_ACCESS_BLOCKED_HTTP_{response.status_code}')
                if response.status_code == 429 or response.status_code >= 500:
                    retry = response.headers.get('Retry-After', '')
                    delay = min(60, int(retry)) if retry.isdigit() else min(60, 2**attempt + 2)
                    time.sleep(delay)
                    continue
                if response.status_code != 200:
                    raise RuntimeError(f'PUBLIC_SOURCE_HTTP_{response.status_code}')
                payload = bytearray()
                hasher = hashlib.sha256()
                for block in response.iter_content(1024 * 1024):
                    payload.extend(block)
                    hasher.update(block)
                    if len(payload) > item['size']:
                        raise RuntimeError('PUBLISHED_LENGTH_EXCEEDED')
                if len(payload) != item['size'] or hasher.hexdigest() != expected:
                    raise RuntimeError('PUBLISHED_PAYLOAD_IDENTITY_MISMATCH')
                if minimum_free:
                    minimum_free(len(payload))
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open('xb') as stream:
                    stream.write(payload)
                return {'status': 'ACQUIRED_VERIFIED', 'bytes': len(payload), 'sha256': expected,
                        'source_url': url, 'utc': utc()}
        raise RuntimeError('TRANSIENT_SOURCE_ERRORS_RETRY_ON_RESUME')
    finally:
        session.close()


def acquire(c=None):
    c = c or config()
    published = read(resolve(c['publisher_inventory']))
    assert published['sha'] == c['revision']
    files = {row['rfilename']: row for row in published['siblings']}
    keys = ['video_high', 'video_left', 'video_right']
    wanted = [row[key] for row in core(c) for key in keys]
    assert len(wanted) == len(set(wanted)) == 13152
    missing = [name for name in wanted if not video_path(c, name).exists()]
    required = sum(files[name]['size'] for name in missing)
    disk_reserve(c, required)
    output = PROJECT / '02_dataset_verification/video_audit/runs' / c['run_id']
    output.mkdir(parents=True, exist_ok=True)
    plan = {'revision': c['revision'], 'requested_files': len(wanted), 'missing_files': len(missing),
            'missing_bytes': required, 'free_before_bytes': disk_reserve(c), 'workers': c['download_workers'],
            'configuration_sha256': sha(PROJECT / 'configs/experiment.json'), 'overwrite_existing': False}
    if not (output / 'ACQUISITION_PLAN.json').exists():
        write(output / 'ACQUISITION_PLAN.json', plan)
    event(c, 'VIDEO_ACQUISITION_STARTED', **plan)
    stop = threading.Event()

    def worker(relative):
        item = files[relative]
        receipt = output / 'source_receipts' / (relative + '.json')
        path = video_path(c, relative)
        if receipt.exists():
            old = read(receipt)
            if old.get('status') in ['VERIFIED_EXISTING', 'ACQUIRED_VERIFIED'] and path.exists() and path.stat().st_size == old['bytes'] and path.stat().st_mtime_ns == old.get('mtime_ns'):
                return old
        if stop.is_set():
            return {'path': relative, 'status': 'WAITING_SOURCE_PERMISSION'}
        url = f'https://huggingface.co/datasets/{c["repository"]}/resolve/{c["revision"]}/{relative}'
        try:
            result = acquire_one(item, path, url=url, minimum_free=lambda n: disk_reserve(c, n))
            row = {'path': relative, 'local_path': str(path.relative_to(PROJECT.parent)), 'revision': c['revision'],
                   'mtime_ns': path.stat().st_mtime_ns, **result}
            write(receipt, row)
            return row
        except PermissionError as error:
            stop.set()
            return {'path': relative, 'status': 'BLOCKED_PERMISSION', 'error': str(error)}
        except Exception as error:
            return {'path': relative, 'status': 'BLOCKED', 'error': type(error).__name__ + ':' + str(error).split('?')[0][:200]}

    rows = []
    with ThreadPoolExecutor(max_workers=c['download_workers']) as pool:
        futures = [pool.submit(worker, name) for name in wanted]
        for future in as_completed(futures):
            rows.append(future.result())
            if len(rows) % 100 == 0:
                counts = dict(Counter(row['status'] for row in rows))
                write(output / 'ACQUISITION_PROGRESS.json', {'utc': utc(), 'done': len(rows), 'total': len(wanted), 'counts': counts})
                event(c, 'VIDEO_ACQUISITION_PROGRESS', done=len(rows), total=len(wanted), counts=counts)
    rows.sort(key=lambda row: row['path'])
    result = {'utc': utc(), 'rows': rows, 'counts': dict(Counter(row['status'] for row in rows)),
              'complete': all(row['status'] in ['VERIFIED_EXISTING', 'ACQUIRED_VERIFIED'] for row in rows)}
    write(output / 'ACQUISITION_COMPLETE.json', result)
    event(c, 'VIDEO_ACQUISITION_FINISHED', complete=result['complete'], counts=result['counts'])
    return result
