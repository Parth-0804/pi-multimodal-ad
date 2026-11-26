"""Compare original annotation/HDF5 bytes against publisher Git/LFS identities."""
import hashlib,json
from sources import ROOT


if __name__=='__main__':
    source=ROOT/'source_evidence';entries={}
    for path in (source/'original_trees').glob('*.json'):
        if path.name.endswith('.receipt.json'):continue
        for entry in json.loads(path.read_text()):
            if entry['type']=='file':entries[entry['path']]=entry
    rows=[]
    for path in (source/'original').rglob('*'):
        if not path.is_file() or path.name.endswith('.receipt.json'):continue
        name=str(path.relative_to(source/'original'));entry=entries[name];raw=path.read_bytes()
        expected=entry['lfs']['oid'] if 'lfs' in entry else entry['oid']
        actual=hashlib.sha256(raw).hexdigest() if 'lfs' in entry else hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert len(raw)==entry['size'] and actual==expected,name
        rows.append({'original_path':name,'bytes':len(raw),'identity_type':'LFS SHA-256' if 'lfs' in entry else 'Git blob SHA-1','publisher_identity':expected,'matched':True})
    (ROOT/'checks/original_publisher_identity_validation.json').write_text(json.dumps({'passed':True,'files':len(rows),'rows':rows},indent=2)+'\n')
    print('Original publisher identity verified for',len(rows),'files')
