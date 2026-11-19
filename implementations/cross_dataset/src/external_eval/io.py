"""Exclusive publication and checked, restartable public-data acquisition."""
import csv
import hashlib
import json
import os
import tarfile
import time
from datetime import datetime,timezone
from pathlib import Path

import requests


def utc():return datetime.now(timezone.utc).isoformat()


def sha(path,algorithm='sha256'):
    h=hashlib.new(algorithm)
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    return h.hexdigest()


def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(value,indent=2,allow_nan=False,default=lambda x:x.item())+'\n'
    if path.exists():
        if path.read_text()!=text:raise ValueError('Existing immutable JSON differs: '+str(path))
        return
    part=path.with_name(path.name+f'.{time.time_ns()}.{os.getpid()}.writing')
    with part.open('x') as f:f.write(text);f.flush();os.fsync(f.fileno())
    os.link(part,path)


def csv_rows(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def download(entry,dest,receipts,max_attempts=3):
    """Byte ranges resume only when honored; verify official MD5 and exact size."""
    dest=Path(dest);receipts=Path(receipts);dest.parent.mkdir(parents=True,exist_ok=True);receipts.mkdir(parents=True,exist_ok=True)
    algorithm,expected=entry['checksum'].split(':',1)
    if dest.exists():
        if dest.stat().st_size!=entry['size'] or sha(dest,algorithm)!=expected:
            raise ValueError('Mismatching existing official file preserved: '+str(dest))
        return {'file':entry['key'],'status':'reused_verified','bytes':entry['size'],'sha256':sha(dest),'official_checksum':entry['checksum'],'path':str(dest)}
    part=dest.with_name(dest.name+'.part')
    for attempt in range(max_attempts):
        offset=part.stat().st_size if part.exists() else 0
        if offset>entry['size']:raise ValueError('Oversized partial file preserved')
        try:
            if offset<entry['size']:
                response=requests.get(entry['links']['self'],headers={'Range':f'bytes={offset}-'} if offset else {},stream=True,timeout=(45,120))
                if response.status_code in (401,403):raise PermissionError('Official access restriction; no bypass attempted')
                response.raise_for_status()
                if offset and response.status_code!=206:raise ValueError('Server does not honor safe byte resume; partial file preserved')
                if offset and not response.headers.get('Content-Range','').startswith(f'bytes {offset}-'):
                    raise ValueError('Response byte range mismatch')
                with part.open('ab' if offset else 'xb') as f:
                    for block in response.iter_content(1024**2):
                        if block:f.write(block)
                        if f.tell()>entry['size']:raise ValueError('Official size exceeded')
                    f.flush();os.fsync(f.fileno())
                response.close()
            if part.stat().st_size!=entry['size']:raise IOError('Incomplete official transfer')
            if sha(part,algorithm)!=expected:raise ValueError('Official checksum mismatch; preserve file and stop')
            os.link(part,dest)
            result={'file':entry['key'],'status':'downloaded_verified','bytes':entry['size'],'sha256':sha(dest),
                'official_checksum':entry['checksum'],'path':str(dest),'utc':utc(),'source':entry['links']['self']}
            write_json(receipts/(entry['key']+'.json'),result);return result
        except PermissionError:
            raise
        except (requests.exceptions.RequestException,IOError) as exc:
            write_json(receipts/(entry['key']+f'.attempt{attempt+1}.failure.json'),{'utc':utc(),'error_type':type(exc).__name__,'partial_bytes':part.stat().st_size if part.exists() else 0})
            if attempt+1==max_attempts:raise
            time.sleep(min(5,attempt+1))


def extract_verified(archive,dest,allowed_names=None):
    """Never overwrite a member or follow an archive-supplied link."""
    archive=Path(archive);dest=Path(dest);dest.mkdir(parents=True,exist_ok=True);rows=[]
    with tarfile.open(archive,'r:gz') as tar:
        for member in tar:
            rel=Path(member.name)
            if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe archive path')
            target=dest/rel
            if member.isdir():target.mkdir(parents=True,exist_ok=True);continue
            if not member.isfile():raise ValueError('Unsupported linked/special member')
            if allowed_names is not None and rel.name not in allowed_names and not (rel.suffix=='.json' and member.size<=1024**2):
                rows.append({'member':member.name,'bytes':member.size,'status':'preserved_in_verified_archive_not_extracted'})
                continue
            target.parent.mkdir(parents=True,exist_ok=True)
            data=tar.extractfile(member)
            if target.exists():
                h=hashlib.sha256()
                for block in iter(lambda:data.read(1024**2),b''):h.update(block)
                if target.stat().st_size!=member.size or sha(target)!=h.hexdigest():raise ValueError('Existing member mismatch')
                status='reused_verified'
            else:
                part=target.with_name(target.name+'.extracting')
                with part.open('xb') as f:
                    for block in iter(lambda:data.read(1024**2),b''):f.write(block)
                    f.flush();os.fsync(f.fileno())
                if part.stat().st_size!=member.size:raise ValueError('Incomplete extraction')
                os.link(part,target);status='extracted'
            rows.append({'member':member.name,'path':str(target),'bytes':member.size,'sha256':sha(target),'status':status})
    return rows
