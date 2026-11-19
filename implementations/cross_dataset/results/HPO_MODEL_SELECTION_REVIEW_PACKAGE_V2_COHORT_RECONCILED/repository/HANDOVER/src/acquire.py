"""Official pinned Zenodo record acquisition, sample-first then gated full data."""
import argparse
import json
import shutil
import sys
from pathlib import Path
import requests

sys.path.insert(0,'CROSS_DATASET_COMPARISON/src')
from external_eval.io import download,extract_verified,write_json,utc

ROOT=Path('HANDOVER/01_raw_dataset')


def acquire(full=False):
    evidence=ROOT/'source_evidence';evidence.mkdir(exist_ok=True)
    done=evidence/('full_acquisition.json' if full else 'sample_acquisition.json')
    if done.exists():
        from external_eval.io import sha
        for item in json.loads(done.read_text()):
            p=Path(item['path'])
            if not p.is_file() or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:
                raise ValueError('Previously completed official acquisition changed')
        print('REUSED verified completed acquisition',done,flush=True);return
    path=evidence/'zenodo_record_10708763.json'
    if path.exists():record=json.loads(path.read_text())
    else:
        r=requests.get('https://zenodo.org/api/records/10708763',timeout=60)
        if r.status_code in (401,403):raise PermissionError('Official Zenodo metadata access restricted')
        r.raise_for_status();record=r.json();assert int(record['id'])==10708763
        write_json(path,record)
        write_json(evidence/'source_access.json',{'utc':utc(),'record':'https://zenodo.org/records/10708763','doi':'10.5281/zenodo.10708763','pinned_record':10708763,'page_version':'v1','record_created':record['created'],'record_updated':record['updated']})
    wanted=['datasheet.pdf','class_names.json','wrench_stats.json','training_labels.tar.gz','val_labels.tar.gz','test_labels.tar.gz','sample_training_set.tar.gz']
    if full:
        gate=Path('HANDOVER/02_labels_and_alignment/sample_gate.json')
        if not gate.exists() or not json.loads(gate.read_text()).get('passed'):raise ValueError('Sample validation gate has not passed')
        wanted=['training_set.tar.gz','val_set.tar.gz','test_set.tar.gz']
        total=sum(f['size'] for f in record['files'] if f['key'] in wanted)
        ratio=json.loads(gate.read_text()).get('sample_required_uncompressed_ratio',json.loads(gate.read_text())['sample_uncompressed_ratio'])
        projected=total*(1+max(1.25,ratio*1.2))+3*1024**3+10*1024**3
        if shutil.disk_usage(ROOT).free<projected:raise ValueError('Insufficient archive/extraction/cache space plus 10 GiB reserve')
        write_json(evidence/'full_storage_gate.json',{'archive_bytes':total,'sample_expansion_ratio':ratio,'projected_bytes_including_10gib_reserve':int(projected),'free_bytes':shutil.disk_usage(ROOT).free,'passed':True})
    entries={f['key']:f for f in record['files']};results=[]
    for name in wanted:
        entry=entries[name];target=ROOT/'official_dataset/archives'/name
        result=download(entry,target,evidence/'receipts');results.append(result);print(json.dumps(result),flush=True)
        if name.endswith('.tar.gz') and name!='sample_training_set.tar.gz':
            # Native split archive hierarchy is preserved under separate roots.
            category='labels' if '_labels' in name else 'data'
            split='train' if name.startswith('training') else 'validation' if name.startswith('val') else 'test'
            needed={'head_cam.mp4','head_cam_ts.npy','wrench_resampled.npy','wrench_ts.npy','wrench.npy','task_info.json','joint_names.npy'}
            members=extract_verified(target,ROOT/'official_dataset'/category/split,needed if category=='data' else None)
            write_json(evidence/(name+'.members.json'),members)
    if not full:
        sample=ROOT/'official_dataset/archives/sample_training_set.tar.gz'
        members=extract_verified(sample,ROOT/'official_dataset/sample')
        write_json(evidence/'sample_members.json',members)
        print('SAMPLE_MEMBERS',json.dumps(members,indent=2),flush=True)
    write_json(evidence/('full_acquisition.json' if full else 'sample_acquisition.json'),results)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');acquire(p.parse_args().full)
