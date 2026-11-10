"""Bounded, anonymous source acquisition; preserve originals and provenance."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 500_000_000
MIN_FREE = 20 * 1024**3


def acquire(url, name, limit=30_000_000, byte_range=None):
    dest = ROOT / 'source_evidence' / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    receipt = dest.with_name(dest.name + '.receipt.json')
    if receipt.exists():
        prior = json.loads(receipt.read_text())
        if prior['source_url'] != url or prior.get('request_range') != byte_range:
            raise ValueError('Existing source has different URL')
        if dest.exists():
            assert hashlib.sha256(dest.read_bytes()).hexdigest() == prior['sha256']
        return dest
    assert not dest.exists(), f'Unreceipted source exists: {dest}'
    used = sum(p.stat().st_size for p in (ROOT/'source_evidence').rglob('*') if p.is_file())
    allowed = min(limit, LIMIT-used)
    if allowed <= 0 or shutil.disk_usage(ROOT).free - allowed < MIN_FREE:
        raise RuntimeError('Acquisition budget/free-space guard')
    session = requests.Session()
    session.trust_env = False  # Do not consult netrc or inherited authentication.
    info = {'source_url':url, 'utc':datetime.now(timezone.utc).isoformat(), 'request_range':byte_range}
    headers={'User-Agent':'Research-label-audit/1.0'}
    if byte_range:
        headers['Range']=byte_range
    try:
        with session.get(url, stream=True, timeout=(20,60), headers=headers) as response:
            info.update(http_status=response.status_code, declared_bytes=response.headers.get('Content-Length'),
                        etag=response.headers.get('ETag'), content_type=response.headers.get('Content-Type'),
                        content_range=response.headers.get('Content-Range'))
            response.raise_for_status()
            if byte_range and response.status_code != 206:
                raise RuntimeError('Server did not honor bounded range; no body downloaded')
            if int(response.headers.get('Content-Length', 0)) > allowed:
                raise RuntimeError('Source exceeds acquisition budget')
            total = 0
            digest = hashlib.sha256()
            with dest.open('xb') as out:
                for block in response.iter_content(65536):
                    total += len(block)
                    if total > allowed or shutil.disk_usage(ROOT).free < MIN_FREE:
                        raise RuntimeError('Streaming budget/free-space guard')
                    out.write(block)
                    digest.update(block)
            info.update(bytes=total, sha256=digest.hexdigest(), status='ACQUIRED')
    except Exception as exc:
        info.update(status='BLOCKED', error=str(exc))
        if dest.exists():
            info.update(partial_bytes=dest.stat().st_size, partial_sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    receipt.write_text(json.dumps(info, indent=2)+'\n')
    if info['status'] != 'ACQUIRED':
        print('BLOCKED', name, info.get('http_status'), info.get('error'))
    else:
        print('ACQUIRED', name, info['bytes'])
    return dest


def json_source(url, name):
    return json.loads(acquire(url,name).read_text())


if __name__ == '__main__':
    for dataset,name in [('MINT-SJTU/RoboFAC-dataset','robofac')]:
        info=json_source('https://huggingface.co/api/datasets/'+dataset, name+'/dataset_api.json')
        sha=info['sha']
        tree=json_source(f'https://huggingface.co/api/datasets/{dataset}/tree/{sha}?recursive=true&limit=1000',name+'/file_tree.json')
        acquire(f'https://huggingface.co/datasets/{dataset}/resolve/{sha}/README.md',name+'/README.md')
        print(name,sha,'tree entries',len(tree),'siblings',len(info.get('siblings',[])))
    for repo,name in [('MINT-SJTU/RoboFAC','robofac_code'),('ardai/fino-net','failure_code')]:
        info=json_source('https://api.github.com/repos/'+repo+'/commits/main',name+'/commit.json')
        sha=info['sha']
        tree=json_source(f'https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1',name+'/file_tree.json')
        acquire(f'https://raw.githubusercontent.com/{repo}/{sha}/README.md',name+'/README.md')
        acquire(f'https://raw.githubusercontent.com/{repo}/{sha}/LICENSE',name+'/LICENSE')
        print(name,sha,'tree entries',len(tree['tree']))
    acquire('https://air.cs.itu.edu.tr/projects/finonet.html','failure_code/project.html')
