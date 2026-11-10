"""Verify/reuse all minimal laboratory sources; acquire only verified missing paths."""
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime,timezone

LEGACY=Path('MSM/99_preserved_previous_work/MILLING_DATASET')
sys.path[:0]=[str(LEGACY/'source/stage2'),'CROSS_DATASET_COMPARISON/src']
from download_msm import transfer,sha256
from external_eval.io import write_json


def main():
    final=LEGACY/'runs/20261027T015205931708Z-stage5-full-lab-validated'
    import pandas as pd
    plan=pd.read_csv(final/'MSM_DOWNLOAD_MANIFEST.csv').to_dict('records')
    known={r['relative_source_path']:{'path':r['relative_source_path'],'bytes':int(r['official_bytes']),'sha256':r['sha256']} for r in plan}
    for r in json.loads((final/'manifests/input_manifest.json').read_text()):
        path=Path(r['path']);parts=path.parts
        if path.name=='label.csv':
            relative='/'.join(parts[-3:]);known[relative]={'path':relative,'bytes':r['bytes'],'sha256':r['sha256']}
    root=Path('MSM/01_raw_dataset/official_dataset');missing=[]
    for name,row in known.items():
        path=root/name
        if path.exists():
            if path.stat().st_size!=row['bytes'] or sha256(path)!=row['sha256']:raise ValueError('Existing version-2 raw input mismatch; preserved: '+name)
        else:missing.append(row)
    if shutil.disk_usage(root).free<sum(r['bytes'] for r in missing)+10*1024**3:raise ValueError('Insufficient minimum raw-data reserve')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    staging=Path('MSM/01_raw_dataset/acquisition_staging')/stamp
    receipts=[]
    for row in missing:
        result=transfer('manufuturetoday/multi-sensor-for-metal-milling-anomaly/versions/2',row,root,staging)
        if result['sha256']!=row['sha256']:raise ValueError('Pinned official file differs from preserved original hash; stop')
        receipts.append(result)
    write_json(Path('MSM/01_raw_dataset/source_evidence')/('reuse_verification_'+stamp+'.json'),
        {'version':2,'verified_minimal_sources':len(known),'downloaded':len(receipts),'download_bytes':sum(x['bytes'] for x in receipts),'receipts':receipts,
         'source_final_manifest':str(final),'large_existing_media_not_duplicated':True})
    print('MSM minimal raw source hashes verified:',len(known),'downloaded:',len(receipts),flush=True)


if __name__=='__main__':main()
