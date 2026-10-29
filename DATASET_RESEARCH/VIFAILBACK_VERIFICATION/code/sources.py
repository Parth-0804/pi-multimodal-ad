"""Anonymous, bounded source acquisition with immutable receipts."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
HF='sii-rhos-ai/vifailback-dataset-lerobot'
REV='619791b94f61667333fe179d471051e0bca0e06f'
MAX_BYTES=2_000_000_000
MIN_FREE=20*1024**3


def acquire(url,name,limit=25_000_000,headers=None):
    path=ROOT/'source_evidence'/name;path.parent.mkdir(parents=True,exist_ok=True)
    receipt=path.with_name(path.name+'.receipt.json')
    if receipt.exists():
        info=json.loads(receipt.read_text())
        assert info['source_url']==url and info.get('request_headers',{})==(headers or {})
        if path.exists():assert hashlib.sha256(path.read_bytes()).hexdigest()==info['sha256']
        return path
    if path.exists():raise FileExistsError(path)
    used=sum(p.stat().st_size for p in (ROOT/'source_evidence').rglob('*') if p.is_file())
    allowed=min(limit,MAX_BYTES-used)
    if allowed<=0 or shutil.disk_usage(ROOT).free-allowed<MIN_FREE:raise RuntimeError('Budget/reserve guard')
    session=requests.Session();session.trust_env=False
    info={'source_url':url,'utc':datetime.now(timezone.utc).isoformat(),'request_headers':headers or {}}
    try:
        with session.get(url,stream=True,timeout=(20,90),headers={'User-Agent':'Scientific-source-audit/1.0',**(headers or {})}) as response:
            info.update(http_status=response.status_code,etag=response.headers.get('ETag'),content_range=response.headers.get('Content-Range'),declared_bytes=response.headers.get('Content-Length'))
            response.raise_for_status()
            if headers and 'Range' in headers and response.status_code!=206:raise RuntimeError('Byte range not honored; body not acquired')
            if int(response.headers.get('Content-Length',0))>allowed:raise RuntimeError('File exceeds current bounded acquisition plan')
            digest=hashlib.sha256();count=0
            with path.open('xb') as f:
                for block in response.iter_content(65536):
                    count+=len(block)
                    if count>allowed or shutil.disk_usage(ROOT).free<MIN_FREE:raise RuntimeError('Streaming size/reserve guard')
                    f.write(block);digest.update(block)
            info.update(status='ACQUIRED',bytes=count,sha256=digest.hexdigest())
    except Exception as error:info.update(status='BLOCKED',error=str(error))
    receipt.write_text(json.dumps(info,indent=2)+'\n')
    print(info['status'],name,info.get('bytes',info.get('error')))
    return path


def hf_file(path,limit=25_000_000):
    return acquire(f'https://huggingface.co/datasets/{HF}/resolve/{REV}/{path}','vifailback/'+path,limit)


if __name__=='__main__':
    acquire(f'https://huggingface.co/api/datasets/{HF}/revision/{REV}?blobs=true','vifailback_files.json',12_000_000)
    hf_file('README.md')
